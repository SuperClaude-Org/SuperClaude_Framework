---
spec_source: .dev/releases/current/v2.02-Roadmap-v3/sprint-spec.md
generated: 2026-02-25T12:00:00Z
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
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.547)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Invocation Wiring Restoration), M3 (Return Contract Transport) | Skill tool in allowed-tools (SC-001); Wave 2 step 3 sub-steps 3a-3f present (SC-003); return contract 9 fields (SC-006); 3-status routing (SC-007); Tier 1 gate (SC-008); fallback error coverage (SC-009); zero subagent_type lines (SC-011) | Any grep verification fails; sub-step count ≠ 6; return contract schema mismatch between producer and consumer; Tier 1 gate missing checks or out of order |
| V2 | M4 (Specification Rewrite), M5 (Post-Edit Sync) | Glossary before Wave 0 (SC-002); Wave 1A step 2 consistency (SC-004); zero pseudo-CLI (SC-005); glossary verb coverage (SC-010); make verify-sync (SC-012); no broken tests (SC-013) | Glossary missing or misplaced; pseudo-CLI grep count > 0; make verify-sync exit code ≠ 0; pytest failures |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 fires after M2+M3 (the two core implementation milestones). V2 fires after M4+M5 (specification rewrite + quality sync). M6 is itself an acceptance test milestone — it validates V1 and V2 coverage plus E2E.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Skill tool not in allowed-tools after Task 1.1; return contract schema mismatch between producer and consumer; `make verify-sync` fails with structural divergence |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Wave 2 step 3 has fewer than 6 sub-steps; fallback protocol missing an error type; pseudo-CLI syntax remains in converted sections |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Glossary verb not used in one non-critical step; inconsistent formatting in YAML examples; minor wording ambiguity |
| Info | Log only, no action required | N/A | Alternative implementation order suggestion (IMP-07); optimization opportunity in fallback step sequencing |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | D1.1: Skill tool probe documented; D1.3: all 6 prerequisite checks pass | Decision gate result recorded; sprint variant decided; no check unanswered |
| M2 | D2.1-D2.2: grep PASS; D2.3: 6 sub-steps with glossary verbs; D2.4: 3 error types covered, 3 fallback invocations defined; D2.5: 3-status routing with threshold | All grep verifications pass; structural audit confirms sub-step count and verb compliance; fallback coverage complete |
| M3 | D3.1: 9-field section present; D3.2: zero subagent_type; D3.3: consumption section with guard; D3.4: Tier 1 gate with 4 checks; D3.5: schema consistency | Field count exact; grep returns 0; all sections present with required content; producer-consumer field sets identical |
| M4 | D4.1: glossary before Wave 0; D4.2: 100% verb coverage; D4.3: Wave 1A step 2 consistent; D4.4: grep count = 0 | All structural checks pass; no bare "Invoke" verbs; zero standalone pseudo-CLI |
| M5 | D5.1-D5.4: all exit codes 0 | make sync-dev, make verify-sync, make lint, uv run pytest all pass |
| M6 | D6.1-D6.7: all 7 verification tests pass | Full DoD checklist confirmed; E2E invocation chain functional (or fallback validated if primary path blocked) |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-004 | V1 | M2 | `grep -q "Skill" src/superclaude/commands/roadmap.md` |
| FR-005 | V1 | M2 | `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` |
| FR-006 | V1 | M2 | Manual: count sub-steps 3a-3f in Wave 2 step 3 |
| FR-010 | V1 | M2 | Manual: verify Skill tool call syntax in step 3d |
| FR-011 | V1 | M2 | Manual: verify 3 error types listed in fallback trigger |
| FR-015 | V1 | M2 | Manual: verify 3-status routing in step 3e |
| FR-020 | V1 | M3 | Manual: verify 9 fields in Return Contract section |
| FR-021 | V1 | M3 | Manual: field-by-field schema audit |
| FR-022 | V1 | M3 | Manual: verify null usage and write-on-failure instruction |
| FR-023 | V1 | M3 | `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` = 0 |
| FR-024 | V1 | M3 | Manual: verify consumption section with guard and routing |
| FR-025 | V1 | M3 | Manual: verify Tier 1 gate section heading and 4 checks |
| FR-017 | V2 | M4 | Manual: verify glossary section before Wave 0 with scope statement |
| FR-018 | V2 | M4 | Manual: verify Wave 1A step 2 uses Skill tool pattern |
| FR-019 | V2 | M4 | `grep -c "sc:adversarial --" adversarial-integration.md` = 0 |
| NFR-001 | V2 | M5 | `make lint` exit code 0 |
| NFR-002 | V2 | M5 | `uv run pytest` exit code 0 |
| NFR-003 | V2 | M5 | `make verify-sync` exit code 0 |
| FR-001 | M6 | M1 | Verification Test 5 (E2E invocation) |
| FR-012..FR-014 | M6 | M2 | Verification Test 7 (fallback protocol validation) |
