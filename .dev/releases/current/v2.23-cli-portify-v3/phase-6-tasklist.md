# Phase 6 -- Sync & Documentation

Propagate changes and update documentation. This phase runs component sync, updates architectural decision records, refreshes SKILL.md documentation references, and confirms the refs/code-templates.md artifact is properly marked inactive.

### T06.01 -- Run make sync-dev and make verify-sync

| Field | Value |
|---|---|
| Roadmap Item IDs | R-045, R-046 |
| Why | The roadmap requires running `make sync-dev` (Constraint 10) to propagate `src/superclaude/` changes to `.claude/` and `make verify-sync` to confirm both sides match. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████▓░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036, D-0037 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0036/evidence.md
- TASKLIST_ROOT/artifacts/D-0037/evidence.md

**Deliverables:**
1. `make sync-dev` executed successfully, propagating all `src/superclaude/` changes to `.claude/`
2. `make verify-sync` passes, confirming `src/` and `.claude/` are in sync

**Steps:**
1. **[PLANNING]** Verify all Phase 1-5 changes are committed or staged in `src/superclaude/`
2. **[PLANNING]** Confirm make targets `sync-dev` and `verify-sync` are available
3. **[EXECUTION]** Run `make sync-dev` to copy changes from `src/superclaude/{skills,agents}` to `.claude/`
4. **[EXECUTION]** Run `make verify-sync` to confirm sync integrity
5. **[VERIFICATION]** Verify `make verify-sync` exits with code 0
6. **[COMPLETION]** Record sync execution results

**Acceptance Criteria:**
- `make sync-dev` completes without errors
- `make verify-sync` exits with code 0, confirming `src/superclaude/` and `.claude/` are in sync
- All modified files (SKILL.md, cli-portify.md, pipeline-spec.md) synced to `.claude/` counterparts
- No unsynced differences remain between `src/` and `.claude/`

**Validation:**
- Manual check: `make verify-sync` exit code 0
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0036/evidence.md)

**Dependencies:** T05.05
**Rollback:** `make sync-dev` (re-run sync)

---

### T06.02 -- Update decisions.yaml with Architectural Decisions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-047 |
| Why | The roadmap requires updating `decisions.yaml` with architectural decisions from this work (mandatory). Key decisions include: inline behavioral pattern embedding, additive-only incorporation, state machine convergence loop, quality threshold 7.0. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0038/spec.md

**Deliverables:**
1. Updated `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml` with architectural decisions: Constraint 1 (inline behavioral patterns), Constraint 2 (additive-only incorporation), Constraint 6 (quality formula), Constraint 7 (CRITICAL handling), Constraint 8 (downstream-ready threshold 7.0), state machine convergence model

**Steps:**
1. **[PLANNING]** Read current `decisions.yaml` to understand existing format and entries
2. **[PLANNING]** Compile list of architectural decisions from Constraints 1-10 and debate resolutions
3. **[EXECUTION]** Add decision entries for: inline behavioral patterns (Constraint 1), additive-only incorporation (Constraint 2), sentinel format (Constraint 5), quality formula (Constraint 6), CRITICAL handling (Constraint 7), downstream threshold (Constraint 8), state machine convergence model, implementation order (Constraint 9), sync requirement (Constraint 10)
4. **[EXECUTION]** Include rationale and source (spec section, debate ID) for each decision
5. **[VERIFICATION]** Verify all 10 constraints are represented and YAML syntax is valid
6. **[COMPLETION]** Document decision entries added

**Acceptance Criteria:**
- `decisions.yaml` contains entries for all 10 constraints from the roadmap with rationale
- Each decision entry includes: ID, title, rationale, source reference (spec section or debate ID)
- YAML syntax validates without errors
- State machine convergence model decision documented with state diagram reference

**Validation:**
- Manual check: `decisions.yaml` parses as valid YAML and contains entries for Constraints 1-10
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0038/spec.md)

