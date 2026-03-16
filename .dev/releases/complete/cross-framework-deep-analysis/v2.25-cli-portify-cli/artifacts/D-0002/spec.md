# D-0002: Open Question Resolution List

**Task**: T01.02 — Resolve Contract-Affecting Blocking Open Questions
**Date**: 2026-03-15
**Status**: PASS — all 5 mandatory blocking OQs resolved

---

## Resolution Summary

| OQ | Title | Blocking? | Status |
|----|-------|-----------|--------|
| OQ-001 | TurnLedger semantics — "one turn" | YES (blocking) | RESOLVED |
| OQ-002 | Kill signal mechanism (SIGTERM vs SIGKILL) | POTENTIAL | RESOLVED — non-blocking confirmed |
| OQ-003 | `phase_contracts` schema | YES (blocking) | RESOLVED |
| OQ-004 | `api_snapshot_hash` algorithm and scope | YES (blocking) | RESOLVED |
| OQ-005 | Dry-run phase scope | non-blocking | RESOLVED (via decisions.yaml) |
| OQ-006 | Integration contract schema | non-blocking | RESOLVED (via decisions.yaml) |
| OQ-007 | Agent discovery warning behavior | non-blocking | DOCUMENTED |
| OQ-008 | Default output path and --file subprocess arg | non-blocking | RESOLVED (via decisions.yaml) |
| OQ-009 | `failure_type` enum values (PortifyValidationError) | YES (blocking) | RESOLVED |
| OQ-010 | Step boundary algorithm | non-blocking | RESOLVED (via decisions.yaml) |
| OQ-011 | `--debug` flag behavior | YES (blocking) | RESOLVED |
| OQ-012 | Overwrite rules for generated modules | non-blocking | RESOLVED |
| OQ-013 | `PASS_NO_SIGNAL` retry behavior | POTENTIAL | RESOLVED — non-blocking confirmed |
| OQ-014 | Workdir cleanup policy | non-blocking | DOCUMENTED |

---

## OQ-001: TurnLedger Semantics — What Constitutes "One Turn"

**Status**: RESOLVED
**Blocking**: YES

### Resolution

One "turn" = one `claude` CLI subprocess invocation. The TurnLedger tracks budget across all Claude subprocess calls in the pipeline. Each `_run_claude_step()` call consumes exactly 1 turn via `ledger.debit(1)` before subprocess launch.

**Concrete rules**:
- `TurnLedger.can_launch()` returns `True` if `available() >= minimum_allocation` (minimum_allocation=5)
- `available()` = `initial_budget - consumed + reimbursed`
- Budget exhaustion → `PortifyOutcome.HALTED` with `halt_step` set to the blocking step ID
- TurnLedger is NOT in `superclaude.cli.pipeline.models` — it lives in `superclaude.cli.sprint.models`
- Portified pipelines import it directly: `from superclaude.cli.sprint.models import TurnLedger`

**Default budget**: `max_turns=200` (CLI default); recommended `suggested_resume_budget = remaining_steps * 25`

**Implementable interface**:
```python
from superclaude.cli.sprint.models import TurnLedger

ledger = TurnLedger(initial_budget=config.max_turns)

# Before each Claude step:
if not ledger.can_launch():
    result.outcome = PortifyOutcome.HALTED
    result.halt_step = step.id
    break
ledger.debit(1)
# Run step...
```

---

## OQ-002: Kill Signal Mechanism (SIGTERM → SIGKILL vs SIGKILL Directly)

**Status**: RESOLVED
**Blocking**: Non-blocking confirmed (affects Phase 2 process.py)

### Resolution

The existing `ClaudeProcess.terminate()` in `superclaude.cli.pipeline.process` implements the established pattern:
1. Send SIGTERM to process group
2. Wait 10 seconds grace period
3. Escalate to SIGKILL if process has not exited

This is the correct pattern to follow for `cli_portify/process.py`. Use SIGTERM → 10s grace → SIGKILL, not SIGKILL directly.

