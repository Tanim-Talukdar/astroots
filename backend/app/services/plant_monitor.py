
from app.models.history import DailyGrowthRecord


# Temporary in-memory history store.
# Records will reset when the backend restarts.
_growth_history: dict[str, list[DailyGrowthRecord]] = {}


def record_daily_growth(
    plant,
    result: dict,
    environment,
) -> DailyGrowthRecord:

    record = DailyGrowthRecord(
        plant_id=plant.plant_id,
        day=result["age_days"],
        growth_stage=result["growth_stage"],
        height_cm=result["height_cm"],
        leaf_count=result["leaf_count"],
        root_depth_cm=result["root_depth_cm"],
        canopy_cover_percent=result["canopy_cover_percent"],
        biomass_g=result["total_biomass_g"],
        thermal_time=result["thermal_time"],
        water_stress=result["water_stress"],
        temperature_stress=result["temperature_stress"],
        environment=environment.model_dump(),
    )

    _growth_history.setdefault(
        plant.plant_id, []
    ).append(record)

    return record


def get_growth_history(plant_id: str) -> list[DailyGrowthRecord]:
    return _growth_history.get(plant_id, [])


def get_latest_growth(plant_id: str):
    history = get_growth_history(plant_id)
    return history[-1] if history else None


def clear_growth_history(plant_id: str):
    _growth_history.pop(plant_id, None)
