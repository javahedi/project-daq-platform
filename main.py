from daq_core.acquisition import AcquisitionEngine
from daq_core.message_bus import InMemoryMessageBus
from simulators.temp_simulator import generate_temperature_sample
from consumers import print_consumer


bus = InMemoryMessageBus(maxsize=1000)

engine = AcquisitionEngine(
    sample_function=generate_temperature_sample,
    sample_rate_hz=5,
    bus=bus,
)

engine.start()

try:
    print_consumer(bus)

except KeyboardInterrupt:
    engine.stop()
    print("Stopped")