# Phase 4 — Validation & Acceptance

Validate that generated tasklist bundles are correct, lean, Sprint CLI-compatible, and functionally identical to v3.0 generator output (M5). Then verify all 13 success criteria pass for final acceptance (V2).

### T04.01 — Manual test: run `/sc:tasklist @<roadmap>` and verify valid output bundle

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | End-to-end manual test validates that the command produces a valid multi-file tasklist bundle from a real roadmap input |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Cross-cutting scope (full pipeline execution) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0030/evidence.md`

**Deliverables:**
- Valid `tasklist-index.md` + `phase-N-tasklist.md` files produced from a test roadmap input

**Steps:**
1. **[PLANNING]** Select a test roadmap (use the v2.07 roadmap or a canonical test roadmap)
2. **[PLANNING]** Identify expected output: `tasklist-index.md` with Phase Files table + N phase files
3. **[EXECUTION]** Run `/sc:tasklist @<test-roadmap>` with `--output` pointing to a test directory
4. **[EXECUTION]** Verify `tasklist-index.md` exists with Phase Files table containing literal filenames
5. **[EXECUTION]** Verify all referenced `phase-N-tasklist.md` files exist on disk
6. **[VERIFICATION]** Index has Phase Files table with literal filenames (FR-061, FR-044, FR-045)
7. **[VERIFICATION]** All phase files start with `# Phase N — <Name>` and end with end-of-phase checkpoint
8. **[COMPLETION]** Record test output evidence

**Acceptance Criteria:**
- `tasklist-index.md` exists with Phase Files table containing literal filenames (e.g., `phase-1-tasklist.md`)
- All phase files referenced in the index exist on disk
- Phase files use correct heading format: `# Phase N — <Name>` (em-dash, ≤50 char name)
- All tasks have `T<PP>.<TT>` IDs, tier classifications, and per-task metadata

**Validation:**
- Manual check: `/sc:tasklist @<roadmap>` produces `tasklist-index.md` + phase files in output directory
- Evidence: linkable artifact produced (generated bundle listing and spot-check output)

**Dependencies:** T03.06
**Rollback:** `rm -rf <test-output-directory>`
**Notes:** RISK-004 mitigation: verify Sprint CLI filename pattern by inspecting source code

---

### T04.02 — Sprint compatibility test: verify `superclaude sprint run` discovers all phase files

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Sprint CLI must discover all phase files from the generated index for automated execution |
| Effort | M |
| Risk | High |
| Risk Drivers | Cross-cutting scope (Sprint CLI integration); deployment (runtime compatibility) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0031/evidence.md`

**Deliverables:**
- Sprint CLI finds and lists all phase files from the generated index

**Steps:**
1. **[PLANNING]** Review Sprint CLI phase discovery regex/logic in source code
2. **[PLANNING]** Identify expected filename pattern: `phase-N-tasklist.md`
3. **[EXECUTION]** Run `superclaude sprint run <generated-index> --dry-run` to test phase discovery
4. **[EXECUTION]** Verify Sprint CLI lists all N phase files from the index
5. **[VERIFICATION]** All phase files discovered (FR-066, FR-078)
6. **[VERIFICATION]** Phase count matches index Phase Files table
7. **[COMPLETION]** Record Sprint compatibility evidence

**Acceptance Criteria:**
- `superclaude sprint run <generated-index> --dry-run` discovers all phase files
- Phase file count matches the number of phases in the index Phase Files table
- Sprint CLI correctly parses literal filenames from the index
- No phase files missing or duplicated in discovery

**Validation:**
- Manual check: `superclaude sprint run <index> --dry-run` output lists all phase files
- Evidence: linkable artifact produced (Sprint CLI dry-run output)

**Dependencies:** T04.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** RISK-004: Sprint CLI naming convention must match `phase-N-tasklist.md` pattern

---

### T04.03 — Functional parity test: diff v3.0 generator output vs. `/sc:tasklist` output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | The `/sc:tasklist` output must be structurally identical to the v3.0 generator output to confirm no algorithm drift |
| Effort | M |
| Risk | High |
| Risk Drivers | Data integrity (algorithm drift detection); cross-cutting scope |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0032/evidence.md`

