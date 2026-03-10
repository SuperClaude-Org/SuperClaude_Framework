---
spec_source: "spec-roadmap-pipeline-reliability.md"
complexity_score: 0.72
adversarial: true
---

# Roadmap: Roadmap Pipeline Reliability (Merged)

## Executive Summary

This release hardens the `superclaude roadmap` CLI pipeline against frontmatter validation failures caused by three root issues: (1) a gate function that only checks byte-0 for frontmatter, (2) no sanitization of LLM preamble text before gate validation, and (3) prompt instructions that don't sufficiently constrain LLM output format. The fix applies defense-in-depth across four phases touching 4 files in 2 package subdirectories.

The architecture addresses a systemic reliability gap — not a single bug. Four independent defense layers (detection correctness, artifact sanitation, prompt hardening, protocol parity) ensure that no single LLM behavior change or infrastructure drift can cause pipeline failures. The shared `_check_frontmatter()` gate is the highest-risk change due to cross-pipeline impact; all other changes are scoped to the roadmap executor.

Total scope: 26 requirements (20 functional, 6 non-functional), moderate complexity (0.72). Estimated effort: 12-18 hours for a single experienced developer.

## Phased Implementation Plan

### Phase 1: Gate Fix — Tolerant Frontmatter Discovery

**Files:** `src/superclaude/cli/pipeline/gates.py`
**Risk:** Medium-high (shared infrastructure)
**Estimated effort:** 3-5 hours (includes scoping prerequisite)

#### Scoping Prerequisite (2-3 hours, time-boxed)

Before writing the regex, confirm the implementation surface:

1. Run `grep -r "_check_frontmatter" src/` to enumerate all callers and confirm shared usage scope
2. Confirm the canonical extraction frontmatter field set from `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md` — enumerate all 13+ fields explicitly
3. Capture one failing artifact and one passing artifact as test fixtures from current pipeline output
4. Record caller inventory for regression test planning

**Exit gate:** Canonical field list documented, caller count confirmed, at least 2 fixture files captured.

#### Implementation

1. Replace the byte-0 frontmatter check in `_check_frontmatter()` with `re.search()` using a compiled `_FRONTMATTER_PATTERN` module-level constant
2. Pattern must use `re.MULTILINE` and require at least one `key: value` line between `---` delimiters (FR-001, FR-002, FR-006, FR-020)
3. Extract `required_fields` validation from the discovered block via parsed `key: value` lines (FR-003)
4. Return `(False, reason)` when no valid block found or fields missing; `(True, None)` on success (FR-004, FR-005)
5. Write 8 unit test cases:
   - Frontmatter at byte 0 (existing behavior preserved)
   - Frontmatter after preamble text
   - Horizontal rule `---` without key-value content (must not match)
   - Missing required fields
   - Multiple `---` blocks (first valid block wins)
   - Empty document
   - Frontmatter with extra whitespace
   - Existing pipeline gate inputs (regression from caller inventory)

**Coverage dimensions to verify against:** position variants, content variants, encoding variants, delimiter ambiguity. Add test cases beyond the 8 baseline if coverage gaps are discovered.

**Milestone:** All existing pipeline gate tests pass unchanged. New tests pass. Regression verified against all callers identified in scoping step.

**Validation gate:** `uv run pytest tests/pipeline/test_gates.py tests/roadmap/test_gates_data.py -v` — all green, no regressions in other pipeline commands.

### Phase 2: Output Sanitizer

**Files:** `src/superclaude/cli/roadmap/executor.py`
**Risk:** Low (scoped to roadmap executor only)
**Estimated effort:** 3-4 hours

1. Add `_sanitize_output(path: Path) -> int` function that strips content before first YAML frontmatter block (FR-007)
2. Early returns: already clean (starts with `---` after strip) → return 0; no frontmatter found → return 0 (FR-008, FR-009)
3. Implement atomic write: write to `path.with_suffix('.tmp')`, then `os.replace()` (FR-010)
4. Log preamble bytes stripped via `_log.info()` (FR-011)
5. Wire into `roadmap_run_step()` after subprocess completion, before gate validation (FR-012)
6. Write 7 unit test cases:
   - Clean file (no-op)
   - Preamble present (stripped, byte count logged)
   - No frontmatter at all (no-op)
   - Atomic write failure recovery (tmp file cleanup)
   - UTF-8 preservation through rewrite (NFR-004)
   - Idempotence (sanitizing an already-clean file is no-op)
   - Large file up to 10MB (NFR boundary behavior)

