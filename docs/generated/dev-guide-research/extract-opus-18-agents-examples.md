# Agent Definition Patterns — Complete Extraction

## Source Files

| File | Agent Type | Category | Complexity |
|------|-----------|----------|------------|
| `/config/workspace/SuperClaude_Framework/src/superclaude/agents/debate-orchestrator.md` | Complex orchestrator | analysis | High — multi-agent coordination |
| `/config/workspace/SuperClaude_Framework/src/superclaude/agents/pm-agent.md` | Meta-layer lifecycle agent | meta | High — session persistence, PDCA cycles |
| `/config/workspace/SuperClaude_Framework/src/superclaude/agents/deep-research-agent.md` | Specialist investigator | analysis | Medium — adaptive strategy, multi-hop reasoning |
| `/config/workspace/SuperClaude_Framework/src/superclaude/agents/audit-scanner.md` | Constrained sub-agent | quality | Low — single-pass, read-only, batch worker |
| `/config/workspace/SuperClaude_Framework/src/superclaude/agents/merge-executor.md` | Specialist executor | quality | Medium — plan follower, no decision-making |

---

## 1. Agent File Structure and Format

### YAML Frontmatter

Every agent `.md` file begins with YAML frontmatter delimited by `---`. The frontmatter declares machine-readable metadata. Two patterns emerge: a minimal set and an extended set.

**Minimal frontmatter** (most agents):

```yaml
---
name: debate-orchestrator
description: Coordinate adversarial debate pipeline without participating in debates — process manager for sc:adversarial
category: analysis
---
```

```yaml
---
name: pm-agent
description: Self-improvement workflow executor that documents implementations, analyzes mistakes, and maintains knowledge base continuously
category: meta
---
```

```yaml
---
name: deep-research-agent
description: Specialist for comprehensive research with adaptive strategies and intelligent exploration
category: analysis
---
```

**Extended frontmatter** (constrained sub-agents):

```yaml
---
name: audit-scanner
description: "Fast read-only surface scanner for repository audit Pass 1. Classifies files as DELETE/REVIEW/KEEP with grep evidence."
tools: Read, Grep, Glob
model: haiku
maxTurns: 20
permissionMode: plan
---
```

The extended frontmatter adds:
- `tools`: Explicit tool allowlist (comma-separated). Restricts what the agent can use.
- `model`: Target model tier (`haiku`, `sonnet`, `opus`). Determines cost/capability trade-off.
- `maxTurns`: Maximum conversation turns allowed. Prevents runaway execution.
- `permissionMode`: Access control (`plan` = read-only planning mode).

**Observed frontmatter fields across all agents:**

| Field | Required | Values | Purpose |
|-------|----------|--------|---------|
| `name` | Yes | kebab-case identifier | Agent identity for routing and invocation |
| `description` | Yes | One-line summary | Displayed in help, used for auto-activation matching |
| `category` | Yes | `analysis`, `meta`, `quality`, `development`, etc. | Grouping and routing |
| `tools` | No | Comma-separated tool names | Restricts available tools (sub-agents only) |
| `model` | No | `haiku`, `sonnet`, `opus` | Model tier preference |
| `maxTurns` | No | Integer | Execution budget limit |
| `permissionMode` | No | `plan`, `execute` | Access control level |

### Markdown Body Structure

After frontmatter, the body uses a consistent section hierarchy. The common sections across all four agents are:

```
# Agent Name

## Triggers
## Behavioral Mindset
## Tools (or within responsibilities)
## Responsibilities / Core Capabilities
## Focus Areas
## Outputs
## Boundaries (Will / Will Not)
```

Some agents add specialized sections depending on complexity. Here is the full union of sections observed:

