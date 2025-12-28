---
name: troubleshoot
description: "Diagnose and resolve issues in code, builds, deployments, and system behavior"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

# /sc:troubleshoot - Issue Diagnosis and Resolution

## Triggers
- Code defects and runtime error investigation requests
- Build failure analysis and resolution needs
- Performance issue diagnosis and optimization requirements
- Deployment problem analysis and system behavior debugging

## Usage
```
/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```

## Behavioral Flow
1. **Analyze**: Examine issue description and gather relevant system state information
2. **Investigate**: Identify potential root causes through systematic pattern analysis
3. **Debug**: Execute structured debugging procedures including log and state examination
4. **Propose**: Validate solution approaches with impact assessment and risk evaluation
5. **Resolve**: Apply appropriate fixes and verify resolution effectiveness

Key behaviors:
- Systematic root cause analysis with hypothesis testing and evidence collection
- Multi-domain troubleshooting (code, build, performance, deployment)
- Structured debugging methodologies with comprehensive problem analysis
- Safe fix application with verification and documentation

## Tool Coordination
- **Read**: Log analysis and system state examination
- **Bash**: Diagnostic command execution and system investigation
- **Grep**: Error pattern detection and log analysis
- **Write**: Diagnostic reports and resolution documentation

## Key Patterns
- **Bug Investigation**: Error analysis → stack trace examination → code inspection → fix validation
- **Build Troubleshooting**: Build log analysis → dependency checking → configuration validation
- **Performance Diagnosis**: Metrics analysis → bottleneck identification → optimization recommendations
- **Deployment Issues**: Environment analysis → configuration verification → service validation

## Examples

### Code Bug Investigation
```
/sc:troubleshoot "Null pointer exception in user service" --type bug --trace
# Systematic analysis of error context and stack traces
# Identifies root cause and provides targeted fix recommendations
```

### Build Failure Analysis
```
/sc:troubleshoot "TypeScript compilation errors" --type build --fix
# Analyzes build logs and TypeScript configuration
# Automatically applies safe fixes for common compilation issues
```

### Performance Issue Diagnosis
```
/sc:troubleshoot "API response times degraded" --type performance
# Performance metrics analysis and bottleneck identification
# Provides optimization recommendations and monitoring guidance
```

### Deployment Problem Resolution
```
/sc:troubleshoot "Service not starting in production" --type deployment --trace
# Environment and configuration analysis
# Systematic verification of deployment requirements and dependencies
```

## Boundaries

**Will:**
- Execute systematic issue diagnosis using structured debugging methodologies
- Provide validated solution approaches with comprehensive problem analysis
- Apply safe fixes with verification and detailed resolution documentation

**Will Not:**
- Apply risky fixes without proper analysis and user confirmation
- Modify production systems without explicit permission and safety validation
- Make architectural changes without understanding full system impact