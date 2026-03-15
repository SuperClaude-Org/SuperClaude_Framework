# Phase 5 -- Conditional --file Fallback

**Activates only if Phase 1 result is BROKEN.** This phase replaces broken `--file`-based fallback paths with inline embedding across all affected non-inheriting executors. If Phase 1 result is WORKING, this entire phase is skipped and its tasks are marked N/A.

### T05.01 -- Fix `executor.py` fallback path (replace `--file` with inline)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | If `--file` is broken, the fallback path in `executor.py` that uses `--file` must be replaced with inline `-p` embedding to avoid silent data loss. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (fallback mechanism replacement), multi-file scope |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0020/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/roadmap/executor.py` with `--file` fallback replaced by inline `-p` embedding

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/executor.py` and locate `--file` fallback path
2. **[PLANNING]** Design inline `-p` embedding replacement that preserves content delivery semantics
3. **[EXECUTION]** Replace `--file` usage with inline `-p` embedding in fallback path
4. **[EXECUTION]** Verify prompt construction includes the file content inline
5. **[VERIFICATION]** Sub-agent confirms `--file` no longer used in fallback, inline embedding correct
6. **[COMPLETION]** Record diff and verification in D-0020/evidence.md

**Acceptance Criteria:**
- `--file` no longer appears in the fallback path of `executor.py`
- Inline `-p` embedding delivers equivalent content to the subprocess
- Fallback behavior functionally equivalent to pre-fix inline embedding
- Diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0020/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/ -v` exits 0
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0020/evidence.md

**Dependencies:** T01.05 (Phase 1 result must be BROKEN), T03.03
**Rollback:** `git checkout src/superclaude/cli/roadmap/executor.py`
**Notes:** Conditional on Phase 1 = BROKEN. Becomes release-blocking if activated.

---

### T05.02 -- Fix `remediate_executor.py:177` inline embedding

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | `remediate_executor.py` line 177 uses unconditional `--file` which is broken; must replace with inline embedding. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (fallback replacement) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0021/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/roadmap/remediate_executor.py` with unconditional `--file` at line 177 replaced by inline embedding

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/remediate_executor.py` and locate `--file` usage at/near line 177
2. **[PLANNING]** Understand the data flow to determine correct inline embedding approach
3. **[EXECUTION]** Replace `--file` with inline `-p` embedding
4. **[EXECUTION]** Verify content delivery semantics preserved
5. **[VERIFICATION]** Sub-agent confirms `--file` removed, inline embedding correct
6. **[COMPLETION]** Record diff and verification in D-0021/evidence.md

**Acceptance Criteria:**
- `--file` no longer used at `remediate_executor.py:177` (or surrounding context)
- Inline embedding delivers equivalent content to subprocess
- No other `--file` usages remain in `remediate_executor.py`
- Diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0021/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/ -v` exits 0
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0021/evidence.md

**Dependencies:** T05.01
**Rollback:** `git checkout src/superclaude/cli/roadmap/remediate_executor.py`
**Notes:** Conditional on Phase 1 = BROKEN.

---

### T05.03 -- Fix `validate_executor.py:109` inline embedding

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | `validate_executor.py` line 109 uses `--file` which is broken; must replace with inline embedding. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (fallback replacement) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0022/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/roadmap/validate_executor.py` with `--file` at line 109 replaced by inline embedding

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/validate_executor.py` and locate `--file` usage at/near line 109
2. **[PLANNING]** Understand the data flow to determine correct inline embedding approach
3. **[EXECUTION]** Replace `--file` with inline `-p` embedding
4. **[EXECUTION]** Verify content delivery semantics preserved
5. **[VERIFICATION]** Sub-agent confirms `--file` removed, inline embedding correct
6. **[COMPLETION]** Record diff and verification in D-0022/evidence.md

**Acceptance Criteria:**
- `--file` no longer used at `validate_executor.py:109` (or surrounding context)
- Inline embedding delivers equivalent content to subprocess
- No other `--file` usages remain in `validate_executor.py`
- Diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0022/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/ -v` exits 0
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0022/evidence.md

**Dependencies:** T05.01
**Rollback:** `git checkout src/superclaude/cli/roadmap/validate_executor.py`
**Notes:** Conditional on Phase 1 = BROKEN.

---

### T05.04 -- Fix `tasklist/executor.py:121` inline embedding

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | `tasklist/executor.py` line 121 uses `--file` which is broken; must replace with inline embedding. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (fallback replacement) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0023/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/tasklist/executor.py` with `--file` at line 121 replaced by inline embedding

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/tasklist/executor.py` and locate `--file` usage at/near line 121
2. **[PLANNING]** Understand the data flow to determine correct inline embedding approach
3. **[EXECUTION]** Replace `--file` with inline `-p` embedding
4. **[EXECUTION]** Verify content delivery semantics preserved
5. **[VERIFICATION]** Sub-agent confirms `--file` removed, inline embedding correct
6. **[COMPLETION]** Record diff and verification in D-0023/evidence.md

