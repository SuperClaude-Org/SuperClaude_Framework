# Roadmap CLI Tools — Release Guide

This guide covers the `superclaude roadmap` CLI tooling, including:
- what each component does,
- when to use it,
- how to run it,
- practical examples with all options,
- the 8-step adversarial pipeline architecture,
- gate criteria and validation,
- and how it fits into the **spec → roadmap → tasklist → execution** workflow.

---

## 1) Release Summary (What is included)

### Core command surface
The `superclaude roadmap` command group provides 1 subcommand:
1. `run` — Execute the 8-step adversarial roadmap generation pipeline

### Architecture overview
The roadmap CLI orchestrates an **adversarial dual-agent pipeline** that:
- Extracts requirements from a specification file
- Generates two independent roadmap variants via different agent personas
- Produces a structured diff analysis of divergences
- Facilitates a multi-round adversarial debate between variants
- Scores and selects a base variant
- Merges the best elements into a final roadmap
- Generates a test strategy aligned to the merged roadmap

### Module structure
```
src/superclaude/cli/roadmap/
├── __init__.py      # Exports roadmap_group
├── commands.py      # Click CLI definition (FR-009)
├── models.py        # AgentSpec + RoadmapConfig dataclasses
├── executor.py      # 8-step pipeline orchestration
├── gates.py         # Gate criteria + semantic check functions
└── prompts.py       # Pure prompt builder functions (NFR-004)
```

### Shared pipeline dependency
The roadmap CLI builds on the shared `pipeline/` module:
- `pipeline/models.py` — Step, StepResult, StepStatus, GateCriteria, PipelineConfig
- `pipeline/executor.py` — Generic step sequencer with retry, gates, parallel dispatch
- `pipeline/process.py` — ClaudeProcess subprocess management
- `pipeline/gates.py` — Gate evaluation logic

### Key design decisions
- **Context isolation**: Each subprocess receives only its prompt and `--file` inputs. No `--continue`, `--session`, or `--resume` flags are passed (FR-003, FR-023)
- **Inline embedding**: Input files are embedded directly into prompts up to 100KB; larger inputs fall back to `--file` flags
- **Atomic writes**: State files and sanitized outputs use `tmp + os.replace()` for crash safety
- **Preamble sanitization**: Conversational text before YAML frontmatter is automatically stripped from step outputs
- **Pipeline diagnostics injection**: Executor-populated timing metadata is injected into extraction frontmatter post-subprocess (FR-033)

---

## 2) Command Reference — When and How to Use

## `superclaude roadmap run`

### What it does
Loads a specification file, builds an 8-step adversarial pipeline, validates outputs through gate criteria at each step, and produces a final merged roadmap with test strategy.

Pre-flight: creates the output directory if it doesn't exist.

### Use when
- You have a specification document (markdown) ready for roadmap generation.
- You want adversarial quality: two independent agent perspectives debated and merged.
- You want deterministic, gate-validated pipeline execution with resume capability.
- You want to plug into the downstream `spec → roadmap → tasklist → sprint` workflow.

### Syntax
```bash
superclaude roadmap run <SPEC_FILE> [options]
```

### Positional arguments
| Argument | Required | Description |
|----------|----------|-------------|
| `SPEC_FILE` | Yes | Path to a specification markdown file. Must exist on disk. |

### Key options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--agents` | String | `opus:architect,haiku:architect` | Comma-separated agent specs in `model[:persona]` format. Controls which models/personas generate the two roadmap variants. |
| `--output` | Path | Parent dir of SPEC_FILE | Output directory for all pipeline artifacts. Created automatically if it doesn't exist. |
| `--depth` | Choice | `standard` | Debate round depth: `quick` (1 round), `standard` (2 rounds), `deep` (3 rounds). |
| `--resume` | Flag | Off | Skip steps whose outputs already pass their gates. Re-run from the first failing step. Detects stale spec files via SHA-256 hash comparison. |
| `--dry-run` | Flag | Off | Print step plan, gate criteria, and timeout budgets, then exit without launching any subprocesses. |
| `--model` | String | (empty) | Override model for all steps. When empty, per-agent models from `--agents` are used for generate steps; other steps use the default Claude model. |
| `--max-turns` | Integer | `100` | Maximum agent turns per Claude subprocess. Applies to every step. |
| `--debug` | Flag | Off | Enable debug-level logging to `<output_dir>/roadmap-debug.log`. |

### Agent spec format
The `--agents` flag accepts a comma-separated list of agent specifications:

```
model[:persona]
```

| Component | Required | Default | Examples |
|-----------|----------|---------|----------|
| `model` | Yes | — | `opus`, `sonnet`, `haiku`, `claude-sonnet-4-20250514` |
| `persona` | No | `architect` | `architect`, `security`, `qa`, `performance` |

The model value is passed directly to `claude --model` (no resolution needed — the Claude CLI accepts shorthand names natively).

**Parsing rules**:
- `"opus:architect"` → model=`opus`, persona=`architect`
- `"haiku"` → model=`haiku`, persona=`architect` (default persona)
- `"sonnet:security"` → model=`sonnet`, persona=`security`

The agent's ID (used in output filenames) is `{model}-{persona}`, e.g., `opus-architect`.

### Examples

```bash
# Basic execution with defaults (opus:architect + haiku:architect)
superclaude roadmap run spec.md

# Custom agent personas
superclaude roadmap run spec.md --agents sonnet:security,haiku:qa

# Deep debate with 3 rounds
superclaude roadmap run spec.md --depth deep

# Quick single-round debate for rapid iteration
superclaude roadmap run spec.md --depth quick

# Custom output directory
superclaude roadmap run spec.md --output .dev/releases/current/v2.20/

# Validate pipeline plan without execution
superclaude roadmap run spec.md --dry-run

# Resume from last failure point
superclaude roadmap run spec.md --resume

# Override model for all steps
superclaude roadmap run spec.md --model claude-sonnet-4-20250514

# Increase max turns for complex specs
superclaude roadmap run spec.md --max-turns 200

# Full debug logging
superclaude roadmap run spec.md --debug

# Production-quality deep run with custom agents and output
superclaude roadmap run .dev/releases/current/v2.20/spec.md \
  --agents opus:architect,sonnet:security \
  --depth deep \
  --output .dev/releases/current/v2.20/ \
  --max-turns 150 \
  --debug
```

---

## 3) The 8-Step Adversarial Pipeline

The roadmap pipeline generates a high-quality roadmap through adversarial comparison and debate. Each step runs as a fresh, isolated Claude subprocess.

### Pipeline overview

```
Step 1: Extract ──────────┐
                          │
              ┌───────────┴───────────┐
              │                       │
Step 2a: Generate (Agent A)   Step 2b: Generate (Agent B)   ← parallel
              │                       │
              └───────────┬───────────┘
                          │
Step 3: Diff ─────────────┤
                          │
Step 4: Debate ───────────┤
                          │
Step 5: Score ────────────┤
                          │
Step 6: Merge ────────────┤
                          │
Step 7: Test Strategy ────┘
```

### Step details

| Step | ID | Timeout | Gate Tier | Parallel | Description |
|------|----|---------|-----------|----------|-------------|
| 1 | `extract` | 300s | STRICT | No | Extract requirements from the spec file into structured format with 13 YAML frontmatter fields and 8 body sections |
| 2a | `generate-{agent_a.id}` | 900s | STRICT | Yes | Generate roadmap variant A with agent A's persona perspective |
| 2b | `generate-{agent_b.id}` | 900s | STRICT | Yes | Generate roadmap variant B with agent B's persona perspective |
| 3 | `diff` | 300s | STANDARD | No | Produce structured diff analysis identifying divergences and shared assumptions |
| 4 | `debate` | 600s | STRICT | No | Facilitate multi-round adversarial debate between variants |
| 5 | `score` | 300s | STANDARD | No | Score both variants and select a base for merging |
| 6 | `merge` | 600s | STRICT | No | Produce final merged roadmap from base variant + debate-resolved improvements |
| 7 | `test-strategy` | 300s | STANDARD | No | Generate test strategy mapped to the merged roadmap |

