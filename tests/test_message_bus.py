import time

from daq_core.models import SensorSample, Quality
from daq_core.message_bus import InMemoryMessageBus


def test_in_memory_message_bus_publish_consume():
    bus = InMemoryMessageBus(maxsize=10)

    sample = SensorSample(
        sensor_id="TEMP_001",
        timestamp_ns=time.monotonic_ns(),
        value=25.0,
        unit="C",
        quality=Quality.GOOD,
        source="TEST",
        location="LAB_001",
    )

    bus.publish(sample)

    received = bus.consume(timeout=1.0)

    assert received == sample
    assert received.sensor_id == "TEMP_001"

# python3 -m pytest