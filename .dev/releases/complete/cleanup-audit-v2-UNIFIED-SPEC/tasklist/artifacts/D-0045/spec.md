# D-0045 Spec: Benchmark Results

## Task Reference
- Task: T05.06
- Roadmap Item: R-045
- AC: AC9, AC12, AC17

## Benchmark Configuration

Three repository tiers tested with self-contained in-memory fixtures:

| Tier | Size | File Count | Description |
|------|------|------------|-------------|
| Small | <50 files | 33 | Single-module Python project |
| Medium | 50-500 files | 223 | Multi-package Python project |
| Dead Code | Mixed | 33 | Repo with 10 documented dead code files |

## Benchmark Metrics

### Small Repo (<50 files)
- Decomposition: Completes without error (batch_count > 0)
- Dry-run estimation: Produces token estimates
- Profiling: All files receive domain + risk tier profiles
- Report generation: Standard depth renders without error

### Medium Repo (50-500 files)
- Decomposition: Completes without error (223 files, batch_count > 0)
- Budget estimation: Produces valid token/batch estimates
- Coverage tracking: 100+ files tracked with per-tier metrics

### Known Dead Code Repo
- Detection rate: >= 80% of documented dead code files detected
- False positive rate: 0% on entry points (__init__.py, setup.py, conftest.py)
- Exclusion rules: All excluded candidates have documented exclusion reasons

## Test Files
- `tests/audit/test_benchmark.py` — 9 tests across 3 benchmark classes
