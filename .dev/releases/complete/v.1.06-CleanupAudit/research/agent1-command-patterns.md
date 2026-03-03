# SuperClaude Command Pattern Analysis

**Generated**: 2026-02-19
**Source**: 11 command files + 1 skill file analyzed
**Commands analyzed**: analyze, cleanup, spawn, task, implement, research, build, reflect, test, sc (dispatcher)
**Skill analyzed**: confidence-check/SKILL.md

---

## Section A: Pattern Ruleset

A numbered list of every structural and behavioral rule that ALL well-formed commands follow.

### Frontmatter Rules

1. **Every command file MUST begin with YAML frontmatter** delimited by `---` on its own line, before and after the metadata block.

2. **Frontmatter MUST include these fields in this order**:
   - `name`: lowercase, single-word command name (e.g., `analyze`, `cleanup`, `spawn`)
   - `description`: quoted string, one-sentence description starting with a verb or noun phrase
   - `category`: one of `utility`, `workflow`, `special`, `command` (inconsistency exists -- see Best Practices)
   - `complexity`: one of `basic`, `standard`, `enhanced`, `advanced`, `high`
   - `mcp-servers`: YAML array of MCP server names in lowercase (e.g., `[sequential, context7]`), empty array `[]` if none
   - `personas`: YAML array of persona names in lowercase (e.g., `[architect, quality, security]`), empty array `[]` if none

3. **The `sc.md` dispatcher is an exception** -- it uses minimal frontmatter with only `name` and `description`.

4. **Skill files use a simpler frontmatter** with only `name` and `description` (no category, complexity, mcp-servers, or personas fields).

### Header Rules

5. **The first H1 heading MUST follow the pattern**: `# /sc:<name> - <Short Title>` where `<name>` matches the frontmatter `name` field and `<Short Title>` is a 2-5 word descriptive title.

6. **Some commands include an optional context note** as a blockquote immediately after H1: `> **Context Framework Note**: ...`. This appears in `implement` and `research` but NOT in most commands. It is optional.

### Section Ordering Rules

7. **Commands MUST follow this canonical section order** (with some sections being optional):
   1. Frontmatter (`---` block)
   2. H1 Title (`# /sc:<name> - <Title>`)
   3. Optional: Context Framework Note (blockquote)
   4. `## Triggers` -- when the command activates
   5. `## Usage` or `## Context Trigger Pattern` -- invocation syntax
   6. `## Behavioral Flow` -- numbered step sequence
   7. `## MCP Integration` -- MCP server details (if `mcp-servers` is non-empty)
   8. `## Tool Coordination` -- native tool usage
   9. `## Key Patterns` -- domain-specific patterns
   10. `## Examples` -- usage examples with code blocks
   11. `## Boundaries` -- Will/Will Not constraints
   12. Optional: `## CRITICAL BOUNDARIES` -- hard stop rules
   13. Optional: Additional domain-specific sections (e.g., `## AUTO-FIX VS APPROVAL-REQUIRED`)

8. **The `## Triggers` section MUST contain 3-5 bullet points** describing activation conditions. Each bullet starts with a noun phrase describing the scenario.

9. **The `## Usage` section MUST contain a fenced code block** showing the command invocation pattern: `/sc:<name> [positional-args] [--flag-options]`.

### Behavioral Flow Rules

10. **The `## Behavioral Flow` section MUST contain exactly 5 numbered steps**. Every analyzed command uses exactly 5 steps.

11. **Each behavioral flow step MUST follow the format**: `N. **VerbWord**: Description sentence` where VerbWord is a single capitalized action verb (e.g., Analyze, Plan, Execute, Validate, Report).

12. **The 5-step flow MUST follow this general arc**:
    - Step 1: Analyze/Discover/Understand (assessment phase)
    - Step 2: Plan/Validate/Decompose (preparation phase)
    - Step 3: Execute/Generate/Orchestrate (action phase)
    - Step 4: Validate/Analyze/Monitor (verification phase)
    - Step 5: Report/Integrate/Optimize (output phase)

