---
feature: /sc:forensic + sc:forensic-protocol
artifact: spec-amendments-checklist
date: 2026-02-26
source_verdicts: .dev/releases/backlog/forensic/proposal-verdicts.md
---

# Spec Amendments Checklist — /sc:forensic

This checklist tracks the integration of all 22 adversarially-validated proposals into `forensic-spec.md`. It is the primary tracking document for M0 and M1.

**CRITICAL**: Complete P-001 in Tier 1 before beginning any other proposal. P-001 moves normative content from Section 17 into canonical sections, establishing the true spec baseline that all subsequent edits build on. Editing sections before this move risks introducing contradictions with content still stranded in Section 17.

---

## Tier 1 — Structural Prerequisites (M0 tasks T-M0-1 through T-M0-8)

Execute these in order. P-001 must be complete before any others. P-004 and P-009 are independent of each other. P-006, P-013, P-014, P-015, P-021 are independent of each other.

### P-001: Section 17 Normativity Integration
**Verdict**: ACCEPT | **Score**: 7.75/10 | **Group**: C | **Milestone**: M0

**Sections to modify**: 3.1, 3.2, 5.3, 7 (all phase subsections), 9, 12, 14, Section 17

- [ ] Move FR-047 to Section 3.1 (or 3.2 if non-functional)
- [ ] Move FR-048 to Section 3.1 (or 3.2 if non-functional)
- [ ] Move FR-049 to Section 3.1 (superseded by P-020 redaction scope)
- [ ] Move FR-050 to Section 3.1
- [ ] Move FR-051 to Section 3.1
- [ ] Move FR-052 to Section 3.1 (includes `--clean` flag; add guard clause from P-019)
- [ ] Move FR-053 to Section 3.1 or appropriate phase section
- [ ] Move FR-054 to Section 3.1 or appropriate phase section
- [ ] Move FR-055 to Section 5.3 (command flags)
- [ ] Move NFR-009 to Section 3.2
- [ ] Move NFR-010 to Section 3.2
- [ ] Move Schema 9.9 to Section 9 (renumber as needed)
- [ ] Replace each moved block in Section 17 with forward reference to new location
- [ ] Verify: zero normative requirements remain stranded in Section 17
- [ ] Verify: no numbering collisions introduced (FRs and NFRs renumber sequentially)
- [ ] NOTE: This is a MECHANICAL move — do not rephrase, expand, or improve content during this step

---

### P-004: Fix Artifact Path Inconsistencies
**Verdict**: ACCEPT | **Score**: 10.00/10 | **Group**: C | **Milestone**: M0

**Sections to modify**: FR-015, FR-033, Section 7.7, Section 12.1

- [ ] Update FR-015: change adversarial output paths to `phase-2/adversarial/debate-transcript.md` and `phase-2/adversarial/base-selection.md`
- [ ] Update FR-033: update Phase 6 input list to use `phase-2/adversarial/base-selection.md`
- [ ] Update Section 7.7: update input artifacts list to use `phase-2/adversarial/base-selection.md`
- [ ] Update Section 12.1 directory tree: verify `phase-2/adversarial/` subdirectory is shown
- [ ] Search entire spec for bare `adversarial/` prefix (without `phase-2/`) — standardize all occurrences

---

### P-009: Stable Domain IDs
**Verdict**: ACCEPT | **Score**: 0.92/1.00 | **Group**: A | **Milestone**: M0

**Sections to modify**: Section 7.0, Section 9.4, Section 9.5, Section 9.6, Section 9.7

- [ ] Section 7.0 (orchestrator domain generation action): Add `domain_id` generation as deterministic hash of `(domain_name, sorted(files_in_scope))`, first 8 hex chars
- [ ] Section 7.0: Add `display_index` as separate field for human-readable ordering (sort by risk_score descending)
- [ ] Section 9.4 (InvestigationDomainsSchema): Add `domain_id` (string, pattern: `[a-f0-9]{8}`) to domain item required fields
- [ ] Section 9.4: Add `display_index` (integer) to domain item required fields
- [ ] Section 9.5 (HypothesisFindingSchema): Update `id` pattern from `^H-\d+-\d+$` to `^H-[a-f0-9]{8}-\d+$`
- [ ] Section 9.6 (FixProposalSchema): Update `hypothesis` field description to reflect hash-based ID
- [ ] Section 9.7 (ChangesManifestSchema): Update `hypothesis_id` field to reflect hash-based ID pattern

