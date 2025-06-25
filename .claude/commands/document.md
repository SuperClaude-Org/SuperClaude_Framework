**Purpose**: Professional documentation creation

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Generate comprehensive documentation for code, APIs, or systems specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/document --type api --format openapi` - Generate API documentation
- `/document --type readme --style detailed` - Create comprehensive README
- `/document --type user --style tutorial` - User guide w/ tutorials

Documentation modes:

**--type:** Documentation type
- api: API documentation (OpenAPI/Swagger) | code: Code documentation (JSDoc/docstrings)
- readme: Project README files | architecture: System architecture docs
- user: End-user documentation | dev: Developer guides

**--format:** Output format  
- markdown: Markdown format (default) | html: HTML documentation
- pdf: PDF output | docusaurus: Docusaurus compatible | mkdocs: MkDocs compatible

**--style:** Documentation style
- concise: Brief, essential information only | detailed: Comprehensive with examples
- tutorial: Step-by-step guide format | reference: API reference style

@include shared/docs-patterns.yml#Project_Documentation

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates