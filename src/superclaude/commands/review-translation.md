---
name: review-translation
description: "Systematic localization review with adversarial validation, real-world evidence search, and comprehensive quality scoring"
category: orchestration
complexity: advanced
mcp-servers: [tavily, sequential, context7, serena]
personas: [localization-reviewer, linguistic-validator, cultural-consultant, research-analyst]
---

# /sc:review-translation - Localization Quality Review System

> **Orchestration Command**: This command manages a complete translation review workflow with parallel analysis, adversarial validation, and evidence-based scoring. Produces actionable reports with prioritized fixes.

## Triggers
- Translation file review requests (e.g., "Review", "Review translations", "Check localization")
- Localization quality assessment
- Multi-language content validation
- Steam/game/software localization QA
- Marketing copy translation review

## Context Trigger Pattern
```
/sc:review-translation [source-file] [translation-files...] [--strict] [--depth quick|standard|deep]

# Implicit trigger - when source + translation files are provided:
"Review" | "Review these" | "Check translations" | "Validate localization"
```

## Orchestration Protocol

### Phase 0: File Detection & Validation
```yaml
Automatic Detection:
  1. Identify source file (English .json or specified)
  2. Locate all translation files (language code pattern: *_de.json, *_fr.json, etc.)
  3. Validate file structure compatibility
  4. Report: "Found [N] translation files for review against [source]"

Validation Checks:
  - JSON structure validity
  - Key parity (missing/extra keys)
  - Encoding consistency (UTF-8)
  - Placeholder preservation ({0}, %s, etc.)
```

### Phase 1: Context Analysis (REQUIRED - Chain of Thought)

**CRITICAL**: This phase MUST complete with user confirmation before ANY review work begins.

```yaml
Chain of Thought Analysis:
  1. Product Context Extraction:
     - Analyze source content for product type indicators
     - Identify industry markers (gaming, SaaS, e-commerce, etc.)
     - Detect brand voice signals (formal/casual, technical/accessible)
     - Note domain-specific terminology

  2. Audience Inference:
     - Demographics indicators (age range, expertise level)
     - Geographic distribution (global vs regional)
     - Cultural context requirements
     - Accessibility considerations

  3. Use Case Classification:
     - Marketing copy (persuasive, emotional)
     - UI/UX text (clarity, brevity)
     - Legal/compliance (precision, formality)
     - Documentation (technical accuracy)
     - Entertainment/gaming (immersion, tone)

  4. Tone Mapping:
     Per-language considerations:
       - Formality level (T-V distinction languages)
       - Humor/wordplay transferability
       - Cultural sensitivity requirements
       - Regional variant selection (es-ES vs es-LA, pt-BR vs pt-PT, zh-CN vs zh-TW)

Output - Context Summary for User Confirmation:
  ┌─────────────────────────────────────────────────┐
  │ 📋 LOCALIZATION CONTEXT ANALYSIS                │
  ├─────────────────────────────────────────────────┤
  │ Product Type: [Game/SaaS/E-commerce/etc.]       │
  │ Target Audience: [Description]                  │
  │ Primary Use Case: [Marketing/UI/Legal/etc.]     │
  │ Recommended Tone: [Formal/Casual/Technical]     │
  │                                                 │
  │ Language-Specific Considerations:               │
  │ • German: [formal Sie/informal du]              │
  │ • French: [France/Canada variant]               │
  │ • Spanish: [Spain/LatAm variant]                │
  │ • [etc.]                                        │
  │                                                 │
  │ ⚠️  CONFIRMATION REQUIRED                       │
  │ Please confirm or provide feedback on this      │
  │ context analysis before review proceeds.        │
  └─────────────────────────────────────────────────┘

STOP AND WAIT: Do not proceed until user confirms or provides corrections.
```

### Phase 2: Review Framework Definition

```yaml
Scoring KPIs (Weighted):
  1. Accuracy (30%):
     - Semantic fidelity to source
     - No additions/omissions
     - Correct terminology

  2. Fluency (25%):
     - Natural expression in target language
     - Grammar and syntax correctness
     - Idiomatic usage

  3. Consistency (20%):
     - Terminology consistency within file
     - Style consistency with brand voice
     - Format consistency (capitalization, punctuation)

  4. Cultural Adaptation (15%):
     - Appropriate localization vs translation
     - Cultural sensitivity
     - Regional appropriateness

  5. Technical Compliance (10%):
     - Placeholder preservation
     - Character limits (if applicable)
     - Format string validity

Severity Classification:
  🔴 Critical (Must Fix):
     - Meaning reversal or significant distortion
     - Offensive or culturally inappropriate content
     - Broken placeholders/variables
     - Legal/compliance violations

  🟠 High Priority:
     - Notable accuracy issues
     - Grammar errors affecting comprehension
     - Inconsistent terminology for key terms

  🟡 Medium Priority:
     - Minor fluency issues
     - Style inconsistencies
     - Non-optimal word choices

  🟢 Low Priority (Suggestions):
     - Preference-based improvements
     - Minor polish opportunities
     - Alternative phrasings
```

### Phase 3: Parallel Sub-Agent Deployment

```yaml
Orchestration Pattern:
  Spawn parallel review agents (one per translation file):

  Agent Configuration:
    - Agent ID: review-[language-code]
    - Input: Source file + Target translation file
    - Context: Confirmed context from Phase 1
    - Framework: Scoring KPIs from Phase 2

  Per-Agent Workflow:
    1. Full file scan with source comparison
    2. Issue identification and classification
    3. Severity assignment per finding
    4. Score calculation per KPI
    5. Preliminary report generation

  Synchronization:
    - All agents complete before Phase 4
    - Aggregate findings for cross-language patterns
    - Identify systematic issues across translations
```

### Phase 4: Adversarial Validation (For Issues Found)

```yaml
Trigger: When Critical or High Priority issues are identified

Adversarial Debate Protocol:
  1. Challenger Role:
     - Question the validity of each finding
     - Consider alternative interpretations
     - Check if "error" might be intentional localization
     - Verify against target language norms

  2. Defender Role:
     - Justify original assessment with evidence
     - Cite linguistic rules or conventions
     - Reference source meaning preservation
     - Provide authoritative sources

  3. Resolution:
     - Findings that survive challenge → Confirmed
     - Findings refuted → Downgraded or removed
     - Ambiguous cases → Flagged for human review

Research Sub-Agent Activation:
  For each confirmed error/suggestion:
    1. Search for real-world usage of suggested phrase
    2. Prioritize similar context (gaming, marketing, etc.)
    3. Find evidence of native speaker usage
    4. Document sources for validation

  Search Patterns:
    - "[suggested phrase]" site:[target-language-domains]
    - "[suggested phrase]" [product-context]
    - Comparison: original vs suggested frequency

  Evidence Requirements:
    - Minimum 2-3 independent sources for suggestions
    - Native speaker content preferred
    - Context similarity weighted
```

### Phase 5: Individual Report Generation

