# Diff Analysis -- Q6: execution_mode Annotation Location

## Variants Under Comparison

| Variant | Label | Summary |
|---|---|---|
| 3a | Index-level column | New `Execution Mode` column in the Phase Files table of `tasklist-index.md` |
| 3b | Phase file YAML frontmatter | YAML `---` block at the top of each `phase-N-tasklist.md` |
| 3c | Per-task metadata field | New row `Execution Mode` in each task's `Field | Value` table |
| 3d | Dual-level (index + per-task override) | Index marks phase as `python-eligible`; individual tasks can override |

---

## Structural Differences

### 1. Where the annotation lives

| Variant | File(s) modified | Parse site |
|---|---|---|
| 3a | `tasklist-index.md` only | `discover_phases()` |
| 3b | Each `phase-N-tasklist.md` | `parse_tasklist()` or new frontmatter extractor |
| 3c | Each `phase-N-tasklist.md` (per-task block) | `parse_tasklist()` |
| 3d | `tasklist-index.md` + each `phase-N-tasklist.md` (per-task block) | Both `discover_phases()` and `parse_tasklist()` |

### 2. Granularity

| Variant | Granularity | Override possible? |
|---|---|---|
| 3a | Phase-level only | No |
| 3b | Phase-level only | No |
| 3c | Task-level only | N/A (no phase default) |
| 3d | Phase-level default + task-level override | Yes |

### 3. Discovery timing (relative to subprocess launch)

| Variant | Available before subprocess launch? | Mechanism |
|---|---|---|
| 3a | Yes -- read from index during `discover_phases()` | Index is always read first |
| 3b | Yes -- but requires new file I/O before phase loop | Must open each phase file and parse frontmatter |
| 3c | No -- requires full `parse_tasklist()` which currently happens inside the subprocess prompt builder | Task metadata parsed after launch decision |
| 3d | Partially -- index gives phase default; task overrides require `parse_tasklist()` | Split timing |

### 4. Generator compatibility (`/sc:tasklist`)

| Variant | Generator change required |
|---|---|
| 3a | Add one column to Phase Files table template -- trivial |
| 3b | Add YAML frontmatter emission before the `# Phase N` heading -- moderate (new output format) |
| 3c | Add one row to every task metadata table -- moderate (per-task logic) |
| 3d | 3a changes + 3c changes -- compound |

### 5. Format consistency with existing conventions

| Variant | Consistent with existing format? |
|---|---|
| 3a | Yes -- Phase Files table already has columns; adding one is natural |
| 3b | No -- no existing tasklist uses YAML frontmatter; introduces a new convention |
| 3c | Yes -- task metadata tables already have `Field | Value` rows |
| 3d | Yes for both parts independently, but introduces a new concept (inheritance/override) |

---

## Contradictions and Tensions

1. **3c contradicts the timing requirement**: The runner needs execution_mode BEFORE launching a subprocess. `parse_tasklist()` runs after phase discovery. To use 3c, the runner would need to pre-parse all tasks just to determine execution mode, which defeats the purpose of avoiding unnecessary file I/O.

2. **3b introduces format divergence**: YAML frontmatter is not used anywhere in the current tasklist ecosystem. Every other piece of metadata uses markdown tables. This would be the sole exception.

3. **3d's override model adds complexity for unclear benefit**: The question "is task-level ever needed?" is central. If all tasks in a python-mode phase are python tasks, per-task override adds complexity with no value. If mixed-mode phases exist, 3d is the only option that handles them.

---

## Unique Contributions

- **3a**: Simplest possible change; single point of truth; zero parser changes needed for the critical path (discovery).
- **3b**: Self-contained per-file metadata; phase files are standalone (no index dependency for mode).
- **3c**: Maximum granularity; every task explicitly declares its mode.
- **3d**: Only option that handles mixed-mode phases without losing phase-level efficiency.
