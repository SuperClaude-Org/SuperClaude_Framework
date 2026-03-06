# D-0004 Evidence: Evidence-Gated Rules

## Test Results (10/10 passed)
- TestDeleteEvidenceGate: delete_with_evidence_passes, delete_without_evidence_fails, non_delete_always_passes, referenced_file_rejected_as_delete
- TestKeepEvidenceGate: keep_with_evidence_passes, keep_without_evidence_fails
- TestCombinedEvidenceGate: valid_delete_passes, invalid_delete_rejected, valid_keep_passes, gate_result_serialization

## AC Verification
- [x] AC4: No DELETE without zero-reference evidence
- [x] AC5: KEEP requires reference evidence for tier-1/tier-2
- [x] Referenced file rejected as DELETE (test_referenced_file_rejected_as_delete)
