# 03 — Retrospective & Merged Spec Analysis

**Scope**: v2.07 Sprint Retrospective Consolidated + v2.08 Merged Spec (Roadmap CLI)
**Focus**: Quality — lessons learned vs lessons incorporated
**Date**: 2026-03-08
**Purpose**: Diagnostic only — no fixes proposed

---

## Document Inventory

| Document | Lines | Role |
|----------|-------|------|
| v2.07-sprint-retrospective-consolidated.md | 217 | Post-mortem of first real sprint execution |
| merged-spec.md | 1,096 | Roadmap CLI specification incorporating lessons from v2.03, v2.05, v2.07 |
| v2.03-impact-on-v2.08-analysis.md | Supporting | How diagnostic framework spec influenced roadmap design |
| v2.05-impact-on-v2.08-analysis.md | Supporting | How sprint CLI spec influenced roadmap design |
| v2.07-impact-on-v2.08-adversarial-debate.md | Supporting | Adversarial debate on retrospective implications |

---

## Retrospective Findings vs Merged Spec: Were Lessons Incorporated?

### Finding 1: "No End-to-End Invocation Test" (§4.1, Most Significant Gap)

**Retrospective says**: "Phase 4 validated artifacts structurally but never demonstrated a user typing `/sc:tasklist @roadmap.md` and observing the full command-to-skill-to-output pipeline."

**Merged spec response**: The merged spec's test architecture (§13.6) includes "Full pipeline E2E | Integration (optional) | Requires `claude` binary in PATH... Not in v1 scope."

**Assessment**: **Acknowledged but NOT incorporated.** The retrospective's most significant finding — the absence of end-to-end testing — is explicitly deferred again in the merged spec. The exact same gap identified in v2.07 is carried forward into v2.08. The language changed from "Phase 4 validated artifacts structurally" to "Not in v1 scope — AC-02 validated manually," but the substance is identical: no automated end-to-end test.

### Finding 2: "PARTIAL Status Silently Promoted to PASS" (§5 #1, P0)

**Retrospective says**: `EXIT_RECOMMENDATION: CONTINUE` overrides `status: PARTIAL` in the priority chain. Phase 3 showed as PASS in telemetry despite being PARTIAL.

**Merged spec response**: The merged spec defines a new `StepStatus` enum with PASS, FAIL, TIMEOUT, SKIPPED (§3.2) but does NOT include a PARTIAL status. Sprint's `_phase_to_step()` maps phases to steps with "Sprint's sprint_run_step returns the status based on its own EXIT_RECOMMENDATION parsing."

**Assessment**: **Silently dropped.** The P0 bug from the retrospective is not addressed in the merged spec's new pipeline model. The sprint executor retains its own status logic, and the roadmap executor inherits the pipeline's StepStatus which lacks PARTIAL. The bug is neither fixed nor documented as deferred.

### Finding 3: "`files_changed` Always 0" (§5 #2, P1)

**Retrospective says**: Regex expects human-readable output; Claude uses stream-json NDJSON.

**Merged spec response**: The merged spec introduces `output_format` as a parameter on `ClaudeProcess` — sprint uses `stream-json`, roadmap uses `text`. But the monitor's regex-based extraction is not updated to parse NDJSON events.

**Assessment**: **Partially addressed at architecture level, not at implementation level.** The `output_format` parameterization is correct architecture, but the monitor's signal extraction logic remains regex-based and was not updated. The bug persists.

### Finding 4: "Sprint Runner Telemetry Gaps" (§5, 7 findings)

**Retrospective says**: 7 specific telemetry bugs listed (§5), recommended as "Sprint Runner Improvements (Next Sprint)" action items.

**Merged spec response**: The merged spec's scope (§2) explicitly lists "Changes to sprint's poll loop, TUI, or monitoring subsystems" as Out of Scope for v2.13. Sprint improvements are architectural (hook migration) not behavioral (bug fixes).

**Assessment**: **Acknowledged as out of scope.** The telemetry bugs are known, documented, and explicitly deferred. This is technically correct process, but it means known P0/P1 bugs persist across multiple releases.

### Finding 5: "Adversarial Debate Gaps — ~85-90% Incorporated" (§4.5)

