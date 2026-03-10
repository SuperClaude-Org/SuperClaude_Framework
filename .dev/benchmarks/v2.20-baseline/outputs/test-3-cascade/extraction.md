---
spec_source: SC-ROADMAP-V2-SPEC.md
generated: "2026-03-09T00:00:00Z"
generator: requirements-extraction-agent
functional_requirements: 46
nonfunctional_requirements: 12
total_requirements: 58
complexity_score: 0.82
complexity_class: complex
domains_detected: 7
risks_identified: 9
dependencies_identified: 8
success_criteria_count: 30
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 139.0, started_at: "2026-03-09T02:21:55.203848+00:00", finished_at: "2026-03-09T02:24:14.221618+00:00"}
---

## Functional Requirements

**FR-001**: Produce exactly 3 output artifacts per invocation: `roadmap.md`, `extraction.md`, and `test-strategy.md`.

**FR-002**: All output artifacts include YAML frontmatter with machine-parseable metadata following the schemas defined in Section 4 (FR-002).

**FR-003**: `roadmap.md` frontmatter includes exactly one of `spec_source` (scalar, single-spec mode) or `spec_sources` (list, multi-spec mode), never both.

**FR-004**: `roadmap.md` frontmatter includes `milestone_index` with per-milestone structured metadata (id, title, type, priority, dependencies, deliverable_count, risk_level).

**FR-005**: `roadmap.md` frontmatter includes `adversarial` block (mode, agents, convergence_score, base_variant, artifacts_dir) when adversarial modes are used; absent otherwise.

**FR-006**: `extraction.md` frontmatter includes requirement counts, domain list, complexity score, risk count, dependency count, and success criteria count.

**FR-007**: `test-strategy.md` frontmatter includes `validation_philosophy: continuous-parallel`, `interleave_ratio`, and `major_issue_policy: stop-and-fix`.

**FR-008**: Multi-spec consolidation mode activated via `--specs spec1.md,spec2.md[,...,specN.md]` flag, invoking `sc:adversarial --compare` to produce a unified spec before roadmap generation.

**FR-009**: Multi-roadmap generation mode activated via `--multi-roadmap --agents <agent-spec>[,...]` flag, invoking `sc:adversarial --source --generate roadmap --agents` to produce competing variants and merge them.

**FR-010**: Combined mode supports both `--specs` and `--multi-roadmap` flags together, chaining spec consolidation (Wave 1A) then roadmap adversarial generation (Wave 2) sequentially.

**FR-011**: Agent spec format supports `model[:persona[:"instruction"]]` parsing — split on `,` for agent list, then `:` per agent (max 3 segments). Model-only agents inherit the auto-detected primary persona from Wave 1B.

**FR-012**: Agent count enforced at 2-10 range (inherits sc:adversarial limit). With ≥5 agents, an orchestrator agent is added to coordinate elimination rounds.

**FR-013**: Implement 5-wave architecture: Wave 0 (Prerequisites), Wave 1A (Spec Consolidation, conditional), Wave 1B (Detection & Analysis), Wave 2 (Planning & Template Selection), Wave 3 (Generation), Wave 4 (Validation).

**FR-014**: Wave 0 validates spec files exist/readable, output directory writable, template directory availability, adversarial skill availability (if `--specs`/`--multi-roadmap`), and model identifier recognition (if `--multi-roadmap`).

**FR-015**: Wave 0 output collision check — if output directory already contains artifacts, append `-N` suffix (incrementing) to all output filenames instead of overwriting.

**FR-016**: Wave 1A invokes `sc:adversarial --compare` for multi-spec mode and handles return contract: `success` → proceed, `partial` with convergence ≥60% → proceed with warning, `partial` with convergence <60% → prompt user (if `--interactive`) or abort, `failed` → abort.

**FR-017**: Wave 1A applies divergent-specs heuristic: emit warning if sc:adversarial returns convergence <50%.

**FR-018**: Wave 1B loads `refs/extraction-pipeline.md` + `refs/scoring.md`, parses the spec, runs the extraction pipeline, writes `extraction.md` to disk immediately, scores complexity, classifies domains, and activates personas.

**FR-019**: Wave 1B supports `--persona` flag to override auto-detected primary persona.

**FR-020**: Wave 2 loads `refs/templates.md`, performs 4-tier template discovery (local → user → plugin → inline generation) with compatibility scoring, creates milestone structure, and maps dependencies.

**FR-021**: Wave 2 invokes `sc:adversarial --source --generate roadmap --agents` when `--multi-roadmap` flag is present, replacing template-based generation.

