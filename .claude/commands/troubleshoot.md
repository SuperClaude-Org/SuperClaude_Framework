# /troubleshoot - Debug and resolve issues systematically

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
Debug and resolve issues in code or systems specified in $ARGUMENTS using systematic troubleshooting methodologies and analysis techniques.

## Syntax
`/troubleshoot [flags] [issue-description]`

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

**Troubleshooting Modes:**
- `--investigate`: Focus on understanding and analyzing issues without immediate fixes
- `--fix`: Complete bug-fixing workflow with testing and verification (default)
- `--analyze`: Deep technical analysis of complex system interactions
- `--diagnose`: Systematic diagnostic approach with structured methodology

**Analysis Methods:**
- `--five-whys`: Apply root cause analysis methodology iteratively
- `--binary-search`: Use binary search approach to isolate problem scope
- `--timeline`: Analyze issue timeline and recent changes
- `--dependencies`: Focus on dependency and integration issues

**Environment Focus:**
- `--prod`: Production-specific issue handling with minimal disruption
- `--staging`: Staging environment debugging and testing
- `--local`: Local development environment troubleshooting
- `--cross-env`: Cross-environment consistency analysis

**Investigation Tools:**
- `--logs`: Focus on log analysis and pattern detection
- `--performance`: Performance profiling and bottleneck analysis
- `--security`: Security-focused investigation and vulnerability analysis
- `--network`: Network connectivity and API integration debugging

## Examples
- `/troubleshoot --investigate --logs --think` → Log analysis with context
- `/troubleshoot --five-whys --prod --think-hard` → Production root cause analysis
- `/troubleshoot --fix --performance --ultrathink` → Performance issue resolution
- `/troubleshoot --binary-search --dependencies` → Systematic dependency debugging
- `/troubleshoot --analyze --security --network` → Security and network analysis

## Troubleshooting Workflow

**1. Issue Reproduction and Understanding**
- **Minimal Reproduction**: Create smallest possible reproduction case
- **Behavior Documentation**: Document expected vs actual behavior clearly
- **Impact Assessment**: Identify affected components, users, and business impact
- **Severity Classification**: Determine urgency and priority level
- **Environment Analysis**: Understand where and when the issue occurs

**2. Investigation and Isolation**
- **Tool Utilization**: Apply debugging tools and strategic logging
- **Scope Narrowing**: Use binary search to isolate problem area
- **Change Analysis**: Review recent changes using git history and blame
- **Data Collection**: Analyze logs, stack traces, and monitoring data
- **Factor Elimination**: Rule out environmental and configuration factors

**3. Root Cause Analysis**
- **Underlying Causes**: Look beyond symptoms to find root causes
- **Five-Whys Method**: Apply iterative questioning technique
- **Systemic Analysis**: Consider broader system and process issues
- **Contributing Factors**: Document all factors that led to the issue
- **Pattern Recognition**: Identify similar issues and common causes

**4. Solution Development (--fix mode)**
- **Test Creation**: Write failing test that reproduces the issue
- **Minimal Fix**: Implement focused solution addressing root cause
- **Compatibility**: Ensure backward compatibility and minimal disruption
- **Edge Cases**: Consider side effects and edge case scenarios
- **Code Review**: Apply standard code review and quality practices

**5. Verification and Prevention**
- **Fix Validation**: Verify solution resolves issue completely
- **Regression Testing**: Run full test suite to prevent regressions
- **Realistic Testing**: Test in production-like conditions
- **Monitoring**: Add monitoring and alerting for early detection
- **Documentation**: Record lessons learned and prevention measures

## Investigation Techniques

**Debugging Approaches:**
- **Strategic Logging**: Add targeted logging at key decision points
- **Breakpoint Analysis**: Use debugger breakpoints for step-through analysis
- **State Inspection**: Examine variable states and data structures
- **Call Stack Analysis**: Trace execution paths and function calls
- **Memory Debugging**: Analyze memory usage and potential leaks

**Performance Analysis:**
- **Profiling Tools**: Use performance profilers for bottleneck identification
- **Resource Monitoring**: Track CPU, memory, and I/O usage patterns
- **Query Analysis**: Analyze database queries and execution plans
- **Network Inspection**: Monitor network requests and response times
- **Caching Evaluation**: Assess caching effectiveness and hit rates

**System Analysis:**
- **Configuration Review**: Examine system and application configurations
- **Dependency Mapping**: Map and analyze component dependencies
- **Integration Testing**: Test inter-service communication and APIs
- **Infrastructure Analysis**: Review infrastructure and deployment setup
- **Security Assessment**: Analyze security configurations and access controls

## Five-Whys Analysis (--five-whys)

