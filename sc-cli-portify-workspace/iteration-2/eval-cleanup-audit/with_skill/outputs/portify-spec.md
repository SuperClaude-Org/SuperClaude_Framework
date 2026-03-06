# Pipeline Specification: cleanup-audit

Complete code specification for the `superclaude cleanup-audit` CLI pipeline, portified from `sc-cleanup-audit-protocol`.

Prompt text has been extracted to `portify-prompts.md` to keep this spec focused on code architecture.

---

## 1. Module Layout

```
src/superclaude/cli/cleanup_audit/
├── __init__.py        # Package exports
├── commands.py        # Click CLI surface
├── config.py          # Config loading and validation
├── models.py          # Domain types (enums, dataclasses)
├── prompts.py         # Prompt builders (imports from portify-prompts.md)
├── gates.py           # Gate criteria and semantic checks
├── executor.py        # Sprint-style supervised execution loop
├── inventory.py       # Pure-programmatic: repo inventory (replaces repo-inventory.sh)
├── filtering.py       # Pure-programmatic: file filtering between passes
├── monitor.py         # NDJSON output monitor
├── process.py         # Claude subprocess wrapper
├── tui.py             # Rich live TUI dashboard
├── logging_.py        # Dual JSONL + Markdown logging
└── diagnostics.py     # Failure classification and reporting
```

---

## 2. Models (`models.py`)

### Enums

```python
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.sprint.models import TurnLedger


class AuditPass(Enum):
    """Which audit pass to run."""
    SURFACE = "surface"
    STRUCTURAL = "structural"
    CROSS_CUTTING = "cross-cutting"
    ALL = "all"

    @property
    def pass_number(self) -> int:
        return {
            "surface": 1,
            "structural": 2,
            "cross-cutting": 3,
            "all": 0,
        }[self.value]


class AuditFocus(Enum):
    """Domain filter for targeted auditing."""
    INFRASTRUCTURE = "infrastructure"
    FRONTEND = "frontend"
    BACKEND = "backend"
    ALL = "all"


class FileDomain(Enum):
    """Domain classification for file inventory."""
    INFRASTRUCTURE = "infrastructure"
    FRONTEND = "frontend"
    BACKEND = "backend"
    TESTS = "tests"
    DOCUMENTATION = "documentation"
    CONFIG = "config"
    ASSETS = "assets"
    OTHER = "other"


class FileClassification(Enum):
    """Audit classification for a single file."""
    DELETE = "DELETE"
    REVIEW = "REVIEW"
    KEEP = "KEEP"
    CONSOLIDATE = "CONSOLIDATE"
    MOVE = "MOVE"
    FLAG = "FLAG"
    BROKEN_REF = "BROKEN_REF"
    UNAUDITED = "UNAUDITED"


class AuditStepStatus(Enum):
    """Step-level status for cleanup-audit pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    INCOMPLETE = "incomplete"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


class AuditOutcome(Enum):
    """Aggregate pipeline outcome."""
    SUCCESS = "success"
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"


class AgentType(Enum):
    """Agent types used in the audit pipeline."""
    SCANNER = "audit-scanner"       # Haiku, Pass 1
    ANALYZER = "audit-analyzer"     # Sonnet, Pass 2
    COMPARATOR = "audit-comparator" # Sonnet, Pass 3
    CONSOLIDATOR = "audit-consolidator"  # Sonnet, reporting
    VALIDATOR = "audit-validator"   # Sonnet, spot-check

    @property
    def model(self) -> str:
        if self == AgentType.SCANNER:
            return "haiku"
        return "sonnet"

    @property
    def max_turns(self) -> int:
        return {
            "audit-scanner": 20,
            "audit-analyzer": 35,
            "audit-comparator": 35,
            "audit-consolidator": 40,
            "audit-validator": 25,
        }[self.value]
```

### Configuration

```python
@dataclass
class AuditConfig(PipelineConfig):
    """Cleanup-audit pipeline configuration."""

    # Required inputs
    target_path: Path = field(default_factory=lambda: Path("."))

    # Audit parameters
    audit_pass: AuditPass = AuditPass.ALL
    focus: AuditFocus = AuditFocus.ALL
    batch_size_pass1: int = 50
    batch_size_pass2: int = 25
    batch_size_pass3: int = 30
    max_concurrency: int = 7

    # Budget
    max_turns: int = 200
    min_launch_allocation: int = 10
    min_remediation_budget: int = 5

    # Timeouts
    batch_timeout: int = 600
    consolidation_timeout: int = 900
    stall_timeout: int = 120
    stall_action: str = "kill"

    # Resume
    resume_from_pass: int | None = None
    resume_from_batch: int | None = None

    def __post_init__(self):
        if not self.work_dir or self.work_dir == Path("."):
            self.work_dir = self.target_path / ".claude-audit"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    @property
    def pass_dir(self) -> dict[int, Path]:
        return {
            1: self.work_dir / "pass1",
            2: self.work_dir / "pass2",
            3: self.work_dir / "pass3",
        }

    @property
    def inventory_path(self) -> Path:
        return self.work_dir / "inventory.json"

    @property
    def pass_config_path(self) -> Path:
        return self.work_dir / "pass-config.json"

    def batch_report_path(self, pass_num: int, batch_num: int) -> Path:
        return self.pass_dir[pass_num] / f"batch-{batch_num:02d}.md"

    def pass_summary_path(self, pass_num: int) -> Path:
        return self.work_dir / f"pass{pass_num}-summary.md"

    @property
    def final_report_path(self) -> Path:
        return self.work_dir / "final-report.md"

    @property
    def progress_path(self) -> Path:
        return self.work_dir / "progress.json"

    def batch_size_for_pass(self, pass_num: int) -> int:
        return {1: self.batch_size_pass1, 2: self.batch_size_pass2, 3: self.batch_size_pass3}[pass_num]

    def passes_to_run(self) -> list[int]:
        if self.audit_pass == AuditPass.ALL:
            return [1, 2, 3]
        return [self.audit_pass.pass_number]
```

### Inventory Types

```python
@dataclass
class FileEntry:
    """A single file in the inventory."""
    path: str
    domain: FileDomain
    extension: str
    size_bytes: int = 0
    classification: FileClassification = FileClassification.UNAUDITED

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "domain": self.domain.value,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "classification": self.classification.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FileEntry:
        return cls(
            path=data["path"],
            domain=FileDomain(data["domain"]),
            extension=data["extension"],
            size_bytes=data.get("size_bytes", 0),
            classification=FileClassification(data.get("classification", "UNAUDITED")),
        )


@dataclass
class BatchAssignment:
    """A batch of files assigned to an agent."""
    batch_number: int
    pass_number: int
    files: list[str]
    agent_type: AgentType
    domain: str
    output_path: str

    def to_dict(self) -> dict:
        return {
            "batch_number": self.batch_number,
            "pass_number": self.pass_number,
            "files": self.files,
            "agent_type": self.agent_type.value,
            "domain": self.domain,
            "output_path": self.output_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> BatchAssignment:
        return cls(
            batch_number=data["batch_number"],
            pass_number=data["pass_number"],
            files=data["files"],
            agent_type=AgentType(data["agent_type"]),
            domain=data["domain"],
            output_path=data["output_path"],
        )


@dataclass
class Inventory:
    """Complete file inventory with domain grouping."""
    files: list[FileEntry]
    total_count: int = 0
    domain_counts: dict[str, int] = field(default_factory=dict)
    extension_counts: dict[str, int] = field(default_factory=dict)
    target_path: str = "."

    def to_dict(self) -> dict:
        return {
            "files": [f.to_dict() for f in self.files],
            "total_count": self.total_count,
            "domain_counts": self.domain_counts,
            "extension_counts": self.extension_counts,
            "target_path": self.target_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Inventory:
        return cls(
            files=[FileEntry.from_dict(f) for f in data["files"]],
            total_count=data["total_count"],
            domain_counts=data["domain_counts"],
            extension_counts=data["extension_counts"],
            target_path=data.get("target_path", "."),
        )
```

