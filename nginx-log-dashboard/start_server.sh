#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="${SCRIPT_DIR}/run"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_FILE="${PID_DIR}/dashboard.pid"
LOG_FILE="${LOG_DIR}/dashboard.log"

mkdir -p "${PID_DIR}" "${LOG_DIR}"

is_running() {
    local pid="$1"
    [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1
}

if [[ -f "${PID_FILE}" ]]; then
    old_pid="$(cat "${PID_FILE}")"
    if is_running "${old_pid}"; then
        echo "Dashboard is already running: pid=${old_pid}"
        echo "Log file: ${LOG_FILE}"
        exit 0
    fi
    rm -f "${PID_FILE}"
fi

cd "${SCRIPT_DIR}"
nohup /usr/bin/env bash "${SCRIPT_DIR}/start.sh" dashboard >>"${LOG_FILE}" 2>&1 &

pid="$!"
echo "${pid}" >"${PID_FILE}"

sleep 1
if ! is_running "${pid}"; then
    echo "ERROR: Dashboard failed to start. Check log: ${LOG_FILE}" >&2
    rm -f "${PID_FILE}"
    exit 1
fi

echo "Dashboard started in background."
echo "PID     : ${pid}"
echo "PID file: ${PID_FILE}"
echo "Log file: ${LOG_FILE}"
