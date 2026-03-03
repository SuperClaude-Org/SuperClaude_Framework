# Pass 2: Structural Audit Rules

## Goal
Validate placement, staleness, broken references, and structural issues — things that "look fine" but aren't. Requires per-file proof.

## Guiding Question
**"Is this file in the right place, correctly documented, and structurally sound?"**

## Scope Limitation
**Only files marked KEEP or REVIEW from Pass 1.** Files classified as DELETE in Pass 1 are excluded.

## Finding Types (Diagnostic)

| Finding Type | Meaning | Trigger |
|-------------|---------|---------|
| MISPLACED | Valid content in wrong location | File type doesn't match directory convention |
| STALE | Outdated or no longer accurate | References to removed files/APIs, outdated versions |
| STRUCTURAL ISSUE | Internal problems requiring code changes | Dead imports, unused exports, circular deps |
| BROKEN REFS | References to non-existent paths or files | Referenced file/path does not exist |
| VERIFIED OK | Confirmed correct with evidence | All checks pass |

## Action Recommendations (Prescriptive)

| Action | Meaning | Evidence Required |
|--------|---------|-------------------|
| KEEP | Verified; has evidence of active use | At least one reference + sensible location |
| DELETE | Confirmed dead with evidence | Zero references + no dynamic loading |
| MOVE | Valid but wrong location | Clear target rationale + refs to update |
| FLAG | Needs code changes or human decision | Issue described + action specified + impact estimated |

## Mandatory Per-File Profile (8 Fields — ALL REQUIRED)

| # | Field | Requirement |
|---|-------|-------------|
| 1 | **What it does** | 1-2 sentence plain-English explanation |
| 2 | **Nature** | Classify: script / test / doc / config / source code / data / asset / migration / one-time artifact |
| 3 | **References** | Who/what references this file? Grep results with files + line numbers. "None found" is valid but must be stated explicitly |
| 4 | **CI/CD usage** | Called by any automation? Check workflows, compose files, Makefile, package.json, Dockerfiles |
| 5 | **Superseded by / duplicates** | Is there a newer/better version? Check for `_v2`, `_enhanced`, `_new` variants |
| 6 | **Risk notes** | Runtime/CI/test/doc impact if removed or moved |
| 7 | **Recommendation** | KEEP / MOVE / DELETE / FLAG with finding type where applicable |
| 8 | **Verification notes** | Explicit list of what was checked (prevents lazy KEEP) |

## Failure Criterion

**Reports missing mandatory per-file profiles are FAILED and must be regenerated.**

A profile is considered missing if any of the 8 fields is absent or contains only "N/A" without justification.

## Extra Rules by File Type

### Tests
- Check test runner discovery: Is the file in a test-discovered path?
- Check test patterns: pytest conventions, Jest patterns, Go test naming
- Verify the test would actually run (not orphaned outside test discovery)
- Check if test targets still exist (testing dead code = dead test)

### Scripts
- Check if functionality is handled by a canonical script elsewhere
- Verify schema/field names reference current data structures
- Check if script is referenced in package.json, Makefile, or CI workflows

### Documentation
- **Verify 3-5 technical claims** against actual implementation
- Check referenced files/paths actually exist
- Highest-value finding: "this README/doc describes things that don't exist"
- Check version numbers, API endpoints, configuration values against actual state

### Config
- Compare with similar configs in other directories
- Check if values match current architecture (ports, paths, feature flags)
- Verify config is loaded by at least one runtime/build/CI system

## Evidence Standards

- Every KEEP needs at least one verified reference (file:line)
- Every DELETE needs grep proof + dynamic loading check
- Every FLAG needs specific actionable description
- Every MOVE needs target location rationale + list of refs to update

## Incremental Save Protocol

Save after every 5-10 files. Never accumulate more than 10 unwritten results.
