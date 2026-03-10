# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 3: Return Contract Transport Mechanism

**Phase Goal**: Establish the file-based `return-contract.yaml` convention so `sc:adversarial`
reliably transports structured pipeline results back to `sc:roadmap`. Phase 3 covers three
distinct concerns in a single coordinated milestone: the producer schema (9 fields written by
`sc:adversarial`), the consumer logic (status routing and missing-file guard in
`adversarial-integration.md`), and the Tier 1 artifact existence gate that runs before YAML
parsing. Dead code removal (two `subagent_type` lines) is bundled with the producer task because
it touches the same file. A cross-reference consistency check closes the phase by confirming that
producer and consumer schemas are identical in field set and type. Phase 3 may execute partially
in parallel with Phase 2 (different primary files), but Task T03.03 must complete before Phase 4
Task T04.03 because both modify `adversarial-integration.md`.

**Roadmap milestone**: M3 — Return Contract Transport Mechanism
**Deliverable IDs covered**: D-0010 through D-0014
**Estimated effort**: M (medium)
**Risk level**: Medium
**Phase dependency**: M1 prerequisite validation complete (Phase 1 checkpoint passed)
**File conflict constraint**: T03.03 must complete before T04.03 (same file)

---

## T03.01 — Add Return Contract (MANDATORY) Section to sc:adversarial SKILL.md

**Roadmap Item ID(s)**: R-013, R-014
**Deliverable IDs**: D-0010

**Why**: The adversarial pipeline currently produces no structured output that `sc:roadmap` can
consume programmatically. Without a machine-readable return contract written to a predictable
file path, the caller has no reliable way to determine pipeline status, convergence score, or
artifact locations. This task defines the producer side of the file-based transport convention
(9 fields, YAML format, written even on failure) that enables the full integration chain.

**Effort**: M
**Risk**: Medium
**Risk Drivers**: Schema definition introduces a new API contract; incorrect field types or
missing write-on-failure instruction will silently break consumer logic in T03.03.

**Tier**: STRICT
**Tier Confidence**: 90%
**Tier Confidence Bar**: [=========.] 90%
**Tier Rationale**: Schema definition, api contract keywords, multi-file impact (producer +
consumer share the same schema). Context booster: security path not applicable, but schema/api
contract keywords push firmly to STRICT.

**Requires Confirmation**: No (confidence >= 0.85, tier is unambiguous)
**Critical Path Override**: None

**Verification Method**: Sub-agent (quality-engineer)
**Verification Command**:
```
grep -c "Return Contract" src/superclaude/skills/sc-adversarial/SKILL.md
# Expected: >= 1

grep -E "schema_version|status|convergence_score|merged_output_path|artifacts_dir|unresolved_conflicts|base_variant|failure_stage|fallback_mode" src/superclaude/skills/sc-adversarial/SKILL.md | wc -l
# Expected: 9 (all 9 fields present)
```

**MCP Requirements**: Sequential (schema coherence analysis); Context7 (YAML conventions)
**Fallback Allowed**: No — this section is the foundation for T03.03 and T03.05; skipping blocks
the entire return contract subsystem.
**Sub-Agent Delegation**: Yes — quality-engineer sub-agent performs post-write schema audit

---

**Artifacts**:
- `src/superclaude/skills/sc-adversarial/SKILL.md` (modified — new section added as final pipeline step)

**Deliverables**:
- D-0010: "Return Contract (MANDATORY)" section present as the final step of the adversarial pipeline, containing all 9 fields with correct types, write-on-failure instruction, and an example YAML block

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-adversarial/SKILL.md` in full. Identify the current
   final pipeline step to determine the correct insertion point for the new section. Note the
   heading style used by existing pipeline steps.

2. [READ] Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` to understand
   what the consumer expects, so the producer schema is aligned before T03.03 adds the consumer
   side. Note any field references that already appear in the integration doc.

3. [WRITE] Add "Return Contract (MANDATORY)" section as the final pipeline step in
   `src/superclaude/skills/sc-adversarial/SKILL.md`. The section must contain exactly 9 fields:

   | Field | Type | Notes |
   |-------|------|-------|
   | `schema_version` | string | Fixed value `"1.0"` |
   | `status` | enum | `success` / `partial` / `failed` |
   | `convergence_score` | float | Range 0.0–1.0; `null` if unreached |
   | `merged_output_path` | string | Absolute path; `null` if unreached |
   | `artifacts_dir` | string | Absolute path to output directory |
   | `unresolved_conflicts` | integer | Count only — NOT a list; `null` if unreached |
   | `base_variant` | string | Name of selected base; `null` if unreached |
   | `failure_stage` | string | Stage name where failure occurred; `null` on success |
   | `fallback_mode` | boolean | `true` if fallback protocol executed; `false` otherwise |

   Use YAML null (bare `null`) for fields not reached due to early failure. Write the contract
   even when the pipeline fails — the write-on-failure instruction must appear explicitly in the
   section prose.

