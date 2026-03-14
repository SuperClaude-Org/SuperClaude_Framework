---
title: "v2.25 Roadmap v5: Deviation-Aware Pipeline -- Design Option A (Incremental Refactor)"
version: "2.25.0-A"
status: draft
scope:
  - "Scope 2: annotate-deviations step (prevention)"
  - "Scope 1: deviation-analysis step (recovery)"
  - "Scope 0: certify gate hardening (pre-existing gap fix)"
variant: A
design_philosophy: incremental_refactor
new_steps: 2
modified_steps: 3
new_executor_primitives: 0
pipeline_version: "v4 -> v5"
author: opus-architect
created: 2026-03-13
source: brainstorm-reference.md
---

# v2.25 Specification: Deviation-Aware Roadmap Pipeline (Option A)

## 1. Problem Statement

### 1.1 Triggering Incident

The roadmap pipeline for release v2.24-cli-portify-cli-v4 failed at the
`spec-fidelity` gate after exhausting its retry budget (2 attempts). The gate
enforces `high_severity_count == 0` via a STRICT-tier semantic check. The
fidelity report identified 20 deviations (3 HIGH, 12 MEDIUM, 5 LOW), and
because the retry mechanism re-runs the same prompt against the same unchanged
`roadmap.md`, both attempts produced identical output. The pipeline halted
permanently with no recovery path.

### 1.2 Root Cause Analysis

Six systemic failures converge to produce the v2.24 failure:

| # | Failure | Impact |
|---|---------|--------|
| F-1 | **Information loss in extraction**: spec-to-extraction loses module names, data models, function signatures. Generate agents work from extraction, not spec. | Generate agents cannot produce what they never saw. |
| F-2 | **No spec context in debate**: debate agents receive diff + two variants but never the spec file. They cannot flag spec departures. | Intentional deviations are undocumented. |
| F-3 | **No deviation annotation at merge**: merge agent produces `roadmap.md` without companion metadata marking spec departures. | Downstream steps lack classification context. |
| F-4 | **Fidelity agent works blind**: must rediscover all context from scratch, re-reading debate artifacts to understand what was intentional vs. accidental. | Misclassification risk; HIGH false positive rate. |
| F-5 | **Retry is futile**: same inputs produce same outputs. The retry mechanism re-runs the same fidelity prompt against the same unchanged roadmap. | Permanent halt on first fidelity failure. |
| F-6 | **No remediation path for classified deviations**: even correctly identified deviations have no automated flow distinguishing "fix this SLIP" from "this intentional deviation is fine." | Manual intervention required for every fidelity failure. |

### 1.3 Deviation Classification

Analysis of the v2.24 deviations reveals two distinct categories:

**INTENTIONAL (debate-resolved)**: 5 deviations with debate citations
- `steps/` subdirectory layout (D-02, R2 consensus)
- `executor.py` as explicit module (D-04, R2 consensus)
- `convergence.py` state enum (D-11, R2 partial consensus)
- `resume.py` as Phase 2 deliverable (D-12, consensus)
- Section hashing for additive-only enforcement (D-14, consensus)

**SLIPS (not debated, generation failures)**: 3 HIGH-severity deviations
- Module renames (`commands.py` -> `cli.py`, 3 modules collapsed into `monitor.py`)
- Missing 3/6 data models (`PortifyStatus`, `PortifyOutcome`, `PortifyStepResult`)
- Missing 8 semantic check function implementations

The pipeline cannot distinguish these categories. All 3 HIGH deviations are
SLIPs that should be automatically remediated, but the STRICT fidelity gate
blocks remediation from ever running.

---

## 2. Design Option A: Incremental Refactor

### 2.1 Design Philosophy

Option A introduces **two new steps** and **modifies three existing components**
using only existing executor primitives (`Step`, `GateCriteria`, `SemanticCheck`).
No new executor loop constructs, no new pipeline control flow, no new dataclass
hierarchies.

Key principles:
1. **Scope 2 implemented first** (prevention): reduces false positives at fidelity time
2. **Scope 1 implemented second** (recovery): catches what Scope 2 misses, routes to remediation
3. **Certify hardening last**: fixes a pre-existing gap that becomes critical for the SLIP flow
4. **Failure recovery via bounded `--resume` cycles**: max 2 remediate-certify attempts, no loop primitives

### 2.2 Pipeline Flow: v4 vs. v5

**v4 (current, 8 core steps + 2 post-validation)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> test-strategy -> spec-fidelity(STRICT)
  -> [post-pipeline: remediate -> certify]
```

**v5 (proposed, 10 core steps + 2 post-validation)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> annotate-deviations(NEW, STANDARD)
  -> test-strategy
  -> spec-fidelity(DOWNGRADED to STANDARD)
  -> deviation-analysis(NEW, STRICT)
  -> [post-pipeline: remediate(MODIFIED) -> certify(HARDENED)]
```

### 2.3 Step Inventory (Complete Pipeline Order)

| # | Step ID | Tier | Gate Blocks On | New/Modified |
|---|---------|------|----------------|--------------|
| 1 | `extract` | STRICT | frontmatter completeness | unchanged |
| 2a | `generate-{agent-A}` | STRICT | non-empty frontmatter, actionable content | unchanged |
| 2b | `generate-{agent-B}` | STRICT | non-empty frontmatter, actionable content | unchanged |
| 3 | `diff` | STANDARD | frontmatter presence | unchanged |
| 4 | `debate` | STRICT | convergence_score valid | unchanged |
| 5 | `score` | STANDARD | frontmatter presence | unchanged |
| 6 | `merge` | STRICT | heading structure, cross-refs | unchanged |
| 7 | `annotate-deviations` | STANDARD | frontmatter completeness | **NEW** |
| 8 | `test-strategy` | STANDARD | frontmatter presence | unchanged |
| 9 | `spec-fidelity` | STANDARD | frontmatter presence only | **MODIFIED** (downgraded) |
| 10 | `deviation-analysis` | STRICT | `ambiguous_count == 0` | **NEW** |
| -- | `remediate` | STRICT | all actionable have status | **MODIFIED** (input source) |
| -- | `certify` | STRICT | `certified == true` | **MODIFIED** (new semantic check) |

---

## 3. New Step: `annotate-deviations` (Scope 2 -- Prevention)

### 3.1 Step Definition

