# Research Report: Skill Creator Alternatives

**Generated**: 2026-03-04
**Query**: GitHub repos and skill marketplaces for tools similar to Anthropic's skill-creator
**Depth**: Standard

---

## Executive Summary

The Claude Code skill creation ecosystem has exploded since Anthropic released the Agent Skills Open Standard in December 2025. There are **6 notable skill-creator/builder tools**, **3 curated awesome-lists**, **2 marketplace platforms** (one with 350K+ indexed skills), and **multiple skill collection repos**. The most directly comparable to Anthropic's skill-creator are obra/superpowers (TDD-based skill creation), FrancyJGLisboa/agent-skill-creator (autonomous end-to-end generation), and alirezarezvani/claude-code-skill-factory (template-driven factory). None match Anthropic's quantitative benchmarking + description optimization pipeline.

---

## 1. Skill Creation Tools (Direct Competitors)

### 1a. Anthropic skill-creator (Baseline)
- **Repo**: [anthropics/skills](https://github.com/anthropics/skills) → `skills/skill-creator/`
- **Approach**: Interview → Draft → Test with subagents (with-skill vs baseline) → Grade with assertions → Human review via HTML viewer → Iterate → Description optimization
- **Unique features**: Quantitative benchmarking (mean ± stddev), blind A/B comparison, automated description optimizer with train/test split, timing/token capture
- **Maturity**: Official Anthropic release, well-documented, includes eval-viewer, grader, comparator, and analyzer agents

### 1b. obra/superpowers — "writing-skills" meta-skill
- **Repo**: [obra/superpowers](https://github.com/obra/superpowers) (42K+ stars)
- **Approach**: TDD for skills — write pressure-test scenarios, watch subagents fail (RED), write skill, watch them pass (GREEN), refactor
- **Philosophy**: "If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing"
- **Unique features**: Automatic skill activation (no slash command needed), battle-tested with 20+ core skills, accepted into Anthropic's official plugin marketplace
- **Skill creation docs**: [writing-skills/SKILL.md](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)
- **Comparison**: More opinionated (TDD-only), less quantitative (no benchmark viewer), but deeply integrated into a proven workflow methodology
- **Also**: [superpowers-skills](https://github.com/obra/superpowers-skills) (community skills), [superpowers-lab](https://github.com/obra/superpowers-lab) (experimental)

### 1c. FrancyJGLisboa/agent-skill-creator
- **Repo**: [agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)
- **Approach**: Fully autonomous — "no spec writing, no prompt engineering, no coding required"
- **Pipeline**: UNDERSTAND (ingest sources) → BUILD (generate structure) → VERIFY (validate + security scan)
- **Unique features**: Accepts mixed inputs (text, links, code, PDFs, transcripts), auto platform detection, team skill registry (`skill_registry.py`), staleness detection, security scanning
- **Cross-platform**: Works with Claude Code, VS Code Copilot (1.108+), Cursor
- **Comparison**: Broader input acceptance and team sharing features than Anthropic's, but no quantitative eval loop

### 1d. alirezarezvani/claude-code-skill-factory
- **Repo**: [claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory) (v1.4.0)
- **Approach**: Template-driven factory with guided Q&A via coordinator agent routing to specialist guides
- **Pipeline**: Natural language intent → Coordinator routes to specialist → Guided Q&A → Validate → Install
- **Unique features**: Builds skills, agents, prompts, hooks, AND slash commands; Codex CLI bridge; ZIP packaging
- **Comparison**: Broadest artifact type coverage, but less focused on skill quality iteration

### 1e. metaskills/skill-builder
- **Repo**: [skill-builder](https://github.com/metaskills/skill-builder)
- **Approach**: Templates + reference docs, includes `converting-sub-agents-to-skills.md`
- **Maturity**: Minimal — appears to be a lightweight template collection
- **Comparison**: Much simpler than others, primarily documentation

### 1f. Jamie-BitFlight/claude_skills — plugin-creator
- **Repo**: [claude_skills](https://github.com/Jamie-BitFlight/claude_skills) (25 plugins)
- **Skill creation**: Includes `/plugin-creator` toolkit for creating/refactoring/validating plugins
- **Unique features**: `agentskill-kaizen` — analyzes session transcripts and generates skill patches (continuous improvement loop)
- **Comparison**: Plugin-centric (not pure skill), but kaizen concept is unique — auto-improvement from usage patterns

---

## 2. Skill Collection Repositories

| Repo | Skills | Focus |
|------|--------|-------|
| [levnikolaevich/claude-code-skills](https://github.com/levnikolaevich/claude-code-skills) | Full SDLC | Research → planning → implementation → testing → review → quality gates |
| [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | i18n, marketplace | Internationalization, localization setup and auditing |
| [abubakarsiddik31/claude-skills-collection](https://github.com/abubakarsiddik31/claude-skills-collection) | Curated | Official + community skills collection |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Real-world | Includes subagents and commands |
| [mhattingpete/claude-skills-marketplace](https://github.com/mhattingpete/claude-skills-marketplace) | Code execution | 90-99% token reduction for bulk ops |

---

## 3. Curated Lists (Awesome-Lists)

| Repo | Stars | Scope |
|------|-------|-------|
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 21.6K | Skills, hooks, slash-commands, agents, plugins |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | — | Skills-focused curation |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | — | Skills + resources + tools |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | — | 135 agents, 35 skills, 42 commands, 120 plugins |

---

## 4. Marketplaces & Directories

### 4a. SkillsMP.com
- **URL**: [skillsmp.com](https://skillsmp.com)
- **Scale**: 350,000+ indexed agent skills (as of March 2026)
- **Growth**: 66K (early Jan 2026) → 87K → 96K → 350K+
- **Features**: AI search, 12 categories, quality filtering (minimum 2 stars), GitHub sync
- **Compatible with**: Claude Code, Codex CLI, ChatGPT
- **Not affiliated with Anthropic** — independent community project

### 4b. obra/superpowers-marketplace
- **URL**: [superpowers-marketplace](https://github.com/obra/superpowers-marketplace)
- **Status**: Accepted into Anthropic's official plugin marketplace
- **Install**: `/plugin marketplace add obra/superpowers-marketplace`

### 4c. Anthropic Official
- **Repo**: [anthropics/skills](https://github.com/anthropics/skills)
- **Install**: `/plugin install document-skills@anthropic-agent-skills`
- **Status**: Official, includes partner skills (Box, Canva planned)
- **Open Standard**: Adopted by OpenAI for Codex CLI and ChatGPT (Dec 2025)

---

## 5. Slash Command Suites (Related but Distinct)

| Repo | Stars | Scope |
|------|-------|-------|
| [wshobson/commands](https://github.com/wshobson/commands) | 1.7K | Production-ready slash commands |
| [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite) | 904 | 216+ commands, 12 skills, 54 agents |
| [vincenthopf/My-Claude-Code](https://github.com/vincenthopf/My-Claude-Code) | — | Personal workflow commands |

---

## 6. Key Ecosystem Facts

- **Agent Skills Open Standard**: Released Dec 2025 by Anthropic, adopted by OpenAI for Codex CLI and ChatGPT
- **Cross-platform**: Skills in `~/.claude/skills/` are auto-discovered by Claude Code AND VS Code Copilot (1.108+)
- **Token efficiency**: Skill metadata scanning uses ~100 tokens; full skill loads at <5K tokens
- **Enterprise**: Anthropic working on organization-wide skill management and deployment

---

## 7. Feature Comparison Matrix

| Feature | Anthropic skill-creator | obra/superpowers | agent-skill-creator | skill-factory | Jamie plugin-creator |
|---------|------------------------|------------------|---------------------|---------------|---------------------|
| Guided interview | Yes | No (TDD-driven) | Autonomous | Q&A wizard | No |
| Test execution | Parallel subagents | TDD subagents | Verify phase | Validation cmd | No |
| Baseline comparison | With vs without | RED/GREEN | No | No | No |
| Quantitative benchmark | Yes (mean ± stddev) | No | No | No | No |
| Human review UI | HTML viewer | No | No | No | No |
| Description optimizer | Automated (5 iter) | No | No | No | No |
| Multi-input (PDF, links) | No | No | Yes | No | No |
| Team sharing | No | Plugin marketplace | Registry + repo | No | Marketplace |
| Security scanning | No | No | Yes | No | Yes |
| Continuous improvement | Manual iteration | No | Staleness detection | No | Kaizen (transcript analysis) |
| Cross-platform | Claude Code only | Claude Code | CC + VSCode + Cursor | CC + Codex | CC + Codex + Cursor |
| Builds agents too | No | No | No | Yes | Yes (plugins) |

---

## 8. Recommendations for SuperClaude

1. **Anthropic's skill-creator** remains the most rigorous for quality (quantitative benchmarks + description optimization). Already integrated via submodule.

2. **obra/superpowers writing-skills** offers the strongest *philosophy* — TDD for skills. Consider adopting its RED/GREEN testing approach.

3. **agent-skill-creator** has the broadest input acceptance (PDFs, transcripts, links) — useful for converting existing workflows to skills.

4. **skill-factory** is the only tool that also builds agents, hooks, and commands — relevant since SuperClaude has all these artifact types.

5. **Jamie's kaizen concept** (auto-improvement from session transcripts) is unique and could inform a post-deployment skill improvement workflow.

---

Sources:
- [anthropics/skills](https://github.com/anthropics/skills)
- [obra/superpowers](https://github.com/obra/superpowers)
- [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)
- [alirezarezvani/claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory)
- [metaskills/skill-builder](https://github.com/metaskills/skill-builder)
- [Jamie-BitFlight/claude_skills](https://github.com/Jamie-BitFlight/claude_skills)
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [SkillsMP.com](https://skillsmp.com)
- [Anthropic Skills Announcement](https://www.anthropic.com/news/skills)
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [SkillsMP Guide](https://smartscope.blog/en/blog/skillsmp-marketplace-guide/)
