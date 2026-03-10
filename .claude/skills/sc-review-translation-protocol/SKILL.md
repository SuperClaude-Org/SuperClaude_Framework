---
name: sc:review-translation-protocol
description: "Full behavioral protocol for sc:review-translation — systematic localization review with adversarial validation, real-world evidence search, and comprehensive quality scoring"
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---

# /sc:review-translation — Localization Review Protocol

## Triggers

sc:review-translation-protocol is invoked ONLY by the `sc:review-translation` command via `Skill sc:review-translation-protocol` in the `## Activation` section. It is never invoked directly by users.

Activation conditions:
- User runs `/sc:review-translation [source] [translations...]` in Claude Code
- Any `--strict`, `--depth`, `--tone-matrix`, `--platform`, `--export` flags are passed through

Do NOT invoke this skill directly. Use the `sc:review-translation` command.

## Phase 0: File Detection & Validation

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
- Placeholder patterns: {.*?}, \[.*?\], %[sd], \$\w+\$, <<.*?>>
- BBCode tags: h2, h1, b, i, u, list, *, img, url, quote, code
- HTML tags: br, p, span, div, a, strong, em

## Phase 1: Context Analysis (REQUIRED - Chain of Thought)

**CRITICAL**: Must complete with user confirmation before ANY review work begins.

1. Product Context Extraction:
   - Analyze source content for product type indicators
   - Identify industry markers (gaming, SaaS, e-commerce, etc.)
   - Detect brand voice signals (formal/casual, technical/accessible)
   - Identify platform context (Steam, console, mobile, web, enterprise)

2. Audience Inference (Structured Tree):
   - Primary Demographic
   - Regional Considerations
   - Purchase Intent Stage
   - Expected Familiarity

3. Use Case Classification:
   - Marketing copy (persuasive, emotional)
   - UI/UX text (clarity, brevity)
   - Legal/compliance (precision, formality)
   - Documentation (technical accuracy)
   - Entertainment/gaming (immersion, tone)
   - Store page (conversion-focused)

4. Tone Mapping (Per-Language):
   - Formality level (T-V distinction)
   - Humor/wordplay transferability
   - Cultural sensitivity requirements
   - Regional variant selection

5. Tone Calibration Matrix (if --tone-matrix):
   - Formality (1-5), Intensity (1-5), Localization Depth
   - Per-language expected deviation from source

Output: Context Summary for User Confirmation → STOP AND WAIT for user.

## Phase 2: Review Framework Definition

### Scoring KPIs (Weighted - 6 Dimensions)
1. Accuracy (25%): Semantic fidelity, no additions/omissions
2. Fluency (20%): Natural expression, grammar, idiomatic usage
3. Terminology (20%): Domain conventions, consistency
4. Tone Alignment (15%): Matches calibrated profile, register
5. Cultural Adaptation (10%): Localization vs translation appropriateness
6. Technical Compliance (10%): Placeholders, character limits, formatting

### Severity Classification
- 🔴 CRITICAL: Meaning reversal, offensive content, broken placeholders, legal violations
- 🟠 HIGH: Notable accuracy issues, comprehension-affecting grammar, terminology inconsistency
- 🟡 MEDIUM: Minor fluency issues, style inconsistencies, non-optimal word choices
- 🟢 LOW: Preference-based improvements, minor polish, alternative phrasings

### Grading Criteria
- ✅ PASS: Score ≥75 AND Critical = 0
- ⚠️ CONDITIONAL PASS: Score ≥70 AND Critical = 0 AND High ≤ 3
- ❌ FAIL: Score <70 OR Critical > 0

## Phase 2.5: Verification Scope Confirmation

Core Verification (Always Required):
- Full segment coverage, technical integrity, locale compliance
- Issue classification, actionable output with proposed fixes

Conditional Verification (Context-Based):
- Character/length limits, brand term consistency
- Marketing phrase impact, genre terminology, platform formatting

## Phase 3: Parallel Sub-Agent Deployment

Spawn parallel review agents (one per translation file):
- Agent ID: review-[language-code]
- Input: Source + target file + confirmed context + scoring framework
- Workflow: Full scan → automated validation → issue identification → severity → scoring → report

## Phase 4: Adversarial Validation (For Issues Found)

Trigger: When Critical or High Priority issues identified.

For each contested finding:
- Document original and proposed text
- Arguments for change (semantic accuracy, native norms, evidence)
- Arguments against change (intentional localization, cultural appropriateness)
- Resolution: CONFIRM CHANGE / KEEP ORIGINAL / FLAG FOR HUMAN REVIEW
- Confidence: HIGH / MEDIUM / LOW with justification

### Research Sub-Agent (Evidence Gathering)

Source Prioritization Hierarchy:
- Tier 1: Domain-authoritative (official publications, platform content)
- Tier 2: Industry sources (publications, competitor localizations)
- Tier 3: Community sources (forums, verified native speakers)
- Tier 4: General web (search results, MT comparisons)

Evidence Requirements:
- CRITICAL: Minimum 2 sources, prefer Tier 1-2
- HIGH: Minimum 2 sources from any tier
- Suggestions: 1+ sources acceptable

## Phase 5: Individual Report Generation

Per-language report with:
- Executive Summary (score, grade, issue counts)
- Critical Issues (with adversarial validation)
- High Priority Issues
- Score Breakdown (all 6 KPIs weighted)
- Tone Alignment Details (if --tone-matrix)
- Verification Scope Attestation
- Medium/Low issues in table format
- Validation Evidence with sources
- Adversarial Debate Records

## Phase 6: Project Summary Generation

Cross-language summary with:
- Localization Quality Matrix (all languages)
- Overall Statistics (pass/conditional/fail)
- Release Readiness assessment
- Aggregated Critical and High issues
- Implementation Task List with copy-paste JSON
- Post-implementation verification checklist

## Phase 7: User Prompt & Implementation Path

Options presented:
1. IMPLEMENT FIXES: Apply all critical/high fixes automatically
2. IMPLEMENT SPECIFIC LANGUAGE: Apply fixes for one language
3. REVIEW SPECIFIC ITEMS: Discuss findings in detail
4. PROVIDE FEEDBACK: Re-evaluate with user input
5. EXPORT FOR TEAM: Generate handoff package
6. SKIP IMPLEMENTATION: Keep reports only

## Special Handling Rules

### Variables and Placeholders
- Never modify content inside: {}, [], <>, %s, %d, %@, {{}}
- Preserve placeholder order when language requires reordering
- Flag any modified variable syntax

### Brand Terms and Terminology
- Product names: Keep source OR use official localized name
- Feature names: Check for official translations; default to source
- Made-up terms: Typically keep as source
- Maintain glossary; flag inconsistencies

### Platform-Specific Formatting
- Steam: BBCode preservation, flexible length
- PlayStation: HTML subset, strict character limits
- Mobile: Minimal formatting, character-limited UI
- Web: Standard HTML, moderate constraints
- Enterprise: Markdown or plain, formal register

### Length Sensitivity
- UI strings: WARN at 1.3x source, CRITICAL at 1.5x
- Marketing copy: Flexible, prioritize impact
- Character-limited: Strict enforcement if limits specified

## Error Recovery
- Analysis blocked: State what blocked, provide partials, specify needed info
- Partial completion: Document progress, save for resume
- Research unavailable: Note limitations, base on linguistic rules, mark as "Inferred"
