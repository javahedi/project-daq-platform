import time

from daq_core.acquisition import AcquisitionEngine

from simulators.temp_simulator import (
    generate_temperature_sample,
)

engine = AcquisitionEngine(
    sample_function=generate_temperature_sample,
    sample_rate_hz=2,
)

engine.start()

try:
    while True:
        sample = engine.queue.get()
        print(sample.to_dict())
except KeyboardInterrupt:
    engine.stop()