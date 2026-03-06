---
title: "Roadmap Validate — Post-Pipeline Reflection & Adversarial Validation"
version: "1.0.0"
status: draft
feature_id: FR-050
parent_feature: roadmap-pipeline
complexity_score: 0.65
complexity_class: moderate
target_release: v2.19
authors: [user, claude]
created: 2026-03-06
---

# FR-050: `superclaude roadmap validate`

## 1. Problem Statement

The roadmap pipeline (8 steps: extract → generate ×2 → diff → debate → score → merge → test-strategy) produces artifacts that pass per-step file-on-disk gates. However, these gates only verify **per-file structural properties** (frontmatter field existence, min line count, heading hierarchy). They do **not** verify:

1. **Cross-file consistency** — test-strategy milestone references match roadmap milestones
2. **Deliverable ID uniqueness** — no duplicate D-xxxx IDs across milestones
3. **Bidirectional traceability** — every deliverable → requirement AND every requirement → deliverable
4. **Milestone DAG validity** — no circular dependencies, all dependency refs resolve
5. **Tasklist parseability** — roadmap content is parseable into items by sc:tasklist's heading/bullet/numbered-list splitter
6. **Content-level interleave** — test activities are actually interleaved with milestones, not back-loaded

Without this validation, users discover these issues only when `sc:tasklist` fails or produces a broken tasklist — wasting 15-30 minutes + tokens.

## 2. Solution Overview

Add a `superclaude roadmap validate` subcommand that runs a structured Claude subprocess to validate the merged roadmap against 7 dimensions. Optionally runs multiple agents in parallel with adversarial merge for higher-confidence results.

### 2.1 CLI Surface

```
superclaude roadmap validate <output-dir> [--agents model:persona,...] [--model MODEL] [--max-turns N] [--debug]
superclaude roadmap run <spec-file> [--no-validate] [...]   # validate is ON by default
```

### 2.2 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Subprocess vs in-session | Subprocess | Context independence eliminates confirmation bias |
| Always-on vs opt-in | Always-on (`--no-validate` to skip) | ROI positive even at 20% catch rate |
| Blocking issues behavior | Warn, don't exit non-zero | User may want to proceed with known issues |
| Agent spec format | Same `model:persona` as `roadmap run` | Consistency, code reuse |
| Report format | Structured MD with YAML frontmatter | Machine-readable + human-readable |

## 3. Functional Requirements

### FR-050.1: `superclaude roadmap validate` Subcommand

**Input**: `<output-dir>` — path to directory containing roadmap pipeline outputs.

**Required files in output-dir**:
- `roadmap.md` (merged roadmap from step 6)
- `test-strategy.md` (from step 7)
- `extraction.md` (from step 1)

**Behavior**: Validates presence of all 3 required files, then runs validation pipeline.

### FR-050.2: Single-Agent Validation (default)

When `--agents` is not specified or has exactly 1 agent:

```
Step layout:
  reflect    (sequential, single subprocess)
```

Produces:
```
<output-dir>/validate/
└── validation-report.md
```

### FR-050.3: Multi-Agent Adversarial Validation

When `--agents` specifies 2+ agents (e.g., `--agents opus,haiku`):

```
Step layout:
  [reflect-opus, reflect-haiku]   (parallel)
              ↓
      adversarial-merge            (sequential)
```

Produces:
```
<output-dir>/validate/
├── reflect-opus-architect.md
├── reflect-haiku-architect.md
└── validation-report.md
```

### FR-050.4: Auto-Invocation from `roadmap run`

After the 8-step pipeline succeeds, `execute_roadmap()` automatically invokes `execute_validate()` unless `--no-validate` is passed.

The validate step inherits `--agents`, `--model`, `--max-turns`, and `--debug` from the parent `roadmap run` invocation.

Validation only runs after full pipeline success. If `--resume` is used and some steps were skipped but all gates pass, validation still runs on the final artifacts. If the pipeline halts on a failed step, validation is skipped (no artifacts to validate).

### FR-050.5: Validation Dimensions

The reflection prompt covers 7 dimensions. Each finding is classified by severity.

| # | Dimension | What it checks | Severity if failed |
|---|-----------|---------------|-------------------|
| 1 | Schema | YAML frontmatter fields present, non-empty, correctly typed | BLOCKING |
| 2 | Structure | Milestone DAG acyclic, all refs resolve, no duplicate deliverable IDs, heading hierarchy valid | BLOCKING |
| 3 | Traceability | Every deliverable → requirement AND every requirement → deliverable | BLOCKING |
| 4 | Cross-file | test-strategy milestone refs match roadmap milestones | BLOCKING |
| 5 | Interleave | interleave_ratio in [0.1, 1.0], test activities not back-loaded | WARNING |
| 6 | Decomposition | No compound deliverables that would need splitting by sc:tasklist | WARNING |
| 7 | Parseability | Content parseable into items via headings, bullets, numbered lists | BLOCKING |

