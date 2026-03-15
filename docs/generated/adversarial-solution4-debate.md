# Adversarial Debate: Solution #4 -- Artifact Batching (Separate Implementation from Documentation)

**Date**: 2026-03-15
**Format**: 3-round structured adversarial debate
**Orchestrator**: Debate Orchestrator (neutral)
**Proponent**: Advocate-A (argues for Solution #4 as primary/complete solution)
**Opponent**: Advocate-B (challenges completeness, complexity cost, and quality claims)

---

## Source Evidence Inventory

Before debate begins, the following evidence was loaded and verified by the orchestrator:

| Source | Key Facts Extracted |
|--------|-------------------|
| `solution-4-artifact-batching-brainstorm.md` | 5 approaches (A-E), hybrid A+D+E recommended, 10 documentation files per phase, crash at turn 106 writing completion report |
| `executor.py` | `AggregatedPhaseReport` (lines 179-282) with `to_markdown()` and `to_yaml()`, single-subprocess-per-phase model in `execute_sprint()` (lines 490-763), `_determine_phase_status()` reads result file |
| `models.py` | `PhaseResult` has no `impl_status`/`artifacts_status` fields, `TurnLedger` supports `debit()`/`credit()`, `SprintConfig` has no `artifact_mode` field |
| `process.py` | `ClaudeProcess.build_prompt()` instructs agent to execute tasks AND write completion report in same session, `build_task_context()` provides prior-task injection |
| `D-0005/spec.md` | 66 lines, factual content (algorithm rules, error codes, module location, test coverage), no decision rationale or subjective assessment |

---

## Round 1: Completeness vs. Complexity

### Advocate-A (Proponent)

**Claim**: Solution #4 is the only solution among the five proposed that eliminates the root cause of the context exhaustion bug rather than mitigating symptoms.

**Argument**:

The crash at turn 106 occurred because a single Claude Code subprocess was asked to do two fundamentally different jobs in one session: (1) implement 7 tasks with code and tests, and (2) write 10 documentation artifacts. By turn 106, the implementation work had consumed the vast majority of the 200K context window. The remaining documentation work -- which the brainstorm document correctly identifies as "pure bookkeeping" -- had no room to execute.

Solutions #2 (detection/recovery) and #3 (prompt reduction) are symptom mitigations:

- **Solution #2** detects that context is exhausted and gracefully exits. This is valuable for resilience, but it does not prevent the loss of artifacts. The sprint still fails to produce its documentation. Detection without prevention is an incomplete answer.

- **Solution #3** reduces prompt size to buy more headroom. This delays the crash but does not eliminate it. As phase complexity scales (more tasks, more deliverables), the headroom gained by prompt reduction will eventually be consumed. It is a linear mitigation against a problem that grows with phase size.

**Solution #4** eliminates the structural cause: it separates the two workloads into two subprocesses, each with a fresh 200K context budget. The implementation subprocess does only implementation. The artifact writer subprocess does only documentation. Neither can exhaust the other's budget.

The evidence supports this:

1. `AggregatedPhaseReport.to_markdown()` (executor.py lines 244-282) already produces a complete phase report with per-task status, turns consumed, and EXIT_RECOMMENDATION. The executor can write `phase-N-result.md` directly from this method, decoupling status determination from the agent entirely. This is a 15-line change to `execute_sprint()`.

2. The artifact writer subprocess receives: (a) the `AggregatedPhaseReport` output, (b) the phase tasklist file path, (c) the list of artifact paths to produce. With a fresh 200K context budget and only ~10 files to write, this is well within capacity.

3. The `TurnLedger` in `models.py` already supports `debit()`/`credit()` operations. Allocating a reserved artifact budget (15-25 turns) is straightforward.

**Position**: Solution #4 should be the primary solution. Solutions #2 and #3 are complementary hardening measures, not alternatives.

---

### Advocate-B (Opponent)

**Challenge**: The complexity cost is disproportionate to the frequency and severity of the failure, and the "completeness" claim overstates the architectural necessity.

**Argument**:

1. **Frequency**: The context exhaustion crash occurred once, in Phase 2 of one specific sprint, where 7 tasks produced 10 documentation artifacts. This is the most artifact-dense phase in the project's history. The brainstorm document provides no evidence that this failure has occurred in other phases or other sprints. Building a two-subprocess architecture for a single observed failure is over-engineering unless there is evidence that this will recur.

2. **Complexity cost is real and understated**: The brainstorm lists 5 files to modify and a "moderate" complexity assessment, but the actual implementation scope includes:
   - A new `ArtifactWriterProcess` class or `build_artifact_prompt()` method
   - Conditional logic in `execute_sprint()` for the two-stage flow
   - Extension of `PhaseResult` with `impl_status` and `artifacts_status`
   - A new `artifact_mode` field on `SprintConfig`
   - A new CLI option `--artifact-mode`
   - Integration tests for two-stage phase execution
   - Modified prompt in `build_prompt()` to conditionally exclude artifact instructions

   This is not "moderate." This is a significant architectural refactor of the sprint executor's core loop. Every future change to the executor must account for the two-stage model.

3. **Solution #3 (prompt reduction) may be sufficient**: If the prompt is reduced by 30-40% (which the solution-3 brainstorm explores), and the completion report is simplified to use `AggregatedPhaseReport.to_markdown()` (which both solutions agree on), the combined headroom may be enough to avoid the crash entirely. The cost of Solution #3 is a prompt change -- no architectural modifications, no new subprocess types, no conditional execution paths.

4. **The "quick win" undermines the "complete solution" narrative**: The brainstorm's own implementation priority lists "Executor writes result file" as item #1 -- the smallest change with the highest impact. If the executor writes the result file from `AggregatedPhaseReport.to_markdown()`, the crash at turn 106 (which was writing the completion report) would not have occurred. That single change, combined with Solution #3's prompt reduction, addresses the observed failure without the full two-subprocess architecture.

**Position**: The executor writing the result file is a standalone quick win that should be implemented immediately. The full artifact batching architecture should be deferred until there is evidence of recurrence.

---

### Round 1 Scoring Matrix

| Point | Proponent Score | Opponent Score | Convergence |
|-------|----------------|----------------|-------------|
| Root cause elimination vs. symptom mitigation | 8/10 | 5/10 | 35% -- fundamental disagreement on whether root cause elimination is necessary for a single-occurrence failure |
| Complexity cost justification | 5/10 | 8/10 | 30% -- proponent understates complexity; opponent's enumeration of changes is accurate |
| Executor writing result file as quick win | 9/10 | 9/10 | 95% -- both sides agree this is high-value, low-cost |
| Scalability argument | 7/10 | 4/10 | 40% -- proponent's argument that phase complexity will grow is reasonable but unquantified |
| Solution #3 sufficiency | 4/10 | 7/10 | 35% -- opponent's point about combined headroom is credible but speculative |

**Round 1 Convergence**: 47% (below 70% threshold -- proceed to Round 2)

---

## Round 2: Artifact Quality and the 10-20% Gap

### Advocate-A (Proponent)

**Response to complexity concerns**: The complexity argument is valid but must be weighed against the benefit of clean separation of concerns. The current architecture conflates two responsibilities into one subprocess. Even if the crash occurred only once, the conflation is an architectural smell.

**Addressing artifact quality with evidence**:

Examining D-0005/spec.md (the actual artifact produced by the sprint), the content is:

1. **Algorithm rules** (lines 15-27): Factual documentation of `resolve_workflow_path()` behavior. This is directly derivable from reading the source code.

2. **Error codes** (lines 29-33): A table mapping codes to triggers. This is directly derivable from the exception classes in `models.py`.

3. **Module location** (lines 37-44): Code snippets showing function signatures and class names. This is literally copy-paste from source files.

4. **Test coverage** (lines 60-66): Test file path and test method names. This is derivable from running `grep -r "def test_" tests/cli_portify/test_config.py`.

**100% of D-0005's content is factual and reconstructable from source files.** A post-phase artifact writer with access to the codebase would produce identical content. There is no decision rationale, no subjective assessment, no "lived experience" content in this artifact.

The brainstorm document's own assessment states: "For 80-90% of artifact content (factual records, file listings, test results), quality will be equivalent. For 10-20% (decision rationale, nuanced observations), quality may degrade."

I challenge this 10-20% estimate as too high for the actual artifacts produced. The D-0005 through D-0014 series are specification documents, not decision journals. The "10-20% quality gap" applies to a hypothetical artifact type (decision records with rationale) that is not well-represented in the actual deliverables.

**The executor writing the result file is not just a "quick win" -- it is the foundation of the full solution.** Once the executor owns the result file, the conceptual separation between "implementation subprocess" and "documentation stage" is established. The artifact writer subprocess is a natural extension, not a separate initiative.

---

### Advocate-B (Opponent)

**Concession on D-0005 quality**: The evidence is persuasive for spec-type artifacts. D-0005 is indeed entirely factual. However, this creates a selection bias -- D-0005 is the simplest artifact type (a single function's algorithm documentation).

**Counter-evidence -- the quality gap is real for non-trivial artifacts**:

The brainstorm document references D-0008 (22 KB, 372 lines) containing "rich interface documentation, dependency analysis, and system quality assessments." Without access to D-0008, I note that the brainstorm author -- who had full access to all artifacts -- assessed the quality gap at 10-20%. The proponent's claim that this is "too high" contradicts the assessment of the person who examined the full artifact set.

More importantly, the brainstorm identifies specific content types that degrade:

1. **Decision records** (like "OQ-006 Decision Record"): These capture WHY a particular approach was chosen, not just WHAT was implemented. A post-hoc writer can describe what exists but cannot reconstruct the reasoning that led to choosing it over alternatives.

2. **Evidence artifacts** (like D-0007 evidence.md): These record the specific verification steps taken during implementation. A post-hoc writer would need to re-run verification commands rather than recording them in real time. This is both slower and potentially produces different results if the system state has changed.

3. **Nuanced observations** (like the OQ-008 annotation in D-0008): These arise from the agent's direct experience during implementation and would not surface in a cold review of source files.

**The incremental path is safer**: The proponent frames the executor-writes-result-file change as "the foundation of the full solution." This is a rhetorical framing, not a technical dependency. The executor can write the result file without any commitment to the full two-subprocess architecture. The two changes are independently valuable.

**What about the interaction with Solutions #2 and #3?** If Solution #2 (context exhaustion detection) is implemented, the executor can detect when the agent is approaching context limits and gracefully exit before the crash. If Solution #3 (prompt reduction) is implemented, the headroom increases. Together, these two solutions may prevent the crash from recurring without the complexity of a second subprocess. Solution #4 becomes insurance against a failure that has already been mitigated twice.

---

### Round 2 Scoring Matrix

| Point | Proponent Score | Opponent Score | Convergence |
|-------|----------------|----------------|-------------|
| D-0005 quality reproducibility | 9/10 | 7/10 | 75% -- both agree spec-type artifacts are reproducible; disagreement on generalizability |
| 10-20% quality gap accuracy | 6/10 | 7/10 | 60% -- proponent's challenge is credible for spec-type but opponent correctly notes selection bias |
| Decision record quality loss | 4/10 | 8/10 | 35% -- proponent has no counter-evidence; decision rationale genuinely cannot be reconstructed post-hoc |
| Executor-writes-result as foundation vs. standalone | 6/10 | 7/10 | 55% -- technically both are right; it is independently valuable AND a natural foundation |
| Solutions #2 + #3 as sufficient combined mitigation | 5/10 | 7/10 | 45% -- credible but speculative; depends on prompt reduction effectiveness |

**Round 2 Convergence**: 54% (below 70% threshold -- proceed to Round 3)

---

## Round 3: Synthesis and Refined Recommendation

### Advocate-A (Proponent) -- Final Position

I accept three of the opponent's points:

1. **The full two-subprocess architecture should not be implemented for a single-occurrence failure.** The complexity cost is real, and building it now is premature unless there is evidence of recurrence.

2. **The executor writing the result file is independently valuable and should be implemented immediately.** I withdraw the framing of it as merely "the foundation" -- it is a complete, standalone improvement that decouples status determination from agent artifact writing.

3. **Solutions #2 and #3 are complementary, not inferior.** My original framing of them as "symptom mitigations" was dismissive. Detection (Solution #2) provides resilience. Prompt reduction (Solution #3) provides headroom. Both are necessary.

**However, I maintain that the architectural separation is the correct long-term direction.** As sprint complexity grows (more phases, more tasks per phase, more deliverables), the single-subprocess model will hit context limits again. The question is not IF but WHEN. The full artifact batching architecture should be designed now and implemented when triggered by either:
- A second occurrence of the context exhaustion crash, or
- A sprint spec that exceeds 8 deliverables per phase

**Revised position**: Implement the quick win now; design (but do not build) the full architecture; implement it on the next recurrence.

---

### Advocate-B (Opponent) -- Final Position

I accept two of the proponent's points:

1. **The architectural separation is the correct long-term direction.** The single-subprocess conflation of implementation and documentation is a design limitation that will eventually constrain scalability. I withdraw my characterization of it as "over-engineering" -- it is premature engineering, not over-engineering.

2. **D-0005 demonstrates that spec-type artifacts are fully reproducible post-hoc.** For artifact types that document WHAT EXISTS (function signatures, error codes, test coverage), a post-phase writer produces equivalent output.

**However, I maintain three reservations**:

1. **Decision records cannot be reconstructed.** Any artifact that documents WHY a choice was made (not just WHAT was chosen) requires implementation-time capture. If the full architecture is eventually built, the Approach C manifest (lightweight metadata capture during implementation) should be incorporated to capture key decisions.

2. **The trigger threshold should be evidence-based.** "8 deliverables per phase" is arbitrary. The correct trigger is when `(estimated_artifact_tokens / remaining_context_budget) > 0.5` -- that is, when artifact writing is projected to consume more than half the remaining context budget. This can be calculated from the number of artifacts times an average token cost per artifact.

3. **The "deferred" default in Approach E is the wrong default for v1.** When the full architecture is built, the default should be "inline" (current behavior) with "deferred" as an opt-in flag. This preserves backward compatibility and allows users to choose based on their specific phase complexity. Once deferred mode is validated in production, the default can be flipped.

---

### Round 3 Scoring Matrix

| Point | Proponent Score | Opponent Score | Convergence |
|-------|----------------|----------------|-------------|
| Executor writes result file: implement now | 10/10 | 10/10 | 100% |
| Full architecture: design now, defer implementation | 8/10 | 8/10 | 90% |
| Decision records need implementation-time capture | 6/10 | 9/10 | 75% |
| Trigger threshold for implementation | 7/10 | 8/10 | 80% |
| Default mode for artifact writing | 5/10 | 8/10 | 60% |
| Solutions #2 + #3 as complementary | 8/10 | 9/10 | 90% |

**Round 3 Convergence**: 82.5% (above 70% threshold -- debate concludes)

---

## Final Recommendation

### Consensus Points (convergence > 70%)

1. **IMPLEMENT NOW -- Executor writes `phase-N-result.md` from `AggregatedPhaseReport.to_markdown()`**
   - This is a ~15-line change to `execute_sprint()` at line 694 (after `logger.write_phase_result(phase_result)`)
   - Decouples status determination from agent artifact writing entirely
   - `_determine_phase_status()` reads the executor-written result file, which is deterministic and never crashes
   - This alone would have prevented the turn-106 crash
   - **Estimated effort**: Small (1-2 hours)
   - **Risk**: Very low -- `AggregatedPhaseReport.to_markdown()` is already tested and produces valid output

2. **IMPLEMENT NOW -- Solutions #2 (detection) and #3 (prompt reduction) as complementary hardening**
   - Solution #2: Context exhaustion detection with graceful exit prevents data loss
   - Solution #3: Prompt reduction increases headroom for all phases, not just artifact-heavy ones
   - Together with the quick win above, these three changes provide defense in depth

3. **DESIGN NOW, DEFER IMPLEMENTATION -- Full artifact batching architecture (Approach A+E)**
   - Design the `ArtifactWriterProcess` class, `build_artifact_prompt()` method, and `PhaseResult` extension
   - Document the design in a spec file for future implementation
   - **Implementation trigger**: Second occurrence of context exhaustion crash, OR phase spec with >8 deliverables, OR when `(artifact_count * 1500 tokens) > (200K - estimated_implementation_tokens) * 0.5`

4. **IF BUILT -- Include manifest capture (Approach C hybrid) for decision records**
   - Lightweight metadata capture during implementation (task_id, key_decision, 1-2 sentences)
   - Supplements post-hoc artifact writing for the 10-20% of content that cannot be reconstructed

### Contested Points (convergence < 70%)

1. **Default mode for artifact writing** (60% convergence): The proponent favors "deferred" as default; the opponent favors "inline" as default with "deferred" as opt-in. This should be resolved by production data: run deferred mode on 3 sprints and compare artifact quality against inline artifacts from prior sprints.

2. **10-20% quality gap magnitude** (60% convergence): The actual gap depends on artifact type distribution. For spec-heavy sprints (like the CLI Portify sprint), the gap may be <5%. For decision-heavy sprints, it may be >20%. This is an empirical question that cannot be resolved by debate alone.

### Assessment of the Five Original Claims

| # | Claim | Verdict |
|---|-------|---------|
| 1 | Artifact writing is pure bookkeeping -- separating it is architecturally clean | **Mostly true**. Spec-type artifacts (D-0005 class) are pure bookkeeping. Decision records and evidence artifacts contain implementation-time knowledge that is not bookkeeping. The separation is architecturally clean for ~80% of artifact types. |
| 2 | The executor should write `phase-N-result.md` itself using `AggregatedPhaseReport.to_markdown()` | **True and actionable now.** Both sides agree. This decouples status determination from agent behavior and prevents the observed crash. Highest-priority change. |
| 3 | A post-phase artifact writer subprocess can produce equivalent-quality artifacts | **True for spec/factual artifacts; false for decision rationale.** Quality is equivalent for content derivable from source files (80-95% of actual artifacts). Quality degrades for decision records and nuanced observations (5-20%). Mitigation: manifest capture during implementation. |
| 4 | The complexity cost is justified | **Not yet justified.** The complexity is real (5 files, new subprocess type, conditional execution). For a single-occurrence failure, the cost exceeds the benefit. Justified when evidence of recurrence is established. |
| 5 | This is a complete solution on its own | **Partially true.** It eliminates the root cause (context exhaustion from artifact writing) but is not needed as a standalone solution when combined with the quick win (executor writes result file) and Solutions #2 + #3. It becomes necessary when simpler mitigations are insufficient. |

### Implementation Sequence

```
Phase 1 (Immediate -- this sprint):
  [1] Executor writes phase-N-result.md from AggregatedPhaseReport.to_markdown()
  [2] Solution #2: Context exhaustion detection in the monitor
  [3] Solution #3: Prompt reduction in build_prompt()

Phase 2 (Design only):
  [4] Write architecture spec for ArtifactWriterProcess
  [5] Define PhaseResult extension (impl_status, artifacts_status)
  [6] Define SprintConfig.artifact_mode and CLI flag

Phase 3 (Triggered by recurrence):
  [7] Implement ArtifactWriterProcess
  [8] Implement two-stage execution in execute_sprint()
  [9] Implement manifest capture (Approach C hybrid)
  [10] Integration tests for two-stage flow
```

---

## Debate Metadata

| Metric | Value |
|--------|-------|
| Total rounds | 3 |
| Final convergence | 82.5% |
| Points fully converged (>90%) | 3 of 12 |
| Points contested (<70%) | 4 of 12 |
| Unresolved conflicts | 2 (default mode, quality gap magnitude) |
| Primary recommendation | Implement quick win + Solutions #2/#3 now; design full architecture; defer implementation |
