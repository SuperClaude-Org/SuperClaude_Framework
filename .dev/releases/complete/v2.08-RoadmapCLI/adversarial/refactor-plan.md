# Refactoring Plan: Merge Variant B Strengths into Variant A Base

## Overview
- **Base variant**: Variant A (`roadmap-cli-spec.md`) — score 0.910
- **Incorporated variant**: Variant B (`tasklist-spec-integration-strategies.md`) — score 0.668
- **Planned changes**: 6
- **Changes rejected**: 3
- **Overall risk**: Medium (additive and restructure changes; no deletions from base)

---

## Planned Changes

### Change #1: Add Tier-Proportional Gate Enforcement Model
- **Source**: Variant B, Strategy 4 (Acceptance Criteria Quality Rules) + tier model
- **Target**: New §3.3 "Gate Enforcement Tiers" in Variant A (after §3.2 Pipeline Interface Contract)
- **Integration approach**: INSERT new section
- **Rationale**: Both advocates agreed B's STRICT/STANDARD/LIGHT/EXEMPT model is "well-designed" and "genuinely better engineering" (Debate Round 2, Opus concession). A's uniform gate validation lacks risk sensitivity (Opus concession #3).
- **Concrete change**: Add `enforcement_tier` field to `GateCriteria` dataclass. Define 4 tiers with different validation intensity:
  - STRICT: full frontmatter + semantic checks + min_lines
  - STANDARD: frontmatter + min_lines
  - LIGHT: file exists + non-empty
  - EXEMPT: no gate (pass-through)
- Map steps to tiers: generate steps → STRICT, extract → STANDARD, test-strategy → STANDARD
- **Risk level**: Medium (modifies `GateCriteria` dataclass; requires updating `gate_passed()` logic and test fixtures)

### Change #2: Add Semantic Quality Rules to Gate Criteria
- **Source**: Variant B, Strategy 3 (Minimum Task Specificity Rule) + Strategy 4 (Acceptance Criteria Quality Rules)
- **Target**: Extend `GateCriteria` in §3.2 and `gate_passed()` in §3.2 / §13.5
- **Integration approach**: APPEND to existing dataclass
- **Rationale**: A concedes "mechanical gate validation misses semantic defects" (Opus concession #1). B's prohibited-verb lists and artifact-reference checks are "better gate criteria than anything A specifies" (Opus Round 3 concession #1). Debate scoring: C-005 won by Variant B at 85% confidence.
- **Concrete change**: Add optional `semantic_checks` field to `GateCriteria`:
  ```python
  @dataclass
  class GateCriteria:
      required_frontmatter_fields: list[str]
      min_lines: int
      enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
      semantic_checks: list[SemanticCheck] | None = None  # NEW
  ```
  Where `SemanticCheck` is a simple rule (e.g., `ProhibitedPatterns(["as appropriate", "as needed"])`, `RequiredPatterns(["specific file", "module", "endpoint"])`). These are pure Python regex checks, not LLM-evaluated — preserving A's deterministic gate design.
- **Risk level**: Medium (extends data model; semantic checks are pure Python regex, not LLM calls)

### Change #3: Add Circular Self-Validation Design Rationale
- **Source**: Variant B, Strategy 1 (Stage Completion Reporting) — specifically the rejected items rationale
- **Target**: New subsection in §1 Problem Statement or §3 Architecture
- **Integration approach**: APPEND rationale paragraph
- **Rationale**: B's framing — "the same model that produces output cannot reliably validate its own intermediate state (circular self-validation)" — articulates precisely why A's external conductor exists. Currently A states the solution but doesn't name the problem as clearly. Debate scoring: U-008 agreed at 95% confidence.
- **Concrete change**: Add paragraph to §1 after "Fabrication becomes impossible without writing the required output files":
  > **Design principle — no circular self-validation**: The conductor enforces a strict trust boundary. Gate validation (`gate_passed()`) is pure Python — it never invokes Claude to evaluate Claude's output. This eliminates the circular self-validation failure mode where the same model that produced an artifact judges its own quality, which produces false confidence regardless of how sophisticated the validation criteria are.
- **Risk level**: Low (additive documentation; no behavioral change)

### Change #4: Add Scope Discipline Section
- **Source**: Variant B, "Keep as-is" section + v1.0 parity philosophy
- **Target**: New §2.1 "Design Constraints" (after §2 Scope)
- **Integration approach**: INSERT new section
- **Rationale**: Opus Round 3 concession #3: "B's scope discipline section (YAGNI, no speculative architecture) is a valuable inclusion A lacks entirely." Prevents conductor from becoming overengineered.
- **Concrete change**: Add:
  > ### 2.1 Design Constraints
  > - **YAGNI enforcement**: The pipeline/ module implements only patterns required by sprint/ and roadmap/. No speculative abstractions for hypothetical future commands.
  > - **Conductor minimalism**: The conductor's responsibility is step sequencing, gate enforcement, retry logic, and state management. It does not interpret, evaluate, or transform artifact content.
  > - **v1.1 deferral tracking**: Features considered and deferred are recorded in §11 with rationale, preserving decision provenance.
- **Risk level**: Low (additive documentation)

### Change #5: Integrate Pre-Write Semantic Checks as Additional Gate Definitions
- **Source**: Variant B, Strategy 5 (Extended Pre-Write Validation, checks 13-17)
- **Target**: §4 Pipeline Steps — add semantic gate criteria for relevant steps; roadmap/gates.py data
- **Integration approach**: APPEND to gate definitions table
- **Rationale**: B's semantic checks (task count bounds, circular dependency detection, XL splitting enforcement) represent validation logic that A's gate framework can execute as pure Python checks. Debate scoring: C-005 won by B at 85% confidence.
- **Concrete change**: For the `merge` step, add semantic gates:
  - Check: no heading-level gaps in merged output (H2→H4 without H3)
  - Check: all cross-references resolve (Section X refs exist)
  - Check: no duplicate section headings
  These are implementable as `SemanticCheck` instances in `roadmap/gates.py`, executed by `gate_passed()` alongside frontmatter checks.
- **Risk level**: Low (additive gate criteria; pure Python implementation)

### Change #6: Add Deferred Features Table with Debate Provenance
- **Source**: Variant B, "v1.1 Deferred Items" table
- **Target**: Expand §11 "Open Questions (Resolved)" → rename to "Open Questions & Deferred Features"
- **Integration approach**: RESTRUCTURE existing section
- **Rationale**: B's explicit deferral table with debate provenance is a transparency contribution. Opus Round 3 concession #3 acknowledges this. Currently §11 only has 3 resolved questions.
- **Concrete change**: Add table:
  | Feature | Considered In | Deferral Reason |
  |---------|--------------|-----------------|
  | Multi-spec consolidation (--specs) | §2 Out of Scope | Requires adversarial merge across >2 variants |
  | --blind adversarial mode | §2 Out of Scope | Adds complexity without proven value |
  | >2 agents | §2 Out of Scope | v1 validates 2-agent pipeline first |
  | TUI/rich progress display | §2 Out of Scope | stdout logging sufficient for v1 |
  | Tier-proportional semantic gates | This merge | Implementation deferred to v1.1; framework designed in §3.3 |
- **Risk level**: Low (additive documentation)

---

## Changes NOT Being Made

### Rejected Change R-1: Replace A's File-on-Disk Gates with B's TodoWrite Observability
- **Diff point**: C-001, C-006
- **B's approach**: TodoWrite stage completion reporting for 6-stage internal pipeline
- **Rationale for rejection**: TodoWrite is session-scoped (ephemeral), cannot persist across crashes, and provides observability without enforcement. A's file-on-disk gates provide both enforcement and persistence. Both advocates agreed A's conductor is mandatory (Haiku Round 3 final concession).

### Rejected Change R-2: Adopt B's v1.0 Parity Constraint as Governing Scope
- **Diff point**: X-004
- **B's approach**: Only "execution-hardening patterns" that preserve existing behavior
- **Rationale for rejection**: The merged output exceeds both original scopes. Constraining to B's v1.0 parity would eliminate A's crash recovery, state management, and parallel execution — features Haiku conceded are "the strongest reliability argument." Opus Round 3 argument that parity constraint is "obsolete in merged output."

### Rejected Change R-3: Adopt B's Sequential-Only Execution Model
- **Diff point**: C-004
- **B's approach**: No parallel execution; sequential 6-stage pipeline
- **Rationale for rejection**: A's parallel generate steps with cross-cancellation are architecturally sound and tested against the existing sprint/ codebase. Sequential execution would be a regression in throughput without quality benefit.

---

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Tier enforcement | Medium | Extends GateCriteria dataclass | Revert field addition |
| #2 Semantic checks | Medium | Extends GateCriteria + gate_passed() | Remove optional field |
| #3 Design rationale | Low | Documentation only | Remove paragraph |
| #4 Scope discipline | Low | Documentation only | Remove section |
| #5 Merge semantic gates | Low | Additive gate criteria | Remove check instances |
| #6 Deferral table | Low | Documentation restructure | Revert section rename |

---

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-04T19:30:00Z
