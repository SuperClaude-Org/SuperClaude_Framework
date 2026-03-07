---
source_skill: sc-cleanup-audit-protocol
cli_name: cleanup-audit
package: src/superclaude/cli/cleanup_audit/
step_count: 11
files_to_generate: 12
base_types: PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck
---

# Pipeline Specification: cleanup-audit

## 1. Step Graph Design

### Static Steps (always present)

```python
# Step definitions are templates; actual batched steps are generated at runtime
STEP_INVENTORY = Step(
    id="repo-inventory",
    prompt="",                          # No Claude — pure programmatic
    output_file=Path("inventory.json"),
    gate=INVENTORY_GATE,
    timeout_seconds=60,
    inputs=[],
    retry_limit=0,
    model="",                           # Not used
)

STEP_CONFIGURE = Step(
    id="configure-passes",
    prompt="",                          # No Claude — pure programmatic
    output_file=Path("pass-config.json"),
    gate=CONFIGURE_GATE,
    timeout_seconds=10,
    inputs=[Path("inventory.json")],
    retry_limit=0,
    model="",
)
```

### Dynamic Batch Steps (generated at runtime)

Pass 1, 2, and 3 batch steps are generated dynamically from `pass-config.json`:

```python
def build_pass_steps(pass_config: PassConfig, pass_num: int) -> list:
    """Generate batch steps for a given pass.

    Returns:
        [
            [batch_step_1, batch_step_2, ...],  # Parallel group
            validate_step,                       # Sequential
            consolidate_step,                    # Sequential
        ]
    """
    batch_steps = []
    for batch in pass_config.batches:
        batch_steps.append(Step(
            id=f"pass{pass_num}-batch-{batch.id:02d}",
            prompt=build_batch_prompt(pass_num, batch),
            output_file=Path(f"pass{pass_num}/batch-{batch.id:02d}.md"),
            gate=BATCH_GATES[pass_num],
            timeout_seconds=BATCH_TIMEOUTS[pass_num],
            inputs=batch.input_files,
            retry_limit=1,
            model=PASS_MODELS[pass_num],
        ))

    validate_step = Step(
        id=f"pass{pass_num}-validate",
        prompt=build_validate_prompt(pass_num),
        output_file=Path(f"pass{pass_num}/validation-report.md"),
        gate=VALIDATE_GATE,
        timeout_seconds=300,
        inputs=[s.output_file for s in batch_steps],
        retry_limit=1,
        model="sonnet",
    )

    consolidate_step = Step(
        id=f"pass{pass_num}-consolidate",
        prompt=build_consolidate_prompt(pass_num),
        output_file=Path(f"pass{pass_num}-summary.md"),
        gate=CONSOLIDATE_GATES[pass_num],
        timeout_seconds=600,
        inputs=[s.output_file for s in batch_steps]
                + [validate_step.output_file],
        retry_limit=1,
        model="sonnet",
    )

    return [batch_steps, validate_step, consolidate_step]
```

### Final Report Step (conditional on --pass all)

```python
STEP_FINAL_REPORT = Step(
    id="final-report",
    prompt=build_final_report_prompt(),
    output_file=Path("final-report.md"),
    gate=FINAL_REPORT_GATE,
    timeout_seconds=900,
    inputs=[
        Path("pass1-summary.md"),
        Path("pass2-summary.md"),
        Path("pass3-summary.md"),
    ],
    retry_limit=1,
    model="sonnet",
)
```

### Full Pipeline Assembly

```python
def build_step_graph(config: CleanupAuditConfig) -> list:
    """Build the complete step graph based on configuration.

    The graph structure varies based on --pass flag:
      surface:       [inventory, configure, [pass1-batches], p1-validate, p1-consolidate]
      structural:    [inventory, configure, [pass2-batches], p2-validate, p2-consolidate]
      cross-cutting: [inventory, configure, [pass3-batches], p3-validate, p3-consolidate]
      all:           [inventory, configure,
                      [pass1-batches], p1-validate, p1-consolidate,
                      [pass2-batches], p2-validate, p2-consolidate,
                      [pass3-batches], p3-validate, p3-consolidate,
                      final-report]
    """
    graph = [STEP_INVENTORY, STEP_CONFIGURE]

    for pass_num in config.passes_to_run:
        pass_config = config.pass_configs[pass_num]
        graph.extend(build_pass_steps(pass_config, pass_num))

    if config.run_final_report:
        graph.append(STEP_FINAL_REPORT)

    return graph
```

## 2. Data Models

### models.py

