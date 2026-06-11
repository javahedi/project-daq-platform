from dataclasses import dataclass
from enum import Enum
import json


class Quality(str, Enum):
    GOOD = "GOOD"
    BAD = "BAD"
    UNCERTAIN = "UNCERTAIN"
    TIMEOUT = "TIMEOUT"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    SIMULATED = "SIMULATED"


@dataclass(frozen=True)
class SensorSample:
    sensor_id: str
    timestamp_ns: int
    value: float
    unit: str
    quality: Quality
    source: str
    location: str

    def to_dict(self) -> dict:
        return {
            "sensor_id": self.sensor_id,
            "timestamp_ns": self.timestamp_ns,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality.value,
            "source": self.source,
            "location": self.location,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


    # later we'll receive samples from ZeroMQ ,MQTT, REST APIs, Database records Files
    # and we'll want to reconstruct a proper SensorSample object
    """
     SensorSample
      ↓
    to_dict()
        ↓
    to_json()
        ↓
    network/database
        ↓
    from_dict()
        ↓
    SensorSample
    
    Example:
        payload = {
            "sensor_id": "TEMP_001",
            "timestamp_ns": 123456789,
            "value": 25.3,
            "unit": "C",
            "quality": "GOOD",
            "source": "SIMULATOR",
            "location": "LAB_001",
            }

    sample = SensorSample.from_dict(payload)

   
    """
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            sensor_id=data["sensor_id"],
            timestamp_ns=data["timestamp_ns"],
            value=data["value"],
            unit=data["unit"],
            quality=Quality(data["quality"]),
            source=data["source"],
            location=data["location"],
        )
    

    # # This is a regular instance method (no decorator)
    # def update_from_dict(self, data: dict) -> dict:
    #     # 1. Update the existing object's properties
    #     self.sensor_id = data["sensor_id"]
    #     self.timestamp_ns = data["timestamp_ns"]
    #     self.value = data["value"]
    #     self.unit = data["unit"]
    #     self.quality = Quality(data["quality"])
    #     self.source = data["source"]
    #     self.location = data["location"]
        
    #     # 2. Return a proper dictionary format
    #     return {
    #         "sensor_id": self.sensor_id,
    #         "value": self.value
    #         # ... and so on
    #     }