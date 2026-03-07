<!-- DOCUMENT PROVENANCE
  Base: Variant B (haiku:analyzer) — adversarial/variant-2-original.md, score 0.877
  Incorporated: Variant A (opus:architect) — adversarial/variant-1-original.md
  Merge plan: adversarial/refactor-plan.md (7 changes)
  Merge executor: merge-executor agent
  Date: 2026-03-06
-->

<!-- Source: Base (original) -->
# sc:cli-portify v2.15 Development Session -- Technical Findings Report

**Date**: 2026-03-06
**Branch**: `feature/2.15-cli-portify`
**Scope**: Specification review, refactored spec design, pipeline failure investigation, root cause analysis
**Report Classification**: Engineering session findings (merged)

---

<!-- Source: Base (original), modified per Change #3 — "four-PR" corrected to "three-PR" -->
## 1. Abstract

This report documents five workstreams conducted during the sc:cli-portify v2.15 development session: (1) a six-perspective expert panel review of the original SKILL.md specification, (2) design of a 16-section refactored specification addressing all identified deficiencies, (3) a readiness assessment scoring the refactored spec for sc:roadmap consumption, (4) investigation of a pipeline gate validation failure during an actual `superclaude roadmap run` execution, and (5) a systematic four-layer root cause analysis culminating in a three-debater adversarial consensus on nine distinct failure causes and eight candidate solutions. The investigation revealed that the pipeline's most critical defect is CLAUDE.md environment contamination of subprocess behavior, not the commonly suspected prompt formatting issues, and produced a three-PR remediation sequence (with two deferred solutions) with projected 95-100% failure reduction.

---

<!-- Source: Base (original), modified per Change #3 — "4-PR" corrected to "3-PR" -->
## 2. Timeline

| Sequence | Workstream | Key Output |
|----------|-----------|------------|
| WS-1 | Spec Panel Review | 15 findings (5C/7M/3N), quality scores 3-6/10 |
| WS-2 | Refactored Spec Design | 16-section specification with live API snapshot mechanism |
| WS-3 | Readiness Assessment | 8-9/10 across dimensions, 8 gaps identified (G1-G8) |
| WS-4 | Pipeline Failure Investigation | Gate validation failure on `extraction.md` -- preamble contamination |
| WS-5 | Adversarial Root Cause Analysis | 9 root causes, 8 solutions, 3-PR implementation sequence |

---

<!-- Source: Base (original) -->
## 3. Part I: Specification Analysis

### 3.1 Original Skill Review -- Panel Structure

The review examined `src/superclaude/skills/sc-cli-portify/SKILL.md` (236 lines) through six expert perspectives:

| Perspective | Expert Model | Focus Area |
|------------|-------------|------------|
| Wiegers | Requirements engineering | Completeness, testability, traceability |
| Fowler | Software architecture | Refactoring patterns, coupling, cohesion |
| Nygard | Release engineering | Operational readiness, failure modes, resilience |
| Whittaker | Adversarial testing | Attack surfaces, boundary conditions, exploits |
| Crispin | Acceptance testing | Verification criteria, test coverage, user stories |
| Adzic | Specification by example | Concrete examples, living documentation, collaboration |

### 3.2 Quality Scores

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Requirements completeness | 5/10 | Missing command entry point, no MCP declaration in frontmatter, phase interfaces undefined |
| Architecture soundness | 6/10 | Good pipeline/sprint reuse intent, but API references drift from live code |
| Generation correctness | 4/10 | No self-validation mechanism, template applicability undefined |
| Testability | 3/10 | Non-measurable claims ("100% completion"), no boundary conditions |
| Operational determinism | 3/10 | No failure routing, no progress tracking, output location underspecified |

### 3.3 Findings Registry

#### 3.3.1 Critical Findings (5)

**C1: Missing command entry point**
The SKILL.md defines `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration` arguments but never specifies the actual CLI invocation command. The `allowed-tools` frontmatter lists `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` but there is no Click command group definition or `main.py` registration pattern.

Evidence -- `SKILL.md:57-67`:
```
/sc:cli-portify --workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>]
```
This is a skill invocation syntax, not a CLI command. No mapping to the Click command infrastructure in `src/superclaude/cli/main.py` is specified.

**C2: No generation self-validation**
Phase 3 (Code Generation) produces 12-14 Python files but defines no mechanism to validate that the generated code is syntactically correct, importable, or structurally consistent with the pipeline API. The only post-generation check is Phase 4's "Verify imports -- Quick check for circular dependencies."

Evidence -- `SKILL.md:157-161`:
```
Generate files in dependency order (models -> gates -> prompts -> config -> monitor
-> process -> executor -> tui -> logging -> diagnostics -> commands -> __init__).
Each file imports from `superclaude.cli.pipeline` for shared base types and follows
sprint/roadmap naming conventions.
```
No validation step follows generation.

**C3: Phase interfaces leak prose, not contracts**
Phase transitions are described narratively ("Present to user for review before Phase 2") but never define structured inter-phase contracts. What data structure does Phase 1 produce that Phase 2 consumes? The spec says `portify-analysis.md` but does not define required sections, frontmatter schema, or machine-readable markers.

Evidence -- `SKILL.md:106-108`:
```
**Output**: `portify-analysis.md` -- Complete decomposition following the template
in `refs/analysis-protocol.md`. Must include: component inventory, step graph with
classifications, parallel groups, gates summary, data flow diagram, and recommendations.
```
"Must include" is prose, not a validatable contract.

**C4: Pipeline API drift between refs and live code**
The SKILL.md references API contracts that do not match the live pipeline code:

| SKILL.md Claim | Live Code Reality |
|---------------|-------------------|
| "semantic checks return `tuple[bool, str]`" (line 137, 202) | `SemanticCheck.check_fn: Callable[[str], bool]` -- returns bare `bool`, not `tuple` (`pipeline/models.py:63`) |
| "ClaudeProcess subclass with domain-specific prompt building" (line 43) | `ClaudeProcess` uses composition, not inheritance -- no subclass pattern exists (`pipeline/process.py:24-66`) |
| "4-layer subprocess isolation model" (line 205-208) | `build_env()` only strips 2 env vars (`pipeline/process.py:89-98`) |

This is the most operationally dangerous finding because generated code following the SKILL.md's API descriptions will fail at import time.

