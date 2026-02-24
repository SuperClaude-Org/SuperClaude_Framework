# Specification: claude -p Headless Invocation for sc:roadmap Adversarial Pipeline

**Version**: 1.0-draft
**Date**: 2026-02-23
**Status**: DRAFT — Pending expert panel review
**Source**: Merged adversarial approach (base: Approach 2, score: 0.900)
**Convergence**: 1.00 (12/12 debate points resolved)

---

## 0. Document Purpose & Scope

This specification defines the modifications to the sc:roadmap sprint tasklist required to wire `claude -p` headless CLI invocation as the **primary** mechanism for launching sc:adversarial, with an enhanced 5-step Task-agent fallback when headless invocation fails.

### Scope Boundaries

**In scope**:
- Task 0.0 replacement (viability probe)
- Wave 2 step 3d rewrite (headless invocation + enhanced fallback)
- Wave 1A step 2 adaptation (same pattern)
- Return contract schema update (10th field)
- Verb glossary addition
- New reference file (`refs/headless-invocation.md`)
- Phase 3 validation task updates (T03.01, T03.02)
- Glossary updates

**Out of scope**:
- Changes to sc:adversarial SKILL.md itself (separate sprint)
- `--invocation-mode` flag (rejected: YAGNI)
- Depth-based routing (rejected: premature optimization)
- 10-run reliability test (rejected: cost/scope)

### Task ID Mapping

This specification uses sprint tasklist IDs (T01.01-T06.05) as the canonical reference. The following mapping connects the merged approach's informal names to actual task IDs:

| Merged Approach Name | Sprint Task ID | Phase | Description |
|---------------------|---------------|-------|-------------|
| Task 0.0 | T01.01 | 1 | `claude -p` Viability Probe |
| Tasks 1.1-1.2 | T02.01, T02.02 | 2 | `Skill`/`Bash` in allowed-tools |
| Task 1.3 | T02.03 | 2 | Wave 2 step 3d rewrite |
| Task 1.4 | T02.03 (within) | 2 | Fallback designation |
| Task 2.1 | T05.01 | 5 | Verb glossary |
| Task 2.3 | T05.02 | 5 | Wave 1A step 2 |
| Task 2.4 | T05.03 | 5 | adversarial-integration.md conversion |
| Task 3.1 | T04.01 | 4 | Return contract schema |
| Task 3.2 | T04.02 | 4 | Return contract consumption |
| Task 3.3 | T04.03 | 4 | Tier 1 artifact gate |
| (unaddressed) | T03.01 | 3 | Wiring validation: tool availability |
| (unaddressed) | T03.02 | 3 | Wiring validation: structural audit |

---

## 1. Philosophy

`claude -p` is the **primary** invocation mechanism for the sc:adversarial pipeline within sc:roadmap. It provides:

- **Process isolation**: Separate context window, independent token budget
- **Behavioral control**: Full SKILL.md content injected via `--append-system-prompt`
- **Structured output**: JSON result with `session_id`, `cost_usd`, `is_error`, `duration_ms`
- **Cost ceiling**: `--max-budget-usd` hard cap per invocation

The Task-agent fallback is an **enhanced 5-step pipeline** (F1/F2/F3/F4/F5) that activates when `claude -p` fails. It is NOT a peer path. The primary/fallback hierarchy is maintained for architectural clarity and maintenance simplicity.

The **return contract** (`return-contract.yaml`) is the abstraction boundary. Step 3e reads and routes on `status` and `convergence_score`. It does not know or care whether the contract was produced by headless or fallback.

---

## 2. Invocation Design

### 2.1 Command Construction Pattern

| Component | Flag | Content |
|-----------|------|---------|
| Behavioral instructions | `--append-system-prompt` | Raw content of `sc-adversarial/SKILL.md` |
| Task prompt | `-p` (positional) | Mode B invocation with runtime parameters |
| Tool access | `--allowedTools` | `Read,Write,Edit,Bash,Glob,Grep,Task` |
| Cost control | `--max-budget-usd` | Per-invocation spending cap |
| Output format | `--output-format json` | Structured JSON with session_id, usage, cost |
| Permissions | `--dangerously-skip-permissions` | Autonomous execution without interactive prompts |

**Permission flag rationale**: `--dangerously-skip-permissions` is chosen over `--permission-mode bypassPermissions`. Both are valid Claude CLI flags. `--dangerously-skip-permissions` is preferred because: (a) it's a boolean flag requiring no value argument, reducing command template complexity; (b) its name makes the security implication explicit; (c) it's documented as the primary bypass mechanism.

### 2.2 Exact Command Template

