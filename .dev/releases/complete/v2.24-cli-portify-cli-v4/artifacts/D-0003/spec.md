---
deliverable_id: D-0003
task_id: T01.03
roadmap_item: R-003
phase: 1
type: artifact-contract
status: FINAL
depends_on: D-0001
---

# D-0003: Artifact Contract — Output Names, Locations, and Frontmatter Rules

## Purpose

Standardize the 9 artifact outputs defined in the roadmap's "Artifact Outputs" section. Each artifact has a defined filename, directory, format, frontmatter schema, and failure/default population rules per NFR-009.

---

## Artifact Contract Table

### Artifact 1: `validate-config-result.json`

| Field | Value |
|-------|-------|
| Filename | `validate-config-result.json` |
| Directory | `{output_dir}/` |
| Format | JSON |
| Produced By | Step 1 (validate-config) |
| Gate | SC-001 (EXEMPT) |
| Frontmatter | N/A (JSON format) |
| Required Fields | `workflow_path`, `cli_name`, `output_dir`, `valid` (bool), `errors` (array), `collision_detected` (bool) |
| Failure Default | `{"valid": false, "errors": ["<error_description>"], "collision_detected": false}` |

### Artifact 2: `component-inventory.md`

| Field | Value |
|-------|-------|
| Filename | `component-inventory.md` |
| Directory | `{output_dir}/` |
| Format | Markdown with YAML frontmatter |
| Produced By | Step 2 (discover-components) |
| Gate | SC-002 (EXEMPT) |
| Frontmatter Schema | `source_skill` (string), `component_count` (int) |
| Required Sections | Component listing table with columns: Component, Path, Type, Line Count |
| Failure Default | Frontmatter with `source_skill: "<workflow_path>"`, `component_count: 0`; body: "No components discovered." |

### Artifact 3: `portify-analysis.md`

| Field | Value |
|-------|-------|
| Filename | `portify-analysis.md` |
| Directory | `{output_dir}/` |
| Format | Markdown with YAML frontmatter |
| Produced By | Step 3 (analyze-workflow) — Claude-assisted |
| Gate | SC-003 (STRICT) |
| Frontmatter Schema | `source_skill` (string), `analysis_version` (string), `step_count` (int), `gate_count` (int), `parallel_groups` (int) |
| Required Sections | (1) Behavioral Flow, (2) Step Boundaries, (3) Programmatic Spectrum Classification, (4) Dependency/Parallel Groups, (5) Gate Requirements, (6) Data Flow Diagram (arrow notation) |
| Size Constraint | <400 lines |
| Failure Default | Frontmatter with all fields set to defaults (0/empty); body: "Analysis incomplete — step failed or timed out." |

### Artifact 4: `portify-spec.md`

| Field | Value |
|-------|-------|
| Filename | `portify-spec.md` |
| Directory | `{output_dir}/` |
| Format | Markdown with YAML frontmatter |
| Produced By | Step 4 (design-pipeline) — Claude-assisted |
| Gate | SC-004 (STRICT) |
| Frontmatter Schema | `step_mapping_count` (int), `model_count` (int), `gate_definition_count` (int) |
| Required Sections | Step graph, domain models, prompt builder specs, gate criteria with semantic checks, pure-programmatic steps as runnable Python code, executor loop, Click CLI integration |
| Failure Default | Frontmatter with all count fields set to 0; body: "Design incomplete — step failed or timed out." |

### Artifact 5: Synthesized Release Spec

| Field | Value |
|-------|-------|
| Filename | Derived from template (e.g., `release-spec.md`) |
| Directory | `{output_dir}/` |
| Format | Markdown with YAML frontmatter |
| Produced By | Step 5 (synthesize-spec) — Claude-assisted |
| Gate | SC-005 (STRICT) |
| Frontmatter Schema | Inherited from `release-spec-template.md` |
| Validation | Zero remaining `{{SC_PLACEHOLDER:*}}` sentinels; 7 FRs with consolidation mapping |
| Resume Policy | Re-run on partial failure (per D-0001 Resolution 2) |
| Failure Default | Template file with remaining placeholders marked; body includes sentinel scan results |

### Artifact 6: Brainstorm Findings (Augmented Spec Sections)

| Field | Value |
|-------|-------|
| Filename | Augmented sections within the synthesized spec + standalone findings |
| Directory | `{output_dir}/` |
| Format | Structured findings objects within Markdown |
| Produced By | Step 6 (brainstorm-gaps) — Claude-assisted |
| Gate | SC-006 (STANDARD) |
| Finding Schema | `gap_id` (string), `description` (string), `severity` (string), `affected_section` (string), `persona` (string) |
| Required Sections | Section 12 (summary) with either: (a) findings table with Gap ID column, or (b) zero-gap summary text. Heading-only content MUST fail. |
| Validation | SC-015: `has_section_12` structural content validation |
| Failure Default | Section 12 with text "Brainstorm step failed — no findings produced." |

