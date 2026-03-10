---
spec_source: ".dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md"
generated: "2026-02-23T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 4
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score 0.584)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Invocation Wiring Restoration) | Skill tool availability in both files (Test 1); Wave 2 step 3 structural correctness — 6 sub-steps, glossary verbs, Skill call syntax, fallback error types, missing-file guard, convergence threshold, skip-template instruction (Test 2) | Any grep FAIL in Test 1; any of the 7 structural checklist items missing in Test 2 |
| V2 | M3 (Specification Rewrite) + M4 (Return Contract) | Schema consistency between producer and consumer (Test 3); cross-reference field alignment (Test 3.5); pseudo-CLI elimination (Test 4); Tier 1 gate structure (Test 6); sync integrity and regression freedom (make verify-sync, pytest, lint) | Any field mismatch in Test 3/3.5; grep count > 0 in Test 4; any of 7 gate checklist items missing in Test 6; make verify-sync failure; test regression; lint failure |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates M1+M2. V2 validates M3+M4. Each validation milestone references specific work milestones by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | `Skill` missing from allowed-tools after Task 1.1/1.2 (blocks entire pipeline); return contract schema mismatch between producer and consumer (breaks data flow); circular dependency in milestone plan |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Fallback protocol missing one of 3 error types; glossary verb missing from Wave step; sub-step count != 6; Tier 1 gate check missing failure treatment |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Inconsistent phrasing between spec and implementation; optional field missing cross-reference comment; minor formatting differences |
| Info | Log only, no action required | N/A | Alternative approaches noted during review; optimization opportunities in fallback protocol; documentation enhancement suggestions |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | Task 0.0 decision gate documented; Task 0.1 all 6 checks passed; sprint variant decision recorded | All 3 deliverables (D1.1-D1.3) have documented results; no check left unanswered |
| M2 | Skill in allowed-tools (2 files); Wave 2 step 3 has 6 sub-steps; fallback protocol with 3 error types and 3 execution steps; return contract routing with missing-file guard | D2.1-D2.5 acceptance criteria all met; no Critical/Major issues from V1 preview |
| V1 | Verification Tests 1 and 2 pass | All grep commands return PASS; all 7 structural checklist items confirmed |
| M3 | Glossary exists before Wave 0 with 4 mappings and scope statement; Wave 1A step 2 fixed; pseudo-CLI count = 0 | D3.1-D3.3 acceptance criteria all met |
| M4 | Return contract section with 9 fields; zero subagent_type lines; consumption section with 3-status routing; Tier 1 gate with 4 checks | D4.1-D4.4 acceptance criteria all met |
| V2 | Verification Tests 3, 3.5, 4, 6 pass; make sync-dev && verify-sync passes; uv run pytest passes; make lint passes | All verification tests green; zero regressions; sync integrity confirmed |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | M1 gate | M1 | Task 0.0 empirical probe result |
| FR-002 | M1 gate | M1 | Task 0.1 6-check validation |
| FR-003 | V1, Test 1 | M2 | grep static analysis on roadmap.md |
| FR-004 | V1, Test 1 | M2 | grep static analysis on SKILL.md |
| FR-005 | V1, Test 2 | M2 | 7-point structural audit of Wave 2 step 3 |
| FR-006 | V2, DV2.5 | M3 | Section existence check + verb coverage audit |
| FR-007 | V2, DV2.5 | M3 | Glossary-consistent verb + fallback presence check |
| FR-008 | V2, Test 4 | M3 | grep -c pattern count = 0 |
| FR-009 | V2, Test 3 | M4 | Producer schema field count and null semantics |
| FR-010 | V2, Test 3 | M4 | Consumer routing section audit |
| FR-011 | V2, Test 6 | M4 | 7-point Tier 1 gate structural audit |
| FR-012 | V2, DV2.5 | M4 | grep -c "subagent_type" = 0 |
| FR-013 | V1, Test 2 | M2 | F1 step presence with input/output/failure definitions |
| FR-014 | V1, Test 2 | M2 | F2/3 step presence with labeled sections requirement |
| FR-015 | V1, Test 2 | M2 | F4/5 step presence with base-selection + merged-output + contract |
| FR-016 | M1 gate | M1 | Sprint variant decision recorded if primary path blocked |
| FR-017 | Post-sprint | N/A | Deferred to pre-v2.1 gap; not validated in this sprint |
| NFR-001 | V2, Test 3 | M4 | Schema consistency between producer and consumer |
| NFR-002 | V1, Test 2 | M2 | 3 error types covered in fallback trigger |
| NFR-003 | V2, Test 3 | M4 | Write-on-failure instruction present in producer |
| NFR-004 | V1, Test 2 | M2 | Quality threshold present (>=100 words, >=2 variants) |
| NFR-005 | V2, Test 4 | M3 | grep count = 0 for pseudo-CLI syntax |
| NFR-006 | V2, DV2.5 | V2 | make verify-sync exit code = 0 |

## Post-Sprint Validation (Deferred)

The following validation items are deferred to post-sprint or follow-up sprint per spec decisions:

| Test | Description | Condition | Sprint Action |
|------|-------------|-----------|---------------|
| Test 5 | End-to-end invocation chain | Requires all 3 epics complete + Claude Code session | Manual post-sprint execution |
| Test 7 | Fallback protocol validation | If primary path viable: lightweight smoke test only; if blocked: full validation mandatory | Conditional per Task 0.0 result |
| FR-017 | Debt register initialization | Pre-v2.1 gap activity | Not validated in this sprint |

---

*Test strategy generated 2026-02-23. Interleave ratio 1:2 from MEDIUM complexity (0.584). 2 validation milestones validating 4 work milestones.*