| Property | Value |
|----------|-------|
| Step ID | `annotate-deviations` |
| Position | Between `merge` (step 6) and `test-strategy` (step 8) |
| Inputs | `spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md` |
| Output | `spec-deviations.md` |
| Gate | `ANNOTATE_DEVIATIONS_GATE` (STANDARD tier) |
| Timeout | 300s |
| Retry limit | 0 (no retry -- diagnostic artifact) |

### 3.2 Step Construction in `_build_steps()`

```python
# In src/superclaude/cli/roadmap/executor.py, _build_steps()
# Insert between merge and test-strategy steps:

deviations_file = out / "spec-deviations.md"

# Step 7: Annotate Deviations (NEW -- Scope 2)
Step(
    id="annotate-deviations",
    prompt=build_annotate_deviations_prompt(
        config.spec_file, merge_file, debate_file, diff_file,
    ),
    output_file=deviations_file,
    gate=ANNOTATE_DEVIATIONS_GATE,
    timeout_seconds=300,
    inputs=[config.spec_file, merge_file, debate_file, diff_file],
    retry_limit=0,
),
```

### 3.3 Prompt Design: `build_annotate_deviations_prompt()`

New function in `src/superclaude/cli/roadmap/prompts.py`:

```python
def build_annotate_deviations_prompt(
    spec_file: Path,
    roadmap_file: Path,
    debate_file: Path,
    diff_file: Path,
) -> str:
    """Prompt for step 'annotate-deviations'.

    Reads the ORIGINAL spec file (not extraction) to avoid F-1 information
    loss. Compares spec against merged roadmap.md to identify deviations,
    then cross-references debate transcript for intentionality evidence.

    Classification scheme:
    - INTENTIONAL_IMPROVEMENT: debated, consensus reached, technically superior
    - INTENTIONAL_PREFERENCE: debated, consensus reached, stylistic preference
    - SCOPE_ADDITION: new element not in spec, debated
    - NOT_DISCUSSED: deviation with no debate citation

    Only INTENTIONAL_IMPROVEMENT with valid debate citation is eligible
    for fidelity exclusion. All other classes count normally.
    """
```

**Prompt instructions** (summarized):

1. Read the specification file in its entirety -- do NOT rely on the extraction.
2. Read the merged roadmap (`roadmap.md`).
3. For each element in the spec (modules, data models, function signatures, file
   paths, architectural decisions), check whether the roadmap faithfully
   represents it.
4. For each deviation found:
   a. Search the debate transcript for explicit discussion. Look for D-XX
      identifiers and round numbers.
   b. If discussed: determine whether consensus was reached. Quote the specific
      debate text (minimum 20 characters) that supports the classification.
   c. Classify as one of the four categories above.
5. Produce output in the specified YAML frontmatter + table + evidence format.

**Anti-laundering safeguards embedded in prompt**:
- "You MUST cite the specific D-XX identifier and round number for every
  INTENTIONAL_IMPROVEMENT classification."
- "A deviation without an exact, verifiable debate citation MUST be classified
  as NOT_DISCUSSED."
- "Do NOT infer intentionality from architectural quality. A superior design
  that was never debated is still NOT_DISCUSSED."

### 3.4 Output Format: `spec-deviations.md`

```yaml
---
total_annotated: 5
intentional_improvement_count: 2
intentional_preference_count: 1
scope_addition_count: 1
not_discussed_count: 1
---
```

Body structure:

```markdown
## Deviation Annotations

| ID | Spec Element | Deviation | Debate Ref | Round | Classification |
|----|-------------|-----------|------------|-------|----------------|
| AD-001 | File structure | `steps/` subdirectory | D-02 | R2 | INTENTIONAL_IMPROVEMENT |
| AD-002 | Data models | 3/6 models missing | -- | -- | NOT_DISCUSSED |
| ...    | ...          | ...                  | ... | ... | ... |

## Evidence

### AD-001: `steps/` subdirectory layout

**Debate Citation**: D-02, Round 2
> "The steps/ subdirectory provides cleaner separation of concerns.
> Both variants agree this is superior to flat layout." -- R2 consensus

**Consensus Status**: Full consensus (both agents agree)
**Classification**: INTENTIONAL_IMPROVEMENT
**Rationale**: Explicit debate with cited consensus. Superior to spec's flat layout.

### AD-002: Missing data models

**Debate Citation**: None
**Consensus Status**: N/A
**Classification**: NOT_DISCUSSED
**Rationale**: No mention of PortifyStatus, PortifyOutcome, or PortifyStepResult
in debate transcript. These models appear in spec Section 4.2 but are absent
from both generated roadmaps.
```

### 3.5 Gate Definition