**FR-022**: Wave 3 generates `roadmap.md` first (with YAML frontmatter, milestone hierarchy, Decision Summary), then generates `test-strategy.md` referencing concrete milestones from roadmap.md. Sequencing constraint: roadmap.md MUST complete before test-strategy.md begins.

**FR-023**: Wave 3 `roadmap.md` body includes a Decision Summary section with rows for Primary Persona, Template, Milestone Count, Adversarial Mode, and Adversarial Base Variant — each citing specific data points that drove the decision.

**FR-024**: Wave 4 dispatches quality-engineer agent (completeness, consistency, traceability, test-strategy validation) and self-review agent (4-question protocol), aggregates scores, and produces PASS (≥85%) / REVISE (70-84%) / REJECT (<70%).

**FR-025**: Wave 4 quality-engineer validates test-strategy.md: interleave ratio matches complexity class, every validation milestone references a real work milestone, continuous parallel validation philosophy is explicitly encoded, stop-and-fix thresholds defined.

**FR-026**: Wave 4 checks adversarial artifacts: missing artifacts when adversarial mode used → REJECT; missing convergence score → REVISE.

**FR-027**: REVISE loop (FR-017): if score 70-84%, re-run Wave 3 → Wave 4 up to 2 iterations. If still REVISE after 2 iterations, accept with `validation_status: PASS_WITH_WARNINGS`.

**FR-028**: `test-strategy.md` encodes continuous parallel validation philosophy: work assumed deviated until proven otherwise, validation agent runs in parallel, major issues trigger stop, validation milestones interleaved (not batched).

**FR-029**: Interleave ratio computed from complexity: LOW → 1:3, MEDIUM → 1:2, HIGH → 1:1.

**FR-030**: No downstream handoff — sc:roadmap does not trigger or reference any downstream commands. Final output message lists artifacts and says "Review the roadmap before proceeding to tasklist generation."

**FR-031**: `--depth` flag maps to both internal analysis depth and adversarial debate depth: quick (1 round), standard (2 rounds), deep (3 rounds).

**FR-032**: Adversarial availability check at Wave 0: if `--specs` or `--multi-roadmap` present but sc:adversarial not installed, abort with actionable error and install instructions.

**FR-033**: Progress reporting emitted at each wave boundary including wave number, completion status, key decisions, and next wave.

**FR-034**: Chunked extraction protocol (FR-016) activates automatically when spec exceeds 500 lines. Includes: section indexing, chunk assembly (~400 lines, max 600), per-chunk extraction with global ID counters, structural merge, deduplication (ID collision, normalized match, substring >0.8), cross-reference resolution, global ID assignment.

**FR-035**: Chunked extraction completeness verification: 4-pass protocol (Source Coverage ≥95%, Anti-Hallucination 100%, Section Coverage 100%, Count Reconciliation exact match). On failure: re-process failing chunks (max 1 retry), then STOP with error.

**FR-036**: Dry run mode (`--dry-run`) executes Waves 0-2, outputs structured console preview (spec, complexity, persona, template, milestone structure, domain distribution, estimated counts), writes no files, dispatches no validation agents.

**FR-037**: Dry run combined with `--specs` or `--multi-roadmap` still executes adversarial invocations (they are part of planning).

**FR-038**: Compliance tier behavior via `--compliance` flag: `strict` (full extraction + 4-pass verification even <500 lines, all template tiers, full Wave 4), `standard` (default), `light` (reduced extraction, inline templates only, skip Wave 4, set `validation_status: LIGHT`).

**FR-039**: Compliance auto-detection: security/auth/compliance keywords → STRICT; spec >500 lines → STRICT; spec <100 lines with <5 requirements → LIGHT; otherwise → STANDARD.

**FR-040**: Template discovery 4-tier search: local (`.dev/templates/roadmap/`), user (`~/.claude/templates/roadmap/`), plugin (future v5.0), inline generation fallback.

**FR-041**: Template compatibility scoring: domain match (0.40), complexity alignment (0.30), type match (0.20), version compatibility (0.10). Use highest-scoring template with score ≥0.6; below threshold → inline generation. `--template` flag skips scoring.

**FR-042**: `--no-validate` flag skips Wave 4, sets `validation_score: 0.0` and `validation_status: SKIPPED` in frontmatter.

**FR-043**: SKILL.md + refs/ architecture: lean SKILL.md (~400 lines) with behavioral instructions only; refs/ directory with 5 files (extraction-pipeline.md, scoring.md, validation.md, templates.md, adversarial-integration.md) containing algorithms and formulas.

