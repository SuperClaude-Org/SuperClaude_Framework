# D-0031: Convergence Gate for Invariant Probe

## Overview

The invariant probe convergence gate reads `invariant-probe.md`, blocks convergence when HIGH-severity UNADDRESSED items exist, and logs MEDIUM-severity items as warnings without blocking.

## Gate Logic

```
IF count(Status==UNADDRESSED AND Severity==HIGH) > 0:
    BLOCK convergence
    Report: "CONVERGENCE BLOCKED: {N} HIGH-severity UNADDRESSED invariant(s)"
    List blocking INV-NNN IDs

IF count(Status==UNADDRESSED AND Severity==MEDIUM) > 0:
    LOG warning
    Report: "WARNING: {N} MEDIUM-severity UNADDRESSED invariant(s)"
    List warning INV-NNN IDs

LOW-severity items: no action
```

## Integration Point

Added to `convergence_detection` section in SKILL.md:
- `gate_condition` updated: now requires `no_high_unaddressed_invariants == true`
- New `invariant_probe_gate` subsection with algorithm, messages, and acceptance test
- `status_output` updated: new `BLOCKED_BY_INVARIANTS` status

## Skipped Behavior

When Round 2.5 is skipped (`--depth quick`), the invariant probe gate is not applied. Convergence uses only diff-point and taxonomy gates — fully backward compatible.

## Acceptance Criteria

- AC-AD1-3: 90% diff-point agreement + 2 HIGH UNADDRESSED items = convergence BLOCKED (PASS)
- MEDIUM items produce warnings, do not block (PASS)
- Gate message identifies specific INV-NNN blocking items (PASS)
