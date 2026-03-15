# Solution #4: Artifact Batching -- Separate Implementation from Documentation

## Problem Statement

The sprint executor runs each phase as a single Claude Code subprocess. The subprocess prompt (built by `ClaudeProcess.build_prompt()` in `src/superclaude/cli/sprint/process.py`) instructs the agent to execute all tasks AND write completion documentation within the same session. For Phase 2 of the CLI Portify sprint, this means:

- 7 implementation tasks (T02.01 through T02.07), each with code + tests
- 7 artifact specification documents (D-0005 through D-0011)
- 2 checkpoint files (CP-P02-T01-T04.md, CP-P02-END.md)
- 1 completion report (phase-2-result.md)

The implementation work succeeded (192 tests passing, all code written). The crash occurred at turn 106 with "Prompt is too long" while writing the final completion report. The 10 documentation files are pure bookkeeping -- they record what was done, not do new work.

### Quantitative Context

Examining existing artifacts from the cross-framework-deep-analysis sprint:

| Artifact Type | Count (Phase 2) | Typical Size | Total Bytes |
|---|---|---|---|
| spec.md / evidence.md / notes.md | 7 | 1.5-22 KB | ~87 KB total across 16 artifacts |
| Checkpoint reports | 2 | ~2 KB each | ~4 KB |
| Completion report | 1 | ~3 KB | ~3 KB |

Each artifact write requires the agent to: recall implementation details, formulate structured markdown with YAML frontmatter, invoke the Write tool, and verify the file was created. At ~160K tokens of accumulated context, each additional tool call and response adds to the problem exponentially.

---

## Approach A: Post-Phase Artifact Writer Subprocess

### Description

After the phase subprocess completes (exits 0), the executor spawns a NEW, fresh subprocess dedicated exclusively to writing artifacts. This subprocess receives a purpose-built prompt containing: (1) the list of artifacts to produce, (2) the phase tasklist as reference, and (3) a summary of task outcomes extracted from the phase output.

### Mechanism

In `executor.py`, after the main phase subprocess finishes and `_determine_phase_status()` returns a success status, insert a new stage:

```
Phase subprocess (implementation) -> exit 0
    |
    v
Executor extracts task outcome summary from output/result files
    |
    v
Artifact writer subprocess (fresh context, ~0 tokens consumed)
    -> Reads phase tasklist file
    -> Reads task outcome summary
    -> Writes D-00XX/spec.md for each deliverable
    -> Writes checkpoint files
    -> Writes completion report (phase-N-result.md)
```

### Architectural Implications

1. **New execution stage**: The `execute_sprint()` loop in `executor.py` (lines 490-763) currently treats each phase as a single subprocess. This approach adds a second subprocess per phase, requiring a new concept: "phase implementation" vs "phase documentation."

2. **Prompt construction**: Requires a new `build_artifact_prompt()` method on `ClaudeProcess` or a separate `ArtifactWriterProcess` class. The prompt must include:
   - The phase tasklist file path (so the agent can read deliverable requirements)
   - The aggregated task results (from `AggregatedPhaseReport`)
   - The artifact output paths (from tasklist "Artifacts (Intended Paths)" sections)

3. **Result file ownership**: Currently, the completion report (`phase-N-result.md`) is expected to be written by the phase subprocess itself, and `_determine_phase_status()` reads it. If the artifact writer is responsible for the completion report, the status determination logic must be restructured -- either the executor writes the result file from `AggregatedPhaseReport.to_markdown()` (which it already can do), or the artifact writer produces it.

4. **Turn budget**: The artifact writer subprocess needs its own turn budget allocation. Based on artifact sizes (7 documents averaging ~5 KB each, plus 3 smaller files), a budget of 15-25 turns should suffice. The `TurnLedger` in `models.py` already supports `debit()`/`credit()` operations, so allocating a reserved artifact budget is straightforward.

### Trade-offs

| Dimension | Assessment |
|---|---|
| Context exhaustion risk | Eliminated -- fresh subprocess has full 200K context budget |
| Artifact quality | Moderate risk -- writer lacks lived implementation context; must reconstruct from summaries |
| Execution time | +3-8 minutes per phase (subprocess startup + artifact writing) |
| API cost | +15-25 additional turns per phase at model cost |
| Complexity | Moderate -- new subprocess type, new prompt builder, modified execution loop |
| Reliability | High -- artifact writing is deterministic and low-risk; failures are recoverable |

### Key Risk: Context Loss

