# Phase 7 — Validation & Adversarial Review

**Goal**: Validate the refactoring plan through adversarial challenge.
**Tier**: STRICT (validation of plans that will drive code changes)
**Phase Gate**: All 5 tasks complete; `final-refactor-plan.md` produced as the corrected, validated master plan.

---

### T07.01 — Adversarial Review: Completeness & Coverage

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Challenge whether the refactoring plan actually captures all cross-framework insights from Phases 1-5 |
| **Effort** | M |
| **Risk** | Medium — missed insights mean wasted analysis work |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Traceability audit from Phase 1 map through to Phase 6 plan items |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required for verification), Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | Recommended — adversarial debate agent |
| **Deliverable IDs** | — |
| **Artifacts** | Section in `TASKLIST_ROOT/artifacts/validation-report.md` |

**Steps**:
1. [READ] `component-map.md` (Phase 1), all comparison artifacts (Phase 4), `merged-strategy.md` (Phase 5), `refactor-master.md` (Phase 6)
2. [TRACE] for each component pair in component-map.md:
   - Does it have a Phase 4 comparison? → Yes/No
   - Does the comparison verdict appear in merged-strategy.md? → Yes/No
   - Does the merged strategy produce a Phase 6 plan item? → Yes/No
   - If any "No": flag as gap
3. [CHALLENGE] for each gap: was it intentionally dropped (justified) or accidentally lost?
4. [DOCUMENT] traceability audit results with pass/fail per component

**Acceptance Criteria**:
1. Every component pair traced through all 6 phases
2. All gaps identified and classified as intentional or accidental
3. Accidental gaps have remediation recommendations

**Validation**:
1. Traceability table has zero unresolved "accidental" gaps
2. No merged strategy decision without a corresponding plan item (unless explicitly "discard")
3. All "discard" decisions have documented rationale

**Dependencies**: T06.05

---

### T07.02 — Adversarial Review: Scope Creep & "Patterns Not Mass" Enforcement

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The highest risk is that the plan silently imports llm-workflows complexity |
| **Effort** | M |
| **Risk** | High — scope creep is insidious and hard to detect |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Every plan item assessed against R-RULE-05 with specific evidence |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | Section in `TASKLIST_ROOT/artifacts/validation-report.md` |

**Steps**:
1. [READ] `refactor-master.md` and `merge-criteria.md`
2. [ASSESS] each plan item against R-RULE-05:
   - Is this a pattern adoption or a mass import?
   - Does it add >100 new lines? If yes, is it justified?
   - Does it introduce new external dependencies?
   - Does it violate any efficiency constraint from T05.03?
3. [CHALLENGE] items that are borderline:
   - Can the pattern be expressed more simply?
   - Is the full adoption necessary or would a partial adoption suffice?
   - What would a minimal viable version look like?
4. [QUERY] auggie MCP (SC) to verify that proposed changes don't duplicate existing SC functionality
5. [DOCUMENT] R-RULE-05 assessment per plan item: Pass/Fail/Needs Simplification

**Acceptance Criteria**:
1. Every plan item has R-RULE-05 assessment
2. Items marked "Needs Simplification" have concrete simplification suggestions
3. No plan item fails R-RULE-05 without remediation

**Validation**:
1. R-RULE-05 pass rate ≥ 80% (remaining items have remediation plans)
2. Total new code estimated across all plan items ≤ reasonable threshold
3. No new external dependencies without explicit justification

**Dependencies**: T06.05

---

