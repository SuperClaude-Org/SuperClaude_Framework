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

@include shared/quality-patterns.yml#Code_Quality_Metrics

@include shared/security-patterns.yml#OWASP_Top_10

@include shared/compression-performance-patterns.yml#Performance_Baselines

@include shared/architecture-patterns.yml#DDD_Building_Blocks

## Review Process & Methodology

**1. Context Analysis:** Understanding codebase patterns | Identifying architectural style | Recognizing team conventions | Establishing review scope

**2. Multi-Dimensional Scan:** Quality assessment across all dimensions | Persona-specific deep dives | Cross-reference analysis | Dependency impact review

**3. Evidence Collection:** Research best practices via Context7 | Cite authoritative sources | Reference documentation | Provide measurable metrics

**4. Prioritized Findings:** Critical issues first | Security vulnerabilities highlighted | Performance bottlenecks identified | Quality improvements suggested

**5. Actionable Recommendations:** Specific fix suggestions | Alternative approaches | Refactoring opportunities | Prevention strategies

**Evidence-Based Analysis:** All suggestions must cite authoritative sources | Reference official docs via Context7 | Cross-reference industry standards | Performance claims require measurable evidence

**Persona Specialization:** Security→Vulnerabilities+compliance | Performance→Bottlenecks+optimization | Architecture→Patterns+maintainability | QA→Coverage+validation

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/quality-patterns.yml#Validation_Sequence

## Persona Integration

**--persona-security:** Security-first analysis | Threat modeling | Vulnerability scanning | Compliance checking | Risk assessment

**--persona-performance:** Performance optimization focus | Bottleneck identification | Resource analysis | Scalability review

**--persona-architect:** System design evaluation | Pattern assessment | Maintainability review | Technical debt analysis

**--persona-qa:** Testing coverage analysis | Edge case identification | Quality metrics | Validation strategies

**--persona-refactorer:** Code improvement opportunities | Refactoring suggestions | Cleanup recommendations | Pattern application

@include shared/execution-patterns.yml#Servers

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates