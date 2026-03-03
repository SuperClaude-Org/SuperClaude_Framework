# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

---

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | sc:roadmap Adversarial Pipeline Remediation |
| Generator Version | Roadmap→Tasklist Generator v2.2 |
| Generated | 2026-02-25 |
| Status | Active |
| TASKLIST_ROOT | `.dev/releases/current/v2.02-Roadmap-v3/` |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Phase 4 Tasklist | `TASKLIST_ROOT/phase-4-tasklist.md` |
| Phase 5 Tasklist | `TASKLIST_ROOT/phase-5-tasklist.md` |
| Phase 6 Tasklist | `TASKLIST_ROOT/phase-6-tasklist.md` |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/checkpoint-P{N}.md` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/D-####/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |
| Source Roadmap | `TASKLIST_ROOT/roadmap.md` |
| Sprint Spec | `TASKLIST_ROOT/sprint-spec.md` |

---

## Source Snapshot

- **Sprint scope**: Restores full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` invocations across three epics spanning invocation wiring, return contract transport, and specification clarity.
- **Root cause**: Skill tool missing from `allowed-tools` in both `roadmap.md` and `sc-roadmap/SKILL.md`, preventing cross-skill invocation; return-contract.yaml transport convention undefined; Wave 2 step 3 lacks sub-step decomposition; pseudo-CLI syntax used in integration file.
- **Empirical-first constraint**: Phase 1 must complete probe tasks (T01.01–T01.03) and produce a sprint variant decision (T01.04) before any file edits begin; fallback-only path is a valid outcome.
- **Three-epic structure**: Epic 1 — Invocation Wiring (Phases 2); Epic 2 — Return Contract Transport (Phase 3); Epic 3 — Specification Rewrite (Phase 4); preceded by pre-implementation gates (Phase 1) and followed by sync, quality gates, and E2E validation (Phases 5–6).
- **Quality gate chain**: All file edits must pass `make sync-dev`, `make verify-sync`, `make lint`, and `uv run pytest` before E2E verification tests execute; no phase 6 work begins until phase 5 gates are green.
- **Compliance tiers**: Tasks are classified STRICT (file edits touching security or multi-file scope), STANDARD (single-file code changes), LIGHT (trivial fixes), or EXEMPT (read-only probes, git ops, documentation); tier drives verification method and MCP server selection.

---

## Deterministic Rules Applied

