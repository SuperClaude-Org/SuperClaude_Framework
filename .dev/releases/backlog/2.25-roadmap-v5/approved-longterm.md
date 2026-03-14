---
## ISSUE 1 (W-ADV-2 extended, MAJOR): `roadmap.md` content hash in `spec-deviations.md` for stale-detection

### Recommended Approach

**Approach A, Sub-approach A3** (pre-gate validation hook in `_apply_resume()`).

Rationale:
1. Achieves the detection goal: if roadmap.md changed since annotate-deviations
   ran, the step is re-queued on `--resume`
2. Zero impact on gate architecture, NFR-010 compliance maintained
3. Executor-local change — one new helper function, ~35 lines
4. Requires `roadmap_hash` to be written into `spec-deviations.md` frontmatter
   by the executor (not the LLM), which is safe and precise

The `roadmap_hash` injection uses the same executor-writes-hash pattern already
established for `spec_hash` in `_save_state()`.

### Draft Spec Language

**Insert into §3.2 (Step Construction in `_build_steps()`) after existing FR-004:**

> **FR-055**: After the `annotate-deviations` subprocess completes and
> `_sanitize_output()` runs, the executor SHALL inject a `roadmap_hash` field
> into `spec-deviations.md` frontmatter containing the SHA-256 hex digest of
> `roadmap.md` at the time of injection (same atomic-write pattern as
> `_inject_pipeline_diagnostics()`).
>
> Implementation:
> ```python
> # In roadmap_run_step(), after _sanitize_output():
> if step.id == "annotate-deviations" and step.output_file.exists():
>     _inject_roadmap_hash(step.output_file, config.output_dir / "roadmap.md")
> ```
>
> `_inject_roadmap_hash(output_file, roadmap_path)` reads the current
> frontmatter, adds or overwrites `roadmap_hash: <sha256>`, and writes
> atomically via `.tmp` + `os.replace()`.

**Insert into §3.5 (Gate Definition) after existing FR-013:**

> **FR-070**: The `ANNOTATE_DEVIATIONS_GATE` required frontmatter fields SHALL
> include `roadmap_hash`. A missing or empty `roadmap_hash` field SHALL cause
> the STANDARD gate to fail on structural completeness grounds (existing
> frontmatter field check behavior).

**Insert into §8.2 (Impact of v5 Changes on Resume) after existing FR-038 prose:**

> **FR-071**: `_apply_resume()` SHALL call
> `_check_annotate_deviations_freshness(config, deviations_file)` before
> deciding to skip the `annotate-deviations` step. If the function returns
> `False` (meaning `roadmap_hash` in `spec-deviations.md` does not match the
> current SHA-256 of `roadmap.md`), the step SHALL be re-added to the execution
> queue regardless of whether the STANDARD gate would otherwise pass.
>
> ```python
> def _check_annotate_deviations_freshness(
>     config: RoadmapConfig,
>     deviations_file: Path,
> ) -> bool:
>     """Returns True if spec-deviations.md is fresh for current roadmap.md.
>
>     Returns False if:
>     - spec-deviations.md does not exist
>     - roadmap_hash field is missing or empty
>     - roadmap.md does not exist
>     - SHA-256 of roadmap.md does not match stored roadmap_hash
>     """
>     if not deviations_file.exists():
>         return False
>     content = deviations_file.read_text(encoding="utf-8")
>     fm = _parse_frontmatter(content)
>     if fm is None:
>         return False
>     stored_hash = fm.get("roadmap_hash", "")
>     if not stored_hash:
>         return False
>     merge_file = config.output_dir / "roadmap.md"
>     if not merge_file.exists():
>         return False
>     current_hash = hashlib.sha256(merge_file.read_bytes()).hexdigest()
>     return stored_hash == current_hash
> ```
>
> **NFR-016**: `_check_annotate_deviations_freshness()` SHALL be fail-closed:
> any missing file, missing field, or read error SHALL cause it to return
> `False` (force re-run), not skip. It SHALL NOT raise exceptions.
---

---
## ISSUE 2 (W-ADV-4, MAJOR): Non-integer `remediation_attempts` crashes `_check_remediation_budget()`

### Recommended Approach

**Combined Approach A + B** for v2.25.

- Approach A: defensive `int()` coercion + warning log in `_check_remediation_budget()`
- Approach B: defensive `int()` coercion in `_save_state()` read path

Together these cover both the read and write paths. Implementation cost is
~14 lines total. No new dependencies. No schema changes.

### Draft Spec Language

**Insert into §8.4 (Remediation Cycle Bounding) after existing FR-041:**