**Methodology:**
1. **Problem Statement**: Clearly define the observed problem
2. **First Why**: Why did this problem occur? (immediate cause)
3. **Second Why**: Why did that cause occur? (deeper cause)
4. **Third Why**: Why did that deeper cause occur? (root cause)
5. **Fourth Why**: Why does that root cause exist? (systemic cause)
6. **Fifth Why**: Why is that system in place? (organizational cause)

**Documentation:**
- Record each level of analysis with evidence
- Document contributing factors at each level
- Identify prevention measures for each cause
- Propose systemic improvements to prevent recurrence
- Create action items for short-term and long-term fixes

## Production Issue Handling (--prod)

**Production-Specific Considerations:**
- **Minimal Disruption**: Prioritize system stability and user experience
- **Rollback Readiness**: Prepare immediate rollback options
- **Monitoring Integration**: Use existing monitoring and alerting systems
- **Communication**: Maintain stakeholder communication throughout
- **Documentation**: Record all changes and decisions for audit trail

**Production Analysis:**
- **Deployment Correlation**: Correlate issues with recent deployments
- **Traffic Patterns**: Analyze user traffic and usage patterns
- **Configuration Changes**: Review recent configuration modifications
- **Resource Utilization**: Monitor system resource usage and limits
- **Service Dependencies**: Check health of dependent services

**Safe Production Practices:**
- **Feature Flags**: Use feature toggles to isolate problematic features
- **Gradual Rollout**: Implement fixes gradually with monitoring
- **A/B Testing**: Compare fix effectiveness with control groups
- **Circuit Breakers**: Implement circuit breakers for failing services
- **Health Checks**: Continuous health monitoring during fixes

## Investigation Tools and Techniques

**Logging and Monitoring:**
- Centralized log aggregation and analysis
- Real-time monitoring dashboards and alerts
- Distributed tracing for microservices
- Application performance monitoring (APM)
- Custom metrics and business intelligence

**Debugging Tools:**
- Interactive debuggers and IDE integration
- Remote debugging capabilities
- Memory profilers and leak detectors
- Performance profiling tools
- Network traffic analyzers

**Testing and Validation:**
- Unit test creation for bug reproduction
- Integration testing for component interactions
- Load testing for performance issues
- Security testing for vulnerability assessment
- Chaos engineering for resilience testing

## Deliverables
- **Investigation Report**: Comprehensive analysis of issue and findings
- **Root Cause Analysis**: Detailed five-whys analysis with evidence
- **Solution Documentation**: Fix implementation with rationale
- **Prevention Plan**: Measures to prevent similar issues
- **Monitoring Enhancements**: Improved detection and alerting
- **Lessons Learned**: Knowledge base updates and team learnings

## Output Locations
- **Incident Reports**: `.claudedocs/incidents/rca-{issue}-{timestamp}.md`
- **Investigation Logs**: `.claudedocs/reports/troubleshoot-{timestamp}.md`
- **Solution Documentation**: `.claudedocs/summaries/fix-{issue}-{timestamp}.md`

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

## Best Practices

**Systematic Approach:**
- Follow structured troubleshooting methodology
- Document findings and decisions throughout process
- Maintain objectivity and avoid assumption-based debugging
- Use data and evidence to drive investigation
- Consider multiple hypotheses before settling on solutions

**Collaboration and Communication:**
- Involve relevant team members and stakeholders
- Communicate status and findings regularly
- Share knowledge and learnings with team
- Document solutions for future reference
- Conduct post-incident reviews for improvement

**Prevention Focus:**
- Address root causes, not just symptoms
- Implement monitoring and alerting improvements
- Update processes and procedures based on learnings
- Enhance testing and quality assurance practices
- Build resilience and error handling into systems

## Common Error Scenarios

### Database Connection Issues
```bash
/troubleshoot --investigate --dependencies "connection timeout"
# → Checks DB connectivity, credentials, network latency
# → Verifies connection pool settings and timeouts
# → Tests failover mechanisms and retry logic
```

### Memory Leaks & Performance
```bash
/troubleshoot --performance --logs --binary-search
# → Profiles memory usage patterns over time
# → Identifies allocation hotspots and retention issues
# → Implements heap dump analysis and GC tuning
```

### Production Emergencies
```bash
/troubleshoot --prod --investigate --timeline --critical
# → Creates incident timeline with system events
# → Preserves logs and state for post-mortem analysis
# → Implements safe rollback procedures if needed
```

### Integration & API Failures
```bash
/troubleshoot --dependencies --network --cross-env
# → Tests API endpoints and service dependencies
# → Validates authentication and authorization flows
# → Checks rate limiting and circuit breaker status
```

## Troubleshooting
- **Complex Issues**: Use `--ultrathink --five-whys` for comprehensive analysis
- **Production Emergencies**: Apply `--prod --investigate --timeline` for safe handling
- **Performance Problems**: Combine `--performance --logs --binary-search`
- **Integration Issues**: Use `--dependencies --network --cross-env`

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
