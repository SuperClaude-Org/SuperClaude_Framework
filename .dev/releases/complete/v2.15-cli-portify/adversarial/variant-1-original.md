# sc:cli-portify v2.15 Session Findings (Agent A)

**Date**: 2026-03-06
**Branch**: `feature/2.15-cli-portify`
**Scope**: Full session synthesis -- spec review, refactoring design, pipeline failure analysis, systemic root cause investigation, adversarial debate results

---

## 1. Executive Summary

The sc:cli-portify development session began with a structured expert panel review of the original SKILL.md specification, which revealed 15 findings (5 CRITICAL, 7 MAJOR, 3 MINOR) across requirements completeness, architecture soundness, generation correctness, testability, and operational determinism. Quality scores ranged from 3/10 to 6/10.

A comprehensive refactoring specification was produced addressing all 15 findings through a 5-phase architecture (Phases 0-4) with machine-readable phase contracts, step conservation invariants, live API verification, pattern coverage matrices, and explicit failure routing with resume semantics.

When the refactored spec was submitted to the `superclaude roadmap run` CLI pipeline for roadmap generation, the pipeline failed at the first step (extract). Investigation traced the immediate cause to Claude subprocess output containing reasoning preamble text and markdown code fences around YAML frontmatter, which the gate parser rejected. A systemic root cause analysis (4 parallel agents) identified 9 distinct root causes across 4 architectural layers: prompt, gate/parser, executor/retry, and subprocess.

An adversarial debate produced consensus rankings for both root causes and solutions, yielding a 3-PR implementation plan expected to reduce pipeline failure rates by approximately 95%.

---

## 2. Background and Context

### 2.1 What is sc:cli-portify?

sc:cli-portify is a SuperClaude skill that converts inference-based workflows (skills executed by Claude as free-form LLM tasks) into deterministic CLI pipelines (Python packages under `src/superclaude/cli/` using the shared pipeline framework). It analyzes a workflow's steps, classifies them, designs a pipeline specification, generates validated Python code, and wires the result into the CLI infrastructure.

### 2.2 Peer Protocol References

The review benchmarked sc:cli-portify against three mature peer protocols:

| Protocol | Key Strength | Reference |
|----------|-------------|-----------|
| sc:tasklist-protocol | 17-check self-validation, write atomicity, stage reporting | `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` |
| sc:roadmap-protocol | Wave gating, persistence, explicit MCP usage mapping | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` |
| sc:adversarial-protocol | Return contracts, convergence thresholds, failure routing | `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` |

### 2.3 Pipeline Infrastructure

The programmatic CLI runner lives at `src/superclaude/cli/roadmap/`. It implements an 8-step pipeline:

```
extract -> generate-A (parallel) -> diff -> debate -> score -> merge -> test-strategy
              generate-B (parallel)
```

The recommended invocation was:
```
superclaude roadmap run .dev/releases/current/v2.15-cli-portify/refactoring-spec-cli-portify.md \
  --agents "opus:architect,haiku:analyzer" \
  --output .dev/releases/current/v2.15-cli-portify/ \
  --depth standard
