# Phase 3 -- Interactive Prompt and Tasklist Plan

Produce the user-facing control surface: terminal summary, interactive severity-scoped prompt, scope filtering, and remediation tasklist as a planning artifact. All functions are pure (no I/O). Prompt logic lives in execute_roadmap(), preserving execute_pipeline() non-interactive contract.

---

### T03.01 -- Implement Terminal Summary Printer and Interactive Prompt

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010, R-011 |
| Why | After validation completes, the pipeline must print a severity-grouped finding summary and present a 4-option prompt ([1] BLOCKING, [2] +WARNING, [3] All, [n] Skip) in execute_roadmap(). |
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
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0009/spec.md`

**Deliverables:**
- Terminal summary function that formats findings by severity with IDs and descriptions per spec §2.2 box layout
- Interactive 4-option prompt handler in `execute_roadmap()` returning user's scope selection

**Steps:**
1. **[PLANNING]** Read `execute_roadmap()` in `executor.py` to identify the insertion point after `_auto_invoke_validate()`
2. **[PLANNING]** Design summary printer as pure formatting function: `format_validation_summary(findings: list[Finding]) -> str`
3. **[EXECUTION]** Implement `format_validation_summary()` grouping findings by severity (BLOCKING, WARNING, INFO) with counts
4. **[EXECUTION]** Implement prompt handler in `execute_roadmap()` accepting input [1], [2], [3], [n] and returning scope enum
5. **[EXECUTION]** Handle zero-BLOCKING-zero-WARNING case: skip prompt entirely per spec §2.2
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "summary or prompt"` to verify all prompt paths
7. **[COMPLETION]** Document prompt behavior and edge cases in `D-0009/spec.md`

**Acceptance Criteria:**
- `format_validation_summary()` exists as a pure function producing severity-grouped output matching spec §2.2 format
- Prompt logic lives in `execute_roadmap()`, NOT in `execute_pipeline()` (preserving non-interactive contract per FR-032)
- All 4 input paths handled: [1] BLOCKING, [2] BLOCKING+WARNING, [3] All, [n] Skip
- Zero-BLOCKING-zero-WARNING case auto-skips prompt

**Validation:**
- `uv run pytest tests/roadmap/ -k "summary or prompt"` exits 0
- Evidence: linkable artifact produced at `D-0009/spec.md`

**Dependencies:** T02.01 (Finding dataclass)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`

---

### T03.02 -- Implement Scope Filter and Auto-SKIP Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012, R-013 |
| Why | Filter findings by user-selected scope (BLOCKING only, +WARNING, All) and auto-SKIP findings marked NO_ACTION_REQUIRED or OUT_OF_SCOPE regardless of scope selection. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0010/spec.md`

**Deliverables:**
- Pure filter function: `filter_findings(findings: list[Finding], scope: ScopeEnum) -> tuple[list[Finding], list[Finding]]` returning (actionable, skipped)

**Steps:**
1. **[PLANNING]** Define scope enum: BLOCKING_ONLY, BLOCKING_WARNING, ALL
2. **[PLANNING]** List auto-SKIP conditions: NO_ACTION_REQUIRED, OUT_OF_SCOPE agreement categories
3. **[EXECUTION]** Implement `filter_findings()` as pure function (no I/O per NFR-004)
4. **[EXECUTION]** Apply auto-SKIP before scope filtering: NO_ACTION_REQUIRED and OUT_OF_SCOPE → SKIPPED regardless of scope
5. **[EXECUTION]** Apply scope filter: Option 1 keeps BLOCKING, Option 2 keeps BLOCKING+WARNING, Option 3 keeps all with fix_guidance
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "filter or skip"` to verify filter logic
7. **[COMPLETION]** Document filter behavior in `D-0010/spec.md`

**Acceptance Criteria:**
- `filter_findings()` is a pure function with no I/O or side effects
- Auto-SKIP always applies for NO_ACTION_REQUIRED and OUT_OF_SCOPE findings
- Scope filtering correctly partitions findings into actionable vs skipped
- Return type provides both actionable and skipped lists

**Validation:**
- `uv run pytest tests/roadmap/ -k "filter or skip"` exits 0
- Evidence: linkable artifact produced at `D-0010/spec.md`

**Dependencies:** T02.01 (Finding dataclass)
**Rollback:** N/A (pure function, isolated module)

---

### T03.03 -- Implement Zero-Findings Guard and Skip-Remediation Path

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014, R-015 |
| Why | When filtering produces 0 actionable findings, emit a stub tasklist with actionable: 0 and proceed to certify. When user selects [n], save state as validated-with-issues and end pipeline. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0011/spec.md`

**Deliverables:**
- Zero-findings guard: emits stub `remediation-tasklist.md` with `actionable: 0` when no actionable findings exist
- Skip-remediation handler: saves state as `validated-with-issues` when user selects [n]

