# D-0001: --pipeline Flag Detection Stub (step_0 Guard)

## Overview

The `--pipeline` flag detection stub is a step_0 guard inserted **before** the existing Mode A/B parsing logic in the `input_mode_parsing` section of `SKILL.md`. It gates all pipeline mode logic by checking for the `--pipeline` flag first, routing to the Meta-Orchestrator section when present, and falling through to existing Mode A/B behavior when absent.

## Guard Logic

```
step_0_pipeline_guard:
  IF --pipeline flag is present:
    1. Set pipeline_mode = true
    2. Skip step_1 through step_4 (Mode A/B parsing not applicable)
    3. Route to "Meta-Orchestrator: Pipeline Mode" section
  IF --pipeline flag is absent:
    1. Set pipeline_mode = false
    2. Proceed to step_1_detect_mode (existing behavior unchanged)
  CONFLICT:
    IF --pipeline is present alongside --compare or --source/--generate/--agents:
      STOP with error: 'Cannot use --pipeline with --compare or
      --source/--generate/--agents. Pipeline mode defines its own phases.'
```

## Modifications Made

| File | Section | Change |
|------|---------|--------|
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | Required Input (line ~26) | Added `--pipeline` as third input mode option with usage examples |
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | Configurable Parameters table (line ~265) | Added `--pipeline` row to flags table |
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | Input Mode Parsing Protocol (line ~444) | Inserted `step_0_pipeline_guard` before `step_1_detect_mode`; added `condition: "pipeline_mode == false"` to step_1 |
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | step_1_detect_mode neither clause (line ~465) | Updated error message to mention `--pipeline` as third option |
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | End of file (line ~1786) | Added "Meta-Orchestrator: Pipeline Mode" placeholder section with implementation comment referencing M2/M4 |

## Backward Compatibility

- **Mode A without `--pipeline`**: Unchanged. step_0 sets `pipeline_mode = false`, step_1 processes `--compare` as before.
- **Mode B without `--pipeline`**: Unchanged. step_0 sets `pipeline_mode = false`, step_1 processes `--source`+`--generate`+`--agents` as before.
- **No mode flags**: Error message updated to include `--pipeline` option but behavior (STOP with error) is unchanged.
- **`--pipeline` + `--compare`**: New error — explicit conflict detection prevents ambiguous invocation.

## Routing Diagram

```
User invocation
  │
  ▼
step_0_pipeline_guard
  │
  ├── --pipeline present? ──YES──▶ Meta-Orchestrator section (stub, impl in M2/M4)
  │
  └── --pipeline absent? ──YES──▶ step_1_detect_mode (existing Mode A/B logic)
                                    │
                                    ├── --compare? ──▶ Mode A
                                    ├── --source+--generate+--agents? ──▶ Mode B
                                    └── neither? ──▶ STOP with error
```

## Deliverable Status

- **Task**: T01.01
- **Roadmap Item**: R-001
- **Status**: COMPLETE
- **Tier**: STRICT
