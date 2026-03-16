# Phase 1 -- OQ-006 Gate and Env Plumbing

Resolve the mechanism question that all isolation work depends on (OQ-006: whether `CLAUDE_WORK_DIR` env var or subprocess `cwd` controls `@` resolution scope), then establish the `env_vars` propagation chain through `ClaudeProcess` and `build_env()`. This phase cannot be shortened — OQ-006 must be answered before Phase 2 isolation code is written.

---

### T01.01 -- Resolve OQ-006 Verification Gate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002, R-003, R-004, R-005, R-006 |
| Why | All isolation work depends on knowing whether `CLAUDE_WORK_DIR` env var or subprocess `cwd` controls `@` reference resolution. This gate must be resolved before any Phase 2 code is written. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (end-to-end trace), dependency (Phase 2 blocked by this) |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001, D-0002 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0001/spec.md
- TASKLIST_ROOT/artifacts/D-0002/notes.md

**Deliverables:**
- D-0001: OQ-006 resolution document confirming whether `CLAUDE_WORK_DIR` env var or subprocess `cwd` controls `@` reference resolution, with explicit defaults and fallback named
- D-0002: PhaseStatus.PASS grep audit inventory listing all switch sites and identifying PASS_RECOVERED parity gaps (feeds Phase 4 M4.4)

**Steps:**
1. **[PLANNING]** Identify the trace path: `execute_sprint()` -> `ClaudeProcess` -> subprocess launch boundary in `src/superclaude/cli/sprint/executor.py` and `src/superclaude/cli/sprint/process.py`
2. **[PLANNING]** Identify where `@` reference resolution occurs in the subprocess launch chain
3. **[EXECUTION]** Test `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` as the candidate mechanism for controlling `@` resolution scope
4. **[EXECUTION]** Confirm or falsify the env var mechanism; if ineffective, document subprocess `cwd` as the explicit fallback
5. **[EXECUTION]** Validate current interfaces: `ClaudeProcess.__init__()`, `build_env()`, `execute_sprint()` signatures and call patterns
6. **[EXECUTION]** Perform codebase grep for all `PhaseStatus.PASS` handling sites to identify `PASS_RECOVERED` parity gaps
7. **[VERIFICATION]** Document the confirmed mechanism decision with explicit defaults
8. **[COMPLETION]** If timeline impact is material from cwd fallback, re-estimate Phase 2 before proceeding

**Acceptance Criteria:**
- OQ-006 resolution document exists at TASKLIST_ROOT/artifacts/D-0001/spec.md confirming `CLAUDE_WORK_DIR` or `cwd` as the isolation mechanism
- PhaseStatus.PASS grep audit at TASKLIST_ROOT/artifacts/D-0002/notes.md lists all switch sites with PASS_RECOVERED parity status
- Explicit fallback mechanism named if primary is ineffective
- Timeline re-estimation documented if cwd fallback changes Phase 2 scope

**Validation:**
- Manual check: OQ-006 resolution document reviewed and confirmed actionable for Phase 2
- Evidence: TASKLIST_ROOT/artifacts/D-0001/spec.md and TASKLIST_ROOT/artifacts/D-0002/notes.md produced

**Dependencies:** None
**Rollback:** TBD
**Notes:** This is a phase gate (M1.0). Phase 2 cannot begin until this task completes with a confirmed mechanism decision.

---

### T01.02 -- Add env_vars Parameter to ClaudeProcess.__init__()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007, R-008 |
| Why | The environment propagation chain requires `ClaudeProcess` to accept and store extra env vars so they can be forwarded to subprocess launch. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0003/evidence.md

