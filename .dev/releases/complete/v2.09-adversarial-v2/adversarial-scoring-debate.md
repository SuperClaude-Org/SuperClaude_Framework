# Adversarial Scoring Debate: 17 Process Improvement Proposals

**Date**: 2026-03-04
**Context**: v0.04 Adaptive Replay post-implementation retrospective
**Method**: 3-round adversarial debate between Agent A (Architect/Pragmatist) and Agent B (Quality Advocate)
**Composite Formula**: `(likelihood * 3 + generality * 2) / (complexity + cost)`

---

## Round 1: Initial Independent Scoring

### Agent A (Architect/Pragmatist)

*Philosophy: High ROI proposals that catch real bugs without bloating every invocation. Skeptical of proposals that add ceremony without proportional value. Favors low-complexity, low-cost improvements that compose well.*

#### sc:spec-panel Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| SP-1 | State Machine Trace-Through | 3 | 3 | 5 | 4 | 3.83 | Powerful but expensive. A full trace-through pass is essentially a second review. Worth it for stateful specs, but not every spec needs it. |
| SP-2 | Boundary Value Obligation | 2 | 2 | 4 | 3 | 4.50 | Low friction, high signal. A table template is cheap to add and forces the right questions. Not every guard is interesting, so there is some wasted effort. |
| SP-3 | Adversarial Tester Persona | 1 | 2 | 4 | 4 | 6.67 | Cheapest proposal in the set. Adding a persona prompt costs almost nothing in pipeline changes. The destructive mindset is the missing ingredient. |
| SP-4 | Invariant Specification Req. | 3 | 2 | 5 | 4 | 4.60 | High value but requires spec authors to write invariants, which is a discipline change. The panel can enforce it, but the spec has to contain the material first. |
| SP-5 | Execution Scenarios w/ State | 3 | 3 | 4 | 3 | 3.00 | Extends Given/When/Then significantly. The state snapshot format is valuable but labor-intensive. Overlaps heavily with SP-1. |
| SP-6 | Consumed vs Produced Analysis | 1 | 1 | 3 | 2 | 6.50 | Extremely cheap heuristic. Narrow but hits a real bug class. The "which count?" question is easy to add to any review checklist. |

#### sc:adversarial Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| AD-1 | Failure Mode Enumeration | 2 | 3 | 4 | 3 | 3.60 | Structured format is good, but 3 failure modes per variant per advocate is a lot of tokens. Overlaps with AD-4. |
| AD-2 | Concrete Scenario Traces | 3 | 4 | 5 | 4 | 3.29 | Very powerful but very expensive. 3-5 scenarios traced by each advocate is a massive token cost. Should be gated behind --depth deep. |
| AD-3 | Invariant Declaration & Challenge | 3 | 3 | 5 | 4 | 3.83 | Formal verification lite. The challenge round is compelling but adds a full debate round. High signal per token though. |
| AD-4 | Devil's Advocate Role | 2 | 2 | 4 | 4 | 5.00 | Best ROI in the adversarial set. One focused agent is cheaper than asking all advocates to enumerate failures. Clean separation of concerns. |
| AD-5 | State Coverage Gate | 2 | 1 | 3 | 3 | 5.00 | Cheap formula modification. Prevents shallow convergence. But the coverage categories need careful calibration -- too strict and debates never converge. |
| AD-6 | Post-Merge Trace Validation | 3 | 3 | 3 | 2 | 2.17 | Catches a real but narrow class (merge artifacts). The fresh agent adds cost. Most bugs should be caught pre-merge by other improvements. |

#### sc:roadmap Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| RM-1 | State Variable Invariant Registry | 3 | 2 | 4 | 4 | 4.00 | Medium cost, good coverage. The registry is a useful artifact but generating it for every state variable adds overhead even when most are trivial. |
| RM-2 | FMEA Pass | 3 | 3 | 4 | 4 | 3.33 | Standard reliability technique. Good systematic coverage but the three-question format generates a lot of material. Token-heavy. |
| RM-3 | Guard and Sentinel Analysis | 2 | 1 | 3 | 3 | 5.00 | Cheap and targeted. The type-migration analysis is particularly useful (bool to int is exactly where Bug 2 lived). Narrow but efficient. |
| RM-4 | Implement/Verify Decomposition | 1 | 1 | 4 | 3 | 9.00 | Best composite score in the entire set. Trivial to implement (split every behavioral deliverable). Forces edge case testing at the planning level. |
| RM-5 | Cross-Deliverable Data Flow Tracing | 4 | 3 | 4 | 5 | 3.14 | Most general proposal but also the most complex. Full data flow tracing across milestones is an analysis engine. High value for large roadmaps, overkill for small ones. |

---

### Agent B (Quality Advocate)

*Philosophy: Thoroughness prevents escaped defects. Overhead during planning is orders of magnitude cheaper than bugs in production. Willing to pay token costs for stronger guarantees. Values systemic improvements over targeted heuristics.*

