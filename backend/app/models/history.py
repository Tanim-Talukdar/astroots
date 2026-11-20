
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class DailyGrowthRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid4()))
    plant_id: str
    day: int
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    growth_stage: str
    height_cm: float
    leaf_count: int
    root_depth_cm: float
    canopy_cover_percent: float
    biomass_g: float
    thermal_time: float
    water_stress: float
    temperature_stress: float

    environment: dict = Field(default_factory=dict)
