---
spec_source: .dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md
generated: 2026-02-24T00:00:00Z
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 5
work_milestones: 5
interleave_ratio: "1:1"
major_issue_policy: stop-and-fix
complexity_class: HIGH
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:1** (one validation milestone per one work milestone), derived from complexity class **HIGH** (0.727)

**Why 1:1 for this project**: The v2.01 Architecture Refactor has a critical partial-application risk (RISK-001) where incomplete changes break all invocation wiring. The 68-file incident that triggered the rollback demonstrates the cost of deferred validation. Every work milestone is validated before the next begins.

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (M2) | M1: Foundation & Environment Probe | Probe result deterministic; prerequisites verified; no rogue staged changes | Probe result contradicts D-0001 (requires variant redesign) |
| V2 (M4) | M3: Invocation Wiring & Activation Fix | 8-point audit passes; activation chain loads skill; `allowed-tools` includes `Skill` | Any audit point fails; activation chain silent-skips skill invocation |
| V3 (M6) | M5: Build System Enforcement | `make lint-architecture` exits 0; positive and negative cases work; Makefile heuristics removed | Any ERROR-severity lint check fails on compliant tree |
| V4 (M8) | M7: Structural Validation & Testing | Return contract routing covers 3 paths; adversarial fallback produces valid YAML; artifact gates defined | Return contract misroutes convergence scores; fallback protocol produces no output |
| V5 (M10) | M9: Polish, Integration & Closure | All 10 success criteria pass; zero stale references; full regression green | Any SC-### criterion fails; stale references found |

**Placement rule**: Validation milestones are placed after every 1 work milestone per the 1:1 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Broken invocation chain (activation loads wrong skill); partial application detected (command updated, skill not renamed); `make lint-architecture` reports ERROR on compliant tree |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing `Skill` in `allowed-tools`; return contract parse failure; stale path reference in active code path |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Documentation gap in verb-to-tool glossary; style inconsistency in SKILL.md frontmatter; non-blocking WARN from lint |
| Info | Log only, no action required | N/A | Alternative design approach noted; optimization opportunity for future `claude -p` implementation; v2.02 backlog item identified |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | Probe result documented; prerequisites validated per §15 Day 1 procedure | D1.1-D1.3 all complete with documented evidence |
| M3 | `Skill` in `allowed-tools` for both command and SKILL.md; `## Activation` references `Skill sc:roadmap-protocol`; Wave 2 Step 3 has 6 sub-steps | D3.1-D3.5 all complete; 8-point audit ready for M4 |
| M5 | `make lint-architecture` target exists with 6 checks; exits 0 on current tree; heuristics removed | D5.1-D5.4 all complete; both positive and negative lint tests queued for M6 |
| M7 | Return contract tests pass for 3 routing paths; adversarial integration test passes; artifact gates documented | D7.1-D7.3 all complete; zero Critical issues |
| M9 | All 4 remaining commands updated atomically; `task-unified.md` ≤106 lines; BUGs 002-005 fixed | D9.1-D9.8 all complete; `make sync-dev && make verify-sync` pass |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 (M2) | M1 | Verify `docs/architecture/command-skill-policy.md` exists and is non-empty |
| FR-002 | V5 (M10) | M9 | `ls src/superclaude/skills/sc-*-protocol/` confirms 5 `-protocol` directories |
| FR-003 | V2 (M4), V5 (M10) | M3, M9 | `grep "## Activation" src/superclaude/commands/*.md` returns 5 results |
| FR-004 | V3 (M6) | M5 | `make lint-architecture` exits 0; negative test exits 1 |
| FR-005 | V3 (M6) | M5 | Verify 4-line skip heuristic absent from Makefile `sync-dev` target |
| FR-006 | V3 (M6) | M5 | Verify 5-line skip heuristic absent from Makefile `verify-sync` target |
| FR-007 | V4 (M8) | M7 | Adversarial integration test exercises F1/F2-3/F4-5 fallback path |
| FR-008 | V4 (M8) | M7 | Return contract consumer test validates 10 fields with correct types |
| FR-009 | V2 (M4), V5 (M10) | M3, M9 | `grep "Skill" src/superclaude/commands/*.md` in `allowed-tools` returns 5 results |
| FR-010 | V2 (M4) | M3 | `grep "Skill sc:roadmap-protocol" src/superclaude/commands/roadmap.md` matches |
| FR-011 | V5 (M10) | M9 | `validate-tests.md` line 63 references `sc-validate-tests-protocol/` |
| FR-012 | V5 (M10) | M9 | All threshold references align to `>= 3` |
| FR-013 | V5 (M10) | M9 | Single canonical policy at `docs/architecture/`; symlink from `src/superclaude/` |
| FR-014 | V5 (M10) | M9 | Wave 0 Step 5 references `sc-adversarial-protocol/SKILL.md` |
| FR-015 | V2 (M4) | M3 | Wave 2 Step 3 has exactly 6 sub-steps (3a-3f) with verb→tool mappings |
| FR-016 | V1 (M2) | M1 | Probe result documented with variant decision |
| FR-017 | V5 (M10) | M9 | Cross-skill invocation pattern document exists |
| FR-018 | V5 (M10) | M9 | Tier 2 ref loader design document exists |
| FR-019 | V5 (M10) | M9 | `wc -l src/superclaude/commands/task-unified.md` ≤ 106 |
| FR-020 | V5 (M10) | M9 | All 4 remaining commands pass activation and `allowed-tools` checks |
| FR-024 | V4 (M8) | M7 | Consumer routing tests pass for convergence scores 0.7, 0.55, 0.3 |
| FR-025 | V4 (M8) | M7 | Adversarial pipeline test produces valid `return-contract.yaml` |
| FR-021 | V5 (M10) | M9 | Verb-to-tool glossary document exists with entries for "Invoke", "Dispatch", "Load" |
| FR-022 | V5 (M10) | M9 | Wave 1A Step 2 references match updated return contract schema fields |
| FR-023 | V5 (M10) | M9 | Zero pseudo-CLI patterns remain; all converted to executable tool bindings |
| FR-026 | V4 (M8) | M7 | Artifact gate spec document exists with gate criteria for all 3 artifacts |
| NFR-001 | V5 (M10) | M9 | All paired command files ≤350 lines (`wc -l` check) |
| NFR-004 | V2 (M4), V5 (M10) | M3, M9 | Each command update applied as atomic group; `make verify-sync` confirms |
| NFR-005 | V3 (M6) | M5 | `make lint-architecture` exits 1 when ERROR condition injected |
| NFR-006 | V5 (M10) | M10 | Full regression pass with zero partial-application artifacts |

---

*Test strategy generated by sc:roadmap — 1:1 interleave (HIGH complexity), 5 validation milestones, continuous parallel validation philosophy*
