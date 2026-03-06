# Phase 9 -- Final Validation — E2E Acceptance

End-to-end acceptance testing of the complete unified solution: budget economics, per-task subprocess, trailing gates, remediation, diagnostic chain, and backward compatibility. This phase validates all success criteria.

### T09.01 -- Implement End-to-End Sprint Test with Trailing Gates

| Field | Value |
|---|---|
| Roadmap Item IDs | R-049 |
| Why | An end-to-end test exercising the complete flow (budget → subprocess → gate → remediation → context → report) validates the system works as an integrated whole, not just individual components. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | end-to-end (complete system), system-wide (all components) |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0038/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0038/evidence.md

**Deliverables:**
- End-to-end sprint test with trailing gates enabled: multi-task sprint exercising budget allocation, per-task subprocess, gate evaluation, remediation, context injection, and phase report generation

**Steps:**
1. **[PLANNING]** Design E2E test scenario: multi-task sprint with mixed outcomes triggering all major code paths
2. **[PLANNING]** Define mock boundaries: mock Claude subprocess, use real sprint runner with all components
3. **[EXECUTION]** Implement E2E test: configure trailing gates (grace_period > 0), run multi-task sprint
4. **[EXECUTION]** Assert: correct per-task results, budget accounting verified, no silent incompletion, context injected
5. **[EXECUTION]** Assert: gate evaluation recorded per task, remediation triggered on failure, phase report accurate
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k e2e_trailing -v`
7. **[COMPLETION]** Record test output in D-0038/evidence.md

**Acceptance Criteria:**
- Multi-task sprint completes with correct per-task results under trailing gate mode
- Budget accounting verified: total consumed + remaining == initial budget (accounting identity)
- No silent incompletion: error_max_turns scenarios correctly trigger INCOMPLETE + HALT
- `uv run pytest tests/sprint/ -k e2e_trailing` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k e2e_trailing -v`
- Evidence: test output artifact at D-0038/evidence.md

**Dependencies:** All Phase 1-8 deliverables
**Rollback:** Remove E2E test

---

### T09.02 -- Implement Backward Compatibility Regression (grace_period=0)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-050 |
| Why | The complete system with grace_period=0 must produce output identical to v1.2.1 — any behavioral divergence indicates a regression that could break existing users. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking (backward compatibility), rollback |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0039/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0039/evidence.md

**Deliverables:**
- Backward compatibility regression test: grace_period=0 sprint produces identical results to v1.2.1 baseline; zero daemon threads; all existing tests pass without modification

**Steps:**
1. **[PLANNING]** Capture v1.2.1 baseline: expected output, thread count, result format for reference scenario
2. **[PLANNING]** Define comparison criteria: byte-for-byte result equivalence, thread count, timing bounds
3. **[EXECUTION]** Run complete sprint with grace_period=0 and compare all outputs to v1.2.1 baseline
4. **[EXECUTION]** Assert `threading.active_count()` shows zero daemon threads from gate/remediation system
5. **[EXECUTION]** Run all existing v1.2.1 sprint tests to confirm no modifications needed
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -v` (full suite — all tests must pass)
7. **[COMPLETION]** Record comparison results in D-0039/evidence.md

**Acceptance Criteria:**
- grace_period=0 sprint results are equivalent to v1.2.1 baseline output
- `threading.active_count()` shows zero additional daemon threads beyond v1.2.1 baseline
- All existing sprint tests pass without modification under the new architecture
- `uv run pytest tests/sprint/ -v` exits 0 with zero failures

**Validation:**
- `uv run pytest tests/sprint/ -v`
- Evidence: comparison artifact at D-0039/evidence.md

**Dependencies:** All Phase 1-8 deliverables
**Rollback:** N/A (this is a validation task)
**Notes:** STRICT tier due to backward compatibility verification (breaking keyword).

---

### T09.03 -- Implement Property-Based Tests for TurnLedger Invariants

| Field | Value |
|---|---|
| Roadmap Item IDs | R-051 |
| Why | Property-based tests validate system invariants across randomized inputs, catching edge cases that example-based tests miss — critical for TurnLedger arithmetic and gate ordering. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (randomized inputs) |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0040/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0040/evidence.md

**Deliverables:**
- Property-based tests using hypothesis (or equivalent): TurnLedger budget monotonicity invariant, gate result ordering invariant, remediation idempotency property

**Steps:**
1. **[PLANNING]** Define properties: budget monotonicity (consumed never decreases), gate ordering (results ordered by submission), remediation idempotency
2. **[PLANNING]** Choose property-based testing framework (hypothesis recommended)
3. **[EXECUTION]** Implement TurnLedger monotonicity property: for any sequence of debit/credit operations, consumed never decreases
4. **[EXECUTION]** Implement gate result ordering property: results from GateResultQueue arrive in submission order per step_id
5. **[EXECUTION]** Implement remediation idempotency property: marking same entry remediated twice produces same state
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k property_based -v` with sufficient examples (≥100 per property)
7. **[COMPLETION]** Record property test results in D-0040/evidence.md

