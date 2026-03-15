# Refactoring Plan: Python Classifier-Based Assertion Engine

## Base Selection: Option C (Hardcoded Python Classifiers)

This plan integrates strengths from Options A and B into the Option C base.

---

## Architecture

### New Module: `src/superclaude/cli/sprint/classifiers.py`

```python
"""Task output classifiers for pre-sprint Python executor.

Each classifier receives captured command output and returns a
ClassificationResult with a label and pass/fail status.

Register new classifiers by adding entries to the CLASSIFIERS dict.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    """Result of classifying task command output.

    Attributes:
        label: Human-readable classification (e.g., "WORKING", "BROKEN").
        passed: Whether the task execution itself succeeded (distinct from
                what the classification label means semantically).
        detail: Optional explanation of the classification decision.
    """
    label: str
    passed: bool
    detail: str = ""
```

### Classifier Function Signature

```python
Classifier = Callable[[int, str, str], ClassificationResult]
#                       ^     ^     ^
#                  exit_code stdout stderr
```

### Classifier Registry

```python
CLASSIFIERS: dict[str, Classifier] = {
    "empirical_gate_v1": _empirical_gate_v1,
    "cli_availability":  _cli_availability,
    "file_flag_check":   _file_flag_check,
}
```

---

## Integration Points

### IP-1: Structured result type (from Option B's `required` semantics)
- **Risk**: Low
- **Rationale**: Option B's `required` keyword distinguishes "task failed to execute" from "task executed but classified as BROKEN." The `ClassificationResult.passed` field captures this distinction in a type-safe way.
- **Implementation**: `ClassificationResult(label="BROKEN", passed=True)` means the executor ran correctly but the CLI feature is broken. `ClassificationResult(label="CLI FAILURE", passed=False)` means the task itself failed.

### IP-2: Tasklist-visible classifier name (from Option A's inline visibility)
- **Risk**: Low
- **Rationale**: Option A's strength was that assertions are visible in the metadata table. Adding a `| Classifier |` row achieves this without a DSL.
- **Implementation**: Add `| Classifier | empirical_gate_v1 |` row to per-task metadata table. The pre-sprint Python executor reads this field and dispatches to the registered function.
- **Tasklist format example**:
  ```markdown
  | Field | Value |
  |---|---|
  | ... | ... |
  | Classifier | empirical_gate_v1 |
  ```

### IP-3: Explicit stdout/stderr separation (from Option B)
- **Risk**: Low
- **Rationale**: Option B explicitly distinguished `stdout contains` from `stderr contains`. The classifier function signature `(exit_code, stdout, stderr)` provides the same capability.
- **Implementation**: All three arguments are always provided. Classifiers that only need exit_code can ignore stdout/stderr.

---

## Non-Integrated Elements

| Element | Source | Reason for Exclusion |
|---|---|---|
| DSL parsing | A, B | Disproportionate cost for 3 known use cases. Can be added later as a layer that produces classifier functions. |
| `default` keyword | A, B | Python's `else` clause serves the same purpose. |
| First-match-wins evaluation | A | Python control flow (if/elif/else) is clearer. |
| Per-line independence | B | Not needed when logic is a Python function. |

---

## Implementation Tasks

### Task 1: Create classifiers module
- **File**: `src/superclaude/cli/sprint/classifiers.py`
- **Content**: `ClassificationResult` dataclass, `Classifier` type alias, 3 classifier functions, `CLASSIFIERS` registry dict
- **Effort**: XS (~30-50 LOC)
- **Risk**: Low

### Task 2: Integrate with pre-sprint executor
- **File**: `src/superclaude/cli/sprint/executor.py` (or new pre-sprint executor module)
- **Action**: After `subprocess.run()` captures output, look up `| Classifier |` from task metadata. If present, call `CLASSIFIERS[name](exit_code, stdout, stderr)`. Write `ClassificationResult` to evidence artifact.
- **Effort**: S (~20-30 LOC)
- **Risk**: Low

### Task 3: Update tasklist metadata schema
- **File**: Tasklist generator in `/sc:tasklist` command
- **Action**: Add optional `| Classifier |` row to per-task metadata table when task has `execution_mode: python` and needs output classification.
- **Effort**: XS (~5-10 LOC template change)
- **Risk**: Low

### Task 4: Write classifier tests
- **File**: `tests/sprint/test_classifiers.py`
- **Action**: Standard pytest for each classifier function. Test matrix: exit_code variations, stdout content variations, stderr content. Verify ClassificationResult fields.
- **Effort**: S (~50-80 LOC)
- **Risk**: Low

### Task 5: Document classifier authoring
- **File**: Docstrings in `classifiers.py` + brief section in developer guide
- **Action**: Document function signature, registration process, naming conventions.
- **Effort**: XS
- **Risk**: Low

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Classifier name not found in registry | Medium | Low | Raise `KeyError` with helpful message listing available classifiers |
| Classifier function raises exception | Low | Medium | Wrap in try/except, record error in evidence artifact, mark task as failed |
| Future need exceeds classifier pattern | Low | Low | Add DSL parser as optional layer that compiles to classifier functions |
| Naming collisions in registry | Very Low | Low | Enforce naming convention: `{purpose}_{version}` (e.g., `empirical_gate_v1`) |

---

## Migration Path (if C proves insufficient)

If a DSL becomes needed (e.g., non-developer tasklist authors need to specify custom assertions):

1. Build DSL parser (Option B's format recommended over A's for readability)
2. Parser output: a `Classifier` callable (same signature)
3. Add `| Assert |` row as alternative to `| Classifier |`
4. Executor checks for `| Assert |` first (inline DSL), falls back to `| Classifier |` (registered function)
5. Zero changes to existing classifier functions or the `ClassificationResult` type

This migration path is possible precisely because Option C establishes a clean function interface that any future DSL can target.
