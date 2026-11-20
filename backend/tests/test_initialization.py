
from app.models.plant import PlantRecord, PlantProfile
from simulation.biology.growth import (
    DailyGrowthInput,
    simulate_growth_day,
)

environment = DailyGrowthInput(
    temperature_c=25,
    daily_par_mj_m2=15,
    soil_water_mm=100,
    field_capacity_mm=150,
    wilting_point_mm=30,
    irrigation_mm=5,
    reference_et_mm=4,
)

for species in ["tomato", "cucumber", "lettuce"]:
    plant = PlantRecord(
        profile=PlantProfile(species=species)
    )

    print(f"\n{species.upper()} BEFORE SIMULATION")
    print("Initial leaves:", plant.state.leaf_count)

    result = simulate_growth_day(plant, environment)

    print("Initialized:", plant.state.is_initialized)
    print("Age:", result["age_days"])
    print("Leaves:", result["leaf_count"])
    print("Biomass:", result["total_biomass_g"], "g")
    print("Canopy:", result["canopy_cover_percent"], "%")
    print(
        "Remaining seed reserve:",
        plant.state.seed_reserve_remaining_g,
        "g",
    )

    assert plant.state.is_initialized
    assert result["leaf_count"] >= 2
    assert result["total_biomass_g"] > 0
    assert result["canopy_cover_percent"] > 0

print("\nAll initial development tests passed!")
