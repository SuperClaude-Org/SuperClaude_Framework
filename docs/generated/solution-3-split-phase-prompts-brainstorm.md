# Solution #3: Split Phase Prompts -- Feed Only Relevant Phase Data

## Brainstorm Document

**Date:** 2026-03-15
**Scope:** Sprint executor context exhaustion mitigation
**Status:** Research only -- no implementation

---

## 1. Problem Statement (Grounded in Source)

The sprint executor (`src/superclaude/cli/sprint/process.py`, line 122) builds a prompt via `build_prompt()` that references only the phase file:

```
f"/sc:task-unified Execute all tasks in @{phase_file} "
```

However, the `@{phase_file}` directive causes Claude Code to load the referenced file into context. The phase file itself (e.g., `phase-2-tasklist.md` at 223 lines) is reasonable. The **actual problem** is that the `tasklist-index.md` is NOT directly referenced in the prompt -- but it IS present in the same directory and may be loaded via Claude Code's file-resolution mechanics or via the `/sc:task-unified` command's own context-loading behavior.

**Key measurements from the codebase:**

| File | Lines | Estimated Tokens |
|------|-------|-----------------|
| `tasklist-index.md` (9-phase sprint) | 292 | ~10-12K |
| `tasklist-index.md` (11-phase, 73-task sprint) | 415 | ~14-16K |
| `phase-2-tasklist.md` (cross-framework) | 223 | ~8K |
| `phase-2-tasklist.md` (portify, 7 tasks) | 380 | ~13K |

For the 11-phase portify sprint, Phase 2 alone has 7 tasks across 380 lines (~13K tokens). Combined with the index (~14K), that is ~27K tokens consumed before any execution begins -- 13.5% of the 200K context window gone to static reference material.

**Critical finding:** The `build_prompt()` method (process.py lines 115-157) does NOT reference `tasklist-index.md` at all. The prompt contains only `@{phase_file}`. This means the index may be loaded indirectly by:
1. Claude Code's `@` file resolution scanning adjacent files
2. The `/sc:task-unified` command's internal context-loading logic
3. The agent itself choosing to read the index during execution

This distinction matters for solution design: if the index is loaded by the agent's own initiative (not injected), solutions must prevent the agent from seeking it out, not just stop injecting it.

---

## 2. Implementation Approaches

### Approach A: Simple Substitution -- Phase File Only (No Index Reference)

**Description:** Ensure `tasklist-index.md` is never loaded by the subprocess. Since `build_prompt()` already references only `@{phase_file}`, the fix is to prevent the agent from discovering and loading the index on its own.

**Mechanism:**
- The 4-layer isolation system (executor.py lines 96-172) already restricts the subprocess working directory to `config.release_dir`. The index lives in the same directory as the phase files, so isolation alone does not help.
- Option A1: Set the subprocess working directory to a phase-specific subdirectory containing only the phase file (copy or symlink).
- Option A2: Add an explicit instruction in `build_prompt()`: "Do NOT read tasklist-index.md or any file other than the referenced phase file."
- Option A3: Use file-level isolation -- copy only the phase file into an isolated temp directory and point the subprocess there.

**Token savings:** ~14K per phase (the full index). For an 11-phase sprint, that is ~154K tokens saved across the entire sprint.

**Trade-offs:**
- (+) Simplest change: either a prompt amendment or a directory isolation tweak
- (+) Maximum token savings -- eliminates 100% of index overhead
- (-) Agent loses ALL global context: sprint name, total phases, deliverable registry, traceability matrix
- (-) Agent cannot resolve cross-phase dependency references (e.g., "D-0008 from Phase 2")
- (-) Agent cannot validate artifact paths against the deliverable registry
- (-) Prompt-based instruction ("do not read") is unreliable -- agents may ignore soft directives under context pressure

**Verdict:** Too aggressive. The index contains genuinely useful metadata that phases need. Pure elimination is not viable without compensating context.

---

### Approach B: Phase Context Document -- Phase-Specific Data + Minimal Cross-References

