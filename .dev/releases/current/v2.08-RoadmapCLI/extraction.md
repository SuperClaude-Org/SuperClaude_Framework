---
spec_source: ".dev/releases/current/v2.06-RoadmapCLI/merged-spec.md"
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
functional_requirements: 33
nonfunctional_requirements: 7
total_requirements: 40
domains_detected: [backend, documentation]
complexity_score: 0.522
complexity_class: MEDIUM
risks_identified: 6
dependencies_identified: 6
success_criteria_count: 7
extraction_mode: single-pass
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  fallback_activated: false
---

# Extraction: `superclaude roadmap` CLI Command

## Overview

**Project**: `superclaude roadmap` — a CLI command that acts as an external conductor for roadmap generation, calling Claude as a subprocess per step with file-on-disk gates between steps. Eliminates fabrication risk by ensuring Claude cannot advance to step N+1 without writing required output files.

**Source Spec**: `.dev/releases/current/v2.06-RoadmapCLI/merged-spec.md` (v1.1, 1095 lines)

**Complexity**: MEDIUM (0.522) — 40 requirements, 6 dependencies, moderate dependency depth, single-domain focus (backend)

---

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | CLI command `superclaude roadmap <spec-file>` executes 8-step pipeline with gates enforced between steps | backend | P0 | L437 |
| FR-002 | Steps generate-A and generate-B launch as concurrent subprocesses; diff waits for both gates | backend | P0 | L438 |
| FR-003 | Each step's prompt built from only the files in its `inputs` list; no other context passed (context isolation) | backend | P0 | L439 |
| FR-004 | `gate_passed()` checks: file exists, non-empty, line count >= minimum, YAML parseable, required fields present | backend | P0 | L440 |
| FR-005 | On gate failure: retry once (same prompt), then halt with diagnostic output per §6.2 | backend | P0 | L441 |
| FR-006 | `--resume` skips steps whose output files pass their gates; forces extract re-run if spec hash changed | backend | P1 | L442 |
| FR-007 | `--dry-run` prints step plan (ID, output file, gate criteria, timeout) and exits without subprocess invocations | backend | P1 | L443 |
| FR-008 | Default output directory is the parent directory of the spec-file | backend | P1 | L444 |
| FR-009 | `superclaude roadmap` registered as a Click command group in `main.py` | backend | P0 | L445 |
| FR-010 | Sprint module migrated to import `ClaudeProcess` and generic step execution from `pipeline/`; sprint external CLI API unchanged | backend | P0 | L446 |
| FR-011 | `gate_passed()` returns `(bool, str\|None)` — failure reason is a human-readable string per defined message format | backend | P0 | L447 |
| FR-012 | `.roadmap-state.json` written to `output_dir` after each step with spec-file SHA-256 hash and timestamp | backend | P1 | L448 |
| FR-013 | Progress output emitted to stdout during step execution, updated every 5 seconds | backend | P1 | L449 |
| FR-014 | Per-step timeouts enforced: extract=300s, generate=900s, diff=300s, debate=600s, score=300s, merge=600s, test-strategy=300s | backend | P0 | L450 |
| FR-015 | `--agents` value passed directly to `claude -p --model`; no model ID resolution performed by CLI | backend | P1 | L451 |
| FR-016 | Shared `pipeline/` base module extracted from `sprint/` — owns ClaudeProcess, execute_pipeline, Step, GateCriteria | backend | P0 | L30, L57-L86 |
| FR-017 | `PipelineConfig` dataclass: work_dir, dry_run, max_turns, model, permission_flag, debug | backend | P0 | L90-L101 |
| FR-018 | `Step` dataclass: id, prompt, output_file, gate (Optional), timeout_seconds, inputs, model, retry_limit | backend | P0 | L114-L127, L1016-L1026 |
| FR-019 | `StepResult` dataclass: step, status (PASS/FAIL/TIMEOUT/SKIPPED/CANCELLED), attempt, gate_failure_reason, timestamps | backend | P0 | L130-L139 |
| FR-020 | `GateCriteria` dataclass: required_frontmatter_fields, min_lines, enforcement_tier, semantic_checks | backend | P0 | L153-L162 |
| FR-021 | `SemanticCheck` dataclass: name, check_fn (Callable), failure_message | backend | P0 | L142-L151 |
| FR-022 | Gate enforcement is tier-proportional: EXEMPT(noop), LIGHT(exists+non-empty), STANDARD(+lines+frontmatter), STRICT(+semantic) | backend | P0 | L190-L200 |
| FR-023 | Context isolation: each step receives context exclusively through prompt string + `--file` flags; no shared memory between steps | backend | P0 | L214-L228 |
| FR-024 | `AgentSpec` dataclass: model, persona, id property (`model-persona`), parse classmethod from `model:persona` string | backend | P0 | L533-L550 |
| FR-025 | `execute_pipeline()` generic executor using composition via callable `StepRunner` protocol injection | backend | P0 | L887-L952 |
| FR-026 | Parallel subprocess concurrency via `threading.Thread` + shared `threading.Event` for cross-cancellation | backend | P0 | L602-L657 |
| FR-027 | 7 prompt builders as pure functions in `roadmap/prompts.py`: extract, generate, diff, debate, score, merge, test-strategy | backend | P0 | L659-L795 |
| FR-028 | `.roadmap-state.json` schema: schema_version, spec_file, spec_hash, agents, depth, timestamps, per-step status; atomic writes via tmp+rename | backend | P0 | L797-L885 |
| FR-029 | Resume algorithm: compare spec hashes, skip passing gates, re-run from first failing step | backend | P1 | L868-L885 |
| FR-030 | `SprintConfig` inherits from `PipelineConfig`; `release_dir` becomes property alias for `work_dir` | backend | P0 | L556-L599 |
| FR-031 | Semantic checks for STRICT steps: merge (no_heading_gaps, cross_refs_resolve, no_duplicate_headings), generate (frontmatter_values_non_empty, has_actionable_content), debate (convergence_score_valid) | backend | P1 | L256-L270 |
| FR-032 | Depth-to-prompt mapping: quick=1 debate round, standard=2 rounds, deep=3 rounds | backend | P1 | L772-L795 |
| FR-033 | HALT output: step name, gate failure reason, output file details, completed/failed/skipped step summary, retry command | backend | P0 | L364-L383 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Sprint's external CLI API produces identical behavior before and after pipeline/ migration | maintainability | All existing sprint tests pass | L459 |
| NFR-002 | All existing sprint tests pass after migration | maintainability | `uv run pytest tests/sprint/` exits 0 | L460 |
| NFR-003 | `gate_passed()` is pure Python — no subprocess, no I/O beyond reading the output file | performance | Unit test verifies no subprocess | L461 |
| NFR-004 | Step prompts in `roadmap/prompts.py` are pure functions: no I/O, no subprocess calls | maintainability | Module imports cleanly; functions return str | L462 |
| NFR-005 | Gate criteria defined as data (list of GateCriteria instances), not embedded in executor logic | maintainability | Gate criteria readable without running executor | L463 |
| NFR-006 | PipelineConfig, Step, StepResult, GateCriteria have no sprint-specific fields | maintainability | Sprint-specific fields only in SprintConfig | L464 |
| NFR-007 | `pipeline/` module has no imports from `sprint/` or `roadmap/` (one-directional dependency) | maintainability | Import check: assert no sprint/roadmap references | L465 |

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | `pipeline/` module must be extracted before `roadmap/` can be built | internal | FR-016, FR-025 |
| DEP-002 | Sprint migration to `pipeline/` must complete before roadmap work | internal | FR-010, FR-030 |
| DEP-003 | Sprint tests must pass after migration (regression canary) | internal | NFR-001, NFR-002 |
| DEP-004 | `claude` CLI binary required in PATH for E2E testing | external | SC-002 |
| DEP-005 | Click framework required for CLI registration | external | FR-009 |
| DEP-006 | Both parallel generate steps must pass before diff step can start | internal | FR-002 |

