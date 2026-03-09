# Commands and Skills Cross-Reference Matrix

## Purpose

This document gives contributors a current, repository-grounded map of how SuperClaude commands, skills, and Python implementation layers relate.

Source of truth for this document:
- `src/superclaude/commands/`
- `src/superclaude/skills/`
- `src/superclaude/cli/`

If older docs conflict with the current repository structure, prefer the current code and package contents. In this repository state, that matters: some older command documentation still references `plugins/superclaude/...`, but the active package and install code resolve from `src/superclaude/...` first.

## Executive summary

| Area | Current state | Contributor takeaway |
|---|---|---|
| Command source of truth | `src/superclaude/commands/*.md` | Edit command behavior and user-facing contract here. |
| Skill source of truth | `src/superclaude/skills/<skill>/...` | Edit protocol-heavy behavior here when a command delegates to a skill. |
| Installer behavior | `src/superclaude/cli/install_commands.py`, `install_skill.py`, `install_skills.py` | Packaging/install semantics are implemented in Python, not in markdown assets. |
| Protocol-backed commands | Present for roadmap, adversarial, recommend, task-unified, tasklist, cleanup-audit, cli-portify, review-translation, pm, validate-tests | These commands are thin entry points; the skill usually contains the real workflow. |
| Direct-only commands | Many commands have no matching skill package | Their behavior currently lives in the command markdown and any supporting Python/runtime conventions. |
| Deprecated task commands | `task.md` and `task-mcp.md` are deprecated in favor of `task-unified.md` | Avoid extending deprecated commands unless maintaining backwards compatibility. |
| Inventory ambiguity | `sc-forensic-qa-protocol/` exists as a directory but has no `SKILL.md` | Treat as an internal or incomplete asset until a manifest is added. |

## Repository-grounded component model

| Layer | What it does | Primary location | Typical change type |
|---|---|---|---|
| Command | User-facing slash command contract, triggers, flags, examples, and boundaries | `src/superclaude/commands/` | Update invocation UX, flags, top-level workflow summary, deprecation notices |
| Skill / protocol | Detailed execution protocol, reference material, templates, rules, scripts | `src/superclaude/skills/` | Update behavioral algorithm, generation rules, reusable protocol assets |
| Python implementation | Installation, packaging, CLI plumbing, validation helpers | `src/superclaude/cli/` and other Python packages under `src/superclaude/` | Update actual install/discovery behavior, runtime plumbing, tests |

## Command inventory

The table below reflects the current files under `src/superclaude/commands`.