```bash
# Environment preparation: unset CLAUDECODE to prevent nested session detection
CLAUDECODE_BACKUP="${CLAUDECODE:-}" && unset CLAUDECODE

# Read SKILL.md content for system prompt injection
ADVERSARIAL_SKILL_CONTENT="$(cat src/superclaude/skills/sc-adversarial/SKILL.md)"

# Compute budget from depth: quick=1.00, standard=2.00, deep=5.00
BUDGET="<computed-from-depth>"

# Compute model from depth: quick/standard=sonnet, deep=opus
MODEL="<computed-from-depth>"

# Construct the invocation
HEADLESS_OUTPUT=$(timeout "${TIMEOUT}" claude -p \
  "Execute the sc:adversarial pipeline in Mode B (generate + compare from source).

   Parameters:
   - Source file: <spec-file-path>
   - Generate type: roadmap
   - Agents: <expanded-agent-specs-comma-separated>
   - Depth: <depth>
   - Output directory: <output-dir>
   - Interactive: false
   - Convergence threshold: 0.80

   MANDATORY REQUIREMENTS:
   1. Execute ALL 5 steps of the adversarial protocol defined in your system instructions.
   2. Create the output directory structure: <output-dir>/adversarial/
   3. Write ALL intermediate artifacts (variant files, diff-analysis.md, debate-transcript.md,
      base-selection.md, refactor-plan.md, merge-log.md, merged output).
   4. As the ABSOLUTE FINAL step, write <output-dir>/adversarial/return-contract.yaml with
      ALL 10 required fields: schema_version (1.0), status, convergence_score,
      merged_output_path, artifacts_dir, unresolved_conflicts, base_variant, failure_stage,
      fallback_mode (false), invocation_method (headless).
   5. If ANY step fails, still write return-contract.yaml with status: failed and
      failure_stage set to the failed step name.
   6. Do NOT prompt for user input. All decisions are auto-resolved.
   7. Use YAML null (~) for fields not reached during failed runs." \
  --append-system-prompt "${ADVERSARIAL_SKILL_CONTENT}" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --dangerously-skip-permissions \
  --output-format json \
  --max-budget-usd "${BUDGET}" \
  --model "${MODEL}" \
  2>/dev/null)

HEADLESS_EXIT=$?

# Restore environment
if [ -n "$CLAUDECODE_BACKUP" ]; then
  export CLAUDECODE="$CLAUDECODE_BACKUP"
fi
```

### 2.3 Parameter Configuration

| Parameter | Quick | Standard | Deep | Rationale |
|-----------|-------|----------|------|-----------|
| `--model` | sonnet | sonnet | opus | Cost-effective for standard; high-quality for deep |
| `--max-budget-usd` | $1.00 | $2.00 | $5.00 | Hard cost ceiling per invocation |
| Timeout | 180s | 300s | 600s | Process kill if exceeded |
| `--allowedTools` | (same) | (same) | (same) | `Read,Write,Edit,Bash,Glob,Grep,Task` |
| `--dangerously-skip-permissions` | present | present | present | Required for autonomous file writes |
| `--output-format json` | present | present | present | Structured output parsing |

### 2.4 Output Capture and Parsing

The primary validation is the **file-based return contract** at `<output-dir>/adversarial/return-contract.yaml`. JSON output provides supplementary metadata.

```bash
# Primary validation: return contract existence
if [ -f "<output-dir>/adversarial/return-contract.yaml" ]; then
  echo "HEADLESS_CONTRACT: found"
else
  echo "HEADLESS_CONTRACT: missing"
fi

# Supplementary: extract cost from JSON output
HEADLESS_COST=$(echo "$HEADLESS_OUTPUT" | grep -o '"cost_usd":[0-9.]*' | cut -d: -f2)
```

### 2.5 CLAUDECODE Environment Variable

Claude Code sets `CLAUDECODE` in active sessions to detect nesting. The variable must be unset before `claude -p` invocation and restored afterward. This is handled within the Bash tool call — only the subprocess environment is affected.

### 2.6 Error Detection Matrix

| Error Condition | Detection Method | Handling |
|-----------------|-----------------|----------|
| `claude` not in PATH | `which claude` non-zero | Abort; trigger fallback |
| Non-zero exit code | `$?` after invocation | Log error; scan for partial artifacts |
| Timeout (exit 124) | Bash `timeout` command | Kill process; scan for partial artifacts |
| Permission denied (126/127) | Exit code | Abort; trigger fallback |
| Malformed JSON output | JSON parse failure | Ignore JSON; rely on file-based contract |
| Budget exceeded | `--max-budget-usd` enforced by CLI | CLI self-terminates; scan partial artifacts |
| Return contract missing | File existence check | Trigger 3-state fallback scan |
| Return contract malformed | YAML parse attempt | Treat as `status: failed, failure_stage: transport` |

---

## 3. Sprint-Spec Modifications

### 3.1 T01.01: `claude -p` Viability Probe (Replaces Task 0.0)

**Replaces**: Current T01.01 (Skill Tool Probe)
**Deliverables affected**: D-0001 (evidence), D-0002 (variant decision)

