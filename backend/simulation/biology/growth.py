
import math

from pydantic import BaseModel, Field

from app.models.plant import PlantRecord, GrowthStage
from simulation.biology.parameters import CROP_PARAMETERS
from simulation.biology.development import (
    calculate_thermal_time,
    calculate_temperature_stress,
)
from simulation.biology.water import calculate_water_stress
from simulation.biology.nutrients import calculate_nutrient_effect
from simulation.biology.lifecycle import calculate_lifecycle
from simulation.biology.health import calculate_plant_health
from simulation.biology.recovery import calculate_recovery
from simulation.biology.damage import calculate_tissue_damage


class DailyGrowthInput(BaseModel):
    temperature_c: float
    daily_par_mj_m2: float = Field(ge=0)
    soil_water_mm: float = Field(ge=0)
    field_capacity_mm: float = Field(gt=0)
    wilting_point_mm: float = Field(ge=0)
    irrigation_mm: float = Field(default=0, ge=0)
    rainfall_mm: float = Field(default=0, ge=0)
    reference_et_mm: float = Field(default=0, ge=0)
    plant_area_m2: float = Field(default=1.0, gt=0)

    soil_ph: float = Field(default=6.5, ge=0, le=14)
    ec_ds_m: float = Field(default=1.0, ge=0)
    nitrogen_mg_kg: float = Field(default=120, ge=0)
    phosphorus_mg_kg: float = Field(default=40, ge=0)
    potassium_mg_kg: float = Field(default=150, ge=0)
    soil_mass_kg: float = Field(default=20, gt=0)


STAGE_THRESHOLDS = {
    "tomato": [
        (50, GrowthStage.SEEDLING),
        (150, GrowthStage.VEGETATIVE),
        (650, GrowthStage.FLOWERING),
        (900, GrowthStage.FRUITING),
        (1400, GrowthStage.MATURITY),
    ],
    "cucumber": [
        (40, GrowthStage.SEEDLING),
        (120, GrowthStage.VEGETATIVE),
        (450, GrowthStage.FLOWERING),
        (650, GrowthStage.FRUITING),
        (950, GrowthStage.MATURITY),
    ],
    "lettuce": [
        (35, GrowthStage.SEEDLING),
        (100, GrowthStage.VEGETATIVE),
        (600, GrowthStage.MATURITY),
    ],
}


LIGHT_REFERENCE_PAR = {
    "tomato": 20.0,
    "cucumber": 20.0,
    "lettuce": 14.0,
}


def initialize_plant(plant: PlantRecord) -> PlantRecord:
    species = plant.profile.species.lower()

    if species not in CROP_PARAMETERS:
        raise ValueError(f"Unsupported crop: {species}")

    if plant.state.is_initialized:
        return plant

    crop = CROP_PARAMETERS[species]

    plant.state = plant.state.model_copy(
        update={
            "leaf_count": crop.initial_leaf_count,
            "root_depth_cm": crop.initial_root_depth_cm,
            "canopy_cover_percent": crop.initial_canopy_cover_percent,
            "biomass_g": crop.initial_biomass_g,
            "seed_reserve_remaining_g": crop.initial_seed_reserve_g,
            "is_initialized": True,
        }
    )

    return plant


