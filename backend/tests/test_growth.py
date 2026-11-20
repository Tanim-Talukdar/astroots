
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
    rainfall_mm=0,
    reference_et_mm=4,
)

for species in ["tomato", "cucumber", "lettuce"]:
    plant = PlantRecord(
        profile=PlantProfile(species=species)
    )

    for day in range(30):
        result = simulate_growth_day(plant, environment)

    print(f"\n{species.upper()}")
    print("Age:", result["age_days"])
    print("Stage:", result["growth_stage"])
    print("Height:", result["height_cm"], "cm")
    print("Leaves:", result["leaf_count"])
    print("Biomass:", result["total_biomass_g"], "g")
    print("Canopy:", result["canopy_cover_percent"], "%")
