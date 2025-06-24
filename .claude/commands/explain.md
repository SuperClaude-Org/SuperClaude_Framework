# /explain - Provide detailed technical explanations

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |
| > | greater than | | val | validation |
| ∀ | for all/every | | req | requirements |
| ∃ | exists/there is | | deps | dependencies |
| ∴ | therefore | | env | environment |
| ∵ | because | | db | database |
| ≡ | equivalent | | api | interface |
| ≈ | approximately | | docs | documentation |
| 📁 | directory/path | | std | standard |
| 🔢 | number/count | | def | default |
| 📝 | text/string | | ctx | context |
| ⚙ | setting/config | | err | error |
| 🎛 | control/flags | | exec | execution |
| 🔧 | configuration | | qual | quality |
| 📋 | group/category | | rec | recovery |
| 🚨 | critical/urgent | | sev | severity |
| ⚠ | warning/caution | | resp | response |
| 🔄 | retry/recovery | | esc | escalation |
| ✅ | success/fixed | | tok | token |
| ❌ | failure/error | | opt | optimization |
| ℹ | information | | UX | user experience |
| ⚡ | fast/quick | | UI | user interface |
| 🐌 | slow/delayed | | C | critical |
| ✨ | complete/done | | H | high |
| 📖 | read operation | | M | medium |
| ✏ | edit operation | | L | low |
| 🗑 | delete operation | | |

## Purpose
Provide comprehensive explanations of concepts, code, or systems specified in $ARGUMENTS with appropriate depth and visual aids.

## Syntax
`/explain [flags] [concept/topic]`

## Universal Flags
--plan: "Show execution plan before running"
--uc: "UltraCompressed mode (~70% token reduction)"
--ultracompressed: "Alias for --uc"
--think: "Multi-file analysis w/ context (4K tokens)"
--think-hard: "Deep architectural analysis (10K tokens)"
--ultrathink: "Critical system redesign (32K tokens)"
--c7: "Enable Context7→library documentation lookup"
--seq: "Enable Sequential→complex analysis & thinking"
--magic: "Enable Magic→UI component generation"
--pup: "Enable Puppeteer→browser automation & testing"
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"

## Command-Specific Flags

**Explanation Depth:**
- `--depth eli5`: Simple analogies, avoid jargon, focus on core concepts
- `--depth beginner`: Cover basics with step-by-step guidance and simple examples
- `--depth intermediate`: Technical details, best practices, common patterns
- `--depth expert`: Deep implementation details, edge cases, performance considerations

**Content Enhancement:**
- `--visual`: Create diagrams using Mermaid syntax, ASCII art, flowcharts
- `--examples`: Include practical, runnable code examples
- `--comparisons`: Add comparison tables and pros/cons analysis
- `--interactive`: Create interactive explanations with guided discovery

**Research Integration:**
- `--c7`: Fetch official library/framework documentation
- `--seq`: Step-by-step concept breakdown with complex analysis
- `--no-mcp`: Explain using only codebase context

**Output Format:**
- `--structured`: Organize explanation with clear sections and hierarchy
- `--quick`: Concise explanation focusing on key points
- `--comprehensive`: Complete explanation covering all aspects

## Examples
- `/explain --c7 "React hooks" --visual --think` → React hooks with diagrams and connections
- `/explain --seq "OAuth flow" --depth expert --think-hard` → Deep OAuth analysis with security implications
- `/explain --depth eli5 "async/await" --examples` → Simple async explanation with examples
- `/explain --visual --comparisons "REST vs GraphQL"` → API comparison with diagrams
- `/explain --comprehensive --c7 "Docker containers"` → Complete Docker explanation with docs

## Explanation Structure

**1. High-Level Overview:**
- Start with the big picture
- Define the problem or concept
- Explain why it matters
- Set context and scope

**2. Core Components:**
- Break down into logical parts
- Explain each component clearly
- Show relationships and dependencies
- Use appropriate technical depth

**3. Practical Application:**
- Provide concrete examples
- Show real-world usage
- Include code snippets
- Demonstrate best practices

**4. Advanced Concepts:**
- Cover edge cases and gotchas
- Explain performance implications
- Discuss alternatives and trade-offs
- Address common misconceptions

