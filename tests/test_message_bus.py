import time
import pytest
from daq_core.models import SensorSample, Quality
from daq_core.message_bus import InMemoryMessageBus


def make_sample(sensor_id: str = "TEMP_001") -> SensorSample:
    return SensorSample(
        sensor_id=sensor_id,
        timestamp_ns=time.monotonic_ns(),
        value=25.0,
        unit="C",
        quality=Quality.SIMULATED,
        source="TEST",
        location="LAB_001",
    )



def test_publish_and_consume_single_sample():
    """
    A sample published to the queue
    can be consumed by a consumer.
    """

    bus = InMemoryMessageBus(maxsize=10)

    sample = make_sample()

    bus.publish(sample)

    received = bus.consume(timeout=1.0)

    assert received == sample



def test_queue_size_increases_after_publish():
    """
    Publishing a sample should increase
    the queue size.
    """

    bus = InMemoryMessageBus(maxsize=10)

    assert bus.size() == 0

    bus.publish(make_sample())

    assert bus.size() == 1


def test_queue_size_decreases_after_consume():
    """
    Consuming a sample removes it
    from the queue.
    """

    bus = InMemoryMessageBus(maxsize=10)

    bus.publish(make_sample())

    assert bus.size() == 1

    bus.consume(timeout=1.0)

    assert bus.size() == 0




def test_samples_are_consumed_in_fifo_order():
    """
    Queue should preserve publish order.

    First In
    First Out
    """

    bus = InMemoryMessageBus(maxsize=10)

    first = make_sample("TEMP_001")
    second = make_sample("TEMP_002")

    bus.publish(first)
    bus.publish(second)

    assert bus.consume(timeout=1.0) == first
    assert bus.consume(timeout=1.0) == second


def test_consume_empty_queue_raises_timeout():
    """
    Consuming from an empty queue
    should raise TimeoutError.
    """

    bus = InMemoryMessageBus(maxsize=10)

    with pytest.raises(TimeoutError):
        bus.consume(timeout=0.1)


def test_publish_to_full_queue_is_dropped():
    """
    Current implementation drops samples
    when queue is full.

    This is a design choice.
    """

    bus = InMemoryMessageBus(maxsize=1)

    first = make_sample("TEMP_001")
    second = make_sample("TEMP_002")

    bus.publish(first)
    bus.publish(second)

    received = bus.consume(timeout=1.0)

    assert received == first



# python3 -m pytest