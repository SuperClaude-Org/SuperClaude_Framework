# Reddit & Community Research: Claude Code Custom Commands, Agents, Skills & Plugins

**Research Date**: 2026-02-21
**Sources**: Reddit (r/ClaudeAI, r/ClaudeCode), community blogs, GitHub repositories
**Scope**: Best practices, tips, tricks, and examples for creating custom agents, skills, and slash commands for Claude Code

> **Note on methodology**: Reddit.com blocks direct programmatic access (both Anthropic's web crawler and curl/JSON API). Content was gathered via Tavily search snippets of Reddit threads, community blog posts that aggregate Reddit discussions, and the aitooldiscovery.com Reddit synthesis article. Where possible, original Reddit thread URLs are cited even when full thread content was inaccessible.

---

## Table of Contents

1. [Custom Slash Commands](#1-custom-slash-commands)
2. [Building Custom Agents & Subagents](#2-building-custom-agents--subagents)
3. [Creating Skills & SKILL.md](#3-creating-skills--skillmd)
4. [CLAUDE.md Best Practices & Prompt Engineering](#4-claudemd-best-practices--prompt-engineering)
5. [MCP Integration with Custom Commands](#5-mcp-integration-with-custom-commands)
6. [Complex Multi-Phase Commands & Orchestration](#6-complex-multi-phase-commands--orchestration)
7. [Hooks & Automation](#7-hooks--automation)
8. [Plugin System & Marketplace](#8-plugin-system--marketplace)
9. [SuperClaude Framework Discussions](#9-superclaude-framework-discussions)
10. [Community Tools & Resource Collections](#10-community-tools--resource-collections)

---

## 1. Custom Slash Commands

### Key Reddit Threads

- **[How are you using custom commands in Claude Code to...](https://www.reddit.com/r/ClaudeAI/comments/1las0z9/how_are_you_using_custom_commands_in_claude_code/)** (r/ClaudeAI)
  - Discussion on practical use cases for custom commands
  - Users share that markdown files in `.claude/commands/` each become a slash command (e.g., `architect.md` becomes `/architect`)

- **[Claude Command Suite - Professional slash commands](https://www.reddit.com/r/ClaudeAI/comments/1la4jrt/claude_command_suite/)** (r/ClaudeAI)
  - A developer shared a collection of professional slash commands providing structured workflows for common software development tasks

- **[Slash command manager for Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1ljnln4/slash_command_manager_for_claude_code/)** (r/ClaudeAI)
  - Addresses the problem of version management for slash commands -- knowing which version is installed and in use
  - Includes screenshots of a `/status` command showing installed command versions

- **[Claude Code can invoke your custom slash commands](https://www.reddit.com/r/ClaudeAI/comments/1noyvmq/claude_code_can_invoke_your_custom_slash_commands/)** (r/ClaudeAI)
  - Covers Claude Code v1.0.123 which added the SlashCommand tool enabling Claude to invoke user-defined slash commands programmatically

- **[Easiest way to automate adding custom /commands to Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1mpc26c/easiest_way_to_automate_adding_custom_commands_to/)** (r/ClaudeAI)
  - Guide: "Stop hand-coding slash commands -- grab this one file and let Claude make any command for you"

- **[Improving my CLAUDE.md by talking to Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1m0ah3h/improving_my_claudemd_by_talking_to_claude_code/)** (r/ClaudeAI)
  - User created a slash command that accepts arguments instead of a hook: "I did a similar thing but instead of a hook, I made a slash command that accepts arguments `/my actual prompt/`. Hooks run on every event."

### Core Patterns & Best Practices

**Two types of commands:**
- **Project Commands**: `.claude/commands/` -- project-specific, shareable via version control
- **Personal Commands**: `~/.claude/commands/` -- available across all projects, personal use only

**Creation pattern:**
```
.claude/commands/<command-name>.md
```
The filename becomes the slash command name. Write instructions in natural language. Use `$ARGUMENTS` for dynamic input.

**When to use custom commands (community consensus):**
- Commands that encode specific workflows you frequently use
- Prompts you find tedious to repeatedly re-enter
- NOT for short prompts you could simply retype
- Best for: commits, code reviews, branch management, multi-step workflows

**Community warning:** "If you add too many custom commands, you're adding a level of indirection that might confuse new developers on a project."

### Practical Examples from the Community

**1. Commit command** (`~/.claude/commands/commit.md`):
Reviews all local modifications relative to HEAD, checking for patterns like TODO, FIXME, HACK, commented-out code blocks, and debugging/test flags left enabled.

**2. Hugo blog management** (`.claude/commands/posts/new.md`):
Generates proper kebab-case filenames with today's date using verb-noun naming format.

**3. Language checking** (`.claude/commands/posts/check_language.md`):
Reviews files for UK English spelling, grammar/punctuation errors, and undefined acronyms.

**4. YouTube research agent** (`/youtube @channelname`):
Outputs a `youtube-research.md` file with a channel's top recent videos plus key insights.

**5. SEO workflow** (`/seo`):
Analyzes blog post, identifies keywords, generates semantic variants, looks up keyword volumes via API, then generates in-depth SEO analysis.

**6. Catchup command** (Shrivu Shankar):
Reads all uncommitted changes into context. Enables the pattern: `/clear` to free context, then `/catchup` to reload work-in-progress.

**7. Production-ready command collections** (wshobson/commands):
57 production-ready commands (15 workflows + 42 tools). Workflows invoked with directory prefixes like `/workflows:feature-development implement OAuth2` or `/tools:security-scan perform vulnerability assessment`.

### Evolution: Commands Merged into Skills

Custom slash commands have been merged into skills. A file at `.claude/commands/review.md` and a skill at `.claude/skills/review/SKILL.md` both create `/review` and work the same way. Existing `.claude/commands/` files keep working.

---

## 2. Building Custom Agents & Subagents

### Key Reddit Threads

- **[New to Claude Code. Please help me understand plugins, agents...](https://www.reddit.com/r/ClaudeCode/comments/1pj2udc/new_to_claude_code_please_help_me_understand/)** (r/ClaudeCode)
  - Users explain: "custom slash commands are basically shortcuts for things you normally prompt Claude Code to do"
  - Clear distinction between commands, agents, skills, and plugins

### What Are Subagents

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with:
- A custom system prompt
- Specific tool access
- Independent permissions

### Built-in Subagents

- **Explore**: Fast, read-only agent for searching and analyzing codebases
- **Plan**: Research agent for gathering context during plan mode
- **General-purpose**: For complex, multi-step tasks requiring both exploration and action

### How to Create Custom Subagents

Subagents are defined as Markdown files with YAML frontmatter. Create via:
1. The `/agents` command (interactive)
2. Manual file creation in `.claude/agents/` (project) or `~/.claude/agents/` (user-level)

**Template structure:**
```yaml
---
name: agent-name
description: What this agent does and when Claude should use it
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
model: sonnet
---

# Role Description
[Agent instructions here]

## Checklists
[Quality gates and verification steps]

## Communication Protocol
[How to report findings]
```

### Best Practices (Community Consensus)

**1. Tool permissions by role:**
- Read-only agents (reviewers, auditors): `Read, Grep, Glob`
- Research agents: `Read, Grep, Glob, WebFetch, WebSearch`
- Full agents: `Read, Write, Edit, Bash, Glob, Grep`

**2. Make agents opinionated:**
> "In your system prompt, it helps to instruct your agent to 'be honest' or 'be critical' or 'be realistic.' Many LLM system prompts default to an agreeable demeanor. Making subagents a little argumentative and opinionated will protect you from bad design decisions."

**3. Start small:**
> "In the beginning, you'll want to define and deploy your subagents one at a time. Get used to how they work. You'll probably max out at about 3 or 4 subagents total."

**4. Context window advantage:**
> "One important advantage of agents is that they have their own context window and can provide a summary after doing extensive research to the main agent. That way you can save precious time within the main agent before it has to 'compact'."

**5. Getting Claude to use subagents:**
Add instructions to CLAUDE.md reminding Claude about available subagents. Claude automatically summons the relevant agent based on task description matching.

**6. Pipeline architecture:**
> "Give them roles: Product Spec, Architect, Implementer/Tester, and chain them with Claude Code hooks to create a dependable software pipeline with reproducibility, separation of concerns, and governance & safety."

**7. Model selection for cost efficiency:**
> "Claude Haiku 4.5 delivers 90% of Sonnet 4.5's agentic coding performance at 2x speed and 3x cost savings ($1/$5 vs $3/$15). This makes Haiku 4.5 the optimal choice for lightweight agents requiring frequent invocation."

### Important Constraints

- Subagents cannot spawn other subagents (`Task(agent_type)` has no effect in subagent definitions)
- Programmatically defined agents take precedence over filesystem-based agents with the same name
- Each subagent counts toward your usage limits

### Community Resources

- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)**: 100+ specialized subagent templates
- **[Build with Claude Marketplace](https://www.buildwithclaude.com/)**: 400+ extensions
- **SubAgents.cc**: Template generator tool

---

## 3. Creating Skills & SKILL.md

### Key Reddit Threads

- **[Understanding CLAUDE.md vs Skills vs Slash Commands vs Plugins](https://www.reddit.com/r/ClaudeAI/comments/1ped515/understanding_claudemd_vs_skills_vs_slash/)** (r/ClaudeAI)
  - Definitive explanation of the differences:
  > "**Skills** are like better-structured CLAUDE.md files. They can be invoked by Claude automatically when relevant, or manually by the user with a slash. **Slash Commands** are similar -- they can be invoked manually by the user, or by Claude itself. The difference is the intention of the design -- skills are primarily designed for Claude to use, and slash commands are primarily designed for the user to use."

- **[Claude Code customization guide: CLAUDE.md, skills, subagents...](https://www.reddit.com/r/ClaudeCode/comments/1psdrtb/claude_code_customization_guide_claudemd_skills/)** (r/ClaudeCode)
  - Notes that slash commands now invoke via the Skill tool instead of the SlashCommand tool

### How Skills Work (Progressive Disclosure)

1. Claude scans for SKILL.md files and loads only their **names and descriptions**
2. When a request matches a skill's description, the **full instructions are loaded**
3. Claude only sees what it needs, when it needs it -- context efficient

### SKILL.md Structure

```yaml
---
name: skill-name
description: Brief description that Claude uses for matching
---

# Skill Instructions

[Full instructions Claude follows when the skill is activated]
```

### Skills vs. CLAUDE.md

| Aspect | CLAUDE.md | Skills |
|--------|-----------|--------|
| Loading | Every session | On-demand |
| Token cost | Always consumed | Only when activated |
| Best for | Universal project rules | Domain-specific knowledge |
| Activation | Always active | Context-matched or manual |

> "Skills are more token-efficient because Claude Code only loads them when needed. Putting everything in `~/.claude/CLAUDE.md` gets loaded into every conversation whether you need it or not."

### Best Practices

- **Clear descriptions**: Name and description appear in every interaction for matching
- **Focused purpose**: One skill should do one thing well
- **Concise instructions**: "More lines does not equal better instructions. Claude is smart enough to work with concise, well-structured guidance."
- **Under 500 lines**: Anthropic recommends keeping SKILL.md under 500 lines
- **Security awareness**: Skills can execute code on your machine -- only install from trusted sources

### The Skill Activation Problem

Skills that sit dormant because Claude does not realize they are relevant is a known frustration. One developer ran 200+ tests and found:
- Simple hook baseline: ~20% activation rate
- Forced eval hook: **84% activation rate** (perfect scores on 3 of 5 prompt types)

The "forced eval" approach requires a structured 3-step process: Evaluate, Activate, Implement.

> "The difference between the simple hook and the forced eval hook is the commitment mechanism. A simple passive instruction gets ignored, whereas the forced eval requires structured reasoning."

---

## 4. CLAUDE.md Best Practices & Prompt Engineering

### Key Reddit Threads

- **[Improving my CLAUDE.md by talking to Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1m0ah3h/improving_my_claudemd_by_talking_to_claude_code/)** (r/ClaudeAI)

### What to Include in CLAUDE.md

1. **Project context**: Tech stack, project structure, architecture decisions
2. **Code style preferences**: Specific formatting rules, not vague directives
3. **Commands**: How to run tests, build, lint, deploy (exact commands)
4. **Gotchas**: Project-specific warnings (e.g., "NEVER commit .env files")
5. **Personal preferences**: Your experience level and communication needs

### Critical Best Practices

**Keep it concise (~1K tokens, max 150 lines):**
> "LLMs bias towards instructions that are on the peripheries of the prompt... As instruction count increases, instruction-following quality decreases uniformly."

> "For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions."

**Use pointers, not copies:**
> "Don't include code snippets in these files if possible -- they will become out-of-date quickly. Instead, include file:line references to point Claude to the authoritative context."

**Use emphasis for critical rules:**
> "You can tune instructions by adding emphasis (e.g., 'IMPORTANT' or 'YOU MUST') to improve adherence."

**Treat it like code:**
> "Review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts."

**Do NOT use CLAUDE.md for linting rules:**
> "Never send an LLM to do a linter's job. LLMs are comparably expensive and incredibly slow compared to traditional linters and formatters."

### Prompt Engineering for Claude 4.x

**Be explicit -- Claude 4.x takes you literally:**
> "Earlier versions of Claude would infer your intent and expand on vague requests. Claude 4.x takes you literally and does exactly what you ask for, nothing more."

**Avoid over-engineering instructions:**
> "Claude Opus models have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested. Add specific guidance like 'Avoid over-engineering' and 'Keep solutions simple and focused.'"

**Extended Thinking is highly effective:**
> "Effectiveness rating: 10/10 for complex reasoning, 3/10 for simple queries."

**Explain the "why":**
> "Providing context or motivation behind your instructions can help Claude better understand your goals."

### File Location Hierarchy

Claude reads CLAUDE.md in order:
1. `~/.claude/CLAUDE.md` (global personal)
2. Project root `CLAUDE.md` (project-wide)
3. Subdirectory `CLAUDE.md` files (local overrides)

### Monorepo Approach (Reddit)

Multiple CLAUDE.md files: root for global rules, subfolders for local constraints. Users define sub-agent rules via CLAUDE.md to govern multi-agent behavior.

### Quick Start

The `/init` command generates a starter CLAUDE.md based on project structure and detected tech stack. Recommendation: use `/init` as a starting point and delete what you don't need.

**Save memories on the fly**: Prefix a message with `#` and Claude will offer to save that information to your CLAUDE.md.

### Boris Cherny (Creator of Claude Code) on CLAUDE.md

> "His team shares a single CLAUDE.md for the Claude Code repo, checked into git, with the whole team contributing multiple times a week. Anytime they see Claude do something incorrectly, they add it to the CLAUDE.md."

### Shrivu Shankar's Approach

> "He considers the root CLAUDE.md 'the single most important file in your codebase' and calls it 'the agent's constitution.' For professional work, his monorepo's CLAUDE.md is strictly maintained at 13KB."

### Iterative Improvement Pattern (Reddit)

> "He actively updates these files when Claude makes repeated mistakes. He adds guidelines with good and bad examples, describing it as 'iteratively training your own AI assistant.'"

---

## 5. MCP Integration with Custom Commands

### Core Architecture

MCP (Model Context Protocol) creates a universal connection layer between AI applications and external tools/data sources. Claude Code can simultaneously act as:
- **MCP Client**: Consuming other MCP servers you configure
- **MCP Server**: Exposing its tools (Bash, Read, Write, Edit, etc.) via `claude mcp serve`

### Building Custom MCP Servers

Three core primitives:
- **Tools**: Functions Claude can call (like API endpoints)
- **Resources**: Data Claude can read (documentation, schemas)
- **Prompts**: Templates for common operations

### Configuration

```json
// .mcp.json at project root
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["my-mcp-server"],
      "env": { "API_KEY": "${MY_API_KEY}" }
    }
  }
}
```

### Best Practices (Community)

**Token management is critical:**
> "Don't enable all MCPs at once. Each MCP tool description consumes tokens from your 200k window, potentially reducing it to ~70k."

**MCP Tool Search** enables lazy loading, reducing context usage by up to 95%.

**Naming convention**: `mcp__<server-name>__<tool-name>`

**Security**: Never hardcode secrets -- use environment variables. Sanitize inputs to prevent injection.

**Start small**: "Start with one tool that addresses your biggest context gap, then iterate from there."

### Workflow Examples

- Connect to ticket systems (JIRA/Linear) via MCP: Claude reads tickets, implements features, updates status, creates new tickets for bugs found
- GitHub MCP for reading issues, managing PRs, triggering CI/CD without leaving the terminal
- Sequential Thinking MCP for structured reasoning
- Playwright MCP for browser automation and testing

### Claude Code as MCP Server (Agent Orchestration)

Using `claude mcp serve`, Claude Code exposes its tools via MCP protocol. Other MCP clients (Claude Desktop, Cursor, Windsurf) can invoke Claude Code remotely.

> "The bigger trend is clear: AI tools calling other AI tools, each specializing in what it does best, composing through protocols like MCP."

---

## 6. Complex Multi-Phase Commands & Orchestration

### Key Community Patterns

**1. The AB Method (Ayoub Bensalah):**
A principled, spec-driven workflow that transforms large problems into focused, incremental missions using Claude Code's specialized subagents.

**2. RIPER Workflow (Tony Narlock):**
Structured development workflow enforcing separation between Research, Innovate, Plan, Execute, and Review phases.

**3. Agentic Workflow Patterns (ThibautMelen):**
Comprehensive collection covering:
- Subagent Orchestration
- Progressive Skills
- Parallel Tool Calling
- Master-Clone Architecture
- Wizard Workflows

**4. Four-Agent Split (Reddit):**
> "A non-technical person built a multi-agent orchestration system using Claude Code that cuts development time by 75%, splitting responsibilities across four specialized Claude Code agents, each running in separate VSCode terminals with distinct roles."

**5. External Orchestrator Pattern (Albert Sikkema):**
> "Subagents cannot spawn other subagents -- this is probably by design. The solution is to use an external LLM as the orchestrator, since it doesn't live inside Claude's context and can spawn Claude Code instances without violating nesting constraints."

### Production-Ready Orchestration

The wshobson/agents repository provides:
- 112 specialized AI agents
- 16 multi-agent workflow orchestrators
- 146 agent skills
- 79 development tools
- Organized into 72 focused, single-purpose plugins

Workflow pattern: Context --> Spec & Plan --> Implement, with interactive setup, track-based development, TDD workflow, and semantic revert capabilities.

### Claude-Flow Framework

Enterprise-grade multi-agent orchestration platform featuring:
- Distributed swarm intelligence
- RAG integration
- Native Claude Code support via MCP protocol
- Autonomous workflow coordination

### Multi-Agent tmux Pipelines (Reddit)

> "subagents let you organize AI like a startup team."

Example: parallel tmux panes running Claude Code + Codex CLI; one agent can consult the other for verification/delegation. CLAUDE.md rules govern how each agent behaves, preventing one agent from undoing another's work.

---

## 7. Hooks & Automation

### What Are Hooks

Hooks provide **deterministic** control over Claude Code's behavior, guaranteeing certain actions always happen.

> "If you tell Claude Code in your CLAUDE.md not to modify .env files, it will probably listen. If you set up a PreToolUse hook that blocks writes to .env files, it will always block them. For anyone working on production codebases, that distinction between 'probably' and 'always' is everything."

### Hook Types

| Type | Description |
|------|-------------|
| `command` | Runs a shell command (most common) |
| `prompt` | Single-turn Claude model evaluation |
| `agent` | Multi-turn verification with tool access |

### Hooks + Skills Together

> "The real win is conditional context loading. Instead of dumping everything in CLAUDE.md or letting skills sit dormant, hooks let you say 'only load this 10k token skill when working in these directories.' Team onboarding improves (guidelines load automatically), context stays lean (progressive disclosure), and token usage drops."

### Practical Hook Examples

- Auto-format code on save
- Run tests when test files change
- Type-check TypeScript after edits
- Block edits on the main branch
- Stop Event Hook: analyze edited files for high-risk patterns (error handling, async functions)
- Forced eval hook: analyze every prompt and suggest which skills Claude should activate

### Skills vs. Hooks Summary

> "Skills teach Claude how to code. Hooks enforce that it does. A skill says 'prefer for...of over .forEach()' -- but Claude can still forget. A hook catches it in real-time, warning or blocking before the code is written."

> "For context/tool selection, hooks + skills are the right pattern. For workflow orchestration, slash commands remain the better choice."

---

## 8. Plugin System & Marketplace

### Plugin Structure

Plugins bundle skills, slash commands, agents, hooks, and MCP servers into a single distributable unit.

```
my-plugin/
  .claude-plugin/
    plugin.json          # Only this goes inside .claude-plugin/
  skills/
    my-skill/
      SKILL.md
  commands/
    my-command.md
  agents/
    my-agent.md
```

**Common mistake**: Don't put commands/, agents/, skills/, or hooks/ inside the `.claude-plugin/` directory. Only `plugin.json` goes there.

### Key Community Quote

> "Simon Willison called Skills 'maybe a bigger deal than MCP.' Plugin marketplaces are already proliferating across GitHub."

### Claude Code's Superpowers Plugin (Reddit)

- **[Claude Code's Superpowers plugin actually delivers](https://www.reddit.com/r/ClaudeCode/comments/1r9y2ka/claude_codes_superpowers_plugin_actually_delivers/)** (r/ClaudeCode)
  - "Besides mostly write-plan and brainstorming slash commands I use occasionally, the customization of the stop hook has been [most valuable]"
  - Described as "a strong bundle of core competencies for software engineering with good coverage of the SDLC -- from planning, reviewing, testing, and debugging"

### Notable Plugins

- **Compound Engineering Plugin** (EveryInc): Turns past mistakes into lessons. Good documentation.
- **Context Engineering Kit** (Vlad Goncharov): Advanced context engineering techniques with minimal token footprint.
- **dx plugin** (ykdojo): Commands for `/dx:clone`, `/dx:half-clone`, `/dx:handoff`, `/dx:gha`, plus auto-invoked skills.
- **everything-claude-code** (Anthropic Hackathon winner): 912 tests, 98% coverage, 102 static analysis rules. Scans configurations for vulnerabilities.

### Token Efficiency of Skills vs. MCP

> "You can make dozens of Skills available without bloating your context window. Compare to MCP: GitHub's MCP alone consumes tens of thousands of tokens just describing its capabilities. Add several MCPs and you've burned most of your context before doing actual work."

---

## 9. SuperClaude Framework Discussions

No Reddit-specific threads were found discussing the SuperClaude Framework directly. The framework appears primarily on:

- **GitHub**: [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) (5.7K stars)
- **Official site**: [superclaude.org](https://superclaude.org/)
- **PyPI**: [superclaude package](https://pypi.org/project/superclaude/)

### Community Coverage

- **[Apidog review](https://apidog.com/blog/superclaude/)**: "SuperClaude: Power Up Your Claude Code Instantly"
- **[tenten.co article](https://developer.tenten.co/revolutionizing-development-with-superclaude-the-ultimate-claude-code-framework)**: "Revolutionizing Development with SuperClaude"
- **[Medium article](https://medium.com/@maxslashwang/a-tool-to-supercharge-claude-codes-power-many-times-over-7a43b149d704)**: "A Tool to Supercharge Claude Code's Power Many Times Over"

### Framework Description in Community

> "SuperClaude is a meta-programming configuration framework that transforms Claude Code into a structured development platform through behavioral instruction injection and component orchestration."

Latest version (v7.0.0) features: 35 Agents (16 Core + 12 Traits + 7 Extensions), 30 Skills, 14 Commands, 6 Modes, and Quality-Driven Loops.

---

## 10. Community Tools & Resource Collections

### Curated Collections

| Resource | Description | URL |
|----------|-------------|-----|
| awesome-claude-code | Curated list of skills, hooks, commands, agent orchestrators, plugins | [GitHub](https://github.com/hesreallyhim/awesome-claude-code) |
| awesome-claude-code-subagents | 100+ specialized subagent templates | [GitHub](https://github.com/VoltAgent/awesome-claude-code-subagents) |
| wshobson/commands | 57 production-ready slash commands | [GitHub](https://github.com/wshobson/commands) |
| wshobson/agents | 112 agents + 16 orchestrators + 146 skills | [GitHub](https://github.com/wshobson/agents) |
| claude-code-showcase | Complete project configuration example | [GitHub](https://github.com/ChrisWiles/claude-code-showcase) |
| everything-claude-code | Hackathon-winning config collection | [GitHub](https://github.com/affaan-m/everything-claude-code) |
| claude-code-tips | 45 tips from basics to advanced | [GitHub](https://github.com/ykdojo/claude-code-tips) |
| My-Claude-Code | Daily-use curated commands | [GitHub](https://github.com/vincenthopf/My-Claude-Code) |
| claude-code-system-prompts | All system prompts across 104 versions | [GitHub](https://github.com/Piebald-AI/claude-code-system-prompts) |
| claude-code-plugins-plus-skills | 270+ plugins with 739 agent skills | [GitHub](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) |

### Key Community Blogs

| Author | Focus | URL |
|--------|-------|-----|
| Scott Spence | Plugin marketplaces, skill activation reliability | [Blog](https://scottspence.com/posts/organising-claude-code-skills-into-plugin-marketplaces) |
| Shrivu Shankar | Using every Claude Code feature | [Blog](https://blog.sshh.io/p/how-i-use-every-claude-code-feature) |
| Alex Op | Full extensibility stack explained | [Blog](https://alexop.dev/posts/understanding-claude-code-full-stack/) |
| YK (Agentic Coding) | 32-45 tips from basics to advanced | [Substack](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to) |
| Builder.io | How to write a good CLAUDE.md | [Blog](https://www.builder.io/blog/claude-md-guide) |
| Harper Reed | Basic Claude Code setup | [Blog](https://harper.blog/2025/05/08/basic-claude-code/) |
| Arize | CLAUDE.md prompt optimization (5.19% accuracy boost) | [Blog](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/) |

### Reddit Subreddits

- **r/ClaudeAI**: General Claude discussions including Claude Code
- **r/ClaudeCode**: Dedicated to Claude Code (newer, growing)
- **r/ChatGPTCoding**: Cross-tool comparisons including Claude Code

---

## Key Takeaways for SuperClaude Development

### Commands/Skills Architecture

1. **Skills are the future** -- commands still work but skills offer progressive disclosure and auto-activation
2. **Forced eval hooks** dramatically improve skill activation (84% vs 20% baseline)
3. **Keep instructions concise** -- Claude works better with focused, well-structured guidance
4. **One skill = one purpose** -- follow the single responsibility principle

### Agent Design

1. **Make agents opinionated** -- override the default agreeable demeanor
2. **Start with 3-4 agents max** -- do not over-proliferate
3. **Use Haiku 4.5 for lightweight agents** -- 90% of Sonnet performance at 3x cost savings
4. **Subagents cannot spawn subagents** -- plan orchestration accordingly

### CLAUDE.md Strategy

1. **Keep it under 150 lines / ~1K tokens** for optimal instruction-following
2. **Use skills for domain knowledge** that does not apply to every session
3. **Treat it like code** -- review, prune, test changes
4. **Team-shared CLAUDE.md** at project root, committed to version control

### MCP Integration

1. **Do NOT enable all MCPs at once** -- each tool description consumes context tokens
2. **MCP Tool Search** enables lazy loading (95% token reduction)
3. **Custom MCP servers** offer the highest leverage for team-specific workflows
4. **Start with one tool** addressing your biggest context gap

### Orchestration Patterns

1. **External orchestrators** work around the "no nested subagents" limitation
2. **tmux multi-agent setups** with CLAUDE.md governance rules prevent conflicts
3. **Pipeline architecture** (Spec -> Architect -> Implement -> Test) with hook chaining
4. **The four-agent split** in separate terminals cuts development time by ~75% (per Reddit report)

---

## Source URLs

### Reddit Threads (Direct)

1. https://www.reddit.com/r/ClaudeAI/comments/1las0z9/how_are_you_using_custom_commands_in_claude_code/
2. https://www.reddit.com/r/ClaudeAI/comments/1la4jrt/claude_command_suite/
3. https://www.reddit.com/r/ClaudeAI/comments/1ljnln4/slash_command_manager_for_claude_code/
4. https://www.reddit.com/r/ClaudeAI/comments/1noyvmq/claude_code_can_invoke_your_custom_slash_commands/
5. https://www.reddit.com/r/ClaudeAI/comments/1mpc26c/easiest_way_to_automate_adding_custom_commands_to/
6. https://www.reddit.com/r/ClaudeAI/comments/1m0ah3h/improving_my_claudemd_by_talking_to_claude_code/
7. https://www.reddit.com/r/ClaudeAI/comments/1ped515/understanding_claudemd_vs_skills_vs_slash/
8. https://www.reddit.com/r/ClaudeCode/comments/1psdrtb/claude_code_customization_guide_claudemd_skills/
9. https://www.reddit.com/r/ClaudeCode/comments/1pj2udc/new_to_claude_code_please_help_me_understand/
10. https://www.reddit.com/r/ClaudeCode/comments/1r9y2ka/claude_codes_superpowers_plugin_actually_delivers/

### Community Sources (Reddit-Aggregating)

11. https://www.aitooldiscovery.com/guides/claude-code-reddit
12. https://www.oreateai.com/blog/claudemd-best-practices-reddit/3a29cdd605ebb2025681e71218021b5e
13. https://sjramblings.io/multi-agent-orchestration-claude-code-when-ai-teams-beat-solo-acts/

### Official Documentation

14. https://code.claude.com/docs/en/slash-commands
15. https://code.claude.com/docs/en/sub-agents
16. https://code.claude.com/docs/en/plugins
17. https://code.claude.com/docs/en/hooks-guide
18. https://code.claude.com/docs/en/mcp
19. https://code.claude.com/docs/en/best-practices
20. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

### Community Blogs & Guides

21. https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably
22. https://scottspence.com/posts/organising-claude-code-skills-into-plugin-marketplaces
23. https://blog.sshh.io/p/how-i-use-every-claude-code-feature
24. https://alexop.dev/posts/understanding-claude-code-full-stack/
25. https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/
26. https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to
27. https://www.builder.io/blog/claude-md-guide
28. https://www.builder.io/blog/claude-code
29. https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/
30. https://harper.blog/2025/05/08/basic-claude-code/

### GitHub Repositories

31. https://github.com/hesreallyhim/awesome-claude-code
32. https://github.com/VoltAgent/awesome-claude-code-subagents
33. https://github.com/wshobson/commands
34. https://github.com/wshobson/agents
35. https://github.com/ChrisWiles/claude-code-showcase
36. https://github.com/affaan-m/everything-claude-code
37. https://github.com/ykdojo/claude-code-tips
38. https://github.com/vincenthopf/My-Claude-Code
39. https://github.com/Piebald-AI/claude-code-system-prompts
40. https://github.com/jeremylongshore/claude-code-plugins-plus-skills
41. https://github.com/ruvnet/claude-flow
42. https://github.com/zhsama/claude-sub-agent
43. https://github.com/mbruhler/claude-orchestration
