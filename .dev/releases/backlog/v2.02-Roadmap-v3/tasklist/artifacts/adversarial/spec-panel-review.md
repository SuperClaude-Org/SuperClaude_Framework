# Specification Panel Review: claude -p Headless Invocation for sc:roadmap Adversarial Pipeline

**Specification Version**: 1.0-draft (2026-02-23)
**Review Date**: 2026-02-23
**Panel Size**: 6 domain experts
**Mode**: CRITIQUE

---

=== KARL WIEGERS -- Requirements Engineering ===

FINDING-W1: [CRITICAL] Return contract schema mismatch between specification and sc:adversarial SKILL.md
- Issue: The specification defines 10 fields for the return contract (Section 3.7), including `schema_version`, `failure_stage`, `fallback_mode`, and `invocation_method`. However, the sc:adversarial SKILL.md "Return Contract (FR-007)" section (line 339-350) defines only 5 fields: `merged_output_path`, `convergence_score`, `artifacts_dir`, `status`, `unresolved_conflicts`. The specification adds 5 new fields but claims only 1 is new ("9 original + 1 new"). The actual original contract has 5 fields, not 9.
- Evidence: Section 3.7 states "10 fields total (9 original + 1 new)" but sc:adversarial SKILL.md FR-007 defines exactly 5 fields. The implementation details section (T05.07, lines 1525-1588) also shows only 5 fields.
- Recommendation: Correct the field count arithmetic. The actual situation is: 5 original fields (from sc:adversarial SKILL.md FR-007) + 5 new fields (`schema_version`, `base_variant`, `failure_stage`, `fallback_mode`, `invocation_method`). Alternatively, clarify which "9 original" fields are referenced -- if these 9 come from the current sc:roadmap SKILL.md fallback (line 144), that must be explicitly stated with a citation to the current source of truth.
- Impact: Implementers will have an incorrect mental model of what already exists vs. what they are adding, leading to either missing fields or duplicated work.

FINDING-W2: [MAJOR] `unresolved_conflicts` type inconsistency
- Issue: The specification (Section 3.7) defines `unresolved_conflicts` as `<integer> | ~` (a count). The sc:adversarial SKILL.md T05.07 (line 1551-1554) defines it as `type: "list[string]"` containing diff point IDs. The sc:adversarial FR-007 (line 349) defines it as a list: `["<list of unresolved items>"]`. The tasklist T06.01 acceptance criteria (line 150) states "`unresolved_conflicts` typed as `integer` in both."
- Evidence: Section 3.7 line: `unresolved_conflicts: <integer> | ~`. sc:adversarial SKILL.md line 1551: `type: "list[string]"`. These are incompatible types.
- Recommendation: Decide on one type. If the specification intends to change the type from list to integer, this is a breaking schema change that must be explicitly called out. If the intent is to preserve the list type, fix Section 3.7 to use `list[string]`. Add a migration note if the type is changing.
- Impact: Producer (sc:adversarial) and consumer (sc:roadmap) will disagree on field type, causing YAML parse failures or silent data loss at runtime.

FINDING-W3: [MAJOR] Acceptance criteria for T01.01 test 4 are insufficiently measurable
- Issue: Test 4 (behavioral adherence mini-test) uses a "3-category binary checklist" but the criteria are qualitative. "Multi-step execution?" asks for "evidence of more than a single-pass comparison (round markers, scoring matrix, or base selection)" -- this is ambiguous. What counts as a "round marker"? What if the output has a scoring section but no explicit "round" label?
- Evidence: Section 3.1, test 4 criteria: "Multi-step execution? Output shows evidence of more than a single-pass comparison (round markers, scoring matrix, or base selection)."
- Recommendation: Define concrete, machine-verifiable checks. For example: "File count in output directory >= 2" (already covered by criterion 3), "diff-analysis.md contains at least 2 distinct section headings", "output contains the literal strings 'Round' or 'Score' or 'Base Selection'". Provide exact grep patterns.
- Impact: Test 4 pass/fail will be subjective, potentially leading to different implementers reaching different conclusions about viability.

FINDING-W4: [MINOR] Missing requirement for headless session stderr handling
- Issue: The command template (Section 2.2) uses `2>/dev/null` to discard stderr. No requirement specifies what happens if stderr contains actionable diagnostic information (e.g., "model not found", "budget exceeded mid-run"). The error detection matrix (Section 2.6) does not cover stderr-based diagnostics.
- Evidence: Section 2.2 line: `2>/dev/null)`. Section 2.6 has no stderr-specific detection.
- Recommendation: Capture stderr to a temporary file (`2>"$STDERR_FILE"`) and inspect it in step 3d-iii on failure. Add to the error detection matrix: "Stderr contains error patterns" with appropriate handling. Alternatively, document the rationale for discarding stderr if intentional.
- Impact: Debugging headless failures will be harder; operators lose diagnostic information that could distinguish between failure modes.