> **T01.01: `claude -p` Headless Invocation Viability Probe (Pre-Implementation Gate)**
>
> **Goal**: Empirically confirm that `claude -p` can be launched from a Bash tool call and can execute a multi-step pipeline with behavioral adherence to injected SKILL.md instructions.
>
> **Method**: Run 4 test invocations:
>
> 1. **Existence check**: `which claude && claude --version` — confirms CLI in PATH.
> 2. **Basic invocation**: `CLAUDECODE= claude -p "Write the text 'hello' to /tmp/sc-probe-test.txt" --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.05` — confirms basic headless execution with file I/O.
> 3. **System prompt injection**: `CLAUDECODE= claude -p "List the sections defined in your system instructions. Write them to /tmp/sc-probe-sections.txt" --append-system-prompt "# Test Skill\n## Section A\nDo thing A.\n## Section B\nDo thing B." --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.10` — confirms `--append-system-prompt` content is accessible.
> 4. **Behavioral adherence mini-test**: Execute a minimal system-prompt-injected pipeline on tiny fixtures (2 pre-written 100-word variants). Score output against 3-category binary checklist:
>    - **Diff Analysis present?** Output directory contains a diff analysis section/file distinguishing the two variants.
>    - **Multi-step execution?** Output shows evidence of more than a single-pass comparison (round markers, scoring matrix, or base selection).
>    - **Artifacts written to disk?** At least 2 distinct output files exist in the target directory.
>
> **Decision gate**:
> - **All 4 pass**: `claude -p` is viable as primary invocation. Proceed with implementation.
> - **Tests 1-3 pass, test 4 fails**: Headless works mechanically but doesn't follow behavioral instructions. Augment the system prompt with stronger anchoring (explicit "YOU MUST" instructions for each step). Re-run test 4 once. If still failing, route to fallback-only sprint variant.
> - **Test 1 fails**: CLI not installed. Route to fallback-only.
> - **Test 2 or 3 fails**: Headless mode broken or sandboxed. Investigate; if persistent, route to fallback-only.
>
> **Informational output** (not gated): Log SKILL.md file size in characters and estimated tokens (~4 chars/token). Log test 4 cost from JSON output.
>
> **Time cost**: ~20 minutes. **API cost**: ~$4. **Blocks**: All subsequent tasks.

**Acceptance Criteria**:
- All 4 tests executed with documented results
- Decision gate applied correctly
- Sprint variant decision recorded in D-0002
- Evidence of each test result in D-0001 with exact command output

### 3.2 T02.01, T02.02: Allowed-Tools Verification

**Retained but deprioritized**. `Skill` remains in allowed-tools for forward compatibility. `Bash` is now the critical tool for `claude -p` invocation and is already present.

**Addition to both ACs**: "Verify `Bash` is present in allowed-tools (required for `claude -p` invocation)."

### 3.3 T02.03: Wave 2 Step 3d — Complete Rewrite

**Deliverables affected**: D-0006 (step 3 sub-steps), D-0007 (fallback protocol), D-0008 (return contract routing)

This is the core specification change. The full rewrite of step 3d is defined below.

