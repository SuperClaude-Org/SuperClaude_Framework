# D-0041: Implicit Contract Extractor Specification

## ImplicitContract Structure

```python
ImplicitContract:
    variable: str               # State variable name
    writer_deliverable: str     # ID of writing deliverable
    reader_deliverable: str     # ID of reading deliverable
    writer_semantics: str       # Extracted meaning ("UNSPECIFIED" if below threshold)
    reader_assumption: str      # Extracted assumption ("UNSPECIFIED" if below threshold)
    writer_confidence: float    # 0.0-1.0 extraction confidence
    reader_confidence: float    # 0.0-1.0 extraction confidence

Properties:
    needs_human_review: bool    # True if either confidence < 0.60
    overall_confidence: float   # Geometric mean of writer/reader confidence
    is_fully_specified: bool    # Both sides != UNSPECIFIED
    highest_risk: bool          # Both sides == UNSPECIFIED
```

## Extraction Patterns

### Writer Semantics (8 patterns, confidence range 0.55-0.85)
| Pattern | Base Confidence |
|---------|----------------|
| "set X to mean/represent/track Y" | 0.85 |
| "X represents Y" | 0.80 |
| "X tracks/counts/measures Y" | 0.80 |
| "store Y in X" | 0.75 |
| "X equals/becomes Y" | 0.75 |
| "increment/advance X by Y" | 0.75 |
| "update X with/to Y" | 0.70 |
| "X is Y" (weak) | 0.55 |

### Reader Assumptions (8 patterns, confidence range 0.50-0.90)
| Pattern | Base Confidence |
|---------|----------------|
| "assumes X is/equals Y" | 0.90 |
| "expects X to be Y" | 0.85 |
| "when X equals/is Y" | 0.85 |
| "X should/must be Y" | 0.80 |
| "if X is/equals Y" | 0.75 |
| "based on/depends on X" | 0.70 |
| "requires X" | 0.60 |
| "uses/reads X" (weak) | 0.50 |

## Confidence Scoring Algorithm

1. Match description against all patterns
2. Select highest-confidence match
3. Apply proximity boost (+0.05) if variable name within 50 chars of match
4. Cap at 1.0
5. Below 0.60 threshold → classify as UNSPECIFIED with mandatory human review

## UNSPECIFIED Handling

- **writer_semantics = UNSPECIFIED**: Writer pattern not found or below threshold
- **reader_assumption = UNSPECIFIED**: Reader pattern not found or below threshold
- **Both UNSPECIFIED**: Highest-risk classification, always flagged
- **needs_human_review**: True if either side below 0.60
