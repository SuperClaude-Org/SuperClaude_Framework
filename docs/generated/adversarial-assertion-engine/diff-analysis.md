# Diff Analysis: Assertion Engine Options A, B, C

## Structural Differences

| Aspect | A (Inline DSL) | B (Structured Block) | C (Hardcoded Python) |
|---|---|---|---|
| Location in tasklist | Single row in metadata table | New `**Assertions:**` block | Single row in metadata table |
| Assertion format | Single-line DSL string | Multi-line, one assertion per line | Python function name reference |
| Logic location | Embedded in markdown | Embedded in markdown | Python source module |
| Parser requirement | Custom tokenizer + evaluator | Per-line parser + evaluator | Dict lookup only |
| Runtime dependency | Parser + evaluator (~150 LOC) | Parser + evaluator (~120 LOC) | Function registry (~30 LOC) |

## Content Differences

### Assertion Specification
- **A**: `output contains "PINEAPPLE" -> WORKING; exit_code != 0 -> CLI FAILURE; default -> BROKEN`
- **B**: Multi-line with `stdout contains "PINEAPPLE": label=WORKING`, `exit_code == 0: required`, `default: label=BROKEN`
- **C**: `| Classifier | empirical_gate_v1 |` pointing to a Python lambda/function

### Semantic Model
- **A**: First-match-wins evaluation, no distinction between "task failure" and "classification label"
- **B**: Explicit `required` vs `label=` distinction. `required` means executor-level failure; `label=` means classification outcome
- **C**: Full Python semantics. Any distinction can be modeled. Return type is developer-defined

### Extensibility Model
- **A/B**: Extend by adding new DSL operators (regex, numeric ranges, multi-field). Requires parser changes
- **C**: Extend by writing new Python functions. No parser changes ever needed

## Contradictions

1. **Self-describing vs. separation of concerns**: A and B prioritize the tasklist being a complete specification. C prioritizes separation of logic (Python) from configuration (markdown). These are fundamentally different architectural philosophies.

2. **Generator workflow**: A and B assume the generator produces the assertion logic. C assumes the assertion logic is pre-written in the executor codebase and the generator merely references it. Both are valid but lead to different development workflows.

## Unique Contributions

- **A only**: Maximum information density -- everything in one table row
- **B only**: `required` keyword providing explicit pass/fail semantics distinct from classification labels; explicit `stderr contains` targeting
- **C only**: Leverages existing codebase patterns (`FailureClassifier`, `TrailingGatePolicy`); standard Python testability; zero parsing risk; unlimited expressiveness

## Codebase Context

The existing codebase contains several patterns relevant to this decision:
- `FailureClassifier` in `src/superclaude/cli/sprint/diagnostics.py` -- already classifies failures in Python
- `TrailingGatePolicy` in `src/superclaude/cli/pipeline/trailing_gate.py` -- gate evaluation in Python
- `GateCriteria` in `src/superclaude/cli/pipeline/models.py` -- criteria modeling in Python dataclasses
- The tasklist metadata table already has 15+ fields; adding one more row is negligible cost
