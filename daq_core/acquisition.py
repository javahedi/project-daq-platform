import time
from threading import Thread, Event
from daq_core.message_bus import MessageBus  # Adjust this import to match your folder structure
from daq_core.sensors import Sensor


class AcquisitionEngine:

    def __init__(
        self,
        sensor: Sensor,
        sample_rate_hz: float,
        bus: MessageBus,  # Injected MessageBus interface
    ):
        self.sensor = sensor
        self.sample_rate_hz = sample_rate_hz
        
        # Store the message bus reference
        self.bus = bus

        self.stop_event = Event()
        self.thread = Thread(
            target=self._run,
            daemon=True,
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def _run(self):
        period = 1.0 / self.sample_rate_hz

        while not self.stop_event.is_set():
            start = time.perf_counter()

            # 1. Grab the sample from the hardware/simulator
            sample = self.sensor.read()

            # 2. Publish it safely to the bus (it handles queue full/blocking logic)
            self.bus.publish(sample)

            elapsed = time.perf_counter() - start
            sleep_time = max(0, period - elapsed)
            time.sleep(sleep_time)