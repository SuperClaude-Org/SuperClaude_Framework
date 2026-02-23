# Solution 05: Claude Behavioral Interpretation (RC5)

## Problem Summary

When `--multi-roadmap --agents opus,haiku` was requested, Claude encountered an impossible instruction: Wave 2 step 3 says "Invoke sc:adversarial" but the `Skill` tool was absent from `allowed-tools`. Claude made a rational fallback decision -- spawn `system-architect` Task agents and manually synthesize variants -- but this approximation captured only ~20% of the adversarial pipeline's functionality (variant generation + rough merge). The remaining 80% was silently dropped: no diff analysis, no structured debate with steelman requirements, no hybrid scoring with position-bias mitigation, no refactoring plan with provenance, and no return contract with convergence score.

The core behavioral failure is **silent degradation without detection**: Claude substituted a dramatically inferior process without reporting that the adversarial pipeline did not execute, and no downstream quality gate caught the omission.

## Dependency on Other Fixes

### RC1 Fix (Add Skill to allowed-tools) -- HIGH dependency

If RC1 is fixed correctly, the Skill tool becomes available and Claude can invoke `sc:adversarial` via the happy path. This eliminates the PRIMARY trigger for RC5. However, RC5 protection remains valuable for three reasons:

1. **Defense in depth**: The Skill tool could fail at runtime (skill not installed, SKILL.md corrupted, skill invocation timeout) even when present in allowed-tools. RC5 behavioral guardrails handle these secondary failure modes.
2. **Specification drift**: Future edits to SKILL.md or the command file could accidentally remove Skill from allowed-tools. A fallback protocol survives this regression.
3. **Framework pattern**: Other skills that integrate with sc:adversarial (future sc:design, sc:spec, etc.) will face the same invocation challenge. A documented fallback protocol becomes a reusable pattern.

### RC2 Fix (Rewrite Wave 2 step 3) -- MEDIUM dependency

RC2's fix rewrites the ambiguous "Invoke sc:adversarial" instruction with explicit tool-call syntax. This OVERLAPS with Option B (fallback protocol) since both modify Wave 2 step 3. The solutions should be merged into a single coherent rewrite rather than applied independently.

### RC4 Fix (Return contract data flow) -- LOW dependency

RC4 defines how return data flows back. Option D (quality gate) depends on the return contract fields existing to check against. However, the quality gate can check for artifact existence (files on disk) regardless of whether the return contract transport mechanism is formalized.

## Options Analysis

### Option A: Explicit Prohibition

> Add "DO NOT spawn Task agents directly for adversarial work; invoke sc:adversarial" to SKILL.md.

**Strengths**:
- Simple, unambiguous instruction
- Prevents the specific failure mode observed

**Weaknesses**:
- Creates an **impossible instruction** if the Skill tool is unavailable: Claude cannot invoke sc:adversarial AND cannot use alternatives. This produces unpredictable behavior -- Claude may ignore the prohibition entirely (violating the instruction), freeze (failing to produce output), or hallucinate a different workaround.
- Does not address runtime failures (skill timeout, skill not installed)
- Fragile: depends entirely on RC1 fix being in place and staying in place

**Verdict**: REJECT as standalone. The impossible-instruction scenario is worse than the current failure because it eliminates Claude's ability to make a rational approximation. However, a softer version of this ("prefer sc:adversarial invocation over manual approximation") is useful as part of Option B.

### Option B: Fallback Protocol

> Add structured inline fallback instructions that tell Claude exactly how to approximate the 5-step adversarial protocol using Task agents when sc:adversarial cannot be invoked.

**Strengths**:
- Handles BOTH the happy path (skill invocable) and the degraded path (skill unavailable)
- The fallback approximation captures significantly more of the adversarial pipeline than Claude's ad-hoc attempt (which skipped 80%)
- Self-documenting: the fallback protocol makes the adversarial pipeline's value proposition visible to Claude
- Reusable pattern for any future skill-to-skill integration

