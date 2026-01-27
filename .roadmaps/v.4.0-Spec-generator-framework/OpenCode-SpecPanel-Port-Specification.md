# OpenCode Spec-Panel Port: Specification Input

> **Purpose**: Input document for generating a formal specification to port `/sc:spec-panel` from Claude Code (SuperClaude) to OpenCode (IBOpenCode)
> **Generated**: 2026-01-17
> **Method**: Parallel research synthesis with chain-of-thought analysis

---

## Executive Summary

Port the `/sc:spec-panel` multi-expert specification review system from Claude Code to OpenCode, enhancing it with a new **Motivation Discovery** capability that understands why users want features (not business objectives) to propose alternative approaches.

---

## 1. Source System Analysis

### 1.1 Current Claude Code Implementation

**Location**: `~/.claude/commands/sc/spec-panel.md`

**Core Components**:
1. **Expert Panel System**: 10 specification experts with distinct voices and methodologies
2. **Three Analysis Modes**: Discussion, Critique, Socratic
3. **MCP Integration**: Sequential (reasoning), Context7 (documentation)
4. **Persona System**: technical-writer, system-architect, quality-engineer
5. **Iterative Improvement**: Multi-iteration refinement with validation gates
6. **Quality Metrics**: Clarity, Completeness, Testability, Consistency scoring

**Expert Roster**:
| Expert | Domain | Methodology |
|--------|--------|-------------|
| Karl Wiegers | Requirements Engineering | SMART criteria, testability analysis |
| Gojko Adzic | Specification by Example | Given/When/Then, example mapping |
| Alistair Cockburn | Use Case Methodology | Actor-goal analysis, scenarios |
| Martin Fowler | Software Architecture | DDD, bounded contexts, patterns |
| Michael Nygard | Production Systems | Failure modes, resilience |
| Sam Newman | Microservices | Service boundaries, API contracts |
| Gregor Hohpe | Integration Patterns | Messaging, event-driven |
| Lisa Crispin | Agile Testing | Test quadrants, automation |
| Janet Gregory | Testing Advocacy | ATDD, quality coaching |
| Kelsey Hightower | Cloud Native | Kubernetes, declarative config |

### 1.2 Analysis Modes

**Discussion Mode**:
- Sequential expert commentary building on previous insights
- Cross-expert validation and refinement
- Consensus building around improvements
- Output: Collaborative analysis with convergent insights

**Critique Mode**:
- Issue identification with severity (CRITICAL/MAJOR/MINOR)
- Specific improvement recommendations
- Priority ranking by impact and effort
- Output: Systematic review with improvement roadmap

**Socratic Mode**:
- Expert-guided questioning from each framework
- Assumption identification and validation
- Alternative approach exploration
- Output: Learning-focused inquiry with deeper understanding

---

## 2. Target Platform: OpenCode

### 2.1 Architecture Mapping

| Claude Code Feature | OpenCode Equivalent |
|---------------------|---------------------|
| Skill frontmatter | Agent YAML frontmatter |
| `/sc:command` | `/rf:command` (namespace configurable) |
| Sequential MCP | maxSteps + chain-of-thought prompts |
| Context7 MCP | Context7 MCP (direct equivalent) |
| Persona system | Agent definitions with embedded personas |
| Task subagents | `@task` tool with agent invocation |

### 2.2 OpenCode File Structure

```
.opencode/
  command/
    spec-panel.md                    # Main entry point
    spec-panel-critique.md           # Critique mode shortcut
    spec-panel-socratic.md           # Socratic mode shortcut
  agent/
    experts/
      wiegers.md                     # Requirements expert
      adzic.md                       # BDD expert
      cockburn.md                    # Use case expert
      fowler.md                      # Architecture expert
      nygard.md                      # Production systems expert
      newman.md                      # Microservices expert
      hohpe.md                       # Integration expert
      crispin.md                     # Testing expert
      gregory.md                     # Quality expert
      hightower.md                   # Cloud native expert
    personas/
      technical-writer.md            # Writing quality persona
      system-architect.md            # Architecture persona
      quality-engineer.md            # QA persona
    orchestration/
      spec-panel-orchestrator.md     # Main orchestrator
      motivation-discoverer.md       # NEW: Motivation analysis
      alternative-generator.md       # NEW: Alternative solutions
      iterative-reviewer.md          # Iteration management
      validation-gate.md             # Quality validation
  resources/
    scoring-config.md                # Quality scoring rubrics
    expert-selection-rules.md        # Expert selection logic
    motivation-questions.md          # Motivation discovery Q bank
```

