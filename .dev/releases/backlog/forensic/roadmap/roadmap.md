---
feature: /sc:forensic + sc:forensic-protocol
spec_version: 1.0.0-draft
roadmap_version: 1.0.0
date: 2026-02-26
authors: SuperClaude Architecture Team
template: feature
depth: deep
compliance: strict
status: planning
input_spec: .dev/releases/backlog/forensic/forensic-spec.md
input_verdicts: .dev/releases/backlog/forensic/proposal-verdicts.md
proposals_applied: 22 (14 ACCEPT + 8 MODIFY)
total_milestones: 9
estimated_total_effort: XL (10-14 weeks)
---

# /sc:forensic — Implementation Roadmap

## Overview

This roadmap governs the implementation of the `/sc:forensic` command and the `sc:forensic-protocol` skill for the SuperClaude Framework. It incorporates all 22 adversarially-validated change proposals from the proposal-verdicts file as mandatory pre-implementation spec amendments, followed by a phased implementation that respects the dependency order of the 7-phase pipeline architecture.

**Feature summary**: A generic forensic QA and debug pipeline that auto-discovers investigation domains, runs parallel root-cause analysis with model tiering, delegates hypothesis and fix validation to the existing `/sc:adversarial` command, delegates implementation to specialist agents, and produces a comprehensive evidence-backed report with checkpoint/resume support.

**Relationship to existing commands**:
- Depends on `/sc:adversarial` (Phases 2 and 3b) — runtime dependency, must be operational
- Borrows patterns from `/sc:cleanup-audit` (checkpoint protocol, fan-out/fan-in orchestration)
- Borrows patterns from `/sc:spawn` (epic/story/task decomposition for domain generation)
- Borrows compliance tiering concept from `sc:task-unified-protocol` (fix risk classification)

---

## Milestone Index

| ID | Name | Effort | Depends On | Blocks |
|----|------|--------|------------|--------|
| M0 | Spec Amendments (Tier 1-2 Proposals) | M | — | all |
| M1 | Spec Amendments (Tier 3-5 Proposals) | M | M0 | M2+ |
| M2 | Foundation: Command, Skill Shell, Schemas | M | M1 | M3+ |
| M3 | Checkpoint/Resume Protocol | S | M2 | M4+ |
| M4 | Phase 0: Reconnaissance Agents | M | M3 | M5 |
| M5 | Phase 1 + Phase 3: Discovery & Fix Proposals | L | M4 | M6 |
| M6 | Adversarial Integration (Phases 2 & 3b) | M | M5 | M7 |
| M7 | Implementation & Validation Pipeline (Phases 4-5) | L | M6 | M8 |
| M8 | Phase 6: Final Report + CLI Integration | M | M7 | M9 |
| M9 | Testing, Verification & Documentation | L | M8 | release |

---

## M0 — Spec Amendments: Structural Prerequisites (Tier 1-2)

**Effort**: M (1 week)
**Depends on**: nothing — this is the mandatory first step
**Blocks**: all subsequent milestones

These proposals must execute before any implementation work begins. They establish the true baseline of the spec (P-001 integrates Section 17 normative content), fix runtime-breaking artifact paths (P-004), resolve the latent domain-ID resume bug (P-009), and close implementation-blocking schema/contract gaps (P-006, P-013, P-014, P-015, P-021).

### Tasks

**T-M0-1: P-001 — Section 17 normativity integration** (Priority: 1)
- Mechanically move FR-047 through FR-055, NFR-009, NFR-010, and Schema 9.9 from Section 17 into their canonical normative sections (Sections 3.1, 3.2, 5.3, 7, 9, 12, 14, and Appendix A)
- Replace each moved block in Section 17 with a forward reference to the new location
- Constraint: move content verbatim, adjust numbering only — do not rephrase or expand during this step
- Verify no normative content remains stranded in Section 17 after integration

**T-M0-2: P-004 — Fix adversarial artifact path inconsistencies** (Priority: 2)
- Standardize all references to adversarial output artifacts to use the `phase-2/` prefix throughout the spec
  - `phase-2/adversarial/base-selection.md`
  - `phase-2/adversarial/debate-transcript.md`
- Update: FR-015, FR-033 (Phase 6 input list), Section 7.7, Section 12.1 directory tree

**T-M0-3: P-009 — Stable domain IDs across retries/resume** (Priority: 3)
- Generate `domain_id` as deterministic hash of `(domain_name, sorted(files_in_scope))` — not position-based index
- Hypothesis IDs become `H-{domain_id_short}-{sequence}` where `domain_id_short` is first 8 characters of hash
- Add `display_index` as a separate field for human-readable report ordering
- Update schemas: Section 9.4 (add `domain_id`, `display_index`), Section 9.5 (update ID pattern to `H-[a-f0-9]{8}-\d+`), Section 9.6 (hypothesis reference format), Section 9.7 (hypothesis_id format in changes manifest)

**T-M0-4: P-006 — Add `new-tests-manifest.json` schema** (Priority: 4, ACCEPT)
- Define schema in Section 9 (new Section 9.7b, or renumber as 9.8 and shift existing 9.8/9.9)
- Required fields: `file_path` (string), `test_type` (enum: unit/integration/e2e), `related_hypothesis_ids` (array of H-ID strings), `status` (enum: new/modified)
- Optional: `scenario_tags` (array of strings)
- Cross-reference from FR-027, FR-028, and Agent 5b prompt template

**T-M0-5: P-013 — Model-tier fallback and observability** (Priority: 5, ACCEPT)
- Add `requested_tier` and `actual_tier` fields to all phase metadata and agent invocation records in `progress.json`
- Define `tier_source` field values: `best-effort` (prompt hinting), `verified` (future runtime), `overridden` (user forced)
- Add "Model Tier Compliance" section to final report template (Section 13)
- Update Section 8 agent specifications to include `requested_tier` per agent definition

**T-M0-6: P-015 — Minimum-domain rule for small targets** (Priority: 6, ACCEPT)
- Change domain count constraint from `3..10` to `1..10` in FR-005 and schema Section 9.4
- Add domain count heuristic table to Section 7.0:
  - 1-3 files → 1 domain
  - 4-10 files → 1-3 domains
  - 11-50 files → 3-7 domains
  - 51+ files → 5-10 domains
- Add single-domain handling note to Section 7.2: when N=1, Phase 2 adversarial debate passes through with full confidence score (skip debate)

**T-M0-7: P-014 — MCP tool contract alignment** (Priority: 7, ACCEPT)
- Update `allowed-tools` in both command frontmatter (Section 5.1) and skill frontmatter (Section 6.1) to include `Edit` and `MultiEdit`
- Add MCP activation precondition block to agent prompt templates in Section 8
- Update fallback chain in Section 14.2 to reference only tools in the `allowed-tools` contract

