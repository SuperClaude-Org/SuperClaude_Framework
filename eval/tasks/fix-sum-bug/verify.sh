#!/usr/bin/env bash
# Machine pass/fail. Runs in python:3.12-slim against /work. Isolated from the
# agent (the agent never sees this file).
set -euo pipefail
cd /work
python - <<'PY'
from calc import add
assert add(2, 3) == 5, f"add(2,3)={add(2,3)}"
assert add(-1, 1) == 0, f"add(-1,1)={add(-1,1)}"
assert add(0, 0) == 0
print("ok")
PY