**Retrospective says**: Three specific omissions from adversarial debate: simplified error format, missing forward notes, dropped standalone criterion.

**Merged spec response**: The merged spec includes its own adversarial debate (v2.07-impact-on-v2.08-adversarial-debate.md) but this debates the *impact of retrospective findings on the roadmap spec*, not whether the original adversarial omissions were addressed.

**Assessment**: **Meta-level response without substance.** The workflow responded to "adversarial gaps exist" by conducting more adversarial debate, but about a different topic. The original 10-15% gap in adversarial incorporation was never revisited.

---

## Recurring Themes That Persist Across Releases

### Theme 1: End-to-End Testing Is Always "Next Release"

| Release | E2E Testing Status |
|---------|-------------------|
| v2.03 (Sprint Diagnostic) | L0 tests use fake claude scripts; E2E deferred |
| v2.05 (Sprint CLI Spec) | "Not in v1 scope — AC-02 validated manually" |
| v2.07 (Retrospective) | "No end-to-end invocation test" identified as #1 gap |
| v2.08 (Merged Spec) | "Not in v1 scope" again |
| v2.13 (Pipeline Unification) | "6 untested subsystems remain" |
| v2.19 (Reliability) | Pipeline halts on first real run — the E2E gap manifests |

End-to-end testing is identified as critical in *every release's* retrospective or analysis, and deferred in *every release's* scope definition. This is the single most persistent gap in the workflow.

### Theme 2: Known Bugs Are Documented, Deferred, and Then Rediscovered

| Bug | First Found | Documented Deferral | Rediscovered |
|-----|------------|--------------------|-|
| No PARTIAL status | v2.07 (P0) | v2.08 "out of scope" | Still absent in v2.13 StepStatus |
| files_changed always 0 | v2.07 (P1) | v2.08 "out of scope" | Not fixed as of v2.13 |
| TUI silently dies | v2.03 (root cause) | Not addressed in v2.05 | v2.13 "TUI error resilience" untested |
| Byte-position frontmatter | Implicit in design | Never questioned | v2.19 pipeline halts |

### Theme 3: Confidence Scores Don't Decrease Across Releases

| Release | Self-Assessment |
|---------|----------------|
| v2.03 | "Overall: 8.6/10" |
| v2.07 | "Overall Grade: B+" — despite 7 telemetry bugs |
| v2.08 | Extensive architecture review with expert sign-offs |
| v2.13 | "Option 3 — Targeted Fixes (RECOMMENDED)" — careful, measured |

Every release assesses itself positively. Even the v2.07 retrospective, which found 7 bugs on the first real run, awards a B+ grade because "The work was done completely and accurately according to the spec." This reveals a fundamental issue: quality is measured against the *spec*, not against *production behavior*. If the spec doesn't require E2E testing, then the absence of E2E testing doesn't reduce the grade.

---

## Whether the Merge Process Introduced Contradictions

### Contradiction 1: "No Circular Self-Validation" vs "Gate Checks Are Structural Only"

The merged spec (§1) establishes a core design principle: "Gate validation (gate_passed()) is pure Python — it never invokes Claude to evaluate Claude's output." This prevents circular self-validation.

But the gate checks only validate structural properties: file existence, frontmatter field presence, minimum line count, and basic semantic checks (heading gaps, duplicate headings). A file that passes all gates could contain completely wrong content — wrong requirements, wrong architecture, wrong risk assessment. The gates ensure the *format* is correct but not the *substance*.

The merge process introduced this as a strength ("we prevented the most dangerous failure mode — self-validation!") but it's actually a different kind of weakness: the gates create a false floor of quality. Passing a gate means "this document is structurally well-formed" but the workflow treats it as "this document is correct."

### Contradiction 2: "Conductor Minimalism" vs Rich State Management

The merged spec (§2.1) states: "Conductor minimalism: The conductor's responsibility is step sequencing, gate enforcement, retry logic, and state management. It does not interpret, evaluate, or transform artifact content."

But the conductor *does* make quality judgments — through gates. A `min_lines: 100` gate is a quality judgment ("a roadmap should be at least 100 lines"). An `enforcement_tier: STRICT` designation is a quality judgment. The conductor is minimal in the sense that it doesn't invoke Claude for validation, but it's not minimal in the sense that it makes substantive decisions about what constitutes acceptable output.