**T-M0-8: P-021 — Multi-root path provenance** (Priority: 8, ACCEPT)
- Add `target_root` (string) field to all path-bearing schema records: structural-inventory items (9.1), dependency-graph import chains (9.2), hypothesis evidence entries (9.5), fix change records (9.6), changes-manifest entries (9.7), new-tests-manifest entries
- Add `target_roots` array to top-level metadata in `investigation-domains.json` (9.4) mapping root IDs to absolute paths
- Normalize: all relative paths are relative to their `target_root`, never to CWD
- For single-root invocations, `target_root` defaults to the sole path

### Acceptance Criteria (M0)

- [ ] Section 17 is forward-reference-only; all normative content is in canonical sections
- [ ] All adversarial artifact path references use `phase-2/adversarial/` prefix consistently
- [ ] Domain IDs are deterministic hash-based; test: same inputs on two independent runs produce identical domain IDs
- [ ] `new-tests-manifest.json` schema is present in Section 9 with all required fields
- [ ] Every agent definition in Section 8 includes `requested_tier`; `progress.json` schema includes tier tracking
- [ ] FR-005 and Section 9.4 allow `minItems: 1` for domains
- [ ] `allowed-tools` in Section 5.1 and 6.1 includes Edit and MultiEdit
- [ ] All path-bearing schema records include `target_root` field

---

## M1 — Spec Amendments: Behavioral Completeness, Runtime Policy & Hardening (Tiers 3-5)

**Effort**: M (1 week)
**Depends on**: M0 (Section 17 integration establishes baseline before additional edits)
**Blocks**: M2+

### Tasks

**T-M1-1: P-017 — Baseline test artifact** (Priority: 9, ACCEPT)
- Update Section 7.5 (Phase 4 contract): add `phase-4/baseline-test-results.md` as required output artifact produced before implementing any fixes
- Update Section 7.6 (Phase 5 contract): require Agent 5b to compute `introduced_failures` vs `preexisting_failures` by diffing against baseline
- Update Section 12.1 artifact tree to include `phase-4/baseline-test-results.md`
- Update Section 16.2 quality metrics: test pass rate metric references baseline-diffed results

**T-M1-2: P-018 — Exit state model** (Priority: 10, ACCEPT)
- Define three-state exit model with explicit boundary conditions:
  - `success`: all phases complete, 0 lint errors, 0 introduced test failures, self-review finds no regressions
  - `success_with_risks`: all phases complete, 0 lint errors, 0 introduced test failures, but self-review identifies residual risks
  - `failed`: any of: introduced test failures, lint errors in changed files, Phase 4 errors, or pipeline-level errors
  - `--dry-run` exits: `success` if Phases 0-3b complete without error, `failed` otherwise
- Add exit status to final report YAML frontmatter as machine-readable block
- Add to new Section 4.5 (or as subsection of 4.3)

**T-M1-3: P-003 — Dry-run behavior and `skipped_phases` array** (Priority: 11, MODIFY)
- Codify dry-run phase plan in FR-044: executes Phases 0→1→2→3→3b→6; skips Phases 4 and 5
- Replace any `skipped_by_mode` per-phase status with `skipped_phases` array in `progress.json`
  - Example: `"skipped_phases": [4, 5]` when `"flags": {"dry_run": true}`
- Require "would-implement" section in Phase 6 dry-run final report (implementation plan from fix-selection, never executed)
- Update `progress.json` schema Section 9.8 (previously 9.8, may be renumbered after M0 schema additions)

**T-M1-4: P-002 — `--depth` precedence rule** (Priority: 12, ACCEPT)
- Add precedence rule to Section 5.3 (FR-038):
  - `--depth` precedence: circuit-breaker override > explicit `--depth` CLI flag > phase-specific default
  - Per-phase defaults (Phase 2: `deep`, Phase 3b: `standard`) apply only when `--depth` is omitted
- Update Sections 7.2 and 7.4 invocation patterns to show defaults as conditional, not hardcoded

**T-M1-5: P-005 — Phase 3b canonical output path** (Priority: 13, MODIFY)
- Define canonical path as `phase-3b/fix-selection.md`
- Add `phase-3b/` directory to Section 12.1 directory tree
- Update Section 7.4, FR-023, FR-024, and FR-033 to reference `phase-3b/fix-selection.md`
- Remove any migration fallback language (spec is draft, no existing implementations)

**T-M1-6: P-011 — Three-level adversarial fallback chain** (Priority: 14, ACCEPT)
- Replace Section 14.1 fallback with three-level degradation chain:
  1. Level 1: Retry adversarial protocol with `--depth quick`
  2. Level 2: Spawn single Sonnet scoring agent with 60-second hard timeout and 1,000-token output cap; agent reads finding summaries and produces ranked list by confidence
  3. Level 3: If scoring agent fails, emit finding file paths with `"debate_status": "skipped"` metadata; all surviving hypotheses proceed to Phase 3 without scoring
- Ensure no level reads raw source code (preserves orchestrator constraint from Section 4.3)

**T-M1-7: P-012 — Token overflow policy** (Priority: 15, MODIFY)
- Add Section 4.4 "Token Budget Overflow Policy" with per-phase static rules table:
  | Phase | Context | Soft Target | Hard Stop | Overflow Action |
  |-------|---------|-------------|-----------|-----------------|
  | Phase 0 synthesis | FR-006 | 500 tokens | 750 tokens | Truncate domain descriptions to single sentence |
  | Phase 1 collection | FR-011 | 1,000 tokens | 1,500 tokens | List file paths only; omit finding summaries |
  | Phase 2 consumption | FR-016 | 500 tokens | 750 tokens | Read top-N hypotheses by confidence; skip lowest |
  | Phase 3b consumption | FR-024 | 800 tokens | 1,200 tokens | Read top-N fixes by composite score; skip lowest |
  | Phase 6 synthesis | FR-035 | 2,000 tokens | 3,000 tokens | Omit rejected-hypotheses section |
- Add `budget_status` field to `progress.json` per-phase metadata
- Reword FR-006, FR-011, FR-016, FR-024, FR-035 as soft targets with overflow policy references

**T-M1-8: P-020 — Artifact-wide redaction** (Priority: 16, ACCEPT)
- Specify pipeline-level post-processing redaction (not per-agent prompt modification)
- After each phase writes artifacts, a redaction pass scans all new files
- Default patterns: AWS keys (AKIA...), GCP service account keys, `password=`, `secret=`, `token=`, `api_key=`, PEM private key blocks
- Add `--no-redact` flag with mandatory warning (FR addition)
- Update FR-049 to supersede with new scope covering all artifacts
- Defer `--redaction-config` to future enhancement

**T-M1-9: P-016 — Zero-hypothesis terminal path** (Priority: 17, ACCEPT)
- Add deterministic behavior when zero hypotheses survive confidence filtering
- Add `--auto-relax-threshold` opt-in flag (FR-041 extension)
- Default: threshold is immutable; pipeline emits terminal report
- Terminal report must include: original threshold value, count of hypotheses filtered out, suggestion to re-run with `--auto-relax-threshold`
- Add to Section 7.2 (Phase 2 orchestrator action) and Section 14

