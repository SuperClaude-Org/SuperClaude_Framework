# Strategy: LW Component — Failure Debugging System

**Component**: Failure Debugging System
**Source**: `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The failure debugging system is an automated diagnostic report generator triggered by repeated QA failures. It produces a pre-packaged failure context bundle that enables systematic root cause analysis.

**Core rigor mechanisms:**

- **Automatic trigger points**: System auto-activates on QA FAIL after 3rd retry, batch retry limit exceeded (3 attempts), critical violation in QA report, or manual invocation. No human must remember to investigate — the system initiates investigation automatically. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:163-167`
- **4-category pattern scoring** (`analyze_failure_pattern()`): Separate scoring for execution patterns (`execution_score`), template violations (`template_score`), evidence issues (`evidence_score`), and workflow problems (`workflow_score`). The highest-scoring category determines the primary failure classification. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:784-840`
- **Confidence scoring**: "High (≥5 points)", "Medium (3-4 points)", "Low (≤2 points)". Classification confidence is explicit, not assumed. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:333-335`
- **Pre-packaged artifact collection**: Report includes QA report, worker handoff, batch state JSON, conversation log excerpt, task progress log — all evidence bundled before analysis begins. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:243-248`
- **Three ranked solutions**: Debugging agent proposes 3 solutions (surgical/systemic/hybrid) with prioritization. Not a single recommendation — explicitly considers different solution scopes. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:564-566`
- **Framework-level vs. project-level distinction**: The debugger explicitly analyzes "a QA failure in the .gfdoc framework itself, not a user project." This scoping prevents false positives where framework issues are misdiagnosed as user errors. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:395`

**Rigor verdict**: The 4-category scoring with explicit confidence levels transforms debugging from an ad-hoc process into a structured, reproducible one. The "50% debugging time reduction" and "90%+ success rate" claims are aspirational metrics from the spec, but the underlying design (pre-packaged context → classified failure → ranked solutions) is sound.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The v2 scoring system (4 separate scores with grep pattern matching) versus the v1 simple if/elif chain introduces more complexity but similar practical classification power for the small number of known failure categories.
- The diagnostic report format is highly detailed (~350 lines per report). For a simple execution pattern violation, most fields are not relevant.
- The 3-solution requirement (surgical/systemic/hybrid) forces a solution framework even when one solution is clearly correct.

**Operational drag:**
- The debugging system is reactive — it only activates after 3 QA failures. By that point, the batch has failed 3 times, each failure consuming a Worker session + QA session + correction session. The system helps after significant waste has already occurred.
- The manual invocation path (`troubleshoot.sh --qa-failure`) requires user awareness of the system's existence and correct usage.

**Token/runtime expense:**
- The diagnostic report itself (if comprehensive) is a large document that must be loaded into the debugging agent's context. Complex failures may produce reports exceeding 1000 lines.
- The debugging agent reads `FRAMEWORK_DEBUGGING_GUIDE.md` + the diagnostic report + all referenced artifacts. Context load is substantial.

**Maintenance burden:**
- The grep-based pattern matching in `analyze_failure_pattern()` is fragile — QA report wording changes can break pattern detection. `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:796-840`
- Two versions exist (v1 and v2) in the backlog, with a separate reflection document. The production version is not clearly identified from file names alone.
- The "50% debugging time reduction" and "90%+ success rate" metrics in the spec have no validation data cited in the document. These are targets, not measurements.

---

## 3. Execution Model

The failure debugging system operates as a **triggered diagnostic workflow**:

1. `automated_qa_workflow.sh` detects max retry exceeded → calls `generate_diagnostic_report()`
2. Report generator: collects failure evidence (QA report + handoffs + state + logs)
3. Calls `analyze_failure_pattern()`: runs 4-category scoring → classifies failure with confidence
4. Generates structured diagnostic report with failure summary, evidence, analysis, debugging prompt
5. Reports output path + suggests: `cat report.md` OR invoke `/rf:framework-debug @report.md`
6. Debugging agent (if invoked): reads report + FRAMEWORK_DEBUGGING_GUIDE.md → root cause analysis → 3 ranked solutions → test cases → documentation update recommendations

**Quality enforcement**: The debugging system is a meta-quality mechanism — it enforces quality by detecting and classifying quality failures in the main workflow.

**Extension points**:
- Additional pattern categories can be added to `analyze_failure_pattern()`
- Confidence thresholds are adjustable
- Solution ranking criteria can be customized
- Diagnostic report format can be extended with project-specific fields

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The automatic trigger-after-N-failures pattern is directly adoptable for SuperClaude's sprint CLI: if a task fails N times, auto-generate a diagnostic context bundle.
- The 4-category failure classification (execution, template, evidence, workflow) is directly adoptable as SuperClaude's sprint failure taxonomy.
- Confidence scoring on failure classification (High/Medium/Low based on evidence weight) is directly adoptable.

**Conditionally Adoptable:**
- The pre-packaged artifact collection (gather all relevant evidence before analysis) is conditionally adoptable. In SuperClaude's context, this maps to: on task failure, collect (task file + prior outputs + error logs + execution state) into a diagnostic bundle.
- The framework-vs-project diagnostic distinction is conditionally adoptable for sprint CLI: distinguish between "the sprint runner failed" (framework issue) vs. "the task was poorly specified" (user/spec issue).

**Reject:**
- The grep-based pattern matching in bash. In a Python sprint runner, regex matching on structured failure data is more reliable.
- The 3-solution requirement as mandatory structure when a single fix is obvious.
- Reactive-only triggering (after 3 failures). Proactive failure prevention (pre-execution confidence check) is more efficient — the confidence-check skill already implements this for SuperClaude.