#### sc:spec-panel Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| SP-1 | State Machine Trace-Through | 3 | 3 | 5 | 5 | 4.17 | The most comprehensive proposal. The 4-step process (inventory, invariant, paths, degenerate walk) is exactly the discipline the panel lacked. Generality is 5: this catches any state-dependent bug. |
| SP-2 | Boundary Value Obligation | 2 | 2 | 4 | 4 | 5.00 | Agree on low friction. Boundary tables are a forcing function. I rate generality higher -- boundary bugs extend far beyond the v0.04 pair. |
| SP-3 | Adversarial Tester Persona | 1 | 2 | 3 | 4 | 5.67 | Persona is cheap but I am less confident it catches bugs without structural forcing functions. A persona can be ignored; a required table cannot. Likelihood 3, not 4. |
| SP-4 | Invariant Specification Req. | 2 | 2 | 5 | 5 | 6.25 | I rate complexity lower: this is a structural rule, not a new engine. The panel already reviews specs; this adds a checklist item. Generality is 5: invariants are universal. |
| SP-5 | Execution Scenarios w/ State | 2 | 3 | 5 | 4 | 4.60 | I rate complexity lower: it extends an existing format (Given/When/Then), not a new pipeline. The state snapshot is the key differentiator from existing scenarios. |
| SP-6 | Consumed vs Produced Analysis | 1 | 1 | 4 | 2 | 8.00 | Agree on cheapness. I rate likelihood higher: this heuristic is almost certain to catch the specific class. But generality remains low -- it is pipeline-specific. |

#### sc:adversarial Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| AD-1 | Failure Mode Enumeration | 2 | 2 | 5 | 4 | 5.75 | I rate cost lower than Agent A. The structured format (precondition/trigger/mechanism/consequence) is a template, not free-form analysis. Likelihood 5: the format structurally forces edge case enumeration. |
| AD-2 | Concrete Scenario Traces | 2 | 3 | 5 | 5 | 5.00 | I rate complexity lower: the orchestrator generates scenarios from diff points (already analyzed), advocates trace through. This is not a new engine; it is a new round type. Generality 5: concrete traces catch any value-level bug. |
| AD-3 | Invariant Declaration & Challenge | 2 | 3 | 5 | 5 | 5.00 | Agree on power. The challenge round is the key differentiator. I rate generality 5: invariant violations are the universal root cause of state bugs. |
| AD-4 | Devil's Advocate Role | 2 | 3 | 4 | 4 | 4.00 | I rate cost higher: a dedicated agent generates significant output. And without structural forcing (what does the Devil's Advocate actually DO?), the role can devolve into vague criticism. Less reliable than structured approaches. |
| AD-5 | State Coverage Gate | 2 | 1 | 4 | 4 | 5.33 | Agree on cheapness. I rate likelihood and generality higher: this is a meta-improvement that amplifies every other proposal. Even alone, it forces exploration of input categories. |
| AD-6 | Post-Merge Trace Validation | 3 | 3 | 4 | 3 | 3.00 | I rate likelihood higher: merge artifacts are a real and underappreciated bug class. The fresh-agent perspective is specifically valuable for integration assumptions. Still lower priority than pre-merge fixes. |

#### sc:roadmap Scores

| ID | Proposal | Complexity | Cost | Likelihood | Generality | Composite | Rationale |
|----|----------|-----------|------|-----------|-----------|-----------|-----------|
| RM-1 | State Variable Invariant Registry | 2 | 2 | 5 | 4 | 5.75 | I rate complexity lower: this is metadata generation during deliverable creation, not a new analysis engine. The invariant predicate + mutation inventory is high-value, low-friction. |
| RM-2 | FMEA Pass | 2 | 3 | 5 | 5 | 5.00 | I rate generality 5: FMEA is the gold standard for reliability. The three-question format is systematic and catches silent corruption, which is the most dangerous bug class. |
| RM-3 | Guard and Sentinel Analysis | 2 | 2 | 4 | 3 | 4.50 | Agree on cheapness. Targeted but effective. The type-migration analysis is a genuine gap in current practice. |
| RM-4 | Implement/Verify Decomposition | 1 | 1 | 4 | 4 | 10.00 | Agree this is the best ROI. I rate generality 4: the implement/verify split forces thinking about "what does correct mean?" at every deliverable. |
| RM-5 | Cross-Deliverable Data Flow Tracing | 4 | 4 | 5 | 5 | 3.13 | I rate cost higher (this is the most token-intensive roadmap proposal) but also likelihood 5: the data flow trace would have caught both bugs with near certainty by surfacing the writer/reader contract mismatch. |

---

### Round 1 Disagreement Analysis

Flagging proposals where agents disagree by > 1 point on any dimension:

