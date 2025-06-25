**Purpose**: AI-powered code review and quality analysis

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Perform comprehensive code review and quality analysis on files, commits, or pull requests specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/review --files src/auth.ts --persona-security` - Security-focused file review
- `/review --commit HEAD --quality --evidence` - Quality review with sources
- `/review --pr 123 --all --interactive` - Comprehensive PR review
- `/review --files src/ --persona-performance --think` - Performance analysis

## Command-Specific Flags
--files: "Review specific files or directories"
--commit: "Review changes in specified commit (HEAD, hash, range)"
--pr: "Review pull request changes (git diff main..branch)"
--quality: "Focus on code quality issues (DRY, SOLID, complexity)"
--evidence: "Include sources and documentation for all suggestions"
--fix: "Suggest specific fixes for identified issues"
--summary: "Generate executive summary of review findings"

## Review Dimensions

**Code Quality:** Naming conventions | Structure & organization | DRY violations | SOLID principles | Complexity metrics | Technical debt | Maintainability patterns

**Security Analysis:** Input validation | Authentication & authorization | Data exposure | Injection vulnerabilities | Cryptographic practices | Secret management | OWASP compliance

**Performance Review:** Algorithm complexity | N+1 queries | Memory usage | Caching opportunities | Database optimization | Resource utilization | Bottleneck identification

**Architecture Assessment:** Design patterns | Layer separation | Coupling & cohesion | Scalability considerations | Dependency management | Interface design

**Testing Coverage:** Unit test presence | Edge case handling | Mock usage | Test quality | Integration coverage | E2E scenarios

## Review Process

**1. Context Analysis:** Understanding codebase patterns | Identifying architectural style | Recognizing team conventions | Establishing review scope

**2. Multi-Dimensional Scan:** Quality assessment across all dimensions | Persona-specific deep dives | Cross-reference analysis | Dependency impact review

**3. Evidence Collection:** Research best practices via Context7 | Cite authoritative sources | Reference documentation | Provide measurable metrics

**4. Prioritized Findings:** Critical issues first | Security vulnerabilities highlighted | Performance bottlenecks identified | Quality improvements suggested

**5. Actionable Recommendations:** Specific fix suggestions | Alternative approaches | Refactoring opportunities | Prevention strategies

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/review-patterns.yml#Review_Methodology

## Persona Integration

**--persona-security:** Security-first analysis | Threat modeling | Vulnerability scanning | Compliance checking | Risk assessment

**--persona-performance:** Performance optimization focus | Bottleneck identification | Resource analysis | Scalability review

**--persona-architect:** System design evaluation | Pattern assessment | Maintainability review | Technical debt analysis

**--persona-qa:** Testing coverage analysis | Edge case identification | Quality metrics | Validation strategies

**--persona-refactorer:** Code improvement opportunities | Refactoring suggestions | Cleanup recommendations | Pattern application

## MCP Integration

**Context7:** Research best practices | Find authoritative documentation | Compare alternative approaches | Validate suggestions

**Sequential:** Complex architectural analysis | Root cause investigation | Multi-step problem solving | System design evaluation

**Magic:** UI component improvements | Frontend pattern suggestions | Component library recommendations

**Puppeteer:** Test review suggestions | Validate UI changes | Performance testing | E2E validation

## Deliverables

**Review Report:** `.claudedocs/reviews/review-{timestamp}.md` | Executive summary | Detailed findings | Priority classification | Fix recommendations

**Action Items:** Specific tasks for developers | Prioritized improvement list | Technical debt tracking | Follow-up recommendations

**Evidence Documentation:** Source citations | Best practice references | Performance metrics | Security guidelines

**Knowledge Base:** Pattern library updates | Team convention documentation | Common issue prevention | Review templates

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates