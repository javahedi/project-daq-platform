import sqlite3
import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from threading import Thread, Event
from daq_core.message_bus import MessageBus, Subscriber
from daq_core.models import SensorSample, Quality


class SQLiteSampleRepository:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False, # Allow this SQLite connection to be used from another thread.
            )
        
        logger.info("Connected to SQLite database: %s", self.db_path)
    
        self._create_tables()

    def _create_tables(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                timestamp_ns INTEGER NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                quality TEXT NOT NULL,
                source TEXT NOT NULL,
                location TEXT NOT NULL
            )
            """
        )

        self.connection.commit()

    
    


    def insert_sample(self, sample: SensorSample) -> None:
        self.connection.execute(
            """
            INSERT INTO samples (
                sensor_id,
                timestamp_ns,
                value,
                unit,
                quality,
                source,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sample.sensor_id,
                sample.timestamp_ns,
                sample.value,
                sample.unit,
                sample.quality.value,
                sample.source,
                sample.location,
            ),
        )

        self.connection.commit()


    def _row_to_sample(self, row) -> SensorSample:
        return SensorSample(
            sensor_id=row[0],
            timestamp_ns=row[1],
            value=row[2],
            unit=row[3],
            quality=Quality(row[4]),
            source=row[5],
            location=row[6],
        )
    

    def get_latest_sample(self) -> SensorSample | None:
        cursor = self.connection.execute(
            """
            SELECT
                sensor_id,
                timestamp_ns,
                value,
                unit,
                quality,
                source,
                location
            FROM samples
            ORDER BY id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_sample(row)
    

    def get_sample_count(self) -> int:
        cursor = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM samples
            """
        )

        row = cursor.fetchone()

        return row[0]
    
    def get_recent_samples(self, limit: int = 100) -> list[SensorSample]:
        cursor = self.connection.execute(
            """
            SELECT
                sensor_id,
                timestamp_ns,
                value,
                unit,
                quality,
                source,
                location
            FROM samples
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()

        return [self._row_to_sample(row) for row in rows]
    
    
    
    def get_samples_by_sensor(self, sensor_id: str, limit: int = 100 ) -> list[SensorSample]:
        cursor = self.connection.execute(
            """
            SELECT
                sensor_id,
                timestamp_ns,
                value,
                unit,
                quality,
                source,
                location
            FROM samples
            WHERE sensor_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (sensor_id, limit),
        )

        rows = cursor.fetchall()

        return [self._row_to_sample(row) for row in rows]
    

    # def get_sensor(self) -> list[str]:
    #     cursor = self.connection.execute(
    #         """
    #         SELECT DISTINCT sensor_id
    #         FROM samples
    #         ORDER BY sensor_id;
    #         """
    #     )

    def get_sensor_ids(self) -> list[str]:
        cursor = self.connection.execute(
            """
            SELECT DISTINCT sensor_id
            FROM samples
            ORDER BY sensor_id
            """
        )

        rows = cursor.fetchall()

        return [row[0] for row in rows]
    


    def get_sensor_statistics(self, sensor_id: str) -> dict:
        cursor = self.connection.execute(
            """
            SELECT
                COUNT(*),
                MIN(value),
                MAX(value),
                AVG(value)
            FROM samples
            WHERE sensor_id = ?
            """,
            (sensor_id,),
        )

        row = cursor.fetchone()

        return {
            "sensor_id": sensor_id,
            "count": row[0],
            "min": row[1],
            "max": row[2],
            "avg": row[3],
        }
    
    def get_sensor_details(self) -> list[dict]:
        cursor = self.connection.execute(
            """
            SELECT
                sensor_id,
                location,
                unit,
                source
            FROM samples
            GROUP BY sensor_id, location, unit, source
            ORDER BY sensor_id
            """
        )

        rows = cursor.fetchall()

        return [
            {
                "sensor_id": row[0],
                "location": row[1],
                "unit": row[2],
                "source": row[3],
            }
            for row in rows
        ]


    
   

class StorageWorker:
    def __init__(
        self,
        subscriber: Subscriber,
        repository: SQLiteSampleRepository,
    ):
        self.subscriber = subscriber
        self.repository = repository

        self.stop_event = Event()

        self.thread = Thread(
            target=self._run,
            daemon=True,
        )

    def start(self) -> None:
        logger.info("Starting storage worker")
        self.thread.start()

    def stop(self) -> None:
        logger.info("Stopping storage worker")
        self.stop_event.set()
        self.thread.join()

    def _run(self) -> None:
        logger.info("Storage worker loop started")

        while not self.stop_event.is_set():
            try:
                sample = self.subscriber.consume(timeout=1.0)
                self.repository.insert_sample(sample)

            except TimeoutError:
                continue
    


# class StorageWorker:
#     def __init__(
#         self,
#         bus: MessageBus,
#         repository: SQLiteSampleRepository,
#     ):
#         self.bus = bus
#         self.repository = repository

#         self.stop_event = Event()

#         self.thread = Thread(
#             target=self._run,
#             daemon=True,
#         )

#     def start(self) -> None:
#         logger.info("Starting storage worker")
#         self.thread.start()

#     def stop(self) -> None:
#         logger.info("Stopping storage worker")
#         self.stop_event.set()
#         self.thread.join()


#     def _run(self) -> None:
#         logger.info("Storage worker loop started")
#         while not self.stop_event.is_set():
#             try:
#                 sample = self.bus.consume(timeout=1.0)
#                 self.repository.insert_sample(sample)

#             except TimeoutError:
#                 continue