# D-0046 Spec: Concurrent-Run Isolation

## Task Reference
- Task: T05.07
- Roadmap Item: R-046
- AC: AC20

## Isolation Mechanism

Each audit run operates in an isolated namespace:

1. **Progress isolation**: Each run writes to a separate `progress.json` file in its own run directory (`<output_dir>/run-<id>/progress.json`)
2. **Cache isolation**: Each run creates a separate `ResultCache` instance. Cache entries are keyed by content hash within the in-memory instance, not shared across runs.
3. **Registry isolation**: Known-issues registries are loaded from and saved to per-run paths.
4. **Output isolation**: Batch decomposition is deterministic — same inputs produce same outputs, meaning concurrent runs on identical input produce identical (not conflicting) results.

## Verification Approach

- **Thread safety**: Two threads write checkpoints simultaneously to separate directories; both read back correctly with no corruption.
- **Cache independence**: Two separate `ResultCache` instances store different results for the same content hash without cross-contamination.
- **Registry independence**: Two separate registry files on different paths are loaded/saved independently.
- **Determinism**: Same file list + batch size → identical batch IDs, ensuring concurrent-vs-sequential equivalence.

## Test File
- `tests/audit/test_concurrent_isolation.py` — 8 tests across 4 test classes
