# Adversarial Debate: Integration Strategy 2 — Single-Pass Clarification Rules

**Date**: 2026-03-04
**Proposal**: Add Single-Pass Clarification Rules for missing/ambiguous inputs
**Base Spec**: `sc-tasklist-command-spec-v1.0.md` (sections 5.4, 5.6)
**Reference**: `tasklist-spec-integration-strategies.md` Strategy 2
**Debate format**: ADVOCATE vs CRITIC with SYNTHESIS

---

## Proposal Under Debate

Adapt taskbuilder's "ask once for gaps" principle to non-interactive mode:

1. If required input is missing or ambiguous, perform **one deterministic fallback resolution attempt**
2. If still unresolved, **fail with a concise structured error** listing exact missing fields
3. Expand Section 5.4 Input Validation with one-pass resolution for ambiguous path/state
4. Add structured validation errors to Boundaries (Will)

**Current behavior**: Section 5.4 validates file existence (`roadmap-path` resolves to readable file, `--spec` resolves if provided, `--output` parent exists) but does NOT validate roadmap content quality. A roadmap with no headings and a single paragraph silently falls back to the 3-bucket default (Section 4.2: Phase 1 Foundations, Phase 2 Build, Phase 3 Stabilize) with no user warning.

---

## ADVOCATE Position: Fail-Fast with Diagnostics Is Critical

### Argument 1: Silent Bad Output Is Worse Than Loud Failure

The current spec produces output from ANY structurally valid file. A roadmap containing `"TODO: fill this in later"` or a changelog accidentally passed as roadmap input will generate a 3-phase tasklist with fabricated phase names and tasks derived from meaningless content. The operator sees files written to disk and assumes success. The failure is discovered minutes or hours later when a human reviews the output or when Sprint CLI executes nonsensical tasks.

**Evidence from spec**: Section 4.2 explicitly states: "If no headings exist, create exactly 3 buckets: Phase 1: Foundations, Phase 2: Build, Phase 3: Stabilize." This is a catch-all that treats zero-structure input identically to a well-structured roadmap with three natural phases. There is no signal to the operator that the fallback activated.

**Cost of silent failure**: In a CI pipeline, a malformed tasklist propagates downstream. Sprint CLI consumes it, spawns agents against meaningless tasks, burns tokens, and produces artifacts that must be discarded. The debugging cycle starts at "why are my sprint results wrong?" and works backward through the entire pipeline before reaching "the roadmap was bad." With fail-fast diagnostics, the debugging cycle is zero steps: the error message tells you what was wrong before any downstream work begins.

### Argument 2: CI Automation Demands Structured Exit Codes and Error Messages

The spec states in Section 3 Non-Goals: "No integration with `superclaude sprint run`." But the output IS consumed by Sprint CLI. This is a pipeline. Pipelines require reliable signal propagation. A generator that always succeeds (exit 0 equivalent, always writes files) is a pipeline antipattern because downstream stages cannot distinguish "valid output" from "generator fell through to defaults."

Structured validation errors enable:
- CI gates: `if /sc:tasklist fails -> block sprint run`
- Operator diagnostics: exact field names and resolution attempts shown
- Retry logic: operator fixes the specific missing field and reruns
- Audit trails: validation failures are logged, not silently swallowed

Without structured errors, the only CI strategy is post-hoc output validation -- parsing the generated tasklist to determine if it looks "real." This duplicates the generator's own parsing logic and is strictly less reliable than failing at the source.

### Argument 3: One-Pass Resolution Is the Minimal Viable Improvement

The proposal is not asking for interactive clarification or multi-round resolution. It asks for exactly one deterministic fallback attempt -- which the spec ALREADY does for `--output` derivation (Section 5.4 item 4: "derive TASKLIST_ROOT from roadmap content using the Section 3.1 algorithm"). The proposal simply extends this pattern to other ambiguous inputs.

Concrete examples of one-pass resolution:
- **Missing `--output`**: Already resolved via Section 3.1 algorithm (scan for `.dev/releases/current/<segment>/`, then version token, then fallback to `v0.0-unknown/`). This IS a one-pass resolution. The proposal merely asks for the same treatment of other ambiguities.
- **Roadmap has no parseable items** (Section 4.1 finds zero items): One-pass attempt: check if file is empty, check if file is binary, check if content matches known non-roadmap patterns (changelog, README). If still zero items after one pass, fail with: `"Roadmap parsing produced 0 items. File appears to be [empty|binary|non-roadmap content]. Expected: markdown with headings, bullets, or numbered lists."`
- **Ambiguous phase structure**: The 3-bucket fallback in Section 4.2 is itself a resolution strategy. The proposal adds a diagnostic: `"WARNING: No phase/milestone/version headings found. Falling back to 3-phase default (Foundations/Build/Stabilize). If this is unintended, add ## headings to your roadmap."`

### Argument 4: Reduced Debugging Time Is Measurable

Every silent fallback that produces output adds a debugging step. The operator must:
1. Notice the output looks wrong (requires human review)
2. Determine which part is wrong (phases? tasks? metadata?)
3. Trace backward to the generator input
4. Determine what the generator did with that input (requires reading the spec)
5. Fix the input and rerun

