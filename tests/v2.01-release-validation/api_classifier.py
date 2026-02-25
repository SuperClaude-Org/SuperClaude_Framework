#!/usr/bin/env python3
"""
S5: API-based Classification Correctness Tests

Validates tier classification logic via direct Anthropic API calls,
bypassing claude -p subprocess infrastructure. Complementary to
the main orchestrator.py harness -- tests classification logic
correctness, NOT Claude Code integration.

This eliminates 5 confirmed failure modes of the claude -p approach:
  CF-3 nesting, CF-1 turn exhaustion, CF-2 concurrency amplification,
  RC-3 startup overhead, T-9 slash command interpretation.

Usage:
    uv run python tests/v2.01-release-validation/api_classifier.py
    uv run python tests/v2.01-release-validation/api_classifier.py --models haiku
    uv run python tests/v2.01-release-validation/api_classifier.py --models haiku,sonnet
    uv run python tests/v2.01-release-validation/api_classifier.py --models haiku,sonnet,opus
    uv run python tests/v2.01-release-validation/api_classifier.py --parallel
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency guard: anthropic package
# ---------------------------------------------------------------------------
try:
    import anthropic
except ImportError:
    print(
        "ERROR: The 'anthropic' package is not installed.\n"
        "Install it with:\n\n"
        "    uv pip install anthropic\n"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Scorer import (reuse existing scoring engine)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from scorer import score_classification  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_FILE = REPO_ROOT / "src" / "superclaude" / "commands" / "task-unified.md"
RESULTS_DIR = Path(__file__).parent / "results"

MODEL_IDS: dict[str, str] = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}

CLASSIFICATION_TESTS: list[dict] = [
    {
        "id": "B1",
        "prompt": "fix security vulnerability in auth module",
        "expected_tier": "STRICT",
    },
    {
        "id": "B2",
        "prompt": "explain how the routing middleware works",
        "expected_tier": "EXEMPT",
    },
    {
        "id": "B3",
        "prompt": "fix typo in error message",
        "expected_tier": "LIGHT",
    },
    {
        "id": "B4",
        "prompt": "add pagination to user list endpoint",
        "expected_tier": "STANDARD",
    },
]

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0  # seconds
API_TIMEOUT = 30.0  # seconds per call


# ---------------------------------------------------------------------------
# System prompt loader
# ---------------------------------------------------------------------------
def load_system_prompt() -> str:
    """Read the task-unified.md command file to use as the system prompt."""
    if not COMMAND_FILE.exists():
        print(f"ERROR: Command file not found at {COMMAND_FILE}")
        print("Ensure you are running from the repository root.")
        sys.exit(1)
    return COMMAND_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Single API classification call
# ---------------------------------------------------------------------------
async def run_api_classification(
    test: dict,
    model_id: str,
    system_prompt: str,
    client: anthropic.AsyncAnthropic,
) -> tuple[str, float]:
    """Run a single classification test via the Anthropic API.

    Returns:
        (output_text, elapsed_seconds)

    Raises after MAX_RETRIES exhausted.
    """
    user_message = (
        f'You are executing the /sc:task command. Follow the system prompt instructions EXACTLY.\n'
        f'Classify this task and emit the classification header as your FIRST output:\n\n'
        f'{test["prompt"]}'
    )

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.monotonic()
            response = await asyncio.wait_for(
                client.messages.create(
                    model=model_id,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                ),
                timeout=API_TIMEOUT,
            )
            elapsed = time.monotonic() - start

            # Extract text from response content blocks
            output_text = ""
            for block in response.content:
                if block.type == "text":
                    output_text += block.text

            return output_text, elapsed

        except anthropic.RateLimitError as exc:
            last_error = exc
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            print(
                f"    Rate limited on {test['id']} (attempt {attempt}/{MAX_RETRIES}), "
                f"retrying in {delay:.0f}s..."
            )
            await asyncio.sleep(delay)

        except asyncio.TimeoutError:
            last_error = TimeoutError(
                f"API call timed out after {API_TIMEOUT}s"
            )
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            print(
                f"    Timeout on {test['id']} (attempt {attempt}/{MAX_RETRIES}), "
                f"retrying in {delay:.0f}s..."
            )
            await asyncio.sleep(delay)

        except anthropic.APIError as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                print(
                    f"    API error on {test['id']} (attempt {attempt}/{MAX_RETRIES}): "
                    f"{exc}, retrying in {delay:.0f}s..."
                )
                await asyncio.sleep(delay)

    raise RuntimeError(
        f"Failed after {MAX_RETRIES} attempts for {test['id']}: {last_error}"
    )


# ---------------------------------------------------------------------------
# Run all tests for a single model
# ---------------------------------------------------------------------------
async def run_model_tests(
    model_short: str,
    system_prompt: str,
    client: anthropic.AsyncAnthropic,
    sequential: bool = True,
) -> list[dict]:
    """Run all classification tests for one model.

    Args:
        model_short: Short model name (haiku, sonnet, opus).
        system_prompt: Content of task-unified.md.
        client: Async Anthropic client.
        sequential: If True, run tests sequentially to avoid rate limits.

    Returns:
        List of result dicts.
    """
    model_id = MODEL_IDS[model_short]
    results = []

    if sequential:
        for test in CLASSIFICATION_TESTS:
            result = await _run_single_test(
                test, model_short, model_id, system_prompt, client
            )
            results.append(result)
    else:
        tasks = [
            _run_single_test(test, model_short, model_id, system_prompt, client)
            for test in CLASSIFICATION_TESTS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        results = list(results)

    return results


async def _run_single_test(
    test: dict,
    model_short: str,
    model_id: str,
    system_prompt: str,
    client: anthropic.AsyncAnthropic,
) -> dict:
    """Execute one test case and score the result."""
    try:
        output_text, elapsed = await run_api_classification(
            test, model_id, system_prompt, client
        )
        scores = score_classification(output_text, test["expected_tier"])
        error = None
    except Exception as exc:
        output_text = ""
        elapsed = 0.0
        scores = {
            "header_present": 0.0,
            "tier_correct": 0.0,
            "confidence_adequate": 0.0,
            "keywords_relevant": 0.0,
            "weighted_total": 0.0,
            "parsed": {},
        }
        error = str(exc)

    tier_from_scores = ""
    parsed = scores.get("parsed", {})
    if isinstance(parsed, dict) and parsed.get("tier"):
        tier_from_scores = parsed["tier"]

    result = {
        "test_id": test["id"],
        "test_type": "api_classification",
        "model": model_short,
        "model_id": model_id,
        "prompt": test["prompt"],
        "expected_tier": test["expected_tier"],
        "actual_tier": tier_from_scores,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_s": round(elapsed, 2),
        "scores": scores,
        "score": scores["weighted_total"],
        "pass": scores["weighted_total"] >= 0.80,
        "output_text": output_text,
        "error": error,
    }

    # Print progress indicator
    status = "PASS" if result["pass"] else "FAIL"
    tier_display = tier_from_scores or "(no header)"
    print(
        f"    {test['id']} [{model_short}] "
        f"expected={test['expected_tier']:8s} "
        f"actual={tier_display:8s} "
        f"score={scores['weighted_total']:.2f} "
        f"[{status}] "
        f"({elapsed:.1f}s)"
    )
    if error:
        print(f"      ERROR: {error}")

    return result


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def print_summary_table(all_results: list[dict], models: list[str]) -> None:
    """Print a formatted summary table to stdout."""
    print()
    print("=" * 78)
    print("  S5 API Classification Results Summary")
    print("=" * 78)

    # Header row
    header = f"  {'Test':4s} {'Expected':10s}"
    for m in models:
        header += f" | {m:>18s}"
    print(header)
    print("  " + "-" * (16 + len(models) * 21))

    # Group results by test_id
    by_test: dict[str, dict[str, dict]] = {}
    for r in all_results:
        tid = r["test_id"]
        model = r["model"]
        if tid not in by_test:
            by_test[tid] = {}
        by_test[tid][model] = r

    # Data rows
    for test in CLASSIFICATION_TESTS:
        tid = test["id"]
        row = f"  {tid:4s} {test['expected_tier']:10s}"
        for m in models:
            r = by_test.get(tid, {}).get(m)
            if r is None:
                row += f" | {'--':>18s}"
            else:
                tier = r.get("actual_tier") or "?"
                score = r["score"]
                status = "PASS" if r["pass"] else "FAIL"
                row += f" | {tier:>6s} {score:.2f} {status:>4s}"
        print(row)

    # Totals row
    print("  " + "-" * (16 + len(models) * 21))
    totals_row = f"  {'':4s} {'TOTAL':10s}"
    for m in models:
        model_results = [r for r in all_results if r["model"] == m]
        if model_results:
            avg_score = sum(r["score"] for r in model_results) / len(model_results)
            pass_count = sum(1 for r in model_results if r["pass"])
            totals_row += f" | {pass_count}/{len(model_results)} avg={avg_score:.2f}"
        else:
            totals_row += f" | {'--':>18s}"
    print(totals_row)
    print("=" * 78)

    # Overall pass rate
    total_pass = sum(1 for r in all_results if r["pass"])
    total_tests = len(all_results)
    print(
        f"\n  Overall: {total_pass}/{total_tests} passed "
        f"({100 * total_pass / total_tests:.0f}%)" if total_tests else ""
    )
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main() -> None:
    parser = argparse.ArgumentParser(
        description="S5: API-based Classification Correctness Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run python api_classifier.py\n"
            "  uv run python api_classifier.py --models haiku\n"
            "  uv run python api_classifier.py --models haiku,sonnet,opus --parallel\n"
        ),
    )
    parser.add_argument(
        "--models",
        type=str,
        default="haiku",
        help="Comma-separated model short names (default: haiku). Options: haiku, sonnet, opus",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Run tests within each model in parallel (may trigger rate limits)",
    )
    args = parser.parse_args()

    # Validate API credentials — support both standard key and proxy auth
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if not api_key:
        print(
            "ERROR: No Anthropic API credentials found.\n"
            "Set one of:\n\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
            "    export ANTHROPIC_AUTH_TOKEN=cli-...\n"
        )
        sys.exit(1)

    # Parse and validate models
    models = [m.strip() for m in args.models.split(",")]
    for m in models:
        if m not in MODEL_IDS:
            print(
                f"ERROR: Unknown model '{m}'. "
                f"Valid options: {', '.join(MODEL_IDS.keys())}"
            )
            sys.exit(1)

    # Load system prompt
    system_prompt = load_system_prompt()
    prompt_size = len(system_prompt)

    print("=" * 62)
    print("  S5: API-based Classification Correctness Tests")
    print("=" * 62)
    print(f"  Models:        {', '.join(models)}")
    print(f"  Tests:         {len(CLASSIFICATION_TESTS)} classification cases")
    print(f"  System prompt: {COMMAND_FILE.name} ({prompt_size:,} chars)")
    print(f"  Parallel:      {args.parallel}")
    print(f"  Max retries:   {MAX_RETRIES}")
    print(f"  Timeout:       {API_TIMEOUT}s per call")
    print()

    # Initialize async client — use proxy base_url and auth token if available
    client_kwargs = {}
    if base_url:
        client_kwargs["base_url"] = base_url
    if api_key:
        client_kwargs["api_key"] = api_key
    client = anthropic.AsyncAnthropic(**client_kwargs)

    all_results: list[dict] = []
    total_start = time.monotonic()

    for model_short in models:
        model_id = MODEL_IDS[model_short]
        print(f"  Model: {model_short} ({model_id})")
        print(f"  {'─' * 56}")

        model_results = await run_model_tests(
            model_short,
            system_prompt,
            client,
            sequential=not args.parallel,
        )
        all_results.extend(model_results)
        print()

    total_duration = time.monotonic() - total_start
    print(f"  Total duration: {total_duration:.1f}s")

    # Print summary
    print_summary_table(all_results, models)

    # Save results JSON (strip raw output to keep file manageable)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / "api_classification_results.json"

    # Build saveable results (without full output_text in the aggregate)
    saveable = []
    for r in all_results:
        entry = {k: v for k, v in r.items() if k != "output_text"}
        # Truncate output for the JSON (keep first 500 chars for debugging)
        entry["output_preview"] = (r.get("output_text") or "")[:500]
        saveable.append(entry)

    results_payload = {
        "test_suite": "S5_api_classification",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_s": round(total_duration, 2),
        "models": models,
        "system_prompt_file": str(COMMAND_FILE),
        "system_prompt_chars": prompt_size,
        "results": saveable,
        "summary": {
            "total_tests": len(all_results),
            "total_pass": sum(1 for r in all_results if r["pass"]),
            "pass_rate": (
                sum(1 for r in all_results if r["pass"]) / len(all_results)
                if all_results
                else 0.0
            ),
            "avg_score": (
                sum(r["score"] for r in all_results) / len(all_results)
                if all_results
                else 0.0
            ),
            "per_model": {
                m: {
                    "tests": len([r for r in all_results if r["model"] == m]),
                    "pass": len(
                        [r for r in all_results if r["model"] == m and r["pass"]]
                    ),
                    "avg_score": round(
                        (
                            sum(
                                r["score"]
                                for r in all_results
                                if r["model"] == m
                            )
                            / len([r for r in all_results if r["model"] == m])
                        )
                        if [r for r in all_results if r["model"] == m]
                        else 0.0,
                        3,
                    ),
                }
                for m in models
            },
        },
    }

    results_path.write_text(json.dumps(results_payload, indent=2))
    print(f"  Results saved to: {results_path}")

    # Also save per-test raw outputs for debugging
    for r in all_results:
        output_path = (
            RESULTS_DIR
            / f"api_{r['test_id']}_{r['model']}_output.txt"
        )
        output_path.write_text(r.get("output_text", ""))

    print(f"  Raw outputs saved to: {RESULTS_DIR}/api_*_output.txt")
    print()


if __name__ == "__main__":
    asyncio.run(main())
