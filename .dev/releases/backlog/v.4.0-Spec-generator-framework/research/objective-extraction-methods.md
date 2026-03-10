# Higher-Level Objective Extraction Methodologies

**Research Document for Spec Generator Framework v4.0**

*Research conducted: January 2026*

---

## Executive Summary

This research document explores proven methodologies for understanding the TRUE motivations and higher-level objectives behind user requests. The goal is to equip an AI specification generator with techniques to move beyond surface-level requirements to understand WHY users want what they are asking for.

### Key Findings

1. **Jobs-to-be-Done (JTBD)** provides the most robust framework for understanding user motivations by focusing on the "job" users are trying to accomplish rather than demographic characteristics or stated preferences.

2. **Socratic Questioning** offers six categories of probing questions that systematically uncover assumptions, clarify goals, and reveal hidden requirements.

3. **Design Thinking** emphasizes empathy and iterative problem framing, distinguishing between discovering needs and deriving requirements.

4. **The 5 Whys and Ladder of Abstraction** enable movement between specific requests and general objectives, uncovering root causes and broader goals.

5. **Value-Based Requirements Engineering** addresses the often-overlooked emotional and motivational dimensions of stakeholder needs.

### Recommended Integration Strategy

An AI spec generator should implement a **layered questioning approach**:
1. Start with context and situation understanding
2. Apply JTBD framework to identify the functional, emotional, and social jobs
3. Use Socratic questioning to probe assumptions and implications
4. Employ the Ladder of Abstraction to find the right level of problem framing
5. Generate "How Might We" statements to open solution space
6. Validate understanding through outcome-driven need statements

---

## 1. Jobs-to-be-Done Framework (JTBD)

### 1.1 Core Philosophy

The Jobs-to-be-Done framework shifts focus from customer attributes to the task they want to accomplish. As Tony Ulwick describes: "People buy products and services to get a job done."

**Key Insight**: Users do not buy products; they "hire" them to make progress in specific circumstances.

### 1.2 The Three Types of Jobs

| Job Type | Description | Example |
|----------|-------------|---------|
| **Functional Jobs** | The practical tasks users are trying to accomplish | "Organize my music collection for easy listening" |
| **Emotional Jobs** | How users want to feel or avoid feeling | "Feel in control of my schedule" |
| **Social Jobs** | How users want to be perceived by others | "Be seen as innovative in my industry" |

### 1.3 Job Story Format

The canonical job story format provides a structured way to capture user objectives:

```
When [situation/context],
I want to [motivation/action],
So I can [desired outcome/benefit].
```

**Examples**:
- When I am preparing for a client presentation, I want to quickly find relevant data, so I can appear knowledgeable and win the client's trust.
- When I am debugging a complex system, I want to trace the root cause systematically, so I can fix the issue permanently rather than applying band-aids.

### 1.4 Outcome-Driven Innovation (ODI)

Tony Ulwick's Outcome-Driven Innovation operationalizes JTBD through **Desired Outcome Statements**:

**Structure**: [Direction of improvement] + [Unit of measure] + [Object of control] + [Context]

**Examples**:
- "Minimize the time it takes to get the songs in the desired order for listening"
- "Minimize the likelihood of missing an important deadline"
- "Increase the ability to track changes across the system"

### 1.5 Job Mapping Process

A job map breaks down the customer's core functional job into discrete steps:

1. **Define** - Determine goals and plan approach
2. **Locate** - Gather required inputs and information
3. **Prepare** - Set up the environment for execution
4. **Confirm** - Verify readiness to proceed
5. **Execute** - Perform the core activity
6. **Monitor** - Track progress and status
7. **Modify** - Make adjustments as needed
8. **Conclude** - Finish and clean up

**Application**: For each step, identify 6-12 desired outcomes that users are trying to achieve.

### 1.6 Practical Questions for AI Implementation

**Initial Discovery Questions**:
- "What situation triggered your need for this?"
- "What are you ultimately trying to accomplish?"
- "How will you measure success?"
- "What happens if you cannot accomplish this?"

**Drilling into the Job**:
- "Walk me through what you are doing when this need arises"
- "What is the hardest part of accomplishing this today?"
- "What workarounds have you tried?"
- "How do you currently measure whether you have succeeded?"

---

## 2. Socratic Questioning Methodology

