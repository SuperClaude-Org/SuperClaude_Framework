# v2.01 Architecture Refactor: Extracted Findings from Rollback Analysis

**Source files:**
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/context/commands-to-planning.md`
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/context/skill-renames-to-planning.md`

**Extraction date:** 2026-02-24
**Filter:** Only systemic architectural findings relevant to v2.01. All v2.02-specific roadmap sprint details, D-xxxx artifact references, and task linkages excluded.

---

## 1. Traceability Gap: Only 1/5 Commands Had Full Traceability

Of 5 commands modified during the prior release attempt, only `roadmap.md` had a complete traceability chain (tasklist task, decision artifact, evidence record). The other 4 commands (adversarial, cleanup-audit, task-unified, validate-tests) had **zero** formal tracking -- no task, no artifact, no evidence.

| Command | Tasklist Task | Decision Artifact | Evidence Record |
|---------|:---:|:---:|:---:|
| adversarial.md | NO | NO | NO |
| cleanup-audit.md | NO | NO | NO |
| roadmap.md | YES | YES | YES |
| task-unified.md | NO | NO | NO |
| validate-tests.md | NO | NO | NO |

**v2.01 requirement:** Every file modification in a release must trace to a task. Architecture policy mandates are not a substitute for task tracking. If a policy drives changes beyond the sprint scope, those changes must either (a) be added as explicit tasks in the current sprint, or (b) be deferred to a dedicated sprint.

---

## 2. Scope Expansion: Planned 4 Files, Actual 68

The prior sprint planned to modify 4 files across 3 skill packages. The actual implementation touched 68 files:

- 10 command files (5 commands x 2 locations: `src/` and `.claude/`)
- 30 skill files renamed
- 1 Makefile
- 2 documentation files created
- 25 new `.claude/skills/` dev copies

**v2.01 requirement:** Task decomposition must account for the full scope of architecture policy mandates before sprint start. If a policy's migration checklist implies N files, the sprint plan must enumerate all N files, not just the subset the sprint originally intended to touch. Scope boundaries must be explicit: "this sprint executes Phase 1 steps 1-3 for skills X and Y only" rather than leaving the policy as an implicit mandate covering everything.

---

## 3. Policy-Driven Renames Without Task Tracking (4/5)

Of 5 skill directory renames (`sc-{name}` to `sc-{name}-protocol`), only the roadmap rename had associated sprint tasks. The other 4 were driven solely by the architecture policy document with no task decomposition.

| Skill Rename | Had Sprint Task | Driving Authority |
|---|:---:|---|
| sc-adversarial -> sc-adversarial-protocol | NO | Architecture policy only |
| sc-cleanup-audit -> sc-cleanup-audit-protocol | NO | Architecture policy only |
| sc-roadmap -> sc-roadmap-protocol | YES | Sprint tasks + architecture policy |
| sc-task-unified -> sc-task-unified-protocol | NO | Architecture policy only |
| sc-validate-tests -> sc-validate-tests-protocol | NO | Architecture policy only |

**v2.01 requirement:** Policy-mandated changes must be decomposed into trackable tasks. A policy document is an authority for *what* must change, but it does not replace *task tracking* of when and how each change is executed. Each rename (including companion files) should be a discrete task with verification criteria.

---

## 4. Allowed-Tools Inconsistency Pattern

A systemic inconsistency exists across command frontmatter:

- `roadmap.md` uses an `allowed-tools` field in its frontmatter
- The other 4 commands use `mcp-servers` instead (or have no frontmatter at all)
- All 5 commands now contain an `## Activation` section that invokes the `Skill` tool
- For 4/5 commands, `Skill` is NOT listed in any tool whitelist

This creates a latent bug: if Claude Code enforces frontmatter tool whitelists, 4 commands will fail when attempting to invoke their protocol skill.

**Specific instances:**
- `adversarial.md`: Uses `mcp-servers` field, no `allowed-tools`. Activation section calls `Skill`.
- `cleanup-audit.md`: Uses `mcp-servers` and `personas` fields, no `allowed-tools`. Activation section calls `Skill`.
- `task-unified.md`: Frontmatter uses `name: task` (not `task-unified`), inconsistent with skill name `sc:task-unified-protocol`.
- `validate-tests.md`: Has no YAML frontmatter at all.

**v2.01 requirement:** Define a single canonical command frontmatter schema. All commands must use the same field names and structure. If `allowed-tools` is the correct field, all commands must have it. If `Skill` tool is required for activation, it must appear in the whitelist. This is a systemic consistency problem, not a per-command fix.

---

## 5. Command-Skill Linkage Requirements

From the architecture policy and observed patterns, a valid command-skill pair requires:

### Naming Convention
- Command file: `{name}.md` (e.g., `adversarial.md`)
- Skill directory: `sc-{name}-protocol/` (e.g., `sc-adversarial-protocol/`)
- SKILL.md `name` field: `sc:{name}-protocol` (e.g., `sc:adversarial-protocol`)

### Required Command Elements
1. `## Activation` section containing `Skill sc:{name}-protocol` directive
2. "Do NOT proceed without loading this skill" warning
3. `Skill` listed in the command's tool whitelist (currently broken for 4/5 commands)
4. Command <= 150 lines total
5. No inline protocol content (YAML blocks, step definitions, scoring algorithms)

### Required Skill Elements
1. SKILL.md with frontmatter including `name`, `description`, `allowed-tools`
2. `allowed-tools` must include `Skill` if cross-skill invocation is needed
3. `__init__.py` Python package marker
4. Companion files in `refs/`, `rules/`, `templates/`, `scripts/` subdirectories as needed