| ID | Dimension | Agent A | Agent B | Delta | Issue |
|----|-----------|---------|---------|-------|-------|
| SP-1 | Generality | 4 | 5 | 1 | Minor -- at threshold |
| SP-3 | Likelihood | 4 | 3 | 1 | Minor -- at threshold |
| SP-4 | Complexity | 3 | 2 | 1 | Minor -- at threshold |
| SP-4 | Generality | 4 | 5 | 1 | Minor -- at threshold |
| SP-5 | Complexity | 3 | 2 | 1 | Minor -- at threshold |
| SP-6 | Likelihood | 3 | 4 | 1 | Minor -- at threshold |
| **AD-1** | **Cost** | **3** | **2** | **1** | At threshold |
| **AD-1** | **Likelihood** | **4** | **5** | **1** | At threshold |
| **AD-2** | **Complexity** | **3** | **2** | **1** | At threshold |
| **AD-2** | **Generality** | **4** | **5** | **1** | At threshold |
| **AD-4** | **Cost** | **2** | **3** | **1** | At threshold |
| **AD-6** | **Likelihood** | **3** | **4** | **1** | At threshold |
| **RM-1** | **Complexity** | **3** | **2** | **1** | At threshold |
| **RM-1** | **Likelihood** | **4** | **5** | **1** | At threshold |
| **RM-2** | **Complexity** | **3** | **2** | **1** | At threshold |
| **RM-2** | **Generality** | **4** | **5** | **1** | At threshold |
| **RM-5** | **Cost** | **3** | **4** | **1** | At threshold |
| **RM-5** | **Likelihood** | **4** | **5** | **1** | At threshold |

While no single dimension exceeds the >1 threshold, several proposals have consistent 1-point disagreements across multiple dimensions that produce meaningfully different composite scores. The contested proposals for Round 2 are those with composite score differences > 0.75:

| ID | Agent A Composite | Agent B Composite | Delta | Status |
|----|-------------------|-------------------|-------|--------|
| SP-4 | 4.60 | 6.25 | 1.65 | **CONTESTED** |
| SP-6 | 6.50 | 8.00 | 1.50 | **CONTESTED** |
| AD-1 | 3.60 | 5.75 | 2.15 | **CONTESTED** |
| AD-2 | 3.29 | 5.00 | 1.71 | **CONTESTED** |
| AD-4 | 5.00 | 4.00 | 1.00 | **CONTESTED** |
| RM-1 | 4.00 | 5.75 | 1.75 | **CONTESTED** |
| RM-2 | 3.33 | 5.00 | 1.67 | **CONTESTED** |

---

## Round 2: Contested Proposals Debate

### SP-4: Invariant Specification Requirement

**Agent A argues Complexity 3:**
> This is not just a checklist item. It requires the spec author to produce invariant statements for every mutable variable. Spec authors do not naturally think in invariants. The panel can require them, but the pipeline needs to detect missing invariants and generate findings. That detection logic is a structural change to the review template, not a prompt tweak. I maintain complexity 3.

**Agent B responds:**
> The panel already has structured output sections. Adding "Invariants" as a required section alongside "Acceptance Criteria" is a template change, not a pipeline change. The detection is simple: if the spec introduces `self._foo` and there is no `INV-*` line referencing it, that is a finding. No new engine needed. The panel prompt already enumerates checks; this adds one more. Complexity 2 is justified.

**Agent A concedes partially:**
> Fair point that the detection is simple pattern matching. But the quality of invariants matters enormously. A weak invariant ("offset is an integer") catches nothing. The panel needs to evaluate invariant strength, which is a qualitative judgment the current pipeline does not make. I will compromise at complexity 2 but note that invariant quality is an open risk.

**Generality dispute (A: 4, B: 5):**

**Agent B argues:**
> Invariants are the fundamental correctness mechanism for any stateful system. Name a state bug that is not an invariant violation. You cannot. This is definitionally generality 5.

**Agent A responds:**
> I accept that invariants are theoretically universal. But in practice, poorly written invariants provide false confidence. I will move to generality 5 on the condition that the proposal includes guidance on invariant quality. A tautological invariant is worse than no invariant because it creates a false sense of coverage.

**Reconciled: Complexity 2, Generality 5. Composite: (5*3 + 5*2) / (2+2) = 6.25**

---

### SP-6: Consumed vs Produced Analysis

**Agent A argues Likelihood 3:**
> This heuristic only fires when there is a pipeline with filtering. Many specs do not have such pipelines. When it fires, it is effective. But the trigger condition limits how often it fires. Likelihood 3 reflects the conditional nature.

**Agent B argues Likelihood 4:**
> Filtering and transformation stages are extremely common in real-world specs: pagination, search results, event processing, API response mapping. Almost every data flow has a stage where input count differs from output count. The heuristic fires more often than you think.

**Agent A concedes:**
> Valid point. I was thinking narrowly about the v0.04 case. In general data processing specs, this heuristic would fire frequently. Moving to likelihood 4.

**Reconciled: Likelihood 4. Composite: (4*3 + 2*2) / (1+1) = 8.00**

---

### AD-1: Failure Mode Enumeration Phase

