# D-0026: synthesize-spec Step Implementation

## Deliverable

`synthesize_spec` step implementation in `src/superclaude/cli/cli_portify/steps/synthesize_spec.py`.

## Implementation

The step:
1. Verifies `release-spec-template.md` exists (fail-fast per Recommendation #5)
2. Loads analysis and design artifacts as @path inputs
3. Executes via `PortifyProcess` with retry loop for sentinel resolution
4. Runs SC-003 sentinel scan: regex `\{\{SC_PLACEHOLDER:[^}]+\}\}` on output
5. On sentinel scan failure: retries with specific remaining placeholder names
6. Runs SC-005 STRICT gate: zero remaining sentinels

## Files

- `src/superclaude/cli/cli_portify/steps/synthesize_spec.py` (implementation)
- `tests/cli_portify/test_synthesize_spec.py` (9 tests)

## Gate: SC-005 (STRICT)

- Required frontmatter: step, source_skill, cli_name, synthesis_version, placeholder_count
- Zero `{{SC_PLACEHOLDER:*}}` sentinels remaining
- Minimum 15 lines

## Verification

`uv run python3 -m pytest tests/cli_portify/test_synthesize_spec.py -v` exits 0 (9/9 passed)
