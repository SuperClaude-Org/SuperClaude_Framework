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
/sc:review-translation [source-file] [translation-files...] [flags]

Flags:
  --strict              Enable strict validation mode
  --depth [level]       quick|standard|deep (default: standard)
  --tone-matrix         Enable quantified tone calibration (optional)
  --platform [name]     steam|playstation|mobile|web|enterprise (default: auto-detect)
  --export              Generate team handoff format

# Implicit trigger - when source + translation files are provided:
"Review" | "Review these" | "Check translations" | "Validate localization"
```

---

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

Automated Technical Validation:
  placeholder_patterns: ["{.*?}", "\\[.*?\\]", "%[sd]", "\\$\\w+\\$", "<<.*?>>"]
  action: flag_if_modified

  formatting_preservation:
    bbcode_tags: ["h2", "h1", "b", "i", "u", "list", "*", "img", "url", "quote", "code"]
    html_tags: ["br", "p", "span", "div", "a", "strong", "em"]
    action: error_if_missing_or_modified
```

---

### Phase 1: Context Analysis (REQUIRED - Chain of Thought)

**CRITICAL**: This phase MUST complete with user confirmation before ANY review work begins.

```yaml
Chain of Thought Analysis:

  1. Product Context Extraction:
     - Analyze source content for product type indicators
     - Identify industry markers (gaming, SaaS, e-commerce, etc.)
     - Detect brand voice signals (formal/casual, technical/accessible)
     - Note domain-specific terminology
     - Identify platform context (Steam, console, mobile, web, enterprise)

  2. Audience Inference (Structured Tree):
     AUDIENCE ANALYSIS
     ├── Primary Demographic: [e.g., Core gamers 18-35, competitive FPS players]
     ├── Regional Considerations: [Platform popularity, genre reception by region]
     ├── Purchase Intent Stage: [Discovery, consideration, conversion]
     └── Expected Familiarity: [Genre conventions, gaming terminology]

  3. Use Case Classification:
     - Marketing copy (persuasive, emotional)
     - UI/UX text (clarity, brevity)
     - Legal/compliance (precision, formality)
     - Documentation (technical accuracy)
     - Entertainment/gaming (immersion, tone)
     - Store page (conversion-focused)

  4. Tone Mapping (Per-Language):
     - Formality level (T-V distinction languages)
     - Humor/wordplay transferability
     - Cultural sensitivity requirements
     - Regional variant selection (es-ES vs es-LA, pt-BR vs pt-PT, zh-CN vs zh-TW)

  5. Tone Calibration Matrix (if --tone-matrix enabled):
     Source Tone Profile:
       | Dimension | Score (1-5) | Calibration Example |
       |-----------|-------------|---------------------|
       | Formality | [1-5] | 1="Hey!", 3="Welcome", 5="We respectfully invite..." |
       | Intensity | [1-5] | 1="Try our game", 3="Experience adventure", 5="DOMINATE!" |
       | Localization Depth | Literal / Moderate / Adaptive | How much cultural adaptation |

     Per-Language Expected Deviation:
       - German: Formality +0.5, Intensity -1.0 (cultural norm)
       - Japanese: Formality +1.0, Intensity -1.5 (cultural norm)
       - Brazilian Portuguese: Formality -0.5, Intensity +0.5 (cultural norm)
       - [Language-specific calibration based on detected languages]

Output - Context Summary for User Confirmation:

═══════════════════════════════════════════════════════════════
CONTEXT ANALYSIS - AWAITING CONFIRMATION
═══════════════════════════════════════════════════════════════

PRODUCT IDENTIFIED:
[Product name and type]

CONTENT CLASSIFICATION:
[What the content is—store page, UI, etc.]

PLATFORM DETECTED:
[Steam/PlayStation/Mobile/Web/Enterprise]

TARGET AUDIENCE:
├── Primary: [Demographic and behavioral profile]
├── Regional: [Key regional considerations]
├── Intent Stage: [Discovery/Consideration/Conversion]
└── Familiarity: [Expected domain knowledge]

RECOMMENDED TONE PROFILE:
[Summary of tone calibration - qualitative or matrix if enabled]

LOCALIZATION APPROACH:
[Literal vs. adaptive recommendation with rationale]

KEY CONSIDERATIONS:
• [Consideration 1]
• [Consideration 2]
• [Consideration 3]

═══════════════════════════════════════════════════════════════
Please confirm this analysis is correct, or provide adjustments
before I proceed with the translation review.
═══════════════════════════════════════════════════════════════

STOP AND WAIT: Do not proceed until user confirms or provides corrections.
```

