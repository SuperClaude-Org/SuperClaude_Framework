# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 4: Specification Rewrite with Executable Instructions

**Phase Goal**: Eliminate specification ambiguity by converting every action verb in the
`sc:roadmap` SKILL.md pipeline into a glossary-backed tool-call instruction, and by removing all
remaining pseudo-CLI syntax from `adversarial-integration.md`. Phase 4 has three tasks: adding
the verb-to-tool glossary (which also satisfies the coverage audit for Waves 0–4), fixing Wave
1A step 2 to use the same Skill tool invocation pattern established in Phase 2, and converting
the pseudo-CLI syntax in `adversarial-integration.md` to Skill tool call format. The third task
carries a hard dependency on Phase 3 Task T03.03 because both tasks modify the same file.

Phase 4 depends on Phase 2 (Skill tool must be in allowed-tools for glossary-consistent
invocations to be meaningful) and on Phase 3 Task T03.03 (same-file conflict on
`adversarial-integration.md`). T04.01 and T04.02 may begin as soon as Phase 2 is complete.
T04.03 must wait for T03.03 to complete.

**Roadmap milestone**: M4 — Specification Rewrite with Executable Instructions
**Deliverable IDs covered**: D-0015 through D-0018
**Estimated effort**: M (medium)
**Risk level**: Low
**Phase dependencies**: Phase 2 complete (M2); Phase 3 T03.03 complete (file conflict constraint)

---

## T04.01 — Add Execution Vocabulary Glossary Before Wave 0

**Roadmap Item ID(s)**: R-019, R-020, R-021
**Deliverable IDs**: D-0015, D-0016

**Why**: The `sc:roadmap` SKILL.md currently uses verbs like "Invoke", "Dispatch", "Read ref",
and "Write artifact" without mapping them to specific tool calls. An agent executing the spec
must infer which tool to use, leading to inconsistent behavior. The Execution Vocabulary glossary
makes these mappings explicit and authoritative. By placing the glossary before Wave 0, it is
visible to an agent before any pipeline step is encountered. R-021 requires that every verb used
in Waves 0–4 appears in the glossary — this task satisfies both the glossary creation (D-0015)
and the coverage audit (D-0016) in a single pass.

**Effort**: S
**Risk**: Low
**Risk Drivers**: The glossary is an additive section. The main risk is incomplete coverage —
a verb used in Waves 0–4 that is not listed in the glossary would violate D-0016. The coverage
audit (Step 4) mitigates this risk.

**Tier**: STANDARD
**Tier Confidence**: 75%
**Tier Confidence Bar**: [=======...] 75%
**Tier Rationale**: `add new section to spec file` maps to STANDARD (implement, add keywords).
The `docs/*.md` context booster would push toward EXEMPT, but this file contains executable
instructions that the running agent interprets as tool operations — it is not pure documentation.
STANDARD is correct. Confidence is 75% (not higher) because the coverage audit step introduces
scope uncertainty: the number of verbs in Waves 0–4 is not pre-counted.

**Requires Confirmation**: Yes — confidence is 75%, below the 85% no-confirmation threshold.
Before beginning, count the distinct action verbs in Waves 0–4 of `sc-roadmap/SKILL.md` and
confirm the planned glossary entries cover all of them. If additional entries are needed, add
them to the glossary before marking Step 3 complete.
**Critical Path Override**: None — T04.02 depends on this task (same file, glossary must
exist before step 2 is rewritten to reference it).

**Verification Method**: Direct test execution
**Verification Command**:
```
grep -c "Execution Vocabulary" src/superclaude/skills/sc-roadmap/SKILL.md
# Expected: >= 1 (glossary section present)

grep -n "Wave 0" src/superclaude/skills/sc-roadmap/SKILL.md | head -1
# Use to confirm glossary appears before the first Wave 0 heading
```

**MCP Requirements**: Sequential (verb-extraction and coverage analysis across Waves 0–4)
**Fallback Allowed**: Yes — if Sequential is unavailable, manually scan each Wave section for
action verbs and build the glossary from that scan.
**Sub-Agent Delegation**: No — single-file section addition

---

**Artifacts**:
- `src/superclaude/skills/sc-roadmap/SKILL.md` (modified — new "Execution Vocabulary" section inserted before Wave 0)

**Deliverables**:
- D-0015: "Execution Vocabulary" section exists in `src/superclaude/skills/sc-roadmap/SKILL.md`
  before the Wave 0 heading, containing a mapping table for at minimum: "Invoke skill" → Skill
  tool call, "Dispatch agent" → Task tool call, "Read ref" → Read tool call on a `refs/` path,
  "Write artifact" → Write tool call. A scope statement specifies that the glossary covers
  actionable step instructions in Waves 0–4 only.
- D-0016: Audit confirms 100% coverage — every action verb used in Waves 0–4 of SKILL.md
  appears in the glossary.

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-roadmap/SKILL.md` in full. Identify: (a) the position
   of the Wave 0 heading (insertion point for the glossary), (b) all action verbs used in steps
   across Waves 0–4. Create a verb inventory list.

2. [ANALYZE] Review the verb inventory and confirm it includes at minimum the four core verbs
   from the sprint-spec: "Invoke skill", "Dispatch agent", "Read ref", "Write artifact". Identify
   any additional verbs in Waves 0–4 that require glossary entries.

3. [WRITE] Insert "Execution Vocabulary" section immediately before the Wave 0 heading in
   `src/superclaude/skills/sc-roadmap/SKILL.md`. The section must contain:

   a. A mapping table with these minimum entries (add more as needed from Step 2):

   | Verb | Tool Call | Notes |
   |------|-----------|-------|
   | Invoke skill | `Skill` tool call with `skill:` parameter | Used when calling another SuperClaude skill |
   | Dispatch agent | `Task` tool call | Used when delegating to a sub-agent |
   | Read ref | `Read` tool call on a path under `refs/` | Used when loading behavioral context from a reference file |
   | Write artifact | `Write` tool call | Used when producing a pipeline output file |

   b. A scope statement immediately following the table:
   > **Scope**: This glossary covers tool-call verbs used in pipeline orchestration steps
   > (Waves 0–4). It does NOT cover prose descriptions, comments, or documentation references —
   > only actionable step instructions that the executing agent must interpret as tool operations.

4. [VERIFY] Perform a coverage audit: for each Wave (0, 1, 1A, 2, 3, 4) in the file, read
   each step's action verb and confirm it appears in the glossary. If any verb is found without
   a glossary entry, add the entry before proceeding. Document the audit result.

5. [VERIFY] Confirm the glossary section appears before the Wave 0 heading by checking that
   the "Execution Vocabulary" heading line number is less than the Wave 0 heading line number.

---

**Acceptance Criteria**:
1. "Execution Vocabulary" section exists in `src/superclaude/skills/sc-roadmap/SKILL.md` and
   appears before the Wave 0 heading in document order.
2. The section contains a mapping table with at minimum 4 entries: "Invoke skill" → Skill,
   "Dispatch agent" → Task, "Read ref" → Read (refs/ path), "Write artifact" → Write.
3. A scope statement explicitly scopes the glossary to Waves 0–4 actionable step instructions,
   excluding prose, comments, and documentation references.
4. Coverage audit (Step 4) confirms 100% of action verbs in Waves 0–4 appear in the glossary —
   documented in the task completion notes.

**Validation**:
1. `grep -c "Execution Vocabulary" src/superclaude/skills/sc-roadmap/SKILL.md` — expected: >= 1.
2. `grep -n "Execution Vocabulary" src/superclaude/skills/sc-roadmap/SKILL.md` and
   `grep -n "Wave 0" src/superclaude/skills/sc-roadmap/SKILL.md | head -1` — confirm glossary
   line number is smaller (appears earlier in file) than Wave 0 line number.

**Dependencies**: Phase 2 complete (T02.01–T02.05). T04.02 depends on this task completing
first (glossary must exist before Wave 1A step 2 is rewritten to be glossary-consistent).
**Rollback**: Remove the inserted "Execution Vocabulary" section. The file existed before this
task; no other content is changed.

**Notes**: The scope statement is mandatory (from T02-synthesis.md gap G6). Without it, the
glossary's intended coverage boundary is ambiguous and implementers may incorrectly apply glossary
constraints to prose sections. The fallback protocol steps (F1, F2/3, F4/5) must also use
glossary-consistent verbs (G7 requirement from T02-synthesis.md) — verify this during Step 4's
coverage audit.

---

## T04.02 — Fix Wave 1A Step 2 Invocation Pattern

**Roadmap Item ID(s)**: R-019, R-022
**Deliverable IDs**: D-0017

**Why**: Wave 1A step 2 currently uses a bare "Invoke sc:adversarial" instruction that does not
reference the Skill tool explicitly. This is inconsistent with the pattern established in Wave 2
step 3d (rewritten in Phase 2), which uses the correct Skill tool call syntax with `skill:`,
`args:`, and `output-dir:` parameters. An agent following Wave 1A would use a different
invocation mechanism than Wave 2 for the same operation, creating unpredictable behavior.
Aligning Wave 1A step 2 to the same pattern as Wave 2 step 3d ensures consistent behavior
across all adversarial invocation points.

**Effort**: S
**Risk**: Low
**Risk Drivers**: Low — targeted single-step rewrite in a spec file. Risk is limited to
introducing a typo in the Skill tool call syntax or omitting the fallback reference.

**Tier**: STANDARD
**Tier Confidence**: 80%
**Tier Confidence Bar**: [========..] 80%
**Tier Rationale**: `modify existing spec section` — update keyword. Single file. Not STRICT
because no schema change; not LIGHT because it changes executable spec behavior.

**Requires Confirmation**: No
**Critical Path Override**: None — T04.02 does not block any subsequent task

**Verification Method**: Direct test execution
**Verification Command**:
```
grep -n "Wave 1A" src/superclaude/skills/sc-roadmap/SKILL.md
# Locate Wave 1A section; then inspect step 2 manually

grep -c "skill.*sc:adversarial\|sc:adversarial.*skill" src/superclaude/skills/sc-roadmap/SKILL.md
# Expected: >= 2 (one in Wave 1A step 2, one in Wave 2 step 3d)
```

**MCP Requirements**: None
**Fallback Allowed**: Yes — if the step 3d pattern cannot be read from Phase 2 output, use the
sprint-spec's Task 2.3 description as the reference pattern.
**Sub-Agent Delegation**: No

---

**Artifacts**:
- `src/superclaude/skills/sc-roadmap/SKILL.md` (modified — Wave 1A step 2 rewritten)

**Deliverables**:
- D-0017: Wave 1A step 2 uses Skill tool call syntax identical in structure to Wave 2 step 3d
  (explicit `skill: "sc:adversarial"` parameter, enumerated `args:`, `output-dir:` reference,
  fallback present or referenced)

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-roadmap/SKILL.md`, specifically Wave 2 step 3d.
   Extract the exact Skill tool call pattern used (parameters, syntax, structure). This is the
   reference pattern for Wave 1A step 2.

2. [READ] Locate Wave 1A step 2 in the same file. Read the current text and identify the
   gap: bare "Invoke" language vs. explicit Skill tool call.

3. [EDIT] Rewrite Wave 1A step 2 to use the Skill tool call pattern from Wave 2 step 3d.
   Preserve the Wave 1A-specific arguments (these may differ from Wave 2 step 3d's arguments
   if Wave 1A calls sc:adversarial with different flags). Do not copy Wave 2's arguments
   verbatim — adapt them to the Wave 1A context.

4. [VERIFY] Confirm Wave 1A step 2 now uses a Skill tool call with an explicit `skill:`
   parameter. Confirm the verb used in the step is present in the Execution Vocabulary glossary
   from T04.01 (the invocation verb should be "Invoke skill" or equivalent glossary entry).

---

**Acceptance Criteria**:
1. Wave 1A step 2 in `src/superclaude/skills/sc-roadmap/SKILL.md` no longer uses bare "Invoke
   sc:adversarial" language — it uses an explicit Skill tool call with `skill: "sc:adversarial"`
   parameter.
2. The Skill tool call pattern in Wave 1A step 2 is structurally identical to Wave 2 step 3d
   (same parameter structure) while using Wave 1A-appropriate argument values.
3. The verb used in Wave 1A step 2 appears in the Execution Vocabulary glossary added by T04.01.
4. `grep -c "skill.*sc:adversarial\|sc:adversarial.*skill" src/superclaude/skills/sc-roadmap/SKILL.md`
   returns >= 2 (confirming the pattern is present in at least two locations).

**Validation**:
1. `grep -n "skill.*sc:adversarial\|sc:adversarial.*skill" src/superclaude/skills/sc-roadmap/SKILL.md` — confirm both Wave 1A and Wave 2 occurrences appear.
2. Manual inspection of Wave 1A step 2 confirms no bare "Invoke" language remains.

**Dependencies**: T04.01 must complete first (glossary must exist before step 2 is verified
as glossary-consistent). Phase 2 must be complete (Skill tool in allowed-tools).
**Rollback**: Revert Wave 1A step 2 to its previous text.

**Notes**: Do not copy Wave 2 step 3d's arguments verbatim unless they are appropriate for
Wave 1A. Wave 1A may invoke sc:adversarial for a different purpose or with different
`--agents` / `--compare` / `--depth` values. The structural pattern must match; the argument
values may differ.

---

## T04.03 — Convert Pseudo-CLI Syntax in adversarial-integration.md to Skill Tool Call Format

**Roadmap Item ID(s)**: R-019, R-023
**Deliverable IDs**: D-0018

**Why**: `adversarial-integration.md` currently contains `sc:adversarial --flag value` pseudo-CLI
syntax in its invocation instructions. An agent reading this file interprets such syntax as a
shell command, not as a Skill tool call — which is incorrect for the Claude Code execution
environment. Converting all pseudo-CLI occurrences to Skill tool call format makes the
integration doc consistent with the sc:roadmap SKILL.md specification and eliminates the
ambiguity that Root Cause RC2 identified as a specification-execution gap.

**Effort**: S
**Risk**: Low
**Risk Drivers**: Low — targeted text substitution. The primary risk is missing an occurrence
(grep validation with expected count 0 mitigates this). Secondary risk: inadvertently converting
`--flag` syntax inside a Skill tool call's `args:` string — those occurrences are valid and
must not be modified.

**Tier**: STANDARD
**Tier Confidence**: 85%
**Tier Confidence Bar**: [========..] 85%
**Tier Rationale**: `modify existing file` — update keyword. Single file. Not STRICT because no
schema change or security domain; not LIGHT because it changes executable spec behavior.

**Requires Confirmation**: No (confidence >= 0.85)
**Critical Path Override**: This task CANNOT begin until T03.03 is complete. Both T04.03 and
T03.03 modify `adversarial-integration.md`. Executing T04.03 before T03.03 risks overwriting
or conflicting with the "Return Contract Consumption" section added in T03.03.

**Verification Method**: Direct test execution
**Verification Command**:
```
grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
# Expected: 0 (all standalone pseudo-CLI invocations converted)
```

**MCP Requirements**: None
**Fallback Allowed**: Yes — if any pseudo-CLI occurrence is structurally ambiguous (cannot
determine if it is a standalone invocation vs. an `args:` string inside a Skill call),
document it as a NOTE inline and flag for manual review rather than converting it incorrectly.
**Sub-Agent Delegation**: No

---

**Artifacts**:
- `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` (modified — pseudo-CLI syntax converted to Skill tool call format)

**Deliverables**:
- D-0018: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
  returns 0. All standalone `sc:adversarial --flag value` invocation patterns have been
  converted to Skill tool call format. Note: `--flag` syntax within `args:` strings inside
  Skill tool calls is valid and is preserved.

---

**Steps**:

1. [READ] Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` in its
   current state (after T03.03 has added the "Return Contract Consumption" section and T03.04
   has added the Tier 1 gate section). Identify every occurrence of `sc:adversarial --` that
   represents a standalone invocation instruction — not an occurrence inside an `args:` string
   of a Skill tool call that may have been introduced in earlier phases.

2. [ANALYZE] For each pseudo-CLI occurrence, determine the intended Skill tool call equivalent:
   - `sc:adversarial --agents X --compare Y --depth Z --output-dir W` becomes a Skill tool
     call with `skill: "sc:adversarial"`, `args: "--agents X --compare Y --depth Z"`,
     `output-dir: W` (or the equivalent parameter structure used in Wave 2 step 3d).
   - Preserve the flag values; only the invocation syntax changes.

3. [EDIT] Replace each standalone pseudo-CLI occurrence with the Skill tool call format.
   Use the same structural pattern as Wave 2 step 3d in `sc-roadmap/SKILL.md` (reference
   T04.02 which confirmed that pattern). Do not modify `--flag` syntax inside `args:` strings
   of Skill tool calls that already exist in the file.

4. [VERIFY] Run `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
   and confirm the result is 0. If any occurrences remain, inspect them: if they are inside
   `args:` strings of a Skill tool call, they are valid and the count should reflect only
   standalone occurrences. Adjust the verification if needed using a more targeted grep pattern.

5. [VERIFY] Confirm the "Return Contract Consumption" section (T03.03) and the Tier 1 gate
   section (T03.04) are intact and unmodified by the pseudo-CLI conversion edits.

---

**Acceptance Criteria**:
1. `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
   returns 0 for standalone pseudo-CLI invocations. (Occurrences within `args:` strings of
   Skill tool calls are explicitly excluded from this count and are valid to retain.)
2. All converted invocations use Skill tool call format structurally consistent with Wave 2
   step 3d in `sc-roadmap/SKILL.md`.
3. The "Return Contract Consumption" section added in T03.03 is intact — no lines removed,
   no content overwritten.
4. The "Post-Adversarial Artifact Existence Gate (Tier 1)" section added in T03.04 is intact.

**Validation**:
1. `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: 0.
2. `grep -c "Return Contract Consumption" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expected: >= 1 (T03.03 content preserved).

**Dependencies**: T03.03 MUST complete before this task begins (same-file conflict constraint).
T04.01 should complete before this task to confirm the Skill tool call format being used is
glossary-consistent.
**Rollback**: Revert the converted Skill tool call entries back to pseudo-CLI syntax. Preserve
all T03.03 and T03.04 additions.

**Notes**: The acceptance criterion uses `grep -c "sc:adversarial --"` with expected result 0
for standalone invocations. If the document uses a pattern like `sc:adversarial --agents` inside
an `args:` string (e.g., `args: "--agents 3 --compare all"`), that occurrence is valid and
acceptable. The verification must distinguish standalone invocations from args-string occurrences.
A more precise grep — `grep -c "^\s*sc:adversarial --\|[^args:]sc:adversarial --"` — may be
needed if `args:` strings contain `sc:adversarial --` patterns.

---

## Phase 4 Checkpoint (End-of-Phase)

**Cumulative task count at this checkpoint**: T01.01–T01.04 (Phase 1), T02.01–T02.05 (Phase 2),
T03.01–T03.05 (Phase 3), T04.01–T04.03 (Phase 4) = 17 tasks completed

**Checkpoint Gate**: All of the following must be true before Phase 5 (Post-Edit Sync &
Quality Gates) begins:

| Gate | Verification Command | Expected |
|------|---------------------|----------|
| Execution Vocabulary glossary present | `grep -c "Execution Vocabulary" src/superclaude/skills/sc-roadmap/SKILL.md` | >= 1 |
| Glossary before Wave 0 | Glossary line number < Wave 0 line number | Pass |
| 100% verb coverage | Coverage audit documented in T04.01 completion notes | Pass |
| Wave 1A step 2 uses Skill call | `grep -c "skill.*sc:adversarial" src/superclaude/skills/sc-roadmap/SKILL.md` | >= 2 |
| Zero standalone pseudo-CLI syntax | `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | 0 |
| T03.03 content intact | `grep -c "Return Contract Consumption" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | >= 1 |
| T03.04 content intact | `grep -c "Artifact Existence Gate\|Tier 1" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | >= 1 |

**Checkpoint Failure Action**: If any gate fails, remediate the corresponding task before
proceeding. The zero-pseudo-CLI gate failure indicates unconverted occurrences remain in
T04.03 — inspect each remaining occurrence to determine if it is a standalone invocation (must
be converted) or an `args:` string inclusion (valid, update grep pattern accordingly).

**Transition to Phase 5**: With Phase 4 complete, all four target files have been edited:
- `src/superclaude/commands/roadmap.md` — Skill tool in allowed-tools (Phase 2)
- `src/superclaude/skills/sc-roadmap/SKILL.md` — Skill tool in allowed-tools, glossary, Wave 1A
  step 2 rewritten, Wave 2 step 3 rewritten (Phases 2 and 4)
- `src/superclaude/skills/sc-adversarial/SKILL.md` — Return Contract section, dead code removed
  (Phase 3)
- `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — Consumption section,
  Tier 1 gate, pseudo-CLI conversion (Phases 3 and 4)

Phase 5 executes `make sync-dev && make verify-sync`, runs lint on all 4 files, and confirms no
existing tests are broken before Phase 6 (End-to-End Validation & Acceptance) begins.

---

*Phase 4 generated 2026-02-25. Roadmap milestone: M4 — Specification Rewrite with Executable
Instructions. Deliverables D-0015 through D-0018. Sprint: sc:roadmap Adversarial Pipeline
Remediation.*
