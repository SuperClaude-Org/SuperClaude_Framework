# SuperClaude Agents Guide 🤖

SuperClaude provides 16 domain specialist agents that Claude Code can invoke for specialized expertise.


## 🧪 Testing Agent Activation

Before using this guide, verify agent selection works:

```bash
# Test manual agent invocation
@agent-python-expert "explain decorators"
# Example behavior: Python expert responds with detailed explanation

# Test security agent auto-activation
/sc:implement "JWT authentication"
# Example behavior: Security engineer should activate automatically

# Test frontend agent auto-activation
/sc:implement "responsive navigation component"  
# Example behavior: Frontend architect + Magic MCP should activate

# Test systematic analysis
/sc:troubleshoot "slow API performance"
# Example behavior: Root-cause analyst + performance engineer activation

# Test combining manual and auto
/sc:analyze src/
@agent-refactoring-expert "suggest improvements"
# Example behavior: Analysis followed by refactoring suggestions
```

**If tests fail**: Check agent files exist in `~/.claude/agents/` or restart Claude Code session

## Core Concepts

### What are SuperClaude Agents?
**Agents** are specialized AI domain experts implemented as context instructions that modify Claude Code's behavior. Each agent is a carefully crafted `.md` file in the `superclaude/Agents/` directory containing domain-specific expertise, behavioral patterns, and problem-solving approaches.

**Important**: Agents are NOT separate AI models or software - they are context configurations that Claude Code reads to adopt specialized behaviors.

### Two Ways to Use Agents

#### 1. Manual Invocation with @agent- Prefix
```bash
# Directly invoke a specific agent
@agent-security "review authentication implementation"
@agent-frontend "design responsive navigation"
@agent-architect "plan microservices migration"
```

#### 2. Auto-Activation (Behavioral Routing)
"Auto-activation" means Claude Code reads behavioral instructions to engage appropriate contexts based on keywords and patterns in your requests. SuperClaude provides behavioral guidelines that Claude follows to route to the most appropriate specialists.

> **📝 How Agent "Auto-Activation" Works**: 
> Agent activation isn't automatic system logic - it's behavioral instructions in context files. 
> When documentation says agents "auto-activate", it means Claude Code reads instructions to engage 
> specific domain expertise based on keywords and patterns in your request. This creates the 
> experience of intelligent routing while being transparent about the underlying mechanism.

```bash
# These commands auto-activate relevant agents
/sc:implement "JWT authentication"  # → security-engineer auto-activates
/sc:design "React dashboard"        # → frontend-architect auto-activates
/sc:troubleshoot "memory leak"      # → performance-engineer auto-activates
```

**MCP Servers** provide enhanced capabilities through specialized tools like Context7 (documentation), Sequential (analysis), Magic (UI), Playwright (testing), and Morphllm (code transformation).

**Domain Specialists** focus on narrow expertise areas to provide deeper, more accurate solutions than generalist approaches.

### Agent Selection Rules

**Priority Hierarchy:**
1. **Manual Override** - @agent-[name] takes precedence over auto-activation
2. **Keywords** - Direct domain terminology triggers primary agents
3. **File Types** - Extensions activate language/framework specialists  
4. **Complexity** - Multi-step tasks engage coordination agents
5. **Context** - Related concepts trigger complementary agents

**Conflict Resolution:**
- Manual invocation → Specified agent takes priority
- Multiple matches → Multi-agent coordination
- Unclear context → Requirements analyst activation
- High complexity → System architect oversight
- Quality concerns → Automatic QA agent inclusion

**Selection Decision Tree:**
```
Task Analysis →
├─ Manual @agent-? → Use specified agent
├─ Single Domain? → Activate primary agent
├─ Multi-Domain? → Coordinate specialist agents  
├─ Complex System? → Add system-architect oversight
├─ Quality Critical? → Include security + performance + quality agents
└─ Learning Focus? → Add learning-guide + technical-writer
```

## Quick Start Examples

### Manual Agent Invocation
```bash
# Explicitly call specific agents with @agent- prefix
@agent-python-expert "optimize this data processing pipeline"
@agent-quality-engineer "create comprehensive test suite"
@agent-technical-writer "document this API with examples"
@agent-socratic-mentor "explain this design pattern"
```

### Automatic Agent Coordination
```bash
# Commands that trigger auto-activation
/sc:implement "JWT authentication with rate limiting"
# → Triggers: security-engineer + backend-architect + quality-engineer

/sc:design "accessible React dashboard with documentation"
# → Triggers: frontend-architect + learning-guide + technical-writer  

/sc:troubleshoot "slow deployment pipeline with intermittent failures"
# → Triggers: devops-architect + performance-engineer + root-cause-analyst

/sc:audit "payment processing security vulnerabilities"
# → Triggers: security-engineer + quality-engineer + refactoring-expert
```

### Combining Manual and Auto Approaches
```bash
# Start with command (auto-activation)
/sc:implement "user profile system"

# Then explicitly add specialist review
@agent-security "review the profile system for OWASP compliance"
@agent-performance-engineer "optimize database queries"
```