13. **After the 5 numbered steps, a `Key behaviors:` subsection MUST follow** with 3-5 bullet points summarizing the command's distinctive behavioral characteristics.

### MCP Integration Rules

14. **The `## MCP Integration` section is REQUIRED if `mcp-servers` in frontmatter is non-empty**. If `mcp-servers: []`, the section may be omitted or replaced with a note about native-only operation.

15. **Each MCP server listed in frontmatter MUST have a corresponding bullet** in the MCP Integration section using the format: `- **<ServerName> MCP**: <Purpose description>`.

16. **MCP server references use consistent naming**: `Sequential MCP`, `Context7 MCP`, `Magic MCP`, `Playwright MCP`, `Serena MCP`, `Tavily`, `Morphllm MCP`.

### Tool Coordination Rules

17. **The `## Tool Coordination` section MUST list tools as bold-prefixed bullets** in the format: `- **ToolName**: Purpose description`.

18. **Tools MUST be grouped logically**, with related tools combined: `Read/Grep/Glob` for analysis, `Edit/MultiEdit` for modification, `Write` for generation, `Bash` for execution, `TodoWrite` for tracking, `Task` for delegation.

19. **TodoWrite is referenced in commands with complexity >= `standard`** that involve multi-step or multi-file operations.

20. **Task tool (sub-agent delegation) is referenced when a command may need to spawn sub-agents** for large-scale operations. It appears in `cleanup`, `implement`, and `task` commands.

### Key Patterns Rules

21. **The `## Key Patterns` section MUST contain 3-5 bullet points** using a consistent arrow notation format: `- **Pattern Name**: Input/trigger → transformation → output/result`.

22. **Pattern names use Title Case** and are 2-3 words descriptive of the pattern type.

### Examples Rules

23. **The `## Examples` section MUST contain 3-4 examples** as H3 subsections, each with a descriptive title.

24. **Each example MUST contain a fenced code block** showing the command invocation, followed by comment lines (`#`) explaining what happens.

25. **Examples progress from simple to complex**: first example is basic usage, last example is advanced/specialized usage.

### Boundaries Rules

26. **The `## Boundaries` section MUST contain two subsections**: `**Will:**` and `**Will Not:**`, each with exactly 3 bullet points.

27. **Will bullets describe positive capabilities** using verbs: "Perform", "Provide", "Execute", "Generate", "Apply", "Implement".

28. **Will Not bullets describe negative constraints** using verbs: "Modify", "Override", "Execute", "Make", "Install", "Replace", "Operate".

29. **Some commands include a `## CRITICAL BOUNDARIES` section** that defines hard-stop rules. This section uses bold uppercase headers and includes:
    - A bold directive statement (e.g., `**STOP AFTER TASK DECOMPOSITION**`)
    - An `**Explicitly Will NOT**:` list
    - An `**Output**:` specification
    - A `**Next Step**:` recommendation pointing to other `/sc:*` commands

### Output Specification Rules

30. **Commands with `## CRITICAL BOUNDARIES` MUST define their output format** under `**Output**:` as a colon-list describing what the command produces.

31. **Commands MUST specify a `**Next Step**:` recommendation** suggesting which `/sc:*` commands to use after completion (e.g., "use `/sc:test` to run tests, then `/sc:git` to commit").

### Argument Pattern Rules

32. **Positional arguments use `[brackets]`** to indicate optional positional parameters: `[target]`, `[query]`, `[action]`.

33. **Flag arguments use `--double-dash` notation** with pipe-separated options: `--type unit|integration|e2e|all`, `--depth quick|deep`.

34. **Boolean flags use `--flag-name` without values**: `--safe`, `--clean`, `--verbose`, `--interactive`, `--parallel`, `--delegate`.