> **3d [Launch headless adversarial session]**: Use the `claude -p` headless CLI to invoke sc:adversarial in a separate session with full pipeline execution. Read `refs/headless-invocation.md` for the invocation template and parameter mapping.
>
> **3d-i [Construct invocation command]**: Build the headless invocation command using the Mode B template from `refs/headless-invocation.md`. Substitute runtime parameters: `<spec-file-path>`, `<expanded-agent-specs>`, `<depth>`, `<output-dir>`, `<budget>`, `<model>`, `<timeout>`. Agent specs must be in expanded form (model-only agents already filled with primary persona from step 3b).
>
> **3d-ii [Execute headless session]**: Use the `Bash` tool to execute the constructed command:
>
> ```bash
> CLAUDECODE_BACKUP="${CLAUDECODE:-}" && unset CLAUDECODE
> SKILL_CONTENT=$(cat src/superclaude/skills/sc-adversarial/SKILL.md)
>
> HEADLESS_OUTPUT=$(timeout ${TIMEOUT} claude -p "${PROMPT}" \
>   --append-system-prompt "${SKILL_CONTENT}" \
>   --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
>   --dangerously-skip-permissions \
>   --output-format json \
>   --max-budget-usd "${BUDGET}" \
>   --model "${MODEL}" \
>   2>/dev/null)
> HEADLESS_EXIT=$?
>
> if [ -n "$CLAUDECODE_BACKUP" ]; then
>   export CLAUDECODE="$CLAUDECODE_BACKUP"
> fi
> ```
>
> **Timeout**: quick=180s, standard=300s, deep=600s.
>
> **3d-iii [Validate headless output]**: Perform validation in order:
>
> 1. **Exit code check**: If `HEADLESS_EXIT` is non-zero:
>    - Exit 124 = timeout. Emit: `"claude -p timed out after <N> seconds."`. Proceed to artifact scan.
>    - Exit 126/127 = command not found or permission denied. Proceed to fallback (3d-iv).
>    - Other non-zero = general failure. Proceed to artifact scan.
>
> 2. **JSON output parse** (informational): If `HEADLESS_OUTPUT` is non-empty, extract `is_error`, `cost_usd`, `duration_ms`. Log: `"Headless session: cost=$<cost>, duration=<duration>ms, error=<is_error>"`.
>
> 3. **Return contract existence**: Check if `<output-dir>/adversarial/return-contract.yaml` exists.
>    - If exists: proceed to step 3e (consume return contract).
>    - If missing: proceed to artifact scan (3d-iv).
>
> 4. **Cost guard**: If `cost_usd` exceeds `BUDGET * 1.5`, emit warning (informational, not abort).
>
> **3d-iv [Fallback: enhanced Task-agent pipeline with mid-pipeline awareness]**: If step 3d-iii determines the headless invocation failed or no return contract was produced, execute the enhanced 5-step Task-agent fallback.
>
> **Before starting fallback, perform artifact scan** (3-state model):
>
> - **State A**: `<output-dir>/adversarial/` directory does not exist OR is empty. Action: Full fallback from F1. Emit: `"No headless artifacts found. Executing full Task-agent pipeline."`.
> - **State B**: Variant files (`variant-*.md`) exist but no `diff-analysis.md`. Action: Fallback from F2 (skip generation, use existing variants). Emit: `"Headless variants preserved. Resuming from diff analysis."`.
> - **State C**: `diff-analysis.md` exists. Action: Fallback from F3 (skip generation and diff, use existing analysis). Emit: `"Headless diff analysis preserved. Resuming from adversarial debate."`.
>
> **Enhanced fallback protocol** (5-step):
>
> **F1 [Variant generation]** (skip if State B or C): Use `Task` tool to dispatch one generation agent per expanded agent spec. Each agent receives: source spec file path, assigned model and persona, and instruction to generate a complete roadmap variant. Each variant must contain >=100 words in analysis sections. Write each variant to `<output_dir>/adversarial/variant-<model>-<persona>.md`. F1 must produce >=2 variant files.
>
> **F2 [Diff analysis]** (skip if State C): Use `Task` tool to dispatch a single analytical agent. The agent receives the relevant Step 1 instructions extracted from sc:adversarial SKILL.md **by section heading** (not line number). Produce `diff-analysis.md` with all 4 sections: structural_diff, content_diff, contradiction_detection, unique_contribution_extraction. Include severity ratings per item.
>
> **F3 [Adversarial debate]**: Use `Task` tool to orchestrate multi-round debate:
> - **Round 1**: Dispatch parallel advocate Task agents (one per variant). Each receives its variant content, all other variant contents, diff-analysis.md, and the Step 2 advocate instructions from SKILL.md (extracted by section heading). Must include steelman of opposing variants.
> - **Round 2** (if `--depth standard` or `--depth deep`): Sequential rebuttal Task agents. Each sees all Round 1 transcripts.
> - **Round 3** (if `--depth deep` AND convergence < threshold): Final arguments.
> - **Convergence tracking**: After each round, dispatch an orchestrator Task agent to evaluate per-diff-point agreement. Compute `convergence = agreed_points / total_diff_points`. Track per round. This replaces the hardcoded 0.5 sentinel with real measurement.
>
> Write `debate-transcript.md` with all rounds, scoring matrix, and convergence assessment.
>
> **F4 [Hybrid scoring and base selection]**: Use `Task` tool to dispatch a scoring agent. Receives Step 3 instructions from SKILL.md (by section heading). Execute dual-pass scoring:
> - Layer 1 (Quantitative, 50%): 5 metrics (RC, IC, SR, DC, SC) per variant.
> - Layer 2 (Qualitative, 50%): 25-criterion binary rubric across 5 dimensions.
> - Position-bias mitigation: Score in forward and reverse order, resolve disagreements.
> - Select base variant. Write `base-selection.md`.
>
> **F5 [Refactoring plan and merge]**: Two sequential Task agents:
> - **Planner**: Receives base variant, scoring rationale, all variants, debate transcript. Produces `refactor-plan.md` with per-change source attribution, integration approach, risk level.
> - **Executor**: Applies refactoring plan to base. Produces `merged-output.md` with provenance annotations (`<!-- Source: Variant N, Section ref -->`) and `merge-log.md`.
>
> **F-contract [Return contract assembly]**: sc:roadmap writes `return-contract.yaml` directly (no Task agent needed):
> - `schema_version: "1.0"`
> - `status`: derived from merge validation
> - `convergence_score`: from F3 convergence tracking (real value, not sentinel)
> - `merged_output_path`: path to merged-output.md
> - `artifacts_dir`: path to adversarial/ directory
> - `unresolved_conflicts`: count from convergence assessment
> - `base_variant`: from F4 base selection
> - `failure_stage: ~` (null if success)
> - `fallback_mode: true`
> - `invocation_method: "task_agent"`
>
> After fallback completes, proceed to step 3e (consume return contract).

### 3.4 T02.03 (within): Fallback Designation

The enhanced 5-step fallback is demoted from "sole mechanism" to "fallback for headless failure."

