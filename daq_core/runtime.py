import logging

from daq_core.acquisition import AcquisitionEngine
from daq_core.config import load_config
from daq_core.message_bus import BroadcastMessageBus
from daq_core.sensor_factory import create_sensor
from daq_core.storage import SQLiteSampleRepository, StorageWorker


logger = logging.getLogger(__name__)

live_bus = BroadcastMessageBus()


engines = []
storage_worker = None


def start_daq(config_path: str = "config.yaml") -> None:
    global engines
    global storage_worker

    config = load_config(config_path)

    repo = SQLiteSampleRepository(
        config["database"]["path"]
    )

    storage_subscriber = live_bus.subscribe()

    for sensor_config in config["sensors"]:
        sensor = create_sensor(sensor_config)

        engine = AcquisitionEngine(
            sensor=sensor,
            sample_rate_hz=sensor_config["sample_rate_hz"],
            bus=live_bus,
        )

        engines.append(engine)

    storage_worker = StorageWorker(
        subscriber=storage_subscriber,
        repository=repo,
    )

    logger.info("Starting %d acquisition engines", len(engines))

    for engine in engines:
        engine.start()

    storage_worker.start()