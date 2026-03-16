---
convergence_score: 0.72
rounds_completed: 2
---

# Structured Adversarial Debate: Opus vs. Haiku Roadmap Variants

## Round 1: Initial Positions on Divergence Points

---

### Variant A (Opus) — Opening Position

**On Token Budget and Resource Planning**

The absence of any token budget in Haiku's variant is a critical operational blind spot. This is not a stylistic preference — it is a risk management failure. A 170K token sprint that discovers it is resource-constrained at Phase 4 (the most expensive phase) has no recovery path except aborting or partial execution. Opus provides per-phase estimates with explicit identification of Phase 4 as the 40K bottleneck. This enables teams to make a go/no-go decision *before* committing. Resource blindness is not conservatism; it is negligence.

**On Phase 2/3 Parallelism**

Haiku's "sequence conservatively unless parallelism is confirmed" stance introduces unnecessary latency. OQ-006 is explicitly designated for Phase 0 resolution in Opus's plan — the executor capability question is answered *before* Phase 1 even begins. By Phase 2, the team is not guessing; they know. Haiku treats the open question as if it will remain open indefinitely and builds its entire execution model around that pessimistic assumption. The correct response to uncertainty is to resolve it early, not to permanently degrade throughput.

**On Timeline Concreteness**

"Working sessions" is an operationally useless unit. A "session" could be 90 minutes of focused work or 6 hours of deep analysis depending on context. Haiku's 14–25 session range spans a 78% variance. Opus's 3–5 day estimate with an hours-based critical path of 38 hours gives project sponsors and schedulers something they can actually use. The fact that Haiku's range is wider is not a feature — it reflects imprecision masquerading as caution.

**On OQ-005 and OQ-007 Resolution**

Haiku is silent on OQ-007 (fixed vs. dynamic comparison pairs) and hedges on OQ-005 (schema validator). These are not optional positions. The 8-pair cap question has direct scope implications for Phase 4, which is already the most expensive phase. Leaving this ambiguous until Phase 1 exit without a recommended default means teams may re-debate it under time pressure. Opus's "cap at 8 unless critical gap discovered" is concrete and correct. Similarly, "automate if low effort, otherwise document" for OQ-005 is a hedge that leaves the team making the same decision twice. A 50-line validation script is always low effort compared to manual review of 35+ artifacts.

---

### Variant B (Haiku) — Opening Position

**On Team Model and Organizational Reality**

Opus treats this sprint as a solo operation. Haiku explicitly defines four roles: Architect lead, Analysis operator, Validation reviewer, and optional Human reviewer. Any non-trivial analytical program — one producing 35+ artifacts across 8 phases — will involve multiple people in practice. A roadmap that provides no role decomposition forces improvised coordination. Haiku's role model is not overhead; it is the minimum scaffolding needed for a team to divide work without collision. Opus's silence on this point is not simplicity — it is an unexamined assumption.

**On Phase 5 Synthesis Architecture**

This is arguably the highest-stakes divergence. Opus organizes Phase 5 synthesis around *components*. Haiku organizes it around *principles*: evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement. The difference in downstream output is significant. A component-organized merged strategy produces a document where each section answers "what do we do with component X?" A principle-organized merged strategy produces a document where each section answers "what architectural discipline do we enforce?" The latter is transferable across future sprints, reusable in other contexts, and produces more durable guidance. Opus's approach optimizes for traceability; Haiku's optimizes for architectural leverage.

**On Phase 7 Rigor**

Opus characterizes Phase 7 as "a completeness and compliance scan." Haiku characterizes it as "a formal architecture review gate" with explicit disqualifying conditions: unverifiable evidence, copied mass, broken lineage, drift into implementation scope. These are not equivalent. Calling Phase 7 a "scan" undersets expectations and invites a checkbox mentality. If the adversarial validation layer is the primary defense against systematic invariant violations, it must be treated as a genuine gate with genuine failure conditions — not a scan that happens to catch things. Haiku's characterization is more honest about the stakes.

