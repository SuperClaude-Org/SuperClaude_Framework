# Approach 2: `claude -p` as Primary Invocation Mechanism

**Date**: 2026-02-23
**Author**: claude-opus-4-6 (system-architect persona)
**Status**: PROPOSAL
**Scope**: Sprint-spec modification for sc:roadmap adversarial pipeline remediation
**Supersedes**: Skill tool invocation path (Task 0.0 primary path)

---

## 1. Philosophy

### Why Commit to `claude -p`?

The current sprint-spec treats `claude -p` as an implicit fallback possibility never seriously considered. The Skill tool is framed as the "primary path" despite multiple known blockers:

1. **The Skill tool has no callable API**. The `Skill` tool in Claude Code is a conversational dispatch mechanism, not a programmatic one. It cannot return structured data. It cannot be parameterized with runtime-computed values. It exists to load and execute SKILL.md instructions within the *current* session context.

2. **Cross-skill invocation is architecturally blocked**. The Claude Code documentation explicitly states "Do not invoke a skill that is already running." Since sc:roadmap IS the running skill, invoking sc:adversarial via the Skill tool from within sc:roadmap is blocked by design. Task 0.0 in the current sprint-spec exists precisely because this is uncertain -- but the architectural evidence strongly suggests it will fail.

3. **The fallback protocol is already the de-facto path**. The current SKILL.md (line 141) already states: "The primary Skill tool invocation path is unavailable in this environment. Fallback protocol executes unconditionally as the sole invocation mechanism." This was written AFTER Task 0.0 was discovered to fail. The sprint-spec has not caught up.

4. **`claude -p` provides genuine process isolation**. A headless Claude session is a separate process with its own context window, tool access, and execution lifecycle. This is architecturally superior to the fallback's Task-agent approach, which operates within the parent's context window and cannot access the full sc:adversarial SKILL.md behavioral instructions.

### Architectural Rationale

The `claude -p` approach treats skill-to-skill invocation as **inter-process communication** rather than intra-process delegation:

```
Current Fallback (intra-process):
  sc:roadmap session
    └─ Task agent (limited context, no SKILL.md access)
       └─ F1: generate variants (bare prompt, no adversarial protocol)
       └─ F2/3: diff + debate (single pass, no structured protocol)
       └─ F4/5: merge + contract (estimated convergence, no measurement)

Proposed claude -p (inter-process):
  sc:roadmap session
    └─ Bash: claude -p (launches independent session)
       └─ sc:adversarial session (full SKILL.md loaded via --append-system-prompt)
          └─ Step 1: Diff Analysis (full protocol)
          └─ Step 2: Adversarial Debate (multi-round, convergence tracking)
          └─ Step 3: Hybrid Scoring (quantitative + qualitative)
          └─ Step 4: Refactoring Plan
          └─ Step 5: Merge Execution
          └─ Writes: return-contract.yaml (structured, measured convergence)
```

**Key advantages**:
- Full sc:adversarial behavioral instructions are loaded (not approximated by Task agent prompts)
- Convergence is measured, not estimated at a fixed 0.5 sentinel
- The 5-step pipeline executes as designed, not compressed into 3 fallback steps
- Separate context window means the adversarial pipeline does not consume sc:roadmap's context budget
- Cost and token usage are independently observable via `--output-format json`
- Session can be resumed via `--resume <session_id>` if interrupted

**Key trade-off**: `claude -p` requires the `claude` CLI to be installed and in PATH. This is a reasonable assumption for a Claude Code environment but must be validated.

---

## 2. Invocation Design

### 2.1 Command Construction Pattern

The invocation uses two complementary mechanisms:

| Component | Mechanism | Content |
|-----------|-----------|---------|
| **Behavioral instructions** | `--append-system-prompt` | Raw content of `sc-adversarial/SKILL.md` |
| **Task prompt** | `-p` (positional prompt) | Specific invocation with parameters |
| **Tool access** | `--allowedTools` | Tool whitelist |
| **Cost control** | `--max-budget-usd` | Per-invocation spending cap |
| **Output** | `--output-format json` | Structured result with session_id, usage, cost |
| **Permissions** | `--dangerously-skip-permissions` | Autonomous execution (no interactive prompts) |

**Decision: Raw prompt with SKILL.md system prompt, NOT slash command invocation.**

Rationale per GitHub #1048: Custom slash commands are unreliable in headless mode. Claude may ignore behavioral instructions delivered via skill invocation. By injecting the full SKILL.md content via `--append-system-prompt`, the behavioral instructions become part of the system prompt, which has the highest compliance priority.

### 2.2 The Exact Command Template

