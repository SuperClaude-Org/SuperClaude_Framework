# D-0022: Step Mapping with Coverage Invariant Enforcement Specification

**Task**: T03.01
**Roadmap Items**: R-050, R-051, R-052, R-053
**Date**: 2026-03-08
**Depends On**: D-0017 (Phase 1 source step registry), D-0018 (dependency DAG and gate assignments)

---

## 1. Step Mapping Engine (FR-024)

### Mapping Types

The step mapping engine transforms source steps (from Phase 1 analysis) into generated steps (for code generation). Four mapping types are supported:

| Mapping Type | Description | Justification Requirement |
|-------------|-------------|--------------------------|
| `1:1` | One source step maps to exactly one generated step | Optional — default mapping |
| `1:N` | One source step splits into N generated steps | Required — explain split rationale |
| `N:1` | N source steps merge into one generated step | Required — explain merge rationale |
| `1:0` | One source step is eliminated | Required — must provide elimination record |

### Mapping Algorithm

```
map_source_to_generated(
    source_steps: list[SourceStep],
    classified_steps: list[ClassifiedStep],
    dag: DependencyDAG,
    gate_assignments: list[GateAssignment]
) -> StepMappingResult
```

**Process**:
1. For each source step `S-NNN`, determine the appropriate mapping type:
   - If the step translates directly to one generated step → `1:1`
   - If the step requires splitting (e.g., a batch operation with pre-batch and post-batch logic) → `1:N`
   - If multiple source steps share enough implementation that they should be a single generated step → `N:1`
   - If the step has no generated equivalent (e.g., absorbed into executor logic or eliminated) → `1:0`
2. Assign generated step IDs in format `G-NNN` (sequential, zero-padded to 3 digits)
3. Record justification for all non-1:1 mappings
4. For `1:0` mappings, create an elimination record

### Generated Step ID Assignment

```
assign_generated_ids(mappings: list[StepMapping]) -> list[StepMapping]
```

Generated IDs are assigned sequentially based on the topological order of their source steps:
- `G-001`, `G-002`, ..., `G-NNN`
- For `1:N` splits, sub-IDs use the pattern `G-NNN` (each gets its own top-level ID)
- For `N:1` merges, the merged step gets a single `G-NNN` ID
- `1:0` eliminated steps receive no generated ID

### Mapping Record Structure

```yaml
step_mapping:
  - source_id: "S-001"           # Source step from Phase 1
    generated_step_ids: ["G-001"] # Generated step(s)
    mapping_type: "1:1"          # Mapping type
    justification: null          # Not required for 1:1
```

---

## 2. Elimination Records (FR-025)

### Record Structure

Steps mapped as `1:0` must have an elimination record with all three required fields:

```yaml
elimination_records:
  - source_id: "S-NNN"          # Which source step was eliminated
    reason: "<explanation>"      # Why it was eliminated
    approved_by: "auto" | "user" # Who approved the elimination
```

**Field requirements**:
- `source_id`: Must reference a valid source step ID from Phase 1 analysis (non-empty string matching `S-\d{3}`)
- `reason`: Must be a non-empty string explaining why this step has no generated equivalent
- `approved_by`: Must be either `"auto"` (if the elimination is self-evident, e.g., step absorbed into executor overhead) or `"user"` (if the elimination required user review)

### Auto-Approval Criteria

An elimination may be auto-approved (`approved_by: "auto"`) when:
- The step's function is absorbed into the executor's built-in behavior (e.g., step sequencing, retry logic)
- The step is purely orchestrational with no domain-specific output
- The step's output is a subset of another step's output (deduplication)

All other eliminations require `approved_by: "user"`.

---

## 3. Coverage Invariant Enforcement (FR-025, FR-049)

### Invariant Equation

```
|source_step_registry| == |mapped_steps| + |elimination_records|
```

Where:
- `|source_step_registry|` = number of source steps from Phase 1 (the `source_step_count` from D-0017)
- `|mapped_steps|` = number of unique source steps that have at least one generated step mapping (mapping types 1:1, 1:N, or participating in N:1)
- `|elimination_records|` = number of `1:0` elimination records

