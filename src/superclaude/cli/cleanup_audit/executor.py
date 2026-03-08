"""Sprint-style supervised executor for Cleanup Audit pipeline.

Controls the execution loop with:
- Per-step live monitoring
- TUI refresh at ~2Hz
- Stall detection and watchdog
- Signal-aware graceful shutdown
- Deterministic status classification
- Failure diagnostics

IMPORTANT: Use synchronous execution with threading, NOT async/await.
Uses time.sleep() polling loops and concurrent.futures.ThreadPoolExecutor
for parallel batch dispatch. Do not use asyncio.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import GateMode

from .config import load_cleanup_audit_config
from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator
from .gates import ALL_GATES
from .logging_ import CleanupAuditLogger
from .models import (
    AuditPassType,
    CleanupAuditConfig,
    CleanupAuditMonitorState,
    CleanupAuditOutcome,
    CleanupAuditResult,
    CleanupAuditStatus,
    CleanupAuditStep,
    CleanupAuditStepResult,
)
from .monitor import OutputMonitor, detect_error_max_turns
from .process import CleanupAuditProcess, SignalHandler
from .prompts import (
    build_consolidation_prompt,
    build_cross_cutting_prompt,
    build_structural_analysis_prompt,
    build_surface_scan_prompt,
    build_validation_prompt,
)
from .tui import CleanupAuditTUI


def execute_cleanup_audit(config: CleanupAuditConfig) -> CleanupAuditResult:
    """Execute the Cleanup Audit pipeline with supervised monitoring."""

    # Pre-flight
    if not shutil.which("claude"):
        print("Error: 'claude' binary not found in PATH", file=sys.stderr)
        sys.exit(1)

    # Setup infrastructure
    handler = SignalHandler()
    handler.install()
    logger = CleanupAuditLogger(config)
    tui = CleanupAuditTUI(config)
    monitor = OutputMonitor(config.work_dir / "placeholder.jsonl")
    result = CleanupAuditResult(config=config)

    logger.write_header()
    tui.start()

    try:
        for step in _build_steps(config):
            if handler.shutdown_requested:
                result.outcome = CleanupAuditOutcome.INTERRUPTED
                break

            # Reset monitor for this step's output
            output_path = config.work_dir / step.output_file
            monitor.reset(output_path)
            monitor.start()

            # Launch subprocess
            process = CleanupAuditProcess(config, step)
            logger.write_step_start(step)
            deadline = time.monotonic() + step.timeout_seconds
            process.start()

            # Supervision loop
            while process.is_running():
                if handler.shutdown_requested:
                    process.stop()
                    break

                if time.monotonic() > deadline:
                    process.stop()
                    break

                state = monitor.get_state()

                # Stall watchdog
                if (
                    config.stall_timeout
                    and state.stall_seconds > config.stall_timeout
                    and state.events_received > 0
                ):
                    if config.stall_action == "kill":
                        process.stop()
                        break

                try:
                    tui.update(step, state)
                except Exception:
                    pass

                time.sleep(0.5)

            # Classify result
            exit_code = process.wait()
            monitor.stop()
            status = _determine_status(exit_code, step, config)

            step_result = CleanupAuditStepResult(
                step=step,
                status=status,
                exit_code=exit_code,
                started_at=process.started_at,
                finished_at=time.time(),
                output_bytes=monitor.state.output_bytes,
            )
            result.step_results.append(step_result)
            logger.write_step_result(step_result)

            # Gate check for passing steps
            if status == CleanupAuditStatus.PASS and step.gate:
                output_file = config.work_dir / step.output_file
                if output_file.exists():
                    passed, reason = gate_passed(output_file, step.gate)
                    if not passed:
                        step_result.status = CleanupAuditStatus.HALT
                        step_result.gate_failure_reason = reason
                        status = CleanupAuditStatus.HALT

            # Handle failures
            if status not in (
                CleanupAuditStatus.PASS,
                CleanupAuditStatus.PASS_NO_SIGNAL,
                CleanupAuditStatus.PASS_NO_REPORT,
            ):
                collector = DiagnosticCollector(config)
                bundle = collector.collect(step_result, monitor.state)
                classifier = FailureClassifier()
                category = classifier.classify(bundle)
                bundle.category = category
                reporter = ReportGenerator()
                reporter.write(bundle, config)

                result.outcome = CleanupAuditOutcome.HALTED
                result.halt_step = step.id
                break

        # Finalize
        if result.outcome == CleanupAuditOutcome.SUCCESS:
            all_passed = all(
                r.status
                in (
                    CleanupAuditStatus.PASS,
                    CleanupAuditStatus.PASS_NO_SIGNAL,
                    CleanupAuditStatus.PASS_NO_REPORT,
                    CleanupAuditStatus.SKIPPED,
                )
                for r in result.step_results
            )
            if not all_passed:
                result.outcome = CleanupAuditOutcome.ERROR

        result.finished_at = time.time()
        logger.write_summary(result)

    finally:
        tui.stop()
        monitor.stop()
        handler.restore()

    return result


def _build_steps(config: CleanupAuditConfig) -> list[CleanupAuditStep]:
    """Build the step graph for the cleanup audit pipeline."""
    steps: list[CleanupAuditStep] = []

    # Step G-001: Surface scan
    steps.append(
        CleanupAuditStep(
            id="G-001",
            prompt=build_surface_scan_prompt(config, []),
            output_file=Path("surface-scan-result.md"),
            gate=ALL_GATES["G-001"],
            timeout_seconds=600,
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.SURFACE,
            agent_type="audit-scanner",
        )
    )

    # Step G-002: Structural analysis
    steps.append(
        CleanupAuditStep(
            id="G-002",
            prompt=build_structural_analysis_prompt(config, [], "surface-scan-result.md"),
            output_file=Path("structural-analysis-result.md"),
            gate=ALL_GATES["G-002"],
            timeout_seconds=900,
            inputs=[Path("surface-scan-result.md")],
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.STRUCTURAL,
            agent_type="audit-analyzer",
        )
    )

    # Step G-003: Per-file profiling (parallel with G-002 output)
    steps.append(
        CleanupAuditStep(
            id="G-003",
            prompt=build_structural_analysis_prompt(config, [], "surface-scan-result.md"),
            output_file=Path("per-file-profiles-result.md"),
            gate=ALL_GATES["G-003"],
            timeout_seconds=900,
            inputs=[Path("surface-scan-result.md")],
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.STRUCTURAL,
            agent_type="audit-analyzer",
        )
    )

    # Step G-004: Cross-cutting analysis
    steps.append(
        CleanupAuditStep(
            id="G-004",
            prompt=build_cross_cutting_prompt(config, "structural-analysis-result.md"),
            output_file=Path("cross-cutting-result.md"),
            gate=ALL_GATES["G-004"],
            timeout_seconds=900,
            inputs=[
                Path("structural-analysis-result.md"),
                Path("per-file-profiles-result.md"),
            ],
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.CROSS_CUTTING,
            agent_type="audit-comparator",
        )
    )

    # Step G-005: Consolidation and summary
    steps.append(
        CleanupAuditStep(
            id="G-005",
            prompt=build_consolidation_prompt(config, "cross-cutting-result.md"),
            output_file=Path("consolidation-result.md"),
            gate=ALL_GATES["G-005"],
            timeout_seconds=600,
            inputs=[Path("cross-cutting-result.md")],
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.CONSOLIDATION,
            agent_type="audit-consolidator",
        )
    )

    # Step G-006: Validation
    steps.append(
        CleanupAuditStep(
            id="G-006",
            prompt=build_validation_prompt(config, "consolidation-result.md"),
            output_file=Path("validation-result.md"),
            gate=ALL_GATES["G-006"],
            timeout_seconds=600,
            inputs=[Path("consolidation-result.md")],
            gate_mode=GateMode.BLOCKING,
            pass_type=AuditPassType.VALIDATION,
            agent_type="audit-validator",
        )
    )

    return steps


def _determine_status(
    exit_code: int | None,
    step: CleanupAuditStep,
    config: CleanupAuditConfig,
) -> CleanupAuditStatus:
    """Classify step outcome from exit code and output artifacts."""
    if exit_code == 124:
        return CleanupAuditStatus.TIMEOUT
    if exit_code and exit_code != 0:
        return CleanupAuditStatus.ERROR

    result_path = config.work_dir / f"{step.id}-result.md"
    output_path = config.work_dir / step.output_file

    if result_path.exists():
        content = result_path.read_text()
        if "EXIT_RECOMMENDATION: HALT" in content:
            return CleanupAuditStatus.HALT
        if "EXIT_RECOMMENDATION: CONTINUE" in content:
            return CleanupAuditStatus.PASS
        if "status: PASS" in content.lower():
            return CleanupAuditStatus.PASS
        if "status: FAIL" in content.lower():
            return CleanupAuditStatus.HALT
        return CleanupAuditStatus.PASS_NO_SIGNAL

    if output_path.exists():
        if detect_error_max_turns(output_path):
            return CleanupAuditStatus.INCOMPLETE
        return CleanupAuditStatus.PASS_NO_REPORT

    return CleanupAuditStatus.ERROR
