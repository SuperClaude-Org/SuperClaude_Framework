# Sprint CLI Specification Analysis — Diagnostic Report

**Spec Analyzed**: v2.05 Sprint CLI Specification (4 documents)
**Agent**: 3 (Specification Gap Analyst)
**Date**: 2026-03-08
**Scope**: Diagnostic only — no fixes proposed

---

## 1. Top 3 Theories for Why Bugs Survive the Workflow Despite Planning Rigor

### Theory 1: The Spec Is a Blueprint for a Static System, but the Agent Produces a Living System That Outgrows It

The specification describes a clean, bounded 2,160-line system across 11 files. The actual implementation is 3,844 lines across 14 files, with entirely new subsystems (pipeline inheritance layer, trailing gate policies, 4-layer subprocess isolation, KPI tracking, diagnostic collection, debug logging) that were never specified. The spec's roadmap (roadmap.md) places all validation at the end (M6, M7), after all feature milestones are complete. This means the architecture was locked before the agent discovered it needed features like `SprintGatePolicy`, `IsolationLayers`, `DiagnosticCollector`, `FailureClassifier`, `TurnLedger`, and inheritance from `superclaude.cli.pipeline.models`.

**The bug mechanism**: When the agent discovers mid-implementation that the spec's architecture doesn't cover a real need (e.g., trailing gates, context injection), it invents new abstractions on the fly without revising the spec or its test strategy. The test strategy (test-strategy.md) validates against the *original* requirements (FR-001 through FR-035), not the *emergent* architecture. New subsystems ship without acceptance criteria because they were never in the extraction.

**Evidence**:
- Spec Section 1 estimates `~2,160 lines estimated across 11 files` — actual is 3,844 across 14 files (78% growth)
- `executor.py` alone is 815 lines vs. spec's estimate of ~300 lines (172% over)
- `models.py` is 609 lines vs. spec's ~180 lines (238% over), containing `TaskEntry`, `TaskResult`, `TaskStatus`, `GateOutcome`, `GateDisplayState`, `TurnLedger` — none of which appear in the spec
- Extraction (extraction.md) lists exactly 38 requirements; no mechanism exists to add requirements discovered during implementation
- Roadmap (roadmap.md) D2.7 acceptance criteria: "Iterates active phases; launches subprocess per phase; polls until process exits" — actual executor has 4-layer isolation, budget guards, task-level execution, remediation steps, git diff context injection, and trailing gate integration

### Theory 2: The Spec Assumes the Agent's Output Is Deterministic, but LLM-Generated Code Has Semantic Drift

The specification provides exact code blocks as implementation targets (Section 2 data models, Section 5 tmux, Section 6 monitor, Section 7 process, Section 8 executor, Section 10 config). These are treated as blueprints the implementing agent should reproduce. But an LLM agent does not copy-paste from a spec — it regenerates from context, and each regeneration drifts from the reference.

**The bug mechanism**: The spec's code examples define contracts (e.g., `_determine_phase_status` with a 7-level priority chain). The agent implements something structurally similar but semantically different. The actual `_determine_phase_status` adds PARTIAL detection (`re.search(r"status:\s*PARTIAL\b", content, re.IGNORECASE)`) and `INCOMPLETE` status (`detect_error_max_turns`), neither of which is in the spec. The test strategy validates against the spec's 7 levels, not the implementation's 9 levels. Any test written against the spec passes, but the two extra code paths are untested.

**Evidence**:
- Spec Section 8, `_determine_phase_status`: 7-level priority (timeout → error → HALT → CONTINUE → PASS/FAIL → no report → error)
- Actual implementation adds level 5a (`status: PARTIAL` → HALT) and level 7a (`detect_error_max_turns` → INCOMPLETE)
- `PhaseStatus` enum in spec: 9 states. Actual enum adds `INCOMPLETE` state — not in extraction FR-009
- Spec `ClaudeProcess.build_prompt()` generates a `/sc:task-unified` prompt with specific format. Actual `process.py` inherits from `pipeline.process.ClaudeProcess` and uses factory closures for hooks — entirely different architecture
- Test strategy (test-strategy.md) Validation Coverage Matrix maps FR-030 to "Status determination: 7-level priority chain verified" — the implemented 9-level chain escapes validation

### Theory 3: The Validation Architecture Tests Structure, Not Behavior Under Real Conditions

The test strategy (test-strategy.md) is rigorous in coverage mapping — every FR maps to a validation milestone and a test method. But the tests are designed around mocked components: `Mock ClaudeProcess.start/wait`, `Mock subprocess.run`, `Console(file=StringIO)`. The spec explicitly states in Section 12.2: "executor.py: Integration — Mock ClaudeProcess.start/wait, mock monitor, verify flow."