### Enforcement Algorithm

```
enforce_coverage_invariant(
    source_steps: list[SourceStep],
    mappings: list[StepMapping],
    eliminations: list[EliminationRecord]
) -> CoverageInvariantResult
```

1. Compute `source_count = len(source_steps)`
2. Compute `mapped_source_ids = set(m.source_id for m in mappings if m.mapping_type != "1:0")`
3. Compute `eliminated_source_ids = set(e.source_id for e in eliminations)`
4. Verify no overlap: `mapped_source_ids & eliminated_source_ids == {}`
5. Verify completeness: `mapped_source_ids | eliminated_source_ids == {s.source_id for s in source_steps}`
6. Verify count: `len(mapped_source_ids) + len(eliminated_source_ids) == source_count`

**On violation**: The engine halts with a blocking error:
```
COVERAGE_INVARIANT_VIOLATION: Source step count (N) != mapped (M) + eliminated (E)
Missing source steps: [S-NNN, ...]
Duplicate mappings: [S-NNN, ...]
Action: Every source step must appear in exactly one mapping or elimination record.
```

### Result Structure

```yaml
coverage_invariant:
  source_step_count: 6           # |source_step_registry|
  mapped_step_count: 6           # |mapped_steps|
  eliminated_count: 0            # |elimination_records|
  invariant_holds: true          # source == mapped + eliminated
```

---

## 4. Test Execution: sc-cleanup-audit-protocol

### Source Step Registry (from D-0017)

| source_id | Name | Classification |
|-----------|------|---------------|
| S-001 | Discover and classify files | pure_programmatic |
| S-002 | Surface scan (Pass 1) — batch | claude_assisted |
| S-003 | Structural analysis (Pass 2) — batch | claude_assisted |
| S-004 | Cross-cutting comparison (Pass 3) | claude_assisted |
| S-005 | Consolidate findings | claude_assisted |
| S-006 | Validate claims (spot-check) | claude_assisted |

### Step Mapping Result

| source_id | generated_step_ids | mapping_type | justification |
|-----------|-------------------|-------------|---------------|
| S-001 | ["G-001"] | 1:1 | null |
| S-002 | ["G-002"] | 1:1 | null |
| S-003 | ["G-003"] | 1:1 | null |
| S-004 | ["G-004"] | 1:1 | null |
| S-005 | ["G-005"] | 1:1 | null |
| S-006 | ["G-006"] | 1:1 | null |

**Mapping rationale**: The sc-cleanup-audit workflow has 6 well-defined steps with clear boundaries. Each source step maps directly to one generated step with no splits, merges, or eliminations needed. The batch operations (S-002, S-003) are handled within their respective generated steps using the executor's batch dispatch mechanism rather than splitting into separate steps.

### Elimination Records

```yaml
elimination_records: []
```

No steps eliminated — all 6 source steps have direct generated equivalents.

### Coverage Invariant Verification

```yaml
coverage_invariant:
  source_step_count: 6
  mapped_step_count: 6
  eliminated_count: 0
  invariant_holds: true    # 6 == 6 + 0
```

**Verification**:
- `source_count = 6` (from D-0017)
- `mapped_source_ids = {S-001, S-002, S-003, S-004, S-005, S-006}` → count = 6
- `eliminated_source_ids = {}` → count = 0
- No overlap: `{} & {S-001..S-006} == {}` ✅
- Completeness: `{S-001..S-006} | {} == {S-001..S-006}` ✅
- Count: `6 + 0 == 6` ✅

**Coverage invariant HOLDS** ✅

---

## 5. Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| Step mapping engine correctly records all 4 mapping types (1:1, 1:N, N:1, 1:0) with justifications | ✅ PASS — all types defined with justification requirements |
| Coverage invariant `\|source_step_registry\| == \|mapped_steps\| + \|elimination_records\|` verified for test workflow | ✅ PASS — 6 == 6 + 0 |
| All elimination records contain non-empty source_id, reason, and approved_by fields | ✅ PASS — no eliminations in test workflow; field requirements specified |
| Step mapping specification documented in D-0022/spec.md | ✅ PASS — this document |
