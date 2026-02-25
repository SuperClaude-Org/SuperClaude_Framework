# TASKLIST — v1.06-CleanupAudit `/sc:cleanup-audit` Skill Implementation

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.roadmaps/v1.06/`
- **Tasklist Path**: `.roadmaps/v1.06/tasklist.md`
- **Execution Log Path**: `.roadmaps/v1.06/execution-log.md`
- **Checkpoint Reports Path**: `.roadmaps/v1.06/checkpoints/`
- **Evidence Root**: `.roadmaps/v1.06/evidence/`
- **Artifacts Root**: `.roadmaps/v1.06/artifacts/`
- **Feedback Log Path**: `.roadmaps/v1.06/feedback-log.md`

---

## Source Snapshot

- **Project**: `/sc:cleanup-audit` — Multi-pass read-only repository audit skill for SuperClaude framework
- **Architecture**: Hybrid skill (SKILL.md orchestrator) + 5 custom subagent definitions + 5 rules files + 4 templates + 1 script
- **Milestones**: 6 (Foundation → Rules → Templates → Agents → Integration → Validation)
- **Total Roadmap Tasks**: 36 across 6 milestones (14 P0-Critical, 18 P1-High, 3 P2-Medium, 1 P3-Low)
- **Execution Order**: M1 → (M2 ∥ M3) → M4 → M5 → M6
- **Key Constraint**: Subagents cannot spawn sub-subagents; MCP unavailable in background subagents

---

## Deterministic Rules Applied

- **Phase buckets**: 6 phases derived from explicit milestones M1–M6, renumbered sequentially as Phase 1–6 with no gaps
- **Task ID scheme**: `T<PP>.<TT>` where PP = 2-digit phase, TT = 2-digit task within phase (e.g., T01.03)
- **Checkpoint cadence**: After every 5 tasks within a phase + end-of-phase checkpoint (9 total)
- **Clarification task rule**: Insert before blocked task when info missing or tier confidence < 0.70
- **Deliverable registry**: D-0001 through D-0037 assigned in task order, each with intended artifact paths
- **Effort mapping**: EFFORT_SCORE computed via text length (≥120 chars: +1), split status (+1), keyword match (+1), dependency words (+1) → XS/S/M/L/XL
- **Risk mapping**: RISK_SCORE computed via security/audit keywords (+2), migration/data (+2), auth (+1), performance (+1), cross-cutting (+1) → Low/Medium/High
- **Tier classification**: STRICT/STANDARD/LIGHT/EXEMPT via compound phrase check → keyword matching → context boosters → priority resolution (STRICT > EXEMPT > LIGHT > STANDARD)
- **Verification routing**: STRICT → sub-agent (quality-engineer, 3-5K tokens, 60s) | STANDARD → direct test (300-500, 30s) | LIGHT → sanity check (~100, 10s) | EXEMPT → skip
- **MCP requirements**: STRICT requires Sequential + Serena; STANDARD prefers Sequential + Context7; LIGHT/EXEMPT none required
- **Traceability matrix**: Every R-### mapped to T<PP>.<TT> → D-#### → artifact paths → tier → confidence
- **No policy forks**: All choices deterministic per Section 4.9 tie-breakers

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | — | Release Roadmap: v1.06-CleanupAudit — /sc:cleanup-audit Skill |
| R-002 | — | Milestones Overview table with 6 milestones, dependencies, risk levels |
| R-003 | — | Dependency Graph showing M1 → (M2 ∥ M3) → M4 → M5 → M6 |
| R-004 | — | Risk Register with 8 identified risks (R1–R8) |
| R-005 | — | Success Criteria with 13 verification items |
| R-006 | Phase 1 | T1.1: Create Skill Directory Structure — .claude/skills/sc-cleanup-audit/{rules,templates,scripts} |
| R-007 | Phase 1 | T1.2: Write SKILL.md Frontmatter & Header — YAML frontmatter with all required fields |
| R-008 | Phase 1 | T1.3: Write Behavioral Flow (5-Step) — Discover, Configure, Orchestrate, Validate, Report |
| R-009 | Phase 1 | T1.4: Write MCP Integration Section — Sequential, Serena, Context7 bullets |
| R-010 | Phase 1 | T1.5: Write Tool Coordination Section — Read/Grep/Glob, Bash, Write, TodoWrite, Task |
| R-011 | Phase 1 | T1.6: Write Key Patterns Section — 5 patterns with arrow notation |
| R-012 | Phase 1 | T1.7: Write Examples Section — 4 examples progressing simple to complex |
| R-013 | Phase 1 | T1.8: Write Boundaries and Critical Boundaries — Will/Will Not + STOP directive |
| R-014 | Phase 1 | T1.9: Write Shell Preprocessing Context Block — !cmd syntax for repo metadata |
| R-015 | Phase 1 | T1.10: Write repo-inventory.sh Script — git ls-files enumeration, batch creation |
| R-016 | Phase 1 | T1.11: SKILL.md Line Count Validation — ensure under 500 lines |
| R-017 | Phase 2 | T2.1: Write Pass 1 Surface Scan Rules — 3-tier classification taxonomy |
| R-018 | Phase 2 | T2.2: Write Pass 2 Structural Audit Rules — 8-field per-file profile |
| R-019 | Phase 2 | T2.3: Write Pass 3 Cross-Cutting Rules — duplication matrix, tiered depth |
| R-020 | Phase 2 | T2.4: Write Universal Verification Protocol — evidence requirements per recommendation type |
| R-021 | Phase 2 | T2.5: Write Dynamic-Use Checklist — 5 dynamic loading patterns |
| R-022 | Phase 3 | T3.1: Write Batch Report Template — per-agent output format with required sections |
| R-023 | Phase 3 | T3.2: Write Pass Summary Template — consolidated pass summary with dedup |
| R-024 | Phase 3 | T3.3: Write Final Report Template — executive summary, action items |
| R-025 | Phase 3 | T3.4: Write Finding Profile Template — per-file finding profile mandatory fields |
| R-026 | Phase 4 | T4.1: Write audit-scanner.md — Haiku, read-only, surface scan methodology |
| R-027 | Phase 4 | T4.2: Write audit-analyzer.md — Sonnet, read-only, deep structural profiling |
| R-028 | Phase 4 | T4.3: Write audit-comparator.md — Sonnet, read-only, cross-cutting comparison |
| R-029 | Phase 4 | T4.4: Write audit-consolidator.md — Sonnet, Write-enabled, report merging |
| R-030 | Phase 4 | T4.5: Write audit-validator.md — Sonnet, read-only, finding verification |
| R-031 | Phase 5 | T5.1: Add COMMANDS.md Entry — command listed with auto-persona, MCP, tools |
| R-032 | Phase 5 | T5.2: Add ORCHESTRATOR.md Routing Entry — pattern matching and confidence score |
| R-033 | Phase 5 | T5.3: Update PERSONAS.md Trigger Keywords — new trigger keywords for analyzer |
| R-034 | Phase 6 | T6.1: Validate Skill Loading — skill discoverable, frontmatter parsed, tool restrictions |
| R-035 | Phase 6 | T6.2: Test Pass 1 on Small Directory — subagent spawning, batch report validation |
| R-036 | Phase 6 | T6.3: Test Pass 2 on Small Directory — 8-field profiles, file-type rules |
| R-037 | Phase 6 | T6.4: Test Pass 3 Cross-Cutting — duplication matrix, overlap percentages |
| R-038 | Phase 6 | T6.5: Test Quality Gate Enforcement — validator spawning, spot-check sampling |
| R-039 | Phase 6 | T6.6: Test Full 3-Pass Audit — all passes, quality gates, final report |
| R-040 | Phase 6 | T6.7: Test Resume-from-Checkpoint — progress.json detection, batch skip, resume |
| R-041 | Phase 6 | T6.8: Write Validation Report — document all test results, issues, score |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-006 | Skill directory structure | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0001/evidence.md` | XS | Low |
| D-0002 | T01.02 | R-007 | SKILL.md frontmatter & header | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0002/spec.md` | S | Medium |
| D-0003 | T01.03 | R-008 | Behavioral flow (5-step) section | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0003/spec.md` | S | Low |
| D-0004 | T01.04 | R-009 | MCP Integration section | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0004/spec.md` | S | Low |
| D-0005 | T01.05 | R-010 | Tool Coordination section | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0005/spec.md` | S | Low |
| D-0006 | T01.06 | R-011 | Key Patterns section | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0006/spec.md` | XS | Low |
| D-0007 | T01.07 | R-012 | Examples section (4 examples) | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0007/spec.md` | S | Low |
| D-0008 | T01.08 | R-013 | Boundaries + Critical Boundaries | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0008/spec.md` | S | Low |
| D-0009 | T01.09 | R-014 | Shell preprocessing block | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0009/spec.md` | S | Low |
| D-0010 | T01.10 | R-015 | repo-inventory.sh script | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0010/spec.md`, `.roadmaps/v1.06/artifacts/D-0010/evidence.md` | S | Low |
| D-0011 | T01.11 | R-016 | Line count validation result | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0011/evidence.md` | XS | Low |
| D-0012 | T02.01 | R-017 | pass1-surface-scan.md rules | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0012/spec.md` | S | Low |
| D-0013 | T02.02 | R-018 | pass2-structural-audit.md rules | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0013/spec.md` | M | Low |
| D-0014 | T02.03 | R-019 | pass3-cross-cutting.md rules | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0014/spec.md` | S | Low |
| D-0015 | T02.04 | R-020 | verification-protocol.md | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0015/spec.md` | S | Low |
| D-0016 | T02.05 | R-021 | dynamic-use-checklist.md | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0016/spec.md` | S | Low |
| D-0017 | T03.01 | R-022 | batch-report.md template | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0017/spec.md` | S | Low |
| D-0018 | T03.02 | R-023 | pass-summary.md template | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0018/spec.md` | S | Low |
| D-0019 | T03.03 | R-024 | final-report.md template | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0019/spec.md` | S | Low |
| D-0020 | T03.04 | R-025 | finding-profile.md template | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0020/spec.md` | S | Low |
| D-0021 | T04.01 | R-026 | audit-scanner.md agent definition | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0021/spec.md` | M | Medium |
| D-0022 | T04.02 | R-027 | audit-analyzer.md agent definition | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0022/spec.md` | M | Medium |
| D-0023 | T04.03 | R-028 | audit-comparator.md agent definition | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0023/spec.md` | M | Medium |
| D-0024 | T04.04 | R-029 | audit-consolidator.md agent definition | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0024/spec.md` | M | Medium |
| D-0025 | T04.05 | R-030 | audit-validator.md agent definition | STRICT | Sub-agent (quality-engineer) | `.roadmaps/v1.06/artifacts/D-0025/spec.md` | M | Medium |
| D-0026 | T05.01 | R-031 | COMMANDS.md entry | EXEMPT | Skip verification | `.roadmaps/v1.06/artifacts/D-0026/notes.md` | XS | Low |
| D-0027 | T05.02 | R-032 | ORCHESTRATOR.md routing entry | EXEMPT | Skip verification | `.roadmaps/v1.06/artifacts/D-0027/notes.md` | XS | Low |
| D-0028 | T05.03 | R-033 | PERSONAS.md trigger updates | EXEMPT | Skip verification | `.roadmaps/v1.06/artifacts/D-0028/notes.md` | XS | Low |
| D-0029 | T06.01 | R-034 | Skill loading test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0029/evidence.md` | S | Low |
| D-0030 | T06.02 | R-035 | Pass 1 small directory test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0030/evidence.md` | S | Medium |
| D-0031 | T06.03 | R-036 | Pass 2 small directory test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0031/evidence.md` | S | Medium |
| D-0032 | T06.04 | R-037 | Pass 3 cross-cutting test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0032/evidence.md` | S | Medium |
| D-0033 | T06.05 | R-038 | Quality gate enforcement test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0033/evidence.md` | S | Medium |
| D-0034 | T06.06 | R-039 | Full 3-pass audit test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0034/evidence.md` | S | Medium |
| D-0035 | T06.07 | R-040 | Resume-from-checkpoint test results | STANDARD | Direct test | `.roadmaps/v1.06/artifacts/D-0035/evidence.md` | S | Low |
| D-0036 | T06.08 | R-041 | Validation report document | EXEMPT | Skip verification | `.roadmaps/v1.06/artifacts/D-0036/spec.md` | M | Low |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| 1 | Foundation & Orchestration | T01.01–T01.11 | SKILL.md + repo-inventory.sh | STRICT: 1, STANDARD: 10, LIGHT: 0, EXEMPT: 0 |
| 2 | Rules Engine | T02.01–T02.05 | 5 rules files defining audit methodology | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 3 | Output Templates | T03.01–T03.04 | 4 template files for structured output | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 4 | Subagent Definitions | T04.01–T04.05 | 5 custom subagent .md files | STRICT: 5, STANDARD: 0, LIGHT: 0, EXEMPT: 0 |
| 5 | Framework Integration | T05.01–T05.03 | COMMANDS.md, ORCHESTRATOR.md, PERSONAS.md entries | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 3 |
| 6 | Validation & Testing | T06.01–T06.08 | Functional tests + validation report | STRICT: 0, STANDARD: 7, LIGHT: 0, EXEMPT: 1 |

**Total**: 36 tasks — STRICT: 6, STANDARD: 26, LIGHT: 0, EXEMPT: 4

---

## Phase 1: Foundation & Orchestration

Create the core SKILL.md orchestration file and the repo-inventory shell script. These are the backbone that all other files reference and depend on. No external dependencies — this is the first milestone.

### T01.01 — Create Skill Directory Structure

**Roadmap Item ID(s):** R-006
**Why:** All subsequent files require this directory tree to exist. Foundation for the entire skill.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0001
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0001/evidence.md`

