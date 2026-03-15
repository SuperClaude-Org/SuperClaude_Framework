---
title: "v2.25 Spec Amendment Brainstorm: 5 Immediate Pre-Implementation Blockers"
version: "2.25.0-amendments-v1"
status: draft
scope: immediate-blockers
author: brainstorm-agent
created: 2026-03-14
source: spec-panel-review
target_spec: v2.25-spec-merged.md
issues_addressed:
  - W-1 (CRITICAL): spec-patch cycle silently broken by STANDARD downgrade
  - W-ADV-1 (CRITICAL): empty routing_fix_roadmap silently drops all SLIPs
  - W-3 (MAJOR): artifact boundary between dev-*-accepted-deviation.md and spec-deviations.md undefined
  - W-2 (MAJOR): §11 affected-files summary omits all v2.24.2 functions
  - W-4+W-5 (MAJOR/MINOR): NFR-006 incomplete + no FR for behavioral consequence
---

# v2.25 Spec Amendment Brainstorm: 5 Immediate Pre-Implementation Blockers

This document is a pre-implementation amendment brainstorm, not a summary. Each section
identifies a specific flaw in v2.25-spec-merged.md, enumerates approaches with full tradeoff
analysis, recommends one approach, and provides exact draft spec language ready to insert.

---

## ISSUE 1 (W-1, CRITICAL): Spec-Patch Cycle Silently Broken by STANDARD Downgrade

### Problem Restatement

The v2.24.2 code in `executor.py` contains `_apply_resume_after_spec_patch()`, triggered when
`spec_fidelity_failed == True`. That boolean is set by checking whether the `spec-fidelity` step
produced a FAIL or TIMEOUT result. With v2.25 downgrading `SPEC_FIDELITY_GATE` from STRICT to
STANDARD, the gate now checks only frontmatter presence — no semantic checks remain. A fidelity
report with `high_severity_count: 5` passes the STANDARD gate and produces `StepStatus.PASS`.
`spec_fidelity_failed` is therefore almost always `False`, and `_apply_resume_after_spec_patch()`
never triggers for its original purpose. The v2.25 spec introduces this behavioral change without
acknowledging the spec-patch cycle exists at all, leaving implementors to discover the dormancy
through code archaeology after the fact. This is a documentation gap with active correctness
implications: if anyone expects the spec-patch auto-resume to continue functioning as documented
in the v2.24.2 FR set (FR-2.24.1.9 through FR-2.24.1.13), they will be silently wrong.

### Approaches Considered

#### Approach A: Retire the Spec-Patch Cycle

**Mechanism**: Add an explicit FR in §8 (Resume Logic Modifications) stating that
`_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`,
and `_spec_patch_cycle_count` are retired as of v2.25. Add a §14 backward-compat note explaining
the retirement rationale and documenting what the cycle did for historical reference. The code
can be deleted immediately or deprecated with a comment block pending cleanup.

**What this simplifies**:
- v2.25 executor.py gets ~130 lines simpler (deleting the spec-patch cycle code path).
- The `auto_accept` parameter to `execute_roadmap()` becomes dead code and can be removed.
- No future implementor needs to reason about two different auto-resume mechanisms co-existing
  (spec-patch cycle vs. the new deviation-analysis + remediation-budget cycle).
- The §14 compat note explicitly answers "where did accept-spec-change go?" for operators who
  used `roadmap accept-spec-change` in v2.24.x.

**What breaks**:
- Operators who manually triggered `roadmap accept-spec-change` and relied on the spec-patch
  auto-resume cycle lose that workflow. They must use `--resume` directly after patching the spec.
  This is a CLI behavioral change and requires a changelog entry.
- The `dev-*-accepted-deviation.md` artifact format becomes inert from the executor's perspective.
  The `spec_patch.py` module's `scan_accepted_deviation_records()` is still callable (e.g., by the
  `accept-spec-change` CLI command), but nothing in the pipeline reads it automatically.
- Any existing test coverage for `_apply_resume_after_spec_patch()` becomes dead weight.

**Risks remaining**:
- If a future version wants to reintroduce auto-resume on spec-patch, it must rebuild the logic.
  The v2.24.2 implementation (three-condition gate, six-step disk-reread sequence) is reasonably
  well-tested and deleting it means losing that implementation investment.
- Retirement removes the spec-fidelity STRICT failure path entirely. With the new pipeline,
  spec-fidelity never halts — which is correct. But if spec-fidelity somehow fails its STANDARD
  gate (e.g., agent produces empty output), the pipeline halts normally, NOT via spec-patch cycle.
  This is correct behavior but must be explicit.

**Verdict on Approach A**: Cleanest long-term. The spec-patch cycle was a targeted fix for a
world where spec-fidelity was STRICT. That world ends in v2.25. Retiring the cycle removes dead
code and eliminates a subtle "two resume mechanisms" confusion. However, retirement should not
be done silently — it needs an explicit FR, a §14 entry, and a note about `accept-spec-change`
CLI command behavior.

---

#### Approach B: Re-Trigger on Deviation-Analysis Failure

**Mechanism**: Change the trigger condition in `execute_roadmap()`. Instead of:

```python
spec_fidelity_failed = any(
    r.step and r.step.id == "spec-fidelity"
    and r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)
    for r in results
)
```

Change to:

```python
spec_fidelity_failed = any(
    r.step and r.step.id in ("spec-fidelity", "deviation-analysis")
    and r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)
    for r in results
)
```

The rationale: the spec-patch cycle was designed to handle "agent subprocess patched the spec
file and wrote a `dev-*-accepted-deviation.md`." This scenario is still possible in v2.25 if
`deviation-analysis` fails its STRICT gate (e.g., `ambiguous_count > 0`) AND a subprocess
wrote new accepted-deviation records AND the spec hash changed. The cycle provides auto-resume
in this case.

**What this preserves**:
- The spec-patch cycle machinery in executor.py remains alive and purposeful.
- `scan_accepted_deviation_records()` in `spec_patch.py` continues to serve a pipeline function.
- Operators who rely on `roadmap accept-spec-change` keep a clear mental model: deviation-analysis
  STRICT failure can auto-recover if the right evidence files exist.

**What changes**:
- The trigger fires on `deviation-analysis` FAIL instead of `spec-fidelity` FAIL.
- The spec must document the new trigger condition explicitly (a new FR with a distinct number).
- The three original conditions (cycle_count==0, qualifying dev-*-accepted-deviation.md files with
  mtime > fidelity started_at, spec hash changed) must be re-evaluated. Condition 2 references
  `started_at` from `spec-fidelity` state — this would need to change to `deviation-analysis`
  started_at, requiring a small code change and a spec amendment.

**Tradeoffs and risks**:
- The semantic connection is weaker than in v2.24.2. In v2.24.2, spec-fidelity STRICT failure +
  spec-patched + new deviation records = "agent fixed the spec, resume from fidelity." In v2.25,
  deviation-analysis STRICT failure + spec-patched + new deviation records is a plausible scenario
  (a subprocess classified ambiguous deviations and patched the spec and the debate artifact), but
  it is a more exotic case. The common case for deviation-analysis STRICT failure (`ambiguous_count
  > 0`) is NOT resolved by spec-patching — it requires human review.
