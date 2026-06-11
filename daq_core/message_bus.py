from queue import Queue, Full, Empty  # solve Race Condition
from daq_core.models import SensorSample


class MessageBus:
    """
    abstract base class (or interface). It doesn't actually do anything;
    """
    def publish(self, sample: SensorSample) -> None:
        raise NotImplementedError

    def consume(self, timeout: float | None = None) -> SensorSample:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError


class InMemoryMessageBus(MessageBus):
    def __init__(self, maxsize: int = 1000):
        self._queue = Queue(maxsize=maxsize)

    def publish(self, sample: SensorSample) -> None:
        try:
            self._queue.put(sample, block=False)
        except Full:
            # For now: drop newest sample if buffer is full.
            # Later we can implement metrics/logging here.
            pass

    def consume(self, timeout: float | None = None) -> SensorSample:
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            raise TimeoutError("No sample available")

    def size(self) -> int:
        return self._queue.qsize()