### 2.1 The Six Categories of Socratic Questions

Socratic questioning provides a systematic framework for uncovering deeper understanding through targeted inquiry.

#### Category 1: Clarifying Questions
**Purpose**: Ensure clear understanding of what is being said

| Question Pattern | Application |
|------------------|-------------|
| "What do you mean by [X]?" | Clarify ambiguous terms |
| "Can you give me an example?" | Make abstract concepts concrete |
| "How does this relate to [Y]?" | Establish connections |
| "Can you rephrase that?" | Verify understanding |

#### Category 2: Probing Assumptions
**Purpose**: Challenge unstated beliefs underlying the request

| Question Pattern | Application |
|------------------|-------------|
| "What are you assuming here?" | Surface hidden assumptions |
| "Is that always the case?" | Test universality |
| "What if the opposite were true?" | Challenge core beliefs |
| "Why do you think that assumption holds?" | Validate foundations |

#### Category 3: Probing Reasons and Evidence
**Purpose**: Understand the basis for beliefs and requests

| Question Pattern | Application |
|------------------|-------------|
| "Why do you think that is true?" | Understand reasoning |
| "What evidence supports this?" | Validate claims |
| "Are there reasons to doubt this?" | Identify weaknesses |
| "What would change your mind?" | Understand conviction level |

#### Category 4: Questioning Viewpoints and Perspectives
**Purpose**: Explore alternative viewpoints

| Question Pattern | Application |
|------------------|-------------|
| "How might others see this differently?" | Expand perspective |
| "What would [stakeholder] say about this?" | Consider other interests |
| "What are the strengths of the alternative view?" | Fair evaluation |
| "How could both views be valid?" | Seek synthesis |

#### Category 5: Probing Implications and Consequences
**Purpose**: Explore downstream effects and impacts

| Question Pattern | Application |
|------------------|-------------|
| "If we do this, what happens next?" | Trace implications |
| "How does this affect [X]?" | Identify ripple effects |
| "What are the risks of this approach?" | Assess downside |
| "What are the unintended consequences?" | Consider second-order effects |

#### Category 6: Questions About the Question
**Purpose**: Meta-level examination of the inquiry itself

| Question Pattern | Application |
|------------------|-------------|
| "Why is this question important?" | Validate relevance |
| "Is this the right question to ask?" | Challenge framing |
| "What question should we be asking instead?" | Reframe problem |
| "What does this question assume?" | Expose hidden premises |

### 2.2 The Power of "Why"

The simple question "Why?" is the most versatile follow-up question:
- Moves from vague to specific
- Moves from symptom to cause
- Moves from wants to needs
- Challenges status quo

**Best Practice**: Ask "Why?" 3-5 times to reach root motivations, but phrase tactfully to avoid seeming combative.

### 2.3 Practical Application for AI

**Question Sequence Strategy**:
1. Start with clarifying questions to establish shared understanding
2. Probe assumptions to identify unstated constraints
3. Ask about evidence to validate the problem exists
4. Explore implications to understand scope and impact
5. Use meta-questions to ensure you are solving the right problem

---

## 3. Design Thinking for Requirements

### 3.1 The Design Thinking Process

Design Thinking is a human-centered approach with five iterative stages:

```
EMPATHIZE --> DEFINE --> IDEATE --> PROTOTYPE --> TEST
    ^                                              |
    |______________________________________________|
                    (Iterate)
```

### 3.2 Key Distinction: Needs vs. Requirements

| Concept | Definition | Focus |
|---------|------------|-------|
| **User Needs** | Relate to people; express wants, beliefs, desires | The "Why" |
| **Requirements** | Technical specifications derived from needs | The "What" |

**Key Insight**: Design Thinking explicitly separates discovering needs from deriving requirements, preventing premature solution commitment.

### 3.3 Empathize Phase Techniques

#### Empathy Mapping
The four quadrants of empathy mapping:

```
+------------------+------------------+
|      SAYS        |      THINKS      |
| Direct quotes    | Beliefs, goals,  |
| from users       | aspirations      |
+------------------+------------------+
|      DOES        |      FEELS       |
| Observable       | Emotional state, |
| behaviors        | frustrations     |
+------------------+------------------+
```

**Application**: Look for inconsistencies between quadrants - these reveal hidden insights.

