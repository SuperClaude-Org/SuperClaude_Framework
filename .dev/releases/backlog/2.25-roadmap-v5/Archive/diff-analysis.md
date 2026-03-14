# Diff Analysis: v2.25 Roadmap v5 Spec Comparison

## Metadata
- Generated: 2026-03-13
- Variants compared: 2
- Total differences found: 27
- Categories: structural (5), content (11), contradictions (4), unique contributions (4), shared assumptions (3)
- Focus areas: architecture, feasibility, failure-handling, token-efficiency

---

## Structural Differences

| # | Area | Variant A (Incremental) | Variant B (Structural) | Severity |
|---|------|------------------------|----------------------|----------|
| S-001 | Document organization | 15 sections (1-15) with phased implementation as separate section | 16 sections (1-16) with appendices A-C for type summaries | Low |
| S-002 | Pipeline flow representation | ASCII flow diagram absent; uses inline code blocks for v4 vs v5 comparison | Full ASCII flow diagram (Section 3) with box-style phases | Low |
| S-003 | Section depth | Problem statement uses table-based root cause analysis (F-1 through F-6 identifiers) | Problem statement uses numbered list format for root causes | Low |
| S-004 | Code example density | ~12 concrete Python code blocks with full function signatures | ~10 Python code blocks with some abbreviated ("implementation detail" placeholders) | Medium |
| S-005 | Risk assessment granularity | 9 risks with severity+probability+mitigation; includes R-9 (YAML parsing fragility) with dedicated mitigation detail subsection | 8 risks in matrix + 2 separate structural-refactor risks in prose; less granular mitigations | Medium |

---

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | **Number of new pipeline steps** | 2 new steps (`annotate-deviations`, `deviation-analysis`) inserted between existing steps | 1 new step (`classify-and-validate`) replacing `spec-fidelity` | High |
| C-002 | **Executor primitives** | Zero new executor primitives. Uses only existing `Step`, `GateCriteria`, `SemanticCheck` | Introduces new `LoopStep` dataclass (~30 LOC) and `_execute_loop_step()` function (~90 LOC) in `pipeline/executor.py` | High |
| C-003 | **Spec-fidelity disposition** | Retained but downgraded: `enforcement_tier` STRICT→STANDARD, semantic checks removed. Gate and step remain in pipeline. | Replaced entirely: `classify-and-validate` takes over. `SPEC_FIDELITY_GATE` removed from `_build_steps()` and `ALL_GATES`, retained as deprecated constant. | High |
| C-004 | **Classification architecture** | Two-pass: Scope 2 (annotate, prevent) → Scope 1 (classify, recover). 4-class scheme: `INTENTIONAL_IMPROVEMENT`, `INTENTIONAL_PREFERENCE`, `SCOPE_ADDITION`, `NOT_DISCUSSED` for annotation; 4-class for analysis: `PRE_APPROVED`, `INTENTIONAL`, `SLIP`, `AMBIGUOUS` | Single-pass: One LLM invocation does annotation + fidelity + classification. 3-class scheme: `INTENTIONAL`, `SLIP`, `AMBIGUOUS` | High |
| C-005 | **Remediation loop mechanism** | No loop primitive. Uses `--resume` with `remediation_attempts` counter in `.roadmap-state.json`. Max 2 sequential CLI invocations. | `LoopStep` primitive with `max_iterations=2`. Remediate-certify cycle expressed declaratively in `_build_steps()`. Single CLI invocation. | High |
| C-006 | **Implementation phasing** | 3 phases: Phase 1 (Scope 2, ~200 LOC), Phase 2 (Scope 1, ~350 LOC), Phase 3 (certify hardening, ~150 LOC). Incremental delivery with intermediate value. | Single phase: All 20 deliverables, ~615 LOC total. No intermediate deliverable. | High |
| C-007 | **Finding.deviation_class default** | Default: `""` (empty string). Validates only when non-empty. | Default: `"UNCLASSIFIED"`. Always validates against `VALID_DEVIATION_CLASSES`. | Medium |
| C-008 | **Deviation-to-Finding conversion** | Separate `deviations_to_findings()` function in `remediate.py` that reads `deviation-analysis.md` + `spec-fidelity.md` and produces `Finding` objects | Built into LLM output: `classify-and-validate` prompt instructs LLM to produce structured Finding blocks. Parser function `parse_findings_from_classify_output()` extracts them. | Medium |
| C-009 | **Blast radius analysis** | Included in `deviation-analysis` step for INTENTIONAL deviations: import chain, type contract, interface surface, spec coherence | Deferred to v2.26. `classify-and-validate` does not perform blast radius analysis. | Medium |
| C-010 | **Pipeline step count** | 12 steps (10 core + remediate + certify) | 10 steps (8 core + classify-and-validate + LoopStep composite) | Medium |
| C-011 | **YAML frontmatter routing** | Identifies R-9 risk: nested YAML routing in frontmatter incompatible with `_parse_frontmatter()`. Proposes flat CSV fields (`routing_fix_roadmap: DEV-002,DEV-003`). | Finding blocks embedded in markdown body, parsed by dedicated function. No frontmatter routing. | Medium |