FINDING-W5: [MINOR] Cost estimate for T01.01 may be inaccurate
- Issue: Section 3.1 states "API cost: ~$4" for 4 test invocations, but the budget caps for tests 2 and 3 are $0.05 and $0.10 respectively. Test 4 budget is unspecified. Even if test 4 uses the deep budget ($5.00), the total would be $5.15, not ~$4. If test 4 uses standard ($2.00), total is $2.15.
- Evidence: Section 3.1: tests 2-3 budget caps ($0.05, $0.10), test 4 unspecified, total claimed ~$4.
- Recommendation: Specify test 4's `--max-budget-usd` value explicitly. Recompute the total cost estimate. If $4 is an upper bound including cost of the orchestrating session, state that.
- Impact: Sprint budget planning may be incorrect by 2-3x.

FINDING-W6: [SUGGESTION] Missing explicit requirement for idempotency of the viability probe
- Issue: If T01.01 is re-run (e.g., after environment change), there is no guidance on whether previous results should be overwritten or preserved. The probe writes to `/tmp/sc-probe-*` paths that may collide.
- Evidence: Section 3.1, test 2 and 3 write to fixed paths `/tmp/sc-probe-test.txt` and `/tmp/sc-probe-sections.txt`.
- Recommendation: Add a cleanup step at the beginning of T01.01 that removes `/tmp/sc-probe-*` files, or use unique paths with timestamps.
- Impact: Stale files from previous runs could cause false-positive results.

---

=== MARTIN FOWLER -- Software Architecture ===

FINDING-F1: [CRITICAL] The specification modifies the return contract schema but the sc:adversarial SKILL.md is explicitly out of scope
- Issue: Section 0 states "Changes to sc:adversarial SKILL.md itself (separate sprint)" is out of scope. Yet Section 3.7 defines a 10-field return contract schema that is incompatible with the 5-field schema in sc:adversarial SKILL.md FR-007. The specification expects the headless session (which loads sc:adversarial SKILL.md via `--append-system-prompt`) to produce 10 fields, but the SKILL.md it reads only defines 5 fields. The headless session will follow its SKILL.md instructions and produce a 5-field contract.
- Evidence: Section 0 "Out of scope": "Changes to sc:adversarial SKILL.md itself (separate sprint)". Section 3.7 defines `schema_version`, `base_variant`, `failure_stage`, `fallback_mode`, `invocation_method` -- none present in sc:adversarial SKILL.md FR-007. The prompt in Section 2.2 line 118-120 tries to override this with "MANDATORY REQUIREMENTS" instruction #4, but this creates a fragile coupling between the prompt text and the schema definition.
- Recommendation: Either (a) bring sc:adversarial SKILL.md return contract updates into scope for this sprint, or (b) accept that the headless session will produce the 5-field contract and handle the missing fields in the consumer (step 3e) by applying defaults. Option (b) is cleaner architecturally. If choosing (a), update the scope boundaries explicitly.
- Impact: The headless session will either produce a 5-field contract (SKILL.md wins over prompt) or a 10-field contract (prompt wins over SKILL.md), and the behavior is non-deterministic. This is the most architecturally risky aspect of the entire specification.

FINDING-F2: [MAJOR] Hidden coupling between prompt text and schema definition
- Issue: The command template (Section 2.2) embeds the 10-field schema directly in the prompt text ("write return-contract.yaml with ALL 10 required fields: schema_version (1.0), status, convergence_score..."). This creates a maintenance coupling where the schema is defined in three places: (1) the specification Section 3.7, (2) the prompt template in Section 2.2, (3) the headless-invocation.md reference file from Section 4.1. Any schema change requires synchronized updates across all three.
- Evidence: Section 2.2 lines 117-120 (prompt text), Section 3.7 (formal schema), Section 4.1 item 6 (reference file).
- Recommendation: Define the schema in exactly one place -- `refs/headless-invocation.md` -- and reference it from both the specification and the prompt template. The prompt should say "write return-contract.yaml per the schema defined in your system instructions" if sc:adversarial SKILL.md is updated, or provide the schema once in the prompt without duplicating it in the spec.
- Impact: Schema drift between prompt, specification, and reference file will cause subtle bugs where different invocations produce different field sets.

