# D-0011: Per-Phase Contract Schemas

**Task**: T02.02
**Roadmap Items**: R-021
**Date**: 2026-03-08
**Depends On**: D-0010 (common header schema, versioning policy, null-field policy)

---

## 1. portify-prerequisites.yaml (Phase 0 Output → Phase 1 Input)

**Producer**: Phase 0 (Prerequisite Scanning)
**Consumer**: Phase 1 (Workflow Analysis)
**FR References**: FR-010, FR-011, FR-012, FR-013, FR-014

```yaml
# Common header (from D-0010)
schema_version: "1.0"
phase: 0
status: "passed" | "failed" | "skipped"
timestamp: <ISO8601>
resume_checkpoint: "phase-0:<step>"
validation_status:
  blocking_passed: <int>
  blocking_failed: <int>
  advisory: <list[string]>

# Phase 0 specific fields
workflow_path: <string>                  # Resolved absolute path to workflow root dir
workflow_components:                     # Discovered workflow file inventory
  command_md: <string | null>            # Path to command .md file
  skill_md: <string | null>              # Path to SKILL.md
  refs: <list[string]>                   # Paths to ref files
  rules: <list[string]>                  # Paths to rule files
  templates: <list[string]>              # Paths to template files
  scripts: <list[string]>               # Paths to script files
  agents: <list[string]>                 # Paths to referenced agent files

api_snapshot:                            # Live API surface capture
  snapshot_path: <string>                # Path to api-snapshot.yaml file
  content_hash: <string>                 # SHA-256 hash of snapshot content
  signatures:                            # Extracted API signatures
    SemanticCheck: <string>              # Signature string
    GateCriteria: <string>               # Signature string
    gate_passed: <string>                # Signature string
    PipelineConfig: <string>             # Signature string
    Step: <string>                       # Signature string
    StepResult: <string>                 # Signature string
    GateMode: <string>                   # Signature string

collision_status: <string>               # One of: "clean", "portified_exists", "non_portified_exists", "name_collision"
collision_details: <string | null>       # Human-readable collision description if not "clean"

pattern_scan_result: <string>            # One of: "supported", "unsupported"
unsupported_patterns: <list[string]>     # Names of detected unsupported patterns (empty if supported)

output_dir: <string>                     # Resolved output directory path
derived_name: <string>                   # Derived CLI name (kebab-case)
```

---

## 2. portify-analysis.yaml (Phase 1 Output → Phase 2 Input)

**Producer**: Phase 1 (Workflow Analysis)
**Consumer**: Phase 2 (Pipeline Specification/Design)
**FR References**: FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-022

```yaml
# Common header
schema_version: "1.0"
phase: 1
status: "passed" | "failed" | "skipped"
timestamp: <ISO8601>
resume_checkpoint: "phase-1:<step>"
validation_status:
  blocking_passed: <int>
  blocking_failed: <int>
  advisory: <list[string]>

# Phase 1 specific fields
component_inventory:                     # FR-015: Component inventory with stable IDs
  - component_id: <string>              # Format: "C-NNN" (e.g., "C-001")
    path: <string>                       # Relative path from project root
    type: <string>                       # One of: "command", "skill", "ref", "rule", "template", "script", "agent"
    line_count: <int>                    # Number of lines
    purpose: <string>                    # Brief description

step_graph:                              # FR-016: Step decomposition with stable IDs
  - source_id: <string>                  # Format: "S-NNN" (e.g., "S-001")
    name: <string>                       # Human-readable step name
    classification: <string>             # One of: "pure_programmatic", "claude_assisted", "hybrid"
    classification_confidence: <float>   # 0.0-1.0. Flag for review if < 0.7
    inputs: <list[string]>              # List of input artifact names or source_ids
    output: <string>                     # Output artifact name
    gate_tier: <string>                  # One of: "EXEMPT", "LIGHT", "STANDARD", "STRICT"
    gate_mode: <string>                  # One of: "BLOCKING", "TRAILING"
    agent: <string | null>               # Agent name if Claude-assisted, null if programmatic
    parallel_group: <int | null>         # Parallel group number, null if sequential
    timeout_seconds: <int>               # Per-step timeout
    retry_limit: <int>                   # Retry attempts on gate failure
    notes: <string | null>               # Special considerations

dependency_dag:                          # FR-018: Directed acyclic graph
  nodes: <list[string]>                  # List of source_ids
  edges:                                 # Dependency edges
    - from: <string>                     # source_id of producer
      to: <string>                       # source_id of consumer
  is_acyclic: <bool>                     # True if DAG validation passed

gate_assignments:                        # FR-019, FR-020: Gate tier and mode assignments
  - source_id: <string>                  # Step source_id
    tier: <string>                       # "EXEMPT" | "LIGHT" | "STANDARD" | "STRICT"
    mode: <string>                       # "BLOCKING" | "TRAILING"
    safety_escalated: <bool>             # True if trailing gate was escalated to blocking
    escalation_reason: <string | null>   # Reason for escalation, null if not escalated

self_validation:                         # FR-021: 7 self-validation checks
  checks:
    - name: <string>                     # Check name
      type: <string>                     # "blocking" | "advisory"
      passed: <bool>                     # Whether check passed
      message: <string>                  # Human-readable result message

  all_blocking_passed: <bool>            # True if all 6 blocking checks passed

divergence_warnings: <list[string]>      # FR-050: Ambiguous step boundary warnings

conservation_invariant:                  # FR-049: Conservation check
  source_step_count: <int>               # |source_steps|
  classified_step_count: <int>           # |classified_steps|
  invariant_holds: <bool>               # source_step_count == classified_step_count

analysis_md_path: <string>               # Path to portify-analysis.md output
analysis_md_line_count: <int>            # Line count (must be < 400)

user_review_status: <string | null>      # One of: "pending", "approved", "overrides_applied", null
user_overrides: <list[object]>           # List of classification overrides from user review
```

