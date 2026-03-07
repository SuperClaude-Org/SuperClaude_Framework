# Phase 1 -- Live Evidence — 3 Quick Tasks

Three small tasks to prove the sprint runner's per-task subprocess loop, TurnLedger budget tracking, and gate evaluation work end-to-end with real Claude Code subprocesses.

### T01.01 -- Write a Python hello-world script

| Field | Value |
|---|---|
| Tier | STANDARD |
| Deliverable IDs | D-0001 |

**Deliverables:**
- Create a file `hello.py` in the current working directory that prints "Hello from T01.01" when run with `python hello.py`

**Steps:**
1. **[EXECUTION]** Write hello.py with a single print statement
2. **[COMPLETION]** Write evidence to artifacts/D-0001/evidence.md confirming the file was created

**Acceptance Criteria:**
- File `hello.py` exists and contains a print statement
- Evidence file at artifacts/D-0001/evidence.md exists

**Validation:**
- `python hello.py` prints output

**Dependencies:** None

---

### T01.02 -- Write a simple math utility

| Field | Value |
|---|---|
| Tier | STANDARD |
| Deliverable IDs | D-0002 |

**Deliverables:**
- Create a file `math_util.py` in the current working directory that defines `add(a, b)` and `multiply(a, b)` functions

**Steps:**
1. **[EXECUTION]** Write math_util.py with add and multiply functions
2. **[COMPLETION]** Write evidence to artifacts/D-0002/evidence.md

**Acceptance Criteria:**
- File `math_util.py` exists with add() and multiply() functions
- Evidence file at artifacts/D-0002/evidence.md exists

**Validation:**
- `python -c "from math_util import add, multiply; print(add(2,3), multiply(4,5))"`

**Dependencies:** None

---

### T01.03 -- Write a status summary file

| Field | Value |
|---|---|
| Tier | STANDARD |
| Deliverable IDs | D-0003 |

**Deliverables:**
- Create a file `status.md` summarizing that all 3 tasks completed

**Steps:**
1. **[EXECUTION]** Check that hello.py and math_util.py exist
2. **[EXECUTION]** Write status.md with a summary
3. **[COMPLETION]** Write evidence to artifacts/D-0003/evidence.md

**Acceptance Criteria:**
- File `status.md` exists
- Evidence file at artifacts/D-0003/evidence.md exists

**Validation:**
- `cat status.md` shows content

**Dependencies:** T01.01, T01.02
