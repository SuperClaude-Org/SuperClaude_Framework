# Policy Extract: Command/Skill Architecture Policy

> **Source**: `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/framework/command-skill-policy.md`
> **Source Version**: 1.0.0
> **Extracted for**: v2.01 Architecture Refactor spec planning
> **Extraction date**: 2026-02-24

---

## 1. Core Principle

> **Commands are doors. Skills are rooms. Refs are drawers.**

A **command** is a slim entry point that the user invokes. A **protocol skill** holds the full behavioral specification. **Ref files** hold detailed algorithms, templates, and scoring rubrics loaded on-demand per pipeline step.

This separation exists because:
1. Commands are auto-loaded into context when the user types `/sc:<name>` -- they must be small
2. Protocol skills contain the actual execution logic -- they can be arbitrarily detailed
3. Ref files are step-specific detail -- loading them all upfront wastes context budget

---

## 2. 3-Tier Loading Architecture (Full Specification)

| Tier | What | Where (deployed) | Loading Mechanism | Max Size |
|------|------|-------------------|-------------------|----------|
| **0** -- Command | Entry point: metadata, usage, examples, activation directive, boundaries | `.claude/commands/sc/<name>.md` | Auto-loaded on `/sc:<name>` invocation | **<=150 lines** |
| **1** -- Protocol Skill | Full behavioral protocol: steps, agent dispatch, YAML specs, error handling | `.claude/skills/sc-<name>-protocol/SKILL.md` | Agent invokes `Skill sc:<name>-protocol` | Unlimited |
| **2** -- Refs | Detailed algorithms, templates, scoring rubrics | `.claude/skills/sc-<name>-protocol/refs/*.md` | Loaded via `claude -p` script per step | Unlimited |

### Loading Flow

```
User types:     /sc:adversarial --compare file1.md,file2.md
                        |
                        v
Tier 0:         adversarial.md auto-loaded (<=150 lines)
                        |
                        v (## Activation section says: Invoke Skill sc:adversarial-protocol)
                        |
Tier 1:         Agent calls Skill tool -> sc:adversarial-protocol/SKILL.md loaded
                        |
                        v (Step 3 says: Load refs/scoring-protocol.md via claude -p)
                        |
Tier 2:         claude -p injects scoring-protocol.md into sub-agent context
```

---

## 3. The Re-Entry Block Problem

The command and skill MUST have different names to avoid the "skill already running" re-entry block. When `/sc:adversarial` triggers, the skill `sc:adversarial` is marked as running. If the command tried to invoke `Skill sc:adversarial`, it would be blocked. Using `sc:adversarial-protocol` as the skill name avoids this entirely.

This is the fundamental reason for the `-protocol` suffix convention.

---

## 4. Naming Conventions

| Component | Name Pattern | Example | Directory/File |
|-----------|-------------|---------|----------------|
| Command | `<name>` | `adversarial` | `commands/<name>.md` |
| Protocol Skill | `sc:<name>-protocol` | `sc:adversarial-protocol` | `skills/sc-<name>-protocol/SKILL.md` |
| Ref files | descriptive name | `scoring-protocol.md` | `skills/sc-<name>-protocol/refs/` |
| Standalone Skill | no `sc-` prefix | `confidence-check` | `skills/<name>/SKILL.md` |

**Rules**:
- Protocol skills MUST end in `-protocol`
- Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`
- Standalone skills (no matching command) do NOT use the `-protocol` suffix
- Command names NEVER include `-protocol`

---

## 5. Command File Contract (Tier 0) -- Verbatim Template

Every command that has a protocol skill follows this exact template:

```markdown
---
name: <name>
description: "<one-line description>"
category: <development|analysis|quality|testing|documentation|meta>
complexity: <basic|moderate|advanced>
mcp-servers: [<server-list>]
personas: [<persona-list>]
---

# /sc:<name> - <Title>

## Usage
<invocation patterns with code blocks>

## Arguments
<flags/options table>

## Examples
<3-5 concrete usage examples>

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:<name>-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Behavioral Summary
<<=5 sentences describing what the pipeline does at a high level>

