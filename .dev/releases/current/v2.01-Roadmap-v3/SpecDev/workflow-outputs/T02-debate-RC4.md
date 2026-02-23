# Adversarial Debate: RC4 Return Contract Data Flow

**Debate Question**: Does the sprint specification effectively mitigate RC4 (Return Contract Data Flow)?

**RC4 Summary**: The return contract specifies 6 structured fields but defines no transport mechanism. The only inter-agent data flow precedent (sc:cleanup-audit) uses explicit file-based fan-out/fan-in, which the adversarial return contract does not adopt. Task agents return unstructured text, not typed structs. Likelihood: 0.75, Impact: 0.75, Combined Score: 0.750.

**Sprint Spec Coverage**: Epic 3 (Tasks 3.1-3.4), Risks R3 and R4, plus supporting elements in Epic 1 Task 1.4 (fallback contract writes) and Epic 2 Task 2.2 step 3e (consumer routing logic).

---

## Round 1: Opening Statements

### FOR Position (Advocate)

The sprint specification delivers a comprehensive, layered mitigation for RC4. The root cause diagnosis is precise: RC4 is a transport mechanism gap -- structured fields exist in the spec but have no defined delivery channel. The sprint's Epic 3 directly addresses this with a file-based YAML convention that mirrors the only known working inter-agent data flow pattern in the codebase (sc:cleanup-audit's fan-out/fan-in). Here is why the mitigation is sufficient:

**1. Transport mechanism is now explicit.** Task 3.1 adds a "Return Contract (MANDATORY)" section as the final pipeline step in sc:adversarial's SKILL.md. This is not a suggestion or a convention buried in documentation -- it is a mandatory instruction positioned as the absolute last action before the skill exits. The transport medium (file-based YAML at `<output-dir>/adversarial/return-contract.yaml`) is concrete and deterministic. No ambiguity remains about HOW the data gets from producer to consumer.

**2. Schema is expanded and tightened.** The original contract had 6 fields. The sprint expands this to 9 fields, adding `schema_version`, `failure_stage`, and `fallback_mode`. Each addition addresses a specific gap:
- `schema_version: "1.0"` enables forward-compatible evolution without breaking consumers.
- `failure_stage` provides diagnostic granularity -- the consumer knows not just that something failed but WHERE in the pipeline it failed.
- `fallback_mode` distinguishes between "full pipeline ran but didn't converge" (partial) and "degraded single-round fallback ran" (partial + fallback_mode: true). This is a qualitatively important distinction for downstream quality decisions.

**3. Null convention eliminates sentinel ambiguity.** Task 3.1 specifies "Use YAML null (`~`) instead of sentinel values (-1, '') for fields not reached during failed runs." This directly addresses a common data contract failure mode: consumers cannot reliably distinguish "field was set to zero" from "field was never computed" when sentinel values like -1 or empty strings are used. YAML null is semantically unambiguous.

**4. Write-on-failure is explicitly mandated.** Risk R4 identifies "Claude does not write return-contract.yaml on failure paths" as a medium-probability threat. The sprint addresses this with explicit "write even on failure with `status: failed`" language in Task 3.1. This means the consumer can always distinguish "pipeline failed gracefully" (file exists with status: failed) from "pipeline crashed" (file does not exist).

**5. Consumer-side routing is fully specified.** Task 3.2 defines a three-branch status routing (success/partial/failed) with a convergence threshold (0.6) for partial results and a missing-file guard ("If return-contract.yaml does not exist, treat as status: failed with failure_stage: 'transport'"). This closes the loop -- the consumer knows exactly what to do with every possible state of the return contract, including its absence.

**6. Producer-consumer alignment is enforced.** Tasks 3.3 and 3.4 add cross-reference comments in both directions: the producer schema references the consumer, and the consumer references the canonical schema definition. This creates a human-discoverable link that reduces future drift.

**7. Fallback protocol also writes contracts.** Epic 1 Task 1.4 specifies that each of the 5 fallback steps (F1-F5) writes return-contract.yaml on failure with an appropriate `failure_stage`. On successful fallback completion, it writes `status: partial, fallback_mode: true`. This means the return contract transport mechanism works regardless of whether the full sc:adversarial pipeline ran or the degraded fallback executed.

**8. Type inconsistency is resolved.** Task 3.1 notes that `unresolved_conflicts` was typed as `list[string]` at line 349 of the existing SKILL.md but resolves it to `integer` for simplicity. The Definition of Done explicitly checks that this type is consistent in both producer and consumer. This prevents a class of deserialization/interpretation errors.

