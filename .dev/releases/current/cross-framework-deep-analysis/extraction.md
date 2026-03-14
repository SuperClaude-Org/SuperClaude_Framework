---
spec_source: spec-cross-framework-deep-analysis.md
generated: "2026-03-14T00:00:00Z"
generator: requirements-extraction-agent-v1
functional_requirements: 24
nonfunctional_requirements: 6
total_requirements: 30
complexity_score: 0.85
complexity_class: complex
domains_detected: 8
risks_identified: 7
dependencies_identified: 14
success_criteria_count: 18
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 119.0, started_at: "2026-03-14T07:10:07.931170+00:00", finished_at: "2026-03-14T07:12:06.947026+00:00"}
---

## Functional Requirements

**FR-001**: Produce a complete, verified inventory of IronClaude's quality-enforcement layer reflecting the current codebase state using Auggie MCP as the primary discovery mechanism. (Derived from FR-XFDA-001.1)

**FR-002**: Inventory all 8 IronClaude component groups: roadmap pipeline, cleanup-audit CLI, sprint executor, PM agent, adversarial pipeline, task-unified tier system, quality agents, and pipeline analysis subsystem. (FR-XFDA-001.1)

**FR-003**: Each IronClaude component inventory entry must include verified file paths, exposed interfaces, internal dependencies, and extension points — no hallucinated paths permitted. (FR-XFDA-001.1)

**FR-004**: Produce a cross-framework component map with ≥8 IronClaude-to-llm-workflows mappings; components with no llm-workflows counterpart must be explicitly annotated as "IC-only". (FR-XFDA-001.1)

**FR-005**: Produce `inventory-llm-workflows.md` from the known component list in `artifacts/prompt.md` without re-surveying llm-workflows. (FR-XFDA-001.2)

**FR-006**: Run Auggie MCP verification queries against `/config/workspace/llm-workflows` to confirm all file paths from `artifacts/prompt.md` are still valid; flag and annotate any path that no longer exists. (FR-XFDA-001.2)

**FR-007**: Extract per-component strategy documents (design philosophy, execution model, quality enforcement mechanism, error handling strategy, extension points) for all 8 IronClaude component groups. (FR-XFDA-001.3)

**FR-008**: Extract per-component strategy documents for all 11 llm-workflows components from the original prompt, explicitly noting what makes each rigorous AND what makes it bloated/slow/expensive. (FR-XFDA-001.3)

**FR-009**: Enforce the anti-sycophancy rule across all strategy extraction: every "strength" claim must be paired with a documented weakness or trade-off. (FR-XFDA-001.3)

**FR-010**: Back all strategy claims with specific file:line evidence sourced from Auggie MCP results. (FR-XFDA-001.3)

**FR-011**: Run a structured adversarial debate for each of the 8 defined component comparison pairs, producing comparison artifacts with debating positions, evidence, verdict, and confidence score. (FR-XFDA-001.4)

**FR-012**: Each adversarial comparison must cite specific file:line evidence from both repositories and produce a clear verdict identifying which approach is stronger, under what conditions, with the "adopt patterns not mass" constraint verified. (FR-XFDA-001.4)

**FR-013**: Produce `merged-strategy.md` synthesizing all comparison verdicts into a unified best-of-both strategy covering all 8 component areas, with an explicit "rigor without bloat" section and justified discard decisions. (FR-XFDA-001.5)

**FR-014**: The merged strategy must be internally consistent with no contradictions between component sections, and must document the "adopt patterns not mass" principle applied per adopted pattern. (FR-XFDA-001.5)

**FR-015**: Produce per-component improvement plans for all 8 IronClaude component groups, where each item specifies: specific file paths, what to change, why, priority (P0/P1/P2/P3), effort (XS/S/M/L/XL), dependencies, acceptance criteria, and risk assessment. (FR-XFDA-001.6)

**FR-016**: Produce `improve-master.md` containing a dependency graph across all per-component improvement plans. (FR-XFDA-001.6)

**FR-017**: Verify the "adopt patterns not mass" constraint for every improvement item that adopts a llm-workflows pattern; distinguish items adding new code from items strengthening existing code. (FR-XFDA-001.6)