**Description:** Generate a synthetic "phase context" document at sprint startup that contains only the information relevant to each phase, extracted from the full index. Each phase subprocess receives its own tailored context file instead of the full index.

**Mechanism:**
1. At sprint startup (in `load_sprint_config` or a new pre-processing step), parse `tasklist-index.md`
2. For each phase N, generate `phase-N-context.md` containing:
   - Sprint metadata header (name, total phases, current phase number) -- ~200 tokens
   - Phase N's row from the Phase Files table -- ~50 tokens
   - Deliverable registry entries for Phase N's tasks ONLY -- ~200-400 tokens per phase
   - Traceability matrix rows for Phase N's roadmap items ONLY -- ~200-400 tokens per phase
   - Adjacent phase summaries (Phase N-1 outputs, Phase N+1 inputs) -- ~200 tokens
   - Artifact path prefix (TASKLIST_ROOT) -- ~50 tokens
3. Modify `build_prompt()` to reference `@{phase_context_file}` in addition to `@{phase_file}`
4. Optionally: embed the context directly in the prompt string instead of a file reference

**Token budget per phase:**
- Sprint header: ~200 tokens
- Phase-specific deliverable rows: ~300 tokens (for a 4-task phase)
- Phase-specific traceability rows: ~300 tokens
- Adjacent phase summaries: ~200 tokens
- **Total: ~1,000 tokens** vs. the current ~14,000 tokens

**Token savings:** ~13K per phase. For 11 phases: ~143K total savings.

**Trade-offs:**
- (+) Retains all information the agent actually needs for its phase
- (+) Preserves deliverable ID references (D-NNNN) for artifact path resolution
- (+) Preserves traceability for the current phase's roadmap items
- (+) Adjacent phase summaries maintain dependency awareness
- (-) Requires parsing logic to extract sections from the index
- (-) Generated files must be kept in sync if the index is regenerated mid-sprint
- (-) Adds a pre-processing step to sprint startup
- (-) Moderate implementation complexity

**Verdict:** Strong candidate. Best balance of token savings vs. context preservation.

---

### Approach C: Dynamic Prompt Assembly -- Extract Relevant Sections Inline

**Description:** Instead of generating files, dynamically extract relevant sections from `tasklist-index.md` at prompt construction time and embed them directly in the prompt string.

**Mechanism:**
1. In `build_prompt()` (process.py line 115), add a call to a new `extract_phase_context(index_path, phase_number)` function
2. This function reads `tasklist-index.md`, parses it, and returns only:
   - Metadata header (sprint name, TASKLIST_ROOT)
   - Deliverable registry rows matching `T{phase_number:02d}.*`
   - Traceability rows matching the same task ID pattern
3. The extracted text is appended to the prompt string directly (no file reference)
4. The `@{phase_file}` reference remains unchanged

**Token budget:** Same as Approach B (~1,000 tokens per phase).

**Trade-offs:**
- (+) No generated files to manage -- extraction is ephemeral
- (+) Always reads from the current state of the index (no sync issues)
- (+) Prompt string is self-contained -- no additional file references
- (-) Increases prompt string size (but by only ~1K tokens, well within limits)
- (-) Parsing logic must handle index format variations
- (-) Index format changes require parser updates
- (-) Slightly more complex `build_prompt()` method

**Verdict:** Strong candidate. Slightly simpler than Approach B (no file generation) but couples the executor to the index format.

---

### Approach D: Hybrid -- Sprint Summary Header + Phase File Only

**Description:** The lightest-touch approach. Append a compact sprint summary header (~500 tokens) to the prompt string. Do not extract per-phase deliverable rows or traceability data. Rely on the phase file itself (which already contains deliverable IDs, artifact paths, acceptance criteria, and dependencies).

**Mechanism:**
1. In `build_prompt()`, prepend a static sprint summary block:
   ```
   ## Sprint Context
   - Sprint: {sprint_name}
   - TASKLIST_ROOT: {tasklist_root}
   - Total Phases: {total_phases}
   - Current Phase: {phase_number} of {total_phases}
   - Artifact base: {artifact_base_path}
   - Previous phase outputs: {list of prior phase result files}
   ```
