# Phase 1 -- Adversarial Mindset

Phase 1 introduces the James Whittaker adversarial tester persona and wires it into the existing spec-panel review sequence. The goal is to begin generating adversarial findings immediately with minimal integration risk and token overhead (target: 5-10% additional).

---

### T01.01 -- Define Whittaker Adversarial Tester Persona in spec-panel.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The current panel lacks an expert whose primary role is to break specifications; Whittaker fills this gap with attack-based testing methodology. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/spec.md`
- `TASKLIST_ROOT/artifacts/D-0001/notes.md`

**Deliverables:**
1. Whittaker persona YAML block added to Expert Panel System section of `spec-panel.md` with identity, role description ("Adversarial Testing Pioneer"), behavioral directives, and scope boundaries that do not duplicate Nygard or Crispin roles

**Steps:**
1. **[PLANNING]** Read `spec-panel.md` Expert Panel System section to identify existing persona YAML structure and current expert list
2. **[PLANNING]** Verify Nygard and Crispin scope boundaries to ensure no duplication in the new persona definition
3. **[EXECUTION]** Write Whittaker persona YAML block following existing expert format: identity ("James Whittaker"), role ("Adversarial Testing Pioneer"), domain ("Attack surface analysis, boundary exploitation, degenerate input generation, guard condition probing")
4. **[EXECUTION]** Add scope boundary statement explicitly excluding Nygard's resilience domain and Crispin's testing strategy domain
5. **[VERIFICATION]** Verify persona follows existing YAML structure (NFR-2) and scope does not overlap with Nygard or Crispin
6. **[COMPLETION]** Record persona definition in evidence artifact

**Acceptance Criteria:**
- File `spec-panel.md` contains a new expert entry for "James Whittaker" in the Expert Panel System section following existing YAML structure
- Persona scope boundary explicitly excludes resilience (Nygard) and testing strategy (Crispin) domains
- Persona definition is additive-only; no existing expert descriptions are modified
- Change is traceable to R-001 via deliverable D-0001

**Validation:**
- Manual check: Whittaker persona block present in spec-panel.md Expert Panel System section with all required fields (identity, role, domain, methodology, critique focus, activation, review order)
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0001/spec.md`

**Dependencies:** None
**Rollback:** Remove Whittaker persona block from spec-panel.md
**Notes:** First milestone; no prior dependencies. Persona format copies existing expert template.

---

### T01.02 -- Define Five Attack Methodologies and Output Format Template

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002, R-003 |
| Why | Each attack methodology must be concrete enough to apply mechanically to a specification; the output format ensures findings cite specific invariant locations with state traces. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0002, D-0003 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0002/spec.md`
- `TASKLIST_ROOT/artifacts/D-0003/spec.md`
- `TASKLIST_ROOT/artifacts/D-0002/notes.md`

**Deliverables:**
1. Five attack methodology definitions in Whittaker persona: Zero/Empty Attack (FR-2.1), Divergence Attack (FR-2.2), Sentinel Collision Attack (FR-2.3), Sequence Attack (FR-2.4), Accumulation Attack (FR-2.5)
2. Output format template per FR-3: "I can break this specification by [attack]. The invariant at [location] fails when [condition]. Concrete attack: [scenario with state trace]."

**Steps:**
1. **[PLANNING]** Review FR-2.1 through FR-2.5 definitions from spec to confirm each methodology's scope
2. **[PLANNING]** Identify existing output format patterns in spec-panel.md for consistency
3. **[EXECUTION]** Write Zero/Empty Attack definition: "For every input, argument, and collection: what if it is zero, empty, null, or negative?"
4. **[EXECUTION]** Write remaining four attack definitions (Divergence, Sentinel Collision, Sequence, Accumulation) each as a concrete, mechanically applicable probe
5. **[EXECUTION]** Add output format template to persona Critique Focus field per FR-3
6. **[VERIFICATION]** Verify each methodology is specific enough to apply mechanically to a specification without interpretation
7. **[COMPLETION]** Record methodology definitions and template in evidence artifacts