---

## The SuperClaude Agent Team 👥

### Meta-Layer Agent 🎯

### pm-agent 📚
**Expertise**: Self-improvement workflow executor that documents implementations, analyzes mistakes, and maintains knowledge base continuously

**Auto-Activation**:
- **Post-Implementation**: After any task completion requiring documentation
- **Mistake Detection**: Immediate analysis when errors or bugs occur
- **Monthly Maintenance**: Regular documentation health reviews
- **Knowledge Gap**: When patterns emerge requiring documentation
- Commands: Automatically activates after `/sc:implement`, `/sc:build`, `/sc:improve` completions

**Capabilities**:
- **Implementation Documentation**: Record new patterns, architectural decisions, edge cases discovered
- **Mistake Analysis**: Root cause analysis, prevention checklists, pattern identification
- **Pattern Recognition**: Extract success patterns, anti-patterns, best practices
- **Knowledge Maintenance**: Monthly reviews, noise reduction, duplication merging, freshness updates
- **Self-Improvement Loop**: Transform every experience into reusable knowledge

**How PM Agent Works** (Meta-Layer):
1. **Specialist Agents Complete Task**: Backend-architect implements feature
2. **PM Agent Auto-Activates**: After implementation completion
3. **Documentation**: Records patterns, decisions, edge cases in docs/
4. **Knowledge Update**: Updates CLAUDE.md if global pattern discovered
5. **Evidence Collection**: Links test results, screenshots, metrics
6. **Learning Integration**: Extracts lessons for future implementations

**Self-Improvement Workflow Examples**:
1. **Post-Implementation Documentation**:
   - Scenario: Backend architect just implemented JWT authentication
   - PM Agent: Analyzes implementation → Documents JWT pattern → Updates docs/authentication.md → Records security decisions → Creates evidence links
   - Output: Comprehensive authentication pattern documentation for future reuse

2. **Immediate Mistake Analysis**:
   - Scenario: Direct Supabase import used (Kong Gateway bypassed)
   - PM Agent: Stops implementation → Root cause analysis → Documents in self-improvement-workflow.md → Creates prevention checklist → Updates CLAUDE.md
   - Output: Mistake recorded with prevention strategy, won't repeat error

3. **Monthly Documentation Maintenance**:
   - Scenario: Monthly review on 1st of month
   - PM Agent: Reviews docs older than 6 months → Deletes unused documents → Merges duplicates → Updates version numbers → Reduces verbosity
   - Output: Fresh, minimal, high-signal documentation maintained

**Integration with Task Execution**:
PM Agent operates as a **meta-layer** above specialist agents:
```
Task Flow:
1. User Request → Auto-activation selects specialist agent
2. Specialist Agent → Executes implementation (backend-architect, frontend-architect, etc.)
3. PM Agent (Auto-triggered) → Documents learnings
4. Knowledge Base → Updated with patterns, mistakes, improvements
```

**Works Best With**: All agents (documents their work, not replaces them)

**Quality Standards**:
- **Latest**: Last Verified dates on all documents
- **Minimal**: Necessary information only, no verbosity
- **Clear**: Concrete examples and copy-paste ready code
- **Practical**: Immediately applicable to real work

**Self-Improvement Loop Phases**:
- **AFTER Phase**: Primary responsibility - document implementations, update docs/, create evidence
- **MISTAKE RECOVERY**: Immediate stop, root cause analysis, documentation update
- **MAINTENANCE**: Monthly pruning, merging, freshness updates, noise reduction

**Verify**: Activates automatically after task completions requiring documentation
**Test**: Should document patterns after backend-architect implements features
**Check**: Should create prevention checklists when mistakes detected

---

### Architecture & System Design Agents 🏗️

### system-architect 🏢
**Expertise**: Large-scale distributed system design with focus on scalability and service architecture

**Auto-Activation**:
- Keywords: "architecture", "microservices", "scalability", "system design", "distributed"
- Context: Multi-service systems, architectural decisions, technology selection
- Complexity: >5 components or cross-domain integration requirements

**Capabilities**:
- Service boundary definition and microservices decomposition
- Technology stack selection and integration strategy
- Scalability planning and performance architecture
- Event-driven architecture and messaging patterns
- Data flow design and system integration

**Examples**:
1. **E-commerce Platform**: Design microservices for user, product, payment, and notification services with event sourcing
2. **Real-time Analytics**: Architecture for high-throughput data ingestion with stream processing and time-series storage
3. **Multi-tenant SaaS**: System design with tenant isolation, shared infrastructure, and horizontal scaling strategies

### Success Criteria
- [ ] System-level thinking evident in responses
- [ ] Mentions service boundaries and integration patterns
- [ ] Includes scalability and reliability considerations
- [ ] Provides technology stack recommendations

**Verify:** `/sc:design "microservices platform"` should activate system-architect  
**Test:** Output should include service decomposition and integration patterns  
**Check:** Should coordinate with devops-architect for infrastructure concerns

