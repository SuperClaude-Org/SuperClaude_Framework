# Diff Analysis: Roadmap Extract Failure Documents

## Metadata
- Generated: 2026-03-07
- Variants compared: 2
- Total differences found: 18
- Categories: structural (3), content (4), contradictions (2), unique (9), shared assumptions (3)

## Structural Differences

| # | Area | Variant A (context) | Variant B (final report) | Severity |
|---|------|---------------------|--------------------------|----------|
| S-001 | Document purpose | Investigative context gathering; stops at "initial conclusion" | Definitive root cause report with solutions and implementation plan | High |
| S-002 | Section count | 11 H2 sections, evidence-gathering structure | 7 H2 sections, analysis-to-action structure | Medium |
| S-003 | Organizational model | Evidence-first: files → flow → contract → evidence → conclusion | Solution-first: summary → cause chain → fix → impact → implementation | High |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|--------------------|--------------------|----------|
| C-001 | Root cause depth | Identifies 3 "likely root-cause families" as hypotheses for further investigation | Presents definitive root cause chain with ASCII diagram showing causal sequence | High |
| C-002 | Fix strategy | No fixes proposed; lists "constraints for follow-up investigation" | 3 prioritized solutions with production-ready code, effort estimates, and risk ratings | High |
| C-003 | Protocol mismatch | Extensively documents that CLI extract prompt is "much thinner" than source `sc-roadmap` protocol; lists 10+ missing frontmatter fields | Not mentioned at all | High |
| C-004 | Quantitative impact | No quantitative analysis | Calculates compound reliability: P(8 steps pass) = 0.9^8 = 43% pre-fix → 100% post-fix | Medium |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|--------------------|--------------------|--------|
| X-001 | Primary root cause | Lists "Artifact framing failure" (raw subprocess output) as first root cause family, implying it is primary | Explicitly labels "Gate validation is brittle" as PRIMARY cause; subprocess capture is merely an "enabler" | High |
| X-002 | CLI invocation flags | Identifies "--verbose + text output" as a third root cause family ("CLI mode incompatibility") suggesting flags contribute to the problem | Does not mention --verbose flag or CLI mode as a contributing factor at all | Medium |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | Comprehensive key files listing across 4 categories (CLI, pipeline, source protocol, runtime artifacts) | Medium |
| U-002 | A | Source protocol mismatch analysis: CLI extract prompt missing 10+ frontmatter fields vs. source `sc-roadmap` protocol | High |
| U-003 | A | CLI mode incompatibility hypothesis: `--verbose` flag may contribute to preamble | Medium |
| U-004 | A | Explicit constraints for evaluating any fix (protocol parity, resumability, gate strictness, fix location) | Medium |
| U-005 | B | Production-ready code for all 3 fixes: regex gate, sanitizer, prompt hardening | High |
| U-006 | B | Impact analysis table mapping all 8 pipeline steps with gate tiers and frontmatter requirements | High |
| U-007 | B | Compound reliability probability analysis (0.9^8 = 43% → 100%) | Medium |
| U-008 | B | 4-phase implementation plan with effort estimates and validation criteria | High |
| U-009 | B | List of 10 analysis artifacts produced during investigation | Low |

## Shared Assumptions

| # | Agreement Source | Assumption | Classification | Promoted |
|---|----------------|------------|----------------|----------|
| A-001 | Both diagnose preamble text as the core issue | The preamble line is the primary obstacle, not a deeper architectural problem with how ClaudeProcess captures output (e.g., stderr mixing, buffering issues) | UNSTATED | Yes |
| A-002 | Both use the 3-field frontmatter contract | The current 3-field frontmatter contract (functional_requirements, complexity_score, complexity_class) is correct and sufficient for the extract step | UNSTATED | Yes |
| A-003 | Both propose code-level fixes | The fix should happen in pipeline code (gates, sanitizer, prompts), not by changing how Claude is invoked (different --output-format, system prompts, or structured output mode) | UNSTATED | Yes |

## Summary
- Total structural differences: 3
- Total content differences: 4
- Total contradictions: 2
- Total unique contributions: 9
- Total shared assumptions surfaced: 3 (UNSTATED: 3, STATED: 0, CONTRADICTED: 0)
- Highest-severity items: S-001, S-003, C-001, C-002, C-003, X-001
