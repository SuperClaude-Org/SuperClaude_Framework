# Diff Analysis: v2.20 Spec Comparison

## Metadata
- Generated: 2026-03-09T00:00:00Z
- Variants compared: 2
- Variant 1: spec-workflow-evolution.md (FR-051, "Claude spec")
- Variant 2: v2.20-WorkflowEvolution_Spec-GPT.md (FR-052, "GPT spec")
- Total differences found: 47
- Categories: structural (8), content (14), contradictions (9), unique (10), shared assumptions (6)

---

## Structural Differences

| # | Area | Variant 1 (FR-051) | Variant 2 (FR-052) | Severity |
|---|------|--------------------|---------------------|----------|
| S-001 | Integration point for spec-fidelity harness | Added as new step in roadmap **generation** pipeline (after test-strategy in `executor.py`) | Added to **validate subsystem** (extends `validate_executor.py`, `validate_prompts.py`, `validate_gates.py`) | High |
| S-002 | New module creation | Creates new `cli/tasklist/` module with 5 new files: `__init__.py`, `commands.py`, `executor.py`, `prompts.py`, `gates.py` | No new module created; extends existing `roadmap/validate*` files only | High |
| S-003 | Tasklist validation CLI surface | Implemented as new CLI subcommand: `superclaude tasklist validate` with full executor | Explicitly deferred to future release as "reusable contract"; not implemented | High |
| S-004 | Config model extended | Extends `RoadmapConfig` with `retrospective_file: Path \| None` | Extends `ValidateConfig` (not `RoadmapConfig`) with `spec_file: Path \| None` and `boundary_mode` | High |
| S-005 | Python dataclass introduction | No named dataclass for deviation representation; raw frontmatter counts only | Introduces `FidelityDeviation` Python dataclass for structured deviation tracking | Medium |
| S-006 | State persistence | No mention of writing pass/fail to state file | Explicitly writes semantic pass/fail to `.roadmap-state.json` | Medium |
| S-007 | Files modified | `roadmap/gates.py`, `validate_gates.py`, `executor.py`, `prompts.py`, `models.py`, `commands.py` + 5 new tasklist files | `validate_executor.py`, `validate_prompts.py`, `validate_gates.py`, `models.py`, `commands.py`, `executor.py` | High |
| S-008 | Multi-agent conflict resolution | No explicit multi-agent fidelity merge protocol described | Explicit multi-agent fidelity merge with conservative escalation on unresolved conflicts | Medium |

---

## Content Differences

| # | Topic | Variant 1 Approach | Variant 2 Approach | Severity |
|---|-------|--------------------|---------------------|----------|
| C-001 | REFLECT_GATE tier | Promoted from STANDARD → STRICT (FR-051.3) to fix silent semantic-check skip | Not mentioned; no gate tier changes | High |
| C-002 | `_cross_refs_resolve()` fix | Explicitly fixed to actually validate cross-references (FR-051.4) — was always returning True | Not mentioned; cross-ref validation bug not addressed | Medium |
| C-003 | Retrospective wiring | Extract prompt extended with prior release retrospective content; `--retrospective` flag added to `roadmap run` | Not mentioned; no retrospective wiring | Medium |
| C-004 | `--no-validate` flag semantics | Skips only validate pipeline; spec-fidelity harness remains active as generation quality gate | Skips fidelity harnesses entirely alongside validate pipeline | High |
| C-005 | Deviation report frontmatter schema | `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`, `upstream_file`, `downstream_file`, `source_pair` | `blocking_issues_count`, `warnings_count`, `tasklist_ready`, `source_pair`, `validation_complete` | High |
| C-006 | Degraded validation handling | No explicit degraded-validation path; timeout 600s, retry_limit: 1 (hard error on failure) | FR-052.5: explicit degraded validation contract (`validation_complete: false` when agents fail) | Medium |
| C-007 | Gate semantic check function | Named `_high_severity_count_zero(content)` — explicit testable predicate; returns False if field missing | Not named; implied through `blocking_issues_count` field check | Low |
| C-008 | Spec-fidelity output location | `{output_dir}/spec-fidelity.md` explicit | Integrated into validate subsystem output path; location not separately specified | Low |
| C-009 | Performance timeout numbers | Explicit: ≤120s NFR; step timeout 600s; retry_limit: 1 | No explicit timeout numbers; no retry_limit specified | Medium |
| C-010 | Complexity rating | 0.65 (moderate) | 0.88 (high) | Medium |
| C-011 | Test coverage documented | 19+ unit tests (named), 6 integration tests (named) | 6 unit tests (named), 4 integration tests (named) | Medium |
| C-012 | Open items count | 3 open items | 4 open items (different set) | Low |
| C-013 | Risk count | 6 risks documented with probability/impact | 6 risks documented with probability/impact | Low |
| C-014 | `boundary_mode` config field | Not present | Introduced on `ValidateConfig`; values and behavior underspecified | Low |

---

## Contradictions

