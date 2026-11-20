from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.plant import PlantRecord

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Demo storage: diagnosis metadata is held in memory.
# Uploaded image files are written to backend/uploads.
_diagnoses: dict[str, list[dict]] = {}


def add_diagnosis(
    plant: PlantRecord,
    image_bytes: bytes,
    content_type: str,
    analysis: dict,
) -> dict:
    extension_by_type = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    extension = extension_by_type[content_type]
    filename = f"{uuid4().hex}{extension}"
    image_path = UPLOAD_DIR / filename
    image_path.write_bytes(image_bytes)

    diagnosis = {
        "diagnosis_id": str(uuid4()),
        "plant_id": plant.plant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image_url": f"/uploads/{filename}",
        "analysis": analysis,
    }
    _diagnoses.setdefault(plant.plant_id, []).insert(0, diagnosis)
    return diagnosis


def get_plant_diagnoses(plant_id: str) -> list[dict]:
    return list(_diagnoses.get(plant_id, []))