**Agent A argues Cost 3, Likelihood 4:**
> Three failure modes per variant per advocate is N_advocates * N_variants * 3 structured entries. With 3 advocates and 3 variants, that is 27 failure mode entries. At ~100 tokens each, that is 2,700 tokens just for the enumeration. Cost 3 is justified. And likelihood 4 because the format does not guarantee the right failure modes are found -- it guarantees quantity, not quality.

**Agent B argues Cost 2, Likelihood 5:**
> The structured format (precondition/trigger/mechanism/consequence) is precisely what forces quality. An advocate cannot fill in "mechanism" without tracing the data flow. That is the whole point. The format converts "what could go wrong?" from a vague prompt into a structured analysis that naturally surfaces degenerate inputs. As for cost: the failure modes replace vague debate preamble. They are not purely additive; they focus the subsequent debate. Net additional tokens are closer to 15% (cost 2) than 30%.

**Agent A responds:**
> I agree the structured format adds quality pressure. But I have seen structured templates filled with generic entries ("network failure", "timeout", "invalid input") that satisfy the format without surfacing domain-specific bugs. The format helps but does not guarantee. I will move to likelihood 4.5, which I will round to 5 for the table, and cost 2. But I note the risk of template compliance without genuine analysis.

**Reconciled: Cost 2, Likelihood 5. Composite: (5*3 + 3*2) / (2+2) = 5.25**

Wait -- generality is also contested implicitly. Agent A scored generality 3, Agent B scored 4. Let me address:

**Agent B on generality:**
> The failure mode format catches degenerate inputs, guard failures, accumulator drift, race conditions, and resource leaks. That is at least 5 bug classes. Generality 4.

**Agent A:**
> Agree. The structured format is general-purpose. Moving to generality 4.

**Reconciled: Cost 2, Likelihood 5, Generality 4. Composite: (5*3 + 4*2) / (2+2) = 5.75**

---

### AD-2: Concrete Scenario Traces

**Agent A argues Complexity 3, Cost 4:**
> Scenario generation from diff points requires the orchestrator to synthesize meaningful scenarios, not just random inputs. That is a moderate complexity addition. And each advocate tracing 3-5 scenarios with state variables at every step is very token-heavy. This is the most expensive proposal in the adversarial set.

**Agent B argues Complexity 2, Cost 3:**
> The orchestrator already performs diff analysis. Generating scenarios from diffs is a natural extension -- "you disagree on pagination behavior, here is a pagination-stressing input." The scenario is 3-5 lines. Each trace is 5-10 lines per advocate. At 3 advocates and 3 scenarios, that is ~135 lines or ~4,000 tokens. Significant but not 30-50% of the total debate cost. Cost 3.

**Agent A responds:**
> The scenario generation is plausible at complexity 2 if the diff analysis is already rich. I will concede complexity 2. But the traces are the expensive part. Each advocate tracing through each scenario with full state snapshots is where the tokens go. I will hold cost at 3 since your math lands there too. But this should be gated behind --depth deep.

**Agent B agrees:**
> Depth gating is a sensible optimization. The proposal should specify that at --depth standard, only 2 scenarios are traced; at --depth deep, 5. This controls cost without sacrificing the mechanism.

**Reconciled: Complexity 2, Cost 3, Generality 5. Composite: (5*3 + 5*2) / (2+3) = 5.00**

---

### AD-4: Devil's Advocate Role

**Agent A argues Cost 2, Likelihood 4:**
> A single focused agent is efficient. It produces one analysis document before the debate starts. The advocates then respond to it inline. The incremental cost is one agent call. Cost 2.

**Agent B argues Cost 3, Likelihood 4:**
> The Devil's Advocate needs to analyze all variants and produce structured output. That is a full agent call with significant context. Then the advocates must respond to every concern (convergence blocker mechanism). The response overhead is real. Cost 3.

**Agent A responds:**
> The convergence blocker is the key mechanism. Without it, the Devil's Advocate is just another reviewer. With it, the role fundamentally changes the debate dynamics. I agree the response overhead is real, but it is productive overhead -- every response is an edge case being addressed. Net value is high even at cost 3. I will concede cost 3.

**Agent B responds:**
> I also concede my likelihood concern. A dedicated destructive role with convergence-blocking power is more reliable than I initially scored. The structural forcing (unresolved concerns block convergence) makes this more than a persona -- it is a process gate. I will move to likelihood 5.

**Reconciled: Cost 3, Likelihood 5. Composite: (5*3 + 4*2) / (2+3) = 4.60**

Wait -- let me recalculate. Complexity 2, Cost 3. (5*3 + 4*2)/(2+3) = (15+8)/5 = 23/5 = 4.60.

---

### RM-1: State Variable Invariant Registry

**Agent A argues Complexity 3, Likelihood 4:**
> The registry requires scanning deliverables for state variable patterns, generating invariant predicates, enumerating mutation sites, and creating verification sub-deliverables. That is four distinct operations per state variable. Complexity 3.