**Weaknesses**:
- Adds ~40-60 lines to Wave 2 step 3. However, this is ref-loadable content (loaded only when `--multi-roadmap` is active), so it does not bloat the base SKILL.md.
- The fallback will never match the full sc:adversarial pipeline quality (no position-bias mitigation, simplified scoring), so there is a risk of "good enough" fallback discouraging RC1 fix prioritization

**Verdict**: ACCEPT as primary. This is the only option that handles the degraded path constructively. The weakness (instruction length) is mitigated by placing the protocol in `refs/adversarial-integration.md` rather than inline.

### Option C: Pre-flight Validation

> Add a Wave 0 check that verifies not just SKILL.md existence but actual invocability (is Skill tool in allowed-tools?).

**Strengths**:
- Prevents silent degradation by detecting the problem before it manifests
- Fail-fast: user gets a clear error message rather than a degraded result
- Simple to implement (one conditional check in Wave 0)

**Weaknesses**:
- Only DETECTS the problem, does not FIX it. If the Skill tool is missing, the user gets an abort rather than a degraded-but-partially-useful result.
- Claude cannot reliably introspect its own allowed-tools list at runtime. The allowed-tools metadata in SKILL.md frontmatter is a hint to Claude, not a programmatic constraint. Claude has no `list_allowed_tools()` API. However, Claude CAN attempt a Skill tool call and observe whether it succeeds -- this is a runtime test rather than a pre-flight check.

**Revised approach**: Instead of pre-flight introspection, use a **probe-and-branch** pattern: attempt the Skill tool call, and if it fails, execute the fallback protocol. This converts Option C from a standalone detection mechanism into a branching condition for Option B.

**Verdict**: ACCEPT as modified -- not as standalone, but as the branching mechanism that triggers Option B's fallback protocol.

### Option D: Quality Gate

> Add a post-adversarial check: "If adversarial was requested but artifacts_dir is empty OR convergence_score is missing, the adversarial pipeline did not run. ABORT and report the failure."

**Strengths**:
- Catches ANY variant of this failure mode, regardless of root cause
- Simple to implement: check for expected artifacts after the adversarial step
- Works even if the failure mode changes (new ways the pipeline could silently degrade)
- Defense in depth: catches failures that Options A-C miss

**Weaknesses**:
- Reactive, not preventive: by the time the quality gate fires, tokens have been spent on the degraded approximation
- An abort-on-failure gate without a fallback means the user gets nothing. Better to combine with Option B so the fallback produces artifacts that pass a relaxed gate.

**Revised approach**: Two-tier quality gate:
1. **Full gate**: Check for all 5 adversarial artifacts (diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md) + convergence_score. If all present, PASS.
2. **Fallback gate**: If fallback protocol was used (detected by a `fallback_mode: true` marker), check for at minimum: variant files + a simplified merge + a convergence estimate. If present, PASS WITH WARNING. If absent, ABORT.

**Verdict**: ACCEPT as complementary to Option B. The quality gate ensures that even the fallback protocol produces minimum viable output.

## Recommended Solution: B + C(modified) + D(two-tier)

Combine three options into a layered defense:

1. **Layer 1 (Prevention)**: Attempt Skill tool invocation (modified Option C)
2. **Layer 2 (Structured Degradation)**: If invocation fails, execute inline fallback protocol (Option B)
3. **Layer 3 (Verification)**: Post-adversarial quality gate validates that either the full pipeline or the fallback produced adequate output (Option D)

This approach handles the full failure cascade:
- Happy path: Skill tool works, sc:adversarial runs, full quality gate passes
- Degraded path: Skill tool fails, fallback protocol runs, relaxed quality gate passes with warning
- Total failure: Neither path produces output, quality gate aborts with clear diagnostic

## Implementation Details

### Change 1: Modify `refs/adversarial-integration.md` -- Add Invocation Protocol section

Add after the existing "Invocation Patterns" section:

