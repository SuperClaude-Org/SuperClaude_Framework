# Phase 2 -- Prerequisites and Config

Implement the deterministic setup layer so the pipeline fails early and safely. Covers workflow path resolution, CLI name derivation, collision detection, workdir creation, component discovery, and timeout enforcement.

### T02.01 -- Implement Workflow Path Resolution in config.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Pipeline must resolve workflow paths under src/superclaude/skills/, require SKILL.md, and raise AMBIGUOUS_PATH or INVALID_PATH for invalid inputs. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | auth (path validation), depends (SKILL.md required) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0005/spec.md

**Deliverables:**
- Workflow path resolution logic in `src/superclaude/cli/cli_portify/config.py` that resolves paths under `src/superclaude/skills/`, requires `SKILL.md`, and raises `AMBIGUOUS_PATH` or `INVALID_PATH`

**Steps:**
1. **[PLANNING]** Review existing `src/superclaude/skills/` directory structure to understand path patterns
2. **[PLANNING]** Check T01.02 resolution for OQ-007 (agent discovery warning behavior) to inform error handling
3. **[EXECUTION]** Implement path resolution: accept skill name or path, resolve to `src/superclaude/skills/<name>/`
4. **[EXECUTION]** Add SKILL.md existence check; raise `INVALID_PATH` if missing
5. **[EXECUTION]** Add ambiguity detection: if multiple skill directories match partial name, raise `AMBIGUOUS_PATH` with candidate list
6. **[VERIFICATION]** Write unit tests covering: valid path, missing SKILL.md, ambiguous name, explicit path override
7. **[COMPLETION]** Document path resolution algorithm and error codes in D-0005/spec.md

**Acceptance Criteria:**
- `config.py` resolves `src/superclaude/skills/<name>/` paths and verifies `SKILL.md` exists at the resolved location
- `AMBIGUOUS_PATH` raised with candidate list when multiple skill directories match a partial name
- `INVALID_PATH` raised when resolved path does not contain `SKILL.md`
- Unit tests for valid path, missing SKILL.md, and ambiguous name scenarios pass via `uv run pytest`

**Validation:**
- `uv run pytest tests/ -k "test_workflow_path"` exits 0
- Evidence: linkable artifact produced at D-0005/spec.md

**Dependencies:** T01.04 (architecture baseline)
**Rollback:** TBD (if not specified in roadmap)

---

### T02.02 -- Implement CLI Name Derivation Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Pipeline must derive a CLI module name by stripping sc- prefix and -protocol suffix, normalizing to kebab-case, and supporting explicit --name override. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0006/spec.md

**Deliverables:**
- CLI name derivation function in `config.py` that strips `sc-` prefix and `-protocol` suffix, normalizes to kebab-case, and accepts explicit `--name` override

**Steps:**
1. **[PLANNING]** Review existing skill naming conventions in `src/superclaude/skills/`
2. **[PLANNING]** Confirm kebab-case normalization rules (hyphens, lowercase, no special chars)
3. **[EXECUTION]** Implement name derivation: strip `sc-` prefix, strip `-protocol` suffix, normalize to kebab-case
4. **[EXECUTION]** Add `--name` explicit override that bypasses derivation
5. **[EXECUTION]** Handle derivation failure: if stripping prefix/suffix yields empty string, raise `DERIVATION_FAILED` with diagnostic message
6. **[VERIFICATION]** Write unit tests: `sc-cli-portify-protocol` → `cli-portify`, explicit `--name custom-name` → `custom-name`, edge cases (no prefix/suffix), empty derivation result
6. **[COMPLETION]** Document derivation algorithm in D-0006/spec.md

**Acceptance Criteria:**
- Name derivation transforms `sc-cli-portify-protocol` to `cli-portify` correctly
- Explicit `--name` override bypasses automatic derivation and uses provided name directly
- Kebab-case normalization produces lowercase-hyphenated output for all valid inputs
- `DERIVATION_FAILED` error raised when automatic name derivation produces an empty or invalid result (no `--name` override provided and derivation yields no usable name)
- Unit tests pass via `uv run pytest` covering derivation, override, edge cases, and derivation failure

**Validation:**
- `uv run pytest tests/ -k "test_cli_name"` exits 0
- Evidence: linkable artifact produced at D-0006/spec.md

**Dependencies:** T02.01
**Rollback:** TBD (if not specified in roadmap)

---

### T02.03 -- Implement Collision Detection and Output Validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014, R-015 |
| Why | Pipeline must detect name collisions with existing modules in src/superclaude/cli/ and validate output destination is writable. Overwrite allowed only for previously portified modules (marker check). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking (collision detection), depends (marker check) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0007/spec.md

