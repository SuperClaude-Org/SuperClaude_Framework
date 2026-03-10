# v1.7 sc:adversarial — Implementation Tasklist

## Legend
- **Status**: `[ ]` pending | `[~]` in progress | `[x]` complete | `[!]` blocked
- **Priority**: P0 (blocker) | P1 (critical) | P2 (important) | P3 (nice-to-have)
- **Effort**: S (≤30min) | M (30-60min) | L (1-2h) | XL (2-4h)

---

## M0: Foundation & Scaffolding [Total: 2-3h]

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T0.1 | Create `src/superclaude/commands/adversarial.md` — command definition with usage, flags table (Section 6), examples (Section 6.3), boundaries (Section 9) | P0 | M | — | [ ] |
| T0.2 | Create `src/superclaude/skills/sc-adversarial/SKILL.md` — behavioral instructions: 5-step protocol overview, input mode handling, convergence logic, error handling, interactive mode behavior | P0 | L | — | [ ] |
| T0.3 | Create `src/superclaude/skills/sc-adversarial/__init__.py` — package marker | P0 | S | — | [ ] |
| T0.4 | Create `src/superclaude/skills/sc-adversarial/refs/debate-protocol.md` — detailed 5-step protocol from Sections 3 (FR-002), convergence detection, round structure | P1 | M | — | [ ] |
| T0.5 | Create `src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md` — full Appendix A algorithm: quant metrics, qual rubric, CEV protocol, combined scoring, tiebreaker, position-bias mitigation | P1 | M | — | [ ] |
| T0.6 | Create `src/superclaude/skills/sc-adversarial/refs/agent-specs.md` — agent specification format, advocate behavior, model/persona/instruction parsing | P1 | S | — | [ ] |
| T0.7 | Create `src/superclaude/skills/sc-adversarial/refs/artifact-templates.md` — output templates for all 6 artifacts (diff-analysis, debate-transcript, base-selection, refactor-plan, merge-log, merged output) | P1 | M | — | [ ] |
| T0.8 | Create `src/superclaude/agents/debate-orchestrator.md` — process coordinator agent: delegates but doesn't participate, opus preferred, tools: Task/Read/Write/Glob/Grep/Bash | P0 | M | — | [ ] |
| T0.9 | Create `src/superclaude/agents/merge-executor.md` — plan executor agent: follows refactoring plan, provenance annotations, tools: Read/Write/Edit/Grep | P0 | S | — | [ ] |
| T0.10 | Run `make sync-dev && make verify-sync` — confirm all files synced to .claude/ | P0 | S | T0.1-T0.9 | [ ] |

**Gate**: All 9 files exist, sync passes. No behavioral testing needed.

---

## M1: Diff Analysis Engine [Total: 3-4h]

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T1.1 | Implement input mode parsing in SKILL.md — `--compare file1,file2,...` (Mode A), `--source/--generate/--agents` (Mode B). Validate 2-10 file range, file existence. | P0 | M | M0 | [ ] |
| T1.2 | Implement variant loading — Mode A: read files, copy to `adversarial/variant-N-original.md`. Mode B: placeholder stubs (actual generation in M5). | P0 | M | T1.1 | [ ] |
| T1.3 | Structural diff — compare heading hierarchies, section ordering, depth levels. Output structured table with severity ratings. | P1 | M | T1.2 | [ ] |
| T1.4 | Content diff — topic-by-topic comparison: requirements coverage, detail level, approach differences. Severity ratings. | P1 | M | T1.2 | [ ] |
| T1.5 | Contradiction detection — per Appendix A protocol: opposing claims on same subject, requirement-constraint conflicts, impossible sequences. Falsifiability requirement. | P1 | L | T1.2 | [ ] |
| T1.6 | Unique contribution extraction — identify ideas in only one variant, assess value (High/Medium/Low). | P2 | S | T1.2 | [ ] |
| T1.7 | Generate `diff-analysis.md` — assemble all sections per artifact template (Section 8.1). Include metadata, counts, severity distributions. | P0 | M | T1.3-T1.6 | [ ] |

**Gate**: Feed 2 real markdown files → inspect diff-analysis.md for completeness and accuracy.

---

## M2: Adversarial Debate Protocol [Total: 6-8h] ★ Critical Path

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T2.1 | Advocate agent instantiation — parse `model[:persona[:"instruction"]]`, create Task agent prompts with steelman instructions, persona behavior, and variant assignment. | P0 | L | M1 | [ ] |
| T2.2 | Round 1 (parallel) — dispatch all advocate agents simultaneously via Task tool. Each receives: their variant, all other variants, diff-analysis.md. Each produces: strengths, weaknesses of others, evidence. | P0 | L | T2.1 | [ ] |
| T2.3 | Round 2 (sequential) — rebuttals. Each advocate receives Round 1 transcript, addresses criticisms with counter-evidence. Only runs for `--depth standard\|deep`. | P0 | L | T2.2 | [ ] |
| T2.4 | Round 3 (conditional) — final arguments. Only runs for `--depth deep` AND convergence < threshold. Includes convergence re-check. | P1 | L | T2.3 | [ ] |
| T2.5 | Convergence detection — track per-point agreement. Configurable threshold (default 80%). Early termination: unanimous agreement, stable 80%+ majority for 2 rounds, position oscillation. | P0 | L | T2.2 | [ ] |
| T2.6 | Per-point scoring matrix — for each diff point, determine winner, confidence %, evidence summary. | P1 | M | T2.3-T2.5 | [ ] |
| T2.7 | Generate `debate-transcript.md` — per artifact template (Section 8.2). Metadata, round transcripts, scoring matrix, convergence assessment. | P0 | M | T2.6 | [ ] |

