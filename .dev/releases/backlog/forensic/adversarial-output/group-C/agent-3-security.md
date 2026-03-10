# Agent 3 Assessment: Security Perspective

**Focus**: Resume safety and data integrity
**Core Question**: "Could the inconsistency cause data corruption, stale artifact consumption, or non-deterministic behavior during resume?"

---

## PROPOSAL-001: Move panel additions into normative sections

**Verdict**: ACCEPT

**Analysis**: From a resume safety perspective, the most dangerous panel additions are:
- **FR-053** (stale codebase detection on resume): If this is not normative, implementations may skip the `git rev-parse HEAD` check, allowing stale findings to be consumed after the codebase changed between sessions. This is a data integrity risk -- the pipeline would produce a final report that references hypotheses about code that no longer exists.
- **FR-054** (pre-flight validation): Without this, a resumed pipeline may fail mid-phase because the output directory is no longer writable or target paths were moved. Partial writes could corrupt artifacts.
- **FR-049** (secret redaction): If not normative, the final report could leak credentials extracted during hypothesis evidence gathering. This is a direct security risk.

These are not optional enhancements. They are integrity and security controls. Leaving them in commentary status means implementations can legally omit them.

**Data Integrity Impact**: HIGH. FR-053 directly prevents stale data consumption during resume.

---

## PROPOSAL-002: Resolve `--depth` semantic conflict

**Verdict**: ACCEPT

**Analysis**: The `--depth` conflict creates non-deterministic behavior: the same command input can produce different debate depths depending on which section the implementer follows. During resume, this becomes dangerous:

1. Session 1 runs Phases 0-2 with Phase 2 using `deep` (per Section 7.2 hardcode).
2. Session is interrupted.
3. Session 2 resumes. The resume logic restores `--depth standard` from `progress.json.flags`.
4. Phase 3b runs with `standard` (per the restored flag).
5. But if the circuit breaker fires, it forces `quick`.

Without a defined precedence, the resume logic cannot determine what depth was *actually* used in Phase 2 vs what was *stored* in flags. The proposal's precedence order resolves this by making the behavior deterministic and flag-recoverable.

**Data Integrity Impact**: MEDIUM. Does not corrupt artifacts, but produces inconsistent analytical depth across phases in a non-reproducible way.

---

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs

**Verdict**: ACCEPT

**Analysis**: This is the highest-severity resume safety issue in the group. Consider the resume scenario:

1. Phase 2 completes. Implementation A writes to `phase-2/adversarial/base-selection.md`.
2. Session is interrupted.
3. Resume logic (Section 12.3) verifies "all expected artifacts for completed phases exist."
4. The verification logic follows FR-033 and looks for `adversarial/base-selection.md` (root-relative).
5. File not found. Phase 2 is demoted to incomplete. Phase 2 re-executes from scratch.

This is a **data loss scenario**: a correctly completed phase is re-executed because the resume validator looks in the wrong directory. Worse, if the adversarial protocol has internal state that is not idempotent, re-execution could produce different results.

The reverse is equally dangerous: if the resume validator looks at the right path but Phase 6 reads from the wrong path, the final report references a nonexistent artifact and either fails or silently uses stale data.

**Data Integrity Impact**: CRITICAL. Causes unnecessary phase re-execution or stale/missing artifact reads during resume.

---

## PROPOSAL-005: Correct Phase 3b output location contract

**Verdict**: ACCEPT

**Analysis**: Similar to Proposal-004 but for a different artifact. The resume scenario:

1. Phase 3b completes, writes `fix-selection.md` to an ambiguous location.
2. Session is interrupted.
3. Resume validator checks: is `fix-selection.md` present? Depending on where it looks, it may or may not find it.
4. Phase 4 starts, reads `fix-selection.md` from yet another assumed location.

The data integrity risk here is that Phase 4 could read a stale or incomplete `fix-selection.md` from a fallback location while a correct version exists elsewhere. The proposal to define a canonical path is necessary.

Regarding the `phase-3b/` vs `phase-3/` debate: from a security and integrity perspective, I prefer `phase-3b/` because it enforces phase ownership boundaries. If Phase 3 and Phase 3b share a directory, the resume validator cannot distinguish which artifacts belong to which phase when doing completeness checks. A Phase 3 restart (re-run missing fix proposals) should not touch `fix-selection.md`, but if both share `phase-3/`, the validator might accidentally include it in Phase 3's artifact set.

The migration fallback is unnecessary for a draft spec and I am neutral on it. But the separate directory is a net positive for integrity.

**Data Integrity Impact**: HIGH. Ambiguous artifact location causes incorrect resume behavior and potential stale data consumption.

---

## PROPOSAL-003: Normalize dry-run behavior and final report semantics

**Verdict**: ACCEPT

**Analysis**: The dry-run inconsistency creates a checkpoint integrity problem:

1. User runs `--dry-run`. Phases 0-3b execute.
2. Current spec is ambiguous on Phase 6. If it does not execute, `progress.json` shows `completed_phases: [0, 1, 2, 3, "3b"]` and `current_phase: "3b"`.
3. User later runs `--resume` on this checkpoint (without `--dry-run`).
4. Resume logic computes next phase: `max(completed_phases) + 1` = Phase 4.
5. Phase 4 proceeds. This is correct behavior.

But if Phase 6 DID execute in dry-run:
1. `completed_phases: [0, 1, 2, 3, "3b", 6]` with phases 4 and 5 missing.
2. Resume from this checkpoint: `max(completed_phases) + 1` = 7, which does not exist.
3. The pipeline considers itself "complete" even though phases 4-5 never ran.
4. A subsequent `--resume` without `--dry-run` would incorrectly believe the pipeline is finished.

The proposal's `skipped_by_mode` status and explicit phase plan prevent this by making the checkpoint schema unambiguous about why phases were skipped, enabling resume logic to distinguish "skipped intentionally" from "not yet executed."

**Data Integrity Impact**: HIGH. Incorrect resume after dry-run could either skip critical phases or incorrectly mark the pipeline as complete.

---

## Summary Scores

| Proposal | Integrity Score (0-10) | Resume Risk | Verdict |
|----------|----------------------|-------------|---------|
| P-001 | 8 | HIGH | ACCEPT |
| P-002 | 7 | MEDIUM | ACCEPT |
| P-004 | 10 | CRITICAL | ACCEPT |
| P-005 | 9 | HIGH | ACCEPT |
| P-003 | 9 | HIGH | ACCEPT |