**Assessment**: Non-blocking — this is a Phase 2 implementation detail. The pattern is already determined from `superclaude.cli.pipeline.process.ClaudeProcess.terminate()` (lines 144–172). No architecture decision required here; inherit or replicate the existing behavior.

---

## OQ-003: `phase_contracts` Schema

**Status**: RESOLVED
**Blocking**: YES

### Resolution

`phase_contracts` is a field in `return-contract.yaml` that records per-phase completion status as a dictionary. Schema:

```python
phase_contracts: dict[str, dict] = {
    "prerequisites": {
        "completed": True,
        "artifacts": ["portify-config.yaml", "component-inventory.yaml"],
        "timestamp": float,
    },
    "analysis": {
        "completed": True,
        "artifacts": ["protocol-map.md", "portify-analysis-report.md"],
        "timestamp": float,
    },
    "user_review_p1": {
        "completed": True,
        "artifacts": ["phase1-approval.yaml"],
        "timestamp": float,
    },
    "specification": {
        "completed": True,
        "artifacts": ["step-graph-spec.md", "models-gates-spec.md", "prompts-executor-spec.md", "portify-spec.md"],
        "timestamp": float,
    },
    "user_review_p2": {
        "completed": True,
        "artifacts": ["phase2-approval.yaml"],
        "timestamp": float,
    },
    "synthesis": {
        "completed": True,
        "artifacts": ["portify-release-spec.md"],
        "timestamp": float,
    },
    "panel_review": {
        "completed": True,
        "artifacts": ["portify-release-spec.md", "panel-report.md"],
        "timestamp": float,
    },
}
```

**Builder function**:
```python
def _build_phase_contracts(result: PortifyResult) -> dict:
    """Build per-phase contract summaries from step results."""
    contracts = {}
    for phase in PortifyPhaseType:
        phase_steps = [r for r in result.step_results
                       if hasattr(r.step, 'phase_type') and r.step.phase_type == phase]
        if phase_steps:
            completed = all(r.status in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL,
                                          PortifyStatus.PASS_NO_REPORT)
                            for r in phase_steps)
            artifacts = [a for r in phase_steps for a in getattr(r, 'artifacts_produced', [])]
            contracts[phase.value] = {
                "completed": completed,
                "artifacts": artifacts,
                "timestamp": max((getattr(r, 'finished_at', 0.0) or 0.0) for r in phase_steps),
            }
    return contracts
```

---

## OQ-004: `api_snapshot_hash` Algorithm and Scope

**Status**: RESOLVED
**Blocking**: YES

### Resolution

`api_snapshot_hash` is a content-fingerprint of the final release spec (or most advanced artifact produced). It goes into `return-contract.yaml` to enable deterministic diffing across runs.

**Algorithm**: SHA-256 of the content of `portify-release-spec.md` (if it exists). If the spec file does not exist, use the SHA-256 of `portify-spec.md`. If neither exists, return empty string.

**Scope**: Single file content hash only. Not a directory hash or multi-file hash.

**Implementable function**:
```python
import hashlib

def _compute_spec_hash(result: PortifyResult, config: PortifyConfig) -> str:
    """Compute SHA-256 of the most advanced spec artifact produced."""
    for candidate in [
        config.work_dir / "portify-release-spec.md",
        config.work_dir / "portify-spec.md",
    ]:
        if candidate.exists():
            content = candidate.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]  # 16-char prefix for readability
    return ""
```

**Note**: 16-character prefix is sufficient for fingerprinting purposes; full hex digest is 64 chars and unnecessary for change detection.

---

## OQ-005: Dry-Run Phase Scope

**Status**: RESOLVED (non-blocking, via decisions.yaml OQ-003)

Execute phases 0-2 only (PREREQUISITES + ANALYSIS + USER_REVIEW + SPECIFICATION phase types), emit contracts, no code generation.

---

## OQ-006: Integration Contract Schema

**Status**: RESOLVED (non-blocking, via decisions.yaml OQ-004)

Fields: `schema_version`, `phase`, `status`, `timestamp`, `main_py_patched`, `command_registered`, `test_file_generated`, `smoke_test_passed`.

