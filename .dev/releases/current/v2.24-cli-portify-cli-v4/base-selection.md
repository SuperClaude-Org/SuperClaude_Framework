

---
base_variant: "Opus-Architect (Variant A)"
variant_scores: "A:82 B:74"
---

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced 8 key dimensions for evaluation:

| # | Criterion | Weight | Source |
|---|-----------|--------|--------|
| 1 | **Actionability & Implementation Readiness** | 15% | D-01, D-02: whether phases produce running code vs documents |
| 2 | **Architectural Completeness** | 15% | D-04, D-11: convergence detail, domain models, CLI options |
| 3 | **Risk Identification & Mitigation Specificity** | 12% | Both variants identify risks; quality of mitigations varies |
| 4 | **Open Question Resolution** | 12% | D-07, GAP-008: consolidated resolution vs flagging |
| 5 | **Test Strategy Depth** | 12% | D-07: counts vs edge cases vs validation sequence |
| 6 | **Contract & Gate Specification** | 10% | D-02: gate signatures, return contracts, failure taxonomy |
| 7 | **Failure & Resume Handling** | 12% | D-04, D-11: resume semantics, failure classification |
| 8 | **Structural Clarity & Navigability** | 12% | Phase organization, milestone definitions, readability |

## 2. Per-Criterion Scores

### Criterion 1: Actionability & Implementation Readiness (15%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| First running code | Day 3-4 (Phase 1) | Day 3-5 (after Phase 0) | A produces executable output sooner |
| Task granularity | 7 numbered tasks in P1 with specific files | 6 activities, less file-specific | A names exact modules per task |
| CLI options enumeration | Complete list in P1 | Implicit | Debate Round 2: B concedes this point |
| Deliverable checklists | Checkbox lists per phase | Milestone markers only | A more actionable for tracking |

**Scores**: A: 88 | B: 70

### Criterion 2: Architectural Completeness (15%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Convergence architecture | TurnLedger, budget pre-launch, terminal states, single-subprocess rationale | Loop control described, less mechanistic | B concedes A's depth in Round 3 |
| Domain model specification | `PortifyConfig`, `PortifyResult`, `StepStatus`, `PhaseContract` named | "Define canonical data contracts" — abstract | A specifies types; B describes intent |
| Dependency table | Full table with module/used-by/verified columns | List format, less structured | A more verifiable |
| Base module extension strategy | `ClaudeProcess` extension, `gate_passed()` reuse explicit | Referenced but not detailed | |

**Scores**: A: 86 | B: 72

### Criterion 3: Risk Identification & Mitigation Specificity (12%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Risk count | 9 risks with severity/likelihood matrix | 9 risks, tiered High/Medium/Low | Comparable coverage |
| Mitigation specificity | Specific techniques per risk (e.g., `--add-dir` for R-007) | More general strategies | A's mitigations are implementation-ready |
| Risk tiering | Severity × Likelihood matrix | Priority tiers with affected phases | B's tiering is cleaner for project management |
| Unlisted risks | Template path stability noted | Resume partial writes, monitoring vocabulary | B identifies more subtle risks |

**Scores**: A: 78 | B: 80

