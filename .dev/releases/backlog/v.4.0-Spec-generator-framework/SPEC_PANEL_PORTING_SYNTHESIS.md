# Comprehensive Synthesis: Porting /sc:spec-panel to OpenCode

**Document Purpose**: Foundation document synthesizing all research for porting and improving the SuperClaude /sc:spec-panel command to OpenCode
**Version**: 1.0
**Date**: 2026-01-17

---

## Executive Summary

This document synthesizes findings from seven parallel research streams to create a comprehensive foundation for porting the SuperClaude `/sc:spec-panel` expert specification review system to OpenCode. The synthesis identifies architectural mappings, dependency resolutions, methodology integrations, and improvement opportunities.

### Key Findings

1. **OpenCode Compatibility**: HIGH - OpenCode's command/agent architecture directly supports the spec-panel pattern with minimal adaptation
2. **MCP Integration**: FULL SUPPORT - OpenCode's MCP client enables Sequential Thinking and Context7 integration
3. **Enhancement Opportunities**: The port provides opportunities to add adversarial validation, higher-level objective extraction, and expansive questioning frameworks not present in the original
4. **Primary Gap**: OpenCode lacks native parallel subagent execution, requiring workarounds for multi-expert concurrent analysis

---

## 1. Architecture Mapping: Claude Code to OpenCode

### 1.1 Command System Translation

| Claude Code | OpenCode | Notes |
|-------------|----------|-------|
| `.claude/commands/sc:spec-panel.md` | `.opencode/command/sc-spec-panel.md` | Path + naming convention change |
| YAML frontmatter | YAML frontmatter | Identical format |
| `$ARGUMENTS` placeholder | `$ARGUMENTS` placeholder | Direct compatibility |
| `@filename` inclusion | `@filename` inclusion | Direct compatibility |
| Skill activation | Agent/Command routing | Different mechanism, similar outcome |

### 1.2 Agent System Translation

| SuperClaude Concept | OpenCode Equivalent | Implementation |
|---------------------|---------------------|----------------|
| Personas (architect, analyzer, qa) | Subagents | Create specialized agents in `.opencode/agent/` |
| Skill system | Plugin + Agent combination | Plugins for tools, Agents for behavior |
| Auto-activation | Agent routing logic | Command template + conditional invocation |
| Sequential MCP | MCP server integration | Configure in `opencode.json` |
| Context7 MCP | MCP server integration | Configure in `opencode.json` |

### 1.3 Configuration Migration

**SuperClaude CLAUDE.md** → **OpenCode AGENTS.md**

```yaml
# Example transformation
# From: SuperClaude skill definition in CLAUDE.md
# To: OpenCode agent definition

# .opencode/agent/spec-panel-coordinator.md
---
description: Coordinates expert specification review panel
mode: subagent
temperature: 0.3
maxSteps: 50
tools:
  read: true
  grep: true
  glob: true
  task: true
  webfetch: true
  bash: false
  edit: false
  write: false
permission:
  task: allow
---
You are the /sc:spec-panel expert coordinator. You orchestrate multi-expert
specification reviews using Karl Wiegers, Gojko Adzic, Alistair Cockburn,
Martin Fowler, Michael Nygard, Sam Newman, Gregor Hohpe, Lisa Crispin,
Janet Gregory, and Kelsey Hightower methodologies.

[Full system prompt with expert definitions...]
```

---

## 2. Dependency Catalog and Resolution

### 2.1 Claude Code Dependencies → OpenCode Equivalents

| Dependency | Claude Code | OpenCode | Resolution Strategy |
|------------|-------------|----------|---------------------|
| Sequential Thinking | Native `mcp__sequential-thinking` | MCP Server integration | Configure Sequential Thinking MCP server |
| Context7 Documentation | Native Context7 skill | MCP Server integration | Configure Context7 MCP server |
| Parallel Subagents | Native parallel execution | Community plugins (oh-my-opencode) | Use plugin or sequential execution |
| Persona System | PERSONAS.md framework | Agent configuration | Create dedicated agents per persona |
| Wave Orchestration | ORCHESTRATOR.md waves | Custom orchestrator agent | Build custom agent with task delegation |
| Quality Gates | MODES.md validation | Custom validation logic | Implement in agent prompt |
| Token Efficiency | MODE_Token_Efficiency.md | Native + prompt engineering | Implement compression in prompts |