### 2.3 Configuration Requirements

**opencode.json additions**:
```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

---

## 3. NEW CAPABILITY: Motivation Discovery

### 3.1 Purpose

**CRITICAL**: This is NOT about business objectives or corporate goals.

Motivation Discovery helps understand **why** a user wants something at the human level, enabling proposal of **alternative approaches** that might achieve the same goal better.

The workflow:
1. User states a feature/requirement
2. System discovers underlying motivation (the "why")
3. System proposes alternatives (different "hows")
4. User can choose the best approach for their actual need

### 3.2 Core Methodology

**Job Stories over User Stories**:
```
User Story: "As a user, I want export to PDF"
Job Story: "When presenting to stakeholders, I want shareable reports so I can demonstrate progress"
```

Format: **"When [situation], I want to [motivation], so I can [outcome]"**

### 3.3 Discovery Techniques

**1. Jobs-to-be-Done (JTBD)**:
- What "job" is the user hiring this feature for?
- Functional dimension: The practical task
- Emotional dimension: How they want to feel
- Social dimension: How they want to be perceived

**2. Five Whys**:
- Ask "why" iteratively to drill to root motivation
- Each answer becomes subject of next "why"
- Stop when reaching something non-obvious

**3. Socratic Questioning**:
- Clarification: "What do you mean by...?"
- Assumptions: "What are you assuming about...?"
- Evidence: "How do you know...?"
- Perspectives: "How might someone else see this?"
- Implications: "If we do this, what else happens?"

**4. Goal Decomposition**:
- Break goals into sub-goals (AND/OR trees)
- Find where proposed solution sits
- Explore sibling paths (OR alternatives)

**5. Means-Ends Analysis**:
- Separate the "what" (goal) from the "how" (mechanism)
- User often proposes mechanism when asked about goal
- Dig back to discover actual goal

### 3.4 Discovery Questions Bank

**Opening**:
- "What are you ultimately trying to accomplish?"
- "Walk me through the last time you needed to do this"
- "What would success look like?"

**Deepening**:
- "Why is that important to you?"
- "What happens if you can't do that?"
- "What have you tried already?"

**Assumption Testing**:
- "What would have to be true for this solution to work?"
- "What if that assumption was wrong?"

**Alternative Exploration**:
- "If this feature didn't exist, what would you do instead?"
- "What's the simplest thing that could possibly work?"
- "How might someone else approach this problem?"

### 3.5 Integration with Spec-Panel

**New Mode**: `--mode motivation` or auto-activated when requirements are vague

**Workflow**:
1. Receive feature request
2. Invoke motivation-discoverer agent
3. Generate clarifying questions using JTBD framework
4. Extract underlying motivation from user responses
5. Pass motivation to alternative-generator agent
6. Present alternatives with rationale
7. Proceed with standard spec-panel analysis

---

## 4. NEW CAPABILITY: Alternative Solution Generation

### 4.1 Purpose

Once underlying motivation is understood, propose different approaches that might achieve the goal better than the originally stated solution.

### 4.2 Generation Techniques

**1. Lateral Thinking (de Bono)**:
- Challenge assumptions
- Reversal: What if we did the opposite?
- Random entry: Introduce unrelated concepts
- Fractionation: Break apart and recombine

**2. TRIZ Contradiction Resolution**:
- Identify trade-off contradictions
- Apply inventive principles:
  - #1 Segmentation: Progressive disclosure
  - #2 Taking Out: Move complexity elsewhere
  - #13 Other Way Round: Pull vs push
  - #24 Intermediary: Proxy layers

**3. Design Thinking HMW**:
- Reframe as "How Might We" questions
- Generate many alternatives (quantity first)
- Dot-vote on promising candidates

**4. Constraint Removal**:
- List all constraints (explicit and implicit)
- Question each: Is this actually true?
- Generate "unconstrained" solutions
- Map back to achievable implementations

**5. First Principles**:
- Strip away all implementation details
- What outcome matters, ignoring mechanisms?
- Rebuild from fundamentals

**6. Analogy-Based**:
- How do other domains solve similar problems?
- Software domains: GitHub, IDEs, documentation tools
- Non-software: Libraries, restaurants, healthcare

**7. Blue Ocean ERRC**:
- Eliminate: What can we remove?
- Reduce: What can be simpler?
- Raise: What should exceed expectations?
- Create: What's never been offered?

### 4.3 Example Application

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Motivation Discovery**: "Identify individual contributors to observed trends"

**Alternatives Generated**:

| # | Alternative | Technique | Description |
|---|-------------|-----------|-------------|
| 1 | Contributor Drawer | Constraint Removal | Slide-out panel with full contributor details |
| 2 | Avatar Stack | TRIZ Intermediary | Show avatars in tooltip, expand on click |
| 3 | Filter by Person | HMW | Toggle to view one contributor's work |
| 4 | GitHub-style Blame | Analogy | Click any point to see "who did this" |
| 5 | Export with Breakdown | Constraint Removal | Detailed data in downloadable format |

### 4.4 Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Motivation Fit | 30% | Does it achieve the underlying goal? |
| User Experience | 25% | Is it intuitive and pleasant? |
| Feasibility | 25% | Can we build it reasonably? |
| Maintainability | 10% | Is it sustainable long-term? |
| Innovation | 10% | Does it offer novel value? |

---

## 5. Output Format: Roadmap Generator Compatible

### 5.1 ID Scheme

| Prefix | Type | Description |
|--------|------|-------------|
| `REQ-###` | FEATURE | New features and requirements |
| `BUG-###` | BUGFIX | Bug fixes |
| `IMP-###` | IMPROVEMENT | Enhancements to existing features |
| `REF-###` | REFACTOR | Code restructuring |
| `DOC-###` | DOC | Documentation |

