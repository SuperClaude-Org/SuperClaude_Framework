# AC Traceability Report — v2.24.2 Accept-Spec-Change

All 14 acceptance criteria mapped to automated test functions. All tests pass (65/65).

## AC Traceability Matrix

| AC | Description | Test Function(s) | File | Status |
|----|-------------|-------------------|------|--------|
| AC-1 | No deviation files exits 1 | `TestScanDeviationRecords::test_no_deviation_files_exits_1` | test_accept_spec_change.py | PASS |
| AC-2 | Only spec_hash changes, all keys preserved | `TestAtomicWrite::test_only_spec_hash_changes`, `TestStateIntegrity::test_only_spec_hash_changes_in_auto_resume` | test_accept_spec_change.py, test_spec_patch_cycle.py | PASS |
| AC-3 | Run twice, second exits 0 (idempotent) | `TestIdempotency::test_second_run_idempotent`, `TestCLIIntegration::test_cli_happy_path_idempotent` | test_accept_spec_change.py | PASS |
| AC-4 | Answer N, mtime unchanged | `TestPromptBehavior::test_answer_n_aborts`, `TestStateIntegrity::test_cli_abort_n_preserves_mtime` | test_accept_spec_change.py, test_spec_patch_cycle.py | PASS |
| AC-5a | CLI exit codes correct | `TestCLIIntegration::test_cli_help_shows_usage`, `test_cli_missing_directory_exits_nonzero`, `test_cli_missing_state_file_exits_1`, `test_cli_hash_current_exits_0`, `test_cli_no_deviation_files_exits_1`, `test_cli_happy_path_with_input_y`, `test_cli_happy_path_idempotent` | test_accept_spec_change.py | PASS |
| AC-5b | Executor auto-resume skips upstream | `TestAutoAccept::test_auto_accept_true_skips_prompt`, `TestCycleGuard::test_cycle_allowed_when_count_0`, `TestDiskReread::test_post_write_state_has_new_hash` | test_spec_patch_cycle.py | PASS |
| AC-6 | Cycle fires at most once | `TestCycleGuard::test_cycle_blocked_when_count_ge_1`, `TestLogging::test_cycle_guard_preserves_state_mtime` | test_spec_patch_cycle.py | PASS |
| AC-7 | Disk-reread state used for resume | `TestDiskReread::test_post_write_state_has_new_hash`, `TestStateIntegrity::test_disk_reread_passed_to_apply_resume` | test_spec_patch_cycle.py | PASS |
| AC-8 | Persistent failure exits 1 | `TestCycleExhaustion::test_resumed_failure_exits_via_sys_exit` | test_spec_patch_cycle.py | PASS |
| AC-9 | auto_accept skips prompt | `TestAutoAccept::test_auto_accept_true_skips_prompt`, `TestPromptBehavior::test_auto_accept_skips_prompt` | test_spec_patch_cycle.py, test_accept_spec_change.py | PASS |
| AC-10 | Backward compatible signature | `TestBackwardCompat::test_signature_backward_compatible` | test_spec_patch_cycle.py | PASS |
| AC-11 | Non-interactive aborts | `TestPromptBehavior::test_non_interactive_aborts` | test_accept_spec_change.py | PASS |
| AC-12 | Logging with [roadmap] prefix | `TestLogging::test_cycle_entry_logging`, `TestLogging::test_suppression_logging` | test_spec_patch_cycle.py | PASS |
| AC-13 | Write failure aborts cycle | `TestWriteFailure::test_write_failure_aborts_cycle`, `test_write_failure_logs_to_stderr`, `test_write_failure_preserves_state_mtime`, `test_write_failure_preserves_all_state_keys` | test_spec_patch_cycle.py | PASS |
| AC-14 | Malformed YAML skipped | `TestScanDeviationRecords::test_malformed_yaml_skipped` | test_accept_spec_change.py | PASS |

## Coverage Summary

- **Total AC items**: 14
- **AC items with automated tests**: 14
- **Unmapped AC items**: 0
- **Test suite result**: 65 passed in 1.10s

## Verification Command

```bash
uv run pytest tests/roadmap/test_accept_spec_change.py tests/roadmap/test_spec_patch_cycle.py -v --tb=short
```
