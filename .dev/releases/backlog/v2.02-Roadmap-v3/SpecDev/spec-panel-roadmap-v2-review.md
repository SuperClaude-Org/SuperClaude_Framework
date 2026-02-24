# Spec Panel Review: sc:roadmap Adversarial Pipeline Sprint Specification
## v2.01-Roadmap-v3 Amendments Based on Adversarial Debate Outcomes

**Document purpose**: Precise, implementer-ready edits and additions to `sprint-spec.md` derived from escalation decisions and valuable amendments identified in `deferral-confidence-matrix.md`.

**Source files**:
- Sprint spec: `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md`
- Confidence matrix: `docs/generated/deferral-confidence-matrix.md`

**Review date**: 2026-02-23

---

## Panel Composition

| Expert | Role in This Review |
|--------|---------------------|
| **Karl Wiegers** (Requirements Engineering) | Escalation 1 (scope boundary verification), Amendment E (DoD precision) |
| **Gojko Adzic** (Specification by Example) | Escalations 2 & 3 (acceptance criteria for quality gate Task 3.5) |
| **Alistair Cockburn** (Use Cases, Simplicity) | Amendment A (scope clarification note, preventing over-generalization) |
| **Martin Fowler** (Refactoring, Architecture) | Amendment B (risk register — dependency linkage between deferred items) |
| **Michael Nygard** (Release It!, Stability Patterns) | Escalations 2 & 3 (fault tolerance gap, quality gate necessity) |
| **Sam Newman** (Microservices, Contracts) | Amendment D (agents/README.md incorrect path — developer experience hazard) |
| **Lisa Crispin** (Agile Testing) | Amendment C (process deliverable — debt register initialization), Amendment E (DoD additions) |

---

## Priority Ordering of Changes

Apply changes in this order to avoid forward references and minimize re-reading:

1. **Change 1** — Escalation 1: Amend Task 3.1 scope (append dead code removal)
2. **Change 2** — Amendment D: Add Maintenance Errata section (standalone, no dependencies)
3. **Change 3** — Amendment A: Add Epic 3 scope clarification note
4. **Change 4** — Escalation 2 & 3: Add new Task 3.5 to Epic 3 task table
5. **Change 5** — Amendment B: Add R8 to Risk Register
6. **Change 6** — Amendment C: Add Sprint 0 Process Deliverable section
7. **Change 7** — Amendment E: Add DoD checklist items for Task 3.5 and Task 3.1 amendment

---

## Change 1 — Escalation 1: Amend Task 3.1 to Include Dead Code Removal

**Panel expert**: Karl Wiegers (scope boundary verification)

**Rationale**: The `subagent_type: "general-purpose"` field is not a valid Task tool parameter. The Task tool API has no `subagent_type` parameter; confirmation via grep shows the field appears at lines 802 and 1411 of `src/superclaude/skills/sc-adversarial/SKILL.md`. This is provably dead metadata with zero coordination overhead — Task 3.1 already modifies this file. Keeping the dead field post-sprint creates developer debugging tax and a copy-risk vector where other skill authors may infer it is functional. Scope boundary rule: when a cleanup item can be absorbed by an in-flight task with no coordination cost, it belongs in that task, not in a follow-up sprint. The confidence matrix scored this deferral at 0.38, the lowest score in the matrix (well into "deferral strongly unjustified" band).

**Location**: Epic 3 task table, Task 3.1 row, "Change" column and "Acceptance Criteria" column.

### BEFORE (Task 3.1 Change column, exact text):

