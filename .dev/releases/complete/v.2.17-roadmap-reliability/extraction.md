---
spec_source: "spec-roadmap-pipeline-reliability.md"
generated: "2026-03-08T00:00:00Z"
generator: "claude-opus-4-6-requirements-extractor"
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
---

## Functional Requirements

**FR-001:** `_check_frontmatter()` in `src/superclaude/cli/pipeline/gates.py` SHALL locate YAML frontmatter anywhere in the document, not only at byte 0. Uses regex search instead of startswith to tolerate LLM preamble.

**FR-002:** The frontmatter regex SHALL require at least one `key: value` line between `---` delimiters to distinguish valid frontmatter from markdown horizontal rules.

**FR-003:** The function SHALL extract and validate all `required_fields` from the discovered frontmatter block, iterating over field names and checking presence in parsed keys.

**FR-004:** The function SHALL return `(False, reason)` when no valid frontmatter block is found anywhere in the content, or when any required field is absent from the discovered frontmatter.

**FR-005:** The function SHALL return `(True, None)` when a valid frontmatter block is found and all required fields are present.

**FR-006:** The regex pattern SHALL use `re.MULTILINE` to anchor `^---` to line beginnings, not just document start, enabling discovery at any position in the file.

**FR-010:** A new function `_sanitize_output()` SHALL be added to `src/superclaude/cli/roadmap/executor.py` to strip LLM conversational preamble from artifact files.

**FR-011:** `_sanitize_output()` SHALL strip all content before the first YAML frontmatter block (`^---` on a line by itself) from the artifact file.

**FR-012:** If the file already starts with `---` (after whitespace stripping), the function SHALL return 0 and make no changes, avoiding unnecessary file rewrites.

**FR-013:** If no frontmatter block is found at all, the function SHALL return 0 and make no changes, leaving non-frontmatter files untouched.

**FR-014:** File rewrite SHALL use atomic write (write to `.tmp`, then `os.replace`) to prevent partial writes that could corrupt artifacts mid-pipeline.

**FR-015:** The function SHALL log the number of preamble bytes stripped, providing observability into preamble frequency and size.

**FR-016:** `roadmap_run_step()` SHALL call `_sanitize_output()` after subprocess completion and before gate validation, ensuring clean artifacts enter the gate check.

**FR-020:** All 7 `build_*_prompt()` functions in `src/superclaude/cli/roadmap/prompts.py` SHALL include XML-tagged output format constraints (`<output_format>` blocks).

**FR-021:** The output format constraint SHALL include: explicit instruction that the response must start immediately with `---`, negative instruction prohibiting introductory text/thinking/commentary before frontmatter, and a format template showing expected first lines.

**FR-022:** The constraint SHALL be placed at the end of each prompt to exploit LLM recency bias for better compliance.

**FR-030:** `build_extract_prompt()` SHALL request all frontmatter fields defined in the source protocol template (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`), expanding from 3 fields to 13+.

**FR-031:** The required frontmatter fields SHALL include (at minimum): `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`.

**FR-032:** The extract gate (`EXTRACT_GATE`) in `src/superclaude/cli/roadmap/gates.py` SHALL be updated to require the expanded field set, aligning gate validation with protocol expectations.

**FR-033:** Fields that the LLM cannot reliably produce (e.g., `pipeline_diagnostics`) SHALL be populated by the executor after subprocess completion, not requested from the LLM. This separates LLM-generated content from pipeline-generated metadata.

**FR-034:** The extract prompt body SHALL request structured extraction sections matching the source protocol: functional requirements with IDs (FR-NNN), non-functional requirements with IDs (NFR-NNN), complexity assessment with scoring rationale, architectural constraints, risk inventory, dependency inventory, success criteria, and open questions.

## Non-Functional Requirements

**NFR-001:** Gate fix SHALL not break any existing gate validations for other pipeline commands that share `_check_frontmatter`. Backward compatibility is mandatory since the function is shared infrastructure.

**NFR-002:** Gate fix SHALL be backward-compatible — files that currently pass validation SHALL continue to pass. The regex-based approach is a strict superset of the current startswith check.

**NFR-003:** Sanitizer SHALL handle files up to 10MB without excessive memory usage. Pipeline artifacts are typically small but edge cases (large specs) must not cause OOM.

**NFR-004:** Sanitizer SHALL preserve file encoding (UTF-8) through the atomic rewrite. No encoding corruption during the tmp-write-and-replace cycle.

**NFR-005:** Prompt hardening SHALL not increase prompt token count by more than 200 tokens per prompt function. The `<output_format>` XML block must be compact.

**NFR-006:** Protocol parity changes SHALL not break the `generate` step prompts that consume extraction output. The generate step must be updated to consume newly available fields.

## Complexity Assessment

**Complexity Score: 0.72** — **Complexity Class: moderate**

**Scoring Rationale:**

- **Scope breadth (0.15/0.20):** 4 files affected across 3 modules (pipeline/gates, roadmap/executor, roadmap/prompts, roadmap/gates). Moderate cross-module impact but within a single subsystem.
- **Integration risk (0.15/0.20):** `_check_frontmatter()` is shared infrastructure used by all pipeline commands. Changes must be backward-compatible. The sanitizer introduces a new processing step in the execution flow.
- **LLM interaction complexity (0.12/0.20):** Prompt hardening relies on LLM behavioral compliance which is inherently probabilistic. Defense-in-depth strategy (gate tolerance + sanitizer + prompt hardening) mitigates this.
- **Protocol alignment (0.15/0.20):** Expanding from 3 to 13+ frontmatter fields requires coordinated changes across prompt, gate, and downstream consumer (generate step).
- **Testing complexity (0.15/0.20):** 4 test suites covering gate behavior, file I/O atomicity, prompt structure validation, and end-to-end pipeline runs. The E2E test requires LLM subprocess execution.

**Complexity reducers:** Reference implementations provided for P1 and P2. Clear 5-phase implementation order. Well-defined test matrices.

## Architectural Constraints

1. **Shared gate infrastructure:** `_check_frontmatter()` in `pipeline/gates.py` is shared across all pipeline commands (not just roadmap). Any change must maintain backward compatibility for non-roadmap pipelines.

2. **Sanitizer scoping:** The output sanitizer is scoped to `roadmap/executor.py` (not shared pipeline level). This is a deliberate design decision — pipeline-level sanitization is too broad and could mask issues in other pipelines.

3. **Sanitizer timing:** Must execute after subprocess completion and before gate validation. This ordering is critical for the defense-in-depth strategy.

4. **Atomic file writes:** File rewrites must use write-to-tmp + `os.replace` pattern. No in-place file mutation during sanitization.

5. **Prompt placement:** Output format constraints must be placed at the end of each prompt function (recency bias optimization for LLMs).

6. **LLM vs executor field responsibility:** Fields that LLMs cannot reliably produce (e.g., `pipeline_diagnostics`) must be populated by the executor, not requested from the LLM. Clear separation of LLM-generated vs pipeline-generated metadata.

7. **Protocol parity scope:** Only the `extract` step is aligned with source protocol in this release. Other steps (generate, diff, debate, score, merge, test-strategy) are deferred to follow-up audit.

8. **Python version:** Uses `tuple[bool, str | None]` type hints and `list[str]` syntax, requiring Python 3.10+.

## Risk Inventory

**RISK-001: Regex false positive on horizontal rules** — Severity: **high** — Probability: low
The regex could match a markdown horizontal rule (`---`) as frontmatter. Mitigation: regex requires at least one `key: value` line between `---` delimiters, which horizontal rules lack.

**RISK-002: Sanitizer strips valid pre-frontmatter content** — Severity: **high** — Probability: low
If a file intentionally has content before frontmatter, the sanitizer would strip it. Mitigation: only strips before the first `^---$` line; atomic rewrite preserves original on failure; current pipeline artifacts never have intentional pre-frontmatter content.

**RISK-003: Prompt hardening insufficient** — Severity: **low** — Probability: medium
LLMs may still add preamble despite XML format constraints. Mitigation: P1 gate fix and P2 sanitizer handle this case as fallback layers. Prompt hardening reduces frequency but is not relied upon as sole defense.

**RISK-004: Protocol parity breaks generate step** — Severity: **medium** — Probability: medium
Expanding extraction frontmatter from 3 to 13+ fields requires the generate step prompt to consume the new fields. If `build_generate_prompt()` is not updated, new fields are wasted. Mitigation: test end-to-end; update generate prompt to reference new fields.

**RISK-005: Shared `_check_frontmatter` regression** — Severity: **medium** — Probability: low
Other pipeline commands using the same gate function could be affected. Mitigation: regex-based search is a strict superset of startswith — files that currently pass will continue to pass. Regression tests against existing pipelines.

## Dependency Inventory

1. **Python `re` module** — Standard library regex module. Used for `_FRONTMATTER_PATTERN` compilation with `re.MULTILINE` flag. No external dependency.

2. **Python `os` module** — Standard library. Used for `os.replace()` in atomic file writes. No external dependency.

3. **Python `pathlib.Path`** — Standard library. Used for file read/write operations in `_sanitize_output()`. No external dependency.

4. **`ClaudeProcess` subprocess wrapper** — Internal dependency (`src/superclaude/cli/`). The sanitizer runs after `ClaudeProcess` completes. Must not interfere with subprocess stdout capture.

5. **Source protocol templates** — `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`. FR-030 requires field alignment with this file. If templates change, extract prompt must be updated.

6. **`_embed_inputs()` pipeline function** — Internal dependency. Downstream pipeline steps embed previous step outputs. Sanitized artifacts must be clean before this embedding occurs, which the timing constraint (FR-016) ensures.

## Success Criteria

1. **SC-001: Full pipeline completion** — `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes all 8 steps without halting. Acceptance: 0 step failures.

2. **SC-002: Clean artifacts** — No preamble text in any artifact `.md` file after pipeline completion. Acceptance: all artifacts start with `---` as first non-whitespace content.

3. **SC-003: Protocol-compliant extraction** — Extraction frontmatter contains all 13+ fields from source protocol. Acceptance: all fields present with valid values.

4. **SC-004: Unit test coverage** — All unit tests pass for gate fix (§6.1), sanitizer (§6.2), prompt hardening (§6.3), and protocol parity (§6.4). Acceptance: 100% pass rate.

5. **SC-005: No regressions** — No regressions in other pipeline commands that share `_check_frontmatter()`. Acceptance: existing test suites pass unchanged.

## Open Questions

1. **`--verbose` flag stdout interaction:** Does the `--verbose` flag on `ClaudeProcess` inject text into stdout that could be captured as artifact content? The spec assumes preamble is LLM conversational text, but verbose logging could be a contributing factor. Requires investigation against `ClaudeProcess` implementation.

2. **Other step prompt parity:** Steps beyond `extract` (generate, diff, debate, score, merge, test-strategy) may also have protocol drift relative to source protocol templates. Should all steps be audited for field parity in this release or deferred? Spec defers this but it represents latent risk.

3. **Gate tier differentiation:** Should STRICT-tier gate steps reject preamble (requiring clean output) while STANDARD-tier gates tolerate it? The current spec applies uniform tolerance across all tiers. This may be too lenient for security-critical or high-assurance steps.

4. **Generate step prompt update scope:** FR-034 expands extraction output from 3 to 13+ fields. The spec notes that `build_generate_prompt()` must consume these new fields, but does not specify which fields the generate step should use or how. This requires design clarification.

5. **Sanitizer idempotency under concurrent access:** If multiple pipeline steps or parallel runs write to the same artifact directory, could the sanitizer's tmp-file-and-replace pattern conflict? The spec assumes sequential step execution but does not explicitly constrain this.

6. **`extraction_mode` field values:** The spec lists `single | multi | adversarial` as valid values for `extraction_mode`, but the source protocol template in `templates.md` may use different values (e.g., `full | partial | incremental`). The canonical value set needs confirmation against the source protocol.
