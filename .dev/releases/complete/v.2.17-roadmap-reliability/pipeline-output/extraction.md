---
spec_source: "spec-roadmap-pipeline-reliability.md"
generated: "2026-03-08T00:00:00Z"
generator: "claude-opus-4-6/requirements-extractor"
functional_requirements: 20
nonfunctional_requirements: 6
total_requirements: 26
complexity_score: 0.72
complexity_class: moderate
domains_detected: 4
risks_identified: 5
dependencies_identified: 6
success_criteria_count: 5
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 64.0, started_at: "2026-03-08T15:04:15.043346+00:00", finished_at: "2026-03-08T15:05:19.058822+00:00"}
---

## Functional Requirements

**FR-001:** `_check_frontmatter()` in `src/superclaude/cli/pipeline/gates.py` SHALL locate YAML frontmatter anywhere in the document, not only at byte 0. Uses `re.search()` instead of checking document start.

**FR-002:** The frontmatter regex SHALL require at least one `key: value` line between `---` delimiters to distinguish frontmatter from markdown horizontal rules.

**FR-003:** The function SHALL extract and validate all `required_fields` from the discovered frontmatter block by parsing `key: value` lines and checking set membership.

**FR-004:** The function SHALL return `(False, reason)` when no valid frontmatter block is found anywhere in the content, or when any required field is absent from the discovered frontmatter.

**FR-005:** The function SHALL return `(True, None)` when a valid frontmatter block is found and all required fields are present.

**FR-006:** The regex pattern SHALL use `re.MULTILINE` to anchor `^---` to line beginnings, not just document start.

**FR-007:** A new function `_sanitize_output()` SHALL be added to `src/superclaude/cli/roadmap/executor.py` that strips all content before the first YAML frontmatter block from artifact files.

**FR-008:** `_sanitize_output()` SHALL return 0 and make no changes if the file already starts with `---` (after whitespace stripping).

**FR-009:** `_sanitize_output()` SHALL return 0 and make no changes if no frontmatter block is found at all.

**FR-010:** File rewrite in `_sanitize_output()` SHALL use atomic write (write to `.tmp`, then `os.replace`) to prevent partial writes.

**FR-011:** `_sanitize_output()` SHALL log the number of preamble bytes stripped.

**FR-012:** `roadmap_run_step()` SHALL call `_sanitize_output()` after subprocess completion and before gate validation.

**FR-013:** All 7 `build_*_prompt()` functions in `src/superclaude/cli/roadmap/prompts.py` SHALL include XML-tagged output format constraints (`<output_format>` blocks).

**FR-014:** The output format constraint SHALL include an explicit instruction that the response must start immediately with `---`, a negative instruction prohibiting introductory text before frontmatter, and a format template showing expected first lines.

**FR-015:** The output format constraint SHALL be placed at the end of each prompt (leveraging LLM recency bias).

