# Phase 1 -- Foundation and Prerequisite Remediation

Eliminate known API drift in ref files, establish the command/protocol split architecture, and resolve all 10 blocking open questions before downstream implementation begins. This phase is the hard prerequisite for all subsequent work — no Phase 2 tasks may start until Phase 1 exit criteria pass.

---

### T01.01 -- Update refs/pipeline-spec.md to Match Live API Signatures

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-005 |
| Why | Ref file staleness (RISK-002) is the highest-priority prerequisite; downstream code generation depends on accurate API field names and signatures. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data/schema (GateCriteria field alignment, SemanticCheck contract correction) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0001/evidence.md

**Deliverables:**
- Updated `refs/pipeline-spec.md` with tier casing fixed (`enforcement_tier="STRICT"`), `GateCriteria` field names aligned to live dataclass, `SemanticCheck` contract corrected to `Callable[[str], bool]` signature

**Steps:**
1. **[PLANNING]** Identify all field names in current `refs/pipeline-spec.md` that reference `models.py` and `gates.py` API surfaces
2. **[PLANNING]** Read live `src/superclaude/cli/pipeline/models.py` and `src/superclaude/cli/pipeline/gates.py` to capture current signatures
3. **[EXECUTION]** Fix tier casing: replace all instances of `tier="strict"` with `enforcement_tier="STRICT"` in pipeline-spec.md
4. **[EXECUTION]** Align `GateCriteria` field names to match live dataclass constructor fields
5. **[EXECUTION]** Correct `SemanticCheck` contract from `tuple[bool, str]` to `Callable[[str], bool]` signature
6. **[VERIFICATION]** Diff every field name in updated pipeline-spec.md against live API — zero mismatches required
7. **[COMPLETION]** Record diff results as evidence in D-0001/evidence.md

**Acceptance Criteria:**
- File `refs/pipeline-spec.md` contains zero field name mismatches when diffed against live `models.py` and `gates.py` API signatures
- All `enforcement_tier` values use UPPER_CASE enum format (STRICT, STANDARD, LIGHT, EXEMPT)
- `SemanticCheck` contract references `Callable[[str], bool]` exclusively, with no residual `tuple[bool, str]` references
- Changes traceable to specific R-004, R-005 roadmap items via D-0001 evidence artifact

**Validation:**
- Manual check: `diff` output between ref field names and live API signatures shows zero discrepancies
- Evidence: linkable artifact produced at .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0001/evidence.md

**Dependencies:** None (first task in critical path)
**Rollback:** `git checkout -- refs/pipeline-spec.md`
**Notes:** Addresses RISK-002 (ref file staleness). Runs in parallel with T01.03-T01.06 (M1.2).

---

### T01.02 -- Update refs/code-templates.md and Create Stale-Ref Detector Script

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006, R-007 |
| Why | Code templates reference incorrect import paths and base class constructors; a stale-ref detector prevents future drift. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data alignment (12 file templates, import paths), cross-cutting (affects all generated files) |
| Tier | STRICT |
| Confidence | [██████----] 75% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0002, D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0002/evidence.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0003/spec.md

**Deliverables:**
- Updated `refs/code-templates.md` with all import paths aligned to `superclaude.cli.pipeline.models` / `.gates`, gate template using actual `GateCriteria` constructor fields, all 12 file templates verified against correct base classes
- Stale-ref detector script that compares ref field names against live API signatures and exits non-zero on mismatch

**Steps:**
1. **[PLANNING]** Catalog all import statements and base class references across 12 file templates in `refs/code-templates.md`
2. **[PLANNING]** Cross-reference against live API signatures captured in T01.01
3. **[EXECUTION]** Align all import paths to `superclaude.cli.pipeline.models` and `superclaude.cli.pipeline.gates`
4. **[EXECUTION]** Fix gate template to use actual `GateCriteria` constructor fields from live dataclass
5. **[EXECUTION]** Create stale-ref detector script in `scripts/` that extracts field names from refs and diffs against live API
6. **[VERIFICATION]** Run stale-ref detector against updated refs — must exit 0 with zero mismatches
7. **[COMPLETION]** Record verification results in D-0002/evidence.md and script specification in D-0003/spec.md

**Acceptance Criteria:**
- All 12 file templates in `refs/code-templates.md` reference `superclaude.cli.pipeline.models` and `.gates` import paths exclusively
- Stale-ref detector script at `scripts/check-ref-staleness.py` exits 0 when run against updated refs and live API
- `GateCriteria` constructor in gate template matches live dataclass field names exactly
- Evidence artifacts D-0002 and D-0003 exist with verification data

**Validation:**
- `uv run python scripts/check-ref-staleness.py` exits 0
- Evidence: linkable artifacts produced at D-0002/evidence.md and D-0003/spec.md

