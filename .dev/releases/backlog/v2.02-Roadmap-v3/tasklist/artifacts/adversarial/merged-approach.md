# Merged Approach: claude -p Headless Invocation with Enhanced Fallback

**Base**: Approach 2 (claude -p as Primary Invocation)
**Absorbed from**: Approach 1 (behavioral adherence testing), Approach 3 (enhanced 5-step fallback, mid-pipeline awareness)
**Date**: 2026-02-23
**Status**: FINAL — Ready to replace sprint-spec amendments section
**Convergence score**: 1.00 (all debate points resolved)

<!-- Source: Approach 2, Architecture -->
<!-- Absorbed: Approach 1, §3 T05 behavioral adherence rubric -->
<!-- Absorbed: Approach 3, §4 enhanced Task-agent pipeline (F1-F5) -->
<!-- Absorbed: Approach 3, §3 mid-pipeline fallover (simplified to 3-state) -->
<!-- Rejected: Approach 3, --invocation-mode flag (YAGNI) -->
<!-- Rejected: Approach 3, depth-based routing (premature optimization) -->
<!-- Rejected: Approach 1, full 13-test probe (over-scoped) -->

---

## 1. Philosophy

<!-- Source: Approach 2, §1 -->

`claude -p` is the primary invocation mechanism for the sc:adversarial pipeline within sc:roadmap. It provides genuine process isolation: a separate context window, full SKILL.md behavioral instructions loaded via `--append-system-prompt`, structured JSON output with cost/usage metadata, and independence from the parent session's context budget.

The Task-agent fallback is an enhanced 5-step pipeline (upgraded from the previous 3-step compression) that activates when `claude -p` fails. It is NOT a peer path — it is a fallback. The primary/fallback hierarchy is maintained for architectural clarity and maintenance simplicity.

<!-- Source: Approach 3, §6 -->

The **return contract** (`return-contract.yaml`) is the abstraction boundary between invocation mechanism and consumer logic. Step 3e in sc:roadmap reads the return contract and routes on `status` and `convergence_score`. It does not know and does not care whether the contract was produced by a headless session or the Task-agent fallback.

---

## 2. Invocation Design

### 2.1 Command Construction Pattern

<!-- Source: Approach 2, §2.1-2.2 -->

| Component | Mechanism | Content |
|-----------|-----------|---------|
| **Behavioral instructions** | `--append-system-prompt` | Raw content of `sc-adversarial/SKILL.md` |
| **Task prompt** | `-p` (positional prompt) | Specific invocation with parameters |
| **Tool access** | `--allowedTools` | `Read,Write,Edit,Bash,Glob,Grep,Task` |
| **Cost control** | `--max-budget-usd` | Per-invocation spending cap |
| **Output** | `--output-format json` | Structured result with session_id, usage, cost |
| **Permissions** | `--dangerously-skip-permissions` | Autonomous execution (no interactive prompts) |

### 2.2 The Exact Command Template

```bash
# Environment preparation: unset CLAUDECODE to prevent nested session detection
CLAUDECODE_BACKUP="${CLAUDECODE:-}" && unset CLAUDECODE

# Read SKILL.md content for system prompt injection
ADVERSARIAL_SKILL_CONTENT="$(cat src/superclaude/skills/sc-adversarial/SKILL.md)"

# Compute budget from depth: quick=1.00, standard=2.00, deep=5.00
BUDGET="<computed-from-depth>"

# Compute model from depth (optional): quick/standard=sonnet, deep=opus
MODEL="<computed-from-depth>"

# Construct the invocation
timeout "${TIMEOUT}" claude -p \
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
  2>/dev/null

HEADLESS_EXIT=$?

# Restore environment
if [ -n "$CLAUDECODE_BACKUP" ]; then
  export CLAUDECODE="$CLAUDECODE_BACKUP"
fi
```