35. **Common flag patterns recur across commands**:
    - `--type` for operation variant selection
    - `--depth` or `--strategy` for execution intensity
    - `--format` for output format selection
    - `--safe` / `--aggressive` for safety level
    - `--with-tests` for test integration
    - `--parallel` / `--delegate` for orchestration control

### Consistency Rules

36. **All section headers use `##` (H2) level** for primary sections; `###` (H3) is used only within Examples and for subsections within Behavioral Flow.

37. **Bold text is used for emphasis** on key terms within bullets, not italic or ALL-CAPS (except in CRITICAL BOUNDARIES).

38. **Code blocks use triple-backtick fencing** without language specifier for command examples within the Usage and Examples sections.

39. **Persona names in frontmatter use kebab-case**: `qa-specialist`, `devops-engineer`, `deep-research-agent`, `project-manager`.

40. **MCP server names in frontmatter use lowercase single words**: `sequential`, `context7`, `magic`, `playwright`, `serena`, `tavily`, `morphllm`.

---

## Section B: Best Practices Guide

Best practices derived from analyzing what makes the most effective commands work well.

### 1. Frontmatter Precision

**Do**: Declare every MCP server and persona the command actually uses. This enables tooling, documentation generation, and the orchestration system to make informed routing decisions.

**Do not**: Leave `mcp-servers: []` and `personas: []` when the command uses MCP servers or personas in its behavioral flow. The `analyze` command currently has empty arrays despite referencing pattern analysis -- this is a consistency gap. If a command truly uses no MCP servers, state it explicitly in the MCP Integration section (as `spawn` does with "Native Orchestration").

**Best**: Match frontmatter arrays 1:1 with MCP Integration and persona references in the body text.

### 2. The 5-Step Behavioral Flow

The strongest commands (cleanup, implement, task) use exactly 5 steps with single-verb bold labels. This creates a scannable, predictable cognitive pattern.

**Best practice pattern**:
- Step 1: Assessment verb (Analyze, Discover, Understand)
- Step 2: Preparation verb (Plan, Validate, Configure, Decompose)
- Step 3: Execution verb (Execute, Generate, Orchestrate, Coordinate)
- Step 4: Verification verb (Validate, Analyze, Monitor)
- Step 5: Output verb (Report, Integrate, Optimize, Package, Document)

**Anti-pattern**: Combining two actions in one step or having more than 5 steps. The `research` command uses 6 sub-headed steps -- this is the only deviation and it works because research is inherently more complex, but the standard should be 5.

### 3. MCP Integration Specificity

The best commands (task, implement, research) describe not just WHICH MCP server is used but WHEN and WHY it activates.

**Good**: `- **Context7 MCP**: Framework patterns and official documentation for React, Vue, Angular, Express`
**Better**: `- **Playwright MCP**: Auto-activated for --type e2e browser testing` (includes activation trigger)
**Best**: `- **Sequential MCP**: Auto-activated for complex multi-step cleanup analysis and planning` (includes both trigger and purpose)

### 4. Tool Grouping Strategy

Group tools by operation category rather than listing them alphabetically:
- **Discovery tools**: `Read/Grep/Glob` -- always grouped together for analysis
- **Modification tools**: `Edit/MultiEdit` -- grouped for code changes
- **Generation tools**: `Write` -- for creating new content
- **Execution tools**: `Bash` -- for running external processes
- **Orchestration tools**: `TodoWrite`, `Task` -- for tracking and delegation

This grouping appears consistently in the best commands and aids scannability.

### 5. Boundary Symmetry

The most effective boundary sections maintain symmetry: each "Will" statement has a corresponding implicit "Will Not" constraint, and vice versa. The `cleanup` command excels here by adding a third section (`## AUTO-FIX VS APPROVAL-REQUIRED`) that disambiguates the grey area between auto-fix and approval-required operations.

**Best practice**: For any command that modifies files, add an explicit safety threshold section defining what gets auto-applied vs. what requires user approval.

