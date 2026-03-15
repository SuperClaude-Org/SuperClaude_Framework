# Refactor Plan -- Q6: Implement execution_mode as Index-Level Column (3a)

## Selected Approach

Add an `Execution Mode` column to the Phase Files table in `tasklist-index.md`. Default value: `claude`. Alternative value: `python`.

## Integration Points

### 1. Model change: `Phase` dataclass

**File**: `src/superclaude/cli/sprint/models.py` (line 254)
**Change**: Add field
**Risk**: Low

```python
@dataclass
class Phase:
    number: int
    file: Path
    name: str = ""
    execution_mode: str = "claude"  # "claude" | "python"
```

### 2. Parser change: `discover_phases()`

**File**: `src/superclaude/cli/sprint/config.py` (line 27)
**Change**: After extracting phase file references from the index, also parse the Phase Files table to extract the Execution Mode column. If the column is absent (backward compatibility), default to `"claude"`.
**Risk**: Medium -- must handle indexes that lack the column.

Approach: After the existing `PHASE_FILE_PATTERN` scan, do a secondary pass over the index text to find the Phase Files markdown table and extract column values keyed by phase number. This avoids modifying the regex-based discovery and keeps the two concerns (file discovery vs. metadata extraction) separate.

### 3. Generator change: `/sc:tasklist` template

**File**: The tasklist generator template (slash command)
**Change**: Add `Execution Mode` column to the Phase Files table template. Default to `claude` for all phases. The roadmap must specify which phases are python-mode; the generator maps this through.
**Risk**: Low

New table format:
```
| Phase | File | Phase Name | Task IDs | Tier Distribution | Execution Mode |
|---|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Pre-Sprint Setup | T01.01-T01.07 | STANDARD: 4, EXEMPT: 3 | claude |
| 2 | phase-2-tasklist.md | Empirical Gate | T02.01-T02.05 | STRICT: 5 | python |
```

### 4. Executor change: `execute_sprint()`

**File**: `src/superclaude/cli/sprint/executor.py` (line 526)
**Change**: In the phase loop, check `phase.execution_mode` before launching. If `"python"`, invoke the python executor instead of `ClaudeProcess`.
**Risk**: Medium -- this is the core behavioral change.

```python
for phase in config.active_phases:
    if phase.execution_mode == "python":
        result = execute_python_phase(config, phase)
    else:
        result = execute_claude_phase(config, phase)  # existing logic
```

### 5. Test changes

**File**: `tests/sprint/test_config.py`
**Changes**:
- Test `discover_phases()` with index containing Execution Mode column
- Test `discover_phases()` with index LACKING the column (backward compat -> defaults to "claude")
- Test `Phase.execution_mode` defaults to "claude"

**File**: `tests/sprint/test_models.py`
**Changes**:
- Test `Phase` dataclass with `execution_mode` field

## Backward Compatibility

- Existing `tasklist-index.md` files without the column will work unchanged (default to `"claude"`)
- The `Phase` dataclass default is `"claude"`, so all existing code paths are unaffected
- No changes to `parse_tasklist()` or `TaskEntry` -- task-level parsing is untouched

## Future Evolution Path (to 3d if needed)

If mixed-mode phases become necessary:
1. Add optional `execution_mode: str = ""` to `TaskEntry`
2. Extend `parse_tasklist()` to extract it from the task metadata table
3. Resolution: task override wins over phase default; empty string means "inherit from phase"
4. No breaking changes to the index-level annotation

## Risk Summary

| Component | Risk | Mitigation |
|---|---|---|
| `Phase` dataclass | Low | Default value ensures backward compat |
| `discover_phases()` | Medium | Feature-detect column presence; fall back to default |
| `/sc:tasklist` template | Low | Additive change to template |
| `execute_sprint()` | Medium | Branch on `execution_mode`; existing path unchanged |
| Backward compatibility | Low | All defaults are "claude" (current behavior) |
