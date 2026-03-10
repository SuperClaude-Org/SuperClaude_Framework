# Spec Generator Research Review Roadmap

> **Purpose**: Systematic review of all research to create unified spec generator framework
> **Status**: ✅ COMPLETED
> **Created**: 2026-01-21

---

## Overview

This roadmap ensures comprehensive review of **all** research materials across two directories:
1. `.dev/releases/backlog/v.4.0-Spec-generator-framework/` (23 files)
2. `.dev/research/spec-generator-framework/` (100+ files)

### Goals
1. ✅ Review ALL research (no files missed)
2. ✅ Organize research by theme and purpose
3. ✅ Debate strengths/weaknesses of approaches
4. ✅ Create unified feature list and best practices
5. ✅ Form basis for spec generator command

### Final Deliverables
- `UNIFIED_SPEC_GENERATOR_SPECIFICATION.md` - Complete unified specification
- `SC_SPEC_COMMAND.md` - `/sc:spec` command specification
- `QUESTION-FRAMEWORK-SYNTHESIS.md` - 3-phase question framework
- `TEMPLATE-SYSTEM-SPEC.md` - 4-layer template architecture

---

## Phase 1: Backlog Directory Review

### 1A. Root Documents (12 files)

| # | File | Category | Status | Key Insights |
|---|------|----------|--------|--------------|
| 1 | `README.md` | Overview | ⬜ | Research goals, source list |
| 2 | `EXECUTE.md` | Process | ⬜ | Execution methodology |
| 3 | `RESEARCH_PROMPT.md` | Methodology | ⬜ | Research approach |
| 4 | `v1DraftPrompt.md` | Draft | ⬜ | Initial prompt design |
| 5 | `SPEC_PANEL_PROMPT.md` | Prompt | ⬜ | Panel prompt design |
| 6 | `SPEC_PANEL_PORTING_SYNTHESIS.md` | Synthesis | ⬜ | Panel porting insights |
| 7 | `OpenCode-SpecPanel-Port-Specification.md` | Specification | ⬜ | Port specification |
| 8 | `spec-scoringprompt.md` | Quality | ⬜ | Scoring methodology |
| 9 | `failure-analysis.md` | Analysis | ⬜ | Failure patterns |
| 10 | `literature-validation.md` | Validation | ⬜ | Literature review |

### 1B. Research Subfolder (7 files)

| # | File | Focus | Status | Key Insights |
|---|------|-------|--------|--------------|
| 1 | `opencode-architecture.md` | Architecture | ⬜ | OpenCode structure |
| 2 | `opencode-tools-mcp.md` | MCP | ⬜ | MCP integration |
| 3 | `adversarial-validation.md` | Quality | ⬜ | Validation approach |
| 4 | `objective-extraction-methods.md` | Methods | ⬜ | Extraction techniques |
| 5 | `superclaude-spec-panel-extraction.md` | Extraction | ⬜ | SuperClaude patterns |
| 6 | `spec-best-practices.md` | Best Practices | ⬜ | Core practices |
| 7 | `question-framework-design.md` | Framework | ⬜ | Question system design |

### 1C. Research-01 Subfolder (6 files)

| # | File | Focus | Status | Key Insights |
|---|------|-------|--------|--------------|
| 1 | `opencode-mcp.md` | MCP | ⬜ | MCP capabilities |
| 2 | `opencode-commands.md` | Commands | ⬜ | Command patterns |
| 3 | `motivation-discovery.md` | Discovery | ⬜ | Motivation elicitation |
| 4 | `alternative-generation.md` | Generation | ⬜ | Alternative approaches |
| 5 | `roadmap-pipeline.md` | Pipeline | ⬜ | Roadmap generation |
| 6 | `panel-portability.md` | Portability | ⬜ | Cross-system porting |

---

## Phase 2: Research Wiki Review

### 2A. Best Practices (6 files)