### 2.2 MCP Server Configuration for OpenCode

```json
{
  "$schema": "https://opencode.ai/config.json",

  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"],
      "enabled": true,
      "timeout": 60000
    },
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@context7/mcp-server"],
      "enabled": true
    }
  }
}
```

### 2.3 Feature Parity Analysis

| Feature | SuperClaude | OpenCode Native | Gap Resolution |
|---------|-------------|-----------------|----------------|
| 10 Expert Panel | ✅ | ❌ | Implement in agent prompt |
| 3 Analysis Modes | ✅ | ❌ | Implement in command routing |
| 4 Focus Areas | ✅ | ❌ | Implement via arguments |
| Quality Scoring | ✅ | ❌ | Implement in agent logic |
| Iterative Improvement | ✅ | ✅ (via task) | Use task delegation |
| Cross-Expert Synthesis | ✅ | ❌ | Implement in coordinator agent |

---

## 3. Expert Panel System Extraction

### 3.1 The 10 Specification Experts

The spec-panel leverages 10 software specification and engineering experts:

| Expert | Domain | Primary Methodology | Signature Questions |
|--------|--------|---------------------|---------------------|
| **Karl Wiegers** | Requirements Engineering | SMART criteria, testability | "Is this requirement testable?" |
| **Gojko Adzic** | Specification by Example | Concrete examples, BDD | "Can you give me an example?" |
| **Alistair Cockburn** | Use Cases | Actor-goal, success/failure scenarios | "Who is the primary actor?" |
| **Martin Fowler** | Architecture | DDD, patterns, abstraction | "What pattern applies here?" |
| **Michael Nygard** | Production Systems | Stability patterns, failure modes | "What happens when this fails?" |
| **Sam Newman** | Microservices | Service boundaries, APIs | "What owns this data?" |
| **Gregor Hohpe** | Enterprise Integration | Messaging, async patterns | "Is this sync or async?" |
| **Lisa Crispin** | Agile Testing | Testing quadrants, automation | "What's the test strategy?" |
| **Janet Gregory** | ATDD | Acceptance tests, continuous | "Can we test this now?" |
| **Kelsey Hightower** | Cloud Native | K8s, declarative, IaC | "How is this deployed?" |

### 3.2 Analysis Mode Implementations

**Discussion Mode**: Collaborative multi-perspective analysis
- Auto-select 3-5 relevant experts
- Cross-pollination of insights
- Convergent synthesis

**Critique Mode**: Adversarial challenge and stress-testing
- Conflict identification
- Position articulation and rebuttal
- Gap hunting through structured disagreement

**Socratic Mode**: Question-driven capability development
- Progressive questioning depth
- User interaction and reflection
- Learning pattern extraction

### 3.3 Quality Metrics System

| Dimension | Weight | Sub-Criteria |
|-----------|--------|--------------|
| **Clarity** | 25% | Language precision, terminology, organization |
| **Completeness** | 30% | Section coverage, edge cases, integration points |
| **Testability** | 25% | Acceptance criteria, examples, measurability |
| **Consistency** | 20% | No contradictions, terminology consistency |

**Aggregate Formula**: `Overall = (Clarity × 0.25) + (Completeness × 0.30) + (Testability × 0.25) + (Consistency × 0.20)`

---

## 4. Methodology Enhancements for OpenCode Port

### 4.1 Higher-Level Objective Extraction (NEW)

**Integration from research: objective-extraction-methods.md**

The enhanced spec-panel will incorporate methodologies for understanding the TRUE motivations behind user requests:

**Jobs-to-be-Done Framework**:
```yaml
objective_extraction:
  functional_jobs: "What task is being accomplished?"
  emotional_jobs: "How do users want to feel?"
  social_jobs: "How do users want to be perceived?"

  job_story_format: |
    When [situation/context],
    I want to [motivation/action],
    So I can [desired outcome/benefit].
```

**Ladder of Abstraction**:
- Ask "Why?" to move UP (more abstract, broader scope)
- Ask "How?" to move DOWN (more concrete, specific actions)
- Find the "just right" level for actionable but flexible specifications

