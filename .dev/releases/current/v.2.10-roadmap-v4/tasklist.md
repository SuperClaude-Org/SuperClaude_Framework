# TASKLIST — sc:roadmap Edge Case and Invariant Violation Detection

---

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Generator Version | Roadmap→Tasklist Generator v2.2 |
| Generated Date | 2026-03-04 |
| Roadmap | sc:roadmap Edge Case and Invariant Violation Detection |
| Roadmap Complexity | LOW (0.378) |
| Total Milestones | 4 (M1→M2→M3→M4) |
| Total Roadmap Items | 44 (R-001–R-044) |
| Total Tasks | 44 |
| TASKLIST_ROOT | `.dev/releases/current/v.2.08-roadmap-v4/` |

### Standard Artifact Paths

| Artifact | Path |
|---|---|
| Tasklist | `.dev/releases/current/v.2.08-roadmap-v4/tasklist.md` |
| Execution Log | `.dev/releases/current/v.2.08-roadmap-v4/execution-log.md` |
| Checkpoint Reports | `.dev/releases/current/v.2.08-roadmap-v4/checkpoints/` |
| Evidence | `.dev/releases/current/v.2.08-roadmap-v4/evidence/` |
| Artifacts | `.dev/releases/current/v.2.08-roadmap-v4/artifacts/` |
| Feedback Log | `.dev/releases/current/v.2.08-roadmap-v4/feedback-log.md` |

---

## Source Snapshot

- Roadmap covers 4 milestones: M1 (Deliverable Decomposition and Schema Extension), M2 (State Variable Invariant Registry + FMEA Pass), M3 (Guard and Sentinel Analysis), M4 (Cross-Deliverable Data Flow Tracing).
- Motivated by two source bugs: wrong operand in state mutation (`_loaded_start_index -= mounted` using widget count instead of events_consumed) and boolean-to-integer sentinel ambiguity (`_replayed_event_offset = len(plan.tail_events)` = 0 on empty tail).
- Five proposals (P1=Invariant Registry, P2=FMEA, P3=Guard Analysis, P4=Implement/Verify Pairs, P5=Data Flow Tracing) combined into 4 milestones.
- Three release gate rules enforced: Rule 1 (silent corruption blocks downstream), Rule 2 (guard ambiguity requires named owner + review date), Rule 3 (all .b deliverables must contain at least one state assertion or boundary case).
- Each roadmap item maps 1:1 to a task (44 items → 44 tasks); .a deliverables are implementation tasks, .b deliverables are verification tasks.
- Pilot execution (R-043/R-044) gates general enablement of data flow tracing on evidence-based go/no-go decision.

---

## Deterministic Rules Applied

- **Non-Leakage**: No external context imported; roadmap text and brainstorm context are the sole sources of truth.
- **Phase Buckets**: M1→Phase 1 (T01.xx), M2→Phase 2 (T02.xx), M3→Phase 3 (T03.xx), M4→Phase 4 (T04.xx).
- **Task IDs**: Format `T<PP>.<TT>` zero-padded; sequential within phase in roadmap appearance order.
- **1:1 Mapping**: Each R-001–R-044 maps to exactly one task; no splits required (each item has a single deliverable output).
- **Effort Scoring**: Baseline 0; increments per keyword hits and text length; maps to XS/S/M/L/XL.
- **Risk Scoring**: Baseline 0; increments per risk keyword categories; maps to Low/Medium/High.
- **Tier Classification**: STRICT > EXEMPT > LIGHT > STANDARD priority; scored by keyword weights plus context boosters; schema/model → STRICT; verify/analyze with no STRICT keyword → EXEMPT over STANDARD.
- **Confidence**: max(tier_scores) capped 0.95; -15% if top-2 within 0.1; +15% if compound phrase; <0.70 requires confirmation.
- **Verification Routing**: STRICT→sub-agent quality-engineer 3-5K/60s; STANDARD→direct test 300-500/30s; LIGHT→sanity check ~100/10s; EXEMPT→skip.
- **MCP Requirements**: STRICT→Sequential+Serena required, Context7 preferred, no fallback; STANDARD→Sequential+Context7 preferred, fallback allowed; LIGHT/EXEMPT→none, fallback allowed.
- **Sub-Agent Delegation**: STRICT+High→Required; STRICT OR High→Recommended; otherwise→None.
- **Checkpoints**: After every 5 tasks within a phase and at end of each phase.

---

## Roadmap Item Registry

