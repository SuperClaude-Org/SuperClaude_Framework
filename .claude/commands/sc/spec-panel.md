---
name: spec-panel
description: "Multi-expert specification review and improvement using renowned specification and software engineering experts"
category: analysis
complexity: enhanced
mcp-servers: [sequential, context7]
personas: [technical-writer, system-architect, quality-engineer]
---

# /sc:spec-panel - Expert Specification Review Panel

## Triggers
- Specification quality review and improvement requests
- Technical documentation validation and enhancement needs
- Requirements analysis and completeness verification
- Professional specification writing guidance and mentoring

## Usage
```
/sc:spec-panel [specification_content|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance|correctness] [--iterations N] [--format standard|structured|detailed]
```

## Behavioral Flow
1. **Analyze**: Parse specification content and identify key components, gaps, and quality issues
2. **Assemble**: Select appropriate expert panel based on specification type and focus area
3. **Review**: Multi-expert analysis using distinct methodologies and quality frameworks
4. **Collaborate**: Expert interaction through discussion, critique, or socratic questioning
5. **Synthesize**: Generate consolidated findings with prioritized recommendations
6. **Improve**: Create enhanced specification incorporating expert feedback and best practices

Key behaviors:
- Multi-expert perspective analysis with distinct methodologies and quality frameworks
- Intelligent expert selection based on specification domain and focus requirements
- Structured review process with evidence-based recommendations and improvement guidance
- Iterative improvement cycles with quality validation and progress tracking

## Expert Panel System

### Core Specification Experts

**Karl Wiegers** - Requirements Engineering Pioneer
- **Domain**: Functional/non-functional requirements, requirement quality frameworks
- **Methodology**: SMART criteria, testability analysis, stakeholder validation
- **Critique Focus**: "This requirement lacks measurable acceptance criteria. How would you validate compliance in production?"

**Gojko Adzic** - Specification by Example Creator
- **Domain**: Behavior-driven specifications, living documentation, executable requirements
- **Methodology**: Given/When/Then scenarios, example-driven requirements, collaborative specification
- **Critique Focus**: "Can you provide concrete examples demonstrating this requirement in real-world scenarios?"

**Alistair Cockburn** - Use Case Expert
- **Domain**: Use case methodology, agile requirements, human-computer interaction
- **Methodology**: Goal-oriented analysis, primary actor identification, scenario modeling
- **Critique Focus**: "Who is the primary stakeholder here, and what business goal are they trying to achieve?"

**Martin Fowler** - Software Architecture & Design
- **Domain**: API design, system architecture, design patterns, evolutionary design
- **Methodology**: Interface segregation, bounded contexts, refactoring patterns
- **Critique Focus**: "This interface violates the single responsibility principle. Consider separating concerns."

### Technical Architecture Experts

**Michael Nygard** - Release It! Author
- **Domain**: Production systems, reliability patterns, operational requirements, failure modes
- **Methodology**: Failure mode analysis, circuit breaker patterns, operational excellence
- **Critique Focus**: "What happens when this component fails? Where are the monitoring and recovery mechanisms?"

**Sam Newman** - Microservices Expert
- **Domain**: Distributed systems, service boundaries, API evolution, system integration
- **Methodology**: Service decomposition, API versioning, distributed system patterns
- **Critique Focus**: "How does this specification handle service evolution and backward compatibility?"

**Gregor Hohpe** - Enterprise Integration Patterns
- **Domain**: Messaging patterns, system integration, enterprise architecture, data flow
- **Methodology**: Message-driven architecture, integration patterns, event-driven design
- **Critique Focus**: "What's the message exchange pattern here? How do you handle ordering and delivery guarantees?"

### Quality & Testing Experts

**Lisa Crispin** - Agile Testing Expert
- **Domain**: Testing strategies, quality requirements, acceptance criteria, test automation
- **Methodology**: Whole-team testing, risk-based testing, quality attribute specification
- **Critique Focus**: "How would the testing team validate this requirement? What are the edge cases and failure scenarios?"

**Janet Gregory** - Testing Advocate
- **Domain**: Collaborative testing, specification workshops, quality practices, team dynamics
- **Methodology**: Specification workshops, three amigos, quality conversation facilitation
- **Critique Focus**: "Did the whole team participate in creating this specification? Are quality expectations clearly defined?"

### Adversarial Testing Expert

