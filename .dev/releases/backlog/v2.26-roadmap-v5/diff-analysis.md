---
total_diff_points: 14
shared_assumptions_count: 22
---

## Shared Assumptions and Agreements

Both variants agree on:

1. Two new pipeline steps: `annotate-deviations` and `deviation-analysis`
2. `annotate-deviations` inserted between `merge` and `test-strategy`; `deviation-analysis` inserted after `spec-fidelity`
3. Zero new executor primitives (Step, GateCriteria, SemanticCheck reuse only)
4. No modifications to generic pipeline layer (NFR-009, NFR-010)
5. `Finding.deviation_class` field with default `"UNCLASSIFIED"` and `__post_init__` validation
6. `_parse_frontmatter()` → `parse_frontmatter()` rename required before downstream work
7. `SPEC_FIDELITY_GATE` downgraded STANDARD; `CERTIFY_GATE` receives `certified_true` check
8. `DEVIATION_ANALYSIS_GATE` is STRICT tier with 6 semantic checks
9. `ANNOTATE_DEVIATIONS_GATE` is STANDARD tier
10. All 8 semantic check functions required (same list)
11. `roadmap_hash` injected as SHA-256 after `annotate-deviations`, using atomic `.tmp` + `os.replace()` write
12. Remediation budget capped at 2 attempts; third triggers terminal halt with `sys.exit(1)` owned by caller
13. `_apply_resume_after_spec_patch()` retired but retained dormant (NFR-019)
14. Fail-closed semantics throughout all new gate checks
15. Anti-laundering requires D-XX + round citation; missing citation → `NOT_DISCUSSED`
16. `schema_version: "2.25"` as first frontmatter field in both new artifacts
17. `_parse_routing_list()` validates `DEV-\d+` regex with whitespace stripping
18. OQ-A (GateCriteria.aux_inputs) must be resolved before coding
19. `deviations_to_findings()` converts only `fix_roadmap` deviations; severity mapping HIGH→BLOCKING, MEDIUM→WARNING, LOW→INFO
20. Stdlib-only dependencies (`hashlib`, `os`, `re`, `json`)
21. SC-1 through SC-10 as acceptance criteria
22. Pre-recorded/mock subprocess fixtures for integration tests (no live Claude calls)

---

## Divergence Points

### 1. Phase Count and Structure

**Opus-Architect**: 4 implementation phases (plus Phase 0 pre-implementation), total 5 phases.

**Haiku-Analyzer**: 5 implementation phases (plus Phase 0), total 6 phases. Splits remediation routing (Phase 4) into its own phase, separate from executor/resume work (Phase 3).

**Impact**: Haiku's separation of remediation routing from executor changes creates a clearer dependency boundary but adds coordination overhead. Opus's consolidation reduces phase transitions but increases per-phase scope, raising the risk of late integration failures.

---

### 2. Remediation Work Placement

**Opus-Architect**: Remediation module (`remediate.py`) work — `deviations_to_findings()`, `_parse_routing_list()`, prompt updates — placed in **Phase 2** alongside prompt builders and step wiring.

**Haiku-Analyzer**: Remediation routing is a dedicated **Phase 4**, explicitly sequenced after executor/state/freshness (Phase 3).

**Impact**: Opus risks building remediation before the executor state model is stable, potentially requiring rework when Phase 3 changes the state shape. Haiku's ordering is safer but extends the critical path.

---

### 3. Parallelization Guidance

**Opus-Architect**: States that within Phase 2, prompt authoring (2.1) and remediation module work (2.3) can proceed in parallel once step wiring decisions (2.2) are made. No other explicit parallelization.

**Haiku-Analyzer**: Provides a detailed parallelization plan across all phases — test drafting during Phase 1, golden artifact preparation during Phase 2, fixture building during Phase 3, negative validation during Phase 4.