```bash
# Environment preparation: unset CLAUDECODE to prevent nested session detection
CLAUDECODE_BACKUP="${CLAUDECODE:-}" && unset CLAUDECODE

# Read SKILL.md content for system prompt injection
ADVERSARIAL_SKILL_CONTENT="$(cat src/superclaude/skills/sc-adversarial/SKILL.md)"

# Construct the invocation
claude -p \
  "Execute the sc:adversarial pipeline in Mode B (generate + compare).
   Source: <spec-file-path>
   Generate type: roadmap
   Agents: <expanded-agent-specs>
   Depth: <depth>
   Output directory: <output-dir>
   Interactive: false

   CRITICAL REQUIREMENTS:
   1. Execute ALL 5 steps of the adversarial protocol as defined in your system instructions.
   2. Write return-contract.yaml to <output-dir>/adversarial/return-contract.yaml as the FINAL step.
   3. The return-contract.yaml MUST contain these 9 fields:
      schema_version, status, convergence_score, merged_output_path, artifacts_dir,
      unresolved_conflicts, base_variant, failure_stage, fallback_mode.
   4. Set fallback_mode: false (this is a full pipeline execution, not a fallback).
   5. Write return-contract.yaml even on failure (status: failed, failure_stage: <step name>).
   6. Do NOT prompt for user input. All decisions are auto-resolved." \
  --append-system-prompt "${ADVERSARIAL_SKILL_CONTENT}" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --dangerously-skip-permissions \
  --output-format json \
  --max-budget-usd 2.00 \
  --model claude-sonnet-4-20250514 \
  2>/dev/null

# Restore environment
export CLAUDECODE="${CLAUDECODE_BACKUP}"
```

### 2.3 Parameter Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `--model` | `claude-sonnet-4-20250514` | Cost-effective for adversarial pipeline. Opus available via `--model claude-opus-4-20250514` for `--depth deep`. Model selection can be parameterized based on sc:roadmap's `--depth` flag. |
| `--allowedTools` | `Read,Write,Edit,Bash,Glob,Grep,Task` | Matches sc:adversarial's own `allowed-tools` minus `TodoWrite` (unnecessary in headless). `Task` enables sub-agent delegation within the adversarial pipeline. |
| `--max-budget-usd` | `2.00` (default), `5.00` (deep) | Cost guard. Abort if adversarial pipeline exceeds budget. Mapped from `--depth`: quick=1.00, standard=2.00, deep=5.00. |
| `--dangerously-skip-permissions` | present | Required for autonomous file writes to output directory. |
| `--output-format json` | present | Enables structured output parsing: `session_id`, `result`, `usage`, `cost_usd`. |

### 2.4 Output Capture and Parsing

The `--output-format json` flag produces output in this structure:

```json
{
  "session_id": "abc123...",
  "type": "result",
  "subtype": "success",
  "result": "Pipeline completed successfully...",
  "is_error": false,
  "duration_ms": 45000,
  "duration_api_ms": 42000,
  "num_turns": 15,
  "cost_usd": 1.23,
  "usage": {
    "input_tokens": 50000,
    "output_tokens": 25000
  }
}
```

**Parsing strategy**: The headless session output is captured as a Bash variable. The primary validation is NOT the JSON output but the **file-based return contract** at `<output-dir>/adversarial/return-contract.yaml`. The JSON output provides supplementary metadata (cost, duration, error status).

```bash
# Capture output
HEADLESS_OUTPUT=$(claude -p "..." --output-format json ... 2>/dev/null)
HEADLESS_EXIT_CODE=$?

# Parse exit code first
if [ $HEADLESS_EXIT_CODE -ne 0 ]; then
  echo "HEADLESS_ERROR: claude -p exited with code $HEADLESS_EXIT_CODE"
fi

# Check if return contract was written (primary validation)
if [ -f "<output-dir>/adversarial/return-contract.yaml" ]; then
  echo "HEADLESS_CONTRACT: found"
else
  echo "HEADLESS_CONTRACT: missing"
fi

# Extract cost from JSON output (supplementary)
HEADLESS_COST=$(echo "$HEADLESS_OUTPUT" | grep -o '"cost_usd":[0-9.]*' | cut -d: -f2)
echo "HEADLESS_COST: $HEADLESS_COST"
```

### 2.5 `CLAUDECODE=` Environment Variable Handling

Claude Code sets the `CLAUDECODE` environment variable in active sessions. If this variable is present when launching `claude -p`, the CLI may detect it as a nested invocation and refuse to start or behave unexpectedly.

**Mitigation**: Unset `CLAUDECODE` before invocation, restore after.

```bash
# Save and unset
CLAUDECODE_BACKUP="${CLAUDECODE:-}"
unset CLAUDECODE

# ... run claude -p ...

# Restore
if [ -n "$CLAUDECODE_BACKUP" ]; then
  export CLAUDECODE="$CLAUDECODE_BACKUP"
fi
```

This is handled within the Bash tool invocation, so it affects only the subprocess environment, not the parent sc:roadmap session.

### 2.6 Error Detection and Handling

| Error Condition | Detection Method | Handling |
|-----------------|------------------|----------|
| `claude` not in PATH | `which claude` returns non-zero | Abort with message; fall through to Task-agent fallback |
| Non-zero exit code | `$?` after invocation | Log error; check if return-contract.yaml was partially written |
| Timeout (>5 minutes) | Bash `timeout` command | Kill process; check partial artifacts |
| Permission denied | Exit code 126/127 | Abort; suggest `--dangerously-skip-permissions` |
| Malformed JSON output | JSON parse failure | Ignore JSON; rely on file-based contract |
| Cost exceeded | `--max-budget-usd` enforced by CLI | CLI self-terminates; check partial artifacts |
| Return contract missing | File existence check | Treat as `status: failed, failure_stage: transport` |
| Return contract malformed | YAML parse attempt | Treat as `status: failed, failure_stage: transport` |

---

## 3. Sprint-Spec Modifications

### Epic 1 Changes: Invocation Wiring Restoration

#### Task 0.0: Replace Skill Tool Probe with `claude -p` Viability Probe

**Current**: Dispatch a Task agent to test Skill tool cross-skill invocation.

**Proposed replacement**:

> **Task 0.0: `claude -p` Viability Probe (Pre-Implementation Gate)**
>
> **Goal**: Empirically confirm that `claude -p` can be launched from a Bash tool call within a Claude Code session and can execute a multi-step pipeline with file I/O.
>
> **Method**: Run 3 lightweight test invocations:
>
> 1. **Existence check**: `which claude && claude --version` -- confirms CLI is in PATH
> 2. **Basic invocation**: `CLAUDECODE= claude -p "Write the text 'hello' to /tmp/sc-probe-test.txt" --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.05` -- confirms basic headless execution with file I/O
> 3. **System prompt injection**: `CLAUDECODE= claude -p "List the sections defined in your system instructions. Write them to /tmp/sc-probe-sections.txt" --append-system-prompt "# Test Skill\n## Section A\nDo thing A.\n## Section B\nDo thing B." --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.10` -- confirms `--append-system-prompt` content is accessible
>
> **Decision gate**:
> - If **all 3 pass**: `claude -p` is viable as primary invocation. Proceed with Epic 1 as specified in this proposal.
> - If **test 1 fails**: `claude` CLI not installed. Abort `claude -p` approach. Revert to Task-agent fallback as sole mechanism (current SKILL.md behavior). Document installation requirement.
> - If **test 2 fails**: Headless mode broken or sandboxed. Investigate error. If permission issue, test with `--dangerously-skip-permissions`. If persistent, revert to fallback.
> - If **test 3 fails**: System prompt injection not working. Test with `--append-system-prompt` reading from file. If persistent, use explicit prompt reinforcement (include SKILL.md content in the `-p` prompt itself, not system prompt).
>
> **Time cost**: <10 minutes. **Blocks**: All subsequent tasks.

#### Tasks 1.1-1.2: `Skill` in allowed-tools

**Current**: Add `Skill` to allowed-tools in both `roadmap.md` and `SKILL.md`.

**Proposed modification**: These tasks are **retained but deprioritized**. The `Skill` tool remains in allowed-tools as a forward-compatibility measure (future Claude Code versions may support cross-skill invocation). However, `Bash` is now the critical tool for the `claude -p` invocation. `Bash` is already in the allowed-tools list for both files.

**Change to Task 1.1 AC**: Append: "Verify `Bash` is present in allowed-tools (required for `claude -p` invocation). It is already present in current files; confirm no accidental removal."

**Change to Task 1.2 AC**: Same addition.

#### Task 1.3: Complete Rewrite of Wave 2 Step 3d

**Current**: Step 3d is the fallback protocol with F1/F2-3/F4-5 Task-agent steps.

**Proposed**: Replace step 3d entirely with the `claude -p` headless invocation. The current fallback (F1, F2/3, F4/5) becomes the fallback for when `claude -p` itself fails. See Section 5 below for the exact specification text.

**New sub-step structure for 3d**:

- **3d-i [Construct headless invocation]**: Build the `claude -p` command string with all parameters derived from sc:roadmap context (spec path, agents, depth, output dir).
- **3d-ii [Execute headless session]**: Run via Bash tool with timeout guard.
- **3d-iii [Validate output]**: Check exit code, return-contract.yaml existence, YAML validity, and JSON output metadata.
- **3d-iv [Fallback if headless fails]**: If `claude -p` fails (CLI not found, non-zero exit, no return contract, cost exceeded), execute the current F1/F2-3/F4-5 Task-agent fallback. Emit: `"claude -p headless invocation failed — executing inline Task-agent fallback (fallback_mode: true)"`.

Steps 3e (consume return contract) and 3f (skip template) remain unchanged -- they operate on return-contract.yaml regardless of whether it was produced by `claude -p` or the Task-agent fallback.

#### Task 1.4: Fallback When Primary is `claude -p`

The fallback is the **existing F1/F2-3/F4-5 protocol** from the current SKILL.md. It is demoted from "sole mechanism" to "fallback for headless failure." The only change is:

