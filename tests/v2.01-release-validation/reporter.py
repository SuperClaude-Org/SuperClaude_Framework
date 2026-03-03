"""
v2.01 Release Validation — Report Generator

Aggregates results from all runs/models/tests and produces a comprehensive report.
"""

import statistics
from collections import defaultdict


def generate_report(
    all_results: list[dict], models: list[str], num_runs: int
) -> str:
    """Generate the aggregate validation report."""
    lines = []

    # --- Header ---
    total = len(all_results)
    structural = [r for r in all_results if r.get("test_type") == "structural"]
    classification = [r for r in all_results if r.get("test_type") == "classification"]
    wiring = [r for r in all_results if r.get("test_type") == "wiring"]
    behavioral = classification + wiring
    errors = [r for r in all_results if "error" in r]

    lines.append("=" * 70)
    lines.append("  v2.01 Release Validation Report")
    lines.append("=" * 70)
    lines.append(f"  Runs:          {num_runs}")
    lines.append(f"  Models:        {', '.join(models)}")
    lines.append(f"  Data points:   {total} ({len(structural)} structural + {len(behavioral)} behavioral)")
    if errors:
        lines.append(f"  Errors:        {len(errors)}")
    lines.append("")

    # --- Structural Results ---
    lines.append("STRUCTURAL TESTS")
    lines.append("-" * 70)
    structural_by_id = defaultdict(list)
    for r in structural:
        structural_by_id[r["test_id"]].append(r.get("score", 0))

    for test_id in sorted(structural_by_id.keys()):
        scores = structural_by_id[test_id]
        mean = statistics.mean(scores) if scores else 0
        passed = sum(1 for s in scores if s >= 0.8)
        bar = _bar(mean)
        name = _test_name(test_id)
        lines.append(f"  {test_id} {name:<25s} {passed}/{len(scores)}  {bar}  {mean*100:.0f}%")

    structural_mean = (
        statistics.mean(r.get("score", 0) for r in structural) if structural else 0
    )
    lines.append(f"\n  Structural aggregate: {structural_mean*100:.1f}%")
    lines.append("")

    # --- Classification Results by Model ---
    lines.append("TIER CLASSIFICATION — By Model")
    lines.append("-" * 70)

    # Header row
    header = f"  {'':6s}"
    for model in models:
        header += f"  {model:>12s}"
    header += f"  {'Mean':>8s}"
    lines.append(header)

    classification_by_id = defaultdict(lambda: defaultdict(list))
    for r in classification:
        classification_by_id[r["test_id"]][r.get("model", "unknown")].append(
            r.get("score", 0)
        )

    for test_id in sorted(classification_by_id.keys()):
        row = f"  {test_id:6s}"
        all_scores = []
        for model in models:
            scores = classification_by_id[test_id].get(model, [])
            if scores:
                m = statistics.mean(scores)
                s = statistics.stdev(scores) if len(scores) > 1 else 0
                row += f"  {m:.2f}\u00b1{s:.2f}  "
                all_scores.extend(scores)
            else:
                row += f"  {'N/A':>12s}"
        if all_scores:
            row += f"  {statistics.mean(all_scores):.2f}"
        lines.append(row)

    classification_mean = (
        statistics.mean(r.get("score", 0) for r in classification)
        if classification
        else 0
    )
    lines.append(f"\n  Classification aggregate: {classification_mean*100:.1f}%")
    lines.append("")

    # --- Wiring Results by Model ---
    lines.append("SKILL WIRING — By Model")
    lines.append("-" * 70)
    lines.append(header)  # Reuse model header

    wiring_by_id = defaultdict(lambda: defaultdict(list))
    for r in wiring:
        wiring_by_id[r["test_id"]][r.get("model", "unknown")].append(
            r.get("score", 0)
        )

    for test_id in sorted(wiring_by_id.keys()):
        row = f"  {test_id:6s}"
        all_scores = []
        for model in models:
            scores = wiring_by_id[test_id].get(model, [])
            if scores:
                m = statistics.mean(scores)
                s = statistics.stdev(scores) if len(scores) > 1 else 0
                row += f"  {m:.2f}\u00b1{s:.2f}  "
                all_scores.extend(scores)
            else:
                row += f"  {'N/A':>12s}"
        if all_scores:
            row += f"  {statistics.mean(all_scores):.2f}"
        lines.append(row)

    wiring_mean = (
        statistics.mean(r.get("score", 0) for r in wiring) if wiring else 0
    )
    lines.append(f"\n  Wiring aggregate: {wiring_mean*100:.1f}%")
    lines.append("")

    # --- Model Comparison ---
    lines.append("MODEL COMPARISON")
    lines.append("-" * 70)

    for model in models:
        model_results = [
            r for r in behavioral if r.get("model") == model
        ]
        if not model_results:
            lines.append(f"  {model:>8s}:  No results")
            continue

        scores = [r.get("score", 0) for r in model_results]
        m = statistics.mean(scores)
        s = statistics.stdev(scores) if len(scores) > 1 else 0
        mn = min(scores)
        mx = max(scores)
        lines.append(
            f"  {model:>8s}:  Mean {m*100:.1f}%  Std {s*100:.1f}%  "
            f"Min {mn*100:.0f}%  Max {mx*100:.0f}%"
        )

    behavioral_mean = (
        statistics.mean(r.get("score", 0) for r in behavioral) if behavioral else 0
    )
    lines.append("")

    # --- Per-Run Breakdown ---
    lines.append("PER-RUN BREAKDOWN")
    lines.append("-" * 70)

    for run in range(1, num_runs + 1):
        run_results = [r for r in all_results if r.get("run") == run]
        if not run_results:
            continue
        run_score = statistics.mean(r.get("score", 0) for r in run_results)
        run_struct = [r for r in run_results if r.get("test_type") == "structural"]
        run_behav = [r for r in run_results if r.get("test_type") in ("classification", "wiring")]

        struct_score = statistics.mean(r.get("score", 0) for r in run_struct) if run_struct else 0
        behav_score = statistics.mean(r.get("score", 0) for r in run_behav) if run_behav else 0

        lines.append(
            f"  Run {run}: {run_score*100:.1f}% overall  "
            f"(structural: {struct_score*100:.0f}%, behavioral: {behav_score*100:.1f}%)"
        )

    lines.append("")

    # --- Verdict ---
    lines.append("AGGREGATE VERDICT")
    lines.append("=" * 70)

    overall_mean = statistics.mean(r.get("score", 0) for r in all_results) if all_results else 0

    # Model-specific behavioral scores
    model_behavioral_means = {}
    for model in models:
        model_scores = [
            r.get("score", 0) for r in behavioral if r.get("model") == model
        ]
        model_behavioral_means[model] = (
            statistics.mean(model_scores) if model_scores else 0
        )

    best_model = max(model_behavioral_means, key=model_behavioral_means.get) if model_behavioral_means else "N/A"
    best_model_score = model_behavioral_means.get(best_model, 0)

    # Cross-model std
    if len(model_behavioral_means) > 1:
        cross_model_std = statistics.stdev(model_behavioral_means.values())
    else:
        cross_model_std = 0

    # Per-test minimums
    test_minimums = {}
    for r in all_results:
        tid = r.get("test_id", "?")
        score = r.get("score", 0)
        if tid not in test_minimums or score < test_minimums[tid]:
            test_minimums[tid] = score
    worst_test_min = min(test_minimums.values()) if test_minimums else 0

    lines.append(f"  Overall mean:         {overall_mean*100:.1f}%")
    lines.append(f"  Structural:           {structural_mean*100:.1f}%")
    lines.append(f"  Behavioral mean:      {behavioral_mean*100:.1f}%")
    lines.append(f"  Best model:           {best_model} ({best_model_score*100:.1f}%)")
    lines.append(f"  Cross-model std:      {cross_model_std*100:.1f}%")
    lines.append(f"  Worst per-test min:   {worst_test_min*100:.0f}%")
    lines.append("")

    # Threshold checks
    thresholds = [
        ("Structural = 100%", structural_mean >= 1.0),
        ("Behavioral (any model) >= 80%", any(v >= 0.80 for v in model_behavioral_means.values())),
        ("Behavioral (best model) >= 90%", best_model_score >= 0.90),
        ("Cross-model std <= 15%", cross_model_std <= 0.15),
        ("Per-test minimum >= 50%", worst_test_min >= 0.50),
    ]

    all_passed = True
    for label, passed in thresholds:
        status = "PASS" if passed else "FAIL"
        icon = "  \u2705" if passed else "  \u274c"
        lines.append(f"{icon} {label}: {status}")
        if not passed:
            all_passed = False

    lines.append("")
    if all_passed:
        lines.append("  VERDICT: RELEASE APPROVED \u2705")
    else:
        lines.append("  VERDICT: RELEASE NOT APPROVED \u274c")
        lines.append("  Review failing thresholds above and address issues.")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def _bar(ratio: float, width: int = 20) -> str:
    """Generate a text progress bar."""
    filled = int(ratio * width)
    empty = width - filled
    return "\u2588" * filled + "\u2591" * empty


def _test_name(test_id: str) -> str:
    """Map test ID to human name."""
    names = {
        "S1": "lint-architecture",
        "S2": "verify-sync",
        "S3": "stale-references",
        "S4": "task-unified-size",
        "S5": "frontmatter",
        "B1": "STRICT-detection",
        "B2": "EXEMPT-detection",
        "B3": "LIGHT-detection",
        "B4": "STANDARD-detection",
        "W1": "task-wiring",
        "W2": "adversarial-wiring",
        "W3": "validate-wiring",
        "W4": "roadmap-wiring",
    }
    return names.get(test_id, test_id)