- **R-RULE-01 Empirical-before-edit**: No source file is modified until T01.01 (Skill probe) and T01.03 (prerequisite validation) produce documented evidence artifacts in `TASKLIST_ROOT/artifacts/`.
- **R-RULE-02 Sprint variant gate**: T01.04 sprint variant decision artifact must exist and record either "primary path viable" or "fallback-only" before any Phase 2 task is opened; fallback-only closes Phases 2–4 and proceeds directly to Phase 5.
- **R-RULE-03 Phase sequencing**: Phases execute in strict order 1 → 2 → 3 → 4 → 5 → 6; no phase may begin until the preceding phase's milestone is marked complete in the execution log.
- **R-RULE-04 Single active task**: Only one task may be `in_progress` at a time within a session; task state transitions (pending → in_progress → completed | blocked) must be logged with timestamp.
- **R-RULE-05 Deliverable-to-artifact binding**: Every deliverable D-0001 through D-0029 must produce a verifiable artifact at its declared path under `TASKLIST_ROOT/artifacts/D-####/`; deliverables without artifacts cannot be marked complete.
- **R-RULE-06 Tier-driven verification**: STRICT tasks require sub-agent (quality-engineer) verification; STANDARD tasks require direct test execution; LIGHT tasks may skip verification; EXEMPT tasks skip verification entirely.
- **R-RULE-07 Traceability closure**: Every Roadmap Item R-001 through R-036 must map to at least one Task ID and one Deliverable ID in the Traceability Matrix; unmapped items are flagged as gaps.
- **R-RULE-08 Dead code scope**: T03.02 dead code removal (D-0011) is scoped exclusively to `subagent_type` lines; no other structural changes are permitted within the same edit unless explicitly listed in the task file.
- **R-RULE-09 Cross-reference consistency**: D-0014 (cross-reference consistency) must be verified after D-0010 (return contract section) and D-0012 (consumption section) are both complete; the producer and consumer schemas must use identical field names and types.
- **R-RULE-10 Pseudo-CLI zero tolerance**: After T04.03, a grep pass confirming zero pseudo-CLI syntax instances in `adversarial-integration.md` is required before D-0018 is accepted.
- **R-RULE-11 Glossary coverage audit**: After T04.01, 100% of verbs appearing in Waves 0–4 of the modified files must resolve to a glossary entry; any unresolved verb blocks D-0016 acceptance.
- **R-RULE-12 Checkpoint cadence**: A checkpoint report (template in this file) must be written at the close of each phase before the next phase's first task transitions to `in_progress`.

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text |
|---|---|---|
| R-001 | Phase 1 | This roadmap restores full adversarial pipeline functionality for sc:roadmap --multi-roadmap --agents across three epics |
| R-002 | Phase 1 | Empirically determine Skill tool cross-skill invocation viability and validate all external dependencies before file edits |
| R-003 | Phase 1 | Skill tool probe (Task 0.0): test cross-skill invocation and Task agent Skill access |
| R-004 | Phase 1 | Determine "skill already running" constraint semantics |
| R-005 | Phase 1 | Prerequisite validation (Task 0.1): 6 dependency checks |
| R-006 | Phase 1 | Sprint variant decision — if primary path blocked: fallback-only task modifications applied |
| R-007 | Phase 2 | Enable skill-to-skill invocation by adding the Skill tool to allowed-tools |
| R-008 | Phase 2 | Skill in allowed-tools of src/superclaude/commands/roadmap.md (Task 1.1) |
| R-009 | Phase 2 | Skill in allowed-tools of src/superclaude/skills/sc-roadmap/SKILL.md (Task 1.2) |
| R-010 | Phase 2 | Wave 2 step 3 rewritten as sub-steps 3a-3f (merged Task 1.3) |
| R-011 | Phase 2 | Fallback protocol with F1, F2/3, F4/5 (merged Task 1.3) |
| R-012 | Phase 2 | Return contract routing in step 3e (merged Task 1.3) |
| R-013 | Phase 3 | Establish the file-based return-contract.yaml convention so sc:adversarial reliably transports structured pipeline results |
| R-014 | Phase 3 | Return Contract (MANDATORY) section in sc:adversarial SKILL.md — 9 fields defined |
| R-015 | Phase 3 | Dead code removal: zero subagent_type lines (Task 3.1 appended scope) |
| R-016 | Phase 3 | Return Contract Consumption section in adversarial-integration.md — 3-status routing, missing-file guard |
| R-017 | Phase 3 | Post-Adversarial Artifact Existence Gate (Tier 1) section — 4 existence checks |
| R-018 | Phase 3 | Cross-reference consistency between producer and consumer schemas |
| R-019 | Phase 4 | Eliminate specification ambiguity by adding verb-to-tool glossary, fixing Wave 1A, converting pseudo-CLI |
| R-020 | Phase 4 | Verb-to-tool glossary (Execution Vocabulary) section before Wave 0 |
| R-021 | Phase 4 | Every verb in Waves 0-4 appears in glossary — 100% audit coverage |
| R-022 | Phase 4 | Wave 1A step 2 uses glossary-consistent Skill tool invocation |
| R-023 | Phase 4 | adversarial-integration.md pseudo-CLI syntax fully converted |
| R-024 | Phase 5 | Verify all code changes synchronized, quality gates pass, codebase clean for E2E |
| R-025 | Phase 5 | make sync-dev executed successfully |
| R-026 | Phase 5 | make verify-sync passes |
| R-027 | Phase 5 | make lint passes on all modified files |
| R-028 | Phase 5 | uv run pytest passes — no existing tests broken |
| R-029 | Phase 6 | Execute all 7 verification tests to confirm full invocation chain |
| R-030 | Phase 6 | Verification Test 1: Skill tool in allowed-tools confirmation |
| R-031 | Phase 6 | Verification Test 2: Wave 2 step 3 structural audit |
| R-032 | Phase 6 | Verification Test 3: Return contract schema consistency |
| R-033 | Phase 6 | Verification Test 3.5: Cross-reference field consistency |
| R-034 | Phase 6 | Verification Test 4: Pseudo-CLI elimination |
| R-035 | Phase 6 | Verification Test 5: E2E invocation (post-sprint, manual) |
| R-036 | Phase 6 | Verification Test 6: Tier 1 quality gate structure audit |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Path | Effort | Risk |
|---|---|---|---|---|---|---|---|---|
| D-0001 | T01.01 | R-003 | Skill tool probe result document | EXEMPT | None (read-only) | `TASKLIST_ROOT/artifacts/D-0001/probe-result.md` | S | Low |
| D-0002 | T01.02 | R-004 | Constraint semantics analysis | EXEMPT | None (read-only) | `TASKLIST_ROOT/artifacts/D-0002/constraint-semantics.md` | S | Low |
| D-0003 | T01.03 | R-005 | Prerequisite validation report (6 checks) | EXEMPT | None (read-only) | `TASKLIST_ROOT/artifacts/D-0003/prereq-validation.md` | S | Low |
| D-0004 | T01.04 | R-006 | Sprint variant decision artifact | EXEMPT | None (decision doc) | `TASKLIST_ROOT/artifacts/D-0004/variant-decision.md` | S | Medium |
| D-0005 | T02.01 | R-008 | Skill in allowed-tools (roadmap.md) | STRICT | Sub-agent quality-engineer | `TASKLIST_ROOT/artifacts/D-0005/diff.md` | S | Medium |
| D-0006 | T02.01 | R-009 | Skill in allowed-tools (SKILL.md) | STRICT | Sub-agent quality-engineer | `TASKLIST_ROOT/artifacts/D-0006/diff.md` | S | Medium |
| D-0007 | T02.02 | R-010 | Wave 2 step 3 sub-steps 3a-3f | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0007/wave2-step3.md` | M | Medium |
| D-0008 | T02.02 | R-011 | Fallback protocol (F1, F2/3, F4/5) | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0008/fallback-protocol.md` | M | Medium |
| D-0009 | T02.02 | R-012 | Return contract routing in step 3e | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0009/step3e-routing.md` | S | Low |
| D-0010 | T03.01 | R-014 | Return Contract (MANDATORY) section | STRICT | Sub-agent quality-engineer | `TASKLIST_ROOT/artifacts/D-0010/return-contract-section.md` | M | High |
| D-0011 | T03.02 | R-015 | Dead code removal (subagent_type) | LIGHT | Skip verification | `TASKLIST_ROOT/artifacts/D-0011/dead-code-diff.md` | S | Low |
| D-0012 | T03.03 | R-016 | Return Contract Consumption section | STRICT | Sub-agent quality-engineer | `TASKLIST_ROOT/artifacts/D-0012/consumption-section.md` | M | High |
| D-0013 | T03.04 | R-017 | Tier 1 Artifact Existence Gate | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0013/tier1-gate.md` | M | Medium |
| D-0014 | T03.05 | R-018 | Cross-reference consistency verification | EXEMPT | None (audit doc) | `TASKLIST_ROOT/artifacts/D-0014/cross-ref-audit.md` | S | Medium |
| D-0015 | T04.01 | R-020 | Execution Vocabulary glossary | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0015/glossary.md` | M | Low |
| D-0016 | T04.01 | R-021 | Glossary verb coverage audit | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0016/verb-coverage-audit.md` | S | Low |
| D-0017 | T04.02 | R-022 | Wave 1A step 2 fix | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0017/wave1a-fix.md` | S | Low |
| D-0018 | T04.03 | R-023 | Pseudo-CLI conversion | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0018/pseudo-cli-conversion.md` | M | Low |
| D-0019 | T05.01 | R-025 | make sync-dev execution | STANDARD | Direct command output | `TASKLIST_ROOT/artifacts/D-0019/sync-dev-output.txt` | S | Low |
| D-0020 | T05.02 | R-026 | make verify-sync result | STANDARD | Direct command output | `TASKLIST_ROOT/artifacts/D-0020/verify-sync-output.txt` | S | Low |
| D-0021 | T05.03 | R-027 | Lint pass | STANDARD | Direct command output | `TASKLIST_ROOT/artifacts/D-0021/lint-output.txt` | S | Low |
| D-0022 | T05.04 | R-028 | Pytest pass | LIGHT | Skip additional verification | `TASKLIST_ROOT/artifacts/D-0022/pytest-output.txt` | S | Low |
| D-0023 | T06.01 | R-030 | VT1: allowed-tools grep | EXEMPT | None (grep output) | `TASKLIST_ROOT/artifacts/D-0023/vt1-grep.txt` | S | Low |
| D-0024 | T06.02 | R-031 | VT2: structural audit | EXEMPT | None (audit doc) | `TASKLIST_ROOT/artifacts/D-0024/vt2-structural-audit.md` | S | Low |
| D-0025 | T06.03 | R-032 | VT3: schema consistency | EXEMPT | None (audit doc) | `TASKLIST_ROOT/artifacts/D-0025/vt3-schema.md` | S | Low |
| D-0026 | T06.04 | R-033 | VT3.5: cross-reference | EXEMPT | None (audit doc) | `TASKLIST_ROOT/artifacts/D-0026/vt3.5-crossref.md` | S | Low |
| D-0027 | T06.05 | R-034 | VT4: pseudo-CLI elimination | EXEMPT | None (grep output) | `TASKLIST_ROOT/artifacts/D-0027/vt4-grep.txt` | S | Low |
| D-0028 | T06.06 | R-035 | VT5: E2E invocation | STRICT | Manual post-sprint | `TASKLIST_ROOT/artifacts/D-0028/vt5-e2e-result.md` | L | High |
| D-0029 | T06.07 | R-036 | VT6: Tier 1 gate audit | EXEMPT | None (audit doc) | `TASKLIST_ROOT/artifacts/D-0029/vt6-tier1-audit.md` | S | Low |

