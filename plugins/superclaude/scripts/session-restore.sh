#!/usr/bin/env bash
# session-restore.sh — SessionStart hook: deterministic context emission.
#
# Prints lightweight project context (current task, git state) and probes
# optional services. Every external piece degrades silently — this script
# must never break a session. Always exits 0.
set -u

cwd="${CLAUDE_PROJECT_DIR:-$PWD}"

# 1. Current task context (TASK.md, first ~30 lines)
if [ -f "$cwd/TASK.md" ]; then
  echo "## TASK.md (first 30 lines)"
  head -n 30 "$cwd/TASK.md" 2>/dev/null
  echo ""
fi

# 2. Git context
if git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
  dirty=$(git -C "$cwd" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  echo "## Git: branch ${branch:-detached}, ${dirty:-0} modified files"
  git -C "$cwd" log --oneline -5 2>/dev/null
  echo ""
fi

# 3. Mindbase probe (optional service; silent when absent)
for port in 18002 18003; do
  if curl -sf --max-time 1 "http://localhost:${port}/health" >/dev/null 2>&1; then
    echo "Mindbase is running (port ${port}): mindbase MCP tools are available for deeper cross-session context."
    break
  fi
done

exit 0
