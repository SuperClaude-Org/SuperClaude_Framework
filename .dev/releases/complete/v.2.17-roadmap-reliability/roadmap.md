---
spec_source: ".dev/releases/current/v.2.17-roadmap-reliability/spec-roadmap-pipeline-reliability.md"
generated: "2026-03-08T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.42
complexity_class: MEDIUM
domain_distribution:
  backend: 70
  security: 15
  performance: 10
  documentation: 5
primary_persona: backend
consulting_personas: [architect, security]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Gate Fix — Regex-Based Frontmatter Discovery"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    effort: S
    risk_level: Medium
  - id: M2
    title: "Output Sanitizer"
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 4
    effort: S
    risk_level: Medium
  - id: V1
    title: "P1+P2 Integration Validation"
    type: TEST
    priority: P3
    dependencies: [M1, M2]
    deliverable_count: 3
    effort: XS
    risk_level: Low
  - id: M3
    title: "Prompt Hardening"
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 3
    effort: S
    risk_level: Low
  - id: M4
    title: "Extract Step Protocol Parity"
    type: FEATURE
    priority: P1
    dependencies: [M1, M3]
    deliverable_count: 4
    effort: M
    risk_level: Medium
  - id: V2
    title: "End-to-End Pipeline Validation"
    type: TEST
    priority: P3
    dependencies: [M1, M2, M3, M4, V1]
    deliverable_count: 3
    effort: S
    risk_level: Low
total_deliverables: 21
total_risks: 7
estimated_phases: 5
validation_score: 0.92
validation_status: PASS
---

# Roadmap: Roadmap Pipeline Reliability

## Overview

This roadmap addresses a critical pipeline reliability issue where the `superclaude roadmap run` command halts at the extract step due to strict YAML frontmatter parsing. The root cause is a `_check_frontmatter()` function that requires `---` at byte 0, rejecting valid extraction output that contains conversational preamble from Claude's subprocess.

The fix follows a defense-in-depth strategy across 4 priorities: P1 makes the gate tolerant of preamble (regex-based discovery), P2 sanitizes output before gates run, P3 reduces preamble frequency via prompt hardening, and P4 aligns the CLI extract prompt with the source protocol's field expectations. All 8 pipeline steps share the same gate code, so the compound reliability improvement affects the entire pipeline.

The roadmap is structured as 4 work milestones with 2 interleaved validation milestones (1:2 ratio per MEDIUM complexity class). P1 and P2 are independent but share a validation gate. P3 is independent of P2. P4 depends on P1 (tolerant gate needed for expanded field validation) and P3 (prompt structure must support expanded fields).

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Gate Fix — Regex-Based Frontmatter Discovery | FEATURE | P0 | S | None | 4 | Medium |
| M2 | Output Sanitizer | FEATURE | P1 | S | M1 | 4 | Medium |
| V1 | P1+P2 Integration Validation | TEST | P3 | XS | M1, M2 | 3 | Low |
| M3 | Prompt Hardening | FEATURE | P1 | S | M1 | 3 | Low |
| M4 | Extract Step Protocol Parity | FEATURE | P1 | M | M1, M3 | 4 | Medium |
| V2 | End-to-End Pipeline Validation | TEST | P3 | S | M1, M2, M3, M4, V1 | 3 | Low |

## Dependency Graph

```
M1 → M2 → V1
M1 → M3 → M4 → V2
M1 → M4
V1 → V2
```

---

## M1: Gate Fix — Regex-Based Frontmatter Discovery

### Objective