**Effort key**: S = Small (< 30 min), M = Medium (30–90 min), L = Large (> 90 min)

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---|---|---|
| Phase 1 | Pre-Implementation Gates & Probing | T01.01, T01.02, T01.03, T01.04 | Sprint variant decision artifact produced; all 6 prerequisites validated; go/no-go gate for Phase 2 | 4 EXEMPT |
| Phase 2 | Invocation Wiring Restoration | T02.01, T02.02 | Skill tool in allowed-tools for both files; Wave 2 step 3 rewritten with 3a-3f sub-steps and fallback protocol | 1 STRICT, 1 STANDARD |
| Phase 3 | Return Contract Transport Mechanism | T03.01, T03.02, T03.03, T03.04, T03.05 | return-contract.yaml convention established; producer and consumer sections written; Tier 1 existence gate in place; dead code removed | 2 STRICT, 1 STANDARD, 1 LIGHT, 1 EXEMPT |
| Phase 4 | Specification Rewrite | T04.01, T04.02, T04.03 | Execution Vocabulary glossary with 100% verb coverage; Wave 1A fixed; zero pseudo-CLI instances remain | 3 STANDARD |
| Phase 5 | Post-Edit Sync & Quality Gates | T05.01, T05.02, T05.03, T05.04 | All modified files synchronized; verify-sync green; lint clean; pytest suite passing | 3 STANDARD, 1 LIGHT |
| Phase 6 | E2E Validation & Acceptance | T06.01, T06.02, T06.03, T06.04, T06.05, T06.06, T06.07 | All 7 verification tests executed and documented; sprint acceptance criteria met | 1 STRICT, 6 EXEMPT |