```python
# In src/superclaude/cli/roadmap/gates.py

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

This gate is non-blocking in the semantic sense: it validates structural
completeness (frontmatter fields present, minimum content length) but does not
block on any deviation count. The artifact is diagnostic -- it feeds downstream
steps with pre-computed classification context.

---

## 4. Spec-Fidelity Downgrade (Scope 2 Modification)

### 4.1 Rationale

With the deviation-analysis step (Scope 1) taking over as the STRICT blocking
gate for deviation classification, spec-fidelity becomes a **diagnostic step**.
Its role changes from "gate that blocks the pipeline" to "analysis that feeds
the classifier."

### 4.2 Gate Change

**Before (v4)**:
```python
SPEC_FIDELITY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "high_severity_count", "medium_severity_count",
        "low_severity_count", "total_deviations",
        "validation_complete", "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="high_severity_count_zero",
            check_fn=_high_severity_count_zero,
            failure_message="high_severity_count must be 0 for spec-fidelity gate to pass",
        ),
        SemanticCheck(
            name="tasklist_ready_consistent",
            check_fn=_tasklist_ready_consistent,
            failure_message="tasklist_ready is inconsistent with severity counts or validation_complete",
        ),
    ],
)
```

**After (v5)**:
```python
SPEC_FIDELITY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "high_severity_count", "medium_severity_count",
        "low_severity_count", "total_deviations",
        "validation_complete", "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STANDARD",
    semantic_checks=None,  # Removed -- diagnostic only
)
```

Changes:
1. `enforcement_tier`: `"STRICT"` -> `"STANDARD"`
2. `semantic_checks`: removed (`high_severity_count_zero`, `tasklist_ready_consistent`)

The semantic check functions `_high_severity_count_zero` and
`_tasklist_ready_consistent` remain in `gates.py` (they are not deleted) because
they may be useful for manual validation or future steps. They are simply
de-registered from the gate criteria.

### 4.3 Fidelity Prompt Modification

`build_spec_fidelity_prompt()` gains a new optional parameter:

```python
def build_spec_fidelity_prompt(
    spec_file: Path,
    roadmap_file: Path,
    spec_deviations_path: Path | None = None,  # NEW
) -> str:
```

When `spec_deviations_path` is provided, the prompt adds instructions for the
fidelity agent to:

1. **VERIFY** each `INTENTIONAL_IMPROVEMENT` citation: confirm the D-XX
   reference exists in the debate transcript and supports the claimed decision.
2. **VERIFY** the deviation description matches the actual observation in
   `roadmap.md`.
3. **EXCLUDE** verified `INTENTIONAL_IMPROVEMENT` deviations from HIGH/MEDIUM
   severity counts.
4. **REPORT** invalid annotations (bogus citation, mismatched description) as
   HIGH severity findings -- this is the anti-laundering enforcement.
5. **ANALYZE** all `NOT_DISCUSSED` deviations independently, assigning severity
   as before.

### 4.4 Step Input Update

The spec-fidelity step gains `spec-deviations.md` as an additional input:

```python
# Updated spec-fidelity step in _build_steps()
Step(
    id="spec-fidelity",
    prompt=build_spec_fidelity_prompt(
        config.spec_file, merge_file,
        spec_deviations_path=deviations_file,  # NEW
    ),
    output_file=spec_fidelity_file,
    gate=SPEC_FIDELITY_GATE,
    timeout_seconds=600,
    inputs=[config.spec_file, merge_file, deviations_file],  # deviations_file added
    retry_limit=1,
),
```

---

## 5. New Step: `deviation-analysis` (Scope 1 -- Recovery)

### 5.1 Step Definition

| Property | Value |
|----------|-------|
| Step ID | `deviation-analysis` |
| Position | Between `spec-fidelity` (step 9) and `remediate` |
| Inputs | `spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md` |
| Output | `deviation-analysis.md` |
| Gate | `DEVIATION_ANALYSIS_GATE` (STRICT tier) |
| Timeout | 300s |
| Retry limit | 1 |

### 5.2 Step Construction in `_build_steps()`

```python
# In src/superclaude/cli/roadmap/executor.py, _build_steps()
# Insert after spec-fidelity step:

deviation_analysis_file = out / "deviation-analysis.md"

# Step 10: Deviation Analysis (NEW -- Scope 1)
Step(
    id="deviation-analysis",
    prompt=build_deviation_analysis_prompt(
        spec_fidelity_file, debate_file, diff_file,
        deviations_file, roadmap_a, roadmap_b,
    ),
    output_file=deviation_analysis_file,
    gate=DEVIATION_ANALYSIS_GATE,
    timeout_seconds=300,
    inputs=[
        spec_fidelity_file, debate_file, diff_file,
        deviations_file, roadmap_a, roadmap_b,
    ],
    retry_limit=1,
),
```

### 5.3 Prompt Design: `build_deviation_analysis_prompt()`

New function in `src/superclaude/cli/roadmap/prompts.py`:

```python
def build_deviation_analysis_prompt(
    spec_fidelity_file: Path,
    debate_file: Path,
    diff_file: Path,
    deviations_file: Path,
    roadmap_a_file: Path,
    roadmap_b_file: Path,
) -> str:
    """Prompt for step 'deviation-analysis'.

    Classifies each HIGH and MEDIUM deviation from the fidelity report
    into one of four categories, then produces a remediation routing
    table consumed by the downstream remediate step.

    Classification scheme:
    - PRE_APPROVED: already annotated as INTENTIONAL_IMPROVEMENT in
      spec-deviations.md and verified by fidelity agent
    - INTENTIONAL: discussed in debate with citation (not pre-approved
      but confirmed via debate search)
    - SLIP: not discussed in debate, no annotation -- generation failure
    - AMBIGUOUS: partially discussed, unclear consensus

    Remediation routing:
    - SLIP -> fix roadmap.md to match spec
    - INTENTIONAL (superior) -> recommend spec update (no roadmap change)
    - INTENTIONAL (preference only) -> fix roadmap.md to match spec
    - AMBIGUOUS -> flag for human review (gate blocks)
    """
```

**Prompt instructions** (summarized):

For each HIGH and MEDIUM deviation in `spec-fidelity.md`:

1. Check `spec-deviations.md` for a pre-approved annotation with verified
   citation. If found and fidelity agent confirmed it, classify as `PRE_APPROVED`.
2. If not pre-approved, search `debate-transcript.md` for explicit discussion.
   Require specific D-XX identifier and round. If found with consensus, classify
   as `INTENTIONAL`.
3. If not found in debate, classify as `SLIP`.
4. If partially discussed (mentioned but no resolution, or disputed), classify
   as `AMBIGUOUS`.

For each `INTENTIONAL` deviation, perform bounded blast radius analysis:
- Import chain impact (which modules import the changed element)
- Type contract impact (do type signatures change downstream)
- Interface surface changes (are public APIs affected)
- Spec coherence assessment (should spec be updated to match)

Produce a remediation routing table:
- `fix_roadmap`: list of deviation IDs classified as SLIP or INTENTIONAL-preference
- `update_spec`: list of deviation IDs classified as INTENTIONAL-superior
- `no_action`: list of PRE_APPROVED deviation IDs
- `human_review`: list of AMBIGUOUS deviation IDs

### 5.4 Output Format: `deviation-analysis.md`

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

Body structure:

```markdown
## Deviation Classification

| ID | Original Severity | Classification | Debate Ref | Routing |
|----|-------------------|---------------|------------|---------|
| DEV-001 | HIGH | PRE_APPROVED | D-02, R2 | no_action |
| DEV-002 | HIGH | SLIP | -- | fix_roadmap |
| DEV-003 | HIGH | SLIP | -- | fix_roadmap |

## Classification Evidence

### DEV-001: File structure mismatch

**Pre-Approved**: Yes (AD-001 in spec-deviations.md)
**Fidelity Verification**: Confirmed -- D-02 citation valid
**Classification**: PRE_APPROVED
**Routing**: no_action

### DEV-002: Missing data models

**Pre-Approved**: No
**Debate Search**: No mention of PortifyStatus, PortifyOutcome, PortifyStepResult
**Classification**: SLIP
**Routing**: fix_roadmap
**Fix Guidance**: Add missing data model definitions to roadmap Section 4.2:
PortifyStatus, PortifyOutcome, PortifyStepResult with fields per spec.

### DEV-003: Missing semantic check implementations

**Pre-Approved**: No
**Debate Search**: No discussion of gate check function implementations
**Classification**: SLIP
**Routing**: fix_roadmap
**Fix Guidance**: Add 8 semantic check function signatures to roadmap Section 5.2.1.