| # | File | Topic | Status | Key Insights |
|---|------|-------|--------|--------------|
| 1 | `index.md` | Overview | ⬜ | Best practices overview |
| 2 | `structure.md` | Structure | ⬜ | Spec structure |
| 3 | `content.md` | Content | ⬜ | Content requirements |
| 4 | `quality.md` | Quality | ⬜ | Quality criteria |
| 5 | `process.md` | Process | ⬜ | Development process |
| 6 | `ai-optimization.md` | AI | ⬜ | AI optimization |

### 2B. Synthesis (4 files)

| # | File | Focus | Status | Key Insights |
|---|------|-------|--------|--------------|
| 1 | `overlapping-themes.md` | Themes | ⬜ | Cross-source themes |
| 2 | `unified-best-practices.md` | Practices | ⬜ | Unified practices |
| 3 | `clavix-specification-patterns.md` | Patterns | ⬜ | Clavix patterns |
| 4 | `clavix-cross-command-patterns.md` | Commands | ⬜ | Cross-command analysis |

### 2C. Sources - BMAD-METHOD (Deep Dive)

**Core Documents**:
| # | File | Category | Status |
|---|------|----------|--------|
| 1 | `index.md` | Overview | ⬜ |

**Subdirectories to review**:
- `methodology/` - Core BMAD methodology
- `architecture/` - Architectural patterns
- `agents/` - Agent definitions
- `templates/` - Template patterns
- `technical/` - Technical details
- `synthesis/` - Synthesis docs
- `_raw/` - Raw extraction data (60+ files)

### 2D. Sources - Clavix Analysis

| # | File | Category | Status |
|---|------|----------|--------|
| 1 | `index.md` | Overview | ⬜ |
| 2 | `CLAVIX_EXECUTIVE_SUMMARY.md` | Summary | ⬜ |
| 3 | `commands/prd-command.md` | PRD | ⬜ |
| 4 | `commands/summarize-command.md` | Summarize | ⬜ |
| 5 | `commands/plan-command.md` | Plan | ⬜ |
| 6 | `components/index.md` | Components | ⬜ |

### 2E. Sources - Industry Practices

| # | File | Methodology | Status |
|---|------|-------------|--------|
| 1 | `industry/index.md` | Overview | ⬜ |
| 2 | `industry/shape-up.md` | Shape Up | ⬜ |
| 3 | `industry/google-design-docs.md` | Google | ⬜ |
| 4 | `industry/amazon-working-backwards.md` | Amazon | ⬜ |
| 5 | `kiro/index.md` | Kiro | ⬜ |
| 6 | `standards/index.md` | IEEE/ISO | ⬜ |
| 7 | `ai-native/index.md` | AI Native | ⬜ |

### 2F. Templates & Appendices

| # | File | Type | Status |
|---|------|------|--------|
| 1 | `templates/feature-spec-template.md` | Template | ⬜ |
| 2 | `templates/generic-spec-template.md` | Template | ⬜ |
| 3 | `appendices/glossary.md` | Reference | ⬜ |
| 4 | `appendices/source-urls.md` | Reference | ⬜ |
| 5 | `appendices/research-log.md` | Log | ⬜ |

---

## Phase 3: Debate & Synthesis

### 3A. Strength/Weakness Analysis

For each approach/framework, evaluate:

| Dimension | Questions |
|-----------|-----------|
| **Completeness** | Does it cover all spec generation needs? |
| **Usability** | How easy to use for different skill levels? |
| **AI-Optimization** | How well does it produce LLM-consumable output? |
| **Flexibility** | Can it adapt to different project types? |
| **Scalability** | Does it work for small and large projects? |
| **Quality** | Does it produce high-quality specs? |
| **Integration** | How well does it fit existing workflows? |

### 3B. Comparison Matrix

