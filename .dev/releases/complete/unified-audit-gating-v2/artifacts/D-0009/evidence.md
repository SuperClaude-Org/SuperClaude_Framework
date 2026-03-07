# D-0009 Evidence: execute-sprint.sh help text "default: 100"

## Change
- **File**: `.dev/releases/execute-sprint.sh`
- **Line**: 14
- **Before**: `#   --max-turns N    Max agent turns per phase (default: 50)`
- **After**: `#   --max-turns N    Max agent turns per phase (default: 100)`

## Verification
```
$ grep -n 'default:' .dev/releases/execute-sprint.sh
12:#   --start N        Start from phase N (default: 1)
14:#   --max-turns N    Max agent turns per phase (default: 100)
```

No "default: 50" remains in the file.