**C5: No step conservation guarantee**
The spec describes step decomposition (Phase 1, items 3-5) but provides no invariant ensuring that every source workflow step maps to exactly one pipeline step. Steps could be silently dropped during decomposition or duplicated during generation without detection.

#### 3.3.2 Major Findings (7)

**M1: Commented metadata block**
The `category`, `complexity`, `mcp-servers`, and `personas` fields are in an HTML comment block, not in the YAML frontmatter.

Evidence -- `SKILL.md:7-12`:
```markdown
<!-- Extended metadata (for documentation, not parsed):
category: development
complexity: high
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
-->
```
This metadata is invisible to any tooling that parses frontmatter.

**M2: MCP servers undeclared in frontmatter**
The `allowed-tools` field lists native tools only. MCP servers (sequential, serena, context7, auggie-mcp) are buried in the HTML comment and not machine-readable.

**M3: No progress tracking**
No `TodoWrite` usage pattern is defined for the 4-phase execution. A user running this skill has no visibility into which phase is active or what percentage is complete.

**M4: Vague import verification**
Phase 4 specifies "Quick check for circular dependencies" with no algorithm, tool choice, or pass/fail criteria.

**M5: Template applicability undefined**
Phase 3 references `refs/code-templates.md` but does not define which templates apply to which workflow types. A workflow without batch parallelism would still receive batch-related templates.

**M6: No failure routing**
If Phase 1 analysis determines the workflow is unsuitable for portification (e.g., purely creative, no structural outputs), no abort path is defined.

**M7: Output location underspecified**
Default output is `src/superclaude/cli/<name>/` but no collision handling is defined for existing modules.

#### 3.3.3 Minor Findings (3)

**N1: Sync inconsistency** -- The SKILL.md references `refs/analysis-protocol.md`, `refs/pipeline-spec.md`, `refs/code-templates.md` but these files are not checked for existence at skill load time.

**N2: Non-measurable claims** -- "100% completion and consistency between runs" (line 17) is not testable.

**N3: Boundaries too broad** -- "Analyze any SuperClaude skill/command/agent workflow" (line 218) has no scoping limits.

### 3.4 Whittaker Adversarial Attacks

Five attack vectors identified against the portification pipeline:

| ID | Attack | Vector | Expected Behavior | Actual Risk |
|----|--------|--------|-------------------|-------------|
| A1 | Zero/Empty | Empty SKILL.md, empty refs/ directory | Should abort at Phase 1 with diagnostic | No abort path defined (M6) |
| A2 | Divergence | Workflow with contradictory phase instructions | Should detect and flag contradictions | No contradiction detection mechanism |
| A3 | Sentinel Collision | Workflow containing `---` YAML delimiters in content | Gate parser would split on wrong boundary | `_check_frontmatter()` uses naive `find("\n---")` |
| A4 | Sequence | Workflow with circular step dependencies | Should detect cycle and abort | No cycle detection in dependency mapping |
| A5 | Accumulation | Workflow generating 50+ steps, exhausting context | Should chunk or fail gracefully | No step count limit or context budget |

<!-- Source: Base (original), modified per Change #6 — provenance note added -->
### 3.5 State Variable Registry

> **Provenance note**: The SV registry and GAP table (Sections 3.5-3.6) are synthesis artifacts derived from WS-1 (Spec Panel Review) findings. They are not independent workstreams but structured extractions from the six-perspective expert analysis, organized for reference and traceability.

Eleven state variables tracked across the 4-phase lifecycle:

| ID | Variable | Type | Set In | Read In | Validated |
|----|----------|------|--------|---------|-----------|
| SV1 | `workflow_path` | `Path` | Input | Phase 1 | Existence only |
| SV2 | `component_inventory` | `dict[str, ComponentInfo]` | Phase 1 | Phase 2 | No schema |
| SV3 | `step_graph` | `list[StepSpec]` | Phase 1 | Phase 2, 3 | No schema |
| SV4 | `parallel_groups` | `list[list[str]]` | Phase 1 | Phase 2 | No validation |
| SV5 | `gate_assignments` | `dict[str, GateCriteria]` | Phase 1 | Phase 2, 3 | No validation |
| SV6 | `prompt_contracts` | `dict[str, PromptSpec]` | Phase 2 | Phase 3 | No schema |
| SV7 | `model_definitions` | `dict[str, DataclassSpec]` | Phase 2 | Phase 3 | No schema |
| SV8 | `generated_files` | `list[Path]` | Phase 3 | Phase 4 | Existence only |
| SV9 | `integration_patches` | `list[Patch]` | Phase 2 | Phase 4 | No validation |
| SV10 | `cli_name` | `str` | Input | All phases | No collision check |
| SV11 | `output_dir` | `Path` | Input/derived | Phase 3, 4 | No collision check |

<!-- Source: Base (original), modified per Change #6 — provenance note added -->
### 3.6 Guard Condition Boundary Table

> **Provenance note**: Like the SV registry above, this GAP table is a synthesis artifact derived from WS-1 findings, not a separate workstream. It consolidates guard-condition gaps identified across multiple expert perspectives into a single reference table.

Twelve GAP (Guard-Absent-Problem) entries identified:

| ID | Guard Condition | Location | Current State | Risk |
|----|----------------|----------|---------------|------|
| GAP-1 | Workflow file exists and is valid SKILL.md | Phase 1 entry | `STOP` instruction only | Medium |
| GAP-2 | At least one step is Claude-assisted | Phase 1 exit | Not checked | High -- pure-programmatic workflow generates empty prompts.py |
| GAP-3 | No circular dependencies in step graph | Phase 1 step 5 | Not checked | High -- infinite loop in executor |
| GAP-4 | All referenced `refs/` files exist | Phase 1 step 1 | Not checked | Medium -- Phase 3 generates incomplete code |
| GAP-5 | Step count within context budget | Phase 1 exit | Not checked | Medium -- context exhaustion |
| GAP-6 | Generated models.py passes `mypy --strict` | Phase 3 exit | Not checked | High -- runtime import failures |
| GAP-7 | Generated gates.py semantic checks match prompt contracts | Phase 3 exit | Not checked | Critical -- gates pass bad output |
| GAP-8 | Generated executor.py imports resolve | Phase 3 exit | "Quick check" only | High |
| GAP-9 | Output directory does not contain existing module | Phase 3 entry | Not checked | Medium -- overwrites production code |
| GAP-10 | main.py patch does not break existing commands | Phase 4 | Not checked | High |
| GAP-11 | Phase 2 prompt contracts cover all Phase 1 Claude-assisted steps | Phase 2 exit | Not checked | Critical -- missing prompts |
| GAP-12 | Phase 1 gates cover all step outputs | Phase 1 exit | Not checked | High -- unvalidated outputs |