### Artifact 7: `panel-report.md`

| Field | Value |
|-------|-------|
| Filename | `panel-report.md` |
| Directory | `{output_dir}/` |
| Format | Markdown with machine-readable convergence block |
| Produced By | Step 7 (panel-review) — Claude-assisted |
| Gate | SC-007 (STRICT) |
| Required Content | Convergence terminal state, quality scores (clarity, completeness, testability, consistency, overall), downstream readiness evaluation, iteration log |
| Quality Score Schema | Each dimension: float (0.0-10.0); overall = arithmetic mean of 4 dimensions (+/-0.01 per SC-008) |
| Downstream Readiness | `overall >= 7.0` (7.0 true, 6.9 false per D-0001 Resolution 3) |
| Failure Default | Convergence state: `FAILED`; all quality scores: 0.0; downstream_ready: false |

### Artifact 8: Final Return Contract

| Field | Value |
|-------|-------|
| Filename | Emitted to stdout/returned programmatically |
| Directory | N/A (not written to file) |
| Format | Phase Contracts schema YAML |
| Produced By | `contract.py` on all exit paths |
| Gate | SC-010 |
| Contract Statuses | `success`, `partial`, `failed`, `dry_run` |
| Required Fields | `status`, `phases` (array with per-phase status), `artifacts` (array of produced artifact paths), `resume_command` (if applicable), `timing` (total and per-step) |
| Failure Default (NFR-009) | `status: "failed"`, all phase statuses populated with last-known state, `artifacts: []`, `resume_command` generated for resumable failures |

### Artifact 9: Step/Phase Timing and Diagnostic Logs (NDJSON)

| Field | Value |
|-------|-------|
| Filename | `execution-log.jsonl` |
| Directory | `{output_dir}/` |
| Format | NDJSON (newline-delimited JSON) |
| Produced By | `monitor.py` throughout execution |
| Gate | None (informational) |
| Event Schema | `timestamp` (ISO 8601), `signal` (from signal vocabulary D-0004), `step` (string), `phase` (int), `data` (object) |
| Companion Report | `execution-log.md` (Markdown summary generated from NDJSON at pipeline end) |
| Failure Default | Last event logged before failure; no truncation of partial logs |

---

## Frontmatter Rules

### Parsing Behavior

1. YAML frontmatter is delimited by `---` on its own line at the start and end of the frontmatter block.
2. Frontmatter must appear at the very beginning of the file (line 1).
3. Missing frontmatter in a file that requires it is a gate failure.
4. Unknown frontmatter fields are ignored (forward-compatible).
5. Required fields that are missing cause a gate failure with a diagnostic message naming the missing field(s).

### Validation Behavior

1. Type validation: fields must match their declared types (string, int, float, bool).
2. Range validation: count fields must be >= 0; score fields must be 0.0-10.0.
3. Semantic validation: per-gate SC criteria (e.g., SC-003 requires 5 specific frontmatter fields).

---

## Failure/Default Population Rules (NFR-009)

All failure paths must produce populated contract objects. No exit path may produce an empty or null contract.

1. **Step-level failure**: The step's artifact is written with failure defaults (see per-artifact table above). The step's `PortifyStepResult` records the failure with classification (timeout, missing_artifact, malformed_frontmatter, gate_failure, user_rejection, budget_exhaustion, partial_artifact).
2. **Pipeline-level failure**: `contract.py` emits a `failed` contract with all phases populated to their last-known state.
3. **Dry-run termination**: `contract.py` emits a `dry_run` contract with phases 3-4 marked `skipped`.
4. **User rejection**: `contract.py` emits a `failed` contract with `user_rejection` as the failure reason.
5. **Budget exhaustion**: `contract.py` emits a `partial` contract with `ESCALATED` convergence state and resume guidance.

---

## Cross-Reference to Roadmap

| Artifact | Roadmap "Artifact Outputs" # | Step | Phase |
|----------|------------------------------|------|-------|
| validate-config-result.json | 1 | Step 1 | Phase 2 |
| component-inventory.md | 2 | Step 2 | Phase 2 |
| portify-analysis.md | 3 | Step 3 | Phase 4 |
| portify-spec.md | 4 | Step 4 | Phase 4 |
| Synthesized release spec | 5 | Step 5 | Phase 4 |
| Brainstorm findings | 6 | Step 6 | Phase 5 |
| panel-report.md | 7 | Step 7 | Phase 5 |
| Final return contract | 8 | All | All |
| NDJSON execution logs | 9 | All | All |

All 9 artifacts from roadmap Section "Artifact Outputs" are covered.