#### User Journey Mapping
Document the complete user experience:
1. **Stages**: What phases does the user go through?
2. **Actions**: What does the user do at each stage?
3. **Thoughts**: What is the user thinking?
4. **Emotions**: How does the user feel?
5. **Pain Points**: Where does friction occur?
6. **Opportunities**: Where can we improve?

### 3.4 Define Phase: Problem Statement Formulation

**Problem Statement Formula**:
```
[User persona] needs a way to [user need] because [insight/reason].
```

**Characteristics of Good Problem Statements**:
1. **Human-centered**: Focuses on people, not technology
2. **Broad enough**: Allows creative freedom in solutions
3. **Narrow enough**: Manageable scope
4. **Actionable**: Points toward solutions

### 3.5 "How Might We" (HMW) Questions

Transform problem statements into opportunity statements:

**Before**: "Users hate long checkout processes"
**After**: "How might we make online checkout faster and more enjoyable?"

**HMW Guidelines**:
- Broad enough for creative solutions
- Narrow enough for specific ideas
- Optimistic and possibility-focused
- Does not imply a specific solution

### 3.6 Practical Templates for AI Implementation

**Empathy Interview Script**:
```
1. "Tell me about the last time you [relevant activity]"
2. "Walk me through what happened step by step"
3. "What was the hardest part?"
4. "How did that make you feel?"
5. "What would have made it better?"
6. "If you had a magic wand, what would you change?"
```

**Problem Framing Template**:
```
Based on [user research/context],
We discovered that [user type]
Is struggling with [problem area]
Because [root cause/insight].
This matters because [impact/consequence].
```

---

## 4. Root Cause Analysis for Goals

### 4.1 The 5 Whys Technique

The Five Whys technique, developed by Sakichi Toyoda, iteratively asks "Why?" to drill down to root causes.

**Example for Goal Extraction**:

```
Request: "I need a faster reporting system"

Why do you need faster reports?
--> "So I can make decisions more quickly"

Why do you need to make decisions more quickly?
--> "Because market conditions change rapidly"

Why does that matter?
--> "Because slow decisions mean missed opportunities"

Why are missed opportunities a problem?
--> "Because our competitors are more agile"

Why is competitor agility a concern?
--> "Because we are losing market share"

ROOT OBJECTIVE: Improve competitive positioning by enabling faster
market response, with reporting being one enabler.
```

### 4.2 Applying 5 Whys to Goal Setting

The 5 Whys is not just for troubleshooting - it reveals deeper motivations behind objectives:

**Goal Discovery Application**:
1. Start with stated request
2. Ask "Why is this important?"
3. Continue asking "Why?" for each answer
4. Stop when you reach a fundamental value or unchangeable constraint
5. Use the deeper understanding to validate or reframe the original request

### 4.3 The Ladder of Abstraction

The Ladder of Abstraction, introduced by S.I. Hayakawa, provides a framework for moving between concrete specifics and abstract concepts.

```
MORE ABSTRACT (Why?)
        ^
        |   "Make life better"
        |   "Be more productive"
        |   "Save time"
        |   "Automate reporting"
        |   "Generate monthly reports automatically"
        v
MORE CONCRETE (How?)
```

**Navigation**:
- **Ask "Why?"** to move UP the ladder (more abstract, broader scope)
- **Ask "How?"** to move DOWN the ladder (more concrete, specific actions)

### 4.4 Finding the Right Level of Abstraction

**Too Abstract**: "Improve the human condition" - not actionable
**Too Concrete**: "Add a blue button on page 3" - no context for decisions
**Just Right**: Specific enough to guide solutions, abstract enough for creative freedom

**Test Question**: "Does this framing allow for multiple valid solutions while still constraining the problem space meaningfully?"

### 4.5 Practical Application for AI

**Abstraction Laddering Exercise**:
```
Given the user request: [REQUEST]

Moving UP (asking Why?):
- Why do you need this? --> [ANSWER 1]
- Why is that important? --> [ANSWER 2]
- Why does that matter? --> [ANSWER 3]

Moving DOWN (asking How?):
- How specifically would this work? --> [DETAIL 1]
- How would you use this? --> [DETAIL 2]
- How would you measure success? --> [DETAIL 3]

OPTIMAL FRAMING LEVEL: [Identified sweet spot]
```