| Section | debate-orchestrator | pm-agent | deep-research-agent | audit-scanner | merge-executor |
|---------|:--:|:--:|:--:|:--:|:--:|
| `# Title` | Yes | Yes | Yes | Yes | Yes |
| `## Triggers` | Yes | Yes | Yes | (implicit in Role) | Yes |
| `## Behavioral Mindset` | Yes | Yes | Yes | (implicit in Role) | Yes |
| `## Model Preference` | Yes | No | No | (in frontmatter) | Yes |
| `## Tools` | Yes | No | No | (in frontmatter) | Yes |
| `## Role` | No | No | No | Yes | No |
| `## Safety Constraint` | No | No | No | Yes | No |
| `## Input` | No | No | No | Yes | No |
| `## Methodology` | No | No | No | Yes | No |
| `## Responsibilities` | Yes | No | No | No | Yes |
| `## Core Capabilities` | No | No | Yes | No | No |
| `## Focus Areas` | Yes | Yes | No | No | Yes |
| `## Key Actions` | No | Yes | No | No | No |
| `## Research Workflow` | No | No | Yes | No | No |
| `## Quality Standards` | No | Yes | Yes | No | No |
| `## Outputs` | Yes | Yes | No | No | Yes |
| `## Output Format` | No | No | No | Yes | No |
| `## Does NOT` | Yes | No | No | No | Yes |
| `## Boundaries` | Yes | Yes | Yes | No | Yes |
| `## Session Lifecycle` | No | Yes | No | No | No |
| `## PDCA Self-Evaluation` | No | Yes | No | No | No |
| `## Memory Operations` | No | Yes | No | No | No |
| `## Performance Metrics` | No | Yes | No | No | No |
| `## Example Workflows` | No | Yes | No | No | No |
| `## Integration with Specialist Agents` | No | Yes | No | No | No |
| `## Performance Optimization` | No | No | Yes | No | No |
| `## Classification Taxonomy` | No | No | No | Yes | No |
| `## Incremental Save Protocol` | No | No | No | Yes | No |

---

## 2. How Agents Define Their Capabilities and Tools

### Pattern A: Explicit Tools Section (Orchestrator / Executor Agents)

The `debate-orchestrator` and `merge-executor` list tools in a dedicated `## Tools` section with per-tool purpose annotations:

**debate-orchestrator:**
```markdown
## Tools
- **Task**: Delegate to advocate agents and merge-executor
- **Read**: Load variant files, diff analysis, debate transcripts
- **Write**: Produce scoring artifacts, base-selection report, refactoring plan
- **Glob**: Discover variant files and artifact structure
- **Grep**: Pattern matching for requirement coverage and contradiction detection
- **Bash**: File operations, directory creation, variant copying
```

**merge-executor:**
```markdown
## Tools
- **Read**: Load base variant and refactoring plan
- **Write**: Produce merged output and merge-log
- **Edit**: Apply targeted changes to base document during merge
- **Grep**: Content verification, reference validation, contradiction re-scan
```

### Pattern B: Frontmatter Tool Restriction (Constrained Sub-Agents)

The `audit-scanner` declares tools in frontmatter as an allowlist:

```yaml
tools: Read, Grep, Glob
```

This is a hard constraint. The agent cannot use Write, Edit, Bash, or Task tools. This enforces the read-only safety requirement stated in its body.

### Pattern C: Implicit Tools via Workflow Description (Research / Meta Agents)

The `deep-research-agent` and `pm-agent` do not have a `## Tools` section. Instead, tool usage is embedded within workflow descriptions:

**deep-research-agent** — tools appear in `## Tool Orchestration`:
```markdown
### Tool Orchestration

**Search Strategy**
1. Broad initial searches (Tavily)
2. Identify key sources
3. Deep extraction as needed
4. Follow interesting leads

**Extraction Routing**
- Static HTML → Tavily extraction
- JavaScript content → Playwright
- Technical docs → Context7
- Local context → Native tools
```

**pm-agent** — tools appear in `## Memory Operations Reference` and workflow YAML blocks:
```yaml
Session Start (MANDATORY):
  - list_memories() → Check what memories exist
  - read_memory("pm_context") → Overall project state
```

And throughout PDCA cycle descriptions:
```yaml
Do Phase:
  Actions:
    - TodoWrite for task tracking (3+ steps required)
    - write_memory("checkpoint", progress) every 30min
```

### Summary of Tool Declaration Approaches

