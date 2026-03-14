# Design: accept-spec-change Command + Auto-Resume Cycle
# Source spec: brainstorm-accept-spec-change.md
# Date: 2026-03-13
# Status: Ready for sc:roadmap

---

## 1. System Context

```
┌─────────────────────────────────────────────────────────────────┐
│  superclaude roadmap                                            │
│                                                                 │
│  ┌──────────┐   ┌────────────────┐   ┌───────────────────────┐ │
│  │  run     │   │ accept-spec-   │   │  validate             │ │
│  │ command  │   │ change command │   │  command              │ │
│  └────┬─────┘   └───────┬────────┘   └───────────────────────┘ │
│       │                 │                                       │
│       ▼                 ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  executor.py                                            │   │
│  │  execute_roadmap()   ←── NEW: auto_accept param        │   │
│  │  _apply_resume()                                        │   │
│  │  _apply_resume_after_spec_patch()  ←── NEW             │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                           │
│                     ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  spec_patch.py  ←── NEW MODULE                          │  │
│  │  scan_accepted_deviation_records()                       │  │
│  │  update_spec_hash()                                      │  │
│  │  prompt_accept_spec_change()                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                     │                                           │
│                     ▼                                           │
│            .roadmap-state.json  (on disk)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency graph (strict — no cycles)

```
commands.py  ──►  spec_patch.py
executor.py  ──►  spec_patch.py
spec_patch.py ──► (stdlib only: pathlib, hashlib, json, yaml, os, sys)
```

`spec_patch.py` imports nothing from `executor.py` or `commands.py`.

---

## 2. New Module: `src/superclaude/cli/roadmap/spec_patch.py`

### 2.1 Module header

```python
"""spec_patch — utilities for accepting spec-hash changes backed by deviation evidence.

Public API:
    scan_accepted_deviation_records(output_dir) -> list[DeviationRecord]
    update_spec_hash(state_file, new_hash, old_hash) -> None
    prompt_accept_spec_change(records, auto_accept) -> bool
"""
from __future__ import annotations

import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # PyYAML — already a transitive dependency via existing roadmap code
```

### 2.2 Data types

```python
@dataclass(frozen=True)
class DeviationRecord:
    """Parsed and validated accepted deviation record."""
    id: str                           # e.g. "DEV-001"
    disposition: str                  # normalized to uppercase
    spec_update_required: bool        # YAML boolean only
    affects_spec_sections: list[str]  # may be empty list
    acceptance_rationale: str         # may be empty string
    source_file: Path                 # absolute path to the .md file
    mtime: float                      # os.path.getmtime() at scan time
```

**Invariants**:
- `disposition` is always stored uppercase after normalization
- `spec_update_required` is always a Python `bool` (never str)
- `mtime` is a Unix timestamp float, captured once at scan time

### 2.3 `scan_accepted_deviation_records()`

```python
def scan_accepted_deviation_records(
    output_dir: Path,
    *,
    require_disposition: str = "ACCEPTED",
    require_spec_update: bool = True,
) -> list[DeviationRecord]:
    """Scan output_dir for dev-*-accepted-deviation.md files matching criteria.

    Glob pattern: output_dir / "dev-*-accepted-deviation.md"
    For each file:
      - Parse YAML frontmatter (content between first --- delimiters)
      - On parse failure: emit warning to stderr, skip file
      - On missing field: apply negative default (see below)
      - disposition: case-insensitive string match against require_disposition
      - spec_update_required: must be Python bool True (not string "true")

    Field defaults on absent/null:
      disposition        → "" (empty, will not match any require_disposition)
      spec_update_required → False
      id                 → filename stem (e.g. "dev-001-accepted-deviation")
      affects_spec_sections → []
      acceptance_rationale  → ""

    Returns:
        List of DeviationRecord instances that match all filter criteria.
        Empty list if no files found or none match.

    Side effects:
        Warnings emitted to sys.stderr for unparseable files.
        No exceptions raised for individual file failures.
    """