The sprint does not just define a schema -- it establishes a complete data flow protocol with transport mechanism, schema versioning, null conventions, failure handling, consumer routing logic, cross-references, and type consistency. This is a thorough mitigation.

### AGAINST Position (Challenger)

The sprint specification addresses the surface of RC4 but leaves several structural and operational gaps that undermine confidence in the mitigation's real-world effectiveness. The core concern is not whether the schema is well-designed on paper but whether Claude agents can reliably produce valid YAML conforming to this schema in practice. Here are the gaps:

**1. No validation of YAML correctness.** The entire return contract mechanism depends on Task agents writing syntactically valid, schema-compliant YAML. But Task agents return unstructured text -- this is literally stated in RC4's diagnosis. The sprint adds an instruction to "write return-contract.yaml with the following fields" but provides no mechanism to validate that the written file is (a) parseable YAML, (b) contains all 9 required fields, (c) has correct types for each field, or (d) uses null instead of empty strings or -1. If a Task agent writes `convergence_score: "high"` instead of `convergence_score: 0.85`, the consumer's numeric comparison (`>= 0.6`) will fail silently or throw an error. The sprint specification contains no YAML validation step, no schema enforcement, and no error handling for malformed contract files.

**2. The convergence threshold of 0.6 is arbitrary.** Task 3.2 specifies that partial results are usable "if convergence_score >= 0.6." This threshold is not justified by any empirical data, simulation, or even a heuristic argument. Why 0.6 and not 0.5 or 0.7? A threshold too low admits poor-quality merges as "good enough." A threshold too high rejects usable results unnecessarily. The sprint provides no guidance on how this threshold was determined or how to calibrate it. Furthermore, the convergence_score itself is produced by the adversarial pipeline's scoring mechanism -- if the pipeline only ran partially (status: partial), the convergence_score may be unreliable. Routing on an unreliable score compounds the error.

**3. Schema versioning is declared but not operationalized.** Task 3.1 includes `schema_version: "1.0"` and Task 3.2 says "check schema_version, warn on unknown version." But there is no migration path, no backward compatibility guarantee, and no specification of what "warn" means operationally. Does the consumer proceed with a best-effort parse? Does it abort? Does it attempt to map unknown fields? When schema 1.1 ships, what happens to consumers still expecting 1.0? The versioning is ceremonial rather than functional.

**4. The 9-field schema may be too complex for reliable agent production.** The original contract had 6 fields. The sprint adds 3 more. Each field has specific type constraints (integer, boolean, path-or-null, enum). Task agents generating this YAML must remember all 9 fields, their types, their null conventions, and the conditional logic (e.g., `failure_stage` is null on success but a pipeline step name on failure; `fallback_mode` is false normally but true in fallback context). This is a significant cognitive load for an LLM generating a YAML block at the end of a long pipeline execution. The more complex the schema, the higher the probability of omission or type errors.

**5. Cross-reference comments are fragile.** Tasks 3.3 and 3.4 add comments like `# Canonical schema definition: src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section`. These are plain-text comments with hardcoded file paths. They have no enforcement mechanism. When files are moved, renamed, or restructured, these comments become misleading. They are better than nothing but should not be counted as a robust alignment mechanism.

**6. The missing-file guard conflates two failure modes.** Epic 2 Task 2.2 step 3e specifies: "If return-contract.yaml not found, treat as status: partial with convergence_score: 0.0." But a missing file could mean (a) the pipeline crashed before reaching the write step, (b) the file was written to a wrong path, or (c) a filesystem error occurred. Treating all of these as "partial with convergence 0.0" is arguably wrong -- case (a) should be treated as "failed," not "partial." The sprint spec itself is inconsistent here: Task 3.2 says treat missing file as "status: failed with failure_stage: 'transport'" while Task 2.2 step 3e says treat it as "status: partial with convergence_score: 0.0." This is a direct contradiction between two tasks in the same sprint.

**7. No negative testing or acceptance test for malformed input.** Risk R4 mentions "Add negative test: invoke with malformed input and verify file is written with status: failed." This is mentioned as a risk mitigation strategy but is NOT included in the Definition of Done or the Verification Plan. The verification plan has Test 3 (schema consistency between producer and consumer) but no test for malformed YAML, missing fields, or type violations. The sprint acknowledges the risk but does not commit to verifying the mitigation works.

