# D-0012 Evidence: roadmap CLI help text "Default: 100"

## Change
- **File**: `src/superclaude/cli/roadmap/commands.py`
- **Line**: 76
- **Before**: `help="Max agent turns per claude subprocess. Default: 50.",`
- **After**: `help="Max agent turns per claude subprocess. Default: 100.",`

## Verification
```
$ grep -n 'Default:' src/superclaude/cli/roadmap/commands.py
38:        "Default: opus:architect,haiku:architect"
46:    help="Output directory for all artifacts. Default: parent dir of spec-file.",
52:    help="Debate round depth: quick=1, standard=2, deep=3. Default: standard.",
70:    help="Override model for all steps. Default: per-agent model for generate steps.",
76:    help="Max agent turns per claude subprocess. Default: 100.",
```

No "Default: 50" remains in the file.
