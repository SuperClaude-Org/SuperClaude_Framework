

---
total_diff_points: 14
shared_assumptions_count: 12
---

## 1. Shared Assumptions and Agreements

1. **Complexity assessment**: Both agree on 0.82 complexity score and classify the project as complex
2. **5-wave execution model**: Both implement Waves 0, 1A, 1B, 2, 3, 4 with identical sequencing semantics
3. **3-artifact output**: Both produce exactly `roadmap.md`, `extraction.md`, `test-strategy.md`
4. **Chunked extraction**: Both activate at 500-line threshold with 4-pass verification (source coverage ≥95%, anti-hallucination 100%, section coverage 100%, count reconciliation exact)
5. **Template discovery**: Both implement 4-tier search (local → user → plugin → inline) with identical scoring weights (domain 0.40, complexity 0.30, type 0.20, version 0.10) and ≥0.6 threshold
6. **REVISE loop**: Both cap at 2 iterations then accept with `PASS_WITH_WARNINGS`
7. **Validation scoring**: Both use PASS ≥85% / REVISE 70-84% / REJECT <70%
8. **Adversarial agent range**: Both enforce 2-10 agents with orchestrator at ≥5
9. **Circuit breaker fallbacks**: Both define identical fallbacks (Sequential → native reasoning, Context7 → WebSearch, Serena → continue without persistence)
10. **SKILL.md constraint**: Both enforce ≤500 lines with 5 refs/ files
11. **No downstream coupling**: Both explicitly prohibit tasklist generation references in output
12. **Session persistence**: Both save state at wave boundaries with spec hash comparison on resume

## 2. Divergence Points

### D1: Phase 0 — Contract Freeze Phase
- **Opus**: Jumps directly into implementation (Phase 1 = Foundation & Core Pipeline); schema decisions are implicit within milestone work
- **Haiku**: Introduces an explicit Phase 0 for schema contract freeze, open-question resolution, and architecture baseline (2-3 days)
- **Impact**: Haiku's approach reduces rework risk but adds upfront time; Opus risks schema drift discovered mid-implementation

### D2: Phase Count and Structure
- **Opus**: 6 phases — Foundation → Generation → Validation → Adversarial → Persistence → Hardening
- **Haiku**: 7 phases (0-6) — Definition → Orchestrator → Extraction → Adversarial+Planning → Artifact Generation → Validation+Hardening → Release Verification
- **Impact**: Haiku separates orchestrator construction from extraction; Opus bundles them together. Haiku's separation enables earlier testability of the wave runner

### D3: Wave Orchestrator as Explicit Deliverable
- **Opus**: Wave execution logic is implicit — embedded within phase milestones without a dedicated orchestrator component
- **Haiku**: Dedicates M1.1 specifically to building a wave runner engine as a standalone component with explicit sequencing, gating, and loop control
- **Impact**: Haiku's explicit orchestrator is more testable and reusable; Opus risks scattered orchestration logic

### D4: Adversarial Phase Placement
- **Opus**: Defers adversarial to Phase 4 (after validation pipeline in Phase 3), treating it as an extension
- **Haiku**: Places adversarial integration in Phase 3 (before artifact generation in Phase 4), treating it as part of the planning layer
- **Impact**: Opus enables a fully functional single-spec pipeline first; Haiku integrates adversarial routing into the generation decision path earlier, which may catch integration issues sooner

### D5: Artifact Generation as Distinct Phase
- **Opus**: Generation is embedded in Phase 2 (milestones 2.2, 2.3) alongside template discovery
- **Haiku**: Separates artifact generation into its own Phase 4 with dedicated milestones for each artifact, decision summary, dry-run, and downstream handoff enforcement
- **Impact**: Haiku's isolation makes cross-artifact consistency easier to validate independently

### D6: Validation and Hardening Bundling
- **Opus**: Separates validation (Phase 3) from hardening (Phase 6)
- **Haiku**: Bundles validation, revision loop, circuit breakers, and resume into a single Phase 5
- **Impact**: Opus's separation allows parallel work on validation vs. hardening; Haiku's bundling ensures reliability concerns are addressed holistically

### D7: Persona Treatment
- **Opus**: `architect` persona — focuses on structural decisions, dependency mapping, critical path analysis
- **Haiku**: `analyst` persona — focuses on contract stability, failure modes, operational correctness, risk quantification
- **Impact**: Opus produces a more implementation-ready roadmap; Haiku produces a more defensively-oriented roadmap with stronger emphasis on what can go wrong

