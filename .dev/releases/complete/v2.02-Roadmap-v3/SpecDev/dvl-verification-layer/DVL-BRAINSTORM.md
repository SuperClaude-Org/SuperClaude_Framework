# Deterministic Verification Layer (DVL) — Brainstorm

> **Status**: BRAINSTORM ONLY — ideas, strategies, and approach. Not approved for implementation.
> **Origin**: Extracted from sprint-spec.md on 2026-02-23. Originally added via `/sc:brainstorm --depth deep --parallel --strategy systematic`
> **Sprint context**: `.dev/releases/current/v2.1-CleanupAudit-v2/sprint-spec.md`

## Problem Statement

The current workflow relies on agents to **self-report** completion, score accuracy, and artifact validity. This fails in three ways:
1. **Hallucination**: Agents claim files exist that don't, cite lines that don't match, report scores with arithmetic errors
2. **Context rot**: Long-running agents lose track of their task ID, input constraints, or earlier phase findings
3. **Silent degradation**: The original sc:roadmap failure *was* silent — it produced output that looked reasonable but bypassed 80% of the pipeline

**Core insight**: Separate what CAN be verified programmatically (structure, existence, math, schemas) from what REQUIRES intelligence (analysis depth, reasoning quality). Never ask agents to self-report on the programmatic half.

## Architecture: Three Verification Tiers

```
┌──────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                           │
│  (outer loop — fresh context, runs all scripts)          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tier 1: PRE-GATES          (before agent starts)        │
│  ├── verify_allowed_tools.py                             │
│  ├── dependency_gate.sh                                  │
│  └── content_hash_tracker.py  (snapshot inputs)          │
│                                                          │
│  Tier 2: POST-GATES         (after agent claims done)    │
│  ├── validate_return_contract.py                         │
│  ├── verify_pipeline_completeness.sh                     │
│  ├── validate_wave2_spec.py                              │
│  ├── verify_numeric_scores.py                            │
│  ├── check_file_references.py                            │
│  └── content_hash_tracker.py  (verify inputs unchanged)  │
│                                                          │
│  Tier 3: CROSS-PHASE        (at checkpoint boundaries)   │
│  └── generate_checkpoint.py   (replaces agent-written)   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Output: .verified sentinel files + script-generated     │
│  checkpoints = immutable audit trail                     │
└──────────────────────────────────────────────────────────┘
```

**Key design principle**: The ORCHESTRATOR runs all verification scripts, not the sub-agents. Sub-agents do creative work (analysis, writing, synthesis). Scripts produce binary pass/fail. Failure = hard stop, not soft warning.

## Script Inventory (10 Scripts, 3 Categories)

### Priority Assessment (from reflection-final.md)

| Script | Priority | Rationale |
|--------|----------|-----------|
| `verify_allowed_tools.py` | **KEEP** — implement with sprint | Highest value, simplest, directly validates Epic 1 |
| `validate_return_contract.py` | **KEEP** — implement with sprint | Highest value, validates Epic 3 acceptance criteria |
| `validate_wave2_spec.py` | **KEEP** — implement if time permits | Validates Epic 2; manual checklist is acceptable substitute |
| `verify_pipeline_completeness.sh` | DEFER | Only useful after end-to-end test |
| `dependency_gate.sh` | DEFER | Overkill for 3 epics with clear human-managed ordering |
| `check_file_references.py` | DEFER | Useful for general quality but not sprint-critical |
| `generate_checkpoint.py` | DEFER | Workflow improvement, not a fix for the adversarial pipeline |
| `content_hash_tracker.py` | CUT | Risk R5 mitigated by single-author constraint |
| `verify_numeric_scores.py` | CUT | No numeric scoring in this sprint's deliverables |
| `context_rot_canary.py` | CUT | Untested concept; high effort for speculative benefit |

### Tier 1: Pre-Execution Gate Scripts

**1. `verify_allowed_tools.py`**
- **Purpose**: Parse SKILL.md / roadmap.md frontmatter, assert required tools are present
- **Input**: File path + list of required tool names
- **Logic**: Read file → extract `allowed-tools:` line → parse as comma-separated list → check membership
- **Output**: Exit 0 (all present) or exit 1 (missing tools listed to stderr)
- **Cost**: <50ms, deterministic
- **Sprint tie-in**: Epic 1 tasks 1.1/1.2 acceptance criteria. Run BEFORE any agent touches Wave 2.

