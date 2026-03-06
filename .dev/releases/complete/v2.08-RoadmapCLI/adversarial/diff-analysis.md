# Diff Analysis: CLI Pipeline Specification Comparison

## Metadata
- Generated: 2026-03-04T19:00:00Z
- Variants compared: 2
- Variant A: `roadmap-cli-spec.md` — `superclaude roadmap` CLI command specification (v1.1, 1010 lines)
- Variant B: `tasklist-spec-integration-strategies.md` — Tasklist v1.0 integration strategies (226 lines)
- Total differences found: 27
- Categories: structural (6), content (9), contradictions (4), unique (8)
- Focus areas: overlapping proposals, pipeline architecture, gate validation, execution patterns

---

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Document type & scope | Full implementation specification (1010 lines): architecture, data models, CLI interface, test plans, code samples | Post-debate integration strategy document (226 lines): 5 refined proposals with concrete spec-change patches | **High** — fundamentally different artifact types serving different purposes |
| S-002 | Section organization | 13 numbered top-level sections (Problem → Scope → Architecture → Pipeline Steps → CLI → Failure → Progress → FR → NFR → AC → Open Questions → Impl Notes → Design) | 2-level flat structure: Executive Summary → 5 numbered strategies → Additional Context → Deferred Items → Patch Order | **High** — Variant A is implementation-ready spec; Variant B is decision record with action items |
| S-003 | Hierarchy depth | Max depth H4 (§13.x subsections with code blocks) | Max depth H3 (strategy subsections: What/Rejected/Changes/Value) | **Medium** — reflects complexity difference, not organizational disagreement |
| S-004 | Code artifact density | 15+ code blocks (Python dataclasses, function signatures, JSON schema, CLI examples) | 2 tables, no code blocks | **High** — Variant A is code-near; Variant B is prose-near |
| S-005 | Versioning posture | Explicit In Scope/Out of Scope with v1 boundary | Explicit v1.0 parity constraints with v1.1 deferral table | **Low** — both define scope boundaries, different framing |
| S-006 | Debate provenance | No adversarial debate history (spec was produced via spec-panel) | Full debate verdict table (5 strategies × Opus vs Haiku outcomes) | **Medium** — Variant B carries its own adversarial audit trail |

---

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | **Pipeline architecture** | 8-step gated pipeline enforced by external CLI conductor (`superclaude roadmap`); each step is a `claude -p` subprocess; file-on-disk gates between steps; Python `pipeline/` base module with `execute_pipeline()` | 6-stage internal skill pipeline (ingest → parse → convert → enrich → emit → validate) reported via TodoWrite; no external conductor; same-session execution | **High** — fundamentally different execution models (external CLI vs internal skill) |
| C-002 | **Gate validation approach** | `gate_passed()` — pure Python function checking file existence + YAML frontmatter fields + minimum line count; returns `(bool, str\|None)` with structured failure messages | Pre-Write validation checklist (§8.1 checks 13-17): task count bounds, clarification adjacency, circular dependency detection, XL splitting, confidence bar format; all must pass before `Write()` | **High** — Variant A gates between subprocess steps; Variant B gates within a single session before file emission |
| C-003 | **Failure/retry policy** | Retry-once-then-halt per step; on 2nd failure → HALT with diagnostic output; `--resume` to restart from failed step; stale-spec detection via SHA-256 hash | No retry mechanism; self-check is pass/fail before write; no resume capability; relies on re-running the full skill | **High** — Variant A has robust failure recovery; Variant B has no retry/resume |
| C-004 | **Parallel execution** | `threading.Thread` with shared `threading.Event` for cross-cancellation; exactly 2 parallel generate steps; detailed concurrency model | No parallel execution; sequential 6-stage pipeline | **Medium** — different scale of ambition; not contradictory |
| C-005 | **Validation scope** | Structural validation only: file exists, frontmatter parseable, required fields present, minimum line count | Semantic validation: task specificity (artifact references, concrete verbs), acceptance criteria quality, circular dependency detection, phase bounds | **High** — Variant A validates form; Variant B validates meaning |
| C-006 | **Observability** | Progress display (stdout, 5s refresh), HALT output format, `.roadmap-state.json` for run history | TodoWrite stage completion reporting (6 stages), Generation Notes section in output | **Medium** — different observability mechanisms for different execution models |
| C-007 | **Code modularity** | `pipeline/` base module extracted from `sprint/`; inheritance hierarchy (`PipelineConfig` → `SprintConfig`/`RoadmapConfig`); composition via `StepRunner` Protocol | No code architecture; spec-change patches target existing `sc-tasklist-command-spec-v1.0.md` sections | **High** — Variant A defines new Python architecture; Variant B patches existing spec |
| C-008 | **Test architecture** | 3 test directories (pipeline/, sprint/, roadmap/); 20+ test files; unit/integration boundary; mock strategies; sprint regression guarantee | No test architecture; references "parity criterion" and "golden fixtures" as risks to address | **Medium** — Variant A is test-complete; Variant B acknowledges testing gaps |
| C-009 | **Quality enforcement** | Implicit via frontmatter field requirements (each step must produce specific YAML fields) | Explicit quality rules: minimum task specificity, acceptance criteria artifact references, prohibited vague verbs, tier-proportional enforcement (STRICT/STANDARD/LIGHT/EXEMPT) | **High** — Variant B has richer quality model; Variant A has mechanical enforcement |