- The cycle's Condition 3 (spec hash changed) is a necessary but not sufficient signal. Deviation
  analysis ambiguity is resolved by clarifying the debate artifacts, not the spec file. So the
  auto-resume trigger would fire in cases where it cannot actually help, and fail to fire in the
  common case where human review is the only resolution.
- This approach keeps dead code alive under a new name while giving it a role it does not fit well.

**Verdict on Approach B**: Not recommended. The scenario where deviation-analysis STRICT failure
is resolved by a spec patch + new accepted-deviation records is real but rare. The more common
deviation-analysis STRICT failure (ambiguous_count > 0) cannot be auto-resolved this way. Keeping
the cycle alive for the rare case adds complexity and requires careful documentation of when it
does and does not help.

---

#### Approach C: Keep As-Is (Document Dormancy)

**Mechanism**: Add a prose note to §8.2 or a new §8.7 stating that
`_apply_resume_after_spec_patch()` remains in executor.py from v2.24.2 and is effectively dormant
in normal v2.25 runs. Document the specific conditions under which it could still trigger: if
spec-fidelity somehow fails its STANDARD gate (missing frontmatter, zero-byte output), AND a
subprocess wrote qualifying `dev-*-accepted-deviation.md` files, AND the spec hash changed, the
cycle fires. Acknowledge that this path is a corner case and that the cycle is not the primary
recovery mechanism in v2.25 (that role belongs to deviation-analysis + --resume).

**What this preserves**:
- Zero code changes relative to v2.24.2 executor.py.
- `roadmap accept-spec-change` CLI command continues to work as documented.
- Implementation teams do not need to delete tested code.

**Tradeoffs and risks**:
- The spec now contains a documented feature that essentially never fires in production. This
  is technically honest but architecturally confusing: implementors implementing from the spec
  must understand two resume mechanisms — the new deviation-analysis-driven `--resume` cycle
  (§8.3–8.6) and the dormant spec-patch auto-resume — and reason about when each applies.
- Fails to prevent the next implementor from asking "why is `_apply_resume_after_spec_patch()`
  still here?" The docstring already says "FR-2.24.1.9" — but those FR numbers are from the
  previous spec version. Without an explicit statement in v2.25 that this function is dormant
  by design, any implementor will assume it is a bug or an oversight.
- Dormant code with live wiring (the trigger check is still in execute_roadmap()) is a latent
  confusion vector for code reviewers and future AI agents reading the executor.

**Verdict on Approach C**: Acceptable as a minimal patch if retirement is politically blocked,
but inferior to Approach A. Dormancy documentation is better than silence, but explicit
retirement is cleaner.

---

### Recommended Approach

**Approach A: Retire the spec-patch cycle.**

The fundamental justification: the spec-patch cycle existed to handle a world where spec-fidelity
STRICT was the only recovery mechanism and it was permanently blocked. v2.25 eliminates that world.
The deviation-analysis STRICT gate + bounded `--resume` remediation cycle is the new recovery path.
There is no scenario in v2.25 where the spec-patch auto-resume adds value that the new mechanisms
do not already provide. Retiring it removes ~130 lines of code, eliminates a subtle "two resume
mechanisms" mental model for implementors, and makes the spec internally consistent.

The `roadmap accept-spec-change` CLI command (`prompt_accept_spec_change()` in `spec_patch.py`)
is NOT retired — it remains useful as a manual operator tool for updating the spec hash after a
deliberate spec modification. Only the auto-triggering from within `execute_roadmap()` is retired.

### Draft Spec Language

**Insert as new §8.7 in §8 (Resume Logic Modifications)**:

---

#### 8.7 Spec-Patch Auto-Resume Cycle: Retirement

**FR-055**: As of v2.25, the spec-patch auto-resume cycle introduced in v2.24.2
(`_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`,
`_spec_patch_cycle_count`) SHALL be retired from `executor.py`. The trigger check in
`execute_roadmap()` — which fired when `spec_fidelity_failed == True` — SHALL be removed.

**Rationale**: The spec-patch cycle was designed for a pipeline where `SPEC_FIDELITY_GATE` was
STRICT and a permanent halt on fidelity failure could only be recovered by patching the spec and
resuming. v2.25 eliminates this failure mode: `SPEC_FIDELITY_GATE` is now STANDARD (never
semantically blocks), and the `DEVIATION_ANALYSIS_GATE` (STRICT) is the new blocking gate, with
recovery via bounded `--resume` remediation cycles (§8.4–8.6). The auto-resume scenario the
spec-patch cycle handled — "subprocess patched spec, wrote `dev-*-accepted-deviation.md`, pipeline
should resume from spec-fidelity" — no longer arises in the v2.25 pipeline because spec-fidelity
no longer blocks.

**Scope of retirement** (code to be deleted from `executor.py`):
- The `_spec_patch_cycle_count = 0` local variable in `execute_roadmap()`
- The `initial_spec_hash = hashlib.sha256(...)` capture in `execute_roadmap()`
- The `spec_fidelity_failed` boolean and the `if spec_fidelity_failed:` block in `execute_roadmap()`
- The `_apply_resume_after_spec_patch()` function definition (~90 lines)
- The `_find_qualifying_deviation_files()` function definition (~45 lines)
- The `auto_accept` parameter from `execute_roadmap()` signature

**Not retired**: `spec_patch.py` and its `prompt_accept_spec_change()` function remain unchanged.
The `roadmap accept-spec-change` CLI command continues to function as a manual operator tool for
updating `spec_hash` in `.roadmap-state.json` after deliberate spec modifications. The
`scan_accepted_deviation_records()` function and the `DeviationRecord` dataclass remain in
`spec_patch.py` unchanged. Only the executor's automatic triggering is removed.

**Insert as new subsection §14.7 in §14 (Backward Compatibility)**:

---

#### 14.7 Spec-Patch Auto-Resume Retirement

**NFR-011**: The `_apply_resume_after_spec_patch()` auto-resume cycle SHALL NOT be present in
v2.25 executor.py. Operators who relied on automatic spec-patch auto-resume in v2.24.x SHALL
use explicit `--resume` invocations after any spec modification.

The v2.24.2 spec-patch auto-resume cycle triggered when three conditions were simultaneously true:

1. `spec-fidelity` step failed its STRICT gate (`spec_fidelity_failed == True`)
2. Qualifying `dev-*-accepted-deviation.md` files existed with mtime > fidelity started_at
3. The spec file SHA-256 hash changed since `execute_roadmap()` entry

In v2.25, Condition 1 never occurs in normal operation because `SPEC_FIDELITY_GATE` is STANDARD
(no semantic checks). The recovery mechanism that replaced the spec-patch cycle is:

- `DEVIATION_ANALYSIS_GATE` (STRICT) blocks on `ambiguous_count > 0` (human review required)
- Bounded `--resume` remediation cycle (max 2 attempts) for SLIP remediation failure
- Manual `roadmap accept-spec-change` for deliberate spec modifications followed by `--resume`