**Acceptance Criteria:**
- `--file` no longer used at `tasklist/executor.py:121` (or surrounding context)
- Inline embedding delivers equivalent content to subprocess
- No other `--file` usages remain in `tasklist/executor.py`
- Diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0023/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/ tests/pipeline/ -v` exits 0
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0023/evidence.md

**Dependencies:** T05.01
**Rollback:** `git checkout src/superclaude/cli/tasklist/executor.py`
**Notes:** Conditional on Phase 1 = BROKEN.

---

### T05.05 -- Assess OQ-4 `--tools default` for non-inheriting executors

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Non-inheriting executors (remediate, validate, tasklist) may also need `--tools default` if they construct subprocess commands independently of `ClaudeProcess`. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (multiple executors) |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0024/notes.md

**Deliverables:**
- OQ-4 assessment document: whether non-inheriting executors need `--tools default`; apply if yes

**Steps:**
1. **[PLANNING]** List all non-inheriting executors: `remediate_executor.py`, `validate_executor.py`, `tasklist/executor.py`
2. **[PLANNING]** Determine how each constructs subprocess commands (inherit `ClaudeProcess` or independent)
3. **[EXECUTION]** Read command construction in each executor
4. **[EXECUTION]** Determine if `--tools default` is absent and needed; apply if yes
5. **[VERIFICATION]** Document assessment with evidence from source code
6. **[COMPLETION]** Record assessment in D-0024/notes.md

**Acceptance Criteria:**
- All three non-inheriting executors assessed for `--tools default` need
- Assessment documents whether each inherits from `ClaudeProcess` or constructs commands independently
- If `--tools default` is needed, it is applied within Phase 5 scope
- Assessment recorded in .dev/releases/current/v2.24.5/artifacts/D-0024/notes.md

**Validation:**
- Manual check: assessment covers all three executors with source code evidence
- Evidence: assessment in .dev/releases/current/v2.24.5/artifacts/D-0024/notes.md

**Dependencies:** T05.01, T05.02, T05.03, T05.04
**Rollback:** N/A (assessment; apply changes have their own rollback)
**Notes:** OQ-4 from roadmap. Conditional on Phase 1 = BROKEN.

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.05

**Purpose:** Verify all --file fallback replacements are correct before adding conditional tests.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P05-T01-T05.md

**Verification:**
- `--file` removed from fallback paths in all four affected executors
- Inline `-p` embedding delivers equivalent content in each case
- OQ-4 assessment complete with documented findings

**Exit Criteria:**
- All four executor fallback paths use inline embedding
- No remaining `--file` usage in fallback code paths
- OQ-4 assessment documented

---

### T05.06 -- Add conditional fallback tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | Need tests verifying the inline embedding fallback works correctly for each affected executor when `--file` is broken. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0025/evidence.md

**Deliverables:**
- Two test functions: `test_remediate_inline_embed_replaces_file_flag` and `test_inline_embed_fallback_when_file_broken` (parameterized over `remediate_executor`, `validate_executor`, `tasklist/executor` using their respective `_EMBED_SIZE_LIMIT` values per spec Section 8.1)

**Steps:**
1. **[PLANNING]** Design `test_remediate_inline_embed_replaces_file_flag` test
2. **[PLANNING]** Design parameterized `test_inline_embed_fallback_when_file_broken` covering three executors
3. **[EXECUTION]** Implement `test_remediate_inline_embed_replaces_file_flag`
4. **[EXECUTION]** Implement parameterized `test_inline_embed_fallback_when_file_broken` with `@pytest.mark.parametrize` over three executors
5. **[VERIFICATION]** `uv run pytest tests/roadmap/ -k "inline_embed" -v` exits 0
6. **[COMPLETION]** Record test code and output in D-0025/evidence.md

**Acceptance Criteria:**
- `test_remediate_inline_embed_replaces_file_flag` exists and passes
- `test_inline_embed_fallback_when_file_broken` is parameterized over three executors per spec Section 8.1
- Each parameterized case uses the executor's respective `_EMBED_SIZE_LIMIT` value
- Tests pass with `uv run pytest tests/roadmap/ -k "inline_embed" -v`

**Validation:**
- `uv run pytest tests/roadmap/ -k "inline_embed" -v` exits 0
- Evidence: test code in .dev/releases/current/v2.24.5/artifacts/D-0025/evidence.md

**Dependencies:** T05.01, T05.02, T05.03, T05.04
**Rollback:** `git checkout tests/roadmap/`
**Notes:** Conditional on Phase 1 = BROKEN. Tests exist only when Phase 5 is activated.

---

### T05.07 -- Run affected test suites for Phase 5 validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | All roadmap and pipeline tests must pass after Phase 5 modifications to confirm no regressions. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0026/evidence.md

**Deliverables:**
- `uv run pytest tests/roadmap/ tests/pipeline/ -v` output showing 0 failures

**Steps:**
1. **[PLANNING]** Confirm all Phase 5 code and test changes are saved
2. **[PLANNING]** Verify no uncommitted changes outside Phase 5 scope
3. **[EXECUTION]** Run `uv run pytest tests/roadmap/ tests/pipeline/ -v`
4. **[EXECUTION]** Capture full test output including pass/fail counts
5. **[VERIFICATION]** Confirm 0 failures in output
6. **[COMPLETION]** Record full test output in D-0026/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ tests/pipeline/ -v` exits with code 0
- Output shows 0 failures across roadmap and pipeline test suites
- No test skips that mask failures
- Full test output recorded in .dev/releases/current/v2.24.5/artifacts/D-0026/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/ tests/pipeline/ -v` exits 0
- Evidence: complete test output in .dev/releases/current/v2.24.5/artifacts/D-0026/evidence.md

**Dependencies:** T05.05, T05.06
**Rollback:** N/A (test execution only)
**Notes:** SC-011 conditional success criteria. Conditional on Phase 1 = BROKEN.

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm all conditional --file fallback remediations are complete and tested before integration.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P05-END.md

**Verification:**
- All four executors use inline embedding instead of `--file` in fallback paths
- Conditional tests pass for all three parameterized executors
- `uv run pytest tests/roadmap/ tests/pipeline/ -v` shows 0 failures

**Exit Criteria:**
- SC-011 conditional success criteria met (if Phase 1 = BROKEN)
- No remaining `--file` usage in fallback code paths
- OQ-4 assessment complete and documented
