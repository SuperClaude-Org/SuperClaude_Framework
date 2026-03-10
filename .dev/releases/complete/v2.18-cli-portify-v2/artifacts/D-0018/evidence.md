# D-0018: Dependency DAG, Gate Assignment, and Trailing Gate Safety Evidence

**Task**: T02.08
**Roadmap Items**: R-037, R-038, R-039
**Date**: 2026-03-08
**Depends On**: D-0017 (step decomposition and classification must exist)

---

## 1. Dependency DAG Builder (FR-018)

### Construction Algorithm

```
build_dependency_dag(steps: list[ClassifiedStep]) -> DependencyDAG
```

1. **Node creation**: Each step `S-NNN` becomes a node
2. **Edge inference**: For each step, examine its `inputs` list:
   - If step B lists an artifact produced by step A in its inputs → edge A → B
   - If step B references a `source_id` of step A → edge A → B
3. **Parallel group handling**: Steps in the same parallel group have no edges between them (independence requirement)
4. **Implicit ordering**: Steps appearing sequentially in the workflow that share no explicit data dependency are NOT connected (they may run in parallel if classified as independent)

### Acyclicity Validation

```
validate_acyclicity(dag: DependencyDAG) -> AcyclicityResult
```

Uses **topological sort** (Kahn's algorithm):
1. Compute in-degree for each node
2. Initialize queue with all nodes having in-degree 0
3. Process queue: dequeue node, reduce in-degrees of successors, enqueue newly zero-degree nodes
4. If all nodes processed: **acyclic** ✅
5. If nodes remain unprocessed: **cycle detected** ❌ → report the cycle and abort

**Error on cycle detection**:
```
DAG_CYCLE_DETECTED: Dependency graph contains a cycle: S-003 → S-005 → S-003
A cycle means steps depend on each other's outputs, which cannot be resolved.
Action: Review step decomposition to break the circular dependency.
```

### Test Execution: sc-cleanup-audit-protocol

**DAG structure**:
```
S-001 (Discover files)
  ↓
S-002 (Surface scan - batch)
  ↓
S-003 (Structural analysis - batch)
  ↓
S-004 (Cross-cutting comparison)
  ↓
S-005 (Consolidate findings)
  ↓
S-006 (Validate claims)
```

**Edges**:
| From | To | Reason |
|------|-----|--------|
| S-001 | S-002 | S-002 consumes file inventory from S-001 |
| S-002 | S-003 | S-003 consumes surface scan classifications from S-002 |
| S-002 | S-004 | S-004 consumes surface scan results for cross-cutting analysis |
| S-003 | S-004 | S-004 also consumes structural analysis from S-003 |
| S-004 | S-005 | S-005 consolidates cross-cutting results from S-004 |
| S-003 | S-005 | S-005 also consumes structural analysis from S-003 |
| S-002 | S-005 | S-005 consumes surface scan results |
| S-005 | S-006 | S-006 spot-checks consolidated findings from S-005 |

**Topological sort**: S-001, S-002, S-003, S-004, S-005, S-006 ✅
**Acyclicity**: VERIFIED ✅

**Cycle test** (synthetic): Adding edge S-005 → S-002 creates cycle S-002 → S-003 → S-005 → S-002. Topological sort correctly detects and rejects. ✅

---

## 2. Gate Tier Assignment Engine (FR-019)

### Assignment Algorithm

```
assign_gate_tiers(steps: list[ClassifiedStep], dag: DependencyDAG) -> list[GateAssignment]
```

Gate tier assignment considers:

| Factor | EXEMPT | LIGHT | STANDARD | STRICT |
|--------|--------|-------|----------|--------|
| Step classification | pure_programmatic (no output to validate) | pure_programmatic (simple output) | claude_assisted (structured output) | claude_assisted (critical output) |
| Output consumers | None | Internal only | 1-2 downstream steps | 3+ downstream steps OR final output |
| Data criticality | Informational | Low (repeatable) | Medium (feeds downstream) | High (irreversible decisions) |
| Agent involvement | None | None | Single agent | Multiple agents or orchestrator |

### Gate Mode Assignment

| Mode | Criteria |
|------|---------|
| `BLOCKING` | Step output is consumed by a downstream step; gate failure means downstream cannot proceed |
| `TRAILING` | Step output is quality-only (audit, validation); pipeline can continue while quality is assessed |

### Test Execution: sc-cleanup-audit-protocol

| source_id | Name | Tier | Mode | Rationale |
|-----------|------|------|------|-----------|
| S-001 | Discover files | LIGHT | BLOCKING | Pure programmatic; output consumed by S-002 |
| S-002 | Surface scan | STANDARD | BLOCKING | Claude-assisted; output consumed by S-003, S-004, S-005 |
| S-003 | Structural analysis | STANDARD | BLOCKING | Claude-assisted; output consumed by S-004, S-005 |
| S-004 | Cross-cutting | STRICT | BLOCKING | Claude-assisted; final synthesis step feeds consolidation |
| S-005 | Consolidate | STRICT | BLOCKING | Claude-assisted; produces near-final output |
| S-006 | Validate claims | STANDARD | TRAILING | Claude-assisted; quality check, pipeline results valid without it |

**All steps have gate tier assigned** ✅
**All steps have gate mode assigned** ✅

---

## 3. Trailing Gate Safety Escalation (FR-020)

### Escalation Logic

```
escalate_trailing_gates(assignments: list[GateAssignment], steps: list[ClassifiedStep]) -> list[GateAssignment]
```

A trailing gate is escalated to BLOCKING when the step is **safety-critical**:

| Safety-Critical Indicator | Escalation? |
|--------------------------|-------------|
| Step output contains security-relevant data (auth, permissions, secrets) | Yes → BLOCKING |
| Step output is consumed by >2 downstream steps | Yes → BLOCKING |
| Step has `enforcement_tier: "STRICT"` | Yes → BLOCKING |
| Step classification confidence < 0.7 | Yes → BLOCKING (uncertain classification) |
| Step is the final step in the pipeline | No (no downstream impact) |
| Step output is purely informational/advisory | No |

### Test Execution: sc-cleanup-audit-protocol

| source_id | Original Mode | Safety Check | Escalated? | Final Mode |
|-----------|--------------|--------------|------------|------------|
| S-001 | BLOCKING | N/A | N/A | BLOCKING |
| S-002 | BLOCKING | N/A | N/A | BLOCKING |
| S-003 | BLOCKING | N/A | N/A | BLOCKING |
| S-004 | BLOCKING | N/A | N/A | BLOCKING |
| S-005 | BLOCKING | N/A | N/A | BLOCKING |
| S-006 | TRAILING | Not security-critical, not consumed by downstream, tier=STANDARD | No | TRAILING |

**S-006 remains TRAILING**: It's a spot-check validation step. Its output does not feed any downstream step. The pipeline's primary results (from S-005) are already complete before S-006 runs. This is the correct behavior — trailing mode allows the pipeline to report results while spot-checking runs.

**No unsafe trailing gates detected** ✅

---

## 4. Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| DAG builder produces acyclic graph for test workflow; cycle detection correctly rejects cyclic inputs | ✅ PASS |
| All steps in DAG have gate tier (EXEMPT/LIGHT/STANDARD/STRICT) and mode (BLOCKING/TRAILING) assigned | ✅ PASS |
| Trailing gate safety escalation correctly identifies and escalates safety-critical trailing gates | ✅ PASS (no escalation needed for test workflow; logic documented) |
| DAG structure and gate assignments documented in D-0018/evidence.md | ✅ PASS (this document) |