- `fallback_mode: true` in return-contract.yaml (already specified)
- Additional `invocation_method: "task-agent-fallback"` field in return contract (new, informational)
- Emit message changes from `"sc:adversarial Skill tool unavailable"` to `"claude -p headless invocation failed"`

### Epic 2 Changes: Specification Rewrite

#### Task 2.1: Verb Glossary

**Addition**: New glossary entry:

| Verb | Tool | Description |
|------|------|-------------|
| **Launch headless session** | `Bash` tool with `claude -p` | Invoke a skill in an independent Claude session via headless CLI mode. The Bash tool executes the `claude -p` command; the headless session loads skill instructions via `--append-system-prompt`. |

Existing entries remain unchanged. The new entry clarifies that "Launch headless session" is a Bash tool operation, not a Skill tool operation.

#### Task 2.3: Wave 1A Step 2

**Current**: "Invoke sc:adversarial with `--compare` mode"

**Proposed**: Use the same `claude -p` pattern as Wave 2 step 3d, but with Mode A parameters:

```bash
claude -p \
  "Execute the sc:adversarial pipeline in Mode A (compare existing).
   Compare files: <spec-files>
   Depth: <depth>
   Output directory: <output-dir>
   Interactive: false
   ..." \
  --append-system-prompt "${ADVERSARIAL_SKILL_CONTENT}" \
  ...
```

The same 3d-i through 3d-iv sub-step pattern applies. The same fallback applies.

#### Task 2.4: adversarial-integration.md Changes

**Current plan**: Convert standalone pseudo-CLI syntax to Skill tool call format.

**Proposed modification**: Convert standalone pseudo-CLI syntax to `claude -p` invocation format instead.

The invocation pattern examples in `refs/adversarial-integration.md` currently show:
```
sc:adversarial --compare spec1.md,spec2.md --depth standard --output .dev/releases/current/auth-system/
```

These become:
```bash
# Headless invocation (primary)
claude -p "Execute sc:adversarial in Mode A. Compare: spec1.md,spec2.md. Depth: standard. Output: .dev/releases/current/auth-system/. Interactive: false." \
  --append-system-prompt "$(cat src/superclaude/skills/sc-adversarial/SKILL.md)" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --dangerously-skip-permissions --output-format json --max-budget-usd 2.00
```

**Verification Test 4 adaptation**: The grep pattern `sc:adversarial --` should now also fail to match (0 results), since invocations are wrapped in `claude -p` format. The test remains valid.

### Epic 3 Changes: Return Contract Transport

#### Task 3.1: Return Contract Write Instruction

**No change required**. The headless sc:adversarial session still writes `return-contract.yaml` as its final step. Whether the session was launched via Skill tool or `claude -p` is irrelevant to the producer side. The 9-field schema remains identical.

**One addition**: Add `invocation_method` as an optional 10th field:
```yaml
invocation_method: "headless-claude-p"  # or "task-agent-fallback" or "skill-tool"
```
This is informational (not routed on), but aids debugging.

#### Task 3.2: Return Contract Read Instruction

**No change required** to the consumption logic. The consumer reads `return-contract.yaml` regardless of how it was produced. Status routing, convergence thresholds, fallback_mode differentiation -- all remain identical.

**One addition**: If `invocation_method` field is present, log it in extraction.md for traceability:
```
Adversarial pipeline invocation method: headless-claude-p
```

#### Task 3.3: Tier 1 Artifact Existence Gate

**No structural change**. The 4-check gate (directory, diff-analysis.md, merged-output.md, return-contract.yaml) remains identical. The gate checks file existence regardless of how files were created.

**One addition**: Add a 5th preliminary check before the existing 4:

> **Check 0 (headless session health)**: If invocation was via `claude -p`, validate the JSON output captured from the headless session. If `is_error: true` in the JSON, log the error details before proceeding to artifact checks. This provides early diagnostic information even if artifacts were partially created.

---

## 4. New Infrastructure Needed

### 4.1 Reference File: `refs/headless-invocation.md`

**Recommendation: YES, create this file.**

This file centralizes the `claude -p` invocation pattern so it is defined once and referenced from both Wave 1A step 2 and Wave 2 step 3d. Without it, the invocation template would be duplicated in two places in SKILL.md.

**Proposed content outline**:

```markdown
# Headless Invocation Reference

Reference document for claude -p headless session invocation within sc:roadmap.

## Prerequisites
- `claude` CLI in PATH (validated in Wave 0)
- `CLAUDECODE` environment variable handling

## Invocation Template
- Mode A (compare): parameters, prompt template, flags
- Mode B (generate): parameters, prompt template, flags

## Parameter Mapping
- sc:roadmap --depth → --max-budget-usd mapping
- sc:roadmap --depth → --model mapping (optional)
- sc:roadmap --interactive → (always false in headless; interactive decisions are sc:roadmap's responsibility)

## Output Parsing
- JSON output structure
- Return contract validation

## Error Handling
- CLI not found, exit code, timeout, cost exceeded, contract missing

## Fallback Protocol
- When to fall back to Task-agent inline execution
- Transition: headless failure → F1/F2-3/F4-5

## Environment Variable Handling
- CLAUDECODE save/restore pattern
```

