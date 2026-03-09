# Base Selection: v2.20 Spec Comparison

## Quantitative Scoring (50% weight)

| Metric | Weight | V1 (FR-051) | V2 (FR-052) | Notes |
|--------|--------|-------------|-------------|-------|
| RC (Requirement Coverage) | 0.30 | **0.95** | 0.60 | V1 addresses all 5 problem requirements (spec→roadmap fidelity, roadmap→tasklist fidelity, gate engine fixes, deviation format, retrospective wiring). V2 skips gate fixes and retrospective wiring entirely. |
| IC (Internal Consistency) | 0.25 | **0.80** | 0.72 | V1: --no-validate split intentionally documented; config placement debatable but coherent. V2: FidelityDeviation serialization to markdown unspecified; boundary_mode values undefined; tasklist "in scope" but deferred — contradiction. |
| SR (Specificity Ratio) | 0.15 | **0.88** | 0.62 | V1: explicit function names, file paths, timeout values (≤120s/600s), retry_limit, gate check names, test names. V2: "conservative conflict escalation" undefined; no timeout numbers; "extend existing subsystem" without function signatures. |
| DC (Dependency Completeness) | 0.15 | **0.85** | 0.78 | V1: Section 4.6 explicit dependency chains (FR-051.4 before FR-051.1; FR-051.2 depends on FR-051.4). V2: "depends on validate_executor.py:365" adequate but code-line references are fragile. |
| SC (Section Coverage) | 0.15 | **0.95** | 0.90 | Both: 11 sections + appendices. V1 marginally broader (retrospective wiring, gate fixes add coverage area). |
| **Quant Total** | — | **0.888** | **0.705** | V1: (0.95×0.30)+(0.80×0.25)+(0.88×0.15)+(0.85×0.15)+(0.95×0.15) = 0.888 |

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| Covers all explicit requirements | — | Addresses all 5 problem requirements: spec→roadmap fidelity (FR-051.1), roadmap→tasklist (FR-051.2), gate fixes (FR-051.3), deviation format (FR-051.4), retrospective wiring (FR-051.5) | **1** | — | Omits gate engine fixes (REFLECT_GATE, cross-ref) and retrospective wiring; scopes only to spec→roadmap + future tasklist contract | **0** |
| Addresses edge cases and failure scenarios | — | 6 risks in Section 7 each with PROBABILITY/IMPACT/MITIGATION; retry_limit: 1 specified; cross-ref fix handles dangling-reference edge case | **1** | — | FR-052.5 degraded validation contract; 6 risks with mitigations; multi-agent failure scenario addressed | **1** |
| Includes dependencies and prerequisites | — | Section 4.6 explicit implementation order with dependency chains; FR-051.1→FR-051.4, FR-051.2→FR-051.4 | **1** | — | Section 4.6 step ordering with numbered dependencies (step 3 depends on 1,2); code line references | **1** |
| Defines success/completion criteria | — | Gate criteria table (Section 5.2) with tier/frontmatter/min-lines/semantic-checks; NFR targets with measurement method; named test suite | **1** | — | Gate criteria table (Section 5.2); NFR targets in table format; named test cases | **1** |
| Specifies what is explicitly out of scope | — | Section 1.2: 6 specific out-of-scope items: "Runtime/execution testing", "Replacing LLM-as-judge", "Sprint runner validation", "Full end-to-end release audit", "brainstorm/spec-panel/adversarial changes", "Score aggregation/REVISE loop" | **1** | — | Section 1.2: 5 specific out-of-scope items with equivalent specificity | **1** |
| **Completeness Total** | | | **5/5** | | | **4/5** |