### Output artifacts

All artifacts are written to the output directory (default: parent of SPEC_FILE).

| Artifact | Source Step | Description |
|----------|------------|-------------|
| `extraction.md` | extract | Structured requirements extraction with YAML frontmatter |
| `roadmap-{agent_a.id}.md` | generate-A | Roadmap variant from agent A |
| `roadmap-{agent_b.id}.md` | generate-B | Roadmap variant from agent B |
| `diff-analysis.md` | diff | Structured comparison of both variants |
| `debate-transcript.md` | debate | Multi-round adversarial debate transcript |
| `base-selection.md` | score | Variant scoring and base selection rationale |
| `roadmap.md` | merge | Final merged roadmap (primary output) |
| `test-strategy.md` | test-strategy | Test strategy for the merged roadmap |
| `.roadmap-state.json` | executor | Pipeline state file for resume capability |

### Example artifact filenames (with default agents)

```
output_dir/
├── extraction.md
├── roadmap-opus-architect.md
├── roadmap-haiku-architect.md
├── diff-analysis.md
├── debate-transcript.md
├── base-selection.md
├── roadmap.md                    ← primary output
├── test-strategy.md
├── .roadmap-state.json
├── extraction.err                ← stderr from each step
├── roadmap-opus-architect.err
├── roadmap-haiku-architect.err
├── diff-analysis.err
├── debate-transcript.err
├── base-selection.err
├── roadmap.err
└── test-strategy.err
```

---

## 4) Gate Criteria and Validation

Every pipeline step has a gate that validates the output before proceeding. Gates check file existence, minimum line counts, required YAML frontmatter fields, and semantic correctness.

### Gate enforcement tiers

| Tier | Behavior |
|------|----------|
| **STRICT** | All checks must pass. Failure halts the pipeline after retry. |
| **STANDARD** | Frontmatter and line count checks. Failure halts after retry. |

### Per-step gate criteria

#### Extract gate (STRICT)
- **Min lines**: 50
- **Required frontmatter** (13 fields):
  - `spec_source`, `generated`, `generator`
  - `functional_requirements`, `nonfunctional_requirements`, `total_requirements`
  - `complexity_score`, `complexity_class`
  - `domains_detected`, `risks_identified`, `dependencies_identified`
  - `success_criteria_count`, `extraction_mode`

#### Generate gates A & B (STRICT)
- **Min lines**: 100
- **Required frontmatter**: `spec_source`, `complexity_score`, `primary_persona`
- **Semantic checks**:
  - `frontmatter_values_non_empty` — All YAML fields must have non-empty values
  - `has_actionable_content` — At least one numbered or bulleted list item

#### Diff gate (STANDARD)
- **Min lines**: 30
- **Required frontmatter**: `total_diff_points`, `shared_assumptions_count`

#### Debate gate (STRICT)
- **Min lines**: 50
- **Required frontmatter**: `convergence_score`, `rounds_completed`
- **Semantic checks**:
  - `convergence_score_valid` — Must parse as float in [0.0, 1.0]

#### Score gate (STANDARD)
- **Min lines**: 20
- **Required frontmatter**: `base_variant`, `variant_scores`

#### Merge gate (STRICT)
- **Min lines**: 150
- **Required frontmatter**: `spec_source`, `complexity_score`, `adversarial`
- **Semantic checks**:
  - `no_heading_gaps` — Heading levels increment by at most 1 (no H2 → H4 skip)
  - `cross_refs_resolve` — Internal cross-references resolve to existing headings
  - `no_duplicate_headings` — No duplicate H2 or H3 heading text