---

### P-006: Add `new-tests-manifest.json` Schema
**Verdict**: ACCEPT | **Score**: 0.95/1.00 | **Group**: A | **Milestone**: M0

**Sections to modify**: Section 9 (add new schema), FR-027, FR-028, Section 7.6 (Agent 5b)

- [ ] Add new schema to Section 9 (as Section 9.7b or renumber 9.8+ and shift existing):
  - Required: `file_path` (string), `test_type` (enum: unit/integration/e2e), `related_hypothesis_ids` (array of H-ID strings), `status` (enum: new/modified)
  - Optional: `scenario_tags` (array of strings)
- [ ] Update FR-027: cross-reference new schema
- [ ] Update FR-028: `new-tests-manifest.json` conforming to Section 9.7b (or new number)
- [ ] Update Section 7.6 (Agent 5b prompt): reference new-tests-manifest.json schema in description of how 5b consumes it

---

### P-013: Model-Tier Fallback and Observability
**Verdict**: ACCEPT | **Score**: 9.33/10 | **Group**: B | **Milestone**: M0

**Sections to modify**: Section 8, Section 9 (progress.json schema), Section 12, Section 13

- [ ] Section 8: Add `requested_tier` field to each agent definition in the Agent Roster table
- [ ] Section 9.8 (ProgressSchema): Add per-agent tier tracking block:
  ```yaml
  agent_tier_log:
    type: array
    items:
      required: [agent, requested_tier, actual_tier, tier_source]
      properties:
        agent: {type: string}
        requested_tier: {type: string, enum: [haiku, sonnet, opus]}
        actual_tier: {type: string, enum: [haiku, sonnet, opus, unknown]}
        tier_source: {type: string, enum: [best-effort, verified, overridden]}
  ```
- [ ] Section 12 (checkpoint protocol): document tier tracking entries are written at each agent invocation
- [ ] Section 13 (output templates): add "Model Tier Compliance" section to final report template structure

---

### P-015: Minimum Domain Rule for Small Targets
**Verdict**: ACCEPT | **Score**: 9.10/10 | **Group**: B | **Milestone**: M0

**Sections to modify**: FR-005, Section 7.0, Section 9.4, Section 7.2

- [ ] FR-005: change "3-10 dynamically discovered domains" to "1-10 dynamically discovered domains"
- [ ] Section 7.0: Add domain count heuristic table:
  | Source Files | Domain Range | Rationale |
  |---|---|---|
  | 1-3 files | 1 domain | Single investigation scope sufficient |
  | 4-10 files | 1-3 domains | Group by module or concern |
  | 11-50 files | 3-7 domains | Standard auto-discovery |
  | 51+ files | 5-10 domains | Full-scale investigation |
- [ ] Section 9.4: Update `minItems` from 3 to 1 in domains array
- [ ] Section 7.2: Add note — when domain count is 1, skip adversarial debate (pass through with full confidence score); add `"debate_status": "single-domain-passthrough"` to checkpoint

---

### P-014: MCP Tool Contract Alignment
**Verdict**: ACCEPT | **Score**: 9.06/10 | **Group**: B | **Milestone**: M0

**Sections to modify**: Section 5.1, Section 6.1, Section 8, Section 14.2

- [ ] Section 5.1 (command frontmatter): Update `allowed-tools` to include `Edit, MultiEdit`
- [ ] Section 6.1 (skill frontmatter): Update `allowed-tools` to include `Edit, MultiEdit`
- [ ] Section 8: Add MCP activation precondition to ALL agent prompt templates:
  ```
  PRECONDITION: Before using any MCP tool (Serena, Context7, Sequential),
  invoke ToolSearch to load the required tool. Example:
    ToolSearch("select:mcp__serena__replace_symbol_body")
  If ToolSearch fails, fall back to native tool equivalents:
    - Serena replace_symbol_body → Edit tool
    - Serena find_referencing_symbols → Grep tool
    - Context7 → WebSearch or WebFetch
  ```
- [ ] Section 14.2: Audit all fallback chain references — verify every fallback tool appears in the updated `allowed-tools` list

---

### P-021: Multi-Root Path Provenance
**Verdict**: ACCEPT | **Score**: 0.87/1.00 | **Group**: A | **Milestone**: M0

**Sections to modify**: Section 9.1, 9.2, 9.4, 9.5, 9.6, 9.7, 9.7b (new)

- [ ] Section 9.1 (StructuralInventorySchema): Add `target_root` (string) to file_tree items
- [ ] Section 9.2 (DependencyGraphSchema): Add `target_root` (string) to import_chain items
- [ ] Section 9.4 (InvestigationDomainsSchema): Add `target_roots` (object, maps root_id → absolute_path) to `generation_metadata`
- [ ] Section 9.5 (HypothesisFindingSchema): Add `target_root` (string) to evidence items (pattern: `"file:line -- excerpt"` becomes `"target_root:file:line -- excerpt"` or separate field)
- [ ] Section 9.6 (FixProposalSchema): Add `target_root` (string) to change record items
- [ ] Section 9.7 (ChangesManifestSchema): Add `target_root` (string) to changes items
- [ ] Section 9.7b (NewTestsManifestSchema): Add `target_root` (string) to manifest items
- [ ] Note: For single-root invocations, `target_root` defaults to the sole path; no behavior change for common case

---

## Tier 2 — Core Schema & Contract Gaps (M0 continuation)

The above 8 proposals constitute M0. No additional Tier 2 proposals exist beyond those listed (all 8 implementation-blocking proposals are in M0).

---

## Tier 3 — Behavioral Completeness (M1 tasks T-M1-1 through T-M1-5)

### P-017: Baseline Test Artifact
**Verdict**: ACCEPT | **Score**: 8.88/10 | **Group**: D | **Milestone**: M1

**Sections to modify**: Section 7.5, Section 7.6, Section 12.1, Section 16.2

- [ ] Section 7.5 (Phase 4 contract): Add `phase-4/baseline-test-results.md` as required output, captured BEFORE any fix implementation
- [ ] Section 7.6 (Phase 5 contract, Agent 5b): Add requirement to compute `introduced_failures` vs `preexisting_failures` by diffing against baseline
- [ ] Section 12.1: Add `phase-4/baseline-test-results.md` to artifact directory tree
- [ ] Section 16.2 (quality metrics): Update test pass rate metric to reference baseline-diffed results

---

### P-018: Pass/Fail Exit Criteria
**Verdict**: ACCEPT | **Score**: 8.70/10 | **Group**: D | **Milestone**: M1

**Sections to modify**: Section 4 (new subsection), Section 13, FR additions

- [ ] Add new Section 4.5 "Pipeline Exit State Model" (or subsection of 4.3):
  - `success`: all phases complete, 0 lint errors, 0 introduced test failures, self-review no regressions
  - `success_with_risks`: all phases complete, 0 lint errors, 0 introduced test failures, self-review has residual risks
  - `failed`: any introduced test failures, lint errors in changed files, Phase 4 errors, or pipeline-level errors
  - `--dry-run`: `success` if Phases 0-3b complete without error, `failed` otherwise
- [ ] Section 13 (output templates): Add YAML frontmatter block to final report template:
  ```yaml
  ---
  exit_status: success | success_with_risks | failed
  pipeline_version: 1.0.0
  phases_completed: [0, 1, 2, 3, "3b", 4, 5, 6]
  phases_skipped: []
  ---
  ```
- [ ] Add FR for exit state to Section 3.1 (after P-001 moves Section 17 content in place)

---

### P-003: Dry-Run Behavior and `skipped_phases`
**Verdict**: MODIFY | **Score**: 8.40/10 | **Group**: C | **Milestone**: M1

**Sections to modify**: FR-044, Section 9.8 (ProgressSchema), Section 7.7