> **FR-072**: `_check_remediation_budget()` SHALL coerce `remediation_attempts`
> to `int` before comparison. If the coercion raises `ValueError` or
> `TypeError`, the function SHALL log a WARNING and treat `remediation_attempts`
> as `0` (fresh budget), allowing the current attempt to proceed.
>
> ```python
> raw = remediate.get("remediation_attempts", 0)
> try:
>     attempts = int(raw)
> except (ValueError, TypeError):
>     _log.warning(
>         "remediation_attempts value %r is not a valid integer in "
>         ".roadmap-state.json; treating as 0. State file may be corrupt.",
>         raw,
>     )
>     attempts = 0
> ```
>
> **Rationale**: External tampering or filesystem corruption may produce
> non-integer values. An uncaught TypeError crashing the pipeline is a worse
> outcome than allowing one more attempt. The WARNING log provides observability.

> **NFR-017**: `_save_state()` SHALL coerce `existing_attempts` to `int`
> before incrementing, using `try: int(...) except (ValueError, TypeError): 0`.
> This ensures that `remediation_attempts` is always written as a Python `int`
> to `.roadmap-state.json`, preventing corruption propagation across write
> cycles.
---

---
## ISSUE 3 (W-ADV-3, MAJOR): Deviation ID format not constrained — comma in ID corrupts routing

### Recommended Approach

**Approach A** (constrained ID format + validation in `_parse_routing_list()`
+ `_routing_ids_valid()` semantic check on `DEVIATION_ANALYSIS_GATE`), with the
`total_analyzed` cross-check from Approach D as a warning.

This is the only approach that addresses the root cause (unconstrained ID
format) rather than the symptom (comma as separator). Routing corruption is
prevented at two layers: the STRICT gate blocks non-conforming output from
reaching `deviations_to_findings()`, and `_parse_routing_list()` defensively
filters any tokens that bypass the gate.

### Draft Spec Language

**Insert into §5.4 (Output Format: `deviation-analysis.md`) after existing FR-024:**

> **FR-073**: Deviation IDs in `deviation-analysis.md` SHALL match the pattern
> `DEV-\d+` (e.g., DEV-001, DEV-042). The prompt for `deviation-analysis`
> SHALL instruct the agent to use only deviation IDs as they appear in
> `spec-fidelity.md`, which generates IDs in the `DEV-NNN` format.

**Insert into §5.5 (Gate Definition) after existing FR-026:**

> **FR-074**: A `_routing_ids_valid(content: str) -> bool` semantic check
> function SHALL be added to `gates.py`. The function SHALL:
> 1. Parse the frontmatter of `deviation-analysis.md`
> 2. For each of the four routing fields (`routing_fix_roadmap`,
>    `routing_update_spec`, `routing_no_action`, `routing_human_review`),
>    split the value on commas and validate each non-empty token against
>    `re.compile(r'^DEV-\d+$')`
> 3. Return `False` if any token fails validation; return `True` if all tokens
>    are valid or all routing fields are empty
>
> This check SHALL be registered as a STRICT semantic check on
> `DEVIATION_ANALYSIS_GATE`.

**Modify §7.2 (`deviations_to_findings()`) to add after the `_parse_routing_list()` call:**

> **FR-075**: `_parse_routing_list()` SHALL validate each token against
> `re.compile(r'^DEV-\d+$')`. Non-conforming tokens SHALL be logged as
> WARNING and excluded from the returned list. An empty string token (from
> trailing comma or empty field) SHALL be silently skipped without logging.
>
> Additionally, `_parse_routing_list()` SHALL cross-check `len(returned_tokens)`
> against the `total_analyzed` frontmatter field. If `len(returned_tokens) >
> total_analyzed`, a WARNING SHALL be logged (routing more IDs than were analyzed
> suggests a parse error or duplicate IDs).
---

---
## ISSUE 4 (N-2 extended, MAJOR): Two independent retry counters with no coordination spec

### Recommended Approach

**Approach A** (§8.7 documentation table) **+ Approach D** (§14.7 dormancy note),
with the specific interaction rule from Approach C added to §8.7 prose without
implementing the state schema change.

Rationale:
- The interaction between the two counters is a documentation gap, not a
  behavioral defect: the independent caps already bound total attempts correctly
- A §8.7 table gives implementers and reviewers a clear reference
- The §14.7 dormancy note honestly documents the spec-patch cycle's reduced
  relevance in v5
- The Approach C interaction rule (what `_print_terminal_halt()` says when
  both fire) can be specified in the spec text without implementing the state
  change — making it a v2.26 implementation requirement

### Draft Spec Language

**New §8.7 to insert after §8.6:**

