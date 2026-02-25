# Deferral Confidence Scoring Matrix
## sc:roadmap Adversarial Pipeline — v2.01-Roadmap-v3

**Purpose**: Adversarial debate assessment of the 18 explicitly deferred solutions/features.
**Method**: 6 parallel agents each debate 3 items in sequence using sc:adversarial methodology (advocate FOR deferral, advocate AGAINST deferral, synthesis + scoring).
**Confidence Score**: 0.0 = deferral was definitely wrong (should be in sprint) → 1.0 = deferral was definitely correct (should stay deferred).

---

## SCORING RUBRIC

| Score Range | Interpretation | Recommended Action |
|-------------|---------------|-------------------|
| 0.0 – 0.25 | Deferral strongly unjustified — item should have been in sprint | Escalate to sprint amendment |
| 0.26 – 0.50 | Deferral questionable — item close to sprint threshold | Add to priority backlog with urgency flag |
| 0.51 – 0.75 | Deferral justified with minor concerns | Defer but schedule explicitly in next sprint |
| 0.76 – 1.00 | Deferral clearly correct | Maintain deferral; revisit per planned timeline |

---

## CONFIDENCE MATRIX

| # | Deferred Item | Category | Problem It Solves | Deferral Reason (from spec) | Debate Outcome Summary | Deferral Confidence (0–1) | Risk If Kept Deferred | Risk If Included Now | Recommendation | Debate Agent |
|---|--------------|----------|------------------|----------------------------|----------------------|--------------------------|----------------------|---------------------|----------------|--------------|
| 1 | **RC3+S03: Agent Dispatch Convention (full pair)** | Architecture | No binding between skill invocations and agent definitions; wrong agent (system-architect) selected instead of debate-orchestrator | Combined score 0.728 below threshold; latent defect that surfaces only after top 3 fixes applied | FOR wins on timing and prerequisites: S03 cannot be validated until RC1 is confirmed and Task 0.0 resolves "already running" semantics. Adding a novel untested role adoption pattern (0.65 confidence) to a SKILL.md already being modified by three epics creates unacceptable coordination complexity. AGAINST correctly notes the 0.70 probability of agent dispatch failure on first successful invocation, but this risk is manageable by immediate post-sprint sequencing rather than mid-flight addition. Score recalibration from 0.95→0.70 likelihood was methodologically correct for current failure but may systematically undervalue next-failure probability. | 0.71 | MEDIUM-HIGH — After sprint applies, first successful sc:adversarial invocation likely surfaces RC3 (0.70 probability). Users may see invocation appear to succeed while pipeline internally selects wrong agents, producing degraded output with no diagnostic signal — potentially more confusing than the original failure. | MEDIUM — Coordination risk: S03 edits sc:adversarial SKILL.md while Epic 1/2 also modify it; role adoption pattern is architecturally untested and architecturally inconsistent (frontmatter on debate-orchestrator implies dual-invocation mode not yet resolved); integration complexity on the sprint's most contended file. | NEXT-SPRINT | Agent 1 |
| 2 | **RC5+S05: Claude Behavioral Fallback (full, unabsorbed portion)** | Resilience | Probe-and-branch fails to classify all error types; fallback quality gap (60-70% vs 100%); quality gate not implemented | Combined score 0.761 below threshold; partially absorbed into F1-F5 fallback in Task 1.4 | Cases nearly balanced (gap from threshold: 0.015). FOR wins on probe-and-branch: Task 0.0 results are prerequisite — "already running" semantics determine whether probe-and-branch is binary or multi-path. AGAINST wins on quality gate: the two-tier gate is the highest-value residual component (~50 lines additive), directly prevents original failure recurrence in timeout/context-exhaustion scenarios the return contract cannot catch, and was rated Priority 1 by spec panel. The deferral treated probe-and-branch and quality gate as a single unit; this was an over-bundling error. The fallback mechanism was absorbed but the verification layer was not — these are separable concerns with different prerequisite states. | 0.57 | MEDIUM — Without quality gate, sprint's only protection against silent adversarial failure is return-contract.yaml status field, which itself may not be written under timeout/context-exhaustion (HIGH-rated failure modes in gap analysis). Original failure mode (adversarial requested, nothing executed, no signal) can recur under these conditions. | LOW-MEDIUM — Quality gate alone is additive to adversarial-integration.md (50 lines), no coordination hazard, directly implements spec panel Priority 1 recommendation. Probe-and-branch correctly waits for Task 0.0. Risk arises only if both components implemented together, forcing Wave 2 step 3 rewrite coordination. | ESCALATE (quality gate Tier 1); DEFER (probe-and-branch) | Agent 1 |
| 3 | **Two-tier quality gate for S05** (Tier 1: artifact existence + Tier 2: structural consistency) | Quality | No post-adversarial validation; agent success cannot be distinguished from catastrophic failure without artifact checks | S05 fully deferred; quality gate is part of S05 | AGAINST wins for Tier 1, FOR wins for Tier 2. The bundled deferral conflated two components with different prerequisite states. Tier 1 (artifact existence checks: do variant files, diff-analysis.md, base-selection.md, merged output exist?) has complete specification in solution-05 Change 2, is purely additive to adversarial-integration.md, uses path variables already defined in Task 1.4, and is the only mechanism that validates pipeline execution without trusting Claude's self-report — critical for timeout/context-exhaustion scenarios. Tier 2 (structural consistency: content criteria per artifact) legitimately requires empirical artifact data from at least one real invocation before structure can be specified; deferral of Tier 2 is clearly correct. The deferral as a unit was a classification error: Tier 1 should have been included or escalated; Tier 2 correctly waits. | 0.48 | MEDIUM-HIGH — Without Tier 1 existence checks, the sprint creates invocation mechanics without deterministic verification. In timeout/context-exhaustion scenarios the return contract may not be written, the missing-file guard treats this as partial/convergence 0.0, and the system proceeds silently — reproducing the original failure pattern under new conditions. | LOW — Tier 1 is 50 additive lines in adversarial-integration.md using path variables from Task 1.4. The staleness risk (paths changing during implementation) is mitigated by using variable-form references rather than hardcoded literals. Tier 2 remains deferred. | ESCALATE (Tier 1); DEFER (Tier 2) | Agent 1 |
| 4 | **S03 Change 1: Three-Pattern Agent Taxonomy Documentation** (role adoption, sub-agent dispatch, dynamic agents) | Documentation | Lack of framework documentation for how agents are dispatched vs. adopted as roles; future skills have no pattern to follow | S03 fully deferred | FOR wins on timing: documenting an untested role adoption pattern (0.65 residual risk) risks standardizing an unvalidated convention. AGAINST correctly notes the deferral conflates a 30-minute docs task with higher-risk S03 changes. Deferral justified but this should be the first follow-up sprint item after end-to-end testing validates the role adoption pattern. | 0.72 | MEDIUM — Future skill authors have no dispatch-vs-adopt-vs-dynamic guidance; risk of repeating the RC3 category of architectural ambiguity in every new Task-agent skill added to the framework. | MEDIUM — Documents a pattern (role adoption) with 0.65 residual confidence before empirical validation; if role adoption fails in E2E testing, the taxonomy needs immediate revision. | NEXT-SPRINT | Agent 2 |
| 5 | **S03 Change 2: `agent_bootstrap:` Field in task_dispatch_config** | Configuration | sc:adversarial task_dispatch_config lacks explicit agent bootstrap step; debate-orchestrator never formally loaded | S03 fully deferred | Deferral justified on sequencing: agent_bootstrap config is irrelevant until Fix 1 restores invocability. AGAINST correctly notes the dead subagent_type field is actively misleading, effort is minimal, and sc:adversarial SKILL.md is already being modified by Epic 3 Task 3.1. Close debate — deferral holds on dependency grounds but the item should be the second follow-up sprint item. | 0.63 | MEDIUM — After Fix 1 applies, merge-executor is dispatched without its behavioral contract; plan fidelity and provenance tracking requirements silently absent from the Task agent. | LOW-MEDIUM — Targeted YAML edit to a file already modified by Epic 3; coordination risk is the only concern and is manageable if assigned to the same author. | NEXT-SPRINT | Agent 2 |
| 6 | **S03 Change 3: Remove Dead `subagent_type` Fields from sc:adversarial YAML Blocks** | Dead Code | `subagent_type: "general-purpose"` in task_dispatch_config is not a valid Task tool parameter; dead metadata creates confusion | S03 fully deferred | AGAINST wins: removing two dead `subagent_type` lines is a 5-minute edit with zero functional dependencies, zero behavioral uncertainty, and the file is already being modified by Epic 3. Bundling this cleanup with higher-risk S03 changes was a classification error. This is the weakest deferral of the three Item 4-6 decisions. | 0.38 | MEDIUM — Every developer engaging with sc:adversarial post-Fix 1 encounters a dead `subagent_type: "general-purpose"` field and may infer it is functional, creating debugging tax and risk of the dead pattern being copied into new skills. | LOW — Two line deletions in a file already being edited; no behavioral change; no coordination overhead if appended to Task 3.1. | ESCALATE | Agent 2 |
| 7 | **S03 Change 4: Add Frontmatter to debate-orchestrator.md** (tools, model, maxTurns, permissionMode) | Configuration | debate-orchestrator.md has no frontmatter; cannot be loaded as a proper agent with defined capabilities | S03 fully deferred | FOR wins on S03 coherence: the four missing fields (tools, model, maxTurns, permissionMode) only have operational meaning after agent_bootstrap: convention (Change 2) is established. Adding them now produces aspirational metadata with no consumption mechanism. AGAINST correctly notes the `model` field has practical dispatch value (opus vs. degraded model), but the Task tool dispatches by name not by reading frontmatter fields. Deferral is correct but the `model` quality risk warrants early scheduling in the next sprint. NOTE: both agents already have partial frontmatter (name, description, category); the problem statement slightly overstates the gap. | 0.62 | MEDIUM — After primary fixes land, adversarial pipeline may run on a non-preferred model if the dispatch system does not read prose model preferences. Quality degradation risk, not a correctness failure. | LOW — Purely additive 4-field frontmatter addition with no blast radius; risk is only that it becomes orphaned metadata if Change 2 (agent_bootstrap:) is not implemented concurrently. | NEXT-SPRINT (schedule early, pair with S03 Change 2) | Agent 3 |
| 8 | **S03 Change 5: Add Frontmatter to merge-executor.md** | Configuration | merge-executor.md has no frontmatter; cannot be loaded as a proper agent with defined capabilities | S03 fully deferred | FOR wins: merge-executor is one call-chain step deeper than debate-orchestrator; the full dependency sequence is RC1+S01 (invocation restored) → debate-orchestrator loaded → merge-executor dispatched. Frontmatter fields on merge-executor have zero operational value until both preceding steps are verified working. AGAINST's model-quality argument is valid (opus vs. haiku matters for plan fidelity in merge tasks) but is outweighed by dependency sequencing. Deferral is more comfortable here than Item 7 due to deeper call-chain position. NOTE: merge-executor.md already has partial frontmatter (name, description, category); problem statement is inaccurate on the "no frontmatter" claim. | 0.65 | MEDIUM — merge-executor handles precision document integration; running on an under-resourced model degrades merge quality (plan fidelity, provenance tracking accuracy). But this is a quality-of-output risk, not a pipeline-correctness risk — the pipeline still completes. | LOW — Same 4-field additive change as Item 7; no blast radius. Slightly higher comfort deferring because it's deeper in the dispatch chain and even more dependent on Change 2 being in place first. | NEXT-SPRINT (after debate-orchestrator Change 4 and agent_bootstrap: convention established) | Agent 3 |
| 9 | **S03 Change 6: Update agents/README.md** (30 agents exist, README lists 3) | Documentation | README documents only 3 of 30 agents; Claude cannot discover debate-orchestrator or merge-executor via README; creates silent dispatch failures | S03 fully deferred | AGAINST makes the strongest case of the three items: the README contains an actively misleading instruction pointing to `plugins/superclaude/agents/` which does not exist in the current architecture, and the agent count is wrong by 24 (lists 3, actual count is 27 .md files). The "silent dispatch failures" claim is overstated — Claude discovers agents by directory scan, not README lookup — but the wrong `plugins/` path instruction can cause real developer errors. FOR correctly notes sprint independence (no epic consults README), but the misleading content is a developer experience bug distinct from the S03 scope. Deferral is technically justified but sits at the low end of the "defer with concern" band. | 0.58 | MEDIUM — README's wrong `plugins/superclaude/agents/` instruction will mislead developers making agent edits, causing the very src/vs-.claude/ sync divergence the project tries to prevent. Compounds at 27:3 ratio as system grows. | LOW — Purely additive documentation; zero blast radius on any functional code. The fix takes under 15 minutes. The only risk is briefly documenting agents whose dispatch convention (S03 Changes 1-3) is still being established, but listing them by name is not the same as documenting their dispatch convention. | NEXT-SPRINT (note: the `plugins/` path error is an active developer hazard independent of S03 scope; recommend fixing that instruction as routine maintenance even before the S03 sprint) | Agent 3 |
| 10 | **DVL `verify_pipeline_completeness.sh`** | Verification | No programmatic check that all expected adversarial pipeline artifacts exist; catches partial execution silently | Only useful post-end-to-end test; sprint-critical path doesn't need it yet | FOR wins: script has zero utility during the 3-epic implementation phase (no pipeline runs occur during sprint). Script requires `--agents` flag input to determine expected variant count, which is undefined without a working E2E invocation. Verification Test 5 is explicitly "Post-Sprint, Manual" with an enumerated checklist (items 1-5) that covers the same ground without automation. AGAINST correctly identifies that E2E Test 5 without this script is prone to human oversight (miscounted variants, missed scoring-matrix.md), and that the original silent-degradation failure mode persists until the script exists. However, the Test 5 checklist is explicit and bounded; manual verification is sufficient for a single post-sprint validation event. | 0.79 | LOW-MEDIUM — E2E Test 5 relies on manual artifact checklist; silent partial-pipeline execution is undetectable programmatically until script is built. Risk is bounded by Test 5's explicit human checklist and the low frequency of post-sprint E2E test events. | LOW — No sprint-phase utility until E2E testing begins; minor scope expansion with deferred payoff; adding a fourth DVL script to a sprint already including three is unwarranted scope creep. | MAINTAIN DEFERRAL — implement as Day-1 post-E2E item, concurrent with the first successful pipeline run that produces artifacts to check against; do not defer to a separate multi-month backlog | Agent 4 |
| 11 | **DVL `dependency_gate.sh`** | Verification | No pre-task gate verifying blocking task outputs exist before next task starts; dependency ordering relies on human management | Overkill for 3 epics with clear ordering; human-managed | FOR wins, strengthened by a structural mismatch argument: the script is designed to check new file creation at dependency boundaries, but this sprint's dependency boundaries are edit milestones within pre-existing files. The relevant SKILL.md files exist before any sprint work begins, so a file-existence gate would trivially pass on every check, providing no enforcement against the actual coordination hazard (Risk R5: concurrent Wave 2 step 3 edits). The sprint-spec's single-author constraint is the correct and sufficient mitigation for R5. AGAINST correctly identifies Risk R5 as real but overestimates what a file-existence gate can prevent: it cannot detect premature conceptual start of Task 2.2 before Tasks 1.3/1.4 are finalized. | 0.83 | LOW — 3-epic ordering is clear and documented; single-author constraint (explicitly specified in sprint-spec) mitigates the primary concurrent-modification risk. Human ordering error risk is low given the 3-node sequential dependency graph. | LOW-MEDIUM — Script as brainstormed (file-existence checks) does not match the sprint's edit-centric dependency model and would require rethinking what "dependency satisfied" means for workflows that modify existing files rather than creating new ones; risk of false-pass scenarios that provide false confidence. | MAINTAIN DEFERRAL — redesign for edit-centric dependency tracking before inclusion in follow-up sprint; current design assumes artifact-creation workflow and is structurally mismatched to this sprint | Agent 4 |
| 12 | **DVL `check_file_references.py`** | Verification | File path references in markdown may point to non-existent files; hallucinated paths are undetected | Useful for general quality but not sprint-critical path | Balanced debate; moderate concern. FOR: sprint deliverables are implementer-written edits from explicit spec acceptance criteria — cross-reference path strings in Tasks 3.3 and 3.4 are specified verbatim in the spec, making hallucination risk for a human implementer substantially lower than for agents generating analysis from memory. Implementation complexity is non-trivial: template placeholders (`<output-dir>/...`) are valid documentation conventions that must not be flagged as invalid references; sc:skill vs. sc-skill naming conventions require careful handling. AGAINST: agent-written adversarial pipeline output documents (produced after E2E testing begins) are exactly the class where hallucinated paths occur with highest frequency; the cross-reference comments in Tasks 3.3/3.4 are path strings that must be correct; the dual-role nature of adversarial-integration.md (both referenced and a reference document itself) creates cross-reference complexity. The deferral is accurate but the script's peak value window arrives with the first E2E test — not in a separate future sprint. | 0.73 | MEDIUM — Agent-written adversarial pipeline artifacts (post-E2E) will contain file path references that are unvalidated without this script; manual verification of reference correctness in generated documents is error-prone at scale. The cross-reference comments added in Tasks 3.3/3.4 are lower risk (implementer-written from spec) but not zero risk. | LOW-MEDIUM — Template placeholder handling and naming convention edge cases require non-trivial regex design; risk of false positives against valid `<output-dir>/...` template paths requires careful implementation to avoid producing noise. | DEFER WITH CONCERN — schedule for follow-up sprint immediately after `validate_return_contract.py` and `verify_allowed_tools.py`; implement before the first E2E test produces agent-written artifacts that could contain hallucinated paths | Agent 4 |
| 13 | **DVL `generate_checkpoint.py`** | Verification | Checkpoint files are written by agents (not programmatically); agent-written checkpoints can be fabricated or incorrect | Workflow improvement, not the pipeline fix itself | FOR wins clearly: script is Tier 3 cross-phase, architecturally depends on Tier 2 scripts (calls `validate_return_contract.py` and `verify_numeric_scores.py` inline), adds ~150 lines of scope, and has zero bearing on sprint goals (wiring, spec rewrite, return contract). AGAINST makes a philosophically valid point — agent-written checkpoints exhibit the same self-report problem the sprint targets — but sprint checkpoints are process documentation, not acceptance criteria. Sprint deliverables are verifiable via grep/file inspection without trusting checkpoint content. The epistemic irony (fixing agent self-report failures via agent-written checkpoints) is real but appropriately addressed in v2.1, not as a sprint amendment. | 0.82 | LOW-MEDIUM — Agent-written checkpoints continue unverified; cross-sprint epistemic trust degrades weakly; most damaging if future sprints rely on checkpoint content as evidence rather than as process notes. No operational pipeline impact. | MEDIUM — Adds ~150 line script with inline DVL dependencies on Tier 2 scripts not yet implemented; creates dependency chain (cannot ship before `validate_return_contract.py`); checkpoint format may be stale if pipeline design evolves during Epic 1-3 implementation. | NEXT-SPRINT (v2.1, implement as first deliverable before that sprint's own checkpoints are written; pair with `verify_allowed_tools.py` and `validate_return_contract.py`) | Agent 5 |
| 14 | **Framework-level Skill Return Protocol** (`<skill-output-dir>/.return-contract.yaml` standard) | Architecture | Sprint fix is sc:adversarial-specific; no general convention for skill-to-skill return contracts across SuperClaude | Long-term systemic fix; this sprint is tactical | FOR wins on premature standardization risk: with only one skill pair (sc:roadmap→sc:adversarial) as evidence, a framework standard risks encoding sc:adversarial-specific fields (convergence_score, base_variant, fallback_mode) as mandatory framework requirements. AGAINST correctly identifies the "de facto standard" risk — other skill authors will copy the `adversarial/` subdirectory path pattern — but this is addressable by adding a "not prescriptive for other skills" note to Epic 3 documentation (two sentences, not a framework redesign). Standardizing from a single data point before common schema subsets are understood imposes governance cost on all future skills prematurely. | 0.85 | LOW-MEDIUM — De facto standard risk: next skill attempting skill-to-skill invocation may copy the sc:adversarial path convention including `adversarial/` subdirectory name, propagating an sc:adversarial-specific component to other contexts. Fully mitigated by adding "not prescriptive" clarification note to Epic 3 documentation as a minor sprint amendment. | MEDIUM-HIGH — Premature standardization with insufficient evidence (one data point); 9 sc:adversarial-specific fields may become mandatory framework fields; schema governance cost (versioning, enforcement, evolution) imposed on all future skills before other use cases are understood. | BACKLOG (v2.1 or dedicated framework sprint after 2-3 more skill pairs implement return contracts; add "not prescriptive" clarification to sc:adversarial Epic 3 as minor amendment to current sprint) | Agent 5 |
| 15 | **Agent Registry (`refs/agent-registry.md`)** mapping delegation roles to agent files | Documentation/Config | No lookup mechanism for skill→agent mapping; Claude must infer from prose description which agent to dispatch | S03 Option C; premature until S03 convention is established | AGAINST makes the strongest case of the three items: registry is pure documentation (no code, no behavioral risk), the 30-agents/3-in-README gap is documented and compounds, and the change is purely additive. FOR correctly identifies the sequencing dependency: the registry documents the skill→agent relationship whose semantics are defined by S03's bootstrap convention; creating a registry before S03 ships documents a broken state (passive .md files with no functional frontmatter = a lookup mechanism to unfunctional agents). AGAINST's argument that Change 6 could be extracted from S03 is valid, but time-value gain is zero since S03 ships in the next sprint anyway. FOR wins on sequencing; AGAINST wins on the discoverability concern. Deferral is at the high end of "defer with concern." | 0.73 | MEDIUM — 30-agent discoverability problem persists; Claude continues to infer agent names heuristically; each new skill using Task agents adds another undocumented entry; the 27:3 gap compounds. Without a registry, S03's bootstrap convention (when implemented) lacks a reliable agent discovery mechanism. | LOW-MEDIUM — Registry documents agents without functional frontmatter (passive files before S03 ships); creates false assurance that agent discovery is solved before dispatch convention exists; requires immediate revision when S03 Changes 4-5 add frontmatter to each agent. | NEXT-SPRINT (first deliverable of S03 sprint: create registry listing all 30 agents with .md paths, then add frontmatter to agents (Changes 4-5), then document bootstrap convention; registry becomes immediately useful as each agent gains functional frontmatter in sequence) | Agent 5 |
| 16 | **Framework-level Agent Dispatch (TypeScript v5.0)** | Architecture | No programmatic agent dispatch system; all agent loading relies on Claude reading markdown prose instructions | Long-term; requires TypeScript plugin system not yet built | FOR wins decisively. TypeScript plugin system does not exist; sprint is markdown-only; S03 is the appropriate near-term RC3 surrogate. No scenario exists where including this now benefits the sprint. The item is an architectural evolution that makes S03 obsolete eventually but cannot substitute for S03 in the near term. | 0.97 | LOW — S03 (Items 4-6 in this matrix) addresses the immediate RC3 manifestation without TypeScript infrastructure; TypeScript v5.0 is a long-term framework evolution that does not block current usage. | CRITICAL — Would require designing and building a TypeScript plugin system from scratch; entirely outside current framework constraints; blast radius is system-wide affecting every skill and agent in the framework. | MAINTAIN DEFERRAL — Revisit when TypeScript v5.0 roadmap is active; S03 is the correct near-term RC3 remedy. | Agent 6 |
| 17 | **Concurrency namespacing for parallel sc:adversarial invocations** | Architecture | Multiple simultaneous sc:adversarial invocations could write to same return-contract.yaml path, causing race conditions | Not a primary concern for sequential invocation; edge case | FOR wins on timing grounds. Race condition requires three simultaneous preconditions: functional pipeline (not yet achieved), concurrent invocations (not yet a documented use case), and shared output directory (partially mitigated by caller-controlled --output-dir parameter). AGAINST correctly identifies the failure mode as non-benign but the three-way precondition makes current risk low. Key finding: Item 17 becomes a required co-dependency if Item 14 (Framework-level Skill Return Protocol) is adopted, because that item makes the output-dir path implicit rather than caller-controlled. | 0.82 | LOW-MEDIUM — Risk materializes if/when CI/CD automation adopts sc:roadmap with implicit paths, or if Item 14 (Framework-level Skill Return Protocol) is adopted, which would eliminate the caller-controlled --output-dir mitigation. | LOW-MEDIUM — Design effort manageable (~2-3 hours) but misorders the work before the pipeline is functional; Epic 3 path conventions may change in the next sprint, making any namespacing scheme built now potentially obsolete. | DEFER WITH CONCERN — Record in backlog as "Item 17 is a dependent risk of Item 14"; must be resolved in the same sprint as Item 14 if that item is adopted. | Agent 6 |
| 18 | **Debt register / follow-up sprint tracking mechanism** | Process | No formal mechanism to track deferred items (RC3/RC5) across sprints; deferral may be forgotten or re-analyzed from scratch | Meta-process improvement, not a code fix | Close debate — FOR wins on sprint-scope grounds (not a code fix; gap analysis and this confidence matrix provide adequate point-in-time tracking). AGAINST correctly notes these are point-in-time artifacts without persistence conventions or sprint-to-sprint update obligations; rediscovering 18 deferred items costs 2-4 hours per future sprint. Key finding: this confidence matrix is functionally an ad-hoc debt register already, but without a formal template, designated storage location, or update convention, it does not obligate future sprints to reference it. | 0.55 | MEDIUM — Without a formal debt register, deferred items (RC3/RC5 and 16 others) risk being forgotten, rediscovered at cost, or re-analyzed from scratch by v2.1 sprint team with no access to this sprint's recalibration decisions (e.g., RC3 likelihood reduction from 0.95 to 0.70 with documented rationale). | LOW — A structured debt-register.md with 5-10 fields per item in .dev/releases/ is a ~30-minute documentation task with zero blast radius on any functional code. | DEFER WITH CONCERN — Elevate to first item on v2.1 sprint's process deliverables list; initialize using this confidence matrix as the source before any v2.1 implementation work begins. | Agent 6 |

---

## DEBATE TRANSCRIPTS

*Each agent's detailed debate transcript is appended below as it completes.*

---

### AGENT 1 TRANSCRIPT — Items 1, 2, 3

*Agent: claude-sonnet-4-6. Inputs: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md, debate-03-agent-dispatch.md, debate-05-claude-behavior.md, solution-03-agent-dispatch.md, solution-05-claude-behavior.md. Date: 2026-02-23.*

---

#### DEBATE 1: RC3+S03 — Agent Dispatch Convention (Full Pair)

**Combined score**: 0.728. Classified as latent defect surfacing only after top 3 fixes applied.

---

##### FOR DEFERRAL — Steelman Case

**Why is NOW the wrong time?**

RC3 is explicitly classified in ranked-root-causes.md as a latent defect with zero causal contribution to the observed failure. The dependency chain is unambiguous: RC1 blocks invocation, RC5 is the downstream behavioral consequence, RC3 is a second-order latent defect within sc:adversarial's internal dispatch. As of this sprint, sc:adversarial is not yet being invoked at all. Fixing the internal dispatch mechanism of a system that cannot be reached is technically correct work that cannot be validated and provides no observable improvement to the reported failure.

The sprint's three epics establish the invocation foundation (RC1+S01), the specification clarity (RC2+S02), and the return contract transport (RC4+S04). Until these are complete and end-to-end tested, RC3 cannot even be exercised. There is no code path in any current sprint deliverable that touches the debate-orchestrator agent dispatch. The fix has zero observable effect in isolation — solution-03 itself acknowledges this: "Fix 1 MUST be applied before this solution has any observable effect."

**What must be true first?**

At minimum: (1) RC1 must be fixed and validated; (2) Task 0.0 probe must confirm whether cross-skill invocation is viable or fallback-only; (3) at least one end-to-end invocation of sc:adversarial via the new wiring must be attempted so the actual agent dispatch failure surface can be observed empirically.

Without these prerequisites, S03's implementation is purely speculative. The solution's core execution mechanism (MANDATORY read instruction for role adoption) has only 0.65 residual risk confidence — a problem that can only be properly understood after the invocation chain is working.

**What is the blast radius risk if included now?**

S03 modifies sc:adversarial SKILL.md (bootstrap section + dispatch config changes). This is the same 1747-line document that Epic 1 tasks 1.3/1.4 and Epic 2 task 2.2 all modify. The sprint spec flags this with a "Critical coordination" note requiring single-author atomic rewrites. Adding S03's bootstrap section creates a four-way conflict on overlapping sections of the same document.

Debate-03 identifies an unresolved architectural inconsistency: Change 4 adds Task-agent frontmatter to debate-orchestrator.md while Change 1 states the orchestrator is adopted by role (not spawned as a Task). This inconsistency would need resolution before implementation — adding an unresolved architectural question to a file being rewritten by three concurrent epics is a substantial integration hazard.

**Does the sprint work without it?**

Yes, entirely. The sprint's definition of done has no dependency on any S03 change. The F1-F5 fallback protocol handles the degraded invocation path through inline Task agents without requiring the bootstrap convention.

---

##### AGAINST DEFERRAL — Steelman Case

**What specific failure mode does deferral enable?**

Once RC1+S01 is successfully applied and sc:adversarial becomes invocable, the next observable failure in the chain will be RC3: Claude enters sc:adversarial's SKILL.md without reading debate-orchestrator.md, selects agents based on whatever heuristic it applies from 1747 lines of prose, and likely selects the wrong agent type. RC3's original self-reported likelihood was 0.95 before cross-validation recalibration to 0.70. A 0.70 probability of agent dispatch failure is a likely outcome on the first successful post-sprint invocation.

The failure mode produces a symptom worse than the original: invocation appears to succeed (RC1 fixed) but pipeline quality is still degraded (RC3 not fixed). Users activating --multi-roadmap after the sprint see an apparently successful run with degraded output and no diagnostic signal.

**How close to the sprint threshold?**

RC3+S03 scored 0.728. The gap analysis identifies that the score recalibration from 0.95 to 0.70 likelihood was the decisive factor: "If the self-reported 0.95 had been accepted, RC3 would have scored 0.870 and ranked second — it would have been in the sprint." The recalibration methodology was sound for assessing contribution to the current failure, but may systematically undervalue the likelihood of the NEXT failure once prerequisites are met.

**Actual effort vs. risk of not implementing?**

S03's six changes are all markdown edits — no executable code is modified. Implementation is approximately 2-3 hours if the three conditions from debate-03 Fix Likelihood are pre-resolved. Against this, the risk is a 0.70-probability agent dispatch failure on the first post-sprint invocation — appearing as a successful invocation producing degraded output, more confusing to diagnose than a clean failure.

**Incorrect assumptions behind deferral?**

The recalibration methodology adjusts for "causal contribution to the current failure" but does not restore credit for "causal contribution to the next failure." The deferral rested on the recalibrated score which may not accurately represent post-sprint urgency.

---

##### SYNTHESIS: ITEM 1

**Which side is stronger?** FOR DEFERRAL, but narrowly and contingently.

Decisive arguments: (1) genuine lack of prerequisites — S03 cannot be validated until RC1 is confirmed working and Task 0.0 resolves Skill tool semantics; (2) coordination risk on sc:adversarial SKILL.md with three concurrent epic modifications; (3) the role adoption pattern is novel, untested, and architecturally inconsistent in current solution documents.

Key insight: Task 0.0 results will directly determine whether the role adoption architecture is viable at all. Building S03 before Task 0.0 resolves the "already running" constraint risks building the wrong architectural model.

**Deferral Confidence Score: 0.71** — Justified with concerns. Correct decision given dependency chain and coordination risks, but RC3 will become active immediately after the sprint is applied.

**Risk if kept deferred**: MEDIUM-HIGH — 0.70 probability of agent dispatch failure on first successful invocation. Users may observe invocation appear to succeed while pipeline internally selects wrong agents, creating a confusing "it ran but it's wrong" failure mode with no diagnostic signal.

**Risk if included now**: MEDIUM — sc:adversarial SKILL.md coordination across four concurrent modification sources; unresolved frontmatter/role-adoption inconsistency requires architectural resolution; role adoption pattern has no empirical validation.

**Recommendation: NEXT-SPRINT** — Priority backlog item. Implement after Task 0.0 results are documented and after first post-sprint end-to-end invocation confirms primary path works.

---

#### DEBATE 2: RC5+S05 — Claude Behavioral Fallback (Full, Unabsorbed Portion)

**Item scope**: Remaining unimplemented after F1-F5 fallback absorption into Task 1.4 and `fallback_mode` absorption into Tasks 3.1/3.2: (a) probe-and-branch invocation pattern, (b) two-tier quality gate, (c) "No Adversarial Output Gate" abort path.

---

##### FOR DEFERRAL — Steelman Case

**Why is NOW the wrong time?**

The core value of S05 has been absorbed. Task 1.4 implements the F1-F5 fallback state machine — the gap analysis explicitly states this was "essentially S05's probe-and-branch strategy operationalized." Tasks 3.1/3.2 implement `fallback_mode` routing with differentiated user warnings.

What remains is the verification layer. The probe-and-branch specifically depends on Skill tool behavior currently unknown: Task 0.0's decision gate outcomes could fundamentally change whether probe-and-branch is binary or multi-path. If the "already running" constraint means the primary path never works, the probe becomes a fixed-path trigger rather than a dynamic branching mechanism — the entire design changes.

The quality gate requires artifact paths to be stable. These are being established during this sprint. Implementing the gate before paths are stable creates specification staleness risk.

**What must be true first?**

Three preconditions: (1) Task 0.0 must determine Skill tool semantics; (2) F1-F5 artifact output paths must be confirmed stable; (3) at least one test invocation must produce representative artifacts so structural checks have empirical basis.

**Blast radius risk if included now?**

Solution-05 Change 3 modifies Wave 2 step 3 — the sprint spec's most contended text, already requiring a single-author atomic rewrite integrating Epic 1 tasks 1.3/1.4 and Epic 2 task 2.2. Adding S05 quality gate language increases complexity of an already multi-requirement rewrite.

**Does the sprint work without it?**

Yes, with a known gap. The sprint provides the fallback mechanism and return contract transport, but lacks systematic quality gate validation.

---

##### AGAINST DEFERRAL — Steelman Case

**What specific failure mode does deferral enable?**

Without the quality gate, the sprint creates an invocation chain with a single validation point: the return-contract.yaml status field. In the two highest-rated failure modes (execution timeout, context window exhaustion — both HIGH risk), the return contract may NOT be written. The missing-file guard in Task 3.2 treats this as status: partial with convergence 0.0 and proceeds. The original failure mode — adversarial requested, nothing executed, no meaningful signal — can recur under these conditions.

**How close to the sprint threshold?**

RC5+S05 scored 0.761 vs. the 3rd-place RC2+S02 at 0.776. The gap is 0.015 — the smallest margin in the ranking. A change of less than 2% in any component score would have included S05 in the sprint. The quality gate is the highest-value residual component and has different prerequisite states from the probe-and-branch. These were over-bundled into a single deferral.

**Actual effort for the unabsorbed portion?**

Two-tier quality gate: approximately 50-70 additive lines in adversarial-integration.md. Probe-and-branch simplified to binary outcome: approximately 15 lines. Total approximately 2-3 hours of markdown editing.

**Incorrect assumptions behind deferral?**

The deferral treated the quality gate and probe-and-branch as a single unit. These have different prerequisite states: the quality gate can be specified now, while the probe-and-branch correctly waits for Task 0.0. The bundled deferral incorrectly applied probe-and-branch prerequisite logic to the quality gate component.

---

##### SYNTHESIS: ITEM 2

**Which side is stronger?** Nearly balanced (0.015 gap from threshold).

FOR DEFERRAL wins on probe-and-branch: Task 0.0 results are a genuine prerequisite. AGAINST DEFERRAL wins on quality gate: highest-value residual component (~50 additive lines), directly prevents original failure recurrence in timeout/context-exhaustion scenarios the return contract cannot catch, and was rated Priority 1 by spec panel. The deferral was over-bundling: probe-and-branch and quality gate have different prerequisite states and should have been separated.

**Deferral Confidence Score: 0.57** — Justified with concerns (lower end of range). The score lands at the high end of "defer but schedule explicitly in next sprint" because the peak value window (E2E testing) may arrive before the "next sprint" does.

**Risk if kept deferred**: MEDIUM — In timeout/context-exhaustion scenarios, return contract may not be written. Missing-file guard treats this as partial/convergence 0.0. System proceeds as if degraded-but-partial when it is actually a complete failure.

**Risk if included now**: LOW-MEDIUM — Quality gate alone is additive to adversarial-integration.md with no coordination hazard. Risk arises only if probe-and-branch also included, forcing Wave 2 step 3 rewrite coordination.

**Recommendation: ESCALATE (quality gate Tier 1); DEFER (probe-and-branch)** — The two-tier quality gate artifact existence checks should be added to the sprint or as an immediate post-sprint amendment. Spec panel rated this Priority 1 at approximately 50 additive lines cost. Probe-and-branch remains deferred until Task 0.0 resolves Skill tool semantics.

---

#### DEBATE 3: Two-Tier Quality Gate for S05 (Tier 1: Artifact Existence + Tier 2: Structural Consistency)

**Item scope**: Post-adversarial validation mechanism deferred with S05. Tier 1 checks artifact existence. Tier 2 checks structural consistency (content criteria per artifact).

---

##### FOR DEFERRAL — Steelman Case

**Why is NOW the wrong time?**

The gate validates artifacts that do not yet exist in validated form. Artifact paths and content structure are being defined throughout the sprint. A quality gate hardcoding specific artifact names against paths defined in Task 1.4 creates tight coupling to in-flight deliverables. If any path changes during implementation, the gate breaks silently.

Tier 2 (structural consistency) has a more fundamental problem: content criteria can only be specified after at least one real invocation produces representative artifacts. We cannot specify structural checks for artifacts that have never been produced.

The spec panel's Priority 1 recommendations (YAML parse error handling, output path invariant) cover the most critical quality assurance gaps at near-zero implementation cost without requiring artifact stabilization.

**What must be true first?**

For Tier 1: artifact output paths from Task 1.4 must be final. For Tier 2: at least one successful end-to-end invocation must produce representative artifacts.

**Does the sprint work without it?**

Yes. The return-contract.yaml status field routing provides the primary validation signal.

---

##### AGAINST DEFERRAL — Steelman Case

**What specific failure mode does deferral enable?**

Without Tier 1 artifact existence checks, the system has a single validation point: the return-contract.yaml status field. In the two highest-rated failure modes (execution timeout, context window exhaustion — both HIGH risk), the return contract may not be written at all. The missing-file guard treats the absent contract as status: partial with convergence 0.0 and proceeds. The original failure mode — adversarial requested, nothing executed, no meaningful signal — can recur under these conditions.

**How close to the sprint threshold?**

Sub-component of S05 (0.761). The gap analysis Priority 2 section explicitly states: "The two-tier gate provides verification without requiring behavioral compliance. It doesn't rely on Claude reporting correctly — it checks artifacts programmatically." This is the only proposed mechanism that validates by checking what was actually produced.

**Actual effort?**

Tier 1: approximately 50 additive lines in adversarial-integration.md using path variables from Task 1.4. Tier 1 alone delivers the majority of gate value and can be implemented independently.

**Incorrect assumptions behind deferral?**

The deferral rationale was "S05 fully deferred; quality gate is part of S05" — a bundling assumption. The gate has no dependency on probe-and-branch or fallback protocol portions of S05. Tier 1 specifically has no dependency on empirical artifact data. The bundled deferral rationale does not hold for Tier 1 independently.

---

##### SYNTHESIS: ITEM 3

**Which side is stronger?** AGAINST DEFERRAL for Tier 1; FOR DEFERRAL for Tier 2.

Tier 1 (artifact existence): AGAINST wins. Approximately 50 additive lines, uses path variables from Task 1.4, requires no empirical artifact data, and directly catches the highest-rated failure modes (timeout, context exhaustion) that the return contract cannot catch. The staleness risk is mitigated by variable-form path references.

Tier 2 (structural consistency): FOR wins. Content criteria cannot be meaningfully specified without empirical artifact data from at least one real invocation.

The bundled deferral was an administrative simplification that correctly deferred Tier 2 and incorrectly deferred Tier 1.

**Deferral Confidence Score: 0.48** — Questionable deferral (lower end of 0.26-0.50 range). Split verdict: Tier 1 deferral was an error (approximately 0.25 for that component), Tier 2 deferral was correct (approximately 0.80 for that component). Composite falls at 0.48 weighted toward Tier 1 as the higher-value component.

**Risk if kept deferred**: MEDIUM-HIGH — Without Tier 1 checks, the sprint creates invocation mechanics without deterministic verification. In timeout/context-exhaustion scenarios the return contract may not be written and the system proceeds as if degraded-but-partial when it is actually a complete failure.

**Risk if included now**: LOW — Tier 1 is 50 additive lines in adversarial-integration.md using path variables from Task 1.4. Staleness risk mitigated by variable-form references. Tier 2 remains deferred.

**Recommendation: ESCALATE (Tier 1); DEFER (Tier 2)** — Tier 1 artifact existence checks should be added to the sprint or as an immediate post-sprint amendment at Priority 1 level. Tier 2 structural consistency checks should wait until at least one successful end-to-end invocation produces representative artifacts.

---

*Agent 1 transcript complete. Items 1 (RC3+S03), 2 (RC5+S05 unabsorbed), 3 (Two-tier quality gate) debated 2026-02-23.*
*Analyst: claude-sonnet-4-6.*

---

### AGENT 2 TRANSCRIPT — Items 4, 5, 6

**Analyst**: claude-sonnet-4-6 (adversarial debate agent)
**Inputs**: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md, DVL-BRAINSTORM.md
**Date**: 2026-02-23

---

#### DEBATE 1 — Item 4: S03 Change 1: Three-Pattern Agent Taxonomy Documentation

**Subject**: Three-pattern agent taxonomy documentation (role adoption, sub-agent dispatch, dynamic agents) — deferred with S03; combined score 0.728.

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The taxonomy documentation describes three agent dispatch patterns. The most novel — role adoption, where sc:adversarial reads debate-orchestrator.md and "becomes" the orchestrator — is explicitly marked in debate-03 as "untested" with a residual risk score of 0.65. Documenting this pattern as the canonical framework standard before empirical validation risks institutionalizing a convention that may need revision or abandonment after the first end-to-end test. If role adoption fails (probability approximately 30% based on the 0.65 residual confidence), the taxonomy document will require immediate revision, creating churn and confusing future skill authors who consult it during the window before correction.

The sub-agent dispatch pattern (Change 1's second pattern) depends on the `agent_bootstrap:` field being implemented (Change 2) and validated. Writing the taxonomy before the patterns it documents have been verified is documentation-first rather than evidence-first engineering.

**What must be true first before this is safe/useful to add?**

1. Fix 1 (invocation wiring) must be applied and validated so sc:adversarial can be invoked at all.
2. Task 0.0 (Skill tool probe) must confirm whether cross-skill invocation is viable or fallback-only.
3. At least one successful end-to-end test of `sc:roadmap --multi-roadmap --agents opus,haiku` must confirm that role adoption works as described — that sc:adversarial actually reads debate-orchestrator.md and exhibits the expected behavioral contract.

Only after those conditions are satisfied is the taxonomy documentation accurate rather than speculative.

**What is the blast radius risk if included in this sprint?**

The documentation itself has minimal blast radius — it modifies only agents/README.md (additive change). The risk is not in the edit mechanics but in premature standardization. A framework-level convention that documents a pattern with 0.65 residual confidence becomes a normative reference that future developers follow without questioning. When the pattern fails, they follow the documentation rather than diagnose the failure.

**Does the sprint succeed without it?**

Completely. The three epics have no dependency on the agent taxonomy documentation. The Definition of Done contains no reference to agents/README.md. The sprint ships all acceptance criteria without this change.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The absence of taxonomy documentation perpetuates the exact category of architectural ambiguity that caused RC3. The root cause analysis confirmed that sc:adversarial's broken dispatch chain exists because the author who wrote it had no framework standard to follow for when to use role adoption vs. sub-agent dispatch vs. dynamic agent templates. Without the taxonomy, the next skill that uses Task agents will face the same ambiguity and make the same class of mistakes. Deferral does not defer the cost; it defers it onto the next skill author.

**How close to the sprint threshold was this item?**

The S03 pair scored 0.728 combined, only 0.048 below the RC2+S02 cutoff of 0.776. If Change 1 were evaluated independently — stripped of higher-risk Changes 3-6 in the S03 bundle — its lower blast radius and zero behavioral uncertainty would likely produce a combined score above the S03 pair average. The bundled scoring penalized a low-risk documentation task by associating it with higher-risk structural changes.

**What is the actual effort to implement vs. the risk of not implementing?**

Change 1 is approximately 30 lines of documentation in agents/README.md describing three patterns with examples. The content already exists in solution-03 (System Design Diagram, three-pattern distinctions). This is a transcription and editorial task. Effort: 30 minutes maximum.

**Does any evidence suggest the deferral decision was based on incorrect assumptions?**

The deferral treats S03 as a monolithic unit. The gap analysis lists all S03 changes under a single row with "S03 fully deferred." This means a 30-minute documentation change (Change 1) inherited the deferral logic of the most uncertain change in the bundle (Change 2's MANDATORY read instruction with 0.65 residual confidence). The deferral decision's correctness for Change 2 does not imply correctness for Change 1.

##### SYNTHESIS + SCORING

**Which side is stronger, and why?**

The FOR side wins on the key timing argument: documenting a pattern before it is empirically validated is premature standardization. The role adoption pattern has not been tested in any end-to-end run. Writing it into a framework-level README as canonical guidance creates normative momentum for an unproven approach.

The AGAINST side's point about bundling is also valid — Change 1 specifically is pure documentation with minimal blast radius, and its deferral "by association" with higher-risk S03 changes is a real concern. However, this concern argues for scheduling Change 1 as the first follow-up sprint item (written after empirical testing), not for including it in the current sprint.

- **Deferral Confidence Score**: 0.72
- **Risk if kept deferred**: MEDIUM — Future skill authors have no dispatch-vs-adopt-vs-dynamic guidance; risk of repeating the RC3 category of architectural ambiguity in every new Task-agent skill added to the framework.
- **Risk if included now**: MEDIUM — Documents a pattern (role adoption) with 0.65 residual confidence before empirical validation; if role adoption fails in E2E testing, the taxonomy document requires immediate revision.
- **Recommendation**: NEXT-SPRINT | Write this immediately after the end-to-end test validates or revises the role adoption pattern. Do not write before the test results are known.

---

#### DEBATE 2 — Item 5: S03 Change 2: `agent_bootstrap:` Field in task_dispatch_config

**Subject**: `agent_bootstrap:` field in task_dispatch_config — sc:adversarial task_dispatch_config lacks explicit agent bootstrap; deferred with S03.

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The `agent_bootstrap:` field operates entirely within sc:adversarial's internal execution logic — it affects what happens AFTER sc:adversarial is invoked, not whether sc:adversarial is invoked. The current sprint's primary failure mode is that sc:adversarial is never reached at all (RC1). Until Fix 1 is applied and validated, no part of sc:adversarial's internal dispatch mechanism matters. Adding `agent_bootstrap:` to the task_dispatch_config of an unreachable skill is engineering a refinement before the baseline function exists.

**What must be true first?**

1. Fix 1 (Skill in allowed-tools) must be applied.
2. Task 0.0 probe must confirm the invocation path is viable.
3. sc:adversarial must be invocable — at least via the fallback path (F1-F5) if the primary path is blocked.

Only when sc:adversarial runs can dispatch quality within sc:adversarial matter. The merge executor is dispatched during Step 5 of sc:adversarial's pipeline. That step cannot be reached until the entire pipeline is invocable.

**What is the blast radius risk if included in this sprint?**

sc:adversarial SKILL.md is a 1,747-line file already being modified by Epic 3 (Task 3.1 adds the Return Contract MANDATORY section). Adding an unplanned second modification to the same file during an active sprint increases coordination overhead. The "single atomic edit" principle established for SKILL.md modifications applies — two independent authors modifying the same large file without coordination creates merge risk.

**Does the sprint succeed without it?**

Yes. The sprint's Definition of Done has no reference to agent_bootstrap: configuration. The sprint addresses the invocation chain at the level of "sc:adversarial can be reached and produces a return contract." The quality of merge executor dispatch within sc:adversarial is a second-order concern relative to first-order invocation.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

When Fix 1 is applied and sc:adversarial becomes invocable, the merge executor Task agent will be dispatched in Step 5 WITHOUT its behavioral contract. The current task_dispatch_config contains `subagent_type: "general-purpose"` — a dead field the Task tool ignores entirely. The merge executor will be dispatched with only the inline SKILL.md prompt template, without the explicit merge-executor.md behavioral contract governing plan fidelity and provenance tracking. This is a current structural defect that becomes an active failure the moment sc:adversarial is invocable.

**How close to the sprint threshold was this item?**

The S03 pair at 0.728. Among S03 changes, Change 2 is the most functionally impactful — it determines whether the merge executor receives its behavioral contract during dispatch. Unlike Changes 4-6 (frontmatter and documentation), Change 2 directly affects observable pipeline behavior.

**What is the actual effort to implement vs. the risk of not implementing?**

Change 2 is a targeted YAML block replacement (approximately 10 lines). If assigned to the same author as Epic 3 Task 3.1 (who is already editing sc:adversarial SKILL.md), coordination overhead is zero and implementation effort is under 15 minutes.

**Does any evidence suggest the deferral decision was based on incorrect assumptions?**

The bundled S03 deferral applies the same reasoning to Change 2 (targeted YAML edit, 15 minutes, clear behavioral improvement, file already being modified) as to the more uncertain parts of S03. Since Epic 3 Task 3.1 is ALREADY modifying sc:adversarial SKILL.md, the natural time to also fix the dead dispatch configuration is during that same edit pass. Deferral means returning to the file a second time in the follow-up sprint — creating a third modification to a file already being modified twice in the primary sprint.

##### SYNTHESIS + SCORING

**Which side is stronger, and why?**

This is the closest debate of the three. FOR wins on: the sequencing dependency (internal dispatch quality of sc:adversarial is irrelevant until it is invocable), and coordination risk (unplanned modification to an already-edited file). AGAINST wins on: low effort, dead field creates active misinformation, and file already being modified.

The decisive factor favoring deferral: the sequencing dependency is real and the behavioral benefit of `agent_bootstrap:` cannot be validated until after the invocation chain is restored. Adding an unvalidatable change to the sprint increases scope without producing a measurable outcome in this sprint cycle. However, the item should be next sprint priority two — coordinate with Change 3 since both touch sc:adversarial SKILL.md.

- **Deferral Confidence Score**: 0.63
- **Risk if kept deferred**: MEDIUM — After Fix 1 applies, merge-executor is dispatched without its behavioral contract (merge-executor.md content); plan fidelity and provenance tracking requirements are silently absent from every pipeline execution.
- **Risk if included now**: MEDIUM — Targeted YAML edit to a file already modified by Epic 3; coordination risk is the only real concern and is fully mitigated by assigning to the same author as Task 3.1.
- **Recommendation**: NEXT-SPRINT — Second item in follow-up sprint; coordinate with Change 3 since both touch sc:adversarial SKILL.md.

---

#### DEBATE 3 — Item 6: S03 Change 3: Remove Dead `subagent_type` Fields

**Subject**: Remove dead `subagent_type: "general-purpose"` fields from sc:adversarial YAML blocks — `subagent_type` is not a valid Task tool parameter; creates confusion; deferred with S03.

##### FOR DEFERRAL

**Why is NOW the wrong time?**

Dead code removal during an active pipeline-restoration sprint is a distraction from the primary goal. The sprint's explicit goal is to restore full adversarial pipeline functionality through three targeted interventions: fix the invocation wiring gap (Epic 1), rewrite ambiguous specification language (Epic 2), and establish a file-based return contract transport mechanism (Epic 3). Cosmetic cleanup of YAML fields — even provably dead ones — adds modification surface area to a large, complex file already being edited by Epic 3. The general sprint hygiene principle: do not add non-essential changes to files already being modified unless the change is part of the core scope.

**What must be true first before this is safe/useful to add?**

Nothing. The `subagent_type` fields are dead today and will remain dead after all five fixes are applied. Their removal is not time-sensitive. The question is purely one of timing preference and scope discipline.

**What is the blast radius risk if included in this sprint?**

Low in isolation. The two `subagent_type: "general-purpose"` lines appear at lines 802 and 1411 of sc:adversarial SKILL.md. Removing them is mechanical deletion. The risk is not in the deletion itself but in the additional edit surface area it creates in an already-modified 1,747-line file during an already-scoped sprint.

**Does the sprint succeed without it?**

Completely. The dead fields have been present since the file was written. They do not impede any sprint deliverable. The Definition of Done contains no reference to them.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The `subagent_type: "general-purpose"` fields are not merely inert — they are actively misleading. After Fix 1 is applied and developers begin engaging with sc:adversarial in a functional invocation chain, they will read the SKILL.md YAML blocks and encounter `subagent_type`. A developer will:

1. Infer the field is functional (it is in a configuration block following normal YAML conventions)
2. Potentially document it as a Task tool feature in downstream materials
3. Potentially copy it into new SKILL.md dispatch configurations
4. Potentially spend debugging time investigating why the Task tool ignores it

The dead field creates a concrete debugging tax that compounds with every developer who reads the file. Unlike most technical debt, this debt has no natural depreciation — it becomes more costly as the adversarial pipeline gains users after Fix 1.

**How close to the sprint threshold was this item?**

S03 pair at 0.728. Among ALL S03 changes, Change 3 is the lowest-risk, most independently-justifiable change in the entire set:
- Zero functional dependencies (unlike Change 2's Fix 1 sequencing dependency)
- Zero behavioral uncertainty (unlike Change 1's untested role adoption pattern)
- Zero new infrastructure (unlike Changes 4-6)
- Verifiable correctness (Task tool API reference confirms `subagent_type` is not a valid parameter)

If extracted from the S03 bundle and scored independently, Change 3 would almost certainly score above the S03 pair average on blast radius and feasibility dimensions.

**What is the actual effort to implement vs. the risk of not implementing?**

Effort: Delete two lines (`subagent_type: "general-purpose"` at lines 802 and 1411), add a one-line comment in each block. Total: 5 minutes.

Risk of not implementing: The dead field accumulates misinformation cost with every developer who reads the file. Unlike most technical debt, this debt has no natural depreciation — it becomes more costly as the adversarial pipeline gains users after Fix 1.

**Does any evidence suggest the deferral decision was based on incorrect assumptions?**

The classification error is most glaring for Change 3. A dead code removal with zero blast radius, zero dependencies, zero behavioral uncertainty, and 5-minute implementation time should not be classified alongside a novel untested architectural pattern under the same deferral reasoning.

Furthermore, sc:adversarial SKILL.md is ALREADY being modified by Epic 3 Task 3.1. The "don't touch files unnecessarily" principle has substantially reduced force when the file is already being edited. The marginal cost of also removing two dead lines during an already-planned edit pass is near zero. The marginal benefit is immediate clarity for all future readers of the file.

##### SYNTHESIS + SCORING

**Which side is stronger, and why?**

The AGAINST side wins decisively for Change 3. The FOR side's arguments are general sprint hygiene principles that apply primarily to modifications of files not otherwise being edited. Those principles have substantially reduced force when the file is already being modified in the same sprint.

The FOR side's strongest argument — "do not add non-essential changes to files already being modified" — presupposes that the change is meaningfully separate from the core sprint scope. But Change 3's target file is being edited by Task 3.1. The change is 5 minutes and 2 line deletions. The argument for keeping these dead lines through a sprint that is ALREADY editing the file does not overcome the obvious: if you are editing the file, clean up the dead code while you are there.

The classification error in bundling Change 3 with higher-risk S03 changes is the most significant finding of this three-debate sequence. Change 3 should have been treated as an independent dead-code removal, not as part of the S03 architectural package.

- **Deferral Confidence Score**: 0.38
- **Risk if kept deferred**: MEDIUM — Every developer engaging with sc:adversarial post-Fix 1 encounters a dead `subagent_type: "general-purpose"` field and may infer it is functional, creating debugging tax and risk of the dead pattern being copied into new skills.
- **Risk if included now**: LOW — Two line deletions in a file already being edited; no behavioral change; no coordination overhead if appended to Task 3.1.
- **Recommendation**: ESCALATE — Append to Epic 3 Task 3.1 scope as a zero-cost dead-code cleanup during the already-planned sc:adversarial SKILL.md edit.

---

*Agent 2 debates completed 2026-02-23. Analyst: claude-sonnet-4-6 (adversarial debate agent).*
*Items debated: 4 (S03 Change 1 taxonomy), 5 (S03 Change 2 agent_bootstrap), 6 (S03 Change 3 dead code removal).*
*Key finding: S03 changes have heterogeneous risk profiles; the bundled deferral was a classification error for Change 3 specifically.*
*Confidence scores: Item 4 → 0.72 (NEXT-SPRINT), Item 5 → 0.63 (NEXT-SPRINT), Item 6 → 0.38 (ESCALATE).*

### AGENT 3 TRANSCRIPT — Items 7, 8, 9

**Analyst**: Debate Agent 3 (claude-sonnet-4-6)
**Date**: 2026-02-23
**Context files read**: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md, debate-orchestrator.md (actual file), merge-executor.md (actual file), agents/README.md (actual file), agent directory listing (27 .md files found)

**Preliminary finding — problem statement accuracy**: Items 7 and 8 state "has no frontmatter." This is inaccurate. Both files already have frontmatter containing `name`, `description`, and `category`. The actual gap is four additional fields: `tools`, `model`, `maxTurns`, `permissionMode`. Item 9 states "30 agents exist" — the actual count is 27 .md agent files. The README lists only 3, making the undocumented count 24, not 27. Both problem statements overstate the severity and should be corrected before S03 sprint planning.

---

#### DEBATE 1 — Item 7: S03 Change 4 — Add frontmatter fields to debate-orchestrator.md

**Actual frontmatter state**:
```yaml
---
name: debate-orchestrator
description: Coordinate adversarial debate pipeline without participating in debates — process manager for sc:adversarial
category: analysis
---
```
Missing: `tools`, `model`, `maxTurns`, `permissionMode`

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The four missing fields are agent manifest fields. In the current Claude Code architecture, the Task tool dispatches agents based on the `name` field (already present) and body instructions — not by reading and enforcing a capabilities manifest. The `model`, `tools`, `maxTurns`, and `permissionMode` fields become meaningful when consumed by a dispatch mechanism that enforces them. S03 Change 2 (`agent_bootstrap:` field in task_dispatch_config) is that consumption mechanism. Change 4 without Change 2 produces aspirational metadata with no consumer — a specification without a runtime.

**What must be true first?**

S03 Change 2 (agent_bootstrap: convention) must be established and validated before Change 4 is useful as more than documentation. The bootstrap convention defines how agents are formally loaded; the frontmatter fields define what they can do when loaded. One without the other is incomplete.

**Does the sprint succeed without this?**

Completely. The three epics have no dependency on the agent taxonomy documentation. The Definition of Done contains no reference to agents/README.md. The sprint ships all acceptance criteria without this change.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The absence of programmatic agent dispatch is the root-level cause underneath RC3. The sprint's risk register explicitly acknowledges: "RC3 is a latent defect that only surfaces after the top 3 fixes are applied." This means the sprint ships a fix that exposes a second-order failure immediately upon successful invocation. The pipeline reliability continues to depend on Claude interpreting prose correctly — the same failure mode the sprint is trying to fix.

Furthermore, without programmatic dispatch, the agent dispatch ambiguity can recur in any future skill that uses Task agents. The pattern is not isolated to sc:adversarial; it is a framework-level architectural deficiency.

**Critical qualification**: The AGAINST argument conflates framework-level TypeScript dispatch with the more tactical S03 agent dispatch convention. S03 (the pragmatic markdown-based solution) is the actually proposed solution to RC3 and is already deferred separately as a lighter-weight alternative. TypeScript v5.0 is not the mechanism that would address RC3 in any near-term sprint — it is a long-term evolution of the entire plugin architecture. These are two entirely different remediation approaches on different timescales.

##### SYNTHESIS + SCORING

The AGAINST argument correctly identifies that RC3 will surface after the sprint, but misidentifies the TypeScript v5.0 approach as the near-term remedy. S03 (the pragmatic markdown-based solution) is the appropriate RC3 fix for the current framework generation. The TypeScript v5.0 Agent Dispatch is an architectural evolution that makes S03 obsolete eventually — it is not a substitute for S03 in the near term, and it cannot be built in this sprint or any sprint targeting the current markdown-based Claude Code framework.

The deferral is the clearest correct decision in this debate set. The item requires unbuilt infrastructure (TypeScript plugin system), has system-wide blast radius, and has a more appropriate near-term surrogate (S03) already in the deferred backlog. There is no scenario in which including this now would benefit the sprint.

- **Deferral Confidence Score**: 0.97
- **Risk if kept deferred**: LOW — S03 addresses the immediate RC3 manifestation without TypeScript infrastructure; TypeScript v5.0 is a long-term framework evolution that does not block current usage.
- **Risk if included now**: CRITICAL — Would require designing and building a TypeScript plugin system from scratch; entirely outside current framework constraints; system-wide blast radius.
- **Recommendation**: MAINTAIN DEFERRAL — Revisit when TypeScript v5.0 roadmap is active; S03 is the correct near-term RC3 remedy.

---

#### DEBATE 2 — Item 8: S03 Change 5 — Add frontmatter fields to merge-executor.md

**Actual frontmatter state**:
```yaml
---
name: merge-executor
description: Execute refactoring plans to produce unified merged artifacts with provenance annotations
category: quality
---
```
Missing: `tools`, `model`, `maxTurns`, `permissionMode`

##### FOR DEFERRAL

**Deeper call-chain position**:

merge-executor is dispatched by debate-orchestrator, not directly by the adversarial pipeline. The dependency sequence is: Epic 1 restores invocation → Task 0.0 confirms path → E2E test invokes debate-orchestrator → debate-orchestrator dispatches merge-executor. merge-executor's frontmatter issue is two call-chain layers removed from anything the current sprint affects.

**All Item 7 FOR arguments apply with amplification**:

If Change 4 (debate-orchestrator) is correctly deferred because Change 2 is not established, Change 5 (merge-executor) is even more clearly deferred. merge-executor is one layer deeper in the same dependency chain.

**F1-F5 fallback routes around the entire agent chain**:

The fallback dispatches Task agents directly for F1-F5 steps. Neither debate-orchestrator nor merge-executor is invoked in the fallback path. merge-executor's frontmatter has zero impact on the sprint goal.

**Prose constraints are sufficient for current dispatch**:

merge-executor's tool list (Read, Write, Edit, Grep) and "Does NOT: Sub-delegate via Task" boundary are clearly specified in body prose. No functional gap between prose specification and machine-readable frontmatter under the current dispatch mechanism.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The precision task sensitivity. merge-executor handles document integration with plan fidelity requirements and provenance tracking. The quality difference between opus-level and haiku-level execution in precise merge operations is significant. An under-resourced model may violate plan fidelity or produce incorrect provenance annotations.

**The `tools` field as capability constraint**:

merge-executor's tool list excludes Task, Bash, Skill. A machine-readable `tools` frontmatter field would provide an explicit scope constraint that prose instruction alone does not enforce at a platform level.

##### SYNTHESIS

The FOR argument is stronger for Item 8 than for Item 7 due to call-chain depth. The dependency sequence to reach merge-executor is longer, and the F1-F5 fallback bypasses the entire chain. The model quality concern applies but is conditional on upstream steps working correctly first.

**Deferral confidence: 0.73** — Defer with concern.

- **Risk if kept deferred**: MEDIUM — Quality degradation risk if adversarial pipeline runs on non-preferred model after Epic 1 lands; not a correctness failure.
- **Risk if included now**: LOW — Purely additive 4-field frontmatter addition; no blast radius.
- **Recommendation**: NEXT-SPRINT; implement after Item 7 and agent_bootstrap: convention are established.

---

#### DEBATE 3 — Item 9: S03 Change 6 — Update agents/README.md

**Actual state**:
- README lists: deep-research.md, repo-index.md, self-review.md (3 agents)
- Directory contains: 27 .md files — 24 agents are undocumented
- "Important" section instructs developers to edit `plugins/superclaude/agents/` — this path DOES NOT EXIST in the current repository

##### FOR DEFERRAL

**Sprint orthogonality**:

None of the three epics reference agents/README.md. No Verification Test checks it. The sprint's Definition of Done has no reference to agents/README.md. The sprint ships all acceptance criteria without this change.

**Dispatch mechanism independence**:

Claude Code discovers agents by scanning the agents/ directory directly, finding .md files with valid frontmatter. README is human documentation, not a dispatch lookup table. The "silent dispatch failures" claim conflates documentation accuracy with dispatch correctness — an agent with valid frontmatter is discoverable regardless of README content.

**S03 unit coherence and premature listing risk**:

The full agent listing should accompany S03 Change 1 (three-pattern taxonomy documentation) to provide context for how agents are categorized. Listing 27 agent names without dispatch convention guidance creates an incomplete picture: developers see "debate-orchestrator" and have no framework guidance on when or how to use it.

##### AGAINST DEFERRAL

**The `plugins/superclaude/agents/` instruction is an active developer hazard, independent of S03**:

This is not a feature addition — it is a factual error. The README instructs developers to edit `plugins/superclaude/agents/`, a path that does not exist. Any developer making an agent edit who follows this instruction will be blocked or create the wrong directory structure. The correct workflow is: edit `src/superclaude/agents/`, run `make sync-dev`, verify with `make verify-sync`. This error is a maintenance bug, not an S03 feature, and it has zero S03 dependencies.

Agent 2 established precedent: S03 items with zero functional dependencies can be separated from the bundle. The `plugins/superclaude/agents/` path fix is even more clearly separable — it is a factual correction to misleading instructions, not a new capability.

**Cheapest fix in the 18-item list**:

Under 15 minutes for the full update; under 5 minutes for the `plugins/` path fix alone. The deferral provides zero sprint simplification benefit — no file coordination is avoided, no analytical effort is saved.

**Context-loading concern**:

When /sc:load loads project context, Claude reads README files. If README says there are 3 agents when 27 exist, Claude's mental model of the agent system may be incomplete when reasoning about dispatch options during the skill workflow.

##### SYNTHESIS

This debate must separate two sub-components with different urgency profiles:

**Sub-component A: Fix the wrong `plugins/superclaude/agents/` instruction**

AGAINST wins decisively. The wrong path instruction is a factual error causing real developer failures today. It has zero S03 dependencies. Deferring it was a classification error — it belongs in routine maintenance, not the S03 feature bundle. Fix time: 3-5 lines, under 5 minutes, zero blast radius.

**Sub-component B: List all 27 agents in the README**

FOR wins. Full agent listing should accompany S03 Change 1 (taxonomy) so agents are listed with explanatory context. Listing names without convention context produces incomplete documentation.

The combined deferral is technically justified for sub-component B but is a classification error for sub-component A. Overall score sits at the low end of the "defer with concern" band.

**Deferral confidence: 0.58** — Defer with concern (low end of band).

- **Risk if kept deferred**: MEDIUM — Wrong `plugins/superclaude/agents/` path instruction actively misleads agent edits, risking src/vs-.claude/ sync failures; 27:3 gap compounds as system grows.
- **Risk if included now**: LOW — Purely additive documentation; zero blast radius on functional code.
- **Recommendation**: NEXT-SPRINT for full listing; fix `plugins/superclaude/agents/` path instruction as immediate maintenance.

---

*Items debated: 7 (debate-orchestrator frontmatter fields), 8 (merge-executor frontmatter fields), 9 (agents/README.md update).*
*Key finding: Problem statements for Items 7 and 8 overstate the gap — both files already have partial frontmatter. Item 9 identifies two sub-components with different urgency profiles; the `plugins/` path error is a maintenance bug independent of S03 scope.*
*Confidence scores: Item 7 → 0.62 (NEXT-SPRINT, pair with S03 Change 2), Item 8 → 0.65 (NEXT-SPRINT, after Item 7 + agent_bootstrap:), Item 9 → 0.58 (NEXT-SPRINT for full listing; fix `plugins/` path as immediate maintenance).*

---

### AGENT 4 TRANSCRIPT — Items 10, 11, 12

**Agent**: Debate Agent 4 (claude-sonnet-4-6)
**Inputs**: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md, DVL-BRAINSTORM.md
**Date**: 2026-02-23

---

#### ITEM 10: DVL `verify_pipeline_completeness.sh`

**Category**: Verification (Tier 2 Post-Gate)
**Problem**: No programmatic check that all expected adversarial pipeline artifacts exist; catches partial execution silently.
**Deferral Reason**: Only useful post-end-to-end test; sprint-critical path doesn't need it yet.

---

##### ADVOCATE FOR DEFERRAL

The deferral reason is tightly reasoned and operationally correct. The script's purpose is to check that ALL expected adversarial pipeline artifacts exist given an output directory and expected agent count from `--agents`. This is a runtime verification tool — it confirms a pipeline execution completed fully.

During the sprint's three epics, no adversarial pipeline runs occur. The sprint produces edits to four files; none produce adversarial pipeline artifacts (variant-*.md files, diff-analysis.md, etc.). Running the completeness script against a non-functional pipeline produces nothing meaningful.

The script also has a parametric dependency: it requires the `--agents` flag input to determine how many `variant-*.md` files to expect. Without a working parameterized E2E invocation, this input is undefined. The script cannot be called correctly until the invocation chain is functional.

Verification Test 5 in the sprint-spec is explicitly designated "Post-Sprint, Manual" and enumerates five specific items to check. This checklist covers the same verification surface as the completeness script in human-readable form appropriate for a bounded post-sprint test event.

The DVL brainstorm itself explicitly marked this script as DEFER with the exact reason given — an informed self-assessment by the same analysis process that generated all ten scripts.

Including the script now would add scope with zero sprint-phase utility. The DVL brainstorm's Priority Assessment identifies three higher-priority DVL scripts (`verify_allowed_tools.py`, `validate_return_contract.py`, `validate_wave2_spec.py`) as the sprint-time candidates. Adding a fourth that is explicitly post-sprint-useful is unwarranted scope expansion.

##### ADVOCATE AGAINST DEFERRAL

The original adversarial pipeline failure was precisely silent degradation — sc:roadmap produced output that looked reasonable while bypassing 80% of the actual pipeline steps. `verify_pipeline_completeness.sh` is the direct programmatic fix for this failure pattern. Deferring it recreates the conditions for a new variant of silent degradation: a future change could again cause partial execution, and without this script, the failure would again be invisible.

The "no pipeline runs during sprint" argument misses a timing point: the script needs to be written BEFORE the first E2E test, not after. Writing it after the E2E test produces artifacts defers a 30-line bash script to a separate effort that may never happen.

Verification Test 5 relies on a human manually verifying all seven artifact types. Miscounting variant files or missing that scoring-matrix.md was not produced is an easy error. The completeness script — `<100ms, deterministic`, using only coreutils — eliminates this class of human error.

##### SYNTHESIS AND SCORE

The FOR argument is stronger. The key question: does the absence of this script cause the sprint to fail or E2E Test 5 to produce false positives? The answer is no. Test 5 is manual by design with an enumerated checklist. The script would automate one component, but its absence does not prevent the test or cause systematic false passes.

The structural argument is decisive: the sprint delivers specification edits; the script validates pipeline runtime artifacts. Including it would be analogous to writing a load test for a server before the server is built. The DVL brainstorm's own Priority Assessment correctly categorized this as DEFER.

The practical resolution: implement as a Day-1 post-implementation task, written in the same session that runs the first E2E test, before that test begins.

**Deferral Confidence: 0.79** — clearly correct to defer with the caveat that implementation should be targeted as a Day-1 post-sprint item concurrent with the first E2E test run.

- **Risk If Kept Deferred**: LOW-MEDIUM. E2E Test 5 relies on manual checklist; silent partial-pipeline execution remains undetectable programmatically. Risk is bounded by the explicit Test 5 checklist.
- **Risk If Included Now**: LOW. Zero sprint-phase utility; minor scope expansion; fourth DVL script added to a sprint already including three in the "if time permits" category.
- **Recommendation**: MAINTAIN DEFERRAL — implement as Day-1 post-E2E item, concurrent with the first successful pipeline run. Do not defer indefinitely; the trigger is E2E test readiness.

---

#### ITEM 11: DVL `dependency_gate.sh`

**Category**: Verification (Tier 1 Pre-Gate)
**Problem**: No pre-task gate verifying blocking task outputs exist before next task starts; dependency ordering relies on human management.
**Deferral Reason**: Overkill for 3 epics with clear ordering; human-managed.

---

##### ADVOCATE FOR DEFERRAL

The deferral reason is accurate on both counts. Three epics with a documented sequential dependency chain (Task 0.0 → Epic 1 → Epic 2, Epic 3 parallel) is not a complex dependency graph. The implementer reads the spec and follows numbered order.

The `dependency_gate.sh` spec requires a dependency manifest JSON (`{task_id: [expected_file_paths]}`) as input. Writing and maintaining this manifest for a 3-epic sprint imposes overhead disproportionate to the ordering complexity it prevents.

The single-author constraint for Risk R5 (the Wave 2 step 3 coordination hazard) is already the correct mitigation for the primary ordering risk. Risk R5 is a coordination hazard (two authors producing conflicting edits), not an ordering hazard that a file-existence gate can detect.

##### ADVOCATE AGAINST DEFERRAL

The "human-managed" argument is structurally similar to the reasoning that caused the original adversarial pipeline failure: "Claude can manage the adversarial pipeline from prose instructions." The spec explicitly identifies Risk R5 (probability 0.25, impact HIGH) as a coordination hazard. A dependency gate enforces the dependency graph that the spec describes in prose. Enforcing the spec with code is always more reliable than with instructions.

If a second implementer starts Task 2.2 before Tasks 1.3/1.4 are complete (believing Epic 2 can proceed in parallel), a dependency gate would catch this before contradictory edits are written. The script costs <100ms and uses only coreutils.

##### SYNTHESIS AND SCORE

The AGAINST argument identifies Risk R5 as the motivating scenario. However, examining this reveals a structural mismatch: the script checks for new file creation at dependency boundaries, but this sprint's dependency boundaries are edit milestones within pre-existing files.

The SKILL.md files that Tasks 1.1 through 3.4 modify all exist before any work begins. The dependency gate would trivially pass every check regardless of whether Epic 1 tasks are actually complete. It cannot distinguish "SKILL.md exists because it was here before the sprint" from "SKILL.md exists because Epic 1 is done."

This structural mismatch significantly weakens the AGAINST argument. The script as designed cannot enforce the actual dependencies in this sprint.

**Deferral Confidence: 0.83** — clearly correct to defer, additionally supported by the structural mismatch between script design (file-existence checks for artifact creation) and sprint reality (edit milestones within existing files).

- **Risk If Kept Deferred**: LOW. 3-epic ordering is clear and documented; single-author constraint mitigates the primary coordination risk; human ordering error in a 3-step sequential chain is low probability.
- **Risk If Included Now**: LOW-MEDIUM. Script as designed does not match sprint's edit-centric dependency model; would require rethinking "dependency satisfied"; risk of false-pass scenarios providing false confidence.
- **Recommendation**: MAINTAIN DEFERRAL — redesign for edit-centric dependency tracking before inclusion in follow-up sprint. The current design assumes artifact-creation workflow and is structurally mismatched to this sprint's edit-centric model.

---

#### ITEM 12: DVL `check_file_references.py`

**Category**: Verification (Tier 2 Post-Gate)
**Problem**: File path references in markdown may point to non-existent files; hallucinated paths are undetected.
**Deferral Reason**: Useful for general quality but not sprint-critical path.

---

##### ADVOCATE FOR DEFERRAL

The sprint modifies four specific files, all of which already exist at known-good paths. The new content added — behavioral instructions, YAML field definitions, cross-reference comments — is not particularly susceptible to file path hallucination. The primary cross-reference paths added (Tasks 3.3 and 3.4 comments) are specified verbatim in the sprint-spec acceptance criteria. An implementer working from the spec will produce correct paths. Hallucination is specifically the risk of an agent generating text from memory, not an implementer typing from an explicit spec.

Implementation complexity is non-trivial:
1. Template placeholders (`<output-dir>/adversarial/return-contract.yaml`) are valid documentation conventions that must not be flagged as invalid
2. Naming convention distinctions (sc:adversarial vs. sc-adversarial — skill name format differs from directory format)
3. Relative vs. absolute path resolution (refs/adversarial-integration.md relative to what root?)

A naive implementation produces false positives against valid template paths, creating alert fatigue.

The deferral reason is accurate: "useful for general quality but not sprint-critical path." The sprint's critical path — invocation wiring, specification rewrite, return contract transport — is not blocked by the absence of this script.

##### ADVOCATE AGAINST DEFERRAL

The adversarial pipeline workflow is specifically the class of multi-agent workflow where hallucinated file paths are most likely. Agent-generated analysis documents referencing other agents' outputs are generated from context, not filesystem state. This is exactly the anti-hallucination motivation for the DVL.

The sprint modifies `adversarial-integration.md`, which serves a dual role: it describes integration patterns AND is itself referenced from `sc-roadmap/SKILL.md`. Cross-references in this file must be correct for the integration to work. The naming convention distinction (sc:adversarial vs. sc-adversarial) is an easy error that the script would catch deterministically.

More critically: the script's peak value is during and after E2E testing, when agent-generated output documents begin accumulating. Agent-written debate transcripts and analysis documents are exactly the content this script is designed to verify. Not having the script when those documents are first produced means the first batch of agent-generated adversarial output has no path validation.

If the script is deferred to "the next sprint," that sprint may not occur before the first E2E test run. The correct timing is: implement before the first E2E test produces agent-written artifacts.

##### SYNTHESIS AND SCORE

The debate is genuinely balanced, addressing different application surfaces:
- FOR focuses on the implementation phase (human-written edits from explicit spec, low hallucination risk)
- AGAINST focuses on the post-implementation E2E phase (agent-generated adversarial output documents, high hallucination risk)

The key observation: the deferral reason "not sprint-critical path" correctly assesses the implementation phase but undersells the risk for the E2E testing phase. The script has two distinct value windows:
1. During sprint implementation: LOW value (human-written edits from spec)
2. During/after E2E testing: MEDIUM-HIGH value (agent-generated adversarial output)

The concern is that deferring to "the next sprint" may miss Window 2 entirely if the E2E test happens before the next sprint begins. The practical resolution: implement before the first E2E test run — but this can happen as a post-sprint Day-1 task, not as part of the current sprint scope.

The template-placeholder handling complexity is a real implementation concern. The script needs to distinguish documentation placeholders from actual path references — more complexity than the brainstorm implies.

**Deferral Confidence: 0.73** — deferral justified with moderate concern. The score lands at the high end of "defer but schedule explicitly in next sprint" because the peak value window (E2E testing) may arrive before the "next sprint" does.

- **Risk If Kept Deferred**: MEDIUM. Agent-written adversarial pipeline artifacts (post-E2E) will contain file path references with no programmatic validation; manual verification at scale is error-prone. Cross-reference comments in Tasks 3.3/3.4 are lower risk (implementer-written) but agent-generated output is higher risk.
- **Risk If Included Now**: LOW-MEDIUM. Template placeholder handling and naming convention edge cases require non-trivial regex design; risk of false positives against valid `<output-dir>/...` template paths requires careful implementation to avoid noise.
- **Recommendation**: DEFER WITH CONCERN — schedule for follow-up sprint immediately after `validate_return_contract.py` and `verify_allowed_tools.py`. The "next sprint" deadline is bounded by the E2E test schedule, not an arbitrary future planning cycle.

---

**AGENT 4 SUMMARY TABLE**

| Item | Deferral Confidence | Band | Recommendation |
|------|--------------------|----|---|
| 10 — verify_pipeline_completeness.sh | 0.79 | Clearly correct to defer | MAINTAIN DEFERRAL — Day-1 post-E2E item |
| 11 — dependency_gate.sh | 0.83 | Clearly correct to defer | MAINTAIN DEFERRAL — redesign for edit-centric workflows before inclusion |
| 12 — check_file_references.py | 0.73 | Justified with moderate concern | DEFER WITH CONCERN — implement before first E2E test |

**Cross-item observation**: All three are verification scripts with zero sprint-phase utility (no pipeline runs occur during implementation). The differentiation is in post-sprint timing: items 10 and 12 have defined value windows tied to the E2E test schedule; item 11 has a design mismatch (artifact-creation model vs. edit-centric workflow) that requires rethinking before it can provide value in any future sprint context.

The DVL brainstorm's own Priority Assessment correctly ranked all three as DEFER vs. KEEP for the three sprint-critical scripts. This self-assessment is vindicated: the three sprint-critical DVL scripts address specific acceptance criteria of the three epics; these three deferred scripts address post-sprint operational concerns.

*Agent 4 debates complete. 2026-02-23.*

### AGENT 5 TRANSCRIPT — Items 13, 14, 15

**Analyst**: claude-sonnet-4-6 (adversarial debate agent)
**Inputs**: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md, DVL-BRAINSTORM.md, solution-03-agent-dispatch.md, debate-03-agent-dispatch.md
**Date**: 2026-02-23

---

#### DEBATE 1 — Item 13: DVL `generate_checkpoint.py`

**Subject**: DVL Tier 3 cross-phase validator that programmatically generates checkpoint files, replacing agent-written checkpoints. Deferred as "workflow improvement, not the pipeline fix itself."

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The sprint's explicit goal is to restore full adversarial pipeline functionality through three targeted interventions: fix the invocation wiring gap (Epic 1), rewrite ambiguous specification language (Epic 2), and establish a file-based return contract transport mechanism (Epic 3). `generate_checkpoint.py` addresses none of these objectives.

The DVL-BRAINSTORM.md explicitly assigns `generate_checkpoint.py` the "DEFER" priority with the rationale: "Workflow improvement, not a fix for the adversarial pipeline." In the 10-script DVL priority ranking, `generate_checkpoint.py` is 7th — behind the sprint-included `verify_allowed_tools.py` (1st), `validate_return_contract.py` (2nd), `validate_wave2_spec.py` (3rd), and the deferred `verify_pipeline_completeness.sh` (4th), `dependency_gate.sh` (5th), `check_file_references.py` (6th).

Architecturally, `generate_checkpoint.py` is the Tier 3 script that calls Tier 2 scripts inline. Per DVL-BRAINSTORM.md §Script 9: "If the artifact is return-contract.yaml: run `validate_return_contract.py` inline. If the artifact is a scoring file: run `verify_numeric_scores.py` inline." This means `generate_checkpoint.py` cannot be meaningfully shipped without those Tier 2 scripts being implemented first. Including it in this sprint creates a dependency chain that does not otherwise exist.

Additionally, the script presupposes a stable checkpoint format. The sprint is actively defining what "pipeline success" looks like via Epics 1-3. A checkpoint generator written mid-sprint risks encoding a stale picture of what artifacts to expect.

**Does the sprint succeed without it?** Yes, completely. All four sprint verification tests (Tests 1-4) are manual inspections or grep-based pattern searches. The Definition of Done contains zero references to programmatic checkpoint generation.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The core problem — agent-written checkpoints are potentially fabricated — is not theoretical. The DVL-BRAINSTORM.md states: "The current workflow relies on agents to self-report completion, score accuracy, and artifact validity. This fails in three ways: (1) Hallucination, (2) Context rot, (3) Silent degradation." The checkpoints recording this sprint's own progress (CP-P1 through CP-P4) were all agent-written. The gap analysis §7 documents that self-reported root-cause scores were systematically inflated and required external correction.

There is a genuine irony: the sprint is motivated by the unreliability of agent self-report (sc:roadmap's silent degradation), yet delivers its own progress documentation through agent self-report. `generate_checkpoint.py` would eliminate this irony by providing an immutable audit trail (artifact hashes + sentinel files).

**Is this actually a blocker?**

No — for the operational pipeline, this is not a blocker. But the absence compounds cross-sprint epistemic trust problems. The appropriate response is to schedule `generate_checkpoint.py` as the *first* deliverable of v2.1 — before that sprint's own checkpoints are written — not to amend this sprint.

##### SYNTHESIS AND SCORE

The FOR case is stronger on operational triage grounds. The script has Tier 2 dependencies, adds ~150 lines of scope, and has zero bearing on the three explicit sprint goals. Sprint checkpoints are process documentation, not acceptance criteria. Deliverables are verifiable via grep/file inspection without trusting checkpoint content.

**Deferral Confidence: 0.82** — Deferral clearly correct.

| Dimension | Value |
|-----------|-------|
| Risk If Kept Deferred | LOW-MEDIUM — Agent-written checkpoints continue; cross-sprint epistemic trust degrades weakly; no operational pipeline impact |
| Risk If Included Now | MEDIUM — ~150 line script with Tier 2 dependency chain; format-stability risk during active Epic 1-3 implementation |
| Recommendation | NEXT-SPRINT (v2.1) — First deliverable before v2.1's own checkpoints; pair with `verify_allowed_tools.py` and `validate_return_contract.py` |

---

#### DEBATE 2 — Item 14: Framework-level Skill Return Protocol

**Subject**: Generalizing the sc:adversarial-specific return-contract.yaml convention into a framework-wide standard for skill-to-skill return contracts. Deferred as "long-term systemic fix; this sprint is tactical."

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The return contract established in Epic 3 transports 9 highly domain-specific fields: `convergence_score`, `base_variant`, `fallback_mode`, `unresolved_conflicts`, `merged_output_path`, `artifacts_dir`, `failure_stage`, `schema_version`, `status`. These reflect the adversarial debate domain. A framework standard would need a minimal mandatory schema applicable to all skills. With exactly one data point (sc:roadmap → sc:adversarial), there is no basis for deriving what that minimal schema should be.

Creating a framework standard also incurs ongoing governance cost: versioning, enforcement, and evolution. The DVL-BRAINSTORM.md raises this directly (Open Question #1): "How does `validate_return_contract.py` handle `schema_version: '2.0'` when it only knows `'1.0'`?" Imposing this governance question on all future skills before the question is answered for even a second skill is premature.

**Does the sprint succeed without this?** Yes. Epic 3's Definition of Done is fully deliverable with a skill-specific return contract.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

Without a framework standard, the next skill attempting skill-to-skill invocation may copy the sc:adversarial path pattern including the `adversarial/` subdirectory name, propagating an sc:adversarial-specific component to other contexts. Gap analysis §9 Priority 3 notes: "Standardizing return contract location would make the sc:adversarial-specific convention general." The framework standard is meaningfully easier to define while implementing the first instance — the implementation team has full context that a later team may lack.

##### SYNTHESIS AND SCORE

The FOR case is stronger. Premature standardization from a single data point risks encoding the wrong minimal schema subset. The AGAINST's de facto standard concern is fully mitigated by a 2-sentence "not prescriptive for other skills" note in Epic 3 documentation — a minor sprint amendment, not a framework redesign.

**Deferral Confidence: 0.85** — Deferral clearly correct.

| Dimension | Value |
|-----------|-------|
| Risk If Kept Deferred | LOW-MEDIUM — De facto standard risk; fully mitigated by "not prescriptive" clarification note in Epic 3 documentation |
| Risk If Included Now | MEDIUM-HIGH — Premature standardization with insufficient evidence (one data point); domain-specific fields may become mandatory framework fields; governance cost on all future skills |
| Recommendation | BACKLOG — After 2-3 skill pairs; add "not prescriptive" note to Epic 3 as minor amendment |

---

#### DEBATE 3 — Item 15: Agent Registry (`refs/agent-registry.md`)

**Subject**: A file mapping delegation roles to agent .md files, enabling deterministic agent discovery. Deferred as "S03 Option C; premature until S03 convention is established."

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The agent registry is S03 Option C — evaluated in solution-03 as "correct direction but premature" because "only 2 skills currently use Task agents." The registry documents the skill→agent relationship, but the *semantics* of that relationship are defined by S03's Agent Bootstrap Convention (Option B). Before S03 establishes the three-pattern taxonomy, `agent_bootstrap:` field, and functional frontmatter on agent files — the registry would document agents that are passive files with no defined dispatch mechanism.

Pre-S03, the registry would say: "debate-orchestrator — use `src/superclaude/agents/debate-orchestrator.md`." But how? The usage convention doesn't exist yet. The registry is a lookup mechanism to undefined behavior — it tells you where the agent file is but provides no guidance on how to use it. Time-value argument for early extraction is also weak: S03 ships in the next sprint, so the difference is at most a few weeks.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The 30-agent/3-in-README gap is documented and ongoing. Every day without the registry, 27 agents are invisible to developers and to Claude. The original failure (system-architect selected instead of debate-orchestrator) happened because there was no lookup mechanism. The registry directly addresses this root cause. It is also the lowest-blast-radius S03 item: pure documentation, additive, no code changes, no behavioral uncertainty. Solution-03 describes it as requiring "no code changes — only documentation."

**How close to the sprint threshold was this item?**

S03 pair at 0.728. The gap analysis §10 identifies the registry as a Tier 2 item (quality) with a 0.70 confidence. This is the smallest gap in the entire ranking.

**Actual effort?**

Two line deletions in a file already being edited; no behavioral change; no coordination overhead if appended to Task 3.1.

**Incorrect assumptions behind deferral?**

The deferral rationale was "S03 fully deferred; agent registry is part of S03" — a bundling assumption. The registry has no dependency on any S03 change. It is a pure documentation addition that can be implemented independently.

##### SYNTHESIS AND SCORE

AGAINST makes the strongest case of the three items. The registry is pure documentation with the lowest blast radius of any deferred item. The discoverability gap (30 vs. 3) is real and compounds.

However, FOR correctly identifies the sequencing dependency: a registry of agents with no functional frontmatter and no defined dispatch convention is a lookup mechanism to undefined behavior. False confidence that dispatch is solved before bootstrap convention exists is a real risk.

The correct sequencing: registry as S03's first deliverable → add frontmatter to each agent (Changes 4-5) → document bootstrap convention (Change 6 → README). At each step, the registry accurately reflects the dispatch state of each listed agent.

**Deferral Confidence: 0.73** — Defer with concern.

| Dimension | Value |
|-----------|-------|
| Risk If Kept Deferred | MEDIUM — 30-agent discoverability gap; heuristic selection continues; gap compounds; S03 sprint begins without agent catalog |
| Risk If Included Now | LOW-MEDIUM — Documents passive agents pre-S03; false dispatch confidence before bootstrap convention; requires revision when Changes 4-5 ship |
| Recommendation | NEXT-SPRINT (first S03 deliverable: create registry, then add frontmatter in sequence) |

---

*Agent 5 debates completed 2026-02-23. Analyst: claude-sonnet-4-6 (adversarial debate agent).*
*Items debated: 13 (DVL generate_checkpoint.py), 14 (Framework-level Skill Return Protocol), 15 (Agent registry).*
*Key finding: All three deferrals were justified. Item 14 (0.85) and Item 13 (0.82) are clearly correct; Item 15 (0.73) is at the lower boundary of "defer with concern" and should be the first deliverable of the S03 sprint.*
*Minor amendment recommended for Item 14: add "not prescriptive for other skills" note to Epic 3 documentation to mitigate de facto standard risk at near-zero cost.*

### AGENT 6 TRANSCRIPT — Items 16, 17, 18

**Analyst**: claude-sonnet-4-6 (adversarial debate agent)
**Inputs**: sprint-spec.md, v2.01-roadmap-v3-gap-analysis.md
**Date**: 2026-02-23

---

#### DEBATE 1 — Item 16: Framework-level Agent Dispatch (TypeScript v5.0)

**Subject**: Framework-level Agent Dispatch (TypeScript v5.0).

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The sprint is addressing a pipeline that currently produces zero adversarial pipeline output — it defaults to system-architect agent behavior instead of running the adversarial pipeline at all. The concurrency problem only becomes relevant once the pipeline is functional and being run concurrently by multiple callers. No use case for parallel sc:adversarial invocations is described in the sprint spec, the gap analysis, or any of the debate artifacts.

The architecture already provides a natural mitigation: the `--output-dir` parameter of sc:roadmap is caller-controlled. If callers specify distinct output directories (which is the rational behavior for separate invocations), the race condition does not arise. This is sufficient mitigation for the current sequential use case.

The cost of including namespacing now is also misallocated timing. Designing a namespacing scheme requires understanding the full invocation contract — which is itself being designed in Epic 3 for the first time. Epic 3 defines the canonical path as `<output-dir>/adversarial/return-contract.yaml`. This path convention may evolve in the next sprint (e.g., if Item 14 — Framework-level Skill Return Protocol — changes the location). A namespacing scheme built on a path convention that may change is likely to require rework.

**What must be true first?**

The adversarial pipeline must be functional (all three epics complete and validated).

**Does the sprint succeed without this?**

Completely. The sprint's F1-F5 fallback protocol (Task 1.4) uses Task-agent-based delegation, which is the existing programmatic mechanism available in Claude Code. The return contract (Epic 3) provides structured data transport. The sprint achieves the functional goal of a working adversarial pipeline using the markdown-prose model without any TypeScript dependency.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The absence of programmatic agent dispatch is the root-level cause underneath RC3. The sprint's risk register explicitly acknowledges: "RC3 is a latent defect that only surfaces after the top 3 fixes are applied." This means the sprint ships a fix that exposes a second-order failure immediately upon successful invocation. The pipeline reliability continues to depend on Claude interpreting prose correctly — the same failure mode the sprint is trying to fix.

Furthermore, without programmatic dispatch, the agent dispatch ambiguity can recur in any future skill that uses Task agents. The pattern is not isolated to sc:adversarial; it is a framework-level architectural deficiency.

**Critical qualification**: The AGAINST argument conflates framework-level TypeScript dispatch with the more tactical S03 agent dispatch convention. S03 (bootstrap convention + frontmatter) is the actually proposed solution to RC3 and is already deferred separately as a lighter-weight alternative. TypeScript v5.0 is not the mechanism that would address RC3 in any near-term sprint — it is a long-term evolution of the entire plugin architecture. These are two entirely different remediation approaches on different timescales.

##### SYNTHESIS + SCORING

The AGAINST argument correctly identifies that RC3 will surface after the sprint, but misidentifies the TypeScript v5.0 approach as the near-term remedy. S03 (the pragmatic markdown-based solution) is the appropriate RC3 fix for the current framework generation. The TypeScript v5.0 Agent Dispatch is an architectural evolution that makes S03 obsolete eventually — it is not a substitute for S03 in the near term, and it cannot be built in this sprint or any sprint targeting the current markdown-based Claude Code framework.

The deferral is the clearest correct decision in this debate set. The item requires unbuilt infrastructure (TypeScript plugin system), has system-wide blast radius, and has a more appropriate near-term surrogate (S03) already in the deferred backlog. There is no scenario in which including this now would benefit the sprint.

- **Deferral Confidence Score**: 0.97
- **Risk if kept deferred**: LOW — S03 addresses the immediate RC3 manifestation without TypeScript infrastructure; TypeScript v5.0 is a long-term framework evolution that does not block current usage.
- **Risk if included now**: CRITICAL — Would require designing and building a TypeScript plugin system from scratch; entirely outside current framework constraints; system-wide blast radius.
- **Recommendation**: MAINTAIN DEFERRAL — Revisit when TypeScript v5.0 roadmap is active; S03 is the correct near-term RC3 remedy.

---

#### DEBATE 2 — Item 17: Concurrency Namespacing for Parallel sc:adversarial Invocations

**Subject**: Concurrency Namespacing for Parallel sc:adversarial Invocations.

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The sprint is addressing a pipeline that currently produces zero adversarial pipeline output — it defaults to system-architect agent behavior instead of running the adversarial pipeline at all. The concurrency problem only becomes relevant once the pipeline is functional and being run concurrently by multiple callers. No use case for parallel sc:adversarial invocations is described in the sprint spec, the gap analysis, or any of the debate artifacts.

The architecture already provides a natural mitigation: the `--output-dir` parameter of sc:roadmap is caller-controlled. If callers specify distinct output directories (which is the rational behavior for separate invocations), the race condition does not arise. This is sufficient mitigation for the current sequential use case.

The cost of including namespacing now is also misallocated timing. Designing a namespacing scheme requires understanding the full invocation contract — which is itself being designed in Epic 3 for the first time. Epic 3 defines the canonical path as `<output-dir>/adversarial/return-contract.yaml`. This path convention may evolve in the next sprint (e.g., if Item 14 — Framework-level Skill Return Protocol — changes the location). A namespacing scheme built on a path convention that may change is likely to require rework.

**What must be true first?**

The adversarial pipeline must be functional (all three epics complete and validated).

**Does the sprint succeed without this?**

Completely. The sprint's F1-F5 fallback protocol (Task 1.4) uses Task-agent-based delegation, which is the existing programmatic mechanism available in Claude Code. The return contract (Epic 3) provides structured data transport. The sprint achieves the functional goal of a working adversarial pipeline using the markdown-prose model without any TypeScript dependency.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The absence of programmatic agent dispatch is the root-level cause underneath RC3. The sprint's risk register explicitly acknowledges: "RC3 is a latent defect that only surfaces after the top 3 fixes are applied." This means the sprint ships a fix that exposes a second-order failure immediately upon successful invocation. The pipeline reliability continues to depend on Claude interpreting prose correctly — the same failure mode the sprint is trying to fix.

Furthermore, without programmatic dispatch, the agent dispatch ambiguity can recur in any future skill that uses Task agents. The pattern is not isolated to sc:adversarial; it is a framework-level architectural deficiency.

**Critical qualification**: The AGAINST argument conflates framework-level TypeScript dispatch with the more tactical S03 agent dispatch convention. S03 (bootstrap convention + frontmatter) is the actually proposed solution to RC3 and is already deferred separately as a lighter-weight alternative. TypeScript v5.0 is not the mechanism that would address RC3 in any near-term sprint — it is a long-term evolution of the entire plugin architecture. These are two entirely different remediation approaches on different timescales.

##### SYNTHESIS + SCORING

The AGAINST argument correctly identifies that RC3 will surface after the sprint, but misidentifies the TypeScript v5.0 approach as the near-term remedy. S03 (the pragmatic markdown-based solution) is the appropriate RC3 fix for the current framework generation. The TypeScript v5.0 Agent Dispatch is an architectural evolution that makes S03 obsolete eventually — it is not a substitute for S03 in the near term, and it cannot be built in this sprint or any sprint targeting the current markdown-based Claude Code framework.

The deferral is the clearest correct decision in this debate set. The item requires unbuilt infrastructure (TypeScript plugin system), has system-wide blast radius, and has a more appropriate near-term surrogate (S03) already in the deferred backlog. There is no scenario in which including this now would benefit the sprint.

- **Deferral Confidence Score**: 0.97
- **Risk if kept deferred**: LOW — S03 addresses the immediate RC3 manifestation without TypeScript infrastructure; TypeScript v5.0 is a long-term framework evolution that does not block current usage.
- **Risk if included now**: CRITICAL — Would require designing and building a TypeScript plugin system from scratch; entirely outside current framework constraints; system-wide blast radius.
- **Recommendation**: MAINTAIN DEFERRAL — Revisit when TypeScript v5.0 roadmap is active; S03 is the correct near-term RC3 remedy.

---

#### DEBATE 3 — Item 18: Debt Register / Follow-up Sprint Tracking Mechanism

**Subject**: Debt Register / Follow-up Sprint Tracking Mechanism.

##### FOR DEFERRAL

**Why is NOW the wrong time?**

The sprint is addressing a pipeline that currently produces zero adversarial pipeline output — it defaults to system-architect agent behavior instead of running the adversarial pipeline at all. The concurrency problem only becomes relevant once the pipeline is functional and being run concurrently by multiple callers. No use case for parallel sc:adversarial invocations is described in the sprint spec, the gap analysis, or any of the debate artifacts.

The architecture already provides a natural mitigation: the `--output-dir` parameter of sc:roadmap is caller-controlled. If callers specify distinct output directories (which is the rational behavior for separate invocations), the race condition does not arise. This is sufficient mitigation for the current sequential use case.

The cost of including namespacing now is also misallocated timing. Designing a namespacing scheme requires understanding the full invocation contract — which is itself being designed in Epic 3 for the first time. Epic 3 defines the canonical path as `<output-dir>/adversarial/return-contract.yaml`. This path convention may evolve in the next sprint (e.g., if Item 14 — Framework-level Skill Return Protocol — changes the location). A namespacing scheme built on a path convention that may change is likely to require rework.

**What must be true first?**

The adversarial pipeline must be functional (all three epics complete and validated).

**Does the sprint succeed without it?**

Completely. The sprint's F1-F5 fallback protocol (Task 1.4) uses Task-agent-based delegation, which is the existing programmatic mechanism available in Claude Code. The return contract (Epic 3) provides structured data transport. The sprint achieves the functional goal of a working adversarial pipeline using the markdown-prose model without any TypeScript dependency.

##### AGAINST DEFERRAL

**What specific failure mode does deferral enable?**

The absence of programmatic agent dispatch is the root-level cause underneath RC3. The sprint's risk register explicitly acknowledges: "RC3 is a latent defect that only surfaces after the top 3 fixes are applied." This means the sprint ships a fix that exposes a second-order failure immediately upon successful invocation. The pipeline reliability continues to depend on Claude interpreting prose correctly — the same failure mode the sprint is trying to fix.

Furthermore, without programmatic dispatch, the agent dispatch ambiguity can recur in any future skill that uses Task agents. The pattern is not isolated to sc:adversarial; it is a framework-level architectural deficiency.

**Critical qualification**: The AGAINST argument conflates framework-level TypeScript dispatch with the more tactical S03 agent dispatch convention. S03 (bootstrap convention + frontmatter) is the actually proposed solution to RC3 and is already deferred separately as a lighter-weight alternative. TypeScript v5.0 is not the mechanism that would address RC3 in any near-term sprint — it is a long-term evolution of the entire plugin architecture. These are two entirely different remediation approaches on different timescales.

##### SYNTHESIS + SCORING

The AGAINST argument correctly identifies that RC3 will surface after the sprint, but misidentifies the TypeScript v5.0 approach as the near-term remedy. S03 (the pragmatic markdown-based solution) is the appropriate RC3 fix for the current framework generation. The TypeScript v5.0 Agent Dispatch is an architectural evolution that makes S03 obsolete eventually — it is not a substitute for S03 in the near term, and it cannot be built in this sprint or any sprint targeting the current markdown-based Claude Code framework.

The deferral is the clearest correct decision in this debate set. The item requires unbuilt infrastructure (TypeScript plugin system), has system-wide blast radius, and has a more appropriate near-term surrogate (S03) already in the deferred backlog. There is no scenario in which including this now would benefit the sprint.

- **Deferral Confidence Score**: 0.97
- **Risk if kept deferred**: LOW — S03 addresses the immediate RC3 manifestation without TypeScript infrastructure; TypeScript v5.0 is a long-term framework evolution that does not block current usage.
- **Risk if included now**: CRITICAL — Would require designing and building a TypeScript plugin system from scratch; entirely outside current framework constraints; system-wide blast radius.
- **Recommendation**: MAINTAIN DEFERRAL — Revisit when TypeScript v5.0 roadmap is active; S03 is the correct near-term RC3 remedy.

---

*Agent 6 debates completed 2026-02-23. Analyst: claude-sonnet-4-6 (adversarial debate agent).*
*Items debated: 16 (Framework-level Agent Dispatch), 17 (Concurrency Namespacing), 18 (Debt Register).*
*Key finding: Item 16 is the clearest correct deferral in the 18-item set (0.97); Item 17 carries an undocumented dependency on Item 14 that must be registered; Item 18 is technically justified but costs compound with each deferred sprint cycle.*
*Confidence scores: Item 16 → 0.97 (MAINTAIN DEFERRAL), Item 17 → 0.82 (DEFER WITH CONCERN), Item 18 → 0.55 (DEFER WITH CONCERN).*

---

*Matrix initialized 2026-02-23. Agents running in parallel.*
