# Base Selection: Roadmap CLI Spec vs Tasklist Integration Strategies

## Quantitative Scoring (50% weight)

### Metric Computation

| Metric | Weight | Variant A (roadmap-cli-spec) | Variant B (tasklist-strategies) | Notes |
|--------|--------|------------------------------|--------------------------------|-------|
| **Requirement Coverage (RC)** | 0.30 | **0.95** — 15 FR, 7 NFR, 7 AC explicitly enumerated; maps to architecture, CLI, failure policy, test plan | **0.40** — No formal requirement IDs; 5 strategies with "Concrete spec changes" but references external spec | A has formal reqs; B patches external spec |
| **Internal Consistency (IC)** | 0.25 | **0.92** — 2 minor tensions: gate_passed() described in §3.2 and §13.5 with slight wording variance; test architecture section references "20+" files but lists 19 | **0.95** — Highly consistent; each strategy's "What was rejected" aligns with debate verdicts; v1.1 deferral table consistent with rejection rationale | B is shorter, easier to keep consistent |
| **Specificity Ratio (SR)** | 0.15 | **0.88** — Concrete: 300s/600s/900s timeouts, SHA-256, min_lines thresholds, Python dataclass fields, exact file paths. Vague: "meaningful" (1), "appropriate" (0) | **0.72** — Concrete: prohibited verb list, "≥1 and ≤25 tasks", "0 bytes or whitespace-only". Vague: "properly formatted", "quality", "worst offenders" (3+ instances) | A is more numerically specific |
| **Dependency Completeness (DC)** | 0.15 | **0.95** — Section cross-refs resolve: §3.2→§13.5, §6→§7.3, FR-01→§4, NFR-01→AC-06; code imports reference correct modules | **0.80** — References external "sc-tasklist-command-spec-v1.0.md" sections (§5.4, §6.2, §6A, §6B.2, §7, §8, §8.1); references debate artifacts not included | B depends on external docs |
| **Section Coverage (SC)** | 0.15 | **1.00** — 13 top-level sections (max) | **0.46** — 6 top-level sections | A is structurally comprehensive |

**Quantitative Score Calculation**:

| Variant | RC×0.30 | IC×0.25 | SR×0.15 | DC×0.15 | SC×0.15 | **quant_score** |
|---------|---------|---------|---------|---------|---------|-----------------|
| A | 0.285 | 0.230 | 0.132 | 0.143 | 0.150 | **0.940** |
| B | 0.120 | 0.238 | 0.108 | 0.120 | 0.069 | **0.655** |

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements from source input | **MET** — 15 FR + 7 NFR enumerated with traceability | **NOT MET** — Patches external spec; requirements not self-contained |
| 2 | Addresses edge cases and failure scenarios | **MET** — §6 failure policy, §6.2 HALT output, stale-spec, cross-cancel | **MET** — Circular dependency detection, empty-file guard, orphaned clarifications |
| 3 | Includes dependencies and prerequisites | **MET** — Step inputs list, pipeline/ extraction order, sprint migration sequence | **MET** — Patch order with dependency reasoning; "enforcement mechanism first" |
| 4 | Defines success/completion criteria | **MET** — 7 acceptance criteria (AC-01 through AC-07) | **NOT MET** — No explicit acceptance criteria; "estimated effort ~3 hours" but no completion definition |
| 5 | Specifies what is explicitly out of scope | **MET** — §2 "Out of Scope (v1)" with 5 items | **MET** — v1.1 deferral table with 6 items and debate provenance |

