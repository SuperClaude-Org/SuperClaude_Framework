# Phase 1 — Foundation & Architecture Setup

Establish the file layout, directory structure, and empty scaffolding for the `/sc:tasklist` command/skill pair. This phase creates all directories and placeholder files that subsequent phases will populate with content. No functional code is written in this phase.

### T01.01 — Create `sc-tasklist-protocol/` directory tree with `rules/` and `templates/` subdirs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The skill requires a directory structure matching §4.1 file layout before any content files can be created |
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
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/evidence.md`

**Deliverables:**
- Directory tree `src/superclaude/skills/sc-tasklist-protocol/` with `rules/` and `templates/` subdirectories

**Steps:**
1. **[PLANNING]** Identify target path `src/superclaude/skills/sc-tasklist-protocol/` per §4.1
2. **[PLANNING]** Verify `src/superclaude/skills/` parent directory exists
3. **[EXECUTION]** Run `mkdir -p src/superclaude/skills/sc-tasklist-protocol/rules`
4. **[EXECUTION]** Run `mkdir -p src/superclaude/skills/sc-tasklist-protocol/templates`
5. **[VERIFICATION]** Run `ls -R src/superclaude/skills/sc-tasklist-protocol/` to confirm all 3 directories exist
6. **[COMPLETION]** Record directory creation evidence

**Acceptance Criteria:**
- `src/superclaude/skills/sc-tasklist-protocol/`, `rules/`, and `templates/` directories all exist on disk
- Directory structure matches §4.1 file layout specification exactly
- No extraneous files or directories created
- Evidence of directory creation recorded

**Validation:**
- Manual check: `ls -R src/superclaude/skills/sc-tasklist-protocol/` shows `rules/` and `templates/` subdirs
- Evidence: linkable artifact produced (directory listing output)

**Dependencies:** None
**Rollback:** `rm -rf src/superclaude/skills/sc-tasklist-protocol/`
**Notes:** None

---

### T01.02 — Create empty `__init__.py` in `sc-tasklist-protocol/`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | Python packaging requires `__init__.py` for the skill directory; must be zero-byte per FR-008, NFR-012 |
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
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Deliverables:**
- Empty `src/superclaude/skills/sc-tasklist-protocol/__init__.py` file (zero bytes)

**Steps:**
1. **[PLANNING]** Confirm directory `src/superclaude/skills/sc-tasklist-protocol/` exists (depends on T01.01)
2. **[PLANNING]** Verify `pyproject.toml` package discovery config excludes skill dirs from Python import scanning (RISK-009 mitigation)
3. **[EXECUTION]** Run `touch src/superclaude/skills/sc-tasklist-protocol/__init__.py`
4. **[VERIFICATION]** Run `wc -c src/superclaude/skills/sc-tasklist-protocol/__init__.py` to confirm 0 bytes
5. **[COMPLETION]** Record file creation evidence

**Acceptance Criteria:**
- File `src/superclaude/skills/sc-tasklist-protocol/__init__.py` exists and is zero bytes
- `pyproject.toml` package discovery does not inadvertently import the skill directory
- File satisfies Python packaging requirements (FR-008, NFR-012)
- Creation evidence recorded

**Validation:**
- Manual check: `wc -c src/superclaude/skills/sc-tasklist-protocol/__init__.py` outputs `0`
- Evidence: linkable artifact produced (file size verification output)

**Dependencies:** T01.01
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/__init__.py`
**Notes:** RISK-009 mitigation: verify `pyproject.toml` excludes `skills/` from package scanning

---

### T01.03 — Create placeholder `tasklist.md` command file with valid YAML frontmatter

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | The command file placeholder establishes the `name: tasklist` identity for later population in Phase 2 |
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
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0003/evidence.md`

**Deliverables:**
- Placeholder `src/superclaude/commands/tasklist.md` with valid YAML frontmatter containing `name: tasklist`

**Steps:**
1. **[PLANNING]** Confirm `src/superclaude/commands/` directory exists
2. **[PLANNING]** Review §5.1 for required frontmatter fields
3. **[EXECUTION]** Write `src/superclaude/commands/tasklist.md` with YAML frontmatter block containing `name: tasklist`
4. **[EXECUTION]** Include only frontmatter (no body content) — body added in Phase 2
5. **[VERIFICATION]** Parse frontmatter to confirm `name: tasklist` is present and valid YAML
6. **[COMPLETION]** Record placeholder creation evidence

**Acceptance Criteria:**
- File `src/superclaude/commands/tasklist.md` exists with valid YAML frontmatter
- Frontmatter contains `name: tasklist`
- YAML frontmatter parses without errors
- No body content beyond frontmatter (placeholder only)

**Validation:**
- Manual check: `head -5 src/superclaude/commands/tasklist.md` shows `---` delimiters and `name: tasklist`
- Evidence: linkable artifact produced (frontmatter parse output)

**Dependencies:** None
**Rollback:** `rm src/superclaude/commands/tasklist.md`
**Notes:** None

---

### T01.04 — Create placeholder `SKILL.md` with valid frontmatter

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | The SKILL.md placeholder establishes the `name: sc:tasklist-protocol` identity for later population in Phase 2 |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Deliverables:**
- Placeholder `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` with valid frontmatter containing `name: sc:tasklist-protocol`

**Steps:**
1. **[PLANNING]** Confirm directory `src/superclaude/skills/sc-tasklist-protocol/` exists (depends on T01.01)
2. **[PLANNING]** Review §6.1 for required SKILL.md frontmatter fields
3. **[EXECUTION]** Write `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` with YAML frontmatter containing `name: sc:tasklist-protocol`
4. **[EXECUTION]** Include only frontmatter (no body content) — body added in Phase 2
5. **[VERIFICATION]** Parse frontmatter to confirm `name: sc:tasklist-protocol` is present and ends in `-protocol`
6. **[COMPLETION]** Record placeholder creation evidence

**Acceptance Criteria:**
- File `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` exists with valid YAML frontmatter
- Frontmatter contains `name: sc:tasklist-protocol` (ending in `-protocol` per FR-057)
- YAML frontmatter parses without errors
- No body content beyond frontmatter (placeholder only)

**Validation:**
- Manual check: `head -5 src/superclaude/skills/sc-tasklist-protocol/SKILL.md` shows `---` delimiters and `name: sc:tasklist-protocol`
- Evidence: linkable artifact produced (frontmatter parse output)

**Dependencies:** T01.01
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/SKILL.md`
**Notes:** None

---

### Checkpoint: End of Phase 1

**Purpose:** Verify all scaffolding directories and placeholder files exist before proceeding to content implementation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`

**Verification:**
- All 3 directories (`sc-tasklist-protocol/`, `rules/`, `templates/`) exist under `src/superclaude/skills/`
- `__init__.py`, `SKILL.md` placeholders exist in `sc-tasklist-protocol/`; `tasklist.md` placeholder exists in `src/superclaude/commands/`
- Both placeholder files have valid, parseable YAML frontmatter with correct `name:` fields

**Exit Criteria:**
- T01.01 through T01.04 all completed successfully
- No extraneous files created outside the specified directory structure
- `pyproject.toml` package discovery verified to exclude skill directories (RISK-009)