FINDING-F3: [MAJOR] Fallback path writes artifacts to different directory structure than headless path
- Issue: The current SKILL.md fallback (line 142-144) writes variants to `<output_dir>/variant-*.md` (flat). The specification's enhanced fallback F1 (Section 3.3) writes to `<output_dir>/adversarial/variant-*.md` (subdirectory). The headless session, following sc:adversarial SKILL.md artifact output structure (lines 291-304), writes to `<output-dir>/adversarial/`. The 3-state artifact scan (Section 3.3, 3d-iv) checks `<output-dir>/adversarial/` only. If partial headless artifacts land in the wrong location, the scan will report State A (empty) even when artifacts exist.
- Evidence: sc:adversarial SKILL.md line 293-304 shows `<output-dir>/adversarial/` structure. Current SKILL.md line 142 uses `<output_dir>/variant-*.md` (no subdirectory). Spec Section 3.3 F1 uses `<output_dir>/adversarial/variant-*.md`.
- Recommendation: Explicitly state that the enhanced fallback (F1-F5) writes ALL artifacts under `<output-dir>/adversarial/`, matching the sc:adversarial SKILL.md artifact structure. Add a note that the current SKILL.md's flat-directory fallback paths must be updated as part of this sprint.
- Impact: Mid-pipeline artifact recovery (the key value proposition of the 3-state model) will fail silently if directory structures are mismatched.

FINDING-F4: [MINOR] The `invocation_method` field creates a semantic coupling despite being declared informational
- Issue: Section 3.4 defines `invocation_method: "headless+task_agent"` for cases where "mid-pipeline artifacts were preserved from a partial headless run." This compound value implies the consumer needs logic to parse and interpret the `+` separator, contradicting the "informational only" designation. Section 3.7 also states "Consumers (step 3e) MUST NOT branch on this field" but the value structure invites branching.
- Evidence: Section 3.4: `"headless+task_agent"` as a compound value. Section 3.7: "informational only...MUST NOT branch on this field."
- Recommendation: Either keep the field truly informational with simple enum values (`"headless"`, `"task_agent"`, `"hybrid"`) or accept it as a routing field and define consumption rules. Don't define a compound value format while prohibiting consumption.
- Impact: Low immediate impact but creates technical debt -- future maintainers will branch on this field regardless of the prohibition.

---

=== MICHAEL NYGARD -- Production Systems & Reliability ===

FINDING-N1: [CRITICAL] No timeout for the `cat` of SKILL.md before invocation
- Issue: The command template (Section 2.2) reads the entire SKILL.md content into a variable: `ADVERSARIAL_SKILL_CONTENT="$(cat src/superclaude/skills/sc-adversarial/SKILL.md)"`. The sc:adversarial SKILL.md is 1747 lines (~75KB). This content is then passed as `--append-system-prompt "${ADVERSARIAL_SKILL_CONTENT}"`. There is no validation that the file was successfully read, no size check, and no consideration of shell argument length limits (`ARG_MAX`, typically 2MB on Linux but potentially lower in containerized environments).
- Evidence: Section 2.2 line 91: `ADVERSARIAL_SKILL_CONTENT="$(cat ...)"`. sc:adversarial SKILL.md is 1747 lines.
- Recommendation: Add a validation step after reading: check that `ADVERSARIAL_SKILL_CONTENT` is non-empty and its length is below `ARG_MAX`. If too large, either truncate non-essential sections or write to a temp file and use a file-reference mechanism if the CLI supports one. Add this check to the error detection matrix (Section 2.6).
- Impact: If the file read fails silently (empty variable), the headless session runs without behavioral instructions, producing garbage output. If `ARG_MAX` is exceeded, the command fails with an unhelpful "Argument list too long" error not covered by any detection path.

FINDING-N2: [MAJOR] The 3-state artifact scan model is incomplete -- missing State D
- Issue: The 3-state model (Section 3.3, 3d-iv) covers: A (no artifacts), B (variants exist, no diff-analysis), C (diff-analysis exists). But there are additional partial completion states not covered: (D) diff-analysis + debate-transcript exist but no base-selection, (E) base-selection exists but no merged-output, (F) merged-output exists but no return-contract. The specification jumps from "diff-analysis exists" (State C) to "start from F3" but F3 (debate) may have already completed.
- Evidence: Section 3.3, step 3d-iv defines only States A, B, C. The 5-step pipeline has 5 potential interruption points, not 3.
- Recommendation: Either expand to a 5-state model (one per step boundary) or explicitly justify why 3 states are sufficient. A pragmatic middle ground: add State D ("debate-transcript.md exists") which skips to F4 (scoring). Beyond that, the diminishing returns argument is valid, but it should be stated explicitly.
- Impact: If the headless session completes through debate but fails at scoring, the fallback will re-run the entire debate (potentially the most expensive step), wasting time and budget.