| File | Frontmatter name | Category | Status | Notes |
|---|---|---:|---|---|
| `adversarial.md` | `adversarial` | analysis | active | Explicitly delegates to `sc:adversarial-protocol`. |
| `agent.md` | `sc:agent` | — | active | Specialized controller entry point; no protocol skill found in current skill inventory. |
| `analyze.md` | `analyze` | utility | active | No protocol skill found. |
| `brainstorm.md` | `brainstorm` | orchestration | active | No protocol skill found. |
| `build.md` | `build` | utility | active | No protocol skill found. |
| `business-panel.md` | not parsed from frontmatter in quick inventory | — | active | Command exists; no matching skill package found. |
| `cleanup.md` | `cleanup` | workflow | active | No protocol skill found. |
| `cleanup-audit.md` | `cleanup-audit` | utility | active | Explicitly delegates to `sc:cleanup-audit-protocol`. |
| `cli-portify.md` | `cli-portify` | development | active | Explicitly delegates to `sc:cli-portify-protocol`. |
| `design.md` | `design` | utility | active | No protocol skill found. |
| `document.md` | `document` | utility | active | No protocol skill found. |
| `estimate.md` | `estimate` | special | active | No protocol skill found. |
| `explain.md` | `explain` | workflow | active | No protocol skill found. |
| `git.md` | `git` | utility | active | No protocol skill found. |
| `help.md` | `help` | utility | active | Reference/help surface. |
| `implement.md` | `implement` | workflow | active | No protocol skill found. |
| `improve.md` | `improve` | workflow | active | No protocol skill found. |
| `index.md` | `index` | special | active | No protocol skill found. |
| `index-repo.md` | `sc:index-repo` | — | active | Uses `sc:` prefix in frontmatter name; no matching skill package found. |
| `load.md` | `load` | session | active | No protocol skill found. |
| `pm.md` | `pm` | orchestration | active | Explicitly delegates to `sc:pm-protocol`. |
| `recommend.md` | `sc:recommend` | utility | active | Explicitly delegates to `sc:recommend-protocol`. |
| `reflect.md` | `reflect` | special | active | No protocol skill found. |
| `research.md` | `research` | command | active | No protocol skill found. |
| `review-translation.md` | `review-translation` | orchestration | active | Explicitly delegates to `sc:review-translation-protocol`. |
| `roadmap.md` | `sc:roadmap` | — | active | Explicitly delegates to `sc:roadmap-protocol`. |
| `save.md` | `save` | session | active | No protocol skill found. |
| `sc.md` | `sc` | — | active | Dispatcher/help surface. |
| `select-tool.md` | `select-tool` | special | active | No protocol skill found. |
| `spawn.md` | `spawn` | special | active | No protocol skill found. |
| `spec-panel.md` | `spec-panel` | analysis | active | No matching skill package found. |
| `task.md` | `task-legacy` | special | deprecated | Deprecated in favor of `task-unified`. |
| `task-mcp.md` | `task-mcp` | special | deprecated | Deprecated in favor of `task-unified`. |
| `task-unified.md` | `task` | special | active | Explicitly delegates to `sc:task-unified-protocol` for STANDARD/STRICT tiers. |
| `tasklist.md` | `tasklist` | utility | active | Explicitly delegates to `sc:tasklist-protocol`. |
| `test.md` | `test` | utility | active | No protocol skill found. |
| `troubleshoot.md` | `troubleshoot` | utility | active | No protocol skill found. |
| `validate-tests.md` | `validate-tests` | testing | active | Explicitly delegates to `sc:validate-tests-protocol`. |
| `workflow.md` | `workflow` | orchestration | active | No protocol skill found. |

## Skill and protocol inventory

The table below reflects the current directories under `src/superclaude/skills`.

| Skill directory | Manifest name | Primary role | Supporting assets observed | Contributor note |
|---|---|---|---|---|
| `confidence-check` | `Confidence Check` | Pre-implementation readiness gate | `confidence.ts`, `__init__.py` | General-purpose skill, not tied to one command. |
| `sc-adversarial-protocol` | `sc:adversarial-protocol` | Adversarial debate, comparison, merge protocol | `refs/` | Backing protocol for `/sc:adversarial`. |
| `sc-cleanup-audit-protocol` | `sc:cleanup-audit-protocol` | Multi-pass repository audit | `rules/`, `scripts/`, `templates/` | Backing protocol for `/sc:cleanup-audit`. |
| `sc-cli-portify-protocol` | `sc-cli-portify-protocol` | CLI-portify workflow protocol | `decisions.yaml`, `refs/`, `__init__.py` | Backing protocol for `/sc:cli-portify`. |
| `sc-forensic-qa-protocol` | no `SKILL.md` present | Unclear / incomplete in current repo state | `refs/`, `rules/`, `templates/` | Present as assets only; not currently a valid manifest-backed skill package. |
| `sc-pm-protocol` | `sc:pm-protocol` | PM orchestration protocol | `SKILL.md` | Backing protocol for `/sc:pm`. |
| `sc-recommend-protocol` | `sc:recommend-protocol` | Recommendation engine protocol | `SKILL.md` | Backing protocol for `/sc:recommend`. |
| `sc-review-translation-protocol` | `sc:review-translation-protocol` | Localization review protocol | `SKILL.md` | Backing protocol for `/sc:review-translation`. |
| `sc-roadmap-protocol` | `sc:roadmap-protocol` | Roadmap generation protocol | `refs/`, `__init__.py` | Backing protocol for `/sc:roadmap`. |
| `sc-task-unified-protocol` | `sc:task-unified-protocol` | Tiered task workflow protocol | `SKILL.md`, `__init__.py` | Backing protocol for `/sc:task` in unified mode. |
| `sc-tasklist-protocol` | `sc:tasklist-protocol` | Roadmap-to-tasklist generation | `rules/`, `templates/`, `__init__.py` | Backing protocol for `/sc:tasklist`. |
| `sc-validate-tests-protocol` | `sc:validate-tests-protocol` | Self-validation for classification behavior | `classification-algorithm.yaml`, `__init__.py` | Backing protocol for `/sc:validate-tests`. |