**Loaded in**: Wave 1A (when `--specs` present) and Wave 2 (when `--multi-roadmap` present) -- same loading points as `refs/adversarial-integration.md`.

### 4.2 sc:adversarial Changes for Headless Execution

**Minimal changes needed**. The sc:adversarial SKILL.md is already written as behavioral instructions for a Claude session. When injected via `--append-system-prompt`, the instructions work as-is.

**One consideration**: The SKILL.md frontmatter (`allowed-tools` line) is not parsed by `--append-system-prompt`. Tool access is controlled by the `--allowedTools` CLI flag instead. Ensure the `--allowedTools` value matches sc:adversarial's `allowed-tools` frontmatter.

**No changes to sc:adversarial SKILL.md are required** beyond the return contract additions already specified in Epic 3 Task 3.1.

### 4.3 Shell Script Wrapper vs. Inline Bash

**Recommendation: Inline Bash commands, not a shell script wrapper.**

Rationale:
- A shell script would need to be installed, versioned, and synced -- adding a new artifact to manage.
- The Bash tool can execute multi-line commands directly.
- The invocation is parameterized by sc:roadmap context (spec path, agents, depth, output dir), which is most naturally interpolated inline.
- If the invocation pattern stabilizes, a wrapper script can be extracted later (YAGNI).

The inline Bash commands are defined in `refs/headless-invocation.md` as templates. The sc:roadmap skill reads the ref and constructs the actual command with runtime parameters.

---

## 5. The Exact Wave 2 Step 3d Rewrite

This is the specification text that would replace the current step 3d in `src/superclaude/skills/sc-roadmap/SKILL.md`:

---