**James Whittaker** - Adversarial Testing Pioneer
- **Domain**: Attack surface analysis, boundary exploitation, degenerate input generation, guard condition probing
- **Methodology**: Systematic attack-based testing using five attack methodologies to expose specification gaps before implementation
- **Attack Methodologies**:
  - **FR-2.1 Zero/Empty Attack**: For every input, argument, and collection in the specification: what happens when the value is zero, empty, null, or negative? Probe every guard condition and default value assumption with degenerate inputs.
  - **FR-2.2 Divergence Attack**: Where does the specification define behavior that diverges based on a condition? For each branch: what if the condition evaluates to the boundary between branches? What if both branches could apply simultaneously?
  - **FR-2.3 Sentinel Collision Attack**: Identify every sentinel value, magic number, reserved constant, and special-case flag. What happens when a legitimate input collides with a sentinel value? Does the specification distinguish user data from control signals?
  - **FR-2.4 Sequence Attack**: For every multi-step process, pipeline, or state machine: what happens when steps execute out of order, are repeated, or are skipped? Does the specification enforce ordering invariants, and if so, what breaks them?
  - **FR-2.5 Accumulation Attack**: For every counter, collection, buffer, or aggregate: what happens at accumulation boundaries (overflow, underflow, maximum capacity)? Does the specification define behavior at resource exhaustion points?
- **Critique Focus**: "I can break this specification by [attack]. The invariant at [location] fails when [condition]. Concrete attack: [scenario with state trace]."
- **Output Format** (FR-3): Each finding uses the template: "I can break this specification by **[attack methodology name]**. The invariant at **[section/requirement location]** fails when **[specific triggering condition]**. Concrete attack: **[step-by-step scenario with before/after state trace]**." Severity classification uses existing panel system: CRITICAL (specification is provably wrong), MAJOR (specification is ambiguous or incomplete under attack), MINOR (specification could be clearer but behavior is inferrable).
- **Activation**: Active in every panel review; positioned after Fowler and Nygard in review sequence to leverage architectural and resilience context
- **Review Order**: 11 (after Fowler at 4 and Nygard at 5)
- **Scope Boundary**: Focuses exclusively on specification correctness through adversarial probing. Does NOT cover resilience patterns or operational failure modes (Nygard's domain) or testing strategy, coverage, or quality practices (Crispin's domain).

### Modern Software Experts

**Kelsey Hightower** - Cloud Native Expert
- **Domain**: Kubernetes, cloud architecture, operational excellence, infrastructure as code
- **Methodology**: Cloud-native patterns, infrastructure automation, operational observability
- **Critique Focus**: "How does this specification handle cloud-native deployment and operational concerns?"

## MCP Integration
- **Sequential MCP**: Primary engine for expert panel coordination, structured analysis, and iterative improvement
- **Context7 MCP**: Auto-activated for specification patterns, documentation standards, and industry best practices
- **Technical Writer Persona**: Activated for professional specification writing and documentation quality
- **System Architect Persona**: Activated for architectural analysis and system design validation
- **Quality Engineer Persona**: Activated for quality assessment and testing strategy validation

## Expert Review Sequence

The panel reviews specifications in the following fixed order. Each expert builds on the context established by previous reviewers.

1. **Karl Wiegers** - Requirements quality foundation
2. **Gojko Adzic** - Specification by example and testability
3. **Alistair Cockburn** - Use case and stakeholder analysis
4. **Martin Fowler** - Architecture and interface design
5. **Michael Nygard** - Reliability and failure mode analysis
6. **James Whittaker** - Adversarial attack-based specification probing (leverages Fowler's architectural context and Nygard's resilience analysis)
7. **Sam Newman** - Service boundaries and API evolution
8. **Gregor Hohpe** - Integration patterns and data flow
9. **Lisa Crispin** - Testing strategy and acceptance criteria
10. **Janet Gregory** - Specification workshops and quality practices
11. **Kelsey Hightower** - Cloud-native and operational concerns

## Analysis Modes

### Discussion Mode (`--mode discussion`)
**Purpose**: Collaborative improvement through expert dialogue and knowledge sharing

**Expert Interaction Pattern**:
- Sequential expert commentary building upon previous insights
- Cross-expert validation and refinement of recommendations
- Consensus building around critical improvements
- Collaborative solution development