**T-M1-10: P-022 — MCP concurrency and prompt-based budgets** (Priority: 18, MODIFY)
- Change `--concurrency` default from 10 to 5 in Section 5.3
- Add per-phase MCP access budget table to agent specification templates in Section 8:
  | Phase | Agent Type | Serena Calls (max) | Context7 Calls (max) |
  |-------|-----------|-------------------|---------------------|
  | Phase 0 | Recon (Haiku) | 0 | 0 |
  | Phase 1 | Investigation | 3 per domain | 1 per domain |
  | Phase 3 | Fix Proposal | 2 per proposal | 2 per proposal |
  | Phase 4a | Implementation | 5 per fix | 2 per fix |
  | Phase 4b | Test Creation | 0 | 3 per fix |
- Add advisory note to Section 11 explaining prompt-based enforcement (not runtime semaphores)

**T-M1-11: P-007 — Risk Surface schema alignment** (Priority: 19, MODIFY — partial)
- Accept: align Agent 0c prompt to require `overall_risk_score` computation
- Specify calculation method: weighted average of category `risk_score` values
- Update FR-004 to explicitly mention `overall_risk_score` as a required output
- Reject: `secrets_exposure` category (no FR, oracle testing gap) — deferred

**T-M1-12: P-010 — Fix tier uniqueness constraint** (Priority: 20, MODIFY — partial)
- Add uniqueness constraint on `tier` values within `fix_options` array (schema: `uniqueItems: true` by tier field)
- Update FR-018 text from "containing three fix tiers" to "containing up to three fix tiers (minimal, moderate, robust)"
- Add orchestrator `--fix-tier` fallback logic: if requested tier is absent, select next-lower available tier and emit warning to final report
- Reject `minItems: 3` enforcement (generates filler tiers)

**T-M1-13: P-008 — `progress.json` hardening** (Priority: 21, MODIFY — partial)
- Add `target_paths` as required field (enables stale-target detection on resume)
- Promote `flags` to required (resume logic already depends on it; formalizes the dependency)
- Add `git_head_or_snapshot` as optional field (enables stale-codebase detection)
- Defer: `spec_version`, `run_id` (YAGNI for v1.0), `phase_status_map` (duplicates existing fields)

**T-M1-14: P-019 — `--clean` guard clause** (Priority: 22, MODIFY — minimal scope)
- Add single guard-clause sentence to FR-052:
  - `--clean` SHALL only execute artifact removal after all phases have completed successfully (progress.json shows all phases in `completed_phases`). If pipeline did not complete successfully, `--clean` is ignored and a warning is emitted.
- Reject `--clean=archive|delete` variants (over-engineered for <5% scenario)

### Acceptance Criteria (M1)

- [ ] Baseline test artifact contract exists in Phases 4 and 5 sections
- [ ] Exit state model with boundary conditions is defined in Section 4 or 7
- [ ] Dry-run phase plan is codified: Phases 0-3b-6, skip 4-5, `skipped_phases` array in progress.json
- [ ] `--depth` precedence rule is documented in Section 5.3
- [ ] `phase-3b/fix-selection.md` is the canonical path in all FRs and Section 12.1
- [ ] Three-level adversarial fallback chain is in Section 14.1
- [ ] Token budget overflow policy table exists in new Section 4.4
- [ ] Redaction post-processing is specified with default patterns and `--no-redact` flag
- [ ] Zero-hypothesis terminal path is defined with `--auto-relax-threshold` flag
- [ ] `--concurrency` default is 5; per-phase MCP budgets are in agent templates
- [ ] All 22 proposal changes are either fully integrated or explicitly deferred with justification

---

## M2 — Foundation: Command Definition, Skill Shell, and Data Schemas

**Effort**: M (1 week)
**Depends on**: M1 (amended spec is the authoritative source)
**Blocks**: M3, M4, M5, M6, M7, M8

This milestone creates all the structural files that subsequent milestones will populate. The command file, skill shell, and schema definitions are created first so that all implementation milestones work against a stable artifact contract.

### Tasks

**T-M2-1: Create `src/superclaude/commands/forensic.md`**
- YAML frontmatter per Section 5.1 (amended by M0-T7 to include Edit, MultiEdit)
- Usage section per Section 5.2
- All flag definitions per amended Section 5.3 (concurrency default: 5; `--auto-relax-threshold` from P-016; `--no-redact` from P-020)
- Examples section per Section 5.4
- Activation section: `Skill sc:forensic-protocol` (mandatory, non-negotiable)
- Boundaries section per Section 5.6
- Related Commands section per Section 5.7
- Pattern reference: `src/superclaude/commands/cleanup-audit.md` for structure and `src/superclaude/commands/adversarial.md` for the activation/boundaries pattern

**T-M2-2: Create `src/superclaude/skills/sc-forensic-protocol/SKILL.md` (shell)**
- YAML frontmatter per amended Section 6.1
- Trigger conditions (invoked only by `sc:forensic` command)
- Purpose and identity section
- Section stubs for each of the 8 protocol sections (to be filled in M4-M8):
  - Phase specifications (placeholder)
  - Domain auto-discovery algorithm (placeholder)
  - Agent prompt templates (placeholder)
  - Adversarial integration invocation patterns (placeholder)
  - Model tier decision matrix (from Section 10, amended by M0-T5)
  - Checkpoint/resume protocol (placeholder, to be filled in M3)
  - Orchestrator token budget rules (from amended Section 4.3/4.4)
  - Output templates (placeholder)
