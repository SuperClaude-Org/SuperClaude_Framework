# /document - Generate comprehensive documentation

## Legend
@include shared/universal-constants.yml#Universal_Legend

## Purpose
Generate comprehensive documentation for code, APIs, or systems specified in $ARGUMENTS with various output formats and styles.

## Syntax
`/document [flags] [target]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--type flag:
- api: API documentation (OpenAPI/Swagger)
- code: Code documentation (JSDoc/docstrings)
- readme: Project README files
- architecture: System architecture docs
- user: End-user documentation
- dev: Developer guides

--format flag:
- markdown: Markdown format (default)
- html: HTML documentation
- pdf: PDF output
- docusaurus: Docusaurus compatible
- mkdocs: MkDocs compatible

--style flag:
- concise: Brief, essential information only
- detailed: Comprehensive with examples
- tutorial: Step-by-step guide format
- reference: API reference style

## Documentation Types

API Documentation:
- OpenAPI 3.0 specification
- Request/response examples
- Authentication details
- Error codes & handling
- Rate limiting information

Code Documentation:
- Function/method descriptions
- Parameter & return types
- Usage examples
- Edge cases & limitations
- Related functions

Architecture Documentation:
- System overview diagrams
- Component interactions
- Data flow documentation
- Technology decisions
- Scalability considerations

User Documentation:
- Getting started guides
- Feature explanations
- Common use cases
- Troubleshooting guides
- FAQ sections

## Best Practices

Structure:
- Clear hierarchy & navigation
- Consistent formatting
- Search-friendly content
- Version-specific docs
- Cross-references

Content:
- Examples for everything
- Progressive disclosure
- Visual aids when helpful
- Keep updated with code
- Test documentation

@include shared/docs-patterns.yml#Documentation_Standards

## Examples

```bash
# Generate API documentation
/document --type api --format openapi

# Create comprehensive README
/document --type readme --style detailed

# Architecture documentation with diagrams
/document --type architecture --think

# User guide with tutorials
/document --type user --style tutorial
```

## Deliverables

- Documentation files in specified format
- Table of contents & navigation
- Code examples & snippets
- Diagrams & visual aids
- Search index if applicable