**Phase file references**: `TASKLIST_ROOT/phase-{1..6}-tasklist.md`

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Path(s) |
|---|---|---|---|---|---|
| R-001 | T01.01–T01.04 | D-0001–D-0004 | EXEMPT | High | `artifacts/D-0001/` – `artifacts/D-0004/` |
| R-002 | T01.01, T01.03 | D-0001, D-0003 | EXEMPT | High | `artifacts/D-0001/probe-result.md`, `artifacts/D-0003/prereq-validation.md` |
| R-003 | T01.01 | D-0001 | EXEMPT | High | `artifacts/D-0001/probe-result.md` |
| R-004 | T01.02 | D-0002 | EXEMPT | High | `artifacts/D-0002/constraint-semantics.md` |
| R-005 | T01.03 | D-0003 | EXEMPT | High | `artifacts/D-0003/prereq-validation.md` |
| R-006 | T01.04 | D-0004 | EXEMPT | High | `artifacts/D-0004/variant-decision.md` |
| R-007 | T02.01 | D-0005, D-0006 | STRICT | High | `artifacts/D-0005/diff.md`, `artifacts/D-0006/diff.md` |
| R-008 | T02.01 | D-0005 | STRICT | High | `artifacts/D-0005/diff.md` |
| R-009 | T02.01 | D-0006 | STRICT | High | `artifacts/D-0006/diff.md` |
| R-010 | T02.02 | D-0007 | STANDARD | High | `artifacts/D-0007/wave2-step3.md` |
| R-011 | T02.02 | D-0008 | STANDARD | High | `artifacts/D-0008/fallback-protocol.md` |
| R-012 | T02.02 | D-0009 | STANDARD | High | `artifacts/D-0009/step3e-routing.md` |
| R-013 | T03.01, T03.03, T03.04 | D-0010, D-0012, D-0013 | STRICT/STANDARD | High | `artifacts/D-0010/`, `artifacts/D-0012/`, `artifacts/D-0013/` |
| R-014 | T03.01 | D-0010 | STRICT | High | `artifacts/D-0010/return-contract-section.md` |
| R-015 | T03.02 | D-0011 | LIGHT | High | `artifacts/D-0011/dead-code-diff.md` |
| R-016 | T03.03 | D-0012 | STRICT | High | `artifacts/D-0012/consumption-section.md` |
| R-017 | T03.04 | D-0013 | STANDARD | High | `artifacts/D-0013/tier1-gate.md` |
| R-018 | T03.05 | D-0014 | EXEMPT | High | `artifacts/D-0014/cross-ref-audit.md` |
| R-019 | T04.01, T04.02, T04.03 | D-0015–D-0018 | STANDARD | High | `artifacts/D-0015/` – `artifacts/D-0018/` |
| R-020 | T04.01 | D-0015 | STANDARD | High | `artifacts/D-0015/glossary.md` |
| R-021 | T04.01 | D-0016 | STANDARD | High | `artifacts/D-0016/verb-coverage-audit.md` |
| R-022 | T04.02 | D-0017 | STANDARD | High | `artifacts/D-0017/wave1a-fix.md` |
| R-023 | T04.03 | D-0018 | STANDARD | High | `artifacts/D-0018/pseudo-cli-conversion.md` |
| R-024 | T05.01–T05.04 | D-0019–D-0022 | STANDARD/LIGHT | High | `artifacts/D-0019/` – `artifacts/D-0022/` |
| R-025 | T05.01 | D-0019 | STANDARD | High | `artifacts/D-0019/sync-dev-output.txt` |
| R-026 | T05.02 | D-0020 | STANDARD | High | `artifacts/D-0020/verify-sync-output.txt` |
| R-027 | T05.03 | D-0021 | STANDARD | High | `artifacts/D-0021/lint-output.txt` |
| R-028 | T05.04 | D-0022 | LIGHT | High | `artifacts/D-0022/pytest-output.txt` |
| R-029 | T06.01–T06.07 | D-0023–D-0029 | STRICT/EXEMPT | High | `artifacts/D-0023/` – `artifacts/D-0029/` |
| R-030 | T06.01 | D-0023 | EXEMPT | High | `artifacts/D-0023/vt1-grep.txt` |
| R-031 | T06.02 | D-0024 | EXEMPT | High | `artifacts/D-0024/vt2-structural-audit.md` |
| R-032 | T06.03 | D-0025 | EXEMPT | High | `artifacts/D-0025/vt3-schema.md` |
| R-033 | T06.04 | D-0026 | EXEMPT | High | `artifacts/D-0026/vt3.5-crossref.md` |
| R-034 | T06.05 | D-0027 | EXEMPT | High | `artifacts/D-0027/vt4-grep.txt` |
| R-035 | T06.06 | D-0028 | STRICT | Medium | `artifacts/D-0028/vt5-e2e-result.md` |
| R-036 | T06.07 | D-0029 | EXEMPT | High | `artifacts/D-0029/vt6-tier1-audit.md` |