```python
"""Cleanup-audit pipeline data models.

Extends pipeline base types (PipelineConfig, Step, StepResult, StepStatus)
with audit-specific domain types.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    SemanticCheck,
    Step,
    StepResult,
    StepStatus,
)


# --- Enums ---

class AuditPass(Enum):
    """Which audit pass to execute."""
    SURFACE = 1
    STRUCTURAL = 2
    CROSS_CUTTING = 3

    @property
    def agent_name(self) -> str:
        return {1: "audit-scanner", 2: "audit-analyzer", 3: "audit-comparator"}[self.value]

    @property
    def model(self) -> str:
        return {1: "haiku", 2: "sonnet", 3: "sonnet"}[self.value]

    @property
    def default_batch_size(self) -> int:
        return {1: 50, 2: 25, 3: 30}[self.value]


class FileDomain(Enum):
    """Domain classification for repository files."""
    INFRASTRUCTURE = "infrastructure"
    CONFIG = "config"
    TESTS = "tests"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DOCUMENTATION = "documentation"
    ASSETS = "assets"
    OTHER = "other"


class FileClassification(Enum):
    """Audit classification for a file."""
    DELETE = "DELETE"
    REVIEW = "REVIEW"
    KEEP = "KEEP"
    CONSOLIDATE = "CONSOLIDATE"
    MOVE = "MOVE"
    FLAG = "FLAG"
    BROKEN_REF = "BROKEN_REF"
    NOT_AUDITED = "NOT_AUDITED"


class AuditStepStatus(Enum):
    """Extended status for audit pipeline steps."""
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"       # Completed but no structured markers
    PASS_PARTIAL = "pass_partial"           # Some files not reached (partial coverage)
    INCOMPLETE = "incomplete"               # Budget exhausted mid-batch
    VALIDATION_FAIL = "validation_fail"     # Spot-check failed (>= 20% discrepancy)
    CRITICAL_FAIL = "critical_fail"         # False-negative DELETE detected
    HALT = "halt"                           # Step recommends stopping
    TIMEOUT = "timeout"                     # Hard timeout exceeded
    ERROR = "error"                         # Process crash
    SKIPPED = "skipped"                     # Skipped by config (pass not selected)

    @property
    def is_success(self) -> bool:
        return self in (self.PASS, self.PASS_NO_SIGNAL, self.PASS_PARTIAL)

    @property
    def is_retriable(self) -> bool:
        return self in (self.INCOMPLETE, self.VALIDATION_FAIL, self.TIMEOUT)


# --- File & Batch Types ---

@dataclass
class FileEntry:
    """A single file in the repository inventory."""
    path: str
    domain: FileDomain
    batch_id: int = 0
    classification: FileClassification = FileClassification.NOT_AUDITED
    pass1_result: Optional[str] = None      # DELETE/REVIEW/KEEP from pass 1


@dataclass
class BatchAssignment:
    """A batch of files assigned to one agent subprocess."""
    id: int
    files: list[FileEntry] = field(default_factory=list)
    domain: FileDomain = FileDomain.OTHER
    pass_num: int = 1

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def file_paths(self) -> list[str]:
        return [f.path for f in self.files]


@dataclass
class PassConfig:
    """Configuration for a single audit pass."""
    pass_num: int
    agent: str
    model: str
    batches: list[BatchAssignment] = field(default_factory=list)
    batch_size: int = 50
    max_concurrency: int = 8

    @property
    def total_files(self) -> int:
        return sum(b.file_count for b in self.batches)

    @property
    def batch_count(self) -> int:
        return len(self.batches)


# --- Inventory ---

@dataclass
class RepoInventory:
    """Complete file inventory with domain classification and batch assignments."""
    files: list[FileEntry] = field(default_factory=list)
    domains: dict[str, int] = field(default_factory=dict)
    total_files: int = 0
    target_path: str = "."
    repo_name: str = ""
    file_types: dict[str, int] = field(default_factory=dict)

    def filter_by_domain(self, domain: FileDomain) -> list[FileEntry]:
        return [f for f in self.files if f.domain == domain]

    def filter_by_classification(self, *classes: FileClassification) -> list[FileEntry]:
        return [f for f in self.files if f.classification in classes]

    def to_json(self) -> str:
        return json.dumps({
            "files": [{"path": f.path, "domain": f.domain.value, "batch_id": f.batch_id}
                       for f in self.files],
            "domains": self.domains,
            "total_files": self.total_files,
            "target_path": self.target_path,
            "repo_name": self.repo_name,
            "file_types": self.file_types,
        }, indent=2)

    @classmethod
    def from_json(cls, data: str) -> RepoInventory:
        d = json.loads(data)
        files = [FileEntry(path=f["path"], domain=FileDomain(f["domain"]),
                           batch_id=f.get("batch_id", 0))
                 for f in d["files"]]
        return cls(
            files=files,
            domains=d.get("domains", {}),
            total_files=d.get("total_files", len(files)),
            target_path=d.get("target_path", "."),
            repo_name=d.get("repo_name", ""),
            file_types=d.get("file_types", {}),
        )


# --- Config ---

@dataclass
class CleanupAuditConfig(PipelineConfig):
    """Configuration for the cleanup-audit pipeline."""

    # Required: target
    target_path: Path = field(default_factory=lambda: Path("."))

    # Pass selection
    pass_selection: str = "all"           # surface|structural|cross-cutting|all
    focus: str = "all"                    # infrastructure|frontend|backend|all

    # Batch configuration
    batch_size_override: Optional[int] = None   # Override default per-pass batch sizes
    max_concurrency: int = 8                     # Max concurrent Claude subprocesses

    # Timeouts
    batch_timeout: int = 600              # Per-batch subprocess timeout
    stall_timeout: int = 120              # Seconds without output before stall detection

    # Model overrides
    pass1_model: str = "haiku"
    pass2_model: str = "sonnet"
    pass3_model: str = "sonnet"

    # Resume
    resume: bool = False                  # Resume from last checkpoint

    # Computed
    pass_configs: dict[int, PassConfig] = field(default_factory=dict)
    inventory: Optional[RepoInventory] = None

    @property
    def passes_to_run(self) -> list[int]:
        mapping = {
            "surface": [1],
            "structural": [2],
            "cross-cutting": [3],
            "all": [1, 2, 3],
        }
        return mapping.get(self.pass_selection, [1, 2, 3])

    @property
    def run_final_report(self) -> bool:
        return self.pass_selection == "all"

    @property
    def audit_dir(self) -> Path:
        return self.work_dir / ".claude-audit"

    def pass_dir(self, pass_num: int) -> Path:
        return self.audit_dir / f"pass{pass_num}"

    def batch_report_path(self, pass_num: int, batch_id: int) -> Path:
        return self.pass_dir(pass_num) / f"batch-{batch_id:02d}.md"

    def validation_report_path(self, pass_num: int) -> Path:
        return self.pass_dir(pass_num) / "validation-report.md"

    def pass_summary_path(self, pass_num: int) -> Path:
        return self.audit_dir / f"pass{pass_num}-summary.md"

    def final_report_path(self) -> Path:
        return self.audit_dir / "final-report.md"

    def progress_path(self) -> Path:
        return self.audit_dir / "progress.json"


# --- Results ---

@dataclass
class BatchResult:
    """Result of executing one batch subprocess."""
    batch_id: int
    pass_num: int
    status: AuditStepStatus = AuditStepStatus.PENDING
    exit_code: Optional[int] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    output_bytes: int = 0
    files_assigned: int = 0
    files_audited: int = 0
    classifications: dict[str, int] = field(default_factory=dict)  # e.g. {"DELETE": 3, "KEEP": 12}
    gate_details: dict = field(default_factory=dict)
    error_message: str = ""

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return 0.0

    @property
    def coverage(self) -> float:
        return self.files_audited / self.files_assigned if self.files_assigned else 0.0


@dataclass
class PassResult:
    """Aggregated result for one audit pass."""
    pass_num: int
    batch_results: list[BatchResult] = field(default_factory=list)
    validation_status: AuditStepStatus = AuditStepStatus.PENDING
    consolidation_status: AuditStepStatus = AuditStepStatus.PENDING
    discrepancy_rate: float = 0.0
    total_files_audited: int = 0
    total_files_assigned: int = 0
    aggregate_classifications: dict[str, int] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        return all(b.status.is_success for b in self.batch_results) and \
               self.validation_status.is_success and \
               self.consolidation_status.is_success

    @property
    def coverage(self) -> float:
        return self.total_files_audited / self.total_files_assigned if self.total_files_assigned else 0.0

    @property
    def failed_batches(self) -> list[BatchResult]:
        return [b for b in self.batch_results if not b.status.is_success]


@dataclass
class AuditResult:
    """Top-level result for the entire cleanup-audit pipeline run."""
    config: CleanupAuditConfig = field(default_factory=CleanupAuditConfig)
    pass_results: dict[int, PassResult] = field(default_factory=dict)
    final_report_status: AuditStepStatus = AuditStepStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    outcome: str = "in_progress"          # in_progress|completed|halted|error

    @property
    def success(self) -> bool:
        return self.outcome == "completed"

    @property
    def total_files_audited(self) -> int:
        # Pass 1 coverage is the primary metric (all files go through Pass 1)
        if 1 in self.pass_results:
            return self.pass_results[1].total_files_audited
        return 0

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0


# --- Monitor State ---

@dataclass
class BatchMonitorState:
    """Per-batch monitoring state extracted from NDJSON output."""
    batch_id: int = 0
    pass_num: int = 0
    output_bytes: int = 0
    last_growth_time: float = 0.0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    # Audit-specific signals
    files_processed: int = 0
    current_file: Optional[str] = None
    last_classification: Optional[str] = None
    sections_found: set = field(default_factory=set)
    errors_detected: int = 0


@dataclass
class PassMonitorState:
    """Aggregate monitoring state for all batches in a pass."""
    pass_num: int = 0
    total_batches: int = 0
    completed_batches: int = 0
    running_batches: int = 0
    failed_batches: int = 0
    batch_states: dict[int, BatchMonitorState] = field(default_factory=dict)

    @property
    def progress_pct(self) -> float:
        return self.completed_batches / self.total_batches * 100 if self.total_batches else 0.0
```

