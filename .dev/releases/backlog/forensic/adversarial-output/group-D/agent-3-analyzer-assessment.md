# Agent 3: Analyzer Perspective Assessment

**Focus**: Edge case severity and likelihood
**Core question**: How likely is this edge case in real usage? Is the proposed handling proportional to the probability?

---

## PROPOSAL-016: Deterministic handling when zero hypotheses survive

**Verdict**: ACCEPT

**Analysis**: The zero-survivors scenario is more likely than it appears at first glance. Consider these trigger conditions:

1. **High confidence threshold** (`--confidence-threshold 0.9`): Aggressive filtering makes zero survivors common, especially on well-maintained codebases.
2. **Small target scope**: Running forensic on a single well-tested file may yield hypotheses below threshold.
3. **False positive suppression**: The adversarial debate phase is designed to eliminate weak hypotheses. An effective debate can legitimately reject all candidates.

Estimated probability: **15-25%** of runs, higher with strict thresholds or small scopes.

The current behavior (silently lowering threshold by 0.1) is problematic not because it fails, but because it creates a hidden state transition. The pipeline's behavior changes based on whether the first filter pass succeeds, making debugging and reasoning about outcomes significantly harder.

The proposal's "strict no-findings terminal path" is proportionate. It requires:
- A dedicated report section (minimal template work)
- Threshold immutability by default (simplifies logic)
- An opt-in flag for relaxation (preserves flexibility)

This is not over-engineering. The terminal path codifies what the spec already implies but does not enforce.

**Probability**: High (15-25%)
**Severity without fix**: Moderate (non-deterministic behavior, debugging difficulty)
**Proportionality**: Well-calibrated

**Score**: 8.5/10

---

## PROPOSAL-017: Add baseline test artifact to normative phase contracts

**Verdict**: ACCEPT

**Analysis**: The "pre-existing test failures" edge case is extremely common in real-world codebases. Consider:

1. **Flaky tests**: Many projects have intermittently failing tests. Without a baseline, every flaky failure is attributed to pipeline changes.
2. **Known failures**: Projects with `@pytest.mark.skip` or `xfail` markers still show in test counts. Baseline diffing contextualizes them.
3. **Dependency-driven failures**: Tests that fail due to network issues, missing fixtures, or environment differences create noise.

Estimated probability of pre-existing failures: **60-80%** on real codebases.

The current spec added FR-050 (baseline test run) based on expert panel feedback, but the proposal correctly identifies that the normative phase contracts and artifact tree were not updated. This means:
- Phase 4 contract does not require `baseline-test-results.md` as an output artifact
- Phase 5b contract does not require computing `introduced_failures` vs `preexisting_failures`
- The artifact tree in Section 12.1 does not list the baseline file

This is a documentation-implementation gap that would cause confusion during skill development. The fix is purely additive -- updating contracts and artifact listings.

**Probability**: Very high (60-80% of real runs encounter pre-existing failures)
**Severity without fix**: High (every failure is ambiguous)
**Proportionality**: Minimal cost, high value

**Score**: 9.0/10

---

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

**Verdict**: ACCEPT

**Analysis**: The absence of exit criteria is not an "edge case" in the traditional sense -- it affects 100% of runs. Every pipeline execution produces a report without a formal verdict. This is a specification gap, not a rare condition.

However, from an edge-case perspective, the interesting question is: what happens at the boundaries of the proposed states?

- **success vs success_with_risks**: When the self-review identifies a minor concern (e.g., "fix could be more idiomatic"), is that a "risk"? The boundary needs crisp definition.
- **success_with_risks vs failed**: If lint reports 1 warning (not error) and all tests pass, what state applies?
- **Partial pipeline runs**: `--dry-run` skips Phases 4-5. What exit state applies when validation was never run?

The proposal should define these boundary conditions. Without them, the three-state model introduces new ambiguity at the state boundaries.

Estimated likelihood of boundary ambiguity: **30-40%** of runs will fall near a state boundary.

**Probability**: 100% (affects all runs)
**Severity without fix**: High (no machine-readable outcome)
**Proportionality**: Core infrastructure, not optional

