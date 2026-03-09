# Decision D-0005: Module Placement

| Field | Value |
|---|---|
| Decision ID | D-0005 |
| Open Question | OQ-002 |
| Related Requirements | AC-006 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

Should tasklist validation code live under `cli/tasklist/` (new module) or `cli/roadmap/` (extend existing)?

## Decision

**`src/superclaude/cli/tasklist/` as a new module. Tasklist validation is cleanly separated from roadmap generation.**

### Module Structure

```
src/superclaude/cli/tasklist/
├── __init__.py       # Module exports, CLI group registration
├── commands.py       # Click command definitions (validate, check, report)
├── executor.py       # Tasklist validation pipeline executor
├── gates.py          # Tasklist-specific gate checks (severity, count, fidelity)
└── prompts.py        # LLM prompt templates for tasklist fidelity checking
```

### Import Paths

```python
from superclaude.cli.tasklist import validate_tasklist
from superclaude.cli.tasklist.gates import tasklist_fidelity_gate
from superclaude.cli.tasklist.executor import TasklistValidator
```

### CLI Registration

The `tasklist` module registers as a Click group under the main CLI:

```python
# In src/superclaude/cli/main.py
from superclaude.cli.tasklist.commands import tasklist_group
app.add_command(tasklist_group, "tasklist")
```

Usage: `superclaude tasklist validate <path>`

## Rationale

- **AC-006 compliance**: "All new logic extends the `roadmap/` module or creates the new `tasklist/` module." A new module is the cleaner choice since tasklist validation has distinct responsibilities from roadmap generation.
- **Separation of concerns**: Roadmap generation (`cli/roadmap/`) produces roadmaps; tasklist validation (`cli/tasklist/`) validates tasklists against roadmaps. Different input/output contracts.
- **Existing `cli/` conventions**: The `cli/` directory already uses a flat module structure (`main.py`, `doctor.py`, `install_skill.py`). A `tasklist/` subdirectory follows the same pattern as the existing `roadmap/` module.
- **Import clarity**: `superclaude.cli.tasklist` is unambiguous about the module's purpose.

## Impacts

- **AC-006**: Satisfied by creating a new module rather than extending `roadmap/`.
- **Import paths**: All tasklist validation imports use `superclaude.cli.tasklist.*`.
- **CLI surface**: New `superclaude tasklist` command group.
- **Pipeline module**: `pipeline/` (models.py, gates.py, executor.py) remains unchanged per AC-006.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-002 | New `cli/tasklist/` module for tasklist validation | AC-006 |