**Dependencies:** T01.01 (live API signatures must be captured first)
**Rollback:** `git checkout -- refs/code-templates.md`
**Notes:** Addresses RISK-002. Stale-ref detector is reusable in Phase 4 (M4.1) for conformance checking.

---

### T01.03 -- Create sc-cli-portify-protocol Directory with Migrated SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008, R-009 |
| Why | The command/protocol split requires a new protocol directory to house the migrated skill logic separately from the command shim. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STRICT |
| Confidence | [███████---] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0004/evidence.md

**Deliverables:**
- Directory `src/superclaude/skills/sc-cli-portify-protocol/` containing migrated `SKILL.md`, `__init__.py`, and `refs/` subdirectory (moved from `sc-cli-portify/refs/`)

**Steps:**
1. **[PLANNING]** Verify current `src/superclaude/skills/sc-cli-portify/` structure and identify all files to migrate
2. **[PLANNING]** Confirm `refs/` directory contents match updated files from T01.01 and T01.02
3. **[EXECUTION]** Create `src/superclaude/skills/sc-cli-portify-protocol/` directory
4. **[EXECUTION]** Migrate `SKILL.md` from `sc-cli-portify/` to `sc-cli-portify-protocol/`
5. **[EXECUTION]** Create `__init__.py` and move `refs/` directory with updated ref files
6. **[VERIFICATION]** Verify directory structure matches expected layout: SKILL.md, __init__.py, refs/ with all ref files
7. **[COMPLETION]** Record directory listing as evidence in D-0004/evidence.md

**Acceptance Criteria:**
- Directory `src/superclaude/skills/sc-cli-portify-protocol/` exists with `SKILL.md`, `__init__.py`, and `refs/` subdirectory
- `refs/` contains updated `pipeline-spec.md` and `code-templates.md` from T01.01-T01.02
- `__init__.py` is present and importable (no syntax errors)
- Migration traceable via D-0004/evidence.md with directory listing

**Validation:**
- Manual check: `ls -R src/superclaude/skills/sc-cli-portify-protocol/` shows expected structure
- Evidence: linkable artifact produced at D-0004/evidence.md

**Dependencies:** T01.01, T01.02 (ref files must be updated before migration)
**Rollback:** `rm -rf src/superclaude/skills/sc-cli-portify-protocol/`
**Notes:** Runs in parallel with T01.01-T01.02 for directory creation; ref file copy waits for T01.01-T01.02 completion.

---

### T01.04 -- Create cli-portify.md Command Shim with Argument Parsing

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The thin command shim provides the user-facing entry point that validates arguments and delegates to the protocol skill. |
| Effort | M |
| Risk | Low |
| Risk Drivers | none |
| Tier | STRICT |
| Confidence | [███████---] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0005/spec.md

**Deliverables:**
- File `src/superclaude/commands/cli-portify.md` implementing argument parsing (`--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`), input validation with 6 error codes (MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED), and delegation to `Skill sc:cli-portify-protocol`

**Steps:**
1. **[PLANNING]** Review existing command shim patterns in `src/superclaude/commands/` for structural conventions
2. **[PLANNING]** Define the 6 error code behaviors and argument validation rules from roadmap spec
3. **[EXECUTION]** Create `src/superclaude/commands/cli-portify.md` with argument section, validation section, and skill delegation
4. **[EXECUTION]** Implement all 6 error codes with user-facing error messages and corrective action hints
5. **[EXECUTION]** Add `Skill sc:cli-portify-protocol` delegation block with context passing
6. **[VERIFICATION]** Review command shim against existing patterns (e.g., `cli-portify.md` vs `tasklist.md` command) for structural consistency
7. **[COMPLETION]** Record command specification in D-0005/spec.md

**Acceptance Criteria:**
- File `src/superclaude/commands/cli-portify.md` exists and follows project command shim conventions
- All 5 arguments (`--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`) are documented with types and defaults
- All 6 error codes (MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED) produce distinct error messages
- Command delegates to `Skill sc:cli-portify-protocol` with validated context

**Validation:**
- Manual check: command shim structure matches existing commands in `src/superclaude/commands/`
- Evidence: linkable artifact produced at D-0005/spec.md

**Dependencies:** None (can run in parallel with T01.01-T01.03)
**Rollback:** `rm src/superclaude/commands/cli-portify.md`

---

### T01.05 -- Promote YAML Frontmatter and Configure verify-sync Coverage

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011, R-012 |
| Why | YAML frontmatter standardizes skill metadata; verify-sync coverage ensures the new protocol directory stays in sync across src/ and .claude/. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████---] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0006/evidence.md