| Approach | Used By | Enforcement Level |
|----------|---------|-------------------|
| Dedicated `## Tools` section with per-tool purpose | debate-orchestrator, merge-executor | Documentation-level (soft) |
| Frontmatter `tools:` field | audit-scanner | System-level (hard restriction) |
| Embedded in workflow descriptions | deep-research-agent, pm-agent | Behavioral guidance (softest) |

---

## 3. Trigger and Activation Patterns

### debate-orchestrator — Command-Invoked Orchestrator

```markdown
## Triggers
- Invoked by `/sc:adversarial` command to coordinate the 5-step adversarial pipeline
- Multi-variant comparison requiring structured debate coordination
- Base selection scoring requiring hybrid quantitative-qualitative evaluation
```

Pattern: Primarily command-driven (`/sc:adversarial`), secondarily pattern-matched on task characteristics.

### pm-agent — Multi-Trigger Lifecycle Agent

```markdown
## Triggers
- **Session Start (MANDATORY)**: ALWAYS activates to restore context from Serena MCP memory
- **Post-Implementation**: After any task completion requiring documentation
- **Mistake Detection**: Immediate analysis when errors or bugs occur
- **State Questions**: "どこまで進んでた", "現状", "進捗" trigger context report
- **Monthly Maintenance**: Regular documentation health reviews
- **Manual Invocation**: `/sc:pm` command for explicit PM Agent activation
- **Knowledge Gap**: When patterns emerge requiring documentation
```

Pattern: The richest trigger set. Combines mandatory auto-activation (session start), event-driven activation (post-implementation, mistake detection), keyword-driven activation (Japanese state queries), scheduled activation (monthly), and manual command activation (`/sc:pm`).

### deep-research-agent — Command + Context Activation

```markdown
## Triggers
- /sc:research command activation
- Complex investigation requirements
- Complex information synthesis needs
- Academic research contexts
- Real-time information requests
```

Pattern: Primary command trigger plus contextual pattern matching on task nature.

### audit-scanner — Delegated Sub-Agent

```markdown
## Input
You will receive:
1. A list of files to audit (your batch)
2. The batch number and total batch count
3. The output file path for your report
```

Pattern: No `## Triggers` section. This agent is never auto-activated or command-invoked directly. It is always delegated to by a parent orchestrator via the Task tool. Its activation is defined by its input contract.

### merge-executor — Delegated Sub-Agent

```markdown
## Triggers
- Invoked by debate-orchestrator agent during Step 5 of the adversarial pipeline
- Refactoring plan ready for execution against a selected base variant
- Document integration tasks requiring structural integrity preservation
```

Pattern: Explicitly states parent agent dependency. Activated by another agent, not by commands or user interaction.

### Trigger Type Taxonomy

| Trigger Type | Example | Agents Using |
|-------------|---------|-------------|
| **Command invocation** | `/sc:adversarial`, `/sc:research`, `/sc:pm` | debate-orchestrator, deep-research-agent, pm-agent |
| **Mandatory auto-activation** | Session start | pm-agent |
| **Event-driven** | Post-implementation, mistake detection | pm-agent |
| **Keyword matching** | Japanese state queries, research keywords | pm-agent, deep-research-agent |
| **Scheduled** | Monthly maintenance | pm-agent |
| **Delegated by parent agent** | Task tool invocation | audit-scanner, merge-executor |
| **Context pattern matching** | Complex investigation needs, academic contexts | deep-research-agent |

---

## 4. Behavioral Mindset Definitions

Each agent defines a `## Behavioral Mindset` section that establishes the agent's operational personality. These are exact quotes:

### debate-orchestrator
> Coordinate the adversarial pipeline with strict neutrality. Never participate in debates or advocate for any variant. Focus on process integrity, fair scoring, and comprehensive documentation of all decisions with evidence.

Key traits: **Neutrality**, **process integrity**, **evidence documentation**.

### pm-agent
> Think like a continuous learning system that transforms experiences into knowledge. After every significant implementation, immediately document what was learned. When mistakes occur, stop and analyze root causes before continuing. Monthly, prune and optimize documentation to maintain high signal-to-noise ratio.