## Boundaries
**Will:** <bullet list>
**Will Not:** <bullet list>

## Related Commands
<optional: table of related commands>
```

### Hard Constraints

- **<=150 lines** total
- **NO** protocol YAML blocks, step definitions, or scoring algorithms
- **MUST** have `## Activation` section if a protocol skill exists
- `## Activation` MUST name the exact skill: `sc:<name>-protocol`
- The `## Activation` section MUST include the "Do NOT proceed" warning
- `## Behavioral Summary` is <=5 sentences (high-level only)

### Command-Only Files (No Skill)

Commands without a matching protocol skill:
- Follow the same template but omit `## Activation`
- May contain full behavioral instructions inline
- Subject to size limits: **WARN at 200 lines, ERROR at 500 lines**
- Commands exceeding 500 lines MUST be split into command + protocol skill

---

## 6. Protocol Skill Contract (Tier 1) -- Verbatim Template

```markdown
---
name: sc:<name>-protocol
description: "<description>"
allowed-tools: <tool list>
argument-hint: "<usage hint>"
---

# sc:<name>-protocol - <Title>

## Purpose
<what this protocol does and why>

## Triggers
<when this skill is invoked>

## Protocol Steps
### Step 1: <Name>
<full specification with YAML blocks>
### Step 2: <Name>
...

## Configurable Parameters
<flags, thresholds, defaults>

## Agent Delegation
<which agents are spawned, their roles, dispatch config>

## MCP Integration
<which MCP servers, which steps, circuit breakers>

## Error Handling
<error matrix with recovery actions>

## Return Contract
<output fields for programmatic integration>

## Boundaries
**Will:** / **Will Not:**
```

### Hard Constraints

- **MUST** have frontmatter with `name`, `description`, `allowed-tools`
- `name` field MUST match the directory name pattern: `sc:<name>-protocol`
- **MUST** define all behavioral logic (the command file contains NONE)
- References to Tier 2 content use the standard directive:
  ```
  **Ref**: Load `refs/<filename>.md` via claude -p before executing this step.
  ```
- No size limit, but prefer splitting deep detail into refs/ for context efficiency

---

## 7. Ref File Contract (Tier 2) -- Verbatim Template

Ref files are self-contained reference documents loadable independently via `claude -p`:

```markdown
# <Title>

## Purpose
<what this ref contains and when to load it>

## Content
<the actual specification, algorithm, template, or rubric>

---
*Reference document for sc:<name>-protocol skill*
*Source: <original source attribution>*
```

### Hard Constraints

