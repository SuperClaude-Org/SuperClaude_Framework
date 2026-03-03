# v2.01 Architecture Refactor: Extracted Findings from Synthesis Planning

**Extraction Date:** 2026-02-24
**Source Files:**
- (A) `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/synthesis/dev-planning-synthesis-A.md`
- (B) `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/synthesis/dev-planning-synthesis-B.md`

**Filter Applied:** Only items relevant to the general architectural refactor (v2.01 scope). All roadmap-specific sprint items (adversarial pipeline wiring, `claude -p` headless invocation, specific task IDs T01.01-T06.05, specific decision artifacts D-0001 through D-0008) are excluded.

---

## 1. Three-Tier Loading Model (Architecture Policy)

**Source:** A (Section 4), B (Section 3 causal graph)
**v2.01 Relevance:** This is the foundational architecture that governs ALL commands and skills, not just roadmap.

### Tier Definitions

| Tier | Component | Loading Behavior | Size Constraint |
|------|-----------|-----------------|-----------------|
| 0 | Command | Auto-loaded on `/sc:<name>` invocation | Hard cap: 150 lines (WARN at 200, ERROR at 500) |
| 1 | Protocol Skill | Loaded via `Skill` tool invocation | No limit |
| 2 | Ref File | On-demand via `claude -p` | Self-contained, one concern per file |

**Core Metaphor:** "Commands are doors. Skills are rooms. Refs are drawers." (Source: A, Section 8.4)

### Rationale for Line Cap
- 150-line hard cap on commands ensures auto-loaded context stays minimal (Source: A, Section 8.4)
- Commands are auto-loaded every time a user types `/sc:<name>`, so bloated commands waste tokens on every invocation
- The cap forces behavioral logic into Protocol Skills where it is loaded on-demand

### Why This Matters for v2.01
The 3-tier model is a systemic policy that applies to every command/skill pair in the framework. The v2.01 refactor must enforce this model across all 5+ existing command/skill pairs and establish it as the standard for any future additions.

---

## 2. Naming Conventions

**Source:** A (Sections 4, 8.4), B (Section 3 causal graph)
**v2.01 Relevance:** General naming standard for all commands and skills.

### Convention Rules
- **Commands** use bare names: e.g., `adversarial.md`, `roadmap.md`, `cleanup-audit.md`
- **Protocol Skills** use `-protocol` suffix: e.g., `sc-adversarial-protocol/`, `sc-roadmap-protocol/`
- **Directory naming**: `sc-<name>-protocol/` pattern for all skill directories
- **Command != Skill name invariant**: The command name must differ from the skill name

### Critical Technical Reason
"The primary reason for the Command != Skill name invariant: Claude Code's Skill tool blocks re-entry if a skill with the same name is already running." (Source: A, Section 8.4)

This is a systemic Claude Code runtime constraint, not a stylistic choice. If a command and its associated skill share the same name, the Skill tool will refuse to load the skill because it interprets the command (already running) as the skill being re-entered.

### Affected Directories (All 5 Pairs)
| Old Name | New Name | Status |
|----------|----------|--------|
| `sc-adversarial` | `sc-adversarial-protocol` | Renamed (git RM) |
| `sc-cleanup-audit` | `sc-cleanup-audit-protocol` | Renamed (git RM) |
| `sc-roadmap` | `sc-roadmap-protocol` | Renamed (git RM) |
| `sc-task-unified` | `sc-task-unified-protocol` | Renamed (git RM) |
| `sc-validate-tests` | `sc-validate-tests-protocol` | Renamed (git RM) |

---

## 3. CI Enforcement Requirements

**Source:** A (Sections 4, 8.4), B (Section 8 Issue 4)
**v2.01 Relevance:** These are general-purpose checks for all commands/skills, not roadmap-specific.

### Planned `make lint-architecture` Target

10 automated checks defined (7 ERROR severity, 3 WARN severity). These enforce:
- **Bidirectional links** between commands and skills (every command must reference its skill, every skill must reference its command)
- **Line count limits** on command files (150 WARN, 500 ERROR)
- **Frontmatter completeness** in SKILL.md files
- **Sync integrity** between source and installed locations

