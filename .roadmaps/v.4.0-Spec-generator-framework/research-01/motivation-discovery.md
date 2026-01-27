# Motivation Discovery Methodology

## Purpose

This methodology helps identify the **underlying motivations** behind user requirements so we can propose **alternative approaches** that might achieve the same goal better. This is distinct from business objective analysis - the focus is understanding WHY a user wants something at the human level, enabling us to suggest solutions they may not have considered.

---

## Core Principle: Problem Space vs Solution Space

Before diving into techniques, understand this fundamental distinction:

| Aspect | Problem Space | Solution Space |
|--------|--------------|----------------|
| Focus | Customer needs, desires, pain points | Products, features, implementations |
| Question | "What are you trying to achieve?" | "How should we build it?" |
| Artifact | Job stories, outcomes, motivations | User stories, specs, wireframes |
| Flexibility | High - many solutions possible | Low - committed to approach |

**Key Insight**: Users often present **solutions** when asked what they need. Our job is to dig back into the **problem space** to understand the underlying motivation, then evaluate whether their proposed solution (or alternatives) best addresses it.

---

## Method 1: Jobs-to-be-Done (JTBD) Framework

### How It Works

JTBD teaches that "customers don't buy products - they hire them to do a job." The framework shifts focus from what users *do* to what they're trying to *accomplish*.

A "job" has three dimensions:
- **Functional**: The practical task (e.g., "organize my files")
- **Emotional**: How they want to feel (e.g., "feel in control")
- **Social**: How they want to be perceived (e.g., "appear professional")

### Core Technique: The Job Story

Replace traditional user stories with job stories:

| Format | Example |
|--------|---------|
| User Story | "As a user, I want to export to PDF so I can share reports" |
| Job Story | "When I need to present findings to stakeholders, I want to share polished reports so I can demonstrate progress and maintain credibility" |

The job story format: **"When [situation], I want to [motivation], so I can [outcome]"**

### Interview Questions

**Discovery Questions:**
1. "What were you trying to accomplish when you realized you needed [feature]?"
2. "Walk me through the last time you tried to do this. What happened?"
3. "What would success look like for you in this situation?"
4. "If you had a magic wand, what outcome would you create?"

**Dimension Questions:**
5. "How did it make you feel when [the problem occurred]?" (emotional)
6. "What did others think when you couldn't [accomplish the task]?" (social)
7. "What's the practical impact of not being able to do this?" (functional)

### The Four Forces of Progress

When users switch from one solution to another, four forces are at play:

```
PUSHING TOWARD CHANGE          PULLING BACK
----------------------         -----------------
[Push] Pain with current  -->  <-- [Habit] Comfort with existing
[Pull] Appeal of new      -->  <-- [Anxiety] Fear of change
```

**Questions to uncover forces:**
- "What's frustrating about how you do this today?" (Push)
- "What appeals to you about [proposed solution]?" (Pull)
- "What would you miss about your current approach?" (Habit)
- "What concerns you about changing?" (Anxiety)

### When Most Useful

- Early product discovery before solutions are defined
- Understanding why feature requests keep recurring
- Evaluating competing feature priorities
- Designing for new user segments

### Extracting Actionable Insights

1. **Identify the core job**: Strip away the solution language to find the underlying task
2. **Map the job dimensions**: Functional, emotional, social aspects
3. **Score current satisfaction**: How well do existing solutions address the job?
4. **Generate alternatives**: What other solutions could address this job?

**Example Transformation:**
- User request: "Add dark mode to the dashboard"
- Job discovery: "When working late at night, I want to reduce eye strain so I can work longer without discomfort"
- Alternatives revealed: Dark mode, auto-brightness, scheduled themes, reminder to take breaks, reduced blue light option

---

## Method 2: Five Whys Technique

### How It Works

Ask "why" iteratively (typically 5 times) to drill down from symptoms to root causes. Each answer becomes the subject of the next "why" question.

### Example Application