## 3. Prompt Designs

### prompts.py

Each function returns a complete prompt string that will be passed to Claude via `--print` or `-p` flag.

#### 3.1 Pass 1 Batch Prompt

```python
def build_pass1_batch_prompt(
    batch: BatchAssignment,
    config: CleanupAuditConfig,
) -> str:
    """Prompt for audit-scanner (haiku) — Pass 1 surface scan.

    Embeds: file list, batch metadata.
    Requires: batch-report.md format with DELETE/REVIEW/KEEP sections.
    Machine-readable markers: file count in Summary section.
    """
    file_list = "\n".join(f"- `{f}`" for f in batch.file_paths)

    return f"""You are an audit-scanner performing Pass 1 (Surface Scan) of a repository audit.

## Your Assignment
- **Batch**: {batch.id} of the audit
- **Files to audit**: {batch.file_count} files
- **Output file**: Write your report to the designated output file

## Files in This Batch
{file_list}

## Methodology

For EACH file in your batch, you MUST:

1. **Read** first 20-30 lines to understand purpose and identify file type
2. **Grep** for the filename across the repo: search for the basename in all source files
3. **Check imports**: Verify file is not imported/required by other files (check import statements, package.json, Makefile, CI workflows)
4. **Categorize** as DELETE / REVIEW / KEEP with brief justification citing evidence from steps 1-3

## Classification Taxonomy

| Category | Criteria | Evidence Required |
|----------|----------|-------------------|
| **DELETE** | Zero references, no value, clearly obsolete | Grep proof: pattern + count + zero-result confirmation |
| **REVIEW** | Uncertain — may be needed, needs human judgment | Brief justification of uncertainty |
| **KEEP** | Actively referenced, part of build/runtime/CI | At least one reference cited (file:line) |

## CRITICAL: Conservative Bias
- When uncertain, classify as **REVIEW**, never DELETE
- "No imports found" without grep evidence is NOT sufficient for DELETE
- Before any DELETE: verify no dynamic loading (env-var imports, string-based loaders, plugin registries, glob-based discovery, config-driven loading)

## Binary Asset Handling
For binary files (images, fonts, videos): grep-only audit. KEEP if referenced, REVIEW if unreferenced but in expected directory, DELETE only if unexpected location AND zero references.

## Required Output Format

```markdown
# Batch {batch.id} Audit (Pass 1)

**Status**: Complete
**Files audited**: X / {batch.file_count} assigned
**Date**: YYYY-MM-DD

## Safe to Delete
- [ ] `filepath` — reason (grep: 0 references, pattern: "filename")

## Need Decision
- [ ] `filepath` — what it is, why uncertain

## Keep (verified legitimate)
- `filepath` — why needed (referenced by: file:line)

## Add to .gitignore
- `pattern` — reason

## Remaining / Not Audited
- (list any files not reached)

## Summary
- DELETE: N | REVIEW: N | KEEP: N | .gitignore: N
- Coverage: X/{batch.file_count} = Y%
```

## Machine-Readable Markers

At the END of your output, include exactly one of:
```
EXIT_RECOMMENDATION: CONTINUE
```
or (if you encounter something that should halt the entire audit):
```
EXIT_RECOMMENDATION: HALT
```

## Incremental Save Protocol
Work in mini-batches of 5-10 files. Save/update your output file after each mini-batch.
Never accumulate more than 10 unwritten results.
"""
```

#### 3.2 Pass 2 Batch Prompt

```python
def build_pass2_batch_prompt(
    batch: BatchAssignment,
    config: CleanupAuditConfig,
    pass1_summary_content: str,
) -> str:
    """Prompt for audit-analyzer (sonnet) — Pass 2 structural audit.

    Embeds: file list, pass 1 context (if small enough), batch metadata.
    Requires: 8-field mandatory profiles per file, batch-report.md format.
    """
    file_list = "\n".join(f"- `{f}`" for f in batch.file_paths)

    # Truncate pass1 context if too large
    p1_context = pass1_summary_content[:40000] if len(pass1_summary_content) > 40000 else pass1_summary_content

    return f"""You are an audit-analyzer performing Pass 2 (Structural Audit) of a repository audit.

## Your Assignment
- **Batch**: {batch.id}
- **Files to audit**: {batch.file_count} files (KEEP/REVIEW from Pass 1 only)
- **Output file**: Write your report to the designated output file

## Pass 1 Context (known DELETEs already excluded)
<pass1-summary>
{p1_context}
</pass1-summary>

## Files in This Batch
{file_list}

## MANDATORY Per-File Profile (8 Fields — ALL REQUIRED)

For EVERY file, produce this COMPLETE profile. Reports with MISSING FIELDS are FAILED.

| Field | Requirement |
|-------|-------------|
| **What it does** | 1-2 sentence plain-English explanation |
| **Nature** | script / test / doc / config / source code / data / asset / migration / one-time artifact |
| **References** | Grep results with files + line numbers. "None found" must state grep command |
| **CI/CD usage** | Called by automation? Check workflows, compose, Makefile, package.json, Dockerfile |
| **Superseded by / duplicates** | Newer/better version? Check _v2, _enhanced, _new |
| **Risk notes** | Impact if removed or moved |
| **Recommendation** | KEEP / MOVE / DELETE / FLAG — with finding type |
| **Verification notes** | Explicit list of what was checked (at least 2 checks) |

## Finding Types
- MISPLACED: Valid content in wrong location
- STALE: Outdated or no longer accurate
- STRUCTURAL ISSUE: Dead imports, unused exports, circular deps
- BROKEN REFS: References to non-existent paths
- VERIFIED OK: All checks pass

## File-Type Extra Rules
- **Tests**: Check runner discovery path, framework conventions, test targets exist
- **Scripts**: Check for canonical equivalent, verify schema references
- **Docs**: Verify 3-5 technical claims against implementation
- **Config**: Compare similar configs, verify loaded by runtime/build/CI

## Required Output Format

Use batch-report template with full 8-field profiles per file.
Include Summary section with counts: DELETE / MOVE / FLAG / KEEP / VERIFIED OK

## Machine-Readable Markers
```
EXIT_RECOMMENDATION: CONTINUE
```
or
```
EXIT_RECOMMENDATION: HALT
```

## Incremental Save Protocol
Save after every 5-10 files. Never accumulate more than 10 unwritten results.
"""
```