4. [WRITE] Append an example YAML block to the section showing: (a) a successful run with all
   fields populated, and (b) a failed run with `null` for unreached fields and a populated
   `failure_stage`. Label both examples clearly.

5. [VERIFY] Confirm the section appears after all other pipeline steps, not before them. Confirm
   the heading style matches the document's conventions. Confirm all 9 field names are spelled
   exactly as specified — typos will silently break the consumer's field lookups.

---

**Acceptance Criteria**:
1. The "Return Contract (MANDATORY)" section exists as the final step of the adversarial pipeline
   in `src/superclaude/skills/sc-adversarial/SKILL.md` and uses a heading style consistent with
   other pipeline step headings in the file.
2. All 9 fields are present with correct types: `schema_version` (string `"1.0"`), `status`
   (enum), `convergence_score` (float 0.0–1.0), `merged_output_path` (string), `artifacts_dir`
   (string), `unresolved_conflicts` (integer, NOT list), `base_variant` (string), `failure_stage`
   (string), `fallback_mode` (boolean). YAML `null` is specified for unreached fields.
3. The section contains an explicit write-on-failure instruction and two example YAML blocks
   (one successful, one failed).
4. `grep -E "schema_version|status|convergence_score|merged_output_path|artifacts_dir|unresolved_conflicts|base_variant|failure_stage|fallback_mode" src/superclaude/skills/sc-adversarial/SKILL.md | wc -l` returns 9 or greater.

**Validation**:
1. Run `grep -c "Return Contract" src/superclaude/skills/sc-adversarial/SKILL.md` — expected
   result: >= 1.
2. Run `grep -c "write.*fail\|fail.*write\|on failure\|even.*fail" src/superclaude/skills/sc-adversarial/SKILL.md` — expected result: >= 1 (write-on-failure instruction present).

**Dependencies**: T03.05 (cross-reference check) depends on this task completing first.
**Rollback**: Remove the added section from `src/superclaude/skills/sc-adversarial/SKILL.md`.
The file existed before this task; no other content is changed.

**Notes**: The `unresolved_conflicts` field must be typed as integer (a count), not as a list.
This distinction is critical for consumer parsing — a list type would require different YAML
parsing logic. The `fallback_mode` field must be present even on the primary (non-fallback) path
with value `false`, to allow consumers to branch on this field reliably.

---

## T03.02 — Remove Dead `subagent_type` Lines from sc:adversarial SKILL.md

**Roadmap Item ID(s)**: R-015
**Deliverable IDs**: D-0011

**Why**: Two `subagent_type: "general-purpose"` lines remain in `sc:adversarial/SKILL.md` as
dead code from a previous specification revision. They are not read by any consumer, not
referenced in any integration doc, and create noise that could mislead future readers about the
file's semantics. Removing them reduces confusion and ensures the file reflects only the current
invocation model.

**Effort**: XS
**Risk**: Low
**Risk Drivers**: Minimal — deletion of two non-functional lines. Risk is limited to accidentally
removing adjacent content if a line-targeted edit tool is misused.

**Tier**: LIGHT
**Tier Confidence**: 85%
**Tier Confidence Bar**: [========..] 85%
**Tier Rationale**: Minor cleanup, remove dead code keywords. No functional change. Single file.

**Requires Confirmation**: No
**Critical Path Override**: None — bundled with T03.01 (same file) for efficiency

**Verification Method**: Sanity check (grep)
**Verification Command**:
```
grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md
# Expected: 0
```

**MCP Requirements**: None
**Fallback Allowed**: Yes — if lines cannot be located, document their absence as already-deleted
and mark D-0011 as satisfied by prior cleanup.
**Sub-Agent Delegation**: No — trivial single-file edit

---

**Artifacts**:
- `src/superclaude/skills/sc-adversarial/SKILL.md` (modified — two lines deleted)

