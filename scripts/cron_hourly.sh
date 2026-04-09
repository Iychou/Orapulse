#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${ORAPULSE_CONFIG:-${ROOT_DIR}/config/orapulse.yml}"
DATABASE_NAME="${ORAPULSE_DATABASE:-primary}"
LOG_FILE="${ROOT_DIR}/reports/orapulse_cron.log"

source "${ROOT_DIR}/.venv/bin/activate"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"

orapulse --config "${CONFIG_PATH}" --database "${DATABASE_NAME}" report --include-sql >> "${LOG_FILE}" 2>&1
