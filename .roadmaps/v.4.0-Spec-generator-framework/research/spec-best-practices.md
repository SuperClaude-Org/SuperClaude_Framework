# Specification Generation Best Practices Research

## Executive Summary

This research document synthesizes industry-standard specification generation methodologies, optimized for AI/LLM consumption. The findings draw from established requirements engineering experts (Karl Wiegers, Gojko Adzic, Alistair Cockburn), industry standards (IEEE 830, ISO 29148, RFC 2119), modern product development methodologies (Amazon PR-FAQ, Shape Up, Google Design Docs), and emerging AI-optimized specification patterns.

### Key Findings

1. **Specification-First Development is Resurging**: The rise of AI code generation has reinvigorated the importance of detailed specifications. The pattern "intent -> spec -> plan -> execution" is becoming standard in AI-assisted development.

2. **SMART Requirements Remain Foundational**: Requirements that are Specific, Measurable, Attainable, Relevant, and Time-bound continue to be the gold standard for quality specifications.

3. **BDD Patterns Provide Optimal AI Consumption Format**: Given/When/Then structures create executable specifications that are both human-readable and machine-parseable.

4. **Structured Output Schemas Enable Consistent Implementation**: JSON Schema and YAML configurations provide the contract-based approach that LLMs need for reliable code generation.

5. **Quality Validation Must Be Built-In**: Testability, traceability, and completeness checks should be integrated into the specification process, not added afterward.

---

## 1. Requirements Engineering Methodologies

### 1.1 Karl Wiegers' Requirements Engineering Approach

Karl Wiegers, Principal Consultant with Process Impact and author of 14+ books on software development, has established foundational practices for requirements engineering.

#### Core Practices (from "Software Requirements Essentials" 2023)

Wiegers identifies 20 best practices organized into five areas:

**Practice #1: Define Business Objectives**
- Understand the business problems or opportunities the solution addresses
- Align all participants on key issues before building

**Practice #2: Understand What Users Need**
- Far too often, teams build features that go unused because they didn't understand the business situation
- Focus on user workflows and tasks, not just features

#### Key Principles

- **Iterative Precision**: Work breadth-first, from lower precision to higher precision
  - Level 1: Primary actor's name and goal
  - Level 2: Use case brief or main success scenario
  - Level 3: Extension conditions
  - Level 4: Extension handling steps

- **Spectrum Thinking**: "Either terminal position of a spectrum is almost always silly, and being somewhere in the middle is almost always more reasonable" - applies to Waterfall vs Agile debates

- **Requirements Constantly Change**: Build processes that accommodate evolution

