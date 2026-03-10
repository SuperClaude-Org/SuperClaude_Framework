# Adversarial Verdict Summary — /sc:forensic Spec Proposals

**Consolidation Date**: 2026-02-26
**Source Files**:
- `/adversarial-output/group-A/verdicts.md` (Schema & Data Integrity, 6 proposals)
- `/adversarial-output/group-B/verdicts.md` (Architecture & Feasibility, 6 proposals)
- `/adversarial-output/group-C/verdicts.md` (Phase Contracts & Consistency, 5 proposals)
- `/adversarial-output/group-D/verdicts.md` (Quality Gates, Security & Edge Cases, 5 proposals)

---

## Executive Summary

- **Total proposals**: 22
- **ACCEPT**: 14 | **MODIFY**: 8 | **REJECT**: 0
- **Average convergence**: 0.95 (all groups exceeded the 0.80 threshold)
- **Convergence by group**: A: 0.93 | B: 1.00 | C: 0.97 | D: 0.91

**Cross-cutting theme**: Every group independently surfaced the same systemic tension — the spec contains aspirational or normative statements that have no enforcement mechanism, no artifact contract, or no fallback path when the stated behavior cannot be achieved. Group A found schema gaps (no contract between agents). Group B found runtime enforceability gaps (token budgets, model tiers, MCP scheduling). Group C found path and editorial contract gaps (inconsistent paths, normativity split across sections). Group D found behavioral completeness gaps (undefined terminal states, missing baseline artifacts, no secret redaction pass). The unifying resolution pattern across all 22 proposals is the same: replace aspirational language with deterministic contracts, observable fields, and explicitly-specified fallback behavior.

---

## Verdict Matrix (all 22 proposals, sorted by original proposal number)

| # | Title | Group | Verdict | Score | Modification Summary (if MODIFY) |
|---|-------|-------|---------|-------|----------------------------------|
| P-001 | Move panel additions into normative sections | C | **ACCEPT** | 7.75/10 | Process constraint: integration must be mechanical (verbatim move, adjust numbering only) |
| P-002 | Resolve `--depth` semantic conflict | C | **ACCEPT** | 8.30/10 | — |
| P-003 | Normalize dry-run behavior and final report semantics | C | **MODIFY** | 8.40/10 | Replace `skipped_by_mode` per-phase status with `skipped_phases` array in `progress.json` |
| P-004 | Fix artifact path inconsistencies for adversarial outputs | C | **ACCEPT** | 10.00/10 | — |
| P-005 | Correct Phase 3b output location contract | C | **MODIFY** | 8.05/10 | Use `phase-3b/fix-selection.md`; add directory to Section 12.1 tree; remove migration fallback |
| P-006 | Add missing schema for `new-tests-manifest.json` | A | **ACCEPT** | 0.95/1.00 | — |
| P-007 | Align Risk Surface schema with prompts and requirements | A | **MODIFY** | 0.70/1.00 | Accept `overall_risk_score` alignment only; reject `secrets_exposure` category (no FR, weak evidence, oracle testing gap) |
| P-008 | Strengthen `progress.json` for reproducibility and resume safety | A | **MODIFY** | 0.60/1.00 | Accept 3 of 5 fields: `target_paths` (required), `flags` (promote to required), `git_head_or_snapshot` (optional); defer `spec_version`, `run_id`; reject `phase_status_map` |
| P-009 | Make domain IDs stable across retries/resume | A | **ACCEPT** | 0.92/1.00 | — |
| P-010 | Enforce exactly three fix tiers with uniqueness constraints | A | **MODIFY** | 0.67/1.00 | Accept uniqueness constraint only; reject `minItems: 3`; add orchestrator `--fix-tier` fallback logic; update FR-018 text |
| P-011 | Remove orchestrator-source-read fallback contradiction | B | **ACCEPT** | 8.66/10 | — |
| P-012 | Convert hard token ceilings to enforceable policy with overflow behavior | B | **MODIFY** | 8.71/10 | Implement as static per-phase rules (SHOULD soft target + MUST hard stop + deterministic overflow action), not runtime monitoring |
| P-013 | Add capability fallback for model-tier assignment | B | **ACCEPT** | 9.33/10 | — |
| P-014 | Reconcile MCP tool assumptions with executable tool contract | B | **ACCEPT** | 9.06/10 | — |
| P-015 | Resolve minimum-domain rule for tiny targets | B | **ACCEPT** | 9.10/10 | — |
| P-016 | Deterministic handling when zero hypotheses survive | D | **ACCEPT** | 8.03/10 | Add filtered-count and original threshold value to no-findings terminal report |
| P-017 | Add baseline test artifact to normative phase contracts | D | **ACCEPT** | 8.88/10 | — |
| P-018 | Define pass/fail exit criteria for pipeline completion | D | **ACCEPT** | 8.70/10 | Add explicit state boundary conditions; add `--dry-run` exit semantics |
| P-019 | Clarify resume behavior with `--clean` and artifact lifecycle | D | **MODIFY** | 5.53/10 | Reject `--clean=archive|delete` variant; add single guard-clause sentence to FR-052 only |
| P-020 | Redact sensitive data across all exported artifacts | D | **ACCEPT** | 8.15/10 | Pipeline-level post-processing (not per-agent prompting); fixed default pattern set; defer `--redaction-config` |
| P-021 | Add multi-root path provenance to schemas | A | **ACCEPT** | 0.87/1.00 | — |
| P-022 | Specify scheduler behavior for MCP concurrency caps | B | **MODIFY** | 8.03/10 | Reject full scheduler; replace with per-phase prompt-based MCP access budgets + reduce `--concurrency` default from 10 to 5 |

---

## Detailed Verdicts by Group

---

### Group A: Schema & Data Integrity

**Protocol**: `/sc:adversarial` Mode B (independent assessments)
**Agents**: 3 (architect, analyzer, QA)
**Depth**: standard (2 debate rounds)
**Convergence target**: 0.80
**Focus dimensions**: necessity, proportionality, testability
**Overall convergence**: 0.93 (exceeds 0.80 threshold)

#### Scoring Methodology (Group A)

Group A uses a 0.0–1.0 composite score derived from three agent perspectives:
- **Necessity** (Architect): Is the gap an actual blocker or risk?
- **Proportionality** (Analyzer): Is the fix sized correctly relative to the problem?
- **Testability** (QA): Can the requirement be validated automatically?

Verdicts: ACCEPT ≥ 0.85 composite | MODIFY 0.60–0.84 | REJECT < 0.60

#### Debate Summary

**Round 1**: All three agents independently assessed the 6 proposals. Initial agreement was high on P-006, P-009, and P-021 (unanimous ACCEPT). Divergence appeared on P-007, P-008, and P-010, where all three agents reached MODIFY but with slightly different scoping.

**Round 2**: Agents debated the MODIFY boundaries:
- **P-007**: All agents agreed that `secrets_exposure` lacks sufficient evidence (no FR, weak panel reference, oracle testing problem). Converged on accepting only the `overall_risk_score` alignment.
- **P-008**: Architect pushed for `git_head_or_snapshot` as optional rather than required. Analyzer concurred (non-git codebases exist). QA confirmed the test scenario works with an optional field. Converged on: `target_paths` required, `git_head_or_snapshot` optional, `flags` promoted to required.
- **P-010**: All agents agreed on uniqueness constraint. Architect and QA both independently identified the "filler tier" problem. Converged on: uniqueness + orchestrator fallback, reject "exactly 3."

