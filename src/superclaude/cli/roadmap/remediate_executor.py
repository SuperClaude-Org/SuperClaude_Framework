"""Remediation executor -- orchestrates parallel agent execution with rollback.

Provides:
- create_snapshots(target_files) -> list[str]  (T04.03)
- EDITABLE_FILES constant and enforce_allowlist(findings)  (T04.04)
- execute_remediation(file_groups, config) -> dict  (T04.05)
- Timeout/retry wrapper  (T04.06)
- Failure handler with full rollback  (T04.07)
- Success handler with snapshot cleanup  (T04.08)
- update_remediation_tasklist(tasklist_path, findings)  (T04.09)
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..pipeline.models import PipelineConfig
from ..pipeline.process import ClaudeProcess
from .models import Finding
from .remediate_prompts import build_remediation_prompt

_log = logging.getLogger("superclaude.roadmap.remediate_executor")

# T04.04: File allowlist per spec section 2.3.5
EDITABLE_FILES = frozenset({"roadmap.md", "extraction.md", "test-strategy.md"})

# T04.06: Timeout per agent (seconds) per NFR-001
_AGENT_TIMEOUT_SECONDS = 300

# T04.06: Retry limit per NFR-002
_AGENT_RETRY_LIMIT = 1

# Inline embedding size limit (mirrors executor.py; --file is broken per Phase 1)
_MAX_ARG_STRLEN = 128 * 1024
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD


# ═══════════════════════════════════════════════════════════════
# T04.03 -- Pre-Remediate File Snapshots
# ═══════════════════════════════════════════════════════════════


def create_snapshots(target_files: list[str]) -> list[str]:
    """Create .pre-remediate snapshot copies for all target files.

    Uses atomic copy pattern: read -> write to tmp -> os.replace() per NFR-005.
    Returns list of snapshot paths for rollback reference.

    Raises FileNotFoundError if a target file does not exist.
    """
    snapshot_paths: list[str] = []
    for file_path in target_files:
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"Target file not found: {file_path}")

        snapshot = Path(f"{file_path}.pre-remediate")
        tmp = Path(f"{file_path}.pre-remediate.tmp")

        # Atomic copy: read -> tmp -> os.replace
        content = src.read_bytes()
        tmp.write_bytes(content)
        os.replace(str(tmp), str(snapshot))

        snapshot_paths.append(str(snapshot))
        _log.info("Snapshot created: %s -> %s", file_path, snapshot)

    return snapshot_paths


def restore_from_snapshots(target_files: list[str]) -> None:
    """Restore all target files from their .pre-remediate snapshots.

    Uses os.replace() for atomicity per NFR-005.
    """
    for file_path in target_files:
        snapshot = Path(f"{file_path}.pre-remediate")
        if snapshot.exists():
            os.replace(str(snapshot), str(file_path))
            _log.info("Restored: %s from snapshot", file_path)
        else:
            _log.warning("Snapshot not found for %s, cannot restore", file_path)


def cleanup_snapshots(target_files: list[str]) -> None:
    """Delete .pre-remediate snapshots after successful remediation."""
    for file_path in target_files:
        snapshot = Path(f"{file_path}.pre-remediate")
        if snapshot.exists():
            snapshot.unlink()
            _log.info("Snapshot cleaned up: %s", snapshot)


# ═══════════════════════════════════════════════════════════════
# T04.04 -- File Allowlist Enforcement
# ═══════════════════════════════════════════════════════════════


def enforce_allowlist(
    findings: list[Finding],
) -> tuple[list[Finding], list[Finding]]:
    """Enforce file allowlist on findings.

    Findings with ALL files_affected in EDITABLE_FILES pass through.
    Findings with ANY file outside EDITABLE_FILES are SKIPPED with WARNING.

    Returns (allowed, rejected) tuple.

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    allowed: list[Finding] = []
    rejected: list[Finding] = []

    for finding in findings:
        if not finding.files_affected:
            _log.warning(
                "Finding %s has no files_affected, SKIPPING",
                finding.id,
            )
            rejected.append(finding)
            continue

        # Check if any file is outside the allowlist
        non_allowed = [
            f for f in finding.files_affected
            if _basename(f) not in EDITABLE_FILES
        ]

        if non_allowed:
            _log.warning(
                "Finding %s references non-allowlisted files: %s -- SKIPPING",
                finding.id,
                ", ".join(non_allowed),
            )
            rejected.append(finding)
        else:
            allowed.append(finding)

    return allowed, rejected


def _basename(path: str) -> str:
    """Extract basename from a path, handling both absolute and relative paths."""
    return Path(path).name


# ═══════════════════════════════════════════════════════════════
# T04.05 -- Parallel Agent Execution with ClaudeProcess
# ═══════════════════════════════════════════════════════════════