The artifact writer subprocess has never seen the implementation code. It must reconstruct artifact content from:
- The phase tasklist (describes what should have been done)
- The aggregated task results (describes what was done)
- The actual source files on disk (the agent can read them)

For spec-style artifacts (like D-0005 through D-0011), this is actually fine -- the agent reads the implemented code and documents it. The artifact is a record of what exists, not a creative product. For evidence-style artifacts, the agent can run the test commands listed in acceptance criteria and capture results.

---

## Approach B: Inline Artifact Batching with Context Checkpointing

### Description

Instead of deferring all artifacts to the end, write each artifact immediately after completing the task that produces its deliverable. After each artifact write, the executor could theoretically checkpoint and restart with compressed context -- but Claude Code subprocesses do not support mid-session context compression.

### Realistic Variant: Interleave Artifacts with Tasks

Modify the phase prompt to instruct the agent to write each D-00XX artifact immediately after completing its corresponding task, rather than batching all artifacts at the end.

### Mechanism

Change `build_prompt()` in `process.py` to include an instruction like:
```
After completing each task, IMMEDIATELY write its deliverable artifact
before moving to the next task. Do not defer artifact writing.
```

### Architectural Implications

1. **No executor changes**: This is a prompt-only change. The executor loop is unmodified.

2. **Context distribution**: Artifact writes are spread across the session, consuming tokens incrementally rather than as a burst at the end. If each artifact costs ~500-1000 tokens of tool interaction, 7 artifacts add ~7000 tokens distributed across the session instead of 7000 tokens at the end when budget is exhausted.

3. **Ordering dependency**: Some artifacts reference content from later tasks. For example, CP-P02-END.md (end-of-phase checkpoint) cannot be written until all 7 tasks complete. This approach only works for per-task artifacts (D-00XX), not for cross-task documents (checkpoints, completion reports).

### Trade-offs

| Dimension | Assessment |
|---|---|
| Context exhaustion risk | Reduced but NOT eliminated -- checkpoints and completion report still must be written at the end |
| Artifact quality | High -- written with full implementation context still fresh |
| Execution time | No change -- same subprocess |
| API cost | No change -- same turn count |
| Complexity | Low -- prompt modification only |
| Reliability | Medium -- agent may forget or skip artifact writes under cognitive load |

### Key Risk: Partial Solution

This approach distributes 7 of the 10 documents but still requires 3 documents (2 checkpoints + 1 completion report) at the end. The crash at turn 106 occurred writing the completion report -- so this approach reduces but does not eliminate the failure mode. It also adds token consumption earlier in the session, potentially causing the crash to happen sooner if the total token budget is the binding constraint rather than the timing of writes.

---

## Approach C: Deferred Artifact Generation via Metadata Collection

### Description

During implementation, the agent collects structured metadata about each completed task (status, files modified, test evidence, key decisions) into a lightweight manifest file. After the phase subprocess exits, a separate artifact generation pass reads the manifest and produces the full artifact documents.

### Mechanism

```
Phase subprocess (implementation):
    For each task:
        1. Execute implementation
        2. Append structured YAML record to .artifacts-manifest.yaml:
           - task_id, status, files_modified, test_command, test_result
           - deliverable_id, artifact_type (spec|evidence|notes)
           - key_decisions (1-2 sentences)
    -> exit 0

Executor:
    1. Read .artifacts-manifest.yaml
    2. Spawn artifact generator subprocess:
       - Reads manifest + phase tasklist
       - For each deliverable in manifest:
           - Reads referenced source files
           - Generates artifact document
       - Writes checkpoints and completion report
```

### Architectural Implications

1. **New data type**: `ArtifactManifest` dataclass in `models.py` capturing per-task metadata. This is distinct from `TaskResult` because it includes implementation-specific details (files modified, decisions made) that the executor does not currently track.

2. **Two-stage prompt**: The implementation prompt must include instructions to emit manifest entries. The artifact generation prompt must include the manifest and artifact templates.

3. **Manifest as contract**: The manifest becomes a formal interface between the implementation stage and the documentation stage. Its schema must be versioned and validated.

4. **Similarity to AggregatedPhaseReport**: The existing `AggregatedPhaseReport` in `executor.py` (lines 179-282) already aggregates task outcomes runner-side. The manifest extends this concept with implementation-specific details that only the agent knows (key decisions, design rationale).

### Trade-offs