### Current Status
**NOT YET IMPLEMENTED** in the Makefile. (Source: A Section 4, B Section 8 Issue 4)

The gap between policy and enforcement is flagged as a risk: "The gap between policy and enforcement creates a window where violations can accumulate." (Source: B, Issue 4)

### v2.01 Action Required
Implementing `make lint-architecture` is a core v2.01 deliverable. Without it, the naming conventions and line caps are advisory only.

---

## 4. Compliance Tier Framework for Executable Markdown

**Source:** A (Sections 3, 8.5), B (Section 3 causal graph)
**v2.01 Relevance:** Systemic policy decision affecting how the compliance system classifies ALL `.md` files that contain executable specifications.

### The Decision
Executable `.md` files (commands, SKILL.md files, protocol definitions) are **NOT exempt** from compliance enforcement, even though the compliance system's auto-classifier has an `*.md` EXEMPT booster.

### Why This Matters
The existing compliance tier system (documented in COMMANDS.md and ORCHESTRATOR.md) has a context booster that pushes `*.md` files toward EXEMPT classification:

```
| all doc files | EXEMPT | +0.5 | Docs are read-only equivalent |
```

This booster is inappropriate for executable specification files like commands and skills, which contain behavioral logic that agents must follow. The v2.01 refactor must either:
1. Add an exception to the EXEMPT booster for files under `commands/` and `skills/` paths, or
2. Restructure the auto-classifier to distinguish between documentation markdown and executable specification markdown

### Downstream Impact
This decision affects the compliance tier assigned to any task that modifies command or skill files. Without the fix, agents may treat command/skill edits as EXEMPT (no validation required) when they should be STANDARD or STRICT.

---

## 5. Architecture Policy Document Duplication Issue

**Source:** A (Section 4), B (Sections 5, 8 Issue 2)
**v2.01 Relevance:** General structural problem about canonical source of truth for architecture documents.

### The Problem
The architecture policy exists in two byte-identical locations with no canonical authority designated:
- `docs/architecture/command-skill-policy.md`
- `src/superclaude/ARCHITECTURE.md`

"There is no symlink, no `make sync` target for this pair, and no note in either file about the other's existence." (Source: B, Issue 2)

### Risk
Future edits to one copy will not propagate to the other, causing drift between the documented policy and the developer-facing reference.

### Recommended Resolution (from both sources)
1. Designate one location as canonical (likely `docs/architecture/`)
2. Either symlink the other or add it to the existing `sync-dev` Makefile target
3. Add a note in each file referencing the other

---

## 6. Path Inconsistency Pattern (Systemic Bug)

**Source:** A (Section 5), B (Section 8 Issue 1 -- flagged as BLOCKING)
**v2.01 Relevance:** This is a general pattern where internal references become stale after renames, not specific to the roadmap tasklist.

### The Pattern
When directories are renamed (e.g., `sc-adversarial` to `sc-adversarial-protocol`), internal references in other files are not automatically updated. This creates broken cross-references.

### Systemic Lesson
Any v2.01 rename operation must include a grep-sweep for old paths across:
- Tasklist files
- SKILL.md files (frontmatter references to commands)
- Command files (references to skill directories)
- Documentation files
- Makefile targets
- Test fixtures

### Detection Method
`grep -r "sc-adversarial/" --include="*.md"` (and similar for each renamed directory) should return zero results after a rename is complete.

---

## 7. Oversized Command Files Backlog

**Source:** A (Section 4, 8.4)
**v2.01 Relevance:** General enforcement of the 150-line cap across all commands.

### Status
6 command files are identified as oversized (exceeding the 150-line cap) and queued for splitting. These are listed as medium/low priority backlog items in the architecture policy.

### v2.01 Action
Identify and split all command files exceeding 150 lines. Each oversized command needs its behavioral logic moved into its corresponding Protocol Skill, leaving the command as a slim entry point.