#### Test strategy gate (STANDARD)
- **Min lines**: 40
- **Required frontmatter**: `validation_milestones`, `interleave_ratio`

### Retry behavior
Each step has `retry_limit=1`, meaning **2 total attempts** before the pipeline halts. If the first attempt fails its gate, the step is re-run once. If the retry also fails, the pipeline halts with a diagnostic error message.

---

## 5) Behind the Scenes: What the Python Runtime Actually Executes

### 5.1 `superclaude roadmap run` call path

When you run:
```bash
superclaude roadmap run <SPEC_FILE> [flags]
```

the CLI flow is:
1. `commands.py::run()` parses Click options and positional argument.
2. `AgentSpec.parse()` parses each comma-separated agent spec string.
3. `RoadmapConfig` is constructed with resolved paths and options.
4. `executor.py::execute_roadmap()` is called.
5. `_build_steps()` constructs the 8-step pipeline (steps 2a+2b as a parallel group).
6. If `--dry-run`: `_dry_run_output()` prints the plan and returns.
7. If `--resume`: `_apply_resume()` skips steps with passing gates.
8. `execute_pipeline()` (from `pipeline/executor.py`) runs the steps.
9. `_save_state()` writes `.roadmap-state.json` atomically.
10. On failure: `_format_halt_output()` prints diagnostics and exits with code 1.

### 5.2 What command is run for each step

For each step, the runtime spawns a fresh Claude CLI subprocess via `ClaudeProcess`:

```bash
claude \
  --print \
  --verbose \
  --dangerously-skip-permissions \
  --no-session-persistence \
  --max-turns <N> \
  --output-format text \
  -p "<generated prompt>" \
  [--model <model-if-provided>] \
  [--file <input-path> ...]     # only if embedded inputs exceed 100KB
```

Important details:
- `--no-session-persistence` ensures step isolation (no context leakage between steps).
- `--output-format text` is used (vs `stream-json` for sprint) for gate-compatible plain text output.
- `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` environment variables are stripped from the child process to prevent nested session detection.
- stdout is redirected to the step's output file (e.g., `extraction.md`).
- stderr is redirected to a corresponding `.err` file (e.g., `extraction.err`).

### 5.3 Input embedding strategy

Each step's input files are embedded directly into the prompt as fenced code blocks:

```markdown
# /path/to/extraction.md
\`\`\`
<file contents>
\`\`\`
```

This inline embedding is used when total embedded size is ≤ 100KB (`_EMBED_SIZE_LIMIT`). For larger inputs, the executor falls back to `--file` flags passed as extra CLI arguments.

### 5.4 Output sanitization

After each step's subprocess completes successfully, `_sanitize_output()` strips any conversational preamble before the first `---` YAML frontmatter delimiter. This handles cases where the LLM produces text like "Here is the output:" before the required frontmatter.

The sanitization is atomic: it writes to a `.tmp` file then uses `os.replace()` to prevent partial file states.

### 5.5 Pipeline diagnostics injection (FR-033)

For the `extract` step only, the executor injects `pipeline_diagnostics` into the YAML frontmatter after the subprocess completes. This includes:
- `elapsed_seconds` — wall-clock duration of the extraction step
- `started_at` — ISO-8601 start timestamp
- `finished_at` — ISO-8601 completion timestamp

The LLM cannot reliably produce execution timing, so the executor injects these fields deterministically.

### 5.6 Parallel execution (steps 2a + 2b)

The generate steps run concurrently via Python threading:
- Each step runs in a daemon thread with its own `ClaudeProcess`.
- A shared `threading.Event` provides cross-cancellation: if one step fails, the other is terminated.
- Both steps must PASS before the pipeline proceeds to the diff step.
- Gate checks run independently for each step after its subprocess completes.

### 5.7 State persistence

