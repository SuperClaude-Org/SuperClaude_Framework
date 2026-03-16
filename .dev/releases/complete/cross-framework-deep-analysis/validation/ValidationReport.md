# Validation Report
Generated: 2026-03-14
Roadmap: `.dev/releases/current/cross-framework-deep-analysis/roadmap.md`
Phases validated: 9
Agents spawned: 18 (2 per phase)
Total findings: 39 (High: 13, Medium: 14, Low: 13 — actionable Low only; advisory findings omitted)

---

## Findings

### High Severity

#### H1. T01.07 — Phase file count wrong (9 spec'd, roadmap says 8)
- **Severity**: High
- **Affects**: `phase-1-tasklist.md` / T01.07
- **Problem**: Roadmap Key Action 7 says `phase-{1..8}-tasklist.md` — brace expansion = 8 phase files. Task specifies "10 files (9 phase files + index)" in steps and AC.
- **Roadmap evidence**: "`phase-{1..8}-tasklist.md`" — exactly 8 values
- **Tasklist evidence**: Steps and AC: "10 files (9 phase files + index)"
- **Exact fix**: Change all occurrences of "10 files (9 phase files + index)" to "9 files (8 phase files + index)" in T01.07 steps and AC. Update validation direct test accordingly.

#### H2. T01.04 — Five dependency names not enumerated in AC
- **Severity**: High
- **Affects**: `phase-1-tasklist.md` / T01.04
- **Problem**: AC checks for "5 dependency rows" but does not enforce the correct five named dependencies. A document with five arbitrary rows would pass.
- **Roadmap evidence**: "Record dependency readiness state for: Auggie MCP, IronClaude repo access, llm-workflows repo access, prompt/source documents, downstream command expectations (`/sc:roadmap`, `/sc:tasklist`)"
- **Tasklist evidence**: AC: "artifacts/D-0004/spec.md exists with 5 dependency rows" — no enumeration
- **Exact fix**: Replace "5 dependency rows" in T01.04 AC with: "spec.md contains exactly these five named rows: (1) Auggie MCP, (2) IronClaude repo access, (3) llm-workflows repo access, (4) prompt/source documents, (5) downstream command expectations covering /sc:roadmap and /sc:tasklist — each with Status, Evidence source, and Notes columns populated."

#### H3. T01.03 — artifacts/ subdirectory structure not verified (only root)
- **Severity**: High
- **Affects**: `phase-1-tasklist.md` / T01.03
- **Problem**: Roadmap says "Create `artifacts/` output directory structure" implying a multi-level structure. Task only verifies/creates root `artifacts/` directory.
- **Roadmap evidence**: "Create `artifacts/` output directory structure"
- **Tasklist evidence**: Steps: "creating artifacts/ directory" (root only); AC: "directory writable" — no subdirectory structure check
- **Exact fix**: Expand T01.03 steps and AC to verify all expected subdirectories under `artifacts/` are created and writable (not only the root). AC add: "All expected subdirectories under `artifacts/` are created and writable."

#### H4. T02.04 — AC references wrong consumption phases for OQ-002 decision
- **Severity**: High
- **Affects**: `phase-2-tasklist.md` / T02.04
- **Problem**: AC says decision must be "referenced in Phase 3 and Phase 5 files." Phase 5 is Strategy Synthesis; the correct consumption point under tasklist numbering is Phase 4 (Adversarial Comparisons). This creates a traceability gap.
- **Roadmap evidence**: OQ-002 determines pipeline-analysis scope in IC strategy (tasklist Phase 3) and adversarial comparisons (tasklist Phase 4)
- **Tasklist evidence**: T02.04 AC row 4: "referenced in Phase 3 and Phase 5 files"
- **Exact fix**: Change T02.04 AC from "referenced in Phase 3 and Phase 5 files" to "referenced in Phase 3 and Phase 4 files where pipeline-analysis scope is declared."

#### H5. T03.01 — file:line evidence requirement absent from AC (gate hole vs. SC-002)
- **Severity**: High
- **Affects**: `phase-3-tasklist.md` / T03.01
- **Problem**: SC-002 gate requires "file:line evidence attached to strategic claims." T03.01 AC has no criterion for file:line citations — the task can pass with zero citations, leaving a gate hole.
- **Roadmap evidence**: "Gate SC-002: 8 files produced, each with strength-weakness pairing verified and file:line evidence attached to strategic claims"; Phase 2 Key Action 3
- **Tasklist evidence**: T03.01 AC: no mention of file:line; Step 4 references it but not AC
- **Exact fix**: Add to T03.01 AC: "Each strategy-ic-*.md file contains at least one `file:line` citation from Auggie MCP (zero-citation files fail this criterion)." Add to Validation: "Direct test: grep for `file:line` pattern in each of the 8 strategy files; zero matches in any file is a failure."

#### H6. T03.02 — keyword scan narrower than NFR-002 semantic definition
- **Severity**: High
- **Affects**: `phase-3-tasklist.md` / T03.02
- **Problem**: Step 3 uses a fixed keyword list ("advantage", "benefit", "strength", "enables", "improves", "faster", "reliable") to scan for strength claims. NFR-002 is semantic ("any good pattern without stated cost fails review") — the keyword list will miss synonyms like "superior", "robust", "outperforms."
- **Roadmap evidence**: NFR-002: "every strength claim must have a paired weakness/trade-off; any 'good' pattern without stated cost fails review" (semantic, not keyword-based)
- **Tasklist evidence**: Step 3: fixed keyword list as exhaustive scan mechanism
- **Exact fix**: Revise T03.02 Step 3 to: "scan for strength claims using NFR-002 semantic definition ('any good pattern without stated cost'); use keyword hints as a scanning aid, not an exhaustive list; any positive-attribute claim without a paired trade-off is a Fail regardless of phrasing."

#### H7. T05.03 — OQ-004 references Phase 7 instead of roadmap's Phase 6
- **Severity**: High
- **Affects**: `phase-5-tasklist.md` / T05.03
- **Problem**: Roadmap says "Phase 6 shall default to producing an IC-native improvement item." Task consistently replaces "Phase 6" with "Phase 7 (T07.04)." Under the tasklist's +1 phase offset, this may be correct, but must be explicitly documented.
- **Roadmap evidence**: "Phase 6 shall default to producing an IC-native improvement item with explicit rationale"
- **Tasklist evidence**: T05.03 body and AC: "Phase 7 (T07.04) shall produce IC-native improvement item"
- **Exact fix**: Add an explicit mapping note to T05.03: "Note: roadmap names Phase 6; this tasklist's numbering maps roadmap Phase 6 to Phase 7 (T07.04) due to Phase 0→Phase 1 renumbering." Also update D-0020/notes.md AC to: "references the roadmap's Phase 6 obligation, fulfilled by tasklist Phase 7 (T07.04)."

#### H8. T06.01 — merged-strategy.md canonical filename absent from AC
- **Severity**: High
- **Affects**: `phase-6-tasklist.md` / T06.01
- **Problem**: Roadmap consistently refers to the output as `merged-strategy.md`. T06.01 AC only references `artifacts/D-0022/spec.md`. T06.04 then references "update merged-strategy.md" — creating an unresolvable file reference.
- **Roadmap evidence**: "Synthesize all 8 comparison verdicts into `merged-strategy.md`" (Key Action 1); referenced throughout Key Actions 2–5 and gate criteria by this name
- **Tasklist evidence**: T06.01 AC: only `artifacts/D-0022/spec.md` — `merged-strategy.md` never appears
- **Exact fix**: Add to T06.01 AC: "The deliverable is produced as `artifacts/merged-strategy.md` (or `artifacts/D-0022/spec.md` is explicitly aliased as `merged-strategy.md` with a documented mapping in the index); downstream tasks referencing `merged-strategy.md` resolve to this artifact."

#### H9. T07.01 — AC omits "change description" as required per-item field
- **Severity**: High
- **Affects**: `phase-7-tasklist.md` / T07.01
- **Problem**: Roadmap Key Action 1 requires "Specific file paths and change description" per improvement item. T07.01 AC lists "file paths, P-tier, effort, rationale" but omits "change description."
- **Roadmap evidence**: Key Action 1: "Specific file paths and change description"
- **Tasklist evidence**: T07.01 AC: "every improvement item has file paths, P-tier, effort, rationale tracing" — no change description
- **Exact fix**: Add "change description" to T07.01 AC: "every improvement item has file paths, change description, P-tier, effort, rationale tracing to named merged strategy principle."

#### H10. T08.03 — "Phase 2" should be "Phase 1" for completeness dimension
- **Severity**: High
- **Affects**: `phase-8-tasklist.md` / T08.03
- **Problem**: Roadmap Key Action 3 item 4: "Completeness: all Phase 1 components represented in improvement plans." Task step 4 says "all Phase 2 components represented" — direct factual contradiction.
- **Roadmap evidence**: Key Action 3 item 4: "all Phase 1 components represented"
- **Tasklist evidence**: T08.03 step 4: "all Phase 2 components represented"
- **Exact fix**: Change T08.03 step 4 from "Phase 2 components" to "Phase 1 components" in both the step text and AC criterion.

#### H11. T08.03 — Disqualifying Conditions absent from steps and AC
- **Severity**: High
- **Affects**: `phase-8-tasklist.md` / T08.03
- **Problem**: Roadmap Key Action 4 defines four Disqualifying Conditions (items must be reworked, not approved): (1) evidence unverifiable, (2) copied mass in adoption, (3) broken cross-artifact lineage, (4) implementation-scope drift. None appear in T08.03 steps or AC.
- **Roadmap evidence**: Key Action 4: "Disqualifying conditions (items failing any of these must be reworked, not approved)"
- **Tasklist evidence**: T08.03: no reference to disqualifying conditions
- **Exact fix**: Add to T08.03 steps: "For each item, evaluate against four disqualifying conditions: (1) unverifiable evidence, (2) copied mass in adoption recommendations, (3) broken cross-artifact lineage, (4) implementation-scope drift. Any triggered condition classifies the item Fail-Rework." Add to AC: "All four disqualifying conditions evaluated per item; zero items approved with an unresolved disqualifying condition."

#### H12. T08.05 — "all file paths verified" gate criterion absent from steps and AC
- **Severity**: High
- **Affects**: `phase-8-tasklist.md` / T08.05
- **Problem**: Gate Criteria SC-007 explicitly requires "all file paths verified" as a condition for `final-improve-plan.md`. Neither T08.05 steps nor AC reference file path verification.
- **Roadmap evidence**: Gate Criteria: "`final-improve-plan.md` with corrections applied, all file paths verified"
- **Tasklist evidence**: T08.05 steps and AC: no file path verification step or criterion
- **Exact fix**: Add to T08.05 steps: "Verify all file paths referenced in final-improve-plan.md via Auggie MCP." Add to T08.05 AC: "All file paths in final-improve-plan.md are verified (Gate Criteria SC-007: 'all file paths verified')."

#### H13. T09.02 — Resume test AC allows sprint completion after failure (weakened gate)
- **Severity**: High
- **Affects**: `phase-9-tasklist.md` / T09.02
- **Problem**: Roadmap: "sprint SHALL NOT complete Phase 8 unless `--start 3` succeeds." T09.02 AC failure branch: "evidence records failure cause and corrective action" — permits sprint completion with a documented failure, contradicting the unconditional SHALL NOT.
- **Roadmap evidence**: "sprint SHALL NOT complete Phase 8 unless `--start 3` with Phase 1–2 artifacts present succeeds; this is a mandatory gate condition, not optional QA"
- **Tasklist evidence**: AC: "if initially fails, evidence records failure cause and corrective action" — does not require ultimate pass
- **Exact fix**: Replace failure branch AC with: "If resume test fails: sprint completion is blocked; D-0036/evidence.md records failure cause and corrective action taken; test MUST be re-executed and pass before T09.03 and T09.04 may proceed."

---

### Medium Severity

#### M1. T01.01 — `path_verified` artifact schema is invented (not roadmap-sourced)
- **Exact fix**: Replace artifact criterion with roadmap-aligned language: "evidence that both repos returned a valid codebase-retrieval query response is recorded in a durable artifact; fallback annotation included if either query failed per OQ-008 definition."

#### M2. T01.03 — "non-empty" check weaker than roadmap's "readable" requirement
- **Exact fix**: Change T01.03 AC to: "artifacts/prompt.md exists, has file read permissions confirmed, and content is successfully read (not just non-zero line count)."

#### M3. T01.05 — cross-reference targets wrong phases (Phase 3+4 instead of Phase 2+3)
- **Exact fix**: Change T01.05 AC from "referenced in Phase 3 and Phase 4 files" to "referenced in Phase 2 and Phase 3 files" (OQ-006 governs Phase 2/3 scheduling per roadmap).

#### M4. T01.06 — "ANY condition met" trigger semantics omitted from AC
- **Exact fix**: Add to T01.06 AC: "notes.md must explicitly record that fallback triggers on the first ANY condition met (not on multiple simultaneous conditions)."

#### M5. T02.02 — ≥11 LW component floor not in AC block (only in Validation hint)
- **Exact fix**: Add explicit AC criterion: "Dual-status table contains ≥11 rows (one per LW component), satisfying gate SC-001 minimum."

#### M6. T03.01 — Sub-Agent Delegation "None" contradicts AC-012 concurrent recommendation
- **Exact fix**: Change T03.01 Sub-Agent Delegation from "None" to "Recommended" to match roadmap AC-012 guidance and the task's own Step 5.

#### M7. T04.02 — "Phase 2 paths" should be "Phase 1 paths"
- **Exact fix**: Replace "verified Phase 2 paths" with "verified Phase 1 paths (D-0009)" in T04.02 deliverable description and steps.

#### M8. T04.03 — OQ-008 criterion reference missing from LW fallback annotation AC
- **Exact fix**: Add to T04.03 AC: "Fallback-annotated claims explicitly state the OQ-008 criterion that triggered fallback (consistent with T03.03 enforcement for IC strategy files)."

#### M9. T06.02 — "at least one" component reference weakens "explicitly preserved/all relevant"
- **Exact fix**: Change T06.02 AC from "each section has at least one named IC component group reference" to "each section references all IC component groups identified as relevant to that principle (completeness, not minimum-one)."

#### M10. T06.03 — "undocumented" check omits "with justification" qualifier
- **Exact fix**: Change T06.03 AC from "zero undocumented discards" to "zero discard decisions without both documentation and explicit justification; each entry states what was discarded and why."

#### M11. T08.01 — "AC-010 schema" is invented (not in roadmap)
- **Exact fix**: Replace "AC-010 schema" references in T08.01 with "schema expectations from the `/sc:roadmap` command definition." Remove the invented AC-010 identifier.

#### M12. T08.01 — D-0030 findings not bound to validation-report.md in AC
- **Exact fix**: Add to T08.01 AC: "D-0030 findings are referenced in validation-report.md (D-0033) per Gate Criteria requirement."

#### M13. T08.04 — corrections list placed in validation-report.md AC; belongs in T08.05
- **Exact fix**: Remove "list of reworked items with corrections" from T08.04 validation-report.md AC. Replace with: "failed items listed with Fail classification and disqualifying condition reference for T08.05 consumption."

#### M14. T08.05 — no AC confirming final plan is /sc:roadmap schema-compliant
- **Exact fix**: Add to T08.05 AC: "final-improve-plan.md is confirmed schema-compliant with `/sc:roadmap` expectations established in D-0030, satisfying Gate Criteria pre-validation requirement."

---

### Low Severity

#### L1. T01.02 — "CLI version documented" is invented content
- **Exact fix**: Remove "CLI version documented" from T01.02 AC; it is not a roadmap gate requirement.

#### L2. T01.01 — fallback annotation doesn't reference OQ-008 definition
- **Exact fix**: Add to T01.01 AC: "If query fails, annotation references OQ-008 multi-criteria definition (resolved in T01.06): unavailable if timeout, 3 consecutive failures, or coverage confidence <50%."

#### L3. T01.06 — downstream impact not documented
- **Exact fix**: Note in T01.06 AC that the decision record must document downstream impact: "Phase 7 citation flagging if Auggie restored."

#### L4. T02.01 — system qualities in Step 5 from wrong phase
- **Exact fix**: Remove Step 5 (system qualities) from T02.01 or annotate it as forward-looking from Phase 3 scope, not a Phase 2 inventory gate requirement.

#### L5. T03.01 — Auggie MCP absent from MCP Requirements field
- **Exact fix**: Change T03.01 MCP Requirements from "Preferred: Sequential, Context7" to "Preferred: Auggie MCP (primary evidence), Sequential, Context7."

#### L6. T03.03 — "Fallback Allowed: No" contradicts roadmap's controlled-degradation model
- **Exact fix**: Change T03.03 "Fallback Allowed: No" to "Fallback Allowed: Controlled (annotated per OQ-008)." Remove "Fallback Not Allowed" from Notes.

#### L7. T05.01 — five verdict class values not enumerated in AC
- **Exact fix**: Expand T05.01 AC to: "explicit verdict class drawn from five permitted values: IC stronger / LW stronger / split by context / no clear winner / discard both."

#### L8. T05.04 — default case (count=8) lacks AC closure requirement
- **Exact fix**: Add to T05.04 AC: "If count equals 8, D-0021/notes.md explicitly states that Phase 1 inventory (D-0008) revealed no critical gap requiring expansion."

#### L9. T06.02 — five heading names not specified verbatim in AC
- **Exact fix**: Add to T06.02 AC: "Headings match roadmap-specified names exactly: 'Evidence integrity', 'Deterministic gates', 'Restartability', 'Bounded complexity', 'Scalable quality enforcement'."

#### L10. T07.02 — "without justification" escape clause weakens ordering rule
- **Exact fix**: Remove escape clause from T07.02 AC; change "no file has P3 items before P0 without justification" to "no file has P3 items before P0."

#### L11. T07.03 — AC doesn't confirm SC-006 total of 9 documents
- **Exact fix**: Add to T07.03 AC: "Gate SC-006 satisfied: 8 component improve-*.md files confirmed present (D-0026) plus this master document equals 9 total required documents."

#### L12. T08.02 — gate scope AC omits "not a formatting pass" negative definition
- **Exact fix**: Expand T08.02 AC gate scope to: "gate scope declared as 'formal architecture review, not a formatting pass or compliance scan.'"

#### L13. T09.04 — script preference rationale absent from Steps
- **Exact fix**: Add to T09.04 steps: "The script is the strongly preferred path (low effort relative to manual review of 35+ artifacts per roadmap); only fall back to manual protocol if script cannot be produced and document why."

---

## Verification Results
Verified: 2026-03-14
Scope: Phase 8 (T08.01–T08.05) and Phase 9 (T09.01–T09.04) regenerated from scratch with all patches applied.
Findings resolved (Phase 8+9 scope): 10/10

| Finding | Status | Notes |
|---------|--------|-------|
| H10 | RESOLVED | T08.03 step 6 and AC now read "Phase 1 components" — grep confirmed at lines 140, 155 |
| H11 | RESOLVED | Four Disqualifying Conditions added to T08.03 step 9 and AC; 23 occurrences of "Disqualifying Condition" in phase-8 file |
| H12 | RESOLVED | T08.05 step 5 adds Auggie MCP file path verification; AC criterion added citing SC-007 |
| M11 | RESOLVED | "AC-010 schema" removed from T08.01 steps and AC; replaced with "/sc:roadmap command definition"; only appears in Notes annotation |
| M12 | RESOLVED | T08.01 step 7 and AC now require D-0030 findings referenced in validation-report.md (D-0033) |
| M13 | RESOLVED | T08.04 AC changed from "corrections list" to "Fail classification and Disqualifying Condition reference for T08.05 consumption" |
| M14 | RESOLVED | T08.05 AC now confirms final-improve-plan.md is schema-compliant with /sc:roadmap expectations per D-0030 |
| L12 | RESOLVED | T08.02 Why field, steps 4-5, step 7, and AC now all include "not a formatting pass or compliance scan" |
| H13 | RESOLVED | T09.02 step 6 and AC failure branch now unconditionally block sprint completion; "MUST be re-executed and pass" before T09.03/T09.04 proceed |
| L13 | RESOLVED | T09.04 step 2 now states "the script is the strongly preferred path"; fallback requires documented rationale |

Findings in scope but NOT in Phase 8/9 (deferred to phases 1-7 patch cycle): H1-H9, M1-M10, L1-L11
