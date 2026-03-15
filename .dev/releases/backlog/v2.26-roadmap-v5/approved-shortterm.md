---
## ISSUE 1 (Y-2, MAJOR): Three undocumented helper functions in `deviations_to_findings()`

### Recommended Approach
**Approach A — Body-text parsing with structured markdown table contract.**

Rationale:
1. Markdown tables are the most LLM-reliable structured format. All existing spec
   artifacts (`spec-deviations.md`, `deviation-analysis.md`) already use markdown
   tables for their machine-readable classification sections.
2. No new dependencies. The existing pipe-split pattern used across the codebase
   is sufficient.
3. The spec-fidelity prompt already instructs the agent to produce structured
   output. Mandating a table section is a minimal addition to the existing FR-016
   prompt instructions.
4. Approach A is consistent with how `_parse_routing_list()` and
   `_extract_deviation_classes()` should work — all three helpers operate on
   markdown table or frontmatter patterns that the existing codebase already handles.

The key implementation requirement: the spec-fidelity prompt must explicitly
instruct the agent to produce a `## Deviations Found` section with the exact
6-column table. This must be stated in FR-016 or a new FR-016a.

For `_parse_routing_list()`: reads from frontmatter (already fully specified via
FR-045 flat comma-separated fields). The spec gap is only the edge-case
specification.

For `_extract_deviation_classes()`: reads from the body classification table in
`deviation-analysis.md` (Section 5.4 body format). The spec gap is the parser
specification for the 5-column table.

### Draft Spec Language
---

**Add as new §7.2a after the `deviations_to_findings()` code stub (before §7.3):**

**§7.2a Helper Function Specifications**

**FR-060**: The `_extract_fidelity_deviations(content: str) -> dict[str, dict]` function
SHALL parse the `spec-fidelity.md` body for a deviation table in the following format,
returning a dict keyed by deviation ID.

Required table header (case-insensitive column names, pipe-delimited):
```
| ID | Severity | Description | Location | Evidence | Fix Guidance |
```

Parsing rules:
1. Scan content line by line for a line containing at least the substrings
   `ID`, `Severity`, `Description`, `Location`, `Evidence`, `Fix Guidance`
   (case-insensitive) separated by pipe characters.
2. The separator row (containing only `-` and `|`) is skipped.
3. For each subsequent pipe-delimited row with 6 or more non-empty pipe-separated
   columns, extract: `col[0]` → `id`, `col[1]` → `severity`, `col[2]` → `description`,
   `col[3]` → `location`, `col[4]` → `evidence`, `col[5]` → `fix_guidance`.
   All values are stripped of leading/trailing whitespace.
4. Extra columns beyond index 5 are silently ignored (forward compatibility).
5. Rows with fewer than 6 pipe-separated tokens after stripping are skipped with
   a `logging.warning()` call identifying the row number.
6. If no header row matching the pattern is found, the function returns `{}`.
7. The function MUST NOT raise exceptions. All parse errors produce empty entries
   or skipped rows, never propagated exceptions.

The spec-fidelity prompt (FR-016) SHALL be updated to explicitly require a
`## Deviations Found` section containing this table. When `spec_deviations_path` is
provided, the table SHALL include only deviations not excluded by pre-approval.

**FR-061**: The `_parse_routing_list(content: str, field_name: str) -> list[str]`
function SHALL parse a comma-separated value from `spec-fidelity.md` or
`deviation-analysis.md` frontmatter and return a list of stripped, non-empty
deviation ID strings.

Parsing rules:
1. Call `_parse_frontmatter(content)`. If `None`, return `[]`.
2. Look up `field_name` in the resulting dict. If absent, return `[]`.
3. Split the value on `,`. Strip whitespace from each token.
4. Filter out empty tokens (handles trailing commas and fields with only whitespace).
5. Filter out tokens that do not match `r'^[A-Z]+-\d+'` (deviation ID pattern).
   Log a `logging.warning()` for each rejected token.