**Completeness**: A = 5/5, B = 3/5

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | **MET** — Technical claims verifiable (threading.Event, subprocess.Popen, SHA-256, Click) | **MET** — Debate verdicts consistent with referenced debate artifacts |
| 2 | Technical approaches are feasible | **MET** — `gate_passed()` pure Python, `StepRunner` Protocol, threading model all standard patterns | **MET** — TodoWrite integration, prohibited verb rules, task count bounds all implementable |
| 3 | Terminology used consistently | **MET** — "gate", "step", "conductor", "pipeline" used consistently throughout | **MET** — "parity", "v1.0", "tier-proportional" used consistently |
| 4 | No internal contradictions | **NOT MET** — Minor: §3.2 says `gate` field is `GateCriteria` but §13.5 says `GateCriteria | None` (resolved in §13.5 but §3.2 not updated) | **MET** — No contradictions found |
| 5 | Claims supported by evidence or rationale | **MET** — Timeout rationale, concurrency model rationale, migration strategy rationale all present | **MET** — Every "What was rejected" has cited debate evidence |

**Correctness**: A = 4/5, B = 5/5

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | **MET** — Problem → Scope → Architecture → Steps → CLI → Failure → FR → NFR → AC → Design | **MET** — Executive Summary → 5 Strategies (ordered by dependency) → Context → Deferral → Patch Order |
| 2 | Consistent hierarchy depth | **MET** — H1→H2→H3→H4 used consistently; no orphaned subsections | **MET** — H1→H2→H3; flatter but consistent |
| 3 | Clear separation of concerns | **MET** — Architecture vs CLI vs Failure vs Design clearly separated | **NOT MET** — "Additional Valuable Context" mixes risks, keep-as-is, and deferred items |
| 4 | Navigation aids present | **MET** — Numbered sections, cross-references (§7.3, FR-01), code blocks as anchors | **NOT MET** — No table of contents, limited cross-references, strategies numbered but not cross-linked |
| 5 | Follows conventions of artifact type | **MET** — Standard spec format: FR/NFR/AC/scope/architecture | **MET** — Standard decision record: verdict table, what/why/how per decision |

**Structure**: A = 5/5, B = 3/5

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | **MET** — Specific: "retry once then halt", "file exists AND non-empty AND line count >= minimum" | **MET** — Specific: "MUST name at least one specific target", prohibited verb list |
| 2 | Concrete rather than abstract | **MET** — Python dataclasses, exact file paths, timeout values in seconds | **MET** — Exact spec section references (§5.4, §6.2), concrete check descriptions |
| 3 | Each section has clear purpose | **MET** — Every section title describes its purpose | **MET** — Every strategy has clear What/Rejected/Changes/Value structure |
| 4 | Acronyms and domain terms defined | **NOT MET** — "YAML" not defined; "StepRunner" introduced without explicit definition until §13.5 | **NOT MET** — "TodoWrite", "Sprint CLI", "TUI" used without definition |
| 5 | Actionable next steps clearly identified | **MET** — §12 Implementation Notes with ordered migration strategy | **MET** — "Revised Spec Patch Order" with time estimates and dependency ordering |

**Clarity**: A = 4/5, B = 4/5

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Identifies ≥3 risks with probability and impact | **NOT MET** — Failure modes identified but no explicit risk register with probability/impact | **NOT MET** — "Risks to address" section lists 3 risks but no probability/impact assessment |
| 2 | Provides mitigation for each identified risk | **MET** — Retry, --resume, cross-cancellation, stale-spec detection all mitigate identified risks | **MET** — Empty-file guard, prohibited verbs, dependency detection all mitigate quality risks |
| 3 | Addresses failure modes and recovery | **MET** — §6 comprehensive failure policy with recovery via --resume | **NOT MET** — No failure recovery mechanism; relies on full re-run |
| 4 | Considers external dependencies and their failure | **MET** — Claude binary availability, subprocess timeout, network interruption addressed | **NOT MET** — No consideration of external dependency failures |
| 5 | Includes monitoring/validation mechanism | **MET** — §7 progress display, .roadmap-state.json, gate validation | **MET** — TodoWrite stage reporting, Generation Notes, pre-write checklist |

**Risk Coverage**: A = 4/5, B = 2/5

---

