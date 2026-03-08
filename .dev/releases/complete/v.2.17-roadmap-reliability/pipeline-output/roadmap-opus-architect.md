

---
spec_source: "spec-roadmap-pipeline-reliability.md"
complexity_score: 0.72
primary_persona: architect
---

# Roadmap: Roadmap Pipeline Reliability

## Executive Summary

This release hardens the `superclaude roadmap` CLI pipeline against frontmatter validation failures caused by three root issues: (1) a gate function that only checks byte-0 for frontmatter, (2) no sanitization of LLM preamble text before gate validation, and (3) prompt instructions that don't sufficiently constrain LLM output format. The fix applies defense-in-depth across four phases touching 4 files in 2 package subdirectories.

The architecture is well-scoped. The shared `_check_frontmatter()` gate is the highest-risk change due to cross-pipeline impact; all other changes are scoped to the roadmap executor. Total scope: 26 requirements (20 functional, 6 non-functional), moderate complexity (0.72).

## Phased Implementation Plan

### Phase 1: Gate Fix — Tolerant Frontmatter Discovery
**Files:** `src/superclaude/cli/pipeline/gates.py`
**Risk:** Medium-high (shared infrastructure)
**Estimated effort:** 2-3 hours

1. Replace the byte-0 frontmatter check in `_check_frontmatter()` with `re.search()` using a compiled `_FRONTMATTER_PATTERN` module-level constant
2. Pattern must use `re.MULTILINE` and require at least one `key: value` line between `---` delimiters (FR-001, FR-002, FR-006, FR-020)
3. Extract `required_fields` validation from the discovered block via parsed `key: value` lines (FR-003)
4. Return `(False, reason)` when no valid block found or fields missing; `(True, None)` on success (FR-004, FR-005)
5. Write 8 unit test cases covering:
   - Frontmatter at byte 0 (existing behavior preserved)
   - Frontmatter after preamble text
   - Horizontal rule `---` without key-value content (must not match)
   - Missing required fields
   - Multiple `---` blocks (first valid block wins)
   - Empty document
   - Frontmatter with extra whitespace
   - Existing pipeline gate inputs (regression)

**Milestone:** All existing pipeline gate tests pass unchanged. New tests pass.

**Validation gate:** Run `uv run pytest tests/pipeline/test_gates.py tests/roadmap/test_gates_data.py -v` — all green, no regressions in other pipeline commands.

### Phase 2: Output Sanitizer
**Files:** `src/superclaude/cli/roadmap/executor.py`
**Risk:** Low (scoped to roadmap executor only)
**Estimated effort:** 2-3 hours

1. Add `_sanitize_output(path: Path) -> int` function that strips content before first YAML frontmatter block (FR-007)
2. Early returns: already clean (starts with `---` after strip) → return 0; no frontmatter found → return 0 (FR-008, FR-009)
3. Implement atomic write: write to `path.with_suffix('.tmp')`, then `os.replace()` (FR-010)
4. Log preamble bytes stripped via `_log.info()` (FR-011)
5. Wire into `roadmap_run_step()` after subprocess completion, before gate validation (FR-012)
6. Write 5 unit test cases:
   - Clean file (no-op)
   - Preamble present (stripped, byte count logged)
   - No frontmatter at all (no-op)
   - Atomic write failure recovery (tmp file cleanup)
   - UTF-8 preservation through rewrite (NFR-004)

**Milestone:** Sanitizer strips preamble from synthetic test artifacts. Atomic write confirmed via interrupted-write test.

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

### Phase 4: Protocol Parity — Extract Step
**Files:** `src/superclaude/cli/roadmap/prompts.py`, `src/superclaude/cli/roadmap/gates.py`
**Risk:** Medium (coordinated multi-file, downstream impact on generate step)
**Estimated effort:** 2-3 hours

1. Update `build_extract_prompt()` to request all 13+ frontmatter fields from source protocol template (FR-016):
   - `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`
2. Update `EXTRACT_GATE` in `roadmap/gates.py` to require expanded field set (FR-017)
3. Ensure `pipeline_diagnostics` and similar executor-populated fields are injected post-subprocess, not requested from LLM (FR-018)
4. Verify extract prompt body requests structured sections with FR-NNN/NFR-NNN IDs (FR-019)
5. Verify `build_generate_prompt()` can consume expanded extraction output (NFR-006)
6. Write 4 validation checks:
   - Extract gate requires all 13+ fields
   - Extract prompt references all required fields
   - Executor-populated fields not in LLM prompt
   - Generate step consumes expanded extraction without error

