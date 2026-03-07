# Refactoring Spec: sc:task-unified-protocol

## Current Architecture Assessment

### Current Step Count and Flow

The system is split across two files with a handoff boundary:

1. **Command layer** (`src/superclaude/commands/task-unified.md`): Performs tier classification as pure text output (no tool invocation), emits the `<!-- SC:TASK-UNIFIED:CLASSIFICATION -->` header, then dispatches to the skill for STANDARD/STRICT tiers. LIGHT and EXEMPT execute inline without skill invocation.

2. **Skill layer** (`src/superclaude/skills/sc-task-unified-protocol/SKILL.md`): Receives the pre-classified tier and executes the tier-specific workflow. Step counts per tier:
   - STRICT: 11 steps (activate project, verify git clean, load context, check memories, identify files, make changes, find importers, update affected files, spawn verification agent, run tests, answer adversarial questions)
   - STANDARD: 5 steps (load context, search impacts, make changes, run tests, verify)
   - LIGHT: 4 steps (scope check, make changes, sanity check, proceed)
   - EXEMPT: 2 steps (execute immediately, no verification)

Total distinct execution phases across the full lifecycle: Classification (1) + Confidence Display (1) + Execution (4-11) + Verification (0-2) + Feedback (1) = 7 to 16 phases depending on tier.

### Current Validation Mechanisms

All validation is inference-based. There are zero programmatic checks:

- **Tier classification**: Claude performs keyword matching, compound phrase detection, context boosting, and confidence scoring entirely through natural language reasoning. The command file instructs Claude to do this as "TEXT-ONLY" (no tools), which means Claude is manually pattern-matching keywords from a list.
- **Git cleanliness check**: Claude runs `git status` via Bash and interprets the output.
- **Verification routing**: Claude decides whether to spawn a sub-agent or run tests based on its reading of the tier.
- **Critical path override**: Claude checks file paths against `auth/`, `security/`, `crypto/`, `models/`, `migrations/` patterns by inspection.
- **Confidence threshold**: Claude self-reports a confidence score and self-enforces the <0.70 prompt rule.
- **Feedback collection**: Claude self-reports whether the user overrode the tier.

### Current Integration Points

- **MCP servers**: Serena (activate_project, memories, find_referencing_symbols), Sequential (complex reasoning), Context7 (documentation), codebase-retrieval (context loading)
- **Sub-agent spawning**: Task tool with quality-engineer persona for STRICT verification
- **Git operations**: Bash tool for `git status`, `pytest` execution
- **TodoWrite**: Task tracking during execution
- **Configuration references**: `config/tier-keywords.yaml`, `config/verification-routing.yaml`, `config/tier-acceptance-criteria.yaml` (these files are referenced but do not appear to exist in the repository -- the actual keyword lists are embedded in the command and skill markdown)

### Architectural Strengths to Preserve

