# T01: DVL Script Evaluation and Sprint-Spec Refactor Proposal

> **Panel**: Specification Expert, Testing Expert, DevOps Engineer, Architect
> **Date**: 2026-02-23
> **Input**: DVL-BRAINSTORM.md (10 scripts, 3 tiers), sprint-spec.md (3 epics, 12 tasks)
> **Context**: The original sc:roadmap adversarial pipeline failure was SILENT -- it produced output that looked reasonable but bypassed 80% of the pipeline. The core evaluation criterion is: would this script have CAUGHT that failure?

---

## 1. Script Evaluation Table

The **detection effectiveness** score answers one question: "If the silent pipeline bypass happened again, would this script detect it?" Scored 0.0 (would not detect) to 1.0 (guaranteed detection).

| # | Script | Tier | Detection Effectiveness | Rationale |
|---|--------|------|------------------------|-----------|
| 1 | `verify_allowed_tools.py` | Pre-Gate | **0.95** | Directly detects the root cause (RC1). If Skill is absent from allowed-tools, this script fails before any agent runs. Would have prevented the original failure entirely. Docked 0.05 because the failure could also occur with Skill present but unavailable at runtime. |
| 2 | `dependency_gate.sh` | Pre-Gate | **0.50** | Checks that predecessor output files exist before a task starts. The original failure was WITHIN a phase (steps skipped inside Wave 2), not BETWEEN phases. Catches inter-phase failures but not intra-phase pipeline bypass. |
| 3 | `content_hash_tracker.py` | Pre-Gate | **0.15** | Detects concurrent file modification. The original failure had nothing to do with concurrent writes -- it was a tool unavailability leading to pipeline bypass. Minimal relevance. |
| 4 | `validate_return_contract.py` | Post-Gate | **0.85** | If the return contract mechanism existed during the original failure, this script would have caught that `return-contract.yaml` was either missing or had `status: failed` / missing fields. Catches the failure at the output boundary. Docked 0.15 because the original failure produced no return contract at all (the mechanism did not exist), so the detection depends on the missing-file guard (a secondary check). |
| 5 | `verify_pipeline_completeness.sh` | Post-Gate | **0.95** | THE most direct detector of the original symptom. The failure bypassed 80% of pipeline steps, meaning 80% of expected artifacts were missing. This script checks that ALL artifacts exist. It would have caught the exact failure with a simple file-existence check. Docked 0.05 for edge cases where artifacts exist but are empty/stub. |
| 6 | `validate_wave2_spec.py` | Post-Gate | **0.70** | Preventive, not detective. Validates that the specification itself is unambiguous (verbs bound to tools, sub-steps present). Would have flagged the original ambiguous "Invoke" verb before runtime, preventing the failure from occurring. Docked 0.30 because it validates spec structure, not runtime behavior -- a correct spec can still fail silently at execution. |
| 7 | `verify_numeric_scores.py` | Post-Gate | **0.10** | Detects arithmetic errors in scoring matrices. The original failure was not about score inflation -- it was about pipeline bypass. Score checking is orthogonal to the failure mode. Only relevant if agents produce scoring artifacts (which they didn't in the failure case). |
| 8 | `check_file_references.py` | Post-Gate | **0.45** | Catches hallucinated file paths in agent output. The original failure DID produce some output that referenced artifacts that didn't exist or were never created. However, the failure's primary signal was missing artifacts, not bad references in existing artifacts. Partial detection. |
| 9 | `generate_checkpoint.py` | Cross-Phase | **0.60** | Replaces agent-written checkpoints with script-generated ones based on filesystem evidence. Would have exposed the failure at checkpoint time: the checkpoint would show 80% of expected artifacts as missing/unchecked. Effective but delayed -- detection occurs at phase boundary, not immediately after the bypass. |
| 10 | `context_rot_canary.py` | Cross-Phase | **0.25** | Detects context loss during long agent runs. The original failure was not context rot -- it was tool unavailability causing a rational fallback to a degraded pipeline. The agent maintained context; it simply could not call the required tool. Low relevance to this failure mode. |

---

## 2. Ranked List (by Detection Effectiveness)

| Rank | Script | Score | Category | Sprint Priority (from brainstorm) |
|------|--------|-------|----------|-----------------------------------|
| 1 | `verify_pipeline_completeness.sh` | 0.95 | Symptom detector | DEFER |
| 2 | `verify_allowed_tools.py` | 0.95 | Root cause detector | KEEP |
| 3 | `validate_return_contract.py` | 0.85 | Output boundary validator | KEEP |
| 4 | `validate_wave2_spec.py` | 0.70 | Preventive spec validator | KEEP (if time) |
| 5 | `generate_checkpoint.py` | 0.60 | Audit trail generator | DEFER |
| 6 | `dependency_gate.sh` | 0.50 | Inter-phase gate | DEFER |
| 7 | `check_file_references.py` | 0.45 | Hallucination detector | DEFER |
| 8 | `context_rot_canary.py` | 0.25 | Context integrity canary | CUT |
| 9 | `content_hash_tracker.py` | 0.15 | Concurrent modification detector | CUT |
| 10 | `verify_numeric_scores.py` | 0.10 | Arithmetic verifier | CUT |

### Panel Notes on Ranking

**Specification Expert**: The gap between ranks 1-3 (0.85-0.95) and ranks 4-5 (0.60-0.70) is significant. The top 3 scripts together cover root cause detection (verify_allowed_tools), output validation (validate_return_contract), and symptom detection (verify_pipeline_completeness). This is a complete detection chain. Scripts ranked 4+ add defense-in-depth but are not strictly necessary for catching the primary failure mode.

**Testing Expert**: `verify_pipeline_completeness.sh` was ranked DEFER in the brainstorm, which I strongly disagree with. The brainstorm states "Only useful after end-to-end test" -- but that is exactly when you need it most. The original failure WAS an end-to-end test that failed silently. This script should be promoted to KEEP.

**DevOps Engineer**: The top 3 scripts have zero external dependencies (Python stdlib + bash coreutils), sub-500ms combined runtime, and deterministic output. They can run as pre-commit hooks or CI checks with zero friction.

**Architect**: `validate_wave2_spec.py` (rank 4) is the only preventive script in the top 5 -- all others are detective. A balanced verification layer needs at least one preventive check. Recommend including it despite the higher implementation cost.

---

## 3. Lightweight vs Full Implementation Classification

### Lightweight: < 30 lines, < 1 hour

| Script | Est. LOC | Est. Time | Rationale |
|--------|----------|-----------|-----------|
| `verify_allowed_tools.py` | 15-20 | 20 min | Read file, regex extract allowed-tools line, check membership. Trivially simple. |
| `verify_pipeline_completeness.sh` | 20-25 | 30 min | List of expected filenames, for-loop checking existence. Pure bash. |
| `dependency_gate.sh` | 20-25 | 30 min | Read JSON manifest, check file existence per entry. Pure bash. |

### Medium: 30-100 lines, 1-4 hours

| Script | Est. LOC | Est. Time | Rationale |
|--------|----------|-----------|-----------|
| `validate_return_contract.py` | 60-80 | 1.5 hours | YAML parsing, field validation, type checking, status-specific constraints. Moderate complexity but well-scoped. |
| `content_hash_tracker.py` | 35-45 | 1 hour | SHA-256 hashing, JSON manifest read/write. Simple but two modes (snapshot/verify). |
| `check_file_references.py` | 50-70 | 2 hours | Regex extraction of file paths from markdown, path resolution, existence checking. Multiple regex patterns needed. |
| `context_rot_canary.py` | 40-55 | 1.5 hours | Task fingerprint extraction, cross-contamination checks. Moderate regex complexity. |
| `verify_numeric_scores.py` | 50-65 | 2 hours | Table parsing, arithmetic verification. Regex for markdown tables is error-prone. |

### Full: > 100 lines, > 4 hours

| Script | Est. LOC | Est. Time | Rationale |
|--------|----------|-----------|-----------|
| `validate_wave2_spec.py` | 100-130 | 3-4 hours | Markdown section extraction, verb glossary cross-referencing, multi-pattern validation. Complex parsing logic. |
| `generate_checkpoint.py` | 100-140 | 4-5 hours | Orchestrates multiple sub-validators, generates structured markdown, hash computation. Highest integration complexity. |

---

## 4. Sprint-Spec Refactor Proposal

### Summary of Proposed Additions

Promote 4 DVL scripts from deferred/keep-if-time to concrete sprint tasks. Place them within the existing 3-epic structure, positioned after the tasks they validate.

### Additions by Epic

#### Epic 1: Add Task 1.5 -- `verify_allowed_tools.py`

**Rationale**: This script validates the acceptance criteria of Tasks 1.1 and 1.2. It is the lightest script (15-20 LOC, 20 min) and catches the root cause. Not including it is leaving the highest-value, lowest-cost verification on the table.

| Field | Value |
|-------|-------|
| Task # | 1.5 |
| Task Name | Create `verify_allowed_tools.py` pre-gate script |
| File | `scripts/dvl/tier1/verify_allowed_tools.py` |
| Change | Create script that parses frontmatter `allowed-tools` line from a given file and asserts all required tools are present. Accept file path and required tool names as CLI arguments. Exit 0 if all present, exit 1 with missing tools to stderr. |
| Dependencies | Tasks 1.1 and 1.2 (needs files to validate against) |
| Acceptance Criteria | Script exists; `uv run python scripts/dvl/tier1/verify_allowed_tools.py src/superclaude/commands/roadmap.md Skill` exits 0 after Epic 1 tasks complete; exits 1 on a test file missing Skill |
| LOC Estimate | 15-20 |
| Complexity | Low |
| Time Estimate | 20 min |

#### Epic 1: Add Task 1.6 -- `verify_pipeline_completeness.sh`

**Rationale**: This script catches the EXACT original failure (missing pipeline artifacts). The brainstorm classified it as DEFER because "only useful after end-to-end test." The panel overrides this: the E2E test IS the context where this script must run. It is lightweight (20-25 LOC), and its absence means the E2E test (Verification Test 5) has no programmatic pass/fail -- only manual inspection. That is how the original failure went undetected.

| Field | Value |
|-------|-------|
| Task # | 1.6 |
| Task Name | Create `verify_pipeline_completeness.sh` post-gate script |
| File | `scripts/dvl/tier2/verify_pipeline_completeness.sh` |
| Change | Create script that accepts an output directory path and agent count, then checks for existence of all expected pipeline artifacts: variant files (count = agent count), diff-analysis.md, debate-transcript.md, scoring-matrix.md, merged-output.md, return-contract.yaml. Exit 0 if all present, exit 1 with missing file list. |
| Dependencies | None (can be written before pipeline exists; validates output after E2E runs) |
| Acceptance Criteria | Script exists; exits 1 on empty directory; exits 0 on directory with all expected files |
| LOC Estimate | 20-25 |
| Complexity | Low |
| Time Estimate | 30 min |

#### Epic 2: Add Task 2.5 -- `validate_wave2_spec.py` (conditional)

**Rationale**: This is the only preventive script in the top 4. It validates that the rewritten Wave 2 step 3 (the primary deliverable of Epic 2) is structurally correct. It is more expensive (100-130 LOC, 3-4 hours) and should only be implemented if the core Epic 2 tasks complete ahead of schedule. However, it replaces Verification Test 2 (currently a manual checklist) with a programmatic check.

| Field | Value |
|-------|-------|
| Task # | 2.5 |
| Task Name | Create `validate_wave2_spec.py` post-gate script (CONDITIONAL) |
| File | `scripts/dvl/tier2/validate_wave2_spec.py` |
| Change | Create script that parses SKILL.md, extracts Wave 2 step 3 sub-steps, verifies: (a) exactly 6 sub-steps (3a-3f), (b) each sub-step uses exactly one verb from the glossary, (c) step 3d contains `skill: "sc:adversarial"`, (d) step 3d fallback covers three error types, (e) step 3e contains convergence threshold, (f) zero ambiguous verbs ("Invoke", "Execute" without tool binding). Output structured per-sub-step pass/fail report. |
| Dependencies | Task 2.1 (glossary must exist for verb cross-reference), Task 2.2 (Wave 2 step 3 must be rewritten) |
| Acceptance Criteria | Script exists; produces all-pass report on correctly rewritten SKILL.md; produces at least one failure on current (pre-edit) SKILL.md |
| LOC Estimate | 100-130 |
| Complexity | High |
| Time Estimate | 3-4 hours |
| Condition | Implement only if Tasks 2.1-2.4 complete within 60% of Epic 2 time budget |

#### Epic 3: Add Task 3.5 -- `validate_return_contract.py`

**Rationale**: This script validates the acceptance criteria of Task 3.1. It is the second-highest detection effectiveness script (0.85) and directly prevents the "agent writes malformed return contract" failure mode (Risk R4). It replaces Verification Test 3 (currently manual field diffing) with a deterministic schema validator. Medium effort (60-80 LOC, 1.5 hours).

| Field | Value |
|-------|-------|
| Task # | 3.5 |
| Task Name | Create `validate_return_contract.py` post-gate script |
| File | `scripts/dvl/tier2/validate_return_contract.py` |
| Change | Create script that accepts path to return-contract.yaml and validates: (a) YAML parses successfully, (b) `schema_version` == "1.0", (c) all 9 required fields present, (d) type constraints (status in {success, partial, failed}, convergence_score in [0.0, 1.0], fallback_mode is boolean), (e) status-specific constraints (merged_output_path non-null when success, failure_stage non-null when failed), (f) null used for unreached values (not -1 or ""). Output JSON verdict: `{valid: bool, errors: [...], warnings: [...]}`. |
| Dependencies | Task 3.1 (schema definition must exist for the validator to reference) |
| Acceptance Criteria | Script exists; validates a correct return-contract.yaml as valid; rejects: missing fields, wrong types, status/field constraint violations, non-null sentinels for unreached values |
| LOC Estimate | 60-80 |
| Complexity | Medium |
| Time Estimate | 1.5 hours |

### Scaffolding Task: DVL Directory and Shared Utilities

Add as the FIRST new task (before any script tasks) to establish the directory structure.

| Field | Value |
|-------|-------|
| Task # | 0.1 |
| Task Name | Create DVL directory structure and `__init__.py` |
| File | `scripts/dvl/` (new directory tree) |
| Change | Create: `scripts/dvl/__init__.py` (shared utilities: YAML loading, file existence check, exit code helpers), `scripts/dvl/tier1/`, `scripts/dvl/tier2/`, `scripts/dvl/tier3/`, `scripts/dvl/schemas/`. The `__init__.py` provides: `load_yaml(path)`, `check_file_exists(path)`, `fail(message)`, `pass_gate(message)`. |
| Dependencies | None |
| Acceptance Criteria | Directory structure exists; `__init__.py` importable; shared utilities tested with a trivial assertion |
| LOC Estimate | 25-35 |
| Complexity | Low |
| Time Estimate | 15 min |

### Updated Implementation Order

```
Task 0.0 (Skill Tool Probe) --- decision gate
  |
  +-- Task 0.1 (DVL directory scaffolding) --- no dependencies, can run parallel
  |
  +---(primary path viable)---> Epic 1 (Invocation Wiring)
  |                               |
  |                               +---> Task 1.5 (verify_allowed_tools.py)
  |                               |       validates Tasks 1.1/1.2
  |                               |
  |                               +---> Task 1.6 (verify_pipeline_completeness.sh)
  |                               |       independent, can parallel with 1.5
  |                               |
  |                               +---> Epic 2 (Specification Rewrite)
  |                               |       |
  |                               |       +-- Task 2.2 integrates 1.3/1.4
  |                               |       +-- Task 2.5 (validate_wave2_spec.py) CONDITIONAL
  |                               |             depends on 2.1, 2.2
  |                               |
  |                               +---> Epic 3 (Return Contract)
  |                                       |
  |                                       +-- Task 3.5 (validate_return_contract.py)
  |                                             depends on 3.1
  |
  +---(primary path blocked)---> Adapted sprint: fallback-only invocation
                                  (DVL scripts still apply to fallback path)
```

### Updated Verification Plan

The DVL scripts replace manual verification tests:

| Original Test | Replaced By | Change |
|---------------|-------------|--------|
| Test 1 (Skill tool in allowed-tools, grep) | `verify_allowed_tools.py` (Task 1.5) | Programmatic, reusable, CI-compatible |
| Test 2 (Wave 2 step 3 structural audit, manual) | `validate_wave2_spec.py` (Task 2.5, conditional) | Programmatic if implemented; manual fallback preserved |
| Test 3 (Return contract schema consistency, manual diff) | `validate_return_contract.py` (Task 3.5) | Programmatic, deterministic, reusable |
| Test 4 (Pseudo-CLI elimination, grep) | No change | Already a one-liner grep; no script needed |
| Test 5 (E2E invocation, manual) | `verify_pipeline_completeness.sh` (Task 1.6) provides pass/fail gate | E2E still manual but script provides the structural check |

### Updated Definition of Done (DVL additions)

Add to the "Verification" section:

- [ ] `scripts/dvl/` directory structure exists with `__init__.py`
- [ ] `verify_allowed_tools.py` passes on modified `roadmap.md` and `SKILL.md`
- [ ] `verify_pipeline_completeness.sh` exits 1 on empty dir, documents expected artifacts
- [ ] `validate_return_contract.py` validates a sample return-contract.yaml against the 9-field schema
- [ ] (CONDITIONAL) `validate_wave2_spec.py` produces all-pass report on rewritten Wave 2 step 3

---

## 5. LOC/Complexity Summary

| Task | Script | LOC | Complexity | Time | Dependencies | Classification |
|------|--------|-----|------------|------|--------------|----------------|
| 0.1 | DVL scaffolding (`__init__.py` + dirs) | 25-35 | Low | 15 min | None | Lightweight |
| 1.5 | `verify_allowed_tools.py` | 15-20 | Low | 20 min | Tasks 1.1, 1.2 | Lightweight |
| 1.6 | `verify_pipeline_completeness.sh` | 20-25 | Low | 30 min | None | Lightweight |
| 2.5 | `validate_wave2_spec.py` | 100-130 | High | 3-4 hours | Tasks 2.1, 2.2 | Full (CONDITIONAL) |
| 3.5 | `validate_return_contract.py` | 60-80 | Medium | 1.5 hours | Task 3.1 | Medium |
| **Total (unconditional)** | | **120-160** | | **2.25 hours** | | |
| **Total (with conditional)** | | **220-290** | | **5.5-6.25 hours** | | |

---

## 6. Panel Consensus Notes

### Unanimous Agreements

1. **verify_pipeline_completeness.sh must be promoted from DEFER to KEEP.** The brainstorm's rationale ("only useful after end-to-end test") is exactly backwards. The original failure WAS a de facto end-to-end test that failed silently because no completeness check existed. This script is 20-25 lines, 30 minutes, and catches the exact original failure. There is no defensible reason to defer it.

2. **verify_allowed_tools.py is the highest ROI script in the entire DVL.** 15-20 lines, 20 minutes, directly validates the root cause fix. The brainstorm correctly marked it KEEP.

3. **validate_return_contract.py must be implemented, not deferred.** Without it, Risk R4 ("Claude does not write return-contract.yaml on failure paths") has no programmatic detector. The sprint spec currently relies on manual field diffing (Verification Test 3), which is how failures go undetected.

4. **Content hash tracker (CUT) and numeric score verifier (CUT) are correctly cut.** Neither is relevant to the primary failure mode. Content hash tracker addresses Risk R5 (concurrent modification), which is already mitigated by the single-author constraint. Numeric score verifier addresses a different failure class entirely.

5. **DVL directory scaffolding (Task 0.1) should be the first new task.** It can run in parallel with Task 0.0 (Skill Tool Probe) and creates the directory structure all subsequent DVL tasks depend on.

### Majority Agreements (3/4)

6. **validate_wave2_spec.py should be CONDITIONAL, not unconditional.** Three panelists (Testing, DevOps, Architect) agree it is valuable but its 3-4 hour cost is high relative to the sprint's core deliverables. The Specification Expert argues it should be unconditional because "the spec rewrite IS the deliverable of Epic 2, and a spec without a programmatic validator is a spec that will drift." Compromise: conditional with a clear trigger (implement if Epic 2 core tasks complete within 60% of time budget).

7. **context_rot_canary.py is correctly CUT for this sprint** but should be the first script reconsidered in the follow-up sprint (when RC5+S05 Claude behavioral fallback is addressed). Context rot is a real risk for long-running agents; it just wasn't the failure mode here.

### Dissents

8. **Testing Expert dissent on generate_checkpoint.py**: "The brainstorm's DEFER classification is correct for this sprint, but the checkpoint generation pattern is the single most impactful long-term investment in the DVL. Agent-written checkpoints are the primary vector for undetected quality erosion. I recommend it as the #1 priority for the follow-up sprint, ahead of context_rot_canary.py."

9. **Architect dissent on script scope**: "The proposal adds 4-5 scripts to a 3-epic sprint that already has 12 tasks. The unconditional additions (0.1, 1.5, 1.6, 3.5) total only 2.25 hours and 120-160 LOC, which is manageable. But if validate_wave2_spec.py is also triggered, the sprint grows by 5.5-6.25 hours total, which is a 25-30% scope increase. I recommend hard-capping DVL work at 3 hours per sprint to prevent scope creep."

### Final Recommendation

**Implement unconditionally**: Tasks 0.1, 1.5, 1.6, 3.5 (2.25 hours, 120-160 LOC).
**Implement conditionally**: Task 2.5 (3-4 additional hours, 100-130 additional LOC).
**Total DVL overhead**: 2.25 hours minimum, 5.5-6.25 hours maximum.
**Detection coverage**: The unconditional scripts cover root cause (verify_allowed_tools), symptom (verify_pipeline_completeness), and output boundary (validate_return_contract) -- a complete detection chain for the primary failure mode.

---

*Panel evaluation generated 2026-02-23. Panelists: Specification Expert, Testing Expert, DevOps Engineer, Architect.*
*Input: DVL-BRAINSTORM.md, sprint-spec.md.*
*Method: Independent scoring with consensus reconciliation.*
