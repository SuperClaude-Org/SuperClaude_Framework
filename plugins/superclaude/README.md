# SuperClaude Plugin for Claude Code

AI-enhanced development framework — 30 commands, 20 agents, 7 skills, and lifecycle hooks.

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

### 30 Slash Commands (`/superclaude:*`)

Planning: `pm`, `brainstorm`, `design`, `estimate`, `spec-panel`
Development: `implement`, `build`, `improve`, `cleanup`, `explain`
Testing: `test`, `analyze`, `troubleshoot`, `reflect`
Documentation: `document`, `help`
Research: `research`, `business-panel`
Utilities: `agent`, `index-repo`, `git`, `task`, `workflow`, `spawn`, `load`, `save`

### 20 Domain-Specialist Agents

`@pm-agent`, `@system-architect`, `@frontend-architect`, `@backend-architect`,
`@security-engineer`, `@deep-research`, `@quality-engineer`, `@performance-engineer`,
`@python-expert`, `@technical-writer`, `@devops-architect`, `@refactoring-expert`,
`@requirements-analyst`, `@root-cause-analyst`, `@socratic-mentor`, `@learning-guide`,
`@self-review`, `@repo-index`, `@business-panel-experts`, `@deep-research-agent`

### 7 Skills

| Skill | Auto-triggers on |
|-------|-----------------|
| `confidence-check` | Pre-implementation confidence assessment |
| `deep-research` | Research, investigate, explore requests |
| `brainstorm` | Vague requests, idea exploration |
| `troubleshoot` | Error reports, debugging |
| `pm` | Session start, task planning |
| `token-efficiency` | Low context, brevity requests |

### Hooks

| Event | Behavior |
|-------|----------|
| `SessionStart` | Initialize session context |
| `Stop` | Check for uncommitted changes and incomplete tasks |
| `PostToolUse` (Write/Edit) | Verify edit correctness |

### MCP Servers

- **Context7** — Official library documentation (prevents hallucination)
- **Sequential Thinking** — Multi-step problem solving

## Version

4.3.0
