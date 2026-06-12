#!/usr/bin/env bash
# tab-title.sh — Claude Code terminal tab-title hook (opt-in, cosmetic).
#
# Canonical home: https://github.com/agiletec-inc/claude-code-terminal-ux
# (tab-title module). This copy is adapted for plugin distribution; sync
# behavioral changes from upstream rather than diverging here.
#
# Silent no-op unless SUPERCLAUDE_TAB_TITLE=1 is set in the environment.
#
# Sets the tab title via the `terminalSequence` hook output — Claude Code
# emits OSC 0 on our behalf (hooks have no controlling TTY, so we cannot
# write the escape sequence directly).
#
# Usage: tab-title.sh <state> <running-emoji> <waiting-emoji> <idle-emoji>
#   state: idle | running | waiting | stop
#
# Hot paths (idle/running/waiting) spawn zero subprocesses beyond this script
# itself. Only `stop` reads stdin and calls jq, because Stop fires on every
# turn end (including question-asking turns) and we need the transcript to
# disambiguate "done" from "asked a question".
set -u

[ "${SUPERCLAUDE_TAB_TITLE:-0}" = "1" ] || exit 0

state="${1-}"
running_emoji="${2-}"
waiting_emoji="${3-}"
idle_emoji="${4-}"

cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
repo=$(basename "$cwd")
[ -z "$repo" ] && repo="claude"

emoji=""
case "$state" in
  running) emoji="$running_emoji" ;;
  waiting) emoji="$waiting_emoji" ;;
  idle)    emoji="$idle_emoji" ;;
  stop)
    emoji="$idle_emoji"
    payload=$(cat)
    tp=$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null)
    if [ -n "$tp" ] && [ -f "$tp" ]; then
      last=$(tail -n 200 "$tp" | grep '"type":"assistant"' | tail -n 1)
      if [ -n "$last" ]; then
        names=$(printf '%s' "$last" | jq -r \
          '[.message.content[]? | select(.type=="tool_use") | .name] | join(" ")' \
          2>/dev/null)
        case " $names " in
          *" AskUserQuestion "*|*" ExitPlanMode "*) emoji="$waiting_emoji" ;;
        esac
      fi
    fi
    ;;
  *) exit 0 ;;
esac

if [ -n "$emoji" ]; then
  title="$emoji $repo"
else
  title="$repo"
fi

# JSON-escape backslash and double-quote in the title. ESC and BEL are
# emitted as \u escapes so the JSON payload stays free of raw control bytes.
esc=$(printf '%s' "$title" | sed 's/\\/\\\\/g; s/"/\\"/g')
printf '{"terminalSequence":"\\u001b]0;%s\\u0007"}\n' "$esc"
exit 0
