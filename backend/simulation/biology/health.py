
from dataclasses import dataclass


@dataclass
class PlantHealthResult:
    health_score: float
    health_status: str
    limiting_factor: str
    temperature_stress: float
    water_stress: float
    nutrient_stress: float
    light_stress: float
    salinity_stress: float
    recovery_potential: float


WEIGHTS = {
    "temperature": 0.20,
    "water": 0.25,
    "nutrients": 0.25,
    "light": 0.15,
    "salinity": 0.15,
}


def _factor(value: float) -> float:
    """Clamp a health factor to the range 0–1."""
    return max(0.0, min(1.0, float(value)))


def calculate_plant_health(
    temperature_factor: float,
    water_factor: float,
    nutrient_factor: float,
    light_factor: float,
    salinity_factor: float,
) -> PlantHealthResult:

    factors = {
        "temperature": _factor(temperature_factor),
        "water": _factor(water_factor),
        "nutrients": _factor(nutrient_factor),
        "light": _factor(light_factor),
        "salinity": _factor(salinity_factor),
    }

    score = sum(
        factors[name] * weight
        for name, weight in WEIGHTS.items()
    ) * 100

    limiting_factor = min(factors, key=factors.get)

    if score >= 85:
        status = "Healthy"
    elif score >= 70:
        status = "Mild Stress"
    elif score >= 50:
        status = "Moderate Stress"
    elif score >= 30:
        status = "Severe Stress"
    else:
        status = "Critical"

    # Recovery potential is an estimate, not a guaranteed outcome.
    recovery = max(0.0, min(100.0, score + 15))

    return PlantHealthResult(
        health_score=round(score, 2),
        health_status=status,
        limiting_factor=limiting_factor,
        temperature_stress=round(1 - factors["temperature"], 3),
        water_stress=round(1 - factors["water"], 3),
        nutrient_stress=round(1 - factors["nutrients"], 3),
        light_stress=round(1 - factors["light"], 3),
        salinity_stress=round(1 - factors["salinity"], 3),
        recovery_potential=round(recovery, 2),
    )