**Integration Point**: Add JTBD questioning to the Socratic mode expert questioning

### 4.2 Adversarial Validation Framework (NEW)

**Integration from research: adversarial-validation.md**

Enhanced debate/critique mode with structured adversarial patterns:

**Pre-Mortem Analysis**:
```yaml
premortem_protocol:
  trigger: "After initial spec draft"
  prompt: "Imagine it's 6 months from now. This specification led to complete project failure. What went wrong?"
  categories:
    - Ambiguity: "Specification was misinterpreted"
    - Incompleteness: "Critical requirements were missing"
    - Infeasibility: "Technical approach was impossible"
    - Scope_creep: "Boundaries were unclear"
    - Integration: "Components didn't work together"
```

**Multi-Agent Debate Pattern**:
```yaml
debate_agents:
  proposer: "Defends specification decisions"
  critic: "Devil's advocate - challenges assumptions"
  security_agent: "STRIDE threat modeling"
  feasibility_agent: "Technical viability challenge"
  arbiter: "Moderates and synthesizes"

debate_config:
  max_rounds: 3
  termination: ["consensus", "no_new_arguments", "max_rounds"]
```

**STRIDE Integration** for security-focused reviews:
- **S**poofing → Authenticity requirements
- **T**ampering → Integrity requirements
- **R**epudiation → Non-repudiability requirements
- **I**nformation Disclosure → Confidentiality requirements
- **D**enial of Service → Availability requirements
- **E**levation of Privilege → Authorization requirements

### 4.3 Expansive Question Framework (NEW)

**Integration from research: question-framework-design.md**

Enhanced questioning to help users build upon, challenge, and expand their ideas:

**Question Taxonomy**:
1. **Clarifying**: "What do you mean by...?"
2. **Expanding**: "What else could this include...?" (SCAMPER)
3. **Challenging**: "What if we did the opposite...?"
4. **Connecting**: "How does this relate to...?"
5. **Future-focused**: "Where could this lead...?"

**Sequencing Strategies**:
- **Funnel**: Broad → Specific (initial discovery)
- **Diamond**: Diverge → Converge (feature exploration)
- **Spiral**: Iterative deepening (complex requirements)

**"Yes, And..." Methodology**:
```yaml
idea_expansion:
  validation: "Acknowledge and validate contribution"
  building: "Add value by extending the idea"
  rules:
    - Separate creation from editing
    - Focus on expansion before evaluation
    - Generate 10x ideas, not 10% improvements
```

**10x Thinking Integration**:
- "What would make this 10x better?"
- "What if you had unlimited budget?"
- "What would competitors fear you'd build?"

---

## 5. OpenCode Implementation Architecture

### 5.1 File Structure

```
.opencode/
├── command/
│   └── sc-spec-panel.md          # Main command entry point
├── agent/
│   ├── spec-panel-coordinator.md  # Orchestrator agent
│   ├── spec-expert-wiegers.md     # Individual expert agents
│   ├── spec-expert-adzic.md
│   ├── spec-expert-cockburn.md
│   ├── spec-expert-fowler.md
│   ├── spec-expert-nygard.md
│   ├── spec-expert-newman.md
│   ├── spec-expert-hohpe.md
│   ├── spec-expert-crispin.md
│   ├── spec-expert-gregory.md
│   ├── spec-expert-hightower.md
│   ├── spec-adversarial-critic.md # Devil's advocate
│   └── spec-synthesis-agent.md    # Cross-expert synthesis
├── plugin/
│   └── spec-panel-tools/          # Custom tools
│       ├── quality-scorer.ts
│       ├── objective-extractor.ts
│       └── debate-moderator.ts
└── tool/
    └── spec-quality-metrics.ts    # Quality scoring tool
```

### 5.2 Command Definition