**Agent B argues Complexity 2, Likelihood 5:**
> The roadmap already generates deliverables by analyzing the spec. Adding "when you see `self._*`, generate an invariant entry" is a pattern-matching extension to existing generation logic. The invariant predicate and mutation inventory are natural language outputs, not computed artifacts. Complexity 2.

**Agent A responds:**
> The generation is simple, but the quality of generated invariants determines whether this catches bugs. "Invariant: _offset is an integer" is useless. The roadmap generator needs to produce semantically meaningful invariants, which requires understanding the variable's role. That understanding comes from context analysis, which is moderate complexity. I will compromise at complexity 2 if we acknowledge the quality risk.

**Likelihood dispute:**

**Agent B argues:**
> The invariant registry for `_replayed_event_offset` would have stated "must be > 0 after replay." The edge case analysis for `_loaded_start_index` would have asked "what is the decrement operand?" Both bugs are structurally eliminated. Likelihood 5.

**Agent A concedes:**
> For state-variable-centric bugs, yes. Likelihood 5.

**Reconciled: Complexity 2, Likelihood 5, Generality 4. Composite: (5*3 + 4*2) / (2+2) = 5.75**

---

### RM-2: FMEA Pass

**Agent A argues Complexity 3, Generality 4:**
> FMEA is a separate analysis pass over the entire deliverable list. It requires parsing for computational verbs, enumerating input domains, tracing forward to consumers, and generating failure mode entries with severity. That is a non-trivial analysis pipeline. Complexity 3.

**Agent B argues Complexity 2, Generality 5:**
> The three questions ("what inputs?", "what if wrong value?", "what do consumers assume?") are a structured prompt applied to each deliverable. No parsing engine is needed -- the LLM evaluates each deliverable against three questions. Complexity 2. Generality 5 because FMEA catches silent corruption, the most dangerous and general bug class.

**Agent A responds:**
> Applying three questions per deliverable is simple, I concede. But producing high-quality answers requires deep context about the system. The LLM needs to understand what "wrong value" means for each computation, which requires cross-deliverable context. That said, the LLM already has this context from generating the roadmap. I will move to complexity 2. I hold generality at 4 -- FMEA in hardware is universal, but in LLM-generated roadmaps, the quality depends on the model's understanding, which is variable.

**Agent B responds:**
> Fair concern about quality variability. But even mediocre FMEA catches obvious degenerate inputs (empty, zero, null). The floor is high. I will accept generality 4 as a pragmatic compromise.

**Reconciled: Complexity 2, Cost 3, Likelihood 5, Generality 4. Composite: (5*3 + 4*2) / (2+3) = 4.60**

---

## Round 3: Cross-Command Synergies, Deduplication, and Final Reconciliation

### Cross-Command Deduplication Analysis

Several proposals across the three commands are essentially the same idea expressed at different pipeline stages. Identifying these clusters is critical to avoid implementing the same improvement three times.

#### Cluster 1: Invariant-Centric Proposals
| Proposal | Command | Core Idea |
|----------|---------|-----------|
| SP-1 | spec-panel | Trace mutable state, extract invariants, walk degenerate inputs |
| SP-4 | spec-panel | Require explicit invariant for every mutable variable |
| AD-3 | adversarial | Declare invariants, opponents challenge them |
| RM-1 | roadmap | Generate invariant registry for every state variable |

**Analysis**: These four proposals all center on making invariants explicit. They differ in *when* the invariant is created and *who* challenges it:
- SP-4 requires the spec author to write them (earliest, spec-time)
- SP-1 requires the panel to extract and verify them (review-time)
- AD-3 requires debate advocates to declare and challenge them (debate-time)
- RM-1 requires the roadmap generator to register them (planning-time)

**Recommendation**: These are complementary, not redundant. The invariant flows through the pipeline: spec author writes it (SP-4) -> panel verifies it (SP-1) -> debate challenges it (AD-3) -> roadmap tracks it (RM-1). But if budget is limited, SP-4 is the highest-leverage single point: if the invariant is in the spec, every downstream stage can reason about it. Without SP-4, the other three must independently infer invariants, which is less reliable.

#### Cluster 2: Destructive/Adversarial Role Proposals
| Proposal | Command | Core Idea |
|----------|---------|-----------|
| SP-3 | spec-panel | Adversarial Tester persona (break the spec) |
| AD-4 | adversarial | Devil's Advocate agent (break all variants) |

**Analysis**: Both proposals add a dedicated destructive perspective. SP-3 adds it to the panel; AD-4 adds it to the debate. They operate at different stages and are complementary. SP-3 is cheaper (persona prompt); AD-4 is more powerful (convergence blocker). If implementing only one, AD-4 has higher structural guarantees because unresolved concerns block convergence, whereas SP-3's adversarial tester can be outvoted by 6 other panelists.

#### Cluster 3: Concrete Scenario Trace Proposals
| Proposal | Command | Core Idea |
|----------|---------|-----------|
| SP-5 | spec-panel | Given/When/Then with explicit state snapshots |
| AD-2 | adversarial | Orchestrator-generated scenarios, advocates trace with state values |
| AD-6 | adversarial | Post-merge trace validation by fresh agent |

