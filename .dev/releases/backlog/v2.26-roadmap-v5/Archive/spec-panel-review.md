---
title: "Spec Panel Review: v2.25 Deviation-Aware Pipeline"
type: spec-panel-review
spec_reviewed: adversarial/v2.25-spec-merged.md
review_date: 2026-03-13
mode: critique
focus: correctness,architecture,requirements
experts: wiegers,fowler,nygard,whittaker,crispin,adzic
overall_score: 7.4/10
requirements_quality: 6.8/10
architecture_clarity: 8.1/10
testability_score: 7.0/10
consistency_score: 6.5/10
findings_critical: 4
findings_major: 5
findings_minor: 3
---

# Spec Panel Review: v2.25 Deviation-Aware Pipeline

## Panel Composition

| Expert | Focus | Role |
|--------|-------|------|
| Karl Wiegers | Requirements quality, testability | Lead reviewer |
| Martin Fowler | Architecture, data flow, interfaces | Architecture reviewer |
| Michael Nygard | Reliability, failure modes, operational | Resilience reviewer |
| James Whittaker | Adversarial attack, boundary probing | Adversarial reviewer |
| Lisa Crispin | Testing strategy, acceptance criteria | Test reviewer |
| Gojko Adzic | Specification by example, concrete scenarios | Example reviewer |

---

## Executive Summary

The specification is architecturally sound. The two-scope design (prevention + recovery)
is well-reasoned, the incremental refactor avoids new executor primitives, and the
gate migration from spec-fidelity to deviation-analysis correctly resolves the v2.24
deadlock. The anti-laundering safeguards are thoughtful.

However, the spec has **four critical gaps** that will cause pipeline failures if
unaddressed, primarily around deviation set divergence between independent agents,
edge cases in the zero-deviation path, stale artifact handling on resume, and an
ambiguity in how pre-approved deviations flow through the fidelity report.

The spec also lacks formal FR-NNN / NFR-NNN identifiers, which the roadmap pipeline's
extraction step requires. A companion enumeration document is provided alongside
this review.

---

## CRITICAL Findings

### C-1: Deviation Set Divergence Between Annotate and Fidelity

**Expert**: Fowler (architecture) + Whittaker (sequence attack)