```yaml
Report Template Per Language:
  File: reports/localization/[language-code]_review_[timestamp].md

  Structure:
  ───────────────────────────────────────────────────
  # [Language] Localization Review Report

  ## Executive Summary
  | Metric | Value |
  |--------|-------|
  | Overall Score | [X]/100 |
  | Grade | [PASS/FAIL] |
  | Critical Issues | [N] |
  | High Priority | [N] |
  | Total Findings | [N] |

  ## Pass/Fail Criteria
  - PASS: Score ≥75, Zero Critical Issues
  - FAIL: Score <75 OR Any Critical Issues

  ## Critical Issues (Immediate Action Required)

  ### Issue #1: [Brief Description]
  - **Location**: Key: `[key_name]`
  - **Source**: "[original English text]"
  - **Current**: "[current translation]"
  - **Problem**: [Description of the issue]
  - **Severity**: 🔴 Critical
  - **Proposed Fix**: "[suggested correction]"
  - **Evidence**: [Link/source validating suggestion]

  [Repeat for all critical issues...]

  ## High Priority Issues
  [Same format as critical...]

  ## Score Breakdown
  | KPI | Score | Weight | Weighted |
  |-----|-------|--------|----------|
  | Accuracy | [X]/100 | 30% | [X] |
  | Fluency | [X]/100 | 25% | [X] |
  | Consistency | [X]/100 | 20% | [X] |
  | Cultural Adaptation | [X]/100 | 15% | [X] |
  | Technical Compliance | [X]/100 | 10% | [X] |
  | **Total** | | | **[X]/100** |

  ## Medium Priority Issues
  [Condensed format...]

  ## Low Priority Suggestions
  [Condensed format...]

  ## Validation Evidence
  ### Suggested Phrase Evidence
  - "[phrase 1]": [Source 1], [Source 2]
  - "[phrase 2]": [Source 1], [Source 2]

  ## Methodology Notes
  [Any language-specific considerations applied]
  ───────────────────────────────────────────────────
```

### Phase 6: Project Summary Generation

```yaml
Summary Report:
  File: reports/localization/PROJECT_SUMMARY_[timestamp].md

  Structure:
  ───────────────────────────────────────────────────
  # Localization Review - Project Summary

  ## Review Matrix
  | Language | Score | Accuracy | Fluency | Consistency | Cultural | Technical | Status | Critical | High |
  |----------|-------|----------|---------|-------------|----------|-----------|--------|----------|------|
  | German   | 85    | 88       | 82      | 85          | 80       | 95        | ✅ PASS | 0        | 2    |
  | French   | 72    | 70       | 75      | 70          | 75       | 90        | ❌ FAIL | 1        | 4    |
  | Spanish  | 91    | 92       | 90      | 88          | 92       | 95        | ✅ PASS | 0        | 1    |
  | [...]    |       |          |         |             |          |           |        |          |      |

  ## Overall Statistics
  - Total Languages: [N]
  - Passed: [N] ([%])
  - Failed: [N] ([%])
  - Average Score: [X]/100

  ## All Critical Issues
  [Aggregated list from all languages with links to individual reports]

  | # | Language | Key | Issue | Proposed Fix |
  |---|----------|-----|-------|--------------|
  | 1 | French   | `key_x` | Meaning reversal | "[fix]" |
  | 2 | Japanese | `key_y` | Broken placeholder | "[fix]" |

  ## All High Priority Issues
  [Aggregated list...]

  ## Implementation Task List

  ### Critical Fixes (Complete First)
  - [ ] **French `key_x`**: Change "[current]" → "[proposed]"
        - File: `fr_FR.json`
        - Line: [N]
        - Validation: Run JSON lint after edit

  - [ ] **Japanese `key_y`**: Change "[current]" → "[proposed]"
        - File: `ja_JP.json`
        - Line: [N]
        - Validation: Verify placeholder count matches source

  ### High Priority Fixes
  [Same format...]

  ## Individual Reports
  - [German Review](./de_DE_review_[timestamp].md)
  - [French Review](./fr_FR_review_[timestamp].md)
  - [Spanish Review](./es_ES_review_[timestamp].md)
  - [...]
  ───────────────────────────────────────────────────
```

### Phase 7: User Prompt & Implementation Path

