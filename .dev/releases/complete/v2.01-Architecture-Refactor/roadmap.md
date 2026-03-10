---
spec_source: .dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md
generated: 2026-02-24T00:00:00Z
generator: sc:roadmap
complexity_score: 0.727
complexity_class: HIGH
domain_distribution:
  backend: 40
  infrastructure: 25
  architecture: 20
  documentation: 10
  quality: 5
primary_persona: architect
consulting_personas: [backend, devops]
milestone_count: 10
milestone_index:
  - id: M1
    title: "Foundation & Environment Probe"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Medium
  - id: M2
    title: "Foundation Validation"
    type: TEST
    priority: P3
    dependencies: [M1]
    deliverable_count: 2
    risk_level: Low
  - id: M3
    title: "Invocation Wiring & Activation Fix"
    type: FEATURE
    priority: P0
    dependencies: [M1, M2]
    deliverable_count: 6
    risk_level: High
  - id: M4
    title: "Invocation Wiring Validation"
    type: TEST
    priority: P3
    dependencies: [M3]
    deliverable_count: 2
    risk_level: Medium
  - id: M5
    title: "Build System Enforcement"
    type: FEATURE
    priority: P0
    dependencies: [M4]
    deliverable_count: 4
    risk_level: Medium
  - id: M6
    title: "Build System Validation"
    type: TEST
    priority: P3
    dependencies: [M5]
    deliverable_count: 2
    risk_level: Low
  - id: M7
    title: "Structural Validation & Testing"
    type: TEST
    priority: P1
    dependencies: [M5, M6]
    deliverable_count: 3
    risk_level: High
  - id: M8
    title: "Structural Validation Review"
    type: TEST
    priority: P3
    dependencies: [M7]
    deliverable_count: 2
    risk_level: Low
  - id: M9
    title: "Polish, Integration & Closure"
    type: FEATURE
    priority: P1
    dependencies: [M7]
    deliverable_count: 8
    risk_level: Medium
  - id: M10
    title: "Final Release Validation"
    type: TEST
    priority: P1
    dependencies: [M9]
    deliverable_count: 3
    risk_level: Medium
total_deliverables: 36
total_risks: 7
estimated_phases: 6
validation_score: 0.898
validation_status: PASS
---

# Roadmap: v2.01 Architecture Refactor

## Overview

This roadmap structures the v2.01 Architecture Refactor of the SuperClaude Framework into 10 milestones with 1:1 validation interleaving (HIGH complexity class). The refactor enforces a 3-tier separation model — Commands (doors), Skills (rooms), Refs (drawers) — to fix root causes of agents not following `/sc:command` instructions.

The roadmap follows the spec's 6-phase plan and execution DAG (§13.7), organizing 18 tasks and 6 bug fixes into work milestones with validation checkpoints after each. All work starts from commit `5733e32` (rollback point). No prior implementation work is trusted.

Key architectural decisions carried forward: FALLBACK-ONLY variant (D-0001/D-0002), Task agent dispatch as sole viable invocation mechanism, 10-field canonical return contract schema, and `-protocol` suffix naming convention for all paired skills.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Environment Probe | FEATURE | P0 | S | None | 4 | Medium |
| M2 | Foundation Validation | TEST | P3 | XS | M1 | 2 | Low |
| M3 | Invocation Wiring & Activation Fix | FEATURE | P0 | M | M1, M2 | 6 | High |
| M4 | Invocation Wiring Validation | TEST | P3 | S | M3 | 2 | Medium |
| M5 | Build System Enforcement | FEATURE | P0 | S | M4 | 4 | Medium |
| M6 | Build System Validation | TEST | P3 | XS | M5 | 2 | Low |
| M7 | Structural Validation & Testing | TEST | P1 | M | M5, M6 | 3 | High |
| M8 | Structural Validation Review | TEST | P3 | XS | M7 | 2 | Low |
| M9 | Polish, Integration & Closure | FEATURE | P1 | L | M7 | 8 | Medium |
| M10 | Final Release Validation | TEST | P1 | S | M9 | 3 | Medium |

## Dependency Graph

```
M1 → M2 → M3 → M4 → M5 → M6
                M5 → M7 → M8
                M6 → M7
                      M7 → M9 → M10
```

**Critical path**: M1 → M3 → M4 → M5 → M7 → M9 → M10

