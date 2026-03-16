# D-0001: Architecture Validation Notes

**Task**: T01.01 — Validate Target Architecture and Confirm Base Type Imports
**Date**: 2026-03-15
**Status**: PASS

---

## 1. Base Type Import Verification

All 6 framework base types import successfully with zero errors.

### Import Command (Verified)

```bash
uv run python -c "from superclaude.cli.pipeline.models import PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck; print('OK')"
# Output: OK (exit code 0)
```

### Module Location

| Base Type | Module Path | Kind |
|-----------|-------------|------|
| `PipelineConfig` | `superclaude.cli.pipeline.models` | `@dataclass` |
| `Step` | `superclaude.cli.pipeline.models` | `@dataclass` |
| `StepResult` | `superclaude.cli.pipeline.models` | `@dataclass` |
| `GateCriteria` | `superclaude.cli.pipeline.models` | `@dataclass` |
| `GateMode` | `superclaude.cli.pipeline.models` | `Enum` |
| `SemanticCheck` | `superclaude.cli.pipeline.models` | `@dataclass` |

**File on disk**: `/config/workspace/IronClaude/src/superclaude/cli/pipeline/models.py`
**Package version**: `superclaude 4.2.0`
**Python version**: 3.12.3

---

## 2. Public Interface Contracts

### `PipelineConfig`

```python
@dataclass
class PipelineConfig:
    work_dir: Path = Path(".")
    dry_run: bool = False
    max_turns: int = 100
    model: str = ""
    permission_flag: str = "--dangerously-skip-permissions"
    debug: bool = False
    grace_period: int = 0
```

### `Step`

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

### `StepResult`

```python
@dataclass
class StepResult:
    step: Optional[Step] = None
    status: StepStatus = StepStatus.PENDING
    attempt: int = 1
    gate_failure_reason: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_seconds(self) -> float: ...
```

### `GateCriteria`

```python
@dataclass
class GateCriteria:
    required_frontmatter_fields: list[str]
    min_lines: int
    enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
    semantic_checks: list[SemanticCheck] | None = None
```

### `GateMode`

```python
class GateMode(Enum):
    BLOCKING = "BLOCKING"
    TRAILING = "TRAILING"
```

### `SemanticCheck`

```python
@dataclass
class SemanticCheck:
    name: str
    check_fn: Callable[[str], bool]
    failure_message: str
```

---

## 3. `__init__.py` Export Gap — CRITICAL FINDING

**Finding**: `GateMode` is NOT re-exported from `superclaude.cli.pipeline.__init__`.

```python
# superclaude.cli.pipeline imports GateMode (not exported):
# from .models import GateCriteria, PipelineConfig, SemanticCheck, Step, StepResult, StepStatus
# GateMode is absent from __init__.py __all__
```

**Implication**: Domain model code must import directly from `superclaude.cli.pipeline.models`, not from `superclaude.cli.pipeline`. The correct import for all 6 base types is:

```python
from superclaude.cli.pipeline.models import (
    PipelineConfig,
    Step,
    StepResult,
    GateCriteria,
    GateMode,
    SemanticCheck,
)
```

**Status**: Non-blocking — direct submodule imports are stable and idiomatic. No API instability; this is a documentation gap in the public API surface, not a breakage risk.

---

## 4. Deprecated / Unstable API Assessment

| Type | Deprecated? | Unstable? | Notes |
|------|-------------|-----------|-------|
| `PipelineConfig` | No | No | Stable dataclass; used by sprint and roadmap |
| `Step` | No | No | Core pipeline primitive; stable |
| `StepResult` | No | No | Core pipeline primitive; stable |
| `GateCriteria` | No | No | Stable; enforcement_tier Literal is typed |
| `GateMode` | No | No | 2-value enum; no deprecated members |
| `SemanticCheck` | No | No | Stable; Callable field is functional |

**Result**: No deprecated or unstable APIs identified. All 6 types are safe for domain model inheritance.

---

## 5. `TurnLedger` Location

**Finding**: `TurnLedger` is NOT in `superclaude.cli.pipeline.models`. It resides in `superclaude.cli.sprint.models` only.

```python
from superclaude.cli.sprint.models import TurnLedger
```

`TurnLedger` interface:
- `initial_budget: int`
- `consumed: int = 0`
- `reimbursed: int = 0`
- `can_launch() -> bool`  (requires `available() >= minimum_allocation` where minimum_allocation=5)
- `can_remediate() -> bool`
- `debit(turns: int) -> None`
- `credit(turns: int) -> None`
- `available() -> int`  (= initial_budget - consumed + reimbursed)

**Confirmed**: portified pipelines import `TurnLedger` from `sprint.models` directly — this is the established pattern per `decisions.yaml` OQ-002.

---

## 6. Kill Signal Mechanism (ClaudeProcess)

`ClaudeProcess.terminate()` in `superclaude.cli.pipeline.process` implements:
- SIGTERM → wait 10s grace period → SIGKILL escalation
- Uses process groups (`os.killpg`) when available

This is the confirmed pattern for OQ-002 (kill signal) — SIGTERM→SIGKILL with 10s grace, not SIGKILL directly.

---

## Conclusion

Architecture baseline confirmed. All 6 base types are importable and stable. Direct import from `superclaude.cli.pipeline.models` is the correct path. `TurnLedger` imports from `superclaude.cli.sprint.models`. No breaking changes or unstable APIs detected.

**EXIT_RECOMMENDATION: CONTINUE**