Key traits: **Continuous learning**, **immediate documentation**, **root cause analysis**, **knowledge pruning**.

Additional **Core Philosophy** elaboration:
```markdown
- **Experience → Knowledge**: Every implementation generates learnings
- **Immediate Documentation**: Record insights while context is fresh
- **Root Cause Focus**: Analyze mistakes deeply, not just symptoms
- **Living Documentation**: Continuously evolve and prune knowledge base
- **Pattern Recognition**: Extract recurring patterns into reusable knowledge
```

### deep-research-agent
> Think like a research scientist crossed with an investigative journalist. Apply systematic methodology, follow evidence chains, question sources critically, and synthesize findings coherently. Adapt your approach based on query complexity and information availability.

Key traits: **Systematic methodology**, **critical source evaluation**, **adaptive approach**.

### audit-scanner
Does not have a `## Behavioral Mindset` section. Instead uses `## Role`:
> You are a read-only surface scanner for repository audits. Your job is to quickly classify files as DELETE, REVIEW, or KEEP based on evidence from reading file content and grepping for references.

Key traits: **Read-only**, **classification-focused**, **evidence-based**.

### merge-executor
> Follow the refactoring plan precisely and methodically. Focus on structural integrity, accurate provenance tracking, and producing a unified document that faithfully incorporates planned changes without introducing new content or making strategic decisions.

Key traits: **Plan fidelity**, **structural integrity**, **no autonomous decision-making**.

### Mindset Pattern Summary

| Agent | Autonomy Level | Decision Authority | Primary Orientation |
|-------|---------------|-------------------|-------------------|
| debate-orchestrator | High | Process decisions only, not content | Coordination and scoring |
| pm-agent | High | Full documentation decisions | Knowledge management |
| deep-research-agent | High | Full research strategy decisions | Investigation and synthesis |
| audit-scanner | Low | Classification within taxonomy only | Batch processing |
| merge-executor | Low | None — follows plan | Execution without judgment |

---

## 5. Focus Areas and Key Actions

### debate-orchestrator — Focus Areas

```markdown
## Focus Areas
- **Process Integrity**: Ensure every step executes completely with proper inputs/outputs
- **Scoring Accuracy**: Apply quantitative metrics deterministically and qualitative rubric with CEV protocol
- **Convergence Management**: Track debate convergence and manage round progression
- **Artifact Completeness**: Verify all 6 artifacts are produced (diff-analysis, debate-transcript, base-selection, refactor-plan, merge-log, merged output)
```

### pm-agent — Focus Areas and Key Actions

```markdown
## Focus Areas

### Implementation Documentation
- **Pattern Recording**: Document new patterns and architectural decisions
- **Decision Rationale**: Capture why choices were made (not just what)
- **Edge Cases**: Record discovered edge cases and their solutions
- **Integration Points**: Document how components interact and depend

### Mistake Analysis
- **Root Cause Analysis**: Identify fundamental causes, not just symptoms
- **Prevention Checklists**: Create actionable steps to prevent recurrence
- **Pattern Identification**: Recognize recurring mistake patterns
- **Immediate Recording**: Document mistakes as they occur (never postpone)

### Pattern Recognition
- **Success Patterns**: Extract what worked well and why
- **Anti-Patterns**: Document what didn't work and alternatives
- **Best Practices**: Codify proven approaches as reusable knowledge
- **Context Mapping**: Record when patterns apply and when they don't

### Knowledge Maintenance
- **Monthly Reviews**: Systematically review documentation health
- **Noise Reduction**: Remove outdated, redundant, or unused docs
- **Duplication Merging**: Consolidate similar documentation
- **Freshness Updates**: Update version numbers, dates, and links

### Self-Improvement Loop
- **Continuous Learning**: Transform every experience into knowledge
- **Feedback Integration**: Incorporate user corrections and insights
- **Quality Evolution**: Improve documentation clarity over time
- **Knowledge Synthesis**: Connect related learnings across projects
```

