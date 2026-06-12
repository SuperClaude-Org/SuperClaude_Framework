"""Smoke-test the harness plumbing WITHOUT spending claude tokens.

Checks: task discovery, docker-based verify (oracle must pass, buggy env must
fail), and the stats/verdict math. Run: `uv run python scripts/smoke_plumbing.py`
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from harness.config import TrialResult  # noqa: E402
from harness.load import load_arms, load_tasks  # noqa: E402
from harness.scoring import verify  # noqa: E402
from harness.stats import summarize_arm, verdict  # noqa: E402

ok = True


def check(label: str, cond: bool) -> None:
    global ok
    ok = ok and cond
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")


# 1. discovery
tasks = load_tasks(ROOT / "tasks")
check("load_tasks finds fix-sum-bug", any(t.id == "fix-sum-bug" for t in tasks))
arms = load_arms(ROOT / "variants")
check("load_arms always includes baseline A", arms[0].name == "A")
task = next(t for t in tasks if t.id == "fix-sum-bug")

# 2. docker verify: oracle (fixed) passes, environment (buggy) fails
tmp = Path(tempfile.mkdtemp(prefix="sc-smoke-"))
try:
    good = tmp / "good"
    shutil.copytree(task.environment_dir, good)
    shutil.copy(task.root / "oracle" / "calc.py", good / "calc.py")
    passed_good, _ = verify(task, good)
    check("verify PASSES on fixed (oracle) workdir", passed_good)

    bad = tmp / "bad"
    shutil.copytree(task.environment_dir, bad)
    passed_bad, tail = verify(task, bad)
    check("verify FAILS on buggy (environment) workdir", not passed_bad)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# 3. stats / verdict math on synthetic trials
def trials(arm: str, n_pass: int, n: int, out_tok: int) -> list[TrialResult]:
    return [TrialResult("t", arm, i, i < n_pass, False, 100, out_tok, 0.1, 0, 1)
            for i in range(n)]

base = summarize_arm(trials("A", 2, 20, 500), k=3)        # 10% pass
winner = summarize_arm(trials("B_x", 18, 20, 500), k=3)    # 90% pass, same tokens
loser = summarize_arm(trials("B_y", 2, 20, 500), k=3)      # 10% pass
check("pass_rate computed", abs(base.pass_rate - 0.10) < 1e-9)
check("clear winner -> SURVIVE", verdict(base, winner).startswith("SURVIVE"))
check("no improvement -> not SURVIVE", not verdict(base, loser).startswith("SURVIVE"))

print("\nSMOKE", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
