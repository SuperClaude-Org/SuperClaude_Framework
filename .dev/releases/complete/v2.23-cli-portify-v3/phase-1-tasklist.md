# Phase 1 -- Template Foundation

Verify scope boundaries, trace downstream dependencies, and create the reusable release spec template. This phase establishes the foundational artifact and confirms all pre-implementation constraints before any behavioral changes begin.

### T01.01 -- Execute Pre-Implementation Verification Checklist

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002, R-003, R-004, R-005 |
| Why | The roadmap requires confirming scope (4 modified files + 1 new), tracing downstream consumers, verifying Phases 0-2 are unchanged, and documenting the sync requirement before any implementation begins. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001, D-0002, D-0003, D-0004 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0001/evidence.md
- TASKLIST_ROOT/artifacts/D-0002/evidence.md
- TASKLIST_ROOT/artifacts/D-0003/evidence.md
- TASKLIST_ROOT/artifacts/D-0004/notes.md

**Deliverables:**
1. Change inventory listing the 4 files to be modified (`SKILL.md`, `cli-portify.md`, `pipeline-spec.md`, `decisions.yaml`) and 1 file to be created (`release-spec-template.md`)
2. Dependency trace documenting all downstream consumers of the return contract (`sc:roadmap` and `sc:tasklist`) and the reviewed spec artifact
3. Regression checklist confirming Phases 0-2 behavior is unchanged and no phase references old Phase 3/4 outputs
4. Sync requirement confirmation that `src/superclaude/` changes require `make sync-dev`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` to identify current Phase 3 and Phase 4 outputs
2. **[PLANNING]** Check which downstream skills consume the return contract and reviewed spec
3. **[EXECUTION]** List the 4 files to be modified and 1 file to be created per roadmap specification
4. **[EXECUTION]** Trace `sc:roadmap` and `sc:tasklist` dependency on the return contract schema
5. **[EXECUTION]** Verify Phases 0-2 in SKILL.md produce no references to old Phase 3/4 outputs
6. **[VERIFICATION]** Confirm all 4 deliverables are documented with evidence
7. **[COMPLETION]** Record verification results in evidence artifacts

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0001/evidence.md` exists listing exactly 5 files (4 modified + 1 created)
- Downstream consumers of the return contract (`sc:roadmap` and `sc:tasklist`) and the reviewed spec artifact identified with specific contract fields they consume
- Phases 0-2 contain zero references to old Phase 3/4 output artifacts (code files, integration tests)
- Sync requirement documented: `make sync-dev` required after `src/superclaude/` changes

**Validation:**
- Manual check: Verify change inventory matches roadmap's 4+1 file list and dependency trace covers both downstream consumers
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0001/evidence.md through D-0004/notes.md)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Read-only verification task; no code changes.

---

### T01.02 -- Create Release Spec Template at src/superclaude/examples/release-spec-template.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006, R-007, R-008, R-010 |
| Why | The roadmap requires a reusable release spec template (FR-017) with frontmatter schema, 12 sections, `{{SC_PLACEHOLDER:name}}` sentinel format, and conditional section markers for spec-type-specific sections. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005, D-0006, D-0007 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0005/spec.md
- TASKLIST_ROOT/artifacts/D-0006/evidence.md
- TASKLIST_ROOT/artifacts/D-0007/evidence.md

**Deliverables:**
1. Template file at `src/superclaude/examples/release-spec-template.md` with frontmatter schema (quality score fields) and all 12 sections: problem statement, solution overview, FRs, architecture, interface contracts, NFRs, risk assessment, test plan, migration, downstream inputs, open items, brainstorm gap analysis
2. Sentinel collision validation confirming `{{SC_PLACEHOLDER:name}}` format does not collide with template prose content
3. Conditional section markers (FR-060.7) on sections only required for specific spec types (migration for portification, backward compatibility for refactoring)