**Works Best With**: devops-architect (infrastructure), performance-engineer (optimization), security-engineer (compliance)

---

### backend-architect ⚙️
**Expertise**: Robust server-side system design with emphasis on API reliability and data integrity

**Auto-Activation**:
- Keywords: "API", "backend", "server", "database", "REST", "GraphQL", "endpoint"
- File Types: API specs, server configs, database schemas
- Context: Server-side logic, data persistence, API development

**Capabilities**:
- RESTful and GraphQL API architecture and design patterns
- Database schema design and query optimization strategies
- Authentication, authorization, and security implementation
- Error handling, logging, and monitoring integration
- Caching strategies and performance optimization

**Examples**:
1. **User Management API**: JWT authentication with role-based access control and rate limiting
2. **Payment Processing**: PCI-compliant transaction handling with idempotency and audit trails
3. **Content Management**: RESTful APIs with caching, pagination, and real-time notifications

**Works Best With**: security-engineer (auth/security), performance-engineer (optimization), quality-engineer (testing)

---

### frontend-architect 🎨
**Expertise**: Modern web application architecture with focus on accessibility and user experience

**Auto-Activation**:
- Keywords: "UI", "frontend", "React", "Vue", "Angular", "component", "accessibility", "responsive"
- File Types: .jsx, .vue, .ts (frontend), .css, .scss
- Context: User interface development, component design, client-side architecture

**Capabilities**:
- Component architecture and design system implementation
- State management patterns (Redux, Zustand, Pinia)
- Accessibility compliance (WCAG 2.1) and inclusive design
- Performance optimization and bundle analysis
- Progressive Web App and mobile-first development

**Examples**:
1. **Dashboard Interface**: Accessible data visualization with real-time updates and responsive grid layout
2. **Form Systems**: Complex multi-step forms with validation, error handling, and accessibility features
3. **Design System**: Reusable component library with consistent styling and interaction patterns

**Works Best With**: learning-guide (user guidance), performance-engineer (optimization), quality-engineer (testing)

---

### devops-architect 🚀
**Expertise**: Infrastructure automation and deployment pipeline design for reliable software delivery

**Auto-Activation**:
- Keywords: "deploy", "CI/CD", "Docker", "Kubernetes", "infrastructure", "monitoring", "pipeline"
- File Types: Dockerfile, docker-compose.yml, k8s manifests, CI configs
- Context: Deployment processes, infrastructure management, automation

**Capabilities**:
- CI/CD pipeline design with automated testing and deployment
- Container orchestration and Kubernetes cluster management
- Infrastructure as Code with Terraform and cloud platforms
- Monitoring, logging, and observability stack implementation
- Security scanning and compliance automation

**Examples**:
1. **Microservices Deployment**: Kubernetes deployment with service mesh, auto-scaling, and blue-green releases
2. **Multi-Environment Pipeline**: GitOps workflow with automated testing, security scanning, and staged deployments
3. **Monitoring Stack**: Comprehensive observability with metrics, logs, traces, and alerting systems

**Works Best With**: system-architect (infrastructure planning), security-engineer (compliance), performance-engineer (monitoring)

---

### deep-research-agent 🔬
**Expertise**: Comprehensive research with adaptive strategies and multi-hop reasoning

**Auto-Activation**:
- Keywords: "research", "investigate", "discover", "explore", "find out", "search for", "latest", "current"
- Commands: `/sc:research` automatically activates this agent
- Context: Complex queries requiring thorough research, current information needs, fact-checking
- Complexity: Questions spanning multiple domains or requiring iterative exploration

**Capabilities**:
- **Adaptive Planning Strategies**: Planning (direct), Intent (clarify first), Unified (collaborative)
- **Multi-Hop Reasoning**: Up to 5 levels - entity expansion, temporal progression, conceptual deepening, causal chains
- **Self-Reflective Mechanisms**: Progress assessment after each major step with replanning triggers
- **Evidence Management**: Clear citations, relevance scoring, uncertainty acknowledgment
- **Tool Orchestration**: Parallel-first execution with Tavily (search), Playwright (JavaScript content), Sequential (reasoning)
- **Learning Integration**: Pattern recognition and strategy reuse via Serena memory

**Research Depth Levels**:
- **Quick**: Basic search, 1 hop, summary output
- **Standard**: Extended search, 2-3 hops, structured report (default)
- **Deep**: Comprehensive search, 3-4 hops, detailed analysis
- **Exhaustive**: Maximum depth, 5 hops, complete investigation

**Examples**:
1. **Technical Research**: `/sc:research "latest React Server Components patterns"` → Comprehensive technical research with implementation examples
2. **Market Analysis**: `/sc:research "AI coding assistants landscape 2024" --strategy unified` → Collaborative analysis with user input
3. **Academic Investigation**: `/sc:research "quantum computing breakthroughs" --depth exhaustive` → Comprehensive literature review with evidence chains