```yaml
Completion Output:
  ┌─────────────────────────────────────────────────┐
  │ ✅ LOCALIZATION REVIEW COMPLETE                 │
  ├─────────────────────────────────────────────────┤
  │ Summary: [N] languages reviewed                 │
  │ Passed: [N] | Failed: [N]                       │
  │ Critical Issues: [N] | High Priority: [N]       │
  │                                                 │
  │ 📁 Reports Generated:                           │
  │ • PROJECT_SUMMARY_[timestamp].md                │
  │ • [language]_review_[timestamp].md (×N)         │
  │                                                 │
  │ 📋 Task List: [N] fixes documented              │
  │                                                 │
  │ ─────────────────────────────────────────────── │
  │ NEXT STEPS:                                     │
  │                                                 │
  │ 1️⃣  Review the PROJECT_SUMMARY for overview     │
  │ 2️⃣  Check individual reports for details        │
  │ 3️⃣  Choose your action:                         │
  │                                                 │
  │ 🔧 "Implement fixes" - Apply all critical/high  │
  │    priority fixes automatically                 │
  │                                                 │
  │ 📝 "Implement [language] fixes" - Apply fixes   │
  │    for specific language only                   │
  │                                                 │
  │ 💬 "I have feedback on [issue]" - Discuss       │
  │    specific findings before implementation      │
  │                                                 │
  │ ⏭️  "Skip implementation" - Keep reports only   │
  └─────────────────────────────────────────────────┘

Implementation Execution (if requested):
  1. Parse task list from PROJECT_SUMMARY
  2. Read target translation files
  3. Apply edits with validation:
     - Verify key exists
     - Confirm placeholder preservation
     - Validate JSON structure post-edit
  4. Generate change summary
  5. Offer to create git commit with changes
```

## Tool Coordination

- **Read**: Source and translation file parsing, JSON validation
- **Write**: Report generation (individual + summary)
- **Task**: Parallel sub-agent deployment for multi-file review
- **WebSearch/Tavily**: Real-world usage evidence search
- **TodoWrite**: Progress tracking across review phases
- **Edit**: Translation fix implementation
- **Bash**: JSON validation, git operations

## Key Patterns

- **Context-First Analysis**: Understand before judging → appropriate evaluation criteria
- **Parallel Review**: Concurrent file analysis → efficient multi-language processing
- **Adversarial Validation**: Challenge findings → reduce false positives
- **Evidence-Based Suggestions**: Research-backed recommendations → credible improvements
- **Actionable Output**: Prioritized task lists → clear implementation path

## Examples

### Basic Usage
```
# Upload English source and translation files, then:
"Review"

# Or explicitly:
/sc:review-translation english.json de_DE.json fr_FR.json es_ES.json
```

### Deep Analysis Mode
```
/sc:review-translation source.json translations/*.json --depth deep --strict
# Enables additional checks:
# - Character limit validation
# - Exhaustive terminology consistency
# - Extended evidence search
```

### Steam Store Page Review
```
# Context: User uploads Steam store page localization files
"Review these Steam store translations"

# System infers:
# - Product Type: Video Game
# - Audience: Gamers
# - Use Case: Marketing (store page)
# - Tone: Engaging, persuasive, genre-appropriate
```

## Boundaries

**Will:**
- Perform comprehensive linguistic and cultural quality assessment
- Generate prioritized, actionable reports with evidence
- Implement confirmed fixes upon user request
- Search for real-world usage evidence to validate suggestions

**Will Not:**
- Proceed with review before user confirms context analysis
- Mark subjective preferences as critical errors
- Implement changes without explicit user consent
- Replace professional human translator review for high-stakes content

## CRITICAL BOUNDARIES

**MANDATORY CONFIRMATION GATE**

Phase 1 context analysis MUST receive user confirmation before any review work begins. This ensures:
- Correct tone/formality assessment
- Appropriate cultural context
- Accurate audience targeting
- Aligned evaluation criteria

**Output Artifacts:**
1. Individual language reports (`reports/localization/[lang]_review_*.md`)
2. Project summary (`reports/localization/PROJECT_SUMMARY_*.md`)
3. Implementation task list (embedded in summary)

**Next Step**: After review, user chooses to implement fixes, provide feedback, or skip implementation.