### 6. Critical Boundaries for Scope-Limited Commands

Commands that produce output but do NOT implement (spawn, research) benefit greatly from a `## CRITICAL BOUNDARIES` section with:
- A bold stop directive
- An explicit "Will NOT" list
- A defined output format
- A next-step recommendation

This prevents scope creep where Claude might try to implement findings from a research command or execute tasks from a spawn decomposition.

### 7. Example Progression

The best example sections follow a clear progression:
1. **Bare minimum invocation** -- just the command with no flags
2. **Focused single-flag usage** -- one key flag demonstrated
3. **Combined flags** -- two or more flags showing interaction
4. **Advanced/specialized usage** -- edge case or power-user scenario

Each example should be self-contained: a code block with the invocation, followed by 1-3 comment lines explaining the behavior.

### 8. Next-Step Chaining

The strongest commands end with explicit next-step recommendations that chain to other `/sc:*` commands. This creates a workflow pipeline:
- `/sc:analyze` -> `/sc:improve` or `/sc:cleanup`
- `/sc:implement` -> `/sc:test` -> `/sc:git`
- `/sc:research` -> `/sc:design` or `/sc:implement`
- `/sc:spawn` -> `/sc:implement`, `/sc:design`, `/sc:test`

**Best practice**: Always end with a `**Next Step**:` that names 1-2 specific `/sc:*` commands.

### 9. Persona-MCP Alignment

When a command activates multiple personas, each persona should map to a specific concern and ideally to a specific MCP server:
- architect -> Sequential (analysis)
- frontend -> Magic (UI generation)
- security -> Sequential (threat modeling)
- qa-specialist -> Playwright (testing)
- devops-engineer -> Playwright (validation)
- deep-research-agent -> Tavily (search)

**Best practice**: Document the persona-MCP-concern triple explicitly in the MCP Integration section.

### 10. Complexity-Driven Feature Inclusion

The `complexity` field should drive which features are included:
- `basic`: No MCP, no personas, no TodoWrite, no Task delegation
- `standard`: Optional MCP, optional personas, TodoWrite for multi-file ops
- `enhanced`: MCP integration, persona activation, TodoWrite standard
- `advanced`/`high`: Full MCP suite, multi-persona, TodoWrite + Task delegation, wave eligibility

### 11. Consistent Category Taxonomy

The current category values are inconsistent (`utility`, `workflow`, `special`, `command`). Standardize to:
- `utility`: Single-purpose tools (analyze, build, test)
- `workflow`: Multi-step processes that modify code (cleanup, implement)
- `special`: Meta-system orchestration (spawn, task, reflect)
- `reference`: Dispatchers and help (sc, help, index)

### 12. Safety-First Design

Commands that modify code (cleanup, implement, build) should always:
1. Default to safe mode unless `--aggressive` is explicitly passed
2. Include a validation step in the behavioral flow
3. Define auto-fix vs. approval-required thresholds
4. Reference backup/rollback capability in boundaries

---

## Section C: Command Template

A complete template for creating new SuperClaude commands, following all discovered rules and best practices.

```markdown
---
name: <command-name>
description: "<Verb-phrase describing what the command does>"
category: <utility|workflow|special|reference>
complexity: <basic|standard|enhanced|advanced|high>
mcp-servers: [<server1>, <server2>]
personas: [<persona1>, <persona2>]
---

# /sc:<command-name> - <Short Descriptive Title>

## Triggers
- <Scenario 1 when this command should activate>
- <Scenario 2 when this command should activate>
- <Scenario 3 when this command should activate>
- <Scenario 4 when this command should activate>

## Usage
\```
/sc:<command-name> [target] [--type option1|option2|option3] [--flag1] [--flag2 value]
\```

## Behavioral Flow
1. **<AssessVerb>**: <Description of assessment/discovery phase>
2. **<PrepareVerb>**: <Description of planning/validation phase>
3. **<ExecuteVerb>**: <Description of primary action phase>
4. **<VerifyVerb>**: <Description of validation/quality check phase>
5. **<OutputVerb>**: <Description of reporting/integration phase>

Key behaviors:
- <Distinctive behavior 1 -- what makes this command special>
- <Distinctive behavior 2 -- MCP or persona coordination pattern>
- <Distinctive behavior 3 -- execution strategy or optimization>
- <Distinctive behavior 4 -- quality or safety characteristic>

## MCP Integration
- **<Server1> MCP**: <When auto-activated and why; what capability it provides>
- **<Server2> MCP**: <When auto-activated and why; what capability it provides>
- **Persona Coordination**: <Which personas activate and for what concerns>

## Tool Coordination
- **Read/Grep/Glob**: <Analysis and discovery purpose>
- **Edit/MultiEdit**: <Modification and code change purpose>
- **Write**: <Generation and documentation purpose>
- **Bash**: <External execution and system operation purpose>
- **TodoWrite**: <Progress tracking for multi-step operations>
- **Task**: <Delegation for large-scale workflows requiring sub-agent coordination>

## Key Patterns
- **<Pattern Name 1>**: <Input/trigger> → <transformation> → <output/result>
- **<Pattern Name 2>**: <Input/trigger> → <transformation> → <output/result>
- **<Pattern Name 3>**: <Input/trigger> → <transformation> → <output/result>
- **<Pattern Name 4>**: <Input/trigger> → <transformation> → <output/result>

## Examples

### <Basic Usage Title>
\```
/sc:<command-name>
# <What happens with bare invocation>
# <Key outcome>
\```

### <Focused Flag Usage Title>
\```
/sc:<command-name> <target> --<key-flag> <value>
# <What the flag changes>
# <Key outcome with this flag>
\```

### <Combined Flags Title>
\```
/sc:<command-name> <target> --<flag1> --<flag2> <value>
# <What the combination achieves>
# <Key outcome>
\```

### <Advanced/Specialized Title>
\```
/sc:<command-name> <target> --<advanced-flag> <value> --<specialized-flag>
# <Power-user scenario description>
# <Advanced outcome>
\```

## Boundaries

**Will:**
- <Positive capability 1 -- what this command accomplishes>
- <Positive capability 2 -- what quality/safety it provides>
- <Positive capability 3 -- what comprehensive output it generates>

**Will Not:**
- <Negative constraint 1 -- scope limitation>
- <Negative constraint 2 -- safety boundary>
- <Negative constraint 3 -- authority boundary>

## CRITICAL BOUNDARIES

<!-- Include this section for commands that produce output but should NOT implement -->
<!-- Remove this section for commands that are expected to make changes -->

**<STOP DIRECTIVE IN BOLD CAPS>**

This command produces a <OUTPUT TYPE> ONLY - <what it does not do>.

**Explicitly Will NOT**:
- <Hard constraint 1>
- <Hard constraint 2>
- <Hard constraint 3>
- <Hard constraint 4>

**Output**: <Output type> containing:
- <Output element 1>
- <Output element 2>
- <Output element 3>
- <Output element 4>

**Next Step**: <Workflow continuation guidance naming specific /sc:* commands>
```

### Template Usage Notes

**When filling in the template:**

1. **Frontmatter `name`**: Must match the filename (without `.md` extension). Lowercase, single word or hyphenated.

2. **Frontmatter `description`**: Start with a verb or noun. Keep to one sentence. Wrap in double quotes.

3. **Frontmatter `category`**: Choose based on what the command does:
   - `utility` -- reads/analyzes/reports without modifying code
   - `workflow` -- multi-step process that modifies code
   - `special` -- meta-system orchestration or delegation
   - `reference` -- help, index, dispatcher

