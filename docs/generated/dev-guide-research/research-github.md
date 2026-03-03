# GitHub Research: Claude Code Custom Agents, Skills, and Slash Commands

**Research Date**: 2026-02-21
**Scope**: GitHub repositories extending Claude Code with custom commands, agents, skills, plugins, hooks, and MCP integrations
**Method**: Systematic web search across GitHub with deep extraction from key repositories

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Official Anthropic Resources](#official-anthropic-resources)
3. [Curated Lists and Guides](#curated-lists-and-guides)
4. [Skill Package Structure (Official)](#skill-package-structure-official)
5. [Agent Definition Format](#agent-definition-format)
6. [Slash Command Patterns](#slash-command-patterns)
7. [Plugin and Marketplace System](#plugin-and-marketplace-system)
8. [Hook Configuration Patterns](#hook-configuration-patterns)
9. [Multi-Agent Orchestration Frameworks](#multi-agent-orchestration-frameworks)
10. [CLAUDE.md and Configuration Patterns](#claudemd-and-configuration-patterns)
11. [MCP Server Integration Examples](#mcp-server-integration-examples)
12. [Community Framework Repositories](#community-framework-repositories)
13. [Prompt Engineering Patterns](#prompt-engineering-patterns)
14. [Key Architectural Decisions and Patterns](#key-architectural-decisions-and-patterns)
15. [Comparison with SuperClaude](#comparison-with-superclaude)

---

## Executive Summary

The Claude Code extension ecosystem has matured significantly through 2025-2026. The official plugin system (released October 2025) provides a standardized structure for distributing agents, skills, commands, and hooks. Key findings:

- **Official skill format**: SKILL.md with YAML frontmatter (`name`, `description`) + markdown instructions body (1500-2000 words target)
- **Agent format**: `.md` files in `.claude/agents/` with YAML frontmatter (`name`, `description`, `model`) + system prompt body
- **Command format**: Markdown files in `.claude/commands/` where filename = command name, `$ARGUMENTS` captures user input
- **Plugin format**: Directory with `.claude-plugin/plugin.json` metadata + optional commands/, agents/, skills/, hooks/
- **Hook system**: JSON configuration in `.claude/settings.json` with PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit events
- **Ecosystem size**: 100+ repos, 500+ community commands, 200+ agents, 50+ skills across the ecosystem

---

## Official Anthropic Resources

### 1. anthropics/skills (Official Skills Repository)

**URL**: [github.com/anthropics/skills](https://github.com/anthropics/skills)

The official Anthropic skills repository defines the canonical skill format.

**Key Structure**:
```
./skills/          # Skill examples (Creative, Dev, Enterprise, Document)
./spec/            # The Agent Skills specification
./template/        # Skill template
```

**Skill Discovery**: Skills are loaded dynamically by Claude when relevant. Users activate by mentioning the skill in their request:
> "Use the PDF skill to extract the form fields from path/to/some-file.pdf"

**Installation**:
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

**Document skills included**: `docx`, `pdf`, `pptx`, `xlsx`

---

### 2. anthropics/claude-code (Official Plugins Directory)

**URL**: [github.com/anthropics/claude-code/tree/main/plugins](https://github.com/anthropics/claude-code/tree/main/plugins)

Official plugins from Anthropic demonstrating all extension patterns:

| Plugin | Type | Description |
|--------|------|-------------|
| `agent-sdk-dev` | Command + Agents | Development kit for Claude Agent SDK |
| `code-review` | Command + 5 Agents | Automated PR review with confidence-based scoring |
| `commit-commands` | Commands | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `feature-dev` | Command + 3 Agents | 7-phase feature development workflow |
| `frontend-design` | Skill | Auto-invoked for bold frontend design choices |
| `hookify` | Commands + Agent + Skill | Create custom hooks from conversation analysis |
| `plugin-dev` | Command + 3 Agents + 7 Skills | Complete plugin development toolkit |
| `pr-review-toolkit` | Command + 6 Agents | Parallel PR review from multiple perspectives |
| `ralph-wiggum` | Commands + Hook | Self-referential iteration loops |
| `security-guidance` | Hook | PreToolUse security pattern monitoring |
| `explanatory-output-style` | Hook | Educational insights at session start |
| `learning-output-style` | Hook | Interactive learning at decision points |

---

### 3. anthropics/claude-plugins-official

**URL**: [github.com/anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

Official, Anthropic-managed directory of high-quality Claude Code Plugins. Serves as a curated marketplace.

---

### 4. Piebald-AI/claude-code-system-prompts

**URL**: [github.com/Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts)

Extracted system prompts from Claude Code v2.1.50 (2026-02-20). Contains all internal prompts Claude Code uses, including:

**Sub-agent prompts**: Explore, Plan mode (enhanced), Task tool
**Creation assistants**: Agent creation architect, CLAUDE.md creation, Status line setup
**Slash command agents**: `/review-pr`, `/security-review`, `/pr-comments`
**Utility agents**: Conversation summarization, session memory, sentiment analysis, WebFetch summarizer
**Data references**: Agent SDK patterns (Python/TypeScript), API references (7 languages), model catalog
**System prompt parts**: 30+ modular system prompt components
**System reminders**: 40+ contextual reminder messages
**Tool descriptions**: 25+ builtin tool instruction blocks

Also provides **tweakcc** tool to customize and patch Claude Code system prompts.

---

## Curated Lists and Guides

### awesome-claude-code

**URL**: [github.com/hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)

The definitive curated list for the ecosystem. Notable entries include:
- **Context Engineering Kit** (Vlad Goncharov) -- Advanced context engineering with minimal token footprint
- **Auto-Claude** (AndyMik90) -- Autonomous multi-agent framework with kanban UI
- **Claude Swarm** -- Connected swarm of Claude Code agent sessions
- **Claude Code Flow** -- Recursive agent cycle orchestration
- **AgentSys** (avifenesh) -- Task-to-production workflow automation

### Claude Code Everything You Need to Know

**URL**: [github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know](https://github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know)

Comprehensive guide covering setup through advanced usage. Key insights on CLAUDE.md:
- Run `/init` to auto-generate CLAUDE.md
- CLAUDE.md files become part of Claude's prompts -- refine like frequently used prompts
- Common mistake: adding extensive content without iterating on effectiveness

### Claude Code Best Practice

**URL**: [github.com/shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)

Key insight: Custom slash commands have been merged into skills. Files in `.claude/commands/` still work, but skills (`.claude/skills/`) are recommended as they support additional features like supporting files, invocation control, and subagent execution.

---

## Skill Package Structure (Official)

### Directory Layout

```
skill-name/
├── SKILL.md                    # Required - instructions + metadata
│   ├── YAML frontmatter        # Required (name, description)
│   └── Markdown instructions   # Required (1500-2000 words target)
└── Bundled Resources           # Optional
    ├── scripts/                # Executable code (Python/Bash)
    ├── references/             # Documentation loaded as needed
    └── assets/                 # Templates, icons, fonts for output
```

### YAML Frontmatter (Required Fields Only)

```yaml
---
name: my-skill-name
description: This skill should be used when the user asks to "specific phrase 1",
  "specific phrase 2", "specific phrase 3". Include exact phrases users would say
  that should trigger this skill. Be concrete and specific.
---
```

**Only `name` and `description` are read by Claude** to determine when the skill triggers.

### Description Best Practices

The description field is critical for discovery. It must be:
- Written in **third person** ("This skill should be used when...")
- Include **concrete trigger phrases** (literal phrases users say)
- Be comprehensive about when the skill should activate

**Good example**:
```yaml
description: This skill should be used when the user asks to "create a hook",
  "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks",
  or mentions hook events (PreToolUse, PostToolUse, Stop).
```

**Bad examples**:
```yaml
description: Use this skill when working with hooks.    # Wrong person, vague
description: Load when user needs hook help.             # Not third person
description: Provides hook guidance.                     # No trigger phrases
```

### SKILL.md Body Writing Guidelines

- Write in **imperative/infinitive form** (verb-first instructions), not second person
- Use objective, instructional language
- **Correct**: "To create a hook, define the event type." / "Configure the MCP server with authentication."
- **Incorrect**: "You should create a hook..." / "You need to..."
- Target **1,500-2,000 words** for the body
- Move detailed content to `references/`
- The skill is being created for **another instance of Claude** to use
- Include non-obvious procedural knowledge, domain-specific details, or reusable assets

### Progressive Disclosure Model (3 Levels)

| Level | Content | When Loaded | Size Target |
|-------|---------|-------------|-------------|
| 1. Metadata | name + description | Always in context | ~100 words |
| 2. SKILL.md body | Full instructions | When skill triggers | <2,000 words |
| 3. Bundled resources | scripts/refs/assets | As needed | Unlimited (scripts run without loading) |

### Bundled Resource Guidelines

- **scripts/**: Deterministic, repeatable code; executed without loading into context
- **references/**: Documentation loaded as needed; avoid duplicating content from SKILL.md
  - If reference files are large (>10k words), include grep/search patterns in SKILL.md
- **assets/**: Files for final output (templates, images, boilerplate), not meant for context

### Skill Template

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

### Creating Skills for Plugins

For plugins, create skill directories directly under the plugin:
```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

Plugin skills are created manually (don't use `init_skill.py`).

---

## Agent Definition Format

### Two Formats in the Ecosystem

#### Format 1: YAML Frontmatter `.md` Files (File Storage Format)

Agent files stored in `.claude/agents/` use YAML frontmatter:

```yaml
---
name: evaluator
description: Invoke this agent to run the evaluations for ideas proposed by the user
model: inherit
---

# Agent System Prompt

You are an expert evaluator specializing in...

## Responsibilities
- Evaluate user proposals against criteria
- Provide scoring with rationale
...
```

**Required fields**:
- `name` -- The agent's identifier
- `description` -- Defines when the orchestrator picks this subagent for delegation

**Optional fields**:
- `model` -- `inherit` (use parent model), `sonnet`, `opus`, `haiku`
- `color` -- UI color for the agent

**Key insight**: The content below the frontmatter is the **system prompt**, not a user prompt. This is the #1 misunderstanding when creating agents.

#### Format 2: JSON Object (Internal Creation Format)

Claude Code's internal agent creation system outputs agents as JSON:

```json
{
  "identifier": "test-runner",
  "whenToUse": "Use this agent when the user needs to run tests...",
  "systemPrompt": "You are an expert test runner..."
}
```

**Fields**:
- `identifier` -- Lowercase letters, numbers, hyphens; typically 2-4 hyphenated words; avoid "helper/assistant"
- `whenToUse` -- Must start with "Use this agent when..." and include usage examples
- `systemPrompt` -- Complete system prompt in 2nd person ("You are...", "You will...")

The JSON format gets translated into the YAML frontmatter `.md` file format by Claude Code's `/agents` command.

### Agent Creation Architect (Official Internal Prompt)

The agent creation architect follows a 5-step workflow:
1. **Extract intent** (purpose, responsibilities, success criteria)
2. **Design persona** (expert identity appropriate to domain)
3. **Write comprehensive instructions** (boundaries, methods, edge cases, output formats)
4. **Optimize performance** (decision frameworks, QA/self-checks, escalation/fallback)
5. **Create identifier** (lowercase/numbers/hyphens, 2-4 words, avoid generic terms)

### System Prompt Writing Principles

- Be specific and detailed
- Use examples when helpful
- Maintain clarity
- Handle variations and edge cases
- Ask for clarification proactively
- Include QA/self-correction mechanisms
- Write as complete operational manual (agents operate autonomously)

### Example Agent Definitions from Community

**Code Reviewer** (from feiskyer/claude-code-settings):
```yaml
---
name: pr-reviewer
description: Invoke this agent for comprehensive PR code review covering
  TypeScript strictness, error handling, loading states, mutation patterns,
  and architectural compliance.
model: sonnet
---

You are an expert code reviewer...
```

**QA Agents** (from darcyegb/ClaudeCodeAgents):
- Each agent follows a specific format Claude Code can interpret
- Focused on single QA responsibility
- Include checklist-style validation steps

---

## Slash Command Patterns

### File-Based Commands

Commands are markdown files in `.claude/commands/` where:
- **Filename** = command name (e.g., `code-review.md` = `/code-review`)
- **Content** = execution instructions and prompts
- **`$ARGUMENTS`** = placeholder capturing user input
- **Directory** = namespace prefix (e.g., `dev/code-review.md` = `/dev:code-review`)

### Command with Frontmatter (artemgetmann pattern)

```yaml
---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
description: Perform comprehensive code review
argument-hint: [file or directory to review]
---

Analyze $ARGUMENTS for code quality issues...
```

### Namespace Organization (qdhenry/Claude-Command-Suite)

148+ commands organized by namespace:

| Namespace | Domain | Example Commands |
|-----------|--------|-----------------|
| `/project:*` | Project Management | `init-project`, `create-feature`, `milestone-tracker` |
| `/dev:*` | Development | `code-review`, `debug-error`, `refactor-code`, `ultra-think` |
| `/test:*` | Testing | `generate-test-cases`, `write-tests`, `e2e-setup` |
| `/security:*` | Security | `security-audit`, `dependency-audit`, `security-hardening` |
| `/performance:*` | Performance | `performance-audit`, `optimize-build`, `optimize-bundle-size` |
| `/sync:*` | Integration | `sync-issues-to-linear`, `bidirectional-sync` |
| `/deploy:*` | Deployment | `prepare-release`, `hotfix-deploy`, `containerize-application` |
| `/docs:*` | Documentation | `generate-api-documentation`, `migration-guide` |
| `/setup:*` | Configuration | `setup-dev-environment`, `setup-monorepo`, `design-rest-api` |
| `/team:*` | Collaboration | `standup-report`, `sprint-planning`, `retrospective-analyzer` |

### Workflow Commands (wshobson/commands)

57 production-ready commands split into:
- **15 Workflows** (multi-agent orchestration)
- **42 Tools** (single-purpose utilities)

**Workflow example invocation**:
```
/workflows:feature-development OAuth2 authentication with JWT tokens
/workflows:tdd-cycle shopping cart with discount calculation logic
```

**Tool example invocation**:
```
/tools:api-scaffold REST endpoints for user management with RBAC
/tools:security-scan perform vulnerability assessment
```

### Workflow-Oriented Commands (ronnycoding/.claude)

Three methodologies:
1. **Issue-driven**: `/issue` -> `/task` (issue to implementation to PR)
2. **BDD-first**: `/user-story` -> `/issue` -> `/task` (Gherkin scenarios first)
3. **Scaled execution**: `/work-on-opens` using git worktrees and tiered dependency grouping

### Command Precedence

- Project commands (`.claude/commands/`) override global commands (`~/.claude/commands/`)
- Within directories, the filename determines the command name
- Files loaded on startup and available immediately

---

## Plugin and Marketplace System

### Plugin Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata (required)
├── commands/               # Slash commands (optional)
├── agents/                 # Specialized agents (optional)
├── skills/                 # Agent Skills (optional)
├── hooks/                  # Event handlers (optional)
│   └── hooks.json          # Auto-loaded by Claude Code v2.1+
├── .mcp.json               # MCP server configuration (optional)
└── README.md               # Plugin documentation
```

### plugin.json Format

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "A brief description of what your plugin does",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com"
  }
}
```

**Important**: Do NOT add a `"hooks"` field to `plugin.json`. Claude Code v2.1+ auto-loads `hooks/hooks.json` from installed plugins. Declaring it explicitly causes duplicate detection errors.

### marketplace.json Format

A marketplace is a Git repository with `.claude-plugin/marketplace.json`:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "marketplace-name",
  "version": "1.0.0",
  "description": "Description of the marketplace",
  "owner": {
    "name": "Organization Name",
    "email": "email@example.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "What the plugin does",
      "source": "./plugins/plugin-name",
      "category": "development",
      "version": "1.0.0",
      "author": {
        "name": "Author Name",
        "email": "author@example.com"
      }
    }
  ]
}
```

### Installation Commands

```
# Add a marketplace
/plugin marketplace add https://github.com/org/repo

# Install from marketplace
/plugin install plugin-name@marketplace-name

# Direct from local path
/plugin marketplace add ./path/to/marketplace
```

For private repositories, Claude Code uses existing git credential helpers.

### Cross-Tool Plugin Conversion

The [compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) includes a CLI that converts Claude Code plugins to: OpenCode, Codex, Factory Droid, Pi, Gemini CLI, GitHub Copilot, and Kiro CLI formats.

### Plugin Template

**URL**: [github.com/ivan-magda/claude-code-plugin-template](https://github.com/ivan-magda/claude-code-plugin-template)

GitHub template for creating Claude Code plugin marketplaces with validation, CI/CD workflows, and pre-configured structure.

---

## Hook Configuration Patterns

### Hook Events

| Event | When | Use Cases |
|-------|------|-----------|
| `PreToolUse` | Before tool execution | Block dangerous ops, validate inputs, security checks |
| `PostToolUse` | After tool execution | Auto-format, run tests, log actions |
| `Stop` | When Claude Code stops | Create checkpoints, cleanup, summarize |
| `SubagentStop` | After subagents finish | Validate output, aggregate results |
| `UserPromptSubmit` | First prompt of session | Set context, activate tools, thinking level |

### Configuration in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/script.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/post-script.sh"
          }
        ]
      }
    ]
  }
}
```

### Exit Code Behavior

| Code | Behavior |
|------|----------|
| `0` | Success, continue execution |
| `2` | Block the tool use; stderr fed back to Claude |

- `stdout` shown to user in transcript mode (Ctrl-R)
- `stderr` automatically fed back to Claude

### Prompt-Based Hooks (New in 2026)

```json
{
  "type": "prompt",
  "prompt": "Check if this file write is safe: validate system paths, credentials, path traversal, and sensitive content. Return 'approve' or 'deny'."
}
```

### Community Hook Examples

**Block edits on main branch** (PreToolUse):
```bash
#!/bin/bash
branch=$(git branch --show-current 2>/dev/null)
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  echo "Cannot edit on main branch" >&2
  exit 2
fi
```

**Auto-format on write** (PostToolUse):
```bash
#!/bin/bash
file="$1"
if [[ "$file" == *.ts ]] || [[ "$file" == *.tsx ]]; then
  npx prettier --write "$file"
fi
```

**Security pattern monitoring** (PreToolUse) -- from official `security-guidance` plugin:
Monitors 9 patterns including command injection, XSS, eval usage, dangerous HTML, pickle deserialization, and os.system calls.

### Best Practices

1. Use `$CLAUDE_PROJECT_DIR` for reliable path resolution
2. Keep hooks as standalone scripts (e.g., in `.claude/hooks/`)
3. Validate and sanitize inputs; quote shell variables
4. Block path traversal; use absolute paths
5. Skip sensitive files (`.env`, `.git/`)
6. Default 60-second timeout (configurable per command)
7. All matching hooks run in parallel
8. Use `/hooks` command for interactive configuration
9. Test with `claude --debug` for hook logs

### Key Hook Repositories

- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) -- Comprehensive mastery guide
- [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) -- Real-time agent monitoring
- [karanb192/claude-code-hooks](https://github.com/karanb192/claude-code-hooks) -- Copy-paste hook collection
- [decider/claude-hooks](https://github.com/decider/claude-hooks) -- Clean code enforcement hooks
- [johnlindquist/claude-hooks](https://github.com/johnlindquist/claude-hooks) -- TypeScript-based hook framework
- [anthropics/claude-code/examples/settings](https://github.com/anthropics/claude-code/tree/main/examples/settings) -- Official settings examples

---

## Multi-Agent Orchestration Frameworks

### 1. claude-flow (ruvnet/claude-flow) -- "Ruflo"

**URL**: [github.com/ruvnet/claude-flow](https://github.com/ruvnet/claude-flow)

Leading agent orchestration platform. Features:
- Intelligent multi-agent swarms
- Autonomous workflow coordination
- Enterprise-grade architecture
- RAG integration
- Native MCP protocol support

**Integration**:
```bash
claude mcp add ruflo -- npx -y ruflo@latest mcp start
```

### 2. claude-code-mcp (steipete/claude-code-mcp)

**URL**: [github.com/steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp)

Claude Code as a one-shot MCP server ("agent in your agent"). Single `claude_code` tool handles complex multi-step tasks like branch creation, file updates, commits, and PR creation in one operation.

### 3. claude-code-mcp-enhanced (grahama1970)

**URL**: [github.com/grahama1970/claude-code-mcp-enhanced](https://github.com/grahama1970/claude-code-mcp-enhanced)

Enhanced MCP server with "boomerang pattern" -- breaks complex tasks into manageable subtasks. Features task orchestration, health check API, hot reloading.

### 4. oh-my-claude (lgcyaxi/oh-my-claude)

**URL**: [github.com/lgcyaxi/oh-my-claude](https://github.com/lgcyaxi/oh-my-claude)

Multi-provider orchestration: Routes background tasks to DeepSeek, ZhiPu GLM, MiniMax via Anthropic-compatible APIs. Includes Prometheus planning agent.

### 5. claude-mpm (bobmatnyc/claude-mpm)

**URL**: [github.com/bobmatnyc/claude-mpm](https://github.com/bobmatnyc/claude-mpm)

Multi-Agent Project Manager with 47+ specialized agents, intelligent PM orchestration, 44+ bundled skills, semantic code search, and ticket management via GitHub, Linear, Jira.

### 6. multi-agent-ralph-loop (alfredolopez80)

**URL**: [github.com/alfredolopez80/multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop)

Memory-driven planning with task classification, model routing, multi-agent coordination, and persistent cross-session memory.

### Orchestration Patterns (Summary)

| Pattern | Description | Example |
|---------|-------------|---------|
| Sequential | Agents run in series | Plan -> Implement -> Review |
| Parallel | Agents run simultaneously | 5 reviewers analyze different aspects |
| Validation | One agent validates another's work | Implementer + Reviewer |
| Conditional | Agent selection based on context | Security for auth files, Frontend for UI |
| Boomerang | Break tasks into subtasks, reassemble | Complex feature decomposition |
| Swarm | Multiple agents self-organize | Distributed codebase analysis |
| Loop | Iterative refinement until criteria met | TDD cycles |

---

## CLAUDE.md and Configuration Patterns

### File Discovery Hierarchy

1. `~/.claude/CLAUDE.md` -- Global defaults (all projects)
2. Project root `CLAUDE.md` -- Project-specific
3. `.claude/CLAUDE.md` -- Project config directory
4. Subdirectory `CLAUDE.md` files -- Directory-specific context

Files concatenated from root down; project-level overrides global.

### AGENTS.md Cross-Tool Compatibility

Emerging standard for universal agent instructions:

```markdown
# AGENTS.md

## Build Commands
- `npm run build` for production
- `npm run dev` for development

## Testing
- `npm test` for unit tests
- Always run tests before committing

## Code Style
- TypeScript strict mode
- ESLint + Prettier configured
```

**Bridge pattern**: `CLAUDE.md` references `@AGENTS.md` for shared instructions plus Claude-specific features.

### Configuration Examples

**settings.json** (from ChrisWiles/claude-code-showcase):
```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["jira", "linear"]
}
```

**settings.local.json** for personal overrides (not committed to git).

### CLAUDE.md Best Practices

1. Keep under 150 lines -- long files bury the signal
2. Iterate on effectiveness like a frequently used prompt
3. Wrap commands in backticks so agents can copy-paste
4. Use `/init` to auto-generate initial CLAUDE.md
5. Include build/test/lint commands Claude will need
6. Reference other instruction files with `@filename.md`

---

## MCP Server Integration Examples

### .mcp.json Configuration

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-jira"],
      "env": {
        "JIRA_HOST": "https://your-instance.atlassian.net",
        "JIRA_EMAIL": "your@email.com",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    },
    "linear": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-linear"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

### MCP + Command Integration (ChrisWiles pattern)

The `/ticket` command orchestrates end-to-end ticket workflow:
1. Read ticket criteria from Linear/Jira (MCP)
2. Implement the feature
3. Link PR to ticket
4. Update tracker status

---

## Community Framework Repositories

### Complete Configuration Examples

| Repository | Agents | Commands | Skills | Hooks | Stars Pattern |
|-----------|--------|----------|--------|-------|---------------|
| [ronnycoding/.claude](https://github.com/ronnycoding/.claude) | 83+ | 13 | 10 | Yes | Personal config |
| [feiskyer/claude-code-settings](https://github.com/feiskyer/claude-code-settings) | 7 | 8+ | Yes | Yes | Vibe coding |
| [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite) | 54 | 148+ | 2 | Yes | Enterprise suite |
| [wshobson/commands](https://github.com/wshobson/commands) | - | 57 | - | - | Production commands |
| [wshobson/agents](https://github.com/wshobson/agents) | 112 | - | 146 | - | Agent collection |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 12+ | 3+ | 20+ | Yes | Hackathon winner |
| [carlrannaberg/claudekit](https://github.com/carlrannaberg/claudekit) | Yes | 15+ | - | 15+ | CLI toolkit |
| [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) | Yes | 3+ | Yes | Yes | GitHub Actions |
| [Yugoge/claude-code-config](https://github.com/Yugoge/claude-code-config) | 14 | 32 | - | 21 | Global config |
| [vincenthopf/My-Claude-Code](https://github.com/vincenthopf/My-Claude-Code) | - | Yes | - | - | Daily essentials |

### Framework-Style Projects

| Repository | Description |
|-----------|-------------|
| [alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) | Toolkit for building production-ready skills, agents, and commands at scale |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 26+ domain skill packages |
| [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | Skills marketplace |
| [Aaronontheweb/dotnet-skills](https://github.com/Aaronontheweb/dotnet-skills) | .NET-specific skills and subagents |
| [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | Manus-style persistent markdown planning |

### Prompt Engineering and Guides

| Repository | Description |
|-----------|-------------|
| [ThamJiaHe/claude-prompt-engineering-guide](https://github.com/ThamJiaHe/claude-prompt-engineering-guide) | Anthropic 10-Component Framework, XML tagging, tool integration |
| [Comfy-Org/comfy-claude-prompt-library](https://github.com/Comfy-Org/comfy-claude-prompt-library) | Reusable Claude Code commands for team workflows |
| [langgptai/awesome-claude-prompts](https://github.com/langgptai/awesome-claude-prompts) | Prompt curation for better Claude usage |
| [zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide) | Setup, commands, workflows, agents, skills, tips |
| [awattar/claude-code-best-practices](https://github.com/awattar/claude-code-best-practices) | Best practices for prompt design and safe automation |
| [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | CLI tool for configuring and monitoring Claude Code |

---

## Prompt Engineering Patterns

### Pattern 1: Structured Task Decomposition

Commands that break complex tasks into phases with explicit agent delegation:

```markdown
# Feature Development Workflow

## Phase 1: Analysis
Analyze $ARGUMENTS for scope, dependencies, and risks.
Delegate codebase exploration to the code-explorer agent.

## Phase 2: Architecture
Design the solution using the code-architect agent.
Produce a clear implementation plan.

## Phase 3: Implementation
Execute the plan with appropriate tooling.
Create tests alongside implementation.

## Phase 4: Review
Use the code-reviewer agent for quality assessment.
Address all identified issues.
```

### Pattern 2: Multi-Agent Orchestration in Commands

```markdown
# Full Code Review

Coordinate the following specialist agents in parallel:

1. **Architecture Review** - Evaluate patterns and structure
2. **Security Review** - Check for vulnerabilities
3. **Performance Review** - Identify bottlenecks
4. **Quality Review** - Code style and maintainability
5. **Test Coverage** - Verify test completeness

Synthesize findings into a unified report with severity ratings.
```

### Pattern 3: Context-Aware Conditional Logic

```markdown
# Smart Fix

Analyze the error described in $ARGUMENTS.

If the error is in a test file:
- Run the test to reproduce
- Check the implementation being tested
- Fix the root cause, not just the test

If the error is a type error:
- Check TypeScript strict mode settings
- Verify interface definitions
- Update types without breaking consumers

If the error is a runtime error:
- Add error boundary/handling
- Check for null/undefined edge cases
- Add defensive coding patterns
```

### Pattern 4: Iterative Improvement Loop

```markdown
# TDD Cycle

For $ARGUMENTS, execute:

1. RED: Write failing test that defines expected behavior
2. GREEN: Write minimum code to make test pass
3. REFACTOR: Improve code while keeping tests green
4. VERIFY: Run full test suite to check for regressions

Repeat until all requirements are satisfied.
Document each cycle's decisions and trade-offs.
```

### Pattern 5: $ARGUMENTS Handling

User input is passed as `$ARGUMENTS` and can be referenced throughout the command:

```markdown
# API Scaffold

Create REST API endpoints for $ARGUMENTS.

Steps:
1. Analyze $ARGUMENTS to determine required endpoints
2. Generate route handlers with proper HTTP methods
3. Add input validation and error handling
4. Create corresponding test files
5. Update API documentation
```

---

## Key Architectural Decisions and Patterns

### 1. Skills vs Commands vs Agents

| Dimension | Skills | Commands | Agents |
|-----------|--------|----------|--------|
| **Activation** | Automatic (context-based) | Manual (`/command-name`) | Delegated by orchestrator |
| **Scope** | Domain knowledge + workflows | Single task automation | Specialized sub-task |
| **Persistence** | Session-scoped | Invocation-scoped | Task-scoped |
| **Resources** | scripts/ + references/ + assets/ | Markdown only | System prompt only |
| **Distribution** | Plugin marketplace | File copy | Plugin marketplace |
| **Recommended for** | Recurring workflows, domain expertise | One-off tasks, user-triggered flows | Complex delegated analysis |

### 2. Directory Organization Strategies

**Flat** (simple projects):
```
.claude/
├── commands/
│   ├── review.md
│   ├── deploy.md
│   └── test.md
├── agents/
│   └── reviewer.md
└── skills/
    └── testing/SKILL.md
```

**Namespaced** (large projects):
```
.claude/
├── commands/
│   ├── dev/
│   │   ├── code-review.md
│   │   └── debug-error.md
│   ├── test/
│   │   ├── generate-tests.md
│   │   └── e2e-setup.md
│   └── deploy/
│       ├── prepare-release.md
│       └── rollback.md
├── agents/
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   └── test-engineer.md
└── skills/
    ├── testing-patterns/SKILL.md
    └── api-design/SKILL.md
```

### 3. Plugin vs Direct Installation

- **Plugin**: Proper packaging, versioning, marketplace distribution, hooks auto-loading
- **Direct**: Simple file copy to `.claude/`, faster iteration, no marketplace overhead
- **Recommendation**: Start with direct files for development, package as plugin for distribution

### 4. Global vs Project Scope

- **Global** (`~/.claude/`): Universal tools, personal preferences, cross-project utilities
- **Project** (`.claude/`): Team standards, project-specific workflows, committed to git
- **Security**: Global skills execute in ALL projects -- only add trusted skills

### 5. Hook Architecture Decisions

- Use **command hooks** for deterministic operations (format, lint, test)
- Use **prompt hooks** for AI-judgment operations (security review, content validation)
- Keep hooks **fast** (<5 seconds) to avoid blocking workflow
- Use **exit code 2** for blocking with feedback, not just silent failure

### 6. Multi-Agent Coordination

- **Official pattern**: Use Task tool to launch subagents with specific system prompts
- **Parallel execution**: Multiple Sonnet agents for independent review tasks
- **Sequential chains**: Plan -> Implement -> Review with different agents
- **Confidence scoring**: Filter false positives with scoring thresholds (code-review plugin)

---

## Comparison with SuperClaude

### How SuperClaude Aligns

| Ecosystem Pattern | SuperClaude Equivalent | Status |
|-------------------|----------------------|--------|
| SKILL.md format | `src/superclaude/skills/*/SKILL.md` | Implemented |
| Agent .md files | `src/superclaude/agents/*.md` | Implemented |
| Commands .md files | `src/superclaude/commands/*.md` | Implemented |
| `$ARGUMENTS` placeholder | Used in command files | Implemented |
| Plugin marketplace | `superclaude install` CLI | Custom approach |
| hooks.json | Not yet using official hook system | Gap |
| .claude-plugin/plugin.json | Not yet packaged as plugin | Gap |
| marketplace.json | Not yet a marketplace | Gap |
| Namespace prefixes | Uses `sc:` prefix (e.g., `/sc:adversarial`) | Partial |
| Progressive disclosure | SKILL.md + references/ pattern | Partial |
| Cross-tool compatibility | CLAUDE.md with @references | Implemented |

### SuperClaude Differentiators

1. **Persona system**: 11 specialized personas with auto-activation (unique in ecosystem)
2. **Wave orchestration**: Multi-stage command execution with compound intelligence
3. **Compliance tiers**: STRICT/STANDARD/LIGHT/EXEMPT classification
4. **MCP orchestration**: Coordinated multi-server usage with circuit breakers
5. **Token efficiency mode**: Symbol system with 30-50% reduction
6. **Pytest plugin**: Python-native testing integration with confidence checking
7. **PM Agent**: Self-improvement layer with reflexion patterns

### Opportunities from Ecosystem

1. **Adopt official plugin format**: Package SuperClaude as a `.claude-plugin` for marketplace distribution
2. **Implement hooks.json**: Leverage official hook system for quality gates
3. **Adopt prompt-based hooks**: Use AI-judgment hooks for security validation
4. **Cross-tool support**: Create AGENTS.md bridge for OpenCode/Codex compatibility
5. **Skill progressive disclosure**: Ensure SKILL.md files stay under 2000 words with references/
6. **Community marketplace**: Publish SuperClaude skills/agents as installable plugins
7. **GitHub Actions integration**: Automated PR review, scheduled audits (ChrisWiles pattern)
8. **Security scanning**: Integrate AgentShield-style config scanning

---

## Source Repository Index

### Official Anthropic
- [anthropics/skills](https://github.com/anthropics/skills) -- Official skills repository
- [anthropics/claude-code/plugins](https://github.com/anthropics/claude-code/tree/main/plugins) -- Official plugins
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) -- Official plugin marketplace
- [anthropics/claude-code/examples/settings](https://github.com/anthropics/claude-code/tree/main/examples/settings) -- Official settings examples

### System Prompts and Internals
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) -- All Claude Code system prompts (v2.1.50)

### Curated Lists
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) -- Definitive curated list
- [GiladShoham/awesome-claude-plugins](https://github.com/GiladShoham/awesome-claude-plugins) -- Plugin-focused list
- [hekmon8/awesome-claude-code-plugins](https://github.com/hekmon8/awesome-claude-code-plugins) -- Plugin discovery

### Comprehensive Guides
- [wesammustafa/Claude-Code-Everything-You-Need-to-Know](https://github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know) -- All-in-one guide
- [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) -- Best practices
- [awattar/claude-code-best-practices](https://github.com/awattar/claude-code-best-practices) -- Best practices and examples
- [zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide) -- Setup through tips

### Complete Configuration Examples
- [ronnycoding/.claude](https://github.com/ronnycoding/.claude) -- 83+ agents, 13 commands, 10 skills
- [feiskyer/claude-code-settings](https://github.com/feiskyer/claude-code-settings) -- Settings, agents, commands
- [Yugoge/claude-code-config](https://github.com/Yugoge/claude-code-config) -- 32 commands, 21 hooks, 14 agents
- [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) -- Full showcase with GitHub Actions
- [vincenthopf/My-Claude-Code](https://github.com/vincenthopf/My-Claude-Code) -- Daily essentials

### Command Collections
- [wshobson/commands](https://github.com/wshobson/commands) -- 57 production-ready commands
- [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite) -- 148+ commands, 54 agents
- [artemgetmann/claude-slash-commands](https://github.com/artemgetmann/claude-slash-commands) -- Commands with frontmatter
- [Comfy-Org/comfy-claude-prompt-library](https://github.com/Comfy-Org/comfy-claude-prompt-library) -- Team command library

### Agent Collections
- [wshobson/agents](https://github.com/wshobson/agents) -- 112 agents, 146 skills, 79 tools
- [darcyegb/ClaudeCodeAgents](https://github.com/darcyegb/ClaudeCodeAgents) -- QA agents
- [vizra-ai/claude-code-agents](https://github.com/vizra-ai/claude-code-agents) -- Agent collection
- [lelandg/ClaudeAgents](https://github.com/lelandg/ClaudeAgents) -- Agent documentation

### Skill Collections
- [alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) -- Skill creation toolkit
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) -- 26+ domain packages
- [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) -- Skills marketplace
- [Aaronontheweb/dotnet-skills](https://github.com/Aaronontheweb/dotnet-skills) -- .NET skills

### Multi-Agent Orchestration
- [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) -- Agent orchestration platform
- [steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp) -- Agent-in-agent MCP
- [grahama1970/claude-code-mcp-enhanced](https://github.com/grahama1970/claude-code-mcp-enhanced) -- Enhanced orchestration MCP
- [lgcyaxi/oh-my-claude](https://github.com/lgcyaxi/oh-my-claude) -- Multi-provider orchestration
- [bobmatnyc/claude-mpm](https://github.com/bobmatnyc/claude-mpm) -- Multi-Agent Project Manager
- [alfredolopez80/multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop) -- Memory-driven orchestration

### Hook Frameworks
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) -- Hook mastery guide
- [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) -- Agent monitoring hooks
- [carlrannaberg/claudekit](https://github.com/carlrannaberg/claudekit) -- CLI toolkit with hooks
- [karanb192/claude-code-hooks](https://github.com/karanb192/claude-code-hooks) -- Hook collection
- [decider/claude-hooks](https://github.com/decider/claude-hooks) -- Clean code hooks
- [johnlindquist/claude-hooks](https://github.com/johnlindquist/claude-hooks) -- TypeScript hooks

### Plugin Development
- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) -- Cross-tool plugin + marketplace
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) -- Full plugin with security scanning
- [ivan-magda/claude-code-plugin-template](https://github.com/ivan-magda/claude-code-plugin-template) -- Plugin template
- [mrlm-xyz/demo-claude-marketplace](https://github.com/mrlm-xyz/demo-claude-marketplace) -- Marketplace demo
- [claude-code-plugin-marketplaces](https://github.com/claude-code-plugin-marketplaces) -- Marketplace collection

### Prompt Engineering
- [ThamJiaHe/claude-prompt-engineering-guide](https://github.com/ThamJiaHe/claude-prompt-engineering-guide) -- Anthropic best practices
- [langgptai/awesome-claude-prompts](https://github.com/langgptai/awesome-claude-prompts) -- Prompt curation

### Security
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) -- AgentShield security scanner

### Cross-Tool Compatibility
- [shakacode/claude-code-commands-skills-agents](https://github.com/shakacode/claude-code-commands-skills-agents) -- Codex + Claude Code shared configs
- [alexanderop/claude-code-builder](https://github.com/alexanderop/claude-code-builder) -- CLAUDE.md builder patterns
- [iannuttall/claude-sessions](https://github.com/iannuttall/claude-sessions) -- Session tracking commands

### Subagent Frontmatter References
- [danielrosehill/96dd15d1313a9bd426f7f12f5375a092](https://gist.github.com/danielrosehill/96dd15d1313a9bd426f7f12f5375a092) -- Subagent frontmatter guide
- [ThomasRohde/af9d281a7a8c73e37448e1a94485eb0c](https://gist.github.com/ThomasRohde/af9d281a7a8c73e37448e1a94485eb0c) -- Agent creation expert prompt
- [kieranklaassen/d2b35569be2c7f1412c64861a219d51f](https://gist.github.com/kieranklaassen/d2b35569be2c7f1412c64861a219d51f) -- Multi-agent orchestration system
- [stevenringo/d7107d6096e7d0cf5716196d2880d5bb](https://gist.github.com/stevenringo/d7107d6096e7d0cf5716196d2880d5bb) -- About Claude Skills guide
- [alirezarezvani/a0f6e0a984d4a4adc4842bbe124c5935](https://gist.github.com/alirezarezvani/a0f6e0a984d4a4adc4842bbe124c5935) -- Ultimate extending guide

---

*Research conducted 2026-02-21 using WebSearch with GitHub domain filtering. All URLs verified at time of search.*
