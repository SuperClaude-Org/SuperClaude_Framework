# Phase 7 -- UX and Operational Hardening

Make the system usable in real workflows, not just correct in narrow successful paths. This phase adds TUI rendering, review gates, resume semantics, and comprehensive failure-path handling.

### T07.01 -- Implement Rich TUI Live Dashboard

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | The TUI provides real-time visibility into step progress, gate state, timing, and review pause prompts during pipeline execution. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0035/spec.md

**Deliverables:**
1. Rich TUI live dashboard in `src/superclaude/cli/cli_portify/tui.py` rendering: step progress (current step, completed steps), gate state (pass/fail/pending), timing (elapsed per step and total), current convergence iteration, review pause prompts, warnings/advisories

**Steps:**
1. **[PLANNING]** Identify Rich library live rendering patterns compatible with existing CLI
2. **[PLANNING]** Define dashboard layout: step progress, gate state, timing, iteration counter, review prompts
3. **[EXECUTION]** Implement Rich Live display with step progress table and gate status indicators
4. **[EXECUTION]** Implement timing display showing per-step elapsed and total elapsed time
5. **[EXECUTION]** Implement convergence iteration counter and review pause prompt rendering
6. **[VERIFICATION]** Verify TUI renders correctly during mock pipeline execution
7. **[COMPLETION]** Document TUI layout and rendering behavior

**Acceptance Criteria:**
- TUI renders step progress, gate state, timing, current iteration, and warnings in real-time
- Dashboard pauses display when review gate prompts user on stderr
- TUI uses Rich library for live rendering consistent with existing CLI patterns
- Dashboard degrades gracefully in non-terminal environments

**Validation:**
- Manual check: TUI renders legibly during mock pipeline execution with all dashboard elements visible
- Evidence: linkable artifact produced at D-0035/spec.md

**Dependencies:** T04.03, T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### T07.02 -- Implement User Review Gates with --skip-review Bypass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | User review gates ensure human oversight at critical pipeline decision points while --skip-review enables CI/CD compatibility. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0036/spec.md

**Deliverables:**
1. User review gate module in `src/superclaude/cli/cli_portify/review.py`: pause TUI when review required, prompt on stderr, continue on `y`, halt with `USER_REJECTED` on `n`, `--skip-review` flag bypasses all user prompts

**Steps:**
1. **[PLANNING]** Identify review gate insertion points: after design-pipeline (Step 4) and after panel-review (Step 7)
2. **[PLANNING]** Define review gate protocol: stderr prompt, y/n response, USER_REJECTED status
3. **[EXECUTION]** Implement review gate function that pauses TUI and prompts on stderr
4. **[EXECUTION]** Implement --skip-review bypass that auto-continues at all review points
5. **[VERIFICATION]** Test review gate with mocked stdin: y continues, n halts with USER_REJECTED, --skip-review bypasses
6. **[COMPLETION]** Document review gate behavior and CI/CD compatibility

**Acceptance Criteria:**
- Review gate pauses TUI and prompts on stderr at design-pipeline and panel-review steps
- `y` response continues pipeline execution; `n` halts with `USER_REJECTED` status
- `--skip-review` flag bypasses all user review prompts
- USER_REJECTED status is captured in the return contract

**Validation:**
- `uv run pytest tests/cli_portify/test_review.py -v` exits 0 (testing y, n, and --skip-review paths)
- Evidence: linkable artifact produced at D-0036/spec.md

**Dependencies:** T02.02, T05.02, T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### T07.03 -- Implement Resume Semantics with Resumability Matrix

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Resume semantics define which steps can be re-entered after failure, how prior context is preserved, and what commands to generate for resumable failures. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | rollback (resume behavior), data integrity (prior-context injection) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0037, D-0038, D-0052 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0037/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0038/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0052/spec.md

**Deliverables:**
1. Resumability matrix defining which steps support resume entry (Steps 5-7 resumable per roadmap), with explicit resume entry points for each
2. Resume command generation: produce `--start <step>` commands with suggested budget for resumable failures (SC-014)
3. Prior-context injection for Phase 4 resume: preserve `focus-findings.md` when resuming at brainstorm-gaps or panel-review

