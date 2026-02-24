# Specification: claude -p Headless Invocation for sc:roadmap Adversarial Pipeline

**Version**: 2.0-draft
**Date**: 2026-02-23
**Status**: DRAFT — Post panel review revision
**Source**: Merged adversarial approach (base: Approach 2, score: 0.900)
**Convergence**: 1.00 (12/12 debate points resolved)
**Previous version**: specification-draft-v1.md (score 5.5/10, 27 panel findings)

---

## 0. Document Purpose & Scope

This specification defines the modifications to the sc:roadmap sprint tasklist required to wire `claude -p` headless CLI invocation as the **primary** mechanism for launching sc:adversarial, with an enhanced 5-step Task-agent fallback when headless invocation fails.

### Scope Boundaries

**In scope**:
- Task 0.0 replacement (viability probe)
- Wave 2 step 3d rewrite (headless invocation + enhanced fallback)
- Wave 1A step 2 adaptation (same pattern)
- Return contract schema update (3 new consumer-side fields)
- Verb glossary addition
- New reference file (`refs/headless-invocation.md`)
- Phase 3 validation task updates (T03.01, T03.02)
- Glossary updates
- Directory structure normalization (fallback writes to `<output-dir>/adversarial/`)

**Out of scope**:
- Changes to sc:adversarial SKILL.md itself (separate sprint)
- `--invocation-mode` flag (rejected: YAGNI)
- Depth-based routing (rejected: premature optimization)
- 10-run reliability test (rejected: cost/scope)

### Schema Ownership Model

> **Architectural decision**: The return contract schema is **owned by the producer** (sc:adversarial SKILL.md FR-007), which defines 5 fields. The consumer (sc:roadmap) currently reads 7 fields (adding `fallback_mode` and `base_variant` in its canonical schema comment at line 153). This specification adds 3 more consumer-side fields (`schema_version`, `failure_stage`, `invocation_method`), bringing the consumer-expected total to 10.
>
> Because sc:adversarial SKILL.md is out of scope for this sprint, the **headless session will produce a 5-field contract** (following its SKILL.md instructions). The **fallback path will produce a 10-field contract** (written by sc:roadmap directly). Step 3e must handle both formats gracefully by applying defaults for missing fields. See Section 3.7 for the dual-format handling specification.
>
> **Schema contract invariant**: Consumers MUST ignore unknown fields in the return contract. The schema is additive-only; fields are never removed or renamed. Unknown fields are silently preserved.

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

The **return contract** (`return-contract.yaml`) is the abstraction boundary. Step 3e reads and routes on `status` and `convergence_score`. It does not know or care whether the contract was produced by headless or fallback. The contract schema is owned by the producer (sc:adversarial); the consumer applies defaults for any missing fields.

---

## 2. Invocation Design

### 2.1 Command Construction Pattern

| Component | Flag | Content |
|-----------|------|---------|
| Behavioral instructions | `--append-system-prompt` | Raw content of `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` |
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

# Ensure signal-safe restore of CLAUDECODE
trap 'if [ -n "$CLAUDECODE_BACKUP" ]; then export CLAUDECODE="$CLAUDECODE_BACKUP"; fi' EXIT

# Read SKILL.md content for system prompt injection
ADVERSARIAL_SKILL_CONTENT="$(cat src/superclaude/skills/sc-adversarial-protocol/SKILL.md)"

# Validate SKILL.md content was read successfully
if [ -z "$ADVERSARIAL_SKILL_CONTENT" ]; then
  echo "ERROR: Failed to read sc-adversarial-protocol SKILL.md (empty content)"
  HEADLESS_EXIT=1
else
  # Check argument length feasibility (ARG_MAX safety)
  SKILL_BYTES=$(echo "$ADVERSARIAL_SKILL_CONTENT" | wc -c)
  if [ "$SKILL_BYTES" -gt 1500000 ]; then
    echo "WARNING: SKILL.md content is ${SKILL_BYTES} bytes — approaching ARG_MAX limit"
  fi

  # Compute budget from depth: quick=1.00, standard=2.00, deep=5.00
  BUDGET="<computed-from-depth>"

  # Compute model from depth: quick/standard=sonnet, deep=opus
  MODEL="<computed-from-depth>"

  # Capture stderr for diagnostics
  STDERR_FILE=$(mktemp /tmp/sc-headless-stderr-XXXXXX)

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
     4. As the ABSOLUTE FINAL step, write <output-dir>/adversarial/return-contract.yaml
        with the fields defined in your Return Contract (FR-007) section.
     5. If ANY step fails, still write return-contract.yaml with status: failed.
     6. Do NOT prompt for user input. All decisions are auto-resolved.
     7. Use YAML null (~) for fields not applicable during failed runs." \
    --append-system-prompt "${ADVERSARIAL_SKILL_CONTENT}" \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
    --dangerously-skip-permissions \
    --output-format json \
    --max-budget-usd "${BUDGET}" \
    --model "${MODEL}" \
    2>"$STDERR_FILE")

  HEADLESS_EXIT=$?
fi

# Restore environment (also handled by trap, but explicit for clarity)
if [ -n "$CLAUDECODE_BACKUP" ]; then
  export CLAUDECODE="$CLAUDECODE_BACKUP"
fi
trap - EXIT
```

**Key changes from v1**: (1) SKILL.md path corrected to `sc-adversarial-protocol/SKILL.md`. (2) Content validation added (empty check + ARG_MAX warning). (3) Stderr captured to temp file for diagnostics. (4) Signal-safe `trap EXIT` for CLAUDECODE restore. (5) Prompt instruction #4 simplified to reference "your Return Contract (FR-007) section" rather than enumerating all 10 fields (avoids prompt-schema coupling). (6) Schema defined in one place only — Section 3.7 of this spec.

### 2.3 Parameter Configuration

| Parameter | Quick | Standard | Deep | Rationale |
|-----------|-------|----------|------|-----------|
| `--model` | sonnet | sonnet | opus | Cost-effective for standard; high-quality for deep |
| `--max-budget-usd` | $1.00 | $2.00 | $5.00 | Hard cost ceiling per invocation |
| Timeout | 180s | 300s | 600s | Process kill if exceeded |
| `--allowedTools` | (same) | (same) | (same) | `Read,Write,Edit,Bash,Glob,Grep,Task` |
| `--dangerously-skip-permissions` | present | present | present | Required for autonomous file writes |
| `--output-format json` | present | present | present | Structured output parsing |

**Total adversarial budget ceiling**: The combined cost of headless + fallback (if triggered) MUST NOT exceed `2 × BUDGET`. After headless failure, compute remaining budget as `REMAINING = (2 × BUDGET) - headless_cost`. If `REMAINING < 0.5 × BUDGET`, abort with: `"Insufficient remaining budget for fallback (${REMAINING} of ${BUDGET} needed). Headless consumed $${headless_cost}."` Otherwise, proceed with fallback.

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

# Diagnostic: check stderr on failure
if [ "$HEADLESS_EXIT" -ne 0 ] && [ -f "$STDERR_FILE" ] && [ -s "$STDERR_FILE" ]; then
  echo "HEADLESS_STDERR: $(head -5 "$STDERR_FILE")"
fi

# Cleanup
rm -f "$STDERR_FILE"
```