2. Keep `@{phase_file}` as the sole file reference
3. Do NOT reference `tasklist-index.md` at all
4. Add an explicit instruction: "All task details, deliverable IDs, artifact paths, and acceptance criteria are contained in the phase file above. Do not seek additional index files."

**Token budget:** ~500 tokens for the summary header.

**Token savings:** ~13.5K per phase (all index overhead eliminated, only 500 tokens added).

**Trade-offs:**
- (+) Minimal implementation change -- a few lines added to `build_prompt()`
- (+) Maximum token savings
- (+) No parsing logic, no generated files, no format coupling
- (+) Phase files already contain everything needed (verified: deliverable IDs, artifact paths, acceptance criteria, dependencies, steps, validation commands are all present in phase-2-tasklist.md)
- (-) Agent loses the deliverable registry cross-reference (but each task already lists its deliverable IDs)
- (-) Agent loses the traceability matrix (but this is a planning artifact, not needed during execution)
- (-) Agent loses the roadmap item registry (also a planning artifact)

**Verdict:** Best option for most cases. The phase files are already self-contained execution documents. The index is primarily a planning/tracking artifact, not an execution artifact.

---

## 3. What Metadata from the Index IS Needed Per Phase?

Analyzing the index structure against what each phase subprocess actually requires:

| Index Section | Lines | Tokens | Needed During Execution? | Already in Phase File? |
|---------------|-------|--------|-------------------------|----------------------|
| Metadata & Artifact Paths | 37 | ~1.2K | Partially (TASKLIST_ROOT, artifact base) | No, but artifact paths are in each task |
| Phase Files table | 12 | ~400 | No (agent only executes its own phase) | No, but phase file is already loaded |
| Source Snapshot | 6 | ~200 | No (planning context) | No |
| Deterministic Rules Applied | 13 | ~500 | No (generator metadata) | No |
| Roadmap Item Registry | 40 | ~1.5K | No (planning traceability) | Task-level roadmap IDs in phase file |
| Deliverable Registry | 40 | ~3K | Partially (artifact paths) | Yes -- each task lists its deliverable IDs and artifact paths |
| Traceability Matrix | 40 | ~3K | No (planning traceability) | Roadmap IDs referenced per-task |
| Execution Log Template | 5 | ~200 | Partially (log path) | No |
| Checkpoint Report Template | 18 | ~600 | Yes (checkpoint format) | Yes -- checkpoint block at end of phase file |
| Feedback Collection Template | 5 | ~200 | No (post-sprint) | No |
| Generation Notes | 15 | ~500 | No (meta) | No |

**Conclusion:** The phase files are remarkably self-contained. Each task block includes:
- Deliverable IDs (e.g., D-0008)
- Artifact paths (full paths in "Artifacts (Intended Paths)" section)
- Acceptance criteria with verification commands
- Dependencies on prior tasks
- Checkpoint blocks with report paths and exit criteria

The only information NOT duplicated in phase files:
1. TASKLIST_ROOT path prefix
2. Overall sprint metadata (name, total phases, complexity class)
3. The execution log path
4. Cross-phase deliverable references (e.g., Phase 3 referencing D-0008 from Phase 2)

Items 1-3 can be injected as a ~200 token header. Item 4 is already handled by the dependency annotations in each task (e.g., "Dependencies: T02.01, T02.02").

---

## 4. Minimum Viable Context Per Phase

Based on the analysis above, the minimum viable context is:

```
## Sprint Context
- Sprint: {config.index_path.parent.name}
- Phase: {phase.number} of {total_phases}
- Artifact Root: {config.release_dir}/artifacts/
- Results Dir: {config.results_dir}
- Execution Log: {config.execution_log_md}
```

That is approximately **100-150 tokens**. Combined with the phase file content (8-13K tokens), this provides everything the agent needs.

