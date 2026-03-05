# Phase 3 — Integration & Tooling

Validate that the command and skill pair integrate correctly (V1), then ensure the pair works with `superclaude install`, `make sync-dev`, `make verify-sync`, and `make lint-architecture` tooling (M4). This phase gates all downstream validation work.

### T03.01 — Verify command `## Activation` references `sc:tasklist-protocol` and skill directory exists

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Lint check #1 validates the command→skill directional pairing: Activation section must reference an existing skill directory |
| Effort | XS |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Deliverables:**
- Lint check #1 passes: `## Activation` section in `tasklist.md` references `sc:tasklist-protocol` and `sc-tasklist-protocol/` directory exists

**Steps:**
1. **[PLANNING]** Read `tasklist.md` `## Activation` section for skill reference
2. **[PLANNING]** Identify expected skill directory path: `src/superclaude/skills/sc-tasklist-protocol/`
3. **[EXECUTION]** Verify `## Activation` contains `Skill sc:tasklist-protocol` reference
4. **[EXECUTION]** Verify `src/superclaude/skills/sc-tasklist-protocol/` directory exists
5. **[VERIFICATION]** Confirm lint check #1 criteria satisfied (FR-071)
6. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- `## Activation` section in `tasklist.md` contains `Skill sc:tasklist-protocol` text
- Directory `src/superclaude/skills/sc-tasklist-protocol/` exists on disk
- Command→skill directional pairing validated
- Evidence of verification recorded

