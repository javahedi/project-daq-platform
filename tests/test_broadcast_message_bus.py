import time
import pytest

from daq_core.message_bus import BroadcastMessageBus
from daq_core.models import SensorSample, Quality


def make_sample(sensor_id: str = "TEMP_001") -> SensorSample:
    """
    Helper used by all tests.

    Creates one valid SensorSample without repeating
    boilerplate in every test.
    """

    return SensorSample(
        sensor_id=sensor_id,
        timestamp_ns=time.monotonic_ns(),
        value=25.0,
        unit="C",
        quality=Quality.SIMULATED,
        source="TEST",
        location="LAB_001",
    )


def test_broadcast_bus_sends_same_sample_to_all_subscribers():
    """
    BroadcastMessageBus implements publish/subscribe.

    One published sample is delivered to all subscribers.

    This is different from InMemoryMessageBus:

        InMemoryMessageBus:
            one sample -> one consumer

        BroadcastMessageBus:
            one sample -> many consumers

    This is useful when the same DAQ sample must go to:
        - SQLite storage
        - WebSocket live stream
        - alarm processing
        - cloud publishing
    """

    bus = BroadcastMessageBus()

    storage_subscriber = bus.subscribe()
    live_subscriber = bus.subscribe()

    sample = make_sample()

    bus.publish(sample)

    assert storage_subscriber.consume(timeout=1.0) == sample
    assert live_subscriber.consume(timeout=1.0) == sample


def test_broadcast_subscribers_are_independent():
    """
    Each subscriber has its own queue.

    Consuming from one subscriber should not remove the
    sample from another subscriber.
    """

    bus = BroadcastMessageBus()

    sub_1 = bus.subscribe()
    sub_2 = bus.subscribe()

    sample = make_sample()

    bus.publish(sample)

    received_1 = sub_1.consume(timeout=1.0)

    assert received_1 == sample

    # sub_2 should still have its own copy/reference available.
    received_2 = sub_2.consume(timeout=1.0)

    assert received_2 == sample


def test_broadcast_bus_tracks_subscriber_count():
    """
    The bus should know how many subscribers exist.

    This is useful later for diagnostics, logging,
    and debugging live stream clients.
    """

    bus = BroadcastMessageBus()

    assert bus.subscriber_count() == 0

    bus.subscribe()
    assert bus.subscriber_count() == 1

    bus.subscribe()
    assert bus.subscriber_count() == 2


def test_subscriber_times_out_when_no_sample_available():
    """
    A subscriber with no available sample should raise TimeoutError.

    This prevents consumers from blocking forever.
    """

    bus = BroadcastMessageBus()

    subscriber = bus.subscribe()

    with pytest.raises(TimeoutError):
        subscriber.consume(timeout=0.1)


def test_late_subscriber_does_not_receive_old_samples():
    """
    Broadcast bus is not persistent storage.

    If a sample is published before a subscriber exists,
    that late subscriber should not receive the old sample.

    This is important:

        BroadcastMessageBus = live distribution
        SQLiteRepository    = historical storage
    """

    bus = BroadcastMessageBus()

    sample = make_sample()

    bus.publish(sample)

    late_subscriber = bus.subscribe()

    with pytest.raises(TimeoutError):
        late_subscriber.consume(timeout=0.1)


def test_broadcast_preserves_fifo_order_per_subscriber():
    """
    Each subscriber should receive samples in publish order.

    This matters for time-series data.
    """

    bus = BroadcastMessageBus()

    subscriber = bus.subscribe()

    first = make_sample("TEMP_001")
    second = make_sample("TEMP_002")

    bus.publish(first)
    bus.publish(second)

    assert subscriber.consume(timeout=1.0) == first
    assert subscriber.consume(timeout=1.0) == second