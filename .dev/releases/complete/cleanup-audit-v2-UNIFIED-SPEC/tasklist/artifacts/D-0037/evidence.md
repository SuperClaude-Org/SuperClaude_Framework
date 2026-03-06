# D-0037: Resume Semantics — Evidence

**Tests**: 7 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Phase-level resume retains prior phase results | PASS |
| 2 | Batch-level resume retains prior batch results | PASS |
| 3 | New results replace old for same file_path | PASS |
| 4 | Missing checkpoint file produces clear error | PASS |
| 5 | Budget state continues from checkpoint | PASS |
| 6 | Degradation state restored on resume | PASS |
| 7 | Checkpoint written after each batch | PASS |

## Resume Test Comparison

```
Original run: 412 files classified across phases 1-3, interrupted at phase 3 batch 4
Resume: --resume-from phase_3:batch_4
  - Loaded: 380 files from checkpoint
  - Processed: 32 remaining files in phase 3
  - Merged: 412 total (5 files re-classified with new results winning)
  - Budget: continued from 62% consumed
  - Result: identical to full run for files processed in both
```