## Blast Radius Analysis

No INTENTIONAL deviations require blast radius analysis (all PRE_APPROVED or SLIP).
```

### 5.5 Gate Definition

```python
# In src/superclaude/cli/roadmap/gates.py

def _no_ambiguous_deviations(content: str) -> bool:
    """Validate that ambiguous_count equals zero in deviation analysis frontmatter.

    The deviation-analysis gate blocks on unresolved ambiguity, NOT on SLIP
    count. SLIPs are expected -- they get fixed by remediate downstream.
    The gate ensures all deviations are fully classified before remediation.

    Returns True only if ambiguous_count is present and equals 0.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("ambiguous_count")
    if value is None:
        return False

    try:
        count = int(value)
    except (ValueError, TypeError):
        return False

    return count == 0


DEVIATION_ANALYSIS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_analyzed",
        "pre_approved_count",
        "intentional_count",
        "slip_count",
        "ambiguous_count",
        "adjusted_high_severity_count",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_ambiguous_deviations",
            check_fn=_no_ambiguous_deviations,
            failure_message=(
                "All deviations must be fully classified. "
                "ambiguous_count must be 0 before remediation can proceed."
            ),
        ),
    ],
)
```

**Critical design decision**: The gate blocks on **unresolved ambiguity**, NOT
on SLIP count or `adjusted_high_severity_count`. SLIPs are expected outputs --
they represent generation failures that the remediate step will fix. Blocking on
SLIP count would prevent remediation from ever running, recreating the v2.24
failure. The gate's purpose is to ensure every deviation has been definitively
classified so remediation receives unambiguous routing instructions.

### 5.6 Why `ambiguous_count == 0` and Not `adjusted_high_severity_count == 0`

The initial brainstorm considered blocking on `adjusted_high_severity_count == 0`.
This was rejected because:

1. A SLIP with HIGH original severity contributes to `adjusted_high_severity_count`.
2. The remediate step exists specifically to fix SLIPs.
3. Blocking on adjusted count would prevent remediation from running on the
   exact findings it needs to fix -- the same deadlock as v2.24.

The `ambiguous_count == 0` check ensures the classifier has made a definitive
decision on every deviation. If it cannot decide, the pipeline halts for human
review. If all deviations are classified (even if many are SLIPs), remediation
proceeds with clear routing instructions.

---

## 6. Certify Gate Hardening

### 6.1 Pre-Existing Gap

The current `CERTIFY_GATE` validates structural completeness (frontmatter fields
present, per-finding table exists) but does NOT check whether `certified` is
actually `true`. A certification report with `certified: false` and
`findings_failed: 3` passes the gate structurally. This is a pre-existing bug
that becomes critical for the SLIP remediation flow.

### 6.2 New Semantic Check

```python
# In src/superclaude/cli/roadmap/gates.py

def _certified_is_true(content: str) -> bool:
    """Validate that the certified field is 'true' in certification report.

    Returns True only if frontmatter contains certified: true (case-insensitive).
    Returns False if:
    - Frontmatter is missing
    - certified field is missing
    - certified value is anything other than 'true'
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("certified")
    if value is None:
        return False

    return value.strip().lower() == "true"
```

### 6.3 Updated CERTIFY_GATE

```python
CERTIFY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "findings_verified",
        "findings_passed",
        "findings_failed",
        "certified",
        "certification_date",
    ],
    min_lines=15,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
        SemanticCheck(
            name="per_finding_table_present",
            check_fn=_has_per_finding_table,
            failure_message="Certification report missing per-finding results table",
        ),
        SemanticCheck(
            name="certified_true",
            check_fn=_certified_is_true,
            failure_message=(
                "Certification failed -- certified must be true. "
                "Not all findings verified as FIXED."
            ),
        ),
    ],
)
```

The new `certified_true` semantic check is appended to the existing list. The
two original checks (`frontmatter_values_non_empty`, `per_finding_table_present`)
remain unchanged.

---

## 7. Remediation Flow Modifications

### 7.1 Finding Model Extension

Add `deviation_class` field to `Finding` in `src/superclaude/cli/roadmap/models.py`:

```python
VALID_FINDING_STATUSES = frozenset({"PENDING", "FIXED", "FAILED", "SKIPPED"})
VALID_DEVIATION_CLASSES = frozenset({
    "SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", "",
})


@dataclass
class Finding:
    """A single validation finding extracted from a report.

    Fields align with spec section 2.3.1. Status lifecycle defined in D-0003:
    PENDING -> FIXED | FAILED | SKIPPED (all terminal).

    deviation_class added in v2.25 for deviation-aware remediation routing.
    Empty string indicates a finding from the pre-v5 pipeline (backward compat).
    """

    id: str
    severity: str
    dimension: str
    description: str
    location: str
    evidence: str
    fix_guidance: str
    files_affected: list[str] = field(default_factory=list)
    status: str = "PENDING"
    agreement_category: str = ""
    deviation_class: str = ""  # NEW: SLIP | INTENTIONAL | AMBIGUOUS | PRE_APPROVED | ""

    def __post_init__(self) -> None:
        if self.status not in VALID_FINDING_STATUSES:
            raise ValueError(
                f"Invalid Finding status {self.status!r}. "
                f"Must be one of: {', '.join(sorted(VALID_FINDING_STATUSES))}"
            )
        if self.deviation_class and self.deviation_class not in VALID_DEVIATION_CLASSES:
            raise ValueError(
                f"Invalid deviation_class {self.deviation_class!r}. "
                f"Must be one of: {', '.join(sorted(VALID_DEVIATION_CLASSES))}"
            )
