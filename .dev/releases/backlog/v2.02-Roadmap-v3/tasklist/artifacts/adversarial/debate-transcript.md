# Adversarial Debate Transcript

**Pipeline**: sc:adversarial Mode A (compare existing)
**Artifacts compared**: approach-1-empirical-probe-first.md, approach-2-claude-p-proposal.md, approach-3-hybrid-dual-path.md
**Depth**: standard (2 rounds + final scoring)
**Date**: 2026-02-23

---

## Round 1: Advocate Statements

### Advocate A1 (Approach 1: Empirical Probe First)

**Position Summary**: The probe-first approach is the only epistemically honest strategy. Approaches 2 and 3 both assume `claude -p` will work reliably for a complex 5-step pipeline — an assumption contradicted by GitHub Issues #837, #1048, and #1339. Spending 1-2 hours and ~$25 to empirically validate before committing 12-15 hours of implementation is a 6-7x ROI on risk reduction.

**Steelman of Approach 2**: Approach 2's clarity is its greatest asset. The exact command template (Section 2.2) is immediately implementable. The 8-row error handling matrix is comprehensive. The philosophy of "commit fully" reduces decision fatigue and eliminates the architectural ambiguity of trying to support multiple paths. If `claude -p` works, Approach 2 is the fastest path to a shipping feature.

**Steelman of Approach 3**: Approach 3's mid-pipeline fallover (Section 3, "Mid-Pipeline Fallover") addresses a real architectural gap. If a headless session crashes after producing diff-analysis.md but before completing the debate, Approaches 1 and 2 both discard that work and restart from scratch. Approach 3's artifact inventory and resume logic preserves partial progress. The enhanced 5-step Task-agent pipeline with real convergence tracking is also a genuine quality improvement over the current 3-step fallback.

**Strengths Claimed**:
1. **Risk quantification**: Table in Section 1 assigns probability and consequence to each risk, enabling rational resource allocation. No other approach quantifies risk.
2. **Three-strategy testing**: S1/S2/S3 comparison ensures we select the objectively best invocation form, not the one we assumed would work.
3. **20-point behavioral adherence rubric**: The only approach that measures whether the adversarial pipeline actually follows SKILL.md instructions vs. drifting to its own interpretation. Issue #1048 specifically warns about behavioral instruction drift.
4. **Statistical methodology**: Wilson score interval at 95% CI for reliability testing. Not guessing — measuring.
5. **Decision gates**: Three sequential gates with explicit pass/fail criteria and defined fallback actions at each gate.

**Weaknesses Identified in Others**:
1. **Approach 2 (Section 3, Task 0.0)**: The 3-test "viability probe" tests only mechanics (binary exists, basic invocation, system prompt injection). It does NOT test behavioral adherence — whether the injected SKILL.md instructions are actually followed for a complex multi-step pipeline. This is the critical gap: `claude -p` may work mechanically but produce garbage output that ignores the adversarial protocol.
2. **Approach 3 (Section 5, Task 0.0)**: The "Invocation Capability Probe" runs 3 probe executions for Path A and a smoke test for Path B. It records `probe_success_count` and `avg_latency_ms` but does NOT measure behavioral adherence or pipeline fidelity. Same gap as Approach 2.

**Concessions**:
- The 10-run reliability test (T11) is expensive ($15-25, 45 minutes) and may not be justified within sprint scope.
- The probe itself does not specify the implementation design. After the probe completes, you still need an implementation spec — which is what Approaches 2 and 3 provide.
- The probe is a pre-gate, not an architecture. It answers "should we use `claude -p`?" but not "how should we use it?"

---

### Advocate A2 (Approach 2: claude -p as Primary)

**Position Summary**: The implementation design IS the deliverable. A probe that costs $25+ and 2 hours, only to produce a boolean "yes/no" that still requires a separate implementation spec, is not efficient sprint planning. Approach 2 provides the complete, implementable specification with a lightweight viability check baked in as Task 0.0.

**Steelman of Approach 1**: The 20-point behavioral adherence rubric (Section 3, T05) is genuinely valuable. If we're going to depend on `claude -p` executing a complex pipeline, we should measure whether it actually follows the protocol. Approach 1 is right that mechanical invocation success (binary exists, file I/O works) is necessary but not sufficient. The rubric's 5 categories (Diff Analysis Structure, Debate Protocol, Scoring Method, Base Selection, Merge Execution) map directly to the 5 pipeline steps and would serve as excellent acceptance criteria.

