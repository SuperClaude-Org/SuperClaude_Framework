---
title: "Roadmap Pipeline Reliability — Gate Tolerance, Output Sanitization, Prompt Hardening, and Protocol Parity"
version: "1.0.0"
status: draft
feature_id: FR-051
parent_feature: roadmap-pipeline
complexity_score: 0.72
complexity_class: moderate
target_release: v2.18
authors: [user, claude]
created: 2026-03-07
source: "Adversarial merge of roadmap-extract-failure-context.md and roadmap-extract-failure-2.md"
---

# FR-051: Roadmap Pipeline Reliability

## 1. Problem Statement

The `superclaude roadmap run` pipeline halts at step 1 (`extract`) with:

```
YAML frontmatter missing or unparseable in extraction.md: no opening ---
```

**Root cause chain:**
1. Claude's subprocess output contains conversational preamble before YAML frontmatter
2. `ClaudeProcess` captures raw stdout directly to disk with no post-processing
3. `_check_frontmatter()` requires `---` as the absolute first non-whitespace content

The content is valid — all required frontmatter fields are present and the extraction is correct. The pipeline rejects valid work due to a single line of preamble.

**Compound impact:** All 8 pipeline steps share the same `_check_frontmatter()` code path. With even a 5% preamble rate per step, P(all 8 pass) = 0.95^8 = 66%. At 10%, P = 43%.

**Secondary issue discovered:** The CLI extract prompt requests only 3 frontmatter fields while the source `sc-roadmap-protocol` expects 13+ fields. Even after the preamble fix, extraction artifacts will be structurally incomplete relative to the source protocol.

## 2. Solution Overview

Four-priority defense-in-depth strategy addressing both immediate pipeline failures and structural protocol drift.

| Priority | Fix | File(s) | Effort | Risk | Impact |
|----------|-----|---------|--------|------|--------|
| P1 | Regex-based frontmatter discovery | `pipeline/gates.py` | 1-2h | Low | Unblocks all 8 steps |
| P2 | Output sanitizer | `roadmap/executor.py` | 2-3h | Low-Med | Clean downstream artifacts |
| P3 | Prompt hardening | `roadmap/prompts.py` | 1-2h | Low | Reduces preamble frequency |
| P4 | Protocol parity | `roadmap/prompts.py` + `roadmap/gates.py` | 3-4h | Medium | Source protocol alignment |

### 2.1 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gate fix approach | Regex search, not startswith | Tolerates preamble while requiring valid frontmatter structure |
| Sanitizer scope | Roadmap executor, not shared pipeline | Pipeline-level is too broad; roadmap-specific preamble patterns |
| Sanitizer timing | After subprocess, before gate | Clean artifact on disk prevents preamble propagation via `_embed_inputs()` |
| Prompt hardening method | XML-tagged output format constraints | Structured format anchoring is more effective than prose instructions |
| Protocol parity scope | Extract step only (this release) | Other steps to be audited in follow-up |

## 3. Functional Requirements

### 3.1 P1: Gate Fix — Regex-Based Frontmatter Discovery

**FR-001:** `_check_frontmatter()` in `src/superclaude/cli/pipeline/gates.py` SHALL locate YAML frontmatter anywhere in the document, not only at byte 0.

**FR-002:** The frontmatter regex SHALL require at least one `key: value` line between `---` delimiters to distinguish frontmatter from markdown horizontal rules.

**FR-003:** The function SHALL extract and validate all `required_fields` from the discovered frontmatter block.

**FR-004:** The function SHALL return `(False, reason)` when:
- No valid frontmatter block is found anywhere in the content
- Any required field is absent from the discovered frontmatter

**FR-005:** The function SHALL return `(True, None)` when a valid frontmatter block is found and all required fields are present.

**FR-006:** The regex pattern SHALL use `re.MULTILINE` to anchor `^---` to line beginnings, not just document start.

#### Reference Implementation

```python
import re

_FRONTMATTER_PATTERN = re.compile(
    r'^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$',
    re.MULTILINE
)

def _check_frontmatter(content: str, required_fields: list[str], output_file: str) -> tuple[bool, str | None]:
    match = _FRONTMATTER_PATTERN.search(content)
    if match is None:
        return False, f"YAML frontmatter not found in {output_file}"

    frontmatter_text = match.group(1)
    found_keys = set()
    for line in frontmatter_text.splitlines():
        line = line.strip()
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key:
                found_keys.add(key)

    for field in required_fields:
        if field not in found_keys:
            return False, f"Missing required frontmatter field '{field}' in {output_file}"

    return True, None
```

### 3.2 P2: Output Sanitizer

**FR-010:** A new function `_sanitize_output()` SHALL be added to `src/superclaude/cli/roadmap/executor.py`.

**FR-011:** `_sanitize_output()` SHALL strip all content before the first YAML frontmatter block (`^---` on a line by itself) from the artifact file.

**FR-012:** If the file already starts with `---` (after whitespace stripping), the function SHALL return 0 and make no changes.