**Steps:**
1. **[PLANNING]** Review roadmap section-to-source mapping table to determine template section structure
2. **[PLANNING]** Identify which sections are conditional vs mandatory per spec type (new feature, refactoring, portification, infrastructure)
3. **[EXECUTION]** Create `src/superclaude/examples/release-spec-template.md` with frontmatter schema including quality score fields
4. **[EXECUTION]** Add all 12 template sections using `{{SC_PLACEHOLDER:name}}` sentinel format (Constraint 5)
5. **[EXECUTION]** Mark conditional sections with explicit indicators per FR-060.7
6. **[EXECUTION]** Validate template works for all 4 spec types: new feature, refactoring, portification, infrastructure
7. **[VERIFICATION]** Run regex scan to confirm zero sentinel collisions with template prose
8. **[COMPLETION]** Record sentinel validation results and cross-type reusability confirmation

**Acceptance Criteria:**
- File `src/superclaude/examples/release-spec-template.md` exists with frontmatter schema and all 12 named sections mapping 1:1 to the section-to-source mapping table from the spec
- Zero sentinel collisions: `grep -c '{{SC_PLACEHOLDER:' src/superclaude/examples/release-spec-template.md` returns only intentional placeholder uses
- Conditional sections (migration, backward compatibility) have explicit conditional indicators distinguishing them from mandatory sections
- Template validated against all 4 spec types (new feature, refactoring, portification, infrastructure) per debate D-13

**Validation:**
- Manual check: Template contains all 12 sections named in roadmap with `{{SC_PLACEHOLDER:name}}` sentinels and conditional markers
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0005/spec.md)

**Dependencies:** T01.01
**Rollback:** `git checkout -- src/superclaude/examples/release-spec-template.md`
**Notes:** Template location is Constraint 4: `src/superclaude/examples/release-spec-template.md`.

---

### T01.03 -- Write Sentinel Self-Validation Regex Check (SC-003)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | The roadmap requires a self-validation check (SC-003) that uses regex to scan generated specs for remaining `{{SC_PLACEHOLDER:name}}` sentinels, ensuring no unresolved placeholders in output. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0008/spec.md

**Deliverables:**
1. Regex-based self-validation check in SKILL.md that scans generated spec output for remaining `{{SC_PLACEHOLDER:` sentinels and reports any unresolved placeholders

**Steps:**
1. **[PLANNING]** Identify where in the SKILL.md pipeline the sentinel check should execute (after Phase 3 content population)
2. **[PLANNING]** Define the regex pattern to match `{{SC_PLACEHOLDER:...}}` format
3. **[EXECUTION]** Write the self-validation check logic as a SKILL.md instruction block
4. **[EXECUTION]** Specify that zero remaining sentinels is the pass condition
5. **[VERIFICATION]** Confirm the regex pattern matches all sentinel variants and produces zero false positives
6. **[COMPLETION]** Document the check's integration point and expected behavior

**Acceptance Criteria:**
- SKILL.md contains a self-validation step that applies regex `\{\{SC_PLACEHOLDER:[^}]+\}\}` to generated spec output
- Check reports pass when zero sentinels remain and fail with sentinel count when unresolved placeholders exist
- Check is positioned after Phase 3 content population step (3b) in the pipeline
- Check behavior documented in TASKLIST_ROOT/artifacts/D-0008/spec.md

**Validation:**
- Manual check: Regex pattern correctly matches `{{SC_PLACEHOLDER:example}}` format and self-validation step is present in SKILL.md pipeline
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0008/spec.md)

**Dependencies:** T01.02
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |

**Purpose:** Verify Gate A criteria are met: template exists at canonical location, zero sentinel collisions, sections map 1:1 to mapping table, dependency trace complete, cross-type reusability confirmed.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P01-END.md
**Verification:**
- Template file exists at `src/superclaude/examples/release-spec-template.md` with all 12 sections
- Zero sentinel collisions confirmed by regex scan
- Template sections map 1:1 to the section-to-source mapping table from the spec
- Dependency trace complete: downstream consumers (`sc:roadmap`, `sc:tasklist`) identified with specific contract fields
**Exit Criteria:**
- All 3 tasks (T01.01-T01.03) completed with deliverables D-0001 through D-0008 produced
- Cross-type reusability confirmed for all 4 spec types (new feature, refactoring, portification, infrastructure)
- Pre-implementation verification checklist fully documented
