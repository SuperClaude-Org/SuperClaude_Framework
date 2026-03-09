# Decision Log: v2.20 WorkflowEvolution Pre-Implementation Decisions

| Field | Value |
|---|---|
| Deliverable ID | D-0009 |
| Phase | Phase 1 — Pre-Implementation Decisions |
| Date | 2026-03-09 |
| Total Decisions | 8 |
| Status | COMPLETE |

## Decision Index

| # | OQ ID | Decision ID | Title | Artifact |
|---|---|---|---|---|
| 1 | OQ-001 | D-0001 | Cross-Reference Strictness Rollout | artifacts/D-0001/spec.md |
| 2 | OQ-004 | D-0002 | Fidelity vs Reflect Step Ordering | artifacts/D-0002/spec.md |
| 3 | OQ-006 | D-0003 | Deviation Table Schema | artifacts/D-0003/spec.md |
| 4 | OQ-007 | D-0004 | Multi-Agent Mode Deferral | artifacts/D-0004/spec.md |
| 5 | OQ-002 | D-0005 | Module Placement | artifacts/D-0005/spec.md |
| 6 | OQ-003 | D-0006 | Count Cross-Validation Policy | artifacts/D-0006/spec.md |
| 7 | OQ-005 | D-0007 | MEDIUM Severity Blocking Policy | artifacts/D-0007/spec.md |
| 8 | OQ-008 | D-0008 | Step Timeout vs NFR Mismatch | artifacts/D-0008/spec.md |

---

## Decision Entries

### 1. OQ-001 — Cross-Reference Strictness Rollout

| Field | Value |
|---|---|
| Decision | Warning-first for v2.20, blocking enforcement in v2.21 |
| Rationale | Existing roadmaps may have dangling cross-references; immediate blocking risks false-positive pipeline failures (RSK-003). Warning-first provides a migration window. |
| Impacted FRs | FR-019 |
| Risk Mitigation | RSK-003 |

---

### 2. OQ-004 — Fidelity vs Reflect Step Ordering

| Field | Value |
|---|---|
| Decision | Spec-fidelity runs after reflect; complementary validation (reflect=structural, fidelity=content) |
| Rationale | Reflect catches structural defects first, ensuring spec-fidelity operates on a sound document. Running fidelity before reflect wastes tokens on potentially malformed input. |
| Impacted FRs | FR-008 |

---

### 3. OQ-006 — Deviation Table Schema

| Field | Value |
|---|---|
| Decision | 7-column FR-051.4 schema with generic Upstream/Downstream Quote names; Source Pair encoded in frontmatter |
| Rationale | Generic column names enable schema reuse across document pairs. 7-column schema is simpler and avoids redundancy with frontmatter source_pair field. |
| Impacted FRs | FR-051.4, FR-026 |
| Supersedes | FR-051.1 AC-5 (8-column schema) |

---

### 4. OQ-007 — Multi-Agent Mode Deferral

| Field | Value |
|---|---|
| Decision | Defer FR-012 to v2.21; document conservative merge protocol only (highest severity wins, validation_complete=false if any agent fails) |
| Rationale | Spec provides insufficient detail for reliable implementation. Partial implementation introduces dead code. Deferral reduces v2.20 scope. |
| Impacted FRs | FR-012 |

---

### 5. OQ-002 — Module Placement

| Field | Value |
|---|---|
| Decision | New `src/superclaude/cli/tasklist/` module with __init__.py, commands.py, executor.py, gates.py, prompts.py |
| Rationale | Tasklist validation has distinct responsibilities from roadmap generation. New module follows AC-006 and existing cli/ conventions. |
| Impacted FRs | AC-006 |

---

### 6. OQ-003 — Count Cross-Validation Policy

| Field | Value |
|---|---|
| Decision | Warning log for frontmatter-vs-table-row count mismatches; not a gate blocker |
| Rationale | LLMs frequently miscalculate counts. Blocking on count mismatches creates false-positive pipeline halts. Warnings enable auditability without disruption. |
| Impacted FRs | NFR-006 |

---

### 7. OQ-005 — MEDIUM Severity Blocking Policy

| Field | Value |
|---|---|
| Decision | HIGH=blocking, MEDIUM=non-blocking in v2.20; MEDIUM-blocks policy revisited in v2.21 |
| Rationale | HIGH-only blocking provides safety without over-constraining initial deployment. v2.20 data collection informs v2.21 policy refinement. |
| Impacted FRs | (gate design) |

---

### 8. OQ-008 — Step Timeout vs NFR Mismatch

| Field | Value |
|---|---|
| Decision | 120s = p95 performance target (NFR measurement); 600s = hard timeout (runtime enforcement). Measure during Phases 3-4. |
| Rationale | Distinct purposes: 120s is a quality metric, 600s is a safety mechanism. LLM response variance requires 5x headroom. Early measurement enables iterative optimization. |
| Impacted FRs | NFR-001, NFR-002, NFR-009 |

---

## Cross-Decision Consistency

All 8 decisions have been verified for mutual consistency:

- **Graduated enforcement pattern**: D-0001 (warning-first cross-refs) and D-0007 (MEDIUM non-blocking) establish a consistent pattern of conservative initial enforcement.
- **Schema and module alignment**: D-0003 (7-column schema) is consumed by D-0005 (tasklist module) without conflict.
- **Step ordering and module boundaries**: D-0002 (reflect → spec-fidelity) operates within `roadmap/executor.py`, separate from D-0005's `cli/tasklist/` module.
- **Scope control**: D-0004 (defer multi-agent) reduces complexity consistently with the conservative rollout approach of other decisions.
- **Performance values**: D-0008 (120s/600s distinction) is referenced consistently across NFR-001, NFR-002, and NFR-009.

## Unresolved Blockers

None. All 8 open questions are resolved. Phase 2 implementation can begin without ambiguity.
