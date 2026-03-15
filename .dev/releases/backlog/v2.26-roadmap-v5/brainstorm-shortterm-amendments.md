---
title: "v2.25 Spec Amendment Brainstorm: Short-Term Delivery Risk Issues"
version: "2.25.0-amendments-shortterm"
status: draft
scope: "Phase 2 delivery risk — 6 issues from spec panel review"
author: amendment-brainstorm-agent
created: 2026-03-14
source_spec: v2.25-spec-merged.md
issue_count: 6
issue_ids: "ISSUE-1 (Y-2), ISSUE-2 (N-1), ISSUE-3 (N-4), ISSUE-4 (Y-3), ISSUE-5 (Y-1), ISSUE-6 (W-ADV-2)"
---

# v2.25 Spec Amendment Brainstorm: Short-Term Delivery Risk Issues

This document brainstorms targeted amendments to the v2.25 merged spec to address
six Phase-2 delivery risk issues identified by the spec panel review. Each section
provides a full problem restatement, analysis of all approaches with tradeoffs, a
recommended approach with justification, and exact draft spec language ready to
copy-paste.

---

## ISSUE 1 (Y-2, MAJOR): Three undocumented helper functions in `deviations_to_findings()`

### Problem Restatement

FR-033 specifies `deviations_to_findings()` with a code stub that calls three helper
functions — `_parse_routing_list()`, `_extract_fidelity_deviations()`, and
`_extract_deviation_classes()` — none of which are defined anywhere in the spec.
`_extract_fidelity_deviations()` is the highest-risk gap: it must parse
LLM-generated `spec-fidelity.md` body text, where format variance is a real threat.
Without a format contract, two separate implementors will write incompatible parsers.
`_parse_routing_list()` and `_extract_deviation_classes()` are also missing their
edge-case and failure behavior definitions. Together, these omissions make Phase 2
unimplementable from the spec alone.

### Approaches Considered

#### Approach A — Body-text parsing with structured markdown table contract

Pin `spec-fidelity.md` body format as a mandatory machine-parseable markdown table.
`_extract_fidelity_deviations()` is specified as a table parser that reads rows from
a table with header `| ID | Severity | Description | Location | Evidence | Fix Guidance |`.

**Format contract**:
```markdown
## Deviations Found

| ID | Severity | Description | Location | Evidence | Fix Guidance |
|----|----------|-------------|----------|----------|--------------|
| DEV-001 | HIGH | Missing data models | roadmap.md §4.2 | Section 4.2 absent | Add PortifyStatus, PortifyOutcome, PortifyStepResult |
| DEV-002 | MEDIUM | Wrong module name | roadmap.md §3.1 | cli.py not commands.py | Rename cli.py to commands.py |
```

`_extract_fidelity_deviations()` scans the content for lines matching
`| <ID> | <SEVERITY> | ...` (pipe-delimited, at least 6 columns), skipping the
header separator row, and returns `dict[str, dict]` keyed by deviation ID.

**Tradeoffs**:
- LLM compliance risk: The spec-fidelity prompt must explicitly require this exact
  table. Any prose deviation (e.g., the LLM adds a footnote column, wraps a cell
  with bold markers) can break column-count parsing. The parser must be lenient about
  extra columns but strict about the first six.
- Parser complexity: Moderate. A pipe-split regex loop is ~20 lines. Column alignment
  and cell whitespace trimming are needed.
- Versioning: Adding a column in a future spec version requires a parser update. The
  spec must be clear about column ordering being load-bearing.
- Failure behavior: If no valid table is found, return empty dict. If a row has fewer
  than 6 columns, skip it with a log warning. Caller sees empty dict → returns empty
  findings list.
- Prompt alignment: Approach A requires modifying the spec-fidelity prompt to
  mandate the table. This is a Phase 1 deliverable; the table format must be
  specified in FR-016/FR-017 territory.

#### Approach B — Frontmatter-only machine interface

Move all machine-readable deviation data into `spec-fidelity.md` frontmatter as a
YAML list. Body is human-readable prose only. `_extract_fidelity_deviations()` reads
from frontmatter only using `_parse_frontmatter()` — but `_parse_frontmatter()`
cannot handle multi-line YAML lists. This approach requires either extending
`_parse_frontmatter()` to use `yaml.safe_load` or adding a new frontmatter parser.

**Format contract**:
```yaml
---
high_severity_count: 3
deviations:
  - id: DEV-001
    severity: HIGH
    description: "Missing data models"
    location: "roadmap.md §4.2"
    evidence: "Section 4.2 absent from roadmap"
    fix_guidance: "Add PortifyStatus, PortifyOutcome, PortifyStepResult"
  - id: DEV-002
    severity: MEDIUM
    ...
---
```

