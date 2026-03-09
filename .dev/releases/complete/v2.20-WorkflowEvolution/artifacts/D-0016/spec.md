# Severity Classification: Deviation Report

| Field | Value |
|---|---|
| Deliverable ID | D-0016 |
| Task | T02.05 |
| Related Requirements | FR-022, FR-023, RSK-007 |
| Date | 2026-03-09 |
| Status | COMPLETE |

## Severity Levels

### HIGH — Pipeline-Blocking Deviations

Deviations that indicate missing functionality, broken contracts, or security gaps. HIGH-severity deviations block pipeline progression in v2.20.

**Criteria**: Functional requirement missing, signature changed, constraint dropped, API contract broken, security control absent.

**Examples**:
1. A functional requirement specified in the spec (e.g., FR-019 "Cross-references must be validated") is entirely absent from the roadmap
2. An API endpoint's parameter types differ from the spec (e.g., `timeout: int` in spec, `timeout: str` in roadmap)
3. A security constraint is dropped (e.g., spec requires input sanitization, roadmap omits it)

**Boundary with MEDIUM**: If the requirement is _present but simplified_ (not missing), classify as MEDIUM. If the requirement is _entirely absent or semantically inverted_, classify as HIGH.

### MEDIUM — Non-Blocking Deviations (v2.20)

Deviations that indicate simplification, weakening, or renaming without complete loss. MEDIUM deviations are logged but do not block the pipeline in v2.20 (per OQ-005 / D-0007).

**Criteria**: Requirement simplified, parameter renamed, NFR softened, threshold relaxed, coverage reduced.

**Examples**:
1. A requirement is simplified: spec says "retry with exponential backoff and jitter", roadmap says "retry on failure"
2. A parameter is renamed without semantic loss: `spec_file` → `source_file`
3. An NFR threshold is relaxed: spec says "p95 < 100ms", roadmap says "p95 < 200ms"

**Boundary with HIGH**: If the simplification eliminates a _critical constraint_ (e.g., removing retry behavior entirely), classify as HIGH. If the simplification preserves intent but reduces precision, classify as MEDIUM.

**Boundary with LOW**: If the change is purely cosmetic (formatting, ordering) with zero semantic impact, classify as LOW. If the change alters meaning even slightly, classify as MEDIUM.

### LOW — Informational Deviations

Deviations that are cosmetic, organizational, or additive with no semantic impact. LOW deviations are recorded for completeness but have no effect on pipeline behavior.

**Criteria**: Formatting difference, section reordering, clarification added, whitespace change, editorial improvement.

**Examples**:
1. A section is moved from position 3 to position 5 in the document without changing content
2. A paragraph is rewritten for clarity but preserves the exact same meaning
3. Additional explanatory notes are added that do not contradict the spec

**Boundary with MEDIUM**: If the reordering or reformatting changes the _logical grouping_ of requirements (e.g., moving a security requirement out of the security section), classify as MEDIUM.

## Classification Rationale for Prompt Reuse (RSK-007)

When embedding severity classification in LLM prompts, include these disambiguation rules:

1. **Missing vs. Simplified**: A requirement that is _absent_ is HIGH; a requirement that is _present but weakened_ is MEDIUM
2. **Rename vs. Semantic Change**: A parameter _renamed_ without behavioral change is MEDIUM; a parameter whose _type or semantics change_ is HIGH
3. **Additive vs. Contradictory**: Content _added_ that does not contradict the spec is LOW; content that _contradicts_ the spec is HIGH
4. **Format vs. Structure**: Pure _formatting_ changes are LOW; _structural reorganization_ that changes logical grouping is MEDIUM