**FR-018**: Adversarially validate the improvement plan for completeness, scope creep (patterns-not-mass violation), missing cross-framework insights, and file path existence via Auggie MCP. (FR-XFDA-001.7)

**FR-019**: Produce `validation-report.md` with pass/fail status per improvement plan item, and `final-improve-plan.md` with all corrections applied. (FR-XFDA-001.7)

**FR-020**: Produce `artifact-index.md` linking all produced artifacts with one-line descriptions, with verified end-to-end traceability from every Phase 1 component through strategy → comparison → merged strategy → improvement plan. (FR-XFDA-001.8)

**FR-021**: Produce `rigor-assessment.md` as a consolidated narrative covering findings, per-component-area verdicts, and overall rigor gap assessment. (FR-XFDA-001.8)

**FR-022**: Produce `improvement-backlog.md` as machine-readable improvement items formatted for direct `/sc:roadmap` consumption, conforming to the defined schema (id, component, title, priority, effort, pattern_source, rationale, file_targets, acceptance_criteria, risk, patterns_not_mass_verified). (FR-XFDA-001.8)

**FR-023**: Produce `sprint-summary.md` containing: findings count, comparison verdicts summary, plan items by priority tier, estimated total effort, and recommended implementation order. (FR-XFDA-001.8)

**FR-024**: Support sprint restart from any phase gate using `--start` and `--end` flags on the CLI executor, enabling phase-range execution without re-running completed phases. (Section 5.1, NFR-XFDA.5)

---

## Non-Functional Requirements

**NFR-001**: All code-reading tasks across all phases must use Auggie MCP as the primary tool, with compliance enforced at every R-RULE-01 checkpoint per phase. (NFR-XFDA.1)

**NFR-002**: The anti-sycophancy rule must achieve 100% coverage — every strength claim in every strategy and comparison artifact must have a paired weakness; enforced via checkpoint scan per phase. (NFR-XFDA.2)

**NFR-003**: All file:line citations across all artifacts must be verifiable via Auggie MCP; 100% of citations verified during Phase 7 adversarial validation. (NFR-XFDA.3)

**NFR-004**: The "adopt patterns not mass" constraint must be verified for 100% of improvement items that adopt a llm-workflows pattern; enforced at Phase 6 and Phase 7 checkpoints. (NFR-XFDA.4)

**NFR-005**: The sprint must be restartable from any phase gate; the `--start` flag on the CLI executor must correctly resume from a given phase when prior gate artifacts exist. (NFR-XFDA.5)

**NFR-006**: `improvement-backlog.md` must be directly consumable by `/sc:roadmap` without schema errors; validated during Phase 8. (NFR-XFDA.6)

---

## Complexity Assessment

**complexity_score**: 0.85  
**complexity_class**: complex

**Scoring Rationale**:

| Factor | Score | Weight | Contribution |
|--------|-------|--------|-------------|
| Multi-phase sequential pipeline with strict gate enforcement (8 phases) | 0.9 | 0.20 | 0.18 |
| Dual-repository analysis requiring Auggie MCP connectivity to two separate workspaces | 0.8 | 0.15 | 0.12 |
| 8 adversarial comparison pairs each requiring file:line evidence from both repos | 0.85 | 0.20 | 0.17 |
| 35+ artifact files produced with dependency graph and traceability requirements | 0.85 | 0.15 | 0.13 |
| Machine-readable schema output consumed by downstream tool (/sc:roadmap) | 0.7 | 0.10 | 0.07 |
| Multiple cross-cutting invariants (anti-sycophancy, patterns-not-mass, evidence-only) enforced across all phases | 0.8 | 0.10 | 0.08 |
| Sprint CLI executor dependency with phase-gate enforcement and resume capability | 0.7 | 0.10 | 0.07 |
| **Total** | | | **0.82** (rounded to 0.85 per spec self-assessment) |