| Item ID | Deliverable | Description Summary | Phase |
|---|---|---|---|
| R-001 | D1.1a | Define extended deliverable schema with `kind` field and `metadata` attachment point | Phase 1 |
| R-002 | D1.1b | Verify extended deliverable schema (4 test cases) | Phase 1 |
| R-003 | D1.2a | Implement decomposition rule: behavioral deliverables split into D.x.a/D.x.b pairs | Phase 1 |
| R-004 | D1.2b | Verify decomposition rule (5 test cases) | Phase 1 |
| R-005 | D1.3a | Implement behavioral detection heuristic | Phase 1 |
| R-006 | D1.3b | Verify behavioral detection heuristic (6 test cases) | Phase 1 |
| R-007 | D1.4a | Integrate decomposition into roadmap generator pipeline as post-generation pass | Phase 1 |
| R-008 | D1.4b | Verify generator integration (integration test) | Phase 1 |
| R-009 | D2.1a | Implement InvariantEntry data structure with mutation_sites and constrained grammar | Phase 2 |
| R-010 | D2.1b | Verify invariant registry data structure (4 test cases) | Phase 2 |
| R-011 | D2.2a | Implement state variable detector scanning deliverable descriptions | Phase 2 |
| R-012 | D2.2b | Verify state variable detector (5 test cases) | Phase 2 |
| R-013 | D2.3a | Implement mutation inventory generator enumerating code paths writing to variables | Phase 2 |
| R-014 | D2.3b | Verify mutation inventory generator (4 test cases) | Phase 2 |
| R-015 | D2.4a | Implement verification deliverable emitter generating invariant-check deliverables | Phase 2 |
| R-016 | D2.4b | Verify verification deliverable emitter (4 test cases) | Phase 2 |
| R-017 | D2.5a | Implement invariant registry pipeline integration (post-decomposition pass) | Phase 2 |
| R-018 | D2.5b | Verify registry integration (integration test) | Phase 2 |
| R-019 | D2.6a | Implement FMEA input domain enumerator | Phase 2 |
| R-020 | D2.6b | Verify FMEA input domain enumerator (4 test cases) | Phase 2 |
| R-021 | D2.7a | Implement FMEA failure mode classifier with dual detection signal | Phase 2 |
| R-022 | D2.7b | Verify FMEA failure mode classifier (4 test cases) | Phase 2 |
| R-023 | D2.8a | Implement FMEA deliverable promotion above severity threshold | Phase 2 |
| R-024 | D2.8b | Verify FMEA deliverable promotion (5 test cases) | Phase 2 |
| R-025 | D2.9a | Integrate invariant registry + FMEA as combined pipeline pass | Phase 2 |
| R-026 | D2.9b | Verify combined pipeline integration (integration test) | Phase 2 |
| R-027 | D3.1a | Implement guard and sentinel analyzer | Phase 3 |
| R-028 | D3.1b | Verify guard and sentinel analyzer (5 test cases) | Phase 3 |
| R-029 | D3.2a | Implement guard resolution requirement generating guard_test deliverables | Phase 3 |
| R-030 | D3.2b | Verify guard resolution requirement (4 test cases) | Phase 3 |
| R-031 | D3.3a | Integrate guard analysis as post-generation pass after M2 combined pass | Phase 3 |
| R-032 | D3.3b | Verify guard analysis integration (2 integration tests) | Phase 3 |
| R-033 | D4.1a | Implement data flow graph builder (directed graph with cycle detection) | Phase 4 |
| R-034 | D4.1b | Verify data flow graph builder (5 test cases) | Phase 4 |
| R-035 | D4.2a | Implement implicit contract extractor for cross-milestone edges | Phase 4 |
| R-036 | D4.2b | Verify implicit contract extractor (4 test cases) | Phase 4 |
| R-037 | D4.3a | Implement conflict detector flagging divergent writer/reader semantics | Phase 4 |
| R-038 | D4.3b | Verify conflict detector (4 test cases) | Phase 4 |
| R-039 | D4.4a | Implement cross-milestone verification deliverable emitter (contract_test) | Phase 4 |
| R-040 | D4.4b | Verify cross-milestone verification deliverable emitter (4 test cases) | Phase 4 |
| R-041 | D4.5a | Integrate data flow tracing as final post-generation pass | Phase 4 |
| R-042 | D4.5b | Verify data flow tracing integration (2 integration tests) | Phase 4 |
| R-043 | D4.6a | Pilot execution on one high-complexity roadmap (6+ milestones) | Phase 4 |
| R-044 | D4.6b | Pilot go/no-go decision before general enablement | Phase 4 |

---

## Deliverable Registry