FINDING-N3: [MAJOR] No cascading failure protection between headless and fallback
- Issue: The specification assumes the fallback runs in the same parent session. If the headless session consumed significant time before failing (e.g., 280 seconds of a 300-second timeout on standard depth), the parent session has spent that time and budget. The fallback (F1-F5) then runs on top of that. There is no total budget or total time limit for the combined headless+fallback execution. The parent session could exhaust its own token budget during fallback.
- Evidence: Section 2.3 defines per-invocation budgets ($1-$5). Section 3.3 defines fallback steps F1-F5. No combined budget ceiling specified.
- Recommendation: Add a "total adversarial budget" parameter that caps the sum of headless cost + fallback cost. After headless failure, compute remaining budget before starting fallback. If insufficient, abort with a clear message rather than starting a fallback that will be truncated.
- Impact: In the worst case (headless times out at maximum budget, then full fallback runs), the adversarial step costs 2x the expected budget with no guardrail.

FINDING-N4: [MINOR] CLAUDECODE environment variable restore is not signal-safe
- Issue: If the parent process is interrupted (SIGINT, SIGTERM) between the `unset CLAUDECODE` and the restore block, the environment variable remains unset for the rest of the session. The `trap` mechanism is not used.
- Evidence: Section 2.2 lines 88-138. No `trap` command for signal handling.
- Recommendation: Use `trap 'export CLAUDECODE="$CLAUDECODE_BACKUP"' EXIT` before the unset. This ensures restoration even on abnormal termination.
- Impact: Low probability, but if triggered, subsequent `claude -p` calls in the same session would not detect the nesting issue, potentially causing unexpected behavior.

FINDING-N5: [SUGGESTION] Cost guard threshold should be configurable
- Issue: Section 3.3 step 3d-iii check 4 uses a hardcoded 1.5x multiplier for the cost guard warning. This is informational-only and non-blocking, but the threshold should be configurable for different deployment environments.
- Evidence: Section 3.3: "If `cost_usd` exceeds `BUDGET * 1.5`, emit warning"
- Recommendation: Make the multiplier configurable via a parameter (default 1.5) or at minimum document why 1.5x was chosen.
- Impact: Minimal -- this is informational only. But hardcoded constants are a maintenance smell.

---

=== GOJKO ADZIC -- Specification by Example ===

FINDING-A1: [CRITICAL] Section 5 heading-to-step mapping does not match actual sc:adversarial SKILL.md headings
- Issue: The specification's heading mapping table (Section 5) lists headings like "Step 1" or "Diff Analysis", "Step 2" or "Adversarial Debate", etc. The actual sc:adversarial SKILL.md headings are: "### Step 1: Diff Analysis" (line 70), "### Step 2: Adversarial Debate" (line 102), "### Step 3: Hybrid Scoring & Base Selection" (line 141), "### Step 4: Refactoring Plan" (line 201), "### Step 5: Merge Execution" (line 237). The mapping says F5 extracts from "Step 4" and "Step 5" or "Refactoring" and "Merge" -- but there is no heading containing just "Refactoring" or "Merge". The actual heading is "### Step 4: Refactoring Plan" and "### Step 5: Merge Execution".
- Evidence: Section 5 table, column "SKILL.md Section Heading": F4 maps to `"Step 3" or "Hybrid Scoring"`. Actual heading: `### Step 3: Hybrid Scoring & Base Selection`. The `or` alternatives are not substrings of the actual headings in all cases -- "Hybrid Scoring" would match a substring of "Hybrid Scoring & Base Selection" but "Diff Analysis" alone would NOT match "Step 1: Diff Analysis" if using exact heading match. The extraction method ("by heading match") is ambiguous about exact vs. substring matching.
- Recommendation: (1) Use the EXACT headings from sc:adversarial SKILL.md, not paraphrased alternatives. (2) Specify whether the extraction uses exact match, prefix match, or substring/fuzzy match. (3) The SKILL.md also has "## Implementation Details" sections (lines 411+) with much more detailed content than the summary "### Step N" headings. The mapping must clarify whether to extract the summary heading content (lines 70-250) or the implementation details (lines 411-1589). These contain vastly different levels of detail.
- Impact: If the extraction logic uses exact heading match, it will fail to find any of the mapped headings. If it uses substring match, "Step 1" will match both "### Step 1: Diff Analysis" (line 70) and "## Implementation Details -- Step 1: Diff Analysis Engine" (line 411), extracting potentially 340 lines of implementation detail when only the 30-line summary was intended.