**Acceptance Criteria:**
- File `spec-panel.md` Whittaker persona contains exactly 5 named attack methodologies matching FR-2.1 through FR-2.5
- Each methodology description is concrete and mechanically applicable (not abstract guidance)
- Output format template matches FR-3 structure: attack identification, invariant location, failure condition, concrete state trace
- All five methodologies use existing severity classification system (CRITICAL, MAJOR, MINOR) per NFR-3

**Validation:**
- Manual check: Each of the 5 attack types is defined with a specific probe question and produces findings using the FR-3 template format
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0002/spec.md` and `TASKLIST_ROOT/artifacts/D-0003/spec.md`

**Dependencies:** T01.01 (persona must exist before adding methodologies)
**Rollback:** Remove methodology and template sections from Whittaker persona block
**Notes:** D-0002 and D-0003 are logically coupled (methodologies produce findings in the template format); kept in one task per Section 4.4 (single deliverable type: persona content).

---

### T01.03 -- Update Boundaries Section to 11 Experts

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | The panel expert count in the Boundaries section must reflect the addition of Whittaker (10 to 11 experts). |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/spec.md`

**Deliverables:**
1. Boundaries section in `spec-panel.md` updated: expert count changed from 10 to 11

**Steps:**
1. **[PLANNING]** Locate the Boundaries section in spec-panel.md that states the expert count
2. **[PLANNING]** Confirm current count is 10 (or whatever the existing value is)
3. **[EXECUTION]** Update the expert count to 11 in the Boundaries section
4. **[EXECUTION]** Verify no other references to expert count exist that need updating
5. **[VERIFICATION]** Confirm count is 11 and existing expert descriptions are unchanged
6. **[COMPLETION]** Record change in evidence artifact

**Acceptance Criteria:**
- Boundaries section in `spec-panel.md` states "11 simulated experts" (or equivalent count reference)
- No existing expert descriptions are modified
- Change is a single numeric update with no side effects
- Traceable to R-004 via D-0004

**Validation:**
- Manual check: Boundaries section in spec-panel.md shows updated expert count of 11
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0004/spec.md`

**Dependencies:** T01.01 (persona must be added before count update is meaningful)
**Rollback:** Revert count to previous value in Boundaries section

---

### T01.04 -- Wire Whittaker into Review Sequence and Add Output Section

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005, R-006 |
| Why | A persona definition that never executes is worthless; M2 makes Whittaker an active participant in every panel review with a dedicated output section. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005, D-0006 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/spec.md`
- `TASKLIST_ROOT/artifacts/D-0006/spec.md`

**Deliverables:**
1. Review sequence in `spec-panel.md` updated: Whittaker appears after Fowler and Nygard (FR-5)
2. "Adversarial Analysis" section added to all output format templates in `spec-panel.md` (not gated behind a flag)

**Steps:**
1. **[PLANNING]** Locate the expert review sequence definition in spec-panel.md
2. **[PLANNING]** Identify all output format templates (standard, structured, detailed) that need the new section
3. **[EXECUTION]** Insert Whittaker into review sequence after Fowler and Nygard, ensuring he sees architectural and resilience context before attacking
4. **[EXECUTION]** Add "Adversarial Analysis" section to each output format template with attack methodology identification per finding
5. **[VERIFICATION]** Verify ordering is correct and output section appears in every format variant (not conditionally gated)
6. **[COMPLETION]** Record changes in evidence artifacts

**Acceptance Criteria:**
- Review sequence in `spec-panel.md` shows Whittaker positioned after Fowler and Nygard
- "Adversarial Analysis" section present in all output format examples (standard, structured, detailed)
- Section is unconditional (appears in every panel run, not gated behind --focus correctness or any other flag)
- Existing expert outputs are unchanged (additive-only integration)