def _run_agent_for_file(
    target_file: str,
    findings: list[Finding],
    config: PipelineConfig,
    output_dir: Path,
) -> tuple[str, int]:
    """Spawn a ClaudeProcess for a single file group.

    Returns (target_file, exit_code) tuple.
    """
    base_prompt = build_remediation_prompt(target_file, findings)

    # Inline embedding: read target file content into the prompt.
    # --file is broken (cloud download mechanism, not local file injector).
    try:
        file_content = Path(target_file).read_text(encoding="utf-8")
        file_block = f"## Current File Content\n\n```\n{file_content}\n```"
        composed = base_prompt + "\n\n" + file_block
        if len(composed.encode("utf-8")) > _EMBED_SIZE_LIMIT:
            _log.warning(
                "remediate_executor: composed prompt for '%s' exceeds %d bytes;"
                " embedding inline anyway (--file fallback is unavailable)",
                target_file,
                _EMBED_SIZE_LIMIT,
            )
        prompt = composed
    except OSError as exc:
        _log.warning("remediate_executor: could not read '%s': %s; using base prompt", target_file, exc)
        prompt = base_prompt

    output_file = output_dir / f"remediate-{Path(target_file).stem}.md"
    error_file = output_file.with_suffix(".err")

    proc = ClaudeProcess(
        prompt=prompt,
        output_file=output_file,
        error_file=error_file,
        max_turns=config.max_turns,
        model=config.model,
        permission_flag=config.permission_flag,
        timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        output_format="text",
    )

    proc.start()
    exit_code = proc.wait()
    return target_file, exit_code


def _run_agent_with_retry(
    target_file: str,
    findings: list[Finding],
    config: PipelineConfig,
    output_dir: Path,
    all_target_files: list[str],
) -> tuple[str, int, int]:
    """Run agent with single retry on failure per NFR-002.

    On first failure, restores snapshot and retries once.
    Returns (target_file, exit_code, attempt_count).
    """
    # Attempt 1
    target, exit_code = _run_agent_for_file(
        target_file, findings, config, output_dir
    )

    if exit_code == 0:
        return target, exit_code, 1

    _log.warning(
        "Agent for %s failed (exit %d), restoring snapshot and retrying",
        target_file,
        exit_code,
    )

    # Restore snapshot before retry
    snapshot = Path(f"{target_file}.pre-remediate")
    if snapshot.exists():
        os.replace(str(snapshot), str(target_file))
        # Re-create snapshot for the retry
        content = Path(target_file).read_bytes()
        tmp = Path(f"{target_file}.pre-remediate.tmp")
        tmp.write_bytes(content)
        os.replace(str(tmp), str(snapshot))

    # Attempt 2
    target, exit_code = _run_agent_for_file(
        target_file, findings, config, output_dir
    )

    return target, exit_code, 2


# ═══════════════════════════════════════════════════════════════
# T04.07 -- Failure Handling with Full Rollback
# ═══════════════════════════════════════════════════════════════


def _handle_failure(
    failed_file: str,
    all_target_files: list[str],
    findings_by_file: dict[str, list[Finding]],
    executor: ThreadPoolExecutor | None = None,
) -> list[Finding]:
    """Handle agent failure: rollback ALL files, mark findings FAILED.

    Spec section 2.3.8 five-step procedure:
    1. Halt remaining agents (via executor shutdown)
    2. Rollback ALL target files from .pre-remediate snapshots
    3. Mark all findings for failed agent as FAILED
    4. Mark cross-file findings involving failed file as FAILED
    5. Set remediate step to FAIL

    Returns list of all findings with updated statuses.
    """
    # Step 1: Halt remaining agents
    if executor is not None:
        executor.shutdown(wait=False, cancel_futures=True)

    # Step 2: Rollback ALL target files
    restore_from_snapshots(all_target_files)
    _log.info("Rolled back all %d target files", len(all_target_files))

    # Steps 3-4: Mark findings as FAILED
    all_findings: list[Finding] = []
    for file_path, file_findings in findings_by_file.items():
        for finding in file_findings:
            if finding.id not in {f.id for f in all_findings}:
                # Check if this finding involves the failed file
                if failed_file in finding.files_affected or file_path == failed_file:
                    finding.status = "FAILED"
                all_findings.append(finding)

    return all_findings


# ═══════════════════════════════════════════════════════════════
# T04.08 -- Success Handling with Snapshot Cleanup
# ═══════════════════════════════════════════════════════════════


def _handle_success(
    all_target_files: list[str],
    findings_by_file: dict[str, list[Finding]],
) -> list[Finding]:
    """Handle full success: delete snapshots, mark findings FIXED.

    Only runs when ALL agents succeed (not partial).
    SKIPPED findings remain in SKIPPED status.

    Returns list of all findings with updated statuses.
    """
    # Delete snapshots
    cleanup_snapshots(all_target_files)

    # Mark all agent-targeted findings as FIXED (preserve SKIPPED)
    all_findings: list[Finding] = []
    seen_ids: set[str] = set()
    for file_findings in findings_by_file.values():
        for finding in file_findings:
            if finding.id not in seen_ids:
                seen_ids.add(finding.id)
                if finding.status == "PENDING":
                    finding.status = "FIXED"
                # SKIPPED findings stay SKIPPED
                all_findings.append(finding)

    return all_findings


