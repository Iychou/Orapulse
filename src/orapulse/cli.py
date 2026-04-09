from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .alerts import emit_alerts
from .analyzer import analyze_metrics
from .collector import OracleCollector, SampleCollector
from .config import get_database, load_config
from .formatter import write_reports
from .models import ScanResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orapulse", description="Simple Oracle performance monitoring toolkit")
    parser.add_argument("--config", default="config/orapulse.yml", help="Path to configuration file")
    parser.add_argument("--database", default="primary", help="Database profile name")
    parser.add_argument("--sample-data", action="store_true", help="Use sample data instead of a real Oracle connection")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_cmd = subparsers.add_parser("scan", help="Analyze current Oracle performance")
    scan_cmd.add_argument("--write-report", action="store_true", help="Also write HTML, JSON, and TXT report files")

    report_cmd = subparsers.add_parser("report", help="Generate report files")
    report_cmd.add_argument("--include-sql", action="store_true", help="Export SQL scripts as a JSON bundle")

    monitor_cmd = subparsers.add_parser("monitor", help="Run continuous monitoring mode")
    monitor_cmd.add_argument("--iterations", type=int, default=0, help="Stop after N loops. Use 0 for infinite.")

    alert_cmd = subparsers.add_parser("alert", help="Run scan and trigger alerts")
    alert_cmd.add_argument("--write-report", action="store_true", help="Write reports before sending alerts")

    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def purge_old_reports(folder: Path, retention_days: int) -> None:
    if retention_days <= 0 or not folder.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    for item in folder.iterdir():
        if item.is_file() and datetime.fromtimestamp(item.stat().st_mtime, timezone.utc) < cutoff:
            item.unlink()


def get_collector(use_sample_data: bool, database):
    return SampleCollector(database) if use_sample_data else OracleCollector(database)


def run_scan(config_path: str, database_name: str, sample_data: bool) -> tuple[ScanResult, object]:
    config = load_config(config_path)
    database = get_database(config, database_name)
    collector = get_collector(sample_data, database)
    metrics = collector.collect()
    findings = analyze_metrics(database, metrics)
    return ScanResult(database=database.name, metrics=metrics, findings=findings), collector


def save_result(config_path: str, result: ScanResult, collector, include_sql: bool) -> ScanResult:
    config = load_config(config_path)
    output_dir = Path(config.output_dir) / result.database
    purge_old_reports(output_dir, config.report_retention_days)
    result.generated_files = write_reports(result, output_dir)
    if include_sql:
        result.generated_files["sql_bundle"] = str(collector.export_sql_bundle(output_dir))
    return result


def print_summary(result: ScanResult) -> None:
    print(f"OraPulse scan completed for database: {result.database}")
    print(f"Captured at: {result.metrics.captured_at}")
    for finding in result.findings:
        print(f"[{finding.severity.upper()}] {finding.title} - {finding.summary}")
    if result.generated_files:
        print("Generated files:")
        for name, path in result.generated_files.items():
            print(f"  {name}: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)
    configure_logging(config.log_level)

    try:
        if args.command == "scan":
            result, collector = run_scan(args.config, args.database, args.sample_data)
            if args.write_report:
                save_result(args.config, result, collector, include_sql=False)
            print_summary(result)
            return 0

        if args.command == "report":
            result, collector = run_scan(args.config, args.database, args.sample_data)
            save_result(args.config, result, collector, include_sql=args.include_sql)
            print_summary(result)
            return 0

        if args.command == "alert":
            result, collector = run_scan(args.config, args.database, args.sample_data)
            if args.write_report:
                save_result(args.config, result, collector, include_sql=False)
            channels = emit_alerts(config, result)
            print_summary(result)
            print(f"Alert channels triggered: {', '.join(channels) if channels else 'none'}")
            return 0

        if args.command == "monitor":
            loop_count = 0
            while True:
                result, collector = run_scan(args.config, args.database, args.sample_data)
                save_result(args.config, result, collector, include_sql=False)
                emit_alerts(config, result)
                print_summary(result)
                loop_count += 1
                if args.iterations and loop_count >= args.iterations:
                    return 0
                time.sleep(config.poll_interval_seconds)

    except Exception as exc:  # pragma: no cover
        logging.getLogger(__name__).exception("OraPulse failed: %s", exc)
        return 1

    return 0
