---
deliverable: D-0042
task: T05.06
status: PASS
date: 2026-03-09
---

# D-0042: --no-validate Behavior Verification

## Evidence

`--no-validate` does **NOT** skip the spec-fidelity step (SC-014 verified).

### Architecture Proof

The spec-fidelity step is a **pipeline step** built by `_build_steps(config)`.
The `--no-validate` flag controls only post-pipeline validation invocation
(`_auto_invoke_validate(config)`), which is a separate subsystem.

```
_build_steps(config) signature: (config: RoadmapConfig) -> list[Step | list[Step]]
  no_validate parameter present: False
```

### Flag Combination Matrix

| Flag Combination | Fidelity Step Runs | Post-Pipeline Validate Runs |
|------------------|--------------------|-----------------------------|
| (default) | Yes | Yes |
| `--no-validate` | Yes | No |
| `--dry-run` | Listed (not run) | No |
| `--resume` | Yes (if not already passed) | Yes (if not already done) |
| `--no-validate --resume` | Yes (if not already passed) | No |

### Pipeline Step Order (verified programmatically)

1. extract (STRICT)
2. generate-opus-architect (STRICT)
3. generate-haiku-architect (STRICT)
4. diff (STANDARD)
5. debate (STRICT)
6. score (STANDARD)
7. merge (STRICT)
8. test-strategy (STANDARD)
9. **spec-fidelity (STRICT)** — always present in pipeline

### Implementation Reference

- `_build_steps()`: `src/superclaude/cli/roadmap/executor.py`
- `--no-validate` handling: `executor.py` lines 710-758
- Docstring confirms: "Note: --no-validate does NOT skip the spec-fidelity step"
