
from uuid import uuid4

from pydantic import BaseModel, Field


class GreenhouseZone(BaseModel):
    zone_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str | None = None
    plant_ids: list[str] = Field(default_factory=list)
    temperature_target_c: tuple[float, float] | None = None
    humidity_target_percent: tuple[float, float] | None = None
    light_target_lux: tuple[float, float] | None = None
    active: bool = True


class Greenhouse(BaseModel):
    greenhouse_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    location: str = "Earth"
    is_simulated: bool = True
    zones: list[GreenhouseZone] = Field(default_factory=list)