| Dimension | Assessment |
|---|---|
| Context exhaustion risk | Eliminated -- artifact generation runs in fresh subprocess |
| Artifact quality | Good -- manifest captures key context; generator can read source files |
| Execution time | +5-10 minutes (manifest parsing + artifact generation) |
| API cost | +20-30 turns (artifact generation subprocess) |
| Complexity | High -- new data type, manifest schema, two-stage protocol |
| Reliability | Medium -- manifest completeness depends on agent discipline |

### Key Risk: Manifest Completeness

If the agent forgets to record a decision or omits a file path from the manifest, the artifact generator will produce incomplete documents. The manifest itself is a cognitive burden on the agent during implementation -- exactly when it should be focused on code.

Mitigation: The executor can supplement the manifest with git-derived data (`git diff --stat` since phase start, `git log --oneline` for commit messages). This provides a safety net for file-change tracking even if the agent omits entries.

---

## Approach D: Reduced Artifact Verbosity -- Structured Data Instead of Prose

### Description

Replace full prose spec.md/evidence.md documents with minimal structured YAML or JSON artifacts. Instead of a 372-line spec.md (like D-0008), emit a 30-line YAML file with machine-readable fields.

### Mechanism

Each artifact becomes a structured record:

```yaml
deliverable: D-0005
task: T02.01
title: Workflow Path Resolution
status: complete
files_modified:
  - src/superclaude/cli/cli_portify/config.py
  - tests/cli_portify/test_config.py
test_command: "uv run pytest tests/ -k test_workflow_path"
test_result: PASS
acceptance_criteria_met:
  - path_resolution: true
  - ambiguous_path_error: true
  - invalid_path_error: true
  - unit_tests_pass: true
key_decisions:
  - "Used pathlib.Path for all path operations"
```

### Architectural Implications

1. **Artifact format change**: All downstream consumers of artifact documents must accept YAML instead of Markdown. This affects: checkpoint verification logic, phase status determination, and any human review workflows.

2. **Token cost reduction**: A 30-line YAML artifact costs ~200 tokens to write vs ~2000 tokens for a prose spec.md. For 7 artifacts, this saves ~12,600 tokens -- potentially enough to avoid the context exhaustion entirely.

3. **No executor changes**: This is a prompt modification. The executor does not parse artifact content (it only checks for result files via `_determine_phase_status()`).

4. **Reversibility**: YAML artifacts can be expanded into prose documents later via a separate generation pass, making this compatible with Approach A as a two-stage process.

### Trade-offs

| Dimension | Assessment |
|---|---|
| Context exhaustion risk | Significantly reduced -- 85-90% fewer tokens per artifact |
| Artifact quality | Lower for human readability; higher for machine consumption |
| Execution time | Reduced -- less writing per artifact |
| API cost | Reduced -- fewer tokens generated |
| Complexity | Low -- prompt modification only |
| Reliability | High -- YAML is simpler to produce than prose |

### Key Risk: Loss of Human-Readable Documentation

The existing artifacts serve as human-readable records of architectural decisions, implementation rationale, and verification evidence. Converting to YAML loses narrative context. The D-0008 spec.md (22 KB, 372 lines) contains rich interface documentation, dependency analysis, and system quality assessments that a 30-line YAML cannot capture.

Mitigation: Use YAML for the sprint execution artifacts (ensuring the sprint does not crash) and generate expanded prose documents in a post-sprint documentation pass.

---

## Approach E: Configurable Artifact Writing (Optional/Deferred)

### Description

Make artifact writing a configurable behavior in the sprint executor. By default, artifacts are deferred to a separate pass. Users can opt in to inline artifact writing with a flag like `--inline-artifacts`.

### Mechanism

Add to `SprintConfig`:
```python
artifact_mode: str = "deferred"  # "deferred" | "inline" | "none"
```

- `"deferred"`: Artifacts written in a post-phase subprocess (Approach A)
- `"inline"`: Artifacts written within the implementation subprocess (current behavior)
- `"none"`: No artifacts written; only the result file is produced

The CLI exposes this as `--artifact-mode deferred|inline|none`.

### Architectural Implications

1. **Config extension**: New field on `SprintConfig` (which extends `PipelineConfig`). Backward compatible -- defaults to `"deferred"`.

2. **Prompt branching**: `build_prompt()` must conditionally include or exclude artifact-writing instructions based on `config.artifact_mode`.

3. **Executor branching**: `execute_sprint()` must conditionally spawn the artifact writer subprocess when `artifact_mode == "deferred"`.

