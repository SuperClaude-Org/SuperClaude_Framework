# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 4.0.x   | ✅ Yes    |
| < 4.0   | ❌ No     |

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Reporting (Preferred)

1. **Do NOT** create a public issue
2. Email security details to: anton.knoery@gmail.com
3. Include "SuperClaude Security" in subject line
4. Provide detailed description of the vulnerability

### 📝 Required Information

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes or mitigations
- Your contact information for follow-up

### ⏱️ Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Preliminary assessment
- **7 days**: Detailed response with next steps
- **30 days**: Resolution target (depending on complexity)

## Security Considerations

### Configuration Framework Security
- SuperClaude is a configuration framework, not executable software
- No network connections or data transmission
- Files are stored locally in ~/.claude/
- Shell scripts have limited system access
- Template reference system (@pattern) validated for integrity

### Installation Security
- install.sh performs file operations only
- No sudo/admin privileges required
- Backup existing configurations before installation
- All operations within user home directory

### Usage Security
- Configuration files are read-only for Claude Code
- No sensitive data stored in configurations
- Slash commands execute through Claude Code's security model
- MCP integrations follow Claude Code's sandbox restrictions

## Best Practices

### For Users
- Review install.sh before execution
- Keep SuperClaude updated
- Report suspicious behavior
- Use official installation methods only

### For Contributors
- Follow secure coding practices
- No hardcoded secrets or credentials
- Validate all user inputs
- Test security implications of changes

## Scope

This security policy covers:
- SuperClaude configuration files
- Installation scripts
- GitHub repository security
- Community interaction security

## Disclaimer

SuperClaude is provided "as is" without warranty. While we strive for security, users are responsible for:
- Reviewing code before installation
- Using in appropriate environments
- Following Claude Code security guidelines
- Backing up existing configurations

---

**Questions?** Contact anton.knoery@gmail.com

*SuperClaude v2 | Security-conscious configuration framework*