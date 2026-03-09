Briefing: Spec-Conformance Drift in Roadmap → Tasklist → Execution Workflows
 
  This issue is about upstream semantic drift, not runner misbehavior. The roadmap
   generated for v2.19-roadmap-validate contains several substantive deviations
  from the source spec, and the Phase 2/3 tasklists contain additional scope,
  sequencing, and validation narrowing relative to the roadmap. The repo already
  has structural gate infrastructure, reflection capabilities, and
  sc-roadmap-protocol docs that explicitly describe a spec-faithfulness validation
   wave (src/superclaude/skills/sc-roadmap-protocol/refs/validation.md), but
  semantic conformance is not being enforced as a blocking gate consistently
  enough across artifact boundaries. The most promising solution is to
  operationalize a harnessed semantic conformance gate at each handoff: roadmap
  against spec, tasklist against roadmap, and then execution against tasklist.

  Objective

  This briefing captures the problem, findings, architectural implications, and
  solution directions discussed in this conversation, with direct links to the
  most relevant files so a future agent can begin ideation immediately without
  repo-wide searching.

  ---
  Core problem statement

  The workflow currently allows semantic drift to enter the artifact chain:

  1. Spec is used to generate a roadmap
  2. Roadmap is used to generate tasklists
  3. Task runner / sprint runner executes against the tasklist

  If the roadmap already deviates from the spec, then the tasklist can faithfully
  encode that deviation, and the runner can still behave correctly relative to the
   tasklist while producing output that is wrong relative to the original spec.

  Correct validation layering

  The intended validation model should be:

  - roadmap validated against spec
  - tasklist validated against roadmap
  - execution validated against tasklist

  Not:
  - tasklist validated against original spec
  - execution validated against original spec

  That distinction is central.

  ---
  Key insight from this conversation

  A simple reflective semantic review was enough to catch major deviations
  quickly.

  You observed that this was easy to detect by asking an agent to look for
  deviations:
  - roadmap vs spec
  - tasklist vs roadmap

  That suggests the repo's main weakness is not lack of detection capability, but
  lack of consistent blocking enforcement at artifact handoff boundaries.

  ---
  Confirmed findings

  1) Roadmap deviated materially from the spec

  We identified several important roadmap ↔ spec mismatches.

  High-signal deviations

  A. Resume / validation-state behavior drift

  The spec says validation state is separate and successful resumed runs still
  validate final artifacts.

  The roadmap instead introduced:
  - persistence under .roadmap-state.json
  - skip re-validation semantics on resume

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - spec-roadmap-validate.md:103
  - spec-roadmap-validate.md:515-516
  - roadmap.md:95-96
  - roadmap.md:244-245

  ---
  B. Degraded report schema drift

  The roadmap introduced degraded partial-success reporting with
  validation_complete: false, which is not in the spec’s defined report schema.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - spec-roadmap-validate.md:123-131
  - spec-roadmap-validate.md:461-468
  - roadmap.md:19
  - roadmap.md:74-75
  - roadmap.md:236-239

  ---
  C. ValidateConfig contract drift

  The roadmap-described ValidateConfig diverged from the spec’s model.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - spec-roadmap-validate.md:212-221
  - roadmap.md:29-30

  ---
  D. Prompt-builder API drift

  The roadmap changed prompt-builder naming/signatures relative to the spec.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - spec-roadmap-validate.md:301-307
  - spec-roadmap-validate.md:325-329
  - roadmap.md:47-49

  ---
  E. --dry-run coverage omission

  The spec includes explicit dry-run validation behavior; the roadmap planning
  omitted it.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - spec-roadmap-validate.md:498-499
  - roadmap.md:87-96
  - roadmap.md:115-138

  ---
  2) Phase 2 / 3 tasklists deviated from the roadmap

  These were a mix of scope additions, sequencing drift, and narrowed validation
  intent.

  Major tasklist-level findings

  A. Extra tier-classification tasks were added

  Both phase tasklists prepend tier-confirmation tasks that are not roadmap
  deliverables.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - phase-2-tasklist.md:7
  - phase-3-tasklist.md:7
  - roadmap.md:46-56
  - roadmap.md:64-78

  ---
  B. Tasklists added artifact/process overhead

  Per-task evidence/spec artifacts were introduced beyond what the roadmap
  explicitly required.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md

  Specific refs
  - phase-2-tasklist.md:75-76
  - phase-3-tasklist.md:75-76

  ---
  C. Tasklists tightened sequencing

  The roadmap allowed more phase-level parallelism than the tasklists actually
  encoded.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md

  Specific refs
  - roadmap.md:44-45
  - roadmap.md:76
  - roadmap.md:210-212
  - phase-2-tasklist.md:102
  - phase-2-tasklist.md:151
  - phase-3-tasklist.md:102
  - phase-3-tasklist.md:201

  ---
  D. “Known-bad outputs” got narrowed

  The roadmap intended testing against known-bad pipeline outputs; the tasklist
  wording narrowed this toward missing/malformed inputs.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md

  Specific refs
  - roadmap.md:78
  - phase-3-tasklist.md:179-183

  ---
  E. Multi-agent verification was under-specified in tasklist acceptance

  The roadmap explicitly requires verification of per-agent + merged reporting
  behavior; tasklist acceptance criteria under-emphasized that.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md

  Specific refs
  - roadmap.md:195-197
  - phase-3-tasklist.md:193-194

  ---
  F. Count-field naming drift

  The tasklist hardened generic count language into implementation-specific field
  names.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md

  Specific refs
  - roadmap.md:44
  - roadmap.md:73
  - phase-3-tasklist.md:88

  ---
  G. Traceability IDs in tasklists were not visibly backed by roadmap IDs

  Tasklists referred to roadmap item IDs not visibly present in the roadmap text.

  Relevant files
  - .dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md

  Specific refs
  - phase-2-tasklist.md:60
  - phase-3-tasklist.md:60
  - phase-3-tasklist.md:112
  - phase-3-tasklist.md:161

  ---
  Important architectural conclusion

  The sprint/task runner is not the primary fault domain

  Per your clarification:

  - the runner executes the tasklist
  - if the tasklist already contains deviations inherited from the roadmap, that
  is upstream drift
  - it is acceptable that the runner validates against the tasklist, not directly
  against the original spec

  This is the right model.

  The failure is upstream:
  - roadmap generation / acceptance
  - tasklist generation / acceptance

  ---
  Existing mechanisms already present in repo

  1) Pipeline gate infrastructure exists

  There is already reusable gate infrastructure for structural/programmatic
  validation.

  Key files
  - src/superclaude/cli/pipeline/gates.py
  - src/superclaude/cli/pipeline/models.py
  - src/superclaude/cli/roadmap/gates.py
  - src/superclaude/cli/roadmap/validate_gates.py

  What these currently cover

  Examples include:
  - required frontmatter fields
  - minimum line counts
  - agreement-table presence
  - semantic checks implemented as pure Python functions

  Important note
  These are valuable, but they are mostly structure-oriented, not a full blocking
  semantic “faithfulness to source artifact” check.

  ---
  2) /sc:reflect already supports deviation detection

  There is already a command conceptually designed for reflective validation and
  task-adherence checks.

  Key file
  - src/superclaude/commands/reflect.md

  Important sections
  - reflect.md:10-17
  - reflect.md:48-52
  - reflect.md:56-75

  This supports the idea that:
  - the capability already exists
  - the workflow just does not consistently operationalize it as a blocking gate
  where needed

  ---
  3) Reflection engine exists in code

  There is also a pre-execution reflection engine.

  Key files
  - src/superclaude/execution/reflection.py
  - src/superclaude/execution/__init__.py

  Important refs
  - reflection.py:60-72
  - reflection.py:90-119
  - reflection.py:391-400

  This again shows the ecosystem already contains reflection primitives.

  ---
  4) Tasklist protocol currently treats semantic gates as advisory

  This is one of the most important repo-level findings.

  Key file
  - src/superclaude/skills/sc-tasklist-protocol/SKILL.md

  Important refs
  - SKILL.md:864-868

  Meaning:
  - structural gates are blocking
  - semantic gates are advisory

  This likely explains why semantically wrong but structurally valid artifacts can
   continue downstream.

  ---
  Critical clarification: sc:roadmap-protocol already documents the desired check

  You specifically asked whether the roadmap protocol docs already describe this.

  Answer: yes, they do

  Relevant files

  - src/superclaude/skills/sc-roadmap-protocol/SKILL.md
  - src/superclaude/skills/sc-roadmap-protocol/refs/validation.md

  Why this matters

  The roadmap protocol already defines a Wave 4 Validation step where read-only
  agents validate generated roadmap artifacts against the source specification.

  Key references

  In refs/validation.md

  - refs/validation.md:14
    - validate generated roadmap artifacts against source specification
  - refs/validation.md:24-57
    - completeness / consistency / traceability / test-strategy checks
  - refs/validation.md:91-95
    - “Does the roadmap faithfully represent the spec?”
  - refs/validation.md:155-161
    - PASS / REVISE / REJECT thresholds
  - refs/validation.md:171-196
    - REVISE loop

  In SKILL.md

  - SKILL.md:229-245
    - Wave 4 validation
  - SKILL.md:236-239
    - dispatch quality-engineer and self-review agents in parallel
  - SKILL.md:239-243
    - score aggregation + revise loop

  Important interpretation

  The issue is therefore not that the concept is missing from docs.

  The real issue is likely one or more of:
  1. the documented validation wave is not always enforced in the actual concrete
  workflow path
  2. the scoring model is too soft/permissive to block obvious drift
  3. equivalent downstream conformance gates are missing, especially for:
    - roadmap → tasklist

  ---
  Harness: how it should be understood here

  Definition

  A harness in this context is a repeatable, automated, read-only validation
  wrapper around an artifact-producing step.

  It should:
  - take an upstream source-of-truth artifact
  - take a generated downstream artifact
  - run reflective/adversarial semantic review
  - emit normalized structured deviation findings
  - decide pass / warn / block

  ---
  Evidence that “harness” is already a repo pattern

  There are existing test harness patterns elsewhere in the repo.

  Relevant files
  - tests/sprint/diagnostic/conftest.py
  - tests/sprint/diagnostic/test_level_0.py
  - tests/sprint/diagnostic/test_level_2.py
  - tests/sprint/diagnostic/test_level_3.py

  These are not the same workflow, but they show the codebase already uses
  harness-style validation abstractions.

  ---
  Best solution direction

  Add blocking semantic conformance harnesses at artifact boundaries

  Gate A: Spec → Roadmap

  After roadmap generation:
  - compare roadmap.md against spec-roadmap-validate.md
  - optionally also include extraction.md and test-strategy.md
  - block on high-severity deviations

  Gate B: Roadmap → Tasklist

  After tasklist generation:
  - compare phase-*.md tasklists against roadmap.md
  - block on high-severity deviations

  Gate C: Tasklist → Execution

  Execution validates against the tasklist only.

  This preserves correct layering.

  ---
  Why this is high value

  1. It catches semantic drift that structural gates miss

  A document can:
  - satisfy frontmatter rules
  - satisfy min-line thresholds
  - contain all expected sections

  and still be wrong relative to the source artifact.

  2. It stops bad artifacts before they become downstream truth

  Once drift is encoded in the roadmap/tasklist, later steps can be “correct”
  relative to the wrong input.

  3. It turns an easy manual review into policy

  You already demonstrated that “ask an agent to find deviations” works well.

  4. It produces reusable evidence

  Normalized deviation reports can become:
  - diagnostics
  - audit artifacts
  - CI failure explanations
  - revise-loop inputs

  ---
  Recommended implementation framing

  Do not reinvent the concept

  Because sc-roadmap-protocol/refs/validation.md already documents the
  roadmap-side semantic validation pattern, the right move is to:

  - operationalize it
  - make it blocking where appropriate
  - extend the same pattern to tasklist generation

  ---
  Suggested normalized output contract

  For both roadmap and tasklist harnesses, emit rows with:

  - source_pair
  - severity
  - deviation
  - evidence
  - likely_impact
  - recommended_correction

  This matches the matrix format produced during this conversation and makes
  results easy to:
  - dedupe
  - score
  - gate on
  - feed back into revise loops

  ---
  Most relevant files to read first

  Highest-priority conversation-specific artifacts

  These are the first files a future agent should read.

  Source and generated artifacts

  - .dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md
  - .dev/releases/complete/v2.19-roadmap-validate/extraction.md
  - .dev/releases/complete/v2.19-roadmap-validate/test-strategy.md
  - .dev/releases/complete/v2.19-roadmap-validate/tasklist-index.md

  Checkpoints / supporting evidence

  - .dev/releases/complete/v2.19-roadmap-validate/checkpoints/CP-P02-END.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap-haiku-analyzer.md
  - .dev/releases/complete/v2.19-roadmap-validate/roadmap-opus-architect.md

  ---
  Workflow / protocol files

  Roadmap protocol

  - src/superclaude/skills/sc-roadmap-protocol/SKILL.md
  - src/superclaude/skills/sc-roadmap-protocol/refs/validation.md

  Tasklist protocol

  - src/superclaude/skills/sc-tasklist-protocol/SKILL.md
  - src/superclaude/skills/sc-tasklist-protocol/templates/phase-template.md

  Reflection capability

  - src/superclaude/commands/reflect.md
  - src/superclaude/execution/reflection.py

  Pipeline / gate infrastructure

  - src/superclaude/cli/pipeline/gates.py
  - src/superclaude/cli/pipeline/models.py
  - src/superclaude/cli/roadmap/gates.py
  - src/superclaude/cli/roadmap/validate_gates.py

  Existing roadmap validation implementation area

  - src/superclaude/cli/roadmap/commands.py
  - src/superclaude/cli/roadmap/executor.py
  - src/superclaude/cli/roadmap/models.py
  - src/superclaude/cli/roadmap/validate_executor.py
  - src/superclaude/cli/roadmap/validate_gates.py
  - src/superclaude/cli/roadmap/validate_prompts.py

  Tests around validate behavior

  - tests/roadmap/test_validate_cli.py
  - tests/roadmap/test_validate_defects.py
  - tests/roadmap/test_validate_executor.py
  - tests/roadmap/test_validate_gates.py
  - tests/roadmap/test_validate_resume_failure.py
  - tests/roadmap/test_validate_sc001_sc003.py
  - tests/roadmap/test_validate_unit.py

  Harness/testing pattern references

  - tests/sprint/diagnostic/conftest.py
  - tests/sprint/diagnostic/test_level_0.py
  - tests/sprint/diagnostic/test_level_2.py
  - tests/sprint/diagnostic/test_level_3.py

  ---
  Questions a future agent should start with

  1. Is the documented Wave 4 roadmap validation actually invoked in the concrete
  execution path used to generate these artifacts?
  2. If yes, why did it not block the roadmap/spec deviations identified here?
    - scoring too soft?
    - wrong prompt?
    - missing required evidence extraction?
    - non-blocking integration?
  3. Does /sc:tasklist have any equivalent blocking semantic conformance gate for
  roadmap → tasklist?
  4. Should semantic conformance move from advisory to blocking at artifact
  boundaries?
  5. What is the smallest harness contract that can be reused across roadmap and
  tasklist generation?

  ---
  Recommended design principle

  Validate each artifact against its immediate upstream source of truth, and make
  semantic conformance blocking before generating the next artifact.

  Concretely:
  - roadmap vs spec
  - tasklist vs roadmap
  - execution vs tasklist

  That is the central solution direction supported by this conversation.

  ---
 