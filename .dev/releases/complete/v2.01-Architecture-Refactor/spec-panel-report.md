# v2.01 Sprint Spec — Expert Panel Review Report

**Spec reviewed**: `sprint-spec.md`
**Date**: 2026-02-24
**Panel**: Karl Wiegers · Gojko Adzic · Martin Fowler · Michael Nygard · Lisa Crispin
**Method**: 5 parallel independent reviews, consolidated and deduplicated

---

## Panel Scores

| Expert | Domain | Score | Headline |
|--------|--------|-------|---------|
| Karl Wiegers | Requirements | 5.5/10 | Strong problem definition; systematic failure in completion criteria |
| Martin Fowler | Architecture | 5.0/10 | Sound tier model; fallback-first inversion is a design smell |
| Gojko Adzic | Testability | 3.0/10 | Near-total absence of executable behavioral specifications |
| Michael Nygard | Production | 3.0/10 | 6 unhandled failure modes; silent failure paths unacceptable |
| Lisa Crispin | Testing | 3.0/10 | Phase exit criteria missing for 3/6 phases; test plan unimplementable |

**Panel Average: 3.9/10**

The spec earns its high marks on problem diagnosis, decision traceability, and architectural direction. It loses them on completion criteria, behavioral verifiability, and failure mode coverage — all of which are sprint-execution concerns, not design concerns.

---

## Cross-Expert Consensus Findings

Issues flagged independently by 3 or more experts. These are the highest-confidence findings.

### CC-1: Missing Exit Criteria — Phases 4, 5, and 6 (4 experts)
**Flagged by**: Wiegers (CRITICAL), Crispin (CRITICAL), Nygard (implicitly), Adzic (implicitly)

Phases 1, 2, and 3 have exit criteria. Phases 4, 5, and 6 do not. Phase 4 is the validation phase (STRICT compliance on all 3 tasks). Phase 6 contains T06.03 — the single highest-risk content change (461-line extraction). There is no definition of "done" for the sprint.

**Action required**: Add measurable exit criteria to Phases 4, 5, and 6 before sprint start.

Suggested Phase 4: "T04.01–T04.03 complete; return-contract.yaml validates against 10-field schema; 3 priority tests from CC-7 passing."
Suggested Phase 6: "`make lint-architecture` exits 0; `make verify-sync` exits 0; `task-unified.md` ≤106 lines verified; BUG-002–006 all resolved with evidence."

---

### CC-2: Runtime Scope Control — Unmitigated, Root Cause of Rollback (4 experts)
**Flagged by**: Wiegers (CRITICAL), Fowler (CRITICAL risk), Nygard (CRITICAL), Crispin (CRITICAL)

The spec explicitly states: "The rollback incident's primary symptom — an agent changing 68 files when 4 were planned — cannot be prevented by the current architecture." The 3-tier model addresses instruction quality but not execution boundaries. This sprint asks implementers to re-execute in the same environment, with the same unconstrained agent, with no new protective mechanism.

This is not an architectural gap — it is an active sprint risk. The sprint itself can suffer the same rollback.

**Action required**: One of the following before sprint execution begins:
- (a) Define a mandatory pre-execution plan approval gate: "Before any Phase 2+ task, the agent MUST present the list of files to be changed and receive explicit user confirmation."
- (b) Add a scope sentinel to every phase task: "This task modifies exactly [N] files: [file list]. Any deviation requires stopping and re-planning."
- (c) Document the accepted risk explicitly: "Sprint owner acknowledges this sprint may require rollback. Risk accepted. No compensating control."

Option (c) is valid; the sprint should not lie about its risk posture.

---

### CC-3: T01.01 Probe — Sprint Variant Could Be Solving the Wrong Problem (3 experts)
**Flagged by**: Wiegers (CRITICAL), Nygard (CRITICAL), Adzic (implicitly)

