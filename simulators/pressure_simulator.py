import random
import time

from daq_core.models import SensorSample, Quality
from daq_core.sensors import Sensor


class PressureSimulator(Sensor):
    def __init__(
        self,
        sensor_id: str = "PRESS_001",
        location: str = "LAB_001",
    ):
        self.sensor_id = sensor_id
        self.location = location

    def read(self) -> SensorSample:
        return SensorSample(
            sensor_id=self.sensor_id,
            timestamp_ns=time.monotonic_ns(),
            value=1.0 + random.uniform(-0.05, 0.05),
            unit="bar",
            quality=Quality.SIMULATED,
            source="SIMULATOR",
            location=self.location,
        )