**Workflow Pattern** (6-Phase):
1. **Understand** (5-10%): Assess query complexity
2. **Plan** (10-15%): Select strategy and identify parallel opportunities  
3. **TodoWrite** (5%): Create adaptive task hierarchy (3-15 tasks)
4. **Execute** (50-60%): Parallel searches and extractions
5. **Track** (Continuous): Monitor progress and confidence
6. **Validate** (10-15%): Verify evidence chains

**Output**: Reports saved to `claudedocs/research_[topic]_[timestamp].md`

**Works Best With**: system-architect (technical research), learning-guide (educational research), requirements-analyst (market research)

### Quality & Analysis Agents 🔍

### security-engineer 🔒
**Expertise**: Application security architecture with focus on threat modeling and vulnerability prevention

**Auto-Activation**:
- Keywords: "security", "auth", "authentication", "vulnerability", "encryption", "compliance", "OWASP"
- Context: Security reviews, authentication flows, data protection requirements
- Risk Indicators: Payment processing, user data, API access, regulatory compliance needs

**Capabilities**:
- Threat modeling and attack surface analysis
- Secure authentication and authorization design (OAuth, JWT, SAML)
- Data encryption strategies and key management
- Vulnerability assessment and penetration testing guidance
- Security compliance (GDPR, HIPAA, PCI-DSS) implementation

**Examples**:
1. **OAuth Implementation**: Secure multi-tenant authentication with token refresh and role-based access
2. **API Security**: Rate limiting, input validation, SQL injection prevention, and security headers
3. **Data Protection**: Encryption at rest/transit, key rotation, and privacy-by-design architecture

**Works Best With**: backend-architect (API security), quality-engineer (security testing), root-cause-analyst (incident response)

---

### performance-engineer ⚡
**Expertise**: System performance optimization with focus on scalability and resource efficiency

**Auto-Activation**:
- Keywords: "performance", "slow", "optimization", "bottleneck", "latency", "memory", "CPU"
- Context: Performance issues, scalability concerns, resource constraints
- Metrics: Response times >500ms, high memory usage, poor throughput

**Capabilities**:
- Performance profiling and bottleneck identification
- Database query optimization and indexing strategies  
- Caching implementation (Redis, CDN, application-level)
- Load testing and capacity planning
- Memory management and resource optimization

**Examples**:
1. **API Optimization**: Reduce response time from 2s to 200ms through caching and query optimization
2. **Database Scaling**: Implement read replicas, connection pooling, and query result caching
3. **Frontend Performance**: Bundle optimization, lazy loading, and CDN implementation for <3s load times

**Works Best With**: system-architect (scalability), devops-architect (infrastructure), root-cause-analyst (debugging)

---

### root-cause-analyst 🔍
**Expertise**: Systematic problem investigation using evidence-based analysis and hypothesis testing

**Auto-Activation**:
- Keywords: "bug", "issue", "problem", "debugging", "investigation", "troubleshoot", "error"
- Context: System failures, unexpected behavior, complex multi-component issues
- Complexity: Cross-system problems requiring methodical investigation

**Capabilities**:
- Systematic debugging methodology and root cause analysis
- Error correlation and dependency mapping across systems
- Log analysis and pattern recognition for failure investigation
- Hypothesis formation and testing for complex problems
- Incident response and post-mortem analysis procedures

**Examples**:
1. **Database Connection Failures**: Trace intermittent failures across connection pools, network timeouts, and resource limits
2. **Payment Processing Errors**: Investigate transaction failures through API logs, database states, and external service responses
3. **Performance Degradation**: Analyze gradual slowdown through metrics correlation, resource usage, and code changes

**Works Best With**: performance-engineer (performance issues), security-engineer (security incidents), quality-engineer (testing failures)

---

### quality-engineer ✅
**Expertise**: Comprehensive testing strategy and quality assurance with focus on automation and coverage

**Auto-Activation**:
- Keywords: "test", "testing", "quality", "QA", "validation", "coverage", "automation"
- Context: Test planning, quality gates, validation requirements
- Quality Concerns: Code coverage <80%, missing test automation, quality issues

**Capabilities**:
- Test strategy design (unit, integration, e2e, performance testing)
- Test automation framework implementation and CI/CD integration
- Quality metrics definition and monitoring (coverage, defect rates)
- Edge case identification and boundary testing scenarios
- Accessibility testing and compliance validation

**Examples**:
1. **E-commerce Testing**: Comprehensive test suite covering user flows, payment processing, and inventory management
2. **API Testing**: Automated contract testing, load testing, and security testing for REST/GraphQL APIs
3. **Accessibility Validation**: WCAG 2.1 compliance testing with automated and manual accessibility audits

**Works Best With**: security-engineer (security testing), performance-engineer (load testing), frontend-architect (UI testing)

---

### refactoring-expert 🔧
**Expertise**: Code quality improvement through systematic refactoring and technical debt management

**Auto-Activation**:
- Keywords: "refactor", "clean code", "technical debt", "SOLID", "maintainability", "code smell"
- Context: Legacy code improvements, architecture updates, code quality issues
- Quality Indicators: High complexity, duplicated code, poor test coverage