```

**Internal parse logic** (not exposed):

```python
def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract and parse YAML frontmatter from a markdown file.

    Looks for content between the first pair of '---' delimiters.
    Returns None on any parse failure (caller emits warning and skips).
    Returns empty dict {} if delimiters found but content is empty.
    """
    try:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        end = text.index("---", 3)
        frontmatter_text = text[3:end].strip()
        if not frontmatter_text:
            return {}
        return yaml.safe_load(frontmatter_text) or {}
    except Exception:  # noqa: BLE001
        return None
```

**YAML boolean guard** (not exposed):

```python
def _coerce_spec_update_required(value: Any) -> bool:
    """Return True only for Python bool True. Strings like 'true' return False."""
    return value is True  # strict identity — rejects str, int, etc.
```

**YAML boolean note**: PyYAML `safe_load` treats `yes`, `on`, `1` as boolean `True`
per YAML 1.1 spec. This is intentional — all YAML boolean forms are accepted for
`spec_update_required`. The `_coerce_spec_update_required` guard (`value is True`)
accepts any Python `True` regardless of which YAML literal produced it.

### 2.4 `update_spec_hash()`

```python
def update_spec_hash(
    state_file: Path,
    new_hash: str,
    *,
    old_hash: str,          # used for verification and FR-7 output only
) -> None:
    """Atomically update spec_hash in state_file, preserving all other keys.

    Reads current state from state_file, replaces spec_hash, writes to
    <state_file>.tmp on the same filesystem, then os.replace() to final path.

    Args:
        state_file: Absolute path to .roadmap-state.json
        new_hash:   sha256 hex digest of the current spec file
        old_hash:   sha256 hex digest stored in current state (for logging)

    Raises:
        FileNotFoundError: if state_file does not exist
        json.JSONDecodeError: if state_file content is not valid JSON
        OSError: if the atomic write fails (caller must handle)

    Contract:
        - If this function raises, state_file is guaranteed unmodified
          (atomic write semantics: tmp is written, then os.replace())
        - If .tmp file exists on entry, it is overwritten
        - Only spec_hash key is modified; all other keys preserved verbatim
    """
    import json

    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["spec_hash"] = new_hash

    tmp = state_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(state_file))
```

**Design note**: `update_spec_hash()` does NOT read the spec file itself — it takes
pre-computed hashes. The caller (commands or executor) computes the hash. This keeps
`spec_patch.py` free of `config` or `RoadmapConfig` dependencies.

### 2.5 `prompt_accept_spec_change()`

```python
def prompt_accept_spec_change(
    records: list[DeviationRecord],
    *,
    auto_accept: bool,
    old_hash: str,
    new_hash: str,
) -> bool:
    """Display evidence summary and optionally prompt user for confirmation.

    Args:
        records:     Non-empty list of matching DeviationRecord instances
        auto_accept: If True, skip prompt and return True immediately
        old_hash:    Currently stored spec_hash (for display)
        new_hash:    Current spec file hash (for display)

    Returns:
        True  — user confirmed (or auto_accept=True)
        False — user declined, non-interactive with auto_accept=False, or empty input

    Non-interactive detection:
        If not sys.stdin.isatty() and auto_accept is False, returns False immediately
        without printing the prompt. Prints "Aborted." to stdout.

    Input normalization:
        Confirmation requires exactly 'y' or 'Y'. All other input returns False.
    """
```

**Sequence diagram** (interactive path):

```
prompt_accept_spec_change(records, auto_accept=False)
│
├─ auto_accept=True?  ──yes──► return True
│
├─ not sys.stdin.isatty()?  ──yes──► print "Aborted." ──► return False
│
├─ print summary block (N records, IDs, sections, rationale)
├─ print "[y/N]: " (no newline)
├─ read one line from stdin
├─ strip() and lower()
├─ == "y"? ──yes──► return True
└─ else ──────────► return False
```

---

## 3. Modified: `executor.py`

### 3.1 `execute_roadmap()` — signature change

```python
# BEFORE
def execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
) -> None:

# AFTER
def execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
    auto_accept: bool = False,         # NEW — default preserves backward compat
) -> None:
```

### 3.2 `execute_roadmap()` — body changes

Two additions to the existing body:

**Addition A** — capture `initial_spec_hash` at function entry (before pipeline):

```python
def execute_roadmap(..., auto_accept: bool = False) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # NEW: capture hash before pipeline runs (FR-9 Condition 3)
    initial_spec_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
    _spec_patch_cycle_count = 0  # NEW: local recursion guard (FR-11)

    steps = _build_steps(config)
    # ... rest of existing body unchanged until failure check ...
```

**Addition B** — post-failure check (after existing `_save_state()` call, before
`_format_halt_output`):

```python
    # Save state (existing)
    _save_state(config, results)

    # Check for failures (existing logic, slightly restructured)
    failures = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]
    if failures:
        # NEW: attempt spec-patch auto-resume before surfacing failure
        resumed = _apply_resume_after_spec_patch(
            config=config,
            results=results,
            initial_spec_hash=initial_spec_hash,
            spec_patch_cycle_count=_spec_patch_cycle_count,
            auto_accept=auto_accept,
        )
        if resumed is not None:
            # Cycle fired — resumed is the new results list
            results = resumed
            _spec_patch_cycle_count += 1  # guard: prevent second cycle
            failures = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]

        if failures:
            halt_msg = _format_halt_output(results, config)
            print(halt_msg, file=sys.stderr)
            sys.exit(1)

    # ... rest unchanged (pipeline complete message, validation) ...
```

### 3.3 New private function: `_apply_resume_after_spec_patch()`

```python
def _apply_resume_after_spec_patch(
    config: RoadmapConfig,
    results: list[StepResult],
    initial_spec_hash: str,
    spec_patch_cycle_count: int,
    auto_accept: bool,
) -> list[StepResult] | None:
    """Detect and execute one spec-patch-then-resume cycle.

    Called after execute_pipeline() returns with spec-fidelity FAIL.
    Returns the new results list if the cycle fired, or None if not triggered.

    Trigger conditions (all three must be true):
      1. spec_patch_cycle_count == 0  (guard: at most one cycle)
      2. output_dir contains qualifying dev-*-accepted-deviation.md files
         (written after spec-fidelity started, matching disposition+spec_update_required)
      3. sha256(config.spec_file) != initial_spec_hash  (spec changed during run)

    If not triggered:
        Logs suppression message if cycle_count >= 1.
        Returns None.

    If triggered:
        Executes FR-10 6-step disk-reread sequence.
        Calls _apply_resume() with post-write disk state.
        Returns new results list.

    Raises:
        Does not raise. OSError from atomic write is caught and logged;
        returns None on write failure (caller falls through to normal failure).
    """
```

**Sequence** (internal, maps to FR-10 steps):

```
_apply_resume_after_spec_patch(...)
│
├─ Check condition 1: spec_patch_cycle_count >= 1?
│   ──yes──► print suppression message ──► return None
│
├─ Read state from disk (fresh_state)
│
├─ Check condition 2: qualifying deviation files written after started_at?
│   ──no──►  return None
│
├─ Check condition 3: sha256(spec_file) != initial_spec_hash?
│   ──no──►  return None
│
├─ All conditions met — log entry messages (FR-12)
│
├─ Prompt / auto_accept (calls prompt_accept_spec_change)
│   user declines ──► return None
│
├─ Compute new_hash = sha256(spec_file)
│
├─ Atomic write via update_spec_hash()  [FR-10 Step 3]
│   OSError ──► log error ──► return None
│
├─ Re-read state from disk → post_write_state  [FR-10 Step 4]
│
├─ steps = _build_steps(config)  [FR-10 Step 5]
│
├─ resumed_steps = _apply_resume(post_write_state, config, gate_passed)  [FR-10 Step 6]
│
├─ results = execute_pipeline(steps=resumed_steps, ...)
│
├─ _save_state(config, results)
│
├─ print "Spec-patch resume cycle complete."  (FR-12)
│
└─ return results
```

### 3.4 Condition 2 helper (inline or extracted)

```python
def _find_qualifying_deviation_files(
    output_dir: Path,
    spec_fidelity_started_at: str,   # ISO 8601 string from state
) -> list[Path]:
    """Return dev-*-accepted-deviation.md files written after spec-fidelity started.

    Comparison:
        os.path.getmtime(file) > datetime.fromisoformat(started_at).timestamp()
    Operator: strict > (not >=).
    Type safety: started_at is ISO 8601 str; getmtime() is float; convert before compare.
    """
    from datetime import datetime
    threshold = datetime.fromisoformat(spec_fidelity_started_at).timestamp()
    result = []
    for f in sorted(output_dir.glob("dev-*-accepted-deviation.md")):
        if os.path.getmtime(f) > threshold:
            result.append(f)
    return result
```

---

## 4. Modified: `commands.py`

### 4.1 New command: `accept-spec-change`

Registered under `roadmap_group` as a Click command. Imports from `spec_patch` at
call time (lazy import, consistent with existing commands pattern).

```python
@roadmap_group.command("accept-spec-change")
@click.argument("output_dir", type=click.Path(exists=True, path_type=Path))
def accept_spec_change(output_dir: Path) -> None:
    """Acknowledge a spec documentation sync backed by accepted deviation records.

    Updates spec_hash in .roadmap-state.json when the spec file has been edited
    to formalize an accepted deviation (not a functional change). Requires at least
    one dev-*-accepted-deviation.md file with disposition: ACCEPTED and
    spec_update_required: true in OUTPUT_DIR.

    After running this command, use 'roadmap run <spec> --resume' to continue
    from the spec-fidelity step without re-running the full pipeline.
    """
    import hashlib
    import json
    import sys

    from .spec_patch import (
        prompt_accept_spec_change,
        scan_accepted_deviation_records,
        update_spec_hash,
    )

    # FR-1: Locate state file
    state_file = output_dir / ".roadmap-state.json"
    if not state_file.exists():
        click.echo(
            f"No .roadmap-state.json found in {output_dir}. "
            "Run `roadmap run` first.",
            err=True,
        )
        sys.exit(1)

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"Could not read state file: {exc}", err=True)
        sys.exit(1)

    # FR-2: Recompute current spec hash
    spec_file_path = state.get("spec_file")
    if not spec_file_path:
        click.echo("State file missing 'spec_file' key.", err=True)
        sys.exit(1)
    spec_file = Path(spec_file_path)
    if not spec_file.exists():
        click.echo(f"Spec file not found: {spec_file}", err=True)
        sys.exit(1)
    current_hash = hashlib.sha256(spec_file.read_bytes()).hexdigest()

    # FR-3: Check hash mismatch
    stored_hash = state.get("spec_hash") or ""
    if stored_hash and current_hash == stored_hash:
        click.echo("Spec hash is already current. Nothing to do.")
        sys.exit(0)

    # FR-4: Scan for evidence
    records = scan_accepted_deviation_records(output_dir)
    if not records:
        click.echo(
            f"Spec file has changed but no accepted deviation records with "
            f"spec_update_required: true were found in {output_dir}.\n"
            "If this is a functional spec change, run `roadmap run` without --resume.\n"
            "If it is a documentation sync, create a dev-NNN-accepted-deviation.md "
            "record with spec_update_required: true before running this command.",
            err=True,
        )
        sys.exit(1)

    # FR-5: Prompt (or auto-accept — N/A for CLI; auto_accept always False here)
    confirmed = prompt_accept_spec_change(
        records=records,
        auto_accept=False,
        old_hash=stored_hash,
        new_hash=current_hash,
    )
    if not confirmed:
        click.echo("Aborted.")
        sys.exit(0)

    # FR-6: Atomic write
    try:
        update_spec_hash(state_file, current_hash, old_hash=stored_hash)
    except OSError as exc:
        click.echo(f"Failed to update state file: {exc}", err=True)
        sys.exit(1)

    # FR-7: Confirmation output
    dev_ids = ", ".join(r.id for r in records)
    click.echo(
        f"[roadmap] spec_hash updated.\n"
        f"  Old: {stored_hash[:12]}...\n"
        f"  New: {current_hash[:12]}...\n"
        f"  Accepted deviations: {dev_ids}\n"
        f"Run `superclaude roadmap run {spec_file} --resume` to continue from the failing step."
    )
```

---

## 5. Data Flow Diagrams

### 5.1 `accept-spec-change` command (manual path)

```
User: superclaude roadmap accept-spec-change <output_dir>
│
▼
commands.accept_spec_change(output_dir)
│
├── read_state(output_dir/.roadmap-state.json)
│     ├── missing → exit 1
│     └── → state dict
│
├── sha256(state["spec_file"])
│     ├── file missing → exit 1
│     └── → current_hash
│
├── current_hash == stored_hash?
│     └── yes → "Nothing to do." exit 0
│
├── spec_patch.scan_accepted_deviation_records(output_dir)
│     ├── glob dev-*-accepted-deviation.md
│     ├── for each: parse frontmatter
│     │     ├── parse error → warn + skip
│     │     └── filter: disposition=ACCEPTED, spec_update_required=True(bool)
│     └── records: list[DeviationRecord]
│           └── empty → exit 1 with guidance message
│
├── spec_patch.prompt_accept_spec_change(records, auto_accept=False, ...)
│     ├── not tty → "Aborted." return False
│     ├── print summary
│     ├── read input
│     └── "y"/"Y" → True | else → False
│           └── False → "Aborted." exit 0
│
├── spec_patch.update_spec_hash(state_file, current_hash, old_hash=stored_hash)
│     ├── read state
│     ├── state["spec_hash"] = current_hash
│     ├── write to .roadmap-state.json.tmp
│     ├── os.replace(.tmp → .roadmap-state.json)
│     └── OSError → exit 1
│
└── print FR-7 confirmation
    exit 0
```

### 5.2 Auto-resume cycle (automatic path within `execute_roadmap()`)

```
execute_roadmap(config, auto_accept=False)
│
├── initial_spec_hash = sha256(spec_file)     ← captured BEFORE pipeline
├── _spec_patch_cycle_count = 0
│
├── [existing: build steps, apply_resume if --resume]
│
├── results = execute_pipeline(...)
│
├── _save_state(config, results)
│
├── failures = [FAIL/TIMEOUT results]
│
└── if failures:
      │
      └── _apply_resume_after_spec_patch(
              config, results, initial_spec_hash,
              spec_patch_cycle_count=0, auto_accept
          )
          │
          ├── Condition 1: cycle_count >= 1?
          │     yes → log "already exhausted" → return None
          │
          ├── fresh_state = read_state(state_file)
          │
          ├── qualifying_files = _find_qualifying_deviation_files(
          │       output_dir, fresh_state["steps"]["spec-fidelity"]["started_at"]
          │   )
          │     → files where mtime > fromisoformat(started_at).timestamp()
          │
          ├── Condition 2: qualifying_files is empty?
          │     yes → return None
          │
          ├── records = scan_accepted_deviation_records(output_dir)
          │   (filter to only files in qualifying_files set)
          │
          ├── Condition 2b: records is empty?
          │     yes → return None
          │
          ├── Condition 3: sha256(spec_file) == initial_spec_hash?
          │     yes (unchanged) → return None
          │
          ├── log "[roadmap] Spec patched by subprocess..."
          │
          ├── prompt_accept_spec_change(records, auto_accept, ...)
          │     declined → return None
          │
          ├── new_hash = sha256(spec_file)
          │
          ├── update_spec_hash(state_file, new_hash, old_hash=stored)
          │     OSError → log error → return None
          │
          ├── post_write_state = read_state(state_file)   ← AFTER write
          │
          ├── steps = _build_steps(config)
          │
          ├── resumed_steps = _apply_resume(post_write_state, config, gate_passed)
          │     (hashes now match → no force_extract;
          │      spec-fidelity=FAIL → re-run; upstream=PASS → skip)
          │
          ├── results = execute_pipeline(resumed_steps, ...)
          │
          ├── _save_state(config, results)
          │
          ├── log "[roadmap] Spec-patch resume cycle complete."
          │
          └── return results
```

---

## 6. Error Taxonomy and Exit Codes

| Error | Exit | Location | Message |
|---|---|---|---|
| `.roadmap-state.json` missing | 1 | commands | "No .roadmap-state.json found in ..." |
| State file unreadable (JSON) | 1 | commands | "Could not read state file: ..." |
| `spec_file` key absent in state | 1 | commands | "State file missing 'spec_file' key." |
| Spec file missing from disk | 1 | commands | "Spec file not found: ..." |
| Hash current (idempotent) | 0 | commands | "Spec hash is already current. Nothing to do." |
| Zero matching records | 1 | commands | Long guidance message (FR-4) |
| YAML parse failure per-file | warning | spec_patch | "[roadmap] WARNING: Could not parse frontmatter in ..." |
| User declined prompt | 0 | commands | "Aborted." |
| Non-interactive, no auto_accept | 0 | spec_patch | "Aborted." |
| Atomic write failure (commands) | 1 | commands | "Failed to update state file: ..." |
| Atomic write failure (auto-resume) | — | executor | "[roadmap] ERROR: Failed to update spec_hash ..." → fall through |
| Cycle suppressed by guard | — | executor | "[roadmap] Spec-patch cycle already exhausted ..." |

---

## 7. Type Contracts

### `spec_patch.py` public surface

```python
# Inputs / outputs, fully typed

def scan_accepted_deviation_records(
    output_dir: Path,
    *,
    require_disposition: str = "ACCEPTED",
    require_spec_update: bool = True,
) -> list[DeviationRecord]: ...

def update_spec_hash(
    state_file: Path,
    new_hash: str,          # 64-char sha256 hex
    *,
    old_hash: str,          # 64-char sha256 hex (for display only)
) -> None: ...              # raises OSError on write failure

def prompt_accept_spec_change(
    records: list[DeviationRecord],
    *,
    auto_accept: bool,
    old_hash: str,
    new_hash: str,
) -> bool: ...
```

### `executor.py` public surface (unchanged except signature)

```python
def execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
    auto_accept: bool = False,   # NEW — default=False preserves AC-10
) -> None: ...
```

### `executor.py` private additions (not exported)

```python
def _apply_resume_after_spec_patch(
    config: RoadmapConfig,
    results: list[StepResult],
    initial_spec_hash: str,
    spec_patch_cycle_count: int,
    auto_accept: bool,
) -> list[StepResult] | None: ...   # None = cycle did not fire

def _find_qualifying_deviation_files(
    output_dir: Path,
    spec_fidelity_started_at: str,  # ISO 8601
) -> list[Path]: ...
```

---

## 8. State Machine: `_spec_patch_cycle_count`

```
State: int (local to execute_roadmap() invocation)

Initial: 0

Transitions:
  0 ──[spec-fidelity FAIL, all 3 conditions met, cycle fires]──► 1
  0 ──[any condition false, cycle does not fire]──────────────► 0 (stays)
  1 ──[second spec-fidelity FAIL detected]────────────────────► 1 (guard blocks)

Terminal states:
  0: normal pipeline completion (no auto-resume needed)
  1: one cycle fired; any subsequent failure surfaces normally

Per-invocation: this counter is NOT a module-level variable.
Each call to execute_roadmap() creates a fresh local int = 0.
```

---

## 9. Test Architecture

### `tests/roadmap/test_accept_spec_change.py` — unit tests

Covers AC-1 through AC-5 and AC-11. All tests use `tmp_path` fixtures.
No subprocess invocation; `spec_patch` functions tested directly and via CLI runner.

```python
# Test groups:

class TestLocateStateFile:          # FR-1: AC-1 precondition
class TestRecomputeHash:            # FR-2
class TestHashMismatchCheck:        # FR-3, AC-3 (idempotency)
class TestScanDeviationRecords:     # FR-4, AC-1
    test_zero_files_exits_1()
    test_empty_frontmatter_skips_with_warning()
    test_string_true_does_not_match()   # YAML type guard
    test_bool_true_matches()
    test_disposition_case_insensitive()
    test_parse_error_warns_and_continues()
    test_all_parse_errors_triggers_zero_path()
class TestPromptBehavior:           # FR-5, AC-4, AC-11
    test_non_interactive_aborts_without_prompt()
    test_y_confirms()
    test_Y_confirms()
    test_yes_does_not_confirm()     # input normalization
    test_empty_does_not_confirm()
class TestAtomicWrite:              # FR-6, AC-2
    test_only_spec_hash_modified()
    test_all_other_keys_preserved()
    test_tmp_overwritten_if_exists()
class TestConfirmationOutput:       # FR-7
    test_both_hashes_truncated_12_chars()
class TestIdempotency:              # AC-3
    test_second_run_exits_0()
```

### `tests/roadmap/test_spec_patch_cycle.py` — integration-level unit tests

Covers AC-6 through AC-10. Uses mocking for `execute_pipeline()` and disk state.

```python
class TestCycleGuard:               # FR-11, AC-6
    test_cycle_fires_at_most_once()
    test_second_failure_surfaces_normally()
class TestDiskReread:               # FR-10, AC-7
    test_apply_resume_uses_post_write_state()
    test_pre_write_state_not_used()
class TestConditionChecks:          # FR-9
    test_all_three_conditions_required()
    test_mtime_strict_greater_than()
    test_mtime_type_conversion()    # ISO str → float
    test_initial_hash_not_state_hash()  # Condition 3 uses local var
class TestAutoAccept:               # FR-8, AC-9
    test_auto_accept_true_skips_prompt()
    test_auto_accept_false_prompts()
class TestBackwardCompat:           # AC-10
    test_execute_roadmap_default_signature()
class TestCycleExhaustion:          # FR-13, AC-8
    test_second_fidelity_fail_exits_1_no_loop()
class TestWriteFailure:             # FR-10 Step 3 failure path
    test_write_failure_falls_through_to_normal_failure()
```

---

## 10. Integration Points with Existing Code

| Existing symbol | Change | Location |
|---|---|---|
| `execute_roadmap()` | Add `auto_accept: bool = False` param; add `initial_spec_hash` local; add `_spec_patch_cycle_count` local; add post-failure cycle check | `executor.py:822` |
| `_save_state()` | No change — called unchanged before and within cycle | `executor.py:567` |
| `_apply_resume()` | No change to function itself — called with post-write state | `executor.py:1055` |
| `_build_steps()` | No change — called within cycle at Step 5 | `executor.py:302` |
| `_format_halt_output()` | No change — called with post-resume results | `executor.py:437` |
| `read_state()` / `write_state()` | Not used by `spec_patch.py` — spec_patch uses raw json + os.replace directly to avoid importing executor | `executor.py:784,794` |
| `roadmap_group` | New `accept-spec-change` subcommand added | `commands.py:12` |
| `commands.py` imports | Add lazy import of `spec_patch` inside command function | `commands.py` |

**Why `spec_patch.py` does NOT use `read_state()`/`write_state()` from executor**:
Importing from `executor.py` would create an `executor → spec_patch → executor` cycle
risk in the future. `spec_patch` is a leaf module. It reimplements the 3-line
`os.replace` pattern inline, which is acceptable duplication for cycle prevention.

---

## 11. Files to Create/Modify (Implementation Checklist)

| File | Action | Key changes |
|---|---|---|
| `src/superclaude/cli/roadmap/spec_patch.py` | CREATE | Full new module per §2 |
| `src/superclaude/cli/roadmap/executor.py` | MODIFY | §3.1–3.4: signature, initial_spec_hash, cycle_count, _apply_resume_after_spec_patch, _find_qualifying_deviation_files |
| `src/superclaude/cli/roadmap/commands.py` | MODIFY | §4.1: accept_spec_change() command |
| `tests/roadmap/test_accept_spec_change.py` | CREATE | §9 test groups |
| `tests/roadmap/test_spec_patch_cycle.py` | CREATE | §9 test groups |
