# Phase 2 -- CLI Command Registration

Wire `accept-spec-change` into the Click CLI, resolve dependency management, add integration tests, and document resolved open questions. Milestone: `superclaude roadmap accept-spec-change <output_dir>` works end-to-end from terminal.

---

### T02.01 -- Register accept-spec-change Click command in commands.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | The `accept-spec-change` function must be accessible as a CLI command via `superclaude roadmap accept-spec-change <output_dir>`. |
| Effort | S |
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
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0005/spec.md

**Deliverables:**
- Click command `accept-spec-change` in `src/superclaude/cli/roadmap/commands.py` with `click.Path(exists=True)` for `output_dir`, zero optional flags, importing only from `spec_patch.py`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/commands.py` to understand existing command registration patterns
2. **[PLANNING]** Confirm dependency direction: `commands.py` -> `spec_patch.py` (never reverse)
3. **[EXECUTION]** Add `accept-spec-change` Click command with `output_dir` argument using `click.Path(exists=True)`
4. **[EXECUTION]** Wire command body to call `prompt_accept_spec_change(Path(output_dir))` and `sys.exit()` with return code
5. **[VERIFICATION]** Run `superclaude roadmap accept-spec-change --help` to verify command is registered and shows correct usage
6. **[COMPLETION]** Verify import in `commands.py` is `from .spec_patch import prompt_accept_spec_change`

**Acceptance Criteria:**
- `superclaude roadmap accept-spec-change --help` displays usage with `output_dir` argument
- Command imports only `prompt_accept_spec_change` from `spec_patch.py` (dependency direction: `commands.py` -> `spec_patch.py`)
- Zero optional flags on the command (per spec)
- Command exits with return code from `prompt_accept_spec_change()`

**Validation:**
- `superclaude roadmap accept-spec-change --help`
- Evidence: CLI help output captured at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T02.01-cli-help.txt

**Dependencies:** T01.01, T01.02, T01.03
**Rollback:** Remove `accept-spec-change` command from `commands.py`

---

### T02.02 -- Add pyyaml>=6.0 dependency to pyproject.toml

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | `spec_patch.py` uses PyYAML for YAML frontmatter parsing; dependency must be declared explicitly. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0006/evidence.md

**Deliverables:**
- `pyyaml>=6.0` in `pyproject.toml` `[project.dependencies]` (added if not already present; if transitive, add explicit declaration)

**Steps:**
1. **[PLANNING]** Run `uv pip list | grep -i yaml` to check if PyYAML is already transitively available
2. **[PLANNING]** Read `pyproject.toml` dependencies section to check for existing PyYAML entry
3. **[EXECUTION]** Add `"pyyaml>=6.0"` to `[project.dependencies]` in `pyproject.toml` if not already present
4. **[EXECUTION]** Run `uv pip install -e .` to verify dependency resolution succeeds
5. **[VERIFICATION]** Run `uv pip list | grep -i yaml` to confirm PyYAML >=6.0 is installed
6. **[COMPLETION]** Record PyYAML version in evidence

**Acceptance Criteria:**
- `pyproject.toml` contains `"pyyaml>=6.0"` in dependencies list
- `uv pip list | grep -i yaml` shows PyYAML >= 6.0 installed
- No version conflicts with existing dependencies
- `uv run python -c "import yaml; print(yaml.__version__)"` succeeds

**Validation:**
- `uv pip list | grep -i yaml`
- Evidence: dependency verification output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T02.02-dep-check.txt

**Dependencies:** T01.02 (PyYAML import in spec_patch.py)
**Rollback:** Remove `"pyyaml>=6.0"` from `pyproject.toml`

---

### T02.03 -- Write integration test for accept-spec-change CLI command

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | CLI invocation with real file fixtures must be validated end-to-end, including exit codes for all error paths. |
| Effort | S |
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
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0007/evidence.md

**Deliverables:**
- Integration test cases in `tests/roadmap/test_accept_spec_change.py` (or separate integration file) testing CLI invocation via `click.testing.CliRunner`, real file fixtures, and exit codes for success, no-deviation-files, and error paths

**Steps:**
1. **[PLANNING]** Design integration test fixtures: state file, spec file, deviation files in `tmp_path`
2. **[PLANNING]** Identify all exit code paths: success (0), no qualifying deviations (1), missing state file (1)
3. **[EXECUTION]** Implement integration tests using `click.testing.CliRunner` to invoke `accept-spec-change`
4. **[EXECUTION]** Test happy path: valid state + spec + deviation files -> exit 0, hash updated
5. **[EXECUTION]** Test error paths: missing directory, no deviation files, already-current hash
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "cli or integration"` -- all pass
7. **[COMPLETION]** Record integration test results

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "cli or integration"` exits 0 with all integration tests passing
- Tests use `click.testing.CliRunner` for CLI invocation (not subprocess)
- Exit codes verified for: success path, no-deviation-files path, missing-state-file path
- Tests use real file fixtures (not mocks) in `tmp_path`

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "cli or integration"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T02.03-integration-test.log

**Dependencies:** T02.01, T02.02
**Rollback:** Remove integration test functions

---

### T02.04 -- Resolve and document open questions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Four open questions must be resolved and documented before Phase 3 begins: severity field source, `started_at` fallback, post-acceptance file lifecycle, and multiple deviation batches. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0008/notes.md

**Deliverables:**
- Decision artifact documenting resolved answers for: (1) severity field source -- inspect existing deviation frontmatter, remove from prompt if not present, (2) `started_at` fallback -> fail-closed (absent = condition not met), (3) post-acceptance file lifecycle -> leave deviation files in place as immutable audit trail, (4) multiple deviation batches -> show all qualifying records in single prompt

**Steps:**
1. **[PLANNING]** Read roadmap section 2.4 for the four open questions and their proposed resolutions
2. **[PLANNING]** Verify proposed resolutions are consistent with Phase 3 requirements
3. **[EXECUTION]** Run `grep -r "severity" .dev/releases/` to check if severity field exists in deviation files
4. **[EXECUTION]** Document all four decisions with rationale in decision artifact
5. **[VERIFICATION]** Manual check: all four questions have documented answers with clear rationale
6. **[COMPLETION]** Record decisions for Phase 3 consumption

**Acceptance Criteria:**
- Manual check: decision artifact at .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0008/notes.md exists with all 4 questions answered
- `started_at` fallback documented as fail-closed (retry condition not met when absent)
- Deviation file lifecycle documented as immutable audit trail (files remain after hash update)
- All four decisions consistent with Phase 3 implementation requirements

**Validation:**
- Manual check: all four open questions documented with decisions and rationale
- Evidence: decision artifact at .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0008/notes.md

**Dependencies:** T01.04 (Phase 1 complete)
**Rollback:** N/A (documentation only)

---

### Checkpoint: End of Phase 2

**Purpose:** Verify CLI command is registered, dependency resolved, integration tests pass, and all open questions documented before Phase 3 executor integration.
**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/CP-P02-END.md

**Verification:**
- `superclaude roadmap accept-spec-change --help` displays correct usage
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v` exits 0 (unit + integration tests)
- Decision artifact for open questions exists with all 4 questions answered

**Exit Criteria:**
- CLI command `accept-spec-change` is registered and functional end-to-end
- PyYAML >=6.0 declared in `pyproject.toml` and installed
- All four open questions from roadmap section 2.4 resolved and documented
