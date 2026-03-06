# D-0031: Evidence — Convergence Gate for Invariant Probe

## Verification: AC-AD1-3

**Scenario**: 90% diff-point agreement with 2 HIGH-severity UNADDRESSED items.

**Gate algorithm** (from SKILL.md `invariant_probe_gate`):
1. Parse invariant-probe.md table
2. Filter: Status == UNADDRESSED AND Severity == HIGH
3. Count = 2 (> 0)
4. Block convergence: "CONVERGENCE BLOCKED: 2 HIGH-severity UNADDRESSED invariant(s)"
5. Report blocking items: INV-003, INV-007

**Expected output**:
```
CONVERGENCE BLOCKED: 2 HIGH-severity UNADDRESSED invariant(s) detected
Blocking items: INV-003, INV-007
These invariant violations must be resolved before convergence can be declared.
```

The 90% diff-point agreement score is irrelevant — the gate blocks regardless of agreement score when HIGH UNADDRESSED items exist.

**Verdict: AC-AD1-3 PASS**

## Verification: MEDIUM items are warnings only

The `warning_message` template is separate from the `block_message`. MEDIUM items are logged as:
```
WARNING: {count} MEDIUM-severity UNADDRESSED invariant(s) detected
Items: {inv_id_list}
These items do not block convergence but should be reviewed.
```

No blocking occurs for MEDIUM items.

**Verdict: PASS**

## Verification: Gate message identifies specific INV-NNN items

Both `block_message` and `warning_message` include `{inv_id_list}` which lists the specific INV-NNN identifiers.

**Verdict: PASS**

## Files Modified

- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`:
  - `gate_condition` updated to include `no_high_unaddressed_invariants`
  - New `invariant_probe_gate` subsection added to convergence_detection
  - `status_output` extended with `BLOCKED_BY_INVARIANTS`
