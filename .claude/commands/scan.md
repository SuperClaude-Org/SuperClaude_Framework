# /scan - Perform security and validation scans

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
Perform comprehensive security and validation scans on code, operations, or systems specified in $ARGUMENTS to identify vulnerabilities and safety issues.

## Syntax
`/scan [flags] [target]`

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

**Scan Types:**
- `--validate`: Pre-execution safety validation and risk assessment
- `--security`: Comprehensive security analysis and vulnerability scanning
- `--owasp`: Focus on OWASP Top 10 security risks
- `--deps`: Dependency vulnerability and license scanning
- `--config`: Configuration security and compliance checking

**Scan Depth:**
- `--quick`: Fast validation for common issues with rapid feedback
- `--comprehensive`: Deep analysis covering all security aspects
- `--strict`: Zero-tolerance mode flagging all potential issues

**Specialized Scans:**
- `--infrastructure`: Infrastructure and deployment security
- `--code`: Source code security analysis
- `--data`: Data protection and privacy compliance
- `--network`: Network security and exposure analysis

**Output Control:**
- `--report`: Generate detailed security report
- `--json`: Output results in JSON format for automation
- `--summary`: Provide executive summary with key findings

## Examples
- `/scan --validate --quick` → Fast pre-execution safety check
- `/scan --security --owasp --comprehensive` → Complete OWASP security audit
- `/scan --deps --strict --report` → Dependency scan with detailed report
- `/scan --validate --security --think` → Combined validation and security with analysis
- `/scan --infrastructure --config --json` → Infrastructure security in JSON format

## Validation Mode (--validate)

**Pre-Execution Safety Checks:**

**Security Validation:**
- Path traversal prevention and boundary enforcement
- Secrets and credentials detection in code
- Permission verification and access control
- Input sanitization and validation checks
- Output encoding and XSS prevention

**Code Validation:**
- Syntax correctness and compilation checks
- Import and dependency verification
- Breaking change detection and compatibility
- Configuration validity and completeness
- Type safety and null pointer checks

**Operation Validation:**
- Git repository state verification
- Branch protection compliance
- Resource availability and capacity
- Rollback capability assessment
- Blast radius and impact analysis

**Risk Assessment Framework:**
- Calculate comprehensive risk score (1-10)
- Impact analysis (data loss, downtime, security)
- Reversibility and recovery evaluation
- Required permissions and access verification
- Compliance and regulatory checks

**Validation Workflow:**
1. Parse and analyze intended operation
2. Run all applicable safety checks
3. Generate risk score and impact assessment
4. Report with clear status indicators:
   - ✅ **Pass**: Safe to proceed without concerns
   - ⚠️ **Warning**: Caution advised, review recommended
   - ❌ **Block**: Do not proceed, issues must be resolved

## Security Mode (--security)

**OWASP Top 10 Analysis:**
- **Injection Flaws**: SQL, NoSQL, OS command, LDAP injection detection
- **Broken Authentication**: Session management and auth weakness detection
- **Sensitive Data Exposure**: Data protection and encryption analysis
- **XML External Entities (XXE)**: XML processing vulnerability detection
- **Broken Access Control**: Authorization and privilege escalation issues
- **Security Misconfiguration**: Configuration hardening assessment
- **Cross-Site Scripting (XSS)**: XSS vulnerability detection and prevention
- **Insecure Deserialization**: Object deserialization security analysis
- **Known Vulnerable Components**: Dependency vulnerability scanning
- **Insufficient Logging**: Security monitoring and audit trail analysis

**Code Security Analysis:**
- Input validation gaps and boundary checks
- Output encoding issues and data sanitization
- Authentication mechanism weaknesses
- Authorization logic flaws and privilege escalation
- Cryptographic implementation problems
- Error handling information leakage
- Session management security issues
- File operation safety and path traversal

**Dependency Security Scanning:**
- Known CVE (Common Vulnerabilities and Exposures) detection
- Outdated package identification with security implications
- License compliance and legal risk assessment
- Transitive dependency vulnerability analysis
- Security patch availability and update recommendations
- Typosquatting and malicious package detection

**Configuration Security:**
- Hardcoded secrets and credentials scanning
- Environment variable security assessment
- File and directory permission configurations
- Network exposure and attack surface analysis
- TLS/SSL configuration and certificate validation
- CORS policies and cross-origin security
- Security headers implementation verification

**Infrastructure Security:**
- Open ports and unnecessary services identification
- Firewall rules and network segmentation
- Access control lists and identity management
- Encryption in transit and at rest verification
- Backup security and disaster recovery assessment
- Logging configuration and audit trail analysis

