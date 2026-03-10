# D-0015: API Snapshot Schema

**Task**: T02.04
**Roadmap Items**: R-028
**Date**: 2026-03-08

---

## api-snapshot.yaml Schema

The API snapshot captures the live signatures of 7 pipeline API surfaces at the time of Phase 0 execution. The content hash enables downstream phases to verify API conformance.

```yaml
schema_version: "1.0"
captured_at: <ISO8601>                   # Timestamp of capture
source_files:
  models: "src/superclaude/cli/pipeline/models.py"
  gates: "src/superclaude/cli/pipeline/gates.py"
content_hash: <string>                   # SHA-256 of the canonical signature block below

signatures:
  SemanticCheck:
    source_file: "models.py"
    kind: "dataclass"
    fields:
      - name: "name"
        type: "str"
        default: null
      - name: "check_fn"
        type: "Callable[[str], bool]"
        default: null
      - name: "failure_message"
        type: "str"
        default: null

  GateCriteria:
    source_file: "models.py"
    kind: "dataclass"
    fields:
      - name: "required_frontmatter_fields"
        type: "list[str]"
        default: null
      - name: "min_lines"
        type: "int"
        default: null
      - name: "enforcement_tier"
        type: 'Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"]'
        default: '"STANDARD"'
      - name: "semantic_checks"
        type: "list[SemanticCheck] | None"
        default: "None"

  gate_passed:
    source_file: "gates.py"
    kind: "function"
    signature: "gate_passed(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]"
    parameters:
      - name: "output_file"
        type: "Path"
      - name: "criteria"
        type: "GateCriteria"
    return_type: "tuple[bool, str | None]"

  PipelineConfig:
    source_file: "models.py"
    kind: "dataclass"
    fields:
      - name: "work_dir"
        type: "Path"
        default: 'field(default_factory=lambda: Path("."))'
      - name: "dry_run"
        type: "bool"
        default: "False"
      - name: "max_turns"
        type: "int"
        default: "100"
      - name: "model"
        type: "str"
        default: '""'
      - name: "permission_flag"
        type: "str"
        default: '"--dangerously-skip-permissions"'
      - name: "debug"
        type: "bool"
        default: "False"
      - name: "grace_period"
        type: "int"
        default: "0"

  Step:
    source_file: "models.py"
    kind: "dataclass"
    fields:
      - name: "id"
        type: "str"
        default: null
      - name: "prompt"
        type: "str"
        default: null
      - name: "output_file"
        type: "Path"
        default: null
      - name: "gate"
        type: "Optional[GateCriteria]"
        default: null
      - name: "timeout_seconds"
        type: "int"
        default: null
      - name: "inputs"
        type: "list[Path]"
        default: "field(default_factory=list)"
      - name: "retry_limit"
        type: "int"
        default: "1"
      - name: "model"
        type: "str"
        default: '""'
      - name: "gate_mode"
        type: "GateMode"
        default: "GateMode.BLOCKING"

  StepResult:
    source_file: "models.py"
    kind: "dataclass"
    fields:
      - name: "step"
        type: "Optional[Step]"
        default: "None"
      - name: "status"
        type: "StepStatus"
        default: "StepStatus.PENDING"
      - name: "attempt"
        type: "int"
        default: "1"
      - name: "gate_failure_reason"
        type: "str | None"
        default: "None"
      - name: "started_at"
        type: "datetime"
        default: "field(default_factory=lambda: datetime.now(timezone.utc))"
      - name: "finished_at"
        type: "datetime"
        default: "field(default_factory=lambda: datetime.now(timezone.utc))"

  GateMode:
    source_file: "models.py"
    kind: "enum"
    members:
      - name: "BLOCKING"
        value: '"BLOCKING"'
      - name: "TRAILING"
        value: '"TRAILING"'
```

## Content Hash Computation

The SHA-256 hash is computed over the canonical representation of the signatures block:
1. Serialize the `signatures` section to sorted-key JSON
2. Compute SHA-256 of the UTF-8 encoded JSON string
3. Store as `"sha256:<hex-digest>"`

This ensures that any change to API signatures (field additions, type changes, renames) results in a different hash, enabling drift detection in downstream phases.
