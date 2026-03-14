---
title: "v2.25 Roadmap v5: Deviation-Aware Pipeline"
type: brainstorm-reference
status: draft
created: 2026-03-13
source_conversation: brainstorm-session-roadmap-v5
prior_release: v2.24-cli-portify-cli-v4
pipeline_version: v4 (current) -> v5 (proposed)
scope_count: 2
new_steps: 2
modified_steps: 3
open_questions: 10
---

# Brainstorm Reference: Roadmap v5 Deviation-Aware Pipeline

> This document captures all design decisions, architecture proposals, failure
> analysis, open questions, and implementation constraints from the v2.25
> brainstorm session. It is the primary input for drafting the v2.25 PRD.

---

## 1. Problem Statement

### 1.1 Triggering Incident

The roadmap pipeline for release v2.24-cli-portify-cli-v4 failed at the
`spec-fidelity` gate after 2 attempts. The gate enforces
`high_severity_count == 0` in the fidelity report frontmatter before the
pipeline can proceed to `remediate` and `certify`.

**Pipeline state at failure**:
- Completed steps (PASS): `generate-opus-architect`, `generate-haiku-architect`,
  `diff`, `debate`, `score`, `merge`, `test-strategy`
- Failed step (attempt 2/2): `spec-fidelity`
- Skipped: `extract`, `remediate`, `certify`
- State file: `.dev/releases/current/v2.24-cli-portify-cli-v4/.roadmap-state.json`

### 1.2 Fidelity Report Summary

The fidelity report found 20 deviations: 3 HIGH, 12 MEDIUM, 5 LOW.

**The 3 HIGH-severity deviations**:

| ID | Deviation | Root Cause |
|----|-----------|------------|
| DEV-001 | File structure mismatch: `steps/` subdirectory with renamed modules (`cli.py` instead of `commands.py`, collapsed `tui.py`+`logging_.py`+`diagnostics.py` into `monitor.py`) | Mixed: `steps/` layout was INTENTIONAL (D-02, R2 consensus); module renames were SLIPS (never debated) |
| DEV-002 | Missing data models: only 3 of 6 spec-defined models appear. Missing: `PortifyStatus`, `PortifyOutcome`, `PortifyStepResult`, `PortifyMonitorState`. Non-spec `ComponentInventory` introduced. | SLIP: never discussed in debate |
| DEV-003 | Missing semantic check implementations: 8 gate check functions in spec Section 5.2.1 referenced abstractly; `_all_gates_defined()` not mentioned anywhere | SLIP: never discussed in debate |

### 1.3 Root Cause Analysis

Deviations fall into two categories:

**INTENTIONAL (debate-resolved)**:
- `steps/` subdirectory layout (D-02, R2 consensus)
- `executor.py` as explicit module (D-04, R2 consensus)
- `convergence.py` state enum (D-11, R2 partial consensus)
- `resume.py` as Phase 2 deliverable (D-12, consensus)
- Section hashing for additive-only enforcement (D-14, consensus)

**SLIPS (not debated, generation failures)**:
- Module renames (`commands.py` -> `cli.py`, three modules -> `monitor.py`)
- Missing 3/6 data models
- Missing semantic check function implementations

### 1.4 Systemic Failures Identified

1. **Information loss**: spec -> extraction loses module names, data models,
   function signatures. Generate agents work from extraction, not spec.

2. **No spec context in debate**: debate agents receive diff + two variants
   but never the spec file. They cannot flag spec departures.

3. **No deviation annotation at merge**: merge agent produces roadmap.md
   without any companion metadata marking spec departures.

4. **Fidelity agent works blind**: must rediscover all context from scratch,
   re-reading debate artifacts to understand what was intentional.

5. **Retry is futile**: same inputs -> same outputs. The retry mechanism
   reruns the same fidelity prompt against the same unchanged roadmap.

6. **No remediation path for classified deviations**: even if deviations
   are correctly identified, there is no automated flow that distinguishes
   "fix this SLIP in the roadmap" from "this intentional deviation is fine."

---

## 2. Proposed Architecture: Two-Scope Refactor

### 2.1 Design Philosophy

- **Scope 2** (annotation) is a **prevention** mechanism: reduces false
  positives at fidelity time by pre-annotating known intentional deviations
