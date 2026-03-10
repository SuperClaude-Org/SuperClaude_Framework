# D-0001: Pipeline Foundation Review Notes

## Overview

Review of the existing pipeline infrastructure to confirm extension points, state schema, and patterns available for v2.22 remediate/certify steps.

---

## 1. execute_pipeline() Step Model

**Source**: `src/superclaude/cli/pipeline/executor.py`

### Step Sequencing
- `execute_pipeline()` accepts `steps: list[Step | list[Step]]` -- a mixed list where:
  - Single `Step` entries execute sequentially
  - `list[Step]` entries execute as parallel groups (all steps in the group run concurrently via threads)
- For each step: `on_step_start` -> `run_step()` -> gate check -> `on_step_complete` -> `on_state_update`
- If any step fails after retry exhaustion: pipeline HALTs (no further steps execute)
- Parallel groups: if any step in the group fails, remaining steps are cancelled via `threading.Event`

### Retry Logic
- `retry_limit` on `Step` dataclass controls retries (retry_limit=1 means 2 total attempts)
- Retry only happens when gate check fails; subprocess errors (non-zero exit, timeout) are terminal

### Gate Evaluation
- Two modes: `GateMode.BLOCKING` (synchronous, default) and `GateMode.TRAILING` (deferred, grace period)
- `grace_period == 0` forces BLOCKING regardless of step's `gate_mode`
- Trailing gates collect at sync point after all steps complete

### State Save Pattern
- `_build_state()` produces a dict with `steps`, `total`, `passed`, `failed` counts
- Called via `on_state_update` callback after each step/group completes
- Consumers (roadmap, sprint) provide their own `on_state_update` implementation

### Extension Points
- **StepRunner Protocol**: Any callable matching `(Step, PipelineConfig, Callable[[], bool]) -> StepResult`
- **Callbacks**: `on_step_start`, `on_step_complete`, `on_state_update`, `cancel_check`
- **TrailingGateRunner**: Optional trailing gate support

---

## 2. execute_roadmap() Extension Points

**Source**: `src/superclaude/cli/roadmap/executor.py`

### Pipeline Composition
- `_build_steps()` constructs a 9-step pipeline (8 sequential + 1 parallel group for generate)
- Steps: extract -> [generate-A, generate-B] -> diff -> debate -> score -> merge -> test-strategy -> spec-fidelity
- `execute_roadmap()` is the top-level orchestrator that:
  1. Builds steps via `_build_steps()`
  2. Handles `--dry-run` and `--resume`
  3. Delegates to `execute_pipeline()` with `roadmap_run_step` as the StepRunner
  4. Saves state via `_save_state()`
  5. Auto-invokes validation via `_auto_invoke_validate()`

### Extension Points for New Steps
- New steps (remediate, certify) can be added to the `_build_steps()` return list
- `execute_roadmap()` already handles post-pipeline actions (validation) -- remediation can follow the same pattern
- The interactive prompt (FR-003, FR-032) should live in `execute_roadmap()`, NOT in `execute_pipeline()`, preserving the latter's non-interactive contract

### State Preservation
- `_save_state()` preserves existing `validation` and `fidelity_status` keys across rewrites
- New keys (e.g., `remediate`, `certify`) can be added additively without breaking backward compatibility

---

## 3. validate_executor.py -- ClaudeProcess Patterns

**Source**: `src/superclaude/cli/roadmap/validate_executor.py`

### Agent Spawning Pattern
- `validate_run_step()` mirrors `roadmap_run_step()`: builds argv, launches ClaudeProcess, waits with timeout, sanitizes output
- Both use the same `ClaudeProcess` API with identical parameter patterns:
  - `prompt`, `output_file`, `error_file`, `max_turns`, `model`, `permission_flag`, `timeout_seconds`, `output_format`, `extra_args`
- Inline embedding pattern: read input files into prompt string (up to 100KB), fall back to `--file` flags for larger inputs

### Multi-Agent Parallel Execution
- `_build_multi_agent_steps()`: creates N parallel reflection steps (one per agent), then a sequential adversarial-merge step
- The parallel group pattern is: `[reflect_steps, merge_step]` -- parallel reflections followed by sequential merge
- **Precedent for remediation**: This is the exact pattern needed for parallel remediation agents (one per finding/file batch)