- [ ] FR-044: Codify dry-run phase plan: executes Phases 0→1→2→3→3b→6; skips Phases 4 and 5
- [ ] Section 9.8 (ProgressSchema): Add `skipped_phases` as optional array field:
  ```yaml
  skipped_phases:
    type: array
    items: {type: [integer, string]}
    description: "Phases intentionally skipped (e.g., [4, 5] for dry-run)"
  ```
- [ ] Remove any `skipped_by_mode` per-phase status from schema or narrative
- [ ] Section 7.7 (Phase 6 output): Add "Would-Implement" section requirement for dry-run reports (implementation plan from fix-selection, clearly marked as not executed)

---

### P-002: `--depth` Precedence Rule
**Verdict**: ACCEPT | **Score**: 8.30/10 | **Group**: C | **Milestone**: M1

**Sections to modify**: Section 5.3 (FR-038), Section 7.2, Section 7.4

- [ ] Section 5.3 / FR-038: Add precedence rule:
  > `--depth` precedence: circuit-breaker override > explicit `--depth` CLI flag > phase-specific default. Per-phase defaults (Phase 2: `deep`, Phase 3b: `standard`) apply only when `--depth` is omitted from the command.
- [ ] Section 7.2 (Phase 2 invocation): Change hardcoded `--depth deep` to `--depth {depth_flag or "deep"}` with annotation "default: deep"
- [ ] Section 7.4 (Phase 3b invocation): Change hardcoded `--depth standard` to `--depth {depth_flag or "standard"}` with annotation "default: standard"

---

### P-005: Phase 3b Canonical Output Path
**Verdict**: MODIFY | **Score**: 8.05/10 | **Group**: C | **Milestone**: M1

**Sections to modify**: Section 7.4, FR-023, FR-024, FR-033, Section 12.1

- [ ] Section 7.4: Change all references to fix-selection output to `phase-3b/fix-selection.md`
- [ ] FR-023: Update output path to `phase-3b/fix-selection.md`
- [ ] FR-024: Update input path to `phase-3b/fix-selection.md`
- [ ] FR-033: Update Phase 6 input list to use `phase-3b/fix-selection.md`
- [ ] Section 12.1: Add `phase-3b/` directory entry to artifact tree (with `fix-selection.md` listed)
- [ ] Confirm: no migration fallback language added (spec is draft, no existing implementations)

---

## Tier 4 — Runtime Policy & Error Handling (M1 tasks T-M1-6 through T-M1-10)

### P-011: Three-Level Adversarial Fallback Chain
**Verdict**: ACCEPT | **Score**: 8.66/10 | **Group**: B | **Milestone**: M1

**Sections to modify**: Section 14.1

- [ ] Section 14.1: Replace current fallback with three-level degradation chain:
  1. Level 1: Retry adversarial protocol with `--depth quick`
  2. Level 2: Spawn single Sonnet scoring agent (60-second hard timeout, 1,000-token output cap); reads all finding summaries; produces ranked list by confidence score
  3. Level 3: Emit finding file paths with `"debate_status": "skipped"` metadata; all surviving hypotheses proceed to Phase 3 without scoring
- [ ] Verify: no level in the chain reads raw source code (orchestrator constraint from Section 4.3 preserved)
- [ ] Verify: Level 2 scoring agent is within `allowed-tools` contract

---

### P-012: Token Budget Overflow Policy
**Verdict**: MODIFY | **Score**: 8.71/10 | **Group**: B | **Milestone**: M1

**Sections to modify**: New Section 4.4, Section 9.8 (ProgressSchema), FR-006, FR-011, FR-016, FR-024, FR-035

- [ ] Add Section 4.4 "Token Budget Overflow Policy" with table:
  | Phase | Context | Soft Target | Hard Stop | Overflow Action |
  |---|---|---|---|---|
  | Phase 0 synthesis | FR-006 | 500 tokens | 750 tokens | Truncate domain descriptions to single sentence |
  | Phase 1 collection | FR-011 | 1,000 tokens | 1,500 tokens | List file paths only; omit finding summaries |
  | Phase 2 consumption | FR-016 | 500 tokens | 750 tokens | Read top-N hypotheses by confidence; skip lowest |
  | Phase 3b consumption | FR-024 | 800 tokens | 1,200 tokens | Read top-N fixes by composite score; skip lowest |
  | Phase 6 synthesis | FR-035 | 2,000 tokens | 3,000 tokens | Omit rejected-hypotheses section from final report |
