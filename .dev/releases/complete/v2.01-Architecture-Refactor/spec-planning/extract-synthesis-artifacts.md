# Extracted Patterns from v2.02 Synthesis Artifacts (v2.01-Relevant Only)

**Date**: 2026-02-24
**Source**: `dev-artifacts-synthesis-A.md` and `dev-artifacts-synthesis-B.md`
**Filter**: Only general architectural patterns applicable to the v2.01 systemic refactor. All v2.02-specific content (roadmap command, `claude -p`, T01.xx/T02.xx tasks, D-0001 through D-0008, fallback protocols) excluded.

---

## 1. Specification Structure Patterns (What Makes a Good Spec)

### Spec Evolution Shows a Clear Quality Trajectory

The synthesis documents a spec that scored **5.5/10** on first draft and required addressing **27 findings** (4 CRITICAL, 11 MAJOR, 6 MINOR, 6 SUGGESTION) to reach an acceptable state. Key lessons:

1. **A merged design document is NOT a specification**. The merged-approach (546 lines) had to be formally rewritten into a specification (653 lines v1, then 872 lines v2). Design intent and implementation spec are different artifacts with different quality requirements.

2. **Reflection review before panel review catches different issues**. The pipeline used a two-pass review:
   - Pass 1 (self-reflection): Found 5 critical + 5 important issues (structural, logical)
   - Pass 2 (6-expert panel): Found 27 findings the reflection missed (cross-cutting concerns, schema consistency, edge cases)
   - **Pattern**: Self-review catches structural gaps; external review catches integration defects.

3. **Spec maturity indicators** (from the evolution table):
   - **Immature spec**: Uses generic references ("your section"), inconsistent types across sections, missing edge case handling, no schema versioning policy
   - **Mature spec**: Exact headings with line numbers, consistent types everywhere, explicit error/edge case handling, producer/consumer ownership model, signal-safe cleanup, content validation before injection

4. **Specification sections that were missing from v1 but required for v2**:
   - Schema ownership model (who produces, who consumes, who can change)
   - Content validation before use (empty checks, size limits)
   - Signal-safe resource cleanup (trap-based, not if/then)
   - Budget/cost ceilings
   - Schema evolution/versioning policy
   - Verification sections for each integration point

### General Principle: Specs Must Define Ownership Boundaries

The panel review's CRITICAL findings centered on **ownership ambiguity**: which component owns the schema, which component is responsible for validation, which headings map to which implementation. This pattern applies to all SuperClaude commands/skills:

- Every data contract between components needs explicit producer/consumer ownership
- Every file reference needs exact path, not generic description
- Every threshold/constant needs a single authoritative source

---

## 2. Adversarial Debate as a General QA Pattern

### Pipeline Structure (Generalizable to Any Decision)

The adversarial evaluation followed an 8-stage pipeline that can be abstracted for any architectural decision:

| Stage | Purpose | Quality Gate |
|-------|---------|--------------|
| **Multi-Approach Generation** | Generate 2-3+ competing proposals | Minimum 2 substantively different approaches |
| **Structured Debate** | Advocates argue for each approach with rebuttals | Convergence score >= 0.80 |
| **Quantitative Scoring** | Measurable metrics (50% weight) | Position-bias delta < 5% |
| **Qualitative Scoring** | Binary criteria rubric (50% weight) | All criteria evaluated |
| **Base Selection** | Choose winning approach + absorption plan | Gap between top-2 > 5% |
| **Synthesis/Merge** | Combine best elements with provenance tracking | All absorptions justified |
| **Expert Panel Review** | Multi-persona critique with severity ratings | All CRITICAL findings addressed |
| **Revision** | Address all findings systematically | Score improvement documented |

### Position-Bias Mitigation

The scoring methodology used **forward + reverse passes** to detect position bias. This is a generalizable pattern: whenever multiple options are evaluated, run the evaluation in both orders and check for delta. If delta > 5%, the evaluation is unreliable.

### Convergence Decisions as Decision Records

The debate produced 12 named convergence decisions (C-001 through C-010, U-001, U-002). Each recorded:
- What was decided
- Which approach it came from (absorption, rejection, compromise)
- Why

**General pattern**: Any multi-option architectural decision should produce named, numbered convergence decisions that record provenance.

### YAGNI Enforcement Through Debate

Several debate decisions explicitly rejected features as YAGNI:
- C-004: Rejected user-facing flag for internal routing (over-engineering)
- C-005: Rejected depth-based routing (premature optimization)
- C-009: Rejected reliability testing suite (out of scope)

**Pattern**: Adversarial debate naturally surfaces YAGNI violations because advocates for simpler approaches challenge unnecessary complexity.

---

## 3. Evidence Chain Structure as a Project Management Pattern

### Two-Tier Evidence Model

All evidence followed a consistent structure:
- **Tier 1 (result.md)**: 5-6 lines; result status, validation method, pointer to detailed artifact
- **Tier 2 (artifact)**: Full detailed evidence with specifications, checklists, or policy rationale

**General pattern for any task system**:
- Every task produces a lightweight receipt (status + method + pointer)
- Detailed evidence lives in a separate artifact linked from the receipt
- This separates "did it pass?" from "how do we know?"

### Dependency Chains Create Go/No-Go Gates

The evidence chain had explicit gate points: prerequisites had to PASS before implementation could begin. This is a generalizable pattern:

```
Probe/Validate → Gate Decision → Prerequisites Check → GATE → Implementation
```

**Pattern**: Every phase transition should have an explicit gate with documented pass/fail criteria.

### Evidence Traceability Matrix

Every evidence record linked to:
1. The task that produced it
2. The decision artifact it supports
3. The validation method used

**Pattern**: `Task → Evidence → Decision` traceability should be enforced for any compliance tier above LIGHT.

---

## 4. Compliance Tier Classification Patterns

### Executable Spec Files Are Code, Not Documentation

The T01.03 policy established that `.md` files functioning as executable specifications (SKILL.md, command .md, ref .md) should NOT receive the EXEMPT documentation booster. They are code for compliance purposes.

**General rule for v2.01**: The compliance tier classifier must distinguish between:
- Documentation `.md` (README, guides, changelogs) -> EXEMPT eligible
- Executable `.md` (SKILL.md, command definitions, agent definitions, ref files) -> Classified as code, minimum STANDARD, often STRICT

### Tier Assignment Depends on Functional Impact, Not File Extension

File extension is an unreliable proxy for compliance tier. The determining factor is **what the file controls**:
- Controls agent behavior -> STRICT
- Controls command execution flow -> STRICT
- Provides reference information consumed by agents -> STANDARD minimum
- Pure documentation for humans -> EXEMPT

---

## 5. Why Agents Fail to Follow Instructions (Root Cause Patterns)

### Heading/Instruction Mapping Failures

The expert panel flagged as CRITICAL that the spec used **paraphrased headings** instead of exact SKILL.md headings. When an agent is told to follow instructions from a heading, and that heading doesn't exactly match any heading in the source file, the agent silently fails to find the instruction.

**Root cause pattern**: Agents perform literal string matching on headings. Any paraphrase, abbreviation, or rewording causes a lookup failure. The fix is:
- Use exact headings from source files
- Include line numbers as backup references
- Define a matching algorithm (exact match -> prefix match -> fuzzy match with threshold)

### Schema/Contract Inconsistency

The return contract had field count mismatches across 3 different locations in the spec. When a schema is defined in multiple places, they drift apart. Agents receive conflicting instructions.

**Root cause pattern**: Single-source-of-truth violation. Schemas must be defined in exactly ONE location with all other references pointing to that canonical definition.

### Threshold/Constant Drift

Behavioral thresholds appeared with different values across different artifacts (50% in one place, 70% in another, finally reconciled to different values for different contexts). Agents encountering conflicting thresholds may use whichever they find first.

**Root cause pattern**: Constants and thresholds must have ONE authoritative definition with explicit derivation for any context-specific variants.

### Implicit vs Explicit State Models

The spec evolved from 3-state to 4-state models across versions. When state models are implicit (described in prose rather than enumerated), agents may implement incomplete state machines.

**Root cause pattern**: All state machines, enums, and finite option sets must be explicitly enumerated, not described narratively.

---

## 6. General Spec Quality Indicators

### Consistency Score Pattern (from Synthesis B)

Agent B rated the artifact corpus at **6/10 for consistency**, identifying these failure modes:

| Failure Mode | Example | Impact |
|---|---|---|
| Path naming inconsistency | 24 of 25 artifacts used stale paths | Grep validations fail, cross-references break |
| Type inconsistency | `integer` vs `list[string]` across sections | Schema consumers implement wrong type |
| Threshold inconsistency | 50% vs 70% vs 60% for same concept | Agents use wrong threshold |
| Compound value leakage | `headless+task_agent` leaks implementation detail | Abstraction boundary violated |
| Field count mismatch | "10 fields" claimed but only 5 defined | Agents attempt to produce non-existent fields |

**General quality checklist for any spec**:
1. Are all paths current and verified?
2. Are all types consistent across every mention?
3. Are all thresholds defined in exactly one place?
4. Do all enums/options use simple values (no compound encodings)?
5. Do all counts match actual definitions?

### Completeness Score Pattern (from Synthesis B)

Agent B rated **8/10 for completeness**, with gaps caused by:
- Referenced files that were never created (fixtures, infrastructure refs)
- Referenced artifact IDs with no corresponding files
- Phases referenced in tasklist but with no evidence of execution

**General rule**: Every reference in a spec must resolve to an existing artifact, or be explicitly marked as "TBD" with a creation task.

### Recreation Difficulty as Quality Signal

Artifacts rated EASY to recreate were typically:
- Deterministic (same input always produces same output)
- Mechanical (file existence checks, single-line additions)
- Policy decisions with clear rationale

Artifacts rated HARD to recreate were:
- Creative/emergent (design approaches, debate transcripts)
- Context-dependent (expert panel reviews with line-number references)

**Pattern**: Specifications should strive to make their own recreation EASY by being fully deterministic from their inputs. If a spec is HARD to recreate, it likely contains implicit knowledge that should be made explicit.

---

## 7. Naming Convention Patterns

### The `-protocol` Suffix Rename

During the sprint, all skill directories were renamed to add `-protocol`:
- `sc-adversarial/` -> `sc-adversarial-protocol/`
- `sc-roadmap/` -> `sc-roadmap-protocol/`
- `sc-cleanup-audit/` -> `sc-cleanup-audit-protocol/`
- `sc-task-unified/` -> `sc-task-unified-protocol/`
- `sc-validate-tests/` -> `sc-validate-tests-protocol/`

This rename affected 24 of 25 artifacts (all except the final spec-v2). The systemic cost of a naming convention change mid-sprint was significant: every path reference, grep validation, and line-number cross-reference became stale.

**General lesson for v2.01**: Naming conventions must be established BEFORE specification work begins. A naming change during implementation invalidates all existing references and creates a consistency debt that compounds across every artifact.

---

## 8. Decision Record Structure (Generalizable)

Each decision record followed this pattern:

| Field | Purpose |
|---|---|
| ID | Sequential identifier (D-NNNN) |
| Task | Which task produced this decision |
| Compliance Tier | EXEMPT / LIGHT / STANDARD / STRICT |
| Purpose | One-line description |
| Key Content | What was decided |
| Dependencies | Which prior decisions this depends on |
| Reversibility | Can this decision be undone? At what cost? |

**Pattern for v2.01**: All architectural decisions during the refactor should use this structure, with explicit dependency chains and reversibility assessment.