```

The `deviation_class` field defaults to empty string for backward compatibility
with pre-v5 pipelines. The `__post_init__` validation is extended to check the
new field only when non-empty.

### 7.2 Deviation-to-Finding Conversion

New function in `src/superclaude/cli/roadmap/remediate.py` (or a new
`deviation_analysis.py` module if remediate.py is too large):

```python
def deviations_to_findings(
    deviation_analysis_path: Path,
    spec_fidelity_path: Path,
) -> list[Finding]:
    """Convert classified deviations into Finding objects for remediation.

    Reads the deviation-analysis.md routing table and spec-fidelity.md
    deviation details. Produces Finding objects only for deviations routed
    to fix_roadmap (SLIPs and INTENTIONAL-preference).

    Mapping:
    - FidelityDeviation.severity HIGH -> Finding.severity "BLOCKING"
    - FidelityDeviation.severity MEDIUM -> Finding.severity "WARNING"
    - FidelityDeviation.recommended_correction -> Finding.fix_guidance
    - deviation_class from routing table -> Finding.deviation_class

    Deviations routed to no_action or update_spec are excluded from the
    returned list (they do not need roadmap changes).

    Parameters
    ----------
    deviation_analysis_path:
        Path to deviation-analysis.md (contains routing table).
    spec_fidelity_path:
        Path to spec-fidelity.md (contains deviation details and evidence).

    Returns
    -------
    list[Finding]:
        Findings for deviations that require roadmap fixes.
    """
    from .gates import _parse_frontmatter

    # Parse deviation analysis frontmatter for routing table
    da_content = deviation_analysis_path.read_text(encoding="utf-8")
    da_fm = _parse_frontmatter(da_content)
    if da_fm is None:
        return []

    # Extract fix_roadmap list from routing
    # Frontmatter YAML list format: ["DEV-002", "DEV-003"]
    fix_ids = _parse_routing_list(da_content, "fix_roadmap")

    if not fix_ids:
        return []

    # Parse fidelity report for deviation details
    fidelity_content = spec_fidelity_path.read_text(encoding="utf-8")
    fidelity_deviations = _extract_fidelity_deviations(fidelity_content)

    findings: list[Finding] = []
    for dev_id in fix_ids:
        dev = fidelity_deviations.get(dev_id)
        if dev is None:
            continue

        severity_map = {"HIGH": "BLOCKING", "MEDIUM": "WARNING", "LOW": "INFO"}
        finding_severity = severity_map.get(dev.get("severity", ""), "WARNING")

        findings.append(Finding(
            id=dev_id,
            severity=finding_severity,
            dimension="spec-fidelity",
            description=dev.get("description", ""),
            location=dev.get("location", "roadmap.md"),
            evidence=dev.get("evidence", ""),
            fix_guidance=dev.get("fix_guidance", ""),
            files_affected=["roadmap.md"],
            status="PENDING",
            deviation_class="SLIP",
        ))

    return findings
```

### 7.3 Remediate Step Input Change

The remediate step changes its primary input source:

**Before (v4)**: reads `spec-fidelity.md` directly, parses all deviations as findings
**After (v5)**: reads `deviation-analysis.md` routing table, only processes
deviations routed to `fix_roadmap`

This change is in the remediation prompt builder and executor, not in
`_build_steps()` (remediate is built separately via `build_remediate_step()` or
equivalent in the post-pipeline flow).

### 7.4 Remediate Prompt Modification

The remediation prompt gains deviation-class awareness:

```python
# In src/superclaude/cli/roadmap/remediate_prompts.py
# Modified prompt section for each SLIP finding:

"""
For finding {finding.id} (deviation_class: {finding.deviation_class}):
- This is a SLIP: the roadmap deviates from the spec and the deviation
  was never discussed or approved in the debate.
- Fix: modify roadmap.md to match the spec for this specific element.
- Do NOT change elements classified as INTENTIONAL or PRE_APPROVED.
- Specific guidance: {finding.fix_guidance}
"""
```

---

## 8. Resume Logic Modifications

### 8.1 Current Resume Behavior

`_apply_resume()` iterates through steps, checking each step's output file
against its gate criteria. Steps whose outputs already pass their gates are
skipped. The first step that fails its gate check (or whose output does not
exist) becomes the resume point.

### 8.2 Impact of v5 Changes on Resume

With spec-fidelity downgraded to STANDARD, it will "always pass" on resume
(STANDARD gates check frontmatter presence only, no semantic blocking). This is
correct behavior: spec-fidelity is now diagnostic, and its output persists
across resume cycles.

The new `deviation-analysis` step with its STRICT gate (`ambiguous_count == 0`)
becomes the natural resume checkpoint. If the deviation analysis produced
ambiguous results, `--resume` will re-run it (after the user addresses the
ambiguity in the underlying artifacts).

### 8.3 New Step IDs in `_get_all_step_ids()`

```python
def _get_all_step_ids(config: RoadmapConfig) -> list[str]:
    """Get all step IDs in pipeline order."""
    agent_a = config.agents[0]
    agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]
    return [
        "extract",
        f"generate-{agent_a.id}",
        f"generate-{agent_b.id}",
        "diff",
        "debate",
        "score",
        "merge",
        "annotate-deviations",  # NEW
        "test-strategy",
        "spec-fidelity",
        "deviation-analysis",   # NEW
        "remediate",
        "certify",
    ]
```

### 8.4 Remediation Cycle Bounding

Add `remediation_attempts` counter to `.roadmap-state.json`:

```python
# In _save_state(), when remediate metadata is present:
if remediate_metadata is not None:
    existing_attempts = 0
    if existing_remediate is not None:
        existing_attempts = existing_remediate.get("remediation_attempts", 0)
    remediate_metadata["remediation_attempts"] = existing_attempts + 1
    state["remediate"] = remediate_metadata
```

The `--resume` flow checks this counter:

```python
# In the post-pipeline remediate-certify flow:
def _check_remediation_budget(config: RoadmapConfig, max_attempts: int = 2) -> bool:
    """Check if remediation attempts are within budget.

    Returns True if more attempts are allowed, False if max reached.
    When False, produces terminal halt with manual-fix instructions.
    """
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    if state is None:
        return True

    remediate = state.get("remediate")
    if remediate is None:
        return True

    attempts = remediate.get("remediation_attempts", 0)
    if attempts >= max_attempts:
        _print_terminal_halt(config, state)
        return False

    return True
```

### 8.5 Terminal Halt Output

When remediation budget is exhausted:

```python
def _print_terminal_halt(config: RoadmapConfig, state: dict) -> None:
    """Print terminal halt message with manual-fix instructions."""
    remediate = state.get("remediate", {})
    certify = state.get("certify", {})

    failed_findings = certify.get("findings_failed", 0)

    lines = [
        f"ERROR: Remediation failed after {remediate.get('remediation_attempts', 0)} attempts.",
        f"  Findings still failing: {failed_findings}",
        "",
        "Manual intervention required.",
        "  1. Review the certification report for specific failures:",
        f"     cat {config.output_dir / 'certification-report.md'}",
        "  2. Edit roadmap.md to fix the identified issues",
        "  3. Re-run certification:",
        f"     superclaude roadmap certify --resume {config.spec_file}",
        "",
        "The pipeline will not retry automatically beyond this point.",
    ]
    print("\n".join(lines), file=sys.stderr, flush=True)