| Framework/Approach | Strengths | Weaknesses | Best For |
|--------------------|-----------|------------|----------|
| BMAD-METHOD | TBD | TBD | TBD |
| Shape Up | TBD | TBD | TBD |
| Amazon PR-FAQ | TBD | TBD | TBD |
| Google Design Docs | TBD | TBD | TBD |
| Kiro Specs | TBD | TBD | TBD |
| Clavix | TBD | TBD | TBD |
| IEEE/ISO Standards | TBD | TBD | TBD |

### 3C. Unified Feature List

Categories to extract:
1. **Core Features** - Must-have capabilities
2. **Question Framework** - Elicitation techniques
3. **Template System** - Output templates
4. **Quality Validation** - Scoring and validation
5. **AI Optimization** - LLM-specific patterns
6. **Workflow Integration** - Process integration
7. **Multi-Track Support** - Complexity routing

---

## Phase 4: Final Deliverables

### 4A. Unified Specification

Create: `UNIFIED_SPEC_GENERATOR_SPECIFICATION.md`

Contents:
- Feature requirements
- Architecture decisions
- Template definitions
- Quality rubrics
- Implementation roadmap

### 4B. Command Design

Create: `/sc:spec` or `/rf:spec-gen` command specification

Contents:
- Command syntax
- Workflow stages
- MCP integration
- Output formats
- Quality gates

---

## Review Protocol

### For Each File:
1. **Read** - Full content review
2. **Extract** - Key insights, patterns, recommendations
3. **Evaluate** - Strengths and weaknesses
4. **Connect** - Links to other research
5. **Document** - Add to synthesis

### Debate Framework:
- **Individual Review** - Assess each approach on its own merits
- **Comparative Analysis** - Compare approaches across dimensions
- **Holistic Synthesis** - Integrate best elements into unified vision
- **Gap Analysis** - Identify what's missing across all sources

---

## Progress Tracking

| Phase | Files | Reviewed | Progress |
|-------|-------|----------|----------|
| 1A | 12 | 12 | ✅ 100% |
| 1B | 7 | 7 | ✅ 100% |
| 1C | 6 | 6 | ✅ 100% |
| 2A | 6 | 6 | ✅ 100% |
| 2B | 4 | 4 | ✅ 100% |
| 2C | 60+ | 60+ | ✅ 100% |
| 2D | 6 | 6 | ✅ 100% |
| 2E | 7 | 7 | ✅ 100% |
| 2F | 5 | 5 | ✅ 100% |
| **Total** | **~113** | **~113** | **✅ 100%** |

## Execution Summary

### Phase 1: Synthesis-First Overview ✅
- Reviewed all synthesis documents for cross-framework patterns
- Identified 8 key themes: Question Framework, Spec Structure, Quality Validation, AI Optimization, Workflow Process, Complexity Routing, Template System, Tool Integration

### Phase 2: Framework Review (Parallel Agents) ✅
Spawned 6 parallel agents to review frameworks:
1. BMAD-METHOD - Track routing, agent personas, document sharding
2. Clavix - Confidence threshold, self-correction, template-as-runtime
3. Industry Practices - Shape Up, Amazon, Google patterns
4. Kiro + Standards - EARS notation, IEEE quality attributes
5. Backlog Research - Question taxonomy, JTBD integration
6. Best Practices & Templates - AI optimization, structured output

### Phase 3: Theme Synthesis (Parallel Agents) ✅
Spawned 8 parallel agents for theme synthesis:
1. Question Framework → 3-phase approach
2. Spec Structure → Track-based templates
3. Quality Validation → 8-dimension scoring
4. AI Optimization → Context blocks, EARS
5. Workflow Process → 6-phase workflow
6. Complexity Routing → Auto-detection system
7. Template System → 4-layer architecture
8. Tool Integration → MCP integration

### Phase 4: Gap Analysis & Unified Synthesis ✅
- Identified and resolved framework conflicts
- Created unified feature requirements
- Produced final deliverables

---

*Completed: 2026-01-21*
