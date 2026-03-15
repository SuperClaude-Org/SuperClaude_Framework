---
deliverable: D-0020
task: T03.09
title: Signal Handlers for SIGINT/SIGTERM
status: PASS
---

# D-0020: Signal Handlers

## Implementation

`src/superclaude/cli/cli_portify/executor.py` — `_install_signal_handlers()` / `_restore_signal_handlers()`

## Behavior

- SIGINT and SIGTERM both set `self._interrupted = True`
- After each step completes, the executor checks `_interrupted`; if True → `PortifyOutcome.INTERRUPTED`
- The current step is allowed to complete before the interrupt is processed (FR-039, NFR-003)
- Return contract is emitted with `INTERRUPTED` outcome on the INTERRUPTED path
- Original handlers are restored in the `finally` block after execution

## Signal flow

```
Signal → handler sets _interrupted=True
         → current step finishes
         → main loop checks _interrupted
         → break loop with INTERRUPTED outcome
         → finally: restore handlers, emit return contract
```

## Validation

`uv run pytest tests/ -k "test_signal_handler"` → 5 passed
