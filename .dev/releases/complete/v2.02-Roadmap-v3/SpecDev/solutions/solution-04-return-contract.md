# Solution 04: Return Contract Data Flow

## Problem Summary

The return contract between sc:adversarial and sc:roadmap defines 6 structured fields (`status`, `merged_output_path`, `convergence_score`, `artifacts_dir`, `unresolved_conflicts`, `base_variant`) but has **no transport mechanism**. Task agents return unstructured text. The consuming skill (sc:roadmap) documents detailed consumption logic in `refs/adversarial-integration.md` -- status routing, convergence thresholds, frontmatter population -- but none of it can execute because there is no way for the data to travel from producer to consumer.

The only working inter-agent data flow pattern in the codebase is sc:cleanup-audit's fan-out/fan-in model, which uses **file-based orchestration**: subagents write batch reports to disk, the orchestrator reads and merges them. The adversarial return contract does not adopt this pattern.

**Root cause rank**: 4 of 5 (combined score 0.75). This is a latent defect -- it would surface once RC1 (invocation wiring) and RC2 (spec-execution gap) are fixed, even if never the active cause of the observed failure.

---

## Options Analysis

### Option A: File-Based Contract

sc:adversarial writes `return-contract.yaml` to the output directory as its final step. sc:roadmap reads it after invocation completes.

| Dimension | Assessment |
|-----------|------------|
| **Reliability** | High. File I/O is deterministic. If the file exists, it has the data. If it does not exist, the invocation failed. Binary signal. |
| **Inspectability** | High. Human-readable YAML on disk. Debuggable with `cat`. Survives session crashes. Persists for post-mortem analysis. |
| **Precedent** | Direct. sc:cleanup-audit uses exactly this pattern: subagents write structured reports to `.claude-audit/`, orchestrator reads and merges. This is the proven inter-agent data flow in the codebase. |
| **Coupling** | Moderate. Both skills must agree on filename (`return-contract.yaml`) and schema. However, the schema is already defined -- only the filename convention and write/read instructions need to be added. |
| **Complexity** | Low. One Write instruction in sc:adversarial, one Read instruction in sc:roadmap. No parsing logic beyond YAML. |
| **Failure modes** | File not written (pipeline crashed before final step). File written with partial data (pipeline interrupted mid-write). Both detectable by existence check + schema validation. |

### Option B: Structured Text in Task Agent Return

The debate-orchestrator Task agent outputs YAML-formatted return contract as its final text response. The calling code parses it from the text.

| Dimension | Assessment |
|-----------|------------|
| **Reliability** | Low. Task agent text output is unstructured free text. Claude may add commentary, formatting, or explanations around the YAML block. Extraction requires regex or delimiter-based parsing. |
| **Inspectability** | Low. The contract is embedded in a potentially long agent response. No persistent artifact. If the session ends, the data is lost. |
| **Precedent** | None. No skill in the codebase uses structured text parsing of Task agent output. The `machine-readable headers` pattern (Section 5.8 of the Developer Guide) uses HTML comment blocks in file output, not in agent text responses. |
| **Coupling** | Low nominal, high practical. No file agreement needed, but the calling code must know the exact delimiters and handle arbitrary surrounding text. |
| **Complexity** | High. Requires a parsing protocol (start/end delimiters, YAML extraction, error handling for malformed output). Fragile to model behavior changes. |
| **Failure modes** | Model adds natural language around YAML. Model uses slightly different field names. Model omits the block entirely. Model outputs valid YAML but with wrong indentation. All are silent failures -- no crash, just wrong data. |

### Option C: Convention-Based Discovery

Define naming conventions so the caller knows where to find outputs (e.g., `<output>/adversarial/merged-output.md`, `<output>/adversarial/scoring-summary.md`). The caller extracts contract fields from within those files.

| Dimension | Assessment |
|-----------|------------|
| **Reliability** | Moderate. File existence is reliable, but extracting `convergence_score` from within a scoring summary requires content parsing. |
| **Inspectability** | High for files. Low for extracted values -- the caller must know which file contains which field and how to extract it. |
| **Precedent** | Partial. sc:adversarial already produces artifacts in an `adversarial/` directory. But the artifacts are prose documents, not structured data carriers. |
| **Coupling** | High. The caller must understand the internal structure of multiple adversarial output files. Any format change in those files breaks extraction. |
| **Complexity** | High. Multiple files to read, multiple extraction patterns, multiple failure points. The contract is distributed across files rather than centralized. |
| **Failure modes** | File format changes silently break extraction. A renamed section heading in scoring-summary.md causes convergence_score extraction to fail. No single point of validation. |

### Option D: Hybrid (File + Text)

Write `return-contract.yaml` to disk AND include it in the Task agent's text response.