Replace the strict byte-0 `_check_frontmatter()` implementation with a regex-based search that discovers YAML frontmatter anywhere in the document while distinguishing valid frontmatter from markdown horizontal rules.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Replace `_check_frontmatter()` in `pipeline/gates.py` with regex using `re.MULTILINE` pattern `^---` anchored to line beginnings | Function discovers frontmatter preceded by preamble text; returns `(True, None)` for valid frontmatter at any position |
| D1.2 | Regex requires at least one `key: value` line between `---` delimiters | Horizontal rules (`---` with no key:value content) are rejected; valid frontmatter blocks are accepted |
| D1.3 | Validate all `required_fields` from the discovered frontmatter block | Missing required fields return `(False, "Missing required frontmatter field '<field>' in <output_file>")` |
| D1.4 | Unit tests covering 8 test cases from spec §6.1 | All test cases pass: preamble, clean, horizontal rule, missing FM, missing field, multiple blocks, whitespace, empty file |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-001: Regex false positive — horizontal rule matched as frontmatter | Low | High | Regex requires `key: value` lines between delimiters (FR-002) |
| RISK-005: Shared `_check_frontmatter` breaks other pipelines | Low | Medium | Backward-compatible: files currently passing continue to pass (NFR-002); regression tests |

---

## M2: Output Sanitizer

### Objective

Add a `_sanitize_output()` function to `roadmap/executor.py` that strips conversational preamble from subprocess output files before gate validation, using atomic file writes to prevent partial writes.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Implement `_sanitize_output()` function in `roadmap/executor.py` | Function strips all content before first `^---` line; returns byte count of stripped preamble |
| D2.2 | Atomic write via `.tmp` + `os.replace()` pattern | No partial file state on disk during rewrite; verified via test or code review |
| D2.3 | Wire `_sanitize_output()` into `roadmap_run_step()` between subprocess completion and gate validation | Call order: subprocess → `_sanitize_output()` → `_check_frontmatter()` |
| D2.4 | Unit tests covering 5 test cases from spec §6.2 | All test cases pass: preamble present, no preamble, no frontmatter, atomic safety, multi-line preamble |

### Dependencies

- M1: Gate fix must be in place so sanitized output passes the new tolerant gate

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-002: Sanitizer strips valid content before frontmatter | Low | High | Only strips before first `^---$` line; atomic rewrite preserves original on failure |
| RISK-006: Atomic write failure on disk full or permission error | Low | Medium | `os.replace()` is atomic on POSIX; `.tmp` file left as evidence on failure |

---

## V1: P1+P2 Integration Validation

### Objective

Validate that M1 (gate fix) and M2 (output sanitizer) work together correctly — the sanitizer cleans output and the tolerant gate validates it, with no regressions to other pipeline commands.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D-V1.1 | Run existing pipeline test suite to verify zero regressions | All pre-existing pipeline tests pass without modification |
| D-V1.2 | Manual test: run `superclaude roadmap run` extract step with a spec known to produce preamble | Extract step completes; output file starts with `---` after sanitization |
| D-V1.3 | Verify sanitizer + gate interaction: inject preamble into test fixture, confirm cleaned and validated | Sanitizer strips preamble → gate validates → pipeline continues |

### Dependencies

- M1: Gate fix implementation
- M2: Output sanitizer implementation

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration mismatch between sanitizer regex and gate regex | Low | Medium | Both use same `^---` anchor pattern |

---

## M3: Prompt Hardening

### Objective

Add XML-tagged output format constraints to all 7 `build_*_prompt()` functions in `roadmap/prompts.py`, reducing the frequency of preamble in LLM subprocess output by exploiting recency bias.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Add `<output_format>` XML block to all 7 `build_*_prompt()` functions | Each function's return value contains the XML constraint block |
| D3.2 | XML block placed at end of each prompt (recency bias positioning) | `<output_format>` is the last XML block in each prompt string |
| D3.3 | Token budget validation: ≤200 tokens added per function | Measured delta for each function ≤200 tokens (NFR-005) |

### Dependencies

- M1: Gate fix must exist as fallback (prompt hardening reduces but does not eliminate preamble)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-003: Prompt hardening insufficient (LLM still adds preamble) | Medium | Low | M1 gate fix and M2 sanitizer handle residual preamble |

---

## M4: Extract Step Protocol Parity

### Objective

