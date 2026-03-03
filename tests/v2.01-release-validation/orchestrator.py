#!/usr/bin/env python3
"""
v2.01 Release Validation — Orchestrator

Runs 5 parallel teams, each executing 29 tests (5 structural + 3 models × 8 behavioral).
Produces 145 data points and an aggregate report.

Usage:
    uv run python tests/v2.01-release-validation/orchestrator.py
    uv run python tests/v2.01-release-validation/orchestrator.py --runs 3
    uv run python tests/v2.01-release-validation/orchestrator.py --models sonnet,opus
    uv run python tests/v2.01-release-validation/orchestrator.py --concurrency 15
"""

import asyncio
import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from runner import run_structural_test, run_behavioral_test
from scorer import score_classification, score_wiring, score_structural
from reporter import generate_report

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = Path(__file__).parent / "results"
MODELS = ["haiku", "sonnet", "opus"]

# Test definitions
STRUCTURAL_TESTS = [
    {"id": "S1", "name": "lint-architecture", "sc": "SC-004"},
    {"id": "S2", "name": "verify-sync", "sc": "SC-005"},
    {"id": "S3", "name": "stale-references", "sc": "SC-009"},
    {"id": "S4", "name": "task-unified-size", "sc": "SC-010"},
    {"id": "S5", "name": "frontmatter-completeness", "sc": "SC-003"},
]

CLASSIFICATION_TESTS = [
    {
        "id": "B1",
        "prompt": "fix security vulnerability in auth module",
        "expected_tier": "STRICT",
        "sc": "SC-007",
        "max_turns": 5,
    },
    {
        "id": "B2",
        "prompt": "explain how the routing middleware works",
        "expected_tier": "EXEMPT",
        "sc": "SC-007",
        "max_turns": 5,
    },
    {
        "id": "B3",
        "prompt": "fix typo in error message",
        "expected_tier": "LIGHT",
        "sc": "SC-007",
        "max_turns": 5,
    },
    {
        "id": "B4",
        "prompt": "add pagination to user list endpoint",
        "expected_tier": "STANDARD",
        "sc": "SC-007",
        "max_turns": 5,
    },
]

WIRING_TESTS = [
    {
        "id": "W1",
        "command": '/sc:task "implement JWT authentication system"',
        "expected_protocol": "sc:task-unified-protocol",
        "detection_patterns": [
            r"SC:TASK-UNIFIED:CLASSIFICATION",
            r"TIER:",
            r"task-unified-protocol",
        ],
        "sc": "SC-002",
        "max_turns": 8,
    },
    {
        "id": "W2",
        "command": None,  # Special: needs temp files, built at runtime
        "expected_protocol": "sc:adversarial-protocol",
        "detection_patterns": [
            r"adversarial-protocol",
            r"[Ss]tep 1|[Dd]iff [Aa]nalysis|Mode [AB]",
            r"compare|variant",
        ],
        "sc": "SC-002",
        "max_turns": 6,
    },
    {
        "id": "W3",
        "command": "/sc:validate-tests --all --summary",
        "expected_protocol": "sc:validate-tests-protocol",
        "detection_patterns": [
            r"validate-tests-protocol",
            r"[Ll]oad|[Tt]est [Ss]pec|classification",
            r"YAML|test file",
        ],
        "sc": "SC-002",
        "max_turns": 8,
    },
    {
        "id": "W4",
        "command": f"/sc:roadmap @{REPO_ROOT}/.dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md",
        "expected_protocol": "sc:roadmap-protocol",
        "detection_patterns": [
            r"roadmap-protocol",
            r"[Ww]ave 0|[Ss]pec.*[Ll]oad|roadmap gen",
            r"specification|spec file",
        ],
        "sc": "SC-002",
        "max_turns": 10,
    },
]