### Degraded Mode Handling
- `_write_degraded_report()`: writes a report with `validation_complete: false` when agents partially fail
- This pattern can be reused for remediation -- partial agent failure should produce a degraded tasklist update

---

## 4. Gate/State Models

**Source**: `src/superclaude/cli/pipeline/models.py`

### GateCriteria Dataclass
```python
@dataclass
class GateCriteria:
    required_frontmatter_fields: list[str]
    min_lines: int
    enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
    semantic_checks: list[SemanticCheck] | None = None
```

### SemanticCheck Dataclass
```python
@dataclass
class SemanticCheck:
    name: str
    check_fn: Callable[[str], bool]
    failure_message: str
```

### Step Dataclass
```python
@dataclass
class Step:
    id: str
    prompt: str
    output_file: Path
    gate: Optional[GateCriteria]
    timeout_seconds: int
    inputs: list[Path] = field(default_factory=list)
    retry_limit: int = 1
    model: str = ""
    gate_mode: GateMode = GateMode.BLOCKING
```

### StepStatus Enum
- Values: PENDING, PASS, FAIL, TIMEOUT, CANCELLED, SKIPPED
- Properties: `is_terminal` (all except PENDING), `is_success` (PASS only), `is_failure` (FAIL, TIMEOUT)

### Gate Evaluation Tiers (pipeline/gates.py)
- EXEMPT: always passes
- LIGHT: file exists + non-empty
- STANDARD: + min_lines + YAML frontmatter fields
- STRICT: + semantic checks

---

## 5. Resume Flow

**Source**: `src/superclaude/cli/roadmap/executor.py` (`_apply_resume`)

### Resume Logic
1. Read `.roadmap-state.json` from output_dir
2. Check spec hash: if spec file changed since last run, force re-run of extract step
3. For each step in pipeline order:
   - If step has a gate: run `gate_passed()` against existing output file
   - If gate passes: skip the step
   - On first failing gate: include that step and all subsequent steps
4. If all steps pass: print "Nothing to do" and return empty list

### Stale Detection
- Uses SHA-256 hash of spec file stored in state as `spec_hash`
- On mismatch: prints WARNING and forces extract step re-run

---

## 6. Hash Usage Patterns

**Source**: Multiple files across the codebase

### Existing Hash Patterns
| Location | Algorithm | Purpose |
|----------|-----------|---------|
| `roadmap/executor.py:529` | `hashlib.sha256` | Spec file hash for resume staleness detection |
| `roadmap/executor.py:825` | `hashlib.sha256` | Spec hash comparison during resume |
| `audit/tool_orchestrator.py:101` | `hashlib.sha256` | Content hash for audit deduplication |
| `sprint/tmux.py:29` | `hashlib.sha1` | Short hash for tmux session naming (non-security) |
| `execution/self_correction.py:292` | `hashlib.md5` | Failure ID generation (non-security) |

### Hash Algorithm Assessment
- **SHA-256 is the dominant pattern** for content integrity checks (2/3 security-relevant usages)
- SHA-1 and MD5 are only used for non-security purposes (naming, identification)
- No conflicts exist with adopting SHA-256 for `source_report_hash`

---

## 7. Schema Version

**Source**: `.roadmap-state.json` (current v2.22 state file)

### Current Value
```json
"schema_version": 1
```

### Compatibility Assessment
- Schema version 1 is the current and only version used in `.roadmap-state.json`
- The state file already supports additive extension: `_save_state()` preserves existing keys (`validation`, `fidelity_status`) across rewrites
- Adding `remediate` and `certify` step entries follows the same additive pattern -- no schema version bump required
- Adding new top-level keys (e.g., `remediate_summary`, `certify_status`) is backward-compatible because `read_state()` uses `dict.get()` throughout

### Extension Strategy
- **Additive-only**: New keys added to the state dict; no existing keys modified or removed
- **No schema version bump needed** unless the semantics of existing keys change (they do not in v2.22)
- Consumers of `.roadmap-state.json` (resume flow, validation status) use `dict.get()` with defaults, so missing new keys are handled gracefully
