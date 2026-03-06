# D-0043 Evidence: ALREADY_TRACKED Report Section

## Test Results
```
7 passed in 0.02s
```

## Section Sample (markdown)
```markdown
## Already Tracked

| Finding Path | Registry Entry ID | Matched Pattern | Classification |
|---|---|---|---|
| src/legacy/old.py | KI-001 | src/legacy/*.py | DELETE |
| src/legacy/dead.py | KI-001 | src/legacy/*.py | DELETE |
```

## Section Sample (dict, when present)
```json
{
  "already_tracked": [
    {"file_path": "src/legacy/old.py", "classification": "DELETE", "matched": true, "registry_entry_id": "KI-001", "matched_pattern": "src/legacy/*.py"}
  ],
  "already_tracked_count": 1
}
```

## Section absent (dict, when no matches)
```json
{}
```
