**Purpose**: Security audits and validation

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Perform comprehensive security, quality, and dependency scanning on code specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/scan --security` - Security vulnerability scan
- `/scan --deps` - Dependency audit
- `/scan --validate` - Full validation scan
- `/scan --quick` - Quick scan for critical issues

## Command-Specific Flags
--security: "Deep security vulnerability scanning (OWASP, CVEs, secrets)"
--deps: "Dependency vulnerability audit w/ fix recommendations"
--validate: "Comprehensive validation (syntax, types, logic, security)"
--quick: "Fast scan focusing on critical issues only"
--fix: "Auto-fix safe issues"
--strict: "Zero-tolerance mode (fail on any issue)"
--report: "Generate detailed report"
--ci: "CI-friendly output format"

## Scan Types

**Security Scan:** OWASP Top 10 | Injection vulnerabilities | Auth flaws | Sensitive data exposure | Hardcoded secrets | CVE database check

**Dependency Scan:** Known vulnerabilities | Outdated packages | License compliance | Supply chain risks | Transitive dependencies

**Code Quality:** Complexity metrics | Duplication | Dead code | Type safety | Best practices | Performance antipatterns

**Configuration:** Misconfigured services | Insecure defaults | Missing security headers | Exposed endpoints | Weak crypto

## Validation Levels

**Quick (--quick):** Critical security only | Known CVEs | Hardcoded secrets | SQL injection | XSS vulnerabilities

**Standard (default):** All security checks | Major quality issues | Dependency vulnerabilities | Configuration problems

**Strict (--strict):** Everything + minor issues | Style violations | Documentation gaps | Test coverage | Performance warnings

@include shared/security-patterns.yml#OWASP_Top_10

## Deliverables

**Reports:** `.claudedocs/scans/security-{timestamp}.md` | Severity classification | Fix recommendations | Risk assessment

**Fix Scripts:** Auto-generated patches | Safe automated fixes | Manual fix instructions | Rollback procedures

**CI Integration:** Exit codes | JSON output | SARIF format | GitHub/GitLab integration

@include shared/universal-constants.yml#Standard_Messages_Templates