### FR-050.6: Validation Report Schema

`validation-report.md` YAML frontmatter:

```yaml
---
blocking_issues_count: <int>
warnings_count: <int>
info_count: <int>
tasklist_ready: <true|false>
validation_agents: <comma-separated agent IDs>
validation_mode: <single|adversarial>
---
```

Body structure:

```markdown
# Validation Report

## Summary
<1-paragraph summary of findings>

## Blocking Issues
### B-001: <title>
- **Dimension**: <schema|structure|traceability|cross-file|parseability>
- **Location**: <file:line or file:section>
- **Detail**: <description>
- **Fix**: <recommended action>

## Warnings
### W-001: <title>
...

## Info
### I-001: <title>
...

## Validation Metadata
- Agents used: <list>
- Mode: single | adversarial
- Inputs validated: roadmap.md, test-strategy.md, extraction.md
```

### FR-050.7: Adversarial Merge Report (Multi-Agent Only)

When multi-agent mode is used, the merge step adds a section:

```markdown
## Agent Agreement Analysis
| Finding | Agent A | Agent B | Resolution |
|---------|---------|---------|------------|
| B-001   | FOUND   | FOUND   | BOTH_AGREE — high confidence |
| B-002   | FOUND   | —       | ONLY_A — review recommended |
| W-001   | —       | FOUND   | ONLY_B — likely structural |
| W-002   | FOUND   | FOUND (different severity) | CONFLICT — escalated to BLOCKING |
```

## 4. Architecture

### 4.1 New Files

```
src/superclaude/cli/roadmap/
├── validate_executor.py    # execute_validate(), _build_validate_steps()
├── validate_gates.py       # REFLECT_GATE, ADVERSARIAL_MERGE_GATE
└── validate_prompts.py     # build_reflect_prompt(), build_adversarial_merge_prompt()
```

### 4.2 Modified Files

```
src/superclaude/cli/roadmap/
├── commands.py             # Add 'validate' subcommand, add --no-validate to 'run'
├── executor.py             # Call execute_validate() after pipeline success
└── models.py               # Add ValidateConfig dataclass
```

### 4.3 Module Dependency Graph

```
commands.py
  ├── executor.py (execute_roadmap)
  │     ├── pipeline/executor.py (execute_pipeline)
  │     └── validate_executor.py (execute_validate)  ← NEW
  │           ├── pipeline/executor.py (execute_pipeline, reused)
  │           ├── validate_gates.py ← NEW
  │           └── validate_prompts.py ← NEW
  └── validate_executor.py (execute_validate, direct for 'validate' subcommand)
```

### 4.4 Data Model

```python
@dataclass
class ValidateConfig(PipelineConfig):
    """Configuration for the validate sub-pipeline."""
    output_dir: Path          # Parent dir containing roadmap.md etc.
    validate_dir: Path        # output_dir / "validate"
    agents: list[AgentSpec]
    roadmap_file: Path        # output_dir / "roadmap.md"
    test_strategy_file: Path  # output_dir / "test-strategy.md"
    extraction_file: Path     # output_dir / "extraction.md"
```

### 4.5 Gate Criteria

```python
# --- Semantic check functions (pure: content -> bool) ---

# Reuse from roadmap/gates.py (no circular dependency: validate → roadmap, not vice versa)
from .gates import _frontmatter_values_non_empty


def _has_agreement_table(content: str) -> bool:
    """Verify adversarial merge report contains Agent Agreement Analysis table."""
    marker = "## Agent Agreement Analysis"
    if marker not in content:
        return False
    after_marker = content.split(marker, 1)[1][:500]
    return "|" in after_marker


# --- Gate instances ---

REFLECT_GATE = GateCriteria(
    required_frontmatter_fields=[
        "blocking_issues_count",
        "warnings_count",
        "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="Validation report has empty frontmatter values",
        ),
    ],
)

ADVERSARIAL_MERGE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "blocking_issues_count",
        "warnings_count",
        "tasklist_ready",
        "validation_mode",
        "validation_agents",
    ],
    min_lines=30,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="Merged validation report has empty frontmatter values",
        ),
        SemanticCheck(
            name="has_agreement_table",
            check_fn=_has_agreement_table,
            failure_message="Adversarial merge report missing Agent Agreement Analysis table",
        ),
    ],
)
```

### 4.6 Implementation Order

