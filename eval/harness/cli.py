"""Entry point: run the head-to-head eval and print a verdict table.

    uv run sc-eval --trials 5 --k 3
    uv run sc-eval --arms B_confidence --tasks fix-null-deref

Every (task, arm, trial) writes one line to results/<run>.jsonl. Verdicts are
computed per arm against the `A` baseline using stats.verdict.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from collections import defaultdict
from pathlib import Path

from .config import DEFAULT_MODEL, DEFAULT_TRIALS, Arm, Task, TrialResult
from .load import load_arms, load_tasks
from .runner import prepare_workdir, run_agent
from .scoring import verify
from .stats import ArmSummary, summarize_arm, verdict

EVAL_ROOT = Path(__file__).resolve().parent.parent


def _usage_ints(data: dict) -> tuple[int, int, float, int, int]:
    usage = data.get("usage", {}) or {}
    inp = int(usage.get("input_tokens", 0))
    out = int(usage.get("output_tokens", 0))
    cost = float(data.get("total_cost_usd", 0.0) or 0.0)
    dur = int(data.get("duration_ms", 0) or 0)
    turns = int(data.get("num_turns", 0) or 0)
    return inp, out, cost, dur, turns


def run_trial(task: Task, arm: Arm, trial: int, model: str) -> TrialResult:
    workdir = prepare_workdir(task)
    try:
        data = run_agent(task, arm, workdir, model=model)
        is_error = bool(data.get("is_error"))
        passed, tail = (False, "agent error") if is_error else verify(task, workdir)
        inp, out, cost, dur, turns = _usage_ints(data)
        note = ""
        if data.get("_timed_out"):
            note = "agent timeout"
        elif data.get("_parse_error"):
            note = "parse error"
        elif not passed:
            note = tail[-300:]
        return TrialResult(task.id, arm.name, trial, passed, is_error,
                           inp, out, cost, dur, turns, note)
    finally:
        shutil.rmtree(workdir.parent, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(prog="sc-eval")
    ap.add_argument("--tasks-dir", type=Path, default=EVAL_ROOT / "tasks")
    ap.add_argument("--variants-dir", type=Path, default=EVAL_ROOT / "variants")
    ap.add_argument("--out-dir", type=Path, default=EVAL_ROOT / "results")
    ap.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    ap.add_argument("--k", type=int, default=3, help="k for pass@k")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--arms", nargs="*", help="restrict to these arm/comp names")
    ap.add_argument("--tasks", nargs="*", help="restrict to these task ids")
    args = ap.parse_args()

    tasks = load_tasks(args.tasks_dir, set(args.tasks) if args.tasks else None)
    arms = load_arms(args.variants_dir, set(args.arms) if args.arms else None)
    if not tasks:
        raise SystemExit(f"no tasks under {args.tasks_dir}")
    print(f"tasks={[t.id for t in tasks]} arms={[a.name for a in arms]} "
          f"trials={args.trials} model={args.model}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d-%H%M%S")
    out_path = args.out_dir / f"{run_id}.jsonl"
    results: list[TrialResult] = []
    with out_path.open("w") as fh:
        for task in tasks:
            for arm in arms:
                for trial in range(args.trials):
                    r = run_trial(task, arm, trial, args.model)
                    results.append(r)
                    fh.write(json.dumps(r.as_dict()) + "\n")
                    fh.flush()
                    print(f"  {task.id:24} {arm.name:16} t{trial} "
                          f"{'PASS' if r.passed else 'fail'} "
                          f"out={r.output_tokens} ${r.cost_usd:.3f} {r.notes[:40]}")

    _report(results, args.k, out_path)


def _report(results: list[TrialResult], k: int, out_path: Path) -> None:
    by_arm: dict[str, list[TrialResult]] = defaultdict(list)
    for r in results:
        by_arm[r.arm].append(r)
    summaries: dict[str, ArmSummary] = {
        arm: summarize_arm(rs, k) for arm, rs in by_arm.items()
    }
    base = summaries.get("A")
    print(f"\n=== summary ({out_path.name}) ===")
    print(f"{'arm':16} {'pass':>6} {'CI':>15} {'p@1':>5} {'p@k':>5} "
          f"{'out_tok':>8} {'q/1k':>6} verdict")
    for arm in sorted(summaries):
        s = summaries[arm]
        v = "" if arm == "A" or base is None else verdict(base, s)
        print(f"{arm:16} {s.pass_rate:6.2f} "
              f"[{s.pass_ci[0]:.2f},{s.pass_ci[1]:.2f}] "
              f"{s.pass_at_1:5.2f} {s.pass_at_k:5.2f} "
              f"{s.mean_output_tokens:8.0f} {s.quality_per_1k_tokens:6.2f} {v}")


if __name__ == "__main__":
    main()