**FR-044**: Refs loaded on-demand per wave: Wave 0 none, Wave 1A adversarial-integration (if --specs), Wave 1B extraction-pipeline + scoring, Wave 2 templates (+ adversarial-integration if --multi-roadmap), Wave 3 none (uses loaded context), Wave 4 validation. Max 2-3 refs loaded at any point.

**FR-045**: Session persistence via Serena memory: sc:save triggered at each wave boundary, storing spec_source, output_dir, flags, last_completed_wave, extraction state, complexity, persona, template, milestone count, adversarial results, validation score.

**FR-046**: Resume protocol: detect matching Serena memory session (same spec path + output dir), prompt user to resume from last completed wave, detect spec file modification via hash mismatch and warn if changed.

## Non-Functional Requirements

**NFR-001**: Single-spec roadmap generation completes in <2 minutes. Multi-spec and multi-roadmap modes add sc:adversarial time (variable).

**NFR-002**: SKILL.md must not exceed 500 lines. No YAML pseudocode blocks in SKILL.md. All algorithms, formulas, and agent prompts reside in refs/ files.

**NFR-003**: Frontmatter schema stability — fields may be added but not removed or renamed after v2.0 release. New optional fields are backward-compatible; new required fields require a major version bump.

**NFR-004**: v2.0 breaking change from v1.x — `generated_by` → `generator`, `generated_at` → `generated` (ISO-8601). Stability guarantee applies from v2.0 forward.

**NFR-005**: Refs files have no individual size limit but each must be focused on a single concern.

**NFR-006**: Maximum 2-3 ref files loaded at any point during execution to prevent context bloat.

**NFR-007**: Command file (`commands/roadmap.md`) ~80 lines, covering triggers, flags, usage, behavioral summary, and boundaries.

**NFR-008**: YAML frontmatter on all output artifacts must be parseable by standard YAML parsers.

**NFR-009**: Template file format uses YAML frontmatter with required fields: name, type, domains, target_complexity, min_version, milestone_count_range.

**NFR-010**: Separation of concerns between command file (WHEN/WHAT) and SKILL.md (HOW), with SKILL.md never duplicating algorithm details from refs/.

**NFR-011**: Circuit breaker fallbacks: Sequential unavailable → native Claude reasoning (reduced depth); Context7 unavailable → WebSearch; Serena unavailable → proceed without persistence with user warning.

**NFR-012**: Chunked extraction output is in identical format to single-pass extraction, plus `extraction_mode: chunked (N chunks)` metadata and verification summary.

## Complexity Assessment

**Complexity Score**: 0.82

**Complexity Class**: complex

**Scoring Rationale**:

| Factor | Raw Value | Normalized | Weight | Score |
|--------|-----------|------------|--------|-------|
| requirement_count | 58 | 0.85 | 0.25 | 0.213 |
| dependency_depth | Deep (adversarial chaining, wave sequencing, ref loading, session persistence) | 0.80 | 0.25 | 0.200 |
| domain_spread | 7 domains (CLI, adversarial pipeline, extraction, template system, validation, persistence, compliance) | 0.85 | 0.20 | 0.170 |
| risk_severity | 9 risks, several medium-high | 0.70 | 0.15 | 0.105 |
| scope_size | 5-wave architecture, 3 artifacts, 5 ref files, 20 flags, 4 modes | 0.90 | 0.15 | 0.135 |
| **Total** | | | | **0.823** |

Key complexity drivers:
- Multi-mode operation (single, multi-spec, multi-roadmap, combined) with conditional wave execution
- Deep sc:adversarial integration with return contract handling and convergence-based routing
- Chunked extraction protocol with 4-pass completeness verification
- REVISE loop with iterative re-generation
- Session persistence and resume protocol with hash-based staleness detection
- 4-tier template discovery with weighted compatibility scoring
- Compliance tier system with auto-detection heuristics

## Architectural Constraints

1. **SKILL.md ≤500 lines** — behavioral instructions only, no YAML pseudocode, no algorithms, no formulas, no agent prompts.

2. **Refs/ directory structure** — exactly 5 files: `extraction-pipeline.md`, `scoring.md`, `validation.md`, `templates.md`, `adversarial-integration.md`. Each focused on a single concern.

3. **On-demand ref loading** — refs loaded per-wave, max 2-3 at any point. Wave-to-ref mapping is fixed (see FR-044).

4. **Command file / SKILL.md separation** — command file (~80 lines) handles WHEN/WHAT; SKILL.md handles HOW. No duplication between them.

5. **File structure mandated**:
   - `src/superclaude/commands/roadmap.md` (command definition)
   - `src/superclaude/skills/sc-roadmap/SKILL.md` + `refs/` (skill implementation)