> **3d [Launch headless adversarial session]**: Use the `claude -p` headless CLI to invoke sc:adversarial in a separate session with full pipeline execution. Read `refs/headless-invocation.md` for the invocation template and parameter mapping.
>
> **3d-i [Construct invocation command]**: Build the headless invocation command using the Mode B template from `refs/headless-invocation.md`:
>
> ```bash
> # Save and unset CLAUDECODE to prevent nested session detection
> CLAUDECODE_BACKUP="${CLAUDECODE:-}" && unset CLAUDECODE
>
> # Read sc:adversarial SKILL.md for system prompt injection
> SKILL_CONTENT=$(cat src/superclaude/skills/sc-adversarial/SKILL.md)
>
> # Compute budget from depth: quick=1.00, standard=2.00, deep=5.00
> BUDGET="<computed-from-depth>"
>
> # Compute model from depth (optional): quick/standard=sonnet, deep=opus
> MODEL="<computed-from-depth>"
>
> # Build prompt with runtime parameters
> PROMPT="Execute the sc:adversarial pipeline in Mode B (generate + compare from source).
>
> Parameters:
> - Source file: <spec-file-path>
> - Generate type: roadmap
> - Agents: <expanded-agent-specs-comma-separated>
> - Depth: <depth>
> - Output directory: <output-dir>
> - Interactive: false
> - Convergence threshold: 0.80
>
> MANDATORY REQUIREMENTS:
> 1. Execute ALL 5 steps of the adversarial protocol defined in your system instructions.
> 2. Create the output directory structure: <output-dir>/adversarial/
> 3. Write ALL intermediate artifacts (variant files, diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged output).
> 4. As the ABSOLUTE FINAL step, write <output-dir>/adversarial/return-contract.yaml with ALL 9 required fields: schema_version (1.0), status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts, base_variant, failure_stage, fallback_mode (false).
> 5. If ANY step fails, still write return-contract.yaml with status: failed and failure_stage set to the failed step name.
> 6. Do NOT prompt for user input. All decisions are auto-resolved.
> 7. Use YAML null (~) for fields not reached during failed runs."
> ```
>
> **Parameter substitution**: Replace `<spec-file-path>`, `<expanded-agent-specs-comma-separated>`, `<depth>`, `<output-dir>`, `<computed-from-depth>` with values from the current sc:roadmap execution context. Agent specs must be in expanded form (model-only agents already filled with primary persona from step 3b).
>
> **3d-ii [Execute headless session]**: Use the `Bash` tool to execute the constructed command with a timeout guard:
>
> ```bash
> HEADLESS_OUTPUT=$(timeout 300 claude -p "${PROMPT}" \
>   --append-system-prompt "${SKILL_CONTENT}" \
>   --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
>   --dangerously-skip-permissions \
>   --output-format json \
>   --max-budget-usd "${BUDGET}" \
>   --model "${MODEL}" \
>   2>/dev/null)
> HEADLESS_EXIT=$?
>
> # Restore environment
> if [ -n "$CLAUDECODE_BACKUP" ]; then
>   export CLAUDECODE="$CLAUDECODE_BACKUP"
> fi
> ```
>
> **Timeout**: 300 seconds (5 minutes) for quick/standard depth; 600 seconds (10 minutes) for deep depth. If the process exceeds the timeout, it is terminated via SIGTERM.
>
> **3d-iii [Validate headless output]**: Perform validation in this order:
>
> 1. **Exit code check**: If `HEADLESS_EXIT` is non-zero:
>    - Exit 124 = timeout. Emit: `"claude -p timed out after <N> seconds."`. Proceed to artifact check (partial output may exist).
>    - Exit 126/127 = command not found or permission denied. Emit: `"claude -p failed: command not found or permission denied (exit <N>)."`. Proceed to fallback (3d-iv).
>    - Other non-zero = general failure. Emit: `"claude -p failed with exit code <N>."`. Proceed to artifact check.
>
> 2. **JSON output parse** (informational): If `HEADLESS_OUTPUT` is non-empty, attempt to extract `is_error`, `cost_usd`, and `duration_ms`. Log: `"Headless session: cost=$<cost>, duration=<duration>ms, error=<is_error>"`. If `is_error` is true, log the error details. This is informational only -- the file-based contract is the primary validation.
>
> 3. **Return contract existence**: Check if `<output-dir>/adversarial/return-contract.yaml` exists.
>    - If exists: proceed to step 3e (consume return contract). The headless invocation succeeded (at least partially).
>    - If missing: check if `<output-dir>/adversarial/` directory exists.
>      - Directory exists but no contract: Pipeline started but failed before writing contract. Emit: `"Headless session completed but return-contract.yaml not written. Pipeline may have failed mid-execution."`. Proceed to fallback (3d-iv).
>      - Directory missing: Pipeline did not start. Proceed to fallback (3d-iv).
>
> 4. **Cost guard**: If `cost_usd` was extracted from JSON and exceeds `BUDGET * 1.5` (50% overshoot tolerance), emit warning: `"Headless session cost ($<cost>) exceeded budget ($<BUDGET>) by >50%. Review adversarial pipeline cost."`. This is a warning, not an abort (the work is already done).
>
> **3d-iv [Fallback: inline Task-agent execution]**: If step 3d-iii determines the headless invocation failed (CLI not found, no return contract, no artifacts directory), execute the current fallback protocol. Emit: `"claude -p headless invocation failed — executing inline Task-agent fallback (fallback_mode: true)"`.
>
> The fallback protocol is identical to the current F1/F2-3/F4-5 steps:
> - **F1 [Variant generation]**: Use `Task` tool to dispatch one generation agent per expanded agent spec. Each agent receives: source spec file path, assigned model and persona, and instruction to generate a complete roadmap variant. Each variant must contain >=100 words in its analysis sections. Write each variant to `<output_dir>/variant-<model>-<persona>.md`. F1 must produce >=2 variant files.
> - **F2/3 [Diff analysis + single-round debate]**: Use `Task` tool to read all variants, write diff-analysis.md with per-variant summaries and conflict summary, conduct one debate round. Minimum: diff-analysis.md >=100 words.
> - **F4/5 [Base selection + merge + contract]**: Use `Task` tool to score variants, select base, write merged-output.md, and write return-contract.yaml with `status: partial, fallback_mode: true, convergence_score: 0.5` (estimated, not measured).
>
> After fallback completes, proceed to step 3e (consume return contract) regardless of whether the contract was produced by headless session or fallback.

---

## 6. Risk Analysis

### R-NEW-1: `claude -p` Reliability for Complex Multi-Step Pipelines

**Probability**: MEDIUM (0.35)
**Impact**: HIGH -- full adversarial pipeline may not execute correctly in headless mode

**Concern**: The sc:adversarial pipeline is a complex 5-step protocol with sub-agent delegation (advocate agents, debate orchestrator, merge executor). In headless mode, all of this must execute autonomously without human oversight. The `--append-system-prompt` SKILL.md may be too long or complex for reliable behavioral compliance.

**Mitigation**:
- The `-p` prompt includes explicit MANDATORY REQUIREMENTS that reinforce the most critical behaviors (write return contract, execute all 5 steps).
- The `--output-format json` output provides `is_error` and `num_turns` for post-hoc diagnostics.
- The Task-agent fallback (3d-iv) provides a degraded but functional path.
- Progressive adoption: start with `--depth quick` (1 debate round) to validate, then expand to standard/deep.

### R-NEW-2: Cost Unpredictability

**Probability**: MEDIUM (0.30)
**Impact**: MEDIUM -- unexpected costs accumulate across invocations

**Concern**: Each `claude -p` invocation is an independent session with its own token budget. The adversarial pipeline can be token-intensive (multiple full-text variants, multi-round debates). Cost depends on variant count, debate depth, and spec complexity.

**Mitigation**:
- `--max-budget-usd` provides a hard ceiling per invocation.
- Depth-based budget mapping: quick=$1, standard=$2, deep=$5.
- JSON output includes `cost_usd` for post-hoc tracking.
- Cost guard in 3d-iii warns on >50% budget overshoot.
- sc:roadmap can log cumulative adversarial costs in roadmap.md frontmatter for transparency.