**Capabilities**:
- SOLID principles application and design pattern implementation
- Code smell identification and systematic elimination
- Legacy code modernization strategies and migration planning
- Technical debt assessment and prioritization frameworks
- Code structure improvement and architecture refactoring

**Examples**:
1. **Legacy Modernization**: Transform monolithic application to modular architecture with improved testability
2. **Design Patterns**: Implement Strategy pattern for payment processing to reduce coupling and improve extensibility  
3. **Code Cleanup**: Remove duplicated code, improve naming conventions, and extract reusable components

**Works Best With**: system-architect (architecture improvements), quality-engineer (testing strategy), python-expert (language-specific patterns)

### Specialized Development Agents 🎯

### python-expert 🐍
**Expertise**: Production-ready Python development with emphasis on modern frameworks and performance

**Auto-Activation**:
- Keywords: "Python", "Django", "FastAPI", "Flask", "asyncio", "pandas", "pytest"
- File Types: .py, requirements.txt, pyproject.toml, Pipfile
- Context: Python development tasks, API development, data processing, testing

**Capabilities**:
- Modern Python architecture patterns and framework selection
- Asynchronous programming with asyncio and concurrent futures
- Performance optimization through profiling and algorithmic improvements
- Testing strategies with pytest, fixtures, and test automation
- Package management and deployment with pip, poetry, and Docker

**Examples**:
1. **FastAPI Microservice**: High-performance async API with Pydantic validation, dependency injection, and OpenAPI docs
2. **Data Pipeline**: Pandas-based ETL with error handling, logging, and parallel processing for large datasets
3. **Django Application**: Full-stack web app with custom user models, API endpoints, and comprehensive test coverage

**Works Best With**: backend-architect (API design), quality-engineer (testing), performance-engineer (optimization)

---

### requirements-analyst 📝
**Expertise**: Requirements discovery and specification development through systematic stakeholder analysis

**Auto-Activation**:
- Keywords: "requirements", "specification", "PRD", "user story", "functional", "scope", "stakeholder"
- Context: Project initiation, unclear requirements, scope definition needs
- Complexity: Multi-stakeholder projects, unclear objectives, conflicting requirements

**Capabilities**:
- Requirements elicitation through stakeholder interviews and workshops
- User story writing with acceptance criteria and definition of done
- Functional and non-functional specification documentation
- Stakeholder analysis and requirement prioritization frameworks
- Scope management and change control processes

**Examples**:
1. **Product Requirements Document**: Comprehensive PRD for fintech mobile app with user personas, feature specifications, and success metrics
2. **API Specification**: Detailed requirements for payment processing API with error handling, security, and performance criteria
3. **Migration Requirements**: Legacy system modernization requirements with data migration, user training, and rollback procedures

**Works Best With**: system-architect (technical feasibility), technical-writer (documentation), learning-guide (user guidance)

### Communication & Learning Agents 📚

### technical-writer 📚
**Expertise**: Technical documentation and communication with focus on audience analysis and clarity

**Auto-Activation**:
- Keywords: "documentation", "readme", "API docs", "user guide", "technical writing", "manual"
- Context: Documentation requests, API documentation, user guides, technical explanations
- File Types: .md, .rst, API specs, documentation files

**Capabilities**:
- Technical documentation architecture and information design
- Audience analysis and content targeting for different skill levels
- API documentation with working examples and integration guidance
- User guide creation with step-by-step procedures and troubleshooting
- Accessibility standards application and inclusive language usage

**Examples**:
1. **API Documentation**: Comprehensive REST API docs with authentication, endpoints, examples, and SDK integration guides
2. **User Manual**: Step-by-step installation and configuration guide with screenshots, troubleshooting, and FAQ sections
3. **Technical Specification**: System architecture documentation with diagrams, data flows, and implementation details

**Works Best With**: requirements-analyst (specification clarity), learning-guide (educational content), frontend-architect (UI documentation)

---

### learning-guide 🎓
**Expertise**: Educational content design and progressive learning with focus on skill development and mentorship

**Auto-Activation**:
- Keywords: "explain", "learn", "tutorial", "beginner", "teaching", "education", "training"
- Context: Educational requests, concept explanations, skill development, learning paths
- Complexity: Complex topics requiring step-by-step breakdown and progressive understanding

**Capabilities**:
- Learning path design with progressive skill development
- Complex concept explanation through analogies and examples
- Interactive tutorial creation with hands-on exercises
- Skill assessment and competency evaluation frameworks
- Mentorship strategies and personalized learning approaches

**Examples**:
1. **Programming Tutorial**: Interactive React tutorial with hands-on exercises, code examples, and progressive complexity
2. **Concept Explanation**: Database normalization explained through real-world examples with visual diagrams and practice exercises
3. **Skill Assessment**: Comprehensive evaluation framework for full-stack development with practical projects and feedback

**Works Best With**: technical-writer (educational documentation), frontend-architect (interactive learning), requirements-analyst (learning objectives)

---

## Agent Coordination & Integration 🤝

### Coordination Patterns