---

## 3. portify-spec.yaml (Phase 2 Output → Phase 3 Input)

**Producer**: Phase 2 (Pipeline Specification/Design)
**Consumer**: Phase 3 (Code Generation)
**FR References**: FR-024, FR-025, FR-026, FR-027, FR-028, FR-029, FR-030, FR-031, FR-032, FR-033

```yaml
# Common header
schema_version: "1.0"
phase: 2
status: "passed" | "failed" | "skipped"
timestamp: <ISO8601>
resume_checkpoint: "phase-2:<step>"
validation_status:
  blocking_passed: <int>
  blocking_failed: <int>
  advisory: <list[string]>

# Phase 2 specific fields
step_mapping:                            # FR-024: Source-to-generated step mapping
  - source_id: <string>                  # Source step S-NNN
    generated_step_ids: <list[string]>   # Generated step IDs (1:1, 1:N, N:1, 1:0)
    mapping_type: <string>               # One of: "1:1", "1:N", "N:1", "1:0"
    justification: <string | null>       # Required for 1:0 eliminations

elimination_records:                     # FR-025: Eliminated step records
  - source_id: <string>                  # Eliminated source step
    reason: <string>                     # Why eliminated
    approved_by: <string>                # "auto" or "user"

coverage_invariant:                      # FR-025, FR-049
  source_step_count: <int>               # |source_step_registry|
  mapped_step_count: <int>               # |mapped_steps|
  eliminated_count: <int>                # |elimination_records|
  invariant_holds: <bool>               # source == mapped + eliminated

module_plan:                             # FR-026, FR-034: Files to generate
  - file_name: <string>                  # e.g., "models.py"
    purpose: <string>                    # Brief description
    generation_order: <int>              # 1-12 dependency order
    estimated_lines: <int>               # Estimated line count

gate_definitions:                        # FR-028: Gate designs
  - step_id: <string>                    # Generated step ID
    tier: <string>                       # "EXEMPT" | "LIGHT" | "STANDARD" | "STRICT"
    required_frontmatter: <list[string]> # Required frontmatter fields
    min_lines: <int>                     # Minimum line count
    semantic_checks: <list[string]>      # Names of semantic check functions

pattern_coverage:                        # FR-031: Pattern coverage matrix
  required_patterns: <list[string]>      # Patterns needed by this workflow
  covered_patterns: <list[string]>       # Patterns the design covers
  coverage_complete: <bool>              # All required patterns covered

api_conformance:                         # RISK-001: API snapshot conformance
  snapshot_hash: <string>                # SHA-256 from Phase 0
  verified_at: <string>                  # ISO 8601 timestamp of verification
  conformance_passed: <bool>             # True if all API references match snapshot

self_validation:                         # FR-032: 8 self-validation checks
  checks:
    - name: <string>
      type: <string>                     # "blocking" | "advisory"
      passed: <bool>
      message: <string>
  all_blocking_passed: <bool>            # True if all 7 blocking checks passed

spec_md_path: <string | null>            # Path to portify-spec.md
prompts_md_path: <string | null>         # Path to portify-prompts.md (if split)
```

---

## 4. portify-codegen.yaml (Phase 3 Output → Phase 4 Input)

**Producer**: Phase 3 (Code Generation)
**Consumer**: Phase 4 (Integration)
**FR References**: FR-034, FR-035, FR-036, FR-037, FR-038

```yaml
# Common header
schema_version: "1.0"
phase: 3
status: "passed" | "failed" | "skipped"
timestamp: <ISO8601>
resume_checkpoint: "phase-3:<step>"
validation_status:
  blocking_passed: <int>
  blocking_failed: <int>
  advisory: <list[string]>

# Phase 3 specific fields
generated_files:                         # FR-034: Generated file inventory
  - file_name: <string>                  # e.g., "models.py"
    path: <string>                       # Full path to generated file
    line_count: <int>                    # Actual line count
    generation_order: <int>              # Order generated (1-12+)
    ast_valid: <bool>                    # FR-036: ast.parse() passed

per_file_validation:                     # FR-036: Per-file validation results
  - file_name: <string>
    checks:
      - name: <string>                   # Check name
        type: <string>                   # "blocking" | "advisory"
        passed: <bool>
        message: <string>
    all_blocking_passed: <bool>

cross_file_validation:                   # FR-037: Cross-file validation results
  module_complete: <bool>                # All required files present
  import_graph_acyclic: <bool>           # No circular imports
  init_exports_match: <bool>             # __init__.py exports match
  step_count_matches: <bool>             # Step count matches spec
  all_passed: <bool>                     # All 4 checks passed

atomic_generation: <bool>                # FR-035: True if all files generated atomically
generation_halted: <bool>                # True if generation halted on failure
halt_file: <string | null>               # File that caused halt, null if no halt
```

---

## 5. portify-integration.yaml (Phase 4 Output → Return Contract)

**Producer**: Phase 4 (Integration)
**Consumer**: Return contract aggregator
**FR References**: FR-039, FR-040, FR-041, FR-042
**OQ Resolution**: OQ-004

```yaml
# Common header
schema_version: "1.0"
phase: 4
status: "passed" | "failed" | "skipped"
timestamp: <ISO8601>
resume_checkpoint: "phase-4:<step>"
validation_status:
  blocking_passed: <int>
  blocking_failed: <int>
  advisory: <list[string]>

# Phase 4 specific fields (per OQ-004 resolution)
main_py_patched: <bool>                  # FR-039: main.py import + add_command succeeded
command_registered: <bool>               # FR-040: Click command group accessible
test_file_generated: <bool>              # FR-041: Structural test file created
smoke_test_passed: <bool>                # FR-040: Integration smoke test passed

test_file_path: <string | null>          # Path to generated test file
summary_md_path: <string | null>         # Path to portify-summary.md (FR-042)
```

---

## 6. Return Contract Structure

**Producer**: Aggregated from all phase contracts
**Consumer**: Caller of sc:cli-portify
**FR References**: FR-043

```yaml
# Common header
schema_version: "1.0"
phase: -1                                # -1 indicates return/aggregate contract
status: "passed" | "failed" | "skipped"  # Overall pipeline status
timestamp: <ISO8601>
resume_checkpoint: <string | null>       # Last successful checkpoint, null if fully passed
validation_status:
  blocking_passed: <int>                 # Total across all phases
  blocking_failed: <int>                 # Total across all phases
  advisory: <list[string]>              # Aggregated advisories

# FR-043 return contract fields
failure_phase: <int | null>              # Phase number where failure occurred, null if passed
failure_type: <string | null>            # One of: "validation_failed", "gate_failed", "unsupported_pattern",
                                         #         "collision", "generation_error", "integration_error", null
generated_files: <list[string]>          # All files generated (paths)
counts:                                  # Aggregate counts
  total_steps: <int>                     # Total steps in pipeline
  programmatic_steps: <int>              # Pure programmatic steps
  claude_assisted_steps: <int>           # Claude-assisted steps
  hybrid_steps: <int>                    # Hybrid steps
  files_generated: <int>                 # Number of files generated
  gates_passed: <int>                    # Number of gates that passed
  gates_failed: <int>                    # Number of gates that failed

api_snapshot_hash: <string | null>       # SHA-256 hash from Phase 0 snapshot
resume_command: <string | null>          # CLI command to resume from failure point
warnings: <list[string]>                 # Aggregated warnings from all phases

phase_contracts:                         # All phase contracts embedded
  phase_0: <object | null>               # portify-prerequisites content or null
  phase_1: <object | null>               # portify-analysis content or null
  phase_2: <object | null>               # portify-spec content or null
  phase_3: <object | null>               # portify-codegen content or null
  phase_4: <object | null>               # portify-integration content or null
```

---

## Cross-Phase Field Coverage Verification

Every field produced by one phase and consumed by a downstream phase is accounted for:

| Produced Field | Producer Phase | Consumer Phase | Purpose |
|---------------|---------------|----------------|---------|
| `workflow_path` | 0 | 1 | Locate workflow for analysis |
| `workflow_components` | 0 | 1 | Component discovery input |
| `api_snapshot.content_hash` | 0 | 2, 3 | API conformance verification |
| `api_snapshot.signatures` | 0 | 2, 3 | Gate design and code gen validation |
| `collision_status` | 0 | 4 | Integration collision re-check |
| `pattern_scan_result` | 0 | 1 | Gate Phase 1 entry on unsupported |
| `output_dir` | 0 | 3, 4 | Code generation target directory |
| `derived_name` | 0 | 3, 4 | CLI name for commands and imports |
| `component_inventory` | 1 | 2 | Step mapping input |
| `step_graph` | 1 | 2 | Spec design input |
| `dependency_dag` | 1 | 2 | Executor design input |
| `gate_assignments` | 1 | 2 | Gate design input |
| `conservation_invariant` | 1, 2 | Validation | Invariant holds across phases |
| `step_mapping` | 2 | 3 | Code generation blueprint |
| `module_plan` | 2 | 3 | File generation order |
| `gate_definitions` | 2 | 3 | Gate code generation input |
| `generated_files` | 3 | 4 | Integration file list |
| `main_py_patched` | 4 | Return | Integration status |
| `smoke_test_passed` | 4 | Return | Integration validation |

**Verification**: No consuming phase references a field not defined in the producing phase's schema. All cross-phase data flows are explicitly defined above.