**Steps:**
1. **[PLANNING]** Identify the two control flow paths: zero-findings and user-skip
2. **[PLANNING]** Define stub tasklist format per spec §2.3.2 zero-findings guard
3. **[EXECUTION]** Implement zero-findings guard: check if `len(actionable) == 0` after filtering, emit stub tasklist, proceed to certify
4. **[EXECUTION]** Implement skip path: on user [n] input, call `_save_state()` with `validation.status = "validated-with-issues"`, return early
5. **[EXECUTION]** Ensure both paths produce valid state for `--resume` to consume
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "zero_findings or skip_remediation"` to verify both paths
7. **[COMPLETION]** Document guard and skip behavior in `D-0011/spec.md`

**Acceptance Criteria:**
- Zero-findings guard produces `remediation-tasklist.md` with `actionable: 0` and all entries SKIPPED
- Skip path saves state as `validated-with-issues` and ends pipeline cleanly
- Both paths produce state compatible with `--resume` logic
- No partial or corrupted state on either path

**Validation:**
- `uv run pytest tests/roadmap/ -k "zero_findings or skip_remediation"` exits 0
- Evidence: linkable artifact produced at `D-0011/spec.md`

**Dependencies:** T03.02 (filter provides actionable count), T03.01 (prompt provides user selection)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`

---

### T03.04 -- Implement Remediation Tasklist Generation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Generate remediation-tasklist.md with full YAML frontmatter (type, source_report, source_report_hash, generated, total_findings, actionable, skipped) and severity-grouped entries per spec §2.3.6. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0012/spec.md`

**Deliverables:**
- Tasklist generator function: `generate_remediation_tasklist(findings: list[Finding], source_report_path: str) -> str` producing markdown with YAML frontmatter

**Steps:**
1. **[PLANNING]** Define frontmatter fields per spec §2.3.6: type, source_report, source_report_hash, generated, total_findings, actionable, skipped
2. **[PLANNING]** Define entry format per spec §2.3.6: `- [ ] F-XX | file | STATUS — description`
3. **[EXECUTION]** Implement `generate_remediation_tasklist()` as pure function (NFR-004)
4. **[EXECUTION]** Compute `source_report_hash` as SHA-256 of the source report content
5. **[EXECUTION]** Group findings by severity (BLOCKING, WARNING, INFO, SKIPPED) in output
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "tasklist_generation"` to verify output format
7. **[COMPLETION]** Document tasklist format in `D-0012/spec.md`

**Acceptance Criteria:**
- `generate_remediation_tasklist()` is a pure function producing markdown matching spec §2.3.6 format
- YAML frontmatter contains all required fields with computed values
- `source_report_hash` is SHA-256 of the source report content
- Findings grouped by severity with consistent entry format

**Validation:**
- `uv run pytest tests/roadmap/ -k "tasklist_generation"` exits 0
- Evidence: linkable artifact produced at `D-0012/spec.md`

**Dependencies:** T02.01 (Finding dataclass), T03.02 (filtered findings)
**Rollback:** N/A (pure function, new module)

---

### T03.05 -- Define REMEDIATE_GATE with Semantic Checks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | The REMEDIATE_GATE validates remediation-tasklist.md output using required frontmatter fields, min_lines, and semantic checks per spec §2.3.7. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0013/spec.md`

**Deliverables:**
- `REMEDIATE_GATE` GateCriteria instance with: required_frontmatter_fields (type, source_report, source_report_hash, total_findings, actionable, skipped), min_lines=10, enforcement_tier="STRICT", semantic_checks (frontmatter_values_non_empty, all_actionable_have_status)

**Steps:**
1. **[PLANNING]** Review existing GateCriteria and SemanticCheck patterns from pipeline infrastructure (T01.01 notes)
2. **[PLANNING]** Map spec §2.3.7 gate definition to concrete GateCriteria constructor arguments
3. **[EXECUTION]** Implement `_frontmatter_values_non_empty()` check function
4. **[EXECUTION]** Implement `_all_actionable_have_status()` check function verifying FIXED/FAILED status on all non-SKIPPED entries
5. **[EXECUTION]** Define `REMEDIATE_GATE` constant matching spec §2.3.7 exactly
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "remediate_gate"` to verify gate validates correct and rejects incorrect tasklists
7. **[COMPLETION]** Document gate definition in `D-0013/spec.md`

**Acceptance Criteria:**
- `REMEDIATE_GATE` exists as a GateCriteria instance matching spec §2.3.7 field-for-field
- Semantic check `frontmatter_values_non_empty` rejects empty frontmatter values
- Semantic check `all_actionable_have_status` rejects findings without FIXED/FAILED status
- Gate passes on well-formed remediation tasklists and rejects malformed ones

**Validation:**
- `uv run pytest tests/roadmap/ -k "remediate_gate"` exits 0
- Evidence: linkable artifact produced at `D-0013/spec.md`

**Dependencies:** T02.01 (Finding dataclass), T03.04 (tasklist format to validate against)
**Rollback:** N/A (gate definition, isolated module)

---

### Checkpoint: End of Phase 3

**Purpose:** Verify all user-facing control surfaces and tasklist planning artifacts are operational before orchestration work begins.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P03-END.md`
**Verification:**
- All 4 prompt paths tested (options 1, 2, 3, n) and produce correct downstream behavior
- Zero-findings guard produces correct stub output with `actionable: 0`
- `remediation-tasklist.md` validates against `REMEDIATE_GATE` schema in pre-execution state
**Exit Criteria:**
- No I/O in filter/scope functions (pure function verification)
- Prompt logic confirmed in `execute_roadmap()` not `execute_pipeline()`
- All Phase 3 tests pass: `uv run pytest tests/roadmap/ -k "phase3 or prompt or filter or tasklist_generation or remediate_gate"`