6. **Output directory convention** — default `.dev/releases/current/<spec-name>/`, configurable via `--output`.

7. **Frontmatter schema is a versioned contract** — downstream tasklist generator depends on it. Additions only, no renames/removals after v2.0.

8. **Wave sequencing constraints** — Wave 1A conditional (only with `--specs`), Wave 3 roadmap.md before test-strategy.md, Wave 4 after Wave 3. REVISE loops back to Wave 3.

9. **sc:adversarial dependency** — adversarial modes require sc:adversarial v1.1.0 installed. Return contract schema defined in SC-ADVERSARIAL-SPEC.md FR-007; sc:roadmap only consumes it.

10. **No downstream handoff** — sc:roadmap never triggers tasklist generation, execution prompts, or downstream commands.

11. **MCP server integration**: Sequential (Waves 1-4), Context7 (Waves 1-2), Serena (Wave 0, Wave 4). Circuit breaker fallbacks required.

12. **4-tier template discovery order**: local → user → plugin (future v5.0) → inline generation. No reordering.

13. **Agent spec parsing**: Split on `,` for list, then `:` per agent (max 3 segments). First = model, second (unquoted) = persona, second (quoted) = instruction.

## Risk Inventory

**RISK-001** (Medium probability, High impact): SKILL.md split causes Claude to miss ref files. Mitigation: SKILL.md explicitly references each ref by name; on-demand loading protocol.

**RISK-002** (Low probability, High impact): sc:adversarial unavailable/not installed. Mitigation: Detect at Wave 0; abort with actionable install instructions.

**RISK-003** (Medium probability, Medium impact): Frontmatter schema breaks future tasklist generator. Mitigation: Versioned contract; additions only, no removals after v2.0.

**RISK-004** (Medium probability, Medium impact): Multi-spec mode produces incoherent unified spec. Mitigation: Adversarial debate + Wave 4 validation; divergent-specs heuristic warns at <50% convergence.

**RISK-005** (Medium probability, Low impact): Combined mode takes too long (two adversarial passes). Mitigation: Progress reporting keeps user informed; no cost/time constraints.

**RISK-006** (Medium probability, Medium impact): Adversarial partial status causes silent quality degradation. Mitigation: Explicit convergence thresholds (≥60% proceed with warning, <60% abort or prompt).

**RISK-007** (Medium probability, High impact): Large spec files overwhelm context window. Mitigation: Chunked extraction protocol with 4-pass completeness verification.

**RISK-008** (Low probability, Medium impact): Interrupted session produces partial/stale artifacts. Mitigation: sc:save at wave boundaries; resume protocol with spec-hash mismatch detection.

**RISK-009** (Low probability, Medium impact): Unrecognized model in --agents causes late failure. Mitigation: Wave 0 validates all model identifiers before starting.

## Dependency Inventory

| ID | Dependency | Type | Version | Used By |
|----|-----------|------|---------|---------|
| DEP-001 | sc:adversarial skill | Internal (SuperClaude) | v1.1.0 | FR-008, FR-009, FR-010 (multi-spec, multi-roadmap, combined modes) |
| DEP-002 | sc:save / sc:load | Internal (SuperClaude) | Current | FR-045, FR-046 (session persistence and resumability) |
| DEP-003 | Serena MCP server | External (MCP) | Current | FR-045, FR-046 (cross-session memory persistence) |
| DEP-004 | Sequential MCP server | External (MCP) | Current | NFR-011 (wave analysis, validation reasoning) |
| DEP-005 | Context7 MCP server | External (MCP) | Current | NFR-011 (template patterns, domain best practices) |
| DEP-006 | Standard YAML parser | External | Any | NFR-008 (frontmatter parseability contract) |
| DEP-007 | Future tasklist generator command | Internal (SuperClaude) | Not yet built | FR-002 (consumes roadmap.md frontmatter as contract) |
| DEP-008 | Future v5.0 plugin marketplace | Internal (SuperClaude) | Not yet built | FR-040 (template discovery tier 3 — placeholder) |

## Success Criteria

**SC-001**: Single-spec mode produces all 3 artifacts with valid, parseable YAML frontmatter.

**SC-002**: `--specs` flag invokes sc:adversarial and produces unified spec before roadmap generation.

**SC-003**: `--multi-roadmap --agents` flag invokes sc:adversarial and produces merged roadmap.

**SC-004**: Combined mode chains both adversarial invocations correctly.

**SC-005**: `--interactive` flag propagates to sc:adversarial invocations.

**SC-006**: Wave 4 validation produces PASS/REVISE/REJECT with score in frontmatter.

**SC-007**: REVISE loop re-runs Wave 3 → Wave 4 up to 2 iterations, then PASS_WITH_WARNINGS.

