#!/usr/bin/env bash
# commit-msg-normalize.sh — Git commit-msg hook
# Validates and normalizes commit messages to Conventional Commits format.
# Install: cp commit-msg-normalize.sh .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
#
# Enforces:
#   - Valid type prefix: feat|fix|docs|style|refactor|test|chore
#   - Lowercase type
#   - Subject line under 72 characters
#   - Optional scope in parentheses
#   - Body lines wrapped at 72 characters (preserving trailers and URLs)
#   - No trailing period on subject

set -euo pipefail

readonly COMMIT_MSG_FILE="${1:?Usage: commit-msg-normalize <commit-msg-file>}"

# Valid conventional commit types (from execution-patterns.yml Commit_Standards)
readonly VALID_TYPES="feat|fix|docs|style|refactor|test|chore"

# --- Color support ---
use_color() {
  [[ -t 2 ]] && [[ -z "${NO_COLOR:-}" ]] && [[ "${TERM:-dumb}" != "dumb" ]]
}

if use_color; then
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  GREEN='\033[0;32m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  RED='' YELLOW='' GREEN='' BOLD='' RESET=''
fi

error() { printf "${RED}error:${RESET} %s\n" "$1" >&2; }
warn()  { printf "${YELLOW}warn:${RESET} %s\n" "$1" >&2; }
info()  { printf "${GREEN}info:${RESET} %s\n" "$1" >&2; }

# --- Read and strip git comments ---
raw_msg=$(cat "$COMMIT_MSG_FILE")

# Strip lines starting with # (git comments) and trailing blank lines
# Use awk for portability across macOS and GNU
msg=$(printf '%s\n' "$raw_msg" | grep -v '^#' | awk 'NF{found=1} found{lines[++n]=$0} END{for(i=1;i<=n;i++){if(lines[i]~/[^[:space:]]/)last=i} for(i=1;i<=last;i++) print lines[i]}')

if [[ -z "$msg" ]]; then
  error "Commit message is empty."
  exit 1
fi

# --- Parse subject and body ---
subject=$(printf '%s\n' "$msg" | head -n1)
body=""
if [[ $(printf '%s\n' "$msg" | wc -l) -gt 1 ]]; then
  body=$(printf '%s\n' "$msg" | tail -n +2)
fi

# --- Validate and normalize subject ---

# Check for conventional commit pattern: type[(scope)][!]: description
if ! printf '%s' "$subject" | grep -qE "^[A-Za-z]+(\([A-Za-z0-9._-]+\))?\!?:"; then
  error "Subject must follow Conventional Commits format: type[(scope)]: description"
  printf "  Valid types: %s\n" "$VALID_TYPES" >&2
  printf "  Examples:\n" >&2
  printf "    feat: add user login\n" >&2
  printf "    fix(auth): resolve token expiry\n" >&2
  exit 1
fi

# Extract type
type=$(printf '%s' "$subject" | sed -E 's/^([A-Za-z]+)(\([^)]*\))?\!?:.*/\1/')

# Normalize type to lowercase
type_lower=$(printf '%s' "$type" | tr '[:upper:]' '[:lower:]')

# Validate type against allowed list
if ! printf '%s' "$type_lower" | grep -qE "^(${VALID_TYPES})$"; then
  error "Invalid commit type '${type}'."
  printf "  Valid types: %s\n" "$VALID_TYPES" >&2
  exit 1
fi

# Replace original type with lowercase version in subject
if [[ "$type" != "$type_lower" ]]; then
  subject="${type_lower}${subject#"$type"}"
  warn "Type normalized to lowercase: '${type}' -> '${type_lower}'"
fi

# Strip trailing period from subject
if [[ "$subject" == *. ]]; then
  subject="${subject%.}"
  warn "Removed trailing period from subject."
fi

# Validate subject length (72 chars max)
subject_len=${#subject}
if [[ $subject_len -gt 72 ]]; then
  error "Subject line is ${subject_len} chars (max 72)."
  exit 1
fi

# Ensure blank line between subject and body
if [[ -n "$body" ]]; then
  first_body_line=$(printf '%s\n' "$body" | head -n1)
  if [[ -n "$first_body_line" ]]; then
    body=$'\n'"$body"
  fi
fi

# --- Normalize body: wrap at 72 chars, preserving trailers and URLs ---
if [[ -n "$body" ]]; then
  normalized_body=""
  while IFS= read -r line; do
    # Preserve blank lines
    if [[ -z "$line" ]]; then
      normalized_body+=$'\n'
      continue
    fi
    # Preserve git trailers (Key: Value or Key-Word: Value)
    if printf '%s' "$line" | grep -qE '^[A-Za-z][A-Za-z0-9-]*: '; then
      normalized_body+="$line"$'\n'
      continue
    fi
    # Preserve lines containing URLs
    if printf '%s' "$line" | grep -qE 'https?://'; then
      normalized_body+="$line"$'\n'
      continue
    fi
    # Preserve lines that are already <= 72 chars
    if [[ ${#line} -le 72 ]]; then
      normalized_body+="$line"$'\n'
      continue
    fi
    # Wrap long lines at 72 chars using fold at word boundaries
    wrapped=$(printf '%s\n' "$line" | fold -s -w 72)
    normalized_body+="$wrapped"$'\n'
  done <<< "$body"
  body="$normalized_body"
fi

# --- Reassemble and write ---
{
  printf '%s\n' "$subject"
  if [[ -n "$body" ]]; then
    printf '%s' "$body"
  fi
} > "$COMMIT_MSG_FILE"

info "Commit message validated and normalized."
exit 0
