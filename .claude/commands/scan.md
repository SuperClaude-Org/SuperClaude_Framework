# Security Validation & Safety

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Scan code, ops, or systems→security vulns & safety issues in $ARGUMENTS.

Scan type w/ flags:

--validate flag:
- Pre-execution safety validation | Op risk assessment
- Permission & access checks | Quick safety verification before running commands

--security flag:
- Comprehensive security analysis
- w/ --owasp: Focus→OWASP Top 10 | w/ --deps: Deps vuln scan
- Deep security audit→code & cfg

## Validation Mode (--validate)

Pre-execution safety checks:

**Security validation**:
- Path traversal prevention | No execution outside project boundaries
- Secrets and credentials detection
- Permission verification
- Input sanitization checks

**Code validation**:
- Syntax correctness
- Import and dependency verification
- Breaking change detection
- Configuration validity
- Type safety checks

**Operation validation**:
- Git state verification
- Branch protection compliance
- Resource availability
- Rollback capability
- Blast radius assessment

**Risk assessment**:
- Calculate risk score (1-10)
- Impact analysis (data loss, downtime)
- Reversibility evaluation
- Required permissions check
- Compliance verification

Validation workflow:
1. Parse intended operation
2. Run all applicable checks
3. Generate risk score
4. Report with clear indicators:
   - ✅ Pass - Safe to proceed
   - ⚠️ Warning - Caution advised
   - ❌ Block - Do not proceed

Integration behavior:
- Auto-trigger for risky operations
- Chain with execution: scan --validate && execute
- Block CRITICAL [10] severity issues
- Require confirmation for HIGH [7-9] risks

## Security Mode (--security)

Comprehensive security analysis:

**OWASP Top 10 checks**:
- Injection flaws (SQL, NoSQL, OS command, LDAP)
- Broken authentication and session management
- Sensitive data exposure
- XML external entities (XXE)
- Broken access control
- Security misconfiguration
- Cross-site scripting (XSS)
- Insecure deserialization
- Using components with known vulnerabilities
- Insufficient logging and monitoring

**Code security analysis**:
- Input validation gaps
- Output encoding issues
- Authentication weaknesses
- Authorization flaws
- Cryptographic problems
- Error handling leaks
- Session management
- File operation safety

**Dependency scanning**:
- Known CVE detection
- Outdated package identification
- License compliance check
- Transitive dependency analysis
- Security patch availability
- Typosquatting detection

**Configuration security**:
- Hardcoded secrets scan
- Environment variable safety
- Permission configurations
- Network exposure
- TLS/SSL settings
- CORS policies
- Security headers

**Infrastructure security**:
- Open ports and services
- Firewall rules
- Access control lists
- Encryption in transit/rest
- Backup security
- Logging configuration

## Quick Scan Options

With --quick flag:
- Fast validation for common issues
- Skip deep analysis
- Focus on critical problems
- Rapid feedback loop

With --strict flag:
- Zero-tolerance mode
- Flag all potential issues
- Enforce best practices
- Require explicit overrides

## Scan Output

Results include:
- Executive summary with risk level
- Detailed findings by category
- Severity ratings (CRITICAL/HIGH/MEDIUM/LOW)
- Specific remediation steps
- Code examples for fixes
- References to security resources
- Compliance mapping (if applicable)

Severity classification:
- **CRITICAL [10]**: Immediate action required
- **HIGH [7-9]**: Fix before deployment
- **MEDIUM [4-6]**: Address in next sprint
- **LOW [1-3]**: Best practice improvements

## Integration

Works with other commands:
- Run before deploy: `/project:scan --validate && /project:deploy`
- Security gate: `/project:scan --security --strict`
- CI/CD integration: Fail build on HIGH+ findings
- Pre-commit hooks: Quick validation

Best practices:
- Run validation before any risky operation
- Schedule regular security scans
- Track and trend findings over time
- Automate where possible
- Document exceptions with justification

@include shared/command-templates.yml#Report_Output

@include shared/constants.yml#Success_Messages