---

#### PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.95 | Implementation blocker: no contract between Agent 4b and 5b |
| Proportionality | Analyzer | 0.95 | ~20 lines YAML prevents integration class bugs |
| Testability | QA | 0.95 | Schema validation + cross-reference integrity |
| **Composite** | | **0.95** | |

**VERDICT: ACCEPT** | Convergence: 1.00 (unanimous)

**Rationale**: Unanimous across all three perspectives. The gap is unambiguous (every other mandatory artifact has a schema; this one does not). The fix is small, the risk of omission is high, and the result is fully testable. No debate required.

**Implementation guidance**: Define schema in Section 9 (new Section 9.7b or renumber). Required fields: `file_path` (string), `test_type` (enum: unit/integration/e2e), `related_hypothesis_ids` (array of hypothesis ID strings), `status` (enum: new/modified). Optional: `scenario_tags` (array of strings).

---

#### PROPOSAL-007: Align Risk Surface schema with prompts and requirements

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.75 | risk_score gap is blocking; secrets_exposure is speculative |
| Proportionality | Analyzer | 0.70 | Mixed: one small fix + one disproportionate expansion |
| Testability | QA | 0.65 | risk_score testable; secrets detection has oracle problem |
| **Composite** | | **0.70** | |

**VERDICT: MODIFY** | Convergence: 0.93

**Accept**:
- Align Agent 0c prompt to require `overall_risk_score` computation (already `required` in schema Section 9.3)
- Specify calculation method: weighted average of category `risk_score` values
- Update FR-004 language to explicitly mention `overall_risk_score` as a required output

**Reject**:
- `secrets_exposure` category addition. Three independent deficiencies identified:
  1. No functional requirement drives it (architect: no FR)
  2. Evidence is a vague panel reference without section citation (analyzer: weak evidence)
  3. Correct detection requires oracle test fixtures that do not exist (QA: untestable)

**Deferred**: `secrets_exposure` may be added in a future iteration when backed by a formal FR and accompanied by a test fixture corpus.

---

#### PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.60 | Resume works without most fields; edge-case hardening |
| Proportionality | Analyzer | 0.55 | 5 fields is over-engineered; 2-3 suffice |
| Testability | QA | 0.65 | 3 fields enable high-value test scenarios; others are noise |
| **Composite** | | **0.60** | |

**VERDICT: MODIFY** | Convergence: 0.90

**Accept** (3 fields):

| Field | Disposition | Rationale |
|-------|-------------|-----------|
| `target_paths` | Add as **required** | Enables stale-target detection on resume. All 3 agents agreed. |
| `flags` | Promote to **required** | Resume logic (Section 12.3 step 6) already depends on it. Formalizes existing dependency. |
| `git_head_or_snapshot` | Add as **optional** | Enables stale-codebase detection. Optional because spec does not mandate git as target. |

**Reject** (3 fields):

| Field | Disposition | Rationale |
|-------|-------------|-----------|
| `spec_version` | Defer to post-v1.0 | No version exists yet. YAGNI. (architect + analyzer) |
| `run_id` | Defer to post-v1.0 | Observability, not correctness. Resume logic does not use it. (all 3 agents) |
| `phase_status_map` | Reject | Duplicates `completed_phases` + `current_phase`. No unique information identified. (architect + analyzer) |

**Net schema change**: +2 required fields, +1 optional field (vs. +5 required proposed). This is proportional.

---

#### PROPOSAL-009: Make domain IDs stable across retries/resume

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.90 | Latent bug: index drift breaks all cross-phase references |
| Proportionality | Analyzer | 0.90 | Low-cost fix for severe risk; rigorous evidence chain |
| Testability | QA | 0.95 | Determinism invariant is precise and automatable |
| **Composite** | | **0.92** | |

**VERDICT: ACCEPT** | Convergence: 1.00 (unanimous)

**Rationale**: Strongest consensus proposal. All three agents independently identified the same failure chain: parallel Phase 0 agents produce non-deterministic order, index-based IDs inherit that non-determinism, resume re-runs Phase 0, downstream references break. QA additionally provided a concrete negative test that proves the bug exists under the current design.

**Implementation guidance**:
- Generate `domain_id` as deterministic hash of `(domain_name, sorted(files_in_scope))`.
- Hypothesis IDs become `H-{domain_id_short}-{sequence}` where `domain_id_short` is first 8 characters of hash.
- Retain `display_index` as a separate field for human-readable report ordering.
- Update schemas: Section 9.4 (add `domain_id`), Section 9.5 (update ID pattern), Section 9.6 (hypothesis reference format), Section 9.7 (hypothesis_id format).

---

#### PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.70 | Uniqueness needed; "exactly 3" is over-rigid |
| Proportionality | Analyzer | 0.60 | "Exactly 3" creates token waste and perverse incentives |
| Testability | QA | 0.70 | Uniqueness trivially testable; "exactly 3" quality unverifiable |
| **Composite** | | **0.67** | |

**VERDICT: MODIFY** | Convergence: 0.93

**Accept**:
- Add uniqueness constraint on `tier` values within `fix_options` array. Schema addition: `uniqueItems: true` (by tier field). Prevents duplicate `minimal`/`minimal` entries, which is a clear data integrity bug.

**Reject**:
- Change `minItems` from 1 to 3. Three independent reasons:
  1. Forces filler content when fewer tiers are meaningful (architect: too rigid)
  2. ~500-1000 tokens per proposal wasted on padding, multiplied by N hypotheses (analyzer: disproportionate)
  3. Cannot distinguish genuine tiers from filler in automated tests (QA: creates false positives)

**Add** (not in original proposal):
- Orchestrator `--fix-tier` fallback logic: if requested tier is absent, select next-lower available tier and emit warning to final report. This addresses the root concern (tier selection failure) without constraining the generation side.
- Update FR-018 text from "containing three fix tiers" to "containing up to three fix tiers (minimal, moderate, robust)" to resolve the FR-schema inconsistency.

---

#### PROPOSAL-021: Add multi-root path provenance to schemas

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.85 | Multi-root is a MUST FR; paths ambiguous without provenance |
| Proportionality | Analyzer | 0.85 | Cost of NOT implementing exceeds cost of schema additions |
| Testability | QA | 0.90 | Path resolution is deterministic; round-trip tests are clean |
| **Composite** | | **0.87** | |

**VERDICT: ACCEPT** | Convergence: 1.00 (unanimous)

**Rationale**: FR-036 (MUST priority) explicitly supports multiple target paths. Without path provenance, a core feature is silently broken for any codebase with overlapping relative paths (common in monorepos). All three agents independently concluded that the cost of the schema additions is justified by the severity of the gap.

**Implementation guidance**:
- Add `target_root` (string) to all path-bearing schema records: structural-inventory items (9.1), dependency-graph import chains (9.2), hypothesis evidence entries (9.5), fix change records (9.6), changes-manifest entries (9.7), new-tests-manifest entries (new).
- Add `target_roots` array to top-level metadata in `investigation-domains.json` (9.4) mapping root IDs to absolute paths.
- For single-root invocations, `target_root` defaults to the sole path. No schema overhead for the common case beyond the field presence.
- Normalize: all relative paths are relative to their `target_root`, never to CWD.