1. **Two-layer separation**: Command handles classification, skill handles execution. This is a clean responsibility boundary that maps directly to a pipeline architecture (classification step + execution steps).
2. **Tier-appropriate overhead**: The graduated response (EXEMPT=0 verification, STRICT=full verification) is well-designed. The pipeline should preserve this proportionality.
3. **Escape hatches**: `--skip-compliance`, `--force-strict`, and `--compliance [tier]` overrides give users control. Any pipeline must preserve these as CLI flags.
4. **"Better false positives than false negatives" philosophy**: When uncertain, escalate to a higher tier. This is a sound safety principle.
5. **MCP circuit breaker semantics**: STRICT blocks if Sequential/Serena unavailable; other tiers allow fallbacks. This maps naturally to gate prerequisites.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement over self-referential LLM validation** | **HIGH** -- Single biggest win. Tier classification is a deterministic algorithm (keyword matching, compound phrase detection, context boosting, confidence scoring) currently executed by inference. Critical path override is regex. MCP requirement routing is a lookup table. All three are pure functions with no creative judgment required. | Implement `classify_tier(description: str, flags: dict, file_paths: list[str]) -> TierClassification` as a Python function. Returns `(tier, confidence, keywords_matched, rationale)`. Implement `check_critical_path(paths: list[str]) -> bool` as regex. Implement `resolve_mcp_requirements(tier: str) -> MCPRequirements` as lookup. The command layer becomes a CLI entry point that calls these functions before dispatching to the skill/pipeline. | **Medium** (2-3 days). The algorithm is fully specified in the command markdown; it needs translation to Python. | **CRITICAL**: Without this, classification depends on Claude correctly parsing 4 priority tiers, 40+ keywords, 8+ compound phrases, and 6+ context boosters from natural language instructions. Measured failure modes include inventing invalid tiers ("ITERATIVE", "SIMPLE", "IMPLEMENT") and inconsistent confidence scores. The command file has explicit warnings about these failures, which is evidence they occur. |
| **(b) Pure-function gate criteria** | **HIGH** -- Multiple verification points are currently subjective inference that could be objective checks. | Gates for: (1) `git_clean_gate: (str) -> tuple[bool, str]` -- parse `git status` output for clean working directory; (2) `affected_files_gate: (str) -> tuple[bool, str]` -- verify step output contains a file list with at least one entry; (3) `test_exit_code_gate: (str) -> tuple[bool, str]` -- parse pytest output for exit code 0; (4) `adversarial_coverage_gate: (str) -> tuple[bool, str]` -- verify N adversarial questions were answered (check for numbered list pattern); (5) `import_chain_gate: (str) -> tuple[bool, str]` -- verify all files importing changed modules were identified. | **Low-Medium** (1-2 days). Each gate is a simple regex/parsing function. | **HIGH**: Without gates, the only verification that STRICT steps were actually completed is Claude self-reporting. A STRICT task could skip step 7 (find importers) or step 11 (adversarial questions) and no programmatic mechanism would catch it. |
| **(c) Classification rubric: programmatic vs inference** | **HIGH** -- This is the architectural blueprint for the entire portification. | **100% Programmatic**: Tier classification (keyword + compound + context booster scoring), critical path override (regex), MCP requirement resolution (lookup), git status check (parse), test execution dispatch + exit code (subprocess), feedback logging (append to file), confidence display (template rendering). **Orchestration (programmatic dispatch, inference interpretation)**: Context loading (dispatch codebase-retrieval, Claude interprets), impact analysis (dispatch find_referencing_symbols, Claude interprets), memory check (dispatch list_memories/read_memory, Claude interprets). **100% Inference**: Code changes (Claude writes code), verification agent reasoning (sub-agent inference), adversarial question generation and answering (creative reasoning). | **Low** (0.5 days for the classification document). The classification is already implicit in the analysis; formalizing it ensures nothing is missed during implementation. | **MEDIUM**: Without an explicit rubric, implementers will either over-portify (trying to make code changes programmatic) or under-portify (leaving classification in inference). |
| **(d) Step graph with dependency resolution** | **HIGH** -- The 4 tier-specific execution paths have clear sequential dependencies that map directly to step graphs. | STRICT step graph: `classify` -> `git_clean_check` -> `[load_context, check_memories]` (parallel) -> `identify_files` -> `make_changes` -> `find_importers` -> `update_affected` -> `[spawn_verifier, run_tests]` (parallel) -> `adversarial_qa`. STANDARD step graph: `classify` -> `load_context` -> `search_impacts` -> `make_changes` -> `run_tests`. LIGHT: `classify` -> `scope_check` -> `make_changes` -> `sanity_check`. EXEMPT: `classify` -> `execute`. The step graph enables the executor to enforce ordering, parallelize where safe, and provide progress tracking. | **Medium** (1-2 days). Four step graphs to define, each with Step/GateCriteria/timeout definitions. | **HIGH**: Without a step graph, there is no mechanism to enforce that STRICT step 7 (find importers) runs before step 8 (update affected files). Steps could be reordered or skipped by inference without detection. |
| **(e) Resume/retry with exact CLI resume commands** | **MEDIUM-HIGH** -- STRICT tasks are long-running (11 steps, 60s+ verification timeout). Failure at step 8 means repeating steps 1-7 from scratch in the current architecture. | Implement state persistence: each step writes its result to a JSONL checkpoint file. On resume, the executor reads the checkpoint, identifies the last successful step, and resumes from the next step. CLI interface: `superclaude task --resume .task-unified/checkpoint.jsonl`. Context from completed steps is injected into the resume prompt. | **Medium** (2-3 days). Requires checkpoint serialization, resume logic, and context re-injection. The pipeline executor already supports step-level state tracking. | **MEDIUM**: Without resume, a STRICT task that fails at step 9 (verification) wastes all token budget from steps 1-8. For large codebases this could be 10K+ tokens lost. The risk scales with task complexity and STRICT tier frequency. |
| **(f) Budget economics via TurnLedger** | **MEDIUM** -- Token costs are specified per tier (STRICT verification: 3-5K, STANDARD: 300-500) but not enforced. Sub-agent spawning for STRICT has no budget cap. | Implement `TurnLedger` that tracks token spend per step. STRICT verification sub-agent gets a hard budget of 5K tokens (current max target). If the sub-agent exceeds budget, the diagnostic chain fires instead of allowing unbounded retry. Budget is allocated proportionally: classification (200), context loading (2K), code changes (variable, uncapped), verification (5K cap). | **Low-Medium** (1-2 days). TurnLedger pattern exists in the pipeline infrastructure; adapt for task-unified's budget targets. | **LOW-MEDIUM**: Runaway verification costs are a real risk but are bounded by Claude's max_turns. The bigger value is observability -- knowing where tokens are spent enables optimization. |
| **(g) Diagnostic chain** | **MEDIUM** -- When STRICT verification fails, the current skill provides no structured failure analysis. Claude reports "verification failed" and the user must debug manually. | Adapt the existing `DiagnosticCollector -> FailureClassifier -> ReportGenerator` pattern. For task-unified: (1) Collect: gate failure reason + step output + test stderr; (2) Classify: test failure (assertion mismatch), missing import (ModuleNotFoundError), type error (TypeError/mypy), behavioral regression (test passed before, fails now), missing file (FileNotFoundError); (3) Report: targeted fix suggestion per failure class, with exact file:line references where available. | **Low** (1 day). The `diagnostic_chain.py` module already exists in the pipeline package with the 4-stage chain (troubleshoot, root causes, solutions, summary). Adapt the stage implementations for task-unified failure patterns. | **MEDIUM**: Without diagnostics, STRICT task failures produce opaque "verification failed" messages. Users must manually investigate, which defeats the purpose of the compliance framework. |
| **(h) 4-layer subprocess isolation** | **LOW-MEDIUM** -- Only relevant for STRICT tier, which spawns a quality-engineer sub-agent. The sub-agent currently has unrestricted access to the workspace. | Layer 1 (process isolation): Sub-agent runs as a separate `claude -p` process via ClaudeProcess. Layer 2 (file scope): Sub-agent prompt specifies read-only access to changed files and test files only. Layer 3 (tool restriction): Sub-agent allowed-tools limited to Read, Grep, Bash (for pytest only). Layer 4 (output isolation): Sub-agent writes to a designated output file; gate validates output before main process consumes it. | **Medium** (2 days). ClaudeProcess exists. The main work is prompt engineering for the sub-agent to enforce file scope and tool restrictions, plus gate validation of the sub-agent's output. | **LOW**: The risk of a verification sub-agent modifying production files is real but mitigated by the sub-agent's purpose (verification, not modification). The more likely failure mode is the sub-agent consuming excessive tokens (addressed by pattern f). |
| **(i) Context injection for inter-step data flow** | **HIGH** -- The current architecture relies on Claude's context window to carry information between steps. This is fragile: if context is lost (window overflow, session reset, or simply not attended to), downstream steps operate on incomplete information. | Implement explicit context injection: (1) `classify` step outputs `TierClassification` dataclass; (2) `load_context` step outputs `ContextBundle` (file list, dependency graph); (3) `identify_files` step outputs `AffectedFileSet`; (4) `make_changes` step outputs `ChangeManifest` (files changed, diff summary); (5) `find_importers` step outputs `ImportChainMap`; (6) Each subsequent step receives the outputs of all predecessor steps as structured data in its prompt context. The pipeline executor handles this injection automatically via `step.inputs`. | **Medium** (2-3 days). Requires defining dataclass schemas for each step's output, serialization to/from the checkpoint format, and prompt injection logic. | **HIGH**: Context window loss is the primary failure mode for long-running STRICT tasks. Without explicit context injection, step 8 (update affected files) may not have access to step 5's file list if Claude's attention has drifted to step 6-7 outputs. This manifests as missed files, incomplete updates, and silent regressions. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Tier Classification** | Inference (Claude pattern-matches keywords from markdown instructions) | **Pure programmatic** (`classify_tier()` Python function) | N/A -- deterministic, no gate needed | This is the single highest-value portification target. The algorithm is fully specified, entirely deterministic, and has documented failure modes (invalid tier values). A Python function eliminates all classification errors and runs in <1ms. |
| **Confidence Display** | Inference (Claude formats a progress bar and summary) | **Pure programmatic** (template rendering from `TierClassification` output) | N/A -- presentation only | String formatting is not a valid use of inference. `f"**Tier: {tier}** [{bar}] {confidence:.0%}"` is cheaper and more consistent. |
| **Git Clean Check** (STRICT step 2) | Inference (Claude runs `git status` and interprets output) | **Hybrid** -- programmatic dispatch + programmatic parse | `git_clean_gate: (stdout) -> tuple[bool, str]` -- checks for `nothing to commit, working tree clean` or empty `--porcelain` output | Parsing `git status` output is a solved problem. No inference needed. |
| **Context Loading** (STRICT step 3, STANDARD step 1) | Inference (Claude invokes codebase-retrieval) | **Hybrid** -- programmatic dispatch, inference interpretation | `context_loaded_gate: (output) -> tuple[bool, str]` -- verify output contains at least one file reference and is non-empty | Dispatch is mechanical; interpretation requires inference. Gate ensures the step produced usable output. |
| **Memory Check** (STRICT step 4) | Inference (Claude invokes list_memories, read_memory) | **Hybrid** -- programmatic dispatch, inference interpretation | `memory_checked_gate: (output) -> tuple[bool, str]` -- verify step completed (even if no relevant memories found) | Same pattern as context loading. The memory API calls are mechanical. |
| **Identify Affected Files** (STRICT step 5, related to STANDARD step 2) | Inference (Claude reasons about which files are affected) | **Inference with programmatic gate** | `affected_files_gate: (output) -> tuple[bool, str]` -- verify output contains a structured file list (at least one file path pattern) | File identification requires codebase understanding. Gate ensures the step produced a concrete list. |
| **Make Changes** (all tiers) | Inference (Claude writes code) | **Inference** -- no portification possible | `changes_made_gate: (output) -> tuple[bool, str]` -- verify at least one Edit/Write tool was invoked (check for tool call markers in output) | Code authorship is fundamentally creative. Gate ensures the step actually modified something. |
| **Find Importers** (STRICT step 7) | Inference (Claude invokes find_referencing_symbols or grep) | **Hybrid** -- programmatic dispatch, inference interpretation | `import_chain_gate: (output) -> tuple[bool, str]` -- verify output contains file references and covers all files from step 6's change manifest | Dispatch is mechanical; interpretation of results requires judgment. Gate cross-references against the change manifest from step 6. |
| **Update Affected Files** (STRICT step 8) | Inference (Claude edits downstream files) | **Inference with programmatic gate** | `downstream_updated_gate: (output) -> tuple[bool, str]` -- verify all files identified in step 7 were addressed (each file path appears in the step's tool invocations) | Like code changes, this is creative work. Gate ensures completeness by cross-referencing step 7 output. |
| **Verification Agent** (STRICT step 9) | Inference (sub-agent spawned via Task tool) | **Programmatic dispatch, inference execution, programmatic gate** | `verification_gate: (output) -> tuple[bool, str]` -- verify sub-agent output contains pass/fail determination with evidence | The dispatch is mechanical (spawn sub-agent with specific prompt). The sub-agent's reasoning is inference. The result interpretation is regex (look for PASS/FAIL marker). |
| **Test Execution** (STRICT step 10, STANDARD step 4) | Inference (Claude runs pytest via Bash) | **Pure programmatic** (subprocess call + exit code check) | `test_gate: (exit_code, stdout) -> tuple[bool, str]` -- exit code 0 = pass, non-zero = fail with parsed failure summary | Running pytest and checking the exit code requires zero inference. This should be a direct subprocess call with structured output parsing. |
| **Adversarial Questions** (STRICT step 11) | Inference (Claude generates and answers questions) | **Inference with programmatic gate** | `adversarial_gate: (output) -> tuple[bool, str]` -- verify N questions were posed and answered (check for numbered Q/A pattern, minimum 3 questions) | Question generation and answering is creative. Gate ensures the step was not skipped or insufficiently thorough. |
| **Feedback Collection** | Inference (Claude self-reports) | **Pure programmatic** (append to JSONL log) | N/A -- logging operation | Feedback logging (tier used, override status, completion time, error count) is structured data appending. No inference needed. |
| **MCP Requirement Resolution** | Inference (Claude reads the tier-to-server mapping from markdown) | **Pure programmatic** (lookup table) | `mcp_available_gate: (tier, available_servers) -> tuple[bool, str]` -- verify required servers are available for the tier | A lookup table: STRICT requires [Sequential, Serena], STANDARD prefers [Sequential, Context7], LIGHT/EXEMPT require none. |
| **Critical Path Override** | Inference (Claude checks paths against patterns) | **Pure programmatic** (regex match against `auth/|security/|crypto/|models/|migrations/`) | N/A -- deterministic, built into classification | This is `re.search(r'(auth|security|crypto|models|migrations)/', path)`. No inference needed. |

---

## Portification Candidacy

**Recommendation: SELECTIVE ADOPTION**

### Justification

sc:task-unified-protocol is a **meta-skill that orchestrates other work**. It is not a content generator like a documentation skill or an analysis skill. This fundamentally shapes the portification strategy:

1. **Full portification is not appropriate** because the core value of the skill is its ability to invoke Claude for creative work (writing code, analyzing impact, answering adversarial questions). These phases cannot be replaced by programmatic logic.

2. **No portification is not appropriate** because the orchestration layer itself -- classification, routing, gate enforcement, progress tracking, resume -- is entirely deterministic and gains no benefit from inference. Leaving these in inference introduces documented failure modes (invalid tiers, inconsistent confidence, skipped steps).

3. **Selective adoption is the correct strategy**: Portify the orchestration skeleton (classification, dispatch, gates, context injection, budget tracking, feedback logging) while preserving inference for the creative phases (code changes, impact analysis, adversarial reasoning).

### Specific Evidence

- The command markdown contains explicit warnings about invalid tier values ("ITERATIVE", "SIMPLE", "IMPLEMENT"), proving that inference-based classification fails in practice.
- The command mandates "TEXT-ONLY" classification (no tools), which is an attempt to constrain inference to behave deterministically -- a clear signal that this should be code.
- The 11-step STRICT workflow has no resume capability, meaning a failure at step 9 wastes all prior token spend.
- The verification sub-agent has no budget cap or output validation gate.
- Context flows between steps implicitly through Claude's attention, which degrades with window length.

### Architecture Sketch

```
superclaude task "description" [--compliance tier] [--resume checkpoint]
    |
    v
[Python: classify_tier()] --> TierClassification
    |
    v
[Python: resolve_steps(tier)] --> StepGraph
    |
    v
[Python: execute_pipeline(steps, config, run_step)]
    |
    +--> Step 1: git_clean_check  [programmatic: subprocess + parse]
    +--> Step 2: load_context     [claude -p: codebase-retrieval prompt]
    +--> Step 3: identify_files   [claude -p: file identification prompt]
    +--> Step 4: make_changes     [claude -p: code change prompt, context-injected]
    +--> Step 5: find_importers   [claude -p: impact analysis prompt, context-injected]
    +--> Step 6: update_affected  [claude -p: downstream update prompt, context-injected]
    +--> Step 7: run_tests        [programmatic: pytest subprocess + exit code]
    +--> Step 8: verify           [claude -p: quality-engineer prompt, isolated subprocess]
    +--> Step 9: adversarial_qa   [claude -p: adversarial prompt]
    |
    v
[Python: log_feedback()] --> feedback.jsonl
```

Steps 1 and 7 are fully programmatic (no Claude invocation). Steps 2-6, 8-9 are Claude-assisted with programmatic gates. The executor manages ordering, retry, resume, and budget tracking.

---

## Testing Plan

### Phase 1: Unit Tests for Programmatic Functions

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| `classify_tier()` | Parameterized unit tests | 100% of keyword list, all compound phrases, all context boosters, all priority ordering scenarios |
| `classify_tier()` edge cases | Property-based (hypothesis) | Random strings never produce invalid tier values; confidence is always in [0.0, 1.0]; STRICT keywords always beat STANDARD |
| `check_critical_path()` | Parameterized unit tests | All 5 path patterns (`auth/`, `security/`, `crypto/`, `models/`, `migrations/`), negative cases, path variations |
| `resolve_mcp_requirements()` | Exhaustive unit tests | All 4 tiers, fallback-allowed flag, server availability matrix |
| `git_clean_gate()` | Parameterized unit tests | Clean output, dirty output (staged, unstaged, untracked), empty output, malformed output |
| `test_exit_code_gate()` | Parameterized unit tests | Exit code 0, 1, 2, 5 (no tests collected), 124 (timeout) |
| `affected_files_gate()` | Unit tests | Non-empty file list, empty output, malformed output |
| `adversarial_gate()` | Unit tests | 3+ Q/A pairs, fewer than 3, no Q/A pattern |
| `confidence_display()` | Snapshot tests | Correct formatting for all tiers and confidence levels |
| `resolve_steps()` | Unit tests | Correct step graph for each tier, correct dependency ordering |

### Phase 2: Integration Tests for Pipeline Compatibility

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| Step graph execution | Integration test with mock StepRunner | STRICT 11-step graph completes in order, STANDARD 5-step graph completes, gates fire at correct points |
| Resume from checkpoint | Integration test | Write checkpoint at step N, resume, verify steps 1..N are skipped, step N+1 executes |
| Parallel step groups | Integration test | `[load_context, check_memories]` execute concurrently, cross-cancellation works |
| Budget enforcement | Integration test | TurnLedger halts execution when budget exceeded, diagnostic chain fires |
| Gate failure retry | Integration test | Step fails gate, retries, passes on second attempt |
| Gate failure exhaustion | Integration test | Step fails gate after max retries, pipeline halts with diagnostic report |

### Phase 3: Regression Tests

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| Tier classification parity | Golden-file regression | 50+ real task descriptions from usage history, verify `classify_tier()` matches the expected tier from ORCHESTRATOR.md examples |
| Override behavior | Regression tests | `--compliance strict` always produces STRICT regardless of keywords; `--skip-compliance` bypasses classification; `--force-strict` overrides auto-detection |
| Backward compatibility | Smoke tests | Existing `/sc:task` invocations produce identical tier classifications under the new system |

### Phase 4: Property-Based Tests for Determinism

| Property | Generator | Assertion |
|----------|-----------|-----------|
| Tier stability | Random task descriptions | `classify_tier(desc)` called 100 times with same input always returns same output |
| Tier validity | Random strings | Output tier is always one of {STRICT, STANDARD, LIGHT, EXEMPT} |
| Confidence bounds | Random descriptions | `0.0 <= confidence <= 1.0` |
| Priority ordering | Descriptions containing both STRICT and STANDARD keywords | STRICT always wins |
| Compound phrase precedence | Descriptions matching compound phrases | Compound phrase tier overrides individual keyword tier |
| Critical path override | Random paths with/without security patterns | `check_critical_path()` is idempotent and deterministic |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Classification regression**: Python `classify_tier()` produces different results than inference-based classification for edge cases not covered by the keyword lists. | Medium (0.4) | High -- users experience unexpected tier changes, eroding trust | Golden-file regression suite with 50+ real descriptions. A/B testing: run both classifiers in parallel for 2 weeks, log disagreements, tune before cutover. |
| **Over-portification creep**: Pressure to make inference steps programmatic (e.g., "automate impact analysis") leads to brittle, low-quality automation. | Medium (0.3) | High -- programmatic impact analysis misses dependencies that Claude would catch, causing regressions | Strict adherence to the classification rubric (pattern c). Inference phases are inference by design. Code review gate: any new programmatic step must have a clear deterministic algorithm, not a heuristic. |
| **Context injection bloat**: Injecting all predecessor step outputs into each subsequent step's prompt inflates token usage beyond budget targets. | Medium (0.4) | Medium -- token costs increase, possibly exceeding STRICT budget targets | Selective injection: each step declares which predecessor outputs it needs (not all). Summary injection: large outputs (e.g., codebase-retrieval results) are summarized before injection. Budget monitoring via TurnLedger with early warning at 80% of budget. |
| **Resume state corruption**: Checkpoint file becomes inconsistent with actual workspace state (e.g., user manually edits files between resume attempts). | Low (0.2) | High -- resumed execution operates on stale assumptions, producing incorrect changes | Checkpoint includes workspace hash (git commit SHA). On resume, verify workspace matches checkpoint; if not, warn user and offer to restart from a specific step. |
| **Sub-agent escape**: Quality-engineer verification sub-agent modifies files it should only read, corrupting the workspace. | Low (0.15) | High -- verification step introduces bugs instead of catching them | Subprocess isolation via ClaudeProcess with restricted allowed-tools in the prompt. Git stash before verification; diff after; reject if unexpected changes detected. |
| **MCP server dependency**: STRICT tier requires Sequential and Serena. If either is unavailable, the pipeline blocks entirely. No graceful degradation path. | Medium (0.3) | Medium -- STRICT tasks cannot execute during server outages | Implement circuit breaker with configurable fallback: if servers unavailable for >30s, offer user choice between (a) wait, (b) downgrade to STANDARD with warning, (c) abort. Log the degradation decision. |
| **Step graph maintenance burden**: Four separate step graphs (one per tier) must be kept in sync with the skill's behavioral contract. Changes to the skill require updating the step graph. | Medium (0.35) | Low-Medium -- step graphs drift from intended behavior | Single source of truth: step graphs are defined in code, and the skill markdown is generated from them (or at minimum, a CI check verifies consistency). |
| **Pipeline executor overhead**: Adding subprocess management, gates, checkpoints, and TUI for a workflow that currently runs inline adds latency and complexity. | Medium (0.3) | Low -- increased execution time for simple tasks | LIGHT and EXEMPT tiers bypass the pipeline entirely (current behavior preserved). Only STANDARD and STRICT use the pipeline. Pipeline overhead target: <2s per programmatic step, <5s total for pipeline setup/teardown. |
| **Adoption friction**: Users accustomed to inline `/sc:task` execution may find the pipeline-based approach slower or harder to debug. | Low-Medium (0.25) | Medium -- users avoid the pipeline, negating the reliability improvements | Transparent mode: pipeline runs with Rich TUI showing step progress, making the pipeline visible and trustworthy. `--debug` flag shows full pipeline state. Inline mode preserved for LIGHT/EXEMPT. |