- **MUST** be independently useful (no dangling references requiring SKILL.md context)
- **MUST** have a `## Purpose` section explaining when to load it
- Loaded via `claude -p` with ref content as `--append-system-prompt`
- One ref per concern (don't combine scoring + templates in one file)

---

## 8. Source Layout (Reference Directory Structure)

```
src/superclaude/
  commands/
    adversarial.md                  # Tier 0 (<=150L, has ## Activation)
    cleanup-audit.md                # Tier 0 (<=150L, has ## Activation)
    roadmap.md                      # Tier 0 (<=150L, has ## Activation)
    analyze.md                      # Command-only (no skill needed)
    build.md                        # Command-only
    ...
  skills/
    sc-adversarial-protocol/        # Tier 1+2
      SKILL.md
      __init__.py
      refs/
        scoring-protocol.md
        artifact-templates.md
        debate-protocol.md
        agent-specs.md
    sc-roadmap-protocol/            # Tier 1+2
      SKILL.md
      refs/
    sc-cleanup-audit-protocol/      # Tier 1+2
      SKILL.md
      refs/
    sc-task-unified-protocol/       # Tier 1
      SKILL.md
    sc-validate-tests-protocol/     # Tier 1
      SKILL.md
    confidence-check/               # Standalone skill (no command)
      SKILL.md
```

---

## 9. CI Enforcement -- All 10 Checks

### `make lint-architecture`

| # | Check | Severity | Rule |
|---|-------|----------|------|
| 1 | Bidirectional link (cmd->skill) | ERROR | Command with `## Activation` referencing a skill -> that skill directory MUST exist |
| 2 | Bidirectional link (skill->cmd) | ERROR | Skill directory matching `sc-*-protocol` -> command `<name>.md` MUST exist (strip `sc-` prefix and `-protocol` suffix) |
| 3 | Command size (warn) | WARN | Command file >200 lines |
| 4 | Command size (error) | ERROR | Command file >500 lines |
| 5 | Inline protocol in command | ERROR | Command with matching `-protocol` skill contains YAML code blocks >20 lines |
| 6 | Activation section present | ERROR | Command with matching `-protocol` skill directory missing `## Activation` section |
| 7 | Activation references correct skill | ERROR | `## Activation` section does not contain `Skill sc:<name>-protocol` |
| 8 | Skill frontmatter complete | ERROR | SKILL.md missing `name`, `description`, or `allowed-tools` in frontmatter |
| 9 | Skill naming consistency | ERROR | Skill directory `sc-*-protocol/` but SKILL.md `name` field doesn't end in `-protocol` |
| 10 | Sync integrity | ERROR | Files in `src/` not matching `.claude/` (existing `verify-sync` check) |

### `make verify-sync` updates

- **Remove** the "served by command" skip message
- **Always** check skill directories against `.claude/skills/`
- **Validate** `-protocol` naming convention

---

## 10. Migration Checklist (4 Phases)

### Phase 1: Rename Skill Directories

| Current | Target | SKILL.md `name` field |
|---------|--------|-----------------------|
| `src/skills/sc-adversarial/` | `src/skills/sc-adversarial-protocol/` | `sc:adversarial-protocol` |
| `src/skills/sc-cleanup-audit/` | `src/skills/sc-cleanup-audit-protocol/` | `sc:cleanup-audit-protocol` |
| `src/skills/sc-roadmap/` | `src/skills/sc-roadmap-protocol/` | `sc:roadmap-protocol` |
| `src/skills/sc-task-unified/` | `src/skills/sc-task-unified-protocol/` | `sc:task-unified-protocol` |
| `src/skills/sc-validate-tests/` | `src/skills/sc-validate-tests-protocol/` | `sc:validate-tests-protocol` |

### Phase 2: Refactor Command Files

For each of the 5 commands with protocol skills:
1. Trim to <=150 lines
2. Add `## Activation` section with `Skill sc:<name>-protocol` directive
3. Remove any inline protocol YAML
4. Keep: metadata, usage, arguments, examples, behavioral summary, boundaries

### Phase 3: Update Build System

1. Remove skip logic from `sync-dev` (Makefile lines 114-117)
2. Add `lint-architecture` target
3. Update `verify-sync` to remove "served by command" skip

### Phase 4: Validate

1. `make sync-dev` -- deploys all commands AND skills
2. `make verify-sync` -- confirms no drift
3. `make lint-architecture` -- all 10 checks pass

---

## 11. Line Count Constraints Summary

| Component | Soft Limit | Hard Limit | Action |
|-----------|-----------|------------|--------|
| Command with protocol skill | 150 lines | 150 lines | ERROR if exceeded |
| Command without skill | 200 lines (WARN) | 500 lines (ERROR) | Must split at 500+ |
| Protocol Skill (SKILL.md) | None | Unlimited | Prefer splitting to refs |
| Ref files | None | Unlimited | One concern per file |
| YAML blocks in commands (with skill) | N/A | 20 lines | ERROR if exceeded |

---

## 12. Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Model 1 (Command = Entry Point, Skill = Protocol) | Clean separation, commands readable, skills unlimited | 2026-02-23 |
| Skill tool dispatch for Tier 1 loading | Reliable, framework-native, agent must explicitly load | 2026-02-23 |
| `claude -p` for Tier 2 ref loading | Guaranteed injection, no trust gap, aligns with headless exploration | 2026-02-23 |
| Separate names (command != skill) | Avoids "skill already running" re-entry block | 2026-02-23 |
| `-protocol` suffix convention | Clear semantic signal, easy to lint, no ambiguity | 2026-02-23 |
| 500-line error threshold for commands | Catches worst outliers, leaves room for moderate complexity | 2026-02-23 |
| CI enforcement via lint-architecture | Prevents drift, catches violations at PR time | 2026-02-23 |

---

## 13. Current Migration Status (Pre-Rollback)

Based on the git status of the current branch (`feature/v2.01-Roadmap-V3`), **Phase 1 (Rename Skill Directories) has been executed**. The following renames are staged:

- `sc-adversarial/` -> `sc-adversarial-protocol/`
- `sc-cleanup-audit/` -> `sc-cleanup-audit-protocol/`
- `sc-roadmap/` -> `sc-roadmap-protocol/`
- `sc-task-unified/` -> `sc-task-unified-protocol/`
- `sc-validate-tests/` -> `sc-validate-tests-protocol/`

**Phase 2 (Refactor Command Files)**: Not started or incomplete -- no evidence of command trimming in git status.
**Phase 3 (Update Build System)**: Not started -- no evidence of Makefile changes.
**Phase 4 (Validate)**: Not started -- depends on Phase 2 and 3.

---

## 14. Backlog Items (Future Work from Policy)

| Item | Priority | Trigger |
|------|----------|---------|
| Split `recommend.md` (1005L) into command + protocol skill | Medium | Next feature touch |
| Split `review-translation.md` (913L) | Medium | Next feature touch |
| Split `pm.md` (592L) | Medium | Next feature touch |
| Split `task-unified.md` command (567L) | Low | Already has protocol skill |
| Split `spec-panel.md` (435L) | Low | Next feature touch |
| Split `task-mcp.md` (375L) | Low | Next feature touch |
| Design `claude -p` Tier 2 ref loader script | High | Before sc:adversarial re-run |
| Cross-skill invocation patterns (roadmap -> adversarial-protocol) | High | Sprint spec dependency |

---

## 15. Gaps and Ambiguities for v2.01 to Address

### Gap 1: `claude -p` Tier 2 Loader Not Designed
The policy references `claude -p` for loading ref files but provides no script, no implementation, and no specification for how this works in practice. The backlog calls out "Design `claude -p` Tier 2 ref loader script" as High priority. v2.01 needs to either:
- Design and implement the loader script, OR
- Define an alternative Tier 2 loading mechanism

### Gap 2: Cross-Skill Invocation Not Specified
The backlog notes "Cross-skill invocation patterns (roadmap -> adversarial-protocol)" as High priority but the policy provides no specification for how one protocol skill invokes another. This is critical for pipeline composition.

### Gap 3: `__init__.py` Purpose Undefined
The source layout shows `__init__.py` files in skill directories but the policy never explains their purpose, required content, or whether they are mandatory. Some skills have them, some don't.

### Gap 4: Frontmatter Field `argument-hint` vs Other Fields
The Skill Contract template includes `argument-hint` in frontmatter, but this field is not mentioned in the CI enforcement checks (Check 8 only validates `name`, `description`, `allowed-tools`). Is `argument-hint` required or optional?

### Gap 5: Standalone Skill Contract Not Fully Specified
The policy says standalone skills (no matching command) do NOT use `-protocol` suffix, but provides no contract template for standalone skills. Do they follow the same SKILL.md structure as protocol skills? Which frontmatter fields are required?

### Gap 6: Command Frontmatter Fields Not CI-Validated
The Command Contract specifies frontmatter fields (`name`, `description`, `category`, `complexity`, `mcp-servers`, `personas`) but no CI check validates command frontmatter completeness. Only skill frontmatter is checked (Check 8).

### Gap 7: No Rollback Procedure
The migration checklist defines a forward path but no rollback procedure. When the v2.02 rollback happened, there was no documented process for reverting the architectural changes.

### Gap 8: Sync Direction Ambiguity
The policy says `src/` is source of truth and `.claude/` is deployed copy, but the existing `verify-sync` behavior (which had a "served by command" skip) suggests historical confusion about which direction sync flows. v2.01 should make this unambiguous.

---

*Extracted from command-skill-policy.md v1.0.0 for v2.01 Architecture Refactor specification planning.*
