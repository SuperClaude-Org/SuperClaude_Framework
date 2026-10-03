# Python API Reference

Complete reference for the `superclaude` Python package (`src/superclaude/`).

**Audience**: Developers using SuperClaude's Python API directly — writing tests with the pytest plugin, embedding PM Agent patterns in tooling, or extending the CLI.

**Installation**:

```bash
pipx install superclaude      # CLI usage
uv pip install superclaude    # Library / pytest plugin usage
```

---

## Table of Contents

- [Top-Level Package (`superclaude`)](#top-level-package-superclaude)
- [PM Agent (`superclaude.pm_agent`)](#pm-agent-superclaudepm_agent)
  - [ConfidenceChecker](#confidencechecker)
  - [SelfCheckProtocol](#selfcheckprotocol)
  - [ReflexionPattern](#reflexionpattern)
  - [TokenBudgetManager](#tokenbudgetmanager)
- [Execution Engine (`superclaude.execution`)](#execution-engine-superclaudeexecution)
  - [High-Level Functions](#high-level-functions)
  - [ParallelExecutor](#parallelexecutor)
  - [ReflectionEngine](#reflectionengine)
  - [SelfCorrectionEngine](#selfcorrectionengine)
- [Pytest Plugin (`superclaude.pytest_plugin`)](#pytest-plugin-superclaudepytest_plugin)
- [CLI (`superclaude.cli`)](#cli-superclaudecli)
- [Scripts (`superclaude.scripts`)](#scripts-superclaudescripts)

---

## Top-Level Package (`superclaude`)

The package root re-exports the three PM Agent patterns:

```python
from superclaude import ConfidenceChecker, SelfCheckProtocol, ReflexionPattern, __version__
```

| Export | Type | Purpose |
|---|---|---|
| `ConfidenceChecker` | class | Pre-implementation confidence assessment |
| `SelfCheckProtocol` | class | Post-implementation evidence-based validation |
| `ReflexionPattern` | class | Error learning and prevention |
| `__version__` | str | Package version string |

---

## PM Agent (`superclaude.pm_agent`)

Three patterns that bracket every implementation: check confidence **before**, validate with evidence **after**, and learn from any error in between.

### ConfidenceChecker

`superclaude.pm_agent.confidence.ConfidenceChecker`

Pre-implementation confidence assessment. Prevents wrong-direction execution by scoring readiness before any code is written. Token budget: 100–200 tokens; ROI: 25–250x savings when a wrong direction is stopped early.

#### Methods

**`assess(context: Dict[str, Any]) -> float`**

Assess confidence level from 0.0 to 1.0 using five weighted investigation checks:

| Check | Weight |
|---|---|
| No duplicate implementations | 25% |
| Architecture compliance | 25% |
| Official documentation verified | 20% |
| Working OSS implementations referenced | 15% |
| Root cause identified | 15% |

- **Args**: `context` — dict with task details (e.g., `has_official_docs`, `no_duplicates`, `root_cause_identified`)
- **Returns**: `float` — 0.0 (no confidence) to 1.0 (absolute certainty)

**`get_recommendation(confidence: float) -> str`**

Map a confidence score to a recommended action.

- **Args**: `confidence` — score from `assess()`
- **Returns**: `str` — recommended action

#### Decision thresholds

| Score | Action |
|---|---|
| ≥ 0.90 | Proceed immediately |
| 0.70 – 0.89 | Present alternatives to the user |
| < 0.70 | Stop and request clarification |

#### Example

```python
from superclaude import ConfidenceChecker

checker = ConfidenceChecker()
confidence = checker.assess({
    "task_name": "add-retry-logic",
    "has_official_docs": True,
    "root_cause_identified": True,
})

if confidence >= 0.9:
    pass  # High confidence — proceed
elif confidence >= 0.7:
    pass  # Medium — present options to user
else:
    print(checker.get_recommendation(confidence))  # Low — stop and clarify
```

---

### SelfCheckProtocol

`superclaude.pm_agent.self_check.SelfCheckProtocol`

Post-implementation validation that prevents hallucinated "done" claims by requiring evidence. Detection rate: 94% (Reflexion benchmark). Token budget: 200–2,500 depending on complexity.

The Four Questions:

1. **Are all tests passing?** — run tests, show actual results
2. **Are all requirements met?** — compare implementation vs. requirements
3. **No assumptions without verification?** — were official docs consulted?
4. **Is there evidence?** — test output, file list, lint/typecheck results

#### Methods

**`validate(implementation: Dict[str, Any]) -> Tuple[bool, List[str]]`**

Run self-check validation against an implementation record.

- **Args**: `implementation` — dict containing:
  - `tests_passed` (bool) — whether tests passed
  - `test_output` (str) — actual test output
  - `requirements` (List[str]) — required items
  - `requirements_met` (List[str]) — items actually met
  - `assumptions` (List[str]) — assumptions made
  - `assumptions_verified` (List[str]) — assumptions verified
  - `evidence` (Dict) — `test_results`, `code_changes`, `validation`
- **Returns**: `(passed: bool, issues: List[str])`

**`format_report(passed: bool, issues: List[str]) -> str`**

Format the validation result as a human-readable report.

#### Example

```python
from superclaude import SelfCheckProtocol

protocol = SelfCheckProtocol()
passed, issues = protocol.validate({
    "tests_passed": True,
    "test_output": "34 passed in 1.2s",
    "requirements": ["retry", "backoff"],
    "requirements_met": ["retry", "backoff"],
    "assumptions": [],
    "assumptions_verified": [],
    "evidence": {"test_results": "...", "code_changes": ["client.py"], "validation": "ruff: ok"},
})
print(protocol.format_report(passed, issues))
```

---

### ReflexionPattern

`superclaude.pm_agent.reflexion.ReflexionPattern`

Error learning and prevention. Records errors with solutions so recurring errors resolve instantly (cache hit: 0 tokens; cache miss: 1–2K tokens). Error recurrence rate < 10%, solution reuse rate > 90%.

Storage locations:

- `docs/memory/solutions_learned.jsonl` — append-only solution log
- `docs/mistakes/[feature]-[date].md` — detailed per-mistake analysis

#### Methods

**`get_solution(error_info: Dict[str, Any]) -> Optional[Dict[str, Any]]`**

Look up a known solution for a similar error. Strategy: (1) mindbase semantic search if available, (2) grep-based text search fallback, (3) `None` if no match.

**`record_error(error_info: Dict[str, Any]) -> None`**

Record an error (and optionally its solution) for future learning.

- **Args**: `error_info` — dict with `test_name`, `error_type`, `error_message`, `traceback`, and optionally `solution` and `root_cause`

**`get_statistics() -> Dict[str, Any]`**

Return statistics: `total_errors`, `errors_with_solutions`, `solution_reuse_rate`.

#### Example

```python
from superclaude import ReflexionPattern

reflexion = ReflexionPattern()
error_info = {
    "error_type": "AssertionError",
    "error_message": "Expected 5, got 3",
    "test_name": "test_calculation",
}

solution = reflexion.get_solution(error_info)
if solution:
    print(f"Known error — solution: {solution}")
else:
    reflexion.record_error(error_info)  # New error — record for next time
```

---

### TokenBudgetManager

`superclaude.pm_agent.token_budget.TokenBudgetManager`

Token allocation by task complexity. Invalid complexity values fall back to `"medium"`.

| Complexity | Budget | Typical task |
|---|---|---|
| `simple` | 200 | Typo fix, trivial change |
| `medium` | 1,000 | Bug fix, small feature |
| `complex` | 2,500 | Large feature, refactoring |

#### Methods

| Method | Signature | Description |
|---|---|---|
| `__init__` | `(complexity: ComplexityLevel = "medium")` | Create manager for a complexity level |
| `allocate` | `(amount: int) -> bool` | Allocate tokens; `False` if the budget would be exceeded |
| `use` | `(amount: int) -> bool` | Alias for `allocate()` (historical CLI compatibility) |
| `remaining` | property `-> int` | Tokens still available |
| `remaining_tokens` | `() -> int` | Backward-compatible mirror of `remaining` |
| `reset` | `() -> None` | Reset the used-token counter |

#### Example

```python
from superclaude.pm_agent.token_budget import TokenBudgetManager

manager = TokenBudgetManager(complexity="medium")
assert manager.limit == 1000
manager.allocate(400)
print(manager.remaining)  # 600
```

---

## Execution Engine (`superclaude.execution`)

Three engines integrated behind one entry point: **Reflection** (think ×3 before executing), **Parallel** (execute at maximum speed), and **Self-Correction** (learn from failures).

```python
from superclaude.execution import (
    intelligent_execute, ReflectionEngine, ParallelExecutor, SelfCorrectionEngine,
    ConfidenceScore, ExecutionPlan, RootCause, Task,
    should_parallelize, reflect_before_execution, learn_from_failure,
)
```

### High-Level Functions

**`intelligent_execute(task, operations, context=None, repo_path=None, auto_correct=True) -> Dict[str, Any]`**

Full pipeline: reflect ×3 → plan → execute in parallel → validate and learn from failures.

- **Args**:
  - `task` (str) — task description
  - `operations` (List[Callable]) — callables to execute
  - `context` (Optional[Dict]) — project index, git status, etc.
  - `repo_path` (Optional[Path]) — repository root (defaults to cwd)
  - `auto_correct` (bool) — enable automatic self-correction (default `True`)
- **Returns**: dict with execution results and metadata

**`quick_execute(operations: List[Callable]) -> List[Any]`**

Parallel execution without reflection. Use for simple, low-risk operations.

**`safe_execute(task: str, operation: Callable, context: Optional[Dict] = None) -> Any`**

Single-operation execution guarded by reflection. Blocks if confidence < 70%.

---

### ParallelExecutor

`superclaude.execution.parallel.ParallelExecutor`

Automatic parallelization engine. Builds a dependency graph via topological sort, groups independent tasks into waves, and runs each wave concurrently on a `ThreadPoolExecutor` (the Wave → Checkpoint → Wave pattern).

#### Constructor

**`ParallelExecutor(max_workers: int = 10)`** — `max_workers` caps concurrent threads per parallel group.

#### Methods

**`plan(tasks: List[Task]) -> ExecutionPlan`**

Build the execution plan. Raises `ValueError` if a circular dependency is detected.

**`execute(plan: ExecutionPlan) -> Dict[str, Any]`**

Execute the plan group by group. Returns `{task_id: result}`; a failed task's entry is `None` and its `Task.error` holds the exception.

#### Supporting types

| Type | Description |
|---|---|
| `TaskStatus` | Enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED` |
| `Task` | Dataclass: `id`, `description`, `execute` (callable), `depends_on` (list of task IDs), plus `status` / `result` / `error` populated during execution. `can_execute(completed)` checks whether dependencies are satisfied |
| `ParallelGroup` | Dataclass: one wave of tasks that can run concurrently (`group_id`, `tasks`, `dependencies`) |
| `ExecutionPlan` | Dataclass: `groups`, `total_tasks`, `sequential_time_estimate`, `parallel_time_estimate`, `speedup` |

#### Module-level helpers

**`parallel_file_operations(files: List[str], operation: Callable) -> List[Any]`** — apply one operation to many files concurrently.

**`should_parallelize(items: List[Any], threshold: int = 3) -> bool`** — auto-trigger: `True` when `len(items) >= threshold`.

#### Example

```python
from superclaude.execution.parallel import ParallelExecutor, Task

executor = ParallelExecutor(max_workers=10)
tasks = [
    Task("read1", "Read config.py", lambda: read_file("config.py"), []),
    Task("read2", "Read utils.py",  lambda: read_file("utils.py"),  []),
    Task("analyze", "Analyze", lambda: analyze(), ["read1", "read2"]),
]
plan = executor.plan(tasks)        # 2 groups: [read1, read2] then [analyze]
results = executor.execute(plan)   # {"read1": ..., "read2": ..., "analyze": ...}
```

---

### ReflectionEngine

`superclaude.execution.reflection.ReflectionEngine`

3-stage pre-execution reflection ("Triple Reflection"). Blocks execution when overall confidence < 70%.

| Stage | Weight | Question |
|---|---|---|
| Requirement clarity | 0.5 | Is the task specific enough to build? |
| Past mistakes | 0.3 | Have similar tasks failed before? (checks `docs/memory/reflexion.json`) |
| Context readiness | 0.2 | Is enough context loaded (project index, branch, git status)? |

#### Constructor

**`ReflectionEngine(repo_path: Path)`** — creates `docs/memory/` under `repo_path` if needed; reflection logs and reflexion memory live there.

#### Methods

**`reflect(task: str, context: Optional[Dict[str, Any]] = None) -> ConfidenceScore`**

Run all three reflection stages and return the weighted decision.

**`record_reflection(task: str, confidence: ConfidenceScore, decision: str) -> None`**

Append the reflection outcome to `docs/memory/reflection_log.json` for future learning.

#### Supporting types

| Type | Description |
|---|---|
| `ReflectionResult` | Dataclass: one stage's `stage`, `score` (0.0–1.0), `evidence`, `concerns` |
| `ConfidenceScore` | Dataclass: the three `ReflectionResult`s, weighted `confidence`, `should_proceed`, `blockers`, `recommendations` |

#### Module-level helpers

**`get_reflection_engine(repo_path: Optional[Path] = None) -> ReflectionEngine`** — get or create the singleton (defaults to cwd).

**`reflect_before_execution(task: str, context: Optional[Dict] = None) -> ConfidenceScore`** — convenience wrapper around the singleton's `reflect()`.

#### Example

```python
from superclaude.execution import reflect_before_execution

score = reflect_before_execution(
    "fix parse_config() crash on empty file in src/config.py",
    context={"project_index": "...", "current_branch": "fix/config", "git_status": "clean"},
)
if score.should_proceed:
    ...  # confidence ≥ 70%
else:
    print(score.blockers, score.recommendations)
```

---

### SelfCorrectionEngine

`superclaude.execution.self_correction.SelfCorrectionEngine`

Reflexion-based failure learning: detect failure → analyze root cause → store in memory → generate prevention rules → apply automatically in future runs. Persistent memory lives in `docs/memory/reflexion.json`.

#### Constructor

**`SelfCorrectionEngine(repo_path: Path)`** — creates `docs/memory/` if needed and initializes `reflexion.json` on first use.

#### Methods

**`detect_failure(execution_result: Dict[str, Any]) -> bool`**

`True` when `execution_result["status"]` is `failed`, `error`, or `exception`.

**`analyze_root_cause(task: str, failure: Dict[str, Any]) -> RootCause`**

Categorize the failure (`validation`, `dependency`, `logic`, `assumption`, `type`, or `unknown`), match against similar past failures, and generate a prevention rule plus validation tests.

**`learn_and_prevent(task, failure, root_cause, fixed=False, fix_description=None) -> None`**

Persist the failure to reflexion memory. Recurring failures (same task + error) increment a `recurrence_count` instead of duplicating entries; new prevention rules are deduplicated.

**`get_prevention_rules() -> List[str]`**

Return all active prevention rules from memory.

**`check_against_past_mistakes(task: str) -> List[FailureEntry]`**

Return past failures whose task descriptions overlap the given task (≥ 2 shared keywords).

#### Supporting types

| Type | Description |
|---|---|
| `RootCause` | Dataclass: `category`, `description`, `evidence`, `prevention_rule`, `validation_tests` |
| `FailureEntry` | Dataclass: one reflexion-memory record (`id`, `timestamp`, `task`, `failure_type`, `error_message`, `root_cause`, `fixed`, `fix_description`, `recurrence_count`) with `to_dict()` / `from_dict()` JSON round-tripping |

#### Module-level helpers

**`get_self_correction_engine(repo_path: Optional[Path] = None) -> SelfCorrectionEngine`** — get or create the singleton (defaults to cwd).

**`learn_from_failure(task, failure, fixed=False, fix_description=None) -> RootCause`** — convenience: analyze the root cause and store the learning in one call.

#### Example

```python
from superclaude.execution import learn_from_failure

root_cause = learn_from_failure(
    task="add retry logic to http client",
    failure={"error": "ModuleNotFoundError: No module named 'tenacity'", "type": "exception"},
)
print(root_cause.prevention_rule)  # "ALWAYS check dependencies exist before importing"
```

---

## Pytest Plugin (`superclaude.pytest_plugin`)

Auto-loaded via the `pytest11` entry point when `superclaude` is installed — no `conftest.py` changes needed.

### Fixtures

| Fixture | Provides | Typical use |
|---|---|---|
| `confidence_checker` | `ConfidenceChecker` instance | `confidence_checker.assess(context)` |
| `self_check_protocol` | `SelfCheckProtocol` instance | `self_check_protocol.validate(implementation)` |
| `reflexion_pattern` | `ReflexionPattern` instance | `reflexion_pattern.get_solution(error_info)` |
| `token_budget` | `TokenBudgetManager` sized by `@pytest.mark.complexity(...)` | `assert token_budget.limit == 1000` |
| `pm_context` | Temp `docs/memory/` structure (`pm_context.md`, `last_session.md`, `next_actions.md`) | Testing PM Agent memory flows |

### Markers

| Marker | Effect |
|---|---|
| `@pytest.mark.confidence_check` | Runs pre-execution confidence assessment; test is skipped if confidence < 70% |
| `@pytest.mark.self_check` | Post-implementation validation |
| `@pytest.mark.reflexion` | Failures are recorded to reflexion memory for future prevention |
| `@pytest.mark.complexity("simple"\|"medium"\|"complex")` | Sets the `token_budget` fixture's limit (200 / 1,000 / 2,500) |

Auto-applied markers (no annotation needed):

- Tests under `tests/unit/` → `@pytest.mark.unit`
- Tests under `tests/integration/` → `@pytest.mark.integration`
- Files matching `*hallucination*` → `hallucination`; `*performance*` → `performance`

### Hooks (implementation detail)

| Hook | Role |
|---|---|
| `pytest_configure(config)` | Registers the plugin and custom markers |
| `pytest_runtest_setup(item)` | Runs the confidence check for `confidence_check`-marked tests; skips below 70% |
| `pytest_runtest_makereport(item, call)` | Records outcomes/errors for reflexion learning |
| `pytest_collection_modifyitems(config, items)` | Applies the automatic markers above |
| `pytest_report_header(config)` | Adds the SuperClaude version to the pytest header |

### Example

```python
import pytest

@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7

@pytest.mark.complexity("medium")
def test_with_budget(token_budget):
    assert token_budget.limit == 1000
```

---

## CLI (`superclaude.cli`)

Entry point: the `superclaude` console command (Click-based, defined in `cli/main.py`).

### Commands (`cli/main.py`)

| Command | Function | Description |
|---|---|---|
| `superclaude install` | `install(target, force, list_only)` | Install all `/sc:*` slash commands to `~/.claude/commands/sc/`. Options: `--force`, `--list`, `--target PATH` |
| `superclaude update` | `update(target)` | Re-install commands at the current package version (equivalent to `install --force`) |
| `superclaude mcp` | `mcp(servers, list_only, scope, dry_run)` | Install/manage MCP servers. Options: `--list`, `--servers NAME` (repeatable), `--scope`, `--dry-run` |
| `superclaude install-skill` | `install_skill(skill_name, target, force)` | Install a skill (e.g., `pm-agent`) to `~/.claude/skills/` |
| `superclaude doctor` | `doctor(verbose)` | Health check: pytest plugin loaded, skills installed, config present |
| `superclaude version` | `version()` | Show the package version |

### Command Installation (`cli/install_commands.py`)

| Function | Signature | Description |
|---|---|---|
| `install_commands` | `(target_path=None, force=False) -> Tuple[bool, str]` | Install all slash commands (default target `~/.claude/commands/sc/`) |
| `install_agents` | `(target_path=None, force=False) -> Tuple[bool, str]` | Install agent files to `~/.claude/agents/` |
| `list_available_commands` | `() -> List[str]` | Commands shipped with the package |
| `list_installed_commands` | `() -> List[str]` | Commands present in `~/.claude/commands/sc/` |
| `list_available_agents` | `() -> List[str]` | Agent files shipped with the package |

### Skill Installation (`cli/install_skill.py`)

| Function | Signature | Description |
|---|---|---|
| `install_skill_command` | `(skill_name, target_path, force=False) -> Tuple[bool, str]` | Copy a skill into the target directory; refuses to overwrite unless `force=True` |
| `list_available_skills` | `() -> list[str]` | Installable skills (packaged and repo-checkout locations; kebab-case canonical names) |

### MCP Installation (`cli/install_mcp.py`)

| Function | Signature | Description |
|---|---|---|
| `install_mcp_servers` | `(selected_servers=None, scope="user", dry_run=False, use_gateway=None) -> Tuple[bool, str]` | Main entry: install selected servers or run interactive selection; optionally the AIRIS gateway |
| `install_mcp_server` | `(server_info, scope="user", dry_run=False) -> bool` | Install one server via the Claude Code API |
| `install_airis_gateway` | `(dry_run=False) -> bool` | Install the AIRIS MCP Gateway with Docker (into `~/.superclaude/airis-mcp-gateway/`) |
| `list_available_servers` | `() -> None` | Print the available server catalog |
| `check_docker_available` | `() -> bool` | Is Docker installed and running? |
| `check_prerequisites` | `() -> Tuple[bool, List[str]]` | Verify required tools are present |
| `check_mcp_server_installed` | `(server_name) -> bool` | Is a server already installed? |
| `prompt_for_api_key` | `(server_name, env_var, description) -> Optional[str]` | Interactively collect an API key when required |

### Health Check (`cli/doctor.py`)

**`run_doctor(verbose: bool = False) -> Dict[str, Any]`** — run installation health checks (plugin loaded, skills present, config files) and return the results dict.

---

## Scripts (`superclaude.scripts`)

### `clean_command_names.py`

Maintenance script that removes redundant `name:` attributes from command frontmatter (names are derived from plugin name + filename).

| Function | Signature | Description |
|---|---|---|
| `find_project_root` | `() -> Path` | Locate the project root via `plugin.json`; raises `FileNotFoundError` if not found |
| `clean_name_attributes` | `(content: str) -> Tuple[str, bool]` | Strip `name:` from YAML frontmatter; returns `(cleaned, was_modified)` |
| `process_commands_directory` | `(commands_dir: Path) -> int` | Clean every command `.md` file; returns count modified |
| `main` | `() -> int` | Script entry point; exit code 0 on success, 1 on error |

---

## Related Documentation

- [Commands Reference](commands-list.md) — all 30 `/sc:*` slash commands
- [Examples Cookbook](examples-cookbook.md) — practical usage recipes
- [Technical Architecture](../developer-guide/technical-architecture.md) — system design
- [Testing & Debugging](../developer-guide/testing-debugging.md) — test-suite guidance