**FR-013:** If no frontmatter block is found at all, the function SHALL return 0 and make no changes.

**FR-014:** File rewrite SHALL use atomic write (write to `.tmp`, then `os.replace`) to prevent partial writes.

**FR-015:** The function SHALL log the number of preamble bytes stripped.

**FR-016:** `roadmap_run_step()` SHALL call `_sanitize_output()` after subprocess completion and before gate validation.

#### Reference Implementation

```python
def _sanitize_output(output_file: Path) -> int:
    """Strip preamble before YAML frontmatter. Returns bytes stripped."""
    content = output_file.read_text(encoding="utf-8")
    if content.lstrip().startswith("---"):
        return 0

    match = re.search(r'^---[ \t]*$', content, re.MULTILINE)
    if match is None:
        return 0

    preamble = content[:match.start()]
    cleaned = content[match.start():]

    tmp = output_file.with_suffix(".tmp")
    tmp.write_text(cleaned, encoding="utf-8")
    os.replace(str(tmp), str(output_file))

    _log.info("Stripped %d-byte preamble from %s", len(preamble.encode()), output_file)
    return len(preamble.encode())
```

### 3.3 P3: Prompt Hardening

**FR-020:** All 7 `build_*_prompt()` functions in `src/superclaude/cli/roadmap/prompts.py` SHALL include XML-tagged output format constraints.

**FR-021:** The output format constraint SHALL include:
- Explicit instruction that the response must start immediately with `---`
- Negative instruction prohibiting introductory text, thinking, or commentary before frontmatter
- A format template showing the expected first lines

**FR-022:** The constraint SHALL be placed at the end of each prompt (recency bias for LLMs).

#### Template

```xml
<output_format>
CRITICAL: Your response must start IMMEDIATELY with the YAML frontmatter block.
Do NOT include any introductory text, thinking, or commentary before the frontmatter.
The very first characters of your response must be: ---

Example of CORRECT output start:
---
field_name: value
---

Example of INCORRECT output start:
Here is the document you requested.
---
</output_format>
```

### 3.4 P4: Extract Step Protocol Parity