pm-agent also has a `## Key Actions` section with 5 numbered action workflows:
1. Post-Implementation Recording
2. Immediate Mistake Documentation
3. Pattern Extraction
4. Monthly Documentation Pruning
5. Knowledge Base Evolution

Each contains YAML-formatted procedural instructions.

### deep-research-agent — Implicit Focus via Capabilities and Workflow

No explicit `## Focus Areas`. Instead organized as:
- `## Core Capabilities` (6 subsections: Adaptive Planning, Multi-Hop Reasoning, Self-Reflective Mechanisms, Evidence Management, Tool Orchestration, Learning Integration)
- `## Research Workflow` (4 phases: Discovery, Investigation, Synthesis, Reporting)

### audit-scanner — Implicit Focus via Methodology

No explicit `## Focus Areas`. Operational focus defined through:
- `## Methodology` (4-step per-file process)
- `## Classification Taxonomy` (DELETE/REVIEW/KEEP criteria)
- `## Conservative Bias` rule
- `## Dynamic Loading Check` rule
- `## Binary Asset Handling` rule

### merge-executor — Focus Areas

```markdown
## Focus Areas
- **Plan Fidelity**: Execute exactly what the refactoring plan specifies
- **Structural Integrity**: Preserve document coherence through merge operations
- **Provenance Tracking**: Clear attribution for every merged section
- **Post-Merge Validation**: Catch structural breaks, dangling references, and introduced contradictions
```

---

## 6. How Agents Integrate with Commands and Skills

### Command Integration Patterns

**Direct command binding:**
- `debate-orchestrator` is the execution engine for `/sc:adversarial`
- `deep-research-agent` is activated by `/sc:research`
- `pm-agent` is activated by `/sc:pm` and auto-activates on session lifecycle events

**Indirect invocation (delegation chain):**
- `/sc:adversarial` → `debate-orchestrator` → (Task tool) → `merge-executor`
- `/cleanup-audit` → parent orchestrator → (Task tool) → `audit-scanner`

**Meta-layer integration:**
- `pm-agent` operates as a meta-layer above all specialist agents. It auto-activates after any agent completes work:
```yaml
Task Execution Flow:
  1. User Request → Auto-activation selects specialist agent
  2. Specialist Agent → Executes implementation
  3. PM Agent (Auto-triggered) → Documents learnings
```

### Agent-to-Agent Communication

The `debate-orchestrator` demonstrates the most complex agent coordination:

**Delegation pattern:**
```markdown
## Does NOT
- **Generate variants**: Delegates to specified agents via Task tool (Mode B)
- **Participate in debates**: Delegates to dynamically instantiated advocate agents
- **Execute merges**: Delegates to merge-executor agent for Step 5
```

**Return contract pattern** (debate-orchestrator output to calling command):
```markdown
- **Return contract**: Status, paths, convergence score, unresolved conflicts
```

### MCP Server Integration

**pm-agent** integrates deeply with Serena MCP for session persistence:
```yaml
Session Start (MANDATORY):
  - list_memories() → Check what memories exist
  - read_memory("pm_context") → Overall project state

During Work (Checkpoints):
  - write_memory("plan", goal) → Save current plan
  - write_memory("checkpoint", progress) → Save progress every 30min
```

**deep-research-agent** routes to multiple MCP servers based on content type:
```markdown
**Extraction Routing**
- Static HTML → Tavily extraction
- JavaScript content → Playwright
- Technical docs → Context7
- Local context → Native tools
```

---

## 7. Complete Anatomy of an Agent .md File

### Minimal Agent (Constrained Sub-Agent Pattern)

Based on `audit-scanner`:

```markdown
---
name: agent-name
description: "One-line purpose statement"
tools: Tool1, Tool2, Tool3
model: haiku
maxTurns: 20
permissionMode: plan
---

# Agent Title — Context Subtitle

## Role
[Direct second-person instruction: "You are a..."]

## Safety Constraint
[Hard behavioral restriction with failure consequence]

## Input
[What the agent receives when invoked]

## Methodology
[Step-by-step procedure for each work unit]

## Classification Taxonomy / Decision Criteria
[Table or structured rules for categorization decisions]

## Special Rules
[Edge cases, bias corrections, exception handling]

## Output Format
[Exact template with example structure]

## Incremental Save Protocol
[Progress persistence rules]
```

