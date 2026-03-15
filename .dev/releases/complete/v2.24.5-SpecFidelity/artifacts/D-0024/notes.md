# D-0024 Notes — T05.05: OQ-4 Assessment: `--tools default` for Non-Inheriting Executors

## OQ-4 Question

> If Phase 1.5 activates, do `remediate_executor.py`, `validate_executor.py`, and
> `tasklist/executor.py` also need `--tools default`? These do not inherit from
> `ClaudeProcess`; tool schema discovery failure could recur in these code paths.

## Assessment

All three executors **do** receive `--tools default` automatically.

### Evidence

Each executor imports and instantiates `ClaudeProcess` from `pipeline/process.py`:

```python
# remediate_executor.py:24
from ..pipeline.process import ClaudeProcess
# ...
proc = ClaudeProcess(...)  # line 192

# validate_executor.py:24
from ..pipeline.process import ClaudeProcess
# ...
proc = ClaudeProcess(...)  # line 117

# tasklist/executor.py:26
from ..pipeline.process import ClaudeProcess
# ...
proc = ClaudeProcess(...)  # line 129
```

`ClaudeProcess.build_command()` (pipeline/process.py:69) already includes `--tools default`:

```python
def build_command(self) -> list[str]:
    cmd = [
        "claude",
        "--print",
        "--verbose",
        self.permission_flag,
        "--no-session-persistence",
        "--tools",
        "default",           # <-- present in all ClaudeProcess instances
        "--max-turns",
        str(self.max_turns),
        "--output-format",
        self.output_format,
        "-p",
        self.prompt,
    ]
```

### Conclusion

None of the three non-inheriting executors require additional `--tools default`
modifications. Since all three instantiate `ClaudeProcess` directly, `build_command()`
provides `--tools default` to every subprocess they spawn.

**OQ-4 resolution: No action needed.**

## Scope Reminder

The spec (Section 1.2) notes:
> Adding `--tools default` to `remediate_executor.py`, `validate_executor.py`,
> `tasklist/executor.py` (these do not inherit from `ClaudeProcess` — tracked as
> open item OQ-4 if FIX-ARG-TOO-LONG Phase 1.5 activates)

The "do not inherit" language refers to `execute_pipeline()`, not `ClaudeProcess`.
Since `ClaudeProcess` itself carries `--tools default` in `build_command()`, any
direct instantiation automatically gets the flag.
