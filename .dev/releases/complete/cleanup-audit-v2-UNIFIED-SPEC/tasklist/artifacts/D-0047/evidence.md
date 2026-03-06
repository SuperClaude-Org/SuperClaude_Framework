# D-0047 Evidence: Limitations Section Sample

## Sample Limitations Section (as rendered in final report)

---

## Known Limitations and Non-Determinism Sources

This section documents known sources of non-determinism and their impact on result reliability.

| # | Source | Impact | Mitigation |
|---|--------|--------|------------|
| 1 | LLM Classification Variance | Borderline files may shift 1-2 categories between runs | Evidence gates, confidence thresholds, anti-lazy guard, spot-check validation |
| 2 | Git History Dependency | Shallow clones may produce inaccurate profiling | Graceful handling of missing data, budget caveats |
| 3 | Dynamic Import Detection | Dynamically-imported files may be false-positive DELETE | Pattern scanner, KEEP:monitor protection, exclusion lists |
| 4 | Tier-C Inference Confidence | Co-occurrence heuristic may create false relationships | Lower weighting (40%), Tier-A/B prioritization, evidence labeling |

**Overall Assessment**: The mitigations above reduce but do not eliminate non-determinism. Users should treat audit results as recommendations requiring human review, particularly for DELETE classifications on files with low confidence scores.

---

## Verification

- Section contains 4 non-determinism sources (exceeds minimum of 3)
- Each source has impact description and mitigation notes
- Section is designed for insertion between validation results and appendix
