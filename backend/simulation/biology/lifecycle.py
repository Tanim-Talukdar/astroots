
from dataclasses import dataclass


LIFECYCLE_PARAMETERS = {
    "tomato": {
        "flowering_start": 650,
        "fruiting_start": 900,
        "harvest_maturity": 1400,
        "harvest_index": 0.60,
    },
    "cucumber": {
        "flowering_start": 450,
        "fruiting_start": 650,
        "harvest_maturity": 950,
        "harvest_index": 0.70,
    },
    "lettuce": {
        "flowering_start": None,
        "fruiting_start": None,
        "harvest_maturity": 600,
        "harvest_index": 0.90,
    },
}


@dataclass
class LifecycleResult:
    flowering_progress_percent: float
    fruit_development_percent: float
    estimated_yield_g: float
    harvest_readiness_percent: float
    harvest_status: str


def _progress(value: float, start: float, end: float) -> float:
    if end <= start:
        return 0.0

    return max(0.0, min(1.0, (value - start) / (end - start)))


def calculate_lifecycle(
    species: str,
    cumulative_thermal_time: float,
    biomass_g: float,
) -> LifecycleResult:

    if species not in LIFECYCLE_PARAMETERS:
        raise ValueError(f"Unsupported crop: {species}")

    if cumulative_thermal_time < 0 or biomass_g < 0:
        raise ValueError("Thermal time and biomass cannot be negative.")

    params = LIFECYCLE_PARAMETERS[species]

    maturity = params["harvest_maturity"]
    harvest_index = params["harvest_index"]

    if species == "lettuce":
        harvest_progress = _progress(
            cumulative_thermal_time, 0, maturity
        )
        flowering_progress = 0.0
        fruit_progress = 0.0
    else:
        flowering_progress = _progress(
            cumulative_thermal_time,
            params["flowering_start"],
            params["fruiting_start"],
        )

        fruit_progress = _progress(
            cumulative_thermal_time,
            params["fruiting_start"],
            maturity,
        )

        harvest_progress = fruit_progress

    estimated_yield = biomass_g * harvest_index

    if species == "lettuce":
        harvest_status = (
            "ready" if harvest_progress >= 1.0 else "developing"
        )
    else:
        harvest_status = (
            "ready" if harvest_progress >= 1.0
            else "fruit_developing" if fruit_progress > 0
            else "flowering" if flowering_progress > 0
            else "vegetative"
        )

    return LifecycleResult(
        flowering_progress_percent=round(flowering_progress * 100, 2),
        fruit_development_percent=round(fruit_progress * 100, 2),
        estimated_yield_g=round(estimated_yield, 3),
        harvest_readiness_percent=round(harvest_progress * 100, 2),
        harvest_status=harvest_status,
    )