```
Add a "Return Contract (MANDATORY)" section as the final pipeline step. Instruction: "As the absolute final step, write `<output-dir>/adversarial/return-contract.yaml` with the following fields." Define 9 fields: `schema_version: "1.0"`, `status` (success/partial/failed), `convergence_score` (0.0-1.0), `merged_output_path` (path or null), `artifacts_dir` (path), `unresolved_conflicts` (integer or null), `base_variant` (string or null), `failure_stage` (null on success, pipeline step name on failure), `fallback_mode` (boolean, default: false — set to true when pipeline was executed via inline Task agents instead of the full sc:adversarial skill). Use YAML null (`~`) instead of sentinel values (-1, "") for fields not reached during failed runs. Instruction: write even on failure with `status: failed`. **Type note**: `unresolved_conflicts` is typed as `integer` (count of conflicts). The existing sc:adversarial SKILL.md line 349 types it as `list[string]` — resolve to `integer` for simplicity, since neither consumer uses the list contents. | Section exists as final pipeline step; 9 fields defined; null is used for unreached values (not -1 or ""); write-on-failure instruction is explicit; `fallback_mode` field present; example YAML block is provided
```

### AFTER (Task 3.1 Change column, full replacement):

```
Add a "Return Contract (MANDATORY)" section as the final pipeline step. Instruction: "As the absolute final step, write `<output-dir>/adversarial/return-contract.yaml` with the following fields." Define 9 fields: `schema_version: "1.0"`, `status` (success/partial/failed), `convergence_score` (0.0-1.0), `merged_output_path` (path or null), `artifacts_dir` (path), `unresolved_conflicts` (integer or null), `base_variant` (string or null), `failure_stage` (null on success, pipeline step name on failure), `fallback_mode` (boolean, default: false — set to true when pipeline was executed via inline Task agents instead of the full sc:adversarial skill). Use YAML null (`~`) instead of sentinel values (-1, "") for fields not reached during failed runs. Instruction: write even on failure with `status: failed`. **Type note**: `unresolved_conflicts` is typed as `integer` (count of conflicts). The existing sc:adversarial SKILL.md line 349 types it as `list[string]` — resolve to `integer` for simplicity, since neither consumer uses the list contents. **Dead code removal (appended scope)**: In the same editing session, delete the two `subagent_type: "general-purpose"` lines from the `task_dispatch_config` YAML blocks in this file (located at lines 802 and 1411 in the current file). The `subagent_type` field is not a valid Task tool parameter; it is dead metadata. Remove the entire `subagent_type: "general-purpose"` line from each block; do not replace it with any other value.
```

### BEFORE (Task 3.1 Acceptance Criteria column, exact text):

```
Section exists as final pipeline step; 9 fields defined; null is used for unreached values (not -1 or ""); write-on-failure instruction is explicit; `fallback_mode` field present; example YAML block is provided
```

### AFTER (Task 3.1 Acceptance Criteria column, full replacement):

```
Section exists as final pipeline step; 9 fields defined; null is used for unreached values (not -1 or ""); write-on-failure instruction is explicit; `fallback_mode` field present; example YAML block is provided; zero `subagent_type` lines remain in the file (confirm via: `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0)
```

---

## Change 2 — Amendment D: Add Maintenance Errata Section

**Panel expert**: Sam Newman (developer experience hazard)

**Rationale**: The `agents/README.md` file at `src/superclaude/agents/README.md` contains a factually incorrect path reference: it instructs developers to edit files in `plugins/superclaude/agents/` — a directory that does not exist in the current architecture. This creates the exact sync-divergence failure the project's `make verify-sync` workflow is designed to prevent. The correct source of truth is `src/superclaude/agents/`. This is a developer-facing hazard independent of Epic 3 scope and independent of S03 sequencing. It requires no coordination with any sprint task and costs under 15 minutes to fix. Recording it in the sprint spec ensures it is not lost; it should be fixed in the same implementation session as any other task.

**Location**: Insert a new top-level section after the "Future Work: Deterministic Verification Layer (DVL)" section and before "Definition of Done."

### BEFORE (no section exists — this is a pure addition):

_(The section does not exist. Insert between "Future Work: Deterministic Verification Layer (DVL)" section and "Definition of Done" section.)_

### AFTER (new section — insert in full):

```markdown
---

## Maintenance Errata: agents/README.md Incorrect Path Reference

**File**: `src/superclaude/agents/README.md`

**Issue**: The README contains an incorrect path instruction:

> "These agents are copies from `plugins/superclaude/agents/` for package distribution."
> "When updating agents: 1. Edit files in `plugins/superclaude/agents/`"

