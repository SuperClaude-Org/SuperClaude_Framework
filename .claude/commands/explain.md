# /explain - Provide detailed technical explanations

## Legend
@include shared/universal-constants.yml#Universal_Legend

## Purpose
Provide comprehensive explanations of concepts, code, or systems specified in $ARGUMENTS with appropriate depth and visual aids.

## Syntax
`/explain [flags] [concept/topic]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--depth flag:
- beginner: Basic concepts, simple language
- intermediate: Standard technical depth
- advanced: Deep technical details
- expert: Cutting-edge & internals

--style flag:
- tutorial: Step-by-step learning
- reference: Quick lookup format
- conversational: Natural dialogue
- academic: Formal & thorough

--visual flag:
- Include diagrams & flowcharts
- Code examples with annotations
- Architecture visualizations
- Sequence diagrams for flows

## Explanation Types

Code Explanation:
- Line-by-line breakdown
- Algorithm walkthrough
- Design pattern usage
- Performance implications
- Edge cases & limitations

Concept Explanation:
- Core principles
- Real-world applications
- Common misconceptions
- Related concepts
- Best practices

System Explanation:
- Architecture overview
- Component interactions
- Data flow analysis
- Scalability factors
- Security considerations

## Methodology

Structure:
1. Overview - What & why
2. Core concepts - Building blocks
3. Deep dive - How it works
4. Examples - Practical usage
5. Gotchas - Common pitfalls
6. Resources - Further learning

Techniques:
- Analogies for complex concepts
- Progressive complexity
- Interactive examples
- Visual representations
- Real-world scenarios

## Best Practices

Clarity:
- Define terms before use
- Build on prior knowledge
- Use consistent terminology
- Provide context
- Summarize key points

Engagement:
- Start with "why it matters"
- Use relatable examples
- Address common questions
- Provide hands-on exercises
- Link to resources

## Examples

```bash
# Explain React hooks for beginners
/explain --depth beginner --style tutorial "React hooks"

# Deep dive into database indexing
/explain --depth advanced --visual "B-tree indexes"

# System architecture explanation
/explain --style reference --visual "microservices communication"

# Algorithm explanation with complexity
/explain --depth expert --think "quicksort optimization"
```

## Deliverables

- Comprehensive explanation document
- Code examples & snippets
- Visual diagrams if requested
- Practice exercises
- Resource links & references
- Summary & key takeaways