from fastapi import APIRouter, HTTPException, UploadFile, File

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
from app.services.plant_vision import analyze_plant_image
from app.services.diagnosis_registry import (
    add_diagnosis,
    get_plant_diagnoses,
)

from simulation.biology.growth import (
    DailyGrowthInput,
    simulate_growth_day,
    initialize_plant,
)

router = APIRouter(prefix="/api/plants", tags=["Plants"])


class PlantRegistrationRequest(PlantProfile):
    zone_id: str | None = None

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024


async def read_plant_image(image: UploadFile) -> bytes:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPG, PNG, or WebP image.",
        )

    image_bytes = await image.read(MAX_UPLOAD_BYTES + 1)
    await image.close()

    if not image_bytes or len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=422,
            detail="Image must be between 1 byte and 8 MB.",
        )

    return image_bytes


@router.post("/")
def create_plant(profile: PlantRegistrationRequest):
    try:
        plant_profile = PlantProfile(
            **profile.model_dump(exclude={"zone_id"})
        )
        plant = PlantRecord(
            profile=plant_profile,
            zone_id=profile.zone_id,
        )
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
    return {"total": len(plants), "plants": plants}


@router.get("/{plant_id}")
def plant_status(plant_id: str):
    plant = get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@router.post("/{plant_id}/simulate")
def simulate_plant_day(
    plant_id: str,
    environment: DailyGrowthInput,
):
    plant = get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    effective_environment = apply_soil_state(plant_id, environment)

    try:
        result = simulate_growth_day(plant, effective_environment)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    update_soil_state(plant_id, result)
    record_daily_growth(plant, result, effective_environment)

    return {
        "message": "Daily growth simulation completed",
        "result": result,
        "soil_state": get_soil_state(plant_id),
    }


@router.get("/{plant_id}/history")
def plant_history(plant_id: str):
    if not get_plant(plant_id):
        raise HTTPException(status_code=404, detail="Plant not found")

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
        raise HTTPException(status_code=404, detail="Plant not found")

    latest = get_latest_growth(plant_id)
    return {
        "plant": plant,
        "latest_record": latest,
        "soil_state": get_soil_state(plant_id),
        "monitoring_status": (
            "active" if latest else "awaiting_first_simulation"
        ),
    }


@router.post("/analyze-image")
async def analyze_plant_photo(image: UploadFile = File(...)):
    image_bytes = await read_plant_image(image)
    try:
        return analyze_plant_image(image_bytes)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Plant vision model is unavailable.",
        ) from error


@router.post("/{plant_id}/analyze-image")
async def analyze_image_for_plant(
    plant_id: str,
    image: UploadFile = File(...),
):
    plant = get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    image_bytes = await read_plant_image(image)

    try:
        analysis = analyze_plant_image(image_bytes)
        diagnosis = add_diagnosis(
            plant=plant,
            image_bytes=image_bytes,
            content_type=image.content_type,
            analysis=analysis,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Plant vision model or diagnosis storage is unavailable.",
        ) from error

    return {
        "message": "Plant image analyzed and diagnosis saved",
        "diagnosis": diagnosis,
    }


@router.get("/{plant_id}/diagnoses")
def plant_diagnoses(plant_id: str):
    if not get_plant(plant_id):
        raise HTTPException(status_code=404, detail="Plant not found")

    diagnoses = get_plant_diagnoses(plant_id)
    return {
        "plant_id": plant_id,
        "total_records": len(diagnoses),
        "diagnoses": diagnoses,
    }
