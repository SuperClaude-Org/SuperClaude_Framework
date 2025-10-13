# Contributing to SuperClaude Framework

SuperClaude Framework transforms Claude Code into a structured development platform through behavioral instruction injection and intelligent workflow orchestration. We welcome contributions that enhance the framework's capabilities, improve documentation, and expand the ecosystem of specialized agents and MCP server integrations.

**Project Mission**: Enable systematic software development workflows with automated expert coordination, quality gates, and session persistence for Claude Code users.

**Community Approach**: Open development with focus on practical utility, educational value, and professional development workflows. All contributions undergo review to ensure alignment with framework principles and quality standards.

## 🎯 Ways to Contribute

### 🐛 Bug Reports
**Before Reporting:**
- Search existing issues to avoid duplicates
- Test with latest SuperClaude version
- Verify issue isn't covered in [Troubleshooting Guide](docs/Reference/troubleshooting.md)

**Required Information:**
- SuperClaude version: `SuperClaude --version`
- Operating system and version
- Claude Code version: `claude --version`
- Python version: `python3 --version`
- Exact steps to reproduce the issue
- Expected vs actual behavior
- Error messages or logs
- Minimal code example (if applicable)

**Good Bug Report Example:**
```
**Environment:**
- SuperClaude: 4.1.5
- OS: Ubuntu 22.04
- Claude Code: 1.5.2
- Python: 3.9.7

**Issue:** `/sc:implement` command fails with ModuleNotFoundError

**Steps to Reproduce:**
1. Run `SuperClaude install --components core`
2. Execute `/sc:implement "user login"`
3. Error appears: ModuleNotFoundError: No module named 'requests'

**Expected:** Command should execute implementation workflow
**Actual:** Import error prevents execution
```

**Issue Labels:**
- `bug`: Confirmed software defects
- `enhancement`: Feature improvements
- `documentation`: Documentation issues
- `question`: Support requests
- `good-first-issue`: Beginner-friendly contributions

### 💡 Feature Requests
**Feature Evaluation Criteria:**
- Aligns with SuperClaude's systematic development workflow mission
- Provides clear utility for software development tasks
- Integrates well with existing command/agent/mode architecture
- Maintains framework simplicity and discoverability

**High-Priority Features:**
- New specialized agents for emerging domains (mobile, ML, blockchain)
- Additional MCP server integrations for enhanced capabilities
- Workflow automation improvements and quality gates
- Cross-session project management enhancements

**Feature Request Template:**
```markdown
**Feature Description:**
Clear summary of the proposed functionality

**Use Case:**
Specific development scenarios where this feature adds value

**Integration Approach:**
How this feature fits with existing commands/agents/modes

**Implementation Ideas:**
Technical approach or reference implementations

**Priority Level:**
Low/Medium/High based on development impact
```

**Enhancement Process:**
1. Open GitHub issue with `enhancement` label
2. Community discussion and feedback
3. Design review by maintainers
4. Implementation planning and assignment
5. Code development with tests
6. Documentation updates
7. Release integration

**Current Focus Areas:**
- Documentation improvements and examples
- MCP server configurations and troubleshooting
- Command workflow optimization
- Agent coordination patterns
- Quality assurance automation

### 📝 Documentation
**High-Impact Documentation Needs:**

**User Experience Improvements:**
- Real-world workflow examples and case studies
- Video tutorials for complex command sequences
- Interactive command discovery and learning paths
- Troubleshooting guides for common configuration issues

**Technical Documentation:**
- MCP server setup and configuration guides
- Agent coordination patterns and best practices
- Custom behavioral mode development
- Framework extension and customization

**Community Resources:**
- Contributing guides for different skill levels
- Code review standards and processes
- Testing procedures and quality gates
- Release notes and changelog maintenance

**Documentation Standards:**
- Clear, actionable instructions with examples
- Progressive complexity (beginner → advanced)
- Cross-references between related concepts
- Regular testing of documented procedures

**Easy Contributions:**
- Fix typos and grammar issues
- Add missing code examples
- Improve existing explanations
- Create new cookbook recipes
- Update outdated screenshots or commands

**Documentation Structure:**
```
Getting-Started/     # Installation and first steps
User-Guide/         # Feature usage and workflows
Developer-Guide/    # Technical implementation
Reference/          # Best practices and troubleshooting
```

**Contribution Process:**
1. Fork repository and create feature branch
2. Make documentation changes with examples
3. Test all commands and procedures
4. Submit pull request with clear description
5. Address review feedback promptly

### 🔧 Code Contributions
**Current Development Priorities:**

**Framework Core:**
- Command parser improvements and error handling
- Agent routing optimization and coordination
- Session management and persistence enhancements
- Quality gate implementation and validation

**MCP Integration:**
- New server configurations and troubleshooting
- Protocol optimization and error recovery
- Cross-server coordination patterns
- Performance monitoring and optimization

