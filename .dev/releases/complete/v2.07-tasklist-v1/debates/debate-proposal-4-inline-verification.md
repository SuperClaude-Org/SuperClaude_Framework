# Adversarial Debate: Integration Strategy 4 — Inline Verification Coupling per Task

**Date**: 2026-03-04
**Proposal**: Add per-task inline verification criteria to `/sc:tasklist` v1.0 output
**Source**: `tasklist-spec-integration-strategies.md` (Strategy 4) + `taskbuilder-integration-proposals.md` (Proposal 5)
**Base Spec**: `sc-tasklist-command-spec-v1.0.md`
**Agents**: Opus (Advocate) vs. Haiku (Critic)

---

## Proposal Summary

Add a `Verify:` field (or equivalent near-field completion criterion) to each generated task, co-locating acceptance criteria with the task content so the Sprint CLI executor has explicit done-criteria in scope at execution time. The `§8 Sprint Compatibility Self-Check` would reject tasks lacking explicit completion conditions. No schema expansion required — maps to existing task metadata/description conventions.

---

## ADVOCATE Position (Opus)

### Argument 1: The Executor Needs Explicit Done-Criteria in Its Context Window

The Sprint CLI executor launches a `claude -p` subprocess per phase with `/sc:task-unified` (see `process.py:build_prompt()`). The prompt instructs the executor to run verification per tier:

```
- For STRICT tier tasks: use Sequential MCP for analysis, run quality verification
- For STANDARD tier tasks: run direct test execution per acceptance criteria
```

The phrase "per acceptance criteria" presupposes that the acceptance criteria are present in the phase file the executor is reading. **If the criteria are vague, absent, or detached from the task, the executor must invent its own definition of "done."** An LLM executor inventing its own acceptance criteria is the definitional case of interpretation drift — the generator's intent diverges from the executor's interpretation across a session boundary.

**Evidence**: The current v3.0 task format (§6B.2) includes `Acceptance Criteria` (4 bullets) and `Validation` (2 bullets) fields. However, the current `§5 Enrichment` algorithm and `§8 Self-Check` do NOT enforce that these fields contain *specific, testable* criteria. Nothing prevents the generator from emitting:

```markdown
**Acceptance Criteria:**
- Implementation is complete
- Tests pass
- Code quality is acceptable
- Documentation is updated
```

These are generic platitudes, not verifiable conditions. An inline verification coupling rule would require criteria that reference specific artifacts, commands, or observable outcomes — making the existing fields actually useful rather than ceremonially present.

### Argument 2: Co-location Prevents Criteria from Being Overlooked

The alternative to inline verification is a separate "Definition of Done" section, a QA pass in a later phase, or reliance on the executor's general intelligence. All three approaches share a structural weakness: the criteria are not in the same visual/contextual scope as the action.

In the Sprint CLI execution model, each phase runs in an isolated `claude -p` session (`executor.py:68`). The executor reads one phase file. If verification criteria live in the index file, a separate spec, or a later phase, they are **outside the executor's context window**. The executor literally cannot see them.

The taskbuilder's `"ensuring..."` clause pattern works because it places the done-condition inside the same sentence as the action. When an LLM reads "Implement rate limiting middleware, ensuring the middleware exports a configurable `rateLimit()` function and tests pass for 429 response on exceeded limit," the verification criteria are syntactically inseparable from the action. They cannot be skipped, deferred, or forgotten.

### Argument 3: Enables Programmatic Completion Checking

If every task has a structured `Verify:` field with concrete criteria, downstream tooling can parse these fields and automate completion checking. Consider:

1. **Sprint CLI dry-run enhancement**: A future `--verify-criteria` flag could check that every task has non-empty, non-generic verification criteria before execution starts.
2. **Post-execution audit**: A script can extract all `Verify:` fields and cross-reference them against the phase completion report's evidence column.
3. **Regression testing**: Verification criteria from completed sprints become a test suite for regression detection.

Without a structured, per-task verification field, these capabilities require natural language parsing of free-text task descriptions — unreliable and brittle.

### Argument 4: Reduces Interpretation Drift Across Session Boundaries

Sprint CLI executes phases in separate sessions. Session 1 might generate the tasklist. Session 2 executes Phase 1. Session 3 executes Phase 2. Each session starts with zero context beyond what is written in the phase file.

If a task says "Implement rate limiting" without verification criteria, the Phase 2 executor might:
- Implement a basic token bucket and declare done
- Implement sliding window rate limiting with Redis backing
- Add rate limiting but skip edge cases (burst handling, header feedback)

