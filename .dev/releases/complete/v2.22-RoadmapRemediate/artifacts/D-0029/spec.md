# D-0029: Certify Step Registration

## Task: T05.06 | Roadmap Item: R-037

### Deliverable
Certify step registration in `_build_steps()` with `CERTIFY_GATE`, executed via `execute_pipeline([certify_step])`.

### Implementation
- **File**: `src/superclaude/cli/roadmap/executor.py`
- `build_certify_step(config, findings, context_sections) -> Step` builds standard Step
- Step id: "certify", gate: CERTIFY_GATE, output_file: certification-report.md
- Registered as standard Step (not ClaudeProcess) per spec §2.5
- `_get_all_step_ids()` updated to include "certify"
- CERTIFY_GATE import added to executor

### Verification
- `uv run python -c "from superclaude.cli.roadmap.executor import build_certify_step"` succeeds
- `uv run pytest tests/roadmap/ -k "certify and registration"` exits 0
