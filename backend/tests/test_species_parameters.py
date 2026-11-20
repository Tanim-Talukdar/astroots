
from simulation.biology.parameters import CROP_PARAMETERS
from simulation.biology.damage import calculate_tissue_damage
from simulation.biology.recovery import calculate_recovery


def test_all_crops_have_species_parameters():
    for species in ("tomato", "cucumber", "lettuce"):
        crop = CROP_PARAMETERS[species]

        assert crop.damage_sensitivity > 0
        assert crop.recovery_rate > 0


def test_species_have_different_damage_responses():
    results = {}

    for species, crop in CROP_PARAMETERS.items():
        results[species] = calculate_tissue_damage(
            health_score=20,
            previous_tissue_loss_percent=0,
            biomass_g=100,
            canopy_cover_percent=50,
            damage_sensitivity=crop.damage_sensitivity,
        )

    assert (
        results["lettuce"].daily_tissue_loss_percent
        > results["tomato"].daily_tissue_loss_percent
        > results["cucumber"].daily_tissue_loss_percent
    )


def test_species_have_different_recovery_responses():
    results = {}

    for species, crop in CROP_PARAMETERS.items():
        results[species] = calculate_recovery(
            previous_stress_days=5,
            previous_accumulated_stress=30,
            previous_damage_percent=10,
            previous_recovery_days=0,
            health_score=90,
            recovery_rate=crop.recovery_rate,
        )

    assert (
        results["tomato"].accumulated_stress
        < results["lettuce"].accumulated_stress
    )

    assert (
        results["tomato"].accumulated_stress
        < results["cucumber"].accumulated_stress
    )


if __name__ == "__main__":
    test_all_crops_have_species_parameters()
    test_species_have_different_damage_responses()
    test_species_have_different_recovery_responses()

    print("All species parameter tests passed!")
