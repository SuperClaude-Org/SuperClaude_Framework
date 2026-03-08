---
spec_source: ".dev/releases/current/v.2.17-roadmap-reliability/spec-roadmap-pipeline-reliability.md"
generated: "2026-03-08T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 4
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Output Sanitizer) | M1 gate fix backward compatibility + M2 sanitizer correctness + M1-M2 integration | Any regression in existing pipeline tests; sanitizer fails to clean known preamble fixture |
| V2 | M4 (Extract Step Protocol Parity) | Full pipeline: all 8 steps complete, clean artifacts, expanded frontmatter, prompt hardening effective | Any step fails; preamble in artifacts; missing frontmatter fields; generate step breakage |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | `_check_frontmatter()` regression breaks existing pipelines; atomic write corrupts file |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Gate regex false positive on horizontal rules; sanitizer strips valid content; generate step fails to consume expanded extraction |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Token budget slightly over 200 per prompt; log message format inconsistency |
| Info | Log only, no action required | N/A | Alternative regex pattern suggestion; prompt wording improvement opportunity |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | 8 unit test cases from §6.1 pass; existing pipeline tests pass | All D1.1-D1.4 acceptance criteria met, no Critical/Major issues |
| M2 | 5 unit test cases from §6.2 pass; atomic write verified | All D2.1-D2.4 acceptance criteria met, no Critical/Major issues |
| V1 | Regression suite green; manual preamble injection test passes | All D-V1.1-D-V1.3 criteria met |
| M3 | All 7 prompts contain `<output_format>` at end; token delta ≤200 | All D3.1-D3.3 acceptance criteria met |
| M4 | Extract prompt requests 13+ fields; gate validates them; generate consumes them | All D4.1-D4.4 acceptance criteria met, no Critical/Major issues |
| V2 | Full pipeline run completes all 8 steps; clean artifacts; expanded frontmatter | All D-V2.1-D-V2.3 criteria met |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 | M1 | Unit test: preamble before frontmatter returns `(True, None)` |
| FR-002 | V1 | M1 | Unit test: horizontal rule without key:value returns `(False, ...)` |
| FR-003 | V1 | M1 | Unit test: missing required field returns `(False, ...)` |
| FR-004 | V1 | M1 | Unit test: no frontmatter returns `(False, ...)` |
| FR-005 | V1 | M1 | Unit test: valid frontmatter returns `(True, None)` |
| FR-006 | V1 | M1 | Code review: regex uses `re.MULTILINE` flag |
| FR-010 | V1 | M2 | Unit test: `_sanitize_output()` function exists and is callable |
| FR-011 | V1 | M2 | Unit test: preamble stripped, file starts with `---` |
| FR-012 | V1 | M2 | Unit test: clean file unchanged, returns 0 |
| FR-013 | V1 | M2 | Unit test: no-frontmatter file unchanged, returns 0 |
| FR-014 | V1 | M2 | Code review: `.tmp` + `os.replace()` pattern used |
| FR-015 | V1 | M2 | Unit test: log output contains byte count |
| FR-016 | V1 | M2 | Code review: `roadmap_run_step()` calls `_sanitize_output()` before gate |
| FR-020 | V2 | M3 | Grep: all 7 `build_*_prompt()` contain `<output_format>` |
| FR-021 | V2 | M3 | Grep: each contains `---` start instruction and negative prohibition |
| FR-022 | V2 | M3 | Parse: `<output_format>` is last XML block in each prompt |
| FR-030 | V2 | M4 | Parse: `build_extract_prompt()` output mentions all 13+ field names |
| FR-031 | V2 | M4 | Parse: all listed fields appear in prompt |
| FR-032 | V2 | M4 | Code review: `EXTRACT_GATE` includes expanded field list |
| FR-033 | V2 | M4 | Code review: executor populates `pipeline_diagnostics` post-subprocess |
| FR-034 | V2 | M4 | Parse: prompt body requests all 8 structured sections |
| NFR-001 | V1 | M1 | Regression test: existing pipeline tests pass |
| NFR-002 | V1 | M1 | Unit test: currently-passing files still pass |
| NFR-003 | V2 | M2 | Test: 10MB file processed without error or timeout |
| NFR-004 | V1 | M2 | Unit test: output file encoding is UTF-8 |
| NFR-005 | V2 | M3 | Measurement: token count delta ≤200 per function |
| NFR-006 | V2 | M4 | Integration test: generate step consumes expanded extraction |
