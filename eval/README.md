# SuperClaude eval harness (gate-zero)

Decides what is allowed into the plugin. A candidate component is ported **only
if** an A/B against the corresponding *native* Claude Code behaviour shows it
wins beyond noise, machine-scored in containers. The verdict comes from the
numbers, never from a belief about what the native feature does.

## Model

- **Arms.** `A` = native baseline (`claude -p`, no plugin). `B_<comp>` =
  `claude -p --plugin-dir variants/<comp>` — a minimal plugin holding *one*
  candidate, so nothing else confounds the measurement.
- **Tasks** (Terminal-Bench shape): `tasks/<id>/{task.md, environment/,
  verify.sh, oracle/, meta.yaml}`. The agent only sees `environment/`;
  `verify.sh` and `oracle/` are isolated so the model cannot read the test.
- **Scoring.** Agent runs on the host in a throwaway copy of `environment/`;
  `verify.sh` runs in `meta.verify_image` with `--network none`. Exit 0 = pass.
  Machine only — no LLM judge.
- **Stats.** `pass@k` + bootstrap CIs; a candidate survives only with disjoint
  CIs above baseline and no quality-per-token regression. See `preregister.yaml`.

## Run

```bash
cd eval
uv run sc-eval --trials 5 --k 3                  # all tasks, all arms
uv run sc-eval --arms B_confidence --tasks fix-x # one candidate, one task
```

Results stream to `results/<timestamp>.jsonl`; a verdict table prints at the end.

## Task layout

```
tasks/<id>/
  task.md         # instruction (the -p prompt)
  environment/    # initial repo state the agent edits (copied per trial)
  verify.sh       # machine pass/fail, runs in container, isolated from the agent
  oracle/         # optional reference solution (sanity)
  meta.yaml       # id, source(self|swebench|terminalbench), verify_image, max_turns
```

## Adding a candidate

Create `variants/<comp>/.claude-plugin/plugin.json` plus the single skill/agent/
hook under test. The harness auto-discovers it as arm `B_<comp>`.
