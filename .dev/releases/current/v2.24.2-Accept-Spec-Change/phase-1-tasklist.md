# Phase 1 -- Foundation -- spec_patch.py Module

Deliver the standalone `accept-spec-change` logic as a testable, isolated leaf module. `spec_patch.py` passes unit tests for all FR-001 through FR-007 with no imports from `executor.py` or `commands.py`.

---

### T01.01 -- Implement state-file discovery and hash computation in spec_patch.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The accept-spec-change workflow requires reading `.roadmap-state.json`, extracting `spec_file`, recomputing SHA-256, and comparing hashes to detect spec drift. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (state file structure), data (hash computation) |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0001/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0001/evidence.md

**Deliverables:**
- `src/superclaude/cli/roadmap/spec_patch.py` containing `prompt_accept_spec_change(output_dir: Path, auto_accept: bool = False) -> int` with FR-001 (read `.roadmap-state.json`, exact error for missing/unreadable), FR-002 (load `spec_file`, recompute SHA-256 from file bytes), FR-003 (byte-exact hex equality comparison; treat missing/null/empty `spec_hash` as mismatch; idempotent success when already current)

**Steps:**
1. **[PLANNING]** Read existing `executor.py` to understand `_save_state()`/`read_state()` patterns and `.roadmap-state.json` schema
2. **[PLANNING]** Identify `spec_file` and `spec_hash` keys in state, confirm SHA-256 is used for hashing
3. **[EXECUTION]** Create `src/superclaude/cli/roadmap/spec_patch.py` with module docstring and imports (only stdlib: `pathlib`, `hashlib`, `json`, `sys`, `os`)
4. **[EXECUTION]** Implement state-file read with exact error messages for missing/unreadable file (FR-001)
5. **[EXECUTION]** Implement SHA-256 recomputation from `spec_file` bytes (FR-002) and hash comparison with null/empty mismatch handling (FR-003)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "hash or state_file or idempotent or unreadable or missing"` to verify FR-001/002/003
7. **[COMPLETION]** Record evidence of passing tests and module structure

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/spec_patch.py` exists with `prompt_accept_spec_change()` function that reads `.roadmap-state.json` and computes SHA-256
- Missing/null/empty `spec_hash` in state file is treated as mismatch (not crash), and already-current hash returns exit code 0
- `spec_patch.py` imports only stdlib and PyYAML (`import yaml`) — no imports from `executor.py`, `commands.py`, or any other superclaude internal module
- Function signature and return type documented in module docstring

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "hash or state_file or idempotent or unreadable or missing"`
- Evidence: test log artifact at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T01.01-test-output.log

**Dependencies:** None
**Rollback:** Delete `src/superclaude/cli/roadmap/spec_patch.py`
**Notes:** Leaf module design -- no reverse imports permitted. All state I/O through stdlib json/pathlib.

---

### T01.02 -- Implement deviation file scanning with DeviationRecord dataclass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | The acceptance workflow must scan for `dev-*-accepted-deviation.md` files, parse YAML frontmatter, and filter by `disposition: ACCEPTED` and `spec_update_required: true`. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (YAML parsing), schema (DeviationRecord 7-field dataclass) |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0002/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0002/evidence.md

**Deliverables:**
- `DeviationRecord` frozen dataclass (7 fields: id, disposition, spec_update_required, affects_spec_sections, acceptance_rationale, source_file, mtime) with invariants (uppercase disposition, bool spec_update_required, float mtime) in `spec_patch.py`
- Glob-based scanner for `dev-*-accepted-deviation.md` files with YAML frontmatter parsing, `ACCEPTED` disposition filter (case-insensitive), boolean `true` for `spec_update_required` (reject string `"true"`), and warn-and-skip on parse errors

**Steps:**
1. **[PLANNING]** Review spec section 4.5 for DeviationRecord fields and invariants
2. **[PLANNING]** Check existing deviation files in `.dev/releases/` to understand real frontmatter structure
3. **[EXECUTION]** Add `DeviationRecord` frozen dataclass to `spec_patch.py` with 7 fields and type invariants
4. **[EXECUTION]** Implement glob scanner for `dev-*-accepted-deviation.md` with PyYAML frontmatter parsing
5. **[EXECUTION]** Add filtering logic: case-insensitive `ACCEPTED` disposition AND boolean `true` `spec_update_required` (YAML 1.1 coercion accepted: `yes`, `on`, `1`; string `"true"` rejected)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "deviation or yaml or coercion or string_true"` to verify FR-004
7. **[COMPLETION]** Document YAML 1.1 boolean coercion acceptance as intentional contract