**FR-030:** `build_extract_prompt()` SHALL request all frontmatter fields defined in the source protocol template (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`).

**FR-031:** The required frontmatter fields SHALL include (at minimum):
- `spec_source` — path to the input specification
- `generated` — ISO-8601 timestamp
- `generator` — agent identifier
- `functional_requirements` — count of functional requirements extracted
- `nonfunctional_requirements` — count of non-functional requirements extracted
- `total_requirements` — sum of functional + nonfunctional
- `complexity_score` — float 0.0-1.0
- `complexity_class` — simple | moderate | complex | enterprise
- `domains_detected` — list of detected domains
- `risks_identified` — count of risks
- `dependencies_identified` — count of dependencies
- `success_criteria_count` — count of success criteria
- `extraction_mode` — single | multi | adversarial

**FR-032:** The extract gate (`EXTRACT_GATE`) in `src/superclaude/cli/roadmap/gates.py` (or wherever step gate criteria are defined) SHALL be updated to require the expanded field set.

**FR-033:** Fields that the LLM cannot reliably produce (e.g., `pipeline_diagnostics`) SHALL be populated by the executor after subprocess completion, not requested from the LLM.

**FR-034:** The extract prompt body SHALL request structured extraction sections matching the source protocol:
- Functional requirements with IDs (FR-NNN)
- Non-functional requirements with IDs (NFR-NNN)
- Complexity assessment with scoring rationale
- Architectural constraints
- Risk inventory
- Dependency inventory
- Success criteria
- Open questions

## 4. Non-Functional Requirements

**NFR-001:** Gate fix SHALL not break any existing gate validations for other pipeline commands (if `_check_frontmatter` is shared).

**NFR-002:** Gate fix SHALL be backward-compatible — files that currently pass validation SHALL continue to pass.

**NFR-003:** Sanitizer SHALL handle files up to 10MB without excessive memory usage.

**NFR-004:** Sanitizer SHALL preserve file encoding (UTF-8) through the atomic rewrite.

**NFR-005:** Prompt hardening SHALL not increase prompt token count by more than 200 tokens per prompt function.

**NFR-006:** Protocol parity changes SHALL not break the `generate` step prompts that consume extraction output.

## 5. Affected Files

| File | Changes | Priority |
|------|---------|----------|
| `src/superclaude/cli/pipeline/gates.py` | Replace `_check_frontmatter()` implementation | P1 |
| `src/superclaude/cli/roadmap/executor.py` | Add `_sanitize_output()`, call from `roadmap_run_step()` | P2 |
| `src/superclaude/cli/roadmap/prompts.py` | Add XML output format to all 7 `build_*_prompt()` functions; expand `build_extract_prompt()` field set | P3, P4 |
| `src/superclaude/cli/roadmap/gates.py` (or gate definition location) | Update `EXTRACT_GATE` required fields | P4 |

## 6. Test Plan

### 6.1 P1: Gate Fix Tests

| Test | Input | Expected |
|------|-------|----------|
| Preamble before frontmatter | `"Preamble\n---\nkey: val\n---\nBody"` | `(True, None)` |
| Clean frontmatter at start | `"---\nkey: val\n---\nBody"` | `(True, None)` |
| Horizontal rule (no key:val) | `"---\nSome text\n---"` | `(False, "not found")` |
| Missing frontmatter entirely | `"No frontmatter here"` | `(False, "not found")` |
| Missing required field | `"---\nother: val\n---"` (requires `key`) | `(False, "Missing required")` |
| Multiple `---` blocks | `"---\nkey: val\n---\ntext\n---\nother: x\n---"` | Matches first valid block |
| Whitespace before frontmatter | `"\n\n---\nkey: val\n---"` | `(True, None)` |
| Empty file | `""` | `(False, "not found")` |

### 6.2 P2: Sanitizer Tests

| Test | Input File Content | Expected |
|------|-------------------|----------|
| Preamble present | `"Preamble\n---\nkey: val\n---"` | File rewritten starting at `---`, returns byte count |
| No preamble | `"---\nkey: val\n---\nBody"` | File unchanged, returns 0 |
| No frontmatter | `"Just text, no frontmatter"` | File unchanged, returns 0 |
| Atomic write safety | Kill process mid-write | Original or new file present, never partial |
| Multi-line preamble | `"Line 1\nLine 2\nLine 3\n---\nkey: val\n---"` | All 3 lines stripped |

### 6.3 P3: Prompt Hardening Tests

| Test | Validation |
|------|-----------|
| All 7 prompts contain `<output_format>` | Grep all `build_*_prompt` return values |
| `<output_format>` is at prompt end | Check last XML block in each prompt |
| Token budget under 200 | Measure prompt length delta |

### 6.4 P4: Protocol Parity Tests

| Test | Validation |
|------|-----------|
| Extract prompt requests all 13 fields | Parse prompt for field names |
| Extract gate requires expanded field set | Check gate criteria definition |
| Generate prompts consume expanded extraction | Verify `build_generate_prompt` references new fields |
| End-to-end pipeline completion | `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` |

## 7. Implementation Order

```
Phase 1 (P1 — IMMEDIATE):
  └─ Replace _check_frontmatter() in pipeline/gates.py
     └─ Regex-based frontmatter discovery
     └─ Unit tests (§6.1)
     └─ Verify: existing pipelines still pass

Phase 2 (P2 — SAME SESSION):
  └─ Add _sanitize_output() to roadmap/executor.py
     └─ Wire into roadmap_run_step() after subprocess, before gate
     └─ Unit tests (§6.2)

Phase 3 (P3 — SAME SESSION):
  └─ Add XML output format tags to all 7 prompts
     └─ Verify token budget (§6.3)

Phase 4 (P4 — FOLLOW-UP):
  └─ Expand build_extract_prompt() to request 13+ fields
     └─ Update EXTRACT_GATE required fields
     └─ Verify generate prompts consume expanded extraction
     └─ Unit tests (§6.4)

Phase 5 (VALIDATION):
  └─ Full pipeline run: superclaude roadmap run <spec> --depth deep
     └─ Verify all 8 steps complete
     └─ Verify artifacts are clean (no preamble)
     └─ Verify extraction has all 13+ frontmatter fields
```

## 8. Investigation Follow-ups

These items were identified during adversarial analysis but are out of scope for this release:

| Item | Description | Tracking |
|------|-------------|----------|
| `--verbose` flag interaction | Validate that `--verbose` on `ClaudeProcess` does not inject text into stdout. Current evidence suggests preamble is LLM conversational text, but the flag's interaction with stdout capture should be confirmed. | Follow-up investigation |
| Other step prompt parity | Steps beyond `extract` (generate, diff, debate, score, merge, test-strategy) may also have protocol drift. Audit all step prompts against source protocol templates. | Follow-up audit |
| Gate tier appropriateness | The regex-tolerant gate may be too lenient for STRICT-tier steps. Consider whether STRICT gates should reject preamble while STANDARD gates tolerate it. | Design review |

## 9. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Regex matches false positive (horizontal rule as frontmatter) | Low | High | Regex requires `key: value` lines between delimiters |
| Sanitizer strips valid content before frontmatter | Low | High | Only strips before first `^---$` line; atomic rewrite preserves original on failure |
| Prompt hardening insufficient (LLM still adds preamble) | Medium | Low | P1 gate fix and P2 sanitizer handle this case |
| Protocol parity breaks generate step | Medium | Medium | Generate prompt must be updated to consume new fields; test end-to-end |
| Shared `_check_frontmatter` affects other pipelines | Low | Medium | Regex is backward-compatible; files that currently pass will continue to pass |

## 10. Success Criteria

- [ ] `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes all 8 steps
- [ ] No preamble text in any artifact `.md` file after pipeline completion
- [ ] Extraction frontmatter contains all 13+ fields from source protocol
- [ ] All unit tests pass (§6.1 through §6.4)
- [ ] No regressions in other pipeline commands that share `_check_frontmatter()`
