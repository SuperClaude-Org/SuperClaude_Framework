# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 5: Post-Edit Sync & Quality Gates

**Phase Goal**: After all code edits from Phases 1–4 are complete, synchronize the source-of-truth `src/superclaude/` tree into the development `.claude/` copies, verify that both sides are byte-for-byte consistent, pass the project linter on every modified file, and confirm no regressions were introduced into the existing test suite. Completion of this phase is the prerequisite for Phase 6 acceptance testing.

---

### T05.01 — Execute make sync-dev

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-025 (D5.1) |
| **Why** | Four files were modified in `src/superclaude/` during Phases 1–4. The `.claude/` development copies must be updated to reflect those changes before any verification tool reads them. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | None identified; operation is a scripted file copy with no destructive side-effects. |
| **Tier** | STANDARD |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test execution — confirm exit code 0 |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual `cp` of each modified file if `make` is unavailable |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0019 |
| **Artifacts** | Terminal output showing `make sync-dev` success |
| **Deliverables** | Synchronized `.claude/` development copies of all 4 modified files |

#### Steps

1. **[PRE]** Confirm working directory is the repository root (`/config/workspace/SuperClaude_Framework`).
2. **[PRE]** Run `git diff --stat HEAD` to record which files are modified — serves as a cross-check after sync.
3. **[EXEC]** Run `make sync-dev` and capture stdout/stderr.
4. **[VERIFY]** Confirm exit code is 0; if non-zero, inspect error output and resolve before proceeding.
5. **[POST]** Spot-check that `.claude/commands/roadmap.md` modification timestamp is newer than before the command ran.

#### Acceptance Criteria

1. `make sync-dev` exits with code 0.
2. `.claude/commands/roadmap.md` reflects the content of `src/superclaude/commands/roadmap.md`.
3. `.claude/skills/sc-roadmap/SKILL.md` reflects the content of `src/superclaude/skills/sc-roadmap/SKILL.md`.
4. No file listed in the sprint spec as modified is absent from the `.claude/` tree after sync.

#### Validation

1. `diff src/superclaude/commands/roadmap.md .claude/commands/roadmap.md` returns exit code 0.
2. `diff src/superclaude/skills/sc-roadmap/SKILL.md .claude/skills/sc-roadmap/SKILL.md` returns exit code 0.

#### Dependencies

- All edits from Phases 1–4 must be committed or staged before sync.

#### Rollback

Restore `.claude/` copies from the last known-good state using `git checkout .claude/` if the sync produces corrupted output.

#### Notes

This is a non-destructive, idempotent operation. Re-running is safe if any uncertainty exists about whether the sync completed correctly.

---

### T05.02 — Verify Sync with make verify-sync

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-026 (D5.2) |
| **Why** | `make sync-dev` copies files but does not self-report per-file correctness. `make verify-sync` provides the authoritative CI-friendly assertion that `src/superclaude/` and `.claude/` are in sync. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | A failure here indicates a sync regression; root cause must be identified before Phase 6 proceeds. |
| **Tier** | STANDARD |
| **Confidence** | `[████████░░]` 80% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test execution — confirm exit code 0 |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual `diff -r src/superclaude/.claude/` to diagnose discrepancies |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0020 |
| **Artifacts** | Terminal output showing `make verify-sync` success |
| **Deliverables** | Verified parity confirmation between `src/superclaude/` and `.claude/` |

#### Steps

1. **[PRE]** Confirm T05.01 completed with exit code 0.
2. **[EXEC]** Run `make verify-sync` and capture full output.
3. **[VERIFY]** Confirm exit code is 0; if non-zero, read diff output to identify the out-of-sync file(s).
4. **[REMEDIATE]** If discrepancies are found, re-run `make sync-dev` targeting the offending file(s), then repeat this task.
5. **[POST]** Record the successful verify-sync output as evidence artifact.

#### Acceptance Criteria

1. `make verify-sync` exits with code 0.
2. No diff output is produced (or output explicitly states all files match).
3. The command completes within 30 seconds.
4. No warnings about missing files are emitted.

#### Validation

1. `make verify-sync` produces exit code 0 on a clean re-run immediately after initial success.
2. The terminal output contains no lines beginning with `<` or `>` (unified diff markers).

#### Dependencies

- T05.01 must be completed successfully.

#### Rollback

If verify-sync fails and sync cannot be corrected, escalate to a manual per-file diff to identify the root cause before blocking further phases.

#### Notes

`make verify-sync` is described in `CLAUDE.md` as CI-friendly. Its exit code is the authoritative pass/fail signal.

---

