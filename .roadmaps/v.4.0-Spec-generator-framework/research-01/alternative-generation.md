# Alternative Solution Generation Methodology

Research findings on techniques for generating alternative approaches once underlying motivations are understood.

## Executive Summary

This document synthesizes seven complementary methodologies for generating alternative solutions to requirements. The goal is to move beyond the first solution that comes to mind and systematically explore the solution space to find approaches that may better serve the underlying motivation.

**Key Insight**: The best alternative generation happens when we separate the *motivation* (why) from the *mechanism* (how). Once we understand why someone wants something, we can propose many different hows.

---

## 1. Lateral Thinking (Edward de Bono)

### Overview

Lateral thinking is about breaking out of established patterns of perception. Unlike vertical (logical) thinking that digs deeper into the same hole, lateral thinking digs holes in different places.

**Source**: [de Bono Group - Six Thinking Hats](https://www.debonogroup.com/services/core-programs/six-thinking-hats/)

### When to Use

- The obvious solution feels unsatisfying
- Stakeholders are stuck in one way of thinking
- Need to challenge assumptions about how things "should" work
- Looking for non-obvious connections

### Step-by-Step Process

1. **State the motivation clearly** - What outcome does the user actually need?
2. **Challenge assumptions** - List everything assumed about the solution space
3. **Random entry** - Introduce unrelated concepts to spark new connections
4. **Reversal** - What if we did the opposite?
5. **Analogy** - How do other domains solve similar problems?
6. **Fractionation** - Break the problem into smaller pieces and recombine

### Six Thinking Hats Application

Use hats to explore alternatives systematically:

| Hat | Color | Application to Alternatives |
|-----|-------|---------------------------|
| White | Facts | What data do we have about user needs? |
| Red | Emotion | How do users *feel* about current solutions? |
| Black | Caution | What could go wrong with each alternative? |
| Yellow | Benefits | What's the best case for each option? |
| Green | Creativity | What wild alternatives exist? |
| Blue | Process | How do we evaluate and choose? |

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Motivation Discovery**: User wants to identify individual contributors to trends

**Lateral Alternatives**:
- **Reversal**: Instead of breaking down existing view, create dedicated contributor view
- **Random entry**: "Restaurant menu" - What if contributors were browsable like menu items?
- **Fractionation**: Separate "see who" from "see contribution amount" - different UI for each
- **Challenge assumption**: Must it be in a tooltip? What about inline, overlay, or separate page?

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Motivation Fit | 40% | Does it achieve the underlying goal? |
| Usability | 25% | Is it intuitive to discover and use? |
| Complexity | 20% | Implementation and maintenance burden? |
| Novelty | 15% | Does it offer advantages over obvious solution? |

---

## 2. TRIZ Contradiction Resolution

### Overview

TRIZ (Theory of Inventive Problem Solving) is a systematic methodology developed by Genrich Altshuller from analyzing 40,000+ patents. It identifies patterns of invention and provides principles for resolving contradictions.

**Source**: [TRIZ Knowledge Base - Contradiction Matrix](https://wiki.matriz.org/knowledge-base/triz/problem-solving-tools-5890/contradictions/engineering-contradiction-5995/contradiction-matrix-6026/)

### When to Use

- Improving one aspect makes another worse (contradictions)
- Traditional trade-offs seem unavoidable
- Need systematic rather than random exploration
- Technical constraints seem insurmountable

### Types of Contradictions

1. **Technical Contradiction**: Improving parameter A worsens parameter B
   - Example: Adding more data to tooltips improves information but worsens readability

2. **Physical Contradiction**: Same parameter needs opposite values
   - Example: Tooltip needs to be detailed (for analysis) AND simple (for quick glance)

### Key TRIZ Principles for Software

From the 40 inventive principles, these are most applicable to software:

| Principle | Definition | Software Application |
|-----------|------------|---------------------|
| #1 Segmentation | Divide into independent parts | Modular features, progressive disclosure |
| #2 Taking Out | Extract the problematic part | Move complexity to dedicated views |
| #10 Preliminary Action | Pre-arrange for convenience | Pre-compute, cache, prefetch |
| #13 The Other Way Round | Invert the action | Pull vs push, user initiates vs system shows |
| #15 Dynamics | Allow adaptation to conditions | Responsive design, user preferences |
| #17 Another Dimension | Move to 2D, 3D, or time | Add depth, layers, or temporal navigation |
| #24 Intermediary | Use intermediate object | Proxy views, summary layers |
| #35 Parameter Change | Change properties | Different formats, densities, abstractions |

### Step-by-Step Process

1. **Identify the contradiction**
   - What do you want to improve?
   - What gets worse when you improve it?

2. **Formulate in TRIZ terms**
   - Map to TRIZ parameters (e.g., information quantity, ease of operation)

3. **Consult the matrix**
   - Find suggested principles at intersection

4. **Apply principles creatively**
   - Interpret each principle for your specific context

5. **Generate multiple solutions**
   - Each principle should yield 2-3 alternatives

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Contradiction Identified**:
- Improving: Information completeness (want developer details)
- Worsening: Ease of operation (tooltip becomes cluttered)

**TRIZ Principles Applied**:

| Principle | Alternative Generated |
|-----------|----------------------|
| #1 Segmentation | Show summary in tooltip, details on click |
| #2 Taking Out | Create separate "Contributors" panel |
| #13 Other Way Round | Let users request breakdown (not automatic) |
| #17 Another Dimension | Add time dimension - animate through contributors |
| #24 Intermediary | Show "3 contributors" with expand option |
| #35 Parameter Change | Use avatars instead of text for density |

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Contradiction Resolved | 35% | Does it truly resolve both sides? |
| Elegance | 25% | Is it a clean solution or a workaround? |
| Implementation | 25% | Can we build it with current tech? |
| User Mental Model | 15% | Does it match how users think? |

---

## 3. Design Thinking Divergent Ideation

### Overview

Design Thinking uses "How Might We" (HMW) questions to reframe problems as opportunities. The divergent phase deliberately generates many ideas before convergent evaluation.

**Sources**:
- [IDEO U - Design Thinking Process](https://www.ideou.com/blogs/inspiration/design-thinking-process)
- [Interaction Design Foundation - How Might We](https://www.interaction-design.org/literature/topics/how-might-we)
- [NN/g - How Might We Questions](https://www.nngroup.com/articles/how-might-we-questions/)

### When to Use

- Need volume of ideas (quantity over quality initially)
- Want to involve diverse stakeholders
- Problem is human-centered, not purely technical
- Need to escape solution fixation

### HMW Question Crafting

The power comes from three psychological shifts:
- **Optimism**: "might" signals possibility without pressure
- **Framing**: Questions invite inquiry and divergent thinking
- **Focus**: Creates boundaries without over-constraining

**Good HMW Patterns**:
- "How might we help [user] achieve [goal]?"
- "How might we make [action] more [quality]?"
- "How might we eliminate the need for [current solution]?"

**Anti-Patterns** (too constrained):
- "How might we add X to Y?" (embeds solution)
- "How might we improve the tooltip?" (assumes mechanism)

### Step-by-Step Process

1. **Reframe as HMW** (5 min)
   - Generate 5-10 different HMW questions from the motivation
   - Vary the scope (narrow to broad)

2. **Silent Brainstorm** (10 min)
   - Each participant writes ideas on sticky notes
   - One idea per note
   - Quantity goal: 50+ ideas total

3. **Share and Build** (15 min)
   - Post all ideas visibly
   - Group similar concepts
   - Build on others' ideas ("Yes, and...")

4. **Dot Vote** (5 min)
   - Each person gets 3-5 dots
   - Vote on most promising alternatives

5. **Evaluate Top Candidates** (10 min)
   - Discuss top 3-5 alternatives in depth

### Complementary Techniques

**SCAMPER** (applied to existing solutions):
- **S**ubstitute: What if tooltip was replaced by...?
- **C**ombine: What if we merged this with...?
- **A**dapt: What works in another context?
- **M**odify: What if we amplified or minimized...?
- **P**ut to another use: What else could this serve?
- **E**liminate: What if we removed...?
- **R**everse: What if we did the opposite?

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**HMW Questions Generated**:
1. "How might we help managers understand who contributed to trends?"
2. "How might we make individual contributions visible without cluttering?"
3. "How might we help users explore contribution patterns?"
4. "How might we celebrate individual contributors?"
5. "How might we enable drill-down from aggregate to individual?"

**Divergent Ideas from HMW #3**:

| Idea | Description |
|------|-------------|
| Contributor timeline | Show who worked when on a time axis |
| Heat map view | Color intensity shows contribution level |
| Avatar stack | Click to expand individual stats |
| Leaderboard panel | Ranked contributors with metrics |
| Filter by person | Toggle to see one person's work |
| Export with breakdown | CSV/PDF with individual data |
| Contribution rings | Pie chart in tooltip showing proportions |
| Hover-to-reveal | Hover on data point shows contributor |

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Desirability | 35% | Do users actually want this? |
| Feasibility | 35% | Can we build it reasonably? |
| Viability | 15% | Does it fit our product strategy? |
| Delight | 15% | Does it create positive emotion? |

---

## 4. Constraint Removal / "What If We Didn't Have To..."

### Overview

Many solutions are constrained by assumptions we don't realize we're making. Constraint removal systematically questions these assumptions to open up new solution spaces.

**Source**: [Untools - First Principles](https://untools.co/first-principles/)

### When to Use

- Solutions feel artificially limited
- "We've always done it this way" thinking is present
- Technical constraints are assumed but not verified
- Looking for breakthrough rather than incremental solutions

### Types of Constraints to Question

| Constraint Type | Example | Question Pattern |
|----------------|---------|------------------|
| Technical | "We can only show X in tooltips" | "What if tooltip weren't the container?" |
| Historical | "Users expect tooltips" | "What if we trained new expectations?" |
| Resource | "We don't have time for..." | "What if we had unlimited time?" |
| Organizational | "That team owns that area" | "What if boundaries were different?" |
| User | "Users won't change behavior" | "What if users would adopt new patterns?" |
| Business | "That doesn't fit our model" | "What if our model evolved?" |

### Step-by-Step Process

1. **List all constraints** (explicit and implicit)
   - Technical limitations
   - User expectations
   - Business rules
   - Resource limits
   - Timeline pressures

2. **For each constraint, ask**:
   - Is this actually true?
   - Who said so, and when?
   - What evidence supports it?
   - What would change if we removed it?

3. **Generate "unconstrained" solutions**
   - Temporarily ignore all constraints
   - What would ideal look like?

4. **Reintroduce constraints selectively**
   - Which constraints are truly immovable?
   - Which can be negotiated?
   - Which are worth challenging?

5. **Find the closest achievable solution**
   - Map back from ideal to achievable

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Constraints Listed**:
- Tooltip has limited space
- Data must load quickly
- Must work on mobile
- Can't change database schema significantly
- Users expect tooltips to be ephemeral

**Constraint Removal Exercise**:

| Constraint | Removed | New Possibility |
|------------|---------|-----------------|
| "Limited tooltip space" | What if space were unlimited? | Full dashboard of contributor data |
| "Must load quickly" | What if we pre-computed? | Rich contributor analytics ready instantly |
| "Tooltips are ephemeral" | What if they persisted? | Pinnable detail cards |
| "Must work in current UI" | What if UI evolved? | New "Contributors" section entirely |
| "Schema can't change" | What if it could? | First-class contributor entities |

**Synthesized Alternative**: Pre-computed contributor dashboard that slides out (drawer pattern) when any data point is clicked, satisfying the need for rich information without tooltip constraints.

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Constraint Validity | 30% | Were the removed constraints actually false? |
| Solution Quality | 30% | Is the unconstrained solution better? |
| Achievability | 25% | Can we actually remove these constraints? |
| Risk | 15% | What could go wrong? |

---

## 5. First Principles Reasoning

### Overview

First principles thinking breaks problems down to their most fundamental truths, then reasons up from there. It avoids reasoning by analogy to existing solutions.

**Sources**:
- [Addy Osmani - First Principles for Software Engineers](https://addyosmani.com/blog/first-principles-thinking-software-engineers/)
- [Atomic Object - Disciplined Problem Solving](https://spin.atomicobject.com/first-principles-problem-solving/)

### When to Use

- Existing solutions feel like "cargo cult" implementations
- Need to justify why, not just what
- Optimizing an already-good solution
- Building something genuinely new

### Key Questions

1. "What are we fundamentally trying to achieve?"
2. "What are the absolute minimum requirements?"
3. "What is unavoidably true about this domain?"
4. "Why do we currently do it this way?"
5. "What would we build if starting from scratch?"

### Step-by-Step Process

1. **Identify the fundamental goal**
   - Strip away all implementation details
   - What outcome matters, ignoring all mechanisms?

2. **List first principles**
   - Physical constraints (screen size, human attention)
   - Logical necessities (data must exist before display)
   - User fundamentals (people want to understand, not just see)

3. **Challenge existing solutions**
   - Why does the current approach exist?
   - What problem did it originally solve?
   - Is that problem still the same?

4. **Rebuild from principles**
   - Given only the fundamentals, what would you build?
   - Don't reference existing patterns initially

5. **Compare and synthesize**
   - How does first-principles solution differ?
   - What hybrid captures best of both?

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**First Principles Analysis**:

**Fundamental Goal**: Enable understanding of who contributed what to observed patterns

**First Principles**:
- Information must be accessible (people need to find it)
- Attention is limited (can't show everything at once)
- Context matters (contribution data needs context to be meaningful)
- Actions follow understanding (users want to do something with this info)

**Reasoning Up**:
- From "information must be accessible" -> Contribution data should be findable from any relevant view
- From "attention is limited" -> Show summary by default, details on demand
- From "context matters" -> Connect contributors to the specific work they did
- From "actions follow understanding" -> Enable follow-up actions (contact, review, thank)

**First-Principles Solution**: A contribution discovery system that:
1. Indicates "contributors available" on any data point
2. Expands to show key contributors with context
3. Links to full profile with actionable options
4. Remembers user's preferred level of detail

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Principled | 35% | Is it derived from fundamentals? |
| Complete | 25% | Does it address all necessary aspects? |
| Efficient | 25% | Does it avoid unnecessary complexity? |
| Novel | 15% | Does it offer genuine improvement? |

---

## 6. Analogy-Based Solution Finding

### Overview

Analogy-based thinking imports solutions from other domains. The power comes from finding structural similarities between problems, not surface similarities.

**Sources**:
- [Number Analytics - Analogical Problem Solving Strategies](https://www.numberanalytics.com/blog/analogical-problem-solving-strategies)
- [MIT - Function Based Design-by-Analogy](https://dspace.mit.edu/bitstream/handle/1721.1/108768/Function%20based%20design.pdf)

### When to Use

- Problem feels unique but probably isn't
- Domain expertise is creating blind spots
- Looking for proven patterns from other fields
- Need to explain solution to non-experts

### Types of Analogies

| Type | Definition | Example |
|------|------------|---------|
| Surface | Similar features/appearance | "Tooltips are like popup books" |
| Structural | Similar relationships/functions | "Data attribution is like academic citation" |
| Near-field | Same domain | "Like how another dashboard shows..." |
| Far-field | Different domain | "Like how restaurants show ingredient sourcing" |

**Key Insight**: Far-field structural analogies are most powerful for innovation but hardest to find.

### Analogy Domains for Software

| Domain | What They Solve Well |
|--------|---------------------|
| **Libraries** | Information organization, discovery, browsing |
| **Museums** | Curated exploration, contextual information |
| **Maps** | Multi-scale navigation, progressive detail |
| **Restaurants** | Menus, customization, sourcing transparency |
| **Healthcare** | Attribution, history, handoffs |
| **Finance** | Audit trails, accountability, breakdowns |
| **News** | Bylines, attribution, sourcing |
| **Social Media** | Profiles, mentions, @-references |

### Step-by-Step Process

1. **Abstract the problem**
   - Remove domain-specific language
   - What is the core function needed?
   - "Need to show who contributed to aggregate data"

2. **Find analogous domains**
   - What other domains solve this function?
   - "Where else do we need attribution for aggregates?"

3. **Study the analog**
   - How exactly does that domain solve it?
   - What principles guide their approach?

4. **Map back to original domain**
   - What translates directly?
   - What needs adaptation?

5. **Generate domain-specific solutions**
   - Apply the analog's approach in your context

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Abstracted Problem**: "Show individual contributions to collective output"

**Analogy Exploration**:

| Domain | How They Handle Attribution | Translated Solution |
|--------|---------------------------|-------------------|
| **Academic papers** | Bylines, author order, contribution statements | "Contributors" section with role descriptions |
| **Film credits** | Scrolling credits, department groupings | Credit roll animation showing who did what |
| **Recipe sites** | "Recipe by X, adapted by Y" | "Data from: [contributors]" inline |
| **GitHub** | Blame view, contribution graphs | Contribution timeline, blame-style drilldown |
| **News** | "Reported by X, with contributions from Y, Z" | Byline pattern with expandable team |
| **Restaurants** | "Sourced from [farm]" labels | "Data sourced from [team]" badges |

**Selected Analog**: GitHub's contribution model
- Shows aggregate first (contribution graph)
- Allows drill-down to individual (blame view)
- Links to full profile
- Shows timeline of activity

**Translated Solution**: Contribution graph widget showing team activity over time, with click-to-blame functionality that highlights individual work, linked to contributor profiles.

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Structural Match | 35% | Is the analogy structurally sound? |
| Translation Quality | 25% | Does it adapt well to our domain? |
| User Familiarity | 25% | Will users recognize the pattern? |
| Differentiation | 15% | Does it add value beyond the analog? |

---

## 7. Blue Ocean ERRC Grid

### Overview

The ERRC Grid (Eliminate, Reduce, Raise, Create) helps break from industry norms by systematically questioning what to add, remove, or change. Originally for strategy, it works well for feature design.

**Sources**:
- [Blue Ocean Strategy - ERRC Grid](https://www.blueoceanstrategy.com/tools/errc-grid/)
- [Blue Ocean Strategy - Four Actions Framework](https://www.blueoceanstrategy.com/blog/errc-grid-template-examples/)

### When to Use

- Feature feels like "me too" copying
- Want to differentiate from competitors
- Need to simplify while adding value
- Challenging industry assumptions

### The Four Actions

| Action | Question | Purpose |
|--------|----------|---------|
| **Eliminate** | What factors can be eliminated that the industry takes for granted? | Remove unnecessary complexity |
| **Reduce** | What factors can be reduced below industry standard? | Cut without losing value |
| **Raise** | What factors can be raised above industry standard? | Exceed expectations where it matters |
| **Create** | What factors can be created that the industry has never offered? | Innovate genuinely |

### Step-by-Step Process

1. **Map the current solution space**
   - What does the typical solution include?
   - What's standard in the industry?

2. **Apply Eliminate**
   - What do users not actually need?
   - What creates complexity without value?

3. **Apply Reduce**
   - What's over-engineered?
   - What could be simpler?

4. **Apply Raise**
   - What matters most to users?
   - Where would exceeding expectations delight?

5. **Apply Create**
   - What's never been offered?
   - What latent need is unaddressed?

6. **Design the new value curve**
   - Combine all four actions into coherent solution

### Software Requirements Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Industry Standard**: Data dashboards typically show aggregate data with limited attribution, often just "Updated by: Admin" timestamps.

**ERRC Analysis**:

| Action | Current Industry Practice | Our Alternative |
|--------|--------------------------|-----------------|
| **Eliminate** | Complex hover interactions, data overload in tooltips | No tooltip at all - use click interaction |
| **Reduce** | Number of data points shown simultaneously | Focus on top 3 contributors only |
| **Raise** | Attribution visibility (usually buried) | Make contributors first-class citizens |
| **Create** | Nothing exists | "Team Pulse" view showing who's actively contributing |

**Synthesized Solution**:

Instead of cramming contributor data into tooltips (industry standard):
- **Eliminate** complex hover interactions entirely
- **Reduce** to showing just "3 contributors" indicator
- **Raise** contributor visibility with dedicated "Team Pulse" panel
- **Create** new "Contributor Spotlight" feature celebrating individual work

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| Differentiation | 30% | Is it genuinely different from competitors? |
| Value Innovation | 30% | Does it increase value while reducing cost/complexity? |
| Coherence | 25% | Do the four actions work together? |
| Defensibility | 15% | Is it hard to copy? |

---

## Integrated Methodology

### Overview

For systematically generating alternatives when a user states a requirement, use this integrated flow:

```
User Requirement
      |
      v
[Motivation Discovery]
      |
      v
[Alternative Generation] --> Lateral Thinking
      |                  --> TRIZ
      |                  --> HMW Questions
      |                  --> Constraint Removal
      |                  --> First Principles
      |                  --> Analogies
      |                  --> ERRC Grid
      v
[Evaluation & Selection]
      |
      v
Prioritized Alternatives
```

### Phase 1: Motivation Discovery

Before generating alternatives, understand the "why":

**Questions to Ask**:
1. "What outcome do you need to achieve?"
2. "What problem does this solve?"
3. "Why is that problem important?"
4. "How would you know if the solution worked?"
5. "What would you do differently once you have this?"

**Document the Motivation**:
```
Stated Requirement: [What they asked for]
Underlying Motivation: [Why they need it]
Success Criteria: [How we'll know it worked]
Follow-on Actions: [What they'll do with the capability]
```

### Phase 2: Alternative Generation

Apply techniques in parallel or sequence based on time available:

**Quick (5-10 min)**: HMW + Constraint Removal
- Generate 3 HMW questions
- List and challenge top 3 constraints
- Aim for 5+ alternatives

**Standard (20-30 min)**: HMW + TRIZ + Analogies
- 5 HMW questions
- Identify contradiction, apply 3 TRIZ principles
- Explore 2 analogous domains
- Aim for 10+ alternatives

**Deep (1+ hour)**: Full methodology
- Complete HMW divergence
- Full TRIZ contradiction analysis
- First principles decomposition
- Multiple analogy explorations
- ERRC grid analysis
- Lateral thinking session
- Aim for 20+ alternatives

### Phase 3: Evaluation and Selection

**Initial Screening** (pass/fail):
- Does it address the motivation?
- Is it technically feasible?
- Does it fit product direction?

**Weighted Scoring** (for passing alternatives):

| Criterion | Weight | Scale |
|-----------|--------|-------|
| Motivation Fit | 30% | How well does it serve the underlying need? |
| User Experience | 25% | Is it intuitive and pleasant? |
| Technical Feasibility | 20% | Can we build it reasonably? |
| Maintainability | 15% | Is it sustainable long-term? |
| Innovation | 10% | Does it offer novel value? |

**Output Format**:
```
## Alternative 1: [Name]
Description: [What it is]
Technique Used: [Which methodology generated it]
Motivation Fit: [How it serves the underlying need]
Score: [Weighted score]
Trade-offs: [What we gain/lose]

## Alternative 2: ...
```

### Complete Example

**Stated Requirement**: "Add per-developer breakdown in tooltips"

**Motivation Discovery**:
- Underlying Motivation: Identify individual contributors to observed trends
- Success Criteria: Manager can see who contributed what within 2 clicks
- Follow-on Actions: Recognize contributors, investigate anomalies, balance workload

**Alternatives Generated**:

| # | Alternative | Technique | Description |
|---|-------------|-----------|-------------|
| 1 | Contributor Drawer | Constraint Removal | Slide-out panel with full contributor details on click |
| 2 | Avatar Stack | TRIZ (#24 Intermediary) | Show small avatars in tooltip, expand on click |
| 3 | Team Pulse View | ERRC (Create) | New dedicated section for contributor analytics |
| 4 | GitHub-style Blame | Analogy | Click any data point to see "who did this" |
| 5 | Filter by Person | HMW | Toggle to view only one contributor's work |
| 6 | Export with Breakdown | Constraint Removal | Detailed contributor data in downloadable format |
| 7 | Contribution Timeline | First Principles | Time-based view of who worked when |
| 8 | Hover-to-Reveal | TRIZ (#15 Dynamics) | Progressive disclosure on extended hover |
| 9 | Contributor Badges | ERRC (Raise) | Visual indicators of top contributors |
| 10 | @-mention Pattern | Analogy (Social Media) | Inline contributor mentions like @developer |

**Top 3 Recommendations**:

1. **Contributor Drawer** (Score: 87)
   - Best balance of information density and usability
   - Familiar pattern (slide-out drawers are common)
   - Separates quick view from deep dive

2. **Filter by Person** (Score: 82)
   - Empowers exploration without cluttering default view
   - Reuses existing filter UI patterns
   - Enables comparison between contributors

3. **Avatar Stack with Expand** (Score: 79)
   - Minimal change to current UI
   - Progressive disclosure respects attention
   - Quick to implement, easy to enhance later

---

## Quick Reference Card

### When to Use Each Technique

| Situation | Best Technique |
|-----------|----------------|
| "We need more ideas" | HMW + Divergent Brainstorming |
| "This feels limited" | Constraint Removal |
| "Trade-offs seem unavoidable" | TRIZ Contradiction Resolution |
| "We're stuck in our assumptions" | Lateral Thinking |
| "What would we build from scratch?" | First Principles |
| "How do others solve this?" | Analogy-Based Finding |
| "How do we differentiate?" | ERRC Grid |

### Red Flags That Indicate Need for Alternatives

- "This is the only way to do it"
- "Everyone does it this way"
- "We've always done it like this"
- "The user asked for exactly this"
- "It's obvious"
- "There's no time to explore"

### Success Indicators

- Generated 5+ distinct alternatives
- At least one alternative surprises you
- Alternatives span different implementation approaches
- User motivation is satisfied by multiple alternatives
- Trade-offs between alternatives are clear

---

## Sources

### Lateral Thinking
- [de Bono Group - Six Thinking Hats](https://www.debonogroup.com/services/core-programs/six-thinking-hats/)
- [Toolshero - Six Thinking Hats](https://www.toolshero.com/decision-making/six-thinking-hats-de-bono/)
- [Innovation Cloud - Six Thinking Hats](https://innovationcloud.com/blog/six-thinking-hats-as-idea-generation-method.html)

### TRIZ
- [TRIZ Knowledge Base - Contradiction Matrix](https://wiki.matriz.org/knowledge-base/triz/problem-solving-tools-5890/contradictions/engineering-contradiction-5995/contradiction-matrix-6026/)
- [Product Development Engineers - TRIZ Guide](https://product-development-engineers.com/2025/10/06/triz-a-guide-to-inventive-problem-solving/)
- [TRIZ40 - Matrix and Principles](https://www.triz40.com/aff_Matrix_TRIZ.php)
- [ScienceDirect - TRIZ for Software Architecture](https://www.sciencedirect.com/science/article/pii/S1877705811001767)

### Design Thinking & HMW
- [IDEO U - Design Thinking Process](https://www.ideou.com/blogs/inspiration/design-thinking-process)
- [Interaction Design Foundation - How Might We](https://www.interaction-design.org/literature/topics/how-might-we)
- [NN/g - How Might We Questions](https://www.nngroup.com/articles/how-might-we-questions/)
- [Conceptboard - HMW Template](https://conceptboard.com/blog/how-might-we-template/)

### First Principles
- [Untools - First Principles](https://untools.co/first-principles/)
- [Addy Osmani - First Principles for Software Engineers](https://addyosmani.com/blog/first-principles-thinking-software-engineers/)
- [Atomic Object - Disciplined Problem Solving](https://spin.atomicobject.com/first-principles-problem-solving/)

### Blue Ocean Strategy
- [Blue Ocean Strategy - ERRC Grid](https://www.blueoceanstrategy.com/tools/errc-grid/)
- [Blue Ocean Strategy - Four Actions Framework](https://www.blueoceanstrategy.com/blog/errc-grid-template-examples/)
- [ResearchGate - ERRC and Value Innovation](https://www.researchgate.net/publication/385257668_The_Application_of_The_Eliminate-Reduce-Raise-Create_ERRC_Grid_in_Achieving_Value_Innovation_Strategy)

### Analogy-Based Design
- [Number Analytics - Analogical Problem Solving](https://www.numberanalytics.com/blog/analogical-problem-solving-strategies)
- [MIT - Function Based Design-by-Analogy](https://dspace.mit.edu/bitstream/handle/1721.1/108768/Function%20based%20design.pdf)
- [arXiv - Data-Driven Design-by-Analogy](https://arxiv.org/pdf/2106.01592)
