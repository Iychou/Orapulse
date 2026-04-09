from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import oracledb
except ImportError:  # pragma: no cover
    oracledb = None

from .models import DatabaseConfig, ScanMetrics

LOGGER = logging.getLogger(__name__)
SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def _rows_to_dicts(cursor: Any) -> list[dict[str, Any]]:
    names = [column[0].lower() for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


class OracleCollector:
    def __init__(self, database: DatabaseConfig) -> None:
        self.database = database

    def _connect(self):
        if oracledb is None:
            raise RuntimeError("The 'oracledb' package is not installed.")
        return oracledb.connect(
            user=self.database.username,
            password=self.database.password,
            dsn=self.database.dsn,
        )

    def _query(self, cursor: Any, sql_text: str) -> list[dict[str, Any]]:
        cursor.execute(sql_text)
        return _rows_to_dicts(cursor)

    def collect(self) -> ScanMetrics:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cpu = self._collect_cpu(cursor)
                wait_events = self._query(cursor, (SQL_DIR / "ash_waits.sql").read_text(encoding="utf-8"))
                top_sql = self._query(cursor, (SQL_DIR / "top_sql.sql").read_text(encoding="utf-8"))
                blocking_sessions = self._query(cursor, (SQL_DIR / "blocking_sessions.sql").read_text(encoding="utf-8"))
                io_hotspots = self._query(cursor, (SQL_DIR / "io_hotspots.sql").read_text(encoding="utf-8"))
                session_activity = self._query(cursor, (SQL_DIR / "ash_activity.sql").read_text(encoding="utf-8"))

        return ScanMetrics(
            captured_at=datetime.now(timezone.utc),
            cpu=cpu,
            wait_events=wait_events,
            top_sql=top_sql,
            blocking_sessions=blocking_sessions,
            io_hotspots=io_hotspots,
            session_activity=session_activity,
            source={"dsn": self.database.dsn, "collector": "oracle"},
        )

    def export_sql_bundle(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = output_dir / f"{self.database.name}_sql_bundle.json"
        payload: dict[str, str] = {}
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            payload[sql_file.name] = sql_file.read_text(encoding="utf-8")
        bundle_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return bundle_path

    def _collect_cpu(self, cursor: Any) -> dict[str, Any]:
        cpu_sql = """
        SELECT ROUND(value / 100, 2) AS cpu_cores
        FROM v$osstat
        WHERE stat_name = 'NUM_CPU_CORES'
        """
        aas_sql = """
        SELECT ROUND(COUNT(*) / 60, 2) AS avg_active_sessions
        FROM v$active_session_history
        WHERE sample_time > SYSTIMESTAMP - INTERVAL '60' SECOND
        """
        cpu_rows = self._query(cursor, cpu_sql)
        aas_rows = self._query(cursor, aas_sql)
        cpu_cores = float(cpu_rows[0]["cpu_cores"]) if cpu_rows else 0
        avg_active_sessions = float(aas_rows[0]["avg_active_sessions"]) if aas_rows else 0
        cpu_usage_pct = round((avg_active_sessions / cpu_cores) * 100, 2) if cpu_cores else 0
        return {
            "cpu_cores": cpu_cores,
            "avg_active_sessions": avg_active_sessions,
            "cpu_usage_pct": cpu_usage_pct,
        }


class SampleCollector(OracleCollector):
    def collect(self) -> ScanMetrics:
        LOGGER.warning("Using sample data mode.")
        return ScanMetrics(
            captured_at=datetime.now(timezone.utc),
            cpu={"cpu_cores": 8, "avg_active_sessions": 10.5, "cpu_usage_pct": 131.25},
            wait_events=[
                {"event": "db file sequential read", "samples": 220, "pct": 48.5},
                {"event": "log file sync", "samples": 90, "pct": 19.8},
                {"event": "enq: TX - row lock contention", "samples": 54, "pct": 11.9},
            ],
            top_sql=[
                {
                    "sql_id": "8abc1234xyz99",
                    "elapsed_sec": 600.1,
                    "executions": 2,
                    "avg_elapsed_sec": 300.05,
                    "buffer_gets": 800000,
                    "disk_reads": 40000,
                    "sql_text": "SELECT * FROM ORDERS WHERE STATUS = :B1",
                },
                {
                    "sql_id": "4kkk7777pqr11",
                    "elapsed_sec": 410.0,
                    "executions": 1,
                    "avg_elapsed_sec": 410.0,
                    "buffer_gets": 650000,
                    "disk_reads": 21000,
                    "sql_text": "UPDATE INVENTORY SET QUANTITY = QUANTITY - :B1 WHERE PRODUCT_ID = :B2",
                },
            ],
            blocking_sessions=[
                {
                    "blocking_sid": 101,
                    "blocking_serial": 4555,
                    "blocked_sid": 202,
                    "blocked_serial": 9888,
                    "wait_class": "Application",
                    "event": "enq: TX - row lock contention",
                    "seconds_in_wait": 120,
                }
            ],
            io_hotspots=[
                {"file_name": "/oradata/users01.dbf", "avg_read_ms": 22.4, "reads": 14000},
                {"file_name": "/oradata/app01.dbf", "avg_read_ms": 16.2, "reads": 6000},
            ],
            session_activity=[
                {"module": "JDBC Thin Client", "active_sessions": 5, "wait_class": "User I/O"},
                {"module": "Batch Job", "active_sessions": 3, "wait_class": "Application"},
                {"module": "SQL Developer", "active_sessions": 2, "wait_class": "CPU"},
            ],
            source={"dsn": self.database.dsn, "collector": "sample"},
        )