### T05.03 — Run Linter on All Modified Files

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-027 (D5.3) |
| **Why** | The sprint modifies Markdown files that may include inline code blocks, YAML frontmatter, and structured content. The linter enforces project-wide style consistency and catches formatting regressions that would degrade readability or tooling compatibility. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | Modified files are Markdown, not Python; lint failures are likely cosmetic and fast to fix. |
| **Tier** | LIGHT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Sanity check — confirm exit code 0 |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — run ruff directly on Python files if `make lint` target is unavailable |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0021 |
| **Artifacts** | Terminal output showing `make lint` success |
| **Deliverables** | Clean lint report for all sprint-modified files |

#### Steps

1. **[PRE]** Confirm T05.02 completed with exit code 0.
2. **[EXEC]** Run `make lint` from the repository root and capture output.
3. **[VERIFY]** Confirm exit code is 0.
4. **[REMEDIATE]** If lint errors are reported, apply the suggested fixes (typically whitespace or formatting), re-stage the affected files, and re-run.
5. **[POST]** Record exit code 0 as evidence.

#### Acceptance Criteria

1. `make lint` exits with code 0.
2. No errors or warnings are emitted for any of the 4 sprint-modified files.
3. Lint completes without timeout.
4. Any pre-existing lint warnings unrelated to this sprint remain unchanged (no regressions introduced).

#### Validation

1. `make lint` exit code is 0.
2. Grep for any of the 4 sprint file paths in lint output returns no matches with severity `error` or `warning`.

#### Dependencies

- T05.01 and T05.02 must be completed (files must be synced before lint runs against both trees).

#### Rollback

Revert the last edit that introduced the lint failure using `git diff` to isolate the offending change.

#### Notes

The project linter is `ruff` per `CLAUDE.md`. For `.md` files, ruff may not lint Markdown directly; if `make lint` only covers Python files, this task passes trivially and should be noted as such in the evidence artifact.

---

### T05.04 — Run Full Test Suite

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-028 (D5.4) |
| **Why** | Phases 1–4 modify command and skill files. While these are Markdown documents, any Python code that reads, parses, or references these files could be broken by structural changes. The full test suite is the definitive regression gate. |
| **Effort** | S |
| **Risk** | Low |
| **Risk Drivers** | Test failures here indicate an unintended structural regression in sprint deliverables; investigation overhead could be moderate. |
| **Tier** | STANDARD |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test execution — `uv run pytest` exit code 0 |
| **MCP Requirements** | None |
| **Fallback Allowed** | No — test suite must pass; failures must be resolved, not skipped |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0022 |
| **Artifacts** | `uv run pytest` output with pass/fail summary |
| **Deliverables** | Confirmed zero regressions in the existing test suite |

#### Steps

1. **[PRE]** Confirm T05.03 completed with exit code 0.
2. **[PRE]** Confirm the Python environment is active: `uv run python --version`.
3. **[EXEC]** Run `uv run pytest` from the repository root; capture stdout/stderr.
4. **[VERIFY]** Confirm exit code is 0 and the summary line shows 0 failures, 0 errors.
5. **[REMEDIATE]** If failures exist, read the traceback, isolate whether the failure was pre-existing or introduced by this sprint, and fix accordingly. Per RULES.md: never skip or comment out failing tests.
6. **[POST]** Record the summary line (e.g., `47 passed in 3.21s`) as evidence.

#### Acceptance Criteria

1. `uv run pytest` exits with code 0.
2. The summary reports 0 failures and 0 errors.
3. No tests are skipped that were previously passing.
4. Test run completes within the project's standard timeout window.

#### Validation

1. `uv run pytest` exit code is 0.
2. Output summary line contains `passed` with no `failed` or `error` counts.

#### Dependencies

- T05.01, T05.02, T05.03 must be completed.
- All sprint file edits must be finalized before this task runs.

#### Rollback

If test failures are introduced by sprint changes, revert the relevant Phase edits using `git diff` to identify the breaking change and correct it before re-running.

#### Notes

Per `CLAUDE.md`: all Python operations must use `uv run`. Do not use `python -m pytest` directly.

---

### Phase 5 End-of-Phase Checkpoint

| Check | Expected Result |
|---|---|
| T05.01 sync-dev | Exit code 0 |
| T05.02 verify-sync | Exit code 0 |
| T05.03 lint | Exit code 0 |
| T05.04 pytest | Exit code 0, 0 failures |
| All D-0019–D-0022 deliverables present | Yes |
| Phase 6 unblocked | Yes |

**Gate**: All four tasks must show exit code 0 before Phase 6 begins.
