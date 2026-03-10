# Phase 4 -- Validation and Acceptance

This phase validates the roadmap outcomes against the stated success metrics and acceptance checks. The work is limited to the explicit commands, grep checks, and diff-based confirmations named in the roadmap.

### T04.01 -- Run full-suite and sprint coverage validation for targeted pipeline fixes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | The roadmap requires zero-regression validation through the full test suite and a sprint executor coverage target of at least 70 percent. These checks confirm the earlier phases did not regress core behavior. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/evidence.md`

**Deliverables:**
- Validation record for full-suite execution
- Coverage validation note for sprint executor coverage >= 70%
- Evidence placeholder for acceptance command results

**Steps:**
1. **[PLANNING]** Load roadmap context for full-suite and sprint coverage validation.
2. **[PLANNING]** Check dependencies and confirm all implementation phases are complete before acceptance testing starts.
3. **[EXECUTION]** Run the full test suite validation defined by the roadmap.
4. **[EXECUTION]** Run the sprint executor coverage validation path named by the roadmap.
5. **[VERIFICATION]** Compare the results against the zero-regression and >=70% coverage requirements.
6. **[COMPLETION]** Document the command outcomes and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- `uv run pytest` exits 0 with all tests passing.
- The task preserves the roadmap requirement that sprint executor coverage is verified against the >= 70% target.
- Re-running the same acceptance commands yields the same pass/fail signals for full-suite and coverage validation.
- Traceability from `R-016` to `D-0011` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/notes.md`.

**Validation:**
- `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor` reports >= 70%
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/evidence.md`

**Dependencies:** T03.02
**Rollback:** TBD (if not specified in roadmap)

### T04.02 -- Verify diff-based removal targets and pipeline import boundary compliance

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016, R-017 |
| Why | The roadmap requires diff-based confirmation of net line removals and a grep-based NFR-007 import-boundary check. These validations ensure the refactor delivered the expected cleanup results without violating pipeline boundaries. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/evidence.md`

**Deliverables:**
- Diff-based validation record for sprint and roadmap line-removal goals
- NFR-007 import-boundary verification note
- Evidence placeholder for diff and grep command outputs

**Steps:**
1. **[PLANNING]** Load roadmap context for diff-stat and import-boundary validation.
2. **[PLANNING]** Check dependencies and confirm full-suite validation is complete before cleanup metrics are recorded.
3. **[EXECUTION]** Run the diff-based checks for sprint/process.py and roadmap/executor.py line-removal targets.
4. **[EXECUTION]** Run the grep-based NFR-007 import-boundary check named by the roadmap.
5. **[VERIFICATION]** Compare the diff and grep outputs against the roadmap acceptance thresholds.
6. **[COMPLETION]** Document the validation results and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/spec.md` records the diff-stat removal targets and the NFR-007 grep validation scope.
- The task preserves the roadmap requirement that sprint/process.py loses at least 58 net lines and roadmap/executor.py loses at least 25 lines.
- Re-running the same diff and grep checks yields the same measurable acceptance thresholds.
- Traceability from `R-016` and `R-017` to `D-0012` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/notes.md`.

**Validation:**
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/evidence.md`

**Dependencies:** T04.01
**Rollback:** TBD (if not specified in roadmap)

### T04.03 -- Confirm Python dependency set remains unchanged after targeted fixes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | The roadmap explicitly requires no new Python package dependencies as part of final acceptance. This validation closes the acceptance checklist by confirming dependency stability. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/evidence.md`

**Deliverables:**
- Dependency validation record for `pyproject.toml`
- Evidence note for no additions to project dependencies
- Evidence placeholder for dependency diff output

**Steps:**
1. **[PLANNING]** Load roadmap context for dependency-stability validation.
2. **[PLANNING]** Check dependencies and confirm the prior acceptance validations are complete.
3. **[EXECUTION]** Run the dependency diff validation for `pyproject.toml` named by the roadmap.
4. **[EXECUTION]** Record the expected no-additions result for `[project.dependencies]` in the task artifacts.
5. **[VERIFICATION]** Compare the dependency diff result against the roadmap's no-new-dependencies requirement.
6. **[COMPLETION]** Document the outcome and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/spec.md` records the `pyproject.toml` dependency-diff validation scope.
- The task preserves the roadmap requirement that `[project.dependencies]` gains no new additions.
- Re-running the same dependency diff uses the same no-additions acceptance rule.
- Traceability from `R-017` to `D-0013` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/notes.md`.

**Validation:**
- Manual check: `git diff pyproject.toml` shows no additions to `[project.dependencies]`.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/evidence.md`

**Dependencies:** T04.02
**Rollback:** TBD (if not specified in roadmap)

### Checkpoint: End of Phase 4
**Purpose:** Confirm all roadmap acceptance conditions are validated and the targeted fix bundle is ready for execution reporting.
**Checkpoint Report Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/CP-P04-END.md`
**Verification:**
- Confirm Phase 4 covers full-suite, coverage, diff-stat, grep, and dependency validations from the roadmap.
- Confirm D-0011 through D-0013 have intended artifact paths and evidence placeholders under the tasklist root.
- Confirm the acceptance tasks close every milestone-level success criterion listed in the roadmap.
**Exit Criteria:**
- T04.01 through T04.03 are complete or explicitly recorded as blocked.
- D-0011 through D-0013 are registered in the index and linked from this phase file.
- The tasklist bundle is ready for execution logging and feedback capture.