> ### 8.7 Retry Budget Summary and Counter Interaction
>
> The v5 pipeline contains two independent retry mechanisms. They operate on
> different triggers, different storage, and different failure modes.
>
> | Counter | Type | Max | Storage | Trigger | Effective in v5 |
> |---------|------|-----|---------|---------|-----------------|
> | `_spec_patch_cycle_count` | in-memory | 1 per invocation | local var in `execute_roadmap()` | spec-fidelity STANDARD FAIL + deviation files + spec hash change | Rarely (STANDARD gate failures are structural only) |
> | `remediation_attempts` | persisted | 2 | `.roadmap-state.json` | certify FAIL on `--resume` | Yes (primary recovery mechanism) |
>
> **FR-076**: The spec-patch cycle (`_spec_patch_cycle_count`) and the
> remediation budget (`remediation_attempts`) SHALL remain independent in v5.
> No global recovery budget counter is introduced.
>
> **FR-077**: If the spec-patch cycle completes (cycle_count reaches 1) and
> remediation subsequently exhausts its budget (remediation_attempts reaches 2),
> `_print_terminal_halt()` SHALL be called with the standard remediation-
> exhausted message. The message SHALL include a sentence noting that the
> pipeline attempted both automatic recovery mechanisms. The exact wording is:
>
> ```
> Note: A spec-patch auto-resume cycle also occurred before remediation began.
> Both recovery mechanisms are now exhausted. Manual intervention is required.
> ```
>
> Implementation of the "also occurred" note requires `_print_terminal_halt()`
> to receive information about spec-patch cycle history. The state file
> mechanism for this is deferred to v2.26 (see §14.7). For v2.25, this note
> is a specification-only requirement pending implementation.
>
> **NFR-018**: The combined maximum automatic recovery attempts in a single
> pipeline lifetime SHALL NOT exceed 3 (1 spec-patch + 2 remediation). This
> bound is enforced by the independent caps on each counter and requires no
> additional global counter.

**New §14.7 to insert after §14.6:**

> ### 14.7 Spec-Patch Cycle Dormancy in v5
>
> **NFR-019**: The `_apply_resume_after_spec_patch()` function and
> `_spec_patch_cycle_count` counter SHALL be retained unchanged in v5. They
> are not removed and not modified.
>
> With spec-fidelity downgraded to STANDARD in v5 (FR-014), the spec-patch
> cycle's trigger condition fires only when the STANDARD gate fails (missing
> frontmatter or insufficient line count at the spec-fidelity step). HIGH
> deviation count no longer triggers gate failure and therefore no longer
> triggers the spec-patch cycle. The mechanism is functionally dormant in the
> common pipeline path.
>
> The mechanism is retained because:
> 1. It imposes no runtime cost when inactive
> 2. It provides a backstop for unforeseen STANDARD gate failures
> 3. Removing it would require coordinated changes with v2.24.2 deployments
>
> Consumers of v2.25 who observe unexpected spec-patch cycle activation should
> investigate whether `spec-fidelity.md` is missing required frontmatter or
> whether `roadmap.md` is being modified by an external process during pipeline
> execution.
---

---
## Consolidated FR/NFR List

| Number | Type | Section | Summary | v2.25 or v2.26 |
|--------|------|---------|---------|----------------|
| FR-055 | FR | §3.2 | Executor injects `roadmap_hash` into `spec-deviations.md` frontmatter after subprocess completes | v2.25 |
| FR-070 | FR | §3.5 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` | v2.25 |
| FR-071 | FR | §8.2 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping `annotate-deviations`; fail-closed | v2.25 |
| NFR-016 | NFR | §8.2 | `_check_annotate_deviations_freshness()` is fail-closed; missing file/field/error returns False (force re-run), never raises | v2.25 |
| FR-072 | FR | §8.4 | `_check_remediation_budget()` coerces `remediation_attempts` to `int`; logs WARNING on corrupt value; treats corruption as 0 | v2.25 |
| NFR-017 | NFR | §8.4 | `_save_state()` coerces `existing_attempts` to `int` before incrementing; `remediation_attempts` is always written as Python `int` | v2.25 |
| FR-073 | FR | §5.4 | Deviation IDs SHALL match `DEV-\d+`; prompt instructs agent to use only IDs as they appear in `spec-fidelity.md` | v2.25 |
| FR-074 | FR | §5.5 | `_routing_ids_valid(content: str) -> bool` added to `gates.py`; validates all routing field tokens against `^DEV-\d+$`; registered as STRICT check on `DEVIATION_ANALYSIS_GATE` | v2.25 |
| FR-075 | FR | §7.2 | `_parse_routing_list()` validates each token against `^DEV-\d+$`; warns and excludes non-conforming; cross-checks `len(returned_tokens) <= total_analyzed` | v2.25 |
| FR-076 | FR | §8.7 (new) | Spec-patch cycle and remediation budget remain independent; no global budget counter introduced | v2.25 (doc) |
| FR-077 | FR | §8.7 (new) | `_print_terminal_halt()` SHALL include spec-patch-also-fired note when both mechanisms are exhausted; state mechanism deferred to v2.26 | v2.26 (impl) |
| NFR-018 | NFR | §8.7 (new) | Combined max recovery attempts SHALL NOT exceed 3; enforced by independent caps | v2.25 (doc) |
| NFR-019 | NFR | §14.7 (new) | `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5; not removed | v2.25 (doc) |

