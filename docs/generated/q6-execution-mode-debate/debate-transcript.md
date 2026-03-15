# Debate Transcript -- Q6: execution_mode Annotation Location

## Round 1: Opening Arguments

### Advocate 3a (Index-level column)

The runner's decision point is in `execute_sprint()` at line 526: `for phase in config.active_phases`. Before entering this loop, `discover_phases()` has already parsed the index file. The execution mode decision -- "should I launch a Claude subprocess or a Python process?" -- must be made at this exact point, BEFORE any phase file is opened.

Option 3a places the annotation exactly where the runner already looks: the Phase Files table in `tasklist-index.md`. The existing `discover_phases()` function iterates over `PHASE_FILE_PATTERN` matches in the index text. Adding an `Execution Mode` column to the Phase Files table means:

1. **Zero new file I/O** -- the index is already read into memory at line 39 of config.py.
2. **Trivial parser change** -- extend the regex or table parser in `discover_phases()` to extract one additional column.
3. **Perfect format consistency** -- the Phase Files table already has 5 columns; a 6th is natural.

The generator (`/sc:tasklist`) already emits this table. Adding a column is a template-level change, not a logic change.

Evidence from codebase: `Phase` dataclass (models.py:254-267) has `number`, `file`, `name`. Adding `execution_mode: str = "claude"` is a one-field extension.

### Advocate 3b (Phase file YAML frontmatter)

The index file is a registry, not a configuration surface. Putting execution semantics in the index conflates discovery (what phases exist) with configuration (how to run them). YAML frontmatter is the standard way to attach metadata to markdown files across the entire software ecosystem (Jekyll, Hugo, Pandoc, Obsidian, MkDocs).

Each phase file should be self-describing. If someone reads `phase-3-tasklist.md` in isolation, they should know it is a python-mode phase without cross-referencing the index. This is the principle of locality.

The runner can parse frontmatter with 3 lines of code:
```python
import re
fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if fm_match:
    # parse YAML or simple key: value pairs
```

This happens before `parse_tasklist()` and before subprocess launch, so timing is satisfied.

### Advocate 3c (Per-task metadata field)

Execution mode is fundamentally a property of the TASK, not the phase. Consider: a phase might contain 5 tasks where 4 are analysis (claude-mode) and 1 is "run pytest" (python-mode). Forcing phase-level granularity means either:
- Splitting the pytest task into its own phase (artificial phase proliferation), or
- Running it through Claude unnecessarily (wasteful).

The existing task metadata table already has 12+ fields including Tier, Confidence, Effort, Risk, Verification Method, MCP Requirements, etc. Adding `Execution Mode` is entirely consistent with this pattern.

The `parse_tasklist()` function (config.py:196) already extracts task blocks. Adding one more field extraction follows the same pattern as dependency extraction.

### Advocate 3d (Dual-level)

Both the phase-level and task-level camps have valid points. The solution is not to choose one; it is to layer them. The index provides a phase-level default (`python-eligible` or `claude`), and individual tasks can override.

This mirrors how CSS works (cascade), how Git config works (system/global/local), and how `SprintConfig` already works (defaults with per-phase overrides for things like `max_turns`).

The resolution algorithm is simple:
1. Read phase default from index (during `discover_phases()`)
2. For each task, check if it has an `Execution Mode` override
3. If override exists, use it; otherwise, inherit phase default

This is the only option that handles mixed-mode phases without artificial phase splitting.

---

## Round 2: Cross-Examination

### 3a challenges 3b

**3a**: You claim YAML frontmatter is "standard across the software ecosystem," but this codebase has zero instances of YAML frontmatter in any tasklist file. Introducing it creates a format divergence that every downstream tool must now handle. The `/sc:tasklist` generator, the sprint runner parser, any future tooling -- all must know about this new convention. What concrete problem does locality solve when the runner ALWAYS reads the index first?

**3b response**: The index-first reading is an implementation detail of the current runner. Future tools may process phase files independently. However, I concede that the current toolchain is index-driven, and introducing YAML frontmatter for a single field is disproportionate.

### 3a challenges 3c

