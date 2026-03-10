# v1.7 Roadmap: sc:adversarial — Generic Adversarial Debate & Merge Pipeline

## Metadata
- **Version**: 1.7.0
- **Status**: Planned (Backlog)
- **Source Spec**: SC-ADVERSARIAL-SPEC.md v1.1.0
- **Priority**: P1
- **Dependencies**: None (foundational command)
- **Dependents**: sc:roadmap v2 (multi-spec, multi-roadmap modes)
- **Estimated Effort**: 5-7 days (1 developer)
- **Risk Level**: Medium-High (new agent types, multi-model orchestration)

---

## Executive Summary

Implement `/sc:adversarial`, a generic reusable command that orchestrates structured adversarial debate, comparison, and merge across 2-10 artifacts. The pipeline uses multi-model adversarial reasoning (empirically validated: 10-15% accuracy gains, 30%+ factual error reduction) to produce unified outputs that are demonstrably stronger than any single input.

This is a foundational infrastructure command — once built, it can be invoked by sc:roadmap, sc:design, sc:implement, sc:spec-panel, sc:improve, and sc:test.

---

## Milestone Overview

```
M0: Foundation & Scaffolding ─────────────────────── [2-3h]
 │
M1: Diff Analysis Engine (Step 1) ───────────────── [3-4h]
 │
M2: Adversarial Debate Protocol (Step 2) ────────── [6-8h]  ← Core complexity
 │
M3: Hybrid Scoring & Base Selection (Step 3) ─────── [4-6h]
 │
M4: Refactoring Plan & Merge Execution (Steps 4-5) ─ [4-6h]
 │
M5: Integration, Polish & Validation ────────────── [4-6h]
```

**Critical Path**: M0 → M1 → M2 → M3 → M4 → M5 (strictly sequential — each step depends on prior artifacts)

**Total Estimate**: 23-33 hours (~4-5 days)

---

## Dependency Graph

```
M0: Foundation
├── T0.1: Command definition (adversarial.md)
├── T0.2: Skill scaffold (SKILL.md + refs/)
├── T0.3: Agent definitions (debate-orchestrator.md, merge-executor.md)
└── T0.4: Artifact output directory structure logic

M1: Diff Analysis ← M0
├── T1.1: Input mode parsing (Mode A: --compare, Mode B: --source/--generate/--agents)
├── T1.2: Variant file loading and normalization
├── T1.3: Structural diff engine (section ordering, hierarchy depth)
├── T1.4: Content diff engine (requirements coverage, approach comparison)
├── T1.5: Contradiction detection protocol
├── T1.6: Unique contribution extraction
└── T1.7: diff-analysis.md artifact generation

M2: Adversarial Debate ← M1
├── T2.1: Advocate agent instantiation from --agents spec
├── T2.2: Round 1 — parallel advocate statements
├── T2.3: Round 2 — sequential rebuttals (--depth standard|deep)
├── T2.4: Round 3 — final arguments with convergence check (--depth deep)
├── T2.5: Convergence detection (configurable threshold, default 80%)
├── T2.6: Per-point scoring matrix
└── T2.7: debate-transcript.md artifact generation

M3: Scoring & Base Selection ← M2
├── T3.1: Quantitative layer — 5 deterministic metrics (RC, IC, SR, DC, SC)
├── T3.2: Qualitative layer — 25-criterion binary rubric with CEV protocol
├── T3.3: Position-bias mitigation (dual-pass evaluation)
├── T3.4: Combined scoring (50/50 quant/qual)
├── T3.5: Tiebreaker protocol (debate performance → correctness → input order)
└── T3.6: base-selection.md artifact generation

M4: Refactor & Merge ← M3
├── T4.1: Refactoring plan generation from debate outcomes
├── T4.2: Interactive mode checkpoints (--interactive)
├── T4.3: Merge executor — apply planned changes to base
├── T4.4: Provenance annotation system
├── T4.5: Post-merge consistency validation
├── T4.6: refactor-plan.md + merge-log.md artifact generation
└── T4.7: Return contract implementation (FR-007)

M5: Integration & Validation ← M4
├── T5.1: Error handling matrix (FR-006)
├── T5.2: Mode B variant generation (parallel agent dispatch)
├── T5.3: MCP integration (Sequential, Serena, Context7)
├── T5.4: Framework registration (COMMANDS.md, FLAGS.md, ORCHESTRATOR.md updates)
├── T5.5: End-to-end validation — Mode A (compare 2-3 files)
├── T5.6: End-to-end validation — Mode B (generate + compare)
└── T5.7: Documentation and integration guide
```

---

## Milestone Details

### M0: Foundation & Scaffolding [2-3h]

**Objective**: Create all file scaffolds so subsequent milestones have clear targets.

**Deliverables**:

| Task | File | Description | Effort |
|------|------|-------------|--------|
| T0.1 | `src/superclaude/commands/adversarial.md` | Command definition (~80-100 lines): usage, flags, examples, boundaries | 30min |
| T0.2 | `src/superclaude/skills/sc-adversarial/SKILL.md` | Behavioral instructions (~400-500 lines): 5-step protocol, convergence, error handling | 1h |
| T0.3a | `src/superclaude/agents/debate-orchestrator.md` | Process coordinator: delegates but doesn't participate | 30min |
| T0.3b | `src/superclaude/agents/merge-executor.md` | Plan executor: follows refactoring plan, provenance annotations | 30min |
| T0.4 | `src/superclaude/skills/sc-adversarial/refs/` | Reference docs: `debate-protocol.md`, `scoring-protocol.md`, `agent-specs.md`, `artifact-templates.md` | 30min |

**Acceptance**: All files created, `make sync-dev` copies to `.claude/`, `make verify-sync` passes.

**Risk**: Low — scaffolding only, no behavioral logic.

---

### M1: Diff Analysis Engine [3-4h]

**Objective**: Implement Step 1 of the 5-step protocol — systematic comparison of input artifacts.

**Deliverables**:

| Task | Description | Effort | Complexity |
|------|-------------|--------|------------|
| T1.1 | Parse dual input modes: `--compare file1,file2,...` (Mode A) and `--source/--generate/--agents` (Mode B). Validate 2-10 file range. | 30min | Low |
| T1.2 | Load and normalize variant files. Mode A: copy originals to adversarial/ dir. Mode B: placeholder for M5. | 30min | Low |
| T1.3 | Structural diff: compare section ordering, hierarchy depth, heading structure across variants. | 45min | Medium |
| T1.4 | Content diff: compare approaches topic-by-topic, identify coverage differences. | 45min | Medium |
| T1.5 | Contradiction detection: structured scan per Appendix A (opposing claims, requirement-constraint conflicts, impossible sequences). | 45min | Medium-High |
| T1.6 | Unique contribution extraction: identify ideas present in only one variant with value assessment. | 30min | Medium |
| T1.7 | Generate `diff-analysis.md` following the artifact template (Section 8.1 of spec). | 30min | Low |

**Acceptance**: Given 2+ input files, produces a well-structured diff-analysis.md with structural, content, contradiction, and unique contribution sections.

**Risk**: Contradiction detection quality depends on LLM reasoning. Mitigated by CEV-style evidence requirements.

---

### M2: Adversarial Debate Protocol [6-8h] — CRITICAL PATH

**Objective**: Implement Step 2 — structured multi-agent debate with configurable depth and convergence.

**Deliverables**:

| Task | Description | Effort | Complexity |
|------|-------------|--------|------------|
| T2.1 | Advocate agent instantiation: parse `model[:persona[:"instruction"]]` spec, create Task agents with appropriate prompts, steelman instructions. | 1h | Medium |
| T2.2 | Round 1 (parallel): Each advocate receives their variant + all others + diff-analysis.md. Generates: strengths, weaknesses of others, evidence. Run via parallel Task agents. | 1.5h | High |
| T2.3 | Round 2 (sequential): Rebuttals — each advocate receives Round 1 transcripts, addresses criticisms with counter-evidence. Only for `--depth standard\|deep`. | 1.5h | High |
| T2.4 | Round 3 (conditional): Final arguments if `--depth deep` AND convergence < threshold. Continue until convergence or max rounds. | 1h | Medium |
| T2.5 | Convergence detection: per-point agreement tracking, configurable threshold (default 80%). Early termination on unanimous agreement or stable majority. | 1h | Medium |
| T2.6 | Per-point scoring matrix: for each diff point, record winner, confidence, evidence summary. | 30min | Low |
| T2.7 | Generate `debate-transcript.md` following artifact template (Section 8.2). | 30min | Low |

**Acceptance**: Given diff-analysis.md and 2+ advocate agents, produces debate with correct round count, convergence tracking, and per-point scoring.

**Risk**:
- **High**: Advocate agents may converge sycophantically. Mitigated by steelman protocol and explicit "maintain distinct positions" prompting.
- **Medium**: Parallel agent dispatch may hit rate limits. Mitigated by sequential fallback.

---

### M3: Hybrid Scoring & Base Selection [4-6h]

**Objective**: Implement Step 3 — the hybrid quantitative-qualitative scoring protocol from Appendix A.

**Deliverables**:

| Task | Description | Effort | Complexity |
|------|-------------|--------|------------|
| T3.1 | Quantitative layer: implement 5 deterministic metrics. RC via grep-matching against source requirements. IC via contradiction scan. SR via concrete/vague statement classifier. DC via internal reference resolver. SC via section count normalization. | 2h | High |
| T3.2 | Qualitative layer: implement 25-criterion additive binary rubric across 5 dimensions (completeness, correctness, structure, clarity, risk coverage). Enforce CEV evidence citation protocol. | 1.5h | High |
| T3.3 | Position-bias mitigation: run qualitative evaluation twice (forward + reverse order). Detect inconsistencies, re-evaluate conflicting criteria. | 1h | Medium |
| T3.4 | Combined scoring: `variant_score = (0.50 × quant_score) + (0.50 × qual_score)` | 15min | Low |
| T3.5 | Tiebreaker protocol: within-5% detection → debate performance → correctness count → input order. | 30min | Low |
| T3.6 | Generate `base-selection.md` with full scoring breakdown, evidence citations, selection rationale. | 30min | Low |

**Acceptance**: Given variants + debate transcript, produces deterministic quantitative scores, evidence-backed qualitative scores, combined ranking, and documented base selection.

**Risk**:
- **High**: Quantitative metrics require robust text analysis (grep-matching requirements, detecting vague vs. concrete statements). May need iterative refinement.
- **Medium**: Position-bias mitigation doubles qualitative evaluation cost.

---

### M4: Refactoring Plan & Merge Execution [4-6h]

**Objective**: Implement Steps 4-5 — plan generation and unified merge output.

**Deliverables**:

| Task | Description | Effort | Complexity |
|------|-------------|--------|------------|
| T4.1 | Refactoring plan: for each non-base strength from debate, generate improvement description + integration point + risk + merge approach. For each base weakness, reference the non-base fix. | 1.5h | Medium |
| T4.2 | Interactive mode: implement pause points at diff analysis, debate, base selection, and refactoring plan. Use AskUserQuestion for overrides. | 1h | Medium |
| T4.3 | Merge executor: apply each planned change to base document methodically. Maintain structural integrity. | 1.5h | High |
| T4.4 | Provenance annotations: tag merged sections with source attribution (e.g., `<!-- Source: Variant B, Section 3.2 -->`). | 30min | Low |
| T4.5 | Post-merge consistency validation: structural integrity check, internal reference validation, contradiction re-scan. | 30min | Medium |
| T4.6 | Generate `refactor-plan.md` + `merge-log.md` artifacts. | 30min | Low |
| T4.7 | Return contract: path to merged output, convergence score, artifacts dir path, status (success/partial/failed), unresolved conflicts list. | 30min | Low |

**Acceptance**: Given base + other variants + debate transcript, produces a merge plan, executes it to produce a unified document with provenance, and returns the contract.

**Risk**:
- **Medium**: Merge execution may produce structurally broken output. Mitigated by post-merge validation and preserving all original artifacts for manual recovery.

---

### M5: Integration, Polish & Validation [4-6h]

**Objective**: Wire everything together, implement error handling, Mode B generation, MCP integration, and validate end-to-end.

**Deliverables**:

| Task | Description | Effort | Complexity |
|------|-------------|--------|------------|
| T5.1 | Error handling matrix (FR-006): agent failure retry + N-1 fallback, <10% diff skip, non-convergence force-select, invalid merge preservation, single-variant abort. | 1h | Medium |
| T5.2 | Mode B variant generation: parallel dispatch of Task agents per `--agents` spec, each generating an artifact from `--source` using `--generate` type. | 1h | Medium |
| T5.3 | MCP integration: Sequential for debate scoring/convergence analysis (Steps 2-4), Serena for memory persistence of outcomes (Step 5), Context7 for domain pattern validation (Step 5). Circuit breaker fallbacks. | 1h | Medium |
| T5.4 | Framework registration: update COMMANDS.md, FLAGS.md, ORCHESTRATOR.md, PERSONAS.md routing tables for sc:adversarial. | 30min | Low |
| T5.5 | E2E validation — Mode A: compare 2-3 existing markdown files, verify all 5 artifacts produced correctly, verify return contract. | 1h | Medium |
| T5.6 | E2E validation — Mode B: generate 2 variants from a source spec with different agents, run full pipeline. | 1h | Medium |
| T5.7 | Documentation: update integration guide, add examples to command docs, document sc:roadmap v2 integration pattern. | 30min | Low |

**Acceptance**: Full pipeline runs successfully in both Mode A and Mode B. All error handling paths tested. Framework files updated. `make sync-dev && make verify-sync` passes.

**Risk**:
- **Medium**: E2E testing with multiple models may reveal latency issues. Mitigated by parallel dispatch and early termination.

---

## Risk Assessment

