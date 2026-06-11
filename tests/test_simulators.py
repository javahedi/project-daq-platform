from daq_core.models import SensorSample, Quality
from daq_core.sensors import Sensor
from simulators.temp_simulator import TemperatureSimulator
from simulators.pressure_simulator import PressureSimulator


def test_temperature_simulator_is_sensor():
    sensor = TemperatureSimulator(
        sensor_id="TEMP_001",
        location="LAB_001",
    )

    assert isinstance(sensor, Sensor)


def test_pressure_simulator_is_sensor():
    sensor = PressureSimulator(
        sensor_id="PRESS_001",
        location="LAB_001",
    )

    assert isinstance(sensor, Sensor)


def test_temperature_simulator_returns_sensor_sample():
    sensor = TemperatureSimulator(
        sensor_id="TEMP_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert isinstance(sample, SensorSample)


def test_pressure_simulator_returns_sensor_sample():
    sensor = PressureSimulator(
        sensor_id="PRESS_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert isinstance(sample, SensorSample)


def test_temperature_simulator_uses_configured_sensor_id_and_location():
    sensor = TemperatureSimulator(
        sensor_id="TEMP_002",
        location="LAB_002",
    )

    sample = sensor.read()

    assert sample.sensor_id == "TEMP_002"
    assert sample.location == "LAB_002"


def test_pressure_simulator_uses_configured_sensor_id_and_location():
    sensor = PressureSimulator(
        sensor_id="PRESS_002",
        location="LAB_003",
    )

    sample = sensor.read()

    assert sample.sensor_id == "PRESS_002"
    assert sample.location == "LAB_003"


def test_temperature_simulator_sample_fields():
    sensor = TemperatureSimulator(
        sensor_id="TEMP_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert sample.unit == "C"
    assert sample.quality == Quality.SIMULATED
    assert sample.source == "SIMULATOR"
    assert isinstance(sample.timestamp_ns, int)
    assert isinstance(sample.value, float)


def test_pressure_simulator_sample_fields():
    sensor = PressureSimulator(
        sensor_id="PRESS_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert sample.unit == "bar"
    assert sample.quality == Quality.SIMULATED
    assert sample.source == "SIMULATOR"
    assert isinstance(sample.timestamp_ns, int)
    assert isinstance(sample.value, float)


def test_temperature_value_reasonable_range():
    sensor = TemperatureSimulator(
        sensor_id="TEMP_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert 20.0 <= sample.value <= 30.0


def test_pressure_value_reasonable_range():
    sensor = PressureSimulator(
        sensor_id="PRESS_001",
        location="LAB_001",
    )

    sample = sensor.read()

    assert 0.8 <= sample.value <= 1.2


def test_two_temperature_sensors_are_distinct():
    temp_1 = TemperatureSimulator(
        sensor_id="TEMP_001",
        location="LAB_001",
    )

    temp_2 = TemperatureSimulator(
        sensor_id="TEMP_002",
        location="LAB_002",
    )

    sample_1 = temp_1.read()
    sample_2 = temp_2.read()

    assert sample_1.sensor_id == "TEMP_001"
    assert sample_1.location == "LAB_001"

    assert sample_2.sensor_id == "TEMP_002"
    assert sample_2.location == "LAB_002"

    assert sample_1.sensor_id != sample_2.sensor_id
    assert sample_1.location != sample_2.location