
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
    """Keep environmental response factors within the 0–1 range."""
    return max(0.0, min(1.0, float(value)))


def _health_status(score: float, weakest_factor: float) -> str:
    """Combine the overall score with a safeguard for critical individual stress."""
    if weakest_factor <= 0.10:
        return "Critical"

    if weakest_factor <= 0.25:
        return "Severe Stress"

    if weakest_factor <= 0.40:
        return "Moderate Stress"

    if weakest_factor <= 0.60:
        return "Mild Stress"

    if score >= 85:
        return "Healthy"

    if score >= 70:
        return "Mild Stress"

    if score >= 50:
        return "Moderate Stress"

    if score >= 30:
        return "Severe Stress"

    return "Critical"


def calculate_plant_health(
    temperature_factor: float,
    water_factor: float,
    nutrient_factor: float,
    light_factor: float,
    salinity_factor: float,
) -> PlantHealthResult:
    """
    Estimate plant health from environmental response factors.

    Each input represents a factor from 0 (extreme limitation)
    to 1 (no limitation).

    The score combines weighted environmental performance with
    a weakest-factor adjustment so critical stress is not hidden.
    """

    factors = {
        "temperature": _factor(temperature_factor),
        "water": _factor(water_factor),
        "nutrients": _factor(nutrient_factor),
        "light": _factor(light_factor),
        "salinity": _factor(salinity_factor),
    }

    weighted_score = sum(
        factors[name] * WEIGHTS[name]
        for name in factors
    )

    weakest_factor = min(factors.values())

    # A severe limitation in one factor must meaningfully reduce health.
    adjusted_score = weighted_score * (
        0.5 + 0.5 * weakest_factor
    )

    health_score = round(adjusted_score * 100, 2)

    limiting_factor = min(factors, key=factors.get)

    health_status = _health_status(
        health_score,
        weakest_factor,
    )

    recovery_potential = round(
        max(0.0, min(100.0, health_score + 15.0)),
        2,
    )

    return PlantHealthResult(
        health_score=health_score,
        health_status=health_status,
        limiting_factor=limiting_factor,
        temperature_stress=round(1.0 - factors["temperature"], 4),
        water_stress=round(1.0 - factors["water"], 4),
        nutrient_stress=round(1.0 - factors["nutrients"], 4),
        light_stress=round(1.0 - factors["light"], 4),
        salinity_stress=round(1.0 - factors["salinity"], 4),
        recovery_potential=recovery_potential,
    )