- Skill dependencies per Section 6.3
- Agent dependencies per Section 6.4
- Pattern reference: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` for overall SKILL.md structure

**T-M2-3: Create schema reference document `src/superclaude/skills/sc-forensic-protocol/schemas.md`**
- All 9 data schemas from Section 9 (amended by M0 to include target_root, domain_id, new-tests-manifest, tier tracking):
  - 9.1 StructuralInventorySchema
  - 9.2 DependencyGraphSchema
  - 9.3 RiskSurfaceSchema (amended by M1-T11 for overall_risk_score method)
  - 9.4 InvestigationDomainsSchema (amended: minItems:1, domain_id, target_roots)
  - 9.5 HypothesisFindingSchema (amended: updated ID pattern)
  - 9.6 FixProposalSchema (amended: uniqueItems on tier, "up to three tiers")
  - 9.7 ChangesManifestSchema (amended: target_root, updated hypothesis_id format)
  - 9.7b NewTestsManifestSchema (new, from M0-T4)
  - 9.8 ProgressSchema (amended: target_paths required, flags required, git_head_or_snapshot optional, skipped_phases, budget_status, tier tracking)
- Pattern reference: existing schemas in cleanup-audit-protocol for how schemas are formatted in skills

**T-M2-4: Create `src/superclaude/skills/sc-forensic-protocol/rules/` directory structure**
- Create directory placeholders consistent with cleanup-audit-protocol pattern (rules/ for phase-specific operational rules)
- `rules/phase-0-recon.md` — stub
- `rules/phase-1-discovery.md` — stub
- `rules/phase-2-3b-adversarial.md` — stub
- `rules/phase-3-fix-proposals.md` — stub
- `rules/phase-4-implementation.md` — stub
- `rules/phase-5-validation.md` — stub
- `rules/phase-6-report.md` — stub

**T-M2-5: Validate file placement and `make sync-dev`**
- Verify new files follow the src/superclaude/ canonical source pattern
- Run `make sync-dev` to copy src/superclaude/skills/ → .claude/skills/ and src/superclaude/commands/ → .claude/commands/
- Run `make verify-sync` to confirm both sides match

### Acceptance Criteria (M2)

- [ ] `src/superclaude/commands/forensic.md` exists with all sections, valid YAML frontmatter, correct flag set
- [ ] `src/superclaude/skills/sc-forensic-protocol/SKILL.md` exists with all section stubs
- [ ] `src/superclaude/skills/sc-forensic-protocol/schemas.md` exists with all 9 schemas including M0 amendments
- [ ] `rules/` directory exists with 7 phase stub files
- [ ] `make verify-sync` passes cleanly

---

## M3 — Checkpoint and Resume Protocol

**Effort**: S (3-4 days)
**Depends on**: M2 (SKILL.md shell must exist)
**Blocks**: M4+ (every phase writes checkpoints; protocol must exist before phase implementation)

The checkpoint/resume protocol underpins the entire pipeline's resilience. It must be implemented before any phase-specific code, because each subsequent milestone must write conforming checkpoint updates.

### Tasks

**T-M3-1: Implement `progress.json` schema and writer in SKILL.md**
- Fill in the checkpoint/resume protocol section of `SKILL.md` (previously a stub from M2)
- Define `progress.json` structure (fully amended by M0-T3, M1-T3, M1-T7, M1-T13):
  - Required: `current_phase`, `completed_phases`, `started_at`, `last_checkpoint`, `target_paths`, `flags`
  - Optional: `git_head_or_snapshot`, `skipped_phases`, `investigation_domains`, `surviving_hypotheses`, `greenlit_fixes`
  - Per-phase: `budget_status` objects, agent tier tracking objects
- Define checkpoint write protocol: checkpoint is written at the completion of every phase (never mid-phase)
- Define atomic write pattern: write to `.progress.json.tmp`, then rename to `progress.json`

**T-M3-2: Implement resume logic in SKILL.md**
- Define resume validation steps (invoked when `--resume <path>` is passed):
  1. Verify `progress.json` exists at specified path
  2. Load `target_paths` and verify all paths still exist and are readable
  3. Load `flags` and compare with current invocation flags; warn on divergence
  4. Optionally load `git_head_or_snapshot` and compare with current HEAD; warn if different
  5. Identify `completed_phases` and `skipped_phases`
  6. Determine first phase to execute: lowest integer not in `completed_phases` and not in `skipped_phases`
  7. Skip all phases before resume point; read their artifacts from disk
- Define resume error cases: missing progress.json, unreadable target paths, corrupted artifacts

**T-M3-3: Define artifact directory tree in SKILL.md**
- Specify output directory structure per amended Section 12.1:
  ```
  <output>/
    progress.json
    phase-0/
      structural-inventory.json
      dependency-graph.json
      risk-surface.json
      investigation-domains.json
    phase-1/
      findings-domain-{N}.md  (N = domain display_index)
    phase-2/
      adversarial/
        debate-transcript.md
        base-selection.md
    phase-3/
      fix-proposal-H-{id}-{seq}.md
    phase-3b/
      fix-selection.md
    phase-4/
      baseline-test-results.md
      changes-manifest.json
      new-tests-manifest.json
    phase-5/
      lint-results.txt
      test-results.md
      self-review.md
    phase-6/
      final-report.md
  ```
- Specify path resolution: all artifact paths are relative to `<output>/`

**T-M3-4: Implement `--clean` guard clause behavior in SKILL.md**
- Per P-019 (M1-T14): `--clean` only executes if all phases are in `completed_phases`
- If pipeline incomplete: emit warning, skip cleanup, retain artifacts
- If pipeline complete: remove all phase artifact directories; retain only `final-report.md` and `progress.json`

**T-M3-5: Write unit tests for checkpoint/resume logic**
- Test: progress.json round-trip (write + read + verify all fields)
- Test: resume from each phase (phases 0-5 interrupted, resume correctly identifies next phase)
- Test: `skipped_phases` distinguishes intentionally skipped from not-yet-executed
- Test: stale target detection (target_paths differ between original run and resume)
- Test: domain ID stability (same inputs → same domain IDs across separate Phase 0 runs)
- Location: `tests/forensic/test_checkpoint.py`

### Acceptance Criteria (M3)

- [ ] `progress.json` schema is fully specified in SKILL.md matching all M0/M1 amendments
- [ ] Resume validation logic is defined with all 7 steps and error cases
- [ ] Artifact directory tree is defined with all phase subdirectories and file paths
- [ ] `--clean` guard clause behavior is specified
- [ ] Checkpoint unit tests pass: `uv run pytest tests/forensic/test_checkpoint.py`

---

## M4 — Phase 0: Reconnaissance Agents

**Effort**: M (1 week)
**Depends on**: M3 (checkpoint protocol must be stable)
**Blocks**: M5 (Phase 1 consumes Phase 0 output)

### Tasks

**T-M4-1: Implement Agent 0a (Structural Inventory) in SKILL.md rules/phase-0-recon.md**
- Fill in the Phase 0 agent prompt templates (from amended Section 7.0)
- Agent 0a prompt: structural inventory scan using Glob and Read tools only (no code logic analysis)
- Output: `phase-0/structural-inventory.json` conforming to 9.1 schema (with target_root fields from M0-T8)
- Model tier: Haiku (no Serena/Context7 calls per M1-T10 budget: 0/0)
- MCP activation precondition (from M0-T7)

**T-M4-2: Implement Agent 0b (Dependency Graph) in rules/phase-0-recon.md**
- Agent 0b prompt: dependency graph using Grep and Serena `get_symbols_overview` for hot path detection
- Output: `phase-0/dependency-graph.json` conforming to 9.2 schema (with target_root fields)
- Model tier: Haiku
- Note: Serena calls for Agent 0b are permitted as per the MCP routing table (Section 11) — however the P-022 budget table shows Phase 0 recon at 0 Serena calls. Resolve: Serena `get_symbols_overview` is used only by Agent 0b as specified in FR-003 and remains in the routing table as a Phase 0 MCP tool. The budget cap of 0 in P-022 applies to the generic recon agent template; FR-003 overrides with a specific carve-out for Agent 0b's symbol overview call. Document this resolution in Section 11 advisory note.

**T-M4-3: Implement Agent 0c (Risk Surface Scan) in rules/phase-0-recon.md**
- Agent 0c prompt: pattern-based risk scan using Grep tool
- Output: `phase-0/risk-surface.json` conforming to amended 9.3 schema (overall_risk_score required, calculation method specified per M1-T11)
- Model tier: Haiku (no MCP calls)

**T-M4-4: Implement orchestrator domain generation action in SKILL.md**
- Orchestrator reads 3 Phase 0 JSON summaries (never source code)
- Produces `phase-0/investigation-domains.json` conforming to amended 9.4 schema
- Applies adaptive domain count heuristic from M0-T6 (1-10 domains)
- Incorporates `--focus` hints as supplementary domains
- Generates deterministic `domain_id` hash per M0-T3
- Token budget: soft 500 / hard 750 per M1-T7; overflow action: truncate domain descriptions
- Writes Phase 0 checkpoint to `progress.json`

**T-M4-5: Write Phase 0 integration tests**
- Test: parallel agent execution (3 agents spawn simultaneously, all produce valid output)
- Test: domain ID determinism (two runs with same target produce identical domain IDs)
- Test: single-file target produces 1 domain (adaptive heuristic edge case)
- Test: `--focus` hints appear in generated domains
- Test: token budget overflow action triggers correctly with oversized input
- Location: `tests/forensic/test_phase0.py`
- Use mock agent responses (no real LLM calls in unit tests)

### Acceptance Criteria (M4)

- [ ] All three Phase 0 agent prompt templates are fully specified in SKILL.md
- [ ] Orchestrator domain generation action is specified with token budget enforcement
- [ ] Domain count heuristic handles all 4 file-count ranges
- [ ] `phase-0/investigation-domains.json` schema includes `domain_id`, `display_index`, `target_roots`
- [ ] Phase 0 tests pass: `uv run pytest tests/forensic/test_phase0.py`

---

## M5 — Phase 1 (Root-Cause Discovery) and Phase 3 (Fix Proposals)

**Effort**: L (1.5 weeks)
**Depends on**: M4 (Phase 1 consumes investigation-domains.json from Phase 0)
**Blocks**: M6 (adversarial phases consume Phase 1 and Phase 3 outputs)

Phase 1 and Phase 3 are grouped because they share the same architectural pattern (parallel Sonnet agents, one per unit of work, using Serena + Context7), and Phase 3 depends only on Phase 2 output which itself depends on Phase 1. The adversarial invocations (Phases 2 and 3b) are M6's responsibility.

### Tasks

**T-M5-1: Implement Phase 1 investigation agent template in rules/phase-1-discovery.md**
- Fill in investigation agent prompt template (from Section 7.1, amended by M0-T7 for MCP precondition and M1-T10 for per-agent MCP budget)
- Agent receives: domain definition, structural-inventory.json (read-only), dependency-graph.json (read-only)
- Output: `phase-1/findings-domain-{display_index}.md` conforming to amended 9.5 schema
  - Hypothesis IDs use hash-based format: `H-{domain_id_short}-{sequence}`
  - Evidence entries include `target_root`
- Model tier: Sonnet if risk_score >= 0.7; Haiku otherwise (per FR-010)
- MCP budget: Serena 3 calls max, Context7 1 call max, Sequential 0 calls (per M1-T10)

**T-M5-2: Implement Phase 1 orchestrator collection action in SKILL.md**
- After all domain agents complete, orchestrator collects finding file paths (not contents)
- Records file paths in progress checkpoint
- Token budget: soft 1,000 / hard 1,500; overflow: list file paths only, omit summaries
- Writes Phase 1 checkpoint

**T-M5-3: Implement Phase 3 fix-proposal agent template in rules/phase-3-fix-proposals.md**
- Fill in fix proposal agent prompt template (from Section 7.3, amended by M0-T7, M1-T10, M1-T12)
- Agent receives: one hypothesis cluster (H-ID, summary, evidence, severity)
- Output: `phase-3/fix-proposal-{H-domain_id_short}-{seq}.md` conforming to amended 9.6 schema
  - `fix_options` array with `uniqueItems: true` on `tier`
  - "up to three tiers" (not mandatory three)
  - `test_requirements` array with at least one entry
- Uses Serena `find_referencing_symbols` for impact tracing (2 calls max)
- Uses Context7 for idiomatic patterns (2 calls max)
- Model tier: Sonnet (per Section 10)

**T-M5-4: Implement Phase 3 orchestrator collection action in SKILL.md**
- After all fix-proposal agents complete, orchestrator collects proposal file paths
- Applies `--fix-tier` fallback logic from M1-T12: if requested tier absent, select next-lower available tier
- Writes Phase 3 checkpoint

**T-M5-5: Implement parallel agent dispatch pattern in SKILL.md**
- Define fan-out/fan-in orchestration: orchestrator divides domains → spawns N parallel agents (bounded by `--concurrency`, default 5) → agents write to disk → orchestrator reads paths
- Define wave batching: if discovered domains > concurrency limit, dispatch in waves
- Reuse pattern from sc-cleanup-audit-protocol behavioral flow

**T-M5-6: Write Phase 1 and Phase 3 tests**
- Test: Phase 1 produces one findings file per domain
- Test: Hypothesis IDs conform to hash-based pattern `H-[a-f0-9]{8}-\d+`
- Test: Phase 3 produces one fix-proposal per surviving hypothesis
- Test: Fix tier uniqueness constraint enforced (no duplicate tier values)
- Test: Fix tier fallback when requested tier absent
- Test: Concurrency batching when domain count > concurrency limit
- Location: `tests/forensic/test_phase1.py`, `tests/forensic/test_phase3.py`

### Acceptance Criteria (M5)

- [ ] Phase 1 agent template specifies all required input, output, MCP budget constraints
- [ ] Hypothesis ID format matches amended schema pattern
- [ ] Phase 3 agent template specifies all required input, output, MCP budget constraints
- [ ] Fix tier uniqueness constraint is enforced in template instructions
- [ ] Parallel dispatch pattern is defined in SKILL.md
- [ ] Phase 1 tests pass: `uv run pytest tests/forensic/test_phase1.py`
- [ ] Phase 3 tests pass: `uv run pytest tests/forensic/test_phase3.py`

---

## M6 — Adversarial Integration (Phases 2 and 3b)

**Effort**: M (1 week)
**Depends on**: M5 (Phase 1 output feeds Phase 2; Phase 3 output feeds Phase 3b); `/sc:adversarial` command must be operational
**Blocks**: M7 (Phase 4 consumes Phase 3b output)

This milestone implements the delegation to the existing `/sc:adversarial` command for both adversarial debate phases. The critical constraint is that the `/sc:adversarial` command must be working correctly before this milestone can be validated end-to-end.

### Tasks

**T-M6-1: Implement Phase 2 adversarial invocation pattern in rules/phase-2-3b-adversarial.md**
- Fill in Phase 2 invocation specification (from Section 7.2, amended by M1-T4 for depth precedence)
- Invocation: `/sc:adversarial --compare <all findings-domain-N.md files> --depth deep --convergence {threshold} --focus "evidence-quality,reproducibility,severity"`
- Note: depth `deep` is the per-phase default (applies when `--depth` flag was omitted from /sc:forensic invocation); explicit `--depth` overrides this per M1-T4 precedence rule
- Single-domain handling: when domain count is 1 (M0-T6), skip adversarial invocation and pass findings through with full confidence score; add `"debate_status": "single-domain-passthrough"` to checkpoint
- Output: `phase-2/adversarial/debate-transcript.md`, `phase-2/adversarial/base-selection.md` (using amended paths from M0-T2)
- Three-level fallback chain (from M1-T6): retry with `--depth quick` → Sonnet scoring agent → direct passthrough

**T-M6-2: Implement Phase 2 orchestrator hypothesis filtering in SKILL.md**
- Orchestrator reads `phase-2/adversarial/base-selection.md` summary scores only
- Applies confidence threshold filter (`--confidence-threshold`, default 0.7)
- Zero-hypothesis handling per M1-T9:
  - If zero hypotheses survive: emit terminal report with threshold value and filtered count
  - `--auto-relax-threshold` flag auto-retries with threshold × 0.8 (capped at 0.5 minimum)
- Record surviving hypothesis IDs and cluster groupings in progress checkpoint
- Token budget: soft 500 / hard 750; overflow: read top-N by confidence, skip lowest

**T-M6-3: Implement Phase 3b adversarial invocation pattern in rules/phase-2-3b-adversarial.md**
- Fill in Phase 3b invocation specification (from Section 7.4, amended by M1-T5 for canonical path and M1-T4 for depth precedence)
- Invocation: `/sc:adversarial --compare <all fix-proposal-H-N.md files> --depth standard --focus "correctness,risk,side-effects"`
- Note: depth `standard` is the per-phase default; explicit `--depth` overrides
- Output: `phase-3b/fix-selection.md` (amended canonical path from M1-T5)
- Same three-level fallback chain as Phase 2

**T-M6-4: Implement Phase 3b orchestrator fix greenlight decision in SKILL.md**
- Read `phase-3b/fix-selection.md` summary only
- Build implementation plan:
  - For each surviving hypothesis, select fix tier matching `--fix-tier` flag
  - Apply fallback logic: if requested tier absent, select next-lower tier, emit warning (M1-T12)
  - Compute combined risk score
  - Greenlight fixes where confidence > threshold AND risk is acceptable
- Output: ordered list of greenlit fixes with assigned specialist agents (per Section 8.2 agent selection logic)
- Token budget: soft 800 / hard 1,200; overflow: read top-N fixes by composite score, skip lowest
- Write Phase 3b checkpoint; this is the orchestrator's PRIMARY decision point

**T-M6-5: Write Phase 2 and Phase 3b integration tests**
- Test: Phase 2 invocation constructs correct `/sc:adversarial` command string
- Test: single-domain passthrough produces correctly structured checkpoint
- Test: confidence threshold filtering with various thresholds (0.5, 0.7, 0.9)
- Test: zero-hypothesis terminal path produces correct terminal report with threshold/count
- Test: `--auto-relax-threshold` retries with adjusted threshold
- Test: Phase 3b invocation constructs correct `/sc:adversarial` command string
- Test: fix tier selection respects `--fix-tier` flag and fallback logic
- Test: three-level fallback chain (mock adversarial failures)
- Location: `tests/forensic/test_phase2.py`, `tests/forensic/test_phase3b.py`

### Acceptance Criteria (M6)

- [ ] Phase 2 invocation pattern is fully specified including depth precedence, single-domain handling, and fallback chain
- [ ] Phase 2 orchestrator filtering is specified with zero-hypothesis terminal path
- [ ] Phase 3b canonical path is `phase-3b/fix-selection.md` throughout
- [ ] Phase 3b fix greenlight decision is specified as the orchestrator's primary decision point
- [ ] All adversarial invocations preserve the orchestrator no-source-read constraint
- [ ] Phase 2 tests pass: `uv run pytest tests/forensic/test_phase2.py`
- [ ] Phase 3b tests pass: `uv run pytest tests/forensic/test_phase3b.py`

---

## M7 — Implementation and Validation Pipeline (Phases 4-5)

**Effort**: L (1.5 weeks)
**Depends on**: M6 (Phase 4 consumes Phase 3b fix-selection)
**Blocks**: M8 (Phase 6 consumes Phase 5 validation artifacts)

Phases 4 and 5 are grouped because they form the implementation execution pair. The baseline test artifact (P-017) is implemented at the start of Phase 4, before any code changes, which is a prerequisite for Phase 5's diff-based failure analysis.

### Tasks

**T-M7-1: Implement Phase 4 baseline test capture in rules/phase-4-implementation.md**
- Before any code modifications, Agent 4 (or a new pre-implementation agent) runs the full test suite
- Command: `uv run pytest {test_dirs} -v --tb=short > phase-4/baseline-test-results.md`
- Output: `phase-4/baseline-test-results.md` (required artifact per M1-T1)
- This artifact feeds Phase 5 Agent 5b's `introduced_failures` vs `preexisting_failures` computation

**T-M7-2: Implement Agent 4a (code fix specialist) in rules/phase-4-implementation.md**
- Fill in implementation agent prompt template (from Section 7.5, amended by M0-T7, M1-T10)
- Agent selection logic per amended Section 8.2: Python files → `python-expert`; backend/API → `backend-architect`; frontend → `frontend-architect`; mixed → `python-expert` (default)
- Uses Serena `replace_symbol_body` for surgical symbol-level edits (5 calls max per M1-T10)
- Uses Context7 for idiomatic patterns (2 calls max per M1-T10)
- Receives: `phase-3b/fix-selection.md` (greenlit fixes only)
- Output: `phase-4/changes-manifest.json` conforming to amended 9.7 schema (with target_root, hash-based hypothesis_id)
- Worktree isolation recommendation: document as SHOULD per NFR-008

**T-M7-3: Implement Agent 4b (regression test creator) in rules/phase-4-implementation.md**
- Fill in quality-engineer test creation prompt template
- Runs in parallel with Agent 4a after baseline capture
- Receives: aggregated `test_requirements` from fix proposals
- Uses Context7 for test framework patterns (3 calls max per M1-T10; no Serena calls)
- Output: `phase-4/new-tests-manifest.json` conforming to 9.7b schema (from M0-T4)
- Both positive (fix works) and negative (regression doesn't recur) test cases required

**T-M7-4: Implement Phase 4 post-write redaction pass in SKILL.md**
- Per M1-T8: after Phase 4 writes artifacts, run redaction scan on all new files
- Apply default patterns: AWS keys, GCP keys, password=, secret=, token=, api_key=, PEM blocks
- If `--no-redact`: emit mandatory warning and skip redaction
- Write Phase 4 checkpoint (baseline captured + implementation complete)

**T-M7-5: Implement Agent 5a (lint pass) in rules/phase-5-validation.md**
- Model tier: Haiku
- Command: `uv run ruff check {changed_files_from_changes_manifest}`
- Output: `phase-5/lint-results.txt` (raw lint output + pass/fail summary)
- Runs in parallel with Agents 5b and 5c

**T-M7-6: Implement Agent 5b (test execution and analysis) in rules/phase-5-validation.md**
- Model tier: Sonnet (quality-engineer)
- Command: `uv run pytest {test_dirs} -v --tb=short`
- Analysis: diff against `phase-4/baseline-test-results.md` to compute `introduced_failures` vs `preexisting_failures` (per M1-T1)
- Output: `phase-5/test-results.md` with pass/fail counts, failure analysis, fix correlation, and baseline comparison
- Consumes: `phase-4/changes-manifest.json`, `phase-4/new-tests-manifest.json`

**T-M7-7: Implement Agent 5c (post-implementation self-review) in rules/phase-5-validation.md**
- Model tier: Sonnet (self-review)
- Reads all changes from changes-manifest.json and new-tests-manifest.json
- Verifies against original hypotheses from `phase-2/adversarial/base-selection.md`
- Runs 4 mandatory self-check questions (from Section 7.6)
- Output: `phase-5/self-review.md`

**T-M7-8: Implement Phase 5 post-write redaction pass in SKILL.md**
- Apply same redaction pass as Phase 4 to all new Phase 5 artifacts
- Write Phase 5 checkpoint

**T-M7-9: Determine exit state in SKILL.md after Phase 5**
- Apply exit state model (M1-T2):
  - `success`: 0 introduced failures + 0 lint errors + no regressions in self-review
  - `success_with_risks`: 0 introduced failures + 0 lint errors + residual risks in self-review
  - `failed`: any introduced failures or lint errors or Phase 4 errors
- Record exit state in progress checkpoint; used by Phase 6 final report

**T-M7-10: Write Phase 4 and Phase 5 tests**
- Test: baseline test capture runs before any code modification
- Test: Agent 4a receives only greenlit fixes (not all fixes)
- Test: changes-manifest.json conforms to schema (hash-based hypothesis IDs, target_root)
- Test: new-tests-manifest.json conforms to schema (file_path, test_type, related_hypothesis_ids)
- Test: Agent 5b produces `introduced_failures` count (0 when no regressions)
- Test: Agent 5b distinguishes pre-existing vs introduced failures
- Test: exit state correctly classifies success/success_with_risks/failed
- Test: `--dry-run` skips Phases 4-5, `skipped_phases` contains [4, 5]
- Location: `tests/forensic/test_phase4.py`, `tests/forensic/test_phase5.py`

### Acceptance Criteria (M7)

- [ ] `phase-4/baseline-test-results.md` is captured before any code changes
- [ ] Agent 4a and 4b run in parallel after baseline capture
- [ ] Redaction pass is applied after Phase 4 and Phase 5 artifact writes
- [ ] Agent 5b computes `introduced_failures` by diffing against baseline
- [ ] Exit state model is applied and recorded after Phase 5
- [ ] `--dry-run` flag correctly skips Phases 4-5
- [ ] Phase 4 tests pass: `uv run pytest tests/forensic/test_phase4.py`
- [ ] Phase 5 tests pass: `uv run pytest tests/forensic/test_phase5.py`

---

## M8 — Phase 6: Final Report, Output Templates, and CLI Integration

**Effort**: M (1 week)
**Depends on**: M7 (Phase 6 reads validation artifacts from Phase 5)
**Blocks**: M9 (testing milestone)

### Tasks

**T-M8-1: Implement Phase 6 orchestrator synthesis in rules/phase-6-report.md**
- Fill in Phase 6 specification (from Section 7.7, amended by M1-T7 token budget and M1-T2 exit state)
- Orchestrator reads ONLY summary artifacts (never source code):
  - `phase-0/investigation-domains.json`
  - `phase-2/adversarial/base-selection.md`
  - `phase-3b/fix-selection.md`
  - `phase-5/lint-results.txt`
  - `phase-5/test-results.md`
  - `phase-5/self-review.md`
- Token budget: soft 2,000 / hard 3,000; overflow: omit rejected-hypotheses section
- Model tier: Opus

**T-M8-2: Implement final report output template in SKILL.md**
- Fill in output template section per Section 13 (amended by M0-T5 model tier compliance, M1-T2 exit state, M1-T9 zero-hypothesis handling)
- Required sections:
  - YAML frontmatter (exit_status: success/success_with_risks/failed, pipeline metadata)
  - Ranked Root Causes (with evidence) — or terminal no-findings report if zero hypotheses
  - Rejected Hypotheses (and why) — may be omitted if token overflow triggers
  - Chosen Fixes (and why)
  - Files Changed (from changes-manifest)
  - Test/Lint Results (with introduced vs preexisting failure counts)
  - Model Tier Compliance (requested_tier vs actual_tier per agent, per M0-T5)
  - Residual Risks and Follow-ups (from self-review)
  - Domain Coverage Map
  - Dry-run "Would-Implement" section (present only when `--dry-run` was used, per M1-T3)

**T-M8-3: Implement final report redaction pass in SKILL.md**
- Apply redaction pass to `phase-6/final-report.md` after generation
- Write Phase 6 checkpoint (all phases complete, final exit state recorded)

**T-M8-4: Integrate command into SuperClaude command discovery**
- Verify `forensic.md` appears in command catalog output (`/sc:index`)
- Verify activation pattern matches other sc commands (`Skill sc:forensic-protocol`)
- Verify `make sync-dev` installs `forensic.md` to `.claude/commands/sc/forensic.md`
- Verify `make sync-dev` installs `sc-forensic-protocol/` to `.claude/skills/sc-forensic-protocol/`

**T-M8-5: Write Phase 6 and integration tests**
- Test: final report contains all required sections
- Test: YAML frontmatter includes exit_status field
- Test: dry-run report contains "would-implement" section; omits Files Changed and Test/Lint sections
- Test: terminal no-findings report includes threshold value and filtered count
- Test: Model Tier Compliance section enumerates all agents with requested_tier
- Test: token overflow omits only rejected-hypotheses section (not required sections)
- Location: `tests/forensic/test_phase6.py`

### Acceptance Criteria (M8)

- [ ] Phase 6 reads only the 6 specified summary artifacts (no source code)
- [ ] Final report contains all required sections in spec order
- [ ] YAML frontmatter includes machine-readable exit_status
- [ ] Dry-run report includes "would-implement" section
- [ ] Model Tier Compliance section is present in all reports
- [ ] Command is discoverable via `/sc:index`
- [ ] `make verify-sync` passes after sync
- [ ] Phase 6 tests pass: `uv run pytest tests/forensic/test_phase6.py`

---

## M9 — Testing, Verification, and Documentation

**Effort**: L (1.5 weeks)
**Depends on**: M8 (all implementation milestones must be complete)
**Blocks**: release

### Tasks

**T-M9-1: End-to-end integration test suite**
- Create `tests/forensic/test_e2e.py` with mock agent framework
- E2E test 1: Single-file target → 1 domain → all phases → `success` exit state
- E2E test 2: Multi-root invocation → path provenance in all artifacts
- E2E test 3: Resume from Phase 3 (simulate Phase 0-2 complete, resume at Phase 3)
- E2E test 4: `--dry-run` → Phases 0-3b-6 → `skipped_phases: [4, 5]` in progress.json
- E2E test 5: Zero hypotheses survive → terminal report with threshold/count
- E2E test 6: Adversarial Phase 2 fails → three-level fallback chain executes correctly
- E2E test 7: `--no-redact` flag → artifacts contain mock secret patterns, warning emitted
- E2E test 8: `--concurrency 2` → domain batching with 6 domains (3 waves of 2)

**T-M9-2: Schema validation tests**
- Create `tests/forensic/test_schemas.py`
- Validate each of the 9 schemas against sample JSON/YAML documents (valid and invalid)
- Test: domain_id determinism (same domain_name + files → same hash)
- Test: hypothesis ID format validation (`H-[a-f0-9]{8}-\d+`)
- Test: progress.json with all M0/M1 amendments (target_paths required, flags required, skipped_phases, budget_status)
- Test: new-tests-manifest.json schema against valid/invalid documents
- Test: fix proposal uniqueItems constraint (duplicate tier values rejected)

**T-M9-3: Adversarial integration validation**
- Create `tests/forensic/test_adversarial_integration.py`
- Test: `/sc:adversarial` is invocable from within forensic pipeline (command exists, skill loads)
- Test: Phase 2 passes correct flags to adversarial command
- Test: Phase 3b passes correct flags to adversarial command
- Test: adversarial output artifacts written to correct phase-prefixed paths

**T-M9-4: Command documentation update**
- Update `src/superclaude/commands/README.md` to document `forensic.md`
- Add `/sc:forensic` to the command reference section with examples
- Update `COMMANDS.md` in CLAUDE.md if it lists available commands

**T-M9-5: Skill documentation**
- Add docstring/header to `sc-forensic-protocol/SKILL.md` explaining skill invocation rules (invoked only by `/sc:forensic`, not directly by users)
- Document all 8 rule files in `rules/` with a `rules/README.md`

**T-M9-6: Run full test suite and coverage report**
- Command: `uv run pytest tests/forensic/ -v --cov=superclaude --cov-report=html`
- Minimum coverage target: 80% of logic paths exercised
- All previously passing tests must still pass (regression check)
- Command: `make test` (full suite)

**T-M9-7: `make verify-sync` final pass**
- Run `make sync-dev` to ensure all src/ changes are reflected in .claude/
- Run `make verify-sync` and confirm clean output
- Run `make lint` and `make format` to enforce code quality

### Acceptance Criteria (M9)

- [ ] All 8 E2E test scenarios pass: `uv run pytest tests/forensic/test_e2e.py`
- [ ] All schema validation tests pass: `uv run pytest tests/forensic/test_schemas.py`
- [ ] Adversarial integration tests pass: `uv run pytest tests/forensic/test_adversarial_integration.py`
- [ ] `make test` passes with no regressions against existing test suite
- [ ] Coverage >= 80% for tests/forensic/
- [ ] `make verify-sync` clean
- [ ] `make lint` clean

---

## Dependency Graph Summary

```
M0 (Tier 1-2 Spec Amendments)
  └── M1 (Tier 3-5 Spec Amendments)
        └── M2 (Foundation Files)
              └── M3 (Checkpoint Protocol)
                    └── M4 (Phase 0: Recon)
                          └── M5 (Phase 1 + Phase 3)
                                └── M6 (Adversarial: Phase 2 + 3b)  ← also requires /sc:adversarial operational
                                      └── M7 (Phase 4 + Phase 5)
                                            └── M8 (Phase 6 + CLI Integration)
                                                  └── M9 (Testing + Docs) → RELEASE