### D8: Open Questions Handling
- **Opus**: Lists 10 open questions in a dedicated section at the end with recommended resolutions and blocking-phase mapping
- **Haiku**: Expects all open questions resolved in Phase 0 before any implementation begins; references them as design blockers
- **Impact**: Opus allows parallel resolution during implementation; Haiku enforces sequential resolution first. Haiku is safer but slower

### D9: Timeline Estimates
- **Opus**: 14-23 days total, critical path 10-16 days
- **Haiku**: 20-31 days total, no explicit critical path calculation
- **Impact**: Opus is ~30% more aggressive; Haiku adds contingency buffer. The difference largely comes from Haiku's Phase 0 and more conservative per-phase estimates

### D10: Parallelization Analysis
- **Opus**: Explicitly identifies Phase 4 and Phase 5 as parallelizable after Phase 2, with a critical path diagram
- **Haiku**: Presents phases as largely sequential with no explicit parallelization analysis
- **Impact**: Opus enables faster delivery if resources allow parallel work; Haiku's linear approach is simpler but slower

### D11: Engineering Roles
- **Opus**: Does not specify team roles or resource allocation
- **Haiku**: Defines 4 engineering roles (implementation owner, validation/test owner, architecture reviewer, documentation owner)
- **Impact**: Haiku's role clarity helps team planning; Opus assumes a single implementer or leaves staffing to the reader

### D12: Validation Strategy Layering
- **Opus**: Uses a checkpoint table + end-to-end test list organized by mode combination
- **Haiku**: Introduces a 4-layer validation model (Contract → Flow → Dependency/Failure → Quality) with explicit gate structure
- **Impact**: Haiku's layered model is more systematic for progressive confidence building; Opus's mode-based approach is more practical for test execution

### D13: Release Readiness
- **Opus**: No explicit release gate — Phase 6 exit criteria serve as implicit release criteria
- **Haiku**: Dedicates Phase 6 entirely to verification matrix, performance tuning, and release readiness with measurable thresholds (100% pass on contract tests, etc.)
- **Impact**: Haiku provides clearer go/no-go criteria for release decisions

### D14: Risk Count and Depth
- **Opus**: 12 risks with probability/impact/mitigation/phase mapping in tabular format
- **Haiku**: 9 risks with narrative-style analysis grouped by priority (high/medium)
- **Impact**: Opus covers more risks with better traceability to phases; Haiku's narrative format provides deeper reasoning per risk

## 3. Areas Where One Variant Is Clearly Stronger

### Opus Is Stronger
- **Critical path analysis**: Explicit dependency diagram and parallelization opportunities
- **Requirement traceability**: Every milestone maps to specific SC-* and FR-* identifiers
- **Risk breadth**: 12 risks vs 9, with phase-level traceability
- **Implementation specificity**: Milestones contain concrete implementation details (frontmatter field names, exact algorithms, threshold values)
- **Timeline realism**: Parallelization-aware estimates with critical path distinction

### Haiku Is Stronger
- **Contract-first discipline**: Phase 0 eliminates interface ambiguity before coding begins
- **Orchestrator as first-class component**: Explicit wave runner prevents scattered execution logic
- **Validation methodology**: 4-layer validation model with explicit gates is more rigorous
- **Release criteria**: Measurable, quantified go/no-go thresholds
- **Team planning**: Role definitions support multi-person delivery
- **Failure-mode thinking**: Analyst lens catches operational risks Opus treats as implementation details

## 4. Areas Requiring Debate to Resolve

1. **Phase 0 necessity**: Is a dedicated contract-freeze phase worth 2-3 days, or can schemas be defined inline during Phase 1? (Haiku's safety vs Opus's speed)

2. **Adversarial phase ordering**: Should adversarial integration come before or after the validation pipeline is built? Opus's "single-spec first" approach vs Haiku's "integrated planning layer" approach affects how early adversarial bugs surface

3. **Orchestrator explicitness**: Does the wave runner deserve its own milestone/component, or is it emergent from the phase structure? This affects testability and maintainability

4. **Parallelization vs linearity**: Should the roadmap assume parallel execution capacity (Opus) or plan for sequential delivery (Haiku)? Depends on team size and risk tolerance

5. **Open question resolution timing**: Resolve all upfront (Haiku) vs resolve as encountered (Opus)? Front-loading is safer but may over-invest in questions that prove irrelevant during implementation

6. **Timeline aggressiveness**: 14-23 days (Opus) vs 20-31 days (Haiku) — the ~30% gap needs calibration against actual team velocity and dependency availability
