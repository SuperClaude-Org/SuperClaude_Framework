# Claude Code Custom Agents, Skills & Slash Commands: General Web Research

**Research Date**: 2026-02-21
**Scope**: Blog posts, tutorials, official documentation, and community guides (excluding reddit.com and github.com)
**Purpose**: Best practices, techniques, and examples for creating custom agents, skills, and slash commands for Claude Code

---

## Table of Contents

1. [Official Documentation: Skills](#1-official-documentation-skills)
2. [Official Documentation: Custom Subagents](#2-official-documentation-custom-subagents)
3. [Official Documentation: Hooks](#3-official-documentation-hooks)
4. [Skill Authoring Best Practices (Anthropic)](#4-skill-authoring-best-practices-anthropic)
5. [CLAUDE.md Configuration Best Practices](#5-claudemd-configuration-best-practices)
6. [Prompt Engineering for Claude Code](#6-prompt-engineering-for-claude-code)
7. [Agent Orchestration Patterns](#7-agent-orchestration-patterns)
8. [MCP (Model Context Protocol) Integration](#8-mcp-model-context-protocol-integration)
9. [Plugin System Architecture](#9-plugin-system-architecture)
10. [Power User Tips & Advanced Techniques](#10-power-user-tips--advanced-techniques)
11. [Community Guides & Tutorials](#11-community-guides--tutorials)
12. [Complete Source Index](#12-complete-source-index)

---

## 1. Official Documentation: Skills

**Source**: [Extend Claude with Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)

### Key Insight
Skills are the unified extensibility mechanism in Claude Code, replacing and subsuming the older slash commands system. A skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown instructions. Claude discovers skills automatically and uses them when relevant, or users invoke them directly with `/skill-name`.

### SKILL.md Format

```yaml
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks "how does this work?"
---

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
3. **Walk through the code**: Explain step-by-step what happens
4. **Highlight a gotcha**: What's a common mistake or misconception?
```

### Complete Frontmatter Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name / slash command. Lowercase letters, numbers, hyphens only (max 64 chars). Defaults to directory name. |
| `description` | Recommended | What the skill does and when to use it. Claude uses this for auto-discovery. |
| `argument-hint` | No | Hint shown during autocomplete. Example: `[issue-number]` |
| `disable-model-invocation` | No | Set `true` to prevent Claude auto-loading. Manual `/name` only. Default: `false` |
| `user-invocable` | No | Set `false` to hide from `/` menu. Background knowledge only. Default: `true` |
| `allowed-tools` | No | Tools Claude can use without asking permission when skill is active |
| `model` | No | Model to use when skill is active |
| `context` | No | Set to `fork` to run in a forked subagent context |
| `agent` | No | Which subagent type when `context: fork` is set |
| `hooks` | No | Hooks scoped to this skill's lifecycle |

### Invocation Control Matrix

| Frontmatter | You can invoke | Claude can invoke | When loaded |
|-------------|---------------|-------------------|-------------|
| (default) | Yes | Yes | Description always in context; full content on invocation |
| `disable-model-invocation: true` | Yes | No | Description NOT in context; loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context; loads when invoked |

### Directory Structure

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples/
│   └── sample.md      # Example output
└── scripts/
    └── validate.sh    # Script Claude can execute
```

### Where Skills Live (Priority Order)

| Location | Path | Applies to |
|----------|------|-----------|
| Enterprise | Managed settings | All users in organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

### String Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking |
| `$ARGUMENTS[N]` | Specific argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session ID |

### Dynamic Context Injection

The `` !`command` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder:

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

### Running Skills in Subagents

With `context: fork`, the skill content becomes the prompt that drives the subagent. It runs in isolation without access to conversation history:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### Practical Applicability
- Skills are the primary extensibility mechanism for Claude Code
- The `context: fork` pattern is essential for isolating heavy operations
- Dynamic context injection (`!`command``) enables real-time data in skills
- The invocation control system allows fine-grained access control
- Supporting files enable progressive disclosure without context cost

---

## 2. Official Documentation: Custom Subagents

**Source**: [Create Custom Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)

### Key Insight
Subagents are specialized AI assistants that run in their own context window with custom system prompts, specific tool access, and independent permissions. They preserve context by keeping exploration and implementation out of the main conversation, and can be routed to cheaper/faster models.

### Agent File Format

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

### Complete Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tools the subagent can use. Inherits all tools if omitted |
| `disallowedTools` | No | Tools to deny from inherited or specified list |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit`. Defaults to `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum number of agentic turns |
| `skills` | No | Skills to preload into the subagent's context at startup |
| `mcpServers` | No | MCP servers available to this subagent |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | Set `true` to always run as background task |
| `isolation` | No | Set to `worktree` for isolated git worktree |

### Storage Locations (Priority Order)

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag | Current session | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All your projects | 3 |
| Plugin's `agents/` directory | Where plugin enabled | 4 (lowest) |

### Built-in Subagents

- **Explore**: Haiku model, read-only tools, codebase exploration
- **Plan**: Inherits model, read-only tools, plan mode research
- **General-purpose**: Inherits model, all tools, complex multi-step tasks

### Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Standard permission checking with prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny permission prompts |
| `bypassPermissions` | Skip all permission checks |
| `plan` | Plan mode (read-only exploration) |

### Persistent Memory

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

Memory scopes:
- `user`: `~/.claude/agent-memory/<name>/` - across all projects
- `project`: `.claude/agent-memory/<name>/` - project-specific, version-controllable
- `local`: `.claude/agent-memory-local/<name>/` - project-specific, not version-controlled

### Hooks in Agent Definitions

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

### Preloading Skills into Subagents

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

### Tool Scoping for Spawnable Subagents

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Task(worker, researcher), Read, Bash
---
```

### CLI-defined Subagents (Session-only)

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### Example Agents

**Code Reviewer** (read-only):
```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Good test coverage

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

**Debugger** (with edit access):
```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works
```

**Database Query Validator** (with PreToolUse hook):
```markdown
---
name: db-reader
description: Execute read-only database queries.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access.
Execute SELECT queries to answer questions about the data.
```

### Practical Applicability
- Subagents keep main context clean by isolating heavy operations
- The `model` field enables cost optimization (Haiku for research, Opus for reasoning)
- Persistent memory (`memory` field) enables cross-session learning
- Hooks in agent definitions enable domain-specific guardrails
- Background subagents (`background: true`) enable parallel work
- Git worktree isolation (`isolation: worktree`) prevents conflicts

---

## 3. Official Documentation: Hooks

**Source**: [Automate Workflows with Hooks - Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)

### Key Insight
Hooks are user-defined shell commands that execute at specific lifecycle points in Claude Code. They provide deterministic control over behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them.

### Hook Events

| Event | When it fires | Use case |
|-------|--------------|----------|
| `SessionStart` | Session begins | Environment setup, context loading |
| `SessionEnd` | Session ends | Cleanup, logging |
| `UserPromptSubmit` | Before Claude processes prompt | Validate/enrich prompts |
| `PreToolUse` | Before Claude performs action | Validation, blocking dangerous ops |
| `PostToolUse` | After Claude completes action | Formatting, linting, testing |
| `Notification` | Alerts | User notifications |
| `Stop` | End of response | Quality gates |
| `SubagentStart` | Subagent begins | Setup for specific agents |
| `SubagentStop` | Subagent completes | Cleanup |
| `PreCompact` | Before context compaction | Save state |

### Configuration Format

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-bash-firewall.sh"
          }
        ]
      }
    ]
  }
}
```

### Configuration Locations

- **User-wide**: `~/.claude/settings.json`
- **Project-specific**: `.claude/settings.json` (version-controllable)
- **Local overrides**: `.claude/settings.local.json` (not committed)

### Hook Types

- `"type": "command"` - Run a shell command (most common)
- `"type": "prompt"` - Single-turn LLM evaluation
- `"type": "agent"` - Multi-turn verification with tool access

### Exit Codes

- **0** = allow/ok
- **2** = block (PreToolUse only; message to stderr for Claude)
- Other non-zero = non-blocking error shown to user

### PreToolUse Input Modification (v2.0.10+)

PreToolUse hooks can modify tool inputs before execution, enabling transparent sandboxing, automatic security enforcement, and convention adherence.

### Practical Examples

**Block dangerous commands**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/pre-bash-firewall.sh" }
        ]
      }
    ]
  }
}
```

**Auto-format after edits**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/post-edit-quality.sh" }
        ]
      }
    ]
  }
}
```

**Gate PR creation on passing tests**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__github__create_pull_request",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/pre-pr-requires-tests.sh" }
        ]
      }
    ]
  }
}
```

### Practical Applicability
- Hooks enable deterministic guardrails that don't depend on LLM compliance
- PreToolUse hooks are ideal for security policies (blocking dangerous commands)
- PostToolUse hooks enforce code quality (auto-formatting, linting)
- Hook input modification enables transparent sandboxing
- Hooks in agent definitions scope guardrails to specific subagents

---

## 4. Skill Authoring Best Practices (Anthropic)

**Source**: [Skill Authoring Best Practices - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Key Insight
The most important Skill authoring principle is **progressive disclosure**: show just enough information to help agents decide what to do next, then reveal more details as needed. Claude is already very smart -- only add context Claude doesn't already have.

### Core Principles

#### 1. Concise is Key
The context window is a shared resource. Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?"

Good (approximately 50 tokens):
```markdown
## Extract PDF text
Use pdfplumber for text extraction:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

Bad (approximately 150 tokens): Don't explain what PDFs are or how libraries work.

#### 2. Set Appropriate Degrees of Freedom

- **High freedom** (text instructions): Multiple approaches valid, context-dependent
- **Medium freedom** (pseudocode/scripts with params): Preferred pattern exists, some variation ok
- **Low freedom** (specific scripts, no params): Operations fragile, consistency critical

Think of it as a robot on a path: narrow bridge with cliffs = low freedom; open field = high freedom.

#### 3. Test with All Models
- **Haiku**: Does the Skill provide enough guidance?
- **Sonnet**: Is the Skill clear and efficient?
- **Opus**: Does the Skill avoid over-explaining?

### Progressive Disclosure Patterns

**Pattern 1: High-level guide with references**
```markdown
# PDF Processing

## Quick start
[inline code example]

## Advanced features
**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
```

**Pattern 2: Domain-specific organization**
```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    └── product.md (usage analytics)
```

**Pattern 3: Conditional details**
```markdown
## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

### Key Anti-Patterns to Avoid

1. **Deeply nested references** -- keep references one level deep from SKILL.md
2. **Windows-style paths** -- always use forward slashes
3. **Too many options** -- provide a default, mention alternatives only when necessary
4. **Time-sensitive information** -- use "old patterns" sections instead
5. **Inconsistent terminology** -- choose one term and use it throughout
6. **Vague descriptions** -- be specific and include trigger keywords

### Naming Conventions

Prefer gerund form (verb + -ing) for clarity:
- Good: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`
- Acceptable: `pdf-processing`, `process-pdfs`
- Avoid: `helper`, `utils`, `tools`, `documents`

### Description Writing

Write in third person. Include both what the Skill does AND when to use it:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

### Workflow and Feedback Loop Patterns

**Checklist pattern for complex tasks**:
```markdown
Copy this checklist and track your progress:

Task Progress:
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```

**Feedback loop pattern** (run validator -> fix errors -> repeat):
```markdown
1. Make your edits
2. Validate immediately: `python scripts/validate.py`
3. If validation fails: fix issues, validate again
4. Only proceed when validation passes
```

### Evaluation-Driven Development

1. Identify gaps: Run Claude without a Skill, document failures
2. Create evaluations: Build three scenarios testing those gaps
3. Establish baseline: Measure performance without the Skill
4. Write minimal instructions: Just enough to pass evaluations
5. Iterate: Execute evaluations, compare, refine

### Iterative Development with Claude

Use "Claude A" (expert) to create/refine Skills that "Claude B" (agent) tests:
1. Complete a task without a Skill -- notice what context you repeatedly provide
2. Ask Claude A to create a Skill capturing the pattern
3. Review for conciseness
4. Test with Claude B on similar tasks
5. Observe behavior, bring insights back to Claude A
6. Iterate

### Checklist for Effective Skills

- [ ] Description specific with key trigger terms
- [ ] SKILL.md body under 500 lines
- [ ] Details in separate files with progressive disclosure
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Concrete examples
- [ ] File references one level deep
- [ ] Clear workflow steps with feedback loops
- [ ] At least three evaluations created
- [ ] Tested with multiple models

### Practical Applicability
- Progressive disclosure is the most impactful pattern for skill design
- The "concise is key" principle prevents context window bloat
- Evaluation-driven development ensures skills solve real problems
- The iterative Claude A / Claude B workflow is highly practical for refinement
- Checklist pattern enables complex multi-step workflows with tracking

---

## 5. CLAUDE.md Configuration Best Practices

**Sources**:
- [Writing a Good CLAUDE.md - HumanLayer Blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [CLAUDE.md Best Practices - Arize](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)

### Key Insight
CLAUDE.md is a high-leverage configuration point. Organize it around three pillars: WHAT (tech stack, project structure), WHY (purpose and function), and HOW (workflows, verification commands). Keep it concise -- frontier LLMs can follow approximately 150-200 instructions with reasonable consistency, and Claude Code's system prompt already contains approximately 50 instructions.

### Three Pillars

1. **WHAT**: Tech stack, project structure, codebase map (especially important in monorepos)
2. **WHY**: Purpose of the project, what different parts do
3. **HOW**: Verification steps, test commands, build tools (e.g., use bun instead of node)

### Nested CLAUDE.md Strategy

- Root-level `CLAUDE.md` for "always true" standards
- Folder-level CLAUDE.md files loaded conditionally when files in that folder are accessed
- Example: `tests/CLAUDE.md` for test conventions, `src/db/CLAUDE.md` for database rules

### Optimization Research (Arize)

Repository-specific CLAUDE.md optimization via Prompt Learning improved Claude Code test accuracy by 5.19%, with approximately 11% improvement on familiar codebases. All improvements came purely from refining instructions -- no model, tooling, or architecture changes.

### Template

```markdown
# CLAUDE.md

## Project Overview
[Brief description of what this project does]

## Tech Stack
[List key technologies, versions, and tools]

## Project Structure
[Map of key directories and their purposes]

## Development Workflow
[How to build, test, and verify changes]

## Conventions
[Coding standards, naming patterns, import styles]
```

### Practical Applicability
- Keep CLAUDE.md as concise as possible -- every instruction competes for attention
- Nested CLAUDE.md files prevent context bloat in monorepos
- Focus on what Claude can't infer from the codebase itself
- Include verification commands (test, lint, typecheck) -- these are high-value
- Repository-specific optimization yields measurable improvements

---

## 6. Prompt Engineering for Claude Code

**Sources**:
- [Prompting Best Practices - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Claude 4 Best Practices - Claude Docs](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Prompt Engineering Best Practices - DreamHost](https://www.dreamhost.com/blog/claude-prompt-engineering/)

### Key Insight
Claude responds best to clear, explicit instructions with context about WHY the instruction matters. The 4-block pattern (INSTRUCTIONS / CONTEXT / TASK / OUTPUT FORMAT) produces the most consistent results. Claude Opus models tend to overengineer -- add guidance to keep solutions minimal.

### Core Techniques

#### 1. Be Clear and Explicit
If you want "above and beyond" behavior, explicitly request it. Don't rely on inference from vague prompts.

#### 2. Provide Context and Motivation
Explain WHY behavior is important to help Claude deliver more targeted responses.

#### 3. Use Structured Prompts (4-Block Pattern)
```
INSTRUCTIONS: [role, constraints, style]
CONTEXT: [relevant background, files, decisions]
TASK: [specific action to perform]
OUTPUT FORMAT: [expected structure]
```

#### 4. Use Few-Shot Examples
Examples clarify subtle requirements better than descriptions. Claude 4.x pays very close attention to example details -- ensure they align with desired behaviors.

#### 5. Manage Opus Over-Engineering
Claude Opus tends to create extra files, add unnecessary abstractions, or build in flexibility that wasn't requested. Add specific guidance like "keep the solution minimal" or "don't add features beyond what's requested."

#### 6. Guide Risky Actions
Without guidance, Claude Opus may take irreversible actions (delete files, force-push). Add prompts like "confirm before taking potentially destructive actions."

#### 7. Context Window Management
If using agent harnesses that compact context, tell Claude about this so it can plan accordingly rather than trying to wrap up work as the limit approaches.

### Practical Applicability
- The 4-block pattern is directly applicable to skill and command design
- Few-shot examples in SKILL.md dramatically improve output quality
- Explicit minimal-scope instructions prevent scope creep in agents
- Context/motivation statements improve instruction adherence
- Managing Opus over-engineering is critical for production workflows

---

## 7. Agent Orchestration Patterns

**Sources**:
- [AI Agent Design Patterns - Microsoft Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Multi-Agent Patterns in ADK - Google Developers Blog](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/)
- [Choosing the Right Orchestration Pattern - Kore.ai](https://www.kore.ai/blog/choosing-the-right-orchestration-pattern-for-multi-agent-systems)
- [Conductors to Orchestrators - O'Reilly](https://www.oreilly.com/radar/conductors-to-orchestrators-the-future-of-agentic-coding/)
- [Agent Design Patterns - rlancemartin](https://rlancemartin.github.io/2026/01/09/agent_design/)
- [Claude Code Sub-Agent Best Practices - claudefa.st](https://claudefa.st/blog/guide/agents/sub-agent-best-practices)
- [Claude Code Multi-Agents Guide - TURION.AI](https://turion.ai/blog/claude-code-multi-agents-subagents-guide/)

### Key Patterns

#### 1. Sequential (Pipeline)
Each stage builds on the previous. Best for workflows with clear dependencies.
- Agent A completes task -> passes output to Agent B -> Agent B processes -> Agent C
- No AI orchestration needed -- just predefined flow logic

#### 2. Supervisor / Centralized Command
A central orchestrator receives the request, decomposes into subtasks, delegates to specialists, monitors progress, validates outputs, and synthesizes the final response.

#### 3. Adaptive / Decentralized Collaboration
Agents collaborate without a central coordinator. Best for dynamic, unpredictable workflows.

#### 4. Event-Driven Multi-Agent
Patterns include orchestrator-worker, hierarchical, blackboard, and market-based approaches.

### Claude Code Specific Patterns

#### Parallel vs. Sequential Dispatch

**Parallel dispatch** (all conditions must be met):
- 3+ unrelated tasks or independent domains
- No shared state between tasks
- Clear file boundaries with no overlap

**Sequential dispatch** (any condition triggers):
- Tasks have dependencies (B needs A's output)
- Shared files or state (merge conflict risk)
- Unclear scope

**Background dispatch**:
- Research or analysis tasks (not file modifications)
- Results not blocking current work

#### Cost Optimization
Run main session on Opus for complex reasoning, sub-agents on Sonnet for focused tasks. Both Tasks and subagents start with approximately 20,000 tokens of context loading.

#### Conductor vs. Orchestrator Paradigm
- **Conductor** mode: developer triggers each action and reviews output (interactive)
- **Orchestrator** mode: system manages multiple agents autonomously
- Both modes will coexist -- start with conductor, graduate to orchestrator

### Key Decision Criteria

- Is the workflow predictable? Sequential patterns win on cost and speed
- Does quality matter more than speed? Add reflection or human-in-the-loop
- Is the task genuinely complex? Consider multi-agent or planning patterns
- **Start simple. Add complexity only when you encounter clear limitations.**

### Practical Applicability
- The sequential pipeline pattern maps directly to multi-phase skills
- Supervisor pattern applies to orchestrator commands that coordinate subagents
- Parallel dispatch rules are directly applicable to `background: true` subagents
- Cost optimization via model routing is built into Claude Code's `model` field
- "Start simple" principle prevents premature complexity in agent design

---

## 8. MCP (Model Context Protocol) Integration

**Sources**:
- [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
- [MCP Best Practice Guide](https://mcp-best-practice.github.io/mcp-best-practice/)
- [Code Execution with MCP - Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [MCP Enterprise Adoption Guide](https://guptadeepak.com/the-complete-guide-to-model-context-protocol-mcp-enterprise-adoption-market-trends-and-implementation-strategies/)
- [MCP Auth Updates - Auth0](https://auth0.com/blog/mcp-specs-update-all-about-auth/)

### Key Insight
MCP is the universal standard for connecting AI agents to external tools, with 97M+ monthly SDK downloads and backing from Anthropic, OpenAI, Google, and Microsoft. It uses JSON-RPC 2.0 transport and follows LSP-inspired message flow patterns.

### Architecture

- **MCP Client**: The LLM that initiates calls
- **MCP Server**: External tool wrapped in MCP-compatible format
- **Session ID**: Tracks context across interactions
- **Registry**: Holds and manages trusted MCP servers

### Key Updates (2025)

1. **Streamable HTTP** (March 2025): Replaced SSE with scalable bi-directional model. Supports cloud deployment (AWS Lambda) without long-lived connections.
2. **Tool Output Schemas** (June 2025): Client/LLM knows tool output shapes ahead of time, improving token efficiency.
3. **OAuth 2.0 Integration**: MCP servers classified as OAuth Resource Servers with RFC 8707 Resource Indicators.

### Best Practices

#### Efficient Tool Usage
Code execution with MCP enables agents to use context more efficiently by:
- Loading tools on demand
- Filtering data before it reaches the model
- Executing complex logic in a single step
- Writing code to call tools instead of direct tool calls (scales better)

#### Production Deployment
- Emphasize simple, observable, secure designs that scale
- Build robust consent and authorization flows
- Implement appropriate access controls and data protections
- Follow security best practices

#### In Claude Code Subagents

```yaml
---
name: api-analyst
description: Analyzes API endpoints using external tools
mcpServers:
  - slack
  - github
---
```

MCP servers can be referenced by name (already configured) or defined inline in subagent frontmatter.

### Practical Applicability
- MCP servers extend subagent capabilities beyond built-in tools
- The `mcpServers` frontmatter field enables per-agent MCP scoping
- Tool Output Schemas improve token efficiency for MCP-heavy workflows
- Streamable HTTP enables serverless MCP deployment
- OAuth integration is critical for enterprise MCP adoption

---

## 9. Plugin System Architecture

**Sources**:
- [Discover and Install Plugins - Claude Code Docs](https://code.claude.com/docs/en/discover-plugins)
- [How to Build Claude Code Plugins - DataCamp](https://www.datacamp.com/tutorial/how-to-build-claude-code-plugins)
- [Claude Code Plugins Guide - Morph](https://www.morphllm.com/claude-code-plugins)
- [Claude Code Plugins Blog - Anthropic](https://claude.com/blog/claude-code-plugins)
- [Claude Plugins - Anthropic](https://claude.com/plugins)

### Key Insight
Plugins are a packaging format that bundles Claude Code extensions for easy sharing and installation. The ecosystem grew from zero to 9,000+ plugins in under a year. Plugins use a simple directory-based architecture with no build step, compilation, or registry approval.

### Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json       # Manifest (required)
├── commands/              # Slash commands
├── skills/                # Skills
├── agents/                # Subagents
└── hooks/                 # Hook configurations
```

The `name` field in `plugin.json` becomes the namespace prefix: a plugin named `my-tool` has commands like `/my-tool:review`.

### What Plugins Can Contain

- **Slash commands**: Custom shortcuts
- **Subagents**: Purpose-built agents
- **MCP servers**: External tool connections
- **Hooks**: Behavior customizations
- **Skills**: Auto-discovered workflows

### Distribution

- **Marketplaces**: GitHub repositories with curated plugin collections
- **Official Marketplace**: `claude-plugins-official` (auto-available at startup)
- **CLI**: `/plugin marketplace add user-or-org/repo-name`

### Most Popular Plugins (by installs)
1. Frontend Design (96K)
2. Context7 (71K)
3. Ralph Loop (57K)
4. Code Review (50K)
5. Playwright (28K)
6. Security Guidance (25K)

### Practical Applicability
- Plugins are the primary distribution mechanism for Claude Code extensions
- The namespace system prevents conflicts between plugins
- Marketplace system enables easy discovery and installation
- No build step means rapid development and iteration
- All component types (skills, agents, hooks, MCP) can be bundled together

---

## 10. Power User Tips & Advanced Techniques

**Sources**:
- [20+ Claude Code CLI Tricks - mlearning.substack.com](https://mlearning.substack.com/p/20-most-important-claude-code-tricks-2025-2026-cli-january-update)
- [Claude Code Best Practices for Power Users - sidetool.co](https://www.sidetool.co/post/claude-code-best-practices-tips-power-users-2025/)
- [32 Claude Code Tips - agenticcoding.substack.com](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to)
- [50 Claude Code Tips - Geeky Gadgets](https://www.geeky-gadgets.com/claude-code-tips-2/)
- [10 Claude Code Productivity Workflows - f22labs.com](https://www.f22labs.com/blogs/10-claude-code-productivity-tips-for-every-developer/)
- [How I Use Claude Code - builder.io](https://www.builder.io/blog/claude-code)
- [Advanced Claude Code Workflows - sidetool.co](https://www.sidetool.co/post/advanced-claude-code-workflows-tips-and-tricks-for-power-users/)

### Context Management Techniques

| Technique | Description |
|-----------|-------------|
| `/clear` | Reset context between tasks to reduce token waste |
| `/compact` | Condense lengthy sessions without losing critical info |
| `/context` | Visualize and audit current context window usage |
| `/resume` | Recover lost instances |
| `@file` | Reference specific files for targeted context |
| Escape key | Instantly interrupt and redirect Claude's focus |
| Escape x2 | Browse all previous messages |

### Workflow Patterns

- **Plan Mode (Shift+Tab)**: Force Claude to think like a Senior Architect before coding
- **Parallel Development**: Run multiple Claude instances on separate parts of codebase
- **Git Worktrees**: Simultaneous edits without branch conflicts
- **Claude-first Workflow**: Use Claude as primary interface, review code changes afterward
- **Background Agents (Ctrl+B)**: Send running agents to background

### Terminal Tips

- Use Escape (not Ctrl+C) to stop the agent
- Hold Shift while dragging files to reference them
- Use Control+V (not Command+V) to paste images
- Run `/terminal-setup` for better multiline entry

### Model Strategy

- Default to Opus for complex reasoning
- Switch to Sonnet for focused, well-scoped tasks
- Use Haiku subagents for research and exploration
- Auto-switch may occur after 50% usage for cost efficiency

### GitHub Integration

```yaml
# claude-code-review.yml
direct_prompt: |
  Please review this pull request and look for bugs and security issues.
  Only report on bugs and potential vulnerabilities you find. Be concise.
```

### Practical Applicability
- Context management commands are essential for long-running sessions
- Plan Mode (Shift+Tab) should precede complex implementations
- Parallel development with Git Worktrees enables multi-agent workflows
- Model routing between Opus/Sonnet/Haiku optimizes cost and speed
- The Escape key for interruption is a critical workflow tool

---

## 11. Community Guides & Tutorials

**Sources**:
- [Claude Code Customization Guide - alexop.dev](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)
- [Mastering Agentic Coding in Claude - Medium (LM Po)](https://medium.com/@lmpo/mastering-agentic-coding-in-claude-a-guide-to-skills-sub-agents-slash-commands-and-mcp-servers-5c58e03d4a35)
- [Claude Code Custom Agents Guide - claudefa.st](https://claudefa.st/blog/guide/agents/custom-agents)
- [Complete Guide to Claude Code - siddharthbharath.com](https://www.siddharthbharath.com/claude-code-the-complete-guide/)
- [Slash Commands Guide - eesel.ai](https://www.eesel.ai/blog/slash-commands-claude-code)
- [Claude Code Features Guide - producttalk.org](https://www.producttalk.org/how-to-use-claude-code-features/)
- [Claude Code Agent Teams Guide - claudefa.st](https://claudefa.st/blog/guide/agents/agent-teams)
- [Claude Sub-Agents Delegation - theaistack.dev](https://www.theaistack.dev/p/orchestrating-claude-sub-agents)
- [Task Tool vs Subagents - amitkoth.com](https://amitkoth.com/claude-code-task-tool-vs-subagents/)
- [Claude Skills Deep Dive - leehanchung.github.io](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Claude Code Skills Analysis - mikhail.io](https://mikhail.io/2025/10/claude-code-skills/)
- [How to Create Claude Code Skills - websearchapi.ai](https://websearchapi.ai/blog/how-to-create-claude-code-skills)
- [Claude Code Hooks Guide - DataCamp](https://www.datacamp.com/tutorial/claude-code-hooks)
- [Claude Code Hooks - GitButler](https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks)
- [Claude Code Hook Examples - Steve Kinney](https://stevekinney.com/courses/ai-development/claude-code-hook-examples)
- [CLI Agent Orchestrator - AWS Open Source Blog](https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse/)

### Decision Matrix (from alexop.dev)

| Use Case | Mechanism | When to Choose |
|----------|-----------|---------------|
| Baseline team conventions | CLAUDE.md | Always-on project rules |
| Explicit, repeatable workflows | Slash commands / Skills | Manual triggers via `/name` |
| Heavy reading/searching | Subagents | Isolate from main context |
| Auto-applied capabilities | Skills with `user-invocable: false` | Claude decides when to apply |

### Doc Freshness Pattern

A recurring community pattern:
1. Fetch a docs index (e.g., `llms.txt` endpoint)
2. Fetch only the pages needed for the current task
3. Answer/implement based on those sources

This works across CLAUDE.md, commands, skills, and subagents.

### Subagent Best Practices (from community)

- Descriptions control delegation -- if vague, the main agent keeps work for itself
- Include "use proactively" in descriptions to encourage auto-delegation
- Subagents start with approximately 20,000 tokens of context loading
- Parallelism caps at 10 concurrent operations
- Over-parallelizing wastes tokens; group related micro-tasks
- Under-parallelizing runs independent analyses sequentially -- look for domain independence

### Skills vs. Subagents (from community analysis)

- **Skills**: Run in main thread context (or forked), reusable prompts, auto-discovered
- **Subagents**: Own context window, isolated execution, distilled results returned
- **Skills in subagents**: Full content injected at startup via `skills` field
- **Skills with `context: fork`**: Skill drives the subagent task

### Role-Based Agent Pipeline (from community)

Give agents roles and chain them with hooks:
1. **PM Agent**: Asks questions, defines requirements
2. **Architect Agent**: Validates design, reviews approach
3. **Implementer/Tester Agent**: Builds and tests
4. **QA Agent**: Verifies output

### Practical Applicability
- The decision matrix provides clear guidance for mechanism selection
- The doc freshness pattern is universally applicable
- Role-based pipelines enable multi-phase command workflows
- Community consensus: start simple, measure, then optimize bottlenecks
- Subagent context isolation is the primary benefit for complex workflows

---

## 12. Complete Source Index

### Official Anthropic Documentation
1. [Extend Claude with Skills](https://code.claude.com/docs/en/skills) - Primary skills documentation
2. [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents) - Primary subagents documentation
3. [Automate Workflows with Hooks](https://code.claude.com/docs/en/hooks-guide) - Primary hooks documentation
4. [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Official best practices
5. [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - Agent Skills standard
6. [Introducing Agent Skills](https://www.anthropic.com/news/skills) - Announcement blog
7. [Equipping Agents for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Engineering blog
8. [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) - MCP engineering blog
9. [Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - Prompt engineering
10. [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Model-specific tips
11. [Agent SDK Overview](https://docs.anthropic.com/en/docs/claude-code/sdk) - SDK documentation
12. [Slash Commands in the SDK](https://platform.claude.com/docs/en/agent-sdk/slash-commands) - SDK slash commands
13. [Discover and Install Plugins](https://code.claude.com/docs/en/discover-plugins) - Plugin marketplace
14. [Claude Code Plugins Blog](https://claude.com/blog/claude-code-plugins) - Plugin announcement
15. [Claude Plugins Directory](https://claude.com/plugins) - Official plugin directory

### MCP Documentation
16. [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25) - Official spec
17. [MCP Best Practices Guide](https://modelcontextprotocol.info/docs/best-practices/) - Community best practices
18. [MCP Best Practice (Linux Foundation)](https://mcp-best-practice.github.io/mcp-best-practice/) - Production guidance
19. [MCP Auth Updates](https://auth0.com/blog/mcp-specs-update-all-about-auth/) - Security/auth updates
20. [MCP Enterprise Adoption Guide](https://guptadeepak.com/the-complete-guide-to-model-context-protocol-mcp-enterprise-adoption-market-trends-and-implementation-strategies/) - Enterprise guide

### Blog Posts & Tutorials
21. [Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) - alexop.dev
22. [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) - HumanLayer
23. [CLAUDE.md Optimization with Prompt Learning](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/) - Arize
24. [How I Use Claude Code](https://www.builder.io/blog/claude-code) - builder.io
25. [Mastering Agentic Coding in Claude](https://medium.com/@lmpo/mastering-agentic-coding-in-claude-a-guide-to-skills-sub-agents-slash-commands-and-mcp-servers-5c58e03d4a35) - Medium
26. [Claude Code Custom Agents Guide](https://claudefa.st/blog/guide/agents/custom-agents) - claudefa.st
27. [Sub-Agent Best Practices](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) - claudefa.st
28. [Agent Teams Guide](https://claudefa.st/blog/guide/agents/agent-teams) - claudefa.st
29. [Complete Guide to Claude Code](https://www.siddharthbharath.com/claude-code-the-complete-guide/) - Sid Bharath
30. [Slash Commands Guide](https://www.eesel.ai/blog/slash-commands-claude-code) - eesel.ai
31. [Claude Code Features Guide](https://www.producttalk.org/how-to-use-claude-code-features/) - ProductTalk
32. [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) - Lee Han Chung
33. [Inside Claude Code Skills](https://mikhail.io/2025/10/claude-code-skills/) - Mikhail Shilkov
34. [How to Create Claude Code Skills](https://websearchapi.ai/blog/how-to-create-claude-code-skills) - WebSearchAPI
35. [Claude Code Hooks Guide](https://www.datacamp.com/tutorial/claude-code-hooks) - DataCamp
36. [Claude Code Hooks Automation](https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks) - GitButler
37. [Claude Code Hook Examples](https://stevekinney.com/courses/ai-development/claude-code-hook-examples) - Steve Kinney
38. [How to Build Claude Code Plugins](https://www.datacamp.com/tutorial/how-to-build-claude-code-plugins) - DataCamp
39. [Claude Code Plugins Guide](https://www.morphllm.com/claude-code-plugins) - Morph

### Power User & Tips Collections
40. [20+ Claude Code CLI Tricks](https://mlearning.substack.com/p/20-most-important-claude-code-tricks-2025-2026-cli-january-update) - mlearning
41. [Claude Code Best Practices for Power Users](https://www.sidetool.co/post/claude-code-best-practices-tips-power-users-2025/) - SideTool
42. [32 Claude Code Tips](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to) - Agentic Coding
43. [50 Claude Code Tips](https://www.geeky-gadgets.com/claude-code-tips-2/) - Geeky Gadgets
44. [10 Claude Code Productivity Workflows](https://www.f22labs.com/blogs/10-claude-code-productivity-tips-for-every-developer/) - F22 Labs
45. [Advanced Claude Code Workflows](https://www.sidetool.co/post/advanced-claude-code-workflows-tips-and-tricks-for-power-users/) - SideTool
46. [Beyond the Chatbox: Mastering Claude Code 2026](https://medium.com/@vinayanand2/beyond-the-chatbox-a-non-technical-guide-to-mastering-claude-code-in-2026-8f7acd3a6e7d) - Medium

### Orchestration & Architecture
47. [AI Agent Design Patterns - Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) - Microsoft
48. [Multi-Agent Patterns in ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - Google
49. [Choosing Orchestration Patterns](https://www.kore.ai/blog/choosing-the-right-orchestration-pattern-for-multi-agent-systems) - Kore.ai
50. [Conductors to Orchestrators](https://www.oreilly.com/radar/conductors-to-orchestrators-the-future-of-agentic-coding/) - O'Reilly
51. [Agent Design Patterns](https://rlancemartin.github.io/2026/01/09/agent_design/) - rlancemartin
52. [Multi-Agent Orchestration for Claude Code](https://shipyard.build/blog/claude-code-multi-agent/) - Shipyard
53. [Claude Code Multi-Agents Guide](https://turion.ai/blog/claude-code-multi-agents-subagents-guide/) - TURION.AI
54. [Claude Sub-Agents Delegation](https://www.theaistack.dev/p/orchestrating-claude-sub-agents) - The AI Stack
55. [Task Tool vs Subagents](https://amitkoth.com/claude-code-task-tool-vs-subagents/) - Amit Kothari
56. [CLI Agent Orchestrator](https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse/) - AWS
57. [Claude Prompt Engineering Best Practices 2026](https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026) - Prompt Builder
58. [Claude Prompt Engineering Tested](https://www.dreamhost.com/blog/claude-prompt-engineering/) - DreamHost

### Tutorials & Courses
59. [Build a YouTube Research Agent](https://creatoreconomy.so/p/claude-code-tutorial-build-a-youtube-research-agent-in-15-min) - Creator Economy
60. [Create Your First Claude Code Skill](https://egghead.io/create-your-first-claude-code-skill~sds93) - egghead.io
61. [How to Build Claude Skills: Lesson Plan](https://www.codecademy.com/article/how-to-build-claude-skills) - Codecademy
62. [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en) - Anthropic Resources (PDF)
63. [Claude Code Hooks Automation Guide](https://www.gend.co/blog/configure-claude-code-hooks-automation) - Gend
64. [Claude Code Hooks Development Guide](https://claude-world.com/articles/hooks-development-guide/) - Claude World
65. [Hooks Documentation Understanding](https://blog.promptlayer.com/understanding-claude-code-hooks-documentation/) - PromptLayer
66. [Claude Code Hooks How-To](https://apidog.com/blog/claude-code-hooks/) - APIDog

---

*Research compiled from 66 sources across official documentation, engineering blogs, community tutorials, and industry analysis. All URLs verified as of 2026-02-21.*