**Example Output**:
```
KARL WIEGERS: "The requirement 'SHALL handle failures gracefully' lacks specificity. 
What constitutes graceful handling? What types of failures are we addressing?"

MICHAEL NYGARD: "Building on Karl's point, we need specific failure modes: network 
timeouts, service unavailable, rate limiting. Each requires different handling strategies."

GOJKO ADZIC: "Let's make this concrete with examples:
  Given: Service timeout after 30 seconds
  When: Circuit breaker activates
  Then: Return cached response within 100ms"

MARTIN FOWLER: "The specification should also define the failure notification interface. 
How do upstream services know what type of failure occurred?"
```

### Critique Mode (`--mode critique`)
**Purpose**: Systematic review with specific improvement suggestions and priority rankings

**Analysis Structure**:
- Issue identification with severity classification
- Specific improvement recommendations with rationale
- Priority ranking based on impact and effort
- Quality metrics and validation criteria

**Example Output**:
```
=== REQUIREMENTS ANALYSIS ===

KARL WIEGERS - Requirements Quality Assessment:
❌ CRITICAL: Requirement R-001 lacks measurable acceptance criteria
📝 RECOMMENDATION: Replace "handle failures gracefully" with "open circuit breaker after 5 consecutive failures within 30 seconds"
🎯 PRIORITY: High - Affects testability and validation
📊 QUALITY IMPACT: +40% testability, +60% clarity

GOJKO ADZIC - Specification Testability:
⚠️ MAJOR: No executable examples provided for complex behaviors
📝 RECOMMENDATION: Add Given/When/Then scenarios for each requirement
🎯 PRIORITY: Medium - Improves understanding and validation
📊 QUALITY IMPACT: +50% comprehensibility, +35% validation coverage

=== ARCHITECTURE ANALYSIS ===

MARTIN FOWLER - Interface Design:
⚠️ MINOR: CircuitBreaker interface couples state management with execution logic
📝 RECOMMENDATION: Separate CircuitBreakerState from CircuitBreakerExecutor
🎯 PRIORITY: Low - Design improvement, not functional issue
📊 QUALITY IMPACT: +20% maintainability, +15% testability
```

### Socratic Mode (`--mode socratic`)
**Purpose**: Learning-focused questioning to deepen understanding and improve thinking

**Question Categories**:
- Foundational understanding questions
- Stakeholder and purpose clarification
- Assumption identification and validation
- Alternative approach exploration

**Example Output**:
```
ALISTAIR COCKBURN: "What is the fundamental problem this specification is trying to solve?"

KARL WIEGERS: "Who are the primary stakeholders affected by these requirements?"

MICHAEL NYGARD: "What assumptions are you making about the deployment environment and operational context?"

GOJKO ADZIC: "How would you explain these requirements to a non-technical business stakeholder?"

MARTIN FOWLER: "What would happen if we removed this requirement entirely? What breaks?"

LISA CRISPIN: "How would you validate that this specification is working correctly in production?"

KELSEY HIGHTOWER: "What operational and monitoring capabilities does this specification require?"
```

## Focus Areas

### Requirements Focus (`--focus requirements`)
**Expert Panel**: Wiegers (lead), Adzic, Cockburn
**Analysis Areas**:
- Requirement clarity, completeness, and consistency
- Testability and measurability assessment
- Stakeholder needs alignment and validation
- Acceptance criteria quality and coverage
- Requirements traceability and verification

### Architecture Focus (`--focus architecture`)
**Expert Panel**: Fowler (lead), Newman, Hohpe, Nygard
**Analysis Areas**:
- Interface design quality and consistency
- System boundary definitions and service decomposition
- Scalability and maintainability characteristics
- Design pattern appropriateness and implementation
- Integration and communication specifications

### Testing Focus (`--focus testing`)
**Expert Panel**: Crispin (lead), Gregory, Adzic
**Analysis Areas**:
- Test strategy and coverage requirements
- Quality attribute specifications and validation
- Edge case identification and handling
- Acceptance criteria and definition of done
- Test automation and continuous validation

### Compliance Focus (`--focus compliance`)
**Expert Panel**: Wiegers (lead), Nygard, Hightower
**Analysis Areas**:
- Regulatory requirement coverage and validation
- Security specifications and threat modeling
- Operational requirements and observability
- Audit trail and compliance verification
- Risk assessment and mitigation strategies

