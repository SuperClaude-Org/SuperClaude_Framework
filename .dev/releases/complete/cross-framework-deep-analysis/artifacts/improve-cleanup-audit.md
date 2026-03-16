---
component: cleanup-audit
deliverable: D-0026
source_comparison: comparison-cleanup-audit.md
verdict: IC stronger
principle_primary: Evidence Integrity
principle_secondary: Deterministic Gates
generated: 2026-03-15
---

# Improvement Plan: Cleanup-Audit CLI

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM CA-001 — Presumption of Falsehood in Audit Agent Instructions

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's Presumption of Falsehood epistemic stance, not LW's anti-hallucination structured evidence table enforcement for all output types
**Why not full import**: LW's full implementation requires per-claim structured evidence tables with mandatory FAS -100 penalty scoring; IC's audit system needs only the epistemic stance (start from "unverified") applied to agent behavioral instructions, not a new evidence-accounting infrastructure.

**File paths and change description**:
- `src/superclaude/agents/audit-scanner.md` — Add to the behavioral instructions: "Default classification status for all file findings is UNVERIFIED until evidence is gathered. Do not assume a file is safe-to-delete or safe-to-keep without positive evidence. If no importers are found for a file, document 'no importers found' explicitly — do not leave absence of evidence undocumented."
- `src/superclaude/agents/audit-validator.md` — Add to validation instructions: "Treat all scanner findings as unverified claims. Each finding requires positive confirmation before PASS classification. Document when confirmation evidence is absent (not just when it is found)."
- `.claude/agents/audit-scanner.md` and `.claude/agents/audit-validator.md` — Sync copies (via `make sync-dev`).

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 2: "Audit agents should default classification status to 'unverified' until evidence is gathered, not 'classified' pending flagging."

**Dependencies**: None (foundational for CA-002)
**Acceptance criteria**: audit-scanner.md contains the word "UNVERIFIED" as a default classification state in its instructions; audit-validator.md contains explicit instructions to document absence of confirmation; both agent files have matching dev copies.
**Risk**: Low. Agent instruction additions; no code changes; behavioral improvement only.

---

## ITEM CA-002 — Mandatory Negative Evidence Documentation

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's mandatory negative evidence documentation requirement (not LW's structured evidence tables or PABLOV chain)
**Why not full import**: LW implements negative evidence through per-claim tables in all output types at all tiers; IC needs mandatory negative evidence only in audit report outputs (not in all verification outputs at all tiers).

**File paths and change description**:
- `src/superclaude/cli/audit/scanner_schema.py` — In the Phase 1 schema, add an optional but logged `negative_evidence` field to finding records: when `has_references` is False and no importers are found, the field must be set to `"no_importers_found"` or similar value. The schema validator should warn (not error) when this field is absent for a zero-reference finding.
- `src/superclaude/cli/audit/classification.py` — In `classify_finding()`, when `has_references=False`, set a `negative_evidence_documented` flag on the `ClassificationResult`. This flag is used by the audit report formatter to verify that negative evidence is explicitly recorded.
- `src/superclaude/cli/cleanup_audit/executor.py` — In the report generation step, assert that all REVIEW/DELETE findings with zero references have `negative_evidence_documented=True`. Log a warning for any finding where this is absent.

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 3: "When an agent finds no importers, no errors, or no supporting evidence for a claim, 'not found' must be explicitly documented as a result. Silent omission is not acceptable."

**Dependencies**: CA-001 (epistemic stance must be established in agent instructions first)
**Acceptance criteria**: `classify_finding()` sets `negative_evidence_documented` on zero-reference findings; executor generates a warning when the flag is absent in a REVIEW/DELETE finding; at least one test verifies the flag is set correctly.
**Risk**: Low. Schema addition is backward-compatible (optional field); warning does not block pipeline.

---

## ITEM CA-003 — Typed State Transitions in Audit Pass Progression

**Priority**: P1
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's typed inter-agent communication (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE, BLOCKED) as IC-native typed state transitions for the G-001 → G-002 → G-003 audit pass progression
**Why not full import**: LW's typed message protocol is implemented via bash inter-process communication; IC's audit passes are Python function-to-function calls. The typed state concept is adoptable; the IPC mechanism is not.

**File paths and change description**:
- `src/superclaude/cli/cleanup_audit/executor.py` — Define an `AuditPassState` enum with values: `PENDING`, `SCANNING`, `SCAN_COMPLETE`, `ANALYZING`, `ANALYSIS_COMPLETE`, `VALIDATING`, `DONE`, `BLOCKED`. At each pass transition (G-001 → G-002, G-002 → G-003), emit the current state to the audit logger. If a pass returns an empty result set, emit `BLOCKED` with reason.
- `src/superclaude/cli/pipeline/models.py` — Add `AuditPassState` to the models module export list so consuming code can reference it without importing from executor.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 5: "For IC components that involve sequential agent invocation (cleanup-audit's G-001 → G-002 → G-003 progression), adopt explicit typed state transitions. BLOCKED as a first-class message type prevents silent failures in agent coordination."

**Dependencies**: CA-001, CA-002
**Acceptance criteria**: `AuditPassState` enum exists in executor.py; BLOCKED state is emitted when a pass produces an empty result; each G-001/G-002/G-003 transition logs the current state.
**Risk**: Medium. New enum and state emission; requires integration test across all three passes.

---

## ITEM CA-004 — Executor Validation Gate Before Agent Invocation

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's executor validation gate pattern (validate input before starting execution) without LW's permissionMode:bypassPermissions or all-opus model requirement
**Why not full import**: LW's rf-task-executor validation gate is tied to its permissionMode:bypassPermissions agent execution model, which is explicitly rejected in D-0022 Principle 4. The input validation pattern is adoptable; the permission model is not.

**File paths and change description**:
- `src/superclaude/cli/cleanup_audit/executor.py` — At the beginning of `execute_cleanup_audit()`, before invoking any audit pass, validate: (a) target directory exists and is readable, (b) `--batch-size` is within valid range (1–100), (c) `--focus` value is a known domain (`infrastructure|frontend|backend|all`). If validation fails, emit `AuditPassState.BLOCKED` with reason and return early (fail-fast, not fail-mid-execution).
- `src/superclaude/cli/cleanup_audit/commands.py` — Move CLI-level validation (Click option types) to complement executor-level validation, not replace it. Executor must re-validate inputs it receives from any call site (not only the CLI).

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 6: "Before any agent begins execution, it should validate its input file/specification and emit BLOCKED if the structure is invalid."

**Dependencies**: CA-003 (BLOCKED state enum must exist)
**Acceptance criteria**: `execute_cleanup_audit()` validates inputs before the first pass invocation; invalid target path returns BLOCKED immediately; unit test for each validation condition.
**Risk**: Low. Input validation is additive; no existing code paths are removed.