```

**External dependency**: `/sc:adversarial` command must be operational before M6 validation tests can run end-to-end. M6 implementation can proceed without it (the invocation patterns are specified), but E2E tests in M9 require a working adversarial command.

---

## Success Criteria (Feature Complete)

The feature is complete when all of the following are satisfied:

| Criterion | Tied to FRs/NFRs | Milestone |
|-----------|------------------|-----------|
| Command file exists and is discoverable | FR-036 through FR-046 | M2 |
| Skill loads without errors | FR-046 | M2 |
| All 9 data schemas are valid YAML | All schema FRs | M2 |
| Checkpoint writes and reads correctly | NFR-003, NFR-006 | M3 |
| Phase 0 produces 3 JSON artifacts + domains file | FR-001 through FR-006 | M4 |
| Domain IDs are deterministic across runs | NFR-007, P-009 | M4 |
| Phase 1 produces one findings file per domain | FR-007 through FR-011 | M5 |
| Phase 3 produces fix proposals with tier uniqueness | FR-017 through FR-020, P-010 | M5 |
| Phase 2 delegates to /sc:adversarial correctly | FR-012 through FR-016 | M6 |
| Phase 3b delegates to /sc:adversarial correctly | FR-021 through FR-024 | M6 |
| Zero-hypothesis terminal path works | P-016 | M6 |
| Baseline test artifact captured before code changes | P-017 | M7 |
| Phase 4 uses specialist agents with Serena edits | FR-025 through FR-029 | M7 |
| Phase 5 validation produces all 3 artifacts | FR-030 through FR-032 | M7 |
| Phase 5 distinguishes introduced vs preexisting failures | P-017, P-018 | M7 |
| Exit state model produces machine-readable status | P-018 | M7/M8 |
| Phase 6 synthesizes final report from summaries only | FR-033 through FR-035 | M8 |
| Redaction pass applied to all artifacts | P-020 | M4-M8 |
| Dry-run mode executes correct phase subset | FR-044, P-003 | M3/M8 |
| Resume works from any completed phase | NFR-003, P-008, P-009 | M3/M9 |
| All 22 proposal amendments incorporated | (all proposals) | M0/M1 |
| Full test suite passes | NFR tests | M9 |

---

## Estimated Schedule

| Milestone | Effort | Calendar Week |
|-----------|--------|---------------|
| M0 | M (1 week) | Week 1 |
| M1 | M (1 week) | Week 2 |
| M2 | M (1 week) | Week 3 |
| M3 | S (3-4 days) | Week 4 (first half) |
| M4 | M (1 week) | Week 4-5 |
| M5 | L (1.5 weeks) | Week 5-6 |
| M6 | M (1 week) | Week 7 |
| M7 | L (1.5 weeks) | Week 8-9 |
| M8 | M (1 week) | Week 10 |
| M9 | L (1.5 weeks) | Week 11-12 |
| **Total** | **XL** | **~12 weeks** |

---

## Related Artifacts

| Artifact | Location |
|----------|----------|
| Technical specification | `.dev/releases/backlog/forensic/forensic-spec.md` |
| Proposal verdicts (22 proposals) | `.dev/releases/backlog/forensic/proposal-verdicts.md` |
| Risk register | `.dev/releases/backlog/forensic/roadmap/risk-register.md` |
| Dependency graph | `.dev/releases/backlog/forensic/roadmap/dependency-graph.md` |
| Spec amendments checklist | `.dev/releases/backlog/forensic/roadmap/spec-amendments-checklist.md` |
