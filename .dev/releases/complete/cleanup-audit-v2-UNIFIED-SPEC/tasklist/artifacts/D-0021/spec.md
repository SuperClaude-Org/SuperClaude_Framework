# D-0021: Env Key-Presence Matrix Specification (CRITICAL PATH)

## Security Constraint

**CRITICAL**: This module outputs environment variable **key names only**. Secret values are never read, stored, or emitted. All tests verify this invariant.

## Code Pattern Detection

| Pattern | Language | Example |
|---------|----------|---------|
| `process.env.KEY` | JavaScript/TypeScript | `process.env.DATABASE_URL` |
| `os.environ["KEY"]` | Python | `os.environ["SECRET_KEY"]` |
| `os.getenv("KEY")` | Python | `os.getenv("API_TOKEN", "default")` |

## Drift Categories

| Category | Meaning |
|----------|---------|
| missing_from_example | Key used in code but absent from `.env.example` |
| unused_in_code | Key present in `.env.example` but no code reference found |
| missing_from_env | Key used in code but absent from actual `.env` file |
| example_unused | Key in `.env` but not in `.env.example` (documentation gap) |

## Implementation

- Module: `src/superclaude/cli/audit/env_matrix.py`
- Scans `.env`, `.env.example`, and source files in a single pass
- Outputs a matrix of key names with their presence/absence across each source
- Drift report groups findings by category for actionable remediation