### R-NEW-3: Context Window Limits in Headless Sessions

**Probability**: LOW-MEDIUM (0.25)
**Impact**: HIGH -- pipeline fails silently when context exhausted

**Concern**: The headless session has its own context window. The `--append-system-prompt` with full SKILL.md (~1,700 lines, ~45K tokens) consumes significant context before any pipeline work begins. With 5+ variants of substantial specs, the context may be exhausted during debate rounds.

**Mitigation**:
- Consider trimming SKILL.md for headless injection: include only the core protocol sections (Steps 1-5, Return Contract, Error Handling), exclude Implementation Details sections that add ~1,000 lines.
- The `--model` flag can select models with larger context windows.
- Document recommended spec size limits for adversarial mode.
- Context exhaustion typically causes the session to end early -- the return contract may not be written, triggering the file-existence guard and fallback.

### R-NEW-4: Permission/Sandbox Concerns

**Probability**: LOW (0.15)
**Impact**: HIGH -- headless session cannot write files

**Concern**: `claude -p` runs in a subprocess. Depending on the environment (Docker container, restricted user, filesystem permissions), the headless session may not have write access to the output directory.

**Mitigation**:
- `--dangerously-skip-permissions` bypasses Claude Code's permission system (not OS permissions).
- Wave 0 already validates output directory is writable -- the parent session has access. The child session inherits the same filesystem permissions.
- The viability probe (Task 0.0 test 2) validates file I/O capability before any pipeline work begins.

### R-NEW-5: `claude` CLI Not Installed or Not in PATH

**Probability**: LOW (0.10) in Claude Code environments, MEDIUM (0.40) in custom installations
**Impact**: HIGH -- primary invocation path completely blocked

**Concern**: `claude -p` requires the Claude Code CLI to be installed. In standard Claude Code environments (VS Code extension, web IDE), it should be available. In custom or self-hosted environments, it may not be.

**Mitigation**:
- Task 0.0 test 1 (`which claude && claude --version`) validates availability before any pipeline work.
- If not available, the fallback (3d-iv) activates automatically.
- Documentation should note the CLI requirement.

### R-NEW-6: Session Nesting Detection

**Probability**: LOW (0.15)
**Impact**: MEDIUM -- headless session refuses to start

**Concern**: Even with `CLAUDECODE` unset, future Claude Code versions may detect nested sessions via other mechanisms (process tree inspection, lock files).

**Mitigation**:
- The `CLAUDECODE` unset pattern handles the known detection mechanism.
- The viability probe (Task 0.0 test 2) detects this failure mode before pipeline execution.
- If nested detection evolves, the fallback path remains available.

### Risk Comparison: `claude -p` vs. Current Fallback

| Dimension | `claude -p` (primary) | Task-agent fallback | Assessment |
|-----------|----------------------|---------------------|------------|
| Pipeline fidelity | Full 5-step protocol | Compressed 3-step approximation | `claude -p` substantially better |
| Convergence measurement | Real (computed from debate) | Fixed sentinel 0.5 | `claude -p` substantially better |
| Context consumption | Separate context window | Shares sc:roadmap's context | `claude -p` better |
| Cost visibility | JSON output with cost_usd | No visibility | `claude -p` better |
| Reliability | Depends on CLI availability | Always available (Task tool) | Fallback better |
| Latency | Higher (session startup overhead) | Lower (inline execution) | Fallback better |
| Debugging | Separate session (harder to inspect) | Same session (easier) | Fallback better |

**Net assessment**: `claude -p` provides meaningfully higher quality output at the cost of an additional failure mode (CLI availability). The Task-agent fallback fully covers the failure mode. This is a sound architecture: high-quality primary path with a degraded but functional fallback.

---

## 7. Verification Plan

### Probe Test (Replaces Task 0.0)

**Purpose**: Confirm `claude -p` is viable as an invocation mechanism.

**Method**: 3 lightweight tests as specified in Section 3 (Task 0.0 replacement).

**Pass criteria**:
1. `which claude` returns 0, `claude --version` outputs version string
2. Basic invocation writes file successfully, JSON output is parseable
3. System prompt injection: headless session can reference injected content

**Time**: <10 minutes.
**Cost**: <$0.20 (two minimal invocations).

### Structural Audit (Adapts Test 2)

**Purpose**: Confirm Wave 2 step 3 rewrite meets the specification.

**Method**: Manual inspection checklist.

