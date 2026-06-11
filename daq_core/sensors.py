from abc import ABC, abstractmethod

from daq_core.models import SensorSample


class Sensor(ABC):
    @abstractmethod
    def read(self) -> SensorSample:
        pass