4. **Resume interaction**: If artifact writing fails in deferred mode, the executor can retry the artifact pass without re-executing the implementation. This requires tracking "implementation complete" vs "artifacts complete" separately (see Architecture Questions below).

### Trade-offs

| Dimension | Assessment |
|---|---|
| Context exhaustion risk | Eliminated in deferred mode; present in inline mode (user choice) |
| Artifact quality | User-selectable trade-off |
| Execution time | Configurable |
| API cost | Configurable |
| Complexity | Moderate -- config extension + conditional logic in executor and prompt builder |
| Reliability | High -- user can fall back to inline if deferred produces poor artifacts |

---

## Cross-Cutting Implications Analysis

### 1. Impact on Sprint Execution Time

| Approach | Time Delta | Explanation |
|---|---|---|
| A (post-phase writer) | +3-8 min/phase | Subprocess startup (~30s) + artifact writing (~2-7 min) |
| B (inline batching) | +0 min | Same subprocess, redistributed work |
| C (manifest + generator) | +5-10 min/phase | Manifest parsing + more complex generation |
| D (reduced verbosity) | -2-5 min/phase | Less writing overall |
| E (configurable) | Varies | Depends on selected mode |

For a 9-phase sprint, Approach A adds 27-72 minutes total. This is acceptable for a sprint that runs 6-12 hours.

### 2. Impact on Artifact Quality

The central question: does a subprocess that never performed the implementation produce worse artifacts?

**Arguments for acceptable quality:**
- Artifacts document what IS, not what was THOUGHT. The source code and test results exist on disk; the artifact writer can read them.
- The phase tasklist contains detailed acceptance criteria, deliverable descriptions, and intended artifact paths. This provides strong structure.
- The existing D-0005 through D-0014 artifacts are primarily factual records (file paths, interface lists, dependency mappings), not creative prose. Factual content can be reconstructed from source.

**Arguments for quality degradation:**
- Decision records (like D-0005 "OQ-006 Decision Record") capture rationale that exists only in the implementation agent's reasoning. A post-hoc writer would have to infer rationale from outcomes.
- Evidence artifacts (like D-0007 evidence.md) record the specific verification steps taken. A post-hoc writer would need to re-run verification commands rather than recording them in real time.
- Nuanced observations (like the OQ-008 annotation in D-0008) arise from the agent's experience during implementation and may not surface in a cold review.

**Assessment:** For 80-90% of artifact content (factual records, file listings, test results), quality will be equivalent. For 10-20% (decision rationale, nuanced observations), quality may degrade. Approach C (manifest) partially mitigates this by capturing key decisions during implementation.

### 3. Impact on Sprint Executor Architecture

All approaches except B require changes to the executor architecture:

| Component | Current | After Approach A | After Approach C |
|---|---|---|---|
| Phase lifecycle | 1 subprocess | 2 subprocesses (impl + docs) | 2 subprocesses (impl + docs) |
| PhaseStatus | Single status | Needs impl_status + docs_status | Needs impl_status + docs_status |
| Result determination | Reads result file from phase subprocess | Reads result from executor-generated report OR artifact writer | Reads from manifest + artifact writer |
| Resume flow | Re-run entire phase | Can re-run only artifact pass | Can re-run only artifact pass |

### 4. Impact on Resume Flow

This is a significant architectural benefit. Currently, if artifact writing crashes at turn 106, the ENTIRE phase must be re-executed (all 7 implementation tasks + tests). With separated stages:

- Implementation completes and exits 0 -> executor records implementation as PASS
- Artifact writer crashes -> executor records artifacts as INCOMPLETE
- Resume: `superclaude sprint run --start 2 --artifact-only` re-runs only the artifact pass

This requires the executor to persist per-phase stage completion, which the current `PhaseResult` does not track.

### 5. Impact on Cost

| Approach | Additional API Turns | Estimated Cost Delta |
|---|---|---|
| A | 15-25/phase | ~$0.50-1.50/phase (Opus pricing) |
| B | 0 | $0.00 |
| C | 20-30/phase | ~$0.75-2.00/phase |
| D | -5-10/phase (fewer tokens generated) | -$0.25-0.50/phase |
| E | Depends on mode | Variable |

---

## Risk Analysis

### R1: Artifact Writer Lacks Implementation Context (Approaches A, C, E)

**Severity:** Medium
**Probability:** High (guaranteed for some artifact types)
**Mitigation:**
- Supply the artifact writer with: phase tasklist, aggregated task results, git diff summary, and the actual source files on disk.
- For decision records, capture key decisions in the manifest (Approach C) or in commit messages.
- Accept that some rationale may be lost; this is an acceptable trade-off vs. crashing entirely and producing NO artifacts.