Existing `.roadmap-state.json` files containing `spec_hash` entries remain valid. The
`accept-spec-change` CLI command continues to update `spec_hash` for manual use.

---

## ISSUE 2 (W-ADV-1, CRITICAL): Empty `routing_fix_roadmap` Silently Drops All SLIPs

### Problem Restatement

The `deviations_to_findings()` function (FR-033) reads `routing_fix_roadmap` from
`deviation-analysis.md` frontmatter and converts those IDs to `Finding` objects. If
`routing_fix_roadmap:` is empty (blank value after the colon, which is valid YAML for a null
or empty string), `_parse_routing_list()` returns `[]`, and `deviations_to_findings()` returns
an empty list at line `if not fix_ids: return []`. The remediate step receives zero findings.
The certify agent writes `certified: true` because there is nothing to certify against. The
`CERTIFY_GATE` semantic check `_certified_is_true()` sees `certified: true` and passes. The
pipeline completes "successfully." Every SLIP in the fidelity report was silently ignored.

This failure mode is not hypothetical: an agent under context pressure or prompt ambiguity might
produce `routing_fix_roadmap:` with a null value when it meant `routing_fix_roadmap: DEV-002,DEV-003`.
The YAML parses silently, the gate passes, and the discrepancy is invisible in the output.

### Approaches Considered

#### Approach A: Semantic Check on DEVIATION_ANALYSIS_GATE

**Mechanism**: Add a new semantic check function `_routing_consistent_with_slip_count()` to
`gates.py`. The check reads two frontmatter fields from `deviation-analysis.md`: `slip_count`
(integer) and `routing_fix_roadmap` (comma-separated string). If `slip_count > 0` AND
`routing_fix_roadmap` is empty/null/whitespace-only, the check returns `False`. The gate
fails with a clear error message.

The check does NOT require that routing_fix_roadmap contain exactly `slip_count` entries — that
would be too strict (INTENTIONAL-preference deviations also go to fix_roadmap). It only enforces
the invariant: if there are SLIPs, at least one deviation must be routed somewhere.

Wait — that is not quite right either. INTENTIONAL-preference SLIPs go to fix_roadmap. PRE_APPROVED
go to no_action. So the minimum correct invariant is: if `slip_count > 0`, then
`routing_fix_roadmap` must be non-empty (because SLIPs are always routed to fix_roadmap per
FR-022). This is a necessary consequence of the classification rules.

Refined check: `slip_count > 0` implies `len(fix_ids) >= slip_count`. But since INTENTIONAL-preference
also goes to fix_roadmap, the minimum constraint is: `routing_fix_roadmap` must have at least
`slip_count` entries (each SLIP must appear in routing_fix_roadmap). Enforcing exact membership
requires parsing the body, which is out of scope for a frontmatter-only gate.

Practical implementation: check that `slip_count > 0` implies `routing_fix_roadmap` is non-empty.
This catches the silent-drop case while remaining implementable as a pure-frontmatter check.

```python
def _routing_consistent_with_slip_count(content: str) -> bool:
    """Validate routing_fix_roadmap is non-empty when slip_count > 0.

    Invariant: if slip_count > 0, at least one deviation must appear in
    routing_fix_roadmap (SLIPs are always routed to fix_roadmap per FR-022).

    Returns True if:
    - slip_count == 0 (no SLIPs, routing_fix_roadmap may be empty)
    - slip_count > 0 AND routing_fix_roadmap has at least one ID

    Returns False if:
    - slip_count > 0 AND routing_fix_roadmap is empty/null/whitespace
    - slip_count is missing or unparseable (fail-closed)
    - routing_fix_roadmap field is absent (fail-closed)
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    # Fail-closed: slip_count must be present and parseable
    slip_val = fm.get("slip_count")
    if slip_val is None:
        return False
    try:
        slip_count = int(slip_val)
    except (ValueError, TypeError):
        return False

    # If no SLIPs, routing_fix_roadmap may be empty -- that is correct
    if slip_count == 0:
        return True

    # slip_count > 0: routing_fix_roadmap must be non-empty
    routing_val = fm.get("routing_fix_roadmap", "")
    if routing_val is None:
        return False
    routing_str = str(routing_val).strip()
    return len(routing_str) > 0
```

Gate failure message: `"slip_count > 0 but routing_fix_roadmap is empty. Every SLIP must be routed to fix_roadmap. Verify the deviation-analysis agent output is complete."`

**Where in the pipeline this fires**: `DEVIATION_ANALYSIS_GATE` (STRICT tier, step 10), before
`deviations_to_findings()` is ever called. The gate blocks the pipeline and halts with the message
above, rather than allowing the silent-pass-with-empty-findings scenario.

**What this prevents**: Any run where the deviation-analysis agent wrote `slip_count: 2` but left
`routing_fix_roadmap:` blank will halt at the gate with a clear diagnostic message.

**Tradeoffs**:
- This check is purely structural: it cannot verify that the IDs in routing_fix_roadmap are the
  correct IDs (e.g., it cannot detect routing_fix_roadmap: DEV-999 when the actual SLIPs are
  DEV-002 and DEV-003). ID-level validation requires body parsing.
- Does NOT catch the case where slip_count: 0 but actually there are uncounted SLIPs — that
  failure mode is upstream (the agent undercounting slips) and requires anti-laundering checks.
- Simple to implement: one function, one gate amendment, no pipeline structure changes.

---

#### Approach B: Guard in `deviations_to_findings()`

**Mechanism**: In `deviations_to_findings()`, after `fix_ids = _parse_routing_list(...)`, add:

```python
if not fix_ids:
    # Check if slip_count says there should be findings
    da_fm = _parse_frontmatter(da_content)
    slip_count = int(da_fm.get("slip_count", 0)) if da_fm else 0
    if slip_count > 0:
        raise ValueError(
            f"deviation-analysis.md reports slip_count={slip_count} but "
            f"routing_fix_roadmap is empty. The deviation-analysis artifact "
            f"is inconsistent. Re-run deviation-analysis or fix the routing table."
        )
    return []
```

**Where this fires**: Inside `deviations_to_findings()`, which is called by the remediate step
or its orchestration logic (not the gate). This fires later than Approach A — after the
`DEVIATION_ANALYSIS_GATE` has already passed.

**What this prevents**: The silent-empty-findings scenario. The `ValueError` propagates up to
whatever calls `deviations_to_findings()`, which should be caught and converted to a pipeline
step failure.

**Tradeoffs**:
- Fires after the gate has passed, meaning the gate passed on a bad artifact. The gate itself
  has no record of the inconsistency. Debugging requires looking at remediate step logs, not
  deviation-analysis gate output.
- Requires that the caller of `deviations_to_findings()` handles `ValueError` correctly. If it
  does not (e.g., bare call without try/except), the exception propagates unchecked and could
  produce an unhelpful traceback rather than a clean pipeline failure message.
- Better than nothing, but defense-in-depth should catch this earlier (at the gate level).
- This approach can be combined with Approach A for defense-in-depth: gate blocks first, then
  the ValueError is a secondary guard against gate bypass or future gate relaxation.