| Deliverable ID | Kind | Description | Task ID | Phase |
|---|---|---|---|---|
| D1.1a | implement | Extended deliverable schema with kind field + metadata | T01.01 | Phase 1 |
| D1.1b | verify | Verify extended deliverable schema | T01.02 | Phase 1 |
| D1.2a | implement | Decomposition rule: behavioral → D.x.a/D.x.b pairs | T01.03 | Phase 1 |
| D1.2b | verify | Verify decomposition rule | T01.04 | Phase 1 |
| D1.3a | implement | Behavioral detection heuristic | T01.05 | Phase 1 |
| D1.3b | verify | Verify behavioral detection heuristic | T01.06 | Phase 1 |
| D1.4a | implement | Generator pipeline integration (decomposition pass) | T01.07 | Phase 1 |
| D1.4b | verify | Verify generator integration | T01.08 | Phase 1 |
| D2.1a | implement | InvariantEntry data structure + constrained grammar | T02.01 | Phase 2 |
| D2.1b | verify | Verify invariant registry data structure | T02.02 | Phase 2 |
| D2.2a | implement | State variable detector | T02.03 | Phase 2 |
| D2.2b | verify | Verify state variable detector | T02.04 | Phase 2 |
| D2.3a | implement | Mutation inventory generator | T02.05 | Phase 2 |
| D2.3b | verify | Verify mutation inventory generator | T02.06 | Phase 2 |
| D2.4a | implement | Verification deliverable emitter (invariant_check kind) | T02.07 | Phase 2 |
| D2.4b | verify | Verify verification deliverable emitter | T02.08 | Phase 2 |
| D2.5a | implement | Invariant registry pipeline integration | T02.09 | Phase 2 |
| D2.5b | verify | Verify registry integration | T02.10 | Phase 2 |
| D2.6a | implement | FMEA input domain enumerator | T02.11 | Phase 2 |
| D2.6b | verify | Verify FMEA input domain enumerator | T02.12 | Phase 2 |
| D2.7a | implement | FMEA failure mode classifier (dual detection) | T02.13 | Phase 2 |
| D2.7b | verify | Verify FMEA failure mode classifier | T02.14 | Phase 2 |
| D2.8a | implement | FMEA deliverable promotion | T02.15 | Phase 2 |
| D2.8b | verify | Verify FMEA deliverable promotion | T02.16 | Phase 2 |
| D2.9a | implement | Combined invariant registry + FMEA pipeline pass | T02.17 | Phase 2 |
| D2.9b | verify | Verify combined pipeline integration | T02.18 | Phase 2 |
| D3.1a | implement | Guard and sentinel analyzer | T03.01 | Phase 3 |
| D3.1b | verify | Verify guard and sentinel analyzer | T03.02 | Phase 3 |
| D3.2a | implement | Guard resolution requirement + guard_test emitter | T03.03 | Phase 3 |
| D3.2b | verify | Verify guard resolution requirement | T03.04 | Phase 3 |
| D3.3a | implement | Guard analysis pipeline integration | T03.05 | Phase 3 |
| D3.3b | verify | Verify guard analysis integration | T03.06 | Phase 3 |
| D4.1a | implement | Data flow graph builder | T04.01 | Phase 4 |
| D4.1b | verify | Verify data flow graph builder | T04.02 | Phase 4 |
| D4.2a | implement | Implicit contract extractor | T04.03 | Phase 4 |
| D4.2b | verify | Verify implicit contract extractor | T04.04 | Phase 4 |
| D4.3a | implement | Conflict detector | T04.05 | Phase 4 |
| D4.3b | verify | Verify conflict detector | T04.06 | Phase 4 |
| D4.4a | implement | Cross-milestone verification deliverable emitter (contract_test) | T04.07 | Phase 4 |
| D4.4b | verify | Verify cross-milestone verification deliverable emitter | T04.08 | Phase 4 |
| D4.5a | implement | Data flow tracing final pipeline pass | T04.09 | Phase 4 |
| D4.5b | verify | Verify data flow tracing integration | T04.10 | Phase 4 |
| D4.6a | implement | Pilot execution on high-complexity roadmap | T04.11 | Phase 4 |
| D4.6b | verify | Pilot go/no-go decision (evidence-based) | T04.12 | Phase 4 |

---

## Tasklist Index