## Content Types

**Technical Concepts:**
- Explain "what" before "how"
- Connect to familiar concepts
- Build understanding incrementally
- Use analogies and metaphors
- Address common misconceptions

**Code Explanations:**
- Walk through logic step by step
- Explain design decisions and rationale
- Highlight important patterns
- Point out potential pitfalls
- Show alternative approaches

**System Architecture:**
- Start with overall design
- Explain component interactions
- Show data flow and processes
- Discuss scalability and performance
- Cover security considerations

**Framework/Library Usage:**
- Explain core concepts first
- Show common usage patterns
- Provide working examples
- Explain configuration options
- Cover troubleshooting tips

## Visual Aids (--visual)

**Diagram Types:**
- **Mermaid Diagrams**: Flowcharts, sequence diagrams, class diagrams
- **ASCII Art**: Simple visualizations and layouts
- **Process Flows**: Step-by-step workflow diagrams
- **Architecture Diagrams**: System component relationships

**When to Use Visuals:**
- Complex processes or workflows
- System architecture explanations
- Data flow and transformations
- Relationship mapping
- Timeline or sequence explanations

## Research Requirements

**Authoritative Sources:**
- Official documentation via `--c7`
- Framework guides and best practices
- Industry standards and specifications
- Expert opinions and case studies

**Verification Standards:**
- Never explain without verification
- Always cite authoritative sources
- Test code examples before including
- Validate against current versions
- Include source references in explanations

## UltraCompressed Mode (--uc)

**Compression Rules:**
- ~70% token reduction from standard explanations
- Generate legend for symbols/abbreviations
- Use telegram-style formatting
- Structure: lists > paragraphs, tables > prose
- Remove articles, conjunctions, fillers
- Focus on essential information only

**Example Transformation:**
- Standard: "The function takes three parameters and returns a boolean value"
- Compressed: "fn takes 3 params→bool"

## Deliverables
- **Clear Explanations**: Appropriate depth level with structured content
- **Working Examples**: Tested, runnable code snippets
- **Visual Aids**: Diagrams, charts, and illustrations (if requested)
- **Learning Resources**: Curated resources for further study
- **Source References**: Comprehensive citations and links

## Output Locations
- **Explanations**: `.claudedocs/summaries/explanation-{topic}-{timestamp}.md`
- **Learning Resources**: `.claudedocs/reports/learning-resources-{timestamp}.md`
- **Code Examples**: Embedded in explanation files

## Research Requirements
External_Library_Research:
  - Identify library/framework mentioned
  - Context7 lookup for official documentation
  - Verify API patterns and examples
  - Check version compatibility
  - Document findings in implementation
Pattern_Research:
  - Search existing codebase for similar patterns
  - Magic component search if UI-related
  - WebSearch for official documentation
  - Validate approach with Sequential thinking
  - Document pattern choice rationale
API_Integration_Research:
  - Official documentation lookup
  - Authentication requirements
  - Rate limiting and error handling
  - SDK availability and examples
  - Integration testing approach

## Report Notifications
📄 Analysis report saved to: {path}
📊 Metrics updated: {path}
📋 Summary saved to: {path}
💾 Checkpoint created: {path}
📚 Documentation created: {path}
📁 Created directory: {path}
✅ {operation} completed successfully
❌ {operation} failed: {reason}
⚠ {operation} completed w/ warnings

## Best Practices

**Effective Explanations:**
- Start simple, build complexity gradually
- Use concrete examples and analogies
- Address the audience's experience level
- Anticipate and answer common questions
- Provide multiple perspectives when helpful

**Quality Standards:**
- Verify all technical information
- Test all code examples
- Keep explanations current and accurate
- Use clear, precise language
- Structure content logically

## Troubleshooting
- **Complex Topics**: Use `--seq --think-hard` for step-by-step breakdown
- **Framework Questions**: Combine `--c7 --examples` for comprehensive coverage
- **Beginner Audiences**: Use `--depth eli5 --visual --examples`
- **Expert Deep Dives**: Apply `--depth expert --comprehensive --ultrathink`

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
