# D-0002: `--file` Argument Format Documentation

## Task: T01.02 -- Check `claude --help` for `--file` format

**Date**: 2026-03-15

## Finding

### Help Text (verbatim)
```
--file <specs...>   File resources to download at startup.
                    Format: file_id:relative_path
                    (e.g., --file file_abc:doc.txt file_def:img.png)
```

### Format Analysis

| Aspect | Detail |
|--------|--------|
| Format required | `file_id:relative_path` (prefix required) |
| Plain path accepted? | **NO** — requires `file_id:` prefix |
| Purpose | Download file resources at startup |
| Multiple files | Space-separated specs |
| Example | `--file file_abc:doc.txt file_def:img.png` |

### Critical Interpretation

The `--file` flag is designed for **downloading file resources** (likely from the Anthropic API/cloud storage), NOT for passing local filesystem paths to the model context. This means:

1. `claude --file /tmp/file-test.md` — would likely **fail or be misinterpreted** (no `file_id:` prefix)
2. The flag expects pre-uploaded file IDs, not local paths
3. This is fundamentally different from what the tasklist T01.03 assumes

### Implications for T01.03

The empirical test as designed (`claude --print -p "What is the secret answer?" --file /tmp/file-test.md`) would need to be adjusted. The `--file` flag cannot be used to pass arbitrary local file content to the model.

**Alternative approaches for passing file content**:
- Pipe file content via stdin: `cat file.md | claude --print -p "question"`
- Use the `--system-prompt` flag with file content
- Use the prompt itself to include file content

### OQ-5 Resolution

This addresses OQ-5 from the roadmap. The `--file` flag requires `file_id:relative_path` format — it is NOT a mechanism for passing local file content to the CLI. Any fallback remediation (Phase 5) must account for this — `--file` is not the correct mechanism for local file injection.

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `claude --help` output captured | PASS | Full help text captured |
| `--file` section identified | PASS | See verbatim excerpt above |
| Format requirement documented | PASS | `file_id:relative_path` prefix required |
| Finding addresses OQ-5 | PASS | Documented above |