**The bug mechanism**: The most failure-prone part of the system is the boundary between the sprint executor and the actual Claude CLI subprocess — the part where the agent's output is parsed for signals (`EXIT_RECOMMENDATION`, task IDs, status frontmatter). This boundary is never tested with real (or realistic) Claude output. The monitor regex patterns (`T\d{2}\.\d{2}` for task IDs, `\b(Read|Edit|...)\b` for tools) are validated against hand-crafted test strings, not against actual Claude output transcripts. When real Claude output doesn't match the expected format (missing `EXIT_RECOMMENDATION`, different task ID formatting, output truncation at token limits), the status determination falls through to `PASS_NO_SIGNAL` or `PASS_NO_REPORT` — false positives that let broken phases appear successful.

**Evidence**:
- Spec Section 12.2: Every component tested with mocks, zero integration tests with real subprocess output
- Spec Section 6, monitor regex: `TASK_ID_PATTERN = re.compile(r"T\d{2}\.\d{2}")` — matches only strict `T##.##` format
- Spec Section 8, `_determine_phase_status` fallthrough: missing result file + output exists → `PASS_NO_REPORT` — this is a **permissive default**, not a conservative one
- Spec Section 14, Open Question #2: "Should the monitor track token usage from claude output? Defer to v4.4" — the token-budget problem was recognized but deferred
- Test strategy D4.1 acceptance criteria: "Test renders TUI to StringIO; status transitions verified in output" — validates rendering, not correctness of status determination
- Risk register RISK-005: "Monitor regex patterns for task IDs and tools may miss new Claude output formats" — acknowledged as Medium probability but mitigation is only "integration tests with real output samples" — which are never actually specified as deliverables

---

## 2. Blind Spots Identified — What the Workflow Systematically Fails to Examine

### Blind Spot A: No Spec-to-Implementation Drift Detection

The workflow has Extraction → Roadmap → Test Strategy → Implementation, but no reverse loop. Once the agent begins implementation and discovers that the spec's architecture is insufficient (leading to the 78% codebase growth), there is no mechanism to:
1. Update the extraction with new requirements
2. Revise the roadmap with new milestones
3. Extend the test strategy to cover emergent code

The validation milestones (M4, M7) check against the *original* spec, creating a blind spot for all code that the agent invented beyond the spec.

**Spec evidence**: Extraction metadata states "Pass 1 (Source Coverage): 98%" — this is coverage of the *spec*, not coverage of what will actually be built. The 2% missed was "testing strategy patterns," but the real gap is the 78% growth that happens post-extraction.

### Blind Spot B: The Prompt-to-Output Contract Is Unspecified

The spec defines `ClaudeProcess.build_prompt()` (Section 7) with a specific prompt template including `EXIT_RECOMMENDATION: CONTINUE` and `EXIT_RECOMMENDATION: HALT` markers. But there is no contract for what Claude's output *actually looks like*. The spec assumes the Claude subprocess will:
- Write task IDs in `T##.##` format
- Use tool names like `Read`, `Edit`, `Bash`
- Write a result file with YAML frontmatter and `EXIT_RECOMMENDATION`
- Exit with code 0 on success and non-zero on failure

None of these assumptions are validated or documented as contracts. The specification treats the Claude subprocess as a black box with assumed behavior, then builds a parsing layer (monitor, status determination) that depends on that assumed behavior being correct.

**Spec evidence**: Section 7, `build_prompt()` says "Write a phase completion report to {result_file} containing: YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL)..." — but these are *instructions to the LLM*, not contracts. An LLM may not follow instructions precisely, especially under token pressure or after errors.

### Blind Spot C: Error Path Combinatorics Are Not Explored

The spec defines 9 PhaseStatus values and 4 SprintOutcome values, creating a state space. But the test strategy only validates 4 flows: PASS, HALT, TIMEOUT, INTERRUPTED (test-strategy.md D6.5). The actual implementation adds `INCOMPLETE`, `PASS_NO_SIGNAL`, `PASS_NO_REPORT`, and `SKIPPED` — each representing a distinct failure mode with different downstream behavior. The combinatorial space of "phase 1 PASS → phase 2 PASS_NO_SIGNAL → phase 3 HALT" is never tested.

**Spec evidence**: Test strategy D6.5: "Full integration test with mocked subprocess covering PASS, HALT, TIMEOUT, INTERRUPTED flows" — only 4 of 9+ possible status values are covered. The actual implementation's `INCOMPLETE` status (from `detect_error_max_turns`) has no test coverage in the test strategy at all.

### Blind Spot D: Resource and Timing Constraints Under Real Execution

