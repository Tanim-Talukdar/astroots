
from simulation.biology.recovery import calculate_recovery


def test_stress_accumulation():
    result = calculate_recovery(0, 0, 0, 0, 40)

    assert result.stress_days == 1
    assert result.accumulated_stress == 9
    assert result.damage_percent == 1.5
    assert result.plant_condition == "Recovering" or result.plant_condition == "Under Stress"


def test_gradual_recovery():
    result = calculate_recovery(5, 30, 10, 0, 95)

    assert result.stress_days == 4
    assert result.accumulated_stress == 27
    assert result.damage_percent == 9.5
    assert result.recovery_days == 1


def test_damage_limit():
    result = calculate_recovery(10, 90, 99, 0, 20)

    assert result.damage_percent <= 100
    assert result.accumulated_stress <= 100


def test_repeated_stress():
    state = (0, 0, 0, 0)

    for _ in range(10):
        result = calculate_recovery(*state, 40)
        state = (
            result.stress_days,
            result.accumulated_stress,
            result.damage_percent,
            result.recovery_days,
        )

    assert result.stress_days == 10
    assert result.damage_percent > 0


if __name__ == "__main__":
    test_stress_accumulation()
    test_gradual_recovery()
    test_damage_limit()
    test_repeated_stress()
    print("All recovery tests passed!")
