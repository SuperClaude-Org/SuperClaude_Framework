---
deliverable: D-0022
task: T06.01
title: Merged Architectural Strategy — IronClaude Cross-Framework Synthesis
status: complete
comparison_pairs_covered: 8
comparison_pairs:
  - comparison-roadmap-pipeline.md
  - comparison-sprint-executor.md
  - comparison-pm-agent.md
  - comparison-adversarial-pipeline.md
  - comparison-task-unified-tier.md
  - comparison-quality-agents.md
  - comparison-pipeline-analysis.md
  - comparison-cleanup-audit.md
generated: 2026-03-15
---

# D-0022: Merged Architectural Strategy

## Executive Summary

All 8 adversarial comparison pairs have been synthesized into five architectural principles that govern IronClaude's Phase 7 improvement planning. The synthesis reveals a consistent pattern: IC's programmatic, Python-native, deterministic foundation is architecturally sound and should not be replaced. LW contributes adoptable patterns in four specific areas — epistemic stance, restartability semantics, quality vocabulary, and agent coordination formalism — that can be integrated into IC's existing architecture without wholesale adoption of LW components.

Verdict distribution: 5 IC-stronger, 3 split-by-context, 0 LW-stronger, 0 no-clear-winner, 0 discard-both. The absence of LW-stronger or discard-both verdicts confirms IC's structural advantage, while the three split verdicts identify where IC can absorb LW's complementary strengths for specific execution contexts.

**Adopt patterns, not mass.** This principle governs all seven adoptable LW contributions identified below. No LW component is adopted wholesale; each adoption is scoped to a specific pattern with explicit reject conditions.

---

## Principle 1: Evidence Integrity

**Governing IC components**: PM Agent (pair 3), Adversarial Pipeline (pair 4), Cleanup-Audit CLI (pair 8), Quality Agents (pair 6)

### Current State

IC's evidence mechanisms are strong for programmatic verification (ConfidenceChecker 5-check pre-execution scoring; SelfCheckProtocol 7 red-flag detection; 3-tier confidence-graded dependency graph) but weak on epistemic stance. The default assumption is that an agent's output is correct until a specific red flag is triggered. IC's self-check detects hallucination signals reactively; it does not invert the default epistemic stance proactively.

### Strategic Direction

Adopt LW's **Presumption of Falsehood** as the default epistemic stance for IC's verification agents. This means:

1. **For PM Agent (pair 3)**: `SelfCheckProtocol.validate()` should treat all self-reported completions as "unverified" by default, requiring affirmative evidence before accepting a claim as "verified." The current 7 red-flag approach catches specific hallucination patterns but does not systematically require proof. Add a `filesystem_verified` flag analogous to LW's claim/proof distinction (`worker_handoff` vs. `programmatic_handoff`): the SelfCheckProtocol should distinguish between a self-reported claim and a filesystem-verifiable artifact.

2. **For Cleanup-Audit CLI (pair 8)**: Audit agents (Haiku scanner in G-001, Sonnet in G-002) should default classification status to "unverified" until evidence is gathered, not "classified" pending flagging. The `classify_finding()` function is deterministic and correct; the behavioral instructions to agents should reinforce that classification starts from zero, not from a positive assumption.

3. **For all IC evidence-gathering agents (pairs 3, 6, 8)**: Adopt LW's **mandatory negative evidence documentation** requirement. When an agent finds no importers, no errors, or no supporting evidence for a claim, "not found" must be explicitly documented as a result. Silent omission is not acceptable. This closes a gap in IC's audit and PM agent workflows where absence of evidence is not distinguished from evidence of absence.

4. **For Adversarial Pipeline (pair 4)**: The CEV (Claim-Evidence-Verdict) protocol already implements a form of evidence integrity at the comparison level. Extend this vocabulary to the IC framework as a whole: all qualitative claims in verification outputs should cite specific evidence (file:line or artifact reference).