6. Return the filtered list. Return `[]` if no valid IDs remain.

Edge cases:
- `routing_fix_roadmap:` (empty value) → `[]`
- `routing_fix_roadmap: DEV-001,  ,DEV-003` → `["DEV-001", "DEV-003"]`
- `routing_fix_roadmap: DEV-001, invalid-id, DEV-003` → `["DEV-001", "DEV-003"]`
  with a warning for `invalid-id`
- `routing_fix_roadmap: DEV-001,DEV-001` → `["DEV-001", "DEV-001"]` (deduplication
  is the caller's responsibility; the function preserves order)

**FR-062**: The `_extract_deviation_classes(content: str) -> dict[str, str]` function
SHALL parse the deviation classification table in the `deviation-analysis.md` body
(§5.4 format) and return a dict mapping deviation ID to classification string.

Required table header (case-insensitive, pipe-delimited):
```
| ID | Original Severity | Classification | Debate Ref | Routing |
```

Parsing rules:
1. Scan content line by line for a header matching the pattern above (at least
   columns `ID` and `Classification` must be present; column positions are
   determined by the header order).
2. Record the column index of `ID` (0-based) and `Classification`.
3. For each subsequent data row with sufficient columns, extract the value at the
   `ID` column index and the value at the `Classification` column index.
   Strip whitespace from both.
4. Rows with fewer columns than needed to reach either index are skipped with
   a `logging.warning()`.
5. If no header matching the pattern is found, return `{}`.
6. Valid classification values are: `PRE_APPROVED`, `INTENTIONAL`, `SLIP`,
   `AMBIGUOUS`. Values outside this set are stored as-is (caller handles validation).
7. The function MUST NOT raise exceptions.

---

**Amend FR-016 (§4.3) to add the following sentence at the end of the prompt
instructions list:**

> **FR-016a**: When the spec-fidelity prompt produces a fidelity report, it SHALL
> include a `## Deviations Found` section containing a pipe-delimited markdown
> table with the exact header `| ID | Severity | Description | Location | Evidence | Fix Guidance |`.
> The deviation IDs in this table SHALL use the prefix `DEV-` followed by a
> zero-padded three-digit integer (e.g., `DEV-001`). The table SHALL include one
> row per deviation regardless of severity. When `spec_deviations_path` is
> provided, deviations excluded by verified pre-approval SHALL be omitted from
> this table but listed in a separate `## Pre-Approved Deviations (Excluded)` section.

---

## ISSUE 2 (N-1, MAJOR): `deviation-analysis` STRICT gate failure has no recovery runbook

### Recommended Approach
**Combination of Approach A and Approach B.**

Approach A provides the spec-level runbook (required regardless). Approach B
provides the runtime artifact that makes the runbook actionable. Together they
address both the "what do I do" documentation gap and the "I can't find the
relevant information in deviation-analysis.md" UX problem.

Approach C is rejected. OQ-1 resolution stands.

The `AMBIGUOUS_ITEMS.md` artifact writing should be gated on `ambiguous_count > 0`
and implemented as a post-gate-failure hook, not a separate step. It requires no
new Step, GateCriteria, or pipeline primitive — only a new function called from the
gate failure handler.

### Draft Spec Language
---

**Add as new §8.3 (after §8.2, before §8.4):**

**§8.3 Recovering from `deviation-analysis` Gate Failure**

**FR-063**: When `DEVIATION_ANALYSIS_GATE` blocks on `ambiguous_count > 0`, the
pipeline SHALL write an `AMBIGUOUS_ITEMS.md` artifact to the output directory before
halting. This artifact is produced by `_write_ambiguous_items_report()`, which
extracts all AMBIGUOUS-classified deviation entries from the `deviation-analysis.md`
body and formats them as actionable recovery guidance.

**FR-064**: `_write_ambiguous_items_report(deviation_analysis_path: Path, output_dir: Path) -> None`
SHALL be called from the gate failure path when the `no_ambiguous_deviations`
semantic check returns `False`. It SHALL write `AMBIGUOUS_ITEMS.md` to `output_dir`
containing:
1. A summary count of AMBIGUOUS items.
2. Per-item sections (one per AMBIGUOUS deviation ID) containing:
   - The deviation ID and original severity from the classification table.
   - The debate search result excerpt from the `## Classification Evidence` section
     that explains why the item was classified AMBIGUOUS (i.e., the "partially
     discussed / unclear consensus" evidence).
   - A `spec-deviations.md` amendment template stub pre-populated with the
     deviation's ID, formatted as:
     ```markdown
     ### AD-NNN: <deviation description>
     **Debate Citation**: <fill in: D-XX, Round N>
     **Consensus Status**: <fill in: Full consensus | Partial consensus | No consensus>
     **Classification**: <fill in: INTENTIONAL_IMPROVEMENT | INTENTIONAL_PREFERENCE>
     **Rationale**: <fill in>
     ```
3. Instructions for the recovery workflow (see runbook below).

**FR-065**: If `deviation-analysis.md` body parsing fails to extract AMBIGUOUS
item details, `_write_ambiguous_items_report()` SHALL still write `AMBIGUOUS_ITEMS.md`
with the summary count and instructions, noting that per-item details could not be
extracted and directing the user to `deviation-analysis.md` directly.

**Runbook: Recovering from `deviation-analysis` gate failure**

When the pipeline halts with `ambiguous_count > 0`:

Step 1 — Identify AMBIGUOUS items.
  Read `AMBIGUOUS_ITEMS.md` (written to the output directory on gate failure).
  It lists each AMBIGUOUS deviation with its debate search result and why the
  agent could not resolve the classification.
  Alternatively, read `deviation-analysis.md` directly and search for
  `Classification**: AMBIGUOUS` entries in the `## Classification Evidence` section.

Step 2 — Decide the correct classification.
  For each AMBIGUOUS item, determine whether the deviation was intentional:
  - If the debate transcript (in `debate-transcript.md`) contains a relevant
    discussion that the deviation-analysis agent missed: the item is INTENTIONAL.
  - If there is no debate discussion and the deviation is a generation error: the
    item is a SLIP.
  - If you are uncertain, treat it as a SLIP (the safer default: fix the roadmap
    to match the spec).

Step 3 — Provide richer evidence (for INTENTIONAL items).
  Edit `spec-deviations.md` directly. Add a new annotation entry for the AMBIGUOUS
  deviation using the template stub from `AMBIGUOUS_ITEMS.md`. Populate the debate
  citation (D-XX, Round N), consensus status, classification, and rationale.
  This gives the deviation-analysis agent pre-approved evidence to use on re-run.

  Note: `spec-deviations.md` is a pipeline-generated artifact. Direct edits persist
  across `--resume` cycles because `_apply_resume()` skips `annotate-deviations`
  if its STANDARD gate already passes. The user's manual annotation will be present
  when `deviation-analysis` re-runs.

Step 4 — For SLIP items, no edit is needed.
  If an AMBIGUOUS item is actually a SLIP, no change to `spec-deviations.md` is
  required. The deviation-analysis agent will reclassify it as SLIP on re-run
  if the ambiguity evidence in `debate-transcript.md` is reinterpreted more clearly.
  However, if the same debate evidence produces the same AMBIGUOUS result, the user
  may need to append a clarifying comment to `deviation-analysis.md` directly
  (which `_apply_resume()` will re-run since its STRICT gate failed).

  Warning: Direct edits to `deviation-analysis.md` are overwritten when the step
  re-runs. Edits to `spec-deviations.md` persist because its gate passes.
  Always edit `spec-deviations.md`, not `deviation-analysis.md`, for intent evidence.

Step 5 — Re-run with `--resume`.
  After completing steps 3 and/or 4:
  ```
  superclaude roadmap run <spec_file> --resume
  ```
  `_apply_resume()` will skip all steps whose gates pass, including
  `annotate-deviations` (passes because you edited `spec-deviations.md` without
  invalidating its gate), and re-run `deviation-analysis` (fails because
  `ambiguous_count > 0`).

Step 6 — If ambiguity persists after re-run.
  A second re-run with no input changes will produce the same result. If
  `deviation-analysis` remains AMBIGUOUS on a specific deviation after providing
  annotation evidence, the debate transcript may genuinely be insufficient for
  automated resolution. In this case:
  - Treat the item as a SLIP and let remediation fix the roadmap.
  - Or: manually edit the deviation's classification in `deviation-analysis.md`
    to SLIP/INTENTIONAL after the step runs but before the gate check (not
    recommended — the file is overwritten on re-run).
  - Or: file a bug — the deviation-analysis prompt may need stronger disambiguation
    instructions for this pattern of ambiguity.

---

## ISSUE 3 (N-4, MAJOR): `unfixed_details` state field never specified or written

### Recommended Approach
**Approach A — Populate via `_extract_unfixed_findings()` called before `build_certify_metadata()`.**

It is the only approach that does not violate NFR-010, does not add per-step
knowledge to the generic step runner, and produces a fully specified schema.

The key additional spec work is:
1. Define `_extract_unfixed_findings()` completely.
2. Update `build_certify_metadata()` signature.
3. Specify the `unfixed_details` JSON schema for the `certify` state section.

### Draft Spec Language
---

**Replace §8.5 terminal halt paragraph with the following (full replacement of
the `_print_terminal_halt()` spec text and addition of new FRs):**

**FR-042** (amended): When remediation budget is exhausted, `_print_terminal_halt()`
SHALL output to `stderr`: the number of failed attempts, the count of findings still
failing, per-finding details (ID and description) from `unfixed_details` in state,
and manual-fix instructions including the path to the certification report and the
`superclaude roadmap certify --resume` command.

The `unfixed_details` list SHALL be populated by `build_certify_metadata()` (see
FR-066 below). `_print_terminal_halt()` reads `certify.get("unfixed_details", [])`
from state; if empty (e.g., state written by pre-v5 pipeline), it outputs
"(no per-finding details available)" in place of the finding list.

**FR-066**: A `_extract_unfixed_findings(content: str) -> list[dict]` function
SHALL be added to `src/superclaude/cli/roadmap/executor.py`. It parses the
`certification-report.md` per-finding table (already required by the
`per_finding_table_present` semantic check, FR-028) and returns a list of dicts
for findings with `Result == "FAILED"`.

Parsing rules:
1. Locate the table header row matching `| Finding | Severity | Result | Justification |`
   (case-insensitive; the exact check from `_has_per_finding_table()` in `gates.py`).
2. Determine column indices: `Finding` at col 0, `Severity` at col 1, `Result` at
   col 2, `Justification` at col 3. Column index is determined by header order, not
   assumed fixed (forward compatibility).
3. For each data row (matching `| F-\d+ |`), extract the `Result` column value.
4. If `Result.strip().upper() == "FAILED"`, add
   `{"id": finding_col.strip(), "description": justification_col.strip()}` to the
   result list.
5. Return the list. Return `[]` if no table found or no FAILED rows.
6. MUST NOT raise exceptions.

**FR-067**: The `build_certify_metadata()` function signature SHALL be extended to
accept `unfixed_details: list[dict] | None = None`:

```python
def build_certify_metadata(
    status: str,
    findings_verified: int,
    findings_passed: int,
    findings_failed: int,
    certified: bool,
    report_file: str,
    unfixed_details: list[dict] | None = None,  # NEW
) -> dict:
    """Build certify metadata dict for state schema §3.1.

    unfixed_details: list of {"id": str, "description": str} for findings
    with Result=FAILED in the certification report. Populated by calling
    _extract_unfixed_findings() on the certification report content before
    this function is called.
    """
    return {
        "status": status,
        "findings_verified": findings_verified,
        "findings_passed": findings_passed,
        "findings_failed": findings_failed,
        "certified": certified,
        "report_file": report_file,
        "unfixed_details": unfixed_details or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

The caller of `build_certify_metadata()` in the post-pipeline certify flow SHALL:
1. Read `certification-report.md` content after the certify step completes.
2. Call `_extract_unfixed_findings(content)` to get the unfixed details list.
3. Pass the result as `unfixed_details=` to `build_certify_metadata()`.

**FR-068**: The `.roadmap-state.json` `certify` section schema SHALL include
`unfixed_details` as a required field (empty list `[]` when all findings passed):

```json
{
  "certify": {
    "status": "fail | pass",
    "findings_verified": 3,
    "findings_passed": 1,
    "findings_failed": 2,
    "certified": false,
    "report_file": "/abs/path/to/certification-report.md",
    "timestamp": "2026-03-14T10:00:00+00:00",
    "unfixed_details": [
      {"id": "F-002", "description": "Missing PortifyStatus model not added to roadmap §4.2"},
      {"id": "F-003", "description": "8 semantic check function signatures still absent from roadmap §5.2.1"}
    ]
  }
}
```

**NFR-013** (new): `unfixed_details` entries SHALL contain exactly two string fields:
`"id"` (the Finding ID matching `F-\d+` pattern) and `"description"` (the
`Justification` cell text from the certification table, truncated to 500 characters
if necessary). No other fields are required.

---

**Add to Phase 3 deliverables table (§10, Phase 3):**

| # | File | Change |
|---|------|--------|
| (existing) | `src/superclaude/cli/roadmap/executor.py` | Add `_check_remediation_budget()` and `_print_terminal_halt()` |
| 7 (new) | `src/superclaude/cli/roadmap/executor.py` | Add `_extract_unfixed_findings()` |
| 8 (new) | `src/superclaude/cli/roadmap/executor.py` | Update `build_certify_metadata()` signature with `unfixed_details` parameter |
| 9 (new) | `tests/roadmap/test_executor.py` | Tests for `_extract_unfixed_findings()`, `build_certify_metadata()` with unfixed_details |

---

## ISSUE 4 (Y-3, MAJOR): LOW deviation handling in `deviations_to_findings()` unspecified

### Recommended Approach
**Approach A — Explicit exclusion.**

The purpose of `deviation-analysis` is classification for remediation routing.
LOW deviations are informational — they do not block and do not need routing.
Adding them to the pipeline creates noise in the tasklist and requires additional
prompt engineering in `deviation-analysis` to pre-route them. The information
is already available in `spec-fidelity.md` without any pipeline changes.

The FR-034 LOW → INFO mapping is an error of omission: the spec described a
theoretical mapping without considering that LOWs never reach `deviations_to_findings()`.
The mapping should be removed from FR-034 and the severity map in FR-033's code
stub to prevent future confusion.

### Draft Spec Language
---

**Amend FR-021 (§5.3) to add the following sentence:**

> **FR-021** (amended): The deviation-analysis prompt SHALL classify each HIGH and
> MEDIUM deviation into exactly one of: `PRE_APPROVED`, `INTENTIONAL`, `SLIP`, or
> `AMBIGUOUS`. LOW-severity deviations SHALL be explicitly excluded from this
> classification process. The deviation-analysis step SHALL NOT receive LOW deviations
> as input classification targets, and LOW deviation IDs SHALL NOT appear in any
> routing field of `deviation-analysis.md` frontmatter.

---

**Amend FR-034 (§7.2) to replace the severity mapping with:**

> **FR-034** (amended): The severity mapping for `deviations_to_findings()` SHALL be:
> fidelity `HIGH` -> Finding `BLOCKING`, fidelity `MEDIUM` -> Finding `WARNING`.
> LOW-severity deviations are excluded from `deviations_to_findings()` entirely
> and produce no Finding objects. They are informational annotations in
> `spec-fidelity.md` only, visible to developers reviewing the fidelity report,
> but they do not enter the remediation pipeline.
>
> The `severity_map` in `deviations_to_findings()` SHALL therefore be:
> ```python
> severity_map = {"HIGH": "BLOCKING", "MEDIUM": "WARNING"}
> ```
> If a deviation ID from `routing_fix_roadmap` resolves to a LOW-severity deviation
> in the fidelity report (which should not occur per FR-021 but may result from
> a malformed deviation-analysis output), the `.get(severity, "WARNING")` default
> produces a WARNING finding, logged with a warning message identifying the
> inconsistency.

---

**Add new NFR-014 in §14 (Backward Compatibility):**

> **NFR-014**: LOW-severity deviation exclusion is a clarification, not a behavior
> change. Pre-v5 pipelines did not process LOWs. LOW deviations remain in
> `spec-fidelity.md` as informational annotations for manual review. The
> `low_severity_count` frontmatter field in `spec-fidelity.md` is retained and
> continues to be counted. The exclusion applies only to the remediation pipeline.

---

## ISSUE 5 (Y-1, MAJOR): `roadmap_a`/`roadmap_b` variables undefined in §5.2 code snippet

### Recommended Approach
**Approach C** — use the actual path construction inline, consistent with the
`build_deviation_analysis_prompt()` signature in §5.3 which already uses
`roadmap_a_file` and `roadmap_b_file` as parameter names.

This also fixes a secondary inconsistency: the §5.3 function signature uses
`roadmap_a_file` and `roadmap_b_file`, but the §5.2 snippet passes `roadmap_a`
and `roadmap_b`. The corrected snippet should use the same names throughout.

The full corrected snippet uses locally defined variables within the snippet
context, avoiding any dependency on reading other sections.

### Draft Spec Language
---

**Replace the §5.2 code stub (FR-020) entirely with:**

**FR-020** (amended): The `deviation-analysis` step SHALL be inserted in
`_build_steps()` after `spec-fidelity`, with `retry_limit=1`. The step uses
the existing `roadmap_a` and `roadmap_b` path variables already defined earlier
in `_build_steps()` (assigned as `out / f"roadmap-{agent_a.id}.md"` and
`out / f"roadmap-{agent_b.id}.md"` respectively):

```python
# In src/superclaude/cli/roadmap/executor.py, _build_steps()
# The following variable assignments already exist from earlier in _build_steps():
#   agent_a = config.agents[0]
#   agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]
#   roadmap_a = out / f"roadmap-{agent_a.id}.md"
#   roadmap_b = out / f"roadmap-{agent_b.id}.md"
#   diff_file = out / "diff-analysis.md"
#   debate_file = out / "debate-transcript.md"
#   spec_fidelity_file = out / "spec-fidelity.md"
#   deviations_file = out / "spec-deviations.md"  (defined in annotate-deviations step, §3.2)
#
# Add after spec-fidelity step:

deviation_analysis_file = out / "deviation-analysis.md"

# Step 10: Deviation Analysis (NEW -- Scope 1)
Step(
    id="deviation-analysis",
    prompt=build_deviation_analysis_prompt(
        spec_fidelity_file=spec_fidelity_file,
        debate_file=debate_file,
        diff_file=diff_file,
        deviations_file=deviations_file,
        roadmap_a_file=roadmap_a,
        roadmap_b_file=roadmap_b,
    ),
    output_file=deviation_analysis_file,
    gate=DEVIATION_ANALYSIS_GATE,
    timeout_seconds=300,
    inputs=[
        spec_fidelity_file,
        debate_file,
        diff_file,
        deviations_file,
        roadmap_a,
        roadmap_b,
    ],
    retry_limit=1,
),
```

Note: the keyword argument names in `build_deviation_analysis_prompt()` use the
`_file` suffix (e.g., `roadmap_a_file=roadmap_a`) to match the function signature
defined in §5.3. The local variables `roadmap_a` and `roadmap_b` (without suffix)
are Path objects constructed as `out / f"roadmap-{agent_a.id}.md"` and
`out / f"roadmap-{agent_b.id}.md"` from the existing `_build_steps()` preamble.

---

**Add a note at the end of §3.2 (annotate-deviations step construction) to
establish the `deviations_file` variable for cross-step reference:**

> Note: `deviations_file = out / "spec-deviations.md"` is defined in the
> `annotate-deviations` step construction (§3.2) and referenced in both the
> `spec-fidelity` step (§4.4) and `deviation-analysis` step (§5.2). Implementors
> MUST ensure this variable is defined before both downstream step constructors.

---

## ISSUE 6 (W-ADV-2, MAJOR): Stale `spec-deviations.md` when `roadmap.md` manually edited before `--resume`

### Recommended Approach
**Approach C as the primary mechanism, with Approach B's prose documentation as
a fallback explanation.**

Approach C provides automatic, zero-user-action detection for the most common case
(user edits `roadmap.md` after pipeline completion). mtime comparison is imperfect
but adequate for the target use case: manual human edits happen seconds to minutes
after pipeline completion, not within the same second.

Approach A (hash-based) is more robust than mtime but requires:
(a) executor post-processing to inject the hash (a new `_inject_roadmap_hash()` hook),
(b) a new frontmatter field in `ANNOTATE_DEVIATIONS_GATE`,
(c) the mtime-based detection in `_apply_resume()` anyway as a fallback.

Given the mtime approach handles the primary case and the hash approach's additional
complexity cost is non-trivial, Approach C alone is recommended for v2.25.
Approach A can be revisited in v2.26 if mtime-based detection proves insufficient.

### Draft Spec Language
---

**Amend §8.2 to add the following paragraph at the end:**

**FR-069**: `_apply_resume()` SHALL detect manual edits to `roadmap.md` that
invalidate `spec-deviations.md` using mtime comparison. Before the gate check
for the `annotate-deviations` step, `_apply_resume()` SHALL:

1. Check whether `spec-deviations.md` exists. If it does not exist, skip the
   mtime check (the gate check will determine re-run as normal).
2. If `spec-deviations.md` exists, compare `mtime(roadmap.md)` to
   `mtime(spec-deviations.md)`.
3. If `mtime(roadmap.md) > mtime(spec-deviations.md)`, print a warning to stderr
   and force re-run of `annotate-deviations` (set `found_failure = True` at the
   `annotate-deviations` entry, regardless of gate status):

```
WARNING: roadmap.md is newer than spec-deviations.md.
  roadmap.md mtime:          <iso timestamp>
  spec-deviations.md mtime:  <iso timestamp>
  spec-deviations.md may contain stale annotations from the previous roadmap.
  Forcing re-run of annotate-deviations and all subsequent steps.
```

4. If `mtime(roadmap.md) <= mtime(spec-deviations.md)`, proceed with the normal
   gate check (no forced re-run).

**NFR-015**: The mtime comparison in FR-069 uses `Path.stat().st_mtime` (float,
seconds since epoch). On filesystems with 1-second mtime resolution (e.g., HFS+,
FAT32, some NFS mounts), manual edits within the same second as the last pipeline
write may not be detected. This is an accepted limitation. Users on affected
filesystems SHOULD wait at least 2 seconds after pipeline completion before
manually editing `roadmap.md`, or delete `spec-deviations.md` manually before
running `--resume`.

---

**Add to §8.2 after the existing content and before §8.3, a user-facing warning:**

> **Manual roadmap edit guidance**: If you manually edit `roadmap.md` between
> pipeline runs (e.g., to fix a SLIP directly), `spec-deviations.md` becomes
> stale. The `--resume` flag detects this via mtime comparison (FR-069) and forces
> re-annotation automatically in most cases. If detection fails (clock skew,
> same-second edits), manually delete `spec-deviations.md` before running
> `--resume` to guarantee re-annotation:
> ```
> rm <output_dir>/spec-deviations.md
> superclaude roadmap run <spec_file> --resume
> ```

---

**Add FR-069 implementation to Phase 2 deliverables (§10):**

| # | File | Change |
|---|------|--------|
| 15 (new) | `src/superclaude/cli/roadmap/executor.py` | Add mtime staleness check for `spec-deviations.md` in `_apply_resume()` (FR-069) |
| 16 (new) | `tests/roadmap/test_executor.py` | Tests for `spec-deviations.md` mtime staleness detection |

---

## Consolidated FR/NFR List

| ID | Section | Issue | Type | Summary |
|----|---------|-------|------|---------|
| FR-016a | §4.3 | ISSUE 1 | FR | spec-fidelity prompt SHALL produce `## Deviations Found` markdown table with 6-column header |
| FR-060 | §7.2a | ISSUE 1 | FR | Specify `_extract_fidelity_deviations()` — markdown table parser, edge cases, failure behavior |
| FR-061 | §7.2a | ISSUE 1 | FR | Specify `_parse_routing_list()` — comma-separated frontmatter parser, edge cases, ID validation |
| FR-062 | §7.2a | ISSUE 1 | FR | Specify `_extract_deviation_classes()` — deviation classification table parser, edge cases |
| FR-034 (amended) | §7.2 | ISSUE 4 | FR | LOW deviations excluded from `deviations_to_findings()`; remove LOW→INFO mapping; `severity_map` is `{"HIGH": "BLOCKING", "MEDIUM": "WARNING"}` only |
| FR-021 (amended) | §5.3 | ISSUE 4 | FR | Explicitly exclude LOW deviations from `deviation-analysis` classification and routing tables |
| FR-020 (amended) | §5.2 | ISSUE 5 | FR | Replace §5.2 snippet with corrected version using real variable names and keyword arguments matching §5.3 signature |
| FR-063 | §8.3 | ISSUE 2 | FR | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` before halting |
| FR-064 | §8.3 | ISSUE 2 | FR | Specify `_write_ambiguous_items_report()` — extraction of AMBIGUOUS entries, template stubs, failure behavior |
| FR-065 | §8.3 | ISSUE 2 | FR | `_write_ambiguous_items_report()` SHALL still write summary + instructions if body parsing fails |
| FR-066 | §8.5 (amended) | ISSUE 3 | FR | Specify `_extract_unfixed_findings(content: str) -> list[dict]` — FAILED row extraction from certification table |
| FR-067 | §8.5 (amended) | ISSUE 3 | FR | Update `build_certify_metadata()` signature with `unfixed_details: list[dict] | None = None` |
| FR-068 | §8.5 (amended) | ISSUE 3 | FR | Specify `.roadmap-state.json` `certify.unfixed_details` schema — `[{"id": str, "description": str}]` |
| FR-069 | §8.2 (amended) | ISSUE 6 | FR | `_apply_resume()` mtime check: force re-run of `annotate-deviations` if `mtime(roadmap.md) > mtime(spec-deviations.md)` |
| NFR-013 | §8.5 (amended) | ISSUE 3 | NFR | `unfixed_details` entries contain exactly `"id"` and `"description"` string fields; description truncated at 500 chars |
| NFR-014 | §14 | ISSUE 4 | NFR | LOW exclusion is a clarification, not behavior change; `low_severity_count` in spec-fidelity frontmatter retained |
| NFR-015 | §8.2 (amended) | ISSUE 6 | NFR | mtime comparison uses `st_mtime` float; 1-second resolution limitation accepted; workaround documented |

### Phase Assignment for New FRs/NFRs

| Phase | New IDs |
|-------|---------|
| Phase 1 (Scope 2 — Annotation) | FR-016a |
| Phase 2 (Scope 1 — Classification) | FR-021(amended), FR-034(amended), FR-020(amended), FR-060, FR-061, FR-062, FR-063, FR-064, FR-065, FR-069, NFR-014, NFR-015 |
| Phase 3 (Certify Hardening) | FR-042(amended), FR-066, FR-067, FR-068, NFR-013 |
