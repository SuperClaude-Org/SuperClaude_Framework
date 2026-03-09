---
deliverable: D-0046
task: T05.09
status: PASS
date: 2026-03-09
---

# Rollback Plan for Gate Strictness Changes

## Scope

This plan covers rollback for all 3 new gates introduced in v2.20:
1. **REFLECT_GATE** (validate_gates.py)
2. **SPEC_FIDELITY_GATE** (gates.py)
3. **TASKLIST_FIDELITY_GATE** (tasklist/gates.py)

## Rollback Triggers

| Trigger | Threshold | Gate Affected |
|---------|-----------|---------------|
| False positive rate | >5% per gate | Any |
| Pipeline blocked on known-good input | 1 occurrence | Any |
| Degraded runs exceed 20% | >20% in 7 days | REFLECT_GATE |
| HIGH severity inflation | >50% increase vs baseline | SPEC_FIDELITY_GATE |
| Tasklist validation blocking valid tasklists | 1 occurrence | TASKLIST_FIDELITY_GATE |

## Step-by-Step Rollback Procedure

### Step 1: Identify Affected Gate

Determine which gate is causing issues based on the error message and
pipeline output. Gate names appear in `[step-id] FAIL:` messages.

### Step 2: Demote Gate Enforcement Tier

Change the gate's `enforcement_tier` from `"STRICT"` to `"STANDARD"` in the
relevant file:

```python
# In src/superclaude/cli/roadmap/gates.py (for SPEC_FIDELITY_GATE)
# Change: enforcement_tier="STRICT"
# To:     enforcement_tier="STANDARD"
```

This preserves gate checking but removes semantic check enforcement.

### Step 3: Run Verification

```bash
uv run pytest tests/roadmap/ -v
uv run pytest tests/tasklist/ -v
```

### Step 4: Document Rollback

Record in the release execution log:
- Which gate was demoted
- Trigger condition that caused rollback
- Evidence of false positive(s)
- Date and time

### Step 5: Restore After Fix

After the gate logic is corrected:
1. Restore `enforcement_tier="STRICT"`
2. Replay the failing artifact to confirm fix
3. Run full test suite
4. Document restoration

## Rollback Drill Results

### Drill: SPEC_FIDELITY_GATE Demotion (Dry Run)

**Scenario**: Simulate demoting SPEC_FIDELITY_GATE from STRICT to STANDARD.

**Expected behavior**: Gate still validates frontmatter fields and min_lines,
but skips semantic checks (`_high_severity_count_zero`,
`_tasklist_ready_consistent`).

**Verification**: The `gate_passed()` function in `pipeline/gates.py` exits
after frontmatter check at tier "STANDARD" (line ~60), before semantic checks
(line ~65). This is confirmed by reading the implementation — STANDARD tier
returns True after frontmatter validation.

**Result**: Drill confirms rollback mechanism is functional. Demoting a gate
to STANDARD preserves structural validation while removing semantic blocking.

## Recovery Time Estimate

| Action | Time |
|--------|------|
| Identify affected gate | 5 min |
| Edit enforcement_tier | 2 min |
| Run tests | 1 min |
| Document | 5 min |
| **Total** | **~13 min** |

## Evidence Paths

- Monitoring metrics: `artifacts/D-0045/spec.md`
- This rollback plan: `artifacts/D-0046/spec.md`
- Rollback drill evidence: documented inline above