| # | Risk | Probability | Impact | Mitigation | Owner |
|---|------|-------------|--------|------------|-------|
| R1 | Sycophantic convergence — advocates agree too quickly | Medium | High | Steelman protocol, explicit "maintain distinct positions" prompting, longer advocate prompts | M2 |
| R2 | Quantitative metrics produce inconsistent results on diverse artifact types | Medium | Medium | Calibrate metrics against test corpus of 3+ artifact types, allow per-type weight overrides | M3 |
| R3 | Merge execution corrupts base document structure | Low | High | Post-merge validation, all originals preserved, merge-log enables manual recovery | M4 |
| R4 | Parallel agent dispatch hits rate limits or timeouts | Medium | Low | Sequential fallback, retry logic, no cost constraints per spec | M2, M5 |
| R5 | Position-bias mitigation disagrees on many criteria, slowing scoring | Low | Medium | Re-evaluation with explicit comparison prompt, cap at 1 re-eval per criterion | M3 |
| R6 | Agents generate nearly identical outputs (Mode B) | Medium | Low | Detect <10% diff, skip debate, return either variant with log | M5 |
| R7 | 10-agent deep debate produces extremely long transcripts | Medium | Low | No token constraints per spec, but document actual usage for future optimization | M2 |
| R8 | Integration with sc:roadmap v2 reveals contract mismatches | Low | Medium | Define return contract early (M4), validate against sc:roadmap expectations in M5 | M4, M5 |

---

## File Manifest

Files to be created (sorted by milestone):

### M0: Scaffolding
```
src/superclaude/commands/adversarial.md                    # ~80-100 lines
src/superclaude/skills/sc-adversarial/SKILL.md             # ~400-500 lines
src/superclaude/skills/sc-adversarial/__init__.py           # Package marker
src/superclaude/skills/sc-adversarial/refs/debate-protocol.md    # 5-step protocol detail
src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md   # Appendix A algorithm
src/superclaude/skills/sc-adversarial/refs/agent-specs.md        # Agent spec format
src/superclaude/skills/sc-adversarial/refs/artifact-templates.md # Output templates
src/superclaude/agents/debate-orchestrator.md               # ~60-80 lines
src/superclaude/agents/merge-executor.md                    # ~40-60 lines
```

### M5: Framework Updates (edits to existing files)
```
COMMANDS.md      # Add sc:adversarial entry
FLAGS.md         # Add --adversarial flags if needed
ORCHESTRATOR.md  # Add routing rules for adversarial pattern
```

**Total new files**: 9
**Total edited files**: 3

---

## Implementation Strategy

### Recommended Approach: Bottom-Up with Artifact Validation

Each milestone produces testable artifacts. Validate each step's output quality before proceeding:

1. **M0**: Scaffold → `make sync-dev` → verify all files exist
2. **M1**: Test with 2 real markdown files → inspect diff-analysis.md quality
3. **M2**: Test with diff-analysis.md from M1 → inspect debate-transcript.md for genuine disagreement (not sycophantic)
4. **M3**: Test with debate transcript → verify scoring determinism (run twice, same quant scores)
5. **M4**: Test merge → verify provenance annotations, structural integrity
6. **M5**: Full pipeline E2E → both modes → error handling edge cases

### Model Selection for Agent Roles

Per spec and research:
- **debate-orchestrator**: Opus (strongest reasoning for scoring/coordination)
- **merge-executor**: Opus or Sonnet (strong writing + structural reasoning)
- **Advocate agents**: Per user's `--agents` spec (any available model)

### Parallel Execution Opportunities

- **M2 T2.2**: Advocate statements generated in parallel (all agents simultaneously)
- **M5 T5.2**: Mode B variant generation in parallel (all agents simultaneously)
- **M3 T3.3**: Position-bias dual-pass can run in parallel (forward + reverse simultaneously)

---

## Success Criteria (from Spec Section 11)

### Functional
- [ ] Mode A (compare) produces valid merged output from 2-10 input files
- [ ] Mode B (generate) produces variants using specified agent configurations
- [ ] All 5 protocol steps execute and produce documented artifacts
- [ ] Debate depth respects --depth flag (1/2/3 rounds)
- [ ] Convergence detection works at configurable threshold
- [ ] Interactive mode pauses at correct decision points
- [ ] Return contract provides all required fields to calling command

### Quality
- [ ] Every decision traceable to evidence in artifacts
- [ ] Merged output incorporates documented strengths from all variants
- [ ] No silent conflict resolution — all contradictions addressed in artifacts
- [ ] Provenance annotations in merged output

### Performance
- [ ] Variant generation runs in parallel (Mode B)
- [ ] Standard depth completes in <5 minutes for typical artifacts
- [ ] 5-10 agents supported without degradation

---

## Next Steps

1. Review this roadmap for completeness and priority alignment
2. Use `/sc:task` to begin executing M0 (Foundation & Scaffolding)
3. After M0, iterate through M1-M5 sequentially with artifact validation at each gate

---

*Generated by /sc:roadmap from SC-ADVERSARIAL-SPEC.md v1.1.0*
*Date: 2026-02-21*
