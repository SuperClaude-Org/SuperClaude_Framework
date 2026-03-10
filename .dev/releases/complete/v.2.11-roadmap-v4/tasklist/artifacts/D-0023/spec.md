# D-0023: FMEA Failure Mode Classifier Specification

## Module
`src/superclaude/cli/pipeline/fmea_classifier.py`

## Dual Signal Architecture

### Signal 1: Invariant Cross-Reference
Cross-references computation outputs against invariant predicates from the M2 registry.
- Mutation of tracked variable without error path → silent corruption
- Requires invariant entries from the invariant registry pass
- Not a hard dependency: Signal 2 operates independently

### Signal 2: Independent No-Error-Path Detection
Detects computations that return values on degenerate inputs without raising exceptions.
- Works even when NO invariant predicates are registered
- Prevents circular dependency on M2 registry completeness
- Uses description heuristics: mutation patterns, return patterns, wrong-outcome patterns

## Detection Difficulty Levels
| Level | Description | Example |
|-------|-------------|---------|
| immediate | Error raised at point of failure | TypeError on null input |
| delayed | Error surfaces later in execution | Filter returns empty, downstream fails |
| silent | No error at all, wrong value produced | Offset advances by wrong amount |

## Severity Levels
| Level | Rank | Description |
|-------|------|-------------|
| data_loss | 4 (highest) | Data permanently lost or corrupted |
| wrong_state | 3 | System state incorrect but recoverable |
| degraded | 2 | Reduced functionality or performance |
| cosmetic | 1 (lowest) | Visual or display issues only |

## Signal Combination Rules
- Silent corruption from either signal → severity elevated to WRONG_STATE minimum
- Both signals fire → take worst detection_difficulty and highest severity
- Single signal → use as-is with silent corruption elevation

## Key Design Decision
From adversarial Round 2: dual signal architecture retained from V1 variant.
Signal 2 independence prevents circular dependency on registry completeness.
