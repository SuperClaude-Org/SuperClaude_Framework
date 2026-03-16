# Phase 3 -- Prompt Resilience and Context Header

Provide subprocess orientation without index file access by adding a Sprint Context header to prompts, and extend prompt-too-long detection to scan stderr. This phase can proceed concurrently with Phase 4 after Phase 1 completes — no dependency on Phase 2.

---

### T03.01 -- Add Sprint Context Header to build_prompt()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Isolated subprocesses need orientation context (sprint name, phase number, artifact paths) without access to the index file. The Sprint Context header provides this inline. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0010/evidence.md

**Deliverables:**
- D-0010: `build_prompt()` in `src/superclaude/cli/sprint/prompt.py` emits a `## Sprint Context` section containing: sprint name (`config.release_name or config.release_dir.name`), current phase N of M, artifact root path and results directory, prior-phase artifact directories, and instruction "All task details are in the phase file. Do not seek additional index files."

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/prompt.py` and locate `build_prompt()` function
2. **[PLANNING]** Identify where to insert the Sprint Context section in the prompt output
3. **[EXECUTION]** Add `## Sprint Context` section with sprint name using `config.release_name or config.release_dir.name` (OQ-002 resolved with safe fallback)
4. **[EXECUTION]** Include current phase N of M, artifact root path, results directory, and prior-phase artifact directories
5. **[EXECUTION]** Add instruction: "All task details are in the phase file. Do not seek additional index files."
6. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
7. **[COMPLETION]** Record evidence of Sprint Context header content

**Acceptance Criteria:**
- `build_prompt()` output contains `## Sprint Context` header section
- Sprint name derived from `config.release_name or config.release_dir.name`
- Phase N of M, artifact root, results directory, and prior-phase dirs all present in header
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: Inspect `build_prompt()` output; confirm `## Sprint Context` section present with all required fields
- Evidence: TASKLIST_ROOT/artifacts/D-0010/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Remove Sprint Context section from `build_prompt()`
**Notes:** FR-007/FR-008 implementation. Milestone M3.1. Sprint name uses safe fallback per OQ-002 resolution.

---

### T03.02 -- Extend detect_prompt_too_long() with error_path Parameter

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Prompt-too-long errors can appear in stderr, not just stdout. Extending detection to scan an error file increases recovery reliability. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0011/evidence.md

**Deliverables:**
- D-0011: `detect_prompt_too_long()` in `src/superclaude/cli/sprint/monitor.py` accepts `error_path: Path | None = None` keyword-only parameter; scans `error_path` using the same last-10-lines logic; returns `True` if pattern found in either file

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/monitor.py` and locate `detect_prompt_too_long()` signature and implementation
2. **[PLANNING]** Understand the existing last-10-lines scanning logic
3. **[EXECUTION]** Add `*, error_path: Path | None = None` keyword-only parameter to `detect_prompt_too_long()`
4. **[EXECUTION]** If `error_path` is not None, scan it using the same last-10-lines logic; return `True` if pattern found in either the original output path or the error path
5. **[VERIFICATION]** Verify `error_path=None` maintains backward-compatible behavior (existing calls unchanged)
6. **[COMPLETION]** Record evidence of parameter addition and dual-scan behavior

**Acceptance Criteria:**
- `detect_prompt_too_long()` accepts `error_path: Path | None = None` as keyword-only parameter
- Error path scanned using identical last-10-lines logic as output path
- Returns `True` if pattern found in either file
- `error_path=None` produces identical behavior to current implementation
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0011/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Remove `error_path` parameter from `detect_prompt_too_long()`
**Notes:** FR-009 implementation. Milestone M3.2. Keyword-only with None default per NFR-001.

---

### T03.03 -- Extend _determine_phase_status() with error_file and Wire to execute_sprint()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019, R-020 |
| Why | The phase status determination must forward error file information to prompt-too-long detection so context exhaustion is caught from stderr. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0012/evidence.md

**Deliverables:**
- D-0012: `_determine_phase_status()` in `src/superclaude/cli/sprint/executor.py` accepts `error_file: Path | None = None` keyword-only parameter and forwards it to `detect_prompt_too_long(error_path=error_file)`; `execute_sprint()` call site passes `config.error_file(phase)`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` and locate `_determine_phase_status()` signature
2. **[PLANNING]** Identify the call to `detect_prompt_too_long()` within `_determine_phase_status()`
3. **[EXECUTION]** Add `*, error_file: Path | None = None` keyword-only parameter to `_determine_phase_status()`
4. **[EXECUTION]** Forward to `detect_prompt_too_long(error_path=error_file)`
5. **[EXECUTION]** Update `execute_sprint()` call site to pass `error_file=config.error_file(phase)` to `_determine_phase_status()`
6. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
7. **[COMPLETION]** Record evidence of error_file plumbing

**Acceptance Criteria:**
- `_determine_phase_status()` accepts `error_file: Path | None = None` as keyword-only parameter
- Error file forwarded to `detect_prompt_too_long(error_path=error_file)`
- `execute_sprint()` passes `config.error_file(phase)` at the call site
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0012/evidence.md produced

**Dependencies:** T03.02
**Rollback:** Remove `error_file` parameter from `_determine_phase_status()` and revert call site
**Notes:** FR-010/FR-011/FR-012 implementation. Milestone M3.3. Covered by named test T04.10 in Phase 5.

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm prompt resilience is complete: Sprint Context header present, error_path detection extended, and error_file plumbed through to execute_sprint().

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P03-END.md

**Verification:**
- `build_prompt()` output contains `## Sprint Context` block with all required fields (M3.1)
- `detect_prompt_too_long()` accepts and scans `error_path` alongside output path (M3.2)
- `_determine_phase_status()` passes `error_file` through to detection logic (M3.3)

**Exit Criteria:**
- Milestones M3.1, M3.2, M3.3 all satisfied
- `uv run pytest tests/sprint/ -v --tb=short` exits 0
- All new parameters are keyword-only with None defaults
