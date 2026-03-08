# Phase 2 -- Prompt Engineering

Build reflection and merge prompt templates in `validate_prompts.py` that produce structurally valid validation reports. Phase 2 can run concurrently with Phase 1, with a 30-minute alignment checkpoint before Phase 3 to verify field-name consistency between gate definitions and prompt templates.

---

### T02.01 -- Confirm Tier Classifications for Phase 2 Tasks

| Field | Value |
|---|---|
| Roadmap Item IDs | -- |
| Why | Tier classifications for Phase 2 tasks have confidence < 0.70 due to infrastructure-domain keyword mismatch. Confirm tiers before execution. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0005/notes.md`

**Deliverables:**
- Confirmed tier assignments for T02.02 (STANDARD), T02.03 (STANDARD) with justification for any overrides

**Steps:**
1. **[PLANNING]** Review tier assignments for T02.02 and T02.03
2. **[PLANNING]** Assess whether keyword-driven tier matches task risk profile
3. **[EXECUTION]** Record confirmed or overridden tier for each task
4. **[EXECUTION]** Document override reasoning if any tier is changed
5. **[VERIFICATION]** Verify both tasks have confirmed tiers
6. **[COMPLETION]** Write decision artifact to D-0005/notes.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0005/notes.md` exists with confirmed tiers for T02.02 and T02.03
- Each tier decision includes a one-line justification
- Override reasons documented if any tier differs from computed assignment
- Traceability maintained (task IDs referenced in decision artifact)

**Validation:**
- Manual check: all Phase 2 tasks have a confirmed tier recorded in D-0005/notes.md
- Evidence: linkable artifact produced (D-0005/notes.md)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Clarification task for batch tier confirmation.

---

### T02.02 -- Create `validate_prompts.py` with Reflection and Merge Prompt Builders

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005, R-006, R-007, R-008 |
| Why | Prompt templates define the validation dimensions and output structure that agents use to produce structurally valid reports. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0006/spec.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/validate_prompts.py` containing `build_reflect_prompt()` and `build_merge_prompt()` functions with embedded validation dimensions, interleave formula, and false-positive constraint

**Steps:**
1. **[PLANNING]** Read existing prompt builder patterns in `src/superclaude/cli/roadmap/` (e.g., pipeline prompt modules)
2. **[PLANNING]** Catalog the 7 validation dimensions and their severity classifications from the roadmap
3. **[EXECUTION]** Create `src/superclaude/cli/roadmap/validate_prompts.py`
4. **[EXECUTION]** Implement `build_reflect_prompt(roadmap: str, test_strategy: str, extraction: str) -> str` covering all 7 validation dimensions with BLOCKING/WARNING severity classifications
5. **[EXECUTION]** Implement `build_merge_prompt(reflect_reports: list[str]) -> str` with BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categorization instructions
6. **[EXECUTION]** Embed interleave ratio formula: `interleave_ratio = unique_phases_with_deliverables / total_phases` (marked as initial, subject to refinement)
7. **[EXECUTION]** Embed false-positive reduction constraint text in reflection prompt
8. **[VERIFICATION]** Run `uv run python -c "from superclaude.cli.roadmap.validate_prompts import build_reflect_prompt, build_merge_prompt"` to verify imports
9. **[COMPLETION]** Record prompt specifications in D-0006/spec.md

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/validate_prompts.py` exists with `build_reflect_prompt` and `build_merge_prompt` functions
- `build_reflect_prompt` accepts 3 string arguments and returns a string containing all 7 validation dimension names with BLOCKING/WARNING severity labels
- `build_merge_prompt` accepts a list of report strings and returns a string containing BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categorization instructions
- Interleave ratio formula embedded verbatim: `interleave_ratio = unique_phases_with_deliverables / total_phases`

**Validation:**
- `uv run python -c "from superclaude.cli.roadmap.validate_prompts import build_reflect_prompt, build_merge_prompt; p = build_reflect_prompt('r','t','e'); assert 'BLOCKING' in p and 'WARNING' in p; print('OK')"` exits 0
- Evidence: linkable artifact produced (D-0006/spec.md)

**Dependencies:** T02.01
**Rollback:** TBD
**Notes:** Effort is M due to 4 grouped roadmap items (R-005 through R-008) contributing to a single file with embedded domain-specific content. Parallel with Phase 1; alignment checkpoint required before Phase 3.

---

### T02.03 -- Smoke Test Prompts Against Phase 1 Gate Criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Validates that prompt output structure matches gate requirements before integration, catching field-name mismatches early. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███░░░░░░░] 30% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0007/evidence.md`

**Deliverables:**
- Smoke test evidence confirming prompt outputs pass gate criteria (frontmatter fields present, semantic checks pass, line count thresholds met)

**Steps:**
1. **[PLANNING]** Identify sample roadmap, test-strategy, and extraction inputs from existing pipeline test fixtures or outputs
2. **[PLANNING]** Confirm gate criteria field names from Phase 1 (T01.03)
3. **[EXECUTION]** Generate sample prompt output by calling `build_reflect_prompt` with sample inputs
4. **[EXECUTION]** Verify generated prompt references all required frontmatter field names (`blocking_issues_count`, `warnings_count`, `tasklist_ready`)
5. **[VERIFICATION]** Confirm prompt template instructs agents to produce output that would pass `REFLECT_GATE` criteria
6. **[COMPLETION]** Record smoke test results in D-0007/evidence.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0007/evidence.md` exists with smoke test results
- Prompt output references all frontmatter field names required by `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE`
- No field-name mismatches between gate definitions (Phase 1) and prompt templates (Phase 2)
- Evidence documents which sample inputs were used and which checks passed

**Validation:**
- Manual check: prompt output structure matches gate criteria field names
- Evidence: linkable artifact produced (D-0007/evidence.md)

**Dependencies:** T01.03, T02.02
**Rollback:** TBD
**Notes:** This is the 30-minute alignment checkpoint referenced in the roadmap. Must complete before Phase 3 begins.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify that prompt templates produce structurally valid output that aligns with Phase 1 gate criteria before building the executor.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P02-END.md`

**Verification:**
- `build_reflect_prompt` and `build_merge_prompt` importable and return non-empty strings
- Prompt templates reference all frontmatter field names required by `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE`
- Smoke test evidence (D-0007) confirms no field-name mismatches

**Exit Criteria:**
- All Phase 2 tasks (T02.01-T02.03) marked completed
- 30-minute alignment checkpoint between Phase 1 gates and Phase 2 prompts passed
- No blocking field-name inconsistencies between gate definitions and prompt templates