After pipeline execution (success or failure), `.roadmap-state.json` is written atomically:

```json
{
  "schema_version": 1,
  "spec_file": "/absolute/path/to/spec.md",
  "spec_hash": "<sha256 hex>",
  "agents": [
    {"model": "opus", "persona": "architect"},
    {"model": "haiku", "persona": "architect"}
  ],
  "depth": "standard",
  "last_run": "2026-03-08T12:00:00+00:00",
  "steps": {
    "extract": {
      "status": "PASS",
      "attempt": 1,
      "output_file": "/path/to/extraction.md",
      "started_at": "...",
      "completed_at": "..."
    }
  }
}
```

### 5.8 Resume behavior

When `--resume` is passed:
1. The executor reads `.roadmap-state.json` from the output directory.
2. The spec file's SHA-256 hash is compared against `spec_hash` in the state file.
3. If the spec has changed, a warning is printed and the `extract` step is forced to re-run.
4. For each step in pipeline order, the gate is re-evaluated against the existing output file:
   - If the gate passes → step is skipped (logged as `[roadmap] Skipping <id> (gate passes)`).
   - If the gate fails → this step and all subsequent steps are re-run.
5. For parallel groups, all steps in the group must pass their gates to be skipped.
6. If all steps already pass: `[roadmap] All steps already pass gates. Nothing to do.`

### 5.9 Halt diagnostics

When a step fails after exhausting retries, the executor prints structured diagnostics:

```
ERROR: Roadmap pipeline halted at step 'debate' (attempt 2/2)
  Gate failure: convergence_score must be a float in [0.0, 1.0]
  Output file: /path/to/debate-transcript.md
  Output size: 1234 bytes (45 lines)
  Step timeout: 600s | Elapsed: 120s

Completed steps: extract (PASS, attempt 1), generate-opus-architect (PASS, attempt 1), ...
Failed step:     debate (FAIL, attempt 2)
Skipped steps:   score, merge, test-strategy

To retry from this step:
  superclaude roadmap run /path/to/spec.md --resume

To inspect the failing output:
  cat /path/to/debate-transcript.md
```

---

## 6) Depth Modes: Debate Configuration

The `--depth` flag controls how many rounds of adversarial debate occur in step 4:

### `quick` (1 round)
Each perspective states its position on the key divergence points, then a convergence assessment is provided.

**Use when**: Rapid iteration, small specs, or when variants are expected to be similar.

### `standard` (2 rounds) — Default
- **Round 1**: Each perspective states initial positions on divergence points.
- **Round 2**: Each perspective rebuts the other's key claims.
- Then a convergence assessment is provided.

**Use when**: Most specifications. Provides good coverage without excessive token consumption.

### `deep` (3 rounds)
- **Round 1**: Each perspective states initial positions on divergence points.
- **Round 2**: Each perspective rebuts the other's key claims.
- **Round 3**: Final synthesis — each perspective identifies concessions and remaining disagreements.
- Then a convergence assessment is provided.

**Use when**: Critical specifications, security-sensitive projects, or when maximum deliberation quality is needed.

---

## 7) Data Models Reference

### AgentSpec
```python
@dataclass
class AgentSpec:
    model: str        # e.g., "opus", "sonnet", "haiku"
    persona: str      # e.g., "architect", "security", "qa"

    @classmethod
    def parse(cls, spec: str) -> AgentSpec:
        # "opus:architect" → AgentSpec("opus", "architect")
        # "haiku"          → AgentSpec("haiku", "architect")

    @property
    def id(self) -> str:
        # "opus-architect"
```

### RoadmapConfig (extends PipelineConfig)