**Deliverables**:
- D-0011: Zero `subagent_type` lines remain in `src/superclaude/skills/sc-adversarial/SKILL.md`

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-adversarial/SKILL.md` (already read in T03.01 —
   reuse that context). Locate both `subagent_type` lines. Note their exact line numbers and
   surrounding context to ensure the correct lines are targeted.

2. [EDIT] Delete both `subagent_type: "general-purpose"` lines. Do not alter any adjacent
   content. If a deleted line was the only content on its parent list item, remove the blank
   line created by the deletion only if it creates a double-blank-line gap.

3. [VERIFY] Run `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` and
   confirm the result is 0.

---

**Acceptance Criteria**:
1. `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns exactly 0.
2. No adjacent content was inadvertently deleted — the lines immediately before and after each
   removed line are intact and the section remains coherent.
3. The file is valid Markdown with no double-blank-line gaps introduced by the deletion.
4. T03.01's newly added "Return Contract (MANDATORY)" section is unaffected.

**Validation**:
1. `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` — expected: 0.
2. Manual inspection of the two deletion sites confirms surrounding content is intact.

**Dependencies**: T03.01 should complete first (same file — avoid simultaneous edits).
**Rollback**: Re-insert the two deleted lines at their original positions.

**Notes**: If the lines are already absent (deleted by a prior edit in the same session), confirm
via grep and mark this task complete without further edits. Do not re-create the lines.

---

## T03.03 — Add Return Contract Consumption Section to adversarial-integration.md

**Roadmap Item ID(s)**: R-013, R-016
**Deliverable IDs**: D-0012

**Why**: The consumer side of the return contract transport mechanism is currently absent from
`adversarial-integration.md`. Without explicit read instructions, status routing logic, a
missing-file guard, and a convergence threshold, the `sc:roadmap` agent has no specification
for how to interpret the return contract written by `sc:adversarial`. This task closes that gap
by making the consumption behavior fully explicit and machine-actionable.

**Effort**: M
**Risk**: Medium
**Risk Drivers**: API contract keywords; schema routing logic (3-status branching); same-file
constraint with T04.03 means this task gates Phase 4. Incorrect missing-file guard status value
(`partial` vs `failed`) was a previously identified critical gap (G1 in T02-synthesis.md) — the
corrected value `failed` with `failure_stage: transport` must be used.

**Tier**: STRICT
**Tier Confidence**: 85%
**Tier Confidence Bar**: [========..] 85%
**Tier Rationale**: API contract, schema routing, multi-file coordination (producer in T03.01,
consumer here). Context booster: estimated file changes > 2 across Phase 3 (+0.3 STRICT).

**Requires Confirmation**: No (confidence >= 0.85)
**Critical Path Override**: This task is on the critical path for T04.03 — T04.03 cannot begin
until T03.03 is complete (same-file edit constraint on `adversarial-integration.md`).

**Verification Method**: Sub-agent (quality-engineer)
**Verification Command**:
```
grep -c "Return Contract Consumption" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: >= 1

grep -c "schema_version" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: >= 1

grep -c "convergence_score" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: >= 1
```

**MCP Requirements**: Sequential (multi-status routing logic coherence); Context7 (YAML
parsing patterns)
**Fallback Allowed**: No — this section is prerequisite for T04.03 and for the full integration
chain. Skipping breaks Phase 4.
**Sub-Agent Delegation**: Yes — quality-engineer sub-agent audits 3-status routing completeness

---

**Artifacts**:
- `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` (modified — new section added)