### Cross-Component Consistency

The evidence integrity principle binds pairs 3, 4, 6, and 8 to a consistent epistemic standard: **no claim is accepted without evidence; absence of evidence must be documented; every verification output distinguishes between claimed and proven.** This does not require LW's full PABLOV artifact chain — the pattern is the epistemic stance, not the five-artifact implementation.

**Do not adopt**: LW's mandatory per-claim structured evidence tables for all output types at all tiers (pair 5 reject), the full five-artifact PABLOV chain for lightweight single-session tasks (pair 3 reject), or the FAS -100 penalty scoring system (specific to LW's batch execution model, not applicable to IC's session-level patterns).

---

## Principle 2: Deterministic Gates

**Governing IC components**: Pipeline Analysis Subsystem (pair 7), Task-Unified Tier System (pair 5), Sprint Executor (pair 2), Cleanup-Audit CLI (pair 8)

### Current State

IC's gate system is already strong: `gate_passed()` is pure Python (no subprocess, no LLM — deterministic for given inputs); the STRICT > EXEMPT > LIGHT > STANDARD tier conflict resolution is deterministic; NFR-007 enforces no reverse imports from pipeline to sprint/roadmap consumers. The tier system's compound phrase overrides and critical path filesystem override provide semantic safety beyond keyword matching.

### Strategic Direction

The deterministic gate principle has two improvement areas identified by the adversarial comparisons:

1. **Fail-closed semantics must be explicit and universal (pairs 2, 3, 5)**: LW's fail-closed verdict logic (mismatch between claimed completion and programmatic handoff = FAIL, not best-effort PASS) is a stronger stance than IC's current gate tier system allows for partial completions. IC should adopt the fail-closed principle at the gate level: when a gate evaluation cannot definitively confirm PASS, the result is FAIL — not PASS with caveats. The `gate_passed()` function's boolean return already supports this; the pattern should be enforced in task completion logic for the Sprint Executor as well. A phase gate that is inconclusive is a FAIL.

2. **CRITICAL FAIL conditions for unconditional gate failure (pairs 6, 8)**: The `audit-validator`'s CRITICAL FAIL on false-negative DELETE is the right model. Extend this to the Sprint Executor and Task-Unified Tier System: define specific failure types that force unconditional gate failure regardless of overall metrics. For example: a STRICT-tier task that cannot reach its Sequential + Serena MCP requirements should fail (not degrade) — this already exists but should be explicit in the gate model as a CRITICAL condition class.

3. **Automatic tier classification with confidence scoring must extend to output type (pair 5)**: IC's tier system correctly classifies tasks but applies uniform verification overhead across all output types. LW's output-type-specific gate tables (different verification for code outputs vs. analysis outputs vs. opinion outputs) prevent both over-checking and under-checking. Phase 7 should integrate output-type discrimination into the STRICT/STANDARD/LIGHT/EXEMPT routing so that documentation tasks are not subjected to code-verification overhead, and analysis tasks are not subjected to structural-linting gates that do not apply.

4. **Pre-execution specification analysis gates (pair 7)**: IC's FMEA dual-signal detection and invariant registry are the strongest pre-execution gate mechanisms in this comparison — LW has nothing equivalent. This advantage should be preserved. The FMEA Signal 2 (no-error-path detection for degenerate inputs) specifically catches a class of specification errors that only manifest at runtime; this proactive gating is architecturally superior to reactive failure analysis.

### Cross-Component Consistency

Deterministic gates apply uniformly: same input → same gate result. No gate may produce a "PASS with conditions" that could be interpreted as PASS for some consumers and FAIL for others. The gate system is the source of truth for pipeline correctness; its determinism is non-negotiable.

**Do not adopt**: LW's behavioral-only quality gate application without programmatic automation (pair 5 reject), LW's grep-based bash pattern matching for failure classification (pair 7 reject), or any gate mechanism that requires LLM evaluation for its pass/fail determination.

---

