# TASKLIST INDEX -- Roadmap Pipeline Reliability

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | Roadmap Pipeline Reliability |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-08 |
| TASKLIST_ROOT | `.dev/releases/current/v.2.17-roadmap-reliability/` |
| Total Phases | 5 |
| Total Tasks | 17 |
| Total Deliverables | 21 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | architect, security |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Phase 4 Tasklist | `TASKLIST_ROOT/phase-4-tasklist.md` |
| Phase 5 Tasklist | `TASKLIST_ROOT/phase-5-tasklist.md` |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Gate Fix (Foundation) | T01.01-T01.02 | STRICT: 1, STANDARD: 1 |
| 2 | phase-2-tasklist.md | Output Sanitizer + Prompt Hardening | T02.01-T02.05 | STANDARD: 4, EXEMPT: 1 |
| 3 | phase-3-tasklist.md | P1+P2 Integration Validation | T03.01-T03.03 | EXEMPT: 3 |
| 4 | phase-4-tasklist.md | Extract Step Protocol Parity | T04.01-T04.04 | STRICT: 3, STANDARD: 1 |
| 5 | phase-5-tasklist.md | End-to-End Pipeline Validation | T05.01-T05.03 | EXEMPT: 3 |

## Source Snapshot

- Pipeline halts at extract step: `_check_frontmatter()` requires `---` at byte 0, rejecting valid output with conversational preamble
- Defense-in-depth strategy: P1 gate tolerance, P2 output sanitizer, P3 prompt hardening, P4 protocol parity
- All 8 pipeline steps share `_check_frontmatter()` — compound reliability improvement
- 4 affected files: `pipeline/gates.py`, `roadmap/executor.py`, `roadmap/prompts.py`, `roadmap/gates.py`
- MEDIUM complexity (0.42), 27 requirements (21 FR + 6 NFR), 7 risks
- Validation score: 0.92 (PASS)

## Deterministic Rules Applied