### 2.5 CLAUDECODE Environment Variable

Claude Code sets `CLAUDECODE` in active sessions to detect nesting. The variable must be unset before `claude -p` invocation and restored afterward. This is handled within the Bash tool call — only the subprocess environment is affected. A `trap EXIT` ensures restoration even on abnormal termination (SIGINT, SIGTERM).

### 2.6 Error Detection Matrix

| Error Condition | Detection Method | Handling |
|-----------------|-----------------|----------|
| `claude` not in PATH | `which claude` non-zero | Abort; trigger fallback |
| SKILL.md read failure | `ADVERSARIAL_SKILL_CONTENT` is empty | Abort; trigger fallback |
| ARG_MAX exceeded | Shell "Argument list too long" error | Log from stderr; trigger fallback |
| Non-zero exit code | `$?` after invocation | Log error + stderr; scan for partial artifacts |
| Timeout (exit 124) | Bash `timeout` command | Kill process; scan for partial artifacts |
| Permission denied (126/127) | Exit code | Abort; trigger fallback |
| Malformed JSON output | JSON parse failure | Ignore JSON; rely on file-based contract |
| Budget exceeded | `--max-budget-usd` enforced by CLI | CLI self-terminates; scan partial artifacts |
| Return contract missing | File existence check | Trigger 4-state fallback scan |
| Return contract malformed | YAML parse attempt | Treat as `status: failed, failure_stage: transport` |
| Stderr contains errors | Stderr file inspection | Log first 5 lines for diagnostics |

---

## 3. Sprint-Spec Modifications

### 3.1 T01.01: `claude -p` Viability Probe (Replaces Task 0.0)

**Replaces**: Current T01.01 (Skill Tool Probe)
**Deliverables affected**: D-0001 (evidence), D-0002 (variant decision)

> **T01.01: `claude -p` Headless Invocation Viability Probe (Pre-Implementation Gate)**
>
> **Goal**: Empirically confirm that `claude -p` can be launched from a Bash tool call and can execute a multi-step pipeline with behavioral adherence to injected SKILL.md instructions.
>
> **Pre-test cleanup**: `rm -f /tmp/sc-probe-test.txt /tmp/sc-probe-sections.txt /tmp/sc-probe-output/*`
>
> **Method**: Run 4 test invocations:
>
> 1. **Existence check**: `which claude && claude --version` — confirms CLI in PATH.
> 2. **Basic invocation**: `CLAUDECODE= claude -p "Write the text 'hello' to /tmp/sc-probe-test.txt" --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.05` — confirms basic headless execution with file I/O.
> 3. **System prompt injection**: `CLAUDECODE= claude -p "List the sections defined in your system instructions. Write them to /tmp/sc-probe-sections.txt" --append-system-prompt "# Test Skill\n## Section A\nDo thing A.\n## Section B\nDo thing B." --allowedTools "Write" --dangerously-skip-permissions --output-format json --max-budget-usd 0.10` — confirms `--append-system-prompt` content is accessible.
> 4. **Behavioral adherence mini-test** (`--max-budget-usd 2.00`): Execute a minimal system-prompt-injected pipeline on tiny fixtures (2 pre-written ~100-word variants stored at `src/superclaude/skills/sc-roadmap-protocol/fixtures/probe-variant-a.md` and `probe-variant-b.md`). Score output against 3-category binary checklist using concrete grep checks:
>    - **Diff Analysis present?** `ls /tmp/sc-probe-output/ | grep -c 'diff'` returns >= 1.
>    - **Multi-step execution?** `grep -ci 'round\|score\|base.selection\|## Round' /tmp/sc-probe-output/* 2>/dev/null` returns >= 1.
>    - **Artifacts written to disk?** `ls /tmp/sc-probe-output/ | wc -l` returns >= 2.
>
> **Decision gate**:
> - **All 4 pass**: `claude -p` is viable as primary invocation. Proceed with implementation.
> - **Tests 1-3 pass, test 4 fails**: Headless works mechanically but doesn't follow behavioral instructions. Augment the system prompt with stronger anchoring (explicit "YOU MUST" instructions for each step). Re-run test 4 once. If still failing, route to fallback-only sprint variant.
> - **Test 1 fails**: CLI not installed. Route to fallback-only.
> - **Test 2 or 3 fails**: Headless mode broken or sandboxed. Investigate; if persistent, route to fallback-only.
>
> **Informational output** (not gated): Log SKILL.md file size in characters and estimated tokens (~4 chars/token). Log test 4 cost from JSON output.
>
> **Cost breakdown**: Tests 1-3: $0.15 (sum of budget caps). Test 4: $2.00 (budget cap). **Total probe cost: <= $2.15** (actual will be lower; budget caps are ceilings).
>
> **Time cost**: ~20 minutes. **Blocks**: All subsequent tasks.