- **Scope 1** (analysis) is a **recovery** mechanism: when fidelity still
  finds issues, produces structured classification to drive intelligent
  remediation
- Together they compose: Scope 2 reduces the work for Scope 1, and Scope 1
  catches anything Scope 2 misses

### 2.2 Pipeline Comparison

**v4 (current)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> test-strategy -> spec-fidelity(STRICT) -> remediate -> certify
```

**v5 (proposed)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> annotate-deviations(NEW) -> test-strategy
  -> spec-fidelity(DOWNGRADED) -> deviation-analysis(NEW)
  -> remediate(MODIFIED) -> certify(MODIFIED)
```

### 2.3 Pipeline Flow Diagram

```
                    +--------------------------------------------------+
                    |           GENERATION PHASE                        |
                    +--------------------------------------------------+
                    |  extract --+-- gen-A (opus)  --+                  |
                    |            +-- gen-B (haiku) --+                  |
                    |                    |                              |
                    |               diff-analysis                      |
                    |                    |                              |
                    |                 debate                            |
                    |                    |                              |
                    |                  score                            |
                    |                    |                              |
                    |                  merge ----------> roadmap.md     |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |        ANNOTATION PHASE (Scope 2 -- NEW)         |
                    +--------------------------------------------------+
                    |  annotate-deviations                              |
                    |    reads: spec + roadmap + debate + diff          |
                    |    produces: spec-deviations.md                   |
                    |    gate: STANDARD (non-blocking)                  |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |           VALIDATION PHASE                        |
                    +--------------------------------------------------+
                    |  test-strategy (unchanged)                        |
                    |                    |                              |
                    |  spec-fidelity  (DOWNGRADED: STANDARD)            |
                    |    reads: spec + roadmap + spec-deviations        |
                    |    produces: spec-fidelity.md (diagnostic)        |
                    |    gate: STANDARD (non-blocking)                  |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |     CLASSIFICATION PHASE (Scope 1 -- NEW)        |
                    +--------------------------------------------------+
                    |  deviation-analysis                               |
                    |    reads: fidelity + debate + diff + deviations   |
                    |    produces: deviation-analysis.md                |
                    |    gate: STRICT (no AMBIGUOUS deviations)         |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |           REMEDIATION PHASE (MODIFIED)            |
                    +--------------------------------------------------+
                    |  remediate                                        |
                    |    reads: deviation-analysis.md (routing table)   |
                    |    routes: SLIPs -> fix roadmap.md                |
                    |            INTENTIONAL -> no action               |
                    |                    |                              |
                    |  certify (STRICT: certified == true)              |
                    |    re-checks SLIP fixes were applied correctly    |
                    +--------------------------------------------------+
```

---

## 3. Scope 2: Debate-Time Deviation Annotation (Prevention)

### 3.1 New Step: `annotate-deviations`

| Property | Value |
|----------|-------|
| Step ID | `annotate-deviations` |
| Position | Between `merge` and `test-strategy` |
| Inputs | `spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md` |
| Output | `spec-deviations.md` |
| Gate | `ANNOTATE_DEVIATIONS_GATE` -- STANDARD tier |
| Timeout | 300s |
| Retry | 0 |

### 3.2 Prompt Design: `build_annotate_deviations_prompt()`

**New function in `prompts.py`**. Key instructions:

- Reads the spec file directly (not the extraction) to avoid information loss
- For each deviation found, determines:
  1. Was it explicitly discussed in the debate transcript? (cite D-XX and round)
  2. Was consensus reached?
  3. Classification: `INTENTIONAL_IMPROVEMENT` | `INTENTIONAL_PREFERENCE` |
     `SCOPE_ADDITION` | `NOT_DISCUSSED`
- Only `INTENTIONAL_IMPROVEMENT` with valid debate citation excludes from
  fidelity severity counting
- `INTENTIONAL_PREFERENCE`, `SCOPE_ADDITION`, `NOT_DISCUSSED` all count normally

### 3.3 Output Format: `spec-deviations.md`

```yaml
---
total_annotated: 5
intentional_improvement_count: 2
intentional_preference_count: 1
scope_addition_count: 1
not_discussed_count: 1
---
```

Body contains:
- Structured table: ID, Spec Element, Deviation, Debate Ref, Round, Classification
- Evidence section per deviation: debate quote, consensus status, architectural assessment