### 2.3 Parameter Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `--model` | sonnet (quick/standard), opus (deep) | Cost-effective for standard; high-quality for deep |
| `--allowedTools` | `Read,Write,Edit,Bash,Glob,Grep,Task` | Matches sc:adversarial's allowed-tools. `Task` enables sub-agent delegation. |
| `--max-budget-usd` | quick=$1.00, standard=$2.00, deep=$5.00 | Hard cost ceiling per invocation |
| `--dangerously-skip-permissions` | present | Required for autonomous file writes |
| `--output-format json` | present | Structured output parsing: session_id, cost_usd, is_error |
| Timeout | quick=180s, standard=300s, deep=600s | Process kill if exceeded |

### 2.4 Output Capture and Parsing

<!-- Source: Approach 2, §2.4 -->

The primary validation is the **file-based return contract** at `<output-dir>/adversarial/return-contract.yaml`. The JSON output from `--output-format json` provides supplementary metadata (cost, duration, error status).

```bash
HEADLESS_OUTPUT=$(timeout ${TIMEOUT} claude -p "${PROMPT}" ... 2>/dev/null)
HEADLESS_EXIT=$?

# Primary validation: return contract existence
if [ -f "<output-dir>/adversarial/return-contract.yaml" ]; then
  echo "HEADLESS_CONTRACT: found"
else
  echo "HEADLESS_CONTRACT: missing"
fi

# Supplementary: extract cost from JSON output
HEADLESS_COST=$(echo "$HEADLESS_OUTPUT" | grep -o '"cost_usd":[0-9.]*' | cut -d: -f2)
```

### 2.5 CLAUDECODE Environment Variable Handling

<!-- Source: Approach 2, §2.5 -->

Claude Code sets `CLAUDECODE` in active sessions. Unset before invocation, restore after. This is handled within the Bash tool call — only the subprocess environment is affected.

### 2.6 Error Detection Matrix

<!-- Source: Approach 2, §2.6 -->

| Error Condition | Detection | Handling |
|-----------------|-----------|----------|
| `claude` not in PATH | `which claude` non-zero | Abort; fall through to fallback |
| Non-zero exit code | `$?` after invocation | Log error; check for partial artifacts |
| Timeout | Bash `timeout` command (exit 124) | Kill process; check partial artifacts |
| Permission denied | Exit code 126/127 | Abort; fall through to fallback |
| Malformed JSON output | JSON parse failure | Ignore JSON; rely on file-based contract |
| Cost exceeded | `--max-budget-usd` enforced by CLI | CLI self-terminates; check partial artifacts |
| Return contract missing | File existence check | Trigger 3-state fallback scan |
| Return contract malformed | YAML parse attempt | Treat as `status: failed, failure_stage: transport` |

---

## 3. Sprint-Spec Modifications

### Task 0.0: `claude -p` Viability Probe (Enhanced)

<!-- Source: Approach 2, §3 Task 0.0 -->
<!-- Absorbed: Approach 1, §3 T05 behavioral adherence rubric (simplified) -->

**Replaces**: Current Task 0.0 (Skill Tool Probe)

> **Task 0.0: `claude -p` Headless Invocation Viability Probe (Pre-Implementation Gate)**
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
> **Informational output** (not gated): Log SKILL.md file size in characters and estimated tokens. Log test 4 cost from JSON output.
>
> **Time cost**: ~20 minutes. **API cost**: ~$4. **Blocks**: All subsequent tasks.

### Tasks 1.1-1.2: `Skill` in allowed-tools

<!-- Source: Approach 2, §3 Tasks 1.1-1.2 -->

**Retained but deprioritized**. `Skill` remains in allowed-tools for forward compatibility. `Bash` is now the critical tool for `claude -p` invocation and is already present.

**Addition to both ACs**: "Verify `Bash` is present in allowed-tools (required for `claude -p` invocation)."

### Task 1.3: Wave 2 Step 3d — Complete Rewrite

