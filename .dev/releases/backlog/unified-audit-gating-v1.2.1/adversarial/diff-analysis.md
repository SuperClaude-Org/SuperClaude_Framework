# Diff Analysis: Unified Audit Gating System v1.2.1 Roadmap Variants

**Pipeline**: Adversarial 3-variant comparison (Mode B)
**Timestamp**: 2026-03-03T00:00:00Z
**Depth**: deep (3 debate rounds)
**Variants analyzed**: 3

| Variant | File | Persona | Approach |
|---------|------|---------|----------|
| V1 | `variant-1-opus-architect.md` | opus:architect | Contracts-first, 6 milestones (Lock Data Contracts, Evaluator, Runtime Controls, CLI Integration, Rollout, Release Gate) |
| V2 | `variant-2-sonnet-qa.md` | sonnet:qa | Validation rigor, 6 milestones (Blocker Resolution, State Machine+Tests, Evaluator+Profile Tests, Runtime+Override Tests, Sprint CLI Regression Gate, Rollout Validation+Rollback Drill) |
| V3 | `variant-3-haiku-analyzer.md` | haiku:analyzer | Risk-first, 6 milestones (Blocker Closure, Contract Foundation, Reliability Hardening, Shadow+Calibration Gate, Soft Enforcement+Rollback Drill, Full Enforcement Gate) |

---

## Structural Differences

| ID | Aspect | V1 (Architect) | V2 (QA) | V3 (Analyzer) | Severity |
|----|--------|-----------------|----------|----------------|----------|
| S-001 | Milestone naming convention | Named by technical artifact: "Lock Data Contracts", "Deterministic Evaluator", "Runtime Controls", "CLI Integration", "Rollout Execution", "Release Decision Gate" | Named by deliverable+test suite: "State Machine Implementation AND Illegal-Transition Test Suite", "Deterministic Gate Evaluator AND Profile Test Suite" | Named by reliability phase: "Blocker Closure", "Contract Foundation", "Reliability Hardening", "Shadow+Calibration Gate", "Soft Enforcement+Rollback Drill", "Full Enforcement Gate" | Medium |
| S-002 | Rollout milestone granularity | Single M5 milestone covers Shadow, Soft, and Full rollout phases with 6 deliverables | Single M6 milestone covers rollout validation with 10 deliverables; separate M5 for Sprint CLI regression | Three separate milestones: M4 (Shadow+Calibration+Shadow-to-Soft gate), M5 (Soft+Rollback Drill), M6 (Full Enforcement+Soft-to-Full gate) | High |

### S-001 Analysis

The naming convention reflects each persona's priorities. The Architect names milestones after what is being built (artifact-centric), which aids technical planning. The QA persona names milestones after what is being validated alongside what is built (deliverable+test pairing), which aids acceptance tracking. The Analyzer names milestones after the risk phase they address (risk-centric), which aids rollout confidence. The QA naming approach provides the clearest traceability from milestone title to acceptance gate.

### S-002 Analysis

This is the highest-severity structural difference. The Architect collapses all three rollout phases into one milestone (M5), which reduces milestone count but makes it harder to gate promotion independently. The QA variant collapses rollout into M6 but adds a standalone Sprint CLI regression gate (M5), acknowledging that shared-file regression is a distinct risk deserving its own acceptance criterion. The Analyzer splits rollout into three milestones (M4/M5/M6), providing the most granular phase-gate tracking but consuming 50% of the milestone budget on rollout alone.

---

## Content Differences

