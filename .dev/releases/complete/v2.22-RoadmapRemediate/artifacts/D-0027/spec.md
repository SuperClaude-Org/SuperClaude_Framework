# D-0027: Outcome Routing + No-Loop Enforcement

## Task: T05.04 | Roadmap Items: R-035, R-038

### Deliverable
Outcome router mapping certification results to state updates with explicit no-loop enforcement.

### Implementation
- **File**: `src/superclaude/cli/roadmap/certify_prompts.py`
- Function: `route_certification_outcome(results) -> dict`
- All-pass path: `status="certified"`, `tasklist_ready=True`
- Some-fail path: `status="certified-with-caveats"`, `tasklist_ready=False`, failure list
- `loop=False` enforced in all paths (NFR-012)

### Verification
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "outcome or routing"` exits 0 (7 tests pass)
