# Knowledge Hub

Community best practices for Claude Code-era development. Curated, not crowdsourced:
every entry must be backed by **eval results or verifiable evidence** (official docs,
reproducible measurements, first-party experience reports with specifics). Opinions
and vibes are out of scope — that is the same bar the framework itself is held to
(see [eval/README.md](../../eval/README.md)).

## Entries

| Entry | What it covers |
|---|---|
| [claude-md-principles.md](claude-md-principles.md) | Four coding principles for LLM-driven development, as a copy-paste-able CLAUDE.md section |
| [runtime-workflow.md](runtime-workflow.md) | Match your dev runtime to your deploy runtime; per-workload Docker decisions |

Related: a minimal starter CLAUDE.md embedding the principles lives at
[docs/Templates/CLAUDE.template.md](../Templates/CLAUDE.template.md).

## Contributing an entry

1. Open a PR adding one Markdown file to this directory and a row to the table above.
2. State the claim, then the evidence. Acceptable evidence:
   - citations to official documentation (link the exact page),
   - reproducible measurements (include the commands and numbers),
   - adapted external work (include attribution and what you changed).
3. Keep entries practical: something a reader can apply to their repo today.

## Proposing a skill / agent / hook

Knowledge entries describe practice; framework components enforce it. If your
entry implies "this should be a skill", the bar is higher:

1. Build a single-component variant under `eval/variants/<comp>/`.
2. Run the harness (`cd eval && uv run sc-eval`) against the native baseline.
3. Attach results meeting the pre-registered survive rule in
   [eval/preregister.yaml](../../eval/preregister.yaml) — disjoint CIs above
   baseline, no quality-per-token regression — to the PR.

Inconclusive results are not a yes. See [eval/README.md](../../eval/README.md)
for the task format and how arms are discovered.
