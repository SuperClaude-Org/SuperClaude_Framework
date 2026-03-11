# D-0015: Phase 3 Timing Instrumentation

## Instrumentation Points

1. **Start**: Line 165 — `Record phase_3_start = current_time()` at Phase 3 entry
2. **End**: Line 231 — `Record phase_3_end = current_time()`, compute `phase_3_seconds = phase_3_end - phase_3_start`
3. **Contract field**: `phase_timing.phase_3_seconds` in return contract
4. **NFR-001 advisory**: 10-minute (600s) wall clock target, non-blocking warning if exceeded