4. **Frontmatter `complexity`**: Drives feature inclusion:
   - `basic` -- no MCP, no personas, simple tool usage
   - `standard` -- optional MCP, optional personas, TodoWrite for multi-file
   - `enhanced` -- MCP integration expected, persona activation, TodoWrite standard
   - `advanced`/`high` -- full MCP suite, multi-persona, Task delegation, wave-eligible

5. **Frontmatter `mcp-servers`**: Only list servers the command actually uses. Valid values: `sequential`, `context7`, `magic`, `playwright`, `serena`, `tavily`, `morphllm`.

6. **Frontmatter `personas`**: Only list personas the command activates. Use kebab-case: `architect`, `frontend`, `backend`, `security`, `qa-specialist`, `devops-engineer`, `deep-research-agent`, `project-manager`, `quality`.

7. **Behavioral Flow verbs**: Pick from these proven verb pools:
   - Step 1 (Assess): Analyze, Discover, Understand, Examine
   - Step 2 (Prepare): Plan, Validate, Configure, Decompose, Choose
   - Step 3 (Act): Execute, Generate, Orchestrate, Coordinate, Apply
   - Step 4 (Verify): Validate, Analyze, Monitor, Assess
   - Step 5 (Output): Report, Integrate, Optimize, Package, Document

8. **CRITICAL BOUNDARIES**: Include this section ONLY for commands that should NOT implement/execute (research, spawn, analyze-only). Remove for commands that are expected to make changes (implement, cleanup, build).

9. **Next Step**: Always chain to 1-2 specific `/sc:*` commands to guide the user's workflow.

10. **Tool Coordination**: Only list tools the command actually uses. Remove unused tool groups from the template.

---

## Appendix: Per-Command Extraction Summary

### /sc:analyze
| Dimension | Value |
|-----------|-------|
| Category | utility |
| Complexity | basic |
| MCP Servers | [] (none declared) |
| Personas | [] (none declared) |
| Behavioral Flow Steps | Discover, Scan, Evaluate, Recommend, Report |
| Tools | Glob, Grep, Read, Bash, Write |
| Sub-agent delegation | No |
| Wave/orchestration | No |
| Quality gates | Severity-based prioritization |
| Output format | Analysis report (severity-rated findings, metrics, recommendations) |
| Progress tracking | Not specified |
| Safety rails | Will Not modify code without consent |
| Error handling | Not specified |
| Critical boundaries | No |
| Next step | /sc:improve or /sc:cleanup |

### /sc:cleanup
| Dimension | Value |
|-----------|-------|
| Category | workflow |
| Complexity | standard |
| MCP Servers | [sequential, context7] |
| Personas | [architect, quality, security] |
| Behavioral Flow Steps | Analyze, Plan, Execute, Validate, Report |
| Tools | Read/Grep/Glob, Edit/MultiEdit, TodoWrite, Task |
| Sub-agent delegation | Yes (Task for large-scale workflows) |
| Wave/orchestration | No explicit wave, but multi-persona coordination |
| Quality gates | Pre/during/post safety checks, auto-fix vs approval thresholds |
| Output format | Cleanup summary with maintenance recommendations |
| Progress tracking | TodoWrite for multi-file operations |
| Safety rails | Auto-fix vs approval-required matrix, safety threshold rules |
| Error handling | Backup and rollback capabilities referenced |
| Critical boundaries | No |
| Next step | Not explicitly specified |

### /sc:spawn
| Dimension | Value |
|-----------|-------|
| Category | special |
| Complexity | high |
| MCP Servers | [] (native orchestration) |
| Personas | [] (none declared) |
| Behavioral Flow Steps | Analyze, Decompose, Orchestrate, Monitor, Integrate |
| Tools | TodoWrite, Read/Grep/Glob, Edit/MultiEdit/Write, Bash |
| Sub-agent delegation | Core purpose -- delegates to other /sc:* commands |
| Wave/orchestration | Hierarchical breakdown (Epic > Story > Task > Subtask) |
| Quality gates | Dependency analysis and validation before execution |
| Output format | Task breakdown document with hierarchy, dependencies, delegation assignments |
| Progress tracking | TodoWrite hierarchical task breakdown |
| Safety rails | STOP AFTER TASK DECOMPOSITION -- will not execute |
| Error handling | Not specified |
| Critical boundaries | Yes -- produces task hierarchy only, delegates execution |
| Next step | /sc:implement, /sc:design, /sc:test |