FINDING-A2: [MAJOR] No concrete Given/When/Then examples for the 3-state artifact scan
- Issue: The 3-state artifact scan (Section 3.3, 3d-iv) is described abstractly but has no concrete examples. What exactly does "variant files (variant-*.md) exist" mean? Does a 0-byte variant file count? Does a single variant file constitute "variants exist" or must there be >=2? What if variant files exist but are from a previous run (stale)?
- Evidence: Section 3.3 State B: "Variant files (`variant-*.md`) exist but no `diff-analysis.md`."
- Recommendation: Add 3 concrete examples:
  - Given: `adversarial/` contains `variant-sonnet-architect.md` (500 bytes) and `variant-opus-security.md` (800 bytes), no `diff-analysis.md`. When: artifact scan runs. Then: State B detected, emit "Headless variants preserved. Resuming from diff analysis."
  - Given: `adversarial/` contains `variant-sonnet-architect.md` (0 bytes). When: artifact scan runs. Then: State A (0-byte files are treated as absent).
  - Given: `adversarial/` does not exist. When: artifact scan runs. Then: State A.
- Impact: Without examples, implementers must guess at edge case behavior, leading to inconsistent implementations.

FINDING-A3: [MAJOR] The behavioral adherence rubric (Section 7.3) is not executable as written
- Issue: The 20-point rubric defines scoring ranges (e.g., "4=all 4 sections + severity, 3=all sections, 2=2-3 sections") but does not define a concrete verification method. "All 4 sections" -- which 4 sections? The diff-analysis has 4 categories (structural_diff, content_diff, contradiction_detection, unique_contribution_extraction), but the rubric does not name them. A human reviewer could interpret this differently than an automated check.
- Evidence: Section 7.3 "Diff Analysis Structure" category: "4=all 4 sections + severity".
- Recommendation: Make each rubric criterion verifiable by grep. For example: "4 points if diff-analysis.md contains all 4 section headings: '## Structural Differences', '## Content Differences', '## Contradictions', '## Unique Contributions' AND at least one severity rating per section. 3 points if all 4 headings present without severity ratings."
- Impact: The rubric cannot be applied consistently across different reviewers or automated in CI.

FINDING-A4: [MINOR] The multi-round debate verification (Section 7.4) relies on fragile grep patterns
- Issue: The verification script greps for "round.1", "first.round", "round 1" etc. These patterns assume specific formatting in the debate transcript. The sc:adversarial SKILL.md (line 1012-1025) uses headings like "## Round 1: Advocate Statements" and "## Round 2: Rebuttals" which would match some but not all patterns.
- Evidence: Section 7.4 grep patterns: `"round.1\|first.round\|round 1"`. Actual SKILL.md heading: `## Round 1: Advocate Statements`.
- Recommendation: Align grep patterns with the actual headings defined in sc:adversarial SKILL.md. The primary pattern should be `## Round [0-9]` rather than the loose alternatives.
- Impact: False negatives possible if the headless session produces correctly structured output with slightly different formatting.

FINDING-A5: [SUGGESTION] The probe fixture specification (Section 4.2) lacks concrete content
- Issue: Section 4.2 mentions "Two minimal variant files (~100 words each) with deliberate structural and content differences" but does not define what the differences should be. For a viability probe, the fixture content directly affects whether the test is meaningful.
- Evidence: Section 4.2: "deliberate structural and content differences" with no specifics.
- Recommendation: Specify at least: (a) one variant uses a flat heading structure (H1, H2), the other uses nested (H1, H2, H3); (b) at least one contradiction between them (e.g., different technology choices); (c) both cover the same 3 topics but in different order. This ensures test 4 can actually exercise multi-step pipeline behavior.
- Impact: If fixtures are too similar, test 4 may pass trivially without exercising adversarial behavior.

---

=== LISA CRISPIN -- Testing Strategy ===

FINDING-C1: [CRITICAL] No test for the headless-to-fallback transition path
- Issue: The verification plan (Section 7) defines an end-to-end test (Section 7.5) and a separate fallback verification test. But there is no explicit test for the most critical path: headless starts, produces partial artifacts, fails, and fallback resumes from the correct state. This is the exact scenario the 3-state model is designed to handle, and it has zero test coverage.
- Evidence: Section 7.5 fallback verification: "Force headless failure. Verify: 1. Fallback activates with warning message. 2. F1-F5 all execute (5 steps, not 3)." This tests fallback from scratch (State A), not mid-pipeline recovery (States B or C).
- Recommendation: Add explicit test cases:
  - Test: "Headless produces variants but times out before diff-analysis." Verify: State B detected, fallback starts from F2, uses headless-generated variants.
  - Test: "Headless produces variants + diff-analysis but fails at debate." Verify: State C detected, fallback starts from F3, uses headless-generated diff-analysis.
  - These can be simulated by pre-populating the artifact directory with the expected partial artifacts and then triggering fallback.
