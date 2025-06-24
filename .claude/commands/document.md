# /document - Generate comprehensive documentation

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
Generate comprehensive documentation for code, APIs, or systems specified in $ARGUMENTS with various output formats and styles.

## Syntax
`/document [flags] [target]`

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

**Documentation Types:**
- `--api`: Generate API documentation with endpoints, schemas, examples
- `--user`: Create user-friendly guides with tutorials and walkthroughs
- `--architecture`: System design documentation with diagrams
- `--developer`: Developer guides with setup and implementation details
- `--readme`: Project README with overview and quick start

**Output Format:**
- `--visual`: Include diagrams, flowcharts, and visual aids
- `--examples`: Generate practical code examples and snippets
- `--interactive`: Create interactive documentation with live examples

**Content Depth:**
- `--depth`: Explanation depth (basic|intermediate|advanced|expert)
- `--complete`: Comprehensive documentation covering all aspects
- `--quick`: Essential documentation for rapid reference

## Documentation Types

**README Documentation:**
- Project overview and purpose
- Installation instructions and requirements
- Quick start guide with examples
- Configuration options and environment setup
- Basic usage examples
- Contributing guidelines and standards

**API Documentation:**
- Complete endpoint descriptions
- HTTP methods and status codes
- Request/response schemas with validation
- Authentication and authorization methods
- Rate limiting and quota information
- Code examples in multiple languages
- Error handling and troubleshooting

**Architecture Documentation:**
- System design overview and principles
- Component relationships and dependencies
- Data flow diagrams and sequence charts
- Technology choices and rationale
- Scalability considerations and patterns
- Security architecture and threat model

**User Guides:**
- Getting started tutorials
- Feature walkthroughs with screenshots
- Best practices and common patterns
- Integration guides and examples
- Migration guides and upgrade paths
- FAQ and troubleshooting sections

**Developer Documentation:**
- Codebase structure and organization
- Development environment setup
- Testing guidelines and frameworks
- Deployment processes and CI/CD
- Debugging tips and tools
- Performance optimization techniques

## Examples
- `/document --api --examples --c7` → API docs with framework examples
- `/document --user --visual --interactive` → Interactive user guides
- `/document --architecture --complete --seq` → Comprehensive system docs
- `/document --developer --depth advanced` → Advanced developer guides
- `/document --readme --quick --uc` → Concise project README

## Documentation Standards

**Content Quality:**
- Use clear, concise language appropriate for audience
- Include practical, tested examples
- Add visual aids where helpful
- Keep information current and accurate
- Make content searchable and navigable
- Version documentation with code changes

**Structure Guidelines:**
- Logical organization with clear hierarchy
- Progressive disclosure of complexity
- Cross-references between related topics
- Glossary for technical terms
- Index for quick reference
- Changelog maintenance

**UltraCompressed Mode (--uc):**
- Apply token reduction rules (~70% savings)
- Generate symbol/abbreviation legend
- Use telegram-style formatting
- Structure: YAML > tables > lists > prose
- Compress headers and sentences
- Focus on essential information only

## Deliverables
- **Documentation Files**: Complete docs in specified format
- **Code Examples**: Working, tested code snippets
- **Visual Aids**: Diagrams, charts, and illustrations
- **Index Files**: Navigation and cross-reference guides
- **Templates**: Reusable documentation templates

## Output Locations
- **API Documentation**: `docs/api/`
- **User Guides**: `docs/guides/`
- **Architecture Docs**: `docs/architecture/`
- **Developer Docs**: `docs/development/`
- **README Files**: Project root and subdirectories
- **Index**: `docs/index.md` with navigation links

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

## Integration & Best Practices

**Quality Assurance:**
- Test all code examples
- Verify links and references
- Review for clarity and accuracy
- Validate against actual implementation

**Maintenance Strategy:**
- Update with code changes
- Regular review and refresh
- User feedback integration
- Version control alignment

## Troubleshooting
- **Large Codebases**: Use `--depth` to control scope
- **Complex APIs**: Combine `--api --examples --c7` for comprehensive docs
- **Technical Concepts**: Use `--visual --examples` for clarity
- **Token Limits**: Apply `--uc` for compressed documentation

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