## Command-to-skill relationship matrix

This matrix reflects explicit evidence in the current command files, plus likely family relationships where the repository structure suggests a pairing.

| Command | Explicitly invokes skill? | Skill / family | Relationship confidence | Notes |
|---|---|---|---|---|
| `/sc:adversarial` | Yes | `sc:adversarial-protocol` | high | Command is a thin activation surface for the protocol. |
| `/sc:cleanup-audit` | Yes | `sc:cleanup-audit-protocol` | high | Protocol includes rules, scripts, and report templates. |
| `/sc:cli-portify` | Yes | `sc-cli-portify-protocol` | high | Explicit activation in command file. |
| `/sc:pm` | Yes | `sc:pm-protocol` | high | Command defers to protocol. |
| `/sc:recommend` | Yes | `sc:recommend-protocol` | high | Command explicitly says not to execute protocol steps from command file alone. |
| `/sc:review-translation` | Yes | `sc:review-translation-protocol` | high | Protocol-backed review flow. |
| `/sc:roadmap` | Yes | `sc:roadmap-protocol` | high | Command passes user args through to the skill. |
| `/sc:task` (unified) | Yes, for STANDARD/STRICT | `sc:task-unified-protocol` | high | LIGHT and EXEMPT tiers are handled directly by the command instructions. |
| `/sc:tasklist` | Yes | `sc:tasklist-protocol` | high | Command describes itself as a thin wrapper over the skill. |
| `/sc:validate-tests` | Yes | `sc:validate-tests-protocol` | high | Self-validation command for task classification behavior. |
| `/sc:spec-panel` | No explicit protocol call found | likely adjacent to adversarial/review families | medium | Analysis-oriented command with no current matching skill package. |
| `/sc:workflow` | No | likely adjacent to task/roadmap family | low | Similar planning space, but no explicit skill package present. |
| `/sc:document` | No | no current protocol package | medium | Behavior appears command-defined. |
| `/sc:analyze` | No | no current protocol package | medium | Behavior appears command-defined. |
| `/sc:implement` | No | may use `confidence-check` as a contributor pattern, not explicit wiring | low | No explicit protocol-backed link in current command file inventory. |
| `/sc:build` | No | may use `confidence-check` as a contributor pattern, not explicit wiring | low | No explicit skill package for build. |
| `/sc:test` | No | overlaps conceptually with `sc:validate-tests-protocol` but not equivalent | medium | `/sc:test` is general execution; validate-tests is specialized self-test infrastructure. |
| `/sc:task-mcp` | No current protocol activation checked | superseded by `sc:task-unified-protocol` family | high | Deprecated. Contributors should prefer unified task flow. |
| `/sc:task` (legacy file) | No current protocol activation checked | superseded by `sc:task-unified-protocol` family | high | Deprecated. |

## Skill-family view

This view is useful when deciding where a new behavior belongs.

| Skill family | Current commands most related | What belongs in the skill | What belongs in the command |
|---|---|---|---|
| Adversarial | `adversarial`, `roadmap`, possibly `spec-panel` | Debate phases, scoring, merge rules, reusable artifact templates | User-facing flags, examples, handoff instructions |
| Roadmap / planning | `roadmap`, `tasklist`, `workflow` | Extraction pipelines, scoring, generation templates, downstream roadmap/tasklist protocol | Entry point, required inputs, examples, command boundaries |
| Unified task execution | `task-unified`, legacy `task`, legacy `task-mcp`, `validate-tests` | Tier rules, workflow enforcement, reusable compliance logic, test specs | Classification preamble, deprecation messaging, user ergonomics |
| Audit / QA | `cleanup-audit`, possibly forensic QA assets | Multi-pass audit rules, evidence templates, scripts, reporting structure | Audit invocation surface and output expectations |
| Recommendation / orchestration | `recommend`, `pm` | Recommendation logic, orchestration protocol, PDCA loops | User-visible entry points and top-level behavior contract |
| Translation / localization | `review-translation` | Evaluation rubric, review workflow, evidence collection | Invocation syntax and audience-facing description |
| Confidence / readiness | indirectly related to implementation commands | Readiness checks and validation heuristics | Command-specific choice to invoke or recommend the skill |