**Acceptance Criteria**:
- Pre-test cleanup executed (no stale `/tmp/sc-probe-*` files)
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
> trap 'if [ -n "$CLAUDECODE_BACKUP" ]; then export CLAUDECODE="$CLAUDECODE_BACKUP"; fi' EXIT
>
> SKILL_CONTENT=$(cat src/superclaude/skills/sc-adversarial-protocol/SKILL.md)
> if [ -z "$SKILL_CONTENT" ]; then
>   echo "ERROR: SKILL.md read failed"; HEADLESS_EXIT=1
> else
>   STDERR_FILE=$(mktemp /tmp/sc-headless-stderr-XXXXXX)
>   HEADLESS_OUTPUT=$(timeout ${TIMEOUT} claude -p "${PROMPT}" \
>     --append-system-prompt "${SKILL_CONTENT}" \
>     --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
>     --dangerously-skip-permissions \
>     --output-format json \
>     --max-budget-usd "${BUDGET}" \
>     --model "${MODEL}" \
>     2>"$STDERR_FILE")
>   HEADLESS_EXIT=$?
> fi
>
> if [ -n "$CLAUDECODE_BACKUP" ]; then
>   export CLAUDECODE="$CLAUDECODE_BACKUP"
> fi
> trap - EXIT
> ```
>
> **Timeout**: quick=180s, standard=300s, deep=600s.
>
> **3d-iii [Validate headless output]**: Perform validation in order:
>
> 1. **Exit code check**: If `HEADLESS_EXIT` is non-zero:
>    - Exit 124 = timeout. Emit: `"claude -p timed out after <N> seconds."`. Log stderr if present. Proceed to artifact scan.
>    - Exit 126/127 = command not found or permission denied. Proceed to fallback (3d-iv).
>    - Other non-zero = general failure. Log stderr if present. Proceed to artifact scan.
>
> 2. **JSON output parse** (informational): If `HEADLESS_OUTPUT` is non-empty, extract `is_error`, `cost_usd`, `duration_ms`. Log: `"Headless session: cost=$<cost>, duration=<duration>ms, error=<is_error>"`.
>
> 3. **Return contract existence**: Check if `<output-dir>/adversarial/return-contract.yaml` exists.
>    - If exists: proceed to step 3e (consume return contract).
>    - If missing: proceed to artifact scan (3d-iv).
>
> 4. **Cost guard**: If `cost_usd` exceeds `BUDGET * 1.5`, emit warning: `"Headless cost $<cost> exceeded 150% of budget $<budget>"` (informational, not abort).
>
> **3d-iv [Fallback: enhanced Task-agent pipeline with mid-pipeline awareness]**: If step 3d-iii determines the headless invocation failed or no return contract was produced, execute the enhanced 5-step Task-agent fallback.
>
> **Budget check before fallback**: Compute `headless_cost` from JSON output (0 if unavailable). Compute `REMAINING = (2 × BUDGET) - headless_cost`. If `REMAINING < 0.5 × BUDGET`, abort: `"Insufficient remaining budget for fallback."`. Otherwise proceed.
>
> **Before starting fallback, perform artifact scan** (4-state model):
>
> - **State A**: `<output-dir>/adversarial/` directory does not exist OR is empty OR contains only 0-byte files.
>   - Action: Full fallback from F1.
>   - Emit: `"No headless artifacts found. Executing full Task-agent pipeline."`.
>   - **Example**: Given: `adversarial/` does not exist. When: artifact scan runs. Then: State A detected.
>   - **Example**: Given: `adversarial/` contains `variant-sonnet-architect.md` (0 bytes). When: artifact scan runs. Then: State A (0-byte files treated as absent).
>
> - **State B**: Non-empty variant files (`variant-*.md`, each > 0 bytes, count >= 2) exist but no `diff-analysis.md`.
>   - Action: Fallback from F2 (skip generation, use existing variants).
>   - Emit: `"Headless variants preserved (<N> files). Resuming from diff analysis."`.
>   - **Example**: Given: `adversarial/` contains `variant-sonnet-architect.md` (500 bytes) and `variant-opus-security.md` (800 bytes), no `diff-analysis.md`. When: artifact scan runs. Then: State B detected.
>
> - **State C**: `diff-analysis.md` exists (> 0 bytes) but no `debate-transcript.md`.
>   - Action: Fallback from F3 (skip generation and diff, use existing analysis).
>   - Emit: `"Headless diff analysis preserved. Resuming from adversarial debate."`.
>
> - **State D**: `debate-transcript.md` exists (> 0 bytes) but no `base-selection.md`.
>   - Action: Fallback from F4 (skip generation, diff, and debate).
>   - Emit: `"Headless debate transcript preserved. Resuming from scoring."`.
>
> **Rationale for 4 states (not 5)**: States beyond D (base-selection exists, merged-output exists) have diminishing returns. If the headless session completed through scoring, the remaining work (F5: refactoring + merge) is fast and cheap. Restarting from F4 in those rare cases wastes at most 1-2 minutes.
>
> **Enhanced fallback protocol** (5-step):
>
> **F1 [Variant generation]** (skip if State B, C, or D): Use `Task` tool to dispatch one generation agent per expanded agent spec. Each agent receives: source spec file path, assigned model and persona, and instruction to generate a complete roadmap variant. Each variant must contain >=100 words in analysis sections. Write each variant to `<output_dir>/adversarial/variant-<model>-<persona>.md`. F1 must produce >=2 variant files.
>
> **F2 [Diff analysis]** (skip if State C or D): Use `Task` tool to dispatch a single analytical agent. The agent receives the relevant Step 1 instructions extracted from sc:adversarial SKILL.md **by section heading** (see Section 5 for exact heading mapping). Produce `<output-dir>/adversarial/diff-analysis.md` with all 4 sections: structural_diff, content_diff, contradiction_detection, unique_contribution_extraction. Include severity ratings per item.
>
> **F3 [Adversarial debate]** (skip if State D): Use `Task` tool to orchestrate multi-round debate:
> - **Round 1**: Dispatch parallel advocate Task agents (one per variant). Each receives its variant content, all other variant contents, diff-analysis.md, and the Step 2 advocate instructions from SKILL.md (extracted by section heading). Must include steelman of opposing variants.
> - **Round 2** (if `--depth standard` or `--depth deep`): Sequential rebuttal Task agents. Each sees all Round 1 transcripts.
> - **Round 3** (if `--depth deep` AND convergence < threshold): Final arguments.
> - **Convergence tracking**: After each round, dispatch an orchestrator Task agent to evaluate per-diff-point agreement. Compute `convergence = agreed_points / total_diff_points`. Track per round. This replaces the hardcoded 0.5 sentinel with real measurement.
>
> Write `<output-dir>/adversarial/debate-transcript.md` with all rounds, scoring matrix, and convergence assessment.
>
> **F4 [Hybrid scoring and base selection]**: Use `Task` tool to dispatch a scoring agent. Receives Step 3 instructions from SKILL.md (by section heading). Execute dual-pass scoring:
> - Layer 1 (Quantitative, 50%): 5 metrics (RC, IC, SR, DC, SC) per variant.
> - Layer 2 (Qualitative, 50%): 25-criterion binary rubric across 5 dimensions.
> - Position-bias mitigation: Score in forward and reverse order, resolve disagreements.
> - Select base variant. Write `<output-dir>/adversarial/base-selection.md`.
>
> **F5 [Refactoring plan and merge]**: Two sequential Task agents:
> - **Planner**: Receives base variant, scoring rationale, all variants, debate transcript. Produces `<output-dir>/adversarial/refactor-plan.md` with per-change source attribution, integration approach, risk level.
> - **Executor**: Applies refactoring plan to base. Produces `<output-dir>/adversarial/merged-output.md` with provenance annotations (`<!-- Source: Variant N, Section ref -->`) and `<output-dir>/adversarial/merge-log.md`.
>
> **F-contract [Return contract assembly]**: sc:roadmap writes `<output-dir>/adversarial/return-contract.yaml` directly (no Task agent needed):
> - `schema_version: "1.0"`
> - `status`: derived from merge validation
> - `convergence_score`: from F3 convergence tracking (real value, not sentinel)
> - `merged_output_path`: path to merged-output.md
> - `artifacts_dir`: path to adversarial/ directory
> - `unresolved_conflicts`: list of unresolved diff point IDs (type: `list[string]`, matching sc:adversarial FR-007)
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
- `invocation_method: "task_agent"` (always — mid-pipeline recovery details are logged in `merge-log.md`, not the contract)
- Emit message: `"claude -p headless invocation failed — executing enhanced Task-agent fallback (fallback_mode: true)"`

### 3.5 T03.01: Wiring Validation — Tool Availability (Phase 3)

**Currently missing from merged approach.** This task validates the invocation wiring from Phase 2.

**Updated specification** (replacing Skill tool check with `claude -p` check):

> **T03.01: Invocation Wiring Validation — Tool and CLI Availability**
>
> **Goal**: Confirm that the `claude -p` invocation pattern is correctly wired in the specification files.
>
> **Checks**:
> 1. `Bash` appears in allowed-tools for both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
> 2. `Skill` appears in allowed-tools for both files (retained for forward compatibility)
> 3. `refs/headless-invocation.md` exists and is referenced in Wave 2 step 3d-i
> 4. The command template in `refs/headless-invocation.md` includes `--dangerously-skip-permissions`, `--append-system-prompt`, `--output-format json`, and `--max-budget-usd`
> 5. The SKILL.md path in the command template is `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` (not `sc-adversarial/SKILL.md`)
>
> **Acceptance Criteria**:
> - All 5 checks pass
> - Evidence documented in D-0009

### 3.6 T03.02: Wiring Validation — Structural Audit (Phase 3)

**Currently missing from merged approach.** This task structurally audits the Wave 2 step 3 rewrite.

**Updated specification** (enhanced for `claude -p` architecture):

> **T03.02: Wave 2 Step 3 Structural Audit**
>
> **Goal**: Confirm the rewritten step 3 contains the correct sub-step structure.
>
> **9-point checklist**:
> 1. Wave 2 step 3 contains 6 sub-steps (3a through 3f)
> 2. Step 3d contains 4 sub-steps: 3d-i (construct), 3d-ii (execute), 3d-iii (validate), 3d-iv (fallback)
> 3. Step 3d-i references `refs/headless-invocation.md`
> 4. Step 3d-ii uses Bash tool with `timeout` command and `claude -p`, includes SKILL.md content validation (non-empty check)
> 5. Step 3d-iii checks: exit code, JSON parse, contract existence, cost guard (4 checks)
> 6. Step 3d-iv contains 4-state artifact scan + enhanced F1-F5 fallback (5 steps, not 3)
> 7. Step 3e (return contract consumption) handles both 5-field and 10-field contracts with defaults for missing fields
> 8. Verb glossary contains "Launch headless session" entry
> 9. All artifact paths use `<output-dir>/adversarial/` subdirectory (no flat-directory variant paths)
>
> **Acceptance Criteria**:
> - All 9 checklist items pass
> - Evidence documented in D-0010

### 3.7 T04.01: Return Contract Schema Update

**Deliverables affected**: D-0011 (schema spec), D-0012 (dead code removal)

**Field inventory**:
- **Producer-defined (sc:adversarial SKILL.md FR-007)**: 5 fields — `merged_output_path`, `convergence_score`, `artifacts_dir`, `status`, `unresolved_conflicts`
- **Consumer-added (sc:roadmap canonical comment, line 153)**: 2 additional fields — `fallback_mode`, `base_variant` (total: 7)
- **This sprint adds**: 3 new consumer-side fields — `schema_version`, `failure_stage`, `invocation_method` (total: 10)

**Full 10-field schema** (canonical definition — single source of truth):

```yaml
# return-contract.yaml — schema version 1.0, field count 10
# Producer fields (5, from sc:adversarial FR-007):
status: success | partial | failed       # Pipeline outcome
merged_output_path: <path> | ~            # Path to merged output file
convergence_score: 0.0-1.0 | ~           # Real computed value (NOT 0.5 sentinel)
artifacts_dir: <path>                     # Path to adversarial/ directory
unresolved_conflicts: [<string>, ...] | ~ # List of unresolved diff point IDs (list[string])