---

## Execution Log Template

Copy this template to `TASKLIST_ROOT/execution-log.md` at sprint start and append an entry for every task state transition.

```markdown
# Execution Log — sc:roadmap Adversarial Pipeline Remediation

| # | Timestamp (UTC) | Task ID | Deliverable ID(s) | Transition | Notes |
|---|---|---|---|---|---|
| 1 | YYYY-MM-DD HH:MM | T01.01 | D-0001 | pending → in_progress | |
| 2 | YYYY-MM-DD HH:MM | T01.01 | D-0001 | in_progress → completed | Artifact: artifacts/D-0001/probe-result.md |

## Blocked Task Log

| Timestamp (UTC) | Task ID | Blocked By | Unblock Condition | Resolution |
|---|---|---|---|---|
| | | | | |

## Sprint Variant Record

- Decision timestamp:
- Variant selected: [ ] Primary path viable  [ ] Fallback-only
- Evidence artifact: artifacts/D-0004/variant-decision.md
- Phases affected by variant:

## Phase Milestone Log

| Phase | Milestone Marker | Completed Timestamp | Checkpoint Report |
|---|---|---|---|
| Phase 1 | All 4 EXEMPT tasks completed; D-0004 exists | | checkpoints/checkpoint-P1.md |
| Phase 2 | D-0005, D-0006 diffs verified; D-0007–D-0009 complete | | checkpoints/checkpoint-P2.md |
| Phase 3 | D-0010–D-0014 complete; schema cross-ref verified | | checkpoints/checkpoint-P3.md |
| Phase 4 | D-0015–D-0018 complete; zero pseudo-CLI confirmed | | checkpoints/checkpoint-P4.md |
| Phase 5 | D-0019–D-0022 all green (sync, verify, lint, pytest) | | checkpoints/checkpoint-P5.md |
| Phase 6 | D-0023–D-0029 complete; VT5 manual result filed | | checkpoints/checkpoint-P6.md |
```