## Principle 3: Restartability

**Governing IC components**: Sprint Executor (pair 2), Roadmap Pipeline (pair 1), Pipeline Analysis Subsystem (pair 7)

### Current State

IC's restartability is phase-level for the Sprint Executor and step-level for the Roadmap Pipeline. The Roadmap Pipeline's `_apply_resume()` with stale-spec sha256 detection is a strong restartability mechanism at the step level. Sprint Executor's `--start N` flag allows phase-level re-entry. However, within a phase, IC has no sub-phase restartability: if Phase 3 fails on task 14 of 15, all 15 tasks re-run on restart.

### Strategic Direction

1. **Batch immutability and per-item UID tracking (pair 2)**: Adopt LW's batch immutability principle — once a sprint phase begins, task identifiers are frozen. No task renaming or reordering mid-run. Additionally, adopt per-item UID tracking within a phase: each task should receive a stable identifier that persists across session resets, enabling sub-phase restartability (re-enter at the first failed task, not at the first task in the phase). This closes IC's restartability gap without requiring LW's 6000-line bash implementation.

2. **Three-mode execution (pair 2)**: LW's three-mode prompt selection (normal / incomplete / correction) handles the three most common mid-phase interruption scenarios deterministically. IC's Sprint Executor should adopt this pattern: when resuming a phase, the execution mode (fresh / incomplete-resume / correction) should be explicitly declared in the TurnLedger and reflected in the prompt construction. This eliminates the current ambiguity where a resumed phase cannot distinguish between "task never started" and "task started but not completed."

3. **Per-track state machine pattern (pair 1)**: For future multi-track execution scenarios, LW's per-track state machine (explicit states: pending → in_progress → done → failed, maintained by orchestrator) is superior to IC's phase-level pass/fail. IC's current single-track model does not need this immediately, but the step-level states in `StepResult` should be extended to match this formalism for forward compatibility.

4. **Pre-packaged artifact collection before diagnostic runs (pair 7)**: IC's diagnostic chain (`run_diagnostic_chain()`) should adopt LW's pattern of assembling all relevant artifacts before analysis begins. Currently, IC's diagnostic chain reads artifacts during analysis; pre-packaging ensures the diagnostic has a complete, consistent evidence snapshot even if the pipeline continues running. This prevents a class of partial-evidence diagnostics.

5. **Documented fallback degradation path (pair 1)**: LW's Roadmap fallback (event-driven → phased-parallel with documented trigger conditions) should be adopted as a pattern for any IC component with a primary and secondary execution mode. The fallback path and its trigger conditions should be explicitly documented in the component specification, not inferred. For the Sprint Executor, this means explicitly documenting what happens when tmux is unavailable, when `_subprocess_factory` raises, or when TurnLedger exhausts budget.

### Cross-Component Consistency

Restartability is a first-class quality requirement. Every pipeline component must have: (a) explicit restart semantics defined, (b) stable identifiers for resumption points, and (c) documented fallback behavior when the primary execution mode is unavailable. IC's current checkpoint reliability is good at the phase level; these improvements extend it to the task level.

**Do not adopt**: LW's experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` infrastructure for multi-track execution (pair 1 reject), or the specific 6000-line bash batch state machine (pair 2 reject).

---

## Principle 4: Bounded Complexity

**Governing IC components**: All 8 component groups

### Current State

IC consistently rejects LW's complexity drivers: bash orchestration (pairs 2, 8), all-opus model selection regardless of task complexity (pairs 1, 6), experimental infrastructure dependencies (pair 1), full PABLOV artifact chain for lightweight tasks (pair 3), and per-claim evidence tables for all output types at all tiers (pair 5). These rejections reflect a coherent architectural decision: IC's complexity is bounded by the Python-native, tier-proportional, standard-infrastructure design.

### Strategic Direction

The bounded complexity principle is largely a **defensive principle** — it defines what IC must not adopt. But it also has two positive prescriptions:

