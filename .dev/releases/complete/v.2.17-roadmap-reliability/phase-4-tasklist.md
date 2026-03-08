# Phase 4 -- Extract Step Protocol Parity

Align the CLI `build_extract_prompt()` with the source `sc-roadmap-protocol` by expanding requested frontmatter fields from 3 to 13+, updating the `EXTRACT_GATE` required fields, expanding the prompt body for structured extraction sections, and ensuring `build_generate_prompt()` consumes the expanded output.

---

### T04.01 -- Expand `build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` to request all 13+ frontmatter fields per source protocol

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020, R-021 |
| Why | The CLI extract prompt currently requests only 3 frontmatter fields while the source protocol expects 13+. This structural mismatch makes extraction artifacts incomplete. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (frontmatter field expansion), multi-file (prompt + gate + downstream consumer) |
| Tier | STRICT |
| Confidence | `[███████▒░░] 78%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer), 3-5K tokens, 60s timeout |
| MCP Requirements | Required: Sequential, Serena · Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Deliverables:**
1. `D-0015`: `build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` updated to request all 13+ frontmatter fields: `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`

**Steps:**
1. **[PLANNING]** Read current `build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` to identify existing field requests
2. **[PLANNING]** Read source protocol template (`src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`) to confirm all required fields
3. **[EXECUTION]** Update `build_extract_prompt()` to include all 13+ fields in the YAML frontmatter request section with field descriptions and expected types
4. **[EXECUTION]** Preserve the `<output_format>` XML block from T02.04 at the end of the prompt
5. **[VERIFICATION]** Dispatch quality-engineer to verify prompt contains all 13+ field names and correct types; run `uv run pytest tests/ -v`
6. **[COMPLETION]** Record expanded prompt specification in `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Acceptance Criteria:**
- `build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` requests all 13 fields listed in FR-031 by name
- Each field has a type annotation and description in the prompt text
- `<output_format>` XML block remains at the end of the prompt (not displaced by new content)
- Expanded prompt documented in `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Validation:**
- Manual check: grep `build_extract_prompt` return value for all 13 field names — expect 13 matches
- Evidence: `TASKLIST_ROOT/artifacts/D-0015/spec.md` produced

**Dependencies:** T02.04 (prompt hardening XML must be in place), T01.01 (tolerant gate for expanded validation)
**Rollback:** `git checkout src/superclaude/cli/roadmap/prompts.py`
**Notes:** None.

---

### T04.02 -- Update `EXTRACT_GATE` required fields in `src/superclaude/cli/roadmap/gates.py` to match expanded field set

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | The extract gate must validate the expanded frontmatter fields. Without updating the gate, extraction would pass with incomplete frontmatter. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | schema (gate field list expansion), system-wide (gate shared with validation) |
| Tier | STRICT |
| Confidence | `[████████░░] 82%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer), 3-5K tokens, 60s timeout |
| MCP Requirements | Required: Sequential, Serena · Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0016/spec.md`

**Deliverables:**
1. `D-0016`: `EXTRACT_GATE` (or equivalent gate definition) in `src/superclaude/cli/roadmap/gates.py` updated to require all 13+ frontmatter fields

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/gates.py` (or wherever `EXTRACT_GATE` is defined) to find the current required fields list
2. **[PLANNING]** Confirm the field list matches the 13+ fields from T04.01
3. **[EXECUTION]** Update the `EXTRACT_GATE` required fields list to include: `spec_source`, `generated`, `generator`, `functional_requirements`, `nonfunctional_requirements`, `total_requirements`, `complexity_score`, `complexity_class`, `domains_detected`, `risks_identified`, `dependencies_identified`, `success_criteria_count`, `extraction_mode`
4. **[VERIFICATION]** Run `uv run pytest tests/ -v`; dispatch quality-engineer to verify gate field list matches prompt field list
5. **[COMPLETION]** Record gate update in `TASKLIST_ROOT/artifacts/D-0016/spec.md`

**Acceptance Criteria:**
- `EXTRACT_GATE` required fields list in `src/superclaude/cli/roadmap/gates.py` contains all 13+ field names
- Gate rejects extraction output missing any of the 13+ required fields
- Gate field list matches `build_extract_prompt()` field list exactly (no drift)
- Gate update documented in `TASKLIST_ROOT/artifacts/D-0016/spec.md`

**Validation:**
- Manual check: read gate definition and verify all 13 field names present
- Evidence: `TASKLIST_ROOT/artifacts/D-0016/spec.md` produced

**Dependencies:** T04.01 (prompt must request fields before gate validates them)
**Rollback:** `git checkout src/superclaude/cli/roadmap/gates.py`
**Notes:** None.

---

