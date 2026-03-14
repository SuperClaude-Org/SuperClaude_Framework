---
title: "v2.25 Spec-Panel Amendments Tasklist"
source: spec-panel-review (2026-03-14)
target: v2.25-spec-merged.md
compliance: strict
strategy: systematic
estimated_tasks: 28
fr_range: "FR-078 – FR-094"
nfr_range: "NFR-020 – NFR-024"
priority_breakdown:
  critical: 4
  major: 17
  minor: 7
executor: sc:task-unified
---

# v2.25 Spec-Panel Amendments — Implementation Tasklist

All tasks operate on:
- **Target file**: `.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md`
- **FR/NFR registry**: `.dev/releases/backlog/2.25-roadmap-v5/fr-registry.md`

## Critical Prerequisites

**This tasklist MUST be executed AFTER all three prior tasklists complete:**
1. `tasklist-immediate-amendments.md` — Immediate amendments (FR-056–FR-059, NFR-011–NFR-012)
2. Short-term amendments tasklist (FR-060–FR-069, NFR-013–NFR-015)
3. `tasklist-longterm-amendments.md` — Long-term amendments (FR-070–FR-077, NFR-016–NFR-019)

**FR/NFR baseline**: The highest canonical number after all prior tasklists is FR-077 / NFR-019.
All new FRs in this tasklist begin at **FR-078**. All new NFRs begin at **NFR-020**.

**Section number baseline**: After prior tasklists complete:
- §3 has subsections 3.1–3.6 (3.1 = Artifact Taxonomy inserted by immediate A-1/B-1)
- §8 has subsections 8.1–8.9 (8.7 = Spec-Patch Retirement, 8.8 = Retry Budget Summary,
  8.9 = Spec-Patch Cycle Dormancy — see longterm tasklist)
- §14 has subsections 14.1–14.9

Before starting, verify section structure with:
```bash
grep "^## \|^### " .dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md | head -80
```

---

## Findings Map

The following table maps every spec-panel finding to its assigned task(s).

| Finding | Expert | Severity | Task(s) |
|---------|--------|----------|---------|
| `SCOPE_ADDITION` class has no routing path defined | Wiegers + Adzic | CRITICAL | GROUP A (A-1) |
| Step 7 vs Step 10 classification divergence: no cross-check | Whittaker | CRITICAL | GROUP B (B-1) |
| Empty `ambiguous_count` produces misleading gate error | Whittaker | CRITICAL | GROUP C (C-1) |
| `slip_count > len(routing_fix_roadmap)` mismatch undetected | Whittaker | CRITICAL | GROUP D (D-1) |
| Silent-skip of unmatched DEV-NNN IDs in `deviations_to_findings()` | Fowler | MAJOR | GROUP E (E-1) |
| Whitespace token `" DEV-003"` silently drops a SLIP from routing | Whittaker | MAJOR | GROUP F (F-1) |
| `--resume` after remediate: undefined execution queue re `annotate-deviations` | Whittaker | MAJOR | GROUP G (G-1) |
| `total_annotated == sum(counts)` invariant unvalidated | Whittaker | MAJOR | GROUP H (H-1, H-2) |
| `update_spec` routing has no operator-visible action | Cockburn | MAJOR | GROUP I (I-1) |
| `deviations_to_findings()` imports `_parse_frontmatter` via private function | Fowler | MAJOR | GROUP J (J-1) |
| `_check_annotate_deviations_freshness()` has no test spec | Crispin | MAJOR | GROUP K (K-1) |
| DEV-NNN routing IDs not validated against fidelity report | Hohpe | MAJOR | GROUP L (L-1) |
| `.roadmap-state.json` corruption resets `remediation_attempts` budget | Hightower | MAJOR | GROUP M (M-1) |
| Annotator producing `total_annotated: 0` on spec with real deviations: silent failure | Adzic | MAJOR | GROUP N (N-1) |
| `INTENTIONAL_PREFERENCE` sub-routing uses informal terminology | Wiegers | MAJOR | GROUP O (O-1) |
| Schema version field missing from new artifact formats | Newman | MAJOR | GROUP P (P-1) |
| Negative `remediation_attempts` bypasses budget check | Whittaker | MAJOR | GROUP Q (Q-1) |
| AMBIGUOUS deviation human review process not specified | Gregory | MINOR | GROUP R (R-1) |
| Observability requirements missing for new pipeline steps | Nygard | MAJOR | GROUP S (S-1) |
| Artifact cleanup policy not specified for fresh runs | Hightower | MINOR | GROUP T (T-1) |
| `INTENTIONAL_PREFERENCE` → fidelity treatment unspecified (cross-ref table) | Wiegers | CRITICAL | GROUP A (A-1) |
| `_extract_fidelity_deviations()` / `_extract_deviation_classes()` behavior undefined | Fowler | MINOR | GROUP J (J-2) |
| Annotate-deviations TOCTOU after remediate | Nygard | MAJOR | GROUP G (G-1) |
| SC-1 test classification (manual vs automated) unclear | Crispin | MAJOR | GROUP U (U-1) |
| `_parse_routing_list()` module location unspecified | Newman | MINOR | GROUP J (J-1) |
| `_inject_roadmap_hash()` failure mode unspecified | Hohpe | MINOR | GROUP V (V-1) |
| `_print_terminal_halt()` exit code chain ambiguous | Nygard | MINOR | GROUP W (W-1) |
| Retaining `_high_severity_count_zero` without deprecation markers | Wiegers | MINOR | GROUP X (X-1) |

---

## GROUP A — Classification Cross-Reference Table (CRITICAL)

### TASK A-1: Insert §5.3a "Classification Mapping: annotate-deviations to deviation-analysis"

**Panel finding**: Wiegers CRITICAL (SCOPE_ADDITION routing gap) + Adzic MAJOR (no worked example
for SCOPE_ADDITION) + Wiegers CRITICAL (INTENTIONAL_PREFERENCE treatment in fidelity unspecified)

**Priority**: CRITICAL — blocks correct implementation of both annotate-deviations and
deviation-analysis agents. Without this table, an implementor cannot write a correct prompt
for either step. `SCOPE_ADDITION` deviations have no defined routing.

**FR/NFR**: FR-078 (new, §5.3a)

**Context**:
The spec defines a four-class taxonomy in annotate-deviations (§3.4):
- `INTENTIONAL_IMPROVEMENT` — debated, consensus, technically superior
- `INTENTIONAL_PREFERENCE` — debated, consensus, stylistic
- `SCOPE_ADDITION` — new element not in spec, debated
- `NOT_DISCUSSED` — no debate citation

The spec defines a four-class taxonomy in deviation-analysis (§5.3):
- `PRE_APPROVED` — already in spec-deviations.md as INTENTIONAL_IMPROVEMENT and verified
- `INTENTIONAL` — confirmed via direct debate search (not pre-approved)
- `SLIP` — not in debate at all
- `AMBIGUOUS` — partially discussed, unclear consensus

FR-007 says only `INTENTIONAL_IMPROVEMENT` is eligible for fidelity exclusion. FR-022 says
SLIPs and INTENTIONAL-preference route to `fix_roadmap`. But the full mapping between the two
classification systems — including `SCOPE_ADDITION` — is never specified.

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.3 Prompt Design: build_deviation_analysis_prompt()`.
After the prompt instructions summary (the numbered list ending with "Produce a remediation
routing table") and before the next subsection (`### 5.4`), insert the following new subsection:

```
### 5.3a Classification Mapping: `annotate-deviations` → `deviation-analysis`

**FR-078**: The `deviation-analysis` prompt SHALL use the following mapping table when
cross-referencing `spec-deviations.md` annotations against `spec-fidelity.md` findings.
This table is normative: it defines how each `annotate-deviations` classification class
translates into a `deviation-analysis` classification and routing decision.

| `spec-deviations.md` class | Fidelity treatment | `deviation-analysis` class | Routing |
|----------------------------|-------------------|---------------------------|---------|
| `INTENTIONAL_IMPROVEMENT` (valid citation verified by fidelity) | Excluded from HIGH/MEDIUM count | `PRE_APPROVED` | `no_action` |
| `INTENTIONAL_IMPROVEMENT` (citation invalid or unverified) | Re-flagged as HIGH by fidelity agent | `SLIP` (or `AMBIGUOUS` if partial) | `fix_roadmap` (or `human_review`) |
| `INTENTIONAL_PREFERENCE` | Counts normally in fidelity | `INTENTIONAL` (preference sub-class) | `fix_roadmap` |
| `SCOPE_ADDITION` | Counts normally in fidelity | `INTENTIONAL` (if debate citation confirmed) or `SLIP` (if no debate citation found) | `fix_roadmap` |
| `NOT_DISCUSSED` | Counts normally in fidelity | `SLIP` (if no debate found) or `AMBIGUOUS` (if partially discussed) | `fix_roadmap` or `human_review` |
| Not present in spec-deviations.md | Counts normally in fidelity | Classified from debate transcript alone | Per classification result |

**Clarification on `SCOPE_ADDITION`**: A `SCOPE_ADDITION` deviation is a roadmap element that
does not appear in the spec but was discussed in the debate. In `deviation-analysis`, the agent
MUST search the debate transcript for a citation. If a valid D-XX citation is found with
consensus, classify as `INTENTIONAL`. If no citation is found, classify as `SLIP`. A
`SCOPE_ADDITION` element that was discussed in the debate but never reached consensus is
classified as `AMBIGUOUS` and routed to `human_review`.

**Clarification on `INTENTIONAL_PREFERENCE`**: A deviation classified as `INTENTIONAL_PREFERENCE`
by `annotate-deviations` is a stylistic choice debated and resolved in the debate. The spec is
authoritative on style unless the debate reached explicit consensus to deviate. Therefore,
`INTENTIONAL_PREFERENCE` deviations are routed to `fix_roadmap` (the roadmap should conform to
the spec's style). The `INTENTIONAL` classification in `deviation-analysis` with
`(preference sub-class)` is the downstream signal that triggers the `fix_roadmap` routing (not
`update_spec`). The `update_spec` routing is reserved for `INTENTIONAL`-superior deviations
only — deviations where the roadmap is objectively better than the spec (not merely preferred).

**Sub-classification signal in `deviation-analysis.md`**: The agent SHOULD include a
`sub_class` column in the Deviation Classification table body (§5.4) to distinguish
`INTENTIONAL (preference)` from `INTENTIONAL (superior)`. This sub-class drives the
`fix_roadmap` vs. `update_spec` routing split described in FR-022. The `sub_class` column
is informational only; the routing fields in frontmatter are authoritative.
```

**Acceptance criteria**:
- `grep "FR-078" v2.25-spec-merged.md` returns exactly one match in §5.3a
- `grep "### 5.3a" v2.25-spec-merged.md` returns exactly one match
- `grep "SCOPE_ADDITION" v2.25-spec-merged.md` returns matches in §5.3a (routing defined)
- `grep "INTENTIONAL_PREFERENCE" v2.25-spec-merged.md` returns a match in §5.3a (routing defined)
- The table has exactly 6 rows covering all annotation classes including the "not present" fallback
- `grep "preference sub-class" v2.25-spec-merged.md` returns a match (sub-classification signal)

---

## GROUP B — Step 7/Step 10 Divergence Guard (CRITICAL)

### TASK B-1: Add FR-079 cross-validation requirement between annotate-deviations and deviation-analysis