**Deliverables:**
- Updated `SKILL.md` in `sc-cli-portify-protocol/` with promoted YAML frontmatter (name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint)
- Updated `make verify-sync` configuration covering `sc-cli-portify-protocol/` directory

**Steps:**
1. **[PLANNING]** Review existing skill YAML frontmatter patterns in other skills for field conventions
2. **[PLANNING]** Identify verify-sync configuration file and understand inclusion patterns
3. **[EXECUTION]** Add YAML frontmatter block to `sc-cli-portify-protocol/SKILL.md` with all 8 required fields
4. **[EXECUTION]** Update verify-sync configuration to include `sc-cli-portify-protocol/` in sync validation
5. **[VERIFICATION]** Run `make verify-sync` and confirm `sc-cli-portify-protocol/` is included in sync check
6. **[COMPLETION]** Record verify-sync output in D-0006/evidence.md

**Acceptance Criteria:**
- `sc-cli-portify-protocol/SKILL.md` contains YAML frontmatter with all 8 fields (name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint)
- `make verify-sync` includes `sc-cli-portify-protocol/` in its validation scope
- `make verify-sync` exits 0 when `src/` and `.claude/` copies match
- Evidence artifact D-0006 records successful verify-sync output

**Validation:**
- `make verify-sync` exits 0
- Evidence: linkable artifact produced at D-0006/evidence.md

**Dependencies:** T01.03 (protocol directory must exist)
**Rollback:** Revert SKILL.md frontmatter and verify-sync config changes via git

---

### T01.06 -- Mark sc-cli-portify Directory for Deprecation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | The old monolithic skill directory must be deprecated to prevent confusion; actual removal deferred to Phase 5 after all validation passes. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | LIGHT |
| Confidence | [██████----] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0007/notes.md

**Deliverables:**
- Deprecation notice added to `sc-cli-portify/SKILL.md` header indicating replacement by `sc-cli-portify-protocol/` and planned removal in Phase 5

**Steps:**
1. **[PLANNING]** Confirm `sc-cli-portify/SKILL.md` exists and is the correct target
2. **[EXECUTION]** Add deprecation notice to top of `sc-cli-portify/SKILL.md`: "DEPRECATED: Replaced by sc-cli-portify-protocol/. Scheduled for removal after Phase 5 validation."
3. **[VERIFICATION]** Verify deprecation notice is present at top of file
4. **[COMPLETION]** Record deprecation action in D-0007/notes.md

**Acceptance Criteria:**
- `sc-cli-portify/SKILL.md` contains deprecation notice as first non-frontmatter content
- Notice references `sc-cli-portify-protocol/` as replacement
- Notice indicates Phase 5 removal timeline
- D-0007/notes.md documents the deprecation action

**Validation:**
- Manual check: deprecation notice visible at top of `sc-cli-portify/SKILL.md`
- Evidence: linkable artifact produced at D-0007/notes.md

**Dependencies:** T01.03 (replacement directory must exist before deprecating old one)
**Rollback:** Remove deprecation notice from SKILL.md

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.06

**Purpose:** Verify ref file alignment and command/protocol split architecture are correctly established before proceeding to open question resolution.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P01-T01-T06.md
**Verification:**
- Stale-ref detector script exits 0 against updated ref files
- Protocol directory structure matches expected layout with all migrated files
- `make verify-sync` passes including `sc-cli-portify-protocol/`
**Exit Criteria:**
- Zero field name mismatches between refs and live API
- Command shim and protocol SKILL.md both discoverable from `src/` and `.claude/`
- Old directory marked deprecated with clear replacement pointer

---

### T01.07 -- Confirm: T01.09 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Tier classification confidence for T01.09 (open question resolution) is below threshold; confirm STANDARD tier is appropriate for decision documentation work. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T01.09 with justification

**Steps:**
1. **[PLANNING]** Review T01.09 task scope: resolve 10 open questions, produce decisions.yaml
2. **[EXECUTION]** Confirm or override STANDARD tier classification based on task characteristics
3. **[COMPLETION]** Record confirmation: "Tier confirmed" or "Tier overridden to [X] because [reason]"

**Acceptance Criteria:**
- Tier decision recorded with justification
- Decision documented in feedback log if overridden
- T01.09 unblocked for execution
- Override reason documented if changed from STANDARD

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T01.08 -- Confirm: T01.10 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Tier classification confidence for T01.10 (exit criteria validation) is below threshold; confirm EXEMPT tier is appropriate for validation-only work. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T01.10 with justification

