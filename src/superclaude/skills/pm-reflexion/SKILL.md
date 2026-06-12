---
name: PM Reflexion
description: Cross-session project management with structured error learning. Use when resuming work across sessions ("where did we leave off", continuing multi-session work), when managing a project that spans multiple sessions, or for a post-mortem after an error, failed attempt, or wrong-direction work.
---

# PM Reflexion

Three behaviors: restore context at session start, run a PDCA loop during work,
and record a reflexion note after real failures. Every external backend is
optional — probe silently, fall back silently, never error on absence.

## 1. Session Restore

When resuming work, recover context in this priority order. Use the first
source that exists; skip missing ones without comment.

1. **Native memory directory** — if the harness provides an auto-memory
   directory (e.g. `~/.claude/projects/<project>/memory/`), read `MEMORY.md`
   and any topic files it links.
2. **Mindbase MCP** — if `mindbase_search` is available as a tool, query it
   for recent context on this project. If the tool is not present, skip
   silently; do not mention it.
3. **Repo files** — `TASK.md`, `KNOWLEDGE.md` if present, and
   `git log --oneline -10` plus `git status` for recent activity.

Then report briefly before doing anything:

```
Previous: [what the last session accomplished]
Next:     [planned next step]
Blockers: [open issues, or "none"]
```

If no source yields context, say so in one line and ask the user where work
left off. Never fabricate a previous state.

## 2. PDCA Execution Loop

For each unit of work:

- **Plan** — state the goal as something verifiable ("fix bug" → "write a
  reproducing test, make it pass"). If confidence in the approach is shaky,
  run the `confidence-check` skill before writing code.
- **Do** — execute. Track multi-step work with the todo list. Record errors
  and their fixes as they happen, not retroactively.
- **Check** — verify against evidence: tests pass, output observed, docs
  confirm. "It should work" is not a check result.
- **Act** — record what was learned. Success: note the working pattern in the
  active memory backend (same priority order as restore: native memory →
  `mindbase_store` → tell the user). Failure: run the reflexion procedure
  below.

At a natural stopping point, persist a short state snapshot (accomplished /
next / blockers) to the same backend so the next session can restore from it.

## 3. Reflexion on Failure

Trigger: a real error shipped, a test regression, or work that went in the
wrong direction and had to be redone. Not for trivial typos caught instantly.

Stop before continuing and write a structured note:

```markdown
## [short title] — YYYY-MM-DD
**What happened**: the observable failure
**Root cause**: the fundamental reason, not the symptom
**Why missed**: which check or reading was skipped
**Fix applied**: what corrected it
**Prevention**: 1-3 concrete checks to avoid recurrence
```

Where to store it, in priority order:

1. **Native memory** — append to the auto-memory directory if available.
2. **Mindbase MCP** — `mindbase_store` if the tool is available.
3. **Neither available** — show the note to the user and suggest a location
   (e.g. a `docs/mistakes/` directory). Do NOT write files into the repo
   unless the user asks.

If the user wants programmatic recording, the Python `ReflexionPattern` API
(`superclaude.pm_agent.reflexion`) requires the
`SUPERCLAUDE_REFLEXION_OUTPUT_DIR` environment variable to persist anything;
without it, nothing is written.

At the start of similar future work, check the same backends for matching
past failures and apply their prevention steps.