```markdown
---
description: Multi-expert specification review and improvement panel
agent: spec-panel-coordinator
model: anthropic/claude-sonnet-4-5
subtask: false
---
# /sc:spec-panel - Expert Specification Review

Execute a multi-expert specification review panel on $ARGUMENTS.

## Mode Selection
Parse arguments for mode flags:
- Default or `--mode discussion`: Collaborative analysis
- `--mode critique` or `--mode debate`: Adversarial challenge
- `--mode socratic`: Question-driven exploration

## Focus Area
Parse arguments for focus:
- `--focus requirements`: Requirements engineering
- `--focus architecture`: System architecture
- `--focus testing`: Quality and testing
- `--focus compliance`: Compliance and audit

## Expert Selection
- Default: Auto-select 3-5 experts based on content domain
- `--experts "name1,name2"`: Specific expert selection
- `--experts all`: Full panel

## Analysis Depth
- Default: Standard analysis
- `--think`: Enhanced reasoning
- `--think-hard`: Deep analysis
- `--ultrathink`: Comprehensive analysis

## Output Format
- Default: Standard markdown report
- `--structured`: Detailed structured output
- `--synthesis-only`: Synthesis without full expert views

## Iterations
- Default: Single pass
- `--iterations N`: Multi-pass improvement (1-5)

Begin analysis of the specification.
```

### 5.3 Configuration (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",

  "agent": {
    "spec-panel-coordinator": {
      "description": "Coordinates expert specification review panel",
      "mode": "primary",
      "temperature": 0.3,
      "maxSteps": 100,
      "tools": {
        "read": true,
        "grep": true,
        "glob": true,
        "task": true,
        "webfetch": true,
        "todowrite": true,
        "bash": false,
        "edit": false,
        "write": false
      }
    },
    "spec-expert": {
      "description": "Individual specification expert subagent",
      "mode": "subagent",
      "temperature": 0.4,
      "maxSteps": 30,
      "tools": {
        "read": true,
        "grep": true,
        "bash": false,
        "edit": false
      }
    },
    "spec-synthesis": {
      "description": "Cross-expert synthesis and integration",
      "mode": "subagent",
      "temperature": 0.2,
      "maxSteps": 20
    }
  },

  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"],
      "enabled": true,
      "timeout": 60000
    }
  },

  "command": {
    "sc-spec-panel": {
      "template": "@.opencode/command/sc-spec-panel.md",
      "description": "Multi-expert specification review panel",
      "agent": "spec-panel-coordinator"
    }
  }
}
```

---

## 6. Execution Workflow

### 6.1 High-Level Flow

```
User: /sc:spec-panel @spec.md --mode critique --focus architecture

┌─────────────────────────────────────────────────────────────────┐
│ 1. COMMAND PARSING                                               │
│    - Parse mode: critique                                        │
│    - Parse focus: architecture                                   │
│    - Load spec.md content                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. OBJECTIVE EXTRACTION (NEW)                                    │
│    - JTBD analysis: What job is this spec doing?                │
│    - Ladder of abstraction: Right level of specification?       │
│    - Stakeholder needs: Who cares and why?                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXPERT SELECTION                                              │
│    - Architecture focus → Fowler, Newman, Hohpe, Hightower     │
│    - Add Nygard for production concerns                         │
│    - Add Wiegers for requirement quality                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. EXPERT ANALYSIS (Sequential or Parallel via plugin)          │
│    - Each expert analyzes through their methodology             │
│    - Sequential MCP for deep reasoning                          │
│    - Critique mode: Position articulation and challenge         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. ADVERSARIAL VALIDATION (Critique mode - NEW)                  │
│    - Pre-mortem analysis: "What went wrong?"                    │
│    - Devil's advocate challenges                                 │
│    - STRIDE security review (if applicable)                     │
│    - Structured rebuttal and defense                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. QUALITY SCORING                                               │
│    - Clarity: X.X/10                                            │
│    - Completeness: X.X/10                                       │
│    - Testability: X.X/10                                        │
│    - Consistency: X.X/10                                        │
│    - Overall: X.X/10                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. CROSS-EXPERT SYNTHESIS                                        │
│    - Convergent insights                                        │
│    - Productive tensions (with resolution)                      │
│    - Blind spots identified                                     │
│    - Prioritized recommendations                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. EXPANSIVE QUESTIONING (NEW)                                   │
│    - SCAMPER: What else could be substituted/combined/adapted? │
│    - 10x Thinking: What would make this 10x better?            │
│    - "Yes, And...": Build upon findings                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. OUTPUT GENERATION                                             │
│    - Structured report with quality scores                      │
│    - Expert insights and recommendations                        │
│    - Prioritized improvement roadmap                            │
│    - Strategic questions for follow-up                          │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Mode-Specific Flows

