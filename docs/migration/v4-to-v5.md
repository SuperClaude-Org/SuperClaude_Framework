# Migrating from v4 to v5

v5 is an eval-gated slim-down: a component ships only if it beats native Claude
Code behavior in an A/B eval ([eval/README.md](../../eval/README.md),
[eval/preregister.yaml](../../eval/preregister.yaml)). This guide covers what
was removed, what replaces it, the breaking changes, and the upgrade steps.

## Summary

| | v4.3.0 | v5 (5.0.0a1) |
|---|---|---|
| Slash commands | 30 (`/sc:*`) | 0 |
| Skills | 0 | 4 (confidence-check, spec-panel, socratic, pm-reflexion) |
| Agents | 20 | 1 (explore-haiku) |
| Behavioral modes | 7 | 0 |
| Hooks | 0 (empty directory, despite docs) | 5 |
| Prompt content | 286KB | 84KB built plugin |

## What was removed, and what replaces it

### 30 slash commands → native skills + just asking

The `/sc:*` commands (`implement`, `analyze`, `troubleshoot`, `research`,
`document`, `git`, `task`, `workflow`, ...) were mostly structured prompts for
things current models do well when asked directly. Claude Code has also merged
custom slash commands into the [Skills system](https://code.claude.com/docs/en/skills),
which adds progressive disclosure and auto-triggering.

Replacements:

- `/sc:implement "X"` → just ask: "implement X". Pre-flight rigor is covered by
  the **confidence-check** skill and enforced by the **confidence-gate** hook.
- `/sc:spec-panel` → the **spec-panel** skill.
- `/sc:reflect` after failures → the **pm-reflexion** skill + the
  **reflexion-trigger** Stop hook.
- `/sc:load` / `/sc:save` → the **session-restore** SessionStart hook, the
  **session-summary** Stop hook, and Claude Code's native `--continue` / `--resume`.
- Everything else (`/sc:analyze`, `/sc:build`, `/sc:cleanup`, `/sc:git`, ...) →
  describe what you want in plain language. If you find a case where the v4
  command measurably beats asking, bring it through the eval gate.

### 20 persona agents → native subagents

`@system-architect`, `@security-engineer`, `@python-expert`, etc. were persona
system prompts. Native Claude Code subagents already provide the valuable part
(context isolation, parallelism), and current models adopt a domain stance from
a one-line request ("review this as a security engineer").

The exception that survived: **explore-haiku** changes the *model* (cheap
Haiku-powered codebase exploration), which a persona prompt cannot do.

### 7 modes → CLAUDE.md + hooks

The behavioral modes (Brainstorming, Business Panel, Deep Research,
Introspection, Orchestration, Task Management, Token Efficiency) were
always-loaded instruction text. Persistent behavioral rules belong in your
project's [CLAUDE.md](https://code.claude.com/docs/en/memory) (kept lean);
rules that must *always* fire belong in
[hooks](https://code.claude.com/docs/en/hooks-guide), because a hook is
deterministic and a prompt instruction is not. See
[docs/Templates/CLAUDE.template.md](../Templates/CLAUDE.template.md) for a
starter.

### parallel.py → native subagents (confirmed cut by eval)

The in-plugin parallel executor is listed under `confirmed_cuts` in
[eval/preregister.yaml](../../eval/preregister.yaml): native async subagents
cover it, and an in-plugin DAG double-schedules against native orchestration.

## Breaking changes

1. **Reflexion file persistence is opt-in.** v4's pytest plugin wrote
   `docs/mistakes/*.md` into the repo under test on failures. v5 writes nothing
   unless `SUPERCLAUDE_REFLEXION_OUTPUT_DIR` is set to a directory.
   `docs/mistakes/` is gitignored in this repo.
2. **CLI flags renamed.** `--target` is replaced by `--skills-dir` and
   `--agents-dir` on `superclaude install` / `superclaude update`
   (defaults: `~/.claude/skills`, `~/.claude/agents`).
3. **Pytest plugin no longer writes files.** Fixtures and markers
   (`confidence_checker`, `@pytest.mark.confidence_check`, ...) are unchanged.
4. **Removed surfaces.** `/sc:*` commands, the 19 removed agents, and the 7
   modes are not installed and receive no updates.

## Upgrade steps

```bash
# 1. Upgrade the package
pipx upgrade superclaude          # or: pipx install superclaude==5.0.0a1

# 2. Install the v5 skills, agent, and hooks
superclaude install               # or: superclaude install --minimal

# 3. Remove the v4 slash commands (no longer maintained)
rm -rf ~/.claude/commands/sc

# 4. Optional: clean remaining legacy artifacts (takes a backup first)
./scripts/uninstall_legacy.sh

# 5. Verify
superclaude doctor
```

If you had v4 agents installed in `~/.claude/agents/`, `superclaude install`
manages only the files it ships; remove leftover v4 persona agents manually if
you no longer want them.

## v4 freeze policy

v4.3.x remains on PyPI, frozen: security fixes only, no feature work. Issues
against v4 behavior should state the version; fixes land on `master`, while v5
development happens on the `v5` branch.

## Rollback

v5 is an alpha. To return to v4:

```bash
pipx install --force superclaude==4.3.0
superclaude install
```

Your `~/.claude/commands/sc/` directory is recreated by the v4 installer; the
v5 skills in `~/.claude/skills/` can be removed by hand or left in place (they
are inert without the v5 hooks).