---

## Checkpoint Report Template

Copy this template for each phase close. Save as `TASKLIST_ROOT/checkpoints/checkpoint-P{N}.md`.

```markdown
# Checkpoint Report — Phase {N}: {Phase Name}

**Sprint**: sc:roadmap Adversarial Pipeline Remediation
**Phase**: {N}
**Completed**: YYYY-MM-DD HH:MM UTC
**Author**: {executor-id or "Claude Code session"}

---

## Phase Summary

- **Milestone achieved**: {yes / no — if no, explain}
- **Tasks completed**: {list Task IDs}
- **Tasks blocked**: {list Task IDs or "none"}
- **Deliverables produced**: {list D-#### IDs with artifact paths}

---

## Quality Gate Results

| Gate | Command / Method | Result | Notes |
|---|---|---|---|
| Tier verification | {sub-agent / direct test / skip} | {pass / fail / n/a} | |
| Artifact existence | ls TASKLIST_ROOT/artifacts/D-####/ | {pass / fail} | |
| Traceability | All R-IDs for phase mapped to deliverables | {pass / fail} | |

---

## Deviations from Plan

| Deviation | Impact | Mitigation Applied |
|---|---|---|
| {describe or "none"} | | |

---

## Carry-Forward Items

| Item | Type | Target Phase | Owner |
|---|---|---|---|
| {item or "none"} | blocked / deferred / discovered | | |

---

## Go / No-Go Decision for Next Phase

- [ ] Go — all deliverables accepted, no blocking carry-forward items
- [ ] No-Go — reason: {explain}

**Authorized by**: {executor-id}
**Next phase file**: `TASKLIST_ROOT/phase-{N+1}-tasklist.md`
```

---

## Feedback Collection Template

Copy this template to `TASKLIST_ROOT/feedback-log.md` and append entries throughout the sprint.

```markdown
# Feedback Log — sc:roadmap Adversarial Pipeline Remediation

Instructions: Record any feedback on task descriptions, deliverable definitions, tier assignments,
artifact path conventions, or generator output quality. Each entry informs generator v2.3+ improvements.

---

## Feedback Entries

### Entry 001

- **Date**: YYYY-MM-DD
- **Category**: [ ] Task description  [ ] Deliverable definition  [ ] Tier assignment
            [ ] Artifact path  [ ] Template usability  [ ] Generator output  [ ] Other
- **Phase / Task / Deliverable**: {e.g., Phase 2 / T02.02 / D-0007}
- **Observation**: {what was unclear, incorrect, or missing}
- **Suggested Improvement**: {specific change for next generator version}
- **Severity**: [ ] Blocking  [ ] High  [ ] Medium  [ ] Low (cosmetic)
- **Status**: [ ] Open  [ ] Incorporated  [ ] Deferred

---

## Aggregate Feedback Summary (end-of-sprint)

| Category | Count | Most Common Issue | Recommended Generator Change |
|---|---|---|---|
| Task description | | | |
| Deliverable definition | | | |
| Tier assignment | | | |
| Artifact path | | | |
| Template usability | | | |
| Generator output | | | |

---

## Sprint Retrospective Notes

**What worked well in this tasklist structure**:
-

**What should change for the next sprint**:
-

**Deterministic rules that need revision**:
-

**New rules to consider for v2.3**:
-
```