**Steps:**
1. **[PLANNING]** Identify resumable steps from roadmap: synthesize-spec (Step 5), brainstorm-gaps (Step 6), panel-review (Step 7)
2. **[PLANNING]** Define resume entry point for each step: what prior artifacts must exist, what context is preserved
3. **[EXECUTION]** Implement resumability matrix as a data structure mapping step names to resume requirements
4. **[EXECUTION]** Implement resume command generation: `--start <step>` with suggested budget based on remaining steps
5. **[EXECUTION]** Implement prior-context injection: preserve `focus-findings.md` when resuming at Phase 5 steps
6. **[VERIFICATION]** Trigger failures in Steps 6 and 7, verify resume commands are generated correctly (SC-014)
7. **[COMPLETION]** Document resume behavior, entry points, and context preservation

**Acceptance Criteria:**
- Resumability matrix defines Steps 5-7 as resumable with explicit entry point requirements
- Resume commands generated for resumable failures include `--start <step>` and suggested budget (SC-014)
- Prior-context injection preserves `focus-findings.md` when resuming at brainstorm-gaps or panel-review
- Non-resumable step failures (Steps 1-4) do not generate resume commands

**Validation:**
- `uv run pytest tests/cli_portify/test_resume.py -v` exits 0 (testing resume command generation for Steps 5-7)
- Evidence: linkable artifact produced at D-0037/spec.md, D-0038/spec.md, D-0052/spec.md

**Dependencies:** T02.03, T06.01, T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### T07.04 -- Implement Comprehensive Failure-Path Handling for 7 Failure Types

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | All 7 failure types must have explicit handling paths with clear error messages, remediation guidance, and contract emission. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (all failure paths), rollback (recovery behavior) |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0039/spec.md

**Deliverables:**
1. Failure-path handlers for all 7 types in `src/superclaude/cli/cli_portify/failures.py`: (a) missing template: fail-fast with clear error and remediation path, (b) missing skills: graceful fallback with warning, (c) malformed artifact: diagnostic classification and targeted retry, (d) timeout: per-iteration and total budget handling, (e) partial artifact: re-run policy (prefer re-run over trust), (f) non-writable output: early detection in validate-config, (g) exhausted budget: ESCALATED terminal state with resume guidance

**Steps:**
1. **[PLANNING]** Map all 7 failure types from roadmap to specific handler implementations
2. **[PLANNING]** Identify which failures are resumable vs terminal
3. **[EXECUTION]** Implement missing template handler: fail-fast, clear error, remediation path
4. **[EXECUTION]** Implement missing skills handler: graceful fallback with warning (reuse D-0029 fallback)
5. **[EXECUTION]** Implement malformed artifact, timeout, partial artifact, non-writable output, and budget exhaustion handlers
6. **[VERIFICATION]** Test each failure handler produces correct contract with populated defaults
7. **[COMPLETION]** Document failure types, handling behavior, and recovery paths

**Acceptance Criteria:**
- All 7 failure types have explicit handler implementations with clear error messages
- Missing template triggers fail-fast with remediation path; missing skills activates graceful fallback
- Timeout handling distinguishes per-iteration and total budget exhaustion
- All failure handlers emit populated contracts with no None/empty fields per NFR-009

**Validation:**
- `uv run pytest tests/cli_portify/test_failures.py -v` exits 0 (testing all 7 failure types)
- Evidence: linkable artifact produced at D-0039/spec.md

**Dependencies:** T02.03, T04.03, T06.02
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 7

**Purpose:** Verify operational resilience is complete: resume works, all exit paths emit contracts, user review is reliable, and all 7 failure types are handled.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P07-END.md
**Verification:**
- Resume behavior works for Steps 5-7 with correct resume commands generated
- All exit paths emit complete contracts with populated defaults
- User review interaction is reliable and testable
**Exit Criteria:**
- All 7 failure types have explicit handling paths (M6 criterion)
- `uv run pytest tests/cli_portify/test_resume.py tests/cli_portify/test_failures.py tests/cli_portify/test_review.py -v` exits 0
- --skip-review bypasses all user prompts