---

#### Group A Consolidated Scoring Matrix

| Proposal | Verdict | Necessity | Proportionality | Testability | Composite | Convergence |
|----------|---------|-----------|-----------------|-------------|-----------|-------------|
| P-006 | **ACCEPT** | 0.95 | 0.95 | 0.95 | **0.95** | 1.00 (unanimous) |
| P-007 | **MODIFY** | 0.75 | 0.70 | 0.65 | **0.70** | 0.93 |
| P-008 | **MODIFY** | 0.60 | 0.55 | 0.65 | **0.60** | 0.90 |
| P-009 | **ACCEPT** | 0.90 | 0.90 | 0.95 | **0.92** | 1.00 (unanimous) |
| P-010 | **MODIFY** | 0.70 | 0.60 | 0.70 | **0.67** | 0.93 |
| P-021 | **ACCEPT** | 0.85 | 0.85 | 0.90 | **0.87** | 1.00 (unanimous) |

#### Group A Deferred Items

| Item | Source Proposal | Reason for Deferral | Trigger to Reconsider |
|------|----------------|---------------------|----------------------|
| `secrets_exposure` risk category | P-007 | No FR, weak evidence, oracle testing gap | Formal FR + test fixture corpus |
| `spec_version` field | P-008 | YAGNI for v1.0 | Schema breaking change in v2.0 |
| `run_id` field | P-008 | Observability, not correctness | Observability/debugging sprint |
| `phase_status_map` field | P-008 | Duplicates existing fields | New per-phase metadata requirements |
| "Exactly 3 tiers" constraint | P-010 | Token waste, filler incentives, untestable quality | Evidence that 1-2 tier proposals cause downstream failures |

---

### Group B: Architecture & Feasibility

**Agents**: Architect (A1), DevOps (A2), Performance (A3)
**Depth**: Standard (2 rounds)
**Convergence achieved**: 1.00 (target: 0.80)
**Focus**: architectural-integrity, runtime-feasibility, cost-efficiency

#### Scoring Methodology (Group B)

**Hybrid scoring** combines three weighted dimensions (0-10 scale):
- Architectural Integrity (A1): 35% weight
- Runtime Feasibility (A2): 35% weight
- Cost Efficiency (A3): 30% weight

Verdicts: ACCEPT — weighted score >= 8.0 and no agent scores below 7.0 | MODIFY — weighted score >= 7.0 but at least one agent flags a required change | REJECT — weighted score < 7.0 or any agent scores below 5.0

---

#### PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 7.0 (MODIFY) | 8.5 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 6.5 (MODIFY) | 8.2 (ACCEPT) | 30% |

**Weighted Score**: (9.2 × 0.35) + (8.5 × 0.35) + (8.2 × 0.30) = 3.22 + 2.975 + 2.46 = **8.66** | Convergence: 1.0

**VERDICT: ACCEPT**

**Consensus specification**: Replace the current adversarial-failure fallback with a three-level degradation chain:

1. **Level 1**: Retry adversarial protocol with `--depth quick`
2. **Level 2**: Spawn a single Sonnet scoring agent with 60-second hard timeout and 1,000-token output cap. The agent reads all finding summaries and produces a ranked list by confidence score.
3. **Level 3**: If the scoring agent also fails, emit finding file paths directly in the phase output with metadata `"debate_status": "skipped"`. The orchestrator passes these through to Phase 3 without scoring — all surviving hypotheses proceed to fix proposal generation.

**Spec changes required**:
- Section 14.1: Replace "orchestrator reads all findings and ranks by confidence score directly" with the three-level chain above
- Section 4.3: No change needed (orchestrator constraint preserved)

---

#### PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 7.5 (MODIFY) | 8.8 (MODIFY) | 35% |
| Runtime Feasibility | A2 | 8.8 (ACCEPT) | 8.8 (MODIFY) | 35% |
| Cost Efficiency | A3 | 8.5 (ACCEPT) | 8.5 (ACCEPT) | 30% |

**Weighted Score**: (8.8 × 0.35) + (8.8 × 0.35) + (8.5 × 0.30) = 3.08 + 3.08 + 2.55 = **8.71** | Convergence: 1.0

**VERDICT: MODIFY**

**Modification**: Implement as static per-phase rules in the spec (not runtime token monitoring). Define each phase's budget as a soft target (SHOULD) and hard stop (MUST) with a deterministic truncation action.

**Per-phase overflow policy table** (add to Section 4.3 or new Section 4.4):

| Phase | Context | Soft Target | Hard Stop | Overflow Action |
|-------|---------|-------------|-----------|-----------------|
| Phase 0 synthesis | FR-006 | 500 tokens | 750 tokens | Truncate domain descriptions to single sentence |
| Phase 1 collection | FR-011 | 1,000 tokens | 1,500 tokens | List file paths only; omit finding summaries |
| Phase 2 consumption | FR-016 | 500 tokens | 750 tokens | Read top-N hypotheses by confidence; skip lowest |
| Phase 3b consumption | FR-024 | 800 tokens | 1,200 tokens | Read top-N fixes by composite score; skip lowest |
| Phase 6 synthesis | FR-035 | 2,000 tokens | 3,000 tokens | Omit rejected-hypotheses section from final report |

**Warning artifact**: Each phase emits a `budget_status` field in `progress.json`:
```json
{
  "phase": "phase_0",
  "budget_status": "exceeded",
  "soft_target": 500,
  "hard_stop": 750,
  "overflow_action_taken": "truncate_descriptions"
}
```

**Spec changes required**:
- New Section 4.4 "Token Budget Overflow Policy" with the table above
- Section 12 (Checkpoint): Add `budget_status` to `progress.json` schema
- FR-006, FR-011, FR-016, FR-024, FR-035: Reword as soft targets with reference to overflow policy

---

#### PROPOSAL-013: Add capability fallback for model-tier assignment

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.0 (ACCEPT) | 9.0 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.5 (ACCEPT) | 9.5 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.5 (ACCEPT) | 9.5 (ACCEPT) | 30% |

**Weighted Score**: (9.0 × 0.35) + (9.5 × 0.35) + (9.5 × 0.30) = 3.15 + 3.325 + 2.85 = **9.33** | Convergence: 1.0

**VERDICT: ACCEPT**

**Consensus specification**: Add `requested_tier` and `actual_tier` fields to all phase metadata and agent invocation records.

**Implementation**:
1. Each agent invocation record in `progress.json` includes:
   ```json
   {
     "agent": "investigation-domain-3",
     "requested_tier": "sonnet",
     "actual_tier": "unknown",
     "tier_source": "best-effort"
   }
   ```
2. The `actual_tier` field defaults to `"unknown"` since Claude Code does not currently expose the model used by Task sub-agents. Future runtime improvements may populate this field.
3. The `tier_source` field indicates the enforcement mechanism: `"best-effort"` (prompt hinting), `"verified"` (runtime confirmation), `"overridden"` (user forced a different tier).
4. The final report includes a "Model Tier Compliance" section summarizing requested vs actual tiers across all phases.