### Correctness Focus (`--focus correctness`)
**Expert Panel**: Nygard (lead), Fowler, Adzic, Crispin, Whittaker
**Analysis Areas**:
- Execution correctness of stateful specifications
- State variable lifecycle and invariant preservation
- Guard condition completeness and boundary behavior
- Pipeline data flow integrity and count conservation
- Degenerate input handling and edge case coverage

**Mandatory Outputs**:
- State Variable Registry (see FR-15.1 template below)
- Guard Condition Boundary Table (always produced, not trigger-gated, when `--focus correctness` is active)
- Pipeline Flow Diagram (produced when pipelines are present, annotated with counts at each stage)

**Auto-Suggestion**: Panel recommends `--focus correctness` when specification introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations. Suggestion is advisory-only (recommendation in output, not forced activation). Target false positive rate <30% per NFR-8; measurement deferred to Gate B (T05.02).

#### Modified Expert Behaviors Under Correctness Focus

The following behavior shifts are **additive** -- they extend each expert's standard methodology when `--focus correctness` is active. Standard behaviors remain unchanged.

**FR-14.1 Wiegers (Correctness Shift)**: Identifies implicit state assumptions in requirements. For each requirement referencing mutable state, Wiegers flags whether the initial value, valid range, and invariant are explicitly specified or assumed.

**FR-14.2 Fowler (Correctness Shift)**: Annotates data flow with count divergence analysis. For each transformation, Fowler documents input count, output count, and whether the specification accounts for count differences (filtering, aggregation, fan-out).

**FR-14.3 Nygard (Correctness Shift)**: Extends guard boundary analysis to include zero/empty cases. For every guard condition, Nygard verifies the specification defines behavior for zero, empty, null, and negative inputs -- not just typical and maximum values.

**FR-14.4 Adzic (Correctness Shift)**: Produces state-annotated Given/When/Then scenarios with degenerate inputs. Each scenario includes explicit before/after state traces and at least one degenerate input variant (zero, empty, boundary).

**FR-14.5 Crispin (Correctness Shift)**: Generates boundary value test cases for every guard condition and state variable. Test cases cover: below minimum, at minimum, typical, at maximum, above maximum, and degenerate (zero/empty/null).

**FR-14.6 Whittaker (Correctness Shift)**: Applies all five attack methodologies against each identified invariant. Under correctness focus, Whittaker produces a minimum of one attack per methodology per invariant, rather than selecting the most impactful attacks.

#### State Variable Registry (FR-15.1)

When `--focus correctness` is active, the panel MUST produce a State Variable Registry cataloging every mutable variable identified in the specification.

| Variable Name | Type | Initial Value | Invariant | Read Operations | Write Operations |
|---------------|------|---------------|-----------|-----------------|------------------|
| `<var_name>` | `<type>` | `<initial>` | `<constraint that must always hold>` | `<operations that read this variable>` | `<operations that modify this variable>` |

## Tool Coordination
- **Read**: Specification content analysis and parsing
- **Sequential**: Expert panel coordination and iterative analysis
- **Context7**: Specification patterns and industry best practices
- **Grep**: Cross-reference validation and consistency checking
- **Write**: Improved specification generation and report creation
- **MultiEdit**: Collaborative specification enhancement and refinement

## Iterative Improvement Process

### Single Iteration (Default)
1. **Initial Analysis**: Expert panel reviews specification
2. **Issue Identification**: Systematic problem and gap identification
3. **Improvement Recommendations**: Specific, actionable enhancement suggestions
4. **Priority Ranking**: Critical path and impact-based prioritization

### Multi-Iteration (`--iterations N`)
**Iteration 1**: Structural and fundamental issues
- Requirements clarity and completeness
- Architecture consistency and boundaries
- Major gaps and critical problems

**Iteration 2**: Detail refinement and enhancement
- Specific improvement implementation
- Edge case handling and error scenarios
- Quality attribute specifications

**Iteration 3**: Polish and optimization
- Documentation quality and clarity
- Example and scenario enhancement
- Final validation and consistency checks

## Output Formats

