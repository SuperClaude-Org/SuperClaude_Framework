# D-0023: Operator Documentation — YAML Coercions and Limitations

## Accepted YAML Boolean Values for spec_update_required

The `spec_update_required` field in deviation files (`dev-*-accepted-deviation.md`) accepts the following YAML 1.1 boolean forms as `true`:

| YAML Value | Accepted | Notes |
|------------|----------|-------|
| `true` | Yes | Standard YAML boolean |
| `True` | Yes | YAML 1.1 case variant |
| `TRUE` | Yes | YAML 1.1 case variant |
| `yes` | Yes | YAML 1.1 boolean coercion |
| `Yes` | Yes | YAML 1.1 boolean coercion |
| `YES` | Yes | YAML 1.1 boolean coercion |
| `on` | Yes | YAML 1.1 boolean coercion |
| `1` | Yes | YAML 1.1 integer-as-boolean |
| `"true"` | **No** | Quoted string, not boolean |
| `"yes"` | **No** | Quoted string, not boolean |

This is an intentional design contract. PyYAML's `safe_load` parses unquoted YAML 1.1 values as Python `bool`. Quoted values become Python `str` and are rejected.

## Single-Writer Limitation

`.roadmap-state.json` requires exclusive write access during execution. No file locking is implemented. The operator must prevent concurrent access:

- Do not run multiple `roadmap run` or `accept-spec-change` commands targeting the same output directory simultaneously
- Do not edit `.roadmap-state.json` while a roadmap command is running

## mtime Resolution

The auto-resume detection compares deviation file mtime against `started_at` using strict `>`. On filesystems with low mtime resolution (HFS+ at 1s, NFS with varying resolution), deviation files created within the same second as `started_at` may not be detected. This is a deliberate fail-closed behavior.
