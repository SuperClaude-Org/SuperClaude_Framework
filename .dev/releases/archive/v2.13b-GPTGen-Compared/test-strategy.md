---
spec_source: ".dev/releases/current/v2.13-CLIRunner-PipelineUnification/release-spec.md"
generated: "2026-03-05T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 1
work_milestones: 3
interleave_ratio: "1:3"
major_issue_policy: stop-and-fix
complexity_class: LOW
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** -- the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop -- work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:3 (one validation milestone per 3 work milestones), derived from complexity class LOW

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M3 (Roadmap File-Passing Fix) | M1 test coverage, M2 hook migration correctness, M3 file-passing behavior | Any D4 test regression, NFR-007 violation, or coverage < 70% |

**Placement rule**: With a 1:3 interleave ratio and 3 work milestones (M1, M2, M3), one validation milestone V1 is placed after M3. V1 (= M4 in the roadmap) validates all preceding work milestones.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | SIGTERM/SIGKILL escalation broken, NFR-007 violated, test suite red |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Hook fires with wrong arguments, characterization test fails on current code, dead code deletion breaks import |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Debug log format differs from current, test coverage at 68% (close to 70% threshold) |
| Info | Log only, no action required | N/A | Optimization opportunity in hook factory, additional test case idea |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | 12+ new test cases, all pass on current code, coverage >= 70% | `uv run pytest tests/sprint/test_executor_characterization.py -v` passes; `--cov` shows >= 70% |
| M2 (M2a) | wait() override deleted, all tests pass | Zero test failures after deletion |
| M2 (M2b) | Hooks added to base, sprint migrated, all tests pass, NFR-007 clean | Full suite green; grep returns 0 pipeline-to-sprint imports |
| M2 (M2c) | Dead code deleted, grep confirms 0 references | `grep -rn "_build_subprocess_argv" src/` returns 0 |
| M3 | Inline embedding works, size guard tested, --file flags removed | Unit test: prompt contains embedded content; integration test: paths with spaces handled |
| M4 | All SC-001 through SC-005 met | All 5 success criteria verified with measurement evidence |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | D2.2, D2.3 unit tests | M2 | Unit test: hooks called with correct args when provided; no-op when None |
| FR-002 | D2.5 + D4 characterization suite | M2 | Run D4 tests before/after override deletion; behavioral equivalence |
| FR-003 | D2.6 grep check | M2 | `grep -r` confirms no sprint/roadmap types in pipeline module |
| FR-004 | D2.2 unit tests | M2 | Unit test: hook fires before _log.debug; no try/except around hook call |
| FR-005 | D2.7 grep + test suite | M2 | Negative grep + full suite green |
| FR-006 | D3.3 integration test | M3 | Test fixture comparison: inline prompt vs --file output equivalence |
| FR-007 | D3.3 size guard test | M3 | Test with >100KB mock input triggers --file fallback path |
| FR-008 | D1.1-D1.4 test execution | M1 | 12+ new tests pass on current codebase; coverage measurement |
| FR-009 | D2.3 unit test | M2 | Test: on_exit fires in wait() success path (not just terminate()) |
| FR-010 | D2.4 unit test | M2 | Test: hook factory produces was_timeout=True only when returncode==124 |
| NFR-001 | D4.1 full suite | M4 | `uv run pytest` zero regressions |
| NFR-002 | D4.5 grep | M4 | `grep -r` returns 0 |
| NFR-003 | M2 gate | M2 | D4 tests run before/after every M2 deliverable |
| NFR-004 | D4.6 pyproject.toml diff | M4 | `git diff pyproject.toml` shows no additions to [project.dependencies] |
