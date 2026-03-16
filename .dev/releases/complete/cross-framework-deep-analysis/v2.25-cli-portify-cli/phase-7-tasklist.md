# Phase 7 -- Release Spec Synthesis

Produce the release-ready spec from prior artifacts with placeholder elimination and structured gap capture. Loads template, populates sections, runs brainstorm enrichment, and validates output.

### T07.01 -- Load Release Spec Template and Create Working Copy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-082, R-083 |
| Why | AC-009 and D-007 require loading template from src/superclaude/examples/release-spec-template.md and creating a working copy for synthesis. |
| Effort | S |
| Risk | Low |
| Risk Drivers | depends (template dependency D-007) |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0040/evidence.md

**Deliverables:**
- Template loading from `src/superclaude/examples/release-spec-template.md` with working copy creation in workdir

**Steps:**
1. **[PLANNING]** Verify D-007 dependency: confirm template exists at `src/superclaude/examples/release-spec-template.md` with all 13 sections and `{{SC_PLACEHOLDER:*}}` sentinels
2. **[PLANNING]** Define working copy location in workdir
3. **[EXECUTION]** Implement template loader reading release-spec-template.md
4. **[EXECUTION]** Create working copy in workdir for synthesis modification
5. **[VERIFICATION]** Verify working copy contains all 13 template sections and placeholder sentinels
6. **[COMPLETION]** Document template loading in D-0040/evidence.md

**Acceptance Criteria:**
- Template loaded from `src/superclaude/examples/release-spec-template.md` (AC-009, D-007)
- Working copy created in workdir preserving all 13 sections and `{{SC_PLACEHOLDER:*}}` sentinels
- Template file existence verified before synthesis proceeds
- Template loading documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0040/evidence.md

**Validation:**
- Manual check: working copy in workdir contains all 13 template sections
- Evidence: linkable artifact produced at D-0040/evidence.md

**Dependencies:** T06.07 (Phase 2 complete)
**Rollback:** TBD (if not specified in roadmap)

---

### T07.02 -- Implement 4-Substep Synthesis: Populate, Brainstorm, Incorporate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-084 |
| Why | FR-027 requires 4-substep synthesis: working copy creation (3a), populate all 13 template sections from Phase 1+2 outputs (3b), 3-persona brainstorm pass (3c), incorporate findings (3d). |
| Effort | XL |
| Risk | High |
| Risk Drivers | end-to-end, system-wide, depends |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0041/spec.md

**Deliverables:**
- 4-substep synthesis logic: (3a) working copy, (3b) populate 13 sections from Phase 1+2 outputs, (3c) 3-persona brainstorm pass (architect, analyzer, backend) producing `{gap_id, description, severity, affected_section, persona}` findings, (3d) incorporate actionable findings into body and route unresolvable to Section 11
- `BrainstormFinding` dataclass in `models.py` with fields: gap_id, description, severity, affected_section, persona

**Steps:**
1. **[PLANNING]** Map Phase 1+2 output artifacts to template sections for population (3b)
2. **[PLANNING]** Define brainstorm persona roles: architect (structural gaps), analyzer (completeness gaps), backend (implementation gaps)
3. **[EXECUTION]** Implement substep 3b: populate all 13 template sections by extracting content from analysis report, design specs, and portify-spec.md
4. **[EXECUTION]** Implement substep 3c: 3-persona brainstorm pass producing structured findings with {gap_id, description, severity, affected_section, persona}
5. **[EXECUTION]** Implement substep 3d: incorporate actionable findings into body; route unresolvable findings to Section 11 (FR-027)
6. **[VERIFICATION]** Write integration test: synthesis populates all 13 sections; brainstorm produces findings; incorporation routes correctly by severity
7. **[COMPLETION]** Document synthesis algorithm in D-0041/spec.md

**Acceptance Criteria:**
- All 13 template sections populated from Phase 1+2 outputs (protocol-map, analysis-report, design specs, portify-spec)
- 3-persona brainstorm pass produces findings with `{gap_id, description, severity, affected_section, persona}` structure
- Actionable findings incorporated into body; unresolvable findings routed to Section 11 (FR-027)
- `BrainstormFinding` dataclass defined in `models.py` with all 5 required fields: gap_id, description, severity, affected_section, persona
- Synthesis algorithm documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0041/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_synthesis"` exits 0
- Evidence: linkable artifact produced at D-0041/spec.md

**Dependencies:** T07.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** XL effort — 4 substeps with Claude subprocess invocation and brainstorm panel coordination.

---

### T07.03 -- Implement Placeholder Validation and Section 12 Check

| Field | Value |
|---|---|
| Roadmap Item IDs | R-085, R-086 |
| Why | FR-028 requires zero {{SC_PLACEHOLDER:*}} sentinels in final output. Section 12 (Brainstorm Gap Analysis) must exist per G-010. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (placeholder leakage Risk 3) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0042 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0042/spec.md

**Deliverables:**
- Placeholder validation scanning for `{{SC_PLACEHOLDER:*}}` sentinels with zero-tolerance enforcement, and Section 12 existence verification

**Steps:**
1. **[PLANNING]** Define placeholder regex pattern: `\{\{SC_PLACEHOLDER:[^}]+\}\}`
2. **[PLANNING]** Define Section 12 heading pattern for detection
3. **[EXECUTION]** Implement placeholder scan: regex search for all `{{SC_PLACEHOLDER:*}}` sentinels
4. **[EXECUTION]** Report remaining placeholders by name in diagnostics if any found
5. **[EXECUTION]** Implement Section 12 existence check: verify Brainstorm Gap Analysis section present
6. **[VERIFICATION]** Write unit tests: zero placeholders passes, remaining placeholders fails with names listed, Section 12 missing fails
7. **[COMPLETION]** Document validation rules in D-0042/spec.md

**Acceptance Criteria:**
- Placeholder scan detects all `{{SC_PLACEHOLDER:*}}` sentinels using regex (FR-028)
- Validation fails with diagnostic listing remaining placeholder names when any sentinels remain (Risk 3 mitigation)
- Section 12 (Brainstorm Gap Analysis) existence verified for G-010 compliance
- Validation rules documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0042/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_placeholder_validation"` exits 0
- Evidence: linkable artifact produced at D-0042/spec.md

**Dependencies:** T07.02
**Rollback:** TBD (if not specified in roadmap)

---

### T07.04 -- Emit portify-release-spec.md with Frontmatter

| Field | Value |
|---|---|
| Roadmap Item IDs | R-087 |
| Why | FR-029 requires final portify-release-spec.md with frontmatter containing title, status, quality_scores fields. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0043 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0043/spec.md

**Deliverables:**
- `portify-release-spec.md` emission with YAML frontmatter containing `{title, status, quality_scores}` fields

**Steps:**
1. **[PLANNING]** Define frontmatter schema: title (string), status (draft/final), quality_scores (object with dimensions)
2. **[PLANNING]** Confirm output location in workdir
3. **[EXECUTION]** Implement release spec writer: add YAML frontmatter to synthesized content
4. **[EXECUTION]** Write `portify-release-spec.md` to workdir with complete content
5. **[VERIFICATION]** Verify frontmatter is valid YAML with all required fields; G-010 passes (zero placeholders, Section 12 present)
6. **[COMPLETION]** Document release spec format in D-0043/spec.md

**Acceptance Criteria:**
- `portify-release-spec.md` emitted in workdir with YAML frontmatter containing title, status, quality_scores (FR-029)
- Frontmatter is valid YAML with all required fields parseable
- Content passes G-010 validation: zero placeholders, Section 12 present (SC-008)
- Release spec format documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0043/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_release_spec_emission"` exits 0
- Evidence: linkable artifact produced at D-0043/spec.md

**Dependencies:** T07.02, T07.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 7 / Tasks T07.01-T07.04

**Purpose:** Verify synthesis produces release spec passing G-010 with zero placeholders and Section 12 present.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P07-T01-T04.md

**Verification:**
- Template loaded and all 13 sections populated from Phase 1+2 artifacts
- 3-persona brainstorm produces structured findings with severity routing
- portify-release-spec.md passes G-010: zero placeholders, Section 12 present

**Exit Criteria:**
- SC-008 (G-010 passes) validated
- Synthesis substeps execute in correct order (3a → 3b → 3c → 3d)
- Brainstorm findings correctly routed by severity

---

### T07.05 -- Implement --file Argument Passing for Templates Exceeding 50KB

| Field | Value |
|---|---|
| Roadmap Item IDs | R-088 |
| Why | R-011 requires --file argument passing when template content exceeds 50KB to avoid subprocess argument length limits. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (large template handling) |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0044 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0044/spec.md

**Deliverables:**
- `--file` argument passing in `build_release_spec_prompt()`: if template content exceeds 50,000 characters, write to temp file and pass via `--file <path>` to Claude subprocess

**Steps:**
1. **[PLANNING]** Review Phase 0 OQ-008 resolution for exact subprocess file argument API
2. **[PLANNING]** Define threshold: 50,000 characters (50KB)
3. **[EXECUTION]** Implement size check in `build_release_spec_prompt()`: `if len(template_content) > 50_000`
4. **[EXECUTION]** When threshold exceeded: write template to temp file, pass `--file <path>` to Claude subprocess
5. **[VERIFICATION]** Write unit test: template under 50KB uses inline passing; template over 50KB uses --file
6. **[COMPLETION]** Document file passing mechanism in D-0044/spec.md

**Acceptance Criteria:**
- `build_release_spec_prompt()` checks template content length against 50,000 character threshold
- Templates exceeding 50KB written to temp file and passed via `--file <path>` to Claude subprocess (R-011)
- Templates under 50KB passed inline without file argument
- File passing documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0044/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_file_passing"` exits 0
- Evidence: linkable artifact produced at D-0044/spec.md

**Dependencies:** T07.04
**Rollback:** TBD (if not specified in roadmap)

---

### T07.06 -- Enforce 900s Timeout for Synthesis Step

| Field | Value |
|---|---|
| Roadmap Item IDs | R-089 |
| Why | NFR-001 requires 900s timeout for the release spec synthesis step to prevent hung Claude subprocesses during long synthesis operations. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (timeout) |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0045 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0045/evidence.md

**Deliverables:**
- 900s timeout enforcement for the release spec synthesis step (Step 10)

**Steps:**
1. **[PLANNING]** Confirm timeout value: 900s for synthesis step per NFR-001
2. **[PLANNING]** Review executor timeout mechanism from T03.06
3. **[EXECUTION]** Configure synthesis step with 900s timeout
4. **[VERIFICATION]** Verify timeout configuration matches NFR-001 specification
5. **[COMPLETION]** Document timeout setting in D-0045/evidence.md

**Acceptance Criteria:**
- Synthesis step (Step 10) enforces 900s timeout per NFR-001
- Timeout expiry triggers TIMEOUT status classification via exit code 124 path
- Timeout value is 900s (not the default 600s used by analysis steps)
- Timeout documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0045/evidence.md

**Validation:**
- Manual check: synthesis step timeout configuration verified at 900s
- Evidence: linkable artifact produced at D-0045/evidence.md

**Dependencies:** T07.04
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 7

**Purpose:** Verify Step 10 produces a release spec passing G-010 (zero placeholders, Section 12 present) with 900s timeout and >50KB file handling.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P07-END.md

**Verification:**
- Milestone M6 satisfied: Step 10 produces release spec passing G-010
- --file argument passing works for templates exceeding 50KB
- 900s timeout enforced for synthesis step

**Exit Criteria:**
- SC-008 (G-010 passes for release-spec.md) validated
- All 6 tasks (T07.01-T07.06) completed with deliverables D-0040 through D-0045 produced
- Super-milestone B (Pipeline Generation) complete: Phases 5-7 done