```
1. models.py              — add ValidateConfig (other files depend on it)
2. validate_gates.py      — gate criteria + semantic checks (no deps beyond pipeline/models)
   validate_prompts.py    — prompt builders (no deps beyond models)    [parallel with gates]
3. validate_executor.py   — _build_validate_steps() + execute_validate() (depends on gates + prompts)
4. commands.py            — add 'validate' subcommand + --no-validate flag (depends on executor)
   executor.py            — call execute_validate() after pipeline success [parallel with commands]
```

## 5. Prompt Specifications

### 5.1 Reflection Prompt

```python
def build_reflect_prompt(
    agent: AgentSpec,
    roadmap_file: Path,
    test_strategy_file: Path,
    extraction_file: Path,
) -> str:
```

The prompt instructs Claude to:

1. Read all 3 input files
2. Validate across 7 dimensions (see FR-050.5)
3. Classify each finding as BLOCKING / WARNING / INFO
4. Output structured report with YAML frontmatter (see FR-050.6)
5. Set `tasklist_ready: true` only if `blocking_issues_count == 0`

Key prompt constraints:
- "You are a validation specialist. You did NOT generate these artifacts."
- "Be thorough but precise — false positives waste user time."
- "Every finding must cite a specific location (file:line or file:section)."

### 5.2 Adversarial Merge Prompt

```python
def build_adversarial_merge_prompt(
    reflect_files: list[Path],
    roadmap_file: Path,
) -> str:
```

The prompt instructs Claude to:

1. Read all reflection reports
2. Deduplicate findings (same location + same issue = BOTH_AGREE)
3. Categorize unique findings as ONLY_A / ONLY_B
4. For severity conflicts, evaluate evidence and escalate to higher severity
5. Produce merged validation-report.md with Agent Agreement Analysis table
6. Recalculate `blocking_issues_count` and `tasklist_ready` from merged findings

## 6. Step Construction

### 6.1 Single-Agent Steps

```python
def _build_validate_steps(config: ValidateConfig) -> list[Step | list[Step]]:
    if len(config.agents) == 1:
        return [
            Step(
                id="reflect",
                prompt=build_reflect_prompt(config.agents[0], ...),
                output_file=config.validate_dir / "validation-report.md",
                gate=REFLECT_GATE,
                timeout_seconds=300,
                inputs=[config.roadmap_file, config.test_strategy_file, config.extraction_file],
                retry_limit=1,
                model=config.agents[0].model,
            ),
        ]
```

### 6.2 Multi-Agent Steps

```python
    else:
        reflect_steps = [
            Step(
                id=f"reflect-{agent.id}",
                prompt=build_reflect_prompt(agent, ...),
                output_file=config.validate_dir / f"reflect-{agent.id}.md",
                gate=REFLECT_GATE,
                timeout_seconds=300,
                inputs=[config.roadmap_file, config.test_strategy_file, config.extraction_file],
                retry_limit=1,
                model=agent.model,
            )
            for agent in config.agents
        ]
        reflect_files = [s.output_file for s in reflect_steps]

        return [
            reflect_steps,  # parallel group
            Step(
                id="adversarial-merge",
                prompt=build_adversarial_merge_prompt(reflect_files, config.roadmap_file),
                output_file=config.validate_dir / "validation-report.md",
                gate=ADVERSARIAL_MERGE_GATE,
                timeout_seconds=300,
                inputs=reflect_files + [config.roadmap_file],
                retry_limit=1,
            ),
        ]
```

## 7. CLI Integration

### 7.1 `roadmap run` Changes

```python
@roadmap_group.command()
# ... existing options ...
@click.option(
    "--no-validate",
    is_flag=True,
    help="Skip post-pipeline validation step.",
)
def run(spec_file, agents, ..., no_validate, ...):
    ...
    execute_roadmap(config, resume=resume)

    if not no_validate:
        execute_validate(validate_config)
```

### 7.2 New `roadmap validate` Subcommand

```python
@roadmap_group.command()
@click.argument("output_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--agents", default="opus:architect",
              help="Comma-separated agent specs. Use 2+ for adversarial mode.")
# NOTE: Default is single-agent for cost efficiency when run standalone.
# When auto-invoked from `roadmap run`, inherits the parent's --agents
# (default: opus:architect,haiku:architect = adversarial mode).
# To match `roadmap run` behavior: --agents opus:architect,haiku:architect
@click.option("--model", default="", help="Override model for all steps.")
@click.option("--max-turns", type=int, default=50)
@click.option("--debug", is_flag=True)
def validate(output_dir, agents, model, max_turns, debug):
    """Validate roadmap artifacts for sc:tasklist readiness."""
    ...
```

## 8. Output Behavior

### 8.1 Success (no blocking issues)

```
[validate] Starting validation (1 agent: opus-architect)
[validate] Step reflect  PASS (attempt 1, 45s)
[validate] Validation complete: 0 blocking, 2 warnings, 1 info
[validate] tasklist_ready: true
[validate] Report: ./output/validate/validation-report.md
```

