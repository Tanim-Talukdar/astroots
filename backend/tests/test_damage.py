
from simulation.biology.damage import calculate_tissue_damage


def test_healthy_plant_has_no_damage():
    result = calculate_tissue_damage(
        95, 0, 100, 50
    )

    assert result.daily_tissue_loss_percent == 0
    assert result.biomass_after_damage_g == 100
    assert result.canopy_after_damage_percent == 50


def test_severe_stress_causes_damage():
    result = calculate_tissue_damage(
        0, 0, 100, 50
    )

    assert result.daily_tissue_loss_percent == 0.5
    assert result.biomass_after_damage_g == 99.5
    assert result.canopy_after_damage_percent == 49.75


def test_tissue_loss_accumulates():
    first = calculate_tissue_damage(
        0, 0, 100, 50
    )

    second = calculate_tissue_damage(
        0,
        first.permanent_tissue_loss_percent,
        100,
        50,
    )

    assert (
        second.permanent_tissue_loss_percent
        > first.permanent_tissue_loss_percent
    )


def test_recovery_does_not_restore_dead_tissue():
    first = calculate_tissue_damage(
        0, 0, 100, 50
    )

    recovered = calculate_tissue_damage(
        95,
        first.permanent_tissue_loss_percent,
        100,
        50,
    )

    assert recovered.daily_tissue_loss_percent == 0
    assert (
        recovered.permanent_tissue_loss_percent
        == first.permanent_tissue_loss_percent
    )


if __name__ == "__main__":
    test_healthy_plant_has_no_damage()
    test_severe_stress_causes_damage()
    test_tissue_loss_accumulates()
    test_recovery_does_not_restore_dead_tissue()
    print("All physical damage tests passed!")