---

## 8. Migration Phases (General Framework)

**Source:** A (Section 4), B (Section 3 causal graph)
**v2.01 Relevance:** The 4-phase migration is the general execution framework for the architecture refactor.

### Phase Status

| Phase | Description | Status | v2.01 Scope |
|-------|-------------|--------|-------------|
| 1 | Rename skill directories to `-protocol` suffix | EXECUTED | Yes -- complete |
| 2 | Refactor command files (trim to 150 lines, update references) | IN PROGRESS | Yes -- core deliverable |
| 3 | Build system updates (`make lint-architecture`) | NOT STARTED | Yes -- core deliverable |
| 4 | Validate (run CI checks, confirm all links resolve) | BLOCKED on Phase 3 | Yes -- core deliverable |

### Dependencies
- Phase 2 depends on Phase 1 (renames must be done before command references can be updated)
- Phase 3 depends on the policy document defining what checks to implement
- Phase 4 depends on Phase 3 (can't validate without the validation tooling)

---

## 9. Lessons Learned: Why Agents Weren't Following Instructions

**Source:** A (Section 4), B (Section 8 Issues 1, 4)
**v2.01 Relevance:** Systemic insights about framework compliance gaps.

### Root Causes Identified

1. **Auto-loaded context bloat**: When commands exceed 150 lines, agents receive excessive context on every invocation, increasing the chance they ignore or misinterpret parts of it. The 150-line cap is a direct response to this. (Source: A, Section 4)

2. **Naming collision causing tool re-entry blocks**: When a command and skill shared the same name, the Skill tool would refuse to load the skill, silently failing. Agents would then proceed without the skill's behavioral instructions. The `-protocol` suffix naming convention prevents this. (Source: A, Section 8.4)

3. **Missing enforcement mechanisms**: Without `make lint-architecture`, there was no automated way to detect when commands grew too large, when links between commands and skills broke, or when frontmatter was incomplete. Agents could drift from the intended architecture without any CI signal. (Source: B, Issue 4)

4. **Compliance misclassification of executable markdown**: The compliance system's EXEMPT booster for `.md` files meant that changes to command and skill files could be classified as exempt from validation, allowing agents to make unvalidated changes to behavioral specifications. (Source: A, Section 8.5)

---

## 10. Unresolved High-Priority Items

**Source:** A (Section 4), B (Section 8 Issue 5)
**v2.01 Relevance:** These items affect the general architecture, not just roadmap.

### Item 1: Tier 2 Ref Loader Script
- **Priority:** HIGH
- **Description:** Design the `claude -p` script that loads Tier 2 ref files on demand
- **Impact:** Full 3-tier model is incomplete without this; currently only Tier 0 and Tier 1 are operational
- **v2.01 Decision Needed:** Is this in scope for v2.01, or deferred to a later release?

### Item 2: Cross-Skill Invocation Patterns
- **Priority:** HIGH
- **Description:** Define how one skill can invoke another skill
- **Impact:** Without this, skills operate in isolation; complex workflows requiring multiple skills cannot be composed
- **v2.01 Decision Needed:** Is this in scope for v2.01, or deferred?

---

## 11. Quality Standards Extracted

**Source:** A (Section 8.4), B (Section 5)
**v2.01 Relevance:** General quality standards for all commands/skills.

### Command File Standards
- Maximum 150 lines (hard cap)
- Must contain a reference to its associated Protocol Skill
- Must be a "slim entry point" -- behavioral logic belongs in the skill

### SKILL.md Standards
- Must have complete frontmatter
- Must contain a reference back to its associated command
- Inline YAML limited to 20 lines (per architecture policy)

### Build System Standards
- `make lint-architecture` must enforce all 10 CI checks
- `make sync-dev` must keep `src/` and `.claude/` in sync
- `make verify-sync` must validate sync state (CI-friendly, non-destructive)

### Document Management Standards
- Single canonical location for each policy document
- Derived copies managed via symlinks or sync targets
- No macOS Finder duplicates (space-containing filenames are forbidden)