**Architecture Teams**:
- **Full-Stack Development**: frontend-architect + backend-architect + security-engineer + quality-engineer
- **System Design**: system-architect + devops-architect + performance-engineer + security-engineer
- **Legacy Modernization**: refactoring-expert + system-architect + quality-engineer + technical-writer

**Quality Teams**:
- **Security Audit**: security-engineer + quality-engineer + root-cause-analyst + requirements-analyst
- **Performance Optimization**: performance-engineer + system-architect + devops-architect + root-cause-analyst
- **Testing Strategy**: quality-engineer + security-engineer + performance-engineer + frontend-architect

**Communication Teams**:
- **Documentation Project**: technical-writer + requirements-analyst + learning-guide + domain experts
- **Learning Platform**: learning-guide + frontend-architect + technical-writer + quality-engineer
- **API Documentation**: backend-architect + technical-writer + security-engineer + quality-engineer

### MCP Server Integration

**Enhanced Capabilities through MCP Servers**:
- **Context7**: Official documentation patterns for all architects and specialists
- **Sequential**: Multi-step analysis for root-cause-analyst, system-architect, performance-engineer
- **Magic**: UI generation for frontend-architect, learning-guide interactive content
- **Playwright**: Browser testing for quality-engineer, accessibility validation for frontend-architect
- **Morphllm**: Code transformation for refactoring-expert, bulk changes for python-expert
- **Serena**: Project memory for all agents, context preservation across sessions

### Troubleshooting Agent Activation

## Troubleshooting

For troubleshooting help, see:
- [Common Issues](../Reference/common-issues.md) - Quick fixes for frequent problems
- [Troubleshooting Guide](../Reference/troubleshooting.md) - Comprehensive problem resolution

### Common Issues
- **No agent activation**: Use domain keywords: "security", "performance", "frontend"
- **Wrong agents selected**: Check trigger keywords in agent documentation
- **Too many agents**: Focus keywords on primary domain or use `/sc:focus [domain]`
- **Agents not coordinating**: Increase task complexity or use multi-domain keywords
- **Agent expertise mismatch**: Use more specific technical terminology

### Immediate Fixes
- **Force agent activation**: Use explicit domain keywords in requests
- **Reset agent selection**: Restart Claude Code session to reset agent state
- **Check agent patterns**: Review trigger keywords in agent documentation
- **Test basic activation**: Try `/sc:implement "security auth"` to test security-engineer

### Agent-Specific Troubleshooting

**No Security Agent:**
```bash
# Problem: Security concerns not triggering security-engineer
# Quick Fix: Use explicit security keywords
"implement authentication"              # Generic - may not trigger
"implement JWT authentication security" # Explicit - triggers security-engineer
"secure user login with encryption"    # Security focus - triggers security-engineer
```

**No Performance Agent:**
```bash
# Problem: Performance issues not triggering performance-engineer
# Quick Fix: Use performance-specific terminology
"make it faster"                       # Vague - may not trigger
"optimize slow database queries"       # Specific - triggers performance-engineer  
"reduce API latency and bottlenecks"   # Performance focus - triggers performance-engineer
```

**No Architecture Agent:**
```bash
# Problem: System design not triggering architecture agents
# Quick Fix: Use architectural keywords
"build an app"                         # Generic - triggers basic agents
"design microservices architecture"    # Specific - triggers system-architect
"scalable distributed system design"   # Architecture focus - triggers system-architect
```

**Wrong Agent Combination:**
```bash
# Problem: Getting frontend agent for backend tasks
# Quick Fix: Use domain-specific terminology
"create user interface"                # May trigger frontend-architect
"create REST API endpoints"            # Specific - triggers backend-architect
"implement server-side authentication" # Backend focus - triggers backend-architect
```

### Support Levels

**Quick Fix:**
- Use explicit domain keywords from agent trigger table
- Try restarting Claude Code session
- Focus on single domain to avoid confusion

**Detailed Help:**
- See [Common Issues Guide](../Reference/common-issues.md) for agent installation problems
- Review trigger keywords for target agents

**Expert Support:**  
- Use `SuperClaude install --diagnose`
- See [Diagnostic Reference Guide](../Reference/diagnostic-reference.md) for coordination analysis

**Community Support:**
- Report issues at [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)
- Include examples of expected vs actual agent activation

### Success Validation

After applying agent fixes, test with:
- [ ] Domain-specific requests activate correct agents (security → security-engineer)
- [ ] Complex tasks trigger multi-agent coordination (3+ agents)
- [ ] Agent expertise matches task requirements (API → backend-architect)
- [ ] Quality agents auto-include when appropriate (security, performance, testing)
- [ ] Responses show domain expertise and specialized knowledge

## Quick Troubleshooting (Legacy)
- **No agent activation** → Use domain keywords: "security", "performance", "frontend"
- **Wrong agents** → Check trigger keywords in agent documentation
- **Too many agents** → Focus keywords on primary domain
- **Agents not coordinating** → Increase task complexity or use multi-domain keywords