### T04.03 -- Expand extract prompt body in `build_extract_prompt()` to request 8 structured extraction sections per source protocol

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | The source protocol expects structured extraction sections (FRs with IDs, NFRs, complexity, constraints, risks, dependencies, success criteria, open questions). The current prompt body is incomplete. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Sequential, Context7 · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0017/spec.md`

**Deliverables:**
1. `D-0017`: `build_extract_prompt()` body section updated to request 8 structured sections: functional requirements (with FR-NNN IDs), non-functional requirements (with NFR-NNN IDs), complexity assessment with scoring rationale, architectural constraints, risk inventory, dependency inventory, success criteria, open questions

**Steps:**
1. **[PLANNING]** Read source protocol reference (`src/superclaude/skills/sc-roadmap-protocol/refs/extraction-pipeline.md`) for section structure
2. **[PLANNING]** Read current `build_extract_prompt()` body to identify what sections are already requested
3. **[EXECUTION]** Add/expand body section instructions for each of the 8 structured sections, including ID format requirements (FR-NNN, NFR-NNN)
4. **[EXECUTION]** Ensure body section request is positioned before the `<output_format>` XML block
5. **[VERIFICATION]** Run `uv run pytest tests/ -v` to verify no regressions
6. **[COMPLETION]** Record expanded body specification in `TASKLIST_ROOT/artifacts/D-0017/spec.md`

**Acceptance Criteria:**
- `build_extract_prompt()` body requests all 8 structured sections by name
- FR-NNN and NFR-NNN ID formats specified in the prompt
- Body sections positioned before `<output_format>` XML block
- Body expansion documented in `TASKLIST_ROOT/artifacts/D-0017/spec.md`

**Validation:**
- Manual check: parse `build_extract_prompt()` return value for 8 section headers
- Evidence: `TASKLIST_ROOT/artifacts/D-0017/spec.md` produced

**Dependencies:** T04.01 (frontmatter fields must be expanded before body sections)
**Rollback:** `git checkout src/superclaude/cli/roadmap/prompts.py`
**Notes:** None.

---

### T04.04 -- Update `build_generate_prompt()` to consume expanded extraction output and add executor-populated fields (`pipeline_diagnostics`) post-subprocess

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | The generate step must consume the expanded extraction fields. Additionally, fields the LLM cannot reliably produce (e.g., `pipeline_diagnostics`) must be populated by the executor post-subprocess. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-file (prompts.py + executor.py), breaking (downstream consumer contract change) |
| Tier | STRICT |
| Confidence | `[████████▒░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer), 3-5K tokens, 60s timeout |
| MCP Requirements | Required: Sequential, Serena · Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0018/spec.md`

**Deliverables:**
1. `D-0018`: `build_generate_prompt()` in `src/superclaude/cli/roadmap/prompts.py` updated to reference expanded extraction fields; executor in `src/superclaude/cli/roadmap/executor.py` updated to populate `pipeline_diagnostics` and other executor-only fields post-subprocess

**Steps:**
1. **[PLANNING]** Read `build_generate_prompt()` in `src/superclaude/cli/roadmap/prompts.py` to identify how it references extraction output
2. **[PLANNING]** Identify which frontmatter fields are executor-populated vs LLM-produced (per FR-033: `pipeline_diagnostics` is executor-populated)
3. **[EXECUTION]** Update `build_generate_prompt()` to reference expanded extraction fields (complexity_score, domains_detected, risks_identified, etc.) in its input context
4. **[EXECUTION]** Add post-subprocess field population in `roadmap_run_step()` in `src/superclaude/cli/roadmap/executor.py`: inject `pipeline_diagnostics` into extraction output frontmatter after subprocess completes
5. **[VERIFICATION]** Dispatch quality-engineer to verify generate prompt references all expanded fields; run `uv run pytest tests/ -v`
6. **[COMPLETION]** Record changes in `TASKLIST_ROOT/artifacts/D-0018/spec.md`

**Acceptance Criteria:**
- `build_generate_prompt()` in `src/superclaude/cli/roadmap/prompts.py` references expanded extraction fields for roadmap generation context
- Executor in `src/superclaude/cli/roadmap/executor.py` populates `pipeline_diagnostics` in extraction frontmatter post-subprocess
- Generate step does not fail when consuming expanded extraction output
- Changes documented in `TASKLIST_ROOT/artifacts/D-0018/spec.md`

**Validation:**
- Manual check: read `build_generate_prompt()` and verify references to expanded extraction fields
- Evidence: `TASKLIST_ROOT/artifacts/D-0018/spec.md` produced

**Dependencies:** T04.01 (expanded extract prompt), T04.02 (gate validates expanded fields), T04.03 (body sections)
**Rollback:** `git checkout src/superclaude/cli/roadmap/prompts.py src/superclaude/cli/roadmap/executor.py`
**Notes:** Tier conflict: STANDARD (modify/add) vs STRICT (multi-file + breaking contract) → resolved to STRICT by priority rule.

---

### Checkpoint: End of Phase 4

**Purpose:** Verify protocol parity changes are complete and the generate step correctly consumes expanded extraction before end-to-end validation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`

**Verification:**
- `build_extract_prompt()` requests all 13+ frontmatter fields and 8 structured body sections
- `EXTRACT_GATE` validates the expanded field set
- `build_generate_prompt()` references expanded extraction fields and executor populates `pipeline_diagnostics`

**Exit Criteria:**
- All T04.xx tasks completed with passing validation
- No STRICT-tier tasks have unresolved issues
- Evidence artifacts produced for D-0015 through D-0018