#### 3.3 Pass 3 Batch Prompt

```python
def build_pass3_batch_prompt(
    batch: BatchAssignment,
    config: CleanupAuditConfig,
    pass1_summary_content: str,
    pass2_summary_content: str,
    known_issues: list[str],
) -> str:
    """Prompt for audit-comparator (sonnet) — Pass 3 cross-cutting sweep.

    Embeds: grouped similar files, prior-pass context, known-issues list.
    Requires: 7-field profiles, duplication matrix, batch-report.md format.
    """
    file_list = "\n".join(f"- `{f}`" for f in batch.file_paths)
    issues = "\n".join(f"- Issue #{i+1}: {iss}" for i, iss in enumerate(known_issues))

    return f"""You are an audit-comparator performing Pass 3 (Cross-Cutting Sweep) of a repository audit.

## Your Assignment
- **Batch**: {batch.id}
- **Files to compare**: {batch.file_count} files (grouped by similarity)
- **Output file**: Write your report to the designated output file

## Known Issues from Prior Passes (DO NOT re-flag)
{issues if issues else "No known issues from prior passes."}

## Files in This Batch (grouped by type for comparison)
{file_list}

## 6 Critical Differentiators

1. **Compare, don't just catalog**: DIFF similar files, quantify overlap %
2. **Group audit**: Audit similar files together, compare within group
3. **Mandatory duplication matrix**: Required when similar files detected
4. **Already-known issues**: Note "Already tracked as issue #N", don't re-flag
5. **Auto-KEEP for previously audited**: Focus on cross-cutting relationships only
6. **Directory-level assessments**: For 50+ file dirs, sample 10-15 representative files

## Per-File Profile (7 Fields — ALL REQUIRED)

| Field | Requirement |
|-------|-------------|
| **What it does** | 1-2 sentence explanation |
| **Nature** | File type classification |
| **References** | Grep results with files + line numbers |
| **Similar files** | Overlapping files, quantify % overlap or key differences |
| **Superseded?** | Newer/better version? Evidence required |
| **Currently used?** | Referenced by app/CI/build? Cite specific references |
| **Recommendation** | DELETE / CONSOLIDATE (with what) / MOVE / FLAG / KEEP |

## MANDATORY Duplication Matrix (when similar files detected)

| File A | File B | Overlap % | Key Differences | Recommendation |
|--------|--------|-----------|-----------------|----------------|

## Required Output Format
Use batch-report template with 7-field profiles and duplication matrix.

## Machine-Readable Markers
```
EXIT_RECOMMENDATION: CONTINUE
```
or
```
EXIT_RECOMMENDATION: HALT
```
"""
```

#### 3.4 Validate Prompt

```python
def build_validate_prompt(
    pass_num: int,
    batch_report_paths: list[Path],
    sample_findings: list[dict],
) -> str:
    """Prompt for audit-validator (sonnet) — spot-check validation.

    Embeds: sampled findings with original batch context.
    Requires: 4-check validation per finding, pass/fail with discrepancy rate.
    """
    findings_text = ""
    for i, f in enumerate(sample_findings, 1):
        findings_text += f"""
### Finding {i}
- **File**: `{f['filepath']}`
- **Original classification**: {f['classification']}
- **Original evidence**: {f['evidence_summary']}
- **From batch report**: `{f['batch_report']}`
"""

    return f"""You are an audit-validator performing independent spot-check validation of Pass {pass_num} findings.

## Independence Instruction
DO NOT assume the prior agent was correct. Verify everything from scratch.

## Findings to Validate (10% sample)
{findings_text}

## Verification Methodology (4 Checks per Finding)

### Check 1: Grep Claim Verification
Re-run the grep command. Compare results with agent's claims.

### Check 2: File Content Verification
Read the file. Verify description accuracy.

### Check 3: Classification Accuracy
Based on independent verification, is the classification correct?

### Check 4: Evidence Completeness
Are all mandatory fields present and substantive?

## Required Output Format

```markdown
# Validation Report — Pass {pass_num}

**Findings validated**: N
**Sample rate**: 10%

## Validation Results

### Finding 1: `filepath`
- **Original classification**: ...
- **Check 1 (Grep)**: PASS/FAIL — details
- **Check 2 (Content)**: PASS/FAIL — details
- **Check 3 (Classification)**: PASS/FAIL — details
- **Check 4 (Evidence)**: PASS/FAIL — details
- **Overall**: CONFIRMED / DISCREPANCY

## Summary
- Confirmed accurate: N (%)
- Discrepancies: N (%)

## Validation Status: PASS / FAIL
```

## Machine-Readable Markers
```
VALIDATION_STATUS: PASS
DISCREPANCY_RATE: 0.XX
```
or
```
VALIDATION_STATUS: FAIL
DISCREPANCY_RATE: 0.XX
```
or (for false-negative DELETE — actively referenced file recommended for deletion):
```
VALIDATION_STATUS: CRITICAL_FAIL
DISCREPANCY_RATE: 0.XX
```
"""
```

#### 3.5 Consolidate Prompt

```python
def build_consolidate_prompt(
    pass_num: int,
    batch_report_contents: dict[str, str],
    validation_report_content: str,
    template: str,
) -> str:
    """Prompt for audit-consolidator (sonnet) — merge batch reports.

    Embeds: all batch reports (or file references for large sets), validation report.
    Requires: pass-summary template adherence, deduplication, aggregate metrics.
    """
    batch_section = ""
    file_args = []
    for path, content in batch_report_contents.items():
        if len(content) < 30000:
            batch_section += f"\n---\n## Batch Report: {path}\n\n{content}\n"
        else:
            file_args.append(path)
            batch_section += f"\n- [Large batch report — provided as file: {path}]\n"

    return f"""You are an audit-consolidator merging batch reports for Pass {pass_num}.

## Batch Reports
{batch_section}

## Validation Report
{validation_report_content}

## Template to Follow
{template}

## Your Tasks

1. **Merge** findings into unified lists (DELETE, CONSOLIDATE, MOVE, FLAG, KEEP, BROKEN REF)
2. **Deduplicate** findings from multiple batches — assign single finding number
3. **Extract** cross-agent patterns (systemic findings across batches)
4. **Compute** aggregate metrics (counts per category, coverage %)
5. **Record** validation results and quality gate status
6. **Write** consolidated pass summary following the template

## Required Frontmatter

```yaml
---
pass_number: {pass_num}
total_batches: N
total_files_audited: N
coverage_percentage: N.N
---
```

## Machine-Readable Markers
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```

