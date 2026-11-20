
from app.models.plant import PlantRecord

_plants: dict[str, PlantRecord] = {}


def register_plant(plant: PlantRecord) -> PlantRecord:
    _plants[plant.plant_id] = plant
    return plant


def get_plant(plant_id: str):
    return _plants.get(plant_id)


def get_all_plants() -> list[PlantRecord]:
    return list(_plants.values())
