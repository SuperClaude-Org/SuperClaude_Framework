# D-0041 Evidence: Known-Issues Registry

## Test Results
```
12 passed in 0.03s
```

## Registry Match Test Log
- Matching pattern `src/legacy/*.py` + classification `DELETE` against `src/legacy/old.py` -> SUPPRESSED (KI-001)
- Non-matching path `src/core/new.py` -> NOT SUPPRESSED
- Non-matching classification `KEEP` -> NOT SUPPRESSED
- Empty classification matches any classification -> SUPPRESSED
- `last_matched` updated to current timestamp on match
- Persistence: save -> load -> match -> save -> reload preserves all fields