**Panel finding**: Whittaker Divergence Attack (CRITICAL) — Step 7 classifies deviation X as
`INTENTIONAL_IMPROVEMENT`, fidelity verifies it, but Step 10 independently re-classifies it
as `SLIP` (e.g., debate transcript truncated in context). The gate passes (`ambiguous_count == 0`),
remediation receives X as a SLIP, and reverts an intentionally-chosen design. This is a silent
correctness failure with no detection.

**Priority**: CRITICAL

**FR/NFR**: FR-079 (new, §5.3)

**Context**:
The `deviation-analysis` agent in Step 10 independently re-classifies every HIGH and MEDIUM
deviation. It has access to `spec-deviations.md` and should use `PRE_APPROVED` for anything
already annotated as `INTENTIONAL_IMPROVEMENT` with a verified citation. But there is no gate
check that enforces this. If the agent ignores the pre-approved annotation (perhaps due to
context window issues or prompt ambiguity), the resulting `deviation-analysis.md` will have
a conflict: `spec-deviations.md` says `INTENTIONAL_IMPROVEMENT` for deviation X, but
`deviation-analysis.md` says `SLIP` for X and routes it to `fix_roadmap`. The gate only checks
`ambiguous_count == 0`, not whether the classification is consistent with pre-approved annotations.

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition`. Find the existing
`DEVIATION_ANALYSIS_GATE` definition and the three semantic checks. After the last existing
semantic check (`_routing_consistent_with_slip_count` — added by immediate tasklist), and
BEFORE the closing `]` of `semantic_checks=`, insert a fourth semantic check reference.
Then add the following FR and function definition after the gate block:

**Insert after the `DEVIATION_ANALYSIS_GATE` block** (the complete gate code block):

```
**FR-079**: A `_pre_approved_not_in_fix_roadmap()` semantic check function SHALL be added to
`gates.py`. The function:
1. Parses the frontmatter of `deviation-analysis.md` for `routing_fix_roadmap` (comma-separated)
2. Reads `spec-deviations.md` frontmatter path from `DEVIATION_ANALYSIS_STEP.inputs` (the
   `deviations_file` path) — OR accepts `spec_deviations_content` as an optional second argument
   for testability
3. Extracts every deviation ID classified as `PRE_APPROVED` in `deviation-analysis.md` body table
4. Returns `False` if any `PRE_APPROVED` ID appears in `routing_fix_roadmap`
5. Returns `True` if no `PRE_APPROVED` ID is in `routing_fix_roadmap` (or if there are no
   `PRE_APPROVED` IDs)
6. Fails closed: missing frontmatter, missing inputs, or parse errors return `False`

**Implementation note**: Because this check requires reading two files (the deviation-analysis
artifact being validated AND the spec-deviations artifact from a prior step), it cannot follow
the single-`content: str` function signature used by existing semantic checks. Two implementation
options are acceptable:

**Option A** (preferred): Make `_pre_approved_not_in_fix_roadmap()` a two-argument function
`(content: str, spec_deviations_content: str) -> bool`. `GateCriteria` must support an
`aux_inputs: list[Path] | None` field that the gate evaluator reads and passes as additional
positional arguments to the check function. If `aux_inputs` is not yet in `GateCriteria`, this
FR also requires adding it.

**Option B** (fallback): Implement the check purely from the `deviation-analysis.md` content
by requiring the agent to embed the `PRE_APPROVED` ID list in frontmatter as
`pre_approved_ids: DEV-001,DEV-005` (a new frontmatter field). The check then validates that
`routing_fix_roadmap` and `pre_approved_ids` have no intersection. This avoids multi-file
reads at the cost of an additional required frontmatter field.

The FR-079 implementation MUST specify which option is chosen before coding begins. Option B
is simpler and recommended if `GateCriteria.aux_inputs` does not already exist.

**If Option B is chosen**, add `pre_approved_ids` to `DEVIATION_ANALYSIS_GATE` required
frontmatter fields (amending the gate definition added by FR-057).
```

Also update the `DEVIATION_ANALYSIS_GATE` definition to reference this check as a fourth
`SemanticCheck`. The failure message SHALL be:
```
"PRE_APPROVED deviation ID(s) found in routing_fix_roadmap. A PRE_APPROVED deviation has
already been intentionally excluded from remediation. Re-run deviation-analysis or correct
the routing table manually. Affected IDs: {ids}."
```

**Acceptance criteria**:
- `grep "FR-079" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "_pre_approved_not_in_fix_roadmap" v2.25-spec-merged.md` returns a match in §5.5
- `grep "Option A\|Option B" v2.25-spec-merged.md` returns matches describing the two impl paths
- The `DEVIATION_ANALYSIS_GATE` `semantic_checks` list now references four checks

---

## GROUP C — Gate Error Message Correctness (CRITICAL)

### TASK C-1: Add FR-080 — gate check functions must distinguish parse errors from semantic failures

**Panel finding**: Whittaker Zero/Empty Attack (CRITICAL) — `ambiguous_count: ""` (empty string)
causes `int("")` → `ValueError`, check returns `False`, gate blocks with "All deviations must be
fully classified. ambiguous_count must be 0" — which is a misleading error because the real
problem is a malformed frontmatter field, not an unclassified deviation.

Same issue applies to `slip_count: ""` in `_routing_consistent_with_slip_count()`, which returns
`False` and triggers "slip_count > 0 but routing_fix_roadmap is empty" — again misleading, since
the actual count is unknown.

**Priority**: CRITICAL — incorrect error messages are operationally dangerous: they direct the
operator to investigate the wrong thing.

**FR/NFR**: FR-080 (new, §5.5)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition`. After the `DEVIATION_ANALYSIS_GATE`
definition block and its four semantic check specifications, insert:

```
**FR-080**: Semantic check functions in `gates.py` that parse integer fields SHALL distinguish
between "field is missing" (key absent from frontmatter), "field is malformed" (present but not
parseable as int), and "field has a failing value" (parseable int, but value fails the check).
Malformed fields SHALL produce a distinct error message that does NOT accuse the agent of an
incorrect classification decision.

The following amendments apply to existing check functions:

**`_no_ambiguous_deviations()` (amends FR-027 spec)**:
Replace the current single-path failure return `False` with three distinct paths:

```python
def _no_ambiguous_deviations(content: str) -> bool:
    fm = _parse_frontmatter(content)
    if fm is None:
        return False  # Structural failure -- frontmatter missing

    value = fm.get("ambiguous_count")
    if value is None:
        return False  # Field absent

    try:
        count = int(str(value).strip())
    except (ValueError, TypeError):
        # Field present but not a valid integer -- log as malformed
        _log.warning(
            "ambiguous_count value %r is not a valid integer in "
            "deviation-analysis.md frontmatter. Artifact may be malformed.",
            value,
        )
        return False

    if count < 0:
        _log.warning(
            "ambiguous_count value %r is negative in deviation-analysis.md. "
            "Expected 0 or positive integer.",
            count,
        )
        return False

    return count == 0
```

**`_routing_consistent_with_slip_count()` (amends FR-056 spec)**:
Apply the same three-path pattern. The malformed-field path SHALL log:
```
"slip_count value %r is not a valid integer in deviation-analysis.md frontmatter.
 Artifact may be malformed."
```
And return `False` without triggering the "routing_fix_roadmap is empty" message.

**Implementation note**: The gate failure messages in `SemanticCheck.failure_message` are
static strings shown on gate failure. They cannot adapt to the reason for `False`. The
WARNING log provides the distinguishing context to the operator. Implementors MUST ensure
that malformed-field cases produce the WARNING log before returning `False`.
```

**Acceptance criteria**:
- `grep "FR-080" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "malformed" v2.25-spec-merged.md` returns a match in the FR-080 context (malformed vs missing distinction)
- `grep "count < 0" v2.25-spec-merged.md` returns a match (negative value handling)
- The `_no_ambiguous_deviations()` body in §5.5 contains the three-path `int(str(value).strip())` pattern

---

## GROUP D — Routing Count vs. List Length Validation (CRITICAL)

### TASK D-1: Add FR-081 — validate `slip_count` equals the count of IDs in `routing_fix_roadmap`

**Panel finding**: Whittaker boundary table GAP — `slip_count: 5, routing_fix_roadmap: DEV-001`
passes `_routing_consistent_with_slip_count()` (routing is non-empty) but only one ID is routed
when five SLIPs should be. Four SLIPs are silently dropped with no detection.

**Priority**: CRITICAL

**FR/NFR**: FR-081 (new, §5.5)

**Context**:
FR-022 states: "SLIPs are always routed to fix_roadmap." FR-056 checks that `routing_fix_roadmap`
is non-empty when `slip_count > 0`. But neither check validates that `len(routing_fix_roadmap
tokens) == slip_count`. A `slip_count: 5` with only `routing_fix_roadmap: DEV-001` passes all
existing gates. Four SLIPs are never remediated.

Note: `total_analyzed == slip_count + pre_approved_count + intentional_count + ambiguous_count`
is also unvalidated — this is covered by the accumulation attack. This FR addresses only the
routing completeness for SLIPs specifically, which has direct correctness impact.

**What to do**:
In `v2.25-spec-merged.md`, locate §5.5. After the FR-080 block, insert:

```
**FR-081**: A `_slip_count_matches_routing()` semantic check function SHALL be added to
`gates.py`. The function:
1. Parses frontmatter of `deviation-analysis.md` for `slip_count` (int)
2. Parses `routing_fix_roadmap` field, splits on comma, strips whitespace, filters empty tokens
3. If `slip_count == 0`: return `True` (empty routing is correct)
4. If `slip_count > 0`: return `True` only if `len(routing_fix_roadmap_tokens) >= slip_count`
5. Fails closed: missing or unparseable `slip_count` returns `False`

**Rationale**: SLIPs that are counted but not routed are silently lost. This check is a
count-completeness gate: it verifies the routing list is at least as long as the SLIP count.
It does NOT verify that each SLIP ID is valid (that is FR-074's responsibility).

**Failure message**:
```
"slip_count is N but routing_fix_roadmap contains only M entries (M < N).
All SLIPs must appear in routing_fix_roadmap (FR-022).
Check deviation-analysis agent output for missing routing entries."
```

This check SHALL be registered as a fifth semantic check on `DEVIATION_ANALYSIS_GATE`, appended
after the four checks added by FR-056/FR-057 (two original), FR-079 (third), FR-079 appended
fourth. The order is: `no_ambiguous_deviations`, `validation_complete_true`,
`routing_consistent_with_slip_count`, `pre_approved_not_in_fix_roadmap`,
`slip_count_matches_routing`.

**Implementation note**: `len(tokens) >= slip_count` (not `==`) is intentional. It is possible
for the routing to contain IDs from both SLIP and INTENTIONAL-preference deviations. The count
may legitimately be higher than `slip_count` alone. A strict `==` check would produce false
positives. Downstream, FR-075 cross-checks total routing length against `total_analyzed`.
```

**Acceptance criteria**:
- `grep "FR-081" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "_slip_count_matches_routing" v2.25-spec-merged.md` returns a match in §5.5
- `grep "slip_count_matches_routing" v2.25-spec-merged.md` returns a match inside the DEVIATION_ANALYSIS_GATE semantic_checks list
- The DEVIATION_ANALYSIS_GATE now references five semantic checks in the correct order

---

## GROUP E — Silent-Skip Logging in `deviations_to_findings()` (MAJOR)

### TASK E-1: Add FR-082 — require WARNING log when a routing ID resolves to no fidelity deviation

**Panel finding**: Fowler MAJOR — `if dev is None: continue` silently discards a DEV-NNN ID
that was in `routing_fix_roadmap` but not found in the `spec-fidelity.md` deviation table.
This is a pipeline data consistency problem with no observable trace.