---

### Phase 2: Review Framework Definition

```yaml
Scoring KPIs (Weighted - 6 Dimensions):

  1. Accuracy (25%):
     - Semantic fidelity to source
     - No additions/omissions
     - Meaning preservation

  2. Fluency (20%):
     - Natural expression in target language
     - Grammar and syntax correctness
     - Idiomatic usage

  3. Terminology (20%):
     - Correct use of domain/genre conventions
     - Consistent terminology throughout
     - Industry-standard terms applied

  4. Tone Alignment (15%):
     - Matches calibrated tone profile
     - Appropriate register for audience
     - Brand voice consistency

  5. Cultural Adaptation (10%):
     - Appropriate localization vs translation
     - Cultural sensitivity
     - Regional appropriateness

  6. Technical Compliance (10%):
     - Placeholder preservation
     - Character limits (if applicable)
     - Format string validity
     - Markup/formatting preservation

Severity Classification:

  🔴 CRITICAL (Must Fix - Blocks Release):
     - Meaning reversal or significant distortion
     - Offensive or culturally inappropriate content
     - Broken placeholders/variables causing runtime errors
     - Legal/compliance violations
     - Missing critical content

  🟠 HIGH (Should Fix Before Release):
     - Notable accuracy issues
     - Grammar errors affecting comprehension
     - Inconsistent terminology for key terms
     - Tone significantly misaligned
     - Formatting issues affecting display

  🟡 MEDIUM (Professional Polish):
     - Minor fluency issues
     - Style inconsistencies
     - Non-optimal word choices
     - Minor formatting variations

  🟢 LOW (Suggestions/Enhancements):
     - Preference-based improvements
     - Minor polish opportunities
     - Alternative phrasings
     - Regional optimization suggestions

Grading Criteria (Three-Tier):
  ✅ PASS: Score ≥75 AND Critical Issues = 0
  ⚠️ CONDITIONAL PASS: Score ≥70 AND Critical = 0 AND High ≤ 3
  ❌ FAIL: Score <70 OR Critical Issues > 0
```

---

### Phase 2.5: Verification Scope Confirmation

**Thoroughness Verification Protocol** - Required before Phase 3 execution.

```yaml
Core Verification Scope (Always Required):
  □ Full segment coverage: All distinct text keys will be reviewed
  □ Technical integrity: Variables, placeholders, format strings validated
  □ Locale compliance: Numbers, dates, currencies, units checked
  □ Issue classification: All findings categorized by severity
  □ Actionable output: Proposed fixes provided for CRITICAL and HIGH

Conditional Verification (Enabled Based on Context):
  □ Character/length limits: [If UI constraints detected or specified]
  □ Brand term consistency: [If glossary/style guide provided]
  □ Marketing phrase impact: [If use case = marketing/store page]
  □ Genre-specific terminology: [If domain terminology detected]
  □ Platform formatting: [If platform-specific rules apply]

Attestation Output (Included in Phase 5 Reports):
  ┌─────────────────────────────────────────────────┐
  │ VERIFICATION SCOPE ATTESTATION                  │
  ├─────────────────────────────────────────────────┤
  │ ✅ Full segment coverage: [N]/[N] keys reviewed │
  │ ✅ Technical integrity: Placeholders validated  │
  │ ✅ Locale compliance: Format checks complete    │
  │ ✅ Issue classification: Applied                │
  │ ✅ Actionable output: Fixes provided            │
  │ ─────────────────────────────────────────────── │
  │ ⚪ Character limits: N/A (no limits specified)  │
  │ ✅ Brand terms: [N] terms validated             │
  │ ✅ Marketing phrases: [N] evaluated             │
  │ ⚪ Genre terminology: N/A (general content)     │
  └─────────────────────────────────────────────────┘
```

---

### Phase 3: Parallel Sub-Agent Deployment

```yaml
Orchestration Pattern:
  Spawn parallel review agents (one per translation file):

  Agent Configuration:
    - Agent ID: review-[language-code]
    - Input: Source file + Target translation file
    - Context: Confirmed context from Phase 1
    - Framework: Scoring KPIs from Phase 2
    - Verification: Scope from Phase 2.5

  Per-Agent Workflow:
    1. Full file scan with source comparison
    2. Apply automated validation checks (placeholders, formatting)
    3. Issue identification and classification
    4. Severity assignment per finding
    5. Score calculation per KPI
    6. Preliminary report generation

  Synchronization:
    - All agents complete before Phase 4
    - Aggregate findings for cross-language patterns
    - Identify systematic issues across translations
```

