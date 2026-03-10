# D-0011 Evidence: roadmap CLI --max-turns default=100

## Change
- **File**: `src/superclaude/cli/roadmap/commands.py`
- **Line**: 75
- **Before**: `default=50,`
- **After**: `default=100,`

## Verification
```
$ grep -n 'default=' src/superclaude/cli/roadmap/commands.py
35:    default="opus:architect,haiku:architect",
45:    default=None,
51:    default="standard",
69:    default="",
75:    default=100,
```

The `--max-turns` Click option now defaults to 100. No other defaults were modified.