**8. The `unresolved_conflicts` type change is a breaking change with no migration.** Task 3.1 changes `unresolved_conflicts` from `list[string]` (existing SKILL.md line 349) to `integer`. This is presented as a simplification, but if any existing code or documentation references the list format, this is a breaking change. The sprint does not audit for consumers of the list format.

---

## Round 2: Cross-Examination

### Advocate Cross-Examines Challenger

**Q1**: You argue YAML validation is missing, but consider: the return contract is written by an LLM following explicit instructions within a SKILL.md file. The entire SuperClaude framework operates on the premise that LLMs can follow structured instructions to produce formatted outputs. Every artifact in the adversarial pipeline (diff-analysis.md, debate-transcript.md, scoring matrices) is produced the same way -- LLM writes structured content based on instructions. If YAML validation is required for the return contract, then by your logic, every artifact in the system needs validation, and the entire framework's operating model is flawed. Is your objection specific to RC4 or a general complaint about the framework?

**A1 (Challenger)**: This is a fair challenge, but the return contract is qualitatively different from other artifacts. A debate transcript or diff analysis is consumed by humans or by LLMs that can tolerate formatting variation. The return contract is consumed by branching logic (`if status == "success"`, `if convergence_score >= 0.6`) that requires exact field names, correct types, and valid YAML syntax. A human reading a debate transcript can handle a missing heading. A routing algorithm comparing a string to 0.6 cannot handle `convergence_score: "high"`. The return contract is the one artifact where structural correctness is load-bearing. My objection is specific to programmatic consumption of agent output, which is exactly what RC4 identified as the core problem.

**Q2**: You call the 0.6 threshold "arbitrary." But every threshold in engineering is chosen by judgment until empirical data refines it. The sprint explicitly defines the threshold so it can be adjusted later. Would you prefer no threshold (accept any partial result) or no partial-result path at all (binary success/fail)?

**A2 (Challenger)**: I would prefer the threshold to be documented with its rationale, even if the rationale is "initial engineering judgment, to be calibrated based on operational data." The sprint states 0.6 as if it were derived from analysis. Transparency about the basis helps future maintainers understand whether to raise or lower it. The existence of a threshold is good; its unjustified precision creates false confidence.

**Q3**: You identified a contradiction between Task 3.2 (missing file = failed) and Task 2.2 step 3e (missing file = partial with convergence 0.0). Is this a fundamental design flaw or an editorial error that would be caught during implementation?

**A3 (Challenger)**: It is almost certainly an editorial error, but that is precisely the point -- the sprint spec contains an internal contradiction in a critical failure-handling path. If the implementer follows Task 2.2 literally, the behavior differs from Task 3.2. The sprint's Critical Coordination section warns about Wave 2 step 3 rewrite conflicts but does not catch this semantic conflict in the missing-file guard. This suggests the spec was not reviewed for cross-task consistency in failure handling.

### Challenger Cross-Examines Advocate

**Q1**: You emphasize that "MANDATORY" language and "write-even-on-failure" instructions address R4. But how does an instruction prevent a crash? If the adversarial pipeline hits an unhandled exception or the agent context is truncated before reaching the final step, no amount of "MANDATORY" language will produce a file. What is the actual mechanism that ensures the contract file exists after pipeline failure?

**A1 (Advocate)**: You are correct that MANDATORY language cannot prevent hard crashes. However, the sprint addresses this at two levels. First, the missing-file guard in the consumer (Task 3.2 / Task 2.2 step 3e) handles the case where the file simply does not exist -- the consumer does not hang waiting for it. Second, the fallback protocol in Epic 1 Task 1.4 provides a parallel path: each fallback step (F1-F5) independently writes return-contract.yaml on failure. Even if the primary pipeline crashes, the fallback path produces a contract. The combination of "write on failure" (handles graceful failures) and "missing file guard" (handles hard crashes) covers both failure modes. No single mechanism prevents all crashes, but the layered approach is resilient.

**Q2**: You claim the schema is "tightened" by expanding from 6 to 9 fields. But more fields means more surface area for errors. The Challenger's point about cognitive load is concrete: an LLM finishing a multi-thousand-token pipeline execution must remember 9 fields with specific types and conditional logic. Have you seen evidence that LLMs reliably produce 9-field YAML blocks after long context windows?