**Agent Not Activating?**
1. **Check Keywords**: Use domain-specific terminology (e.g., "authentication" not "login" for security-engineer)
2. **Add Context**: Include file types, frameworks, or specific technologies
3. **Increase Complexity**: Multi-domain problems trigger more agents
4. **Use Examples**: Reference concrete scenarios that match agent expertise

**Too Many Agents?**
- Focus keywords on primary domain needs
- Use `/sc:focus [domain]` to limit scope
- Start with specific agents, expand as needed

**Wrong Agents?**
- Review trigger keywords in agent documentation
- Use more specific terminology for target domain
- Add explicit requirements or constraints

## Quick Reference 📋

### Agent Trigger Lookup

| Trigger Type | Keywords/Patterns | Activated Agents |
|-------------|-------------------|------------------|
| **Security** | "auth", "security", "vulnerability", "encryption" | security-engineer |
| **Performance** | "slow", "optimization", "bottleneck", "latency" | performance-engineer |
| **Frontend** | "UI", "React", "Vue", "component", "responsive" | frontend-architect |
| **Backend** | "API", "server", "database", "REST", "GraphQL" | backend-architect |
| **Testing** | "test", "QA", "validation", "coverage" | quality-engineer |
| **DevOps** | "deploy", "CI/CD", "Docker", "Kubernetes" | devops-architect |
| **Architecture** | "architecture", "microservices", "scalability" | system-architect |
| **Python** | ".py", "Django", "FastAPI", "asyncio" | python-expert |
| **Problems** | "bug", "issue", "debugging", "troubleshoot" | root-cause-analyst |
| **Code Quality** | "refactor", "clean code", "technical debt" | refactoring-expert |
| **Documentation** | "documentation", "readme", "API docs" | technical-writer |
| **Learning** | "explain", "tutorial", "beginner", "teaching" | learning-guide |
| **Requirements** | "requirements", "PRD", "specification" | requirements-analyst |
| **Research** | "research", "investigate", "latest", "current" | deep-research-agent |

### Command-Agent Mapping

| Command | Primary Agents | Supporting Agents |
|---------|----------------|-------------------|
| `/sc:implement` | Domain architects (frontend, backend) | security-engineer, quality-engineer |
| `/sc:analyze` | quality-engineer, security-engineer | performance-engineer, root-cause-analyst |
| `/sc:troubleshoot` | root-cause-analyst | Domain specialists, performance-engineer |
| `/sc:improve` | refactoring-expert | quality-engineer, performance-engineer |
| `/sc:document` | technical-writer | Domain specialists, learning-guide |
| `/sc:design` | system-architect | Domain architects, requirements-analyst |
| `/sc:test` | quality-engineer | security-engineer, performance-engineer |
| `/sc:explain` | learning-guide | technical-writer, domain specialists |
| `/sc:research` | deep-research-agent | Technical specialists, learning-guide |

### Effective Agent Combinations

**Development Workflows**:
- Web application: frontend-architect + backend-architect + security-engineer + quality-engineer + devops-architect
- API development: backend-architect + security-engineer + technical-writer + quality-engineer  
- Data platform: python-expert + performance-engineer + security-engineer + system-architect

**Analysis Workflows**:
- Security audit: security-engineer + quality-engineer + root-cause-analyst + technical-writer
- Performance investigation: performance-engineer + root-cause-analyst + system-architect + devops-architect
- Legacy assessment: refactoring-expert + system-architect + quality-engineer + security-engineer + technical-writer

**Communication Workflows**:
- Technical documentation: technical-writer + requirements-analyst + domain experts + learning-guide
- Educational content: learning-guide + technical-writer + frontend-architect + quality-engineer

## Best Practices 💡

### Getting Started (Simple Approach)

**Natural Language First:**
1. **Describe Your Goal**: Use natural language with domain-specific keywords
2. **Trust Auto-Activation**: Let the system route to appropriate agents automatically  
3. **Learn from Patterns**: Observe which agents activate for different request types
4. **Iterate and Refine**: Add specificity to engage additional specialist agents

### Optimizing Agent Selection

**Effective Keyword Usage:**
- **Specific > Generic**: Use "authentication" instead of "login" for security-engineer
- **Technical Terms**: Include framework names, technologies, and specific challenges
- **Context Clues**: Mention file types, project scope, and complexity indicators
- **Quality Keywords**: Add "security", "performance", "accessibility" for comprehensive coverage

**Request Optimization Examples:**
```bash
# Generic (limited agent activation)
"Fix the login feature"

# Optimized (multi-agent coordination)  
"Implement secure JWT authentication with rate limiting and accessibility compliance"
# → Triggers: security-engineer + backend-architect + frontend-architect + quality-engineer
```

### Common Usage Patterns

**Development Workflows:**
```bash
# Full-stack feature development
/sc:implement "responsive user dashboard with real-time notifications"
# → frontend-architect + backend-architect + performance-engineer

# API development with documentation
/sc:create "REST API for payment processing with comprehensive docs"  
# → backend-architect + security-engineer + technical-writer + quality-engineer

# Performance optimization investigation
/sc:troubleshoot "slow database queries affecting user experience"
# → performance-engineer + root-cause-analyst + backend-architect
```