**Priority**: MAJOR — blocks reliable remediation; the operator has no way to know a SLIP was
silently dropped.

**FR/NFR**: FR-082 (new, §7.2 — amends the `deviations_to_findings()` code stub)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 7.2 Deviation-to-Finding Conversion`. Find the
`deviations_to_findings()` code stub. Locate the loop body:

```python
        if dev is None:
            continue
```

Replace with:

```python
        if dev is None:
            _log.warning(
                "Routing ID %r appears in routing_fix_roadmap of deviation-analysis.md "
                "but was not found in spec-fidelity.md deviation table. "
                "This ID will not be remediated. Possible causes: ID format mismatch, "
                "fidelity report truncation, or agent hallucinated ID. "
                "Verify spec-fidelity.md contains a deviation with this ID.",
                dev_id,
            )
            continue
```

Precede this change with:

```
**FR-082**: In `deviations_to_findings()`, when a routing ID from `routing_fix_roadmap` is
not found in the `spec-fidelity.md` deviation table, the function SHALL emit a `WARNING`
log at `logging.WARNING` level before continuing. The log MUST include the unresolved ID,
identify both source artifacts, and suggest diagnostic steps. A silent `continue` without
logging is not permitted.

The WARNING level (not ERROR or CRITICAL) is correct: the function still produces a valid
(if incomplete) findings list. The caller decides whether incomplete findings is an
acceptable state. The WARNING provides observability without halting the pipeline.
```

**Acceptance criteria**:
- `grep "FR-082" v2.25-spec-merged.md` returns exactly one match in §7.2
- `grep "WARNING" v2.25-spec-merged.md` returns a match in the `deviations_to_findings()` context
- `grep "not found in spec-fidelity" v2.25-spec-merged.md` returns a match (log message spec)
- The `continue` in the loop body is preceded by a `_log.warning()` call with the four required elements

---

## GROUP F — Routing Token Whitespace Normalization (MAJOR)

### TASK F-1: Add FR-083 — `_parse_routing_list()` must strip whitespace before regex validation

**Panel finding**: Whittaker Sentinel Collision Attack (MAJOR) — agent produces
`routing_fix_roadmap: DEV-002, DEV-003` (space after comma). `_parse_routing_list()` splits
on comma, produces token `" DEV-003"` (leading space). Token fails `r'^DEV-\d+$'` regex per
FR-075. Token is silently skipped. SLIP DEV-003 is never remediated.

**Priority**: MAJOR

**FR/NFR**: FR-083 (new, §7.2a — amends FR-061 `_parse_routing_list()` spec)

**Context**:
FR-061 specifies `_parse_routing_list()`. FR-075 specifies token validation against `^DEV-\d+$`.
Neither explicitly specifies that whitespace is stripped BEFORE regex validation. The omission
allows a leading/trailing-space token to fail regex validation and be silently dropped.

**What to do**:
In `v2.25-spec-merged.md`, locate `### 7.2a Helper Function Specifications` (inserted by the
short-term tasklist). Find the `FR-061` block for `_parse_routing_list()`. In the parsing rules
list, find rule 3 ("Split the value on `,`..."). Replace it with:

```
3. Split the value on `,`. **Strip leading and trailing whitespace from each token immediately
   after splitting, before any other processing.** This normalization MUST occur before the
   empty-token filter and before the regex validation. The agent may produce `DEV-002, DEV-003`
   (with a space after the comma) and the parser MUST handle this correctly by producing tokens
   `["DEV-002", "DEV-003"]`.
```

Then add a new FR immediately after the FR-061 block:

```
**FR-083**: The `_parse_routing_list()` function SHALL normalize routing tokens by stripping
whitespace (both `str.strip()` and `str.lstrip()` / `str.rstrip()`) from each token
BEFORE applying the regex filter `r'^DEV-\d+$'` (FR-074/FR-075). A token that is a valid
`DEV-NNN` ID with surrounding whitespace SHALL be treated as valid after normalization.

This normalization applies to ALL four routing fields:
`routing_fix_roadmap`, `routing_update_spec`, `routing_no_action`, `routing_human_review`.

**Rationale**: LLM agents frequently produce comma-separated lists with spaces after the
comma (`DEV-002, DEV-003`). The spec must not silently drop valid IDs due to formatting
conventions that differ between agents. Whitespace normalization is a correctness requirement,
not a best-practice suggestion.
```

**Acceptance criteria**:
- `grep "FR-083" v2.25-spec-merged.md` returns exactly one match in §7.2a
- `grep "strip.*before.*regex\|before.*regex.*strip\|normali" v2.25-spec-merged.md` returns a match in §7.2a context (normalization before regex)
- `grep "DEV-002, DEV-003" v2.25-spec-merged.md` returns a match (the canonical example of the failure case)

---

## GROUP G — Resume After Remediate: Execution Queue Specification (MAJOR)

### TASK G-1: Add FR-084 / NFR-020 — define resume execution queue when `annotate-deviations` staleness is detected after `remediate` has run

**Panel finding**: Whittaker Sequence Attack (MAJOR) + Nygard TOCTOU (MAJOR) —
When `--resume` is invoked after `remediate` has modified `roadmap.md`, the freshness check
(FR-071) finds `roadmap_hash` stale, re-adds `annotate-deviations` to the execution queue.
But the spec does not define which subsequent steps also re-run. Does `spec-fidelity` re-run?
Does `deviation-analysis` re-run? Without this spec, the implementation will diverge from intent.

**Priority**: MAJOR

**FR/NFR**: FR-084 (new, §8.2 — amends the resume logic section)
         NFR-020 (new, §14 — adds a backward-compat note)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.2 Impact of v5 Changes on Resume`. After the existing
FR-071 block (the `_check_annotate_deviations_freshness()` function and NFR-016 fail-closed spec),
insert:

```
**FR-084**: When `_check_annotate_deviations_freshness()` returns `False` and
`annotate-deviations` is re-added to the execution queue during `--resume`, `_apply_resume()`
SHALL also reset the gate-pass state for ALL steps that depend on `annotate-deviations` output.
Specifically:

1. `spec-fidelity` MUST re-run (it consumes `spec-deviations.md` as input per FR-018)
2. `deviation-analysis` MUST re-run (it consumes `spec-deviations.md` as input per FR-019)
3. `remediate` and `certify` are NOT automatically re-run by freshness detection alone —
   they are gated by whether `deviation-analysis` produces a new failing output

**Implementation**: `_apply_resume()` currently iterates steps in order and re-runs from the
first failing gate. Since `annotate-deviations` precedes both `spec-fidelity` and
`deviation-analysis` in pipeline order (FR-002), re-adding `annotate-deviations` to the queue
means the `_apply_resume()` loop will naturally encounter `spec-fidelity` and
`deviation-analysis` as subsequent unverified steps and re-run them. No special handling
is needed UNLESS `_apply_resume()` uses cached gate results from the state file. In that case,
the state file entries for `spec-fidelity` and `deviation-analysis` MUST be invalidated when
`annotate-deviations` is force-re-queued.

**FR-084 scope**: If `_apply_resume()` does NOT cache gate results in `.roadmap-state.json`
(i.e., it re-evaluates gates fresh on each `--resume` invocation), this FR is satisfied
automatically by pipeline order. If it DOES cache results, the implementation MUST clear the
`spec-fidelity` and `deviation-analysis` cached gate results when freshness detection forces
`annotate-deviations` to re-run.

Implementors MUST verify the caching behavior of `_apply_resume()` before implementing FR-084.
The correct behavior in both cases is that `spec-fidelity` and `deviation-analysis` re-run
whenever `annotate-deviations` re-runs due to stale `roadmap_hash`.
```

Then in `§14` (Backward Compatibility), after the last existing NFR in §14 (NFR-019 or the
last section number after prior tasklists — verify with grep), add:

```
### 14.10 Resume Behavior After Remediate Modifies `roadmap.md`

**NFR-020**: When `--resume` is invoked after `remediate` has already run and modified
`roadmap.md`, the `roadmap_hash` stored in `spec-deviations.md` will not match the current
`roadmap.md`. This is EXPECTED behavior. The v2.25 design intentionally re-runs
`annotate-deviations` in this scenario (FR-071, FR-084) to ensure that the deviation
classification reflects the remediated roadmap.

Operators who observe `annotate-deviations` re-running after `remediate` should not treat
this as an error. It indicates that `remediate` changed `roadmap.md` and the deviation
annotations need to be refreshed. The refreshed annotations may produce zero deviations
(all SLIPs fixed) or a reduced count (some SLIPs partially fixed), allowing the pipeline
to proceed through `deviation-analysis` → `certify`.

**This is not a TOCTOU vulnerability**: The design is intentional. `roadmap_hash` is
re-computed at resume time (not at annotation time) so that stale annotations are always
detected and refreshed.
```

**Acceptance criteria**:
- `grep "FR-084" v2.25-spec-merged.md` returns exactly one match in §8.2
- `grep "NFR-020" v2.25-spec-merged.md` returns exactly one match in §14.10
- `grep "### 14.10" v2.25-spec-merged.md` returns exactly one match
- `grep "spec-fidelity.*re-run\|re-run.*spec-fidelity" v2.25-spec-merged.md` returns a match in §8.2
- `grep "TOCTOU" v2.25-spec-merged.md` returns a match in §14.10

---

## GROUP H — Count Conservation Invariant Validation (MAJOR)

### TASK H-1: Add FR-085 — validate `total_annotated == sum(count fields)` in `ANNOTATE_DEVIATIONS_GATE`

**Panel finding**: Whittaker Accumulation Attack (MAJOR) — `ANNOTATE_DEVIATIONS_GATE` validates
frontmatter fields are present but does NOT validate that `total_annotated` equals the sum of
the four count fields. An agent can write `total_annotated: 5` with counts summing to 3 and the
gate passes. Downstream steps receive incorrect aggregate counts.

**Priority**: MAJOR

**FR/NFR**: FR-085 (new, §3.6 gate definition — note: §3.6 = former §3.5, renumbered by immediate tasklist)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 3.6 Gate Definition` (formerly §3.5). After the
`FR-070` block (added by long-term tasklist, which adds `roadmap_hash` to required fields),
insert:

```
**FR-085**: A `_total_annotated_consistent()` semantic check function SHALL be added to
`gates.py`. The function:
1. Parses frontmatter of `spec-deviations.md`
2. Reads `total_annotated`, `intentional_improvement_count`, `intentional_preference_count`,
   `scope_addition_count`, `not_discussed_count` as integers
3. Returns `True` if `total_annotated == sum(intentional_improvement_count,
   intentional_preference_count, scope_addition_count, not_discussed_count)`
4. Returns `False` if any field is missing, unparseable, or if the sum does not match
5. Fails closed: any parse error returns `False` with a `WARNING` log identifying which field
   failed to parse

```python
def _total_annotated_consistent(content: str) -> bool:
    """Validate total_annotated equals sum of classification count fields.

    Count conservation invariant: every annotated deviation must be classified
    into exactly one of the four categories. total_annotated must equal the sum.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False
    try:
        total = int(fm.get("total_annotated", ""))
        ii = int(fm.get("intentional_improvement_count", ""))
        ip = int(fm.get("intentional_preference_count", ""))
        sa = int(fm.get("scope_addition_count", ""))
        nd = int(fm.get("not_discussed_count", ""))
    except (ValueError, TypeError):
        _log.warning(
            "spec-deviations.md count field(s) are not valid integers. "
            "Cannot validate total_annotated consistency."
        )
        return False
    return total == (ii + ip + sa + nd)
```

This check SHALL be registered as a STANDARD semantic check on `ANNOTATE_DEVIATIONS_GATE`.
It is STANDARD (not STRICT) because `annotate-deviations` is a diagnostic step with `retry_limit=0`.
Blocking on count inconsistency at STANDARD tier means the pipeline halts at a STANDARD gate
failure, which produces a structural error (not a semantic block), consistent with FR-013.

**Failure message**: "total_annotated does not equal the sum of classification counts
(intentional_improvement + intentional_preference + scope_addition + not_discussed). The
annotation artifact may be incomplete. Re-run annotate-deviations."
```

Then add the `_total_annotated_consistent` check to the `ANNOTATE_DEVIATIONS_GATE` definition
(amending the gate to add `semantic_checks=[SemanticCheck(name="total_annotated_consistent",
check_fn=_total_annotated_consistent, failure_message="...")]`).

**Acceptance criteria**:
- `grep "FR-085" v2.25-spec-merged.md` returns exactly one match in §3.6
- `grep "_total_annotated_consistent" v2.25-spec-merged.md` returns the function definition and a reference in ANNOTATE_DEVIATIONS_GATE
- `grep "ANNOTATE_DEVIATIONS_GATE" v2.25-spec-merged.md | wc -l` returns ≥2 (definition + semantic_checks reference)

---

### TASK H-2: Add FR-086 — validate `total_analyzed == sum(count fields)` in `DEVIATION_ANALYSIS_GATE`

**Panel finding**: Same accumulation attack applies to `deviation-analysis.md`:
`total_analyzed` frontmatter field is never verified against the sum of
`pre_approved_count + intentional_count + slip_count + ambiguous_count`.

**Priority**: MAJOR

**FR/NFR**: FR-086 (new, §5.5)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition`. After the FR-081 block, insert:

```
**FR-086**: A `_total_analyzed_consistent()` semantic check function SHALL be added to
`gates.py`. The function validates that `total_analyzed == sum(pre_approved_count,
intentional_count, slip_count, ambiguous_count)` in `deviation-analysis.md` frontmatter.
Implementation follows the same pattern as `_total_annotated_consistent()` (FR-085) with
the corresponding field names.

This check SHALL be registered as a STRICT semantic check on `DEVIATION_ANALYSIS_GATE`,
appended as the sixth semantic check (after `slip_count_matches_routing` from FR-081).

**Failure message**: "total_analyzed does not equal the sum of classification counts
(pre_approved + intentional + slip + ambiguous). The deviation analysis artifact may be
incomplete or incorrectly aggregated. Re-run deviation-analysis."
```

**Acceptance criteria**:
- `grep "FR-086" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "_total_analyzed_consistent" v2.25-spec-merged.md` returns a match in §5.5
- The DEVIATION_ANALYSIS_GATE semantic_checks list now references six checks

---

## GROUP I — `update_spec` Operator Experience (MAJOR)

### TASK I-1: Add FR-087 — `update_spec` routing must produce human-readable remediation guidance and CLI output

**Panel finding**: Cockburn MAJOR — `update_spec` routing is "informational only" (OQ-8) but
the spec does not specify how the operator discovers this recommendation, what format it appears
in, or what guidance they receive to update the spec.

**Priority**: MAJOR

**FR/NFR**: FR-087 (new, §5.3 — amends deviation-analysis prompt requirements and §13 OQ-8)

**What to do**:
In `v2.25-spec-merged.md`, locate `## 13. Open Questions Resolved`. Find the `OQ-8` row in
the "Open Questions Deferred to Implementation" table. Replace the OQ-8 row content with:

```
| OQ-8 | Spec update recommendations: who executes `update_spec` routing? | **FR-087**: Manual handoff in v5. The `deviation-analysis.md` body MUST include a `## Spec Update Recommendations` section for every deviation routed to `update_spec`. Each entry SHALL contain: (1) the deviation ID, (2) the spec section that should be updated, (3) the change rationale (why the roadmap version is superior), and (4) the exact text or structural change recommended. The CLI output on successful pipeline completion MUST print a summary when `routing_update_spec` is non-empty: "Note: N deviation(s) suggest spec updates. Review deviation-analysis.md §Spec Update Recommendations for details." Automated spec update step deferred to v6. |
```

Also in `### 5.3 Prompt Design: build_deviation_analysis_prompt()`, in the "Produce a remediation
routing table" instruction (the last numbered item in the prompt instructions summary), add:

```
**FR-087**: For every deviation routed to `update_spec`, the body of `deviation-analysis.md`
SHALL include a `## Spec Update Recommendations` subsection with per-deviation entries in the
following format:

### Update Recommendation: {deviation_id}

**Spec Section**: {section reference in the original spec file}
**Current Spec Text**: {quote the relevant spec text that should change}
**Recommended Change**: {describe the change needed to align spec with roadmap}
**Rationale**: {why the roadmap design is superior to the current spec language}

This section is consumed by human operators performing manual spec updates. The pipeline
does not read or validate this section — it is for operator use only.
```

**Acceptance criteria**:
- `grep "FR-087" v2.25-spec-merged.md` returns matches in both §5.3 prompt spec and §13 OQ-8
- `grep "Spec Update Recommendations" v2.25-spec-merged.md` returns a match in §5.3
- `grep "OQ-8" v2.25-spec-merged.md` references FR-087 and describes the CLI output requirement
- `grep "Note: N deviation" v2.25-spec-merged.md` returns a match (CLI output summary template)

---

## GROUP J — Module Dependency and Private Function Usage (MAJOR + MINOR)

### TASK J-1: Add NFR-021 — module dependency hierarchy and `_parse_frontmatter` visibility

**Panel finding**: Fowler MAJOR — `deviations_to_findings()` in `remediate.py` imports
`_parse_frontmatter` from `gates.py` as a private function (the `_` prefix indicates
internal-only use). Cross-module imports of private functions violate interface segregation.
Newman MINOR — `_parse_routing_list()` module location unspecified.

**Priority**: MAJOR

**FR/NFR**: NFR-021 (new, §7.2 — module organization note)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 7.2 Deviation-to-Finding Conversion`. Before the
`deviations_to_findings()` code stub (before `def deviations_to_findings(...)`), insert:

```
**NFR-021**: The `_parse_frontmatter()` function in `gates.py` SHALL be made public (renamed
to `parse_frontmatter()`, removing the underscore prefix) before v2.25 implementation begins.
All internal callers in `gates.py` SHALL be updated to use the new name. External callers
(`deviations_to_findings()` in `remediate.py`, `_check_annotate_deviations_freshness()` in
`executor.py`, and any function in `executor.py` that reads frontmatter) SHALL import and use
`parse_frontmatter()` from `gates.py` directly.

**Module dependency hierarchy** (authoritative for v2.25 roadmap module graph):
```
models.py          (no imports from other roadmap modules)
gates.py           (imports from models.py only)
prompts.py         (imports from models.py, may use gates.parse_frontmatter for validation)
fidelity.py        (imports from models.py, gates.py)
remediate.py       (imports from models.py, gates.py, fidelity.py)
remediate_prompts.py (imports from models.py only)
executor.py        (imports from all of the above)
spec_patch.py      (imports from models.py, gates.py)
```

Circular imports SHALL NOT exist between any two modules in this hierarchy.

**`_parse_routing_list()` module location**: This function SHALL reside in `remediate.py`
(alongside `deviations_to_findings()` which is its primary caller). It is NOT a gate validation
function and does not belong in `gates.py`. If `_parse_routing_list()` is also needed by the
gate semantic check `_routing_ids_valid()` (FR-074 in `gates.py`), then `_parse_routing_list()`
SHALL be extracted to a new module `src/superclaude/cli/roadmap/parsing.py` which both
`remediate.py` and `gates.py` may import without creating a cycle.
```

Update the `deviations_to_findings()` code stub to use `parse_frontmatter` (without underscore):

Find `from .gates import _parse_frontmatter` in the code stub and replace with:
```python
from .gates import parse_frontmatter
```

And all internal uses of `_parse_frontmatter(...)` in the stub to `parse_frontmatter(...)`.

**Acceptance criteria**:
- `grep "NFR-021" v2.25-spec-merged.md` returns exactly one match in §7.2
- `grep "parse_frontmatter()" v2.25-spec-merged.md` (without underscore) returns matches in §7.2 context
- `grep "parsing.py" v2.25-spec-merged.md` returns a match (extraction option for shared use)
- The module dependency hierarchy table is present with 7 module rows
- `grep "_parse_routing_list.*module\|module.*_parse_routing_list" v2.25-spec-merged.md` returns a match specifying the location

---

### TASK J-2: Add note to FR-060/FR-062 on behavior when agent body format is non-conformant

**Panel finding**: Fowler MINOR — `_extract_fidelity_deviations()` and `_extract_deviation_classes()`
must parse markdown tables but their error behavior when the table is missing or malformed is
underspecified beyond "returns `{}`".

**Priority**: MINOR

**FR/NFR**: Amends FR-060 (§7.2a) and FR-062 (§7.2a) with error behavior detail

**What to do**:
In `v2.25-spec-merged.md`, locate `### 7.2a Helper Function Specifications`. Find the FR-060
block for `_extract_fidelity_deviations()`. In the parsing rules list, after rule 6 ("If no
header row matching the pattern is found, the function returns `{}`"), add:

```
7. If the function returns `{}` due to a missing header row, it SHALL emit a `WARNING` log
   at `logging.WARNING` level stating: "spec-fidelity.md body contains no deviation table
   matching the expected header pattern. deviations_to_findings() will return an empty list.
   Verify that the spec-fidelity agent produced a '## Deviations Found' section with the
   required 6-column table header (FR-016a)."
8. If the function is called with content that has zero non-frontmatter lines (body is empty),
   it SHALL return `{}` with the WARNING log from rule 7.
```

Find the FR-062 block for `_extract_deviation_classes()`. After its parsing rules, add:

```
7. If the function returns `{}` due to a missing classification table, it SHALL emit a
   `WARNING` log stating: "deviation-analysis.md body contains no classification table
   matching the expected header pattern. PRE_APPROVED/SLIP/INTENTIONAL sub-classification
   will default to 'SLIP' for all routed IDs in deviations_to_findings(). Verify that the
   deviation-analysis agent produced a 'Deviation Classification' table."
```

**Acceptance criteria**:
- `grep "rule 7\|rule 8" v2.25-spec-merged.md` (contextual) is present in §7.2a for both FR-060 and FR-062
- `grep "FR-016a" v2.25-spec-merged.md` returns a match in FR-060's rule 7 (connecting the prompt requirement to the parser)
- Both helper function specs explicitly define their WARNING log content on empty/missing table

---

## GROUP K — Test Specification for `_check_annotate_deviations_freshness()` (MAJOR)

### TASK K-1: Add test specification for `_check_annotate_deviations_freshness()` to test file inventory

**Panel finding**: Crispin MAJOR — `_check_annotate_deviations_freshness()` (FR-071) is not in
the test file inventory (§11). It has multiple failure paths and drives a critical resume decision.

**Priority**: MAJOR

**FR/NFR**: Amends §11 (Test Files Modified table) — no new FR number, structural addition

**What to do**:
In `v2.25-spec-merged.md`, locate `## 11. Affected Files Summary`. Find the `### Test Files Modified`
table. Add a new row:

```
| `tests/roadmap/test_executor.py` | 3 | `_check_annotate_deviations_freshness()` freshness check; see test specification below |
```

After the test files table, insert a new subsection:

```
### 11.6 Required Test Cases: `_check_annotate_deviations_freshness()`

The following test cases are REQUIRED for FR-071 (NFR-016) compliance. All cases must be
present in `tests/roadmap/test_executor.py`:

| Test Case | Input State | Expected Result |
|-----------|-------------|-----------------|
| `spec-deviations.md` missing | File does not exist | `False` |
| `spec-deviations.md` exists, frontmatter missing | No `---` delimiters | `False` |
| `roadmap_hash` field absent | Frontmatter has no `roadmap_hash` key | `False` |
| `roadmap_hash` field is empty string | `roadmap_hash: ""` | `False` |
| `roadmap.md` missing | File does not exist | `False` |
| Hash matches | `roadmap_hash` == SHA-256(`roadmap.md`) | `True` |
| Hash mismatch | `roadmap_hash` != SHA-256(`roadmap.md`) | `False` |
| `roadmap.md` read raises `PermissionError` | File unreadable | `False` (NFR-016 fail-closed) |
| `spec-deviations.md` read raises `OSError` | File unreadable mid-read | `False` (NFR-016 fail-closed) |

All nine test cases cover the fail-closed behavior specified in NFR-016. The test suite MUST
NOT use `pytest.raises` to expect exceptions from `_check_annotate_deviations_freshness()` —
the function MUST return `False` in all error cases, never raise.
```

**Acceptance criteria**:
- `grep "### 11.6" v2.25-spec-merged.md` returns exactly one match
- `grep "_check_annotate_deviations_freshness" v2.25-spec-merged.md | wc -l` returns ≥3 (test table + §8.2 FR-071 + §11.6 header)
- The test case table has exactly 9 rows covering all 9 specified paths
- `grep "pytest.raises" v2.25-spec-merged.md` in the §11.6 context contains the instruction NOT to use it

---

## GROUP L — Cross-Reference Validation of Routing IDs Against Fidelity Report (MAJOR)

### TASK L-1: Add FR-088 — amend FR-074 to validate routing IDs exist in fidelity report

**Panel finding**: Hohpe MAJOR — `_routing_ids_valid()` (FR-074) validates token format
(`^DEV-\d+$`) but does NOT validate that each ID actually exists in `spec-fidelity.md`.
A `deviation-analysis.md` that references `DEV-999` (non-existent) passes the gate. The
downstream `deviations_to_findings()` silently skips it (now logged per FR-082, but no gate
blocks).

**Priority**: MAJOR

**FR/NFR**: FR-088 (new, §5.5 — extends FR-074)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition`. Find the FR-074 block for
`_routing_ids_valid()`. After that block, insert:

```
**FR-088**: The `_routing_ids_valid()` function (FR-074) SHALL be extended to optionally
accept a `spec_fidelity_content: str | None = None` second argument. When provided, the
function SHALL additionally validate that every non-empty token in each routing field
is present as a deviation ID in the `spec_fidelity_content` deviation table (parsed by
`_extract_fidelity_deviations()` from FR-060).

When `spec_fidelity_content` is `None` (backward-compatible default), the function performs
only format validation (the FR-074 behavior). When provided, it performs both format and
existence validation.

**Gate integration**: `DEVIATION_ANALYSIS_GATE` SHALL pass `spec-fidelity.md` content as
`aux_inputs` to `_routing_ids_valid()` when `GateCriteria.aux_inputs` is supported (see
FR-079 Option A). If `aux_inputs` is not yet supported, this extension is deferred to the
same implementation milestone as FR-079 Option A.

**Failure message (extended)**:
"Routing ID(s) {ids} appear in routing_fix_roadmap but are not present in spec-fidelity.md.
These IDs cannot be remediated. Possible cause: deviation-analysis agent fabricated deviation
IDs not produced by spec-fidelity agent. Verify deviation-analysis.md routing table against
spec-fidelity.md deviation IDs."

**Severity**: This extended check produces a STRICT gate failure when it fires. An ID that
does not exist in the fidelity report is an artifact consistency error — remediation would
silently no-op for that ID (FR-082 logs a WARNING but the pipeline continues). The STRICT
gate failure here provides a hard block before that silent skip occurs.
```

**Acceptance criteria**:
- `grep "FR-088" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "spec_fidelity_content" v2.25-spec-merged.md` returns a match in §5.5 (new parameter)
- `grep "aux_inputs" v2.25-spec-merged.md` returns matches in both FR-079 and FR-088 contexts (shared concept)
- `grep "fabricated deviation IDs" v2.25-spec-merged.md` returns a match (failure message spec)

---

## GROUP M — State File Corruption Resistance (MAJOR)

### TASK M-1: Add NFR-022 — `.roadmap-state.json` must be written atomically

**Panel finding**: Hightower MAJOR — corrupt `.roadmap-state.json` (truncated write, filesystem
error) causes `read_state()` to return `None`, which causes `_check_remediation_budget()` to
return `True` (treating corrupt = fresh budget). This violates NFR-018 (max 3 total attempts).

**Priority**: MAJOR

**FR/NFR**: NFR-022 (new, §14 — adds a new backward-compat / operational note)

**What to do**:
In `v2.25-spec-merged.md`, locate the last subsection in `## 14. Backward Compatibility`
(§14.9 after prior tasklists complete, or §14.10 if FR-084/NFR-020 added §14.10 in GROUP G).
After that last §14.x subsection, insert a new one (§14.11 if §14.10 was added, or §14.10 if
§14.9 was last):

```
### 14.11 State File Integrity and Atomic Writes

**NFR-022**: `.roadmap-state.json` SHALL be written atomically on every `_save_state()` call.
The write pattern SHALL use the same `.tmp` + `os.replace()` approach specified for
`_inject_roadmap_hash()` in FR-055:

```python
def _save_state(config: RoadmapConfig, ...) -> None:
    state_file = config.output_dir / ".roadmap-state.json"
    tmp_file = state_file.with_suffix(".json.tmp")
    import json
    tmp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(tmp_file, state_file)  # atomic on POSIX; best-effort on Windows
```

**Rationale**: A non-atomic write (write directly to `.roadmap-state.json`) leaves a window
where a filesystem error can produce a truncated or zero-byte file. `read_state()` returns
`None` on parse failure. `_check_remediation_budget()` treats `None` as "no state, fresh
budget" and returns `True`. This allows a third (or fourth, or nth) remediation attempt
beyond the NFR-018 bound of 3.

**NFR-022 scope**: Atomic writes are REQUIRED for `.roadmap-state.json`. They are ALSO
REQUIRED for `spec-deviations.md` (already specified in FR-055 via `_inject_roadmap_hash()`).
No other roadmap output files require atomic writes (they are produced by subprocesses, not
the executor).

**Windows note**: `os.replace()` is atomic on POSIX systems. On Windows, it may not be
atomic if the target file is locked. This is an accepted limitation for the v2.25 CLI tool
which targets POSIX-primary environments. Windows-specific atomic write behavior is deferred
to a future release.
```

**Acceptance criteria**:
- `grep "NFR-022" v2.25-spec-merged.md` returns exactly one match in §14.11
- `grep "atomic" v2.25-spec-merged.md | wc -l` returns ≥3 (FR-055, FR-055 impl, NFR-022)
- `grep "os.replace" v2.25-spec-merged.md` returns a match in §14.11 code block (the atomic write pattern)
- `grep "fresh budget" v2.25-spec-merged.md` returns a match in §14.11 (rationale for why non-atomic is a bug)

---

## GROUP N — Silent Annotator Failure Scenario (MAJOR)

### TASK N-1: Add scenario to §9.1 composition table: "Annotator returns zero annotations on spec with deviations"

**Panel finding**: Adzic MAJOR — the composition table (§9.1) covers "No deviations at all"
(`total_annotated: 0`) but not the failure case where the annotator incorrectly returns
`total_annotated: 0` when real deviations exist.

**Priority**: MAJOR

**FR/NFR**: FR-089 (new, §9.1 — adds a new row to the composition table and a mitigation spec)

**What to do**:
In `v2.25-spec-merged.md`, locate `## 9. Interaction Analysis: How Scopes Compose`,
`### 9.1 Composition Table`. Find the composition table. Add a new row after "No deviations at all":

```
| Annotator produces zero annotations incorrectly | `total_annotated: 0` (incorrect) | All deviations count as HIGH (no pre-approved context) | All unmet HIGH deviations become SLIPs or AMBIGUOUS via debate search | Fixes all SLIPs that were not annotated | Degraded (no prevention benefit) but functionally recovers |
```

Then, after the composition table, insert a new subsection:

```
### 9.3 Annotator Failure Mode: Zero Annotations on Non-Empty Spec

**FR-089**: A scenario where `annotate-deviations` produces `total_annotated: 0` when the
spec/roadmap have known deviations is a functional failure of Scope 2 (prevention). The
system SHALL degrade gracefully: Scope 1 (recovery via `deviation-analysis`) provides a
backstop that classifies deviations independently from the debate transcript.

However, this failure mode is undetectable at the gate level: `ANNOTATE_DEVIATIONS_GATE`
accepts `total_annotated: 0` as valid (there may genuinely be no deviations). The gate
`FR-085` (`_total_annotated_consistent`) validates count arithmetic but not that the count
is non-zero.

**Detection mechanism** (informational, not a gate check): After `annotate-deviations`
completes and before `spec-fidelity` runs, the executor SHOULD log an INFO message:
"annotate-deviations produced N annotations for spec vs. roadmap comparison." If N == 0,
the message SHOULD add: "Zero annotations found. If deviations are expected, verify that
the annotate-deviations agent read the spec file correctly. Check that spec_file path is
resolvable at step execution time." This log is advisory only — it does not block.

**Operator action**: If a pipeline run produces `total_annotated: 0` unexpectedly, the
operator should:
1. Inspect `spec-deviations.md` to confirm `total_annotated` is indeed 0
2. Inspect the annotate-deviations subprocess log for errors
3. Verify the spec file path passed to the step is the correct full spec (not the extraction)
4. Re-run with `--resume` after confirming the spec file is accessible — if the annotator
   was failing due to a transient context issue, retry may succeed
```

**Acceptance criteria**:
- `grep "FR-089" v2.25-spec-merged.md` returns exactly one match in §9.3
- `grep "### 9.3" v2.25-spec-merged.md` returns exactly one match
- The §9.1 composition table contains the new "Annotator produces zero annotations incorrectly" row
- `grep "Zero annotations found" v2.25-spec-merged.md` returns a match (INFO log template)

---

## GROUP O — Formalize `INTENTIONAL_PREFERENCE` Sub-Routing Terminology (MAJOR)

### TASK O-1: Add FR-090 — replace informal "INTENTIONAL-superior" / "INTENTIONAL-preference" with formal routing signal

**Panel finding**: Wiegers MAJOR — FR-022 uses informal terms "INTENTIONAL-superior" and
"INTENTIONAL-preference" that do not map to any formal enum or frontmatter field. The routing
split between `fix_roadmap` and `update_spec` depends on a sub-classification that is never
formally specified.

**Priority**: MAJOR

**FR/NFR**: FR-090 (new, §5.3 — amends FR-022 routing specification)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.3 Prompt Design: build_deviation_analysis_prompt()`.
Find the "Remediation routing table" section. After the four bullet points defining the routing
lists, insert:

```
**FR-090**: The `deviation-analysis` output format SHALL use a `routing_intent` sub-field to
distinguish `INTENTIONAL (superior)` from `INTENTIONAL (preference)` deviations in the body
classification table. The allowed values for `routing_intent` are:

| `routing_intent` value | Routing | Meaning |
|------------------------|---------|---------|
| `superior` | `update_spec` | Roadmap design is objectively better than spec; spec should be updated |
| `preference` | `fix_roadmap` | Roadmap made a stylistic choice the spec does not mandate; roadmap should match spec |
| (not applicable) | `no_action` or `fix_roadmap` | For PRE_APPROVED and SLIP classifications; `routing_intent` is omitted or empty |

The `routing_intent` column SHALL appear in the Deviation Classification table in the body
of `deviation-analysis.md` (amending the table in §5.4 to add this column). It is
informational only and does not appear in frontmatter.

The `deviation-analysis` prompt SHALL instruct the agent that `routing_intent: superior`
requires explicit justification: the agent must state why the roadmap design is objectively
superior (not merely preferred) before assigning `update_spec` routing. Without explicit
justification, the agent SHALL default to `routing_intent: preference` (which routes to
`fix_roadmap`). This default prevents spec drift from undocumented preference decisions.
```

Also amend the body format table in `### 5.4 Output Format: deviation-analysis.md`. Find the
classification table header:
```
| ID | Original Severity | Classification | Debate Ref | Routing |
```
And add a `Routing Intent` column:
```
| ID | Original Severity | Classification | Debate Ref | Routing | Routing Intent |
```

**Acceptance criteria**:
- `grep "FR-090" v2.25-spec-merged.md` returns exactly one match in §5.3
- `grep "routing_intent" v2.25-spec-merged.md` returns matches in §5.3 and §5.4 (table header)
- `grep "superior.*preference\|preference.*superior" v2.25-spec-merged.md` returns a match
- `grep "default.*preference" v2.25-spec-merged.md` returns a match (default to preference)
- The §5.4 deviation classification table header contains "Routing Intent" column

---

## GROUP P — Schema Version Field for New Artifacts (MAJOR)

### TASK P-1: Add NFR-023 — add `schema_version` field to `spec-deviations.md` and `deviation-analysis.md`

**Panel finding**: Newman MAJOR — no schema version field in either new artifact format.
v2.26 cannot evolve these formats without breaking v2.25 readers.

**Priority**: MAJOR

**FR/NFR**: NFR-023 (new, §3.5 output format and §5.4 output format)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 3.5 Output Format: spec-deviations.md` (now §3.5 after
renumbering — formerly §3.4, renumbered by immediate tasklist). Find the YAML frontmatter
example block:

```yaml
---
total_annotated: 5
intentional_improvement_count: 2
...
---
```

Add `schema_version: "2.25"` as the FIRST field in the frontmatter:

```yaml
---
schema_version: "2.25"
total_annotated: 5
...
---
```

Then add to `ANNOTATE_DEVIATIONS_GATE` required frontmatter fields (amending FR-013 gate
definition): add `"schema_version"` to the `required_frontmatter_fields` list.

Similarly, in `### 5.4 Output Format: deviation-analysis.md`, find the frontmatter example
and add `schema_version: "2.25"` as the first field. Add `"schema_version"` to
`DEVIATION_ANALYSIS_GATE` required frontmatter fields.

Precede these changes with:

```
**NFR-023**: Both `spec-deviations.md` and `deviation-analysis.md` SHALL include a
`schema_version` field in their YAML frontmatter. The value for v2.25 artifacts is `"2.25"`.
This field enables future schema readers to detect version mismatches and handle them
gracefully. The `annotate-deviations` prompt SHALL instruct the agent to write
`schema_version: "2.25"` as the first frontmatter field. The `deviation-analysis` prompt
SHALL do the same.

Future versions that change the frontmatter schema SHALL increment this version. A `--resume`
invocation that encounters an artifact with `schema_version` mismatch (e.g., "2.24" artifact
in a v2.25 pipeline run) SHOULD log a WARNING but SHALL NOT block (resume behavior on schema
mismatch is undefined in v2.25 and deferred to v2.26).
```

**Acceptance criteria**:
- `grep "NFR-023" v2.25-spec-merged.md` returns exactly one match
- `grep "schema_version" v2.25-spec-merged.md` returns matches in §3.5 frontmatter example, §5.4 frontmatter example, ANNOTATE_DEVIATIONS_GATE fields, and DEVIATION_ANALYSIS_GATE fields (≥4 matches)
- `grep '"2.25"' v2.25-spec-merged.md` returns matches in both frontmatter examples

---

## GROUP Q — Negative `remediation_attempts` Bypasses Budget (MAJOR)

### TASK Q-1: Add constraint to FR-072 — `remediation_attempts` must be non-negative

**Panel finding**: Whittaker boundary table GAP — `remediation_attempts: -1` causes
`-1 >= max_attempts(2)` to be `False`, so `_check_remediation_budget()` returns `True`
(budget available) for a negative value. This bypasses the budget cap.

**Priority**: MAJOR

**FR/NFR**: Amends FR-072 (§8.4 — the `_check_remediation_budget()` int coercion spec)

**What to do**:
In `v2.25-spec-merged.md`, locate the FR-072 block in `### 8.4 Remediation Cycle Bounding`.
After the existing coercion code block (the `try: int(raw) except...` block), add:

```
**FR-072 Amendment — Non-negative enforcement**: After coercing `raw` to `attempts` (int),
`_check_remediation_budget()` SHALL additionally check:

```python
if attempts < 0:
    _log.warning(
        "remediation_attempts value %r is negative in .roadmap-state.json. "
        "State file may be corrupt or externally modified. "
        "Treating as 0 (fresh budget) to prevent indefinite pipeline bypass.",
        raw,
    )
    attempts = 0
```

**Rationale**: A negative `remediation_attempts` value can only arise from external
modification or state file corruption. Treating it as 0 (fresh budget) is consistent
with the existing corrupt-value handling (FR-072 baseline: corrupt → treat as 0).
Using the raw negative value would allow `attempts >= max_attempts` to return `False`
indefinitely, silently bypassing the NFR-018 bound.
```

**Acceptance criteria**:
- `grep "attempts < 0" v2.25-spec-merged.md` returns a match in §8.4
- `grep "negative" v2.25-spec-merged.md` returns a match in the FR-072 context (negative value rationale)
- The FR-072 code block in §8.4 contains both the ValueError/TypeError handling AND the `< 0` check

---

## GROUP R — AMBIGUOUS Deviation Human Review Process (MINOR)

### TASK R-1: Add FR-091 — specify the operator process for resolving AMBIGUOUS deviations

**Panel finding**: Gregory MINOR — when `DEVIATION_ANALYSIS_GATE` blocks on `ambiguous_count > 0`,
the spec does not describe how the operator resolves the ambiguity. There is no command analogous
to `roadmap accept-spec-change` for AMBIGUOUS deviations.

**Priority**: MINOR (deferred to end of tasklist, but should be present before implementation)

**FR/NFR**: FR-091 (new, §8 — new subsection after the deviation-analysis step spec, before resume logic)

**What to do**:
In `v2.25-spec-merged.md`, locate the end of `## 5. New Step: deviation-analysis (Scope 1 -- Recovery)`
(before `## 6.`). Insert:

```
### 5.7 Operator Resolution of AMBIGUOUS Deviations

**FR-091**: When `DEVIATION_ANALYSIS_GATE` fails because `ambiguous_count > 0`, the pipeline
halts with a STRICT gate failure. The `AMBIGUOUS_ITEMS.md` report (FR-063/FR-064, written by
the shortterm amendments) provides per-item detail. The operator MUST take one of the following
actions for each AMBIGUOUS deviation before running `--resume`:

**Option 1: Reclassify as SLIP** (most common)
If the operator determines the deviation is a generation failure (not intentional):
1. Edit `deviation-analysis.md` body: change the `AMBIGUOUS` classification to `SLIP`
2. Add the deviation ID to `routing_fix_roadmap` in the frontmatter (comma-separated)
3. Decrement `ambiguous_count` by 1, increment `slip_count` by 1 in frontmatter
4. Set `validation_complete: true` if all deviations are now classified
5. Run: `superclaude roadmap certify --resume <spec_file>`

**Option 2: Reclassify as INTENTIONAL**
If the operator determines the deviation was debated and should be accepted:
1. Find or create a `dev-*-accepted-deviation.md` record for the deviation
2. Add the deviation ID to `spec-deviations.md` as `INTENTIONAL_IMPROVEMENT` with
   the correct D-XX debate citation (manual edit)
3. Edit `deviation-analysis.md` to classify the deviation as `PRE_APPROVED`
4. Add the ID to `routing_no_action` in frontmatter
5. Decrement `ambiguous_count` by 1, increment `pre_approved_count` by 1
6. Run: `superclaude roadmap certify --resume <spec_file>`

**Future CLI command (v2.26)**: A `roadmap resolve-ambiguity --id DEV-NNN --action slip|accept`
CLI command is deferred to v2.26. In v2.25, operator resolution is manual file editing per
the steps above.

**Gate re-evaluation**: After the operator edits `deviation-analysis.md` and runs `--resume`,
`_apply_resume()` evaluates `DEVIATION_ANALYSIS_GATE` against the edited file. If
`ambiguous_count == 0` and `validation_complete: true`, the gate passes and remediation
proceeds.
```

**Acceptance criteria**:
- `grep "FR-091" v2.25-spec-merged.md` returns exactly one match in §5.7
- `grep "### 5.7" v2.25-spec-merged.md` returns exactly one match
- `grep "Option 1\|Option 2" v2.25-spec-merged.md` returns matches in §5.7 (both resolution paths documented)
- `grep "resolve-ambiguity" v2.25-spec-merged.md` returns a match (v2.26 CLI command placeholder)

---

## GROUP S — Observability Requirements for New Pipeline Steps (MAJOR)

### TASK S-1: Add NFR-024 — new pipeline steps must emit structured timing and token metadata

**Panel finding**: Nygard MAJOR — no observability requirements for `annotate-deviations`
or `deviation-analysis`. NFR-002 sets a performance target but no measurement mechanism.

**Priority**: MAJOR

**FR/NFR**: NFR-024 (new, §15.2 Non-Functional — amends success criteria)

**What to do**:
In `v2.25-spec-merged.md`, locate `## 15. Success Criteria`, `### 15.2 Non-Functional`.
Add a new row to the non-functional criteria table:

```
| **NFR-024**: Step timing metadata | `_save_state()` records `started_at`, `completed_at`, and (if available) `token_count` for `annotate-deviations` and `deviation-analysis` in `.roadmap-state.json`, consistent with all other pipeline steps |
```

Then insert a brief note after the table:

```
**NFR-024 implementation note**: The `annotate-deviations` and `deviation-analysis` steps use
the same `Step` dataclass as all other pipeline steps. Timing metadata (`started_at`,
`completed_at`) is recorded by `_save_state()` using the `StepResult.started_at` and
`StepResult.completed_at` fields that are already set by `roadmap_run_step()` for all steps.
No new instrumentation is needed — NFR-024 is satisfied by confirming that `_save_state()`
handles the two new step IDs (`annotate-deviations`, `deviation-analysis`) the same way as
all existing steps. Token count is recorded if the subprocess execution result includes token
metadata; this is dependent on the subprocess API surface and is best-effort.
```

**Acceptance criteria**:
- `grep "NFR-024" v2.25-spec-merged.md` returns exactly one match in §15.2
- `grep "started_at.*completed_at\|annotate-deviations.*timing" v2.25-spec-merged.md` returns a match in §15.2
- The §15.2 table now has 5 rows (original 4 + NFR-024)

---

## GROUP T — Artifact Cleanup Policy (MINOR)

### TASK T-1: Add NFR specification for new artifact cleanup on fresh runs and gitignore guidance

**Panel finding**: Hightower MINOR — no cleanup policy for `spec-deviations.md` and
`deviation-analysis.md` on fresh (non-resume) pipeline runs.

**Priority**: MINOR

**FR/NFR**: Amends §7 (Remediation Flow) — adds operational note; no new FR

**What to do**:
In `v2.25-spec-merged.md`, locate `## 14. Backward Compatibility`. After the NFR-022 block
(§14.11 inserted by GROUP M), insert:

```
### 14.12 Output Directory Artifact Lifecycle

The following table specifies the lifecycle of all v2.25 artifacts in the pipeline output
directory (`config.output_dir`):

| Artifact | Fresh run behavior | `--resume` behavior | Retention |
|----------|-------------------|---------------------|-----------|
| `spec-deviations.md` | Regenerated (overwritten) | Skipped if `ANNOTATE_DEVIATIONS_GATE` passes AND hash fresh | Pipeline-run scoped; safe to delete between runs |
| `deviation-analysis.md` | Regenerated (overwritten) | Skipped if `DEVIATION_ANALYSIS_GATE` passes | Pipeline-run scoped; safe to delete between runs |
| `spec-fidelity.md` | Regenerated (overwritten) | Skipped if gate passes | Pipeline-run scoped |
| `.roadmap-state.json` | Created/reset | Read and updated | Must persist between `--resume` invocations; DO NOT delete |
| `roadmap.md` | Generated by merge step | Skipped if merge gate passes | Primary output; persist |

**Version control guidance**: Add the following patterns to `.gitignore` if the pipeline
output directory is tracked by git:
```
spec-deviations.md
deviation-analysis.md
spec-fidelity.md
.roadmap-state.json
```

These are pipeline-internal artifacts. Only `roadmap.md` (the final deliverable) should be
committed to version control. The state file `.roadmap-state.json` may be retained locally
for `--resume` purposes but should not be committed.

**Cleanup on fresh run**: A fresh pipeline run (without `--resume`) does NOT automatically
delete prior artifacts. Prior `spec-deviations.md` or `deviation-analysis.md` files are
overwritten by the new run. If a fresh run is interrupted before `annotate-deviations`
completes, a stale `spec-deviations.md` from the prior run may remain. Running `--resume`
after an interrupted fresh run will evaluate `roadmap_hash` freshness per FR-071 and
re-run `annotate-deviations` if stale.
```

**Acceptance criteria**:
- `grep "### 14.12" v2.25-spec-merged.md` returns exactly one match
- The lifecycle table has 5 rows covering all named artifacts
- `grep ".gitignore" v2.25-spec-merged.md` returns a match in §14.12
- `grep "primary output.*persist\|persist.*primary output" v2.25-spec-merged.md` returns a match (roadmap.md retention policy)

---

## GROUP U — SC-1 Test Classification (MAJOR)

### TASK U-1: Clarify SC-1 as a manual acceptance test; add automated substitute

**Panel finding**: Crispin MAJOR — FR-047 (SC-1) requires an "end-to-end test with v2.24 spec
file" but Phase 4 (§10) calls it manual validation. The spec is inconsistent: is SC-1 a CI
automated test or a manual acceptance gate?

**Priority**: MAJOR

**FR/NFR**: Amends §15.1 (FR-047 row) and §10 (Phase 4 description)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 15.1 Functional`. Find the FR-047 row. Replace the
Verification column text from "End-to-end test with v2.24 spec file" with:

```
Manual acceptance gate: Phase 4 end-to-end validation run with v2.24 spec file. For automated
CI, use the mock-subprocess integration test in `tests/roadmap/test_integration_v5_pipeline.py`
(new file, Phase 4 deliverable) that replays recorded subprocess outputs from the v2.24 pipeline
run without invoking Claude.
```

Then in `## 10. Implementation Phases`, `### Phase 4: Validation`, after the existing 5-item
validation checklist, add:

```
**Automated substitute for SC-1 (CI-friendly)**:

Phase 4 deliverables include a new integration test file:
- `tests/roadmap/test_integration_v5_pipeline.py`: Replays the v2.24 pipeline scenario using
  pre-recorded subprocess outputs (fixtures). Tests the full pipeline control flow (gate
  evaluations, step sequencing, resume behavior, routing) without invoking Claude subprocesses.

This automated test is NOT a full end-to-end test (it uses fixtures, not live Claude calls).
It is a regression guard that validates pipeline control flow correctness. SC-1 (the manual
run) must be performed at least once per release cycle to validate prompt quality in addition
to control flow.
```

Also add to the Phase 4 deliverables table:

```
| 6 | `tests/roadmap/test_integration_v5_pipeline.py` | New integration test file with v2.24 scenario fixtures |
```

**Acceptance criteria**:
- `grep "manual acceptance gate" v2.25-spec-merged.md` returns a match in §15.1 FR-047 row
- `grep "test_integration_v5_pipeline" v2.25-spec-merged.md` returns matches in §10 Phase 4 and §15.1
- `grep "mock-subprocess\|pre-recorded\|fixtures" v2.25-spec-merged.md` returns a match in §10
- The Phase 4 deliverables table has 6 rows

---

## GROUP V — `_inject_roadmap_hash()` Failure Mode (MINOR)

### TASK V-1: Add exception propagation spec for `_inject_roadmap_hash()`

**Panel finding**: Hohpe MINOR — if `_inject_roadmap_hash()` fails (disk full, permission
error), `spec-deviations.md` retains its pre-injection content (no `roadmap_hash` field).
FR-070 then causes the gate to fail with a confusing "missing frontmatter field" error.
The spec should state that `_inject_roadmap_hash()` raises on failure.

**Priority**: MINOR

**FR/NFR**: Amends FR-055 implementation spec in §3.3 (the `_inject_roadmap_hash()` definition)

**What to do**:
In `v2.25-spec-merged.md`, locate the FR-055 block in `### 3.3 Step Construction in _build_steps()`
(formerly §3.2, renumbered by immediate tasklist — adjust section reference based on actual
numbering after prior tasklists). Find `_inject_roadmap_hash(output_file, roadmap_path)`.
After the function description and atomic write explanation, add:

```
**Failure behavior**: If `_inject_roadmap_hash()` cannot write the updated frontmatter
(disk full, permission error, unexpected exception), it SHALL raise the exception to the
caller (`roadmap_run_step()`). The caller treats this as a step execution failure, not a
gate failure. The error message SHALL include the output file path and the specific OS error.

**Rationale**: Swallowing the exception and leaving `spec-deviations.md` without a
`roadmap_hash` field would cause `ANNOTATE_DEVIATIONS_GATE` to fail with "missing frontmatter
field: roadmap_hash" — a misleading error that suggests the agent failed rather than the
executor. A raised exception surfaces the real cause (write failure) immediately.
```

**Acceptance criteria**:
- `grep "SHALL raise the exception" v2.25-spec-merged.md` returns a match in the `_inject_roadmap_hash` context
- `grep "misleading error" v2.25-spec-merged.md` returns a match in the §3.3 rationale

---

## GROUP W — Exit Code Chain Specification (MINOR)

### TASK W-1: Clarify exit code chain for `_print_terminal_halt()` vs `sys.exit(1)`

**Panel finding**: Nygard MINOR — FR-044 specifies `sys.exit(1)` on budget exhaustion. FR-041
says `_check_remediation_budget()` returns `False`. The spec does not make the exit code chain
unambiguous: who calls `sys.exit(1)`?

**Priority**: MINOR

**FR/NFR**: Amends FR-041 / FR-044 in §8.4–8.6 — adds explicit exit code ownership note

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.4 Remediation Cycle Bounding`. Find the
`_check_remediation_budget()` function specification. After the function body, add:

```
**Exit code ownership**: `_check_remediation_budget()` returns `False` when the budget is
exhausted. It does NOT call `sys.exit(1)` directly — it delegates that to the caller.
The caller (`execute_roadmap()` or the post-pipeline remediate-certify flow) MUST call
`sys.exit(1)` when `_check_remediation_budget()` returns `False`. This separation allows
unit testing of `_check_remediation_budget()` without triggering `sys.exit`.

`_print_terminal_halt()` prints to `stderr` and returns normally. It does NOT call
`sys.exit(1)`. The calling sequence is always:

```python
if not _check_remediation_budget(config):
    _print_terminal_halt(config, state)
    sys.exit(1)
```

There is no scenario in v2.25 where `_print_terminal_halt()` is called without a subsequent
`sys.exit(1)` in the same control flow branch. However, the separation is intentional to
preserve testability.
```

**Acceptance criteria**:
- `grep "Exit code ownership" v2.25-spec-merged.md` returns a match in §8.4
- `grep "sys.exit.*_print_terminal_halt\|_print_terminal_halt.*sys.exit" v2.25-spec-merged.md` returns a match showing the calling sequence
- `grep "testability" v2.25-spec-merged.md` returns a match in the exit code ownership rationale

---

## GROUP X — Deprecation Markers for Retained Check Functions (MINOR)

### TASK X-1: Add deprecation markers to `_high_severity_count_zero` and `_tasklist_ready_consistent`

**Panel finding**: Wiegers MINOR — FR-015 retains `_high_severity_count_zero` and
`_tasklist_ready_consistent` "for potential future use" but does not mark them deprecated.
Implementors may accidentally reactivate them.

**Priority**: MINOR

**FR/NFR**: Amends FR-015 spec in §4.2 Gate Change

**What to do**:
In `v2.25-spec-merged.md`, locate `### 4.2 Gate Change`. Find the FR-015 block. After the
existing text about the functions being "retained in `gates.py`", add:

```
**Deprecation markers**: The retained functions SHALL include Python deprecation warnings
in their docstrings:

```python
def _high_severity_count_zero(content: str) -> bool:
    """[DEPRECATED v2.25] Previously registered in SPEC_FIDELITY_GATE (STRICT).
    De-registered in v2.25 (FR-015). The blocking decision has moved to
    DEVIATION_ANALYSIS_GATE via deviation-analysis step.
    Retained for potential use in manual validation scripts or future steps.
    DO NOT re-register in SPEC_FIDELITY_GATE without architectural review.
    """
    ...

def _tasklist_ready_consistent(content: str) -> bool:
    """[DEPRECATED v2.25] Previously registered in SPEC_FIDELITY_GATE (STRICT).
    De-registered in v2.25 (FR-015). The tasklist_ready field is now informational.
    Retained for potential future use.
    DO NOT re-register in SPEC_FIDELITY_GATE without architectural review.
    """
    ...
```

These docstring deprecation markers prevent implementors from accidentally reactivating
the checks. The functions remain callable for manual validation use (e.g., in debugging
scripts or one-off analysis). They are NOT deprecated in the "will be removed" sense —
they are deprecated in the "no longer in active use, do not add back without review" sense.
```

**Acceptance criteria**:
- `grep "DEPRECATED v2.25" v2.25-spec-merged.md` returns exactly 2 matches (one per function)
- `grep "DO NOT re-register" v2.25-spec-merged.md` returns 2 matches
- `grep "FR-015" v2.25-spec-merged.md` returns the amended block containing both deprecated docstrings

---

## GROUP Y — Final Validation (depends on all prior tasks)

### TASK Y-1: Full spec-panel amendments consistency verification

**Priority**: CRITICAL gate — must be last task executed

**What to do**:
Run all of the following verification commands against the modified `v2.25-spec-merged.md`.
Report any failures as blockers before marking Y-1 complete.

**New FR presence checks**:
```bash
cd .dev/releases/backlog/2.25-roadmap-v5/
grep -c "FR-078" v2.25-spec-merged.md   # ≥1 (§5.3a classification mapping table)
grep -c "FR-079" v2.25-spec-merged.md   # ≥1 (§5.5 pre-approved cross-check)
grep -c "FR-080" v2.25-spec-merged.md   # ≥1 (§5.5 malformed field error messages)
grep -c "FR-081" v2.25-spec-merged.md   # ≥1 (§5.5 slip_count vs routing length)
grep -c "FR-082" v2.25-spec-merged.md   # ≥1 (§7.2 silent-skip WARNING log)
grep -c "FR-083" v2.25-spec-merged.md   # ≥1 (§7.2a whitespace normalization)
grep -c "FR-084" v2.25-spec-merged.md   # ≥1 (§8.2 resume queue after remediate)
grep -c "FR-085" v2.25-spec-merged.md   # ≥1 (§3.6 total_annotated consistency)
grep -c "FR-086" v2.25-spec-merged.md   # ≥1 (§5.5 total_analyzed consistency)
grep -c "FR-087" v2.25-spec-merged.md   # ≥1 (§5.3/§13 update_spec operator guidance)
grep -c "FR-088" v2.25-spec-merged.md   # ≥1 (§5.5 routing ID existence validation)
grep -c "FR-089" v2.25-spec-merged.md   # ≥1 (§9.3 annotator zero-annotation scenario)
grep -c "FR-090" v2.25-spec-merged.md   # ≥1 (§5.3 routing_intent formalization)
grep -c "FR-091" v2.25-spec-merged.md   # ≥1 (§5.7 AMBIGUOUS resolution process)
```

**New NFR presence checks**:
```bash
grep -c "NFR-020" v2.25-spec-merged.md  # ≥1 (§14.10 resume after remediate)
grep -c "NFR-021" v2.25-spec-merged.md  # ≥1 (§7.2 module dependency hierarchy)
grep -c "NFR-022" v2.25-spec-merged.md  # ≥1 (§14.11 atomic state file writes)
grep -c "NFR-023" v2.25-spec-merged.md  # ≥1 (§3.5/§5.4 schema_version field)
grep -c "NFR-024" v2.25-spec-merged.md  # ≥1 (§15.2 step timing metadata)
```

**New section structure checks**:
```bash
grep "^### 5\.3a" v2.25-spec-merged.md                    # 1 match: Classification Mapping
grep "^### 5\.7" v2.25-spec-merged.md                     # 1 match: AMBIGUOUS Resolution
grep "^### 9\.3" v2.25-spec-merged.md                     # 1 match: Zero Annotations scenario
grep "^### 11\.6" v2.25-spec-merged.md                    # 1 match: test case spec
grep "^### 14\." v2.25-spec-merged.md | tail -5           # §14.10–14.12 present
```

**Key content spot-checks**:
```bash
grep "SCOPE_ADDITION" v2.25-spec-merged.md | wc -l        # ≥4 (§3.4, §5.3a table, §5.3a clarification, §9.1)
grep "routing_intent" v2.25-spec-merged.md | wc -l        # ≥3 (§5.3 FR-090, §5.4 table header, §5.3a)
grep "schema_version" v2.25-spec-merged.md | wc -l        # ≥4 (§3.5 example, §5.4 example, both gate fields)
grep "_total_annotated_consistent" v2.25-spec-merged.md   # ≥2 matches (function def + gate reference)
grep "_total_analyzed_consistent" v2.25-spec-merged.md    # ≥2 matches (function def + gate reference)
grep "_pre_approved_not_in_fix_roadmap" v2.25-spec-merged.md  # ≥2 (function def + gate check)
grep "_slip_count_matches_routing" v2.25-spec-merged.md   # ≥2 (function def + gate check)
grep "DEVIATION_ANALYSIS_GATE" v2.25-spec-merged.md | wc -l   # ≥4 (original def + 3 amendments)
grep "ANNOTATE_DEVIATIONS_GATE" v2.25-spec-merged.md | wc -l  # ≥3 (original def + 2 amendments)
```

**Guard Condition Boundary Table gap resolution checks**:
```bash
grep "malformed\|Malformed" v2.25-spec-merged.md | wc -l  # ≥2 (FR-080 malformed field handling)
grep "attempts < 0" v2.25-spec-merged.md                  # 1 match (FR-072 amendment, GROUP Q)
grep "parse_frontmatter" v2.25-spec-merged.md | wc -l     # ≥3 (NFR-021 public function rename)
```

**Acceptance criteria**: All checks produce the expected match count. Any `0` match on a
`≥1` check is a BLOCKER. Report exact grep output for any failing check.

---

## Execution Order Summary

```
GROUP A (A-1: classification mapping table — §5.3a) ──────────────────────────────────┐
GROUP B (B-1: Step 7/Step 10 cross-check — §5.5 FR-079) ─────────────────────────────┤
GROUP C (C-1: gate error message correctness — §5.5 FR-080) ─────────────────────────┤
GROUP D (D-1: slip_count vs routing length — §5.5 FR-081) ───────────────────────────┤
GROUP E (E-1: silent-skip WARNING log — §7.2 FR-082) ────────────────────────────────┤
GROUP F (F-1: whitespace normalization — §7.2a FR-083) ──────────────────────────────┤ parallel
GROUP G (G-1: resume queue after remediate — §8.2 FR-084 / §14.10 NFR-020) ─────────┤
GROUP H (H-1: total_annotated consistency — §3.6 FR-085) ────────────────────────────┤
GROUP H (H-2: total_analyzed consistency — §5.5 FR-086) ─────────────────────────────┤
GROUP I (I-1: update_spec operator guidance — §5.3 FR-087 / §13 OQ-8) ──────────────┤
GROUP J (J-1: module dependency + parse_frontmatter public — §7.2 NFR-021) ──────────┤
GROUP J (J-2: helper function error behavior — §7.2a) ───────────────────────────────┤
GROUP K (K-1: freshness check test spec — §11.6) ────────────────────────────────────┤
GROUP L (L-1: routing ID existence validation — §5.5 FR-088) ────────────────────────┤
GROUP M (M-1: atomic state file writes — §14.11 NFR-022) ────────────────────────────┤
GROUP N (N-1: zero-annotation scenario — §9.3 FR-089) ───────────────────────────────┤
GROUP O (O-1: routing_intent formalization — §5.3 FR-090) ───────────────────────────┤
GROUP P (P-1: schema_version field — §3.5/§5.4 NFR-023) ─────────────────────────────┤
GROUP Q (Q-1: negative remediation_attempts — §8.4 FR-072 amendment) ────────────────┤
GROUP R (R-1: AMBIGUOUS resolution process — §5.7 FR-091) ───────────────────────────┤
GROUP S (S-1: observability requirements — §15.2 NFR-024) ───────────────────────────┤
GROUP T (T-1: artifact cleanup policy — §14.12) ─────────────────────────────────────┤
GROUP U (U-1: SC-1 test classification — §15.1/§10) ─────────────────────────────────┤
GROUP V (V-1: inject_roadmap_hash failure — §3.3) ───────────────────────────────────┤
GROUP W (W-1: exit code chain — §8.4) ───────────────────────────────────────────────┤
GROUP X (X-1: deprecation markers — §4.2) ───────────────────────────────────────────┘

GROUP Y (Y-1: full validation) ← depends on ALL prior groups
```

All groups A through X have no mutual dependency and MAY be executed in parallel.
GROUP Y MUST be last.

---

## FR/NFR Canonical Numbers for This Tasklist

| Number | Type | Section | Summary |
|--------|------|---------|---------|
| FR-078 | FR | §5.3a (new) | Classification mapping table: annotate-deviations class → deviation-analysis class + routing |
| FR-079 | FR | §5.5 | `_pre_approved_not_in_fix_roadmap()` — prevents Step 7/Step 10 classification divergence |
| FR-080 | FR | §5.5 | Gate checks distinguish malformed-field from semantic-failure; WARNING log on malformed |
| FR-081 | FR | §5.5 | `_slip_count_matches_routing()` — validates `len(routing_ids) >= slip_count` |
| FR-082 | FR | §7.2 | `deviations_to_findings()` emits WARNING log when routing ID not found in fidelity report |
| FR-083 | FR | §7.2a | `_parse_routing_list()` strips whitespace from tokens before regex validation |
| FR-084 | FR | §8.2 | Resume queue after remediate: spec-fidelity and deviation-analysis must re-run when annotate-deviations is force-re-queued |
| FR-085 | FR | §3.6 | `_total_annotated_consistent()` — validates count conservation in `spec-deviations.md` |
| FR-086 | FR | §5.5 | `_total_analyzed_consistent()` — validates count conservation in `deviation-analysis.md` |
| FR-087 | FR | §5.3 / §13 | `update_spec` routing must include `## Spec Update Recommendations` section; CLI output summary |
| FR-088 | FR | §5.5 | `_routing_ids_valid()` extended to validate routing IDs exist in spec-fidelity.md deviation table |
| FR-089 | FR | §9.3 (new) | Zero-annotation silent failure scenario; INFO log; operator diagnostic steps |
| FR-090 | FR | §5.3 / §5.4 | `routing_intent` column formalizes INTENTIONAL sub-classification (superior vs. preference) |
| FR-091 | FR | §5.7 (new) | Operator process for resolving AMBIGUOUS deviations; two-option manual workflow; v2.26 CLI |
| NFR-020 | NFR | §14.10 (new) | Resume after remediate modifies roadmap.md: expected behavior, not TOCTOU vulnerability |
| NFR-021 | NFR | §7.2 | Module dependency hierarchy; `parse_frontmatter` made public; `_parse_routing_list` location |
| NFR-022 | NFR | §14.11 (new) | `.roadmap-state.json` atomic writes via `.tmp` + `os.replace()` |
| NFR-023 | NFR | §3.5 / §5.4 | `schema_version: "2.25"` field in all new artifact frontmatters |
| NFR-024 | NFR | §15.2 | New pipeline steps emit timing metadata to `.roadmap-state.json` consistent with existing steps |

Amended FRs (no new number, definition extended):
- FR-072 (§8.4): negative `remediation_attempts` treated as 0 (GROUP Q)
- FR-015 (§4.2): deprecated docstring markers for retained check functions (GROUP X)

---

## Notes for `sc:task-unified` Executor

- **Compliance tier**: STRICT for all groups. These are specification amendments to a STRICT-tier document.
- **Parallelization**: All groups A–X may run in parallel. GROUP Y must be last.
- **Target file**: All edits to `v2.25-spec-merged.md` only.
- **Source of truth for wording**: Exact language in each task INSTRUCTION block supersedes any
  paraphrase in this header. When inserting verbatim blocks, copy from the task body exactly.
- **Section number verification**: Before editing, always confirm the current section number
  using `grep "^### [0-9]" v2.25-spec-merged.md` — prior tasklists may have shifted numbers.
- **FR number collision check**: Before inserting any new FR, run
  `grep "FR-07[89]\|FR-08[0-9]\|FR-09[01]" v2.25-spec-merged.md` to confirm the numbers
  FR-078 through FR-091 are not already used. If any collision is found, reassign from the
  next available number after the current maximum.
