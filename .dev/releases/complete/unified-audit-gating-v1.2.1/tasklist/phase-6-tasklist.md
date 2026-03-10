# Phase 6 -- Validation — Context & Gate Infra

Validate M3 (context injection) and M4 (trailing gate) deliverables: context injection correctness, trailing gate thread safety, and gate evaluation performance NFR.

### T06.01 -- Implement Context Injection Correctness Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Context injection correctness must be verified before tasks depend on it — incorrect context causes task N+1 to make decisions based on wrong information about prior work. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0024/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0024/evidence.md

**Deliverables:**
- Context injection test suite covering: prior results summary accuracy, gate outcome inclusion, remediation history presence, progressive summarization correctness

**Steps:**
1. **[PLANNING]** Design test scenarios: 1 task, 5 tasks, 10+ tasks (progressive summarization trigger), mixed outcomes
2. **[PLANNING]** Define expected context content for each scenario
3. **[EXECUTION]** Implement tests verifying prior results summary includes all TaskResult fields
4. **[EXECUTION]** Implement tests verifying gate outcomes and remediation history are present in context
5. **[EXECUTION]** Implement progressive summarization test: context size bounded after compression threshold
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k context_injection_test -v`
7. **[COMPLETION]** Record test output in D-0024/evidence.md

**Acceptance Criteria:**
- Context includes all required fields from prior TaskResults (status, turns, gate outcome)
- Gate outcomes visible in context for preceding tasks (pass/fail/deferred)
- Progressive summarization bounds context size: 10-task context not significantly larger than 5-task context
- `uv run pytest tests/sprint/ -k context_injection_test` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k context_injection_test -v`
- Evidence: test output artifact at D-0024/evidence.md

**Dependencies:** T04.01 (context injection builder), T04.05 (progressive summarization)
**Rollback:** Remove context injection tests

---

### T06.02 -- Implement Trailing Gate Thread Safety Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Thread safety must be proven under concurrent load — race conditions in gate evaluation could cause result loss, incorrect task status, or deadlocks. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (concurrent access), data (result integrity) |
| Tier | STRICT |
| Confidence | [████████──] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0025/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0025/evidence.md

**Deliverables:**
- Thread safety test suite for trailing gate: concurrent submit/drain from multiple threads, pending count accuracy under load, cancel propagation verification, result association by step_id

**Steps:**
1. **[PLANNING]** Design concurrent test scenarios: 3+ threads submitting simultaneously, interleaved submit/drain
2. **[PLANNING]** Define deterministic fixtures with bounded timeouts to avoid flaky tests
3. **[EXECUTION]** Implement concurrent submit/drain test: 3 threads submit, 1 thread drains, verify no result loss
4. **[EXECUTION]** Implement pending_count accuracy test: count matches actual pending items at each check point
5. **[EXECUTION]** Implement cancel propagation test: cancel() terminates all pending evaluations within timeout
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k thread_safety -v` multiple times to detect intermittent failures
7. **[COMPLETION]** Record test output in D-0025/evidence.md

**Acceptance Criteria:**
- No race conditions under concurrent access from ≥3 threads (verified by running test 5+ times)
- Results arrive with correct step_id association (no cross-contamination)
- cancel() terminates pending evaluations within 5-second bounded timeout
- `uv run pytest tests/pipeline/ -k thread_safety` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k thread_safety -v`
- Evidence: test output artifact at D-0025/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner), T05.02 (GateResultQueue)
**Rollback:** Remove thread safety tests

---

### T06.03 -- Implement Gate Performance NFR Benchmark Test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | Gate evaluation must complete in <50ms for 100KB output to avoid becoming a bottleneck in the per-task subprocess loop — slow gates negate trailing benefits. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (latency NFR) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0026/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0026/evidence.md

**Deliverables:**
- Performance benchmark test: `gate_passed()` on synthetic 100KB output must complete in <50ms; TrailingGateResult.evaluation_ms field must be populated with actual timing

**Steps:**
1. **[PLANNING]** Generate synthetic 100KB NDJSON output for benchmark input
2. **[PLANNING]** Define measurement approach: time.perf_counter() around gate_passed() call
3. **[EXECUTION]** Implement timed benchmark test with synthetic 100KB input
4. **[EXECUTION]** Assert evaluation completes in <50ms and evaluation_ms field is populated
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k gate_performance -v` and verify timing assertion
6. **[COMPLETION]** Record benchmark results in D-0026/evidence.md

**Acceptance Criteria:**
- `gate_passed()` on 100KB synthetic output completes in <50ms (timed benchmark)
- TrailingGateResult.evaluation_ms field populated with actual evaluation duration
- Benchmark is deterministic: passes on ≥95% of runs (allows for system load variance)
- `uv run pytest tests/pipeline/ -k gate_performance` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k gate_performance -v`
- Evidence: benchmark results at D-0026/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner with gate_passed())
**Rollback:** Remove performance benchmark test
**Notes:** NFR from roadmap Gap 7: gate evaluation <50ms for 100KB output.

---

### Checkpoint: End of Phase 6

**Purpose:** Confirm context injection and trailing gate infrastructure pass validation before building remediation pipeline.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P06-END.md

**Verification:**
- Context injection tests pass for all scenarios including progressive summarization
- Thread safety tests demonstrate no race conditions under concurrent load
- Gate performance NFR (<50ms for 100KB) met in benchmark

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k context_injection_test -v` exits 0
- `uv run pytest tests/pipeline/ -k "thread_safety or gate_performance" -v` exits 0
- All 3 deliverables (D-0024 through D-0026) have evidence artifacts