**Impact**: Haiku's plan actively shortens calendar time for a team. Opus's plan is adequate for a solo engineer but provides no parallelization guidance for team scenarios.

---

### 4. `fidelity.py` as Modified File

**Opus-Architect**: Lists 6 modified source files; `fidelity.py` is not mentioned.

**Haiku-Analyzer**: Explicitly lists `fidelity.py` (`src/superclaude/cli/roadmap/fidelity.py`) as a required code area.

**Impact**: If `fidelity.py` contains `_extract_fidelity_deviations()` or similar helpers referenced in OQ-E/OQ-F, Opus's omission may indicate an incomplete scope estimate. Haiku's inclusion adds a potential unaccounted modification surface.

---

### 5. Negative Validation Emphasis

**Opus-Architect**: Mentions negative validation briefly in Phase 4 ("prove that intentional deviations are not changed") but does not systematize it.

**Haiku-Analyzer**: Elevates negative validation to a first-class principle throughout — dedicates a section to "what the pipeline refuses to do," frames it as the primary correctness boundary, and lists 5 explicit refusal behaviors as release blockers.

**Impact**: Haiku's framing is meaningfully stronger for a security-sensitive pipeline where silent pass-through of wrong classifications is the primary failure mode.

---

### 6. Open Questions Coverage

**Opus-Architect**: Covers OQ-A, OQ-B, OQ-C, OQ-G, OQ-H as pre-implementation decisions. Notes OQ-J as deferred to v2.26.

**Haiku-Analyzer**: Covers OQ-A, OQ-B, OQ-C, OQ-E, OQ-F, OQ-G, OQ-H, OQ-I, OQ-J — broader coverage including extraction helper signatures (OQ-E/OQ-F) and token-count access confirmation (OQ-I).

**Impact**: Opus's omission of OQ-E/OQ-F may leave the `_extract_fidelity_deviations()` / `_extract_deviation_classes()` interface undefined at the start of Phase 2, risking mid-phase rework.

---

### 7. Timeline Estimates

**Opus-Architect**: 10–14 working days total.

**Haiku-Analyzer**: 9.5–17 working days total, with a wider band reflecting higher uncertainty.

**Impact**: Haiku's wider band is more honest given the 0.92 complexity score and number of unresolved open questions. Opus's tighter estimate may create false confidence, particularly for phases dependent on OQ-A resolution.

---

### 8. Phase 0 Timeline Estimate

**Opus-Architect**: 0.5 day.

**Haiku-Analyzer**: 0.5–1.5 days, explicitly noting that traceability matrix production and architectural freeze documentation take non-trivial time.

**Impact**: Opus underestimates Phase 0 if the team lacks prior context on `GateCriteria` internals. Haiku's range accounts for discovery cost.

---

### 9. Release Criterion Framing

**Opus-Architect**: Release readiness expressed as milestone checklist items (e.g., "SC-1 through SC-10 all verified").

**Haiku-Analyzer**: Explicitly states: "proceed only after Phase 5 evidence review, not on code-complete status alone" and "Block release on evidence, not implementation confidence."

**Impact**: Haiku's framing provides a harder release gate that is less gameable. For an enterprise-complexity feature, this distinction matters operationally.

---

### 10. `_print_terminal_halt()` Design

**Opus-Architect**: Specifies this as a "new/modified function" and details its stderr output requirements. Notes it must NOT call `sys.exit(1)` directly.

**Haiku-Analyzer**: Agrees on the constraint but frames terminal halt behavior as a phase-wide concern requiring both stderr assertion coverage and integration test mock coverage.

**Impact**: Opus provides more precise implementation guidance. Haiku provides more comprehensive test coverage requirements for the same function. Neither is complete without the other.

---

### 11. Graceful Degradation for `total_annotated: 0`

**Opus-Architect**: Explicitly specified — when `annotate-deviations` produces `total_annotated: 0`, log INFO and continue; `deviation-analysis` acts as backstop (FR-089).

