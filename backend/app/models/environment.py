
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    O2 = "o2"
    SOIL_MOISTURE = "soil_moisture"
    SOIL_PH = "soil_ph"
    SOIL_EC = "soil_ec"
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    LIGHT_INTENSITY = "light_intensity"


class SensorReading(BaseModel):
    reading_id: str = Field(default_factory=lambda: str(uuid4()))
    zone_id: str
    sensor_type: SensorType
    value: float
    unit: str
    measured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source: str = "simulation"
    confidence: float = Field(default=1.0, ge=0, le=1)
