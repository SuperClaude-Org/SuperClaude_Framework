# D-0025: Certification Context Extractor

## Task: T05.02 | Roadmap Item: R-033

### Deliverable
Context extractor: `extract_finding_context(file_content: str, finding: Finding) -> str`

### Implementation
- **File**: `src/superclaude/cli/roadmap/certify_prompts.py`
- Handles §-references and line-range references
- Extracts heading + content through next same-level heading
- Token cost proportional to section size, not file size (NFR-011)

### Verification
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "context"` exits 0 (7 tests pass)
