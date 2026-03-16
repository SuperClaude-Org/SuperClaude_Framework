---
component: quality-agents
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Quality Agents

## 1. Design Philosophy

The quality agents group exists to provide independent, specialized quality verification at different granularities: task-level (quality-engineer), audit-level (audit-validator), implementation-level (self-review), and session-level (pm-agent). The core design principle is **agent-as-verifier independence** — each quality agent is explicitly prohibited from assuming the prior agent's output is correct, and must verify claims from scratch.

**Why this design exists**: Self-verification by the same agent that produced the work is subject to confirmation bias — LLMs tend to validate their own outputs rather than genuinely challenging them. Separate quality agents with independent behavioral specifications and explicit independence instructions counter this bias. The `audit-validator`'s first instruction is: "Do NOT assume the prior agent was correct. Verify everything from scratch." (`src/superclaude/agents/audit-validator.md:16`).

**Trade-off**: Independent verification doubles the work for any given operation. A task that the primary agent completes correctly still requires the quality agent to re-verify. The system accepts this overhead on the premise that the reduction in defect escape rate justifies the cost, particularly for STRICT-tier tasks where downstream dependencies are affected.

## 2. Execution Model

**quality-engineer**: Invoked via `Task` tool for STRICT-tier verification in `sc:task-unified`. Performs: requirement analysis, test case design, test prioritization by risk, automated test framework setup, and quality risk assessment. Outputs: test strategy, test cases, automated test suites, quality assessment reports. Behavioral mindset: "think beyond the happy path to discover hidden failure modes" (`.claude/agents/quality-engineer.md:15`).

**audit-validator**: Receives a 10% stratified sample of cleanup-audit findings. Runs 4-check verification methodology:
1. Did the primary agent actually read the files cited?
2. Do grep claims match reality?
3. Are classifications correct?
4. Are DELETE recommendations safe (no false negatives on live files)?

CRITICAL FAIL condition: a false negative on DELETE (audit-validator independently confirms a file is in use but the primary agent recommended DELETE). PASS threshold: <20% discrepancy between primary and validator classifications (`src/superclaude/agents/audit-validator.md`).

**self-review**: Post-implementation reflexion partner. Runs 4 mandatory questions: tests executed with command + outcome, edge cases covered with explicit list of exclusions, requirements matched against acceptance criteria, follow-up or rollback steps needed. Outputs a brief checklist-style report, not a narrative — designed for fast consumption by the orchestrating agent (`src/superclaude/agents/self-review.md:14`).

**pm-agent**: Meta-agent layer operating at session scope. Triggers: session start (MANDATORY — restores context from Serena MCP memory), post-implementation (documents learnings), mistake detection (immediate root cause analysis), monthly maintenance (documentation health review), state questions ("現状", "進捗"). Implements PDCA self-evaluation cycle (`src/superclaude/agents/pm-agent.md:138`).

**Sampling**: `_stratified_sample()` (`src/superclaude/cli/audit/spot_check.py:49`) with `seed=42` by default produces reproducible stratified samples proportional to tier distribution. Minimum 1 sample per populated tier ensures all tier types are validated even in small finding sets.

## 3. Quality Enforcement

**Hard-coded safety gate**: `audit-validator` has a CRITICAL FAIL condition on false negative DELETE findings. This cannot be overridden by configuration — if the validator independently confirms a file is live but the primary audit recommended DELETE, the validation fails unconditionally.

**permissionMode: plan**: `audit-validator` is configured with `permissionMode: plan`, which enforces that the agent operates in read-only planning mode — it cannot modify files during validation. This architectural constraint prevents the validator from accidentally corrupting the audit it is verifying.

**Evidence-based reports**: `self-review` is explicitly designed for evidence-focused output. The instruction "Keep answers brief—focus on evidence, not storytelling" targets the LLM tendency to produce verbose rationalizations rather than concrete evidence citations.

**Hallucination red flags**: `quality-engineer` is specifically tasked with testing edge cases and boundary conditions — the failure modes most likely to be missed by an implementation agent focused on the happy path. Risk-based prioritization focuses verification effort on high-probability, high-impact areas.

**Trade-off**: The `quality-engineer` agent is invoked only for STRICT-tier tasks. STANDARD-tier tasks receive only direct test execution (no quality agent). This means a STANDARD-tier task with 3 affected files and non-trivial logic receives less verification than it might warrant — the tier classification is the sole determinant of whether quality-engineer is invoked.

## 4. Error Handling Strategy

**Verification failure escalation**: If `quality-engineer` produces a quality assessment report identifying critical risks, the result is returned to the orchestrating agent with the assessment inline. The orchestrating agent must decide how to proceed — there is no automatic rollback or halt mechanism in the quality agent itself.

**Validation PASS/FAIL**: `audit-validator` produces a binary PASS/FAIL verdict with a `<20% discrepancy` threshold. A FAIL verdict signals that the cleanup-audit findings cannot be trusted and must be re-run. The validator does not attempt to correct individual findings — it provides a verdict and a citation of the discrepancy.

**pm-agent mistake detection**: When pm-agent detects an error, it activates immediately for root cause analysis before implementation continues. The PDCA cycle's Check phase includes explicit `think_about_task_adherence` and `think_about_whether_you_are_done` prompts to force structured self-assessment.

**Trade-off**: The pm-agent's "mistake detection" trigger relies on the pm-agent being active and monitoring the session. In sessions where the pm-agent fails to activate (e.g., when Serena MCP is unavailable at session start), the automatic mistake detection is not available and errors may propagate undetected.

## 5. Extension Points

- `maxTurns` configurable per agent definition — controls per-invocation token budget ceiling.
- `permissionMode: plan` on audit-validator enforces read-only constraint; removing it would allow the validator to modify files (generally undesirable).
- PM Agent trigger conditions in agent definition frontmatter are extensible — new trigger phrases can be added without code changes.
- New quality agent roles can be added as `.md` files and installed via `superclaude install` to `~/.claude/agents/`.
- `audit-validator` CRITICAL FAIL threshold (20% discrepancy) is documented but not configurable — it is hard-coded as a safety policy.

## 6. System Qualities

**Maintainability**: Agents are `.md` files with no compiled code. Behavioral modifications are text edits that take effect immediately without a build step. Agent definitions are readable by non-developers — the intent and constraints of each agent are expressed in natural language.

**Weakness**: Agent behavior is only as correct as its Markdown specification. There is no schema enforcement or type checking on agent definitions. A malformed agent definition (e.g., conflicting instructions) will not fail at load time — it will produce subtly incorrect behavior at invocation time.

**Checkpoint Reliability**: Quality agents write reports to disk (`validation-report.md`, `self-review-report.md`). The supervisor can re-read these reports independently of the agent session. pm-agent persists session state to Serena MCP memory, enabling context restoration on next session start.

**Extensibility**: New agent roles are trivially addable as `.md` files. The `superclaude install` CLI copies them to `~/.claude/agents/` for Claude Code integration. No code changes are required to add a new specialized quality agent.

**Weakness**: The quality agent ecosystem is not formally coordinated. There is no agent registry or dependency declaration between quality agents. If `quality-engineer` should always invoke `self-review` after task completion, this relationship must be encoded in the behavioral Markdown — it cannot be enforced structurally.

**Operational Determinism**: `audit-validator` stratified sampling with `seed=42` produces reproducible sample selection for a given finding set. The PASS/FAIL threshold (20% discrepancy) is deterministic for a given primary vs. validator classification set. However, the agent's independent verification (grep re-runs, file reads) may produce different results if the filesystem has changed between primary audit and validation.
