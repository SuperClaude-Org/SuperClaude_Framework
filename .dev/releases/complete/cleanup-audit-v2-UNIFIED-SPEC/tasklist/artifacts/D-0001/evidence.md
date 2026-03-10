# D-0001 Evidence: Two-Tier Classification

## Test Results (14/14 passed)
- TestMapToV1: 7 tests (delete, investigate, keep, reorganize, archive, unmapped_raises, all_v1_covered)
- TestClassifyFinding: 6 tests (no_refs→delete, has_refs→keep, temporal→archive, test_config→keep, determinism_3_runs, evidence_preserved)
- TestSerialization: 1 test (to_dict_and_back)

## AC Verification
- [x] AC1: Valid tier-1/tier-2 labels for all input types
- [x] AC15: All 4 v1 categories mapped (test_all_v1_categories_covered)
- [x] Determinism: 3 identical runs produce identical output (test_determinism_three_runs)
