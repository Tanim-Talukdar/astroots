from simulation.biology.nutrients import calculate_nutrient_effect


def test_healthy_soil():
    result = calculate_nutrient_effect(
        species="tomato",
        nitrogen_mg_kg=120,
        phosphorus_mg_kg=50,
        potassium_mg_kg=150,
        soil_ph=6.3,
        ec_ds_m=1.0,
        biomass_gain_g=1.0,
    )

    assert result.overall_stress == 0
    assert result.updated_nitrogen_mg_kg < 120
    assert result.updated_phosphorus_mg_kg < 50
    assert result.updated_potassium_mg_kg < 150


def test_nutrient_deficiency():
    result = calculate_nutrient_effect(
        species="tomato",
        nitrogen_mg_kg=10,
        phosphorus_mg_kg=5,
        potassium_mg_kg=10,
        soil_ph=6.3,
        ec_ds_m=1.0,
    )

    assert result.overall_stress > 0.5
    assert result.nitrogen_stress > 0
    assert result.phosphorus_stress > 0
    assert result.potassium_stress > 0


def test_bad_soil_conditions():
    result = calculate_nutrient_effect(
        species="lettuce",
        nitrogen_mg_kg=120,
        phosphorus_mg_kg=50,
        potassium_mg_kg=150,
        soil_ph=4.0,
        ec_ds_m=5.0,
    )

    assert result.ph_stress > 0
    assert result.salinity_stress > 0
    assert result.overall_stress > 0


if __name__ == "__main__":
    test_healthy_soil()
    test_nutrient_deficiency()
    test_bad_soil_conditions()
    print("All nutrient modelling tests passed!")