**Dependencies:** T06.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml`

---

### T06.03 -- Update SKILL.md Internal Documentation References

| Field | Value |
|---|---|
| Roadmap Item IDs | R-048 |
| Why | The roadmap requires updating SKILL.md internal documentation references to reflect the Phase 3 (spec synthesis) and Phase 4 (panel review) rewrite. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | LIGHT |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0039/notes.md

**Deliverables:**
1. SKILL.md internal documentation references updated: table of contents, phase descriptions, cross-references between phases, and any inline documentation reflecting the new Phase 3 (spec synthesis) and Phase 4 (panel review) structure

**Steps:**
1. **[PLANNING]** Scan SKILL.md for internal documentation sections (table of contents, phase overview)
2. **[PLANNING]** Identify outdated references to old Phase 3/4 descriptions
3. **[EXECUTION]** Update table of contents and phase overview to reflect new Phase 3 and Phase 4 names
4. **[EXECUTION]** Update cross-references between phases
5. **[VERIFICATION]** Scan for any remaining references to "code generation" or "integration" in documentation sections
6. **[COMPLETION]** Document changes made

**Acceptance Criteria:**
- SKILL.md table of contents references Phase 3 as "Spec Synthesis" and Phase 4 as "Panel Review"
- Zero references to "code generation" or "integration phase" in SKILL.md documentation sections
- Cross-references between phases are consistent with new structure
- Internal documentation reflects accurate phase descriptions

**Validation:**
- Manual check: SKILL.md documentation sections reference new phase names and contain no outdated terminology
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0039/notes.md)

**Dependencies:** T06.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### T06.04 -- Verify and Mark refs/code-templates.md as Inactive Reference-Only

| Field | Value |
|---|---|
| Roadmap Item IDs | R-049, R-050 |
| Why | The roadmap requires verifying `refs/code-templates.md` is preserved but unloaded (R-049) and marking it as inactive reference-only per debate R9 mitigation (R-050). |
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
| Deliverable IDs | D-0040, D-0041, D-0042 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0040/evidence.md
- TASKLIST_ROOT/artifacts/D-0041/evidence.md
- TASKLIST_ROOT/artifacts/D-0042/evidence.md

**Deliverables:**
1. Verification that `src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md` exists on disk (preserved)
2. `refs/code-templates.md` marked with inactive reference-only header/notice per debate R9 mitigation
3. Verification that no workflow phase in SKILL.md loads or reads `refs/code-templates.md`

**Steps:**
1. **[PLANNING]** Locate `refs/code-templates.md` in the skill directory
2. **[PLANNING]** Determine appropriate inactive marker format
3. **[EXECUTION]** Verify file exists at `src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md`
4. **[EXECUTION]** Add inactive reference-only notice to file header (e.g., `<!-- INACTIVE: Reference-only. Not loaded by any workflow phase. -->`)
5. **[EXECUTION]** Grep SKILL.md phases for any load/read references to `code-templates.md` → expect zero
6. **[VERIFICATION]** File exists, inactive marker present, zero load references in SKILL.md
7. **[COMPLETION]** Document preservation and inactive status

**Acceptance Criteria:**
- `src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md` exists on disk
- File contains inactive reference-only marker/notice at the top
- `grep -n 'code-templates' src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` returns zero results in phase load/execution sections
- R9 mitigation (debate) satisfied: orphaned reference cannot become misleading

**Validation:**
- Manual check: File exists with inactive marker; zero SKILL.md load references
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0040/evidence.md)

**Dependencies:** T06.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md`

---

### Checkpoint: End of Phase 6

| Field | Value |
|---|---|
| Roadmap Item IDs | R-051 |

**Purpose:** Verify Gate D criteria are met: all changes synced and verified, decisions.yaml updated, overall quality threshold logic validated, no unaddressed CRITICAL findings, reviewed spec consumed by sc:roadmap (downstream interoperability confirmed).
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P06-END.md
**Verification:**
- `make verify-sync` passes with exit code 0
- `decisions.yaml` contains entries for all 10 constraints with valid YAML syntax
- Overall quality threshold logic (`overall >= 7.0` → `downstream_ready: true`) validated end-to-end
- No unaddressed CRITICAL findings remain across all phases
- `refs/code-templates.md` preserved on disk with inactive reference-only marker
**Exit Criteria:**
- All 4 tasks (T06.01-T06.04) completed with deliverables D-0036 through D-0042 produced
- All changes synced between `src/superclaude/` and `.claude/`
- Overall quality threshold logic validated end-to-end
- No unaddressed CRITICAL findings remain across all phases
- Reviewed spec consumed by `sc:roadmap` confirmed (downstream interoperability from Phase 5 T05.05)