The directory `plugins/superclaude/agents/` does not exist in the current architecture. The correct source-of-truth directory is `src/superclaude/agents/`. This instruction will cause any developer following it to edit non-existent files, silently diverging from the actual source, which is exactly the sync divergence `make verify-sync` is designed to prevent.

**Fix**: Replace the README content with accurate path instructions. This is a standalone fix independent of all sprint epics and S03 sequencing. Recommend fixing in the same implementation session as any sprint task.

**Proposed replacement content for `src/superclaude/agents/README.md`**:

```markdown
# SuperClaude Agents

This directory contains agent definition files for specialized AI agents.
`src/superclaude/agents/` is the canonical source of truth for all agent definitions.

## Available Agents

(List agents as they exist in this directory)

## Important

When updating agents:
1. Edit files in `src/superclaude/agents/` (this directory — source of truth)
2. Run `make sync-dev` to copy changes to `.claude/agents/`
3. Run `make verify-sync` to confirm both locations are in sync

Note: The `plugins/` directory structure referenced in older documentation no longer
exists in the current architecture. All agent source files live in `src/superclaude/agents/`.
```

**Acceptance criteria**: `grep -r "plugins/superclaude/agents" src/superclaude/agents/README.md` returns 0 matches.

**Effort estimate**: < 15 minutes. No sprint coordination required.
```

---

## Change 3 — Amendment A: Add Epic 3 Scope Clarification Note

**Panel expert**: Alistair Cockburn (preventing over-generalization from a single example)

**Rationale**: Epic 3 establishes the first skill-to-skill return contract in the SuperClaude framework. Without an explicit "not prescriptive" note, the path convention (`adversarial/` subdirectory), the 9-field schema, and sc:adversarial-specific fields (`convergence_score`, `base_variant`, `fallback_mode`) are at risk of being treated as the mandatory framework standard when other skill authors look for examples. This is the de facto standard copy-risk identified in confidence matrix Item 14. Two sentences of clarification prevents a governance problem that would otherwise require a breaking schema change to correct. The fix belongs in the Epic 3 header — the exact point where an implementer reading the spec would form an impression of the contract's intended scope.

**Location**: Epic 3 header section, immediately after the "Dependency" line.

### BEFORE (exact text):

```
## Epic 3: Return Contract Transport Mechanism (RC4 + S04)

**Goal**: Establish a file-based return-contract.yaml convention so sc:adversarial can reliably transport structured pipeline results back to sc:roadmap.

**Dependency**: Conceptually independent (can be implemented in parallel with Epic 2), but must be tested after Epic 1 is complete.
```

### AFTER (full replacement):

```
## Epic 3: Return Contract Transport Mechanism (RC4 + S04)

**Goal**: Establish a file-based return-contract.yaml convention so sc:adversarial can reliably transport structured pipeline results back to sc:roadmap.

**Dependency**: Conceptually independent (can be implemented in parallel with Epic 2), but must be tested after Epic 1 is complete.