**Acceptance Criteria:**
- Budget monotonicity property holds across ≥100 randomized operation sequences
- Gate result ordering property holds across ≥100 randomized concurrent submission scenarios
- Remediation idempotency property holds: double mark_remediated produces identical state
- `uv run pytest tests/ -k property_based` exits 0

**Validation:**
- `uv run pytest tests/ -k property_based -v`
- Evidence: property test results at D-0040/evidence.md

**Dependencies:** T01.01 (TurnLedger), T05.02 (GateResultQueue), T05.03 (DeferredRemediationLog)
**Rollback:** Remove property-based tests

---

### T09.04 -- Implement Performance NFR Validation Benchmarks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-052 |
| Why | Performance NFRs must be validated under controlled conditions: gate evaluation <50ms on 100KB output and budget calculations O(1) ensure the system scales without degradation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (NFR validation) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0041/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0041/evidence.md

**Deliverables:**
- Performance NFR benchmarks: gate evaluation timing (<50ms for 100KB output), TurnLedger operation timing (O(1) constant time regardless of operation count)

**Steps:**
1. **[PLANNING]** Define benchmark inputs: 100KB synthetic output for gate, varying operation counts for TurnLedger
2. **[PLANNING]** Define NFR thresholds: gate <50ms, TurnLedger operations constant within 2x variance
3. **[EXECUTION]** Implement gate benchmark: time gate_passed() on 100KB output, assert <50ms
4. **[EXECUTION]** Implement TurnLedger benchmark: time debit/credit/available at 10, 100, 1000 operations, assert O(1)
5. **[VERIFICATION]** Run `uv run pytest tests/ -k "nfr_benchmark or performance_nfr" -v`
6. **[COMPLETION]** Record benchmark results in D-0041/evidence.md

**Acceptance Criteria:**
- Gate evaluation completes in <50ms on 100KB synthetic output (p95 across 10 runs)
- TurnLedger debit/credit/available operations are O(1): time at 1000 ops within 2x of time at 10 ops
- Benchmarks are deterministic: pass on ≥95% of runs
- `uv run pytest tests/ -k nfr_benchmark` exits 0

**Validation:**
- `uv run pytest tests/ -k "nfr_benchmark or performance_nfr" -v`
- Evidence: benchmark results at D-0041/evidence.md

**Dependencies:** T01.01 (TurnLedger), T05.01 (gate_passed)
**Rollback:** Remove NFR benchmarks
**Notes:** SC-007 validation: gate evaluation <50ms for 100KB output.

---

### Checkpoint: End of Phase 9

**Purpose:** Final validation gate: confirm all success criteria are met and the system is ready for release.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P09-END.md

**Verification:**
- End-to-end sprint test passes with trailing gates and correct budget accounting
- Backward compatibility regression confirms grace_period=0 equivalence to v1.2.1
- Property-based tests and NFR benchmarks pass across randomized and controlled inputs

**Exit Criteria:**
- `uv run pytest tests/ -v` exits 0 (entire test suite)
- All 4 deliverables (D-0038 through D-0041) have evidence artifacts
- All 7 success criteria (SC-001 through SC-007) validated with evidence
