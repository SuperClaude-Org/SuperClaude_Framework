# D-0028: Spec §3.4 Proof Update

## Evidence

**File**: `.dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md`
**Section**: §3.4 (lines 225-237)

### Changes
1. Title: "The 90% Reimbursement Rate" → "The 80% Reimbursement Rate"
2. Proof math corrected to rate=0.80:
   - `net_cost = 8 - floor(8 × 0.80) + 2 = 8 - 6 + 2 = 4`
   - `46-task drain = 46 × 4 = 184`
   - `margin = 200 - 184 = 16`

### Mathematical Verification
- `floor(8 × 0.80) = floor(6.4) = 6` ✓
- `8 - 6 + 2 = 4` ✓
- `46 × 4 = 184` ✓
- `200 - 184 = 16` ✓

Derivation matches spec §4.1-§4.2 floor model with rate=0.80.

## Traceability
- **Roadmap Item**: R-033
- **Spec §4.4**: Correction mandate
