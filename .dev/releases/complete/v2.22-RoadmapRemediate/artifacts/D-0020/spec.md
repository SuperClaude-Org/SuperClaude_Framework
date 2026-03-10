# D-0020: Failure Handling with Full Rollback

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Function
`_handle_failure(failed_file, all_target_files, findings_by_file, executor) -> list[Finding]`

## Five-Step Procedure (spec section 2.3.8)
1. Halt remaining agents (executor.shutdown)
2. Rollback ALL target files from .pre-remediate snapshots (os.replace)
3. Mark all findings for failed agent as FAILED
4. Mark cross-file findings involving failed file as FAILED
5. Return findings with updated statuses (step status set to FAIL by caller)

## NFR Compliance
- NFR-005: os.replace() for atomic rollback
- Rollback is byte-identical to original (verified by tests)
