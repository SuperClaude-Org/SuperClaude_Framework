# v2.01 Architecture Refactor: Extracted Context from Rollback Analysis

**Source files**:
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/context/makefile-to-planning.md`
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/context/adversarial-to-framework.md`

**Extraction date**: 2026-02-24
**Filter**: Only items relevant to v2.01 (systemic architectural refactor: CI enforcement, build system, quality gates). All roadmap-specific adversarial pipeline details (SKILL.md changes, Wave 2 steps, convergence values) excluded.

---

## 1. CI Policy-to-Implementation Gap (from makefile-to-planning.md)

### 1.1 The 10-Check Policy vs 6-Check Implementation

The architecture policy (`docs/architecture/command-skill-policy.md`, Section "CI Enforcement") defines **10 CI checks** for `make lint-architecture`. The Makefile implements **6 checks** covering 8 of the 10 policy requirements.

**Implemented checks (6 in Makefile, covering 8 policy items)**:

| Makefile Check | Policy # | Rule | Severity |
|---|---|---|---|
| Check 1: Command -> Skill bidirectional link | #1 | Command with `## Activation` referencing a skill -> that skill directory MUST exist | ERROR |
| Check 2: Skill -> Command bidirectional link | #2 | Skill directory matching `sc-*-protocol` -> command `<name>.md` MUST exist | ERROR |
| Check 3: Command size limits | #3 + #4 (combined) | >200 lines = WARN, >500 lines = ERROR | ERROR/WARN |
| Check 4: Activation section present | #6 | Command with matching `-protocol` skill directory missing `## Activation` section | ERROR |
| Check 5: Skill frontmatter validation | #8 | SKILL.md missing `name`, `description`, or `allowed-tools` in frontmatter | ERROR |
| Check 6: Protocol naming consistency | #9 | Skill directory `sc-*-protocol/` but SKILL.md `name` field doesn't end in `-protocol` | ERROR |

**Missing checks (2 genuinely unimplemented)**:

| Policy # | Description | Severity | Reason Missing |
|---|---|---|---|
| **#5** | Inline protocol detection: command with matching `-protocol` skill contains YAML code blocks >20 lines | ERROR | Requires YAML block detection in markdown -- more complex than simple grep/wc checks |
| **#7** | Activation reference correctness: `## Activation` section does not contain `Skill sc:<name>-protocol` | ERROR | Partially covered by Check 1 (validates directory exists) but does NOT validate the reference matches expected naming pattern |

**Accounting notes**:
- Policy #3/#4 are two separate checks (WARN at 200, ERROR at 500) but implemented as one Makefile check with two thresholds.
- Policy #10 (sync integrity) is delegated to the existing `make verify-sync` target rather than duplicated in `lint-architecture`.

**v2.01 action item**: The policy's Migration Checklist Phase 4 expects "all 10 checks pass." Checks #5 and #7 must be implemented to close this gap.

### 1.2 Analysis Agent Discrepancy Pattern

The `dev-planning-synthesis-A.md` incorrectly reported `lint-architecture` as "not yet implemented" and Phase 3 as "NOT STARTED." The git diff proves both are implemented. Root cause: the synthesis agents read the policy document's self-reported migration status rather than verifying against the actual branch state. The `framework-synthesis-A.md` and `framework-synthesis-B.md` (produced from actual file diffs) correctly identified the target as present.

**v2.01 lesson**: Analysis processes must verify claims against actual codebase state, not trust document self-reports.

---

## 2. sync-dev / verify-sync Architectural Requirements (from makefile-to-planning.md)

### 2.1 Skill-Skip Heuristic Removal

The old `sync-dev` and `verify-sync` targets contained a heuristic that skipped syncing skills when a matching command file existed:

```bash
# OLD LOGIC (removed):
cmd_name=${skill_name#sc-};
if [ "$cmd_name" != "$skill_name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    continue;  # Skip -- skill "served by" command
fi;
```

This was removed because:

1. **Conceptual obsolescence**: The old model treated commands and skills as substitutes. The new tiered architecture treats them as complementary layers ("Commands are doors. Skills are rooms."). Both must exist for the activation chain to function.
2. **Future-proofing**: The `-protocol` suffix naming convention happens to break the heuristic naturally, but skills without `-protocol` would still be incorrectly skipped.
3. **Policy mandate**: `command-skill-policy.md` Migration Checklist Phase 3 explicitly requires removal.

### 2.2 verify-sync Policy Additions

The policy's "CI Enforcement" section requires `verify-sync` to:
- Remove the "served by command" skip message
- Always check skill directories against `.claude/skills/`
- Validate `-protocol` naming convention

### 2.3 Traceability Gap

The Makefile changes were implemented but NOT tracked as tasklist tasks. Phase 3 was not decomposed into individual tasks in the tasklist. This suggests implementation occurred outside formal task tracking.

**v2.01 action item**: Ensure all build system changes are tracked as explicit tasks in the v2.01 tasklist.

---

## 3. lint-architecture Target Requirements (from makefile-to-planning.md)

### 3.1 What It Enforces

The `lint-architecture` target enforces the command-skill tiered architecture policy through automated CI checks. It is driven by `docs/architecture/command-skill-policy.md`.

**Core enforcements**:
- Bidirectional linking between commands and skills (commands reference skills that exist; skills have corresponding commands)
- Command file size limits (prevent protocol content leaking into thin command dispatchers)
- Activation section presence in commands with protocol skills
- Skill frontmatter completeness (name, description, allowed-tools)
- Protocol naming convention consistency (directory name suffix matches SKILL.md name field)

