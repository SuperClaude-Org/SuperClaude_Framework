# /sc:spec-panel Invocation Prompt
## OpenCode Spec-Panel Port & Enhancement Specification

---

## PROMPT

```
/sc:spec-panel @.dev/releases/backlog/v.4.0-Spec-generator-framework/SPEC_PANEL_PORTING_SYNTHESIS.md --mode critique --focus requirements,architecture,testing --iterations 3 --format detailed --experts "wiegers,fowler,adzic,nygard,crispin"
```

---

## SPECIFICATION REQUEST

### Project Overview

Generate a comprehensive technical specification for **porting and enhancing the SuperClaude `/sc:spec-panel` command to OpenCode**, transforming it from a monolithic Claude Code skill into a distributed multi-agent architecture leveraging OpenCode's native capabilities.

### Source Documentation

The complete research synthesis is located at:
`@.dev/releases/backlog/v.4.0-Spec-generator-framework/SPEC_PANEL_PORTING_SYNTHESIS.md`

This synthesis document contains:
- Complete extraction of 10 specification experts with methodologies
- 3 analysis modes (Discussion, Critique, Socratic)
- Quality metrics framework (Clarity, Completeness, Testability, Consistency)
- OpenCode architecture mapping (commands, agents, MCP integration)
- Dependency catalog with SuperClaude → OpenCode equivalents
- Enhanced methodologies (JTBD, adversarial validation, expansive questioning)
- Proposed file structure and implementation workflow

---

### Specification Requirements

#### 1. FUNCTIONAL REQUIREMENTS (Wiegers Focus)

**FR-1: Expert Panel System**
- [ ] Port all 10 specification experts as individual OpenCode agents
- [ ] Preserve authentic voice characteristics and signature questions
- [ ] Implement domain-specific activation triggers
- [ ] Define inter-expert communication protocols

**FR-2: Analysis Modes**
- [ ] Implement Discussion mode (collaborative multi-expert analysis)
- [ ] Implement Critique mode (adversarial review with severity ratings)
- [ ] Implement Socratic mode (question-driven exploration)
- [ ] Support mode switching mid-session

**FR-3: Focus Areas**
- [ ] Requirements focus with Wiegers/Adzic/Cockburn panel
- [ ] Architecture focus with Fowler/Newman/Hohpe/Nygard panel
- [ ] Testing focus with Crispin/Gregory/Adzic panel
- [ ] Compliance focus with Wiegers/Nygard/Hightower panel

**FR-4: Quality Metrics**
- [ ] Clarity scoring (language precision, understandability)
- [ ] Completeness scoring (essential element coverage)
- [ ] Testability scoring (measurability, validation capability)
- [ ] Consistency scoring (internal coherence, contradiction detection)

**FR-5: Enhanced Methodologies (NEW)**
- [ ] Jobs-to-be-Done objective extraction before specification
- [ ] Pre-mortem analysis for risk identification
- [ ] STRIDE threat modeling integration
- [ ] SCAMPER technique for idea expansion
- [ ] 10x Thinking for breakthrough questioning

#### 2. ARCHITECTURAL REQUIREMENTS (Fowler/Nygard Focus)

**AR-1: OpenCode Integration Architecture**
```
.opencode/
├── command/
│   └── sc-spec-panel.md          # Main entry point command
├── agent/
│   ├── spec-panel-coordinator.md  # Multi-agent orchestrator
│   ├── spec-expert-wiegers.md     # Requirements Engineering
│   ├── spec-expert-adzic.md       # Specification by Example
│   ├── spec-expert-cockburn.md    # Use Case Expert
│   ├── spec-expert-fowler.md      # Architecture & Design
│   ├── spec-expert-nygard.md      # Production Systems
│   ├── spec-expert-newman.md      # Microservices
│   ├── spec-expert-hohpe.md       # Integration Patterns
│   ├── spec-expert-crispin.md     # Agile Testing
│   ├── spec-expert-gregory.md     # Testing Advocate
│   ├── spec-expert-hightower.md   # Cloud Native
│   └── spec-synthesis-agent.md    # Cross-framework synthesis
└── mcp.json                       # MCP server configuration
```

**AR-2: MCP Server Integration**
- [ ] Sequential Thinking MCP for multi-step reasoning
- [ ] Context retrieval for specification patterns
- [ ] Tool coordination protocol between agents

**AR-3: Agent Communication Protocol**
- [ ] Message passing between coordinator and expert agents
- [ ] State management for iterative analysis sessions
- [ ] Result aggregation and synthesis workflow

**AR-4: Failure Handling**
- [ ] Graceful degradation when experts unavailable
- [ ] Circuit breaker patterns for MCP server failures
- [ ] Recovery mechanisms for interrupted sessions