**Sources**:
- [Software Requirements Essentials (O'Reilly)](https://www.oreilly.com/library/view/software-requirements-essentials/9780138190279/)
- [SE Radio 604: Karl Wiegers and Candase Hokanson](https://se-radio.net/2024/02/se-radio-604-karl-wiegers-and-candase-hokanson-on-software-requirements-essentials/)
- [6 More Important Requirements Practices - LinkedIn](https://www.linkedin.com/pulse/6-more-important-requirements-practices-karl-wiegers)

---

### 1.2 Gojko Adzic's Specification by Example

Gojko Adzic's "Specification by Example" (2011) has become a seminal work connecting requirements, testing, and living documentation.

#### Seven Key Process Patterns

1. **Deriving scope from goals** - Start with business objectives
2. **Specifying collaboratively** - Involve all stakeholders
3. **Illustrating using examples** - Concrete scenarios over abstract requirements
4. **Refining the specification** - Iterate to clarity
5. **Automating validation without changing specifications** - Keep specs readable
6. **Validating frequently** - Continuous verification
7. **Evolving a documentation system** - Living documentation

#### Four Main Benefits

1. Produces living, reliable documentation
2. Defines expectations clearly and makes validation efficient
3. Reduces rework
4. Assures delivery teams and stakeholders that software is fit for purpose

#### Relationship to BDD

Dan North described Specification by Example as "the closest I've seen to a 'BDD book' (as a treatment of methodology)."

Key distinction: BDD is a whole methodology that may include pull-based work models and outside-in design. Working with examples as specifications is a key pillar of BDD, but not all of it.

**Caution**: "I see far more people using G/W/T for test automation than to support BDD/SbE" - Seb Rose

**Sources**:
- [Specification by Example - Gojko Adzic](https://gojko.net/books/specification-by-example/)
- [Specification by Example, 10 years later](https://gojko.net/2020/03/17/sbe-10-years.html)
- [Interview and Book Review: Specification by Example - InfoQ](https://www.infoq.com/articles/specification-by-example-book/)

---

### 1.3 Alistair Cockburn's Use Case Methodology

Dr. Alistair Cockburn, co-author of the Agile Manifesto and named one of the "42 Greatest Software Professionals of All Times" (2020), created a goal-oriented use case practice.

#### Use Case Definition

"All the ways of using a system to achieve a particular goal for a particular user" - includes successful, challenged, and failure scenarios.

#### Core Concepts

1. **System of interest** - The boundary of what you're building
2. **Primary actor with a goal** - Who wants what
3. **Set of scenarios** - Multiple paths to the goal
4. **Use case collection** - Organizing scenarios

#### Template Structure

| Field | Description |
|-------|-------------|
| **Use Case Name** | Goal as a short active verb phrase |
| **Scope** | Black-box (internal hidden) or white-box (internal shown) |
| **Goal Level** | User-goal (preferred), summary, or subfunction |
| **Primary Actor** | Role played when interacting with system |
| **Stakeholders** | Who has interests in this use case |
| **Preconditions** | What must be true before starting |
| **Success Guarantee** | What is true after successful completion |
| **Main Success Scenario** | The happy path |
| **Extensions** | Alternative paths and error handling |

#### Action Step Types

1. **Interaction** - Between two actors (e.g., "Customer enters address")
2. **Validation** - Protects stakeholder interest (e.g., "System validates credentials")
3. **Internal Change** - Satisfies stakeholder (e.g., "System deducts amount")

#### Writing Guidelines

- Write something readable - casual, readable use cases are useful
- Work breadth-first, from lower to higher precision
- Capture actor's intention, not UI details

**Sources**:
- [Writing Effective Use Cases - Amazon](https://www.amazon.com/Writing-Effective-Cases-Alistair-Cockburn/dp/0201702258)
- [Use Case Template - Alistair Cockburn](https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm)
- [Use-Case Foundation - Jacobson & Cockburn (PDF)](https://alistaircockburn.com/Use%20Case%20Foundation.pdf)

---

### 1.4 SMART Criteria for Requirements

Originally introduced by George T. Doran (1981) for management objectives, SMART was adapted to requirements engineering by Mannion and Keepence (1995).

#### The SMART Acronym

| Letter | Original (Doran) | Requirements (Mannion & Keepence) |
|--------|------------------|-----------------------------------|
| S | Specific | Specific - clearly defines what is required |
| M | Measurable | Measurable - can be quantified and verified |
| A | Assignable | Attainable - achievable within constraints |
| R | Realistic | Relevant - aligned with business goals |
| T | Time-related | Time-bound - has clear deadlines |

#### Benefits

- Clarity in requirements reduces disputes with stakeholders
- Faster sign-off and turnaround time
- Better clarity for developers
- Clear expectations

#### SMART Requirements vs SMART Goals

- **SMART Goals**: Describe business outcomes (portfolio/OKR level)
- **SMART Requirements**: Describe what system/team must deliver (testable pass/fail)

They work together: Set the goal, then express work as SMART requirements for concrete testing.

**Impact**: Badly written requirements cause 50% of product defects and 80% of rework efforts.

**Sources**:
- [SMART Requirements - ACM SIGSOFT](https://dl.acm.org/doi/10.1145/224155.224157)
- [SMART Requirements PDF - TU Eindhoven](https://www.win.tue.nl/~wstomv/edu/2ip30/references/smart-requirements.pdf)
- [There is a SMART way to write software requirements - Medium](https://erivanramos.medium.com/there-is-a-smart-way-to-write-software-requirements-48add56d3972)

---

## 2. Industry Standard Formats

### 2.1 IEEE 830 / ISO/IEC/IEEE 29148

#### Evolution

- **IEEE 830-1998**: Original SRS standard (now superseded)
- **ISO/IEC/IEEE 29148:2011**: First international standard
- **ISO/IEC/IEEE 29148:2018**: Current standard

#### Document Types Defined

| Document | Abbreviation | Purpose |
|----------|--------------|---------|
| Stakeholder Requirements Specification | StRS | Business-level needs |
| System Requirements Specification | SyRS | System-level requirements |
| Software Requirements Specification | SRS | Software-specific requirements |

#### Standard SRS Structure (IEEE 830)

```
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions, Acronyms, Abbreviations
   1.4 References
   1.5 Overview

2. Overall Description
   2.1 Product Perspective
   2.2 Product Functions
   2.3 User Characteristics
   2.4 Constraints
   2.5 Assumptions and Dependencies

3. Specific Requirements
   3.1 External Interfaces
   3.2 Functions
   3.3 Performance Requirements
   3.4 Logical Database Requirements
   3.5 Design Constraints
   3.6 Software System Quality Attributes
```

**Sources**:
- [IEEE 830-1998 Standard](https://ieeexplore.ieee.org/document/720574)
- [ISO/IEC/IEEE 29148 Templates - ReqView](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
- [SRS-Template GitHub (Markdown)](https://github.com/jam01/SRS-Template)

---

### 2.2 RFC 2119 (MUST/SHOULD/MAY Keywords)

RFC 2119 (1997) by S. Bradner of Harvard University defines requirement level keywords used in technical specifications.

#### The Keywords

| Keyword | Synonyms | Meaning |
|---------|----------|---------|
| **MUST** | REQUIRED, SHALL | Absolute requirement |
| **MUST NOT** | SHALL NOT | Absolute prohibition |
| **SHOULD** | RECOMMENDED | Valid reasons may exist to ignore, but implications must be understood |
| **SHOULD NOT** | NOT RECOMMENDED | May be acceptable in particular circumstances |
| **MAY** | OPTIONAL | Truly optional; implementations must interoperate |

#### Usage Requirements

Include this boilerplate near the beginning:

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

#### Important Guidelines

- Use only where actually required for interoperation or limiting harmful behavior
- Do NOT use to impose methods when not required for interoperability
- Document security implications of not following recommendations
- Per RFC 8174: Only uppercase keywords indicate requirement levels

**Sources**:
- [RFC 2119 - IETF](https://datatracker.ietf.org/doc/html/rfc2119)
- [RFC 2119 in a nutshell](https://mtsknn.fi/blog/rfc-2119-in-a-nutshell/)
- [OASIS Keyword Guidelines](https://www.oasis-open.org/policies-guidelines/keyword-guidelines/)

---

### 2.3 Amazon Working Backwards / PR-FAQ

Amazon's PR-FAQ methodology, used since 2004, has produced AWS, Kindle, and Prime Video.

#### The Core Concept

"Start by defining the customer experience, then iteratively work backwards from that point until the team achieves clarity of thought around what to build."

#### PR-FAQ Structure

**Press Release (PR)**:
- Written as if product is launching today
- Describes product from customer's perspective
- Focuses on benefits and customer value
- Forces laser-focus on what matters to customers

**Frequently Asked Questions (FAQ)**:
- External FAQs: Customer questions and answers
- Internal FAQs: Implementation challenges, costs, risks
- Provides clear-eyed assessment of difficulty

#### Key Benefits

1. Forces clarity before code
2. Identifies features to invest in
3. Surfaces potential issues early
4. Saves time and money long-term
5. Aligns all stakeholders

#### The Process

- Not unusual to write 10+ drafts
- Meet with senior leaders 5+ times to iterate
- Held in "Narrative" meetings where attendees read before discussing
- Pitches that don't succeed are discarded (no backlog)

**Key Insight**: "Writing a press release is a forcing function to ensure the creator is focused on the customer."

**Sources**:
- [Working Backwards: The Amazon PR/FAQ](https://productstrategy.co/working-backwards-the-amazon-prfaq-for-product-innovation/)
- [Working Backwards PR/FAQ Instructions & Template](https://workingbackwards.com/resources/working-backwards-pr-faq/)
- [Putting Amazon's PR/FAQ to Practice - Commoncog](https://commoncog.com/putting-amazons-pr-faq-to-practice/)

---

### 2.4 Shape Up (Basecamp)

Basecamp's Shape Up methodology, documented in "Shape Up: Stop Running in Circles and Ship Work That Matters," provides a lightweight alternative to traditional agile.

#### Key Concepts

**Appetite (not Estimate)**:
- Estimates start with design, end with number
- Appetites start with number, end with design
- Used as creative constraint on design process
- Two sizes: Small Batch (1-2 weeks) or Big Batch (6 weeks)

**Shaping (not Specifying)**:
- Concrete enough that teams know what to do
- Abstract enough for teams to work out details
- Primarily design work, not specification
- Requires generalist skills or collaboration

**Pitch Components** (5 required ingredients):

| Component | Purpose |
|-----------|---------|
| Problem | Raw idea, use case, or motivation |
| Appetite | Time budget and solution constraints |
| Solution | Core elements in understandable form |
| Rabbit Holes | Details to avoid problems |
| No-gos | What's explicitly excluded |

**Betting Table**:
- Leadership decides which pitches to commit to
- Replaces long-term roadmaps and backlogs
- Once bet, team gets time and space without re-prioritization

**No Backlog**:
- Pitches that don't make the cut are discarded
- If important, will come up again
- Reduces backlog management overhead

**Sources**:
- [Shape Up - Basecamp](https://basecamp.com/shapeup)
- [Write the Pitch - Shape Up](https://basecamp.com/shapeup/1.5-chapter-06)
- [Shape Up Methodology Overview - Curious Lab](https://www.curiouslab.io/blog/what-is-basecamps-shape-up-method-a-complete-overview)

---

### 2.5 Google Design Docs

Google's design doc culture emphasizes trade-offs and long-term documentation value.

#### Purpose

- Define software designs before coding
- Document high-level implementation strategy
- Capture key design decisions
- Emphasize trade-offs considered during decisions

#### Key Components

| Section | Content |
|---------|---------|
| Context | Facts and background |
| Goals | What the design achieves |
| Non-goals | What's explicitly out of scope |
| Design | Proposed solutions with trade-offs |
| Alternatives Considered | Why other approaches weren't chosen |
| Cross-cutting Concerns | Security, privacy, monitoring |

#### Best Practices

**System-Context Diagrams**:
- Show system as part of larger technical landscape
- Help readers contextualize within familiar environment

**Explicit Scope**:
- Define non-scope: topics not covered that readers might expect
- Example: "This document does not describe the design for Project Froobus"

**Audience Declaration**:
- Specify target audience and prerequisite knowledge
- Example: "Assumes understanding of matrix multiplication and backpropagation"

**Use Diagrams Liberally**:
- Complex concepts explained visually
- Architecture diagrams, sequence diagrams, data flow charts

**Link Everything**:
- Design doc as central hub
- Link to related requirements, API specs, previous decisions

**Key Insight**: "The best engineers don't just ship code—they shape decisions. Design docs are how you do that."

**Sources**:
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Google Technical Writing - Documents](https://developers.google.com/tech-writing/one/documents)
- [Mastering Google Design Docs - Medium](https://medium.com/@alessandro.traversi/mastering-google-design-docs-a-comprehensive-guide-with-readme-md-template-a2706b57f64d)

---

## 3. BDD Patterns and Templates

### 3.1 Given/When/Then Format

Developed by Dan North and Chris Matts as part of Behavior-Driven Development.

#### Structure

```gherkin
Given [precondition/context]
When [action/trigger]
Then [expected outcome]
```

#### Detailed Breakdown

| Keyword | Purpose | Example |
|---------|---------|---------|
| Given | State of world before behavior | Given a logged-in user with admin role |
| When | The behavior being specified | When they click "Delete User" |
| Then | Expected changes from behavior | Then the user is removed from the system |
| And | Additional conditions (any section) | And an audit log entry is created |
| But | Negative conditions | But the deleted user's data is archived |

#### The Rule Keyword (2018)

```gherkin
Rule: Users can only delete accounts they have permission for

  Example: Admin deleting a regular user
    Given an admin user
    When they delete a regular user account
    Then the account is removed

  Example: Regular user attempting deletion
    Given a regular user
    When they try to delete another account
    Then they receive a permission denied error
```

**Sources**:
- [Given When Then - Martin Fowler](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Writing better Gherkin - Cucumber](https://cucumber.io/docs/bdd/better-gherkin/)
- [Gherkin Rules - Cucumber Blog](https://cucumber.io/blog/bdd/gherkin-rules/)

---

### 3.2 Best Practices for BDD Scenarios

#### Write Declarative, Not Imperative

**Bad (Imperative)**:
```gherkin
When I click the "Login" button
And I enter "user@example.com" in the email field
And I enter "password123" in the password field
And I click "Submit"
```

**Good (Declarative)**:
```gherkin
When I log in with valid credentials
```

#### One Scenario, One Behavior

- Look for single When-Then pair
- Multiple When-Thens indicate problem
- Each scenario tests one feature

#### Recommended Step Count

- Keep to single-digit steps (<10)
- 3-5 steps per example is ideal
- Long scenarios lose expressive power

#### Avoid UI Implementation Details

**Bad**:
```gherkin
When I click the blue "Submit" button in the header
```

**Good**:
```gherkin
When I submit my registration
```

#### Use Background for Common Setup

```gherkin
Background:
  Given a registered user
  And the user is logged in

Scenario: View profile
  When I navigate to my profile
  Then I see my account details
```

#### Write Scenarios Early

- Write before test code or implementation
- Helps define software behavior
- Removes uncertainty later
- Enables team agreement before coding

**Sources**:
- [BDD 101: Writing Good Gherkin - Automation Panda](https://automationpanda.com/2017/01/30/bdd-101-writing-good-gherkin/)
- [Cucumber Best Practices - BrowserStack](https://www.browserstack.com/guide/cucumber-best-practices-for-testing)
- [Best practices for scenario writing - SmartBear](https://support.smartbear.com/cucumberstudio/docs/tests/best-practices.html)

---

### 3.3 Living Documentation

Living Documentation connects executable specifications to actual system behavior.

#### Characteristics

- **Documentation**: Describes how application works in user-understandable terms
- **Living**: Updates automatically with code changes
- **Executable**: Each line connects to automation code

#### The Three Amigos / Specification Workshop

Collaborative meeting including:
1. Product Owner (the what)
2. Developer (the how)
3. Tester (the what-if)

Purpose: Trigger conversation and identify missing specifications

#### Benefits

1. **Always Current**: Automated scenarios prevent documentation drift
2. **Fast Feedback**: CI/CD integration provides immediate signals
3. **Shared Understanding**: All stakeholders contribute to specifications
4. **Regression Detection**: Changes breaking behavior discovered in minutes

#### Tooling

| Tool | Languages | Features |
|------|-----------|----------|
| Cucumber | Java, JS, Ruby, many others | Gherkin syntax, wide adoption |
| SpecFlow | .NET | Visual Studio integration |
| Behave | Python | Python-native BDD |
| Serenity BDD | Java/JVM | Rich reporting, living documentation |

**Sources**:
- [Living Documentation - Serenity BDD](https://serenity-bdd.github.io/docs/reporting/living_documentation)
- [BDD Automation: from executable specifications to automated tests - Manning](https://freecontent.manning.com/bdd-automation-from-executable-specifications-to-automated-tests/)
- [Behavior-Driven Development - AltexSoft](https://www.altexsoft.com/blog/behavior-driven-development-bdd-in-test-automation/)

---

### 3.4 Acceptance Criteria Formats

#### Format 1: Given/When/Then (Scenario-Oriented)

Best for: User interactions, end-to-end workflows

```
Scenario: [Explain scenario]
Given [how things begin]
When [action taken]
Then [outcome of taking action]
```

#### Format 2: Rule-Oriented (Checklist)

Best for: Complex components, validation rules

```
Acceptance Criteria:
- [ ] User must enter valid email format
- [ ] Password must be at least 8 characters
- [ ] System must send confirmation email within 5 minutes
- [ ] Account must be created in "pending" status
```

#### Combining Formats

```
User Story: As a customer, I want to reset my password so that I can regain access to my account

Acceptance Criteria (Rules):
- [ ] Reset link expires after 24 hours
- [ ] Previous password cannot be reused
- [ ] User receives email confirmation

Acceptance Criteria (Scenarios):
Scenario: Successful password reset
  Given a registered user
  When they request a password reset
  Then they receive an email with a reset link
```

#### Quality Characteristics

- **Specific**: Clear, no ambiguity
- **Measurable**: Quantifiable outcomes
- **Testable**: Translates to pass/fail tests
- **Understandable**: Plain language, no jargon

**Sources**:
- [80+ User Story Examples with Acceptance Criteria - Smartsheet](https://www.smartsheet.com/content/user-story-with-acceptance-criteria-examples)
- [Acceptance Criteria Examples - ProdPad](https://www.prodpad.com/blog/acceptance-criteria-examples/)
- [Acceptance Criteria Explained - Atlassian](https://www.atlassian.com/work-management/project-management/acceptance-criteria)

---

## 4. AI-Optimization Techniques

### 4.1 Spec-Driven Development (SDD)

The emergence of AI code generation has created a new paradigm: Spec-Driven Development.

#### The Core Pattern

```
Intent -> Spec -> Plan -> Execution
```

#### Why Specs Matter More for AI

"A vague prompt like 'add photo sharing to my app' forces the model to guess at potentially thousands of unstated requirements. The AI will make reasonable assumptions, and some will be wrong."

#### Best Practice: Brainstorm First

1. Describe the idea to the LLM
2. Ask it to iteratively ask questions
3. Flesh out requirements and edge cases
4. Compile into comprehensive spec.md containing:
   - Requirements
   - Architecture decisions
   - Data models
   - Testing strategy

#### Tool Categories (2024-2025)

| Category | Examples |
|----------|----------|
| AI-native IDEs | Cursor, Windsurf |
| Command-line tools | Claude Code, Aider |
| Integrated extensions | GitHub Copilot, Codeium |
| Enterprise platforms | AWS Kiro |

**Sources**:
- [Spec-driven development with AI - GitHub Blog](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Spec-Driven Development in 2025 - SoftwareSeni](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/)
- [Inside Spec-Driven Development - EPAM](https://www.epam.com/insights/ai/blogs/inside-spec-driven-development-what-githubspec-kit-makes-possible-for-ai-engineering)

---

### 4.2 Structured Output Schemas

LLMs work best when output format is precisely defined.

#### JSON Schema Approach

```json
{
  "type": "object",
  "properties": {
    "feature_name": {
      "type": "string",
      "description": "Name of the feature to implement"
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "priority": { "enum": ["must", "should", "could", "wont"] },
          "acceptance_criteria": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["id", "description", "priority"]
      }
    }
  },
  "required": ["feature_name", "requirements"]
}
```

#### YAML for Configuration

YAML advantages for AI specifications:
- More readable with clean, indentation-based structure
- Supports comments for documenting decisions
- Less syntax (no brackets/commas) reduces errors
- Native multi-line strings perfect for prompts

```yaml
feature:
  name: User Authentication
  description: |
    Implement secure user authentication with
    OAuth2 support and session management

requirements:
  - id: AUTH-001
    description: Users can log in with email/password
    priority: must
    acceptance_criteria:
      - Valid credentials return access token
      - Invalid credentials return 401 error
      - Failed attempts are rate-limited
```

#### API-Native vs Non-Native Approaches

| Approach | Pros | Cons |
|----------|------|------|
| API-Native (OpenAI Structured Outputs) | Guaranteed compliance, no post-processing | Vendor lock-in |
| Non-Native (Prompt + Parser) | Works with any model, full flexibility | Requires validation |

**Sources**:
- [Structured model outputs - OpenAI](https://platform.openai.com/docs/guides/structured-outputs)
- [The guide to structured outputs and function calling with LLMs - Agenta](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)
- [Using YAML Files for AI Agents - Empathy First Media](https://empathyfirstmedia.com/yaml-files-ai-agents/)

---

### 4.3 Prompt Engineering Patterns for Specifications

#### Chain-of-Thought (CoT) Prompting

Guide the model through step-by-step reasoning:

```
Before implementing, let's think through this step by step:
1. First, identify the core data models needed
2. Then, define the API endpoints
3. Next, consider edge cases and error handling
4. Finally, outline the test cases
```

#### Few-Shot Prompting for Specifications

Provide examples of desired specification format:

```
Here's an example of how we document requirements:

## REQ-001: User Login
**Priority**: Must
**Description**: Users authenticate with email and password
**Acceptance Criteria**:
- AC1: Valid credentials return JWT token
- AC2: Invalid credentials return 401 with error message
- AC3: Account locks after 5 failed attempts

Now, document the following requirement using the same format: [new requirement]
```

#### Self-Review Prompting

```
After generating the specification:
1. Check for completeness - are all scenarios covered?
2. Verify testability - can each requirement be tested?
3. Confirm consistency - do requirements contradict each other?
4. Validate clarity - is there any ambiguity?
```

#### Reduce Hallucinations

```
If you are unsure about something or context is missing, ask for clarification rather than making up an answer.
```

**Sources**:
- [How to write good prompts for generating code - Potpie Wiki](https://github.com/potpie-ai/potpie/wiki/How-to-write-good-prompts-for-generating-code-from-LLMs)
- [My LLM coding workflow - Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)
- [Using LLMs for Code Generation - PromptHub](https://www.prompthub.us/blog/using-llms-for-code-generation-a-guide-to-improving-accuracy-and-addressing-common-issues)

---

### 4.4 Open Agent Specification (Agent Spec)

Emerging standard for defining AI agent workflows in a framework-agnostic manner.

#### Core Concepts

```yaml
component_type: agent
name: specification-generator
description: Generates software specifications from requirements

inputs:
  - name: raw_requirements
    type: string
    description: Unstructured requirements input

outputs:
  - name: specification
    type: object
    schema:
      $ref: "#/schemas/Specification"

flows:
  - name: generate_spec
    nodes:
      - type: LLMNode
        prompt: |
          Analyze the requirements and generate a structured specification
      - type: ToolNode
        tool: validate_spec
```

#### Benefits

- Framework-agnostic portability
- Formal, interoperable definitions
- Reusable across different agent frameworks
- Schema-driven validation

**Sources**:
- [Agent Spec: Unified Agent Workflow Definition - Emergent Mind](https://www.emergentmind.com/topics/open-agent-specification-agent-spec)
- [Specification - Agent Skills](https://agentskills.io/specification)

---

## 5. Quality Framework Synthesis

### 5.1 Testability Criteria

IEEE Standard 1233 defines testability as: "The degree to which a requirement is stated in terms that permit establishment of test criteria and performance of tests to determine whether those criteria have been met."

#### Ten Attributes of Testable Requirements

1. **Specific** - One clear meaning
2. **Measurable** - Quantifiable success criteria
3. **Complete** - All necessary information included
4. **Consistent** - No contradictions
5. **Unambiguous** - Single interpretation possible
6. **Feasible** - Technically achievable
7. **Traceable** - Links to source and tests
8. **Verifiable** - Can be proven correct
9. **Independent** - Testable in isolation
10. **Prioritized** - Importance is clear

#### What to Avoid

- Irrelevant text that doesn't add understanding
- Problem descriptions instead of solutions
- Implementation details (unless constraints)
- Vague expressions ("and so on," "the like")
- Subjective terms ("usually," "fast," "user-friendly")
- Undefined functionality references

**Sources**:
- [Testing the Requirements - HackerNoon](https://hackernoon.com/testing-the-requirements-classifications-criteria-and-checklist)
- [Ten Attributes of a Testable Requirement - Prolifics Testing](https://www.prolifics-testing.com/news/ten-attributes-of-a-testable-requirement)
- [Best Practices Reviewing Requirements for Testability](https://www.softwaretestingmagazine.com/knowledge/best-practices-reviewing-requirements-for-testability/)

---

### 5.2 Completeness Checklist

#### Requirements Document Completeness

| Criterion | Check |
|-----------|-------|
| **Necessary** | Traces to user need |
| **Concise** | Minimal, no redundancy |
| **Feasible** | Attainable within constraints |
| **Testable** | Measurable success criteria |
| **Technology Independent** | Avoids "how to" unless constraint |
| **Unambiguous** | Clear, single interpretation |
| **Complete** | Function fully defined |

#### Six Validation Criteria

1. **Completeness** - All requirements defined, nothing missed
2. **Correctness** - Accurately reflects stakeholder needs
3. **Consistency** - No contradictions across documents
4. **Testability** - Test cases can be derived
5. **Traceability** - Links to origin (stakeholder, goal, regulation)
6. **Feasibility** - Can be implemented

#### Coverage Analysis

Ensure no requirements are overlooked:
- Forward traceability: Requirements -> Test cases
- Backward traceability: Test cases -> Requirements
- Bi-directional: Both directions verified

**Sources**:
- [Requirements Checklist - AcqNotes](https://acqnotes.com/acqnote/tasks/requirements-checklist)
- [6 Testing Requirements for Effective QA - QATestLab](https://blog.qatestlab.com/2011/05/07/6-basic-criteria-for-testing-requirements/)

---

### 5.3 Consistency Validation

#### Types of Consistency

| Type | Definition | Example Issue |
|------|------------|---------------|
| **Internal** | Within same document | Contradictory requirements |
| **Cross-functional** | Between teams | Different interpretations |
| **Temporal** | Across versions | Meaning drift over time |

#### Automated Consistency Checking

CASE tools can detect:
- Non-determinism
- Missing cases
- Type errors
- Circular definitions

#### LLM-Assisted Validation

Emerging approaches use LLMs for:
- Structured formalization of requirements
- Process-state consistency validation
- Automated consistency checks
- Bidirectional feedback loops

**Sources**:
- [AI Based Requirements Validation - V2 Solutions](https://www.v2solutions.com/whitepapers/ai-requirements-validation-quality-consistency-guide/)
- [LLM-Assisted Test-Driven Framework - IET Software](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/sfw2/6714956)

---

### 5.4 Traceability Requirements

#### Requirements Traceability Matrix (RTM)

| Requirement ID | Description | Test Case ID | Status | Notes |
|----------------|-------------|--------------|--------|-------|
| REQ-001 | User login | TC-001, TC-002 | Passed | |
| REQ-002 | Password reset | TC-003 | Pending | |

#### Traceability Types

1. **Forward**: Requirements -> Implementation -> Tests
2. **Backward**: Tests -> Implementation -> Requirements
3. **Bi-directional**: Complete coverage verification

#### Regulatory Compliance

RTMs required for:
- DO-178C (Aerospace)
- ISO 26262 (Automotive)
- FDA regulations (Medical devices)
- ISO 9001 (Quality management)

#### Impact on Quality

Research shows statistically significant relationship between traceability completeness and defect rates. Components with more complete traceability show fewer defects.

**Sources**:
- [Requirements Traceability Matrix - Perforce](https://www.perforce.com/resources/alm/requirements-traceability-matrix)
- [Ultimate Guide to RTM - Ketryx](https://www.ketryx.com/blog/the-ultimate-guide-to-requirements-traceability-matrix-rtm)
- [Requirements Traceability Matrix - Guru99](https://www.guru99.com/traceability-matrix.html)

---

## 6. Recommended Spec Structure

Based on the research findings, here is a recommended specification structure optimized for both human understanding and AI consumption.

### 6.1 Hybrid Specification Template

```yaml
# spec.yaml - Feature Specification

metadata:
  id: FEAT-001
  title: User Authentication System
  version: 1.0.0
  status: draft  # draft | review | approved | implemented
  author: [Author Name]
  created: 2025-01-17
  last_updated: 2025-01-17

# Business Context (Amazon Working Backwards style)
business_context:
  problem_statement: |
    Users currently cannot securely access their accounts,
    leading to security risks and poor user experience.

  customer_impact: |
    This feature enables 10,000+ daily users to securely
    access their personalized dashboards.

  success_metrics:
    - metric: Login success rate
      target: ">= 99.5%"
    - metric: Average login time
      target: "< 3 seconds"
    - metric: Security incidents
      target: "0 breaches"

# Appetite (Shape Up style)
appetite:
  time_budget: "2 weeks"
  team_size: "1 designer + 2 developers"
  scope_type: "small_batch"

# Requirements (SMART + RFC 2119 keywords)
requirements:
  - id: AUTH-001
    description: "System MUST authenticate users with email and password"
    priority: must
    rationale: "Core security requirement for all user access"
    acceptance_criteria:
      - given: "a registered user with valid credentials"
        when: "they submit login form"
        then: "they receive a valid JWT token"
      - given: "a user with invalid credentials"
        when: "they submit login form"
        then: "they receive a 401 error with message"
    testable: true
    verification_method: automated_test

  - id: AUTH-002
    description: "System SHOULD support OAuth2 providers (Google, GitHub)"
    priority: should
    rationale: "Reduces friction for users with existing accounts"
    acceptance_criteria:
      - given: "a user selecting Google login"
        when: "they complete OAuth flow"
        then: "account is created/linked and user is authenticated"
    testable: true
    verification_method: integration_test

  - id: AUTH-003
    description: "System MAY remember user devices for 30 days"
    priority: may
    rationale: "Convenience feature for trusted devices"
    acceptance_criteria:
      - given: "a user on a remembered device"
        when: "they visit the application"
        then: "they are automatically authenticated"
    testable: true
    verification_method: manual_test

# Technical Design (Google Design Doc style)
technical_design:
  overview: |
    JWT-based authentication with refresh token rotation.
    Passwords hashed using bcrypt with cost factor 12.

  system_context_diagram: "[Link to diagram]"

  data_models:
    - name: User
      fields:
        - name: id
          type: uuid
          required: true
        - name: email
          type: string
          required: true
          constraints: "unique, valid email format"
        - name: password_hash
          type: string
          required: true

  api_endpoints:
    - method: POST
      path: /auth/login
      request_body:
        email: string
        password: string
      response:
        access_token: string
        refresh_token: string
        expires_in: integer

  non_goals:
    - "Multi-factor authentication (separate feature)"
    - "Password complexity rules (handled by AUTH-005)"

# Rabbit Holes (Shape Up style)
rabbit_holes:
  - area: "Session management"
    concern: "Concurrent sessions across devices"
    mitigation: "Limit to 5 active sessions, oldest revoked"

  - area: "Token storage"
    concern: "XSS vulnerability with localStorage"
    mitigation: "Use httpOnly cookies for refresh tokens"

# No-Gos (Shape Up style)
no_gos:
  - "Social login beyond Google/GitHub this iteration"
  - "Passwordless/magic link authentication"
  - "Admin impersonation features"

# Traceability
traceability:
  parent_epic: "EPIC-001: User Management"
  child_tasks:
    - "TASK-001: Implement login endpoint"
    - "TASK-002: Create login UI component"
  test_cases:
    - "TC-AUTH-001: Valid login flow"
    - "TC-AUTH-002: Invalid credentials handling"
  documentation:
    - "API Reference: /docs/api/auth"
    - "Security Guidelines: /docs/security"
```

### 6.2 Key Principles Summary

| Principle | Source | Application |
|-----------|--------|-------------|
| Start with customer | Amazon PR-FAQ | Problem statement first |
| Time-box constraints | Shape Up | Appetite over estimates |
| Structured scenarios | BDD | Given/When/Then criteria |
| RFC 2119 keywords | IETF | MUST/SHOULD/MAY precision |
| Trade-off focus | Google Design Docs | Alternatives considered |
| Testability built-in | IEEE/Wiegers | Every requirement verifiable |
| Living documentation | Adzic/BDD | Specs that execute |

---

## 7. Source References

### Books and Publications

1. Wiegers, K., & Beatty, J. (2013). *Software Requirements* (3rd ed.). Microsoft Press.
2. Wiegers, K., & Hokanson, C. (2023). *Software Requirements Essentials*. Addison-Wesley.
3. Adzic, G. (2011). *Specification by Example*. Manning Publications.
4. Cockburn, A. (2000). *Writing Effective Use Cases*. Addison-Wesley.
5. Bryar, C., & Carr, B. (2021). *Working Backwards: Insights, Stories, and Secrets from Inside Amazon*. St. Martin's Press.
6. Singer, R. (2019). *Shape Up: Stop Running in Circles and Ship Work that Matters*. Basecamp.

### Standards

7. IEEE 830-1998. *IEEE Recommended Practice for Software Requirements Specifications*.
8. ISO/IEC/IEEE 29148:2018. *Systems and software engineering — Life cycle processes — Requirements engineering*.
9. RFC 2119. *Key words for use in RFCs to Indicate Requirement Levels*. IETF.
10. RFC 8174. *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words*. IETF.

### Online Resources

11. [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
12. [Shape Up - Basecamp](https://basecamp.com/shapeup)
13. [Cucumber BDD Documentation](https://cucumber.io/docs/bdd/)
14. [Martin Fowler - Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)
15. [Serenity BDD - Living Documentation](https://serenity-bdd.github.io/docs/reporting/living_documentation)

### AI-Specific Resources

16. [Spec-driven development with AI - GitHub Blog](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
17. [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
18. [Agent Spec: Open Agent Specification](https://www.emergentmind.com/topics/open-agent-specification-agent-spec)
19. [My LLM coding workflow going into 2026 - Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)

---

*Research compiled: January 2025*
*Document version: 1.0*