### Criterion 4: Open Question Resolution (12%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Resolution table | Complete table for all 10 questions with rationale | Flags as risks, defers resolution | B explicitly concedes this in Round 3 |
| GAP-008 consistency | Defers to Phase 5 (contradicts "resolve together" per B's rebuttal) | Flags as blocker but doesn't resolve | A has a minor inconsistency; B has no resolution |
| Specificity | Exact recommendations (e.g., `abs(computed - expected) < 0.01`) | General guidance | |

**Scores**: A: 88 | B: 58

### Criterion 5: Test Strategy Depth (12%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Test counts | 17 unit + 5 integration, per-phase counts | Target counts aligned but less per-phase breakdown | Comparable targets |
| Edge case identification | Standard cases | Malformed panel output, empty structures, name normalization, skill unavailability | B superior; A concedes in Round 3 |
| Validation sequence | Per-phase with SC-criteria mapping table | Dependency-ordered 5-step sequence | B's sequence is more methodical |
| Success criteria validation | Full SC-001 through SC-014 mapping table | Grouped by functional/non-functional | A more traceable |

**Scores**: A: 74 | B: 84

### Criterion 6: Contract & Gate Specification (10%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Gate signatures | `tuple[bool, str]` with per-step tier assignment | Same signature, less per-step detail | Comparable |
| Return contracts | `to_contract()` method specified, paths covered | "Canonical data contracts" — abstract | A more concrete |
| Failure taxonomy | Listed in Phase 5 diagnostics | Phase 0 contract baseline proposed | B's early definition is architecturally sound |

**Scores**: A: 80 | B: 76

### Criterion 7: Failure & Resume Handling (12%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Resume semantics | Re-run failed step, context injection from `focus-findings.md` | Same conclusion + idempotency questions | B raises harder questions |
| Failure classification | 5 categories in Phase 5 | 6 categories, per-phase integration proposed | B's per-phase approach is more thorough |
| Partial artifact handling | "Don't trust partial artifacts" | Explicit idempotency contract per step | B more rigorous |
| First-class treatment | Deferred to Phase 5 | Core feature from Phase 0 | B's philosophy is stronger; A concedes taxonomy timing |

**Scores**: A: 72 | B: 82

### Criterion 8: Structural Clarity & Navigability (12%)

| Aspect | A | B | Notes |
|--------|---|---|-------|
| Phase structure | 5 phases, clean progression | 6 phases (Phase 0 adds overhead) | A tighter; B's Phase 0 adds a phase for contracts only |
| Section organization | Executive summary → Phases → Risks → Dependencies → Validation → Timeline → Open Questions | Similar + "Analyzer Concerns" per phase + "Analyzer Recommendations" section | B adds useful review checklists |
| Named checkpoints | Phase exit criteria only | Checkpoints A-E with validation goals | B's checkpoints are better for go/no-go decisions |
| Cross-referencing | SC/NFR/FR codes throughout | Less systematic cross-referencing | A more traceable |

**Scores**: A: 82 | B: 76

## 3. Overall Scores

| Criterion | Weight | A | B | A Weighted | B Weighted |
|-----------|--------|---|---|------------|------------|
| Actionability | 15% | 88 | 70 | 13.2 | 10.5 |
| Architectural Completeness | 15% | 86 | 72 | 12.9 | 10.8 |
| Risk Mitigation | 12% | 78 | 80 | 9.4 | 9.6 |
| Open Question Resolution | 12% | 88 | 58 | 10.6 | 7.0 |
| Test Strategy | 12% | 74 | 84 | 8.9 | 10.1 |
| Contract & Gate Spec | 10% | 80 | 76 | 8.0 | 7.6 |
| Failure & Resume | 12% | 72 | 82 | 8.6 | 9.8 |
| Structural Clarity | 12% | 82 | 76 | 9.8 | 9.1 |

| | Raw Average | Weighted Total |
|---|---|---|
| **Variant A** | 81.0 | **81.4** |
| **Variant B** | 74.8 | **74.5** |

## 4. Base Variant Selection Rationale

**Variant A (Opus-Architect) is the stronger base** for these reasons:

1. **Implementation readiness**: A's phases contain numbered tasks with specific file targets, deliverable checklists, and per-phase test counts. A developer can start coding from Phase 1 without ambiguity. B requires interpretation to extract actionable work items.

2. **Open question resolution**: A provides a complete resolution table with rationale — the single most decisive difference. B flags questions as risks but doesn't resolve them, which the debate confirmed as the weaker approach (B conceded explicitly in Round 3).

3. **Architectural specificity**: A names domain types, specifies base class extensions, enumerates CLI options, and details the convergence architecture (TurnLedger, budget pre-launch, single-subprocess rationale). B describes intent at a higher level of abstraction.

4. **Success criteria traceability**: A's SC-001 through SC-014 validation table with per-criterion method and phase assignment is directly auditable. B groups criteria categorically but doesn't map individual criteria to verification methods as precisely.

5. **No Phase 0 overhead**: Both variants converged during debate that a full Phase 0 is over-scoped. A's 5-phase structure with an expanded Phase 1 (which both agreed on) is the natural merge target.

## 5. Specific Improvements to Incorporate from Variant B

These elements from B should be merged into the A base:

### Must Incorporate

1. **Contract review day in Phase 1** (from B's Phase 0, narrowed per debate convergence): Add a half-day contract review activity at the start of A's Phase 1 covering inter-module data flow contracts (Step 3 output → Step 5 input schema), failure contract structure, and resume state requirements. Not a separate phase — a task within Phase 1.

2. **Named checkpoints A-E** (B §6): Overlay B's checkpoint structure onto A's phases:
   - Checkpoint A: End of P1 — deterministic foundations proven
   - Checkpoint B: End of P2 — dry-run and review gate validated
   - Checkpoint C: End of P3 — synthesis quality and gap incorporation stable
   - Checkpoint D: End of P4 — convergence and readiness logic proven
   - Checkpoint E: End of P5 — release certification against all success criteria

3. **Test edge cases** (B Phase 1-4, conceded by A in Round 3): Add to A's test plans:
   - Malformed panel output parsing
   - Empty or sparse workflow structures
   - Name normalization edge cases (prefix/suffix stripping, case conversion)
   - Skill unavailability fallback paths
   - Review rejection behavior

4. **Validation sequence** (B §5): Adopt B's dependency-ordered validation sequence as the recommended test execution order:
   1. Contract and gate unit tests first
   2. Pure-programmatic step tests second
   3. Claude-assisted artifact structural validation third
   4. Convergence and failure-path tests fourth
   5. End-to-end workflow certification last

5. **Failure taxonomy timing** (converged in debate Round 3): Move failure classification categories from A's Phase 5 to Phase 1 alongside `StepStatus` definition. Categories: gate failure, subprocess crash, budget exhaustion, timeout, user rejection, malformed artifact. Full diagnostics implementation remains in Phase 5.

### Should Incorporate

6. **Per-phase "Analyzer Concerns"** (B Phases 0-5): Add as review checklists at the end of each phase in A. These serve as quality gates for phase reviews. Key examples:
   - P1: "Name derivation rules can create subtle collisions if normalization is not fully specified"
   - P2: "This phase has the highest risk of semantic incompleteness hidden behind structurally valid markdown"
   - P4: "Marker-format variability from `/sc:spec-panel` is a known fragility"

7. **Risk tiering labels** (B §3): Add High/Medium/Low priority labels alongside A's severity/likelihood matrix for clearer project management prioritization.

8. **Integration test for skill unavailability** (B Phase 5): Add as a 6th integration test alongside A's existing 5, covering the fallback path when `/sc:brainstorm` or `/sc:spec-panel` is not installed.

### Do Not Incorporate

- **Phase 0 as a separate phase**: Both variants converged that this is over-scoped. A half-day activity within Phase 1 achieves the same benefit.
- **3-role team recommendation**: B conceded this is aspirational for a 1-2 developer project.
- **Vertical-slice-only development philosophy**: Unresolved debate point; leave development approach to implementer based on team size, as recommended in the convergence assessment.
