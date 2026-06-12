<div align="center">

# SuperClaude v5

### What survives is what models can't do alone

<p align="center">
  <img src="https://img.shields.io/badge/version-5.0.0a1-blue" alt="Version">
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml">
    <img src="https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <a href="https://pypi.org/project/superclaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
  </a>
</p>

<p align="center">
  <a href="README.md">English</a> •
  <a href="README-zh.md">中文</a> •
  <a href="README-ja.md">日本語</a> •
  <a href="README-kr.md">한국어</a>
</p>

</div>

> Translations track v4 and will be updated after the v5 RFC.

---

## The thesis

SuperClaude v4 shipped 30 slash commands, 20 persona agents, and 7 behavioral
modes — 286KB of prompt content teaching Claude things it increasingly knows how
to do by itself. Models got better. A framework that injects instructions must
shrink as the model grows, or it becomes overhead: context cost, instruction
conflicts, degraded trigger precision.

v5 inverts the burden of proof. Every component must beat *native* Claude Code
behavior in a pre-registered A/B eval, or it gets deleted. What survives is what
models can't do alone: deterministic enforcement (hooks), external access (MCP),
persistence — plus a few structured-format skills that demonstrably hold up.

## v4 → v5 at a glance

| | v4.3.0 | v5 (5.0.0a1) |
|---|---|---|
| Slash commands | 30 | 0 — replaced by skills + native Claude Code |
| Skills | 0 | 4 |
| Persona agents | 20 | 1 |
| Behavioral modes | 7 | 0 |
| Hooks | 0 (empty directory) | 5 |
| Prompt content | 286KB | 84KB built plugin (skills 44KB, agents 4KB, hooks 4KB) |
| Eval harness | none | [eval/](eval/README.md), machine-scored A/B vs native |
| Repo side effects | pytest plugin wrote `docs/mistakes/*.md` | no file writes by default (opt-in env var) |

256 tests pass.

## What ships in v5

### Skills

Structured-format content that holds up against just asking the model.

#### confidence-check

Pre-implementation gate (duplicate check, architecture fit, official-docs
verification, root-cause identification) with a TypeScript scoring helper
(`confidence.ts`). Source: [plugins/superclaude/skills](plugins/superclaude/skills/).

#### spec-panel

Multi-expert specification review in a fixed panel format.

#### socratic

Discovery-learning dialogue with a strict question-first structure.

#### pm-reflexion

Failure reflexion: extract the root cause and a prevention rule after a real
error, instead of retrying blindly.

### Agent

#### explore-haiku

The one surviving agent. Runs codebase exploration on Haiku — cheap fan-out
search where Opus/Sonnet reasoning is wasted. The other 19 persona agents are
covered by native subagents and got cut.

### Hooks

Deterministic enforcement — the thing prompts cannot do. Defined in
[plugins/superclaude/hooks/hooks.json](plugins/superclaude/hooks/hooks.json).

#### session-restore

`SessionStart` command script that restores session context.

#### confidence-gate

`PreToolUse` prompt on `Write|Edit`: non-trivial new implementations must have
passed the confidence-check criteria first. Trivial edits are exempt.

#### session-summary

`Stop` prompt: summarize substantive sessions in 2–3 bullets (stores via
mindbase MCP if available, skips silently if not).

#### reflexion-trigger

`Stop` prompt: apply pm-reflexion when the session hit a real error.

#### tab-title

Terminal tab status (running / waiting / idle). Opt-in: silent no-op unless
`SUPERCLAUDE_TAB_TITLE=1`.

### Eval harness

[eval/](eval/README.md) is gate-zero: A/B of native Claude Code (`claude -p`)
against a minimal plugin holding exactly one candidate component. Tasks are
Terminal-Bench-shaped, verification runs in a network-isolated container,
scoring is machine-only (no LLM judge). Survive thresholds are pre-registered
in [eval/preregister.yaml](eval/preregister.yaml) before any run.

### CLI

Reduced to an install surface: `superclaude install [--minimal]`, `update`,
`doctor`, `mcp`, `install-skill`, `version`.

### Pytest plugin

Auto-loaded fixtures and markers (`confidence_checker`, `reflexion_pattern`,
`@pytest.mark.confidence_check`, ...). Unlike v4 it never writes files unless
`SUPERCLAUDE_REFLEXION_OUTPUT_DIR` is set.

## Status

5.0.0a1 is an **alpha** on the `v5` branch. The API surface above is what
exists today; the upstream proposal is in
[docs/rfc/v5-slim-down.md](docs/rfc/v5-slim-down.md).

## Installation

### Requirements