---

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | **Self-validation reliability** | Relies on Claude subprocesses to produce correct output, validated externally by `gate_passed()` (pure Python, no Claude) | Explicitly rejects per-stage halt-on-failure gates because "the same model that produces output cannot reliably validate its own intermediate state (circular self-validation)" | **High** — Variant A's design avoids the circular validation problem by externalizing gates; Variant B identifies the problem but solves it differently (TodoWrite observability without gates) |
| X-002 | **Frontmatter as validation signal** | Core gate mechanism: YAML frontmatter fields are the primary signal that a step completed correctly (e.g., `convergence_score`, `primary_persona`) | No use of YAML frontmatter; quality validation is semantic (artifact references, concrete verbs, dependency graphs) | **Medium** — not directly contradictory (different artifacts), but reveals tension: frontmatter proves structure, not correctness |
| X-003 | **Determinism framing** | Implicit: pipeline steps are deterministic in execution order; output content is LLM-variable | Explicit: "'determinism is a property of the function, not of observing intermediate state'" — rejects the idea that observing stages makes output deterministic | **Medium** — philosophical disagreement about what "deterministic" means in LLM pipelines |
| X-004 | **Scope of v1 vs parity** | v1 scope is feature-additive: new CLI command, new pipeline/ module, new roadmap/ module | v1.0 scope is parity-constrained: "not feature-expanding" — only "execution-hardening patterns" that preserve existing behavior | **Low** — different projects with different scope philosophies; not actually contradictory |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | **External conductor pattern**: CLI acts as untrusted orchestrator — Claude cannot advance to step N+1 because the CLI hasn't issued the prompt yet; fabrication becomes impossible without writing required output files | **High** — solves the fundamental trust problem identified in both variants |
| U-002 | A | **Shared `pipeline/` base module**: Extracted from `sprint/` with inheritance hierarchy, enabling code reuse across sprint and roadmap commands | **High** — architectural contribution with long-term reuse value |
| U-003 | A | **`.roadmap-state.json` with stale-spec detection**: SHA-256 hash comparison on `--resume` to detect spec changes; atomic writes via tmp+rename | **High** — enables safe pipeline resumption |
| U-004 | A | **`StepRunner` Protocol with composition pattern**: Callable injection for subprocess lifecycle; sprint and roadmap provide different runners while sharing step ordering, retry, parallel dispatch | **High** — clean separation of concerns for pipeline extensibility |
| U-005 | B | **Tier-proportional quality enforcement**: STRICT/STANDARD/LIGHT/EXEMPT compliance tiers that scale validation intensity based on task criticality | **High** — graduated quality model absent from Variant A |
| U-006 | B | **Prohibited vague verbs list**: "handle", "address", "deal with", "work on", "look into" — mechanically enforceable quality gate | **Medium** — concrete, low-cost quality improvement |
| U-007 | B | **v1.1 deferral table with debate provenance**: Explicit record of what was considered, debated, and deferred with reasoning | **Medium** — transparency and planning value |
| U-008 | B | **Circular self-validation critique**: Explicit argument that "the same model that produces output cannot reliably validate its own intermediate state" with principled alternative (external observability) | **High** — important architectural insight that informs gate design |

---

## Summary
- Total structural differences: 6
- Total content differences: 9
- Total contradictions: 4
- Total unique contributions: 8
- Highest-severity items: S-001, S-002, S-004, C-001, C-002, C-003, C-005, C-009, X-001, U-001, U-005, U-008
- Similarity assessment: **<10% overlap** — these are fundamentally different artifact types addressing different (but related) problems. The debate will focus on the 4 specified areas where they intersect.