#### 3. INTERFACE REQUIREMENTS (Adzic/Cockburn Focus)

**IR-1: Command Interface**
```markdown
# Usage
/sc:spec-panel [content|@file] [options]

# Options
--mode discussion|critique|socratic
--focus requirements|architecture|testing|compliance
--experts "expert1,expert2,..."
--iterations N
--format standard|structured|detailed

# Examples
/sc:spec-panel @requirements.md --mode critique
/sc:spec-panel "API design proposal" --mode socratic --experts "fowler,newman"
```

**IR-2: Output Formats**
- [ ] Standard: YAML-structured assessment with recommendations
- [ ] Structured: Token-efficient with symbol system
- [ ] Detailed: Full expert commentary with examples

**IR-3: Interactive Workflows**
- [ ] Multi-iteration refinement cycles
- [ ] Expert selection based on content analysis
- [ ] Progress tracking and checkpointing

#### 4. TESTING REQUIREMENTS (Crispin/Gregory Focus)

**TR-1: Unit Testing**
- [ ] Individual expert agent response validation
- [ ] Mode switching correctness
- [ ] Quality metric calculation accuracy

**TR-2: Integration Testing**
- [ ] End-to-end specification analysis workflow
- [ ] Multi-agent coordination verification
- [ ] MCP server interaction testing

**TR-3: Acceptance Criteria**
- [ ] Given a requirements document, the panel produces expert analysis
- [ ] Given mode=critique, adversarial review with severity ratings appears
- [ ] Given focus=architecture, Fowler/Newman/Hohpe/Nygard are activated
- [ ] Quality scores align with manual assessment within ±10%

**TR-4: Performance Criteria**
- [ ] Simple analysis: < 30 seconds
- [ ] Comprehensive analysis: < 2 minutes
- [ ] Multi-document: < 5 minutes

---

### Expert Panel Analysis Request

#### For KARL WIEGERS (Requirements Engineering)
1. Are the functional requirements complete and measurable?
2. What acceptance criteria are missing for each requirement?
3. How would you validate requirement FR-5 (Enhanced Methodologies)?

#### For MARTIN FOWLER (Architecture)
1. Is the agent architecture appropriately modular?
2. What design patterns should govern inter-agent communication?
3. How should the system handle architectural evolution?

#### For GOJKO ADZIC (Specification by Example)
1. Are the given/when/then scenarios complete?
2. What concrete examples would clarify the modes?
3. How should the iterative refinement cycle be specified?

#### For MICHAEL NYGARD (Production Systems)
1. What failure modes need specification?
2. How should circuit breakers be configured?
3. What operational monitoring is required?

#### For LISA CRISPIN (Testing)
1. Is the testing strategy comprehensive?
2. What edge cases are missing from acceptance criteria?
3. How should test automation be approached?

---

### Deliverables Expected

1. **Complete Technical Specification**
   - All functional requirements with acceptance criteria
   - Architecture diagrams and component interfaces
   - Data flow specifications
   - Error handling specifications

2. **Implementation Roadmap**
   - Phase 1: Core infrastructure (coordinator + 3 experts)
   - Phase 2: Full expert panel (all 10 agents)
   - Phase 3: Enhanced methodologies (JTBD, adversarial)
   - Phase 4: Advanced features (persistence, learning)

3. **Quality Assurance Plan**
   - Testing strategy with coverage targets
   - Performance benchmarks
   - Acceptance test suite

4. **Risk Assessment**
   - Technical risks with mitigation strategies
   - Dependency risks
   - Timeline risks

---

### Success Criteria

The specification is considered complete when:
- [ ] All 5 experts have provided critique-mode analysis
- [ ] Clarity score ≥ 8.5/10
- [ ] Completeness score ≥ 9.0/10
- [ ] Testability score ≥ 8.5/10
- [ ] Consistency score ≥ 9.0/10
- [ ] All critical issues resolved through 3 iterations
- [ ] Implementation roadmap validated by architecture experts

---

## EXECUTION NOTES

### Pre-Panel Preparation
1. Ensure `SPEC_PANEL_PORTING_SYNTHESIS.md` is fully read
2. Load research files from `.dev/releases/backlog/v.4.0-Spec-generator-framework/research/`
3. Activate Sequential Thinking MCP for complex reasoning

### Panel Execution
1. **Iteration 1**: Initial critique identifying gaps and issues
2. **Iteration 2**: Refinement addressing high-severity issues
3. **Iteration 3**: Final polish and validation

### Post-Panel Synthesis
1. Aggregate expert feedback into unified specification
2. Generate implementation-ready technical document
3. Create test specification document
4. Produce project roadmap with milestones

---

*Generated for v.4.0-Spec-generator-framework release planning*
*Target: OpenCode multi-agent specification panel system*
