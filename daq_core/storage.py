import sqlite3
from pathlib import Path

from daq_core.models import SensorSample, Quality


class SQLiteSampleRepository:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.db_path)
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