**Milestone:** Sanitizer strips preamble from synthetic test artifacts. Atomic write confirmed via interrupted-write test. 10MB boundary verified.

**Validation gate:** `uv run pytest tests/roadmap/test_executor.py -v` — all green.

### Phase 3: Prompt Hardening

**Files:** `src/superclaude/cli/roadmap/prompts.py`
**Risk:** Low (additive, not sole defense)
**Estimated effort:** 1-2 hours

1. Add `<output_format>` XML block to all 7 `build_*_prompt()` functions (FR-013)
2. Each block must include:
   - Positive instruction: "Your response MUST begin with YAML frontmatter"
   - Negative instruction: "Do NOT include any text before the opening `---`"
   - Format template showing expected first lines (FR-014)
3. Place the block at the end of each prompt for recency bias (FR-015)
4. Verify token overhead stays under 200 tokens per function (NFR-005)
5. Write 3 validation checks:
   - All 7 prompt functions contain `<output_format>` block
   - Block appears after main prompt body (position check)
   - Token count delta within budget

**Milestone:** All prompt functions include output constraints. Token overhead verified.

**Note:** Prompt hardening is an additive layer, not a primary control. The gate (P1) and sanitizer (P2) are the deterministic safeguards. Prompt compliance is probabilistic by nature.

### Phase 4: Protocol Parity — Extract Step

**Files:** `src/superclaude/cli/roadmap/prompts.py`, `src/superclaude/cli/roadmap/gates.py`
**Risk:** Medium (coordinated multi-file, downstream impact on generate step)
**Estimated effort:** 3-4 hours (includes E2E validation exit gate)

#### Implementation

1. Update `build_extract_prompt()` to request all 13+ frontmatter fields from source protocol template (FR-016):
   - `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`
2. Update `EXTRACT_GATE` in `roadmap/gates.py` to require expanded field set (FR-017)
3. Ensure `pipeline_diagnostics` and similar executor-populated fields are injected post-subprocess, not requested from LLM (FR-018). Document runtime-only field injection in executor flow to prevent field ownership ambiguity.
4. Verify extract prompt body requests structured sections with FR-NNN/NFR-NNN IDs (FR-019)
5. Verify `build_generate_prompt()` can consume expanded extraction output (NFR-006)
6. Write 4 validation checks:
   - Extract gate requires all 13+ fields
   - Extract prompt references all required fields
   - Executor-populated fields not in LLM prompt
   - Generate step consumes expanded extraction without error

#### E2E Validation Exit Gate

Before marking P4 complete, execute a full integration validation:

1. Run `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` — all 8 steps must complete
2. Inspect all generated `.md` artifacts: immediate frontmatter start, no preamble contamination, required field completeness
3. Confirm downstream generate step parses expanded extraction without failure
4. Run regression checks for other pipeline commands sharing `_check_frontmatter()`
5. Record evidence for each success criterion

**Milestone:** End-to-end pipeline run produces protocol-complete extraction with all 13+ fields. Generate step consumes it cleanly. Full 8-step pipeline completes without frontmatter failures. All intermediate artifacts inspected for preamble contamination.

## Risk Assessment and Mitigation

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|-------------|------------|-------|
| 1 | Regex matches horizontal rules as frontmatter | High | Low | Require `key: value` line between delimiters; dedicated test case | P1 |
| 2 | Sanitizer strips valid pre-frontmatter content | High | Low | Only strip before first `^---$`; atomic write preserves original on failure | P2 |
| 3 | LLM ignores prompt hardening | Low | Medium | Defense-in-depth: P1 gate + P2 sanitizer catch it regardless | P3 |
| 4 | Protocol parity breaks generate step | Medium | Medium | Explicit test that generate prompt consumes expanded extraction; E2E exit gate in P4 | P4 |
| 5 | Shared gate regression in other pipelines | Medium | Low | Backward-compatible regex (strictly more permissive); regression test suite from caller inventory | P1 |
| 6 | Runtime diagnostics field ownership ambiguity | Medium | Low | Separate LLM-authored fields from executor-authored fields; document injection points; test that extraction prompt excludes runtime-only fields | P4 |