- Impact: The 3-state artifact scan is the specification's key innovation, but it has no dedicated test. If it breaks, the fallback silently re-does all work.

FINDING-C2: [MAJOR] Fallback behavioral adherence threshold (10/20) is not justified
- Issue: Section 7.5 fallback verification states "Behavioral adherence rubric score >= 10/20 for fallback path." The primary path threshold is 14/20 (70%). The fallback threshold is 10/20 (50%). No rationale is given for accepting 50% adherence from the fallback. If the fallback is the enhanced 5-step pipeline, it should be held to a comparable standard.
- Evidence: Section 7.5: "Behavioral adherence rubric score >= 10/20 for fallback path" vs Section 7.3: ">= 14/20 (70%)" for headless.
- Recommendation: Either raise the fallback threshold to 12/20 (60%) with documented rationale for the delta, or explain why 50% is acceptable (e.g., "fallback operates with constrained context, so structural output quality is expectedly lower").
- Impact: A 50% threshold means the fallback can skip entire protocol steps (e.g., no scoring method at all: 0/4 points) and still pass verification, undermining quality guarantees.

FINDING-C3: [MAJOR] No regression test for the schema version field handling
- Issue: Section 3.7 makes a deliberate design decision that `schema_version` stays at "1.0" despite adding a field. The tasklist T06.01 tests schema consistency between producer and consumer. But there is no test that verifies step 3e correctly handles a return contract that has `schema_version: "1.0"` with 10 fields vs. one with no `schema_version` and 5 fields (the current state). Since sc:adversarial SKILL.md is out of scope for changes, the headless path may produce a 5-field contract while the fallback produces a 10-field contract.
- Evidence: Section 3.7 design decision on schema_version. No corresponding test in Section 7.
- Recommendation: Add a test that feeds step 3e both a 5-field contract (legacy) and a 10-field contract (new) and verifies correct routing for both. This is critical because during the transition period, both formats will be in the wild.
- Impact: If step 3e only handles 10-field contracts, the headless path (which may produce 5-field contracts from unmodified sc:adversarial SKILL.md) will be treated as malformed.

FINDING-C4: [MINOR] Verification plan has no test for the `invocation_method` logging behavior
- Issue: Section 3.8 specifies "If `invocation_method` is present, log it." No test verifies this conditional logging occurs. This is a minor feature but since it's specified, it should be tested.
- Evidence: Section 3.8. No corresponding test in Section 7.
- Recommendation: Add to the end-to-end test (Section 7.5): "Verify log output contains 'Adversarial pipeline invocation method: headless'" for the primary path.
- Impact: Low -- logging is informational. But untested specified behavior tends to rot.

FINDING-C5: [SUGGESTION] Missing negative test for the budget exceeded scenario
- Issue: The error detection matrix (Section 2.6) specifies that budget exceedance causes "CLI self-terminates; scan partial artifacts." No test scenario in Section 7 validates this path. Budget exceedance is the most likely failure mode for deep-depth invocations.
- Evidence: Section 2.6 "Budget exceeded" row. Section 7 verification plan contains no budget test.
- Recommendation: Add a low-budget test ($0.10) that intentionally triggers budget exceedance, then verify the artifact scan and fallback behavior.
- Impact: If the CLI's budget termination behavior doesn't produce the expected exit code or partial artifacts, the error handling logic is untested.

---

=== SAM NEWMAN -- Distributed Systems ===

FINDING-S1: [CRITICAL] Return contract is defined in the specification but not in the service boundary it claims to abstract
- Issue: The specification's philosophy (Section 1) states: "The return contract (return-contract.yaml) is the abstraction boundary. Step 3e reads and routes on status and convergence_score. It does not know or care whether the contract was produced by headless or fallback." This is the right principle, but the implementation violates it. The specification defines the 10-field contract in Section 3.7, but the "service" (sc:adversarial, loaded via SKILL.md) only defines a 5-field contract (FR-007). The abstraction boundary is being defined by the consumer, not the producer. This inverts the dependency.
- Evidence: Section 1 philosophy vs. Section 3.7 schema vs. sc:adversarial SKILL.md FR-007 (5 fields). The consumer (specification/sc:roadmap) is adding `schema_version`, `base_variant`, `failure_stage`, `fallback_mode`, `invocation_method` that the producer (sc:adversarial) doesn't know about.
- Recommendation: The return contract schema must be owned by the producer (sc:adversarial). If the producer needs to emit new fields, update the producer. If the consumer needs additional fields, they should be added to a consumer-side wrapper or envelope, not to the producer's contract. Alternatively, explicitly acknowledge that the fallback (F-contract step) writes a superset contract that the headless path may not match, and handle the difference in step 3e.
- Impact: This creates a distributed system anti-pattern where the consumer dictates the producer's contract. When sc:adversarial SKILL.md is eventually updated (separate sprint), there may be version conflicts.

