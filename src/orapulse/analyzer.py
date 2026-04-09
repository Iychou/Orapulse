from __future__ import annotations

from .models import DatabaseConfig, Finding, ScanMetrics


def analyze_metrics(database: DatabaseConfig, metrics: ScanMetrics) -> list[Finding]:
    findings: list[Finding] = []
    thresholds = database.thresholds

    cpu_usage_pct = float(metrics.cpu.get("cpu_usage_pct") or 0)
    if cpu_usage_pct >= thresholds.cpu_percent:
        findings.append(
            Finding(
                severity="high",
                title="High CPU usage detected",
                summary=f"Estimated CPU usage is {cpu_usage_pct}%, above the threshold of {thresholds.cpu_percent}%.",
                recommendation="Check active sessions and top SQL statements to find which workload is using CPU.",
                evidence={"cpu_usage_pct": cpu_usage_pct},
            )
        )

    avg_active_sessions = float(metrics.cpu.get("avg_active_sessions") or 0)
    if avg_active_sessions >= thresholds.avg_active_sessions:
        findings.append(
            Finding(
                severity="medium",
                title="High database activity",
                summary=f"Average active sessions reached {avg_active_sessions}, above the threshold of {thresholds.avg_active_sessions}.",
                recommendation="Review session activity and top waits to understand the pressure on the database.",
                evidence={"avg_active_sessions": avg_active_sessions},
            )
        )

    if metrics.wait_events:
        top_wait = metrics.wait_events[0]
        top_wait_pct = float(top_wait.get("pct") or 0)
        if top_wait_pct >= thresholds.top_wait_event_pct:
            findings.append(
                Finding(
                    severity="medium",
                    title="Important wait event detected",
                    summary=f"The top wait event is '{top_wait.get('event')}' with {top_wait_pct}% of wait samples.",
                    recommendation="Check the sessions and SQL statements related to this wait event.",
                    evidence=top_wait,
                )
            )

    for item in metrics.io_hotspots:
        if float(item.get("avg_read_ms") or 0) >= thresholds.io_wait_ms:
            findings.append(
                Finding(
                    severity="medium",
                    title="I/O contention detected",
                    summary=f"The file {item.get('file_name')} has average read latency of {item.get('avg_read_ms')} ms.",
                    recommendation="Review storage performance and the SQL statements reading this file heavily.",
                    evidence=item,
                )
            )
            break

    for sql in metrics.top_sql:
        if float(sql.get("avg_elapsed_sec") or 0) >= thresholds.long_running_sql_seconds:
            findings.append(
                Finding(
                    severity="high",
                    title="Long-running SQL detected",
                    summary=f"SQL {sql.get('sql_id')} averages {sql.get('avg_elapsed_sec')} seconds per execution.",
                    recommendation="Review the execution plan, indexes, and row estimates for this SQL statement.",
                    evidence=sql,
                )
            )
            break

    if len(metrics.blocking_sessions) >= thresholds.blocking_sessions:
        findings.append(
            Finding(
                severity="critical",
                title="Blocking sessions detected",
                summary=f"{len(metrics.blocking_sessions)} blocking session chain(s) were found.",
                recommendation="Identify the blocking transaction and check whether it should be committed, rolled back, or optimized.",
                evidence={"blocking_sessions": metrics.blocking_sessions},
            )
        )

    if not findings:
        findings.append(
            Finding(
                severity="info",
                title="No major issue detected",
                summary="OraPulse did not find any threshold breach during this scan.",
                recommendation="Keep monitoring and compare future runs with this result.",
                evidence={},
            )
        )

    return findings
