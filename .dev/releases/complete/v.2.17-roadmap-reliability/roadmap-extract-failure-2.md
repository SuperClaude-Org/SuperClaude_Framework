# Final Root Cause Analysis Report
## `superclaude roadmap run` — Extract Step Gate Failure

**Date:** 2026-03-07  
**Pipeline:** `superclaude roadmap run`  
**Failing Step:** `extract` (Step 1 of 8)  
**Error:** `YAML frontmatter missing or unparseable in extraction.md: no opening ---`  
**Severity:** Pipeline-Halting — Blocks all downstream steps  

---

## Executive Summary

The `superclaude roadmap run` pipeline halts at the first step (`extract`) because Claude's subprocess output contains a conversational preamble line ("Now I have the full spec. Let me produce the extraction document.") before the YAML frontmatter block. The gate validation function (`_check_frontmatter`) requires `---` as the absolute first non-whitespace content and has zero tolerance for any preceding text.

**The content is valid.** All required frontmatter fields are present, 190 lines of correct extraction were produced, and the complexity analysis is accurate. The pipeline rejects valid work due to a single line of preamble.

**This is a compound failure** involving three layers:
1. **Gate validation is brittle** — zero tolerance for preamble (primary)
2. **No post-processing** between raw subprocess output and artifact file
3. **Prompt doesn't sufficiently constrain** output format

---

## Root Cause Chain

```
┌─────────────────────────────────────────────────────────┐
│  Claude LLM produces conversational preamble (1 line)   │  ← Contributing Factor
│  before YAML frontmatter, despite prompt instruction     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  ClaudeProcess captures raw stdout → extraction.md       │  ← Enabler
│  output_format="text", no post-processing, no filtering  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  _check_frontmatter() fails: content.lstrip() does not   │  ← Direct Cause
│  startswith("---") because of preamble text               │
│  → Returns False → StepStatus.FAIL → Pipeline halts      │
└─────────────────────────────────────────────────────────┘
```

---

## Recommended Fix Strategy

### Priority 1: Gate Fix (IMMEDIATE — unblocks pipeline)

**Solution: Regex-based frontmatter discovery in `_check_frontmatter()`**

Replace the position-based `startswith("---")` check with a regex search that locates the first valid YAML frontmatter block in the content.

**File:** `src/superclaude/cli/pipeline/gates.py`  
**Function:** `_check_frontmatter()`  
**Effort:** 1-2 hours  
**Risk:** Low  

```python
import re

_FRONTMATTER_PATTERN = re.compile(
    r'^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$',
    re.MULTILINE
)

def _check_frontmatter(content, required_fields, output_file):
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

**Why this regex is safe against horizontal rules:**
The regex requires at least one `word: value` line between the `---` delimiters (`(?:[ \t]*\w[\w\s]*:.*\n)+`). A bare `---` horizontal rule followed by prose text won't match this pattern.

---

### Priority 2: Output Sanitizer (NEAR-TERM — clean artifacts)

**Solution: Post-processing function in the roadmap executor**

After subprocess completion and before gate validation, strip any preamble text before the first frontmatter block. Rewrite the artifact file with clean content.

**File:** `src/superclaude/cli/roadmap/executor.py`  
**Function:** New `_sanitize_output()`  
**Effort:** 2-3 hours  
**Risk:** Low-Medium  

```python
def _sanitize_output(output_file: Path) -> int:
    """Strip preamble before YAML frontmatter. Returns bytes stripped."""
    content = output_file.read_text(encoding="utf-8")
    if content.lstrip().startswith("---"):
        return 0  # No preamble

    match = re.search(r'^---[ \t]*$', content, re.MULTILINE)
    if match is None:
        return 0  # No frontmatter at all

    preamble = content[:match.start()]
    cleaned = content[match.start():]

    # Atomic rewrite
    tmp = output_file.with_suffix(".tmp")
    tmp.write_text(cleaned, encoding="utf-8")
    os.replace(str(tmp), str(output_file))

    _log.info("Stripped %d-byte preamble from %s", len(preamble.encode()), output_file)
    return len(preamble.encode())
