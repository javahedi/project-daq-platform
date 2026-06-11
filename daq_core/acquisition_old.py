"""
Producer-Consumer multi-threading pattern in Python.

The Producer-Consumer pattern is a classic multithreading design 
pattern that decouples work generation from work execution using a shared, 
thread-safe buffer or queue.

It balances workloads, prevents race conditions, and prevents system overload
by stopping producers when the queue is full or consumers when it's empty


>> In multi-threaded programming, 
>> if two threads try to touch the same list or data structure at the same time, 
your data gets corrupted.

>> Queue has built-in locking mechanism primitives. You can safely 
  .put() data into it from this background  thread, and safely 
  .get() data out of it from your main thread without any risk of data corruption.
"""

from queue import Queue  # solve Race Condition
from threading import Thread, Event
import time


class AcquisitionEngine:

    def __init__(
        self,
        sample_function,
        sample_rate_hz: float,
        queue_size: int = 1000,
    ):
        self.sample_function = sample_function
        self.sample_rate_hz = sample_rate_hz

        self.queue = Queue(maxsize=queue_size)

        self.stop_event = Event() # Graceful Shutdown (Event)
        # Instead of violently killing the thread (which can corrupt data or leave hardware connections open), 
        # this code uses an Event() object to say "Please stop when you finish your current loop."

        self.thread = Thread(
            target=self._run,
            daemon=True, # crucial safety feature 
            # If the main program exits (like if the user closes the app or crashes), 
            # kill this thread immediately." Without daemon=True, if your main script finishes, 
            # the background loop will keep running forever in the background, freezing your terminal.
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def _run(self):

        period = 1.0 / self.sample_rate_hz

        while not self.stop_event.is_set(): # self.stop_event.is_set() is checked at the start of every loop.

            start = time.perf_counter()

            sample = self.sample_function()

            self.queue.put(sample)

            # If sample rate is 10 Hz,  target period is 0.1 seconds.
            # If fetching the sample takes 0.02 seconds (elapsed), 
            # a naive loop using time.sleep(0.1) would actually take 0.12 seconds total, 
            # causing  sampler to drift and run too slow.
            elapsed = time.perf_counter() - start
            sleep_time = max(0, period - elapsed) # dynamically adjusts
            time.sleep(sleep_time)