---

<!-- Source: Base (original) -->
## 4. Part II: Pipeline Infrastructure Investigation

### 4.1 Refactored Spec Design (Workstream 2)

A 16-section refactoring specification was designed to address all 15 findings from the panel review.

#### 4.1.1 Architecture

The refactored spec adopts a command/protocol split matching the existing `sc:tasklist` pattern:

- **5 phases** (0-4): Phase 0 (API Snapshot) is new, providing a live validation baseline
- **Dual contracts**: Each phase produces both `.md` (human-readable) and `.yaml` (machine-parseable) artifacts
- **Mandatory return contract**: Every phase function has typed inputs and outputs

#### 4.1.2 Key Innovations

**Live API Snapshot Mechanism (Phase 0)**

Phase 0 reads the live pipeline source files before any generation begins:

- Reads `pipeline/models.py` to extract `SemanticCheck`, `GateCriteria`, `Step`, `StepResult` interfaces
- Reads `pipeline/gates.py` to extract `gate_passed()` signature
- Reads `pipeline/process.py` to extract `ClaudeProcess` constructor and `build_env()` behavior
- Stores all contracts in `api-snapshot.yaml`
- Phases 2-4 validate generated code against the snapshot, not against stale documentation

This directly addresses C4 (pipeline API drift).

**Verified Live Pipeline API**:

From `pipeline/models.py:59-63`:
```python
@dataclass
class SemanticCheck:
    """Pure Python check applied to file content. No LLM invocation."""
    name: str
    check_fn: Callable[[str], bool]
    failure_message: str
```

From `pipeline/models.py:68-74`:
```python
@dataclass
class GateCriteria:
    """Defines what constitutes a passing output for a pipeline step."""
    required_frontmatter_fields: list[str]
    min_lines: int
    enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
    semantic_checks: list[SemanticCheck] | None = None
```

From `pipeline/gates.py:19`:
```python
def gate_passed(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]:
```

**Step Conservation Invariant**

Addresses C5:
```
|source_step_registry| == |mapped_steps| + |elimination_records|
```
Every workflow step must either map to a pipeline step or have an explicit elimination record with justification.

**Pattern Coverage Matrix**

Defines explicit workflow pattern categories with support status. Any workflow containing an unsupported pattern triggers an abort with diagnostic rather than silently producing incorrect output.

**Phase-Level MCP Usage Contract**

Each phase declares which MCP servers it uses and why, moving the buried HTML comment metadata (M1, M2) into the operational contract.

**TodoWrite Progress Tracking**

Addresses M3 by defining TodoWrite checkpoints at subphase granularity across all 5 phases.

**29 Self-Validation Checks**

Distributed across phases: 23 blocking (must pass to continue) and 6 advisory (logged but non-blocking). Each check has a defined input, expected outcome, and failure action.

#### 4.1.3 Readiness Assessment (Workstream 3)

The refactored spec was scored for sc:roadmap consumption:

| Dimension | Score | Notes |
|-----------|-------|-------|
| Structural completeness | 9/10 | All 16 sections present with contracts |
| API accuracy | 9/10 | Phase 0 snapshot mechanism ensures correctness |
| Testability | 8/10 | 29 validation checks, but no worked examples |
| Operational clarity | 8/10 | Clear phase boundaries, but artifact directory unspecified |

**Eight gaps identified (G1-G8)**:

| ID | Gap | Severity | Impact |
|----|-----|----------|--------|
| G1 | Missing Phase 4 contract schema | Medium | Integration patches lack validation format |
| G2 | Unspecified artifact directory | Low | Default `.portify/` vs output dir ambiguity |
| G3 | No worked examples | Medium | First-time users lack concrete reference |
| G4 | Staleness detection on resume | Medium | Resumed sessions may use stale API snapshot |
| G5 | Phase 3 rollback policy | Low | Partial generation leaves inconsistent state |
| G6 | Static/dynamic fan-out boundary | Medium | When to use static step list vs `build_steps()` |
| G7 | Elimination approval policy | Low | Who approves step eliminations |
| G8 | Migration testing strategy | Medium | No strategy for testing portified vs original workflow equivalence |

**Verdict**: Ready for sc:roadmap with gaps noted as non-blocking.

### 4.2 Pipeline Failure Incident (Workstream 4)

#### 4.2.1 Reproduction

Command executed:
```bash
superclaude roadmap run --agents "opus:architect,haiku:analyzer" <spec-file>
```

The pipeline's `extract` step failed gate validation on both attempts (retry_limit=1, so 2 total attempts).

#### 4.2.2 Failure Mechanism

The `_check_frontmatter()` function at `pipeline/gates.py:76-77` performs:

```python
stripped = content.lstrip()
if not stripped.startswith("---"):
    return False, f"YAML frontmatter missing or unparseable in {output_file}: no opening ---"
```

The Claude subprocess output began with preamble text before the frontmatter:

```
Now I have the full spec. Let me produce the requirements extraction document.

---

```yaml
functional_requirements: 47
complexity_score: 0.82
complexity_class: enterprise
```

The `content.lstrip()` strips whitespace but the preamble text ("Now I have the full spec...") is not whitespace. The first non-whitespace characters are `N`, `o`, `w` -- not `---`. Gate fails.

Additionally, the YAML frontmatter was wrapped in a code fence (`` ```yaml ... ``` ``), which is not the expected bare `---` delimiter format.

#### 4.2.3 Output Characteristics

The `extraction.md` file was:
- **18,378 bytes** / **217 lines** -- well above the `min_lines=50` threshold in `EXTRACT_GATE`
- Content was substantively correct: 47 functional requirements extracted, complexity scored, architectural constraints identified
- The only failures were format-related: preamble prefix and code fence wrapping

#### 4.2.4 Gate Configuration

From `roadmap/gates.py:141-145`:
```python
EXTRACT_GATE = GateCriteria(
    required_frontmatter_fields=["functional_requirements", "complexity_score", "complexity_class"],
    min_lines=50,
    enforcement_tier="STANDARD",
)
```

The `STANDARD` tier requires: file exists, non-empty, minimum line count, and YAML frontmatter field validation. The file passed the first three checks but failed frontmatter parsing.

---

<!-- Source: Base (original) -->
## 5. Part III: Adversarial Debate Synthesis

### 5.1 Investigation Architecture

Four parallel investigation agents were deployed, each examining a different layer:

| Agent | Layer | Scope |
|-------|-------|-------|
| Prompt Agent | Prompt construction | `roadmap/prompts.py` -- all 7 `build_*_prompt()` functions |
| Gate Agent | Gate validation | `pipeline/gates.py` -- `gate_passed()` and `_check_frontmatter()` |
| Executor Agent | Retry and orchestration | `pipeline/executor.py` -- `_execute_single_step()` retry loop |
| Subprocess Agent | Process lifecycle | `pipeline/process.py` -- `ClaudeProcess`, `build_env()`, `build_command()` |

### 5.2 Raw Findings (12, Deduplicated to 9)

The 12 raw findings were deduplicated by removing 3 overlaps (prompt-gate interaction counted by both prompt and gate agents; retry-prompt interaction counted by both executor and prompt agents; env contamination noted by both subprocess and executor agents).

### 5.3 Nine Root Causes with Evidence

#### RC1: No Negative Constraints in Prompts

**Layer**: Prompt
**File**: `roadmap/prompts.py`
**Evidence**: All 7 prompt builder functions contain positive instructions ("MUST begin with") but zero negative constraints. No prompt says "Do NOT include preamble text", "Do NOT wrap in code fences", or "Do NOT include thinking/reasoning before the output."

Specific evidence from `prompts.py:49-52`:
```python
"Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
"- functional_requirements: (integer count of identified requirements)\n"
"- complexity_score: (float 0.0-1.0 assessing overall complexity)\n"
"- complexity_class: (one of: simple, moderate, complex, enterprise)\n\n"
```

The instruction "MUST begin with" is aspirational without a corresponding prohibition on preamble.

#### RC2: No Format Example in Prompts

**Layer**: Prompt
**File**: `roadmap/prompts.py`
**Evidence**: Frontmatter fields use parenthetical placeholder descriptions instead of literal YAML examples.

From `prompts.py:49-52`:
```python
"- functional_requirements: (integer count of identified requirements)\n"
"- complexity_score: (float 0.0-1.0 assessing overall complexity)\n"
"- complexity_class: (one of: simple, moderate, complex, enterprise)\n\n"
```

A literal example would be:
```yaml
---
functional_requirements: 12
complexity_score: 0.75
complexity_class: complex
---
```

The parenthetical style invites the LLM to interpret rather than copy the format.

#### RC3: Format Instructions Buried by Embedded Content

**Layer**: Executor
**File**: `roadmap/executor.py:94`
**Evidence**: The `_embed_inputs()` function appends potentially thousands of lines of source content after the format instructions:

```python
effective_prompt = step.prompt + "\n\n" + embedded
```

For the extract step, `step.prompt` is the format-containing prompt (~15 lines), and `embedded` is the full specification file (potentially hundreds of lines). The format instructions at the top of the prompt are pushed far from the end of the context window, reducing their salience in the LLM's attention mechanism.

The embedding function at `executor.py:53-66`:
```python
def _embed_inputs(input_paths: list[Path]) -> str:
    if not input_paths:
        return ""
    blocks: list[str] = []
    for p in input_paths:
        content = Path(p).read_text(encoding="utf-8")
        blocks.append(f"# {p}\n```\n{content}\n```")
    return "\n\n".join(blocks)
```

#### RC4: Brittle Frontmatter Parser with No Recovery

**Layer**: Gate
**File**: `pipeline/gates.py:76-77`
**Evidence**: The parser does a single `startswith("---")` check with no scanning or recovery:

```python
stripped = content.lstrip()
if not stripped.startswith("---"):
    return False, f"YAML frontmatter missing or unparseable in {output_file}: no opening ---"
```

If the output contains valid frontmatter anywhere in the first N lines (e.g., after a 2-line preamble), the parser cannot find it. There is no fallback scan, no regex search, and no attempt to strip common LLM output artifacts (preamble text, code fences, thinking blocks).

The closing delimiter search is similarly fragile (`gates.py:82`):
```python
end_idx = rest.find("\n---")
```

#### RC5: Blind Retry with No Feedback Injection

**Layer**: Executor
**File**: `pipeline/executor.py:224-227`
**Evidence**: When a gate fails, the retry loop continues with the identical prompt:

```python
_log.info("Gate failed for step '%s' (attempt %d/%d): %s", step.id, attempt, max_attempts, reason)

if attempt < max_attempts:
    continue  # retry
