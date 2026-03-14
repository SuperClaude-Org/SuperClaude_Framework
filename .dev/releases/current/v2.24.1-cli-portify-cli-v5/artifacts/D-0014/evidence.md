# D-0014: resolve_target() Core Evidence

- Function exists in src/superclaude/cli/cli_portify/resolution.py
- Accepts target: str | None parameter
- Guards verified:
  - resolve_target(None) raises ResolutionError(ERR_TARGET_NOT_FOUND)
  - resolve_target("") raises ResolutionError(ERR_TARGET_NOT_FOUND)
  - resolve_target("   ") raises ResolutionError(ERR_TARGET_NOT_FOUND)
  - resolve_target("sc:") raises ResolutionError(ERR_TARGET_NOT_FOUND)
  - resolve_target("sc:   ") raises ResolutionError(ERR_TARGET_NOT_FOUND)
- Uses time.monotonic() for timing
- Classification for all 6 forms implemented
- 533 tests pass (no regression)
