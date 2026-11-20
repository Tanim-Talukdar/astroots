
from simulation.biology.recovery import calculate_recovery


def test_stress_accumulates():
    result = calculate_recovery(
        previous_stress_days=0,
        previous_accumulated_stress=0,
        previous_damage_percent=0,
        previous_recovery_days=0,
        health_score=40,
    )

    assert result.stress_days == 1
    assert result.accumulated_stress > 0
    assert result.damage_percent > 0
    assert result.plant_condition == "Under Stress"


def test_severe_stress_increases_damage():
    result = calculate_recovery(
        previous_stress_days=5,
        previous_accumulated_stress=20,
        previous_damage_percent=14,
        previous_recovery_days=0,
        health_score=10,
    )

    assert result.stress_days == 6
    assert result.damage_percent > 10
    assert result.plant_condition == "Moderate Damage"


def test_recovery_requires_stress_history():
    result = calculate_recovery(
        previous_stress_days=0,
        previous_accumulated_stress=0,
        previous_damage_percent=0,
        previous_recovery_days=0,
        health_score=95,
    )

    assert result.recovery_days == 0
    assert result.stress_days == 0
    assert result.plant_condition == "Healthy"


def test_recovery_reduces_reversible_stress():
    result = calculate_recovery(
        previous_stress_days=10,
        previous_accumulated_stress=30,
        previous_damage_percent=10,
        previous_recovery_days=0,
        health_score=90,
    )

    assert result.recovery_days == 1
    assert result.accumulated_stress < 30
    assert result.damage_percent < 10
    assert result.plant_condition == "Recovering"


def test_low_health_does_not_improve_recovery():
    result = calculate_recovery(
        previous_stress_days=5,
        previous_accumulated_stress=30,
        previous_damage_percent=10,
        previous_recovery_days=0,
        health_score=55,
    )

    assert result.stress_days == 6
    assert result.recovery_days == 0
    assert result.accumulated_stress == 36.75
    assert result.damage_percent == 11.125


def test_recovery_never_reduces_stress_day_history():
    result = calculate_recovery(
        previous_stress_days=12,
        previous_accumulated_stress=20,
        previous_damage_percent=5,
        previous_recovery_days=3,
        health_score=90,
    )

    assert result.stress_days == 12
    assert result.recovery_days == 4


def test_values_are_clamped():
    result = calculate_recovery(
        previous_stress_days=-5,
        previous_accumulated_stress=150,
        previous_damage_percent=-10,
        previous_recovery_days=-2,
        health_score=150,
    )

    assert result.stress_days == 0
    assert result.accumulated_stress <= 100
    assert result.damage_percent >= 0
    assert result.recovery_days == 1


if __name__ == "__main__":
    test_stress_accumulates()
    test_severe_stress_increases_damage()
    test_recovery_requires_stress_history()
    test_recovery_reduces_reversible_stress()
    test_low_health_does_not_improve_recovery()
    test_recovery_never_reduces_stress_day_history()
    test_values_are_clamped()

    print("All recovery tests passed!")
