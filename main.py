from daq_core.acquisition import AcquisitionEngine
from daq_core.message_bus import InMemoryMessageBus
from daq_core.storage import SQLiteSampleRepository, StorageWorker
from simulators.temp_simulator import generate_temperature_sample
from consumers import print_consumer
import time 

bus = InMemoryMessageBus(maxsize=1000)
repo = SQLiteSampleRepository("data/daq.db")


engine = AcquisitionEngine(
    sample_function=generate_temperature_sample,
    sample_rate_hz=5,
    bus=bus,
)

storage_worker = StorageWorker(
    bus= bus,
    repository=repo,
)

engine.start()
storage_worker.start()

try:
    while True:
        latest = repo.get_latest_sample()

        if latest is not None:
            print(latest.to_dict())

        time.sleep(1)

except KeyboardInterrupt:
    engine.stop()
    storage_worker.stop()
    print("Stopped")