**Spec changes required**:
- Section 8 (Agent Specifications): Add `requested_tier` to each agent definition
- Section 9 (Data Schemas): Add tier fields to agent invocation schema
- Section 12 (Checkpoint): Add tier tracking to `progress.json`
- Section 13 (Output Templates): Add tier compliance section to final report template

---

#### PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 8.7 (ACCEPT) | 8.7 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.3 (ACCEPT) | 9.3 (ACCEPT) | 30% |

**Weighted Score**: (8.7 × 0.35) + (9.2 × 0.35) + (9.3 × 0.30) = 3.045 + 3.22 + 2.79 = **9.06** | Convergence: 1.0

**VERDICT: ACCEPT**

**Consensus specification**:

1. **Update `allowed-tools`** in both command (Section 5.1) and skill (Section 6.1) frontmatter:
   ```yaml
   allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill, Edit, MultiEdit
   ```

2. **Add MCP activation precondition** to agent prompt templates (Section 8):
   ```
   PRECONDITION: Before using any MCP tool (Serena, Context7, Sequential),
   invoke ToolSearch to load the required tool. Example:
     ToolSearch("select:mcp__serena__replace_symbol_body")
   If ToolSearch fails, fall back to native tool equivalents:
     - Serena replace_symbol_body -> Edit tool
     - Serena find_referencing_symbols -> Grep tool
     - Context7 -> WebSearch or WebFetch
   ```

3. **Update fallback chain** in Section 14.2 to reference only tools in the `allowed-tools` contract.

**Spec changes required**:
- Section 5.1: Add Edit, MultiEdit to allowed-tools
- Section 6.1: Add Edit, MultiEdit to allowed-tools
- Section 8: Add MCP activation precondition to agent templates
- Section 14.2: Verify all fallback tools are in the allowed-tools list

---

#### PROPOSAL-015: Resolve minimum-domain rule for tiny targets

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.1 (ACCEPT) | 9.1 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.0 (ACCEPT) | 9.0 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 30% |

**Weighted Score**: (9.1 × 0.35) + (9.0 × 0.35) + (9.2 × 0.30) = 3.185 + 3.15 + 2.76 = **9.10** | Convergence: 1.0

**VERDICT: ACCEPT**

**Consensus specification**: Change domain count constraint from `3..10` to `1..10` with adaptive sizing heuristics.

**Domain count heuristic**:

| Source Files | Domain Range | Rationale |
|-------------|-------------|-----------|
| 1-3 files | 1 domain | Single investigation scope sufficient |
| 4-10 files | 1-3 domains | Group by module or concern |
| 11-50 files | 3-7 domains | Standard auto-discovery |
| 51+ files | 5-10 domains | Full-scale investigation |

**Schema change**: Update `investigation-domains.json` schema `minItems` from 3 to 1.

**Downstream impact**: When domain count is 1, Phase 2 adversarial debate operates on a single finding set. The adversarial protocol should handle this gracefully (skip debate, pass through with full confidence score).

**Spec changes required**:
- FR-005: Change "3-10 dynamically discovered domains" to "1-10 dynamically discovered domains"
- Section 9 (Data Schemas): Update `minItems` from 3 to 1
- Section 7.0: Add domain count heuristic table
- Section 7.2: Add single-domain handling (skip adversarial debate when N=1)

---

#### PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 6.8 (MODIFY) | 8.5 (MODIFY) | 35% |
| Runtime Feasibility | A2 | 5.5 (MODIFY) | 8.0 (MODIFY) | 35% |
| Cost Efficiency | A3 | 4.0 (REJECT) | 7.5 (MODIFY) | 30% |

**Weighted Score**: (8.5 × 0.35) + (8.0 × 0.35) + (7.5 × 0.30) = 2.975 + 2.80 + 2.25 = **8.03** | Convergence: 1.0

**VERDICT: MODIFY**

**Modification**: Reject the proposed full scheduler (semaphores, exponential backoff, deterministic queue ordering). Replace with prompt-based MCP access budgets and reduced default concurrency.

**Implementation**:

1. **Reduce default `--concurrency`** from 10 to 5 (Section 5.3).

2. **Add per-phase MCP access budgets** to agent prompt templates (Section 8):

   | Phase | Agent Type | Serena Calls (max) | Context7 Calls (max) | Sequential Calls (max) |
   |-------|-----------|-------------------|---------------------|----------------------|
   | Phase 0 | Recon (Haiku) | 0 | 0 | 0 |
   | Phase 1 | Investigation | 3 per domain | 1 per domain | 0 |
   | Phase 3 | Fix Proposal | 2 per proposal | 2 per proposal | 0 |
   | Phase 4a | Implementation | 5 per fix | 2 per fix | 0 |
   | Phase 4b | Test Creation | 0 | 3 per fix | 0 |

3. **Add advisory note** to Section 11 (MCP Routing Table):
   > MCP access budgets are enforced via agent prompt instructions, not runtime semaphores. Agents exceeding their MCP call budget should fall back to native tool equivalents. The `--concurrency` flag limits parallel agents but does not directly limit MCP call volume; the per-agent budgets provide the secondary constraint.

**Spec changes required**:
- Section 5.3: Change `--concurrency` default from 10 to 5
- Section 8: Add MCP access budget table to agent specification templates
- Section 11: Add advisory note on enforcement mechanism
- Remove any references to runtime scheduler, semaphores, or queue ordering

---

#### Group B Verdict Summary

| Proposal | Verdict | Weighted Score | Pre-Debate Spread | Post-Debate Spread | Convergence |
|----------|---------|---------------|--------------------|--------------------|-------------|
| P-011 | **ACCEPT** | 8.66 | 2.7 (6.5-9.2) | 1.0 (8.2-9.2) | 1.0 |
| P-012 | **MODIFY** | 8.71 | 1.3 (7.5-8.8) | 0.3 (8.5-8.8) | 1.0 |
| P-013 | **ACCEPT** | 9.33 | 0.5 (9.0-9.5) | 0.5 (9.0-9.5) | 1.0 |
| P-014 | **ACCEPT** | 9.06 | 0.6 (8.7-9.3) | 0.6 (8.7-9.3) | 1.0 |
| P-015 | **ACCEPT** | 9.10 | 0.2 (9.0-9.2) | 0.2 (9.0-9.2) | 1.0 |
| P-022 | **MODIFY** | 8.03 | 2.8 (4.0-6.8) | 1.0 (7.5-8.5) | 1.0 |

**Group B aggregate**: 4 ACCEPT, 2 MODIFY, 0 REJECT

---

### Group C: Phase Contracts & Consistency

**Date**: 2026-02-26
**Mode**: Assessment (3 agents, independent perspectives)
**Depth**: Standard (2 debate rounds)
**Convergence Target**: 0.80
**Focus**: contract-clarity, minimalism, resume-safety
**Overall Convergence**: 0.97 (exceeds 0.80 target)

#### Scoring Methodology (Group C)

Scoring dimensions weighted by focus areas:
- **Contract Clarity** (35%): Would two independent implementers produce interoperable artifacts?
- **Minimalism** (30%): Is this the simplest fix that resolves the inconsistency?
- **Resume Safety** (35%): Does this prevent data corruption or non-deterministic resume behavior?

#### Agent Perspectives