**Steelman of Approach 3**: The enhanced 5-step Task-agent pipeline (Section 4, F1-F5) is a meaningful upgrade over the current 3-step fallback. The current fallback's fixed `convergence_score: 0.5` sentinel is acknowledged as a quality compromise. Approach 3's real convergence tracking in the Task-agent path eliminates this compromise. The return-contract-as-universal-interface abstraction (Section 6) is also architecturally clean.

**Strengths Claimed**:
1. **Complete implementation spec**: Section 5 provides the exact Wave 2 Step 3d rewrite — copy-paste implementable. No other approach provides implementation-ready specification text.
2. **Exact command template**: Section 2.2 shows the precise `claude -p` command with all flags, environment variable handling, and parameter configuration. Zero ambiguity.
3. **Minimal infrastructure**: One new ref file (`refs/headless-invocation.md`), one new return contract field (`invocation_method`). No new flags, no routing logic, no decision trees.
4. **Sprint-spec mapping**: Section 8 provides a 14-row table mapping every sprint-spec section to its proposed change type (Replace, Append, Rewrite, Add entry, etc.). Implementers can work through the table sequentially.
5. **Clear primary/fallback architecture**: The headless path is primary. The Task-agent path is fallback. No ambiguity about which is "preferred" or when to use which.
6. **CLAUDECODE environment handling**: Section 2.5 addresses the specific nested-session detection issue that neither Approach 1 nor Approach 3 details at the implementation level.

**Weaknesses Identified in Others**:
1. **Approach 1**: The probe is a pre-gate, not a design. After spending 2 hours and $25, you still don't have a single line of implementation specification. The probe's output is "HEADLESS_PRIMARY / HEADLESS_WITH_RETRY / FALLBACK_ONLY" — three categories, none of which include actual implementation details.
2. **Approach 3**: The dual-path architecture doubles the maintenance surface. Every change to the sc:adversarial pipeline must be reflected in both Path A (system prompt injection) AND Path B (Task agent prompt extraction). The `--invocation-mode` flag adds user-facing complexity for a mechanism that should be invisible. The depth-based routing (`--depth quick` → inline) is premature optimization.

**Concessions**:
- The 3-test viability probe (Section 3, Task 0.0) does not test behavioral adherence. If `claude -p` mechanically works but ignores SKILL.md instructions, the probe passes but the pipeline produces garbage. This is a real gap.
- The fallback protocol retains the 3-step compression (F1, F2/3, F4/5) and the 0.5 convergence sentinel. This could be upgraded to the enhanced 5-step pipeline without significantly increasing complexity.
- No mid-pipeline recovery. If headless crashes after Step 2, all work is lost and the fallback starts from scratch.

---

### Advocate A3 (Approach 3: Hybrid Dual-Path)

**Position Summary**: The dual-path architecture is the only approach that provides reliability guarantees regardless of environment. Approach 2 bets everything on `claude -p` being available and reliable. Approach 1 tests whether `claude -p` works but doesn't provide a high-quality alternative when it doesn't. Approach 3 ensures a high-fidelity pipeline executes in every environment.

**Steelman of Approach 1**: The probe-first philosophy correctly identifies that committing to an untested mechanism is risky. The 13-test suite with statistical rigor would produce high-confidence evidence. The 3-strategy comparison (S1/S2/S3) is methodologically sound — we shouldn't assume system-prompt injection is best without testing alternatives.

**Steelman of Approach 2**: The implementation completeness is unmatched. Section 5's exact specification text, Section 8's 14-row modification table, and the clear primary/fallback hierarchy make Approach 2 the most implementable proposal. The CLAUDECODE environment variable handling (Section 2.5) is a genuine implementation detail that both Approaches 1 and 3 should adopt.

**Strengths Claimed**:
1. **Environment portability**: Path B (Task agents) is always available. No dependency on `claude` CLI being in PATH. Works in Docker containers, CI runners, sandboxed environments.
2. **Mid-pipeline fallover**: Artifact-aware resume from partial headless execution. The 5-level resume logic (all steps present → contract assembly only; steps 1-3 → resume from F4; step 1 → resume from F3; variants only → resume from F2; nothing → full restart) preserves work.
3. **Enhanced Task-agent pipeline**: Full 5-step fidelity (F1-F5) with real convergence tracking. Current fallback's 0.5 sentinel eliminated. Quality gap between paths narrowed from ~25% to ~5-10%.
4. **Return contract as universal interface**: Consumer (step 3e) is completely path-agnostic. Adding future paths (Skill tool API) requires zero consumer changes.
5. **Depth-based routing**: `--depth quick` skips headless overhead (5-10s startup) for a single debate round where Task agents achieve equivalent quality. Smart resource allocation.

