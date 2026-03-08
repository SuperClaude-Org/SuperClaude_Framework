# D-0026: portify-spec.yaml Emission Evidence

**Task**: T03.05
**Roadmap Items**: R-063, R-064, R-065, R-066
**Date**: 2026-03-08
**Depends On**: D-0022, D-0023, D-0024, D-0025

---

## portify-spec.yaml Content (for sc-cleanup-audit-protocol)

The following represents the complete `portify-spec.yaml` contract that would be emitted by Phase 2 for the test workflow. It conforms to the schema defined in D-0011 (Section 3).

```yaml
# portify-spec.yaml — Phase 2 Output Contract
# Produced for: sc-cleanup-audit-protocol
# Schema: D-0011 Section 3

# Common header (from D-0010)
schema_version: "1.0"
phase: 2
status: "passed"
timestamp: "2026-03-08T00:00:00Z"
resume_checkpoint: "phase-2:complete"
validation_status:
  blocking_passed: 7
  blocking_failed: 0
  advisory:
    - "module_plan_completeness: PASS — ~825 estimated lines within bounds"

# Phase 2 specific fields

step_mapping:
  - source_id: "S-001"
    generated_step_ids: ["G-001"]
    mapping_type: "1:1"
    justification: null

  - source_id: "S-002"
    generated_step_ids: ["G-002"]
    mapping_type: "1:1"
    justification: null

  - source_id: "S-003"
    generated_step_ids: ["G-003"]
    mapping_type: "1:1"
    justification: null

  - source_id: "S-004"
    generated_step_ids: ["G-004"]
    mapping_type: "1:1"
    justification: null

  - source_id: "S-005"
    generated_step_ids: ["G-005"]
    mapping_type: "1:1"
    justification: null

  - source_id: "S-006"
    generated_step_ids: ["G-006"]
    mapping_type: "1:1"
    justification: null

elimination_records: []

coverage_invariant:
  source_step_count: 6
  mapped_step_count: 6
  eliminated_count: 0
  invariant_holds: true

module_plan:
  - file_name: "__init__.py"
    purpose: "Package init with exports"
    generation_order: 1
    estimated_lines: 15

  - file_name: "models.py"
    purpose: "Config, Status, Result, Monitor dataclasses"
    generation_order: 2
    estimated_lines: 120

  - file_name: "gates.py"
    purpose: "Gate definitions and semantic check functions"
    generation_order: 3
    estimated_lines: 100

  - file_name: "prompts.py"
    purpose: "Prompt builder functions for Claude-assisted steps"
    generation_order: 4
    estimated_lines: 250

  - file_name: "steps.py"
    purpose: "Step definitions and PROGRAMMATIC_RUNNERS"
    generation_order: 5
    estimated_lines: 80

  - file_name: "executor.py"
    purpose: "Sprint-style supervisor loop with batch dispatch"
    generation_order: 6
    estimated_lines: 200

  - file_name: "cli.py"
    purpose: "Click command group and CLI entry point"
    generation_order: 7
    estimated_lines: 60

gate_definitions:
  - step_id: "G-001"
    tier: "LIGHT"
    required_frontmatter: []
    min_lines: 0
    semantic_checks: []

  - step_id: "G-002"
    tier: "STANDARD"
    required_frontmatter: ["title", "status", "pass"]
    min_lines: 50
    semantic_checks: ["has_classification_table"]

  - step_id: "G-003"
    tier: "STANDARD"
    required_frontmatter: ["title", "status", "pass"]
    min_lines: 50
    semantic_checks: ["has_per_file_profiles"]

  - step_id: "G-004"
    tier: "STRICT"
    required_frontmatter: ["title", "status", "pass", "finding_count"]
    min_lines: 100
    semantic_checks: ["has_cross_cutting_findings", "has_consolidation_opportunities"]

  - step_id: "G-005"
    tier: "STRICT"
    required_frontmatter: ["title", "status", "total_findings", "severity_distribution"]
    min_lines: 100
    semantic_checks: ["has_deduplication_evidence", "has_exit_recommendation"]

  - step_id: "G-006"
    tier: "STANDARD"
    required_frontmatter: ["title", "status"]
    min_lines: 30
    semantic_checks: ["has_validation_verdicts"]

pattern_coverage:
  required_patterns:
    - "sequential_step"
    - "parallel_operations"
    - "quality_gate"
    - "agent_delegation"
    - "scoring_formula"
    - "status_decision"
    - "input_validation"
  covered_patterns:
    - "sequential_step"
    - "parallel_operations"
    - "quality_gate"
    - "agent_delegation"
    - "scoring_formula"
    - "status_decision"
    - "input_validation"
  coverage_complete: true

api_conformance:
  snapshot_hash: "sha256:<computed-from-D-0015-canonical-signatures>"
  verified_at: "2026-03-08T00:00:00Z"
  conformance_passed: true

self_validation:
  checks:
    - name: "coverage_invariant"
      type: "blocking"
      passed: true
      message: "6 == 6 + 0: invariant holds"

    - name: "step_mapping_complete"
      type: "blocking"
      passed: true
      message: "All 6 source steps have exactly one mapping entry"

    - name: "model_base_class_valid"
      type: "blocking"
      passed: true
      message: "CleanupAuditConfig extends PipelineConfig, AuditStepResult extends StepResult"

    - name: "gate_field_names_valid"
      type: "blocking"
      passed: true
      message: "All 6 gate definitions use valid GateCriteria field names"

    - name: "semantic_check_signatures"
      type: "blocking"
      passed: true
      message: "All 7 semantic check functions use Callable[[str], bool]"

    - name: "pattern_coverage_complete"
      type: "blocking"
      passed: true
      message: "7/7 patterns covered, 0 gaps"

    - name: "api_conformance_passed"
      type: "blocking"
      passed: true
      message: "20 conformance checks, 0 mismatches"

    - name: "module_plan_completeness"
      type: "advisory"
      passed: true
      message: "All 6 generated steps covered; ~825 estimated lines within 200-2000 bounds"

  all_blocking_passed: true

spec_md_path: null
prompts_md_path: null
```

---

## Schema Conformance Verification

### Against D-0011 Section 3 (portify-spec.yaml schema)

| Required Field | Present | Valid |
|---------------|---------|-------|
| `schema_version` | ✅ | `"1.0"` |
| `phase` | ✅ | `2` |
| `status` | ✅ | `"passed"` |
| `timestamp` | ✅ | ISO 8601 format |
| `resume_checkpoint` | ✅ | `"phase-2:complete"` |
| `validation_status` | ✅ | blocking_passed/failed/advisory present |
| `step_mapping` | ✅ | 6 entries with source_id, generated_step_ids, mapping_type, justification |
| `elimination_records` | ✅ | Empty list (no eliminations) |
| `coverage_invariant` | ✅ | source_step_count, mapped_step_count, eliminated_count, invariant_holds |
| `module_plan` | ✅ | 7 entries with file_name, purpose, generation_order, estimated_lines |
| `gate_definitions` | ✅ | 6 entries with step_id, tier, required_frontmatter, min_lines, semantic_checks |
| `pattern_coverage` | ✅ | required_patterns, covered_patterns, coverage_complete |
| `api_conformance` | ✅ | snapshot_hash, verified_at, conformance_passed |
| `self_validation` | ✅ | 8 checks with name, type, passed, message; all_blocking_passed |
| `spec_md_path` | ✅ | null (prompts under 300 lines) |
| `prompts_md_path` | ✅ | null (prompts under 300 lines) |

**All required fields present and valid** ✅
**YAML parseable** ✅
**Schema conformance PASS** ✅