### Architectural Risk Notes

**Risk 5 (shared gate)** is the highest-impact concern. `_check_frontmatter()` is shared infrastructure used by all 8 pipeline steps and potentially other pipeline commands. The P1 scoping prerequisite captures the caller inventory. The regex change is strictly more permissive (accepts frontmatter at any position, not just byte 0), so existing valid inputs will continue to pass — but this must be verified empirically against the full caller set.

**Risk 6 (field ownership)** is a cross-file coordination hazard in P4. If both the LLM and the executor attempt to own the same metadata fields, artifacts become inconsistent. The mitigation is clear separation: the extraction prompt requests only LLM-authored fields, and the executor injects runtime-only fields (e.g., `pipeline_diagnostics`) after subprocess completion.

## Resource Requirements and Dependencies

### Technical Dependencies (all stdlib — no new packages)

- `re` — regex with `re.MULTILINE`
- `os` — `os.replace()` for atomic rename
- `pathlib.Path` — file I/O
- `logging` — sanitizer diagnostics

### External Dependencies

- **Source protocol template** (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`): Source of truth for 13+ frontmatter fields. Must be read and validated during P1 scoping prerequisite before P4 implementation.
- **`ClaudeProcess` subprocess behavior**: Sanitizer operates on `ClaudeProcess` stdout. The `--verbose` flag interaction should be investigated during P2 but is not a blocker — the sanitizer handles arbitrary preamble regardless of source.

### Environment

- Python 3.10+ (existing requirement, unchanged)
- `uv run pytest` for all test execution
- Access to sample roadmap pipeline outputs for fixture capture
- At least one real roadmap spec for E2E validation

## Success Criteria and Validation Approach

| # | Criterion | Validation Method |
|---|-----------|-------------------|
| 1 | Full pipeline completion without frontmatter failures | `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes 8/8 steps |
| 2 | Clean artifacts (no preamble) | `grep -L '^---' .dev/releases/*/pipeline-output/*.md` returns empty |
| 3 | Protocol-complete extraction | Extraction frontmatter contains all 13+ fields from template |
| 4 | Test suite green | `uv run pytest tests/pipeline/ tests/roadmap/ -v` — 22+ cases, all pass |
| 5 | No regressions | Other pipeline commands pass their existing gate validations unchanged |
| 6 | Post-release observability | Monitor sanitizer invocation frequency via existing `_log.info` lines; sustained high invocation rate indicates prompt hardening insufficiency requiring follow-up |

## Timeline

| Phase | Description | Effort | Cumulative |
|-------|-------------|--------|------------|
| P1 | Gate fix with scoping prerequisite | 3-5h | 3-5h |
| P2 | Output sanitizer with 10MB boundary test | 3-4h | 6-9h |
| P3 | Prompt hardening (output format constraints) | 1-2h | 7-11h |
| P4 | Protocol parity with E2E exit gate | 3-4h | 10-15h |
| **Buffer** | Discovery friction, unexpected callers, fixture iteration | 2-3h | **12-18h** |

**Recommended execution order:** P1 → [P2 ∥ P3] → P4

P1 (gate) must land first since P2's sanitizer is tested against the new gate logic and P1's scoping prerequisite informs all subsequent phases. P3 (prompts) is independent of P2 and can be parallelized. P4 depends on P1 (gate field expansion) and P3 (extract prompt changes). The E2E validation exit gate in P4 serves as the integration confirmation for the entire release.

## Open Questions — Deferred Decisions

1. **`--verbose` stdout interaction**: Investigate during P2 implementation but do not block on it. The sanitizer is source-agnostic by design.
2. **Other step prompt parity**: Defer to a follow-up release. This release establishes the pattern (extract step); subsequent steps can adopt it incrementally.
3. **Gate tier differentiation**: Defer. The tolerant regex is correct for all tiers today. Strict-tier rejection of preamble can be layered on later without architectural changes.
4. **Generate prompt update scope**: Include basic consumption verification in P4. Full generate prompt rework is out of scope.
5. **Sanitizer and `_embed_inputs()` ordering**: Not a concurrency concern — `roadmap_run_step()` is sequential. The timing constraint (sanitize after subprocess, before gate) is enforced by call order in a single function.