#### 3.6 Final Report Prompt

```python
def build_final_report_prompt(
    config: CleanupAuditConfig,
    pass_summary_contents: dict[int, str],
    template: str,
) -> str:
    """Prompt for audit-consolidator (sonnet) — final cross-pass report.

    Embeds: all pass summaries.
    Requires: final-report template adherence, prioritized actions, issues registry.
    """
    pass_sections = ""
    for pnum, content in pass_summary_contents.items():
        pass_sections += f"\n---\n## Pass {pnum} Summary\n\n{content}\n"

    return f"""You are an audit-consolidator producing the final report for a complete 3-pass repository audit.

## Pass Summaries
{pass_sections}

## Repository Context
- **Repository**: {config.inventory.repo_name if config.inventory else 'unknown'}
- **Total files**: {config.inventory.total_files if config.inventory else 'unknown'}
- **Target**: {config.target_path}
- **Passes completed**: {', '.join(str(p) for p in config.passes_to_run)}

## Template to Follow
{template}

## Your Tasks

1. **Merge** across all passes with cross-pass deduplication
2. **Prioritize** action items: Immediate (safe DELETEs/MOVEs) → Requires Decision → Requires Code Changes
3. **Extract** cross-cutting findings and discovered issues
4. **Compute** overall metrics (total coverage, total actions, estimated effort)
5. **Include** duplication matrix from Pass 3 (if available)
6. **Write** final report following the template

## Required Frontmatter

```yaml
---
repository: {config.inventory.repo_name if config.inventory else 'unknown'}
date: YYYY-MM-DD
passes_completed: {len(config.passes_to_run)}
total_files: N
total_audited: N
coverage: N.N
---
```

## Machine-Readable Markers
```
EXIT_RECOMMENDATION: CONTINUE
TOTAL_ACTIONS: N
ESTIMATED_EFFORT_HOURS: N
```
"""
```

## 4. Gate Designs

### gates.py

```python
"""Gate criteria and semantic check functions for cleanup-audit pipeline.

Each gate defines: enforcement tier, required frontmatter, min lines,
and semantic checks (pure functions on file content).
"""

import json
import re
from pathlib import Path

from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck


# --- Semantic Check Functions ---
# Each returns (passed: bool, reason: str)

def _valid_json(content: str) -> bool:
    """Content is valid JSON with expected keys."""
    try:
        data = json.loads(content)
        return isinstance(data, dict)
    except (json.JSONDecodeError, TypeError):
        return False

def _inventory_has_required_keys(content: str) -> bool:
    """Inventory JSON has files, domains, total_files keys."""
    try:
        data = json.loads(content)
        return all(k in data for k in ("files", "domains", "total_files"))
    except (json.JSONDecodeError, TypeError):
        return False

def _config_has_required_keys(content: str) -> bool:
    """Pass config JSON has passes and batches_per_pass keys."""
    try:
        data = json.loads(content)
        return "passes" in data and "batches_per_pass" in data
    except (json.JSONDecodeError, TypeError):
        return False

def _has_summary_section(content: str) -> bool:
    """Batch report has a Summary section with counts."""
    return bool(re.search(r"^## Summary", content, re.MULTILINE))

def _has_required_batch_sections(content: str) -> bool:
    """Pass 1 batch report has DELETE/REVIEW/KEEP sections."""
    required = {"Safe to Delete", "Need Decision", "Keep"}
    headings = set(re.findall(r"^## (.+)$", content, re.MULTILINE))
    return required.issubset(headings)

def _summary_counts_present(content: str) -> bool:
    """Summary section contains classification counts."""
    summary_match = re.search(r"## Summary\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not summary_match:
        return False
    summary = summary_match.group(1)
    return bool(re.search(r"DELETE.*\d|REVIEW.*\d|KEEP.*\d", summary, re.IGNORECASE))

def _has_validation_status(content: str) -> bool:
    """Validation report contains VALIDATION_STATUS marker."""
    return bool(re.search(r"VALIDATION_STATUS:\s*(PASS|FAIL|CRITICAL_FAIL)", content))

def _has_discrepancy_rate(content: str) -> bool:
    """Validation report contains DISCREPANCY_RATE marker."""
    return bool(re.search(r"DISCREPANCY_RATE:\s*\d", content))

def _has_frontmatter(content: str) -> bool:
    """Content has YAML frontmatter block."""
    return content.strip().startswith("---")

def _frontmatter_has_fields(content: str, fields: list[str]) -> bool:
    """Frontmatter contains all required fields."""
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return False
    fm = fm_match.group(1)
    return all(f"{f}:" in fm for f in fields)

def _has_required_consolidation_sections(content: str) -> bool:
    """Pass summary has required sections."""
    required = {"Aggregate Summary", "Coverage Metrics", "Quality Gate Status"}
    headings = set(re.findall(r"^## (.+)$", content, re.MULTILINE))
    return required.issubset(headings)

def _coverage_is_numeric(content: str) -> bool:
    """Coverage percentage in frontmatter is numeric 0-100."""
    match = re.search(r"coverage_percentage:\s*(\d+\.?\d*)", content)
    if not match:
        return False
    val = float(match.group(1))
    return 0 <= val <= 100

def _pass2_profiles_complete(content: str) -> bool:
    """Every file profile in Pass 2 batch has all 8 mandatory fields."""
    required_fields = [
        "What it does", "Nature", "References", "CI/CD usage",
        "Superseded by", "Risk notes", "Recommendation", "Verification notes"
    ]
    # Find all profile blocks (### `filepath` sections)
    profiles = re.split(r"^### `", content, flags=re.MULTILINE)[1:]
    if not profiles:
        return True  # No profiles to check (might be empty batch section)
    for profile in profiles:
        for field_name in required_fields:
            if f"**{field_name}**" not in profile:
                return False
    return True

def _pass3_has_duplication_matrix(content: str) -> bool:
    """Pass 3 batch report has duplication matrix when similar files detected."""
    has_similar = "Similar files" in content and ("%" in content or "overlap" in content.lower())
    has_matrix = "Duplication Matrix" in content or "| File A |" in content
    # If no similar files detected, matrix not required
    if not has_similar:
        return True
    return has_matrix

def _final_report_has_required_sections(content: str) -> bool:
    """Final report has all required sections."""
    required = {
        "Executive Summary",
        "Action Items by Priority",
        "Cross-Cutting Findings",
        "Discovered Issues Registry",
        "Audit Methodology",
    }
    headings = set(re.findall(r"^## (.+)$", content, re.MULTILINE))
    return required.issubset(headings)

