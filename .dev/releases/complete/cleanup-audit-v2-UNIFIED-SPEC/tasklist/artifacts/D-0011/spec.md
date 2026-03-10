# D-0011: Domain and Risk-Tier Profiling Specification

## Module
`src/superclaude/cli/audit/profiler.py`

## Domain Classification Rules

| Domain | Path Patterns | Examples |
|--------|--------------|---------|
| test | `tests/`, `test/`, `__tests__/`, `test_`, `.test.`, `.spec.`, `conftest.py` | `tests/unit/test_foo.py` |
| docs | `docs/`, `README`, `CHANGELOG`, `LICENSE`, `.md` | `docs/setup.md` |
| infra | `.github/`, `Dockerfile`, `Makefile`, `.yml`, `scripts/` | `.github/workflows/ci.yml` |
| frontend | `src/components/`, `.jsx`, `.tsx`, `.vue`, `.css` | `src/components/Button.tsx` |
| backend | `src/api/`, `src/services/`, `models/`, `src/superclaude/` | `src/api/users.py` |

Priority order: test > docs > infra > frontend > backend (first match wins).
Default: `backend` with confidence 0.60.

## Risk-Tier Rules

| Tier | Patterns | Confidence |
|------|---------|------------|
| high | `auth`, `security`, `crypto`, `credential`, `.env`, `migration` | 0.90 |
| medium | `config`, `pyproject.toml`, `Dockerfile`, `.yml` | 0.85 |
| low | (default) | 0.80 |

Size-based bump: files > 15KB get `medium` with confidence 0.70.

## Schema

```json
{
  "file_path": "string",
  "domain": "frontend|backend|infra|docs|test",
  "risk_tier": "high|medium|low",
  "confidence": 0.0-1.0
}
```

## Determinism Guarantee
Same file path + same file size always produces identical profile. No randomness involved.
