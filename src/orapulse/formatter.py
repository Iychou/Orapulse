from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from jinja2 import Template

from .models import ScanResult

HTML_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OraPulse Report - {{ result.database }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f4f7fb; color: #1f2937; }
    .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; }
    .metric { background: #eef3f9; border-radius: 10px; padding: 14px; }
    .metric strong { display: block; font-size: 24px; margin-top: 6px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border-bottom: 1px solid #d7dde6; text-align: left; vertical-align: top; }
    .critical, .high { color: #b42318; font-weight: bold; }
    .medium { color: #b54708; font-weight: bold; }
    .info { color: #027a48; font-weight: bold; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>OraPulse Performance Report</h1>
      <p><strong>Database:</strong> {{ result.database }}</p>
      <p><strong>Captured at:</strong> {{ result.metrics.captured_at }}</p>
      <div class="grid">
        <div class="metric"><span>CPU Usage %</span><strong>{{ result.metrics.cpu.cpu_usage_pct }}</strong></div>
        <div class="metric"><span>CPU Cores</span><strong>{{ result.metrics.cpu.cpu_cores }}</strong></div>
        <div class="metric"><span>Avg Active Sessions</span><strong>{{ result.metrics.cpu.avg_active_sessions }}</strong></div>
        <div class="metric"><span>Blocking Sessions</span><strong>{{ result.metrics.blocking_sessions|length }}</strong></div>
      </div>
    </div>

    <div class="card">
      <h2>Findings</h2>
      <table>
        <thead><tr><th>Severity</th><th>Issue</th><th>Summary</th><th>Recommendation</th></tr></thead>
        <tbody>
        {% for finding in result.findings %}
          <tr>
            <td class="{{ finding.severity }}">{{ finding.severity|upper }}</td>
            <td>{{ finding.title }}</td>
            <td>{{ finding.summary }}</td>
            <td>{{ finding.recommendation }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Top SQL</h2>
      <table>
        <thead><tr><th>SQL ID</th><th>Avg Elapsed (s)</th><th>Executions</th><th>Buffer Gets</th><th>SQL Text</th></tr></thead>
        <tbody>
        {% for row in result.metrics.top_sql %}
          <tr>
            <td>{{ row.sql_id }}</td>
            <td>{{ row.avg_elapsed_sec }}</td>
            <td>{{ row.executions }}</td>
            <td>{{ row.buffer_gets }}</td>
            <td>{{ row.sql_text }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Wait Events</h2>
      <table>
        <thead><tr><th>Event</th><th>Samples</th><th>Percent</th></tr></thead>
        <tbody>
        {% for row in result.metrics.wait_events %}
          <tr>
            <td>{{ row.event }}</td>
            <td>{{ row.samples }}</td>
            <td>{{ row.pct }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
)


def write_reports(result: ScanResult, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = result.metrics.captured_at.strftime("%Y%m%dT%H%M%SZ")
    prefix = f"{result.database}_{stamp}"

    html_file = output_dir / f"{prefix}.html"
    json_file = output_dir / f"{prefix}.json"
    txt_file = output_dir / f"{prefix}.txt"

    html_file.write_text(HTML_TEMPLATE.render(result=asdict(result)), encoding="utf-8")
    json_file.write_text(json.dumps(asdict(result), indent=2, default=str), encoding="utf-8")
    txt_file.write_text(_build_text_report(result), encoding="utf-8")

    return {"html": str(html_file), "json": str(json_file), "txt": str(txt_file)}


def _build_text_report(result: ScanResult) -> str:
    lines = [
        f"OraPulse Report - {result.database}",
        f"Captured at: {result.metrics.captured_at}",
        "",
        "Findings:",
    ]
    for finding in result.findings:
        lines.append(f"- [{finding.severity.upper()}] {finding.title}")
        lines.append(f"  Summary: {finding.summary}")
        lines.append(f"  Recommendation: {finding.recommendation}")

    lines.extend(["", "Top SQL:"])
    for item in result.metrics.top_sql:
        lines.append(
            f"- {item.get('sql_id')} avg_elapsed={item.get('avg_elapsed_sec')}s executions={item.get('executions')} sql={item.get('sql_text')}"
        )

    lines.extend(["", "Wait Events:"])
    for item in result.metrics.wait_events:
        lines.append(f"- {item.get('event')} {item.get('pct')}%")

    return "\n".join(lines) + "\n"