| Agent | Perspective | Focus Lens |
|-------|------------|------------|
| Agent 1 | Architect | Contract clarity, interoperability between independent implementers |
| Agent 2 | Refactorer | Simplicity, minimalism, avoidance of unnecessary complexity |
| Agent 3 | Security | Resume safety, data integrity, non-deterministic behavior prevention |

#### Debate Summary

**Round 1 Initial Alignment**:

| Proposal | Agent 1 | Agent 2 | Agent 3 | Initial Agreement |
|----------|---------|---------|---------|-------------------|
| P-001 | ACCEPT | MODIFY | ACCEPT | 2/3 (66%) |
| P-002 | ACCEPT | ACCEPT | ACCEPT | 3/3 (100%) |
| P-004 | ACCEPT | ACCEPT | ACCEPT | 3/3 (100%) |
| P-005 | MODIFY | MODIFY | ACCEPT | 2/3 agree on change needed, disagree on direction |
| P-003 | ACCEPT | MODIFY | ACCEPT | 2/3 (66%) |

**Round 2 Structured Debate**:

**P-001 Debate**: Agent 2 (refactorer) proposed a lighter alternative: add normative cross-references from Section 3/9 to Section 17 rather than full integration. Agent 1 (architect) countered that cross-references create a "follow the pointers" reading burden and two-location maintenance. Agent 3 (security) sided with Agent 1, noting that FR-053 and FR-054 are safety controls that must be unmissable in the normative section. Agent 2 conceded but added a process constraint: the integration must be mechanical (move verbatim, then adjust numbering) to avoid introducing new inconsistencies. Resolution: ACCEPT with process note. All three agents converged.

**P-005 Debate**: Three-way disagreement on directory structure.
- Agent 1 proposed `phase-3b/fix-selection.md` (clean ownership) but without migration fallback.
- Agent 2 proposed keeping `phase-3/fix-selection.md` (no new directory, simpler).
- Agent 3 preferred `phase-3b/` for resume integrity (phase ownership boundaries aid artifact validation).

Agent 1 challenged Agent 2: "If Phase 3 and Phase 3b share a directory, can the resume validator correctly determine which phase produced which artifact?" Agent 2 acknowledged this is a valid concern but argued it can be solved with naming conventions. Agent 3 countered: "Naming conventions are implicit contracts. Directory boundaries are explicit contracts. For resume safety, explicit is better." Agent 2 conceded the point conditionally: accept `phase-3b/` but drop the migration fallback since the spec is draft. Resolution: MODIFY — use `phase-3b/fix-selection.md`, update Section 12.1 directory tree, drop migration fallback. All three agents converged.

**P-003 Debate**: Agent 2 proposed avoiding `skipped_by_mode` status in favor of inferring skip from `flags.dry_run` + absent phases. Agent 3 presented a concrete resume scenario where this fails: a pipeline interrupted mid-Phase 3 also has phases 4-5 absent but `flags.dry_run` is false. The absence of phases 4-5 is ambiguous without an explicit status. Agent 1 supported Agent 3's reasoning: "The checkpoint schema must be self-describing. Relying on inference from flags creates a coupling between the status interpretation and the flag set." Agent 2 proposed a compromise: instead of a new status value, add a `skipped_phases` array to `progress.json`. Agent 3 accepted this as equivalent in integrity value. Agent 1 accepted it as simpler than a per-phase status enum. Resolution: MODIFY — use `skipped_phases` array instead of per-phase `skipped_by_mode` status. All three agents converged.

**Final Convergence by Proposal**:

| Proposal | Final Agreement | Convergence Score |
|----------|----------------|-------------------|
| P-001 | 3/3 ACCEPT (with process note) | 1.00 |
| P-002 | 3/3 ACCEPT | 1.00 |
| P-004 | 3/3 ACCEPT | 1.00 |
| P-005 | 3/3 MODIFY (converged) | 0.93 |
| P-003 | 3/3 MODIFY (converged) | 0.90 |

---

#### PROPOSAL-001: Move panel additions into normative sections

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 6.0 | 0.30 | 1.80 |
| Resume Safety | 8.0 | 0.35 | 2.80 |
| **Composite** | | | **7.75** |

**VERDICT: ACCEPT** | Severity: Critical | Convergence: 1.00

Integrate FR-047 through FR-055, NFR-009, NFR-010, and Schema 9.9 into their canonical normative sections (Sections 3.1, 3.2, 5.3, 7, 9, 12, 14, and Appendix A). Section 17 retains rationale text only, with each original requirement block replaced by a forward reference to its new location.

**Process constraint**: Integration must be mechanical (move content verbatim, adjust numbering) to avoid introducing new inconsistencies during the rewrite.

---

#### PROPOSAL-002: Resolve `--depth` semantic conflict

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 9.0 | 0.30 | 2.70 |
| Resume Safety | 7.0 | 0.35 | 2.45 |
| **Composite** | | | **8.30** |

**VERDICT: ACCEPT** | Severity: Major | Convergence: 1.00

Add the following precedence rule to Section 5.3 (or FR-038):

> `--depth` precedence: circuit-breaker override > explicit `--depth` CLI flag > phase-specific default. Per-phase defaults (Phase 2: `deep`, Phase 3b: `standard`) apply only when `--depth` is omitted from the command.

Update Sections 7.2 and 7.4 invocation patterns to say "default: deep" / "default: standard" rather than hardcoding the depth value.

---

#### PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 10.0 | 0.35 | 3.50 |
| Minimalism | 10.0 | 0.30 | 3.00 |
| Resume Safety | 10.0 | 0.35 | 3.50 |
| **Composite** | | | **10.00** |

**VERDICT: ACCEPT** | Severity: Major | Convergence: 1.00

Standardize all references to adversarial output artifacts to use the `phase-2/` prefix:
- `phase-2/adversarial/base-selection.md`
- `phase-2/adversarial/debate-transcript.md`

Update FR-015, FR-033 (Phase 6 input list), and Section 7.7 to use the full path. No other changes required.

---

#### PROPOSAL-005: Correct Phase 3b output location contract

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 8.0 | 0.35 | 2.80 |
| Minimalism | 7.0 | 0.30 | 2.10 |
| Resume Safety | 9.0 | 0.35 | 3.15 |
| **Composite** | | | **8.05** |

**VERDICT: MODIFY** | Severity: Major | Convergence: 0.93

**Accepted change**: Define canonical path as `phase-3b/fix-selection.md`.

**Required modifications to the proposal**:
1. Add `phase-3b/` directory to the Section 12.1 directory tree.
2. Update Section 7.4, FR-023, FR-024, and FR-033 to reference `phase-3b/fix-selection.md`.
3. **Remove** the migration fallback for legacy paths. The spec is version 1.0.0-draft with no existing implementations. Migration logic adds complexity for a non-existent concern.

**Rationale for `phase-3b/` over `phase-3/`**: Directory boundaries are explicit contracts that aid resume validation. The resume validator can determine phase ownership of artifacts by directory, eliminating ambiguity about which phase produced `fix-selection.md`. This is a net integrity gain that justifies the new directory.

---

#### PROPOSAL-003: Normalize dry-run behavior and final report semantics

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 7.0 | 0.30 | 2.10 |
| Resume Safety | 9.0 | 0.35 | 3.15 |
| **Composite** | | | **8.40** |

