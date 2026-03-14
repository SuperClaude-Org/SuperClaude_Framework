"""Spec-patch reconciliation module for accepted deviations.

Leaf module: imports ONLY stdlib + PyYAML. No reverse imports from
executor.py or commands.py. No subprocess invocations.

Provides the ``accept-spec-change`` workflow:
  1. Locate .roadmap-state.json
  2. Recompute spec hash
  3. Check for hash mismatch
  4. Scan for accepted deviation records
  5. Display evidence summary and prompt
  6. Update spec_hash atomically
  7. Print confirmation

YAML boolean coercion contract:
  YAML 1.1 boolean forms (yes, on, 1, True, TRUE) are intentionally
  accepted for spec_update_required. The string "true" (quoted in YAML)
  is NOT accepted — PyYAML safe_load returns str, not bool, for quoted values.

Single-writer assumption:
  This module assumes exclusive write access to .roadmap-state.json
  during execution. No file locking is implemented. The operator is
  responsible for preventing concurrent access.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class DeviationRecord:
    """Parsed and validated accepted deviation record.

    Invariants:
    - disposition is always stored uppercase after normalization
    - spec_update_required is always a Python bool (never str)
    - mtime is a Unix timestamp float, captured once at scan time
    """

    id: str
    disposition: str  # normalized to uppercase
    spec_update_required: bool  # YAML boolean only (True/False, yes/no, on/off)
    affects_spec_sections: list[str]  # may be empty list
    acceptance_rationale: str  # may be empty string
    source_file: Path  # absolute path to the .md file
    mtime: float  # os.path.getmtime() at scan time


def scan_accepted_deviation_records(output_dir: Path) -> list[DeviationRecord]:
    """Glob for dev-*-accepted-deviation.md and parse YAML frontmatter.

    Returns only records where:
      - disposition: ACCEPTED (case-insensitive string match)
      - spec_update_required: true (YAML boolean, NOT the string "true")

    Malformed files are warned and skipped (never crash the pipeline).
    """
    pattern = str(output_dir / "dev-*-accepted-deviation.md")
    files = sorted(glob.glob(pattern))
    records: list[DeviationRecord] = []

    for filepath in files:
        path = Path(filepath)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"[roadmap] WARNING: Could not read {path.name}: {exc}. Skipping.",
                file=sys.stderr,
                flush=True,
            )
            continue

        # Extract YAML frontmatter between --- delimiters
        frontmatter = _extract_frontmatter(text)
        if frontmatter is None:
            print(
                f"[roadmap] WARNING: Could not parse frontmatter in {path.name}. Skipping.",
                file=sys.stderr,
                flush=True,
            )
            continue

        try:
            data = yaml.safe_load(frontmatter)
        except yaml.YAMLError:
            print(
                f"[roadmap] WARNING: Could not parse frontmatter in {path.name}. Skipping.",
                file=sys.stderr,
                flush=True,
            )
            continue

        if not isinstance(data, dict):
            print(
                f"[roadmap] WARNING: Could not parse frontmatter in {path.name}. Skipping.",
                file=sys.stderr,
                flush=True,
            )
            continue

        # Check disposition: must be ACCEPTED (case-insensitive)
        disposition = data.get("disposition", "")
        if not isinstance(disposition, str):
            continue
        if disposition.upper() != "ACCEPTED":
            continue

        # Check spec_update_required: must be YAML boolean true, NOT string "true"
        spec_update_required = data.get("spec_update_required", False)
        if not isinstance(spec_update_required, bool):
            continue
        if not spec_update_required:
            continue

        # Build record
        mtime = os.path.getmtime(filepath)
        record = DeviationRecord(
            id=str(data.get("id", path.stem)),
            disposition=disposition.upper(),
            spec_update_required=True,
            affects_spec_sections=data.get("affects_spec_sections", []) or [],
            acceptance_rationale=str(data.get("acceptance_rationale", "")),
            source_file=path.resolve(),
            mtime=mtime,
        )
        records.append(record)

    return records


def update_spec_hash(state_path: Path, new_hash: str) -> None:
    """Atomically update only spec_hash in state file.

    Uses .tmp + os.replace() for atomic write on POSIX.
    All other keys are preserved verbatim.

    Raises OSError on write failure (caller must handle).
    """
    text = state_path.read_text(encoding="utf-8")
    state = json.loads(text)
    state["spec_hash"] = new_hash
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(state_path))


def prompt_accept_spec_change(
    output_dir: Path, auto_accept: bool = False
) -> int:
    """Interactive spec-change acceptance workflow.

    Returns:
        0 on success or idempotent no-op
        1 on error (missing files, no evidence, etc.)
    """
    state_path = output_dir / ".roadmap-state.json"

    # FR-2.24.1.1: Locate state file
    if not state_path.exists():
        print(
            f"No .roadmap-state.json found in {output_dir}. "
            "Run `roadmap run` first.",
            file=sys.stderr,
        )
        return 1

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(
            f"No .roadmap-state.json found in {output_dir}. "
            f"Run `roadmap run` first. ({exc})",
            file=sys.stderr,
        )
        return 1

    # FR-2.24.1.2: Recompute current spec hash
    spec_file_str = state.get("spec_file", "")
    if not spec_file_str:
        print("State file has no spec_file entry.", file=sys.stderr)
        return 1

    spec_file = Path(spec_file_str)
    if not spec_file.exists():
        print(f"Spec file not found: {spec_file}", file=sys.stderr)
        return 1

    current_hash = hashlib.sha256(spec_file.read_bytes()).hexdigest()

    # FR-2.24.1.3: Check for hash mismatch
    saved_hash = state.get("spec_hash")
    if saved_hash and current_hash == saved_hash:
        print("Spec hash is already current. Nothing to do.")
        return 0

    old_hash = saved_hash or "(none)"

    # FR-2.24.1.4: Scan for accepted deviation evidence
    records = scan_accepted_deviation_records(output_dir)

    if not records:
        print(
            f"Spec file has changed but no accepted deviation records with "
            f"spec_update_required: true were found in {output_dir}. "
            f"If this is a functional spec change, run `roadmap run` without "
            f"--resume. If it is a documentation sync, create a "
            f"dev-NNN-accepted-deviation.md record with "
            f"spec_update_required: true before running this command.",
            file=sys.stderr,
        )
        return 1

    # FR-2.24.1.5: Display evidence summary and prompt
    print(
        f"Spec file changed. Found {len(records)} accepted deviation "
        f"record(s) with spec_update_required: true:\n"
    )
    for rec in records:
        sections = ", ".join(rec.affects_spec_sections) if rec.affects_spec_sections else "(none)"
        print(f"  {rec.id}  affects_spec_sections: {sections}")
        if rec.acceptance_rationale:
            print(f"           acceptance_rationale: {rec.acceptance_rationale}")
    print(
        "\nUpdating spec_hash in .roadmap-state.json will allow "
        "--resume to skip the full cascade."
    )

    if auto_accept:
        confirmed = True
    elif not sys.stdin.isatty():
        # Non-interactive: fail-safe
        print("Aborted.")
        return 0
    else:
        try:
            answer = input("Accept this spec change as a documentation sync? [y/N]: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return 0
        confirmed = answer.strip() in ("y", "Y")

    if not confirmed:
        print("Aborted.")
        return 0

    # FR-2.24.1.6: Update spec_hash atomically
    try:
        update_spec_hash(state_path, current_hash)
    except OSError as exc:
        print(
            f"[roadmap] ERROR: Failed to update spec_hash: {exc}",
            file=sys.stderr,
        )
        return 1

    # FR-2.24.1.7: Confirmation output
    deviation_ids = ", ".join(rec.id for rec in records)
    print(f"[roadmap] spec_hash updated.")
    print(f"  Old: {old_hash[:12]}...")
    print(f"  New: {current_hash[:12]}...")
    print(f"  Accepted deviations: {deviation_ids}")
    print(
        f"Run `superclaude roadmap run <spec_file> --resume` to continue "
        f"from the failing step."
    )
    return 0


def _extract_frontmatter(text: str) -> str | None:
    """Extract YAML frontmatter from markdown text.

    Returns the YAML content between the first pair of --- delimiters,
    or None if no valid frontmatter is found.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    return "\n".join(lines[1:end_idx])