With fail-fast diagnostics, steps 1-4 collapse to: "Read the error message." This is not a theoretical improvement -- it is the difference between a 5-minute investigation and a 5-second read. For CI pipelines that run unattended, steps 1-4 may never happen at all without structured errors, because no human is reviewing the output before Sprint CLI consumes it.

### Argument 5: The Spec Already Has an Incomplete Version of This Pattern

Section 5.4 validates file existence but not content viability. This creates an inconsistency: the spec cares enough about input quality to check "is the file readable?" but not "does the file contain parseable roadmap content?" The proposal completes the validation layer that Section 5.4 started.

The `--output` derivation in Section 3.1 already implements fail-through-with-default logic (try `.dev/releases/current/<segment>/`, try version token, fall back to `v0.0-unknown/`). The proposal asks for the same pattern applied to roadmap content parsing, with the addition: if the final fallback activates, emit a diagnostic warning rather than proceeding silently.

---

## CRITIC Position: This Over-Constrains the Generator

### Argument 1: Deterministic Fallback IS the Design Intent

The v3.0 generator is explicitly designed to handle ANY input. Section 1 Objective states: "Given a roadmap (unstructured or structured), produce a canonical task list." The word "unstructured" is deliberate. The generator's value proposition is that it works with messy, incomplete, poorly-formatted roadmaps -- not just pristine markdown documents.

Section 4.2's 3-bucket fallback is not a bug. It is the spec's answer to "what if the roadmap has no structure?" The answer is: impose structure deterministically. The generator does not need the user to provide structure; it manufactures structure from chaos. Adding fail-fast validation undermines this core capability.

**The "works with any roadmap" promise**: If the generator rejects inputs that lack headings, or warns on inputs that trigger the 3-bucket fallback, it is no longer a universal transformer. It becomes a validator-that-sometimes-generates. Operators who deliberately pass unstructured brainstorm documents, meeting notes, or raw feature lists will get errors instead of useful (if imperfect) tasklists.

### Argument 2: Content Quality Validation Duplicates the Generator's Own Parsing

The generator already parses roadmap items (Section 4.1), determines phase buckets (Section 4.2), and converts items to tasks (Section 4.4). Every "quality check" the proposal adds is a redundant pre-parse of the same content:

- "Check if file has parseable items" = running Section 4.1 twice
- "Check if file has phase headings" = running Section 4.2 twice
- "Check if content matches non-roadmap patterns" = heuristic that does not exist in the spec and must be invented

This is classic YAGNI. The generator's parsing algorithm IS the validation. If Section 4.1 finds zero items, the generator produces an empty tasklist -- which is already a clear signal. If Section 4.2 finds no headings, the 3-bucket fallback produces a reasonable default. Adding a pre-validation layer that duplicates this logic increases spec complexity without improving outcomes.

The proposal also introduces a new category of bugs: disagreements between the pre-validation and the generator. If the pre-validator says "no parseable items" but the generator's Section 4.1 algorithm would have found items (because the validator uses different heuristics), the user gets a false rejection.

### Argument 3: Failing on Ambiguous Input Breaks the Non-Interactive Contract

The spec explicitly states in Section 3 Non-Goals: "No interactive mode or progressive generation." Fail-fast validation is a form of interaction: the generator says "I cannot proceed, fix your input." This creates a mandatory round-trip that was explicitly excluded from v1.0 scope.

In a CI pipeline, a fail-fast error does not help unless there is a human or automated system ready to respond to it. For truly automated pipelines, the generator that always produces output (even imperfect output) is MORE useful than one that halts and waits for intervention. The 3-bucket fallback, while imperfect, gives downstream stages something to work with. A validation error gives them nothing.

**The "fix and retry" assumption**: The proposal assumes operators can fix their input and rerun. But in many workflows, the roadmap is generated upstream (by another agent, a project management tool, an export script). The operator calling `/sc:tasklist` may not control the roadmap's structure. Telling them "your roadmap has no headings" is not actionable if they cannot modify the roadmap.

### Argument 4: YAGNI for v1.0 Parity Scope

The spec's Section 2 Goal states: "Achieves exact functional parity with the current v3.0 generator -- no new features." The current v3.0 generator does not validate roadmap content quality. It does not emit structured errors. It does not warn on fallback activation. Adding these behaviors is a new feature, regardless of how it is framed.

The parity constraint exists for a reason: v1.0 is a packaging exercise (command/skill pair), not a feature release. Every new behavior introduced in v1.0 must be tested, documented, and maintained. Structured validation errors require:
- Error message format specification
- Error code enumeration
- Documentation of what each error means
- Test cases for each validation path
- Regression testing to ensure valid roadmaps are not false-rejected

This is scope creep masked as "hardening." The integration strategies document itself labels this as a v1.0 integration, but the effort it introduces (structured error format, one-pass resolution logic, fallback diagnostics) is development work that goes beyond repackaging.

### Argument 5: Warning on Fallback Activation Creates Noise Without Value