Align the CLI `build_extract_prompt()` with the source `sc-roadmap-protocol` by expanding the requested frontmatter fields from 3 to 13+ and updating the `EXTRACT_GATE` required fields to match.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Expand `build_extract_prompt()` to request all 13+ frontmatter fields per source protocol | Prompt requests: spec_source, generated, generator, functional_requirements, nonfunctional_requirements, total_requirements, complexity_score, complexity_class, domains_detected, risks_identified, dependencies_identified, success_criteria_count, extraction_mode |
| D4.2 | Update `EXTRACT_GATE` required fields to match expanded set | Gate validates all 13+ fields; missing fields fail validation |
| D4.3 | Expand prompt body to request structured extraction sections (FRs with IDs, NFRs with IDs, complexity assessment, constraints, risks, dependencies, success criteria, open questions) | Extract output body contains all 8 structured sections |
| D4.4 | Ensure `build_generate_prompt()` consumes expanded extraction output; add executor-populated fields (pipeline_diagnostics) post-subprocess | Generate step receives and uses expanded extraction; executor fills fields LLM cannot produce |

### Dependencies

- M1: Tolerant gate required to validate expanded field set (new fields may trigger false negatives with strict gate)
- M3: Prompt hardening XML structure must be in place before expanding prompt content

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-004: Protocol parity breaks generate step | Medium | Medium | D4.4 explicitly updates generate prompt; end-to-end test in V2 validates |
| NFR-006 violation: downstream consumer breakage | Low | Medium | Generate prompt updated in same milestone; integration tested |

---

## V2: End-to-End Pipeline Validation

### Objective

Validate the complete pipeline by running `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` end-to-end, verifying all 8 steps complete with clean artifacts and expanded frontmatter.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D-V2.1 | Full pipeline run completes all 8 steps without errors | Exit code 0, all 8 step outputs generated |
| D-V2.2 | All artifact `.md` files start with `---` (no preamble) | `head -1` of every artifact is `---` |
| D-V2.3 | Extraction frontmatter contains all 13+ fields from source protocol | YAML parse of extraction.md frontmatter contains all required fields |

### Dependencies

- M1, M2, M3, M4, V1: All work and validation milestones complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| End-to-end failure from unforeseen interaction | Low | Medium | Individual milestones each have unit tests; V2 catches integration issues |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Regex false positive — horizontal rule matched as frontmatter | M1 | Low | High | Regex requires key:value lines between delimiters (FR-002) | backend |
| R-002 | Sanitizer strips valid content before frontmatter | M2 | Low | High | Only strips before first `^---$` line; atomic rewrite preserves original | backend |
| R-003 | Prompt hardening insufficient — LLM still adds preamble | M3 | Medium | Low | M1 gate fix and M2 sanitizer as fallback layers | backend |
| R-004 | Protocol parity breaks generate step | M4 | Medium | Medium | Generate prompt updated in M4 (D4.4); validated in V2 | backend |
| R-005 | Shared `_check_frontmatter` affects other pipelines | M1 | Low | Medium | Backward-compatible regex; regression tests in V1 | backend |
| R-006 | Atomic write failure on disk full or permission error | M2 | Low | Medium | `os.replace()` atomic on POSIX; `.tmp` file as recovery evidence | backend |
| R-007 | Regex performance degradation on large files (10MB) | M1 | Low | Low | `re.MULTILINE` with bounded pattern; NFR-003 validated | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend (confidence: 0.54) | architect (0.46), security (0.12) | Backend domain at 70% of requirements |
| Template | Inline generation (Tier 4) | No templates found in Tiers 1-3 | No `.dev/templates/roadmap/` directory exists |
| Milestone Count | 6 (4 work + 2 validation) | Range 5-7 (MEDIUM class) | base=5 + floor(2 domains / 2) = 6 |
| Adversarial Mode | None | N/A | No `--specs`, `--multi-roadmap`, or `--agents` flags |
| Interleave Ratio | 1:2 | 1:1 (HIGH), 1:3 (LOW) | MEDIUM complexity class → 1:2 |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes all 8 steps | V2 | Yes |
| SC-002 | No preamble text in any artifact `.md` file after pipeline completion | M2, M3, V2 | Yes |
| SC-003 | Extraction frontmatter contains all 13+ fields from source protocol | M4, V2 | Yes |
| SC-004 | All unit tests pass (§6.1 through §6.4) | M1, M2, M3, M4 | Yes |
| SC-005 | No regressions in other pipeline commands sharing `_check_frontmatter()` | M1, V1 | Yes |
