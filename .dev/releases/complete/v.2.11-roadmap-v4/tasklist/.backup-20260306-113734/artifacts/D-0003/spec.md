# D-0003: Decomposition Function Specification

## Function Signature

```python
def decompose_deliverables(deliverables: list[Deliverable]) -> list[Deliverable]
```

## Location

`src/superclaude/cli/pipeline/deliverables.py`

## ID Suffix Rules

- Behavioral deliverable `D.x` → `D.x.a` (implement) + `D.x.b` (verify)
- Non-behavioral deliverables pass through with original IDs
- Already-decomposed deliverables (IDs ending `.a` or `.b`) are not re-decomposed

## Idempotency

Running `decompose_deliverables(decompose_deliverables(input))` produces identical output to a single pass. The `.a`/`.b` suffix check prevents re-decomposition.

## Verify Description Format

```
Verify {D.x.a}: validate internal correctness of '{original description}'
— input domain boundaries, operand identity, post-condition assertions on internal state
```

## Metadata

Original metadata is copied (shallow dict copy) to both `.a` and `.b` deliverables.