---

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | `--dry-run` prints 7 step entries (ID, output file, gate criteria, timeout) and exits 0; no files written | AC-01, FR-007 | Yes |
| SC-002 | Full run produces 8 output files: extraction.md, roadmap-{A,B}.md, diff-analysis.md, debate-transcript.md, base-selection.md, roadmap.md, test-strategy.md | AC-02 | Yes |
| SC-003 | Gate failure → retry once → halt with diagnostic message containing field name and file path | AC-03, FR-005 | Yes |
| SC-004 | `--resume` with all gates passing: prints skip message, exits 0, no subprocesses launched | AC-04, FR-006 | Yes |
| SC-005 | `--resume` with changed spec: detects hash mismatch, warns, re-runs extract step | AC-05, FR-012 | Yes |
| SC-006 | `uv run pytest tests/sprint/` exits 0 after pipeline/ migration (all sprint tests passing at extraction start; no modifications during migration) | AC-06, NFR-002 | Yes |
| SC-007 | `--agents sonnet:security,haiku:qa` uses correct model values in generate subprocess invocations | AC-07, FR-015 | Yes |

---

## Risks

| ID | Description | Probability | Impact | Affected Requirements |
|----|-------------|-------------|--------|----------------------|
| RISK-001 | Sprint regression during pipeline/ extraction — existing behavior changes due to refactoring | Medium | High | FR-010, NFR-001, NFR-002 |
| RISK-002 | Claude subprocess produces non-conforming output (missing frontmatter, insufficient lines), requiring retries | High | Medium | FR-004, FR-005 |
| RISK-003 | Parallel subprocess cross-cancellation race conditions in threading model | Low | High | FR-002, FR-026 |
| RISK-004 | Gate validation calibration — too strict causes false halts, too lenient passes bad output | Medium | Medium | FR-022, FR-031 |
| RISK-005 | State file corruption during atomic write (crash between tmp write and rename) | Low | Medium | FR-028 |
| RISK-006 | Timeout values insufficient for complex specifications on slower systems | Medium | Low | FR-014 |

---

## Domain Analysis

| Domain | Percentage | Key Areas |
|--------|-----------|-----------|
| Backend | 95% | CLI architecture, subprocess management, threading, file I/O, dataclass models, pipeline orchestration, gate validation |
| Documentation | 5% | Progress display format, HALT output format, state file schema documentation |

---

## Complexity Analysis

| Factor | Raw Value | Normalized | Weight | Weighted |
|--------|-----------|-----------|--------|----------|
| requirement_count | 40 | 0.800 | 0.25 | 0.200 |
| dependency_depth | 3 | 0.375 | 0.25 | 0.094 |
| domain_spread | 1 | 0.200 | 0.20 | 0.040 |
| risk_severity | 1.50 | 0.250 | 0.15 | 0.038 |
| scope_size | 1095 | 1.000 | 0.15 | 0.150 |

**Total Complexity Score**: 0.522 (MEDIUM)
**Classification**: 5-7 milestones, 1:2 interleave ratio