Decision D-0001 (`TOOL_NOT_AVAILABLE`) forces the FALLBACK-ONLY variant. Every design decision in §8, §9, §13, and the entire fallback protocol (3a–3f) depends on this being true in the current environment. The spec correctly says "re-verify T01.01" — but it classifies T01.01 as EXEMPT compliance with no probe specification, no observable pass criteria, and no decision tree for what happens if the result changes.

If the tool IS now available, this sprint builds an elaborate workaround for a constraint that no longer exists.

**Action required**: Elevate T01.01 to STANDARD. Specify: exact probe command, expected output for AVAILABLE vs NOT_AVAILABLE, and the branch: if AVAILABLE → stop, escalate to design revision; if NOT_AVAILABLE → proceed FALLBACK-ONLY. Probe fixtures (`spec-minimal.md`, `variant-a.md`) must exist before T01.01 can be executed; they are referenced in §16 as not yet created.

---

### CC-4: CI Checks 5 and 7 — "NEEDS DESIGN" Voids Core Enforcement (4 experts)
**Flagged by**: Wiegers (MAJOR), Fowler, Nygard, Adzic

Check 5 detects inline protocol YAML blocks in command files (the original bloat failure mode). Check 7 validates that `## Activation` references the correct skill (BUG-006 is exactly this failure). Both are listed as `NEEDS DESIGN` and both are ERROR-level in the policy. Without them, a developer can:
- Add 200 lines of inline protocol to a command (CI passes)
- Wire `## Activation` to the wrong skill name (CI passes)

These are the two most important guards in the architecture. Their absence makes `make lint-architecture` a false safety signal.

**Action required**: Either (a) implement Checks 5 and 7 before Phase 3 closes, or (b) explicitly reclassify Phase 3 exit criteria as "partial enforcement only — Checks 5 and 7 deferred with documented risk." Do not present a 6/10 CI implementation as equivalent to a 10/10 implementation.

---

### CC-5: Silent Failure — Missing-File Guard Routes Pipeline Failure as Skip (3 experts)
**Flagged by**: Nygard (FM-01/SF-01), Adzic (silent failure risk), Crispin (implicitly)

Step 3e specifies: "If no contract → skip (return empty result)." This means a complete failure of the adversarial pipeline — Task agent never ran, crashed, timed out — is indistinguishable from a deliberate skip. The parent workflow continues without adversarial validation, producing a roadmap artifact without the quality gate that v2.01 is designed to enforce. No error, no warning, no audit trail.

This is not a "guard" — it is a bypass masquerading as a guard.

**Action required**: Reclassify the missing-file case as FAIL (abort + escalate), not SKIP. If a skip is truly the desired behavior, document the rationale explicitly and add a warning log entry. At minimum, distinguish: "adversarial pipeline was elided by design" from "adversarial pipeline failed silently."

---

### CC-6: Return Contract — Missing Failure Invariants and Mixed Concerns (3 experts)
**Flagged by**: Fowler (interface contract issues), Nygard (FM-01, FM-02, FM-03), Adzic (missing behavioral spec)

Three related issues:
1. **No field invariants under failure**: When `status = "failed"`, is `merged_output_path` guaranteed null? When `convergence_score` is the 0.5 sentinel, is `fallback_mode` guaranteed true? The schema gives types but no field contracts under non-success conditions.
2. **Mixed concerns**: `invocation_method` and `fallback_mode` are observability fields; the others are result fields. Fowler flags ISP violation. Nygard flags that absent fields carry semantic meaning (dangerous for serializers that write defaults).
3. **0.5 sentinel conflates three failure modes**: Partial write, YAML parse error, and unmeasurable convergence all produce 0.5. These have different recovery actions; collapsing them prevents differential operator response.

**Action required**: Add a "Field Invariants Under Non-Success" section to §10. Define which fields are mandatory vs optional for each `status` value. Consider splitting observability fields into a separate `invocation_metadata` sub-object. Give parse errors and partial writes a distinct sentinel (e.g., null or -1) rather than 0.5.

---

### CC-7: No Behavioral Test for the Core Claim (3 experts)
**Flagged by**: Adzic (testability score driver), Crispin (critical gap), Nygard (OG-04)

