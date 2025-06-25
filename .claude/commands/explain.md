# Technical Explanations & Education

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Provide comprehensive explanations of concepts, code, or systems in $ARGUMENTS.

Thinking flags (optional):
- --think→multi-concept explanation w/ connections
- --think-hard→complex system explanations w/ deep analysis
- --ultrathink→comprehensive knowledge synthesis & teaching

MCP flags (optional):
- --c7→fetch official lib/framework docs | --seq→step-by-step concept breakdown
- --no-mcp→explain using only codebase context

Doc flags:
- --ultracompressed or --uc→7 0% token reduction in explanations

Examples:
- `/user:explain --c7 "React hooks" --think` - React hooks w/ contextual connections
- `/user:explain --seq "OAuth flow" --think-hard` - Deep OAuth analysis w/ security implications
- `/user:explain --depth advanced --c7 --ultrathink` - Comprehensive system explanation

--depth flag levels:
- ELI5: Simple analogies, avoid jargon, focus→concepts
- Beginner: Cover basics, step-by-step guidance, simple examples
- Intermediate: Tech details, best practices, common patterns
- Expert: Deep impl details, edge cases, perf considerations

When --visual flag is present:
- Create diagrams using Mermaid syntax
- Use ASCII art for simple visualizations
- Include flowcharts for processes
- Add sequence diagrams for interactions

Structure the explanation:
1. Start with a high-level overview
2. Break down into logical components
3. Explain each component with appropriate depth
4. Show relationships and interactions
5. Provide concrete examples

Include relevant formats:
- Code examples that can be run and tested
- Comparison tables for alternatives
- Pros and cons lists for decisions
- Links to authoritative resources

For technical concepts:
- Explain the "what" before the "how"
- Connect to familiar concepts when possible
- Build understanding incrementally
- Address common misconceptions

For code explanations:
- Walk through logic step by step
- Explain design decisions
- Highlight important patterns
- Point out potential gotchas

## UltraCompressed Mode

When --ultracompressed flag is present:
- Apply shared/ultracompressed.yml rules
- Generate legend for symbols/abbreviations used
- Compress explanations to ~30% of normal size
- Use telegram-style: remove articles, use symbols
- Format: lists>paragraphs, tables>prose
- Example: "fn takes 3 params→bool" instead of "The function takes three parameters and returns a boolean value"

Research requirements for explanations:
- Technical concepts → C7 documentation for authoritative explanations and examples
- Framework patterns → Must verify with official guides and documentation
- Best practices → WebSearch for current industry standards and expert opinions
- Code examples → Research working patterns from official documentation
- Never explain without verification - always cite authoritative sources
- All explanations must include sources: // Source: [documentation reference]

Report Output:
- Explanation summaries: `.claudedocs/summaries/explanation-<topic>-<timestamp>.md`
- Learning resources: `.claudedocs/reports/learning-resources-<timestamp>.md`
- Ensure directory exists: `mkdir -p .claudedocs/summaries/ .claudedocs/reports/`
- Include report location in output: "📚 Explanation saved to: [path]"

Deliverables: Clear explanation at the appropriate depth level, working examples, visual aids if requested, curated resources for further learning, and comprehensive source references.