**On OQ-008 and Operational Robustness**

Opus proposes a single threshold for Auggie "unavailability": <50% query coverage. This is simple but brittle. What counts as a "query"? What if coverage is 51% but all returned results are confidence-degraded? What if queries succeed but return stale cached data? Haiku's multi-criteria approach — covering timeout, repeated failure threshold, and incomplete result confidence — handles the real-world failure modes that a single percentage threshold cannot capture. Simpler is not always better when the failure mode is nuanced.

**On Resume as First-Class Acceptance Criteria**

The sprint's prior crash history (RISK-006) is not a theoretical concern — it is documented operational evidence. Haiku explicitly mandates that resume testing be part of Phase 8 acceptance criteria. Opus mentions resume as "desirable" and includes it in an acceptance table, but does not treat it as a mandatory gate condition. The distinction matters. Optional QA items are the first things cut under schedule pressure. If restartability is foundational to trust (as both variants agree it is), then its verification must be mandatory, not aspirational.

**On Proactive Downstream Schema Validation**

Haiku explicitly recommends validating `/sc:roadmap` schema expectations *before* Phase 8 finalization. Opus mentions `/sc:roadmap` compatibility as a Phase 8 output criterion. The timing difference is significant. Discovering a schema incompatibility *during* Phase 8 creates rework that has already been gated through Phase 7. Discovering it *before* Phase 8 allows schema corrections to be made at the planning level. Haiku's proactive integration check is a basic principle of shift-left quality engineering.

---

## Round 2: Rebuttals

---

### Variant A (Opus) — Rebuttal

**Rebutting Haiku's Role Model**

Haiku's four-role decomposition is valuable for team execution, and Opus concedes this divergence. However, the claim that Opus "assumes solo execution" conflates absence of specification with prescription against teams. Opus's non-specification of roles is an omission, not an architectural constraint. The more important point is that Haiku's role model adds coordination overhead that must be accounted for in the timeline — which Haiku's estimates do not appear to reflect. If Validation reviewer handoffs and Architect lead sign-offs add session overhead, the 14–25 session range underestimates multi-person coordination cost.

**Rebutting the Phase 5 Synthesis Claim**

Haiku's principle-centric synthesis is architecturally elegant, but Opus disputes the claim that it is unambiguously stronger. Component-centric synthesis maintains direct traceability from Phase 1 inventory through Phase 6 improvement plans. If Phase 5's merged strategy is organized around principles while Phase 6's improvement plans are organized around components, a translation layer is required. Any reviewer must map "evidence integrity principle" back to specific components to produce actionable improvement items. Haiku's synthesis is more reusable; Opus's is more directly executable. The question of which matters more depends on whether this sprint's primary consumer is a future sprint runner or a strategic architecture audience. For a sprint producing a machine-readable backlog, component-centricity has meaningful practical advantages.

**Rebutting Phase 7 Framing**

Opus's "compliance scan" characterization is challenged, and the challenge is partly valid. However, Haiku's "formal architecture review gate" framing comes with a cost that Haiku does not price: it requires a qualified architecture reviewer to execute Phase 7, not just a systematic checklist operator. If the Architect lead who designed the program is also the one running Phase 7 validation, the adversarial value is compromised. Opus's framing, while less rigorous-sounding, is more honest about what machine-executable validation can actually accomplish without an independent human reviewer.

**Rebutting OQ-008 Multi-Criteria**

Haiku's multi-criteria Auggie unavailability definition is more nuanced, and Opus concedes this is the stronger approach. However, Haiku's formulation introduces a new problem: it provides three criteria without specifying how they combine. Is it AND (all three conditions must hold)? OR (any one triggers fallback)? Threshold-based (two of three)? Opus's 50% coverage threshold is operationally unambiguous even if it is incomplete. The merged answer should adopt Haiku's criteria taxonomy while specifying explicit combination logic — which neither variant currently does.

