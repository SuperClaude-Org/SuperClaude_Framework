# Phase 1 - Create & Verify

This phase creates a test file, writes content to it, and verifies the defaults are correct via Python import.

---

### T01.01 -- Create smoke test output file

| Field | Value |
|---|---|
| Effort | XS |
| Risk | Low |
| Tier | STANDARD |
| Verification Method | Direct test execution |
| Deliverable IDs | D-0001 |

**Deliverables:**
- Create the file `.dev/releases/current/smoke-test-sprint/artifacts/smoke-output.txt` containing the text "SMOKE_TEST_PHASE_1_OK" on the first line and the current ISO timestamp on the second line.

**Steps:**
1. Create the artifacts directory if it does not exist: `.dev/releases/current/smoke-test-sprint/artifacts/`
2. Write the file `.dev/releases/current/smoke-test-sprint/artifacts/smoke-output.txt` with content: line 1 = `SMOKE_TEST_PHASE_1_OK`, line 2 = current ISO timestamp
3. Verify the file exists and contains the expected first line

**Acceptance Criteria:**
- File `.dev/releases/current/smoke-test-sprint/artifacts/smoke-output.txt` exists
- First line is exactly `SMOKE_TEST_PHASE_1_OK`

**Dependencies:** None

---

### T01.02 -- Verify pipeline defaults via Python import

| Field | Value |
|---|---|
| Effort | XS |
| Risk | Low |
| Tier | STRICT |
| Verification Method | Sub-agent (quality-engineer) |
| Deliverable IDs | D-0002 |

**Deliverables:**
- Run a Python verification that imports PipelineConfig, SprintConfig, and TurnLedger, instantiates each, and confirms max_turns==100 and reimbursement_rate==0.8. Write results to `.dev/releases/current/smoke-test-sprint/artifacts/defaults-check.txt`.

**Steps:**
1. Run `uv run python -c` to import and check: `from superclaude.cli.pipeline.models import PipelineConfig; from superclaude.cli.sprint.models import SprintConfig, TurnLedger; pc=PipelineConfig(); sc=SprintConfig(index_path='/dev/null'); tl=TurnLedger(initial_budget=200); assert pc.max_turns==100; assert sc.max_turns==100; assert tl.reimbursement_rate==0.8; print('ALL_DEFAULTS_OK')`
2. Write the output to `.dev/releases/current/smoke-test-sprint/artifacts/defaults-check.txt`
3. Verify the file contains `ALL_DEFAULTS_OK`

**Acceptance Criteria:**
- File `.dev/releases/current/smoke-test-sprint/artifacts/defaults-check.txt` contains `ALL_DEFAULTS_OK`
- PipelineConfig().max_turns == 100
- SprintConfig(index_path='/dev/null').max_turns == 100
- TurnLedger(initial_budget=200).reimbursement_rate == 0.8

**Dependencies:** None

---

### T01.03 -- Run targeted pytest suite and capture results

| Field | Value |
|---|---|
| Effort | S |
| Risk | Low |
| Tier | STANDARD |
| Verification Method | Direct test execution |
| Deliverable IDs | D-0003 |

**Deliverables:**
- Execute `uv run pytest tests/sprint/test_models.py tests/pipeline/test_models.py tests/pipeline/test_full_flow.py -v --tb=short` and write the full output to `.dev/releases/current/smoke-test-sprint/artifacts/pytest-results.txt`. The test suite must pass with zero failures.

**Steps:**
1. Run `uv run pytest tests/sprint/test_models.py tests/pipeline/test_models.py tests/pipeline/test_full_flow.py -v --tb=short`
2. Capture full stdout+stderr to `.dev/releases/current/smoke-test-sprint/artifacts/pytest-results.txt`
3. Verify the final line shows all tests passed with 0 failures

**Acceptance Criteria:**
- All tests pass (exit code 0)
- Output file contains "passed" and does not contain "failed"
- File `.dev/releases/current/smoke-test-sprint/artifacts/pytest-results.txt` exists and is non-empty

**Dependencies:** None