### R2: Double-Spending on Context Loading (Approaches A, C)

**Severity:** Low
**Probability:** High
**Explanation:** The artifact writer subprocess must load the phase tasklist and read source files, which the implementation subprocess already read. This duplicates ~5-15K tokens of context loading.
**Mitigation:** This is inherent to subprocess isolation and unavoidable. The cost is small relative to the 200K context budget of the fresh subprocess.

### R3: Increased Executor Complexity (All approaches except B)

**Severity:** Medium
**Probability:** High
**Mitigation:**
- Encapsulate artifact writing in a dedicated class (`ArtifactWriter`) with a clean interface.
- Keep the executor loop simple: `run_implementation() -> run_artifacts() -> determine_status()`.
- Add integration tests covering the two-stage flow.

### R4: Artifact Quality Degradation (Approaches A, C, D)

**Severity:** Medium (D is High)
**Probability:** Medium
**Mitigation:**
- For Approaches A/C: Provide rich context (tasklist + results + source files).
- For Approach D: Use YAML as intermediate format; generate prose in a post-sprint pass.
- Validate artifact completeness by checking required fields/sections.

### R5: New Failure Mode -- Artifact Subprocess Fails (Approaches A, C, E)

**Severity:** Low
**Probability:** Low (artifact writing is simpler than implementation)
**Explanation:** The artifact writer has a fresh 200K context budget and only needs to write ~10 files. This is well within budget.
**Mitigation:**
- Set a generous turn budget (25-30 turns) for the artifact writer.
- If the artifact writer fails, the implementation is still preserved. The executor can retry or the user can write artifacts manually.
- Track artifact completion separately from implementation completion.

### R6: Ordering Issues -- Artifacts Needed by Next Phase (Approaches A, C)

**Severity:** High
**Probability:** Medium
**Explanation:** If Phase 3 depends on Phase 2's artifact documents (e.g., D-0008 spec.md is referenced by Phase 3 tasks), the artifacts must be written before Phase 3 begins.
**Mitigation:**
- The artifact writer subprocess runs BEFORE the next phase starts. The executor's sequential phase loop (`for phase in config.active_phases`) already enforces this ordering.
- The executor must wait for the artifact writer to complete before advancing to the next phase.
- This is the natural flow: implementation subprocess -> artifact writer subprocess -> next phase.

### R7: Agent Ignores Manifest Instructions (Approach C)

**Severity:** Medium
**Probability:** Medium
**Explanation:** The agent may not reliably append structured YAML to a manifest file during implementation, especially under cognitive load.
**Mitigation:**
- Make the manifest format extremely simple (task_id, status, files list).
- Supplement with executor-derived data (git diff, test exit codes) so the manifest is not the sole source of truth.
- Fall back to Approach A (no manifest, just tasklist + source files) if manifest is incomplete.

---

## Architecture Questions and Recommendations

### Q1: Should artifact writing be a first-class concept in the sprint executor?

**Recommendation: Yes.**

The current architecture conflates implementation and documentation into a single subprocess, which creates an inherent scalability ceiling. As phase complexity grows (more tasks, more deliverables), context exhaustion during artifact writing will become increasingly common. Making artifact writing a first-class concept -- with its own subprocess, prompt, turn budget, and completion tracking -- creates a clean separation of concerns and eliminates the ceiling.

The relevant insertion point is in `execute_sprint()` at line 694 (after `logger.write_phase_result(phase_result)` and before the continue/halt decision). The artifact writer subprocess would run here, between phase completion and the next phase.

### Q2: Should the executor track "implementation complete" vs "artifacts complete" separately?

**Recommendation: Yes.**

The `PhaseResult` dataclass in `models.py` (lines 347-373) should be extended with:
- `impl_status: PhaseStatus` -- status of the implementation subprocess
- `artifacts_status: PhaseStatus` -- status of the artifact writer subprocess (PENDING if not yet run)

The overall `status` property would derive from both: PASS only if both are PASS; FAIL if impl failed; INCOMPLETE if impl passed but artifacts failed.

This enables targeted resume: `--resume-artifacts-only` re-runs only the artifact pass for phases where implementation succeeded but artifact writing failed.

### Q3: How does this interact with checkpoint cadence rules?