### /sc:task
| Dimension | Value |
|-----------|-------|
| Category | special |
| Complexity | advanced |
| MCP Servers | [sequential, context7, magic, playwright, morphllm, serena] |
| Personas | [architect, analyzer, frontend, backend, security, devops, project-manager] |
| Behavioral Flow Steps | Analyze, Delegate, Coordinate, Validate, Optimize |
| Tools | TodoWrite, Task, Read/Write/Edit, sequentialthinking |
| Sub-agent delegation | Core pattern -- multi-agent coordination |
| Wave/orchestration | Strategy selection (systematic, agile, enterprise), parallel processing |
| Quality gates | Quality gates and completion verification |
| Output format | Task completion report (accomplishments, files modified, test status) |
| Progress tracking | TodoWrite hierarchical + cross-session persistence |
| Safety rails | STOP when task complete, do not continue without user input |
| Error handling | Not specified |
| Critical boundaries | Yes -- user-invoked discrete execution, explicit start/end |
| Next step | User decides next action |

### /sc:implement
| Dimension | Value |
|-----------|-------|
| Category | workflow |
| Complexity | standard |
| MCP Servers | [context7, sequential, magic, playwright] |
| Personas | [architect, frontend, backend, security, qa-specialist] |
| Behavioral Flow Steps | Analyze, Plan, Generate, Validate, Integrate |
| Tools | Write/Edit/MultiEdit, Read/Grep/Glob, TodoWrite, Task |
| Sub-agent delegation | Yes (Task for large-scale feature development) |
| Wave/orchestration | Multi-persona coordination |
| Quality gates | Completion criteria (compiles, basic functionality, ready for testing) |
| Output format | Implemented feature code with post-implementation checklist |
| Progress tracking | TodoWrite for multi-file implementations |
| Safety rails | Will not override safety constraints or bypass quality gates |
| Error handling | Not specified |
| Critical boundaries | No (but has COMPLETION CRITERIA section) |
| Next step | /sc:test then /sc:git |

### /sc:research
| Dimension | Value |
|-----------|-------|
| Category | command |
| Complexity | advanced |
| MCP Servers | [tavily, sequential, playwright, serena] |
| Personas | [deep-research-agent] |
| Behavioral Flow Steps | Understand, Plan, TodoWrite, Execute, Track, Validate (6 steps -- deviation) |
| Tools | Tavily (search/extract), Sequential (reasoning), Playwright (JS content), Serena (persistence) |
| Sub-agent delegation | Parallel-first search batching |
| Wave/orchestration | Adaptive depth (quick/standard/deep/exhaustive), multi-hop exploration |
| Quality gates | Evidence verification, source credibility, contradiction resolution |
| Output format | Research report saved to claudedocs/research_[topic]_[timestamp].md |
| Progress tracking | TodoWrite with adaptive task hierarchy (3-15 tasks) |
| Safety rails | STOP AFTER RESEARCH REPORT -- no implementation |
| Error handling | Not specified |
| Critical boundaries | Yes -- produces research report only, no implementation |
| Next step | /sc:design or /sc:implement |

### /sc:build
| Dimension | Value |
|-----------|-------|
| Category | utility |
| Complexity | enhanced |
| MCP Servers | [playwright] |
| Personas | [devops-engineer] |
| Behavioral Flow Steps | Analyze, Validate, Execute, Optimize, Package |
| Tools | Bash, Read, Grep, Glob, Write |
| Sub-agent delegation | No |
| Wave/orchestration | No |
| Quality gates | Build verification, quality gates, deployment readiness |
| Output format | Build artifacts and comprehensive build report |
| Progress tracking | Not specified |
| Safety rails | Will not modify build configuration or install dependencies |
| Error handling | Intelligent error analysis with resolution guidance |
| Critical boundaries | No |
| Next step | Not explicitly specified |

