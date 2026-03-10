# Command-Skill Architecture Policy

**Version**: 1.0.0
**Authored**: 2026-02-24
**Status**: Active
**Scope**: SuperClaude Framework v2.01+

---

## 1. Overview and Metaphor

This document defines the canonical architecture policy for the SuperClaude Framework's command-skill separation model.

**Central Metaphor**: "Commands are doors. Skills are rooms. Refs are drawers."

- **Commands** (Tier 0): Thin entry points that dispatch to skills. Auto-loaded on `/sc:<name>`.
- **Skills** (Tier 1): Full behavioral protocol specifications. Loaded on-demand via Skill tool.
- **Refs** (Tier 2): Step-specific detail loaded on-demand via `claude -p`.

This separation ensures token efficiency (no protocol bloat in auto-loaded context), clear invocation chains (explicit tool dispatch, not prose), and enforceable contracts (CI-validated structure).

---

## 2. Three-Tier Model

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 0 — COMMAND                                           │
│  Auto-loaded on /sc:<name>  |  target ≤150, max ≤350 lines  │
│  Location: src/superclaude/commands/<name>.md               │
│  "Commands are DOORS"                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ ## Activation → Skill sc:<name>-protocol
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1 — PROTOCOL SKILL                                    │
│  Loaded by agent via Skill tool  |  Unlimited size          │
│  Location: src/superclaude/skills/sc-<name>-protocol/       │
│  "Skills are ROOMS"                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ Ref: Load refs/<file>.md via claude -p
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2 — REF FILES                                         │
│  On-demand via claude -p  |  One concern per file           │
│  Location: src/superclaude/skills/sc-<name>-protocol/refs/  │
│  "Refs are DRAWERS"                                         │
└─────────────────────────────────────────────────────────────┘
```

| Tier | Component | Loading Mechanism | Max Size |
|------|-----------|-------------------|----------|
| 0 | Command | Auto-loaded on `/sc:<name>` invocation | target ≤150, max ≤350 lines |
| 1 | Protocol Skill | Agent invokes `Skill sc:<name>-protocol` | Unlimited |
| 2 | Refs | Loaded via `claude -p` script per step | Unlimited |

---

## 3. Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| Command file | `<name>.md` | `adversarial.md` |
| Skill directory | `sc-<name>-protocol/` | `sc-adversarial-protocol/` |
| SKILL.md `name:` field | `sc:<name>-protocol` | `sc:adversarial-protocol` |
| Ref files | descriptive name | `scoring-protocol.md` |
| Standalone skills | `<name>` (no prefix/suffix) | `confidence-check` |

**Rules**:
- Protocol skills MUST end in `-protocol` (both directory and frontmatter name)
- Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`
- Standalone skills (no matching command) do NOT use the `-protocol` suffix
- Command names NEVER include `-protocol`
- Directory names use hyphens; frontmatter `name:` uses colons

**Why separate names are mandatory**: Using the same name for command and skill triggers a re-entry block ("Skill already running"). The `-protocol` suffix ensures different identifiers.

---

## 4. Command File Contract

**Definition**: A slim, user-facing entry point auto-loaded by Claude Code when the user types `/sc:<name>`.

**Required Sections**:
- YAML frontmatter (`name`, `description`, `category`, `complexity`, `allowed-tools`)
- `## Usage`
- `## Arguments`
- `## Examples`
- `## Activation` (if protocol skill exists)
- `## Behavioral Summary` (≤5 sentences)
- `## Boundaries` (`Will:` / `Will Not:`)

**Hard Constraints**:
- Max size: target ≤150 lines; hard limit ≤350 lines (WARN at 350, ERROR at 500)
- `## Activation` MUST name the exact skill: `sc:<name>-protocol`
- `## Activation` MUST include "Do NOT proceed" warning
- `Skill` MUST appear in `allowed-tools` frontmatter
- NO protocol YAML blocks, step definitions, or scoring algorithms

**Command-Only Files** (no paired skill): Omit `## Activation`, may contain full behavioral instructions inline. WARN at 200 lines, ERROR at 500 lines.

---

## 5. Protocol Skill Contract

**Definition**: A full behavioral specification that agents invoke via the Skill tool.

**Required Frontmatter**: `name`, `description`, `allowed-tools`

**Required Sections**:
- `## Purpose`
- `## Triggers`
- `## Protocol Steps`
- `## Agent Delegation`
- `## MCP Integration`
- `## Error Handling`
- `## Return Contract`
- `## Boundaries`