**Haiku-Analyzer**: Not explicitly called out as a distinct handling case.

**Impact**: Opus is stronger here. The zero-annotation degradation path is a real operational scenario and omitting it from Haiku's plan creates a gap in edge case coverage.

---

### 12. `routing_update_spec` CLI Summary

**Opus-Architect**: Specifies that `routing_update_spec` summary must be printed in CLI output when non-empty (FR-087).

**Haiku-Analyzer**: Covers the `Spec Update Recommendations` subsection in the prompt but does not specify CLI-level surfacing.

**Impact**: Opus addresses operator visibility for spec-update recommendations; Haiku leaves this implicit. Missing CLI output would reduce operator awareness of deviations requiring spec updates.

---

### 13. Module Placement of `_parse_routing_list()`

**Opus-Architect**: Places `_parse_routing_list()` in `remediate.py`; notes a potential new `parsing.py` module if circular imports arise, as an architectural risk to watch.

**Haiku-Analyzer**: Lists `parsing.py` as a distinct potentially required file from the start; frames circular import avoidance as a Phase 1 concern, not a Phase 2 risk.

**Impact**: Haiku's earlier resolution reduces the risk of a mid-Phase-2 refactor. Opus's defer-until-needed approach is pragmatic but may create cleanup work.

---

### 14. `deviation_class` Validation as Breaking Change Risk

**Opus-Architect**: Lists `R-8` (Finding.deviation_class breaks consumers) as LOW severity, LOW probability, mitigated by default and `__post_init__` validation.

**Haiku-Analyzer**: Addresses backward compatibility as a medium-priority delivery risk with explicit test categories: constructor compatibility tests, state migration tests, static diff review.

**Impact**: Haiku treats this more conservatively, which is appropriate — any consumer constructing `Finding` objects with keyword arguments may silently rely on the existing field signature, and the risk is not fully LOW until those consumers are enumerated.

---

## Areas Where One Variant Is Clearly Stronger

**Opus-Architect is stronger on:**
- Precision of implementation specifications (exact function signatures, gate field lists, step wiring details)
- Graceful degradation for zero-annotation edge case (FR-089)
- CLI-level surfacing of spec-update recommendations (FR-087)
- Concrete milestone checklists with verifiable binary exit criteria per phase
- Risk matrix with specific probability/severity ratings

**Haiku-Analyzer is stronger on:**
- Negative validation as a first-class correctness principle
- Broader open question coverage (OQ-E/OQ-F/OQ-I included)
- Parallelization guidance for team execution
- Release criterion framing ("evidence, not confidence")
- Early placement of circular import risk resolution (Phase 1 vs. Phase 2 risk)
- Conservative timeline estimate with honest uncertainty band
- `fidelity.py` scope inclusion

---

## Areas Requiring Debate to Resolve

1. **Phase structure**: 4 vs. 5 implementation phases — specifically whether remediation routing should be isolated from executor/state work. The case for isolation (Haiku) rests on dependency safety; the case for consolidation (Opus) rests on reducing phase overhead.

2. **Remediation placement timing**: Opus puts `deviations_to_findings()` in Phase 2; Haiku defers to Phase 4. Requires agreement on whether executor state shape is stable enough at Phase 2 completion to safely build against.

3. **`fidelity.py` scope**: Does `fidelity.py` require modification? If extraction helpers live there (OQ-E/OQ-F), Haiku's inclusion is correct and Opus's omission is a gap. Requires codebase inspection to resolve.

4. **Timeline band**: The 10–14 vs. 9.5–17 day range difference is materially large for planning. The team should agree on whether the wider band is warranted given current OQ resolution status.

5. **`_parse_routing_list()` module home**: Decide before Phase 1 (Haiku position) vs. treat as Phase 2 risk (Opus position). Given that circular import restructuring mid-phase is disruptive, Haiku's position is defensible and worth resolving in Phase 0.