**Should we include adjacent phase summaries?**

For phases with cross-phase dependencies (e.g., Phase 3 needs D-0008 from Phase 2), the dependency is already declared in the phase file's task blocks. The agent can resolve artifact paths from the declared deliverable IDs without needing to know Phase 2's full context.

However, for phases that produce inputs consumed by the next phase, a brief "previous phase outputs" line could help:

```
- Previous phase artifacts: artifacts/D-0008/, artifacts/D-0009/, artifacts/D-0010/, artifacts/D-0011/
```

This adds ~50 tokens and provides the agent with awareness of what files exist from prior work. Total minimum viable context: **~200 tokens**.

---

## 5. Implications

### 5.1 Token Savings Quantification

| Scenario | Current Cost | Proposed Cost | Savings Per Phase | Savings (11 phases) |
|----------|-------------|---------------|-------------------|---------------------|
| Approach A (no index) | ~14K | 0 | ~14K | ~154K |
| Approach B (phase context file) | ~14K | ~1K | ~13K | ~143K |
| Approach C (inline extraction) | ~14K | ~1K | ~13K | ~143K |
| Approach D (summary header) | ~14K | ~0.2K | ~13.8K | ~151.8K |

For Phase 2 of the portify sprint (the phase that exhausted context): reducing the index from ~14K to ~0.2K frees approximately **13.8K tokens** -- equivalent to roughly 13 additional tool call round-trips or ~7% of the 200K context window.

### 5.2 Impact on Phase Execution Quality

**Low risk.** The phase files are self-contained execution documents. Every task block includes deliverable IDs, artifact paths, acceptance criteria, verification commands, dependencies, and rollback instructions. The agent does not need the global registry to execute its tasks correctly.

The only quality risk is if the agent attempts to validate cross-phase artifact references (e.g., "check that D-0008 exists before starting T03.01"). This validation is already specified in the task's Steps section (e.g., "[PLANNING] Load context: review D-0008"), so the agent knows what to check without the index.

### 5.3 Impact on Cross-Phase Dependency Awareness

**Minimal.** Cross-phase dependencies are declared in each task's Dependencies field (e.g., "Dependencies: T02.01, T02.02"). The agent does not need the full traceability matrix to understand what must be complete before it starts.

### 5.4 Impact on Checkpoint/Artifact Path Resolution