```

### 8.6 Resume Flow: Post-Pipeline Remediate-Certify

The full resume-aware remediate-certify flow (no loop primitives):

```
First run:
  deviation-analysis PASS (ambiguous_count == 0)
  -> deviations_to_findings() produces SLIP findings
  -> remediate runs, fixes SLIPs in roadmap.md
  -> certify runs, checks fixes
  -> if certify PASS: pipeline complete
  -> if certify FAIL: halt with "run --resume"

--resume (attempt 2):
  -> check_remediation_budget() (attempts=1, max=2, allowed)
  -> re-remediate failed findings only
  -> re-certify
  -> if certify PASS: pipeline complete
  -> if certify FAIL: halt with terminal message

--resume (attempt 3):
  -> check_remediation_budget() (attempts=2, max=2, BLOCKED)
  -> _print_terminal_halt() with manual-fix instructions
  -> sys.exit(1)
```

This uses two sequential `--resume` invocations, not a loop primitive. Each
invocation is a fresh pipeline execution that checks state and resumes from
the appropriate point.

---

## 9. Interaction Analysis: How Scopes Compose

### 9.1 Composition Table

| Scenario | Scope 2 (annotate) | Fidelity | Scope 1 (classify) | Remediate | Result |
|----------|--------------------|----------|---------------------|-----------|--------|
| All deviations intentional | All INTENTIONAL_IMPROVEMENT | Excludes pre-approved, 0 HIGH | All PRE_APPROVED, 0 SLIP | No-op | Clean pass |
| Mix of intentional + slips | Intentionals annotated; slips NOT_DISCUSSED | Reports slips as HIGH | Slips classified SLIP; intentionals PRE_APPROVED | Fixes SLIPs only | Targeted remediation |
| Annotator misses some | Partial annotations | Reports all unannotated as HIGH | Catches unannotated from debate search | Fixes SLIPs, accepts found-intentionals | Recovery |
| Annotator over-approves | False INTENTIONAL_IMPROVEMENT | Catches bogus citations -> re-flags as HIGH | Sees re-flagged as HIGH SLIP | Fixes over-approved items | Anti-laundering |
| No deviations at all | Empty report (total_annotated: 0) | 0 deviations | Empty analysis (total_analyzed: 0) | No-op | Trivial pass |
| All ambiguous | Mixed annotations | Reports ambiguous items | ambiguous_count > 0, gate BLOCKS | N/A | Human review required |

### 9.2 v2.24 Retroactive Analysis

With v5, the v2.24 pipeline would have proceeded as follows:

1. **annotate-deviations**: `steps/` layout classified as INTENTIONAL_IMPROVEMENT
   (D-02, R2). Module renames and missing models classified as NOT_DISCUSSED.

2. **spec-fidelity** (STANDARD): Reports all deviations but does not block.
   Excludes verified `steps/` annotation from severity. DEV-002 and DEV-003
   remain HIGH.

3. **deviation-analysis** (STRICT): Classifies DEV-002 (missing models) and
   DEV-003 (missing functions) as SLIPs. `ambiguous_count: 0`. Gate passes.
   Routing: `fix_roadmap: ["DEV-002", "DEV-003"]`.

4. **remediate**: Receives targeted instructions to add 3 missing data models
   and 8 missing function signatures. Fixes `roadmap.md`.

5. **certify**: Verifies SLIP fixes applied correctly. `certified: true`.

Pipeline completes automatically. No manual intervention needed.

---

## 10. Implementation Phases

### Phase 1: Scope 2 -- Annotation (Prevention)

**Rationale**: Simpler scope, immediate value. Reduces false positives at
fidelity time. Scope 1 benefits from Scope 2's output.

**Deliverables**:

| # | File | Change |
|---|------|--------|
| 1 | `src/superclaude/cli/roadmap/prompts.py` | Add `build_annotate_deviations_prompt()` |
| 2 | `src/superclaude/cli/roadmap/gates.py` | Add `ANNOTATE_DEVIATIONS_GATE` constant |
| 3 | `src/superclaude/cli/roadmap/executor.py` | Add `annotate-deviations` step to `_build_steps()` between merge and test-strategy |
| 4 | `src/superclaude/cli/roadmap/prompts.py` | Modify `build_spec_fidelity_prompt()` to accept `spec_deviations_path` parameter |
| 5 | `src/superclaude/cli/roadmap/executor.py` | Update spec-fidelity step inputs to include `deviations_file` |
| 6 | `src/superclaude/cli/roadmap/executor.py` | Update `_get_all_step_ids()` to include `annotate-deviations` |
| 7 | `src/superclaude/cli/roadmap/gates.py` | Update `ALL_GATES` list to include `annotate-deviations` entry |
| 8 | `tests/roadmap/test_gates_data.py` | Tests for `ANNOTATE_DEVIATIONS_GATE` |
| 9 | `tests/roadmap/test_prompts.py` | Tests for `build_annotate_deviations_prompt()` |

**Estimated scope**: 4 files modified, ~200 lines new code, ~50 lines test code.

### Phase 2: Scope 1 -- Classification (Recovery)

**Deliverables**:

| # | File | Change |
|---|------|--------|
| 1 | `src/superclaude/cli/roadmap/prompts.py` | Add `build_deviation_analysis_prompt()` |
| 2 | `src/superclaude/cli/roadmap/gates.py` | Add `_no_ambiguous_deviations()` semantic check function |
| 3 | `src/superclaude/cli/roadmap/gates.py` | Add `DEVIATION_ANALYSIS_GATE` constant |
| 4 | `src/superclaude/cli/roadmap/executor.py` | Add `deviation-analysis` step to `_build_steps()` after spec-fidelity |
| 5 | `src/superclaude/cli/roadmap/gates.py` | Downgrade `SPEC_FIDELITY_GATE`: `enforcement_tier="STANDARD"`, `semantic_checks=None` |
| 6 | `src/superclaude/cli/roadmap/models.py` | Add `deviation_class` field to `Finding`, add `VALID_DEVIATION_CLASSES` |
| 7 | `src/superclaude/cli/roadmap/remediate.py` | Add `deviations_to_findings()` conversion function |
| 8 | `src/superclaude/cli/roadmap/remediate_prompts.py` | Add deviation-class-aware fix guidance in agent prompts |
| 9 | `src/superclaude/cli/roadmap/executor.py` | Update `_get_all_step_ids()` to include `deviation-analysis` |
| 10 | `src/superclaude/cli/roadmap/gates.py` | Update `ALL_GATES` list to include `deviation-analysis` entry |
| 11 | `tests/roadmap/test_gates_data.py` | Tests for `DEVIATION_ANALYSIS_GATE`, `_no_ambiguous_deviations()` |
| 12 | `tests/roadmap/test_prompts.py` | Tests for `build_deviation_analysis_prompt()` |
| 13 | `tests/roadmap/test_deviation_conversion.py` | New test file for `deviations_to_findings()` |
| 14 | `tests/roadmap/test_remediate.py` | Modified tests for deviation-aware remediation |

**Estimated scope**: 6-7 files modified, 1 new test file, ~350 lines new code, ~100 lines test code.

### Phase 3: Certify Hardening

**Deliverables**:

| # | File | Change |
|---|------|--------|
| 1 | `src/superclaude/cli/roadmap/gates.py` | Add `_certified_is_true()` semantic check function |
| 2 | `src/superclaude/cli/roadmap/gates.py` | Append `certified_true` SemanticCheck to `CERTIFY_GATE` |
| 3 | `src/superclaude/cli/roadmap/executor.py` | Add `remediation_attempts` counter to `_save_state()` |
| 4 | `src/superclaude/cli/roadmap/executor.py` | Add `_check_remediation_budget()` and `_print_terminal_halt()` |
| 5 | `tests/roadmap/test_gates_data.py` | Tests for `_certified_is_true()` |
| 6 | `tests/roadmap/test_executor.py` | Tests for remediation budget checking and terminal halt |

**Estimated scope**: 2-3 files modified, ~150 lines new code, ~60 lines test code.

### Phase 4: Validation

Run the v2.24 spec through the updated v5 pipeline end-to-end and verify:

1. `steps/` subdirectory deviation is pre-approved via annotate-deviations
   (not flagged as HIGH by fidelity)
2. Missing data models and functions are classified as SLIPs by
   deviation-analysis
3. Remediation correctly targets only the SLIPs (does not modify
   intentional deviations)
4. Certify verifies SLIP fixes were applied to `roadmap.md`
5. Full pipeline completes without manual intervention

---

## 11. Affected Files Summary

### Files Modified

| File | Phase | Changes |
|------|-------|---------|
| `src/superclaude/cli/roadmap/prompts.py` | 1, 2 | Add `build_annotate_deviations_prompt()`, `build_deviation_analysis_prompt()`; modify `build_spec_fidelity_prompt()` signature |
| `src/superclaude/cli/roadmap/gates.py` | 1, 2, 3 | Add `ANNOTATE_DEVIATIONS_GATE`, `DEVIATION_ANALYSIS_GATE`; add `_no_ambiguous_deviations()`, `_certified_is_true()` semantic checks; downgrade `SPEC_FIDELITY_GATE`; update `ALL_GATES` |
| `src/superclaude/cli/roadmap/executor.py` | 1, 2, 3 | Add 2 steps to `_build_steps()`; update `_get_all_step_ids()`; add `remediation_attempts` counter; add `_check_remediation_budget()`, `_print_terminal_halt()` |
| `src/superclaude/cli/roadmap/models.py` | 2 | Add `deviation_class` field to `Finding`; add `VALID_DEVIATION_CLASSES` |
| `src/superclaude/cli/roadmap/remediate.py` | 2 | Add `deviations_to_findings()` conversion function |
| `src/superclaude/cli/roadmap/remediate_prompts.py` | 2 | Add deviation-class-aware fix guidance |

### Files Potentially Modified

| File | Phase | Changes |
|------|-------|---------|
| `src/superclaude/cli/roadmap/fidelity.py` | 2 | Extend `FidelityDeviation` with classification field if separate from Finding |
| `.claude/skills/sc-roadmap-protocol/SKILL.md` | 1, 2 | Wave sub-step definitions for new steps |

### New Files

| File | Phase | Purpose |
|------|-------|---------|
| `tests/roadmap/test_deviation_conversion.py` | 2 | Unit tests for `deviations_to_findings()` |

### Test Files Modified

| File | Phase | Coverage |
|------|-------|----------|
| `tests/roadmap/test_gates_data.py` | 1, 2, 3 | New gate definitions, semantic checks |
| `tests/roadmap/test_prompts.py` | 1, 2 | New prompt builders |
| `tests/roadmap/test_remediate.py` | 2 | Deviation-aware remediation |
| `tests/roadmap/test_executor.py` | 3 | Remediation budget, terminal halt |

---

## 12. Risk Assessment

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **R-1**: Annotate step over-approves deviations (laundering). Agent classifies SLIPs as INTENTIONAL_IMPROVEMENT to reduce severity counts. | HIGH | LOW | Separate subprocess with no state from generation agents. Citation requirement (must quote D-XX + round). Fidelity agent spot-checks citations and re-flags bogus ones as HIGH. |
| **R-2**: Deviation-analysis misclassifies SLIPs as INTENTIONAL. Agent invents debate citations to avoid triggering remediation. | MEDIUM | LOW | Requires specific D-XX identifier and round number matching entries in debate transcript. Fidelity report provides independent ground truth for cross-validation. |
| **R-3**: Increased pipeline cost. Two new steps add ~600s of Claude subprocess time. | LOW | HIGH (certain) | Each step ~300s. Eliminates futile retry cost (2x spec-fidelity @ 600s each = 1200s saved on failure). Net cost reduction on failure paths. |
| **R-4**: Context window pressure on annotate-deviations. Step reads 4 input files (spec + roadmap + debate + diff). | MEDIUM | MEDIUM | Input set comparable to merge step (also 4 files). Spec files are typically 5-15KB. Total input within 200KB embed limit. |
| **R-5**: Remediate-certify loop does not converge. Same SLIP fixes fail certification repeatedly. | MEDIUM | LOW | Bounded to 2 attempts (no infinite loop). Terminal halt with manual-fix instructions provides escape hatch. |
| **R-6**: Resume logic complexity increases. Two new steps add resume checkpoints. | LOW | LOW | Each new step follows existing resume check pattern in `_apply_resume()`. No new resume primitives needed. |
| **R-7**: spec-fidelity STANDARD downgrade masks real issues. Removing semantic checks means fidelity failures do not halt the pipeline. | MEDIUM | LOW | Deviation-analysis STRICT gate catches all real issues. Fidelity report still produced as diagnostic artifact. The blocking decision moves to a step with better context (classification, not raw counts). |
| **R-8**: `deviation_class` field breaks existing Finding consumers. | LOW | LOW | Field defaults to empty string. `__post_init__` only validates when non-empty. All existing code paths produce Findings without deviation_class, which is valid. |
| **R-9**: YAML frontmatter parsing for routing table is fragile. `remediation_routing` contains nested lists in YAML that `_parse_frontmatter()` may not handle. | MEDIUM | MEDIUM | `_parse_frontmatter()` does simple `key: value` splitting. Nested YAML lists require either: (a) a dedicated parser for the routing section, or (b) encoding the routing as simple comma-separated values in frontmatter. Recommend option (b) for robustness. |

### R-9 Mitigation Detail

The `remediation_routing` field in `deviation-analysis.md` uses YAML list syntax
that the existing `_parse_frontmatter()` cannot parse (it splits on first `:`
per line). Two options:

**Option A (recommended)**: Flatten routing into simple frontmatter fields:
```yaml
---
routing_fix_roadmap: DEV-002,DEV-003
routing_update_spec:
routing_no_action: DEV-001
routing_human_review:
---
```

**Option B**: Use a dedicated YAML parser (`yaml.safe_load`) for the
deviation-analysis output. This adds a dependency but handles complex structures.

This spec recommends Option A (flat fields) for consistency with existing
frontmatter conventions in the pipeline.

If Option A is adopted, the `DEVIATION_ANALYSIS_GATE` frontmatter fields list
should include the routing fields:

```python
DEVIATION_ANALYSIS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_analyzed",
        "pre_approved_count",
        "intentional_count",
        "slip_count",
        "ambiguous_count",
        "adjusted_high_severity_count",
        "routing_fix_roadmap",
        "routing_update_spec",
        "routing_no_action",
        "routing_human_review",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_ambiguous_deviations",
            check_fn=_no_ambiguous_deviations,
            failure_message=(
                "All deviations must be fully classified. "
                "ambiguous_count must be 0 before remediation can proceed."
            ),
        ),
    ],
)
```

And `deviations_to_findings()` would parse the comma-separated `routing_fix_roadmap`
field instead of a nested YAML structure.

---

## 13. Open Questions Resolved

| OQ | Question | Resolution |
|----|----------|------------|
| OQ-1 | Should deviation-analysis accept AMBIGUOUS at lower severity? | No. AMBIGUOUS means the classifier cannot decide. The pipeline should halt for human review, not guess. No `--accept-ambiguous` flag in v5. |
| OQ-2 | How does `--resume` interact with new steps? | Covered in Section 8. spec-fidelity STANDARD always passes on resume (correct: diagnostic). deviation-analysis STRICT is the natural resume checkpoint. |
| OQ-3 | Remediation cycle bound? | 2 attempts maximum. `remediation_attempts` counter in `.roadmap-state.json`. Terminal halt with manual-fix instructions after exhaustion. |
| OQ-4 | Certify semantic check? | Yes. `_certified_is_true` added to `CERTIFY_GATE`. Pre-existing gap, critical for SLIP flow. |
| OQ-5 | Should annotate-deviations receive extraction? | No. The whole point is to avoid F-1 information loss. Annotator reads the spec file directly. |
| OQ-6 | Blast radius depth configurable? | Not in v5. Fixed to import chains, type contracts, and interface surface. Configurable depth is a v6 consideration. |
| OQ-7 | spec-deviations.md as living artifact? | Regenerated on each pipeline run (no incremental update). `--resume` skips it only if its gate already passes. Cost is acceptable (300s, same as other steps). |

### Open Questions Deferred to Implementation

| OQ | Question | Notes |
|----|----------|-------|
| OQ-8 | Spec update recommendations: who executes `update_spec` routing? | Manual handoff in v5. `update_spec` routing is informational only. Automated spec update step is a v6 consideration. |
| OQ-9 | Finding.status lifecycle: add VERIFICATION_FAILED? | Deferred. In v5, certify updates Finding status back to `FAILED` when verification fails. A `VERIFICATION_FAILED` terminal status may be added in a future version if the distinction proves useful. |
| OQ-10 | Skill protocol alignment? | Phase 1 and Phase 2 deliverables include SKILL.md updates for Wave sub-step definitions. Specific content defined during implementation. |

---

## 14. Backward Compatibility

### 14.1 Finding Model

The `deviation_class` field defaults to `""` (empty string). Existing code that
constructs `Finding` objects without this field will work unchanged. The
`__post_init__` validation only checks `deviation_class` when it is non-empty.

### 14.2 Spec-Fidelity Gate

The downgrade from STRICT to STANDARD is a relaxation, not a tightening. Any
pipeline run that passed the STRICT gate will also pass the STANDARD gate.
Existing state files with `spec-fidelity: PASS` remain valid.

### 14.3 Certify Gate

The new `certified_true` semantic check is a tightening. A certification report
that previously passed (because `certified: false` was not checked) will now
fail. This is intentional -- the previous behavior was a bug. Any legitimate
certification with `certified: true` is unaffected.

### 14.4 Resume State

Existing `.roadmap-state.json` files without `remediation_attempts` are handled
gracefully: `state.get("remediate", {}).get("remediation_attempts", 0)` returns
0, allowing the full budget of 2 attempts.

---

## 15. Success Criteria

### 15.1 Functional

| Criterion | Verification |
|-----------|-------------|
| SC-1: Pipeline processes the v2.24 spec without halting at fidelity | End-to-end test with v2.24 spec file |
| SC-2: Intentional deviations (D-02, D-04) are pre-approved and excluded from HIGH count | Inspect `spec-deviations.md` and `spec-fidelity.md` output |
| SC-3: SLIPs (DEV-002, DEV-003) are classified and routed to remediation | Inspect `deviation-analysis.md` routing table |
| SC-4: Remediation targets only SLIPs, does not modify intentional deviations | Diff `roadmap.md` before and after remediation |
| SC-5: Certify blocks on `certified: false` | Unit test for `_certified_is_true` semantic check |
| SC-6: Pipeline halts after 2 failed remediation attempts with manual-fix instructions | Integration test with mock failing certify |

### 15.2 Non-Functional

| Criterion | Target |
|-----------|--------|
| NFR-1: No new executor primitives | Zero new classes in `pipeline/models.py` or `pipeline/executor.py` |
| NFR-2: Pipeline cost increase per run | Less than 600s additional (2 steps x 300s) |
| NFR-3: Backward compatibility | Existing Finding consumers unaffected |
| NFR-4: Resume correctness | `--resume` correctly skips completed steps, re-runs failed steps |