<!-- Source: Approach 2, §5 (exact specification text) -->
<!-- Absorbed: Approach 3, §3 mid-pipeline fallover (3-state) -->
<!-- Absorbed: Approach 3, §4 enhanced 5-step fallback -->

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
> - **State A**: `<output-dir>/adversarial/` directory does not exist OR is empty → Full fallback from F1. Emit: `"No headless artifacts found. Executing full Task-agent pipeline."`.
> - **State B**: Variant files (`variant-*.md`) exist but no `diff-analysis.md` → Fallback from F2 (skip generation, use existing variants). Emit: `"Headless variants preserved. Resuming from diff analysis."`.
> - **State C**: `diff-analysis.md` exists → Fallback from F3 (skip generation and diff, use existing analysis). Emit: `"Headless diff analysis preserved. Resuming from adversarial debate."`.
>
> **Enhanced fallback protocol** (5-step):
>
> **F1 [Variant generation]** (skip if State B or C): Use `Task` tool to dispatch one generation agent per expanded agent spec. Each agent receives: source spec file path, assigned model and persona, and instruction to generate a complete roadmap variant. Each variant must contain >=100 words in analysis sections. Write each variant to `<output_dir>/adversarial/variant-<model>-<persona>.md`. F1 must produce >=2 variant files.
>
> **F2 [Diff analysis]** (skip if State C): Use `Task` tool to dispatch a single analytical agent. The agent receives the relevant Step 1 instructions extracted from sc:adversarial SKILL.md (by section heading, not line number). Produce `diff-analysis.md` with all 4 sections: structural_diff, content_diff, contradiction_detection, unique_contribution_extraction. Include severity ratings per item.
>
> **F3 [Adversarial debate]**: Use `Task` tool to orchestrate multi-round debate:
> - **Round 1**: Dispatch parallel advocate Task agents (one per variant). Each receives its variant content, all other variant contents, diff-analysis.md, and the Step 2 advocate instructions from SKILL.md. Must include steelman of opposing variants.
> - **Round 2** (if `--depth standard` or `--depth deep`): Sequential rebuttal Task agents. Each sees all Round 1 transcripts.
> - **Round 3** (if `--depth deep` AND convergence < threshold): Final arguments.
> - **Convergence tracking**: After each round, dispatch an orchestrator Task agent to evaluate per-diff-point agreement. Compute `convergence = agreed_points / total_diff_points`. Track per round.
>
> Write `debate-transcript.md` with all rounds, scoring matrix, and convergence assessment.
>
> **F4 [Hybrid scoring and base selection]**: Use `Task` tool to dispatch a scoring agent. Receives Step 3 instructions from SKILL.md. Execute dual-pass scoring:
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
> - `convergence_score`: from F3 convergence tracking (real, not sentinel)
> - `merged_output_path`: path to merged-output.md
> - `artifacts_dir`: path to adversarial/ directory
> - `unresolved_conflicts`: count from convergence assessment
> - `base_variant`: from F4 base selection
> - `failure_stage: ~` (null if success)
> - `fallback_mode: true`
> - `invocation_method: "task_agent"`
>
> After fallback completes, proceed to step 3e (consume return contract).

### Task 1.4: Fallback Designation

<!-- Source: Approach 2, §3 Task 1.4 -->

The enhanced 5-step fallback is demoted from "sole mechanism" to "fallback for headless failure." Changes:
- `fallback_mode: true` in return contract
- `invocation_method: "task_agent"` (or `"headless+task_agent"` if mid-pipeline artifacts were preserved)
- Emit message: `"claude -p headless invocation failed — executing enhanced Task-agent fallback (fallback_mode: true)"`

### Epic 2 Changes

#### Task 2.1: Verb Glossary

<!-- Source: Approach 2, §3 Task 2.1 -->

**Addition**:

| Verb | Tool | Description |
|------|------|-------------|
| **Launch headless session** | `Bash` tool with `claude -p` | Invoke a skill in an independent Claude session via headless CLI mode. The Bash tool executes the `claude -p` command; the headless session loads skill instructions via `--append-system-prompt`. |

#### Task 2.3: Wave 1A Step 2