---

## OQ-007: Agent Discovery Warning Behavior

**Status**: DOCUMENTED (non-blocking, assigned to Phase 2 inventory implementation)

**Resolution**: Emit a warning when referenced agent files are not found in `src/superclaude/agents/`. Do not silently suppress. The `discover_components()` function should use a best-effort approach: attempt to resolve agent names from skill frontmatter, log a warning per unresolved agent, and continue. Per decisions.yaml, uses TodoWrite checkpoint pattern for user review gates.

**Phase assignment**: Phase 2 (inventory.py implementation)

---

## OQ-008: Default Output Path and Template --file Argument

**Status**: RESOLVED (non-blocking, via decisions.yaml OQ-008)

Default output: `src/superclaude/cli/<derived_name>/`. If template content exceeds 50,000 bytes, write to temp file and pass via `--file <path>` to Claude subprocess.

---

## OQ-009: `failure_type` Enum Values (Affects PortifyValidationError in Phase 2)

**Status**: RESOLVED
**Blocking**: YES

### Resolution

`failure_type` in the return contract is a string (not a Python Enum). The complete set of values defined in `portify-spec.md` config.py implementation:

| Value | Raised By | Condition |
|-------|-----------|-----------|
| `"NAME_COLLISION"` | `validate_and_build_config()` | Output dir exists and is NOT a portified module |
| `"OUTPUT_NOT_WRITABLE"` | `validate_and_build_config()` | Output dir parent does not exist |
| `"AMBIGUOUS_PATH"` | `_resolve_workflow_path()` | Multiple skill directories match the workflow name |
| `"INVALID_PATH"` | `_resolve_workflow_path()` | No skill directory found matching workflow name |
| `"DERIVATION_FAILED"` | `_derive_cli_name()` | Cannot derive a valid CLI name from the skill directory name |

**Additional runtime failure types** (in return-contract.yaml `failure_type` field):

| Value | Condition |
|-------|-----------|
| `"GATE_FAILURE"` | Step gate check failed after all retries |
| `"TIMEOUT"` | Step exited with code 124 |
| `"BUDGET_EXHAUSTED"` | TurnLedger.can_launch() returned False before step |
| `"INTERRUPTED"` | SIGINT/SIGTERM received during execution |
| `""` (empty string) | No failure (successful outcome) |

**`_get_failure_type()` implementation**:
```python
def _get_failure_type(result: PortifyResult) -> str:
    if result.outcome == PortifyOutcome.SUCCESS:
        return ""
    if result.outcome == PortifyOutcome.INTERRUPTED:
        return "INTERRUPTED"
    if result.outcome == PortifyOutcome.HALTED:
        # Check why we halted
        if result.halt_step:
            failed_step = next(
                (r for r in result.step_results if r.step and r.step.id == result.halt_step),
                None,
            )
            if failed_step:
                if failed_step.status == PortifyStatus.TIMEOUT:
                    return "TIMEOUT"
                if failed_step.gate_details:
                    return "GATE_FAILURE"
        return "BUDGET_EXHAUSTED"
    return ""
```

**PortifyValidationError** (Phase 2 models.py):
```python
class PortifyValidationError(Exception):
    def __init__(self, failure_type: str, message: str) -> None:
        super().__init__(message)
        self.failure_type = failure_type
```

---

## OQ-010: Step Boundary Algorithm

**Status**: RESOLVED (non-blocking, via decisions.yaml OQ-010)

Documented in `refs/analysis-protocol.md` under "Step Decomposition Algorithm → Identify Step Boundaries". No additional extraction needed.

---

## OQ-011: `--debug` Flag Behavior

**Status**: RESOLVED
**Blocking**: YES

### Resolution

When `--debug` is set (i.e., `config.debug=True`), the cli-portify pipeline writes structured debug events to a debug log file. This mirrors the existing sprint framework pattern.