---

## 5. Requirement Elicitation Techniques

### 5.1 Value-Based Requirements Engineering (VBRE)

VBRE addresses the "socio-political" issues often cited as problems in requirements engineering.

**The VME Framework**:

| Component | Definition | Examples |
|-----------|------------|----------|
| **Values** | Personal attitudes or long-term beliefs | "I believe in work-life balance" |
| **Motivations** | Psychological constructs related to personality | Achievement, affiliation, power |
| **Emotions** | Reactive responses to events | Anxiety about change, excitement about opportunity |

### 5.2 Stakeholder Analysis

**Stakeholder Categories**:
- **Primary**: Direct users of the system
- **Secondary**: Indirect users or beneficiaries
- **Tertiary**: People affected by the system's existence
- **Anti-stakeholders**: Those who may oppose the system

**Analysis Questions**:
1. Who are all the stakeholders?
2. What are their interests and motivations?
3. What are their expectations?
4. What power/influence do they have?
5. What conflicts exist between stakeholders?

### 5.3 Context Analysis

Understanding the environment in which the solution will operate:

**PESTLE Framework**:
- **P**olitical factors
- **E**conomic factors
- **S**ocial factors
- **T**echnological factors
- **L**egal factors
- **E**nvironmental factors

### 5.4 Interview Techniques for Hidden Needs

**Types of User Needs**:

| Need Type | Visibility | Discovery Method |
|-----------|------------|------------------|
| **Explicit** | Stated directly | Direct questions |
| **Implicit** | Assumed but unstated | Contextual inquiry |
| **Latent** | Unknown to user | Observation, prototyping |

**Techniques for Latent Need Discovery**:
1. **Ask for stories**: "Tell me about the last time..."
2. **Follow-up deeply**: Use the 5 Whys
3. **Look for workarounds**: What do users hack together?
4. **Observe discrepancies**: What users say vs. do
5. **The magic wand question**: "If you could change anything..."

### 5.5 The JTBD Interview Framework

**Progress Questions**: Uncover what improvement users seek
- "What were you trying to accomplish when you started looking for a solution?"
- "What progress do you want to make in your life/work?"

**Context Questions**: Reveal triggering situations
- "Walk me through what was happening when you realized you needed help"
- "What was the last straw that made you seek a solution?"

**Constraint Questions**: Dig into obstacles
- "What nearly stopped you from moving forward?"
- "What alternatives did you consider?"
- "What would make you switch to something else?"

---

## 6. Practical Question Templates

### 6.1 Initial Discovery Questions

**Understanding the Request**:
```
1. "What are you trying to accomplish with this [feature/system]?"
2. "Who will be using this and in what situations?"
3. "What does success look like for this project?"
4. "What happens if we do not solve this problem?"
```

**Understanding the Context**:
```
1. "What triggered this request? What changed recently?"
2. "How are you handling this today? What is not working?"
3. "What have you tried before? Why did it not work?"
4. "What constraints do we need to work within?"
```

### 6.2 Deepening Understanding

**Probing Motivations**:
```
1. "Why is this important to you/your organization?"
2. "What would be different in your life/work if this existed?"
3. "How would you prioritize this against other needs?"
4. "Who else cares about this? Why do they care?"
```

**Uncovering Hidden Needs**:
```
1. "What keeps you up at night about this area?"
2. "What is the hardest part of [relevant activity]?"
3. "If you had a magic wand, what would you change?"
4. "What do you wish you knew that you do not know now?"
```

### 6.3 Validating Understanding

**Confirmation Questions**:
```
1. "So if I understand correctly, you need to [summary]?"
2. "The underlying goal seems to be [goal]. Is that right?"
3. "Would solving [rephrased problem] address your needs?"
4. "What would I be missing if I focused only on [stated request]?"
```

**Challenge Questions**:
```
1. "What if we could not do [stated solution]? What else might work?"
2. "How would you know if this solution was successful?"
3. "What is the worst case if we get this wrong?"
4. "What assumptions are we making that might be wrong?"
```

### 6.4 Outcome Definition

**Success Criteria Questions**:
```
1. "How will you measure whether this is successful?"
2. "What metrics matter most to you?"
3. "In six months, what would make you say this was worth it?"
4. "What is the minimum viable outcome you would accept?"
```

