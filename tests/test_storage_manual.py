import time

from daq_core.models import SensorSample, Quality
from daq_core.storage import SQLiteSampleRepository



def test_insert_and_read_sample():

    repo = SQLiteSampleRepository("data/test.db")

    sample = SensorSample(
        sensor_id="TEMP_001",
        timestamp_ns=time.monotonic_ns(),
        value=25.7,
        unit="C",
        quality=Quality.SIMULATED,
        source="MANUAL_TEST",
        location="LAB_001",
    )

    repo.insert_sample(sample)

    latest = repo.get_latest_sample()

    assert latest.sensor_id == sample.sensor_id
    assert latest.value == sample.value
    assert latest.unit == sample.unit
   


