# Contributing to SuperClaude

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | PR | pull request |
| & | and/with | | cfg | configuration |

Thanks for contributing to SuperClaude! This guide helps you get started.

## Quick Start

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SuperClaude.git
   cd SuperClaude
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes** → Test → Commit → PR

## Types of Contributions

### 🐛 Bug Fixes
- Use issue template
- Include steps to reproduce
- Test fix before submitting

### ✨ New Features
- Check existing issues first
- Create feature request issue
- Discuss approach before coding

### 📚 Documentation
- Fix typos, improve clarity
- Add examples & use cases
- Update README if needed

### 🔧 Configuration Improvements
- New slash commands (.claude/commands/)
- YAML resources (.claude/commands/shared/)
- Core configs (CLAUDE.md, RULES.md, etc.)
- Template patterns (@pattern system)

## Development Guidelines

### File Structure
```
SuperClaude/
├── CLAUDE.md, RULES.md, PERSONAS.md, MCP.md  # Core configs
├── .claude/commands/                          # Slash commands
├── .claude/commands/shared/                   # YAML resources
├── install.sh                                # Installation script
└── README.md                                 # Documentation
```

### Code Standards
- **YAML**: 2-space indentation, descriptive keys
- **Markdown**: Clear headers, consistent formatting
- **Shell**: Bash compatibility, error handling
- **No executables**: Config framework only

### Testing
- Test install.sh on clean system
- Verify slash commands work in Claude Code
- Check YAML syntax validity
- Test personas & MCP integration
- Run `validate-references.sh` to check @pattern system

## Submission Process

### 1. Before You Start
- Search existing issues & PRs
- Create issue for discussion (features)
- Fork repository

### 2. Development
- Create feature branch
- Make focused commits
- Follow naming conventions
- Test thoroughly

### 3. Pull Request
- Use PR template
- Clear title & description
- Link related issues
- Request review

### 4. Review Process
- Maintainer review required
- Address feedback promptly
- Keep PR up-to-date
- Squash commits if requested

## Issue Guidelines

### Bug Reports
Include:
- SuperClaude version
- Claude Code version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## Slash Command Development

### Creating New Commands
1. **File**: `.claude/commands/your-command.md`
2. **Format**: Follow existing command structure
3. **Flags**: Use consistent flag patterns
4. **Documentation**: Include examples
5. **Integration**: Update index.md

### Command Structure
```markdown
# Command Name
Description & purpose

## Flags
- --flag1: Description
- --flag2: Description

## Examples
/command --flag1
```

### YAML Resources & Templates
1. **Location**: `.claude/commands/shared/`
2. **Purpose**: Reusable configurations & @pattern templates
3. **Naming**: descriptive-name.yml
4. **Structure**: Clear, documented sections
5. **Validation**: Use `validate-references.sh` to check @pattern links

## Persona Development

### Guidelines
- **Core Belief**: What drives this persona
- **Primary Question**: Key question they ask
- **Decision Pattern**: How they prioritize
- **MCP Tools**: Which tools they prefer

### Testing Personas
- Test with various scenarios
- Verify MCP integration
- Check decision consistency
- Document use cases

## Documentation Standards

### Writing Style
- Concise & clear
- Use symbols from legend
- Bullet points > prose
- Include examples

### UltraCompressed Mode
- Use abbreviations
- Remove articles (the, a, that)
- Symbol shortcuts (→, &, w/)
- Auto-generate legends

## Community Guidelines

### Be Respectful
- Professional communication
- Constructive feedback only
- Help newcomers
- Credit contributions

### Quality First
- Test before submitting
- Document changes
- Follow established patterns
- Consider maintenance impact

## Getting Help

### Resources
- README.md → Overview & installation
- Issues → Bug reports & discussions
- Wiki → Extended documentation
- Discussions → Community Q&A

### Contact
- Create issue for bugs/features
- Use discussions for questions
- Tag maintainers for urgent issues

## Developer Certificate of Origin (DCO)

By contributing to this project, you agree to the Developer Certificate of Origin (DCO). This document was created by the Linux Kernel community and is a simple statement that you, as a contributor, have the legal right to make the contribution.

The DCO is legally binding statement that assures contributors have the right to submit their work under the project's license. All commits must be signed off with:

```
git commit -s -m "Your commit message"
```

This adds a `Signed-off-by` line to your commit message.

## Recognition

Contributors are recognized through:
- GitHub contributor graph
- CHANGELOG.md mentions
- Issue/PR acknowledgments
- Community discussions

### Notable Contributors
- @amgiiine - Commands Cheat Sheet and documentation improvements

---

**Ready to contribute?** Create an issue or submit a PR!

*SuperClaude v2 | Community-driven configuration framework*