The central behavioral claim of v2.01: "agents now reliably follow `/sc:command` behavioral specifications." There is no executable test that:
- Demonstrates the old failure mode (agent ignores skill, proceeds from command file alone)
- Demonstrates the new behavior (agent invokes Skill tool, loads SKILL.md, executes protocol)
- Shows they differ

CI Check 6 validates text presence (does `## Activation` exist?). It does not validate behavioral consequence (does the agent actually invoke the skill?).

**Action required** (top 3 tests per Crispin priority ranking):
1. **Scope boundary sentinel** (before sprint execution): Agent presents file change manifest, user approves before any Phase 2+ work. Prevents rollback recurrence.
2. **Return contract routing test**: Pytest fixtures for all three routing branches (PASS ≥0.6, PARTIAL 0.5–0.6, FAIL <0.5) plus YAML parse error and missing file. Fully implementable from §10 today.
3. **Stale reference regression**: 10-line pytest asserting zero occurrences of old skill paths (`sc-adversarial/`, `sc-cleanup-audit/`, `sc-roadmap/`, `sc-task-unified/`, `sc-validate-tests/`) across all .md files. Prevents BUG-002/005 class recurrence permanently.

---

## Single-Expert Critical Findings

Findings from one expert that are independently important.

### SE-1: Behavioral Summary in Command File Recreates v2.0 Failure Mode (Fowler)
**Section**: §5 Command Template, `## Behavioral Summary`

The Command template mandates a `## Behavioral Summary` (≤5 sentences) inside the command file. This is a condensed description of the skill's behavior — exactly the kind of summary that §2 identifies as the mechanism that caused "agents guessing protocol steps when summaries drifted from the actual skill spec." A pure Tier 0 door should carry only the skill's address (`## Activation`), not a summary of what the skill does. When the skill drifts, the summary silently contradicts it.

**Action required**: Remove `## Behavioral Summary` from the mandatory section list, or reclassify it as purely human-facing context that agents are explicitly instructed to ignore in favor of the skill.

---

### SE-2: Step 3f No-Op Instruction Is Reserved Code in a Behavioral Spec (Fowler)
**Section**: §9, Step 3f

Step 3f is: "Skip primary template (no-op in FALLBACK-ONLY variant). This step remains for future when claude -p becomes available." This is commented-out code promoted to specification status. Agents executing this spec must parse "this step is intentionally empty" as a behavioral instruction. No-op steps create ambiguity and clutter.

**Action required**: Remove Step 3f entirely. Introduce it when `claude -p` is available. The spec should describe current behavior, not placeholders for future behavior.

---

### SE-3: Phase 2 8-Point Audit Is Cited But Absent (Wiegers)
**Section**: §13.2 Phase 2 Exit Criteria

The Phase 2 exit criterion references "Wave 2 Step 3 8-point audit." Section 9 does not contain a numbered 8-point audit checklist. The spec cross-references a document that does not exist within it. The exit gate for the highest-risk phase is unverifiable.

**Action required**: Either reproduce the 8-point audit verbatim within §9 or §13.2, or cite the exact external document and section. If it does not yet exist, Phase 2 is blocked until it is authored.

---

### SE-4: Compliance Tier T02.04 (BUG-006 Fix) Is Under-Classified (Wiegers)
**Section**: §13.2, T02.04

T02.04 fixes BUG-006 — a HIGH severity bug whose absence "breaks the entire invocation chain for the primary command." It is classified LIGHT compliance. A change that fixes a critical invocation chain break in the primary command should be STANDARD minimum.

**Action required**: Reclassify T02.04 to STANDARD compliance.

---

### SE-5: Day 1 Verification Procedure Is Disconnected from Phase 1 Task List (Wiegers)
**Section**: §15, §13.1

The Day 1 verification bash block in §15 is never referenced in T01.02 ("Prerequisite validation") and does not appear in Phase 1 exit criteria. An implementer following only §13 will never find it.