**Deliverables:**
- Skill directory tree: `.claude/skills/sc-cleanup-audit/{rules,templates,scripts}` and `.claude/agents/`

**Steps:**
1. **[PLANNING]** Identify required directory structure from spec §1 Architecture Overview
2. **[PLANNING]** Verify `.claude/` directory exists; check if `.claude/agents/` already exists
3. **[EXECUTION]** Create directory tree: `.claude/skills/sc-cleanup-audit/{rules,templates,scripts}`
4. **[EXECUTION]** Create `.claude/agents/` directory if it does not exist
5. **[VERIFICATION]** Verify all directories exist and are writable via `ls -la`
6. **[COMPLETION]** Record directory structure in evidence artifact

**Acceptance Criteria:**
- All 4 subdirectories exist and are writable
- Directory structure matches spec §1 Architecture Overview exactly
- No pre-existing files were overwritten or modified
- Directory creation commands and results documented in evidence

**Validation:**
- `ls -la .claude/skills/sc-cleanup-audit/{rules,templates,scripts} && ls -la .claude/agents/`
- Evidence: linkable artifact produced (directory listing output)

**Dependencies:** None
**Rollback:** `rm -rf .claude/skills/sc-cleanup-audit/` (reversible)
**Notes:** Confidence below 0.70 due to single keyword match ("create" → STANDARD). Task is straightforward directory creation.

---

### T01.02 — Write SKILL.md Frontmatter & Header

**Roadmap Item ID(s):** R-007
**Why:** The frontmatter defines command identity, tool restrictions, and MCP dependencies. All other sections build on this foundation.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (in description text)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0002
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0002/spec.md`

**Deliverables:**
- SKILL.md file with complete YAML frontmatter (6 required + platform fields), H1 title, Triggers section, Usage section

**Steps:**
1. **[PLANNING]** Load spec §2.1 for frontmatter field values and §2.2 for triggers
2. **[PLANNING]** Verify T01.01 directory exists; check no pre-existing SKILL.md
3. **[EXECUTION]** Write YAML frontmatter with all required fields: name, description, category, complexity, mcp-servers, personas, disable-model-invocation, allowed-tools, argument-hint
4. **[EXECUTION]** Write H1 title: `# /sc:cleanup-audit - Multi-Pass Repository Audit`
5. **[EXECUTION]** Write Triggers section with 5 activation scenarios from spec §2.2
6. **[EXECUTION]** Write Usage section with all flags and pipe-separated options from spec §2.3
7. **[VERIFICATION]** Validate frontmatter has all 6 SuperClaude required fields + platform fields; verify field values match spec
8. **[COMPLETION]** Record frontmatter content in spec artifact

**Acceptance Criteria:**
- Frontmatter has all 6 SuperClaude required fields plus platform fields (disable-model-invocation, allowed-tools, argument-hint)
- Field values match spec §2.1 exactly (name: cleanup-audit, category: utility, complexity: high)
- Triggers section has exactly 5 activation scenarios
- Usage section shows all flags with pipe-separated options

**Validation:**
- Manual check: frontmatter YAML parses correctly; all required fields present with correct values
- Evidence: linkable artifact produced (SKILL.md frontmatter content)

**Dependencies:** T01.01
**Rollback:** Delete SKILL.md file (git recoverable)
**Notes:** STRICT tier due to keyword matches on "model" (in mcp-servers/model references) and "permission" (in allowed-tools). These are AI model selection and tool permissions, not data models or access control.

---

### T01.03 — Write Behavioral Flow (5-Step)

**Roadmap Item ID(s):** R-008
**Why:** The 5-step behavioral flow is the core orchestration logic defining how the audit executes end-to-end.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0003
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0003/spec.md`

**Deliverables:**
- Behavioral Flow section in SKILL.md with 5 steps (Discover → Configure → Orchestrate → Validate → Report) + Key behaviors subsection

**Steps:**
1. **[PLANNING]** Load spec §2.4 for behavioral flow requirements and agent names
2. **[PLANNING]** Verify T01.02 complete (SKILL.md exists with frontmatter)
3. **[EXECUTION]** Write Step 1 Discover: repo enumeration, file inventory, batch plan
4. **[EXECUTION]** Write Step 2 Configure: pass selection, rules loading, TodoWrite setup
5. **[EXECUTION]** Write Step 3 Orchestrate: parallel subagent spawning, waves of 7-8, incremental saves
6. **[EXECUTION]** Write Step 4 Validate: audit-validator spawn, 10% spot-check, quality gates
7. **[EXECUTION]** Write Step 5 Report: audit-consolidator spawn, merge reports, ultrathink synthesis
8. **[EXECUTION]** Write Key behaviors section with 5 distinctive characteristics
9. **[VERIFICATION]** Verify exactly 5 steps with single-verb bold labels following Assess → Prepare → Execute → Verify → Output arc
10. **[COMPLETION]** Record behavioral flow content in spec artifact

**Acceptance Criteria:**
- Exactly 5 steps with single-verb bold labels (Discover, Configure, Orchestrate, Validate, Report)
- Steps follow the Assess → Prepare → Execute → Verify → Output arc per SuperClaude convention
- Key behaviors section has exactly 5 bullets describing distinctive characteristics
- All 5 subagent names referenced correctly (audit-scanner, audit-analyzer, audit-comparator, audit-validator, audit-consolidator)

**Validation:**
- Manual check: count steps (must be 5), verify arc mapping, verify agent name references
- Evidence: linkable artifact produced (behavioral flow section content)

**Dependencies:** T01.02
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match ("create" → STANDARD).

---

### T01.04 — Write MCP Integration Section

**Roadmap Item ID(s):** R-009
**Why:** Documents which MCP servers are used, when they activate, and the critical constraint that MCP is unavailable to background subagents.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0004
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0004/spec.md`

**Deliverables:**
- MCP Integration section in SKILL.md with per-server bullets, persona coordination, and MCP constraint note

**Steps:**
1. **[PLANNING]** Load spec §2.5 for MCP integration requirements
2. **[PLANNING]** Verify T01.02 complete; identify insertion point after Behavioral Flow
3. **[EXECUTION]** Write Sequential MCP bullet (cross-cutting synthesis, ultrathink in Step 5)
4. **[EXECUTION]** Write Serena MCP bullet (import chain tracing during discovery)
5. **[EXECUTION]** Write Context7 MCP bullet (framework-specific config validation)
6. **[EXECUTION]** Write Persona Coordination bullet (which personas for which batch domains)
7. **[EXECUTION]** Write MCP Constraint note: "MCP unavailable to background subagents — MCP-dependent work in orchestrator only"
8. **[VERIFICATION]** Verify each declared MCP server has bullet with activation trigger and purpose
9. **[COMPLETION]** Record MCP section content in spec artifact

**Acceptance Criteria:**
- Each declared MCP server (Sequential, Serena, Context7) has a corresponding bullet with activation trigger and purpose
- Persona-MCP alignment is documented (which persona activates which server)
- MCP constraint for subagents is explicitly stated
- Section follows SuperClaude MCP Integration format convention

**Validation:**
- Manual check: verify all 3 MCP servers from frontmatter have matching bullets; verify constraint note present
- Evidence: linkable artifact produced (MCP Integration section content)

**Dependencies:** T01.02
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### T01.05 — Write Tool Coordination Section

**Roadmap Item ID(s):** R-010
**Why:** Defines which tools are available to the orchestrator and subagents, ensuring tool restrictions from frontmatter are documented.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0005
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0005/spec.md`

**Deliverables:**
- Tool Coordination section in SKILL.md with bold-prefixed grouped bullets for each tool category

**Steps:**
1. **[PLANNING]** Load spec §2.6 for tool coordination requirements
2. **[PLANNING]** Cross-reference with `allowed-tools` from frontmatter to ensure consistency
3. **[EXECUTION]** Write Read/Grep/Glob bullet (core audit tools, available to all subagents)
4. **[EXECUTION]** Write Bash(git/wc/find/du) bullet (controlled shell access, orchestrator only)
5. **[EXECUTION]** Write Write bullet (report generation to `.claude-audit/` only)
6. **[EXECUTION]** Write TodoWrite bullet (progress tracking, per-batch tasks)
7. **[EXECUTION]** Write Task bullet (subagent delegation, list all 5 agent types)
8. **[VERIFICATION]** Verify only tools from `allowed-tools` frontmatter are listed; verify grouping follows convention
9. **[COMPLETION]** Record Tool Coordination content in spec artifact

**Acceptance Criteria:**
- Tools grouped by category per SuperClaude convention (bold-prefixed grouped bullets)
- Only tools from `allowed-tools` frontmatter are listed (no unlisted tools)
- Tool restrictions per agent type are clearly stated
- Section is consistent with frontmatter allowed-tools declaration

**Validation:**
- Manual check: diff tool list against frontmatter `allowed-tools`; verify grouping format
- Evidence: linkable artifact produced (Tool Coordination section content)

**Dependencies:** T01.02
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### Checkpoint: Phase 1 / Tasks T01.01–T01.05

**Purpose:** Verify the foundational SKILL.md structure is sound before writing remaining sections.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P01-T01-T05.md`

**Verification:**
- SKILL.md exists with valid frontmatter, H1 title, Triggers, Usage, Behavioral Flow, MCP Integration, and Tool Coordination sections
- Directory structure `.claude/skills/sc-cleanup-audit/{rules,templates,scripts}` exists
- All sections follow SuperClaude conventions (bold labels, grouped bullets, arrow notation where applicable)

