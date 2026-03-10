# Phase 2 -- Foundation — Models, State, Parsing

Build the data model (`Finding` dataclass), state schema shape, and parsing infrastructure that all downstream phases depend on. Parser resilience is a critical dependency — fail loudly when required fields are absent.

---

### T02.01 -- Implement Finding Dataclass in roadmap/models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | The Finding dataclass is the core data structure used by every downstream module (parser, executor, certify). All 10 fields specified in spec §2.3.1 must be present. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | schema, model |
| Tier | STRICT |
| Confidence | `[████████--]` 78% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0004/spec.md`

**Deliverables:**
- `Finding` dataclass in `src/superclaude/cli/roadmap/models.py` with fields: id (str), severity (str), dimension (str), description (str), location (str), evidence (str), fix_guidance (str), files_affected (list[str]), status (str), agreement_category (str)

**Steps:**
1. **[PLANNING]** Read existing `roadmap/models.py` to understand current dataclass patterns and imports
2. **[PLANNING]** Confirm all 10 fields from spec §2.3.1 and their types
3. **[EXECUTION]** Add `Finding` dataclass with `@dataclass` decorator and all 10 typed fields
4. **[EXECUTION]** Add status validation: enforce PENDING/FIXED/FAILED/SKIPPED as valid values per lifecycle model (D-0003)
5. **[EXECUTION]** Ensure `Finding` is importable by downstream modules (remediate_*, certify_*)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/` to verify no import/type errors introduced
7. **[COMPLETION]** Document dataclass fields and usage in `D-0004/spec.md`

**Acceptance Criteria:**
- `Finding` dataclass exists in `src/superclaude/cli/roadmap/models.py` with exactly 10 fields matching spec §2.3.1
- `from roadmap.models import Finding` succeeds without error from any module under `src/superclaude/cli/roadmap/`
- Status field validation enforces the 4 valid values from lifecycle model
- Dataclass follows existing patterns in `roadmap/models.py` (decorator style, type annotations)

**Validation:**
- `uv run pytest tests/roadmap/ -k "finding or model"` exits 0
- Evidence: linkable artifact produced at `D-0004/spec.md`

**Dependencies:** T01.03 (lifecycle model defines valid status values)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/models.py`
**Notes:** Critical Path Override: Yes — models/ path triggers CRITICAL verification. Tier: STRICT due to model/schema keywords.

---

### T02.02 -- Define State Schema Shape for .roadmap-state.json

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | The .roadmap-state.json must be extended with remediate and certify step entry structures using additive fields only, preserving backward compatibility. Field details finalized in Phase 6. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | schema, breaking |
| Tier | STRICT |
| Confidence | `[█████████-]` 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0005/spec.md`

**Deliverables:**
- State schema shape definition document specifying the structure of `remediate` and `certify` step entries in `.roadmap-state.json`, conforming to spec §3.1 additive-extension pattern

**Steps:**
1. **[PLANNING]** Read current `.roadmap-state.json` format and identify schema_version
2. **[PLANNING]** Map spec §3.1 state entries to concrete field definitions
3. **[EXECUTION]** Define `remediate` step entry shape: status, scope, findings_total, findings_actionable, findings_fixed, findings_failed, findings_skipped, agents_spawned, tasklist_file
4. **[EXECUTION]** Define `certify` step entry shape: status, findings_verified, findings_passed, findings_failed, certified, report_file
5. **[EXECUTION]** Define validation status lifecycle values: validated-with-issues, remediated, certified, certified-with-caveats
6. **[VERIFICATION]** Verify additive-only: no existing fields renamed or removed, no breaking changes to existing consumers
7. **[COMPLETION]** Write schema shape document to `D-0005/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0005/spec.md` documents both step entry structures matching spec §3.1
- Schema extension is additive-only: no existing field modifications
- All validation status lifecycle values (validated-with-issues, remediated, certified, certified-with-caveats) are defined
- Schema shape is compatible with existing `_save_state()` patterns from T01.01 review

**Validation:**
- Manual check: schema shape document reviewed against spec §3.1 JSON example for completeness
- Evidence: linkable artifact produced at `D-0005/spec.md`

**Dependencies:** T01.01 (pipeline review provides current schema patterns)
**Rollback:** N/A (design artifact — no code changes at this stage)
**Notes:** Critical Path Override: Yes — models path. Field values finalized in Phase 6 (T06.01) based on implementation evidence.

---

### T02.03 -- Implement Primary Report Parser (remediate_parser.py)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | The primary parser extracts Finding objects from validate/reflect-merged.md and validate/merged-validation-report.md. This is the critical dependency for every downstream phase. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | format-variance (report format fragility is a high-priority risk per roadmap Phase 1 Analyzer Priority note and Risk R-002; parser is critical dependency for all downstream phases) |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0006/spec.md`

**Deliverables:**
- `remediate_parser.py` module in `src/superclaude/cli/roadmap/` implementing a pure function that takes string input and returns `list[Finding]`