### Correctness (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| No factual errors or hallucinated claims | — | Bug citations traceable to Forensic Foundation §F-001, Gap Analysis §2.4, §3.2, §3.6; evidence table with specific section references | **1** | — | Evidence table with weighted sources (Weight 1.0, 0.75); findings traceable to forensic-foundation-validated.md and gap-analysis-merged.md | **1** |
| Technical approaches are feasible | — | REFLECT_GATE fix is one-line tier change; _cross_refs_resolve() fix scoped to heading anchor extraction; retrospective file-based (zero new infra); all referenced code paths exist | **1** | — | FidelityDeviation dataclass defined but serialization path to markdown output not specified; boundary_mode values and behavior undefined; "conservative conflict escalation" defined in name only | **0** |
| Terminology used consistently | — | "Fidelity harness", "semantic gate", "seam", "deviation report", "proxy stacking" defined in Appendix A and applied consistently throughout | **1** | — | "Boundary fidelity harness", "degraded validation", "proxy stacking", "semantic fidelity", "structural validation" defined and used consistently throughout | **1** |
| No internal contradictions | — | --no-validate split intentionally documented ("treats fidelity as generation quality gate"); implementation order dependencies coherent | **1** | — | Tasklist is "in scope" per Section 1.2 ("Normalize deviation reporting for roadmap and tasklist-era validators") but deferred to future release — contradictory framing. FidelityDeviation dataclass lacks serialization path. | **0** |
| Claims supported by evidence | — | Problem statement evidence table (8 rows with source, evidence, impact); design decisions table with rationale vs alternatives considered | **1** | — | Evidence table with source weights; design decisions table with alternatives considered; high-quality attribution throughout | **1** |
| **Correctness Total** | | | **5/5** | | | **3/5** |

### Structure (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| Logical section ordering | — | Problem (1) → Solution (2) → FRs (3) → Architecture (4) → Interfaces (5) → NFRs (6) → Risks (7) → Tests (8) → Migration (9) → Downstream (10) → Open Items (11) — standard spec flow | **1** | — | Same logical ordering maintained | **1** |
| Consistent hierarchy depth | — | H2 top-level sections, H3 subsections, H4 detail consistently applied throughout; code blocks properly fenced | **1** | — | Sections 3–11 formatted as plain text numbered lists ("3. Functional Requirements") rather than markdown H2 headers; tables rendered as ASCII boxes rather than markdown pipes — structural inconsistency | **0** |
| Clear separation of concerns | — | Generation pipeline concerns (executor.py) clearly separated from validate pipeline (validate_executor.py); tasklist module (cli/tasklist/) separated from roadmap module | **1** | — | Validate subsystem extension clearly separated from future tasklist work; boundary_mode parameterizes concerns | **1** |
| Navigation aids present | — | FR-051.1 through FR-051.5 cross-referenced in Section 4.2 (Modified Files), 4.3 (Module Dependency), 4.6 (Implementation Order); section refs used throughout | **1** | — | OI-052-1 through OI-052-4 cross-referenced; code line references (commands.py:128, executor.py:618); dependency graph in Section 4.4 | **1** |
| Follows artifact type conventions | — | YAML frontmatter (properly fenced), numbered FRs with acceptance criteria checklists (- [ ] items), data models in fenced Python code blocks, deviation report example in fenced code | **1** | — | YAML frontmatter present but unclosed (leading spaces, no closing fence); sections 3–11 use plain text not markdown; table formatting inconsistent (mix of pipes and ASCII boxes) | **0** |
| **Structure Total** | | | **5/5** | | | **3/5** |

### Clarity (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| Unambiguous language | — | "Gate blocks if high_severity_count > 0" — binary, deterministic; "_high_severity_count_zero returns False if field missing" — defensive, deterministic | **1** | — | "conservative conflict escalation" — undefined escalation path; "does not materially exceed" — vague; boundary_mode values not specified | **0** |
| Concrete rather than abstract | — | Function signatures (build_spec_fidelity_prompt(spec_content: str, roadmap_content: str) -> str), file paths, timeout values (600s), retry_limit (1), test names all specified | **1** | — | "extend existing subsystem" without function signatures; no timeout numbers; "one additional validation subprocess per boundary" — how many boundaries? | **0** |
| Each section has clear purpose | — | Section headings match content precisely; each FR section has Description + Acceptance Criteria + Dependencies | **1** | — | Section headings match content; FR sections have Description + ACs + Dependencies despite formatting issues | **1** |
| Acronyms and terms defined | — | Appendix A glossary: Fidelity harness, Semantic gate, Seam, Deviation report, Proxy stacking — 5 terms defined | **1** | — | Appendix A: Boundary fidelity harness, Structural validation, Semantic fidelity, Proxy stacking, Degraded validation — 5 terms defined | **1** |
| Actionable next steps clearly identified | — | Section 4.6 implementation order (parallel/sequential); Section 10 downstream inputs for sc:roadmap and sc:tasklist with specific task breakdowns | **1** | — | Section 10 downstream inputs with milestone themes and task breakdowns; Section 4.6 implementation order | **1** |
| **Clarity Total** | | | **5/5** | | | **3/5** |

