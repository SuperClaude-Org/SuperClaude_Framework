---
component: task-unified-tier
deliverable: D-0026
source_comparison: comparison-task-unified-tier.md
verdict: IC stronger
principle_primary: Deterministic Gates
principle_secondary: Scalable Quality Enforcement
generated: 2026-03-15
---

# Improvement Plan: Task-Unified Tier System

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM TU-001 — CRITICAL FAIL Conditions for Unconditional Gate Failure

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting the audit-validator's CRITICAL FAIL pattern (unconditional gate failure for specific failure types) as a formalized CRITICAL condition class in the tier system, not LW's behavioral-only quality gate application
**Why not full import**: LW's CRITICAL FAIL equivalent is applied through behavioral-only quality gate instructions without programmatic automation (explicitly rejected in D-0022 Principle 2); IC's CRITICAL condition class must be programmatically enforced, not only instructional.

**File paths and change description**:
- `src/superclaude/cli/pipeline/gates.py` — Add `CriticalFailCondition` dataclass to represent a CRITICAL FAIL trigger: `condition_type: str`, `description: str`, `always_blocks: bool = True`. Add `critical_conditions: list[CriticalFailCondition]` to `GateCriteria`. When any critical condition is matched, `gate_passed()` returns `(False, f"CRITICAL: {condition_type}")` regardless of all other metrics.
- `src/superclaude/cli/pipeline/models.py` — Add `GateCriteria.critical_conditions` field with default empty list.
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — Document the CRITICAL FAIL conditions for STRICT-tier tasks: (1) Sequential or Serena MCP unavailable — unconditional FAIL (cannot degrade), (2) output file absent after max turns — unconditional FAIL, (3) classification header absent in STRICT-tier task output — unconditional FAIL.
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — Sync copy.

**Rationale**: D-0022 Principle 2 (Deterministic Gates), direction 2: "Define specific failure types that force unconditional gate failure regardless of overall metrics." Also Principle 2: "a STRICT-tier task that cannot reach its Sequential + Serena MCP requirements should fail (not degrade)."

**Dependencies**: None
**Acceptance criteria**: `CriticalFailCondition` exists in gates.py; `GateCriteria` has `critical_conditions` field; a critical condition returns FAIL from `gate_passed()` regardless of other criteria; SKILL.md documents the three named CRITICAL conditions for STRICT-tier tasks.
**Risk**: Low. Additive to gate model; existing GateCriteria without critical_conditions list behaves identically to current behavior.

---

## ITEM TU-002 — Output-Type-Specific Gate Application

**Priority**: P1
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's output-type-specific gate tables (different verification for code vs. analysis vs. opinion outputs) as an output-type discriminator in IC's tier routing, not LW's behavioral-only manual quality gate application
**Why not full import**: LW's output-type gates are applied manually by human operators selecting from a quality gate menu; IC must apply output-type discrimination programmatically through the tier routing logic. LW's specific gate tables for each output type are not adopted wholesale; the discriminator pattern is.

**File paths and change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — In the verification routing table, add an `output_type` column: `code` (compile/test required), `analysis` (evidence citation required, no lint), `documentation` (structure check only, no code testing), `opinion` (CEV structure required, no automated verification). Map each compliance tier × output type to a specific verification method.
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — Sync copy.
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — Add output-type detection rules: if all affected files are `*.md` → output_type=documentation; if primary deliverable is a comparison/analysis report → output_type=analysis; if primary deliverable involves code changes → output_type=code.
- `src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md` — Sync copy.

**Rationale**: D-0022 Principle 2 (Deterministic Gates), direction 3: "Phase 7 should integrate output-type discrimination into the STRICT/STANDARD/LIGHT/EXEMPT routing so that documentation tasks are not subjected to code-verification overhead, and analysis tasks are not subjected to structural-linting gates."

**Dependencies**: TU-001 (CRITICAL conditions must be established before output-type routing can reference them)
**Acceptance criteria**: tier-classification.md has output-type detection rules for at least three output types; SKILL.md verification table has output_type column; documentation tasks skip code verification; analysis tasks use CEV evidence requirement.
**Risk**: Medium. Changes the routing logic for documentation and analysis tasks; requires that existing STRICT-tier doc tasks are re-evaluated against the new output-type routing.

---

## ITEM TU-003 — Six Universal Quality Principles as Verification Agent Vocabulary

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's six quality principles (Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy) as IC's NFR baseline vocabulary for verification agents, not LW's full quality gate menu with manual operator selection
**Why not full import**: LW's quality gate application requires manual operator selection from a quality gate menu per task type (explicitly rejected in D-0022 Principle 2 and Principle 4); IC's adoption is automated — the six principles are embedded as behavioral NFRs in the quality-engineer and self-review agents.

**File paths and change description**:
- `.claude/agents/quality-engineer.md` — Add a "Quality Principles NFR" section listing the six principles with IC-specific application guidance: (1) Verifiability — every claim must have file:line evidence, (2) Completeness — all acceptance criteria must be addressed, (3) Correctness — implementation matches specification intent, (4) Consistency — no contradictions between components, (5) Clarity — output is unambiguous and actionable, (6) Anti-Sycophancy — findings are independent of implementer's stated confidence. Each principle must have an example of how it is checked during STRICT-tier verification.
- `src/superclaude/agents/quality-engineer.md` — Sync copy.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 1: "These six principles provide a named, reproducible check framework that any verification agent can apply regardless of the specific task domain. They are adoptable as IC's NFR baseline for all STRICT-tier verification."

**Dependencies**: AP-001 (sycophancy detection is required to make Anti-Sycophancy principle meaningful)
**Acceptance criteria**: quality-engineer.md has a "Quality Principles NFR" section with all six principles named and described; each principle has an IC-specific application example; dev copy is synced.
**Risk**: Low. Agent instruction addition; no code changes.

---

## ITEM TU-004 — Confidence Threshold <0.70 Explicit Blocking

**Priority**: P2
**Effort**: XS
**Classification**: strengthen existing code
**patterns_not_mass**: true — this is an IC-native gate integrity improvement, not a LW pattern adoption

**File paths and change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — Clarify the confidence <0.70 handling: when classification confidence is below 0.70, the task classification is BLOCKED and requires user confirmation. The blocking message must include: the computed tier, the competing tier (highest alternative), and the specific keywords causing the split. The task must not proceed until the user confirms or overrides.
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — Sync copy.
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — Add explicit blocking message format for low-confidence classifications.

**Rationale**: D-0022 Principle 2 (Deterministic Gates) and existing tier system design: confidence <0.70 must produce a deterministic outcome (BLOCKED, awaiting user confirmation) not a soft degradation to the computed tier.

**Dependencies**: None
**Acceptance criteria**: SKILL.md specifies that confidence <0.70 blocks execution pending user confirmation; the blocking message format includes tier, competing tier, and keywords; no code path proceeds without confirmation at <0.70 confidence.
**Risk**: Low. Clarifying existing documented behavior; no behavioral regression for high-confidence classifications.