**Milestone:** End-to-end pipeline run produces protocol-complete extraction with all 13+ fields. Generate step consumes it cleanly.

## Risk Assessment and Mitigation

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|-------------|------------|-------|
| 1 | Regex matches horizontal rules as frontmatter | High | Low | Require `key: value` line between delimiters; dedicated test case | P1 |
| 2 | Sanitizer strips valid pre-frontmatter content | High | Low | Only strip before first `^---$`; atomic write preserves original on failure | P2 |
| 3 | LLM ignores prompt hardening | Low | Medium | Defense-in-depth: P1 gate + P2 sanitizer catch it regardless | P3 |
| 4 | Protocol parity breaks generate step | Medium | Medium | Explicit test that generate prompt consumes expanded extraction | P4 |
| 5 | Shared gate regression in other pipelines | Medium | Low | Backward-compatible regex; regression test suite for existing pipelines | P1 |

**Architectural risk note:** The highest-impact risk is #5 — `_check_frontmatter()` is shared infrastructure used by all 8 pipeline steps and potentially other pipeline commands. P1 must include regression tests against representative inputs from all pipeline consumers. The regex change is strictly more permissive (accepts frontmatter at any position, not just byte 0), so existing valid inputs will continue to pass, but this must be verified empirically.

## Resource Requirements and Dependencies

### Dependencies (all stdlib — no new packages)
- `re` — regex with `re.MULTILINE`
- `os` — `os.replace()` for atomic rename
- `pathlib.Path` — file I/O
- `logging` — sanitizer diagnostics

### External Dependencies
- **Source protocol template** (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`): Source of truth for 13+ frontmatter fields. Must be read and validated before P4 implementation.
- **`ClaudeProcess` subprocess behavior**: Sanitizer operates on `ClaudeProcess` stdout. The `--verbose` flag interaction (Open Question #1) should be investigated during P2 but is not a blocker — the sanitizer handles arbitrary preamble regardless of source.

### Environment
- Python 3.10+ (existing requirement, unchanged)
- `uv run pytest` for all test execution

## Success Criteria and Validation

| # | Criterion | Validation Method |
|---|-----------|-------------------|
| 1 | Full pipeline completion without frontmatter failures | `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes 8/8 steps |
| 2 | Clean artifacts (no preamble) | `grep -L '^---' .dev/releases/*/pipeline-output/*.md` returns empty |
| 3 | Protocol-complete extraction | Extraction frontmatter contains all 13+ fields from template |
| 4 | Test suite green | `uv run pytest tests/pipeline/ tests/roadmap/ -v` — 20+ cases, all pass |
| 5 | No regressions | Other pipeline commands pass their existing gate validations unchanged |

## Timeline

| Phase | Description | Effort | Cumulative |
|-------|-------------|--------|------------|
| P1 | Gate fix (tolerant frontmatter discovery) | 2-3h | 2-3h |
| P2 | Output sanitizer (atomic preamble stripping) | 2-3h | 4-6h |
| P3 | Prompt hardening (output format constraints) | 1-2h | 5-8h |
| P4 | Protocol parity (extract step field expansion) | 2-3h | 7-11h |
| **Total** | | **7-11h** | |

Phases are ordered by architectural dependency: P1 (gate) must land first since P2's sanitizer is tested against the new gate logic. P3 (prompts) is independent and could be parallelized with P2. P4 depends on P1 (gate field expansion) and P3 (extract prompt changes).

**Recommended execution order:** P1 → [P2 ∥ P3] → P4

## Open Questions — Architect Recommendations

1. **`--verbose` stdout interaction**: Investigate during P2 implementation but do not block on it. The sanitizer is source-agnostic by design.
2. **Other step prompt parity**: Defer to a follow-up release. This release establishes the pattern (extract step); subsequent steps can adopt it incrementally.
3. **Gate tier differentiation**: Defer. The tolerant regex is correct for all tiers today. Strict-tier rejection of preamble can be layered on later without architectural changes.
4. **Generate prompt update scope**: Include basic consumption verification in P4 (the prompt must accept the new fields). Full generate prompt rework is out of scope.
5. **Sanitizer and `_embed_inputs()` race**: Not a real race condition — `roadmap_run_step()` is sequential. The spec's timing constraint (sanitize after subprocess, before gate) is enforced by call order in a single function. No concurrency concern.
6. **10MB threshold**: Acceptable for now. Observed artifacts are well under 1MB. Add a size check log warning if file exceeds 5MB; defer streaming I/O to a future release if needed.
