# Phase 3 -- P1+P2 Integration Validation

Validate that Phase 1 (gate fix) and Phase 2 (output sanitizer + prompt hardening) work together correctly with no regressions to other pipeline commands. This is a read-only validation phase — no code modifications.

---

### T03.01 -- Run existing pipeline test suite to verify zero regressions from gate fix and sanitizer changes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012, R-013 |
| Why | `_check_frontmatter()` is shared across all pipeline commands. Gate fix and sanitizer changes must not break any existing functionality. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[█████████░] 90%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0012/evidence.md`

**Deliverables:**
1. `D-0012`: Full test suite pass/fail results demonstrating zero regressions

**Steps:**
1. **[PLANNING]** Identify the full test suite command for pipeline tests
2. **[EXECUTION]** Run `uv run pytest tests/ -v` and capture output
3. **[EXECUTION]** Specifically verify any pipeline-related tests pass (gate tests, executor tests)
4. **[VERIFICATION]** Confirm zero test failures
5. **[COMPLETION]** Record test results in `TASKLIST_ROOT/artifacts/D-0012/evidence.md`

**Acceptance Criteria:**
- `uv run pytest tests/ -v` exits 0 with no failures
- Pipeline-specific tests (gates, executor) explicitly pass
- No new warnings related to gate or sanitizer changes
- Results captured in `TASKLIST_ROOT/artifacts/D-0012/evidence.md`

**Validation:**
- Manual check: `uv run pytest tests/ -v` output shows 0 failures
- Evidence: `TASKLIST_ROOT/artifacts/D-0012/evidence.md` produced

**Dependencies:** T01.01, T01.02, T02.01, T02.02, T02.03 (all Phase 1 and Phase 2 code changes)
**Rollback:** N/A (read-only validation)
**Notes:** None.

---

### T03.02 -- Manual test: run `superclaude roadmap run` extract step with a spec known to produce preamble

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Unit tests validate components in isolation. This manual test validates the real subprocess-to-gate pipeline with actual LLM output that may contain preamble. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████▒░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0013/evidence.md`

**Deliverables:**
1. `D-0013`: Manual test evidence showing extract step completes successfully and output file starts with `---` after sanitization

**Steps:**
1. **[PLANNING]** Identify or create a test spec file that reliably triggers LLM preamble in extract output
2. **[EXECUTION]** Run `superclaude roadmap run <test-spec> --steps extract` and observe output
3. **[EXECUTION]** Verify extraction output file starts with `---` (sanitizer cleaned any preamble)
4. **[VERIFICATION]** Confirm extract step exits successfully (no gate failure)
5. **[COMPLETION]** Record test evidence in `TASKLIST_ROOT/artifacts/D-0013/evidence.md`

**Acceptance Criteria:**
- Extract step completes without frontmatter gate failure
- Output `.md` file starts with `---` (verified via `head -1`)
- Sanitizer log shows bytes stripped (if preamble was present) or 0 (if clean)
- Evidence captured in `TASKLIST_ROOT/artifacts/D-0013/evidence.md`

**Validation:**
- Manual check: extract step exit code is 0 and output starts with `---`
- Evidence: `TASKLIST_ROOT/artifacts/D-0013/evidence.md` produced

**Dependencies:** T02.02 (sanitizer must be wired into `roadmap_run_step()`)
**Rollback:** N/A (read-only validation)
**Notes:** None.

---

### T03.03 -- Verify sanitizer + gate interaction: inject preamble into test fixture, confirm cleaned and validated

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | The sanitizer and gate must work as a coordinated defense: sanitizer cleans preamble, gate validates cleaned output. This test verifies the interaction. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████▒░] 88%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Deliverables:**
1. `D-0014`: Integration test evidence showing preamble injected → sanitizer strips → gate validates → pipeline continues

**Steps:**
1. **[PLANNING]** Create a test fixture file with known preamble before valid YAML frontmatter
2. **[EXECUTION]** Call `_sanitize_output()` on the fixture file; verify preamble stripped
3. **[EXECUTION]** Call `_check_frontmatter()` on the sanitized file; verify `(True, None)` returned
4. **[VERIFICATION]** Confirm the full chain: preamble → sanitize → gate pass
5. **[COMPLETION]** Record integration evidence in `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Acceptance Criteria:**
- Test fixture with preamble is sanitized (file starts with `---` after sanitization)
- Sanitized file passes `_check_frontmatter()` with `(True, None)`
- Chain verified: inject preamble → sanitize → gate validates → no error
- Evidence captured in `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Validation:**
- Manual check: fixture file before/after sanitization shows preamble removed
- Evidence: `TASKLIST_ROOT/artifacts/D-0014/evidence.md` produced

**Dependencies:** T01.01 (gate fix), T02.01 (sanitizer)
**Rollback:** N/A (read-only validation)
**Notes:** None.

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm P1 and P2 defense layers are integrated and validated before proceeding to P4 protocol parity changes.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`

**Verification:**
- Full test suite passes with zero regressions (T03.01)
- Manual extract step test succeeds with real LLM output (T03.02)
- Sanitizer + gate interaction verified with injected preamble (T03.03)

**Exit Criteria:**
- All T03.xx tasks completed
- No Critical or Major issues found during integration validation
- Evidence artifacts produced for D-0012 through D-0014