**SC-008**: Adversarial `status: partial` handled with convergence-based routing (≥60%/< 60%).

**SC-009**: Progress reporting emitted at each wave boundary.

**SC-010**: No references to tasklist generation, execution prompts, or downstream command triggering in output.

**SC-011**: Output collision appends `-N` suffix instead of overwriting.

**SC-012**: `--no-validate` sets `validation_status: SKIPPED` and `validation_score: 0.0`.

**SC-013**: `--persona` override propagates to model-only agents in `--agents`.

**SC-014**: Model identifiers in `--agents` validated in Wave 0.

**SC-015**: Agent count enforced: 2-10 range.

**SC-016**: sc:save triggered at each wave boundary for resumability.

**SC-017**: Resume from interrupted session detected and offered via Serena memory.

**SC-018**: Chunked extraction activates for specs >500 lines and verifies completeness via 4-pass protocol.

**SC-019**: `--dry-run` executes Waves 0-2, outputs structured preview, writes no files.

**SC-020**: `--compliance` tier auto-detection based on spec characteristics.

**SC-021**: `--compliance light` skips Wave 4 and sets `validation_status: LIGHT`.

**SC-022**: Template discovery searches 4 tiers with compatibility scoring ≥0.6 threshold.

**SC-023**: Template scoring uses correct weights: domain (0.40), complexity (0.30), type (0.20), version (0.10).

**SC-024**: SKILL.md ≤500 lines with no YAML pseudocode.

**SC-025**: refs/ directory contains exactly 5 files covering all algorithms.

**SC-026**: Every algorithm in refs/ is referenced by name from SKILL.md; no duplication.

**SC-027**: Refs loaded on-demand per wave (max 2-3 at any point).

**SC-028**: Exactly one of `spec_source` or `spec_sources` present in frontmatter (never both).

**SC-029**: test-strategy.md encodes continuous parallel validation philosophy with computed interleave_ratio.

**SC-030**: roadmap.md body includes Decision Summary section with evidence-backed rows.

## Open Questions

1. **Plugin tier template discovery**: The spec marks plugin tier (tier 3) as `[future: v5.0 plugin marketplace — plumb in here when available]`. What is the expected interface for this tier? Should a no-op stub be implemented now, or should the tier be skipped entirely until v5.0?

2. **Model identifier validation list**: Wave 0 validates model identifiers in `--agents`, but the spec says `"Available models: opus, sonnet, haiku, gpt52, gemini, ..."` with an ellipsis. What is the canonical, exhaustive list of recognized model identifiers? Is this list configurable or hardcoded?

3. **Orchestrator agent for ≥5 agents**: The spec says "sc:roadmap adds an orchestrator agent that coordinates the adversarial debate rounds to prevent combinatorial explosion." Is this orchestrator a distinct agent type defined in sc:adversarial, or does sc:roadmap implement it? What is its prompt/behavior specification?

4. **sc:adversarial return contract schema**: The spec references "SC-ADVERSARIAL-SPEC.md Section FR-007" for the return contract schema but only documents consumption in refs/adversarial-integration.md. Is the adversarial spec finalized and available? Are there additional return fields beyond status, merged_output_path, convergence_score, artifacts_dir, and unresolved_conflicts?

5. **Serena memory key collision**: The memory key pattern is `sc-roadmap:<spec-name>:<timestamp>`. If the same spec is run multiple times, each run produces a new key. Is there a cleanup/expiry mechanism for old session keys? Should only the most recent session be offered for resume?

6. **Cross-reference resolution in chunked extraction**: The spec says unresolvable references are "logged as warnings." Should these warnings block extraction (like anti-hallucination failures) or are they informational only?

7. **Interleave ratio for edge cases**: The interleave ratio is defined for LOW/MEDIUM/HIGH. What ratio applies if a roadmap has fewer milestones than the ratio demands (e.g., LOW complexity with only 2 milestones — 1:3 ratio can't produce a validation milestone)?

8. **Adversarial depth independence**: The spec says "If the user needs independent control over adversarial debate depth, they should invoke sc:adversarial separately." Should sc:roadmap document this escape hatch prominently, or is it an implicit power-user pattern?

9. **Template file discovery in CI/containers**: The 4-tier template search assumes file system paths (`~/.claude/templates/`). How should this behave in CI environments or containerized execution where user-level paths may not exist?

10. **Dry run + adversarial cost**: FR-037 states dry run still executes adversarial invocations. These can be expensive (multi-model debate). Should `--dry-run` have a `--dry-run-no-adversarial` variant, or should the user be warned about the cost?