| Task ID | Roadmap Item | Deliverable | Tier | Effort | Risk | Confidence | Req. Confirmation | Critical Path |
|---|---|---|---|---|---|---|---|---|
| T01.01 | R-001 | D1.1a | STRICT | M | Low | 0.75 | No | Yes |
| T01.02 | R-002 | D1.1b | EXEMPT | S | Low | 0.72 | No | No |
| T01.03 | R-003 | D1.2a | STANDARD | M | Low | 0.72 | No | Yes |
| T01.04 | R-004 | D1.2b | STANDARD | M | Low | 0.70 | No | No |
| T01.05 | R-005 | D1.3a | STANDARD | M | Low | 0.72 | No | Yes |
| T01.06 | R-006 | D1.3b | STANDARD | M | Low | 0.70 | No | No |
| T01.07 | R-007 | D1.4a | STANDARD | M | Low | 0.70 | No | Yes |
| T01.08 | R-008 | D1.4b | STANDARD | M | Low | 0.70 | No | No |
| T02.01 | R-009 | D2.1a | STRICT | M | Low | 0.75 | No | Yes |
| T02.02 | R-010 | D2.1b | EXEMPT | S | Low | 0.72 | No | No |
| T02.03 | R-011 | D2.2a | STANDARD | M | Low | 0.72 | No | Yes |
| T02.04 | R-012 | D2.2b | STANDARD | S | Low | 0.70 | No | No |
| T02.05 | R-013 | D2.3a | STANDARD | M | Low | 0.72 | No | Yes |
| T02.06 | R-014 | D2.3b | STANDARD | S | Low | 0.70 | No | No |
| T02.07 | R-015 | D2.4a | STANDARD | M | Low | 0.72 | No | Yes |
| T02.08 | R-016 | D2.4b | STANDARD | S | Low | 0.70 | No | No |
| T02.09 | R-017 | D2.5a | STANDARD | M | Low | 0.70 | No | Yes |
| T02.10 | R-018 | D2.5b | STANDARD | S | Low | 0.70 | No | No |
| T02.11 | R-019 | D2.6a | STANDARD | M | Low | 0.72 | No | Yes |
| T02.12 | R-020 | D2.6b | STANDARD | S | Low | 0.70 | No | No |
| T02.13 | R-021 | D2.7a | STANDARD | L | Medium | 0.70 | No | Yes |
| T02.14 | R-022 | D2.7b | STANDARD | M | Medium | 0.70 | No | No |
| T02.15 | R-023 | D2.8a | STANDARD | M | Low | 0.72 | No | Yes |
| T02.16 | R-024 | D2.8b | STANDARD | M | Low | 0.70 | No | No |
| T02.17 | R-025 | D2.9a | STANDARD | L | Low | 0.70 | No | Yes |
| T02.18 | R-026 | D2.9b | STANDARD | M | Low | 0.70 | No | No |
| T03.01 | R-027 | D3.1a | STANDARD | M | Low | 0.72 | No | Yes |
| T03.02 | R-028 | D3.1b | STANDARD | M | Low | 0.70 | No | No |
| T03.03 | R-029 | D3.2a | STANDARD | M | Low | 0.72 | No | Yes |
| T03.04 | R-030 | D3.2b | STANDARD | S | Low | 0.70 | No | No |
| T03.05 | R-031 | D3.3a | STANDARD | M | Low | 0.70 | No | Yes |
| T03.06 | R-032 | D3.3b | STANDARD | M | Low | 0.70 | No | No |
| T04.01 | R-033 | D4.1a | STANDARD | L | Medium | 0.70 | No | Yes |
| T04.02 | R-034 | D4.1b | STANDARD | M | Medium | 0.70 | No | No |
| T04.03 | R-035 | D4.2a | STANDARD | L | Medium | 0.70 | No | Yes |
| T04.04 | R-036 | D4.2b | STANDARD | M | Medium | 0.70 | No | No |
| T04.05 | R-037 | D4.3a | STANDARD | M | Medium | 0.70 | No | Yes |
| T04.06 | R-038 | D4.3b | STANDARD | S | Medium | 0.70 | No | No |
| T04.07 | R-039 | D4.4a | STANDARD | M | Medium | 0.70 | No | Yes |
| T04.08 | R-040 | D4.4b | STANDARD | S | Medium | 0.70 | No | No |
| T04.09 | R-041 | D4.5a | STANDARD | L | Medium | 0.70 | No | Yes |
| T04.10 | R-042 | D4.5b | STANDARD | M | Medium | 0.70 | No | No |
| T04.11 | R-043 | D4.6a | STANDARD | M | Low | 0.72 | No | Yes |
| T04.12 | R-044 | D4.6b | EXEMPT | S | Low | 0.72 | No | Yes |


---

## Phase 1 (M1): Deliverable Decomposition and Schema Extension

### T01.01 — Define Extended Deliverable Schema

| Field | Value |
|---|---|
| Roadmap Item ID | R-001 |
| Deliverable ID | D1.1a |
| Why | Establishes the data contract for all downstream pipeline passes; without a typed `kind` field and `metadata` attachment point, M2–M4 analysis passes have no schema to emit into. |
| Effort | M |
| Risk | Low |
| Risk Drivers | No migration/security keywords; schema change is additive and backward-compatible. |
| Tier | STRICT |
| Confidence | 0.75 |
| Requires Confirmation | No |
| Critical Path Override | Yes — all downstream tasks depend on this schema. |
| Verification Method | Sub-agent (quality-engineer), 3–5K tokens, 60s |
| MCP Requirements | Required: Sequential, Serena \| Preferred: Context7 \| Fallback: No |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Artifacts | `artifacts/D1.1a-schema.py` or equivalent schema module |
| Deliverables | Extended deliverable schema module with `kind` enum (implement, verify, invariant_check, fmea_test, guard_test, contract_test), `metadata` field defaulting to `{}`, `ValueError` on unknown kind, backward-compatible default of `implement` for pre-extension deliverables. |

**Steps**