```python
@dataclass
class RoadmapConfig(PipelineConfig):
    spec_file: Path                    # Resolved spec file path
    agents: list[AgentSpec]            # Default: [opus:architect, haiku:architect]
    depth: "quick"|"standard"|"deep"   # Default: "standard"
    output_dir: Path                   # Resolved output directory

# Inherited from PipelineConfig:
    work_dir: Path          # Default: Path(".")
    dry_run: bool           # Default: False
    max_turns: int          # Default: 100
    model: str              # Default: "" (use per-agent models)
    permission_flag: str    # Default: "--dangerously-skip-permissions"
    debug: bool             # Default: False
    grace_period: int       # Default: 0
```

### GateCriteria

```python
@dataclass
class GateCriteria:
    required_frontmatter_fields: list[str]   # YAML fields that must exist
    min_lines: int                            # Minimum output file lines
    enforcement_tier: "STRICT"|"STANDARD"     # Gate strictness
    semantic_checks: list[SemanticCheck]       # Python-level content checks
```

### SemanticCheck

```python
@dataclass
class SemanticCheck:
    name: str                          # Check identifier
    check_fn: Callable[[str], bool]    # Pure function: content → pass/fail
    failure_message: str               # Human-readable failure reason
```

---

## 8) End-to-End Workflow: Spec → Roadmap → Tasklist → Execution

The roadmap CLI is Stage B in the full release pipeline.

### Stage A: Spec (requirements source)
Create a specification markdown file with project requirements, constraints, and acceptance criteria.

### Stage B: Roadmap (adversarial generation) ← **This tool**
```bash
superclaude roadmap run spec.md --depth standard
```
Produces `roadmap.md` (merged, adversarially validated) + `test-strategy.md`.

### Stage C: Tasklist (execution plan)
```bash
# Use /sc:tasklist to generate Sprint CLI-compatible phase files from the roadmap
```
Produces `tasklist-index.md` + phase files.

### Stage D: Sprint execution
```bash
superclaude sprint run .dev/releases/current/tasklist-index.md
```
Executes the phases with supervised Claude sessions.

### Stage E: Resume on halt
```bash
# Roadmap level
superclaude roadmap run spec.md --resume

# Sprint level
superclaude sprint run .dev/releases/current/tasklist-index.md --start <halt_phase>
```

---

## 9) Practical Use Cases

### Use case 1: Standard roadmap generation
```bash
superclaude roadmap run .dev/releases/current/v2.20/spec.md
```
Runs the full 8-step pipeline with default agents (`opus:architect` + `haiku:architect`) and standard depth (2 debate rounds). Artifacts written to the spec's parent directory.

### Use case 2: Security-focused roadmap
```bash
superclaude roadmap run spec.md --agents opus:architect,sonnet:security --depth deep
```
Uses a security persona for the second variant. Deep debate ensures thorough adversarial review of security concerns.

### Use case 3: Quick iteration roadmap
```bash
superclaude roadmap run spec.md --agents haiku:architect,haiku:qa --depth quick
```
Uses faster (cheaper) models with a single debate round for rapid prototype roadmaps.

### Use case 4: Validate pipeline plan before execution
```bash
superclaude roadmap run spec.md --dry-run
```
Prints the step plan with gate criteria and timeout budgets. No subprocesses are launched. Use this to verify configuration before committing to a full run.

**Sample dry-run output**:
```
Step 1: extract
  Output: /path/to/extraction.md
  Timeout: 300s
  Gate tier: STRICT
  Gate min_lines: 50
  Gate frontmatter: spec_source, generated, generator, ...

Step 2 (parallel): generate-opus-architect
  Output: /path/to/roadmap-opus-architect.md
  Timeout: 900s
  Model: opus
  Gate tier: STRICT
  Gate min_lines: 100
  Gate frontmatter: spec_source, complexity_score, primary_persona
  Semantic checks: frontmatter_values_non_empty, has_actionable_content

...
```

### Use case 5: Resume after failure
```bash
superclaude roadmap run spec.md --resume
```
Skips steps whose outputs already pass their gates. Re-runs from the first failing step. Detects spec changes and forces re-extraction if the spec has been modified.