---

## M1: Foundation & Environment Probe

### Objective

Validate the development environment, run the Skill tool probe to confirm FALLBACK-ONLY variant, and establish tier classification policy for executable `.md` files.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | T01.01: Skill tool probe re-run in current environment | Probe result documented; variant decision (FALLBACK-ONLY or updated) recorded |
| D1.2 | T01.02: Prerequisite validation — all files exist, build targets valid, branch state clean | Day 1 verification procedure (§15) passes; no rogue-agent staged changes |
| D1.3 | T01.03: Tier classification policy — executable `.md` files are STANDARD minimum (Rule 7.6) | Classification documented; downstream task compliance tiers assigned |
| D1.4 | Verify/create architecture policy document at `docs/architecture/command-skill-policy.md` (FR-001, Layer 0) | File exists and is non-empty; content matches v1.0.0 policy spec |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-002: Rogue agent staged changes | Medium | High | Run `git status` first; treat all staged files as untrusted; verify against §15 |
| R-003: Probe result changed | Low | Medium | Re-run probe empirically; document result regardless of outcome |

---

## M2: Foundation Validation

### Objective

Verify all foundation outputs are correct and the environment is ready for invocation wiring work.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Probe result verification: confirm D-0001 still holds or document new variant | Variant decision is deterministic and reproducible |
| D2.2 | Branch state clean: no untrusted staged changes, all prerequisites verified | `git status` shows clean working tree (only expected modifications) |

### Dependencies

- M1: Foundation outputs must exist

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Foundation outputs incomplete | Low | Medium | Re-run M1 tasks if verification fails |

---

## M3: Invocation Wiring & Activation Fix

### Objective

Fix the primary invocation chain for `sc:roadmap` by adding `Skill` to `allowed-tools`, rewriting the `## Activation` section, and decomposing Wave 2 Step 3 into 6 atomic sub-steps with fallback protocol.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | T02.01: Add `Skill` to `roadmap.md` `allowed-tools` frontmatter (BUG-001 partial) | `Skill` present in `allowed-tools` list |
| D3.2 | T02.02: Add `Skill` to `sc-roadmap-protocol/SKILL.md` `allowed-tools` (BUG-001 partial) | `Skill` present in `allowed-tools` list |
| D3.3 | T02.04: Rewrite `roadmap.md` `## Activation` to reference `Skill sc:roadmap-protocol` (BUG-006) | `## Activation` contains exact string `Skill sc:roadmap-protocol` |
| D3.4 | T02.03: Decompose Wave 2 Step 3 into sub-steps 3a-3f with explicit tool bindings | 6 sub-steps with verb→tool mapping for each |
| D3.5 | Fallback protocol F1/F2-3/F4-5 fully specified with convergence routing | 3-status routing (Pass ≥0.6, Partial ≥0.5, Fail <0.5) implemented |
| D3.6 | Rename 5 skill directories with `-protocol` suffix in `src/superclaude/skills/` (FR-002) | All 5 directories renamed; SKILL.md `name:` fields updated; `make sync-dev` copies created |

### Dependencies

- M1: Variant decision (FALLBACK-ONLY) determines sub-step design
- M2: Foundation must be validated before invocation wiring begins

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Partial application breaks invocations | High | High | Apply as atomic group (Group A pattern from §13.7); test end-to-end before marking complete |
| R-006: Context compaction drops Activation | Medium | High | "Do NOT proceed" warning in Activation section; test with fresh agent context |

---

## M4: Invocation Wiring Validation

### Objective

Validate the invocation wiring changes through the 8-point audit and end-to-end activation chain testing.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | 8-point structural audit of Wave 2 Step 3 (per §9) | All 8 audit points pass |
| D4.2 | End-to-end activation chain test: `/sc:roadmap` → `Skill sc:roadmap-protocol` → SKILL.md loads | Invocation chain completes without errors or silent skips |

### Dependencies

- M3: All invocation wiring changes complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-007: No test coverage for activation flow | High | Medium | Create manual activation test procedure; document expected behavior |

---

## M5: Build System Enforcement

### Objective

