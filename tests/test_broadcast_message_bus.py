from daq_core.message_bus import BroadcastMessageBus


def test_publish_to_multiple_subscribers():
    """
    BroadcastMessageBus implements a Publish/Subscribe pattern.

    One published message is delivered to ALL subscribers.

    This differs from InMemoryMessageBus, where a message is
    consumed by only one consumer.

    Example:

        SensorSample
             ↓
        BroadcastBus
         /       \
        /         \
    Storage    WebSocket

    Both consumers receive the same sample.

    This is useful for:
        - Database storage
        - Live dashboards
        - Alarm processing
        - Cloud publishing

    running simultaneously.
    """

    bus = BroadcastMessageBus()

    # Create two independent subscribers.
    sub_1 = bus.subscribe()
    sub_2 = bus.subscribe()

    sample = "hello"

    bus.publish(sample)

    assert sub_1.consume() == "hello"
    assert sub_2.consume() == "hello"