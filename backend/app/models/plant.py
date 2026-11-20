
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class GrowthStage(str, Enum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    DORMANCY = "dormancy"


class PlantProfile(BaseModel):
    species: str
    cultivar: str | None = None
    scientific_name: str | None = None
    growth_duration_days: int | None = Field(default=None, gt=0)
    optimal_temperature_c: tuple[float, float] | None = None
    optimal_ph: tuple[float, float] | None = None


class PlantState(BaseModel):
    growth_stage: GrowthStage = GrowthStage.SEEDLING
    age_days: int = Field(default=0, ge=0)
    height_cm: float = Field(default=0, ge=0)
    leaf_count: int = Field(default=0, ge=0)
    root_depth_cm: float = Field(default=0, ge=0)
    canopy_cover_percent: float = Field(default=0, ge=0, le=100)
    biomass_g: float = Field(default=0, ge=0)
    health_status: str = "unknown"
    thermal_time_cumulative: float = Field(default=0, ge=0)
    seed_reserve_remaining_g: float = Field(default=0, ge=0)
    is_initialized: bool = False
    flowering_progress_percent: float = Field(default=0, ge=0, le=100)
    fruit_development_percent: float = Field(default=0, ge=0, le=100)
    estimated_yield_g: float = Field(default=0, ge=0)
    harvest_readiness_percent: float = Field(default=0, ge=0, le=100)
    harvest_status: str = "vegetative"
    health_score: float = Field(default=100, ge=0, le=100)
    health_status: str = "Healthy"
    limiting_factor: str = "none"
    recovery_potential_percent: float = Field(
        default=100, ge=0, le=100
    )
    permanent_tissue_loss_percent: float = Field(
        default=0, ge=0, le=100
    )
    stress_days: int = Field(default=0, ge=0)
    accumulated_stress: float = Field(default=0, ge=0, le=100)
    damage_percent: float = Field(default=0, ge=0, le=100)
    recovery_days: int = Field(default=0, ge=0)




class PlantRecord(BaseModel):
    plant_id: str = Field(default_factory=lambda: str(uuid4()))
    profile: PlantProfile
    state: PlantState = Field(default_factory=PlantState)
    zone_id: str | None = None
    planted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