**Deliverables:**
- D-0003: `env_vars: dict[str, str] | None = None` keyword-only parameter added to `ClaudeProcess.__init__()` in `src/superclaude/cli/sprint/process.py`, stored as `self._extra_env_vars`, wired through to `build_env()` call

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/process.py` and locate `ClaudeProcess.__init__()` signature
2. **[PLANNING]** Confirm no existing `env_vars` parameter; identify where `build_env()` is called
3. **[EXECUTION]** Add `*, env_vars: dict[str, str] | None = None` keyword-only parameter to `ClaudeProcess.__init__()`
4. **[EXECUTION]** Store as `self._extra_env_vars = env_vars`
5. **[EXECUTION]** Wire `self._extra_env_vars` through to the `build_env()` call site
6. **[VERIFICATION]** Verify signature is backward-compatible: keyword-only with `None` default means no existing call sites break
7. **[COMPLETION]** Record evidence of parameter addition and wiring

**Acceptance Criteria:**
- `ClaudeProcess.__init__()` in `src/superclaude/cli/sprint/process.py` accepts `env_vars: dict[str, str] | None = None` as keyword-only parameter
- `self._extra_env_vars` attribute is set in constructor body
- `build_env()` call site receives `self._extra_env_vars`
- All existing callers of `ClaudeProcess()` compile unchanged (keyword-only + None default)

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0 with no regressions
- Evidence: TASKLIST_ROOT/artifacts/D-0003/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Revert parameter addition from `ClaudeProcess.__init__()`
**Notes:** FR-004 implementation. Parameter must be keyword-only (after `*`) per NFR-001.

---

### T01.03 -- Add env_vars Parameter to build_env()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-010 |
| Why | The environment builder must accept and merge extra env vars using override semantics so isolation directories propagate to subprocesses. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0004/evidence.md

**Deliverables:**
- D-0004: `env_vars: dict[str, str] | None = None` keyword-only parameter added to `build_env()` in `src/superclaude/cli/pipeline/process.py`, with `env.update(env_vars)` merge after `os.environ.copy()`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/process.py` and locate `build_env()` signature
2. **[PLANNING]** Confirm current implementation uses `os.environ.copy()` as base
3. **[EXECUTION]** Add `*, env_vars: dict[str, str] | None = None` keyword-only parameter to `build_env()`
4. **[EXECUTION]** Add `if env_vars: env.update(env_vars)` after `os.environ.copy()` (override semantics per OQ-003 resolution)
5. **[VERIFICATION]** Verify existing call sites remain valid; keyword-only with None default causes no breakage
6. **[COMPLETION]** Record evidence of parameter addition and merge semantics

**Acceptance Criteria:**
- `build_env()` in `src/superclaude/cli/pipeline/process.py` accepts `env_vars: dict[str, str] | None = None` as keyword-only parameter
- Merge uses override semantics: `env.update(env_vars)` after `os.environ.copy()`
- `None` input produces identical behavior to current implementation
- All existing callers of `build_env()` compile unchanged

**Validation:**
- Manual check: `uv run pytest tests/ -v --tb=short` exits 0 with no regressions
- Evidence: TASKLIST_ROOT/artifacts/D-0004/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Revert parameter addition from `build_env()`
**Notes:** FR-005 implementation. Override semantics confirmed by OQ-003 resolution in roadmap.

---

### T01.04 -- Verify End-to-End env_vars Propagation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | The env_vars chain must be traceable end-to-end from execute_sprint() through ClaudeProcess to build_env() to subprocess launch to confirm no gaps in propagation. |
| Effort | XS |
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
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0005/evidence.md

**Deliverables:**
- D-0005: End-to-end propagation trace document confirming `env_vars` flows from `execute_sprint()` -> `ClaudeProcess.__init__()` -> `build_env()` -> subprocess environment, with all existing call sites verified unaffected

**Steps:**
1. **[PLANNING]** Map the full propagation chain: `execute_sprint()` -> `ClaudeProcess(env_vars=...)` -> `self._extra_env_vars` -> `build_env(env_vars=...)` -> `env.update()`
2. **[EXECUTION]** Trace each handoff point and verify the value is forwarded without loss
3. **[EXECUTION]** Grep all existing call sites of `ClaudeProcess()` and `build_env()` to confirm they remain valid
4. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
5. **[COMPLETION]** Document propagation trace and call site audit results

**Acceptance Criteria:**
- Propagation trace at TASKLIST_ROOT/artifacts/D-0005/evidence.md documents each handoff point
- All existing call sites of `ClaudeProcess()` and `build_env()` confirmed unaffected
- `uv run pytest tests/sprint/ -v --tb=short` exits 0
- No keyword-only parameter violations in any call site

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0005/evidence.md produced

**Dependencies:** T01.02, T01.03
**Rollback:** TBD
**Notes:** Milestone M1.3. This is the final verification that Phase 1 plumbing is complete.

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm OQ-006 is resolved, env_vars propagation chain is complete and traceable, and all existing call sites remain unaffected.

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P01-END.md

**Verification:**
- OQ-006 resolution document (D-0001) confirms mechanism decision with explicit defaults
- `env_vars` parameter present on both `ClaudeProcess.__init__()` and `build_env()` with keyword-only + None default
- `uv run pytest tests/sprint/ -v --tb=short` exits 0 with no regressions

**Exit Criteria:**
- Milestones M1.0, M1.1, M1.2, M1.3 all satisfied
- PhaseStatus.PASS grep audit (D-0002) complete for Phase 4 consumption
- If OQ-006 revealed cwd fallback, Phase 2 timeline re-estimated before advancing