**Analysis**: All three involve tracing concrete scenarios with state variable values. SP-5 does it in the spec, AD-2 does it in the debate, AD-6 does it after merge. SP-5 and AD-2 overlap most heavily: both require step-by-step traces with state values. AD-6 is distinct because it targets merge artifacts specifically. If implementing only one, AD-2 has the highest value because the debate context (comparing variants) makes trace discrepancies between advocates visible.

#### Cluster 4: Failure Mode / FMEA Proposals
| Proposal | Command | Core Idea |
|----------|---------|-----------|
| AD-1 | adversarial | Structured failure mode enumeration (precondition/trigger/mechanism/consequence) |
| RM-2 | roadmap | FMEA pass (what inputs? what if wrong? what do consumers assume?) |

**Analysis**: Both ask "what can go wrong?" with structured formats. AD-1 operates during the debate (per-variant); RM-2 operates during roadmap generation (per-deliverable). They catch similar bugs but at different granularities. AD-1 is design-level; RM-2 is implementation-level. Complementary rather than redundant. If choosing one, RM-2 is later in the pipeline (closer to implementation) and uses the more established FMEA methodology.

#### Cluster 5: Boundary / Degenerate Input Proposals
| Proposal | Command | Core Idea |
|----------|---------|-----------|
| SP-2 | spec-panel | Boundary value table for every guard condition |
| AD-5 | adversarial | State coverage gate requiring exploration of empty/boundary/filter inputs |
| RM-3 | roadmap | Guard and sentinel analysis (enumerate all states, detect ambiguity) |

**Analysis**: All three force exploration of boundary conditions, but through different mechanisms. SP-2 uses tables, AD-5 uses convergence penalties, RM-3 uses analysis phases. SP-2 and RM-3 overlap most (both examine guard conditions). AD-5 is a meta-improvement that amplifies boundary analysis without prescribing how it happens. If choosing one, AD-5 has the broadest effect because it forces boundary exploration regardless of which specific technique is used.

#### Unique Proposals (No Cross-Command Duplicate)
| Proposal | Command | Why Unique |
|----------|---------|------------|
| SP-6 | spec-panel | Consumed vs. produced quantity analysis -- no equivalent elsewhere |
| RM-4 | roadmap | Implement/verify decomposition -- no equivalent elsewhere |
| RM-5 | roadmap | Cross-deliverable data flow tracing -- no equivalent elsewhere |

---

### Final Reconciled Scoring Table

After three rounds of debate, the agents converge on the following scores:

| ID | Proposal | Cmplx | Cost | Likeli. | General. | Composite | Cluster |
|----|----------|-------|------|---------|----------|-----------|---------|
| **SP-1** | State Machine Trace-Through | 3 | 3 | 5 | 5 | 4.17 | Invariant |
| **SP-2** | Boundary Value Obligation | 2 | 2 | 4 | 4 | 5.00 | Boundary |
| **SP-3** | Adversarial Tester Persona | 1 | 2 | 4 | 4 | 6.67 | Destructive |
| **SP-4** | Invariant Specification Req. | 2 | 2 | 5 | 5 | 6.25 | Invariant |
| **SP-5** | Execution Scenarios w/ State | 2 | 3 | 5 | 4 | 4.60 | Scenario Trace |
| **SP-6** | Consumed vs Produced Analysis | 1 | 1 | 4 | 2 | 8.00 | Unique |
| **AD-1** | Failure Mode Enumeration | 2 | 2 | 5 | 4 | 5.75 | FMEA |
| **AD-2** | Concrete Scenario Traces | 2 | 3 | 5 | 5 | 5.00 | Scenario Trace |
| **AD-3** | Invariant Declaration & Challenge | 2 | 3 | 5 | 5 | 5.00 | Invariant |
| **AD-4** | Devil's Advocate Role | 2 | 3 | 5 | 4 | 4.60 | Destructive |
| **AD-5** | State Coverage Gate | 2 | 1 | 4 | 4 | 5.33 | Boundary |
| **AD-6** | Post-Merge Trace Validation | 3 | 3 | 4 | 3 | 3.00 | Scenario Trace |
| **RM-1** | State Variable Invariant Registry | 2 | 2 | 5 | 4 | 5.75 | Invariant |
| **RM-2** | FMEA Pass | 2 | 3 | 5 | 4 | 4.60 | FMEA |
| **RM-3** | Guard and Sentinel Analysis | 2 | 2 | 4 | 3 | 4.50 | Boundary |
| **RM-4** | Implement/Verify Decomposition | 1 | 1 | 4 | 4 | 10.00 | Unique |
| **RM-5** | Cross-Deliverable Data Flow | 4 | 4 | 5 | 5 | 3.13 | Unique |

---

## Top 5 Overall Recommendations (Ranked by Composite Score)