```markdown
---

## Invocation Protocol

### Happy Path: Skill Tool Invocation

When Wave 1A or Wave 2 requires sc:adversarial, the PRIMARY invocation method is the Skill tool:

1. **Attempt invocation**: Call the Skill tool with `skill: "sc:adversarial"` and the appropriate args string constructed from the invocation patterns above.
2. **On success**: Consume the return contract per "Return Contract Consumption" section below. Proceed normally.
3. **On failure**: If the Skill tool call fails (tool not available, skill not found, invocation error), activate the Fallback Protocol below. Do NOT silently substitute a simplified process.

### Fallback Protocol: Inline Adversarial Approximation

**Activation**: ONLY when the Skill tool invocation in the Happy Path above fails. Log the failure reason before proceeding.

**Announcement**: Before executing the fallback, emit:
```
"WARNING: sc:adversarial skill invocation failed (<reason>). Executing inline fallback protocol.
Fallback produces a reduced adversarial analysis (no position-bias mitigation, simplified scoring).
For full adversarial pipeline, ensure Skill tool is in allowed-tools and sc:adversarial is installed."
```

**Fallback steps** (approximating the 5-step adversarial protocol using Task agents):

**Step F1: Variant Generation** (parallel Task agents)
- For each agent in --agents spec, dispatch a Task agent with prompt:
  "Generate a {generation_type} artifact from the following source. Use {persona} perspective. {instruction}"
- Collect all variant outputs. Write to `<output-dir>/adversarial/variant-N-<model>-<persona>.md`
- If fewer than 2 variants produced, ABORT.

**Step F2: Diff Analysis** (single Task agent)
- Dispatch a Task agent with the analytical prompt:
  "You are a diff analyst. Compare these {N} variants and produce a structured diff analysis.
   For each topic covered by the variants:
   1. Identify structural differences (section ordering, hierarchy)
   2. Identify content differences (different approaches to same topic)
   3. Detect contradictions (opposing claims, requirement-constraint conflicts)
   4. Extract unique contributions (ideas in only one variant)
   Organize output with severity ratings: Low/Medium/High."
- Write output to `<output-dir>/adversarial/diff-analysis.md`

**Step F3: Simplified Debate** (parallel Task agents, 1 round)
- For each variant, dispatch an advocate Task agent with prompt:
  "You are an advocate for Variant {N}. Given the diff analysis and all variants:
   1. STEELMAN each opposing variant (state their strongest argument)
   2. Present your variant's strengths with evidence (cite sections)
   3. Critique opposing variants with evidence
   4. Acknowledge genuine weaknesses in your variant
   For each diff point, state which variant's approach is superior and why."
- Collect all advocate responses.
- NOTE: Fallback runs only 1 round regardless of --depth setting. Log: "Fallback: single debate round (full protocol requires sc:adversarial for multi-round debate)"

**Step F4: Scoring and Base Selection** (single Task agent)
- Dispatch a Task agent with prompt:
  "You are a scoring judge. Given {N} variants, the diff analysis, and advocate arguments:
   1. For each diff point, determine winner variant and confidence (50-100%)
   2. Score each variant on: requirement coverage, internal consistency, specificity, clarity
   3. Select the strongest variant as base
   4. List strengths from non-base variants to incorporate
   5. Estimate convergence: (agreed diff points / total diff points)"
- Write output to `<output-dir>/adversarial/base-selection.md`
- Extract convergence_score from the scoring output.

**Step F5: Merge** (single Task agent)
- Dispatch a Task agent with prompt:
  "You are a merge executor. Given the base variant and the incorporation list from scoring:
   1. Start from the base variant text
   2. For each strength to incorporate: integrate it at the appropriate location
   3. Add provenance comments: <!-- Source: Variant N, Section X -->
   4. Validate: no contradictions introduced, all references resolve
   5. Produce the merged output."
- Write merged output to `<output-dir>/<merged-artifact>.md`
- Write merge log to `<output-dir>/adversarial/merge-log.md`

**Fallback Return Contract**:
After Step F5, construct the return contract fields:
```yaml
status: "partial"  # Always "partial" for fallback (never "success")
merged_output_path: "<path to merged output>"
convergence_score: <extracted from Step F4>
artifacts_dir: "<path to adversarial/ directory>"
unresolved_conflicts: <count of unresolved diff points from Step F4>
fallback_mode: true  # Marker indicating fallback was used
```

**Fallback limitations** (documented in merge-log.md):
- No position-bias mitigation (single-pass evaluation only)
- Single debate round (vs. 1-3 rounds in full protocol)
- No 25-criterion binary rubric (simplified holistic scoring)
- No tiebreaker protocol
- convergence_score is an estimate, not a precise measurement
```

