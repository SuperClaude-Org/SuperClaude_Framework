# Phase 1 -- Data Models & Gate Infrastructure

Define `ValidateConfig` dataclass and gate criteria (`REFLECT_GATE`, `ADVERSARIAL_MERGE_GATE`) that form the structural foundation for the validation subsystem. All subsequent phases depend on these definitions for field-name consistency and enforcement levels.

---

### T01.01 -- Confirm Tier Classifications for Phase 1 Tasks

| Field | Value |
|---|---|
| Roadmap Item IDs | -- |
| Why | Tier classifications for Phase 1 tasks have confidence < 0.70 due to infrastructure-domain keyword mismatch. Confirm tiers before execution. |
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
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0001/notes.md`

**Deliverables:**
- Confirmed tier assignments for T01.02 (STRICT), T01.03 (STANDARD), T01.04 (STANDARD) with justification for any overrides

**Steps:**
1. **[PLANNING]** Review tier assignments for T01.02, T01.03, T01.04
2. **[PLANNING]** Assess whether keyword-driven tier matches task risk profile
3. **[EXECUTION]** Record confirmed or overridden tier for each task
4. **[EXECUTION]** Document override reasoning if any tier is changed
5. **[VERIFICATION]** Verify all three tasks have confirmed tiers
6. **[COMPLETION]** Write decision artifact to D-0001/notes.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0001/notes.md` exists with confirmed tiers for T01.02, T01.03, T01.04
- Each tier decision includes a one-line justification
- Override reasons documented if any tier differs from computed assignment
- Traceability maintained (task IDs referenced in decision artifact)

**Validation:**
- Manual check: all Phase 1 tasks have a confirmed tier recorded in D-0001/notes.md
- Evidence: linkable artifact produced (D-0001/notes.md)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Clarification task inserted because all Phase 1 implementation tasks have tier confidence < 0.70. T01.02 scored STRICT due to "model" keyword in `models.py` filename, which may warrant override to STANDARD.

---

### T01.02 -- Extend `models.py` with `ValidateConfig` Dataclass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The validation executor requires a typed configuration object to receive CLI arguments and defaults. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0002/spec.md`