FINDING-S2: [MAJOR] Schema evolution strategy is absent
- Issue: Section 3.7 states `schema_version: "1.0"` and argues that adding one field doesn't warrant a version bump. But there's no defined process for what WOULD warrant a version bump. When does "1.0" become "1.1" or "2.0"? What happens when a consumer receives a contract with an unexpected `schema_version`?
- Evidence: Section 3.7: "The addition of one optional informational field does not warrant a version bump."
- Recommendation: Define a versioning policy: (1) Minor version bump (1.0 -> 1.1) for additive, non-breaking changes. (2) Major version bump (1.0 -> 2.0) for breaking changes (field removal, type changes). (3) Consumer behavior for unknown versions: "If schema_version > expected, log warning and process known fields only."
- Impact: Without a versioning policy, future schema changes will either never bump the version (making it meaningless) or bump it without defined consumer behavior (breaking the abstraction).

FINDING-S3: [MAJOR] The `headless+task_agent` value in `invocation_method` leaks implementation details across the boundary
- Issue: The compound value `"headless+task_agent"` (Section 3.4) encodes the execution history into the contract. This violates the abstraction principle stated in Section 1. A consumer processing the return contract now needs to understand that a `+` separator means "two methods were used sequentially" and might reason about the implications (e.g., "artifacts from different sessions might have different quality characteristics").
- Evidence: Section 3.4: `invocation_method: "headless+task_agent"` when mid-pipeline artifacts preserved. Section 1: "It does not know or care whether the contract was produced by headless or fallback."
- Recommendation: Remove the compound value. Use `"task_agent"` when fallback completed the pipeline, regardless of whether headless produced partial artifacts. The mid-pipeline recovery is an implementation detail of the fallback, not a contract-level concern. If traceability is needed, add it to `merge-log.md`, not the contract.
- Impact: This value creates implicit coupling between the consumer's routing logic and the producer's internal execution strategy.

FINDING-S4: [MINOR] No backward compatibility guarantee for consumers of the 5-field contract
- Issue: Existing consumers of the return contract (e.g., the current sc:roadmap SKILL.md step 3e, line 145-153) expect exactly 7 fields (status, merged_output_path, convergence_score, fallback_mode, artifacts_dir, unresolved_conflicts, base_variant -- as shown in the canonical schema comment on line 153). The specification adds 3 more fields (`schema_version`, `failure_stage`, `invocation_method`). There is no guarantee that existing consumers handle unknown fields gracefully (YAML parsers typically do, but the consumer logic might assert on field count).
- Evidence: sc:roadmap SKILL.md line 153: canonical schema comment lists 7 fields. Specification Section 3.7 defines 10 fields.
- Recommendation: Document the backward compatibility guarantee: "Consumers MUST ignore unknown fields in the return contract. The schema is additive-only; fields are never removed or renamed." This should be a stated invariant, not just implied by YAML's flexibility.
- Impact: If a consumer validates "exactly N fields," the addition of new fields will cause validation failures.

FINDING-S5: [SUGGESTION] Consider a contract validation step in the consumer
- Issue: Step 3e (return contract consumption) checks for file existence and YAML parse errors, but does not validate the contract's field types or value ranges. A contract with `convergence_score: "high"` (string instead of float) or `status: "done"` (invalid enum value) would pass the current checks.
- Recommendation: Add a lightweight schema validation step in 3e that checks: (1) `status` is one of `success|partial|failed`, (2) `convergence_score` is a number in [0.0, 1.0] or null, (3) `merged_output_path` is a string or null. Define handling for invalid values (treat as `status: failed` with diagnostic).
- Impact: Without validation, malformed contracts could cause downstream routing errors with misleading symptoms.

---

=== PANEL CONSENSUS ===

CRITICAL findings (must fix before implementation):