**A2 (Advocate)**: The cognitive load concern is legitimate but mitigated by the sprint's approach. The return contract is specified as an example YAML block in the SKILL.md (Task 3.1 acceptance criteria: "example YAML block is provided"). The agent does not need to remember 9 fields from scratch -- it follows a template. LLMs are demonstrably better at filling in templates than generating structured output from memory. The example block serves as both documentation and a copy-paste scaffold. Additionally, 9 fields is not unusually large for YAML output -- it is smaller than many configuration files LLMs routinely generate.

**Q3**: The sprint's verification plan (Test 3) checks schema consistency between producer and consumer by extracting field names and diffing them. But this is a static analysis of the specification files, not a runtime test of actual pipeline output. How do you verify that the pipeline actually writes the correct YAML at runtime?

**A3 (Advocate)**: Test 5 (End-to-End Invocation) is the runtime verification. It specifies: "return-contract.yaml exists in the output directory with valid schema" and "sc:roadmap reads the return contract and routes on status field." This is a manual post-sprint test that validates the complete data flow. I concede that there is no automated runtime schema validation within the pipeline itself, and this is a legitimate gap. However, the sprint explicitly scopes Test 5 as post-sprint manual verification, and the DVL (Deterministic Verification Layer) brainstorm proposes `validate_return_contract.py` as a follow-up script. The sprint acknowledges this gap and provides a path to close it.

---

## Round 3: Rebuttals

### Advocate Rebuttal

The Challenger raises valid points but overstates their severity. Let me address the three strongest objections:

**On YAML validation**: The Challenger is right that the return contract is programmatically consumed and therefore more sensitive to formatting errors than human-read artifacts. However, the sprint mitigates this through (a) an example YAML block that serves as a template, (b) the missing-file guard that handles total failure, and (c) the consumer's status routing which degrades gracefully on unexpected values. The Challenger demands a YAML schema validator -- a reasonable enhancement but not a requirement for RC4 mitigation. RC4's diagnosis was "no transport mechanism." The sprint provides a transport mechanism. Validation of transport payload correctness is a second-order concern.

**On the missing-file guard contradiction**: This is a genuine editorial error in the spec. Task 3.2's treatment (status: failed, failure_stage: 'transport') is the correct behavior and should take precedence. Task 2.2 step 3e's treatment (status: partial, convergence_score: 0.0) is inconsistent and should be aligned during implementation. This is a spec-quality issue, not a design-quality issue. The intent is clear; the wording needs reconciliation.

**On the 0.6 threshold**: The Challenger's objection is well-taken but is a calibration concern, not a mitigation gap. The sprint establishes the mechanism (threshold-based routing) and sets an initial value. If the threshold is wrong, it can be adjusted without architectural changes. The sprint should document the rationale, but the absence of rationale does not invalidate the mitigation.

### Challenger Rebuttal

The Advocate's responses are reasonable but rely heavily on "good enough for now" reasoning. Let me sharpen my three remaining concerns:

**On layered failure handling**: The Advocate claims the combination of "write on failure" + "missing file guard" + "fallback path" covers all failure modes. This is true in theory but creates a complex matrix of possible states. The consumer must handle: (1) file exists with status success, (2) file exists with status partial + fallback_mode false, (3) file exists with status partial + fallback_mode true, (4) file exists with status failed, (5) file does not exist. That is 5 distinct states, each with different routing behavior. The spec defines all 5 but the cognitive load on both the implementing agent (writing consumer routing) and the executing agent (following it at runtime) is substantial. Complexity is the enemy of reliability.

**On the `unresolved_conflicts` type change**: The Advocate did not address this. Changing from `list[string]` to `integer` without auditing consumers is a risk. The existing SKILL.md at line 349 uses `list[string]`. The sprint's Definition of Done says "unresolved_conflicts type resolved to integer in both producer and consumer" -- but does not verify that no OTHER consumers exist. If any agent prompts, documentation, or downstream skills reference the list format, this is a silent breaking change.

**On Test 5 as the runtime verification**: Test 5 is a post-sprint manual test that "can only be run in a Claude Code session." It is not automated, not repeatable, and not included in CI. The sprint's primary verification (Tests 1-4) is entirely static. The gap between "the spec says the right things" and "the pipeline does the right things" is exactly the gap RC4 identified. The sprint addresses the spec gap but does not close the runtime gap.

---