---

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | **Should spec-fidelity be retained?** | Yes, as a diagnostic step (downgraded to STANDARD). "The semantic check functions remain in gates.py... they may be useful for manual validation." | No, replaced entirely by `classify-and-validate`. "Replaces the three-step pipeline proposed in the brainstorm... collapsing them into a single, more efficient step." | High |
| X-002 | **Are new executor primitives needed?** | No. "No new executor loop constructs, no new pipeline control flow, no new dataclass hierarchies." NFR-1 explicitly requires zero new classes in `pipeline/models.py`. | Yes. `LoopStep` is "a new executor primitive that wraps a body of steps in a bounded retry loop." Adds ~120 LOC to the generic pipeline layer. | High |
| X-003 | **Should classification use multiple LLM passes?** | Yes. Two separate LLM invocations (annotate + fidelity), with classification in a third (deviation-analysis). "Scope 2 reduces the work for Scope 1." | No. "A single unified step... eliminates the three-step pipeline." Argues single-pass is "more efficient." | High |
| X-004 | **Finding.deviation_class backward compat strategy** | Empty string default preserves pre-v5 behavior. Validation conditional on non-empty. `VALID_DEVIATION_CLASSES` includes `""`. | `"UNCLASSIFIED"` default with mandatory validation. `VALID_DEVIATION_CLASSES` does NOT include `""`. Always validates. | Medium |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | **Annotation classification granularity**: 4-class annotation scheme distinguishes `INTENTIONAL_IMPROVEMENT` vs. `INTENTIONAL_PREFERENCE` vs. `SCOPE_ADDITION` vs. `NOT_DISCUSSED`. Finer granularity enables nuanced fidelity exclusion (only IMPROVEMENT, not PREFERENCE). | High |
| U-002 | A | **YAML frontmatter parsing risk identification (R-9)**: Identifies that nested YAML in frontmatter is incompatible with existing `_parse_frontmatter()` and proposes flat CSV mitigation. Concrete, actionable risk that would surface during implementation. | High |
| U-003 | B | **LoopStep as reusable primitive**: `LoopStep` is generic — not roadmap-specific. "The sprint pipeline's future test-fix cycle is a natural second consumer." Addresses a systemic gap in the executor. | Medium |
| U-004 | B | **Backward compatibility section (Section 13)**: Explicit coverage of pipeline executor type signature, pipeline models, Finding model, gate registry, and sprint pipeline impact. Comprehensive backward compat analysis. | Medium |

---

## Shared Assumptions

| # | Agreement Source | Assumption | Classification | Promoted |
|---|-----------------|-----------|---------------|----------|
| A-001 | Both variants use `ambiguous_count == 0` as STRICT gate condition | The LLM can reliably distinguish INTENTIONAL vs. SLIP vs. AMBIGUOUS given debate transcript as input | UNSTATED | Yes |
| A-002 | Both variants keep remediate + certify flow for SLIP fixing | The existing remediate executor can fix roadmap.md given structured Finding objects with fix_guidance | UNSTATED | Yes |
| A-003 | Both variants propose `_certified_is_true` semantic check for CERTIFY_GATE | The `_parse_frontmatter()` function can reliably extract `certified: true` from certification report output | STATED | No |

### Promoted Shared Assumptions

| # | Assumption | Impact | Status |
|---|-----------|--------|--------|
| A-001 | LLM classification reliability: Both variants assume the LLM can accurately classify deviations using debate transcript evidence. Neither proposes a fallback if classification accuracy is poor (e.g., >20% misclassification rate). | High — misclassification directly impacts whether SLIPs get fixed or intentional deviations get corrupted | UNSTATED |
| A-002 | Remediate executor capability: Both variants assume the existing remediate executor can apply targeted fixes to roadmap.md given Finding objects. Neither examines whether the current executor handles deviation_class-aware fixes correctly. | Medium — if remediate executor needs changes beyond prompt modifications, both specs underestimate scope | UNSTATED |

---

## Summary
- Total structural differences: 5
- Total content differences: 11
- Total contradictions: 4
- Total unique contributions: 4
- Total shared assumptions surfaced: 3 (UNSTATED: 2, STATED: 1)
- Highest-severity items: C-001, C-002, C-003, C-004, C-005, C-006, X-001, X-002, X-003, U-001, U-002, A-001
