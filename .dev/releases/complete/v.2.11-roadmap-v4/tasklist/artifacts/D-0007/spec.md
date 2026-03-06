# D-0007: Pipeline Integration Specification

## Integration Point

`src/superclaude/cli/roadmap/executor.py` — `apply_decomposition_pass()` function

## Pipeline Position

The decomposition pass runs **after deliverable generation** (merge step produces the final roadmap) and **before output formatting** (test-strategy step). It is exposed as `apply_decomposition_pass()` which delegates to `decompose_deliverables()` from the pipeline module.

## Execution Order

1. extract → 2. generate (parallel) → 3. diff → 4. debate → 5. score → 6. merge → **7. decomposition pass** → 8. test-strategy

## Idempotency Guarantee

Running `apply_decomposition_pass()` twice on the same input produces dict-identical output. The `.a`/`.b` ID suffix guard prevents re-decomposition of already-split deliverables.

## Exports

- `src/superclaude/cli/pipeline/__init__.py` exports `decompose_deliverables`, `is_behavioral`
- `src/superclaude/cli/roadmap/executor.py` exports `apply_decomposition_pass`

## Milestone-Order Preservation

Deliverables within each milestone maintain their relative order after decomposition. Behavioral deliverables expand in-place (D.x → D.x.a, D.x.b) without reordering adjacent deliverables.