**Score**: 8.5/10 (would be 9.5 with boundary definitions)

---

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

**Verdict**: REJECT

**Analysis**: Let me assess the actual probability and severity of the scenarios this proposal addresses:

1. **Interrupted cleanup**: User runs with `--clean`, pipeline completes, cleanup starts, machine crashes mid-deletion. Probability: **<1%**. Impact: orphaned partial artifacts, easily re-cleaned manually.

2. **User runs `--clean` then wants to resume**: This is contradictory by design. `--clean` is for terminal runs. If you want to resume, do not use `--clean`. Probability of user confusion: **5-10%** on first use, dropping to near-zero after.

3. **Forensic evidence loss**: User runs `--clean` and later needs the artifacts. Probability: **5-15%** depending on workflow. Impact: must re-run the pipeline (which is deterministic given the same inputs and checkpoint).

The proposal introduces `--clean=archive|delete` with guardrails. This is disproportionate to the risk:
- Two new flag variants for a flag that most users will never use
- Archive semantics (compression format, retention location, cleanup of archives) create new specification surface
- The "restrict to terminal successful runs" behavior is already implied by the spec

A one-line addition to the spec ("--clean requires all phases to have completed successfully; otherwise it is a no-op with a warning") solves the issue without new flag variants.

**Probability**: Low (<5% for any harmful scenario)
**Severity without fix**: Low (manual recovery is trivial)
**Proportionality**: Over-engineered relative to risk

**Score**: 4.5/10

---

## PROPOSAL-020: Redact sensitive data across all exported artifacts

**Verdict**: MODIFY

**Analysis**: The secret-in-intermediate-artifacts scenario is real, but let me assess the probability chain:

1. **Codebase contains hardcoded secrets**: Probability varies wildly. Well-maintained repos with pre-commit hooks: **5-10%**. Legacy codebases or prototype repos: **30-50%**.
2. **Hypothesis evidence quotes a secret-containing line**: Given secrets exist, Phase 1 agents excerpt relevant lines. If the secret is on a line relevant to a hypothesis, probability: **20-40%**.
3. **Artifacts are exposed**: The `.forensic-qa/` directory must be committed, shared, or accessed by unauthorized parties. With FR-051 (`.gitignore`): **10-20%**.

Combined probability of harmful secret exposure: roughly **0.5-4%** per pipeline run, concentrated on legacy codebases.

The proposal's "configurable redaction policy for all persisted artifacts" is the right direction but introduces non-trivial complexity:
- Every agent prompt must include redaction instructions
- Redaction patterns must be applied post-generation (agents cannot reliably self-redact)
- False positive redaction (e.g., variable named `API_KEY_LENGTH` gets redacted) degrades report quality
- Performance cost of scanning all artifacts with regex patterns

A proportionate approach:
1. Apply post-generation redaction to all artifacts (not agent-level, but pipeline-level)
2. Use a fixed default pattern set (AWS keys, GCP keys, generic `password=`, `secret=`, `token=` patterns)
3. Defer configurable patterns to a future enhancement
4. The "secure raw retention flag" is appropriate for security teams

**Probability**: Low-to-moderate (0.5-4% harmful exposure)
**Severity without fix**: High when it occurs (credential compromise)
**Proportionality**: Proposal is slightly over-scoped; pipeline-level post-processing is more practical than per-agent redaction

**Score**: 8.0/10 (right direction, implementation approach needs refinement)

---

## Summary Table

| Proposal | Verdict | Score | Key Rationale |
|----------|---------|-------|---------------|
| P-016 | ACCEPT | 8.5 | 15-25% probability, proportionate mitigation |
| P-017 | ACCEPT | 9.0 | 60-80% probability, minimal cost to fix |
| P-018 | ACCEPT | 8.5 | 100% of runs affected, needs boundary definitions |
| P-019 | REJECT | 4.5 | <5% harmful probability, over-engineered solution |
| P-020 | MODIFY | 8.0 | Right direction but pipeline-level redaction more practical |