| ID | Aspect | V1 (Architect) | V2 (QA) | V3 (Analyzer) | Severity |
|----|--------|-----------------|----------|----------------|----------|
| C-001 | Blocker resolution placement | Deferred to M6 (Release Decision Gate) as M6.1 deliverable. M1 is pure contract/schema work with no governance content. | Standalone M1 with 5 explicit deliverables (M1-D1 through M1-D5). Blocks all downstream testing. | Standalone M1 with 5 deliverables (D1.1 through D1.5). Blocks all downstream implementation. | High |
| C-002 | Testing approach | Tests embedded within each implementation milestone as deliverable items (e.g., M1.5, M2.5, M2.6). Test files named per milestone. | Dedicated test suite paired with each implementation milestone in the same milestone scope. Test counts explicit (e.g., "17 legal-transition tests", "11+ field-absence tests", "9 determinism assertions"). | Fault-injection suite as standalone M3 deliverable (D3.5). Tests referenced but not individually enumerated. | Medium |
| C-003 | Sprint CLI regression gate | Mentioned in M4 risk assessment ("Run full sprint regression suite") but no dedicated milestone or deliverable. | Standalone M5 milestone with 5 deliverables: baseline audit (M5-D1), PhaseStatus backward-compatibility (M5-D2), existing regression test pass-through (M5-D3), guard isolation test (M5-D4), zero-failure gate (M5-D5). | Not addressed. No mention of sprint CLI regression risk or models.py/tui.py shared-file concern. | High |

### C-001 Analysis

The Architect's choice to defer blocker closure to M6 is architecturally clean (contracts can be defined with provisional values) but creates a testability problem: any test that depends on finalized threshold values, retry budgets, or rollback triggers produces non-deterministic results until M6 completes -- which is the final milestone. The QA and Analyzer variants front-load blocker resolution as M1, ensuring all downstream tests are deterministic from the start. The QA variant provides the strongest rationale: "no downstream testing is meaningful without this."

### C-002 Analysis

The Architect embeds tests alongside deliverables within each milestone, keeping implementation and validation co-located. The QA variant makes the test suite a co-equal deliverable in the milestone title itself, with explicit test counts that serve as acceptance metrics. The Analyzer focuses on fault-injection as a standalone reliability gate (M3-D3.5), which proves resilience but does not enumerate individual test cases. The QA approach provides the highest auditability.

### C-003 Analysis

The QA variant uniquely identifies sprint CLI regression as a standalone risk worthy of its own milestone. The files `models.py` and `tui.py` are shared infrastructure used by the existing sprint runner. Changes to these files for audit gating could silently break sprint execution. The Architect acknowledges this risk in M4 but does not dedicate a milestone. The Analyzer does not address it at all. This is a significant gap in V1 and V3.

---

## Contradictions

| ID | Aspect | V1 (Architect) | V2 (QA) / V3 (Analyzer) | Severity | Resolution Required |
|----|--------|-----------------|--------------------------|----------|---------------------|
| X-001 | Blocker timing | Blocker closure in M6 (end of release cycle). Contracts defined in M1 with no finalized policy values. | Blocker closure in M1 (beginning of release cycle). All policy values finalized before implementation begins. | High | Yes -- incompatible orderings. If blockers are not closed before implementation, test suites for threshold-dependent behavior cannot produce deterministic results. |
| X-002 | Rollout granularity | Single M5 milestone for Shadow+Soft+Full (6 deliverables). Promotion criteria are deliverables within M5. | V3: Three separate milestones (M4/M5/M6) with per-phase acceptance gates. V2: Single M6 with explicit sub-phase sign-offs (M6-D9 Shadow-to-Soft, M6-D10 Soft-to-Full). | Medium | Yes -- determines whether promotion gates are milestone-level or deliverable-level checkpoints. |

### X-001 Resolution Guidance

The QA/Analyzer position is stronger. The specification itself (Section 12.3) identifies the four blockers as NO-GO criteria, meaning they must be resolved before the release can proceed. Deferring them to M6 means all intermediate milestones operate against provisional values that may change, invalidating test assertions. The Architect's approach creates technical debt in the form of test rewrites when values are finalized. Front-loading blocker resolution (M1) eliminates this class of rework entirely.

### X-002 Resolution Guidance

