# D-0041 Spec: Known-Issues Registry

## Task Reference
- Task: T05.02
- Roadmap Item: R-041
- AC: AC20 (supporting)

## Registry Schema

```json
{
  "entries": [
    {
      "issue_id": "KI-001",
      "pattern": "src/legacy/*.py",
      "classification": "DELETE",
      "created_date": "2026-01-01T00:00:00+00:00",
      "last_matched": "2026-03-01T00:00:00+00:00",
      "ttl_days": 90
    }
  ]
}
```

## Matching Algorithm
1. For each finding (file_path, classification):
2. Iterate registry entries
3. If classification is set, must match exactly (empty matches any)
4. File path is matched via `fnmatch` glob pattern
5. First matching entry wins (suppresses finding)
6. `last_matched` timestamp updated on match

## API
- `load_registry(path) -> KnownIssuesRegistry`
- `save_registry(registry, path)`
- `registry.match_finding(file_path, classification) -> MatchResult`
- `registry.match_findings(findings) -> (suppressed, unsuppressed)`

## Implementation
- Source: `src/superclaude/cli/audit/known_issues.py`
- Tests: `tests/audit/test_known_issues.py` (12 tests)
