# Group D: Quality Gates, Security & Edge Cases -- Adversarial Verdicts

**Adversarial Protocol**: Mode B (independent assessments)
**Agents**: QA (Agent 1), Security (Agent 2), Analyzer (Agent 3)
**Depth**: Standard (2 debate rounds)
**Convergence target**: 0.80
**Focus areas**: quality-assurance, security-adequacy, edge-case-likelihood

---

## Debate Process

### Round 1: Cross-Assessment Challenges

**P-016 divergence**: Agent 1 (MODIFY) vs Agents 2+3 (ACCEPT). Agent 1 argued the `--auto-relax-threshold` flag is over-engineering. Agent 2 countered that explicit opt-in flags are standard security practice for behavior changes. Agent 3 supported Agent 2, noting that 15-25% probability warrants a proper mechanism, not just documentation. Agent 1 conceded that the flag is lightweight and the immutability default is correct -- the MODIFY was about CLI cleanliness, not substance.

**P-019 divergence**: Agent 3 (REJECT) vs Agents 1+2 (MODIFY). Agent 3 argued <5% probability does not warrant any spec change beyond documentation. Agent 1 countered that even low-probability scenarios need defined behavior in a spec -- undefined behavior is a testing gap. Agent 2 noted the competing security concerns (evidence preservation vs data minimization) but agreed the `archive|delete` variant is disproportionate. Agent 3 softened to MODIFY with the minimal scope: "one-line addition specifying --clean requires successful completion."

**P-020 divergence**: Agent 3 (MODIFY -- pipeline-level not per-agent) vs Agents 1+2 (ACCEPT as-proposed). Agent 3 argued per-agent redaction adds prompt complexity and agents cannot reliably self-redact. Agent 2 agreed that post-generation pipeline-level redaction is more reliable than agent-level. Agent 1 agreed that the mechanism matters but the proposal's intent is correct. All three converged on: ACCEPT the proposal's scope (all artifacts), MODIFY the implementation approach (pipeline-level post-processing, not per-agent prompting).

### Round 2: Convergence Refinement

**P-016**: All three agents converged on ACCEPT with one modification: the `--auto-relax-threshold` flag is accepted as proposed, but the no-findings terminal report should include the original threshold value and the number of hypotheses that were filtered, so the user can make an informed decision about re-running with a lower threshold. Convergence: 0.93.

**P-017**: No disagreement across any round. All three agents recognized this as a documentation-implementation gap with high probability (60-80%) and minimal fix cost. Convergence: 0.97.

**P-018**: Agents 1 and 2 accepted fully. Agent 3 pushed for boundary definitions between the three states. After debate, all agreed: ACCEPT the three-state model, and add a requirement that the spec must define boundary conditions for each state transition. Convergence: 0.90.

**P-019**: After Round 1, Agent 3 moved from REJECT to MODIFY-minimal. All three converged on: the spec needs a one-sentence clarification that `--clean` is a no-op unless all phases completed successfully. The `archive|delete` variant is rejected as over-engineered. Convergence: 0.87.

**P-020**: All three converged on ACCEPT-with-implementation-modification. The scope (all artifacts) is correct. The mechanism should be pipeline-level post-processing with a default pattern set, not per-agent prompt modification. Configurable patterns deferred to future enhancement. Convergence: 0.90.

---

## Hybrid Scoring Breakdown

Scoring dimensions (each 0-10, weighted):
- **Quality Impact** (30%): Does this improve pipeline trustworthiness?
- **Security Adequacy** (25%): Is the security posture improved proportionally?
- **Edge Case Likelihood** (20%): How probable is the scenario in real usage?
- **Implementation Cost** (15%): How much spec/code change is required?
- **Proportionality** (10%): Is the solution sized appropriately to the problem?

### PROPOSAL-016: Deterministic handling when zero hypotheses survive

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 8.5 | Eliminates non-deterministic pipeline behavior |
| Security Adequacy | 8.0 | Prevents silent threshold relaxation on security hypotheses |
| Edge Case Likelihood | 7.5 | 15-25% probability, higher with strict thresholds |
| Implementation Cost | 7.0 | New CLI flag + terminal report path + filter logic changes |
| Proportionality | 8.5 | Well-sized: flag + report section covers the gap |
| **Weighted Total** | **8.03** | |

### PROPOSAL-017: Add baseline test artifact to normative phase contracts

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 9.5 | Baseline diffing is prerequisite for trustworthy validation |
| Security Adequacy | 7.5 | Forensic evidence value for incident response |
| Edge Case Likelihood | 9.0 | 60-80% of real runs encounter pre-existing failures |
| Implementation Cost | 9.0 | Purely additive: update contracts and artifact tree |
| Proportionality | 9.5 | Minimal cost, maximal quality improvement |
| **Weighted Total** | **8.88** | |

### PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 9.0 | Machine-readable exit status enables CI integration |
| Security Adequacy | 8.5 | CI security gates require formal exit semantics |
| Edge Case Likelihood | 10.0 | 100% of runs produce no formal exit status today |
| Implementation Cost | 7.0 | Report frontmatter + state mapping logic + boundary definitions |
| Proportionality | 8.0 | Three states are well-calibrated; boundaries need definition |
| **Weighted Total** | **8.70** | |

### PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 5.0 | Prevents rare edge case of orphaned artifacts |
| Security Adequacy | 5.0 | Minor data lifecycle concern, competing interests |
| Edge Case Likelihood | 3.5 | <5% harmful probability |
| Implementation Cost | 9.0 | One-sentence spec clarification (after scope reduction) |
| Proportionality | 7.0 | Reduced scope is well-sized to the actual risk |
| **Weighted Total** | **5.53** | |

