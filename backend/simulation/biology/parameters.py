
from dataclasses import dataclass


@dataclass(frozen=True)
class CropParameters:
    species: str
    base_temperature_c: float
    optimal_temperature_c: float
    maximum_temperature_c: float
    maximum_canopy_cover: float
    maximum_root_depth_cm: float
    water_productivity_g_per_m2: float
    reference_harvest_index: float
    radiation_use_efficiency: float
    phyllochron: float

    initial_leaf_count: int
    initial_root_depth_cm: float
    initial_canopy_cover_percent: float
    initial_biomass_g: float
    initial_seed_reserve_g: float


CROP_PARAMETERS = {
    "tomato": CropParameters(
        species="tomato",
        base_temperature_c=10,
        optimal_temperature_c=25,
        maximum_temperature_c=35,
        maximum_canopy_cover=95,
        maximum_root_depth_cm=100,
        water_productivity_g_per_m2=18,
        reference_harvest_index=0.60,
        radiation_use_efficiency=2.5,
        phyllochron=45,
        initial_leaf_count=2,
        initial_root_depth_cm=1.5,
        initial_canopy_cover_percent=2.0,
        initial_biomass_g=0.08,
        initial_seed_reserve_g=0.02,
    ),
    "cucumber": CropParameters(
        species="cucumber",
        base_temperature_c=12,
        optimal_temperature_c=26,
        maximum_temperature_c=35,
        maximum_canopy_cover=95,
        maximum_root_depth_cm=60,
        water_productivity_g_per_m2=20,
        reference_harvest_index=0.70,
        radiation_use_efficiency=2.8,
        phyllochron=35,
        initial_leaf_count=2,
        initial_root_depth_cm=1.5,
        initial_canopy_cover_percent=2.5,
        initial_biomass_g=0.07,
        initial_seed_reserve_g=0.02,
    ),
    "lettuce": CropParameters(
        species="lettuce",
        base_temperature_c=4,
        optimal_temperature_c=20,
        maximum_temperature_c=30,
        maximum_canopy_cover=95,
        maximum_root_depth_cm=40,
        water_productivity_g_per_m2=15,
        reference_harvest_index=0.90,
        radiation_use_efficiency=2.2,
        phyllochron=30,
        initial_leaf_count=2,
        initial_root_depth_cm=1.0,
        initial_canopy_cover_percent=3.0,
        initial_biomass_g=0.06,
        initial_seed_reserve_g=0.015,
    ),
}