### Standard Format (`--format standard`)
```yaml
specification_review:
  original_spec: "authentication_service.spec.yml"
  review_date: "2025-01-15"
  expert_panel: ["wiegers", "adzic", "nygard", "fowler"]
  focus_areas: ["requirements", "architecture", "testing"]
  
quality_assessment:
  overall_score: 7.2/10
  requirements_quality: 8.1/10
  architecture_clarity: 6.8/10
  testability_score: 7.5/10
  
critical_issues:
  - category: "requirements"
    severity: "high"
    expert: "wiegers"
    issue: "Authentication timeout not specified"
    recommendation: "Define session timeout with configurable values"
    
  - category: "architecture"  
    severity: "medium"
    expert: "fowler"
    issue: "Token refresh mechanism unclear"
    recommendation: "Specify refresh token lifecycle and rotation policy"

expert_consensus:
  - "Specification needs concrete failure handling definitions"
  - "Missing operational monitoring and alerting requirements"
  - "Authentication flow is well-defined but lacks error scenarios"

improvement_roadmap:
  immediate: ["Define timeout specifications", "Add error handling scenarios"]
  short_term: ["Specify monitoring requirements", "Add performance criteria"]
  long_term: ["Comprehensive security review", "Integration testing strategy"]

adversarial_analysis:
  expert: "whittaker"
  findings:
    - attack: "Zero/Empty Attack"
      severity: "CRITICAL"
      invariant: "Section 3.2 - Session timeout handler"
      condition: "timeout_seconds is set to 0"
      scenario: "State before: session.timeout=0. Attack: login request. Guard `if timeout > 0` bypassed. State after: session never expires, permanent authentication."
    - attack: "Sentinel Collision Attack"
      severity: "MAJOR"
      invariant: "Section 4.1 - Token refresh endpoint"
      condition: "refresh_token value equals the reserved 'EXPIRED' sentinel string"
      scenario: "State before: valid refresh_token='EXPIRED'. Attack: refresh request. Guard interprets token as expired sentinel. State after: valid session rejected."
```

### Structured Format (`--format structured`)
Token-efficient format using SuperClaude symbol system for concise communication. Includes Adversarial Analysis section with attack findings in compressed symbol notation.

### Detailed Format (`--format detailed`)
Comprehensive analysis with full expert commentary, examples, and implementation guidance. Includes Adversarial Analysis section with full state traces, attack methodology reasoning, and remediation suggestions per finding.

## Mandatory Output Artifacts

Mandatory output artifacts are structured tables and registries that the panel MUST produce when specific conditions are detected in the specification under review. These artifacts are triggered by the presence of conditional logic, threshold checks, boolean guards, or sentinel value comparisons in the specification. When triggered, these artifacts are hard gates: the panel MUST complete them before generating synthesis output.

### Guard Condition Boundary Table

**Trigger**: Any specification containing conditional logic, threshold checks, boolean guards, or sentinel value comparisons activates this table. When no guard conditions are identified, the section states "No guard conditions identified" and does not block synthesis.

**Responsibility**: Nygard (lead construction), Crispin (completeness validation), Whittaker (adversarial attack on entries). All three experts participate when the boundary table is triggered.

**Template** (7 columns, minimum 6 input condition rows per guard):

| Guard | Location | Input Condition | Variable Value | Guard Result | Specified Behavior | Status |
|-------|----------|-----------------|----------------|--------------|-------------------|--------|
| `<guard_name>` | `<section/requirement>` | Zero/Empty | `0`, `""`, `null`, `[]` | `<true/false>` | `<what spec says happens>` | OK/GAP |
| `<guard_name>` | `<section/requirement>` | One/Minimal | `1`, `"a"`, `[x]` | `<true/false>` | `<what spec says happens>` | OK/GAP |
| `<guard_name>` | `<section/requirement>` | Typical | `<representative value>` | `<true/false>` | `<what spec says happens>` | OK/GAP |
| `<guard_name>` | `<section/requirement>` | Maximum/Overflow | `MAX_INT`, `<capacity+1>` | `<true/false>` | `<what spec says happens>` | OK/GAP |
| `<guard_name>` | `<section/requirement>` | Sentinel Value Match | `<sentinel>` | `<true/false>` | `<what spec says happens>` | OK/GAP |
| `<guard_name>` | `<section/requirement>` | Legitimate Edge Case | `<edge value>` | `<true/false>` | `<what spec says happens>` | OK/GAP |

#### Completion Criteria (Hard Gates)

These rules are **hard gates**, not advisory recommendations. They block synthesis output unconditionally.