### Risk Coverage (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| Identifies ≥3 risks with probability and impact | — | Section 7: 6 risks, each with PROBABILITY (LOW/MEDIUM) and IMPACT (LOW/MEDIUM) ratings | **1** | — | Section 7: 6 risks with MED/HIGH probability/impact ratings | **1** |
| Provides mitigation for each risk | — | Each risk has explicit mitigation: "Gate checks frontmatter only; prompt emphasizes consistency requirement"; "Test against existing artifacts"; "Prompt frames retrospective as areas to watch" | **1** | — | Each risk has mitigation column: "Require paired evidence quotes"; "Keep roadmap validate as single entrypoint"; "Block only on HIGH severity in initial rollout" | **1** |
| Addresses failure modes and recovery | — | Section 9 Rollback plan: "Gate fixes are isolated to specific gate definitions; reverting is a one-line tier change"; spec-fidelity step can be disabled via _build_steps() | **1** | — | Section 9 Rollback plan: "Disable fidelity step from auto-validation path while retaining codepaths; existing reflect/merge validation remains operational" | **1** |
| Considers external dependencies and failure scenarios | — | Risk: "Tasklist fidelity check requires reading multiple phase files, increasing token cost" — external dependency failure; Risk: "Retrospective wiring biases extraction toward prior failures" | **1** | — | Risk: "State/inference of spec path fails during resume flows" — runtime failure; Risk: "Blocking semantic gates increase friction on noisy outputs" — external AI reliability | **1** |
| Monitoring/validation for risk detection | — | NFR-051.4 "All existing passing tests continue to pass" — regression monitoring; NFR-051.5 "Gate can extract severity counts from 100% of well-formed reports" — output monitoring. No runtime monitoring mechanism. | **0** | — | No runtime monitoring mechanism specified | **0** |
| **Risk Coverage Total** | | | **4/5** | | | **4/5** |

### Invariant & Edge Case Coverage (5 criteria)

| Criterion | V1 | V1 Evidence | Verdict | V2 | V2 Evidence | Verdict |
|-----------|----|-----------|---------|----|-------------|---------|
| Boundary conditions (empty collections) | — | No handling specified for empty spec, empty roadmap, or reports with zero deviations (success case vs failure case) | **0** | — | FR-052.2 AC: "Reports distinguish between 'no deviations found' and 'validation incomplete/degraded'" — explicit empty-collection distinction | **1** |
| State variable interactions across boundaries | — | Risk documented: "REFLECT_GATE promotion to STRICT causes existing valid validation reports to fail" — identifies state interaction; but no mechanism to track cross-stage state | **0** | — | .roadmap-state.json records semantic pass/fail/skipped status; state persistence prevents cross-stage state loss | **1** |
| Guard condition gaps | — | `_high_severity_count_zero` returns False if field missing (defensive guard); Section 11 open item: "Should gate verify frontmatter counts match actual table row counts?" | **1** | — | boundary_mode values and guard conditions not specified; validation_complete:false/true logic not defined for all paths | **0** |
| Count divergence scenarios | — | Risk identified: "LLM produces inconsistent deviation counts (frontmatter says 0 HIGH but table contains HIGH rows)" — but no guard against this in gate semantic check | **0** | — | FR-052.2 AC: "Reports include machine-parseable counts for blocking/warning/info severities" — but no cross-validation of counts vs. table rows | **0** |
| Interaction effects | — | Risk: "REFLECT_GATE promotion to STRICT may cause existing valid validation reports to fail" — interaction between gate change and existing artifacts; retrospective wiring biases extraction | **1** | — | No analysis of interaction between FidelityDeviation dataclass, state persistence, degraded validation, and multi-agent merge paths | **0** |
| **Invariant & Edge Case Total** | | | **2/5** | | | **2/5** |

---

### Qualitative Summary

| Dimension | V1 (FR-051) | V2 (FR-052) |
|-----------|-------------|-------------|
| Completeness | 5/5 | 4/5 |
| Correctness | 5/5 | 3/5 |
| Structure | 5/5 | 3/5 |
| Clarity | 5/5 | 3/5 |
| Risk Coverage | 4/5 | 4/5 |
| Invariant & Edge Case | 2/5 | 2/5 |
| **Total** | **26/30** | **19/30** |