**FR-016:** `build_extract_prompt()` SHALL request all 13+ frontmatter fields defined in the source protocol template (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`), including: `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`.

**FR-017:** The extract gate (`EXTRACT_GATE`) in `src/superclaude/cli/roadmap/gates.py` SHALL be updated to require the expanded field set of 13+ fields.

**FR-018:** Fields that the LLM cannot reliably produce (e.g., `pipeline_diagnostics`) SHALL be populated by the executor after subprocess completion, not requested from the LLM.

**FR-019:** The extract prompt body SHALL request structured extraction sections: functional requirements (FR-NNN IDs), non-functional requirements (NFR-NNN IDs), complexity assessment with scoring rationale, architectural constraints, risk inventory, dependency inventory, success criteria, and open questions.

**FR-020:** (Implicit) The `_FRONTMATTER_PATTERN` regex SHALL be compiled as a module-level constant for reuse across calls, matching the reference implementation pattern `r'^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$'`.

## Non-Functional Requirements

**NFR-001:** Gate fix SHALL not break any existing gate validations for other pipeline commands that share `_check_frontmatter`.

**NFR-002:** Gate fix SHALL be backward-compatible — files that currently pass validation SHALL continue to pass.

**NFR-003:** Sanitizer SHALL handle files up to 10MB without excessive memory usage.

**NFR-004:** Sanitizer SHALL preserve file encoding (UTF-8) through the atomic rewrite.

**NFR-005:** Prompt hardening SHALL not increase prompt token count by more than 200 tokens per prompt function.

**NFR-006:** Protocol parity changes SHALL not break the `generate` step prompts that consume extraction output.

## Complexity Assessment

**Score: 0.72** | **Class: moderate**

**Scoring rationale:**
- **Scope breadth (+0.15):** Changes span 4 files across 2 package subdirectories (`pipeline/` and `roadmap/`), touching gate logic, executor flow, and prompt construction.
- **Regex correctness (+0.15):** The frontmatter regex must correctly distinguish YAML frontmatter from markdown horizontal rules — a nuanced pattern-matching problem with false-positive risk.
- **Cross-component impact (+0.15):** `_check_frontmatter()` is shared across all pipeline commands; changes must be backward-compatible.
- **Protocol alignment (+0.12):** Expanding the extract prompt to 13+ fields and updating downstream consumers (generate step) requires coordinated multi-file changes.
- **Atomic I/O (+0.08):** The sanitizer requires atomic file rewrite semantics to prevent data loss.
- **LLM behavioral dependency (+0.07):** Prompt hardening effectiveness depends on LLM compliance, which is inherently probabilistic — hence the defense-in-depth approach.

The spec is well-scoped with reference implementations, clear phasing, and defense-in-depth redundancy that reduces implementation risk below what the raw file count would suggest.

## Architectural Constraints

1. **Gate function is shared infrastructure:** `_check_frontmatter()` in `pipeline/gates.py` is used by all 8 pipeline steps and potentially other pipeline commands. Changes must be strictly backward-compatible.

2. **Sanitizer scoped to roadmap executor only:** The sanitizer is intentionally placed in `roadmap/executor.py`, not in the shared pipeline layer, to avoid over-broad application to non-roadmap pipelines.

3. **Sanitizer timing constraint:** `_sanitize_output()` must execute after subprocess completion and before gate validation to prevent preamble propagation via `_embed_inputs()`.

4. **Atomic file writes mandatory:** The sanitizer must use `write-to-tmp + os.replace` pattern; in-place rewrite is not acceptable due to partial-write risk.

5. **Prompt format constraint placement:** XML output format blocks must be placed at the end of prompts to leverage LLM recency bias.

6. **Executor-populated fields:** Some frontmatter fields (e.g., `pipeline_diagnostics`) must be injected by the executor post-subprocess, not requested from the LLM.

7. **Python version compatibility:** Uses `list[str]` and `str | None` type hints (Python 3.10+), consistent with `pyproject.toml` requirement.

## Risk Inventory

1. **Regex false positive — horizontal rule matched as frontmatter** | Severity: **high** | Probability: low | Mitigation: Regex requires at least one `key: value` line between `---` delimiters.

2. **Sanitizer strips valid content before frontmatter** | Severity: **high** | Probability: low | Mitigation: Only strips before first `^---$` line; atomic rewrite preserves original on failure.

3. **Prompt hardening insufficient — LLM still adds preamble** | Severity: **low** | Probability: medium | Mitigation: P1 gate fix and P2 sanitizer provide defense-in-depth; prompt hardening is additive, not sole defense.

4. **Protocol parity breaks generate step** | Severity: **medium** | Probability: medium | Mitigation: Generate prompt must be updated to consume new fields; end-to-end testing required.

5. **Shared `_check_frontmatter` regression in other pipelines** | Severity: **medium** | Probability: low | Mitigation: Regex is backward-compatible; files that currently pass will continue to pass. Test coverage for existing pipelines.

## Dependency Inventory

1. **`re` module (Python stdlib):** Used for `re.MULTILINE` regex-based frontmatter discovery pattern. No external dependency.

2. **`os` module (Python stdlib):** Used for `os.replace()` atomic file rename in sanitizer.

3. **`pathlib.Path` (Python stdlib):** Used for file I/O in sanitizer (`read_text`, `write_text`, `with_suffix`).

4. **`logging` module (Python stdlib):** Used for `_log.info()` in sanitizer to report preamble stripping.

5. **Source protocol template (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`):** Defines the canonical 13+ frontmatter fields that the extract prompt and gate must align with. Protocol parity depends on this file being the source of truth.

6. **`ClaudeProcess` subprocess integration:** The sanitizer and gate operate on files produced by `ClaudeProcess` stdout capture. Behavior depends on `ClaudeProcess` not introducing additional artifacts into stdout (see `--verbose` flag follow-up investigation).

## Success Criteria

1. **Full pipeline completion:** `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes all 8 steps without frontmatter-related failures.

2. **Clean artifacts:** No preamble text present in any artifact `.md` file after pipeline completion.

3. **Protocol-complete extraction:** Extraction frontmatter contains all 13+ fields from source protocol template.

4. **Test suite green:** All unit tests pass across §6.1 (gate fix — 8 cases), §6.2 (sanitizer — 5 cases), §6.3 (prompt hardening — 3 checks), and §6.4 (protocol parity — 4 checks).

5. **No regressions:** Other pipeline commands that share `_check_frontmatter()` continue to pass validation without modification.

## Open Questions

1. **`--verbose` flag stdout interaction:** Does the `--verbose` flag on `ClaudeProcess` inject additional text into stdout that could be mistaken for LLM preamble? The spec flags this as a follow-up investigation but it could affect P2 sanitizer behavior if the preamble source is not purely LLM-generated.

2. **Other step prompt parity:** Steps beyond `extract` (generate, diff, debate, score, merge, test-strategy) may also have protocol drift vs. source templates. When will the follow-up audit occur, and should this release include a basic parity check for all steps?

3. **Gate tier differentiation:** Should STRICT-tier gates reject preamble (requiring clean output) while STANDARD gates tolerate it? The current spec applies the same tolerant regex to all tiers. This design review is deferred but could affect security-sensitive pipeline steps.

4. **`generate` step prompt update scope:** FR-016/FR-017 expand the extract step's output fields. The spec notes that `build_generate_prompt()` must be updated to consume expanded extraction, but no explicit FR covers the generate prompt changes. Is this in-scope for P4 or a separate follow-up?

5. **Sanitizer interaction with `_embed_inputs()`:** The spec states sanitizer timing prevents preamble propagation via `_embed_inputs()`. What happens if a step's input embedding occurs before sanitization due to race conditions or execution order changes?

6. **10MB file size threshold (NFR-003):** Is 10MB a realistic upper bound for pipeline artifacts? What is the observed maximum artifact size in production? If artifacts can exceed 10MB, should the sanitizer use streaming I/O instead of `read_text()`?