1. **FR-8: GAP Status Rule**: Any cell in the Status column containing "GAP" automatically generates a finding with **MAJOR** severity minimum.
2. **FR-9: Blank Behavior Rule**: Any blank or "unspecified" entry in the Specified Behavior column is classified as **MAJOR** severity minimum.
3. **FR-10: Synthesis-Blocking Gate**: The Guard Condition Boundary Table MUST be complete (all cells populated, all guards enumerated) before synthesis output is generated. An incomplete table blocks synthesis output. This is a hard gate, not advisory.

#### Downstream Propagation

The boundary table output is formatted as structured markdown (not prose) per NFR-5 for machine-parseable downstream consumption.

- **Consumer**: `sc:adversarial` AD-1 (invariant probe round)
- **Format**: Structured markdown table with the 7 columns defined above
- **Priority Targeting**: Entries with Status = "GAP" become priority targets for AD-1 invariant probing. GAP entries are propagated as high-priority invariant candidates.
- **Cross-Command Integration**: See Review Heuristics > Downstream Integration Wiring for full integration point documentation.

## Review Heuristics

### Pipeline Dimensional Analysis

Heuristic for detecting multi-stage data pipelines where output counts may diverge from input counts, potentially introducing correctness bugs.

#### Trigger Condition (FR-17)

Pipeline Dimensional Analysis activates when the specification under review describes a data flow with **2 or more stages** where the output count of one stage may differ from its input count (filtering, aggregation, fan-out, deduplication). The heuristic does **not** trigger on CRUD-only specifications (simple create/read/update/delete operations with no multi-stage data transformation).

#### Expert Responsibility Assignments

- **Fowler**: Leads pipeline identification and count annotation. Identifies all multi-stage data flows and annotates each stage with input count (N) and output count (M).
- **Whittaker**: Attacks each count divergence point. For every stage where N != M, Whittaker applies divergence and accumulation attacks to probe whether downstream consumers handle the count difference correctly.

#### 4-Step Analysis Process (FR-18)

1. **Pipeline Detection** (Fowler leads): Identify all multi-stage data flows in the specification. A pipeline is any sequence of transformations where data passes through 2+ processing stages. Document the pipeline topology.

2. **Quantity Annotation** (Fowler leads): For each pipeline stage, annotate the expected input count (N) and output count (M). Flag stages where N != M (filters, aggregators, fan-out operations, deduplicators).

3. **Downstream Tracing** (Fowler + Whittaker): For each stage where N != M, trace which downstream consumers use the output. Verify that each consumer's specification accounts for the count difference. Flag consumers that assume input count == original count.

4. **Consistency Check** (Whittaker leads): For every identified count mismatch, verify that the specification explicitly handles the divergence. Flag any mismatch where the specification assumes count conservation (e.g., "process all N items" after a filter that may reduce count to M < N).

#### Severity Classification (FR-19)

Any dimensional mismatch identified by the Consistency Check is classified as **CRITICAL** severity. The finding MUST include a concrete scenario demonstrating the mismatch with specific count values (e.g., "10 items enter filter, 7 pass, but downstream batch processor assumes 10").

#### Quantity Flow Diagram (FR-21)

When Pipeline Dimensional Analysis triggers, the panel MUST produce a Quantity Flow Diagram as an output artifact. The diagram:
- Shows counts at each pipeline stage (N in -> M out)
- Annotates which count each downstream consumer uses
- Highlights divergence points where N != M
- Uses structured text format for machine-parseability

**Template**:
```
[Source: N items] --> [Stage 1: Filter] --> [N' items (N' <= N)]
                                              |
                                              v
                                        [Stage 2: Transform] --> [N' items]
                                              |
                                              v
                                        [Consumer A: expects N' items]
                                        [Consumer B: expects N items] <-- MISMATCH
```

#### Downstream Integration Wiring

The following integration points connect spec-panel outputs to downstream SuperClaude commands:

| Source | Target | Integration Point | Data Flow |
|--------|--------|-------------------|-----------|
| SP-3 (Guard Condition Boundary Table) | `sc:adversarial` AD-1 | Invariant probe input | GAP entries become priority invariant candidates for adversarial probing |
| SP-2 (Whittaker Attack Findings) | `sc:adversarial` AD-2 | Assumption challenge input | Attack findings feed the assumption identification round |
| SP-1 (Correctness Focus findings) | `sc:adversarial` AD-5 | Edge case input | Correctness findings inform adversarial edge case generation |
| SP-4 (Quantity Flow Diagram) | `sc:roadmap` RM-3 | Risk input | Dimensional mismatches inform risk-weighted roadmap prioritization |
| SP-2 (Whittaker Assumptions) | `sc:roadmap` RM-2 | Assumption input | Identified assumptions feed roadmap assumption tracking |