The spec acknowledges long-running sprints as a risk (RISK-008: ">2 hours may hit resource limits") but provides no mechanism to test or validate this. The timeout formula (`max_turns * 120 + 300`) is specified but never stress-tested. The monitor's exponential moving average for growth rate (`alpha=0.3`) is a tuning parameter with no empirical basis documented.

**Spec evidence**: NFR-003 specifies the timeout formula but no test validates behavior at the boundary. The spec's stall detection thresholds (30s "thinking", 60s "STALLED") are arbitrary constants with no documented rationale or calibration data.

---

## 3. Confidence vs. Reality Gaps — Where Agent Self-Assessment Diverges from Actual Quality

### Gap 1: Extraction Claims 98% Coverage but Misses the Entire Emergent Architecture

The extraction (extraction.md) metadata states "Pass 1 (Source Coverage): 98%" and "Pass 2 (Anti-Hallucination): 100% PASS." These metrics create confidence that the spec is fully captured. But the extraction can only measure coverage of *what the spec says*, not *what the implementation will need*. The 38 extracted requirements cover the spec's 2,160-line vision; the 3,844-line reality includes pipeline inheritance, trailing gates, isolation layers, diagnostics, and KPIs — none extractable from the original spec because they didn't exist yet.

**Evidence**: Extraction Section 8: "Verification: Pass 1 (Source Coverage): 98%... Pass 3 (Section Coverage): 100% PASS... Pass 4 (Count Reconciliation): 32+8-2(dedup review, kept) = 38 total, matches." These are self-referential validation metrics — they confirm the extraction is consistent with itself, not with reality.

### Gap 2: Roadmap Validation Score of 0.92 Masks Architectural Incompleteness

The roadmap (roadmap.md) frontmatter states `validation_score: 0.92` and `validation_status: PASS`. But the roadmap's milestones assume the spec's architecture is complete. M2 ("Backend Core") doesn't include pipeline integration, trailing gates, or isolation layers. M3 ("TUI Dashboard") doesn't include KPI tracking or diagnostic display. The 0.92 score validates the roadmap against the extraction, not against what will actually be needed.

**Evidence**: Roadmap M2 deliverables D2.1-D2.8 cover CLI commands, config, process, and executor — but not `SprintGatePolicy`, `IsolationLayers`, `DiagnosticCollector`, `FailureClassifier`, or `TurnLedger`, all of which appear in the actual `executor.py`. The roadmap's "Decision Summary" states "Complexity score: 0.69, MEDIUM" — a classification that led to only 2 validation checkpoints. The actual complexity was HIGH.

### Gap 3: Test Strategy Claims Complete FR Coverage but Tests Mock Away the Failure Points

The test strategy (test-strategy.md) Validation Coverage Matrix maps all 38 FRs and 8 NFRs to validation milestones. But every FR is validated through mocks. The gap is visible in the method column: FR-026 (executor loop) is validated by "Integration test: executor loop iterates phases" — where the subprocess is mocked. FR-030 (status determination) is validated by "Status determination: 7-level priority chain verified" — where the result files are hand-crafted. The actual failure points (Claude subprocess producing unexpected output, monitor missing signals, status determination falling through to permissive defaults) are exactly the points that mocks eliminate.

**Evidence**: Test strategy Section "Acceptance Gates," M2 gate: "CLI options match spec; phase discovery handles all 4 naming patterns; process builds correct claude command; executor iterates phases and determines status correctly — All D2.1-D2.8 acceptance criteria met; no Critical/Major issues." This gate checks that *specified behavior* works, not that *unspecified behavior* is handled. The spec's own Risk Register (RISK-005) acknowledges "Monitor regex patterns for task IDs and tools may miss new Claude output formats" but classifies it as Medium impact with mitigation "integration tests with real output samples" — tests that are never defined as deliverables in any milestone.

### Gap 4: Complexity Classification Drives Under-Validation

The extraction classifies complexity as `MEDIUM` (score: 0.69), which drives the 1:2 validation-to-work interleave ratio (2 validation milestones for 5 work milestones). The roadmap's Decision Summary confirms: "MEDIUM base(5) + floor(3 domains ≥10% / 2) = 6 candidate slots; 5 work milestones + 2 validation at 1:2 interleave = 7 total." But the actual implementation complexity is substantially higher — it integrates with a separate pipeline abstraction layer, implements a gate policy pattern, adds 4-layer isolation, and includes diagnostic/KPI subsystems. A HIGH complexity classification would have mandated a 1:1 interleave ratio (more validation checkpoints), catching drift earlier.

**Evidence**: Extraction frontmatter: `complexity_score: 0.69, complexity_class: MEDIUM`. Actual codebase growth: 78% over estimate. New files not in spec: `diagnostics.py` (253 lines), `kpi.py` (149 lines), `debug_logger.py` (138 lines). New dependencies not in extraction: `superclaude.cli.pipeline.models`, `superclaude.cli.pipeline.process`, `superclaude.cli.pipeline.trailing_gate`.