# ═══════════════════════════════════════════════════════════════
# T04.09 -- Tasklist Outcome Writer (Two-Write Model)
# ═══════════════════════════════════════════════════════════════


def update_remediation_tasklist(
    tasklist_path: str,
    findings: list[Finding],
) -> None:
    """Update existing remediation-tasklist.md with per-finding outcomes.

    This is the second write of the two-write model (first write in T03.04).
    Updates finding statuses and checkboxes, writes back atomically.

    Uses atomic write (tmp + os.replace) per NFR-005.
    """
    path = Path(tasklist_path)
    content = path.read_text(encoding="utf-8")

    # Build status lookup
    status_map: dict[str, str] = {f.id: f.status for f in findings}

    # Update frontmatter counts
    content = _update_frontmatter_counts(content, findings)

    # Update finding entries
    content = _update_finding_entries(content, status_map)

    # Atomic write
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(str(tmp), str(path))

    _log.info("Updated remediation tasklist: %s", tasklist_path)


def _update_frontmatter_counts(content: str, findings: list[Finding]) -> str:
    """Update YAML frontmatter counts based on final statuses."""
    actionable = sum(1 for f in findings if f.status in ("FIXED", "FAILED", "PENDING"))
    skipped = sum(1 for f in findings if f.status == "SKIPPED")

    content = re.sub(
        r"^actionable: \d+",
        f"actionable: {actionable}",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^skipped: \d+",
        f"skipped: {skipped}",
        content,
        flags=re.MULTILINE,
    )
    return content


def _update_finding_entries(content: str, status_map: dict[str, str]) -> str:
    """Update checklist entries with final statuses."""
    for finding_id, status in status_map.items():
        if status == "FIXED":
            # Change - [ ] F-XX | file | STATUS to - [x] F-XX | file | FIXED
            content = re.sub(
                rf"^(- )\[ \]( {re.escape(finding_id)} \|[^|]*\|)\s*\w+(\s*--)",
                rf"\1[x]\2 FIXED\3",
                content,
                flags=re.MULTILINE,
            )
        elif status == "FAILED":
            # Keep - [ ] but update status to FAILED
            content = re.sub(
                rf"^(- \[ \] {re.escape(finding_id)} \|[^|]*\|)\s*\w+(\s*--)",
                rf"\1 FAILED\2",
                content,
                flags=re.MULTILINE,
            )
        # SKIPPED entries already have [x] from T03.04, leave unchanged

    return content


# ═══════════════════════════════════════════════════════════════
# T04.05 + T04.07 + T04.08 -- Main Execution Coordinator
# ═══════════════════════════════════════════════════════════════


def execute_remediation(
    findings_by_file: dict[str, list[Finding]],
    config: PipelineConfig,
    output_dir: Path,
) -> tuple[str, list[Finding]]:
    """Execute remediation agents in parallel across file groups.

    Orchestrates:
    1. Create snapshots (T04.03)
    2. Spawn parallel agents (T04.05) with timeout/retry (T04.06)
    3. On any failure: full rollback (T04.07), return ("FAIL", findings)
    4. On full success: cleanup snapshots (T04.08), return ("PASS", findings)

    Returns (status, findings) where status is "PASS" or "FAIL".
    """
    all_target_files = list(findings_by_file.keys())

    # Step 1: Create snapshots
    create_snapshots(all_target_files)

    # Step 2: Spawn parallel agents
    results: dict[str, tuple[int, int]] = {}  # file -> (exit_code, attempts)

    with ThreadPoolExecutor(max_workers=len(all_target_files)) as executor:
        futures = {}
        for target_file, file_findings in findings_by_file.items():
            future = executor.submit(
                _run_agent_with_retry,
                target_file,
                file_findings,
                config,
                output_dir,
                all_target_files,
            )
            futures[future] = target_file

        for future in as_completed(futures):
            target_file = futures[future]
            try:
                file_path, exit_code, attempts = future.result()
                results[file_path] = (exit_code, attempts)

                if exit_code != 0:
                    # Step 3: Failure -- rollback ALL files
                    _log.error(
                        "Agent for %s failed after %d attempt(s), triggering rollback",
                        file_path,
                        attempts,
                    )
                    failed_findings = _handle_failure(
                        file_path,
                        all_target_files,
                        findings_by_file,
                        executor,
                    )
                    return "FAIL", failed_findings

            except Exception as exc:
                _log.error("Agent for %s raised exception: %s", target_file, exc)
                failed_findings = _handle_failure(
                    target_file,
                    all_target_files,
                    findings_by_file,
                    executor,
                )
                return "FAIL", failed_findings

    # Step 4: All agents succeeded
    success_findings = _handle_success(all_target_files, findings_by_file)
    return "PASS", success_findings