**3a**: You raise the mixed-mode phase scenario. How many real instances of this exist in the codebase? Let me check.

Evidence: Examining the 29 `tasklist-index.md` files in the repository, every phase contains tasks of a uniform type. Phase 1 tasks are all setup/validation. Phase 5 tasks are all adversarial comparisons. Phase 8 tasks are all validation. There is no existing precedent for a phase containing both "run a python script" and "have Claude analyze something" as separate tasks.

The execution_mode concept itself is new -- it does not exist yet. The design question is whether to anticipate mixed-mode phases that have never occurred, or to build for the actual pattern (uniform phases).

**3c response**: The absence of mixed-mode phases today does not prove they will never exist. But I acknowledge that YAGNI (You Aren't Gonna Need It) applies here. If mixed-mode phases become necessary, we can add task-level overrides later.

### 3c challenges 3a

**3c**: If execution_mode is in the index only, the phase file itself has no indication of how it should be run. A human reading `phase-3-tasklist.md` cannot determine its execution mode without consulting the index.

**3a response**: This is true but inconsequential. The phase file is not a standalone document -- it is always consumed in the context of a sprint, which starts from the index. The runner never processes a phase file without first reading the index. Human readability of individual phase files is a secondary concern.

### 3b challenges 3d

**3b**: The dual-level approach introduces inheritance semantics into markdown parsing. How do you handle the case where a phase is marked `python-eligible` in the index but a task overrides to `claude`? The runner would need to parse the full task inventory before it can decide how to launch the phase -- which defeats the timing optimization that motivated phase-level annotation in the first place.

**3d response**: The resolution is that `python-eligible` in the index means "this phase CAN be run in python mode." The runner reads the index, sees the default, and then must parse tasks to check for overrides. This is additional I/O, but only for python-eligible phases. For claude-mode phases (the majority), no task parsing is needed.

However, this means the runner must parse tasks in two places: once to check for overrides (before launch), and once to build the task inventory (during execution). This is a real complexity cost.

### 3d challenges 3a

**3d**: What happens when you need one task in a python phase to use Claude? You would have to split it into a separate phase, breaking the logical grouping.

**3a response**: Correct, but this scenario has not materialized in practice. If it does, we can evolve to 3d at that point. Starting with 3a and evolving to 3d is a clean migration path: add an optional per-task field, make the index column the default, and task-level overrides win. No breaking changes required.

---

## Round 3: Convergence Assessment

### Per-Dimension Scoring Matrix

| Dimension | 3a | 3b | 3c | 3d | Convergence |
|---|---|---|---|---|---|
| 1. Discovery timing | Fully satisfied | Satisfied (extra I/O) | NOT satisfied | Partially satisfied | 3a wins clearly |
| 2. Granularity | Phase-only (sufficient for now) | Phase-only | Task-level (unnecessary) | Both (unnecessary complexity) | 3a sufficient; 3d future-proof |
| 3. Generator compatibility | Trivial | Moderate (new format) | Moderate (per-task) | Compound (both changes) | 3a easiest |
| 4. Parser impact | Minimal (extend Phase dataclass) | Moderate (new frontmatter parser) | Moderate (extend TaskEntry) | High (both parsers + resolution) | 3a least disruption |
| 5. Format consistency | Fully consistent | Inconsistent (YAML in markdown tables world) | Fully consistent | Consistent individually | 3a and 3c both consistent |

### Convergence Score

**Points of agreement** (all advocates converge):
1. The runner MUST know execution_mode before subprocess launch -- timing is non-negotiable (100%)
2. Phase-level granularity is sufficient for all known use cases (75% -- 3c/3d disagree but concede YAGNI)
3. The index file is already the first thing the runner reads (100%)
4. YAML frontmatter is a poor fit for this codebase (75% -- 3b concedes)

**Points of disagreement**:
1. Whether to anticipate mixed-mode phases (3d says yes, others say YAGNI)
2. Whether phase files should be self-describing (3b/3c say yes, 3a says unnecessary)

**Overall convergence**: 82% -- strong consensus around 3a with acknowledged evolution path to 3d.
