# D-0015: Dry-Run Mode Specification

## Module
`src/superclaude/cli/audit/dry_run.py`

## Pipeline Cutoff
Dry-run executes: profiling + batch planning. Stops before analysis execution.

## Output Schema
```json
{
  "file_count": 100,
  "batch_count": 3,
  "estimated_tokens": 50000,
  "estimated_runtime_seconds": 15.0,
  "domain_distribution": {"backend": 40, "frontend": 30, "test": 20, "docs": 10},
  "risk_distribution": {"high": 5, "medium": 15, "low": 80},
  "segments_detected": ["__root__"]
}
```

## Estimation Heuristics
- Tokens: sum of batch estimates, or file_count * 500 fallback
- Runtime: batch_count * 5 seconds per batch