**Exit Criteria:**
- T01.01–T01.05 all marked completed with no blocking issues
- SKILL.md frontmatter passes YAML validation
- No section ordering violations detected

---

### T01.06 — Write Key Patterns Section

**Roadmap Item ID(s):** R-011
**Why:** Key Patterns document the distinctive transformation patterns that make this command unique.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0006
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0006/spec.md`

**Deliverables:**
- Key Patterns section with 5 arrow-notation patterns

**Steps:**
1. **[PLANNING]** Load spec §2.7 for key pattern definitions
2. **[PLANNING]** Verify insertion point after Tool Coordination section
3. **[EXECUTION]** Write 5 key patterns using arrow notation: Haiku-First Escalation, Evidence-Gated Classification, Incremental Checkpoint, Fan-Out/Fan-In Orchestration, Conservative Escalation
4. **[VERIFICATION]** Verify 5 patterns with arrow notation (input → transformation → output); pattern names in Title Case
5. **[COMPLETION]** Record Key Patterns content in spec artifact

**Acceptance Criteria:**
- Exactly 5 patterns with arrow notation (input → transformation → output)
- Pattern names in Title Case, 2-3 words each
- Patterns match spec §2.7 content
- Arrow notation follows SuperClaude convention

**Validation:**
- Manual check: count patterns (must be 5); verify arrow notation format
- Evidence: linkable artifact produced (Key Patterns section content)

**Dependencies:** T01.05
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### T01.07 — Write Examples Section

**Roadmap Item ID(s):** R-012
**Why:** Examples demonstrate command usage progressing from simple to complex, critical for user adoption.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0007
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0007/spec.md`

**Deliverables:**
- Examples section with 4 examples progressing simple → complex, each with code block + comment lines

**Steps:**
1. **[PLANNING]** Load spec §2.8 for example requirements
2. **[PLANNING]** Verify insertion point after Key Patterns section
3. **[EXECUTION]** Write Example 1: Full Repository Surface Scan (basic, no flags)
4. **[EXECUTION]** Write Example 2: Structural Audit of Source Directory (--pass structural --batch-size 25)
5. **[EXECUTION]** Write Example 3: Infrastructure Cross-Cutting Sweep (--pass cross-cutting --focus infrastructure)
6. **[EXECUTION]** Write Example 4: Complete 3-Pass Audit (--pass all, advanced usage)
7. **[VERIFICATION]** Verify 4 examples progress simple → complex; each has code block + 3-4 comment lines
8. **[COMPLETION]** Record Examples content in spec artifact

**Acceptance Criteria:**
- Exactly 4 examples progressing from simple to complex
- Each example has fenced code block + 3-4 comment lines explaining behavior
- Examples match spec §2.8 content
- Flag combinations in examples are valid per Usage section

**Validation:**
- Manual check: count examples (must be 4); verify progression simple → complex
- Evidence: linkable artifact produced (Examples section content)

**Dependencies:** T01.06
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### T01.08 — Write Boundaries and Critical Boundaries

**Roadmap Item ID(s):** R-013
**Why:** Boundaries define what the command will and will not do. Critical Boundaries enforce the read-only safety constraint.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0008
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0008/spec.md`

**Deliverables:**
- Boundaries section (Will: 3, Will Not: 3) + Critical Boundaries section (STOP directive, Explicitly Will NOT, Output, Next Step)

**Steps:**
1. **[PLANNING]** Load spec §2.9–§2.10 for boundary definitions
2. **[PLANNING]** Verify insertion point after Examples section
3. **[EXECUTION]** Write "Will:" with 3 positive capabilities
4. **[EXECUTION]** Write "Will Not:" with 3 negative constraints
5. **[EXECUTION]** Write Critical Boundaries with bold STOP directive: **READ-ONLY AUDIT — NO REPOSITORY MODIFICATIONS**
6. **[EXECUTION]** Write "Explicitly Will NOT" list (4 items), "Output" specification (4 output types), "Next Step" chain: `/sc:cleanup` → `/sc:test` → `/sc:git`
7. **[VERIFICATION]** Verify Will/Will Not each have exactly 3 bullets; STOP directive is bold caps; Next Step chains to specific /sc:* commands
8. **[COMPLETION]** Record Boundaries content in spec artifact

**Acceptance Criteria:**
- Will/Will Not sections each have exactly 3 bullets (boundary symmetry)
- Critical Boundaries has STOP directive in bold caps
- Next Step chains to specific /sc:* commands (`/sc:cleanup` → `/sc:test` → `/sc:git`)
- Read-only constraint is unambiguous and prominent

**Validation:**
- Manual check: count Will bullets (3), Will Not bullets (3); verify STOP directive format
- Evidence: linkable artifact produced (Boundaries section content)

**Dependencies:** T01.07
**Rollback:** Edit SKILL.md to remove section (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### T01.09 — Write Shell Preprocessing Context Block

**Roadmap Item ID(s):** R-014
**Why:** Shell preprocessing injects live repo metadata before Claude sees the prompt, eliminating wasteful discovery steps.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0009
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0009/spec.md`

**Deliverables:**
- Repository Context block with `!`cmd`` preprocessing and Target Scope block with `$ARGUMENTS`

**Steps:**
1. **[PLANNING]** Load spec §2.11 and custom command guide §9 for preprocessing patterns
2. **[PLANNING]** Verify insertion point in SKILL.md (typically near top, after Usage)
3. **[EXECUTION]** Write Repository Context block: total files, file breakdown, repo size, current branch, last commit using `!`cmd`` syntax
4. **[EXECUTION]** Write Target Scope block using `$ARGUMENTS` for user-provided target path
5. **[VERIFICATION]** Verify `!`cmd`` syntax is correct; verify `$ARGUMENTS` correctly references target path
6. **[COMPLETION]** Record preprocessing block content in spec artifact

**Acceptance Criteria:**
- Shell preprocessing uses correct `!`cmd`` syntax (backtick-wrapped shell commands with ! prefix)
- $ARGUMENTS correctly references user-provided target path
- Preprocessing provides enough context for batch planning (file counts, types, size)
- Repository context includes all 5 required fields (total files, breakdown, size, branch, commit)

**Validation:**
- Manual check: verify `!`cmd`` syntax matches Claude Code skill preprocessing format
- Evidence: linkable artifact produced (preprocessing block content)