---

#### Approach C: Cross-Check in Certify

**Mechanism**: Add a semantic check to `CERTIFY_GATE` that cross-references the
`findings_verified` count in the certification report against the `slip_count` in
`deviation-analysis.md`. Specifically: read `deviation-analysis.md` from the output directory,
parse `slip_count`, and require that `findings_verified >= slip_count` in the certification
report.

```python
def _findings_cover_slip_count(content: str) -> bool:
    """Validate that certify addressed at least as many findings as slip_count."""
    # ... reads both deviation-analysis.md and certification-report.md ...
```

**Where this fires**: `CERTIFY_GATE` (STRICT tier, post-pipeline).

**What this prevents**: The case where certify certified an empty finding set.

**Tradeoffs**:
- Fires extremely late (certify is the last step). A silent drop of SLIPs at deviations_to_findings
  time propagates through the entire remediate step undetected before certify catches it.
- Certify semantic checks are currently single-artifact: they read only the certification report
  content passed to the check function. Adding a file-system read inside a semantic check function
  breaks this assumption and introduces a hidden dependency on the output directory path. The
  current `_certified_is_true()` signature is `(content: str) -> bool` — cross-file checks
  require changing the interface or using a closure.
- Architecturally, the certify gate should validate the certification report, not re-validate
  a previous step's output. Cross-step validation in a gate is an anti-pattern here.
- This approach fixes the wrong place. The problem is at the gate for deviation-analysis (Approach A)
  or at the conversion function (Approach B). Detecting it at certify is too late and architecturally
  awkward.

**Verdict on Approach C**: Not recommended. Catches the failure at the wrong stage with the wrong
mechanism.

---

### Recommended Approach

**Approach A: Add semantic check to DEVIATION_ANALYSIS_GATE**, combined with the `ValueError`
guard from Approach B as a secondary defense.

The gate is the correct place to enforce structural invariants of the `deviation-analysis.md`
artifact before it is consumed downstream. Adding `_routing_consistent_with_slip_count()` to
`DEVIATION_ANALYSIS_GATE` catches the empty-routing case immediately, with a clear failure message
pointing at the deviation-analysis step as the source. The `ValueError` guard in
`deviations_to_findings()` provides secondary defense against future gate relaxation or direct
function calls in tests.

### Draft Spec Language

**Add to §5.5 (Gate Definition) after the existing `DEVIATION_ANALYSIS_GATE` definition**:

---

**FR-056**: A `_routing_consistent_with_slip_count()` semantic check function SHALL be added to
`gates.py`. The check SHALL return `False` if `slip_count > 0` AND `routing_fix_roadmap` is empty,
null, or whitespace-only. It SHALL return `True` if `slip_count == 0` (empty routing is correct
when there are no SLIPs). It SHALL fail-closed: if `slip_count` is absent or unparseable, it
returns `False`.

```python
def _routing_consistent_with_slip_count(content: str) -> bool:
    """Validate routing_fix_roadmap is non-empty when slip_count > 0.

    Invariant (FR-022): SLIPs are always routed to fix_roadmap. Therefore,
    slip_count > 0 implies routing_fix_roadmap must contain at least one ID.

    Fails closed: missing or unparseable slip_count returns False.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    slip_val = fm.get("slip_count")
    if slip_val is None:
        return False
    try:
        slip_count = int(slip_val)
    except (ValueError, TypeError):
        return False

    if slip_count == 0:
        return True  # No SLIPs; empty routing is correct

    routing_val = fm.get("routing_fix_roadmap", "")
    if routing_val is None:
        return False
    return len(str(routing_val).strip()) > 0
```

**FR-057**: The `DEVIATION_ANALYSIS_GATE` SHALL include `_routing_consistent_with_slip_count`
as a third semantic check, appended after `no_ambiguous_deviations` and
`validation_complete_true`. The failure message SHALL be:

```
"slip_count > 0 but routing_fix_roadmap is empty. Every SLIP must appear in
routing_fix_roadmap (FR-022). Verify deviation-analysis agent output is complete
and re-run the deviation-analysis step."
```

**Updated DEVIATION_ANALYSIS_GATE** (replaces the definition in §5.5):

```python
DEVIATION_ANALYSIS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_analyzed",
        "pre_approved_count",
        "intentional_count",
        "slip_count",
        "ambiguous_count",
        "adjusted_high_severity_count",
        "validation_complete",
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
        SemanticCheck(
            name="validation_complete_true",
            check_fn=_validation_complete_true,
            failure_message="validation_complete must be true before remediation can proceed",
        ),
        SemanticCheck(
            name="routing_consistent_with_slip_count",
            check_fn=_routing_consistent_with_slip_count,
            failure_message=(
                "slip_count > 0 but routing_fix_roadmap is empty. "
                "Every SLIP must appear in routing_fix_roadmap (FR-022). "
                "Verify deviation-analysis agent output is complete and "
                "re-run the deviation-analysis step."
            ),
        ),
    ],
)
```

**FR-058**: The `deviations_to_findings()` function SHALL include a secondary guard: if
`_parse_routing_list()` returns an empty list AND frontmatter `slip_count > 0`, the function
SHALL raise `ValueError` with a message indicating the artifact is inconsistent. This guard is
defense-in-depth against gate bypass and direct function calls in test harnesses.

**Add to §7.2 (Deviation-to-Finding Conversion), immediately after the `if not fix_ids: return []`
block in the `deviations_to_findings()` code listing**:

```python
    if not fix_ids:
        # Secondary guard (defense-in-depth against gate bypass):
        # If the gate passed but routing is empty, check slip_count.
        # This should never fire in production if DEVIATION_ANALYSIS_GATE is enforced.
        slip_count = int(da_fm.get("slip_count", 0)) if da_fm else 0
        if slip_count > 0:
            raise ValueError(
                f"deviation-analysis.md reports slip_count={slip_count} but "
                f"routing_fix_roadmap is empty. Artifact is inconsistent. "
                f"Re-run deviation-analysis or fix the routing table manually."
            )
        return []
```

---

## ISSUE 3 (W-3, MAJOR): Artifact Boundary Between `dev-*-accepted-deviation.md` and `spec-deviations.md` Undefined

### Problem Restatement

