# Documentation Generation

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Create comprehensive docs for code, API, or system specified in $ARGUMENTS.

Flags:
- --api: Generate API docs | --user: Generate user-friendly guides
- --ultracompressed, --uc: Generate docs w/ ~70% fewer tokens using telegram-style

--api flag:
- Document all endpoints w/ examples | Include request/response formats
- Specify auth requirements | Document error codes & meanings | Add rate limiting info | Provide code samples→multiple languages

--user flag:
- Create user-friendly guides | Include step-by-step tutorials | Add screenshots or diagrams
- Write FAQ section | Include troubleshooting guide | Provide real-world examples

Documentation types:

README Documentation:
- Project overview and purpose
- Installation instructions
- Quick start guide
- Configuration options
- Basic usage examples
- Contributing guidelines

Architecture Documentation:
- System design overview
- Component relationships
- Data flow diagrams
- Technology choices rationale
- Scalability considerations
- Security architecture

API Documentation:
- Endpoint descriptions
- HTTP methods and status codes
- Request/response schemas
- Authentication methods
- Example requests with curl/code
- Webhook documentation
- WebSocket events (if applicable)

User Guides:
- Getting started tutorial
- Feature walkthroughs
- Best practices guide
- Common use cases
- Integration guides
- Migration guides

Developer Documentation:
- Code structure overview
- Development setup
- Testing guidelines
- Deployment process
- Debugging tips
- Performance optimization

Documentation standards:
- Use clear, concise language
- Include practical examples
- Add visual aids where helpful
- Keep information current
- Make it searchable
- Version-specific when needed
- Test all code examples

When --ultracompressed flag is present:
- Apply shared/ultracompressed.yml rules
- Generate legend at doc start
- Remove articles, conjunctions, fillers
- Use symbols: →&@+- w/ w/o
- Use abbreviations: cfg fn impl req resp
- Headings <20 chars, sentences <50 chars
- Format: YAML>JSON>prose, tables>lists>paragraphs
- Target ~70% token reduction

Structure guidelines:
- Logical organization
- Progressive disclosure
- Cross-references
- Glossary for terms
- Index for quick lookup
- Change log maintenance

Documentation Output:
- API documentation: `/docs/api/`
- User guides: `/docs/guides/`
- Architecture docs: `/docs/architecture/`
- Developer docs: `/docs/development/`
- README files: `/docs/README.md` (main), subdirectory READMEs as needed
- Ensure directory exists: `mkdir -p /docs/[category]/`
- Include location in output: "📚 Documentation created: [path]"
- Update `/docs/index.md` with new documentation links

Deliverables: Complete documentation matching the specified type, working code examples, visual aids or diagrams as needed, and quick reference guide.