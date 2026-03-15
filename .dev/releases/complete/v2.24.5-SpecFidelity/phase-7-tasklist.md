# Phase 7 -- Commit and Release

Final commit, version resolution, and release tagging. All validation must be complete (Phase 6 green) before this phase begins.

### T07.01 -- Final `git diff` review

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Must confirm only expected files were changed before committing, preventing accidental inclusions. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0030/evidence.md

**Deliverables:**
- `git diff` review confirming only expected files changed

**Steps:**
1. **[PLANNING]** List expected changed files from Phases 2-5 (per roadmap Files Modified table)
2. **[PLANNING]** Prepare expected file list for comparison
3. **[EXECUTION]** Run `git diff --name-only` to list all changed files
4. **[EXECUTION]** Compare against expected file list
5. **[VERIFICATION]** Confirm no unexpected files appear in diff
6. **[COMPLETION]** Record diff output in D-0030/evidence.md

**Acceptance Criteria:**
- `git diff --name-only` output matches expected files from roadmap Files Modified table
- No unexpected files appear in the diff
- Expected files: `process.py`, `executor.py`, `test_process.py`, `test_file_passing.py` (plus conditional files if Phase 5 activated)
- Diff review recorded in .dev/releases/current/v2.24.5/artifacts/D-0030/evidence.md

**Validation:**
- Manual check: `git diff --name-only` matches expected file list
- Evidence: diff output in .dev/releases/current/v2.24.5/artifacts/D-0030/evidence.md

**Dependencies:** T06.03 (Phase 6 must be complete)
**Rollback:** N/A (read-only review)
**Notes:** None.

---

### T07.02 -- Commit FIX-001

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | FIX-001 changes (process.py + pipeline tests) must be committed with descriptive conventional commit message. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0031/evidence.md

**Deliverables:**
- Git commit with message: `feat(pipeline): add --tools default to ClaudeProcess.build_command()`

**Steps:**
1. **[PLANNING]** Identify FIX-001 files: `src/superclaude/cli/pipeline/process.py`, `tests/pipeline/test_process.py`
2. **[PLANNING]** Prepare commit message per roadmap specification
3. **[EXECUTION]** Stage FIX-001 files: `git add src/superclaude/cli/pipeline/process.py tests/pipeline/test_process.py`
4. **[EXECUTION]** Commit: `git commit -m "feat(pipeline): add --tools default to ClaudeProcess.build_command()"`
5. **[VERIFICATION]** `git log -1` shows correct commit message
6. **[COMPLETION]** Record commit hash in D-0031/evidence.md

**Acceptance Criteria:**
- Commit contains only FIX-001 files (`process.py` and `test_process.py`)
- Commit message matches: `feat(pipeline): add --tools default to ClaudeProcess.build_command()`
- `git log -1` confirms commit was created successfully
- Commit hash recorded in .dev/releases/current/v2.24.5/artifacts/D-0031/evidence.md

**Validation:**
- Manual check: `git log -1 --name-only` shows expected files and message
- Evidence: commit details in .dev/releases/current/v2.24.5/artifacts/D-0031/evidence.md

**Dependencies:** T07.01
**Rollback:** `git reset HEAD~1`
**Notes:** None.

---

### T07.03 -- Commit FIX-ARG-TOO-LONG

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | FIX-ARG-TOO-LONG changes (executor.py + test_file_passing.py) must be committed with descriptive conventional commit message. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0032/evidence.md

**Deliverables:**
- Git commit with message: `fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string`

**Steps:**
1. **[PLANNING]** Identify FIX-ARG-TOO-LONG files: `src/superclaude/cli/roadmap/executor.py`, `tests/roadmap/test_file_passing.py`
2. **[PLANNING]** Prepare commit message per roadmap specification
3. **[EXECUTION]** Stage files: `git add src/superclaude/cli/roadmap/executor.py tests/roadmap/test_file_passing.py`
4. **[EXECUTION]** Commit: `git commit -m "fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string"`
5. **[VERIFICATION]** `git log -1` shows correct commit message
6. **[COMPLETION]** Record commit hash in D-0032/evidence.md

**Acceptance Criteria:**
- Commit contains only FIX-ARG-TOO-LONG files (`executor.py` and `test_file_passing.py`)
- Commit message matches: `fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string`
- `git log -1` confirms commit was created successfully
- Commit hash recorded in .dev/releases/current/v2.24.5/artifacts/D-0032/evidence.md

**Validation:**
- Manual check: `git log -1 --name-only` shows expected files and message
- Evidence: commit details in .dev/releases/current/v2.24.5/artifacts/D-0032/evidence.md

**Dependencies:** T07.02
**Rollback:** `git reset HEAD~1`
**Notes:** None.

---

### T07.04 -- Commit Phase 5 (if activated)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Why | If Phase 5 was activated (Phase 1 = BROKEN), the --file fallback remediation changes must be committed separately. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0033/evidence.md