**VERDICT: MODIFY** | Severity: Major | Convergence: 0.90

**Accepted changes**:
1. Codify dry-run phase plan: execute Phases 0 -> 1 -> 2 -> 3 -> 3b -> 6; skip Phases 4 and 5.
2. Require "would-implement" section in Phase 6 dry-run report (containing the implementation plan from fix-selection).

**Required modification to the proposal**:
3. Replace `skipped_by_mode` per-phase status with a `skipped_phases` array in `progress.json`. Example:
```json
{
  "completed_phases": [0, 1, 2, 3, "3b", 6],
  "skipped_phases": [4, 5],
  "flags": { "dry_run": true }
}
```
This is self-describing without extending the per-phase status enum. Resume logic can distinguish "skipped intentionally" (present in `skipped_phases`) from "not yet executed" (absent from both `completed_phases` and `skipped_phases`).

---

#### Group C Implementation Priority

| Priority | Proposal | Verdict | Score | Severity |
|----------|----------|---------|-------|----------|
| 1 | P-004 | ACCEPT | 10.00 | Major (runtime file-not-found) |
| 2 | P-003 | MODIFY | 8.40 | Major (resume integrity) |
| 3 | P-002 | ACCEPT | 8.30 | Major (behavioral non-determinism) |
| 4 | P-005 | MODIFY | 8.05 | Major (resume artifact lookup) |
| 5 | P-001 | ACCEPT | 7.75 | Critical (spec authority) |

Note: P-001 is rated Critical severity but scored lowest because it is an editorial/structural fix with no runtime behavior change. Its impact is on implementer interpretation, not system execution. It should still be executed but is lower urgency than the runtime-affecting proposals.

---

### Group D: Quality Gates, Security & Edge Cases

**Adversarial Protocol**: Mode B (independent assessments)
**Agents**: QA (Agent 1), Security (Agent 2), Analyzer (Agent 3)
**Depth**: Standard (2 debate rounds)
**Convergence target**: 0.80
**Focus areas**: quality-assurance, security-adequacy, edge-case-likelihood
**Overall convergence**: 0.91 (exceeds 0.80 target)

#### Scoring Methodology (Group D)

Scoring dimensions (each 0-10, weighted):
- **Quality Impact** (30%): Does this improve pipeline trustworthiness?
- **Security Adequacy** (25%): Is the security posture improved proportionally?
- **Edge Case Likelihood** (20%): How probable is the scenario in real usage?
- **Implementation Cost** (15%): How much spec/code change is required?
- **Proportionality** (10%): Is the solution sized appropriately to the problem?

#### Debate Process

**Round 1 Cross-Assessment Challenges**:

**P-016 divergence**: Agent 1 (MODIFY) vs Agents 2+3 (ACCEPT). Agent 1 argued the `--auto-relax-threshold` flag is over-engineering. Agent 2 countered that explicit opt-in flags are standard security practice for behavior changes. Agent 3 supported Agent 2, noting that 15-25% probability warrants a proper mechanism, not just documentation. Agent 1 conceded that the flag is lightweight and the immutability default is correct — the MODIFY was about CLI cleanliness, not substance.

**P-019 divergence**: Agent 3 (REJECT) vs Agents 1+2 (MODIFY). Agent 3 argued <5% probability does not warrant any spec change beyond documentation. Agent 1 countered that even low-probability scenarios need defined behavior in a spec — undefined behavior is a testing gap. Agent 2 noted the competing security concerns (evidence preservation vs data minimization) but agreed the `archive|delete` variant is disproportionate. Agent 3 softened to MODIFY with the minimal scope: "one-line addition specifying --clean requires successful completion."

**P-020 divergence**: Agent 3 (MODIFY — pipeline-level not per-agent) vs Agents 1+2 (ACCEPT as-proposed). Agent 3 argued per-agent redaction adds prompt complexity and agents cannot reliably self-redact. Agent 2 agreed that post-generation pipeline-level redaction is more reliable than agent-level. Agent 1 agreed that the mechanism matters but the proposal's intent is correct. All three converged on: ACCEPT the proposal's scope (all artifacts), MODIFY the implementation approach (pipeline-level post-processing, not per-agent prompting).

**Round 2 Convergence Refinement**:

**P-016**: All three agents converged on ACCEPT with one modification: the `--auto-relax-threshold` flag is accepted as proposed, but the no-findings terminal report should include the original threshold value and the number of hypotheses that were filtered, so the user can make an informed decision about re-running with a lower threshold. Convergence: 0.93.

**P-017**: No disagreement across any round. All three agents recognized this as a documentation-implementation gap with high probability (60-80%) and minimal fix cost. Convergence: 0.97.

**P-018**: Agents 1 and 2 accepted fully. Agent 3 pushed for boundary definitions between the three states. After debate, all agreed: ACCEPT the three-state model, and add a requirement that the spec must define boundary conditions for each state transition. Convergence: 0.90.

**P-019**: After Round 1, Agent 3 moved from REJECT to MODIFY-minimal. All three converged on: the spec needs a one-sentence clarification that `--clean` is a no-op unless all phases completed successfully. The `archive|delete` variant is rejected as over-engineered. Convergence: 0.87.

**P-020**: All three converged on ACCEPT-with-implementation-modification. The scope (all artifacts) is correct. The mechanism should be pipeline-level post-processing with a default pattern set, not per-agent prompt modification. Configurable patterns deferred to future enhancement. Convergence: 0.90.

---

#### PROPOSAL-016: Deterministic handling when zero hypotheses survive

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 8.5 | Eliminates non-deterministic pipeline behavior |
| Security Adequacy | 8.0 | Prevents silent threshold relaxation on security hypotheses |
| Edge Case Likelihood | 7.5 | 15-25% probability, higher with strict thresholds |
| Implementation Cost | 7.0 | New CLI flag + terminal report path + filter logic changes |
| Proportionality | 8.5 | Well-sized: flag + report section covers the gap |
| **Weighted Total** | **8.03** | |

**VERDICT: ACCEPT** | Convergence: 0.93

Accept as proposed with one addition: the no-findings terminal report must include the original threshold value and the count of hypotheses that were filtered out, enabling informed re-run decisions. The `--auto-relax-threshold` opt-in flag is accepted. Default behavior: threshold is immutable.

---

#### PROPOSAL-017: Add baseline test artifact to normative phase contracts

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 9.5 | Baseline diffing is prerequisite for trustworthy validation |
| Security Adequacy | 7.5 | Forensic evidence value for incident response |
| Edge Case Likelihood | 9.0 | 60-80% of real runs encounter pre-existing failures |
| Implementation Cost | 9.0 | Purely additive: update contracts and artifact tree |
| Proportionality | 9.5 | Minimal cost, maximal quality improvement |
| **Weighted Total** | **8.88** | |

**VERDICT: ACCEPT** | Convergence: 0.97

Accept as proposed. Update the following spec sections:
- Section 7.5 (Phase 4 contract): add `baseline-test-results.md` as required output artifact
- Section 7.6 (Phase 5 contract): require Agent 5b to compute `introduced_failures` vs `preexisting_failures`
- Section 12.1 (artifact tree): add `phase-4/baseline-test-results.md`
- Section 16.2 (quality metrics): update test pass rate metric to reference baseline-diffed results

