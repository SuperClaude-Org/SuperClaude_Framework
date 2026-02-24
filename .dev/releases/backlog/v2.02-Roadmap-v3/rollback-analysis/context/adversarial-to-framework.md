# Adversarial Pipeline to Framework Code: Context Linking Document

**Date**: 2026-02-24
**Analyst**: claude-opus-4-6
**Purpose**: Map every specification decision from the adversarial debate pipeline to its concrete implementation in `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` and related framework files

---

## 1. Decision-to-Code Mapping

This section traces each major specification decision to the exact location in `sc-roadmap-protocol/SKILL.md` where it was implemented.

### 1.1 Wave 2 Step 3 Expansion (3a-3f)

The monolithic "step 3" in Wave 2 was decomposed into six atomic sub-steps. Each sub-step traces to specific artifacts in the adversarial pipeline.

| Sub-Step | SKILL.md Location | Spec Artifact Source | Pipeline Lineage |
|----------|-------------------|---------------------|------------------|
| **3a [Parse agents]** | SKILL.md line 138 | D-0006/spec.md row "3a: Parse agents" | Approach 2 agent spec format -> merged-approach.md "Agent Specification Parsing" -> spec-v1 -> spec-v2 -> D-0006 |
| **3b [Expand variants]** | SKILL.md line 139 | D-0006/spec.md row "3b: Expand variants" | Approach 2 persona assignment -> C-008 (reduced probe) -> merged-approach -> D-0006 |
| **3c [Add orchestrator]** | SKILL.md line 140 | D-0006/spec.md row "3c: Add orchestrator if needed" | Approach 3 convergence tracking (A3-2 in refactoring-plan) -> merged-approach orchestrator pattern -> D-0006 |
| **3d [Execute fallback]** | SKILL.md lines 141-144 | D-0006/spec.md row "3d: Execute fallback protocol" + D-0007/spec.md (full protocol) | C-002 (5-step fallback from Ap3) -> merged-approach fallback protocol -> spec-v1 -> panel review (27 findings) -> spec-v2 -> D-0007 |
| **3e [Consume contract]** | SKILL.md lines 145-153 | D-0006/spec.md row "3e: Consume return contract" + D-0008/spec.md (routing logic) | C-006 (return contract field) -> merged-approach return contract -> spec-v1 -> panel review -> spec-v2 -> D-0008 |
| **3f [Skip template]** | SKILL.md line 154 | D-0006/spec.md row "3f: Skip template" | Approach 2 template bypass logic -> merged-approach -> D-0006 |

**D-0006** (`artifacts/D-0006/spec.md`) is the authoritative specification for the 6-step decomposition. It references task T02.03, roadmap item R-006, and is classified as STRICT tier.

### 1.2 Fallback Protocol (F1, F2/3, F4/5)

| Protocol Stage | SKILL.md Location | D-0007 Spec Section | Adversarial Origin |
|---------------|-------------------|---------------------|-------------------|
| **WARNING emission** | SKILL.md line 141: `Emit WARNING...` | D-0007 TRIGGER block | Approach 2 fallback entry; C-002 enhanced from 3-step to 5-step |
| **F1 [Variant generation]** | SKILL.md line 142 | D-0007 "F1: Variant Generation" | Approach 3 Path B F1 -> C-002 absorption -> merged-approach F1 |
| **F2/3 [Diff + debate]** | SKILL.md line 143 | D-0007 "F2/3: Diff Analysis + Debate (merged)" | Approach 3 F2+F3 merged to reduce Task dispatches -> refactoring-plan A3-1 |
| **F4/5 [Selection + merge + contract]** | SKILL.md line 144 | D-0007 "F4/5: Base Selection + Merge + Contract (merged)" | Approach 3 F4+F5 merged -> refactoring-plan A3-1 |
| **3 error types covered** | SKILL.md line 141: `"this fallback also activates when..."` | D-0007 "3 Error Types Covered" table | Approach 2 primary/fallback architecture -> spec-v2 error handling |
| **convergence_score: 0.5** | SKILL.md line 144: `convergence_score (0.5 # estimated, not measured)` | D-0007 "Contract convergence_score: 0.5" | Deliberate design: see Section 4 (Intentional Gap) below |
| **fallback_mode: true** | SKILL.md line 144: `fallback_mode (true)` | D-0007 "Contract fallback_mode: true" | Approach 3 C-006 -> observability field |

**D-0007** (`artifacts/D-0007/spec.md`) is the authoritative fallback protocol specification. It specifies the 3-stage state machine with merged stages F2/3 and F4/5 to reduce Task agent dispatch overhead.

### 1.3 Return Contract Routing (Step 3e)

| Routing Component | SKILL.md Location | D-0008 Spec Section | Adversarial Origin |
|------------------|-------------------|---------------------|-------------------|
| **Missing-file guard** | SKILL.md line 146 | D-0008 "Missing-File Guard" | spec-v2 addition (panel finding N1: no SKILL.md content validation) |
| **YAML parse error** | SKILL.md line 147 | D-0008 "YAML Parse Error Handling" | spec-v2 addition (panel finding: error handling gaps) |
| **status: success** | SKILL.md line 149 | D-0008 routing table row 1 | Approach 2 return contract -> all specs |
| **status: partial, convergence >= 0.6** | SKILL.md line 150 | D-0008 routing table row 2 | D-0008 threshold decision (see 1.4) |
| **status: partial, convergence < 0.6, --interactive** | SKILL.md line 151 | D-0008 routing table row 3 | Approach 3 interactive fallover -> spec-v2 |
| **status: partial, convergence < 0.6, no --interactive** | SKILL.md line 151 | D-0008 routing table row 4 | spec-v2 non-interactive abort behavior |
| **status: failed** | SKILL.md line 152 | D-0008 routing table row 5 | All approaches agreed on fail-abort |
| **Canonical schema comment** | SKILL.md line 153 | D-0008 "Canonical Schema Comment" | Schema documentation practice from spec-v2 |

**D-0008** (`artifacts/D-0008/spec.md`) is the authoritative return contract routing specification.

### 1.4 Convergence Threshold (0.6)

**Where decided**: D-0008/spec.md, section "Three-Status Routing (convergence threshold: 0.6)".

**SKILL.md implementation**: Line 148: `**Status routing** (convergence threshold: 0.6):`

**Lineage**:
1. Approach 3 introduced convergence as a real metric (not hardcoded)
2. Debate decision C-002 absorbed real convergence tracking from Approach 3
3. merged-approach.md included convergence threshold concept but did not specify the 0.6 value
4. spec-v1 included convergence routing but the specific 0.6 threshold is not documented there
5. Panel review (ADV-7) flagged the "threshold gap" between fallback sentinel (0.5) and routing threshold as a MAJOR finding
6. spec-v2 addressed the threshold gap finding, establishing 0.6 as the explicit routing threshold
7. D-0008 codified 0.6 as the convergence threshold for the SKILL.md implementation

**Rationale** (from dev-artifacts-synthesis-A.md Section 7.3): "Below this, partial results are insufficiently reliable for downstream use."

### 1.5 Orchestrator Threshold Change (>=5 to >=3)

**Discrepancy identified**: The SKILL.md contains two different thresholds for adding the debate-orchestrator agent:

| Location | Threshold | Section |
|----------|-----------|---------|
| SKILL.md line 140 (Wave 2, step 3c) | `agent count >= 3` | Detailed behavioral instruction |
| SKILL.md line 247 (Section 5, Agent Count Rules) | `>= 5 agents` | Summary section |

**Spec artifact source**: D-0006/spec.md row "3c" specifies `agent count >= 3`.

**Adversarial pipeline origin**: The merged-approach.md and spec-v1/spec-v2 discuss the orchestrator in the context of convergence tracking (refactoring-plan item W-7: "Ap3's convergence tracking requires an orchestrator Task agent per round") but do NOT specify a numeric threshold for when the orchestrator is added.

**Assessment**: The >= 3 threshold in step 3c (D-0006) appears to be an implementation-time decision made during the T02.03 sprint execution, not a decision traced through the adversarial pipeline. The >= 5 threshold in Section 5 is a pre-existing value from the original SKILL.md that was not updated to match the new step 3c value. This is an **internal inconsistency** in the SKILL.md file.

---

## 2. Full Pipeline Trace

This section traces the complete path from approach documents through to implemented code for the primary architectural decisions.

### 2.1 Primary Architecture: Fallback Protocol

```
Approach 1 (empirical-probe-first.md)
  -> 13 test cases, 3 strategies
  -> Contributed: behavioral adherence rubric (C-001), reduced probe scope (C-008)

Approach 2 (claude-p-proposal.md)
  -> claude -p as primary invocation, Task-agent as fallback
  -> Score: 0.900 (highest)
  -> SELECTED AS BASE (base-selection.md, ADV-3)

Approach 3 (hybrid-dual-path.md)
  -> Dual-path with runtime routing
  -> Contributed: 5-step fallback upgrade (C-002), real convergence (A3-2),
     invocation_method field (C-006), 3-state mid-pipeline awareness (U-001)

         |
         v

debate-transcript.md (ADV-1)
  -> 2 rounds + final, 12 convergence decisions
  -> Convergence: 1.00
         |
         v

scoring-rubric.md (ADV-2)
  -> Ap1=0.667, Ap2=0.900, Ap3=0.825
         |
         v

base-selection.md (ADV-3)
  -> Approach 2 selected; absorption plan from Ap1 and Ap3
         |
         v

refactoring-plan.md (ADV-4)
  -> 4 absorptions from Ap1, 5 from Ap3
  -> 5 weakness patches, 10 rejections
         |
         v

merged-approach.md (ADV-5)
  -> 8-section unified design, 546 lines
  -> Provenance annotations on each section
         |
         v

specification-draft-v1.md (ADV-6)
  -> 11 sections + 2 appendices, 653 lines
  -> Addressed 10 reflection issues
         |
         v

spec-panel-review.md (ADV-7)
  -> 6 expert reviewers, 27 findings (4 CRITICAL, 11 MAJOR)
  -> Score: 5.5/10
         |
         v

specification-draft-v2.md (ADV-8)
  -> 872 lines, addresses all 27 findings
  -> Corrected -protocol paths, 4-state scan, schema ownership model
         |
         v

T01.01 Probe -> TOOL_NOT_AVAILABLE (D-0001)
  -> Sprint forced to FALLBACK-ONLY variant (D-0002)
         |
         v

D-0003 (Prerequisites: 6/6 PASS) -> Gate cleared
         |
         v

D-0004 (Skill in roadmap.md allowed-tools)
D-0005 (Skill in SKILL.md allowed-tools)
         |
         v

D-0006 (Wave 2 step 3 sub-steps 3a-3f)
D-0007 (Fallback protocol F1, F2/3, F4/5)
D-0008 (Return contract routing in step 3e)
         |
         v

src/superclaude/skills/sc-roadmap-protocol/SKILL.md
  -> Wave 2 Step 3 rewritten with 17 net new lines
  -> Steps 3a-3f, fallback protocol, return contract routing
  -> Skill added to allowed-tools frontmatter
```

### 2.2 Decision Flow Compressed

| Pipeline Stage | Artifact | Key Output | What Survived to SKILL.md |
|---------------|----------|------------|--------------------------|
| Approach generation | AP-1, AP-2, AP-3 | 3 competing designs | AP-2 as base; AP-1 behavioral rubric concept; AP-3 enhanced fallback + convergence |
| Debate | ADV-1 | 12 convergence decisions | C-002 (5-step fallback), C-006 (invocation_method), U-001 (3-state awareness) |
| Scoring + Selection | ADV-2, ADV-3 | AP-2 wins at 0.900 | Primary/fallback architecture (not dual-path) |
| Synthesis | ADV-4, ADV-5 | Merged design with absorptions | F1-F5 fallback structure, return contract schema |
| Spec v1 | ADV-6 | 653-line formal spec | Wave 2 step 3 decomposition concept |
| Panel review | ADV-7 | 27 findings | Threshold gap identified; field count mismatch; error handling gaps |
| Spec v2 | ADV-8 | 872-line revised spec | All 27 findings addressed; path corrections; schema refinements |
| Implementation | D-0006, D-0007, D-0008 | Implementation specs | Direct source for SKILL.md code changes |

---

## 3. Spec v2 Improvements: Implemented vs Pending

### 3.1 Implemented in SKILL.md

| spec-v2 Improvement | SKILL.md Evidence | Status |
|---------------------|-------------------|--------|
| Fallback protocol (F1, F2/3, F4/5) | Lines 141-144 (step 3d) | IMPLEMENTED |
| Return contract routing with 3-status logic | Lines 145-152 (step 3e) | IMPLEMENTED |
| Missing-file guard for return-contract.yaml | Line 146 | IMPLEMENTED |
| YAML parse error handling | Line 147 | IMPLEMENTED |
| Convergence threshold 0.6 | Line 148 | IMPLEMENTED |
| Fallback convergence sentinel 0.5 with comment | Line 144 (`convergence_score (0.5 # estimated, not measured)`) | IMPLEMENTED |
| Template skip on adversarial success | Line 154 (step 3f) | IMPLEMENTED |
| Agent parsing algorithm reference | Line 138 (step 3a) | IMPLEMENTED |
| Variant expansion with persona assignment | Line 139 (step 3b) | IMPLEMENTED |
| Orchestrator agent addition | Line 140 (step 3c) | IMPLEMENTED (threshold discrepancy: >=3 vs >=5) |
| `Skill` added to allowed-tools | Frontmatter line 4 | IMPLEMENTED |
| 3 error types triggering fallback | Line 141 parenthetical | IMPLEMENTED |
| `fallback_mode: true` in contract | Line 144 | IMPLEMENTED |
| Canonical schema comment | Line 153 | IMPLEMENTED |
| Path corrected to `sc-adversarial-protocol` | N/A (implicit in skill invocation context) | IMPLEMENTED (via directory rename) |

### 3.2 NOT Implemented (Still Pending from spec-v2)

| spec-v2 Requirement | Where in spec-v2 | Status | Notes |
|---------------------|------------------|--------|-------|
| **`unresolved_conflicts` as `list[string]`** | spec-v2 schema section (panel finding) | NOT IMPLEMENTED | D-0007 still uses `unresolved_conflicts: 0 # count of unresolved` (integer). SKILL.md line 144 uses `count of unresolved` phrasing. spec-v2 mandated `list[string]` for actionable detail |
| **`invocation_method` field in contract** | spec-v2 schema; C-006 debate decision | NOT IMPLEMENTED | D-0007 return contract schema lists 7 fields; `invocation_method` is absent. spec-v2 mandated it as observability field |
| **4-state artifact scan model** | spec-v2 (States A/B/C/D vs original A/B/C) | NOT IMPLEMENTED | SKILL.md step 3d does not implement directory scanning before fallback. Fallback executes unconditionally in fallback-only variant |
| **Signal-safe CLAUDECODE env restore (`trap EXIT`)** | spec-v2 (panel finding about env leak) | NOT APPLICABLE | Only relevant for headless `claude -p` path, which is unavailable |
| **SKILL.md content validation (empty check + ARG_MAX)** | spec-v2 (panel finding N1) | NOT IMPLEMENTED | No pre-injection validation of SKILL.md size or emptiness |
| **Schema ownership model (producer/consumer)** | spec-v2 schema evolution policy | NOT IMPLEMENTED | No versioning or ownership declaration in contract |
| **Budget ceiling (total adversarial = 2x BUDGET)** | spec-v2 (panel finding about cost) | NOT IMPLEMENTED | No budget enforcement in SKILL.md |
| **Probe cost corrected to <= $2.15** | spec-v2 (corrected arithmetic) | NOT APPLICABLE | No probe executed (fallback-only) |
| **Behavioral threshold: 14/20 headless, 12/20 fallback** | spec-v2 (reconciled from inconsistent values) | NOT APPLICABLE | No behavioral adherence testing implemented |
| **Mid-pipeline recovery tests** | spec-v2 (panel finding C1) | NOT IMPLEMENTED | No test artifacts for fallback recovery |
| **`refs/headless-invocation.md`** | spec-v2, approach-2, merged-approach | NEVER CREATED | Referenced but file does not exist |
| **Probe fixtures** (`spec-minimal.md`, `variant-a.md`, etc.) | spec-v2, approach-1 | NEVER CREATED | Referenced but files do not exist |
| **`expected-schema.yaml`** | approach-1 Appendix B | NEVER CREATED | Schema validation file never produced |
| **Stderr capture to temp file** | spec-v2 (replacing `2>/dev/null`) | NOT APPLICABLE | Only relevant for headless path |
| **Exact SKILL.md heading matching algorithm** | spec-v2 (replacing paraphrased headings) | NOT IMPLEMENTED | Instruction delivery uses ref file references, not heading matching |
| **Schema version field `schema_version: "1.0"`** | spec-v2 schema section | NOT IMPLEMENTED | Not present in D-0007 contract or SKILL.md |

### 3.3 Summary

- **Implemented**: 15 items -- all core fallback protocol, routing logic, and structural changes
- **Not implemented (applicable)**: 8 items -- mostly schema refinements, validation checks, and tooling
- **Not applicable**: 5 items -- related to headless `claude -p` path which is unavailable
- **Never created**: 3 items -- referenced files that were never produced

---

## 4. The Intentional Gap: Fallback Convergence (0.5) < Routing Threshold (0.6)

### 4.1 The Design

| Parameter | Value | Defined In | SKILL.md Location |
|-----------|-------|-----------|-------------------|
| Fallback convergence sentinel | 0.5 | D-0007/spec.md | Line 144: `convergence_score (0.5 # estimated, not measured)` |
| Routing convergence threshold | 0.6 | D-0008/spec.md | Line 148: `(convergence threshold: 0.6)` |

### 4.2 Why This Is Intentional

The fallback protocol in F4/5 writes `convergence_score: 0.5` as a fixed sentinel because convergence is not actually measured during fallback execution (hence the comment `# estimated, not measured`). The routing logic in step 3e uses 0.6 as the threshold for "proceed without user intervention."

Because 0.5 < 0.6, fallback results will **always** trigger the `status: partial AND convergence_score < 0.6` routing path, which means:
- With `--interactive`: user is prompted to approve low-convergence results
- Without `--interactive`: execution aborts with threshold message

This is by design. As documented in dev-artifacts-synthesis-A.md Section 7.3:
- **Convergence threshold 0.6** rationale: "Below this, partial results are insufficiently reliable for downstream use"
- **Fallback convergence sentinel 0.5** rationale: "Deliberately below 0.6 threshold; forces partial/low-convergence path"

### 4.3 Behavioral Consequence

In the current fallback-only environment, the only way to successfully complete multi-roadmap generation is:

1. The fallback protocol succeeds and writes `status: success` (not partial) -- in which case convergence threshold is irrelevant
2. The user passes `--interactive` and approves low-convergence results when prompted
3. The fallback protocol happens to resolve all conflicts, setting `status: success`

If the fallback writes `status: partial` (any unresolved conflicts), the 0.5 sentinel guarantees the low-convergence abort path activates without `--interactive`.

### 4.4 Pipeline Trace for This Decision

```
Approach 3 (hybrid-dual-path.md)
  -> Introduced real convergence tracking concept
       |
       v
C-002 (debate convergence decision)
  -> Absorbed 5-step fallback with real convergence from Ap3
       |
       v
refactoring-plan.md item A3-2
  -> "Replace hardcoded 0.5 sentinel with per-point convergence computation"
       |
       v
merged-approach.md
  -> Convergence tracking via orchestrator Task agent (real measurement)
       |
       v
spec-v1, spec-v2
  -> Real convergence replaces sentinel (for headless path)
  -> Panel review flagged "threshold gap" as MAJOR finding
       |
       v
D-0002 (FALLBACK-ONLY variant decision)
  -> Real convergence tracking NOT available in fallback
  -> 0.5 sentinel retained as fallback-specific value
       |
       v
D-0007 (convergence_score: 0.5)
D-0008 (convergence threshold: 0.6)
  -> Gap is intentional: fallback results are lower-confidence
       |
       v
SKILL.md
  -> Both values implemented exactly as specified
```

The key insight: spec-v2 mandated real convergence tracking (replacing the 0.5 sentinel), but this was for the headless `claude -p` path. When the fallback-only variant was selected (D-0002), real convergence tracking was not feasible (Task agents cannot compute inter-variant agreement scores), so the 0.5 sentinel was retained for the fallback path only. The 0.6 routing threshold was kept from the spec to maintain the designed quality gate.

---

## 5. Unimplemented Spec Requirements

### 5.1 Categorized by Implementation Priority

**HIGH priority** (affect correctness or safety):

| Requirement | spec-v2 Source | Impact |
|-------------|---------------|--------|
| `unresolved_conflicts` should be `list[string]` | Panel finding (type mismatch) | Integer loses conflict detail; consumers cannot act on specific conflicts |
| `invocation_method` field in return contract | C-006 debate decision, spec-v2 schema | Observability gap: cannot distinguish invocation path in logs |
| Schema version field `schema_version: "1.0"` | spec-v2 schema evolution policy | No versioning for contract evolution |
| SKILL.md content validation (empty + ARG_MAX) | Panel finding N1 | Silent failure on empty or oversized SKILL.md injection |

**MEDIUM priority** (affect robustness):

| Requirement | spec-v2 Source | Impact |
|-------------|---------------|--------|
| 4-state artifact scan (A/B/C/D) | spec-v2 (expanded from 3-state) | Mid-pipeline resume cannot detect existing artifacts |
| Budget ceiling (2x BUDGET) | Panel finding (no cost guard) | Unbounded adversarial cost |
| Schema ownership model | spec-v2 schema section | No producer/consumer contract for evolution |

**LOW priority** (documentation/tooling):

| Requirement | spec-v2 Source | Impact |
|-------------|---------------|--------|
| `refs/headless-invocation.md` | Multiple references | Missing infrastructure file (not needed for fallback-only) |
| Probe fixtures | approach-1, spec-v2 | Missing test fixtures (not needed for fallback-only) |
| `expected-schema.yaml` | approach-1 Appendix B | Missing schema validation file |
| Heading matching algorithm | spec-v2 instruction delivery | Fragile line-number references not yet replaced |
| Mid-pipeline recovery tests | Panel finding C1 | No test coverage for fallback recovery scenarios |

### 5.2 Internal Inconsistency (Not from spec-v2)

| Issue | Location | Resolution Needed |
|-------|----------|------------------|
| Orchestrator threshold: `>= 3` in step 3c vs `>= 5` in Section 5 | SKILL.md lines 140 and 247 | Align to one value. D-0006 specifies >=3; Section 5 retains pre-sprint value of >=5 |

---

## 6. Cross-Reference Index

### 6.1 Artifact Paths (All Relative to Repo Root)

**Adversarial pipeline artifacts**:
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/debate-transcript.md` (ADV-1)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/scoring-rubric.md` (ADV-2)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/base-selection.md` (ADV-3)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/refactoring-plan.md` (ADV-4)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/merged-approach.md` (ADV-5)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/specification-draft-v1.md` (ADV-6)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/spec-panel-review.md` (ADV-7)
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/specification-draft-v2.md` (ADV-8)

**Decision artifacts**:
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0001/evidence.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0002/notes.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0003/evidence.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0004/evidence.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0005/evidence.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0006/spec.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0007/spec.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0008/spec.md`

**Framework file**:
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

**Synthesis documents (this analysis depends on)**:
- `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-artifacts-synthesis-A.md`
- `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-artifacts-synthesis-B.md`
- `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/framework-synthesis-A.md`

### 6.2 Key Line References in SKILL.md

| Line(s) | Content | Traced To |
|---------|---------|-----------|
| 4 | `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` | D-0004, D-0005 |
| 138 | Step 3a [Parse agents] | D-0006 |
| 139 | Step 3b [Expand variants] | D-0006 |
| 140 | Step 3c [Add orchestrator if needed] -- threshold >=3 | D-0006 |
| 141 | Step 3d [Execute fallback protocol] -- WARNING + 3 error types | D-0006, D-0007 |
| 142 | F1 [Variant generation] | D-0007 |
| 143 | F2/3 [Diff analysis + debate] | D-0007 |
| 144 | F4/5 [Base selection + merge + contract] -- convergence 0.5 sentinel | D-0007 |
| 145-146 | Step 3e -- missing-file guard | D-0008 |
| 147 | Step 3e -- YAML parse error handling | D-0008 |
| 148-152 | Step 3e -- 3-status routing, convergence threshold 0.6 | D-0008 |
| 153 | Canonical schema comment | D-0008 |
| 154 | Step 3f [Skip template] | D-0006 |
| 247 | Agent Count Rules -- threshold >=5 (inconsistent with line 140) | Pre-existing; not updated by sprint |