All three interpretations are valid readings of "implement rate limiting." Inline verification criteria eliminate this ambiguity: "Verify: `rateLimit()` exported, 429 response on exceeded limit, X-RateLimit-* headers present in response." Now the executor has an unambiguous target.

### Argument 5: Low Implementation Cost, High Compatibility

The proposal explicitly states "no schema expansion required." The v3.0 task format already has `Acceptance Criteria` and `Validation` fields (§6B.2). The integration strategy merely:

1. Adds a generation quality rule to `§5 Enrichment` requiring these fields contain specific, testable criteria (not generic platitudes)
2. Adds a self-check gate to `§8` rejecting tasks with empty or generic completion conditions
3. Optionally adds a compact `Verify:` summary line for executor quick-reference

This is a quality enforcement change, not a structural change. It costs approximately zero additional tokens per task (the fields already exist) and requires only a constraint on their content quality.

---

## CRITIC Position (Haiku)

### Argument 1: The v3.0 Task Format Already Has Acceptance Criteria and Validation Fields

The Advocate frames this as filling a gap, but the gap does not exist. Examine the current §6B.2 task format:

```markdown
**Acceptance Criteria:** (exactly 4 bullets)
- ...

**Validation:** (exactly 2 bullets)
- Manual check: ...
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)
```

Every task already has 6 dedicated verification slots (4 acceptance criteria + 2 validation bullets). The v1.0 spec (§9, Acceptance Criterion 8) already requires: "all tasks have complete metadata fields (Effort, Risk, Tier, Confidence, Verification Method)." Adding a redundant `Verify:` field creates **three separate places** where completion conditions might live: `Acceptance Criteria`, `Validation`, and `Verify`. This is not co-location — it is fragmentation.

If the concern is that acceptance criteria are too generic, the fix is to tighten the generation rules for the existing `Acceptance Criteria` field, not to add a new field that must be kept consistent with the other two.

### Argument 2: Tier Classification Already Implies Verification Level

The spec's tier system (§5.3 + Appendix) already defines verification routing:

| Tier | Verification Method | Agent | Timeout |
|------|---------------------|-------|---------|
| STRICT | Sub-agent (quality-engineer) | 3-5K tokens | 60s |
| STANDARD | Direct test execution | 300-500 tokens | 30s |
| LIGHT | Skip verification | 0 | 0s |
| EXEMPT | Skip verification | 0 | 0s |

The Sprint CLI executor (`process.py:build_prompt()`) already routes verification by tier:
- STRICT: "use Sequential MCP for analysis, run quality verification"
- STANDARD: "run direct test execution per acceptance criteria"
- LIGHT: "quick sanity check only"
- EXEMPT: "skip formal verification"

Adding per-task inline verification duplicates the tier system's job. A LIGHT task should not need inline verification criteria because the executor is instructed to perform only a "quick sanity check." An EXEMPT task should not need them at all. Mandating verification fields for tasks where verification is explicitly skipped creates noise — fields that exist only to satisfy a schema requirement, not to serve a purpose.

### Argument 3: Generating Good Verification Criteria from Roadmap Text Is Unreliable

The generator's input is a roadmap — a planning document, not a specification. Roadmaps contain items like:

- "Improve error handling across the platform"
- "Add monitoring and observability"
- "Harden authentication flow"

From "improve error handling," what verification criteria can the generator reliably produce? The honest answer is one of:

1. **Generic**: "Verify: Error handling is improved" — adds no value
2. **Invented**: "Verify: All endpoints return structured error JSON with error codes" — the generator invented a specific implementation that may not match the project's actual error handling patterns
3. **Trivially safe**: "Verify: Tests pass" — true of every task, adds no signal

The generator has access only to the roadmap text (§2 Input Contract: "Treat the roadmap as the only source of truth"). It cannot inspect the codebase, read existing tests, or understand the project's conventions. Any specific verification criteria it generates are, by definition, **hallucinated from inference rather than grounded in evidence**. This violates §0 Non-Leakage Rule 2: "Do not invent existing code, architecture, libraries."

The taskbuilder can produce good `"ensuring..."` clauses because it operates in an interactive context where the user has described the specific implementation. The tasklist generator operates from a roadmap — a fundamentally different input fidelity level.

### Argument 4: This Adds Fields That Will Be Generic and Useless

Empirically, when generators are required to produce verification criteria for every item in a batch, the criteria converge toward a small set of generic patterns:

- "Tests pass"
- "No linting errors"
- "Code review approved"
- "Documentation updated"
- "Feature works as expected"