| Dimension | Assessment |
|-----------|------------|
| **Reliability** | Highest. Two independent channels. File is the primary; text is the backup. |
| **Inspectability** | High. File on disk for persistence. Text for immediate consumption. |
| **Precedent** | None. No skill uses dual-channel return. |
| **Coupling** | Same as Option A (file agreement), plus Option B's parsing overhead. |
| **Complexity** | Moderate. The file write is simple. The text parsing adds complexity but is optional (used only if file read fails). |
| **Failure modes** | Same as Option A for primary channel. If file is missing, falls back to text parsing with Option B's fragility. The redundancy is real but the fallback channel is unreliable. |

### Comparative Matrix

| Criterion | Weight | A: File | B: Text | C: Convention | D: Hybrid |
|-----------|--------|---------|---------|---------------|-----------|
| Reliability | 0.30 | 9 | 4 | 6 | 9 |
| Simplicity | 0.25 | 9 | 5 | 4 | 7 |
| Precedent alignment | 0.20 | 10 | 2 | 5 | 5 |
| Inspectability | 0.15 | 9 | 4 | 7 | 9 |
| Maintenance cost | 0.10 | 8 | 4 | 3 | 6 |
| **Weighted Score** | | **9.15** | **3.95** | **5.15** | **7.45** |

---

## Recommended Solution: Option A -- File-Based Contract

**Rationale**: Option A scores highest across all weighted dimensions. It follows the only proven inter-agent data flow precedent in the codebase (sc:cleanup-audit), requires the fewest changes, introduces no parsing fragility, and produces a persistent, inspectable artifact. The hybrid option (D) adds complexity for marginal reliability gain -- the file channel is already deterministic, so the text fallback provides little value while doubling the implementation surface.

---

## Implementation Details

### Data Flow Diagram

```
sc:roadmap (orchestrator)
    |
    | [1] Invoke sc:adversarial via Skill tool
    |     (passes --compare/--source, --depth, --output, --interactive)
    |
    v
sc:adversarial (invoked skill)
    |
    | [2] Execute 5-step adversarial pipeline
    |     Step 1: Variant generation/loading
    |     Step 2: Diff analysis
    |     Step 3: Structured debate
    |     Step 4: Scoring + base selection
    |     Step 5: Merge execution
    |
    | [3] Write process artifacts to <output-dir>/adversarial/
    |     - variant-*.md (generated variants)
    |     - diff-analysis.md
    |     - debate-transcript.md
    |     - scoring-summary.md
    |     - merged-output.md
    |     - merge-log.md
    |
    | [4] Write return-contract.yaml to <output-dir>/adversarial/
    |     (MANDATORY final step -- must execute even on partial/failed status)
    |
    v
sc:roadmap (resumes after invocation)
    |
    | [5] Read <output-dir>/adversarial/return-contract.yaml
    |
    | [6] Validate schema (all required fields present, types correct)
    |     - If file missing: abort with "sc:adversarial did not produce return contract"
    |     - If schema invalid: abort with "Return contract malformed: <missing fields>"
    |
    | [7] Route on status field
    |     - success: use merged_output_path, record frontmatter
    |     - partial: check convergence threshold (60%), apply routing logic
    |     - failed: abort with diagnostics from artifacts_dir
    |
    | [8] Populate roadmap.md frontmatter with contract fields
    |     (convergence_score, base_variant, artifacts_dir)
    |
    v
  Continue to subsequent waves
```

### Changes Required

#### 1. sc:adversarial SKILL.md -- Add mandatory write step

**Location**: `src/superclaude/skills/sc-adversarial/SKILL.md`, Return Contract section (line ~339)

**Change**: Replace the current return contract section (which only defines the schema in documentation) with an actionable write instruction.

```markdown
## Return Contract (FR-007)

When invoked by another command, sc:adversarial MUST write the return contract
to disk as its final step, regardless of pipeline outcome.

### Write Location

```
<output-dir>/adversarial/return-contract.yaml
```

Where `<output-dir>` is the value of the `--output` flag passed to sc:adversarial.

### Write Instruction

After the 5-step pipeline completes (or on abort), write the following YAML file:

```yaml
# sc:adversarial return contract
# Written automatically as final pipeline step
# Schema version: 1.0