**Analysis Workflows:**
```bash
# Security assessment
/sc:analyze "authentication system for GDPR compliance vulnerabilities"
# → security-engineer + quality-engineer + requirements-analyst

# Code quality review  
/sc:review "legacy codebase for modernization opportunities"
# → refactoring-expert + system-architect + quality-engineer + technical-writer

# Learning and explanation
/sc:explain "microservices patterns with hands-on examples"
# → system-architect + learning-guide + technical-writer
```

### Advanced Agent Coordination

**Multi-Domain Projects:**
- **Start Broad**: Begin with system-level keywords to engage architecture agents
- **Add Specificity**: Include domain-specific needs to activate specialist agents  
- **Quality Integration**: Automatically include security, performance, and testing perspectives
- **Documentation Inclusion**: Add learning or documentation needs for comprehensive coverage

**Troubleshooting Agent Selection:**

**Problem: Wrong agents activating**
- Solution: Use more specific domain terminology
- Example: "database optimization" → performance-engineer + backend-architect

**Problem: Not enough agents**  
- Solution: Increase complexity indicators and cross-domain keywords
- Example: Add "security", "performance", "documentation" to requests

**Problem: Too many agents**
- Solution: Focus on primary domain with specific technical terms
- Example: Use "/sc:focus backend" to limit scope

### Quality-Driven Development

**Security-First Approach:**
Always include security considerations in development requests to automatically engage security-engineer alongside domain specialists.

**Performance Integration:**
Include performance keywords ("fast", "efficient", "scalable") to ensure performance-engineer coordination from the start.

**Accessibility Compliance:**
Use "accessible", "WCAG", or "inclusive" to automatically include accessibility validation in frontend development.

**Documentation Culture:**
Add "documented", "explained", or "tutorial" to requests for automatic technical-writer inclusion and knowledge transfer.

---

## Understanding Agent Intelligence 🧠

### What Makes Agents Effective

**Domain Expertise**: Each agent has specialized knowledge patterns, behavioral approaches, and problem-solving methodologies specific to their domain.

**Contextual Activation**: Agents analyze request context, not just keywords, to determine relevance and engagement level.

**Collaborative Intelligence**: Multi-agent coordination produces synergistic results that exceed individual agent capabilities.

**Adaptive Learning**: Agent selection improves based on request patterns and successful coordination outcomes.

### Agent vs. Traditional AI

**Traditional Approach**: Single AI handles all domains with varying levels of expertise
**Agent Approach**: Specialized experts collaborate with deep domain knowledge and focused problem-solving

**Benefits**:
- Higher accuracy in domain-specific tasks
- More sophisticated problem-solving methodologies  
- Better quality assurance through specialist review
- Coordinated multi-perspective analysis

### Trust the System, Understand the Patterns

**What to Expect**:
- Automatic routing to appropriate domain experts
- Multi-agent coordination for complex tasks
- Quality integration through automatic QA agent inclusion
- Learning opportunities through educational agent activation

**What Not to Worry About**:
- Manual agent selection or configuration
- Complex routing rules or agent management
- Agent configuration or coordination
- Micromanaging agent interactions

---

## Related Resources 📚

### Essential Documentation
- **[Commands Guide](commands.md)** - Master SuperClaude commands that trigger optimal agent coordination
- **[MCP Servers](mcp-servers.md)** - Enhanced agent capabilities through specialized tool integration  
- **[Session Management](session-management.md)** - Long-term workflows with persistent agent context

### Advanced Usage  
- **[Behavioral Modes](modes.md)** - Context optimization for enhanced agent coordination
- **[Getting Started](../Getting-Started/quick-start.md)** - Expert techniques for agent optimization
- **[Examples Cookbook](../Reference/examples-cookbook.md)** - Real-world agent coordination patterns

### Development Resources
- **[Technical Architecture](../Developer-Guide/technical-architecture.md)** - Understanding SuperClaude's agent system design
- **[Contributing](../Developer-Guide/contributing-code.md)** - Extending agent capabilities and coordination patterns

---

## Your Agent Journey 🚀

**Week 1: Natural Usage**
Start with natural language descriptions. Notice which agents activate and why. Build intuition for keyword patterns without overthinking the process.

**Week 2-3: Pattern Recognition**  
Observe agent coordination patterns. Understand how complexity and domain keywords influence agent selection. Begin optimizing request phrasing for better coordination.

**Month 2+: Expert Coordination**
Master multi-domain requests that trigger optimal agent combinations. Leverage troubleshooting techniques for effective agent selection. Use advanced patterns for complex workflows.

**The SuperClaude Advantage:**
Experience the power of 14 specialized AI experts working in coordinated response, all through simple, natural language requests. No configuration, no management, just intelligent collaboration that scales with your needs.

🎯 **Ready to experience intelligent agent coordination? Start with `/sc:implement` and discover the magic of specialized AI collaboration.**