These criteria are true of every task in every project. They consume tokens, occupy space in the executor's context window, and provide zero discriminating signal. The executor gains nothing from reading "Verify: Tests pass" because the executor already knows to run tests (that is what "run direct test execution" means in the prompt).

The cost is not zero. Each `Verify:` field adds 20-50 tokens per task. A 30-task sprint adds 600-1500 tokens of verification criteria. If 80% of those criteria are generic platitudes, the net effect is 480-1200 wasted tokens that dilute the executor's attention on the actual task content.

### Argument 5: The Sprint CLI Executor Defines Its Own Completion Gates

The Sprint CLI's `build_prompt()` method already defines a structured completion protocol:

```
1. Write a phase completion report to {result_file} containing:
   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL),
     tasks_total, tasks_passed, tasks_failed
   - Per-task status table: Task ID, Title, Tier, Status
     (pass/fail/skip), Evidence
   - Files modified (list all paths)
   - Blockers for next phase (if any)
   - The literal string EXIT_RECOMMENDATION: CONTINUE or HALT
```

The executor already has a comprehensive completion protocol. It must produce a status per task, evidence per task, and a recommendation. Adding inline verification criteria to the task format attempts to pre-specify what the executor should check, but the executor is an LLM agent with `/sc:task-unified --compliance strict --strategy systematic` — it is already designed to determine appropriate verification for each task based on its tier, content, and the codebase state at execution time.

Pre-specifying verification from a roadmap (which lacks codebase context) may actually harm execution quality by constraining the executor to check things that are irrelevant while missing things that matter. The executor, having access to the actual codebase, is better positioned to determine verification criteria than the generator.

### Argument 6: Self-Check Enforcement Creates False Confidence

Adding "Reject tasks lacking explicit completion condition" to §8 Self-Check sounds rigorous, but in practice it creates a perverse incentive: the generator must produce a verification field for every task or fail validation. When forced to produce criteria it cannot ground in evidence, the generator will produce generic criteria to pass the gate. The self-check then passes (every task has a `Verify:` field), creating the illusion of quality without the substance.

This is the "checkbox compliance" anti-pattern: the presence of a field is verified, but its quality cannot be programmatically assessed. A self-check that says "every task has verification criteria" tells you nothing about whether those criteria are useful. It is a false positive factory.

---

## REBUTTAL: Advocate Responds to Critic

### On "Fields Already Exist" (Critic Argument 1)

The Critic is correct that `Acceptance Criteria` and `Validation` fields exist in the v3.0 format. But the Critic conflates field existence with field quality. The proposal is not "add a new field" — it is "enforce that existing verification-adjacent fields contain specific, testable content." If the Critic agrees the existing fields are often generic, then the Critic agrees the problem exists. The disagreement is only about the solution mechanism (new field vs. tightened rules on existing fields), which is a minor implementation detail, not a fundamental objection.

### On "Tier Implies Verification" (Critic Argument 2)

Tier classification tells the executor *how much* verification to do, not *what* to verify. "Run quality verification" is an instruction class, not a verification criterion. The executor still needs to know: verify *what*, exactly? The tier system and per-task criteria are complementary, not redundant.

### On "Hallucination Risk" (Critic Argument 3)

This is the strongest objection. The Advocate concedes that the generator cannot produce implementation-specific criteria from roadmap text alone. However, the generator can produce *category-appropriate* criteria:
- For "add API endpoint" tasks: "Verify: endpoint responds to specified HTTP method, returns documented status codes"
- For "write tests" tasks: "Verify: test suite runs and covers specified scenarios"
- For "update documentation" tasks: "Verify: document exists at target path, covers specified topics"

These are not hallucinations — they are category patterns that any competent executor would check. The value is in making them explicit so the executor does not overlook them, not in specifying implementation details the generator cannot know.

---

## REBUTTAL: Critic Responds to Advocate

### On "Category-Appropriate Criteria" (Advocate Rebuttal on Hallucination)

The Advocate's examples prove the Critic's point. "Endpoint responds to specified HTTP method" — what method? The roadmap says "add API endpoint." The generator does not know if it is GET, POST, or PATCH. "Returns documented status codes" — what documentation? The generator cannot reference documentation it has not read. These are still inferences dressed as criteria.

If the criteria are truly category patterns ("API tasks check for response codes"), they belong in the executor's tier-specific verification protocol, not repeated in every task. The executor, running with `/sc:task-unified --compliance strict`, already has access to verification patterns via the tier system. Putting category patterns in every task is the definition of duplication.

### On "Complementary, Not Redundant" (Advocate Rebuttal on Tiers)