## Scoring

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| **1. Root Cause Coverage** | 0.85 | The sprint directly addresses RC4's core diagnosis: "no transport mechanism." A file-based YAML convention is established with explicit write instructions, consumer routing, and failure handling. The transport gap is closed. Minor gap: the sprint does not address the deeper concern that "Task agents return unstructured text, not typed structs" -- it instructs agents to write typed YAML but provides no enforcement mechanism. |
| **2. Completeness** | 0.72 | The 9-field schema, null convention, status routing, missing-file guard, write-on-failure, cross-references, and type resolution are all present. However: (a) the missing-file guard has a cross-task contradiction, (b) the 0.6 threshold lacks documented rationale, (c) no YAML validation mechanism exists, (d) the `unresolved_conflicts` type change is not audited for other consumers. These are real gaps in an otherwise thorough specification. |
| **3. Feasibility** | 0.80 | The changes are implementable: add a YAML template section to SKILL.md, add routing logic to adversarial-integration.md, add cross-reference comments. The file-based transport mechanism is proven by sc:cleanup-audit precedent. Feasibility risk comes from agent reliability in producing 9-field schema-compliant YAML, which is plausible but not guaranteed. The example YAML block mitigates but does not eliminate this risk. |
| **4. Blast Radius** | 0.88 | Changes are confined to 2 files (sc-adversarial SKILL.md, adversarial-integration.md) with no structural changes to the framework. The `unresolved_conflicts` type change from list to integer is the only potentially breaking change, and it is acknowledged in the spec. Cross-reference comments are additive. The risk of unintended side effects is low. |
| **5. Confidence** | 0.75 | The sprint will likely succeed in establishing the transport mechanism and making the return contract functional in the happy path. Confidence is reduced by: (a) the editorial contradiction in missing-file handling, (b) no runtime validation of YAML correctness, (c) reliance on post-sprint manual testing (Test 5) as the only end-to-end verification, and (d) the 5-state consumer routing complexity. The mitigation is directionally correct and largely complete but has exploitable edge cases. |

**Weighted Average**: (0.85 + 0.72 + 0.80 + 0.88 + 0.75) / 5 = **0.800**

---

## Verdict: NEEDS AMENDMENTS

The sprint specification provides a strong mitigation for RC4 that addresses the root cause (no transport mechanism) with a well-designed file-based YAML convention. The 9-field schema, status routing, failure handling, and cross-references demonstrate thorough engineering. However, three specific amendments are needed before the mitigation can be considered fully sufficient:

### Required Amendments

**Amendment 1 (Critical): Resolve the missing-file guard contradiction.**
Task 3.2 says: treat missing file as `status: failed, failure_stage: 'transport'`.
Task 2.2 step 3e says: treat missing file as `status: partial, convergence_score: 0.0`.
These are mutually exclusive. Recommended resolution: adopt Task 3.2's treatment (`status: failed`) as the canonical behavior, and update Task 2.2 step 3e to match. A missing file is a transport failure, not a partial result.

**Amendment 2 (Important): Add convergence threshold rationale.**
Document that 0.6 is an initial engineering judgment, expected to be calibrated through operational experience. Include guidance: "If >50% of partial results are rejected, consider lowering. If merged outputs from partial results show quality defects, consider raising." This takes 2 sentences and prevents future threshold debates.

**Amendment 3 (Important): Add YAML example block to consumer specification.**
Task 3.1 requires an example YAML block in the producer (sc:adversarial SKILL.md). Task 3.2 should also include a matching example in the consumer (adversarial-integration.md) showing the expected format for all 3 status states (success, partial, failed). This provides the consumer-side implementer with the same template scaffolding that the producer-side implementer receives.

### Acknowledged but Not Blocking

- YAML schema validation is a legitimate follow-up concern but is consistent with the framework's general operating model (LLMs produce structured output from instructions). The DVL brainstorm already proposes `validate_return_contract.py` as a follow-up.
- The `unresolved_conflicts` type change should be noted as potentially breaking but is unlikely to affect any existing consumers given the pipeline has never successfully run.
- The 5-state consumer routing complexity is inherent to the problem domain and cannot be reduced without losing diagnostic granularity.

---

*Debate conducted 2026-02-23. Analyst: claude-opus-4-6 (debate-orchestrator mode).*
*Inputs: sprint-spec.md, ranked-root-causes.md, sc-adversarial/SKILL.md (lines 339-358, 1525-1587), adversarial-integration.md (lines 1-100).*
*Methodology: Structured adversarial debate with cross-examination, 5-criterion scoring (0.0-1.0), verdict with required amendments.*