**Discussion Mode Flow**:
```
Experts analyze → Cross-pollinate insights → Convergent synthesis → Recommendations
```

**Critique Mode Flow**:
```
Pre-mortem → Expert positions → Devil's advocate challenges → Rebuttals → Resolution synthesis
```

**Socratic Mode Flow**:
```
Round 1 questions → User reflection → Follow-up questions → Deeper exploration → Learning synthesis
```

---

## 7. Quality Assurance

### 7.1 Expert Authenticity Validation

Each expert must:
- Use terminology consistent with their published works
- Apply their specific methodology correctly
- Ask their signature questions
- Maintain characteristic voice and perspective

### 7.2 Output Quality Standards

| Criterion | Standard | Validation |
|-----------|----------|------------|
| Citation accuracy | 100% | All findings cite specific spec sections |
| Recommendation actionability | 90%+ | Each recommendation is specific and implementable |
| Expert voice consistency | 85%+ | Voice matches published methodology |
| Synthesis coherence | 90%+ | Synthesis integrates without contradiction |

### 7.3 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Response time (standard) | < 60s | Single expert pass |
| Response time (full panel) | < 5min | All experts + synthesis |
| Token efficiency | 30-50% reduction | With compression |
| Quality score accuracy | ±0.5 points | Compared to human review |

---

## 8. Research Source References

### Research Documents Generated

1. **opencode-architecture.md** - OpenCode command/agent architecture
2. **opencode-tools-mcp.md** - OpenCode tool and MCP capabilities
3. **superclaude-spec-panel-extraction.md** - Complete spec-panel methodology
4. **spec-best-practices.md** - Industry specification standards
5. **objective-extraction-methods.md** - JTBD, Socratic, Design Thinking
6. **adversarial-validation.md** - Debate frameworks, pre-mortem, STRIDE
7. **question-framework-design.md** - Question taxonomy, SCAMPER, sequencing

### Key External References

- OpenCode Official Documentation: https://opencode.ai/docs/
- Sequential Thinking MCP: https://github.com/modelcontextprotocol/servers
- IEEE 830 / ISO 29148 Standards
- RFC 2119 Keyword Conventions
- STRIDE Threat Modeling (Microsoft)
- Jobs-to-be-Done Framework (Ulwick/Christensen)
- Specification by Example (Gojko Adzic)
- Software Requirements (Karl Wiegers)

---

## 9. Implementation Roadmap

### Phase 1: Core Port (Foundation)
- [ ] Create base command definition
- [ ] Implement coordinator agent
- [ ] Create 10 expert agent definitions
- [ ] Configure MCP servers (Sequential Thinking)
- [ ] Basic quality scoring

### Phase 2: Mode Implementation
- [ ] Discussion mode (collaborative analysis)
- [ ] Critique mode (adversarial validation)
- [ ] Socratic mode (question-driven)
- [ ] Focus area routing

### Phase 3: Enhancements
- [ ] Higher-level objective extraction
- [ ] Pre-mortem analysis integration
- [ ] STRIDE security review
- [ ] Expansive questioning framework
- [ ] 10x thinking prompts

### Phase 4: Quality & Polish
- [ ] Multi-iteration workflow
- [ ] Quality gates validation
- [ ] Performance optimization
- [ ] Documentation and examples

---

## 10. Conclusion

The porting of `/sc:spec-panel` from Claude Code to OpenCode is highly feasible with the following key considerations:

**Direct Compatibility**:
- Command syntax and frontmatter format
- MCP server integration
- Agent-based delegation patterns

**Required Adaptations**:
- Path changes (`.claude/` → `.opencode/`)
- Persona system → Agent configuration
- Skill system → Agent + Plugin combination

**Enhancement Opportunities**:
- Higher-level objective extraction (JTBD)
- Structured adversarial validation (pre-mortem, STRIDE)
- Expansive questioning framework (SCAMPER, 10x)
- Multi-agent debate patterns

The resulting OpenCode implementation will not only replicate the original spec-panel functionality but significantly enhance it with modern specification validation methodologies.

---

*Synthesis document generated: 2026-01-17*
*Research streams: 7 parallel agents*
*Total research pages: 600+*