---

#### PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 9.0 | Machine-readable exit status enables CI integration |
| Security Adequacy | 8.5 | CI security gates require formal exit semantics |
| Edge Case Likelihood | 10.0 | 100% of runs produce no formal exit status today |
| Implementation Cost | 7.0 | Report frontmatter + state mapping logic + boundary definitions |
| Proportionality | 8.0 | Three states are well-calibrated; boundaries need definition |
| **Weighted Total** | **8.70** | |

**VERDICT: ACCEPT** | Convergence: 0.90

Accept the three-state model (`success`, `success_with_risks`, `failed`) with one required addition: the spec must define explicit boundary conditions for each state transition. Specifically:
- `success`: All phases complete, 0 lint errors, 0 introduced test failures, self-review identifies no regressions
- `success_with_risks`: All phases complete, 0 lint errors, 0 introduced test failures, but self-review identifies residual risks or incomplete fixes
- `failed`: Any of: introduced test failures, lint errors in changed files, Phase 4 implementation errors, or pipeline-level errors
- `--dry-run` exits: `success` if Phases 0-3b complete without error, `failed` otherwise (no `success_with_risks` for dry runs since validation was not performed)

Add exit status to final report frontmatter as a machine-readable YAML block.

---

#### PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 5.0 | Prevents rare edge case of orphaned artifacts |
| Security Adequacy | 5.0 | Minor data lifecycle concern, competing interests |
| Edge Case Likelihood | 3.5 | <5% harmful probability |
| Implementation Cost | 9.0 | One-sentence spec clarification (after scope reduction) |
| Proportionality | 7.0 | Reduced scope is well-sized to the actual risk |
| **Weighted Total** | **5.53** | |

**VERDICT: MODIFY** | Convergence: 0.87

Reduce scope significantly. The `--clean=archive|delete` variant is rejected as over-engineered. Instead, add a single clarification to the `--clean` flag definition (FR-052):

> `--clean` SHALL only execute artifact removal after all phases have completed successfully (progress.json shows all phases in completed_phases). If the pipeline did not complete successfully, `--clean` is ignored and a warning is emitted: "Artifacts retained: pipeline did not complete successfully."

No new flag variants. No archive semantics. This addresses the actual risk (accidental evidence destruction on partial runs) with proportionate effort.

---

#### PROPOSAL-020: Redact sensitive data across all exported artifacts

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 8.5 | Testable security posture across all outputs |
| Security Adequacy | 9.5 | Closes primary secret leakage vector |
| Edge Case Likelihood | 6.5 | 0.5-4% harmful exposure, concentrated on legacy repos |
| Implementation Cost | 6.5 | Pipeline-level post-processing + default pattern set |
| Proportionality | 8.0 | Scope correct, implementation refined to pipeline-level |
| **Weighted Total** | **8.15** | |

**VERDICT: ACCEPT** | Convergence: 0.90

Accept the proposal's scope (all persisted artifacts, not just final report) with a refined implementation approach:

1. **Mechanism**: Pipeline-level post-processing, not per-agent prompt modification. After each phase writes its artifacts, a redaction pass scans all new files against the pattern set. This is more reliable than expecting agents to self-redact.
2. **Default patterns**: Ship with a fixed default pattern set covering: AWS keys (`AKIA...`), GCP service account keys, generic `password=`, `secret=`, `token=`, `api_key=` patterns, and PEM private key blocks.
3. **Configurable patterns**: Defer to a future `--redaction-config` flag. The default set covers 80%+ of real-world secrets.
4. **Secure raw retention**: Accept the `--no-redact` flag for security teams that need unredacted artifacts, with a mandatory warning: "WARNING: --no-redact retains sensitive data in intermediate artifacts. Ensure appropriate access controls."
5. **Update scope**: FR-049 is superseded. New requirement covers all artifacts including findings files, debate transcripts, fix proposals, and the final report.

---

#### Group D Verdict Summary

| # | Proposal | Verdict | Score | Convergence |
|---|----------|---------|-------|-------------|
| P-016 | Zero hypotheses handling | ACCEPT | 8.03 | 0.93 |
| P-017 | Baseline test artifact | ACCEPT | 8.88 | 0.97 |
| P-018 | Pass/fail exit criteria | ACCEPT | 8.70 | 0.90 |
| P-019 | --clean artifact lifecycle | MODIFY | 5.53 | 0.87 |
| P-020 | Full artifact redaction | ACCEPT | 8.15 | 0.90 |

**Cross-proposal dependencies within Group D**:
- P-020 partially depends on P-017: baseline test results are also an artifact that needs redaction scanning
- P-018 depends on P-017: the `failed` state definition references "introduced test failures" which requires baseline diffing
- P-019 depends on P-018: `--clean` guard clause references "successful completion" which needs the formal exit state model

---

## Cross-Cutting Findings

### Finding CCF-1: Aspirational vs Enforceable (Groups A, B, D)

The single most pervasive pattern across all four groups: the spec makes normative statements that cannot be enforced within the current Claude Code runtime.

- Group A (P-007): Mandates `overall_risk_score` computation but never specifies the calculation method.
- Group B (P-012): Hard token ceilings stated as MUST but there is no mechanism to monitor or enforce them at runtime.
- Group B (P-013): Model tier assignment (Haiku/Sonnet/Opus) is specified per-agent but Claude Code Task sub-agents do not expose which model was actually used.
- Group B (P-022): Concurrency scheduling for MCP calls requires semaphores that do not exist in the runtime.
- Group D (P-016): Zero-hypothesis terminal behavior is undefined, allowing non-deterministic pipeline termination.
- Group D (P-018): No formal exit status exists, making CI integration impossible.

**Pattern resolution** (consistent across all affected proposals): Replace aspirational MUST with observability hooks (`requested_tier`, `actual_tier`, `budget_status`) and deterministic fallback chains. Every requirement that cannot be enforced at runtime must have an explicit fallback that is enforceable.

### Finding CCF-2: Contract Gaps Between Agents (Groups A, B, C)

Multiple proposals identified points where one agent's output is consumed by another agent with no formal contract between them.

- Group A (P-006): Agent 4b produces `new-tests-manifest.json`; Agent 5b consumes it. No schema existed, creating an integration-class gap.
- Group A (P-009): Phase 0 agents produce `domain_id` values; all subsequent phases reference them. Index-based IDs are non-deterministic on resume, silently breaking all downstream references.
- Group A (P-021): Agents producing path-bearing records do not indicate which `target_root` a path belongs to, making multi-root invocation silently broken.
- Group B (P-014): The `allowed-tools` contract in command/skill frontmatter does not include Edit and MultiEdit, but the fallback chain in Section 14.2 references them.
- Group C (P-004): Adversarial output artifacts are referenced inconsistently across sections (with and without `phase-2/` prefix), creating a file-not-found failure at runtime.
- Group C (P-005): Phase 3b's output artifact has no canonical path, meaning the Phase 6 consumer has no reliable lookup location.

**Pattern resolution**: Every inter-agent artifact must have: (a) a schema in Section 9, (b) a canonical path in Section 12.1, (c) consistent references in every FR that produces or consumes it.

### Finding CCF-3: Editorial Normativity Split (Group C, with implications for all groups)