async def run_team(
    run_number: int,
    models: list[str],
    claude_semaphore: asyncio.Semaphore,
    structural_semaphore: asyncio.Semaphore,
    concurrency: int = 1,
) -> list[dict]:
    """Run a complete test team (1 of 5 parallel teams)."""
    results = []
    run_dir = RESULTS_DIR / f"run_{run_number}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # --- Structural tests (parallel, no model dependency) ---
    structural_tasks = []
    for test in STRUCTURAL_TESTS:
        structural_tasks.append(
            run_structural_with_semaphore(
                test, run_number, run_dir, structural_semaphore
            )
        )

    # --- Behavioral tests (parallel across models and test IDs) ---
    behavioral_tasks = []
    for model in models:
        # Classification tests
        for test in CLASSIFICATION_TESTS:
            behavioral_tasks.append(
                run_classification_with_semaphore(
                    test, model, run_number, run_dir, claude_semaphore, concurrency
                )
            )
        # Wiring tests
        for test in WIRING_TESTS:
            behavioral_tasks.append(
                run_wiring_with_semaphore(
                    test, model, run_number, run_dir, claude_semaphore, concurrency
                )
            )

    # Run all tests for this team in parallel
    all_tasks = structural_tasks + behavioral_tasks
    all_results = await asyncio.gather(*all_tasks, return_exceptions=True)

    for r in all_results:
        if isinstance(r, Exception):
            results.append(
                {
                    "error": str(r),
                    "score": 0.0,
                    "run": run_number,
                }
            )
        else:
            results.append(r)

    return results


async def run_structural_with_semaphore(
    test: dict, run_number: int, run_dir: Path, sem: asyncio.Semaphore
) -> dict:
    """Run a structural test with semaphore control."""
    async with sem:
        start = time.monotonic()
        output, exit_code = await run_structural_test(test["id"], REPO_ROOT)
        duration_ms = int((time.monotonic() - start) * 1000)

        scores = score_structural(test["id"], output, exit_code)

        result = {
            "test_id": test["id"],
            "test_name": test["name"],
            "test_type": "structural",
            "sc": test["sc"],
            "run": run_number,
            "model": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "scores": scores,
            "score": scores["weighted_total"],
        }

        # Save result
        result_path = run_dir / f"{test['id']}_result.json"
        result_path.write_text(json.dumps(result, indent=2))

        # Save raw output
        output_path = run_dir / f"{test['id']}_output.txt"
        output_path.write_text(output)

        return result


