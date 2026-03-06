# D-0042 Spec: TTL and LRU Lifecycle Rules

## Task Reference
- Task: T05.03
- Roadmap Item: R-042
- AC: AC20 (supporting)

## TTL Policy
- Entries are expired if their reference date exceeds `ttl_days`
- Reference date: `last_matched` if set, else `created_date`
- Default TTL: 90 days
- Expiration runs on registry load via `expire_entries()`

## LRU Eviction
- When registry exceeds `max_entries` (default: 500), evict least-recently-matched
- Entries sorted by `last_matched` (or `created_date` fallback)
- Most-recently-matched entries are kept

## API
```python
events = registry.expire_entries(now=datetime.now(timezone.utc))
events = registry.evict_lru(max_entries=500)
events = registry.apply_lifecycle(now=now, max_entries=500)  # both
```

## EvictionEvent
```python
@dataclass
class EvictionEvent:
    issue_id: str
    reason: str  # ttl_expired | lru_eviction
    detail: str
```

## Implementation
- Source: `src/superclaude/cli/audit/known_issues.py`
- Tests: `tests/audit/test_known_issues_lifecycle.py` (12 tests)