### Use case 6: Custom output directory for release management
```bash
superclaude roadmap run spec.md --output .dev/releases/current/v2.20-feature/
```
All artifacts are written to the specified directory, keeping releases organized.

### Use case 7: Override model globally
```bash
superclaude roadmap run spec.md --model claude-sonnet-4-20250514
```
Forces all steps (not just generate steps) to use the specified model. Useful for testing with a specific model version.

### Use case 8: Debug a failing pipeline
```bash
superclaude roadmap run spec.md --debug --max-turns 200
```
Enables debug logging to `<output_dir>/roadmap-debug.log` and increases max turns for steps that might need more interaction. Inspect `.err` files for subprocess stderr output.

---

## 10) Prompt Architecture

Each pipeline step uses a specialized prompt builder (defined in `prompts.py`). All prompt functions are **pure** — they accept concrete values, return strings, and perform no I/O (NFR-004).

### Common output format block
All prompts include a critical output format instruction:
```
CRITICAL: Your response MUST begin with YAML frontmatter (--- delimited block).
Do NOT include any text, preamble, or commentary before the opening ---.
```
This ensures gate validation can parse the output correctly.

### Prompt builders

| Builder | Step | Role instruction | Key output requirements |
|---------|------|-----------------|------------------------|
| `build_extract_prompt` | extract | "Requirements extraction specialist" | 13 frontmatter fields + 8 body sections |
| `build_generate_prompt` | generate | "{persona} specialist creating a project roadmap" | 3 frontmatter fields + 6 roadmap sections |
| `build_diff_prompt` | diff | "Comparative analysis specialist" | 2 frontmatter fields + 4 analysis sections |
| `build_debate_prompt` | debate | "Structured debate facilitator" | 2 frontmatter fields + debate transcript |
| `build_score_prompt` | score | "Objective evaluation specialist" | 2 frontmatter fields + scoring analysis |
| `build_merge_prompt` | merge | "Synthesis specialist" | 3 frontmatter fields + complete roadmap |
| `build_test_strategy_prompt` | test-strategy | "Test strategy specialist" | 2 frontmatter fields + test plan |

---

## 11) Error Handling and Process Management

### Process lifecycle
Each step uses `ClaudeProcess` from the shared pipeline module:
- Subprocess is launched with `subprocess.Popen` and process group isolation (`os.setpgrp` on Unix).
- The executor polls for cancellation every 1 second while the subprocess runs.
- Timeout detection: `exit_code == 124` maps to `StepStatus.TIMEOUT`.
- Non-zero exit (except 124): maps to `StepStatus.FAIL`.
- Success: maps to `StepStatus.PASS` (gate check runs next).

### Cancellation
- External cancellation is supported via a `cancel_check` callback.
- For parallel steps, cross-cancellation ensures if one step fails, the other is terminated.

### Graceful shutdown
`ClaudeProcess.terminate()` follows an escalation path:
1. SIGTERM to process group (or process on non-Unix)
2. Wait 10 seconds
3. SIGKILL if still alive
4. Wait 5 seconds for final cleanup

### Non-Unix portability
- Process group operations (`os.setpgrp`, `os.killpg`) are guarded with `hasattr()` checks.
- Fallback uses `process.terminate()` / `process.kill()` on non-Unix environments.

---

## 12) Integration with Slash Commands and Skills

The roadmap CLI has two integration surfaces:

### Python CLI (this tool)
```bash
superclaude roadmap run spec.md [options]
```
Deterministic, programmatic pipeline execution with subprocess orchestration.

### Slash command `/sc:roadmap`
The `/sc:roadmap` slash command (defined in `src/superclaude/commands/roadmap.md`) invokes the `sc-roadmap-protocol` skill for inference-based roadmap generation within a Claude Code session. This is the interactive counterpart to the CLI tool.

