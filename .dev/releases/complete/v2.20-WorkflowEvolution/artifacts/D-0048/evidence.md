---
deliverable: D-0048
task: T05.11
status: PASS
date: 2026-03-09
---

# D-0048: CLI Help Text Verification

## superclaude tasklist validate --help

```
Usage: superclaude tasklist validate [OPTIONS] OUTPUT_DIR

  Validate tasklist fidelity against a roadmap.

Options:
  --roadmap-file PATH  Path to the roadmap file. Default: {output_dir}/roadmap.md.
  --tasklist-dir PATH  Path to the tasklist directory. Default: {output_dir}/.
  --model TEXT         Override model for validation steps.
  --max-turns INTEGER  Max agent turns per claude subprocess. Default: 100.
  --debug              Enable debug logging.
  --help               Show this message and exit.
```

All options documented. Renders correctly.

## superclaude roadmap run --help

```
Usage: superclaude roadmap run [OPTIONS] SPEC_FILE

Options:
  --agents TEXT                  Comma-separated agent specs
  --output PATH                 Output directory
  --depth [quick|standard|deep] Debate round depth
  --resume                      Skip passed steps
  --dry-run                     Print plan only
  --model TEXT                  Override model
  --max-turns INTEGER           Max agent turns
  --debug                       Enable debug logging
  --no-validate                 Skip post-pipeline validation
  --retrospective PATH          Retrospective file (advisory context)
  --help                        Show this message and exit.
```

`--retrospective` flag is present and documented. All descriptions match behavior.
