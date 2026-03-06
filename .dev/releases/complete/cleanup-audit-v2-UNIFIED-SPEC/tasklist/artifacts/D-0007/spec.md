# D-0007 Spec: Gitignore Inconsistency Detection

## Module
`src/superclaude/cli/audit/gitignore_checker.py`

## Output Format
```json
{
  "inconsistencies": [{"file_path": "str", "matching_pattern": "str"}],
  "tracked_file_count": "int",
  "gitignore_pattern_count": "int",
  "inconsistency_count": "int"
}
```

## Pattern Matching
Handles: filename match, full path match, ** wildcards, directory prefix (trailing /).