1. **Model tier proportionality (pairs 1, 6)**: IC's architecture should explicitly specify model tier proportional to task complexity for all agent invocations. The audit-validator (10% spot-check) should not use the same model as quality-engineer (STRICT-tier deep verification). LW's all-opus mandate for all rf-* agents is the anti-pattern: it treats every agent operation as requiring maximum capability, ignoring that most agent operations are routine. IC's tiered model selection (Haiku for surface scanning, Sonnet for structural, implied by cleanup-audit pass structure) should be formalized into an explicit model-selection policy.

2. **Hard caps on resource usage (pair 1)**: The track cap (5 tracks / 15 agents) in LW's Rigorflow is the right principle even if LW's implementation is too complex. IC should formalize resource caps: maximum concurrent phases in sprint execution, maximum parallel steps in roadmap generation, maximum depth for recursive pipeline analysis. These caps prevent runaway resource usage without requiring explicit monitoring logic.

3. **Three-tier severity for gate failures (pair 5)**: LW's Sev 1 (block immediately) / Sev 2 (fix in cycle) / Sev 3 (when able) severity taxonomy should be adopted as IC's standard for gate failure reporting. Currently, IC's gate failures are binary (PASS/FAIL). Introducing severity allows STANDARD-tier issues to cycle rather than block, while ensuring Sev 1 issues remain unconditional blockers. This reduces unnecessary pipeline halts for non-critical issues while maintaining strong safety for critical ones.

### Cross-Component Consistency

The bounded complexity principle applies to all eight IC component groups. Before Phase 7 improvements are planned, each proposed change should be evaluated against: does this addition introduce LW-type complexity (bash, all-model, experimental API, per-claim overhead)? If yes, find the pattern and discard the mass. The "adopt patterns, not mass" invariant is the operational expression of this principle.

**Reject inventory** (all LW patterns explicitly discarded across 8 comparisons):
- LW's bash implementation for sprint orchestration and audit logic (pairs 2, 8)
- LW's experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` dependency (pair 1)
- LW's all-opus model selection for all agent roles (pairs 1, 6)
- LW's `permissionMode: bypassPermissions` for all agents (pair 6)
- LW's mandatory sequential PABLOV execution prohibiting parallelism (pair 3)
- LW's full five-artifact chain for lightweight single-session tasks (pair 3)
- LW's per-claim structured evidence tables for all output types at all tiers (pair 5)
- LW's manual quality gate application without programmatic automation (pair 5)
- LW's grep-based bash pattern matching for failure classification (pair 7)
- LW's three-solution mandate when a single fix is obvious (pair 7)
- LW's static sycophancy pattern weights without adaptive learning (pair 4)
- LW's multiple-backup-file versioning strategy (pair 2)
- LW's Python subprocess call from bash as workaround for bash limitations (pair 2)

**Note**: Zero "discard both" verdicts (D-0020). All rejects above are LW-specific pattern discards; IC's corresponding patterns are retained or improved.

---

## Principle 5: Scalable Quality Enforcement

**Governing IC components**: Task-Unified Tier System (pair 5), Quality Agents (pair 6), Adversarial Pipeline (pair 4), Pipeline Analysis Subsystem (pair 7)

### Current State

IC's quality enforcement is strong in the programmatic layer (automatic tier classification, STRICT MCP blocking, quality-engineer agent, FMEA pre-execution analysis) but has gaps in the ambient layer: quality enforcement for routine interactions, the vocabulary used by verification agents, and the taxonomy for classifying failures. The adversarial pipeline provides deep quality for explicit comparison tasks but does not address ambient quality in everyday pipeline interactions.

### Strategic Direction

1. **Six universal quality principles as verification agent vocabulary (pair 5)**: LW's six quality principles — Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy — should become IC's standard vocabulary for what quality-engineer and self-review agents verify. Currently, IC's verification agents have general instructions ("think beyond the happy path") without a structured principle set. These six principles provide a named, reproducible check framework that any verification agent can apply regardless of the specific task domain. They are adoptable as IC's NFR baseline for all STRICT-tier verification.

