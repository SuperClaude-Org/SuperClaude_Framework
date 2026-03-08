---
name: sc-cli-portify-protocol
description: "Full behavioral protocol for sc:cli-portify — port inference-based SuperClaude workflows into programmatic CLI pipelines with sprint-style supervised execution."
category: development
complexity: high
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
argument-hint: "--workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>] [--dry-run] [--skip-integration]"
---

# sc:cli-portify — Workflow-to-CLI Pipeline Compiler

Convert inference-based SuperClaude workflows into programmatic CLI pipelines that ensure 100% completion and consistency between runs.

## Purpose

SuperClaude workflows implemented as commands + skills + agents + refs rely entirely on Claude's reasoning for orchestration. This works well for flexible, one-off tasks but breaks down for repeatable multi-step pipelines where you need:

- **Deterministic control flow** — Python decides what runs when, not inference
- **Formal artifact validation** — Gates check output quality programmatically
- **Resume/retry** — Failed steps resume without re-running everything
- **Live monitoring** — TUI shows progress, stall detection, diagnostics
- **Budget economics** — Turn ledger tracks consumption across subprocesses
- **Consistent behavior** — Same inputs produce structurally identical outputs every run

The existing `pipeline/` and `sprint/` modules already solve these problems. This skill bridges the gap by analyzing a workflow and generating a new CLI module that uses these proven patterns.

## What Gets Generated

A CLI subcommand package under `src/superclaude/cli/<name>/`:

| File | Purpose | When Generated |
|------|---------|----------------|
| `models.py` | Domain types extending `PipelineConfig`, `Step`, `StepResult` | Always |
| `gates.py` | `GateCriteria` + semantic check functions returning `tuple[bool, str]` | Always |
| `prompts.py` | LLM contract builders per Claude-assisted step | Always |
| `config.py` | CLI arg resolution, file discovery, config construction | Always |
| `executor.py` | Synchronous supervisor loop with `ThreadPoolExecutor` for parallelism | Always |
| `monitor.py` | NDJSON incremental output parser with domain signals | Always |
| `process.py` | `ClaudeProcess` subclass with domain-specific prompt building | Always |
| `tui.py` | Rich live dashboard with gate state machine | Always |
| `logging_.py` | Dual JSONL + Markdown execution logging | Always |
| `diagnostics.py` | `DiagnosticCollector`, `FailureClassifier`, `ReportGenerator` | Always |
| `commands.py` | Click CLI group and subcommands | Always |
| `__init__.py` | Package exports | Always |
| `inventory.py` | Pure-programmatic file discovery/classification | If workflow has discovery steps |
| `filtering.py` | Pure-programmatic inter-step data filtering | If workflow has filtering between steps |

Plus integration patches for `main.py`.

## Required Input

```
/sc:cli-portify --workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--workflow` | Yes | Skill directory path or `sc-*` name to portify |
| `--name` | No | CLI subcommand name (default: derived from workflow) |
| `--output` | No | Output directory (default: `src/superclaude/cli/<name>/`) |
| `--dry-run` | No | Show decomposition plan without generating code |
| `--skip-integration` | No | Generate module only, skip main.py wiring |

**STOP** if `--workflow` is not provided or the path doesn't resolve to a valid skill.

## Behavioral Flow

Four phases, each producing artifacts that feed the next. Present output to user for review after Phases 1 and 2 before continuing.

### Phase 1: Workflow Analysis

Load `refs/analysis-protocol.md` before this phase. It contains the discovery checklist, step decomposition algorithm, classification rubric, and output format template.

**Goal**: Decompose the target workflow into a structured pipeline specification.

1. **Discover components** — Find the command `.md`, skill `SKILL.md`, all `refs/` and `rules/`, all `templates/`, all `scripts/`, and all referenced agents. Build a component inventory table with paths, line counts, and purposes.

2. **Map the protocol** — Extract the step-by-step behavioral flow. Pay attention to:
   - Wave/phase boundaries in the skill
   - Agent delegation patterns (which agent, parallel vs sequential)
   - Conditional execution paths (flags that skip steps)
   - Implicit inter-step data flow (what one step produces that another consumes)

3. **Identify steps** — A new Step boundary exists when:
   - A new artifact is produced
   - A different agent takes over
   - Execution mode changes (sequential → parallel)
   - A quality gate must be evaluated
   - Operation type changes (analysis → generation → validation)