---

### Phase 4: Adversarial Validation (For Issues Found)

```yaml
Trigger: When Critical or High Priority issues are identified

Adversarial Debate Protocol (Structured Format):

  For each contested finding, document:

  ### Adversarial Validation: [Issue Summary]

  **Original:** "[current translation text]"
  **Proposed:** "[suggested change]"

  **For Change (Arguments):**
  • [Argument 1 - e.g., semantic accuracy]
  • [Argument 2 - e.g., native speaker norms]
  • [Evidence/source supporting change]

  **Against Change (Defense of Original):**
  • [Argument 1 - e.g., intentional localization]
  • [Argument 2 - e.g., cultural appropriateness]
  • [Evidence/source supporting original]

  **Resolution:** [CONFIRM CHANGE / KEEP ORIGINAL / FLAG FOR HUMAN REVIEW]
  **Confidence:** [HIGH / MEDIUM / LOW] - [Brief justification]

  Resolution Criteria:
    - Findings that survive challenge → Confirmed with HIGH confidence
    - Findings partially refuted → Downgraded severity or MEDIUM confidence
    - Findings fully refuted → Removed or marked LOW confidence
    - Ambiguous cases → Flagged for human review with rationale

Research Sub-Agent Activation (Evidence Gathering):

  Source Prioritization Hierarchy:
    Tier 1 - Domain-Authoritative:
      - Official publications from established brands in same domain
      - Platform-specific content (Steam store pages, App Store, enterprise docs)
      - Professional localization industry resources

    Tier 2 - Industry Sources:
      - Industry publications and news sites in target language
      - Established community hubs with editorial oversight
      - Competitor/peer product localizations

    Tier 3 - Community Sources:
      - User forums and discussion boards
      - Social media from verified native speakers
      - Wikis and collaborative resources

    Tier 4 - General Web:
      - General search results
      - Machine translation comparisons (baseline only)

    Note: Source quality within a tier can override tier ranking.

  Evidence Documentation Schema:
    For each validated suggestion:
      - URL: Direct link to source
      - Context: How phrase is used (e.g., "marketing headline", "in-game UI")
      - Domain Relevance: High / Medium / Low
      - Source Tier: 1-4 (per hierarchy)
      - Recency: Publication/observation date

    For limited evidence scenarios:
      - Document search terms and platforms attempted
      - Note: "Limited validation available"
      - Basis: Linguistic rules, parallel constructions, or native speaker consultation
      - Mark as "Inferred" rather than "Validated"

  Evidence Requirements:
    - CRITICAL issues: Minimum 2 sources, prefer Tier 1-2
    - HIGH issues: Minimum 2 sources from any tier
    - Suggestions: 1+ sources acceptable, document confidence
```

---

### Phase 5: Individual Report Generation

```yaml
Report Template Per Language:
  File: reports/localization/[language-code]_review_[timestamp].md

Structure:
```