**Tradeoffs**:
- LLM compliance risk: HIGH. Multi-line YAML lists in frontmatter are reliably
  produced by LLMs only when the prompt is extremely explicit about the format.
  A single quoting error (e.g., an unescaped colon in a description) invalidates
  the entire frontmatter block. The spec fidelity agent is already under cognitive
  load; adding structured YAML list generation increases error rate.
- Parser complexity: Requires `yaml.safe_load` or a hand-rolled multi-line
  frontmatter parser. `_parse_frontmatter()` in `gates.py` does simple `key: value`
  splitting (line 144-148 of gates.py); it cannot parse multi-line values.
  Extending it adds complexity to a shared utility used by all gates.
- Versioning: Adding a field to each deviation requires only a comment update.
  Clean extensibility.
- Failure behavior: If `yaml.safe_load` fails, the entire deviation list is lost.
  Fail-closed is correct but harsh — a single malformed field nukes all deviations.
- Adds `yaml` dependency: `yaml.safe_load` is stdlib (`import yaml` is not; requires
  PyYAML). The project uses no YAML parser currently. This approach introduces a
  new dependency.

This approach is high-risk for LLM compliance and introduces a dependency. Not
recommended for v2.25.

#### Approach C — Hybrid: delimited YAML block in body

Require a structured YAML block in the `spec-fidelity.md` body (not frontmatter)
delimited by `<!-- deviations:start -->` / `<!-- deviations:end -->` HTML comment
markers. The parser extracts only the delimited region, then calls `yaml.safe_load`
on it. The rest of the body is unstructured prose.

**Format contract**:
```markdown
<!-- deviations:start -->
- id: DEV-001
  severity: HIGH
  description: "Missing data models"
  location: "roadmap.md §4.2"
  evidence: "Section 4.2 absent"
  fix_guidance: "Add PortifyStatus, PortifyOutcome, PortifyStepResult"
<!-- deviations:end -->
```

**Tradeoffs**:
- LLM compliance risk: MEDIUM. The LLM must produce the correct HTML comment markers
  and valid YAML list within them. Markers are distinctive enough to be reliably
  reproduced. YAML inside the block is scoped to just the list, so a parse error
  is isolated.
- Parser complexity: Two-pass: find marker boundaries, then `yaml.safe_load` on the
  extracted block. ~25 lines.
- Versioning: Same clean extensibility as Approach B.
- Failure behavior: If markers not found, return empty dict. If `yaml.safe_load`
  fails, return empty dict with logged error. Isolated failure.
- Still requires `yaml.safe_load` / PyYAML dependency.
- Prompt alignment: Prompt must explicitly specify the marker syntax. Forgetting the
  closing marker is a common LLM failure mode.

Approach C is better than B but still introduces a YAML parser dependency and a
two-pass extraction that adds complexity.

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

**FR-056**: The `_extract_fidelity_deviations(content: str) -> dict[str, dict]` function
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

**FR-057**: The `_parse_routing_list(content: str, field_name: str) -> list[str]`
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

**FR-058**: The `_extract_deviation_classes(content: str) -> dict[str, str]` function
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

### Problem Restatement

When `ambiguous_count > 0`, the `DEVIATION_ANALYSIS_GATE` (STRICT) blocks the
pipeline. The spec explains the blocking decision rationale (§5.6) but gives the
user zero guidance on what to do next. `ambiguous_count` is not a field the user
can set directly — it is produced by the LLM deviation-analysis agent. The user
cannot fix it without understanding which deviations are AMBIGUOUS and why the agent
could not classify them. Without a recovery path, a single AMBIGUOUS classification
becomes a permanent, opaque blocker — reproducing the exact failure mode the v2.25
spec is designed to solve.

### Approaches Considered

#### Approach A — Documented runbook in §8.3

Add a §8.3 section to the spec titled "Recovering from deviation-analysis gate
failure" with numbered step-by-step instructions. This is a pure documentation fix
requiring no code changes.