Format chosen because:
- YAML frontmatter parseable by existing `_parse_frontmatter()` in `gates.py`
- Table structured enough for fidelity agent to consume without full re-analysis
- Evidence section provides spot-checkable citations

### 3.4 Gate Definition

```python
ANNOTATE_DEVIATIONS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_annotated",
        "intentional_improvement_count",
        "intentional_preference_count",
        "scope_addition_count",
        "not_discussed_count",
    ],
    min_lines=15,
    enforcement_tier="STANDARD",
)
```

Non-blocking: diagnostic artifact, not a quality gate.

### 3.5 Anti-Laundering Safeguards

1. **Separate subprocess**: annotate step runs as fresh Claude process with
   no state from generation/merge agents
2. **Citation requirement**: every `INTENTIONAL_IMPROVEMENT` must cite
   specific D-XX and round with quoted text
3. **Classification limits exclusion**: only `INTENTIONAL_IMPROVEMENT`
   eligible for fidelity exclusion; `INTENTIONAL_PREFERENCE` still counts
4. **Fidelity agent retains authority**: spot-checks annotations, can
   override; bogus citations escalated to HIGH

### 3.6 Fidelity Prompt Modification

`build_spec_fidelity_prompt()` gains parameter `spec_deviations_path: Path | None`.
New prompt section instructs fidelity agent to:

1. VERIFY cited D-XX reference exists and supports the claimed decision
2. VERIFY deviation description matches actual observation
3. EXCLUDE verified `INTENTIONAL_IMPROVEMENT` from severity counts
4. REPORT invalid annotations as HIGH severity
5. Analyze all `NOT_DISCUSSED` deviations independently

### 3.7 Spec-Fidelity Gate Downgrade

```
BEFORE: SPEC_FIDELITY_GATE.enforcement_tier = "STRICT"
        semantic_checks: [high_severity_count_zero, tasklist_ready_consistent]

AFTER:  SPEC_FIDELITY_GATE.enforcement_tier = "STANDARD"
        semantic_checks: [] (removed -- diagnostic only)
```

Rationale: spec-fidelity becomes a diagnostic step. The blocking decision
moves to deviation-analysis, where classification has occurred.

---

## 4. Scope 1: Post-Failure Deviation Analysis (Recovery)

### 4.1 New Step: `deviation-analysis`

| Property | Value |
|----------|-------|
| Step ID | `deviation-analysis` |
| Position | Between `spec-fidelity` and `remediate` |
| Inputs | `spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md` |
| Output | `deviation-analysis.md` |
| Gate | `DEVIATION_ANALYSIS_GATE` -- STRICT tier |
| Timeout | 300s |
| Retry | 1 |

### 4.2 Prompt Design: `build_deviation_analysis_prompt()`

**New function in `prompts.py`**. Key instructions:

For each HIGH and MEDIUM deviation in spec-fidelity.md:

1. Check spec-deviations.md for pre-approved annotations -> `PRE_APPROVED`
2. Search debate transcript for discussion -> `INTENTIONAL` (with citation)
3. If not discussed -> `SLIP`
4. If partially discussed -> `AMBIGUOUS`

For INTENTIONAL deviations, bounded blast radius analysis:
- Import chain impact
- Type contract impact
- Interface surface changes
- Spec coherence (does spec need updating?)

Remediation routing table:
- `SLIP` -> fix roadmap.md to match spec
- `INTENTIONAL` + superior -> recommend spec update
- `INTENTIONAL` + preference only -> fix roadmap.md to match spec
- `AMBIGUOUS` -> flag for human review

### 4.3 Output Format: `deviation-analysis.md`

```yaml
---
total_analyzed: 3
pre_approved_count: 1
intentional_count: 0
slip_count: 2
ambiguous_count: 0
adjusted_high_severity_count: 2
blast_radius_findings: 0
remediation_routing:
  fix_roadmap: ["DEV-002", "DEV-003"]
  update_spec: []
  no_action: ["DEV-001"]
  human_review: []
---
```

### 4.4 Gate Definition (Revised)