**Deliverables:**
- Diff output confirming structural identity between v3.0 generator and `/sc:tasklist` outputs; any delta is non-functional formatting only

**Steps:**
1. **[PLANNING]** Select canonical test roadmap input (same roadmap for both generators)
2. **[PLANNING]** Generate output using v3.0 generator prompt directly
3. **[EXECUTION]** Generate output using `/sc:tasklist` command
4. **[EXECUTION]** Diff the two output bundles file-by-file
5. **[VERIFICATION]** Any differences are non-functional formatting only (FR-005, NFR-002)
6. **[VERIFICATION]** No algorithmic differences: same tasks, same IDs, same tiers, same deliverables
7. **[COMPLETION]** Record functional parity evidence with diff output

**Acceptance Criteria:**
- Output bundles are structurally identical when compared file-by-file
- Any delta is non-functional: whitespace, line breaks, timestamp differences only
- Same task count, same task IDs, same phase assignments, same tier classifications
- RISK-001 confirmed mitigated: no algorithm drift

**Validation:**
- Manual check: `diff -r <v3.0-output> <sc-tasklist-output>` shows only non-functional differences
- Evidence: linkable artifact produced (diff output)

**Dependencies:** T04.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** RISK-001: character-level diff required; any non-formatting delta is a defect

---

### T04.04 — Leanness check: verify phase files contain no registries, matrices, or templates

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Phase files must contain only task content per Sprint format — no cross-phase metadata that belongs in the index |
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
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0033/evidence.md`

**Deliverables:**
- Phase files confirmed lean: no Deliverable Registry, Traceability Matrix, or template sections

**Steps:**
1. **[PLANNING]** Identify prohibited content in phase files: registries, traceability matrices, embedded templates
2. **[EXECUTION]** Grep all generated `phase-N-tasklist.md` files for "Deliverable Registry", "Traceability Matrix", "Template"
3. **[EXECUTION]** Verify zero matches for prohibited section headings
4. **[VERIFICATION]** Phase files contain only: phase heading, phase goal, tasks, inline checkpoints (FR-064, NFR-008)
5. **[COMPLETION]** Record leanness check evidence

**Acceptance Criteria:**
- No phase file contains "Deliverable Registry" section
- No phase file contains "Traceability Matrix" section
- No phase file contains "Template" sections (execution log, checkpoint report, feedback)
- Phase files contain only task content and checkpoints per Sprint format

**Validation:**
- Manual check: `grep -l "Deliverable Registry\|Traceability Matrix" phase-*-tasklist.md` returns no matches
- Evidence: linkable artifact produced (grep output showing no matches)

**Dependencies:** T04.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T04.05 — Task description quality: verify all tasks are standalone per §7.N

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | Every task description must name a specific artifact, use a concrete verb, and reference no external context per §7.N |
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
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0034/evidence.md`

**Deliverables:**
- 100% of tasks pass standalone description criteria: named artifact, concrete verb, no external references