v2.25 introduces `spec-deviations.md` as the output of the new `annotate-deviations` step
(§3.4). v2.24.2 defined `dev-*-accepted-deviation.md` as agent-written records with fields
`disposition: ACCEPTED`, `spec_update_required: true`, read by `scan_accepted_deviation_records()`
in `spec_patch.py`. Both artifact types live in the output directory, both are named with
"deviation" in the filename, and both track deviations from the spec. The v2.25 spec introduces
`spec-deviations.md` in §3 without ever mentioning `dev-*-accepted-deviation.md` or explaining
the relationship. An implementor reading the spec encounters two artifact types that superficially
serve the same purpose and must infer from code archaeology that they are completely different:
different writers (pipeline step vs. subprocess agents), different readers (deviation-analysis step
vs. spec_patch.py / executor's retired spec-patch cycle), different lifecycles, and different
consumption paths. Without explicit documentation, implementors will confuse them — or worse, try
to "unify" them by having `annotate-deviations` write `dev-*-accepted-deviation.md` files, which
would be wrong.

### Approaches Considered

#### Approach A: Add §3.1 "Artifact Taxonomy" Subsection

**Mechanism**: Insert a new subsection §3.1 "Artifact Taxonomy: Deviation-Related Files" into
§3 (New Step: `annotate-deviations`), immediately before §3.1 (Step Definition, renumbered to
§3.2). This subsection enumerates all deviation-related artifact types with a structured table
covering: artifact name/glob, writer, readers, lifecycle, and explicit "does not substitute for"
notes.

**Placement**: §3 is the logical home because it is where `spec-deviations.md` is first introduced.
A reader encountering the new artifact for the first time in §3 immediately gets the full taxonomy
rather than discovering the ambiguity later.

**What this prevents**:
- Implementors conflating the two artifact types.
- Future agents reading the spec and incorrectly routing `annotate-deviations` output to
  `dev-*-accepted-deviation.md` format.
- Test authors writing tests that mix the two formats.

**Tradeoffs**:
- Requires renumbering §3.1–§3.5 to §3.2–§3.6, which is a mechanical change.
- Places taxonomy content in §3 (a step-specific section) rather than a document-level reference
  section. Readers who start at §14 (backward compat) for context will not find the taxonomy there.
  Mitigated by adding a cross-reference in §14.

---

#### Approach B: §14 Backward-Compat Note with Comparison Table

**Mechanism**: Add a new §14.8 "Deviation Artifact Taxonomy" to §14 (Backward Compatibility).
This is a natural placement because understanding the two artifact types is a backward-compat
concern: implementors upgrading from v2.24.x need to know what changed.

**What this prevents**:
- Same as Approach A, but discovery requires navigating to §14.
- More appropriate placement for backward-compat-focused readers.

**Tradeoffs**:
- §14 is a backward-compat section; a general taxonomy belongs in a more foundational location.
  Readers implementing v2.25 from scratch (no v2.24.2 context) will not look in §14 for basic
  artifact definitions.
- The taxonomy content is reference material for the whole spec, not just the compat section.
- Can be combined with Approach A (§3.1 as the primary reference, §14 as a cross-reference).

---

#### Approach C: Allow `annotate-deviations` to Consult `dev-*-accepted-deviation.md`

**Mechanism**: Define an opt-in mechanism by which the `annotate-deviations` agent reads any
existing `dev-*-accepted-deviation.md` files as additional evidence when classifying deviations.
The idea: accepted deviation records from prior pipeline runs (e.g., if the release had prior
`roadmap run` attempts that produced accepted deviations) provide historical context about which
deviations have already been accepted by an operator.

**Opt-in mechanism**: The `build_annotate_deviations_prompt()` function gains an optional
parameter `prior_deviations: list[Path] | None = None`. When provided, the prompt includes the
content of those files as context labeled "Previously accepted deviations from prior pipeline runs."
The `annotate-deviations` step in `_build_steps()` optionally passes any matching
`dev-*-accepted-deviation.md` files from the output directory.

**What this enables**: An iterative refinement workflow where operators accept deviations across
multiple pipeline runs and the annotator benefits from that history.

**Risks**:
- This dramatically increases the conceptual scope of v2.25. The spec would now define not just
  two artifact types but an active relationship between them.
- `dev-*-accepted-deviation.md` files from v2.24.2 pipelines (where spec-fidelity was STRICT)
  may not be semantically equivalent to v2.25's INTENTIONAL_IMPROVEMENT classification. A prior
  accepted deviation may have been accepted for reasons that do not match the v2.25 classification
  scheme. The annotator would need to re-verify, which is exactly what the annotate-deviations
  step already does from the debate transcript.
- Introduces cross-run state dependency. `spec-deviations.md` is defined as regenerated on each
  run (OQ-7 resolution). Having it consult `dev-*-accepted-deviation.md` from prior runs makes
  the annotation non-deterministic relative to the pipeline's own outputs.
- The benefit is marginal: the annotate-deviations step already reads the debate transcript,
  which is the authoritative source for intentionality evidence. Prior accepted-deviation records
  add no new evidence that is not already in the debate transcript.

**Verdict on Approach C**: Not recommended. It conflates two artifact types that serve different
purposes, introduces cross-run state dependency, and provides marginal value over what the
debate transcript already offers.

---

### Recommended Approach

**Approach A as primary, with a §14 cross-reference** (elements of Approach B).

Insert §3.1 "Artifact Taxonomy" immediately before the step definition (renaming current §3.1
to §3.2). Add a cross-reference note in §14. This ensures the taxonomy is discovered on first
encounter with `spec-deviations.md` in §3, while §14 provides a compat-oriented summary for
upgrade-path readers.

### Draft Spec Language

**Insert as new §3.1 in §3 (renumber current §3.1–§3.5 to §3.2–§3.6)**:

---

### 3.1 Artifact Taxonomy: Deviation-Related Files

v2.25 introduces `spec-deviations.md` as a new pipeline artifact. It coexists in the output
directory with `dev-*-accepted-deviation.md` files from v2.24.2. These artifacts are distinct
in purpose, writer, reader, and lifecycle. They MUST NOT be confused or treated as substitutes.

| Property | `spec-deviations.md` | `dev-*-accepted-deviation.md` |
|----------|---------------------|-------------------------------|
| **Glob pattern** | `spec-deviations.md` (exact filename) | `dev-*-accepted-deviation.md` (glob, zero or more) |
| **Writer** | `annotate-deviations` pipeline step (Step 7, FR-003) | Subprocess agent invocations during roadmap generation (v2.24.2); written outside the pipeline orchestration loop |
| **Readers** | `spec-fidelity` step (as additional input, FR-018); `deviation-analysis` step (as classification context, FR-019) | `scan_accepted_deviation_records()` in `spec_patch.py` (for the `roadmap accept-spec-change` CLI command) |
| **Lifecycle** | Regenerated on each pipeline run. Skipped on `--resume` only if its `ANNOTATE_DEVIATIONS_GATE` already passes. Never incrementally updated. | Written by subprocesses during agent execution. Persists across pipeline runs. Accumulates over time. |
| **Format** | YAML frontmatter (`total_annotated`, count fields) + deviation annotation table + evidence sections | YAML frontmatter (`disposition: ACCEPTED`, `spec_update_required: true/false`, `affects_spec_sections`, `acceptance_rationale`) + markdown body |
| **Classification scheme** | `INTENTIONAL_IMPROVEMENT` / `INTENTIONAL_PREFERENCE` / `SCOPE_ADDITION` / `NOT_DISCUSSED` | Binary: `disposition: ACCEPTED` or `REJECTED` |
| **Purpose** | Pre-compute deviation classification for fidelity agent and deviation-analysis step (Scope 2: prevention) | Record operator or subprocess acceptance of a specific deviation, enabling spec-hash update via `accept-spec-change` command |
| **Pipeline role in v2.25** | Active: consumed by steps 9 (spec-fidelity) and 10 (deviation-analysis) | Passive: read only by manual CLI command (`roadmap accept-spec-change`). Not read by any pipeline step in v2.25. |
| **Substitution** | Does NOT substitute for `dev-*-accepted-deviation.md` | Does NOT substitute for `spec-deviations.md` |

**Critical implementation note**: The `annotate-deviations` step SHALL write only `spec-deviations.md`
and SHALL NOT write `dev-*-accepted-deviation.md` files. The two formats are not interchangeable.
An `annotate-deviations` agent that writes `dev-*-accepted-deviation.md` is producing the wrong
artifact and will cause the deviation-analysis step to receive an empty or absent
`spec-deviations.md` input.

**Add cross-reference to §14 as new §14.8**:

---

#### 14.8 Deviation Artifact Taxonomy (Cross-Reference)

See §3.1 for the full artifact taxonomy table. In summary: `spec-deviations.md` (new in v2.25,
written by `annotate-deviations` step, consumed by `spec-fidelity` and `deviation-analysis`) and
`dev-*-accepted-deviation.md` (v2.24.2, written by subprocess agents, consumed only by the
`roadmap accept-spec-change` CLI command in v2.25) serve completely different purposes and MUST
NOT be confused.

**NFR-012**: No pipeline step introduced or modified in v2.25 SHALL read `dev-*-accepted-deviation.md`
files as part of its normal execution. The `dev-*-accepted-deviation.md` artifact format is
consumed exclusively by `spec_patch.py` / the `roadmap accept-spec-change` CLI command.

---

## ISSUE 4 (W-2, MAJOR): §11 Affected-Files Summary Omits All v2.24.2 Functions

### Problem Restatement

§11 (Affected Files Summary) lists every file modified, potentially modified, newly created, or
tested by v2.25. The executor.py row in the "Files Modified" table reads:

> `src/superclaude/cli/roadmap/executor.py` | 1, 2, 3 | Add 2 steps to `_build_steps()`; update `_get_all_step_ids()`; add `remediation_attempts` counter; add `_check_remediation_budget()`, `_print_terminal_halt()`

This list is the set of changes v2.25 makes to executor.py. It is accurate as far as it goes. But
it omits entirely the v2.24.2 functions that already live in executor.py and are NOT modified by
v2.25: `execute_roadmap(auto_accept=False)`, `_apply_resume_after_spec_patch()`,
`_find_qualifying_deviation_files()`, `initial_spec_hash`, and `_spec_patch_cycle_count`. With
the recommendation from Issue 1 (Approach A) to retire these, the §11 entry needs to also list
them as deletions. Without this, an implementor reading §11 as their change checklist has no
indication that they need to handle the existing spec-patch cycle code — whether by deleting it
(if Approach A is adopted) or explicitly leaving it alone (if Approach C is adopted).

### Approaches Considered

#### Approach A: Add "Pre-Existing v2.24.2 Functions Retired by v2.25" Subsection to §11

**Mechanism**: Add a new subsection §11.x "Functions Retired from executor.py in v2.25" with a
table listing each function/variable being deleted, its original v2.24.2 FR reference, and the
retirement rationale. This is the correct approach if Issue 1 Approach A is adopted (retirement).

**Content**: The table lists `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`,
`initial_spec_hash`, `_spec_patch_cycle_count`, the `auto_accept` parameter from
`execute_roadmap()`, and the `spec_fidelity_failed` trigger block.

**What this enables**: Implementors have a complete, verifiable checklist for executor.py
changes: additions (from the existing §11 table), deletions (from the new subsection).

**Tradeoffs**: Requires adopting the retirement decision from Issue 1. If Issue 1 is resolved
differently (Approach C), the subsection title changes to "Functions Dormant in v2.25" with a
different explanation but the same list.

---

#### Approach B: Inline Annotation in Existing §11 Executor.py Entry

**Mechanism**: Extend the executor.py row in the "Files Modified" table with a note:

> `src/superclaude/cli/roadmap/executor.py` | 1, 2, 3 | Add 2 steps to `_build_steps()`; update `_get_all_step_ids()`; add `remediation_attempts` counter; add `_check_remediation_budget()`, `_print_terminal_halt()`; **RETIRE: `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`, `_spec_patch_cycle_count`, `auto_accept` param (FR-055)**

**Tradeoffs**: Inline annotation works but makes the table row unwieldy. The table format in §11
is already wide. Adding a multiline retirement list to a table cell defeats the purpose of using
a table for clarity. A dedicated subsection is cleaner.

---

#### Approach C: Separate §11.x "v2.24.2 → v2.25 Compatibility Surface" Table

**Mechanism**: Add a distinct subsection §11.5 "v2.24.2 → v2.25 Compatibility Surface" with a
two-column table: column 1 lists v2.24.2 functions/variables in executor.py; column 2 states
their v2.25 disposition (RETIRED, UNCHANGED, or MODIFIED). This is a superset of Approach A —
it covers not just retired items but also the functions that are unchanged.

**Content example**:

| v2.24.2 Symbol | v2.25 Disposition |
|----------------|-------------------|
| `execute_roadmap(config, resume, no_validate, auto_accept)` | MODIFIED: `auto_accept` parameter removed (FR-055) |
| `_apply_resume_after_spec_patch()` | RETIRED (FR-055) |
| `_find_qualifying_deviation_files()` | RETIRED (FR-055) |
| `initial_spec_hash` (local var) | RETIRED (FR-055) |
| `_spec_patch_cycle_count` (local var) | RETIRED (FR-055) |
| `_apply_resume()` | UNCHANGED |
| `_build_steps()` | MODIFIED: 2 new steps added (FR-004, FR-020) |
| `_get_all_step_ids()` | MODIFIED: 2 new step IDs added (FR-038) |
| `_save_state()` | MODIFIED: `remediation_attempts` counter added (FR-039) |
| `_check_remediation_budget()` | NEW (FR-040) |
| `_print_terminal_halt()` | NEW (FR-042) |

This gives implementors a complete map of the executor.py surface for both what they must add
and what they must remove, with no ambiguity about what is intentionally left alone.

---

### Recommended Approach

**Approach C: Add §11.5 "v2.24.2 → v2.25 Compatibility Surface" table.**

Approach C provides the most complete reference with the least ambiguity. It serves both
implementors (complete checklist of changes) and reviewers (can verify executor.py diff against
the table). Approach A is a subset of C. Approach B's inline annotation is harder to read.

The table below is the exact content to insert, reflecting the retirement decision from Issue 1
(Approach A). If Issue 1 is resolved differently, only the RETIRED rows change.

### Draft Spec Language

**Insert as new §11.5 after the existing §11 tables**:

---

### 11.5 v2.24.2 → v2.25 Compatibility Surface: `executor.py`

The following table maps every v2.24.2 symbol in `executor.py` to its v2.25 disposition. This
table is authoritative for implementors performing the v2.24.2 → v2.25 migration. Symbols marked
RETIRED are deleted in v2.25. Symbols marked UNCHANGED are intentionally left alone. Symbols
marked MODIFIED or NEW are covered by the FR references.

| v2.24.2 Symbol in `executor.py` | v2.25 Disposition | FR Reference |
|----------------------------------|-------------------|--------------|
| `execute_roadmap(config, resume, no_validate, auto_accept)` — function signature | MODIFIED: `auto_accept` parameter removed | FR-055 |
| `_spec_patch_cycle_count = 0` — local variable in `execute_roadmap()` | RETIRED | FR-055 |
| `initial_spec_hash = hashlib.sha256(...)` — local variable in `execute_roadmap()` | RETIRED | FR-055 |
| `spec_fidelity_failed = any(...)` — boolean + conditional block in `execute_roadmap()` | RETIRED | FR-055 |
| `_find_qualifying_deviation_files(config, results)` — function | RETIRED | FR-055 |
| `_apply_resume_after_spec_patch(config, results, auto_accept, initial_spec_hash, cycle_count)` — function | RETIRED | FR-055 |
| `_apply_resume(steps, config, gate_passed)` | UNCHANGED | — |
| `_build_steps(config)` | MODIFIED: `annotate-deviations` (FR-004) and `deviation-analysis` (FR-020) steps added; spec-fidelity step updated to include `deviations_file` input (FR-018) | FR-004, FR-018, FR-020 |
| `_get_all_step_ids(config)` | MODIFIED: `annotate-deviations` and `deviation-analysis` IDs added in correct pipeline positions | FR-038 |
| `_save_state(config, results)` | MODIFIED: `remediation_attempts` counter logic added | FR-039 |
| `_check_remediation_budget(config, max_attempts)` | NEW | FR-040 |
| `_print_terminal_halt(config, state)` | NEW | FR-042 |
| `_auto_invoke_validate(config)` | UNCHANGED | — |
| `_save_validation_status(config, status)` | UNCHANGED | — |
| `_format_halt_output(results, config)` | UNCHANGED | — |
| `_dry_run_output(steps)` | UNCHANGED | — |
| `_print_step_start(step)` | UNCHANGED | — |
| `_print_step_complete(result)` | UNCHANGED | — |

**Implementation note**: The six symbols marked RETIRED (FR-055) constitute approximately 130
lines of code. Their deletion is a v2.25 correctness requirement, not a cleanup optimization.
Leaving them in place with v2.25 code will result in dead code with incorrect implicit semantics
(the `spec_fidelity_failed` trigger block would reference a STANDARD gate that almost never
fails, and `_apply_resume_after_spec_patch()` would shadow the new --resume mechanism).

---

## ISSUE 5 (W-4+W-5, MAJOR/MINOR): NFR-006 Incomplete + No FR for Spec-Patch Trigger Update

### Problem Restatement

NFR-006 (§14.2) currently reads:

> "The downgrade from STRICT to STANDARD SHALL be a relaxation. Any pipeline run that passed the
> STRICT gate SHALL also pass the STANDARD gate."

This statement is true and necessary, but it is incomplete in a critical way: it describes only
the "passes STRICT → passes STANDARD" direction. It is entirely silent on the behavioral flip for
runs that previously FAILED STRICT: those runs now PASS STANDARD. This is not a safety concern
— it is the explicit intent of the downgrade — but its behavioral consequence is significant:
pipeline runs that previously blocked on `high_severity_count > 0` now succeed at spec-fidelity
and proceed to `deviation-analysis`. An operator whose pipeline was blocked in v2.24.x will
observe their pipeline "suddenly working" at spec-fidelity in v2.25 without any change to their
spec or roadmap. NFR-006 must acknowledge this to prevent confusion and incorrect debugging
(e.g., an operator assuming the STANDARD pass means their deviations were fixed, when actually
the blocking semantics moved downstream to `DEVIATION_ANALYSIS_GATE`).

Separately, there is no FR explicitly governing the spec-patch cycle trigger condition update.
The prompt for this brainstorm references a new FR-055 as the home for the spec-patch retirement
(Issue 1 Approach A), which this document has drafted above. That assignment is confirmed here.
The trigger change needs an FR because it is a behavior change in `execute_roadmap()` that
tests will need to cover and implementors will need to verify.

### Full Analysis

**NFR-006 current text** (§14.2):
> The downgrade from STRICT to STANDARD SHALL be a relaxation. Any pipeline run that passed the
> STRICT gate SHALL also pass the STANDARD gate. Existing state files with `spec-fidelity: PASS`
> remain valid.

**What is missing**:
1. The behavioral flip: runs that FAILED STRICT now PASS STANDARD. This is the dominant behavioral
   change for operators. Not stating it invites misinterpretation.
2. The downstream implication: a STANDARD pass at spec-fidelity means the deviation-analysis step
   now runs (it did not run in v2.24.x, where the pipeline halted at spec-fidelity STRICT before
   reaching deviation-analysis). This is a new pipeline stage for all runs that previously halted.
3. The spec-patch connection: with spec-fidelity STANDARD, `spec_fidelity_failed` is almost never
   True, which means the spec-patch auto-resume cycle no longer fires. NFR-006 is where this
   connection should be surfaced (pointing to FR-055 for the retirement).

**What FR-055 should say**:
FR-055 was drafted in Issue 1 as the FR governing retirement of the spec-patch cycle. It belongs
in §8.7 (new subsection, per Issue 1 Approach A recommendation). Its scope is:
- Remove `_apply_resume_after_spec_patch()` and related code from executor.py
- Remove `auto_accept` parameter from `execute_roadmap()` signature
- Document retirement rationale

**Where FR-055 goes**: §8 (Resume Logic Modifications), as new §8.7. This is natural because §8
covers all resume-related behavior changes. The spec-patch cycle is a resume mechanism, so its
retirement belongs alongside the other resume logic changes (§8.1–8.6).

### Draft Spec Language

**Updated NFR-006 (replaces existing §14.2 text)**:

---

#### 14.2 Spec-Fidelity Gate Downgrade: Relaxation and Behavioral Consequences

**NFR-006**: The downgrade of `SPEC_FIDELITY_GATE` from STRICT to STANDARD enforcement tier
(FR-014, FR-015) is a relaxation with the following behavioral consequences:

**(a) Forward compatibility**: Any pipeline run that passed the STRICT gate (i.e., produced a
`spec-fidelity.md` with `high_severity_count == 0` and passing semantic checks) will also pass
the STANDARD gate. Existing `.roadmap-state.json` files with `spec-fidelity: PASS` remain valid
and will be correctly skipped by `--resume`. No migration of existing state files is required.

**(b) Behavioral flip for previously-failing runs**: Pipeline runs that previously FAILED at the
STRICT `spec-fidelity` gate (because `high_severity_count > 0`) will now PASS the STANDARD gate.
This is the intended behavior: the blocking responsibility has moved from spec-fidelity to the new
`DEVIATION_ANALYSIS_GATE` (STRICT, §5.5). A STANDARD pass at spec-fidelity does NOT mean
deviations were fixed — it means the pipeline proceeds to `deviation-analysis`, which classifies
the deviations and routes them to remediation. Operators whose pipelines previously blocked at
spec-fidelity will observe the pipeline proceeding through spec-fidelity and halting (or passing)
at `deviation-analysis` instead. This is correct v2.25 behavior.

**(c) Spec-patch auto-resume dormancy**: With spec-fidelity STANDARD, the `spec_fidelity_failed`
boolean in `execute_roadmap()` is almost never True. The v2.24.2 spec-patch auto-resume cycle
(`_apply_resume_after_spec_patch()`) is therefore effectively dormant. This cycle is formally
retired in v2.25 per FR-055. See §8.7 for the retirement specification and §14.7 for the
backward-compat summary.

**(d) Existing state file compatibility**: `.roadmap-state.json` files written by v2.24.2 pipelines
that contain `spec-fidelity: FAIL` are valid inputs to v2.25 `--resume`. The STANDARD gate will
pass the existing output file on resume (since it checks only frontmatter presence), allowing
the resume to proceed to `deviation-analysis`. This is the intended `--resume` behavior.

---

**FR-055 (new, §8.7)**:

The full FR-055 text was drafted in Issue 1 above. For cross-reference, its assignment is confirmed:

- **FR-055 location**: §8.7 (new subsection "Spec-Patch Auto-Resume Cycle: Retirement")
- **FR-055 scope**: Retirement of `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`,
  `initial_spec_hash`, `_spec_patch_cycle_count`, and `auto_accept` parameter from `execute_roadmap()`
- **FR-055 rationale**: SPEC_FIDELITY_GATE downgraded to STANDARD means `spec_fidelity_failed`
  is almost never True; the spec-patch auto-resume cycle is dormant and misleading; retirement
  removes ~130 lines of dead code and eliminates the "two resume mechanisms" confusion

**Note on FR numbering**: FR-055 is already assigned in the current spec to the `ALL_GATES`
registry update (§3.5: "The `ALL_GATES` registry in `gates.py` SHALL be updated to include
entries for both `annotate-deviations` and `deviation-analysis` gates"). The spec-patch
retirement FR must therefore be assigned FR-059 (next available after FR-058, the secondary
guard FR drafted in Issue 2). Confirm assignment during spec merge.

**Revised FR numbering recommendation for Issue 5**:

- FR-055: ALL_GATES registry update (existing, keep as-is per §3.5 FR-054 / §3.5 FR-055 text)
- FR-056: `_routing_consistent_with_slip_count()` semantic check (Issue 2 Approach A)
- FR-057: `DEVIATION_ANALYSIS_GATE` third semantic check (Issue 2 Approach A)
- FR-058: `deviations_to_findings()` secondary guard (Issue 2 defense-in-depth)
- FR-059: Spec-patch auto-resume cycle retirement (Issue 1 Approach A — was labeled FR-055 in
  this document's §8.7 draft; corrected here to FR-059 to avoid collision)

**Corrected §8.7 header** (replacing "FR-055" with "FR-059" throughout the §8.7 draft above):

All instances of "FR-055" in the Issue 1 §8.7 draft language and the §14.7 draft language should
read "FR-059." The §11.5 table (Issue 4) should also reference FR-059, not FR-055.

---

## Consolidated FR/NFR List

The following table lists every new FR and NFR drafted in this brainstorm document. All are
additive to the existing v2.25 spec. Section references indicate where the language should be
inserted.

| Number | Type | Title | Insert Location | Issue |
|--------|------|--------|-----------------|-------|
| FR-056 | FR | `_routing_consistent_with_slip_count()` semantic check function | §5.5, after DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-057 | FR | DEVIATION_ANALYSIS_GATE gains third semantic check (`routing_consistent_with_slip_count`) | §5.5, replaces DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-058 | FR | `deviations_to_findings()` secondary guard: raise ValueError if fix_ids empty and slip_count > 0 | §7.2, inside deviations_to_findings() listing | W-ADV-1 |
| FR-059 | FR | Spec-patch auto-resume cycle retirement: delete `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, local vars, `auto_accept` param | New §8.7 | W-1 |
| NFR-006 | NFR | Spec-fidelity downgrade: forward compat, behavioral flip, spec-patch dormancy, state file compat (full replacement) | §14.2 (replaces existing text) | W-4+W-5 |
| NFR-011 | NFR | Spec-patch auto-resume cycle not present in v2.25; operators use explicit --resume | New §14.7 | W-1 |
| NFR-012 | NFR | No v2.25 pipeline step reads dev-*-accepted-deviation.md; format consumed only by accept-spec-change CLI | New §14.8 | W-3 |

Additionally, the following spec locations require structural additions (no new FR/NFR numbers):

| Location | Type | Content | Issue |
|----------|------|---------|-------|
| §3.1 (new subsection; renumber 3.1–3.5 → 3.2–3.6) | Taxonomy table | Deviation artifact taxonomy: spec-deviations.md vs dev-*-accepted-deviation.md | W-3 |
| §11.5 (new subsection) | Compatibility table | v2.24.2 → v2.25 executor.py symbol disposition map (RETIRED / UNCHANGED / MODIFIED / NEW) | W-2 |
| §14.7 (new subsection) | Backward-compat note | Spec-patch auto-resume retirement summary and operator migration guidance | W-1 |
| §14.8 (new subsection) | Backward-compat note | Deviation artifact taxonomy cross-reference; NFR-012 | W-3 |

### FR Number Collision Note

The existing spec assigns **FR-054** (§3.5) as the ALL_GATES registry update, and **FR-055**
appears in some spec drafts as a second ALL_GATES-related entry. Before inserting FR-056 through
FR-059 from this brainstorm, the implementor MUST verify the highest existing FR number in the
merged spec and assign the new FRs sequentially from that point. The numbers FR-056 through
FR-059 in this document are provisional and assume FR-054 is the current maximum. If FR-055 is
also used, the new FRs shift to FR-057 through FR-060.

### Summary: Pre-Implementation Actions Required

Before v2.25 implementation begins, the following spec amendments must be merged into
`v2.25-spec-merged.md`:

1. **W-1 (CRITICAL)**: Insert §8.7 (FR-059 retirement) and §14.7 (NFR-011 compat note). Update
   §14.2 (NFR-006 full replacement). Update §11.5 RETIRED rows (FR-059 reference).

2. **W-ADV-1 (CRITICAL)**: Insert `_routing_consistent_with_slip_count()` function (FR-056) and
   update `DEVIATION_ANALYSIS_GATE` definition (FR-057) in §5.5. Add secondary guard to
   `deviations_to_findings()` (FR-058) in §7.2.

3. **W-3 (MAJOR)**: Insert §3.1 taxonomy table (renumber 3.1–3.5 to 3.2–3.6). Insert §14.8
   cross-reference (NFR-012).

4. **W-2 (MAJOR)**: Insert §11.5 compatibility surface table.

5. **W-4+W-5 (MAJOR/MINOR)**: Replace §14.2 with updated NFR-006 text. Confirm FR-059 number
   (spec-patch retirement).

Issues 1 and 2 are CRITICAL and block implementation of executor.py and gates.py respectively.
Issues 3, 4, and 5 are documentation amendments that should be merged before implementation review.