The primary complexity drivers are: the sequential phase dependency chain (no phase can start until its predecessor's gate passes), the requirement for dual-repo Auggie MCP evidence backing every claim, and the adversarial validation layer that re-challenges all upstream work. The project stops short of "enterprise" class because implementation is excluded from scope and the artifact outputs are documents rather than production code.

---

## Architectural Constraints

**AC-001**: Analysis sprint only — no implementation of identified improvements is in scope. All artifacts are documents; no production code changes are permitted.

**AC-002**: Auggie MCP is the mandatory primary tool for all code-reading operations against both `/config/workspace/IronClaude` and `/config/workspace/llm-workflows`. Serena + Grep/Glob are fallback only, and any fallback usage must be noted in the produced artifact.

**AC-003**: llm-workflows is treated as a stable reference only. No llm-workflows files may be modified or its component inventory re-surveyed.

**AC-004**: Sprint execution is strictly sequential by phase; no phase may begin until the prior phase's gate checkpoint passes all criteria.

**AC-005**: Phase gates use `strict_sequential` enforcement with table-based pass/fail per criterion. Sprint halts on any gate failure.

**AC-006**: All artifacts are written to `.dev/releases/current/cross-framework-deep-analysis/artifacts/`. No files are produced outside this directory tree.

**AC-007**: `artifacts/prompt.md` is retained as reference only; it is superseded by this spec and must not be edited.

**AC-008**: The sprint executor CLI interface is `superclaude sprint run <tasklist-index.md> [--start N] [--end N] [--permission-flag "..."]`.

**AC-009**: The "adopt patterns not mass" principle is an R-RULE — a deterministic rule enforced at sprint phase checkpoints, not advisory guidance. Violations halt the sprint.

**AC-010**: `improvement-backlog.md` must conform to the defined schema (id, component, title, priority, effort, pattern_source, rationale, file_targets, acceptance_criteria, risk, patterns_not_mass_verified) — no additional or removed fields permitted.

**AC-011**: IronClaude scope is bounded to 8 quality-enforcement component groups. Commands not related to quality enforcement (brainstorm, design, document, explain, estimate, git, index, load, save, review-translation) are explicitly out of scope.

**AC-012**: Parallelism within phases is permitted only where the spec explicitly authorizes it (Phase 1 inventory queries, Phase 2+3 parallel execution, Phase 6 per-component plans, Phase 8 consolidated outputs).

---

## Risk Inventory

**RISK-001**: **Auggie MCP unavailable for IronClaude repo**
- Severity: High
- Probability: Low
- Impact: Cannot produce evidence-backed inventory; anti-sycophancy and file:line citation NFRs cannot be met
- Mitigation: Fallback to Serena `get_symbols_overview` + Grep/Glob; annotate limitation in affected artifacts; Phase 7 validation will flag unverified citations

**RISK-002**: **Auggie MCP unavailable for llm-workflows repo**
- Severity: High
- Probability: Low
- Impact: Cannot verify llm-workflows file paths or back comparison claims with evidence
- Mitigation: Same fallback as RISK-001; llm-workflows component list is partially known from `artifacts/prompt.md`, reducing exposure

**RISK-003**: **llm-workflows file paths have changed since prompt.md was written**
- Severity: Medium
- Probability: Medium
- Impact: Phase 1 LW inventory artifact contains stale paths; downstream comparison phases cite non-existent files
- Mitigation: Phase 1 task T01.02 explicitly verifies all LW paths; stale paths annotated and flagged before proceeding to Phase 2

**RISK-004**: **Comparison pairs produce inconclusive verdicts**
- Severity: Medium
- Probability: Medium
- Impact: Phase 5 synthesis has insufficient signal; merged strategy may be vague
- Mitigation: Require explicit "no clear winner" verdict with rationale rather than forcing a false conclusion; treat as valid input to Phase 5

**RISK-005**: **Phase 6 improvement plans violate "patterns not mass" constraint**
- Severity: High
- Probability: Medium
- Impact: Improvement backlog recommends wholesale adoption of llm-workflows implementation machinery, inflating v3.0 scope
- Mitigation: R-RULE enforced at Phase 6 checkpoint; Phase 7 adversarial check independently scans for violations

**RISK-006**: **Sprint crashes mid-phase (as occurred with original execution, exit code -9 after 1m 56s)**
- Severity: Medium
- Probability: Low
- Impact: Loss of in-progress phase work; need to restart from last gate
- Mitigation: Phase-gate checkpoints enable `--start N` resume; artifacts written incrementally within phases where possible

**RISK-007**: **IronClaude component inventory is incomplete due to fast-moving codebase**
- Severity: Medium
- Probability: Medium
- Impact: Missing components in Phase 1 propagate as gaps through all downstream phases; improvement backlog is incomplete
- Mitigation: Auggie MCP queries are broad; Phase 7 cross-checks all file references against actual existence; any discovered gap annotated in sprint summary

---

## Dependency Inventory

**DEP-001**: **Auggie MCP server** — `mcp__auggie-mcp__codebase-retrieval` — Required for all code discovery against `/config/workspace/IronClaude` and `/config/workspace/llm-workflows`. Primary analysis tool for phases 1–7.

**DEP-002**: **IronClaude codebase** at `/config/workspace/IronClaude` — Source repository being analyzed. Must be accessible and contain the 8 quality-enforcement component groups.

**DEP-003**: **llm-workflows codebase** at `/config/workspace/llm-workflows` — Reference framework. Must be accessible for path verification in Phase 1.

**DEP-004**: **`artifacts/prompt.md`** — Original bootstrapping prompt providing the stable llm-workflows component list (11 components with file paths). Retained as reference, not modified.

**DEP-005**: **`superclaude` sprint CLI executor** — `superclaude sprint run` command with `--start`, `--end`, `--permission-flag` support. Required to execute all phases with gate enforcement.

**DEP-006**: **`/sc:adversarial` skill/command** — Used in Phase 4 for structured adversarial debates across 8 comparison pairs.

**DEP-007**: **`/sc:roadmap` command** — Downstream consumer of `improvement-backlog.md`. Schema compliance validated in Phase 8.

**DEP-008**: **`/sc:tasklist` command** — Downstream consumer of `final-improve-plan.md` for v3.0 implementation sequencing.

**DEP-009**: **Serena MCP** (`get_symbols_overview`) — Fallback for code discovery when Auggie MCP is unavailable.

**DEP-010**: **Grep/Glob tools** — Secondary fallback for pattern search when Auggie MCP is unavailable.

**DEP-011**: **`tasklist-index.md`** — Sprint phase index file (produced from this spec) required by the CLI executor to orchestrate phases 1–8.

**DEP-012**: **`phase-{1-8}-tasklist.md`** (8 files) — Per-phase task definitions referenced by `tasklist-index.md`.

**DEP-013**: **`.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md`** — Evidence source for known IronClaude rigor gaps (v2.24 fidelity failure root causes). Used as contextual background, not modified.

**DEP-014**: **`src/superclaude/examples/release-spec-template.md`** — Spec template this document was written against. Informational reference.

---

## Success Criteria

**SC-001**: Phase 1 gate passes: `component-map.md` produced with ≥8 IronClaude components, ≥11 llm-workflows components, ≥8 cross-framework mappings, and all IC-only components annotated.

**SC-002**: Phase 2 gate passes: 8 `strategy-ic-*.md` files produced, each containing a strength section paired with a documented weakness.

**SC-003**: Phase 3 gate passes: 11 `strategy-lw-*.md` files produced, each explicitly covering both the rigorous aspects and the bloated/slow/expensive costs.

**SC-004**: Phase 4 gate passes: 8 `comparison-*.md` files produced, each with file:line evidence from both repositories, a non-trivial verdict, and verified "patterns not mass" constraint.

**SC-005**: Phase 5 gate passes: `merged-strategy.md` produced with a "rigor without bloat" section, no orphaned component areas, all discard decisions justified, and internal consistency verified.

**SC-006**: Phase 6 gate passes: 9 improvement plan documents produced (8 component + master), each item containing P-tier, effort level, specific file path, and verified "patterns not mass" status.

**SC-007**: Phase 7 gate passes: `validation-report.md` produced with pass/fail per item; `final-improve-plan.md` produced with all failures corrected; all file paths verified to exist via Auggie MCP.

**SC-008**: Phase 8 gate passes: 4 consolidated outputs produced (`artifact-index.md`, `rigor-assessment.md`, `improvement-backlog.md`, `sprint-summary.md`).

**SC-009**: `improvement-backlog.md` passes `/sc:roadmap` schema ingestion without errors (all required fields present, enum values valid).

**SC-010**: End-to-end traceability verified: every IronClaude component in the Phase 1 map has a corresponding entry in strategy → comparison → merged strategy → improvement plan → backlog.

**SC-011**: Zero orphaned artifacts in `artifact-index.md` (all produced files linked; no produced files unlinked).

**SC-012**: Anti-sycophancy coverage: grep scan across all strategy and comparison artifacts confirms 100% of strength claims have a paired weakness.

**SC-013**: Evidence coverage: 100% of file:line citations in all artifacts verified as existing via Auggie MCP during Phase 7.

**SC-014**: "Adopt patterns not mass" verified: `patterns_not_mass_verified: true` for 100% of improvement backlog items where `pattern_source` is a llm-workflows component.

**SC-015**: Sprint resume capability: `--start 3` flag successfully picks up from Phase 3 when Phase 1 and Phase 2 artifacts exist (integration test).

**SC-016**: Phase gate enforcement: manually deleting a required gate artifact and attempting to start the subsequent phase causes the sprint to halt with a clear error message.

**SC-017**: Human review of at least 2 comparison documents confirms each contains non-trivial verdicts with file:line evidence from both repositories.

**SC-018**: Total artifact count ≥ 35 files across the `artifacts/` directory upon sprint completion.

---

## Open Questions

**OQ-001** (from OI-1): Do the llm-workflows file paths listed in `artifacts/prompt.md` still match the current state of `/config/workspace/llm-workflows`? Phase 1 task T01.02 will resolve this, but if a significant proportion of paths are stale, the llm-workflows strategy extraction in Phase 3 may require scope adjustment. **Resolution target**: Phase 1 execution.

**OQ-002** (from OI-2): Should the pipeline-analysis subsystem (FMEA, guards, invariants, contracts, dataflow, conflict) be treated as a single component group (as currently specified) or split into sub-components for comparison purposes? Splitting would increase comparison artifact count but improve granularity. **Resolution target**: Before Phase 2 begins.

**OQ-003** (from OI-3): Does `FR-XFDA-001` need to be registered in a formal FR registry before roadmap generation, or is the feature ID in this spec sufficient for `/sc:roadmap` to produce correctly-linked items? **Resolution target**: Before Phase 8 / roadmap generation.

**OQ-004** (from GAP-2): If a Phase 4 comparison pair produces a "discard both" verdict, what specific content feeds Phase 6 for that component? The spec states "document why" but does not specify whether the improvement plan item should be a placeholder, omitted, or replaced with an "IC-native improvement" item. Clarification needed to ensure Phase 6 is unambiguous.

**OQ-005** (from GAP-3): The `improvement-backlog.md` schema is defined in Section 5.3 and validated manually in Phase 8. Is manual review sufficient, or should a validation script be produced as part of Phase 8 to enable automated schema compliance checking for downstream `/sc:roadmap` runs?

**OQ-006**: The spec authorizes parallel execution of Phase 2 and Phase 3. However, both phases depend on Phase 1 artifacts and the sprint executor's concurrency model is not specified in detail. Does the CLI executor support within-sprint parallelism, or must Phase 2 complete before Phase 3 begins in practice?

**OQ-007**: The spec references 8 comparison pairs in Phase 4 but the component map may discover additional IC-only components or additional llm-workflows counterparts during Phase 1. Is the Phase 4 pair list fixed at 8, or should newly discovered high-value pairs be added?

**OQ-008**: The fallback for Auggie MCP unavailability (Serena + Grep/Glob) is specified, but the threshold for "unavailable" is not defined. If Auggie MCP returns partial or low-confidence results, should the phase proceed with those results annotated, or should the fallback be triggered?
