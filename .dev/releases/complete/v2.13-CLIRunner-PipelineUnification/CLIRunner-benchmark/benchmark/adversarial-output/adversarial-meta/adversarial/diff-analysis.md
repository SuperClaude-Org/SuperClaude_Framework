# Diff Analysis: Pipeline Architecture Decision Comparison

## Metadata
- Generated: 2026-03-05
- Variants compared: 2
- Total differences found: 18
- Categories: structural (5), content (6), contradictions (2), unique (5)

## Structural Differences

| # | Area | Variant 1 | Variant 2 | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Document organization model | Challenge-based: 5 named "Challenge" sections followed by 3-option decision framework | Narrative-based: "Verified Findings" then "What Gets Right" / "What Contributes" then phased plan | Medium |
| S-002 | Heading depth | Max depth H3 (22 sections total); heavy use of H2 for challenge framing | Max depth H3 (12 sections total); flatter, more compact structure | Low |
| S-003 | YAML frontmatter | Full frontmatter with title, authors, scope, analysis_type, convergence, base_variant, status | No frontmatter; title only in H1 heading | Medium |
| S-004 | Decision framework placement | Explicit 3-option comparison section with metrics tables for each option | No explicit option comparison; recommendation embedded in phased plan | Medium |
| S-005 | Summary / Q&A section | 6-row "Questions Settled and Open" table with status tracking | "Confidence and Caveats" section splitting verified vs. unverified claims | Low |

## Content Differences

| # | Topic | Variant 1 Approach | Variant 2 Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Evidence depth for extraction history | SETTLED: cites `pipeline/process.py:3`, commit `6548f17`, NFR-007 as definitive proof | Lists as "Unverified" claim — treats extraction history as unconfirmed | High |
| C-002 | Option enumeration | 3 explicit options: Full Unification (rejected), Partial Unification (conditional), Targeted Fixes (recommended) | No explicit option enumeration; goes directly to phased recommendation | Medium |
| C-003 | Recommendation granularity | 6-row targeted-fix table with specific problems, fixes, and effort levels; includes "Accept" rows for non-problems | 3-phase plan (targeted fixes, narrow extractions, re-evaluate) without per-fix effort estimates | Medium |
| C-004 | Revisit conditions | Explicit 3-bullet list: gate-based validation, retry with rollback, third consumer | Implicit: "If those answers show substantial simplification" — less specific triggers | Medium |
| C-005 | Debate round outcomes | Explicit citations: "Variant A conceded in Round 1", "settled by debate", convergence=0.76 | No debate round references; treats conclusions as standing analysis | Low |
| C-006 | Scope of "phased extraction" | Phase 0 (tests) -> Phase 1 (hooks) -> Phase 2 (extraction) -> Phase 3 (swap) — 4 phases with prerequisite chain | Phase 1 (fixes) -> Phase 2 (narrow extractions) -> Phase 3 (re-evaluate) — 3 phases without prerequisite chain | Medium |

## Contradictions

| # | Point of Conflict | Variant 1 Position | Variant 2 Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Pipeline extraction history status | SETTLED fact: "Pipeline was extracted from sprint" — cites `pipeline/process.py:3` and commit `6548f17` as definitive evidence confirmed by both advocates | UNVERIFIED claim: lists "The claim that pipeline was historically extracted from sprint as a half-completed migration" under "Unverified" | High |
| X-002 | Whether full unification reduces complexity | SETTLED: "No. The poll loop relocates into sprint_run_step. Unification eliminates 60-80 lines of sequencing, not the 200+ lines of domain logic." | UNVERIFIED: lists "The claim that full sprint-to-pipeline unification would reduce net complexity rather than repackage it" as unverified, despite the same conclusion being reached in the analysis body | Medium |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | Variant 1 | 7 interleaved subsystems enumeration (subprocess lifecycle, monitor threads, monotonic timeouts, watchdog, tmux, diagnostics, structured logs) — concrete complexity inventory | High |
| U-002 | Variant 1 | Explicit StepRunner Protocol signature analysis: `(Step, PipelineConfig, cancel_check) -> StepResult` with 5-6 captured objects | High |
| U-003 | Variant 1 | 4 benefit-by-benefit rebuttal ("Bug fixes apply everywhere", "New features compose", "Testing surface shrinks", "--file debate disappears") with per-benefit debate outcomes | High |
| U-004 | Variant 2 | "Phased extraction" framing that positions targeted fixes as Phase 1 of a longer extraction roadmap rather than a terminal decision | Medium |
| U-005 | Variant 2 | Explicit "What the Stronger Proposal Still Contributes" section acknowledging the pro-unification position's architectural value even while rejecting its timeline | Medium |

## Summary
- Total structural differences: 5
- Total content differences: 6
- Total contradictions: 2
- Total unique contributions: 5
- Highest-severity items: X-001 (extraction history contradiction), C-001 (evidence depth disagreement)