```

**Why this matters beyond the gate:** Even with a tolerant gate, the preamble stays in the artifact. When the `generate` steps embed `extraction.md` in their prompts via `_embed_inputs()`, they include the preamble text. Cleaning the artifact prevents preamble propagation.

---

### Priority 3: Prompt Hardening (DEFENSE-IN-DEPTH — reduce frequency)

**Solution: XML-tagged format anchoring in all prompt builders**

Add explicit format constraints with XML tags, negative examples, and format templates to all 7 prompt functions.

**File:** `src/superclaude/cli/roadmap/prompts.py`  
**Functions:** All 7 `build_*_prompt()` functions  
**Effort:** 1-2 hours  
**Risk:** Low  

Key additions to each prompt:
```
<output_format>
CRITICAL: Your response must start IMMEDIATELY with the YAML frontmatter block.
Do NOT include any introductory text, thinking, or commentary before the frontmatter.
The very first characters of your response must be: ---
</output_format>
```

---

## Impact Analysis

### Steps Affected
| Step | Gate Tier | Frontmatter Required | Affected? |
|------|-----------|---------------------|-----------|
| extract | STANDARD | Yes (3 fields) | ✅ Yes |
| generate-A | STRICT | Yes (3 fields) + semantic | ✅ Yes |
| generate-B | STRICT | Yes (3 fields) + semantic | ✅ Yes |
| diff | STANDARD | Yes (2 fields) | ✅ Yes |
| debate | STRICT | Yes (2 fields) + semantic | ✅ Yes |
| score | STANDARD | Yes (2 fields) | ✅ Yes |
| merge | STRICT | Yes (3 fields) + semantic | ✅ Yes |
| test-strategy | STANDARD | Yes (2 fields) | ✅ Yes |

**All 8 steps** share the same `_check_frontmatter()` code path. The fix addresses the entire pipeline, not just the extract step.

### Compound Reliability Improvement
With a conservatively estimated 10% preamble rate per step:
- **Before fix:** P(all 8 pass) = 0.9⁸ = 43% end-to-end success
- **After gate fix:** P(all 8 pass) = 100% (gate tolerates preamble)
- **After gate + sanitizer:** 100% success AND clean artifacts
- **After all three fixes:** 100% success, clean artifacts, reduced preamble frequency

---

## Artifacts Produced by This Analysis

| File | Description |
|------|-------------|
| `rca-context.md` | Full technical context document |
| `theory-A-llm-output.md` | Theory: LLM output behavior |
| `theory-B-gate-design.md` | Theory: Gate parsing brittleness |
| `theory-C-process-arch.md` | Theory: Process architecture |
| `debate-theories.md` | Adversarial debate ranking theories |
| `solutions-rc1-gate.md` | 3 solutions for gate design |
| `solutions-rc2-process.md` | 3 solutions for process architecture |
| `solutions-rc3-prompt.md` | 3 solutions for prompt engineering |
| `debate-solutions.md` | Adversarial debate on all solutions |
| `final-report.md` | This document |

---

## Recommended Implementation Order

```
Phase 1 (IMMEDIATE, 1-2h):
  └─ Fix _check_frontmatter() in pipeline/gates.py
     └─ Regex-based frontmatter discovery
     └─ Unit tests for: preamble, no preamble, horizontal rules, missing frontmatter

Phase 2 (SAME SESSION, 2-3h):
  └─ Add _sanitize_output() to roadmap/executor.py
     └─ Call after subprocess completion, before gate validation
     └─ Test: preamble stripping, atomic rewrite, no-preamble passthrough

Phase 3 (NEXT SESSION, 1-2h):
  └─ Harden all 7 prompts in roadmap/prompts.py
     └─ XML format tags + negative instructions
     └─ Test: verify reduced preamble frequency (manual run)

Phase 4 (VALIDATION):
  └─ Re-run: superclaude roadmap run <spec-file> --depth deep --agents opus:architect,haiku:analyzer
  └─ Verify all 8 steps complete successfully
  └─ Verify artifacts are clean (no preamble in any .md file)
```

---

## Decision for Human Review

**Do you want to proceed with implementation?** The recommended approach is:

1. **Gate fix** (Priority 1) — Unblocks the pipeline immediately
2. **Output sanitizer** (Priority 2) — Ensures clean downstream artifacts  
3. **Prompt hardening** (Priority 3) — Reduces preamble frequency as defense-in-depth

All three are complementary and independently valuable. The gate fix alone resolves the immediate failure. The full set creates a robust, defense-in-depth pipeline.