**Validation:**
- Manual check: `grep "sc:tasklist-protocol" src/superclaude/commands/tasklist.md` returns match AND `ls src/superclaude/skills/sc-tasklist-protocol/` succeeds
- Evidence: linkable artifact produced (lint check #1 output)

**Dependencies:** T02.05, T01.01
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T03.02 — Verify bidirectional pairing: skill directory exists implies command file exists

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Lint check #2 validates the reverse pairing: if a skill directory exists, the corresponding command file must also exist |
| Effort | XS |
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
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0022/evidence.md`

**Deliverables:**
- Lint check #2 passes: `sc-tasklist-protocol/` directory exists and corresponding `tasklist.md` command file exists

**Steps:**
1. **[PLANNING]** Identify bidirectional pairing rule: skill dir → command file
2. **[PLANNING]** Map `sc-tasklist-protocol` → `tasklist` (strip `sc-` prefix and `-protocol` suffix)
3. **[EXECUTION]** Verify `src/superclaude/skills/sc-tasklist-protocol/` directory exists
4. **[EXECUTION]** Verify `src/superclaude/commands/tasklist.md` command file exists
5. **[VERIFICATION]** Confirm lint check #2 criteria satisfied (FR-072)
6. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- `src/superclaude/skills/sc-tasklist-protocol/` directory exists on disk
- `src/superclaude/commands/tasklist.md` command file exists on disk
- Bidirectional pairing validated: skill ↔ command
- Evidence of verification recorded

**Validation:**
- Manual check: Both `ls src/superclaude/skills/sc-tasklist-protocol/` and `ls src/superclaude/commands/tasklist.md` succeed
- Evidence: linkable artifact produced (lint check #2 output)

**Dependencies:** T01.01, T01.03
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T03.03 — Verify SKILL.md frontmatter passes lint checks #8 and #9

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Lint checks #8 and #9 validate SKILL.md has required frontmatter fields and `name:` ends in `-protocol` |
| Effort | XS |
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
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0023/evidence.md`

**Deliverables:**
- Lint checks #8 and #9 pass: SKILL.md has `name:`, `description:`, `allowed-tools:` frontmatter; `name:` ends in `-protocol`

**Steps:**
1. **[PLANNING]** Read SKILL.md frontmatter for lint check fields
2. **[PLANNING]** Identify check #8 fields: `name:`, `description:`, `allowed-tools:`
3. **[EXECUTION]** Verify `name:`, `description:`, `allowed-tools:` all present in SKILL.md frontmatter
4. **[EXECUTION]** Verify `name:` value ends in `-protocol` (check #9)
5. **[VERIFICATION]** Confirm lint checks #8 and #9 pass (FR-076, FR-057)
6. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- SKILL.md frontmatter contains `name:`, `description:`, `allowed-tools:` fields (lint check #8)
- `name:` value is `sc:tasklist-protocol` — ends in `-protocol` (lint check #9, FR-057)
- All frontmatter fields parse as valid YAML
- Evidence of verification recorded

**Validation:**
- Manual check: Parse SKILL.md frontmatter and verify `name:` ends in `-protocol`, `description:` and `allowed-tools:` present
- Evidence: linkable artifact produced (lint check #8 and #9 output)

**Dependencies:** T02.09
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T03.04 — Run `make sync-dev` to copy command and skill to `.claude/` directories

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Dev copies in `.claude/` are required for Claude Code to access the command and skill during development |
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
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0024/evidence.md`

**Deliverables:**
- `tasklist.md` copied to `.claude/commands/sc/` and `sc-tasklist-protocol/` copied to `.claude/skills/` after `make sync-dev`

**Steps:**
1. **[PLANNING]** Verify source files exist in `src/superclaude/commands/` and `src/superclaude/skills/`
2. **[PLANNING]** Review `make sync-dev` target to understand copy behavior
3. **[EXECUTION]** Run `make sync-dev`
4. **[EXECUTION]** Verify `tasklist.md` exists in `.claude/commands/sc/`
5. **[EXECUTION]** Verify `sc-tasklist-protocol/` directory exists in `.claude/skills/`
6. **[VERIFICATION]** Confirm both targets populated (FR-069)
7. **[COMPLETION]** Record sync evidence

**Acceptance Criteria:**
- `.claude/commands/sc/tasklist.md` exists after `make sync-dev`
- `.claude/skills/sc-tasklist-protocol/` directory exists with SKILL.md and subdirs after `make sync-dev`
- `make sync-dev` exits with code 0
- Evidence of successful sync recorded

**Validation:**
- Manual check: `ls .claude/commands/sc/tasklist.md` and `ls .claude/skills/sc-tasklist-protocol/SKILL.md` both succeed
- Evidence: linkable artifact produced (sync output)

**Dependencies:** T03.01, T03.02, T03.03
**Rollback:** `rm .claude/commands/sc/tasklist.md && rm -rf .claude/skills/sc-tasklist-protocol/`
**Notes:** None

---

### Checkpoint: Phase 3 / Tasks T03.01–T03.05

**Purpose:** Verify integration checks pass and dev sync is successful before proceeding to lint and install testing.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-T01-T05.md`

**Verification:**
- Lint checks #1, #2, #8, #9 all pass
- `make sync-dev` completed successfully with files in `.claude/`
- `make verify-sync` confirms source and `.claude/` copies are identical

**Exit Criteria:**
- T03.01 through T03.05 completed; integration and sync verified
- No sync discrepancies between source and `.claude/` copies
- Ready for lint-architecture and install testing

---

### T03.05 — Run `make verify-sync` to confirm source and `.claude/` copies are identical

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | Verify-sync ensures no drift between source-of-truth `src/superclaude/` and convenience copies in `.claude/` |
| Effort | XS |
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
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Deliverables:**
- No diff between `src/superclaude/` and `.claude/` copies of command and skill files

**Steps:**
1. **[PLANNING]** Identify files to verify: `commands/tasklist.md`, `skills/sc-tasklist-protocol/` tree
2. **[PLANNING]** Review `make verify-sync` behavior and expected output
3. **[EXECUTION]** Run `make verify-sync`
4. **[VERIFICATION]** Confirm exit code 0 and no diff reported (FR-070)
5. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- `make verify-sync` exits with code 0
- No differences reported between `src/superclaude/` and `.claude/` copies
- Command file and skill directory tree are identical in both locations
- Evidence of successful verification recorded

**Validation:**
- Manual check: `make verify-sync` exits 0 with no diff output
- Evidence: linkable artifact produced (verify-sync output)

**Dependencies:** T03.04
**Rollback:** N/A (verification only — no changes made)
**Notes:** None

---

### T03.06 — Run `make lint-architecture` and verify zero errors for the new pair

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | lint-architecture validates the full command/skill pair against all 6 structural lint checks |
| Effort | S |
| Risk | Medium |
| Risk Drivers | Cross-cutting scope (6 lint checks across command and skill) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Deliverables:**
- All 6 lint-architecture checks pass with zero errors for the `tasklist.md` / `sc-tasklist-protocol` pair

**Steps:**
1. **[PLANNING]** Review the 6 lint checks: (1) Activation→skill dir, (2) skill dir→command, (3-4) line count limits, (6) Activation section, (8) SKILL.md fields, (9) name ends in -protocol
2. **[PLANNING]** Anticipate RISK-003: potential edge cases in lint rules for the new pair
3. **[EXECUTION]** Run `make lint-architecture`
4. **[EXECUTION]** If errors found, investigate rule source before modifying anything (NFR-007 prohibits rule changes)
5. **[VERIFICATION]** Confirm all 6 checks pass with zero errors (FR-003, FR-071–FR-076, NFR-007)
6. **[VERIFICATION]** Record specific check results for each of the 6 checks
7. **[COMPLETION]** Record lint evidence

**Acceptance Criteria:**
- `make lint-architecture` exits with code 0
- All 6 lint checks pass for the `tasklist.md` / `sc-tasklist-protocol` pair
- No lint rule modifications made (NFR-007)
- Per-check results recorded as evidence

**Validation:**
- Manual check: `make lint-architecture` exits 0 with all checks passing
- Evidence: linkable artifact produced (lint output with per-check results)

**Dependencies:** T03.04
**Rollback:** N/A (verification only; if lint fails, fix source files, don't modify lint rules)
**Notes:** RISK-003 mitigation: if lint fails, investigate rule source before any modifications

---

### T03.07 — Verify `superclaude install` installs `tasklist.md` to `~/.claude/commands/sc/`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | The command file must be installable via `superclaude install` for end-user discoverability |
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
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0027/evidence.md`

**Deliverables:**
- `tasklist.md` exists at `~/.claude/commands/sc/tasklist.md` after `superclaude install`

**Steps:**
1. **[PLANNING]** Review `superclaude install` command installation behavior
2. **[PLANNING]** Identify expected install target: `~/.claude/commands/sc/tasklist.md`
3. **[EXECUTION]** Run `superclaude install` (or relevant install command)
4. **[EXECUTION]** Verify `~/.claude/commands/sc/tasklist.md` exists
5. **[VERIFICATION]** Confirm file content matches source `src/superclaude/commands/tasklist.md` (FR-067)
6. **[COMPLETION]** Record install evidence

**Acceptance Criteria:**
- `~/.claude/commands/sc/tasklist.md` exists after `superclaude install`
- File content matches source file in `src/superclaude/commands/`
- Install command exits with code 0
- Evidence of successful install recorded

**Validation:**
- Manual check: `ls ~/.claude/commands/sc/tasklist.md` succeeds after `superclaude install`
- Evidence: linkable artifact produced (install output and file existence verification)

**Dependencies:** T03.06
**Rollback:** `rm ~/.claude/commands/sc/tasklist.md`
**Notes:** None

---

### T03.08 — Verify `superclaude install` does NOT install `sc-tasklist-protocol/` to `~/.claude/skills/`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | Skills with paired commands must NOT be installed to `~/.claude/skills/` — they are accessed only via `Skill sc:tasklist-protocol` from within the command |
| Effort | S |
| Risk | Medium |
| Risk Drivers | Cross-cutting scope (installer logic interaction with `_has_corresponding_command`) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Deliverables:**
- `sc-tasklist-protocol/` directory absent from `~/.claude/skills/` after `superclaude install`

**Steps:**
1. **[PLANNING]** Review `_has_corresponding_command` logic in `src/superclaude/cli/install_skills.py`
2. **[PLANNING]** Identify pairing: `sc-tasklist-protocol` → `tasklist.md` (strip `sc-` prefix and `-protocol` suffix)
3. **[EXECUTION]** Run `superclaude install` (if not already run in T03.07)
4. **[EXECUTION]** Verify `~/.claude/skills/sc-tasklist-protocol/` does NOT exist
5. **[VERIFICATION]** Confirm skill install isolation (FR-068, NFR-006, NFR-010)
6. **[VERIFICATION]** Verify `_has_corresponding_command` correctly handles `sc-tasklist-protocol` pairing (RISK-005)
7. **[COMPLETION]** Record install isolation evidence

**Acceptance Criteria:**
- `~/.claude/skills/sc-tasklist-protocol/` does NOT exist after `superclaude install`
- `_has_corresponding_command` correctly maps `sc-tasklist-protocol` → `tasklist.md`
- Install isolation preserved: skill accessible only via command invocation
- Evidence of absence recorded

**Validation:**
- Manual check: `ls ~/.claude/skills/sc-tasklist-protocol/` fails (directory does not exist)
- Evidence: linkable artifact produced (install isolation verification)

**Dependencies:** T03.07
**Rollback:** `rm -rf ~/.claude/skills/sc-tasklist-protocol/` if incorrectly installed
**Notes:** RISK-005 mitigation: verify `_has_corresponding_command` logic handles the pairing correctly

---

### T03.09 — Verify source files unmodified after all Phase 2-3 work

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | The v3.0 generator prompt and TasklistGenPrompt.md are source-of-truth references and must remain unchanged |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | LIGHT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0029/evidence.md`

**Deliverables:**
- `git diff` confirms `Tasklist-Generator-Prompt-v2.1-unified.md` and `TasklistGenPrompt.md` are unchanged

**Steps:**
1. **[PLANNING]** Identify source files that must remain unchanged (FR-079, FR-080)
2. **[EXECUTION]** Run `git diff` on `Tasklist-Generator-Prompt-v2.1-unified.md`
3. **[EXECUTION]** Run `git diff` on `TasklistGenPrompt.md`
4. **[VERIFICATION]** Confirm both files show zero diff (no modifications)
5. **[COMPLETION]** Record verification evidence

**Acceptance Criteria:**
- `git diff` shows no changes to `Tasklist-Generator-Prompt-v2.1-unified.md`
- `git diff` shows no changes to `TasklistGenPrompt.md`
- Source-of-truth files preserved intact throughout implementation
- Evidence of zero-diff recorded

**Validation:**
- Manual check: `git diff -- "*Tasklist-Generator-Prompt*"` shows no output
- Evidence: linkable artifact produced (git diff output confirming no changes)

**Dependencies:** T02.10
**Rollback:** `git checkout -- <file>` if accidentally modified
**Notes:** None

---

### Checkpoint: End of Phase 3

**Purpose:** Verify all integration checks, tooling, and installation pass before proceeding to output validation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`

**Verification:**
- All 3 integration checks pass (T03.01–T03.03): Activation→skill, skill→command, frontmatter lint
- Dev tooling works: `make sync-dev` (T03.04), `make verify-sync` (T03.05), `make lint-architecture` (T03.06)
- Install works correctly: command installed (T03.07), skill NOT installed (T03.08), source files unchanged (T03.09)

**Exit Criteria:**
- T03.01 through T03.09 all completed with zero errors
- `make lint-architecture` passes with zero errors (NFR-007: no lint rule modifications)
- Source-of-truth files confirmed unchanged