```markdown
# [Language] Localization Review Report
## File: [filename] | Review Date: [YYYY-MM-DD]

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Score** | [XX]/100 |
| **Grade** | [✅ PASS / ⚠️ CONDITIONAL / ❌ FAIL] |
| **Critical Issues** | [N] |
| **High Priority** | [N] |
| **Medium Issues** | [N] |
| **Low Suggestions** | [N] |

### Grading Criteria
- ✅ PASS: Score ≥75 AND Critical = 0
- ⚠️ CONDITIONAL PASS: Score ≥70 AND Critical = 0 AND High ≤ 3
- ❌ FAIL: Score <70 OR Critical > 0

---

## Critical Issues (Immediate Action Required)

### Issue #1: [Brief Description]
| Field | Value |
|-------|-------|
| **Location** | Key: `[key_name]` |
| **Source** | "[original English text]" |
| **Current** | "[current translation]" |
| **Problem** | [Description of the issue] |
| **Severity** | 🔴 CRITICAL |
| **Proposed Fix** | "[suggested correction]" |

**Adversarial Validation:**
- For: [key argument supporting change]
- Against: [key argument for original]
- Resolution: CONFIRM CHANGE | Confidence: HIGH
- Evidence: [URL] - [context]

---

## High Priority Issues

[Same format as Critical, with 🟠 HIGH severity]

---

## Score Breakdown

| KPI | Score | Weight | Weighted | Notes |
|-----|-------|--------|----------|-------|
| Accuracy | [X]/100 | 25% | [X] | [Brief note] |
| Fluency | [X]/100 | 20% | [X] | |
| Terminology | [X]/100 | 20% | [X] | |
| Tone Alignment | [X]/100 | 15% | [X] | |
| Cultural Adaptation | [X]/100 | 10% | [X] | |
| Technical Compliance | [X]/100 | 10% | [X] | |
| **TOTAL** | | | **[X]/100** | |

### Tone Alignment Details (if --tone-matrix)
| Dimension | Source | Target | Expected Dev | Actual Dev | Status |
|-----------|--------|--------|--------------|------------|--------|
| Formality | [X] | [X] | [±X] | [±X] | ✅/⚠️/🔴 |
| Intensity | [X] | [X] | [±X] | [±X] | ✅/⚠️/🔴 |
| Localization | [Level] | [Level] | - | - | ✅/⚠️ |

---

## Verification Scope Attestation

| Check | Status | Details |
|-------|--------|---------|
| Full segment coverage | ✅ | [N]/[N] keys reviewed |
| Technical integrity | ✅ | All placeholders valid |
| Locale compliance | ✅ | Date/number formats OK |
| Issue classification | ✅ | Applied |
| Actionable output | ✅ | Fixes provided |
| Character limits | ⚪ | N/A (no limits specified) |
| Brand terms | ✅ | [N] terms validated |
| Marketing phrases | ✅ | [N] evaluated |

---

## Medium Priority Issues

| # | Key | Issue | Current → Proposed |
|---|-----|-------|-------------------|
| 1 | `key_name` | [Brief issue] | "[current]" → "[fix]" |

---

## Low Priority Suggestions

| # | Key | Suggestion | Rationale |
|---|-----|------------|-----------|
| 1 | `key_name` | "[alternative]" | [Why this might be better] |

---

## Validation Evidence

### Research Findings

| Suggestion | Evidence | Source Tier | Confidence |
|------------|----------|-------------|------------|
| "[phrase]" | [URL] - [context] | Tier [N] | HIGH/MED/LOW |

---

## Methodology Notes

[Any language-specific considerations applied, deviations from standard process, or special handling notes]

---

## Appendix: Adversarial Debate Records

[Full debate transcripts for all contested Critical/High items]
```

---

### Phase 6: Project Summary Generation

```yaml
Summary Report:
  File: reports/localization/PROJECT_SUMMARY_[timestamp].md
```