### 8.2 Blocking Issues Found (warn, don't fail)

```
[validate] Starting validation (2 agents: opus-architect, haiku-architect)
[validate] Step reflect-opus-architect  PASS (attempt 1, 52s)
[validate] Step reflect-haiku-architect  PASS (attempt 1, 23s)
[validate] Step adversarial-merge  PASS (attempt 1, 38s)
[validate] Validation complete: 3 blocking, 1 warning, 0 info
[validate] WARNING: 3 blocking issues found — roadmap may not be sc:tasklist-ready
[validate]   B-001: Duplicate deliverable ID D-0003 in milestones 2 and 4
[validate]   B-002: test-strategy references milestone "M-06" not found in roadmap
[validate]   B-003: Requirement FR-007 has no corresponding deliverable
[validate] Report: ./output/validate/validation-report.md
```

### 8.3 Gate Failure (validation subprocess itself failed)

```
[validate] Step reflect  FAIL (attempt 2, 120s)
           Reason: Missing required frontmatter field 'blocking_issues_count'
WARNING: Validation step failed — validation-report.md may be incomplete.
         Inspect: ./output/validate/validation-report.md
```

## 9. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-050.1 | Validate step adds ≤10% wall time to pipeline | ≤2 min for single agent |
| NFR-050.2 | No imports from validate_* in pipeline/* modules | Maintains NFR-007 |
| NFR-050.3 | validate subcommand works independently of `roadmap run` | Standalone invocation |
| NFR-050.4 | Reuses existing pipeline infrastructure (execute_pipeline, ClaudeProcess, gate_passed) | Zero new infra |
| NFR-050.5 | Single-agent and multi-agent share identical code path | List of 1 vs list of N |

## 10. Test Plan

### 10.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `test_validate_config_from_output_dir` | `tests/roadmap/test_validate_models.py` | Config construction, file resolution |
| `test_build_validate_steps_single` | `tests/roadmap/test_validate_executor.py` | Single-agent produces 1 step |
| `test_build_validate_steps_multi` | `tests/roadmap/test_validate_executor.py` | Multi-agent produces parallel group + merge |
| `test_reflect_gate_criteria` | `tests/roadmap/test_validate_gates.py` | Gate checks frontmatter fields |
| `test_merge_gate_has_agreement_table` | `tests/roadmap/test_validate_gates.py` | Semantic check for agreement table |
| `test_reflect_prompt_contains_dimensions` | `tests/roadmap/test_validate_prompts.py` | All 7 dimensions present in prompt |
| `test_merge_prompt_contains_categories` | `tests/roadmap/test_validate_prompts.py` | BOTH_AGREE/ONLY_A/ONLY_B in prompt |

### 10.2 Integration Tests

| Test | Validates |
|------|-----------|
| `test_validate_dry_run` | `--dry-run` prints plan without launching subprocesses |
| `test_validate_missing_files` | Exits with clear error when roadmap.md/test-strategy.md missing |
| `test_run_with_no_validate` | `--no-validate` skips validation step |
| `test_run_auto_validates` | Default `roadmap run` invokes validation after pipeline success |

### 10.3 End-to-End Tests (manual)

1. Run `superclaude roadmap run spec.md` → verify validate step runs and produces report
2. Run `superclaude roadmap validate ./output/ --agents opus,haiku` → verify parallel reflect + merge
3. Introduce a known issue (duplicate D-ID) → verify it appears as BLOCKING in report
4. Run with `--no-validate` → verify validate step is skipped

## 11. Migration & Rollout

- **No breaking changes** — `--no-validate` preserves previous behavior
- **Default change** — `roadmap run` now runs validation by default (additive)
- **New subcommand** — `roadmap validate` is purely additive
- **No schema migration** — `.roadmap-state.json` unchanged (validate state is separate)

## 12. Open Items

None — all questions from brainstorming phase resolved, all validation findings addressed:
1. Always-on: yes (`--no-validate` to skip)
2. Single-agent format: structured subprocess report
3. Blocking issues: warn, don't exit non-zero
4. Agent spec format: same `model:persona` as `roadmap run`

### Validation Fixes Applied (v1.0.1)
- **B-004 fixed**: Added `_has_agreement_table` semantic check definition (section 4.5)
- **W-001 fixed**: Specified import path for `_frontmatter_values_non_empty` reuse (section 4.5)
- **W-002 fixed**: Added explicit implementation dependency order (section 4.6)
- **W-003 fixed**: Documented default agent count mismatch between invocation modes (section 7.2)
- **I-002 fixed**: Explicit resume + validation interaction behavior (section FR-050.4)
