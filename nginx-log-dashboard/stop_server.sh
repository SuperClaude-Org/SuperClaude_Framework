#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/run/dashboard.pid"
TIMEOUT_SECONDS="${STOP_TIMEOUT_SECONDS:-15}"

is_running() {
    local pid="$1"
    [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1
}

if [[ ! -f "${PID_FILE}" ]]; then
    echo "Dashboard is not running: PID file not found."
    exit 0
fi

pid="$(cat "${PID_FILE}")"
if ! is_running "${pid}"; then
    echo "Dashboard process is not running. Removing stale PID file."
    rm -f "${PID_FILE}"
    exit 0
fi

echo "Stopping Dashboard: pid=${pid}"
kill "${pid}" >/dev/null 2>&1 || true

for _ in $(seq 1 "${TIMEOUT_SECONDS}"); do
    if ! is_running "${pid}"; then
        rm -f "${PID_FILE}"
        echo "Dashboard stopped."
        exit 0
    fi
    sleep 1
done

echo "Dashboard did not stop within ${TIMEOUT_SECONDS}s; sending SIGKILL." >&2
kill -9 "${pid}" >/dev/null 2>&1 || true
rm -f "${PID_FILE}"
echo "Dashboard stopped."