The QA approach (single milestone with explicit sub-phase sign-offs) provides adequate granularity without consuming additional milestone slots. The Analyzer's three-milestone approach is the most granular but consumes 50% of milestones on rollout. A pragmatic resolution is to keep a single rollout milestone but require explicit sub-phase acceptance gates within it, as the QA variant does with M6-D9 and M6-D10.

---

## Unique Contributions

| ID | Source | Description | Value | Integration Recommendation |
|----|--------|-------------|-------|---------------------------|
| U-001 | V1 (Architect) | **Closed-world state machine enforcement**: only listed transitions are legal; all others are illegal by default. Explicit architectural decision in M1.5 risk mitigation and M2.2 validator design. | High | Integrate into base. Eliminates an entire category of bypass vulnerabilities -- any new state added without declaring transitions is automatically blocked. |
| U-002 | V1 (Architect) | **Compile-time enforcement of release override prohibition**: OverrideRecord validator rejects release scope at construction time (M1.2), not only at transition validation time (M2.2). Defense-in-depth. | High | Integrate into base. Catches invalid overrides at the earliest possible point (object creation) rather than relying solely on the transition validator. |
| U-003 | V2 (QA) | **Adversarial test for release override** (M4-D7): test supplies a fully valid OverrideRecord at release scope and asserts it is still rejected. Tests the dangerous case (valid record + forbidden scope), not just the trivial case (absent record). | High | Already in QA base. Preserve. |
| U-004 | V2 (QA) | **Sprint CLI Regression Gate** (M5): standalone milestone with baseline audit (M5-D1), PhaseStatus backward-compatibility assertions (M5-D2), parametrized threshold fixtures, and zero-regression acceptance criterion (M5-D5). | High | Already in QA base. Preserve. |
| U-005 | V3 (Analyzer) | **Dedicated reliability hardening milestone** (M3): fault-injection suite (D3.5) as a standalone gate before any rollout begins. Proves lease/heartbeat/retry/deadlock controls work under adversarial conditions before shadow deployment. Includes deadlock-resistance package (D3.2) and stale-state recovery (D3.3). | High | Integrate key elements into base M4 (Runtime Controls). Add explicit fault-injection suite deliverable and formal deadlock-resistance argument. |
| U-006 | V3 (Analyzer) | **Three separate rollout gate milestones** with phase-specific acceptance criteria: M4 (Shadow+Shadow-to-Soft gate), M5 (Soft+Rollback Drill), M6 (Full+Soft-to-Full gate). Most granular rollout tracking with per-phase sign-off. | High | Integrate granularity into base M6 by structuring it with explicit sub-phases (Shadow-to-Soft and Soft-to-Full) with separate sign-off criteria, without adding new milestones. |

---

## Summary

### Areas of Agreement (All 3 Variants)

- 6-milestone structure with strict sequential dependencies
- Rollback drill as a mandatory, non-waivable gate
- Release override prohibition with no exceptions
- Two shadow windows required for KPI calibration
- Shadow-to-Soft and Soft-to-Full as distinct promotion gates
- Fail-closed behavior for unknown/missing inputs (failed(unknown))
- Override governance limited to task and milestone scope only
- Three-phase rollout: shadow, soft, full
- Ordered rollback: full -> soft -> shadow

### Key Disagreements Requiring Debate Resolution

1. **X-001 Blocker timing** (High): M1 (QA/Analyzer) vs M6 (Architect)
2. **X-002 Rollout granularity** (Medium): 1 milestone (Architect/QA) vs 3 milestones (Analyzer)
3. **C-003 Sprint CLI regression gate** (High): standalone M5 (QA) vs embedded (Architect) vs absent (Analyzer)
4. **C-002 Testing approach** (Medium): embedded (Architect) vs paired (QA) vs fault-injection-focused (Analyzer)

### Unique Contributions to Integrate

6 items identified (U-001 through U-006), all assessed as high value. Two are already present in the QA base (U-003, U-004). Four require integration from Architect (U-001, U-002) and Analyzer (U-005, U-006).