**Issue**: The `annotate-deviations` step (Section 3) and `spec-fidelity` step
(Section 4) are independent Claude subprocesses analyzing the same spec + roadmap
pair. They WILL find different deviation sets. Annotate may find 5 deviations;
fidelity may find 7 (two that annotate missed) or 4 (one annotate found that
fidelity didn't). This creates three problematic scenarios:

1. **Fidelity finds deviations not in spec-deviations.md**: These have no annotation.
   The deviation-analysis step handles this correctly (classifies unannotated deviations
   independently). No functional bug, but the spec should explicitly state this is
   expected behavior.

2. **Annotate finds deviations that fidelity misses**: These annotations exist in
   spec-deviations.md but have no corresponding DEV-NNN in the fidelity report.
   They are orphan annotations. The deviation-analysis step never processes them
   (it iterates over fidelity deviations, not annotations). This is fine but undocumented.

3. **Same deviation, different IDs**: Annotate calls it AD-003; fidelity calls it
   DEV-005. They describe the same deviation differently. The fidelity agent's
   verification step (Section 4.3, step 1-2) matches by citation, not by ID. But
   the deviation-analysis step matches by... what? The spec doesn't define the
   join key between spec-deviations.md entries and spec-fidelity.md entries.

**Severity**: CRITICAL -- scenario 3 can cause the fidelity agent to fail verification
on valid annotations because it cannot match them to its own deviation IDs.

**Recommendation**: Define an explicit matching strategy. Options:
- (a) Match by spec element reference (e.g., "Section 4.1 file structure") -- fuzzy
- (b) Match by debate citation (D-XX + round) -- precise but only works for INTENTIONAL
- (c) Have annotate-deviations use a stable ID scheme that fidelity can reference
- (d) Accept fuzzy matching and document that the fidelity agent should match by
  semantic similarity of the deviation description, not by ID

Option (d) is most pragmatic for v5. Add to Section 4.3: "The fidelity agent
matches pre-approved annotations to its own deviations by semantic content
similarity (same spec element, same roadmap difference), not by ID. An annotation
that cannot be matched to any fidelity deviation is ignored (orphan)."

---

### C-2: Zero-Annotation Edge Case

**Expert**: Whittaker (zero/empty attack)

**Issue**: When `spec-deviations.md` has `total_annotated: 0` (the annotate step
found zero deviations between spec and roadmap), what does the fidelity agent do?

Section 4.3 says the fidelity agent reads spec-deviations.md "first" and excludes
verified INTENTIONAL_IMPROVEMENT deviations. With zero annotations, there is nothing
to exclude. This is the correct behavior -- but the prompt must explicitly handle
this case. An ambiguous prompt could cause the fidelity agent to interpret
"zero annotations" as "everything is pre-approved" (catastrophic) rather than
"no pre-approved context exists" (correct).

**Severity**: CRITICAL -- prompt ambiguity in a zero-deviation scenario could
cause the fidelity agent to skip its entire analysis.

**Recommendation**: Add to the fidelity prompt instructions (Section 4.3):
"If spec-deviations.md contains `total_annotated: 0`, treat this as 'no
pre-approved deviations exist.' Perform your full analysis without any exclusions.
Do NOT interpret zero annotations as blanket approval."

---

### C-3: Stale spec-deviations.md on --resume After Remediation

**Expert**: Whittaker (sequence attack) + Nygard (failure modes)

**Issue**: Consider this sequence:
1. Pipeline runs through remediate (roadmap.md is modified to fix SLIPs)
2. Certify fails (fix was incomplete)
3. User runs `--resume`
4. `_apply_resume()` checks each step's output against its gate
5. `annotate-deviations` output (spec-deviations.md) exists and passes STANDARD gate
6. Pipeline skips annotate-deviations, resumes from certify
7. But roadmap.md has been modified by remediation -- spec-deviations.md is stale

The stale spec-deviations.md was produced from the pre-remediation roadmap. After
remediation, some deviations no longer exist (they were fixed) and new deviations
may have been introduced (remediation side effects). Fidelity reads stale
annotations and may:
- Exclude deviations that no longer exist (harmless but confusing)
- Miss new deviations introduced by remediation (if they happen to match a stale
  annotation)

**Severity**: CRITICAL -- remediation can introduce new deviations that bypass
annotation-based exclusion because the annotation file is stale.

**Recommendation**: Add a hash-based staleness check, similar to the existing
`_check_tasklist_hash_current()` pattern. When `--resume` evaluates the
`annotate-deviations` step, verify that `roadmap.md` has not been modified since
`spec-deviations.md` was produced. If modified (hash mismatch), force re-run of
annotate-deviations.

Implementation: Add `source_roadmap_hash` to spec-deviations.md frontmatter
(SHA-256 of roadmap.md at annotation time). The resume check compares this hash
against current roadmap.md content. This follows the established pattern from
`remediation-tasklist.md` (source_report_hash).

---

### C-4: Fidelity Report Handling of Pre-Approved Deviations

**Expert**: Wiegers (requirements clarity)

**Issue**: Section 4.3 says the fidelity agent should "EXCLUDE verified
INTENTIONAL_IMPROVEMENT deviations from HIGH/MEDIUM severity counts." But it
does not specify whether:

(a) The fidelity agent omits pre-approved deviations from the deviation TABLE
    entirely (they don't appear in the report at all), or
(b) The fidelity agent includes them in the table but at a reduced severity
    (e.g., INFO), or
(c) The fidelity agent includes them in the table at their original severity
    but adjusts only the frontmatter counts

This matters because deviation-analysis (Section 5) reads the fidelity report
to classify each deviation. If option (a), deviation-analysis cannot see
pre-approved deviations through the fidelity path -- it only sees them through
the direct spec-deviations.md path. If option (c), deviation-analysis sees them
as HIGH in the table but excluded from the count, creating an apparent inconsistency.

**Severity**: CRITICAL -- the deviation-analysis step's behavior depends on which
option the fidelity agent implements, and the spec leaves this ambiguous.

**Recommendation**: Specify option (b): "Pre-approved deviations with verified
citations SHOULD still appear in the deviation table with severity reclassified
to INFO and a note 'PRE_APPROVED (AD-NNN)'. Adjust frontmatter counts to reflect
the reclassified severity." This gives deviation-analysis full visibility while
keeping counts accurate.

---

## MAJOR Findings

### M-1: Bogus Citation Detection Specificity

**Expert**: Whittaker (sentinel collision attack)

**Issue**: Section 4.3 says the fidelity agent verifies that a cited D-XX reference
"exists" in the debate transcript. But a debate point D-05 might discuss topic A
(e.g., timeline units) while the annotator cites D-05 for a completely different
deviation B (e.g., module naming). The citation EXISTS but is IRRELEVANT to the
deviation being annotated.

The fidelity agent should verify not just that D-XX exists, but that D-XX's
content is RELEVANT to the specific deviation being annotated.

**Severity**: MAJOR -- allows a sophisticated annotator to launder SLIPs by
citing real but irrelevant debate references.

**Recommendation**: Strengthen Section 4.3 verification step 1: "Verify the cited
D-XX reference exists in the debate transcript AND that the debate discussion is
about the same spec element as the annotated deviation."

---

### M-2: DEVIATION_ANALYSIS_GATE Definition Inconsistency

**Expert**: Wiegers (consistency)

**Issue**: Section 5.5 defines `DEVIATION_ANALYSIS_GATE` with 7 required frontmatter
fields and 2 semantic checks. Section 12 (R-9 mitigation) defines an updated version
with 10 required frontmatter fields (adding 4 routing fields) and only 1 semantic
check (dropping `validation_complete_true`). These are contradictory.

**Severity**: MAJOR -- implementers will not know which definition is canonical.

**Recommendation**: Consolidate into one definition. The R-9 version (with routing
fields) is the more complete one. Place it in Section 5.5 as the canonical
definition. Remove the duplicate from Section 12 and replace with a reference:
"See Section 5.5 for the canonical gate definition."

Additionally, reconcile the semantic checks: Section 5.5 has both
`no_ambiguous_deviations` and `validation_complete_true`; R-9 version has only
`no_ambiguous_deviations`. The `validation_complete_true` check should be
preserved (it serves a distinct purpose: ensuring the analysis ran to completion).

---

### M-3: validation_complete Semantics Undefined

**Expert**: Nygard (failure modes)

**Issue**: Section 5.5 adds `_validation_complete_true` as a semantic check on
the deviation-analysis gate. But the spec never defines when the deviation-analysis
agent should set `validation_complete: false`. Is it:
- On timeout (partial analysis)?
- When the agent cannot read an input file?
- When the agent is uncertain about its own analysis?
- Never (always true unless crashed)?

**Severity**: MAJOR -- without defined semantics, LLM agents will inconsistently
set this field.

**Recommendation**: Add to Section 5.3 (prompt design): "Set `validation_complete: true`
when you have analyzed ALL HIGH and MEDIUM deviations in the fidelity report. Set
`validation_complete: false` only if you were unable to analyze one or more
deviations (e.g., missing input file, unreadable content, exceeded analysis capacity)."

---

### M-4: Diamond Dependency Data Consistency

**Expert**: Fowler (architecture)

**Issue**: `spec-deviations.md` feeds into both `spec-fidelity` and
`deviation-analysis`. But `deviation-analysis` also reads `spec-fidelity.md`
(which was itself influenced by spec-deviations.md). This creates a diamond
dependency where data about the same deviations flows through two paths:

```
spec-deviations.md ──> spec-fidelity ──> spec-fidelity.md ──> deviation-analysis
spec-deviations.md ──────────────────────────────────────────> deviation-analysis
```

If the fidelity agent's interpretation of a pre-approved deviation differs from
what deviation-analysis reads directly from spec-deviations.md, the classification
may be inconsistent.

**Severity**: MAJOR -- potential for conflicting signals in deviation-analysis.

**Recommendation**: Define a precedence rule in Section 5.3: "When information
about a deviation appears in both spec-deviations.md and spec-fidelity.md, the
fidelity report takes precedence (it represents verified analysis). Use
spec-deviations.md only for deviations NOT present in the fidelity report."

---

### M-5: Annotation Error Format Undefined

**Expert**: Wiegers (requirements completeness)

**Issue**: Section 4.3 says the fidelity agent "reports invalid annotations as
HIGH severity findings." But it doesn't define the format. Is an invalid
annotation reported as:
- A new deviation (DEV-NNN) with a special marker?
- A separate annotation-error section?
- An inline note on the pre-approved deviation?

The deviation-analysis step needs to distinguish between "this is a real spec
deviation rated HIGH" and "this is an annotation verification failure rated HIGH."

**Severity**: MAJOR -- deviation-analysis may misroute annotation errors as
spec SLIPs.

**Recommendation**: Define a convention: invalid annotations are reported as
standard deviations with a prefix: "DEV-NNN [ANNOTATION_INVALID]" in the
deviation description. The deviation-analysis prompt should recognize this prefix
and classify such entries as SLIP (the underlying deviation was not actually
pre-approved, so it must be treated as unapproved).

---

## MINOR Findings

### m-1: ANNOTATE_DEVIATIONS_GATE Arithmetic Consistency

**Expert**: Nygard (correctness)

`total_annotated` is a required frontmatter field but no semantic check verifies
that `total_annotated == intentional_improvement_count + intentional_preference_count
+ scope_addition_count + not_discussed_count`. An agent could report inconsistent
counts (total: 3, but individual counts sum to 5).

**Recommendation**: Add arithmetic consistency as a STANDARD-tier semantic check
(non-blocking warning in logs, not a gate failure).

---

### m-2: No Integration Test for Pre-Approval Path

**Expert**: Crispin (testing)

Section 15.1 has SC-2 (intentional deviations pre-approved) but no test that
exercises the full path: annotate → fidelity verification → deviation-analysis
confirmation. A test should verify the three-step handoff with a known-good
annotation and a known-bogus annotation in the same run.

**Recommendation**: Add SC-7: "Integration test with mixed annotations (1 valid
INTENTIONAL_IMPROVEMENT + 1 bogus citation) verifies valid is excluded and bogus
is re-flagged as HIGH."

---

### m-3: Concrete Scenario Missing for Remediate-Certify Retry

**Expert**: Adzic (specification by example)

Section 8.6 describes the retry flow abstractly. A concrete Given/When/Then
scenario would improve implementer understanding:

```
Given: deviation-analysis routes DEV-002 (missing models) to fix_roadmap
  And: remediate spawns agent, adds 2 of 3 models (partial fix)
  And: certify verifies DEV-002: FAIL (PortifyStepResult still missing)
When: user runs --resume (attempt 2)
Then: remediation_attempts incremented to 2
  And: remediate re-runs with DEV-002 only
  And: certify re-verifies
```

**Recommendation**: Add this scenario to Section 8.6 as a concrete example.

---

## Guard Condition Boundary Table

| Guard | Location | Input | Value | Result | Behavior | Status |
|-------|----------|-------|-------|--------|----------|--------|
| `_no_ambiguous_deviations` | Section 5.5 | Zero | `0` | True | Gate passes | OK |
| `_no_ambiguous_deviations` | Section 5.5 | One | `1` | False | Gate blocks | OK |
| `_no_ambiguous_deviations` | Section 5.5 | Missing | absent | False | Gate blocks | OK |
| `_no_ambiguous_deviations` | Section 5.5 | Non-integer | `"none"` | False | try/except catches | OK |
| `_no_ambiguous_deviations` | Section 5.5 | Negative | `-1` | False | -1 != 0 | OK |
| `_no_ambiguous_deviations` | Section 5.5 | Empty string | `""` | False | ValueError caught | OK |
| `_validation_complete_true` | Section 5.5 | True | `true` | True | Gate passes | OK |
| `_validation_complete_true` | Section 5.5 | False | `false` | False | Gate blocks | OK |
| `_validation_complete_true` | Section 5.5 | Missing | absent | False | Gate blocks | OK |
| `_validation_complete_true` | Section 5.5 | Empty | `""` | False | "" != "true" | OK |
| `_certified_is_true` | Section 6.2 | True | `true` | True | Gate passes | OK |
| `_certified_is_true` | Section 6.2 | False | `false` | False | Gate blocks | OK |
| `_certified_is_true` | Section 6.2 | Missing | absent | False | Gate blocks | OK |
| `_check_remediation_budget` | Section 8.4 | First run | `0` | True | Proceeds | OK |
| `_check_remediation_budget` | Section 8.4 | Second run | `1` | True | Proceeds | OK |
| `_check_remediation_budget` | Section 8.4 | Exhausted | `2` | False | Terminal halt | OK |
| `_check_remediation_budget` | Section 8.4 | Missing | absent | True | Defaults to 0 | OK |
| `ANNOTATE_GATE` frontmatter | Section 3.5 | All zero counts | `total: 0, all counts: 0` | True | Empty report passes | GAP |
| `ANNOTATE_GATE` frontmatter | Section 3.5 | Inconsistent sum | `total: 3, sum: 5` | True | No arithmetic check | GAP |

---

## Pipeline Dimensional Analysis

### Flow Diagram

```
[Spec + Roadmap] --> [Annotate: find N deviations] --> [N annotations in spec-deviations.md]
                                                              |
                                                              v
[Spec + Roadmap] --> [Fidelity: find M deviations] --> [M deviations in spec-fidelity.md]
                     (excludes K verified from N)       (M' = M - K in counts)
                                                              |
                                                              v
                     [Deviation-Analysis: classify M deviations]
                     (reads N annotations + M deviations)
                                                              |
                                                              v
                     [Routing: P to fix_roadmap, Q to no_action, R to human_review]
                     (P + Q + R = M)
                                                              |
                                                              v
                     [Remediate: P findings] --> [P agent invocations]
                                                              |
                                                              v
                     [Certify: verify P fixes]
```

### Dimensional Mismatch: N != M

**Finding**: CRITICAL. Annotate finds N deviations; fidelity independently finds M.
N and M may differ because they are independent Claude subprocesses with different
prompts analyzing the same documents. The spec implicitly assumes N >= M (every
fidelity deviation has an annotation), but this is not guaranteed.

**Concrete scenario**: Annotate finds 5 deviations (AD-001 through AD-005).
Fidelity finds 7 deviations (DEV-001 through DEV-007). DEV-006 and DEV-007 have
no annotations. Deviation-analysis classifies them correctly (NOT_DISCUSSED path
via debate search). Pipeline proceeds. No functional failure, but the spec should
document this as expected behavior.

**Reverse scenario**: Annotate finds 7 deviations; fidelity finds 5. Two
annotations are orphans (no matching DEV-NNN). Deviation-analysis never sees them.
If these orphans were INTENTIONAL_IMPROVEMENT, no harm (they're just unused
pre-approvals). If they were NOT_DISCUSSED, fidelity missed those deviations
entirely -- a silent gap.

**Recommendation**: Add to Section 9 (Interaction Analysis): "The annotate and
fidelity steps are independent analyses. Their deviation sets may differ. This is
expected and handled: deviation-analysis processes fidelity deviations (not
annotations), using annotations only as supplementary context. Annotations without
matching fidelity deviations are orphans and have no effect."

---

## FR/NFR Enumeration Status

The spec lacks formal FR-NNN and NFR-NNN identifiers required by the roadmap
pipeline's extraction step. I have identified **38 functional requirements** and
**7 non-functional requirements** distributed across Sections 3-8, 12-15.

These identifiers have been added in a companion edit to the spec file itself.
See the enumeration in the amended spec.

---

## Recommendations Summary (Priority Order)

| Priority | Finding | Action |
|----------|---------|--------|
| P0 | C-1: Deviation set divergence | Add matching strategy to Section 4.3 |
| P0 | C-2: Zero-annotation edge case | Add explicit zero-handling to fidelity prompt |
| P0 | C-3: Stale artifacts on resume | Add source_roadmap_hash to spec-deviations.md |
| P0 | C-4: Pre-approved deviation format | Specify option (b): include in table as INFO |
| P1 | M-2: Gate definition inconsistency | Consolidate to one canonical definition in Section 5.5 |
| P1 | M-3: validation_complete semantics | Define in Section 5.3 prompt design |
| P1 | M-1: Citation topic relevance | Strengthen Section 4.3 verification |
| P1 | M-4: Diamond dependency precedence | Add precedence rule to Section 5.3 |
| P1 | M-5: Annotation error format | Define DEV-NNN [ANNOTATION_INVALID] convention |
| P2 | m-1: Arithmetic consistency | Optional semantic check |
| P2 | m-2: Integration test | Add SC-7 |
| P2 | m-3: Concrete retry scenario | Add Given/When/Then to Section 8.6 |
