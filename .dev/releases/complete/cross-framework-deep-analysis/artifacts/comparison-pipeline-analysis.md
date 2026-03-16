---
comparison_pair: 7
ic_component: Pipeline Analysis Subsystem
lw_component: Failure Debugging System + Critical Flaw Analysis
ic_source: src/superclaude/cli/pipeline/__init__.py, src/superclaude/cli/pipeline/gates.py, src/superclaude/cli/pipeline/fmea_classifier.py, src/superclaude/cli/pipeline/diagnostic_chain.py
lw_source: .dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md, .dev/taskplanning/backlog/FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md
mapping_type: partial
verdict_class: IC stronger
confidence: 0.77
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Pipeline Analysis Subsystem (IC) vs Failure Debugging System (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude pipeline analysis subsystem provides **programmatic, pre-execution analysis** of pipeline specifications: FMEA dual-signal failure mode classification, invariant registry, guard analysis, and dataflow tracing. These analytical passes detect implicit contracts between deliverables before they become runtime failures — operating on specifications, not post-failure artifacts. The 4-stage diagnostic chain (`run_diagnostic_chain()`) provides post-failure analysis with graceful per-stage degradation. Critically, both the analytical passes and the diagnostic chain are **pure Python** — deterministic, testable, and independent of LLM non-determinism.

**Key strengths** (`src/superclaude/cli/pipeline/fmea_classifier.py:129`, `src/superclaude/cli/pipeline/executor.py:46`):
- FMEA dual-signal detection: Signal 1 (invariant cross-ref) + Signal 2 (no-error-path for EMPTY/NULL/ZERO inputs)
- Signal 2 operates independently — detects silent corruption even without registered invariants
- `gate_passed()` is pure Python: no subprocess, no LLM — deterministic for given inputs
- DFS cycle detection on dataflow graph: prevents infinite loops
- NFR-007: no reverse imports (pipeline → sprint/roadmap forbidden) — genuine library isolation
- `cancel_check` injectable for graceful cancellation by external signals
- 42-symbol public API explicit in `__init__.py`

### LW Advocate Position
The llm-workflows failure debugging system provides **triggered, evidence-packaged root cause analysis** with automatic activation after N failures. The 4-category pattern scoring (`execution_score`, `template_score`, `evidence_score`, `workflow_score`) transforms ad-hoc debugging into a structured, reproducible process. The pre-packaged artifact collection (QA report + worker handoff + batch state JSON + conversation log) ensures all evidence is assembled before analysis begins — preventing the common debugging failure mode of starting analysis with incomplete context.

**Key strengths** (`05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:163-167`, `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:784-840`):
- Automatic trigger: activates on 3rd QA FAIL, max retry exceeded, critical violation, or manual
- 4-category pattern scoring with explicit confidence levels (High/Medium/Low)
- Three ranked solutions: surgical/systemic/hybrid — not a single recommendation
- Framework-vs-project diagnostic distinction prevents misdiagnosing framework issues as user errors
- Pre-packaged artifact collection assembles evidence before analysis begins

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/cli/pipeline/fmea_classifier.py` | 129 | Dual-signal FMEA: Signal 1 (invariant violations) + Signal 2 (no-error-path) |
| `src/superclaude/cli/pipeline/fmea_classifier.py` | 7 | Signal 2 operates independently without registered invariants |
| `src/superclaude/cli/pipeline/gates.py` | 20 | `gate_passed()` pure Python, no subprocess, deterministic |
| `src/superclaude/cli/pipeline/invariant_pass.py` | 39 | `InvariantEntry` with constrained predicates |
| `src/superclaude/cli/pipeline/executor.py` | 88 | `cancel_check: Callable[[], bool]` polled before each step |
| `src/superclaude/cli/pipeline/diagnostic_chain.py` | — | 4-stage diagnostic: troubleshoot → adversarial × 2 → summary |
| `src/superclaude/cli/pipeline/__init__.py` | 3 | 42-symbol public API; NFR-007 enforces no reverse imports |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 163-167 | Auto-trigger: 3rd QA FAIL, max retry, critical violation, or manual |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 784-840 | 4-category scoring: execution, template, evidence, workflow |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 333-335 | Confidence levels: High (≥5 pts), Medium (3-4), Low (≤2) |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 564-566 | Three ranked solutions: surgical/systemic/hybrid |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 395 | Framework-vs-project diagnostic distinction |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 243-248 | Pre-packaged artifact collection |
| `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | 796-840 | Grep-based pattern matching in bash (fragile) |

## 3. Adversarial Debate

**IC attacks LW**: LW's failure debugging system is **reactive** — it activates after 3 QA failures. By that point, 3 Worker sessions + 3 QA sessions + 3 correction sessions have been consumed. IC's FMEA and invariant analysis are **proactive**: they run on pipeline specifications before execution, identifying failure modes that would cause runtime failures. IC's Signal 2 (no-error-path detection for degenerate inputs) specifically targets the class of bugs that would only manifest at runtime — and catches them at specification time. LW's system reduces debugging cost; IC's system eliminates some failures entirely.

**LW attacks IC**: IC's FMEA operates on **deliverable descriptions** (text), not actual code. If a deliverable description omits a state variable or error condition, the FMEA analysis has a blind spot — it cannot detect what is not described. LW's failure debugging operates on **actual execution artifacts** (QA reports, worker handoffs, conversation logs) — evidence of what actually happened, not what was described. Real failure classification is more reliable than pre-execution speculation.

**IC counter**: IC's analytical passes operate on text, but the alternative (analyzing actual LLM output at runtime) is post-hoc by definition. The FMEA's text-based analysis has blind spots, but it catches a meaningful class of specification errors (missing error paths, guard ambiguities, cross-deliverable state conflicts) that would otherwise only appear after execution. The guard annotation mechanism (`@no-ambiguity-check`) provides manual correction for false positives.

**LW counter**: LW's grep-based pattern matching in `analyze_failure_pattern()` is fragile — QA report wording changes can break detection. IC's pure-Python FMEA analysis is more robust to this fragility. However, LW's 4-category classification with confidence levels provides a richer debugging result than IC's diagnostic chain output.

**Convergence**: IC is stronger on pre-execution analysis and programmatic quality of implementation. LW is stronger on post-failure structured debugging with explicit classification and ranked solutions. Both address pipeline quality but at different temporal positions in the execution lifecycle.

## 4. Verdict

**Verdict class: IC STRONGER**

**Rationale**: IC's pre-execution analysis capability (FMEA dual-signal, invariant registry, guard analysis, dataflow tracing) is genuinely novel — LW has no equivalent proactive analysis mechanism. The pure-Python gate validation (deterministic, testable, no LLM) is a design advantage with no LW parallel. LW's failure debugging is valuable but reactive; IC's analysis is proactive.

**Conditions where LW patterns should be adopted into IC**:
- Automatic trigger-after-N-failures (IC's diagnostic chain should auto-trigger without explicit invocation)
- 4-category failure classification taxonomy (execution/template/evidence/workflow) for sprint failures
- Confidence scoring on failure classification (IC's diagnostic chain produces free-text analysis, not scored categories)
- Pre-packaged artifact collection before analysis (IC should bundle evidence before running diagnostic chain)
- Framework-vs-project diagnostic distinction (sprint CLI failure vs. task specification failure)

**Confidence: 0.77**

**Adopt patterns, not mass**: From LW: the auto-trigger pattern (N failures → auto-invoke diagnostic), the 4-category scoring taxonomy for failure classification, confidence-scored classification (High/Medium/Low based on evidence weight), pre-packaged artifact bundle before analysis begins, and the framework-vs-project distinction in diagnostic output. From IC: FMEA dual-signal detection (proactive, pre-execution), pure-Python gate validation (deterministic, testable), invariant registry for cross-deliverable state tracking, and DFS cycle detection for dependency graph termination. Do NOT adopt: LW's grep-based pattern matching in bash, the 3-solution mandate when a single fix is obvious, or the reactive-only triggering without proactive analysis.