**Weaknesses Identified in Others**:
1. **Approach 1**: Does not specify what happens after the probe. The sprint still needs an implementation design. Approach 1 is an additive cost, not a substitute for Approaches 2 or 3.
2. **Approach 2**: Single-path dependency. If `claude -p` reliability degrades in a future Claude Code update (Issue #1048 notes behavioral instruction drift), the entire adversarial feature degrades. The fallback is a compressed 3-step approximation, not a full pipeline.

**Concessions**:
- The `--invocation-mode` flag adds user-facing complexity. In most cases, `auto` is correct and users shouldn't need to override the routing decision. The flag may be YAGNI.
- The dual-path architecture approximately doubles the adversarial pipeline test surface. Both paths must be independently verified.
- Sprint scope expansion is real. The enhanced F1-F5 Task-agent pipeline is essentially a second full implementation of the adversarial protocol, plus the routing logic, plus the fallover mechanism. This is likely 40-60% more sprint work than Approach 2.
- The depth-based routing (`--depth quick` → inline) may be premature. If headless startup is only 5-10 seconds, the overhead is negligible for all depth levels.

---

## Round 2: Rebuttals

### Rebuttal A1 (Approach 1 responding)

**On A2's critique ("probe is a pre-gate, not a design")**: This is accurate and intentional. The probe's purpose is NOT to provide an implementation design. It's to prevent wasting 12-15 hours implementing a design that doesn't work. The expected value math is clear: 2 hours to potentially save 12 hours. However, I concede that the probe should be lighter. The full 13-test, $25+ suite is over-scoped for a sprint context. A reduced probe — T01 (smoke), T04 (system-prompt injection), T05 (behavioral adherence rubric applied to T04 output), and T07 (multi-round check) — would take 30-40 minutes and cost ~$5-8. This provides the critical behavioral adherence data that Approaches 2 and 3 lack, without the reliability testing that's genuinely YAGNI.

**On A3's mid-pipeline fallover**: I concede this is genuinely valuable. My approach doesn't address partial-progress recovery at all. If the probe passes and we commit to headless-first, mid-pipeline failures would waste completed work.

**Updated position**: The probe should be integrated INTO Approach 2's Task 0.0, not as a separate pre-phase. Specifically: Approach 2's 3-test viability probe should be extended with ONE additional test — a mini-pipeline execution with behavioral adherence scoring. This adds ~15 minutes and ~$3 to Task 0.0 but provides the critical behavioral data.

---

### Rebuttal A2 (Approach 2 responding)

**On A1's behavioral adherence gap**: Conceded. The 3-test viability probe tests mechanics only. Extending Task 0.0 with a behavioral adherence check is a high-value, low-cost improvement. Specifically: after the 3 mechanical tests pass, run one system-prompt-injection pipeline execution on minimal fixtures and score the output against Approach 1's behavioral adherence rubric (5 categories, 20 points, minimum 14/20). If it fails, route to fallback-only variant immediately. This costs ~$3 and ~15 minutes — well within the sprint's pre-implementation budget.

**On A3's enhanced fallback**: Partially conceded. The current 3-step fallback (F1, F2/3, F4/5) with 0.5 convergence sentinel IS a quality compromise. Upgrading to a 5-step fallback with real convergence tracking is valuable. However, this does NOT require the full dual-path architecture. The upgrade can be applied to Approach 2's fallback (step 3d-iv) without the routing decision tree, `--invocation-mode` flag, or "first-class peer" philosophy. The fallback remains a fallback — it just becomes a better fallback.

**On A3's mid-pipeline fallover**: Partially useful but over-engineered. The full 5-level artifact inventory with step-by-step resume logic is complex and hard to test. A simpler version: if headless fails and `diff-analysis.md` exists in the output directory, the fallback skips F2 (diff analysis) and starts from F3 (debate). Otherwise, start from F1. Two states, not five. This captures 80% of the value at 20% of the complexity.

**On A3's depth-based routing**: Rejected. The headless startup overhead (5-10 seconds) is negligible compared to pipeline execution time (2-30 minutes). Routing `--depth quick` to Task agents saves 5 seconds but adds permanent routing complexity. Not a worthwhile trade.

**Updated position**: Absorb Approach 1's behavioral adherence rubric as an extended Task 0.0 gate. Upgrade the fallback from 3-step to 5-step with real convergence. Add simplified mid-pipeline awareness (2-state, not 5-state). Reject Approach 3's routing tree and `--invocation-mode` flag.

---

### Rebuttal A3 (Approach 3 responding)

**On A2's "over-engineered routing"**: I concede that the full 5-step routing decision tree with the `--invocation-mode` flag is more complexity than the current sprint justifies. The depth-based routing is an optimization that can be added later if data supports it. The core routing logic — binary check + execution probe → select path — is simple and necessary. But it doesn't need a YAML decision tree or a user-facing flag.

**On A2's "two maintenance paths"**: This is the strongest critique. Maintaining two parallel implementations of the adversarial pipeline IS a real burden. The mitigation (both source from SKILL.md) is only partial — the Path B section extraction logic must be kept in sync with SKILL.md reorganizations. However, the enhanced 5-step Task-agent pipeline is valuable regardless of whether Path A (headless) exists. Even in a single-path architecture (Approach 2), upgrading the fallback from 3-step to 5-step improves quality when `claude -p` fails.

**On A1's behavioral adherence**: A2's rebuttal is correct — integrating a behavioral adherence check into the viability probe is a high-value improvement. I concede that this is better than my "3 probe executions + average latency" approach, which tests mechanics but not pipeline quality.

**Updated position**: Drop the `--invocation-mode` flag, the depth-based routing, and the "first-class peer" framing. Accept Approach 2's primary/fallback architecture. Contribute the enhanced 5-step fallback pipeline and the simplified mid-pipeline awareness. The result is Approach 2's structure with Approach 3's fallback quality.

---

## Round 2 Convergence Assessment

### Points Resolved (advocates agree):

| ID | Point | Resolution |
|----|-------|------------|
| C-001 | Behavioral adherence testing | All agree: extend Task 0.0 with adherence rubric (Ap1's T05) |
| C-002 | Fallback should be 5-step | All agree: upgrade from F1/F2-3/F4-5 to F1-F5 with real convergence |
| C-003 | Primary/fallback architecture | Ap3 concedes: primary/fallback (Ap2) over dual-path peer |
| C-004 | `--invocation-mode` flag | Ap3 concedes: YAGNI, routing should be automatic |
| C-005 | Depth-based routing | Ap3 concedes: premature optimization, drop |
| C-006 | Return contract `invocation_method` field | All agree: useful for observability |
| C-007 | CLAUDECODE env handling | All agree: adopt Ap2's pattern (Section 2.5) |
| C-008 | Full 13-test probe is over-scoped | Ap1 concedes: reduce to 4-5 essential tests integrated into Task 0.0 |
| C-009 | 10-run reliability test | Ap1 concedes: YAGNI for sprint scope |
| C-010 | Sprint-spec mapping table | All agree: Ap2's 14-row table (Section 8) is the clearest implementation guide |

### Points Unresolved:

| ID | Point | Disagreement |
|----|-------|-------------|
| U-001 | Mid-pipeline fallover scope | Ap2: 2-state (diff exists → skip F2). Ap3: 5-level resume. Ap1: no position. |
| U-002 | Probe scope | Ap1: 4-5 tests (~30 min, ~$5). Ap2: 3 tests + 1 adherence test (~15 min, ~$3). |

### Convergence Score

Resolved: 10 points. Unresolved: 2 points. **Convergence: 10/12 = 0.83**

This exceeds the standard threshold of 0.80. The debate can conclude.

---

## Final Round: Resolution of Unresolved Points

### U-001: Mid-Pipeline Fallover Scope

**Resolution**: Adopt a 3-state model (compromise between Ap2's 2-state and Ap3's 5-state):

1. **State A**: No artifacts present → full fallback from F1
2. **State B**: Variant files present (but no diff-analysis.md) → fallback from F2
3. **State C**: diff-analysis.md present → fallback from F3

Rationale: The headless pipeline writes variants first (Mode B generation), then diff-analysis, then debate. The most likely failure points are during the debate (most token-intensive) or merge (most complex). These three states cover the realistic failure modes without the complexity of tracking 5+ artifact types.

### U-002: Probe Scope

**Resolution**: Adopt Approach 2's 3-test mechanical probe + 1 behavioral adherence mini-test. Total: 4 tests, ~20 minutes, ~$4. The behavioral adherence test runs a minimal pipeline on tiny fixtures and scores against Approach 1's rubric (simplified to 3 categories: Diff Analysis Structure, Multi-Round Debate, and Artifact Production). Passing threshold: score all 3 categories as "present" (binary, not graded).

**Final Convergence: 12/12 = 1.00**
