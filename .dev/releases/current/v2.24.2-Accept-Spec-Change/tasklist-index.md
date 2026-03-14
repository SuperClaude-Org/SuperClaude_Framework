# TASKLIST INDEX -- v2.24.2 Accept-Spec-Change

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.24.2 Accept-Spec-Change |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-13 |
| TASKLIST_ROOT | .dev/releases/current/v2.24.2-Accept-Spec-Change/ |
| Total Phases | 5 |
| Total Tasks | 23 |
| Total Deliverables | 27 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | security, analyzer, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.24.2-Accept-Spec-Change/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.24.2-Accept-Spec-Change/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.24.2-Accept-Spec-Change/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.24.2-Accept-Spec-Change/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.24.2-Accept-Spec-Change/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/v2.24.2-Accept-Spec-Change/phase-5-tasklist.md |
| Execution Log | .dev/releases/current/v2.24.2-Accept-Spec-Change/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/ |
| Validation Reports | .dev/releases/current/v2.24.2-Accept-Spec-Change/validation/ |
| Feedback Log | .dev/releases/current/v2.24.2-Accept-Spec-Change/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation -- spec_patch.py Module | T01.01-T01.04 | STRICT: 3, STANDARD: 1 |
| 2 | phase-2-tasklist.md | CLI Command Registration | T02.01-T02.04 | STRICT: 0, STANDARD: 3, EXEMPT: 1 |
| 3 | phase-3-tasklist.md | Auto-Resume Integration | T03.01-T03.06 | STRICT: 5, STANDARD: 1 |
| 4 | phase-4-tasklist.md | Edge Cases and Hardening | T04.01-T04.04 | STRICT: 4 |
| 5 | phase-5-tasklist.md | Validation and Release | T05.01-T05.05 | STRICT: 1, STANDARD: 2, LIGHT: 1, EXEMPT: 1 |

## Source Snapshot

- Adds spec-hash reconciliation mechanism to roadmap pipeline for mid-execution spec changes
- One new CLI command (`accept-spec-change`), one new leaf module (`spec_patch.py`), surgical additions to `executor.py`
- Architectural invariants: atomic writes via `.tmp` + `os.replace()`, abort paths read-only, disk-reread at resume boundary, `_apply_resume()` unchanged, max one patch/resume cycle
- 13 functional requirements (FR-001 through FR-013), 14 acceptance criteria, 8 NFRs
- 10 identified risks (R1-R10) with mitigations mapped to phases
- Critical path: P1 -> P2 -> P3 -> P4 -> P5 (fully sequential)

## Deterministic Rules Applied