1. Count sub-steps in Wave 2 step 3. Expected: 6 (3a through 3f).
2. Verify step 3d contains 4 sub-steps: 3d-i (construct), 3d-ii (execute), 3d-iii (validate), 3d-iv (fallback).
3. Verify step 3d-i references `refs/headless-invocation.md`.
4. Verify step 3d-ii uses `Bash` tool with `timeout` command.
5. Verify step 3d-iii checks: exit code, JSON parse, contract existence, cost guard (4 checks).
6. Verify step 3d-iv contains the F1/F2-3/F4-5 fallback protocol.
7. Verify step 3e (return contract consumption) is unchanged from current spec.
8. Verify step 3f (skip template) is unchanged.
9. Verify verb glossary contains "Launch headless session" entry.

**Time**: <15 minutes.

### End-to-End Test (Adapts Test 5)

**Purpose**: Confirm the full invocation chain works: sc:roadmap -> Bash(claude -p) -> sc:adversarial -> return-contract.yaml -> sc:roadmap consumption.

**Method**: Run `sc:roadmap --multi-roadmap --agents opus,sonnet` on a test spec and verify:

1. `claude -p` is invoked (check Bash tool call in session log)
2. A separate headless session executes (check JSON output for `session_id`)
3. Adversarial pipeline artifacts are produced in `<output-dir>/adversarial/`:
   - variant-*.md files (>= 2)
   - diff-analysis.md
   - debate-transcript.md
   - base-selection.md
   - refactor-plan.md
   - merge-log.md
   - merged-output.md (or equivalent named file)
4. `return-contract.yaml` exists with valid 9-field schema
5. `convergence_score` is a computed value (not the fixed 0.5 sentinel from fallback)
6. `fallback_mode: false` (confirming full pipeline, not fallback)
7. sc:roadmap reads the contract and routes on status field
8. Final roadmap.md frontmatter contains adversarial block with measured convergence

**Fallback verification** (separate test): Temporarily rename `claude` binary (or use a non-existent path), run the same invocation, and verify:
1. Fallback activates with appropriate warning message
2. F1/F2-3/F4-5 execute inline
3. `return-contract.yaml` written with `fallback_mode: true` and `convergence_score: 0.5`

**Time**: 30-60 minutes.
**Cost**: ~$2-5 for full pipeline execution.

---

## 8. Summary of All Sprint-Spec Modifications

| Sprint-Spec Section | Change Type | Description |
|---------------------|-------------|-------------|
| Task 0.0 | **Replace** | Skill tool probe -> `claude -p` viability probe (3 tests) |
| Task 1.1 AC | **Append** | Verify `Bash` in allowed-tools |
| Task 1.2 AC | **Append** | Verify `Bash` in allowed-tools |
| Task 1.3 step 3d | **Rewrite** | Fallback-only -> headless primary + fallback |
| Task 1.4 | **Demote** | "Sole mechanism" -> "Fallback for headless failure" |
| Task 2.1 glossary | **Add entry** | "Launch headless session" = Bash + claude -p |
| Task 2.3 Wave 1A | **Rewrite** | "Invoke" -> headless invocation pattern |
| Task 2.4 conversion | **Adapt** | Pseudo-CLI -> claude -p format (not Skill tool format) |
| Task 3.1 schema | **Add field** | `invocation_method` (optional, informational) |
| Task 3.3 gate | **Add check** | Check 0: headless JSON health (before artifact checks) |
| Fallback-Only Variant | **Remove** | No longer needed; fallback is always available as secondary |
| Risk Register | **Add 6 risks** | R-NEW-1 through R-NEW-6 |
| Verification Test 5 | **Adapt** | Add headless-specific checks |
| New: refs/ file | **Create** | `refs/headless-invocation.md` |
| Wave loading table | **Update** | Wave 1A and Wave 2 load `refs/headless-invocation.md` |

---

## 9. Decision Points for Sprint Planning

1. **SKILL.md trimming for headless injection**: Should the full 1,700-line sc:adversarial SKILL.md be injected via `--append-system-prompt`, or should a trimmed version (~500 lines, core protocol only) be created as `refs/adversarial-headless.md`? Trimming reduces context consumption but introduces a maintenance burden (two versions of the protocol).

2. **Model selection strategy**: Should the headless session always use the same model as the parent sc:roadmap session, or should it be independently configured? Recommendation: independent, with depth-based defaults (sonnet for quick/standard, opus for deep).

3. **Concurrent headless sessions**: If sc:roadmap's combined mode triggers both Wave 1A and Wave 2 adversarial invocations, these are sequential (Wave 1A must complete before Wave 2). No concurrency concerns for the current design. However, if future modes allow parallel adversarial invocations, output directory namespacing (already handled by `<output-dir>`) prevents conflicts.

4. **Retry policy**: Should a failed `claude -p` invocation be retried once before falling back to Task-agent execution? Recommendation: no retry (the failure is likely deterministic -- CLI not available, permission issue). Proceed directly to fallback.

---

*Proposal generated 2026-02-23. Analyst: claude-opus-4-6 (system-architect persona).*
*Inputs: sprint-spec.md, sc-roadmap/SKILL.md, sc-adversarial/SKILL.md, adversarial-integration.md, tasklist-P6.md.*
*Approach: claude -p as primary invocation with Task-agent fallback.*
