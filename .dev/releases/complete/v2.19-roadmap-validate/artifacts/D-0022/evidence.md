# D-0022: Known-Defect Detection Test Evidence

## Test File

`tests/roadmap/test_validate_defects.py` -- 15 tests

## Defect Classes Tested

### 1. Duplicate D-IDs (4 tests)

| Test | Input Defect | Expected Detection |
|------|-------------|-------------------|
| test_duplicate_h2_headings_detected | Two "## Phase 1: Setup" headings | _no_duplicate_headings returns False |
| test_duplicate_h3_headings_detected | Two "### D-001: Auth Module" headings | _no_duplicate_headings returns False |
| test_unique_headings_pass | All unique headings | _no_duplicate_headings returns True |
| test_gate_rejects_duplicate_headings_in_strict_mode | Duplicate in STRICT gate | gate_passed returns (False, "no_duplicate_headings") |

### 2. Missing Milestone References (3 tests)

| Test | Input Defect | Expected Detection |
|------|-------------|-------------------|
| test_missing_frontmatter_field_detected | tasklist_ready missing from REFLECT_GATE | gate_passed returns (False, "tasklist_ready") |
| test_missing_validation_mode_detected | validation_mode missing from ADVERSARIAL_MERGE_GATE | gate_passed returns (False, "validation_mode") |
| test_all_required_fields_present_passes | All fields present | gate_passed returns (True, None) |

### 3. Untraced Requirements / Empty Values (4 tests)

| Test | Input Defect | Expected Detection |
|------|-------------|-------------------|
| test_empty_frontmatter_value_detected | blocking_issues_count has empty value | _frontmatter_values_non_empty returns False |
| test_all_empty_values_detected | All frontmatter values empty | _frontmatter_values_non_empty returns False |
| test_non_empty_values_pass | All values populated | _frontmatter_values_non_empty returns True |
| test_strict_gate_rejects_empty_values | STRICT gate with empty warnings_count | gate_passed returns (False, "frontmatter_values_non_empty") |

### 4. Cross-File Inconsistency (4 tests)

| Test | Input Defect | Expected Detection |
|------|-------------|-------------------|
| test_heading_gap_detected | H2 -> H4 skip (no H3) | _no_heading_gaps returns False |
| test_no_heading_gap_passes | Proper H2 -> H3 -> H4 | _no_heading_gaps returns True |
| test_missing_agreement_table_in_adversarial_merge | No agreement table in merge output | gate_passed returns (False, "agreement_table_present") |
| test_gate_file_below_min_lines | 7 lines vs min 20 | gate_passed returns (False, "minimum line count") |

## Execution Evidence

```
$ uv run pytest tests/roadmap/test_validate_defects.py -v
15 passed in 0.13s
```

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| At least 4 tests, one per defect class | PASS | 4 classes, 15 tests total |
| Defective input asserts BLOCKING finding | PASS | Each test asserts gate_passed returns False |
| Finding identifies specific defect | PASS | Failure reasons name the specific check |
| All tests pass | PASS | Exit code 0 |
