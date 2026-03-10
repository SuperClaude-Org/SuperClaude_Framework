# D-0024: Certification Prompt Builder

## Task: T05.01 | Roadmap Item: R-032

### Deliverable
`certify_prompts.py` module with `build_certification_prompt(findings, context_sections) -> str` per spec §2.4.2 template.

### Implementation
- **File**: `src/superclaude/cli/roadmap/certify_prompts.py`
- **Function**: `build_certification_prompt(findings: list[Finding], context_sections: dict[str, str]) -> str`
- Pure function (no I/O, no subprocess per NFR-004)
- Prompt includes: skeptical header, per-finding verification checklist (original issue, fix applied, check instruction), output format (PASS/FAIL per finding with justification)
- Accepts pre-extracted context sections, not full file content (NFR-011)

### Verification
- `uv run pytest tests/roadmap/test_certify_prompts.py` exits 0 (11 tests pass)
