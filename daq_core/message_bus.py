from queue import Queue, Full, Empty  # solve Race Condition
from daq_core.models import SensorSample


class MessageBus:
    """
    Abstract message bus interface.

    Purpose:
        Decouple data producers from data consumers.

    Producers:
        AcquisitionEngine

    Consumers:
        StorageWorker
        WebSocketWorker (future)
        AlarmWorker (future)

    Why?

        AcquisitionEngine should not know where data goes.

        It only knows:

            bus.publish(sample)

    Later we can replace the implementation with:

        InMemoryMessageBus
        BroadcastMessageBus
        ZeroMQMessageBus
        MQTTMessageBus

    without changing AcquisitionEngine.
    """

    def publish(self, sample: SensorSample) -> None:
        raise NotImplementedError

    def consume(self, timeout: float | None = None) -> SensorSample:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError



class InMemoryMessageBus(MessageBus):
    """
    Single-consumer message bus.

    Architecture:

        Producer
            ↓
          Queue
            ↓
         Consumer

    Characteristics:

        - One published sample is consumed once.
        - After consumption the sample disappears.
        - Very simple.
        - Thread-safe.
        - Low memory usage.

    Typical usage:

        Sensor
            ↓
        AcquisitionEngine
            ↓
        InMemoryMessageBus
            ↓
        StorageWorker

    This is the pattern we currently use.

    Limitation:

        Multiple consumers cannot reliably receive
        the same sample.

    Example:

        StorageWorker consumes sample

        WebSocketWorker never sees it.

    Good for:

        - Work queues
        - Job processing
        - Single storage pipeline
    """
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
    


class Subscriber:
    """
    Represents one subscription to a BroadcastMessageBus.

    Every subscriber owns its own queue.

    Example:

        storage_sub = bus.subscribe()

        live_sub = bus.subscribe()

    Both subscribers receive every published sample.

    A Subscriber is essentially:

        "my personal mailbox"

    inside the broadcast system.
    """
    def __init__(self, queue: Queue):
        self._queue = queue

    def consume(self, timeout: float | None = None):
        try:
            return self._queue.get(timeout=timeout)

        except Empty:
            raise TimeoutError("No sample available")
        

class BroadcastMessageBus:
    """
    Publish/Subscribe message bus.

    Architecture:

                    Subscriber A
                         ↑
                         │
        Producer → BroadcastBus
                         │
                         ↓
                    Subscriber B

                         ↓

                    Subscriber C

    Characteristics:

        Every subscriber receives every sample.

    Example:

        sample_1

        StorageWorker receives sample_1

        WebSocketWorker receives sample_1

        AlarmWorker receives sample_1

    simultaneously.

    This is often called:

        Pub/Sub
        Fan-out
        Broadcast

    Why do we need it?

        DAQ systems often have multiple consumers:

            - Database storage
            - Live dashboard
            - Alarm engine
            - Cloud uploader

        All of them need the same measurement.

    Cost:

        More queues.
        More buffering.
        More memory usage.

    Benefit:

        Multiple independent consumers can process
        the same sample without interfering with each other.

    Future:

        This design is conceptually very similar to:

            ZeroMQ PUB/SUB
            MQTT
            DDS
            ROS Topics

        so learning it now will make those systems
        much easier to understand later.
    """
    def __init__(self):
        self._subscribers = []

    def subscribe(self) -> Subscriber:
        queue = Queue()

        self._subscribers.append(queue)

        return Subscriber(queue)

    def publish(self, sample):
        for queue in self._subscribers:
            queue.put(sample)

    def subscriber_count(self) -> int:
        return len(self._subscribers)
