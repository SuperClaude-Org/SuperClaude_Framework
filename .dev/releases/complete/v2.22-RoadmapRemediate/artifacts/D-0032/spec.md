# D-0032: Stale Hash Detection (SHA-256 Comparison)

## Overview

On `--resume`, the remediate step verifies that `source_report_hash` in
`remediation-tasklist.md` matches the SHA-256 of the current validation report.

## Logic

```
_check_tasklist_hash_current(tasklist_file, output_dir):
    1. Parse YAML frontmatter from tasklist_file
    2. Read source_report_hash field
    3. Locate validation report via source_report field (or default paths)
    4. Compute hashlib.sha256(report_content).hexdigest()
    5. Compare: match → True (skip ok), mismatch → False (re-run)
```

## Failure Semantics

- Hash mismatch → re-run remediate from scratch (fail closed)
- Missing tasklist → re-run (no output to check)
- Missing validation report → re-run (can't verify)
- Missing frontmatter → re-run (can't extract hash)

## Consistency with T03.04

`generate_remediation_tasklist()` computes the same hash:
`hashlib.sha256(source_report_content.encode("utf-8")).hexdigest()`

`_check_tasklist_hash_current()` computes:
`hashlib.sha256(report_path.read_bytes()).hexdigest()`

Both use SHA-256 on the same content, producing identical hashes.

## Implementation

- `_check_tasklist_hash_current()` in executor.py (internal function)
- Called from `check_remediate_resume()`