**Steps:**
1. **[PLANNING]** Review T01.10 task scope: verify Phase 1 exit criteria pass
2. **[EXECUTION]** Confirm or override EXEMPT tier classification
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- Decision documented in feedback log if overridden
- T01.10 unblocked for execution
- Override reason documented if changed from EXEMPT

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T01.09 -- Resolve All 10 Open Questions with Documented Decisions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014, R-015 |
| Why | All 10 OQs must be resolved before Phase 2; 6 are blocking for design work (OQ-002, 003, 004, 007, 008, 010). |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting (OQ resolutions affect multiple phases), dependency (blocking OQs gate Phase 2) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008, D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0008/spec.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0009/spec.md

**Deliverables:**
- Documented resolutions for all 10 open questions (OQ-001 through OQ-010) with implementation decisions
- `decisions.yaml` file recording blocking OQ implementation decisions (OQ-002: TurnLedger, OQ-003: dry-run behavior, OQ-004: integration schema, OQ-007: approval gate mechanism, OQ-008: default output path, OQ-010: step boundary algorithm)

**Steps:**
1. **[PLANNING]** List all 10 OQs with their blocking status and proposed resolutions from roadmap
2. **[PLANNING]** Inspect codebase for OQ-002 (TurnLedger presence in pipeline API)
3. **[EXECUTION]** Resolve each OQ per roadmap-specified resolution: OQ-001 (spec typo), OQ-002 (TurnLedger check), OQ-003 (dry-run = Phases 0-2 only), OQ-004 (integration schema fields), OQ-005 (batch_dynamic=false), OQ-006 (verify refs/analysis-protocol.md), OQ-007 (TodoWrite checkpoint pattern), OQ-008 (default output path), OQ-009 (tests/ directory), OQ-010 (step boundary algorithm extraction)
4. **[EXECUTION]** Create `decisions.yaml` with blocking OQ resolutions as structured entries
5. **[EXECUTION]** Extract step boundary algorithm from current SKILL.md into `refs/analysis-protocol.md` per OQ-010
6. **[VERIFICATION]** Verify all 10 OQs have documented resolutions; blocking OQs have entries in decisions.yaml
7. **[COMPLETION]** Record resolution summaries in D-0008/spec.md and decisions.yaml content in D-0009/spec.md

**Acceptance Criteria:**
- All 10 OQs (OQ-001 through OQ-010) have documented resolutions in D-0008/spec.md
- `decisions.yaml` contains structured entries for all 6 blocking OQs (002, 003, 004, 007, 008, 010)
- OQ-010 step boundary algorithm documented in `refs/analysis-protocol.md`
- No OQ left unresolved or marked "TBD"

**Validation:**
- Manual check: `decisions.yaml` contains 6 blocking OQ entries with non-empty resolution fields
- Evidence: linkable artifacts produced at D-0008/spec.md and D-0009/spec.md

**Dependencies:** T01.01 (codebase inspection for OQ-002 requires understanding of live API)
**Rollback:** Revert decisions.yaml and OQ documentation changes via git

---

### T01.10 -- Validate Phase 1 Exit Criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Phase 1 exit criteria must pass before Phase 2 begins; this is the formal gate between phases. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Phase 1 exit criteria validation results

**Steps:**
1. **[PLANNING]** Enumerate Phase 1 exit criteria from roadmap
2. **[EXECUTION]** Verify: no legacy structural conflicts remain
3. **[EXECUTION]** Verify: protocol and command discoverable from both `src/` and `.claude/`
4. **[EXECUTION]** Verify: ref files verified against live API with zero mismatches (run stale-ref detector)
5. **[EXECUTION]** Verify: all 10 OQs resolved and documented
6. **[VERIFICATION]** Run `make verify-sync` — must pass for new protocol directory
7. **[COMPLETION]** Record pass/fail for each exit criterion

**Acceptance Criteria:**
- Stale-ref detector exits 0 (zero API mismatches)
- `make verify-sync` exits 0 including `sc-cli-portify-protocol/`
- All 10 OQs resolved per decisions.yaml
- Protocol and command files exist in both `src/` and `.claude/` locations

**Validation:**
- `make verify-sync` exits 0
- Evidence: exit criteria checklist with pass/fail for each criterion

**Dependencies:** T01.01 through T01.09 (all Phase 1 tasks must complete)
**Rollback:** N/A (validation only)

---

### Checkpoint: End of Phase 1

**Purpose:** Gate Phase 2 entry by confirming all Foundation and Prerequisite Remediation work is complete and verified.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P01-END.md
**Verification:**
- Stale-ref detector script exits 0 with zero API field mismatches
- `make verify-sync` passes for `sc-cli-portify-protocol/` directory
- All 10 OQs have documented resolutions in decisions.yaml
**Exit Criteria:**
- No legacy structural conflicts remain in refs or skill directories
- Protocol and command are discoverable from both `src/` and `.claude/`
- All blocking OQs (002, 003, 004, 007, 008, 010) have implementation decisions recorded