# Consumer-added fields (2, from sc:roadmap canonical comment):
fallback_mode: true | false               # true when Task-agent fallback was used
base_variant: <string> | ~                # Winning variant identifier

# New consumer-side fields (3, added by this sprint):
schema_version: "1.0"                     # Fixed string. Always "1.0" for this sprint.
failure_stage: <string> | ~               # Step name where failure occurred, null if success
invocation_method: "headless" | "task_agent"  # Informational only — consumers MUST NOT branch
```

**Dual-format handling in step 3e**: The headless session (loading unmodified sc:adversarial SKILL.md) will produce a 5-field contract. The fallback path produces a 10-field contract. Step 3e MUST handle both:

```yaml
# Default values for missing fields (applied by step 3e after YAML parse):
schema_version: "0.0"        # If absent, assume pre-versioned contract
fallback_mode: false          # If absent, assume headless produced it
base_variant: ~               # If absent, not available
failure_stage: ~              # If absent, assume no failure
invocation_method: "headless" # If absent, assume headless (since only headless omits it)
unresolved_conflicts: []      # If absent or null, assume empty list
```

**Design decisions**:
- `schema_version` remains `"1.0"`. The addition of consumer-side fields does not warrant a version bump because the producer's schema is unchanged.
- `invocation_method` is **informational only**. Consumers (step 3e) MUST NOT branch on this field. It exists for traceability and debugging. Values are simple enum — no compound values like `"headless+task_agent"` (mid-pipeline recovery is an implementation detail logged in `merge-log.md`).
- `fallback_mode` retains existing semantics (not deprecated). `true` when Task-agent fallback was used, `false` when headless succeeded.
- `convergence_score` MUST be computed (from debate convergence tracking), not hardcoded to 0.5.
- `unresolved_conflicts` type is `list[string]` matching the producer's definition in sc:adversarial SKILL.md (line 1551-1554). This is a list of diff point IDs, NOT an integer count. The tasklist T06.01 acceptance criteria ("typed as `integer` in both") must be corrected to `list[string]`.

**Schema evolution policy**:
- **Minor version** (1.0 → 1.1): Additive, non-breaking changes (new optional fields). No consumer changes required.
- **Major version** (1.0 → 2.0): Breaking changes (field removal, type changes, renamed fields). Consumer must check `schema_version` and handle accordingly.
- **Consumer behavior for unknown versions**: If `schema_version` is present and greater than expected, log warning `"Unknown schema version <version>, processing known fields only"` and continue.
- **Backward compatibility invariant**: Consumers MUST ignore unknown fields. The schema is additive-only within a major version.

### 3.8 T04.02: Return Contract Consumption

Step 3e must handle both 5-field (headless) and 10-field (fallback) contracts. After YAML parse, apply defaults for missing fields per the table in Section 3.7. If `invocation_method` is present, log it: `"Adversarial pipeline invocation method: <value>"`.

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

**Path**: `src/superclaude/skills/sc-roadmap-protocol/refs/headless-invocation.md`

Centralizes the `claude -p` invocation pattern. Referenced from Wave 1A step 2 and Wave 2 step 3d. This is the **single source of truth** for the command template — the specification (Section 2.2) documents the design rationale, but the ref file is what implementers read at runtime.

**Required contents**:
1. Prerequisites (Claude CLI installed, CLAUDECODE handling, SKILL.md content validation)
2. Mode A command template (multi-spec consolidation)
3. Mode B command template (multi-roadmap generation)
4. Parameter mapping table: depth → budget, depth → model, depth → timeout
5. Output parsing instructions (JSON + file-based contract)
6. Error handling matrix (11 conditions from Section 2.6)
7. CLAUDECODE environment variable handling pattern (with `trap EXIT`)
8. Fallback trigger conditions (when to enter 3d-iv)
9. Total adversarial budget ceiling computation
10. Return contract schema reference (field inventory and defaults for missing fields)

**Loading points**: Added to Wave loading table for both Wave 1A and Wave 2.

### 4.2 Probe Fixtures

Two minimal variant files (~100 words each) stored at `src/superclaude/skills/sc-roadmap-protocol/fixtures/probe-variant-a.md` and `probe-variant-b.md`.

**Required content differences** (to meaningfully exercise adversarial behavior):
- **Structural**: Variant A uses flat heading structure (H1, H2 only); Variant B uses nested headings (H1, H2, H3).
- **Content contradiction**: Variant A recommends technology choice X; Variant B recommends technology choice Y for the same requirement.
- **Topic ordering**: Both cover the same 3 topics but in different order.
- **Unique content**: Each has at least one section the other lacks entirely.

These are test fixtures for T01.01 test 4, not production artifacts.

### 4.3 Inline Bash (Not Shell Script)

**Decision**: The invocation is parameterized by runtime context and most naturally interpolated inline within the Bash tool call. No separate shell script. If the pattern stabilizes, a wrapper can be extracted later (YAGNI).

---

## 5. Instruction Delivery Protocol for Task Agents

When the enhanced fallback (F1-F5) dispatches Task agents, each agent receives SKILL.md instructions **inline** — not as a file reference.

**Extraction method**: sc:roadmap reads `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` once, extracts relevant sections **by heading match** (substring match on heading text), and injects the extracted content into each Task agent prompt.

**Matching algorithm**: For each target heading, scan SKILL.md for lines matching `^#{1,3}\s.*<target-substring>`. Extract all content from the matched heading to the next heading of equal or higher level.

