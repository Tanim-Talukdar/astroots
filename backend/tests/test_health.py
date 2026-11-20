
from simulation.biology.health import calculate_plant_health


def test_healthy_plant():
    result = calculate_plant_health(
        temperature_factor=1.0,
        water_factor=0.95,
        nutrient_factor=0.95,
        light_factor=0.90,
        salinity_factor=1.0,
    )

    assert result.health_score >= 85
    assert result.health_status == "Healthy"


def test_water_stress():
    result = calculate_plant_health(
        temperature_factor=0.95,
        water_factor=0.20,
        nutrient_factor=0.90,
        light_factor=0.90,
        salinity_factor=1.0,
    )

    assert result.limiting_factor == "water"
    assert result.water_stress == 0.8
    assert result.health_status != "Healthy"


def test_critical_plant():
    result = calculate_plant_health(
        temperature_factor=0.1,
        water_factor=0.1,
        nutrient_factor=0.1,
        light_factor=0.1,
        salinity_factor=0.1,
    )

    assert result.health_status == "Critical"


def test_factor_clamping():
    result = calculate_plant_health(
        temperature_factor=1.5,
        water_factor=-0.5,
        nutrient_factor=1.0,
        light_factor=1.0,
        salinity_factor=1.0,
    )

    assert result.temperature_stress == 0
    assert result.water_stress == 1


def test_critical_single_factor_is_not_hidden():
    result = calculate_plant_health(
        temperature_factor=1.0,
        water_factor=1.0,
        nutrient_factor=1.0,
        light_factor=1.0,
        salinity_factor=0.0,
    )

    assert result.limiting_factor == "salinity"
    assert result.health_status == "Critical"


def test_each_factor_can_be_limiting():
    factors = [
        "temperature",
        "water",
        "nutrients",
        "light",
        "salinity",
    ]

    for limiting in factors:
        values = {
            "temperature": 1.0,
            "water": 1.0,
            "nutrients": 1.0,
            "light": 1.0,
            "salinity": 1.0,
        }

        values[limiting] = 0.05

        result = calculate_plant_health(
            temperature_factor=values["temperature"],
            water_factor=values["water"],
            nutrient_factor=values["nutrients"],
            light_factor=values["light"],
            salinity_factor=values["salinity"],
        )

        assert result.limiting_factor == limiting
        assert result.health_status == "Critical"


def test_combined_stress():
    result = calculate_plant_health(
        temperature_factor=0.45,
        water_factor=0.35,
        nutrient_factor=0.50,
        light_factor=0.40,
        salinity_factor=0.55,
    )

    assert result.health_score < 50
    assert result.health_status in (
        "Moderate Stress",
        "Severe Stress",
        "Critical",
    )


if __name__ == "__main__":
    test_healthy_plant()
    test_water_stress()
    test_critical_plant()
    test_factor_clamping()
    test_critical_single_factor_is_not_hidden()
    test_each_factor_can_be_limiting()
    test_combined_stress()

    print("All plant health tests passed!")