---

## 7. Integration Strategy for Spec Generator

### 7.1 Recommended Questioning Flow

```
PHASE 1: SITUATION UNDERSTANDING
    |
    |--> What is the context and trigger?
    |--> Who are the stakeholders?
    |--> What are the current constraints?
    |
    v
PHASE 2: JOB IDENTIFICATION
    |
    |--> What job is the user trying to get done?
    |--> What are the functional, emotional, and social jobs?
    |--> What are the desired outcomes?
    |
    v
PHASE 3: ASSUMPTION PROBING
    |
    |--> What assumptions underlie this request?
    |--> What evidence supports these assumptions?
    |--> What might be wrong about our understanding?
    |
    v
PHASE 4: ABSTRACTION CALIBRATION
    |
    |--> Are we at the right level of abstraction?
    |--> What broader goal does this serve? (Why?)
    |--> What specific manifestations exist? (How?)
    |
    v
PHASE 5: VALIDATION AND FRAMING
    |
    |--> Confirm understanding with user
    |--> Generate "How Might We" statements
    |--> Define success criteria
    |
    v
PHASE 6: SPECIFICATION GENERATION
    |
    |--> Transform understanding into specifications
    |--> Include both explicit requirements and implicit needs
    |--> Document the "why" alongside the "what"
```

### 7.2 Adaptive Questioning Strategy

The AI should adapt its questioning depth based on:

| Factor | Low Depth | High Depth |
|--------|-----------|------------|
| Request Clarity | Very specific and detailed | Vague or ambiguous |
| Scope | Small, isolated change | System-wide or strategic |
| Stakeholder Complexity | Single user | Multiple stakeholders |
| Risk Level | Low impact if wrong | High impact if wrong |
| Novelty | Similar to past work | New territory |

### 7.3 Red Flags Requiring Deeper Probing

The AI should probe deeper when detecting:
- Solution statements disguised as requirements
- Vague success criteria
- Missing stakeholder perspectives
- Assumed constraints that may not be real
- Emotional language indicating hidden concerns
- Inconsistencies between stated needs and context
- Requests that seem disproportionate to stated problems

### 7.4 Output Format Recommendations

The spec generator should produce:

1. **User Story / Job Story**
   ```
   When [situation],
   I want to [motivation],
   So I can [outcome].
   ```

2. **Problem Statement**
   ```
   [User] needs a way to [need] because [insight].
   ```

3. **Desired Outcomes**
   ```
   - Minimize [metric] in context of [activity]
   - Maximize [metric] in context of [activity]
   ```

4. **How Might We Questions**
   ```
   - HMW help [user] achieve [outcome]?
   - HMW reduce [pain point] while [constraint]?
   ```

5. **Assumptions and Risks**
   ```
   We are assuming that:
   - [Assumption 1] - Evidence: [support]
   - [Assumption 2] - Risk if wrong: [impact]
   ```

6. **Success Criteria**
   ```
   This will be successful when:
   - [Measurable outcome 1]
   - [Measurable outcome 2]
   ```

---

## 8. Source References

