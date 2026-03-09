# Refactoring Plan: v2.20 Spec Merge

## Overview

- **Base variant**: Variant 1 (FR-051, spec-workflow-evolution.md)
- **Incorporating from**: Variant 2 (FR-052, v2.20-WorkflowEvolution_Spec-GPT.md)
- **Total planned changes**: 7
- **Changes not being made**: 4
- **Risk**: Medium overall (changes are additive to base; no structural rewrites)
- **Review status**: Auto-approved

---

## Planned Changes

### Change 1: Add `FidelityDeviation` Python Dataclass to Architecture

- **Source**: Variant 2, Section 4.5 Data Models
- **Target location**: Base Section 4.5 (Data Models)
- **Integration approach**: Append after existing `RoadmapConfig` dataclass and deviation frontmatter schema comment
- **Rationale**: V1 advocate conceded explicitly in Round 1 that "FidelityDeviation dataclass is a superior data model — typed, introspectable, testable in isolation." V2 advocate won S-005 with 88% confidence. The dataclass should be specified as the *backing model* for frontmatter serialization, not a replacement for the markdown output format.
- **Merge instruction**: Add the following dataclass definition to Section 4.5, with a note that it serializes to/from the frontmatter schema:
  ```python
  @dataclass
  class FidelityDeviation:
      source_pair: str              # "spec→roadmap" | "roadmap→tasklist"
      severity: Literal["HIGH", "MEDIUM", "LOW"]
      deviation: str
      upstream_quote: str
      downstream_quote: str
      impact: str
      recommended_correction: str
  ```
- **Risk**: Low (additive; does not change frontmatter schema or gate behavior)

### Change 2: Add State Persistence to `.roadmap-state.json`

- **Source**: Variant 2, Section 4.2 (Modified Files: executor.py) and FR-052.3 AC
- **Target location**: Base Section 4.2 (Modified Files: executor.py row) and Section 5.1 (CLI Surface)
- **Integration approach**: Extend executor.py modification description to include state persistence; add to downstream inputs
- **Rationale**: V1 advocate conceded in Round 1: "State persistence is a real gap in FR-051. Orchestration scripts that need to read fidelity results across pipeline stages have no clean interface." V2 won S-006 with 85% confidence.
- **Merge instruction**:
  1. In Section 4.2 `executor.py` row, extend change description: "Add spec-fidelity step to `_build_steps()`; pass retrospective to extract step; **persist fidelity semantic pass/fail/skipped to `.roadmap-state.json` after step completion**"
  2. Add new acceptance criterion to FR-051.1: "- [ ] After spec-fidelity step completes, write `fidelity_status: pass|fail|skipped|degraded` to `.roadmap-state.json`"
- **Risk**: Low (additive; state file already exists; extend with new field)

### Change 3: Add Degraded Validation Contract

- **Source**: Variant 2, FR-052.5
- **Target location**: Base Section 3 (Functional Requirements) — add FR-051.6; Section 5.2 (Gate Criteria); Section 7 (Risk Assessment)
- **Integration approach**: Add new FR-051.6 for degraded validation; extend SPEC_FIDELITY_GATE criteria; add disambiguation field
- **Rationale**: V1 advocate conceded in Round 1: "FR-052's degraded contract exposes a gap in FR-051. FR-051 does not specify what happens when the fidelity harness itself fails." V2 won C-006 with 80% confidence. Hard failure on transient AI agent timeout is not viable for production pipelines.
- **Merge instruction**:
  1. Add FR-051.6 section: "**FR-051.6: Degraded Fidelity Validation Handling** — When the spec-fidelity agent call fails (timeout, API error), write `fidelity_check_attempted: true, validation_complete: false` to `.roadmap-state.json`; produce `spec-fidelity.md` with `validation_complete: false` frontmatter field; do not block pipeline progression — log warning. If retry_limit exhausted and still failed, set `fidelity_status: degraded`."
  2. Extend `SPEC_FIDELITY_GATE` frontmatter fields: add `validation_complete` (bool) and `fidelity_check_attempted` (bool)
  3. Remove the "degraded validation" from risk register (Risk 1) — it is now handled by design
- **Risk**: Medium (changes gate behavior for failure path; must test degraded-report handling)

### Change 4: Define Multi-Agent Conflict Escalation Protocol

- **Source**: Variant 2, Section 2 (Solution Overview) and FR-052.3 AC
- **Target location**: Base Section 3 FR-051.1 Acceptance Criteria; Section 5.2 Gate Criteria
- **Integration approach**: Add multi-agent behavior AC to FR-051.1; extend gate semantic check description
- **Rationale**: V2 won S-008 (70% confidence). V1 is silent on multi-agent fidelity merge. When multiple agents produce conflicting severity assessments for the same deviation, the base spec provides no guidance. Conservative escalation (treat disagreement as potential HIGH) is the correct default.
- **Merge instruction**: Add acceptance criterion to FR-051.1: "- [ ] When spec-fidelity is run in multi-agent mode, conflicting severity ratings for the same deviation are resolved conservatively: the highest stated severity from any agent is used (e.g., MEDIUM from one agent + HIGH from another → HIGH retained). The `validation_complete` field is set to `false` if any agent fails."
- **Risk**: Low (additive AC; does not affect single-agent execution path)

### Change 5: Add `tasklist_ready` to Deviation Report Frontmatter