<!-- Source: Approach 2, §3 Task 2.3 -->

Uses the same `claude -p` pattern as Wave 2 step 3d, but with Mode A parameters. The same 3d-i through 3d-iv sub-step pattern applies. The same enhanced fallback applies.

#### Task 2.4: adversarial-integration.md Conversion

<!-- Source: Approach 2, §3 Task 2.4 -->

Convert standalone pseudo-CLI syntax to `claude -p` invocation format. Example:

```bash
# Headless invocation (primary)
claude -p "Execute sc:adversarial in Mode A. Compare: spec1.md,spec2.md. ..." \
  --append-system-prompt "$(cat src/superclaude/skills/sc-adversarial/SKILL.md)" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --dangerously-skip-permissions --output-format json --max-budget-usd 2.00
```

### Epic 3 Changes

#### Task 3.1: Return Contract Schema (v1.1)

<!-- Source: Approach 2, §3 Task 3.1 -->
<!-- Absorbed: Approach 3, §5 invocation_method field -->

10 fields total (9 original + 1 new):

```yaml
schema_version: "1.0"
status: success | partial | failed
convergence_score: 0.0-1.0 | ~
merged_output_path: <path> | ~
artifacts_dir: <path>
unresolved_conflicts: <integer> | ~
base_variant: <string> | ~
failure_stage: <string> | ~
fallback_mode: true | false
invocation_method: "headless" | "task_agent" | "headless+task_agent"
```

`invocation_method` is **informational only**. Consumers (step 3e) MUST NOT branch on this field.

#### Task 3.2: Return Contract Read Instruction

**No change** to consumption logic. If `invocation_method` is present, log it for traceability: `"Adversarial pipeline invocation method: <value>"`.

#### Task 3.3: Tier 1 Artifact Existence Gate

<!-- Source: Approach 2, §3 Task 3.3 -->

Add Check 0 before existing 4 checks: If invocation was via `claude -p`, validate JSON output. If `is_error: true`, log error details before proceeding to artifact checks.

---

## 4. New Infrastructure

### 4.1 Reference File: `refs/headless-invocation.md`

<!-- Source: Approach 2, §4.1 -->

Centralizes the `claude -p` invocation pattern (defined once, referenced from Wave 1A step 2 and Wave 2 step 3d).

Contents: Prerequisites, Mode A/B command templates, parameter mapping (depth→budget, depth→model, depth→timeout), output parsing, error handling matrix, CLAUDECODE env handling, fallback trigger conditions.

Loaded in Wave 1A and Wave 2 at the same points as `refs/adversarial-integration.md`.

### 4.2 Probe Fixtures

Two minimal variant files (~100 words each) with deliberate structural and content differences, stored at a stable path for Task 0.0 test 4. These are test fixtures, not production artifacts.

### 4.3 Shell Script vs Inline Bash

<!-- Source: Approach 2, §4.3 -->

**Decision: Inline Bash, not a shell script.** The invocation is parameterized by runtime context (spec path, agents, depth, output dir) and is most naturally interpolated inline. If the pattern stabilizes, a wrapper can be extracted later (YAGNI).

---

## 5. Risk Register

### R1: `claude -p` Behavioral Drift for Complex Pipelines
**Prob**: 0.35 | **Impact**: HIGH
**Mitigation**: Task 0.0 test 4 validates behavioral adherence pre-implementation. MANDATORY REQUIREMENTS in prompt reinforce critical behaviors. Enhanced fallback provides high-quality degraded path.

### R2: Cost Unpredictability
**Prob**: 0.30 | **Impact**: MEDIUM
**Mitigation**: `--max-budget-usd` hard ceiling. Depth-based budget mapping. JSON output includes `cost_usd`. Cost guard warns on >50% overshoot.

### R3: Context Window Limits
**Prob**: 0.25 | **Impact**: HIGH
**Mitigation**: Task 0.0 logs SKILL.md token estimate. If >40K tokens input, consider trimming non-essential SKILL.md sections for injection. Context exhaustion triggers session end → return contract missing → fallback activates.