**Deliverables:**
- Collision detection logic scanning `src/superclaude/cli/` with marker-based overwrite permission, and output destination writable validation

**Steps:**
1. **[PLANNING]** Review `src/superclaude/cli/` directory for existing module structure
2. **[PLANNING]** Confirm `Generated by` / `Portified from` marker format from T01.03 resolution
3. **[EXECUTION]** Implement collision scan: check if `src/superclaude/cli/<derived_name>/` exists
4. **[EXECUTION]** If collision found, check `__init__.py` for `Generated by` / `Portified from` marker; allow overwrite only if marker present, raise `NAME_COLLISION` otherwise
5. **[EXECUTION]** Implement output destination validation: check parent directory exists and is writable; raise `OUTPUT_NOT_WRITABLE` if not
6. **[VERIFICATION]** Write unit tests: no collision, collision with marker (allow), collision without marker (block), non-writable output
7. **[COMPLETION]** Document collision detection and validation rules in D-0007/spec.md

**Acceptance Criteria:**
- Collision detection scans `src/superclaude/cli/<derived_name>/` and checks `__init__.py` for `Generated by` / `Portified from` markers
- `NAME_COLLISION` error raised when existing module lacks portification markers
- `OUTPUT_NOT_WRITABLE` error raised when output parent directory is not writable
- Unit tests pass via `uv run pytest` covering all 4 collision/validation scenarios

**Validation:**
- `uv run pytest tests/ -k "test_collision"` exits 0
- Evidence: linkable artifact produced at D-0007/spec.md

**Dependencies:** T02.02
**Rollback:** TBD (if not specified in roadmap)

---

### T02.04 -- Implement Workdir Creation and portify-config.yaml Emission

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016, R-017 |
| Why | Pipeline artifacts must be confined to .dev/portify-workdir/<cli_name>/ and portify-config.yaml must capture all resolved paths for downstream steps. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0008/spec.md

**Deliverables:**
- Workdir creation at `.dev/portify-workdir/<cli_name>/` and `portify-config.yaml` emission with all resolved paths

**Steps:**
1. **[PLANNING]** Define portify-config.yaml schema: workflow_path, cli_name, output_dir, workdir_path
2. **[PLANNING]** Confirm no source-tree artifact writing during execution (workdir isolation)
3. **[EXECUTION]** Implement workdir creation at `.dev/portify-workdir/<cli_name>/`
4. **[EXECUTION]** Emit `portify-config.yaml` with resolved paths from config.py outputs
5. **[VERIFICATION]** Verify portify-config.yaml is valid YAML with all required fields present
6. **[COMPLETION]** Document workdir structure in D-0008/spec.md

**Acceptance Criteria:**
- Workdir created at `.dev/portify-workdir/<cli_name>/` with correct directory structure
- `portify-config.yaml` emitted in workdir with fields: `workflow_path`, `cli_name`, `output_dir`, `workdir_path`
- YAML is parseable and all field values are valid filesystem paths
- Config emission documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0008/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_workdir"` exits 0
- Evidence: linkable artifact produced at D-0008/spec.md

**Dependencies:** T02.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify prerequisite validation layer is complete: path resolution, name derivation, collision detection, and config emission all function correctly.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P02-T01-T04.md

**Verification:**
- Workflow path resolution correctly finds skills, raises AMBIGUOUS_PATH and INVALID_PATH as appropriate
- CLI name derivation strips prefixes/suffixes and normalizes to kebab-case
- Collision detection uses marker-based overwrite rules and validates output writability

**Exit Criteria:**
- All 4 tasks (T02.01-T02.04) completed with unit tests passing
- portify-config.yaml schema validated with all required fields
- Error codes NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH all implemented

---

### T02.05 -- Implement Component Discovery and inventory.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019 |
| Why | Pipeline must scan SKILL.md, command files, refs/, rules/, templates/, scripts/, decisions.yaml and produce component-inventory.yaml with path, lines, purpose, type per component. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end (scanning multiple directories) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0009/spec.md

**Deliverables:**
- `inventory.py` implementing component discovery that scans skill directories and emits `component-inventory.yaml` with `{path, lines, purpose, type}` per component

**Steps:**
1. **[PLANNING]** Enumerate all component types to scan: SKILL.md, command .md files (both command directories), refs/, rules/, templates/, scripts/, decisions.yaml
2. **[PLANNING]** Define component type classification rules (skill, command, reference, rule, template, script, config)
3. **[EXECUTION]** Implement directory scanner in `inventory.py` that traverses skill directory and both command directories
4. **[EXECUTION]** For each component found: record path, count lines, infer purpose from filename/content, classify type
5. **[EXECUTION]** Emit `component-inventory.yaml` in workdir with `{path, lines, purpose, type}` per component
6. **[VERIFICATION]** Run inventory against a real skill directory; verify YAML output contains at least one component with SKILL.md
7. **[COMPLETION]** Document discovery algorithm and component type taxonomy in D-0009/spec.md