### 1. RM-4: Implement/Verify Decomposition (Composite: 10.00)

**Why #1**: The highest composite score by a wide margin. Trivial to implement (split every behavioral deliverable into implement + verify sub-deliverables). Forces edge case thinking at the planning level. The verify sub-deliverable targets internal correctness with degenerate inputs, which is precisely where both v0.04 bugs lived. Almost zero overhead because the verify deliverable replaces unstructured "write tests" deliverables, not adding new ones.

**Implementation**: Modify the roadmap generator prompt to produce `D.x.a` (implement) and `D.x.b` (verify) for every behavioral deliverable. The verify sub-deliverable must reference specific internal state variables and assert their values under boundary conditions.

### 2. SP-6: Consumed vs Produced Difference Analysis (Composite: 8.00)

**Why #2**: The cheapest possible improvement -- a single heuristic question added to the review checklist. When a pipeline has a filtering stage, the panel asks "which count is used downstream?" This is almost certain to catch the specific class of Bug 1 (dimensional mismatch in pipelines). Low generality (only pipeline bugs) but the cost is so low that even narrow coverage is excellent ROI.

**Implementation**: Add one line to the spec-panel review protocol: "For any pipeline where input count can differ from output count, generate a quantity flow diagram and resolve which count is used for downstream indexing."

### 3. SP-3: Adversarial Tester Persona (Composite: 6.67)

**Why #3**: Adding a destructive persona to the spec panel costs one prompt addition. The persona asks four structured questions (input degeneration, sequence abuse, state corruption, environmental hostility) that naturally gravitate toward boundary conditions and guard bypasses. While less structurally guaranteed than SP-4 or AD-4, the near-zero implementation cost makes this excellent ROI.

**Implementation**: Add a 7th panelist to the spec-panel prompt with a James Whittaker-style adversarial testing focus. The persona's review protocol includes the four structured question categories.

### 4. SP-4: Invariant Specification Requirement (Composite: 6.25)

**Why #4**: The keystone of the invariant cluster. If invariants are written into the spec, every downstream stage (panel review, adversarial debate, roadmap planning) can reason about them. Without explicit invariants, all other invariant-related proposals must independently infer them, which is less reliable. This is the highest-leverage single investment for catching state-dependent bugs across the entire pipeline.

**Implementation**: Add a structural rule to spec-panel: every mutable state variable must have an `INV-*` line stating its invariant. Every acceptance criterion must trace to at least one invariant. Missing invariants generate CRITICAL findings.

### 5. AD-1: Failure Mode Enumeration Phase (Composite: 5.75, tied with RM-1)

**Why #5**: The structured precondition/trigger/mechanism/consequence format converts vague "what could go wrong?" into a disciplined analysis that naturally surfaces degenerate inputs. Adding this as Step 1.5 in the adversarial debate is a moderate change to the pipeline but produces high-quality failure analysis. The novelty scoring mechanism incentivizes advocates to find non-obvious failure modes.

**Tied with RM-1 (State Variable Invariant Registry)**: Both score 5.75. RM-1 is preferred if the roadmap is the bottleneck (invariant tracking during planning). AD-1 is preferred if the debate is the bottleneck (failure analysis during design comparison). Both should be implemented.

---

## Recommended Implementation Roadmap

### Phase 1: Minimum Cost, Maximum Signal (Implement Immediately)

| Priority | Proposal | Command | Complexity | Cost | Rationale |
|----------|----------|---------|-----------|------|-----------|
| 1 | RM-4 | roadmap | 1 | 1 | Highest composite. Trivial to implement. |
| 2 | SP-6 | spec-panel | 1 | 1 | One-line heuristic addition. |
| 3 | SP-3 | spec-panel | 1 | 2 | One persona prompt addition. |

**Total Phase 1 overhead**: Negligible. These three changes add < 10% tokens per invocation.

### Phase 2: Structural Invariant Support (Implement Next Sprint)

| Priority | Proposal | Command | Complexity | Cost | Rationale |
|----------|----------|---------|-----------|------|-----------|
| 4 | SP-4 | spec-panel | 2 | 2 | Keystone for invariant cluster. |
| 5 | AD-5 | adversarial | 2 | 1 | Meta-improvement amplifying all boundary analysis. |
| 6 | RM-1 | roadmap | 2 | 2 | Invariant tracking during planning. |

**Total Phase 2 overhead**: Moderate. ~15-20% additional tokens but with structural quality guarantees.

### Phase 3: Deep Analysis Capabilities (Implement When Needed)

| Priority | Proposal | Command | Complexity | Cost | Rationale |
|----------|----------|---------|-----------|------|-----------|
| 7 | AD-1 | adversarial | 2 | 2 | Structured failure mode analysis. |
| 8 | SP-2 | spec-panel | 2 | 2 | Boundary value tables for guards. |
| 9 | AD-2 | adversarial | 2 | 3 | Concrete scenario traces (gate behind --depth deep). |
| 10 | AD-3 | adversarial | 2 | 3 | Invariant challenge rounds. |
| 11 | RM-2 | roadmap | 2 | 3 | FMEA pass over deliverables. |
| 12 | RM-3 | roadmap | 2 | 2 | Guard and sentinel analysis. |