2. **Ambient sycophancy detection (pair 4)**: LW's 12-category sycophancy risk taxonomy with non-linear multipliers (1.3× for 2+ patterns, 1.5× for 3+ patterns) addresses a quality dimension IC does not currently enforce: sycophancy risk in everyday agent interactions, not just in explicit adversarial comparisons. IC should adopt this taxonomy as a lightweight Tier 1 check embedded in agent definitions (not requiring explicit invocation), with the four-tier response routing (standard → trade-offs → escalate → challenge premise) applied proportionally to the risk score. This extends quality enforcement to ambient interactions without adding invocation overhead.

3. **Automatic diagnostic triggering (pair 7)**: IC's diagnostic chain (`run_diagnostic_chain()`) currently requires explicit invocation. LW's auto-trigger pattern (activate on 3rd QA FAIL, max retry exceeded, critical violation, or manual invocation) should be adopted: the Sprint Executor should automatically invoke diagnostic analysis when a phase fails N consecutive times, without requiring operator intervention. The threshold and trigger conditions should be configurable, but the auto-trigger capability should be the default behavior.

4. **4-category failure classification taxonomy (pair 7)**: LW's failure classification taxonomy — execution failures, template failures, evidence failures, workflow failures — provides a structured vocabulary for diagnosing sprint execution failures. IC's current diagnostic chain produces free-text analysis without a structured classification. Adopting this taxonomy allows IC to produce scored, categorized failure reports (with confidence levels: High ≥5 pts, Medium 3-4, Low ≤2) that are actionable and comparable across runs.

5. **Typed inter-agent communication for coordination (pair 6)**: LW's typed message protocol (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE, BLOCKED) provides reliable coordination semantics for multi-agent pipelines. IC's quality agents currently produce reports and return results without formal handoff protocols. For IC components that involve sequential agent invocation (cleanup-audit's G-001 → G-002 → G-003 progression; sprint executor's phase-to-phase handoff), adopt explicit typed state transitions. BLOCKED as a first-class message type prevents silent failures in agent coordination.

6. **Executor validation gate pattern (pair 6)**: Before any agent begins execution, it should validate its input file/specification and emit BLOCKED if the structure is invalid. This pattern from LW's rf-task-executor is directly adoptable into IC's sprint and roadmap pipeline agents: an agent that starts executing on a malformed task specification will fail unpredictably; an agent that validates first and blocks on invalid input fails predictably and early.

7. **Framework-vs-project diagnostic distinction (pair 7)**: IC's diagnostic output should distinguish between sprint CLI failures (framework issues) and task specification failures (project issues). This prevents operators from attempting to fix task specifications when the root cause is in the IC framework itself, and vice versa.

### Cross-Component Consistency

Scalable quality enforcement means quality gates do not require expert manual selection — they activate automatically at the appropriate level based on task classification (tier), output type, and failure pattern. The combination of (a) automatic tier routing, (b) six universal principles as verification vocabulary, (c) ambient sycophancy detection, (d) auto-triggered diagnostics with 4-category classification, and (e) typed agent communication creates a quality enforcement system that scales from single-session tasks to multi-phase sprints without proportional operator overhead.

---

## Rigor Without Bloat

The synthesis across all 8 comparisons reveals a specific structural risk: adding LW patterns without the corresponding "adopt patterns, not mass" discipline. This section states the principle explicitly.

**Every LW pattern adoption must pass this test**:
1. Can the pattern be expressed as a modification to an existing IC component, without creating new files/classes/dependencies?
2. Does the pattern add a capability that IC currently lacks (not a re-implementation of something IC already has)?
3. Is the pattern extractable from LW's implementation vehicle (bash, experimental API, all-opus) and implementable in IC's implementation vehicle (Python, standard infrastructure, tier-proportional)?