Characteristics:
- Extended frontmatter with hard constraints (tools, model, maxTurns, permissionMode)
- Second-person voice ("You are...")
- Prescriptive methodology with exact steps
- Rigid output template
- Safety constraints with consequences
- No Behavioral Mindset section — replaced by Role
- No Boundaries section — constraints are in Safety Constraint and frontmatter
- Short document (< 100 lines)

### Standard Agent (Specialist Pattern)

Based on `deep-research-agent` and `merge-executor`:

```markdown
---
name: agent-name
description: Purpose statement
category: analysis|quality|development
---

# Agent Title

## Triggers
[List of activation conditions]

## Behavioral Mindset
[Paragraph defining operational personality and approach]

## Model Preference
[Optional: model tier recommendation with rationale]

## Tools
[Optional: bulleted list with per-tool purpose]

## Core Capabilities / Responsibilities
[Numbered list or subsectioned capabilities]

## Focus Areas
[Bulleted key priorities]

## Research Workflow / Methodology
[Phase-based or step-based procedure]

## Quality Standards
[Requirements for output quality]

## Outputs
[List of artifacts produced]

## Does NOT
[Optional: explicit negative scope]

## Boundaries
**Will:**
- [Positive scope items]

**Will Not:**
- [Negative scope items]

## Performance Optimization
[Optional: efficiency guidance]
```

Characteristics:
- Minimal frontmatter (name, description, category)
- Third-person or imperative voice
- Behavioral Mindset establishes personality
- Multiple capability areas with subsections
- Boundaries section with Will/Will Not pattern
- Medium document (100-200 lines)

### Complex Orchestrator Agent

Based on `debate-orchestrator`:

```markdown
---
name: orchestrator-name
description: Coordination purpose statement
category: analysis
---

# Orchestrator Title

## Triggers
[Command binding + contextual triggers]

## Behavioral Mindset
[Emphasis on neutrality, process integrity, coordination]

## Model Preference
[Highest-capability model recommendation]

## Tools
[Tools with delegation emphasis — Task tool is primary]

## Responsibilities
[Numbered list of coordination duties with detailed descriptions]
1. Parse and validate inputs
2. Dispatch sub-agents (Mode selection)
3. Coordinate multi-step protocol
4. Track convergence/progress metrics
5. Execute scoring/evaluation algorithms
6. Hand off to specialist executors
7. Compile return contract

## Focus Areas
[Process-level concerns, not content-level]

## Outputs
[Multiple artifact types with format specifications]

## Does NOT
[Explicit delegation boundaries — what it delegates vs. does itself]

## Boundaries
**Will:**
- [Coordination scope]

**Will Not:**
- [Content decisions, opinion injection, step skipping]
```

Characteristics:
- Minimal frontmatter but maximum body complexity
- Behavioral Mindset emphasizes neutrality and process
- Responsibilities are the core — numbered, detailed, sequential
- Explicit "Does NOT" section listing delegation boundaries
- Outputs include both artifacts and return contracts
- Highest model preference (opus)
- Task tool is primary for delegation
- Longest among action-oriented agents (60-70 lines)

### Meta-Layer Lifecycle Agent

Based on `pm-agent`:

```markdown
---
name: agent-name
description: Lifecycle and knowledge management purpose
category: meta
---

# Agent Title

## Triggers
[Rich multi-type trigger list: mandatory, event, keyword, scheduled, manual]

## Session Lifecycle (MCP Integration)
### Session Start Protocol
[YAML: memory restoration, context reporting]

### During Work (Continuous Cycle)
[YAML: PDCA phases with memory checkpoints]

### Session End Protocol
[YAML: state preservation, documentation cleanup]

## Self-Evaluation Pattern
[YAML: introspective question framework]

## Documentation Strategy
[YAML: temp → formal knowledge pipeline]

## Memory Operations Reference
[YAML: all MCP memory operations by lifecycle phase]

## Behavioral Mindset
[Learning system personality with Core Philosophy]

## Focus Areas
[5 subsectioned areas with 4 bullets each]

## Key Actions
[5 numbered procedural workflows in YAML]

## Self-Improvement Workflow Integration
### BEFORE Phase
### DURING Phase
### AFTER Phase
### MISTAKE RECOVERY Phase
### MAINTENANCE Phase

## Outputs
[4 output categories with sub-items]

## Boundaries
**Will / Will Not**

## Integration with Specialist Agents
[YAML: how it wraps other agents]

## Quality Standards
[Good/bad documentation criteria]

## Performance Metrics
[YAML: effectiveness tracking]

## Example Workflows
[3 detailed scenario walkthroughs]

## Connection to Global Self-Improvement
[References to framework files]
```

Characteristics:
- Minimal frontmatter despite being the most complex agent
- Heaviest use of YAML code blocks for structured procedures
- Session lifecycle management with mandatory protocols
- Extensive MCP integration (Serena memory operations)
- Self-evaluation and introspection patterns
- Multiple example workflows for different scenarios
- Quality standards with positive/negative criteria
- Performance metrics for self-monitoring
- Longest agent file (693 lines)
- Category `meta` — operates above other agents

---

## 8. Differences Between Simple Agents and Complex Orchestrator Agents

### Comparison Matrix

| Dimension | Simple Sub-Agent (audit-scanner) | Standard Specialist (deep-research, merge-executor) | Complex Orchestrator (debate-orchestrator) | Meta-Layer Agent (pm-agent) |
|-----------|--------------------------------|-----------------------------------------------------|-------------------------------------------|----------------------------|
| **Frontmatter** | Extended (tools, model, maxTurns, permissionMode) | Minimal (name, description, category) | Minimal (name, description, category) | Minimal (name, description, category) |
| **Voice** | Second person ("You are...") | Third person / imperative | Third person / imperative | Third person / imperative |
| **Autonomy** | None — follows procedure | Medium — adapts strategy | High — coordinates process | High — manages knowledge lifecycle |
| **Decision Authority** | Classification within fixed taxonomy | Strategy selection, source evaluation | Process decisions, scoring algorithms | Full documentation decisions |
| **Tool Access** | Hard-restricted via frontmatter | Implicit via workflow | Explicit per-tool section | Implicit via MCP operations |
| **Task Tool Usage** | Never (is delegated TO) | Rarely | Primary tool (delegates TO others) | Never (wraps other agents passively) |
| **Model Tier** | Lowest (haiku) | Medium-high (sonnet/opus) | Highest (opus) | Not specified (context-dependent) |
| **Output Format** | Rigid template | Flexible structured | Multiple typed artifacts + return contract | Multiple document types |
| **Safety Constraints** | Explicit with failure consequence | Boundaries section | Does NOT + Boundaries | Boundaries section |
| **File Length** | ~94 lines | ~185 lines (deep-research) / ~61 lines (merge-executor) | ~69 lines | ~693 lines |
| **Activation** | Delegated by parent only | Command + context | Command-bound | Multi-trigger lifecycle |
| **Session Awareness** | None (stateless batch) | None (single invocation) | Within-pipeline state | Cross-session persistence |
| **MCP Integration** | None | Tavily, Playwright, Context7 (routing) | None specified (uses Task tool) | Serena (deep memory integration) |

### Key Architectural Differences

**1. Control Flow Direction**

- **Sub-agents** (audit-scanner, merge-executor): Receive work, execute, return results. No delegation authority.
- **Orchestrators** (debate-orchestrator): Receive commands, decompose work, delegate to sub-agents, aggregate results.
- **Meta-layer** (pm-agent): Observe other agents' work, extract knowledge, maintain state across sessions.

**2. State Management**

- **Stateless**: audit-scanner processes a batch and produces a report. No memory between invocations.
- **Pipeline-scoped**: debate-orchestrator maintains state within a single adversarial pipeline (convergence scores, round tracking) but does not persist across invocations.
- **Session-persistent**: pm-agent uses Serena MCP memory to persist state across Claude Code sessions with mandatory save/restore protocols.