## Overlap areas contributors should understand

### 1. Task-command overlap

| Asset | Current role | Contributor guidance |
|---|---|---|
| `task.md` | Deprecated legacy task command | Do not add new primary behavior here unless preserving old entry points. |
| `task-mcp.md` | Deprecated MCP-enforced task command | Treat as historical compatibility surface. |
| `task-unified.md` | Current primary `/sc:task` command | Preferred place for user-facing task command behavior. |
| `sc-task-unified-protocol/` | Current detailed task workflow | Preferred place for tier logic and reusable task protocol rules. |
| `sc-validate-tests-protocol/` | Validation support for unified task logic | Update when changing classification behavior or test-spec format. |

### 2. Roadmap and tasklist pipeline overlap

`/sc:roadmap` and `/sc:tasklist` are adjacent pipeline stages. Contributors should keep these aligned:
- `sc-roadmap-protocol` owns roadmap generation behavior.
- `sc-tasklist-protocol` owns deterministic roadmap-to-tasklist emission.
- If roadmap output structure changes, tasklist parsing assumptions may also need updates.

### 3. Audit and forensic QA overlap

The repository contains a complete `sc-cleanup-audit-protocol` and an incomplete-looking `sc-forensic-qa-protocol` asset bundle. That suggests an audit/QA family is emerging, but only cleanup-audit is currently manifest-backed as a skill.

Contributor implication: if you are extending forensic QA behavior, first decide whether the missing `SKILL.md` is intentional or a gap that should be resolved before adding more protocol assets.

## Gaps, ambiguities, and stale documentation

### Current code should win over older docs

| Observation | Evidence in current repo | Contributor interpretation |
|---|---|---|
| Command README references `plugins/superclaude/commands/` as the edit source | `src/superclaude/commands/README.md` still says to edit `plugins/...` first | Treat this as stale guidance unless/until the repository restores that structure. Current package code installs from `src/superclaude/commands` first. |
| Command installer resolves packaged `commands/` first, then falls back to `plugins/...` | `src/superclaude/cli/install_commands.py` | Packaging/runtime behavior is aligned to `src/superclaude/commands` in the current tree. |
| Skill installer resolves `src/superclaude/skills/...` and validates manifest-like content | `src/superclaude/cli/install_skill.py` | Skill source of truth is the current `src/superclaude/skills` tree. |
| Batch skill installer tries to skip `sc-*` skills with matching commands | `src/superclaude/cli/install_skills.py` | The intention is clear, but the current directory names ending in `-protocol` do not match command filenames directly. |
| `sc-forensic-qa-protocol/` has assets but no `SKILL.md` | directory listing under `src/superclaude/skills/` | Likely incomplete, internal, or intentionally non-installable in current state. |

### Important ambiguity: skill skipping logic vs protocol naming

The batch installer documents an intent to skip skills that are already served by `/sc:` commands. However, the current implementation checks directory names by stripping `sc-` and comparing the remainder to command filenames.

Examples from the current tree:
- `sc-roadmap-protocol` maps to `roadmap-protocol`, but the command file is `roadmap.md`
- `sc-tasklist-protocol` maps to `tasklist-protocol`, but the command file is `tasklist.md`

Contributor takeaway: the naming convention for protocol skills does not currently line up with the simplistic skip logic in `install_skills.py`. If you are changing installation/discovery behavior, update the Python implementation, not just the docs.

## Where to update behavior

### Update the command file when the change is about user-facing invocation

Use `src/superclaude/commands/<name>.md` when changing:
- command name, flags, examples, required inputs
- top-level scope and boundaries
- when a command should call a skill
- deprecation notices and migration guidance
- brief behavioral summaries intended for users

### Update the skill package when the change is about reusable execution protocol

Use `src/superclaude/skills/<skill>/...` when changing:
- multi-step execution logic
- reusable protocol rules
- templates, reference docs, decision tables
- report/output structures used by a protocol
- internal workflow details that should stay shared across entry points