The phase tasklist defines mid-phase checkpoints (e.g., CP-P02-T01-T04.md after the first 4 tasks). Currently, these are written by the implementation subprocess at the appropriate point. With artifact batching:

- **Option 1:** Mid-phase checkpoints are still written inline (by the implementation subprocess) since they occur mid-execution. Only end-of-phase checkpoints and deliverable artifacts are deferred.
- **Option 2:** All checkpoints are deferred to the artifact writer. This is simpler but means mid-phase checkpoints are written after all tasks complete, losing their real-time value.

**Recommendation:** Option 1. Mid-phase checkpoints serve as progress markers and should be written in real time. End-of-phase checkpoints and deliverable artifacts are deferred.

### Q4: Can we leverage the existing result file as context for artifact generation?

**Yes, and this is the key enabler for Approach A.**

The `AggregatedPhaseReport` class (executor.py lines 179-282) already produces structured YAML and Markdown output from `TaskResult` data. Its `to_markdown()` method generates a complete phase report with per-task status, turns consumed, and EXIT_RECOMMENDATION.

The artifact writer's prompt should include:
1. The `AggregatedPhaseReport.to_markdown()` output (task outcomes)
2. The phase tasklist file path (deliverable requirements, acceptance criteria)
3. The list of artifact paths to produce (parsed from tasklist "Artifacts (Intended Paths)" sections)
4. A git diff summary since phase start (files actually modified)

This provides sufficient context for the artifact writer to produce high-quality documents without a manifest.

---

## Recommended Solution: Hybrid A+D with E's Configurability

### Summary

Combine Approach A (post-phase artifact writer) with Approach D (reduced verbosity for artifact metadata) and Approach E (configurable behavior):

1. **Default mode (`artifact_mode="deferred"`):** After the implementation subprocess exits 0, the executor spawns a fresh artifact writer subprocess. The writer receives the AggregatedPhaseReport, the phase tasklist path, and the artifact output paths. It reads source files as needed and produces deliverable artifacts.

2. **Artifact format:** Artifacts are written as Markdown with YAML frontmatter (current format) but are structurally guided by the acceptance criteria in the tasklist. The writer does NOT attempt to reproduce decision rationale that it never witnessed -- it documents what EXISTS (code, tests, interfaces) rather than what was THOUGHT.

3. **Completion report ownership:** The executor writes `phase-N-result.md` from `AggregatedPhaseReport.to_markdown()` BEFORE spawning the artifact writer. This decouples status determination from artifact writing entirely. The `_determine_phase_status()` function reads the executor-written result file, not an agent-written one.

4. **Configurability:** `--artifact-mode inline|deferred|none` allows users to choose. Default is `deferred`. `inline` restores current behavior for phases with few artifacts. `none` skips artifacts entirely for rapid iteration.

5. **Resume support:** `PhaseResult` tracks `impl_status` and `artifacts_status` independently. Failed artifact writing can be retried without re-running implementation.

### Why Not the Other Approaches

- **Approach B (inline batching):** Reduces but does not eliminate the problem. The completion report and end-of-phase checkpoint still must be written at the end. Not a complete solution.

- **Approach C (manifest):** Adds complexity (new data type, schema, agent instruction burden) without proportional benefit over Approach A. The executor's `AggregatedPhaseReport` plus git diff provides most of the manifest's value without requiring agent cooperation during implementation.

- **Approach D alone:** Sacrifices human-readable documentation. Acceptable as a component of the hybrid but not as the sole solution.

### Implementation Priority

1. **Executor writes result file** (decouples status from agent artifact writing) -- smallest change, highest impact
2. **Post-phase artifact writer subprocess** (Approach A core) -- eliminates context exhaustion
3. **`--artifact-mode` configuration** (Approach E) -- user control
4. **Independent impl/artifact status tracking** (resume support) -- operational resilience

### Files to Modify

| File | Change |
|---|---|
| `src/superclaude/cli/sprint/executor.py` | Add artifact writer subprocess spawn after phase completion; executor writes result file from AggregatedPhaseReport |
| `src/superclaude/cli/sprint/process.py` | Add `build_artifact_prompt()` method or new `ArtifactWriterProcess` class |
| `src/superclaude/cli/sprint/models.py` | Extend `PhaseResult` with `impl_status`/`artifacts_status`; add `artifact_mode` to `SprintConfig` |
| `src/superclaude/cli/sprint/commands.py` | Add `--artifact-mode` CLI option |
| `tests/sprint/` | Integration tests for two-stage phase execution |