1. Read existing deliverable data model to identify current fields and serialization format.
2. Define `DeliverableKind` enum with exactly six values: `implement`, `verify`, `invariant_check`, `fmea_test`, `guard_test`, `contract_test`.
3. Add `kind: DeliverableKind = DeliverableKind.implement` field to the deliverable schema.
4. Add `metadata: dict = field(default_factory=dict)` field to the deliverable schema.
5. Add validation: unknown kind string raises `ValueError` with descriptive message.
6. Update serialization/deserialization to round-trip `kind` and `metadata` without loss.
7. Verify backward compatibility: existing deliverables parsed without `kind` field default to `implement`.
8. Run existing schema tests to confirm no regression.

**Acceptance Criteria**

1. Unknown kind string raises `ValueError` with message identifying the invalid value.
2. `metadata` field defaults to empty dict `{}` when not specified.
3. Pre-extension deliverables (no `kind` in source) deserialize with `kind == implement`.
4. Existing roadmap files parse without error after schema extension.

**Validation**

1. Execute unit test suite covering all six kind values and unknown-kind error path; all tests pass.
2. Parse a pre-extension roadmap fixture; confirm zero errors and all deliverables carry `kind == implement`.

**Dependencies** | None (first task in phase)
**Rollback** | Revert schema module to pre-extension version; downstream tasks blocked until re-applied.
**Notes** | Effort scored M: text ≥120 chars (+1), `schema` keyword (+1) = 2 → M. Risk Low: no migration/security keywords. Tier STRICT: `schema` keyword triggers STRICT (+0.4), max score 0.4, compound phrase +15% → 0.75 confidence. Sub-agent delegation Recommended (STRICT, Low risk).

---

### T01.02 — Verify Extended Deliverable Schema

| Field | Value |
|---|---|
| Roadmap Item ID | R-002 |
| Deliverable ID | D1.1b |
| Why | Provides contractual evidence that the schema extension behaves correctly for all four specified cases before downstream passes build on it. |
| Effort | S |
| Risk | Low |
| Risk Drivers | Read-only test authoring; no production state mutations. |
| Tier | EXEMPT |
| Confidence | 0.72 |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification (EXEMPT), 0 tokens, 0s |
| MCP Requirements | None \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.1b-schema-tests.py` |
| Deliverables | Test suite with exactly 4 test cases covering: unknown kind raises ValueError, metadata defaults to empty dict, pre-extension deliverables default to implement, backward-compatible parse of existing roadmaps. |

**Steps**

1. Create test file for schema verification in `tests/` directory.
2. Write test: construct deliverable with unknown kind string; assert `ValueError` raised.
3. Write test: construct deliverable without `metadata`; assert `metadata == {}`.
4. Write test: parse deliverable fixture without `kind` field; assert `kind == implement`.
5. Write test: parse existing roadmap fixture; assert no exceptions raised.

**Acceptance Criteria**

1. Test case for unknown kind executes and `ValueError` is raised with non-empty message.
2. Test case for metadata default executes and `metadata` equals `{}`.
3. Test case for pre-extension default executes and `kind` equals `implement`.
4. Test case for backward compatibility executes and existing roadmap parses without error.

**Validation**

1. Run `uv run pytest` on the schema test file; all 4 tests pass with zero failures.
2. Confirm test file contains at least one state assertion (per Release Gate Rule 3).

**Dependencies** | T01.01 (schema must exist before tests can be written)
**Rollback** | Delete test file; no production impact.
**Notes** | Effort S: text <120 chars for test descriptions, no effort keywords = 0 → XS, bump to S for explicit 4-test enumeration. Tier EXEMPT: `verify` maps to analyze/review → EXEMPT (+0.4); `tests/` path → STANDARD (+0.2); EXEMPT > STANDARD per priority → EXEMPT; confidence 0.72. Release Gate Rule 3: each .b deliverable must contain at least one state assertion — enforced in acceptance criteria.

---

### T01.03 — Implement Decomposition Rule

| Field | Value |
|---|---|
| Roadmap Item ID | R-003 |
| Deliverable ID | D1.2a |
| Why | Enables the generator to automatically split behavioral deliverables into implement/verify pairs, which is the foundation for M2–M4 analysis passes that require paired deliverables. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Logic-only transformation; no external state or migrations. |
| Tier | STANDARD |
| Confidence | 0.72 |
| Requires Confirmation | No |
| Critical Path Override | Yes — decomposition is required before invariant registry and FMEA can run. |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.2a-decomposer.py` |
| Deliverables | `decompose_deliverables(deliverables: list[Deliverable]) -> list[Deliverable]` function that: splits behavioral deliverables into D.x.a (Implement) and D.x.b (Verify) pairs; passes non-behavioral through unchanged; appends `.a`/`.b` suffixes correctly; is idempotent on already-decomposed input. |

**Steps**