### T07.03 — Adversarial Review: Technical Feasibility & File Reference Verification

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Plans that reference non-existent files or incompatible interfaces will fail during implementation |
| **Effort** | L |
| **Risk** | Medium — stale file references are common in large plans |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Every file path in plan verified against repo; interface compatibility checked |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required), Serena (optional for symbol verification) |
| **Fallback Allowed** | Serena optional |
| **Sub-Agent Delegation** | Recommended — parallel verification across plan items |
| **Deliverable IDs** | D-0060 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/validation-report.md` |

**Steps**:
1. [EXTRACT] all file paths referenced in `refactor-master.md`
2. [QUERY] auggie MCP (SC) to verify each file path exists and check current content
3. [CHECK] for each plan item: does the proposed change target code that currently exists at the specified location?
4. [CHECK] interface compatibility: do proposed changes maintain backward compatibility where required?
5. [CHECK] dependency conflicts: do any plan items modify the same file in incompatible ways?
6. [COMPILE] `validation-report.md` with:
   - Traceability audit results (from T07.01)
   - R-RULE-05 assessment (from T07.02)
   - File verification results (this task)
   - Per-item pass/fail table
   - Overall validation summary

**Acceptance Criteria**:
1. Every file path in the plan verified — pass/fail recorded
2. Interface compatibility assessed for critical changes
3. No unresolved file path failures
4. Validation report is complete with all 3 sections

**Validation**:
1. File path verification: ≥95% pass rate (remaining have corrections noted)
2. No plan item targets a file that doesn't exist
3. Dependency conflicts identified and resolved
4. Validation report has clear overall pass/fail verdict

**Dependencies**: T07.01, T07.02

---

### T07.04 — Final Refactoring Plan: Corrections & Assembly

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The validated, corrected plan is the definitive output of this sprint |
| **Effort** | M |
| **Risk** | Low — corrections are known from T07.01-T07.03 |
| **Tier** | STRICT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Final plan passes all validation checks that master plan failed |
| **MCP Requirements** | Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0061 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/final-refactor-plan.md` |

**Steps**:
1. [READ] `refactor-master.md` and `validation-report.md`
2. [APPLY] all corrections identified in validation:
   - Fix file path errors
   - Simplify items that failed R-RULE-05
   - Add missing items from traceability gaps
   - Resolve dependency conflicts
3. [RE-ORDER] items based on corrected dependencies
4. [WRITE] `final-refactor-plan.md` with:
   - All corrected plan items
   - Updated dependency graph
   - Updated effort estimates
   - Implementation order
   - Change log from master plan (what changed and why)
5. [VERIFY] no outstanding validation failures

**Acceptance Criteria**:
1. All validation failures from T07.03 resolved
2. Change log documents every correction with rationale
3. Dependency graph is consistent after corrections
4. Implementation order updated to reflect corrections

**Validation**:
1. Re-run validation checks from T07.03 — all pass
2. Change log is non-empty (corrections were made — if zero corrections, that's suspicious)
3. Final plan item count matches expected (master items + additions - removals)
4. No "TBD" or unresolved items

**Dependencies**: T07.03

---

### T07.05 — Phase 7 Sign-off & Confidence Assessment

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Final confidence assessment before the plan becomes the sprint deliverable |
| **Effort** | S |
| **Risk** | Low |
| **Tier** | STRICT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Overall confidence ≥80% for the final plan |
| **MCP Requirements** | Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | Section appended to `TASKLIST_ROOT/artifacts/final-refactor-plan.md` |

**Steps**:
1. [READ] `final-refactor-plan.md` and `validation-report.md`
2. [ASSESS] overall confidence in the plan:
   - What percentage of plan items have high confidence?
   - What are the top 3 risks?
   - What assumptions remain unverified?
   - What would cause the plan to fail during implementation?
3. [WRITE] confidence assessment section appended to `final-refactor-plan.md`:
   - Overall confidence: X%
   - Risk register: top 5 risks with mitigation
   - Assumptions list
   - Prerequisites for implementation
4. [UPDATE] phase checkpoint table

**Acceptance Criteria**:
1. Overall confidence ≥80%
2. Top 5 risks identified with mitigation strategies
3. All assumptions explicitly listed
4. Prerequisites for implementation defined

**Validation**:
1. Confidence percentage is evidence-based (not aspirational)
2. Risk register includes at least one "if this happens, the plan needs revision" scenario
3. Assumptions are falsifiable (can be checked)

**Dependencies**: T07.04

---

## Phase 7 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| Traceability audit complete (no accidental gaps) | T07.01 | ☐ |
| R-RULE-05 assessment complete (≥80% pass rate) | T07.02 | ☐ |
| File reference verification complete (≥95% pass) | T07.03 | ☐ |
| validation-report.md complete with 3 sections | T07.03 | ☐ |
| final-refactor-plan.md produced with corrections | T07.04 | ☐ |
| Change log documents all corrections | T07.04 | ☐ |
| Overall confidence ≥80% | T07.05 | ☐ |
| Top 5 risks identified with mitigation | T07.05 | ☐ |
| Sequential MCP used for all tasks (STRICT tier) | All | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