status: "<success|partial|failed>"
merged_output_path: "<absolute or relative path to merged file>"
convergence_score: <float 0.0-1.0>
artifacts_dir: "<path to adversarial/ directory>"
unresolved_conflicts: <integer count of unresolved items>
base_variant: "<model:persona of winning variant>"
schema_version: "1.0"
timestamp: "<ISO 8601 timestamp>"
```

### Write Timing

- **On success**: Write after merge validation passes (Step 5 complete)
- **On partial**: Write after pipeline completes with warnings
- **On failed**: Write immediately upon abort decision, with fields populated as far as the pipeline progressed:
  - `merged_output_path`: empty string if merge was not attempted
  - `convergence_score`: 0.0 if scoring was not reached
  - `base_variant`: empty string if selection was not reached
  - `unresolved_conflicts`: -1 if conflict counting was not reached

### Critical Rule

**The return contract file MUST be written even when status is "failed".** The consuming skill uses the file's existence as a signal that sc:adversarial completed (successfully or not). A missing file means the pipeline crashed -- a fundamentally different failure mode than a pipeline that ran and reported failure.
```

#### 2. sc:roadmap refs/adversarial-integration.md -- Add read instructions

**Location**: `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`, Return Contract Consumption section (line ~139)

**Change**: Add explicit file read instructions before the existing status routing logic.

```markdown
## Return Contract Consumption

### Reading the Return Contract

After sc:adversarial invocation completes, read the return contract file:

```
Read <output-dir>/adversarial/return-contract.yaml
```

**File existence check**:
- If file exists: parse YAML and proceed to status routing
- If file does NOT exist: the adversarial pipeline crashed before completion.
  Abort with: "sc:adversarial did not produce a return contract.
  Check <output-dir>/adversarial/ for partial artifacts."

**Schema validation**: Verify all required fields are present:
- `status` (required, must be one of: success, partial, failed)
- `merged_output_path` (required, string)
- `convergence_score` (required, float)
- `artifacts_dir` (required, string)
- `unresolved_conflicts` (required, integer)
- `base_variant` (required in multi-roadmap mode, string)

If any required field is missing, abort with:
"Return contract schema validation failed. Missing fields: <list>.
This indicates a bug in sc:adversarial. Report as framework issue."

### Status Routing

[...existing status routing logic remains unchanged...]
```

#### 3. Add `base_variant` to sc:adversarial return contract schema

**Location**: `src/superclaude/skills/sc-adversarial/SKILL.md`, Return Contract section

**Change**: The current return contract definition (lines 343-350) lists 5 fields but omits `base_variant`, which sc:roadmap's `adversarial-integration.md` expects (line 152) and uses for frontmatter population (line 223). Add it:

```yaml
return_contract:
  status: "<success|partial|failed>"
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  unresolved_conflicts: <integer>
  base_variant: "<model:persona of variant selected as merge base>"
  schema_version: "1.0"
  timestamp: "<ISO 8601>"
```

---

## YAML Schema Definition

```yaml
# return-contract.yaml schema v1.0
# Location: <output-dir>/adversarial/return-contract.yaml
# Producer: sc:adversarial (final pipeline step)
# Consumer: any invoking skill (sc:roadmap, future skills)

# --- Required Fields ---

status:
  type: string
  enum: [success, partial, failed]
  description: >
    Pipeline outcome. "success" = all 5 steps completed and post-merge
    validation passed. "partial" = pipeline completed with warnings or
    validation failures. "failed" = pipeline aborted.
  required: true

merged_output_path:
  type: string
  description: >
    Path to the merged output file (relative to output-dir or absolute).
    Empty string when status is "failed" and merge was not attempted.
  required: true
  example: "./adversarial/merged-output.md"

convergence_score:
  type: float
  range: [0.0, 1.0]
  description: >
    Final convergence percentage from the adversarial debate.
    0.0 when scoring was not reached (failed status).
  required: true
  example: 0.85

artifacts_dir:
  type: string
  description: >
    Path to the adversarial/ directory containing all process artifacts
    (variants, diff analysis, debate transcript, scoring summary, merge log).
  required: true
  example: "./adversarial/"

unresolved_conflicts:
  type: integer
  description: >
    Count of diff points where no resolution was reached during debate.
    -1 when conflict counting was not reached (early failure).
    0 when all conflicts were resolved.
  required: true
  example: 2

base_variant:
  type: string
  description: >
    Identifier of the variant selected as the merge base, in the format
    "model:persona" (e.g., "opus:security"). Empty string when base
    selection was not reached.
  required: true
  example: "opus:architect"

# --- Metadata Fields ---

schema_version:
  type: string
  description: >
    Schema version for forward compatibility. Consumers should check this
    field and warn (not abort) if the version is newer than expected.
  required: true
  value: "1.0"

timestamp:
  type: string
  format: ISO 8601
  description: >
    Timestamp of when the return contract was written. Useful for
    correlating with session logs and debugging timing issues.
  required: true
  example: "2026-02-22T14:30:00Z"
```

### Example: Successful Return Contract