**Deliverables:**
- Git commit with message: `fix(executors): replace --file fallback with inline embedding` (only if Phase 5 was activated)

**Steps:**
1. **[PLANNING]** Check Phase 1 gate decision (WORKING or BROKEN)
2. **[PLANNING]** If WORKING: skip this task (no Phase 5 changes to commit)
3. **[EXECUTION]** If BROKEN: stage Phase 5 files (`remediate_executor.py`, `validate_executor.py`, `tasklist/executor.py`, conditional tests)
4. **[EXECUTION]** Commit: `git commit -m "fix(executors): replace --file fallback with inline embedding"`
5. **[VERIFICATION]** `git log -1` shows correct commit message (if committed)
6. **[COMPLETION]** Record commit hash or "Skipped (Phase 1 = WORKING)" in D-0033/evidence.md

**Acceptance Criteria:**
- If Phase 1 = BROKEN: commit contains Phase 5 files with specified message
- If Phase 1 = WORKING: task explicitly skipped with documented reason
- Commit message matches: `fix(executors): replace --file fallback with inline embedding`
- Result recorded in .dev/releases/current/v2.24.5/artifacts/D-0033/evidence.md

**Validation:**
- Manual check: `git log -1 --name-only` shows expected files (if committed) or skip documented
- Evidence: commit details or skip reason in .dev/releases/current/v2.24.5/artifacts/D-0033/evidence.md

**Dependencies:** T07.03
**Rollback:** `git reset HEAD~1` (if committed)
**Notes:** Conditional on Phase 1 = BROKEN.

---

### T07.05 -- Resolve version number

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | Roadmap uses v2.24.5 as working title but spec references v2.25.1; must confirm correct version against project version history before tagging. |
| Effort | XS |
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
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0034/notes.md

**Deliverables:**
- Version number confirmed (v2.24.5 or v2.25.1) with rationale based on project version history

**Steps:**
1. **[PLANNING]** Check `pyproject.toml` for current version
2. **[PLANNING]** Review `git tag` history for existing version tags
3. **[EXECUTION]** Determine correct version based on semver convention and existing tags
4. **[EXECUTION]** Document decision with rationale
5. **[VERIFICATION]** Confirm chosen version does not conflict with existing tags
6. **[COMPLETION]** Record version decision in D-0034/notes.md

**Acceptance Criteria:**
- Version number explicitly confirmed as either v2.24.5 or v2.25.1
- Decision includes rationale referencing project version history
- Chosen version does not conflict with existing `git tag` entries
- Decision recorded in .dev/releases/current/v2.24.5/artifacts/D-0034/notes.md

**Validation:**
- Manual check: `git tag | grep <version>` returns no existing tag
- Evidence: version decision in .dev/releases/current/v2.24.5/artifacts/D-0034/notes.md

**Dependencies:** T07.03
**Rollback:** N/A (decision only)
**Notes:** Version discrepancy noted in roadmap: spec references v2.25.1, roadmap uses v2.24.5.

---

### T07.06 -- Tag release

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | Release must be tagged for distribution and version tracking. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0035/evidence.md

**Deliverables:**
- Git tag created with confirmed version number from T07.05

**Steps:**
1. **[PLANNING]** Read confirmed version from T07.05 (D-0034/notes.md)
2. **[PLANNING]** Verify HEAD is at the correct commit (after all fix commits)
3. **[EXECUTION]** Create tag: `git tag <confirmed-version>`
4. **[EXECUTION]** Verify tag: `git tag | grep <confirmed-version>`
5. **[VERIFICATION]** Tag exists and points to HEAD
6. **[COMPLETION]** Record tag details in D-0035/evidence.md

**Acceptance Criteria:**
- Git tag created with version confirmed in T07.05
- Tag points to HEAD (after all fix commits)
- `git tag | grep <confirmed-version>` returns the tag
- Tag details recorded in .dev/releases/current/v2.24.5/artifacts/D-0035/evidence.md

**Validation:**
- Manual check: `git tag --points-at HEAD` returns the confirmed version
- Evidence: tag confirmation in .dev/releases/current/v2.24.5/artifacts/D-0035/evidence.md

**Dependencies:** T07.05
**Rollback:** `git tag -d <confirmed-version>`
**Notes:** Pending version confirmation from T07.05.

---

### Checkpoint: End of Phase 7

**Purpose:** Confirm release is properly committed, tagged, and ready for distribution.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P07-END.md

**Verification:**
- FIX-001 commit exists with correct message and files
- FIX-ARG-TOO-LONG commit exists with correct message and files
- Release tag exists and points to correct HEAD commit

**Exit Criteria:**
- All commits created with conventional commit messages matching roadmap specification
- Version number confirmed and tag created
- M4 milestone (Release tagged and committed) achieved