Typical examples:
- scoring rules for adversarial review
- roadmap extraction pipeline details
- cleanup-audit pass definitions
- task-unified classification or enforcement logic

### Update Python implementation when the change affects actual package behavior

Use Python modules under `src/superclaude/` when changing:
- installation and discovery behavior
- how commands/skills are copied to `~/.claude/`
- validation logic implemented in code rather than markdown
- CLI packaging behavior or runtime helpers
- tests for install/discovery or package semantics

Primary files for this area:
- `src/superclaude/cli/main.py`
- `src/superclaude/cli/install_commands.py`
- `src/superclaude/cli/install_skill.py`
- `src/superclaude/cli/install_skills.py`

## Contributor decision guide

| If you need to change... | Start here | Then check | Why |
|---|---|---|---|
| A command’s flags or examples | `src/superclaude/commands/<command>.md` | matching skill package, if any | The command is the user-facing contract. |
| The detailed generation/review algorithm behind a protocol-backed command | matching `src/superclaude/skills/<skill>/` package | command doc for summary and examples | The skill is the execution protocol. |
| Whether a command delegates to a skill at all | command file | possibly installer/discovery code | Delegation is expressed at command level. |
| How command and skill assets are installed | `src/superclaude/cli/*.py` | source asset trees | Install behavior is implemented in Python. |
| Deprecation of a command | command file frontmatter and body | related replacement command and docs | Users need migration guidance at the command surface. |
| Output templates for generated artifacts | skill package `templates/` or `refs/` | command examples if user-visible | Templates are protocol assets. |
| Validation of task-tier logic | `sc-task-unified-protocol` and `sc-validate-tests-protocol` | `task-unified.md` | Logic and self-validation should stay aligned. |

## Recommended contributor workflow

1. Identify whether the behavior is command-facing, protocol-facing, or implementation-facing.
2. Check whether the command explicitly delegates to a skill.
3. If yes, update both layers when necessary:
   - command for invocation contract
   - skill for detailed workflow
4. If installation or discovery behavior is involved, inspect the Python installer modules before editing docs.
5. Prefer current `src/superclaude/...` package contents over older references to `plugins/...` unless the repository structure changes again.
6. For task-related work, treat `task-unified` as the primary active surface and the legacy task commands as compatibility artifacts.

## Fast reference

### Explicit protocol-backed commands

| Command | Backing skill |
|---|---|
| `/sc:adversarial` | `sc:adversarial-protocol` |
| `/sc:cleanup-audit` | `sc:cleanup-audit-protocol` |
| `/sc:cli-portify` | `sc-cli-portify-protocol` |
| `/sc:pm` | `sc:pm-protocol` |
| `/sc:recommend` | `sc:recommend-protocol` |
| `/sc:review-translation` | `sc:review-translation-protocol` |
| `/sc:roadmap` | `sc:roadmap-protocol` |
| `/sc:task` | `sc:task-unified-protocol` for STANDARD/STRICT paths |
| `/sc:tasklist` | `sc:tasklist-protocol` |
| `/sc:validate-tests` | `sc:validate-tests-protocol` |

### Commands currently not represented by a dedicated skill package

These commands exist in the current command tree but do not have a current manifest-backed matching skill package in `src/superclaude/skills`:

| Commands |
|---|
| `agent`, `analyze`, `brainstorm`, `build`, `business-panel`, `cleanup`, `design`, `document`, `estimate`, `explain`, `git`, `help`, `implement`, `improve`, `index`, `index-repo`, `load`, `reflect`, `research`, `save`, `sc`, `select-tool`, `spawn`, `spec-panel`, `test`, `troubleshoot`, `workflow` |

That does not mean they are incomplete. It means their behavior is currently command-defined, convention-defined, or supported elsewhere in Python/runtime context rather than by a dedicated skill manifest.

## Relevant files

- `/config/workspace/SuperClaude_Framework/src/superclaude/commands`
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills`
- `/config/workspace/SuperClaude_Framework/src/superclaude/cli/main.py`
- `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_commands.py`
- `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_skill.py`
- `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_skills.py`
