from __future__ import annotations

import json
import logging
import smtplib
from email.message import EmailMessage

from .models import AppConfig, ScanResult

LOGGER = logging.getLogger(__name__)


def emit_alerts(config: AppConfig, result: ScanResult) -> list[str]:
    channels: list[str] = []
    alert_findings = [item for item in result.findings if item.severity in {"critical", "high", "medium"}]
    if not alert_findings:
        return channels

    if "log" in config.alert_channels:
        LOGGER.warning(
            "OraPulse alert: %s",
            json.dumps(
                {
                    "database": result.database,
                    "captured_at": str(result.metrics.captured_at),
                    "issues": [item.title for item in alert_findings],
                }
            ),
        )
        channels.append("log")

    if "email" in config.alert_channels and config.email.enabled:
        _send_email(config, result, alert_findings)
        channels.append("email")

    return channels


def _send_email(config: AppConfig, result: ScanResult, findings) -> None:
    message = EmailMessage()
    message["Subject"] = f"OraPulse alert - {result.database}"
    message["From"] = config.email.from_address
    message["To"] = ", ".join(config.email.to)

    body = [
        f"OraPulse detected {len(findings)} issue(s) for {result.database}.",
        f"Captured at: {result.metrics.captured_at}",
        "",
    ]
    for item in findings:
        body.append(f"- [{item.severity.upper()}] {item.title}: {item.summary}")
    message.set_content("\n".join(body))

    with smtplib.SMTP(config.email.smtp_host, config.email.smtp_port, timeout=20) as smtp:
        if config.email.use_tls:
            smtp.starttls()
        if config.email.username:
            smtp.login(config.email.username, config.email.password)
        smtp.send_message(message)