**Hard Constraints**:
- Naming: `sc:<name>-protocol` in frontmatter `name:` field
- Directory: `src/superclaude/skills/sc-<name>-protocol/`
- MUST define all behavioral logic (the command file contains NONE)
- MUST NOT be auto-loaded; only loaded via explicit Skill tool invocation
- Tier 2 reference format: `**Ref**: Load refs/<filename>.md via claude -p before executing this step.`

---

## 6. Ref File Convention

**Definition**: Step-specific detail loaded on-demand via `claude -p`.

**Required Sections**: `## Purpose`, `## Content`

**Hard Constraints**:
- MUST be independently useful (no dangling references requiring SKILL.md context)
- Loaded via `claude -p` with content as `--append-system-prompt`
- One ref per concern (do not combine scoring + templates in one file)
- Location: `src/superclaude/skills/sc-<name>-protocol/refs/`

---

## 7. Invocation Patterns

| Mechanism | Use Case | Context |
|-----------|----------|---------|
| Skill tool | Invoke skill directly in current context | Loads SKILL.md into conversation |
| Task tool | Delegate to sub-agent in fresh context | Spawns new agent (avoids re-entry block) |
| `claude -p` | Inject ref/detail into current context | `--append-system-prompt` |

**Decision rule**:
- Need full skill protocol in current context? → Skill tool
- Need to invoke a skill without re-entry conflict? → Task tool (Task agent wrapper)
- Need step-specific detail without separate execution? → `claude -p` (ref loading)

---

## 8. Anti-Patterns

### Command Anti-Patterns
- Command files >350 lines when a protocol skill exists
- Missing `## Activation` section when paired with protocol skill
- Inline protocol steps or scoring algorithms
- Re-defining behavioral logic already in the skill

### Skill Anti-Patterns
- Missing or incomplete frontmatter
- Skill name not matching directory pattern
- Using same name as command (creates re-entry block)
- Putting user-facing documentation in skill

### Ref Anti-Patterns
- Refs that require SKILL.md context to be understood
- Combining multiple concerns in one ref file
- Loading all refs upfront instead of per-step

### Invocation Anti-Patterns
- Skill-to-skill invocation via Skill tool (re-entry block)
- Natural language "Invoke" without tool binding
- Missing `Skill` in `allowed-tools` frontmatter

---

## 9. CI Enforcement (`make lint-architecture`)

| # | Check | Severity | Status |
|---|-------|----------|--------|
| 1 | Command → Skill link | ERROR | DESIGNED |
| 2 | Skill → Command link | ERROR | DESIGNED |
| 3 | Command size (warn) | WARN | DESIGNED |
| 4 | Command size (error) | ERROR | DESIGNED |
| 5 | Inline protocol in command | ERROR | NEEDS DESIGN |
| 6 | Activation section present | ERROR | DESIGNED |
| 7 | Activation references correct skill | ERROR | NEEDS DESIGN |
| 8 | Skill frontmatter complete | ERROR | DESIGNED |
| 9 | Protocol naming consistency | ERROR | DESIGNED |
| 10 | Sync integrity | ERROR | DELEGATED to `verify-sync` |

**Exit behavior**: Any ERROR → `exit 1` (CI failure). Warnings only → `exit 0`.

---

## 10. Migration Checklist

### Phase 1: Foundation
- [ ] Architecture policy document verified/created (this document)
- [ ] Tier classification policy established

### Phase 2: Invocation Wiring
- [ ] Skill directories renamed with `-protocol` suffix
- [ ] Command `## Activation` sections added
- [ ] `Skill` added to `allowed-tools` frontmatter

### Phase 3: Enforcement
- [ ] `make lint-architecture` target added
- [ ] Skill-skip heuristic removed from `sync-dev`/`verify-sync`
- [ ] `make lint-architecture` passes on current tree

### Phase 4: Validation
- [ ] End-to-end activation chain tested
- [ ] Return contract routing verified
- [ ] Regression tests pass

---

## 11. Architectural Decision Log

| ID | Decision | Rationale |
|----|----------|-----------|
| D-T01.03 | Executable `.md` files NOT exempt from compliance | `.md` extension ≠ documentation; SKILL.md is code |
| C-003 | Primary/fallback invocation hierarchy | Architectural clarity; one correct path |
| C-004 | REJECTED: `--invocation-mode` flag | YAGNI; internal routing, not user-facing |
| C-006 | `invocation_method` field in return contract | Observability without branching |

---

*Architecture Policy — SuperClaude Framework v2.01*
*Version 1.0.0 — 2026-02-24*
