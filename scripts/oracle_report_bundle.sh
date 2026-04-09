#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "Usage: $0 <connect_string> <begin_snap> <end_snap> <addm_task_name> <output_dir>"
  exit 1
fi

CONNECT_STRING="$1"
BEGIN_SNAP="$2"
END_SNAP="$3"
ADDM_TASK="$4"
OUTPUT_DIR="$5"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

mkdir -p "${OUTPUT_DIR}"

sqlplus -s "${CONNECT_STRING}" @"${ROOT_DIR}/sql/awr_report.sql" \
  "${BEGIN_SNAP}" "${END_SNAP}" "${OUTPUT_DIR}/awr_${BEGIN_SNAP}_${END_SNAP}.html"

sqlplus -s "${CONNECT_STRING}" @"${ROOT_DIR}/sql/ash_report.sql" \
  "${OUTPUT_DIR}/ash_recent.txt"

sqlplus -s "${CONNECT_STRING}" @"${ROOT_DIR}/sql/addm_report.sql" \
  "${ADDM_TASK}" "${OUTPUT_DIR}/addm_${BEGIN_SNAP}_${END_SNAP}.txt"

echo "Reports written to ${OUTPUT_DIR}"
