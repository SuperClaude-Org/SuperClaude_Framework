# D-0042 Evidence: TTL and LRU Lifecycle

## Test Results
```
12 passed in 0.03s
```

## Eviction Test Log
- Entry with TTL=-1 expired immediately on load (test_negative_ttl_immediately_expires)
- Entry with created_date 5 months ago, TTL=90d: EXPIRED
- Entry with last_matched 2 months ago, TTL=90d: KEPT (within TTL)
- 10 entries with max_entries=5: 5 evicted, 5 kept (most recent)
- Boundary: exactly 500 entries with max=500: 0 evicted
- Combined: TTL expiration runs first, then LRU eviction
