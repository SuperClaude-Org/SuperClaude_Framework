#!/usr/bin/env bash
# statusline.sh — Claude Code statusline (optional asset, not wired by hooks).
#
# Renders:
#   <cwd> [<branch>] ctx:<n>% 5h:<n>% 7d:<n>% <model>        <tokens> tokens
#
# Reads the Claude Code statusline JSON payload on stdin.
# To use, reference it from your settings.json:
#   "statusLine": { "type": "command",
#                   "command": "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh" }
set -u

input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')

# Git branch
branch=""
if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" branch --show-current 2>/dev/null || true)
fi

# Short cwd (home -> ~)
short_cwd=""
case "$cwd" in
  "$HOME") short_cwd="~" ;;
  "$HOME"/*) short_cwd="~${cwd#"$HOME"}" ;;
  *) short_cwd="$cwd" ;;
esac

# Context usage
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Rate limits
five=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

# Model
model_display=$(echo "$input" | jq -r '.model.display_name // empty')
model_short="${model_display#Claude }"

# Token count
input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
total_tokens=$((input_tokens + output_tokens))

# Build output
parts=""

if [ -n "$short_cwd" ]; then
  parts="$short_cwd"
fi

if [ -n "$branch" ]; then
  if [ -n "$parts" ]; then
    parts="$parts [$branch]"
  else
    parts="[$branch]"
  fi
fi

if [ -n "$used" ]; then
  ctx=$(printf "ctx:%.0f%%" "$used")
  parts="$parts $ctx"
fi

rate=""
if [ -n "$five" ]; then
  rate="5h:$(printf '%.0f' "$five")%"
fi
if [ -n "$week" ]; then
  if [ -n "$rate" ]; then
    rate="$rate 7d:$(printf '%.0f' "$week")%"
  else
    rate="7d:$(printf '%.0f' "$week")%"
  fi
fi

if [ -n "$rate" ]; then
  parts="$parts $rate"
fi

if [ -n "$model_short" ]; then
  parts="$parts $model_short"
fi

# Format token count with commas
tokens_formatted=$(awk -v n="$total_tokens" 'BEGIN{
    s=n; r=""
    while(length(s)>3){r=","substr(s,length(s)-2,3)r; s=substr(s,1,length(s)-3)}
    print s r
}' 2>/dev/null || echo "$total_tokens")

parts="${parts# }              ${tokens_formatted} tokens"

echo "$parts"
