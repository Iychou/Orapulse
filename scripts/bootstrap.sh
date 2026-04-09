#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "${ROOT_DIR}/.venv"
source "${ROOT_DIR}/.venv/bin/activate"
pip install --upgrade pip
pip install -r "${ROOT_DIR}/requirements.txt"

echo "OraPulse environment is ready."
echo "Edit config/orapulse.yml, export your password, then run:"
echo "orapulse --config config/orapulse.yml --sample-data scan"