### Contradiction 3: "Sprint Test Stability Guarantee" vs Known Breaking Changes

The merged spec (§13.6) guarantees: "All sprint test files passing at extraction start are not modified during pipeline/ migration." It then adds: "Note: v2.07 modified 9 of the original 14 sprint test files; the regression baseline is the post-v2.07 state, not the original test suite."

This means the "stability guarantee" is defined against a moving baseline. If 9 of 14 test files were already modified, the guarantee is that the *already-modified* tests still pass — not that the system's behavior is preserved.

---

## Synthesis

### Top 3 Theories

**Theory 1: Retrospectives Generate Process Artifacts, Not Process Changes**
The v2.07 retrospective identified 7 bugs, 8 action items, and 5 process improvements. The v2.08 merged spec acknowledged these findings but deferred most of them. The retrospective serves as a *documentation* exercise ("we identified the issues") rather than a *change* exercise ("we fixed the issues"). The workflow produces retrospectives because the process requires them, but the content of retrospectives doesn't materially alter the next release's scope.

**Theory 2: The Spec-Compliance Standard Masks Production Failures**
Quality is measured against the spec: "The work was done completely and accurately according to the spec." But if the spec doesn't require E2E testing, then a system that fails on first real use still receives a B+ grade. The quality standard is *spec compliance*, not *production readiness*. This allows every release to claim success while accumulating production-impacting bugs.

**Theory 3: The Merge Process Adds Architectural Constraints Without Removing Deferrals**
Each merge adds new architecture (pipeline/, shared modules, hook protocols) and new constraints (no self-validation, conductor minimalism, NFR-007). But it doesn't remove items from the deferral list. The system grows more architecturally sophisticated while the list of "things we haven't tested" grows longer. Sophistication without coverage is a net negative — more code paths to fail, same number validated.

### Blind Spots

1. **Retrospective action item tracking**: Action items are listed but there's no evidence they're tracked across releases. Items from v2.07 appear as "still open" issues in v2.13 and v2.19.
2. **Quality metrics anchored to spec, not production**: Every quality assessment uses spec compliance as the standard, never "does this work when a user runs it?"
3. **Merge-introduced complexity**: Each merge adds abstractions (PipelineConfig, Step, GateCriteria, SemanticCheck). More abstractions = more potential for semantic drift between abstraction and implementation.
4. **The 10-15% adversarial gap**: The retrospective found ~85-90% adversarial incorporation. The missing 10-15% is never revisited.

### Confidence vs Reality Gaps

| Confidence Claim | Source | Reality |
|------------------|--------|---------|
| "97.4% pass rate (38/39)" | v2.07 §2.1 | The single failure exposed a systemic bug affecting all `-protocol` skills |
| "Sprint runner proved viable for automated release execution" | v2.07 §9 | With 7 telemetry bugs and no E2E testing |
| "B+ Overall Grade" | v2.07 §9 | "PARTIALLY MET items share a common gap: no end-to-end invocation trace" |
| "No criterion was NOT MET" | v2.07 §2.2 | 6 criteria were PARTIALLY MET — the framing makes partial failures sound like successes |
| "Expert Sign-off: Approved" | v2.03, v2.08 | Fictional panel cannot sign off on real-world behavior |

### Evidence Citations

1. v2.07 §4.1: "Phase 4 validated artifacts structurally but never demonstrated a user typing `/sc:tasklist @roadmap.md`"
2. v2.07 §5 #1: "Phase 3 status: `pass` (should be `partial`)" — P0 bug, PARTIAL status silently promoted
3. v2.08 §2: "Out of Scope: TUI / rich progress display (stdout logging only)" — features deferred again
4. v2.08 §13.6: "Full pipeline E2E... Not in v1 scope — AC-02 validated manually" — same deferral as v2.05
5. v2.07 §9: "The work was done completely and accurately according to the spec" — quality measured against spec, not production
6. v2.07 §2.2: "No criterion was NOT MET" — framing that obscures 6 PARTIALLY MET criteria

---

*Analysis complete. Diagnostic only — no fixes proposed.*
