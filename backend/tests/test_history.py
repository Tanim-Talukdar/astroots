
from app.models.plant import PlantRecord, PlantProfile
from simulation.biology.growth import (
    DailyGrowthInput,
    simulate_growth_day,
)
from app.services.plant_monitor import (
    record_daily_growth,
    get_growth_history,
    get_latest_growth,
)


plant = PlantRecord(
    profile=PlantProfile(species="tomato")
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

# Simulate and record 30 days.
for _ in range(30):
    result = simulate_growth_day(plant, environment)
    record_daily_growth(plant, result, environment)

history = get_growth_history(plant.plant_id)
latest = get_latest_growth(plant.plant_id)

print("Growth history test successful!")
print("Plant:", plant.profile.species)
print("Recorded days:", len(history))
print("First day:", history[0].day)
print("Latest day:", latest.day)
print("Latest biomass:", latest.biomass_g, "g")
print("Latest canopy:", latest.canopy_cover_percent, "%")
