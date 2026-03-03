# Agent 2: Security Perspective Assessment

**Focus**: Data safety and attack surface
**Core question**: Does skipping this change create a security risk? Is the proposed mitigation sufficient or overkill?

---

## PROPOSAL-016: Deterministic handling when zero hypotheses survive

**Verdict**: ACCEPT

**Analysis**: From a security standpoint, threshold mutation is a subtle integrity issue. If the pipeline silently lowers the confidence threshold, it may promote hypotheses that would otherwise be filtered -- including hypotheses about security-sensitive code paths with insufficient evidence. A security-critical hypothesis promoted at 0.6 confidence (after relaxation from 0.7) could lead to risky fix proposals being greenlit.

The immutability of user-specified thresholds is a security principle: the user's intent should not be silently overridden. The `--auto-relax-threshold` opt-in flag is appropriate because it makes the relaxation explicit and auditable.

The "no-findings terminal path" with a dedicated report section is also security-positive: it creates an audit trail showing that the pipeline investigated but found nothing actionable, rather than silently skipping phases with no record.

**Security risk if skipped**: Low-to-moderate. Threshold relaxation could promote insufficiently evidenced security hypotheses, leading to incorrect or incomplete fixes applied to security-sensitive code.

**Is the mitigation overkill?**: No. Adding a CLI flag is minimal surface area. The immutability default is the correct security posture.

**Score**: 8.0/10 (sound security reasoning, proportionate mitigation)

---

## PROPOSAL-017: Add baseline test artifact to normative phase contracts

**Verdict**: ACCEPT

**Analysis**: This is primarily a quality concern, but it has a security dimension. Without baseline diffing, a security fix that introduces a test regression cannot be distinguished from a pre-existing failure. If the pipeline reports "3 test failures" without baseline context, the user may dismiss them as pre-existing and merge security-sensitive changes that actually broke something.

More critically, the baseline test artifact becomes forensic evidence. If a security incident occurs after pipeline-recommended fixes are applied, the baseline provides a verifiable pre-state for incident response.

**Security risk if skipped**: Low. The risk is indirect -- misattributed test failures could mask security regressions.

**Is the mitigation overkill?**: No. Running a test suite baseline is cheap and the forensic evidence value is high.

**Score**: 7.5/10 (secondary security concern, but good hygiene)

---

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

**Verdict**: ACCEPT

**Analysis**: Machine-readable exit status is a security control for CI pipelines. Without it, a CI gate cannot enforce that forensic pipeline output is clean before merging. If the pipeline reports lint failures and test regressions in free text but exits with a neutral status, automated gates will pass security-degrading changes.

The three-state model is appropriate. `failed` should be the exit state whenever:
- Security-relevant hypotheses were greenlit but implementation introduced regressions
- Lint failures exist in security-sensitive files (auth, crypto, access control)
- Self-review identifies incomplete security fixes

One enhancement worth considering: the `success_with_risks` state should distinguish security risks from general risks, so CI gates can treat them differently.

**Security risk if skipped**: Moderate. CI pipelines cannot gate on forensic results, potentially allowing security-degrading changes to merge unchecked.

**Is the mitigation overkill?**: No. Exit status is basic pipeline hygiene expected by any CI system.

**Score**: 8.5/10 (clear security-CI integration gap)

---

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

**Verdict**: MODIFY

**Analysis**: The security angle here is about forensic evidence preservation and data lifecycle. Intermediate artifacts may contain sensitive code excerpts, hypothesis evidence with secrets (even if redacted in the final report per FR-049), and detailed analysis of security vulnerabilities.

Two competing security concerns:
1. **Evidence preservation**: `--clean` destroying artifacts eliminates the audit trail of what was investigated, which security/compliance teams may need.
2. **Data minimization**: Retaining artifacts containing security-sensitive analysis increases the exposure window for that data.

The `--clean=archive|delete` approach addresses both: `archive` compresses artifacts for secure retention, `delete` removes them. However, the proposal should specify that archived artifacts inherit the same redaction policy as the final report. If P-020 is accepted, this becomes less critical since all artifacts would already be redacted.

A simpler approach: if `--clean` is specified, validate that the run completed successfully (check `progress.json` for all phases completed) before deleting. This prevents accidental destruction of incomplete run artifacts that might contain clues about pipeline failures.

**Security risk if skipped**: Low. The primary risk is accidental evidence destruction, not data exfiltration.

**Is the mitigation overkill?**: The `archive|delete` variants are slightly over-engineered. A simple completion guard is sufficient.

**Score**: 5.5/10 (low security severity, competing concerns cancel out)

---

## PROPOSAL-020: Redact sensitive data across all exported artifacts

**Verdict**: ACCEPT

**Analysis**: This is the highest-priority security proposal in Group D. The current spec (FR-049) only redacts the final report. Intermediate artifacts are the primary attack surface for secret leakage:

1. **Findings files** (`findings-domain-N.md`): Hypothesis evidence quotes source lines. If a line contains `API_KEY="sk-abc123"`, the evidence field includes it verbatim.
2. **Debate transcripts** (`debate-transcript.md`): Agents discuss evidence including code excerpts. Secrets propagate through multiple debate rounds.
3. **Fix proposals** (`fix-proposal-H-N.md`): "Changes list" shows before/after code. If the original code contains a secret, the "before" state leaks it.
4. **Changes manifest** (`changes-manifest.json`): File paths may reveal sensitive infrastructure topology.

The exposure vector is significant: `.forensic-qa/` artifacts may be committed to git (even with FR-051's `.gitignore` addition, not all repos enforce `.gitignore`), shared in code reviews, or retained on developer machines.

The proposal's "configurable redaction policy" is the correct approach. Different organizations have different secret patterns (AWS keys, GCP service accounts, custom tokens). A default pattern set with extensibility covers the common case.

The "optional secure raw retention flag" is also appropriate for security teams that need unredacted artifacts for incident response -- but it should require explicit opt-in with a warning.

**Security risk if skipped**: HIGH. Secret leakage through intermediate artifacts is a concrete, exploitable risk with real-world impact.

**Is the mitigation overkill?**: No. This is the minimum viable security posture for a tool that systematically excerpts source code.

**Score**: 9.5/10 (critical security gap, well-designed mitigation)

---

## Summary Table

| Proposal | Verdict | Score | Key Rationale |
|----------|---------|-------|---------------|
| P-016 | ACCEPT | 8.0 | Threshold immutability prevents silent security posture changes |
| P-017 | ACCEPT | 7.5 | Baseline provides forensic evidence for security incident response |
| P-018 | ACCEPT | 8.5 | Machine-readable exit status required for CI security gates |
| P-019 | MODIFY | 5.5 | Low security severity; completion guard sufficient |
| P-020 | ACCEPT | 9.5 | Critical: intermediate artifacts are primary secret leakage vector |
