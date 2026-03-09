---
blocking_issues_count: 4
warnings_count: 5
tasklist_ready: false
---

## Findings

### BLOCKING

**[BLOCKING] Traceability: FR-013 has no milestone Validates citation**
- Location: extraction.md:FR-013 / roadmap.md:Phase 1
- Evidence: FR-013 ("Implement 5-wave architecture: Wave 0...Wave 4") is not listed in any milestone's `Validates` annotation. M1.2 (Wave Orchestrator) implements this behavior but only cites SC-001, FR-001, SC-016, SC-017.
- Fix guidance: Add `FR-013` to the Validates line of Milestone 1.2.

**[BLOCKING] Traceability: FR-030 has no milestone Validates citation**
- Location: extraction.md:FR-030 / roadmap.md:Phase 2
- Evidence: FR-030 ("No downstream handoff — sc:roadmap does not trigger or reference any downstream commands") appears in the Phase 2 exit criteria referencing SC-010/FR-030 but is never listed in any milestone's `Validates` annotation. No milestone explicitly owns this requirement.
- Fix guidance: Add `FR-030` to the Validates line of Milestone 2.3 (roadmap generation) or create a dedicated bullet in M2.3 for enforcing no-downstream-handoff language.

**[BLOCKING] Traceability: NFR-005 has no milestone Validates citation**
- Location: extraction.md:NFR-005 / roadmap.md (all phases)
- Evidence: NFR-005 ("Refs files have no individual size limit but each must be focused on a single concern") is never cited in any milestone's `Validates` annotation. M6.1 checks ref loading discipline and M6.3 checks SKILL.md size, but neither validates NFR-005's single-concern constraint.
- Fix guidance: Add `NFR-005` to the Validates line of Milestone 6.1 (On-Demand Ref Loading Enforcement), which already verifies ref file properties.

**[BLOCKING] Traceability: NFR-010 has no milestone Validates citation**
- Location: extraction.md:NFR-010 / roadmap.md:Phase 1
- Evidence: NFR-010 ("Separation of concerns between command file (WHEN/WHAT) and SKILL.md (HOW), with SKILL.md never duplicating algorithm details from refs/") is never cited in any milestone's `Validates` annotation. M1.1 mentions "Validate SKILL.md/command separation" as a deliverable but its Validates line lists only SC-024, SC-025, FR-043.
- Fix guidance: Add `NFR-010` to the Validates line of Milestone 1.1.

### WARNING

**[WARNING] Interleave: Phase 6 consolidates 6 milestones into 1 validation milestone, violating claimed 1:1 ratio**
- Location: test-strategy.md:Phase 6 table / frontmatter `interleave_ratio: '1:1'`
- Evidence: The test strategy claims a 1:1 interleave ratio (24 validation milestones). The roadmap has 29 implementation milestones (M0.1-0.3=3, M1.1-1.5=5, M2.1-2.5=5, M3.1-3.3=3, M4.1-4.5=5, M5.1-5.2=2, M6.1-6.6=6). Phase 6's 6 milestones are covered by a single V-6.1, producing an actual ratio of 24:29 (~0.83:1). The consolidation is acknowledged but contradicts the stated ratio.
- Fix guidance: Either split V-6.1 into per-milestone validation milestones (V-6.1 through V-6.6) to achieve true 1:1, or change the frontmatter to `interleave_ratio: '24:29'` with a note explaining the Phase 6 consolidation rationale.

**[WARNING] Decomposition: M1.2 (Wave Orchestrator) bundles 8+ distinct behavioral concerns**
- Location: roadmap.md:Milestone 1.2
- Evidence: M1.2 lists 8 bullet items as a single deliverable: conditional Wave 1A activation, mandatory sequencing, REVISE loop with iteration counting, dry-run cutoff, state persistence hooks, resume from last completed wave, circuit breaker integration, and mode-aware routing. sc:tasklist would need to split this into at least 4-5 separate tasks.
- Fix guidance: Decompose into sub-milestones (e.g., M1.2a: Core sequencing engine, M1.2b: State persistence & resume, M1.2c: Mode-aware routing & circuit breaker hooks) or explicitly mark the bullet items as separate deliverables with IDs.

**[WARNING] Decomposition: M1.3 (Wave 0 Prerequisites) bundles 6 flag implementations and 3 validation checks**
- Location: roadmap.md:Milestone 1.3
- Evidence: M1.3 combines spec existence check, output dir writability, collision detection, parsing of 6 flags (`--dry-run`, `--compliance`, `--depth`, `--persona`, `--output`, `--no-validate`), and compliance auto-detection heuristics into a single milestone. These are distinct implementation units.
- Fix guidance: Consider splitting flag parsing and validation checks into separate deliverables, or accept that sc:tasklist will auto-decompose this milestone.

**[WARNING] Decomposition: M6.5 (Success Criteria Verification Matrix) describes 30+ sub-tasks as one deliverable**
- Location: roadmap.md:Milestone 6.5
- Evidence: "Map each SC-001 through SC-030 to one or more tests" plus "Execute negative-path tests" (listing 7 negative scenarios). This single milestone represents 37+ distinct test mapping and execution activities.
- Fix guidance: Break into M6.5a (SC-* mapping to tests) and M6.5b (Negative-path test execution), or accept decomposition at tasklist generation time.

**[WARNING] Decomposition: M0.3 (Open Question Resolution) lists 10 distinct decisions as one deliverable**
- Location: roadmap.md:Milestone 0.3
- Evidence: M0.3 contains a numbered list of 10 open questions, each requiring an independent decision. While logically grouped, sc:tasklist would need to split these into individual decision tasks.
- Fix guidance: Accept as-is if the 10 decisions are expected to be resolved in a single session, or split into groups (e.g., M0.3a: Architecture decisions #1-4, M0.3b: Behavioral decisions #5-10).

## Summary

| Severity | Count |
|----------|-------|
| BLOCKING | 4 |
| WARNING | 5 |
| INFO | 0 |

**Overall assessment**: The roadmap is **not ready for tasklist generation**. There are 4 blocking traceability gaps where functional/non-functional requirements (FR-013, FR-030, NFR-005, NFR-010) lack milestone Validates citations. All 4 are straightforward fixes — each requirement has an obvious owning milestone that simply omits the citation. After adding the missing citations, the roadmap would pass all blocking dimensions.

The 5 warnings are non-blocking but worth addressing: the Phase 6 validation consolidation contradicts the claimed 1:1 interleave ratio, and several milestones (M1.2, M1.3, M0.3, M6.5) are compound enough that sc:tasklist will need to decompose them.

## Interleave Ratio

**Formula**: `interleave_ratio = unique_phases_with_deliverables / total_phases`

**Values**:
- Phases with deliverables: Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6 = **7**
- Total phases: **7**

**interleave_ratio = 7 / 7 = 1.0**

Result is within [0.1, 1.0]. Test activities are distributed across all 7 phases (Phase 0 has contract validation, Phase 3 is dedicated validation, Phase 6 includes comprehensive test execution). Test activities are **not** back-loaded — validation is present from Phase 0 onward.

**Note**: While the phase-level interleave ratio is 1.0, the milestone-level interleave ratio in the test strategy is 24:29 (~0.83), due to Phase 6 consolidating 6 implementation milestones into 1 validation milestone (V-6.1). This is flagged as a WARNING above.
