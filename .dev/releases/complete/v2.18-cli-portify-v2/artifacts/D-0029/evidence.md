# portify-codegen.yaml — Phase 3 Output Contract
# Produced for: sc-cleanup-audit-protocol
# Schema: D-0011 Section 4

schema_version: "1.0"
phase: 3
status: "passed"
timestamp: "2026-03-08T00:00:00Z"
resume_checkpoint: "phase-3:complete"
validation_status:
  blocking_passed: 9
  blocking_failed: 0
  advisory:
    - "total_line_count: 1838 lines across 12 files"

generated_files:
  - file_name: "models.py"
    path: "src/superclaude/cli/cleanup_audit/models.py"
    line_count: 230
    generation_order: 1
    ast_valid: true

  - file_name: "gates.py"
    path: "src/superclaude/cli/cleanup_audit/gates.py"
    line_count: 163
    generation_order: 2
    ast_valid: true

  - file_name: "prompts.py"
    path: "src/superclaude/cli/cleanup_audit/prompts.py"
    line_count: 128
    generation_order: 3
    ast_valid: true

  - file_name: "config.py"
    path: "src/superclaude/cli/cleanup_audit/config.py"
    line_count: 102
    generation_order: 4
    ast_valid: true

  - file_name: "monitor.py"
    path: "src/superclaude/cli/cleanup_audit/monitor.py"
    line_count: 195
    generation_order: 5
    ast_valid: true

  - file_name: "process.py"
    path: "src/superclaude/cli/cleanup_audit/process.py"
    line_count: 72
    generation_order: 6
    ast_valid: true

  - file_name: "executor.py"
    path: "src/superclaude/cli/cleanup_audit/executor.py"
    line_count: 319
    generation_order: 7
    ast_valid: true

  - file_name: "tui.py"
    path: "src/superclaude/cli/cleanup_audit/tui.py"
    line_count: 147
    generation_order: 8
    ast_valid: true

  - file_name: "logging_.py"
    path: "src/superclaude/cli/cleanup_audit/logging_.py"
    line_count: 146
    generation_order: 9
    ast_valid: true

  - file_name: "diagnostics.py"
    path: "src/superclaude/cli/cleanup_audit/diagnostics.py"
    line_count: 205
    generation_order: 10
    ast_valid: true

  - file_name: "commands.py"
    path: "src/superclaude/cli/cleanup_audit/commands.py"
    line_count: 120
    generation_order: 11
    ast_valid: true

  - file_name: "__init__.py"
    path: "src/superclaude/cli/cleanup_audit/__init__.py"
    line_count: 11
    generation_order: 12
    ast_valid: true

per_file_validation:
  - file_name: "models.py"
    checks:
      - { name: "ast_parse", type: "blocking", passed: true, message: "Valid Python syntax" }
      - { name: "import_paths", type: "blocking", passed: true, message: "All import paths valid" }
      - { name: "base_class_contract", type: "blocking", passed: true, message: "CleanupAuditConfig extends PipelineConfig, CleanupAuditStepResult extends StepResult" }
      - { name: "gate_field_names", type: "blocking", passed: true, message: "N/A" }
      - { name: "semantic_check_sig", type: "blocking", passed: true, message: "N/A" }
    all_blocking_passed: true

  - file_name: "gates.py"
    checks:
      - { name: "ast_parse", type: "blocking", passed: true, message: "Valid Python syntax" }
      - { name: "import_paths", type: "blocking", passed: true, message: "All import paths valid" }
      - { name: "base_class_contract", type: "blocking", passed: true, message: "N/A" }
      - { name: "gate_field_names", type: "blocking", passed: true, message: "GateCriteria fields match API snapshot" }
      - { name: "semantic_check_sig", type: "blocking", passed: true, message: "All 7 semantic checks use Callable[[str], bool]" }
    all_blocking_passed: true

cross_file_validation:
  module_complete: true
  import_graph_acyclic: true
  init_exports_match: true
  step_count_matches: true
  all_passed: true

atomic_generation: true
generation_halted: false
halt_file: null