```

The `reason` string (e.g., "YAML frontmatter missing or unparseable: no opening ---") is logged but never injected into the retry prompt. The `step.prompt` object is immutable within the loop -- the same `Step` instance is passed to `run_step()` on every attempt.

This means the retry is pure repetition: identical prompt, identical environment, with the same LLM likely producing the same format violation.

#### RC6: Hardcoded Retry Limit

**Layer**: Executor
**File**: `roadmap/executor.py`
**Evidence**: All 8 steps in `_build_steps()` use `retry_limit=1`:

```python
Step(
    id="extract",
    ...
    retry_limit=1,
),
```

This pattern repeats 8 times across lines 197-278. With `retry_limit=1`, the executor makes 2 total attempts (`max_attempts = step.retry_limit + 1` per `pipeline/executor.py:154`). For format-sensitive steps like extract (where the failure mode is format, not content), 2 identical attempts are insufficient.

#### RC7: CLAUDE.md Environment Contamination

**Layer**: Subprocess
**File**: `pipeline/process.py:89-98`
**Evidence**: The `build_env()` method only strips two environment variables:

```python
def build_env(self) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return env
```

The subprocess is launched via `subprocess.Popen()` at `process.py:116`:
```python
self._process = subprocess.Popen(self.build_command(), **popen_kwargs)
```

No `cwd` parameter is passed to `Popen()`, so the child process inherits the parent's working directory. The `claude` CLI, when invoked in a directory containing `.claude/` or with a global `~/.claude/CLAUDE.md`, loads those configuration files automatically.

The project's CLAUDE.md (`/config/workspace/SuperClaude_Framework/CLAUDE.md`) contains extensive persona instructions, thinking mode directives, verbose output preferences, and SuperClaude framework behaviors. The global CLAUDE.md (`/config/.claude/CLAUDE.md`) references `@COMMANDS.md`, `@FLAGS.md`, `@PRINCIPLES.md`, `@RULES.md`, `@MCP.md`, `@PERSONAS.md`, `@ORCHESTRATOR.md`, `@MODES.md` -- loading hundreds of pages of behavioral instructions.

These instructions directly contradict the pipeline's format requirements. For example, the introspection mode's "transparency markers" and the token efficiency mode's symbol system encourage verbose, formatted output that does not start with `---`.

This is the highest-severity root cause because it affects every subprocess in the pipeline, not just the extract step.

#### RC8: No Output Sanitization

**Layer**: Subprocess
**File**: `pipeline/process.py:109`
**Evidence**: The subprocess stdout is redirected directly to the output file:

```python
"stdout": self._stdout_fh,
```

Where `self._stdout_fh` is opened at `process.py:104`:
```python
self._stdout_fh = open(self.output_file, "w")
```

Raw LLM output -- including any preamble, thinking tokens, code fences, or formatting artifacts -- flows directly to the file that the gate subsequently validates. There is no intermediate sanitization layer to strip known LLM output artifacts before writing.

#### RC9: Bare Boolean Semantic Checks

**Layer**: Gate
**File**: `pipeline/models.py:63`
**Evidence**: The `SemanticCheck` dataclass defines:

```python
check_fn: Callable[[str], bool]
failure_message: str
```

The `check_fn` returns only `bool` -- it cannot report what specifically failed or where in the content the failure occurred. The `failure_message` is a static string set at definition time, not a dynamic message computed from the actual content.

From `pipeline/gates.py:64-66`:
```python
for check in criteria.semantic_checks:
    if not check.check_fn(content):
        return False, f"Semantic check '{check.name}' failed: {check.failure_message}"
```

The diagnostic value is limited: a failure message like "No numbered or bulleted items found" does not indicate whether the content was empty, had items in a different format, or was entirely prose.

### 5.4 Adversarial Debate: Three Debater Positions

Three debaters were assigned to rank the root causes by impact and recommend solution priorities:

#### 5.4.1 Architect Perspective

**Position**: RC7 (CLAUDE.md contamination) is the dominant root cause. All other root causes are secondary effects or defense-in-depth concerns. If the subprocess operates in a clean environment without persona contamination, the LLM is far more likely to follow the prompt's format instructions without the competing behavioral directives.

**Key argument**: The prompt says "MUST begin with YAML frontmatter" but the CLAUDE.md says "use transparency markers", "apply symbol system", "activate personas". The LLM resolves conflicting instructions by blending them, producing the observed preamble-then-frontmatter output pattern.

**Solution priority**: S6 (subprocess isolation) first, everything else is secondary.

#### 5.4.2 Reliability Engineer Perspective

**Position**: RC5 (blind retry) is the most cost-effective fix because it applies regardless of root cause. Even if we fix CLAUDE.md contamination, other format violations will occur (LLMs are stochastic). Feedback injection makes retries adaptive rather than repetitive.

**Key argument**: The current retry loop at `executor.py:226` does `continue` with the same prompt. If the gate failure reason ("no opening ---") were injected into the retry prompt, the LLM would self-correct on the second attempt in most cases.

**Estimated cost**: 5-10 lines of code change. Estimated effectiveness: 60-70% of failures self-corrected on retry.

**Solution priority**: S4 (retry feedback) first because lowest effort and broadest applicability.

#### 5.4.3 Pragmatist Perspective

**Position**: The fastest path to reliability is a combination of quick wins. No single fix is sufficient because the failure has multiple contributing causes. The correct approach is to fix the cheap things first (S4 + S1 + S5 + S2) in one PR, then address the architectural issue (S6) in a second PR.

**Key argument**: S4 (feedback injection) + S1 (negative constraints) + S5 (preamble sanitizer) + S2 (prompt reordering) can be implemented in under 1 hour and collectively address 70-80% of failures. S6 (subprocess isolation) is the architecturally correct solution but requires 2-4 hours and careful testing.

**Solution priority**: PR1 (quick wins) then PR2 (isolation).

### 5.5 Consensus Rankings

#### 5.5.1 Root Cause Consensus (Ordered by Impact)

| Rank | ID | Root Cause | Severity | Consensus Level |
|------|-----|-----------|----------|-----------------|
| 1 | RC7 | CLAUDE.md contamination | Critical | Unanimous -- all debaters agreed this is the primary cause |
| 2 | RC5 | Blind retry | High | Unanimous -- most cost-effective single fix |
| 3 | RC1 | No negative constraints | High | 2/3 -- Architect dissented (considers it secondary to RC7) |
| 4 | RC4 | Brittle parser | Medium-High | Unanimous -- defense in depth |
| 5 | RC3 | Format buried by embedded content | Medium | 2/3 -- Pragmatist dissented (considers it low impact) |
| 6 | RC8 | No sanitization | Medium | Unanimous |
| 7 | RC6 | Hardcoded retry | Medium | 2/3 -- Reliability Engineer considered it High |
| 8 | RC2 | No format example | Low-Medium | Unanimous |
| 9 | RC9 | Bare bool checks | Low | Unanimous -- quality of life, not reliability |

#### 5.5.2 Solution Consensus (Ordered by Priority)

| Rank | ID | Solution | Effort | Effectiveness | Consensus |
|------|-----|---------|--------|---------------|-----------|
| 1 | S6 | Subprocess isolation | Medium (2-4hr) | Very High | Architect: #1, others: #2 |
| 2 | S4 | Retry feedback injection | Very Low (<15min) | High | Reliability: #1, others: #2 |
| 3 | S1 | Negative constraints + examples | Low (30min) | High | Unanimous top-3 |
| 4 | S5 | Preamble sanitizer | Very Low (<15min) | Medium-High | Unanimous top-5 |
| 5 | S2 | Reorder prompt sections | Very Low (<15min) | Medium | Unanimous |
| 6 | S3 | Resilient parser | Low (1hr) | Medium | Unanimous |
| 7 | S7 | Configurable retry escalation | High (2-4hr) | Medium | Defer consensus |
| 8 | S8 | State persistence | Medium (2hr) | Low | Defer consensus |

---

<!-- Source: Base (original) -->
## 6. Part IV: Remediation Plan

### 6.1 Solution Descriptions

#### S1: Negative Constraints and Literal Examples

**Target**: `roadmap/prompts.py` -- all 7 `build_*_prompt()` functions

**Change**: Add negative constraints and a literal YAML example to each prompt builder.

Proposed addition to `build_extract_prompt()` (after line 52):
```python
"CRITICAL FORMAT RULES:\n"
"- Your response MUST start with --- on the very first line\n"
"- Do NOT include any preamble, thinking, or explanation before the frontmatter\n"
"- Do NOT wrap the frontmatter in code fences (no ```yaml)\n"
"- Do NOT include any text before the opening ---\n\n"
"Example of correct format:\n"
"---\n"
"functional_requirements: 12\n"
"complexity_score: 0.75\n"
"complexity_class: complex\n"
"---\n\n"
"# Requirements Extraction\n"
"...\n\n"
```

Similar additions for all other prompt builders.

#### S2: Reorder Prompt Sections

**Target**: `roadmap/executor.py:94`

**Change**: Move format instructions to the end of the prompt (after embedded content) so they are closest to the generation point in the attention window.

Current:
```python
effective_prompt = step.prompt + "\n\n" + embedded
```

Proposed:
```python
# Split prompt into role/task and format sections
# Place format section after embedded content for attention proximity
effective_prompt = step.prompt_preamble + "\n\n" + embedded + "\n\n" + step.format_instructions
```

This requires a minor refactor of the prompt builders to return structured prompt parts rather than a single string, or a simpler approach of appending a format reminder:

```python
effective_prompt = step.prompt + "\n\n" + embedded + "\n\n" + FORMAT_REMINDER
```

Where `FORMAT_REMINDER` is a constant reinforcing the output format requirements.

#### S3: Resilient Frontmatter Parser

**Target**: `pipeline/gates.py` -- `_check_frontmatter()` function

**Change**: Add a scanning fallback that searches for `---` within the first N lines if the initial `startswith("---")` check fails.

Proposed replacement for `gates.py:74-101`:
```python
def _check_frontmatter(
    content: str, required_fields: list[str], output_file: Path
) -> tuple[bool, str | None]:
    """Extract and validate YAML frontmatter fields.

    Primary: check if content starts with ---.
    Fallback: scan first 20 lines for --- delimiter pair.
    """
    stripped = content.lstrip()

    # Primary check
    if stripped.startswith("---"):
        return _parse_frontmatter_block(stripped, required_fields, output_file)

    # Fallback: scan first 20 lines for frontmatter block
    lines = content.splitlines()
    for i, line in enumerate(lines[:20]):
        if line.strip() == "---":
            remainder = "\n".join(lines[i:])
            return _parse_frontmatter_block(remainder, required_fields, output_file)

    return False, f"YAML frontmatter missing in {output_file}: no --- found in first 20 lines"