### Jobs-to-be-Done Framework
- [ProductPlan: JTBD Framework Definition](https://www.productplan.com/glossary/jobs-to-be-done-framework/)
- [Strategyn: Jobs-to-be-Done Comprehensive Guide](https://strategyn.com/jobs-to-be-done/)
- [Thrv: Jobs-to-be-Done and Agile](https://www.thrv.com/blog/jobs-to-be-done-and-agile)
- [Designative: Using JTBD in Design Practice](https://www.designative.info/2025/09/16/using-jobs-to-be-done-to-elevate-your-design-and-research-practice/)
- [Agile Seekers: Applying JTBD to Tech Product Discovery](https://agileseekers.com/blog/applying-jobs-to-be-done-jtbd-framework-to-tech-product-discovery)
- [User Interviews: JTBD in UX Research](https://www.userinterviews.com/ux-research-field-guide-chapter/jobs-to-be-done-jtbd-framework)

### Socratic Questioning
- [Mastering Business Analysis: Socratic Questioning](https://masteringbusinessanalysis.com/mba180-socratic-questioning/)
- [Tigo Solutions: Socratic Method for Software Requirements](https://en.tigosolutions.com/how-to-analyze-software-requirements-like-socrates-7-smart-questions-every-analyst-should-ask-65373)
- [Bridging the Gap: Requirements Elicitation Questions](https://www.bridging-the-gap.com/what-questions-do-i-ask-during-requirements-elicitation/)
- [Practical Analyst: Most Valuable Questions](https://practicalanalyst.com/requirements-elicitation-most-valuable-questions/)

### Design Thinking
- [IxDF: Design Thinking Define Phase](https://www.interaction-design.org/literature/article/stage-2-in-the-design-thinking-process-define-the-problem-and-interpret-the-results)
- [MDPI: Design Thinking Challenges for Requirements Elicitation](https://www.mdpi.com/2078-2489/10/12/371)
- [AdaptiveUS: Incorporating Design Thinking into Elicitation](https://www.adaptiveus.com/blog/design-thinking-in-elicitation)
- [RE Magazine: Requirements Elicitation in Modern Product Discovery](https://re-magazine.ireb.org/articles/requirements-elicitation-in-modern-product-discovery)
- [IxDF: How Might We Technique](https://www.interaction-design.org/literature/article/define-and-frame-your-design-challenge-by-creating-your-point-of-view-and-ask-how-might-we)

### 5 Whys and Root Cause Analysis
- [BusinessMap: 5 Whys Explained](https://businessmap.io/lean-management/improvement/5-whys-analysis-tool)
- [Figma: How to Use the 5 Whys](https://www.figma.com/resource-library/what-are-the-5-whys/)
- [Atlassian: Complete Guide to 5 Whys](https://www.atlassian.com/team-playbook/plays/5-whys)
- [KaiNexus: 5 Whys for Root Cause Analysis and Goal Setting](https://blog.kainexus.com/continuous-improvement/5-whys)
- [Wikipedia: Five Whys](https://en.wikipedia.org/wiki/Five_whys)

### Ladder of Abstraction
- [Untools: Abstraction Laddering](https://untools.co/abstraction-laddering/)
- [Atomic Object: Problem Framing with Abstraction Ladder](https://spin.atomicobject.com/2020/07/05/problem-framing-abstraction-ladder/)
- [Daniel Stillman: Fundamental Problem Framing Tool](https://www.danielstillman.com/blog/abstraction-laddering-for-problem-framing)
- [UX Collective: Abstraction Laddering](https://uxdesign.cc/abstraction-laddering-the-most-fundamental-problem-framing-tool-ever-cf0fcbeca487)

### Requirements Engineering and Stakeholder Analysis
- [PMC: Value-Based Requirements Engineering](https://pmc.ncbi.nlm.nih.gov/articles/PMC6559156/)
- [SEBoK: Stakeholder Needs Definition](https://sebokwiki.org/wiki/Stakeholder_Needs_and_Requirements)
- [CMU: Goal-Oriented Requirements Engineering](https://www.cs.toronto.edu/pub/eric/REFSQ98.html)
- [Springer: Goal-Oriented Requirements Engineering Guided Tour](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

### Empathy Mapping and User Research
- [NN/g: Empathy Mapping](https://www.nngroup.com/articles/empathy-mapping/)
- [IxDF: Empathy Map Guide](https://www.interaction-design.org/literature/article/empathy-map-why-and-how-to-use-it)
- [NN/g: User Interviews 101](https://www.nngroup.com/articles/user-interviews/)
- [Specific App: User Interview Questions for JTBD](https://www.specific.app/blog/user-interview-goals-great-questions-for-jtbd-goals-that-uncover-true-user-motivations-1)

### Outcome-Driven Innovation
- [Wikipedia: Outcome-Driven Innovation](https://en.wikipedia.org/wiki/Outcome-Driven_Innovation)
- [Strategyn: Customer Needs Through JTBD Lens](https://strategyn.com/customer-needs-through-a-jobs-to-be-done-lens/)
- [Digital Leadership: ODI for JTBD](https://digitalleadership.com/blog/outcome-driven-innovation/)
- [Tony Ulwick: Jobs-to-be-Done Framework](https://jobs-to-be-done.com/jobs-to-be-done-a-framework-for-customer-needs-c883cbf61c90)

---

*Document generated for IBOpenCode Spec Generator Framework v4.0*
*Research methodology: Deep web research with multi-source synthesis*