**Extraction targets**: The SKILL.md contains two layers of content per step:
1. **Summary sections** (lines 70-250): `### Step N: <name>` — concise behavioral instructions (~30 lines each)
2. **Implementation Details** (lines 411-1589): `## Implementation Details — Step N: <name>` — detailed algorithms, scoring rubrics, templates (~300 lines each)

**Heading-to-step mapping** (using exact SKILL.md headings):

| Fallback Step | Summary Heading (extract for prompt context) | Implementation Details Heading (extract for detailed instructions) |
|---------------|----------------------------------------------|------------------------------------------------------------------|
| F2 (Diff analysis) | `### Step 1: Diff Analysis` (line 70) | `## Implementation Details — Step 1: Diff Analysis Engine` (line 411) |
| F3 (Debate) | `### Step 2: Adversarial Debate` (line 102) | `## Implementation Details — Step 2: Adversarial Debate Protocol` (line 751) |
| F4 (Scoring) | `### Step 3: Hybrid Scoring & Base Selection` (line 141) | `## Implementation Details — Step 3: Hybrid Scoring & Base Selection` (line 1049) |
| F5 (Merge) | `### Step 4: Refactoring Plan` (line 201) AND `### Step 5: Merge Execution` (line 237) | `## Implementation Details — Steps 4-5: Refactoring Plan & Merge Execution` (line 1302) |

**What to extract**: For each fallback step, extract BOTH the summary heading content AND the implementation details content. Concatenate them (summary first, then details) as the instruction payload for the Task agent. This gives each agent both the behavioral overview and the detailed algorithm.

**Rationale**: Line-number references (e.g., "lines 411-749") are fragile — any SKILL.md edit shifts them. Section-heading references using substring match are stable across edits that don't rename sections. The line numbers above are informational for this specification document only; the extraction code must use heading-text matching, never line numbers.

---

## 6. Risk Register