Implement CI enforcement infrastructure (`make lint-architecture`) before any structural migration work, per Rule 7.5: enforcement before migration.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | T03.01: Remove skill-skip heuristic from `sync-dev` and `verify-sync` in Makefile | Old 4-line and 5-line heuristics removed; all skills synced including `-protocol` |
| D5.2 | T03.02: Add `lint-architecture` target to Makefile implementing 6 designed checks (#1-4, #6, #8-9) | Target exists, runs all 6 checks, exits 1 on ERROR |
| D5.3 | T03.03: Run `make lint-architecture` against current tree | Exit 0 (all ERRORs resolved) |
| D5.4 | Makefile `.PHONY` and `help` targets updated to reference `lint-architecture` | New target discoverable via `make help` |

### Dependencies

- M4: Invocation wiring must be validated before build system changes

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-005: 4 unimplemented CI checks leave gaps | Medium | Medium | Document which 4 checks (#5, #7, #10 delegated, plus 1 more) are deferred; track as known gap |
| Lint errors on current tree | Medium | Medium | Fix blocking errors in M5 scope; non-blocking warnings documented |

---

## M6: Build System Validation

### Objective

Verify the build system enforcement infrastructure works correctly for both positive and negative cases.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Positive lint test: `make lint-architecture` exits 0 on compliant tree | Exit code 0 with all 6 checks passing |
| D6.2 | Negative lint test: verify `make lint-architecture` fails when skill is missing or `## Activation` absent | Exit code 1 with appropriate error message |

### Dependencies

- M5: lint-architecture target must exist

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False positives/negatives in lint checks | Low | Medium | Test with known-good and known-bad fixtures |

---

## M7: Structural Validation & Testing

### Objective

Implement integration tests for return contract routing, adversarial pipeline integration, and artifact gate specifications.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | T04.01: Return contract consumer routing tests — validate Pass/Partial/Fail paths with convergence thresholds (0.6/0.5) | Tests pass for all 3 routing paths plus edge cases (missing file, parse error) |
| D7.2 | T04.02: Adversarial pipeline integration tests — verify fallback protocol F1/F2-3/F4-5 | End-to-end fallback path produces valid return-contract.yaml |
| D7.3 | T04.03: Artifact gate specification and standards | Gates defined for all 3 output artifacts (roadmap.md, extraction.md, test-strategy.md) |

### Dependencies

- M5: Build system enforcement must be in place
- M6: Build system must be validated

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Partial application during testing | High | High | Run tests in isolated environment; verify atomicity |
| R-007: Test coverage gaps | High | Medium | Prioritize activation flow tests; document untested paths |

---

## M8: Structural Validation Review

### Objective

Review all structural validation results and confirm the codebase is ready for polish and integration work.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D8.1 | All M7 tests pass with documented results | Test report with pass/fail counts and coverage metrics |
| D8.2 | No Critical or Major issues from M7 testing | Zero Critical issues; any Major issues resolved before proceeding |

### Dependencies

- M7: All structural validation tests complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Major issues discovered | Medium | Medium | Allocate rework budget; fix before proceeding to M9 |

---

## M9: Polish, Integration & Closure

### Objective

Complete all remaining Phase 5 and Phase 6 tasks: documentation, remaining command updates, bug fixes, and major extraction work.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D9.1 | T05.01: Verb-to-tool glossary created | Glossary disambiguates "Invoke" (Bash/`claude -p`), "Dispatch" (Task tool), "Load" (Read tool) |
| D9.2 | T05.02: Wave 1A Step 2 semantic alignment fix | Step 2 semantics match the updated return contract schema |
| D9.3 | T05.03: Pseudo-CLI invocation conversion | All pseudo-CLI patterns converted to executable patterns |
| D9.4 | T06.01: Cross-skill invocation pattern documentation | Document explains Task agent wrapper, Skill tool direct, and `claude -p` patterns |
| D9.5 | T06.02: Tier 2 ref loader design (`claude -p` script) | Design document for ref loading mechanism; implementation deferred |
| D9.6 | T06.03: `task-unified.md` major extraction (567→106 lines) | Command file ≤106 lines; all protocol logic in `sc-task-unified-protocol/SKILL.md` |
| D9.7 | T06.04: Remaining 4 command files updated (adversarial, cleanup-audit, task-unified, validate-tests) — `## Activation` added + BUG-001 fixed | All 4 commands have `## Activation` and `Skill` in `allowed-tools` |
| D9.8 | T06.05-06: BUG-004 (policy dedup), BUG-002 (stale path), BUG-003 (threshold) resolved | All 3 bugs verified fixed with no regressions |

### Dependencies

- M7: Structural validation must pass before integration changes

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Partial application across 4 commands | High | High | Apply per-command atomic groups (Group A from §13.7); sync after each |
| D9.6 functional regression | Medium | Medium | Verify tier classification still works after extraction |
| R-006: Context compaction risk across 4 commands | Medium | High | Test each command's activation independently |

---

## M10: Final Release Validation

### Objective

Run comprehensive validation across the entire refactored codebase to confirm all success criteria are met and the release is ready.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D10.1 | Full regression: `make sync-dev && make verify-sync && make lint-architecture` | All 3 commands exit 0 |
| D10.2 | Stale reference scan: zero references to old skill directory names | `grep -rn` for all 5 old names returns empty |
| D10.3 | All 10 success criteria (SC-001 through SC-010) verified | Each criterion documented as PASS with evidence |

### Dependencies

- M9: All integration and closure work complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Stale references discovered | Medium | Low | Fix in M10 scope; re-run scan after fixes |
| SC-010 (task-unified ≤106 lines) not met | Low | Medium | Adjust extraction if needed; target is guideline from spec |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Partial application breaks all invocation wiring (68-file incident repeat) | M3, M7, M9 | High | High | Atomic change groups (§13.7); sync after each group; test activation end-to-end | architect |
| R-002 | Rogue agent untrusted staged changes contaminate new work | M1 | Medium | High | `git status` verification; treat all staged files as untrusted; fresh renames | architect |
| R-003 | TOOL_NOT_AVAILABLE probe result changed in current environment | M1 | Low | Medium | Re-run probe empirically; adapt variant if result differs | backend |
| R-004 | Runtime scope control unsolved (OUT OF SCOPE for v2.01) | All | High | High | Documented as known gap; not addressable in this release | architect |
| R-005 | 4 unimplemented CI checks leave enforcement gaps | M5, M6 | Medium | Medium | Document deferred checks; track as v2.02 backlog | devops |
| R-006 | Context compaction drops `## Activation` directive silently | M3, M9 | Medium | High | "Do NOT proceed" warning; test with fresh contexts | architect |
| R-007 | Zero test coverage for activation flow creates undetectable regression risk | M4, M7 | High | Medium | Manual activation tests; recommend automated tests for v2.02 | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect (confidence: 0.364) | backend (0.336), devops (0.175) | Architecture domain 20% + generalist coverage bonus (1.3x) = highest confidence |
| Template | inline (Tier 4 fallback) | No templates found in Tiers 1-3 | No `.dev/templates/roadmap/` or `~/.claude/templates/roadmap/` directories exist |
| Milestone Count | 10 | Range 8-12 (HIGH class) | Formula: base(8) + floor(4 domains / 2) = 10 |
| Adversarial Mode | none | N/A | No `--specs` or `--multi-roadmap` flags provided |
| Validation Interleave | 1:1 | 1:2 (MEDIUM), 1:3 (LOW) | Complexity class HIGH (0.727) mandates 1:1 interleave ratio |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | All 5 skill directories renamed with `-protocol` suffix | M3 (D3.6) | Yes |
| SC-002 | All 5 commands have `## Activation` sections | M3 (D3.3), M9 (D9.7) | Yes |
| SC-003 | All 5 commands have `Skill` in `allowed-tools` | M3 (D3.1), M9 (D9.7) | Yes |
| SC-004 | `make lint-architecture` exits 0 | M5 (D5.3), M10 (D10.1) | Yes |
| SC-005 | `make sync-dev && make verify-sync` pass | M10 (D10.1) | Yes |
| SC-006 | Wave 2 Step 3 passes 8-point audit | M4 (D4.1) | Yes |
| SC-007 | Return contract routing handles Pass/Partial/Fail correctly | M7 (D7.1) | Yes |
| SC-008 | All BUG-001 through BUG-006 resolved | M3, M9, M10 | Yes |
| SC-009 | Zero stale references to old skill directory names | M10 (D10.2) | Yes |
| SC-010 | `task-unified.md` reduced to ≤106 lines | M9 (D9.6) | Yes |

---

*Roadmap generated by sc:roadmap from sprint-spec.md — complexity HIGH (0.727), 10 milestones, 1:1 interleave*
