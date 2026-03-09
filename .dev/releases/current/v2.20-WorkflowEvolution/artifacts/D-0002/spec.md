# Decision D-0002: Fidelity vs Reflect Step Ordering

| Field | Value |
|---|---|
| Decision ID | D-0002 |
| Open Question | OQ-004 |
| Related Requirements | FR-008 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

Should the spec-fidelity step run before or after the existing reflect validation step? Does spec-fidelity make reflect redundant for roadmap fidelity checking?

## Decision

**Spec-fidelity runs after reflect. The two steps are complementary, not redundant.**

### Pipeline Step Order

```
... → test-strategy → reflect → spec-fidelity → ...
```

### Step Responsibilities

| Step | Validates | Focus |
|---|---|---|
| reflect | Structural quality | Roadmap structure, section completeness, formatting consistency, internal coherence |
| spec-fidelity | Content accuracy | Requirement coverage, traceability ID validity, deviation detection against source spec |

## Rationale

- **Reflect** catches structural defects (missing sections, broken formatting, incoherent flow) that would make spec-fidelity analysis unreliable. Running reflect first ensures spec-fidelity operates on a structurally sound document.
- **Spec-fidelity** performs content-level validation (are all FRs addressed? are traceability IDs valid?) that reflect is not designed to assess.
- Running fidelity before reflect would waste tokens analyzing a potentially malformed document.
- The two steps form a validation pipeline: structural integrity → content accuracy.

## Impacts

- **FR-008**: The `spec-fidelity` step is inserted into `_build_steps()` after `reflect`, not after `test-strategy` directly. The ordering is: `test-strategy → reflect → spec-fidelity`.
- **Pipeline executor**: No changes to existing reflect step behavior. Spec-fidelity is purely additive.
- **Phase 5 verification**: Gate interaction ordering becomes `reflect → spec-fidelity → tasklist-fidelity`.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-004 | Spec-fidelity runs after reflect; complementary validation | FR-008 |