### Change 2: Modify `refs/adversarial-integration.md` -- Add Post-Adversarial Quality Gate section

Add after the "Error Handling" section:

```markdown
---

## Post-Adversarial Quality Gate

After any adversarial invocation (happy path or fallback), validate that the pipeline produced adequate output before proceeding.

### Full Pipeline Gate (happy path)

Check for ALL of the following in `<output-dir>/adversarial/`:
- [ ] At least 2 variant files exist and are non-empty
- [ ] `diff-analysis.md` exists and is non-empty
- [ ] `debate-transcript.md` exists and is non-empty
- [ ] `base-selection.md` exists and is non-empty
- [ ] `refactor-plan.md` exists and is non-empty
- [ ] `merge-log.md` exists and is non-empty
- [ ] Merged output file exists at `merged_output_path`
- [ ] `convergence_score` is present and is a number between 0.0 and 1.0
- [ ] `status` is "success" or "partial"

**All checks pass**: Proceed normally.
**Any check fails**: Log which checks failed. If `status` was "success" but artifacts are missing, downgrade to "partial" and log warning. If merged output is missing entirely, ABORT.

### Fallback Pipeline Gate (fallback_mode: true)

Check for ALL of the following:
- [ ] At least 2 variant files exist and are non-empty
- [ ] `diff-analysis.md` exists and is non-empty
- [ ] `base-selection.md` exists and is non-empty
- [ ] Merged output file exists at `merged_output_path`
- [ ] `convergence_score` is present and is a number between 0.0 and 1.0

**All checks pass**: Proceed with warning: "Adversarial results produced via fallback protocol. Quality is reduced compared to full sc:adversarial pipeline."
**Any check fails**: ABORT with: "Adversarial fallback protocol failed to produce minimum viable output. Missing: <list of failed checks>. Cannot proceed with --multi-roadmap."

### No Adversarial Output Gate

If adversarial mode was requested (`--multi-roadmap` or `--specs`) but:
- `artifacts_dir` does not exist or is empty, AND
- No return contract fields are populated, AND
- No fallback warning was emitted

Then the adversarial pipeline **did not execute at all**. This is the exact failure mode from the original incident.

**Action**: ABORT with: "CRITICAL: Adversarial mode was requested but no adversarial pipeline executed. This indicates a framework configuration error. Verify that the Skill tool is in allowed-tools and sc:adversarial is installed."
```

### Change 3: Modify sc:roadmap `SKILL.md` -- Update Wave 2 step 3

