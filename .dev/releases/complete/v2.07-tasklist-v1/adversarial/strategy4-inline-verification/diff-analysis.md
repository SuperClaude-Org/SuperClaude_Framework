# Diff Analysis — Strategy 4: Inline Verification Coupling

**Pipeline Step**: 1 of 5
**Date**: 2026-03-04
**Strategy**: Add inline verification coupling per task — require near-field completion criterion, reject tasks lacking explicit completion condition.

---

## 1. Source Documents Analyzed

| Document | Role |
|---|---|
| `tasklist-spec-integration-strategies.md` §4 | Strategy 4 proposal (integration-strategies doc) |
| `taskbuilder-integration-proposals.md` Proposal 5 | Expanded form of the same pattern (Inline Verification Clauses) |
| `sc-tasklist-command-spec-v1.0.md` §6B, §8 | Mutation targets in the base spec |
| `Tasklist-Generator-Prompt-v2.1-unified.md` §4.7, §6B, §8 | Live v3.0 generator — existing verification handling |
| `tasklist-generation-pipeline-prd.md` | PRD context, v1.0 parity constraint anchor |

---

## 2. Structural Differences Between Strategy 4 and Existing v3.0 Behavior

### 2.1 What v3.0 Currently Does for Verification

The v3.0 generator (Tasklist-Generator-Prompt-v2.1-unified.md) already provides the following verification-related constructs at the task level:

| Construct | Location | Content |
|---|---|---|
| `Verification Method` | §6B task metadata table (row) | Tier-routed method: Sub-agent / Direct test / Sanity check / Skip |
| `Acceptance Criteria` | §6B task body (4 bullets, mandatory) | Functional, quality, determinism, documentation criteria |
| `Validation` | §6B task body (2 bullets, mandatory) | Verbatim command or `Manual check: <what>` + `Evidence: <path>` |
| `Verification Method` determination | §4.10 | Routing table: tier → method, token budget, timeout |

### 2.2 What Strategy 4 Proposes

Strategy 4 proposes two concrete changes:

**Change A** (§6B template): Each task block must include a **near-field completion criterion** — a verification element located close to the task action content, not separated into a remote validation section.

**Change B** (§8 Self-Check): Add a new check: "Reject tasks lacking explicit completion condition."

### 2.3 Structural Delta

| Dimension | v3.0 Current State | Strategy 4 Proposed State |
|---|---|---|
| Verification proximity | `Validation` section is at task end (far-field, after Steps + Acceptance Criteria) | Completion criterion must appear near-field (adjacent to action content) |
| Enforcement point | No self-check verifies per-task completion condition presence | §8 self-check rejects tasks missing explicit completion condition |
| Schema impact | No new fields if "near-field" maps to existing Acceptance Criteria row 1 | Possibly requires a new `Completion:` or `Done-When:` field if "near-field" means a distinct element |
| Rejection gate | Self-check verifies structural format (file existence, IDs, heading format) | Self-check upgraded to verify semantic completeness (completion condition presence) |

---

## 3. Content Differences

### 3.1 Overlap With Existing Content

v3.0 §4.7 already mandates:
- **Acceptance Criteria**: exactly 4 bullets (functional, quality, determinism, documentation)
- **Validation**: exactly 2 bullets (command/manual + evidence)

These together constitute a completion condition. The gap is:
1. They are formatted as named sections at the bottom of the task block — they are "far-field" relative to the action title.
2. The §8 self-check does not currently verify their presence or content quality.

### 3.2 Duplication Risk

If Strategy 4 adds a new `Completion:` field while retaining `Acceptance Criteria` and `Validation`, three constructs will independently describe "done" state for every task. This creates:
- Authoring burden (generator must produce three distinct but related descriptions)
- Potential contradiction (field A says X, field B says Y)
- Executor confusion (which field governs completion?)

### 3.3 Integration Strategies vs. Taskbuilder Proposals: Two Descriptions of the Same Strategy

The integration-strategies doc (Strategy 4) is sparse:
> "Ensure each task includes its success condition near task content."
> "Reject tasks lacking explicit completion condition."

The taskbuilder-integration-proposals doc (Proposal 5) is more specific:
> Add a `Verify:` field to §6B task format containing 1–3 concrete, testable criteria (output existence, behavioral correctness, quality constraint).
> Add §5.5 Verification Clause Generation to the enrichment pipeline.
> Upgrade §8 self-check to require non-empty `Verify:` field.

The taskbuilder proposal operationalizes the strategy. Both must be analyzed together.

---

## 4. Contradictions Between Strategy 4 and v3.0

| # | Contradiction | Severity |
|---|---|---|
| C1 | v3.0 §4.7 mandates exactly 4 Acceptance Criteria bullets; Strategy 4 adds a separate completion criterion in near-field position. Two completion signals exist simultaneously. | Medium |
| C2 | v3.0 §6B task format is a fixed schema with 16 metadata rows + named sections. Adding `Verify:` as a 17th row (or separate section) is schema expansion — directly at odds with "no schema expansion required" claim in integration-strategies §4. | Medium-High |
| C3 | v3.0 §8 self-check is structural only (file existence, ID format, heading format, no prohibited sections). Upgrading it to semantic validation (completion condition presence) changes the nature of the self-check from format-gating to content-gating. | Low-Medium |
| C4 | "Near-field" is undefined in Strategy 4. If it means "within the metadata table," it conflicts with the existing `Verification Method` row already in the table. If it means "in the task body before Steps," it requires a new structural position that doesn't exist in v3.0. | High |

---

## 5. Unique Contributions of Strategy 4

Items present in Strategy 4 not covered by any existing v3.0 construct:

1. **Proximity enforcement**: The explicit requirement that the completion criterion be near-field (co-located with action) is not present in v3.0. Current `Validation` appears after Steps and Acceptance Criteria — it is functionally far-field.

2. **Rejection gate in self-check**: v3.0 §8 currently does not verify that completion conditions are present and non-empty. Strategy 4 adds a semantic gate.

3. **Reduction of executor search distance**: An executor processing a task must currently scan the full task block to find the completion signal. Near-field placement reduces search distance to near zero.

---

## 6. Key Findings for Debate

| Finding | Implication |
|---|---|
| v3.0 already has completion criteria (Acceptance Criteria + Validation) but they are structurally far-field | Strategy 4 addresses a real proximity gap |
| "No schema expansion required" claim in integration-strategies §4 is inaccurate if a new field is added | The claim depends on whether "near-field" means repositioning vs. new field |
| Parity constraint (v1.0 = functional parity with v3.0) would be broken if task format changes | Any field addition changes output format |
| §8 semantic upgrade is the lower-risk sub-component | Adding a self-check without changing task format is parity-safe |
| The two sub-components (format change + self-check upgrade) should be evaluated independently | They have different risk profiles |