**Mechanism**: The user reads the `deviation-analysis.md` body's `## Classification
Evidence` section, which already contains per-deviation reasoning (§5.4 format).
AMBIGUOUS deviations will have entries explaining why the agent could not decide.
The user then has two options:
1. Provide richer evidence: add intent documentation to `spec-deviations.md` that
   the annotate-deviations agent can use to strengthen classification on re-run.
2. Accept that the pipeline needs a `--resume` to re-run `deviation-analysis` with
   the same inputs — which will produce the same result unless inputs change.

The runbook must be honest about option 2's limitations: if nothing changes,
`--resume` alone will not resolve AMBIGUOUS items. The user must update some input
artifact first.

**What "updating intent evidence" means in practice**: The `spec-deviations.md`
artifact is writable by the user. Adding a new deviation annotation entry (AD-NNN)
for an AMBIGUOUS item, with a debate citation and rationale, gives the
deviation-analysis agent fresh evidence to reclassify from AMBIGUOUS to
PRE_APPROVED or INTENTIONAL. The user edits `spec-deviations.md` directly,
then runs `--resume` (which will re-run `deviation-analysis` since its gate fails).

**Risk**: The user may not understand that editing `spec-deviations.md` is the
correct intervention. The runbook must be concrete.

**UX**: Requires the user to read the failure output, find the right file, and make
targeted edits. Cognitive load is non-trivial for unfamiliar users.

#### Approach B — `AMBIGUOUS_ITEMS.md` artifact written on gate failure

When `DEVIATION_ANALYSIS_GATE` blocks on `ambiguous_count > 0`, the pipeline
executor writes a structured `AMBIGUOUS_ITEMS.md` artifact to the output directory
listing each AMBIGUOUS deviation with its full classification reasoning and a
template for the user to fill in.

**Mechanism**: After the gate check fails, a new `_write_ambiguous_items_report()`
function reads `deviation-analysis.md`, extracts all AMBIGUOUS deviation entries
from the `## Classification Evidence` section, and writes `AMBIGUOUS_ITEMS.md` with:
- Per-AMBIGUOUS-item sections showing: deviation ID, original severity, the debate
  search result that produced "partially discussed / unclear consensus", and suggested
  resolution steps.
- A template `spec-deviations.md` amendment stub for each item that the user can
  copy-paste to add a manual annotation.
- Instructions on how to use `--resume` after completing the stubs.

**Spec language required**:
- New FR specifying `_write_ambiguous_items_report()` and when it runs
- Extension to the gate failure handling path in the executor
- New field in `deviation-analysis.md` frontmatter (or body parsing) to identify
  AMBIGUOUS items

**Risk**: Adds ~50 lines of production code for a failure path. The function must
parse `deviation-analysis.md` body text to extract AMBIGUOUS evidence sections —
which requires the same body-text parsing infrastructure as ISSUE 1. If the body
format is not machine-parseable (or the agent produces inconsistent AMBIGUOUS
sections), the artifact may be empty or misleading.

**UX**: Significantly better. The user gets a concrete, actionable file pointing
directly at the problem.

#### Approach C — `--accept-ambiguous` flag routing to `human_review`

Revisit OQ-1's "no" resolution. Add a `--accept-ambiguous` CLI flag that, when
provided, causes the pipeline to route all AMBIGUOUS deviations to `human_review`
disposition instead of blocking. The gate check is modified: with
`--accept-ambiguous`, `ambiguous_count > 0` is allowed. The `human_review`
routing list is populated with the AMBIGUOUS IDs; they are excluded from
`fix_roadmap` (no remediation attempted). A warning is printed.

**Risk**: This directly contradicts OQ-1's rationale: "AMBIGUOUS means the
classifier cannot decide. The pipeline should halt for human review, not guess."
The `human_review` routing produces findings that are never acted on by the
automated pipeline. The user still has to manually fix the AMBIGUOUS deviations —
but now the pipeline has proceeded past the ambiguity, possibly remediating other
findings while the AMBIGUOUS ones remain unresolved. This creates an incomplete
remediation state that is worse than a clean halt.

**Risk classification**: HIGH. OQ-1 was correctly resolved. `--accept-ambiguous`
silently degrades pipeline correctness. Not recommended.

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

**FR-059**: When `DEVIATION_ANALYSIS_GATE` blocks on `ambiguous_count > 0`, the
pipeline SHALL write an `AMBIGUOUS_ITEMS.md` artifact to the output directory before
halting. This artifact is produced by `_write_ambiguous_items_report()`, which
extracts all AMBIGUOUS-classified deviation entries from the `deviation-analysis.md`
body and formats them as actionable recovery guidance.

**FR-060**: `_write_ambiguous_items_report(deviation_analysis_path: Path, output_dir: Path) -> None`
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

**FR-061**: If `deviation-analysis.md` body parsing fails to extract AMBIGUOUS
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

### Problem Restatement

`_print_terminal_halt()` reads `certify.get("unfixed_details", [])` from
`.roadmap-state.json` (§8.5 code stub, line reading `unfixed_details`). No FR
specifies when this field is populated, by what code path, or what its schema
looks like. The `build_certify_metadata()` function in the existing `executor.py`
(lines 730-750) does not include `unfixed_details` as a parameter. The
`CERTIFY_GATE` checks structural completeness and `certified: true` but does not
require the `unfixed_details` to be written anywhere. The result: `unfixed_details`
will always be `[]` at runtime, making the per-finding detail in the terminal halt
message permanently empty and useless.

### Approaches Considered

#### Approach A — Populate in `_save_state()` after certify metadata is passed

After the certify step completes, the caller of `_save_state()` passes
`certify_metadata` which includes `unfixed_details`. The `_save_state()` function
stores it. The populate step is: after certify runs and before `_save_state()` is
called, parse `certification-report.md` to extract FAILED finding rows and build
the `unfixed_details` list.

This requires the certify result consumer (the post-pipeline flow) to extract
unfixed findings from the certification report and pass them to
`build_certify_metadata()` as a new `unfixed_details` parameter.

**Extraction logic**: Parse `certification-report.md` body for the per-finding
table. For each row where the `Result` column value (case-insensitive) is `FAILED`,
extract the `Finding` ID (first column) and `Justification` (fourth column). Build
`[{"id": "F-001", "description": "justification text"}, ...]`.

**Schema**:
```json
"certify": {
  "status": "fail",
  "findings_verified": 3,
  "findings_passed": 1,
  "findings_failed": 2,
  "certified": false,
  "report_file": "/path/to/certification-report.md",
  "timestamp": "2026-03-14T10:00:00+00:00",
  "unfixed_details": [
    {"id": "F-002", "description": "Missing PortifyStatus model not added"},
    {"id": "F-003", "description": "semantic check functions still absent"}
  ]
}
```

**Where parsing happens**: A new `_extract_unfixed_findings(content: str) -> list[dict]`
function in `executor.py`. It reads the `| Finding | Severity | Result | Justification |`
table (already required by `_has_per_finding_table()` semantic check) and returns
only FAILED rows.

**Tradeoffs**: Clean separation. `_save_state()` just stores what it's given.
Parsing is colocated with the certify post-processing logic. The `build_certify_metadata()`
function signature must change — but it is called from only one place in the
post-pipeline flow (to be implemented in Phase 3).

#### Approach B — Populate in the certify step runner

The `roadmap_run_step()` function detects when the step ID is `"certify"`, and after
the step completes successfully, calls `_extract_unfixed_findings()` on the output
file, storing results in a `metadata` field on `StepResult`.

**Tradeoffs**: Requires coupling `roadmap_run_step()` to certify-specific parsing
logic. `roadmap_run_step()` currently has one certify-specific branch already
(the `_inject_pipeline_diagnostics` call for `extract`), so this pattern exists.
However, the spec explicitly states NFR-010: "Neither `pipeline/executor.py` nor
`pipeline/models.py` SHALL be modified." `roadmap_run_step()` is in
`cli/roadmap/executor.py` (not `pipeline/`), so NFR-010 does not technically
apply — but adding per-step knowledge to a generic step runner is poor design.
`StepResult` does not have a `metadata` field and adding one would be a model
change.

#### Approach C — Pass through `StepResult.metadata`

Add a `metadata: dict = field(default_factory=dict)` field to `StepResult`. The
certify step runner sets `result.metadata["unfixed_details"] = [...]`.
`_print_terminal_halt()` reads from `StepResult.metadata` rather than from state.

**Tradeoffs**: `StepResult` is in `pipeline/models.py`. Adding a field there violates
NFR-010 ("pipeline/models.py SHALL NOT be modified"). This approach is spec-prohibited.

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
FR-062 below). `_print_terminal_halt()` reads `certify.get("unfixed_details", [])`
from state; if empty (e.g., state written by pre-v5 pipeline), it outputs
"(no per-finding details available)" in place of the finding list.

**FR-062**: A `_extract_unfixed_findings(content: str) -> list[dict]` function
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

**FR-063**: The `build_certify_metadata()` function signature SHALL be extended to
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

**FR-064**: The `.roadmap-state.json` `certify` section schema SHALL include
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

**NFR-011** (new): `unfixed_details` entries SHALL contain exactly two string fields:
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

### Problem Restatement

FR-021 states that `deviation-analysis` classifies "each HIGH and MEDIUM deviation."
FR-034 defines the severity mapping including `fidelity LOW -> Finding INFO`. But LOW
deviations are never processed by `deviation-analysis` — the step only receives HIGH
and MEDIUM deviations. The routing table in `deviation-analysis.md` frontmatter
(`routing_fix_roadmap`, etc.) will therefore never contain LOW deviation IDs. Yet
FR-034's LOW → INFO mapping suggests LOW deviations should appear as INFO findings.
There is a contradiction: the deviation-analysis step is defined to exclude LOWs,
but `deviations_to_findings()` includes a mapping for them. Implementors will make
different choices about what to do with LOWs, creating runtime bugs in the remediation
pipeline. The spec must resolve this explicitly.

### Approaches Considered

#### Approach A — Explicit exclusion: LOW deviations never enter the pipeline

Add a definitive sentence to FR-034 and FR-021 stating that LOW deviations are
excluded from `deviation-analysis` and from `deviations_to_findings()`. The
`LOW -> INFO` mapping in FR-034 is removed or reframed as "not applicable."
LOW deviations remain visible in `spec-fidelity.md` as informational annotations
but never enter the remediation pipeline.

**Impact on `deviations_to_findings()`**:
The `severity_map` in FR-033's code stub can simply omit `"LOW"`. If a LOW deviation
ID somehow appears in `routing_fix_roadmap` (which should not happen per FR-021),
it produces a WARNING-severity finding (the `.get(dev.get("severity", ""), "WARNING")`
default). The implementor does not need to handle LOW as a special case.

**Impact on certify gate counts**:
No impact. `findings_verified` counts only findings produced by `deviations_to_findings()`.
LOW deviations produce no findings, so `findings_verified` does not include them.

**Tradeoffs**:
- Simplest, most unambiguous resolution.
- LOWs are purely diagnostic. Existing `spec-fidelity.md` already reports them;
  making them invisible to the remediation pipeline matches their informational intent.
- One concern: if a LOW deviation accumulates over releases without remediation,
  technical drift increases silently. This is a product design question, not a v2.25
  scope question. The spec can note this as a deferred concern.

#### Approach B — Include LOW as INFO findings with automatic SKIPPED status

Extend FR-021 to include LOW deviations in deviation-analysis classification. LOW
deviations are always routed to `no_action` by default (pre-classification, before
the LLM runs). They appear as INFO findings in the remediation tasklist pre-marked
as SKIPPED.

**Impact on `deviations_to_findings()`**:
Add a second pass after the `fix_ids` loop: for each LOW deviation in
`spec-fidelity.md` (from `_extract_fidelity_deviations()`), create a Finding with
`severity="INFO"` and `status="SKIPPED"`. These findings are added to the list
but never processed by the remediation agent.

**Impact on certify gate counts**:
SKIPPED findings are excluded from `findings_verified` (per the existing
`_all_actionable_have_status()` semantic check pattern: SKIPPED entries are marked
`- [x]` and excluded from actionable checks). `findings_verified` still excludes
SKIPPED. No impact on certification pass/fail logic.

**Tradeoffs**:
- Adds visibility for LOW deviations in the remediation tasklist.
- Increases tasklist size for every run, even when LOWs are trivial.
- The deviation-analysis step prompt would need to process LOWs differently
  (auto-route to `no_action`) or the `routing_no_action` list would be pre-populated
  with all LOW IDs before the LLM runs. The former requires prompt changes; the
  latter requires a pre-processing step in the executor.
- Complexity cost is moderate. The benefit (visibility of LOWs in tasklist) is
  marginal given they appear in `spec-fidelity.md` already.

#### Approach C — Surfaced in remediate tasklist but non-blocking

A variant of Approach B: LOW deviations appear in `remediation-tasklist.md` as
pre-SKIPPED items produced by `deviations_to_findings()`, but the certify step
explicitly excludes SKIPPED findings from its `findings_verified` count.

This is effectively identical to Approach B. The only distinction is whether the
counting exclusion is explicitly specified (Approach C adds explicit certify
language) vs. implied by existing SKIPPED handling.

The spec already specifies `_all_actionable_have_status()` which excludes `[x]`
(SKIPPED) entries from actionable checks. No additional certify spec language is
needed if SKIPPED findings are already excluded.

Approaches B and C collapse to the same implementation; the difference is only
documentation emphasis.

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

**Add new NFR-012 in §14 (Backward Compatibility):**

> **NFR-012**: LOW-severity deviation exclusion is a clarification, not a behavior
> change. Pre-v5 pipelines did not process LOWs. LOW deviations remain in
> `spec-fidelity.md` as informational annotations for manual review. The
> `low_severity_count` frontmatter field in `spec-fidelity.md` is retained and
> continues to be counted. The exclusion applies only to the remediation pipeline.