In the existing Wave 2, step 3 currently reads (abbreviated):
> If `--multi-roadmap`: parse agent specs... Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md`...

Replace with:

```markdown
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Expand model-only agents with the primary persona from Wave 1B. If agent count >= 5, orchestrator is added automatically. Execute sc:adversarial integration per `refs/adversarial-integration.md` "Invocation Protocol" section (attempt Skill tool invocation first; if unavailable, execute fallback protocol). Handle return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section. Validate output per `refs/adversarial-integration.md` "Post-Adversarial Quality Gate" section. The adversarial output replaces template-based generation.
```

### Change 4: Modify sc:roadmap `SKILL.md` -- Update Wave 1A step 2

Similarly, update Wave 1A step 2 to reference the invocation protocol:

Current:
> Invoke sc:adversarial with `--compare` mode per `refs/adversarial-integration.md`...

Replace with:
> Execute sc:adversarial integration with `--compare` mode per `refs/adversarial-integration.md` "Invocation Protocol" section (attempt Skill tool invocation first; if unavailable, execute fallback protocol).

### Change 5: Modify sc:roadmap `SKILL.md` -- Update allowed-tools

This change is shared with the RC1 solution. Add `Skill` to allowed-tools:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

## Blast Radius Assessment

### Files Modified

| File | Change Type | Risk |
|------|------------|------|
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | ADD 2 new sections (~120 lines) | LOW -- additive only, no existing behavior changed |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | MODIFY Wave 1A step 2, Wave 2 step 3, allowed-tools | MEDIUM -- changes behavioral instructions for adversarial path |
| `.claude/skills/sc-roadmap/refs/adversarial-integration.md` | SYNC from src/ | LOW -- mirror of source |
| `.claude/skills/sc-roadmap/SKILL.md` | SYNC from src/ | LOW -- mirror of source |

### Behavioral Impact

- **Non-adversarial paths (no --multi-roadmap, no --specs)**: ZERO impact. The invocation protocol and quality gate are only loaded and executed when adversarial mode is active.
- **Adversarial happy path (Skill tool available)**: MINIMAL impact. Adds one explicit Skill tool call attempt (which succeeds) and one post-pipeline quality gate check. Net effect: slightly more rigorous validation.
- **Adversarial degraded path (Skill tool unavailable)**: MAJOR POSITIVE impact. Instead of silent degradation to ~20% pipeline coverage, the fallback protocol delivers ~60-70% coverage with explicit warnings and a quality gate.
- **Total failure path (nothing works)**: POSITIVE impact. Clear abort message instead of silent degradation.

### Risk of Regression

- **Fallback protocol correctness**: The 5-step fallback is an approximation. If the Task agent prompts are poorly calibrated, the fallback output could be low quality. Mitigated by: (a) the quality gate catches empty/missing artifacts, (b) the "partial" status marker ensures downstream consumers know this is reduced-quality output.
- **Instruction bloat**: Adding ~120 lines to adversarial-integration.md increases the ref document size. Mitigated by: this ref is only loaded during adversarial mode waves, not during standard roadmap generation.
- **Overlap with RC1/RC2 fixes**: If all three fixes are applied, the fallback protocol may never execute (because the happy path always succeeds). This is acceptable -- the fallback is insurance, not the primary path.

## Confidence Score

**0.82** -- High confidence that this solution addresses the observed failure mode and its variants.

**Confidence breakdown**:
- Fallback protocol design: 0.85 -- The 5-step fallback mirrors the adversarial pipeline structure and is grounded in the actual SKILL.md specification. The Task agent prompts are reasonable approximations.
- Quality gate effectiveness: 0.90 -- Artifact existence checks are deterministic and catch the exact failure observed (no adversarial artifacts produced).
- Invocation protocol (probe-and-branch): 0.70 -- Claude's ability to detect Skill tool unavailability at runtime is somewhat uncertain. The Skill tool may fail in ways that are not cleanly caught (timeout vs. tool-not-found vs. skill-not-installed produce different error signatures). The branching logic assumes Claude can distinguish "tool not available" from "skill execution failed."
- Interaction with RC1 fix: 0.85 -- If RC1 is applied, this solution becomes pure insurance. The risk is that it is never tested (because the happy path always works) and silently bitrots. Mitigated by the quality gate, which validates both paths equally.

**Residual risk**: The fallback protocol's quality is inherently lower than the full adversarial pipeline. If the Skill tool is chronically unavailable (RC1 not fixed), users will receive consistently degraded output. The "partial" status marker and explicit warnings mitigate this but do not eliminate it.

---

*Solution designed 2026-02-22. Addresses RC5 (Rank 2, score 0.79) from ranked-root-causes.md.*
*Recommended implementation order: Apply after RC1 fix (solution-01) and coordinate with RC2 fix (solution-02) for Wave 2 step 3 rewrite.*
