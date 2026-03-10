# D-0023: Remediate Step Registration

## Module
`src/superclaude/cli/roadmap/executor.py` (step registration)
`src/superclaude/cli/roadmap/remediate_executor.py` (execution)

## Step Registration
- Step ID: "remediate"
- Gate: REMEDIATE_GATE (STRICT tier)
- Output file: remediation-tasklist.md
- Dual-nature: outer step presents to `execute_pipeline()`, inner uses `ClaudeProcess` directly

## YAML/Heading Preservation (NFR-013)
Agent prompts include:
- "Preserve YAML frontmatter structure"
- "Preserve heading hierarchy"

## Gate Reference
REMEDIATE_GATE already registered in `gates.py` (T03.05) in ALL_GATES list as ("remediate", REMEDIATE_GATE).

## Performance Notes
Steps 10-11 wall-clock overhead measurement deferred to T07.01 E2E test.
Step registration does not break existing steps 1-9 (verified by 475-test regression suite).
