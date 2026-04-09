from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Thresholds:
    cpu_percent: int = 80
    avg_active_sessions: int = 8
    io_wait_ms: int = 20
    long_running_sql_seconds: int = 300
    blocking_sessions: int = 1
    top_wait_event_pct: int = 40


@dataclass(slots=True)
class DatabaseConfig:
    name: str
    host: str
    port: int
    service_name: str
    username: str
    password: str
    mode: str = "thin"
    thresholds: Thresholds = field(default_factory=Thresholds)

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name}"


@dataclass(slots=True)
class EmailConfig:
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    use_tls: bool = True
    username: str = ""
    password: str = ""
    from_address: str = ""
    to: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AppConfig:
    output_dir: str = "reports"
    log_level: str = "INFO"
    poll_interval_seconds: int = 300
    report_retention_days: int = 14
    alert_channels: list[str] = field(default_factory=lambda: ["log"])
    databases: list[DatabaseConfig] = field(default_factory=list)
    email: EmailConfig = field(default_factory=EmailConfig)


@dataclass(slots=True)
class Finding:
    severity: str
    title: str
    summary: str
    recommendation: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScanMetrics:
    captured_at: datetime
    cpu: dict[str, Any]
    wait_events: list[dict[str, Any]]
    top_sql: list[dict[str, Any]]
    blocking_sessions: list[dict[str, Any]]
    io_hotspots: list[dict[str, Any]]
    session_activity: list[dict[str, Any]]
    source: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScanResult:
    database: str
    metrics: ScanMetrics
    findings: list[Finding]
    generated_files: dict[str, str] = field(default_factory=dict)