---
## v2.25 vs. v2.26 Deferral Assessment

### Do in v2.25

**FR-055, FR-070, FR-071, NFR-016 (Issue 1 — roadmap hash stale detection)**

Rationale: The failure mode (stale `spec-deviations.md` silently feeds incorrect
routing to downstream steps) is a correctness defect with no workaround. If a
user edits `roadmap.md` and resumes, the pipeline produces wrong results without
warning. The implementation is ~35 lines in executor.py, one new helper function,
one new required frontmatter field. This is firmly within v2.25 scope alongside
the `annotate-deviations` step implementation.

Cost: low. Risk: very low. Value: high (prevents silent data corruption).

**FR-072, NFR-017 (Issue 2 — non-integer remediation_attempts)**

Rationale: This is a one-step crash defect with a targeted 14-line fix. It
crashes the pipeline with an uncaught exception rather than a controlled halt,
breaking the `sys.exit(1)` contract and losing diagnostic output. Fixing it
requires no architectural changes, no new dependencies, and no spec ambiguity.
This must be in v2.25.

Cost: minimal. Risk: zero. Value: high (correctness).

**FR-073, FR-074, FR-075 (Issue 3 — deviation ID format)**

Rationale: Comma in a deviation ID silently corrupts routing, causing SLIPs to
be skipped in remediation. The STRICT gate check (`FR-074`) prevents malformed
output from reaching `deviations_to_findings()`. The defensive parse filter
(`FR-075`) is defense in depth. Both are pure-function additions to `gates.py`
and executor.py. The `DEVIATION_ANALYSIS_GATE` is new in v2.25 and adding a
new semantic check during initial definition has zero migration cost.

Cost: low (~45 lines). Risk: very low. Value: high (prevents silent data loss).

**FR-076, NFR-018, NFR-019 (Issue 4 — counter interaction documentation)**

Rationale: The §8.7 table and §14.7 dormancy note are documentation-only
changes that cost minutes to add and prevent future implementers from
misunderstanding the retry architecture. Including them in v2.25 alongside the
counter implementation is the natural time to document them.

Cost: documentation only. Risk: zero. Value: medium (long-term maintainability).

### Defer to v2.26

**FR-077 implementation (Issue 4 — `_print_terminal_halt()` dual-mechanism note)**

Rationale: Implementing the "both mechanisms exhausted" note in
`_print_terminal_halt()` requires adding a `spec_patch_attempted` boolean to
`.roadmap-state.json` and a new write call mid-execution in `execute_roadmap()`.
This is disproportionate to the diagnostic value. The scenario (spec-patch fires
AND remediation exhausts) is extremely unlikely in a functioning v5 pipeline.
The spec text (FR-077) is included in v2.25 as a forward requirement; the
implementation is deferred.

Defer to v2.26 with the note "implement state schema extension for
`spec_patch_attempted` tracking."

**Approach C (Issue 1) — Generic input hash tracking for all steps**

Rationale: A pipeline-wide `input_hash` mechanism would provide comprehensive
staleness detection across all steps. For v2.25, the targeted `roadmap_hash`
approach (FR-055/FR-071) is sufficient and correct for the identified failure
mode. The generic mechanism is a v2.26 enhancement that would eliminate the
entire class of stale-artifact problems.

**Formal JSON schema for `.roadmap-state.json` (Issue 2, Approach C)**

Rationale: Schema validation with a library like `jsonschema` adds a runtime
dependency not currently in `pyproject.toml`. The inline coercions in
FR-072 and NFR-017 address the immediate defect without the dependency cost.
A formal schema definition would be appropriate in v2.26 when the state file
has stabilized and all fields from v2.25 are confirmed.

**Separator change (Issue 3, Approaches B/C)**

Rationale: Changing comma to semicolon or space is a cosmetic mitigation that
does not address the root cause (unconstrained ID format). FR-073's regex
constraint eliminates the root cause. The separator change adds a breaking
spec change (8+ locations to update) for no additional protection over Approach A.
Not recommended for any version unless Approach A proves insufficient.