**Acceptance Criteria:**
- `inventory.py` scans SKILL.md, command files, refs/, rules/, templates/, scripts/, decisions.yaml across skill and command directories
- `component-inventory.yaml` emitted with `{path, lines, purpose, type}` for each discovered component
- Inventory contains at least one component with type referencing SKILL.md
- Discovery algorithm documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0009/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_inventory"` exits 0
- Evidence: linkable artifact produced at D-0009/spec.md

**Dependencies:** T02.04
**Rollback:** TBD (if not specified in roadmap)

---

### T02.06 -- Enforce Step 0 and Step 1 Timeouts

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | NFR-001 requires 30s timeout for input-validation (Step 0) and 60s for component-discovery (Step 1) to ensure early failure on hung operations. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (latency) |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0010/evidence.md

**Deliverables:**
- Timeout enforcement logic: 30s for input-validation step, 60s for component-discovery step

**Steps:**
1. **[PLANNING]** Review executor timeout mechanism from T01.02 OQ resolutions
2. **[PLANNING]** Confirm timeout values: 30s (Step 0 input-validation), 60s (Step 1 component-discovery)
3. **[EXECUTION]** Implement timeout wrapper for Step 0 with 30s limit
4. **[EXECUTION]** Implement timeout wrapper for Step 1 with 60s limit
5. **[VERIFICATION]** Write unit tests: verify timeout triggers after specified duration for both steps
6. **[COMPLETION]** Document timeout enforcement in D-0010/evidence.md

**Acceptance Criteria:**
- Step 0 (input-validation) enforces 30s timeout and raises appropriate error on expiry
- Step 1 (component-discovery) enforces 60s timeout and raises appropriate error on expiry
- Timeout values match NFR-001 specification exactly
- Timeout tests documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0010/evidence.md

**Validation:**
- `uv run pytest tests/ -k "test_timeout"` exits 0
- Evidence: linkable artifact produced at D-0010/evidence.md

**Dependencies:** T02.05
**Rollback:** TBD (if not specified in roadmap)

---

### T02.07 -- Implement models.py Error Code Foundations

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | models.py must define all 5 error codes (NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED) used by Phase 2 validation logic. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | model, schema |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0011/spec.md

**Deliverables:**
- Error code definitions in `src/superclaude/cli/cli_portify/models.py`: `NAME_COLLISION`, `OUTPUT_NOT_WRITABLE`, `AMBIGUOUS_PATH`, `INVALID_PATH`, `DERIVATION_FAILED`

**Steps:**
1. **[PLANNING]** Review base type patterns from T01.01 for error/exception conventions
2. **[PLANNING]** Confirm error code naming matches spec module plan (no separate failures.py)
3. **[EXECUTION]** Define `PortifyValidationError` base exception with error code field
4. **[EXECUTION]** Define all 5 error code constants and corresponding exception subclasses or enum values
5. **[VERIFICATION]** Write unit tests: each error code can be raised and caught with correct code string
6. **[COMPLETION]** Document error code taxonomy in D-0011/spec.md

**Acceptance Criteria:**
- `models.py` contains all 5 error code definitions: NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED
- Error codes are importable from `src/superclaude/cli/cli_portify/models.py`
- Each error code can be raised as a typed exception with the correct error code string
- Error taxonomy documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0011/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_error_codes"` exits 0
- Evidence: linkable artifact produced at D-0011/spec.md

**Dependencies:** T01.04 (architecture baseline)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Critical Path Override: Yes — models.py affects all downstream phases. Tier conflict: model/schema keywords (STRICT) vs. implement (STANDARD) → resolved to STANDARD because this is foundational error code definitions, not schema migration. models.py path booster toward STRICT acknowledged but error codes are a contained change.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify Step 0 and Step 1 execute deterministically; SC-001 and SC-002 pass; portify-config.yaml and component-inventory.yaml produced with valid content.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P02-END.md

**Verification:**
- Step 0 completes within 30s and produces valid portify-config.yaml with required fields (workflow_path, cli_name, output_dir)
- Step 1 completes within 60s and produces component-inventory.yaml with at least one component including SKILL.md
- All 5 error codes (NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED) are defined and testable

**Exit Criteria:**
- Milestone M1 satisfied: SC-001 (Step 0 ≤30s, valid config YAML) and SC-002 (Step 1 ≤60s, inventory ≥1 component) pass
- All 7 tasks (T02.01-T02.07) completed with deliverables D-0005 through D-0011 produced
- Phase 2 unit tests pass via `uv run pytest`