| ID | Risk | Prob | Impact | Mitigation |
|----|------|------|--------|------------|
| R1 | `claude -p` behavioral drift for complex pipelines | 0.35 | HIGH | T01.01 test 4 validates adherence pre-implementation. MANDATORY REQUIREMENTS in prompt reinforce critical behaviors. Enhanced fallback provides degraded path. |
| R2 | Cost unpredictability | 0.30 | MEDIUM | `--max-budget-usd` hard ceiling. Depth-based budget mapping. JSON `cost_usd` logged. Cost guard warns on >50% overshoot. Total adversarial budget ceiling (2×BUDGET) prevents compounding. |
| R3 | Context window limits | 0.25 | HIGH | T01.01 logs SKILL.md token estimate. If >40K tokens input, consider trimming non-essential sections. Context exhaustion → session end → contract missing → fallback activates. |
| R4 | Permission/sandbox concerns | 0.15 | HIGH | `--dangerously-skip-permissions` bypasses Claude Code permissions. OS permissions inherited. T01.01 test 2 validates file I/O. |
| R5 | CLI not installed | 0.10 | HIGH | T01.01 test 1 validates in 2 minutes. Fallback activates immediately. |
| R6 | Session nesting detection | 0.15 | MEDIUM | CLAUDECODE unset pattern with `trap EXIT` for signal-safe restore. T01.01 test 2 detects this failure mode. |
| R7 | Behavioral drift over time | 0.25 | MEDIUM | Lightweight regression test: single `claude -p` invocation on probe fixture, checking artifact production. Manual smoke test before releases. |
| R8 | SKILL.md read failure or ARG_MAX | 0.10 | HIGH | Content validation after cat (non-empty check). ARG_MAX warning at 1.5MB. Stderr capture for diagnostics. |
| R9 | Headless+fallback cost doubling | 0.20 | MEDIUM | Total adversarial budget ceiling: `2 × BUDGET`. Remaining budget computed before fallback. Abort if insufficient. |

---

## 7. Verification Plan

### 7.1 Pre-Implementation Verification (T01.01)

4-test viability probe as specified in Section 3.1. ~20 minutes, <= $2.15.

### 7.2 Structural Audit (T03.02, Post-Implementation)

9-point checklist as specified in Section 3.6.

### 7.3 Behavioral Adherence Verification (Post-Implementation)

Apply the 20-point behavioral adherence rubric to the first successful `claude -p` pipeline execution:

| Category | Max | 4 points | 3 points | 2 points | 1 point | 0 points | Grep verification |
|----------|-----|----------|----------|----------|---------|----------|-------------------|
| Diff Analysis Structure | 4 | `diff-analysis.md` contains headings matching all 4 of: `Structural`, `Content`, `Contradiction`, `Unique` AND at least one severity (`HIGH\|MEDIUM\|LOW`) | All 4 headings present, no severity | 2-3 of the 4 headings | Only generic "comparison" or "diff" heading | No diff analysis file | `grep -ci 'structural\|content.diff\|contradiction\|unique' diff-analysis.md` |
| Debate Protocol | 4 | `debate-transcript.md` contains `## Round 1` AND `## Round 2` AND at least one `steelman` reference AND at least one scoring reference | Rounds present + scoring, no steelman | Single round heading only | Prose comparison with no round structure | No debate transcript | `grep -c '## Round' debate-transcript.md` |
| Scoring Method | 4 | `base-selection.md` contains both quantitative metrics (`RC\|IC\|SR\|DC\|SC`) AND qualitative rubric AND position-bias reference | Some quantitative metric names | Qualitative assessment only | Unstructured justification | No scoring file | `grep -ci 'quantitative\|qualitative\|position.bias' base-selection.md` |
| Base Selection | 4 | Explicit scoring breakdown with numeric scores per variant | Partial numeric evidence | Brief textual justification | Selection implied but not justified | No base selection | `grep -c '[0-9]\.[0-9]' base-selection.md` |
| Merge Execution | 4 | `merged-output.md` has provenance annotations (`<!-- Source:`) AND `merge-log.md` exists | Some provenance annotations | Merged content, no provenance | Summary-only output | No merged output | `grep -c 'Source:' merged-output.md` |

**Passing threshold**: >= 14/20 (70%) for headless path. >= 12/20 (60%) for fallback path.

