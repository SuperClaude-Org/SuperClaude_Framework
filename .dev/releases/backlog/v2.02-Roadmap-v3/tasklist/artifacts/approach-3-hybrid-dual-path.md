## Approach 3: Hybrid Dual-Path with Graceful Degradation

**Document type**: Architectural proposal for sc:roadmap adversarial pipeline invocation
**Scope**: Modifications to the P6 sprint spec (`tasklist-P6.md`) and affected skill files
**Status**: PROPOSAL (not yet accepted)
**Date**: 2026-02-23

---

### Table of Contents

1. [Philosophy](#1-philosophy)
2. [Runtime Routing Logic](#2-runtime-routing-logic)
3. [Path A: claude -p Headless Invocation](#3-path-a-claude--p-headless-invocation)
4. [Path B: Enhanced Task-Agent Pipeline](#4-path-b-enhanced-task-agent-pipeline)
5. [Sprint-Spec Modifications](#5-sprint-spec-modifications)
6. [The Abstraction: Return Contract as Universal Interface](#6-the-abstraction-return-contract-as-universal-interface)
7. [Risk Analysis](#7-risk-analysis)
8. [Verification Plan](#8-verification-plan)

---

### 1. Philosophy

#### Why dual-path? Why not commit to one mechanism?

The current sprint spec (tasklist-P6.md) treats the invocation problem as a binary decision: Task 0.0 probes Skill tool viability, then the sprint commits to either the primary path (Skill tool) or the "Fallback-Only Sprint Variant." This commit-once architecture has three structural weaknesses.

**Problem 1: Environment portability.** `claude -p` (the headless CLI) is not universally available. It requires the `claude` binary in PATH, permission to spawn external processes via Bash, and an environment that does not restrict subprocess execution (some Docker images, CI runners, and sandboxed Claude Code instances block this). A sprint that depends on `claude -p` being available will fail silently in these environments. Conversely, a sprint that only uses Task agents leaves performance on the table when `claude -p` IS available.

**Problem 2: Mid-pipeline fragility.** The current fallback protocol activates only at invocation time (step 3d). If a `claude -p` session crashes mid-pipeline (after producing variant files but before completing the debate), the entire adversarial pipeline fails. There is no mechanism to resume from partial state using the Task-agent path. A dual-path architecture enables mid-pipeline handover: if headless crashes after Step 1, Task agents can pick up from Step 2 using the already-written `diff-analysis.md`.

**Problem 3: Quality tiering misalignment.** The `--depth` flag (quick/standard/deep) currently controls only debate rounds. It does not influence invocation strategy. This is a missed optimization: `--depth quick` (1 debate round) gains little from the overhead of launching a headless session, while `--depth deep` (3 rounds, extended convergence tracking) benefits substantially from the higher fidelity of a dedicated Claude Code session. Aligning invocation mechanism with depth creates a natural quality tier.

**Problem 4: Future-proofing.** When Anthropic ships the Skill tool as a callable API (currently unavailable per the sprint spec), it should slot in as a third invocation path without requiring consumer-side changes. The dual-path architecture, with its return-contract abstraction boundary, already supports this: a third path simply needs to produce the same `return-contract.yaml` schema.

#### Design principle

Both paths are first-class citizens. Neither is "primary" or "fallback." The runtime router selects the optimal path based on environment capabilities and user preferences. The return contract is the abstraction boundary that makes the choice invisible to downstream consumers.

```
Invocation Strategy Selector
       |
       +---> [Path A: claude -p]     ---> return-contract.yaml
       |                                        |
       +---> [Path B: Task agents]   ---> return-contract.yaml
       |                                        |
       +---> [Path C: Skill tool]    ---> return-contract.yaml  (future)
                                                |
                                         sc:roadmap step 3e
                                    (consumer, path-agnostic)
```

---

### 2. Runtime Routing Logic

#### Decision Tree

The router executes at the start of Wave 2 step 3d (multi-roadmap mode) or Wave 1A step 2 (multi-spec mode). It produces a single decision: which invocation path to use.

```yaml
routing_decision_tree:
  step_0_user_override:
    check: "--invocation-mode flag present?"
    values:
      headless: "Force Path A (claude -p). If unavailable, abort with error."
      inline: "Force Path B (Task agents). Skip capability probe."
      auto: "Proceed to automated detection (default)."
    note: "User override takes absolute precedence."

  step_1_binary_check:
    check: "Is `claude` binary available in PATH?"
    method: "Bash: which claude 2>/dev/null; echo $?"
    fail_action: "Eliminate Path A. Select Path B."
    pass_action: "Proceed to step 2."

  step_2_execution_check:
    check: "Can claude -p execute successfully?"
    method: |
      Bash: claude -p "respond with exactly: PROBE_OK" \
        --output-format json \
        --max-budget-usd 0.01 \
        --permission-mode bypassPermissions 2>/dev/null
    parse: "Check JSON output contains 'PROBE_OK'"
    fail_action: "Eliminate Path A. Select Path B."
    pass_action: "Proceed to step 3."
    timeout: "15 seconds"

  step_3_depth_routing:
    check: "What is the --depth value?"
    routing:
      quick: "Select Path B (Task agents)"
      standard: "Select Path A (claude -p)"
      deep: "Select Path A (claude -p) with extended budget"
    rationale: |
      --depth quick uses 1 debate round. The overhead of launching
      a headless session (~5-10s startup) is not justified for a
      single-round debate. Task agents achieve equivalent fidelity
      for quick depth at lower latency.

  step_4_emit_decision:
    action: "Log routing decision with rationale"
    format: |
      "Invocation path selected: <Path A|Path B>
       Reason: <binary_available|execution_check|depth_routing|user_override>
       Depth: <quick|standard|deep>
       Environment: <claude_binary: present|absent>"
```

#### New Flag: `--invocation-mode`

Added to sc:roadmap's flag table (Section 3 of SKILL.md):

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--invocation-mode` | | No | `auto` | Adversarial invocation strategy: `headless` (force claude -p), `inline` (force Task agents), `auto` (runtime detection) |

This flag is consumed only in adversarial modes (`--specs` or `--multi-roadmap`). In standard single-spec mode, it is ignored.

#### Routing Decision Cache

The routing decision is made once per sc:roadmap invocation and cached for the session. If the same invocation triggers both Wave 1A (multi-spec) and Wave 2 (multi-roadmap) adversarial passes (combined mode), both use the same routing decision. Rationale: environment capabilities do not change mid-session.

---

### 3. Path A: claude -p Headless Invocation

#### When selected

Path A activates when the routing decision tree selects `headless`. This means: `claude` binary is in PATH, the execution probe succeeded, and either `--depth standard|deep` or `--invocation-mode headless` was specified.

#### Command Construction

```yaml
headless_command_construction:
  base_command: "claude"
  flags:
    prompt: "-p"
    output_format: "--output-format json"
    permission_mode: "--permission-mode bypassPermissions"
    max_budget:
      depth_quick: "--max-budget-usd 0.50"
      depth_standard: "--max-budget-usd 2.00"
      depth_deep: "--max-budget-usd 5.00"
    allowed_tools: "--allowedTools Read,Write,Edit,Glob,Grep,Bash,Task"

  system_prompt_injection:
    method: "--append-system-prompt"
    content: |
      Constructed at runtime by reading the sc:adversarial SKILL.md file
      and extracting the relevant step instructions. The full SKILL.md
      content (1747 lines) is injected as the system prompt supplement.
    construction_steps:
      1: "Read src/superclaude/skills/sc-adversarial/SKILL.md via Read tool"
      2: "Read relevant refs (debate-protocol.md, scoring-protocol.md, artifact-templates.md)"
      3: "Concatenate into a single system prompt string"
      4: "Escape for shell: replace single quotes, handle newlines"
      5: "Pass via --append-system-prompt flag"

  prompt_construction:
    mode_a_compare: |
      Execute the sc:adversarial 5-step pipeline in --compare mode.
      Input files: {comma_separated_variant_paths}
      Depth: {depth_value}
      Output directory: {output_dir}
      Interactive: {true|false}
      Convergence threshold: {convergence_value}

      Execute all 5 steps: Diff Analysis, Adversarial Debate,
      Hybrid Scoring & Base Selection, Refactoring Plan, Merge Execution.

      Write return-contract.yaml to {output_dir}/return-contract.yaml
      with fields: status, merged_output_path, convergence_score,
      artifacts_dir, unresolved_conflicts, base_variant, fallback_mode,
      failure_stage, invocation_method.

      Set invocation_method to "headless" in the return contract.

    mode_b_generate: |
      Execute the sc:adversarial 5-step pipeline in --source/--generate mode.
      Source file: {source_path}
      Generate type: roadmap
      Agents: {expanded_agent_specs}
      Depth: {depth_value}
      Output directory: {output_dir}
      Interactive: {true|false}

      [Same 5-step instructions and return contract requirements as mode_a]

  full_command_template: |
    claude -p "{prompt_text}" \
      --output-format json \
      --permission-mode bypassPermissions \
      --max-budget-usd {budget} \
      --allowedTools Read,Write,Edit,Glob,Grep,Bash,Task \
      --append-system-prompt "{system_prompt_content}"
```

#### Output Capture and Return Contract Parsing

```yaml
output_handling:
  capture:
    method: "Bash tool captures stdout"
    format: "JSON (--output-format json)"
    fields_extracted:
      result: "The text output from the headless session"
      is_error: "Boolean indicating execution error"
      cost: "Token cost of the headless session"

  return_contract_parsing:
    step_1: "Check Bash exit code. Non-zero = invocation failure."
    step_2: "Check is_error field in JSON output. True = session-level failure."
    step_3: "Read {output_dir}/return-contract.yaml via Read tool."
    step_4: "Parse YAML. If parse error, treat as status: failed."
    step_5: "Validate all required fields present."
    step_6: "Proceed to step 3e (consumer routing) with parsed contract."

  missing_contract_handling:
    condition: "return-contract.yaml does not exist after headless session completes"
    action: "Trigger mid-pipeline fallover (see below)"
```

#### Timeout and Budget Handling

`--max-budget-usd` serves as a proxy for timeout. The headless session terminates when the budget is exhausted. Budget values are calibrated to the expected token consumption of each depth level:

| Depth | Budget | Expected Duration | Rationale |
|-------|--------|-------------------|-----------|
| quick | $0.50 | 2-5 min | 1 debate round, minimal scoring |
| standard | $2.00 | 5-15 min | 2 debate rounds, full scoring |
| deep | $5.00 | 10-30 min | 3 debate rounds, convergence tracking, extended merge |

If the session terminates due to budget exhaustion before producing `return-contract.yaml`, this is treated as a headless failure and triggers mid-pipeline fallover.

#### Mid-Pipeline Fallover: Headless to Task-Agent

This is the key architectural advantage of the dual-path approach. If the headless session fails partway through the 5-step pipeline, the artifacts it DID produce are not wasted.

```yaml
mid_pipeline_fallover:
  trigger_conditions:
    - "Headless session exits with non-zero code"
    - "return-contract.yaml not found after session completes"
    - "return-contract.yaml has status: failed AND failure_stage indicates partial completion"
    - "Budget exhaustion before pipeline completion"

  artifact_inventory:
    action: "Scan {output_dir}/adversarial/ for existing artifacts"
    check_order:
      - "variant-*.md files (Step 0 / Mode B generation)"
      - "diff-analysis.md (Step 1 output)"
      - "debate-transcript.md (Step 2 output)"
      - "base-selection.md (Step 3 output)"
      - "refactor-plan.md (Step 4 output)"
      - "merge-log.md + merged-output.md (Step 5 output)"

  resume_logic:
    all_5_steps_present:
      action: "Pipeline likely completed but contract write failed"
      recovery: "Task agent reads artifacts, produces return-contract.yaml"
      resume_from: "Contract assembly only"

    steps_1_through_3_present:
      action: "Debate and scoring complete, merge not started"
      recovery: "Path B Task agent executes Steps 4-5 from base-selection.md"
      resume_from: "F4 (Refactoring Plan)"

    step_1_present:
      action: "Diff analysis complete, debate not started"
      recovery: "Path B Task agents execute Steps 2-5"
      resume_from: "F3 (Debate)"

    variants_only:
      action: "Variants generated but no analysis"
      recovery: "Path B Task agents execute Steps 1-5"
      resume_from: "F2 (Diff Analysis)"

    nothing_present:
      action: "Headless session produced nothing"
      recovery: "Full Path B execution from scratch"
      resume_from: "F1 (Variant Generation, if Mode B) or F2 (if Mode A)"

  fallover_logging:
    emit: |
      "WARNING: Headless session failed at stage {failure_stage}.
       Artifacts found: {artifact_list}.
       Resuming via Task-agent path from {resume_point}.
       invocation_method in return contract will be 'headless+task_agent'."
```

The `failure_stage` field in the return contract (new field, see Section 6) enables precise resume-point determination. If the headless session DID write a partial return contract before crashing, `failure_stage` tells the fallover logic exactly where to resume.

---

### 4. Path B: Enhanced Task-Agent Pipeline

#### When selected

Path B activates when the routing decision tree selects `inline`. This occurs when: `claude` binary is absent, the execution probe fails, `--depth quick` is specified, or `--invocation-mode inline` is set.

#### Upgrade from Current 3-Step to Full 5-Step Pipeline

The current sprint spec's fallback protocol compresses the 5-step adversarial pipeline into 3 merged steps (F1, F2/3, F4/5). This loses fidelity: the single-round debate in F2/3 cannot track convergence, and the merged F4/5 cannot produce the detailed base-selection.md scoring breakdown. Approach 3 upgrades to a full 5-step Task-agent pipeline.

```yaml
enhanced_task_agent_pipeline:
  instruction_source: "src/superclaude/skills/sc-adversarial/SKILL.md"
  instruction_delivery: |
    Each Task agent receives its instructions by having the orchestrating
    sc:roadmap wave read the relevant section from sc:adversarial SKILL.md
    and pass it as part of the Task agent prompt. This avoids depending on
    the Task agent being able to invoke skills or read files independently.

  F1_variant_generation:
    description: "Generate variant artifacts (Mode B) or copy input files (Mode A)"
    delegation: "Parallel Task agents (one per agent spec)"
    fidelity_vs_original: "Equivalent to sc:adversarial Mode B generation (T06.02)"
    instructions_from: "SKILL.md 'Mode B Variant Generation (T06.02)' section"
    prompt_template: |
      Generate a {generation_type} artifact from the following source material.
      Use your expertise as {persona} to produce the highest-quality
      {generation_type} possible.
      {custom_instruction}

      Source material:
      {source_file_content}

      Write your output as a complete markdown document.
    output: "{output_dir}/adversarial/variant-N-{model}-{persona}.md"
    validation: "Each variant non-empty, at least 2 variants produced"
    skip_condition: "Mode A (files already exist as inputs)"

  F2_diff_analysis:
    description: "Structural diff, content diff, contradiction detection, unique contributions"
    delegation: "Single Task agent with analytical prompt"
    fidelity_vs_original: "Full Step 1 fidelity"
    instructions_from: "SKILL.md 'Implementation Details - Step 1: Diff Analysis Engine' section"
    prompt_template: |
      You are performing Step 1 (Diff Analysis) of the sc:adversarial pipeline.

      Read all variant files in {output_dir}/adversarial/:
      {variant_file_list}

      Execute the following analyses IN ORDER:
      1. STRUCTURAL DIFF: Compare heading hierarchies, section ordering.
         Use severity ratings: Low (cosmetic), Medium (different grouping),
         High (incompatible organization). ID scheme: S-NNN.
      2. CONTENT DIFF: Compare approaches topic-by-topic.
         Use severity: Low (same via different wording), Medium (different approaches),
         High (incompatible strategies). ID scheme: C-NNN.
      3. CONTRADICTION DETECTION: Scan for opposing claims, requirement-constraint
         conflicts, impossible sequences. Must be falsifiable claims only.
         ID scheme: X-NNN.
      4. UNIQUE CONTRIBUTIONS: Ideas in only one variant.
         Value: High/Medium/Low. ID scheme: U-NNN.

      Write the complete diff-analysis.md to:
      {output_dir}/adversarial/diff-analysis.md

      Include a Summary section with counts per category.
      If total differences < 10% of comparable items, note "variants substantially identical."
    output: "{output_dir}/adversarial/diff-analysis.md"
    validation: "File exists, non-empty, all 4 sections present"
    similarity_check: "If <10% differences, skip F3 debate, proceed to F4"

  F3_adversarial_debate:
    description: "Multi-round steelman debate with convergence tracking"
    delegation: "Orchestrator Task agent coordinating advocate Task agents"
    fidelity_vs_original: "Full Step 2 fidelity (multi-round, convergence tracking)"
    instructions_from: "SKILL.md 'Implementation Details - Step 2: Adversarial Debate Protocol'"

    round_1:
      description: "Parallel advocate statements"
      delegation: "Parallel Task agents (one per variant)"
      prompt_per_advocate: |
        You are an advocate for {variant_name} in a structured adversarial debate.

        YOUR VARIANT:
        {variant_content}

        OTHER VARIANTS:
        {other_variants_content}

        DIFF ANALYSIS:
        {diff_analysis_content}

        RULES:
        1. Present your variant's strengths with EVIDENCE (cite sections, quotes)
        2. STEELMAN opposing variants BEFORE critiquing them:
           - State the strongest version of their argument
           - Identify what their approach genuinely gets right
           - THEN present your critique with counter-evidence
        3. Acknowledge genuine weaknesses in your variant honestly

        OUTPUT FORMAT:
        ## Position Summary
        [1-3 sentences]
        ## Steelman of Opposing Variants
        [Per-variant subsection]
        ## Strengths Claimed
        [Numbered, with evidence]
        ## Weaknesses Identified in Others
        [Numbered, with evidence]
        ## Concessions
        [Honest weaknesses in own variant]
      execution: "All advocates dispatched in single parallel Task batch"

    round_2:
      condition: "--depth standard OR --depth deep"
      description: "Sequential rebuttals"
      delegation: "Sequential Task agents (each sees all Round 1 transcripts)"
      prompt_per_advocate: |
        You are rebutting criticisms in Round 2 of an adversarial debate.

        ALL ROUND 1 TRANSCRIPTS:
        {round_1_transcripts}

        CRITICISMS RAISED AGAINST YOUR VARIANT:
        {specific_criticisms}

        Respond to each criticism with counter-evidence or concession.
        Provide updated assessment of other variants.
      execution: "Sequential (each advocate sees previous rebuttals)"

    round_3:
      condition: "--depth deep AND convergence < threshold after Round 2"
      description: "Final arguments"
      delegation: "Sequential Task agents"
      prompt_per_advocate: |
        Final round. Consider all prior rounds.
        UNRESOLVED DISAGREEMENTS: {unresolved_list}
        Provide final position and any remaining concessions.

    convergence_tracking:
      method: |
        After each round, the orchestrator Task agent evaluates convergence:
        - For each diff point (S-NNN, C-NNN, X-NNN), determine if advocates
          agree on the superior approach
        - Agreement = unanimous or 2/3+ majority
        - convergence = agreed_points / total_diff_points
        - Track per-point positions across rounds
      orchestrator_prompt: |
        You are the debate orchestrator. Read all advocate transcripts
        from this round.

        DIFF POINTS from diff-analysis.md:
        {diff_point_list}

        For each diff point, determine:
        1. Which variant's approach is favored by majority of advocates?
        2. Confidence level (50-100%)
        3. Is this point RESOLVED (majority agree) or UNRESOLVED?

        Compute convergence = resolved / total.
        Current threshold: {convergence_threshold}.

        Output a scoring matrix table and convergence assessment.
      note: |
        This is the critical fidelity upgrade from the current fallback.
        The current F2/3 merged step uses a fixed 0.5 convergence sentinel.
        This enhanced version computes real convergence from debate evidence.

    output: "{output_dir}/adversarial/debate-transcript.md"
    validation: "Transcript includes all executed rounds, scoring matrix, convergence assessment"

  F4_hybrid_scoring_and_base_selection:
    description: "Dual-pass quantitative + qualitative scoring with position-bias mitigation"
    delegation: "Single Task agent with scoring rubric"
    fidelity_vs_original: "Full Step 3 fidelity (25-criterion rubric, dual-pass)"
    instructions_from: "SKILL.md 'Implementation Details - Step 3: Hybrid Scoring & Base Selection'"
    prompt_template: |
      You are performing hybrid scoring and base selection for the
      sc:adversarial pipeline.

      VARIANTS: {variant_file_list}
      DEBATE TRANSCRIPT: {debate_transcript_content}
      SOURCE REQUIREMENTS: {source_content}

      Execute TWO scoring layers:

      LAYER 1 - QUANTITATIVE (50% weight):
      Compute 5 deterministic metrics per variant:
      - RC (Requirement Coverage, 0.30): grep source requirements in variant
      - IC (Internal Consistency, 0.25): 1 - (contradictions / claims)
      - SR (Specificity Ratio, 0.15): concrete / (concrete + vague)
      - DC (Dependency Completeness, 0.15): resolved refs / total refs
      - SC (Section Coverage, 0.15): sections / max(sections)
      Formula: quant = (RC*0.30)+(IC*0.25)+(SR*0.15)+(DC*0.15)+(SC*0.15)

      LAYER 2 - QUALITATIVE (50% weight):
      25-criterion binary rubric across 5 dimensions (5 criteria each):
      Completeness, Correctness, Structure, Clarity, Risk Coverage.
      For EACH criterion, use Claim-Evidence-Verdict (CEV):
        CLAIM: "[criterion] is met/not met"
        EVIDENCE: "[quote or section reference]"
        VERDICT: MET (1) or NOT MET (0)

      POSITION-BIAS MITIGATION:
      Pass 1: Score variants in input order (A, B, C...)
      Pass 2: Score variants in reverse order (C, B, A...)
      For disagreements: re-evaluate with both pieces of evidence.

      COMBINED: score = (0.50 * quant) + (0.50 * qual)
      Select highest-scoring variant as base.
      If top two within 5%: apply tiebreaker (debate points > correctness > input order).

      Write base-selection.md to:
      {output_dir}/adversarial/base-selection.md
    output: "{output_dir}/adversarial/base-selection.md"
    validation: "File exists, quant + qual sections present, base selected"

  F5_refactoring_plan_and_merge:
    description: "Generate refactoring plan from base + non-base strengths, then execute merge"
    delegation: "Two sequential Task agents: planner then executor"
    fidelity_vs_original: "Full Steps 4+5 fidelity"
    instructions_from: "SKILL.md 'Implementation Details - Steps 4-5'"

    planner_prompt: |
      You are generating a refactoring plan for the adversarial merge.

      BASE VARIANT: {base_variant_content}
      BASE SELECTION RATIONALE: {base_selection_content}
      ALL VARIANTS: {all_variant_contents}
      DEBATE TRANSCRIPT: {debate_transcript_content}

      For each strength from non-base variants:
      - Source variant and section
      - Target location in base
      - Rationale (cite debate evidence)
      - Integration approach: replace | append | insert | restructure
      - Risk level: Low | Medium | High

      For each base weakness identified in debate:
      - Issue description
      - Better variant reference
      - Fix approach

      Document changes NOT being made (rejected alternatives with rationale).

      Write refactor-plan.md to:
      {output_dir}/adversarial/refactor-plan.md

    executor_prompt: |
      You are the merge executor. Apply the refactoring plan to produce
      a unified merged artifact.

      BASE VARIANT: {base_variant_content}
      REFACTORING PLAN: {refactor_plan_content}

      For each planned change:
      1. Apply the change to the base
      2. Add provenance annotation: <!-- Source: Variant N, Section ref -->
      3. Maintain structural integrity (heading hierarchy, section flow)

      After all changes:
      - Validate heading hierarchy (no gaps like H2->H4)
      - Validate internal references resolve
      - Scan for NEW contradictions introduced by merge

      Write:
      - Merged output to: {output_dir}/merged-output.md
      - Merge log to: {output_dir}/adversarial/merge-log.md

    output:
      - "{output_dir}/merged-output.md"
      - "{output_dir}/adversarial/refactor-plan.md"
      - "{output_dir}/adversarial/merge-log.md"

  F_contract:
    description: "Produce return-contract.yaml after pipeline completion"
    delegation: "Inline (sc:roadmap writes directly, no Task agent needed)"
    action: |
      After F5 completes, sc:roadmap assembles return-contract.yaml
      from pipeline artifacts:
      - status: derived from merge validation results
      - merged_output_path: {output_dir}/merged-output.md
      - convergence_score: from F3 convergence tracking
      - artifacts_dir: {output_dir}/adversarial/
      - unresolved_conflicts: count from F3 convergence assessment
      - base_variant: from F4 base selection
      - fallback_mode: false (this IS the designed path, not a fallback)
      - failure_stage: null (success) or last completed step
      - invocation_method: "task_agent"
    output: "{output_dir}/return-contract.yaml"
```

#### How Each Task Agent Gets Its Instructions

The key operational detail: each Task agent receives its instructions inline in the Task prompt, NOT by being told to read SKILL.md. This is critical because Task agents may not have file-reading context from the parent session.

```yaml
instruction_delivery_protocol:
  step_1: |
    sc:roadmap (the orchestrating session) reads the sc:adversarial SKILL.md
    at the start of the adversarial pipeline execution.
  step_2: |
    For each Task agent dispatch, sc:roadmap extracts the relevant section
    from the SKILL.md content and injects it directly into the Task prompt.
  step_3: |
    The Task agent receives its instructions as part of its prompt text,
    NOT as a reference to a file it must read.

  example:
    for_F2_diff_analysis: |
      sc:roadmap reads SKILL.md lines 411-749 (Step 1 implementation details).
      These are included verbatim in the F2 Task agent prompt.
    for_F3_advocate: |
      sc:roadmap reads SKILL.md lines 753-856 (Round 1 protocol).
      These are included verbatim in each advocate Task agent prompt.
    for_F4_scoring: |
      sc:roadmap reads SKILL.md lines 1049-1299 (Step 3 implementation details).
      These are included verbatim in the F4 Task agent prompt.

  rationale: |
    This approach ensures Task agents have full instruction context
    regardless of their file-system access. It also means the instructions
    are version-locked to what sc:roadmap read at dispatch time.
```

#### Convergence Tracking in the Task-Agent Path

The current fallback uses a hardcoded `convergence_score: 0.5` sentinel. The enhanced path computes real convergence.

```yaml
real_convergence_tracking:
  mechanism: |
    After each debate round, the orchestrator Task agent
    (a dedicated Task, not one of the advocates) reads all
    advocate transcripts and evaluates per-point agreement.

  computation:
    input: "All advocate transcripts + diff-analysis.md diff points"
    process:
      1: "List all diff points (S-NNN, C-NNN, X-NNN) from diff-analysis.md"
      2: "For each point, extract each advocate's position"
      3: "Determine agreement: unanimous, majority (>= 2/3), or split"
      4: "agreed_count = points with unanimous or majority agreement"
      5: "convergence = agreed_count / total_diff_points"
    output: "Numeric convergence score (0.0 - 1.0)"

  round_progression:
    after_round_1: "Compute convergence. If >= threshold, skip further rounds."
    after_round_2: "Compute convergence. If >= threshold OR --depth standard, stop."
    after_round_3: "Final convergence measurement (--depth deep only)."

  comparison_with_current_fallback:
    current: "Fixed 0.5 sentinel regardless of actual agreement"
    enhanced: "Computed from advocate positions per diff point"
    fidelity_gain: "From ~70% to ~90% of headless path fidelity"
```

---

### 5. Sprint-Spec Modifications

#### Task 0.0: Replace with "Invocation Capability Probe"

The current T01.01 (Skill Tool Probe) tests only the Skill tool path. Approach 3 replaces it with a dual-path capability probe.

```yaml
T01_01_replacement:
  old_name: "Skill Tool Probe"
  new_name: "Invocation Capability Probe"
  old_purpose: "Determine if Skill tool is viable; commit to primary or fallback"
  new_purpose: "Determine which invocation paths are available; record capabilities"

  phase_A_headless_check:
    step_1: "Run: which claude 2>/dev/null; echo $?"
    step_2: |
      If binary found, run 3 probe executions:
      claude -p "respond with exactly: PROBE_OK" \
        --output-format json \
        --max-budget-usd 0.01 \
        --permission-mode bypassPermissions
    step_3: "Record: binary_present (bool), probe_success_count (0-3), avg_latency_ms"
    decision: "headless_available = binary_present AND probe_success_count >= 2"

  phase_B_task_agent_smoke_test:
    step_1: |
      Dispatch a minimal Task agent:
      "Read the file at {any_existing_file_path} and respond with
       the word count. Format: WORD_COUNT: <N>"
    step_2: "Verify Task agent returns a parseable response"
    step_3: "Record: task_agent_available (bool), response_latency_ms"
    decision: "task_agent_available = response received AND parseable"

  combined_decision:
    both_available: |
      Record: "Both paths available. Runtime routing will select based on
      --depth and --invocation-mode flags."
    headless_only: |
      Record: "Only headless path available. Task agent dispatch failed.
      WARNING: No fallover capability if headless fails mid-pipeline."
    task_agent_only: |
      Record: "Only Task-agent path available. claude -p not found or
      failed probe. All adversarial invocations will use inline pipeline."
    neither_available: |
      ABORT: "Neither invocation path is functional. Cannot execute
      adversarial pipeline. Check environment configuration."

  deliverables:
    D_0001: "Capability probe result document with both phase results"
    D_0002: "Routing capability record (replaces sprint variant decision)"
```

#### Epic 1 (Phase 2): Task T02.03 Modifications

The current T02.03 writes Wave 2 step 3d with a single invocation mechanism (Skill tool primary, fallback protocol). Approach 3 replaces step 3d with a routing decision and two execution branches.

```yaml
T02_03_step_3d_rewrite:
  current_structure: |
    Step 3d: Execute fallback protocol unconditionally
    - F1: Variant generation
    - F2/3: Diff analysis + single-round debate (merged)
    - F4/5: Base selection + merge + contract (merged)

  new_structure: |
    Step 3d: Execute invocation routing
    - 3d-i:   Run routing decision tree (see Section 2)
    - 3d-ii:  If Path A selected: execute headless invocation (see below)
    - 3d-iii: If Path B selected: execute enhanced Task-agent pipeline (see below)
    - 3d-iv:  If Path A fails mid-pipeline: trigger fallover to Path B
              at the appropriate resume point

    Step 3d Path A (headless):
    - Construct claude -p command per Section 3
    - Execute via Bash tool
    - Capture JSON output
    - Parse return-contract.yaml from output directory
    - If missing: trigger 3d-iv fallover

    Step 3d Path B (inline):
    - F1: Variant generation (parallel Task agents, same as current)
    - F2: Diff Analysis (dedicated Task agent with Step 1 spec)
    - F3: Multi-Round Debate (orchestrator + advocate Task agents,
           rounds 2-3 conditional on --depth)
    - F4: Hybrid Scoring & Base Selection (Task agent with Step 3 spec,
           dual-pass, 25-criterion rubric)
    - F5: Refactoring Plan + Merge (planner + executor Task agents)
    - FC: Contract assembly (inline write by sc:roadmap)

  both_branches_produce: "Identical return-contract.yaml schema"

  quality_metadata: |
    Return contract includes:
    invocation_method: "headless" | "task_agent" | "headless+task_agent"
    The third value indicates mid-pipeline fallover occurred.
```

#### Epic 2 (Phase 5): Verb Glossary Additions

```yaml
verb_glossary_additions:
  existing_verbs:
    - "Invoke skill" = Skill tool call
    - "Dispatch agent" = Task tool call
    - "Read ref" = Read tool call
    - "Write artifact" = Write tool call

  new_verbs:
    - verb: "Launch headless session"
      tool: "Bash(claude -p ...)"
      context: "Path A adversarial invocation via claude CLI in headless mode"
      used_in: "Wave 2 step 3d Path A, Wave 1A step 2 Path A"

    - verb: "Execute inline pipeline"
      tool: "Task agent dispatch sequence (F1-F5)"
      context: "Path B adversarial invocation via enhanced Task-agent pipeline"
      used_in: "Wave 2 step 3d Path B, Wave 1A step 2 Path B"

    - verb: "Route invocation"
      tool: "Routing decision tree (Bash + conditional logic)"
      context: "Determine which invocation path to use"
      used_in: "Wave 2 step 3d-i, Wave 1A step 2 pre-invocation"

    - verb: "Trigger fallover"
      tool: "Artifact inventory scan + Path B resume"
      context: "Mid-pipeline switch from Path A to Path B"
      used_in: "Wave 2 step 3d-iv"
```

#### Epic 3 (Phase 4): Return Contract Schema Changes

```yaml
return_contract_schema_v2:
  fields:
    status:
      type: "enum"
      values: ["success", "partial", "failed"]
      unchanged: true

    merged_output_path:
      type: "string"
      unchanged: true

    convergence_score:
      type: "float (0.0-1.0)"
      change: "Now computed from real debate evidence in Path B (was 0.5 sentinel)"

    artifacts_dir:
      type: "string"
      unchanged: true

    unresolved_conflicts:
      type: "integer"
      unchanged: true

    base_variant:
      type: "string (model:persona)"
      unchanged: true

    fallback_mode:
      type: "boolean"
      change: |
        Semantics shift. In the current spec, true = "Skill tool unavailable,
        used fallback." In Approach 3, this field is DEPRECATED in favor of
        invocation_method. Set to false regardless of path for backward
        compatibility. Remove in next major version.

    failure_stage:
      type: "string | null"
      unchanged: true

    invocation_method:
      type: "enum"
      values: ["headless", "task_agent", "headless+task_agent", "skill"]
      new: true
      description: |
        10th field. Records which invocation path produced this contract.
        - "headless": Path A (claude -p) completed successfully
        - "task_agent": Path B (enhanced Task-agent pipeline) completed
        - "headless+task_agent": Path A started, mid-pipeline fallover to Path B
        - "skill": Future Path C (native Skill tool API) completed
      consumer_guidance: |
        This field is INFORMATIONAL. Consumers (step 3e) MUST NOT branch
        on invocation_method. The return contract schema is the abstraction
        boundary. If consumers start routing on invocation_method, the
        dual-path architecture's value is undermined.

  canonical_schema_comment: |
    # return-contract.yaml fields (v2):
    # status, merged_output_path, convergence_score, fallback_mode,
    # artifacts_dir, unresolved_conflicts, base_variant, failure_stage,
    # invocation_method
```

---

### 6. The Abstraction: Return Contract as Universal Interface

The return contract is the single abstraction boundary between invocation mechanism and consumer logic. This is the architectural centerpiece of Approach 3.

```
                    +-------------------+
                    |  Invocation Layer |
                    |                   |
  Path A ---------> |  return-contract  |
  Path B ---------> |     .yaml         | ---------> step 3e consumer
  Path C (future) -> |                   |            (path-agnostic)
                    +-------------------+
```

**Invariants**:

1. **Schema identity**: All paths produce the exact same 9+1 field schema. No path adds extra fields. No path omits required fields.

2. **Consumer ignorance**: Step 3e in sc:roadmap SKILL.md reads `return-contract.yaml` and routes on `status` and `convergence_score`. It does NOT read `invocation_method`. The consumer does not know and does not care how the contract was produced.

3. **Quality equivalence**: While fidelity differs between paths (Path A ~95%, Path B ~85-90%), the return contract schema does not expose this difference. The `invocation_method` field exists for observability (logging, debugging, quality auditing) but is not a routing signal.

4. **Third-path readiness**: When the Skill tool API becomes available, adding a third path requires:
   - Implementing a Skill tool invocation in the routing decision tree
   - Having the Skill tool produce `return-contract.yaml` with the same schema
   - Setting `invocation_method: "skill"`
   - Zero changes to step 3e consumer logic

5. **Convergence score consistency**: Both paths now compute real convergence scores (Path B upgraded from 0.5 sentinel). Consumers can rely on `convergence_score` as a meaningful quality signal regardless of path.

---

### 7. Risk Analysis

#### R1: Maintenance Complexity of Two Paths

**Risk**: Two invocation paths means two code paths that must be kept in sync when the sc:adversarial pipeline changes. A change to Step 3's scoring rubric must be reflected in both the headless system prompt AND the Path B F4 Task agent prompt.

**Severity**: Medium.

**Mitigation**: Both paths source their instructions from the same file (`sc:adversarial SKILL.md`). Path A injects it via `--append-system-prompt`, Path B extracts relevant sections for Task prompts. Changes to SKILL.md propagate to both paths automatically. The risk is in the extraction logic (Path B must know which SKILL.md sections map to which steps), not in duplicate instruction maintenance.

**Residual risk**: If SKILL.md sections are reorganized (headings renamed, sections moved), the Path B section extraction logic breaks silently. Mitigation: verification tests (Section 8) validate both paths against the same test cases.

#### R2: Testing Burden

**Risk**: Verification must cover both paths independently plus the fallover mechanism. This approximately doubles the adversarial pipeline test surface.

**Severity**: Medium.

**Mitigation**: The return-contract schema is the test oracle. Both paths are tested against identical input-output expectations. If Path A and Path B produce `return-contract.yaml` files that satisfy the same schema validation and have `status: success`, both pass. The test surface increase is additive (test Path A, test Path B, test fallover) but not multiplicative.

**Test economy**: The routing decision tree itself is a simple Bash check (binary presence + probe execution) and can be tested with 3-4 cases. The expensive tests are the pipeline tests, which already exist for the current fallback protocol.

#### R3: Behavioral Drift Between Paths

**Risk**: Path A (headless) and Path B (Task agents) may produce materially different quality outputs. Over time, users may discover that `invocation_method: headless` correlates with higher quality and begin depending on this field for routing decisions, undermining the abstraction boundary.

**Severity**: Medium-High.

**Mitigation**:
1. The `invocation_method` field documentation explicitly states it is INFORMATIONAL and must not be used for consumer routing.
2. The enhanced Path B (full 5-step with real convergence) narrows the quality gap from ~70% to ~85-90% fidelity relative to Path A.
3. Quality differences should manifest as different `convergence_score` values, which IS the correct field for quality-based routing (and is already used by step 3e).

**Residual risk**: Anthropic's models may behave differently when running inside `claude -p` versus as Task sub-agents. The system prompt injection mechanism for `claude -p` (via `--append-system-prompt`) may have different effectiveness than inline Task prompts. This is an empirical risk that can only be assessed through testing.

#### R4: claude -p Reliability (GitHub #1048)

**Risk**: Per GitHub issue #1048, `claude -p` with custom commands is unreliable. Claude may ignore behavioral instructions passed via `--append-system-prompt`.

**Severity**: High for Path A alone, Low for the dual-path architecture.

**Mitigation**: This is precisely why Path B exists as a first-class citizen, not a "fallback." If `claude -p` ignores the adversarial pipeline instructions and produces garbage output, the mid-pipeline fallover mechanism detects this (missing or malformed `return-contract.yaml`) and switches to Path B. The dual-path architecture converts this from a pipeline failure to a performance degradation (slower execution via Task agents).

#### R5: Mid-Pipeline Fallover Complexity

**Risk**: Resuming from a partially-completed headless session requires correctly inventorying which artifacts exist and mapping them to pipeline steps. Incorrect inventory leads to either re-doing completed work (waste) or skipping incomplete work (quality loss).

**Severity**: Medium.

**Mitigation**: The artifact inventory is deterministic: each step produces a known output file. The mapping is:
- `variant-*.md` = Step 0/generation complete
- `diff-analysis.md` = Step 1 complete
- `debate-transcript.md` = Step 2 complete
- `base-selection.md` = Step 3 complete
- `refactor-plan.md` = Step 4 complete
- `merge-log.md` + `merged-output.md` = Step 5 complete

If an artifact exists but is malformed, the fallover logic treats it as absent and re-executes from that step. Conservative but safe.

#### R6: Token Cost of Dual-Path

**Risk**: The routing decision tree adds token overhead (Bash calls for binary check and probe execution). The system prompt injection for Path A includes the entire SKILL.md (~1747 lines) which is substantial.

**Severity**: Low.

**Mitigation**: Routing decision overhead is ~200-500 tokens (3 Bash calls). This is negligible compared to the pipeline itself (~10K-50K tokens). The SKILL.md injection for Path A is expensive but is equivalent to what a native Skill tool invocation would need to process anyway.

---

### 8. Verification Plan

#### V1: Path A Independent Test

```yaml
test_path_a:
  name: "Headless invocation end-to-end"
  precondition: "claude binary available, probe succeeds"
  input: |
    Two minimal variant files (100-word markdown documents with
    deliberate structural and content differences)
  invocation: "--invocation-mode headless --depth standard"
  assertions:
    - "claude -p command constructed correctly (verify Bash command string)"
    - "return-contract.yaml exists in output directory"
    - "return-contract.yaml has all 9+1 fields"
    - "invocation_method == 'headless'"
    - "convergence_score is a float between 0.0 and 1.0 (not 0.5 sentinel)"
    - "merged-output.md exists and is non-empty"
    - "adversarial/ directory contains: diff-analysis.md, debate-transcript.md,
       base-selection.md, refactor-plan.md, merge-log.md"
  timeout: "15 minutes"
```

#### V2: Path B Independent Test

```yaml
test_path_b:
  name: "Task-agent pipeline end-to-end"
  precondition: "Task agent dispatch functional"
  input: "Same two minimal variant files as V1"
  invocation: "--invocation-mode inline --depth standard"
  assertions:
    - "No claude -p command executed (verify no Bash calls with 'claude -p')"
    - "return-contract.yaml exists in output directory"
    - "return-contract.yaml has all 9+1 fields"
    - "invocation_method == 'task_agent'"
    - "convergence_score is a float between 0.0 and 1.0 (not 0.5 sentinel)"
    - "merged-output.md exists and is non-empty"
    - "adversarial/ directory contains all 5 step artifacts"
    - "debate-transcript.md contains Round 1 + Round 2 sections (--depth standard)"
    - "base-selection.md contains quantitative AND qualitative scoring sections"
  timeout: "20 minutes"
```

#### V3: Routing Logic Test

```yaml
test_routing:
  name: "Routing decision tree correctness"
  cases:
    case_1:
      condition: "claude binary absent"
      expected: "Path B selected"
    case_2:
      condition: "claude binary present, probe fails"
      expected: "Path B selected"
    case_3:
      condition: "claude binary present, probe succeeds, --depth quick"
      expected: "Path B selected (quick depth routes to inline)"
    case_4:
      condition: "claude binary present, probe succeeds, --depth standard"
      expected: "Path A selected"
    case_5:
      condition: "claude binary present, probe succeeds, --depth deep"
      expected: "Path A selected with extended budget"
    case_6:
      condition: "--invocation-mode headless, claude binary absent"
      expected: "Abort with error (user forced unavailable path)"
    case_7:
      condition: "--invocation-mode inline, claude binary present"
      expected: "Path B selected (user override honored)"
    case_8:
      condition: "--invocation-mode auto (default), both available"
      expected: "Follows depth-based routing (cases 3-5)"
  method: "Structured test with mocked binary checks"
```

#### V4: Mid-Pipeline Fallover Test

```yaml
test_fallover:
  name: "Headless failure triggers Task-agent continuation"
  setup: |
    Simulate headless failure after Step 1 by:
    1. Running Path A with --max-budget-usd 0.05 (extremely low budget)
    2. Budget exhaustion should kill session after diff analysis but before debate
    OR:
    1. Pre-populate adversarial/ with diff-analysis.md from a previous run
    2. Run with a deliberately broken claude -p command
  assertions:
    - "Fallover warning emitted"
    - "Path B resumes from correct step (F3 if diff-analysis.md exists)"
    - "return-contract.yaml produced with invocation_method == 'headless+task_agent'"
    - "Artifacts from headless (diff-analysis.md) preserved, not overwritten"
    - "Artifacts from Task-agent path (debate-transcript.md onward) present"
  timeout: "25 minutes"
```

#### V5: Output Quality Comparison

```yaml
test_quality_comparison:
  name: "Path A vs Path B output quality parity"
  method: |
    Run both paths on identical input (same 2 variant files, --depth standard).
    Compare:
    1. Schema compliance: both return-contract.yaml files valid
    2. Convergence score: both compute real (non-sentinel) scores
    3. Artifact completeness: both produce all 5 step artifacts
    4. Structural quality: both merged-output.md files have valid heading hierarchy
  NOT_compared: |
    Content quality of merged output (subjective, varies by model behavior).
    This test validates structural equivalence, not semantic equivalence.
  acceptance: |
    Both paths produce schema-compliant return contracts with real convergence
    scores and complete artifact sets. Convergence scores need not be identical
    but must both be in [0.0, 1.0] range and non-sentinel.
```

#### V6: Return Contract Schema Consistency

```yaml
test_schema_consistency:
  name: "Both paths produce identical schema"
  method: |
    Extract field names from return-contract.yaml produced by V1 (Path A)
    and V2 (Path B). Diff field sets.
  assertions:
    - "Identical field names in both contracts"
    - "Identical field types (string, float, enum, integer)"
    - "invocation_method field present in both with correct value"
    - "No extra fields in either contract"
```

---

### Appendix A: Comparison with Approaches 1 and 2

| Dimension | Approach 1 (Current Spec) | Approach 2 (claude -p Primary) | Approach 3 (Hybrid Dual-Path) |
|-----------|---------------------------|-------------------------------|-------------------------------|
| Invocation model | Skill tool primary, 3-step fallback | claude -p primary, enhanced fallback | Runtime routing between two first-class paths |
| Environment portability | Depends on Skill tool (unavailable) | Depends on claude binary | Works everywhere (Path B guaranteed) |
| Mid-pipeline recovery | None | Fallover to Task agents | Full artifact-aware fallover |
| Convergence tracking | 0.5 sentinel in fallback | Real in claude -p, enhanced in fallback | Real in both paths |
| Quality tiering | None (depth controls rounds only) | Depth controls budget | Depth controls path selection + budget |
| Future Skill tool | Requires sprint rewrite | Slots in as third path | Slots in as third path |
| Maintenance burden | Low (one path) | Medium (two paths, primary/fallback) | Medium-High (two peer paths + router) |
| Sprint complexity | Low | Medium | High |
| Fidelity (claude -p available) | N/A (Skill tool unavailable) | ~95% | ~95% |
| Fidelity (claude -p unavailable) | ~70% (3-step fallback) | ~85-90% (enhanced fallback) | ~85-90% (enhanced Path B) |

### Appendix B: New Flag Summary

| Flag | Added to | Values | Default | Purpose |
|------|----------|--------|---------|---------|
| `--invocation-mode` | sc:roadmap SKILL.md Section 3 | `headless`, `inline`, `auto` | `auto` | Override runtime routing decision |

### Appendix C: New Return Contract Field

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `invocation_method` | enum | `headless`, `task_agent`, `headless+task_agent`, `skill` | Observability: records which path produced the contract |

---

*Proposal document for SuperClaude Framework sc:roadmap adversarial pipeline remediation sprint.*
*Approach 3 of 3. To be evaluated alongside Approaches 1 (current spec) and 2 (claude -p primary).*
