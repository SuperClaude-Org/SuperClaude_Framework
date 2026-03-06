# D-0004 Spec: Evidence-Gated DELETE and KEEP Rules

## Module
`src/superclaude/cli/audit/evidence_gate.py`

## Decision Tree
1. DELETE action → require zero-reference evidence ("zero" + "ref" in evidence strings)
2. KEEP action at TIER_1/TIER_2 → require reference evidence ("ref" in evidence strings)
3. All other actions → pass gate

## Gate API
- `check_delete_evidence(result) -> GateResult`
- `check_keep_evidence(result) -> GateResult`
- `evidence_gate(result) -> GateResult` (combined)
