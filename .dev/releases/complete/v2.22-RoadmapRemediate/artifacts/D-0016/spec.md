# D-0016: Pre-Remediate File Snapshots

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Function
`create_snapshots(target_files: list[str]) -> list[str]`

## Snapshot Mechanism
- Naming convention: `<filename>.pre-remediate`
- Atomic copy: read -> tmp write -> os.replace() per NFR-005
- Returns list of snapshot paths for rollback reference
- Raises FileNotFoundError if target file missing

## Supporting Functions
- `restore_from_snapshots(target_files)`: os.replace() from snapshot -> original
- `cleanup_snapshots(target_files)`: unlink snapshot files after success