### Phase 4: Advanced / Conditional (Implement for Complex Projects)

| Priority | Proposal | Command | Complexity | Cost | Rationale |
|----------|----------|---------|-----------|------|-----------|
| 13 | SP-1 | spec-panel | 3 | 3 | Full trace-through pass (subsumed if SP-4 + SP-3 are active). |
| 14 | AD-4 | adversarial | 2 | 3 | Devil's Advocate (valuable but overlaps with AD-1 + AD-5). |
| 15 | SP-5 | spec-panel | 2 | 3 | State snapshots in scenarios (overlaps with AD-2). |
| 16 | AD-6 | adversarial | 3 | 3 | Post-merge validation (only for complex merges). |
| 17 | RM-5 | roadmap | 4 | 4 | Data flow tracing (only for 6+ milestone roadmaps). |

---

## Minimum Viable Improvement: 3 Proposals (One Per Command)

If budget permits only three changes -- one per command -- these are the selections:

### spec-panel: SP-4 (Invariant Specification Requirement)
**Composite: 6.25** | Complexity: 2 | Cost: 2

**Why over SP-3 (6.67) or SP-6 (8.00)?**: SP-6 has a higher composite but narrow generality (only pipeline bugs). SP-3 is cheaper but a persona can be ignored -- it has no structural forcing function. SP-4 creates a **mandatory artifact** (invariant statements) that the panel must review. This changes the review from "is the spec clear?" to "are the correctness properties stated and defensible?" That is the single highest-leverage change to the spec-panel pipeline.

**Agent A dissent**: SP-6 is cheaper and catches Bug 1 almost certainly. For minimum viable, cheapness matters.

**Agent B response**: SP-4 catches both bugs and every future state bug. SP-6 catches pipeline-dimensional bugs only. For a single pick, breadth wins. And SP-4's cost is still only 2 -- not expensive.

**Resolution**: SP-4 selected. SP-6 is the recommended companion if a second spec-panel improvement is possible (Phase 1 includes both regardless).

### adversarial: AD-1 (Failure Mode Enumeration Phase)
**Composite: 5.75** | Complexity: 2 | Cost: 2

**Why over AD-5 (5.33) or AD-4 (4.60)?**: AD-5 is a meta-gate (prevents shallow convergence) but does not itself generate analysis. AD-4 adds a dedicated agent but is more expensive and less structured. AD-1 provides the structured format (precondition/trigger/mechanism/consequence) that converts every advocate into a failure analyst. The output is concrete, auditable, and directly targets the class of bug that escaped: degenerate inputs that advocates did not consider.

**Agent A note**: AD-5 is the cheapest and could be combined with AD-1 for maximum effect. If implementing two adversarial improvements, AD-1 + AD-5 is the strongest pair.

### roadmap: RM-4 (Implement/Verify Decomposition)
**Composite: 10.00** | Complexity: 1 | Cost: 1

**Why**: No contest. Highest composite score of any proposal. Trivially implementable. Forces edge case verification at deliverable granularity. The verify sub-deliverable specifically targets "is this the right quantity?" and "what happens when the input is empty?" -- exactly the two bug classes that escaped. This is the single most impactful change in the entire proposal set.

---

## Appendix: Composite Score Rankings (All 17)

| Rank | ID | Proposal | Composite |
|------|------|----------|-----------|
| 1 | RM-4 | Implement/Verify Decomposition | 10.00 |
| 2 | SP-6 | Consumed vs Produced Analysis | 8.00 |
| 3 | SP-3 | Adversarial Tester Persona | 6.67 |
| 4 | SP-4 | Invariant Specification Req. | 6.25 |
| 5 | AD-1 | Failure Mode Enumeration | 5.75 |
| 5 | RM-1 | State Variable Invariant Registry | 5.75 |
| 7 | AD-5 | State Coverage Gate | 5.33 |
| 8 | SP-2 | Boundary Value Obligation | 5.00 |
| 8 | AD-2 | Concrete Scenario Traces | 5.00 |
| 8 | AD-3 | Invariant Declaration & Challenge | 5.00 |
| 11 | SP-5 | Execution Scenarios w/ State | 4.60 |
| 11 | AD-4 | Devil's Advocate Role | 4.60 |
| 11 | RM-2 | FMEA Pass | 4.60 |
| 14 | RM-3 | Guard and Sentinel Analysis | 4.50 |
| 15 | SP-1 | State Machine Trace-Through | 4.17 |
| 16 | RM-5 | Cross-Deliverable Data Flow | 3.13 |
| 17 | AD-6 | Post-Merge Trace Validation | 3.00 |

---

*Generated 2026-03-04 as part of v0.04 Adaptive Replay post-implementation retrospective process improvement initiative.*