| # | Point of Conflict | Variant 1 Position | Variant 2 Position | Impact |
|---|-------------------|--------------------|--------------------|--------|
| X-001 | Where spec-fidelity lives architecturally | "New step in roadmap GENERATION pipeline (after test-strategy in executor.py)" — fidelity is a generation quality gate, always active | "Extends validate_executor.py" — fidelity is a validation concern, skippable via `--no-validate` | High |
| X-002 | `--no-validate` flag behavior | "`--no-validate` skips only validate pipeline, NOT spec-fidelity (treats fidelity as generation quality gate)" | "`--no-validate` skips fidelity harnesses too" | High |
| X-003 | Tasklist validation in this release | Implemented as `superclaude tasklist validate` CLI subcommand, new `cli/tasklist/` module with 5 files | "Tasklist validation: defined as future reusable contract, NOT implemented as separate CLI subcommand in this release" | High |
| X-004 | Config model extension | `RoadmapConfig` extended with `retrospective_file` — generation-time concern | `ValidateConfig` extended with `spec_file` and `boundary_mode` — validation-time concern | High |
| X-005 | Deviation report blocking field name | `high_severity_count` (with separate medium/low counts) — severity-based schema | `blocking_issues_count` (with `warnings_count`) — action-based schema | High |
| X-006 | `tasklist_ready` field | Not present in deviation report schema | Explicit boolean gate field `tasklist_ready` in frontmatter | Medium |
| X-007 | REFLECT_GATE tier promotion | Explicitly promoted STANDARD → STRICT (FR-051.3) — confirms fix needed | Completely absent; implies REFLECT_GATE remains STANDARD | Medium |
| X-008 | `_cross_refs_resolve()` fix | Explicitly included: "changed from always-return-True to actual validation" | Not mentioned; cross-ref validation bug not addressed | Medium |
| X-009 | Degraded validation as explicit contract | No degraded-validation path; fidelity step retry_limit: 1, then hard failure | FR-052.5: named contract — `validation_complete: false`, pipeline continues, report identifies failed agents | Medium |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|--------------|-----------------|
| U-001 | Variant 1 (FR-051) | Retrospective wiring: `--retrospective` flag, `retrospective_file` on RoadmapConfig, extract prompt extended with prior-release findings | High — closes release-to-release feedback loop; enables iterative self-correction |
| U-002 | Variant 1 (FR-051) | REFLECT_GATE promotion STANDARD → STRICT — fixes known silent semantic-check skip | High — directly improves validation rigor on confirmed weak gate |
| U-003 | Variant 1 (FR-051) | `_cross_refs_resolve()` bug fix — function "changed from always-return-True to actual validation" | High — eliminates silent false-positive cross-ref validation |
| U-004 | Variant 1 (FR-051) | Explicit NFR performance targets: ≤120s per fidelity step; 600s step timeout; retry_limit: 1 | Medium — measurable acceptance criteria for CI enforcement |
| U-005 | Variant 1 (FR-051) | Named gate semantic check `_high_severity_count_zero(content)` — explicit testable predicate | Low — implementation detail, aids unit test specificity |
| U-006 | Variant 2 (FR-052) | `FidelityDeviation` Python dataclass — typed, introspectable, serializable deviation representation | Medium — improves code maintainability and enables typed downstream processing |
| U-007 | Variant 2 (FR-052) | State persistence: semantic pass/fail written to `.roadmap-state.json` | High — enables resume/retry workflows and cross-stage orchestration |
| U-008 | Variant 2 (FR-052) | FR-052.5 "degraded validation" explicit contract: `validation_complete: false` when agents fail | High — graceful failure handling prevents pipeline crashes in flaky agent environments |
| U-009 | Variant 2 (FR-052) | Multi-agent fidelity merge with conservative conflict escalation protocol | Medium — addresses multi-agent output disagreement systematically |
| U-010 | Variant 2 (FR-052) | `boundary_mode` config field on `ValidateConfig` — parameterizes validation mode | Low — values/semantics underspecified, but extensibility hook present |

---

## Shared Assumptions

| # | Agreement Source | Assumption | Classification | Promoted |
|---|-----------------|------------|----------------|---------|
| A-001 | Both variants | A spec-fidelity harness is necessary and within scope for v2.20 | STATED | No |
| A-002 | Both variants | `source_pair` is a required field in the deviation report frontmatter | STATED | No |
| A-003 | Both variants | Tasklist validation is valid and desirable — differs only in whether it ships in v2.20 | UNSTATED — V1 ships it, V2 defers it, neither questions its value | Yes |
| A-004 | Both variants | The existing `validate_gates.py` and `validate_prompts.py` are appropriate extension points for fidelity logic | UNSTATED — V2 extends them directly; V1 modifies them as part of a broader change set | Yes |
| A-005 | Both variants | Markdown with YAML frontmatter is the correct output format for deviation reporting | UNSTATED — both describe frontmatter fields without questioning the format itself | Yes |
| A-006 | Both variants | Fidelity checking requires an AI agent call (not deterministic rule-based) | UNSTATED — both describe prompt-based agent execution without questioning this assumption | Yes |

---

## Summary

- Total structural differences: 8
- Total content differences: 14
- Total contradictions: 9
- Total unique contributions: 10
- Total shared assumptions surfaced: 6 (UNSTATED: 4, STATED: 2, CONTRADICTED: 0)
- Highest-severity items:
  - **X-001** — Architectural integration point (generation vs validate subsystem) — determines fidelity mandatoriness
  - **X-002** — `--no-validate` flag semantics are directly contradictory
  - **X-003** — Tasklist validate CLI: ships (V1) vs deferred (V2)
  - **X-004** — Config model changes incompatible (different classes, different fields)
  - **X-005** — Deviation report frontmatter schemas are mutually incompatible
  - **S-001** — Integration point divergence cascades into almost all other differences
  - **U-001** — Retrospective wiring (V1 only) — high-value cross-release feedback mechanism
  - **U-007** — State persistence (V2 only) — high-value orchestration enabler
  - **U-008** — Degraded validation contract (V2 only) — high-value resilience mechanism
  - **U-002/U-003** — REFLECT_GATE + cross-ref fixes (V1 only) — confirmed production bugs