- Phase buckets derived from explicit roadmap Phase labels (Phase 1 through Phase 5)
- Phase numbers preserved as-is (1-5, contiguous, no renumbering needed)
- Task IDs: `T<PP>.<TT>` zero-padded 2-digit format
- 1:1 roadmap-item-to-task mapping (no splits triggered per Section 4.4 criteria)
- Checkpoint cadence: every 5 tasks + end-of-phase mandatory checkpoint
- Clarification tasks: none needed (roadmap resolves all open questions in Phase 2)
- Deliverable IDs: `D-####` in global appearance order
- Effort: deterministic keyword scoring (Section 5.2.1)
- Risk: deterministic keyword scoring (Section 5.2.2)
- Tier classification: keyword matching + context boosters (Section 5.3)
- Verification routing: tier-based method assignment (Section 4.10)
- MCP requirements: tier-based tool dependencies (Section 5.5)
- Multi-file output: index + 5 phase files

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | State-file discovery and hash computation: Create spec_patch.py, implement prompt_accept_spec_change, FR-001 read state, FR-002 recompute SHA-256, FR-003 compare |
| R-002 | Phase 1 | Deviation file scanning: DeviationRecord frozen dataclass, FR-004 glob for dev-*-accepted-deviation.md, parse YAML frontmatter, select ACCEPTED |
| R-003 | Phase 1 | Interactive prompt and atomic write: FR-005 evidence summary, FR-006 atomic write via .tmp + os.replace(), FR-007 confirmation |
| R-004 | Phase 1 | Unit tests: Idempotency, read-only on abort, missing file errors, YAML parse error resilience, non-interactive behavior, atomic |
| R-005 | Phase 2 | Click command registration: Add Click command in commands.py, click.Path(exists=True), zero optional flags, import only from spec_patch.py |
| R-006 | Phase 2 | Dependency management: Add pyyaml>=6.0 to pyproject.toml dependencies, first verify transitive status |
| R-007 | Phase 2 | Integration test: CLI invocation with real file fixtures, exit codes for all error paths |
| R-008 | Phase 2 | Resolve open questions: severity field source, started_at fallback fail-closed, post-acceptance file lifecycle, multiple deviation |
| R-009 | Phase 3 | auto_accept parameter threading: FR-008 add auto_accept bool to execute_roadmap() signature, backward-compatible, thread through call |
| R-010 | Phase 3 | Three-condition detection gate: FR-009 after spec-fidelity FAIL, evaluate recursion guard, qualifying deviation files, |
| R-011 | Phase 3 | Disk-reread sequence FR-010: six-step sequence reread state, recompute hash, atomically write, reread again, rebuild steps, |
| R-012 | Phase 3 | Recursion guard: FR-011 _spec_patch_cycle_count local variable, initialized to 0, max 1 cycle, FR-013 on exhaustion |
| R-013 | Phase 3 | Cycle outcome logging: FR-012 all messages prefixed with [roadmap], entry deviation count, completion success, suppression message |
| R-014 | Phase 3 | Private function naming: _apply_resume_after_spec_patch(), _find_qualifying_deviation_files(), no modification to _apply_resume(), no new public |
| R-015 | Phase 4 | Edge case tests: absent/null/empty spec_hash, .tmp file pre-existence, YAML 1.1 boolean coercion variants, missing started_at |
| R-016 | Phase 4 | Failure-path tests: atomic write failure cycle abort, persistent spec-fidelity failure after retry, recursion guard blocks, |
| R-017 | Phase 4 | TOCTOU and filesystem documentation: RISK-001 docstring documenting single-writer assumption, NFR-005 operator-facing docs, RISK-002 mtime-resolution |
| R-018 | Phase 4 | State integrity validation: verify only spec_hash changes across all mutation paths, verify abort path mtime unchanged, |
| R-019 | Phase 5 | AC matrix validation: verify all acceptance criteria AC-1 through AC-14 mapped to automated tests, verify NFR-001 |
| R-020 | Phase 5 | Module isolation verification: NFR-006 spec_patch.py imports only stdlib + PyYAML, NFR-008 no new public symbols, |
| R-021 | Phase 5 | Documentation updates: CLI help text, developer guide entry, operator documentation of YAML boolean coercions, single-writer assumption, |
| R-022 | Phase 5 | Release gate checklist: all AC mapped to tests, no circular dependency, no new public API, no subprocess |
| R-023 | Phase 5 | Final verification: make sync-dev && make verify-sync && make test && make lint |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | `spec_patch.py` module with `prompt_accept_spec_change()` implementing FR-001/002/003 | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0001/spec.md | M | Medium |
| D-0002 | T01.02 | R-002 | `DeviationRecord` dataclass and YAML frontmatter parser with ACCEPTED filter | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0002/spec.md | M | Medium |
| D-0003 | T01.03 | R-003 | Interactive prompt with `sys.stdin.isatty()` guard and atomic `.tmp` + `os.replace()` write | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0003/spec.md | M | Medium |
| D-0004 | T01.04 | R-004 | Unit test suite in `tests/roadmap/test_accept_spec_change.py` covering AC-1/2/3/4/11/14 | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0004/evidence.md | M | Low |
| D-0005 | T02.01 | R-005 | Click command `accept-spec-change` registered in `commands.py` | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0005/spec.md | S | Low |
| D-0006 | T02.02 | R-006 | `pyyaml>=6.0` in `pyproject.toml` (verified transitive or added) | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0006/evidence.md | XS | Low |
| D-0007 | T02.03 | R-007 | Integration test for CLI invocation with file fixtures and exit code verification | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0007/evidence.md | S | Low |
| D-0008 | T02.04 | R-008 | Decision artifact documenting 4 resolved open questions with rationale | EXEMPT | Skip verification | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0008/notes.md | S | Low |
| D-0009 | T03.01 | R-009 | `auto_accept: bool = False` parameter on `execute_roadmap()` with call-chain threading | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0009/spec.md | M | Medium |
| D-0010 | T03.02 | R-010 | Three-condition detection gate in `executor.py` (recursion guard + deviation mtime + hash diff) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0010/spec.md | L | High |
| D-0011 | T03.03 | R-011 | Six-step disk-reread sequence implementation in `executor.py` | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0011/spec.md | L | High |
| D-0012 | T03.04 | R-012 | `_spec_patch_cycle_count` local guard with max-1 enforcement and halt-on-exhaustion | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0012/spec.md | M | Medium |
| D-0013 | T03.05 | R-013 | `[roadmap]`-prefixed log messages for cycle entry, completion, and suppression | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0013/spec.md | S | Low |
| D-0014 | T03.06 | R-014 | Private function signatures (`_apply_resume_after_spec_patch`, `_find_qualifying_deviation_files`) with no public API additions | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0014/spec.md | S | Low |
| D-0015 | T04.01 | R-015 | Edge case test cases for absent/null/empty `spec_hash`, `.tmp` pre-existence, YAML boolean coercion, missing `started_at` | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0015/evidence.md | M | Medium |
| D-0016 | T04.02 | R-016 | Failure-path test cases for write failure abort, persistent failure after retry, recursion guard block, state integrity | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0016/evidence.md | M | High |
| D-0017 | T04.03 | R-017 | Docstrings documenting single-writer assumption (RISK-001), operator docs for exclusive access (NFR-005), mtime-resolution comments (RISK-002) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0017/spec.md | S | Low |
| D-0018 | T04.04 | R-018 | State integrity validation tests confirming only `spec_hash` changes, abort mtime unchanged, disk-reread state used for resume | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0018/evidence.md | M | Medium |
| D-0019 | T05.01 | R-019 | AC traceability report mapping AC-1 through AC-14 and NFR-001 through NFR-008 to automated tests | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0019/evidence.md | M | Low |
| D-0020 | T05.02 | R-020 | Import analysis report confirming `spec_patch.py` isolation (stdlib + PyYAML only) and no new public symbols | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0020/evidence.md | S | Low |
| D-0021 | T05.03 | R-021 | CLI help text for `accept-spec-change` | LIGHT | Quick sanity check | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0021/spec.md | S | Low |
| D-0022 | T05.03 | R-021 | Developer guide entry for auto-resume behavior | LIGHT | Quick sanity check | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0022/spec.md | S | Low |
| D-0023 | T05.03 | R-021 | Operator documentation of YAML boolean coercions and single-writer/mtime limitations | LIGHT | Quick sanity check | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0023/spec.md | S | Low |
| D-0024 | T05.03 | R-021 | Release notes | LIGHT | Quick sanity check | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0024/spec.md | S | Low |
| D-0025 | T05.04 | R-022 | Release gate checklist with all 6 criteria verified and evidenced | STANDARD | Direct test execution | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0025/evidence.md | S | Low |
| D-0026 | T05.05 | R-023 | Clean `make sync-dev && make verify-sync && make test && make lint` run output | EXEMPT | Skip verification | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0026/evidence.md | XS | Low |
| D-0027 | T05.01 | R-019 | NFR verification report confirming NFR-001 through NFR-008 | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0027/evidence.md | M | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STRICT | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0001/ |
| R-002 | T01.02 | D-0002 | STRICT | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0002/ |
| R-003 | T01.03 | D-0003 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0003/ |
| R-004 | T01.04 | D-0004 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0004/ |
| R-005 | T02.01 | D-0005 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0005/ |
| R-006 | T02.02 | D-0006 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0006/ |
| R-007 | T02.03 | D-0007 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0007/ |
| R-008 | T02.04 | D-0008 | EXEMPT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0008/ |
| R-009 | T03.01 | D-0009 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0009/ |
| R-010 | T03.02 | D-0010 | STRICT | [█████████░] 90% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0010/ |
| R-011 | T03.03 | D-0011 | STRICT | [█████████░] 90% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0011/ |
| R-012 | T03.04 | D-0012 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0012/ |
| R-013 | T03.05 | D-0013 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0013/ |
| R-014 | T03.06 | D-0014 | STRICT | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0014/ |
| R-015 | T04.01 | D-0015 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0015/ |
| R-016 | T04.02 | D-0016 | STRICT | [█████████░] 90% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0016/ |
| R-017 | T04.03 | D-0017 | STRICT | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0017/ |
| R-018 | T04.04 | D-0018 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0018/ |
| R-019 | T05.01 | D-0019, D-0027 | STRICT | [████████░░] 85% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0019/, .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0027/ |
| R-020 | T05.02 | D-0020 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0020/ |
| R-021 | T05.03 | D-0021, D-0022, D-0023, D-0024 | LIGHT | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0021/ through D-0024/ |
| R-022 | T05.04 | D-0025 | STANDARD | [████████░░] 80% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0025/ |
| R-023 | T05.05 | D-0026 | EXEMPT | [█████████░] 90% | .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0026/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

**Template:**

# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/<deterministic-name>.md

**Scope:** <tasks covered>

## Status

Overall: Pass | Fail | TBD

## Verification Results

- <bullet 1>
- <bullet 2>
- <bullet 3>

## Exit Criteria Assessment

- <bullet 1>
- <bullet 2>
- <bullet 3>

## Issues & Follow-ups

- <list blocking issues referencing T<PP>.<TT> and D-####>

## Evidence

- .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/<path>

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |
