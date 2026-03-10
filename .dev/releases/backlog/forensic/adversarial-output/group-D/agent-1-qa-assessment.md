# Agent 1: QA Perspective Assessment

**Focus**: Testing completeness and quality gates
**Core question**: Does the pipeline produce trustworthy results without these changes? What failure modes are exposed?

---

## PROPOSAL-016: Deterministic handling when zero hypotheses survive

**Verdict**: MODIFY

**Analysis**: The current spec (Section 14.1) says "lower threshold by 0.1 and retry; if still zero, skip phases." This is a significant quality gate problem. Silently mutating the user's confidence threshold undermines reproducibility -- the same run with the same inputs can produce different outcomes depending on whether the first pass yields zero survivors. From a testing standpoint, this creates a non-deterministic pipeline path that is extremely difficult to test and validate.

The proposal to make the threshold immutable by default is correct. However, requiring a new `--auto-relax-threshold` flag adds CLI surface area for an edge case. A middle ground: keep the threshold immutable, but instead of a new flag, emit a structured warning in the report recommending the user re-run with a lower threshold. This preserves determinism while keeping the CLI clean.

**Failure modes exposed without this change**:
- Reproducibility failures: same codebase, different results depending on threshold relaxation
- Quality gate bypass: threshold lowering can promote low-confidence hypotheses
- Test verification impossibility: cannot write deterministic integration tests for zero-survivor path

**Score**: 8.5/10 (strong case, minor over-engineering on CLI flag)

---

## PROPOSAL-017: Add baseline test artifact to normative phase contracts

**Verdict**: ACCEPT

**Analysis**: This is a critical quality gap. The spec already added FR-050 (baseline test run before Phase 4) based on expert panel feedback, but the proposal correctly identifies that the phase contracts and artifact tree have not been updated to reflect this. Without baseline diffing formalized in the phase contract, Agent 5b has no normative obligation to compute `introduced_failures` vs `preexisting_failures`. The self-review (Agent 5c) similarly lacks a contractual baseline to verify against.

Without this change, every test failure in Phase 5 is ambiguous -- the report cannot distinguish regressions introduced by the pipeline from pre-existing failures. This directly undermines the trustworthiness of the validation phase.

**Failure modes exposed without this change**:
- False positive regressions: pre-existing failures blamed on pipeline fixes
- False negative regressions: introduced failures hidden in pre-existing noise
- Quality metric corruption: test pass rate is meaningless without baseline comparison
- Acceptance criteria unverifiable: "100% of new regression tests pass" cannot be validated

**Score**: 9.5/10 (clear gap, minimal implementation cost, high quality impact)

---

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

**Verdict**: ACCEPT

**Analysis**: This is a fundamental quality gate gap. The spec defines quality metrics (Section 16.2: "0 lint errors", "100% test pass for new tests") but has no formal mapping from these metrics to a pipeline exit status. The final report is narrative text -- there is no machine-readable success/failure signal. For CI integration or any automated workflow consuming forensic output, this is a blocking omission.

The proposed three-state model (`success`, `success_with_risks`, `failed`) is well-calibrated. A pipeline that produces fixes with passing tests should be `success`. One with self-review residual risks should be `success_with_risks`. One with introduced regressions or lint failures should be `failed`.

Without this change, downstream consumers must parse free-text reports to determine pipeline outcome -- unreliable and untestable.

**Failure modes exposed without this change**:
- CI integration impossible: no exit code or machine-readable status
- Quality gate bypass: no enforcement of the 0-lint and 100%-test targets
- User confusion: narrative report with mixed signals and no clear verdict
- Automated workflow breakage: cannot gate on pipeline success

**Score**: 9.0/10 (essential for production use, well-defined proposal)

---

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

**Verdict**: MODIFY

**Analysis**: The conflict between `--clean` (FR-052: removes output directory) and `--resume` (FR-043: depends on retained artifacts) is real but the severity is minor. The current spec states `--clean` removes the output directory "after the final report is printed to stdout." If the pipeline completed successfully, resume is irrelevant. The actual risk is: (a) interrupted cleanup leaves partial artifacts, and (b) user confusion about when artifacts are safe to delete.

The proposal to restrict `--clean` to terminal successful runs is already implied by the spec (it runs "after final report"). The `--clean=archive|delete` variant adds complexity for a minor edge case. A simpler approach: document that `--clean` requires successful completion, and if interrupted during cleanup, re-running with `--clean` will retry the cleanup. No new flag variants needed.

**Failure modes exposed without this change**:
- Partial cleanup leaves orphaned artifacts (low severity, easily recoverable)
- User accidentally cleans before checking results (mitigated by stdout output)
- No forensic evidence retention for audit (valid for enterprise, but niche)

**Score**: 6.0/10 (real but minor issue, proposal over-engineers the solution)

---

## PROPOSAL-020: Redact sensitive data across all exported artifacts

**Verdict**: ACCEPT

**Analysis**: The spec already added FR-049 (redact secrets in final report) based on expert panel review, but the proposal correctly identifies that intermediate artifacts (findings files, fix proposals, debate transcripts) are equally at risk. If a hypothesis quotes a line containing an API key as evidence, that key appears in `findings-domain-N.md`, `adversarial/debate-transcript.md`, the fix proposal, and only gets redacted in the final report.

From a quality gate perspective, artifact-level redaction is the only way to make the security posture testable. You cannot write a quality gate that says "no secrets in output" if you only redact the last mile.

**Failure modes exposed without this change**:
- Secret leakage through intermediate artifacts (high severity)
- Compliance failure: artifacts committed to git expose secrets
- Quality gate incomplete: cannot verify "no secrets in output" across all artifacts
- Inconsistent redaction: same secret redacted in report but visible in findings

**Score**: 9.0/10 (clear security-quality intersection, well-scoped proposal)

---

## Summary Table

| Proposal | Verdict | Score | Key Rationale |
|----------|---------|-------|---------------|
| P-016 | MODIFY | 8.5 | Threshold immutability correct; CLI flag approach over-engineered |
| P-017 | ACCEPT | 9.5 | Critical quality gap; baseline diffing is contractually required |
| P-018 | ACCEPT | 9.0 | Machine-readable exit status essential for CI and quality gates |
| P-019 | MODIFY | 6.0 | Real issue but low severity; simpler documentation fix sufficient |
| P-020 | ACCEPT | 9.0 | Intermediate artifact redaction required for testable security posture |
