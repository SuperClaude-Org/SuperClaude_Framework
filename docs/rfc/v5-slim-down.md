# RFC: SuperClaude v5 — eval-gated slim-down

> Draft for a GitHub Discussion on SuperClaude-Org/SuperClaude_Framework.
> Status: draft, to be posted manually. Numbers below are from the `v5` branch
> at 5.0.0a1.

## Thesis

Models got better. A framework whose value is injected instruction text must
shrink as the model grows, or it turns into overhead: context cost on every
turn, instruction-budget competition with the user's own CLAUDE.md, and
degraded trigger precision when 50 similar descriptions fight over one request.

Proposal: v5 keeps only what models cannot do alone — deterministic enforcement
(hooks), external access (MCP), persistence — plus structured-format content
skills that demonstrably hold up. "Demonstrably" means a pre-registered A/B
eval against native Claude Code, not a maintainer's intuition. This matches the
direction of Claude Code itself: slash commands merged into Skills, progressive
disclosure, lean CLAUDE.md, enforcement via hooks
(https://code.claude.com/docs/en/skills, https://code.claude.com/docs/en/hooks-guide,
https://code.claude.com/docs/en/memory).

## The numbers

| | v4.3.0 | v5 branch (5.0.0a1) |
|---|---|---|
| Slash commands | 30 | 0 |
| Persona agents | 20 | 1 |
| Behavioral modes | 7 | 0 |
| Skills | 0 | 4 |
| Hooks | 0 shipped (empty `hooks/` directory, despite docs promising hooks) | 5 |
| Prompt content | 286KB | 84KB built plugin (skills 44KB, agents 4KB, hooks 4KB) |
| Pytest side effects | wrote `docs/mistakes/*.md` into user repos | no writes unless `SUPERCLAUDE_REFLEXION_OUTPUT_DIR` is set |
| Tests | — | 256 passing |

## What survives, and the gate that decides

Survivors on the `v5` branch:

- **Skills (4)**: confidence-check (+ TypeScript scoring helper), spec-panel,
  socratic, pm-reflexion.
- **Agent (1)**: explore-haiku — exploration on Haiku; it survives because it
  changes the model, not the persona.
- **Hooks (5)**: session-restore (SessionStart), confidence-gate (PreToolUse on
  Write|Edit), session-summary + reflexion-trigger (Stop), tab-title (opt-in
  via `SUPERCLAUDE_TAB_TITLE=1`).
- **CLI**: `install [--minimal]`, `update`, `doctor`, `mcp`, `install-skill`.

The gate (`eval/` on the branch): each candidate is one minimal plugin variant,
A/B'd against bare `claude -p` on container-verified tasks, machine-scored, no
LLM judge. Survive rule is pre-registered in `eval/preregister.yaml` **before**
running: disjoint 95% CIs above the native baseline AND no quality-per-token
regression. Overlapping CIs = inconclusive = not shipped. The thresholds are
never edited to make a candidate pass.

Honest caveat: the current task corpus is small (smoke-level). The
pre-registration sets ≥20 tasks as the bar for real decisions; growing the
corpus is the main open workstream, and the surviving skills must re-confirm
against it.

## What is deleted, and the native replacement

| Deleted | Native replacement |
|---|---|
| 30 `/sc:*` slash commands | Skills + plainly asking the model; Claude Code merged commands into Skills |
| 19 of 20 persona agents | Native subagents (isolation/parallelism) + one-line domain stance requests |
| 7 behavioral modes | Project CLAUDE.md for persistent rules; hooks for rules that must always fire |
| `parallel.py` executor | Native async subagents — confirmed cut; in-plugin DAG double-schedules against native orchestration |
| Token-budget / ROI marketing numbers | Removed; claims now require eval output |

Migration guide with per-command mapping, breaking changes, and rollback:
`docs/migration/v4-to-v5.md` on the branch.

## Optional-integrations transparency policy

Two MCP servers historically recommended by this repo — airis-mcp-gateway and
mindbase — are maintained by Agile Tech Inc., the company of the v5 author
(this RFC's author). Proposed policy, already applied on the branch:

1. Disclose this affiliation wherever they are mentioned.
2. Always list independent alternatives (`superclaude mcp --servers context7 tavily`).
3. Everything must work with zero MCP servers; hooks referencing MCP tools skip
   silently when the tools are absent.
4. No hard dependency on either, ever.

## PyPI and branch plan

- **v4.3.x: frozen.** Stays on PyPI; security fixes only, released from `master`.
- **v5: demo on the `v5` branch**, published as pre-releases (5.0.0a1 → ...).
  Nothing about v4 breaks for existing users until they opt in.
- **Adoption decides.** If v5 earns it (issues, usage, contributor energy), it
  becomes the default; if not, the branch remains an experiment and v4 stays
  the face of the project. No forced migration.

## Asks

1. **Co-maintainers.** This direction needs more than one pair of hands —
   especially for growing the eval corpus. Explicitly inviting the most active
   v4 contributors: Mithun Gowda B (@<github-handle>) and NomenAK (@NomenAK).
   Interested in co-owning the eval harness or the v5 branch?
2. **Review of the survive rule** in `eval/preregister.yaml` — is
   disjoint-CIs-plus-no-token-regression the right bar, and is ≥20 tasks the
   right minimum?
3. **Candidates for re-admission.** If you believe a removed command/agent/mode
   beats native behavior, propose it as an eval variant; the harness
   auto-discovers `eval/variants/<comp>/`.

## Open questions

- Should the 4 surviving skills also be re-gated on the larger corpus before
  5.0.0 final, with removal if inconclusive? (Author's position: yes.)
- Translation strategy: README translations currently track v4 with a banner;
  re-translate after this RFC settles, or drop to English-only until stable?
- Does upstream want the knowledge hub (`docs/knowledge/`) as part of this
  repo, or as a separate repo?
- npm distribution (`@bifrost_inc/superclaude`) — keep, transfer, or retire
  for v5?
- What is the deprecation window for v4 issue support once v5 is default?
