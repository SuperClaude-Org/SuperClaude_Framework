# D-0015: File-Level Grouping and Cross-File Finding Handler

## Module
`src/superclaude/cli/roadmap/remediate_prompts.py`

## Functions
- `group_findings_by_file(findings: list[Finding]) -> dict[str, list[Finding]]`
- `build_cross_file_fragment(finding: Finding, target_file: str) -> str`

## Grouping Logic
- Primary target = first entry in `files_affected`
- Cross-file findings appear in ALL relevant file groups
- No concurrent same-file groups (each file = one group key)
- No orphaned findings (every finding in at least one group)

## Cross-File Scoping
- Per-agent prompt fragment: "Fix Guidance (YOUR FILE): ..."
- Note field: "The <other_file> side is handled by a separate agent."

## NFR Compliance
- NFR-004: Both functions are pure (no I/O, no side effects)