## Position-Bias Mitigation

### Dual-Pass Results

| Dimension | Variant A (Pass 1→2) | Variant B (Pass 1→2) | Disagreements |
|-----------|---------------------|---------------------|---------------|
| Completeness | 5→5 | 3→3 | 0 |
| Correctness | 4→4 | 5→5 | 0 |
| Structure | 5→5 | 3→3 | 0 |
| Clarity | 4→4 | 4→4 | 0 |
| Risk Coverage | 4→4 | 2→2 | 0 |

No disagreements between passes. Verdicts stable.

---

## Combined Scoring

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 5/5 | 3/5 |
| Correctness | 4/5 | 5/5 |
| Structure | 5/5 | 3/5 |
| Clarity | 4/5 | 4/5 |
| Risk Coverage | 4/5 | 2/5 |
| **Total** | **22/25** | **17/25** |
| **qual_score** | **0.880** | **0.680** |

### Combined Score

| Variant | quant_score | qual_score | Combined (50/50) |
|---------|------------|------------|-------------------|
| **Variant A** | 0.940 | 0.880 | **0.910** |
| **Variant B** | 0.655 | 0.680 | **0.668** |

**Margin**: 0.242 (24.2%) — no tiebreaker needed.

### Debate Performance Cross-Check

| Metric | Variant A | Variant B |
|--------|-----------|-----------|
| Diff points won outright | 4 (C-001, C-003, X-001, U-001) | 3 (C-005, C-009, U-005) |
| Hybrid/agreed points | 3 (C-002, X-002, U-008) | 3 (same) |
| Points lost | 1 (X-003) | 2 (S-001, S-002) |

Consistent with combined scoring — Variant A leads on architectural and structural dimensions.

---

## Selected Base: Variant A (`roadmap-cli-spec.md`)

### Selection Rationale

Variant A is selected as base with **91.0% combined score** (vs 66.8%) for these evidence-based reasons:

1. **Architectural completeness**: Variant A defines the execution model, data models, state management, failure recovery, and test architecture that any merged output requires. Variant B's quality rules need this skeleton to attach to.

2. **Self-contained specification**: Variant A's 15 FR + 7 NFR + 7 AC are fully defined within the document. Variant B patches an external spec and depends on debate artifacts not included.

3. **Trust boundary solution**: Both advocates agree A's external conductor solves the circular self-validation problem that B identifies but concedes is "not fully solved." This is the defining architectural question.

4. **Implementation readiness**: Variant A includes Python dataclasses, function signatures, CLI interface, test directory structure — ready for direct implementation. Variant B requires a second design phase.

### Strengths to Preserve from Base (Variant A)
- External conductor pattern with file-on-disk gates
- `pipeline/` shared module with `PipelineConfig` inheritance hierarchy
- `StepRunner` Protocol for extensibility
- Retry-once-then-halt + `--resume` + stale-spec detection
- Parallel generate with threading + cross-cancellation
- `.roadmap-state.json` state persistence
- Comprehensive test architecture
- 15 FR / 7 NFR / 7 AC traceability

### Strengths to Incorporate from Variant B
1. **Tier-proportional gate enforcement** (U-005): STRICT/STANDARD/LIGHT/EXEMPT compliance tiers to modulate `gate_passed()` validation intensity per step risk level
2. **Semantic quality rules as gate criteria** (C-005, C-009): Prohibited vague verbs, required artifact references, minimum task specificity — integrated into gate definitions
3. **Circular self-validation framing** (U-008): Explicit documentation of why external conductor is architecturally necessary (not just convenient)
4. **Scope discipline section** (from B's v1.0 parity constraints): YAGNI guardrails on conductor complexity
5. **Pre-write semantic checks** (B's checks 13-17): Adaptable as additional gate criteria for semantic validation steps
6. **Debate provenance and deferral tracking**: v1.1 deferral table format for tracking considered-and-rejected features