Changes to SKILL.md line 141 (currently reads: "Fallback protocol executes unconditionally as the sole invocation mechanism"):

**Replace with**:
> **3d [Launch headless adversarial session]**: Use the `claude -p` headless CLI to invoke sc:adversarial in a separate session with full pipeline execution. Read `refs/headless-invocation.md` for the invocation template and parameter mapping. If headless invocation fails, execute the enhanced Task-agent fallback (step 3d-iv).

Changes to return contract fields when fallback is used:
- `fallback_mode: true`
- `invocation_method: "task_agent"` (or `"headless+task_agent"` if mid-pipeline artifacts were preserved from a partial headless run)
- Emit message: `"claude -p headless invocation failed — executing enhanced Task-agent fallback (fallback_mode: true)"`

### 3.5 T03.01: Wiring Validation — Tool Availability (Phase 3)

**Currently missing from merged approach.** This task validates the invocation wiring from Phase 2.

**Updated specification** (replacing Skill tool check with `claude -p` check):

> **T03.01: Invocation Wiring Validation — Tool and CLI Availability**
>
> **Goal**: Confirm that the `claude -p` invocation pattern is correctly wired in the specification files.
>
> **Checks**:
> 1. `Bash` appears in allowed-tools for both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md`
> 2. `Skill` appears in allowed-tools for both files (retained for forward compatibility)
> 3. `refs/headless-invocation.md` exists and is referenced in Wave 2 step 3d-i
> 4. The command template in `refs/headless-invocation.md` includes `--dangerously-skip-permissions`, `--append-system-prompt`, `--output-format json`, and `--max-budget-usd`
>
> **Acceptance Criteria**:
> - All 4 checks pass
> - Evidence documented in D-0009

### 3.6 T03.02: Wiring Validation — Structural Audit (Phase 3)

**Currently missing from merged approach.** This task structurally audits the Wave 2 step 3 rewrite.

**Updated specification** (enhanced for `claude -p` architecture):

> **T03.02: Wave 2 Step 3 Structural Audit**
>
> **Goal**: Confirm the rewritten step 3 contains the correct sub-step structure.
>
> **8-point checklist**:
> 1. Wave 2 step 3 contains 6 sub-steps (3a through 3f)
> 2. Step 3d contains 4 sub-steps: 3d-i (construct), 3d-ii (execute), 3d-iii (validate), 3d-iv (fallback)
> 3. Step 3d-i references `refs/headless-invocation.md`
> 4. Step 3d-ii uses Bash tool with `timeout` command and `claude -p`
> 5. Step 3d-iii checks: exit code, JSON parse, contract existence, cost guard (4 checks)
> 6. Step 3d-iv contains 3-state artifact scan + enhanced F1-F5 fallback (5 steps, not 3)
> 7. Step 3e (return contract consumption) unchanged from current spec
> 8. Verb glossary contains "Launch headless session" entry
>
> **Acceptance Criteria**:
> - All 8 checklist items pass
> - Evidence documented in D-0010

### 3.7 T04.01: Return Contract Schema Update

**Deliverables affected**: D-0011 (schema spec), D-0012 (dead code removal)

10 fields total (9 original + 1 new):

```yaml
# return-contract.yaml — schema version 1.0, field count 10
schema_version: "1.0"              # Fixed string. Always "1.0" for this sprint.
status: success | partial | failed # Pipeline outcome
convergence_score: 0.0-1.0 | ~    # Real computed value (NOT 0.5 sentinel)
merged_output_path: <path> | ~     # Path to merged output file
artifacts_dir: <path>              # Path to adversarial/ directory
unresolved_conflicts: <integer> | ~ # Count of unresolved diff points
base_variant: <string> | ~         # Winning variant identifier
failure_stage: <string> | ~        # Step name where failure occurred, null if success
fallback_mode: true | false        # true when Task-agent fallback was used
invocation_method: "headless" | "task_agent" | "headless+task_agent"  # NEW: informational only
```

**Design decisions**:
- `schema_version` remains `"1.0"`. The addition of one optional informational field does not warrant a version bump. The schema header "v1.1" from the merged approach was an error; the field count changed but the schema contract did not break.
- `invocation_method` is **informational only**. Consumers (step 3e) MUST NOT branch on this field. It exists for traceability and debugging.
- `fallback_mode` retains existing semantics (not deprecated). `true` when Task-agent fallback was used, `false` when headless succeeded.
- `convergence_score` MUST be computed (from debate convergence tracking), not hardcoded to 0.5.

### 3.8 T04.02: Return Contract Consumption

**No change** to consumption logic in step 3e. If `invocation_method` is present, log it: `"Adversarial pipeline invocation method: <value>"`.

### 3.9 T04.03: Tier 1 Artifact Existence Gate

**Addition**: Check 0 before existing 4 checks. If invocation was via `claude -p`, validate JSON output. If `is_error: true`, log error details before proceeding to artifact checks.

### 3.10 T05.01: Verb Glossary

**Addition to glossary**:

| Verb | Tool | Description |
|------|------|-------------|
| **Launch headless session** | `Bash` tool with `claude -p` | Invoke a skill in an independent Claude session via headless CLI mode. The Bash tool executes the `claude -p` command; the headless session loads skill instructions via `--append-system-prompt`. |

### 3.11 T05.02: Wave 1A Step 2

Uses the same `claude -p` pattern as Wave 2 step 3d, but with Mode A parameters. The same 3d-i through 3d-iv sub-step pattern applies. The same enhanced fallback applies.

### 3.12 T05.03: adversarial-integration.md Conversion

Convert standalone pseudo-CLI syntax to `claude -p` invocation format. All `sc:adversarial --` patterns replaced with `claude -p` invocation commands.

---

## 4. New Infrastructure

### 4.1 Reference File: `refs/headless-invocation.md`

**Path**: `src/superclaude/skills/sc-roadmap/refs/headless-invocation.md`

Centralizes the `claude -p` invocation pattern. Referenced from Wave 1A step 2 and Wave 2 step 3d.

**Required contents**:
1. Prerequisites (Claude CLI installed, CLAUDECODE handling)
2. Mode A command template (multi-spec consolidation)
3. Mode B command template (multi-roadmap generation)
4. Parameter mapping table: depth → budget, depth → model, depth → timeout
5. Output parsing instructions (JSON + file-based contract)
6. Error handling matrix (8 conditions from Section 2.6)
7. CLAUDECODE environment variable handling pattern
8. Fallback trigger conditions (when to enter 3d-iv)

**Loading points**: Added to Wave loading table for both Wave 1A and Wave 2.

### 4.2 Probe Fixtures

Two minimal variant files (~100 words each) with deliberate structural and content differences. Stored at `src/superclaude/skills/sc-roadmap/fixtures/probe-variant-a.md` and `probe-variant-b.md`.

These are test fixtures for T01.01 test 4, not production artifacts.

### 4.3 Inline Bash (Not Shell Script)

**Decision**: The invocation is parameterized by runtime context and most naturally interpolated inline within the Bash tool call. No separate shell script. If the pattern stabilizes, a wrapper can be extracted later (YAGNI).

---

## 5. Instruction Delivery Protocol for Task Agents

When the enhanced fallback (F1-F5) dispatches Task agents, each agent receives SKILL.md instructions **inline** — not as a file reference.

**Extraction method**: sc:roadmap reads `src/superclaude/skills/sc-adversarial/SKILL.md` once, extracts relevant sections **by heading match** (not line number), and injects the extracted content into each Task agent prompt.

**Heading-to-step mapping**:

| Fallback Step | SKILL.md Section Heading | Content Extracted |
|---------------|-------------------------|-------------------|
| F2 (Diff analysis) | "Step 1" or "Diff Analysis" | Structural diff, content diff, contradiction detection, unique contribution extraction |
| F3 (Debate) | "Step 2" or "Adversarial Debate" | Advocate instructions, steelman requirements, round structure |
| F4 (Scoring) | "Step 3" or "Hybrid Scoring" | Quantitative metrics, qualitative rubric, position-bias mitigation |
| F5 (Merge) | "Step 4" and "Step 5" or "Refactoring" and "Merge" | Refactoring plan template, merge execution, provenance annotations |

**Rationale**: Line-number references (e.g., "lines 411-749") are fragile — any SKILL.md edit shifts them. Section-heading references are stable across edits that don't rename sections.

---

## 6. Risk Register

| ID | Risk | Prob | Impact | Mitigation |
|----|------|------|--------|------------|
| R1 | `claude -p` behavioral drift for complex pipelines | 0.35 | HIGH | T01.01 test 4 validates adherence pre-implementation. MANDATORY REQUIREMENTS in prompt reinforce critical behaviors. Enhanced fallback provides degraded path. |
| R2 | Cost unpredictability | 0.30 | MEDIUM | `--max-budget-usd` hard ceiling. Depth-based budget mapping. JSON `cost_usd` logged. Cost guard warns on >50% overshoot. |
| R3 | Context window limits | 0.25 | HIGH | T01.01 logs SKILL.md token estimate. If >40K tokens input, consider trimming non-essential sections. Context exhaustion → session end → contract missing → fallback activates. |
| R4 | Permission/sandbox concerns | 0.15 | HIGH | `--dangerously-skip-permissions` bypasses Claude Code permissions. OS permissions inherited. T01.01 test 2 validates file I/O. |
| R5 | CLI not installed | 0.10 | HIGH | T01.01 test 1 validates in 2 minutes. Fallback activates immediately. |
| R6 | Session nesting detection | 0.15 | MEDIUM | CLAUDECODE unset pattern. T01.01 test 2 detects this failure mode. |
| R7 | Behavioral drift over time | 0.25 | MEDIUM | Lightweight regression test: single `claude -p` invocation on probe fixture, checking artifact production. Manual smoke test before releases. |

---

## 7. Verification Plan

### 7.1 Pre-Implementation Verification (T01.01)

4-test viability probe as specified in Section 3.1. ~20 minutes, ~$4.

### 7.2 Structural Audit (T03.02, Post-Implementation)

8-point checklist as specified in Section 3.6.

### 7.3 Behavioral Adherence Verification (Post-Implementation)

Apply the 20-point behavioral adherence rubric to the first successful `claude -p` pipeline execution:

| Category | Max | Scoring |
|----------|-----|---------|
| Diff Analysis Structure | 4 | 4=all 4 sections + severity, 3=all sections, 2=2-3 sections, 1=generic comparison, 0=none |
| Debate Protocol | 4 | 4=steelman+scoring+multi-round, 3=scoring+debate, 2=single round, 1=prose comparison, 0=none |
| Scoring Method | 4 | 4=hybrid quant+qual, 3=some quantitative, 2=qualitative only, 1=unstructured, 0=none |
| Base Selection | 4 | 4=full scoring breakdown, 3=partial evidence, 2=brief justification, 1=implied, 0=none |
| Merge Execution | 4 | 4=provenance+merge-log, 3=some provenance, 2=no provenance, 1=summary only, 0=none |

**Passing threshold**: >= 14/20 (70%).

### 7.4 Multi-Round Debate Verification (Automated)

```bash
TRANSCRIPT="<output-dir>/adversarial/debate-transcript.md"
ROUND1=$(grep -ci "round.1\|first.round\|round 1" "$TRANSCRIPT" 2>/dev/null || echo 0)
ROUND2=$(grep -ci "round.2\|second.round\|round 2\|rebuttal" "$TRANSCRIPT" 2>/dev/null || echo 0)
LINES=$(wc -l < "$TRANSCRIPT" 2>/dev/null || echo 0)