### Edge Case Floor Check

| Variant | Invariant & Edge Case Score | Eligible as Base? |
|---------|-----------------------------|-------------------|
| V1 (FR-051) | 2/5 | ✅ Yes (≥1/5) |
| V2 (FR-052) | 2/5 | ✅ Yes (≥1/5) |

Both variants eligible. No floor suspension needed.

---

## Combined Scoring

| Variant | Quant (×0.50) | Qual Score | Qual (×0.50) | Final Score |
|---------|---------------|------------|--------------|-------------|
| V1 (FR-051) | 0.888 × 0.50 = **0.444** | 26/30 = 0.867 | 0.867 × 0.50 = **0.433** | **0.877** |
| V2 (FR-052) | 0.705 × 0.50 = **0.353** | 19/30 = 0.633 | 0.633 × 0.50 = **0.317** | **0.670** |

**Margin: 20.7% — no tiebreaker required.**

---

## Selected Base: Variant 1 (FR-051)

### Selection Rationale

Variant 1 (FR-051) wins by a 20.7% margin across both quantitative and qualitative dimensions. The primary drivers:

1. **Requirement coverage**: FR-051 addresses all five problem requirements stated in the diagnostic evidence. FR-052 omits three (REFLECT_GATE fix, cross-ref fix, retrospective wiring) — confirmed production issues that the spec's own problem statement identifies as causative.

2. **Correctness**: FR-051 scores 5/5 on correctness; FR-052 scores 3/5. FR-052 fails on feasibility (FidelityDeviation serialization unspecified, boundary_mode undefined) and internal consistency (tasklist "in scope" but deferred).

3. **Structure and Clarity**: FR-051 scores 5/5 on both; FR-052 scores 3/5 on both. FR-052's markdown formatting issues (plain text section headers, ASCII table boxes) reduce parsability and professional quality.

4. **Debate outcome**: V2 advocate conceded REFLECT_GATE omission is "indefensible," cross-ref fix omission is "a miss," and NFR timeout omission is "operationally dangerous" — three high-severity concessions on points where FR-052 is silent.

The central architectural dispute (generation pipeline vs validate subsystem) was contested and resolved in V1's favor on consequence: V2's placement enables `--no-validate` to bypass fidelity, which inverts the harness's purpose.

### Strengths to Preserve from Base (V1)

1. **FR-051.1**: Spec-fidelity as generation pipeline step — mandatory, not bypassable
2. **FR-051.3**: REFLECT_GATE STANDARD→STRICT promotion — confirmed bug fix
3. **FR-051.4**: `_cross_refs_resolve()` actual validation — confirmed bug fix
4. **FR-051.5**: Retrospective wiring (`--retrospective` flag, extract prompt extension)
5. **FR-051.4 deviation schema**: 3-tier severity (high/medium/low) + total_deviations + upstream_file + downstream_file
6. **Explicit NFR timeouts**: ≤120s per step, 600s ceiling, retry_limit: 1
7. **Named gate predicate**: `_high_severity_count_zero(content)` returns False if field missing (defensive)
8. **Comprehensive test suite**: 19+ unit tests (named), 6 integration tests (named)
9. **Tasklist CLI delivery**: `superclaude tasklist validate` with `cli/tasklist/` module

### Strengths to Incorporate from Non-Base (V2)

1. **S-005 / U-006**: `FidelityDeviation` Python dataclass — adopt as backing model behind frontmatter serialization
2. **S-006 / U-007**: State persistence to `.roadmap-state.json` — write fidelity semantic pass/fail/skipped after each run
3. **U-008 / C-006 / FR-052.5**: Degraded validation contract — add `validation_complete: false` path when fidelity agent fails rather than hard pipeline failure; add `fidelity_check_attempted` field for disambiguation
4. **S-008**: Multi-agent fidelity merge protocol — define behavior when multiple agents produce conflicting fidelity assessments (conservative escalation: unresolved = treat as HIGH)
5. **X-006**: `tasklist_ready` field — add to deviation report frontmatter as explicit boolean gate signal
6. **OI-052-1**: Open item "Should spec→roadmap fidelity run before or after existing reflect validation?" — adopt as explicit open item requiring resolution before implementation
7. **OI-052-2**: Open item "Should MEDIUM severity become blocking for certain boundary classes?" — adopt for gate finalization discussion
