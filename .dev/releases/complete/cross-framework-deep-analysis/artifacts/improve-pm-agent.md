---
component: pm-agent
deliverable: D-0026
source_comparison: comparison-pm-agent.md
verdict: split by context
principle_primary: Evidence Integrity
principle_secondary: Bounded Complexity
generated: 2026-03-15
---

# Improvement Plan: PM Agent

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM PM-001 — Filesystem-Verified Flag in SelfCheckProtocol

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's claim/proof distinction (worker_handoff vs. programmatic_handoff) as a `filesystem_verified` flag in SelfCheckProtocol.validate(), not the full five-artifact PABLOV chain
**Why not full import**: LW's PABLOV chain requires sequential evidence-gathering through five structured artifacts per task; IC's SelfCheckProtocol validates post-implementation correctness in a single call. Adopting the full five-artifact chain would prohibit IC's parallelism and add overhead beyond its current scope. Only the claim/proof distinction is adopted.

**File paths and change description**:
- `src/superclaude/pm_agent/self_check.py` — In `SelfCheckProtocol.validate(implementation: dict)`, add a `filesystem_verified: bool` field to the return structure. The field is `True` only when the implementation dict contains a `artifact_path` key whose value points to a file that exists on disk at validation time. Self-reported completions where `artifact_path` is absent or the file does not exist return `filesystem_verified=False`. The overall `passed` result requires `filesystem_verified=True` for STRICT-tier implementations.
- `src/superclaude/pm_agent/self_check.py` — Add a 5th validation question to the 4-question checklist: "Is there a filesystem-verifiable artifact proving this implementation is complete?" Document the question in the method docstring.
- Tests: `tests/pm_agent/` — Add tests verifying that `filesystem_verified=False` when artifact_path is absent; `filesystem_verified=True` when path exists.

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 1: "SelfCheckProtocol should distinguish between a self-reported claim and a filesystem-verifiable artifact." The `filesystem_verified` flag is analogous to LW's `programmatic_handoff` distinction.

**Dependencies**: None
**Acceptance criteria**: `validate()` returns a result with `filesystem_verified` field; STRICT-tier validation fails if `filesystem_verified=False`; tests pass for both cases.
**Risk**: Low. Additive field; backward-compatible (existing callers get the new field in the result without needing to check it unless they explicitly test STRICT tier).

---

## ITEM PM-002 — Mandatory Negative Evidence Documentation in SelfCheckProtocol

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's mandatory negative evidence documentation requirement for PM Agent self-check outputs, not LW's all-output-types per-claim evidence tables
**Why not full import**: LW's negative evidence requirement applies to all output types at all tiers with mandatory structured tables; IC needs this requirement only in PM Agent's SelfCheckProtocol.validate() for the specific case where no evidence is found for a claim.

**File paths and change description**:
- `src/superclaude/pm_agent/self_check.py` — In the validation logic, when a red-flag check finds NO issue (e.g., no hallucination signals detected), record the finding explicitly as `"no_hallucination_signals_found"` (not as silent absence). The `issues` list in the return value should include both positive flags (issues found) and negative confirmations (checks that found nothing, explicitly).
- `src/superclaude/pm_agent/self_check.py` — Add a `negative_evidence` list to the return structure containing all checks where no evidence was found. This mirrors the `issues` list but for confirmed-absent conditions.

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 3: "'Not found' must be explicitly documented as a result. Silent omission is not acceptable."

**Dependencies**: PM-001
**Acceptance criteria**: `validate()` returns both an `issues` list and a `negative_evidence` list; a clean validation produces a non-empty `negative_evidence` list (confirming each check was performed and found nothing); tests verify this.
**Risk**: Low. Additive return structure field; existing callers are not broken.

---

## ITEM PM-004 — ReflexionPattern: Presumption of Falsehood Default Stance

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's Presumption of Falsehood stance for the ReflexionPattern's solution retrieval, not LW's mandatory PABLOV sequential verification for all reflexion outputs
**Why not full import**: LW's Presumption of Falsehood is implemented through PABLOV's sequential five-artifact chain that prohibits parallelism; IC's ReflexionPattern runs as a single-session lookup. Only the stance (treat retrieved solutions as unverified until confirmed) is adopted.

**File paths and change description**:
- `src/superclaude/pm_agent/reflexion.py` — In `ReflexionPattern.get_solution(error_info)`, add a `confidence: float` field to the return value (or a wrapper `SolutionResult` dataclass). Returned solutions from JSONL storage are `confidence=0.5` (unverified) by default. Solutions that have been applied and confirmed (via `record_error()` with a `verified=True` flag) receive `confidence=0.8+`. Callers that auto-apply solutions should check `confidence >= 0.7` before applying without prompting the user.
- `src/superclaude/pm_agent/reflexion.py` — Add `verified: bool = False` parameter to `record_error()`. When `verified=True`, update the stored solution's confidence score.

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 1: The Presumption of Falsehood principle extends to all evidence-gathering agents including the ReflexionPattern — retrieved solutions are claims until confirmed.

**Dependencies**: PM-001 (filesystem_verified flag establishes the claim/proof pattern; this item extends it to reflexion)
**Acceptance criteria**: `get_solution()` returns a result with `confidence` field; new solutions default to `confidence=0.5`; verified solutions reach `confidence >= 0.8`; callers can check confidence before auto-applying.
**Risk**: Low. Additive field; no existing solution storage is invalidated (existing entries default to confidence=0.5 on read).

---

## ITEM PM-003 — Model Tier Proportionality for PM Agent Operations

**Priority**: P2
**Effort**: XS
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's model tier proportionality principle as IC policy documentation and a configuration constant, not LW's all-opus mandate
**Why not full import**: LW uses claude-opus for all rf-* agent operations regardless of task complexity; this is explicitly rejected in D-0022 Principle 4. IC's PM Agent documentation should explicitly formalize the opposite policy: Haiku for routine self-checks, Sonnet for structural validation, Opus reserved for critical cross-session reflexion.

**File paths and change description**:
- `src/superclaude/pm_agent/__init__.py` — Add module-level docstring documenting the model tier policy: "ConfidenceChecker and SelfCheckProtocol run at Haiku tier for routine pre/post checks. ReflexionPattern runs at Sonnet tier for pattern matching. PM Agent's monthly maintenance mode runs at Sonnet tier. Critical cross-session learning (ReflexionPattern + SelfCorrectionEngine) may escalate to Opus tier when confidence score drops below 0.70."
- `.claude/agents/pm-agent.md` — Add a "Model Tier Policy" section to the agent definition specifying the above tiers explicitly. This is a behavioral NFR for the agent.

**Rationale**: D-0022 Principle 4 (Bounded Complexity), direction 1: "IC's tiered model selection should be formalized into an explicit model-selection policy."

**Dependencies**: None
**Acceptance criteria**: `pm_agent/__init__.py` contains a docstring with the tier policy; `pm-agent.md` has a "Model Tier Policy" section; tier rules are named explicitly (Haiku for routine, Sonnet for structural, Opus for critical).
**Risk**: Low. Documentation only; no behavioral change.