- **Source**: Variant 2, Section 5.2 Gate Criteria (spec-fidelity step frontmatter)
- **Target location**: Base Section 4.5 (Deviation report frontmatter schema comment); Section 5.2 (Gate Criteria); FR-051.4 Acceptance Criteria
- **Integration approach**: Extend frontmatter schema with `tasklist_ready: bool`; extend gate semantic check
- **Rationale**: V2 won X-006 (65% confidence). `tasklist_ready` as an explicit boolean signal is more machine-parseable than inferring readiness from `high_severity_count == 0`. Both signals can coexist; `tasklist_ready: true` is derived from `high_severity_count == 0 AND validation_complete == true`.
- **Merge instruction**:
  1. Add `tasklist_ready: bool` to frontmatter YAML schema comment in Section 4.5 (derived field: `high_severity_count == 0 AND validation_complete == true`)
  2. Add gate semantic check: `_tasklist_ready_consistent(content)` — returns True if `tasklist_ready` is consistent with `high_severity_count` and `validation_complete`
  3. Extend FR-051.4 AC: "- [ ] `tasklist_ready: bool` field included in frontmatter; True iff `high_severity_count == 0` AND `validation_complete == true`"
- **Risk**: Low (additive derived field; deterministic from existing fields)

### Change 6: Adopt OI-052-1 as Open Item

- **Source**: Variant 2, Section 11 Open Items (OI-052-1)
- **Target location**: Base Section 11 (Open Items) — add as Item 4
- **Integration approach**: Append to existing 3 open items
- **Rationale**: "Should spec→roadmap fidelity run before or after existing reflect validation, or replace part of it?" is a valid unresolved question affecting executor step ordering. The base spec places spec-fidelity after test-strategy but does not clarify relationship to existing reflect step.
- **Merge instruction**: Add Open Item 4: "OI-051-4 | Fidelity vs. reflect ordering | Should spec-fidelity step run before or after the existing reflect validation step within the validate pipeline? Does spec-fidelity make reflect redundant for roadmap fidelity checking? | Medium — affects executor step ordering and total pipeline time | Before implementation begins"
- **Risk**: Low (additive documentation change)

### Change 7: Adopt OI-052-2 as Open Item

- **Source**: Variant 2, Section 11 Open Items (OI-052-2)
- **Target location**: Base Section 11 (Open Items) — add as Item 5
- **Integration approach**: Append to existing open items
- **Rationale**: "Should MEDIUM severity become blocking for certain boundary classes (e.g., fabricated traceability IDs)?" directly relates to FR-051.2 (tasklist fidelity) and gap analysis finding TD-001. This should be resolved before gate finalization.
- **Merge instruction**: Add Open Item 5: "OI-051-5 | MEDIUM severity blocking policy | Should MEDIUM severity become blocking for certain deviation categories (e.g., fabricated traceability IDs per Gap Analysis TD-001)? | Medium — affects gate strictness and false-positive tolerance | During gate finalization (Phase 2)"
- **Risk**: Low (additive documentation change)

---

## Changes NOT Being Made

### Rejected: Integrate spec-fidelity into validate subsystem (V2's S-001)

**V2 proposed**: Move spec-fidelity harness to `validate_executor.py` instead of `executor.py`.
**Rationale for rejection**: V1 won X-001/S-001 (68% confidence). The consequence of validate-subsystem placement — `--no-validate` bypasses fidelity — inverts the harness's purpose. Fidelity must be a generation quality gate that runs unconditionally. Debate transcript: "V2's placement means you can generate a drifted roadmap, ship it, and only discover the drift if someone runs validate separately."

### Rejected: Defer tasklist CLI to future release (V2's S-003)

**V2 proposed**: Replace `superclaude tasklist validate` CLI with a "reusable contract" placeholder.
**Rationale for rejection**: V1 won X-003/S-003 (78% confidence). V2 advocate conceded "deferral needs explicit sign-off from release ownership, not an implicit scope cut." Delivering a working CLI is superior to a contract no one can use. V2's deferral framing was classified as an unacknowledged scope reduction.

### Rejected: Extend ValidateConfig instead of RoadmapConfig (V2's S-004)

**V2 proposed**: Add `spec_file` and `boundary_mode` to `ValidateConfig`.
**Rationale for rejection**: V1 won S-004/X-004 (62% confidence). `retrospective_file` on `RoadmapConfig` is the correct owner for a generation-time input. `spec_file` in V2's design would live on `ValidateConfig` — meaning the spec path used for fidelity checking is configured in the validate layer, not the generation layer where it is consumed. V1's cohesion is more appropriate.

### Rejected: Use `blocking_issues_count`/`warnings_count` schema (V2's C-005)

**V2 proposed**: Replace 3-tier severity schema with `blocking_issues_count`/`warnings_count` action-based schema.
**Rationale for rejection**: V1 won X-005/C-005 (70% confidence). The 3-tier severity schema (HIGH/MEDIUM/LOW) preserves the distinction between severity and blockingness. An issue can be HIGH-severity with documented workaround (not blocking in context) or MEDIUM-severity with cascading impact (needing blocking). Collapsing to `blocking_issues_count` forces a binary at write time that should remain a policy decision at gate time. The `tasklist_ready` field (Change 5 above) is incorporated as a *derived* signal, not as a replacement for severity counts.