**On Timeline Units — Maintaining the Position**

Haiku does not rebut the operational uselessness of "working sessions" as a unit; the Haiku opening position simply does not address it. The 78% variance in Haiku's range remains a practical scheduling problem. Opus's hours-based estimates are not claimed to be perfectly accurate — they are claimed to be more actionable than session-counts. This position stands.

---

### Variant B (Haiku) — Rebuttal

**Rebutting Opus's Token Budget Claim**

Opus's 170K token estimate is presented as evidence-based, but it is not. The per-phase estimates (40K for Phase 4, 25K for Phase 3, etc.) are architectural approximations with no derivation methodology disclosed. A token budget that was actually derived from historical adversarial debate costs, inventory query patterns, and synthesis complexity would be operationally valuable. A token budget that is architectural intuition dressed as measurement provides false confidence. Teams that plan to Phase 4 budget and discover actual costs are 2x higher — because adversarial debates run long when evidence is contested — face a worse planning failure than teams that had no budget at all. Haiku's silence on token budgets is not negligence; it is an honest refusal to publish numbers that would require disclosure of derivation methodology to be trustworthy.

**Rebutting the Parallelism Timing Argument**

Opus argues that OQ-006 is resolved in Phase 0 so by Phase 2 the team "knows." This is correct as far as it goes, but it does not address what happens when the test in Phase 0 produces an ambiguous result — which is a realistic outcome for executor capability testing. "Does the runner support parallelism?" often has answers like "sometimes, under these conditions, with these caveats." Haiku's conservative default is not pessimism; it is a hedge against ambiguous capability tests producing false confidence. The 4-hour critical path savings from Phase 2/3 parallelism is Opus's estimate — if that estimate is wrong and parallelism creates artifact ordering issues, the cost of recovery exceeds the savings.

**Rebutting the Phase 5 Translation Layer Concern**

Opus argues that principle-centric synthesis requires a translation layer to produce component-level improvement plans in Phase 6. This misunderstands how principle-centric synthesis works in practice. The merged strategy does not eliminate component references — it organizes cross-component guidance under architectural principles that apply to multiple components. A "restartability principle" section would explicitly name which components need resume-semantic improvements. Phase 6 planners read the merged strategy and produce component-level plans with full traceability intact. The added value is that a future sprint runner can consult the merged strategy to understand *why* a given improvement was prioritized, not just *what* was changed. Traceability is preserved; architectural leverage is added.

**Rebutting the Phase 7 Independent Reviewer Argument**

Opus raises a valid concern that Phase 7's adversarial value is compromised if the Architect lead runs both design and validation. However, this is an argument for including Haiku's Validation reviewer role — not an argument against formal architecture review framing. Opus's rebuttal unintentionally strengthens Haiku's case: if Phase 7 requires independence to function as a genuine gate, then the role model that Haiku provides (separate Validation reviewer) is necessary for the framing Haiku recommends. The implication that Opus's lower-bar "compliance scan" framing is more honest about machine-executable limits is actually an argument for human-in-the-loop validation — which is what Haiku's optional Human reviewer provides.

**Rebutting the Timeline Unit Dismissal**

Opus claims "working sessions" is operationally useless. But hours-based estimates carry a different problem: they imply precision that cannot be justified for token-intensive, evidence-dependent analytical work where query latency, MCP availability, and evidence density are variable. A 4-hour Phase 2 estimate that takes 7 hours due to Auggie MCP partial failures creates a scheduling failure that an hours-based plan cannot gracefully absorb. Session-based estimates acknowledge variable-duration units and prompt teams to size sessions appropriately. The 78% variance in Haiku's range is not imprecision — it is calibrated uncertainty disclosure. Opus's narrower range may simply reflect overconfidence.

---

## Convergence Assessment

### Areas of Agreement Reached Through Debate