```python
DEVIATION_ANALYSIS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_analyzed",
        "adjusted_high_severity_count",
        "slip_count",
        "intentional_count",
        "ambiguous_count",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_ambiguous_deviations",
            check_fn=_no_ambiguous_deviations,  # ambiguous_count == 0
            failure_message="All deviations must be classified (no AMBIGUOUS remaining)",
        ),
    ],
)
```

**Critical design decision**: The gate blocks on **unresolved ambiguity**,
NOT on SLIP count. SLIPs are expected -- they get fixed by remediate
downstream. The gate ensures all deviations are fully classified before
remediation begins.

This is a revision from the initial brainstorm which proposed blocking
on `adjusted_high_severity_count == 0`. That design was flawed because
it would block remediation from running on the SLIPs it needed to fix.

---

## 5. Remediation Flow for SLIPs

### 5.1 Deviation-to-Finding Conversion

**New function needed** (in `remediate.py` or new module):

```python
def deviations_to_findings(
    deviation_analysis_path: Path,
    spec_fidelity_path: Path,
) -> list[Finding]:
```

Converts SLIP deviations into `Finding` objects consumable by the existing
`remediate_executor.py`. Maps:
- `FidelityDeviation.severity` HIGH -> `Finding.severity` BLOCKING
- `FidelityDeviation.severity` MEDIUM -> `Finding.severity` WARNING
- `FidelityDeviation.recommended_correction` -> `Finding.fix_guidance`
- Target file inferred from deviation type (model changes -> `roadmap.md`)

### 5.2 Finding Model Extension

```python
@dataclass
class Finding:
    # ... existing fields ...
    deviation_class: str = "SLIP"  # SLIP | INTENTIONAL | AMBIGUOUS | PRE_APPROVED
```

New field enables remediate agents to understand context:
- SLIP: "Fix the roadmap to match the spec for this item."
- INTENTIONAL: "No roadmap change needed."

### 5.3 Remediate Integration

Remediate step changes its primary input:
- **Before (v4)**: reads `spec-fidelity.md` -> parses all deviations
- **After (v5)**: reads `deviation-analysis.md` -> uses routing table ->
  only fixes SLIPs -> leaves INTENTIONAL deviations alone

### 5.4 Complete SLIP Remediation Flow

```
deviation-analysis (STRICT: no AMBIGUOUS)
    |
    +-- slip_count == 0 -> stub tasklist -> certify (trivial pass)
    |
    +-- slip_count > 0 -> remediate (fixes SLIPs in roadmap.md)
                              |
                         certify (STRICT: certified == true)
                              |
                              +-- all PASS -> pipeline complete
                              |
                              +-- some FAIL -> HALT
                                   |
                                   +-- --resume -> re-remediate failed only
                                        |          (max 2 total attempts)
                                        +-- re-certify
                                             |
                                             +-- PASS -> complete
                                             +-- FAIL -> terminal halt
                                                  (manual fix required)
```

---

## 6. Certify Step: Failure Handling (Gap Analysis)

### 6.1 Identified Gaps

The brainstorm identified four gaps in the current certify failure path:

**Gap 1: Certify gate doesn't block on failed findings**

Current `CERTIFY_GATE` has no `_certified_is_true` semantic check. A
certification report with `findings_failed: 1` and `certified: false`
can pass the gate structurally. This is a pre-existing bug.

**Fix**: Add semantic check:
```python
SemanticCheck(
    name="certified_true",
    check_fn=_certified_is_true,
    failure_message="Certification failed -- not all findings verified as FIXED",
)
```

**Gap 2: No recovery path after certify failure**

If certify fails, the current pipeline halts with `retry_limit=1`. The
retry reruns the certification prompt against the same unfixed roadmap --
the same futile-retry problem as spec-fidelity.

**Fix**: On certify failure, `--resume` triggers targeted re-remediation
of only the failed findings, then re-runs certify. Two sequential
`--resume` runs in worst case, no loop primitives needed.

**Gap 3: No distinction between "fix wrong" vs. "fix not attempted"**

`Finding.status` lifecycle is `PENDING -> FIXED | FAILED | SKIPPED`. No
`VERIFICATION_FAILED` state. When remediate exits 0 but fix is wrong,
finding is marked `FIXED`, then certify discovers it's not.

**Fix**: Either add `VERIFICATION_FAILED` status, or have certify update
the Finding status in the tasklist back to `FAILED` before halting.

