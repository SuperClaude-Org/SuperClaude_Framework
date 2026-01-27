# SuperClaude /sc:spec-panel Methodology - Complete Extraction

> **Document Purpose**: Comprehensive extraction of the SuperClaude /sc:spec-panel methodology, expert panel system, analysis modes, quality metrics, and integration patterns.
>
> **Source**: Extracted from SuperClaude framework files (CLAUDE.md system), usage examples, and related specification documents.
>
> **Date**: 2026-01-17

---

## Table of Contents

1. [Overview](#overview)
2. [Expert Panel System](#expert-panel-system)
3. [Analysis Modes](#analysis-modes)
4. [Focus Areas](#focus-areas)
5. [Quality Metrics System](#quality-metrics-system)
6. [Iterative Improvement Process](#iterative-improvement-process)
7. [MCP Integration Points](#mcp-integration-points)
8. [Output Format Templates](#output-format-templates)
9. [Command Syntax and Flags](#command-syntax-and-flags)
10. [Integration with SuperClaude Framework](#integration-with-superclaude-framework)

---

## Overview

The `/sc:spec-panel` command is a multi-expert specification review and improvement system that leverages renowned specification and software engineering experts to analyze, critique, and improve software specifications. It is modeled after the `/sc:business-panel` pattern but specialized for technical specification review.

### Purpose

- **Multi-perspective analysis**: Leverage diverse expert viewpoints to identify gaps, inconsistencies, and improvement opportunities
- **Quality validation**: Systematic scoring against established specification quality criteria
- **Iterative improvement**: Support progressive refinement through expert-guided feedback cycles
- **Framework-specific guidance**: Provide recommendations aligned with industry best practices

### Core Capabilities

1. **Expert Simulation**: Authentic voice and methodology simulation of specification domain experts
2. **Multi-Modal Analysis**: Discussion, Critique, and Socratic inquiry modes
3. **Quality Scoring**: Quantitative assessment across clarity, completeness, testability, and consistency dimensions
4. **Cross-Framework Synthesis**: Integration of insights from multiple expert perspectives

---

## Expert Panel System

The spec-panel includes 10 software specification and engineering experts, each bringing a unique domain perspective and methodology.

### Expert 1: Karl Wiegers

**Domain**: Requirements Engineering, Software Requirements Specification

**Methodology**:
- Requirements elicitation and documentation best practices
- Verification of requirement quality attributes (clear, complete, consistent, verifiable)
- Requirements traceability and dependency analysis
- Stakeholder identification and needs analysis

**Critique Focus**:
- Are requirements stated in a testable manner?
- Is the language unambiguous (avoiding terms like "may", "could", "efficient")?
- Are acceptance criteria explicitly defined?
- Is there proper traceability from requirements to implementation?
- Are edge cases and error conditions specified?

**Voice Characteristics**:
- Methodical and precise
- Emphasis on measurability and verifiability
- Questions vague or ambiguous language
- References to "Software Requirements" principles
- Formal but accessible tone

**Signature Questions**:
- "How would we verify this requirement?"
- "What are the acceptance criteria for this feature?"
- "Is this requirement testable as written?"
- "Have we captured all the 'shall' and 'must' statements correctly?"

---

### Expert 2: Gojko Adzic

**Domain**: Specification by Example, Behavior-Driven Development, Living Documentation

**Methodology**:
- Specification by Example (SBE) patterns
- Concrete examples over abstract descriptions
- Living documentation principles
- Collaborative specification workshops

**Critique Focus**:
- Are there concrete examples illustrating expected behavior?
- Can these examples become executable tests?
- Is the specification "alive" (updatable, versionable)?
- Does the specification bridge business and technical understanding?
- Are edge cases illustrated with specific examples?

**Voice Characteristics**:
- Pragmatic and example-driven
- Emphasis on collaboration between roles
- Focus on executable specifications
- Conversational but technically precise
- Often asks for "show me an example"

**Signature Questions**:
- "Can you give me a concrete example of this behavior?"
- "What would an automated test for this look like?"
- "How would we know when this is done?"
- "What happens in this edge case scenario?"

---

### Expert 3: Alistair Cockburn

**Domain**: Use Cases, Agile Development, Crystal Methodologies

**Methodology**:
- Use case writing at multiple goal levels
- Actor-goal analysis
- Success and failure scenarios
- "Writing Effective Use Cases" framework

**Critique Focus**:
- Are actors and their goals clearly identified?
- Is the main success scenario well-defined?
- Are alternative flows and exception handling documented?
- Is the scope (design scope vs system scope) appropriate?
- Are preconditions and postconditions stated?

**Voice Characteristics**:
- Focused on human interaction patterns
- Emphasis on scenarios and flows
- Questions the "why" behind requirements
- Balances rigor with pragmatism
- References to goal levels (summary, user, subfunction)

**Signature Questions**:
- "Who is the primary actor and what is their goal?"
- "What is the main success scenario?"
- "What happens when step X fails?"
- "At what goal level is this use case written?"

---

### Expert 4: Martin Fowler

**Domain**: Software Architecture, Refactoring, Enterprise Patterns

**Methodology**:
- Domain-Driven Design (DDD) concepts
- Enterprise Integration Patterns
- Refactoring patterns
- Architecture documentation

**Critique Focus**:
- Is the architecture clearly communicated?
- Are key design decisions documented with rationale?
- Is the bounded context and domain model clear?
- Are integration points and contracts well-defined?
- Is the specification at the right level of abstraction?

**Voice Characteristics**:
- Thoughtful and nuanced
- Balances theoretical and practical
- Emphasis on clarity and communication
- Often provides multiple perspectives
- References to patterns and principles

**Signature Questions**:
- "What is the architectural significance of this decision?"
- "How does this fit within the bounded context?"
- "What patterns apply here?"
- "Is this at the right level of abstraction?"

---

### Expert 5: Michael Nygard

**Domain**: Production Systems, Resilience, Release It! Patterns

**Methodology**:
- Stability patterns (circuit breakers, bulkheads, timeouts)
- Failure mode analysis
- Capacity planning
- Production readiness

**Critique Focus**:
- Are failure modes and recovery strategies documented?
- Is graceful degradation planned?
- Are operational concerns (monitoring, logging, alerting) addressed?
- Are there timeouts and circuit breakers specified?
- Is the specification production-ready?

**Voice Characteristics**:
- Pragmatic and experience-driven
- Focus on "what happens when things go wrong"
- Emphasis on operational concerns
- Direct and sometimes blunt
- References to real-world failure scenarios

**Signature Questions**:
- "What happens when this dependency is unavailable?"
- "How do we degrade gracefully?"
- "What's the recovery strategy?"
- "How will we know when this is failing in production?"

---

### Expert 6: Sam Newman

**Domain**: Microservices, API Design, Building Microservices

**Methodology**:
- Service decomposition patterns
- API design principles
- Service boundaries and coupling
- Deployment independence

**Critique Focus**:
- Are service boundaries well-defined?
- Is the API contract clear and versioned?
- Are data ownership and consistency models specified?
- Is the service independently deployable?
- Are inter-service communication patterns documented?

**Voice Characteristics**:
- Practical and grounded
- Focus on organizational and technical boundaries
- Emphasis on loose coupling
- Clear communication style
- References to microservices patterns

**Signature Questions**:
- "What owns this data?"
- "How does this service communicate with others?"
- "Can this be deployed independently?"
- "What's the API contract?"

---

### Expert 7: Gregor Hohpe

**Domain**: Enterprise Integration, Messaging Patterns, Architecture

**Methodology**:
- Enterprise Integration Patterns (EIP)
- Messaging and event-driven architecture
- Conversation patterns
- Integration architecture

**Critique Focus**:
- Are integration patterns clearly identified?
- Is the message format and schema documented?
- Are synchronous vs asynchronous patterns appropriate?
- Is error handling in integration flows specified?
- Are retry and dead-letter patterns defined?

**Voice Characteristics**:
- Analytical and pattern-oriented
- Focus on distributed systems
- Emphasis on messaging semantics
- Often uses diagrams and visual metaphors
- References to EIP catalog

**Signature Questions**:
- "What integration pattern is being used here?"
- "Is this synchronous or asynchronous?"
- "What happens to failed messages?"
- "How are we handling idempotency?"

---

### Expert 8: Lisa Crispin

**Domain**: Agile Testing, Whole-Team Quality, Testing Quadrants

**Methodology**:
- Agile Testing Quadrants
- Test automation strategy
- Exploratory testing
- Whole-team quality approach

**Critique Focus**:
- Are test strategies documented for each quadrant?
- Is the automation approach specified?
- Are acceptance test criteria clear?
- Is there a balance of testing types?
- Are non-functional testing requirements specified?

**Voice Characteristics**:
- Collaborative and team-focused
- Emphasis on quality as everyone's responsibility
- Practical testing perspective
- Supportive but thorough
- References to testing quadrants

**Signature Questions**:
- "What's the testing strategy for this feature?"
- "How will we automate these acceptance criteria?"
- "Have we considered exploratory testing needs?"
- "Which testing quadrant does this address?"

---

### Expert 9: Janet Gregory

**Domain**: Agile Testing Advocacy, ATDD, Continuous Testing

**Methodology**:
- Acceptance Test-Driven Development (ATDD)
- Continuous testing integration
- Test-first specification
- Quality coaching

**Critique Focus**:
- Are acceptance tests written before implementation?
- Is the specification testable from day one?
- Are there Gherkin/BDD scenarios?
- Is the test coverage strategy clear?
- Are regression testing needs addressed?

**Voice Characteristics**:
- Educational and encouraging
- Emphasis on test-first approaches
- Focus on continuous improvement
- Practical coaching tone
- References to ATDD practices

**Signature Questions**:
- "Can we write acceptance tests for this now?"
- "What does a passing test look like?"
- "How does this fit into our continuous testing strategy?"
- "Are these scenarios executable?"

---

### Expert 10: Kelsey Hightower

**Domain**: Cloud Native, Kubernetes, Infrastructure as Code

**Methodology**:
- Cloud-native principles
- Container and orchestration patterns
- Infrastructure as Code (IaC)
- GitOps and declarative configuration

**Critique Focus**:
- Are deployment and infrastructure requirements specified?
- Is the configuration declarative and version-controlled?
- Are scaling and resource requirements documented?
- Is the deployment pipeline specified?
- Are cloud-native patterns followed?

**Voice Characteristics**:
- Clear and practical
- Focus on simplicity and fundamentals
- Emphasis on automation
- Accessible technical communication
- References to Kubernetes and cloud-native patterns

**Signature Questions**:
- "How is this deployed?"
- "What are the resource requirements?"
- "Is the configuration declarative?"
- "How does this scale?"

---

## Analysis Modes

The spec-panel supports three primary analysis modes, each designed for different review contexts and objectives.

### Discussion Mode

**Purpose**: Collaborative multi-perspective analysis through complementary frameworks

**Activation**: Default mode; `--mode discussion`

**Process**:
1. **Document Ingestion**: Parse specification content for technical and structural elements
2. **Expert Selection**: Auto-select 3-5 most relevant experts based on content domain
3. **Framework Application**: Each expert analyzes through their unique methodology
4. **Cross-Pollination**: Experts build upon and reference each other's insights
5. **Pattern Recognition**: Identify convergent themes and complementary perspectives
6. **Synthesis**: Combine insights into actionable recommendations

**Output Format**:
```markdown
## Specification Analysis: [Document Title]

### Expert Perspectives

**WIEGERS (Requirements Engineering)**:
*Analysis of requirement quality, traceability, and verifiability*

**ADZIC building on WIEGERS**:
*How specification-by-example can address identified requirement gaps*

**NYGARD**:
*Operational and resilience considerations*

**CRISPIN**:
*Testing strategy and quality assurance perspective*

### Synthesis

**Convergent Insights**: Areas where experts agree
**Complementary Perspectives**: Unique contributions from each framework
**Recommended Improvements**: Prioritized enhancement opportunities
**Quality Assessment**: Overall specification quality indicators
```

**Use Cases**:
- Initial specification review
- Comprehensive quality assessment
- Identifying improvement opportunities
- Building shared understanding across teams

---

### Critique Mode

**Purpose**: Stress-test specifications through structured disagreement and challenge

**Activation**: `--mode critique` or `--mode debate`

**Triggers**:
- High-stakes specifications
- Production-critical systems
- Security or compliance requirements
- Conflicting stakeholder requirements
- Risk assessment contexts

**Process**:
1. **Conflict Identification**: Detect areas of potential expert disagreement
2. **Position Articulation**: Each expert defends their framework's perspective
3. **Evidence Marshaling**: Support positions with methodology-specific logic
4. **Structured Rebuttal**: Respectful challenge with alternative interpretations
5. **Gap Hunting**: Adversarial search for specification weaknesses
6. **Synthesis Through Tension**: Extract insights from productive disagreement

**Output Format**:
```markdown
## Specification Critique: [Document Title]

### Critical Challenges

**NYGARD challenges specification**:
*"The failure modes section is incomplete. What happens when the database connection pool is exhausted? There's no graceful degradation strategy."*

**WIEGERS responds**:
*"AC-003 mentions error handling, but I concur the acceptance criteria lack specificity. 'Handle errors gracefully' is not testable."*

**ADZIC adds**:
*"Can we have a concrete example of the error flow? Currently there's no specification-by-example for the unhappy path."*

### Productive Tensions

**Requirements vs Operations**:
WIEGERS emphasizes requirement completeness; NYGARD emphasizes operational resilience. Resolution: Add explicit failure mode requirements with testable criteria.

### Resolution Summary
[How conflicts were resolved or documented as open issues]
```

**Use Cases**:
- Pre-production specification validation
- Security-critical system reviews
- Compliance and audit preparation
- Risk identification and mitigation

---

### Socratic Mode

**Purpose**: Develop strategic thinking capability through expert-guided questioning

**Activation**: `--mode socratic`

**Triggers**:
- Learning-focused reviews
- Junior team education
- Complex problems requiring deeper understanding
- Capability building contexts
- When user seeks deeper understanding

**Process**:
1. **Question Generation**: Each expert formulates probing questions from their framework
2. **Question Clustering**: Group related questions by specification themes
3. **Progressive Inquiry**: Present questions in increasing depth
4. **User Interaction**: Await user reflection and response
5. **Follow-up Questions**: Deepen based on user answers
6. **Learning Synthesis**: Extract specification thinking patterns and insights

**Output Format**:
```markdown
## Socratic Inquiry: [Document Title]

### Round 1: Foundation Questions

**WIEGERS asks**:
- "What are the acceptance criteria for requirement R001?"
- "How would a tester verify this is implemented correctly?"

**ADZIC asks**:
- "Can you give me a concrete example of the expected behavior?"
- "What would the test data look like for this scenario?"

**COCKBURN asks**:
- "Who is the primary actor in this use case?"
- "What triggers this flow?"

*[Await user responses]*

### Round 2: Deepening Questions
*[Follow-up questions based on responses]*

### Learning Insights
*[Patterns and insights developed through the inquiry]*
```

**Use Cases**:
- Team education and onboarding
- Specification writing skill development
- Complex requirement clarification
- Building shared specification vocabulary

---

## Focus Areas

The spec-panel supports domain-specific analysis through focus area configuration.

### Requirements Focus

**Expert Panel**: Wiegers (lead), Adzic, Cockburn, Gregory

**Analysis Areas**:
- Requirement completeness and traceability
- Acceptance criteria quality
- Use case and scenario coverage
- Requirement interdependencies
- Verification and validation approach
- Stakeholder needs mapping

**Activation**: `--focus requirements` or `--focus "requirements"`

**Quality Emphasis**:
- MUST/SHOULD/MAY keyword usage (RFC 2119)
- Testability of each requirement
- Ambiguity elimination
- Edge case coverage

---

### Architecture Focus

**Expert Panel**: Fowler (lead), Newman, Hohpe, Hightower

**Analysis Areas**:
- System structure and component boundaries
- Integration patterns and contracts
- Data flow and ownership
- Deployment architecture
- Scalability and performance considerations
- Technology decisions and rationale

**Activation**: `--focus architecture` or `--focus "architecture"`

**Quality Emphasis**:
- Clear architectural decisions
- Rationale documentation
- Pattern identification
- Coupling and cohesion analysis

---

### Testing Focus

**Expert Panel**: Crispin (lead), Gregory, Adzic, Wiegers

**Analysis Areas**:
- Test strategy completeness (testing quadrants)
- Automation approach
- Acceptance test clarity
- Performance and security testing
- Regression strategy
- Test data requirements

**Activation**: `--focus testing` or `--focus "testing"`

**Quality Emphasis**:
- Gherkin/BDD scenario quality
- Test coverage strategy
- Automation feasibility
- Non-functional test requirements

---

### Compliance Focus

**Expert Panel**: Wiegers (lead), Nygard, Fowler, Newman

**Analysis Areas**:
- Regulatory requirement mapping
- Audit trail requirements
- Security and privacy considerations
- Operational compliance
- Documentation requirements
- Traceability for compliance

**Activation**: `--focus compliance` or `--focus "compliance"`

**Quality Emphasis**:
- Explicit compliance requirements
- Audit and reporting capabilities
- Security control specifications
- Data handling requirements

---

## Quality Metrics System

The spec-panel evaluates specifications across four primary quality dimensions, each scored on a 10-point scale.

### Clarity Score (0-10)

**Definition**: How clearly and unambiguously the specification communicates its intent

**Criteria**:
| Score | Description |
|-------|-------------|
| 0-2 | Unclear, ambiguous, jargon-heavy, incomprehensible |
| 3-4 | Significant clarity issues, requires extensive clarification |
| 5-6 | Adequate clarity with some ambiguous sections |
| 7-8 | Good clarity, minor improvements needed |
| 9-10 | Excellent clarity, unambiguous, well-organized |

**Sub-Criteria**:
- Language precision (no "may", "could", "efficient", "user-friendly" without definition)
- Consistent terminology
- Clear structure and organization
- Appropriate level of abstraction
- Audience-appropriate communication

**Expert Weight**: Wiegers (40%), Adzic (30%), Cockburn (30%)

---

### Completeness Score (0-10)

**Definition**: How thoroughly the specification covers all necessary aspects

**Criteria**:
| Score | Description |
|-------|-------------|
| 0-2 | Major gaps, critical sections missing |
| 3-4 | Significant gaps affecting implementation |
| 5-6 | Covers basics, some gaps or TBD sections |
| 7-8 | Comprehensive coverage, minor gaps |
| 9-10 | Excellent coverage, exceeds requirements |

**Sub-Criteria**:
- All required sections present
- Functional requirements complete
- Non-functional requirements addressed
- Error handling and edge cases covered
- Integration points documented
- Operational requirements included

**Expert Weight**: Wiegers (30%), Nygard (25%), Newman (25%), Hohpe (20%)

---

### Testability Score (0-10)

**Definition**: How well the specification supports verification and testing

**Criteria**:
| Score | Description |
|-------|-------------|
| 0-2 | Untestable, no acceptance criteria |
| 3-4 | Minimal testability, vague criteria |
| 5-6 | Testable in parts, some concrete criteria |
| 7-8 | Good testability, clear acceptance criteria |
| 9-10 | Excellent testability, executable specifications |

**Sub-Criteria**:
- Acceptance criteria defined for each requirement
- Concrete examples provided (Specification by Example)
- Measurable success criteria
- Test scenarios identifiable
- Gherkin/BDD scenarios present
- Performance targets quantified

**Expert Weight**: Adzic (35%), Crispin (30%), Gregory (25%), Wiegers (10%)

---

### Consistency Score (0-10)

**Definition**: How internally consistent and coherent the specification is

**Criteria**:
| Score | Description |
|-------|-------------|
| 0-2 | Major contradictions, conflicting requirements |
| 3-4 | Significant inconsistencies |
| 5-6 | Minor inconsistencies, mostly coherent |
| 7-8 | Good consistency, rare issues |
| 9-10 | Excellent consistency, fully coherent |

**Sub-Criteria**:
- No contradictory requirements
- Consistent terminology throughout
- Aligned with referenced standards
- Cross-references accurate
- Version consistency
- Format consistency

**Expert Weight**: Fowler (30%), Wiegers (30%), Newman (20%), Hohpe (20%)

---

### Aggregate Quality Score

**Calculation**:
```
Overall Score = (Clarity × 0.25) + (Completeness × 0.30) + (Testability × 0.25) + (Consistency × 0.20)
```

**Quality Thresholds**:
| Score Range | Assessment | Recommendation |
|-------------|------------|----------------|
| 0.0 - 3.9 | Poor | Major revision required |
| 4.0 - 5.9 | Needs Improvement | Significant revisions recommended |
| 6.0 - 6.9 | Acceptable | Targeted improvements needed |
| 7.0 - 7.9 | Good | Minor refinements suggested |
| 8.0 - 10.0 | Excellent | Ready for implementation |

---

## Iterative Improvement Process

The spec-panel supports both single-pass and multi-iteration improvement workflows.

### Single Iteration Workflow

**Use Case**: Quick specification review with immediate recommendations

**Process**:
```
1. INPUT: Specification document
2. ANALYSIS: Expert panel review (selected mode)
3. SCORING: Quality metrics assessment
4. OUTPUT:
   - Expert insights and recommendations
   - Quality scores with evidence
   - Prioritized improvement list
```

**Command**: `/sc:spec-panel @spec.md`

---

### Multi-Iteration Workflow

**Use Case**: Progressive specification refinement through multiple review cycles

**Process**:
```
ITERATION 1:
  - Initial analysis and scoring
  - Identify critical gaps (severity: HIGH)
  - Generate improvement recommendations

ITERATION 2:
  - Review revised specification
  - Verify HIGH issues addressed
  - Identify remaining gaps (severity: MEDIUM)
  - Refine recommendations

ITERATION 3:
  - Final review
  - Verify MEDIUM issues addressed
  - Polish recommendations (severity: LOW)
  - Final quality assessment

COMPLETION:
  - Quality gates passed
  - All critical issues resolved
  - Final score meets threshold
```

**Command**: `/sc:spec-panel @spec.md --iterations 3`

---

### Quality Gates

**Gate 1: Critical Issues (Must Pass)**
- No undefined acceptance criteria for critical requirements
- No missing failure mode specifications
- No security vulnerabilities in specification
- All external dependencies documented

**Gate 2: High Issues (Should Pass)**
- All requirements have testable acceptance criteria
- Error handling documented for all flows
- Performance targets quantified
- Integration contracts specified

**Gate 3: Medium Issues (Recommended)**
- Concrete examples for complex behaviors
- Non-functional requirements complete
- Operational requirements documented
- Deployment specifications included

**Gate 4: Low Issues (Polish)**
- Terminology consistency
- Format consistency
- Cross-reference accuracy
- Documentation completeness

---

## MCP Integration Points

The spec-panel integrates with the SuperClaude MCP server ecosystem for enhanced analysis capabilities.

### Sequential MCP (Primary)

**Role**: Multi-step structured reasoning for complex specification analysis

**Integration Points**:
- Complex requirement dependency analysis
- Architecture decision evaluation
- Cross-cutting concern identification
- Hypothesis testing for specification completeness

**Activation**: Automatic for `--think`, `--think-hard`, `--ultrathink` flags

**Usage Pattern**:
```yaml
sequential_integration:
  analysis_depth:
    --think: "Standard analysis (~4K tokens)"
    --think-hard: "Deep analysis (~10K tokens)"
    --ultrathink: "Comprehensive analysis (~32K tokens)"
  coordination:
    - "Sequential provides structured reasoning"
    - "Context7 provides pattern reference"
    - "Results synthesized across experts"
```

---

### Context7 MCP (Secondary)

**Role**: Pattern and best practice reference for specification standards

**Integration Points**:
- IEEE/ISO specification standards lookup
- Industry best practice patterns
- Framework-specific specification templates
- Terminology and convention references

**Activation**: Automatic for standards-related queries

**Usage Pattern**:
```yaml
context7_integration:
  reference_types:
    - "IEEE 830 / ISO 29148 structure requirements"
    - "RFC 2119 keyword conventions"
    - "Gherkin syntax standards"
    - "Architecture documentation patterns"
  triggers:
    - "Standards compliance check"
    - "Template structure validation"
    - "Terminology verification"
```

---

### Persona Coordination

**Primary Auto-Activation**: Analyzer, Architect, QA personas from SuperClaude

**Coordination Pattern**:
```yaml
persona_coordination:
  analyzer_persona:
    role: "Root cause analysis for specification gaps"
    activation: "Critique mode, gap identification"
  architect_persona:
    role: "Architecture specification evaluation"
    activation: "Architecture focus, system design review"
  qa_persona:
    role: "Testing and quality specification review"
    activation: "Testing focus, acceptance criteria review"
  mentor_persona:
    role: "Educational guidance in Socratic mode"
    activation: "Socratic mode, learning contexts"
  scribe_persona:
    role: "Documentation quality assessment"
    activation: "Documentation completeness review"
```

---

## Output Format Templates

### Standard Format

**Use Case**: Default output for quick reviews

```markdown
# Specification Panel Analysis

**Document**: [Specification Name]
**Date**: [Analysis Date]
**Mode**: [Discussion/Critique/Socratic]
**Experts**: [Selected Expert List]

## Quality Assessment

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Clarity | X.X/10 | [Brief assessment] |
| Completeness | X.X/10 | [Brief assessment] |
| Testability | X.X/10 | [Brief assessment] |
| Consistency | X.X/10 | [Brief assessment] |
| **Overall** | **X.X/10** | [Overall assessment] |

## Key Findings

### Critical Issues (Must Address)
1. [Issue with evidence and recommendation]

### High Priority (Should Address)
1. [Issue with evidence and recommendation]

### Improvements (Recommended)
1. [Enhancement opportunity]

## Expert Insights

[Summary of key expert perspectives]
```

---

### Structured Format

**Use Case**: Detailed analysis with full expert breakdown

**Activation**: `--structured`

```markdown
# Specification Panel Analysis: Structured Report

**Document**: [Specification Name]
**Analysis Configuration**:
- Mode: [Discussion/Critique/Socratic]
- Focus: [Requirements/Architecture/Testing/Compliance]
- Depth: [Standard/Deep/Comprehensive]
- Experts: [Full list with roles]

---

## Section 1: Quality Metrics

### Clarity Analysis
**Score**: X.X/10
**Evidence**:
- [Specific clarity issue with citation]
- [Another issue with citation]
**Recommendations**:
- [Specific improvement]

### Completeness Analysis
**Score**: X.X/10
**Evidence**:
- [Specific completeness gap with citation]
**Recommendations**:
- [Specific addition needed]

### Testability Analysis
**Score**: X.X/10
**Evidence**:
- [Specific testability issue with citation]
**Recommendations**:
- [Specific acceptance criteria improvement]

### Consistency Analysis
**Score**: X.X/10
**Evidence**:
- [Specific consistency issue with citation]
**Recommendations**:
- [Specific correction needed]

---

## Section 2: Expert Panel Discussion

### WIEGERS (Requirements Engineering)
[Full analysis in authentic voice]

### ADZIC (Specification by Example)
[Full analysis building on Wiegers]

### NYGARD (Production Systems)
[Full analysis with operational focus]

[Continue for each selected expert]

---

## Section 3: Cross-Expert Synthesis

### Convergent Insights
[Areas of expert agreement]

### Productive Tensions
[Areas of expert disagreement with resolution]

### Blind Spots Identified
[Gaps no single expert fully captured]

---

## Section 4: Prioritized Recommendations

| Priority | Issue | Expert Source | Recommendation | Effort |
|----------|-------|---------------|----------------|--------|
| Critical | [Issue] | WIEGERS | [Action] | [Est.] |
| High | [Issue] | NYGARD | [Action] | [Est.] |
| Medium | [Issue] | ADZIC | [Action] | [Est.] |

---

## Section 5: Next Steps

1. [Immediate action]
2. [Short-term improvement]
3. [Long-term enhancement]
```

---

### Detailed Format

**Use Case**: Comprehensive analysis for formal review processes

**Activation**: `--verbose` or `--detailed`

```markdown
# Specification Panel Analysis: Comprehensive Report

## Metadata
- **Document**: [Full path and version]
- **Analysis Date**: [ISO 8601 timestamp]
- **Analysis Configuration**: [Full YAML config]
- **Execution Time**: [Duration]
- **Token Usage**: [Approximate]

---

## Executive Summary
[One-paragraph verdict with key findings]

---

## Quality Assessment Matrix

### Dimension: Clarity (Weight: 25%)

#### Sub-Dimension Scores
| Sub-Criteria | Score | Weight | Weighted |
|--------------|-------|--------|----------|
| Language Precision | X.X | 25% | X.XX |
| Terminology Consistency | X.X | 20% | X.XX |
| Structure/Organization | X.X | 25% | X.XX |
| Abstraction Level | X.X | 15% | X.XX |
| Audience Appropriateness | X.X | 15% | X.XX |
| **Clarity Total** | | | **X.XX** |

#### Evidence
[Detailed citations and analysis]

#### Recommendations
[Specific, actionable improvements]

[Repeat for each dimension]

---

## Expert Panel Proceedings

### Expert: Karl Wiegers
**Framework Applied**: Requirements Engineering Best Practices

#### Initial Assessment
[Detailed analysis]

#### Specific Findings
| Finding ID | Type | Location | Description | Severity |
|------------|------|----------|-------------|----------|
| W-001 | Gap | Section 3.1 | [Description] | High |
| W-002 | Ambiguity | Req R003 | [Description] | Medium |

#### Recommendations
[Detailed improvement suggestions]

[Repeat for each expert]

---

## Synthesis and Integration

### Theme Analysis
[Cross-expert theme identification]

### Conflict Resolution
[How expert disagreements were resolved]

### Gap Analysis
[Comprehensive gap identification]

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)
[Detailed action items]

### Phase 2: High Priority (Week 2-3)
[Detailed action items]

### Phase 3: Enhancements (Week 4+)
[Detailed action items]

---

## Appendices

### Appendix A: Full Expert Transcripts
[Complete expert analysis text]

### Appendix B: Citation Index
[All specification citations]

### Appendix C: Methodology Notes
[Analysis methodology details]
```

---

## Command Syntax and Flags

### Basic Command Structure

```bash
/sc:spec-panel [target] [options]
```

### Target Specification

```bash
# File path
/sc:spec-panel @path/to/specification.md

# Inline content (short specifications)
/sc:spec-panel "User authentication shall support OAuth 2.0 and SAML 2.0"

# Multiple files
/sc:spec-panel @spec1.md @spec2.md --compare
```

### Mode Flags

```bash
--mode discussion    # Default: collaborative analysis
--mode critique      # Adversarial challenge mode
--mode debate        # Alias for critique
--mode socratic      # Question-driven exploration
```

### Expert Selection

```bash
# Specific experts
--experts "wiegers,adzic,nygard"

# All experts
--experts "all"

# Auto-select based on content (default)
--experts "auto"
```

### Focus Area Flags

```bash
--focus requirements    # Requirements engineering focus
--focus architecture    # System architecture focus
--focus testing         # Testing and quality focus
--focus compliance      # Compliance and audit focus
```

### Analysis Depth Flags

```bash
--think           # Standard analysis (~4K tokens)
--think-hard      # Deep analysis (~10K tokens)
--ultrathink      # Comprehensive analysis (~32K tokens)
```

### Output Control Flags

```bash
--structured      # Structured output format
--verbose         # Detailed output format
--detailed        # Alias for verbose
--synthesis-only  # Only synthesis, skip full expert views
```

### Iteration Control

```bash
--iterations N    # Number of improvement iterations (1-5)
--loop            # Enable iterative improvement mode
```

### Quality Thresholds

```bash
--threshold 7.0   # Minimum quality score to pass
--strict          # Enforce all quality gates
```

---

## Integration with SuperClaude Framework

### Wave Mode Integration

The spec-panel supports wave-enabled operations for comprehensive specification analysis.

**Wave-Enabled Operations**:
- Comprehensive specification audit across multiple documents
- Multi-phase specification development with expert validation
- Large specification decomposition and analysis

**Wave Strategies**:
```yaml
wave_strategies:
  progressive: "Incremental specification refinement"
  systematic: "Methodical comprehensive analysis"
  adaptive: "Dynamic expert selection based on findings"
```

### Persona System Integration

**Auto-Activation Mapping**:
```yaml
analyzer_persona:
  triggers: ["investigate", "troubleshoot", "gap analysis"]
  spec_panel_role: "Root cause analysis for specification issues"

architect_persona:
  triggers: ["architecture", "design", "system"]
  spec_panel_role: "Architecture specification evaluation"

qa_persona:
  triggers: ["test", "quality", "validation"]
  spec_panel_role: "Testing specification review"

scribe_persona:
  triggers: ["document", "write", "clarity"]
  spec_panel_role: "Documentation quality assessment"
```

### Tool Orchestration

**Primary Tools**:
- Sequential MCP: Complex reasoning and analysis
- Context7 MCP: Standards and pattern lookup
- Read: Specification document access
- Grep: Pattern search in specifications
- TodoWrite: Improvement tracking

**Tool Selection Matrix**:
```yaml
tool_selection:
  initial_analysis:
    - Read: "Load specification document"
    - Sequential: "Structure analysis approach"
  expert_analysis:
    - Sequential: "Deep reasoning per expert"
    - Context7: "Standard reference lookup"
  synthesis:
    - Sequential: "Cross-expert integration"
  output:
    - Write: "Generate report"
```

---

## Quality Standards

### Analysis Fidelity

**Framework Authenticity**: Each expert maintains true-to-source methodology and voice

**Evidence Requirements**: All findings supported by specification citations

**Traceability**: Recommendations traceable to specific expert insights

### Output Quality

**Professional Standards**: Specification-grade analysis and communication

**Structured Clarity**: Organized output supporting decision-making

**Actionable Recommendations**: Specific, implementable improvements

---

## Appendix A: Expert Framework Cross-Reference

| Expert | Primary Works | Key Concepts | Typical Questions |
|--------|--------------|--------------|-------------------|
| Wiegers | Software Requirements | Requirement quality attributes | "Is this testable?" |
| Adzic | Specification by Example | Concrete examples, living docs | "Give me an example" |
| Cockburn | Writing Effective Use Cases | Actor-goal analysis | "Who is the actor?" |
| Fowler | Enterprise Patterns | DDD, architecture patterns | "What pattern applies?" |
| Nygard | Release It! | Stability patterns, resilience | "What if this fails?" |
| Newman | Building Microservices | Service boundaries, APIs | "What owns this data?" |
| Hohpe | Enterprise Integration | Messaging patterns | "Sync or async?" |
| Crispin | Agile Testing | Testing quadrants | "What's the test strategy?" |
| Gregory | More Agile Testing | ATDD, continuous testing | "Can we test this now?" |
| Hightower | Cloud Native | K8s, declarative config | "How is this deployed?" |

---

## Appendix B: Quality Dimension Mapping

| Dimension | Primary Experts | Secondary Experts | Key Indicators |
|-----------|-----------------|-------------------|----------------|
| Clarity | Wiegers, Adzic | Cockburn | Language precision, examples |
| Completeness | Wiegers, Nygard | Newman, Hohpe | Section coverage, edge cases |
| Testability | Adzic, Crispin | Gregory, Wiegers | Acceptance criteria, examples |
| Consistency | Fowler, Wiegers | Newman, Hohpe | Terminology, cross-refs |

---

## Appendix C: Mode Selection Guide

| Context | Recommended Mode | Expert Focus |
|---------|------------------|--------------|
| Initial review | Discussion | Auto-select |
| Pre-production | Critique | Nygard, Wiegers |
| Security-critical | Critique | Nygard, compliance focus |
| Team education | Socratic | Adzic, Gregory |
| Architecture review | Discussion | Fowler, Newman, Hohpe |
| Test strategy | Discussion | Crispin, Gregory, Adzic |

---

*Document generated from SuperClaude framework analysis - 2026-01-17*