### 3.2 Policy-to-Implementation Mapping Methodology

The traceability chain established in the analysis:

```
docs/architecture/command-skill-policy.md (POLICY SOURCE)
    |
    +-- "Core Principle" section
    |       -> Obsoletes skill-skip heuristic
    |       -> Drives removal of 9 lines from sync-dev + verify-sync
    |
    +-- "Naming Convention" section (-protocol suffix)
    |       -> Drives lint-architecture Check 6
    |       -> Makes old heuristic behaviorally irrelevant
    |
    +-- "CI Enforcement" section (10 checks defined)
    |       -> Drives lint-architecture target (113 lines)
    |       -> 6 of 10 implemented; 2 delegated/combined; 2 deferred
    |
    +-- "Migration Checklist > Phase 3" (Build System)
    |       -> Remove skip logic from sync-dev        [DONE]
    |       -> Add lint-architecture target            [DONE, 6/10]
    |       -> Update verify-sync to remove skip       [DONE]
    |
    +-- "Migration Checklist > Phase 4" (Validate)
            -> All 10 checks pass                      [PARTIAL, 6 checks]
```

**v2.01 relevance**: This policy-to-implementation traceability pattern is the model for how v2.01 should document its own CI enforcement decisions.

---

## 4. Adversarial Review as a General Quality Process (from adversarial-to-framework.md)

### 4.1 The Spec Evolution Pattern (Reusable Process)

The adversarial pipeline followed a repeatable process for evolving specifications through structured quality review:

```
Multiple competing approaches (3 independent designs)
    |
    v
Structured debate (12 convergence decisions, scored rubric)
    |
    v
Base selection + absorption plan (best approach + cherry-picked elements)
    |
    v
Merged approach (unified design with provenance annotations)
    |
    v
Specification draft v1 (formal spec, addressed 10 reflection issues)
    |
    v
Panel review (6 expert reviewers, 27 findings: 4 CRITICAL, 11 MAJOR)
    |
    v
Specification draft v2 (all 27 findings addressed)
    |
    v
Implementation specs (atomic, task-level specifications)
```

**v2.01 relevance**: This is a reusable process template for any architectural decision requiring structured quality review. The key stages are:
1. **Competitive approach generation** (multiple independent designs)
2. **Structured evaluation** (scored rubric, explicit selection criteria)
3. **Selective synthesis** (best base + absorbed strengths from others)
4. **Independent panel review** (multi-expert, severity-classified findings)
5. **Evidence-based revision** (every finding addressed, traceable)

### 4.2 The "Intentional Gap" Design Pattern

A design pattern was identified where a threshold is deliberately set above a sentinel value to create a forced quality gate:

**Pattern**: When a process cannot measure a quality metric directly (e.g., convergence during fallback execution), a fixed sentinel value is emitted that is deliberately below the routing threshold. This ensures results from the unmeasured path always trigger the cautious routing branch (user confirmation or abort), rather than being silently accepted.

**Abstract formulation**:
- `sentinel_value < routing_threshold` (by design)
- Unmeasured results always take the conservative path
- Measured results can exceed the threshold and proceed automatically

**v2.01 relevance**: This is a general safety pattern applicable to any quality gate where some execution paths cannot compute the gate's metric. Rather than skipping the gate or using a pass-through value, the sentinel forces conservative behavior.

### 4.3 The 15-Implemented vs 8-Pending Categorization Method

The analysis categorized spec requirements into:

| Category | Count | Description |
|---|---|---|
| **Implemented** | 15 | Core protocol, routing logic, structural changes |
| **Not implemented (applicable)** | 8 | Schema refinements, validation checks, tooling |
| **Not applicable** | 5 | Related to unavailable execution paths |
| **Never created** | 3 | Referenced files that were never produced |

**v2.01 relevance**: This categorization method is useful for any implementation audit:
1. **Implemented**: Verify these match the spec exactly
2. **Not implemented (applicable)**: These are the backlog -- prioritize by impact (HIGH/MEDIUM/LOW)
3. **Not applicable**: Document why, so future reviewers don't flag as gaps
4. **Never created**: Decide whether to create or remove references

The priority classification used (HIGH = correctness/safety, MEDIUM = robustness, LOW = documentation/tooling) provides a standard triage framework.

---

## 5. Summary of v2.01 Action Items Extracted

| # | Action Item | Source | Priority |
|---|---|---|---|
| 1 | Implement `lint-architecture` Check #5 (inline YAML block detection) | makefile-to-planning.md, Section 3 | HIGH |
| 2 | Implement `lint-architecture` Check #7 (activation reference correctness) | makefile-to-planning.md, Section 3 | HIGH |
| 3 | Track all build system changes as explicit tasklist items | makefile-to-planning.md, Section 5 | MEDIUM |
| 4 | Adopt policy-to-implementation traceability methodology | makefile-to-planning.md, Section 7 | MEDIUM |
| 5 | Adopt spec evolution process template for architectural decisions | adversarial-to-framework.md, Section 2 | MEDIUM |
| 6 | Apply "intentional gap" pattern to quality gates with unmeasured paths | adversarial-to-framework.md, Section 4 | LOW |
| 7 | Use 4-category implementation audit method for spec compliance | adversarial-to-framework.md, Section 3 | LOW |
| 8 | Verify analysis claims against codebase state, not document self-reports | makefile-to-planning.md, Section 4 | MEDIUM |
