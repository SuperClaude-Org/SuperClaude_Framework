# Pass 1: Surface Scan Rules

## Goal
Quickly identify obvious waste — test artifacts, runtime files committed by accident, empty placeholders, files nothing references.

## Guiding Question
**"Is this file junk?"**

## Classification Taxonomy (3-Tier)

| Category | Meaning | Action | Evidence Required |
|----------|---------|--------|-------------------|
| DELETE | No references, no value, clearly obsolete | Safe to remove | Grep proof: zero references + no dynamic loading + successor or transient confirmed |
| REVIEW | Uncertain — may be needed, needs human judgment | Escalate to human | Brief justification of uncertainty |
| KEEP | Actively referenced, part of build/runtime/CI | Leave in place | At least one active reference cited |

## Verification Protocol (4-Step)

For each file in the batch:

1. **Read**: Read first 20-30 lines to understand purpose, identify file type, check for meaningful content vs placeholder/empty
2. **Grep**: Search for filename across repo — `grep -r "filename" --exclude-dir=.git --exclude-dir=node_modules`. Record pattern used, match count, and matched files
3. **Check Imports**: Verify file is not imported/sourced/required by other files. Check for:
   - Direct imports (`import`, `require`, `from`, `source`)
   - Configuration references (`package.json`, `pyproject.toml`, `Makefile`, `docker-compose`)
   - CI/CD references (`.github/workflows/`, `Jenkinsfile`)
4. **Categorize**: Assign DELETE/REVIEW/KEEP with brief justification citing evidence from steps 1-3

## Output Format

```markdown
## Safe to Delete
- [ ] `filepath` — reason (grep: 0 references, pattern: "filename")

## Need Decision
- [ ] `filepath` — what it is, why uncertain

## Keep (verified legitimate)
- `filepath` — why needed (referenced by: file:line)

## Add to .gitignore
- `pattern` — reason (runtime artifact / cache / build output)
```

## Batch Size Guidance

| File Type | Batch Size | Rationale |
|-----------|-----------|-----------|
| Normal source/config/docs | 25-50 files | Standard read + grep per file |
| Binary/assets | 50-100 files | Grep-only, no content reading |

## Binary Asset Handling

Binary files (images, fonts, videos, compiled assets) receive grep-only audits:
- **DO**: Check if filename is referenced in code, docs, configs
- **DO NOT**: Attempt to read binary content
- **Classify**: KEEP if referenced, REVIEW if unreferenced but in expected asset directory, DELETE only if in unexpected location AND zero references

## "Zero References" Evidence Standard

Every DELETE classification must embed:
1. **Grep pattern used**: The exact command (e.g., `grep -r "filename" --exclude-dir=.git`)
2. **Match count**: Number of matches found (must be 0 for DELETE)
3. **Zero-result confirmation**: Explicit statement "0 matches found across N files searched"

**"No imports found" without a reproducible grep command is insufficient evidence for DELETE.**

## Dynamic Loading Check

Before classifying any file as DELETE, verify it is not dynamically loaded. See `rules/dynamic-use-checklist.md` for the 5 patterns to check.

## Incremental Save Protocol

1. Create output file with header template before auditing any files
2. Work in batches of 5-10 files
3. After each mini-batch, immediately save/update the output file
4. Never accumulate more than 10 unwritten results