4. **Classify each step** on the programmatic spectrum:
   - **Pure programmatic**: Runs as a Python function, no Claude subprocess. Examples: file inventory via `git ls-files`, config construction, file filtering between passes, scoring formulas, structural validation, batch assignment. If the logic is deterministic and the input/output formats are well-defined, it should be programmatic.
   - **Claude-assisted**: Runs as a Claude subprocess with a prompt contract and gate. Examples: content analysis, writing reports, rubric-based assessment, creative synthesis, debate.
   - **Hybrid**: Programmatic setup → Claude subprocess → programmatic validation. Examples: steps that need Claude for content but have strict structural validation on the output.

5. **Map dependencies and parallel groups** — Draw the data flow: which steps produce artifacts consumed by downstream steps? Which steps are independent and can run concurrently? For batched workflows, identify where batch parallelism applies.

6. **Extract gates** — For each step output, identify what validation the original workflow expects. Map these to gate tiers: EXEMPT (informational), LIGHT (exists + non-empty), STANDARD (structural checks), STRICT (structural + semantic).

7. **Assign gate modes** — `GateMode.BLOCKING` for steps whose output feeds downstream steps. `GateMode.TRAILING` for quality-only checks that don't affect data flow.

**Output**: `portify-analysis.md` — Complete decomposition following the template in `refs/analysis-protocol.md`. Must include: component inventory, step graph with classifications, parallel groups, gates summary, data flow diagram, and recommendations.

**Present to user for review before Phase 2.**

### Phase 2: Pipeline Specification

Load `refs/pipeline-spec.md` before this phase. It contains Step definition patterns, model design patterns, gate patterns, executor patterns, and the new unified-audit-gating patterns (TurnLedger, gate modes, subprocess isolation, context injection, resume semantics).

**Goal**: Convert the analysis into concrete, code-ready specifications.

1. **Design the Step graph** — Map each workflow step to `Step` objects. Batched parallel steps are `list[Step]` groups. Dynamic step counts (e.g., batch count determined at runtime) require a `build_steps()` function.

2. **Define models** — Design domain-specific dataclasses:
   - Config extending `PipelineConfig` with workflow-specific fields (source paths, pass selection, batch sizes, stall/timeout policies)
   - Status enum with domain-specific states (e.g., `VALIDATION_FAIL`, `CRITICAL_FAIL` for audit workflows)
   - Result extending `StepResult` with execution telemetry
   - Aggregate result with `resume_command()` and `suggested_resume_budget`
   - Monitor state with domain-specific NDJSON signals
   - `TurnLedger` integration for budget tracking

3. **Design prompts** — For each Claude-assisted step, write the prompt builder. Each prompt must specify:
   - What input files/context to embed (inline for <50KB, `--file` args for larger)
   - Required output sections and frontmatter fields
   - Machine-readable markers: `EXIT_RECOMMENDATION: CONTINUE|HALT`
   - Any structural requirements the gate will check

   If prompts collectively exceed ~300 lines, put them in a separate `portify-prompts.md`.

4. **Design gates** — For each output artifact, define:
   - `GateCriteria` with tier, required frontmatter, min lines, semantic checks
   - `GateMode` (BLOCKING or TRAILING)
   - All semantic check functions returning `tuple[bool, str]`

5. **Implement pure-programmatic steps** — Write actual runnable Python code for steps classified as "pure programmatic". These run as direct function calls in the executor, bypassing `ClaudeProcess`. Include: file discovery, domain classification, batch assignment, inter-pass filtering, config construction.

6. **Design the executor** — Sprint-style synchronous supervisor:
   - `ThreadPoolExecutor` for batch parallelism (NOT async/await)
   - `time.sleep()` polling loops for monitoring
   - Per-step/batch monitoring with stall detection
   - `TurnLedger` budget guards before each launch
   - Runner-authored truth: reports from observed data, not Claude self-reporting
   - Subprocess isolation (4-layer model) for child Claude sessions
   - Context injection: prior results compressed into subsequent prompts
   - Signal-aware shutdown with `SignalHandler`

7. **Plan integration** — Click command group, main.py import, file generation order.

**Output**: `portify-spec.md` (+ optional `portify-prompts.md`) — Complete code spec with models, gates, executor design, pure-programmatic implementations, and integration plan.

**Present to user for approval before Phase 3.**

### Phase 3: Code Generation

Load `refs/code-templates.md` before this phase. It contains parameterized file templates for every module.