1. Define function signature `decompose_deliverables(deliverables: list[Deliverable]) -> list[Deliverable]`.
2. Implement behavioral check: call `is_behavioral(deliverable.description)` (from D1.3a); if False, pass through unchanged.
3. For behavioral deliverables, create D.x.a copy with `kind=implement` and ID suffix `.a`.
4. For behavioral deliverables, create D.x.b copy with `kind=verify` and ID suffix `.b`; description references D.x.a by ID.
5. Implement idempotency guard: skip decomposition if deliverable ID already ends in `.a` or `.b`.
6. Preserve relative ordering of deliverables within their milestone.
7. Return flattened list with pairs inserted in place of original behavioral deliverables.

**Acceptance Criteria**

1. 3 behavioral deliverables in input produce exactly 6 deliverables in output.
2. Non-behavioral deliverables pass through with unchanged ID, description, and kind.
3. Already-decomposed deliverables (IDs ending in `.a`/`.b`) are not re-decomposed.
4. Output ordering is consistent with input milestone ordering (behavioral pairs appear at their original position).

**Validation**

1. Run unit tests with fixture of 3 behavioral + 2 non-behavioral; assert output length == 8 and structure matches expected pairs.
2. Run idempotency test: decompose output a second time; assert output is identical to first decomposition.

**Dependencies** | T01.01 (schema with kind field), T01.05 (is_behavioral heuristic — may be stubbed initially)
**Rollback** | Remove decomposition function; generator pipeline reverts to undecomposed output.
**Notes** | Effort M: text ≥120 chars (+1), `implement` keyword (+1) = 2 → M. Risk Low: no risk keywords. Tier STANDARD: `implement` (+0.2) is highest scoring keyword; confidence 0.72.

---

### T01.04 — Verify Decomposition Rule

| Field | Value |
|---|---|
| Roadmap Item ID | R-004 |
| Deliverable ID | D1.2b |
| Why | Provides contractual evidence for all five decomposition edge cases before the pipeline integration task (T01.07) depends on it. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Test authoring with multiple fixture shapes; no production mutations. |
| Tier | STANDARD |
| Confidence | 0.70 |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.2b-decomposer-tests.py` |
| Deliverables | Test suite with exactly 5 test cases: (1) 3 behavioral → 6 output, (2) 2 behavioral + 1 doc → 5 output, (3) empty → empty, (4) already-decomposed not re-decomposed, (5) Verify description references Implement deliverable by ID. |

**Steps**

1. Create test file for decomposition verification.
2. Write test 1: 3 behavioral deliverables input; assert output list length == 6.
3. Write test 2: 2 behavioral + 1 doc deliverable; assert output list length == 5; doc unchanged.
4. Write test 3: empty list input; assert output is empty list.
5. Write test 4: already-decomposed input (IDs with `.a`/`.b` suffix); assert no new splits.
6. Write test 5: verify D.x.b description contains string referencing D.x.a ID.

**Acceptance Criteria**

1. All 5 test cases execute without error and produce correct assertions.
2. Test 5 contains at least one state assertion confirming ID cross-reference (Release Gate Rule 3).
3. Test 2 confirms the doc deliverable passes through with original kind and ID intact.
4. Test 4 confirms idempotency: output length equals input length when already-decomposed.

**Validation**

1. Run `uv run pytest` on test file; all 5 tests pass.
2. Confirm test 5 contains an explicit string-match assertion on the `.b` deliverable description.

**Dependencies** | T01.03 (decompose_deliverables function must exist)
**Rollback** | Delete test file; no production impact.
**Notes** | Effort M: text ≥120 chars (+1), multiple test fixtures add complexity = 1 → M. Tier STANDARD: `verify` maps to EXEMPT but tests/ path gives STANDARD +0.2; however R-004 text uses "verify decomposition rule" and "tests" together — EXEMPT vs STANDARD within 0.1 → -15% confidence → 0.70. Release Gate Rule 3 enforced in test 5.

---

### T01.05 — Implement Behavioral Detection Heuristic

| Field | Value |
|---|---|
| Roadmap Item ID | R-005 |
| Deliverable ID | D1.3a |
| Why | The decomposition pass (T01.03) cannot classify deliverables without a reliable `is_behavioral` predicate; this heuristic is the classification engine. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Text pattern matching logic; no external state dependencies. |
| Tier | STANDARD |
| Confidence | 0.72 |
| Requires Confirmation | No |
| Critical Path Override | Yes — T01.03 depends on this function. |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.3a-heuristic.py` |
| Deliverables | `is_behavioral(description: str) -> bool` function that detects: computational verbs (e.g., compute, calculate, update, increment, advance), state mutation patterns (`self._*` assignments), conditional logic patterns (guard, sentinel, flag, early return). Returns boolean. |

**Steps**

1. Define function signature `is_behavioral(description: str) -> bool`.
2. Implement computational verb detection: regex or keyword set scan for verbs such as compute, calculate, update, increment, advance, reset, replace, set, mutate.
3. Implement state mutation pattern detection: scan for `self._` substring indicating instance variable assignment.
4. Implement conditional logic detection: keyword scan for guard, sentinel, flag, early return.
5. Return `True` if any detection signal fires; return `False` otherwise.
6. Handle empty string input: return `False`.

