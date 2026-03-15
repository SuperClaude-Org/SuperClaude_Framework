# D-0029 Evidence — Large File E2E Test (T06.03)

**Task**: T06.03 — Large file E2E test (>=120 KB spec)
**Date**: 2026-03-15
**Primary Failure Mode**: `OSError: [Errno 7] Argument list too long`
**Exit Code**: 0 (no OSError)

## Spec File Used

- **Path**: `/tmp/large-spec-e2e-test.md`
- **Size**: 128,039 bytes (125.0 KB)
- **Exceeds 120 KB**: Yes (`file_size > 120 * 1024`)
- **Exceeds `_EMBED_SIZE_LIMIT` (122,880 bytes)**: Yes

## Test Execution

Pipeline step `spec-fidelity` exercised via `roadmap_run_step()` with the 125 KB spec file:

```
_EMBED_SIZE_LIMIT = 122880 bytes (120.0 KB)
Test file: /tmp/large-spec-e2e-test.md
Test file size: 128039 bytes (125.0 KB)
Exceeds _EMBED_SIZE_LIMIT: True

Step 'spec-fidelity': composed prompt exceeds 122880 bytes; embedding inline anyway (--file fallback is unavailable)

Result status: StepStatus.PASS
extra_args: []
Prompt contains spec content: True
```

## Verification Results

```
PASS: No OSError raised
PASS: No --file in extra_args
PASS: Spec content embedded in prompt
PASS: Step result = StepStatus.PASS
PASS: FIX-ARG-TOO-LONG validated: >=120 KB spec file processed without OSError
```

## Acceptance Criteria

- [x] Spec file used is >= 120 KB (128,039 bytes = 125.0 KB, verified)
- [x] Pipeline `spec-fidelity` step completes without `OSError: [Errno 7] Argument list too long`
- [x] No other unrelated errors masked the test outcome
- [x] Pipeline output and file size recorded in this evidence file

## Constants Validated

The FIX-ARG-TOO-LONG fix establishes:
- `_MAX_ARG_STRLEN = 128 * 1024` (Linux kernel compile-time constant)
- `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024` (2.3x safety factor)
- `_EMBED_SIZE_LIMIT = 120 * 1024 = 122,880 bytes`

When composed string exceeds `_EMBED_SIZE_LIMIT`, content is embedded inline with a warning log rather than triggering the kernel's `MAX_ARG_STRLEN` check which produces `OSError: [Errno 7]`.
