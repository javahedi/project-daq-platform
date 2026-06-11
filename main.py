import time
import logging
from daq_core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Starting DAQ platform")

from daq_core.acquisition import AcquisitionEngine
from daq_core.config import load_config
from daq_core.message_bus import InMemoryMessageBus
from daq_core.sensor_factory import create_sensor
from daq_core.storage import SQLiteSampleRepository, StorageWorker


config = load_config("config.yaml")
logger.info("Loaded configuration")

bus = InMemoryMessageBus(
    maxsize=config["message_bus"]["max_size"]
)

repo = SQLiteSampleRepository(
    config["database"]["path"]
)

engines = []
logger.info("Starting %d acquisition engines", len(engines))
for sensor_config in config["sensors"]:
    sensor = create_sensor(sensor_config)

    engine = AcquisitionEngine(
        sensor=sensor,
        sample_rate_hz=sensor_config["sample_rate_hz"],
        bus=bus,
    )

    engines.append(engine)

storage_worker = StorageWorker(
    bus=bus,
    repository=repo,
)

for engine in engines:
    engine.start()

storage_worker.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    for engine in engines:
        engine.stop()

    storage_worker.stop()

    print("Stopped")
    logger.info("Stopped DAQ platform")


# try:
#     while True:
#         latest = repo.get_latest_sample()

#         if latest is not None:
#             print(latest.to_dict())
#             print("count:", repo.get_sample_count())

#             recent = repo.get_recent_samples(limit=3)
#             print([s.to_dict() for s in recent])

#         time.sleep(1)

# except KeyboardInterrupt:
#     engine.stop()
#     storage_worker.stop()
#     print("Stopped")



"""
>> sqlite3 data/daq.db

SELECT sensor_id, location, unit, COUNT(*)
FROM samples
GROUP BY sensor_id, location, unit;

.quit
"""