Python ≥3.10 and [Claude Code](https://code.claude.com/docs/en/overview).

### pipx (recommended)

```bash
pipx install superclaude==5.0.0a1
superclaude install
```

### Plugin directory (no Python install)

```bash
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
claude --plugin-dir SuperClaude_Framework/plugins/superclaude
```

### Minimal install

```bash
superclaude install --minimal   # confidence-check skill only, no agents
```

Incremental adoption is the recommended path — start minimal, add pieces that
earn their place ([official guidance](https://code.claude.com/docs/en/claude-code-on-the-web)
applies the same principle to all Claude Code extensions).

### Verify

```bash
superclaude doctor
```

## Upgrading from v4

```bash
pipx upgrade superclaude        # or: pipx install superclaude==5.0.0a1
superclaude install
rm -rf ~/.claude/commands/sc    # remove the 30 legacy slash commands
```

A cleanup script is provided: [scripts/uninstall_legacy.sh](scripts/uninstall_legacy.sh).

### Breaking changes

- Reflexion file output is opt-in (`SUPERCLAUDE_REFLEXION_OUTPUT_DIR`); default is no writes.
- CLI: `--target` is replaced by `--skills-dir` / `--agents-dir`.
- The pytest plugin no longer writes `docs/mistakes/*.md`.

Full guide: [docs/migration/v4-to-v5.md](docs/migration/v4-to-v5.md).

### v4 freeze policy

v4.3.x stays on PyPI, frozen — security fixes only.

### Rollback

```bash
pipx install superclaude==4.3.0
```

## The eval gate

### How a component survives

A candidate is added only if, per [eval/preregister.yaml](eval/preregister.yaml):

1. Its 95% CI on pass rate is disjoint above the native baseline's, and
2. quality per 1k tokens does not regress.

Overlapping CIs are inconclusive, not a win. Thresholds are fixed before
running and never tuned to make a candidate pass.

### Running it yourself

```bash
cd eval
uv run sc-eval --trials 5 --k 3                   # all tasks, all arms
uv run sc-eval --arms B_confidence --tasks fix-x  # one candidate, one task
```

### Confirmed cuts

`parallel.py` (the v4 in-plugin parallel executor) is a confirmed cut: native
async subagents cover it, and an in-plugin DAG double-schedules against native
orchestration.

## Optional integrations

### Disclosure

SuperClaude works with **zero MCP servers**. Where MCP is useful, two of the
servers we mention — **airis-mcp-gateway** and **mindbase** — are maintained by
**Agile Tech Inc., the company of the v5 author**. Treat their recommendation
accordingly; they are optional, never a hard dependency, and every feature
degrades gracefully without them.

### Independent alternatives

Install individual third-party servers instead:

```bash
superclaude mcp --list
superclaude mcp --servers context7 tavily   # docs lookup, web search
```

### Zero-MCP operation

Skills, the agent, hooks, the CLI, and the pytest plugin all function without
any MCP server configured. Hooks that reference MCP tools (session-summary)
skip silently when the tools are absent.

## Why not keep everything?

### Doesn't more context help?

No — context is a budget. Every always-loaded instruction competes with your
code and your task. Claude Code's own design pushes the same way: progressive
disclosure in [Skills](https://code.claude.com/docs/en/skills) (load details
only when triggered) and keeping [CLAUDE.md](https://code.claude.com/docs/en/memory)
lean (~200 lines) because every line is paid on every turn.

### What about trigger precision?

With 30 commands and 20 agents, descriptions overlap and the model picks the
wrong tool — or none. Fewer, sharper components trigger more reliably. This is
why Claude Code merged custom slash commands into the Skills system rather than
growing both ([Skills docs](https://code.claude.com/docs/en/skills)).

### Why cut the 20 persona agents?

They were system prompts pretending to be people. Native subagents already
provide isolation and parallelism; "act as a security engineer" no longer needs
3KB of persona text. The one that survived (explore-haiku) survives because it
changes the *model*, not the personality — that's something a prompt can't do.

### Why did the pytest plugin stop writing files?

v4's reflexion hook wrote `docs/mistakes/*.md` into every repo you tested in.
That's pollution, not persistence. v5 writes nothing unless you set
`SUPERCLAUDE_REFLEXION_OUTPUT_DIR`, and `docs/mistakes/` is gitignored.

### Behavior rules belong in prompts, right?

Enforcement belongs in [hooks](https://code.claude.com/docs/en/hooks-guide):
a `PreToolUse` hook fires deterministically; a prompt rule fires when the model
remembers it. v4 promised hooks and shipped an empty directory; v5 ships five.

### What if I miss a v4 command?

Most of the 30 commands were thin wrappers around things you can just ask for.
The [migration guide](docs/migration/v4-to-v5.md) maps every removed command,
agent, and mode to its native replacement. If a removed piece genuinely beats
native behavior, bring it back through the eval gate — with numbers.

## Contributing

### Adding a component

Run the eval, attach the numbers. PRs proposing new skills/agents/hooks without
results per [eval/preregister.yaml](eval/preregister.yaml) will be redirected
to the eval harness first. See [CLAUDE.md](CLAUDE.md) for the developer setup
and [eval/README.md](eval/README.md) for the harness.

### Knowledge hub

Community best practices for Claude Code-era development live in
[docs/knowledge/](docs/knowledge/README.md) — contributions need evidence, not
opinions.

## Documentation

- [Migration: v4 → v5](docs/migration/v4-to-v5.md)
- [Eval harness](eval/README.md)
- [Knowledge hub](docs/knowledge/README.md)
- [Upstream RFC draft](docs/rfc/v5-slim-down.md)
- [CLAUDE.md template](docs/Templates/CLAUDE.template.md)

## Acknowledgements

v5 stands on four major versions of community work. Thanks to every v4
contributor — the slim-down deletes prompt text, not the lessons it encoded.

## License

[MIT](LICENSE)