**Dependencies:** T01.02
**Rollback:** Edit SKILL.md to remove block (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### T01.10 — Write repo-inventory.sh Script

**Roadmap Item ID(s):** R-015
**Why:** The script automates file enumeration, exclusion filtering, domain grouping, and batch creation for the audit.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0010
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0010/spec.md`
- `.roadmaps/v1.06/artifacts/D-0010/evidence.md`

**Deliverables:**
- Executable shell script at `.claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh` producing file inventory with domain grouping and batch assignments

**Steps:**
1. **[PLANNING]** Load spec §6 for batch strategy and exclusion requirements
2. **[PLANNING]** Design script interface: `repo-inventory.sh <target-path> <batch-size>`
3. **[EXECUTION]** Write file enumeration using `git ls-files` (respects .gitignore)
4. **[EXECUTION]** Write exclusion logic for `.git/`, `node_modules/`, build outputs, caches, vendor
5. **[EXECUTION]** Write file type distribution calculation and domain-based grouping
6. **[EXECUTION]** Write batch creation logic with configurable batch size
7. **[EXECUTION]** Write coverage tracking output (files_audited / total)
8. **[VERIFICATION]** Make executable (`chmod +x`); test with `./repo-inventory.sh . 50`
9. **[COMPLETION]** Record script content and test output in artifacts

**Acceptance Criteria:**
- Uses `git ls-files` for portable, .gitignore-respecting enumeration
- All exclusion patterns from spec §7.1 are applied (.git/, node_modules/, build outputs, caches, vendor)
- Output is machine-parseable (one file per line, grouped by domain)
- Script is POSIX-compatible (no bash-isms) and executable

**Validation:**
- `chmod +x .claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh && .claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh . 50`
- Evidence: linkable artifact produced (script content + test output)

**Dependencies:** T01.01
**Rollback:** Delete script file (git recoverable)
**Notes:** Confidence below 0.70 due to single keyword match.

---

### Checkpoint: Phase 1 / Tasks T01.06–T01.10

**Purpose:** Verify remaining SKILL.md sections and repo-inventory.sh script are complete and consistent.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P01-T06-T10.md`

**Verification:**
- SKILL.md contains Key Patterns (5), Examples (4), Boundaries (3/3), Critical Boundaries (STOP directive), Shell Preprocessing
- repo-inventory.sh is executable and produces valid output
- All sections follow SuperClaude conventions

**Exit Criteria:**
- T01.06–T01.10 all marked completed with no blocking issues
- SKILL.md sections are in correct order per 13-section template
- repo-inventory.sh test run produces expected output format

---

### T01.11 — SKILL.md Line Count Validation

**Roadmap Item ID(s):** R-016
**Why:** SKILL.md must stay under 500 lines per SuperClaude convention. Validates no section bloat.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0011
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0011/evidence.md`

**Deliverables:**
- Line count validation result confirming SKILL.md is under 500 lines, or remediation actions taken

**Steps:**
1. **[PLANNING]** Identify the 500-line limit from SuperClaude convention
2. **[PLANNING]** Check dependencies: T01.02–T01.09 must be complete
3. **[EXECUTION]** Count total lines in SKILL.md via `wc -l`
4. **[EXECUTION]** If >500 lines, identify content to move to supporting files (rules/ or templates/)
5. **[VERIFICATION]** Confirm final line count is ≤500
6. **[COMPLETION]** Record line count and any remediation actions in evidence artifact

**Acceptance Criteria:**
- SKILL.md is under 500 lines
- All domain-specific rules are in `rules/` files, not inline in SKILL.md
- Orchestration logic remains in SKILL.md (not moved out)
- Line count and validation result documented

**Validation:**
- `wc -l .claude/skills/sc-cleanup-audit/SKILL.md`
- Evidence: linkable artifact produced (line count output)

**Dependencies:** T01.02, T01.03, T01.04, T01.05, T01.06, T01.07, T01.08, T01.09
**Rollback:** TBD (refactoring may be needed if over limit)
**Notes:** Confidence below 0.70 due to single keyword match. This is a validation task, not a creation task.

---

### Checkpoint: End of Phase 1

**Purpose:** Verify the complete Foundation & Orchestration milestone is ready for dependent milestones.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P01-END.md`

**Verification:**
- SKILL.md is complete with all 13 sections per SuperClaude template and under 500 lines
- repo-inventory.sh is executable and produces valid domain-grouped file inventory
- Directory structure `.claude/skills/sc-cleanup-audit/{rules,templates,scripts}` and `.claude/agents/` exist

**Exit Criteria:**
- All 11 Phase 1 tasks (T01.01–T01.11) marked completed
- SKILL.md passes structural validation (13 sections, <500 lines, valid frontmatter)
- No blocking issues for Phase 2, 3, or 4

---

## Phase 2: Rules Engine

Create the 5 rules files that define audit methodology, evidence standards, and per-pass criteria. These are loaded by subagents as supporting files. All tasks in this phase are independent and can execute in parallel.

### T02.01 — Write Pass 1 Surface Scan Rules

**Roadmap Item ID(s):** R-017
**Why:** Pass 1 rules define the surface-scan methodology: 3-tier classification, verification protocol, and output format for the scanner agent.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0012
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0012/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/rules/pass1-surface-scan.md` with classification taxonomy, verification protocol, output format, batch guidance

**Steps:**
1. **[PLANNING]** Load spec §3.1 (Pass 1 Surface Scan) and supplementary context spec §3 Pass 1
2. **[PLANNING]** Verify `.claude/skills/sc-cleanup-audit/rules/` directory exists
3. **[EXECUTION]** Write goal statement and guiding question ("Is this file junk?")
4. **[EXECUTION]** Write 3-tier classification taxonomy table (DELETE/REVIEW/KEEP) from spec §3.1
5. **[EXECUTION]** Write verification protocol (4-step: read → grep → check imports → categorize)
6. **[EXECUTION]** Write output format template (Safe to Delete, Need Decision, Keep, Add to .gitignore)
7. **[EXECUTION]** Write batch size guidance (25-50 normal, 50-100 binary/assets) and binary asset handling rules
8. **[EXECUTION]** Write section on "zero references" evidence standard (grep pattern + count + zero-result confirmation)
9. **[VERIFICATION]** Verify 3-tier taxonomy matches spec exactly; all 4 verification protocol steps present
10. **[COMPLETION]** Record rules file content in spec artifact

**Acceptance Criteria:**
- 3-tier taxonomy (DELETE/REVIEW/KEEP) matches spec §3.1 exactly
- Verification protocol has all 4 steps (read → grep → check imports → categorize)
- Output format includes all 4 sections (Delete, Decision, Keep, Gitignore)
- Evidence standard for DELETE is explicit (grep proof with pattern + count required)

**Validation:**
- Manual check: verify taxonomy table has 3 rows; verification protocol has 4 numbered steps
- Evidence: linkable artifact produced (pass1-surface-scan.md content)

**Dependencies:** T01.01 (directory must exist)
**Rollback:** Delete rules file (git recoverable)
**Notes:** Two STANDARD keyword matches ("create" implicit via "write", "build" via output format). Confidence boosted.

---

### T02.02 — Write Pass 2 Structural Audit Rules

**Roadmap Item ID(s):** R-018
**Why:** Pass 2 rules define deep structural profiling: 8-field per-file profiles, extra rules by file type, and failure criteria.
**Effort:** `M`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0013
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0013/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/rules/pass2-structural-audit.md` with finding types, 8-field profile, file-type rules, failure criterion

**Steps:**
1. **[PLANNING]** Load spec §3.2 (Pass 2 Structural Audit) and supplementary context spec §3 Pass 2
2. **[PLANNING]** Verify rules directory exists; check no pre-existing file
3. **[EXECUTION]** Write goal statement and guiding question
4. **[EXECUTION]** Write 5 finding types table and 4 action recommendations table
5. **[EXECUTION]** Write mandatory per-file profile with all 8 fields from spec §3.2
6. **[EXECUTION]** Write extra rules by file type (tests, scripts, documentation, config)
7. **[EXECUTION]** Write failure criterion and scope limitation (only KEEP/REVIEW from Pass 1)
8. **[VERIFICATION]** Verify all 8 profile fields present; 4 file-type extra rules included
9. **[COMPLETION]** Record rules file content in spec artifact

**Acceptance Criteria:**
- All 8 mandatory per-file profile fields present with requirement descriptions
- Extra rules for 4 file types (tests, scripts, docs, config)
- Failure criterion is explicit: "Reports missing mandatory per-file profiles are FAILED"
- Scope limitation references Pass 1 output (KEEP/REVIEW files only)

**Validation:**
- Manual check: count profile fields (must be 8); verify 4 file-type extra rule sections
- Evidence: linkable artifact produced (pass2-structural-audit.md content)

**Dependencies:** T01.01
**Rollback:** Delete rules file (git recoverable)
**Notes:** Effort M due to CI/CD keyword in steps text (file-type rules include CI/CD checks).

---

### T02.03 — Write Pass 3 Cross-Cutting Rules

**Roadmap Item ID(s):** R-019
**Why:** Pass 3 rules define cross-cutting comparison methodology: duplication matrix, tiered depth, and CONSOLIDATE classification.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0014
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0014/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/rules/pass3-cross-cutting.md` with extended taxonomy, 7-field profile, differentiators, duplication matrix

**Steps:**
1. **[PLANNING]** Load spec §3.3 (Pass 3 Cross-Cutting Sweep) and supplementary context
2. **[PLANNING]** Verify rules directory exists
3. **[EXECUTION]** Write goal, extended taxonomy (CONSOLIDATE + BROKEN REF), and 7-field profile
4. **[EXECUTION]** Write 6 critical differentiators from Pass 2 (compare don't catalog, group audit, duplication matrix, known issues, auto-KEEP, directory-level assessments)
5. **[EXECUTION]** Write focus areas and tiered P3 depth strategy (deep/medium/light by category)
6. **[EXECUTION]** Write mandatory duplication matrix requirement with format specification
7. **[VERIFICATION]** Verify extended taxonomy includes CONSOLIDATE and BROKEN REF; all 6 differentiators present
8. **[COMPLETION]** Record rules file content in spec artifact

**Acceptance Criteria:**
- Extended taxonomy includes CONSOLIDATE and BROKEN REF classifications
- All 6 differentiators from spec §3.3 are present and described
- Duplication matrix is mandatory with explicit format (overlap percentages)
- Tiered depth strategy has file count estimates per tier

**Validation:**
- Manual check: verify CONSOLIDATE in taxonomy; count differentiators (must be 6)
- Evidence: linkable artifact produced (pass3-cross-cutting.md content)

**Dependencies:** T01.01
**Rollback:** Delete rules file (git recoverable)
**Notes:** Confidence 60% from multiple STANDARD keyword matches.

---

### T02.04 — Write Universal Verification Protocol

**Roadmap Item ID(s):** R-020
**Why:** Defines evidence requirements for every recommendation type and the cross-reference checklist used by all passes.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0015
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0015/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/rules/verification-protocol.md` with evidence checklists, cross-reference sources, and 16 cleanup principles

**Steps:**
1. **[PLANNING]** Load spec §4 (Unified Classification Taxonomy) and §5 (Verification Protocol) and §13 (Cleanup Principles)
2. **[PLANNING]** Verify rules directory exists
3. **[EXECUTION]** Write unified classification taxonomy (priority-ordered, 6 categories) from spec §4
4. **[EXECUTION]** Write evidence requirements per recommendation type: DELETE (4 items), KEEP (5), CONSOLIDATE (3), FLAG (4), MOVE (2)
5. **[EXECUTION]** Write cross-reference checklist (7 reference sources) from spec §5
6. **[EXECUTION]** Write documentation claim verification protocol
7. **[EXECUTION]** Write 16 reusable cleanup principles from spec §13
8. **[VERIFICATION]** Verify all 5 recommendation types have checklists; cross-reference has 7 sources; 16 principles present
9. **[COMPLETION]** Record rules file content in spec artifact

**Acceptance Criteria:**
- All 5 recommendation types (DELETE, KEEP, CONSOLIDATE, FLAG, MOVE) have explicit checklist evidence requirements
- Cross-reference checklist has all 7 source types
- All 16 cleanup principles are present and ordered by dependency
- Evidence requirements use checkbox format for verifiability

**Validation:**
- Manual check: count recommendation checklists (5); count cross-reference sources (7); count principles (16)
- Evidence: linkable artifact produced (verification-protocol.md content)

**Dependencies:** T01.01
**Rollback:** Delete rules file (git recoverable)
**Notes:** Confidence 60% from multiple STANDARD keyword matches.

---

### T02.05 — Write Dynamic-Use Checklist

**Roadmap Item ID(s):** R-021
**Why:** Prevents false DELETE recommendations by documenting 5 dynamic loading patterns that bypass static reference analysis.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Context7 | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0016
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0016/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/rules/dynamic-use-checklist.md` with 5 dynamic loading patterns and per-language examples

**Steps:**
1. **[PLANNING]** Load spec §5 (Dynamic-Use Checklist section) and supplementary context spec §11 item 4
2. **[PLANNING]** Verify rules directory exists
3. **[EXECUTION]** Write 5 dynamic loading patterns: environment variable-based, string-based imports, plugin registries, glob-based discovery, config-driven loading
4. **[EXECUTION]** For each pattern, provide per-language examples (JavaScript, Python minimum; Go, Ruby where applicable)
5. **[EXECUTION]** Write instruction: "Check ALL patterns before classifying as DELETE"
6. **[VERIFICATION]** Verify all 5 patterns documented; per-language examples for at least JavaScript and Python
7. **[COMPLETION]** Record checklist content in spec artifact

**Acceptance Criteria:**
- All 5 patterns documented with descriptions and per-language examples
- Per-language examples for at least JavaScript and Python
- Clear instruction on when to apply (before any DELETE classification)
- Patterns match spec §5 dynamic-use requirements

**Validation:**
- Manual check: count patterns (must be 5); verify JS + Python examples present per pattern
- Evidence: linkable artifact produced (dynamic-use-checklist.md content)

**Dependencies:** T01.01
**Rollback:** Delete rules file (git recoverable)
**Notes:** Confidence 60% from multiple STANDARD keyword matches.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify all 5 rules files are complete and internally consistent before subagent definitions reference them.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P02-END.md`

**Verification:**
- All 5 rules files exist in `.claude/skills/sc-cleanup-audit/rules/`
- Each file covers its pass methodology completely (taxonomy, evidence, output format)
- verification-protocol.md contains all 16 cleanup principles

**Exit Criteria:**
- All 5 Phase 2 tasks (T02.01–T02.05) marked completed
- No cross-reference inconsistencies between rules files
- Rules files are ready to be embedded in or referenced by subagent prompts

---

## Phase 3: Output Templates

Create the 4 report templates and finding profile template that enforce structured, consistent output from all subagents. All tasks are independent and can execute in parallel. Phase 3 can run in parallel with Phase 2.

### T03.01 — Write Batch Report Template

**Roadmap Item ID(s):** R-022
**Why:** The batch report template enforces consistent per-agent output with all required sections across all passes.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0017
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0017/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/templates/batch-report.md` with all 8 content sections + header + summary + notes

**Steps:**
1. **[PLANNING]** Load spec §7 Output Schema (Per-Agent Output) and supplementary context spec §7
2. **[PLANNING]** Verify templates directory exists
3. **[EXECUTION]** Write header section (scope, pass number, status, files audited, date)
4. **[EXECUTION]** Write 6 content sections: Files to DELETE, CONSOLIDATE, MOVE, FLAG, Broken References, Files to KEEP
5. **[EXECUTION]** Write "Remaining / Not Audited" section (mandatory if scope incomplete) and Summary section
6. **[EXECUTION]** Write Notes section for cross-cutting observations
7. **[VERIFICATION]** Verify all 8 content sections present; "Remaining" marked as mandatory for incomplete scope
8. **[COMPLETION]** Record template content in spec artifact

**Acceptance Criteria:**
- All 8 content sections present (DELETE, CONSOLIDATE, MOVE, FLAG, BROKEN REFS, KEEP, Remaining, Summary)
- Header has status, files audited count, date fields
- "Remaining / Not Audited" section explicitly marked as mandatory for incomplete scope
- Template matches spec §7 Per-Agent Batch Report format

**Validation:**
- Manual check: count content sections (must be 8); verify header fields
- Evidence: linkable artifact produced (batch-report.md content)

**Dependencies:** T01.01
**Rollback:** Delete template file (git recoverable)
**Notes:** Confidence 60% from multiple STANDARD keyword matches.

---

### T03.02 — Write Pass Summary Template

**Roadmap Item ID(s):** R-023
**Why:** The pass summary template consolidates batch reports into a single pass-level view with deduplication and cross-agent patterns.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0018
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0018/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/templates/pass-summary.md` with aggregate counts, coverage metrics, cross-agent patterns, validation results

**Steps:**
1. **[PLANNING]** Load spec §7 for pass summary requirements
2. **[PLANNING]** Verify templates directory exists
3. **[EXECUTION]** Write header, aggregate summary counts, coverage metrics section
4. **[EXECUTION]** Write cross-agent patterns, validation results, deduplication notes, quality gate status
5. **[VERIFICATION]** Verify coverage metrics mandatory; quality gate status with pass/fail
6. **[COMPLETION]** Record template content in spec artifact

**Acceptance Criteria:**
- Coverage metrics (files_audited / total = %) are mandatory
- Cross-agent pattern extraction section present
- Quality gate status includes pass/fail with evidence
- Deduplication notes section present

**Validation:**
- Manual check: verify coverage metrics field; verify quality gate status section
- Evidence: linkable artifact produced (pass-summary.md content)

**Dependencies:** T01.01
**Rollback:** Delete template file (git recoverable)

---

### T03.03 — Write Final Report Template

**Roadmap Item ID(s):** R-024
**Why:** The final report template structures the executive summary and prioritized action items that stakeholders act on.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0019
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0019/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/templates/final-report.md` with executive summary, 3-tier action items, cross-cutting findings, issues registry

**Steps:**
1. **[PLANNING]** Load spec §7 Consolidated Final Report section
2. **[PLANNING]** Verify templates directory exists
3. **[EXECUTION]** Write Executive Summary section (total files, coverage %, action counts, effort estimate)
4. **[EXECUTION]** Write "Action Items by Priority" with 3 subsections: Immediate, Requires Decision, Requires Code Changes
5. **[EXECUTION]** Write Cross-Cutting Findings section and Discovered Issues Registry
6. **[VERIFICATION]** Verify executive summary has all 4 metrics; action items split into 3 tiers
7. **[COMPLETION]** Record template content in spec artifact

**Acceptance Criteria:**
- Executive Summary has all 4 required metrics (total files, coverage %, action counts, effort estimate)
- Action items split into 3 priority tiers (Immediate, Requires Decision, Requires Code Changes)
- Discovered Issues Registry is numbered list format
- Template matches spec §7 Consolidated Final Report format

**Validation:**
- Manual check: verify 4 executive summary metrics; count action item tiers (must be 3)
- Evidence: linkable artifact produced (final-report.md content)

**Dependencies:** T01.01
**Rollback:** Delete template file (git recoverable)

---

### T03.04 — Write Finding Profile Template

**Roadmap Item ID(s):** R-025
**Why:** The finding profile template ensures all mandatory fields are present in per-file assessments across Pass 2 and Pass 3.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 60%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0020
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0020/spec.md`

**Deliverables:**
- `.claude/skills/sc-cleanup-audit/templates/finding-profile.md` with Pass 2 (8-field) and Pass 3 (7-field) profile formats

**Steps:**
1. **[PLANNING]** Load spec §3.2 (Pass 2 profile) and §3.3 (Pass 3 profile)
2. **[PLANNING]** Verify templates directory exists
3. **[EXECUTION]** Write Pass 2 profile format with all 8 mandatory fields
4. **[EXECUTION]** Write Pass 3 profile format with all 7 fields
5. **[EXECUTION]** Add mandatory instruction: "ALL fields are MANDATORY. Reports with missing fields are FAILED."
6. **[VERIFICATION]** Count Pass 2 fields (8) and Pass 3 fields (7); verify mandatory instruction present
7. **[COMPLETION]** Record template content in spec artifact

**Acceptance Criteria:**
- Pass 2 template has all 8 fields (What it does, Nature, References, CI/CD usage, Superseded by/duplicates, Risk notes, Recommendation, Verification notes)
- Pass 3 template has all 7 fields (What it does, Nature, References, Similar files, Superseded?, Currently used?, Recommendation)
- Mandatory instruction is explicit and prominent
- Field descriptions match spec §3.2 and §3.3 exactly

**Validation:**
- Manual check: count Pass 2 fields (8); count Pass 3 fields (7); verify mandatory instruction
- Evidence: linkable artifact produced (finding-profile.md content)

**Dependencies:** T01.01
**Rollback:** Delete template file (git recoverable)

---

### Checkpoint: End of Phase 3

**Purpose:** Verify all 4 template files are complete and consistent with the rules files from Phase 2.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P03-END.md`

**Verification:**
- All 4 template files exist in `.claude/skills/sc-cleanup-audit/templates/`
- batch-report.md has all 8 content sections
- finding-profile.md field counts match spec (Pass 2: 8, Pass 3: 7)

**Exit Criteria:**
- All 4 Phase 3 tasks (T03.01–T03.04) marked completed
- Template field names are consistent with rules file references
- Templates are ready for embedding in subagent prompts

---

## Phase 4: Subagent Definitions

Create the 5 custom subagent definition files that define specialized worker behaviors for each audit phase. All tasks are independent and can execute in parallel. Depends on Phase 1 (SKILL.md spawns agents) and Phase 2 (agents reference rules).

### T04.01 — Write audit-scanner.md (Pass 1 Worker)

**Roadmap Item ID(s):** R-026
**Why:** The scanner agent performs fast surface-scan classification using Haiku for cost optimization. It is the most-spawned agent type.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0021
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0021/spec.md`

**Deliverables:**
- `.claude/agents/audit-scanner.md` with frontmatter (model: haiku, tools: Read/Grep/Glob, maxTurns: 20) and system prompt

**Steps:**
1. **[PLANNING]** Load spec §4 (subagent definitions) for scanner requirements; load Pass 1 rules
2. **[PLANNING]** Verify `.claude/agents/` directory exists; check no pre-existing file
3. **[EXECUTION]** Write frontmatter: name, description, tools (Read, Grep, Glob), model (haiku), maxTurns (20), permissionMode (plan)
4. **[EXECUTION]** Write system prompt: role description, input specification (batch file list), methodology (read 20-30 lines → grep → classify)
5. **[EXECUTION]** Write classification taxonomy (DELETE/REVIEW/KEEP), output format reference, safety instruction, incremental save instruction
6. **[VERIFICATION]** Verify model is haiku; tools are read-only (Read, Grep, Glob); maxTurns is 20; safety instruction present
7. **[COMPLETION]** Record agent definition content in spec artifact

**Acceptance Criteria:**
- Frontmatter has all required fields (name, description, tools, model, maxTurns, permissionMode)
- `model: haiku` for cost optimization (not sonnet/opus)
- `tools: Read, Grep, Glob` enforces read-only at platform level
- System prompt covers methodology, output format, safety ("DO NOT modify any file"), and incremental save

**Validation:**
- Manual check: verify model is "haiku"; verify tools list is exactly "Read, Grep, Glob"; verify maxTurns is 20
- Evidence: linkable artifact produced (audit-scanner.md content)

**Dependencies:** T01.01, T02.01
**Rollback:** Delete agent file (git recoverable)
**Notes:** STRICT tier from "model" and "permission" keyword matches in frontmatter specification text. These refer to AI model selection and agent permission mode.

---

### T04.02 — Write audit-analyzer.md (Pass 2 Worker)

**Roadmap Item ID(s):** R-027
**Why:** The analyzer agent performs deep structural profiling using Sonnet, producing mandatory 8-field per-file profiles.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0022
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0022/spec.md`

**Deliverables:**
- `.claude/agents/audit-analyzer.md` with frontmatter (model: sonnet, tools: Read/Grep/Glob, maxTurns: 35) and system prompt

**Steps:**
1. **[PLANNING]** Load spec §4 for analyzer requirements; load Pass 2 rules and finding-profile template
2. **[PLANNING]** Verify `.claude/agents/` directory exists
3. **[EXECUTION]** Write frontmatter: name, description, tools (Read, Grep, Glob), model (sonnet), maxTurns (35), permissionMode (plan)
4. **[EXECUTION]** Write system prompt: role, input (batch file list + Pass 1 context), methodology (full 8-field profile per file)
5. **[EXECUTION]** Write finding types, extra rules by file type (tests, scripts, docs, config), evidence standard, failure criterion
6. **[VERIFICATION]** Verify model is sonnet; system prompt requires all 8 profile fields; failure criterion stated
7. **[COMPLETION]** Record agent definition content in spec artifact

**Acceptance Criteria:**
- `model: sonnet` for deeper analysis than Pass 1
- System prompt requires all 8 mandatory profile fields per file
- Extra rules for 4 file types (tests, scripts, docs, config) are included in prompt
- Failure criterion explicitly stated: "Reports missing mandatory fields are FAILED"

**Validation:**
- Manual check: verify model is "sonnet"; count profile field requirements in prompt (8); verify failure criterion
- Evidence: linkable artifact produced (audit-analyzer.md content)

**Dependencies:** T01.01, T02.02
**Rollback:** Delete agent file (git recoverable)
**Notes:** STRICT tier from "model" and "permission" keyword matches.

---

### T04.03 — Write audit-comparator.md (Pass 3 Worker)

**Roadmap Item ID(s):** R-028
**Why:** The comparator agent detects cross-cutting duplication and sprawl, producing duplication matrices with overlap quantification.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0023
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0023/spec.md`

**Deliverables:**
- `.claude/agents/audit-comparator.md` with frontmatter (model: sonnet, tools: Read/Grep/Glob, maxTurns: 35) and system prompt

**Steps:**
1. **[PLANNING]** Load spec §4 for comparator requirements; load Pass 3 rules
2. **[PLANNING]** Verify `.claude/agents/` directory exists
3. **[EXECUTION]** Write frontmatter: name, description, tools (Read, Grep, Glob), model (sonnet), maxTurns (35), permissionMode (plan)
4. **[EXECUTION]** Write system prompt: role (cross-cutting comparator), input (similar files grouped by type + Pass 1-2 findings)
5. **[EXECUTION]** Write extended taxonomy (CONSOLIDATE, BROKEN REF), 6 differentiators, known-issues dedup, auto-KEEP, duplication matrix requirement
6. **[VERIFICATION]** Verify CONSOLIDATE classification defined; duplication matrix mandatory; 6 differentiators present
7. **[COMPLETION]** Record agent definition content in spec artifact

**Acceptance Criteria:**
- CONSOLIDATE classification is defined with overlap quantification requirement (% overlap)
- Mandatory duplication matrix requirement in system prompt
- Known-issues deduplication instruction present
- All 6 differentiators from spec §3.3 are included

**Validation:**
- Manual check: verify CONSOLIDATE in taxonomy; verify duplication matrix requirement; count differentiators (6)
- Evidence: linkable artifact produced (audit-comparator.md content)

**Dependencies:** T01.01, T02.03
**Rollback:** Delete agent file (git recoverable)
**Notes:** STRICT tier from "model" and "permission" keyword matches.

---

### T04.04 — Write audit-consolidator.md (Report Merger)

**Roadmap Item ID(s):** R-029
**Why:** The consolidator merges batch reports into pass summaries and final reports with deduplication and cross-agent pattern extraction.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0024
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0024/spec.md`

**Deliverables:**
- `.claude/agents/audit-consolidator.md` with frontmatter (model: sonnet, tools: Read/Grep/Glob/Write, maxTurns: 40) and system prompt

**Steps:**
1. **[PLANNING]** Load spec §4 for consolidator requirements; load pass-summary and final-report templates
2. **[PLANNING]** Verify `.claude/agents/` directory exists
3. **[EXECUTION]** Write frontmatter: name, description, tools (Read, Grep, Glob, Write), model (sonnet), maxTurns (40), permissionMode (plan)
4. **[EXECUTION]** Write system prompt: role (report merger), input (all batch reports + template), methodology (merge → deduplicate → extract patterns → summarize)
5. **[EXECUTION]** Write quality requirements: summary counts, coverage metrics, remaining/not-audited mandatory
6. **[VERIFICATION]** Verify tools include Write (only agent that can write reports); dedup methodology explicit
7. **[COMPLETION]** Record agent definition content in spec artifact

**Acceptance Criteria:**
- `tools` includes `Write` (the only agent type authorized to write report files)
- Deduplication methodology is explicit in system prompt
- Cross-agent pattern extraction is required in output
- Coverage metrics are mandatory in consolidated output

**Validation:**
- Manual check: verify "Write" in tools list; verify dedup instructions; verify pattern extraction requirement
- Evidence: linkable artifact produced (audit-consolidator.md content)

**Dependencies:** T01.01, T02.04
**Rollback:** Delete agent file (git recoverable)
**Notes:** STRICT tier from "model" and "permission" keyword matches. This is the only agent with Write access.

---

### T04.05 — Write audit-validator.md (Quality Checker)

**Roadmap Item ID(s):** R-030
**Why:** The validator independently spot-checks audit findings to catch false positives/negatives before reports are finalized.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STRICT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer, 3-5K tokens, 60s)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required
**Deliverable IDs:** D-0025
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0025/spec.md`

**Deliverables:**
- `.claude/agents/audit-validator.md` with frontmatter (model: sonnet, tools: Read/Grep/Glob, maxTurns: 25) and system prompt

**Steps:**
1. **[PLANNING]** Load spec §4 for validator requirements; load spec §9 Quality Gates
2. **[PLANNING]** Verify `.claude/agents/` directory exists
3. **[EXECUTION]** Write frontmatter: name, description, tools (Read, Grep, Glob), model (sonnet), maxTurns (25), permissionMode (plan)
4. **[EXECUTION]** Write system prompt: role (independent validator), input (randomly sampled 5 findings per 50 files), methodology (re-grep, verify file read, check accuracy)
5. **[EXECUTION]** Write independence instruction: "Do NOT assume prior agent was correct. Verify from scratch."
6. **[VERIFICATION]** Verify sampling rate explicit (5 per 50 = 10%); 4 verification checks present; independence instruction present
7. **[COMPLETION]** Record agent definition content in spec artifact

**Acceptance Criteria:**
- Sampling rate is explicit (5 per 50 files = 10%)
- 4 verification checks from spec §9 are present (grep claim accuracy, file actually read, KEEP genuineness, DELETE safety)
- Independence instruction prevents confirmation bias
- maxTurns (25) is appropriate for validation scope

**Validation:**
- Manual check: verify sampling rate; count verification checks (4); verify independence instruction
- Evidence: linkable artifact produced (audit-validator.md content)

**Dependencies:** T01.01, T02.04
**Rollback:** Delete agent file (git recoverable)
**Notes:** STRICT tier + Risk High → Sub-Agent Delegation Required.

---

### Checkpoint: End of Phase 4

**Purpose:** Verify all 5 custom subagent definitions are complete, consistent with rules, and properly constrained.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P04-END.md`

**Verification:**
- All 5 agent files exist in `.claude/agents/` with correct naming (audit-scanner, audit-analyzer, audit-comparator, audit-consolidator, audit-validator)
- Each agent has valid frontmatter with appropriate model selection (haiku for scanner, sonnet for others)
- Tool restrictions enforce read-only for all agents except consolidator (which has Write)

**Exit Criteria:**
- All 5 Phase 4 tasks (T04.01–T04.05) marked completed
- No inconsistencies between agent prompts and rules files
- Agent tool restrictions match SKILL.md allowed-tools declarations

---

## Phase 5: Framework Integration

Register the new command in SuperClaude's framework files so it appears in routing tables, persona triggers, and command catalogs. Depends on Phases 1-4 being complete. All tasks are independent and can execute in parallel.

### T05.01 — Add COMMANDS.md Entry

**Roadmap Item ID(s):** R-031
**Why:** COMMANDS.md is the command catalog. The entry makes the command discoverable and documents its auto-persona and MCP configuration.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `EXEMPT`
**Confidence:** `[██████----] 55%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Skip verification
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0026
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0026/notes.md`

**Deliverables:**
- Entry in COMMANDS.md under "Quality Commands" section

**Steps:**
1. **[PLANNING]** Read existing COMMANDS.md to identify Quality Commands section and entry format
2. **[PLANNING]** Verify T01.02 complete (frontmatter defines auto-persona, MCP, tools)
3. **[EXECUTION]** Add entry matching existing format: command signature, description, Auto-Persona, MCP, Tools
4. **[VERIFICATION]** Verify entry follows existing format exactly; listed under correct category
5. **[COMPLETION]** Record entry content in notes artifact

**Acceptance Criteria:**
- Entry follows existing COMMANDS.md command entry format exactly
- Listed under "Quality Commands" category
- Auto-Persona, MCP, and Tools all specified correctly
- Entry is consistent with SKILL.md frontmatter declarations

**Validation:**
- Manual check: compare entry format to existing entries in COMMANDS.md
- Evidence: linkable artifact produced (COMMANDS.md entry content)

**Dependencies:** T01.02, T04.01, T04.02, T04.03, T04.04, T04.05
**Rollback:** Edit COMMANDS.md to remove entry (git recoverable)
**Notes:** EXEMPT tier due to documentation path (*.md) context booster (+0.5). Confidence below 0.70 due to ambiguity between EXEMPT and STANDARD.

---

### T05.02 — Add ORCHESTRATOR.md Routing Entry

**Roadmap Item ID(s):** R-032
**Why:** ORCHESTRATOR.md routing table determines how requests are matched to this command and what gets auto-activated.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `EXEMPT`
**Confidence:** `[██████----] 55%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Skip verification
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0027
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0027/notes.md`

**Deliverables:**
- Entry in ORCHESTRATOR.md Master Routing Table

**Steps:**
1. **[PLANNING]** Read existing ORCHESTRATOR.md to identify Master Routing Table format
2. **[PLANNING]** Verify SKILL.md complete with all persona and MCP declarations
3. **[EXECUTION]** Add routing entry: pattern ("cleanup audit" / "repo audit" / "dead code"), complexity (complex), auto-activates (personas + MCP), confidence (95%)
4. **[EXECUTION]** Add to Wave-Enabled Commands list if applicable
5. **[VERIFICATION]** Verify entry matches table format; confidence score is realistic
6. **[COMPLETION]** Record entry content in notes artifact

**Acceptance Criteria:**
- Routing entry matches Master Routing Table format exactly
- Confidence score is realistic (95%)
- Complexity correctly set to "complex"
- Wave-enabled status documented

**Validation:**
- Manual check: compare entry format to existing routing table entries
- Evidence: linkable artifact produced (ORCHESTRATOR.md entry content)

**Dependencies:** T01.02, T04.01, T04.02, T04.03, T04.04, T04.05
**Rollback:** Edit ORCHESTRATOR.md to remove entry (git recoverable)
**Notes:** EXEMPT tier due to documentation path context booster.

---

### T05.03 — Update PERSONAS.md Trigger Keywords

**Roadmap Item ID(s):** R-033
**Why:** New trigger keywords ensure the analyzer persona auto-activates for audit-related requests.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `EXEMPT`
**Confidence:** `[██████----] 55%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Skip verification
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0028
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0028/notes.md`

**Deliverables:**
- Updated analyzer persona triggers in PERSONAS.md

**Steps:**
1. **[PLANNING]** Read existing PERSONAS.md to identify analyzer persona trigger section
2. **[PLANNING]** Verify new keywords don't conflict with existing persona triggers
3. **[EXECUTION]** Add trigger keywords: "audit", "cleanup-audit", "dead code", "orphan files", "repo cleanup"
4. **[VERIFICATION]** Verify no conflicts with existing triggers; keywords are specific enough
5. **[COMPLETION]** Record updated triggers in notes artifact

**Acceptance Criteria:**
- New keywords added to analyzer persona trigger list
- No conflicts with existing persona triggers
- Keywords are specific enough to avoid false positives
- Keywords match the command's intended activation scenarios

**Validation:**
- Manual check: search PERSONAS.md for keyword conflicts
- Evidence: linkable artifact produced (updated trigger keywords)

**Dependencies:** T01.02
**Rollback:** Edit PERSONAS.md to remove keywords (git recoverable)
**Notes:** EXEMPT tier due to documentation path context booster.

---

### Checkpoint: End of Phase 5

**Purpose:** Verify all framework integration entries are in place and consistent with the skill definition.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P05-END.md`

**Verification:**
- COMMANDS.md has the cleanup-audit entry under Quality Commands
- ORCHESTRATOR.md has the routing entry in Master Routing Table
- PERSONAS.md has updated analyzer triggers with no conflicts

**Exit Criteria:**
- All 3 Phase 5 tasks (T05.01–T05.03) marked completed
- Framework entries are consistent with SKILL.md frontmatter
- No keyword conflicts detected in PERSONAS.md

---

## Phase 6: Validation & Testing

Validate the complete skill package works correctly by testing against real repositories at different scales. Depends on all previous phases being complete. Tests are mostly sequential (each pass test builds on the prior).

### T06.01 — Validate Skill Loading

**Roadmap Item ID(s):** R-034
**Why:** Verifies the skill is discoverable, frontmatter parses correctly, tool restrictions are enforced, and shell preprocessing executes.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0029
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0029/evidence.md`

**Deliverables:**
- Skill loading test results confirming discoverability, frontmatter parsing, tool restrictions, and preprocessing

**Steps:**
1. **[PLANNING]** Identify test criteria: skill discovery, frontmatter parsing, disable-model-invocation, allowed-tools, preprocessing
2. **[PLANNING]** Verify all Phase 1-5 tasks are complete
3. **[EXECUTION]** Verify `/sc:cleanup-audit` appears in command autocomplete
4. **[EXECUTION]** Verify frontmatter is parsed correctly (description displays, argument-hint shows)
5. **[EXECUTION]** Verify `disable-model-invocation: true` prevents auto-triggering
6. **[EXECUTION]** Verify `allowed-tools` restriction is enforced
7. **[VERIFICATION]** Confirm all 5 verification checks pass
8. **[COMPLETION]** Record test results in evidence artifact

**Acceptance Criteria:**
- Skill appears in `/` autocomplete with correct name and hint
- Description displays correctly matching frontmatter
- Tool restrictions are active (only allowed tools accessible)
- Shell preprocessing executes and injects repo metadata

**Validation:**
- Manual check: type `/sc:cleanup-audit` and verify autocomplete; check argument-hint displays
- Evidence: linkable artifact produced (test results with screenshots or output)

**Dependencies:** T05.01, T05.02, T05.03 (all framework integration complete)
**Rollback:** N/A (read-only test)
**Notes:** Confidence below 0.70 — no strong tier keywords matched. Test task classified as STANDARD.

---

### T06.02 — Test Pass 1 on Small Directory

**Roadmap Item ID(s):** R-035
**Why:** Validates end-to-end Pass 1 execution: subagent spawning, batch report generation, template compliance, and evidence quality.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0030
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0030/evidence.md`

**Deliverables:**
- Pass 1 test results: subagent spawn confirmation, batch report validation, coverage metrics, evidence quality check

**Steps:**
1. **[PLANNING]** Select a small directory (e.g., `tests/`) with 10-20 files for controlled testing
2. **[PLANNING]** Verify T06.01 passed (skill loads correctly)
3. **[EXECUTION]** Run `/sc:cleanup-audit tests/ --pass surface --batch-size 10`
4. **[EXECUTION]** Verify audit-scanner subagent spawned and completed
5. **[EXECUTION]** Verify batch report written to `.claude-audit/<session>/` and follows template
6. **[EXECUTION]** Verify every file in scope is classified (DELETE/REVIEW/KEEP) with 100% coverage
7. **[VERIFICATION]** Verify DELETE recommendations have grep evidence (pattern + count + zero-result)
8. **[COMPLETION]** Record test results with report excerpts in evidence artifact

**Acceptance Criteria:**
- audit-scanner subagent spawns and completes without error
- Batch report file exists at expected path with all required sections
- Report follows batch-report.md template (8 content sections)
- 100% file coverage within scope with DELETE findings having grep evidence

**Validation:**
- `/sc:cleanup-audit tests/ --pass surface --batch-size 10`
- Evidence: linkable artifact produced (batch report output + coverage metrics)

**Dependencies:** T06.01
**Rollback:** N/A (read-only test; delete audit output directory)
**Notes:** Confidence below 0.70. Risk Medium due to "audit" keyword.

---

### T06.03 — Test Pass 2 on Small Directory

**Roadmap Item ID(s):** R-036
**Why:** Validates Pass 2 execution: Sonnet agent spawning, mandatory 8-field profiles, file-type-specific rules, and scope limitation.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0031
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0031/evidence.md`

**Deliverables:**
- Pass 2 test results: Sonnet agent confirmation, 8-field profile validation, file-type rule application

**Steps:**
1. **[PLANNING]** Use same directory as T06.02 for consistency
2. **[PLANNING]** Verify T06.02 passed (Pass 1 results exist)
3. **[EXECUTION]** Run `/sc:cleanup-audit tests/ --pass structural --batch-size 10`
4. **[EXECUTION]** Verify audit-analyzer agent spawned (Sonnet model)
5. **[EXECUTION]** Verify per-file profiles have all 8 mandatory fields
6. **[EXECUTION]** Verify extra rules applied by file type (test files get test-specific checks)
7. **[VERIFICATION]** Verify scope limited to KEEP/REVIEW from Pass 1 (if prior results exist)
8. **[COMPLETION]** Record test results with profile excerpts in evidence artifact

**Acceptance Criteria:**
- audit-analyzer spawns with Sonnet model and completes
- All 8 mandatory profile fields present for every audited file
- File type-specific rules applied (test files checked for test runner discovery)
- Report follows batch-report.md and finding-profile.md templates

**Validation:**
- `/sc:cleanup-audit tests/ --pass structural --batch-size 10`
- Evidence: linkable artifact produced (per-file profile excerpts + field counts)

**Dependencies:** T06.02
**Rollback:** N/A (read-only test)
**Notes:** Confidence below 0.70. Risk Medium due to "audit" keyword.

---

### T06.04 — Test Pass 3 Cross-Cutting

**Roadmap Item ID(s):** R-037
**Why:** Validates Pass 3 execution: comparator agent, duplication matrix production, overlap quantification, and deduplication.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0032
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0032/evidence.md`

**Deliverables:**
- Pass 3 test results: comparator agent confirmation, duplication matrix, overlap percentages, deduplication check

**Steps:**
1. **[PLANNING]** Select scope with known duplication (e.g., repository root with infrastructure files)
2. **[PLANNING]** Verify T06.02 and T06.03 passed (prior pass results exist)
3. **[EXECUTION]** Run `/sc:cleanup-audit . --pass cross-cutting --focus infrastructure`
4. **[EXECUTION]** Verify audit-comparator agent spawned and completed
5. **[EXECUTION]** Verify duplication matrix produced with overlap percentages
6. **[EXECUTION]** Verify known-issues deduplication works (if prior pass findings exist)
7. **[VERIFICATION]** Verify CONSOLIDATE recommendations have both file paths and quantified overlap
8. **[COMPLETION]** Record test results with duplication matrix in evidence artifact

**Acceptance Criteria:**
- audit-comparator spawns and completes
- Duplication matrix present in output with numeric overlap percentages
- CONSOLIDATE recommendations have both file paths identified
- Known-issues from prior passes are not re-flagged

**Validation:**
- `/sc:cleanup-audit . --pass cross-cutting --focus infrastructure`
- Evidence: linkable artifact produced (duplication matrix + CONSOLIDATE examples)

**Dependencies:** T06.02, T06.03
**Rollback:** N/A (read-only test)
**Notes:** Confidence below 0.70. Risk Medium due to "audit" keyword.

---

### T06.05 — Test Quality Gate Enforcement

**Roadmap Item ID(s):** R-038
**Why:** Validates that the audit-validator spot-checks findings and quality gates block advancement on failure.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0033
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0033/evidence.md`

**Deliverables:**
- Quality gate test results: validator spawn confirmation, spot-check samples, discrepancy detection

**Steps:**
1. **[PLANNING]** Identify quality gate trigger points in audit flow
2. **[PLANNING]** Verify at least one pass test (T06.02-T06.04) produced output
3. **[EXECUTION]** Verify audit-validator spawned after pass completion
4. **[EXECUTION]** Verify spot-check samples selected (5 per 50 files)
5. **[EXECUTION]** Verify validation report identifies any discrepancies
6. **[VERIFICATION]** Verify quality gate blocks pass advancement on failure (if applicable)
7. **[COMPLETION]** Record quality gate test results in evidence artifact

**Acceptance Criteria:**
- audit-validator runs after each pass completes
- Validation report exists with spot-check results
- Discrepancies are clearly flagged with evidence
- Quality gate blocking behavior documented

**Validation:**
- Manual check: verify validator ran; inspect validation report for spot-check results
- Evidence: linkable artifact produced (validation report excerpts)

**Dependencies:** T06.02
**Rollback:** N/A (read-only test)
**Notes:** Confidence below 0.70. Risk Medium due to "audit" keyword.

---

### Checkpoint: Phase 6 / Tasks T06.01–T06.05

**Purpose:** Verify individual pass tests and quality gates before running the full 3-pass integration test.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P06-T01-T05.md`

**Verification:**
- Skill loads correctly (T06.01 passed)
- All 3 individual pass tests produced valid output (T06.02–T06.04)
- Quality gate enforcement validated (T06.05)

**Exit Criteria:**
- T06.01–T06.05 all marked completed
- No critical failures in individual pass tests
- Quality gate mechanism confirmed functional

---

### T06.06 — Test Full 3-Pass Audit

**Roadmap Item ID(s):** R-039
**Why:** Integration test validating the complete audit workflow: all 3 passes in order, quality gates between passes, final consolidated report.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** audit (+2)
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: Sequential | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0034
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0034/evidence.md`

**Deliverables:**
- Full 3-pass audit test results: pass ordering, quality gates, final report, incremental saves, progress tracking

**Steps:**
1. **[PLANNING]** Select appropriate scope (medium directory, 25-50 files)
2. **[PLANNING]** Verify T06.02–T06.05 all passed
3. **[EXECUTION]** Run `/sc:cleanup-audit . --pass all --batch-size 25`
4. **[EXECUTION]** Verify all 3 passes execute in order (Pass 1 → Pass 2 → Pass 3)
5. **[EXECUTION]** Verify quality gates run between passes; final consolidated report produced
6. **[EXECUTION]** Verify incremental saves occurred (batch files on disk) and progress.json created
7. **[VERIFICATION]** Verify executive summary has action counts and coverage %; all report sections present
8. **[COMPLETION]** Record full test results in evidence artifact

**Acceptance Criteria:**
- All 3 passes complete in correct order (1 → 2 → 3)
- Quality gates ran between passes (validator spawned)
- Final report exists with executive summary (4 required metrics)
- Batch report files exist on disk (incremental saves worked) and progress.json tracks completion

**Validation:**
- `/sc:cleanup-audit . --pass all --batch-size 25`
- Evidence: linkable artifact produced (final report + batch file listing + progress.json content)

**Dependencies:** T06.02, T06.03, T06.04, T06.05
**Rollback:** Delete audit output directory
**Notes:** Confidence below 0.70. Risk Medium due to "audit" keyword. This is the primary integration test.

---

### T06.07 — Test Resume-from-Checkpoint

**Roadmap Item ID(s):** R-040
**Why:** Validates crash safety: progress.json detection, completed batch skipping, and resume from last incomplete batch.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** Preferred: None | Fallback Allowed: Yes
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0035
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0035/evidence.md`

**Deliverables:**
- Resume test results: state detection, batch skip confirmation, audit continuation from interruption point

**Steps:**
1. **[PLANNING]** Design test: start multi-batch audit, interrupt after some batches, re-invoke
2. **[PLANNING]** Verify T06.06 passed (full audit produces progress.json)
3. **[EXECUTION]** Start a multi-batch audit and allow some batches to complete
4. **[EXECUTION]** Interrupt the session (or simulate interruption)
5. **[EXECUTION]** Re-invoke the same command; verify progress.json detected
6. **[VERIFICATION]** Verify completed batches are skipped; audit resumes from last incomplete batch
7. **[COMPLETION]** Record resume test results in evidence artifact

**Acceptance Criteria:**
- Previous progress state detected on re-invocation (progress.json found)
- Completed batches not re-processed (skip confirmed)
- Audit continues from interruption point without data loss
- Resume behavior documented with before/after evidence

**Validation:**
- Manual check: compare batch file timestamps; verify no duplicate processing
- Evidence: linkable artifact produced (progress.json content + resume log)

**Dependencies:** T06.06
**Rollback:** N/A (read-only test)
**Notes:** Confidence below 0.70. This tests a P2-Medium priority feature.

---

### T06.08 — Write Validation Report

**Roadmap Item ID(s):** R-041
**Why:** Documents all test results, issues, resolutions, and overall validation score for the release.
**Effort:** `M`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `EXEMPT`
**Confidence:** `[██████----] 55%`
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Skip verification
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0036
**Artifacts (Intended Paths):**
- `.roadmaps/v1.06/artifacts/D-0036/spec.md`

**Deliverables:**
- Validation report at `.dev/.releases/current/v.1.06-CleanupAudit/validation-report.md` with all test results and overall score

**Steps:**
1. **[PLANNING]** Gather results from all test tasks (T06.01–T06.07)
2. **[PLANNING]** Identify pass/fail status for each acceptance criterion across all tests
3. **[EXECUTION]** Document results per test task with pass/fail status
4. **[EXECUTION]** Document any issues found and their resolutions
5. **[EXECUTION]** Calculate overall validation score (% of acceptance criteria passed)
6. **[EXECUTION]** Record coverage metrics and performance observations
7. **[VERIFICATION]** Verify all test results are documented; no test omitted
8. **[COMPLETION]** Write final validation report to release directory

**Acceptance Criteria:**
- All test results (T06.01–T06.07) documented with pass/fail per criterion
- Issues and resolutions recorded with evidence references
- Overall validation score calculated as percentage of criteria passed
- Performance observations noted (execution time, token usage, agent spawn counts)

**Validation:**
- Manual check: verify all 7 test tasks have documented results
- Evidence: linkable artifact produced (validation-report.md)

**Dependencies:** T06.01, T06.02, T06.03, T06.04, T06.05, T06.06, T06.07
**Rollback:** Delete validation report file (git recoverable)
**Notes:** EXEMPT tier due to documentation path (*.md) context booster. This is a pure documentation task.

---

### Checkpoint: End of Phase 6

**Purpose:** Verify all validation tests complete and the validation report is comprehensive.
**Checkpoint Report Path:** `.roadmaps/v1.06/checkpoints/CP-P06-END.md`

**Verification:**
- All 8 Phase 6 tasks (T06.01–T06.08) marked completed
- Validation report exists with all test results documented
- Overall validation score meets minimum acceptance threshold

**Exit Criteria:**
- All test tasks have pass/fail results
- No critical failures remaining unresolved
- Validation report is comprehensive and ready for stakeholder review

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | — | — | — | — | (project context, no task) |
| R-002 | — | — | — | — | (project context, no task) |
| R-003 | — | — | — | — | (dependency graph, no task) |
| R-004 | — | — | — | — | (risk register, no task) |
| R-005 | — | — | — | — | (success criteria, no task) |
| R-006 | T01.01 | D-0001 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0001/evidence.md` |
| R-007 | T01.02 | D-0002 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0002/spec.md` |
| R-008 | T01.03 | D-0003 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0003/spec.md` |
| R-009 | T01.04 | D-0004 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0004/spec.md` |
| R-010 | T01.05 | D-0005 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0005/spec.md` |
| R-011 | T01.06 | D-0006 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0006/spec.md` |
| R-012 | T01.07 | D-0007 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0007/spec.md` |
| R-013 | T01.08 | D-0008 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0008/spec.md` |
| R-014 | T01.09 | D-0009 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0009/spec.md` |
| R-015 | T01.10 | D-0010 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0010/spec.md` |
| R-016 | T01.11 | D-0011 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0011/evidence.md` |
| R-017 | T02.01 | D-0012 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0012/spec.md` |
| R-018 | T02.02 | D-0013 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0013/spec.md` |
| R-019 | T02.03 | D-0014 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0014/spec.md` |
| R-020 | T02.04 | D-0015 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0015/spec.md` |
| R-021 | T02.05 | D-0016 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0016/spec.md` |
| R-022 | T03.01 | D-0017 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0017/spec.md` |
| R-023 | T03.02 | D-0018 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0018/spec.md` |
| R-024 | T03.03 | D-0019 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0019/spec.md` |
| R-025 | T03.04 | D-0020 | STANDARD | 60% | `.roadmaps/v1.06/artifacts/D-0020/spec.md` |
| R-026 | T04.01 | D-0021 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0021/spec.md` |
| R-027 | T04.02 | D-0022 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0022/spec.md` |
| R-028 | T04.03 | D-0023 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0023/spec.md` |
| R-029 | T04.04 | D-0024 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0024/spec.md` |
| R-030 | T04.05 | D-0025 | STRICT | 80% | `.roadmaps/v1.06/artifacts/D-0025/spec.md` |
| R-031 | T05.01 | D-0026 | EXEMPT | 55% | `.roadmaps/v1.06/artifacts/D-0026/notes.md` |
| R-032 | T05.02 | D-0027 | EXEMPT | 55% | `.roadmaps/v1.06/artifacts/D-0027/notes.md` |
| R-033 | T05.03 | D-0028 | EXEMPT | 55% | `.roadmaps/v1.06/artifacts/D-0028/notes.md` |
| R-034 | T06.01 | D-0029 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0029/evidence.md` |
| R-035 | T06.02 | D-0030 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0030/evidence.md` |
| R-036 | T06.03 | D-0031 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0031/evidence.md` |
| R-037 | T06.04 | D-0032 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0032/evidence.md` |
| R-038 | T06.05 | D-0033 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0033/evidence.md` |
| R-039 | T06.06 | D-0034 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0034/evidence.md` |
| R-040 | T06.07 | D-0035 | STANDARD | 40% | `.roadmaps/v1.06/artifacts/D-0035/evidence.md` |
| R-041 | T06.08 | D-0036 | EXEMPT | 55% | `.roadmaps/v1.06/artifacts/D-0036/spec.md` |

---

## Execution Log Template

**Intended Path:** `.roadmaps/v1.06/execution-log.md`

This is a template to be filled during execution (do not fabricate entries).

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | T01.01 | STANDARD | D-0001 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.01/` |
| | T01.02 | STRICT | D-0002 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.02/` |
| | T01.03 | STANDARD | D-0003 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.03/` |
| | T01.04 | STANDARD | D-0004 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.04/` |
| | T01.05 | STANDARD | D-0005 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.05/` |
| | T01.06 | STANDARD | D-0006 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.06/` |
| | T01.07 | STANDARD | D-0007 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.07/` |
| | T01.08 | STANDARD | D-0008 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.08/` |
| | T01.09 | STANDARD | D-0009 | | Manual | TBD | `.roadmaps/v1.06/evidence/T01.09/` |
| | T01.10 | STANDARD | D-0010 | | `chmod +x repo-inventory.sh && ./repo-inventory.sh . 50` | TBD | `.roadmaps/v1.06/evidence/T01.10/` |
| | T01.11 | STANDARD | D-0011 | | `wc -l .claude/skills/sc-cleanup-audit/SKILL.md` | TBD | `.roadmaps/v1.06/evidence/T01.11/` |
| | T02.01 | STANDARD | D-0012 | | Manual | TBD | `.roadmaps/v1.06/evidence/T02.01/` |
| | T02.02 | STANDARD | D-0013 | | Manual | TBD | `.roadmaps/v1.06/evidence/T02.02/` |
| | T02.03 | STANDARD | D-0014 | | Manual | TBD | `.roadmaps/v1.06/evidence/T02.03/` |
| | T02.04 | STANDARD | D-0015 | | Manual | TBD | `.roadmaps/v1.06/evidence/T02.04/` |
| | T02.05 | STANDARD | D-0016 | | Manual | TBD | `.roadmaps/v1.06/evidence/T02.05/` |
| | T03.01 | STANDARD | D-0017 | | Manual | TBD | `.roadmaps/v1.06/evidence/T03.01/` |
| | T03.02 | STANDARD | D-0018 | | Manual | TBD | `.roadmaps/v1.06/evidence/T03.02/` |
| | T03.03 | STANDARD | D-0019 | | Manual | TBD | `.roadmaps/v1.06/evidence/T03.03/` |
| | T03.04 | STANDARD | D-0020 | | Manual | TBD | `.roadmaps/v1.06/evidence/T03.04/` |
| | T04.01 | STRICT | D-0021 | | Manual | TBD | `.roadmaps/v1.06/evidence/T04.01/` |
| | T04.02 | STRICT | D-0022 | | Manual | TBD | `.roadmaps/v1.06/evidence/T04.02/` |
| | T04.03 | STRICT | D-0023 | | Manual | TBD | `.roadmaps/v1.06/evidence/T04.03/` |
| | T04.04 | STRICT | D-0024 | | Manual | TBD | `.roadmaps/v1.06/evidence/T04.04/` |
| | T04.05 | STRICT | D-0025 | | Manual | TBD | `.roadmaps/v1.06/evidence/T04.05/` |
| | T05.01 | EXEMPT | D-0026 | | Manual | TBD | `.roadmaps/v1.06/evidence/T05.01/` |
| | T05.02 | EXEMPT | D-0027 | | Manual | TBD | `.roadmaps/v1.06/evidence/T05.02/` |
| | T05.03 | EXEMPT | D-0028 | | Manual | TBD | `.roadmaps/v1.06/evidence/T05.03/` |
| | T06.01 | STANDARD | D-0029 | | Manual | TBD | `.roadmaps/v1.06/evidence/T06.01/` |
| | T06.02 | STANDARD | D-0030 | | `/sc:cleanup-audit tests/ --pass surface --batch-size 10` | TBD | `.roadmaps/v1.06/evidence/T06.02/` |
| | T06.03 | STANDARD | D-0031 | | `/sc:cleanup-audit tests/ --pass structural --batch-size 10` | TBD | `.roadmaps/v1.06/evidence/T06.03/` |
| | T06.04 | STANDARD | D-0032 | | `/sc:cleanup-audit . --pass cross-cutting --focus infrastructure` | TBD | `.roadmaps/v1.06/evidence/T06.04/` |
| | T06.05 | STANDARD | D-0033 | | Manual | TBD | `.roadmaps/v1.06/evidence/T06.05/` |
| | T06.06 | STANDARD | D-0034 | | `/sc:cleanup-audit . --pass all --batch-size 25` | TBD | `.roadmaps/v1.06/evidence/T06.06/` |
| | T06.07 | STANDARD | D-0035 | | Manual | TBD | `.roadmaps/v1.06/evidence/T06.07/` |
| | T06.08 | EXEMPT | D-0036 | | Manual | TBD | `.roadmaps/v1.06/evidence/T06.08/` |

---

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template (do not fabricate contents).

**Template:**

```markdown
# Checkpoint Report — <Checkpoint Title>

**Checkpoint Report Path:** .roadmaps/v1.06/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>

## Status
Overall: Pass | Fail | TBD

## Verification Results
- <Verification bullet 1 result>
- <Verification bullet 2 result>
- <Verification bullet 3 result>

## Exit Criteria Assessment
- <Exit criterion 1 result>
- <Exit criterion 2 result>
- <Exit criterion 3 result>

## Issues & Follow-ups
- <List blocking issues; reference T<PP>.<TT> and D-####>

## Evidence
- .roadmaps/v1.06/evidence/<relevant-paths>
```

### Checkpoint Reports Required

| Checkpoint | Deterministic Name | Tasks Covered |
|---|---|---|
| Phase 1 / Tasks T01.01–T01.05 | `CP-P01-T01-T05.md` | T01.01–T01.05 |
| Phase 1 / Tasks T01.06–T01.10 | `CP-P01-T06-T10.md` | T01.06–T01.10 |
| End of Phase 1 | `CP-P01-END.md` | T01.01–T01.11 |
| End of Phase 2 | `CP-P02-END.md` | T02.01–T02.05 |
| End of Phase 3 | `CP-P03-END.md` | T03.01–T03.04 |
| End of Phase 4 | `CP-P04-END.md` | T04.01–T04.05 |
| End of Phase 5 | `CP-P05-END.md` | T05.01–T05.03 |
| Phase 6 / Tasks T06.01–T06.05 | `CP-P06-T01-T05.md` | T06.01–T06.05 |
| End of Phase 6 | `CP-P06-END.md` | T06.01–T06.08 |

---

## Feedback Collection Template

Track tier classification accuracy and execution quality for calibration learning.

**Intended Path:** `.roadmaps/v1.06/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | STANDARD | | | | | |
| T01.02 | STRICT | | | | | |
| T01.03 | STANDARD | | | | | |
| T01.04 | STANDARD | | | | | |
| T01.05 | STANDARD | | | | | |
| T01.06 | STANDARD | | | | | |
| T01.07 | STANDARD | | | | | |
| T01.08 | STANDARD | | | | | |
| T01.09 | STANDARD | | | | | |
| T01.10 | STANDARD | | | | | |
| T01.11 | STANDARD | | | | | |
| T02.01 | STANDARD | | | | | |
| T02.02 | STANDARD | | | | | |
| T02.03 | STANDARD | | | | | |
| T02.04 | STANDARD | | | | | |
| T02.05 | STANDARD | | | | | |
| T03.01 | STANDARD | | | | | |
| T03.02 | STANDARD | | | | | |
| T03.03 | STANDARD | | | | | |
| T03.04 | STANDARD | | | | | |
| T04.01 | STRICT | | | | | |
| T04.02 | STRICT | | | | | |
| T04.03 | STRICT | | | | | |
| T04.04 | STRICT | | | | | |
| T04.05 | STRICT | | | | | |
| T05.01 | EXEMPT | | | | | |
| T05.02 | EXEMPT | | | | | |
| T05.03 | EXEMPT | | | | | |
| T06.01 | STANDARD | | | | | |
| T06.02 | STANDARD | | | | | |
| T06.03 | STANDARD | | | | | |
| T06.04 | STANDARD | | | | | |
| T06.05 | STANDARD | | | | | |
| T06.06 | STANDARD | | | | | |
| T06.07 | STANDARD | | | | | |
| T06.08 | EXEMPT | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`
