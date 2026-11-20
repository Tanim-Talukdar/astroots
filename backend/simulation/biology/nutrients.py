
from dataclasses import dataclass


@dataclass(frozen=True)
class NutrientRequirements:
    nitrogen_mg_kg: float
    phosphorus_mg_kg: float
    potassium_mg_kg: float
    optimal_ph_min: float
    optimal_ph_max: float
    ec_limit_ds_m: float


CROP_REQUIREMENTS = {
    "tomato": NutrientRequirements(80, 30, 100, 5.8, 6.8, 2.5),
    "cucumber": NutrientRequirements(100, 35, 120, 5.5, 6.5, 2.5),
    "lettuce": NutrientRequirements(90, 35, 110, 5.8, 6.5, 1.3),
}


@dataclass
class NutrientResult:
    nitrogen_stress: float
    phosphorus_stress: float
    potassium_stress: float
    ph_stress: float
    salinity_stress: float
    overall_stress: float
    updated_nitrogen_mg_kg: float
    updated_phosphorus_mg_kg: float
    updated_potassium_mg_kg: float


def _sufficiency(actual: float, required: float) -> float:
    if actual < 0 or required <= 0:
        raise ValueError("Nutrient values must be non-negative.")
    return min(actual / required, 1.0)


def _ph_sufficiency(
    ph: float,
    minimum: float,
    maximum: float,
) -> float:
    if not 0 <= ph <= 14:
        raise ValueError("Soil pH must be between 0 and 14.")

    if minimum <= ph <= maximum:
        return 1.0

    distance = minimum - ph if ph < minimum else ph - maximum
    return max(0.0, 1.0 - distance / 2.0)


def _salinity_sufficiency(ec: float, limit: float) -> float:
    if ec < 0:
        raise ValueError("EC cannot be negative.")

    if ec <= limit:
        return 1.0

    return max(0.0, 1.0 - (ec - limit) / 4.0)


def calculate_nutrient_effect(
    species: str,
    nitrogen_mg_kg: float,
    phosphorus_mg_kg: float,
    potassium_mg_kg: float,
    soil_ph: float,
    ec_ds_m: float,
    biomass_gain_g: float = 0.0,
    soil_mass_kg: float = 20.0,
) -> NutrientResult:
    """
    Estimate nutrient and soil-condition effects on daily plant growth.

    NPK concentrations are mg/kg of soil.
    EC is dS/m.
    Biomass gain is grams per simulated day.
    """

    if species not in CROP_REQUIREMENTS:
        raise ValueError(f"Unsupported crop: {species}")

    if biomass_gain_g < 0 or soil_mass_kg <= 0:
        raise ValueError("Biomass gain must be non-negative and soil mass positive.")

    requirements = CROP_REQUIREMENTS[species]

    n = _sufficiency(nitrogen_mg_kg, requirements.nitrogen_mg_kg)
    p = _sufficiency(phosphorus_mg_kg, requirements.phosphorus_mg_kg)
    k = _sufficiency(potassium_mg_kg, requirements.potassium_mg_kg)

    ph = _ph_sufficiency(
        soil_ph,
        requirements.optimal_ph_min,
        requirements.optimal_ph_max,
    )
    salinity = _salinity_sufficiency(ec_ds_m, requirements.ec_limit_ds_m)

    # Nutrient balance: the most limiting nutrient has a strong influence.
    nutrient_sufficiency = (
        0.40 * n +
        0.30 * p +
        0.30 * k
    )

    overall_sufficiency = (
        nutrient_sufficiency *
        ph *
        salinity
    )

    # Approximate daily uptake based on new biomass.
    # These are provisional tissue composition assumptions.
    nitrogen_uptake_mg = biomass_gain_g * 30.0
    phosphorus_uptake_mg = biomass_gain_g * 5.0
    potassium_uptake_mg = biomass_gain_g * 30.0

    updated_n = max(
        0.0,
        nitrogen_mg_kg - nitrogen_uptake_mg / soil_mass_kg,
    )
    updated_p = max(
        0.0,
        phosphorus_mg_kg - phosphorus_uptake_mg / soil_mass_kg,
    )
    updated_k = max(
        0.0,
        potassium_mg_kg - potassium_uptake_mg / soil_mass_kg,
    )

    return NutrientResult(
        nitrogen_stress=1.0 - n,
        phosphorus_stress=1.0 - p,
        potassium_stress=1.0 - k,
        ph_stress=1.0 - ph,
        salinity_stress=1.0 - salinity,
        overall_stress=1.0 - overall_sufficiency,
        updated_nitrogen_mg_kg=updated_n,
        updated_phosphorus_mg_kg=updated_p,
        updated_potassium_mg_kg=updated_k,
    )