### Result Types

```python
@dataclass
class BatchResult:
    """Result from a single batch subprocess."""
    batch_number: int
    pass_number: int
    status: AuditStepStatus = AuditStepStatus.PENDING
    exit_code: int | None = None
    started_at: float | None = None
    finished_at: float | None = None
    output_bytes: int = 0
    files_audited: int = 0
    gate_passed: bool = False
    gate_failure_reason: str = ""
    turns_consumed: int = 0

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return 0.0

    def to_context_summary(self, verbose: bool = False) -> str:
        lines = [f"Batch {self.batch_number} (Pass {self.pass_number}): {self.status.value}"]
        if verbose:
            lines.append(f"  Files audited: {self.files_audited}")
            lines.append(f"  Duration: {self.duration_seconds:.1f}s")
            lines.append(f"  Output: {self.output_bytes} bytes")
        return "\n".join(lines)


@dataclass
class PassResult:
    """Aggregate result for a single audit pass."""
    pass_number: int
    batch_results: list[BatchResult] = field(default_factory=list)
    consolidation_result: BatchResult | None = None
    validation_result: BatchResult | None = None
    status: AuditStepStatus = AuditStepStatus.PENDING

    @property
    def batches_passed(self) -> int:
        return sum(1 for r in self.batch_results if r.status == AuditStepStatus.PASS)

    @property
    def batches_failed(self) -> int:
        return sum(1 for r in self.batch_results
                   if r.status in (AuditStepStatus.HALT, AuditStepStatus.ERROR, AuditStepStatus.TIMEOUT))

    @property
    def total_files_audited(self) -> int:
        return sum(r.files_audited for r in self.batch_results)

    @property
    def total_turns_consumed(self) -> int:
        total = sum(r.turns_consumed for r in self.batch_results)
        if self.consolidation_result:
            total += self.consolidation_result.turns_consumed
        if self.validation_result:
            total += self.validation_result.turns_consumed
        return total


@dataclass
class AuditResult:
    """Aggregate result for the entire cleanup-audit pipeline."""
    config: AuditConfig
    pass_results: list[PassResult] = field(default_factory=list)
    outcome: AuditOutcome = AuditOutcome.SUCCESS
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    halt_step: str | None = None
    halt_reason: str = ""

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or time.time()
        return end - self.started_at

    @property
    def total_turns_consumed(self) -> int:
        return sum(pr.total_turns_consumed for pr in self.pass_results)

    @property
    def passes_completed(self) -> int:
        return sum(1 for pr in self.pass_results if pr.status == AuditStepStatus.PASS)

    def resume_command(self) -> str | None:
        """Generate CLI command to resume from the failed point."""
        if not self.halt_step:
            return None
        # Parse halt_step to determine resume pass and batch
        remaining_passes = [
            pr.pass_number for pr in self.pass_results
            if pr.status == AuditStepStatus.PENDING
        ]
        remaining_count = len(remaining_passes)
        budget_suggestion = max(remaining_count * 60, 50)

        parts = ["superclaude", "cleanup-audit", "run", str(self.config.target_path)]
        if remaining_passes:
            parts.append(f"--resume-from-pass {remaining_passes[0]}")
        parts.append(f"--max-turns {budget_suggestion}")
        return " ".join(parts)

    @property
    def suggested_resume_budget(self) -> int:
        remaining_passes = sum(
            1 for pr in self.pass_results
            if pr.status in (AuditStepStatus.PENDING, AuditStepStatus.INCOMPLETE)
        )
        return max(remaining_passes * 60, 50)


@dataclass
class AuditMonitorState:
    """Live execution state fed by the output monitor."""
    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = 0.0
    last_event_time: float = 0.0
    step_started_at: float = 0.0
    events_received: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    # Domain-specific signals
    current_pass: int = 0
    current_batch: int = 0
    files_scanned: int = 0
    current_file: str | None = None
    active_agents: int = 0

    @property
    def stall_status(self) -> str:
        if self.events_received == 0:
            elapsed = time.time() - self.step_started_at if self.step_started_at else 0
            return "waiting..." if elapsed < 30 else "STALLED"
        if self.stall_seconds > 120:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str:
        if self.output_bytes < 1024:
            return f"{self.output_bytes}B"
        if self.output_bytes < 1024 * 1024:
            return f"{self.output_bytes / 1024:.1f}KB"
        return f"{self.output_bytes / (1024 * 1024):.1f}MB"
```

---

## 3. Pure-Programmatic Step: Repo Inventory (`inventory.py`)

Full implementation replacing `scripts/repo-inventory.sh`:

```python
"""Pure-programmatic repo inventory — replaces repo-inventory.sh.

Enumerates files via git ls-files (or find fallback), classifies into
domains, and produces a structured JSON inventory with batch assignments.

No Claude subprocess needed. Runs as a direct Python function call.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .models import (
    AuditConfig,
    BatchAssignment,
    AgentType,
    FileDomain,
    FileEntry,
    Inventory,
)


# --- Domain classification rules ---

_INFRA_PATTERNS = {
    "Dockerfile", "docker-compose", ".yml", ".yaml", "Makefile",
    "Justfile", ".sh", "Jenkinsfile", ".tf", ".tfvars",
}
_INFRA_DIRS = {".github", ".gitlab-ci", ".circleci", "ci", "deploy"}

_FRONTEND_EXTS = {".jsx", ".tsx", ".vue", ".svelte", ".css", ".scss", ".less", ".html"}
_FRONTEND_DIRS = {"components", "pages", "views"}

_BACKEND_EXTS = {".py", ".go", ".rs", ".java", ".rb", ".php"}
_BACKEND_DIRS = {"api", "services", "models", "controllers"}

_TEST_MARKERS = {"test", "spec", "__tests__", "tests"}

_DOC_EXTS = {".md", ".rst", ".txt", ".adoc"}
_DOC_DIRS = {"docs", "doc"}

_CONFIG_EXTS = {".json", ".toml", ".ini", ".cfg", ".conf"}

_ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".webm", ".pdf",
}


def classify_domain(filepath: str) -> FileDomain:
    """Classify a file into a domain based on path and extension."""
    parts = Path(filepath).parts
    ext = Path(filepath).suffix.lower()
    name = Path(filepath).name

    # Infrastructure: check filename patterns and directories
    for p in _INFRA_PATTERNS:
        if p in name:
            return FileDomain.INFRASTRUCTURE
    for d in _INFRA_DIRS:
        if any(part == d or part.startswith(f".{d}") for part in parts):
            return FileDomain.INFRASTRUCTURE

    # Tests: check directory markers
    for marker in _TEST_MARKERS:
        if any(marker in part.lower() for part in parts):
            return FileDomain.TESTS

    # Frontend
    if ext in _FRONTEND_EXTS:
        return FileDomain.FRONTEND
    for d in _FRONTEND_DIRS:
        if d in parts:
            return FileDomain.FRONTEND

    # Backend
    if ext in _BACKEND_EXTS:
        return FileDomain.BACKEND
    for d in _BACKEND_DIRS:
        if d in parts:
            return FileDomain.BACKEND

    # Documentation
    if ext in _DOC_EXTS:
        return FileDomain.DOCUMENTATION
    for d in _DOC_DIRS:
        if d in parts:
            return FileDomain.DOCUMENTATION

    # Config
    if ext in _CONFIG_EXTS or ".env" in name or ".config" in name:
        return FileDomain.CONFIG

    # Assets
    if ext in _ASSET_EXTS:
        return FileDomain.ASSETS

    return FileDomain.OTHER


def enumerate_files(target_path: Path) -> list[str]:
    """Enumerate files using git ls-files or find fallback."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--", str(target_path)],
            capture_output=True, text=True, timeout=30,
            cwd=str(target_path) if target_path.is_dir() else None,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line for line in result.stdout.strip().splitlines() if line]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: use os.walk with exclusions
    exclude_dirs = {
        ".git", "node_modules", "__pycache__", ".cache", "dist",
        "build", ".next", "vendor", ".venv", "venv", ".tox",
        ".mypy_cache", ".pytest_cache", "coverage",
    }
    files = []
    for root, dirs, filenames in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in filenames:
            rel = os.path.relpath(os.path.join(root, f), target_path)
            files.append(rel)
    return files


def build_inventory(config: AuditConfig) -> Inventory:
    """Build complete file inventory from target path.

    Returns:
        Inventory with domain-classified files and aggregate counts.
    """
    raw_files = enumerate_files(config.target_path)

    entries = []
    domain_counts: dict[str, int] = {}
    extension_counts: dict[str, int] = {}

    for filepath in raw_files:
        domain = classify_domain(filepath)
        ext = Path(filepath).suffix.lower() or "(none)"

        # Apply focus filter
        if config.focus != AuditFocus.ALL:
            focus_domain = FileDomain(config.focus.value)
            if domain != focus_domain:
                continue

        entry = FileEntry(
            path=filepath,
            domain=domain,
            extension=ext,
        )
        entries.append(entry)

        domain_counts[domain.value] = domain_counts.get(domain.value, 0) + 1
        extension_counts[ext] = extension_counts.get(ext, 0) + 1

    inventory = Inventory(
        files=entries,
        total_count=len(entries),
        domain_counts=domain_counts,
        extension_counts=extension_counts,
        target_path=str(config.target_path),
    )
    return inventory


def write_inventory(inventory: Inventory, output_path: Path) -> None:
    """Serialize inventory to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(inventory.to_dict(), f, indent=2)


def run_repo_inventory(config: AuditConfig) -> None:
    """Programmatic step runner for repo-inventory.

    Called by the executor for step 1. Writes inventory.json.
    """
    inventory = build_inventory(config)
    write_inventory(inventory, config.inventory_path)
```