**Scope note**: This return contract is specific to the sc:roadmap → sc:adversarial skill pair. The 9-field schema, the `adversarial/` subdirectory path convention, and sc:adversarial-specific fields (`convergence_score`, `base_variant`, `fallback_mode`) are NOT prescriptive for other skill pairs. Other skills implementing skill-to-skill return contracts should design their own schemas based on their specific data needs; they should not copy sc:adversarial's fields as mandatory framework requirements.
```

---

## Change 4 — Escalations 2 & 3: Add New Task 3.5 to Epic 3

**Panel experts**: Gojko Adzic (acceptance criteria specification), Michael Nygard (fault tolerance gap)

**Rationale**: The two-tier quality gate deferral (Items 2 and 3 in the confidence matrix, scores 0.57 and 0.48) was an over-bundling classification error. Probe-and-branch (Item 2) correctly waits for Task 0.0 results. But the Tier 1 quality gate — artifact existence checks — is a purely additive ~50-line addition to `adversarial-integration.md` that uses path variables already defined by Task 1.4. More critically, it is the ONLY validation mechanism that catches the original failure mode (adversarial requested, nothing produced) in timeout and context-exhaustion scenarios where `return-contract.yaml` itself may never be written. The missing-file guard in Task 3.2 treats an absent return contract as `status: partial` with `convergence_score: 0.0` and proceeds — silently reproducing the original failure under new conditions. The confidence matrix's "AGAINST" argument won on Tier 1 in both debates. Adding Tier 1 as Task 3.5 has zero coordination hazard (additive only to a file Task 3.4 already modifies) and directly implements the spec panel's Priority 1 recommendation.

**Location**: Epic 3 task table, append new row after Task 3.4 (and after the struck-through 3.5 sync row, which becomes 3.6).

### BEFORE (exact text — the final two rows of the Epic 3 task table):

```
| 3.4 | Add canonical schema cross-reference to consumer | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Add a comment in the return contract consumption section: `# Canonical schema definition: src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section` | Cross-reference comment present |
| ~~3.5~~ | ~~Sync~~ | *Consolidated into post-edit step (see Implementer's Quick Reference)* | `make sync-dev && make verify-sync` after all epics complete | — |
```

### AFTER (full replacement of those two rows):

```
| 3.4 | Add canonical schema cross-reference to consumer | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Add a comment in the return contract consumption section: `# Canonical schema definition: src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section` | Cross-reference comment present |
| 3.5 | Add Tier 1 artifact existence quality gate | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Append a new "Post-Adversarial Artifact Existence Gate (Tier 1)" section to adversarial-integration.md. This gate runs BEFORE reading return-contract.yaml, providing validation in timeout/context-exhaustion scenarios where the return contract may never be written. The gate checks four artifact existence conditions using path variables defined by Task 1.4's `<output-dir>/adversarial/` convention: (1) **Directory existence**: `<output-dir>/adversarial/` directory exists. If absent: treat as `status: failed`, `failure_stage: "pipeline_not_started"`, abort with error "Adversarial pipeline directory not created — pipeline did not start." (2) **diff-analysis.md existence**: `<output-dir>/adversarial/diff-analysis.md` exists. If absent: treat as `status: failed`, `failure_stage: "diff_analysis"`, abort with error "diff-analysis.md not found — pipeline halted before diff analysis." (3) **merged-output.md existence**: `<output-dir>/adversarial/merged-output.md` exists. If absent: treat as `status: partial`, `convergence_score: 0.0`, warn user "merged-output.md not found — pipeline did not complete merge phase." (4) **return-contract.yaml existence**: `<output-dir>/adversarial/return-contract.yaml` exists. If absent: treat as `status: partial`, `convergence_score: 0.0`, apply missing-file guard from Task 3.2. Gate ordering instruction: "Perform these four checks in sequence before attempting to parse return-contract.yaml contents. If any check fails, apply the specified treatment without proceeding to YAML parsing." Use path variables (not hardcoded literals) to reference all artifact paths, so the gate remains valid if path conventions change. | Tier 1 gate section exists in adversarial-integration.md; four existence checks present in specified order; each check has defined failure treatment; gate is positioned before YAML parsing in the Return Contract Consumption section; path variable references used throughout (not hardcoded literals); gate heading is "Post-Adversarial Artifact Existence Gate (Tier 1)" |
| ~~3.6~~ | ~~Sync~~ | *Consolidated into post-edit step (see Implementer's Quick Reference)* | `make sync-dev && make verify-sync` after all epics complete | — |
```

**Note to implementer**: The struck-through sync row was previously numbered 3.5. Renumber it to 3.6 in the final document to make room for the new Task 3.5 above.

---

## Change 5 — Amendment B: Add R8 to Risk Register

**Panel expert**: Martin Fowler (dependency mapping between deferred architectural items)

**Rationale**: The confidence matrix debate on Item 17 (concurrency namespacing for parallel sc:adversarial invocations) identified a critical dependency linkage: Item 17 is currently a low-risk edge case because callers control the `--output-dir` parameter, providing implicit namespacing. However, if Item 14 (Framework-level Skill Return Protocol) is adopted in a future sprint, the output-dir path becomes implicit and caller-controlled namespacing is eliminated — transforming Item 17 from a low-risk edge case into a required co-feature that must ship in the same sprint as Item 14. The Risk Register is the correct place to record this because it is not a current-sprint concern but a future sprint planning constraint. Failing to record it now risks a future sprint adopting Item 14 without realizing Item 17 becomes mandatory, producing a race condition vulnerability in multi-invocation scenarios.

**Location**: Risk Register table, append new row after R7.

### BEFORE (exact text — final row of Risk Register):

```
| R7 | adversarial-integration.md pseudo-CLI syntax remains in unconverted sections | Debate 02, Unresolved Concern UC-02-03 | LOW (0.15) | LOW -- residual ambiguity in ref file | Full audit of adversarial-integration.md for `sc:adversarial --` patterns. Implemented in Epic 2, Task 2.4. |
```

### AFTER (full replacement of that row plus new R8 row):

```
| R7 | adversarial-integration.md pseudo-CLI syntax remains in unconverted sections | Debate 02, Unresolved Concern UC-02-03 | LOW (0.15) | LOW -- residual ambiguity in ref file | Full audit of adversarial-integration.md for `sc:adversarial --` patterns. Implemented in Epic 2, Task 2.4. |
| R8 | Concurrency namespacing becomes mandatory if Item 14 (Framework-level Skill Return Protocol) is adopted | Confidence matrix Item 17, dependency linkage finding | CONDITIONAL — LOW now, HIGH if Item 14 adopted | HIGH -- race condition: multiple simultaneous sc:adversarial invocations write to same return-contract.yaml path if output-dir is implicit | Current sprint's caller-controlled `--output-dir` parameter provides implicit namespacing and keeps this risk LOW. If Item 14 (Framework-level Skill Return Protocol) is adopted in a future sprint, the output-dir path becomes framework-managed rather than caller-controlled, eliminating the namespacing mitigation. **Constraint**: Item 17 (concurrency namespacing for parallel sc:adversarial invocations) MUST be resolved in the same sprint as Item 14. These items cannot be sequenced independently once Item 14 is adopted. Flag this dependency in the v2.1 sprint planning session when Item 14 is evaluated. |
```

---

## Change 6 — Amendment C: Add Sprint 0 Process Deliverable Section

**Panel expert**: Lisa Crispin (process integrity, debt tracking across sprints)

**Rationale**: The confidence matrix is the first application of a structured deferral-scoring methodology in this project. It contains 18 scored items with documented rationale, recalibrated likelihood estimates (e.g., RC3 from 0.95 to 0.70), and cross-item dependency findings. Without formalization, this information exists only as a point-in-time artifact with no persistence convention, no designated storage location, and no obligation for future sprints to reference it. The confidence matrix debate on Item 18 scored the deferral at 0.55 — "justified with minor concerns" — precisely because of this risk. The v2.1 sprint team rediscovering 18 deferred items from scratch costs 2-4 hours and loses the calibration decisions made during this sprint's debates. The recommended fix is a one-time 30-minute documentation task: before v2.1 implementation begins, initialize `debt-register.md` using this matrix as source.

**Location**: Insert a new top-level section after the "Implementation Order" section and before the "Risk Register" section.

### BEFORE (no section exists — this is a pure addition):

_(Insert between the end of "Implementation Order" and the "Risk Register" heading.)_

### AFTER (new section — insert in full):

```markdown
---

## Sprint 0 Process Deliverable: Formal Debt Register Initialization

**Trigger**: Before v2.1 implementation begins (not during this sprint's implementation phase).

**Deliverable**: Create `.dev/releases/debt-register.md` as the persistent technical debt and deferral tracking document for the SuperClaude framework.

**Source**: Use `docs/generated/deferral-confidence-matrix.md` as the primary source. The confidence matrix is functionally an ad-hoc debt register already — it contains 18 scored items with documented rationale, recalibrated likelihood estimates, cross-item dependency findings, and sprint sequencing recommendations. The formalization step is schema normalization and placement, not new analysis.

**Minimum fields per entry**:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (e.g., DEBT-001) |
| `source_item` | Original confidence matrix item number |
| `description` | Brief description of the deferred feature/fix |
| `category` | Architecture / Resilience / Quality / Documentation / Process |
| `deferral_confidence` | Score from confidence matrix (0.0–1.0) |
| `recommended_sprint` | NEXT-SPRINT / BACKLOG / MAINTAIN-DEFERRAL |
| `dependencies` | Other debt items that must be resolved first or in same sprint |
| `last_reviewed` | Sprint name/date when last assessed |
| `notes` | Key recalibration decisions, risk findings, debate conclusions |

**Why before v2.1 starts**: If initialization is deferred until "sometime in v2.1," it will be deferred indefinitely under implementation pressure. The correct time is the gap between sprint completion and next sprint kickoff — a natural pause that makes initialization a bounded 30-minute task rather than a competing priority.

**Effort**: ~30 minutes. Zero blast radius on any functional code.

**Owner**: Sprint retrospective facilitator or whoever writes the v2.1 sprint spec.
```

---

## Change 7 — Amendment E: Definition of Done Additions

**Panel experts**: Gojko Adzic (acceptance criteria completeness), Lisa Crispin (test coverage for quality gate), Karl Wiegers (DoD coverage for all in-scope tasks)

**Rationale**: The existing DoD has no entries for Task 3.5 (new Tier 1 quality gate) or the Task 3.1 amendment (dead code removal). Leaving these unchecked allows them to be considered "done" without verification. The DoD additions follow the existing structure: Code Changes for the new deliverable, Quality Gates for the dead code removal (a grep-verifiable condition), and Verification for the quality gate implementation.

**Location**: Definition of Done section. Three additions: one to "Code Changes" subsection, one to "Quality Gates" subsection, one to "Verification" subsection.

### BEFORE (Code Changes subsection — final two items, exact text):

```
- [ ] `base_variant` field present in producer schema; cross-reference comments in both producer and consumer files
- [ ] `unresolved_conflicts` type resolved to `integer` in both producer and consumer
- [ ] `make verify-sync` passes (`.claude/` mirrors match `src/superclaude/`)
```

### AFTER (Code Changes subsection — full replacement of those three items):

```
- [ ] `base_variant` field present in producer schema; cross-reference comments in both producer and consumer files
- [ ] `unresolved_conflicts` type resolved to `integer` in both producer and consumer
- [ ] Post-Adversarial Artifact Existence Gate (Tier 1) section exists in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with all four existence checks (directory, diff-analysis.md, merged-output.md, return-contract.yaml) in specified order, each with defined failure treatment, positioned before YAML parsing
- [ ] `make verify-sync` passes (`.claude/` mirrors match `src/superclaude/`)
```

### BEFORE (Quality Gates subsection — all five items, exact text):

```
- [ ] No existing tests broken (`uv run pytest` passes)
- [ ] All modified files pass linting (`make lint`)
- [ ] Every verb in Wave 0-4 appears in the glossary table
- [ ] Every sub-step in Wave 2 step 3 uses exactly one verb from the glossary
- [ ] Fallback trigger covers three error types: tool not in allowed-tools, skill not found, skill already running
```

### AFTER (Quality Gates subsection — full replacement):

```
- [ ] No existing tests broken (`uv run pytest` passes)
- [ ] All modified files pass linting (`make lint`)
- [ ] Every verb in Wave 0-4 appears in the glossary table
- [ ] Every sub-step in Wave 2 step 3 uses exactly one verb from the glossary
- [ ] Fallback trigger covers three error types: tool not in allowed-tools, skill not found, skill already running
- [ ] Zero `subagent_type` lines remain in `src/superclaude/skills/sc-adversarial/SKILL.md` (verify: `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0)
```

### BEFORE (Verification subsection — all four items, exact text):

```
- [ ] Verification Test 1 passes (Skill tool in allowed-tools confirmation)
- [ ] Verification Test 2 passes (Wave 2 step 3 structural audit)
- [ ] Verification Test 3 passes (return contract schema consistency)
- [ ] Verification Test 4 passes (pseudo-CLI elimination)
```

### AFTER (Verification subsection — full replacement):

```
- [ ] Verification Test 1 passes (Skill tool in allowed-tools confirmation)
- [ ] Verification Test 2 passes (Wave 2 step 3 structural audit)
- [ ] Verification Test 3 passes (return contract schema consistency)
- [ ] Verification Test 4 passes (pseudo-CLI elimination)
- [ ] Verification Test 6 passes (Tier 1 quality gate structure audit — see below)
```

### New verification test to add after Test 5 in the Verification Plan section:

_(Insert after the existing "Test 5: End-to-End Invocation (Post-Sprint, Manual)" block and before the closing footnote line.)_

```markdown
### Test 6: Tier 1 Quality Gate Structure Audit

**Purpose**: Confirm the artifact existence gate is correctly positioned and contains all required checks.

**Method**: Manual inspection checklist against `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`.

1. Locate the "Post-Adversarial Artifact Existence Gate (Tier 1)" section heading.
2. Confirm it appears BEFORE the Return Contract YAML parsing instructions (not after).
3. Confirm check 1 targets `<output-dir>/adversarial/` directory existence with `failure_stage: "pipeline_not_started"`.
4. Confirm check 2 targets `diff-analysis.md` existence with `failure_stage: "diff_analysis"`.
5. Confirm check 3 targets `merged-output.md` existence with `status: partial, convergence_score: 0.0`.
6. Confirm check 4 targets `return-contract.yaml` existence with instruction to apply missing-file guard from Task 3.2.
7. Confirm all path references use variable form (`<output-dir>/adversarial/`) not hardcoded literals.

**Expected**: All 7 checklist items confirmed.

**Note**: This test can be performed without a working pipeline — it is a static structural check on the specification document.
```

---

## Panel Consensus Summary

Five key spec quality improvements achieved by these amendments:

- **Dead code risk eliminated at source**: The `subagent_type: "general-purpose"` removal (Change 1) prevents the field from being interpreted as functional by developers and copied into new skills, at zero coordination cost by appending to an already-open file.

- **Fault tolerance gap closed**: Task 3.5's Tier 1 quality gate (Change 4) is the only validation mechanism that catches complete pipeline failures in timeout and context-exhaustion scenarios — precisely the highest-rated failure modes in the gap analysis — where `return-contract.yaml` may never be written. The return contract alone cannot protect against the original failure mode; the existence gate is its necessary complement.

- **Copy-risk contained**: The two-sentence Epic 3 scope note (Change 3) prevents sc:adversarial-specific schema fields from becoming de facto framework requirements when other skill authors look for return contract examples. This is a governance problem that would otherwise require a breaking schema change to correct after adoption.

- **Cross-sprint dependency chain captured**: R8 (Change 5) records the Item 14/Item 17 co-dependency constraint in the Risk Register before the team disperses. Without this record, a future sprint adopting the Framework-level Skill Return Protocol (Item 14) could unknowingly eliminate the caller-controlled `--output-dir` namespacing that currently keeps the concurrency race condition risk LOW.

- **Institutional knowledge preserved**: The Sprint 0 Process Deliverable (Change 6) and the Maintenance Errata (Change 2) together prevent two categories of entropy: calibration decisions and recalibrated scores from this sprint's debates being lost before v2.1, and an incorrect path instruction in `agents/README.md` causing real developer sync divergence that compounds with every new agent added to the framework.

---

*Panel review generated 2026-02-23. Inputs: sprint-spec.md (v2.01-Roadmap-v3), deferral-confidence-matrix.md.*
*Escalation items: confidence matrix Items 6 (score 0.38), 2 (score 0.57), 3 (score 0.48).*
*All BEFORE/AFTER text blocks quote exact source document content. Implementer should apply changes in the priority order specified above.*
