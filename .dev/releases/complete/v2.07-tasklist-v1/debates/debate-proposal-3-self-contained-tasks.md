# Adversarial Debate: Integration Strategy 3 — Self-Contained Task Item Quality Gate

**Date**: 2026-03-04
**Proposal**: Add a generation quality rule enforcing that each task description is standalone and action-oriented
**Spec Target**: `/sc:tasklist` v1.0 (`sc-tasklist-command-spec-v1.0.md`)
**Source Pattern**: `rf:taskbuilder_v2` self-containment enforcement
**Debate Format**: ADVOCATE vs. CRITIC with synthesis

---

## The Proposal Under Debate

Enforce that each generated task includes enough context to execute without external chat history:

1. Add gate to section 7 Style Rules: "Each task description must be standalone and action-oriented"
2. Add to section 9 Acceptance Criteria: "No task requires conversational context outside the generated files to understand execution intent"
3. Does NOT add new task fields -- it is a generation quality rule applied to existing output format

---

## ADVOCATE Position: Self-Containment Is the Single Most Important Quality Gate

### Argument 1: The Session Boundary Is a Hard Wall, Not a Suggestion

The Sprint CLI launches each phase as a separate `claude --print --no-session-persistence` subprocess (confirmed in `process.py:83-100`). The `--no-session-persistence` flag is explicit: there is no session state carried between phases. The `build_prompt()` method even warns the executor directly:

> "Previous phases have already been executed in separate sessions. Do not re-execute work from prior phases."

This means any context established during Phase 1 execution -- variable names discovered, architectural decisions made, file paths explored -- is gone by Phase 2. A task that says "Configure rate limiting" without specifying which file, which middleware pattern, or which API endpoints is not a task. It is a wish. The executor must re-derive every piece of context from scratch, consuming turns, burning tokens, and risking a different interpretation than the generator intended.

Self-containment is not a quality luxury. It is a correctness requirement imposed by the runtime architecture.

### Argument 2: Delegation Safety Requires Zero Ambient Context

The `/sc:task-unified` system supports delegation via `--delegate` flags. When a task is delegated to a sub-agent, that sub-agent receives only the task content and the files it is pointed at. It does not receive the conversation history of the parent agent. It does not receive the roadmap. It does not receive the spec.

A self-contained task works identically whether executed by:
- A human developer reading the tasklist
- The Sprint CLI in automated mode
- A delegated sub-agent within a larger orchestration
- A different AI model entirely

Without self-containment, the task is coupled to a specific execution context that may or may not exist. This is the definition of a fragile interface.

### Argument 3: The Taskbuilder Proved This Pattern Works Under Pressure

The `rf:taskbuilder_v2` reference was production-tested in a headless agent execution context (per `taskbuilder-integration-proposals.md` line 13). Its strongest pattern -- explicitly cited in `tasklist-spec-integration-strategies.md` line 64 -- is self-contained checklist items. The rationale is stated directly:

> "context loaded in batch 1 is lost by batch 3+"

This is not theoretical. It was observed in production. Tasks that lacked embedded context caused execution failures, re-derivation loops, and wasted compute. The pattern exists because the alternative was tested and failed.

### Argument 4: This Is a Quality Rule, Not a Feature Addition

The proposal explicitly states: "Does NOT add new task fields." It does not introduce `Context:`, `Verify:`, or `Blocked-Until:` fields. Those are Proposal 1 from `taskbuilder-integration-proposals.md` -- a v1.1 feature that changes the task schema.

Strategy 3 is a generation discipline. It tells the generator: "When you write the task description, include enough information that the executor knows what to do." This is the difference between:

- "Configure rate limiting" (fails self-containment)
- "Add rate limiting middleware to `src/middleware/rateLimit.ts` using the express-rate-limit pattern from `src/middleware/auth.ts`, targeting 100 req/min per IP on all `/api/v2/*` routes" (passes self-containment)

Both use the same task format. Both have the same metadata fields. The second one works in isolation. The first one does not. This is a generation quality rule, and it belongs in v1.0 Style Rules because Style Rules govern how task content is written, not what fields exist.

### Argument 5: Reduced Human Intervention Is a Direct ROI Metric

Every task that fails self-containment is a task that may require human intervention during Sprint execution. The Sprint CLI is designed to run unattended across phases. Each intervention breaks the automation chain, requires a human to provide missing context, and defeats the purpose of deterministic generation.

If the generator produces 35 tasks across 7 phases (as in the v2.05 sprint example), and 20% fail self-containment, that is 7 potential interruption points. In a 4-hour sprint, each interruption costs 15-30 minutes of context-switching. The self-containment gate costs zero runtime overhead (it is a generation-time quality check) and prevents these interruptions entirely.

---

## CRITIC Position: Self-Containment Creates Verbose, Bloated Tasks That Violate DRY

### Argument 1: Task Descriptions Become Paragraphs Instead of Concise Items

The ADVOCATE's "good" example is 40+ words for a single task title. Scale this across 35 tasks in a sprint and the phase files balloon from concise action checklists into essay-length documents. The current v1.0 task format is:

```markdown
- [ ] T01.03 - Implement rate limiting middleware
  - Effort: M | Risk: moderate | Tier: STANDARD
  - Dependencies: T01.01, T01.02
```

Under self-containment enforcement, this becomes:

```markdown
- [ ] T01.03 - Add rate limiting middleware to src/middleware/rateLimit.ts using
  the express-rate-limit pattern established in src/middleware/auth.ts, targeting
  100 requests per minute per IP address on all /api/v2/* routes, reading the
  rate limit configuration from src/config/limits.json
  - Effort: M | Risk: moderate | Tier: STANDARD
  - Dependencies: T01.01, T01.02
```

The task title is now a paragraph. This is not a style improvement; it is a regression in readability. The Sprint TUI renders task titles in a fixed-width table. Long titles get truncated or wrap awkwardly. The generator is now optimizing for a consumption model (isolated execution) at the expense of every other consumption model (human review, TUI display, progress tracking).

### Argument 2: The Sprint CLI Executor Has Access to the Full Phase File

Look at the `build_prompt()` method in `process.py:39-80`. The prompt is:

```
/sc:task-unified Execute all tasks in @{phase_file} --compliance strict --strategy systematic
```

The `@{phase_file}` syntax loads the entire phase file into the executor's context. The executor does not receive tasks one at a time in isolation. It receives the full phase file, which contains:
- The phase heading with its name and scope
- All tasks in the phase with their dependencies
- The end-of-phase checkpoint

Additionally, the executor operates within a repository that has all source files, the roadmap, and the spec available via `Read`, `Grep`, and `Glob` tools. The executor is not a blind agent receiving a single task string -- it is a full Claude Code session with tool access.

Self-containment solves a problem that does not exist in the actual execution architecture. The executor already has context. Embedding that context into every task description is redundant.

### Argument 3: Self-Containment Conflicts with DRY Across Tasks in the Same Phase

Consider a phase with 5 tasks that all operate on the same middleware layer:

```
T03.01 - Add rate limiting middleware
T03.02 - Add request validation middleware
T03.03 - Add CORS configuration middleware
T03.04 - Add compression middleware
T03.05 - Integration test all middleware
```

Under self-containment, each task must independently specify: the middleware directory path, the existing middleware pattern to follow, the Express app configuration file, and the test file conventions. This context is identical across all 5 tasks. It is repeated 5 times.

This violates DRY at the task level. The phase heading and the preceding tasks already establish the middleware context. Task T03.04 does not need to re-explain the middleware pattern -- the executor has already processed T03.01 through T03.03 in the same session and phase file.

### Argument 4: This Is a v1.1 Feature, Not a v1.0 Parity Item

The PRD (section 2, goal 5) states: "Achieves exact functional parity with the current v3.0 generator -- no new features." The non-goals (section 3) are explicit: "No new generator features beyond what v3.0 already does."

The current v3.0 generator does not enforce self-containment. It generates concise task titles with metadata. Adding a self-containment quality gate is, by definition, a new feature -- a new constraint that changes generator behavior and output content.

The integration strategies document (`tasklist-spec-integration-strategies.md`) itself classifies this as Strategy 3 of 5 compatible integrations and recommends it as the 4th item to implement (line 143): "4. Add self-contained task quality gate (Strategy 3)." It is not positioned as a parity requirement; it is positioned as an improvement.

The v1.0 spec should ship with exact parity. Self-containment belongs in v1.1, where it can be properly specified, tested against real Sprint CLI executions, and evaluated for its impact on task readability and phase file size.

### Argument 5: The "Standalone" Criterion Is Ambiguous and Unverifiable by the Generator

What does "standalone" mean? The ADVOCATE defines it as "enough context to execute without external chat history." But the generator itself cannot verify this. The generator does not know:
- What tools the executor has access to
- What files exist in the repository at execution time
- What changes prior phases made
- What the executor's context window size is

"Standalone" is a subjective judgment that cannot be reduced to a mechanical check. The pre-write validation checklist (Strategy 5) can verify structural properties: "task has non-empty description," "task ID follows format." But it cannot verify semantic self-containment. This makes the gate unenforceable as a hard rule and prone to inconsistent application.

Compare this to the other proposed quality gates: "All task IDs follow T<PP>.<TT> format" is mechanically verifiable. "Each task description must be standalone" is not. Adding an unverifiable gate to a deterministic pipeline introduces subjectivity into a system designed to eliminate it.

---

## SYNTHESIS

### Summary of Positions

| Dimension | ADVOCATE | CRITIC |
|-----------|----------|--------|
| Core claim | Self-containment is a correctness requirement imposed by session isolation | Self-containment is a quality improvement that creates bloat |
| Session boundary | Hard wall -- no state carries across phases | Soft boundary -- phase file provides full context within a session |
| DRY impact | Acceptable cost for execution safety | Unacceptable duplication across co-located tasks |
| v1.0 scope | Quality rule, not a feature (no schema change) | New constraint that changes output, therefore a feature |
| Verifiability | Generator can enforce "action-oriented with explicit targets" | "Standalone" is subjective and unverifiable by machine |
| Evidence | Taskbuilder production failures validate the pattern | Sprint CLI architecture already provides context redundantly |

