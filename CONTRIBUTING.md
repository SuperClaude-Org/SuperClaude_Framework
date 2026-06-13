# Contributing to SuperClaude

v5 inverts the burden of proof: a component ships only if it beats *native*
Claude Code behavior. That single rule shapes how contributions are reviewed.
Read the [thesis in the README](README.md) and the
[RFC](docs/rfc/v5-slim-down.md) before proposing anything.

## Ways to contribute

### Bug reports

Open a GitHub issue with:

- SuperClaude version (`superclaude version`), Claude Code version (`claude --version`), OS, Python version (`python3 --version`)
- Exact steps to reproduce, expected vs. actual behavior, and any error output
- A minimal reproduction if you can produce one

### Proposing a skill, agent, hook, or command — the eval gate

New components are **not** added on intuition. The bar is a pre-registered A/B
eval against native Claude Code:

1. Build a single-component variant under `eval/variants/<comp>/` (see
   [eval/README.md](eval/README.md)).
2. Run it: `cd eval && uv run sc-eval --trials 5 --k 3` (smoke). Real decisions
   need ≥20 tasks per [eval/preregister.yaml](eval/preregister.yaml).
3. It survives only if both pre-registered rules hold: disjoint 95% CIs above
   the native baseline **and** no quality-per-token regression.
4. Attach the numbers to your PR. Overlapping CIs are inconclusive, not a win.

PRs that add components without eval results will be redirected to the harness
first. Never tune `eval/preregister.yaml` to make a candidate pass.

### Documentation and best practices

Evidence-based write-ups on Claude Code-era development go to
[docs/knowledge/](docs/knowledge/README.md). Corrections to the
[migration guide](docs/migration/v4-to-v5.md) are welcome. Keep docs lean —
every line a reader pays for should earn its place.

## Development

Setup, layout, and the full command list live in [CLAUDE.md](CLAUDE.md). The
essentials:

```bash
uv pip install -e ".[dev]"     # editable install
make test                      # uv run python -m pytest (257 collected)
make lint                      # ruff check
make format                    # ruff format
make doctor                    # installation health check
make build-plugin              # assemble dist/ plugin artefacts
```

All Python goes through **UV** — never bare `python`, `pip install`, or the
`pytest` console script.

### Workflow

1. Branch from `v5` (active development branch; PRs target `v5`, not `master`).
2. Implement with tests. New behavior needs a test that fails before and passes after.
3. `make test && make lint` must be green.
4. Use [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:`).
5. Open a PR with a clear description; for new components, include eval numbers.

`master` carries the frozen v4.3.x line (security fixes only) — do not target it.

## Community

Be respectful and keep discussion on technical merit. Assume positive intent,
give specific and actionable feedback, and support evidence over opinion.
General questions and workflow sharing go to
[GitHub Discussions](https://github.com/SuperClaude-Org/SuperClaude_Framework/discussions);
bugs and proposals go to Issues.

## License

By contributing you agree your work is licensed under the project's
[MIT License](LICENSE). Only contribute code that is your own or properly
attributed, and keep third-party dependencies MIT-compatible.