def _final_report_actions_categorized(content: str) -> bool:
    """Final report action items are categorized into 3 tiers."""
    required = {"Immediate", "Requires Decision", "Requires Code Changes"}
    headings = set(re.findall(r"^### (.+)$", content, re.MULTILINE))
    return required.issubset(headings)


# --- Gate Definitions ---

INVENTORY_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=1,
    enforcement_tier="LIGHT",
    semantic_checks=[
        SemanticCheck(
            name="valid_json",
            check_fn=_valid_json,
            failure_message="Inventory output is not valid JSON",
        ),
        SemanticCheck(
            name="required_keys",
            check_fn=_inventory_has_required_keys,
            failure_message="Inventory JSON missing required keys: files, domains, total_files",
        ),
    ],
)

CONFIGURE_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=1,
    enforcement_tier="LIGHT",
    semantic_checks=[
        SemanticCheck(
            name="valid_json",
            check_fn=_valid_json,
            failure_message="Pass config is not valid JSON",
        ),
        SemanticCheck(
            name="required_keys",
            check_fn=_config_has_required_keys,
            failure_message="Pass config missing required keys: passes, batches_per_pass",
        ),
    ],
)

PASS1_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=20,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="has_required_sections",
            check_fn=_has_required_batch_sections,
            failure_message="Batch report missing required sections: Safe to Delete, Need Decision, Keep",
        ),
        SemanticCheck(
            name="has_summary",
            check_fn=_has_summary_section,
            failure_message="Batch report missing Summary section",
        ),
        SemanticCheck(
            name="summary_counts",
            check_fn=_summary_counts_present,
            failure_message="Summary section missing classification counts",
        ),
    ],
)

PASS2_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=40,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="profiles_complete",
            check_fn=_pass2_profiles_complete,
            failure_message="One or more file profiles missing mandatory 8-field entries",
        ),
        SemanticCheck(
            name="has_summary",
            check_fn=_has_summary_section,
            failure_message="Batch report missing Summary section",
        ),
    ],
)

PASS3_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=40,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="has_duplication_matrix",
            check_fn=_pass3_has_duplication_matrix,
            failure_message="Pass 3 batch report missing duplication matrix (required when similar files detected)",
        ),
        SemanticCheck(
            name="has_summary",
            check_fn=_has_summary_section,
            failure_message="Batch report missing Summary section",
        ),
    ],
)

VALIDATE_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=30,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="has_validation_status",
            check_fn=_has_validation_status,
            failure_message="Validation report missing VALIDATION_STATUS marker",
        ),
        SemanticCheck(
            name="has_discrepancy_rate",
            check_fn=_has_discrepancy_rate,
            failure_message="Validation report missing DISCREPANCY_RATE marker",
        ),
    ],
)

PASS_CONSOLIDATE_GATE = GateCriteria(
    required_frontmatter_fields=["pass_number", "total_batches", "total_files_audited", "coverage_percentage"],
    min_lines=60,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="has_required_sections",
            check_fn=_has_required_consolidation_sections,
            failure_message="Pass summary missing required sections: Aggregate Summary, Coverage Metrics, Quality Gate Status",
        ),
        SemanticCheck(
            name="coverage_numeric",
            check_fn=_coverage_is_numeric,
            failure_message="Coverage percentage must be numeric 0-100",
        ),
    ],
)

FINAL_REPORT_GATE = GateCriteria(
    required_frontmatter_fields=["repository", "date", "passes_completed", "total_files", "total_audited", "coverage"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="has_required_sections",
            check_fn=_final_report_has_required_sections,
            failure_message="Final report missing required sections",
        ),
        SemanticCheck(
            name="actions_categorized",
            check_fn=_final_report_actions_categorized,
            failure_message="Action items must be categorized: Immediate, Requires Decision, Requires Code Changes",
        ),
    ],
)

# Lookup tables for dynamic step generation
BATCH_GATES = {
    1: PASS1_BATCH_GATE,
    2: PASS2_BATCH_GATE,
    3: PASS3_BATCH_GATE,
}

CONSOLIDATE_GATES = {
    1: PASS_CONSOLIDATE_GATE,
    2: PASS_CONSOLIDATE_GATE,
    3: PASS_CONSOLIDATE_GATE,
}

BATCH_TIMEOUTS = {
    1: 300,     # Pass 1: Haiku, lighter analysis
    2: 600,     # Pass 2: Sonnet, deep per-file profiles
    3: 600,     # Pass 3: Sonnet, cross-cutting comparison
}

PASS_MODELS = {
    1: "haiku",
    2: "sonnet",
    3: "sonnet",
}
```

## 5. Executor Design

### Supervision Strategy: Sprint-Style Custom Loop

The cleanup-audit pipeline requires a custom executor (not generic `execute_pipeline()`) because:
1. **Dynamic batch generation**: Step count is determined at runtime
2. **Parallel batch dispatch**: Must launch 7-8 concurrent Claude subprocesses
3. **Inter-pass data flow**: Must parse Pass N results to generate Pass N+1 inputs
4. **Validation-triggered retry**: Failed validation can trigger batch regeneration
5. **Conditional pass execution**: `--pass` flag controls which passes run

### executor.py — Function Signatures

```python
"""Cleanup-audit executor — supervised pipeline execution.

Sprint-style custom execution loop managing parallel batch dispatch,
inter-pass data flow, validation-triggered retries, and conditional passes.
"""

import asyncio
import json
import signal
import time
from pathlib import Path
from typing import Optional

from superclaude.cli.cleanup_audit.config import load_config
from superclaude.cli.cleanup_audit.gates import (
    BATCH_GATES, CONSOLIDATE_GATES, VALIDATE_GATE, FINAL_REPORT_GATE,
)
from superclaude.cli.cleanup_audit.models import (
    AuditResult, AuditStepStatus, BatchResult, CleanupAuditConfig,
    PassMonitorState, PassResult,
)
from superclaude.cli.cleanup_audit.monitor import BatchOutputMonitor
from superclaude.cli.cleanup_audit.process import ClaudeProcess
from superclaude.cli.cleanup_audit.prompts import (
    build_pass1_batch_prompt, build_pass2_batch_prompt,
    build_pass3_batch_prompt, build_validate_prompt,
    build_consolidate_prompt, build_final_report_prompt,
)
from superclaude.cli.cleanup_audit.tui import AuditTUI


class SignalHandler:
    """Graceful shutdown on SIGINT/SIGTERM."""

    def __init__(self):
        self.shutdown_requested = False
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handle)
        signal.signal(signal.SIGTERM, self._handle)

    def _handle(self, signum, frame):
        self.shutdown_requested = True

    def restore(self):
        signal.signal(signal.SIGINT, self._original_sigint)
        signal.signal(signal.SIGTERM, self._original_sigterm)