### Pre-Existing Inconsistencies to Resolve
- `task-unified.md` frontmatter `name` is `task`, not `task-unified` -- mismatches the skill name pattern
- `cleanup-audit` SKILL.md previously lacked the `sc:` prefix in its name field (was `cleanup-audit`, should be `sc:cleanup-audit-protocol`)
- `validate-tests.md` has no frontmatter at all

**v2.01 requirement:** Codify the command-skill pair contract as a checkable schema. Each pair must pass a validation check that verifies naming alignment, activation section presence, tool whitelist completeness, and frontmatter schema compliance.

---

## 6. Companion File Inventory Pattern

When a skill directory is renamed, ALL files within it must move. The observed companion file types are:

| File Type | Examples | Typical Count |
|---|---|---|
| `__init__.py` | Python package marker | 1 per skill |
| `refs/*.md` | Reference documentation | 0-5 per skill |
| `rules/*.md` | Rule definitions | 0-5 per skill |
| `templates/*.md` | Output templates | 0-4 per skill |
| `scripts/*.sh` | Utility scripts | 0-1 per skill |
| `*.yaml` | Configuration/specification | 0-1 per skill |

### Actual counts from the 5 renames:

| Skill | SKILL.md | Companions | Total Files |
|---|---|---|---|
| sc-adversarial-protocol | 1 | 5 (1 init + 4 refs) | 6 |
| sc-cleanup-audit-protocol | 1 | 11 (1 init + 5 rules + 1 script + 4 templates) | 12 |
| sc-roadmap-protocol | 1 | 6 (1 init + 5 refs) | 7 |
| sc-task-unified-protocol | 1 | 1 (1 init) | 2 |
| sc-validate-tests-protocol | 1 | 2 (1 init + 1 yaml) | 3 |
| **Grand Total** | **5** | **25** | **30** |

**v2.01 requirement:** Task planning for any skill rename must enumerate all companion files. The task estimation should account for: SKILL.md modification + N companion file moves + internal cross-references that may contain the old path. The validate-tests command had a stale internal reference (`skills/sc-validate-tests/classification-algorithm.yaml`) that was missed during the rename -- proving that companion file enumeration alone is insufficient; internal path references must also be audited.

---

## 7. Architecture Policy Enforcement Gaps

The architecture policy (`command-skill-policy.md`) defines 10 CI enforcement checks via `make lint-architecture`. However:

1. **Build system incomplete**: The `lint-architecture` Makefile target was added but the full Phase 3 (Build System) was never completed
2. **No checkpoints for Phases 3-6**: Only Phases 1-2 have checkpoint records
3. **Lint target never formally run**: No evidence record shows `make lint-architecture` was executed against the modified files
4. **4/5 commands have zero validation evidence**: Only `roadmap.md` has grep-verified evidence

### The 10 Planned CI Checks (for v2.01 to implement)
1. Skill directory without matching SKILL.md
2. SKILL.md without `allowed-tools` frontmatter
3. Command file >200 lines (WARN)
4. Command file >500 lines (ERROR)
5. SKILL.md `allowed-tools` missing required tools
6. Command with matching `-protocol` skill directory missing `## Activation` section
7. `## Activation` section not containing `Skill sc:{name}-protocol`
8. SKILL.md `allowed-tools` missing `Skill` when cross-skill invocation exists
9. Skill directory `sc-*-protocol/` but SKILL.md `name` field doesn't end in `-protocol`
10. Command frontmatter schema validation

**v2.01 requirement:** The architecture policy's enforcement checks must be implemented as actual runnable validation before any migration work begins. Policy without enforcement produces the gaps observed here: 4/5 commands modified without any automated verification that the modifications are correct.

---

## 8. Content Extraction Risk Pattern

The `task-unified.md` command underwent an 81% content extraction (567 lines reduced to 106 lines, 461 lines removed). This was the single largest and riskiest change, yet it had:

- No tasklist task
- No decision artifact
- No evidence record
- No verification that extracted content landed correctly in the skill

The architecture policy had explicitly placed this as a "Low" priority backlog item, but it was executed during the sprint anyway.

**v2.01 requirement:** Content extraction (moving logic from command to skill) is a high-risk operation that requires:
1. Explicit task tracking with acceptance criteria
2. Pre-extraction inventory of what content exists in the command
3. Post-extraction verification that the skill contains the full extracted content
4. Validation that the command's activation section correctly delegates to the skill
5. Backlog items must not be executed during a sprint unless formally added to the sprint scope

---

## Summary: v2.01 Architecture Requirements Derived from These Findings

| # | Requirement | Source Finding |
|---|---|---|
| 1 | Every file modification must trace to a tracked task | Traceability gap (Section 1) |
| 2 | Sprint plans must enumerate all files implied by policy mandates | Scope expansion (Section 2) |
| 3 | Policy-driven changes must decompose into discrete tracked tasks | Untracked renames (Section 3) |
| 4 | Define and enforce a single canonical command frontmatter schema | Allowed-tools inconsistency (Section 4) |
| 5 | Codify command-skill pair contract as a checkable schema | Linkage requirements (Section 5) |
| 6 | Skill rename tasks must enumerate all companions + audit internal references | Companion files (Section 6) |
| 7 | Implement CI enforcement checks before migration work begins | Policy enforcement gaps (Section 7) |
| 8 | Content extraction requires explicit tracking and post-extraction verification | Extraction risk (Section 8) |