```markdown
# Localization Review - Project Summary
## [Project/Product Name]
### Review Completed: [YYYY-MM-DD]

---

## Localization Quality Matrix

| Language | Score | Grade | Accuracy | Fluency | Terminology | Tone | Cultural | Technical | Critical | High |
|----------|-------|-------|----------|---------|-------------|------|----------|-----------|----------|------|
| German | 85 | ✅ PASS | 88 | 82 | 85 | 83 | 80 | 95 | 0 | 2 |
| French | 72 | ⚠️ COND | 70 | 75 | 68 | 72 | 75 | 90 | 0 | 4 |
| Spanish | 91 | ✅ PASS | 92 | 90 | 90 | 88 | 92 | 95 | 0 | 1 |
| Japanese | 65 | ❌ FAIL | 60 | 70 | 62 | 68 | 65 | 85 | 1 | 3 |

---

## Overall Statistics

| Metric | Value |
|--------|-------|
| Total Languages | [N] |
| ✅ Passed | [N] ([%]) |
| ⚠️ Conditional | [N] ([%]) |
| ❌ Failed | [N] ([%]) |
| Average Score | [X]/100 |
| Total Critical Issues | [N] |
| Total High Priority | [N] |

---

## Release Readiness

- **Ready for Release:** [List of PASS languages]
- **Requires Minor Fixes:** [List of CONDITIONAL languages]
- **Blocked - Requires Fixes:** [List of FAIL languages with reasons]

---

## All Critical Issues (Aggregated)

| # | Language | Key | Issue | Proposed Fix | Evidence |
|---|----------|-----|-------|--------------|----------|
| 1 | Japanese | `key_x` | Meaning reversal | "[fix]" | [link] |
| 2 | [Lang] | `key_y` | Broken placeholder | "[fix]" | Automated |

---

## All High Priority Issues (Aggregated)

| # | Language | Key | Issue | Proposed Fix |
|---|----------|-----|-------|--------------|
| 1 | French | `key_a` | Grammar error | "[fix]" |
| 2 | German | `key_b` | Terminology | "[fix]" |

---

## Implementation Task List

### Pre-Implementation Checklist
- [ ] Backup all original translation files
- [ ] Confirm access to localization management system
- [ ] Identify responsible translator/reviewer for each language

### Critical Fixes (MUST COMPLETE)

#### Task 1: Japanese `key_x` - Meaning Reversal
**File:** `ja_JP.json`
**Key:** `"key_x"`

**Current Value:**
```json
"key_x": "[current incorrect text]"
```

**Replace With:**
```json
"key_x": "[corrected text]"
```

**Rationale:** [Brief explanation]
**Verification:** Confirm meaning matches source; run JSON lint

---

### High Priority Fixes (SHOULD COMPLETE)

[Same format as Critical]

---

### Implementation Commands (Copy-Paste Ready)

#### Japanese Changes
```json
{
  "key_x": "[new value]",
  "key_y": "[new value]"
}
```

#### French Changes
```json
{
  "key_a": "[new value]"
}
```

---

### Post-Implementation Verification
- [ ] All critical fixes applied
- [ ] All high priority fixes applied
- [ ] JSON syntax validated (run linter)
- [ ] Encoding verified (UTF-8)
- [ ] Visual review in context (if possible)
- [ ] Re-run QA check on modified files

---

## Individual Reports

| Language | File | Score | Grade | Link |
|----------|------|-------|-------|------|
| German | de_DE.json | 85 | ✅ PASS | [Report](./de_DE_review_[timestamp].md) |
| French | fr_FR.json | 72 | ⚠️ COND | [Report](./fr_FR_review_[timestamp].md) |
| Spanish | es_ES.json | 91 | ✅ PASS | [Report](./es_ES_review_[timestamp].md) |
| Japanese | ja_JP.json | 65 | ❌ FAIL | [Report](./ja_JP_review_[timestamp].md) |
```

---

### Phase 7: User Prompt & Implementation Path

```yaml
Completion Output:

═══════════════════════════════════════════════════════════════
LOCALIZATION REVIEW COMPLETE
═══════════════════════════════════════════════════════════════

SUMMARY:
• [N] languages reviewed
• [N] passed | [N] conditional | [N] failed
• [N] critical issues | [N] high priority issues

GENERATED REPORTS:
• PROJECT_SUMMARY_[timestamp].md
• [language]_review_[timestamp].md (×[N])

TASK LIST: [N] fixes documented with copy-paste JSON

═══════════════════════════════════════════════════════════════

OPTIONS:

1. IMPLEMENT FIXES
   "implement" or "apply fixes"
   → Apply all critical/high priority fixes automatically

2. IMPLEMENT SPECIFIC LANGUAGE
   "implement [language] fixes"
   → Apply fixes for specific language only

3. REVIEW SPECIFIC ITEMS
   "[language]" or "issue [#]"
   → Discuss specific findings in detail

4. PROVIDE FEEDBACK
   "feedback on [issue]"
   → Re-evaluate specific findings with your input

5. EXPORT FOR TEAM
   "export"
   → Generate formatted handoff package for localization team

6. SKIP IMPLEMENTATION
   "skip" or "done"
   → Keep reports only, no automated changes

═══════════════════════════════════════════════════════════════

Implementation Execution (if requested):
  1. Parse task list from PROJECT_SUMMARY
  2. Read target translation files
  3. Apply edits with validation:
     - Verify key exists
     - Confirm placeholder preservation
     - Validate JSON structure post-edit
  4. Generate change summary with diff
  5. Offer to create git commit with changes
```

---

## Special Handling Rules

### Variables and Placeholders
```yaml
protection_rules:
  - Never modify content inside: {}, [], <>, %s, %d, %@, {{}}
  - Preserve placeholder order when language requires reordering
  - Flag any translation that appears to have modified variable syntax
  - Automated validation catches: {.*?}, \[.*?\], %[sd@], \$\w+\$, <<.*?>>
```

### Brand Terms and Terminology
```yaml
brand_handling:
  product_name: Keep as source OR use official localized name if established
  feature_names: Check if official translations exist; default to source
  made_up_terms: Typically keep as source (e.g., "Sigma", "Grav-Sync")
  exception: Localize if standard practice for region (verify with research)

terminology_consistency:
  - Maintain glossary of key terms per project
  - Flag inconsistent usage within same file
  - Cross-reference with industry standard terminology
```

