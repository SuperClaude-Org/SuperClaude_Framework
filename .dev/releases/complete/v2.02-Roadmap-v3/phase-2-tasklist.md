# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 2: Invocation Wiring Restoration

**Phase Goal**: Restore the adversarial pipeline's invocation wiring by making two targeted modifications to existing skill files, then executing the sprint's core deliverable — a complete rewrite of Wave 2 Step 3 in `roadmap.md` that introduces Skill-to-Skill invocation sub-steps (3a-3f), a structured fallback protocol (F1, F2/3, F4/5), and atomic return contract routing. Phase 2 begins only after the Phase 1 checkpoint passes and `sprint-variant.md` has been acknowledged. The variant decision from T01.04 directly governs which sub-paths T02.02 activates. T02.01 is a fast, grep-verifiable prerequisite; T02.02 is the high-risk, high-effort merged mega-task that constitutes the majority of sprint value.

**Input from Phase 1**: `sprint-variant.md` routing instructions must be read at the start of T02.01 and carried forward into T02.02.

---

### T02.01 — Add `Skill` to allowed-tools in roadmap.md and SKILL.md

**Roadmap Item IDs**: R-007, R-008, R-009

**Why**: The `Skill` tool cannot be invoked from within a skill context unless it appears in the `allowed-tools` list of that skill's configuration. Both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md` must declare it. Without this change, any Skill tool invocation written in T02.02 will be blocked at runtime regardless of how correctly it is authored. These two additions are individually trivial but are a hard prerequisite for T02.02.

**Effort**: XS
**Risk**: Low
**Risk Drivers**: Mechanical text additions; grep-verifiable before and after; no logic changes.

**Tier**: STANDARD
**Confidence**: [========] 80%
**Requires Confirmation**: No
**Critical Path Override**: No
**Verification Method**: Direct test execution (STANDARD — 300-500 tokens, 30s; grep confirms presence)
**MCP Requirements**: None required; Edit tool sufficient for both modifications
**Fallback Allowed**: No — both files must be updated; a partial update leaves the pipeline in an inconsistent state
**Sub-Agent Delegation**: No — two-file atomic edit, no delegation benefit

**Deliverable IDs**: D-0005
**Artifacts**: Modified `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md`
**Deliverables**: Both files contain `Skill` in their `allowed-tools` lines; grep validation passes for both

**Steps**:
1. [READ] Read `src/superclaude/commands/roadmap.md` and locate the `allowed-tools` or `tools` declaration line. Note exact formatting (comma-separated, YAML list, inline) to match style.
2. [READ] Read `src/superclaude/skills/sc-roadmap/SKILL.md` and locate the corresponding `allowed-tools` declaration. Note formatting.
3. [EDIT] Add `Skill` to the `allowed-tools` line in `roadmap.md`, matching existing formatting style. Do not alter any other content.
4. [EDIT] Add `Skill` to the `allowed-tools` line in `SKILL.md`, matching existing formatting style. Do not alter any other content.
5. [VERIFY] Run `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "roadmap.md PASS" || echo "roadmap.md FAIL"`.
6. [VERIFY] Run `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "SKILL.md PASS" || echo "SKILL.md FAIL"`.

**Acceptance Criteria**:
1. `Skill` appears in the `allowed-tools` declaration of `src/superclaude/commands/roadmap.md` with formatting consistent with existing entries.
2. `Skill` appears in the `allowed-tools` declaration of `src/superclaude/skills/sc-roadmap/SKILL.md` with formatting consistent with existing entries.
3. Both grep validation commands return PASS output — no manual assertion accepted.
4. No other content in either file was modified; diff shows exactly the `Skill` addition and nothing else.

**Validation**:
1. `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS"` returns PASS.
2. `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS"` returns PASS.

**Dependencies**: CP-P1 (Phase 1 checkpoint must pass), T01.04 (`sprint-variant.md` must be read before this task runs to confirm PRIMARY_VARIANT is selected; if FALLBACK_VARIANT, this task still runs as the `Skill` declaration is needed for future-proofing).
**Rollback**: Revert both files to their pre-edit state using git; the change is a single-line addition in each file and reverts cleanly.
**Notes**: If `allowed-tools` does not exist as a field in either file, do not create it speculatively — flag the finding and pause for clarification. The field structure must already exist for this task to proceed as scoped.

---

### T02.02 — Rewrite Wave 2 Step 3: Skill Invocation, Fallback Protocol, and Atomic Sub-Steps

**Roadmap Item IDs**: R-007, R-010, R-011, R-012

**Why**: Wave 2 Step 3 is the execution point where `sc:roadmap` orchestrates `sc:adversarial`. The current implementation is a single undifferentiated step with no fallback handling, no atomic sub-step structure, and no return contract routing. This task replaces it with a six-sub-step sequence (3a-3f) covering pre-invocation readiness check, primary Skill invocation, result capture, fallback escalation ladder (F1 through F4/5), return contract parsing, and post-invocation state update. This is the highest-value task in the sprint and the most failure-prone: it modifies pipeline control flow, introduces conditional branching, and must remain internally consistent with the constraint semantics determined in T01.02.

**Effort**: XL
**Risk**: High
**Risk Drivers**: Multi-file scope affecting pipeline control flow; system-wide behavioral change to the adversarial orchestration sequence; breaking change to pipeline spec if sub-step IDs are referenced externally; fallback protocol logic must be consistent with constraint semantics from T01.02 and variant decision from T01.04; auth-proxy-adjacent patterns in fallback F4/5 elevate security surface awareness.

**Tier**: STRICT
**Confidence**: [=========] 90%
**Requires Confirmation**: Yes — present the complete rewritten Step 3 prose for review before writing to file
**Critical Path Override**: No
**Verification Method**: Sub-agent (quality-engineer, 3-5K tokens, 60s timeout)
**MCP Requirements**: Sequential (multi-step reasoning across sub-step design, fallback logic, return contract routing), Serena (symbol-level navigation of roadmap.md and SKILL.md to locate exact insertion point and avoid overwriting adjacent steps)
**Fallback Allowed**: No — this task is the sprint deliverable; a partial rewrite is worse than no rewrite because it leaves the pipeline in an inconsistent state
**Sub-Agent Delegation**: Required — STRICT tier + High risk mandates quality-engineer sub-agent validation of the rewritten prose before file write

**Deliverable IDs**: D-0006
**Artifacts**: Modified `src/superclaude/commands/roadmap.md` with Wave 2 Step 3 fully rewritten as sub-steps 3a-3f plus fallback protocol and return contract routing
**Deliverables**: Wave 2 Step 3 in `roadmap.md` replaced with atomic sub-step structure; fallback protocol F1/F2/3/F4/5 documented inline; return contract routing in step 3e; SKILL.md updated if sub-step references require mirroring

**Steps**:
1. [READ] Read `src/superclaude/commands/roadmap.md` in full. Locate Wave 2 Step 3 exact boundaries — identify the start line, end line, and any cross-references from other steps that name Step 3.
2. [READ] Read `src/superclaude/skills/sc-roadmap/SKILL.md` in full. Identify any existing Step 3 references that will need updating after the rewrite.
3. [READ] Read `probe-results.md` constraint semantics label and `sprint-variant.md` routing instructions. Confirm variant and constraint scope before drafting.
4. [DRAFT-3a] Draft sub-step 3a: Pre-invocation readiness check. Content: verify `sc:adversarial` is not already running (per constraint semantics from T01.02); if SAME_NAME_BLOCKED or ANY_SKILL_BLOCKED, proceed to F1 immediately; if clear, continue to 3b.
5. [DRAFT-3b] Draft sub-step 3b: Primary Skill invocation. Content: invoke `sc:adversarial` via Skill tool with the task payload assembled in Step 2; capture raw return value; proceed to 3c. If PRIMARY_VARIANT is not selected per sprint-variant.md, this sub-step is annotated as INACTIVE and control passes directly to F1.
6. [DRAFT-3c] Draft sub-step 3c: Result capture and nil-check. Content: if return value is nil or malformed, proceed to F1; if well-formed, proceed to 3d.
7. [DRAFT-3d] Draft sub-step 3d: Return value type classification. Content: classify return as SUCCESS_PAYLOAD, PARTIAL_PAYLOAD, or ERROR_PAYLOAD; route to 3e (success/partial) or F2/3 (error).
8. [DRAFT-3e] Draft sub-step 3e: Return contract routing. Content: parse SUCCESS_PAYLOAD per return contract schema; extract required fields; write to pipeline state; proceed to Step 4. For PARTIAL_PAYLOAD, extract available fields, flag missing fields, proceed to Step 4 with degraded state annotation.
9. [DRAFT-F1] Draft fallback F1: First-level fallback. Content: log Skill invocation failure reason; attempt lightweight re-invoke with reduced payload; if successful, route to 3c; if failed, proceed to F2/3.
10. [DRAFT-F2/3] Draft fallback F2/3: Intermediate fallback. Content: abandon Skill tool invocation; reconstruct adversarial task execution using inline prose instructions without Skill tool dependency; proceed to 3e with PARTIAL_PAYLOAD classification.
11. [DRAFT-F4/5] Draft fallback F4/5: Terminal fallback. Content: if F2/3 inline execution also fails, log failure with full context; write ERROR_PAYLOAD to pipeline state; surface error to Wave 2 orchestrator; halt adversarial sub-pipeline and continue Wave 2 without adversarial output.
12. [REVIEW] Present complete rewritten Step 3 prose (3a-3f + F1/F2/3/F4/5) to user for confirmation before any file write.
13. [WRITE] After confirmation, use Edit tool to replace existing Wave 2 Step 3 in `roadmap.md` with the confirmed prose. Do not alter Step 2 or Step 4.
14. [UPDATE-SKILL] If SKILL.md contains Step 3 references that now name sub-steps, update those references to use the new sub-step IDs (3a-3f).
15. [DELEGATE] Dispatch quality-engineer sub-agent with prompt: "Review the rewritten Wave 2 Step 3 in src/superclaude/commands/roadmap.md. Verify: (1) sub-steps 3a-3f are internally consistent and form a complete execution sequence with no gaps; (2) fallback levels F1, F2/3, F4/5 are exhaustive and non-overlapping; (3) return contract routing in 3e handles all three payload classifications; (4) constraint semantics from probe-results.md are correctly reflected in sub-step 3a logic; (5) no adjacent steps (Step 2 or Step 4) were inadvertently modified."
16. [RESOLVE] Address any quality-engineer findings. If findings require prose changes, re-confirm with user before writing.

**Acceptance Criteria**:
1. Wave 2 Step 3 in `src/superclaude/commands/roadmap.md` is structured as exactly six labeled sub-steps (3a, 3b, 3c, 3d, 3e, 3f) with no sub-step omitted or merged.
2. Fallback protocol contains exactly three fallback levels labeled F1, F2/3, and F4/5, each with a distinct trigger condition and a defined exit route.
3. Sub-step 3e documents return contract routing for all three payload classifications (SUCCESS_PAYLOAD, PARTIAL_PAYLOAD, ERROR_PAYLOAD) — partial handling is not acceptable.
4. Quality-engineer sub-agent validation completed with no unresolved HIGH-severity findings; any MEDIUM findings are documented with disposition.

**Validation**:
1. `grep -c "3a\|3b\|3c\|3d\|3e\|3f" src/superclaude/commands/roadmap.md` returns a count consistent with six sub-step labels present in the file.
2. Quality-engineer sub-agent report is written to `.dev/releases/current/v2.02-Roadmap-v3/` as `qa-t0202-report.md` with an explicit PASS or CONDITIONAL_PASS verdict on the final line.

**Dependencies**: T02.01 (Skill must be in allowed-tools before the rewrite references it), T01.02 (constraint semantics required for 3a logic), T01.04 (variant decision required for 3b activation status), CP-P1 (Phase 1 checkpoint).
**Rollback**: Revert `src/superclaude/commands/roadmap.md` to pre-edit state using git. The rewrite is bounded to Wave 2 Step 3; git diff will show the exact replacement. If SKILL.md was also updated, revert it in the same operation.
**Notes**: Sub-step 3b must be clearly annotated as INACTIVE (not deleted) when FALLBACK_VARIANT is in effect — the annotation preserves the intended design for future re-activation when the Skill tool constraint is resolved. The quality-engineer sub-agent report is a required deliverable, not optional post-hoc validation. If the sub-agent is unavailable, this task cannot mark complete until an equivalent manual review is documented in `qa-t0202-report.md`.

---

## Phase 2 End-of-Phase Checkpoint

**Checkpoint ID**: CP-P2
**Cumulative Task Count**: 6 (4 from Phase 1 + 2 from Phase 2)

**Gate Conditions — all must be true before Phase 3 begins**:

| # | Condition | Evidence Required |
|---|-----------|------------------|
| 1 | T02.01 complete | Both grep validations return PASS; diff shows only Skill addition in each file |
| 2 | T02.02 confirmed | User confirmation received before file write in step 12 |
| 3 | T02.02 written | Wave 2 Step 3 in roadmap.md contains sub-steps 3a-3f and fallback levels F1/F2/3/F4/5 |
| 4 | T02.02 validated | `qa-t0202-report.md` exists with PASS or CONDITIONAL_PASS verdict |
| 5 | No unresolved HIGH findings | All quality-engineer HIGH-severity findings addressed and documented |
| 6 | make verify-sync passes | Run `make verify-sync` to confirm src/ and .claude/ are in sync after edits |

**On Checkpoint Pass**: Proceed to Phase 3. Both modified files are in a consistent state and the adversarial pipeline invocation wiring is restored.

**On Checkpoint Fail**: Identify the failing gate condition. If T02.02 has an unresolved HIGH finding, re-enter the resolve step and re-run quality-engineer validation. If `make verify-sync` fails, run `make sync-dev` and re-validate. Do not proceed to Phase 3 until all six conditions are green.
