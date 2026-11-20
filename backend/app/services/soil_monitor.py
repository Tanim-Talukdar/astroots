
from typing import Any


# In-memory soil state, indexed by plant ID.
_soil_states: dict[str, dict[str, float]] = {}


def apply_soil_state(plant_id: str, environment: Any) -> Any:
    """
    Use the previous simulation's soil state when available.
    The first simulation uses the values supplied by the user.
    """
    previous = _soil_states.get(plant_id)

    if previous is None:
        return environment

    return environment.model_copy(update=previous)


def update_soil_state(plant_id: str, result: dict) -> None:
    """Save soil conditions after a completed simulation."""
    npk = result["updated_soil_npk"]

    _soil_states[plant_id] = {
        "soil_water_mm": result["soil_water_mm"],
        "nitrogen_mg_kg": npk["nitrogen_mg_kg"],
        "phosphorus_mg_kg": npk["phosphorus_mg_kg"],
        "potassium_mg_kg": npk["potassium_mg_kg"],
    }


def get_soil_state(plant_id: str) -> dict[str, float] | None:
    """Return the latest saved soil conditions."""
    state = _soil_states.get(plant_id)
    return state.copy() if state else None


def clear_soil_state(plant_id: str) -> None:
    """Clear saved soil conditions for a plant."""
    _soil_states.pop(plant_id, None)
