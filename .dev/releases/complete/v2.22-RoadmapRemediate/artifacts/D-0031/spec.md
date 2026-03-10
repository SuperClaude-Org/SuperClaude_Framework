# D-0031: Resume Skip Logic for Remediate and Certify Steps

## Overview

Resume skip logic for remediate and certify pipeline steps, consistent
with existing `_apply_resume()` pattern.

## Resume Conditions

### Remediate Step (`check_remediate_resume`)

Skip when ALL of:
1. `remediation-tasklist.md` exists in output_dir
2. Passes `REMEDIATE_GATE` (frontmatter + semantic checks)
3. `source_report_hash` in tasklist YAML matches SHA-256 of current validation report

Re-run when ANY condition fails (fail closed on hash mismatch).

### Certify Step (`check_certify_resume`)

Skip when ALL of:
1. `certification-report.md` exists in output_dir
2. Passes `CERTIFY_GATE` (frontmatter + semantic checks)

### Post-Certify Resume

When both remediate and certify pass their resume checks, pipeline is complete.
Resume is a no-op.

## Implementation

- `check_remediate_resume(config, gate_fn) -> bool` in executor.py
- `check_certify_resume(config, gate_fn) -> bool` in executor.py
- `_check_tasklist_hash_current(tasklist_file, output_dir) -> bool` (internal)

## Decision Model

Resume decisions are gate- and hash-based, not timestamp-only.