**Deliverables**:
- D-0012: "Return Contract Consumption" section present in `adversarial-integration.md` with
  `schema_version` validation, 3-status routing, missing-file guard, convergence threshold 0.6,
  `fallback_mode` differentiated warning, and example YAML blocks for both a successful and a
  failed return contract

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` in full.
   Identify the appropriate insertion point for the new "Return Contract Consumption" section —
   it should appear after the pipeline invocation steps and before any post-processing or output
   sections. Note the heading style used in the file.

2. [READ] Re-check the 9-field schema from T03.01 (D-0010) to ensure the consumer section
   references exactly the same field names and types.

3. [WRITE] Add "Return Contract Consumption" section to
   `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` containing:

   a. **Read instruction**: Specify the exact path to `return-contract.yaml` relative to
      `--output-dir` or using the path variable convention established in T03.04.

   b. **Schema version validation**: Check `schema_version == "1.0"` before any other field
      access. If the version does not match, emit a WARNING and abort consumption.

   c. **Missing-file guard**: If `return-contract.yaml` does not exist at the expected path,
      treat as `status: failed` with `failure_stage: "transport"`. Do NOT treat as
      `status: partial` — this was a critical gap (G1) that has been resolved.

   d. **3-status routing**:
      - `status: success` — proceed to merge output into roadmap; log convergence score
      - `status: partial` — check `convergence_score >= 0.6`; if yes, warn and proceed;
        if no, abort with user message citing low convergence. If `fallback_mode: true`,
        emit a differentiated warning noting that output was produced by the fallback
        protocol, not the full adversarial pipeline.
      - `status: failed` — abort; log `failure_stage` and surface to user as actionable
        error with suggested remediation (re-run, check sc:adversarial availability)

   e. **YAML parse error handling**: If the file exists but cannot be parsed as valid YAML,
      treat as `status: failed` with `failure_stage: "transport"`.

   f. **`fallback_mode` differentiated warning**: When `fallback_mode: true` AND status is
      `partial`, emit a distinct warning that differentiates fallback output from a low-
      convergence primary-path result.

4. [WRITE] Append two example YAML blocks at the end of the section: one showing a successful
   return contract (all fields populated, `status: success`) and one showing a failed return
   contract (`status: failed`, several fields `null`, `failure_stage` populated). Label both.

5. [VERIFY] Confirm the missing-file guard uses `status: failed` (not `status: partial`) and
   `failure_stage: "transport"`. Confirm the convergence threshold is exactly 0.6.

---

**Acceptance Criteria**:
1. "Return Contract Consumption" section exists in
   `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with a read instruction
   pointing to `return-contract.yaml` using a path variable (not a hardcoded absolute path).
2. The section contains: `schema_version` validation, missing-file guard with
   `status: failed, failure_stage: "transport"`, 3-status routing with convergence threshold
   exactly 0.6, `fallback_mode: true` differentiated warning, and YAML parse error handling.
3. Two example YAML blocks are present (successful and failed cases) and are correctly labeled.
4. `grep -c "convergence" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
   returns >= 1 and the threshold value 0.6 appears in the document.

**Validation**:
1. `grep -c "Return Contract Consumption" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: >= 1.
2. `grep -c "failure_stage.*transport\|transport.*failure_stage" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: >= 1 (missing-file guard uses correct status).

**Dependencies**: T03.01 (producer schema must be finalized before consumer section is written).
T03.04 (Tier 1 gate) may execute in parallel with this task — they add different sections to
the same file. If parallel execution is used, coordinate to avoid merge conflicts.
**Rollback**: Remove the added section from `adversarial-integration.md`. No other content in
the file is changed by this task.

**Notes**: The missing-file guard must use `status: failed` with `failure_stage: "transport"`,
not `status: partial`. This was identified as Critical Gap G1 in T02-synthesis.md. A `partial`
status for a missing file would mask transport failures as recoverable conditions.

---

## T03.04 — Add Tier 1 Artifact Existence Gate to adversarial-integration.md

**Roadmap Item ID(s)**: R-013, R-017
**Deliverable IDs**: D-0013

**Why**: Even with a well-specified return contract schema, a consumer that attempts YAML parsing
before verifying artifact existence will produce confusing errors (file-not-found vs. parse
errors). The Tier 1 gate establishes four sequential existence checks that must all pass before
any YAML parsing begins, making failure modes explicit and actionable. Path variables (not
hardcoded paths) ensure the gate is reusable across different output directory configurations.

**Effort**: S
**Risk**: Low
**Risk Drivers**: Low — this is an additive section with clear sequential structure. The only
risk is ordering: the gate must appear before YAML parsing, not after.

**Tier**: STANDARD
**Tier Confidence**: 80%
**Tier Confidence Bar**: [========..] 80%
**Tier Rationale**: `add section with validation logic` matches STANDARD (implement, add
keywords). Not STRICT because no schema definition or multi-file impact beyond this one addition.

**Requires Confirmation**: No
**Critical Path Override**: None — T03.04 may parallel T03.03 if the file sections do not
conflict (different insertion points within the same file).

**Verification Method**: Direct test execution
**Verification Command**:
```
grep -c "Artifact Existence Gate\|Tier 1" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: >= 1