**Key differences**:
| Aspect | CLI (`superclaude roadmap run`) | Slash command (`/sc:roadmap`) |
|--------|------|------|
| Execution | Subprocess-per-step, automated | Single Claude session, interactive |
| Gate validation | Automated, Python-based | Inference-based within session |
| Resume | `--resume` flag with state file | Session persistence |
| Best for | CI/CD, unattended runs, reproducibility | Interactive exploration, quick iteration |

---

## 13) Quick Command Cheat Sheet

```bash
# Basic roadmap generation
superclaude roadmap run spec.md

# Custom agents
superclaude roadmap run spec.md --agents sonnet:security,haiku:qa

# Deep debate (3 rounds)
superclaude roadmap run spec.md --depth deep

# Quick debate (1 round)
superclaude roadmap run spec.md --depth quick

# Custom output directory
superclaude roadmap run spec.md --output .dev/releases/current/v2.20/

# Dry-run (plan only)
superclaude roadmap run spec.md --dry-run

# Resume from failure
superclaude roadmap run spec.md --resume

# Override model globally
superclaude roadmap run spec.md --model claude-sonnet-4-20250514

# Increase max turns
superclaude roadmap run spec.md --max-turns 200

# Debug mode
superclaude roadmap run spec.md --debug

# Full production run
superclaude roadmap run spec.md \
  --agents opus:architect,sonnet:security \
  --depth deep \
  --output .dev/releases/current/v2.20/ \
  --max-turns 150 \
  --debug
```

---

## 14) Troubleshooting Checklist

### Before running
- [ ] Spec file exists and is readable markdown
- [ ] Output directory is writable (or will be created)
- [ ] `claude` binary is in `PATH`
- [ ] Agent model names are valid (opus, sonnet, haiku, or full model IDs)

### After a failure
- [ ] Check the halt diagnostic output for the failing step and gate reason
- [ ] Inspect the `.err` file for the failing step (subprocess stderr)
- [ ] Inspect the output file — is the YAML frontmatter present and correct?
- [ ] Check if preamble stripping failed (conversational text before `---`)
- [ ] For gate failures: verify required frontmatter fields and minimum line counts
- [ ] For semantic check failures: review the specific check (e.g., heading gaps, empty values)
- [ ] Use `--resume` to retry from the failing step without re-running passed steps
- [ ] Use `--debug` for detailed executor logging

### Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Step 'extract' exited with code 1` | Claude CLI error or missing permissions | Check `.err` file; verify `claude` works standalone |
| `frontmatter_values_non_empty` failure | LLM produced empty YAML field values | Re-run step (retry usually fixes) |
| `convergence_score must be a float in [0.0, 1.0]` | LLM output invalid score format | Re-run; consider `--depth quick` if consistently failing |
| `Heading level gap detected` | Merge produced H2→H4 jump | Re-run merge step; check variant heading structure |
| `spec-file has changed since last run` (with `--resume`) | Spec was edited after previous run | Expected behavior — extract is forced to re-run |
| All steps skipped with `--resume` | All outputs already pass gates | Pipeline already complete; inspect `roadmap.md` |

---

## 15) Notes for Pipeline Operators

- The roadmap CLI is the **generation** layer. It produces `roadmap.md` and `test-strategy.md` that feed into the **tasklist** layer (`/sc:tasklist`) and then the **execution** layer (`superclaude sprint run`).
- Use `--dry-run` as an automated gate between spec authoring and pipeline execution.
- Use `--resume` for efficient iteration: edit spec → re-run → only changed steps execute.
- The `.roadmap-state.json` file is the source of truth for resume decisions. Delete it to force a full re-run.
- Agent persona choice significantly affects roadmap quality. Pair complementary personas (e.g., `architect` + `security`, `architect` + `qa`) for maximum adversarial value.
- Deep debate mode produces higher quality but costs ~3x more tokens than quick mode.
- All outputs use YAML frontmatter for machine parseability. Downstream tools (tasklist generator) rely on this structure.
