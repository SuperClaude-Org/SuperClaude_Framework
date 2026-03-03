# Group D: Quality Gates, Security & Edge Cases (5 proposals)

These proposals address testing gaps, security concerns, edge case handling, and pipeline exit semantics.

## PROPOSAL-016: Define deterministic handling when zero hypotheses survive

**Category**: edge-case | **Severity**: major
**Affected sections**: [14.1, 7.2, 7.3, 7.7, 13]
**Current state**: Error table says lower threshold by 0.1 and retry; if still zero, skip phases. This mutates user intent and can create inconsistent outcomes.
**Proposed change**: Keep user threshold immutable unless `--auto-relax-threshold` is explicitly enabled; define a strict no-findings terminal path with dedicated report section.
**Rationale**: Predictable behavior is required for reproducibility and trust in quality gates.
**Impact**: Filtering logic, CLI flags, final report template.

## PROPOSAL-017: Add baseline test artifact to normative phase contracts

**Category**: testing | **Severity**: major
**Affected sections**: [3.1 FR-031/032, 7.5, 12.1, 17]
**Current state**: Panel text introduces baseline test run, but Phase 4/5 contracts and artifact tree do not include it.
**Proposed change**: Add `phase-4/baseline-test-results.md` as required artifact; require Phase 5b to compute `introduced_failures` vs `preexisting_failures`.
**Rationale**: Without baseline diffing, "regression introduced by fix" is not testable.
**Impact**: Validation logic, reporting metrics, acceptance criteria.

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

**Category**: requirements | **Severity**: major
**Affected sections**: [14.1, 16.2, 7.6, 7.7]
**Current state**: Lint/test failures do not block pipeline, but quality metrics target 0 lint errors and 100% test pass for new tests; no final exit status model is defined.
**Proposed change**: Introduce explicit run outcome states (`success`, `success_with_risks`, `failed`) and map lint/test/self-review signals to each state.
**Rationale**: Consumers need machine-readable success semantics, not only narrative report text.
**Impact**: Final report frontmatter, CI integration, user expectations.

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

**Category**: consistency | **Severity**: minor
**Affected sections**: [5.3, Appendix A, 12, 17]
**Current state**: `--clean` removes output directory after final report, but resumability depends on retained artifacts; behavior is undefined for partial failures or interrupted cleanup.
**Proposed change**: Restrict `--clean` to terminal successful runs, or implement archive-before-clean (`--clean=archive|delete`) with guardrails.
**Rationale**: Prevents accidental loss of forensic evidence and resume checkpoints.
**Impact**: CLI UX, post-run operations, recovery options.

## PROPOSAL-020: Redact sensitive data across all exported artifacts, not just final report

**Category**: security | **Severity**: major
**Affected sections**: [7.1, 9.5, 13, 14, 17]
**Current state**: Secret redaction is proposed only for final report excerpts; raw findings/fix artifacts may still contain sensitive strings.
**Proposed change**: Add configurable redaction policy for all persisted artifacts (`findings`, `fix proposals`, transcripts), with optional secure raw retention flag.
**Rationale**: Most leakage risk comes from intermediate artifacts, not just report output.
**Impact**: Agent prompt requirements, schema notes, security posture.
