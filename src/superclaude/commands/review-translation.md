---
name: review-translation
description: "Systematic localization review with adversarial validation, real-world evidence search, and comprehensive quality scoring"
category: orchestration
complexity: advanced
mcp-servers: [tavily, sequential, context7, serena]
personas: [localization-reviewer, linguistic-validator, cultural-consultant, research-analyst]
---

# /sc:review-translation - Localization Quality Review System

> **Orchestration Command**: Manages a complete translation review workflow with parallel analysis, adversarial validation, and evidence-based scoring.

## Triggers

- Translation file review requests
- Localization quality assessment
- Multi-language content validation
- Software/game localization QA
- Marketing copy translation review

## Usage

```bash
/sc:review-translation [source-file] [translation-files...] [flags]

# Implicit trigger with files present:
"Review" | "Review these" | "Check translations"
```

### Flags

| Flag | Description |
|------|-------------|
| `--strict` | Enable strict validation mode |
| `--depth [level]` | quick, standard (default), deep |
| `--tone-matrix` | Enable quantified tone calibration |
| `--platform [name]` | steam, playstation, mobile, web, enterprise (default: auto) |
| `--export` | Generate team handoff format |

## Behavioral Summary

7-phase localization review protocol: Phase 0 (file detection and technical validation), Phase 1 (context analysis with mandatory user confirmation gate), Phase 2 (review framework with 6-dimension weighted scoring), Phase 3 (parallel sub-agent deployment per language), Phase 4 (adversarial validation with tiered evidence search for Critical/High issues), Phase 5 (individual per-language reports), Phase 6 (project summary with release readiness), Phase 7 (implementation options). Produces scored reports with severity-classified findings and copy-paste JSON fixes.

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:review-translation-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Examples

### Basic Review
```bash
# Upload English source and translation files, then:
"Review"

# Or explicitly:
/sc:review-translation english.json de_DE.json fr_FR.json es_ES.json
```

### Deep Analysis with Tone Matrix
```bash
/sc:review-translation source.json translations/*.json --depth deep --tone-matrix
```

### Platform-Specific Review
```bash
/sc:review-translation steam_page.json translations/*.json --platform steam --strict
```

### Team Export
```bash
/sc:review-translation source.json *.json --export
```

## Boundaries

**Will:**
- Perform comprehensive linguistic and cultural quality assessment
- Generate prioritized, actionable reports with evidence
- Implement confirmed fixes upon user request
- Search for real-world usage evidence to validate suggestions
- Apply platform-specific validation rules
- Provide structured adversarial validation with confidence levels

**Will Not:**
- Proceed with review before user confirms context analysis
- Mark subjective preferences as critical errors
- Implement changes without explicit user consent
- Replace professional human translator review for high-stakes content
- Modify protected elements (placeholders, brand terms) without approval

## CRITICAL BOUNDARIES

**MANDATORY CONFIRMATION GATE**: Phase 1 context analysis MUST receive user confirmation before any review work begins.

**Output Artifacts:**
1. Individual language reports (`reports/localization/[lang]_review_*.md`)
2. Project summary (`reports/localization/PROJECT_SUMMARY_*.md`)
3. Implementation task list with copy-paste JSON
4. Team export package (if `--export` flag used)

**Next Step**: After review, user chooses to implement fixes, provide feedback, export for team, or skip.