**2. `dependency_gate.sh`**
- **Purpose**: Verify all blocking tasks' output files exist before allowing a task to start
- **Input**: Task ID + dependency manifest (JSON: `{task_id: [expected_file_paths]}`)
- **Logic**: For each dependency, check all expected output files exist and are non-empty
- **Output**: Exit 0 (all deps satisfied) or exit 1 (missing files listed)
- **Cost**: <100ms, deterministic
- **Sprint tie-in**: Enforces the dependency graph (Epic 2 can't start until Epic 1 artifacts exist)

**3. `content_hash_tracker.py`**
- **Purpose**: Snapshot input file hashes at task start; verify unchanged at task end
- **Input**: List of input file paths + mode (`snapshot` | `verify`)
- **Logic**: SHA-256 hash each file → write/compare `.input-hashes.json` manifest
- **Output**: Exit 0 (all match) or exit 1 (changed files listed — indicates concurrent modification or context confusion)
- **Cost**: <200ms, deterministic
- **Sprint tie-in**: Catches if SKILL.md is modified by one agent while another is reading it (Risk R5)

### Tier 2: Post-Execution Structural Validators

**4. `validate_return_contract.py`** *(highest value script)*
- **Purpose**: Validate return-contract.yaml against the canonical schema
- **Input**: Path to return-contract.yaml
- **Logic**:
  1. Parse as YAML (fail if malformed)
  2. Check `schema_version` field exists and equals "1.0"
  3. Check all 9 required fields present (`status`, `convergence_score`, `merged_output_path`, `artifacts_dir`, `unresolved_conflicts`, `base_variant`, `failure_stage`, `schema_version`, `fallback_mode`)
  4. Validate types: `status` ∈ {success, partial, failed}, `convergence_score` ∈ [0.0, 1.0], `fallback_mode` ∈ {true, false}, paths resolve to existing files (when status=success)
  5. Validate status-specific constraints: `merged_output_path` must be non-null when status=success; `failure_stage` must be non-null when status=failed
  6. Validate null usage: unreached fields must be null (not -1, not "")
- **Output**: Structured JSON verdict: `{valid: bool, errors: [...], warnings: [...]}`
- **Cost**: <500ms, deterministic
- **Sprint tie-in**: Epic 3 acceptance criteria. Eliminates trust in agent writing correct YAML.

**5. `verify_pipeline_completeness.sh`**
- **Purpose**: Check that ALL expected adversarial pipeline artifacts exist
- **Input**: Output directory path + expected agent count from `--agents` flag
- **Logic**: Check for: `variant-*.md` (count = agent count), `diff-analysis.md`, `debate-transcript.md`, `scoring-matrix.md`, `refactoring-plan.md`, `merged-output.md`, `return-contract.yaml`
- **Output**: Exit 0 (all present) or exit 1 (missing file checklist)
- **Cost**: <100ms, deterministic
- **Sprint tie-in**: Catches the exact original failure — agents produced some output but skipped pipeline steps

**6. `validate_wave2_spec.py`**
- **Purpose**: Parse the rewritten Wave 2 and verify structural compliance
- **Input**: Path to SKILL.md + path to verb glossary section
- **Logic**:
  1. Extract Wave 2 step 3 sub-steps (expect 3a-3f)
  2. Extract verb glossary mappings
  3. For each sub-step: verify exactly one glossary verb is used
  4. Verify step 3d contains `skill: "sc:adversarial"` syntax
  5. Verify step 3d fallback covers three error types (string match)
  6. Verify step 3e contains convergence threshold value
  7. Count ambiguous verbs ("Invoke", "Execute" without tool binding) — must be 0
- **Output**: Structured report with per-sub-step pass/fail
- **Cost**: <200ms, deterministic
- **Sprint tie-in**: Epic 2 task 2.2 acceptance criteria. Catches spec drift before runtime.

**7. `verify_numeric_scores.py`**
- **Purpose**: Extract and validate all numeric scores in ranking/debate files
- **Input**: Markdown file path + expected format (e.g., "weighted scoring matrix")
- **Logic**:
  1. Regex extract all `| ... | 0.XX | ... |` table rows
  2. Verify weights sum to 1.0 (±0.01 tolerance)
  3. Verify `weighted = weight * score` for each row (±0.01 tolerance)
  4. Verify composite = sum of weighted values
  5. Verify all scores ∈ [0.0, 1.0]
- **Output**: Exit 0 (all math checks) or exit 1 (arithmetic errors listed)
- **Cost**: <100ms, deterministic
- **Sprint tie-in**: Would have caught the RC3 score inflation (0.95→0.70) in Phase 1 of this workflow

**8. `check_file_references.py`**
- **Purpose**: Extract all file path references from markdown and verify they exist on disk
- **Input**: Markdown file path + project root
- **Logic**: Regex for `src/...`, `refs/...`, backtick-quoted paths → resolve relative to project root → check existence
- **Output**: List of valid/invalid/ambiguous references
- **Cost**: <300ms, deterministic
- **Sprint tie-in**: Catches hallucinated file paths in agent-written analysis documents

### Tier 3: Cross-Phase Validators

**9. `generate_checkpoint.py`** *(replaces agent-written checkpoints)*
- **Purpose**: Programmatically generate checkpoint files from filesystem evidence
- **Input**: Phase number + expected artifact manifest
- **Logic**:
  1. For each expected artifact: check exists, get file size, get modification timestamp
  2. If the artifact is a scoring file: run `verify_numeric_scores.py` inline
  3. If the artifact is return-contract.yaml: run `validate_return_contract.py` inline
  4. Generate CP-Px-END.md with verified checklist (checked = file exists + validates)
  5. Include hash of all artifacts for tamper detection
- **Output**: Written checkpoint file + exit code
- **Cost**: <2s, deterministic
- **Sprint tie-in**: Checkpoints become trustworthy by construction — no agent self-report

**10. `context_rot_canary.py`** *(anti-context-rot)*
- **Purpose**: Verify agent maintained context throughout its execution
- **Input**: Agent output file + expected task fingerprint (hash of task description)
- **Logic**:
  1. Check output contains the task fingerprint in its header
  2. Check output references the correct task ID and phase number
  3. Check output does not reference task IDs from other phases (cross-contamination)
  4. Check output file count matches expected (agent didn't under/over-produce)
- **Output**: Confidence score 0.0-1.0 for context integrity
- **Cost**: <200ms, deterministic
- **Sprint tie-in**: Detects when a long-running agent (e.g., debate agents at ~160s) loses track of its assignment

## Anti-Hallucination Techniques (6 Strategies)

### AH-1: Citation Verification
When an agent says "In root-cause-01.md, line 45 states X":
- Script reads the actual file at the actual line
- Fuzzy-matches the quoted text against real content (Levenshtein distance ≤ 5%)
- Flags mismatches as hallucination evidence
- **Implementation**: `check_file_references.py` extended with content matching

### AH-2: Score Consistency Checking
When an agent reports weighted scores:
- Script independently computes `weight * score` for each dimension
- Verifies composite = sum of weighted values
- Verifies weights sum to expected total (1.0)
- **Implementation**: `verify_numeric_scores.py`

### AH-3: Cross-Reference Validation
When Phase 3 references Phase 1/2 findings:
- Script extracts references like "as established in solution-02..."
- Greps the referenced file for the claimed finding
- Flags phantom references (claim not found in source)
- **Implementation**: New sub-routine in `check_file_references.py`

### AH-4: Structural Template Enforcement
Instead of trusting agents to produce correctly structured output:
- Provide a YAML/JSON schema for expected output structure
- Agent fills in the template fields
- Script validates against schema
- Missing sections caught structurally, not by agent self-report
- **Implementation**: `validate_return_contract.py` pattern, generalizable to any structured output

### AH-5: Diff-Based Completion Verification
For edit tasks (not creation tasks):
- Hash the file before the agent edits it
- Hash after the agent claims completion
- If hashes are identical → agent claimed to edit but didn't
- If diff doesn't contain expected patterns → edit was wrong/incomplete
- **Implementation**: `content_hash_tracker.py` in `verify` mode + pattern matching

### AH-6: Context Rot Canary (Task Fingerprint Echoing)
- Include a unique hash of the task description in the agent prompt
- Require the agent to echo this fingerprint in its output header
- If fingerprint is wrong or missing → agent lost context during execution
- This is a canary: if the agent can't echo its own task ID, its substantive output is suspect
- **Implementation**: `context_rot_canary.py`

## Integration Strategy

**How scripts get wired into the workflow:**

```
Orchestrator dispatches Task agent
  │
  ├─ BEFORE dispatch: Run Tier 1 pre-gates via Bash tool
  │   ├── verify_allowed_tools.py (if task modifies tool configs)
  │   ├── dependency_gate.sh (always)
  │   └── content_hash_tracker.py --snapshot (always)
  │
  ├─ Agent executes creative work
  │   └── (analysis, writing, synthesis — agent's domain)
  │
  ├─ AFTER agent returns: Run Tier 2 post-gates via Bash tool
  │   ├── Task-specific validators (e.g., validate_return_contract.py)
  │   ├── verify_numeric_scores.py (if output contains scoring)
  │   ├── check_file_references.py (if output references files)
  │   ├── content_hash_tracker.py --verify (always)
  │   └── context_rot_canary.py (always)
  │
  ├─ AT PHASE BOUNDARY: Run Tier 3 cross-phase validators
  │   └── generate_checkpoint.py (replaces agent-written CP-Px-END.md)
  │
  └─ PASS/FAIL decision
      ├── ALL scripts exit 0 → Mark task complete, produce .verified sentinel
      └── ANY script exit 1 → HARD STOP, report failure, do NOT proceed
```

**Sentinel File Convention:**
- Scripts produce `<output-dir>/.verified-<task-id>` on success
- Sentinel contains: timestamp, script versions, input hashes, validation details
- `dependency_gate.sh` checks for sentinel files (not just output files)
- Creates an **immutable audit trail** that no agent can fabricate

**Failure Handling:**
- Script failure = task failure (no soft warnings)
- Orchestrator reports which script failed and what it found
- Agent output is preserved for debugging but NOT accepted as valid
- Retry with fresh agent (not the same agent — context may be corrupted)

## Script Location and Packaging

```
scripts/
└── dvl/                           # Deterministic Verification Layer
    ├── __init__.py                # Shared utilities (YAML parsing, hash, regex)
    ├── tier1/
    │   ├── verify_allowed_tools.py
    │   ├── dependency_gate.sh
    │   └── content_hash_tracker.py
    ├── tier2/
    │   ├── validate_return_contract.py
    │   ├── verify_pipeline_completeness.sh
    │   ├── validate_wave2_spec.py
    │   ├── verify_numeric_scores.py
    │   └── check_file_references.py
    ├── tier3/
    │   ├── generate_checkpoint.py
    │   └── context_rot_canary.py
    └── schemas/
        ├── return-contract.schema.yaml   # Canonical schema for validation
        └── scoring-matrix.schema.yaml    # Expected scoring format
```

**Dependencies**: Python stdlib only (yaml via `PyYAML`, already in most environments). Bash scripts use only coreutils. No external dependencies = no installation friction.

## Applicability Beyond This Sprint

The DVL pattern is **generalizable** to any multi-agent workflow in SuperClaude:

| Workflow | Pre-Gate | Post-Gate | Cross-Phase |
|----------|----------|-----------|-------------|
| sc:roadmap adversarial pipeline | verify_allowed_tools, dependency_gate | validate_return_contract, verify_pipeline_completeness | generate_checkpoint |
| sc:cleanup-audit multi-pass | dependency_gate (pass ordering) | verify file classifications match evidence | consolidate pass reports |
| sc:task-unified STRICT tier | dependency_gate, content_hash_tracker | verify_numeric_scores (if scored), check_file_references | generate_checkpoint |
| sc:adversarial debate pipeline | dependency_gate | verify_numeric_scores (scoring matrix), validate debate structure | final scoring validation |

## Open Questions (For Future Design Decisions)

1. **Schema evolution**: How does `validate_return_contract.py` handle `schema_version: "2.0"` when it only knows "1.0"? Fail closed (reject unknown) or warn-and-pass?
2. **Partial validation**: If 9/10 scripts pass but 1 fails, is the task 90% valid or 0% valid? Current proposal: 0% (hard stop). But should there be a `--lenient` mode?
3. **Performance budget**: 10 scripts × ~200ms each = ~2s overhead per task. Acceptable for STRICT tier. Should STANDARD tier run a subset?
4. **Script versioning**: Should sentinel files record script version so that re-validation with updated scripts can be triggered?
5. **Content quality gap**: DVL verifies structure but not analytical depth. A structurally perfect but intellectually shallow debate output passes all scripts. How to address? (Adversarial debate is the current answer, but it's also agent-based.)