---

## 4. Pure-Programmatic Step: Configure Passes & File Filtering (`filtering.py`)

```python
"""Pure-programmatic pass configuration and inter-pass file filtering.

Builds batch assignments for each pass and filters file lists based
on prior pass results. No Claude subprocess needed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import (
    AgentType,
    AuditConfig,
    AuditFocus,
    BatchAssignment,
    FileClassification,
    FileDomain,
    Inventory,
)


# --- Priority ordering for domain batching ---
_DOMAIN_PRIORITY = [
    "infrastructure", "config", "tests", "backend",
    "frontend", "documentation", "assets", "other",
]


def build_pass_batches(
    files: list[str],
    pass_number: int,
    batch_size: int,
    config: AuditConfig,
    grouping: str = "domain",
) -> list[BatchAssignment]:
    """Build batch assignments for a pass.

    Args:
        files: File paths to batch.
        pass_number: Which pass (1, 2, or 3).
        batch_size: Max files per batch.
        config: Pipeline configuration.
        grouping: "domain" (pass 1-2) or "similarity" (pass 3).

    Returns:
        List of BatchAssignment objects.
    """
    agent_type = {
        1: AgentType.SCANNER,
        2: AgentType.ANALYZER,
        3: AgentType.COMPARATOR,
    }[pass_number]

    batches: list[BatchAssignment] = []
    batch_num = 1
    current_batch: list[str] = []
    current_domain = "mixed"

    if grouping == "domain":
        # Group files by domain, then batch within each domain
        domain_files: dict[str, list[str]] = {}
        for f in files:
            from .inventory import classify_domain
            d = classify_domain(f).value
            domain_files.setdefault(d, []).append(f)

        for domain in _DOMAIN_PRIORITY:
            for f in domain_files.get(domain, []):
                current_batch.append(f)
                if len(current_batch) >= batch_size:
                    batches.append(BatchAssignment(
                        batch_number=batch_num,
                        pass_number=pass_number,
                        files=current_batch.copy(),
                        agent_type=agent_type,
                        domain=domain,
                        output_path=str(config.batch_report_path(pass_number, batch_num)),
                    ))
                    batch_num += 1
                    current_batch = []
                    current_domain = domain

        # Remainder batch
        if current_batch:
            batches.append(BatchAssignment(
                batch_number=batch_num,
                pass_number=pass_number,
                files=current_batch,
                agent_type=agent_type,
                domain="mixed",
                output_path=str(config.batch_report_path(pass_number, batch_num)),
            ))
    else:
        # Similarity grouping for pass 3: group by extension + directory
        ext_groups: dict[str, list[str]] = {}
        for f in files:
            ext = Path(f).suffix.lower() or "(none)"
            ext_groups.setdefault(ext, []).append(f)

        for ext, group_files in sorted(ext_groups.items(), key=lambda x: -len(x[1])):
            for i in range(0, len(group_files), batch_size):
                chunk = group_files[i:i + batch_size]
                batches.append(BatchAssignment(
                    batch_number=batch_num,
                    pass_number=pass_number,
                    files=chunk,
                    agent_type=agent_type,
                    domain=f"ext:{ext}",
                    output_path=str(config.batch_report_path(pass_number, batch_num)),
                ))
                batch_num += 1

    return batches


def run_configure_passes(config: AuditConfig) -> None:
    """Programmatic step runner for configure-passes (step 2).

    Reads inventory.json, builds batch assignments for all requested passes,
    writes pass-config.json.
    """
    inventory = Inventory.from_dict(
        json.loads(config.inventory_path.read_text())
    )
    all_files = [f.path for f in inventory.files]

    pass_configs: dict[str, list[dict]] = {}
    for pass_num in config.passes_to_run():
        batch_size = config.batch_size_for_pass(pass_num)
        grouping = "similarity" if pass_num == 3 else "domain"
        batches = build_pass_batches(all_files, pass_num, batch_size, config, grouping)
        pass_configs[f"pass{pass_num}"] = [b.to_dict() for b in batches]

    output = {
        "passes": config.passes_to_run(),
        "focus": config.focus.value,
        "batch_configs": pass_configs,
        "total_files": inventory.total_count,
    }

    config.pass_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config.pass_config_path, "w") as f:
        json.dump(output, f, indent=2)


def extract_classifications_from_batch(batch_report_path: Path) -> dict[str, FileClassification]:
    """Parse a Pass 1 batch report to extract file classifications.

    Scans the markdown for files listed under known sections.
    Returns a mapping of filepath -> classification.
    """
    if not batch_report_path.exists():
        return {}

    content = batch_report_path.read_text()
    classifications: dict[str, FileClassification] = {}
    current_section = None

    section_map = {
        "## safe to delete": FileClassification.DELETE,
        "## files to delete": FileClassification.DELETE,
        "## need decision": FileClassification.REVIEW,
        "## files to flag": FileClassification.FLAG,
        "## keep": FileClassification.KEEP,
        "## files to keep": FileClassification.KEEP,
        "## files to move": FileClassification.MOVE,
        "## files to consolidate": FileClassification.CONSOLIDATE,
    }

    # Pattern: lines starting with "- [ ] `filepath`" or "- `filepath`" or "### `filepath`"
    file_pattern = re.compile(r'(?:- \[.\] |### |[*-] )`([^`]+)`')

    for line in content.splitlines():
        stripped = line.strip().lower()
        for prefix, cls in section_map.items():
            if stripped.startswith(prefix):
                current_section = cls
                break

        if current_section:
            match = file_pattern.search(line)
            if match:
                classifications[match.group(1)] = current_section

    return classifications


def run_filter_pass2_files(config: AuditConfig) -> None:
    """Programmatic step runner for filter-pass2-files (step 7).

    Reads Pass 1 batch reports, extracts classifications, filters to
    KEEP/REVIEW files, rebuilds batch assignments for Pass 2.
    """
    pass1_dir = config.pass_dir[1]
    all_classifications: dict[str, FileClassification] = {}

    for batch_report in sorted(pass1_dir.glob("batch-*.md")):
        batch_cls = extract_classifications_from_batch(batch_report)
        all_classifications.update(batch_cls)

    # Filter to KEEP and REVIEW only
    pass2_files = [
        fp for fp, cls in all_classifications.items()
        if cls in (FileClassification.KEEP, FileClassification.REVIEW)
    ]

    # Also include files not classified (defensive: unaudited files go to pass 2)
    inventory = Inventory.from_dict(
        json.loads(config.inventory_path.read_text())
    )
    all_inventory_files = {f.path for f in inventory.files}
    classified_files = set(all_classifications.keys())
    unclassified = all_inventory_files - classified_files
    pass2_files.extend(sorted(unclassified))

    batches = build_pass_batches(
        pass2_files, 2, config.batch_size_pass2, config, grouping="domain"
    )

    output = {
        "pass": 2,
        "total_files": len(pass2_files),
        "classified_from_pass1": len(all_classifications),
        "kept_review": len([f for f, c in all_classifications.items()
                           if c in (FileClassification.KEEP, FileClassification.REVIEW)]),
        "deleted_pass1": len([f for f, c in all_classifications.items()
                             if c == FileClassification.DELETE]),
        "batches": [b.to_dict() for b in batches],
    }

    pass2_config_path = config.work_dir / "pass2-config.json"
    with open(pass2_config_path, "w") as f:
        json.dump(output, f, indent=2)


def run_filter_pass3_files(config: AuditConfig) -> None:
    """Programmatic step runner for filter-pass3-files (step 10).

    Groups files by similarity for cross-cutting comparison.
    Reads Pass 2 batch reports for context, builds similarity groups.
    """
    inventory = Inventory.from_dict(
        json.loads(config.inventory_path.read_text())
    )
    all_files = [f.path for f in inventory.files]

    batches = build_pass_batches(
        all_files, 3, config.batch_size_pass3, config, grouping="similarity"
    )

    output = {
        "pass": 3,
        "total_files": len(all_files),
        "batches": [b.to_dict() for b in batches],
    }

    pass3_config_path = config.work_dir / "pass3-config.json"
    with open(pass3_config_path, "w") as f:
        json.dump(output, f, indent=2)
```

---

## 5. Gates (`gates.py`)

### Semantic Check Functions

All semantic checks return `tuple[bool, str]`.

```python
"""Gate criteria and semantic checks for cleanup-audit pipeline.

Each step's output must pass its gate before the pipeline continues.
Gates enforce structural and semantic quality programmatically.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import json
import re

from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck


# ────────────────────────────────────────────
# Semantic Check Functions: (str) -> tuple[bool, str]
# ────────────────────────────────────────────

def _has_required_batch_sections(content: str) -> tuple[bool, str]:
    """Verify batch report has required sections."""
    required = {"## Safe to Delete", "## Need Decision", "## Keep", "## Summary"}
    # Allow alternative headings
    alt_required = {"## Files to DELETE", "## Files to FLAG", "## Files to KEEP", "## Summary"}
    present = set()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            present.add(stripped)

    # Check primary set
    missing = required - present
    if not missing:
        return (True, "")

    # Check alternative set
    alt_missing = alt_required - present
    if not alt_missing:
        return (True, "")

    # Check union - at least Summary must be present
    if "## Summary" not in present:
        return (False, "Missing required section: ## Summary")

    # Lenient: at least 3 of the required sections
    primary_found = len(required & present)
    alt_found = len(alt_required & present)
    if max(primary_found, alt_found) >= 3:
        return (True, "")

    return (False, f"Missing required sections. Found: {present}")


def _has_required_summary_sections(content: str) -> tuple[bool, str]:
    """Verify pass summary has required sections."""
    required = {
        "## Aggregate Summary",
        "## Coverage Metrics",
        "## Quality Gate Status",
    }
    present = {line.strip() for line in content.splitlines() if line.strip().startswith("## ")}
    missing = required - present
    if missing:
        return (False, f"Missing sections: {', '.join(sorted(missing))}")
    return (True, "")


def _has_quality_gate_table(content: str) -> tuple[bool, str]:
    """Verify the report contains a quality gate status table."""
    if "## Quality Gate Status" not in content:
        return (False, "Missing '## Quality Gate Status' section")
    # Check for table markers after the section
    idx = content.index("## Quality Gate Status")
    remainder = content[idx:]
    if "|" not in remainder:
        return (False, "'## Quality Gate Status' section has no table")
    return (True, "")


def _has_mandatory_profiles(content: str) -> tuple[bool, str]:
    """Verify Pass 2 reports contain per-file profiles."""
    # Profiles are formatted as "### `filepath`" followed by a table
    profile_pattern = re.compile(r'^### `[^`]+`', re.MULTILINE)
    matches = profile_pattern.findall(content)
    if not matches:
        return (False, "No per-file profiles found (expected ### `filepath` headings)")
    return (True, "")


def _profiles_have_all_fields(content: str) -> tuple[bool, str]:
    """Verify Pass 2 profiles have all 8 mandatory fields."""
    required_fields = {
        "What it does", "Nature", "References", "CI/CD usage",
        "Superseded by", "Risk notes", "Recommendation", "Verification notes",
    }
    # Split by profile headers
    profiles = re.split(r'^### `[^`]+`', content, flags=re.MULTILINE)
    profiles = [p for p in profiles if p.strip()]  # Drop empty before first profile

    if not profiles:
        return (True, "")  # No profiles to validate (caught by _has_mandatory_profiles)

    for i, profile in enumerate(profiles):
        found_fields = set()
        for line in profile.splitlines():
            for field_name in required_fields:
                if f"**{field_name}**" in line:
                    found_fields.add(field_name)
        missing = required_fields - found_fields
        if missing:
            return (False, f"Profile {i+1} missing fields: {', '.join(sorted(missing))}")

    return (True, "")


def _has_7field_profiles(content: str) -> tuple[bool, str]:
    """Verify Pass 3 profiles have all 7 mandatory fields."""
    required_fields = {
        "What it does", "Nature", "References", "Similar files",
        "Superseded", "Currently used", "Recommendation",
    }
    profiles = re.split(r'^### `[^`]+`', content, flags=re.MULTILINE)
    profiles = [p for p in profiles if p.strip()]

    if not profiles:
        return (True, "")

    for i, profile in enumerate(profiles):
        found_fields = set()
        for line in profile.splitlines():
            for field_name in required_fields:
                if f"**{field_name}**" in line or f"**{field_name}?**" in line:
                    found_fields.add(field_name)
        missing = required_fields - found_fields
        if missing:
            return (False, f"Profile {i+1} missing fields: {', '.join(sorted(missing))}")

    return (True, "")


def _has_duplication_matrix(content: str) -> tuple[bool, str]:
    """Verify Pass 3 reports contain a duplication matrix when similar files exist."""
    # Check if similar files were detected
    has_consolidate = "CONSOLIDATE" in content.upper()
    has_similar = "similar" in content.lower() or "overlap" in content.lower()

    if has_consolidate or has_similar:
        if "## Duplication Matrix" not in content and "| File A |" not in content:
            return (False, "Similar files detected but no Duplication Matrix found")

    return (True, "")


def _has_executive_summary(content: str) -> tuple[bool, str]:
    """Verify final report has executive summary section."""
    if "## Executive Summary" not in content:
        return (False, "Missing '## Executive Summary' section")
    return (True, "")


def _has_action_items(content: str) -> tuple[bool, str]:
    """Verify final report has prioritized action items."""
    if "## Action Items" not in content:
        return (False, "Missing '## Action Items' section")
    return (True, "")


def _has_methodology(content: str) -> tuple[bool, str]:
    """Verify final report has audit methodology section."""
    if "## Audit Methodology" not in content:
        return (False, "Missing '## Audit Methodology' section")
    return (True, "")


def _valid_json_structure(content: str) -> tuple[bool, str]:
    """Verify content is valid JSON."""
    try:
        json.loads(content)
        return (True, "")
    except json.JSONDecodeError as e:
        return (False, f"Invalid JSON: {e}")


def _json_has_batch_lists(content: str) -> tuple[bool, str]:
    """Verify JSON contains batch assignment lists."""
    try:
        data = json.loads(content)
        if "batches" not in data and "batch_configs" not in data:
            return (False, "JSON missing 'batches' or 'batch_configs' key")
        return (True, "")
    except json.JSONDecodeError as e:
        return (False, f"Invalid JSON: {e}")


# ────────────────────────────────────────────
# Gate Definitions
# ────────────────────────────────────────────

INVENTORY_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="LIGHT",
    semantic_checks=[
        SemanticCheck(name="valid_json", check_fn=_valid_json_structure,
                      failure_message="inventory.json is not valid JSON"),
    ],
)

PASS_CONFIG_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="LIGHT",
    semantic_checks=[
        SemanticCheck(name="valid_json", check_fn=_valid_json_structure,
                      failure_message="pass-config.json is not valid JSON"),
        SemanticCheck(name="has_batches", check_fn=_json_has_batch_lists,
                      failure_message="pass-config.json missing batch lists"),
    ],
)

PASS1_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=["status", "batch", "files_audited", "files_total"],
    min_lines=30,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(name="has_sections", check_fn=_has_required_batch_sections,
                      failure_message="Batch report missing required sections"),
    ],
)

PASS1_VALIDATE_GATE = GateCriteria(
    required_frontmatter_fields=["status", "findings_checked", "discrepancies_found"],
    min_lines=20,
    enforcement_tier="STANDARD",
)

PASS_SUMMARY_GATE = GateCriteria(
    required_frontmatter_fields=["status", "total_files", "coverage_pct"],
    min_lines=80,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(name="has_sections", check_fn=_has_required_summary_sections,
                      failure_message="Summary missing required sections"),
        SemanticCheck(name="has_gate_table", check_fn=_has_quality_gate_table,
                      failure_message="Summary missing quality gate table"),
    ],
)

PASS2_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=["status", "batch", "files_audited"],
    min_lines=50,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(name="has_profiles", check_fn=_has_mandatory_profiles,
                      failure_message="Missing mandatory per-file profiles"),
        SemanticCheck(name="profiles_complete", check_fn=_profiles_have_all_fields,
                      failure_message="Profiles missing mandatory fields"),
    ],
)

PASS3_BATCH_GATE = GateCriteria(
    required_frontmatter_fields=["status", "batch", "files_audited"],
    min_lines=40,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(name="has_dup_matrix", check_fn=_has_duplication_matrix,
                      failure_message="Missing duplication matrix"),
        SemanticCheck(name="has_profiles", check_fn=_has_7field_profiles,
                      failure_message="Profiles missing mandatory fields"),
    ],
)

FILTER_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="LIGHT",
    semantic_checks=[
        SemanticCheck(name="valid_json", check_fn=_valid_json_structure,
                      failure_message="Filter output is not valid JSON"),
    ],
)

FINAL_REPORT_GATE = GateCriteria(
    required_frontmatter_fields=[
        "status", "total_files", "passes_completed",
        "delete_count", "consolidate_count", "flag_count",
    ],
    min_lines=150,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(name="has_executive_summary", check_fn=_has_executive_summary,
                      failure_message="Missing Executive Summary"),
        SemanticCheck(name="has_action_items", check_fn=_has_action_items,
                      failure_message="Missing Action Items"),
        SemanticCheck(name="has_methodology", check_fn=_has_methodology,
                      failure_message="Missing Audit Methodology"),
    ],
)


# All gates indexed by step ID
ALL_GATES: dict[str, GateCriteria] = {
    "repo-inventory": INVENTORY_GATE,
    "configure-passes": PASS_CONFIG_GATE,
    "pass1-surface-scan": PASS1_BATCH_GATE,
    "pass1-validate": PASS1_VALIDATE_GATE,
    "pass1-consolidate": PASS_SUMMARY_GATE,
    "pass2-structural-audit": PASS2_BATCH_GATE,
    "pass2-consolidate": PASS_SUMMARY_GATE,
    "pass3-cross-cutting": PASS3_BATCH_GATE,
    "filter-pass2-files": FILTER_GATE,
    "filter-pass3-files": FILTER_GATE,
    "final-report": FINAL_REPORT_GATE,
}
```

---

## 6. Executor Design (`executor.py`)

Synchronous execution loop with `concurrent.futures.ThreadPoolExecutor` for batch parallelism. NOT async/await.

### Architecture

```python
"""Sprint-style supervised executor for cleanup-audit pipeline.

Controls the multi-pass audit execution loop with:
- Per-batch live monitoring via ThreadPoolExecutor
- TUI refresh at ~2Hz
- Stall detection and watchdog per subprocess
- Signal-aware graceful shutdown
- Deterministic status classification
- TurnLedger budget tracking
- Resume semantics at pass and batch level

IMPORTANT: Uses synchronous execution with threading, NOT async/await.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import json
import shutil
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from pathlib import Path
from typing import Callable

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.sprint.models import TurnLedger

from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator
from .filtering import (
    run_configure_passes,
    run_filter_pass2_files,
    run_filter_pass3_files,
)
from .gates import (
    ALL_GATES,
    PASS1_BATCH_GATE,
    PASS2_BATCH_GATE,
    PASS3_BATCH_GATE,
    PASS_SUMMARY_GATE,
    PASS1_VALIDATE_GATE,
    FINAL_REPORT_GATE,
)
from .inventory import run_repo_inventory
from .logging_ import AuditLogger
from .models import (
    AuditConfig,
    AuditMonitorState,
    AuditOutcome,
    AuditResult,
    AuditStepStatus,
    BatchAssignment,
    BatchResult,
    PassResult,
)
from .monitor import OutputMonitor, detect_error_max_turns
from .process import AuditProcess, SignalHandler, setup_isolation
from .tui import AuditTUI


# ── Programmatic step registry ──

PROGRAMMATIC_STEPS: dict[str, Callable[[AuditConfig], None]] = {
    "repo-inventory": run_repo_inventory,
    "configure-passes": run_configure_passes,
    "filter-pass2-files": run_filter_pass2_files,
    "filter-pass3-files": run_filter_pass3_files,
}


def execute_cleanup_audit(config: AuditConfig) -> AuditResult:
    """Execute the cleanup-audit pipeline with supervised monitoring."""

    # ── Pre-flight ──
    if not shutil.which("claude"):
        print("Error: 'claude' binary not found in PATH", file=sys.stderr)
        sys.exit(1)

    # ── Infrastructure setup ──
    handler = SignalHandler()
    logger = AuditLogger(config)
    tui = AuditTUI(config)
    result = AuditResult(config=config)
    ledger = TurnLedger(
        initial_budget=config.max_turns,
        minimum_allocation=config.min_launch_allocation,
        minimum_remediation_budget=config.min_remediation_budget,
    )

    logger.write_header()
    tui.start()

    try:
        # ── Step 1: Repo Inventory (programmatic) ──
        if handler.shutdown_requested:
            result.outcome = AuditOutcome.INTERRUPTED
            return _finalize(result, logger, tui, handler)

        _run_programmatic_step("repo-inventory", config, logger, tui)

        # ── Step 2: Configure Passes (programmatic) ──
        _run_programmatic_step("configure-passes", config, logger, tui)

        # ── Execute passes ──
        for pass_num in config.passes_to_run():
            if handler.shutdown_requested:
                result.outcome = AuditOutcome.INTERRUPTED
                break

            # Skip completed passes on resume
            if config.resume_from_pass and pass_num < config.resume_from_pass:
                continue

            # Filter files for pass 2 and 3
            if pass_num == 2:
                _run_programmatic_step("filter-pass2-files", config, logger, tui)
            elif pass_num == 3:
                _run_programmatic_step("filter-pass3-files", config, logger, tui)

            # Run the pass
            pass_result = _execute_pass(
                pass_num, config, handler, logger, tui, ledger, result
            )
            result.pass_results.append(pass_result)

            if pass_result.status not in (AuditStepStatus.PASS, AuditStepStatus.PASS_NO_SIGNAL):
                result.outcome = AuditOutcome.HALTED
                result.halt_step = f"pass{pass_num}"
                result.halt_reason = f"Pass {pass_num} failed"
                break

        # ── Step 12: Final Report (if all passes completed) ──
        if result.outcome == AuditOutcome.SUCCESS and not handler.shutdown_requested:
            if not ledger.can_launch():
                result.outcome = AuditOutcome.HALTED
                result.halt_reason = "Budget exhausted before final report"
            else:
                _run_final_report(config, handler, logger, tui, ledger, result)

    finally:
        _finalize(result, logger, tui, handler)

    return result


def _execute_pass(
    pass_num: int,
    config: AuditConfig,
    handler: SignalHandler,
    logger: AuditLogger,
    tui: AuditTUI,
    ledger: TurnLedger,
    pipeline_result: AuditResult,
) -> PassResult:
    """Execute a single audit pass with batched parallel agents."""

    pass_result = PassResult(pass_number=pass_num)

    # Load batch assignments
    if pass_num == 1:
        pass_config = json.loads(config.pass_config_path.read_text())
        batches_data = pass_config["batch_configs"].get(f"pass{pass_num}", [])
    else:
        filter_config_path = config.work_dir / f"pass{pass_num}-config.json"
        filter_config = json.loads(filter_config_path.read_text())
        batches_data = filter_config.get("batches", [])

    batches = [BatchAssignment.from_dict(b) for b in batches_data]

    if not batches:
        pass_result.status = AuditStepStatus.SKIPPED
        return pass_result

    # Ensure pass directory exists
    config.pass_dir[pass_num].mkdir(parents=True, exist_ok=True)

    # ── Batch execution via ThreadPoolExecutor ──
    batch_results: list[BatchResult] = []

    with ThreadPoolExecutor(max_workers=config.max_concurrency) as pool:
        future_to_batch: dict[Future, BatchAssignment] = {}

        for batch in batches:
            if handler.shutdown_requested:
                break
            if not ledger.can_launch():
                pipeline_result.halt_reason = "Budget exhausted"
                break

            future = pool.submit(
                _execute_batch, batch, config, handler, tui, ledger
            )
            future_to_batch[future] = batch

        # Collect results as they complete
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_result = future.result()
            except Exception as e:
                batch_result = BatchResult(
                    batch_number=batch.batch_number,
                    pass_number=pass_num,
                    status=AuditStepStatus.ERROR,
                )
            batch_results.append(batch_result)
            logger.write_batch_result(batch_result)

    pass_result.batch_results = batch_results

    # ── Gate check all batch results ──
    all_batches_passed = all(
        br.status in (AuditStepStatus.PASS, AuditStepStatus.PASS_NO_SIGNAL)
        for br in batch_results
    )

    if not all_batches_passed:
        pass_result.status = AuditStepStatus.HALT
        return pass_result

    # ── Validation (TRAILING gate — Pass 1 only) ──
    if pass_num == 1 and ledger.can_launch():
        validation_result = _run_validation(config, handler, tui, ledger)
        pass_result.validation_result = validation_result
        # TRAILING: don't block on validation failure

    # ── Consolidation ──
    if not ledger.can_launch():
        pass_result.status = AuditStepStatus.INCOMPLETE
        return pass_result

    consolidation_result = _run_consolidation(
        pass_num, config, handler, tui, ledger
    )
    pass_result.consolidation_result = consolidation_result

    if consolidation_result.status in (AuditStepStatus.PASS, AuditStepStatus.PASS_NO_SIGNAL):
        pass_result.status = AuditStepStatus.PASS
    else:
        pass_result.status = consolidation_result.status

    return pass_result


def _execute_batch(
    batch: BatchAssignment,
    config: AuditConfig,
    handler: SignalHandler,
    tui: AuditTUI,
    ledger: TurnLedger,
) -> BatchResult:
    """Execute a single batch subprocess. Runs in a thread."""

    br = BatchResult(
        batch_number=batch.batch_number,
        pass_number=batch.pass_number,
        started_at=time.time(),
    )

    monitor = OutputMonitor()
    output_path = Path(batch.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Setup subprocess isolation
    env = setup_isolation(output_path.parent)

    process = AuditProcess(config, batch, env)
    monitor.reset(output_path)
    monitor.start()

    deadline = time.monotonic() + config.batch_timeout
    process.start()

    # Supervision loop (per-thread)
    while process.is_running():
        if handler.shutdown_requested:
            process.stop()
            break
        if time.monotonic() > deadline:
            process.stop()
            br.status = AuditStepStatus.TIMEOUT
            break

        state = monitor.get_state()
        if (config.stall_timeout
                and state.stall_seconds > config.stall_timeout
                and state.events_received > 0):
            process.stop()
            break

        try:
            tui.update_batch(batch.pass_number, batch.batch_number, state)
        except Exception:
            pass

        time.sleep(0.5)

    # Classify result
    exit_code = process.wait()
    monitor.stop()
    br.exit_code = exit_code
    br.finished_at = time.time()
    br.output_bytes = monitor.state.output_bytes

    if br.status == AuditStepStatus.TIMEOUT:
        pass  # already set
    elif exit_code == 124:
        br.status = AuditStepStatus.TIMEOUT
    elif exit_code and exit_code != 0:
        br.status = AuditStepStatus.ERROR
    elif output_path.exists():
        content = output_path.read_text()
        if "EXIT_RECOMMENDATION: HALT" in content:
            br.status = AuditStepStatus.HALT
        elif "EXIT_RECOMMENDATION: CONTINUE" in content:
            br.status = AuditStepStatus.PASS
            # Run gate check
            gate = ALL_GATES.get(f"pass{batch.pass_number}-surface-scan", None)
            if batch.pass_number == 2:
                gate = ALL_GATES.get("pass2-structural-audit")
            elif batch.pass_number == 3:
                gate = ALL_GATES.get("pass3-cross-cutting")
            if gate:
                passed, reason = gate_passed(output_path, gate)
                if not passed:
                    br.status = AuditStepStatus.HALT
                    br.gate_failure_reason = reason or "Gate failed"
                else:
                    br.gate_passed = True
        else:
            br.status = AuditStepStatus.PASS_NO_SIGNAL
    else:
        br.status = AuditStepStatus.ERROR

    # Estimate turns consumed from output size
    br.turns_consumed = max(1, br.output_bytes // 2000)
    ledger.debit(br.turns_consumed)

    return br


def _run_programmatic_step(
    step_id: str,
    config: AuditConfig,
    logger: AuditLogger,
    tui: AuditTUI,
) -> None:
    """Execute a pure-programmatic step."""
    logger.write_step_start(step_id)
    started = time.time()
    try:
        PROGRAMMATIC_STEPS[step_id](config)
        logger.write_step_pass(step_id, time.time() - started)
    except Exception as e:
        logger.write_step_error(step_id, str(e))
        raise


def _run_validation(
    config: AuditConfig,
    handler: SignalHandler,
    tui: AuditTUI,
    ledger: TurnLedger,
) -> BatchResult:
    """Run Pass 1 spot-check validation. TRAILING gate — does not block."""
    # Implementation follows same pattern as _execute_batch
    # but for the audit-validator agent
    br = BatchResult(batch_number=0, pass_number=1, started_at=time.time())
    # ... subprocess launch, monitoring, gate check ...
    br.finished_at = time.time()
    return br


def _run_consolidation(
    pass_num: int,
    config: AuditConfig,
    handler: SignalHandler,
    tui: AuditTUI,
    ledger: TurnLedger,
) -> BatchResult:
    """Run consolidation for a pass."""
    br = BatchResult(batch_number=0, pass_number=pass_num, started_at=time.time())
    # ... subprocess launch for audit-consolidator ...
    br.finished_at = time.time()
    return br


def _run_final_report(
    config: AuditConfig,
    handler: SignalHandler,
    logger: AuditLogger,
    tui: AuditTUI,
    ledger: TurnLedger,
    result: AuditResult,
) -> None:
    """Run final report generation."""
    # ... subprocess launch for audit-consolidator with final-report template ...
    pass


def _finalize(
    result: AuditResult,
    logger: AuditLogger,
    tui: AuditTUI,
    handler: SignalHandler,
) -> AuditResult:
    """Finalize pipeline execution."""
    result.finished_at = time.time()
    logger.write_summary(result)
    tui.stop()
    handler.restore()
    return result
```

---

## 7. Subprocess Isolation (`process.py`)

```python
"""Claude subprocess wrapper for cleanup-audit pipeline.

Provides 4-layer isolation for child Claude sessions:
1. Scoped work directory
2. Git ceiling
3. Isolated plugin directory
4. Isolated settings directory
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from .models import AuditConfig, BatchAssignment


class SignalHandler:
    """Trap SIGINT/SIGTERM and set shutdown flag."""

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


def setup_isolation(work_dir: Path) -> dict[str, str]:
    """Create isolated environment for child Claude subprocess.

    4-layer isolation model:
    1. Scoped work directory — subprocess can only write here
    2. Git ceiling — prevents git operations escaping work_dir
    3. Isolated plugin directory — no cross-contamination
    4. Isolated settings — independent config
    """
    env = os.environ.copy()

    # Layer 1: Scoped work directory
    env["CLAUDE_WORK_DIR"] = str(work_dir)

    # Layer 2: Git ceiling
    env["GIT_CEILING_DIRECTORIES"] = str(work_dir.parent)

    # Layer 3: Isolated plugin directory
    plugin_dir = work_dir / ".claude-plugins"
    plugin_dir.mkdir(exist_ok=True)
    env["CLAUDE_PLUGIN_DIR"] = str(plugin_dir)

    # Layer 4: Isolated settings
    settings_dir = work_dir / ".claude-settings"
    settings_dir.mkdir(exist_ok=True)
    env["CLAUDE_SETTINGS_DIR"] = str(settings_dir)

    return env


class AuditProcess:
    """Wraps a Claude subprocess for audit batch execution."""

    def __init__(
        self,
        config: AuditConfig,
        batch: BatchAssignment,
        env: dict[str, str] | None = None,
    ):
        self.config = config
        self.batch = batch
        self.env = env or os.environ.copy()
        self._process: subprocess.Popen | None = None
        self.started_at: float | None = None
        self._exit_code: int | None = None

    def start(self) -> None:
        """Launch the Claude subprocess."""
        from .prompts import build_prompt_for_batch

        prompt = build_prompt_for_batch(self.batch, self.config)

        cmd = [
            "claude",
            "--print",
            "--output-format", "stream-json",
            "--max-turns", str(self.batch.agent_type.max_turns),
            "--model", self.batch.agent_type.model,
            self.config.permission_flag,
            "-p", prompt,
        ]

        self.started_at = time.time()
        output_path = Path(self.batch.output_path)

        self._process = subprocess.Popen(
            cmd,
            stdout=open(output_path, "w"),
            stderr=subprocess.PIPE,
            env=self.env,
            cwd=str(self.config.target_path),
        )

    def is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    def stop(self) -> None:
        if self._process and self.is_running():
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def wait(self) -> int | None:
        if self._process is None:
            return None
        self._exit_code = self._process.wait()
        return self._exit_code
```

---

## 8. TurnLedger Budget Economics

The pipeline uses the existing `TurnLedger` from `superclaude.cli.sprint.models`.

### Budget Allocation Model

For a full 3-pass audit of a repo with ~500 files:

| Component | Batches | Turns/Batch | Total Turns |
|-----------|---------|-------------|-------------|
| Pass 1 batches (Haiku) | 10 | 15 | 150 |
| Pass 1 validation | 1 | 20 | 20 |
| Pass 1 consolidation | 1 | 30 | 30 |
| Pass 2 batches (Sonnet) | 12 | 25 | 300 |
| Pass 2 consolidation | 1 | 30 | 30 |
| Pass 3 batches (Sonnet) | 8 | 25 | 200 |
| Final report | 1 | 35 | 35 |
| **Total** | **34** | — | **~765** |

### Pre-Launch Budget Guards

```python
# Before launching any batch
if not ledger.can_launch():
    result.outcome = AuditOutcome.HALTED
    result.halt_reason = (
        f"Budget exhausted: {ledger.available()} turns remaining, "
        f"minimum {ledger.minimum_allocation} required"
    )
    break

# Before launching a pass (estimate)
estimated_turns_for_pass = len(batches) * estimated_turns_per_batch
if ledger.available() < estimated_turns_for_pass * 0.5:
    # Warn but don't block — may complete with fewer turns
    logger.write_warning(
        f"Budget may be insufficient for pass {pass_num}: "
        f"{ledger.available()} available, ~{estimated_turns_for_pass} estimated"
    )
```

### Post-Run Reconciliation

```python
# After each batch completes
actual_turns = estimate_turns_from_output(output_path)
allocated_turns = batch.agent_type.max_turns
ledger.debit(actual_turns)

# Credit unused allocation back
if actual_turns < allocated_turns:
    ledger.credit(int((allocated_turns - actual_turns) * ledger.reimbursement_rate))
```

---

## 9. Resume Semantics

### Resume Command Implementation

```python
def resume_command(self) -> str | None:
    """Generate CLI command to resume from the failed point."""
    if not self.halt_step:
        return None

    # Determine resume point
    parts = ["superclaude", "cleanup-audit", "run", str(self.config.target_path)]

    # Parse halt_step to find pass number
    if self.halt_step.startswith("pass"):
        pass_num = int(self.halt_step.replace("pass", ""))
        parts.append(f"--resume-from-pass {pass_num}")

    # Carry forward config
    if self.config.focus != AuditFocus.ALL:
        parts.append(f"--focus {self.config.focus.value}")
    if self.config.audit_pass != AuditPass.ALL:
        parts.append(f"--pass {self.config.audit_pass.value}")

    # Budget suggestion
    parts.append(f"--max-turns {self.suggested_resume_budget}")

    return " ".join(parts)


@property
def suggested_resume_budget(self) -> int:
    """Estimate turns needed to complete remaining work."""
    remaining_passes = [
        pr for pr in self.pass_results
        if pr.status in (AuditStepStatus.PENDING, AuditStepStatus.INCOMPLETE)
    ]
    # 60 turns per remaining pass (conservative estimate)
    return max(len(remaining_passes) * 60, 50)
```

### Resume Logic in Executor

```python
# In execute_cleanup_audit():
for pass_num in config.passes_to_run():
    # Skip completed passes on resume
    if config.resume_from_pass and pass_num < config.resume_from_pass:
        # Verify pass summary exists (proof of completion)
        summary_path = config.pass_summary_path(pass_num)
        if summary_path.exists():
            logger.write_pass_skipped(pass_num, "already completed")
            continue
        else:
            # Summary missing — re-run this pass
            logger.write_warning(f"Pass {pass_num} summary missing, re-running")

    # Within a pass: skip completed batches
    for batch in batches:
        report_path = Path(batch.output_path)
        if report_path.exists():
            # Validate existing report
            content = report_path.read_text()
            gate = ALL_GATES.get(f"pass{pass_num}-surface-scan")
            passed, _ = gate_passed(report_path, gate) if gate else (True, None)
            if passed:
                logger.write_batch_skipped(batch.batch_number, "gate passed")
                continue
```

### Halt Output Format

```python
def build_halt_output(result: AuditResult) -> str:
    """Build actionable HALT output with resume info."""
    lines = [
        "## HALT -- Cleanup Audit Paused",
        "",
        "### Resume Command",
        "```",
        result.resume_command() or "# Unable to generate resume command",
        "```",
        "",
        f"### Status",
        f"- Passes completed: {result.passes_completed}",
        f"- Total turns consumed: {result.total_turns_consumed}",
        f"- Duration: {result.duration_seconds:.1f}s",
    ]

    if result.halt_reason:
        lines.append(f"- Halt reason: {result.halt_reason}")

    lines.extend([
        "",
        "### Remaining Work",
    ])
    for pr in result.pass_results:
        if pr.status in (AuditStepStatus.PENDING, AuditStepStatus.INCOMPLETE):
            lines.append(f"- Pass {pr.pass_number}: {pr.status.value}")

    lines.extend([
        "",
        f"### Suggested Budget: {result.suggested_resume_budget} turns",
        "",
        f"### Diagnostic Output",
        f"See: {result.config.work_dir / 'diagnostics/'}",
    ])

    return "\n".join(lines)
```

---

## 10. Click Commands (`commands.py`)

```python
"""Click CLI commands for cleanup-audit pipeline.

Provides the `superclaude cleanup-audit` command group.
"""

from __future__ import annotations

import sys

import click

from .config import load_cleanup_audit_config
from .executor import execute_cleanup_audit


@click.group("cleanup-audit")
def cleanup_audit_group():
    """Multi-pass read-only repository audit pipeline."""
    pass


@cleanup_audit_group.command("run")
@click.argument("target", default=".")
@click.option("--pass", "audit_pass", default="all",
              type=click.Choice(["surface", "structural", "cross-cutting", "all"]))
@click.option("--batch-size", default=None, type=int,
              help="Override batch size for all passes")
@click.option("--focus", default="all",
              type=click.Choice(["infrastructure", "frontend", "backend", "all"]))
@click.option("--max-turns", default=200, type=int)
@click.option("--max-concurrency", default=7, type=int)
@click.option("--model", default=None, help="Override default model")
@click.option("--resume-from-pass", default=None, type=int,
              help="Resume from a specific pass number")
@click.option("--dry-run", is_flag=True, help="Show plan without running")
@click.option("--debug", is_flag=True)
def run(target, audit_pass, batch_size, focus, max_turns,
        max_concurrency, model, resume_from_pass, dry_run, debug):
    """Execute the cleanup-audit pipeline."""
    config = load_cleanup_audit_config(
        target=target,
        audit_pass=audit_pass,
        batch_size=batch_size,
        focus=focus,
        max_turns=max_turns,
        max_concurrency=max_concurrency,
        model=model,
        resume_from_pass=resume_from_pass,
        dry_run=dry_run,
        debug=debug,
    )

    if dry_run:
        _print_dry_run(config)
        return

    result = execute_cleanup_audit(config)

    if result.outcome == AuditOutcome.HALTED:
        from .models import AuditOutcome
        from .executor import build_halt_output
        print(build_halt_output(result))

    sys.exit(0 if result.outcome.value == "success" else 1)


def _print_dry_run(config):
    """Display execution plan without running."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Cleanup Audit Pipeline Plan")
    table.add_column("Pass", style="cyan")
    table.add_column("Agent", style="green")
    table.add_column("Batch Size", style="yellow")
    table.add_column("Gate Tier", style="dim")

    for pass_num in config.passes_to_run():
        agent = {1: "Haiku (scanner)", 2: "Sonnet (analyzer)", 3: "Sonnet (comparator)"}[pass_num]
        bs = config.batch_size_for_pass(pass_num)
        gate = {1: "STANDARD", 2: "STRICT", 3: "STRICT"}[pass_num]
        table.add_row(f"Pass {pass_num}", agent, str(bs), gate)

    table.add_row("Consolidation", "Sonnet", "-", "STRICT")
    table.add_row("Final Report", "Sonnet", "-", "STRICT")

    console.print(table)
    console.print(f"\nTarget: {config.target_path}")
    console.print(f"Focus: {config.focus.value}")
    console.print(f"Max turns: {config.max_turns}")
    console.print(f"Max concurrency: {config.max_concurrency}")
```

---

## 11. Config Loading (`config.py`)

```python
"""Configuration loading and validation for cleanup-audit pipeline."""

from __future__ import annotations

from pathlib import Path

from .models import AuditConfig, AuditFocus, AuditPass


def load_cleanup_audit_config(
    target: str = ".",
    audit_pass: str = "all",
    batch_size: int | None = None,
    focus: str = "all",
    max_turns: int = 200,
    max_concurrency: int = 7,
    model: str | None = None,
    resume_from_pass: int | None = None,
    dry_run: bool = False,
    debug: bool = False,
) -> AuditConfig:
    """Construct and validate pipeline configuration from CLI arguments."""
    target_path = Path(target).resolve()
    if not target_path.exists():
        raise click.BadParameter(f"Target path does not exist: {target_path}")

    config = AuditConfig(
        target_path=target_path,
        audit_pass=AuditPass(audit_pass),
        focus=AuditFocus(focus),
        max_turns=max_turns,
        max_concurrency=max_concurrency,
        resume_from_pass=resume_from_pass,
        dry_run=dry_run,
        debug=debug,
    )

    # Override batch sizes if specified
    if batch_size is not None:
        config.batch_size_pass1 = batch_size
        config.batch_size_pass2 = batch_size
        config.batch_size_pass3 = batch_size

    if model:
        config.model = model

    return config
```

---

## 12. Integration Plan

### main.py Patch

```python
# Add import:
from superclaude.cli.cleanup_audit import cleanup_audit_group

# Add command:
app.add_command(cleanup_audit_group)
```

### __init__.py

```python
"""CLI subcommand package for cleanup-audit pipeline.

Portified from: sc-cleanup-audit-protocol
Generated by: sc-cli-portify

This module provides the `superclaude cleanup-audit` command group.
"""

from .commands import cleanup_audit_group

__all__ = ["cleanup_audit_group"]
```

---

## 13. Step-to-GateMode Mapping

| Step ID | GateMode | Rationale |
|---------|----------|-----------|
| repo-inventory | BLOCKING | Downstream steps depend on inventory |
| configure-passes | BLOCKING | Batch assignments needed for pass execution |
| pass1-surface-scan | BLOCKING | Pass 2 file list derived from Pass 1 results |
| pass1-gate | BLOCKING | Must verify batch quality before consolidation |
| pass1-validate | TRAILING | Quality signal; does not affect data flow |
| pass1-consolidate | BLOCKING | Pass 2 needs consolidated Pass 1 context |
| filter-pass2-files | BLOCKING | Pass 2 batches derived from this output |
| pass2-structural-audit | BLOCKING | Pass 3 context and final report need this |
| pass2-consolidate | BLOCKING | Pass 3 needs consolidated Pass 2 context |
| filter-pass3-files | BLOCKING | Pass 3 batches derived from this output |
| pass3-cross-cutting | BLOCKING | Final report needs this |
| final-report | BLOCKING | Terminal step; must pass for SUCCESS |

Only `pass1-validate` uses TRAILING mode. All other steps are BLOCKING because each step's output feeds downstream steps.

---

## 14. File Generation Order

1. `models.py` — No internal deps
2. `inventory.py` — Imports from models
3. `filtering.py` — Imports from models, inventory
4. `gates.py` — Imports from models (pipeline)
5. `prompts.py` — Imports from models
6. `config.py` — Imports from models
7. `monitor.py` — Imports from models (follow sprint pattern)
8. `process.py` — Imports from models, config
9. `executor.py` — Imports from everything above
10. `tui.py` — Imports from models (follow sprint pattern)
11. `logging_.py` — Imports from models (follow sprint pattern)
12. `diagnostics.py` — Imports from models (follow sprint pattern)
13. `commands.py` — Imports from config, executor
14. `__init__.py` — Re-exports