Generate files in dependency order (models → gates → prompts → config → monitor → process → executor → tui → logging → diagnostics → commands → __init__). Each file imports from `superclaude.cli.pipeline` for shared base types and follows sprint/roadmap naming conventions.

### Phase 4: Integration

1. Patch `main.py` — Add import and `app.add_command()`
2. Verify imports — Quick check for circular dependencies
3. Generate structural test — Validates step graph, gate definitions, and model consistency
4. Write `portify-summary.md` — File inventory, CLI usage, step graph, known limitations

## Decision Framework: What Becomes Programmatic

The value of portification is moving orchestration out of inference. Here are concrete examples from tested workflows:

| Operation | Classification | Why |
|-----------|---------------|-----|
| Enumerate repo files | Pure programmatic | `git ls-files` + pattern matching is deterministic |
| Classify file domains | Pure programmatic | Extension/path pattern rules, no judgment needed |
| Assign files to batches | Pure programmatic | Math: divide files by batch_size, assign to agents |
| Filter Pass 1 results for Pass 2 | Pure programmatic | Parse markdown, extract classifications, filter list |
| Analyze file for issues | Claude-assisted | Requires reading code, understanding context |
| Score variant quality | Hybrid | Formulas are programmatic, rubric evaluation is Claude |
| Validate structural integrity | Pure programmatic | Regex checks, section presence, field counts |
| Spot-check verification | Claude-assisted | Re-reads files, re-evaluates claims independently |
| Merge batch reports | Claude-assisted | Requires synthesis, deduplication, pattern extraction |
| Compute convergence score | Pure programmatic | `agreed / total` — arithmetic |
| Generate executive summary | Claude-assisted | Requires narrative synthesis |

### Rule of Thumb
If you can write a Python function for it with clear input→output types and no ambiguity, make it programmatic. If it requires reading natural language, making judgments, or synthesizing information, use Claude with a gate to verify the output.

## Code Generation Principles

These align with the unified-audit-gating architecture in `pipeline/`.

### Critical Constraints
1. **Synchronous execution** — Sprint uses `threading` + `time.sleep()` polling. Use `concurrent.futures.ThreadPoolExecutor` for batch parallelism. Do NOT use async/await.
2. **Gate function signatures** — All semantic checks return `tuple[bool, str]`. The reason string feeds diagnostics and retry decisions.
3. **Runner-authored truth** — Reports derive from runner-observed data (exit codes, artifacts, gates, monitor signals), not Claude's self-reported status.
4. **Deterministic flow control** — Python makes all decisions about what runs next. Claude never decides "what's next".

### Shared Pipeline Patterns
5. **Reuse `pipeline/` primitives** — `PipelineConfig`, `Step`, `StepResult`, `GateMode`, `GateCriteria`, `SemanticCheck`, `gate_passed()`, `ClaudeProcess`
6. **Gate modes** — `BLOCKING` (default) stops pipeline on failure. `TRAILING` defers evaluation. Use trailing only for quality checks that don't affect downstream data flow.
7. **Turn budget** — `TurnLedger` with debit/credit/guard for multi-subprocess pipelines. Pre-launch guards prevent launching when budget too low.
8. **Subprocess isolation** — 4-layer model: scoped work dir, git ceiling, isolated plugin dir, isolated settings dir.
9. **Context injection** — Prior results serialized into subsequent prompts. Compress older, preserve recent.
10. **Resume-first failures** — On halt: exact resume command, remaining work, diagnostic path, budget suggestion.
11. **Diagnostic chain** — Runner-side failure analysis that doesn't consume turn budget.

### Output Guidance
- `portify-analysis.md`: Under 400 lines. Step graph, gates, data flow.
- `portify-spec.md`: Split prompts to separate file if spec exceeds 800 lines.
- Pure-programmatic steps: Full implementation code, not descriptions.

## Boundaries

### Will Do
- Analyze any SuperClaude skill/command/agent workflow
- Decompose into structured pipeline specification
- Generate complete CLI subcommand module
- Wire module into CLI infrastructure
- Generate structural tests for pipeline

### Will Not Do
- Execute the generated pipeline
- Modify original skill/command/agent files
- Create new skills or agents
- Make architectural decisions about the workflow's logic
- Generate LLM content quality tests (only structural)

## Related Commands

- `/sc:implement` — General feature implementation
- `/sc:design` — System architecture design
- `/sc:analyze` — Code analysis for understanding workflows
- `/sc:build` — Build and compile after generating