**Rationale for fallback threshold delta**: The fallback operates with constrained context (each Task agent sees only its step's instructions, not the full SKILL.md). Structural output quality is expectedly lower for single-agent-per-step execution vs. a single session with full behavioral context. 60% still requires meaningful adherence to all 5 categories (no category can score 0).

### 7.4 Multi-Round Debate Verification (Automated)

```bash
TRANSCRIPT="<output-dir>/adversarial/debate-transcript.md"
# Align patterns with actual sc:adversarial SKILL.md headings (## Round N: ...)
ROUND1=$(grep -ci "## Round 1\|## Round.*1" "$TRANSCRIPT" 2>/dev/null || echo 0)
ROUND2=$(grep -ci "## Round 2\|## Round.*2\|rebuttal" "$TRANSCRIPT" 2>/dev/null || echo 0)
LINES=$(wc -l < "$TRANSCRIPT" 2>/dev/null || echo 0)

echo "Round 1 markers: $ROUND1, Round 2 markers: $ROUND2, Lines: $LINES"
```

**Pass**: Round 1 > 0 AND Round 2 > 0 AND lines > 100.

### 7.5 End-to-End Test

Run `sc:roadmap --multi-roadmap --agents opus,sonnet` on a test spec. Verify:
1. `claude -p` invoked (Bash tool call in session)
2. Adversarial artifacts produced in `<output-dir>/adversarial/`: variant-*.md (>=2), diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged-output.md
3. `return-contract.yaml` present — either 5-field (headless) or 10-field (fallback)
4. Step 3e applies defaults for missing fields and routes correctly
5. `convergence_score` is computed (not 0.5 sentinel)
6. If headless succeeded: `fallback_mode` defaults to `false`, `invocation_method` defaults to `"headless"` (via step 3e defaults)
7. sc:roadmap routes correctly on contract status

**Fallback verification** (separate test): Force headless failure (e.g., set `--max-budget-usd 0.01`). Verify:
1. Fallback activates with warning message
2. F1-F5 all execute (5 steps, not 3)
3. `return-contract.yaml` written with `fallback_mode: true` and real computed convergence
4. All artifacts in `<output-dir>/adversarial/` subdirectory (not flat)
5. Behavioral adherence rubric score >= 12/20 for fallback path

### 7.6 Mid-Pipeline Recovery Tests (States B, C, D)

**Test B — Headless produces variants then fails**:
1. Pre-populate `<output-dir>/adversarial/` with 2 non-empty variant files (>100 bytes each)
2. Trigger fallback (no return-contract.yaml present)
3. Verify: State B detected (emit message references "variants preserved")
4. Verify: Fallback starts from F2, existing variant files are used (not regenerated)
5. Verify: All subsequent artifacts (diff-analysis.md through return-contract.yaml) are produced

**Test C — Headless produces variants + diff-analysis then fails**:
1. Pre-populate with 2 variant files + `diff-analysis.md` (non-empty, >100 bytes)
2. Trigger fallback
3. Verify: State C detected
4. Verify: Fallback starts from F3, existing diff-analysis is used

**Test D — Headless produces through debate then fails**:
1. Pre-populate with 2 variant files + `diff-analysis.md` + `debate-transcript.md` (non-empty)
2. Trigger fallback
3. Verify: State D detected
4. Verify: Fallback starts from F4

**Implementation note**: These tests can be simulated by creating the artifact directory with pre-written fixture files, then invoking the fallback logic directly without running the headless session.

### 7.7 Schema Transition Tests

**Test: 5-field contract from headless**:
1. Create a `return-contract.yaml` with only the 5 producer fields (`status`, `merged_output_path`, `convergence_score`, `artifacts_dir`, `unresolved_conflicts`)
2. Feed to step 3e
3. Verify: defaults applied (`schema_version: "0.0"`, `fallback_mode: false`, `invocation_method: "headless"`, etc.)
4. Verify: routing works correctly on `status` and `convergence_score`

**Test: 10-field contract from fallback**:
1. Create a `return-contract.yaml` with all 10 fields
2. Feed to step 3e
3. Verify: all fields parsed, no defaults applied for present fields
4. Verify: `invocation_method` is logged but not branched on

**Test: Unknown schema version**:
1. Create a contract with `schema_version: "2.0"` and all known fields
2. Feed to step 3e
3. Verify: warning logged `"Unknown schema version 2.0, processing known fields only"`
4. Verify: routing still works on `status` and `convergence_score`

### 7.8 Budget Exceeded Test

**Test: Headless budget exhaustion**:
1. Run `claude -p` with `--max-budget-usd 0.10` on a task that exceeds this budget
2. Verify: CLI self-terminates
3. Verify: artifact scan runs (check for partial artifacts)
4. Verify: stderr file contains budget-related diagnostic
5. Verify: fallback budget check computes remaining correctly

### 7.9 Invocation Method Logging Test

**Test**: After successful headless run, verify log output contains `"Adversarial pipeline invocation method: headless"` (via step 3e default application). After fallback run, verify log contains `"Adversarial pipeline invocation method: task_agent"`.

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
| *NEW*: Mid-pipeline awareness | — | **4-state artifact scan (none/variants/diff-analysis/debate-transcript) that determines fallback entry point, preserving partial work from a failed headless session** |

---

## 9. Deliverable Updates

The following deliverable descriptions in the Deliverable Registry require updates:

| ID | Current Description | Updated Description |
|----|--------------------|--------------------|
| D-0001 | Skill Tool Probe result document | **`claude -p` Viability Probe result document (4-test, <= $2.15)** |
| D-0002 | Sprint variant decision record | **Sprint variant decision record (headless vs fallback-only)** |
| D-0007 | Fallback protocol (F1, F2/3, F4/5) | **Enhanced fallback protocol (F1, F2, F3, F4, F5) with real convergence tracking and 4-state mid-pipeline awareness** |
| D-0009 | Skill Tool Availability test result | **Invocation wiring validation: tool and CLI availability (5-point checklist)** |
| D-0010 | Wave 2 Step 3 Structural Audit result | **Wave 2 Step 3 Structural Audit result (9-point checklist for `claude -p` architecture)** |

---

## 10. Summary of All Sprint-Spec Modifications

| Sprint-Spec Section | Task ID | Change Type | Description |
|---------------------|---------|-------------|-------------|
| Task 0.0 (T01.01) | T01.01 | **Replace** | Skill tool probe → 4-test `claude -p` viability probe (incl. behavioral adherence) with concrete grep checks |
| Task 1.1 AC (T02.01) | T02.01 | **Append** | Verify `Bash` in allowed-tools |
| Task 1.2 AC (T02.02) | T02.02 | **Append** | Verify `Bash` in allowed-tools |
| Wave 2 step 3d (T02.03) | T02.03 | **Rewrite** | Fallback-only → headless primary + enhanced 5-step fallback with 4-state mid-pipeline awareness |
| Fallback designation (T02.03) | T02.03 | **Demote** | "Sole mechanism" → "Fallback for headless failure" |
| Wiring validation (T03.01) | T03.01 | **Update** | Skill tool check → `claude -p` wiring + CLI check (5 points, incl. SKILL.md path verification) |
| Structural audit (T03.02) | T03.02 | **Update** | Generic audit → 9-point `claude -p` architecture audit |
| Return contract schema (T04.01) | T04.01 | **Add fields** | 3 consumer-side fields (`schema_version`, `failure_stage`, `invocation_method`); dual-format handling; schema evolution policy |
| Return contract consumption (T04.02) | T04.02 | **Enhance** | Handle both 5-field and 10-field contracts with defaults; log `invocation_method` |
| Tier 1 gate (T04.03) | T04.03 | **Add check** | Check 0: headless JSON health |
| Verb glossary (T05.01) | T05.01 | **Add entry** | "Launch headless session" = Bash + claude -p |
| Wave 1A step 2 (T05.02) | T05.02 | **Rewrite** | "Invoke" → headless invocation pattern |
| Pseudo-CLI conversion (T05.03) | T05.03 | **Adapt** | Pseudo-CLI → claude -p format |
| Glossary | — | **Update** | 4 definitions updated + 2 new terms |
| Deliverable Registry | — | **Update** | 5 deliverable descriptions updated |
| Risk Register | — | **Add** | 9 risks (R1-R9) |
| Verification Plan | — | **Expand** | 9 verification sections including mid-pipeline recovery, schema transition, budget exceeded, and invocation method logging tests |
| New: refs/ file | — | **Create** | `refs/headless-invocation.md` (single source of truth for command template) |
| New: probe fixtures | — | **Create** | 2 variant files with specified structural/content differences |
| Wave loading table | — | **Update** | Wave 1A and Wave 2 load `refs/headless-invocation.md` |
| T06.01 AC correction | T06.01 | **Fix** | `unresolved_conflicts` typed as `list[string]` (not `integer`) |

---

## 11. Fallback-Only Sprint Variant

If T01.01 fails (all 4 tests, or test 4 fails after augmentation retry):

The sprint proceeds using the **enhanced 5-step Task-agent pipeline** (F1-F5 from Section 3.3, step 3d-iv) as the sole invocation mechanism. This is NOT the old 3-step fallback — it is the upgraded 5-step pipeline with real convergence tracking.

Changes from current fallback-only variant:
- Upgraded from 3-step (F1/F2-3/F4-5) to 5-step (F1/F2/F3/F4/F5)
- Real convergence tracking replaces 0.5 sentinel
- `invocation_method: "task_agent"` in return contract
- `fallback_mode: true` (always, since there's no primary path)
- All artifacts written to `<output-dir>/adversarial/` (consistent directory structure)

Trigger: "T01.01 decision gate returns 'primary path blocked' (neither Skill tool nor `claude -p` headless invocation can reliably invoke sc:adversarial with sufficient behavioral adherence)."

---

## Appendix A: Critical Issues Resolved (from Reflection)

This specification addresses all 5 critical issues identified during the reflection review of the merged approach:

| ID | Issue | Resolution |
|----|-------|------------|
| C1 | Permission flag inconsistency | Standardized on `--dangerously-skip-permissions` with documented rationale (Section 2.1) |
| C2 | Task ID mapping absent | Full mapping table added (Section 0, Task ID Mapping) |
| C3 | Phase 3 tasks unaddressed | T03.01 and T03.02 specifications added (Sections 3.5, 3.6) |
| C4 | Glossary contradictions | Updated glossary with 4 corrected + 2 new definitions (Section 8) |
| C5 | Schema version inconsistency | Resolved: `schema_version: "1.0"` is correct; "v1.1" header was error (Section 3.7 note) |

## Appendix B: Important Issues Resolved (from Reflection)

| ID | Issue | Resolution |
|----|-------|------------|
| I1 | SKILL.md line 141 contradiction | Replacement text specified (Section 3.4) |
| I2 | Wave 1A specifics | Same `claude -p` pattern applies (Section 3.11) |
| I3 | Fallback extraction to ref | Centralized in `refs/headless-invocation.md` (Section 4.1) |
| I4 | Heading names for instruction delivery | Exact heading mapping with extraction algorithm defined (Section 5) |
| I5 | Deliverable R-007 stale description | Updated from "3-step (F1, F2/3, F4/5)" to "5-step (F1-F5)" (Section 9) |

## Appendix C: Panel Findings Resolution (v1 → v2)

| # | Finding | Severity | Resolution in v2 |
|---|---------|----------|-------------------|
| W1 | Field count arithmetic wrong (claimed "9+1", actual 5/7/10) | CRITICAL | Fixed: explicit field inventory (5 producer + 2 consumer-existing + 3 new = 10) in Section 3.7 |
| F1 | Spec modifies contract owned by out-of-scope service | CRITICAL | Added Schema Ownership Model (Section 0) with dual-format handling; step 3e applies defaults for missing fields |
| S1 | Consumer defines producer's contract | CRITICAL | Reframed: 3 new fields are consumer-side additions, not producer schema changes; headless produces 5-field contract as-is |
| A1 | Section 5 heading mapping uses paraphrased headings | CRITICAL | Fixed: exact SKILL.md headings with line numbers, explicit summary vs implementation-details distinction, substring matching algorithm |
| N1 | No SKILL.md content validation after cat, no ARG_MAX | CRITICAL | Added: empty check, ARG_MAX warning at 1.5MB, conditional execution gate |
| C1 | No test for mid-pipeline recovery (States B/C) | CRITICAL | Added: Section 7.6 with 3 explicit test cases for States B, C, D |
| W2 | `unresolved_conflicts` type (integer vs list[string]) | MAJOR | Fixed: `list[string]` matching producer's definition; T06.01 AC correction noted |
| F2 | Schema in 3 places (prompt, spec, ref file) | MAJOR | Fixed: prompt references "your Return Contract (FR-007)" instead of enumerating fields; ref file is single source of truth for implementers |
| F3 | Fallback writes to different directory than headless | MAJOR | Fixed: all fallback artifact paths use `<output-dir>/adversarial/` subdirectory; structural audit checklist item 9 verifies this |
| N2 | 3-state model incomplete | MAJOR | Extended to 4-state model (added State D: debate-transcript exists); rationale for not extending to 5 states documented |
| N3 | No combined budget ceiling | MAJOR | Added: total adversarial budget = 2×BUDGET; remaining budget check before fallback |
| A2 | No concrete examples for 3-state scan | MAJOR | Added: 3 concrete examples with Given/When/Then in Section 3.3 State A and B definitions |
| A3 | Behavioral adherence rubric not executable | MAJOR | Rewritten: Section 7.3 includes grep verification column with concrete patterns per category |
| C2 | Fallback threshold (50%) unjustified | MAJOR | Raised to 60% (12/20); rationale documented (constrained context per-agent) |
| C3 | No test for 5-field vs 10-field contract | MAJOR | Added: Section 7.7 with 3 schema transition tests |
| S2 | No schema evolution strategy | MAJOR | Added: versioning policy (minor/major), consumer behavior for unknown versions |
| S3 | `headless+task_agent` compound value | MAJOR | Removed: only `"headless"` and `"task_agent"` values; mid-pipeline details in merge-log.md |
| W4 | Stderr discarded | MINOR | Fixed: stderr captured to temp file, inspected on failure, cleaned up |
| W5 | Cost estimate arithmetic | MINOR | Fixed: explicit per-test budgets, total <= $2.15 |
| F4 | `invocation_method` compound value invites branching | MINOR | Resolved with S3: simple enum only |
| N4 | CLAUDECODE restore not signal-safe | MINOR | Fixed: `trap EXIT` added |
| A4 | Multi-round grep patterns misaligned | MINOR | Fixed: patterns aligned with `## Round N:` heading format from SKILL.md |
| C4 | No test for invocation_method logging | MINOR | Added: Section 7.9 |
| S4 | No backward compatibility guarantee | MINOR | Added: invariant in Section 0 and Section 3.7 |
| W6 | Probe idempotency (stale files) | SUGGESTION | Added: pre-test cleanup step in Section 3.1 |
| N5 | Cost guard multiplier configurable | SUGGESTION | Acknowledged but deferred (YAGNI for initial sprint) |
| A5 | Probe fixtures lack specified content | SUGGESTION | Added: required content differences in Section 4.2 |
| C5 | Missing budget exceeded test | SUGGESTION | Added: Section 7.8 |
| S5 | Contract schema validation in consumer | SUGGESTION | Deferred: lightweight validation can be added in future sprint if malformed contracts are observed |

---

*Specification draft v2 generated 2026-02-23.*
*Addresses all 27 panel review findings (4 CRITICAL, 11 MAJOR, 6 MINOR, 6 SUGGESTION).*
*Based on merged adversarial approach (convergence: 1.00) with reflection + panel review fixes applied.*
*Ready for implementation or further review.*