If the Advocate agrees that tier classification tells the executor how much verification to do, and the Advocate also wants to tell the executor what to verify, the question is: who is better positioned to determine what to verify — the generator (which has only roadmap text) or the executor (which has the actual codebase)? The executor wins this comparison on every dimension: it has access to actual file contents, existing tests, project conventions, and runtime state. Deferring "what to verify" to the executor is not a gap; it is the correct architectural choice.

---

## SYNTHESIS

### Verdict: CONDITIONAL ACCEPT with Significant Modifications

The debate reveals a genuine tension between two valid architectural positions:

1. **Advocate's core insight is correct**: The executor benefits from having explicit, grounded completion criteria in its context window. Session isolation means the executor cannot look up criteria from external sources. Co-location of action and verification is a sound principle.

2. **Critic's core insight is also correct**: The generator, operating from roadmap text alone, cannot reliably produce specific, implementation-grounded verification criteria. Mandating a field that the generator will fill with generic content creates noise, not signal. The existing `Acceptance Criteria` and `Validation` fields already occupy the verification space.

### Resolution: Tighten Existing Fields, Do Not Add New Ones

The optimal path is **not** to add a `Verify:` field (the Critic is right about redundancy), but **also not** to leave the existing fields unenforced (the Advocate is right about the quality gap).

### Recommended Modifications

**1. Add Quality Rules to §5 Enrichment for Existing Acceptance Criteria**

Instead of a new `Verify:` field, add generation quality constraints to the existing `Acceptance Criteria` and `Validation` fields in §5 Enrichment:

```markdown
### §5.7 Acceptance Criteria Quality Rules

Each task's Acceptance Criteria (4 bullets) must satisfy:
1. At least 2 of 4 criteria must reference a specific artifact type
   (file, endpoint, function, test, configuration) — not abstract outcomes
2. At least 1 criterion must be executable (a command, test, or
   assertion that produces pass/fail)
3. No criterion may use subjective language without a concrete qualifier
   ("works correctly" is prohibited; "returns 200 for valid input" is acceptable)
4. Criteria must be derivable from the roadmap item — do not invent
   implementation details not implied by the roadmap text

Each task's Validation (2 bullets) must satisfy:
1. Manual check must specify what to inspect (not "check it works")
2. Evidence must specify the artifact type to produce (test log,
   screenshot, spec file, diff output)
```

**2. Extend §8 Self-Check with Criteria Quality Gate**

Add to the §8.1 Semantic Quality Gate:

```markdown
13. Every task's Acceptance Criteria contain at least 2 artifact-referencing
    criteria and at least 1 executable criterion. Reject tasks with all-generic
    criteria ("tests pass", "code works", "documentation updated" without
    specifics).
```

**3. Do NOT add a separate `Verify:` field**

The existing `Acceptance Criteria` (4 bullets) and `Validation` (2 bullets) provide 6 verification slots per task. This is sufficient. Adding a 7th verification location creates fragmentation without improving signal quality.

**4. Tier-appropriate enforcement**

Apply criteria quality rules proportionally to tier:
- **STRICT**: Full enforcement — all 4 acceptance criteria must meet quality rules
- **STANDARD**: Moderate enforcement — at least 2 of 4 must meet quality rules
- **LIGHT**: Minimal enforcement — at least 1 must be non-generic
- **EXEMPT**: No enforcement — criteria may be generic or omitted

This addresses the Critic's valid point that mandating detailed verification for EXEMPT tasks creates useless noise.

### Impact Assessment

| Dimension | Before | After |
|-----------|--------|-------|
| Per-task verification slots | 6 (existing, unenforced) | 6 (existing, quality-enforced) |
| New fields added | — | 0 |
| Schema changes | — | None |
| §5 Enrichment additions | — | §5.7 (quality rules for existing fields) |
| §8 Self-Check additions | — | Check #13 (criteria quality gate) |
| Token cost per task | 0 | 0 (no new fields; existing field content improves) |
| Hallucination risk | N/A | Mitigated by Rule 4 ("derivable from roadmap item") |
| Sprint CLI executor impact | No change | Better criteria in context window at execution time |

### Confidence: 0.78

The synthesis preserves the Advocate's co-location principle while addressing the Critic's redundancy and hallucination concerns. The main residual risk is that quality enforcement on acceptance criteria is harder to validate programmatically than field presence — but this is an inherent limitation of any criteria quality system, not specific to this approach.

### Dissenting Note

If a future version adds a compact summary field (e.g., a one-line `Done-When:` that summarizes the 4 acceptance criteria for executor quick-scanning), this could be revisited as a UX optimization rather than a verification mechanism. Such a field would be a rendering convenience, not a new source of truth. This is a v1.1+ consideration.