**Validation:**
- Manual check: Review sequence ordering verified; Adversarial Analysis section present in each output format template in spec-panel.md
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0005/spec.md` and `TASKLIST_ROOT/artifacts/D-0006/spec.md`

**Dependencies:** T01.01 (persona defined), T01.02 (methodologies defined)
**Rollback:** Remove Whittaker from review sequence; remove Adversarial Analysis section from output templates

---

### T01.05 -- Measure Token Overhead on Two Representative Specifications

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | NFR-1 requires the adversarial tester add no more than 10% token overhead; measurement must happen before Gate A. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (token overhead measurement) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Deliverables:**
1. Token overhead measurement report comparing panel output with and without Whittaker on two representative specifications, documenting measured overhead percentage

**Steps:**
1. **[PLANNING]** Select two representative specifications for measurement (one correctness-heavy, one baseline)
2. **[PLANNING]** Establish baseline token counts by running panel without Whittaker persona
3. **[EXECUTION]** Run panel with Whittaker persona on both specifications and record token counts
4. **[EXECUTION]** Calculate overhead percentage: (with_whittaker - baseline) / baseline * 100
5. **[VERIFICATION]** Verify measured overhead is <=10% per NFR-1; document result regardless of pass/fail
6. **[COMPLETION]** Record measurement report in evidence artifact

**Acceptance Criteria:**
- Measurement report at `TASKLIST_ROOT/artifacts/D-0007/evidence.md` documents token counts for both specs with and without Whittaker
- Overhead calculation methodology is explicit and reproducible
- Result compared against NFR-1 threshold (<=10%)
- Traceable to R-007 via D-0007

**Validation:**
- Manual check: Overhead measurement report contains baseline counts, enhanced counts, and percentage for each of the two specifications
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Dependencies:** T01.04 (Whittaker must be wired into review sequence to measure overhead)
**Rollback:** N/A (measurement task; no specification changes)

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Verify Phase 1 adversarial persona definition and integration are structurally complete before validation run.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-T01-T05.md`

**Verification:**
- Whittaker persona block exists in spec-panel.md with all required fields (identity, role, domain, methodology, critique focus, activation, review order)
- Review sequence places Whittaker after Fowler and Nygard; Adversarial Analysis section present in all output formats
- Token overhead measurement completed and documented for two representative specs

**Exit Criteria:**
- All deliverables D-0001 through D-0007 have evidence artifacts at their intended paths
- No existing expert descriptions or output sections were modified (additive-only changes verified)
- Overhead measurement result is available for Gate A evaluation

---

### T01.06 -- Validate Whittaker Findings on v0.04 Specification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | AC-1 and AC-2 require the adversarial tester to catch zero-value bypass and pipeline dimensional mismatch scenarios on real specifications. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end validation scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Deliverables:**
1. v0.04 validation run log demonstrating Whittaker findings are present, existing expert outputs have no regressions, and both bug classes (guard bypass at zero, pipeline dimensional mismatch) are identified

**Steps:**
1. **[PLANNING]** Identify the v0.04 specification to use for validation
2. **[PLANNING]** Define expected findings: zero-value bypass (AC-1) and pipeline dimensional mismatch (AC-2)
3. **[EXECUTION]** Run spec-panel with Whittaker persona active on v0.04 specification
4. **[EXECUTION]** Capture full panel output including Adversarial Analysis section
5. **[VERIFICATION]** Verify Whittaker findings include at least one zero-value bypass finding and one pipeline count questioning; verify no regressions in existing expert outputs
6. **[COMPLETION]** Record validation run log in evidence artifact

**Acceptance Criteria:**
- Validation run log at `TASKLIST_ROOT/artifacts/D-0008/evidence.md` shows Whittaker findings for v0.04 specification
- At least one finding identifies the zero-value bypass scenario per AC-1
- At least one finding questions pipeline count usage per AC-2
- Existing expert outputs (Fowler, Nygard, Crispin, etc.) show no regressions compared to baseline

**Validation:**
- Manual check: v0.04 run log contains Adversarial Analysis section with findings matching AC-1 (zero-value bypass) and AC-2 (pipeline count)
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Dependencies:** T01.04 (integration complete), T01.05 (overhead measured)
**Rollback:** N/A (validation task; no specification changes)

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm Phase 1 (Adversarial Mindset) is complete and ready for Phase 2 dependency.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`

**Verification:**
- All 6 tasks (T01.01 through T01.06) completed with evidence artifacts
- Whittaker persona is defined, integrated, measured, and validated on v0.04
- Token overhead is <=10% per NFR-1 measurement

**Exit Criteria:**
- All deliverables D-0001 through D-0008 have evidence artifacts
- v0.04 validation run shows Whittaker findings with no regressions
- Phase 2 dependency (M1 complete) is satisfied