**Action required**: Move the Day 1 verification procedure into T01.02 as its explicit execution specification. Or add a "Pre-Phase-1" section in §13 pointing to §15.

---

### SE-6: `<output-dir>` Is Never Formally Defined (Fowler / Nygard)
**Section**: §10, §9

The return contract lives at `<output-dir>/adversarial/return-contract.yaml`. `<output-dir>` is a parameter placeholder used throughout §9 and §10 but is never formally defined. Consumers cannot reliably construct the path without a definition.

**Action required**: Define `<output-dir>` explicitly in §9 or §10: what resolves it (a flag? the `--output` parameter? a default?), and what its default value is.

---

### SE-7: FM-02 — Stale Return Contract from Prior Run (Nygard)
**Section**: §9, §10

A prior run leaves `return-contract.yaml` in `<output-dir>`. If the current Task agent fails before writing, the consumer reads the old file and processes a stale result from a completely different invocation. There is no write-before-read protection, no run-ID correlation, and no timestamp validation.

**Action required**: Before dispatching the Task agent, either delete the prior contract file or write a `status: pending` sentinel. After Task agent completion, verify file modification timestamp is after dispatch timestamp.

---

### SE-8: BUG-003 Orchestrator Threshold Is MEDIUM — Should Be HIGH (Nygard)
**Section**: §12, BUG-003

BUG-003 documents that Step 3c and Section 5 specify different orchestrator thresholds (3 vs 5). This creates a behavioral fork — the adversarial pipeline's architecture changes depending on which line of code executes. This is not MEDIUM; it is a behavioral inconsistency at the dispatch layer. Fix before Phase 4, not Phase 6 (T06.06).

**Action required**: Reclassify BUG-003 to HIGH. Move its fix to Phase 2 (T02 series) or Phase 3 at latest.

---

## Findings That Are Acknowledged But Need Amplification

Issues the spec already identifies that deserve more prominent treatment:

| Item | Spec Location | Panel Verdict |
|------|--------------|---------------|
| BUG-001 `allowed-tools` missing | §12 HIGH | Correct severity. Fix verification is needed: what does Claude Code actually do when Skill is blocked — error or silent fallback? If silent fallback, BUG-001 fix has zero observable behavioral effect without a test. |
| BUG-004 dual policy doc | §12 MEDIUM | Fowler and Nygard both elevate this to HIGH. When the copies diverge, enforcement operates on a different policy than developers read. |
| `claude -p` ref loader not designed | §16 gap #1 HIGH | Adzic: Without this, Tier 2 is aspirational. The 3-tier model is structurally incomplete. Cannot be indefinitely deferred without acknowledging the model only has 2 tiers in practice. |
| Process requirements in Serena memory only | Appendix | Wiegers (minor N4): The 7 rollback-prevention rules are in Serena memory, not in this document. If memory is cleared, those rules are lost. They belong in §15 or as a pre-phase checklist. |

---

## What the Panel Agrees Is Strong

| Strength | Expert | Note |
|----------|--------|------|
| Evidence-based problem definition (§2) | Wiegers, Adzic | GitHub issues, scored root causes, incident count — rare in sprint specs |
| Decision log with rationale (§17) | Wiegers, Adzic, Fowler | 14 decisions with evidence. REJECTED entry for `--invocation-mode` is discipline |
| Scope boundary precision (§14) | Wiegers, Fowler | Two-column IN/OUT table with explicit deferral rationale for every item |
| Atomic change group definition (§13.7) | Wiegers, Nygard, Crispin | Prevents the exact class of partial-migration failure that caused the rollback |
| Bug inventory honesty (§12) | Wiegers, Adzic, Fowler, Nygard | Self-documenting known defects with phase assignments |
| Producer/consumer ownership in return contract (§10) | Nygard, Crispin | Above-average schema versioning discipline for an internal system |
| Root cause ranking methodology (§3) | Fowler, Wiegers | Weighted scoring formula with explicit deferral cut line |