**Gate**: Feed diff-analysis.md + 2 advocate agents → inspect debate for genuine disagreement (not sycophantic), correct round count, scoring matrix populated.

---

## M3: Hybrid Scoring & Base Selection [Total: 4-6h]

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T3.1 | Quantitative metrics — implement all 5: Requirement Coverage (grep-match), Internal Consistency (contradiction ratio), Specificity Ratio (concrete/vague classifier), Dependency Completeness (internal ref resolver), Section Coverage (normalized count). | P0 | XL | M2 | [ ] |
| T3.2 | Qualitative rubric — implement 25-criterion binary assessment across 5 dimensions (completeness, correctness, structure, clarity, risk coverage). Enforce CEV evidence citation for every criterion. | P0 | L | M2 | [ ] |
| T3.3 | Position-bias mitigation — run qual evaluation twice (forward + reverse variant order). Detect disagreements, re-evaluate with comparison prompt. | P1 | L | T3.2 | [ ] |
| T3.4 | Combined scoring — `(0.50 × quant) + (0.50 × qual)`. Select highest. | P0 | S | T3.1, T3.3 | [ ] |
| T3.5 | Tiebreaker protocol — within-5% detection → debate wins → correctness count → input order. | P1 | S | T3.4 | [ ] |
| T3.6 | Generate `base-selection.md` — per artifact template (Section 8.3). Quant table, qual rubric tables, combined matrix, tiebreaker if applied, selection rationale with evidence. | P0 | M | T3.5 | [ ] |

**Gate**: Run scoring twice on same inputs → quantitative scores must be identical. Qualitative scores should be consistent (within position-bias tolerance).

---

## M4: Refactoring Plan & Merge Execution [Total: 4-6h]

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T4.1 | Refactoring plan generation — for each non-base strength: describe improvement, integration point, risk, merge approach. For each base weakness: reference fix from non-base variant. | P0 | L | M3 | [ ] |
| T4.2 | Interactive mode — implement 4 pause points: after diff analysis, after debate, after base selection, after refactoring plan. Use AskUserQuestion. Default: auto-approve. | P1 | L | T4.1 | [ ] |
| T4.3 | Merge executor — apply each planned change to base document. Use merge-executor agent via Task tool. Maintain structural integrity. | P0 | L | T4.1 | [ ] |
| T4.4 | Provenance annotations — tag merged sections with `<!-- Source: Variant N, Section X.Y -->` comments. | P2 | S | T4.3 | [ ] |
| T4.5 | Post-merge validation — structural integrity check (all headings valid), internal references resolve, contradiction re-scan. | P1 | M | T4.3 | [ ] |
| T4.6 | Generate `refactor-plan.md` + `merge-log.md` — per artifact templates (Sections 8.4). | P0 | M | T4.3 | [ ] |
| T4.7 | Return contract — implement FR-007: merged output path, convergence score, artifacts dir path, status, unresolved conflicts list. | P0 | M | T4.3 | [ ] |

**Gate**: Feed base + other variants + debate transcript → merged output preserves base structure + incorporates improvements + has provenance annotations.

---

## M5: Integration, Polish & Validation [Total: 4-6h]

| # | Task | Priority | Effort | Depends | Status |
|---|------|----------|--------|---------|--------|
| T5.1 | Error handling — implement FR-006 matrix: agent failure (retry + N-1), <10% diff (skip debate), non-convergence (force-select), invalid merge (preserve artifacts), single variant (abort with warning). | P0 | L | M4 | [ ] |
| T5.2 | Mode B variant generation — implement parallel dispatch via Task agents per `--agents` spec. Each agent generates artifact from `--source` per `--generate` type. Wire into Step 1 input. | P0 | L | M4 | [ ] |
| T5.3 | MCP integration — Sequential (Steps 2-4: debate scoring, convergence), Serena (Step 5: memory persistence), Context7 (Step 5: domain pattern validation). Circuit breaker: deep→standard→quick fallback. | P1 | L | M4 | [ ] |
| T5.4 | Framework registration — add sc:adversarial to COMMANDS.md, update ORCHESTRATOR.md routing table, add to PERSONAS.md analyzer triggers. | P1 | M | M4 | [ ] |
| T5.5 | E2E validation — Mode A: compare 2-3 real markdown files, verify all 6 artifacts produced, return contract valid. | P0 | L | T5.1-T5.3 | [ ] |
| T5.6 | E2E validation — Mode B: generate 2 variants from source spec with different model/persona combos, verify full pipeline. | P0 | L | T5.2, T5.5 | [ ] |
| T5.7 | Documentation — update integration guide, add sc:roadmap v2 integration pattern (Section 7.1), add examples. | P2 | M | T5.5 | [ ] |
| T5.8 | Run `make sync-dev && make verify-sync` — final sync. | P0 | S | T5.7 | [ ] |

**Gate**: Full pipeline passes in Mode A and Mode B. Error handling edge cases tested. Framework files updated. Sync clean.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total tasks | 41 |
| P0 (blocker) tasks | 22 |
| P1 (critical) tasks | 14 |
| P2 (important) tasks | 4 |
| P3 (nice-to-have) tasks | 1 |
| New files created | 9 |
| Existing files edited | 3 |
| Estimated total effort | 23-33 hours |
| Critical path | M0 → M1 → M2 → M3 → M4 → M5 |
| Highest-risk milestone | M2 (adversarial debate — sycophancy risk) |

---

*Generated from SC-ADVERSARIAL-SPEC.md v1.1.0 — 2026-02-21*