### Platform-Specific Formatting
```yaml
platforms:
  steam:
    formatting: bbcode
    preserve: [h1, h2, b, i, u, list, *, img, url, quote, code, hr]
    length_constraints: flexible (store pages)
    special: Preserve image references exactly

  playstation:
    formatting: html_subset
    preserve: [br, p, strong, em]
    length_constraints: strict (character limits common)

  mobile:
    formatting: minimal
    length_constraints: character_limited (UI elements)
    special: Consider text expansion for UI buttons

  web:
    formatting: html
    preserve: [standard HTML tags]
    length_constraints: moderate

  enterprise:
    formatting: markdown or plain
    length_constraints: flexible
    special: Maintain formal register
```

### Length Sensitivity
```yaml
length_rules:
  ui_strings:
    warning_threshold: 1.3x source length (30% expansion)
    critical_threshold: 1.5x source length
    action: Flag for review, suggest abbreviation

  marketing_copy:
    tolerance: Flexible, prioritize impact over length
    action: Note if significantly different but don't flag as error

  character_limited:
    enforce: Strict if limits specified
    action: Critical error if exceeded
```

---

## Error Recovery

```yaml
error_handling:
  analysis_blocked:
    - Clearly state what blocked completion
    - Provide partial results if available
    - Specify what additional information is needed
    - Do NOT generate placeholder or assumed content

  partial_completion:
    - Document which files/languages completed
    - Save progress to allow resume
    - List remaining items for next session

  research_unavailable:
    - Note: "Limited online validation available"
    - Base recommendation on linguistic rules
    - Mark confidence as "Inferred" not "Validated"
    - Suggest manual native speaker review
```

---

## Tool Coordination

- **Read**: Source and translation file parsing, JSON validation
- **Write**: Report generation (individual + summary)
- **Task**: Parallel sub-agent deployment for multi-file review
- **WebSearch/Tavily**: Real-world usage evidence search (Tier 1-4 sources)
- **TodoWrite**: Progress tracking across review phases
- **Edit**: Translation fix implementation
- **Bash**: JSON validation, git operations
- **Sequential**: Adversarial debate reasoning, complex analysis

---

## Key Patterns

- **Context-First Analysis**: Understand before judging → appropriate evaluation criteria
- **Verification Scope**: Explicit checklist → prevents systematic omissions
- **Parallel Review**: Concurrent file analysis → efficient multi-language processing
- **Adversarial Validation**: Structured challenge → reduces false positives
- **Evidence-Based Suggestions**: Tiered research → credible improvements
- **Actionable Output**: Prioritized task lists with copy-paste JSON → clear implementation path

---

## Examples

### Basic Usage
```
# Upload English source and translation files, then:
"Review"

# Or explicitly:
/sc:review-translation english.json de_DE.json fr_FR.json es_ES.json
```

### Deep Analysis with Tone Matrix
```
/sc:review-translation source.json translations/*.json --depth deep --tone-matrix
# Enables:
# - Quantified tone calibration with deviation tracking
# - Exhaustive terminology consistency
# - Extended evidence search
# - Full adversarial debate for all HIGH+ issues
```

### Platform-Specific Review
```
/sc:review-translation steam_page.json translations/*.json --platform steam --strict
# Enables:
# - BBCode preservation validation
# - Steam-specific formatting rules
# - Store page marketing optimization focus
```

### Team Export
```
/sc:review-translation source.json *.json --export
# After review, generates:
# - Team handoff package
# - Formatted task assignments
# - Copy-paste ready fixes
```

---

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
- Generate assumed content when analysis is blocked
- Modify protected elements (placeholders, brand terms) without explicit approval

---

## CRITICAL BOUNDARIES

**MANDATORY CONFIRMATION GATE**

Phase 1 context analysis MUST receive user confirmation before any review work begins. This ensures:
- Correct tone/formality assessment
- Appropriate cultural context
- Accurate audience targeting
- Aligned evaluation criteria
- Platform-specific rules applied

**Output Artifacts:**
1. Individual language reports (`reports/localization/[lang]_review_*.md`)
2. Project summary (`reports/localization/PROJECT_SUMMARY_*.md`)
3. Implementation task list (embedded in summary with copy-paste JSON)
4. Team export package (if `--export` flag used)

**Next Step**: After review, user chooses to implement fixes, provide feedback, export for team, or skip implementation.