```

#### S4: Retry Feedback Injection

**Target**: `pipeline/executor.py` -- `_execute_single_step()` retry loop

**Change**: When a gate fails and a retry is about to occur, inject the gate failure reason into the step's prompt.

Proposed modification to `executor.py:224-227`:
```python
# Gate failed
_log.info("Gate failed for step '%s' (attempt %d/%d): %s", step.id, attempt, max_attempts, reason)

if attempt < max_attempts:
    # Inject gate failure feedback into retry prompt
    feedback = (
        f"\n\nPREVIOUS ATTEMPT FAILED GATE VALIDATION.\n"
        f"Failure reason: {reason}\n"
        f"You MUST fix this issue in your output. "
        f"Start your response with --- on the very first line.\n"
    )
    step = Step(
        id=step.id,
        prompt=step.prompt + feedback,
        output_file=step.output_file,
        gate=step.gate,
        timeout_seconds=step.timeout_seconds,
        inputs=step.inputs,
        retry_limit=step.retry_limit,
        model=step.model,
    )
    continue  # retry with augmented prompt
```

Note: `Step` is a dataclass, so creating a new instance with the modified prompt preserves immutability of the original.

#### S5: Preamble Sanitizer

**Target**: `pipeline/process.py` or new `pipeline/sanitize.py`

**Change**: After the subprocess completes and before gate validation, strip known LLM output artifacts from the output file.

Proposed sanitizer:
```python
def sanitize_output(file_path: Path) -> None:
    """Strip common LLM output artifacts from a pipeline output file.

    Removes:
    - Preamble text before first --- delimiter
    - Code fence wrappers around YAML frontmatter
    - Thinking/reasoning blocks before content
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find first --- line
    for i, line in enumerate(lines):
        if line.strip() == "---":
            # Strip everything before it
            cleaned = "\n".join(lines[i:])
            # Remove code fence wrappers if present
            cleaned = cleaned.replace("```yaml\n", "").replace("```\n", "")
            file_path.write_text(cleaned, encoding="utf-8")
            return
```

Integration point: call `sanitize_output()` in `roadmap_run_step()` at `roadmap/executor.py:163`, after process completion and before returning the result.

#### S6: Subprocess Isolation

**Target**: `pipeline/process.py` -- `ClaudeProcess.start()` and `build_env()`

**Change**: Implement a 4-layer isolation model:

1. **Scoped working directory**: Set `cwd` to a temporary directory or the output directory
2. **Git ceiling**: Set `GIT_CEILING_DIRECTORIES` to prevent `.claude/` discovery
3. **Isolated config**: Set `CLAUDE_CONFIG_DIR` to an empty temporary directory
4. **Env sanitization**: Strip all `CLAUDE_*` and `SUPERCLAUDE_*` environment variables

Proposed enhancement to `process.py`:
```python
def build_env(self) -> dict[str, str]:
    """Build isolated environment for the child process."""
    env = os.environ.copy()
    # Strip all Claude/SuperClaude environment variables
    for key in list(env.keys()):
        if key.startswith(("CLAUDE", "SUPERCLAUDE")):
            env.pop(key)
    # Prevent .claude/ directory discovery
    env["GIT_CEILING_DIRECTORIES"] = str(self.output_file.parent)
    return env

def start(self) -> subprocess.Popen:
    """Launch the claude process with isolation."""
    self.output_file.parent.mkdir(parents=True, exist_ok=True)
    self._stdout_fh = open(self.output_file, "w")
    self._stderr_fh = open(self.error_file, "w")

    popen_kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": self._stdout_fh,
        "stderr": self._stderr_fh,
        "env": self.build_env(),
        "cwd": str(self.output_file.parent),  # NEW: isolated working directory
    }
    if hasattr(os, "setpgrp"):
        popen_kwargs["preexec_fn"] = os.setpgrp

    self._process = subprocess.Popen(self.build_command(), **popen_kwargs)
    ...
```

#### S7: Configurable Retry Escalation (Deferred)

Replace hardcoded `retry_limit=1` with configurable per-step retry limits that escalate prompt strictness on each attempt. Deferred to PR3+ due to higher complexity.

#### S8: State Persistence (Deferred)

Add structured state persistence between pipeline runs for retry context. Deferred as low impact relative to effort.

<!-- Source: Base (original), modified per Change #4 and Change #5 -->
### 6.2 PR Implementation Sequence

<!-- Source: Base (original), modified per Change #4 — release directory references added from Variant A Section 10.1 -->
| PR | Solutions | Effort | Expected Impact | Files Modified |
|----|----------|--------|-----------------|----------------|
| PR1 | S4 + S1 + S5 + S2 | <1 hour | 70-80% failure reduction | `pipeline/executor.py`, `roadmap/prompts.py`, `roadmap/executor.py`, new `pipeline/sanitize.py` |
| PR2 | S6 | 2-4 hours | Additional 15-20% reduction | `pipeline/process.py` |
| PR3 | S3 | 1 hour | Defense in depth | `pipeline/gates.py` |
| Deferred | S7, S8 | 4-6 hours | Incremental improvement | Multiple files |

**Release directories** (pre-created):

| PR | Release Directory | Status |
|----|-------------------|--------|
| PR1 | `.dev/releases/current/v2.15-RetryFeedbackInjection/` | Created, empty |
| PR2 | `.dev/releases/current/v2.16-SubProcIsolation/` | Created, empty |
| PR3 | `.dev/releases/current/v2.17-FrontmatterParser/` | Created, empty |
| Spec artifacts | `.dev/releases/current/v2.18-cli-portify-v2/` | Contains review + spec documents |

**Cumulative expected failure reduction**: PR1 (70-80%) + PR2 (90-95%) + PR3 (95-100%).

<!-- Source: Debate evidence, inserted per Change #5 — sequencing rationale -->
#### Sequencing Rationale

The solution consensus ranks S6 (subprocess isolation) as the highest-priority solution, yet the PR sequence places it in PR2 rather than PR1. This apparent discrepancy is intentional and reflects the pragmatist debater's argument (Section 5.4.3): the quick-win solutions (S4, S1, S5, S2) collectively address 70-80% of failures at very low implementation cost (under 1 hour total), while S6 requires 2-4 hours and careful testing of multiple isolation approaches against the `claude` CLI's configuration loading behavior. Shipping the quick wins first in PR1 provides immediate reliability improvement while PR2's subprocess isolation work proceeds with the benefit of reduced failure noise. The ranking reflects *severity* (what matters most architecturally), while the PR sequence reflects *implementation pragmatics* (what ships fastest with highest cumulative impact).

<!-- Source: Invariant probe findings, inserted per Change #7 — implementation considerations -->
#### Implementation Considerations

Three implementation risks were identified during adversarial review that neither variant's original analysis addressed. These should be validated during PR implementation:

**INV-002: Sanitizer horizontal-rule ambiguity** (affects S5, PR1)
The proposed `sanitize_output()` function searches for the first `---` line and strips everything before it. However, `---` is also valid Markdown for a horizontal rule. If LLM output contains a horizontal rule before the actual YAML frontmatter delimiter, the sanitizer will incorrectly treat the horizontal rule as the frontmatter start, producing malformed output. The sanitizer should validate that content after the first `---` line parses as valid YAML before committing to that position as the frontmatter boundary.

**INV-006: S4 + S2 interaction effect** (affects PR1)
S4 (retry feedback injection) appends failure context to `step.prompt`, while S2 (format instruction reordering) moves format instructions to the end of the prompt after embedded content. If both are applied, the retry feedback from S4 will appear *before* the embedded content (since it is appended to the original prompt), while S2's format reminder appears *after*. This creates two format instruction blocks separated by potentially thousands of lines. Implementers should ensure the retry feedback is appended after the final format reminder, not after the original prompt preamble.

**INV-007: S6 cwd/path interaction** (affects PR2)
S6 proposes setting `cwd` to `self.output_file.parent` for subprocess isolation. However, the step's `input_paths` may contain relative paths resolved against the original working directory. Changing `cwd` would break those resolutions. Implementers should either (a) resolve all input paths to absolute paths before launching the subprocess, or (b) use `GIT_CEILING_DIRECTORIES` and `CLAUDE_CONFIG_DIR` isolation without changing `cwd`.

### 6.3 Verification Strategy

Each PR should include:

1. **Unit test**: A test that constructs output with preamble text and verifies the fix handles it
2. **Integration test**: A dry-run pipeline execution verifying prompt construction
3. **Regression test**: The specific `extraction.md` content from this incident, fed through the fixed gate

---

<!-- Source: Base (original) -->
## Appendix A: Guard Condition Boundary Table

Full boundary table from Section 3.6, reproduced here for standalone reference.

| ID | Guard Condition | Location | Current State | Risk | Remediation |
|----|----------------|----------|---------------|------|-------------|
| GAP-1 | Workflow file exists and is valid SKILL.md | Phase 1 entry | `STOP` instruction only | Medium | Add `Path.exists()` + frontmatter parse |
| GAP-2 | At least one step is Claude-assisted | Phase 1 exit | Not checked | High | Count classified steps, abort if all programmatic |
| GAP-3 | No circular dependencies in step graph | Phase 1 step 5 | Not checked | High | Topological sort with cycle detection |
| GAP-4 | All referenced `refs/` files exist | Phase 1 step 1 | Not checked | Medium | Glob + existence check |
| GAP-5 | Step count within context budget | Phase 1 exit | Not checked | Medium | Count steps, warn if >20, abort if >50 |
| GAP-6 | Generated models.py passes `mypy --strict` | Phase 3 exit | Not checked | High | Run `uv run mypy --strict` on generated file |
| GAP-7 | Generated gates.py checks match prompt contracts | Phase 3 exit | Not checked | Critical | Cross-reference frontmatter fields in prompts vs gates |
| GAP-8 | Generated executor.py imports resolve | Phase 3 exit | "Quick check" only | High | Run `uv run python -c "import ..."` |
| GAP-9 | Output directory does not contain existing module | Phase 3 entry | Not checked | Medium | Check for `__init__.py` existence |
| GAP-10 | main.py patch does not break existing commands | Phase 4 | Not checked | High | Run `superclaude --help` after patch |
| GAP-11 | Phase 2 prompt contracts cover all Claude-assisted steps | Phase 2 exit | Not checked | Critical | Set comparison: prompted_steps == claude_assisted_steps |
| GAP-12 | Phase 1 gates cover all step outputs | Phase 1 exit | Not checked | High | Set comparison: gated_outputs == all_step_outputs |

---

<!-- Source: Base (original) -->
## Appendix B: State Variable Registry

Full registry from Section 3.5, reproduced here for standalone reference.

| ID | Variable | Type | Set Phase | Read Phase(s) | Schema Defined | Validated |
|----|----------|------|-----------|---------------|----------------|-----------|
| SV1 | `workflow_path` | `Path` | Input | 1 | N/A | Existence only |
| SV2 | `component_inventory` | `dict[str, ComponentInfo]` | 1 | 2 | No | No |
| SV3 | `step_graph` | `list[StepSpec]` | 1 | 2, 3 | No | No |
| SV4 | `parallel_groups` | `list[list[str]]` | 1 | 2 | No | No |
| SV5 | `gate_assignments` | `dict[str, GateCriteria]` | 1 | 2, 3 | No | No |
| SV6 | `prompt_contracts` | `dict[str, PromptSpec]` | 2 | 3 | No | No |
| SV7 | `model_definitions` | `dict[str, DataclassSpec]` | 2 | 3 | No | No |
| SV8 | `generated_files` | `list[Path]` | 3 | 4 | N/A | Existence only |
| SV9 | `integration_patches` | `list[Patch]` | 2 | 4 | No | No |
| SV10 | `cli_name` | `str` | Input | All | N/A | No collision check |
| SV11 | `output_dir` | `Path` | Input/derived | 3, 4 | N/A | No collision check |

---

<!-- Source: Base (original), modified per Change #2 — Critical Code Locations table appended -->
## Appendix C: File Reference Index

Every source file cited in this report, with its role and key line references.

| File | Relative Path | Role | Key Lines Referenced |
|------|--------------|------|---------------------|
| SKILL.md | `src/superclaude/skills/sc-cli-portify/SKILL.md` | Original skill specification under review | 7-12 (metadata), 49-52 (format), 57-67 (args), 106-108 (output), 137 (gate sigs), 157-161 (codegen), 202-208 (constraints), 218 (boundaries) |
| prompts.py | `src/superclaude/cli/roadmap/prompts.py` | Prompt builders for all 7 roadmap pipeline steps | 39-60 (extract), 63-87 (generate), 90-112 (diff), 115-139 (debate), 142-165 (score), 168-197 (merge), 200-223 (test-strategy) |
| gates.py (pipeline) | `src/superclaude/cli/pipeline/gates.py` | Gate validation engine with tier-proportional checks | 19 (gate_passed signature), 25-68 (tier logic), 71-101 (_check_frontmatter) |
| gates.py (roadmap) | `src/superclaude/cli/roadmap/gates.py` | Roadmap-specific gate criteria definitions and semantic checks | 19-34 (_no_heading_gaps), 37-66 (_cross_refs_resolve), 69-84 (_no_duplicate_headings), 87-105 (_frontmatter_values_non_empty), 108-112 (_has_actionable_content), 115-136 (_convergence_score_valid), 141-247 (gate instances) |
| executor.py (pipeline) | `src/superclaude/cli/pipeline/executor.py` | Generic step sequencer with retry, gates, and parallel dispatch | 46-133 (execute_pipeline), 136-250 (_execute_single_step), 154 (max_attempts calc), 224-227 (retry continue), 253-301 (_run_parallel_steps) |
| executor.py (roadmap) | `src/superclaude/cli/roadmap/executor.py` | Roadmap-specific executor building 8-step pipeline | 53-66 (_embed_inputs), 69-170 (roadmap_run_step), 94 (effective_prompt concat), 173-281 (_build_steps), 477-517 (execute_roadmap) |
| process.py | `src/superclaude/cli/pipeline/process.py` | Subprocess lifecycle management for claude -p invocations | 24-66 (ClaudeProcess class), 69-87 (build_command), 89-98 (build_env), 100-127 (start), 104 (stdout_fh open), 109 (stdout redirect), 116 (Popen call) |
| models.py (pipeline) | `src/superclaude/cli/pipeline/models.py` | Shared pipeline data models (Step, StepResult, GateCriteria, SemanticCheck) | 17-44 (StepStatus), 58-65 (SemanticCheck), 68-74 (GateCriteria), 77-89 (Step), 92-106 (StepResult), 169-180 (PipelineConfig) |
| models.py (roadmap) | `src/superclaude/cli/roadmap/models.py` | Roadmap config and agent spec models | 17-43 (AgentSpec), 47-62 (RoadmapConfig) |
| CLAUDE.md (project) | `CLAUDE.md` (repo root) | Project-level Claude Code instructions loaded by subprocess | N/A -- entire file affects subprocess behavior |
| CLAUDE.md (global) | `/config/.claude/CLAUDE.md` | Global Claude Code instructions with persona/mode system | N/A -- references COMMANDS.md, FLAGS.md, PRINCIPLES.md, RULES.md, MCP.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md |

<!-- Source: Variant A, Section 11.2 — merged per Change #2 -->
### C.1 Critical Code Locations (Quick Reference)

Consolidated root-cause-to-code mapping for implementation reference:

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

---

<!-- Source: Variant A, Section 11.3 — merged per Change #1 -->
## Appendix D: Traceability Matrix

End-to-end traceability from spec findings through root causes, solutions, and PRs:

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

### D.1 Related Release Artifacts

| Directory | Purpose | Status |
|-----------|---------|--------|
| `.dev/releases/current/v2.15-RetryFeedbackInjection/` | PR 1 workspace | Created, empty |
| `.dev/releases/current/v2.16-SubProcIsolation/` | PR 2 workspace | Created, empty |
| `.dev/releases/current/v2.17-FrontmatterParser/` | PR 3 workspace | Created, empty |
| `.dev/releases/current/v2.18-cli-portify-v2/` | Spec review and refactoring spec | Contains review + spec documents |

---

*End of merged session findings document.*