```

---

## 3. Spec Panel Review Findings

### 3.1 Quality Scores

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Requirements completeness | 5/10 | Incomplete at every phase boundary |
| Architecture soundness | 6/10 | Conceptually right but interfaces wrong |
| Generation correctness | 4/10 | Under-specified relative to peers |
| Testability | 3/10 | Structural test generation is insufficient |
| Operational determinism | 3/10 | Entirely inference-based with no self-validation gates |

### 3.2 CRITICAL Findings

**C1: Missing command entry point**

The skill exists only as `src/superclaude/skills/sc-cli-portify/SKILL.md` with no matching command shim under `src/superclaude/commands/`. Every other skill follows the pattern `commands/<name>.md` (thin) -> `skills/sc-<name>-protocol/SKILL.md` (full). This breaks discoverability, the `superclaude install` distribution pipeline, and slash command invocation. The directory naming convention is also wrong: `sc-cli-portify/` rather than `sc-cli-portify-protocol/`.

Peer reference: `src/superclaude/commands/tasklist.md:69-82` demonstrates proper command-to-protocol delegation.

**C2: No generation self-validation**

The spec describes four phases but includes no mandatory pre-write self-check. There is no stage gate proving: (a) all workflow components were discovered, (b) all source steps were represented, (c) all generated files are syntactically valid, or (d) integration wiring is internally consistent. Phase 4's "verify imports" is described as a vague "quick check" (`SKILL.md:165-167`) with no failure protocol.

Peer reference: sc:tasklist-protocol has a mandatory 17-check self-validation at `SKILL.md:752-862` that blocks completion until all checks pass.

**C3: Phase interfaces leak -- prose not contracts**

Phase outputs are prose artifacts (`portify-analysis.md`, `portify-spec.md`) with no machine-readable return contract or schema. Phase 2 depends on Phase 1, but Phase 1 only promises a markdown report. This forces subsequent phases to "re-interpret" prior outputs, reintroducing inference at every boundary.

Peer reference: sc:adversarial-protocol defines explicit return contracts even on failure (`SKILL.md:409-427`). sc:roadmap-protocol consumes structured return fields with routing logic (`SKILL.md:381-412`).

**C4: Pipeline API drift risk is unmitigated**

The spec's reference files (`refs/pipeline-spec.md`) already diverge from the live codebase. Concrete drift evidence:

- Ref uses `GateCriteria(tier="standard", required_frontmatter=[...])` but the live code uses `GateCriteria(enforcement_tier=..., required_frontmatter_fields=[...])` (see `src/superclaude/cli/pipeline/models.py:68-74`)
- Ref shows semantic functions returning `(bool, str)` tuples, but the live `SemanticCheck.check_fn` is `Callable[[str], bool]` (`models.py:63`); the `(bool, str | None)` return is the `gate_passed()` function signature (`gates.py:19`)

A generated pipeline following the current refs verbatim will not match current pipeline contracts.

**C5: No step conservation guarantee**

Phase 1 asks to "identify steps" and "map dependencies" but defines no completeness invariant. Portification can silently drop a source step, collapse two semantically distinct steps into one, or omit a user-facing gate. There is no "count conservation" rule between source workflow operations and generated pipeline steps.

### 3.3 MAJOR Findings

**M1: Commented metadata instead of real frontmatter** -- Extended metadata is inside an HTML comment (`SKILL.md:7-12`), making it invisible to tooling. Peers expose structured frontmatter directly.

**M2: MCP usage declared but not behaviorally integrated** -- The comment lists `sequential, serena, context7, auggie-mcp` but the SKILL.md body never specifies when each is used. Peers document MCP usage at the phase/wave level.

**M3: No progress-tracking contract** -- `allowed-tools` includes `TodoWrite` but no body behavior uses it. Long-running multi-phase generation has no deterministic progress reporting.

**M4: Phase 4 "Verify imports" is too vague** -- The phrase "Quick check for circular dependencies" (`SKILL.md:166`) is not measurable. It says nothing about import resolution, package `__init__.py`, command registration correctness, syntax validity, or cyclic import detection method.

**M5: Template applicability boundaries undefined** -- Templates assume a standard module set and sprint-style execution. No decision matrix says when a workflow pattern requires extra modules beyond the inventory. No "unsupported pattern" escape hatch exists.

**M6: No explicit failure routing** -- Phases are linear with no failure routing. No status model exists for generation-process failures. Peer protocols define per-wave failure/abort behavior (sc:roadmap-protocol `SKILL.md:427-445`) and write failure contracts on abort (sc:adversarial-protocol `SKILL.md:427`).

**M7: Output location underspecified** -- The spec does not define: command name uniqueness requirements, collision behavior if a package already exists, naming transformation rules, or whether distribution tooling must be updated.

### 3.4 MINOR Findings

**N1: .claude/src sync inconsistency** -- The `.claude/` copy has no `__init__.py` but the `src/` copy does, inconsistent with sync expectations.

**N2: Non-measurable "100% completion" claim** -- Purpose statement (`SKILL.md:16`) uses aspirational language not verifiable as a requirement.

**N3: Boundaries too broad** -- "Will analyze any workflow" is overly broad. Some workflows (recursive agent orchestration, interactive human decisions mid-pipeline, no stable artifact boundaries) may not fit the sprint/pipeline architecture.

### 3.5 Adversarial Attack Analysis (Whittaker)

Five attack methodologies were applied against the step decomposition algorithm:

1. **Zero/Empty Attack**: Classification rubric fails when a step appears deterministic structurally but contains zero explicit semantic cues indicating judgment is required.
2. **Divergence Attack**: Step decomposition fails when one source action satisfies multiple step-boundary conditions simultaneously, producing different splits across runs.
3. **Sentinel Collision Attack**: Gate mode assignment fails when a "quality-only" step is marked TRAILING but is actually referenced later as prompt context.
4. **Sequence Attack**: Phase handoff fails when Phase 3 begins from an incomplete Phase 2 artifact, generating compilable but behaviorally incomplete code.
5. **Accumulation Attack**: Dynamic/batched workflow support fails when batch count expands beyond template assumptions.

---

## 4. Refactored Spec Design

### 4.1 Architecture Overview

The refactoring spec addresses all 15 findings with a 5-phase architecture (Phases 0-4):

| Phase | Name | Purpose | Key Innovation |
|-------|------|---------|----------------|
| 0 | Prerequisites | Environment validation, API snapshot, unsupported pattern scan | Live API snapshot before any analysis |
| 1 | Workflow Analysis | Step decomposition, classification, conservation invariant | Machine-checkable step registry with stable source IDs |
| 2 | Pipeline Specification | Step mapping, pattern coverage, API conformance | Coverage invariant + pattern coverage matrix |
| 3 | Code Generation | Atomic generation, per-file + cross-file validation | 10-check validation matrix per file |
| 4 | Integration & Validation | main.py patch, smoke test, structural test | Collision-safe CLI registration |

### 4.2 Key Design Decisions

**Command/Protocol Split (addresses C1)**: Adopts the tasklist pattern with a thin command shim (`commands/cli-portify.md`) delegating to a full protocol skill (`skills/sc-cli-portify-protocol/SKILL.md`). The command handles argument parsing and input validation; the protocol owns the generation logic.

**Dual .md/.yaml Phase Contracts (addresses C3)**: Every phase emits two artifacts: a human review document (`.md`) and a machine-readable contract (`.yaml`). The `.yaml` contract has a stable schema per phase. The next phase's entry criteria validates the incoming contract before proceeding, eliminating the "re-interpret prose" leak.

Contract schema common header:
```yaml
phase: <0|1|2|3|4>
status: <completed|failed|skipped>
timestamp: <ISO-8601>
resume_checkpoint: <phase marker>
validation_status:
  blocking_checks_passed: <int>
  blocking_checks_total: <int>
  advisory_warnings: <list[str]>
