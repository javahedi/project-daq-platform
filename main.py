from daq_core.acquisition import AcquisitionEngine
from daq_core.message_bus import InMemoryMessageBus
from daq_core.storage import SQLiteSampleRepository, StorageWorker

from simulators.temp_simulator import TemperatureSimulator
from simulators.pressure_simulator import PressureSimulator

import time 

bus = InMemoryMessageBus(maxsize=1000)
repo = SQLiteSampleRepository("data/daq.db")


temp_lab_1     = TemperatureSimulator(sensor_id="TEMP_001",location="LAB_001")
temp_lab_2     = TemperatureSimulator(sensor_id="TEMP_002",location="LAB_002")
pressure_lab_1 = PressureSimulator(sensor_id="PRESS_002",location="LAB_002") 

engines = [ 
    AcquisitionEngine(sensor=temp_lab_1,sample_rate_hz=5, bus=bus),
    AcquisitionEngine(sensor=temp_lab_2,sample_rate_hz=2, bus=bus),
    AcquisitionEngine(sensor=pressure_lab_1,sample_rate_hz=1, bus=bus),

]

storage_worker = StorageWorker(bus= bus,repository=repo)

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