**Steps:**
1. **[PLANNING]** Read existing validation report formats (reflect-merged.md, merged-validation-report.md) to understand field extraction patterns
2. **[PLANNING]** Design parser as pure function (NFR-004): `parse_validation_report(text: str) -> list[Finding]`
3. **[EXECUTION]** Implement regex/markdown extraction for: finding ID, severity, dimension, description, location, evidence, fix_guidance, files_affected, agreement_category
4. **[EXECUTION]** Set initial status to PENDING for all extracted findings
5. **[EXECUTION]** Add loud failure when required structured fields (id, severity, description) are absent
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_parser.py` to verify parsing against known report formats
7. **[COMPLETION]** Document parser API and supported formats in `D-0006/spec.md`

**Acceptance Criteria:**
- `remediate_parser.py` exists at `src/superclaude/cli/roadmap/remediate_parser.py`
- `parse_validation_report()` is a pure function (no I/O, no subprocess calls, no side effects)
- Parser correctly extracts all Finding fields from reflect-merged.md format
- Parser correctly extracts all Finding fields from merged-validation-report.md format (distinct structure from reflect-merged.md)
- Parser raises explicit error when required fields (id, severity, description) are missing

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_parser.py` exits 0
- Evidence: linkable artifact produced at `D-0006/spec.md`

**Dependencies:** T02.01 (Finding dataclass must exist)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/remediate_parser.py`

---

### T02.04 -- Implement Fallback Parser with Deduplication

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | When merged validation report is unavailable, parser must fall back to individual reflect-* reports with deduplication: same file + within 5 lines = candidate, higher severity wins. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0007/spec.md`

**Deliverables:**
- Fallback parser function in `remediate_parser.py` that parses individual reflect-*.md reports and deduplicates findings using the two-step rule from spec §8/OQ-003

**Steps:**
1. **[PLANNING]** Review individual reflect report formats (reflect-opus-architect.md, reflect-haiku-analyzer.md patterns)
2. **[PLANNING]** Design deduplication algorithm: location match (same file + within 5 lines) then severity resolution (BLOCKING > WARNING > INFO)
3. **[EXECUTION]** Implement `parse_individual_reports(report_texts: list[str]) -> list[Finding]` as pure function
4. **[EXECUTION]** Implement deduplication: merge fix_guidance from both reports, prefer more specific guidance
5. **[EXECUTION]** Include non-matching findings as-is from their source report
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_parser.py -k fallback` to verify dedup logic
7. **[COMPLETION]** Document fallback path and dedup rules in `D-0007/spec.md`

**Acceptance Criteria:**
- Fallback parser function exists in `remediate_parser.py` as a pure function
- Deduplication uses two-step rule: location match (same file + within 5 lines) then severity resolution
- Higher severity wins on match; fix_guidance merged from both reports
- Non-matching findings included as-is

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_parser.py -k fallback` exits 0
- Evidence: linkable artifact produced at `D-0007/spec.md`

**Dependencies:** T02.01 (Finding dataclass), T02.03 (primary parser patterns)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/remediate_parser.py`

---

### T02.05 -- Write Parser Unit Tests (3+ Format Variants)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Parser resilience is a critical dependency. Fixture-based tests against 3+ known report format variants provide R-002 risk mitigation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[█████████-]` 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0008/evidence.md`

**Deliverables:**
- `tests/roadmap/test_remediate_parser.py` with fixture-based tests covering: (1) reflect-merged.md format with remediation status column, (2) merged-validation-report.md format without remediation status, (3) individual reflect-*.md reports with fallback dedup path

**Steps:**
1. **[PLANNING]** Identify 3+ report format variants from roadmap Phase 1 and spec §8/OQ-003
2. **[PLANNING]** Design test fixtures as string constants (known report content with expected Finding outputs)
3. **[EXECUTION]** Write test cases for primary parser: reflect-merged.md format, merged-validation-report.md format
4. **[EXECUTION]** Write test cases for fallback parser: individual reflect-*.md reports with deduplication verification
5. **[EXECUTION]** Write negative tests: missing required fields trigger loud failure, malformed input handled gracefully
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_parser.py -v` to verify all tests pass
7. **[COMPLETION]** Record test results in `D-0008/evidence.md`

**Acceptance Criteria:**
- `tests/roadmap/test_remediate_parser.py` exists with tests covering 3+ report format variants
- All format variant tests use fixture-based string constants (not file I/O)
- Negative tests verify loud failure on missing required fields
- `uv run pytest tests/roadmap/test_remediate_parser.py -v` exits 0 with all tests passing
- Unit test coverage for `remediate_parser.py` and `Finding` dataclass reaches 100% (measured via `uv run pytest tests/roadmap/test_remediate_parser.py --cov=superclaude --cov-report=term-missing`)

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_parser.py -v` exits 0
- `uv run pytest tests/roadmap/test_remediate_parser.py --cov=superclaude --cov-report=term-missing` shows 100% coverage on parser and data model
- Evidence: linkable artifact produced at `D-0008/evidence.md`

**Dependencies:** T02.03 (primary parser), T02.04 (fallback parser)
**Rollback:** `git checkout -- tests/roadmap/test_remediate_parser.py`

---

### Checkpoint: End of Phase 2

**Purpose:** Verify data model, parsers, and state shape are ready for downstream consumption by Phases 3-6.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P02-END.md`
**Verification:**
- Finding dataclass (D-0004) has all 10 fields and is importable from `roadmap.models`
- Primary and fallback parsers (D-0006, D-0007) pass all fixture-based tests (3+ format variants)
- State schema shape (D-0005) is documented with additive-only extensions
**Exit Criteria:**
- `uv run pytest tests/roadmap/test_remediate_parser.py -v` exits 0 with all tests passing
- 100% unit test coverage on parser and data model
- State schema shape passes backward-compatibility check