---

## 4. Evidence Citations

### From sprint-cli-specification.md

| Citation | Section | Relevance |
|----------|---------|-----------|
| "~2,160 lines estimated across 11 files" | Section 1, Line ~47 | Actual is 3,844 across 14 files — the spec cannot predict emergent complexity |
| `models.py` "~180" lines estimated | Section 1, Table | Actual is 609 lines — the data model tripled due to pipeline inheritance, task-level types, and gate types |
| `executor.py` "~300" lines estimated | Section 1, Table | Actual is 815 lines — the executor absorbed isolation, diagnostics, and task-level execution |
| `/sc:task-unified Execute all tasks in @{phase_file}` | Section 7, `build_prompt()` | The prompt assumes Claude will follow structured output instructions — no fallback for when it doesn't |
| "EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT" | Section 7, Completion Protocol | These are LLM instructions, not contracts. The spec builds parsing logic around assumed compliance |
| "No lock because writes are to individual scalar fields (atomic on CPython due to the GIL)" | Section 6, Monitor-TUI Data Flow | Risk acknowledged (RISK-004) but the spec provides no mitigation beyond "add optional threading lock" |
| "Priority: 1. Timeout (exit 124) → TIMEOUT... 7. No result file and no output → ERROR" | Section 8, `_determine_phase_status` | Actual implementation has 9 levels, not 7 — emergent levels are untested by the spec's test strategy |
| "No new dependencies" | Section 13.4, Dependency Impact | Actual implementation depends on `superclaude.cli.pipeline.models`, `.process`, `.trailing_gate` — an entire abstraction layer not mentioned |
| Open Question #1: "Should `--start N` auto-detect incomplete previous runs?" | Section 14 | Deferred decisions accumulate as implicit technical debt that the implementing agent may or may not address |
| Open Question #2: "Should the monitor track token usage from claude output? Defer to v4.4" | Section 14 | Token budget exhaustion is a real failure mode (the implementation added `detect_error_max_turns`) — deferral left a gap |

### From extraction.md

| Citation | Section | Relevance |
|----------|---------|-----------|
| "total_requirements: 38" | Frontmatter | Fixed requirement count cannot accommodate emergent implementation needs |
| "complexity_score: 0.69, complexity_class: MEDIUM" | Frontmatter | Under-classification drives under-validation |
| "Pass 1 (Source Coverage): 98%" | Section 8 | Self-referential — measures extraction vs. spec, not extraction vs. reality |
| "RISK-005: Monitor regex patterns for task IDs and tools may miss new Claude output formats — Probability: Medium" | Section 7 | Risk identified but mitigation ("integration tests with real output samples") never appears as a deliverable |

### From roadmap.md

| Citation | Section | Relevance |
|----------|---------|-----------|
| "validation_score: 0.92, validation_status: PASS" | Frontmatter | Validates roadmap against extraction, not against implementation reality |
| "Critical path: M1 → M2 → M5 → M6 → M7" | Dependency Graph | Critical path doesn't account for the pipeline integration layer that the implementation required |
| "Parallel opportunity: M2 and M3 can execute concurrently after M1" | Dependency Graph | Parallelism assumes independence, but the actual TUI needs types from pipeline models that didn't exist at M1 time |
| "M2 deliverables D2.1-D2.8" | M2 section | Missing: pipeline inheritance, gate policy, isolation layers, diagnostic collection, KPI tracking |
| "Complexity: MEDIUM base(5) + floor(3 domains ≥10% / 2) = 6" | Decision Summary | Formula-driven complexity that doesn't account for emergent architectural needs |

### From test-strategy.md

| Citation | Section | Relevance |
|----------|---------|-----------|
| "continuous parallel validation — the assumption that work has deviated" | Validation Philosophy | Correct assumption, but validation only checks against the original spec, not against deviations |
| "D6.5: Full integration test... covering PASS, HALT, TIMEOUT, INTERRUPTED flows" | M6 deliverables | Only 4 of 9+ status values covered; INCOMPLETE, PASS_NO_SIGNAL, PASS_NO_REPORT, SKIPPED untested |
| "interleave_ratio: 1:2" | Frontmatter | Derived from MEDIUM complexity — too few checkpoints for actual HIGH complexity |
| "FR-030 validated by: Status determination: 7-level priority chain verified" | Coverage Matrix | Actual implementation has 9 levels — 2 levels escape validation |
| "executor.py: Integration — Mock ClaudeProcess.start/wait, mock monitor, verify flow" | Section 12.2 | The failure point (real subprocess output) is precisely what mocks remove |

---

*End of diagnostic report. No fixes proposed.*
