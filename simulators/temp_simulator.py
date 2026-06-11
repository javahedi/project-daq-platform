import random
import time

from daq_core.models import SensorSample
from daq_core.models import Quality


def generate_temperature_sample():

    return SensorSample(
        sensor_id="TEMP_001",
        timestamp_ns=time.monotonic_ns(),
        value=25 + random.uniform(-1, 1),
        unit="C",
        quality=Quality.SIMULATED,
        source="SIMULATOR",
        location="LAB_001",
    )