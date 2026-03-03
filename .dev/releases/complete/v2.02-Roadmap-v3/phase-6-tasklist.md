# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 6: End-to-End Validation & Acceptance

**Phase Goal**: Execute all seven verification tests defined in the sprint spec to confirm that the adversarial pipeline remediation is functionally complete, structurally sound, and regression-free. Tests 1–6 are executed in this phase; Test 7 (fallback protocol validation) is conditionally deferred per Task 0.0 decision recorded in the sprint spec. Passing all in-scope tests constitutes sprint acceptance and authorizes merge to the integration branch.

---

### T06.01 — Verification Test 1: Skill Tool in Allowed-Tools

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-030 (D6.1) |
| **Why** | The core remediation of this sprint adds the `Skill` tool to the `allowed-tools` list in both `roadmap.md` and `sc-roadmap/SKILL.md`. If either grep returns no match, the primary deliverable of the sprint has not landed. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | Read-only operation; no file mutations. Failure indicates a missed edit in Phases 1–4, not a problem with this task. |
| **Tier** | EXEMPT |
| **Confidence** | `[█████████░]` 90% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — grep result is self-evidencing |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual visual inspection of the `allowed-tools` section if grep tooling is unavailable |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0023 |
| **Artifacts** | Terminal output of both grep commands with exit codes |
| **Deliverables** | Confirmed presence of `Skill` in `allowed-tools` in both target files |

#### Steps

1. **[PRE]** Confirm Phase 5 checkpoint passed (all D-0019–D-0022 deliverables present).
2. **[EXEC]** Run: `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS: roadmap.md" || echo "FAIL: roadmap.md"`
3. **[EXEC]** Run: `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS: SKILL.md" || echo "FAIL: SKILL.md"`
4. **[VERIFY]** Both commands must print `PASS`.
5. **[POST]** Record both outputs as evidence artifact D-0023.

#### Acceptance Criteria

1. `grep -q "Skill" src/superclaude/commands/roadmap.md` exits with code 0.
2. `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` exits with code 0.
3. The string `Skill` appears in the `allowed-tools` section specifically (not incidentally in prose).
4. No false positive from a commented-out or negated entry.

#### Validation

1. Both grep commands return exit code 0.
2. A manual line-number inspection (`grep -n "Skill"`) shows the match falls within the `allowed-tools` block context.

#### Dependencies

- Phase 5 checkpoint must be passed.
- Phase 1 and Phase 2 edits (which add `Skill` to allowed-tools) must be complete.

#### Rollback

If grep fails, return to Phase 1/2 tasks and complete the missing `Skill` insertion before re-running this test.

#### Notes

This is a binary pass/fail gate. A grep miss means the sprint's primary objective was not achieved.

---

### T06.02 — Verification Test 2: Wave 2 Step 3 Structural Audit

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-031 (D6.2) |
| **Why** | Wave 2, Step 3 is the structural heart of the adversarial integration. The sprint spec requires a 7-point checklist audit to confirm that the rewritten step contains the correct number of sub-steps, correct Skill tool call syntax, glossary verb alignment, fallback trigger, missing-file guard, convergence threshold, and skip-template handling. |
| **Effort** | S |
| **Risk** | Low |
| **Risk Drivers** | Manual checklist; auditor must be familiar with the sprint spec structure. Subjective interpretation risk on glossary verb alignment. |
| **Tier** | EXEMPT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — read-only audit with human checklist |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — if automated extraction fails, read the file directly and count manually |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0024 |
| **Artifacts** | Completed 7-point checklist with PASS/FAIL per item |
| **Deliverables** | Confirmed structural correctness of Wave 2 Step 3 in `sc-roadmap/SKILL.md` |

#### Steps

1. **[PRE]** Open `src/superclaude/skills/sc-roadmap/SKILL.md` and locate the Wave 2, Step 3 section.
2. **[EXEC]** Work through each checklist item below and record PASS or FAIL:

   | # | Checklist Item | Expected |
   |---|---|---|
   | 2.1 | Sub-step count in Wave 2 Step 3 | Exactly 6 sub-steps |
   | 2.2 | Glossary verbs used in sub-step prose | Match sprint spec glossary (e.g., `invoke`, `emit`, `consume`) |
   | 2.3 | Skill tool call syntax | Uses `Skill` (not `sc:adversarial --`) |
   | 2.4 | Fallback trigger defined | Yes — explicit condition stated |
   | 2.5 | Missing-file guard present | Yes — guard clause present before Skill invocation |
   | 2.6 | Convergence threshold referenced | Yes — numeric threshold or condition stated |
   | 2.7 | Skip-template handling present | Yes — `skip` path documented |

3. **[VERIFY]** All 7 items must be PASS.
4. **[REMEDIATE]** For any FAIL item, identify the corresponding Phase 2 or Phase 3 edit and correct the content.
5. **[POST]** Record the completed checklist as evidence artifact D-0024.

#### Acceptance Criteria

1. All 7 checklist items return PASS.
2. Sub-step count is exactly 6 (not 5, not 7).
3. No instance of `sc:adversarial --` pseudo-CLI syntax appears in Wave 2 Step 3.
4. The Skill tool call syntax is syntactically correct per the sprint spec's tool invocation format.

#### Validation

1. All 7 checklist rows show PASS in the evidence artifact.
2. Independent re-read of the section by a second pass confirms no item was marked PASS incorrectly.

#### Dependencies

- T06.01 must pass (confirms files are in their post-sprint state).
- Phase 2 edits (Wave 2 Step 3 rewrite) must be complete.

#### Rollback

If checklist items fail, return to Phase 2 tasks to correct the Wave 2 Step 3 content, re-sync (T05.01–T05.02), and re-run this test.

#### Notes

This is the most subjective test in Phase 6. When interpreting glossary verb alignment (item 2.2), defer to the exact wording in the sprint spec's glossary section, not to common synonyms.

---

### T06.03 — Verification Test 3: Return Contract Schema Consistency

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-032 (D6.3) |
| **Why** | The adversarial pipeline relies on a shared return contract between `sc-roadmap` (consumer) and `sc-adversarial` (producer). If the field names defined by the producer do not exactly match the field names expected by the consumer, the pipeline will silently fail or produce malformed output at runtime. |
| **Effort** | S |
| **Risk** | Low |
| **Risk Drivers** | Read-only comparison. Schema mismatch failure would require a Phase 3 edit and re-sync. |
| **Tier** | EXEMPT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — read-only field extraction and diff |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual field listing from each file if automated extraction is impractical |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0025 |
| **Artifacts** | Side-by-side field list from producer and consumer with diff result |
| **Deliverables** | Confirmed schema parity between `sc-adversarial/SKILL.md` (producer) and `sc-roadmap/SKILL.md` (consumer) |

#### Steps

1. **[PRE]** Open `src/superclaude/skills/sc-adversarial/SKILL.md` and locate the Return Contract section.
2. **[EXEC]** Extract all top-level field names from the producer's Return Contract and list them in column A.
3. **[EXEC]** Open `src/superclaude/skills/sc-roadmap/SKILL.md` and locate the section that references sc-adversarial return fields.
4. **[EXEC]** Extract all field names referenced by the consumer and list them in column B.
5. **[VERIFY]** Diff column A against column B. The diff must be empty (no additions, no deletions).
6. **[POST]** Record both field lists and the diff result as evidence artifact D-0025.

#### Acceptance Criteria

1. Every field name defined in the producer Return Contract appears in the consumer reference section.
2. Every field name in the consumer reference section exists in the producer Return Contract.
3. Field names are identical in spelling, case, and delimiter style (e.g., `snake_case` vs `camelCase` must match exactly).
4. No orphaned fields exist in either file.

#### Validation

1. `diff <(producer fields) <(consumer fields)` produces no output (exit code 0).
2. Manual spot-check of at least 3 field names confirms exact string match.

#### Dependencies

- T06.01 must pass.
- Phase 3 edits (return contract alignment) must be complete.

#### Rollback

If fields diverge, identify which side (producer or consumer) has the correct definition per the sprint spec, correct the other side in the appropriate Phase 3 task, re-sync, and re-run.

#### Notes

Pay attention to nested field names. Only top-level field names are required to match for this test; nested schema validation is out of scope for this sprint.

---

### T06.04 — Verification Test 3.5: Cross-Reference Field Consistency

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-033 (D6.4) |
| **Why** | The `adversarial-integration.md` reference document in `sc-roadmap/refs/` must accurately cross-reference the same fields verified in T06.03. Stale or incorrect cross-references in this document would mislead future maintainers and create documentation debt. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | Read-only. Failure requires a targeted edit to the reference document, which is a low-effort correction. |
| **Tier** | EXEMPT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — read-only cross-reference check |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual inspection if diff tooling is unavailable |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0026 |
| **Artifacts** | Comparison output confirming field names in `adversarial-integration.md` match the canonical Return Contract |
| **Deliverables** | Confirmed field consistency in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` |

#### Steps

1. **[PRE]** Confirm T06.03 produced a clean diff (empty diff, exit code 0).
2. **[EXEC]** Open `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` and locate all field name references to the sc-adversarial Return Contract.
3. **[EXEC]** Compare those field names against the canonical producer field list from T06.03 column A.
4. **[VERIFY]** All field names in `adversarial-integration.md` must exactly match names from the canonical list. No fields may be absent or renamed.
5. **[POST]** Record the comparison result as evidence artifact D-0026.

#### Acceptance Criteria

1. Every sc-adversarial field referenced in `adversarial-integration.md` exists in the canonical Return Contract.
2. No field referenced in `adversarial-integration.md` uses an alternate name or alias.
3. The document does not reference fields that were removed or renamed during this sprint.
4. Cross-reference section is internally consistent (no contradictions between two mentions of the same field).

#### Validation

1. Manual comparison produces zero discrepancies.
2. No grep match for field names known to have been renamed finds the old name in `adversarial-integration.md`.

#### Dependencies

- T06.03 must pass and its field list (column A) must be available as input.
- Phase 3 edits to `adversarial-integration.md` must be complete.

#### Rollback

If field discrepancies are found in `adversarial-integration.md`, correct them in the Phase 3 task covering that file, re-sync, and re-run T06.04.

#### Notes

This test is numbered 3.5 in the sprint spec, indicating it is a supplementary extension of Test 3. It uses the output of T06.03 as its baseline and does not re-derive the canonical field list independently.

---

### Checkpoint: T06.01–T06.05

All tasks through T06.05 are EXEMPT tier (read-only). If any task above has failed and been remediated, confirm remediation is complete before proceeding to T06.05.

---

### T06.05 — Verification Test 4: Pseudo-CLI Elimination

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-034 (D6.5) |
| **Why** | The sprint spec explicitly prohibits pseudo-CLI invocation syntax (`sc:adversarial --flag`) in `adversarial-integration.md`. Such syntax implies Claude should call itself via a command-line interface, which is architecturally incorrect; all tool invocations must use the `Skill` tool. A grep count of zero is the acceptance signal. |
| **Effort** | XS |
| **Risk** | Low |
| **Risk Drivers** | Read-only grep. Failure indicates Phase 4 edits to `adversarial-integration.md` were incomplete. |
| **Tier** | EXEMPT |
| **Confidence** | `[█████████░]` 90% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — grep count self-evidences |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual text search if grep is unavailable |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0027 |
| **Artifacts** | Terminal output of grep command showing count = 0 |
| **Deliverables** | Confirmed zero occurrences of `sc:adversarial --` in `adversarial-integration.md` |

#### Steps

1. **[PRE]** Confirm T06.04 passed.
2. **[EXEC]** Run: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
3. **[VERIFY]** The command must return `0`.
4. **[REMEDIATE]** If count is non-zero, run `grep -n "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` to locate offending lines, return to Phase 4, replace each occurrence with the correct `Skill` tool invocation syntax, re-sync, and re-run.
5. **[POST]** Record the grep output (`0`) as evidence artifact D-0027.

#### Acceptance Criteria

1. `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns `0`.
2. No variant of the pseudo-CLI pattern (e.g., `sc:adversarial--`, `/sc:adversarial`) appears in the file.
3. All former pseudo-CLI call sites have been replaced with `Skill` tool invocation syntax.
4. The file remains syntactically valid Markdown after all replacements.

#### Validation

1. `grep -c "sc:adversarial --"` returns `0`.
2. A broader grep `grep -c "sc:adversarial"` is run as a sanity check; any matches are reviewed to confirm they are documentation references, not invocation syntax.

#### Dependencies

- T06.04 must pass.
- Phase 4 edits (pseudo-CLI elimination in `adversarial-integration.md`) must be complete.

#### Rollback

If pseudo-CLI syntax remains, locate each instance with `grep -n`, replace with the correct Skill invocation, re-sync via Phase 5 tasks, and re-run.

#### Notes

The exact grep pattern from the sprint spec is `sc:adversarial --` (with a space before `--`). Run an additional check with `sc:adversarial--` (no space) to catch any formatting variants.

---

### T06.06 — Verification Test 5: End-to-End Invocation

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-035 (D6.6) |
| **Why** | All prior tests are static analysis. An actual invocation of `sc:roadmap --multi-roadmap --agents opus,haiku` on a test project is the only way to confirm that the Skill tool call reaches `sc:adversarial`, the return contract is consumed correctly, and no runtime errors occur in the integrated pipeline. |
| **Effort** | L |
| **Risk** | High |
| **Risk Drivers** | End-to-end, cross-cutting, system-wide. Requires a live Claude Code session. Multiple agents are invoked. Output depends on model availability and network state. Failure modes are broad and may require investigation across multiple files. |
| **Tier** | STRICT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | Yes — confirm test project path and model availability before executing |
| **Critical Path Override** | No |
| **Verification Method** | Sub-agent delegation (STRICT tier) — quality-engineer sub-agent validates output |
| **MCP Requirements** | Sequential (pipeline analysis), Serena (cross-file symbol tracking) |
| **Fallback Allowed** | No — this test cannot be substituted; defer to post-sprint manual validation only if model access is unavailable |
| **Sub-Agent Delegation** | Required — delegate execution oversight and output validation to quality-engineer sub-agent |
| **Deliverable IDs** | D-0028 |
| **Artifacts** | Full invocation transcript; sub-agent validation report; pass/fail determination with evidence |
| **Deliverables** | Confirmed end-to-end pipeline execution with no runtime errors and correct return contract consumption |

#### Steps

1. **[PRE]** Confirm T06.01–T06.05 all passed.
2. **[PRE]** Confirm availability of `opus` and `haiku` model endpoints.
3. **[PRE]** Identify or create a minimal test project with at least one roadmap file for `sc:roadmap` to process.
4. **[EXEC]** In a live Claude Code session, invoke: `sc:roadmap --multi-roadmap --agents opus,haiku` against the test project.
5. **[EXEC]** Monitor the execution log for the Wave 2 Step 3 Skill tool call to `sc-adversarial`.
6. **[VERIFY — Sub-Agent]** Delegate to quality-engineer sub-agent: confirm (a) Skill tool was called with correct arguments, (b) sc-adversarial return contract fields appear in sc-roadmap's subsequent processing, (c) no error or exception was raised during the step.
7. **[VERIFY]** Confirm final roadmap output is structurally valid (not corrupted by pipeline failure).
8. **[POST]** Capture invocation transcript and sub-agent report as evidence artifact D-0028.

#### Acceptance Criteria

1. `sc:roadmap --multi-roadmap --agents opus,haiku` completes without runtime error.
2. Wave 2 Step 3 Skill tool call to `sc-adversarial` is present in the execution trace.
3. Return contract fields from `sc-adversarial` are consumed in sc-roadmap's downstream steps.
4. Final roadmap output is structurally valid and contains adversarial-enriched content.

#### Validation

1. Sub-agent quality-engineer confirms all three verification sub-points (a, b, c) in its report.
2. No `error`, `exception`, or `failed` log entries in the execution transcript that are attributable to the adversarial pipeline.

#### Dependencies

- T06.01–T06.05 must all pass.
- Live Claude Code session with model access required.
- Test project must be available with a valid roadmap file.

#### Rollback

If the E2E invocation fails, capture the full error trace, identify the failing step via Sequential analysis, return to the appropriate Phase task for correction, re-sync, re-run Phase 6 tests from T06.01.

#### Notes

Per the sprint spec: "Test 5: E2E — post-sprint, manual." If model endpoints are unavailable at sprint closure time, this test is formally deferred to post-sprint manual validation. The deferral must be recorded as a known open item in the sprint completion report. All other tests (T06.01–T06.05, T06.07) must still pass for sprint acceptance.

---

### T06.07 — Verification Test 6: Tier 1 Quality Gate Structure Audit

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-036 (D6.7) |
| **Why** | The sprint modifies skill files that participate in Tier 1 quality gate processing. The 7-point structural audit confirms that the gate's required structural elements are all present and correctly positioned in `sc-roadmap/SKILL.md`, ensuring the skill remains eligible for Tier 1 classification and will not be silently downgraded by the gate evaluation logic. |
| **Effort** | S |
| **Risk** | Low |
| **Risk Drivers** | Read-only structural check. Failure requires a targeted structural edit, not a logic change. |
| **Tier** | EXEMPT |
| **Confidence** | `[████████░░]` 85% |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Skip verification (EXEMPT tier) — read-only structural checklist |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — manual file inspection if automated section detection is impractical |
| **Sub-Agent Delegation** | Not required |
| **Deliverable IDs** | D-0029 |
| **Artifacts** | Completed 7-point Tier 1 structural checklist with PASS/FAIL per item |
| **Deliverables** | Confirmed Tier 1 quality gate structural compliance of `src/superclaude/skills/sc-roadmap/SKILL.md` |

#### Steps

1. **[PRE]** Confirm T06.05 passed (confirms file is in post-sprint state).
2. **[EXEC]** Open `src/superclaude/skills/sc-roadmap/SKILL.md` and work through the 7-point Tier 1 structural checklist:

   | # | Structural Element | Expected |
   |---|---|---|
   | 6.1 | `SKILL.md` frontmatter block present | Yes — valid YAML or structured header |
   | 6.2 | `allowed-tools` section present and non-empty | Yes — at least one tool listed |
   | 6.3 | `Skill` appears in `allowed-tools` | Yes (confirmed by T06.01) |
   | 6.4 | Wave structure sections present (Wave 1, Wave 2) | Yes — both waves defined |
   | 6.5 | Each wave contains numbered steps | Yes — sequential step numbering |
   | 6.6 | Return contract or output schema section present | Yes — defined for consumer reference |
   | 6.7 | No pseudo-CLI invocation syntax in any step | Yes (confirmed by T06.05 for refs file; confirm here for SKILL.md itself) |

3. **[VERIFY]** All 7 items must be PASS.
4. **[REMEDIATE]** For any FAIL item, identify the relevant Phase task that should have introduced the missing element and complete it before re-running.
5. **[POST]** Record the completed checklist as evidence artifact D-0029.

#### Acceptance Criteria

1. All 7 structural checklist items return PASS.
2. `allowed-tools` section contains `Skill` as confirmed independently in T06.01.
3. Both Wave 1 and Wave 2 sections are present and contain step content.
4. No `sc:adversarial --` pseudo-CLI syntax appears in `SKILL.md` (distinct from the refs file checked in T06.05).

#### Validation

1. All 7 checklist rows show PASS in the evidence artifact.
2. Checklist items 6.3 and 6.7 are cross-referenced against T06.01 and T06.05 results respectively for consistency.

#### Dependencies

- T06.01 and T06.05 must pass (checklist items 6.3 and 6.7 reuse their evidence).
- All Phase 1–4 edits to `sc-roadmap/SKILL.md` must be complete.

#### Rollback

If structural elements are missing, return to the Phase task responsible for that element, add the missing structure, re-sync (T05.01–T05.02), and re-run T06.07.

#### Notes

Checklist items 6.3 and 6.7 are not redundant with T06.01 and T06.05 — they confirm the same properties in `SKILL.md` specifically, whereas T06.01 checked both files and T06.05 checked only the refs file. Explicit per-file confirmation is intentional.

---

### Phase 6 End-of-Phase Checkpoint

| Task | Tier | Expected Result |
|---|---|---|
| T06.01 — Skill tool grep | EXEMPT | Both greps exit 0 |
| T06.02 — Wave 2 Step 3 audit | EXEMPT | All 7 checklist items PASS |
| T06.03 — Return contract schema | EXEMPT | Zero-diff between producer and consumer fields |
| T06.04 — Cross-reference fields | EXEMPT | Zero discrepancies in `adversarial-integration.md` |
| T06.05 — Pseudo-CLI elimination | EXEMPT | grep count = 0 |
| T06.06 — E2E invocation | STRICT | Pipeline completes, return contract consumed (or formally deferred) |
| T06.07 — Tier 1 gate audit | EXEMPT | All 7 structural checklist items PASS |
| All D-0023–D-0029 deliverables present | — | Yes |

**Sprint Acceptance Gate**: T06.01–T06.05 and T06.07 must all pass. T06.06 must pass or be formally deferred with documented rationale. No task may be marked complete without its evidence artifact recorded.

**Post-Sprint Actions** (outside Phase 6 scope):
- If T06.06 was deferred: schedule post-sprint manual E2E session.
- If Test 7 (fallback protocol validation) was deferred per Task 0.0: document open item and schedule.
- Merge to `integration` branch following the Git workflow in `CLAUDE.md`.