---

## Recommended Actions Before Sprint Execution

### Must-Fix (sprint blocker without these)

| # | Action | Expert Source | Section |
|---|--------|--------------|---------|
| A1 | Add exit criteria to Phases 4, 5, 6 | CC-1 (4 experts) | §13.4–13.6 |
| A2 | Define scope compensating control or explicitly accept risk | CC-2 (4 experts) | §16b |
| A3 | Specify T01.01 probe procedure with AVAILABLE/NOT_AVAILABLE decision tree | CC-3 (3 experts) | §13.1 |
| A4 | Reproduce 8-point audit in §9 or §13.2 | SE-3 (Wiegers) | §13.2 |
| A5 | Reclassify missing-file case as FAIL not SKIP | CC-5 (3 experts) | §9 Step 3e |
| A6 | Define `<output-dir>` formally | SE-6 (Fowler/Nygard) | §9, §10 |

### Should-Fix (sprint quality, implement in Phase 1–2)

| # | Action | Expert Source | Section |
|---|--------|--------------|---------|
| B1 | Add return contract failure invariants (field values per status) | CC-6 (3 experts) | §10 |
| B2 | Add pre-Phase-1 pointer to §15 Day 1 verification in §13.1 T01.02 | SE-5 (Wiegers) | §13.1, §15 |
| B3 | Reclassify T02.04 BUG-006 fix from LIGHT to STANDARD | SE-4 (Wiegers) | §13.2 |
| B4 | Reclassify BUG-003 from MEDIUM to HIGH, move fix to Phase 2–3 | SE-8 (Nygard) | §12 |
| B5 | Add stale contract protection (pre-dispatch sentinel) to §9 | SE-7 (Nygard) | §9 Step 3d |
| B6 | Implement return contract routing pytest fixtures (3 branches + error cases) | CC-7 Crispin #2 | §16b |
| B7 | Add stale path regression test (5 grep checks as permanent pytest) | CC-7 Crispin #3 | §16b |

### Nice-to-Fix (next iteration)

| # | Action | Expert Source | Section |
|---|--------|--------------|---------|
| C1 | Remove `## Behavioral Summary` from command template, or mark agent-ignored | SE-1 (Fowler) | §5 |
| C2 | Remove Step 3f no-op instruction | SE-2 (Fowler) | §9 |
| C3 | Acknowledge CI is 6/10 enforcement explicitly in Phase 3 exit criteria | CC-4 | §13.3 |
| C4 | Elevate BUG-004 to HIGH, move to Phase 3 (not Phase 6) | Fowler, Nygard | §12 |
| C5 | Restore process requirements (7 rules) into §15 or as pre-phase checklist | Wiegers N4 | §15 |
| C6 | Add `convergence_measured: bool` field to distinguish sentinel from real score | CC-6, Nygard | §10 |
| C7 | Add `invocation_metadata` sub-object to isolate observability fields | Fowler | §10 |

---

## Panel Summary Statement

This specification demonstrates genuine engineering rigor in its diagnostic layer — the evidence base for the problem, the root cause ranking, the decision log, and the scope boundary. These are its real strengths and they should be preserved.

The specification has not completed the transition from **architectural design artifact** to **sprint execution specification**. The distinction is: a design artifact describes what to build and why; a sprint spec adds when something is done, how to verify it worked, and what happens when it fails.

The four most important gaps are not cosmetic:
1. No compensating control for the failure mode that caused the original rollback
2. No exit criteria for the validation phase (Phase 4) or integration phase (Phase 6)
3. The central behavioral claim has no behavioral test
4. The primary enforcement guard (CI Check 7 — correct activation reference) is undesigned

The specification can be made sprint-ready in one focused session addressing A1–A6 above. That work is smaller than it looks: it is six targeted additions to an already well-structured document, not a rewrite.

---

*Consolidated from 5 independent expert reviews.*
*Panel total: ~360,000 tokens of analysis across all reviewers.*
*Generated: 2026-02-24*