The proposal suggests emitting warnings when the 3-bucket fallback activates. But the v3.0 generator is a batch process consumed by Sprint CLI. Warnings in the output stream are:

- Not machine-parseable unless a warning format is specified (more spec surface area)
- Not visible in CI logs unless the invoking command captures and displays them
- Not actionable if the operator cannot modify the roadmap
- Noise if the operator deliberately passed an unstructured input

The 3-bucket fallback is a FEATURE for unstructured inputs. Warning the user that their unstructured input triggered unstructured-input handling is tautological. The output itself (3 phases named Foundations/Build/Stabilize) is the diagnostic. An operator who sees these phase names and expected custom phases knows immediately what happened.

### Argument 6: The `--spec` Flag Conflict Is a Separate Problem

The debate context mentions that `--spec` flag semantics are undefined (how spec interacts with roadmap on conflict). This is real, but it is not solved by fail-fast validation. It is solved by specifying `--spec` merge semantics. Adding validation errors for `--spec` conflicts conflates two separate issues: input validation and input interpretation. The proposal should not be used as a vehicle to resolve `--spec` ambiguity.

---

## SYNTHESIS

### Scorecard

| Criterion | ADVOCATE | CRITIC | Weight |
|-----------|----------|--------|--------|
| CI automation value | Strong: structured errors enable pipeline gates | Moderate: always-produce-output also valid for CI | 20% |
| Spec consistency | Strong: completes the validation pattern 5.4 started | Moderate: current behavior is internally consistent | 15% |
| Parity constraint | Weak: this IS new behavior | Strong: v1.0 = repackaging, not features | 25% |
| Debugging improvement | Strong: measurable reduction in investigation time | Moderate: output IS diagnostic (3-bucket names) | 15% |
| "Works with any input" | Weak: fail-fast reduces input tolerance | Strong: universal transformer is core value | 15% |
| Implementation cost | Moderate: one-pass resolution is bounded | Strong: error format, test cases, false-rejection risk | 10% |

### Weighted Assessment

- **ADVOCATE total**: 0.65 -- strong on CI value and debugging, weak on parity and universality
- **CRITIC total**: 0.68 -- strong on parity constraint and design intent, moderate elsewhere

### Verdict: CRITIC WINS WITH CONDITIONS

The CRITIC's core argument is correct: v1.0 is a parity release and the deterministic fallback is an intentional design choice, not a defect. Adding fail-fast validation is a new feature that expands scope, introduces implementation cost, and risks breaking the "works with any roadmap" promise.

However, the ADVOCATE identifies a real problem: silent fallback activation gives operators no signal that their input was handled differently than expected. The 3-bucket fallback IS diagnostic (the output phase names are a signal), but only to operators who know the spec well enough to recognize them.

### Recommended Modifications

**Accept (minimal, parity-compatible)**:

1. **Add diagnostic metadata to output, not validation errors to input**. Instead of fail-fast, add a `## Generation Notes` section to `tasklist-index.md` that records which fallbacks activated:
   ```markdown
   ## Generation Notes
   - Phase structure: Fallback (no headings detected; used 3-bucket default)
   - TASKLIST_ROOT: Derived from version token `v2.07`
   - Roadmap items parsed: 14
   - Clarification tasks generated: 2
   ```
   This preserves "always produce output" while giving operators a diagnostic trail. It is output metadata, not input validation -- consistent with parity scope.

2. **Add one structural validation to Section 5.4**: Validate that the roadmap file is non-empty and contains at least one non-whitespace line. An empty file is not an "unstructured roadmap" -- it is no roadmap. This is a file-level check consistent with the existing "resolves to a readable file" validation. Fail with: `"Roadmap file is empty: <path>"`

**Defer to v1.1 (out of parity scope)**:

3. **Structured error format specification** -- requires error code enumeration, test matrix, and documentation. Genuine feature work.

4. **One-pass content quality resolution** -- requires heuristics for detecting non-roadmap content (changelogs, READMEs, binary files). These heuristics do not exist in v3.0 and would be new logic.

5. **`--spec` conflict semantics** -- real gap but separate from input validation. Should be its own spec section, not grafted onto Strategy 2.

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Generation Notes adds spec surface area | Low | 4 lines in index template; no behavioral change |
| Empty-file check is over-restrictive | Very Low | Only catches truly empty files, not sparse content |
| Deferred items create v1.1 tech debt | Low | Documented as explicit v1.1 scope in spec |
| Operators still miss fallback diagnostics | Medium | Generation Notes is passive; active warnings deferred |

### Final Recommendation

**Do not add fail-fast validation or structured input errors in v1.0.** Instead, add passive Generation Notes to the index file output so that fallback activations are recorded in the artifact. Add a single empty-file guard to Section 5.4. Defer all other validation enhancements to v1.1 where they can be designed as a cohesive feature with proper error format specification and test coverage.

This preserves the generator's core value (works with any input), respects the parity constraint (no new behavioral features), and gives operators a diagnostic trail (Generation Notes) without introducing pipeline-breaking failures.