Patterns that fail test (1) require justification. Patterns that fail test (2) are redundant. Patterns that fail test (3) require translation, not adoption.

**Patterns verified as adoptable** (pass all three tests):
- Presumption of Falsehood as epistemic stance (PM Agent, Cleanup-Audit agents)
- Mandatory negative evidence documentation (PM Agent SelfCheckProtocol, audit agents)
- Batch immutability and per-item UID tracking (Sprint Executor)
- Three-mode execution for mid-phase resume (Sprint Executor)
- Fail-closed verdict logic (Sprint Executor gate completion)
- Six universal quality principles as verification vocabulary (quality-engineer agent)
- 12-category sycophancy risk taxonomy with non-linear multipliers (ambient agent instructions)
- Four-tier sycophancy response routing (ambient agent instructions)
- Auto-trigger diagnostic on N failures (Sprint Executor)
- 4-category failure classification taxonomy with confidence scoring (diagnostic chain output)
- Typed inter-agent communication state transitions (cleanup-audit, sprint phase handoffs)
- Executor validation gate pattern (sprint and roadmap pipeline agents)
- Pre-packaged artifact collection before diagnostic analysis (diagnostic chain)
- Framework-vs-project diagnostic distinction (diagnostic output format)
- Three-tier severity for gate failure reporting (gate output format)
- Output-type-specific gate application (task-unified tier routing)
- Model tier proportionality policy (all agent invocations)
- Hard resource caps formalization (sprint, roadmap, pipeline)
- Documented fallback degradation path (all pipeline components)

**"Adopt patterns not mass" verification**: Each item above is a behavioral pattern or data structure extension, not a wholesale component adoption. The largest proposed change (UID tracking per task in Sprint Executor) adds a stable identifier field to existing task models — it does not require rewriting the executor. No LW component is imported into IronClaude.

---

## Cross-Component Traceability

| Comparison Pair | Verdict | Primary Principle | Secondary Principle |
|---|---|---|---|
| comparison-roadmap-pipeline.md | split by context | Restartability | Bounded Complexity |
| comparison-sprint-executor.md | IC stronger | Restartability | Deterministic Gates |
| comparison-pm-agent.md | split by context | Evidence Integrity | Bounded Complexity |
| comparison-adversarial-pipeline.md | IC stronger | Scalable Quality Enforcement | Evidence Integrity |
| comparison-task-unified-tier.md | IC stronger | Deterministic Gates | Scalable Quality Enforcement |
| comparison-quality-agents.md | split by context | Scalable Quality Enforcement | Evidence Integrity |
| comparison-pipeline-analysis.md | IC stronger | Deterministic Gates | Restartability |
| comparison-cleanup-audit.md | IC stronger | Evidence Integrity | Deterministic Gates |

All 8 comparison pairs are covered. No orphaned comparisons.

---

## Phase 7 Planning Directives

Phase 7 improvement plans must trace each proposed improvement to one or more of the five principles above. A Phase 7 improvement item that cannot be traced to a principle is out of scope for this sprint.

Priority ordering for Phase 7:
1. **Evidence Integrity** improvements (PM Agent, Cleanup-Audit CLI): High impact, directly addressable via behavioral NFR additions to existing agents
2. **Restartability** improvements (Sprint Executor): High operational value, directly addressable via task model extension
3. **Scalable Quality Enforcement** improvements (Task-Unified Tier, Quality Agents): Medium-high impact, requires coordination across tier routing and agent definitions
4. **Deterministic Gates** improvements: Existing gates are strong; improvements are refinements (output-type gates, fail-closed universalization)
5. **Bounded Complexity** improvements: Primarily enforcement and documentation of existing policy; model tier proportionality and hard caps are the new additions

T07.04 (OQ-004): Zero "discard both" verdicts — no IC-native improvement items required for OQ-004. This is explicitly confirmed by D-0020.