## Scan Execution Modes

**Quick Scan (--quick):**
- Focus on most critical and common vulnerabilities
- Skip time-intensive deep analysis procedures
- Prioritize immediate security concerns
- Provide rapid feedback for development workflow
- Suitable for pre-commit hooks and fast CI/CD

**Comprehensive Scan (--comprehensive):**
- Complete security analysis across all categories
- Deep dive into complex security patterns
- Thorough dependency and configuration analysis
- Detailed threat modeling and risk assessment
- Suitable for periodic security audits

**Strict Mode (--strict):**
- Zero-tolerance approach to security issues
- Flag all potential security concerns
- Enforce industry best practices and standards
- Require explicit overrides for any findings
- Suitable for high-security environments

## Scan Results and Reporting

**Security Findings Classification:**
- **CRITICAL [10]**: Immediate action required, system at risk
- **HIGH [7-9]**: Fix before deployment, significant security risk
- **MEDIUM [4-6]**: Address in next development cycle
- **LOW [1-3]**: Best practice improvements, technical debt

**Report Contents:**
- Executive summary with overall risk assessment
- Detailed findings categorized by security domain
- Specific remediation steps with code examples
- References to security resources and documentation
- Compliance mapping to relevant standards (SOC2, PCI-DSS)
- Trend analysis compared to previous scans

**Integration Behavior:**
- Auto-trigger validation for high-risk operations
- Chain with execution: `scan --validate && command`
- Block execution for CRITICAL [10] severity issues
- Require explicit confirmation for HIGH [7-9] risks
- Log all scan results for audit and compliance

## Deliverables
- **Security Report**: Comprehensive vulnerability assessment
- **Risk Matrix**: Prioritized list of security issues
- **Remediation Guide**: Step-by-step fix instructions
- **Compliance Report**: Regulatory and standard compliance status
- **Trend Analysis**: Security posture improvement tracking

## Output Locations
- **Security Reports**: `.claudedocs/reports/security-scan-{timestamp}.md`
- **Validation Results**: `.claudedocs/reports/validation-{timestamp}.md`
- **Compliance Reports**: `.claudedocs/reports/compliance-{timestamp}.md`
- **Metrics**: `.claudedocs/metrics/security-metrics-{timestamp}.json`

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

## Integration Patterns

**CI/CD Integration:**
- Fail builds on HIGH or CRITICAL security findings
- Generate security reports for each release
- Track security debt and improvement trends
- Automate security patch application

**Development Workflow:**
- Pre-commit hooks for quick security validation
- Pull request security gates
- Regular scheduled comprehensive scans
- Security review integration with code reviews

**Command Chaining:**
- `scan --validate` before `deploy` operations
- `scan --security --strict` for security audits
- `scan --deps` before `migrate` operations
- `scan --config` after `dev-setup` configuration

## Best Practices

**Regular Scanning:**
- Run validation before any risky operations
- Schedule weekly comprehensive security scans
- Implement automated dependency vulnerability monitoring
- Track and trend security findings over time

**Response Procedures:**
- Document exceptions with business justification
- Implement fix verification with re-scanning
- Maintain security issue tracking and resolution
- Regular security training and awareness programs

## Common Security Issues & Solutions

### SQL Injection Vulnerabilities
```bash
/scan --security --owasp "SQL injection patterns"
# → Identifies unsanitized database queries
# → Suggests parameterized query implementations
# → Validates input sanitization functions
```

### Dependency Vulnerabilities
```bash
/scan --deps --security --json
# → Scans package.json/requirements.txt for known CVEs
# → Provides upgrade paths for vulnerable dependencies
# → Generates automated security patch recommendations
```

### Configuration Security Issues
```bash
/scan --config --env --validate
# → Checks for exposed API keys and secrets
# → Validates SSL/TLS configuration
# → Reviews permission and access control settings
```

### OWASP Top 10 Compliance Check
```bash
/scan --owasp --comprehensive --report
# → Performs full OWASP Top 10 vulnerability assessment
# → Generates compliance report with remediation steps
# → Tracks progress against security benchmarks
```

## Troubleshooting
- **False Positives**: Use `--quick` for initial assessment, then `--comprehensive`
- **Complex Applications**: Apply `--think-hard` for thorough analysis
- **CI/CD Integration**: Use `--json` output for automated processing
- **Legacy Systems**: Combine `--security --deps --config` for complete assessment

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