**Gap 4: No terminal state with manual-fix instructions**

When automated remediation fails after max attempts, the pipeline halts
with generic error output. No specific guidance for what to fix manually.

**Fix**: Add `remediation_attempts` counter to `.roadmap-state.json`.
After 2+ failed attempts for same findings, produce terminal output:
```
ERROR: Remediation failed after 2 attempts for findings: DEV-003
  Manual intervention required.
  Unfixed: _all_gates_defined() still missing from Phase 2 gate deliverables
  To fix manually: edit roadmap.md, then run: superclaude roadmap certify --resume
```

### 6.2 Certify Re-Check Design

When certify follows SLIP remediation, the certification prompt should:
1. Read the SLIP findings from `deviation-analysis.md` routing table
2. For each SLIP finding marked as `fix_roadmap`:
   - Check that `roadmap.md` now contains the missing element
   - Verify the fix matches the spec (not just "something changed")
3. Produce per-finding PASS/FAIL with justification
4. Set `certified: true` only if all SLIP fixes verified

---

## 7. Interaction Analysis: How Both Scopes Compose

| Scenario | Scope 2 (annotate) | Scope 1 (classify) | Result |
|----------|--------------------|---------------------|--------|
| All deviations intentional | All annotated as INTENTIONAL_IMPROVEMENT | All pre-approved | Gate passes immediately |
| Mix of intentional + slips | Intentionals annotated; slips marked NOT_DISCUSSED | Slips classified; INTENTIONAL accepted | Remediate fixes SLIPs only |
| Annotator misses some | Partial annotations | Catches unannotated deviations from scratch | Full classification on remaining |
| Annotator over-approves | False INTENTIONAL_IMPROVEMENT claims | Fidelity agent catches invalid citations -> re-flags as HIGH | Gate blocks on bad annotations |
| No deviations at all | Empty report | Empty analysis | Both gates pass trivially |

### 7.1 What v2.24 Would Have Looked Like With v5

1. **annotate-deviations** would have classified `steps/` layout as
   INTENTIONAL_IMPROVEMENT (D-02, R2) and `executor.py` similarly (D-04, R2).
   Module renames (`cli.py`) and missing models would be NOT_DISCUSSED.

2. **spec-fidelity** would have excluded the `steps/` portion of DEV-001
   (pre-approved), keeping DEV-002 and DEV-003 as HIGH.

3. **deviation-analysis** would classify DEV-002 and DEV-003 as SLIPs,
   producing a routing table: `fix_roadmap: ["DEV-002", "DEV-003"]`.

4. **remediate** would receive targeted instructions: "Add the 3 missing
   data models. Add the 8 semantic check functions. Rename `cli.py` back
   to `commands.py`."

Pipeline still fails (genuine SLIPs exist), but with precise, actionable
remediation instead of blanket "3 HIGH deviations, go figure it out."

---

## 8. Implementation Constraints

### 8.1 Existing Primitives Only

All changes must use existing `Step`, `GateCriteria`, `SemanticCheck`
pattern. No new executor primitives unless strictly necessary.

### 8.2 Context Window Efficiency

Debate agents already consume significant tokens. Scope 2 must not add
prohibitive overhead to debate prompts. The annotate-deviations step reads
the spec directly rather than injecting spec context into debate prompts.

### 8.3 Machine Parseability

`spec-deviations.md` must be parseable by a fresh Claude subprocess with
minimal context. YAML frontmatter + structured markdown table.

### 8.4 Blast Radius Bounding

Blast radius analysis (Scope 1, step 4) must be bounded to import chains,
type contracts, and interface surface for specific named items. Not a full
re-analysis of the entire roadmap.

### 8.5 Skill Protocol Coherence

The Python CLI pipeline (`executor.py`, `prompts.py`, `gates.py`) and the
sc:roadmap skill protocol (Wave architecture in SKILL.md) must stay coherent.
`annotate-deviations` maps to Wave 3 sub-step. `deviation-analysis` maps
to Wave 3 post-validation classifier.

---

## 9. Open Questions

### 9.1 High Priority (must resolve before PRD)

1. **Should deviation-analysis accept AMBIGUOUS at lower severity?**
   Currently AMBIGUOUS with HIGH original severity blocks. Should there be
   a `--accept-ambiguous` flag that treats them as LOW?