grep -c "diff-analysis\|merged-output\|return-contract" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: >= 3 (all 3 artifact names referenced in gate)
```

**MCP Requirements**: Sequential (ordering validation — gate must precede YAML parsing)
**Fallback Allowed**: Yes — if the gate cannot be inserted before YAML parsing (insertion point
ambiguous), add it immediately before the "Return Contract Consumption" section from T03.03.
**Sub-Agent Delegation**: No

---

**Artifacts**:
- `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` (modified — new section added before YAML parsing steps)

**Deliverables**:
- D-0013: "Post-Adversarial Artifact Existence Gate (Tier 1)" section present in
  `adversarial-integration.md`, containing 4 sequential checks in the correct order, each with
  a failure treatment, positioned before YAML parsing, using path variable references.

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` (already
   read in T03.03 — reuse context). Identify the position of any YAML parsing steps in the
   existing document. The new Tier 1 gate section must be inserted before those steps.

2. [WRITE] Add "Post-Adversarial Artifact Existence Gate (Tier 1)" section to
   `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`. The section must contain
   exactly 4 sequential existence checks, in this order:

   | Check # | Target | Failure Treatment |
   |---------|--------|-------------------|
   | 1 | Output directory existence | Abort; `failure_stage: "transport"` — directory missing means pipeline did not complete |
   | 2 | `diff-analysis.md` in artifacts dir | Abort; `failure_stage: "diff_analysis"` — adversarial comparison step did not produce output |
   | 3 | `merged-output.md` in artifacts dir | Abort; `failure_stage: "merge"` — merge step did not complete |
   | 4 | `return-contract.yaml` in artifacts dir | Abort; `failure_stage: "transport"` — contract not written (handled by T03.03 missing-file guard, referenced here) |

   Use path variables throughout — reference `{artifacts_dir}` or an equivalent path variable,
   not hardcoded absolute paths. The variable name must be consistent with whatever convention
   the document already uses for the output directory reference.

3. [VERIFY] Confirm the gate section appears before any YAML parsing steps in the document
   flow. Confirm all 4 checks are in the specified order. Confirm path variables are used
   consistently (no hardcoded paths).

---