### R4: Permission/Sandbox Concerns
**Prob**: 0.15 | **Impact**: HIGH
**Mitigation**: `--dangerously-skip-permissions` bypasses Claude Code permissions. OS permissions inherited from parent session. Task 0.0 test 2 validates file I/O.

### R5: CLI Not Installed
**Prob**: 0.10 | **Impact**: HIGH
**Mitigation**: Task 0.0 test 1 validates in 2 minutes. Fallback activates immediately.

### R6: Session Nesting Detection
**Prob**: 0.15 | **Impact**: MEDIUM
**Mitigation**: CLAUDECODE unset pattern. Task 0.0 test 2 detects this failure mode.

### R7: Behavioral Drift Over Time
**Prob**: 0.25 | **Impact**: MEDIUM
<!-- Source: Approach 1, §6 Risk G -->
**Mitigation**: Add lightweight regression test to project test suite. Single `claude -p` invocation on tiny fixture, checking artifact production and basic structure. Run as manual smoke test before releases.

---

## 6. Verification Plan

### Pre-Implementation Verification (Task 0.0)

4-test viability probe as specified in Section 3. ~20 minutes, ~$4.

### Structural Audit (Post-Implementation)

<!-- Source: Approach 2, §7 Structural Audit -->

Manual inspection checklist:
1. Wave 2 step 3 contains 6 sub-steps (3a through 3f).
2. Step 3d contains 4 sub-steps: 3d-i (construct), 3d-ii (execute), 3d-iii (validate), 3d-iv (fallback).
3. Step 3d-i references `refs/headless-invocation.md`.
4. Step 3d-ii uses Bash tool with `timeout` command.
5. Step 3d-iii checks: exit code, JSON parse, contract existence, cost guard (4 checks).
6. Step 3d-iv contains 3-state artifact scan + enhanced F1-F5 fallback.
7. Step 3e (return contract consumption) unchanged.
8. Verb glossary contains "Launch headless session" entry.

### Behavioral Adherence Verification (Post-Implementation)

<!-- Source: Approach 1, §3 Scoring Rubric for T05 -->

Apply the 20-point behavioral adherence rubric to the first successful `claude -p` pipeline execution:

| Category | Max | Scoring |
|----------|-----|---------|
| Diff Analysis Structure | 4 | 4=all 4 sections + severity, 3=all sections, 2=2-3 sections, 1=generic comparison, 0=none |
| Debate Protocol | 4 | 4=steelman+scoring+multi-round, 3=scoring+debate, 2=single round, 1=prose comparison, 0=none |
| Scoring Method | 4 | 4=hybrid quant+qual, 3=some quantitative, 2=qualitative only, 1=unstructured, 0=none |
| Base Selection | 4 | 4=full scoring breakdown, 3=partial evidence, 2=brief justification, 1=implied, 0=none |
| Merge Execution | 4 | 4=provenance+merge-log, 3=some provenance, 2=no provenance, 1=summary only, 0=none |

**Passing threshold**: >= 14/20 (70%).

### Multi-Round Debate Verification (Automated)

<!-- Source: Approach 1, §T07 -->

```bash
TRANSCRIPT="<output-dir>/adversarial/debate-transcript.md"
ROUND1=$(grep -ci "round.1\|first.round\|round 1" "$TRANSCRIPT" 2>/dev/null || echo 0)
ROUND2=$(grep -ci "round.2\|second.round\|round 2\|rebuttal" "$TRANSCRIPT" 2>/dev/null || echo 0)
LINES=$(wc -l < "$TRANSCRIPT" 2>/dev/null || echo 0)

echo "Round 1 markers: $ROUND1, Round 2 markers: $ROUND2, Lines: $LINES"
```

**Pass**: Round 1 > 0 AND Round 2 > 0 AND lines > 100.

### End-to-End Test

<!-- Source: Approach 2, §7 End-to-End Test -->

