from daq_core.message_bus import MessageBus


def print_consumer(bus: MessageBus) -> None:
    while True:
        try:
            sample = bus.consume(timeout=1.0)
            print(sample.to_dict())
        except TimeoutError:
            print("No sample received")