
from fastapi import APIRouter, HTTPException

from app.models.plant import PlantRecord, PlantProfile
from app.services.plant_registry import (
    register_plant,
    get_plant,
    get_all_plants,
)
from app.services.plant_monitor import (
    record_daily_growth,
    get_growth_history,
    get_latest_growth,
)
from app.services.soil_monitor import (
    apply_soil_state,
    update_soil_state,
    get_soil_state,
)
from simulation.biology.growth import (
    DailyGrowthInput,
    simulate_growth_day,
    initialize_plant,
)

router = APIRouter(prefix="/api/plants", tags=["Plants"])


@router.post("/")
def create_plant(profile: PlantProfile):
    try:
        plant = PlantRecord(profile=profile)
        initialize_plant(plant)
        register_plant(plant)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return {
        "message": "Plant registered successfully",
        "plant": plant,
    }


@router.get("/")
def list_plants():
    plants = get_all_plants()

    return {
        "total": len(plants),
        "plants": plants,
    }


@router.get("/{plant_id}")
def plant_status(plant_id: str):
    plant = get_plant(plant_id)

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found",
        )

    return plant


@router.post("/{plant_id}/simulate")
def simulate_plant_day(
    plant_id: str,
    environment: DailyGrowthInput,
):
    plant = get_plant(plant_id)

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found",
        )

    # First simulation uses supplied soil values.
    # Later simulations use the previous day's remaining soil values.
    effective_environment = apply_soil_state(
        plant_id,
        environment,
    )

    try:
        result = simulate_growth_day(
            plant,
            effective_environment,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    # Save soil conditions for the next simulated day.
    update_soil_state(plant_id, result)

    record_daily_growth(
        plant,
        result,
        effective_environment,
    )

    return {
        "message": "Daily growth simulation completed",
        "result": result,
        "soil_state": get_soil_state(plant_id),
    }


@router.get("/{plant_id}/history")
def plant_history(plant_id: str):
    if not get_plant(plant_id):
        raise HTTPException(
            status_code=404,
            detail="Plant not found",
        )

    history = get_growth_history(plant_id)

    return {
        "plant_id": plant_id,
        "total_records": len(history),
        "history": history,
    }


@router.get("/{plant_id}/monitor")
def monitor_plant(plant_id: str):
    plant = get_plant(plant_id)

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found",
        )

    latest = get_latest_growth(plant_id)

    return {
        "plant": plant,
        "latest_record": latest,
        "soil_state": get_soil_state(plant_id),
        "monitoring_status": (
            "active" if latest else "awaiting_first_simulation"
        ),
    }
