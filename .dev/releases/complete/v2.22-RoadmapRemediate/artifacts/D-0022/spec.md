# D-0022: Tasklist Outcome Writer (Two-Write Model)

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Function
`update_remediation_tasklist(tasklist_path: str, findings: list[Finding]) -> None`

## Two-Write Model
- First write: T03.04 `generate_remediation_tasklist()` creates initial tasklist with PENDING status
- Second write: This function updates with final outcomes (FIXED/FAILED/SKIPPED)

## Update Logic
- FIXED: `- [ ]` -> `- [x]`, status -> FIXED
- FAILED: keep `- [ ]`, status -> FAILED
- SKIPPED: unchanged (already `- [x]` SKIPPED from T03.04)
- Frontmatter counts updated to reflect final states

## NFR Compliance
- NFR-005: Atomic write (tmp + os.replace)
- SC-007: Round-trip consistency (parse -> update -> re-parse)