1. **[W1/F1/S1] Return contract field count and ownership mismatch**: The specification claims "9 original + 1 new = 10 fields" but the sc:adversarial SKILL.md defines only 5 fields. The sc:roadmap SKILL.md canonical comment lists 7 fields. The specification is out of scope for changing sc:adversarial SKILL.md but defines a schema that requires changes to it. This is an architectural contradiction that must be resolved: either bring sc:adversarial SKILL.md updates into scope, or design step 3e to handle both 5-field and 10-field contracts gracefully.

2. **[A1] Section 5 heading mapping does not match actual SKILL.md headings**: The instruction delivery protocol references headings that are paraphrased, not exact. The extraction method (exact vs. substring vs. fuzzy) is unspecified. Implementation will fail or extract wrong content without a precise mapping to the actual heading text in sc:adversarial SKILL.md.

3. **[N1] No validation of SKILL.md content after cat, no ARG_MAX protection**: The 75KB SKILL.md is read into a shell variable and passed as a command-line argument with no validation. Failure modes include empty variable (silent failure) and argument length limit exceeded (unhelpful error).

4. **[C1] No test for mid-pipeline recovery (States B/C)**: The 3-state artifact scan is the specification's key innovation but has zero test coverage. Only State A (full fallback) is tested.

MAJOR findings (should fix, risk if not):

5. **[W2] `unresolved_conflicts` type inconsistency (integer vs. list[string])** -- will cause runtime type errors
6. **[F2] Schema defined in 3 places (prompt, spec, ref file)** -- maintenance coupling
7. **[F3] Fallback writes to different directory than headless** -- breaks mid-pipeline recovery
8. **[N2] 3-state model incomplete -- missing state for debate completion** -- wastes budget on re-run
9. **[N3] No combined budget ceiling for headless+fallback** -- potential 2x cost overrun
10. **[A2] No concrete examples for 3-state artifact scan** -- ambiguous implementation
11. **[A3] Behavioral adherence rubric not executable** -- subjective evaluation
12. **[C2] Fallback threshold (50%) unjustified** -- quality regression risk
13. **[C3] No test for 5-field vs 10-field contract handling** -- transition period brittleness
14. **[S2] No schema evolution strategy** -- future maintenance debt
15. **[S3] `headless+task_agent` leaks execution history into contract** -- violates abstraction principle

MINOR findings (improve when practical):

16. **[W4]** Stderr discarded with no diagnostic capture
17. **[W5]** Cost estimate arithmetic doesn't add up
18. **[F4]** `invocation_method` compound value invites prohibited branching
19. **[N4]** CLAUDECODE restore not signal-safe (missing trap)
20. **[A4]** Multi-round debate grep patterns misaligned with actual headings
21. **[C4]** No test for `invocation_method` logging
22. **[S4]** No explicit backward compatibility guarantee for contract consumers

SUGGESTIONS:

23. **[W6]** Viability probe idempotency (stale /tmp files)
24. **[N5]** Cost guard multiplier should be configurable
25. **[A5]** Probe fixtures need specified content differences
26. **[C5]** Missing negative test for budget exceeded scenario
27. **[S5]** Add lightweight contract schema validation in consumer

---

Quality Scores:

- **Clarity**: 7/10 -- The specification is well-structured and reads clearly. However, the return contract field count claims are confusing (claims 9 original but actual sources show 5 or 7), and the heading mapping in Section 5 uses paraphrased rather than exact headings.

- **Completeness**: 6/10 -- Major gap: the specification modifies a contract schema that belongs to an out-of-scope service. The scope boundary is self-contradictory. Missing: combined budget ceiling, schema evolution policy, concrete examples for the 3-state model, and tests for the most novel feature (mid-pipeline recovery).

- **Testability**: 5/10 -- The verification plan covers happy paths but lacks coverage for the most critical scenarios: mid-pipeline recovery, schema version mismatch, budget exceeded, and the transition period where headless and fallback produce different contract formats. The behavioral adherence rubric is not automatable.

- **Consistency**: 4/10 -- Multiple inconsistencies found: field count arithmetic (5 vs 7 vs 9 vs 10), `unresolved_conflicts` type (integer vs list), directory paths (flat vs subdirectory), heading names (paraphrased vs actual), and the philosophical claim of producer-owned contracts vs the consumer-defined schema in practice.

- **Overall**: 5.5/10 -- The specification demonstrates strong architectural thinking (process isolation, return contract abstraction, mid-pipeline recovery) but has significant implementation-level inconsistencies that would cause real failures during implementation. The core issue is that the specification tries to extend a contract defined by an out-of-scope service without updating that service, creating an inherent tension that surfaces in multiple findings across all reviewers.

---

*Panel review completed 2026-02-23.*
*6 experts, 27 findings: 4 CRITICAL, 11 MAJOR, 6 MINOR, 6 SUGGESTION.*