**None.** Artifact paths are fully specified in each task block:
```
**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/spec.md`
```

Checkpoint report paths are fully specified in the checkpoint blocks:
```
**Checkpoint Report Path:** `.dev/.../checkpoints/CP-P02-END.md`
```

### 5.5 Impact on Sprint Resume Flow

**None.** Sprint resume is handled by the executor (config.py `start_phase` parameter), not by the subprocess. The subprocess does not need to know about other phases to support resume.

---

## 6. Risks

### 6.1 Agent Loses Awareness of Overall Sprint Structure

**Severity:** Low
**Mitigation:** The summary header in Approach D provides phase number and total count. The agent knows it is "Phase 3 of 9" without needing the full index.

### 6.2 Cross-Phase Dependencies Not Visible

**Severity:** Low
**Mitigation:** Dependencies are declared per-task in the phase file. The agent sees "Dependencies: T02.01" and knows to check for that task's output. No global view needed.

### 6.3 Deliverable ID References Broken

**Severity:** Very Low
**Mitigation:** Deliverable IDs are defined per-task in the phase file (e.g., "Deliverable IDs | D-0008"). The deliverable registry in the index is a cross-reference convenience, not the source of truth for individual tasks.

### 6.4 Phase-Specific Files May Not Contain Enough Context

**Severity:** Very Low (verified)
**Evidence:** `phase-2-tasklist.md` (cross-framework) contains 4 complete task blocks, each with: roadmap IDs, effort, risk, tier, confidence, verification method, MCP requirements, artifact paths, deliverables, steps (8 each), acceptance criteria (4+ each), validation commands, dependencies, and a checkpoint block. This is comprehensively self-contained.

### 6.5 Regression in Phase Quality Due to Missing Global Context

**Severity:** Low
**Mitigation:** The "Deterministic Rules Applied" section (generator metadata) and "Generation Notes" (patch history) are not actionable during execution. The "Source Snapshot" is a planning summary. None of these affect task execution quality.

### 6.6 Agent Reads the Index Anyway

**Severity:** Medium
**Mitigation:** This is the most realistic risk. If the agent discovers `tasklist-index.md` in the working directory and reads it for context, we have saved nothing. Mitigations:
1. Prompt instruction: "All required context is in the phase file. Do not read tasklist-index.md."
2. Directory isolation: copy only the phase file to a temp directory (Approach A3)
3. Accept the risk: if the agent reads the index, it costs ~14K tokens but is not catastrophic for phases with fewer tasks

---

## 7. Recommendation

**Recommended approach: Approach D (Hybrid Summary Header) with Approach A3 as a hardening option.**

**Rationale:**

1. **Phase files are already self-contained.** Verified by reading `phase-2-tasklist.md` -- every task has complete execution instructions, deliverable IDs, artifact paths, acceptance criteria, and dependencies. The index adds no actionable information.

2. **Maximum token savings with minimum complexity.** Adding ~5 lines to `build_prompt()` saves ~13.8K tokens per phase. No parsing logic, no generated files, no format coupling.

3. **The prompt already does not reference the index.** The current `build_prompt()` (process.py line 122) uses `@{phase_file}` only. The fix is additive (add a summary header) not subtractive.

4. **Hardening via directory isolation is orthogonal.** If the agent reads the index on its own initiative, Approach A3 (copy phase file to isolated temp dir) can be layered on top without changing the prompt structure.

**Implementation priority:** This is a low-effort, high-impact change. The `build_prompt()` modification is ~10 lines of code. Directory isolation (A3) is ~20 lines. Together they address the largest static token cost in the sprint executor.

**Estimated token savings for the failing scenario:** The portify sprint Phase 2 (7 tasks, 200K context exhausted at turn 106) would recover ~14K tokens (~7% of budget), equivalent to approximately 10-15 additional execution turns. This alone may not prevent exhaustion but combined with Solution #1 (turn budget) and Solution #2 (context compression) creates significant headroom.

---

## 8. Interaction with Other Solutions

| Solution | Interaction with Solution #3 |
|----------|------------------------------|
| #1 (Turn budget management) | Complementary -- #3 reduces base cost, #1 prevents runaway consumption |
| #2 (Context compression) | Complementary -- #3 eliminates static overhead, #2 compresses dynamic growth |
| #4 (Model upgrade to larger context) | Orthogonal -- #3 is beneficial regardless of context window size |
| #5 (Task splitting) | Complementary -- fewer tasks per subprocess means #3's savings are proportionally larger |

**Combined impact estimate:** Solutions #1 + #2 + #3 together could recover 25-40K tokens per phase, increasing the effective execution budget from ~186K to ~210-225K equivalent turns. This should prevent the Phase 2 exhaustion observed at turn 106.

---

## 9. Open Questions for Implementation

1. **How does Claude Code resolve `@{path}` references?** Does it load only the referenced file, or does it scan the directory? If the latter, directory isolation (A3) is essential.

2. **Does `/sc:task-unified` have its own context-loading behavior?** If the slash command loads additional files beyond what `@` provides, the solution must account for that pathway too.

3. **Should the summary header include the execution log path?** The execution log is referenced in the index but not in phase files. If agents are expected to append to it, the path must be provided.

4. **Should prior phase result files be listed?** For phases that depend on prior work (e.g., Phase 3 checking D-0008 from Phase 2), listing the artifact directories from prior phases (~50 tokens) could help the agent locate inputs without reading the index.

5. **Is the checkpoint report template needed?** Phase files already include checkpoint blocks with paths and criteria. The template in the index is redundant with the phase-level checkpoint blocks.