**Steps:**
1. **[PLANNING]** Read §7.N Minimum Task Specificity Rule: (1) named artifact, (2) action verb + explicit object, (3) no cross-task prose dependency
2. **[EXECUTION]** Spot-check every task title and description across all phase files
3. **[EXECUTION]** Flag any task using generic phrases ("the feature", "the component") or external references ("as discussed")
4. **[VERIFICATION]** 100% of tasks pass all 3 criteria (FR-065, NFR-009, §9 AC #11)
5. **[COMPLETION]** Record quality check evidence

**Acceptance Criteria:**
- Every task title names a specific file, function, or component
- Every task description contains an imperative verb with an explicit direct object
- No task description references information only available in another task's description
- 100% pass rate across all phase files

**Validation:**
- Manual check: Review all task titles for specificity; grep for prohibited phrases ("as discussed", "the above")
- Evidence: linkable artifact produced (task quality spot-check results)

**Dependencies:** T04.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### Checkpoint: Phase 4 / Tasks T04.01–T04.05

**Purpose:** Verify output validation and quality checks pass before proceeding to final acceptance criteria.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-T01-T05.md`

**Verification:**
- Manual test produced valid output bundle (T04.01)
- Sprint CLI discovers all phase files (T04.02)
- Functional parity confirmed with v3.0 (T04.03)

**Exit Criteria:**
- T04.01 through T04.05 completed with all checks passing
- No algorithm drift detected (RISK-001 confirmed mitigated)
- Phase files are lean and task descriptions are standalone

---

### T04.06 — Verify SC-001 through SC-005: discoverability, output format, lint

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Why | Success criteria SC-001 through SC-005 validate discoverability, output format, and lint compliance |
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
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0035/evidence.md`

**Deliverables:**
- SC-001 through SC-005 all verified as passing

**Steps:**
1. **[PLANNING]** Review SC-001–SC-005 criteria from roadmap Success Criteria table
2. **[EXECUTION]** SC-001: Verify `/sc:tasklist` discoverable in Claude Code command palette
3. **[EXECUTION]** SC-002: Verify output `tasklist-index.md` has Phase Files table with literal filenames
4. **[EXECUTION]** SC-003: Verify output `phase-N-tasklist.md` files match Sprint CLI naming
5. **[EXECUTION]** SC-004: Verify all tasks have `T<PP>.<TT>` IDs, tier classifications, metadata
6. **[EXECUTION]** SC-005: Verify `make lint-architecture` passes with zero errors
7. **[VERIFICATION]** All 5 criteria pass
8. **[COMPLETION]** Record per-criterion evidence

**Acceptance Criteria:**
- SC-001: `/sc:tasklist` discoverable after `superclaude install`
- SC-002: Index Phase Files table contains literal filenames
- SC-003: Phase files use `phase-N-tasklist.md` naming convention
- SC-004: All tasks have correctly formatted IDs, tiers, and metadata

**Validation:**
- Manual check: Each criterion verified individually with pass/fail result
- Evidence: linkable artifact produced (per-criterion verification results)

**Dependencies:** T04.01, T03.06, T03.07
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T04.07 — Verify SC-006 through SC-009: Sprint compatibility, lean output, stage order, v3.0 parity

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | Success criteria SC-006 through SC-009 validate Sprint compatibility, output leanness, stage ordering, and functional parity |
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
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0036/evidence.md`

**Deliverables:**
- SC-006 through SC-009 all verified as passing

**Steps:**
1. **[PLANNING]** Review SC-006–SC-009 criteria from roadmap Success Criteria table
2. **[EXECUTION]** SC-006: Verify `superclaude sprint run` discovers all phase files
3. **[EXECUTION]** SC-007: Verify phase files are lean (no registries/matrices/templates)
4. **[EXECUTION]** SC-008: Verify stages execute in order 1–6 with TodoWrite reporting
5. **[EXECUTION]** SC-009: Verify output identical to v3.0 generator on same input
6. **[VERIFICATION]** All 4 criteria pass
7. **[COMPLETION]** Record per-criterion evidence

**Acceptance Criteria:**
- SC-006: Sprint CLI discovers all phase files from generated index
- SC-007: Phase files contain no registries, matrices, or templates
- SC-008: Stages execute in order (Ingest → Parse → Convert → Enrich → Emit → Check) with TodoWrite
- SC-009: Output identical to v3.0 generator on same input (diff shows only formatting differences)

**Validation:**
- Manual check: Each criterion verified individually with pass/fail result
- Evidence: linkable artifact produced (per-criterion verification results)

**Dependencies:** T04.02, T04.03, T04.04
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T04.08 — Verify SC-010 through SC-012: quality gates and atomic output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | Success criteria SC-010 through SC-012 validate pre-write quality gates and atomic output behavior |
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
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0037/evidence.md`

**Deliverables:**
- SC-010 through SC-012 all verified as passing: pre-write gates enforced, no files written on Stage 1–4 failure

**Steps:**
1. **[PLANNING]** Review SC-010–SC-012 criteria from roadmap Success Criteria table
2. **[EXECUTION]** SC-010: Verify pre-write semantic quality gate passes (metadata completeness, unique IDs, no placeholders, traceability)
3. **[EXECUTION]** SC-011: Verify pre-write structural quality gate passes (task count bounds, adjacency, no circular deps, XL splitting, confidence format)
4. **[EXECUTION]** SC-012: Verify no output files written if Stage 1–4 validation fails (test with intentionally invalid input)
5. **[VERIFICATION]** All 3 criteria pass
6. **[COMPLETION]** Record per-criterion evidence

**Acceptance Criteria:**
- SC-010: Pre-write semantic quality gate enforced (§8.1 checks 9–12)
- SC-011: Pre-write structural quality gate enforced (§8.2 checks 13–17)
- SC-012: No output files written when Stage 1–4 structural validations fail
- Atomic output behavior confirmed: all-or-nothing file emission

**Validation:**
- Manual check: Test with invalid roadmap input to confirm no output files created
- Evidence: linkable artifact produced (quality gate enforcement verification)

**Dependencies:** T04.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** RISK-008 must be resolved in Phase 2 (T02.11) before this verification

---

### T04.09 — Verify SC-013: task descriptions standalone

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | Every task description must be independently understandable without reference to other tasks or external context |
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
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Deliverables:**
- SC-013 verified: every task description passes standalone check per §7.N

**Steps:**
1. **[PLANNING]** Review §7.N standalone criteria: named artifact, concrete verb, no external references
2. **[EXECUTION]** Review all task descriptions in generated output for SC-013 compliance
3. **[EXECUTION]** Flag any non-conforming descriptions
4. **[VERIFICATION]** SC-013 passes: every task description is standalone
5. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- Every generated task names a specific artifact or target
- Every task contains an imperative verb with explicit direct object
- No task references external conversation context or other task descriptions
- SC-013 criterion passes

**Validation:**
- Manual check: All task descriptions reviewed for §7.N compliance
- Evidence: linkable artifact produced (standalone check results)

**Dependencies:** T04.05
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T04.10 — Verify manual TasklistGenPrompt.md workflow is superseded by `/sc:tasklist`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | The `/sc:tasklist` command must provide equivalent functionality to the manual workflow, making it the recommended approach |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0039/evidence.md`

**Deliverables:**
- Confirmation that `/sc:tasklist` provides equivalent functionality; internal docs updated to reference `/sc:tasklist`

**Steps:**
1. **[PLANNING]** Review TasklistGenPrompt.md manual workflow
2. **[PLANNING]** Compare capabilities with `/sc:tasklist` command
3. **[EXECUTION]** Verify `/sc:tasklist` covers all manual workflow capabilities: roadmap input, spec context, output generation
4. **[EXECUTION]** Update internal documentation to reference `/sc:tasklist` as the recommended approach (FR-004)
5. **[VERIFICATION]** Manual workflow is superseded — no functional gap
6. **[COMPLETION]** Record supersession evidence

**Acceptance Criteria:**
- `/sc:tasklist` provides all functionality of the manual TasklistGenPrompt.md workflow
- Internal documentation references `/sc:tasklist` as the recommended approach
- No functional gaps identified between manual and command-based workflows
- TasklistGenPrompt.md preserved as historical reference (not deleted)

**Validation:**
- Manual check: Feature comparison confirms functional equivalence
- Evidence: linkable artifact produced (feature comparison documentation)

**Dependencies:** T04.01
**Rollback:** N/A (documentation update only)
**Notes:** TasklistGenPrompt.md stays in `.dev/` as historical reference per §8.2

---

### Checkpoint: End of Phase 4

**Purpose:** Verify all 13 success criteria pass and the implementation meets all acceptance criteria from §9.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`

**Verification:**
- All 13 success criteria (SC-001 through SC-013) verified as passing
- Functional parity with v3.0 generator confirmed (RISK-001 mitigated)
- Manual TasklistGenPrompt.md workflow confirmed superseded

**Exit Criteria:**
- T04.01 through T04.10 all completed with all criteria passing
- No unresolved risks or defects
- Release ready: `/sc:tasklist` command/skill pair fully implemented, tested, and validated
