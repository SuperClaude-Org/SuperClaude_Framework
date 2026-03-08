---
spec_source: .dev/releases/current/v2.18-roadmap-validate/spec-roadmap-validate.md
generated: "2026-03-06"
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
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (M3) | M1 (Foundation & Data Model), M2 (Core Validation Pipeline) | ValidateConfig construction, single-agent pipeline correctness, gate criteria, module isolation (NFR-002), infrastructure reuse (NFR-004) | Any unit test failure in validate_models, validate_executor, validate_gates, or validate_prompts; any reverse import detected from pipeline/* to validate_* |
| V2 (M6) | M4 (Multi-Agent Adversarial Mode), M5 (CLI Integration & Auto-Invocation) | Multi-agent step construction, adversarial merge report structure, CLI integration, auto-invocation, standalone operation, all NFR compliance | Any integration test failure; any NFR violation; traceability gap (FR without deliverable or deliverable without FR) |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Breaking dependency between validate_executor and pipeline infrastructure; missing GateCriteria import; circular import chain |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Incorrect YAML frontmatter schema in validation-report.md; missing validation dimension in reflect prompt; _build_validate_steps returns wrong step count |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Inconsistent error message formatting; missing edge case in test fixture; documentation gap in prompt comments |
| Info | Log only, no action required | N/A | Alternative prompt phrasing opportunities; potential optimization in gate semantic checks; style consistency suggestions |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | ValidateConfig instantiates correctly; infrastructure audit confirms reuse feasibility; validate_dir creation works; missing file detection works | All D1.1-D1.4 acceptance criteria met, no Critical/Major issues |
| M2 | build_reflect_prompt covers 7 dimensions; REFLECT_GATE checks correct fields; _build_validate_steps returns 1 Step; execute_validate produces valid report; tasklist_ready logic correct | All D2.1-D2.6 acceptance criteria met, no Critical/Major issues |
| M3 (V1) | All unit tests pass; NFR-002 verified; single-agent integration test produces valid report | All D3.1-D3.3 pass; zero Critical/Major issues from V1 validation |
| M4 | build_adversarial_merge_prompt handles dedup and escalation; ADVERSARIAL_MERGE_GATE includes _has_agreement_table; multi-agent step construction correct; Agent Agreement table present | All D4.1-D4.5 acceptance criteria met, no Critical/Major issues |
| M5 | validate subcommand accepts correct args; --no-validate skips validation; auto-invocation triggers after pipeline success; output format matches spec; standalone mode works | All D5.1-D5.5 acceptance criteria met, no Critical/Major issues |
| M6 (V2) | All integration tests pass; all NFRs verified; traceability matrix complete | All D6.1-D6.4 pass; zero Critical/Major issues from V2 validation |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 (M3) | M1 | Unit test: test_validate_config_from_output_dir; presence check for required files |
| FR-002 | V1 (M3) | M2 | Unit test: test_build_validate_steps_single; integration test with sample artifacts |
| FR-003 | V2 (M6) | M4 | Unit test: test_build_validate_steps_multi; verify parallel group + merge step |
| FR-004 | V2 (M6) | M5 | Integration test: test_run_auto_validates; verify execute_validate called after pipeline success |
| FR-005 | V1 (M3) | M2 | Unit test: test_reflect_prompt_contains_dimensions; verify all 7 dimensions in prompt |
| FR-006 | V1 (M3) | M2 | Unit test: verify report YAML frontmatter schema; integration test validates output structure |
| FR-007 | V2 (M6) | M4 | Unit test: verify Agent Agreement Analysis table format; semantic check _has_agreement_table |
| FR-008 | V1 (M3) | M2 | Unit test: test_reflect_prompt_contains_dimensions; verify constraints in prompt text |
| FR-009 | V2 (M6) | M4 | Unit test: test_merge_prompt_contains_categories; verify BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT |
| FR-010 | V1 (M3) | M2 | File existence; unit test for execute_validate and _build_validate_steps |
| FR-011 | V1 (M3) | M2 | Unit test: test_reflect_gate_criteria; verify gate fields and semantic checks |
| FR-012 | V1 (M3) | M2 | Unit test: prompt function tests; verify function signatures and output |
| FR-013 | V2 (M6) | M5 | Integration test: verify validate subcommand registered; --no-validate flag works |
| FR-014 | V2 (M6) | M5 | Integration test: test_run_auto_validates |
| FR-015 | V1 (M3) | M1 | Unit test: test_validate_config_from_output_dir; type validation |
| FR-016 | V1 (M3) | M2 | Unit test: test_build_validate_steps_single; verify returns list with 1 Step |
| FR-017 | V2 (M6) | M4 | Unit test: test_build_validate_steps_multi; verify parallel group + merge |
| FR-018 | V2 (M6) | M5 | Integration test: validate subcommand accepts correct options |
| FR-019 | V2 (M6) | M5 | Integration test: test_run_with_no_validate |
| FR-020 | V2 (M6) | M5 | Integration test: verify success output format |
| FR-021 | V2 (M6) | M5 | Integration test: verify warning behavior for blocking issues |
| FR-022 | V2 (M6) | M5 | Integration test: verify gate failure output |
| FR-023 | V1 (M3) | M2 | Unit test: test_merge_gate_has_agreement_table; verify semantic check function |
| NFR-001 | V2 (M6) | M6 | Timing measurement: single-agent ≤120s |
| NFR-002 | V1 (M3) | M3 | grep/search: zero imports from validate_* in pipeline/* |
| NFR-003 | V2 (M6) | M5 | Integration test: standalone validate invocation |
| NFR-004 | V1 (M3) | M1 | Infrastructure audit: no new classes in pipeline/* |
| NFR-005 | V2 (M6) | M4 | Code review: single _build_validate_steps handles both modes |
