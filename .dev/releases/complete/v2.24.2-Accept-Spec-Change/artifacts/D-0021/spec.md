# D-0021: CLI Help Text for accept-spec-change

## Location

Click command docstring at `src/superclaude/cli/roadmap/commands.py:155-176`

## Content (verified via `--help`)

```
Usage: roadmap accept-spec-change [OPTIONS] OUTPUT_DIR

  Update spec_hash after accepted deviation records.

  When the spec file is edited to formalize an accepted deviation (documentation
  sync, not a functional change), this command updates the stored spec_hash so
  --resume can proceed without a full cascade.

  Requires at least one dev-*-accepted-deviation.md file with disposition:
  ACCEPTED and spec_update_required: true as evidence.

  Note: .roadmap-state.json requires exclusive write access during execution. Do
  not run concurrent roadmap operations on the same output directory.

  OUTPUT_DIR is the directory containing .roadmap-state.json.

  Examples:     superclaude roadmap accept-spec-change ./output

Options:
  --help  Show this message and exit.
```

## Verification

```bash
uv run python -c "from superclaude.cli.roadmap.commands import roadmap_group; from click.testing import CliRunner; print(CliRunner().invoke(roadmap_group, ['accept-spec-change', '--help']).output)"
```