- [ ] Section 9.8 (ProgressSchema): Add `budget_status` array field for per-phase budget tracking:
  ```yaml
  budget_status:
    type: array
    items:
      required: [phase, status, soft_target, hard_stop]
      properties:
        phase: {type: string}
        status: {type: string, enum: [within_soft, exceeded_soft, exceeded_hard]}
        soft_target: {type: integer}
        hard_stop: {type: integer}
        overflow_action_taken: {type: string}
  ```
- [ ] FR-006: Reword from "SHALL consume no more than 500 tokens" to "SHOULD target 500 tokens (soft); overflow policy Section 4.4 applies"
- [ ] FR-011: Reword similarly (soft 1,000 / hard 1,500)
- [ ] FR-016: Reword similarly (soft 500 / hard 750)
- [ ] FR-024: Reword similarly (soft 800 / hard 1,200)
- [ ] FR-035: Reword similarly (soft 2,000 / hard 3,000)

---

### P-020: Artifact-Wide Redaction
**Verdict**: ACCEPT | **Score**: 8.15/10 | **Group**: D | **Milestone**: M1

**Sections to modify**: FR-049 superseded, new FR in Section 3.1, Section 14 (new subsection), Section 5.3 (new `--no-redact` flag)

- [ ] Supersede FR-049 (if present after P-001 integration): replace with pipeline-level redaction scope
- [ ] Add new FR to Section 3.1: "After each phase writes artifacts, the pipeline SHALL scan all new files for sensitive data patterns and redact matches with `[REDACTED]`"
- [ ] Section 14 (or new Section 14.3 "Redaction Policy"):
  - Mechanism: pipeline-level post-processing (not per-agent prompt modification)
  - Default pattern set: AWS keys (`AKIA[0-9A-Z]{16}`), GCP service account keys, `password=`, `secret=`, `token=`, `api_key=`, PEM private key blocks (`-----BEGIN.*PRIVATE KEY-----`)
  - `--no-redact` flag: applies to all artifact writes; emits mandatory warning
  - Configurable patterns: deferred to future `--redaction-config` flag
- [ ] Section 5.3: Add `--no-redact` flag definition

---

### P-016: Zero-Hypothesis Terminal Path
**Verdict**: ACCEPT | **Score**: 8.03/10 | **Group**: D | **Milestone**: M1

**Sections to modify**: Section 7.2 (orchestrator filtering action), Section 5.3 (new flag), Section 14 (terminal behavior)

- [ ] Section 7.2 (orchestrator hypothesis filtering): Add deterministic terminal path when zero hypotheses survive:
  - Default: threshold is immutable; pipeline terminates with terminal report
  - `--auto-relax-threshold` flag: auto-retries with threshold × 0.8 (capped at 0.5 minimum)
  - Terminal report MUST include: original threshold value, count of filtered hypotheses, suggestion to re-run with `--auto-relax-threshold`
- [ ] Section 5.3: Add `--auto-relax-threshold` flag (boolean, default false)
- [ ] Section 14: Add "Terminal States" section — zero-hypothesis terminal, pipeline error terminal, dry-run terminal

---

### P-022: MCP Concurrency and Prompt-Based Budgets
**Verdict**: MODIFY | **Score**: 8.03/10 | **Group**: B | **Milestone**: M1

**Sections to modify**: Section 5.3, Section 8, Section 11

- [ ] Section 5.3: Change `--concurrency` default from 10 to 5
- [ ] Section 8: Add per-phase MCP access budget table to agent specification section header:
  | Phase | Agent Type | Serena Calls (max) | Context7 Calls (max) | Sequential Calls (max) |
  |---|---|---|---|---|
  | Phase 0 recon | Recon agents (Haiku) | 0 (except Agent 0b: 1 get_symbols_overview) | 0 | 0 |
  | Phase 1 | Investigation | 3 per domain | 1 per domain | 0 |
  | Phase 3 | Fix Proposal | 2 per proposal | 2 per proposal | 0 |
  | Phase 4a | Implementation specialist | 5 per fix | 2 per fix | 0 |
  | Phase 4b | Test creation (quality-eng) | 0 | 3 per fix | 0 |
