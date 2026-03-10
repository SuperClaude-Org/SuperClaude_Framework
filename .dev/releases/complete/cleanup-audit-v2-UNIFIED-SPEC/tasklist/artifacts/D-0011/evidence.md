# D-0011: Evidence — Domain and Risk-Tier Profiling

## Test Results
- 29/29 tests passed (`tests/audit/test_profiler.py`)
- Determinism verified: two runs on identical input produce identical output
- All files receive non-null domain and risk_tier

## Test Repository Profile (7-file fixture)

```
Files: src/api/users.py, src/components/Button.tsx, tests/test_api.py,
       docs/README.md, .github/workflows/ci.yml, src/auth/login.py, pyproject.toml

Domain distribution: backend=2, frontend=1, test=1, docs=1, infra=1, backend=1
Risk distribution: high=1 (auth), medium=1 (pyproject.toml), low=5
```

## Acceptance Criteria Verification
- [x] Every file receives exactly one domain and one risk tier (no null fields)
- [x] Profiling is deterministic (identical output across runs)
- [x] Profile output matches AC13 schema (domain, risk_tier, confidence)
- [x] Rules documented in D-0011/spec.md