### 5.2 Required Fields

| Field | Values |
|-------|--------|
| ID | Unique prefix + number |
| Type | FEATURE, BUGFIX, IMPROVEMENT, REFACTOR, DOC |
| Domain | FRONTEND, BACKEND, DEVOPS, SECURITY, ARCHITECTURE, DOCS, API, CONFIG, TESTING |
| Description | Clear, actionable text |
| Dependencies | None, TBD, or comma-separated IDs |
| Priority | P0-Critical, P1-High, P2-Medium (default), P3-Low |

### 5.3 Output Table Format

```markdown
## Features/Requirements
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | BACKEND | [Description] | None | P1-High |
```

---

## 6. Implementation Requirements

### 6.1 Phase 1: Expert Agents (Foundation)

**REQ-001**: Create individual expert agent files for all 10 specification experts
- Domain: BACKEND
- Each agent must have: distinct voice, methodology, critique pattern
- Temperature: 0.3-0.4 for consistent output
- Tools: read=true, write=false (read-only review)

**REQ-002**: Create persona agent files (technical-writer, system-architect, quality-engineer)
- Domain: BACKEND
- Include priority hierarchy and core principles
- Tools: appropriate for role

**REQ-003**: Configure Context7 MCP in opencode.json
- Domain: CONFIG
- Direct equivalent to Claude Code integration

### 6.2 Phase 2: Orchestration

**REQ-004**: Create spec-panel-orchestrator agent
- Domain: BACKEND
- Coordinates expert panel based on mode
- Routes to appropriate experts based on content domain
- Manages sequential vs parallel expert invocation

**REQ-005**: Implement Discussion mode
- Domain: BACKEND
- Sequential expert commentary
- Cross-pollination between insights
- Synthesis generation

**REQ-006**: Implement Critique mode
- Domain: BACKEND
- Parallel expert invocation
- Issue collection with severity ratings
- Quality scoring and improvement roadmap

**REQ-007**: Implement Socratic mode
- Domain: BACKEND
- Question generation from each framework
- User interaction handling
- Follow-up question generation

### 6.3 Phase 3: Motivation Discovery (NEW)

**REQ-008**: Create motivation-discoverer agent
- Domain: BACKEND
- JTBD framework implementation
- Five Whys questioning
- Socratic elicitation
- Goal decomposition

**REQ-009**: Implement motivation discovery workflow
- Domain: BACKEND
- Auto-activation on vague requirements
- Question generation from discovery techniques
- Motivation extraction and documentation

**REQ-010**: Create alternative-generator agent
- Domain: BACKEND
- Lateral thinking techniques
- TRIZ contradiction resolution
- Constraint removal analysis
- Analogy-based finding

**REQ-011**: Implement alternative evaluation
- Domain: BACKEND
- Weighted scoring criteria
- Trade-off documentation
- Recommendation ranking

### 6.4 Phase 4: Iteration & Validation

**REQ-012**: Create validation-gate agent
- Domain: BACKEND
- Quality criteria checking
- Weighted scoring calculation
- Pass/conditional/fail determination