async def execute_audit(config: CleanupAuditConfig) -> AuditResult:
    """Main entry point: execute the cleanup-audit pipeline.

    Flow:
      1. Pre-flight (verify claude binary, create output dirs)
      2. Run repo-inventory (programmatic)
      3. Configure passes (programmatic)
      4. For each pass in config.passes_to_run:
         a. Generate batch steps
         b. Launch parallel batch subprocesses
         c. Monitor and collect results
         d. Run validation (spot-check)
         e. Handle validation failures (retry failed batches)
         f. Run consolidation
      5. If --pass all: run final report
      6. Write progress.json and return result
    """
    ...


async def run_pass(
    config: CleanupAuditConfig,
    pass_num: int,
    signal_handler: SignalHandler,
    tui: AuditTUI,
    result: AuditResult,
    prior_pass_results: dict[int, PassResult],
) -> PassResult:
    """Execute a single audit pass (batched parallel + validate + consolidate).

    1. Build batch prompts using prior-pass context
    2. Launch parallel batch subprocesses (capped at max_concurrency)
    3. Monitor all batches via pass-level TUI
    4. Collect batch results and evaluate gates
    5. Run validation subprocess
    6. If validation FAIL: retry failed batches (once)
    7. If validation CRITICAL_FAIL: halt entire pipeline
    8. Run consolidation subprocess
    9. Return PassResult
    """
    ...


async def dispatch_batches(
    config: CleanupAuditConfig,
    pass_num: int,
    batch_prompts: list[str],
    signal_handler: SignalHandler,
    tui: AuditTUI,
) -> list[BatchResult]:
    """Launch parallel Claude subprocesses for all batches in a pass.

    Uses asyncio.Semaphore(config.max_concurrency) to cap concurrent processes.
    Each batch gets its own ClaudeProcess and BatchOutputMonitor.
    Returns results for all batches (success and failure).
    """
    ...


async def run_single_batch(
    config: CleanupAuditConfig,
    pass_num: int,
    batch_id: int,
    prompt: str,
    semaphore: asyncio.Semaphore,
    tui: AuditTUI,
) -> BatchResult:
    """Execute one batch subprocess with monitoring and gate evaluation.

    1. Acquire semaphore slot
    2. Launch ClaudeProcess with batch prompt
    3. Monitor output (stall detection, progress signals)
    4. Wait for completion or timeout
    5. Evaluate batch gate on output file
    6. Return BatchResult
    """
    ...


def run_repo_inventory(config: CleanupAuditConfig) -> None:
    """Step 1: Pure programmatic file inventory.

    Runs git ls-files (or find fallback), classifies files by domain,
    creates batch assignments. Writes inventory.json.
    """
    ...


def configure_passes(config: CleanupAuditConfig) -> None:
    """Step 2: Pure programmatic pass configuration.

    Reads inventory.json, applies --pass and --focus filters,
    creates PassConfig for each pass, assigns batches.
    Writes pass-config.json.
    """
    ...


def filter_files_for_pass2(config: CleanupAuditConfig) -> list:
    """Parse Pass 1 batch reports to extract DELETE classifications.

    Returns file list excluding DELETEs for Pass 2 batching.
    Pure programmatic: regex parsing of markdown reports.
    """
    ...


def sample_findings_for_validation(
    batch_reports: list[Path],
    sample_rate: float = 0.10,
) -> list[dict]:
    """Select stratified random sample of findings for spot-check.

    Ensures at least 1 DELETE, 1 KEEP, 1 FLAG in sample.
    Pure programmatic: parse markdown, random selection.
    """
    ...


def extract_known_issues(pass_summaries: dict[int, Path]) -> list[str]:
    """Parse prior pass summaries to extract known issues list.

    Prevents re-flagging in subsequent passes.
    Pure programmatic: regex extraction from markdown.
    """
    ...


def determine_batch_status(
    exit_code: int,
    output_path: Path,
    gate: object,
) -> AuditStepStatus:
    """Classify batch subprocess outcome.

    Maps exit conditions to AuditStepStatus deterministically:
    - exit_code 124 → TIMEOUT
    - exit_code != 0 → ERROR
    - output exists + CRITICAL_FAIL marker → CRITICAL_FAIL
    - output exists + HALT marker → HALT
    - output exists + gate passes → PASS
    - output exists + gate fails → VALIDATION_FAIL
    - output exists but incomplete → INCOMPLETE
    - no output → ERROR
    """
    ...


def determine_validation_status(validation_report: Path) -> AuditStepStatus:
    """Parse validation report to determine pass-level validation status.

    - VALIDATION_STATUS: PASS → AuditStepStatus.PASS
    - VALIDATION_STATUS: FAIL → AuditStepStatus.VALIDATION_FAIL
    - VALIDATION_STATUS: CRITICAL_FAIL → AuditStepStatus.CRITICAL_FAIL
    """
    ...


def save_progress(config: CleanupAuditConfig, result: AuditResult) -> None:
    """Write progress.json for resume capability.

    Records: completed passes, completed batches per pass, last checkpoint time.
    """
    ...


def load_progress(config: CleanupAuditConfig) -> Optional[AuditResult]:
    """Load progress.json and determine which steps to skip on resume."""
    ...
```

## 6. Integration Plan

### commands.py — Click CLI Surface

```python
"""Click command group for cleanup-audit pipeline."""

import sys

import click


@click.group("cleanup-audit")
def cleanup_audit_group():
    """Multi-pass repository audit with evidence-backed recommendations."""
    pass


@cleanup_audit_group.command("run")
@click.argument("target", default=".")
@click.option("--pass", "pass_selection", default="all",
              type=click.Choice(["surface", "structural", "cross-cutting", "all"]),
              help="Which audit pass to run")
@click.option("--batch-size", default=None, type=int,
              help="Override default files-per-batch (default: 50/25/30 by pass)")
@click.option("--focus", default="all",
              type=click.Choice(["infrastructure", "frontend", "backend", "all"]),
              help="Domain filter for targeted auditing")
@click.option("--max-concurrency", default=8, type=int,
              help="Maximum concurrent Claude subprocesses per pass")
@click.option("--max-turns", default=25, type=int,
              help="Maximum turns per Claude subprocess")
@click.option("--model", default=None,
              help="Override default model selection")
@click.option("--resume/--no-resume", default=False,
              help="Resume from last checkpoint")
@click.option("--dry-run", is_flag=True,
              help="Show step graph and batch assignments without executing")
@click.option("--debug", is_flag=True,
              help="Enable debug logging")