**Deliverables:**
- `ValidateConfig` dataclass added to `src/superclaude/cli/roadmap/models.py` with fields: `output_dir` (str), `agents` (list), `model` (str), `max_turns` (int), `debug` (bool)

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/models.py` to understand existing dataclass patterns
2. **[PLANNING]** Confirm field types and defaults from roadmap specification
3. **[EXECUTION]** Add `ValidateConfig` dataclass with fields `output_dir`, `agents`, `model`, `max_turns`, `debug`
4. **[EXECUTION]** Follow existing dataclass conventions (decorators, type annotations, defaults)
5. **[VERIFICATION]** Run `uv run pytest tests/ -k "model" --co` to verify no import breakage
6. **[COMPLETION]** Record specification in D-0002/spec.md

**Acceptance Criteria:**
- `ValidateConfig` dataclass exists in `src/superclaude/cli/roadmap/models.py` with all 5 specified fields
- Field types match specification (`output_dir: str`, `agents: list`, `model: str`, `max_turns: int`, `debug: bool`)
- Dataclass follows existing patterns in `models.py` (same decorator usage, import style)
- D-0002/spec.md documents the dataclass fields and their purposes

**Validation:**
- `uv run python -c "from superclaude.cli.roadmap.models import ValidateConfig; print(ValidateConfig.__dataclass_fields__)"` exits 0
- Evidence: linkable artifact produced (D-0002/spec.md)

**Dependencies:** T01.01
**Rollback:** TBD
**Notes:** Tier conflict: "model" keyword matched in field name/file name context -> resolved to STRICT by keyword match. Low confidence (40%) suggests STANDARD may be more appropriate; see T01.01 for confirmation.

---

### T01.03 -- Create `validate_gates.py` with `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002, R-003 |
| Why | Gate criteria define the structural and semantic requirements for validation reports, enabling automated quality enforcement. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███░░░░░░░] 30% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0003/spec.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/validate_gates.py` containing `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE` gate definitions

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/gates.py` to understand `GateCriteria`, `SemanticCheck`, `_frontmatter_values_non_empty` signatures
2. **[PLANNING]** Verify import paths and confirm available gate construction patterns
3. **[EXECUTION]** Create `src/superclaude/cli/roadmap/validate_gates.py`
4. **[EXECUTION]** Define `REFLECT_GATE` with STANDARD enforcement, min 20 lines, required frontmatter (`blocking_issues_count`, `warnings_count`, `tasklist_ready`), semantic check via `_frontmatter_values_non_empty`
5. **[EXECUTION]** Define `ADVERSARIAL_MERGE_GATE` with STRICT enforcement, min 30 lines, extended frontmatter (`validation_mode`, `validation_agents`), agreement table semantic check
6. **[EXECUTION]** Import `_frontmatter_values_non_empty`, `GateCriteria`, `SemanticCheck` from `roadmap/gates.py`
7. **[VERIFICATION]** Run `uv run python -c "from superclaude.cli.roadmap.validate_gates import REFLECT_GATE, ADVERSARIAL_MERGE_GATE"` to verify imports
8. **[COMPLETION]** Record gate specifications in D-0003/spec.md

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/validate_gates.py` exists with `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE` module-level constants
- `REFLECT_GATE` specifies: STANDARD enforcement, min_lines=20, frontmatter fields `blocking_issues_count`, `warnings_count`, `tasklist_ready`
- `ADVERSARIAL_MERGE_GATE` specifies: STRICT enforcement, min_lines=30, frontmatter fields `validation_mode`, `validation_agents`, agreement table semantic check
- Imports from `roadmap/gates.py` only (unidirectional dependency preserved)

**Validation:**
- `uv run python -c "from superclaude.cli.roadmap.validate_gates import REFLECT_GATE, ADVERSARIAL_MERGE_GATE; print('OK')"` exits 0
- Evidence: linkable artifact produced (D-0003/spec.md)

**Dependencies:** T01.01
**Rollback:** TBD
**Notes:** None

---

### T01.04 -- Write Unit Tests for Gate Criteria, Frontmatter Parsing, and Semantic Checks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Gate criteria must be validated independently before integration with the executor to catch field-name mismatches early. |
| Effort | S |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0004/evidence.md`

**Deliverables:**
- Unit test file covering `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE` criteria construction, frontmatter parsing, and semantic checks

**Steps:**
1. **[PLANNING]** Identify test patterns in existing gate tests (look for `tests/` files testing `gates.py`)
2. **[PLANNING]** Define test cases: missing frontmatter fields, empty semantic values, line count thresholds, agreement table enforcement
3. **[EXECUTION]** Create test file following existing test organization patterns
4. **[EXECUTION]** Write tests for REFLECT_GATE (missing fields, empty values, below min lines, valid input)
5. **[EXECUTION]** Write tests for ADVERSARIAL_MERGE_GATE (missing fields, no agreement table, below min lines, valid input)
6. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
7. **[COMPLETION]** Record test evidence in D-0004/evidence.md

**Acceptance Criteria:**
- Test file exists in `tests/` directory following project conventions, covering both `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE`
- Tests cover: missing frontmatter fields (reject), empty semantic values (reject), line count below threshold (reject), valid input (accept)
- `uv run pytest <test_file> -v` exits 0 with all tests passing
- D-0004/evidence.md records test count and pass/fail summary

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0004/evidence.md)

**Dependencies:** T01.02, T01.03
**Rollback:** TBD
**Notes:** None

---

### Checkpoint: End of Phase 1

**Purpose:** Verify that `ValidateConfig` dataclass and gate criteria are defined, importable, and unit-tested before proceeding to prompt engineering.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P01-END.md`

**Verification:**
- `ValidateConfig` dataclass importable from `models.py` with all 5 specified fields
- `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE` importable from `validate_gates.py` with correct enforcement levels and frontmatter requirements
- All unit tests for gate criteria pass (`uv run pytest` on gate test file)

**Exit Criteria:**
- All Phase 1 tasks (T01.01-T01.04) marked completed
- No import errors across `models.py` and `validate_gates.py`
- 30-minute alignment checkpoint with Phase 2 completed (verify field names in gates match prompt template references)