async def run_classification_with_semaphore(
    test: dict,
    model: str,
    run_number: int,
    run_dir: Path,
    sem: asyncio.Semaphore,
    concurrency: int = 1,
) -> dict:
    """Run a classification behavioral test with semaphore control."""
    async with sem:
        prompt = f'/sc:task "{test["prompt"]}"'
        start = time.monotonic()
        output, exit_code = await run_behavioral_test(
            prompt, model, max_turns=test.get("max_turns", 5), repo_root=REPO_ROOT,
            concurrency=concurrency,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        scores = score_classification(output, test["expected_tier"])

        result = {
            "test_id": test["id"],
            "test_type": "classification",
            "sc": test["sc"],
            "run": run_number,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "prompt": test["prompt"],
            "expected_tier": test["expected_tier"],
            "actual": scores.get("parsed", {}),
            "scores": scores,
            "score": scores["weighted_total"],
        }

        result_path = run_dir / f"{test['id']}_{model}_result.json"
        result_path.write_text(json.dumps(result, indent=2))

        output_path = run_dir / f"{test['id']}_{model}_output.txt"
        output_path.write_text(output)

        return result


async def run_wiring_with_semaphore(
    test: dict,
    model: str,
    run_number: int,
    run_dir: Path,
    sem: asyncio.Semaphore,
    concurrency: int = 1,
) -> dict:
    """Run a wiring behavioral test with semaphore control."""
    async with sem:
        command = test["command"]

        # W2 special case: create temp files for adversarial comparison
        tmpdir = None
        if test["id"] == "W2":
            import tempfile

            tmpdir = tempfile.mkdtemp(prefix="v201_w2_")
            Path(tmpdir, "a.md").write_text(
                "# Draft A\n\n## Approach\nMicroservices architecture with event-driven communication.\n"
            )
            Path(tmpdir, "b.md").write_text(
                "# Draft B\n\n## Approach\nMonolith-first with modular boundaries.\n"
            )
            command = f'/sc:adversarial --compare {tmpdir}/a.md,{tmpdir}/b.md --depth quick'

        start = time.monotonic()
        output, exit_code = await run_behavioral_test(
            command,
            model,
            max_turns=test.get("max_turns", 5),
            repo_root=REPO_ROOT,
            extra_dirs=[tmpdir] if tmpdir else None,
            concurrency=concurrency,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        # Cleanup temp files
        if tmpdir:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)

        scores = score_wiring(output, test["detection_patterns"])

        result = {
            "test_id": test["id"],
            "test_type": "wiring",
            "sc": test["sc"],
            "run": run_number,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "command": command,
            "expected_protocol": test["expected_protocol"],
            "scores": scores,
            "score": scores["weighted_total"],
        }

        result_path = run_dir / f"{test['id']}_{model}_result.json"
        result_path.write_text(json.dumps(result, indent=2))

        output_path = run_dir / f"{test['id']}_{model}_output.txt"
        output_path.write_text(output)

        return result


async def main():
    parser = argparse.ArgumentParser(description="v2.01 Release Validation Orchestrator")
    parser.add_argument("--runs", type=int, default=5, help="Number of parallel runs (default: 5)")
    parser.add_argument(
        "--models",
        type=str,
        default="haiku,sonnet,opus",
        help="Comma-separated models (default: haiku,sonnet,opus)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent claude -p processes (default: 10)",
    )
    parser.add_argument(
        "--structural-concurrency",
        type=int,
        default=25,
        help="Max concurrent structural tests (default: 25)",
    )
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",")]
    num_runs = args.runs

    # Calculate expected data points
    structural_points = num_runs * len(STRUCTURAL_TESTS)
    behavioral_points = num_runs * len(models) * (
        len(CLASSIFICATION_TESTS) + len(WIRING_TESTS)
    )
    total_points = structural_points + behavioral_points

    print(f"╔═══════════════════════════════════════════════════════════════╗")
    print(f"║           v2.01 Release Validation Orchestrator              ║")
    print(f"╚═══════════════════════════════════════════════════════════════╝")
    print(f"  Runs:          {num_runs}")
    print(f"  Models:        {', '.join(models)}")
    print(f"  Concurrency:   {args.concurrency} claude -p / {args.structural_concurrency} structural")
    print(f"  Data points:   {total_points} ({structural_points} structural + {behavioral_points} behavioral)")
    print(f"  Results dir:   {RESULTS_DIR}")
    print()

    # Clean previous results
    if RESULTS_DIR.exists():
        import shutil

        shutil.rmtree(RESULTS_DIR)
    RESULTS_DIR.mkdir(parents=True)

    # Semaphores
    claude_sem = asyncio.Semaphore(args.concurrency)
    structural_sem = asyncio.Semaphore(args.structural_concurrency)

    # Launch all teams in parallel
    print(f"Launching {num_runs} parallel teams...")
    start = time.monotonic()

    team_tasks = [
        run_team(run_num, models, claude_sem, structural_sem, concurrency=args.concurrency)
        for run_num in range(1, num_runs + 1)
    ]
    team_results = await asyncio.gather(*team_tasks, return_exceptions=True)

    total_duration = time.monotonic() - start

    # Flatten results
    all_results = []
    for i, team_result in enumerate(team_results):
        if isinstance(team_result, Exception):
            print(f"  Team {i + 1}: ERROR — {team_result}")
        else:
            all_results.extend(team_result)
            passed = sum(1 for r in team_result if r.get("score", 0) >= 0.8)
            print(f"  Team {i + 1}: {passed}/{len(team_result)} tests scored ≥0.8")

    print(f"\nTotal duration: {total_duration:.1f}s")
    print(f"Results collected: {len(all_results)}/{total_points}")

    # Save all results
    all_results_path = RESULTS_DIR / "all_results.json"
    all_results_path.write_text(json.dumps(all_results, indent=2))

    # Generate report
    report = generate_report(all_results, models, num_runs)
    report_path = RESULTS_DIR / "aggregate_report.md"
    report_path.write_text(report)

    print(f"\nReport written to: {report_path}")
    print()
    # Print summary to stdout
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