- Phase bucketing: roadmap milestones mapped to 5 sequential phases by dependency ordering (M1 → M2+M3 → V1 → M4 → V2)
- Phase renumbering: milestones M1, M2, V1, M3, M4, V2 renumbered to Phases 1-5 contiguously
- Task ID scheme: `T<PP>.<TT>` zero-padded (e.g., T01.01)
- Deliverable ID scheme: `D-####` globally sequential (D-0001 through D-0021)
- Roadmap Item ID scheme: `R-###` in appearance order (R-001 through R-028)
- Checkpoint cadence: end-of-phase checkpoint in every phase (no phase exceeds 5-task inline threshold)
- Effort mapping: deterministic keyword scoring per Section 5.2.1
- Risk mapping: deterministic keyword scoring per Section 5.2.2
- Tier classification: `/sc:task-unified` algorithm with compound phrase overrides, keyword matching, and context boosters
- Verification routing: tier-aligned (STRICT → sub-agent, STANDARD → direct test, EXEMPT → skip)
- MCP requirements: tier-aligned (STRICT requires Sequential+Serena)
- Multi-file output: 1 index + 5 phase files = 6 files total

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤20 words) |
|---|---|---|
| R-001 | Overview | Pipeline halts at extract step due to strict YAML frontmatter parsing |
| R-002 | Phase 1 | Replace strict byte-0 _check_frontmatter() with regex-based search discovering YAML frontmatter anywhere |
| R-003 | Phase 1 | Replace _check_frontmatter() in pipeline/gates.py with regex using re.MULTILINE pattern ^--- |
| R-004 | Phase 1 | Regex requires at least one key: value line between --- delimiters |
| R-005 | Phase 1 | Validate all required_fields from the discovered frontmatter block |
| R-006 | Phase 1 | Unit tests covering 8 test cases from spec §6.1 |
| R-007 | Phase 2 | Add _sanitize_output() to roadmap/executor.py stripping conversational preamble using atomic writes |
| R-008 | Phase 2 | Implement _sanitize_output() function strips all content before first ^--- line |
| R-009 | Phase 2 | Atomic write via .tmp + os.replace() pattern |
| R-010 | Phase 2 | Wire _sanitize_output() into roadmap_run_step() between subprocess completion and gate validation |
| R-011 | Phase 2 | Unit tests covering 5 test cases from spec §6.2 |
| R-012 | Phase 3 | Validate M1 gate fix and M2 output sanitizer work together correctly |
| R-013 | Phase 3 | Run existing pipeline test suite to verify zero regressions |
| R-014 | Phase 3 | Manual test: run superclaude roadmap run extract step with preamble-producing spec |
| R-015 | Phase 3 | Verify sanitizer + gate interaction: inject preamble into test fixture |
| R-016 | Phase 2 | Add XML-tagged output format constraints to all 7 build_*_prompt() functions |
| R-017 | Phase 2 | Add <output_format> XML block to all 7 build_*_prompt() functions |
| R-018 | Phase 2 | XML block placed at end of each prompt (recency bias positioning) |
| R-019 | Phase 2 | Token budget validation: ≤200 tokens added per function |
| R-020 | Phase 4 | Align build_extract_prompt() with source protocol expanding from 3 to 13+ fields |
| R-021 | Phase 4 | Expand build_extract_prompt() to request all 13+ frontmatter fields |
| R-022 | Phase 4 | Update EXTRACT_GATE required fields to match expanded set |
| R-023 | Phase 4 | Expand prompt body to request structured extraction sections |
| R-024 | Phase 4 | Ensure build_generate_prompt() consumes expanded extraction output |
| R-025 | Phase 5 | Validate complete pipeline running superclaude roadmap run end-to-end |
| R-026 | Phase 5 | Full pipeline run completes all 8 steps without errors |
| R-027 | Phase 5 | All artifact .md files start with --- (no preamble) |
| R-028 | Phase 5 | Extraction frontmatter contains all 13+ fields from source protocol |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-003 | Regex-based `_check_frontmatter()` in `pipeline/gates.py` | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0001/spec.md` | M | Medium |
| D-0002 | T01.01 | R-004 | key:value validation between `---` delimiters | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0002/spec.md` | M | Medium |
| D-0003 | T01.01 | R-005 | `required_fields` validation from discovered block | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0003/spec.md` | M | Medium |
| D-0004 | T01.02 | R-006 | 8 unit test cases for `_check_frontmatter()` | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | S | Low |
| D-0005 | T02.01 | R-008 | `_sanitize_output()` function implementation | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0005/spec.md` | S | Medium |
| D-0006 | T02.01 | R-009 | Atomic write via `.tmp` + `os.replace()` | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0006/spec.md` | S | Medium |
| D-0007 | T02.02 | R-010 | `_sanitize_output()` wired into `roadmap_run_step()` | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0007/spec.md` | S | Low |
| D-0008 | T02.03 | R-011 | 5 unit test cases for `_sanitize_output()` | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` | S | Low |
| D-0009 | T02.04 | R-017 | `<output_format>` XML block in all 7 prompts | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0009/spec.md` | S | Low |
| D-0010 | T02.04 | R-018 | XML block at end position (recency bias) | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0010/spec.md` | S | Low |
| D-0011 | T02.05 | R-019 | Token budget validation results (≤200 per function) | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` | XS | Low |
| D-0012 | T03.01 | R-013 | Regression test suite results (zero failures) | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0012/evidence.md` | XS | Low |
| D-0013 | T03.02 | R-014 | Manual extract step test evidence | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0013/evidence.md` | XS | Low |
| D-0014 | T03.03 | R-015 | Sanitizer + gate interaction verification | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0014/evidence.md` | XS | Low |
| D-0015 | T04.01 | R-021 | Expanded `build_extract_prompt()` with 13+ fields | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0015/spec.md` | M | Medium |
| D-0016 | T04.02 | R-022 | Updated `EXTRACT_GATE` required fields | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0016/spec.md` | S | Medium |
| D-0017 | T04.03 | R-023 | Expanded prompt body with 8 structured sections | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0017/spec.md` | S | Low |
| D-0018 | T04.04 | R-024 | Updated `build_generate_prompt()` consuming expanded extraction | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0018/spec.md` | M | Medium |
| D-0019 | T05.01 | R-026 | Full pipeline run completion evidence (all 8 steps) | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0019/evidence.md` | S | Low |
| D-0020 | T05.02 | R-027 | Artifact preamble-free verification evidence | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0020/evidence.md` | XS | Low |
| D-0021 | T05.03 | R-028 | Extraction frontmatter 13+ field verification | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0021/evidence.md` | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0001/spec.md` |
| R-002 | T01.01 | D-0001, D-0002, D-0003 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0001/spec.md` |
| R-003 | T01.01 | D-0001 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0001/spec.md` |
| R-004 | T01.01 | D-0002 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0002/spec.md` |
| R-005 | T01.01 | D-0003 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0003/spec.md` |
| R-006 | T01.02 | D-0004 | STANDARD | 90% | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` |
| R-007 | T02.01 | D-0005, D-0006 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0005/spec.md` |
| R-008 | T02.01 | D-0005 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0005/spec.md` |
| R-009 | T02.01 | D-0006 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0006/spec.md` |
| R-010 | T02.02 | D-0007 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0007/spec.md` |
| R-011 | T02.03 | D-0008 | STANDARD | 90% | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` |
| R-012 | T03.01, T03.02, T03.03 | D-0012, D-0013, D-0014 | EXEMPT | 90% | `TASKLIST_ROOT/artifacts/D-0012/evidence.md` |
| R-013 | T03.01 | D-0012 | EXEMPT | 90% | `TASKLIST_ROOT/artifacts/D-0012/evidence.md` |
| R-014 | T03.02 | D-0013 | EXEMPT | 85% | `TASKLIST_ROOT/artifacts/D-0013/evidence.md` |
| R-015 | T03.03 | D-0014 | EXEMPT | 88% | `TASKLIST_ROOT/artifacts/D-0014/evidence.md` |
| R-016 | T02.04 | D-0009, D-0010 | STANDARD | 82% | `TASKLIST_ROOT/artifacts/D-0009/spec.md` |
| R-017 | T02.04 | D-0009 | STANDARD | 82% | `TASKLIST_ROOT/artifacts/D-0009/spec.md` |
| R-018 | T02.04 | D-0010 | STANDARD | 82% | `TASKLIST_ROOT/artifacts/D-0010/spec.md` |
| R-019 | T02.05 | D-0011 | EXEMPT | 88% | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` |
| R-020 | T04.01 | D-0015 | STRICT | 78% | `TASKLIST_ROOT/artifacts/D-0015/spec.md` |
| R-021 | T04.01 | D-0015 | STRICT | 78% | `TASKLIST_ROOT/artifacts/D-0015/spec.md` |
| R-022 | T04.02 | D-0016 | STRICT | 82% | `TASKLIST_ROOT/artifacts/D-0016/spec.md` |
| R-023 | T04.03 | D-0017 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0017/spec.md` |
| R-024 | T04.04 | D-0018 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0018/spec.md` |
| R-025 | T05.01 | D-0019 | EXEMPT | 92% | `TASKLIST_ROOT/artifacts/D-0019/evidence.md` |
| R-026 | T05.01 | D-0019 | EXEMPT | 92% | `TASKLIST_ROOT/artifacts/D-0019/evidence.md` |
| R-027 | T05.02 | D-0020 | EXEMPT | 92% | `TASKLIST_ROOT/artifacts/D-0020/evidence.md` |
| R-028 | T05.03 | D-0021 | EXEMPT | 92% | `TASKLIST_ROOT/artifacts/D-0021/evidence.md` |

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤12 words) | Validation Run | Result | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

**Template:**

```markdown
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md
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
- <bullet list of paths under TASKLIST_ROOT/evidence/>
```

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |
