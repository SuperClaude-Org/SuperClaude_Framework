# Diff Analysis: Proposal Assessments Comparison

## Metadata
- Generated: 2026-02-28
- Variants compared: 3 (architect, quality-engineer, analyzer)
- Total proposals assessed: 22
- Verdict agreements: 10 unanimous ACCEPT
- Verdict disagreements: 12 (verdict or modification differences)

## Verdict Agreement Matrix

| Proposal | Architect | Quality-Engineer | Analyzer | Agreement |
|----------|-----------|-----------------|----------|-----------|
| P-001 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-002 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-003 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-004 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-005 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-006 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-007 | MODIFY | ACCEPT | MODIFY | 2/3 MODIFY |
| P-008 | MODIFY | ACCEPT | MODIFY | 2/3 MODIFY |
| P-009 | MODIFY | ACCEPT | MODIFY | 2/3 MODIFY |
| P-010 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-011 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-012 | ACCEPT | MODIFY | ACCEPT | 2/3 ACCEPT |
| P-013 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-014 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-015 | ACCEPT | MODIFY | ACCEPT | 2/3 ACCEPT |
| P-016 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-017 | ACCEPT | ACCEPT | MODIFY | 2/3 ACCEPT |
| P-018 | ACCEPT | ACCEPT | ACCEPT | Unanimous |
| P-019 | MODIFY | ACCEPT | MODIFY | 2/3 MODIFY |
| P-020 | MODIFY | ACCEPT | MODIFY | 2/3 MODIFY |
| P-021 | ACCEPT | ACCEPT | MODIFY | 2/3 ACCEPT |
| P-022 | REJECT | MODIFY | REJECT | 2/3 REJECT |

## Structural Differences

### S-001: Risk tolerance gradient
- **Severity**: Medium
- Architect and Analyzer favor pragmatic simplification (reduce scope for v1)
- Quality-Engineer consistently favors comprehensive coverage (no weakened gates)
- Pattern: QE accepts proposals as-is more often; Architect/Analyzer modify to reduce scope

### S-002: Schema completeness vs. implementation burden
- **Severity**: Medium
- Quality-Engineer treats every optional field as a quality gap
- Architect treats optional fields as implementation burden for marginal benefit
- Analyzer treats optional fields based on practical frequency of the use case

## Content Differences

### C-001: Token ceiling approach (P-012)
- Quality-Engineer wants three levels (soft target, hard ceiling, overflow action) to preserve testability
- Architect/Analyzer want soft target + overflow policy, accepting that hard ceilings are not enforceable
- Core tension: testability of constraints vs. feasibility of enforcement

### C-002: progress.json field requirements (P-008)
- Quality-Engineer wants all fields mandatory for reproducibility
- Architect/Analyzer want tiered requirements (essential = required, nice-to-have = optional)
- Core tension: resume safety guarantee vs. implementation simplicity

### C-003: Domain ID stability mechanism (P-009)
- Architect proposes deterministic slugs (e.g., `dom-subprocess-lifecycle`)
- Quality-Engineer accepts any stable ID mechanism (UUID, hash, or slug)
- Analyzer proposes minimal fix: just read IDs from existing artifacts on resume
- Core tension: full stability vs. "good enough" for the common case

### C-004: Baseline test requirement level (P-017)
- Architect/Quality-Engineer: MUST requirement
- Analyzer: SHOULD requirement with timeout escape hatch
- Core tension: quality completeness vs. pipeline runtime impact

### C-005: Redaction scope (P-020)
- Quality-Engineer: full configurable redaction policy
- Architect: single flag with basic pattern matching
- Analyzer: agent prompt requirement + simple flag
- Core tension: enterprise security needs vs. v1 scope

### C-006: Clean behavior (P-019)
- Quality-Engineer: `--clean=archive|delete` sub-options
- Architect: restrict to terminal success only
- Analyzer: document success-only behavior, no sub-options
- Core tension: CLI completeness vs. simplicity

### C-007: Multi-root provenance granularity (P-021)
- Architect/Quality-Engineer: `target_root` on path-bearing records
- Analyzer: `target_root` at domain level only
- Core tension: correctness of path resolution vs. schema weight

### C-008: MCP scheduler (P-022)
- Quality-Engineer: define observable behavior contract (testable)
- Architect/Analyzer: reject/defer to framework-level handling
- Core tension: spec self-containment vs. framework delegation

## Contradictions

### X-001: P-007 risk score calculation
- Quality-Engineer says calculation method MUST be defined for determinism
- Architect says calculation method should NOT be specified to avoid over-specification
- **Impact**: High -- affects model-tier assignment determinism

### X-002: P-008 git_head requirement level
- Quality-Engineer says mandatory for reproducibility
- Architect says creates unwanted git dependency
- Analyzer says over-engineering for v1
- **Impact**: Medium -- affects resume validation strictness

### X-003: P-017 baseline test requirement level
- Quality-Engineer says MUST for quality completeness
- Analyzer says SHOULD with timeout to avoid blocking pipeline
- **Impact**: Medium -- affects validation phase completeness guarantee

## Unique Contributions

### U-001: Architect -- P-009 slug-based domain IDs
- Proposes human-readable deterministic slugs rather than UUIDs/hashes
- **Value**: High -- combines readability with stability

### U-002: Quality-Engineer -- P-006 schema_version field
- Suggests adding schema_version to new-tests-manifest for forward compatibility
- **Value**: Medium -- good practice but not blocking for v1

### U-003: Quality-Engineer -- P-012 three-level token budget
- Proposes soft target + hard ceiling + overflow action (three distinct levels)
- **Value**: Medium -- preserves testability better than two-level approach

### U-004: Analyzer -- P-017 baseline timeout threshold
- Proposes configurable timeout for baseline test runs to prevent pipeline blocking
- **Value**: Medium -- practical concern for large test suites

### U-005: Analyzer -- P-021 domain-level root instead of record-level
- Proposes simpler provenance model at domain granularity
- **Value**: High -- significantly reduces schema complexity for common case
