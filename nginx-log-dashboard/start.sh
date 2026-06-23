#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Deployment configuration
# Edit this section on each server before starting the process.
# ============================================================

# Shared configuration
PYTHON_BIN="/usr/bin/python3"
ZONE_NAME="DMZ1"
INGEST_TOKEN="change-this-token"
POLL_INTERVAL="0.5"

# Dashboard server configuration
DASHBOARD_HOST="0.0.0.0"
DASHBOARD_PORT="8000"
DASHBOARD_LOG_FILE="sample_access.log"
DASHBOARD_DEMO_MODE="0"
DASHBOARD_BASE_PATH="/nginx-log-dashboard"

# ============================================================
# Runtime
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLE="${1:-dashboard}"

export PYTHONPATH="${SCRIPT_DIR}/pylib_py37${PYTHONPATH:+:${PYTHONPATH}}"
export ZONE_NAME
export INGEST_TOKEN
export POLL_INTERVAL

require_file() {
    if [[ ! -f "$1" ]]; then
        echo "ERROR: file not found: $1" >&2
        exit 1
    fi
}

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "ERROR: Python executable not found: ${PYTHON_BIN}" >&2
    exit 1
fi

cd "${SCRIPT_DIR}"

case "${ROLE}" in
    dashboard)
        if [[ "${DASHBOARD_LOG_FILE}" = /* ]]; then
            export LOG_FILE_PATH="${DASHBOARD_LOG_FILE}"
        else
            export LOG_FILE_PATH="${SCRIPT_DIR}/${DASHBOARD_LOG_FILE}"
        fi
        export HOST="${DASHBOARD_HOST}"
        export PORT="${DASHBOARD_PORT}"
        export DEMO_MODE="${DASHBOARD_DEMO_MODE}"
        export DASHBOARD_BASE_PATH="${DASHBOARD_BASE_PATH}"

        require_file "${LOG_FILE_PATH}"
        echo "Starting DMZ1 Dashboard"
        echo "  listen   : ${HOST}:${PORT}"
        echo "  log_file : ${LOG_FILE_PATH}"
        echo "  demo_mode: ${DEMO_MODE}"
        echo "  base_path: ${DASHBOARD_BASE_PATH}"
        exec "${PYTHON_BIN}" -m uvicorn main:app \
            --host "${HOST}" \
            --port "${PORT}"
        ;;

    agent)
        echo "Agent configuration has moved to start_agent.sh."
        exec /usr/bin/env bash "${SCRIPT_DIR}/start_agent.sh"
        ;;

    *)
        echo "Usage: $0 [dashboard|agent]" >&2
        exit 2
        ;;
esac
