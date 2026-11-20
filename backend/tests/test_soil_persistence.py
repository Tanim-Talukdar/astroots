
from simulation.biology.growth import DailyGrowthInput
from app.services.soil_monitor import (
    apply_soil_state,
    update_soil_state,
    get_soil_state,
    clear_soil_state,
)


def test_soil_persistence():
    plant_id = "test-soil-plant"

    clear_soil_state(plant_id)

    first_day = DailyGrowthInput(
        temperature_c=25,
        daily_par_mj_m2=15,
        soil_water_mm=100,
        field_capacity_mm=150,
        wilting_point_mm=30,
        reference_et_mm=4,
        nitrogen_mg_kg=120,
        phosphorus_mg_kg=40,
        potassium_mg_kg=150,
    )

    # First simulation should use the supplied values.
    first_environment = apply_soil_state(plant_id, first_day)

    assert first_environment.soil_water_mm == 100
    assert first_environment.nitrogen_mg_kg == 120

    # Simulate the result of the first day.
    first_result = {
        "soil_water_mm": 95.5,
        "updated_soil_npk": {
            "nitrogen_mg_kg": 118.0,
            "phosphorus_mg_kg": 39.0,
            "potassium_mg_kg": 148.0,
        },
    }

    update_soil_state(plant_id, first_result)

    # The second day's request deliberately contains old soil values.
    second_day = first_day.model_copy(
        update={
            "soil_water_mm": 100,
            "nitrogen_mg_kg": 120,
            "phosphorus_mg_kg": 40,
            "potassium_mg_kg": 150,
        }
    )

    second_environment = apply_soil_state(plant_id, second_day)

    assert second_environment.soil_water_mm == 95.5
    assert second_environment.nitrogen_mg_kg == 118.0
    assert second_environment.phosphorus_mg_kg == 39.0
    assert second_environment.potassium_mg_kg == 148.0

    saved_state = get_soil_state(plant_id)

    assert saved_state["soil_water_mm"] == 95.5

    clear_soil_state(plant_id)

    print("Soil persistence test passed!")


if __name__ == "__main__":
    test_soil_persistence()