**3. Boundary Enforcement Mechanisms**

- **Hard constraints** (sub-agents): Frontmatter tool restrictions + safety constraints with explicit failure consequences.
  ```markdown
  ## Safety Constraint
  **DO NOT modify, edit, delete, move, or rename ANY existing file. Violation = task failure.**
  ```

- **Soft constraints** (specialists/orchestrators): Behavioral guidance via "Does NOT" and "Boundaries" sections.
  ```markdown
  ## Does NOT
  - **Generate variants**: Delegates to specified agents via Task tool (Mode B)
  - **Participate in debates**: Delegates to dynamically instantiated advocate agents
  ```

- **Philosophical constraints** (meta agents): Core philosophy and quality standards guide behavior.
  ```markdown
  **Will Not:**
  - Skip documentation due to time pressure or urgency
  - Allow documentation to become outdated without maintenance
  ```

**4. Output Specificity**

- **Sub-agents**: Exact output template with markdown structure specified line-by-line.
  ```markdown
  ## Output Format
  Write your report following this structure:
  ```markdown
  # {Scope} Audit (Pass 1)
  **Status**: Complete
  ...
  ```

- **Orchestrators**: Named artifact list with content descriptions but not exact templates.
  ```markdown
  ## Outputs
  - **diff-analysis.md**: Structural differences, content differences, contradictions, unique contributions
  - **debate-transcript.md**: Full debate with per-point scoring matrix and convergence assessment
  ```

- **Meta agents**: Output categories with sub-items but flexible format.
  ```markdown
  ## Outputs
  ### Implementation Documentation
  - **Pattern Documents**: New patterns discovered during implementation
  - **Decision Records**: Why certain approaches were chosen over alternatives
  ```

---

## 9. Patterns for Agent Development

### Pattern: The Constrained Worker

Use when: You need a cost-effective, parallelizable batch processor with safety guarantees.

Template signals:
- Extended frontmatter with `tools`, `model`, `maxTurns`, `permissionMode`
- `## Role` instead of `## Behavioral Mindset`
- `## Safety Constraint` with explicit failure consequence
- `## Input` defining the contract from parent
- `## Methodology` with exact per-item steps
- `## Output Format` with rigid template
- No `## Triggers` — activated only via delegation
- Lowest model tier (haiku)
- Short file (~100 lines)

### Pattern: The Specialist Investigator

Use when: You need an autonomous agent that adapts its strategy to the problem.

Template signals:
- Minimal frontmatter
- Rich `## Behavioral Mindset` with personality metaphor
- `## Core Capabilities` with multiple strategy options
- Self-reflective mechanisms (replanning triggers, progress assessment)
- Tool orchestration with routing logic
- `## Boundaries` with "Excel at" / "Limitations"
- Medium model tier (sonnet/opus)
- Medium file (~150-200 lines)

### Pattern: The Process Orchestrator

Use when: You need multi-agent coordination with strict process adherence.

Template signals:
- Minimal frontmatter
- `## Behavioral Mindset` emphasizing neutrality
- `## Model Preference` requesting highest tier
- `## Tools` with Task tool as primary
- `## Responsibilities` as numbered sequential steps
- `## Does NOT` listing delegation boundaries
- `## Outputs` including return contracts
- Strict artifact accountability
- Medium file (~70 lines, but dense)

### Pattern: The Meta-Layer Agent

Use when: You need cross-session knowledge management and lifecycle persistence.

Template signals:
- Minimal frontmatter with `category: meta`
- Multi-type trigger list (mandatory, event, keyword, scheduled, manual)
- `## Session Lifecycle` with Start/During/End protocols
- Deep MCP integration (Serena memory operations)
- PDCA or similar evaluation cycle
- Documentation strategy with temp-to-formal pipeline
- `## Integration with Specialist Agents` explaining meta-layer relationship
- Quality standards with good/bad criteria
- Performance metrics for self-monitoring
- Example workflows for multiple scenarios
- Longest file (~700 lines)
