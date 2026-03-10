# Phase 5 -- Certification Step

Single-agent scoped review verifying remediation was applied correctly. Skeptical by design — justification quality matters as much as PASS/FAIL labels. Keep token cost low via scoped context extraction.

---

### T05.01 -- Build Certification Prompt Builder (certify_prompts.py)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Pure function producing certification agent prompt per spec §2.4.2 template. Scoped sections only (not full file content) to control token cost per NFR-011. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0024/spec.md`

**Deliverables:**
- `certify_prompts.py` module with `build_certification_prompt(findings: list[Finding], context_sections: dict[str, str]) -> str` per spec §2.4.2 template

**Steps:**
1. **[PLANNING]** Read spec §2.4.2 certification prompt template: "You are a certification specialist..."
2. **[PLANNING]** Design function: accepts findings and pre-extracted context sections
3. **[EXECUTION]** Implement prompt builder with per-finding verification checklist (original issue, fix applied, check instruction)
4. **[EXECUTION]** Include output format requirement: PASS/FAIL per finding with one-line justification
5. **[EXECUTION]** Ensure prompt is pure function (NFR-004)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_certify_prompts.py` to verify prompt structure
7. **[COMPLETION]** Document prompt template in `D-0024/spec.md`

**Acceptance Criteria:**
- `build_certification_prompt()` is a pure function (no I/O, no subprocess per NFR-004)
- Prompt follows spec §2.4.2 template with per-finding verification instructions
- Output format specifies PASS/FAIL with justification per finding
- Function accepts pre-extracted context sections (not full file content)

**Validation:**
- `uv run pytest tests/roadmap/test_certify_prompts.py` exits 0
- Evidence: linkable artifact produced at `D-0024/spec.md`

**Dependencies:** T02.01 (Finding dataclass)
**Rollback:** N/A (new module)

---

### T05.02 -- Build Certification Context Extractor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Assembles only relevant sections around finding locations to control token scope per NFR-011/OQ-002. Each finding's check references a specific location; extract surrounding context. |
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
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0025/spec.md`

**Deliverables:**
- Context extractor: `extract_finding_context(file_content: str, finding: Finding) -> str` extracting the section surrounding each finding's location

**Steps:**
1. **[PLANNING]** Design extraction strategy: parse finding.location (e.g., "roadmap.md:§3.1" or "test-strategy.md:lines 85-92") to identify section boundaries
2. **[PLANNING]** Define context window: section heading + content until next same-level heading
3. **[EXECUTION]** Implement location parser: handle §-references and line-range references
4. **[EXECUTION]** Implement section extractor: extract heading + content for the referenced section
5. **[EXECUTION]** Return extracted context per finding, not full file content
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_certify_prompts.py -k "context"` to verify extraction accuracy
7. **[COMPLETION]** Document extraction strategy in `D-0025/spec.md`

**Acceptance Criteria:**
- Context extractor returns scoped sections, not full file content (per NFR-011)
- Location parser handles both §-references and line-range references
- Extracted context includes the section heading and content through next same-level heading
- Token cost per finding is proportional to section size, not file size

**Validation:**
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "context"` exits 0
- Evidence: linkable artifact produced at `D-0025/spec.md`

**Dependencies:** T02.01 (Finding dataclass with location field)
**Rollback:** N/A (pure function, new module)

---

### T05.03 -- Implement Certification Report Generation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | Generate certification-report.md with YAML frontmatter (findings_verified, findings_passed, findings_failed, certified, certification_date) and per-finding PASS/FAIL table per spec §2.4.3. |
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
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0026/spec.md`

**Deliverables:**
- Report generator function producing `certification-report.md` with YAML frontmatter and per-finding results table matching spec §2.4.3

**Steps:**
1. **[PLANNING]** Map spec §2.4.3 output format to function signature
2. **[PLANNING]** Define YAML frontmatter fields: findings_verified, findings_passed, findings_failed, certified, certification_date
3. **[EXECUTION]** Implement report generator parsing certification agent output into structured results
4. **[EXECUTION]** Generate per-finding results table: Finding | Severity | Result | Justification
5. **[EXECUTION]** Add summary section with overall assessment
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_certify_prompts.py -k "report"` to verify output format
7. **[COMPLETION]** Document report format in `D-0026/spec.md`

**Acceptance Criteria:**
- Report matches spec §2.4.3 format with YAML frontmatter and per-finding table
- YAML frontmatter contains all 5 required fields with computed values
- Per-finding table includes Finding, Severity, Result (PASS/FAIL), Justification columns
- `certified` field is boolean derived from whether all findings passed

**Validation:**
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "report"` exits 0
- Evidence: linkable artifact produced at `D-0026/spec.md`

**Dependencies:** T05.01 (prompt builder), T05.02 (context extractor)
**Rollback:** N/A (generator function)

---

### T05.04 -- Implement Outcome Routing and No-Loop Constraint

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035, R-038 |
| Why | Route certification outcomes: all pass → certified:true + tasklist_ready:true; some fail → certified-with-caveats. No automatic loop — single pass only per NFR-012. |
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
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0027/spec.md`

**Deliverables:**
- Outcome router: maps certification results to state updates (certified, certified-with-caveats) with explicit no-loop enforcement

**Steps:**
1. **[PLANNING]** Define outcome paths from spec §2.4.4: all-pass and some-fail
2. **[PLANNING]** Define state updates for each path
3. **[EXECUTION]** Implement all-pass path: `validation.status = "certified"`, `tasklist_ready = true`
4. **[EXECUTION]** Implement some-fail path: `validation.status = "certified-with-caveats"`, report lists failures
5. **[EXECUTION]** Enforce no-loop: pipeline completes after certification regardless of outcome (NFR-012)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_certify_prompts.py -k "outcome or routing"` to verify both paths
7. **[COMPLETION]** Document routing logic in `D-0027/spec.md`

**Acceptance Criteria:**
- All-pass outcome sets `certified: true` and `tasklist_ready: true`
- Some-fail outcome sets `certified-with-caveats` with failure list in report
- No automatic loop: pipeline completes after single certification pass (NFR-012)
- State updates are atomic and consistent

**Validation:**
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "outcome or routing"` exits 0
- Evidence: linkable artifact produced at `D-0027/spec.md`

**Dependencies:** T05.03 (report generation provides results to route)
**Rollback:** N/A (routing logic, no external state changes until committed)

---

### T05.05 -- Define CERTIFY_GATE with Semantic Checks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | The CERTIFY_GATE validates certification-report.md with required frontmatter (findings_verified, findings_passed, findings_failed, certified, certification_date), min 15 lines, semantic checks, and per-finding table presence per spec §2.4.5. |
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
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0028/spec.md`

**Deliverables:**
- `CERTIFY_GATE` GateCriteria instance per spec §2.4.5: required_frontmatter_fields (findings_verified, findings_passed, findings_failed, certified, certification_date), min_lines=15, semantic_checks (frontmatter_values_non_empty, per_finding_table_present)

**Steps:**
1. **[PLANNING]** Review GateCriteria patterns from T01.01 notes and REMEDIATE_GATE (T03.05)
2. **[PLANNING]** Map spec §2.4.5 gate definition to constructor arguments
3. **[EXECUTION]** Implement `_has_per_finding_table()` semantic check
4. **[EXECUTION]** Define `CERTIFY_GATE` constant in `certify_gates.py` matching spec §2.4.5
5. **[EXECUTION]** Reuse `_frontmatter_values_non_empty()` from REMEDIATE_GATE
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_certify_gates.py` to verify gate validation
7. **[COMPLETION]** Document gate definition in `D-0028/spec.md`

**Acceptance Criteria:**
- `CERTIFY_GATE` exists in `certify_gates.py` matching spec §2.4.5 field-for-field
- Required frontmatter: findings_verified, findings_passed, findings_failed, certified, certification_date (all 5 fields enforced by gate)
- Semantic check `per_finding_table_present` rejects reports without the results table
- Gate passes on well-formed reports and rejects malformed ones

**Validation:**
- `uv run pytest tests/roadmap/test_certify_gates.py` exits 0
- Evidence: linkable artifact produced at `D-0028/spec.md`

**Dependencies:** T05.03 (report format to validate against)
**Rollback:** N/A (gate definition, isolated module)

---

### T05.06 -- Register Certify Step via execute_pipeline()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | Certify runs as a standard Step via execute_pipeline() (unlike remediate which uses ClaudeProcess directly) per spec §2.5. |
| Effort | S |
| Risk | Low |
| Risk Drivers | pipeline |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0029/spec.md`

**Deliverables:**
- Certify step registration in `_build_steps()` with `CERTIFY_GATE`, output_file pointing to `certification-report.md`, executed via `execute_pipeline([certify_step])`

**Steps:**
1. **[PLANNING]** Review step registration pattern in `_build_steps()` from T01.01 notes
2. **[PLANNING]** Design certify step: standard Step with single-agent execution
3. **[EXECUTION]** Add certify step to `_build_steps()`: step_id="certify", gate=CERTIFY_GATE, output_file="certification-report.md"
4. **[EXECUTION]** Wire certify execution via `execute_pipeline([certify_step])` per spec §2.5
5. **[EXECUTION]** Integrate with `execute_roadmap()` flow: runs after remediate step completes
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "certify and registration"` to verify step is discoverable
7. **[COMPLETION]** Document step registration in `D-0029/spec.md`

**Acceptance Criteria:**
- Certify step registered in `_build_steps()` as standard Step (not ClaudeProcess)
- Step executed via `execute_pipeline([certify_step])` per spec §2.5
- `CERTIFY_GATE` applied to output validation
- Step integrates into `execute_roadmap()` flow after remediate

**Validation:**
- `uv run pytest tests/roadmap/ -k "certify and registration"` exits 0
- Evidence: linkable artifact produced at `D-0029/spec.md`

**Dependencies:** T05.05 (CERTIFY_GATE), T04.10 (remediate step must run first)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`

---

### Checkpoint: End of Phase 5

**Purpose:** Verify certification step is operational with skeptical single-pass design and correct gate validation.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P05-END.md`
**Verification:**
- Certification correctly identifies unfixed findings as FAIL (SC-003 partial)
- ≥90% BLOCKING findings receive PASS when properly remediated (SC-002 partial)
- Gate validation passes on well-formed reports and rejects malformed ones
**Exit Criteria:**
- Negative tests with intentionally unfixed findings confirm skeptical behavior
- Certify step registered and executable via `execute_pipeline()`
- No automatic loop — single pass terminates regardless of outcome