**Behavior**:
- `config.debug=False` (default): NullHandler attached; no debug output produced; zero performance overhead
- `config.debug=True`: FileHandler writes structured events to `config.work_dir / "debug.log"` in `key=value` format

**Debug events to emit**:
- Step start/end with step ID and timing
- Gate check results (pass/fail + reason)
- Signal events (SIGTERM, SIGKILL, SIGINT)
- Subprocess launch (pid, command, timeout)
- TurnLedger state (available, consumed) before each Claude step
- Convergence loop iteration transitions

**Log path**: `config.work_dir / "debug.log"` (e.g., `.dev/portify-workdir/<cli_name>/debug.log`)

**Implementation pattern** (follow sprint debug_logger.py):
```python
def setup_debug_logger(config: PortifyConfig) -> logging.Logger:
    logger = logging.getLogger("superclaude.cli_portify.debug")
    if config.debug:
        log_path = config.work_dir / "debug.log"
        handler = logging.FileHandler(log_path)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    else:
        logger.addHandler(logging.NullHandler())
    return logger
```

---

## OQ-012: Overwrite Rules for Generated Modules

**Status**: RESOLVED (non-blocking, determined from spec)

Only overwrite an existing module at `output_dir` if `output_dir / "__init__.py"` contains the marker string `"Generated by"` or `"Portified from"`. If neither marker is present, raise `PortifyValidationError("NAME_COLLISION", ...)`.

---

## OQ-013: `PASS_NO_SIGNAL` Retry Behavior

**Status**: RESOLVED
**Blocking**: Non-blocking confirmed (affects Phase 2 executor)

### Resolution

`PASS_NO_SIGNAL` (result file present, no `EXIT_RECOMMENDATION` marker found) **does** trigger retry for steps with `retry_limit >= 1`. This is a Phase 2 executor implementation concern.

**Classification rule**:
- Result file present + `EXIT_RECOMMENDATION: CONTINUE` → `PASS`
- Result file present + `EXIT_RECOMMENDATION: HALT` → `HALT`
- Result file present + NO `EXIT_RECOMMENDATION` → `PASS_NO_SIGNAL` → **triggers retry**
- Output file present but no result file, no `detect_error_max_turns` → `PASS_NO_REPORT` → **does NOT trigger retry** (treated as passing)
- No output file, no result file → `ERROR`

**Assessment**: Non-blocking for Phase 1 architecture — this is a Phase 2 executor implementation detail. The distinction between `PASS_NO_SIGNAL` and `PASS_NO_REPORT` is clear and implementable.

---

## OQ-014: Workdir Cleanup Policy

**Status**: DOCUMENTED (non-blocking, assigned to Phase 9 CLI/docs)

Workdir (`.dev/portify-workdir/<cli_name>/`) is NOT automatically cleaned up after successful runs. It persists for resume, debugging, and artifact inspection. Document in help text. User is responsible for manual cleanup.

**Phase assignment**: Phase 9 (commands.py help text and documentation)

---

## Cross-Phase Dependency Assessment

| OQ | Affects Phase | Notes |
|----|---------------|-------|
| OQ-001 (TurnLedger) | Phase 2 | Import from sprint.models; `debit(1)` per Claude step |
| OQ-002 (kill signal) | Phase 2 | Use pipeline.process.ClaudeProcess pattern |
| OQ-003 (phase_contracts) | Phase 2 | Emit via `_build_phase_contracts()` in return contract |
| OQ-004 (api_snapshot_hash) | Phase 2 | SHA-256 prefix of release spec or portify spec |
| OQ-009 (failure_type) | Phase 2 | 5 validation errors + 4 runtime failure types |
| OQ-011 (--debug) | Phase 2 | NullHandler vs FileHandler pattern |
| OQ-013 (PASS_NO_SIGNAL) | Phase 2 | Triggers retry; PASS_NO_REPORT does not |
| OQ-007 (agent discovery) | Phase 2 | Warn on missing agents; do not suppress |
| OQ-014 (workdir cleanup) | Phase 9 | Document only; no auto-cleanup |

---

**EXIT_RECOMMENDATION: CONTINUE**