def run(target, pass_selection, batch_size, focus, max_concurrency,
        max_turns, model, resume, dry_run, debug):
    """Execute the cleanup-audit pipeline."""
    import asyncio
    from superclaude.cli.cleanup_audit.config import load_config
    from superclaude.cli.cleanup_audit.executor import execute_audit

    config = load_config(
        target_path=target,
        pass_selection=pass_selection,
        batch_size_override=batch_size,
        focus=focus,
        max_concurrency=max_concurrency,
        max_turns=max_turns,
        model=model,
        resume=resume,
        dry_run=dry_run,
        debug=debug,
    )

    if dry_run:
        _print_dry_run(config)
        sys.exit(0)

    result = asyncio.run(execute_audit(config))
    sys.exit(0 if result.success else 1)


@cleanup_audit_group.command("status")
@click.argument("work-dir", default=".claude-audit")
def status(work_dir):
    """Show progress of an in-progress or completed audit."""
    from superclaude.cli.cleanup_audit.executor import load_progress
    from superclaude.cli.cleanup_audit.models import CleanupAuditConfig
    from pathlib import Path

    config = CleanupAuditConfig(work_dir=Path(work_dir))
    progress = load_progress(config)
    if progress:
        _print_status(progress)
    else:
        click.echo("No audit progress found.")


def _print_dry_run(config):
    """Print step graph and batch assignments without executing."""
    click.echo(f"Cleanup Audit — Dry Run")
    click.echo(f"  Target: {config.target_path}")
    click.echo(f"  Passes: {config.passes_to_run}")
    click.echo(f"  Focus: {config.focus}")
    click.echo(f"  Max concurrency: {config.max_concurrency}")
    # ... print batch assignments per pass


def _print_status(result):
    """Print current audit progress."""
    # ... rich table of pass/batch completion status
    pass
```

### main.py Registration

```python
# In src/superclaude/cli/main.py — add to existing imports and registration
from superclaude.cli.cleanup_audit import cleanup_audit_group
app.add_command(cleanup_audit_group)
```

### __init__.py

```python
"""Cleanup-audit CLI pipeline — multi-pass repository audit."""

from superclaude.cli.cleanup_audit.commands import cleanup_audit_group

__all__ = ["cleanup_audit_group"]
```

## 7. File Generation Order

| # | File | Dependencies | Purpose |
|---|------|-------------|---------|
| 1 | `models.py` | pipeline.models | All enums, dataclasses (no internal deps) |
| 2 | `gates.py` | pipeline.models, models | Gate criteria and semantic check functions |
| 3 | `prompts.py` | models | Prompt builder functions for each step type |
| 4 | `config.py` | models | Config loading, validation, batch generation |
| 5 | `monitor.py` | models | NDJSON output monitor with audit-specific signals |
| 6 | `process.py` | models, config | Claude subprocess wrapper with batch support |
| 7 | `executor.py` | all above | Sprint-style execution loop with parallel dispatch |
| 8 | `tui.py` | models | Rich TUI showing per-batch and per-pass progress |
| 9 | `logging_.py` | models | Dual-format (NDJSON + human-readable) logging |
| 10 | `diagnostics.py` | models | Failure classification and diagnostic report generation |
| 11 | `commands.py` | config, executor | Click CLI surface |
| 12 | `__init__.py` | commands | Package exports |

## 8. Key Design Decisions

### 8.1 Parallel Batch Dispatch via asyncio

Unlike sprint (which runs one subprocess at a time), cleanup-audit must run 7-8 concurrent Claude subprocesses. Use `asyncio.create_subprocess_exec` with a `Semaphore(max_concurrency)` to cap parallelism. Each batch gets its own `ClaudeProcess` and `BatchOutputMonitor` instance.

### 8.2 Inter-Pass Data Flow is Programmatic

The current inference workflow relies on Claude to read Pass 1 results and decide which files go to Pass 2. In the pipeline, this is pure Python:
- `filter_files_for_pass2()` parses Pass 1 batch reports with regex
- `extract_known_issues()` parses prior summaries for dedup context
- `sample_findings_for_validation()` uses stratified random sampling

### 8.3 Validation-Triggered Retry

If `determine_validation_status()` returns `VALIDATION_FAIL`, the executor:
1. Identifies which batch reports have discrepancies
2. Regenerates only those batches (up to 1 retry per batch)
3. Re-runs validation on the regenerated batches
4. If still failing, records partial results and continues

If `CRITICAL_FAIL`, the executor halts the entire pipeline immediately.

### 8.4 Dynamic Step Graph

The step graph is not fixed at compile time. Steps 3, 6, and 9 each expand into N batch steps based on inventory size and batch-size configuration. The executor builds the graph dynamically after step 2 (configure-passes).

### 8.5 Resume Capability

`progress.json` tracks:
- Which passes are complete
- Which batches within each pass are complete (with their result files)
- Timestamp of last checkpoint

On `--resume`, the executor loads progress, skips completed batches (if their output files still pass their gates), and continues from the last incomplete batch.

### 8.6 TUI Design

The TUI must show:
- Current pass (1/2/3)
- Batch progress: `[====----] 5/8 batches complete` with per-batch status indicators
- Active batch details: current file being processed (if detectable from output)
- Elapsed time and estimated remaining
- Classification counts running total
- Any errors or warnings

This differs from sprint TUI (single step progress) in that it must track N concurrent processes and show aggregate progress.

## 9. Templates and Rules Embedding

The templates from `templates/` and rules from `rules/` are embedded into prompts:
- `batch-report.md` template format is specified inline in each batch prompt
- `pass-summary.md` template is passed to the consolidate prompt
- `final-report.md` template is passed to the final report prompt
- `pass1-surface-scan.md` rules are encoded as methodology instructions in the pass 1 prompt
- `pass2-structural-audit.md` rules are encoded as profile requirements in the pass 2 prompt
- `pass3-cross-cutting.md` rules are encoded as differentiators in the pass 3 prompt
- `dynamic-use-checklist.md` is summarized as the conservative bias section in all batch prompts
- `verification-protocol.md` evidence standards are encoded in all batch prompts

The templates and rules directories themselves are NOT read at runtime by the pipeline code. All relevant content is baked into `prompts.py`.

## 10. Differences from Sprint Pattern

| Aspect | Sprint | Cleanup-Audit |
|--------|--------|---------------|
| Parallelism | One subprocess at a time | 7-8 concurrent per pass |
| Step count | Fixed at config time | Dynamic (depends on file count) |
| Step types | All Claude-assisted | Mix of programmatic + Claude |
| Inter-step data | Linear chain | Conditional passes, filtered file lists |
| Retry trigger | Gate failure | Validation spot-check failure |
| TUI | Single-step progress | Multi-batch aggregate progress |
| Resume | Per-step | Per-batch within per-pass |
| Models | Single model | Mixed (haiku for Pass 1, sonnet for 2-3) |
| Output | Single artifact per step | Multiple batch reports per pass + summaries |
