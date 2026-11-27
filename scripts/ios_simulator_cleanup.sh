#!/usr/bin/env bash
# iOS Simulator runtime cleanup — removes all downloaded disk-image runtimes.
# Run manually or via a scheduler every 3 days to reclaim disk space.
# Usage: ./ios_simulator_cleanup.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

kill_simulator_processes() {
    local procs=(CoreSimulator simdiskimaged)
    for p in "${procs[@]}"; do
        if pgrep -f "$p" &>/dev/null; then
            log "Stopping $p..."
            $DRY_RUN || sudo pkill -9 -f "$p" 2>/dev/null || true
        fi
    done
}

shutdown_simulators() {
    log "Shutting down all simulators..."
    $DRY_RUN || xcrun simctl shutdown all 2>/dev/null || true
    sleep 2
}

delete_runtimes() {
    local identifiers
    identifiers=$(
        xcrun simctl runtime list -j 2>/dev/null \
        | python3 -c "
import json, sys
data = json.load(sys.stdin)
ids = [r.get('identifier') for r in data.get('diskImages', []) if r.get('identifier')]
print('\n'.join(ids))
" 2>/dev/null
    )

    if [[ -z "$identifiers" ]]; then
        log "No downloaded runtimes found — nothing to delete."
        return 0
    fi

    local count=0
    while IFS= read -r id; do
        [[ -z "$id" ]] && continue
        log "Deleting runtime: $id"
        if $DRY_RUN; then
            log "  (dry-run — skipped)"
        else
            xcrun simctl runtime delete "$id" && ((count++)) || log "  WARNING: failed to delete $id"
        fi
    done <<< "$identifiers"

    $DRY_RUN || log "Deleted $count runtime(s)."
}

verify() {
    log "Remaining runtimes:"
    xcrun simctl runtime list 2>/dev/null || true
}

main() {
    log "=== iOS Simulator Runtime Cleanup ==="
    $DRY_RUN && log "DRY-RUN mode — no changes will be made."

    kill_simulator_processes
    shutdown_simulators
    delete_runtimes
    verify

    log "=== Cleanup complete ==="
}

main