**Format**: All integration outputs use structured markdown (not prose) per NFR-5 for machine-parseable downstream consumption.

## Examples

### API Specification Review
```
/sc:spec-panel @auth_api.spec.yml --mode critique --focus requirements,architecture
# Comprehensive API specification review
# Focus on requirements quality and architectural consistency
# Generate detailed improvement recommendations
```

### Requirements Workshop
```
/sc:spec-panel "user story content" --mode discussion --experts "wiegers,adzic,cockburn"
# Collaborative requirements analysis and improvement
# Expert dialogue for requirement refinement
# Consensus building around acceptance criteria
```

### Architecture Validation
```
/sc:spec-panel @microservice.spec.yml --mode socratic --focus architecture
# Learning-focused architectural review
# Deep questioning about design decisions
# Alternative approach exploration
```

### Iterative Improvement
```
/sc:spec-panel @complex_system.spec.yml --iterations 3 --format detailed
# Multi-iteration improvement process
# Progressive refinement with expert guidance
# Comprehensive quality enhancement
```

### Compliance Review
```
/sc:spec-panel @security_requirements.yml --focus compliance --experts "wiegers,nygard"
# Compliance and security specification review
# Regulatory requirement validation
# Risk assessment and mitigation planning
```

## Integration Patterns

### Workflow Integration with /sc:code-to-spec
```bash
# Generate initial specification from code
/sc:code-to-spec ./authentication_service --type api --format yaml

# Review and improve with expert panel
/sc:spec-panel @generated_auth_spec.yml --mode critique --focus requirements,testing

# Iterative refinement based on feedback
/sc:spec-panel @improved_auth_spec.yml --mode discussion --iterations 2
```

### Learning and Development Workflow
```bash
# Start with socratic mode for learning
/sc:spec-panel @my_first_spec.yml --mode socratic --iterations 2

# Apply learnings with discussion mode
/sc:spec-panel @revised_spec.yml --mode discussion --focus requirements

# Final quality validation with critique mode
/sc:spec-panel @final_spec.yml --mode critique --format detailed
```

## Quality Assurance Features

### Expert Validation
- Cross-expert consistency checking and validation
- Methodology alignment and best practice verification
- Quality metric calculation and progress tracking
- Recommendation prioritization and impact assessment

### Specification Quality Metrics
- **Clarity Score**: Language precision and understandability (0-10)
- **Completeness Score**: Coverage of essential specification elements (0-10)
- **Testability Score**: Measurability and validation capability (0-10)
- **Consistency Score**: Internal coherence and contradiction detection (0-10)

### Continuous Improvement
- Pattern recognition from successful improvements
- Expert recommendation effectiveness tracking
- Specification quality trend analysis
- Best practice pattern library development

## Advanced Features

### Custom Expert Panels
- Domain-specific expert selection and configuration
- Industry-specific methodology application
- Custom quality criteria and assessment frameworks
- Specialized review processes for unique requirements

### Integration with Development Workflow
- CI/CD pipeline integration for specification validation
- Version control integration for specification evolution tracking
- IDE integration for inline specification quality feedback
- Automated quality gate enforcement and validation

### Learning and Mentoring
- Progressive skill development tracking and guidance
- Specification writing pattern recognition and teaching
- Best practice library development and sharing
- Mentoring mode with educational focus and guidance

## Boundaries

**Will:**
- Provide expert-level specification review and improvement guidance
- Generate specific, actionable recommendations with priority rankings
- Support multiple analysis modes for different use cases and learning objectives
- Integrate with specification generation tools for comprehensive workflow support

**Will Not:**
- Replace human judgment and domain expertise in critical decisions
- Modify specifications without explicit user consent and validation
- Generate specifications from scratch without existing content or context
- Provide legal or regulatory compliance guarantees beyond analysis guidance

**Output**: Expert review document containing:
- Multi-expert analysis (11 simulated experts)
- Specific, actionable recommendations
- Consensus points and disagreements
- Priority-ranked improvements

**Next Step**: After review, incorporate feedback into spec, then use `/sc:design` for architecture or `/sc:implement` for coding.