**REQ-013**: Create iterative-reviewer agent
- Domain: BACKEND
- Multi-iteration loop management
- Progress tracking via todowrite
- Quality threshold enforcement

**REQ-014**: Implement iteration focus by round
- Domain: BACKEND
- Round 1: Structural issues
- Round 2: Detail refinement
- Round 3: Polish and optimization

### 6.5 Phase 5: Commands & Integration

**REQ-015**: Create main spec-panel command
- Domain: BACKEND
- Mode routing (discussion/critique/socratic/motivation)
- Expert selection logic
- Output formatting

**REQ-016**: Create mode-specific command shortcuts
- Domain: BACKEND
- /spec-review-discussion
- /spec-review-critique
- /spec-review-socratic
- /spec-discover-motivation

**REQ-017**: Implement roadmap-generator compatible output
- Domain: BACKEND
- ID scheme compliance
- Required fields population
- Table format generation

### 6.6 Documentation

**DOC-001**: Create usage documentation
- Domain: DOCS
- Command reference
- Mode selection guide
- Expert roster description

**DOC-002**: Create migration guide from Claude Code
- Domain: DOCS
- Feature mapping
- Configuration differences
- Testing checklist

---

## 7. Acceptance Criteria

### 7.1 Expert Panel

**GIVEN** a specification document
**WHEN** spec-panel is invoked with `--mode critique`
**THEN** all relevant experts should analyze independently
**AND** issues should be categorized by severity
**AND** quality scores should be calculated

### 7.2 Motivation Discovery

**GIVEN** a vague feature request like "add export button"
**WHEN** motivation discovery is activated
**THEN** system should generate JTBD questions
**AND** extract underlying motivation from responses
**AND** document the "when/want/so" job story

### 7.3 Alternative Generation

**GIVEN** an understood motivation
**WHEN** alternative generation is invoked
**THEN** at least 5 alternatives should be proposed
**AND** each should use a different technique
**AND** each should be evaluated against criteria

### 7.4 Roadmap Compatibility

**GIVEN** spec-panel output
**WHEN** passed to roadmap generator
**THEN** all items should have valid IDs
**AND** types should match enum (FEATURE/BUGFIX/IMPROVEMENT/REFACTOR/DOC)
**AND** domains should match enum
**AND** priorities should match enum

---

## 8. Dependencies

### 8.1 External

- OpenCode CLI (latest version)
- Context7 MCP server access
- Anthropic Claude API access

### 8.2 Internal

```
REQ-003 (Context7) → All REQ-* requiring documentation lookup
REQ-001, REQ-002 (Experts, Personas) → REQ-004 (Orchestrator)
REQ-004 (Orchestrator) → REQ-005, REQ-006, REQ-007 (Modes)
REQ-008 (Motivation Discoverer) → REQ-009 (Workflow)
REQ-010 (Alternative Generator) → REQ-011 (Evaluation)
REQ-012, REQ-013 (Validation, Iteration) → REQ-014 (Iteration Focus)
All REQ-* → REQ-015, REQ-016, REQ-017 (Commands)
```

---

## 9. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Expert voice inconsistency | Medium | Medium | Explicit voice guidelines in prompts, temperature tuning |
| Sequential mode too slow | Medium | Low | Implement parallel expert invocation where possible |
| Motivation questions feel intrusive | Low | High | Frame as collaborative exploration, allow skipping |
| Quality scoring drift | Medium | Medium | Calibration test suite, periodic rubric review |
| Token budget exceeded | Medium | Medium | maxSteps limits, prompt length guidelines |

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Expert voice authenticity | >85% | User feedback rating |
| Motivation extraction accuracy | >80% | Validated against stated goals |
| Alternative novelty | >60% | At least 3/5 alternatives non-obvious |
| Roadmap compatibility | 100% | All outputs pass generator validation |
| User satisfaction | >4/5 | Post-use survey |

---

## Research Sources

This specification was generated from parallel research streams:

1. **OpenCode Commands**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/opencode-commands.md`
2. **OpenCode MCP Integration**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/opencode-mcp.md`
3. **Motivation Discovery Methodology**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/motivation-discovery.md`
4. **Alternative Generation**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/alternative-generation.md`
5. **Roadmap Pipeline Interface**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/roadmap-pipeline.md`
6. **Panel Portability Mapping**: `/config/workspace/ClickProdTools/.dev/releases/current/v0.5/research/panel-portability.md`

---

*Generated by Claude Opus 4.5 through chain-of-thought dependency analysis and parallel research agent synthesis*