1. **OQ-008 Resolution**: Both variants now converge on a multi-criteria approach (Haiku's taxonomy) with explicit combination logic (neither variant provides this, but debate surfaces it as the synthesis target). **Merged position**: Auggie is "unavailable" if ANY of: timeout occurs, repeated failure threshold exceeded (suggest: 3 consecutive), OR coverage confidence falls below 50% (Opus's threshold). This combines Haiku's nuance with Opus's operational clarity.

2. **Phase 0 Thoroughness**: Both agree Phase 0 is where the majority of sprint risk is eliminated. Both agree OQ-006 must be resolved before Phase 2 begins. The debate narrows to what happens when Phase 0 produces an ambiguous parallelism result — Haiku wins this sub-point, suggesting the conservative default is the right fallback.

3. **Resume as Mandatory**: The debate reveals that Haiku's framing (mandatory Phase 8 acceptance) is substantively stronger than Opus's (acceptance table entry). Given prior crash history, restartability verification should not be optional QA. **Merged position**: Resume testing is Phase 8 acceptance criteria, not optional.

4. **Role Model Value**: Opus's rebuttal concedes the value of Haiku's role decomposition while noting it adds coordination overhead not reflected in Haiku's timeline. **Merged position**: Adopt Haiku's four-role model; add coordination overhead to timeline estimates.

5. **Downstream Schema Validation Timing**: Haiku's proactive pre-Phase-8 validation wins this point clearly. Opus's rebuttal does not contest it. **Merged position**: Validate `/sc:roadmap` schema expectations before Phase 8 finalization, not at Phase 8 gate.

### Remaining Disputes

1. **Timeline Units**: This dispute is genuine and unresolved. Opus's hours-based estimates provide calendar utility; Haiku's session-based estimates provide honest uncertainty disclosure. Neither side fully concedes. **Remaining gap**: Teams should use hours for scheduling and sessions for effort-uncertainty communication — a hybrid neither variant currently provides.

2. **Phase 5 Organization Principle**: Both variants make legitimate arguments. Opus's component-centric approach preserves direct Phase 1–6 traceability. Haiku's principle-centric approach produces more architecturally reusable output. Haiku's rebuttal successfully challenges Opus's "translation layer" concern but does not eliminate the traceability complexity. **Remaining gap**: The merged strategy document design is a genuine design decision; teams must choose before Phase 5 begins based on the primary consumer of the output (backlog tooling vs. architectural audience).

3. **Token Budget Legitimacy**: Haiku's rebuttal raises a valid epistemological challenge — undisclosed derivation methodology makes budget estimates dangerous if teams treat them as reliable. Opus's counter — that any estimate is better than none — is also defensible. **Remaining gap**: If token budgets are included, derivation methodology must be disclosed alongside estimates. Opus's 170K figure without derivation is weaker than Haiku's silence if teams misinterpret it as measured rather than estimated.

4. **Phase 7 Gate Height**: Haiku's formal architecture review framing is more rigorous; Opus's compliance scan framing is more honest about automated execution limits. Haiku's rebuttal strengthens the case for its role model (independent Validation reviewer) as the enabler of its Phase 7 framing. **Remaining gap**: Teams must explicitly decide whether Phase 7 will have an independent human reviewer before committing to Haiku's higher bar.

### Final Convergence Score: 0.72

The two variants agree on architecture, invariants, phase structure, artifact targets, and most open question resolutions. The remaining disputes are concentrated in four areas: timeline unit choice, Phase 5 organization principle, token budget methodology, and Phase 7 gate height. These are genuine design decisions — not errors — that require team-level resolution before execution. A merged roadmap incorporating Haiku's role model, formal Phase 7 framing, principle-enriched Phase 5, proactive downstream validation, and mandatory resume testing, combined with Opus's token budgets (with disclosed methodology), parallelism optimization, OQ-005/OQ-007 defaults, and hours-based calendar estimates, would outperform either variant individually.