2. **How does `--resume` interact with the new steps?** The `_apply_resume()`
   logic checks gate pass status. With spec-fidelity now STANDARD, it always
   "passes" on resume. deviation-analysis needs its own resume check.

3. **Remediation cycle bound**: How many remediate-certify cycles before
   terminal halt? Proposed: 2. Need to add `remediation_attempts` counter
   to `.roadmap-state.json`.

4. **Certify semantic check**: Should `_certified_is_true` be added to
   `CERTIFY_GATE`? This is a pre-existing gap, not v5-specific, but critical
   for the SLIP remediation flow to work.

### 9.2 Medium Priority (resolve during spec writing)

5. **Should annotate-deviations receive the extraction?** The extraction
   has structured FR/NFR IDs that could help map deviations to requirements.
   But adds context overhead.

6. **Blast radius depth**: Configurable? For some specs, import chain
   analysis is trivial. For others (monorepo with shared types), expensive.

7. **spec-deviations.md as living artifact**: Should `--resume` update or
   regenerate? Updating risks stale annotations; regenerating costs tokens.

### 9.3 Lower Priority (resolve during implementation)

8. **Spec update recommendations**: When deviation-analysis routes an
   INTENTIONAL+superior deviation to "update spec," who does the update?
   New `spec-update` step, or manual handoff?

9. **Finding.status lifecycle**: Add `VERIFICATION_FAILED` as a new
   terminal status, or reuse `FAILED` with a `failure_reason` field?

10. **Skill protocol alignment**: Specific Wave sub-step definitions for
    annotate-deviations and deviation-analysis in sc-roadmap-protocol SKILL.md.

---

## 10. Implementation Sequencing

### Phase 1: Scope 2 (Annotation) -- Implement First

**Rationale**: Simpler, preventive, reduces false positives immediately.
Scope 1 benefits from Scope 2's output.

**Deliverables**:
1. `build_annotate_deviations_prompt()` in `prompts.py`
2. `ANNOTATE_DEVIATIONS_GATE` in `gates.py`
3. `annotate-deviations` step in `_build_steps()` in `executor.py`
4. Modified `build_spec_fidelity_prompt()` -- accepts `spec_deviations_path`
5. Updated step inputs for spec-fidelity (add `spec-deviations.md`)
6. Tests for new gate and prompt
7. Skill protocol update in `sc-roadmap-protocol/SKILL.md`

**Estimated scope**: 4-5 files modified, ~200 lines new code.

### Phase 2: Scope 1 (Classification) -- Implement Second

**Deliverables**:
1. `build_deviation_analysis_prompt()` in `prompts.py`
2. `_no_ambiguous_deviations()` semantic check in `gates.py`
3. `DEVIATION_ANALYSIS_GATE` in `gates.py`
4. `deviation-analysis` step in `_build_steps()` in `executor.py`
5. Downgrade `SPEC_FIDELITY_GATE` from STRICT to STANDARD
6. `deviations_to_findings()` conversion function
7. Modified `Finding` model -- add `deviation_class` field
8. Modified `remediate_prompts.py` -- deviation-aware fix guidance
9. Resume logic for deviation-analysis step
10. Tests for new gate, semantic check, prompt, and conversion
11. Skill protocol update

**Estimated scope**: 6-7 files modified, ~350 lines new code.

### Phase 3: Certify Hardening

**Deliverables**:
1. `_certified_is_true` semantic check added to `CERTIFY_GATE`
2. `remediation_attempts` counter in `.roadmap-state.json`
3. Targeted re-remediation on `--resume` after certify failure
4. Terminal halt with manual-fix instructions after max attempts
5. Tests for certify gate semantic check and resume logic

**Estimated scope**: 3-4 files modified, ~150 lines new code.

### Phase 4: Validation

Run the v2.24 spec through the updated pipeline and verify:
- `steps/` subdirectory deviation is pre-approved (not flagged as HIGH)
- Missing data models and functions are classified as SLIPs
- Remediation correctly targets only the SLIPs
- Certify verifies SLIP fixes were applied
- End-to-end pipeline completes without manual intervention

---

## 11. Affected Code Paths

### 11.1 Files to Modify

