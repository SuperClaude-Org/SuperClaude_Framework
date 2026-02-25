# Batch 6: Adversarial Specification Artifacts (Part 2)

**Analysis Date**: 2026-02-24
**Scope**: Adversarial pipeline specification drafts and their merged-approach source document
**Files Analyzed**: 3

---

## File Inventory

| # | File | Path (relative) | Lines | Purpose |
|---|------|-----------------|-------|---------|
| 1 | `specification-draft-v1.md` | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/` | 653 | First formal specification for `claude -p` headless invocation in sc:roadmap |
| 2 | `specification-draft-v2.md` | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/` | 872 | Revised specification incorporating 27 expert panel review findings |
| 3 | `merged-approach.md` | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/` | 546 | Upstream source: merged adversarial debate output that served as the base for both specification drafts |

---

## 1. merged-approach.md

### Content Summary

This is the **upstream source document** -- the output of the adversarial debate pipeline that produced the design approach for wiring `claude -p` headless CLI invocation into the sc:roadmap sprint tasklist. It merges three competing approaches:

- **Approach 2 (Base, score 0.900)**: `claude -p` as primary invocation mechanism
- **Approach 1 (Absorbed)**: Behavioral adherence testing, 20-point rubric, multi-round verification
- **Approach 3 (Absorbed)**: Enhanced 5-step fallback (F1-F5), mid-pipeline awareness (3-state model), `invocation_method` field

Key rejected elements:
- Approach 3's `--invocation-mode` flag (YAGNI)
- Approach 3's depth-based routing (premature optimization)
- Approach 1's full 13-test probe (over-scoped)

### Structure

The document is organized into 8 sections:
1. **Philosophy**: `claude -p` as primary, Task-agent fallback as secondary, return contract as abstraction boundary
2. **Invocation Design**: Command template with `--append-system-prompt`, `--dangerously-skip-permissions`, `--output-format json`, `--max-budget-usd`; CLAUDECODE env handling; error detection matrix (8 conditions)
3. **Sprint-Spec Modifications**: Task 0.0 replacement (4-test viability probe), Tasks 1.1-1.2 (allowed-tools), Task 1.3 (Wave 2 step 3d complete rewrite with 3d-i through 3d-iv sub-steps), Task 1.4 (fallback designation), Epic 2 and Epic 3 changes
4. **New Infrastructure**: `refs/headless-invocation.md` reference file, probe fixtures, inline Bash decision
5. **Risk Register**: 7 risks (R1-R7)
6. **Verification Plan**: Pre-implementation probe, structural audit (8-point), behavioral adherence rubric (20-point, 70% threshold), multi-round debate grep verification, end-to-end test
7. **Summary of Modifications**: 17-row change matrix
8. **Fallback-Only Sprint Variant**: Upgrade from 3-step to 5-step if headless path is blocked

### Key Design Decisions

- SKILL.md path uses `sc-adversarial/SKILL.md` (old naming, before rename to `sc-adversarial-protocol`)
- Return contract schema: 10 fields (9 original + 1 new `invocation_method`), claimed as "v1.1"
- `invocation_method` allows compound value `"headless+task_agent"` for mid-pipeline recovery
- `unresolved_conflicts` typed as integer
- 3-state artifact scan model (States A, B, C)
- Fallback behavioral adherence threshold: 10/20 (50%)
- Stderr discarded via `2>/dev/null`
- No SKILL.md content validation
- No combined budget ceiling for headless + fallback

### Provenance Annotations

The document uses HTML comments (`<!-- Source: Approach N, Section -->`) throughout to trace each section back to its originating approach. This is a direct output of the adversarial merge protocol.

---

## 2. specification-draft-v1.md

### Content Summary

The first formal specification draft (Version 1.0-draft, dated 2026-02-23) that transforms the merged approach into an implementable sprint specification. It addresses 5 critical issues and 5 important issues identified during a reflection review of the merged approach.

### Structure (11 sections + 2 appendices)

0. **Document Purpose & Scope**: Scope boundaries (in/out), Task ID mapping table connecting merged-approach informal names to sprint task IDs (T01.01-T06.05)
1. **Philosophy**: Identical to merged approach but with stronger framing of primary/fallback hierarchy
2. **Invocation Design**: Command template (with `HEADLESS_OUTPUT` capture), parameter configuration table, output parsing, CLAUDECODE handling, error detection matrix (8 conditions)
3. **Sprint-Spec Modifications**: 12 sub-sections (T01.01 through T05.03) with full rewrite specifications
4. **New Infrastructure**: `refs/headless-invocation.md` (8 required contents), probe fixtures, inline Bash decision
5. **Instruction Delivery Protocol**: Heading-based extraction from SKILL.md for Task agent dispatch (4-row mapping table)
6. **Risk Register**: 7 risks (R1-R7), same as merged approach
7. **Verification Plan**: 5 sections (pre-implementation, structural audit 8-point, behavioral adherence 20-point, multi-round grep, end-to-end)
8. **Glossary Updates**: 4 updated + 2 new terms
9. **Deliverable Updates**: 5 deliverable descriptions updated
10. **Summary of All Modifications**: 22-row change matrix (expanded from merged approach's 17)
11. **Fallback-Only Sprint Variant**: Same upgrade path

### Key Additions Over merged-approach.md

1. **Task ID Mapping** (Section 0): Full table connecting informal task names to sprint IDs, resolving critical issue C2
2. **Phase 3 Task Specifications** (Sections 3.5, 3.6): T03.01 (4-check wiring validation) and T03.02 (8-point structural audit) -- previously unaddressed, resolving C3
3. **Permission Flag Standardization** (Section 2.1): Documented rationale for `--dangerously-skip-permissions` over `--permission-mode bypassPermissions`, resolving C1
4. **Schema Version Clarification** (Section 3.7): `schema_version: "1.0"` is correct; "v1.1" in merged approach was an error, resolving C5
5. **Glossary Corrections** (Section 8): Updated 4 definitions + 2 new terms, resolving C4
6. **Instruction Delivery Protocol** (Section 5): Heading-based extraction method defined, resolving I4
7. **SKILL.md Line 141 Replacement** (Section 3.4): Exact replacement text for the "sole mechanism" line, resolving I1
8. **Deliverable Registry Updates** (Section 9): 5 deliverable descriptions corrected, resolving I5

### Retained Issues (Carried Forward to v2)

- SKILL.md path still uses old name `sc-adversarial/SKILL.md`
- `unresolved_conflicts` typed as integer (not `list[string]`)
- `invocation_method` allows compound value `"headless+task_agent"`
- 3-state artifact scan model (not 4-state)
- No SKILL.md content validation or ARG_MAX handling
- No stderr capture
- No signal-safe CLAUDECODE restore (no `trap EXIT`)
- No combined budget ceiling
- No concrete examples for artifact scan states
- Behavioral adherence rubric not executable (no grep patterns)
- Fallback threshold at 50% (10/20) without justification
- No mid-pipeline recovery tests
- No schema transition tests
- No budget exceeded test
- Prompt enumerates all 10 contract fields (prompt-schema coupling)
- Schema defined in multiple places
- Probe fixtures lack specified content differences

---

## 3. specification-draft-v2.md

### Content Summary

The substantially revised specification (Version 2.0-draft, dated 2026-02-23) incorporating all 27 findings from an expert panel review of v1. The v1 was scored 5.5/10 by the panel. The v2 addresses 4 CRITICAL, 11 MAJOR, 6 MINOR, and 6 SUGGESTION findings.

### Structure (11 sections + 3 appendices)

Same 11-section structure as v1, with significant expansions:

0. **Document Purpose & Scope**: Added **Schema Ownership Model** (producer vs consumer field ownership, dual-format handling, schema contract invariant)
1. **Philosophy**: Added note about schema ownership and consumer defaults
2. **Invocation Design**: Major rewrite -- SKILL.md path corrected to `sc-adversarial-protocol/SKILL.md`, content validation added (empty check + ARG_MAX warning at 1.5MB), stderr captured to temp file, `trap EXIT` for signal-safe CLAUDECODE restore, prompt simplified to reference "your Return Contract (FR-007) section" instead of enumerating fields, **total adversarial budget ceiling** (2x BUDGET), error matrix expanded to 11 conditions
3. **Sprint-Spec Modifications**: T01.01 adds pre-test cleanup and concrete grep checks for test 4, cost breakdown ($2.15 total); T02.03 expanded to **4-state artifact scan** (added State D: debate-transcript exists); T03.01 expanded to 5-point checklist (added SKILL.md path verification); T03.02 expanded to 9-point checklist (added dual-format handling check, directory normalization check); T04.01 completely rewritten with **field inventory** (5 producer + 2 consumer-existing + 3 new = 10), dual-format handling spec, schema evolution policy, `unresolved_conflicts` corrected to `list[string]`, `invocation_method` simplified to simple enum (no compound values)
4. **New Infrastructure**: `refs/headless-invocation.md` expanded to 10 required contents, probe fixtures given specified structural/content differences
5. **Instruction Delivery Protocol**: Exact SKILL.md headings with line numbers, summary vs implementation-details distinction, substring matching algorithm
6. **Risk Register**: Expanded to 9 risks (added R8: SKILL.md read failure/ARG_MAX, R9: headless+fallback cost doubling)
7. **Verification Plan**: Expanded to 9 sections (added 7.6 mid-pipeline recovery tests for States B/C/D, 7.7 schema transition tests for 5-field/10-field/unknown-version, 7.8 budget exceeded test, 7.9 invocation method logging test); behavioral adherence rubric now includes grep verification column; fallback threshold raised to 60% (12/20) with documented rationale
8-9. **Glossary and Deliverable Updates**: Mid-pipeline awareness updated to "4-state"; deliverables updated for new checklist counts
10. **Summary**: Expanded to include T06.01 AC correction for `unresolved_conflicts` type
11. **Fallback-Only Sprint Variant**: Added directory structure normalization note

### Appendix C (New): Panel Findings Resolution

Complete 27-row table documenting every panel finding (W1-W6, F1-F4, S1-S5, A1-A5, N1-N5, C1-C5) with severity and resolution in v2.

---

## Evolution Analysis

### Lineage

```
merged-approach.md (adversarial debate output, convergence 1.00)
    |
    +-- [reflection review identifies 5 critical + 5 important issues]
    |
    v
specification-draft-v1.md (formal spec, addresses 10 reflection issues)
    |
    +-- [expert panel review scores 5.5/10, identifies 27 findings]
    |
    v
specification-draft-v2.md (revised spec, addresses all 27 panel findings)
```

### Key Evolutionary Changes

| Aspect | merged-approach | spec-v1 | spec-v2 |
|--------|----------------|---------|---------|
| SKILL.md path | `sc-adversarial/` | `sc-adversarial/` | `sc-adversarial-protocol/` |
| Artifact scan states | 3 (A/B/C) | 3 (A/B/C) | 4 (A/B/C/D) |
| `unresolved_conflicts` type | integer | integer | `list[string]` |
| `invocation_method` values | headless, task_agent, headless+task_agent | headless, task_agent, headless+task_agent | headless, task_agent (only) |
| Schema ownership | Not addressed | Not addressed | Producer/consumer model with dual-format handling |
| SKILL.md content validation | None | None | Empty check + ARG_MAX warning |
| Stderr handling | Discarded (`2>/dev/null`) | Discarded (`2>/dev/null`) | Captured to temp file |
| CLAUDECODE restore | Basic if/then | Basic if/then | `trap EXIT` signal-safe |
| Budget ceiling | Per-invocation only | Per-invocation only | Total adversarial = 2x BUDGET |
| Fallback threshold | 10/20 (50%) | 14/20 (70%) headless only | 14/20 headless, 12/20 fallback (with rationale) |
| T03.01 checks | Not addressed | 4-point | 5-point |
| T03.02 checks | Not addressed | 8-point | 9-point |
| Risk count | 7 | 7 | 9 |
| Verification sections | 5 | 5 | 9 |
| Prompt field enumeration | All 10 fields listed | All 10 fields listed | References "your FR-007 section" |
| Schema evolution policy | None | None | Minor/major versioning with consumer behavior rules |
| Probe cost estimate | ~$4 | ~$4 | <= $2.15 (corrected arithmetic) |
| Probe idempotency | Not addressed | Not addressed | Pre-test cleanup step |
| Instruction heading mapping | By section heading (generic) | Paraphrased headings | Exact SKILL.md headings with line numbers + matching algorithm |

### Cross-References

**To sprint tasklist (tasklist-P6.md)**:
- Task ID mapping table in both spec versions maps to T01.01-T06.05
- Glossary updates target the glossary section in tasklist-P6.md
- Deliverable registry updates target D-0001, D-0002, D-0007, D-0009, D-0010

**To sc:adversarial SKILL.md** (`src/superclaude/skills/sc-adversarial-protocol/SKILL.md`):
- System prompt injection reads full SKILL.md content
- Instruction delivery protocol (Section 5) maps fallback steps F2-F5 to specific SKILL.md headings
- Return contract schema references FR-007 in SKILL.md
- `unresolved_conflicts` type correction references SKILL.md lines 1551-1554

**To sc:roadmap SKILL.md** (`src/superclaude/skills/sc-roadmap-protocol/SKILL.md`):
- Wave 2 step 3d rewrite targets the adversarial invocation step
- Wave 1A step 2 uses the same pattern for Mode A
- Return contract consumption in step 3e
- Canonical schema comment at line 153

**To new infrastructure files**:
- `src/superclaude/skills/sc-roadmap-protocol/refs/headless-invocation.md` (to be created)
- `src/superclaude/skills/sc-roadmap-protocol/fixtures/probe-variant-a.md` (to be created)
- `src/superclaude/skills/sc-roadmap-protocol/fixtures/probe-variant-b.md` (to be created)

**Between the three files**:
- merged-approach.md is the source for both spec drafts (cited in headers)
- spec-v1 cites the reflection review that identified issues in the merged approach (Appendix A, B)
- spec-v2 cites the panel review of spec-v1 (Appendix C, 27 findings)
- spec-v2 documents all changes from v1 in its Section 2.2 "Key changes from v1" note

**To renamed skill directories** (from git status):
- The merged approach uses old path `sc-adversarial/SKILL.md`
- spec-v1 also uses old path `sc-adversarial/SKILL.md`
- spec-v2 corrects to `sc-adversarial-protocol/SKILL.md` (matching the rename visible in git status)

---

## Summary

These three files represent a complete design-through-specification pipeline for the `claude -p` headless invocation feature:

1. **merged-approach.md** is the raw adversarial debate output -- a design document with provenance annotations tracing each decision to its source approach. It establishes the architecture (headless primary, 5-step fallback, return contract abstraction) but contains several inconsistencies and gaps.

2. **specification-draft-v1.md** formalizes the merged approach into an implementable specification, adding task ID mapping, Phase 3 task specifications, and resolving 10 reflection-identified issues. However, it carries forward multiple technical issues from the merged approach.

3. **specification-draft-v2.md** is the mature specification that addresses all 27 panel findings. It introduces the schema ownership model, dual-format contract handling, 4-state artifact scan, signal-safe environment handling, combined budget ceiling, executable verification patterns, and comprehensive test coverage. This is the document closest to implementation-ready state.

The evolution demonstrates a rigorous quality pipeline: adversarial debate produces a merged design, reflection identifies structural issues, formal specification addresses them, expert panel review catches remaining gaps, and a final revision resolves everything. The v2 is roughly 33% larger than v1 (872 vs 653 lines) despite being about the same core feature, reflecting the additional robustness in error handling, testing, and schema management.