**Agent Development:**
- Specialized domain agents (mobile, ML, DevSecOps)
- Agent collaboration patterns and workflows
- Context-aware activation improvements
- Multi-agent task decomposition

**User Experience:**
- Command discoverability and help systems
- Progressive complexity and learning paths
- Error messages and user guidance
- Workflow automation and shortcuts

**Code Contribution Guidelines:**
- Follow existing code style and patterns
- Include comprehensive tests for new features
- Document all public APIs and interfaces
- Ensure backward compatibility where possible
- Add examples and usage documentation

**Technical Standards:**
- Python 3.8+ compatibility
- Cross-platform support (Linux, macOS, Windows)
- Comprehensive error handling and logging
- Performance optimization for large projects
- Security best practices for external integrations

**Development Workflow:**
1. Review [Technical Architecture](docs/Developer-Guide/technical-architecture.md)
2. Study [Contributing Code Guide](docs/Developer-Guide/contributing-code.md)
3. Set up development environment
4. Create feature branch from `master`
5. Implement changes with tests
6. Update documentation
7. Submit pull request with detailed description

**Code Review Focus:**
- Functionality correctness and edge cases
- Integration with existing framework components
- Performance impact and resource usage
- Documentation completeness and clarity
- Test coverage and quality

For detailed development guidelines, see [Contributing Code Guide](docs/Developer-Guide/contributing-code.md).

## 🤝 Community Guidelines

### Be Respectful
All community interactions should embody professional software development standards:

**Professional Communication:**
- Use clear, technical language appropriate for software development
- Provide specific, actionable feedback with examples
- Focus discussions on technical merit and project goals
- Respect different experience levels and learning approaches

**Constructive Collaboration:**
- Assume positive intent in all interactions
- Ask clarifying questions before making assumptions
- Provide helpful context and reasoning for decisions
- Acknowledge good contributions and helpful community members

**Technical Focus:**
- Keep discussions centered on software development and framework improvement
- Base decisions on technical merit, user value, and project alignment
- Use evidence and examples to support arguments
- Maintain focus on practical utility over theoretical perfection

**Inclusive Environment:**
- Welcome contributors of all skill levels and backgrounds
- Provide mentorship and guidance for new contributors
- Create learning opportunities through code review and discussion
- Celebrate diverse perspectives and solution approaches

### Stay Focused
**Project Focus:**
SuperClaude Framework enhances Claude Code for systematic software development workflows. Contributions should align with this core mission.

**In Scope:**
- Software development workflow automation
- Domain-specific agent development (security, performance, architecture)
- MCP server integrations for enhanced capabilities
- Quality assurance and validation systems
- Session management and project persistence
- Educational content for software development practices

**Out of Scope:**
- General-purpose AI applications unrelated to software development
- Features that significantly increase complexity without clear developer value
- Platform-specific implementations that don't support cross-platform usage
- Commercial or proprietary integrations without open alternatives

**Decision Framework:**
1. **Developer Value**: Does this help software developers build better systems?
2. **Framework Integration**: Does this work well with existing commands/agents/modes?
3. **Maintenance Burden**: Can this be maintained with available resources?
4. **Educational Merit**: Does this teach good software development practices?

**Scope Boundaries:**
- Focus on software development, not general productivity
- Enhance existing workflows rather than creating entirely new paradigms
- Maintain simplicity while adding powerful capabilities
- Support professional development practices and quality standards

### Quality First
**Code Quality Standards:**

**Technical Excellence:**
- All code must pass existing test suites
- New features require comprehensive test coverage (>90%)
- Follow established coding patterns and architectural principles
- Include proper error handling and edge case management
- Optimize for performance and resource efficiency

**Documentation Requirements:**
- All public APIs must have clear documentation with examples
- User-facing features need usage guides and cookbook recipes
- Code changes require updated relevant documentation
- Breaking changes must include migration guides

**User Experience Standards:**
- Commands should be discoverable and self-explanatory
- Error messages must be actionable and helpful
- Features should follow progressive complexity principles
- Maintain consistency with existing interface patterns

**Quality Gates:**
- Automated testing for all core functionality
- Manual testing for user workflows and integration scenarios
- Code review by at least one maintainer
- Documentation review for clarity and completeness
- Performance impact assessment for changes

**Professional Standards:**
- Code should be production-ready, not prototype quality
- Follow security best practices for external integrations
- Ensure cross-platform compatibility and proper dependency management
- Maintain backward compatibility or provide clear migration paths

## 💬 Getting Help

### Channels
**GitHub Issues** (Primary Support)
- Bug reports and technical issues
- Feature requests and enhancement proposals
- Documentation improvements and clarifications
- General troubleshooting with community help

**GitHub Discussions**
- General questions about usage and best practices
- Sharing workflows and success stories
- Community-driven tips and patterns
- Design discussions for major features

