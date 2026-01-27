# Spec Generator Framework Research: Execution Guide

## Quick Start

Execute this research in 3 phases:

---

## Phase 0: Source Discovery (5 min)

First, discover additional authoritative sources beyond the mandatory ones:

```
/sc:research "specification best practices software engineering AI LLM 2024 2025" --depth exhaustive
```

**Expected Output**: List of 5+ additional sources with URLs to add to the research.

---

## Phase 1: Parallel Deep Dives (spawn 6 agents)

Execute ALL of these in a SINGLE message to run in parallel:

```
/sc:spawn --parallel "
AGENT_GROUP: spec-framework-research

AGENT_1: bmad-method-analyzer
TASK: Analyze BMAD-METHOD repository at https://github.com/bmad-code-org/BMAD-METHOD/tree/v6.0.0-alpha.15
- Clone repository at v6.0.0-alpha.15 tag
- Create manifest of EVERY file with path and purpose
- Analyze ALL .md files for concepts, templates, workflows
- Extract agent/persona definitions
- Document quality gates and validation patterns
- VERIFICATION: Count all files, confirm 100% analyzed
OUTPUT: .dev/research/spec-generator-framework/sources/bmad-method/

AGENT_2: spec-kitchen-analyzer
TASK: Analyze GitHub Spec Kitchen at https://github.com/github/spec-kitchen
- Fetch repository main branch
- Create complete file manifest
- Extract GitHub's specification patterns
- Document templates and automation
OUTPUT: .dev/research/spec-generator-framework/sources/spec-kitchen/

AGENT_3: kiro-docs-analyzer
TASK: Analyze Kiro specification documentation
- Crawl https://kiro.dev/docs/specs/concepts/
- Crawl https://kiro.dev/docs/specs/correctness/
- Crawl https://kiro.dev/docs/specs/best-practices/
- Index ALL linked pages from these roots
- Extract concepts, correctness criteria, best practices
OUTPUT: .dev/research/spec-generator-framework/sources/kiro/

AGENT_4: standards-researcher
TASK: Research formal specification standards
- IEEE 830 / ISO 29148 (SRS standards)
- RFC 2119 (requirement keywords MUST/SHOULD/MAY)
- Extract applicable principles for AI-consumed specs
OUTPUT: .dev/research/spec-generator-framework/sources/standards/

AGENT_5: industry-practices-researcher
TASK: Research industry specification methodologies
- Shape Up (Basecamp) - pitches and appetites
- Amazon Working Backwards / PR-FAQ
- Google Design Docs
- Microsoft Spec Templates
- Extract templates and what makes each effective
OUTPUT: .dev/research/spec-generator-framework/sources/industry/

AGENT_6: ai-native-researcher
TASK: Research AI-native specification patterns
- Anthropic prompt engineering guides
- OpenAI structured output documentation
- Cursor Rules / CLAUDE.md patterns
- Windsurf/Codeium spec patterns
- Extract patterns that improve AI comprehension
OUTPUT: .dev/research/spec-generator-framework/sources/ai-native/
"
```

**Verification**: Each agent must confirm file/page counts and 100% coverage.

---

## Phase 2: Synthesis (after Phase 1 complete)

```
/sc:spawn "
AGENT: synthesizer
WAIT_FOR: All Phase 1 agents complete

TASK: Synthesize all source analyses into unified best practices
INPUTS: All files in .dev/research/spec-generator-framework/sources/*/

REQUIREMENTS:
1. Read ALL source analysis documents completely
2. Identify themes that appear in 2+ sources (overlapping)
3. Identify unique insights from each source
4. Identify and resolve any contradictions
5. Create unified best practices organized by:
   - STRUCTURE: What sections a spec needs
   - CONTENT: What each section should contain
   - QUALITY: How to validate spec quality
   - PROCESS: How to develop specs iteratively
   - AI-OPTIMIZATION: How to make specs AI-consumable

OUTPUT: .dev/research/spec-generator-framework/synthesis/
  - overlapping-themes.md
  - unique-contributions.md
  - contradictions-resolved.md
  - unified-best-practices.md
"
```

---

## Phase 3: Wiki Assembly (after Phase 2 complete)

```
/sc:spawn "
AGENT: wiki-assembler
WAIT_FOR: synthesizer complete

TASK: Assemble final wiki with index and executive summary
INPUTS: All files in .dev/research/spec-generator-framework/

REQUIREMENTS:
1. Create README.md with complete navigation
2. Create EXECUTIVE_SUMMARY.md with key findings
3. Create glossary.md with unified terminology
4. Create source-urls.md with all indexed sources
5. Verify all cross-references work
6. Generate research-log.md with execution summary

OUTPUT: .dev/research/spec-generator-framework/
  - README.md
  - EXECUTIVE_SUMMARY.md
  - appendices/glossary.md
  - appendices/source-urls.md
  - appendices/research-log.md
"
```

---

## Verification Checklist

After all phases complete, verify:

### Coverage
- [ ] BMAD-METHOD: 100% files analyzed (count in manifest)
- [ ] Spec Kitchen: 100% files analyzed
- [ ] Kiro: All /docs/specs/* pages indexed
- [ ] Standards: IEEE 830, ISO 29148, RFC 2119 covered
- [ ] Industry: 4+ methodologies documented
- [ ] AI-Native: 4+ AI tools/patterns documented

### Synthesis Quality
- [ ] 20+ overlapping themes identified
- [ ] 50+ best practices extracted
- [ ] 10+ templates documented
- [ ] 20+ anti-patterns identified
- [ ] All contradictions resolved with rationale

### Wiki Completeness
- [ ] README.md with full navigation
- [ ] EXECUTIVE_SUMMARY.md with key findings
- [ ] All source directories populated
- [ ] All cross-references valid