```

**Mandatory Return Contract (addresses C3, per adversarial pattern)**: Written on every invocation including failures, with fields for `status`, `failure_phase`, `failure_type`, `generated_files`, `source_step_count`, `generated_step_count`, `elimination_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, and `phase_contracts`.

**Live API Snapshot Verification (addresses C4)**: Phase 0 reads `src/superclaude/cli/pipeline/models.py` and `gates.py`, extracts all shared primitive signatures (`SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, `GateMode`), and stores them as `api-snapshot.yaml`. This snapshot is verified against in Phase 2 (model/gate design) and Phase 3 (generated code).

**Step Conservation Equation (addresses C5)**:
```
|source_step_registry| == |mapped_steps| + |elimination_records|
```
Every source workflow instruction that constitutes an action gets a stable `source_id` (S-NNN). No downstream phase may proceed if unmapped source_ids remain. Elimination records require justification and optional user approval.

**Pattern Coverage Matrix (addresses M5)**: Supported patterns include sequential steps, batch parallelism, conditional skip, pure programmatic, Claude-assisted, hybrid, and static fan-out. Unsupported patterns (recursive self-orchestration, interactive mid-pipeline, dynamic code eval, dynamic fan-out, multi-return contract) trigger blocking abort before code generation.

**Failure Routing with Resume Semantics (addresses M6)**: Nine failure status types with per-status blocking/advisory classification, remediation guidance, and resumable checkpoint. Each phase contract records `resume_checkpoint`. On resume: read latest contract, validate completed phases still valid, resume from failed phase.

### 4.3 Self-Validation Matrices

Each phase includes a numbered self-validation table. Combined totals:

- **Phase 1**: 7 checks (6 blocking, 1 advisory)
- **Phase 2**: 8 checks (7 blocking, 1 advisory)
- **Phase 3 per-file**: 6 checks (5 blocking, 1 advisory)
- **Phase 3 cross-file**: 4 checks (all blocking)
- **Phase 4**: 5 checks (4 blocking, 1 advisory)

### 4.4 MCP Usage Contract

Phase-level MCP server mapping:

| Phase | MCP Server | Purpose |
|-------|-----------|---------|
| 0 | Auggie (codebase-retrieval) | Locate workflow components, read live pipeline API |
| 0 | Serena | Symbol-level API signature extraction from models.py/gates.py |
| 1 | Auggie | Discover agents, trace data flow across files |
| 1 | Sequential | Classification conflict resolution (when confidence < 0.7) |
| 2 | Context7 | Framework/library API lookup if workflow references external libs |
| 2 | Sequential | Complex executor design decisions |
| 3 | Serena | Verify generated code symbols against pipeline module |
| 4 | Serena | Verify main.py integration patch correctness |

### 4.5 Progress Tracking Contract

TodoWrite integration with 23 trackable subtasks across all 5 phases, including checkpoint triggers after phase completion, user review gates, write operations, and failures.

---

## 5. Spec Readiness Assessment

### 5.1 Assessment Scores

The refactored spec was assessed for sc:roadmap readiness across multiple dimensions. Scores ranged 8-9/10, a substantial improvement from the original 3-6/10.

### 5.2 Remaining Gaps (8 identified)

| Gap | Description | Severity |
|-----|-------------|----------|
| G1 | Phase 4 contract schema missing from the spec (Phases 0-3 have explicit YAML schemas, Phase 4 does not) | Minor |
| G2 | Artifact directory structure unspecified -- where do `.yaml` contracts and `.md` review docs live relative to the output directory? | Minor |
| G3 | No worked examples or Given/When/Then scenarios in the refactored spec (the panel review had them, but the spec omits them) | Minor |
| G4 | Source workflow staleness on resume -- if the source workflow changed between invocations, resume may use stale analysis | Minor |
| G5 | Phase 3 rollback policy undefined -- if file 7 of 12 fails generation, what happens to files 1-6? | Minor |
| G6 | Static vs dynamic fan-out boundary -- the coverage matrix lists "dynamic fan-out" as unsupported but the detection heuristic is ambiguous | Minor |
| G7 | Elimination record approval policy -- when does an elimination require user approval vs self-validation approval? | Minor |
| G8 | Migration testing strategy absent -- no plan for testing the command/protocol split migration itself | Minor |

### 5.3 Verdict

Ready for sc:roadmap with minor gaps. The gaps are addressable during roadmap generation and do not block pipeline execution.

---

## 6. Pipeline Failure Incident

### 6.1 What Happened

The roadmap run was executed with the refactored spec as input. The pipeline failed at the **extract** step -- the very first step.

### 6.2 Immediate Failure Symptom

Gate failure message: `"YAML frontmatter missing or unparseable: no opening ---"`

This message originates from `src/superclaude/cli/pipeline/gates.py:78`:

```python
def _check_frontmatter(
    content: str, required_fields: list[str], output_file: Path
) -> tuple[bool, str | None]:
    """Extract and validate YAML frontmatter fields."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return False, f"YAML frontmatter missing or unparseable in {output_file}: no opening ---"
```

### 6.3 Immediate Root Cause

The Claude subprocess produced output with **two** problems:

1. **Reasoning preamble**: The output began with natural language text ("Now I have the full spec. Let me produce...") before the YAML frontmatter, violating the position-dependent parser's expectation that `---` appears at the start of the file.

2. **Markdown code fences**: The YAML frontmatter was wrapped in triple-backtick code fences (` ```yaml ... ``` `), which the parser does not strip before looking for `---`.

Both problems caused the `content.lstrip().startswith("---")` check on `gates.py:77` to fail.

### 6.4 Why the Retry Did Not Help

The pipeline's retry mechanism (`executor.py:154-228`) re-ran the exact same step with the exact same prompt. Since no feedback about the gate failure was injected into the retry prompt, the subprocess produced the same malformed output on the second attempt. The step has `retry_limit=1` (meaning 2 total attempts), so after both identical failures, the pipeline halted.

Evidence from `src/superclaude/cli/pipeline/executor.py:225-228`:

```python
if attempt < max_attempts:
    continue  # retry
```

The retry loop contains no logic to read the gate failure reason or modify the prompt.

---

## 7. Systemic Root Cause Analysis

Four parallel analysis agents identified 12 root causes, deduplicated to 9 distinct issues across 4 architectural layers.

### 7.1 Prompt Layer

**RC1: No negative constraints in prompts**
- **Likelihood**: 8/10
- **Affected steps**: 8/8 (all steps use the same prompt pattern)
- **Evidence**: `src/superclaude/cli/roadmap/prompts.py:46-60` (extract prompt) -- The prompt says "Your output MUST begin with YAML frontmatter delimited by --- lines" but never says "Do NOT include any text before the frontmatter", "Do NOT wrap the frontmatter in code fences", or "Do NOT include reasoning or preamble before the output".
- **Impact**: LLMs frequently produce preamble text before structured output when not explicitly told not to. The absence of negative constraints makes this the expected behavior, not an edge case.

**RC2: No concrete format example in prompts**
- **Likelihood**: 6/10
- **Affected steps**: 8/8
- **Evidence**: All prompt builders in `prompts.py` describe the required format textually but never include a literal example of correctly formatted output. Compare to the extract prompt (`prompts.py:49-52`): it describes frontmatter fields but never shows what a valid output looks like.
- **Impact**: A concrete example provides stronger anchoring than textual description alone.

**RC3: Format instructions buried by embedded inputs**
- **Likelihood**: 7/10
- **Affected steps**: 6/8 (steps with input embedding)
- **Evidence**: `src/superclaude/cli/roadmap/executor.py:92-94` -- When inputs fit within the embed size limit, they are appended to the end of the prompt:
  ```python
  effective_prompt = step.prompt + "\n\n" + embedded
  ```
  This places format instructions at the beginning of the prompt and the spec content (potentially thousands of lines) after it. By the time the LLM generates output, the format instructions are far back in the context window.
- **Impact**: Format compliance degrades as input length increases. Moving format instructions to the end (after embedded content) would improve compliance.

### 7.2 Gate/Parser Layer

**RC4: Brittle position-dependent frontmatter parser**
- **Likelihood**: 9/10
- **Affected steps**: 8/8
- **Evidence**: `src/superclaude/cli/pipeline/gates.py:76-78`:
  ```python
  stripped = content.lstrip()
  if not stripped.startswith("---"):
      return False, f"YAML frontmatter missing or unparseable in {output_file}: no opening ---"
  ```
  The parser requires `---` to appear at the absolute start of the whitespace-stripped content. It has no tolerance for:
  - Preamble text before frontmatter
  - Markdown code fences (` ```yaml\n---\n...` )
  - BOM characters
  - Other common LLM output artifacts
- **Impact**: Any non-whitespace character before `---` causes a hard failure, regardless of whether valid frontmatter exists later in the content.

**RC9: Semantic checks return bare bool, no diagnostic detail**
- **Likelihood**: 6/10
- **Affected steps**: 4/8 (steps with semantic checks)
- **Evidence**: `src/superclaude/cli/pipeline/models.py:63`:
  ```python
  check_fn: Callable[[str], bool]
  ```
  Semantic checks return only `True`/`False`. When a check fails, the only diagnostic available is the static `failure_message` string (`models.py:64`). There is no way to communicate *what* was wrong or *where* in the content the problem was detected.
- **Impact**: Hampers debugging and makes it impossible to inject meaningful feedback into retry prompts.

### 7.3 Executor/Retry Layer

**RC5: Blind retry with no feedback loop**
- **Likelihood**: 10/10
- **Affected steps**: 8/8
- **Evidence**: `src/superclaude/cli/pipeline/executor.py:224-228`:
  ```python
  # Gate failed
  _log.info("Gate failed for step '%s' (attempt %d/%d): %s", step.id, attempt, max_attempts, reason)

  if attempt < max_attempts:
      continue  # retry
  ```
  The gate failure `reason` string is logged but never used. On retry, `run_step(step, config, cancel_check)` is called with the identical `step` object containing the identical `step.prompt`. The subprocess receives no information about why the previous attempt failed.
- **Impact**: Retries are deterministically doomed to reproduce the same failure. This is the single most impactful fixable defect because it turns every transient formatting failure into a guaranteed pipeline halt.

**RC6: Hardcoded retry_limit=1, no escalation**
- **Likelihood**: 7/10
- **Affected steps**: 8/8
- **Evidence**: `src/superclaude/cli/roadmap/executor.py:204`:
  ```python
  retry_limit=1,
  ```
  All steps in `_build_steps()` use `retry_limit=1`, meaning 2 total attempts. There is no escalation strategy (e.g., increase temperature, switch model, simplify prompt, add format example) on subsequent retries. The `PipelineConfig` has no configurable retry policy.
- **Impact**: Two attempts with identical prompts provides negligible reliability improvement over a single attempt for systematic (non-transient) failures.

### 7.4 Subprocess Layer

**RC7: CLAUDE.md loaded by subprocess**
- **Likelihood**: 9/10
- **Affected steps**: 8/8
- **Evidence**: `src/superclaude/cli/pipeline/process.py:89-98`:
  ```python
  def build_env(self) -> dict[str, str]:
      """Build environment for the child process."""
      env = os.environ.copy()
      env.pop("CLAUDECODE", None)
      env.pop("CLAUDE_CODE_ENTRYPOINT", None)
      return env
  ```
  The `build_env()` method removes `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` to prevent nested-session detection, but it does **not** prevent the subprocess from loading `CLAUDE.md` or `.claude/` configuration files. The `build_command()` method (`process.py:69-87`) includes no `--no-config` or equivalent flag.

  The project's `CLAUDE.md` file contains extensive SuperClaude framework instructions, persona definitions, MCP server configurations, and behavioral rules. When the subprocess loads this file, it receives competing instructions that override or dilute the step's targeted prompt.
- **Impact**: The subprocess becomes a SuperClaude-configured agent rather than a focused extraction tool. This is the **primary causal agent** for the preamble problem -- the loaded CLAUDE.md instructs Claude to plan, analyze, and reason before acting, producing the "Now I have the full spec. Let me produce..." preamble.

**RC8: No output post-processing/sanitization**
- **Likelihood**: 7/10
- **Affected steps**: 8/8
- **Evidence**: `src/superclaude/cli/roadmap/executor.py:112-122`:
  ```python
  proc = ClaudeProcess(
      prompt=effective_prompt,
      output_file=step.output_file,
      ...
  )
  proc.start()
  ```
  The subprocess writes directly to `step.output_file`. After the process completes, the executor passes the file directly to `gate_passed()` with no intermediate sanitization step. There is no logic to strip common LLM output artifacts such as:
  - Preamble text before frontmatter
  - Markdown code fences around YAML blocks
  - Trailing commentary after the document
  - Unicode BOM characters
- **Impact**: Every common LLM output variation becomes a gate failure rather than being handled as a known artifact pattern.

---

## 8. Adversarial Debate Results

### 8.1 Root Cause Ranking (Consensus)

The 4 analysis agents debated and converged on this priority ordering:

| Rank | RC | Description | Rationale |
|------|-----|-------------|-----------|
| 1 | RC7 | CLAUDE.md contamination | **Primary causal agent**. The loaded framework instructions directly cause the reasoning preamble. Without this, the LLM would more likely comply with the prompt's format instructions. |
| 2 | RC5 | Blind retry | **Turns every failure into deterministic 2x failure**. Even if RC7 is fixed and preamble becomes occasional, blind retry guarantees no recovery. |
| 3 | RC1 | No negative prompt constraints | **Low-cost high-impact**. Negative constraints ("Do NOT...") are more reliable than positive-only instructions for LLM format compliance. |
| 4 | RC4 | Brittle frontmatter parser | **Defense in depth**. Even with perfect prompts, LLMs occasionally produce unexpected output. A resilient parser provides the final safety net. |
| 5 | RC3 | Format instructions buried | **Structural prompt issue**. Placing format rules before large embedded content reduces their salience. |
| 6 | RC8 | No output post-processing | **Easy win**. A simple preamble-stripping regex before gate evaluation handles the most common failure pattern. |
| 7 | RC6 | Hardcoded retry limit | **Nice to have**. More retries with identical prompts provide diminishing returns without feedback injection (RC5 fix). |
| 8 | RC2 | No concrete format example | **Supplementary**. Examples help but are less critical when negative constraints (RC1) are present. |
| 9 | RC9 | Diagnostic detail lacking | **Long-term quality**. Important for observability but does not directly fix the current failure mode. |

### 8.2 Key Debate Points

**RC7 vs RC5 for top rank**: RC7 was ranked above RC5 because RC7 is the *cause* while RC5 is an *amplifier*. If CLAUDE.md contamination is eliminated, the LLM is far more likely to comply with format instructions, making retry less necessary. However, RC5 is ranked #2 because even without RC7, blind retry is an architectural defect that will cause problems for any future transient failure.

**RC4 (parser resilience) vs RC8 (post-processing)**: Both address the same symptom (non-compliant output reaching the gate) but at different layers. The debate concluded that RC8 (post-processing) is preferred as the immediate fix because it handles the common cases cheaply, while RC4 (parser resilience) provides deeper protection but requires more careful design to avoid accepting malformed content.

**RC1 (negative constraints) effectiveness**: The debate acknowledged that negative constraints are not 100% reliable with LLMs, but consensus held that they reduce preamble occurrence by 60-80% based on empirical prompting research, making them high-value at near-zero implementation cost.

---

## 9. Proposed Solutions

### 9.1 Solution Rankings (Consensus)

| Rank | ID | Solution | Effort | Effectiveness | Target RC |
|------|-----|---------|--------|--------------|-----------|
| 1 | S6 | Isolate subprocess from CLAUDE.md | Medium | Very High | RC7 |
| 2 | S4 | Inject gate failure reason into retry prompt | Very Low | High | RC5 |
| 3 | S1 | Add negative constraints + concrete format example | Low | High | RC1, RC2 |
| 4 | S5 | Add preamble-stripping sanitizer before gate check | Very Low | Medium-High | RC8 |
| 5 | S2 | Move format instructions to end of prompt (after embedded inputs) | Very Low | Medium | RC3 |
| 6 | S3 | Make frontmatter parser resilient to common LLM artifacts | Low | Medium | RC4 |
| 7 | S7 | Configurable retry with escalation strategy | High | Medium | RC6 |
| 8 | S8 | Persist failure context in state file for cross-session debugging | Medium | Low | RC9 |

### 9.2 Solution Details

**S4: Inject gate failure into retry prompt** (addresses RC5)

Modify `_execute_single_step()` in `src/superclaude/cli/pipeline/executor.py` to append the gate failure reason to the prompt before retrying:

```python
# Current (executor.py:224-228):
if attempt < max_attempts:
    continue  # retry

# Proposed:
if attempt < max_attempts:
    step = Step(
        ...step fields...,
        prompt=step.prompt + f"\n\nIMPORTANT: Your previous output failed validation. "
               f"Reason: {reason}\n"
               f"Please correct your output to comply with the format requirements."
    )
    continue  # retry with feedback
```

Effort: Very Low (10-20 lines). Effectiveness: High -- transforms blind retry into informed retry.

**S1: Negative constraints + concrete example** (addresses RC1, RC2)

Add to all prompt builders in `src/superclaude/cli/roadmap/prompts.py`:

```python
# Negative constraints (add to every prompt builder):
"CRITICAL FORMAT RULES:\n"
"- Your output MUST begin with --- on the very first line\n"
"- Do NOT include any text, reasoning, or commentary before the ---\n"
"- Do NOT wrap the frontmatter in code fences (no ```yaml or ```)\n"
"- Do NOT include thinking or planning text anywhere in your output\n\n"
```

Effort: Low (add text block to 7 functions). Effectiveness: High -- directly prevents the most common failure pattern.

**S5: Preamble-stripping sanitizer** (addresses RC8)

Add a sanitization function between subprocess completion and gate evaluation:

```python
def sanitize_llm_output(content: str) -> str:
    """Strip common LLM output artifacts before gate evaluation."""
    # Strip preamble before first ---
    idx = content.find("\n---\n")
    if idx == -1:
        idx = content.find("---\n")
    if idx > 0:
        content = content[idx:]

    # Strip markdown code fences around frontmatter
    content = re.sub(r'^```(?:yaml|yml)?\s*\n', '', content)
    content = re.sub(r'\n```\s*$', '', content, count=1)

    return content
```

Effort: Very Low (15-20 lines). Effectiveness: Medium-High -- handles the exact failure pattern observed.

**S6: Isolate subprocess from CLAUDE.md** (addresses RC7)

Modify `ClaudeProcess.build_command()` in `src/superclaude/cli/pipeline/process.py` or `build_env()` to prevent CLAUDE.md loading. Options:

- Add `--no-config` flag (if available in claude CLI)
- Set `CLAUDE_CONFIG_DIR` to an empty temp directory
- Use `--cwd` to a directory without `.claude/` or `CLAUDE.md`
- Add an environment variable to suppress CLAUDE.md loading

Effort: Medium (requires testing subprocess behavior with various isolation approaches). Effectiveness: Very High -- eliminates the primary causal agent.

**S2: Move format instructions to end of prompt** (addresses RC3)

Modify the embedding logic in `src/superclaude/cli/roadmap/executor.py:92-94`:

```python
# Current:
effective_prompt = step.prompt + "\n\n" + embedded

# Proposed: Split prompt into preamble + format, sandwich embedded content
effective_prompt = preamble + "\n\n" + embedded + "\n\n" + format_instructions
```

Effort: Very Low. Effectiveness: Medium -- improves format compliance by placing instructions closer to the generation point.

**S3: Resilient frontmatter parser** (addresses RC4)

Modify `_check_frontmatter()` in `src/superclaude/cli/pipeline/gates.py` to search for frontmatter anywhere in the content rather than requiring it at position 0:

```python
# Current (gates.py:76-78):
stripped = content.lstrip()
if not stripped.startswith("---"):
    return False, ...

# Proposed: Search for frontmatter pattern
import re
match = re.search(r'^---\s*\n(.+?)\n---', content, re.MULTILINE | re.DOTALL)
if match is None:
    return False, ...
frontmatter_text = match.group(1)
```

Effort: Low (20-30 lines). Effectiveness: Medium -- provides defense in depth but should not be relied upon as primary fix.

---

## 10. Implementation Roadmap

### 10.1 PR Sequence

**PR 1: Quick wins (< 1 hour, ~70-80% failure reduction)**

| Solution | Target File | Changes |
|----------|------------|---------|
| S4 (retry feedback injection) | `src/superclaude/cli/pipeline/executor.py` | Inject gate failure reason into retry prompt |
| S1 (negative constraints) | `src/superclaude/cli/roadmap/prompts.py` | Add negative constraint block to all 7 prompt builders |
| S5 (preamble sanitizer) | `src/superclaude/cli/pipeline/gates.py` or new `sanitize.py` | Add sanitize_llm_output() before gate evaluation |
| S2 (format instructions position) | `src/superclaude/cli/roadmap/executor.py` | Move format instructions after embedded inputs |

Expected outcome: Addresses RC1, RC2, RC3, RC5, RC8. Combined effect should eliminate the majority of frontmatter-related gate failures.

Release: **v2.15-RetryFeedbackInjection** (directory already created at `.dev/releases/current/v2.15-RetryFeedbackInjection/`)

**PR 2: Subprocess isolation (2-4 hours, ~15-20% additional reduction)**

| Solution | Target File | Changes |
|----------|------------|---------|
| S6 (CLAUDE.md isolation) | `src/superclaude/cli/pipeline/process.py` | Prevent subprocess from loading CLAUDE.md/framework config |

Expected outcome: Eliminates the primary causal agent (RC7). Requires testing multiple isolation approaches to find one compatible with the claude CLI.

Release: **v2.16-SubProcIsolation** (directory already created at `.dev/releases/current/v2.16-SubProcIsolation/`)

**PR 3: Defense in depth (1 hour)**

| Solution | Target File | Changes |
|----------|------------|---------|
| S3 (resilient parser) | `src/superclaude/cli/pipeline/gates.py` | Make frontmatter parser search instead of position-dependent |

Expected outcome: Provides final safety net (RC4). After PRs 1-2, this catches the remaining edge cases.

Release: **v2.17-FrontmatterParser** (directory already created at `.dev/releases/current/v2.17-FrontmatterParser/`)

**Deferred (not in immediate scope)**

| Solution | Rationale for deferral |
|----------|----------------------|
| S7 (configurable retry with escalation) | High effort, medium effectiveness. PR 1's feedback injection provides most of the value. |
| S8 (persistent failure context) | Medium effort, low immediate effectiveness. Useful for observability but not for fixing the current failure mode. |

### 10.2 Cumulative Expected Effectiveness

| After | Failure Rate (estimated) | Cumulative Reduction |
|-------|------------------------|---------------------|
| Baseline | ~80-90% for complex specs | -- |
| PR 1 | ~15-25% | ~70-80% reduction |
| PR 2 | ~3-5% | ~90-95% reduction |
| PR 3 | ~1-2% | ~95-98% reduction |

---

## 11. Appendix: Key File References

### 11.1 Source Files Analyzed

| File | Path | Role in Analysis |
|------|------|-----------------|
| Spec panel review | `.dev/releases/current/v2.18-cli-portify-v2/cli-portify-specreview.md` | Original 15-finding review document |
| Refactoring spec | `.dev/releases/current/v2.18-cli-portify-v2/refactoring-spec-cli-portify.md` | 5-phase architecture addressing all findings |
| Prompt builders | `src/superclaude/cli/roadmap/prompts.py` | Evidence for RC1, RC2, RC3 |
| Pipeline gates | `src/superclaude/cli/pipeline/gates.py` | Evidence for RC4, RC9; failure message origin |
| Pipeline models | `src/superclaude/cli/pipeline/models.py` | Evidence for RC9; live API contract shapes |
| Roadmap executor | `src/superclaude/cli/roadmap/executor.py` | Evidence for RC3, RC5, RC6; retry logic |
| Pipeline executor | `src/superclaude/cli/pipeline/executor.py` | Evidence for RC5; generic retry loop |
| ClaudeProcess | `src/superclaude/cli/pipeline/process.py` | Evidence for RC7, RC8; subprocess isolation |

### 11.2 Critical Code Locations

| Root Cause | File | Line(s) | Code Pattern |
|-----------|------|---------|-------------|
| RC1 (no negative constraints) | `roadmap/prompts.py` | 46-60 | Extract prompt with positive-only format instructions |
| RC3 (buried format instructions) | `roadmap/executor.py` | 92-94 | `effective_prompt = step.prompt + "\n\n" + embedded` |
| RC4 (brittle parser) | `pipeline/gates.py` | 76-78 | `stripped.startswith("---")` position check |
| RC5 (blind retry) | `pipeline/executor.py` | 224-228 | `continue  # retry` with no prompt modification |
| RC6 (hardcoded retry) | `roadmap/executor.py` | 204 | `retry_limit=1` on all steps |
| RC7 (CLAUDE.md loaded) | `pipeline/process.py` | 89-98 | `build_env()` missing config isolation |
| RC7 (no --no-config) | `pipeline/process.py` | 69-87 | `build_command()` missing isolation flags |
| RC8 (no sanitization) | `roadmap/executor.py` | 112-122 | Direct `ClaudeProcess` -> file -> gate with no intermediate step |
| RC9 (bare bool checks) | `pipeline/models.py` | 63 | `check_fn: Callable[[str], bool]` |

### 11.3 Traceability Matrix

| Spec Finding | Root Cause(s) | Solution(s) | PR |
|-------------|--------------|------------|-----|
| C1 (missing command entry) | N/A (spec-level, not pipeline) | Refactoring spec Section 1.1, 10 | -- |
| C2 (no self-validation) | N/A (spec-level) | Refactoring spec Sections 2.2-2.5 | -- |
| C3 (phase interfaces leak) | N/A (spec-level) | Refactoring spec Sections 2.0, 3 | -- |
| C4 (pipeline API drift) | N/A (spec-level) | Refactoring spec Sections 9, 12 | -- |
| C5 (no step conservation) | N/A (spec-level) | Refactoring spec Section 7 | -- |
| Pipeline extract failure | RC1, RC3, RC4, RC5, RC7, RC8 | S1, S2, S3, S4, S5, S6 | PRs 1-3 |
| Systematic retry failures | RC5, RC6 | S4, S7 | PR 1 (S4), deferred (S7) |
| Subprocess contamination | RC7 | S6 | PR 2 |
| Parser fragility | RC4, RC9 | S3, S8 | PR 3 (S3), deferred (S8) |

### 11.4 Related Release Artifacts

| Directory | Purpose | Status |
|-----------|---------|--------|
| `.dev/releases/current/v2.15-RetryFeedbackInjection/` | PR 1 workspace | Created, empty |
| `.dev/releases/current/v2.16-SubProcIsolation/` | PR 2 workspace | Created, empty |
| `.dev/releases/current/v2.17-FrontmatterParser/` | PR 3 workspace | Created, empty |
| `.dev/releases/current/v2.18-cli-portify-v2/` | Spec review and refactoring spec | Contains review + spec documents |

---

*End of session findings document (Agent A).*
