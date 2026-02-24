## Approach 1: Empirical Probe First

**Author**: claude-opus-4-6 (system-architect persona)
**Date**: 2026-02-23
**Status**: PROPOSAL — Pending approval before execution
**Context**: Sprint-spec Task 0.0 returned `TOOL_NOT_AVAILABLE` for the Skill tool. This proposal replaces the Skill tool invocation strategy with a `claude -p` headless session strategy and defines the empirical validation required before committing to sprint-spec modifications.

---

### 1. Philosophy: Why Probe First?

**Core principle**: Do not rewrite a 450-line sprint specification based on untested assumptions about `claude -p` behavior.

**What we are de-risking**:

| Risk | Consequence of not probing | Cost if wrong |
|------|---------------------------|---------------|
| `claude -p` cannot load slash commands at all | Sprint redesign after partial implementation; wasted 4-6 hours | HIGH |
| `claude -p` loads commands but ignores behavioral instructions (Issue #1048) | Adversarial pipeline produces garbage — single-round summaries instead of 5-step debate | HIGH |
| `--append-system-prompt` injection works but context window is insufficient | Silent truncation; pipeline starts but produces incomplete artifacts | MEDIUM |
| Per-invocation cost exceeds $2 | Feature becomes economically unviable for users | MEDIUM |
| Success rate below 70% | Feature ships but is unreliable — worse than not having it | HIGH |

**The asymmetry argument**: The probe costs 1-2 hours and ~$5-10 in API calls. The sprint implementation costs 12-15 hours. If we probe first and discover `claude -p` is unreliable, we save the entire implementation cost by routing to the fallback-only variant immediately. If the probe succeeds, we have empirical evidence to confidently commit to the headless invocation path. The expected value of probing first is strongly positive regardless of outcome.

**Three invocation strategies under test** (ordered by expected reliability):

| Strategy | Mechanism | Expected Reliability | Rationale |
|----------|-----------|---------------------|-----------|
| **S1: System-Prompt Injection** | `claude -p --append-system-prompt "$(cat SKILL.md)" "Execute the 5-step adversarial protocol..."` | HIGHEST | Bypasses command loading entirely; SKILL.md content becomes system instructions |
| **S2: Project-Scoped Command** | `claude -p "/project:sc:adversarial --compare ..."` | MEDIUM | Issue #837 suggests `/project:` may work in `-p` mode |
| **S3: Direct Slash Command** | `claude -p "/sc:adversarial --compare ..."` | LOWEST | Issue #837 reports slash commands broken in `-p` mode |

The probe tests all three strategies and selects the best-performing one.

---

### 2. Test Suite Design

All tests execute from the repository root (`/config/workspace/SuperClaude_Framework/`). Tests are numbered T01-T12. Each test has a PASS/FAIL criterion and produces a structured evidence file.

#### Fixtures Required

Before running tests, prepare these input fixtures:

```
.dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence/probe-fixtures/
  spec-minimal.md          # 200-line minimal project specification
  variant-a.md             # Pre-written roadmap variant A (opus:architect style)
  variant-b.md             # Pre-written roadmap variant B (sonnet:security style)
  expected-schema.yaml     # return-contract.yaml JSON Schema for validation
```

**spec-minimal.md**: A stripped-down project spec with 5 requirements, 2 milestones, and 1 risk. Small enough to fit in context alongside SKILL.md.

**variant-a.md / variant-b.md**: Pre-written roadmap variants (~300 lines each) that have genuine structural differences, contradictions, and unique contributions — enough material for a real adversarial debate.

**expected-schema.yaml**: JSON Schema defining the 9-field return contract (schema_version, status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts, base_variant, failure_stage, fallback_mode).

---

#### T01: Basic `claude -p` Invocation (Smoke Test)

**Purpose**: Confirm `claude -p` is available and can execute a minimal prompt.

**Command**:
```bash
claude -p "Respond with exactly: PROBE_OK" \
  --output-format json \
  --max-budget-usd 0.10 2>&1
```

**PASS criterion**: Output contains `PROBE_OK`.
**FAIL criterion**: Command not found, timeout, or output missing `PROBE_OK`.
**Evidence file**: `evidence/T01-basic-invocation.json`

---

#### T02: Slash Command Invocation (`/sc:adversarial`)

**Purpose**: Test whether `/sc:adversarial` can be invoked directly in `-p` mode. Expected to fail per Issue #837, but we must confirm empirically.

**Command**:
```bash
claude -p "/sc:adversarial --compare variant-a.md,variant-b.md --output ./evidence/T02-output/" \
  --output-format json \
  --max-budget-usd 2.00 \
  --dangerously-skip-permissions 2>&1
```

**PASS criterion**: Adversarial pipeline artifacts appear in `evidence/T02-output/adversarial/`.
**FAIL criterion**: Error message, no artifacts, or Claude treats the slash command as prose.
**Evidence file**: `evidence/T02-slash-command.json`

---

#### T03: Project-Scoped Command (`/project:sc:adversarial`)

**Purpose**: Test whether `/project:sc:adversarial` works in `-p` mode (Issue #837 suggests this may work).

**Command**:
```bash
claude -p "/project:sc:adversarial --compare variant-a.md,variant-b.md --output ./evidence/T03-output/" \
  --output-format json \
  --max-budget-usd 2.00 \
  --dangerously-skip-permissions 2>&1
```

**PASS criterion**: Adversarial pipeline artifacts appear in `evidence/T03-output/adversarial/`.
**FAIL criterion**: Error message, no artifacts, or Claude treats the command as prose.
**Evidence file**: `evidence/T03-project-command.json`

---

#### T04: System-Prompt Injection with SKILL.md

**Purpose**: Test the system-prompt injection strategy — inject the full sc:adversarial SKILL.md as system instructions, then provide the pipeline trigger as the user prompt.

**Command**:
```bash
SKILL_CONTENT=$(cat src/superclaude/skills/sc-adversarial/SKILL.md)

claude -p "You are executing the sc:adversarial pipeline. Your inputs are:
- Mode A: Compare existing files
- Files: $(pwd)/evidence/probe-fixtures/variant-a.md, $(pwd)/evidence/probe-fixtures/variant-b.md
- Output directory: $(pwd)/evidence/T04-output/
- Depth: standard
- Convergence threshold: 0.80

Execute all 5 steps of the adversarial protocol. Write all artifacts to the output directory." \
  --append-system-prompt "$SKILL_CONTENT" \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --permission-mode bypassPermissions \
  --output-format json \
  --max-budget-usd 3.00 2>&1
```

**PASS criterion**: All of: (1) `evidence/T04-output/adversarial/diff-analysis.md` exists and is non-empty, (2) `evidence/T04-output/adversarial/debate-transcript.md` exists, (3) `evidence/T04-output/adversarial/base-selection.md` exists, (4) `evidence/T04-output/adversarial/merged-output.md` or a merged artifact exists.
**FAIL criterion**: Fewer than 3 of the 4 artifact types produced.
**Evidence file**: `evidence/T04-system-prompt.json`

---

#### T05: Behavioral Adherence Scoring

**Purpose**: Measure whether Claude follows the SKILL.md instructions or drifts to its own interpretation. This test uses the output from T04 (or whichever strategy produced artifacts).

**Method**: Grade the T04 output against a 20-point rubric (see Section 3, Scoring Rubric). This is a post-hoc analysis of T04 artifacts, not a separate invocation.

**Rubric categories** (4 points each, 20 total):
1. **Diff Analysis Structure**: Contains all 4 sections (structural_diff, content_diff, contradiction_detection, unique_contribution_extraction)
2. **Debate Protocol**: Contains advocate statements with steelman requirement, per-point scoring matrix
3. **Scoring Method**: Uses hybrid scoring (quantitative + qualitative layers), not just prose
4. **Base Selection**: Explicit selection with scoring evidence, not just "I chose variant A"
5. **Merge Execution**: Provenance annotations present, merge-log.md produced

**PASS criterion**: Score >= 14/20 (70% behavioral adherence).
**FAIL criterion**: Score < 14/20.
**Evidence file**: `evidence/T05-behavioral-adherence.json` (contains rubric with per-item scores and justifications).

---

#### T06: File Artifact Production

**Purpose**: Verify that the expected file tree is produced on disk, not just discussed in output text.

**Method**: After T04 completes, run automated file existence checks.

```bash
OUTDIR="evidence/T04-output/adversarial"
SCORE=0
TOTAL=6

[ -d "$OUTDIR" ] && ((SCORE++)) || echo "MISSING: output directory"
[ -f "$OUTDIR/diff-analysis.md" ] && ((SCORE++)) || echo "MISSING: diff-analysis.md"
[ -f "$OUTDIR/debate-transcript.md" ] && ((SCORE++)) || echo "MISSING: debate-transcript.md"
[ -f "$OUTDIR/base-selection.md" ] && ((SCORE++)) || echo "MISSING: base-selection.md"
[ -s "$OUTDIR/merged-output.md" ] || [ -s "$OUTDIR/../merged-output.md" ] && ((SCORE++)) || echo "MISSING: merged output"
# Check for any variant files
ls "$OUTDIR"/variant-*.md >/dev/null 2>&1 && ((SCORE++)) || echo "MISSING: variant files"

echo "Artifact score: $SCORE/$TOTAL"
```

**PASS criterion**: Score >= 5/6 (at least 5 of 6 artifact types present).
**FAIL criterion**: Score < 4/6.
**Evidence file**: `evidence/T06-artifact-production.txt`

---

#### T07: Multi-Round Debate Verification

**Purpose**: Confirm the pipeline executes multiple debate rounds (not collapsing to a single-round summary). This is the critical behavioral test — Issue #1048 reports Claude ignoring behavioral instructions, and single-round collapse is the most likely failure mode.

**Method**: Analyze the debate transcript from T04 output.

**Automated checks**:
```bash
TRANSCRIPT="evidence/T04-output/adversarial/debate-transcript.md"

# Check for round markers
ROUND1=$(grep -ci "round.1\|first.round\|round 1" "$TRANSCRIPT" 2>/dev/null || echo 0)
ROUND2=$(grep -ci "round.2\|second.round\|round 2\|rebuttal" "$TRANSCRIPT" 2>/dev/null || echo 0)

# Check for per-point scoring matrix
MATRIX=$(grep -ci "scoring.matrix\|point.*score\|winner.*confidence" "$TRANSCRIPT" 2>/dev/null || echo 0)

# Check minimum length (multi-round debate should be substantial)
LINES=$(wc -l < "$TRANSCRIPT" 2>/dev/null || echo 0)

echo "Round 1 markers: $ROUND1"
echo "Round 2 markers: $ROUND2"
echo "Scoring matrix markers: $MATRIX"
echo "Total lines: $LINES"
```

**PASS criterion**: Round 1 markers > 0 AND Round 2 markers > 0 AND total lines > 100.
**FAIL criterion**: No Round 2 markers (single-round collapse) OR total lines < 50.
**Evidence file**: `evidence/T07-multi-round.json`

---

#### T08: Return Contract Validity

**Purpose**: Verify that `return-contract.yaml` is produced and conforms to the 9-field schema.

**Method**: After T04, check for the return contract file and validate its structure.

```bash
CONTRACT="evidence/T04-output/adversarial/return-contract.yaml"

if [ ! -f "$CONTRACT" ]; then
  echo "FAIL: return-contract.yaml not found"
  exit 1
fi

# Check for all 9 required fields
FIELDS=("schema_version" "status" "convergence_score" "merged_output_path" "artifacts_dir" "unresolved_conflicts" "base_variant" "failure_stage" "fallback_mode")
FOUND=0
for field in "${FIELDS[@]}"; do
  if grep -q "^${field}:" "$CONTRACT" 2>/dev/null; then
    ((FOUND++))
  else
    echo "MISSING FIELD: $field"
  fi
done

echo "Schema compliance: $FOUND/${#FIELDS[@]}"
```

**PASS criterion**: All 9 fields present; `status` is one of `success`, `partial`, `failed`; `schema_version` is `"1.0"`.
**FAIL criterion**: Fewer than 7 fields present OR `status` field missing.
**Evidence file**: `evidence/T08-return-contract.json`

**Note**: The return contract write instruction does not yet exist in sc:adversarial SKILL.md (that is Epic 3, Task 3.1 of the sprint). For this probe, the return contract instruction must be appended to the SKILL.md content injected via `--append-system-prompt`. If the pipeline does not produce a return contract without explicit instruction, that is expected and informative — it tells us that Epic 3 is genuinely necessary.

---

#### T09: Model Selection Differentiation

**Purpose**: Verify that `--model` produces stylistically different outputs when used for variant generation.

**Command**: Run two minimal variant-generation prompts with different models.

```bash
# Variant with opus
claude -p "Read $(pwd)/evidence/probe-fixtures/spec-minimal.md and generate a roadmap variant. Write to $(pwd)/evidence/T09-opus-variant.md" \
  --model claude-opus-4-6 \
  --allowedTools "Read,Write" \
  --permission-mode bypassPermissions \
  --max-budget-usd 1.00 \
  --output-format json 2>&1

# Variant with sonnet
claude -p "Read $(pwd)/evidence/probe-fixtures/spec-minimal.md and generate a roadmap variant. Write to $(pwd)/evidence/T09-sonnet-variant.md" \
  --model claude-sonnet-4-20250514 \
  --allowedTools "Read,Write" \
  --permission-mode bypassPermissions \
  --max-budget-usd 0.50 \
  --output-format json 2>&1
```

**PASS criterion**: Both files produced; content differs structurally (not just token-level noise). Diff shows >20% line-level divergence.
**FAIL criterion**: Either file missing OR outputs are near-identical (<5% divergence).
**Evidence file**: `evidence/T09-model-selection.json`

---

#### T10: Per-Invocation Cost Measurement

**Purpose**: Measure the actual cost of a full pipeline invocation to validate economic viability.

**Method**: Use `--output-format json` and parse the cost fields from the JSON output of T04.

```bash
# Extract cost from T04's JSON output
# Claude -p with --output-format json includes usage metadata
cat evidence/T04-system-prompt.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
# Parse cost_usd or input/output token counts from the response
print(json.dumps({
    'test': 'T10',
    'raw_output_keys': list(data.keys()) if isinstance(data, dict) else 'not_dict',
    'data_sample': str(data)[:500]
}, indent=2))
"
```

**PASS criterion**: Per-invocation cost < $2.00 USD for a 2-variant comparison.
**FAIL criterion**: Per-invocation cost > $3.00 USD (feature economically questionable).
**WARNING zone**: $2.00-$3.00 (viable but needs cost optimization).
**Evidence file**: `evidence/T10-cost-measurement.json`

---

#### T11: Reliability Across 10 Runs

**Purpose**: Measure the success rate of the best-performing strategy across 10 identical runs.

**Method**: Execute the winning strategy (from T02/T03/T04) 10 times with identical inputs. Score each run on artifact production (T06 rubric).

```bash
for i in $(seq 1 10); do
  echo "=== Run $i/10 ==="
  # Execute best strategy with output to evidence/T11-run-$i/
  # ... (strategy-specific command)
  # Score artifacts
  # ... (T06 scoring logic)
done
```

**PASS criterion**: >= 8/10 runs produce artifact score >= 4/6 (80% reliability at 67% artifact threshold).
**FAIL criterion**: < 7/10 runs succeed (below 70% reliability).
**Evidence file**: `evidence/T11-reliability-matrix.json` (contains per-run scores and aggregate statistics).

**Cost note**: 10 runs at ~$1-3 each = $10-30 total. This is the most expensive test. If T04 fails outright, skip T11 — there is no strategy worth reliability-testing.

---

#### T12: Context Window Pressure Test

**Purpose**: Determine whether SKILL.md + pipeline working memory fits in the context window without degradation.

**Method**: Measure the SKILL.md file size and estimate total context consumption.

```bash
# Measure SKILL.md size
SKILL_CHARS=$(wc -c < src/superclaude/skills/sc-adversarial/SKILL.md)
SKILL_TOKENS_EST=$((SKILL_CHARS / 4))  # rough 4:1 char:token ratio

# Measure variant sizes
VA_CHARS=$(wc -c < evidence/probe-fixtures/variant-a.md)
VB_CHARS=$(wc -c < evidence/probe-fixtures/variant-b.md)
VARIANT_TOKENS_EST=$(( (VA_CHARS + VB_CHARS) / 4 ))

TOTAL_INPUT_EST=$((SKILL_TOKENS_EST + VARIANT_TOKENS_EST))

echo "SKILL.md: ~${SKILL_TOKENS_EST} tokens"
echo "Variants: ~${VARIANT_TOKENS_EST} tokens"
echo "Total input estimate: ~${TOTAL_INPUT_EST} tokens"
echo "Context budget (200K): $(( 200000 - TOTAL_INPUT_EST )) tokens remaining for pipeline work"
```

**PASS criterion**: Total input estimate < 40,000 tokens (leaving 160K+ for pipeline working memory).
**FAIL criterion**: Total input estimate > 80,000 tokens (insufficient room for multi-round debate).
**Evidence file**: `evidence/T12-context-pressure.json`

---

#### T13: Error Handling — Timeout and Context Exhaustion

**Purpose**: Observe behavior when the pipeline is forced into failure states.

**Test 13a — Budget exhaustion**:
```bash
claude -p "Execute the full 5-step adversarial protocol on these files..." \
  --append-system-prompt "$SKILL_CONTENT" \
  --max-budget-usd 0.10 \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
  --permission-mode bypassPermissions \
  --output-format json 2>&1
```
Does the session write partial artifacts? Does it write `return-contract.yaml` with `status: failed`?

**Test 13b — Missing input files**:
```bash
claude -p "Execute adversarial pipeline on: /nonexistent/file1.md, /nonexistent/file2.md" \
  --append-system-prompt "$SKILL_CONTENT" \
  --allowedTools "Read,Write" \
  --permission-mode bypassPermissions \
  --output-format json \
  --max-budget-usd 0.50 2>&1
```
Does the session fail gracefully with an error message, or does it hallucinate file contents?

**PASS criterion**: At least one failure mode produces structured error output (not a raw crash).
**FAIL criterion**: Both failure modes produce unstructured crashes with no useful diagnostics.
**Evidence file**: `evidence/T13-error-handling.json`

---

### 3. Test Harness Architecture

#### Runner Design

The test harness is a Bash script (`probe-runner.sh`) that orchestrates all tests sequentially, collects evidence, and produces a summary report. Bash is chosen over Python because the primary operation is invoking `claude -p` as a subprocess — Bash is the natural shell for this.

```
.dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence/
  probe-fixtures/              # Input fixtures (created before run)
    spec-minimal.md
    variant-a.md
    variant-b.md
    expected-schema.yaml
  probe-runner.sh              # Test harness script
  T01-basic-invocation.json    # Evidence files (created during run)
  T02-slash-command.json
  T03-project-command.json
  T04-system-prompt.json
  T04-output/                  # Artifact output directory for T04
    adversarial/
  T05-behavioral-adherence.json
  T06-artifact-production.txt
  T07-multi-round.json
  T08-return-contract.json
  T09-opus-variant.md
  T09-sonnet-variant.md
  T09-model-selection.json
  T10-cost-measurement.json
  T11-reliability-matrix.json  # Only if T04 passes
  T11-run-{1..10}/             # Per-run output directories
  T12-context-pressure.json
  T13-error-handling.json
  probe-summary.md             # Final summary report
```

#### Execution Phases

The runner executes in 4 phases with early termination gates:

```
Phase 1: Smoke Tests (T01)
  |-- FAIL --> Abort: claude -p not functional
  |
Phase 2: Strategy Selection (T02, T03, T04) -- run in parallel
  |-- All FAIL --> Abort: no viable invocation strategy
  |-- At least one PASS --> Select best strategy, continue
  |
Phase 3: Deep Validation (T05-T10, T12, T13) -- sequential
  |-- Uses artifacts from best strategy
  |-- Produces behavioral adherence score, cost data, context analysis
  |
Phase 4: Reliability Test (T11) -- expensive, only if Phase 3 passes
  |-- 10 identical runs of best strategy
  |-- Produces reliability percentage
```

#### Scoring Rubric for Behavioral Adherence (T05)

Each category is scored 0-4:

| Score | Meaning |
|-------|---------|
| 4 | Full compliance — all SKILL.md instructions followed, correct structure |
| 3 | Substantial compliance — minor deviations (e.g., section naming differs) |
| 2 | Partial compliance — correct intent but significant structural drift |
| 1 | Minimal compliance — recognizable attempt but mostly own interpretation |
| 0 | No compliance — completely ignored SKILL.md instructions |

**Category 1: Diff Analysis Structure (0-4)**
- 4: All 4 sections present (structural_diff, content_diff, contradiction_detection, unique_contribution_extraction) with severity ratings
- 3: All 4 sections present, severity ratings missing
- 2: 2-3 sections present
- 1: Generic "comparison" without SKILL.md structure
- 0: No diff analysis produced

**Category 2: Debate Protocol (0-4)**
- 4: Advocate statements with steelman requirement, per-point scoring matrix, multiple rounds
- 3: Advocate statements and scoring present, steelman missing or weak
- 2: Single round of debate with scoring
- 1: Prose comparison labeled as "debate"
- 0: No debate structure

**Category 3: Scoring Method (0-4)**
- 4: Hybrid scoring with quantitative (5 metrics) and qualitative (25-criterion rubric) layers
- 3: Some quantitative scoring present alongside qualitative
- 2: Qualitative-only scoring with explicit criteria
- 1: Unstructured "this variant is better because..."
- 0: No scoring method

**Category 4: Base Selection (0-4)**
- 4: Explicit selection with full scoring breakdown, tiebreaker protocol if applicable
- 3: Explicit selection with partial scoring evidence
- 2: Selection made with brief justification
- 1: Selection implied but not formally declared
- 0: No base selection

**Category 5: Merge Execution (0-4)**
- 4: Merged output with provenance annotations, merge-log.md produced
- 3: Merged output with some provenance, no separate merge log
- 2: Merged output without provenance
- 1: Summary of what should be merged (not actual merge)
- 0: No merge produced

**Total**: 20 points. Minimum passing: 14/20 (70%).

#### Statistical Methodology

For the reliability test (T11):
- **Sample size**: 10 runs (balances statistical significance against cost)
- **Success definition**: Artifact score >= 4/6 AND behavioral adherence >= 10/20
- **Reported metrics**: Success rate (%), mean artifact score, standard deviation, min/max
- **Confidence interval**: Wilson score interval for the success proportion at 95% confidence level
- **Decision threshold**: Lower bound of 95% CI must be >= 60% to declare strategy viable

---

### 4. Decision Gates

#### Gate 1: Strategy Viability (after Phase 2)

| Outcome | Decision |
|---------|----------|
| T04 PASS (system-prompt injection works) | Proceed to Phase 3 with S1 strategy |
| T04 FAIL, T03 PASS (project-scoped command works) | Proceed to Phase 3 with S2 strategy |
| T04 FAIL, T03 FAIL, T02 PASS (slash command works) | Proceed to Phase 3 with S3 strategy (low confidence) |
| All FAIL | **ABORT probe. Route to fallback-only sprint variant.** |

#### Gate 2: Behavioral Quality (after Phase 3)

| Metric | Required | Rationale |
|--------|----------|-----------|
| Behavioral adherence (T05) | >= 14/20 (70%) | Below this, the pipeline produces low-quality output that is worse than the fallback |
| Artifact production (T06) | >= 4/6 | Missing critical artifacts (diff-analysis, debate, merged-output) means the pipeline is incomplete |
| Multi-round debate (T07) | PASS | Single-round collapse defeats the purpose of adversarial debate |
| Cost per invocation (T10) | < $3.00 | Above this, feature is economically unviable for regular use |

**All four conditions must be met to proceed to Gate 3.**

If any condition fails:
- Behavioral adherence < 14/20: Try augmenting the system prompt with stronger behavioral anchoring (explicit "YOU MUST" instructions). If still failing, route to fallback-only.
- Artifact production < 4/6: Investigate which artifacts are missing. If diff-analysis is present but merge is missing, consider a hybrid approach (headless for debate, inline for merge).
- Multi-round collapse: Add explicit round-counting instructions to the prompt. If still collapsing, this is a fundamental behavioral limitation — route to fallback-only.
- Cost > $3.00: Evaluate whether `--model` with a cheaper model (sonnet, haiku) can run the debate rounds while opus handles scoring/merge.

#### Gate 3: Reliability (after Phase 4)

| Metric | Required | Fallback |
|--------|----------|----------|
| Success rate (T11) | >= 80% (8/10) | If 70-79%: viable but add retry logic. If < 70%: route to fallback-only. |
| 95% CI lower bound | >= 60% | Statistical floor — even accounting for sampling noise, strategy must be viable |

#### Gate Summary: Decision Matrix

| Gate 1 | Gate 2 | Gate 3 | Sprint Decision |
|--------|--------|--------|-----------------|
| PASS | PASS | >= 80% | **Full headless invocation path** — rewrite Task 1.3 for `claude -p` |
| PASS | PASS | 70-79% | **Headless with retry** — add retry wrapper (max 2 retries) to Task 1.3 |
| PASS | PASS | < 70% | **Fallback-only** — headless is unreliable; use enhanced Task-agent pipeline |
| PASS | FAIL | — | **Fallback-only** — headless produces low-quality output |
| FAIL | — | — | **Fallback-only** — no viable invocation strategy |

---

### 5. Sprint-Spec Changes

#### 5.1 New Task 0.0A: `claude -p` Viability Probe (replaces Task 0.0)

**Replacement rationale**: Task 0.0 tested the Skill tool and got `TOOL_NOT_AVAILABLE`. The Skill tool path is empirically dead. Task 0.0A replaces it with a `claude -p` probe.

**Proposed Task 0.0A text**:

> **Task 0.0A: `claude -p` Headless Invocation Viability Probe (Pre-Implementation Gate)**
>
> **Goal**: Empirically determine whether `claude -p` can invoke the sc:adversarial pipeline in a headless session with sufficient behavioral adherence and reliability.
>
> **Method**: Execute the probe test suite defined in `artifacts/approach-1-empirical-probe-first.md`. The test suite evaluates three invocation strategies (system-prompt injection, project-scoped command, direct slash command) across 13 test cases covering invocation, behavioral adherence, artifact production, multi-round debate, return contract validity, cost, and reliability.
>
> **Artifacts**: All evidence files written to `tasklist/evidence/`. Summary report at `tasklist/evidence/probe-summary.md`.
>
> **Decision gates** (three sequential):
> - **Gate 1 (Strategy Viability)**: At least one invocation strategy produces adversarial pipeline artifacts. If all fail: route to fallback-only sprint variant.
> - **Gate 2 (Behavioral Quality)**: Best strategy scores >= 14/20 behavioral adherence, >= 4/6 artifact production, passes multi-round debate check, costs < $3/invocation. If any fail: route to fallback-only.
> - **Gate 3 (Reliability)**: Best strategy achieves >= 80% success rate across 10 identical runs. If 70-79%: add retry wrapper. If < 70%: route to fallback-only.
>
> **Time cost**: 1-2 hours (including 10-run reliability test). API cost: ~$10-30.
> **Blocks**: All subsequent tasks.

#### 5.2 Changes to Epic 1 Task 1.3 if Probe Succeeds

If `claude -p` with system-prompt injection (S1) passes all three gates:

**Current Task 1.3 primary path**: Uses the Skill tool to invoke sc:adversarial.

**Proposed modification to sub-step 3d**: Replace Skill tool call with `claude -p` invocation:

```
3d. Invoke sc:adversarial via headless session:
    - Construct prompt: pipeline trigger with file paths and parameters
    - Construct system prompt: full SKILL.md content via file read
    - Execute: Bash tool call to `claude -p` with:
      --append-system-prompt (SKILL.md content)
      --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task"
      --permission-mode bypassPermissions
      --output-format json
      --max-budget-usd 3.00
      --model (from --agents spec)
    - Parse JSON output for completion status
    - If exit code != 0 OR no artifacts produced: execute fallback (sub-step 3d-fallback)
    - If retry configured (Gate 3 = 70-79%): retry once before fallback
```

**Implications for allowed-tools**: The `Skill` tool no longer needs to be in `allowed-tools` for the primary path. However, Tasks 1.1 and 1.2 (adding Skill to allowed-tools) should remain for forward compatibility — the Skill tool may become viable in future Claude Code versions.

**Implications for the fallback protocol**: The fallback protocol (F1-F5) remains unchanged. It activates when `claude -p` invocation fails, exactly as the current fallback activates when the Skill tool fails.

#### 5.3 Fallback-Only Variant (if probe fails)

If all three strategies fail at Gate 1, or behavioral quality fails at Gate 2, or reliability is below 70% at Gate 3:

The sprint proceeds with the **existing Fallback-Only Sprint Variant** (already defined in the sprint-spec, lines 90-111). No changes needed to the fallback-only variant — it is already designed for exactly this scenario.

The only modification: in the Fallback-Only Sprint Variant table, change the "Trigger" description from:

> Task 0.0 decision gate returns "primary path blocked" (Skill tool cannot invoke a second skill...)

To:

> Task 0.0A decision gate returns "primary path blocked" (neither Skill tool nor `claude -p` headless invocation can reliably invoke sc:adversarial with sufficient behavioral adherence).

#### 5.4 Time Estimate for Probe Phase

| Activity | Time | Cost |
|----------|------|------|
| Fixture preparation (spec-minimal.md, variant-a.md, variant-b.md) | 20 min | $0 |
| Phase 1: Smoke test (T01) | 2 min | $0.10 |
| Phase 2: Strategy selection (T02, T03, T04) | 15 min | $6.00 |
| Phase 3: Deep validation (T05-T10, T12, T13) | 30 min | $3.00 |
| Phase 4: Reliability test (T11, 10 runs) | 45 min | $15-25 |
| Summary report and decision documentation | 15 min | $0 |
| **Total** | **~2 hours** | **~$25-35** |

**If probe fails at Gate 1**: Total time is ~40 minutes, total cost is ~$6. Early failure is cheap.

---

### 6. Risk Analysis

#### Risk A: `claude -p` works but unreliably (60-70% success rate)

**Probability**: MEDIUM (0.35)
**Impact**: Feature ships but users experience intermittent failures.

**Mitigation options**:
1. **Retry wrapper**: Add a retry loop (max 2 retries) around the `claude -p` invocation. At 65% per-attempt success, 2 retries gives 95.7% overall success: `1 - (0.35)^3 = 0.957`.
2. **Hybrid approach**: Use `claude -p` for the debate steps (Steps 1-3) and inline Task agents for scoring and merge (Steps 4-5). This reduces the headless session's responsibility and may improve reliability.
3. **Conditional routing**: If `claude -p` fails, silently fall back to the inline fallback protocol. Users get degraded quality but never see an error.

**Decision**: If reliability is 60-70%, implement option 1 (retry wrapper) AND option 3 (silent fallback). This gives a user-facing reliability of ~99% at the cost of occasional degraded quality.

#### Risk B: Slash command works but project-scoped command does not (or vice versa)

**Probability**: MEDIUM (0.40)
**Impact**: LOW — the probe tests all three strategies independently. We select whichever works.

**Mitigation**: The three-strategy design inherently mitigates this. If only one strategy works, we use that one. The sprint-spec modification in Section 5.2 is parameterized by strategy — the same Task 1.3 rewrite works regardless of which `claude -p` invocation form is used.

#### Risk C: `--append-system-prompt` works better than slash command invocation

**Probability**: HIGH (0.60) — this is the expected outcome based on Issue #1048 analysis.
**Impact**: POSITIVE — system-prompt injection gives us more control than slash commands.

**Implications**: If S1 (system-prompt injection) is the winning strategy, we gain additional capabilities:
- We can augment the SKILL.md with additional behavioral anchoring instructions
- We can inject a preamble that explicitly names the return contract requirement
- We can strip non-essential sections from SKILL.md to save context tokens
- We decouple from Claude Code's slash command loading mechanism entirely

**Action**: If S1 wins, document the system-prompt injection pattern as the canonical cross-skill invocation mechanism for SuperClaude. This becomes a framework-level pattern, not just an sc:roadmap workaround.

#### Risk D: Each invocation costs $2+

**Probability**: MEDIUM (0.30) — depends on model, variant count, and debate depth.
**Impact**: Feature economically questionable for frequent use.

**Mitigation options**:
1. **Model tiering**: Use sonnet/haiku for debate rounds (cheaper), opus only for scoring/merge (quality-critical).
2. **Depth control**: Default to `--depth quick` (1 round) for cost-sensitive users, `--depth deep` (3 rounds) only when explicitly requested.
3. **Budget caps**: The `--max-budget-usd` flag provides hard cost limits. Document recommended budgets per depth level.
4. **Caching**: If the same spec is debated multiple times, cache diff-analysis across runs.

**Decision**: T10 measures actual cost. If > $2, implement model tiering (option 1) and re-test. If still > $2 with sonnet, document the cost prominently and let users decide.

#### Risk E: SKILL.md is too large for system-prompt injection

**Probability**: LOW (0.15) — sc-adversarial SKILL.md is ~1400 lines, roughly 8,000-10,000 tokens. Context windows are 200K+.
**Impact**: HIGH if triggered — cannot use S1 strategy.

**Mitigation**: T12 measures this directly. If SKILL.md + variants exceed 40K tokens, strip non-essential sections (examples, templates, configuration tables) from the injected SKILL.md. The core protocol (5 steps, ~300 lines) is what matters.

#### Risk F: `claude -p` is not installed or not available in the execution environment

**Probability**: LOW (0.10) — `claude` CLI is the prerequisite for Claude Code.
**Impact**: HIGH — entire probe fails.

**Mitigation**: T01 catches this in 2 minutes. If `claude -p` is not available, the probe aborts immediately with zero wasted time, and we route to fallback-only.

#### Risk G: Behavioral drift worsens over time (works today, unreliable in 3 months)

**Probability**: MEDIUM (0.25) — model updates can change behavioral adherence.
**Impact**: MEDIUM — feature degrades silently.

**Mitigation**: Add a lightweight regression test to the project's test suite. A single `claude -p` invocation with a tiny fixture, checking for artifact production and basic structure. Run as part of `make test` or as a manual smoke test before releases.

---

### Appendix A: Probe Runner Script Skeleton

```bash
#!/usr/bin/env bash
# probe-runner.sh — claude -p viability probe for sc:adversarial invocation
# Usage: bash probe-runner.sh [--skip-reliability] [--strategy S1|S2|S3]

set -euo pipefail

EVIDENCE_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$EVIDENCE_DIR/probe-fixtures"
REPO_ROOT="$(cd "$EVIDENCE_DIR/../../../../.." && pwd)"
SKILL_PATH="$REPO_ROOT/src/superclaude/skills/sc-adversarial/SKILL.md"

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
BEST_STRATEGY=""
BEST_STRATEGY_SCORE=0

log() { echo "[$(date +%H:%M:%S)] $*"; }
pass() { ((TESTS_PASSED++)); log "PASS: $1"; }
fail() { ((TESTS_FAILED++)); log "FAIL: $1"; }

# Phase 1: Smoke Test
run_t01() { ... }

# Phase 2: Strategy Selection
run_t02() { ... }
run_t03() { ... }
run_t04() { ... }

# Phase 3: Deep Validation
run_t05() { ... }  # Behavioral adherence (manual scoring, outputs rubric template)
run_t06() { ... }  # Artifact production
run_t07() { ... }  # Multi-round debate
run_t08() { ... }  # Return contract
run_t09() { ... }  # Model selection
run_t10() { ... }  # Cost measurement
run_t12() { ... }  # Context pressure
run_t13() { ... }  # Error handling

# Phase 4: Reliability
run_t11() { ... }  # 10 runs

# Summary
generate_summary() {
  cat > "$EVIDENCE_DIR/probe-summary.md" <<EOF
## Probe Summary

**Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Tests run**: $TESTS_RUN
**Passed**: $TESTS_PASSED
**Failed**: $TESTS_FAILED
**Best strategy**: $BEST_STRATEGY
**Best strategy score**: $BEST_STRATEGY_SCORE

### Gate Decisions

- Gate 1 (Strategy Viability): [PASS/FAIL]
- Gate 2 (Behavioral Quality): [PASS/FAIL]
- Gate 3 (Reliability): [PASS/FAIL/SKIPPED]

### Sprint Decision

[HEADLESS_PRIMARY / HEADLESS_WITH_RETRY / FALLBACK_ONLY]

### Evidence Files

$(ls -1 "$EVIDENCE_DIR"/T*.json "$EVIDENCE_DIR"/T*.txt 2>/dev/null || echo "None")
EOF
}

# Main
main() {
  log "Starting claude -p viability probe"
  log "Evidence directory: $EVIDENCE_DIR"

  # Phase 1
  run_t01 || { log "ABORT: claude -p not functional"; generate_summary; exit 1; }

  # Phase 2 (run all three, pick best)
  run_t02 &
  run_t03 &
  run_t04 &
  wait

  select_best_strategy  # Sets BEST_STRATEGY
  [ -z "$BEST_STRATEGY" ] && { log "ABORT: no viable strategy"; generate_summary; exit 1; }

  # Phase 3
  run_t05 && run_t06 && run_t07 && run_t08
  run_t09
  run_t10
  run_t12
  run_t13

  # Gate 2 check
  check_gate_2 || { log "ABORT: behavioral quality insufficient"; generate_summary; exit 1; }

  # Phase 4 (skip if --skip-reliability)
  if [[ "${1:-}" != "--skip-reliability" ]]; then
    run_t11
  fi

  generate_summary
  log "Probe complete. See $EVIDENCE_DIR/probe-summary.md"
}

main "$@"
```

---

### Appendix B: Return Contract JSON Schema (expected-schema.yaml)

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
type: object
required:
  - schema_version
  - status
  - convergence_score
  - merged_output_path
  - artifacts_dir
  - unresolved_conflicts
  - base_variant
  - failure_stage
  - fallback_mode
properties:
  schema_version:
    type: string
    const: "1.0"
  status:
    type: string
    enum: [success, partial, failed]
  convergence_score:
    type: [number, "null"]
    minimum: 0.0
    maximum: 1.0
  merged_output_path:
    type: [string, "null"]
  artifacts_dir:
    type: string
  unresolved_conflicts:
    type: [integer, "null"]
    minimum: 0
  base_variant:
    type: [string, "null"]
  failure_stage:
    type: [string, "null"]
  fallback_mode:
    type: boolean
```

---

*Proposal generated 2026-02-23. Analyst: claude-opus-4-6 (system-architect persona).*
*Inputs: sprint-spec.md, sc-adversarial/SKILL.md, sc-roadmap/SKILL.md, GitHub Issues #837 and #1048.*
*Decision framework: 3 strategies, 13 test cases, 3 sequential gates, 7 identified risks.*