**Acceptance Criteria**

1. `is_behavioral("Replace boolean with int offset")` returns `True`.
2. `is_behavioral("Document API endpoint")` returns `False`.
3. `is_behavioral("Add type definition")` returns `False`.
4. `is_behavioral("")` returns `False`.

**Validation**

1. Run unit tests using all 6 test cases from R-006 roadmap item (anticipating T01.06 test file); all pass.
2. Confirm function returns bool type (not truthy/falsy object) for all inputs.

**Dependencies** | T01.01 (schema awareness; function is logically independent but schema context useful)
**Rollback** | Remove `is_behavioral` function; T01.03 decomposition falls back to treating all deliverables as non-behavioral (safe no-op).
**Notes** | Effort M: text ≥120 chars (+1), `implement` (+1) = 2 → M. Risk Low. Tier STANDARD: `implement` is primary keyword.

---

### CHECKPOINT CP-01.A (after T01.01–T01.05)

| Field | Value |
|---|---|
| Checkpoint ID | CP-01.A |
| After Task | T01.05 |
| Tasks Covered | T01.01, T01.02, T01.03, T01.04, T01.05 |
| Report Path | `.dev/releases/current/v.2.08-roadmap-v4/checkpoints/CP-01.A.md` |

**Gate Criteria**
- [ ] T01.01: Extended deliverable schema implemented and passes sub-agent verification.
- [ ] T01.02: All 4 schema test cases pass.
- [ ] T01.03: `decompose_deliverables` function implemented.
- [ ] T01.04: All 5 decomposition test cases pass.
- [ ] T01.05: `is_behavioral` function implemented.
- [ ] No STRICT-tier tasks have open verification failures.
- [ ] All .b deliverables through this checkpoint contain at least one state assertion (Release Gate Rule 3).

---

### T01.06 — Verify Behavioral Detection Heuristic

| Field | Value |
|---|---|
| Roadmap Item ID | R-006 |
| Deliverable ID | D1.3b |
| Why | Confirms the heuristic correctly classifies both positive and negative cases, preventing false positives that would generate spurious verify deliverables and false negatives that would miss behavioral analysis. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Test-only; no production mutations. |
| Tier | STANDARD |
| Confidence | 0.70 |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.3b-heuristic-tests.py` |
| Deliverables | Test suite with exactly 6 test cases: (1) "Replace boolean with int offset" → behavioral, (2) "Document API endpoint" → not behavioral, (3) "Add type definition" → not behavioral, (4) "Implement retry with bounded attempts" → behavioral, (5) "Update README" → not behavioral, (6) empty string → false. |

**Steps**

1. Create test file for behavioral heuristic verification.
2. Write test 1: assert `is_behavioral("Replace boolean with int offset") == True`.
3. Write test 2: assert `is_behavioral("Document API endpoint") == False`.
4. Write test 3: assert `is_behavioral("Add type definition") == False`.
5. Write test 4: assert `is_behavioral("Implement retry with bounded attempts") == True`.
6. Write test 5: assert `is_behavioral("Update README") == False`.
7. Write test 6: assert `is_behavioral("") == False`.

**Acceptance Criteria**

1. All 6 test cases pass with deterministic inputs and outputs.
2. Tests 1 and 4 (behavioral positives) each contain a state assertion confirming `True` return (Release Gate Rule 3).
3. Tests 2, 3, 5, 6 (non-behavioral) confirm `False` return.
4. No test uses `assert result` (truthy check); all use `assert result == True` or `assert result == False` for explicit verification.

**Validation**

1. Run `uv run pytest` on test file; all 6 tests pass with zero failures.
2. Confirm test 4 ("Implement retry with bounded attempts") correctly classifies as behavioral, validating the computational verb detection path.

**Dependencies** | T01.05 (`is_behavioral` function must exist)
**Rollback** | Delete test file; no production impact.
**Notes** | Effort M: 6 distinct test fixtures = significant authoring effort. Tier STANDARD: `verify` vs EXEMPT balanced by `tests/` path STANDARD booster; top-2 scores within 0.1 → -15% → 0.70 confidence.

---

### T01.07 — Integrate Decomposition into Generator Pipeline

| Field | Value |
|---|---|
| Roadmap Item ID | R-007 |
| Deliverable ID | D1.4a |
| Why | Without pipeline integration, the decomposition function exists in isolation; this task connects it to the roadmap generator so all future roadmap runs automatically produce implement/verify pairs. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Integration changes touch the generator pipeline; idempotency requirement reduces regression risk. |
| Tier | STANDARD |
| Confidence | 0.70 |
| Requires Confirmation | No |
| Critical Path Override | Yes — M2 invariant registry pipeline (T02.09) runs after this pass. |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.4a-pipeline-integration.py` |
| Deliverables | Generator pipeline modified to call `decompose_deliverables` as a post-generation pass: runs after deliverable generation, before output formatting, is idempotent, preserves deliverable ordering within each milestone. |