### Where the ADVOCATE Is Right

The session boundary argument is strong and grounded in code. The Sprint CLI uses `--no-session-persistence` and explicitly warns executors that "previous phases have already been executed in separate sessions." Between phases, context is genuinely lost. A task in Phase 3 cannot rely on discoveries made during Phase 1 execution. The delegation argument is also valid: sub-agents receive even less context than phase executors.

The "quality rule, not a feature" framing is technically correct. The proposal does not change the task schema. It constrains how existing fields are populated. This is analogous to adding "variable names must be descriptive" to a coding standard -- it changes output quality without changing the language grammar.

### Where the CRITIC Is Right

The DRY argument is valid within a single phase. Five middleware tasks in the same phase file will share context, and repeating it 5 times is wasteful. The executor processes the entire phase file in one session, so intra-phase context is available.

The verifiability argument is the strongest CRITIC point. "Standalone" is not mechanically checkable with the same precision as "task ID follows T<PP>.<TT> format." The generator cannot objectively determine whether a task description contains "enough" context. This creates an unfalsifiable quality gate in an otherwise deterministic system.

The v1.0 parity argument has merit but is weaker than it appears. The proposal does not change what the generator outputs structurally -- it changes the quality bar for existing content. Style Rules (section 7) already constrain how content is written ("lean output, no registries"). Adding "standalone and action-oriented" is an incremental tightening of existing style constraints, not a new feature.

### Verdict

**Adopt a weakened version for v1.0. Full self-containment is a v1.1 feature.**

The ADVOCATE correctly identifies a real problem (inter-phase context loss), but the CRITIC correctly identifies that the proposed solution is too broad and unverifiable as stated. The right answer is to split the proposal:

### Recommended Modifications

**For v1.0 -- adopt as a Style Rule (section 7) with bounded scope:**

```markdown
## Style Rule Addition (section 7)

Each task description must:
1. Name the specific file(s) or module(s) it targets (no "configure the system" without a path)
2. Use an action verb that implies a concrete output (create, add, modify, delete, configure)
3. Not depend on context established only during execution of prior tasks within the same phase

Exception: tasks within the same phase may reference shared context established in the
phase heading or in a preceding setup/scaffolding task explicitly marked as a context provider.
```

**For v1.0 -- adopt as an Acceptance Criterion (section 9):**

```markdown
## Acceptance Criterion Addition (section 9)

No task title consists solely of a generic action without a target artifact
(e.g., "implement feature" is rejected; "implement rate limiting in src/middleware/rateLimit.ts" is accepted).
```

**Defer to v1.1:**

- Full self-containment with embedded `Context:` and `Verify:` fields (Proposal 1 from `taskbuilder-integration-proposals.md`)
- Cross-phase self-containment verification (requires dependency graph analysis)
- Machine-verifiable self-containment scoring

### Rationale for This Split

1. The v1.0 version catches the worst offenders (vague tasks with no target) without requiring paragraph-length descriptions
2. The "specific file or module" requirement is mechanically verifiable (does the description contain a path-like string?)
3. The DRY exception for intra-phase context preserves conciseness within a single phase
4. The full self-containment pattern with new fields is properly scoped as a v1.1 schema enhancement where it can be tested against real Sprint CLI execution data
5. This preserves the deterministic character of the pipeline by avoiding a subjective "standalone enough?" judgment

### Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| v1.0 weakened rule is insufficient for cross-phase safety | Medium | Monitor Sprint CLI execution failures in v1.0; use data to calibrate v1.1 self-containment rules |
| "Specific file" requirement over-constrains exploratory tasks | Low | Clarification Tasks (marked with warning indicator) are exempt since they are discovery-oriented by nature |
| Style Rule is ignored by the generator due to lack of enforcement | Medium | Pair with Strategy 5 (Pre-Write Validation) which can mechanically check for path-like strings in task descriptions |

---

## Appendix: Evidence References

| Source | Location | Relevance |
|--------|----------|-----------|
| Sprint CLI subprocess isolation | `src/superclaude/cli/sprint/process.py:83-100` | Confirms `--no-session-persistence` and separate sessions per phase |
| Sprint CLI prompt construction | `src/superclaude/cli/sprint/process.py:39-80` | Shows `@{phase_file}` gives executor full phase context |
| Taskbuilder self-containment rationale | `taskbuilder-integration-proposals.md` lines 20-62 | Production evidence for self-containment pattern |
| Integration strategies ranking | `tasklist-spec-integration-strategies.md` lines 62-79 | Strategy 3 definition and value statement |
| v1.0 parity constraint | `sc-tasklist-command-spec-v1.0.md` section 2, goal 5 | "Exact functional parity with v3.0 -- no new features" |
| Example task verbosity | `v2.05-sprint-cli-specification/tasklist/tasklist.md` | Current concise task format baseline |