**Acceptance Criteria:**
- `DeviationRecord` dataclass in `spec_patch.py` has exactly 7 fields matching spec section 4.5 with frozen=True
- Scanner filters by `disposition: ACCEPTED` (case-insensitive) AND `spec_update_required: true` (boolean, not string)
- Malformed YAML frontmatter triggers warning log and file skip (no crash)
- YAML 1.1 boolean coercion variants (`yes`, `on`, `1`, `True`, `TRUE`) accepted; quoted string `"true"` rejected
- If `disposition` or `spec_update_required` fields are absent from frontmatter, the record is excluded (not an error); processing continues with remaining files

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "deviation or yaml or coercion or string_true"`
- Evidence: test log artifact at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T01.02-test-output.log

**Dependencies:** T01.01
**Rollback:** Revert additions to `spec_patch.py`
**Notes:** PyYAML import added here; dependency resolved in Phase 2 (T02.02). YAML 1.1 boolean coercion is intentional -- documented as explicit contract per Architect Recommendation #5.

---

### T01.03 -- Implement interactive prompt and atomic write in spec_patch.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | The acceptance workflow must display evidence, prompt for confirmation, and atomically update only `spec_hash` in `.roadmap-state.json` while preserving all other keys. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (atomic write), schema (state file mutation) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0003/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0003/evidence.md

**Deliverables:**
- Interactive prompt (FR-005): evidence summary display, single-char `y/Y` confirmation, non-interactive detection via `sys.stdin.isatty()` (exit with `Aborted.` and zero state mutation when non-interactive and `auto_accept=False`)
- Atomic write (FR-006): `.tmp` + `os.replace()` (overwrite pre-existing `.tmp`), modify only `spec_hash`, preserve all other state keys verbatim
- Confirmation output (FR-007): truncated hashes, accepted deviation IDs, resume instruction

**Steps:**
1. **[PLANNING]** Identify state keys that must be preserved (all except `spec_hash`)
2. **[PLANNING]** Confirm `os.replace()` atomicity guarantees on POSIX and Windows best-effort
3. **[EXECUTION]** Implement evidence summary display showing qualifying deviation records and hash diff
4. **[EXECUTION]** Implement `sys.stdin.isatty()` guard: non-interactive + `auto_accept=False` -> `Aborted.` exit with zero mutation
5. **[EXECUTION]** Implement atomic write: write to `.roadmap-state.json.tmp`, then `os.replace()` to final path; overwrite pre-existing `.tmp`
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "prompt or atomic or abort or non_interactive"` to verify FR-005/006/007
7. **[COMPLETION]** Record evidence of atomic write correctness and abort-path read-only behavior

**Acceptance Criteria:**
- Atomic write via `.tmp` + `os.replace()` modifies only `spec_hash` key; `json.loads()` of post-write state preserves all non-`spec_hash` keys verbatim
- Non-interactive terminal (`not sys.stdin.isatty()`) with `auto_accept=False` exits with `Aborted.` message, return code 0, and zero file modification (mtime unchanged) — exit code 1 is reserved for missing file and no-qualifying-deviations conditions
- Confirmation output includes truncated old/new hashes and accepted deviation IDs
- Pre-existing `.tmp` file is overwritten (not appended or errored)

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "prompt or atomic or abort or non_interactive"`
- Evidence: test log artifact at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T01.03-test-output.log

**Dependencies:** T01.01, T01.02
**Rollback:** Revert prompt and write additions to `spec_patch.py`
**Notes:** POSIX atomic guarantee via `os.replace()`. Windows: best-effort (documented). Single-writer assumption documented per Architect Recommendation #4.

---

### T01.04 -- Write unit test suite for spec_patch.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Unit tests must cover idempotency, read-only abort, missing files, YAML resilience, non-interactive behavior, atomic write preservation, and boolean coercion to satisfy AC-1/2/3/4/11/14. |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0004/evidence.md

**Deliverables:**
- `tests/roadmap/test_accept_spec_change.py` with test cases: idempotency (run twice, second exits 0 -- AC-3), read-only on abort (answer N, mtime unchanged -- AC-4), missing file errors (AC-1), YAML parse error resilience (malformed frontmatter -> warning + skip -- AC-14), non-interactive behavior (AC-11), atomic write preserves non-`spec_hash` keys (AC-2), string `"true"` rejection, YAML 1.1 coercion coverage (`yes`, `on`, `1`, `True`, `TRUE`)

**Steps:**
1. **[PLANNING]** Map AC-1/2/3/4/11/14 to specific test functions
2. **[PLANNING]** Design test fixtures: state file, deviation files, spec files with known hashes
3. **[EXECUTION]** Create `tests/roadmap/test_accept_spec_change.py` with `tmp_path` fixtures
4. **[EXECUTION]** Implement 8+ test functions covering all AC items and boolean coercion variants
5. **[EXECUTION]** Add edge cases: missing state file, empty state file, null `spec_hash`, string `"true"` for `spec_update_required`
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v` -- all tests pass, no imports from `executor.py` or `commands.py`
7. **[COMPLETION]** Verify test file has no imports from `executor.py` or `commands.py`

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v` exits 0 with all tests passing
- Test file covers AC-1 (missing file), AC-2 (key preservation), AC-3 (idempotency), AC-4 (abort read-only), AC-11 (non-interactive), AC-14 (malformed YAML)
- String `"true"` for `spec_update_required` is tested and confirmed rejected
- Test file imports only from `spec_patch` module (not `executor` or `commands`)
- Coercion test parametrize set includes `'1'` (YAML 1.1 integer-as-boolean) as a passing case alongside `'yes'`, `'on'`, `'True'`, and `'TRUE'`

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v`
- Evidence: test output log at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T01.04-test-output.log

**Dependencies:** T01.01, T01.02, T01.03
**Rollback:** Delete `tests/roadmap/test_accept_spec_change.py`
**Notes:** Test-first approach recommended per Architect Recommendation #3. Boolean coercion tests make implicit PyYAML behavior an explicit contract.

---

### Checkpoint: End of Phase 1

**Purpose:** Verify `spec_patch.py` is a complete, tested, isolated leaf module implementing FR-001 through FR-007.
**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/CP-P01-END.md

**Verification:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v` exits 0 with all tests passing
- `grep -r "from.*executor\|from.*commands" src/superclaude/cli/roadmap/spec_patch.py` returns no matches (import isolation)
- `spec_patch.py` contains `prompt_accept_spec_change()` with correct signature `(output_dir: Path, auto_accept: bool = False) -> int`

**Exit Criteria:**
- All FR-001 through FR-007 implemented and tested
- `spec_patch.py` has zero imports from `executor.py` or `commands.py`
- Atomic write, abort read-only, and idempotency behaviors all verified by automated tests