def simulate_growth_day(
    plant: PlantRecord,
    environment: DailyGrowthInput,
) -> dict:

    species = plant.profile.species.lower()

    if species not in CROP_PARAMETERS:
        raise ValueError(f"Unsupported crop: {species}")

    crop = CROP_PARAMETERS[species]

    if environment.field_capacity_mm <= environment.wilting_point_mm:
        raise ValueError("Field capacity must exceed wilting point.")

    if environment.soil_water_mm < environment.wilting_point_mm:
        raise ValueError("Soil water cannot be below wilting point.")

    if environment.soil_water_mm > environment.field_capacity_mm:
        raise ValueError("Soil water cannot exceed field capacity.")

    initialize_plant(plant)

    # 1. Thermal time and temperature response
    thermal_time = calculate_thermal_time(
        environment.temperature_c,
        crop.base_temperature_c,
        crop.maximum_temperature_c,
    )

    temperature_stress = calculate_temperature_stress(
        environment.temperature_c,
        crop.base_temperature_c,
        crop.optimal_temperature_c,
        crop.maximum_temperature_c,
    )

    # 2. Soil water balance
    water_before_use = min(
        environment.field_capacity_mm,
        environment.soil_water_mm
        + environment.irrigation_mm
        + environment.rainfall_mm,
    )

    water_stress = calculate_water_stress(
        water_before_use,
        environment.wilting_point_mm,
        environment.field_capacity_mm,
    )

    canopy_fraction = plant.state.canopy_cover_percent / 100

    crop_coefficient = 0.3 + 0.7 * canopy_fraction

    potential_water_use = (
        environment.reference_et_mm * crop_coefficient
    )

    actual_water_use = min(
        max(
            0,
            water_before_use - environment.wilting_point_mm,
        ),
        potential_water_use * water_stress,
    )

    soil_water_after = max(
        environment.wilting_point_mm,
        water_before_use - actual_water_use,
    )

    # 3. Existing permanent tissue loss reduces future growth
    living_tissue_factor = max(
        0.0,
        1.0 - (
            plant.state.permanent_tissue_loss_percent / 100
        ),
    )

    # 4. Light interception and potential biomass
    intercepted_par = (
        environment.daily_par_mj_m2 * canopy_fraction
    )

    potential_biomass_gain = (
        intercepted_par
        * crop.radiation_use_efficiency
        * temperature_stress
        * water_stress
        * environment.plant_area_m2
        * living_tissue_factor
    )

    # 5. Nutrient stress and nutrient uptake
    nutrient_result = calculate_nutrient_effect(
        species=species,
        nitrogen_mg_kg=environment.nitrogen_mg_kg,
        phosphorus_mg_kg=environment.phosphorus_mg_kg,
        potassium_mg_kg=environment.potassium_mg_kg,
        soil_ph=environment.soil_ph,
        ec_ds_m=environment.ec_ds_m,
        soil_mass_kg=environment.soil_mass_kg,
    )

    biomass_gain = (
        potential_biomass_gain
        * (1.0 - nutrient_result.overall_stress)
    )

    nutrient_result = calculate_nutrient_effect(
        species=species,
        nitrogen_mg_kg=environment.nitrogen_mg_kg,
        phosphorus_mg_kg=environment.phosphorus_mg_kg,
        potassium_mg_kg=environment.potassium_mg_kg,
        soil_ph=environment.soil_ph,
        ec_ds_m=environment.ec_ds_m,
        biomass_gain_g=biomass_gain,
        soil_mass_kg=environment.soil_mass_kg,
    )

    # 6. Canopy development
    canopy_growth = (
        crop.maximum_canopy_cover
        - plant.state.canopy_cover_percent
    ) * (
        1 - math.exp(-0.0015 * thermal_time)
    ) * temperature_stress * water_stress * living_tissue_factor

    new_canopy = min(
        crop.maximum_canopy_cover,
        plant.state.canopy_cover_percent + canopy_growth,
    )

    # 7. Root development
    root_growth = (
        thermal_time * 0.03
        * temperature_stress
        * water_stress
        * living_tissue_factor
    )

    new_root_depth = min(
        crop.maximum_root_depth_cm,
        plant.state.root_depth_cm + root_growth,
    )

    # 8. Leaf development
    cumulative_thermal_time = (
        plant.state.thermal_time_cumulative + thermal_time
    )

    new_leaf_count = max(
        plant.state.leaf_count,
        int(cumulative_thermal_time / crop.phyllochron),
    )

    # 9. Plant height
    height_growth = (
        thermal_time * 0.01
        * temperature_stress
        * water_stress
        * living_tissue_factor
    )

    new_height = plant.state.height_cm + height_growth

    # 10. Lifecycle stage
    new_stage = plant.state.growth_stage

    for threshold, stage in STAGE_THRESHOLDS[species]:
        if cumulative_thermal_time >= threshold:
            new_stage = stage

    # 11. Seed reserve
    remaining_seed_reserve = max(
        0,
        plant.state.seed_reserve_remaining_g
        - thermal_time * 0.0005,
    )

    # 12. Plant health
    light_factor = min(
        1.0,
        environment.daily_par_mj_m2
        / LIGHT_REFERENCE_PAR[species],
    )

    nutrient_factor = max(
        0.0,
        min(1.0, 1.0 - nutrient_result.overall_stress),
    )

    salinity_factor = max(
        0.0,
        min(1.0, 1.0 - nutrient_result.salinity_stress),
    )

    health = calculate_plant_health(
        temperature_factor=temperature_stress,
        water_factor=water_stress,
        nutrient_factor=nutrient_factor,
        light_factor=light_factor,
        salinity_factor=salinity_factor,
    )

    # 13. Stress accumulation and recovery
    recovery = calculate_recovery(
        previous_stress_days=plant.state.stress_days,
        previous_accumulated_stress=plant.state.accumulated_stress,
        previous_damage_percent=plant.state.damage_percent,
        previous_recovery_days=plant.state.recovery_days,
        health_score=health.health_score,
    )

    # 14. Physical tissue damage
    biomass_before_damage = (
        plant.state.biomass_g + biomass_gain
    )

    damage = calculate_tissue_damage(
        health_score=health.health_score,
        previous_tissue_loss_percent=(
            plant.state.permanent_tissue_loss_percent
        ),
        biomass_g=biomass_before_damage,
        canopy_cover_percent=new_canopy,
    )

    new_biomass = damage.biomass_after_damage_g
    new_canopy = damage.canopy_after_damage_percent

    net_biomass_change = (
        new_biomass - plant.state.biomass_g
    )

    # 15. Recalculate lifecycle using biomass after damage
    lifecycle = calculate_lifecycle(
        species=species,
        cumulative_thermal_time=cumulative_thermal_time,
        biomass_g=new_biomass,
    )

    # 16. Update plant digital twin
    plant.state = plant.state.model_copy(
        update={
            "age_days": plant.state.age_days + 1,
            "thermal_time_cumulative": cumulative_thermal_time,
            "growth_stage": new_stage,
            "height_cm": new_height,
            "leaf_count": new_leaf_count,
            "root_depth_cm": new_root_depth,
            "canopy_cover_percent": new_canopy,
            "biomass_g": new_biomass,
            "seed_reserve_remaining_g": remaining_seed_reserve,

            "flowering_progress_percent": (
                lifecycle.flowering_progress_percent
            ),
            "fruit_development_percent": (
                lifecycle.fruit_development_percent
            ),
            "estimated_yield_g": lifecycle.estimated_yield_g,
            "harvest_readiness_percent": (
                lifecycle.harvest_readiness_percent
            ),
            "harvest_status": lifecycle.harvest_status,

            "health_score": health.health_score,
            "health_status": health.health_status,
            "limiting_factor": health.limiting_factor,
            "recovery_potential_percent": health.recovery_potential,

            "stress_days": recovery.stress_days,
            "accumulated_stress": recovery.accumulated_stress,
            "damage_percent": recovery.damage_percent,
            "recovery_days": recovery.recovery_days,

            "permanent_tissue_loss_percent": (
                damage.permanent_tissue_loss_percent
            ),
        }
    )

    # 17. Daily simulation result
    return {
        "plant_id": plant.plant_id,
        "species": species,
        "age_days": plant.state.age_days,
        "growth_stage": new_stage.value,

        "thermal_time": round(thermal_time, 2),
        "cumulative_thermal_time": round(
            cumulative_thermal_time, 2
        ),

        "temperature_stress": round(temperature_stress, 3),
        "water_stress": round(water_stress, 3),

        "soil_water_mm": round(soil_water_after, 4),
        "actual_water_use_mm": round(actual_water_use, 4),

        "intercepted_par_mj_m2": round(intercepted_par, 2),

        "biomass_gain_g": round(biomass_gain, 4),
        "net_biomass_change_g": round(net_biomass_change, 4),
        "total_biomass_g": round(new_biomass, 4),

        "height_cm": round(new_height, 2),
        "root_depth_cm": round(new_root_depth, 2),
        "leaf_count": new_leaf_count,
        "canopy_cover_percent": round(new_canopy, 2),

        "seed_reserve_remaining_g": round(
            remaining_seed_reserve, 4
        ),

        "nutrient_stress": round(
            nutrient_result.overall_stress, 4
        ),
        "nitrogen_stress": round(
            nutrient_result.nitrogen_stress, 4
        ),
        "phosphorus_stress": round(
            nutrient_result.phosphorus_stress, 4
        ),
        "potassium_stress": round(
            nutrient_result.potassium_stress, 4
        ),
        "ph_stress": round(nutrient_result.ph_stress, 4),
        "salinity_stress": round(
            nutrient_result.salinity_stress, 4
        ),

        "updated_soil_npk": {
            "nitrogen_mg_kg": nutrient_result.updated_nitrogen_mg_kg,
            "phosphorus_mg_kg": nutrient_result.updated_phosphorus_mg_kg,
            "potassium_mg_kg": nutrient_result.updated_potassium_mg_kg,
        },

        "lifecycle": {
            "flowering_progress_percent": (
                lifecycle.flowering_progress_percent
            ),
            "fruit_development_percent": (
                lifecycle.fruit_development_percent
            ),
            "estimated_yield_g": lifecycle.estimated_yield_g,
            "harvest_readiness_percent": (
                lifecycle.harvest_readiness_percent
            ),
            "harvest_status": lifecycle.harvest_status,
        },

        "health": {
            "health_score": health.health_score,
            "health_status": health.health_status,
            "limiting_factor": health.limiting_factor,
            "temperature_stress": health.temperature_stress,
            "water_stress": health.water_stress,
            "nutrient_stress": health.nutrient_stress,
            "light_stress": health.light_stress,
            "salinity_stress": health.salinity_stress,
            "recovery_potential": health.recovery_potential,
        },

        "recovery": {
            "stress_days": recovery.stress_days,
            "accumulated_stress": recovery.accumulated_stress,
            "damage_percent": recovery.damage_percent,
            "recovery_days": recovery.recovery_days,
            "recovery_rate": recovery.recovery_rate,
            "plant_condition": recovery.plant_condition,
        },

        "physical_damage": {
            "daily_tissue_loss_percent": (
                damage.daily_tissue_loss_percent
            ),
            "permanent_tissue_loss_percent": (
                damage.permanent_tissue_loss_percent
            ),
            "living_tissue_factor": damage.living_tissue_factor,
            "biomass_loss_g": damage.biomass_loss_g,
            "canopy_after_damage_percent": round(
                new_canopy, 2
            ),
        },
    }
