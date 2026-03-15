# D-0003: Empirical `--file` Test Results

## Task: T01.03 -- Execute empirical `--file` test

**Date**: 2026-03-15

## Test Setup

```bash
$ echo "The secret answer is PINEAPPLE." > /tmp/file-test.md
$ cat /tmp/file-test.md
The secret answer is PINEAPPLE.
```

## Test Execution

### Command
```bash
$ timeout 15 claude --print -p "What is the secret answer?" --file /tmp/file-test.md
```

### Output (verbatim)
```
Error: Session token required for file downloads. CLAUDE_CODE_SESSION_ACCESS_TOKEN must be set.
EXIT_CODE=1
```

## Analysis

The `--file` flag **does not accept local filesystem paths**. When given `/tmp/file-test.md`:

1. The CLI interprets it as a file download spec (per `--help`: "File resources to download at startup")
2. It attempts to use `CLAUDE_CODE_SESSION_ACCESS_TOKEN` for authentication
3. Since no session token is set, it fails with exit code 1
4. The response does **not** mention PINEAPPLE — the file content was never delivered to the model

### Result Classification per T01.04 Categories

- Exit code: **1** (non-zero)
- Response mentions PINEAPPLE: **NO**
- Category: **CLI FAILURE** (non-zero exit code)

However, this is NOT a "CLI is broken" failure — it's a "the flag doesn't work the way the spec assumed" failure. The CLI itself is functional (T01.01 confirmed). The `--file` flag is architecturally designed for cloud file downloads, not local file injection.

### Root Cause

The `--file` flag in Claude CLI v2.1.76 is a **cloud file resource download mechanism**, not a local file path injector. The spec's assumption that `--file /path/to/file` would deliver file content to the model context was incorrect.

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `/tmp/file-test.md` created with PINEAPPLE content | PASS | File created and verified |
| Command executed and output captured | PASS | Error message and exit code captured |
| Exit code recorded | PASS | Exit code 1 |
| Full response text recorded verbatim | PASS | Error message above |
| Result recorded in D-0003 | PASS | This file |