```
Request: "I need an export button on the report page"

Why 1: "Why do you need an export button?"
       "So I can send reports to my manager"

Why 2: "Why do you need to send reports to your manager?"
       "She needs to see our weekly progress"

Why 3: "Why does she need to see weekly progress?"
       "She presents it in the leadership meeting on Mondays"

Why 4: "Why does she present your data specifically?"
       "She doesn't have direct access to our metrics"

Why 5: "Why doesn't she have direct access?"
       "We never set up viewer permissions for leadership"

ROOT MOTIVATION: Manager needs visibility into team metrics
ALTERNATIVES:
- Direct dashboard access for leadership
- Automated scheduled reports
- Leadership-specific dashboard view
- Integration with existing reporting tools
```

### Question Variations

Soften "why" to reduce defensiveness:
- "What makes that important to you?"
- "What led you to that conclusion?"
- "Help me understand what's behind that"
- "What would that enable you to do?"
- "What happens if you can't do that?"

### When Most Useful

- Simple to moderately complex problems
- Quick initial investigation
- When the stated need seems surface-level
- When you suspect the request is a symptom, not the disease

### Limitations

- Can be overly linear (problems often have multiple causes)
- May feel confrontational if not handled carefully
- Stops at one root cause when multiple may exist
- Works best for single-cause problems

### Extracting Actionable Insights

1. **Document the chain**: Keep track of each level of "why"
2. **Identify the first non-obvious answer**: Usually the 2nd or 3rd why
3. **Validate the root**: Ask "If we solved this, would the original request still matter?"
4. **Branch alternatives**: At the root level, brainstorm multiple solution paths

---

## Method 3: Socratic Questioning

### How It Works

Use probing questions to help users examine their assumptions and clarify their thinking. Unlike Five Whys, Socratic questioning explores multiple dimensions simultaneously.

### Six Types of Socratic Questions

| Type | Purpose | Example Questions |
|------|---------|-------------------|
| **Clarification** | Define terms and meanings | "What do you mean by 'faster'?" / "Can you give an example?" |
| **Assumptions** | Expose hidden beliefs | "What are you assuming about users?" / "What if that wasn't true?" |
| **Evidence** | Examine reasoning basis | "What led you to believe that?" / "How do you know this?" |
| **Perspectives** | Consider alternatives | "How might someone else see this?" / "What's another way to look at it?" |
| **Implications** | Trace consequences | "If we do this, what else happens?" / "What are the effects?" |
| **Meta-questions** | Question the question | "Why is this the question we're asking?" / "What would a better question be?" |

### Application to Feature Requests

**Clarification Phase:**
- "When you say [term], what specifically does that mean to you?"
- "Can you show me a situation where this would help?"
- "Who else would be affected by this?"

**Assumption Testing:**
- "What has to be true for this solution to work?"
- "What are we assuming about user behavior?"
- "What if users don't use it the way we expect?"

**Alternative Exploration:**
- "What other ways could you achieve this outcome?"
- "If this feature didn't exist, what would you do instead?"
- "What's the simplest thing that could possibly work?"

### When Most Useful

- Complex, ambiguous requirements
- When assumptions seem untested
- Cross-functional discussions
- Challenging conventional thinking

### Extracting Actionable Insights

1. **Map assumptions**: List every assumption embedded in the request
2. **Test critical assumptions**: Which, if wrong, would invalidate the solution?
3. **Generate counter-examples**: Situations where the proposed solution fails
4. **Synthesize alternatives**: Solutions that work even if assumptions are wrong

---

## Method 4: Empathy Mapping

### How It Works

Create a visual representation of what users:
- **Say**: Verbatim quotes about their needs
- **Think**: Internal beliefs and motivations
- **Do**: Observable behaviors and actions
- **Feel**: Emotional states and reactions

Plus two additional dimensions:
- **Pains**: Frustrations, obstacles, fears
- **Gains**: Wants, needs, measures of success