Run `sc:roadmap --multi-roadmap --agents opus,sonnet` on a test spec. Verify:
1. `claude -p` invoked (Bash tool call in session)
2. Adversarial artifacts produced: variant-*.md (>=2), diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged-output.md
3. `return-contract.yaml` has all 10 fields
4. `convergence_score` is computed (not 0.5 sentinel)
5. `fallback_mode: false` and `invocation_method: "headless"`
6. sc:roadmap routes correctly on contract status

**Fallback verification** (separate): Force headless failure (rename `claude` binary or use broken path). Verify:
1. Fallback activates with warning
2. F1-F5 execute
3. `return-contract.yaml` written with `fallback_mode: true` and computed convergence
4. Behavioral adherence rubric score >= 10/20 for fallback path

---

## 7. Summary of All Sprint-Spec Modifications

<!-- Source: Approach 2, §8 (enhanced) -->

| Sprint-Spec Section | Change Type | Description |
|---------------------|-------------|-------------|
| Task 0.0 | **Replace** | Skill tool probe → 4-test `claude -p` viability probe (incl. behavioral adherence) |
| Task 1.1 AC | **Append** | Verify `Bash` in allowed-tools |
| Task 1.2 AC | **Append** | Verify `Bash` in allowed-tools |
| Task 1.3 step 3d | **Rewrite** | Fallback-only → headless primary + enhanced 5-step fallback with 3-state mid-pipeline awareness |
| Task 1.4 | **Demote** | "Sole mechanism" → "Fallback for headless failure" |
| Task 2.1 glossary | **Add entry** | "Launch headless session" = Bash + claude -p |
| Task 2.3 Wave 1A | **Rewrite** | "Invoke" → headless invocation pattern |
| Task 2.4 conversion | **Adapt** | Pseudo-CLI → claude -p format |
| Task 3.1 schema | **Add field** | `invocation_method` (optional, informational) |
| Task 3.2 consumption | **Append** | Log `invocation_method` for traceability |
| Task 3.3 gate | **Add check** | Check 0: headless JSON health |
| Fallback-Only Variant | **Remove** | No longer needed; enhanced fallback always available as secondary |
| Risk Register | **Add 7 risks** | R1 through R7 |
| Verification Plan | **Expand** | Add behavioral adherence rubric + multi-round grep checks |
| New: refs/ file | **Create** | `refs/headless-invocation.md` |
| New: probe fixtures | **Create** | 2 minimal variant files for Task 0.0 test 4 |
| Wave loading table | **Update** | Wave 1A and Wave 2 load `refs/headless-invocation.md` |

---

## 8. Fallback-Only Sprint Variant

If Task 0.0 fails (all 4 tests, or test 4 fails after augmentation retry):

The sprint proceeds using the **enhanced 5-step Task-agent pipeline** (F1-F5 from Section 3, step 3d-iv) as the sole invocation mechanism. This is NOT the old 3-step fallback — it is the upgraded 5-step pipeline with real convergence tracking. The `claude -p` headless path is removed from scope.

Changes from current fallback-only variant:
- Upgraded from 3-step (F1/F2-3/F4-5) to 5-step (F1/F2/F3/F4/F5)
- Real convergence tracking replaces 0.5 sentinel
- `invocation_method: "task_agent"` in return contract
- `fallback_mode: true` (always, since there's no primary path)

Trigger description update: "Task 0.0 decision gate returns 'primary path blocked' (neither Skill tool nor `claude -p` headless invocation can reliably invoke sc:adversarial with sufficient behavioral adherence)."

---

*Merged approach generated 2026-02-23.*
*Base: Approach 2 (claude-opus-4-6). Absorbed elements from: Approach 1 (behavioral adherence rubric, multi-round verification, quality thresholds), Approach 3 (enhanced 5-step fallback, real convergence tracking, mid-pipeline awareness, invocation_method field, instruction delivery protocol).*
*Convergence: 1.00 (12/12 debate points resolved).*
*Combined score: 0.900 (base) + absorbed improvements.*
