# TASKLIST — v2.01 Architecture Refactor

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`
- **Tasklist Path**: `TASKLIST_ROOT/tasklist-header.md` + `TASKLIST_ROOT/tasklist-P1.md` through `tasklist-P6.md`
- **Execution Log Path**: `TASKLIST_ROOT/execution-log.md`
- **Checkpoint Reports Path**: `TASKLIST_ROOT/checkpoints/`
- **Evidence Root**: `TASKLIST_ROOT/evidence/`
- **Artifacts Root**: `TASKLIST_ROOT/artifacts/`
- **Feedback Log Path**: `TASKLIST_ROOT/feedback-log.md`

---

## Source Snapshot

- v2.01 is a strict architectural refactor enforcing 3-tier separation: Commands (doors), Skills (rooms), Refs (drawers)
- 10 milestones with 1:1 validation interleaving; HIGH complexity class (0.727)
- 18 tasks and 6 bug fixes organized across 6 phases; critical path M1→M3→M4→M5→M7→M9→M10
- FALLBACK-ONLY variant: Task agent dispatch is sole viable invocation mechanism (D-0001/D-0002)
- All prior implementation erased by rollback to commit `5733e32`; no staged work trusted
- 5 skill directory renames, 5 command `## Activation` additions, `make lint-architecture` enforcement target

---

## Deterministic Rules Applied

1. **Phase buckets**: 6 explicit phases from roadmap §13 (Phase 1–6), preserved as-is; validation milestones M2/M4/M6/M8/M10 incorporated as tasks within their corresponding phases
2. **Phase numbering**: Sequential Phase 1–6 with no gaps (Section 4.3)
3. **Task IDs**: `T<PP>.<TT>` zero-padded format (e.g., `T01.03`)
4. **Task ordering**: Roadmap top-to-bottom order within each phase; dependencies reordered only within same phase
5. **Checkpoint cadence**: After every 5 tasks within a phase + end-of-phase checkpoint (Section 4.8)
6. **Clarification tasks**: Inserted when roadmap info is missing or tier confidence < 0.70 (Section 4.6)
7. **Deliverable registry**: Global `D-####` IDs in task order (Section 5.1)
8. **Effort/Risk mappings**: Deterministic keyword-based scoring (Section 5.2)
9. **Tier classification**: `/sc:task-unified` algorithm with compound phrase overrides, keyword matching, and context boosters (Section 5.3)
10. **Verification routing**: Tier-aligned verification method (Sub-agent/Direct test/Sanity check/Skip) per Section 4.10
11. **MCP requirements**: Tier-based tool declarations per Section 5.5
12. **Traceability matrix**: R-### → T<PP>.<TT> → D-#### → artifact paths → tier → confidence (Section 5.7)

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | Phase 1 | T01.01: Skill tool probe re-run in current environment |
| R-002 | Phase 1 | T01.02: Prerequisite validation — all files exist, build targets valid, branch state clean |
| R-003 | Phase 1 | T01.03: Tier classification policy — executable `.md` files are STANDARD minimum (Rule 7.6) |
| R-004 | Phase 1 | Verify/create architecture policy document at `docs/architecture/command-skill-policy.md` (FR-001, Layer 0) |
| R-005 | Phase 1 | Probe result verification: confirm D-0001 still holds or document new variant |
| R-006 | Phase 1 | Branch state clean: no untrusted staged changes, all prerequisites verified |
| R-007 | Phase 2 | T02.01: Add `Skill` to `roadmap.md` `allowed-tools` frontmatter (BUG-001 partial) |
| R-008 | Phase 2 | T02.02: Add `Skill` to `sc-roadmap-protocol/SKILL.md` `allowed-tools` (BUG-001 partial) |
| R-009 | Phase 2 | T02.04: Rewrite `roadmap.md` `## Activation` to reference `Skill sc:roadmap-protocol` (BUG-006) |
| R-010 | Phase 2 | T02.03: Decompose Wave 2 Step 3 into sub-steps 3a-3f with explicit tool bindings |
| R-011 | Phase 2 | Fallback protocol F1/F2-3/F4-5 fully specified with convergence routing |
| R-012 | Phase 2 | Rename 5 skill directories with `-protocol` suffix in `src/superclaude/skills/` (FR-002) |
| R-013 | Phase 2 | 8-point structural audit of Wave 2 Step 3 (per §9) |
| R-014 | Phase 2 | End-to-end activation chain test: `/sc:roadmap` → `Skill sc:roadmap-protocol` → SKILL.md loads |
| R-015 | Phase 3 | T03.01: Remove skill-skip heuristic from `sync-dev` and `verify-sync` in Makefile |
| R-016 | Phase 3 | T03.02: Add `lint-architecture` target to Makefile implementing 6 designed checks (#1-4, #6, #8-9) |
| R-017 | Phase 3 | T03.03: Run `make lint-architecture` against current tree |
| R-018 | Phase 3 | Makefile `.PHONY` and `help` targets updated to reference `lint-architecture` |
| R-019 | Phase 3 | Positive lint test: `make lint-architecture` exits 0 on compliant tree |
| R-020 | Phase 3 | Negative lint test: verify `make lint-architecture` fails when skill is missing or `## Activation` absent |
| R-021 | Phase 4 | T04.01: Return contract consumer routing tests — validate Pass/Partial/Fail paths with convergence thresholds |
| R-022 | Phase 4 | T04.02: Adversarial pipeline integration tests — verify fallback protocol F1/F2-3/F4-5 |
| R-023 | Phase 4 | T04.03: Artifact gate specification and standards |
| R-024 | Phase 4 | All M7 tests pass with documented results |
| R-025 | Phase 4 | No Critical or Major issues from M7 testing |
| R-026 | Phase 5 | T05.01: Verb-to-tool glossary created |
| R-027 | Phase 5 | T05.02: Wave 1A Step 2 semantic alignment fix |
| R-028 | Phase 5 | T05.03: Pseudo-CLI invocation conversion |
| R-029 | Phase 6 | T06.01: Cross-skill invocation pattern documentation |
| R-030 | Phase 6 | T06.02: Tier 2 ref loader design (`claude -p` script) |
| R-031 | Phase 6 | T06.03: `task-unified.md` major extraction (567→106 lines) |
| R-032 | Phase 6 | T06.04: Remaining 4 command files updated — `## Activation` added + BUG-001 fixed |
| R-033 | Phase 6 | BUG-004 (policy dedup) resolved |
| R-034 | Phase 6 | BUG-002 (stale path), BUG-003 (threshold) resolved |
| R-035 | Phase 6 | Full regression: `make sync-dev && make verify-sync && make lint-architecture` |
| R-036 | Phase 6 | Stale reference scan: zero references to old skill directory names |
| R-037 | Phase 6 | All 10 success criteria (SC-001 through SC-010) verified |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Probe result document (variant decision) | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0001/spec.md` | XS | Low |
| D-0002 | T01.02 | R-002 | Prerequisite verification report | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0002/evidence.md` | XS | Low |
| D-0003 | T01.03 | R-003 | Tier classification policy document | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0003/spec.md` | XS | Low |
| D-0004 | T01.04 | R-004 | Architecture policy document (verified/created) | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | XS | Low |
| D-0005 | T01.05 | R-005 | Probe verification confirmation | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0005/evidence.md` | XS | Low |
| D-0006 | T01.06 | R-006 | Branch state verification report | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0006/evidence.md` | XS | Low |
| D-0007 | T02.01 | R-007 | Updated `roadmap.md` with `Skill` in `allowed-tools` | LIGHT | Sanity check | `TASKLIST_ROOT/artifacts/D-0007/evidence.md` | XS | Low |
| D-0008 | T02.02 | R-008 | Updated SKILL.md with `Skill` in `allowed-tools` | LIGHT | Sanity check | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` | XS | Low |
| D-0009 | T02.03 | R-010 | Wave 2 Step 3 decomposition (6 sub-steps 3a-3f) | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0009/spec.md` | L | High |
| D-0010 | T02.03 | R-011 | Fallback protocol specification (F1/F2-3/F4-5) | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0010/spec.md` | L | High |
| D-0011 | T02.04 | R-009 | Rewritten `roadmap.md` `## Activation` section | LIGHT | Sanity check | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` | XS | Low |
| D-0012 | T02.05 | R-012 | 5 renamed skill directories | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0012/spec.md` | XL | High |
| D-0013 | T02.05 | R-012 | Updated SKILL.md `name:` fields for all 5 skills | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0013/evidence.md` | XL | High |
| D-0014 | T02.05 | R-012 | `make sync-dev` copies created for all 5 skills | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0014/evidence.md` | XL | High |
| D-0015 | T02.06 | R-013 | 8-point structural audit report | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0015/evidence.md` | S | Medium |
| D-0016 | T02.07 | R-014 | End-to-end activation test report | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0016/evidence.md` | S | Medium |
| D-0017 | T03.01 | R-015 | Updated Makefile (heuristics removed from `sync-dev` and `verify-sync`) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0017/evidence.md` | S | Medium |
| D-0018 | T03.02 | R-016, R-018 | `lint-architecture` target + `.PHONY`/`help` updates | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0018/spec.md`, `TASKLIST_ROOT/artifacts/D-0018/evidence.md` | M | Medium |
| D-0019 | T03.03 | R-017 | `make lint-architecture` passing result on current tree | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0019/evidence.md` | S | Low |
| D-0020 | T03.04 | R-019 | Positive lint test result (exit 0 on compliant tree) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0020/evidence.md` | XS | Low |
| D-0021 | T03.05 | R-020 | Negative lint test result (exit 1 on non-compliant tree) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0021/evidence.md` | XS | Low |
| D-0022 | T04.01 | R-021 | Return contract consumer routing test suite | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0022/spec.md`, `TASKLIST_ROOT/artifacts/D-0022/evidence.md` | M | High |
| D-0023 | T04.02 | R-022 | Adversarial pipeline integration test suite | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0023/spec.md`, `TASKLIST_ROOT/artifacts/D-0023/evidence.md` | M | High |
| D-0024 | T04.03 | R-023 | Artifact gate specification document | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0024/spec.md` | M | Medium |
| D-0025 | T04.04 | R-024 | M7 test results documentation | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0025/evidence.md` | XS | Low |
| D-0026 | T04.05 | R-025 | Issue triage report (zero Critical/Major) | EXEMPT | Skip | `TASKLIST_ROOT/artifacts/D-0026/evidence.md` | XS | Low |
| D-0027 | T05.01 | R-026 | Verb-to-tool glossary | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0027/spec.md` | S | Low |
| D-0028 | T05.02 | R-027 | Wave 1A Step 2 semantic alignment fix | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0028/evidence.md` | S | Low |
| D-0029 | T05.03 | R-028 | Converted pseudo-CLI invocation patterns | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0029/evidence.md` | S | Low |
| D-0030 | T06.01 | R-029 | Cross-skill invocation pattern documentation | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0030/spec.md` | S | Low |
| D-0031 | T06.02 | R-030 | Tier 2 ref loader design document | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0031/spec.md` | M | Medium |
| D-0032 | T06.03 | R-031 | Extracted `task-unified.md` (≤106 lines) | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0032/spec.md` | L | High |
| D-0033 | T06.03 | R-031 | `sc-task-unified-protocol/SKILL.md` with extracted protocol logic | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0033/evidence.md` | L | High |
| D-0034 | T06.04 | R-032 | 4 updated command files (adversarial, cleanup-audit, task-unified, validate-tests) | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0034/spec.md`, `TASKLIST_ROOT/artifacts/D-0034/evidence.md` | M | High |
| D-0035 | T06.05 | R-033 | Resolved BUG-004 (canonical source designated, symlink from `src/`) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0035/evidence.md` | S | Low |
| D-0036 | T06.06 | R-034 | Resolved BUG-002 (stale path fixed in `validate-tests.md` line 63) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0036/evidence.md` | S | Low |
| D-0037 | T06.06 | R-034 | Resolved BUG-003 (orchestrator threshold aligned to ≥3) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0037/evidence.md` | S | Low |
| D-0038 | T06.07 | R-035 | Full regression pass report (`sync-dev`, `verify-sync`, `lint-architecture`) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0038/evidence.md` | S | Medium |
| D-0039 | T06.08 | R-036 | Stale reference scan (zero matches for all 5 old names) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0039/evidence.md` | XS | Low |
| D-0040 | T06.09 | R-037 | SC-001 through SC-010 verification report | STRICT | Sub-agent | `TASKLIST_ROOT/artifacts/D-0040/spec.md`, `TASKLIST_ROOT/artifacts/D-0040/evidence.md` | M | Medium |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| 1 | Foundation & Environment Probe | T01.01–T01.06 | Variant decision documented; environment verified; tier policy established | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 6 |
| 2 | Invocation Wiring & Activation Fix | T02.01–T02.07 | Invocation chain wired end-to-end; 5 skill dirs renamed; 8-point audit passes | STRICT: 4, STANDARD: 0, LIGHT: 2, EXEMPT: 0 |
| 3 | Build System Enforcement | T03.01–T03.05 | `make lint-architecture` operational; heuristics removed; positive/negative tests pass | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 4 | Structural Validation & Testing | T04.01–T04.05 | Return contract routing tested; adversarial pipeline integration tested; issues triaged | STRICT: 3, STANDARD: 0, LIGHT: 0, EXEMPT: 2 |
| 5 | Polish | T05.01–T05.03 | Verb glossary created; semantic alignment fixed; pseudo-CLI patterns converted | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 6 | Integration & Closure | T06.01–T06.09 | All commands updated; extraction complete; bugs fixed; full regression + SC verification | STRICT: 3, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |

**Totals**: 35 tasks across 6 phases — STRICT: 10, STANDARD: 13, LIGHT: 2, EXEMPT: 8, Clarification: 2

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 85% | `TASKLIST_ROOT/artifacts/D-0001/spec.md` |
| R-002 | T01.02 | D-0002 | EXEMPT | 90% | `TASKLIST_ROOT/artifacts/D-0002/evidence.md` |
| R-003 | T01.03 | D-0003 | EXEMPT | 80% | `TASKLIST_ROOT/artifacts/D-0003/spec.md` |
| R-004 | T01.04 | D-0004 | EXEMPT | 85% | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` |
| R-005 | T01.05 | D-0005 | EXEMPT | 85% | `TASKLIST_ROOT/artifacts/D-0005/evidence.md` |
| R-006 | T01.06 | D-0006 | EXEMPT | 90% | `TASKLIST_ROOT/artifacts/D-0006/evidence.md` |
| R-007 | T02.01 | D-0007 | LIGHT | 75% | `TASKLIST_ROOT/artifacts/D-0007/evidence.md` |
| R-008 | T02.02 | D-0008 | LIGHT | 75% | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` |
| R-009 | T02.04 | D-0011 | LIGHT | 80% | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` |
| R-010 | T02.03 | D-0009 | STRICT | 90% | `TASKLIST_ROOT/artifacts/D-0009/spec.md` |
| R-011 | T02.03 | D-0010 | STRICT | 90% | `TASKLIST_ROOT/artifacts/D-0010/spec.md` |
| R-012 | T02.05 | D-0012, D-0013, D-0014 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0012/spec.md`, `TASKLIST_ROOT/artifacts/D-0013/evidence.md`, `TASKLIST_ROOT/artifacts/D-0014/evidence.md` |
| R-013 | T02.06 | D-0015 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0015/evidence.md` |
| R-014 | T02.07 | D-0016 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0016/evidence.md` |
| R-015 | T03.01 | D-0017 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0017/evidence.md` |
| R-016 | T03.02 | D-0018 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0018/spec.md`, `TASKLIST_ROOT/artifacts/D-0018/evidence.md` |
| R-017 | T03.03 | D-0019 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0019/evidence.md` |
| R-018 | T03.02 | D-0018 | STANDARD | 80% | (included in D-0018) |
| R-019 | T03.04 | D-0020 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0020/evidence.md` |
| R-020 | T03.05 | D-0021 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0021/evidence.md` |
| R-021 | T04.01 | D-0022 | STRICT | 90% | `TASKLIST_ROOT/artifacts/D-0022/spec.md`, `TASKLIST_ROOT/artifacts/D-0022/evidence.md` |
| R-022 | T04.02 | D-0023 | STRICT | 90% | `TASKLIST_ROOT/artifacts/D-0023/spec.md`, `TASKLIST_ROOT/artifacts/D-0023/evidence.md` |
| R-023 | T04.03 | D-0024 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0024/spec.md` |
| R-024 | T04.04 | D-0025 | EXEMPT | 80% | `TASKLIST_ROOT/artifacts/D-0025/evidence.md` |
| R-025 | T04.05 | D-0026 | EXEMPT | 80% | `TASKLIST_ROOT/artifacts/D-0026/evidence.md` |
| R-026 | T05.01 | D-0027 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0027/spec.md` |
| R-027 | T05.02 | D-0028 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0028/evidence.md` |
| R-028 | T05.03 | D-0029 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0029/evidence.md` |
| R-029 | T06.01 | D-0030 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0030/spec.md` |
| R-030 | T06.02 | D-0031 | STANDARD | 75% | `TASKLIST_ROOT/artifacts/D-0031/spec.md` |
| R-031 | T06.03 | D-0032, D-0033 | STRICT | 90% | `TASKLIST_ROOT/artifacts/D-0032/spec.md`, `TASKLIST_ROOT/artifacts/D-0033/evidence.md` |
| R-032 | T06.04 | D-0034 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0034/spec.md`, `TASKLIST_ROOT/artifacts/D-0034/evidence.md` |
| R-033 | T06.05 | D-0035 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0035/evidence.md` |
| R-034 | T06.06 | D-0036, D-0037 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0036/evidence.md`, `TASKLIST_ROOT/artifacts/D-0037/evidence.md` |
| R-035 | T06.07 | D-0038 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0038/evidence.md` |
| R-036 | T06.08 | D-0039 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0039/evidence.md` |
| R-037 | T06.09 | D-0040 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0040/spec.md`, `TASKLIST_ROOT/artifacts/D-0040/evidence.md` |

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

Rules:
- If no command is provided in the roadmap, set `Validation Run` to `Manual`.
- `Evidence Path` must be under `TASKLIST_ROOT/evidence/` (placeholder paths only).

---

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template (do not fabricate contents).

**Template:**
- `# Checkpoint Report — <Checkpoint Title>`
- `**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets; align to checkpoint Verification bullets)
  - ...
  - ...
  - ...
- `## Exit Criteria Assessment` (exactly 3 bullets; align to checkpoint Exit Criteria bullets)
  - ...
  - ...
  - ...
- `## Issues & Follow-ups`
  - List blocking issues; reference `T<PP>.<TT>` and `D-####`
- `## Evidence`
  - Bullet list of intended evidence paths under `TASKLIST_ROOT/evidence/`

---

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`

---

*End of tasklist header — see `tasklist-P1.md` through `tasklist-P6.md` for phase-specific tasks.*