echo "Round 1 markers: $ROUND1, Round 2 markers: $ROUND2, Lines: $LINES"
```

**Pass**: Round 1 > 0 AND Round 2 > 0 AND lines > 100.

### 7.5 End-to-End Test

Run `sc:roadmap --multi-roadmap --agents opus,sonnet` on a test spec. Verify:
1. `claude -p` invoked (Bash tool call in session)
2. Adversarial artifacts produced: variant-*.md (>=2), diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged-output.md
3. `return-contract.yaml` has all 10 fields
4. `convergence_score` is computed (not 0.5 sentinel)
5. `fallback_mode: false` and `invocation_method: "headless"`
6. sc:roadmap routes correctly on contract status

**Fallback verification** (separate test): Force headless failure. Verify:
1. Fallback activates with warning message
2. F1-F5 all execute (5 steps, not 3)
3. `return-contract.yaml` written with `fallback_mode: true` and real computed convergence
4. Behavioral adherence rubric score >= 10/20 for fallback path

---

## 8. Glossary Updates

The tasklist glossary (Section "Glossary" in tasklist-P6.md) requires the following updates to align with this specification:

| Term | Current Definition | Updated Definition |
|------|-------------------|-------------------|
| Skill tool | Claude Code tool that invokes a named skill | *No change* (retained for forward compatibility) |
| Fallback protocol | 3-step inline execution (F1, F2/3, F4/5) activated when Skill tool invocation fails | **Enhanced 5-step inline execution (F1, F2, F3, F4, F5) activated when `claude -p` headless invocation fails. Replaces the compressed 3-step protocol.** |
| Primary path | Direct Skill tool invocation of sc:adversarial (preferred if Task 0.0 probe succeeds) | **`claude -p` headless CLI invocation of sc:adversarial (preferred if T01.01 viability probe succeeds)** |
| Fallback-only variant | Sprint adaptation when primary Skill tool path is blocked; fallback becomes sole invocation mechanism | **Sprint adaptation when `claude -p` headless path is blocked; enhanced 5-step fallback becomes sole invocation mechanism** |
| *NEW*: Headless invocation | — | **Non-interactive CLI invocation via `claude -p` with `--append-system-prompt` for behavioral control, `--dangerously-skip-permissions` for autonomous execution, and `--output-format json` for structured output** |
| *NEW*: Mid-pipeline awareness | — | **3-state artifact scan (none/variants/diff-analysis) that determines fallback entry point, preserving partial work from a failed headless session** |

---

## 9. Deliverable Updates

The following deliverable descriptions in the Deliverable Registry require updates:

| ID | Current Description | Updated Description |
|----|--------------------|--------------------|
| D-0001 | Skill Tool Probe result document | **`claude -p` Viability Probe result document (4-test)** |
| D-0002 | Sprint variant decision record | **Sprint variant decision record (headless vs fallback-only)** |
| D-0007 | Fallback protocol (F1, F2/3, F4/5) | **Enhanced fallback protocol (F1, F2, F3, F4, F5) with real convergence tracking** |
| D-0009 | Skill Tool Availability test result | **Invocation wiring validation: tool and CLI availability** |
| D-0010 | Wave 2 Step 3 Structural Audit result | **Wave 2 Step 3 Structural Audit result (8-point checklist for `claude -p` architecture)** |

---

## 10. Summary of All Sprint-Spec Modifications

| Sprint-Spec Section | Task ID | Change Type | Description |
|---------------------|---------|-------------|-------------|
| Task 0.0 (T01.01) | T01.01 | **Replace** | Skill tool probe → 4-test `claude -p` viability probe (incl. behavioral adherence) |
| Task 1.1 AC (T02.01) | T02.01 | **Append** | Verify `Bash` in allowed-tools |
| Task 1.2 AC (T02.02) | T02.02 | **Append** | Verify `Bash` in allowed-tools |
| Wave 2 step 3d (T02.03) | T02.03 | **Rewrite** | Fallback-only → headless primary + enhanced 5-step fallback with 3-state mid-pipeline awareness |
| Fallback designation (T02.03) | T02.03 | **Demote** | "Sole mechanism" → "Fallback for headless failure" |
| Wiring validation (T03.01) | T03.01 | **Update** | Skill tool check → `claude -p` wiring + CLI check (4 points) |
| Structural audit (T03.02) | T03.02 | **Update** | Generic audit → 8-point `claude -p` architecture audit |
| Return contract schema (T04.01) | T04.01 | **Add field** | `invocation_method` (optional, informational) |
| Return contract consumption (T04.02) | T04.02 | **Append** | Log `invocation_method` for traceability |
| Tier 1 gate (T04.03) | T04.03 | **Add check** | Check 0: headless JSON health |
| Verb glossary (T05.01) | T05.01 | **Add entry** | "Launch headless session" = Bash + claude -p |
| Wave 1A step 2 (T05.02) | T05.02 | **Rewrite** | "Invoke" → headless invocation pattern |
| Pseudo-CLI conversion (T05.03) | T05.03 | **Adapt** | Pseudo-CLI → claude -p format |
| Glossary | — | **Update** | 4 definitions updated + 2 new terms |
| Deliverable Registry | — | **Update** | 5 deliverable descriptions updated |
| Risk Register | — | **Add** | 7 risks (R1-R7) |
| Verification Plan | — | **Expand** | Add behavioral adherence rubric + multi-round grep checks + 8-point structural audit |
| New: refs/ file | — | **Create** | `refs/headless-invocation.md` |
| New: probe fixtures | — | **Create** | 2 minimal variant files for T01.01 test 4 |
| Wave loading table | — | **Update** | Wave 1A and Wave 2 load `refs/headless-invocation.md` |

---

## 11. Fallback-Only Sprint Variant

If T01.01 fails (all 4 tests, or test 4 fails after augmentation retry):

The sprint proceeds using the **enhanced 5-step Task-agent pipeline** (F1-F5 from Section 3.3, step 3d-iv) as the sole invocation mechanism. This is NOT the old 3-step fallback — it is the upgraded 5-step pipeline with real convergence tracking.

Changes from current fallback-only variant:
- Upgraded from 3-step (F1/F2-3/F4-5) to 5-step (F1/F2/F3/F4/F5)
- Real convergence tracking replaces 0.5 sentinel
- `invocation_method: "task_agent"` in return contract
- `fallback_mode: true` (always, since there's no primary path)

Trigger: "T01.01 decision gate returns 'primary path blocked' (neither Skill tool nor `claude -p` headless invocation can reliably invoke sc:adversarial with sufficient behavioral adherence)."

---

## Appendix A: Critical Issues Resolved

This specification addresses all 5 critical issues identified during the reflection review of the merged approach:

| ID | Issue | Resolution |
|----|-------|------------|
| C1 | Permission flag inconsistency | Standardized on `--dangerously-skip-permissions` with documented rationale (Section 2.1) |
| C2 | Task ID mapping absent | Full mapping table added (Section 0, Task ID Mapping) |
| C3 | Phase 3 tasks unaddressed | T03.01 and T03.02 specifications added (Sections 3.5, 3.6) |
| C4 | Glossary contradictions | Updated glossary with 4 corrected + 2 new definitions (Section 8) |
| C5 | Schema version inconsistency | Resolved: `schema_version: "1.0"` is correct; "v1.1" header was error (Section 3.7 note) |

## Appendix B: Important Issues Resolved

| ID | Issue | Resolution |
|----|-------|------------|
| I1 | SKILL.md line 141 contradiction | Replacement text specified (Section 3.4) |
| I2 | Wave 1A specifics | Same `claude -p` pattern applies (Section 3.11) |
| I3 | Fallback extraction to ref | Centralized in `refs/headless-invocation.md` (Section 4.1) |
| I4 | Heading names for instruction delivery | Section-heading extraction protocol defined (Section 5) |
| I5 | Deliverable R-007 stale description | Updated from "3-step (F1, F2/3, F4/5)" to "5-step (F1-F5)" (Section 9) |

---

*Specification draft generated 2026-02-23.*
*Based on merged adversarial approach (convergence: 1.00) with reflection-identified fixes applied.*
*Ready for expert panel review.*
