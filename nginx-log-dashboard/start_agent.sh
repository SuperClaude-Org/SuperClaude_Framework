#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# DMZ1 Agent deployment configuration
# Edit this section on each Nginx server before starting.
# ============================================================

PYTHON_BIN="/usr/bin/python3"

ZONE_NAME="DMZ1"
SOURCE_NAME="$(hostname)"
LOG_FILE_PATH="/var/log/nginx/access.log"

DASHBOARD_URL="http://10.0.0.10:8000"
INGEST_TOKEN="change-this-token"

SAMPLE_RATE="0.01"
BATCH_SIZE="500"
FLUSH_INTERVAL="2.0"
POLL_INTERVAL="0.5"
QUEUE_SIZE="100000"

# ============================================================
# Runtime
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="${SCRIPT_DIR}/pylib_py37${PYTHONPATH:+:${PYTHONPATH}}"
export ZONE_NAME
export SOURCE_NAME
export LOG_FILE_PATH
export DASHBOARD_URL
export INGEST_TOKEN
export SAMPLE_RATE
export BATCH_SIZE
export FLUSH_INTERVAL
export POLL_INTERVAL
export QUEUE_SIZE

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "ERROR: Python executable not found: ${PYTHON_BIN}" >&2
    exit 1
fi

if [[ ! -f "${LOG_FILE_PATH}" ]]; then
    echo "ERROR: Nginx log file not found: ${LOG_FILE_PATH}" >&2
    exit 1
fi

cd "${SCRIPT_DIR}"

echo "Starting DMZ1 Nginx Agent"
echo "  node         : ${SOURCE_NAME}"
echo "  zone         : ${ZONE_NAME}"
echo "  log_file     : ${LOG_FILE_PATH}"
echo "  dashboard_url: ${DASHBOARD_URL}"
echo "  sample_rate  : ${SAMPLE_RATE}"
echo "  batch_size   : ${BATCH_SIZE}"
echo "  queue_size   : ${QUEUE_SIZE}"

exec "${PYTHON_BIN}" agent.py
