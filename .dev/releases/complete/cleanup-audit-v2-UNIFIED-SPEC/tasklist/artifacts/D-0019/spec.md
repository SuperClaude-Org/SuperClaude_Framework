# D-0019: Escalation Sub-Engine Specification

## Escalation Signal Detection

| Signal | Trigger Condition | Response |
|--------|-------------------|----------|
| low_confidence | Profile confidence < 0.6 | Re-classify with enhanced evidence collection |
| conflicting_evidence | Mixed KEEP/DELETE indicators in same profile | Gather additional signals before verdict |
| investigate_status | Initial classification returned INVESTIGATE | Attempt deeper analysis within token budget |

## Token Budget Enforcement

| Parameter | Default | Purpose |
|-----------|---------|---------|
| max_file_lines | 500 | Cap on lines read per escalated file to prevent runaway analysis |
| token_budget | 5000 | Hard ceiling on total tokens consumed during escalation pass |

## Re-Classification Logic

1. Collect enhanced evidence (additional import/export scans, git history)
2. Re-run classification with augmented profile
3. If new confidence >= 0.6 and no conflicts: accept new classification
4. Otherwise: fall back to INVESTIGATE with all gathered evidence attached

## Implementation

- Module: `src/superclaude/cli/audit/escalation.py`
- Entry point: `escalate()` accepts a file profile and returns an updated classification
- Budget tracking: internal counter decrements per operation; halts when exhausted
- Integrates with Phase 2 profile data and Phase 3 classification pipeline