**Documentation Resources**
- [Troubleshooting Guide](docs/Reference/troubleshooting.md) - Common issues and solutions
- [Examples Cookbook](docs/Reference/examples-cookbook.md) - Practical usage patterns
- [Quick Start Practices](docs/Reference/quick-start-practices.md) - Optimization strategies
- [Technical Architecture](docs/Developer-Guide/technical-architecture.md) - Framework design

**Development Support**
- [Contributing Code Guide](docs/Developer-Guide/contributing-code.md) - Development setup
- [Testing & Debugging](docs/Developer-Guide/testing-debugging.md) - Quality procedures
- Code review process through pull requests
- Maintainer guidance on complex contributions

**Response Expectations:**
- Bug reports: 1-3 business days
- Feature requests: Review within 1 week
- Pull requests: Initial review within 3-5 days
- Documentation issues: Quick turnaround when straightforward

**Self-Help First:**
Before seeking support, please:
1. Check existing documentation and troubleshooting guides
2. Search GitHub issues for similar problems
3. Verify you're using the latest SuperClaude version
4. Test with minimal reproduction case

### Common Questions

**Development Environment Issues:**

**Q: "SuperClaude install fails with permission errors"**
A: Use `pip install --user SuperClaude` or create virtual environment. See [Installation Guide](docs/Getting-Started/installation.md) for details.

**Q: "Commands not recognized after installation"**
A: Restart Claude Code session. Verify installation with `SuperClaude install --list-components`. Check ~/.claude directory exists.

**Q: "MCP servers not connecting"**
A: Check Node.js installation for MCP servers. Verify ~/.claude/.claude.json configuration. Try `SuperClaude install --components mcp --force`.

**Code Development:**

**Q: "How do I add a new agent?"**
A: Follow agent patterns in setup/components/agents.py. Include trigger keywords, capabilities description, and integration tests.

**Q: "Testing framework setup?"**
A: See [Testing & Debugging Guide](docs/Developer-Guide/testing-debugging.md). Use pytest for Python tests, include component validation.

**Q: "Documentation structure?"**
A: Follow existing patterns: Getting-Started → User-Guide → Developer-Guide → Reference. Include examples and progressive complexity.

**Feature Development:**

**Q: "How do I propose a new command?"**
A: Open GitHub issue with use case, integration approach, and technical design. Reference similar existing commands.

**Q: "MCP server integration process?"**
A: Study existing MCP configurations in setup/components/mcp.py. Include server documentation, configuration examples, and troubleshooting.

**Q: "Performance optimization guidelines?"**
A: Profile before optimizing. Focus on common workflows. Maintain cross-platform compatibility. Document performance characteristics.

## 📄 License

**MIT License Agreement:**

By contributing to SuperClaude Framework, you agree that your contributions will be licensed under the same MIT License that covers the project. This ensures the framework remains open and accessible for educational and commercial use.

**Contribution Terms:**
- All contributions become part of the SuperClaude Framework under MIT License
- Contributors retain copyright to their original work
- No contributor license agreement (CLA) required for simple contributions
- Complex contributions may require explicit license confirmation

**Third-Party Content:**
- Do not include copyrighted code without proper attribution and compatible licensing
- External libraries must use MIT-compatible licenses (Apache 2.0, BSD, etc.)
- Document any third-party dependencies in requirements and documentation
- Respect intellectual property and attribution requirements

**Original Work:**
- Ensure all contributed code is your original work or properly attributed
- Reference external sources, algorithms, or patterns appropriately
- Include proper attribution for adapted or derived code
- Document any patent or licensing considerations

**Commercial Usage:**
The MIT License explicitly allows commercial use of SuperClaude Framework, including contributions. This supports the project's goal of enabling professional software development workflows.

## 🙏 Acknowledgments

**Project Contributors:**

SuperClaude Framework benefits from community contributions across documentation, code development, testing, and user experience improvements. 

**Recognition:**
- [GitHub Contributors Graph](https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors) - Complete contributor list
- Release notes acknowledge significant contributions
- Documentation contributors credited in relevant guides
- Community discussions highlight helpful patterns and solutions

**Community Impact:**
- Enhanced developer productivity through systematic workflows
- Educational value for software development practices
- Open-source contribution to AI-assisted development tools
- Cross-platform compatibility and accessibility

**Contribution Types:**
- **Code Development**: Framework features, agents, MCP integrations
- **Documentation**: Guides, examples, troubleshooting resources  
- **Testing**: Quality assurance, edge case discovery, platform validation
- **Community**: Support, pattern sharing, feedback, and usage examples

**Special Thanks:**
- Early adopters providing feedback and real-world usage patterns
- Documentation contributors improving clarity and completeness
- Testers identifying platform-specific issues and edge cases
- Community members sharing workflows and best practices

**Growth:**
The SuperClaude Framework community continues growing through shared commitment to systematic software development and AI-assisted workflows. Every contribution, from typo fixes to major features, strengthens the framework for all users.

**Join Us:**
Whether you're fixing documentation, adding features, or sharing usage patterns, your contributions help build better software development tools for the entire community.