### Interview Protocol

**Says (Direct quotes):**
- "Tell me about the last time you needed to [do the task]"
- "How would you describe this problem to a colleague?"

**Thinks (Unspoken motivations):**
- "What were you really hoping would happen?"
- "What concerns were running through your mind?"

**Does (Behaviors):**
- "Walk me through exactly what you did"
- "What workarounds have you tried?"

**Feels (Emotions):**
- "How did that make you feel?"
- "What was the most frustrating part?"

**Pains:**
- "What's the worst part of dealing with this?"
- "What keeps you up at night about this?"

**Gains:**
- "What would a perfect solution give you?"
- "How would you know if this was working?"

### When Most Useful

- New product or feature exploration
- Understanding user segments
- Team alignment on user needs
- Humanizing abstract requirements

### Extracting Actionable Insights

1. **Find contradictions**: Where Says differs from Does (actual vs stated behavior)
2. **Identify emotional drivers**: Feelings often reveal true motivation
3. **Map pains to gains**: Each pain implies a desired gain
4. **Prioritize by intensity**: Strongest feelings indicate deepest needs

---

## Method 5: Goal Decomposition (Means-Ends Analysis)

### How It Works

Decompose high-level goals into sub-goals using AND/OR trees, revealing alternative paths to achievement.

### Decomposition Types

**AND decomposition**: All sub-goals required
```
Goal: "Share report with team"
├── [AND] Compile data
├── [AND] Format presentation
└── [AND] Distribute to recipients
```

**OR decomposition**: Any sub-goal sufficient
```
Goal: "Distribute to recipients"
├── [OR] Email PDF attachment
├── [OR] Share dashboard link
├── [OR] Present in meeting
└── [OR] Post to shared workspace
```

### Application Process

1. **State the top-level goal** (what user wants to achieve)
2. **Ask "How?"** to decompose downward
3. **Ask "Why?"** to check upward consistency
4. **Mark AND vs OR** relationships
5. **Identify** where the proposed solution fits
6. **Explore** parallel OR branches as alternatives

### Example Decomposition

User request: "I need to export reports to Excel"

```
WHY? "Analyze data flexibly"
├── [AND] Access raw data
│   ├── [OR] Export to Excel <-- User's proposed solution
│   ├── [OR] API access to data
│   ├── [OR] Direct database query
│   └── [OR] In-app data exploration tools
├── [AND] Perform calculations
│   ├── [OR] Excel formulas
│   ├── [OR] Built-in analytics
│   └── [OR] BI tool integration
└── [AND] Visualize results
    ├── [OR] Excel charts
    ├── [OR] Enhanced in-app charts
    └── [OR] BI dashboard
```

**Insight**: User wants flexible data analysis. Excel export is ONE path. Others include better in-app analytics, BI integration, or API access.

### When Most Useful

- Understanding complex goals with multiple components
- Finding alternative solution paths
- Evaluating build vs integrate decisions
- Prioritizing among competing approaches

### Extracting Actionable Insights

1. **Locate the proposal**: Find where user's solution sits in the tree
2. **Climb up**: Verify the goal it serves
3. **Explore siblings**: What OR alternatives exist at the same level?
4. **Evaluate alternatives**: Which path best serves the root goal?

---

## Method 6: Outcome-Driven Innovation (ODI)

### How It Works

Focus on the **metrics customers use to measure success** rather than the solutions they describe. Identify "desired outcomes" - measurable criteria for job completion.

### Outcome Statement Structure

Format: **[Direction] + [Metric] + [Object of Control] + [Context]**

Examples:
- "Minimize the time it takes to generate a report"
- "Reduce the likelihood of errors in calculations"
- "Increase the ability to customize formatting"

### The Opportunity Algorithm

Score outcomes on two dimensions:
- **Importance**: How important is this outcome? (1-10)
- **Satisfaction**: How satisfied are you with current solutions? (1-10)

**Opportunity Score** = Importance + (Importance - Satisfaction)

High importance + low satisfaction = underserved need = opportunity

### Interview Process

1. **Map the job**: Identify the full job the user is trying to accomplish
2. **List outcomes**: What metrics define success for each job step?
3. **Quantify**: Score importance and satisfaction
4. **Identify gaps**: Find underserved outcomes

### When Most Useful

- Prioritizing among many potential features
- Quantifying opportunity size
- Validating whether a solution truly addresses user needs
- Finding innovation opportunities in mature markets

### Extracting Actionable Insights

1. **List all outcomes**: Every way the user measures success
2. **Score each**: Importance vs current satisfaction
3. **Rank by opportunity**: Highest scores = biggest gaps
4. **Design to outcomes**: Solutions should improve specific outcome metrics

---

## Method 7: Timeline Switch Analysis

### How It Works

Reconstruct the user's journey from first problem awareness to solution search, identifying the trigger events and decision moments that reveal true motivation.

### Timeline Phases

```
FIRST THOUGHT --> EVENT 1 --> EVENT 2 --> ... --> SWITCH MOMENT
(Problem awareness)  (Escalation)  (Investigation)  (Decision to change)
```

### Interview Protocol

**First Thought:**
- "When did you first realize this was a problem?"
- "What was happening in your work/life when this came up?"

**Events:**
- "What happened next?"
- "What made you decide to look for a solution?"
- "What did you try before [current request]?"

**Switch Moment:**
- "What was the final straw that made you seek a new solution?"
- "What convinced you that your current approach wasn't working?"

**Contextual Details:**
- "Where were you when you made this decision?"
- "Who else was involved or affected?"
- "What time of day/week/month was this?"

### The "Dumbing Up" Technique

Pretend confusion to get deeper explanation:
- "Wait, I'm confused. You said you were frustrated, but then you didn't do anything for two weeks. What made you finally act?"
- "Help me understand - if it was that important, why did you try [workaround] first?"

### When Most Useful

- Understanding purchase/adoption decisions
- Identifying trigger events that create urgency
- Discovering what actually motivates action (vs passive frustration)
- Learning from competitor switches

### Extracting Actionable Insights

1. **Identify trigger events**: What pushes users from passive to active?
2. **Map the journey**: Full timeline from awareness to action
3. **Find barriers**: What delayed action?
4. **Design for triggers**: Solutions that address trigger conditions

---

## Integrated Framework: The Motivation Discovery Process

### Phase 1: Surface the Request
- Capture the stated requirement verbatim
- Note any solution language embedded in the request
- Identify the requester and their context

### Phase 2: Explore the Job
Use JTBD questions to understand:
- What job is the user trying to accomplish?
- What are the functional, emotional, and social dimensions?
- What forces are pushing/pulling them toward change?

### Phase 3: Drill to Root
Use Five Whys and Socratic questioning to:
- Uncover assumptions
- Identify the root motivation
- Test whether the stated solution addresses the real need

### Phase 4: Map the Landscape
Use Goal Decomposition to:
- Break down the goal into components
- Identify alternative paths (OR branches)
- Locate where the proposed solution fits

### Phase 5: Quantify Outcomes
Use ODI to:
- Define success metrics
- Score importance vs satisfaction
- Identify underserved outcomes

### Phase 6: Generate Alternatives
Based on insights from all methods:
- List all possible solutions that address the root motivation
- Evaluate each against desired outcomes
- Identify non-obvious alternatives user may not have considered

### Phase 7: Validate and Propose
- Confirm understanding with the user
- Present alternatives with rationale
- Collaborate on best path forward

---

## Quick Reference: Question Bank

### Opening Questions
- "What are you ultimately trying to accomplish?"
- "Walk me through the last time you needed to do this"
- "What would success look like?"

### Deepening Questions
- "Why is that important to you?"
- "What happens if you can't do that?"
- "What have you tried already?"
- "What's the worst part of dealing with this today?"

