# SuperClaude Plugin for Claude Code

Eval-gated toolkit — a few skills that beat native behavior, deterministic hooks,
and optional MCP integrations. Less framework, more leverage.

## Installation

### From marketplace (when published)

```bash
/plugin marketplace add SuperClaude-Org/SuperClaude_Framework
/plugin install superclaude@SuperClaude-Org/SuperClaude_Framework --scope user
```

### Local development

```bash
claude --plugin-dir ./plugins/superclaude
```

## What's Included

### 4 Skills

| Skill | Auto-triggers on |
|-------|-----------------|
| `confidence-check` | Pre-implementation readiness gate (+ `confidence.ts`) |
| `spec-panel` | Reviewing specs, requirements, API contracts via expert panel |
| `socratic` | "Teach me / help me understand" — questions instead of answers |
| `pm-reflexion` | Resuming cross-session work, post-mortems after failures |

### 1 Agent

- `explore-haiku` — cheap codebase exploration on Haiku

### 5 Hooks (`hooks/hooks.json`)

| Hook | Event | Behavior |
|------|-------|----------|
| `session-restore` | SessionStart | TASK.md excerpt, git state, mindbase probe (silent degrade) |
| `confidence-gate` | PreToolUse (`Write\|Edit`) | Confidence criteria reminder for non-trivial work |
| `session-summary` | Stop | Outcome + remaining-work summary |
| `reflexion-trigger` | Stop | Failure reflexion via pm-reflexion skill |
| `tab-title` | session lifecycle | Terminal tab state, opt-in via `SUPERCLAUDE_TAB_TITLE=1` |

### MCP Servers (optional)

`.mcp.json` ships optional server configs. Everything works with zero MCP
servers; see the repository README for the transparency policy on
Agile-Tech-maintained integrations.

New components must pass the eval gate in `eval/` at the repository root —
see `eval/preregister.yaml` for the survive rules.

## Version

5.0.0-alpha.1
