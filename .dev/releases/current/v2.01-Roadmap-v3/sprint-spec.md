# Sprint Specification: sc:roadmap Adversarial Pipeline Remediation

**T04 Optimizations Applied**: 5 adopted-with-modifications (Opt 1: task merge [Tasks 1.3+1.4+2.2 → Task 1.3], Opt 2: amendment fold [T02 G1-G11 integrated into parent ACs], Opt 3: fallback simplification [F1-F5 → F1, F2/3, F4/5], Opt 4: conditional deferral [G2 validation gated on Task 0.0], Opt 5: test embedding [Tests 1 and 4 embedded in task ACs]). See T04-synthesis.md for details. Net savings: 3.95 hrs (26.3% of estimated 15-hour sprint).

## Sprint Goal

Restore full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` by fixing the invocation wiring gap, rewriting ambiguous specification language into executable tool-call instructions, and establishing a file-based return contract transport mechanism.

## Implementer's Quick Reference

**4 files to edit, 1 post-edit step:**

| File | Changes |
|------|---------|
| `src/superclaude/commands/roadmap.md` | Add `Skill` to `allowed-tools` line |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | (1) Add `Skill` to `allowed-tools`, (2) Add execution vocabulary before Wave 0, (3) Rewrite Wave 2 step 3 as sub-steps 3a-3f with Skill tool call + fallback + return contract routing, (4) Rewrite Wave 1A step 2 with same Skill tool pattern |
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Add "Return Contract (MANDATORY)" section as final pipeline step with 9 fields |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | (1) Convert standalone pseudo-CLI syntax to Skill tool call format, (2) Add "Return Contract Consumption" section with status routing and missing-file guard |

**Post-edit**: `make sync-dev && make verify-sync`

**Critical coordination**: Tasks 1.3, 1.4, and 2.2 have been merged into a single Task 1.3 (per T04 Optimization 1). The merged task covers Skill invocation, fallback protocol, and atomic sub-step decomposition as one coherent rewrite of Wave 2 step 3.

## Problem Ranking

| Rank | Root Cause | Likelihood | Impact | Problem Score |
|------|-----------|------------|--------|---------------|
| 1 | RC1: Invocation Wiring Gap (Skill tool absent from allowed-tools) | 0.90 | 0.90 | 0.900 |
| 2 | RC5: Claude Behavioral Interpretation (rational fallback to ~20% pipeline) | 0.85 | 0.70 | 0.790 |
| 3 | RC2: Specification-Execution Gap (undefined "Invoke" verb, compressed steps) | 0.75 | 0.80 | 0.770 |
| 4 | RC4: Return Contract Data Flow (no transport mechanism for 6 contract fields) | 0.75 | 0.75 | 0.750 |
| 5 | RC3: Agent Dispatch Mechanism (no binding between sc:adversarial and debate-orchestrator) | 0.70 | 0.75 | 0.720 |

**Formula**: `problem_score = (likelihood * 0.6) + (impact * 0.4)`

## Solution Ranking

| Rank | Solution | Fix Likelihood | Feasibility | Low Blast Radius | Solution Score |
|------|----------|---------------|-------------|------------------|---------------|
| 1 | S04: Return Contract (file-based YAML transport) | 0.774 | 0.83 | 0.85 | 0.806 |
| 2 | S02: Spec-Execution Gap (atomic sub-steps, verb glossary) | 0.749 | 0.82 | 0.80 | 0.781 |
| 3 | S01: Invocation Wiring (Skill in allowed-tools + fallback) | 0.760 | 0.75 | 0.85 | 0.775 |
| 4 | S03: Agent Dispatch (bootstrap convention + frontmatter) | 0.700 | 0.73 | 0.83 | 0.735 |
| 5 | S05: Claude Behavior (probe-and-branch + quality gate) | 0.716 | 0.70 | 0.82 | 0.732 |

**Formula**: `solution_score = (fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)`

## Combined Ranking (Top 3)

| Rank | Problem | Solution | Problem Score | Solution Score | Combined |
|------|---------|----------|--------------|----------------|----------|
| 1 | RC1: Invocation Wiring Gap | S01: Skill tool + fallback protocol | 0.900 | 0.775 | 0.838 |
| 2 | RC4: Return Contract Data Flow | S04: File-based return-contract.yaml | 0.750 | 0.806 | 0.778 |
| 3 | RC2: Specification-Execution Gap | S02: Atomic sub-steps + verb glossary | 0.770 | 0.781 | 0.776 |

**Formula**: `combined = (problem_score * 0.5) + (solution_score * 0.5)`

**Selection rationale**: RC1+S01 is the clear top priority -- it is both the highest-severity problem and the prerequisite for all other fixes. RC4+S04 and RC2+S02 are within 0.002 of each other; RC4+S04 edges ahead on solution score strength (highest feasibility in the set). All three are required for the invocation chain to function end-to-end.

**Excluded pairs**: RC5+S05 (0.761) and RC3+S03 (0.728) are deferred. RC5's fallback protocol is partially absorbed by S02's fallback in Wave 2 step 3d. RC3's agent dispatch is a latent defect that only surfaces after the top 3 fixes are applied. Both are candidates for a follow-up sprint.

---

## Task 0.0: Skill Tool Probe (Pre-Implementation Gate)

**Goal**: Empirically determine whether the Skill tool can be called cross-skill and whether Task agents can use it.

**Method**: Dispatch a single Task agent with this prompt: "Use the Skill tool with `skill: 'sc:adversarial'`. Report the exact result: success, error message, or tool not available."

Additionally test from the main agent context: Can the main agent call the Skill tool to invoke sc:adversarial while sc:roadmap is the currently running skill?

**Decision gate**:
- If **success**: Primary path is viable. Proceed with Epic 1 as specified.
- If **error "skill already running"**: Cross-skill invocation blocked. Promote the fallback protocol (Task 1.4) to the ONLY invocation mechanism. Remove primary-path framing.
- If **error "tool not available"**: Skill tool not accessible to Task agents. Test direct invocation from main agent. If main agent succeeds, rewrite Task 1.3 for direct invocation (no Task intermediary). If both fail, same as "already running."
- If **error "skill not found"**: sc:adversarial not installed. Fix installation, re-probe.

**Also determine**: Does "Do not invoke a skill that is already running" apply to (a) the exact same skill name, (b) any skill while another is active, or (c) the same skill instance?

**Acceptance Criteria**: Decision gate result documented. Sprint plan updated if primary path non-viable.

**T04 Opt 4 — Conditional fallback validation deferral**: Based on this gate's result, apply the following to the fallback validation scope:
- If **primary path viable** (Skill tool success): Full fallback validation (Verification Test 7 / G2) is deferred to a follow-up sprint. Replace with a lightweight smoke test: run the fallback protocol on a minimal single-input, verify only that `return-contract.yaml` is written with a valid schema (~30 minutes). This replaces the full F1-F5 validation (1-2 hours).
- If **primary path blocked**: Full G2 fallback validation (Verification Test 7) becomes **mandatory**, not deferred. The fallback IS the primary invocation mechanism and must be fully validated before sprint completion.

**Time cost**: <15 minutes. **Blocks**: All subsequent tasks.

---

## Fallback-Only Sprint Variant

**Trigger**: Task 0.0 decision gate returns "primary path blocked" (Skill tool cannot invoke a second skill while one is running, or Skill tool not accessible to Task agents and main agent also fails).

**Task modifications when fallback is the ONLY invocation mechanism**:

| Task | Modification |
|------|-------------|
| 1.1 | Keep — `Skill` in allowed-tools is still needed for future enablement |
| 1.2 | Keep — same rationale |
| 1.3 | **Remove** — primary Skill invocation path is non-functional |
| 1.4 | **Promote to primary** — fallback protocol becomes the only invocation mechanism; remove "fallback" framing, rename to "Inline Adversarial Execution" |
| 2.1 | Keep — glossary still applies to fallback verbs |
| 2.2 | **Simplify** — sub-steps 3a-3c remain; 3d becomes the inline execution (no Skill tool call); 3e-3f remain |
| 2.3 | **Simplify** — Wave 1A step 2 uses inline execution, no Skill tool call |
| 2.4 | Keep — pseudo-CLI conversion still needed |
| 3.1 | Keep — return contract still needed (fallback writes it too) |
| 3.2 | **Adjust** — missing-file guard remains; `fallback_mode` will always be `true` |
| 3.3, 3.4 | Keep |

**Acceptance Criteria**: Sprint plan updated within 30 minutes of Task 0.0 decision. All "Remove" and "Simplify" modifications applied before implementation begins.

---

## Task 0.1: Prerequisite Validation (Pre-Implementation Gate)

**Goal**: Confirm that all external dependencies required by this sprint are present and correctly configured before any file edits begin.

**Method**: Run the following checks sequentially. Each check is a hard gate — if it fails, resolve before proceeding.

1. **sc:adversarial installed**: Verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists and is readable.
2. **sc:roadmap installed**: Verify `src/superclaude/skills/sc-roadmap/SKILL.md` exists and is readable.
3. **adversarial-integration.md present**: Verify `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` exists.
4. **make sync-dev available**: Run `make sync-dev --dry-run` (or check Makefile for target). If unavailable, identify the manual sync steps.
5. **make verify-sync available**: Run `make verify-sync --dry-run`. If unavailable, identify what it checks.
6. **Task 0.0 result documented**: Confirm the Task 0.0 decision gate result has been recorded and the sprint plan has been updated if primary path is non-viable.

**Decision gate**:
- If all 6 checks pass: proceed with Epic 1.
- If checks 1-3 fail: fix installation, re-run Task 0.1.
- If checks 4-5 fail: document manual sync steps as a substitute for the post-edit step.
- If check 6 fails: complete Task 0.0 before proceeding.

**Acceptance Criteria**: All 6 checks documented with pass/fail result. No check left unanswered.

**Time cost**: <10 minutes. **Blocks**: Epic 1.

---

## Epic 1: Invocation Wiring Restoration (RC1 + S01) -- Highest Priority

**Goal**: Enable skill-to-skill invocation by adding the Skill tool to allowed-tools and establishing a Task-agent-based delegation chain with a structured fallback.

**Dependency**: Task 0.0 must confirm primary path viability (or sprint must be adapted per decision gate).

### Tasks

| # | Task | File | Change | Acceptance Criteria |
|---|------|------|--------|---------------------|
| 1.1 | Add `Skill` to allowed-tools in roadmap command | `src/superclaude/commands/roadmap.md` | In the frontmatter `allowed-tools` line, append `Skill` to the tool list | `Skill` appears in allowed-tools; existing tools unchanged; `make verify-sync` passes after sync; **[embeds Verification Test 1]**: `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS" || echo "FAIL"` returns PASS |
| 1.2 | Add `Skill` to allowed-tools in sc-roadmap SKILL.md | `src/superclaude/skills/sc-roadmap/SKILL.md` | In the frontmatter `allowed-tools` line, append `Skill` to the tool list | `Skill` appears in allowed-tools; existing tools unchanged; **[embeds Verification Test 1]**: `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS" || echo "FAIL"` returns PASS |
| 1.3 | Rewrite Wave 2 step 3: Skill invocation + fallback + atomic sub-steps (merged from 1.3+1.4+2.2 per T04 Opt 1; RC1+RC2) | `src/superclaude/skills/sc-roadmap/SKILL.md` | **Merge note**: This task merges original Tasks 1.3 (Skill invocation), 1.4 (fallback protocol), and 2.2 (atomic sub-steps). All three modify Wave 2 step 3 — implementing as a single atomic edit eliminates coordination risk (R5). Root causes addressed: RC1 (invocation wiring) and RC2 (specification-execution gap). **[From 1.3] Skill invocation**: Replace the single compressed "Invoke sc:adversarial" instruction. Option A (preferred if Task 0.0 confirms primary path viable): Direct Skill tool call from main agent — the main sc:roadmap agent calls the Skill tool directly with `skill: "sc:adversarial"`, `args: "..."` — no Task agent intermediary. Option B (Task-agent-mediated): Task agent prompt naming the Skill tool explicitly with `skill: "sc:adversarial"` syntax, arguments: `--agents`, `--compare`, `--depth`, `--output-dir`, expected output: `return-contract.yaml` in output directory. **[From 2.2] Atomic sub-steps 3a-3f**: (3a) Parse `--agents` list into individual agent specs, (3b) Expand agents into variant generation parameters, (3c) If agents list length >= 3, add debate-orchestrator to coordination role — [T02-G4: specify one concrete tool-call action], (3d) Use Skill tool to invoke sc:adversarial with specified arguments OR execute fallback, (3e) Consume return-contract.yaml: route on `status` field (success -> proceed, partial -> warn and proceed if convergence >= 0.6, failed -> abort); step 3e includes canonical schema comment and YAML parse error handling as `status: failed, failure_stage: transport`, (3f) If adversarial succeeded/partial, skip template-based generation and use merged output. **[From 1.4] Fallback protocol**: | `src/superclaude/skills/sc-roadmap/SKILL.md` | In Wave 2 step 3, add sub-step 3d: "If the Skill tool returns any error (including: tool not in allowed-tools, skill not found, or skill already running), execute fallback." Emit WARNING to user before fallback execution. Fallback state machine (5 steps, sequential, hard-stop on any failure): **F1 Variant Generation** — dispatch Task agents per `--agents` spec, each generates a roadmap variant from the spec. Agent prompt template: "You are a {persona} agent. Read the spec at {spec_file_path} and generate a complete roadmap variant in markdown. Write your output to {output_path}." Input data: spec file path (from sc:roadmap `--specs` or current spec context) + parsed agent specs (model, persona, instruction) from the `--agents` flag. Output artifact: `<output-dir>/adversarial/variant-N-<model>-<persona>.md` (one file per agent, N = 1-based index). Pass criterion: file exists and is non-empty at expected path. Failure: abort, write `return-contract.yaml` with `status: failed, failure_stage: variant_generation`. **F2/3 Diff Analysis + Single-Round Debate** — dispatch single Task agent to compare all variants AND conduct one round of debate in a single pass (merged from original F2 + F3 per T04 Opt 3). Agent prompt preamble: "You are performing Steps 2 and 3 of the sc:adversarial pipeline in fallback mode. Your output MUST follow the diff-analysis format defined in sc:adversarial SKILL.md Step 2 AND the debate transcript format defined in sc:adversarial SKILL.md Step 3 (single round). Output both labeled sections in one document." Agent prompt template: "You are an analytical and debate-orchestrator agent. Read all variant files in {variants_glob}. First, produce a structured diff analysis covering structural differences, content differences, contradictions, and unique contributions. Then, for each variant, write one advocate statement presenting strengths and critiquing others (steelman required). After all statements, produce a per-point scoring matrix. Write the full output with both labeled sections (## Diff Analysis and ## Debate Transcript) to {output_path}." Input data: all variant files from F1 (glob: `<output-dir>/adversarial/variant-*.md`). Output artifact: `<output-dir>/adversarial/diff-analysis.md` (contains both ## Diff Analysis and ## Debate Transcript labeled sections). Pass criterion: file exists and contains all four diff-analysis sections (Structural Differences, Content Differences, Contradictions, Unique Contributions) AND advocate statements for each variant plus a scoring matrix. Failure: abort, `failure_stage: comparative_analysis:diff_or_debate_failed`. **NOTE**: This simplified fallback is not a substitute for the full adversarial pipeline. If future sc:adversarial pipeline adds steps, decompose the merged fallback steps accordingly. **F4/5 Base Selection + Merge + Contract** — dispatch single Task agent to score variants, select base, merge best elements, and write return contract in a single pass (merged from original F4 + F5 per T04 Opt 3). Agent prompt template: "You are a scoring, selection, and merge executor agent. Read all variants at {variants_glob} and the analysis at {diff_analysis_path}. First, score each variant on: (1) requirement coverage, (2) internal consistency, (3) specificity, (4) debate points won from scoring matrix. Select the highest-scoring variant as the base. Write your scoring breakdown and selection (## Base Selection labeled section). Then, incorporate the strongest unique elements from non-base variants into the base. Write the merged result (## Merged Output labeled section). Finally, write return-contract.yaml to {contract_path} with status: partial, fallback_mode: true, convergence_score: 0.5 (fixed sentinel — estimated, not measured; single-round debate cannot produce meaningful convergence), and all 9 required fields. Write all three outputs to {output_path}." Input data: all variant files from F1 + diff-analysis.md from F2/3. Output artifacts: `<output-dir>/adversarial/base-selection.md` (contains ## Base Selection and ## Merged Output labeled sections) + `<output-dir>/adversarial/merged-output.md` (extracted from ## Merged Output section for consumer compatibility) + `<output-dir>/adversarial/return-contract.yaml` with `status: partial, fallback_mode: true`. Pass criterion: base-selection.md exists and identifies exactly one selected base variant with scoring evidence; merged-output.md exists and is non-empty; return-contract.yaml exists with valid schema. Failure: abort, `failure_stage: base_selection:merge_or_contract_failed`. Return-contract.yaml path must be `<output-dir>/adversarial/return-contract.yaml` (must match the path checked in step 3e). **Minimum fallback quality threshold**: A successful fallback execution (F1-F5 all pass) MUST produce at minimum: 2 roadmap variants (F1), 1 diff analysis document (F2), 1 debate transcript with scoring (F3), 1 base selection with rationale (F4), and 1 merged output (F5). If any artifact is empty or trivially short (<100 words for analysis artifacts), treat as step failure and abort with appropriate `failure_stage`. | Fallback covers all three Skill tool error types; 3 fallback invocations (F1, F2/3, F4/5) each have defined input, output, and failure action (F2+F3 merged into F2/3, F4+F5 merged into F4/5 per T04 Opt 3); F2/3 output contains labeled sections (## Diff Analysis, ## Debate Transcript) for diagnostic decomposition; F4/5 output contains labeled sections (## Base Selection, ## Merged Output); compound failure_stage values used (F2/3: comparative_analysis:diff_or_debate_failed; F4/5: base_selection:merge_or_contract_failed); WARNING emission is instructed; each step writes `return-contract.yaml` on failure with appropriate `failure_stage`; fallback produces `fallback_mode: true` on success; [T02-G5: convergence_score in fallback-produced return-contract.yaml is set to fixed sentinel 0.5 with YAML comment "# estimated, not measured — fallback does not track convergence"]; [T02-G7: F1-F5 fallback step descriptions use glossary-consistent verbs (Dispatch agent for Task tool, Write artifact for Write tool) — verify all fallback step verbs match the glossary]; [T02-G8: fallback minimum quality threshold: F1 must produce ≥2 variant files; F2 must produce a non-empty diff-analysis.md; F3 must produce a debate-transcript.md with scoring matrix — if threshold not met, abort with status: failed and failure_stage indicating which threshold was not met]; [T02-G9a: F2 Task agent prompt preamble must reference sc:adversarial Step 1 output format (four required sections); F3 Task agent prompt preamble must reference sc:adversarial Step 2 output format (advocate statements + scoring matrix)] |
| ~~1.5~~ | ~~Sync~~ | *Consolidated into post-edit step (see Implementer's Quick Reference)* | `make sync-dev && make verify-sync` after all epics complete | — |

---

## Epic 2: Specification Rewrite with Executable Instructions (RC2 + S02)

**Goal**: Eliminate specification ambiguity by decomposing Wave 2 step 3 into atomic sub-steps with explicit tool-call syntax, adding a verb-to-tool glossary, and converting adversarial-integration.md from pseudo-CLI to tool-call format.

**Dependency**: Epic 1 must be complete (Skill tool must be in allowed-tools for step 3d's primary path to be meaningful).

### Tasks

| # | Task | File | Change | Acceptance Criteria |
|---|------|------|--------|---------------------|
| 2.1 | Add verb-to-tool glossary before Wave 0 | `src/superclaude/skills/sc-roadmap/SKILL.md` | Insert a new "Execution Vocabulary" section before Wave 0 containing a mapping table: "Invoke skill" = Skill tool call, "Dispatch agent" = Task tool call, "Read ref" = Read tool call on refs/ path, "Write artifact" = Write tool call. [T02-G6: Add scope statement: "This glossary covers tool-call verbs used in pipeline orchestration steps (Wave 0-4). It does NOT cover prose descriptions, comments, or documentation references — only actionable step instructions that the executing agent must interpret as tool operations. Domain-specific verbs (Parse, Expand, Consume, Route) are outside the glossary scope."] | Glossary section exists; every verb used in Wave 0-4 is present in the glossary; glossary appears before Wave 0; glossary verbs are also used in fallback protocol steps F1-F5; [T02-G6: scope statement present] |
| 2.3 | Fix Wave 1A step 2 "Invoke" ambiguity | `src/superclaude/skills/sc-roadmap/SKILL.md` | Replace "Invoke sc:adversarial" in Wave 1A step 2 (the `--specs` path) with the same Skill tool call pattern used in step 3d. Add the same fallback protocol. | Wave 1A step 2 uses glossary-consistent verb; fallback is present; matches Wave 2 pattern |
| 2.4 | Rewrite adversarial-integration.md invocation patterns | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Convert all standalone pseudo-CLI invocation syntax (`sc:adversarial --compare <spec-files> --depth <roadmap-depth>`) to Skill tool call specifications with `skill` and `args` fields. Cover both Multi-Spec Consolidation and Multi-Roadmap Generation subsections. **Note**: The Skill tool's `args` parameter IS a CLI-style string. The `--flag` syntax inside `args: "..."` is correct and expected — do NOT remove flag syntax from within args strings. Only convert standalone invocation examples that are not wrapped in Skill tool call format. | All standalone invocation examples are wrapped in Skill tool call format (`skill: "sc:adversarial", args: "..."`); the args string within Skill tool calls MAY contain `--flag` syntax; agent specification parsing examples use consistent format; **[embeds Verification Test 4]**: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns 0 |

---

## Epic 3: Return Contract Transport Mechanism (RC4 + S04)

**Goal**: Establish a file-based return-contract.yaml convention so sc:adversarial can reliably transport structured pipeline results back to sc:roadmap.

**Dependency**: Conceptually independent (can be implemented in parallel with Epic 2), but must be tested after Epic 1 is complete.

**Scope note**: This return contract is specific to the sc:roadmap → sc:adversarial skill pair. The 9-field schema, the `adversarial/` subdirectory path convention, and sc:adversarial-specific fields (`convergence_score`, `base_variant`, `fallback_mode`) are NOT prescriptive for other skill pairs. Other skills implementing skill-to-skill return contracts should design their own schemas based on their specific data needs; they should not copy sc:adversarial's fields as mandatory framework requirements.

### Tasks

| # | Task | File | Change | Acceptance Criteria |
|---|------|------|--------|---------------------|
| 3.1 | Add return contract write instruction to sc:adversarial | `src/superclaude/skills/sc-adversarial/SKILL.md` | Add a "Return Contract (MANDATORY)" section as the final pipeline step. Instruction: "As the absolute final step, write `<output-dir>/adversarial/return-contract.yaml` with the following fields." Define 9 fields: `schema_version: "1.0"`, `status` (success/partial/failed), `convergence_score` (0.0-1.0), `merged_output_path` (path or null), `artifacts_dir` (path), `unresolved_conflicts` (integer or null — NOTE: sc:adversarial SKILL.md line 349 currently types this as `list[string]`; resolve to `integer` during implementation per reflection-final.md IMP-06), `base_variant` (string or null), `failure_stage` (null on success, pipeline step name on failure), `fallback_mode` (boolean, default: false — set to true when pipeline was executed via inline Task agents instead of the full sc:adversarial skill). Use YAML null (`~`) instead of sentinel values (-1, "") for fields not reached during failed runs. Instruction: write even on failure with `status: failed`. **Type note**: `unresolved_conflicts` is typed as `integer` (count of conflicts). The existing sc:adversarial SKILL.md line 349 types it as `list[string]` — resolve to `integer` for simplicity, since neither consumer uses the list contents. **Dead code removal (appended scope)**: In the same editing session, delete the two `subagent_type: "general-purpose"` lines from the `task_dispatch_config` YAML blocks in this file (located at lines 802 and 1411 in the current file). The `subagent_type` field is not a valid Task tool parameter; it is dead metadata. Remove the entire `subagent_type: "general-purpose"` line from each block; do not replace it with any other value. | Section exists as final pipeline step; 9 fields defined; null is used for unreached values (not -1 or ""); write-on-failure instruction is explicit; `fallback_mode` field present; example YAML block is provided; zero `subagent_type` lines remain in the file (confirm via: `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0) |
| 3.2 | Add return contract read instruction to adversarial-integration.md | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Add a "Return Contract Consumption" section. Instruction: "After sc:adversarial completes, read `<output-dir>/adversarial/return-contract.yaml`." Define validation: check schema_version, warn on unknown version. Define status routing: success -> use merged_output_path, partial -> warn user and use merged_output_path if convergence_score >= 0.6, failed -> abort with failure_stage message. Guard: "If return-contract.yaml does not exist, treat as status: failed with failure_stage: 'transport'." **Fallback differentiation**: If `fallback_mode: true`, add explicit warning: "Output produced by degraded fallback (single-round debate, no convergence tracking). Quality is substantially reduced compared to full adversarial pipeline." This is qualitatively different from `fallback_mode: false` + `status: partial` (full pipeline ran but didn't converge). | Read instruction present; schema_version validation present; three-status routing defined; missing-file guard present; convergence threshold specified (0.6); `fallback_mode` routing with differentiated user warning; includes example YAML block showing a successful return contract and a failed return contract for implementer reference |
| 3.3 | Add Tier 1 artifact existence quality gate | `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Append a new "Post-Adversarial Artifact Existence Gate (Tier 1)" section to adversarial-integration.md. This gate runs BEFORE reading return-contract.yaml, providing validation in timeout/context-exhaustion scenarios where the return contract may never be written. The gate checks four artifact existence conditions using path variables defined by Task 1.4's `<output-dir>/adversarial/` convention: (1) **Directory existence**: `<output-dir>/adversarial/` directory exists. If absent: treat as `status: failed`, `failure_stage: "pipeline_not_started"`, abort with error "Adversarial pipeline directory not created — pipeline did not start." (2) **diff-analysis.md existence**: `<output-dir>/adversarial/diff-analysis.md` exists. If absent: treat as `status: failed`, `failure_stage: "diff_analysis"`, abort with error "diff-analysis.md not found — pipeline halted before diff analysis." (3) **merged-output.md existence**: `<output-dir>/adversarial/merged-output.md` exists. If absent: treat as `status: partial`, `convergence_score: 0.0`, warn user "merged-output.md not found — pipeline did not complete merge phase." (4) **return-contract.yaml existence**: `<output-dir>/adversarial/return-contract.yaml` exists. If absent: treat as `status: partial`, `convergence_score: 0.0`, apply missing-file guard from Task 3.2. Gate ordering instruction: "Perform these four checks in sequence before attempting to parse return-contract.yaml contents. If any check fails, apply the specified treatment without proceeding to YAML parsing." Use path variables (not hardcoded literals) to reference all artifact paths, so the gate remains valid if path conventions change. | Tier 1 gate section exists in adversarial-integration.md; four existence checks present in specified order; each check has defined failure treatment; gate is positioned before YAML parsing in the Return Contract Consumption section; path variable references used throughout (not hardcoded literals); gate heading is "Post-Adversarial Artifact Existence Gate (Tier 1)" |
| ~~3.6~~ | ~~Sync~~ | *Consolidated into post-edit step (see Implementer's Quick Reference)* | `make sync-dev && make verify-sync` after all epics complete | — |

---

## Implementation Order

```
Task 0.0 (Skill Tool Probe) ─── decision gate
  |
  +──> Task 0.1 (Prerequisite Validation) ─── blocks Epic 1
  |
  +──(primary path viable)──> Epic 1 (Invocation Wiring)
  |                             |
  |                             +---> Epic 2 (Specification Rewrite) ──> E2E test
  |                             |        (Task 1.3 merges 1.3+1.4+2.2 — Wave 2 step 3
  |                             |         is a single atomic rewrite; per T04 Opt 1)
  |                             |
  |                             +---> Epic 3 (Return Contract) ────────> E2E test
  |
  +──(primary path blocked)──> Adapted sprint: fallback-only invocation
```

**Rationale**:

1. **Epic 1 first**: S01 is the prerequisite for all other fixes. Without the Skill tool in allowed-tools, no skill-to-skill invocation is possible. This unblocks both Epic 2 and Epic 3.

2. **Epic 2 second**: S02 depends on S01 because the specification rewrite references the Skill tool that S01 adds. Task 2.2 has been merged into Task 1.3 (per T04 Opt 1) — the single merged task owns all Wave 2 step 3 changes, eliminating the cross-epic coordination requirement.

3. **Epic 3 can parallel Epic 2**: S04 is conceptually independent (it modifies sc:adversarial SKILL.md and adversarial-integration.md, not the Wave 2 step 3 text). However, it cannot be end-to-end tested until Epic 1 is complete because sc:adversarial must be invocable for the return contract to be written.

4. **Cross-debate ordering alignment**: The debates converged on S01 -> S02 -> S04 -> S05 -> S03. This sprint covers the first three in that sequence.

**Alternative ordering (decision point)**: reflection-final.md IMP-07 proposes: Task 0.1 -> Epic 1 Tasks 1.1-1.2 -> Epic 3 -> Epic 1 Tasks 1.3-1.4 + Epic 2 (unified). Rationale: Epic 3 defines the contract that Epic 2 references; implementing Epic 3 first gives Epic 2 a concrete schema instead of a forward reference. Evaluate at sprint start.

**File conflict avoidance**: Task 3.2 (adds new section to adversarial-integration.md) must complete before Task 2.4 (modifies existing sections in the same file). This prevents parallel-edit conflicts. See reflection-final.md Section 4, "adversarial-integration.md Dual Role."

**Critical coordination point**: Tasks 1.3, 1.4, and 2.2 have been merged into a single Task 1.3 (per T04 Optimization 1). The merged Task 1.3 covers Skill invocation, fallback protocol, and atomic sub-step decomposition as a single coherent rewrite of Wave 2 step 3. There is no longer a coordination risk between separate tasks modifying the same text — all Wave 2 step 3 changes are owned by Task 1.3.

---

## Sprint 0 Process Deliverable: Formal Debt Register Initialization

**Trigger**: Before v2.1 implementation begins (not during this sprint's implementation phase).

**Deliverable**: Create `.dev/releases/debt-register.md` as the persistent technical debt and deferral tracking document for the SuperClaude framework.

**Source**: Use `docs/generated/deferral-confidence-matrix.md` as the primary source. The confidence matrix is functionally an ad-hoc debt register already — it contains 18 scored items with documented rationale, recalibrated likelihood estimates, cross-item dependency findings, and sprint sequencing recommendations. The formalization step is schema normalization and placement, not new analysis.

**Minimum fields per entry**:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (e.g., DEBT-001) |
| `source_item` | Original confidence matrix item number |
| `description` | Brief description of the deferred feature/fix |
| `category` | Architecture / Resilience / Quality / Documentation / Process |
| `deferral_confidence` | Score from confidence matrix (0.0–1.0) |
| `recommended_sprint` | NEXT-SPRINT / BACKLOG / MAINTAIN-DEFERRAL |
| `dependencies` | Other debt items that must be resolved first or in same sprint |
| `last_reviewed` | Sprint name/date when last assessed |
| `notes` | Key recalibration decisions, risk findings, debate conclusions |

**Why before v2.1 starts**: If initialization is deferred until "sometime in v2.1," it will be deferred indefinitely under implementation pressure. The correct time is the gap between sprint completion and next sprint kickoff — a natural pause that makes initialization a bounded 30-minute task rather than a competing priority.

**Effort**: ~30 minutes. Zero blast radius on any functional code.

**Owner**: Sprint retrospective facilitator or whoever writes the v2.1 sprint spec.

---

## Risk Register

| # | Risk | Source | Probability | Impact | Mitigation |
|---|------|--------|-------------|--------|------------|
| R1 | Task agent cannot access the Skill tool (primary invocation path fails) | Debate 01, Unresolved Concern 1 | HIGH (0.40) | HIGH -- primary path non-functional | Fallback protocol (Epic 1, Task 1.4) ensures feature ships regardless. Empirical test before full implementation: dispatch a Task agent with a minimal prompt that uses the Skill tool to load any named skill. |
| R2 | "Skill already running" constraint blocks sc:roadmap from invoking sc:adversarial | Debate 02, Unresolved Concern UC-02-01 | MEDIUM (0.30) | HIGH -- invocation blocked with no fallback | Fallback trigger in step 3d must cover "skill already running" error type explicitly. Implemented in Epic 1, Task 1.4 and Epic 2, Task 2.2. |
| R3 | Step 3e return contract routing fails when return-contract.yaml does not exist (S04 not yet tested) | Debate 02, Unresolved Concern UC-02-02 | MEDIUM (0.25) | MEDIUM -- cannot distinguish crash from failure | Guard condition in step 3e: "If return-contract.yaml not found, treat as status: failed with failure_stage: 'transport'." Implemented in Epic 2, Task 2.2. |
| R4 | Claude does not write return-contract.yaml on failure paths | Debate 04, Unresolved Concern Priority 1 | MEDIUM (0.30) | MEDIUM -- parse error in step 3e | Step 3e routing should attempt YAML parsing and treat parse errors as `status: failed` |
| R5 | Wave 2 step 3 rewrite conflict between Epic 1 and Epic 2 authors | Cross-debate implementation coordination | ~~MEDIUM (0.25)~~ **ELIMINATED** | HIGH -- contradictory instructions in SKILL.md | **T04 Optimization 1 (task merge) eliminates this risk entirely.** Tasks 1.3, 1.4, and 2.2 are merged into a single Task 1.3. There is no longer a multi-author coordination requirement for Wave 2 step 3 — one task, one author, one atomic edit. |
| R6 | Fallback protocol bitrot as sc:adversarial pipeline evolves | Debate 05, Unresolved Concern UC-4 | LOW (0.15) | MEDIUM -- fallback silently stale | Add version comment at top of fallback section: "Fallback mirrors sc:adversarial v{version}. Review on sc:adversarial changes." Log as follow-up maintenance task. |
| R7 | adversarial-integration.md pseudo-CLI syntax remains in unconverted sections | Debate 02, Unresolved Concern UC-02-03 | LOW (0.15) | LOW -- residual ambiguity in ref file | Full audit of adversarial-integration.md for `sc:adversarial --` patterns. Implemented in Epic 2, Task 2.4. |
| R8 | Claude execution timeout — adversarial pipeline may take 10+ minutes; if Skill tool call times out, return contract may not be written | reflection-final.md Section 6, item 1 | MEDIUM (0.25) | MEDIUM -- return contract missing on timeout | Add timeout handling guidance to Task 1.3/2.2 Skill tool call; document expected duration range |
| R9 | Context window exhaustion during sc:adversarial — multiple full-text variants may exhaust context; write-on-failure may not execute | reflection-final.md Section 6, item 2 | LOW (0.20) | HIGH -- silent total failure | Document as known limitation; consider spec size warnings in sc:roadmap |
| R10 | Partial file writes — return-contract.yaml may be malformed YAML if sc:adversarial crashes mid-write | reflection-final.md Section 6, item 3 | LOW (0.15) | MEDIUM -- parse error in step 3e | Step 3e routing should attempt YAML parsing and treat parse errors as `status: failed` |
| R11 | Recursive skill invocation — sc:roadmap -> sc:adversarial -> (another skill) could hit platform depth limits | reflection-final.md Section 6, item 4 | LOW (0.10) | LOW -- theoretical edge case | Document invocation depth limit of 1 (no nested skill calls from sc:adversarial) |
| R12 | Deferred root causes RC3/RC5 surfacing as second-order failures — correct wiring but wrong agent selection within sc:adversarial | reflection-final.md Section 6, item 5 | MEDIUM (0.30) | MEDIUM -- degraded output quality | Flag as post-sprint monitoring item; add to follow-up sprint scope |
| R13 | Concurrency namespacing becomes mandatory if Item 14 (Framework-level Skill Return Protocol) is adopted | Confidence matrix Item 17, dependency linkage finding | CONDITIONAL — LOW now, HIGH if Item 14 adopted | HIGH -- race condition: multiple simultaneous sc:adversarial invocations write to same return-contract.yaml path if output-dir is implicit | Current sprint's caller-controlled `--output-dir` parameter provides implicit namespacing and keeps this risk LOW. If Item 14 (Framework-level Skill Return Protocol) is adopted in a future sprint, the output-dir path becomes framework-managed rather than caller-controlled, eliminating the namespacing mitigation. **Constraint**: Item 17 (concurrency namespacing for parallel sc:adversarial invocations) MUST be resolved in the same sprint as Item 14. These items cannot be sequenced independently once Item 14 is adopted. Flag this dependency in the v2.1 sprint planning session when Item 14 is evaluated. |

---

## Definition of Done

The sprint is complete when ALL of the following are true:

### Code Changes
- [ ] `Skill` is present in `allowed-tools` in both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md`
- [ ] Verb-to-tool glossary exists before Wave 0 in `src/superclaude/skills/sc-roadmap/SKILL.md`
- [ ] Sub-step 3c includes debate-orchestrator bootstrap read instruction (Read tool call on refs/debate-orchestrator.md)
- [ ] Wave 2 step 3 is decomposed into sub-steps 3a-3f with explicit tool-call syntax, fallback protocol, and return contract routing
- [ ] Wave 1A step 2 uses glossary-consistent Skill tool invocation (not bare "Invoke")
- [ ] Zero standalone `sc:adversarial --` pseudo-CLI syntax remains in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` (args strings within Skill tool calls may contain `--flag` syntax)
- [ ] Return contract write instruction exists as final step in `src/superclaude/skills/sc-adversarial/SKILL.md` with 9 fields (including `failure_stage` and `fallback_mode`), YAML null for unreached values, write-on-failure instruction
- [ ] Return contract read instruction and status routing exist in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with missing-file guard, convergence threshold, and `fallback_mode` differentiated warning
- [ ] `base_variant` field present in producer schema; cross-reference comments in both producer and consumer files
- [ ] `unresolved_conflicts` type resolved to `integer` in both producer and consumer
- [ ] Post-Adversarial Artifact Existence Gate (Tier 1) section exists in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with all four existence checks (directory, diff-analysis.md, merged-output.md, return-contract.yaml) in specified order, each with defined failure treatment, positioned before YAML parsing
- [ ] `make verify-sync` passes (`.claude/` mirrors match `src/superclaude/`)

### Quality Gates
- [ ] No existing tests broken (`uv run pytest` passes)
- [ ] All modified files pass linting (`make lint`)
- [ ] Every verb in Wave 0-4 appears in the glossary table
- [ ] Every sub-step in Wave 2 step 3 uses exactly one verb from the glossary
- [ ] Fallback trigger covers three error types: tool not in allowed-tools, skill not found, skill already running
- [ ] Fallback steps F1-F5 use glossary-consistent verbs (each step's action verb appears in the Execution Vocabulary glossary)
- [ ] Zero `subagent_type` lines remain

### Verification (see Verification Plan below)
- [ ] Verification Test 1 passes (Skill tool in allowed-tools confirmation)
- [ ] Verification Test 2 passes (Wave 2 step 3 structural audit)
- [ ] Verification Test 3 passes (return contract schema consistency)
- [ ] Verification Test 3.5 passes (cross-reference field consistency between Wave 2 step 3e and Return Contract schema)
- [ ] Verification Test 4 passes (pseudo-CLI elimination)
- [ ] Verification Test 5 passes (End-to-End Invocation — see below)
- [ ] Verification Test 6 passes (Tier 1 quality gate structure audit — see below)
- [ ] Verification Test 7 passes (fallback protocol validation)

---

## Verification Plan

### Test 1: Skill Tool Availability Confirmation

**Note**: This test is now embedded as a completion criterion in Tasks 1.1 and 1.2 acceptance criteria (per T04 Opt 5). The grep commands below serve as the standalone reference; the embedded versions in each task AC are the authoritative pass gates.

**Purpose**: Confirm the Skill tool is available for skill-to-skill invocation.

**Method**: Static analysis of the modified files.

```bash
# Verify Skill is in allowed-tools for both files
grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS: roadmap.md" || echo "FAIL: roadmap.md"
grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS: SKILL.md" || echo "FAIL: SKILL.md"
```

**Expected**: Both files contain `Skill` in the allowed-tools line.

### Test 2: Wave 2 Step 3 Structural Audit

**Purpose**: Confirm the step 3 rewrite meets the specification: atomic sub-steps, glossary-consistent verbs, fallback protocol, return contract routing.

**Method**: Manual inspection checklist.

1. Count sub-steps in Wave 2 step 3. Expected: 6 (3a through 3f).
2. For each sub-step, verify exactly one verb from the glossary is used.
3. Verify step 3d contains the Skill tool call syntax with `skill: "sc:adversarial"`.
4. Verify step 3d fallback trigger covers three error types.
5. Verify step 3e contains the missing-file guard condition.
6. Verify step 3e contains the convergence threshold (0.6).
7. Verify step 3f contains the skip-template-generation instruction.

### Test 3: Return Contract Schema Consistency (Run immediately after Epic 3 completion)

**Purpose**: Confirm the producer schema (sc:adversarial) and consumer expectations (adversarial-integration.md) are aligned.

**Method**: Extract field names from both files and diff.

```bash
# Extract field names from producer (sc:adversarial SKILL.md, Return Contract section)
# Extract field names from consumer (adversarial-integration.md, Return Contract Consumption section)
# Diff the two lists -- they must match exactly
```

**Expected**: Identical field sets in both files. `base_variant` present in both. `failure_stage` present in both. Cross-reference comments present in both.

### Test 3.5: Cross-Reference Field Consistency

**Purpose**: Validate that the fields referenced in Wave 2 step 3e (consumer) match the fields defined in sc:adversarial's Return Contract section (producer).

**Method**: Manual cross-reference.

1. List all fields referenced in Wave 2 step 3e (status, convergence_score, etc.)
2. List all fields defined in sc:adversarial SKILL.md Return Contract section
3. Confirm: every field referenced by the consumer exists in the producer schema
4. Confirm: the convergence threshold in step 3e (0.6) matches the threshold in adversarial-integration.md status routing (60%)

**Expected**: All consumer-referenced fields exist in the producer schema. Thresholds are consistent.

### Test 4: Pseudo-CLI Elimination

**Note**: This test is now embedded as a completion criterion in Task 2.4 acceptance criteria (per T04 Opt 5). The grep command below serves as the standalone reference; the embedded version in Task 2.4 AC is the authoritative pass gate.

**Purpose**: Confirm no pseudo-CLI invocation syntax remains in adversarial-integration.md.

**Method**: Pattern search.

```bash
grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
```

**Expected**: 0 matches.

### Test 5: End-to-End Invocation (Post-Sprint, Manual)

**Purpose**: Confirm the full invocation chain works: sc:roadmap -> Skill tool -> sc:adversarial -> return-contract.yaml -> sc:roadmap consumption.

**Method**: Run `sc:roadmap --multi-roadmap --agents opus,haiku` on a test project and verify:

1. sc:adversarial is invoked (not approximated with system-architect agents)
2. Adversarial pipeline artifacts are produced (diff-analysis.md, debate transcripts, scoring, merged output)
3. `return-contract.yaml` exists in the output directory with valid schema
4. sc:roadmap reads the return contract and routes on status field
5. Final roadmap output contains adversarial provenance markers

**Note**: This test requires all three epics to be complete and can only be run in a Claude Code session with the Skill tool available. If the Skill tool is not available to Task agents (Risk R1), verify that the fallback protocol activates and produces the expected partial-quality output with `status: partial` and `fallback_mode: true`.

### Test 6: Tier 1 Quality Gate Structure Audit

**Purpose**: Confirm the artifact existence gate is correctly positioned and contains all required checks.

**Method**: Manual inspection checklist against `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`.

1. Locate the "Post-Adversarial Artifact Existence Gate (Tier 1)" section heading.
2. Confirm it appears BEFORE the Return Contract YAML parsing instructions (not after).
3. Confirm check 1 targets `<output-dir>/adversarial/` directory existence with `failure_stage: "pipeline_not_started"`.
4. Confirm check 2 targets `diff-analysis.md` existence with `failure_stage: "diff_analysis"`.
5. Confirm check 3 targets `merged-output.md` existence with `status: partial, convergence_score: 0.0`.
6. Confirm check 4 targets `return-contract.yaml` existence with instruction to apply missing-file guard from Task 3.2.
7. Confirm all path references use variable form (`<output-dir>/adversarial/`) not hardcoded literals.

**Expected**: All 7 checklist items confirmed.

**Note**: This test can be performed without a working pipeline — it is a static structural check on the specification document.

### Test 7: Fallback Protocol Validation

**Purpose**: Confirm the fallback protocol (F1-F5) produces valid output and a well-formed return-contract.yaml.

**Method**: Run the fallback protocol on a test input with Skill tool deliberately unavailable (or simulate error).

1. Provide a minimal spec file and 2 agent specifications as input
2. Execute F1-F5 sequentially
3. Verify each step produces its expected output artifact
4. Verify `return-contract.yaml` is written with `status: partial`, `fallback_mode: true`, and valid schema
5. Verify a failure mid-pipeline (e.g., abort at F3) produces `return-contract.yaml` with `status: failed` and correct `failure_stage`

**Expected**: All 5 fallback steps produce artifacts; return-contract.yaml has valid schema on both success and mid-pipeline failure paths.

---

## Follow-up Sprint Items

The following items were deferred from this sprint:

- **RC5+S05** (Claude behavioral fallback): Problem score 0.761, deferred per selection rationale.
- **RC3+S03** (Agent dispatch convention): Problem score 0.728, latent defect not active cause.
- **G2: Full fallback protocol validation** (T04 Opt 4 conditional deferral): If Task 0.0 returns "primary path viable," the full F1-F5 fallback validation test (Verification Test 7) is deferred to the follow-up sprint. The in-sprint replacement is a lightweight smoke test (single-input run, schema validity check only). See Task 0.0 T04 Opt 4 note.
- **G12: Full S05 quality gate on agent output** (RC5 debate): Requires S05 design work beyond sprint scope.
- **G13: Full S03 agent dispatch convention** (RC3 debate): Correctly deferred; latent defect not active cause.
- **G14: validate_wave2_spec.py DVL script** (RC2 debate): Optional; manual checklist is acceptable substitute.
- **G15: Fallback bitrot active detection** (RC5 debate): Active R6 mitigation; partial fix via DoD check.

---

*Sprint specification generated 2026-02-22. Analyst: claude-opus-4-6 (system-architect persona).*
*Inputs: ranked-root-causes.md, debate-01 through debate-05, CP-P1-END.md, CP-P3-END.md.*
*Top 3 pairs selected by combined problem-solution scoring. Implementation ordered by dependency chain.*
*Deferred to follow-up sprint: RC5+S05 (Claude behavioral fallback), RC3+S03 (agent dispatch convention).*