### Assumption Questions
- "What would have to be true for this solution to work?"
- "What are you assuming about how users will behave?"
- "What if that assumption was wrong?"

### Alternative Questions
- "If this feature didn't exist, what would you do instead?"
- "What's the simplest thing that could possibly work?"
- "How might someone else approach this problem?"
- "What other solutions have you considered?"

### Validation Questions
- "If we solved [root motivation], would [original request] still matter?"
- "Is there anything else that would address this need?"
- "What would you be giving up with this approach?"

---

## Anti-Patterns to Avoid

### 1. Solution Anchoring
**Problem**: Accepting the user's proposed solution as the only option
**Fix**: Always dig to the underlying job before evaluating solutions

### 2. Stopping at Surface Why
**Problem**: Accepting the first "why" answer as the root cause
**Fix**: Keep asking until you reach something non-obvious

### 3. Leading Questions
**Problem**: Suggesting answers in your questions
**Fix**: Use open-ended, neutral language

### 4. Assumption Blindness
**Problem**: Sharing user's assumptions without testing them
**Fix**: Explicitly list and challenge assumptions

### 5. Single-Path Thinking
**Problem**: Only exploring one solution branch
**Fix**: Use goal decomposition to map all possible paths

### 6. Feature vs Outcome Confusion
**Problem**: Treating features as goals
**Fix**: Always ask "What outcome does this feature create?"

---

## Sources

- [Jobs to Be Done Theory - Christensen Institute](https://www.christenseninstitute.org/theory/jobs-to-be-done/)
- [Jobs to Be Done Theory and Frameworks Explained - GoPractice](https://gopractice.io/product/jobs-to-be-done-the-theory-and-the-frameworks/)
- [Jobs-to-be-Done (JTBD) Framework: 2025 Guide - GreatQuestion](https://greatquestion.co/blog/jobs-to-be-done)
- [Five Whys Tool for Root Cause Analysis - Atlassian](https://www.atlassian.com/team-playbook/plays/5-whys)
- [The 5 Whys Explained - Businessmap](https://businessmap.io/lean-management/improvement/5-whys-analysis-tool)
- [Socratic Questioning - Requirements Elicitation - Mastering Business Analysis](https://masteringbusinessanalysis.com/mba180-socratic-questioning/)
- [Socratic Method for Software Requirements - TigoSolutions](https://en.tigosolutions.com/how-to-analyze-software-requirements-like-socrates-7-smart-questions-every-analyst-should-ask-65373)
- [Empathy Mapping: The First Step in Design Thinking - NN/g](https://www.nngroup.com/articles/empathy-mapping/)
- [Empathy Map - Interaction Design Foundation](https://www.interaction-design.org/literature/article/empathy-map-why-and-how-to-use-it)
- [Goal-Oriented Requirements Engineering - University of Toronto](https://www.cs.toronto.edu/pub/eric/REFSQ98.html)
- [Problem Space vs. Solution Space - Productfolio](https://productfolio.com/problem-space-vs-solution-space/)
- [Understanding Customer Needs: Problem Space Vs. Solution Space - Productside](https://productside.com/understanding-customer-needs-problem-space-vs-solution-space/)
- [Outcome-Driven Innovation - Anthony Ulwick](https://anthonyulwick.com/outcome-driven-innovation/)
- [How to Apply Jobs to Be Done Using Outcome-Driven Innovation - airfocus](https://airfocus.com/blog/jobs-to-be-done-outcome-driven-innovation-ulwick/)
- [How to do a Jobs To Be Done Interview - Jason Evanish](https://jasonevanish.com/2014/04/23/how-to-do-a-jobs-to-be-done-interview/)
- [User Story Mapping - NN/g](https://www.nngroup.com/articles/user-story-mapping/)
- [Mapping User Stories in Agile - TechTarget](https://www.techtarget.com/searchsoftwarequality/tip/How-user-story-mapping-aids-requirements-gathering-in-Agile)