**Acceptance Criteria**:
1. "Post-Adversarial Artifact Existence Gate (Tier 1)" section (or equivalent heading) exists
   in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`, positioned before any
   YAML parsing steps.
2. The section contains exactly 4 sequential existence checks in order: output directory,
   `diff-analysis.md`, `merged-output.md`, `return-contract.yaml`. Each check specifies a
   failure treatment with a `failure_stage` value.
3. All path references use path variables, not hardcoded absolute paths.
4. The section is coherent with the "Return Contract Consumption" section added in T03.03 —
   both reference the same path variable convention and the gate's check #4 is consistent with
   the missing-file guard in T03.03.

**Validation**:
1. `grep -c "Artifact Existence Gate\|Tier 1" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: >= 1.
2. `grep -c "diff-analysis\|merged-output\|return-contract" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: >= 3.

**Dependencies**: T03.03 should complete or be in progress; coordinate insertion points to avoid
conflict. T03.04's section is logically upstream of T03.03's section in document flow.
**Rollback**: Remove the added section. No other content is changed by this task.

**Notes**: Check #4 (return-contract.yaml) is also covered by the missing-file guard in T03.03.
The Tier 1 gate is not redundant — it provides a pre-parse existence check that produces a
cleaner failure message than a YAML parse error on a non-existent file. The gate and the
missing-file guard serve different layers of the same defense.

---

## T03.05 — Verify Cross-Reference Consistency Between Producer and Consumer Schemas

**Roadmap Item ID(s)**: R-018
**Deliverable IDs**: D-0014

**Why**: The producer schema (T03.01) and consumer logic (T03.03) must reference identical field
sets with consistent types. A mismatch — for example, `unresolved_conflicts` typed as a list in
one document and an integer in the other, or a field present in the producer but absent from the
consumer routing logic — would cause silent runtime failures. This verification task confirms
consistency before Phase 3 is closed.

**Effort**: XS
**Risk**: Low
**Risk Drivers**: Read-only verification. The only risk is incomplete checking — all 9 fields
must be verified, not just the most obvious ones.

**Tier**: EXEMPT
**Tier Confidence**: 85%
**Tier Confidence Bar**: [========..] 85%
**Tier Rationale**: Read-only verification; analyze, review, check keywords. No file modifications.

**Requires Confirmation**: No
**Critical Path Override**: None — this is the phase closing check

**Verification Method**: Skip (EXEMPT tier — direct manual cross-reference)
**Verification Command**: N/A (read-only task)

**MCP Requirements**: None (read-only diff comparison)
**Fallback Allowed**: Yes — if inconsistencies are found, create remediation notes and flag for
T03.01 or T03.03 amendment before Phase 3 checkpoint.
**Sub-Agent Delegation**: No

---

**Artifacts**:
- No files modified
- Output: inline verification report (document findings in Phase 3 checkpoint notes)

**Deliverables**:
- D-0014: Cross-reference consistency confirmed — identical field sets in producer (`sc-adversarial/SKILL.md`) and consumer (`adversarial-integration.md`); `base_variant` and `failure_stage` present in both; `unresolved_conflicts` typed as integer in both.

---

**Steps**:

1. [READ] Read the "Return Contract (MANDATORY)" section added to
   `src/superclaude/skills/sc-adversarial/SKILL.md` in T03.01. Extract the complete 9-field
   list with their types.

2. [READ] Read the "Return Contract Consumption" section added to
   `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` in T03.03. Extract all
   field references and their treatment in the routing logic.

3. [ANALYZE] Cross-reference the two field lists:
   - Confirm all 9 producer fields appear in the consumer section
   - Confirm `unresolved_conflicts` is referenced as an integer (count) in both documents
   - Confirm `base_variant` appears in both
   - Confirm `failure_stage` appears in both with consistent value semantics
   - Confirm `fallback_mode` is referenced as a boolean in both
   - Confirm the convergence threshold value (0.6) in the consumer matches any threshold
     reference in the producer section

4. [VERIFY] If any inconsistency is found, document it clearly:
   - Field name mismatch (typo or rename)
   - Type mismatch (e.g., list vs. integer for `unresolved_conflicts`)
   - Field present in producer but absent from consumer routing
   - Threshold value discrepancy
   Then create a remediation note identifying which task (T03.01 or T03.03) requires amendment.

---

**Acceptance Criteria**:
1. All 9 producer fields from `sc:adversarial/SKILL.md` are confirmed present (by name) in the
   consumer section of `adversarial-integration.md`.
2. `unresolved_conflicts` is confirmed as integer type in both documents, not as a list.
3. `base_variant` and `failure_stage` are confirmed present in both producer and consumer
   sections with consistent semantics.
4. No field name typos or type mismatches exist between producer and consumer; any issues found
   are documented and flagged for amendment before the Phase 3 checkpoint is accepted.

**Validation**:
1. Produce a comparison table listing all 9 fields with their type in the producer column and
   their treatment in the consumer column — if any cell is blank, that field is missing.
2. Explicitly verify `unresolved_conflicts` type: confirm no list syntax (brackets, hyphens as
   list items) is used for this field in either document.

**Dependencies**: T03.01 and T03.03 must both complete before this task begins.
**Rollback**: N/A — read-only task. If inconsistencies are found, amend T03.01 or T03.03.

**Notes**: This task does not modify files. Its output is a verification report embedded in the
Phase 3 checkpoint notes. If the report identifies any inconsistency, the Phase 3 checkpoint
is blocked until the inconsistency is resolved by amending the appropriate task's output.

---

## Phase 3 Checkpoint

**Cumulative task count at this checkpoint**: T01.01–T01.04 (Phase 1), T02.01–T02.05 (Phase 2),
T03.01–T03.05 (Phase 3) = 14 tasks completed

**Checkpoint Gate**: All of the following must be true before Phase 4 begins:

| Gate | Verification Command | Expected |
|------|---------------------|----------|
| Return Contract section exists | `grep -c "Return Contract" src/superclaude/skills/sc-adversarial/SKILL.md` | >= 1 |
| All 9 fields present | `grep -E "schema_version\|status\|convergence_score\|merged_output_path\|artifacts_dir\|unresolved_conflicts\|base_variant\|failure_stage\|fallback_mode" src/superclaude/skills/sc-adversarial/SKILL.md \| wc -l` | >= 9 |
| Zero subagent_type lines | `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` | 0 |
| Consumption section exists | `grep -c "Return Contract Consumption" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | >= 1 |
| Tier 1 gate exists | `grep -c "Artifact Existence Gate\|Tier 1" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | >= 1 |
| Cross-reference consistent | D-0014 verification report shows no inconsistencies | Pass |
| File conflict released | T03.03 complete | T04.03 may now begin |

**Checkpoint Failure Action**: If any gate fails, remediate the corresponding task before
proceeding to Phase 4. The file conflict constraint (T03.03 complete before T04.03) is the
highest-priority gate for unblocking Phase 4.

---

*Phase 3 generated 2026-02-25. Roadmap milestone: M3 — Return Contract Transport Mechanism.
Deliverables D-0010 through D-0014. Sprint: sc:roadmap Adversarial Pipeline Remediation.*