```yaml
# sc:adversarial return contract
# Schema version: 1.0

status: success
merged_output_path: ./adversarial/merged-output.md
convergence_score: 0.87
artifacts_dir: ./adversarial/
unresolved_conflicts: 0
base_variant: "opus:architect"
schema_version: "1.0"
timestamp: "2026-02-22T14:30:00Z"
```

### Example: Partial Return Contract

```yaml
status: partial
merged_output_path: ./adversarial/merged-output.md
convergence_score: 0.62
artifacts_dir: ./adversarial/
unresolved_conflicts: 3
base_variant: "sonnet:security"
schema_version: "1.0"
timestamp: "2026-02-22T14:45:00Z"
```

### Example: Failed Return Contract

```yaml
status: failed
merged_output_path: ""
convergence_score: 0.0
artifacts_dir: ./adversarial/
unresolved_conflicts: -1
base_variant: ""
schema_version: "1.0"
timestamp: "2026-02-22T14:50:00Z"
```

---

## Blast Radius Assessment

### Files Modified

| File | Change Type | Risk |
|------|-------------|------|
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Add write instruction to Return Contract section; add `base_variant` field; add `schema_version` and `timestamp` metadata fields | Low -- additive change to existing section |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Add Read instruction and schema validation before existing status routing logic | Low -- prepends to existing logic, does not alter routing |

### Files NOT Modified

| File | Reason |
|------|--------|
| `src/superclaude/commands/roadmap.md` | Command file delegates to SKILL.md; no contract logic here |
| `src/superclaude/commands/adversarial.md` | Command file delegates to SKILL.md; no contract logic here |
| `src/superclaude/skills/sc-adversarial/refs/*` | Ref files contain protocol details, not return contract logic |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Waves 1A and 2 already reference `refs/adversarial-integration.md` for return contract handling |

### Downstream Impact

| System | Impact | Severity |
|--------|--------|----------|
| sc:roadmap multi-spec mode (Wave 1A) | Gains working data flow from sc:adversarial | Positive |
| sc:roadmap multi-roadmap mode (Wave 2) | Gains working data flow from sc:adversarial | Positive |
| sc:roadmap standard mode (no adversarial) | No impact -- adversarial block remains absent from frontmatter | None |
| sc:adversarial standalone usage | Adds one file write to output directory. No behavioral change to the 5-step pipeline itself. | Negligible |
| Future skills consuming sc:adversarial | Gain a documented, versioned contract schema to program against | Positive |
| sc:cleanup-audit | No impact -- different skill, different data flow pattern | None |
| Existing adversarial artifacts | No impact -- return-contract.yaml is a new file alongside existing artifacts | None |

### Risk Factors

| Risk | Probability | Mitigation |
|------|-------------|------------|
| sc:adversarial crashes before writing contract file | Moderate | sc:roadmap checks for file existence and reports "pipeline crashed" (distinct from "pipeline failed") |
| Schema evolution breaks consumers | Low | `schema_version` field enables forward-compatible version checking. Consumers warn on unknown version, do not abort. |
| File write fails (disk full, permissions) | Very low | Same risk as all other file writes in the pipeline. No special mitigation needed beyond standard error handling. |
| YAML formatting errors in generated contract | Low | Schema is simple (flat, no nesting). Claude's YAML generation for flat key-value structures is highly reliable. |

### Dependency on Other Fixes

This solution is **independent** of Fix 1 (Skill tool in allowed-tools) and Fix 2 (Wave 2 rewrite). However, it only becomes exercisable once Fix 1 is applied -- without the ability to invoke sc:adversarial, no return contract will ever be produced.

**Recommended implementation order**: Fix 1 (invocation wiring) -> Fix 3 (this solution) -> Fix 2 (spec rewrite). The return contract convention should exist before the spec rewrite references it.

---

## Confidence Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Problem diagnosis accuracy | 0.90 | The gap is concrete and verifiable: 6 fields defined, 0 transport. |
| Solution correctness | 0.90 | File-based contracts are the proven pattern in this codebase. The sc:cleanup-audit precedent validates the approach. |
| Implementation completeness | 0.85 | The changes are well-scoped (2 files), but depend on Fix 1 for end-to-end testing. |
| Blast radius containment | 0.95 | Additive changes only. No existing behavior modified. No schema migration needed. |
| Forward compatibility | 0.85 | `schema_version` field enables evolution. But the convention of a single flat YAML file may need extension if future skills require richer return types (nested structures, binary data). |
| **Overall confidence** | **0.88** | High confidence. The simplest option that follows the established pattern, with clear schema versioning for future evolution. |

---

*Solution designed 2026-02-22. Analyst: claude-opus-4-6 (system-architect persona).*
*Addresses: RC4 (Return Contract Data Flow), Fix 3 from ranked-root-causes.md minimal fix set.*