### PROPOSAL-020: Redact sensitive data across all exported artifacts

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality Impact | 8.5 | Testable security posture across all outputs |
| Security Adequacy | 9.5 | Closes primary secret leakage vector |
| Edge Case Likelihood | 6.5 | 0.5-4% harmful exposure, concentrated on legacy repos |
| Implementation Cost | 6.5 | Pipeline-level post-processing + default pattern set |
| Proportionality | 8.0 | Scope correct, implementation refined to pipeline-level |
| **Weighted Total** | **8.15** | |

---

## Final Verdicts

### PROPOSAL-016: Deterministic handling when zero hypotheses survive
**Verdict: ACCEPT**
**Score: 8.03/10** | Convergence: 0.93

Accept as proposed with one addition: the no-findings terminal report must include the original threshold value and the count of hypotheses that were filtered out, enabling informed re-run decisions. The `--auto-relax-threshold` opt-in flag is accepted. Default behavior: threshold is immutable.

### PROPOSAL-017: Add baseline test artifact to normative phase contracts
**Verdict: ACCEPT**
**Score: 8.88/10** | Convergence: 0.97

Accept as proposed. Update the following spec sections:
- Section 7.5 (Phase 4 contract): add `baseline-test-results.md` as required output artifact
- Section 7.6 (Phase 5 contract): require Agent 5b to compute `introduced_failures` vs `preexisting_failures`
- Section 12.1 (artifact tree): add `phase-4/baseline-test-results.md`
- Section 16.2 (quality metrics): update test pass rate metric to reference baseline-diffed results

### PROPOSAL-018: Define pass/fail exit criteria for pipeline completion
**Verdict: ACCEPT**
**Score: 8.70/10** | Convergence: 0.90

Accept the three-state model (`success`, `success_with_risks`, `failed`) with one required addition: the spec must define explicit boundary conditions for each state transition. Specifically:
- `success`: All phases complete, 0 lint errors, 0 introduced test failures, self-review identifies no regressions
- `success_with_risks`: All phases complete, 0 lint errors, 0 introduced test failures, but self-review identifies residual risks or incomplete fixes
- `failed`: Any of: introduced test failures, lint errors in changed files, Phase 4 implementation errors, or pipeline-level errors
- `--dry-run` exits: `success` if Phases 0-3b complete without error, `failed` otherwise (no `success_with_risks` for dry runs since validation was not performed)

Add exit status to final report frontmatter as a machine-readable YAML block.

### PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle
**Verdict: MODIFY**
**Score: 5.53/10** | Convergence: 0.87

Reduce scope significantly. The `--clean=archive|delete` variant is rejected as over-engineered. Instead, add a single clarification to the `--clean` flag definition (FR-052):

> `--clean` SHALL only execute artifact removal after all phases have completed successfully (progress.json shows all phases in completed_phases). If the pipeline did not complete successfully, `--clean` is ignored and a warning is emitted: "Artifacts retained: pipeline did not complete successfully."

No new flag variants. No archive semantics. This addresses the actual risk (accidental evidence destruction on partial runs) with proportionate effort.

### PROPOSAL-020: Redact sensitive data across all exported artifacts
**Verdict: ACCEPT**
**Score: 8.15/10** | Convergence: 0.90

Accept the proposal's scope (all persisted artifacts, not just final report) with a refined implementation approach:

1. **Mechanism**: Pipeline-level post-processing, not per-agent prompt modification. After each phase writes its artifacts, a redaction pass scans all new files against the pattern set. This is more reliable than expecting agents to self-redact.
2. **Default patterns**: Ship with a fixed default pattern set covering: AWS keys (`AKIA...`), GCP service account keys, generic `password=`, `secret=`, `token=`, `api_key=` patterns, and PEM private key blocks.
3. **Configurable patterns**: Defer to a future `--redaction-config` flag. The default set covers 80%+ of real-world secrets.
4. **Secure raw retention**: Accept the `--no-redact` flag for security teams that need unredacted artifacts, with a mandatory warning: "WARNING: --no-redact retains sensitive data in intermediate artifacts. Ensure appropriate access controls."
5. **Update scope**: FR-049 is superseded. New requirement covers all artifacts including findings files, debate transcripts, fix proposals, and the final report.

---

## Verdict Summary

| # | Proposal | Verdict | Score | Convergence |
|---|----------|---------|-------|-------------|
| P-016 | Zero hypotheses handling | ACCEPT | 8.03 | 0.93 |
| P-017 | Baseline test artifact | ACCEPT | 8.88 | 0.97 |
| P-018 | Pass/fail exit criteria | ACCEPT | 8.70 | 0.90 |
| P-019 | --clean artifact lifecycle | MODIFY | 5.53 | 0.87 |
| P-020 | Full artifact redaction | ACCEPT | 8.15 | 0.90 |

**Overall convergence**: 0.91 (exceeds 0.80 target)

**Implementation priority** (by weighted score):
1. P-017 (8.88) -- Baseline test artifact contracts
2. P-018 (8.70) -- Exit criteria state model
3. P-020 (8.15) -- Artifact-wide redaction
4. P-016 (8.03) -- Zero hypothesis terminal path
5. P-019 (5.53) -- Clean flag guard clause

**Cross-proposal dependencies**:
- P-020 partially depends on P-017: baseline test results are also an artifact that needs redaction scanning
- P-018 depends on P-017: the `failed` state definition references "introduced test failures" which requires baseline diffing
- P-019 depends on P-018: `--clean` guard clause references "successful completion" which needs the formal exit state model