**Steps**

1. Locate the roadmap generator pipeline entry point and identify post-generation stage.
2. Register `decompose_deliverables` as a named post-generation pass in the pipeline.
3. Ensure the pass runs after deliverable generation is complete.
4. Ensure the pass runs before output formatting (serialization).
5. Verify idempotency: running the pass twice on the same generator output produces identical results.
6. Verify milestone ordering: pairs appear at the original deliverable's position within the milestone.

**Acceptance Criteria**

1. Generator produces Implement/Verify pairs for all behavioral deliverables in a known test spec.
2. Non-behavioral deliverables in the same spec are unchanged after pipeline run.
3. Milestone structure (ordering, membership) is preserved — pairs appear in place of the original.
4. Running the pipeline twice on the same input produces identical output (idempotency).

**Validation**

1. Run integration test with known spec containing mix of behavioral and non-behavioral deliverables; assert output structure matches expectation.
2. Run pipeline twice on same input; diff outputs; assert diff is empty.

**Dependencies** | T01.03 (`decompose_deliverables`), T01.05 (`is_behavioral`)
**Rollback** | Remove pass registration from pipeline; generator reverts to undecomposed output with no behavioral classification.
**Notes** | Effort M: text ≥120 chars (+1), `integrate` (+1 from pipeline/infra adjacent) = 2 → M. Tier STANDARD: `implement`, `integrate` keywords dominant.

---

### T01.08 — Verify Generator Integration

| Field | Value |
|---|---|
| Roadmap Item ID | R-008 |
| Deliverable ID | D1.4b |
| Why | Provides end-to-end evidence that the full M1 pipeline produces correct output before M2 passes are layered on top; validates Release Gate Rule 3 compliance for the first pass. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Integration test scope touches full pipeline; no production data at risk. |
| Tier | STANDARD |
| Confidence | 0.70 |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300–500 tokens, 30s |
| MCP Requirements | Preferred: Sequential, Context7 \| Fallback: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Artifacts | `artifacts/D1.4b-integration-test.py` |
| Deliverables | Integration test: known spec → output contains Implement/Verify pairs for all behavioral deliverables; non-behavioral unchanged; milestone structure preserved. Exit criterion: all .b deliverables contain at least one state assertion or boundary case (Release Gate Rule 3). |

**Steps**

1. Create integration test file using a known-spec fixture with at least 3 behavioral and 2 non-behavioral deliverables.
2. Run generator pipeline on fixture; capture output deliverable list.
3. Assert all behavioral deliverables produce D.x.a (Implement) + D.x.b (Verify) pairs.
4. Assert all non-behavioral deliverables are present unchanged.
5. Assert milestone structure is preserved (deliverable count per milestone is correct).
6. Assert every D.x.b deliverable in output contains at least one state assertion or boundary case in its description (Release Gate Rule 3).

**Acceptance Criteria**

1. All behavioral deliverables in known spec produce exactly one Implement + one Verify pair each.
2. Non-behavioral deliverables pass through without modification to ID, description, or kind.
3. Milestone structure (deliverable counts per milestone) matches expected values.
4. Every .b deliverable description contains at least one state assertion or boundary case keyword (Release Gate Rule 3).

**Validation**

1. Run `uv run pytest` on integration test; all assertions pass.
2. Manually inspect one generated .b deliverable description to confirm state assertion presence.

**Dependencies** | T01.07 (pipeline integration must be complete)
**Rollback** | Delete integration test file; pipeline remains as-is.
**Notes** | Effort M: integration test with multiple assertions = moderate complexity. Tier STANDARD: `verify`, `integration` keywords; EXEMPT vs STANDARD; tests/ path booster → STANDARD. Release Gate Rule 3 explicitly enforced in step 6 and acceptance criterion 4.

---

### CHECKPOINT CP-01.B (End of Phase 1)

| Field | Value |
|---|---|
| Checkpoint ID | CP-01.B |
| After Task | T01.08 |
| Tasks Covered | T01.06, T01.07, T01.08 (+ cumulative from CP-01.A) |
| Report Path | `.dev/releases/current/v.2.08-roadmap-v4/checkpoints/CP-01.B.md` |

**Gate Criteria**
- [ ] T01.06: All 6 behavioral heuristic test cases pass.
- [ ] T01.07: Pipeline integration verified idempotent; milestone ordering preserved.
- [ ] T01.08: Integration test confirms Implement/Verify pairs for all behavioral deliverables.
- [ ] Release Gate Rule 3: All .b deliverables (D1.1b, D1.2b, D1.3b, D1.4b) contain at least one state assertion or boundary case.
- [ ] No open STRICT-tier verification failures.
- [ ] Phase 1 complete — Phase 2 unblocked.

