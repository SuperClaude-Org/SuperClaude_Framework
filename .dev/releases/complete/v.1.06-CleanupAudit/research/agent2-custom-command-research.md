# Claude Code Custom Commands & Skills: Complete Research Report

**Date**: 2026-02-19
**Purpose**: Comprehensive capability analysis for building a multi-pass repository audit command within the SuperClaude framework.
**Research Sources**: Official Anthropic documentation (code.claude.com), community guides, and framework analysis.

---

## Table of Contents

- [Part 1: Complete Capability Catalogue](#part-1-complete-capability-catalogue)
- [Part 2: Ranked Feature Utility for Repository Audit](#part-2-ranked-feature-utility-for-repository-audit)
- [Part 3: Commands vs Skills Analysis](#part-3-commands-vs-skills-analysis)
- [Part 4: Advanced Orchestration Patterns](#part-4-advanced-orchestration-patterns)

---

# Part 1: Complete Capability Catalogue

## 1.1 File Format & Structure

### Commands (Legacy Format)
- **Location**: `.claude/commands/<name>.md` (project) or `~/.claude/commands/<name>.md` (personal)
- **Format**: Single markdown file with optional YAML frontmatter
- **Naming**: Filename becomes the slash command name (e.g., `review.md` creates `/review`)
- **Encoding**: UTF-8 markdown

### Skills (Current Format - Recommended)
- **Location**: `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (personal)
- **Format**: Directory containing `SKILL.md` (required) plus optional supporting files
- **Naming**: Directory name or `name` frontmatter field becomes the slash command
- **Max name length**: 64 characters (lowercase letters, numbers, hyphens only)

### Merging Note
Custom slash commands have been merged into skills. A file at `.claude/commands/review.md` and a skill at `.claude/skills/review/SKILL.md` both create `/review` and work identically. Existing `.claude/commands/` files continue to work. If both exist with the same name, the skill takes precedence.

### Priority Hierarchy
| Location | Priority | Scope |
|----------|----------|-------|
| Enterprise (managed settings) | Highest | All org users |
| Personal (`~/.claude/skills/`) | High | All your projects |
| Project (`.claude/skills/`) | Medium | This project only |
| Plugin (`<plugin>/skills/`) | Lowest | Where plugin is enabled |

## 1.2 Frontmatter Reference (Complete)

All fields are optional. Only `description` is recommended.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | directory name | Display name; becomes `/slash-command` |
| `description` | string | first paragraph | What the skill does; Claude uses this for auto-invocation decisions |
| `argument-hint` | string | none | Hint shown during autocomplete (e.g., `[issue-number]`) |
| `disable-model-invocation` | boolean | `false` | If `true`, only user can invoke (prevents auto-loading by Claude) |
| `user-invocable` | boolean | `true` | If `false`, hidden from `/` menu (only Claude can invoke) |
| `allowed-tools` | string (CSV) | all tools | Tools Claude can use without asking permission |
| `model` | string | inherit | Model to use: `sonnet`, `opus`, `haiku`, or `inherit` |
| `context` | string | inline | Set to `fork` to run in isolated subagent context |
| `agent` | string | `general-purpose` | Subagent type when `context: fork` (e.g., `Explore`, `Plan`, custom) |
| `hooks` | object | none | Lifecycle hooks scoped to this skill |

### Invocation Control Matrix
| Frontmatter | User can invoke | Claude can invoke | Context loading |
|-------------|----------------|-------------------|-----------------|
| (default) | Yes | Yes | Description always in context; full content loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description NOT in context; loads only when user invokes |
| `user-invocable: false` | No | Yes | Description always in context; loads when Claude invokes |

## 1.3 String Substitution Variables

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking. If not present in content, appended as `ARGUMENTS: <value>` |
| `$ARGUMENTS[N]` | Specific argument by 0-based index (e.g., `$ARGUMENTS[0]` for first) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`, `$2`) |
| `${CLAUDE_SESSION_ID}` | Current session ID (useful for logging and file naming) |

**Behavior**: When a skill is invoked with arguments but doesn't include `$ARGUMENTS`, Claude Code automatically appends `ARGUMENTS: <your input>` to the end of the skill content.

## 1.4 Supporting Files

Skills can include multiple files in their directory:

```
my-skill/
├── SKILL.md           # Main instructions (required, keep under 500 lines)
├── template.md        # Template for Claude to fill in
├── reference.md       # Detailed API docs (loaded when needed)
├── examples/
│   └── sample.md      # Example output showing expected format
└── scripts/
    └── validate.sh    # Script Claude can execute
```

Supporting files are referenced from `SKILL.md` via markdown links. They are loaded on-demand, not at startup, reducing context consumption.

## 1.5 Shell Command Preprocessing

The `!` backtick syntax runs shell commands BEFORE the skill content is sent to Claude:

```markdown
## Context
- Current branch: !`git branch --show-current`
- Changed files: !`git diff --name-only`
- File count: !`find . -name "*.py" | wc -l`
```

**Execution flow**:
1. Each `` !`command` `` executes immediately (before Claude sees anything)
2. The command output replaces the placeholder in the skill content
3. Claude receives the fully-rendered prompt with actual data

This is preprocessing -- Claude never sees the commands, only the output.

## 1.6 Tool Access

### Available Tools (Complete List)
When a skill is active, Claude has access to these internal tools (restricted by `allowed-tools`):

**Read-Only Tools**:
- `Read` - Read file contents
- `Grep` - Search file contents with regex
- `Glob` - Find files by pattern

**Write Tools**:
- `Write` - Create/overwrite files
- `Edit` - Modify existing files (search-and-replace)
- `MultiEdit` - Batch edit multiple files

**Execution Tools**:
- `Bash` - Execute shell commands (supports `Bash(pattern)` for restricting to specific commands)
- `Task` - Spawn subagents (supports `Task(agent_type)` for restricting agent types)

**Orchestration Tools**:
- `TodoWrite` - Create/update task lists for progress tracking
- `TodoRead` - Read current task list

**Communication Tools**:
- `Skill` - Invoke other skills

**MCP Tools**:
- Any tools provided by configured MCP servers (e.g., Sequential Thinking, Context7, Serena)

### Tool Restriction Patterns
```yaml
# Read-only mode
allowed-tools: Read, Grep, Glob

# Read + shell (restricted)
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(npm test *)

# Full agent spawning
allowed-tools: Read, Grep, Glob, Bash, Task

# Specific agent types only
allowed-tools: Read, Task(researcher, reviewer)
```

## 1.7 Subagent System (Task Tool)

### Built-in Subagent Types

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| **Explore** | Haiku (fast) | Read-only (no Write/Edit) | File discovery, code search, codebase exploration |
| **Plan** | Inherit | Read-only (no Write/Edit) | Codebase research for planning mode |
| **general-purpose** | Inherit | All tools | Complex research, multi-step operations, code modifications |
| **Bash** | Inherit | Bash | Running terminal commands in separate context |

### Custom Subagents

Defined as markdown files in `.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`.

**Frontmatter fields**:
| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tools available (inherits all if omitted) |
| `disallowedTools` | No | Tools to deny |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | Maximum agentic turns before stopping |
| `skills` | No | Skills to preload into subagent context |
| `mcpServers` | No | MCP servers available to this subagent |
| `hooks` | No | Lifecycle hooks |
| `memory` | No | Persistent memory scope: `user`, `project`, `local` |

### Key Subagent Behaviors

1. **Context Isolation**: Each subagent runs in its own context window with a custom system prompt. It does NOT inherit the parent's conversation history.
2. **CLAUDE.md Loading**: Subagents DO load CLAUDE.md from the working directory.
3. **No Nested Spawning**: Subagents CANNOT spawn other subagents. The Task tool is not available within subagents.
4. **Foreground vs Background**: Subagents can run in foreground (blocking) or background (concurrent). Background subagents auto-deny unapproved permissions.
5. **Resume Capability**: Subagents can be resumed with their full conversation history intact.
6. **Auto-Compaction**: Subagents support automatic compaction at ~95% capacity.
7. **Parallel Execution**: Up to ~7-10 concurrent subagents (practical limit).
8. **Token Overhead**: Each Task invocation has ~20K token overhead.

### Subagent Communication
- Subagents return results to the parent as a summary
- No direct inter-subagent communication (use Agent Teams for that)
- Results from parallel subagents are synthesized by the parent

## 1.8 Agent Teams (Experimental)

Agent Teams are a separate, more advanced coordination mechanism.

**Key differences from subagents**:
- Each teammate is a full Claude Code session
- Teammates can message each other directly
- Shared task list for coordination
- Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

**For our use case**: Agent Teams are overkill for a repository audit command. Subagents are the right fit -- we need parallel workers that report back to a coordinator, not inter-agent debate.

## 1.9 MCP Server Integration

### From Skills/Commands
- MCP tools are available during skill execution if the MCP server is configured in the project's `.mcp.json` or user's `~/.claude.json`
- Skills cannot directly specify which MCP servers to activate in frontmatter
- However, custom subagents CAN specify `mcpServers` in their frontmatter
- MCP tools are NOT available in background subagents

### From Custom Subagents
```yaml
---
name: my-agent
mcpServers:
  - slack                    # Reference existing configured server
  - my-server:               # Inline definition
      command: node
      args: ["server.js"]
---
```

### MCP Tool Search (Lazy Loading)
Claude Code supports lazy loading for MCP servers, reducing context usage by up to 95%. Tools are loaded only when needed.

## 1.10 Progress Tracking

### TodoWrite/TodoRead
- Built-in task list management within a session
- States: `pending`, `in_progress`, `completed`, `blocked`
- Capacity: 3-20 tasks per session
- Available via the `TodoWrite` tool

### Pattern for Long Operations
```markdown
## Progress Tracking

For each batch, update the task list:
1. Create tasks with TodoWrite before starting
2. Update status as each batch completes
3. Mark blocked tasks when dependencies exist
4. Complete tasks with evidence of results
```

## 1.11 Extended Thinking

Including the word "ultrathink" anywhere in skill content enables extended thinking mode. This provides deeper reasoning for complex analysis tasks.

## 1.12 Context Budget

Skill descriptions are loaded into context at startup. The budget scales dynamically at 2% of the context window, with a fallback of 16,000 characters. Override with `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable.

Full skill content only loads when invoked -- descriptions are the only persistent context cost.

## 1.13 Hooks System

Skills can define lifecycle hooks:

| Event | When it fires |
|-------|---------------|
| `PreToolUse` | Before a tool is used |
| `PostToolUse` | After a tool is used |
| `Stop` | When the skill/subagent finishes |

Hooks run shell commands and can block operations (exit code 2), allow operations (exit code 0), or fail silently.

## 1.14 Persistent Memory (Subagents Only)

Subagents can have persistent memory across sessions:

| Scope | Location | Use case |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project learning |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, shareable |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, private |

When enabled, the subagent's MEMORY.md (first 200 lines) is injected into its system prompt.

## 1.15 Automatic Discovery

- Skills in nested `.claude/skills/` directories are automatically discovered (monorepo support)
- Skills from `--add-dir` directories are loaded automatically with live change detection
- No restart needed when editing skills during a session

---

# Part 2: Ranked Feature Utility for Repository Audit

Features ranked from most to least useful for our specific use case: a multi-pass repository cleanup audit command that spawns parallel agents to audit batches of files.

## Tier 1: Critical (Must Use)

### 1. Subagent Spawning via Task Tool
**Utility**: 10/10
**Rationale**: The core mechanism for our multi-pass audit. Each audit batch spawns a subagent that independently analyzes a subset of files and returns structured findings. The Task tool enables parallel execution of up to ~7-10 concurrent agents, which is essential for handling 1000+ file repos in reasonable time.

**Application**:
- Pass 1 (Surface Scan): Spawn N parallel Explore agents with read-only tools
- Pass 2 (Structural Audit): Spawn general-purpose agents for deeper analysis
- Pass 3 (Cross-Cutting Sweep): Spawn agents per cross-cutting concern

### 2. `allowed-tools` Restriction
**Utility**: 10/10
**Rationale**: Enforces read-only behavior for audit operations. Setting `allowed-tools: Read, Grep, Glob` prevents accidental modifications during analysis passes. Essential for safety in a cleanup audit -- you want to REPORT issues, not fix them during audit.

**Application**:
```yaml
allowed-tools: Read, Grep, Glob, Bash(wc *), Bash(git log *), TodoWrite, Task
```

### 3. $ARGUMENTS String Substitution
**Utility**: 10/10
**Rationale**: Allows the command to accept target paths, configuration flags, and scope parameters. `$0` for target directory, `$1` for pass selection, etc.

**Application**:
```
/sc:repo-audit src/ --pass surface --batch-size 50
```

### 4. TodoWrite Progress Tracking
**Utility**: 9/10
**Rationale**: Essential for tracking progress across a long-running audit of 1000+ files. Each batch becomes a tracked task with status updates. Provides visibility into completion state and blocked items.

**Application**: Create tasks for each batch, update as subagents complete, aggregate final status.

### 5. Supporting Files in Skill Directory
**Utility**: 9/10
**Rationale**: The audit command needs templates for report output, rule definitions for each audit pass, and example findings formats. These belong in supporting files, not crammed into SKILL.md.

**Application**:
```
sc-repo-audit/
├── SKILL.md                    # Main orchestration logic
├── templates/
│   ├── finding-template.md     # Template for individual findings
│   ├── batch-report.md         # Template for batch summaries
│   └── final-report.md         # Template for consolidated report
├── rules/
│   ├── surface-scan-rules.md   # Pass 1 audit criteria
│   ├── structural-rules.md     # Pass 2 audit criteria
│   └── cross-cutting-rules.md  # Pass 3 audit criteria
└── scripts/
    └── aggregate-findings.py   # Script to merge batch results
```

### 6. Shell Command Preprocessing (`` !`cmd` ``)
**Utility**: 9/10
**Rationale**: Pre-populates the skill with live repo metadata before Claude starts reasoning. Eliminates wasteful initial discovery steps.

**Application**:
```markdown
## Repository Context
- Total files: !`find $0 -type f | wc -l`
- File types: !`find $0 -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20`
- Git status: !`git status --short | head -20`
- Recent changes: !`git log --oneline -10`
```

## Tier 2: High Value (Should Use)

### 7. `context: fork` for Isolated Execution
**Utility**: 8/10
**Rationale**: Running the audit in a forked context prevents it from polluting the main conversation with massive amounts of file analysis data. The audit report is returned as a summary.

**Trade-off**: Forked context loses access to conversation history, but for an audit command this is actually desirable -- each invocation should be self-contained.

### 8. Custom Subagent Definitions
**Utility**: 8/10
**Rationale**: Define specialized audit agents in `.claude/agents/` with tailored system prompts for each audit pass type. A "surface-scanner" agent has different instructions than a "structural-auditor" agent.

**Application**:
```yaml
# .claude/agents/audit-scanner.md
---
name: audit-scanner
description: Read-only file scanner for repository audit passes
tools: Read, Grep, Glob
model: haiku
permissionMode: plan
---
You are a code auditor performing read-only analysis...
```

### 9. `disable-model-invocation: true`
**Utility**: 8/10
**Rationale**: The audit command should only run when explicitly invoked by the user. It is resource-intensive and should never auto-trigger. This field removes it from Claude's auto-invocation context entirely, saving context budget.

### 10. Model Selection (`model` field)
**Utility**: 7/10
**Rationale**: Use `haiku` for Pass 1 (surface scan) subagents to reduce cost and increase speed. Use `sonnet` or `inherit` for Pass 2/3 which require deeper reasoning.

**Application**: Different subagent definitions with different models, or dynamic model selection based on pass type.

### 11. Extended Thinking ("ultrathink")
**Utility**: 7/10
**Rationale**: Useful for the final synthesis phase where cross-cutting patterns need to be identified across all batch results. Include "ultrathink" in the SKILL.md content for the synthesis pass.

### 12. `maxTurns` Limit on Subagents
**Utility**: 7/10
**Rationale**: Prevents runaway subagents. A file batch audit should complete in a bounded number of turns. Setting `maxTurns: 30` ensures agents don't spiral on edge cases.

## Tier 3: Moderate Value (Nice to Have)

### 13. Hooks (`PreToolUse` / `PostToolUse`)
**Utility**: 6/10
**Rationale**: Could enforce read-only behavior as a safety net, or log tool usage for audit trail. The `PreToolUse` hook could block any Write/Edit tool calls as a defense-in-depth measure.

### 14. `${CLAUDE_SESSION_ID}` Variable
**Utility**: 6/10
**Rationale**: Useful for naming audit output files uniquely per session, preventing overwrite of previous audit results.

**Application**: `audit-results/${CLAUDE_SESSION_ID}/report.md`

### 15. Persistent Memory for Subagents
**Utility**: 5/10
**Rationale**: Could allow audit agents to learn patterns across runs -- "this codebase frequently has X issue." However, each audit should primarily be evidence-based from the current codebase state, not biased by prior runs.

### 16. `argument-hint` Frontmatter
**Utility**: 5/10
**Rationale**: Improves UX by showing expected arguments in autocomplete. Purely ergonomic.

**Application**: `argument-hint: [target-path] [--pass surface|structural|cross-cutting] [--batch-size N]`

### 17. Skill Invocation from Skills
**Utility**: 5/10
**Rationale**: Could allow the main audit skill to invoke helper skills (e.g., `/sc:repo-audit-summarize`). However, this adds complexity and the same result can be achieved with well-structured prompts.

### 18. `permissionMode: plan` for Subagents
**Utility**: 4/10
**Rationale**: Forces subagents into read-only plan mode. Redundant if we already restrict tools, but provides defense-in-depth.

## Tier 4: Low Value (Not Needed)

### 19. `user-invocable: false`
**Utility**: 2/10
**Rationale**: Makes skill only Claude-invocable. Not useful -- the audit command should be explicitly triggered by users.

### 20. Agent Teams
**Utility**: 2/10
**Rationale**: Experimental, high token cost, designed for inter-agent debate. Our audit pattern is coordinator-to-worker, not peer collaboration. Subagents are the right abstraction.

### 21. MCP Server Specification in Subagents
**Utility**: 2/10
**Rationale**: Audit agents primarily need read-only codebase tools. MCP servers like Sequential Thinking could help with analysis but add complexity and are unavailable in background subagents.

### 22. Plugin Distribution
**Utility**: 1/10
**Rationale**: Future consideration for distributing the audit command. Not relevant to building it.

---

# Part 3: Commands vs Skills Analysis

## Detailed Feature Comparison

| Capability | Commands (`.claude/commands/`) | Skills (`.claude/skills/`) |
|-----------|-------------------------------|---------------------------|
| **File format** | Single `.md` file | Directory with `SKILL.md` + supporting files |
| **Frontmatter support** | Full (same fields) | Full (same fields) |
| **$ARGUMENTS** | Yes | Yes |
| **Numbered args ($0, $1)** | Yes | Yes |
| **Shell preprocessing** | Yes (`` !`cmd` ``) | Yes (`` !`cmd` ``) |
| **allowed-tools** | Yes | Yes |
| **model selection** | Yes | Yes |
| **context: fork** | Yes | Yes |
| **Supporting files** | No (single file only) | Yes (directory structure) |
| **Auto-invocation by Claude** | Yes (default) | Yes (default) |
| **disable-model-invocation** | Yes | Yes |
| **user-invocable** | Yes | Yes |
| **Hooks** | Yes | Yes |
| **Progressive disclosure** | No (entire file loads) | Yes (description first, full content on invoke) |
| **Monorepo discovery** | Supported | Supported |
| **Live change detection** | Via `--add-dir` | Via `--add-dir` |
| **Conflict resolution** | Skill wins if same name | N/A |

## Recommendation for Repository Audit Command

**Use a Skill (`.claude/skills/sc-repo-audit/SKILL.md`)**

Reasons:

1. **Supporting files are essential**: The audit command needs separate rule definition files, report templates, and helper scripts. A single `.md` file cannot hold all of this cleanly.

2. **Progressive disclosure**: The audit command description is lightweight (~100 chars), but the full orchestration instructions are substantial (~300-500 lines). With a skill, only the description consumes context budget at startup.

3. **Organization**: Templates, rules, and scripts in subdirectories keep the SKILL.md focused on orchestration logic while supporting files handle the details.

4. **`disable-model-invocation: true`**: The audit is resource-intensive and should only run when explicitly triggered. This field removes it from Claude's context entirely when not in use.

5. **Future extensibility**: New audit passes, custom rules, or report formats can be added as supporting files without modifying SKILL.md.

### Recommended Skill Structure

```
.claude/skills/sc-repo-audit/
├── SKILL.md                        # Main orchestration (under 500 lines)
├── rules/
│   ├── pass1-surface-scan.md       # File hygiene, naming, structure rules
│   ├── pass2-structural-audit.md   # Code quality, patterns, architecture rules
│   └── pass3-cross-cutting.md      # Cross-file concerns, duplication, consistency
├── templates/
│   ├── batch-report.md             # Template for per-batch findings
│   ├── pass-summary.md             # Template for per-pass rollup
│   └── final-report.md             # Template for consolidated audit report
└── scripts/
    └── count-files.sh              # Helper for file enumeration and batching
```

### Why Not a Command

A command at `.claude/commands/sc-repo-audit.md` would work for a simple version, but:
- Cannot include separate rule files or templates
- The single file would need to contain ALL orchestration logic, rules, and templates
- At 500+ lines, it becomes unwieldy and wasteful of context
- No separation of concerns

### Why Not a Custom Subagent

A subagent at `.claude/agents/repo-auditor.md` is the wrong abstraction:
- Subagents are workers, not orchestrators
- The audit command IS the orchestrator that SPAWNS subagents
- A skill invokes the Task tool to create subagents; a subagent cannot itself spawn sub-subagents

### Hybrid Approach (Recommended)

Use BOTH a skill AND custom subagent definitions:

```
.claude/skills/sc-repo-audit/       # The orchestrator (skill)
├── SKILL.md
├── rules/
├── templates/
└── scripts/

.claude/agents/audit-scanner.md     # Worker agent (subagent)
.claude/agents/audit-analyzer.md    # Deep analysis agent (subagent)
```

The skill orchestrates; the subagents execute. The skill's `SKILL.md` uses the Task tool to spawn the custom subagents defined in `.claude/agents/`.

---

# Part 4: Advanced Orchestration Patterns

## Pattern 1: Batch-Parallel Fan-Out/Fan-In

The core pattern for our audit command. An orchestrator divides work into batches, fans out to parallel subagents, and fans in results.

### Implementation

```markdown
# In SKILL.md

## Phase 1: Discovery
Use shell preprocessing to gather repo metadata:
- File list: !`find $0 -type f -not -path '*/.git/*' -not -path '*/node_modules/*'`
- Total count: !`find $0 -type f -not -path '*/.git/*' | wc -l`

## Phase 2: Batch Creation
Divide the file list into batches of $1 files (default 50).
Create a TodoWrite task for each batch.

## Phase 3: Parallel Execution
For each batch, spawn a Task subagent with:
- The batch file list
- The audit rules for the current pass
- The report template
- Read-only tool restrictions

Wait for all subagents to complete.

## Phase 4: Aggregation
Read all batch reports.
Synthesize into a consolidated report using the final-report template.
```

### Key Considerations
- **Subagent limit**: ~7-10 concurrent. For 1000 files at 50/batch = 20 batches, run in waves of 7-8.
- **Token overhead**: ~20K per subagent invocation. Budget accordingly.
- **Context isolation**: Each subagent only sees its batch, not the entire repo.

## Pattern 2: Multi-Pass Escalation

Each pass builds on the previous one. Findings from Pass 1 inform the focus areas for Pass 2.

### Implementation

```
Pass 1 (Surface Scan) → Save findings to file
                       → Extract "areas of concern" list

Pass 2 (Structural Audit) → Read Pass 1 findings
                           → Focus on flagged areas
                           → Save deeper findings to file

Pass 3 (Cross-Cutting) → Read Pass 1 + Pass 2 findings
                        → Analyze cross-file patterns
                        → Produce final consolidated report
```

### Key Considerations
- Each pass writes results to disk (e.g., `.claude-audit/pass1-results.md`)
- Subsequent passes read previous results via shell preprocessing
- This creates a natural checkpoint system -- if the session crashes, results from completed passes are preserved

## Pattern 3: Incremental Save to Prevent Context Loss

For long-running operations, save intermediate results to disk after each batch completes.

### Implementation

```markdown
## Incremental Save Protocol

After each batch subagent returns:
1. Write batch findings to `.claude-audit/batch-{N}-findings.md`
2. Update `.claude-audit/progress.json` with completion status
3. Update TodoWrite with current progress

If the session is interrupted:
- Resume by reading `.claude-audit/progress.json`
- Skip completed batches
- Continue from the last incomplete batch
```

### Key Considerations
- Bash tool writes results to disk (not just context)
- Progress file enables resume-from-checkpoint
- Each batch result is independently useful even if the full audit doesn't complete

## Pattern 4: Quality Gates Between Passes

Enforce validation before advancing to the next audit pass.

### Implementation

```markdown
## Quality Gate: Pass N Complete

Before advancing to Pass N+1:
1. Verify all batch tasks for Pass N are marked complete
2. Read all batch reports and verify they contain required sections
3. Check that the pass summary has been generated
4. Verify findings count > 0 (if 0, investigate whether scan was too permissive)
5. Only proceed if all gates pass

If a gate fails:
- Log the failure reason
- Attempt remediation (re-run failed batches)
- If still failing after retry, mark the pass as "incomplete" and proceed with warning
```

## Pattern 5: File-Based Coordination (No Nested Agents)

Since subagents cannot spawn sub-subagents, all coordination must flow through the main orchestrator via files on disk.

### Implementation

```
Orchestrator (Skill)
├── Spawns: Batch Agent 1 → writes batch-1-results.md
├── Spawns: Batch Agent 2 → writes batch-2-results.md
├── Spawns: Batch Agent 3 → writes batch-3-results.md
├── [Waits for all to complete]
├── Reads all batch-N-results.md files
├── Aggregates into pass-summary.md
├── Spawns: Cross-Reference Agent → reads pass-summary.md, writes cross-ref.md
└── Final synthesis: reads all artifacts, writes final-report.md
```

### Key Considerations
- Files on disk are the only coordination channel between subagents
- The orchestrator must handle the fan-in (reading and merging results)
- Use a consistent output directory (e.g., `.claude-audit/{session-id}/`)

## Pattern 6: Adaptive Batch Sizing

Adjust batch sizes based on file complexity, not just count.

### Implementation

```markdown
## Adaptive Batching

When creating batches:
1. Group files by type (code vs config vs docs vs tests)
2. Weight files by size:
   - Small (<100 lines): weight 1
   - Medium (100-500 lines): weight 2
   - Large (500+ lines): weight 4
3. Create batches with total weight <= 100
4. This ensures subagents don't get overloaded with large files
   while handling many small files efficiently
```

## Pattern 7: Structured Output Enforcement

Ensure all subagents produce consistently structured reports.

### Implementation

Include a report template in the skill's supporting files, and inject it into each subagent's prompt:

```markdown
# In rules/output-format.md

## Required Output Format

For each file analyzed, report:

### [filename]
- **Status**: PASS | WARN | FAIL
- **Issues Found**: [count]
- **Severity Distribution**: Critical: N, High: N, Medium: N, Low: N
- **Findings**:
  1. [SEVERITY] [CATEGORY]: Description (line N)
  2. ...

## Batch Summary
- **Files Analyzed**: N
- **Files with Issues**: N
- **Total Issues**: N
- **Critical Issues**: N (list filenames)
```

## Pattern 8: Haiku-First, Escalate-to-Sonnet

Use fast, cheap models for initial scanning and escalate only flagged files to deeper analysis.

### Implementation

```
Pass 1: Haiku agents scan ALL files quickly
        → Flag files with potential issues

Pass 2: Sonnet agents deeply analyze ONLY flagged files
        → This might be 10-20% of total files
        → Much more cost-effective than running Sonnet on everything
```

### Cost Savings
- Haiku: ~10x cheaper than Sonnet
- If Pass 1 flags 15% of files, total cost is:
  - 100% * Haiku + 15% * Sonnet
  - vs. 100% * Sonnet (naive approach)
  - Roughly 50-70% cost reduction

## Pattern 9: Adversarial Validation (Dual-Agent Review)

For high-confidence findings, spawn a second agent to challenge or confirm.

### Implementation

```markdown
## Adversarial Validation (Optional, for critical findings)

For any finding marked CRITICAL:
1. Spawn a "devil's advocate" subagent
2. Provide it the finding and the relevant code
3. Ask it to argue why the finding might be a FALSE POSITIVE
4. If it cannot convincingly argue false positive, the finding is CONFIRMED
5. If it raises valid objections, downgrade to UNCERTAIN
```

### Key Considerations
- Only apply to critical findings (cost-prohibitive otherwise)
- Reduces false positive rate significantly
- Adds ~20K tokens per validated finding

## Pattern 10: Resume-Safe Execution with Checkpointing

Handle session interruptions gracefully.

### Implementation

```markdown
## Checkpoint Protocol

State file: `.claude-audit/state.json`

```json
{
  "session_id": "${CLAUDE_SESSION_ID}",
  "started_at": "2026-02-19T10:00:00Z",
  "current_pass": 1,
  "total_passes": 3,
  "batches": [
    {"id": 1, "status": "complete", "files": 50, "issues": 12},
    {"id": 2, "status": "complete", "files": 50, "issues": 8},
    {"id": 3, "status": "in_progress", "files": 50, "issues": null},
    {"id": 4, "status": "pending", "files": 47, "issues": null}
  ]
}
```

On invocation:
1. Check for existing state file
2. If found, ask user: "Previous audit found. Resume from batch 3 of pass 1? (Y/n)"
3. If yes, skip completed batches and continue
4. If no, start fresh
```

---

## Appendix A: Token Cost Estimates

For a 1000-file repository audit:

| Component | Token Cost | Notes |
|-----------|-----------|-------|
| Skill loading | ~2K | SKILL.md + frontmatter |
| Shell preprocessing | ~1K | File counts, git status |
| Pass 1: Surface Scan | ~400K-600K | 20 batches * ~20-30K each (Haiku) |
| Pass 2: Structural Audit | ~200K-400K | Fewer files (flagged only), Sonnet |
| Pass 3: Cross-Cutting | ~100K-200K | Pattern analysis, Sonnet |
| Aggregation/Synthesis | ~50K-100K | Reading and merging results |
| **Total Estimated** | **~750K-1.3M** | Varies by repo complexity |

**Cost optimization levers**:
- Use Haiku for Pass 1 (reduces by ~60%)
- Increase batch size (reduces subagent overhead)
- Skip Pass 3 for smaller repos
- Use `maxTurns` to prevent runaway agents

## Appendix B: Limitations and Constraints

1. **No nested subagent spawning**: Subagents cannot spawn sub-subagents. All orchestration must happen in the top-level skill.
2. **Background subagents lack MCP**: MCP tools are unavailable in background subagents.
3. **~7-10 concurrent subagent practical limit**: Not a hard limit but performance degrades beyond this.
4. **20K token overhead per subagent**: Significant for many small batches.
5. **No shared memory between subagents**: Coordination must happen via files on disk or through the orchestrator.
6. **Session context limit**: The orchestrator itself has a context window. For very large repos, the aggregation phase may need compaction or multi-stage synthesis.
7. **Skill description budget**: 2% of context window (fallback: 16,000 chars). Keep the audit skill description concise.
8. **SKILL.md recommended under 500 lines**: Move detailed rules and templates to supporting files.

## Appendix C: Sources

- [Slash Commands - Claude Code Docs](https://code.claude.com/docs/en/slash-commands) (redirects to Skills page)
- [Extend Claude with Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Create Custom Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Orchestrate Teams of Claude Code Sessions - Claude Code Docs](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Custom Commands: 3 Practical Examples](https://www.aiengineering.report/p/claude-code-custom-commands-3-practical)
- [Claude Code Sub-Agents: Parallel vs Sequential Patterns](https://claudefa.st/blog/guide/agents/sub-agent-best-practices)
- [Claude Code - When to use task tool vs subagents](https://amitkoth.com/claude-code-task-tool-vs-subagents/)
- [Task/Agent Tools - ClaudeLog](https://claudelog.com/mechanics/task-agent-tools/)
- [Understanding Claude Code's Full Stack: MCP, Skills, Subagents, and Hooks](https://alexop.dev/posts/understanding-claude-code-full-stack/)
- [Choosing between Skills, Subagents, and MCP Servers](https://smithhorngroup.substack.com/p/choosing-between-skills-subagents)
- [Claude Code Agent Teams: The Complete Guide 2026](https://claudefa.st/blog/guide/agents/agent-teams)
- [From Tasks to Swarms: Agent Teams in Claude Code](https://alexop.dev/posts/from-tasks-to-swarms-agent-teams-in-claude-code/)
- [Understanding Claude Code: Skills vs Commands vs Subagents vs Plugins](https://www.youngleaders.tech/p/claude-skills-commands-subagents-plugins)
- [When to Use Claude Code Skills vs Workflows vs Agents](https://danielmiessler.com/blog/when-to-use-skills-vs-commands-vs-agents)
- [Claude Code Tips & Tricks: Custom Slash Commands](https://cloudartisan.com/posts/2025-04-14-claude-code-tips-slash-commands/)
- [Parallel Sub-Agents in Claude Code: Multiplying Your Development Speed](https://proofsource.ai/2025/12/parallel-sub-agents-in-claude-code-multiplying-your-development-speed/)
- [Building a C Compiler with a Team of Parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)