Group C identified that Section 17 contains normative requirements (FR-047 through FR-055, NFR-009, NFR-010, Schema 9.9) that should be in Sections 3, 5, 7, 9, and 12. This is not merely cosmetic: a spec implementer reading only the normative sections would miss critical requirements (specifically the security-relevant FR-053 and FR-054).

This finding has cross-group implications: Groups A, B, and D all identified requirements that appear to be missing or underspecified in their sections. Some of those apparent gaps may in fact be present but buried in Section 17 or other non-canonical locations.

**Pattern resolution**: P-001 (mechanical integration of Section 17 into normative sections) should be executed before any other spec editing work, to establish the true baseline of what the spec currently requires.

### Finding CCF-4: Resume Safety as a Recurring Weak Point (Groups A, C)

Resume safety (the ability to interrupt and restart the pipeline with correct results) was a dominant concern across multiple groups:

- Group A (P-008): `progress.json` lacks `target_paths`, making it impossible to detect stale targets on resume.
- Group A (P-009): Non-deterministic domain IDs break all cross-phase references on resume.
- Group C (P-003): `progress.json` cannot distinguish "phase skipped by mode" from "phase not yet executed," creating ambiguity for the resume validator.
- Group C (P-005): Phase 3b artifact ambiguity means the resume validator cannot determine whether fix-selection was produced.

All four resume-safety proposals received ACCEPT or MODIFY verdicts. The consistent resolution pattern: `progress.json` must be self-describing — every recoverable state must be explicitly encoded, never inferred from flag combinations or absent entries.

### Finding CCF-5: Security Posture Proportionality (Group D)

Group D reviewed five proposals where security concerns were either understated (P-017, P-018, P-020) or overstated (P-019). The pattern:

- High-probability, low-cost security improvements (P-017, P-018, P-020) received ACCEPT verdicts despite requiring non-trivial spec changes. The baseline test artifact (P-017) is a prerequisite for meaningful security evidence in incident response. The exit state model (P-018) is a prerequisite for CI security gates. The artifact redaction pass (P-020) closes the primary secret leakage vector.
- Low-probability, high-cost security additions (P-019 `archive|delete` variant) were trimmed to a one-sentence guard clause. The underlying risk (accidental evidence destruction) is real but narrow; the proposed solution was disproportionate.

**Pattern**: Security requirements should be proportional to both the probability of the threat and the cost of the control. Broad, low-cost controls (redaction patterns, exit semantics) justify ACCEPT. Narrow, high-cost controls (archive semantics for <5% scenarios) should be reduced to the minimal spec change that addresses the documented risk.

### Finding CCF-6: Fallback Chain Integrity (Group B)

Group B's proposals P-011 and P-014 both revealed fallback chains that reference capabilities that are either architecturally prohibited or contractually unavailable:

- P-011: Section 14.1 fallback specified "orchestrator reads all findings and ranks by confidence score directly" — a violation of the Section 4.3 invariant that the orchestrator does not read source code or agent outputs.
- P-014: Section 14.2 fallback chain references Edit and MultiEdit tools that are not in the `allowed-tools` contract.

**Pattern**: Every fallback path must be verified against: (a) the architectural invariants in Section 4, and (b) the tool contract in the command/skill frontmatter. A fallback that itself fails is worse than no fallback.

---

## Implementation Priority

The following ordering synthesizes priority recommendations from all four groups, incorporating cross-group dependency analysis. Groups used different scoring scales (A: 0-1, B: 0-10, C: 0-10, D: 0-10); Group A scores are normalized for comparison.

### Tier 1 — Structural Prerequisites (must execute before other spec editing)

These proposals must be resolved first because they affect the baseline state of the spec or create cascading dependencies.

| Priority | Proposal | Verdict | Score (normalized) | Reason |
|----------|----------|---------|-------------------|--------|
| 1 | **P-001** | ACCEPT | 7.75/10 | Section 17 normativity split — establishes true spec baseline before any editing |
| 2 | **P-004** | ACCEPT | 10.00/10 | Runtime file-not-found: wrong artifact paths cause immediate Phase 6 failure |
| 3 | **P-009** | ACCEPT | 9.20/10 | Latent resume bug: non-deterministic domain IDs break all cross-phase references |

### Tier 2 — Core Schema & Contract Gaps (implementation blockers)

| Priority | Proposal | Verdict | Score (normalized) | Reason |
|----------|----------|---------|-------------------|--------|
| 4 | **P-013** | ACCEPT | 9.33/10 | Model-tier fallback: unenforceable assumption impacts every phase |
| 5 | **P-015** | ACCEPT | 9.10/10 | Domain minimum rule: spec fails for any target with fewer than 3 files |
| 6 | **P-014** | ACCEPT | 9.06/10 | MCP tool contract: allowed-tools mismatch causes fallback chain failure |
| 7 | **P-006** | ACCEPT | 9.50/10 | Missing schema: no contract between Agent 4b and 5b |
| 8 | **P-021** | ACCEPT | 8.70/10 | Multi-root FR-036 silently broken without path provenance |

### Tier 3 — Behavioral Completeness (correctness and CI readiness)

| Priority | Proposal | Verdict | Score (normalized) | Reason |
|----------|----------|---------|-------------------|--------|
| 9 | **P-017** | ACCEPT | 8.88/10 | Baseline test artifact: prerequisite for P-018 exit state definitions |
| 10 | **P-018** | ACCEPT | 8.70/10 | Exit state model: prerequisite for CI integration and P-019 guard clause |
| 11 | **P-003** | MODIFY | 8.40/10 | Dry-run resume integrity: `skipped_phases` array |
| 12 | **P-002** | ACCEPT | 8.30/10 | `--depth` precedence rule: eliminates behavioral non-determinism |
| 13 | **P-005** | MODIFY | 8.05/10 | Phase 3b canonical path: `phase-3b/fix-selection.md` |

### Tier 4 — Runtime Policy & Error Handling

| Priority | Proposal | Verdict | Score (normalized) | Reason |
|----------|----------|---------|-------------------|--------|
| 14 | **P-011** | ACCEPT | 8.66/10 | Orchestrator fallback chain: three-level degradation |
| 15 | **P-012** | MODIFY | 8.71/10 | Token overflow policy: static per-phase rules with `budget_status` |
| 16 | **P-020** | ACCEPT | 8.15/10 | Artifact-wide redaction: pipeline-level post-processing |
| 17 | **P-016** | ACCEPT | 8.03/10 | Zero hypothesis terminal path: `--auto-relax-threshold` flag |
| 18 | **P-022** | MODIFY | 8.03/10 | MCP concurrency: prompt-based budgets, concurrency default to 5 |

### Tier 5 — Hardening & Proportionate Fixes

| Priority | Proposal | Verdict | Score (normalized) | Reason |
|----------|----------|---------|-------------------|--------|
| 19 | **P-007** | MODIFY | 7.00/10 | Risk surface alignment: `overall_risk_score` only |
| 20 | **P-010** | MODIFY | 6.70/10 | Fix tier uniqueness + orchestrator fallback + FR-018 text update |
| 21 | **P-008** | MODIFY | 6.00/10 | `progress.json` hardening: 3 accepted fields |
| 22 | **P-019** | MODIFY | 5.53/10 | `--clean` guard clause: one-sentence addition to FR-052 |