| File | Changes |
|------|---------|
| `src/superclaude/cli/roadmap/prompts.py` | Add `build_annotate_deviations_prompt()`, `build_deviation_analysis_prompt()`; modify `build_spec_fidelity_prompt()` |
| `src/superclaude/cli/roadmap/gates.py` | Add `ANNOTATE_DEVIATIONS_GATE`, `DEVIATION_ANALYSIS_GATE`; add `_no_ambiguous_deviations()`, `_certified_is_true()` semantic checks; downgrade `SPEC_FIDELITY_GATE`; update `ALL_GATES` |
| `src/superclaude/cli/roadmap/executor.py` | Add 2 new steps to `_build_steps()`; update `_get_all_step_ids()`; add resume checks for new steps |
| `src/superclaude/cli/roadmap/models.py` | Add `deviation_class` field to `Finding` |
| `src/superclaude/cli/roadmap/remediate.py` | Add `deviations_to_findings()` conversion |
| `src/superclaude/cli/roadmap/remediate_prompts.py` | Deviation-aware fix guidance in agent prompts |
| `src/superclaude/cli/roadmap/fidelity.py` | Potentially extend `FidelityDeviation` with classification field |

### 11.2 New Files (if any)

| File | Purpose |
|------|---------|
| `src/superclaude/cli/roadmap/deviation_analysis.py` | (Optional) Deviation classification logic if too large for `remediate.py` |

### 11.3 Test Files

| File | Coverage |
|------|----------|
| `tests/roadmap/test_gates_data.py` | New gate definitions, semantic checks |
| `tests/roadmap/test_prompts.py` | New prompt builders |
| `tests/roadmap/test_deviation_conversion.py` | (New) `deviations_to_findings()` |
| `tests/roadmap/test_remediate.py` | Modified remediation flow |

---

## 12. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Annotate step over-approves deviations (laundering) | HIGH | Separate subprocess + citation requirement + fidelity spot-check |
| Deviation-analysis misclassifies SLIPs as INTENTIONAL | MEDIUM | Requires specific debate citation; fidelity report provides ground truth |
| Increased pipeline cost (2 new steps) | LOW | Each step ~300s; eliminates futile retries (saves 2x spec-fidelity cost) |
| Context window pressure on annotate-deviations (4 input files) | MEDIUM | Spec + roadmap + debate + diff is comparable to merge step (also 4 files) |
| Remediate-certify loop doesn't converge | MEDIUM | Bounded to 2 attempts; terminal halt with manual instructions |
| Resume logic complexity increases | LOW | Each new step follows existing resume check pattern |

---

## Appendix A: Key Code References

- Pipeline executor: `src/superclaude/cli/pipeline/executor.py`
- Roadmap step builder: `src/superclaude/cli/roadmap/executor.py:_build_steps()`
- Gate definitions: `src/superclaude/cli/roadmap/gates.py`
- Prompt builders: `src/superclaude/cli/roadmap/prompts.py`
- Fidelity model: `src/superclaude/cli/roadmap/fidelity.py`
- Remediate executor: `src/superclaude/cli/roadmap/remediate_executor.py`
- Remediate prompts: `src/superclaude/cli/roadmap/remediate_prompts.py`
- Finding model: `src/superclaude/cli/roadmap/models.py:Finding`
- Certify prompts: `src/superclaude/cli/roadmap/certify_prompts.py`
- Skill protocol: `.claude/skills/sc-roadmap-protocol/SKILL.md`

## Appendix B: v2.24 Failure Artifacts

- Spec file: `.dev/releases/current/v2.24-cli-portify-cli-v4/portify-release-spec.md`
- Fidelity report: `.dev/releases/current/v2.24-cli-portify-cli-v4/spec-fidelity.md`
- Debate transcript: `.dev/releases/current/v2.24-cli-portify-cli-v4/debate-transcript.md`
- Diff analysis: `.dev/releases/current/v2.24-cli-portify-cli-v4/diff-analysis.md`
- Base selection: `.dev/releases/current/v2.24-cli-portify-cli-v4/base-selection.md`
- Merged roadmap: `.dev/releases/current/v2.24-cli-portify-cli-v4/roadmap.md`
- Pipeline state: `.dev/releases/current/v2.24-cli-portify-cli-v4/.roadmap-state.json`
