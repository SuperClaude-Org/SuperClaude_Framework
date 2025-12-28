---
name: document
description: "Generate focused documentation for components, functions, APIs, and features"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

# /sc:document - Focused Documentation Generation

## Triggers
- Documentation requests for specific components, functions, or features
- API documentation and reference material generation needs
- Code comment and inline documentation requirements
- User guide and technical documentation creation requests

## Usage
```
/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]
```

## Behavioral Flow
1. **Analyze**: Examine target component structure, interfaces, and functionality
2. **Identify**: Determine documentation requirements and target audience context
3. **Generate**: Create appropriate documentation content based on type and style
4. **Format**: Apply consistent structure and organizational patterns
5. **Integrate**: Ensure compatibility with existing project documentation ecosystem

Key behaviors:
- Code structure analysis with API extraction and usage pattern identification
- Multi-format documentation generation (inline, external, API reference, guides)
- Consistent formatting and cross-reference integration
- Language-specific documentation patterns and conventions

## Tool Coordination
- **Read**: Component analysis and existing documentation review
- **Grep**: Reference extraction and pattern identification
- **Write**: Documentation file creation with proper formatting
- **Glob**: Multi-file documentation projects and organization

## Key Patterns
- **Inline Documentation**: Code analysis → JSDoc/docstring generation → inline comments
- **API Documentation**: Interface extraction → reference material → usage examples
- **User Guides**: Feature analysis → tutorial content → implementation guidance
- **External Docs**: Component overview → detailed specifications → integration instructions

## Examples

### Inline Code Documentation
```
/sc:document src/auth/login.js --type inline
# Generates JSDoc comments with parameter and return descriptions
# Adds comprehensive inline documentation for functions and classes
```

### API Reference Generation
```
/sc:document src/api --type api --style detailed
# Creates comprehensive API documentation with endpoints and schemas
# Generates usage examples and integration guidelines
```

### User Guide Creation
```
/sc:document payment-module --type guide --style brief
# Creates user-focused documentation with practical examples
# Focuses on implementation patterns and common use cases
```

### Component Documentation
```
/sc:document components/ --type external
# Generates external documentation files for component library
# Includes props, usage examples, and integration patterns
```

## Boundaries

**Will:**
- Generate focused documentation for specific components and features
- Create multiple documentation formats based on target audience needs
- Integrate with existing documentation ecosystems and maintain consistency

**Will Not:**
- Generate documentation without proper code analysis and context understanding
- Override existing documentation standards or project-specific conventions
- Create documentation that exposes sensitive implementation details