- [ ] Section 8: Add budget enforcement note to each agent template: "MCP budget: {Serena: N}, {Context7: N}. Exceed budget → fall back to native tool equivalents."
- [ ] Section 11 (MCP Routing Table): Add advisory note on prompt-based enforcement (not runtime semaphores)
- [ ] Document Agent 0b carve-out: Serena `get_symbols_overview` is permitted once per Phase 0 despite the recon agent budget of 0 (FR-003 specificity overrides general budget)

---

## Tier 5 — Hardening & Proportionate Fixes (M1 tasks T-M1-11 through T-M1-14)

### P-007: Risk Surface Schema Alignment (partial)
**Verdict**: MODIFY | **Score**: 0.70/1.00 | **Group**: A | **Milestone**: M1

**Sections to modify**: Section 9.3 (RiskSurfaceSchema), Section 7.0 (Agent 0c prompt), FR-004

- [ ] Section 9.3: Confirm `overall_risk_score` is in `required` array (it already is per current spec — verify)
- [ ] Section 9.3: Add calculation method: "weighted average of all category `risk_score` values"
- [ ] Section 7.0 (Agent 0c prompt): Add explicit instruction to compute `overall_risk_score` as weighted average of category scores
- [ ] FR-004: Add "including `overall_risk_score` computed as weighted average of category risk scores" to the output description
- [ ] Note: `secrets_exposure` category is REJECTED — do NOT add to schema or prompts

---

### P-010: Fix Tier Uniqueness (partial)
**Verdict**: MODIFY | **Score**: 0.67/1.00 | **Group**: A | **Milestone**: M1

**Sections to modify**: Section 9.6 (FixProposalSchema), FR-018, Section 7.3 (orchestrator action) and Section 7.4 (orchestrator action)

- [ ] Section 9.6: Add `uniqueItems: true` constraint on `fix_options` array (by tier field)
- [ ] Section 9.6: Note: uniqueness is on the `tier` enum value, not on the entire object
- [ ] FR-018: Change "containing three fix tiers (minimal, moderate, robust)" to "containing up to three fix tiers (minimal, moderate, robust) with unique tier values"
- [ ] Section 7.4 (Phase 3b orchestrator, or Section 7.3): Add `--fix-tier` fallback logic:
  > If the requested `--fix-tier` value is absent from a proposal's `fix_options`, select the next-lower tier (robust → moderate → minimal). If no tiers remain, skip this fix. Emit warning to final report: "Fix {H-id}: requested tier '{tier}' not available; used '{fallback_tier}'"

---

### P-008: `progress.json` Hardening (partial)
**Verdict**: MODIFY | **Score**: 0.60/1.00 | **Group**: A | **Milestone**: M1

**Sections to modify**: Section 9.8 (ProgressSchema), Section 12 (resume protocol)

- [ ] Section 9.8: Add `target_paths` as **required** field:
  ```yaml
  target_paths:
    type: array
    items: {type: string}
    minItems: 1
    description: "Target paths as provided to the command; used for stale-target detection on resume"
  ```
- [ ] Section 9.8: Promote `flags` to **required** (remove from optional/description-only position)
- [ ] Section 9.8: Add `git_head_or_snapshot` as **optional** field:
  ```yaml
  git_head_or_snapshot:
    type: string
    description: "Git HEAD SHA or snapshot identifier at time of original run (optional; aids stale-codebase detection)"
  ```
- [ ] Section 12 (resume protocol): Update step 3 to compare `target_paths`; update step 4 to compare `git_head_or_snapshot`
- [ ] Note: `spec_version`, `run_id`, `phase_status_map` are REJECTED — do NOT add

---

### P-019: `--clean` Guard Clause (minimal scope)
**Verdict**: MODIFY | **Score**: 5.53/10 | **Group**: D | **Milestone**: M1

**Sections to modify**: FR-052 (or equivalent after P-001 integration)

- [ ] Find `--clean` flag definition in Section 3.1 or Section 5.3 (after P-001 integration of FR-052)
- [ ] Add single guard-clause sentence:
  > `--clean` SHALL only execute artifact removal after all phases have completed successfully (progress.json shows all phases in `completed_phases`). If the pipeline did not complete successfully, `--clean` is ignored and a warning is emitted: "Artifacts retained: pipeline did not complete successfully."
- [ ] Note: `--clean=archive|delete` variants are REJECTED — do NOT add any variant syntax

---

## Amendment Completion Tracking

| # | Proposal | Tier | Group | Verdict | Milestone | Status |
|---|----------|------|-------|---------|-----------|--------|
| P-001 | Section 17 normativity | 1 | C | ACCEPT | M0 | [ ] pending |
| P-004 | Artifact path fix | 1 | C | ACCEPT | M0 | [ ] pending |
| P-009 | Domain ID stability | 1 | A | ACCEPT | M0 | [ ] pending |
| P-006 | new-tests-manifest schema | 2 | A | ACCEPT | M0 | [ ] pending |
| P-013 | Model tier tracking | 2 | B | ACCEPT | M0 | [ ] pending |
| P-015 | Min domain rule | 2 | B | ACCEPT | M0 | [ ] pending |
| P-014 | Tool contract alignment | 2 | B | ACCEPT | M0 | [ ] pending |
| P-021 | Multi-root provenance | 2 | A | ACCEPT | M0 | [ ] pending |
| P-017 | Baseline test artifact | 3 | D | ACCEPT | M1 | [ ] pending |
| P-018 | Exit state model | 3 | D | ACCEPT | M1 | [ ] pending |
| P-003 | Dry-run skipped_phases | 3 | C | MODIFY | M1 | [ ] pending |
| P-002 | --depth precedence | 3 | C | ACCEPT | M1 | [ ] pending |
| P-005 | Phase 3b canonical path | 3 | C | MODIFY | M1 | [ ] pending |
| P-011 | Adversarial fallback chain | 4 | B | ACCEPT | M1 | [ ] pending |
| P-012 | Token overflow policy | 4 | B | MODIFY | M1 | [ ] pending |
| P-020 | Artifact redaction | 4 | D | ACCEPT | M1 | [ ] pending |
| P-016 | Zero-hypothesis terminal | 4 | D | ACCEPT | M1 | [ ] pending |
| P-022 | MCP budgets / concurrency=5 | 4 | B | MODIFY | M1 | [ ] pending |
| P-007 | Risk surface alignment (partial) | 5 | A | MODIFY | M1 | [ ] pending |
| P-010 | Fix tier uniqueness (partial) | 5 | A | MODIFY | M1 | [ ] pending |
| P-008 | progress.json hardening (partial) | 5 | A | MODIFY | M1 | [ ] pending |
| P-019 | --clean guard clause | 5 | D | MODIFY | M1 | [ ] pending |

---

## Deferred Items (explicitly not implemented in v1.0)

These items were rejected by the adversarial process or explicitly deferred by MODIFY verdicts. Do not implement in v1.0.

| Item | Source Proposal | Reason for Deferral | Trigger to Reconsider |
|------|----------------|---------------------|----------------------|
| `secrets_exposure` risk category | P-007 | No FR, weak evidence, oracle testing gap | Formal FR + test fixture corpus |
| `spec_version` field in progress.json | P-008 | YAGNI for v1.0 | Schema breaking change in v2.0 |
| `run_id` field in progress.json | P-008 | Observability, not correctness | Observability sprint |
| `phase_status_map` in progress.json | P-008 | Duplicates existing fields | New per-phase metadata requirements |
| "Exactly 3 tiers" constraint | P-010 | Token waste, filler incentives, untestable | Evidence that 1-2 tier proposals cause failures |
| `--clean=archive|delete` variants | P-019 | Over-engineered for <5% scenario | Documented user demand |
| `--redaction-config` flag | P-020 | Future enhancement | User request for custom patterns |
| Full MCP scheduler (semaphores) | P-022 | Rejected in favor of prompt-based budgets | Runtime MCP scheduling capability |