### /sc:reflect
| Dimension | Value |
|-----------|-------|
| Category | special |
| Complexity | standard |
| MCP Servers | [serena] |
| Personas | [] (none declared) |
| Behavioral Flow Steps | Analyze, Validate, Reflect, Document, Optimize |
| Tools | TodoRead/TodoWrite, Serena reflection tools, Memory tools |
| Sub-agent delegation | No |
| Wave/orchestration | No |
| Quality gates | Task adherence verification, completion assessment |
| Output format | Reflection analysis with session metadata and learning insights |
| Progress tracking | Bridge between TodoWrite and Serena analysis |
| Safety rails | Will not override completion decisions without validation |
| Error handling | Not specified |
| Critical boundaries | No |
| Next step | Not explicitly specified |

### /sc:test
| Dimension | Value |
|-----------|-------|
| Category | utility |
| Complexity | enhanced |
| MCP Servers | [playwright] |
| Personas | [qa-specialist] |
| Behavioral Flow Steps | Discover, Configure, Execute, Analyze, Report |
| Tools | Bash, Glob, Grep, Write |
| Sub-agent delegation | No |
| Wave/orchestration | No |
| Quality gates | Coverage thresholds, pass/fail analysis |
| Output format | Coverage reports and test summaries |
| Progress tracking | Not specified |
| Safety rails | Will not generate tests or modify test config without permission |
| Error handling | Test failure analysis and debugging |
| Critical boundaries | No |
| Next step | Not explicitly specified |

### /sc (dispatcher)
| Dimension | Value |
|-----------|-------|
| Category | (not specified -- reference) |
| Complexity | (not specified) |
| MCP Servers | (not specified) |
| Personas | (not specified) |
| Structure | Unique -- serves as help/index, not a behavioral command |
| Notes | Uses minimal frontmatter, does not follow standard command structure |

### Confidence Check Skill
| Dimension | Value |
|-----------|-------|
| Structure | Simpler frontmatter (name + description only) |
| Sections | Purpose, When to Use, Assessment Criteria (5 checks), Score Calculation, Output Format, ROI |
| Key difference | Skills define assessment criteria with weighted percentages, not behavioral flows |
| Output format | Structured checklist with confidence score and proceed/stop decision |
| Integration | References MCP tools (Context7, Tavily/WebSearch) and native tools (Grep, Glob) within assessment criteria |

---

## Appendix: Identified Inconsistencies

These are deviations from the patterns that should be normalized:

1. **analyze.md** declares `mcp-servers: []` and `personas: []` but the command clearly performs analysis that would benefit from Sequential MCP. Likely should declare at minimum `[sequential]`.

2. **research.md** uses `category: command` while other commands use `utility`, `workflow`, or `special`. Should be normalized to `utility` or `special`.

3. **research.md** uses 6 behavioral flow steps instead of the standard 5. The TodoWrite and Track steps could be merged into Execute.

4. **spawn.md** declares `mcp-servers: []` and `personas: []` but its MCP Integration section describes "Native Orchestration" and "Framework Integration". If truly MCP-free, the section should say so more clearly.

5. **cleanup.md** has no explicit `**Next Step**:` recommendation at the end.

6. **build.md**, **reflect.md**, **test.md** have no explicit `**Next Step**:` recommendation.

7. **Category taxonomy** is inconsistent: `utility`, `workflow`, `special`, `command` are all used. Needs standardization.

8. **Persona naming** varies: some use role names (`architect`, `security`), others use role-specialist compounds (`qa-specialist`, `devops-engineer`, `deep-research-agent`). Should standardize.
