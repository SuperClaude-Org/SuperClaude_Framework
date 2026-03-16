# Phase 2 -- Isolation Lifecycle

Create per-phase isolation directories and pass them to subprocesses with deterministic cleanup. This phase depends on Phase 1 M1.0 (OQ-006 resolved) — the isolation mechanism must be known before any Phase 2 code is written.

---

### T02.01 -- Implement Startup Orphan Cleanup in execute_sprint()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Stale `.isolation/` directories from crashed previous runs must be cleaned before starting a new sprint to prevent file contamination. |
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
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0006/evidence.md

**Deliverables:**
- D-0006: `shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True)` added to `execute_sprint()` in `src/superclaude/cli/sprint/executor.py` before the phase loop

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` and locate the phase loop in `execute_sprint()`
2. **[PLANNING]** Identify the correct insertion point: after config initialization but before the first phase iteration
3. **[EXECUTION]** Add `shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True)` before the phase loop
4. **[EXECUTION]** Ensure `shutil` is imported (add import if missing)
5. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
6. **[COMPLETION]** Record evidence of orphan cleanup implementation

**Acceptance Criteria:**
- `shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True)` present in `execute_sprint()` before phase loop
- `ignore_errors=True` prevents cleanup failures from masking primary phase errors
- `shutil` import present in `executor.py`
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0006/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Remove the `shutil.rmtree()` call from `execute_sprint()`
**Notes:** FR-006 implementation. Milestone M2.1. Uses `ignore_errors=True` per Risk M1 mitigation.

---

### T02.02 -- Create Per-Phase Isolation Directory with Single-File Copy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013, R-014 |
| Why | Each phase subprocess must operate in an isolated directory containing only its phase file, preventing access to tasklist-index.md and saving ~14K tokens per phase. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (subprocess boundary interaction), data isolation |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0007/evidence.md

**Deliverables:**
- D-0007: Per-phase isolation directory creation at `config.results_dir / ".isolation" / f"phase-{phase.number}"` with `shutil.copy2(phase.file, isolation_dir / phase.file.name)` copying exactly one file

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` and locate the per-phase subprocess launch section
2. **[PLANNING]** Identify insertion point: before subprocess launch, after phase setup
3. **[EXECUTION]** Create isolation directory: `isolation_dir = config.results_dir / ".isolation" / f"phase-{phase.number}"`; `isolation_dir.mkdir(parents=True, exist_ok=True)`
4. **[EXECUTION]** Copy phase file: `shutil.copy2(phase.file, isolation_dir / phase.file.name)`
5. **[VERIFICATION]** Verify isolation directory contains exactly one file after copy
6. **[COMPLETION]** Record evidence of directory creation and single-file copy

**Acceptance Criteria:**
- Isolation directory created **before subprocess launch** at `config.results_dir / ".isolation" / f"phase-{phase.number}"`
- `shutil.copy2()` copies exactly one file (the phase file) into the isolation directory
- Directory structure uses deterministic naming based on phase number
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: Isolation directory contains exactly one file (phase file) at subprocess launch time
- Evidence: TASKLIST_ROOT/artifacts/D-0007/evidence.md produced

**Dependencies:** T02.01
**Rollback:** Remove isolation directory creation and file copy code
**Notes:** FR-001/FR-002 implementation. Milestone M2.2. The "exactly one file" constraint is the core isolation guarantee.

---

### T02.03 -- Pass Isolation Path to Subprocess via Confirmed Mechanism

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | The subprocess must be mechanically constrained to resolve files only within the isolation directory, making tasklist-index.md unreachable. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (subprocess boundary), dependency (M1.0 mechanism) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0008/evidence.md

**Deliverables:**
- D-0008: Isolation path passed to subprocess boundary using M1.0-confirmed mechanism: primary `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` if OQ-006 confirms env var, or subprocess `cwd=isolation_dir` if env var is ineffective

**Steps:**
1. **[PLANNING]** Read OQ-006 resolution (D-0001) to determine confirmed mechanism
2. **[PLANNING]** Locate subprocess launch call in `src/superclaude/cli/sprint/executor.py`
3. **[EXECUTION]** If env var confirmed: pass `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` to `ClaudeProcess` constructor
4. **[EXECUTION]** If cwd confirmed: pass `cwd=isolation_dir` to subprocess launch
5. **[VERIFICATION]** Verify subprocess file resolution is mechanically constrained to isolation directory
6. **[COMPLETION]** Record which mechanism was used and evidence of constraint

**Acceptance Criteria:**
- If OQ-006 confirms env var support, subprocess receives isolation path via `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}`; if env var is ineffective, subprocess receives isolation path via `cwd=isolation_dir`. Implementation follows the mechanism documented in D-0001.
- `tasklist-index.md` is mechanically unreachable from the subprocess (not just instructionally)
- Primary/Fallback mechanism selection matches the OQ-006 resolution in D-0001
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: Subprocess launched with isolation mechanism applied; file resolution constrained to isolation directory
- Evidence: TASKLIST_ROOT/artifacts/D-0008/evidence.md produced

**Dependencies:** T02.02, T01.01
**Rollback:** Remove mechanism application from subprocess launch
**Notes:** FR-003 implementation. Milestone M2.4. This is the primary system objective — silent failure (Risk H2) is the highest-severity risk.

---

### T02.04 -- Implement Per-Phase Isolation Cleanup in finally Block

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Isolation directories must be removed on both success and failure paths to prevent filesystem accumulation and ensure cleanup is guaranteed. |
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
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0009/evidence.md

**Deliverables:**
- D-0009: `shutil.rmtree(isolation_dir, ignore_errors=True)` in per-phase `finally` block in `src/superclaude/cli/sprint/executor.py`

**Steps:**
1. **[PLANNING]** Locate the per-phase try/except/finally block in `execute_sprint()` in `src/superclaude/cli/sprint/executor.py`
2. **[PLANNING]** Confirm finally block exists; if not, wrap phase execution in try/finally
3. **[EXECUTION]** Add `shutil.rmtree(isolation_dir, ignore_errors=True)` to the `finally` block
4. **[EXECUTION]** Ensure cleanup exception never masks primary phase execution result
5. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
6. **[COMPLETION]** Record evidence of finally-block cleanup

**Acceptance Criteria:**
- `shutil.rmtree(isolation_dir, ignore_errors=True)` present in per-phase `finally` block
- Cleanup executes on both success and failure paths
- `ignore_errors=True` prevents cleanup failures from raising over execution results
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0009/evidence.md produced

**Dependencies:** T02.02
**Rollback:** Remove cleanup call from finally block
**Notes:** FR-003 implementation. Milestone M2.3. `ignore_errors=True` is mandatory per Risk M1 mitigation.

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm isolation lifecycle is complete: orphan cleanup, per-phase directory creation with single-file copy, subprocess mechanism applied, and deterministic cleanup on all exit paths.

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P02-END.md

**Verification:**
- Isolation directory created per phase containing exactly one copied phase file (M2.2)
- Isolation directory removed on both success and failure paths (M2.3)
- Subprocess file resolution mechanically constrained to isolated input (M2.4)

**Exit Criteria:**
- Milestones M2.1, M2.2, M2.3, M2.4 all satisfied
- `uv run pytest tests/sprint/ -v --tb=short` exits 0
- No stale `.isolation/` directories remain after phase execution