---

## ISSUE 5 (Y-1, MAJOR): `roadmap_a`/`roadmap_b` variables undefined in §5.2 code snippet

### Problem Restatement

The §5.2 code stub for the `deviation-analysis` step construction references
`roadmap_a` and `roadmap_b` as arguments to `build_deviation_analysis_prompt()` and
as `inputs`. These variables are not defined in the §5.2 snippet or anywhere in §5
that would give a reader context. In the actual `_build_steps()` function
(executor.py lines 311-317), roadmap output paths are named `roadmap_a` and
`roadmap_b` but are constructed as `out / f"roadmap-{agent_a.id}.md"` and
`out / f"roadmap-{agent_b.id}.md"` respectively — where `agent_a.id` and
`agent_b.id` are the actual agent identifier strings (e.g., `"opus"`, `"haiku"`).
The variable names happen to match, but a reader of the spec cannot know this
without reading `executor.py` source. The spec snippet is orphaned from its context.

**Exact variable assignment from executor.py `_build_steps()` (lines 309-323)**:
```python
agent_a = config.agents[0]
agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]

extraction = out / "extraction.md"
roadmap_a = out / f"roadmap-{agent_a.id}.md"
roadmap_b = out / f"roadmap-{agent_b.id}.md"
diff_file = out / "diff-analysis.md"
debate_file = out / "debate-transcript.md"
score_file = out / "base-selection.md"
merge_file = out / "roadmap.md"
test_strat = out / "test-strategy.md"
spec_fidelity_file = out / "spec-fidelity.md"
```

### Approaches Considered

#### Approach A — Show full variable assignment context in §5.2

Replace the partial §5.2 code stub with a version that includes the full variable
assignment preamble from `_build_steps()`, showing exactly where `roadmap_a` and
`roadmap_b` come from. This is the most self-contained and readable option.

#### Approach B — Add a comment cross-reference

Keep the existing snippet but add a `# roadmap_a, roadmap_b defined in _build_steps() at the output paths section` comment. Add a prose note: "See §3.2 for the full `_build_steps()` variable assignment context." This is minimal but relies on the reader cross-referencing.

#### Approach C — Replace with the actual path construction pattern

Replace `roadmap_a, roadmap_b` in the snippet with their actual computed values,
showing the path construction inline:

```python
roadmap_a_file = out / f"roadmap-{config.agents[0].id}.md"
roadmap_b_file = out / f"roadmap-{config.agents[1].id}.md"
```

And update the `build_deviation_analysis_prompt()` call and `inputs` list to use
`roadmap_a_file` and `roadmap_b_file`. This also fixes the mismatch between the
parameter name `roadmap_a_file` in the `build_deviation_analysis_prompt()` signature
(§5.3, which uses `roadmap_a_file: Path`) and the variable name `roadmap_a` in the
§5.2 snippet.

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

### Problem Restatement

`_apply_resume()` (executor.py lines 1273-1349) skips `annotate-deviations` if
`spec-deviations.md` passes its STANDARD gate. The STANDARD gate checks only
frontmatter field presence and `min_lines=15` — it cannot detect content staleness.
If `roadmap.md` is manually edited between pipeline runs (e.g., the user fixes a
SLIP directly without going through the remediation flow), `spec-deviations.md`
contains classifications from the old roadmap. When `deviation-analysis` then runs,
it receives a fidelity report based on the new roadmap but deviation annotations
based on the old one. Cross-referencing becomes meaningless: a deviation annotated
as INTENTIONAL_IMPROVEMENT in `spec-deviations.md` may no longer exist in the new
roadmap, or a new deviation introduced by the manual edit will lack an annotation.
This is a silent data corruption issue: no error is raised, the pipeline proceeds,
but classification decisions are based on mismatched artifacts.

### Approaches Considered

#### Approach A — `roadmap_hash` in `spec-deviations.md` frontmatter with semantic check

The `annotate-deviations` step is required to write `roadmap_hash: sha256(roadmap.md)`
into `spec-deviations.md` frontmatter. A new semantic check
`_roadmap_hash_matches()` is added to `ANNOTATE_DEVIATIONS_GATE` that recomputes
the hash and returns `False` on mismatch, forcing re-run.

**Implementation challenge**: The existing `SemanticCheck` signature is
`check_fn: Callable[[str], bool]` — it receives only the file content, not the
roadmap file path. A hash check requires knowing the path to `roadmap.md` to
recompute the hash. Two sub-options:

Sub-option A1 — Closure-based check function: The semantic check function is
created as a closure at gate construction time, capturing `merge_file` path from
`_build_steps()`. This requires `ANNOTATE_DEVIATIONS_GATE` to be constructed
dynamically inside `_build_steps()` rather than as a module-level constant.
This is a significant departure from the NFR-005 principle that "Gate criteria are
pure data -- no logic, no imports from pipeline/gates.py enforcement code."

Sub-option A2 — Hash check in `_apply_resume()` directly: `_apply_resume()` already
reads the state file. Add a hash check before the gate check for `annotate-deviations`:
if `spec-deviations.md` frontmatter `roadmap_hash` does not match
`sha256(merge_file)`, force re-run of `annotate-deviations` regardless of gate
status.

Sub-option A2 preserves the module-level constant gate design (no closure needed)
and keeps the detection logic in `_apply_resume()` alongside the existing
`force_extract` stale-spec check pattern.

**Tradeoffs (A2)**:
- Implementation complexity: Moderate. `_apply_resume()` needs to read `roadmap.md`
  and compare with frontmatter `roadmap_hash` from `spec-deviations.md`.
  `_parse_frontmatter()` is importable from `gates.py`. The pattern is identical to
  the existing `force_extract` pattern (lines 1285-1297) which already does hash
  comparison.
- Prompt alignment: The `annotate-deviations` prompt must be updated to write
  `roadmap_hash` into frontmatter. This requires a new required frontmatter field
  in `ANNOTATE_DEVIATIONS_GATE` and a prompt update.
- Gate change: `ANNOTATE_DEVIATIONS_GATE` gains `roadmap_hash` as a required
  frontmatter field.
- Risk: LLMs may write incorrect hash values (they cannot compute SHA-256). The
  hash must be written by the executor post-processing step (like
  `_inject_pipeline_diagnostics` for the extract step), NOT by the LLM. This
  requires a new `_inject_roadmap_hash()` post-processing function called from
  `roadmap_run_step()` when `step.id == "annotate-deviations"`.

#### Approach B — Spec prohibition with mtime detection warning

Add to §8.2: "Manual edits to `roadmap.md` after `annotate-deviations` completes
invalidate `spec-deviations.md`. Before running `--resume` after any manual
roadmap edit, delete `spec-deviations.md` to force re-annotation."

Add a non-blocking mtime check in `_apply_resume()`: if `mtime(roadmap.md) > mtime(spec-deviations.md)`, print a warning but do not force re-run. The gate check still determines whether to skip.

**Tradeoffs**:
- No code changes required beyond the mtime warning.
- Warning relies on filesystem mtime being meaningful. On networked filesystems,
  in Docker volumes, or after `cp` operations, mtime may not reflect edit order.
- More importantly: the warning is a recommendation, not enforcement. A user who
  ignores it proceeds with stale annotations. The warning is easily missed in
  `--resume` output that may contain many lines.
- The instruction "delete `spec-deviations.md`" is easy to follow if documented.
  The problem is discoverability: users will not know to read §8.2 before running
  `--resume`.
- This approach accepts a known data corruption risk in exchange for implementation
  simplicity.

#### Approach C — Invalidation hook in `_apply_resume()`

Before checking the `annotate-deviations` gate, `_apply_resume()` checks
`mtime(roadmap.md)` vs `mtime(spec-deviations.md)`. If `roadmap.md` is newer,
force re-run of `annotate-deviations` (and all subsequent steps) regardless of
gate status.

**Tradeoffs**:
- Clean, automatic, no user action required.
- Relies on mtime: same filesystem reliability concerns as Approach B. mtime-based
  detection is unreliable on some storage backends.
- Over-broad: any write to `roadmap.md` (even automated, e.g., by the pipeline
  itself during a previous run) triggers re-annotation. The pipeline writes
  `roadmap.md` during the `merge` step. On a fresh run this is fine (merge runs
  before annotate-deviations). On `--resume`, if merge was re-run after a previous
  annotate-deviations completion, the mtime relationship would trigger unnecessary
  re-annotation.
- Specifically: after a full run, `roadmap.md` mtime is set when `merge` writes it.
  `spec-deviations.md` mtime is set when `annotate-deviations` writes it. Since
  `annotate-deviations` runs after `merge`, `spec-deviations.md` should always be
  newer than `roadmap.md` after a successful run. mtime comparison correctly
  identifies manual edits to `roadmap.md` that occur after `annotate-deviations`
  completes.
- The main failure mode is clock skew or coarse-grained mtime resolution
  (1-second on some filesystems). A manual edit within the same second as the
  last pipeline write would not be detected.

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

**FR-065**: `_apply_resume()` SHALL detect manual edits to `roadmap.md` that
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

**NFR-013**: The mtime comparison in FR-065 uses `Path.stat().st_mtime` (float,
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
> stale. The `--resume` flag detects this via mtime comparison (FR-065) and forces
> re-annotation automatically in most cases. If detection fails (clock skew,
> same-second edits), manually delete `spec-deviations.md` before running
> `--resume` to guarantee re-annotation:
> ```
> rm <output_dir>/spec-deviations.md
> superclaude roadmap run <spec_file> --resume
> ```

---

**Add FR-065 implementation to Phase 2 deliverables (§10):**

| # | File | Change |
|---|------|--------|
| 15 (new) | `src/superclaude/cli/roadmap/executor.py` | Add mtime staleness check for `spec-deviations.md` in `_apply_resume()` (FR-065) |
| 16 (new) | `tests/roadmap/test_executor.py` | Tests for `spec-deviations.md` mtime staleness detection |

---

## Consolidated FR/NFR List

| ID | Section | Issue | Type | Summary |
|----|---------|-------|------|---------|
| FR-016a | §4.3 | ISSUE 1 | FR | spec-fidelity prompt SHALL produce `## Deviations Found` markdown table with 6-column header |
| FR-056 | §7.2a | ISSUE 1 | FR | Specify `_extract_fidelity_deviations()` — markdown table parser, edge cases, failure behavior |
| FR-057 | §7.2a | ISSUE 1 | FR | Specify `_parse_routing_list()` — comma-separated frontmatter parser, edge cases, ID validation |
| FR-058 | §7.2a | ISSUE 1 | FR | Specify `_extract_deviation_classes()` — deviation classification table parser, edge cases |
| FR-034 (amended) | §7.2 | ISSUE 4 | FR | LOW deviations excluded from `deviations_to_findings()`; remove LOW→INFO mapping; `severity_map` is `{"HIGH": "BLOCKING", "MEDIUM": "WARNING"}` only |
| FR-021 (amended) | §5.3 | ISSUE 4 | FR | Explicitly exclude LOW deviations from `deviation-analysis` classification and routing tables |
| FR-020 (amended) | §5.2 | ISSUE 5 | FR | Replace §5.2 snippet with corrected version using real variable names and keyword arguments matching §5.3 signature |
| FR-059 | §8.3 | ISSUE 2 | FR | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` before halting |
| FR-060 | §8.3 | ISSUE 2 | FR | Specify `_write_ambiguous_items_report()` — extraction of AMBIGUOUS entries, template stubs, failure behavior |
| FR-061 | §8.3 | ISSUE 2 | FR | `_write_ambiguous_items_report()` SHALL still write summary + instructions if body parsing fails |
| FR-062 | §8.5 (amended) | ISSUE 3 | FR | Specify `_extract_unfixed_findings(content: str) -> list[dict]` — FAILED row extraction from certification table |
| FR-063 | §8.5 (amended) | ISSUE 3 | FR | Update `build_certify_metadata()` signature with `unfixed_details: list[dict] | None = None` |
| FR-064 | §8.5 (amended) | ISSUE 3 | FR | Specify `.roadmap-state.json` `certify.unfixed_details` schema — `[{"id": str, "description": str}]` |
| FR-065 | §8.2 (amended) | ISSUE 6 | FR | `_apply_resume()` mtime check: force re-run of `annotate-deviations` if `mtime(roadmap.md) > mtime(spec-deviations.md)` |
| NFR-011 | §8.5 (amended) | ISSUE 3 | NFR | `unfixed_details` entries contain exactly `"id"` and `"description"` string fields; description truncated at 500 chars |
| NFR-012 | §14 | ISSUE 4 | NFR | LOW exclusion is a clarification, not behavior change; `low_severity_count` in spec-fidelity frontmatter retained |
| NFR-013 | §8.2 (amended) | ISSUE 6 | NFR | mtime comparison uses `st_mtime` float; 1-second resolution limitation accepted; workaround documented |

### Phase Assignment for New FRs/NFRs

| Phase | New IDs |
|-------|---------|
| Phase 1 (Scope 2 — Annotation) | FR-016a |
| Phase 2 (Scope 1 — Classification) | FR-021(amended), FR-034(amended), FR-020(amended), FR-056, FR-057, FR-058, FR-059, FR-060, FR-061, FR-065, NFR-012, NFR-013 |
| Phase 3 (Certify Hardening) | FR-042(amended), FR-062, FR-063, FR-064, NFR-011 |
