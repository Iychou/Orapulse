from __future__ import annotations

import os
from pathlib import Path

import yaml

from .models import AppConfig, DatabaseConfig, EmailConfig, Thresholds


def _read_secret(raw_password: str | None, env_name: str | None) -> str:
    if raw_password:
        return raw_password
    if env_name:
        return os.getenv(env_name, "")
    return ""


def load_config(path: str | Path) -> AppConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    global_cfg = data.get("global", {})
    alert_cfg = data.get("alerts", {}).get("email", {})

    databases: list[DatabaseConfig] = []
    for item in data.get("databases", []):
        threshold_cfg = item.get("thresholds", {})
        thresholds = Thresholds(
            cpu_percent=threshold_cfg.get("cpu_percent", 80),
            avg_active_sessions=threshold_cfg.get("avg_active_sessions", 8),
            io_wait_ms=threshold_cfg.get("io_wait_ms", 20),
            long_running_sql_seconds=threshold_cfg.get("long_running_sql_seconds", 300),
            blocking_sessions=threshold_cfg.get("blocking_sessions", 1),
            top_wait_event_pct=threshold_cfg.get("top_wait_event_pct", 40),
        )
        databases.append(
            DatabaseConfig(
                name=item["name"],
                host=item["host"],
                port=int(item.get("port", 1521)),
                service_name=item["service_name"],
                username=item["username"],
                password=_read_secret(item.get("password"), item.get("password_env")),
                mode=item.get("mode", "thin"),
                thresholds=thresholds,
            )
        )

    email = EmailConfig(
        enabled=bool(alert_cfg.get("enabled", False)),
        smtp_host=alert_cfg.get("smtp_host", ""),
        smtp_port=int(alert_cfg.get("smtp_port", 587)),
        use_tls=bool(alert_cfg.get("use_tls", True)),
        username=alert_cfg.get("username", ""),
        password=_read_secret(alert_cfg.get("password"), alert_cfg.get("password_env")),
        from_address=alert_cfg.get("from", ""),
        to=list(alert_cfg.get("to", [])),
    )

    return AppConfig(
        output_dir=global_cfg.get("output_dir", "reports"),
        log_level=global_cfg.get("log_level", "INFO"),
        poll_interval_seconds=int(global_cfg.get("poll_interval_seconds", 300)),
        report_retention_days=int(global_cfg.get("report_retention_days", 14)),
        alert_channels=list(global_cfg.get("alert_channels", ["log"])),
        databases=databases,
        email=email,
    )


def get_database(config: AppConfig, database_name: str) -> DatabaseConfig:
    for database in config.databases:
        if database.name == database_name:
            return database
    available = ", ".join(db.name for db in config.databases) or "<none>"
    raise ValueError(f"Unknown database '{database_name}'. Available profiles: {available}")
