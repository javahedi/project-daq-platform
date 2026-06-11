from daq_core.sensors import Sensor
from simulators.temp_simulator import TemperatureSimulator
from simulators.pressure_simulator import PressureSimulator


def create_sensor(sensor_config: dict) -> Sensor:
    sensor_type = sensor_config["type"]

    if sensor_type == "temperature":
        return TemperatureSimulator(
            sensor_id=sensor_config["sensor_id"],
            location=sensor_config["location"],
        )

    if sensor_type == "pressure":
        return PressureSimulator(
            sensor_id=sensor_config["sensor_id"],
            location=sensor_config["location"],
        )

    raise ValueError(f"Unknown sensor type: {sensor_type}")