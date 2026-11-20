
import math

from app.models.plant import PlantRecord, PlantProfile
from simulation.biology.growth import (
    DailyGrowthInput,
    simulate_growth_day,
)
from simulation.biology.parameters import CROP_PARAMETERS

SPECIES = ["tomato", "cucumber", "lettuce"]


def create_healthy_environment(temperature_c=20):
    return DailyGrowthInput(
        temperature_c=temperature_c,
        daily_par_mj_m2=20,
        soil_water_mm=140,
        field_capacity_mm=150,
        wilting_point_mm=30,
        irrigation_mm=5,
        rainfall_mm=0,
        reference_et_mm=4,
        soil_ph=6.2,
        ec_ds_m=0.8,
        nitrogen_mg_kg=200,
        phosphorus_mg_kg=80,
        potassium_mg_kg=200,
        soil_mass_kg=20,
    )


def create_stress_environment():
    return DailyGrowthInput(
        temperature_c=40,
        daily_par_mj_m2=0.5,
        soil_water_mm=30,
        field_capacity_mm=150,
        wilting_point_mm=30,
        irrigation_mm=0,
        rainfall_mm=0,
        reference_et_mm=4,
        soil_ph=4.0,
        ec_ds_m=5.0,
        nitrogen_mg_kg=0,
        phosphorus_mg_kg=0,
        potassium_mg_kg=0,
        soil_mass_kg=20,
    )


def simulate_days(plant, environment, days):
    latest_result = None

    for _ in range(days):
        latest_result = simulate_growth_day(plant, environment)

        updated_npk = latest_result["updated_soil_npk"]

        environment = environment.model_copy(
            update={
                "soil_water_mm": latest_result["soil_water_mm"],
                "nitrogen_mg_kg": updated_npk["nitrogen_mg_kg"],
                "phosphorus_mg_kg": updated_npk["phosphorus_mg_kg"],
                "potassium_mg_kg": updated_npk["potassium_mg_kg"],
            }
        )

    return latest_result


def validate_plant_state(plant):
    state = plant.state

    numeric_values = [
        state.biomass_g,
        state.height_cm,
        state.root_depth_cm,
        state.canopy_cover_percent,
        state.health_score,
        state.permanent_tissue_loss_percent,
        state.accumulated_stress,
        state.damage_percent,
    ]

    for value in numeric_values:
        assert math.isfinite(value), "Plant state contains an invalid number."

    assert state.biomass_g >= 0
    assert state.height_cm >= 0
    assert state.root_depth_cm >= 0
    assert 0 <= state.canopy_cover_percent <= 100
    assert 0 <= state.health_score <= 100
    assert 0 <= state.permanent_tissue_loss_percent <= 100
    assert 0 <= state.accumulated_stress <= 100
    assert 0 <= state.damage_percent <= 100
    assert state.leaf_count >= 0


def test_healthy_long_term_growth():
    for species in SPECIES:
        plant = PlantRecord(profile=PlantProfile(species=species))

        result = simulate_days(
            plant,
            create_healthy_environment(
                CROP_PARAMETERS[species].optimal_temperature_c
            ),
            30,
        )

        validate_plant_state(plant)

        assert plant.state.age_days == 30
        assert plant.state.biomass_g > 0
        assert plant.state.canopy_cover_percent > 0
        assert plant.state.health_score > 50
        assert plant.state.permanent_tissue_loss_percent < 0.001

        print(
            f"{species.upper()} HEALTHY: "
            f"Biomass={result['total_biomass_g']}g, "
            f"Health={plant.state.health_score}, "
            f"Canopy={plant.state.canopy_cover_percent}%"
        )


def test_continuous_stress_damage():
    for species in SPECIES:
        plant = PlantRecord(profile=PlantProfile(species=species))

        result = simulate_days(
            plant,
            create_stress_environment(),
            20,
        )

        validate_plant_state(plant)

        assert plant.state.age_days == 20
        assert plant.state.health_score < 50
        assert plant.state.stress_days > 0
        assert plant.state.permanent_tissue_loss_percent > 0
        assert result["physical_damage"]["daily_tissue_loss_percent"] > 0

        print(
            f"{species.upper()} STRESS: "
            f"Health={plant.state.health_score}, "
            f"Permanent tissue loss="
            f"{plant.state.permanent_tissue_loss_percent}%"
        )

def test_recovery_after_stress():
    for species in SPECIES:
        plant = PlantRecord(profile=PlantProfile(species=species))

        simulate_days(
            plant,
            create_stress_environment(),
            20,
        )

        stressed_health = plant.state.health_score
        permanent_damage = plant.state.permanent_tissue_loss_percent

        recovery_result = simulate_days(
            plant,
            create_healthy_environment(
                CROP_PARAMETERS[species].optimal_temperature_c
            ),
            15,
        )

        validate_plant_state(plant)

        assert plant.state.health_score > stressed_health
        assert plant.state.permanent_tissue_loss_percent >= permanent_damage
        assert plant.state.recovery_days > 0

        print(
            f"{species.upper()} RECOVERY: "
            f"Health {stressed_health} -> {plant.state.health_score}, "
            f"Permanent tissue loss="
            f"{plant.state.permanent_tissue_loss_percent}%"
        )

if __name__ == "__main__":
    test_healthy_long_term_growth()
    print("\nHealthy growth validation passed!")

    test_continuous_stress_damage()
    print("\nContinuous stress validation passed!")

    test_recovery_after_stress()
    print("\nRecovery validation passed!")

    print("\nAll long-term validation tests passed!")
