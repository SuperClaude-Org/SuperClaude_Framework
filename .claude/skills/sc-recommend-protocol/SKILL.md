---
name: sc:recommend-protocol
description: "Full behavioral protocol for sc:recommend — ultra-intelligent command recommendation engine with multi-language support, context detection, and estimation"
allowed-tools: Read, Glob, Grep, Bash, TodoWrite
---

# /sc:recommend — Command Recommendation Protocol

## Triggers

sc:recommend-protocol is invoked ONLY by the `sc:recommend` command via `Skill sc:recommend-protocol` in the `## Activation` section. It is never invoked directly by users.

Activation conditions:
- User runs `/sc:recommend [query]` in Claude Code
- Any `--estimate`, `--alternatives`, `--stream`, `--community` flags are passed through

Do NOT invoke this skill directly. Use the `sc:recommend` command.

## Multi-language Support

### Language Detection
- Turkish: Detect via Turkish-specific characters (ç, ğ, ı, ö, ş, ü)
- English: Detect via common English words (the, and, is, are, etc.)
- Default: English when uncertain
- Mixed language inputs handled with keyword mapping

## Keyword Extraction and Persona Matching

### Pattern Matching Categories

| Pattern | Category | Personas |
|---------|----------|----------|
| machine learning, ml, ai | ml_category | analyzer, architect |
| website, frontend, ui/ux, react, vue | web_category | frontend, qa |
| api, backend, server, microservice | api_category | backend, security |
| error, bug, issue, not working | debug_category | analyzer, security |
| slow, performance, optimization | performance_category | performance, analyzer |
| security, auth, vulnerability | security_category | security, analyzer |
| new, create, build, develop | create_category | frontend, backend, architect |
| test, qa, quality, validation | test_category | qa, performance |
| how, learn, explain, tutorial | learning_category | mentor, analyzer |
| refactor, cleanup, improve | improve_category | refactorer, mentor |

### Context Analysis
- beginner/starter → beginner_level + mentor persona
- expert/senior → expert_level + architect persona
- continue/resume → continuity_mode + sequential thinking
- next step → next_step_mode + thinking flags

## Command Map by Category

### ml_category
- Primary: `/sc:analyze --seq --c7`, `/sc:design --seq --ultrathink`
- Secondary: `/sc:build --feature --tdd`, `/sc:improve --performance`
- MCP: --c7, --seq | Flags: --think-hard, --evidence

### web_category
- Primary: `/sc:build --feature --magic`, `/sc:design --api --seq`
- Secondary: `/sc:test --coverage --e2e --pup`, `/sc:analyze --code`
- MCP: --magic, --c7, --pup | Flags: --react, --tdd

### api_category
- Primary: `/sc:design --api --ddd --seq`, `/sc:build --feature --tdd`
- Secondary: `/sc:scan --security --owasp`, `/sc:analyze --performance`
- MCP: --seq, --c7, --pup | Flags: --microservices, --ultrathink

### debug_category
- Primary: `/sc:troubleshoot --investigate --seq`, `/sc:analyze --code --seq`
- Secondary: `/sc:scan --security`, `/sc:improve --quality`
- MCP: --seq, --all-mcp | Flags: --evidence, --think-hard

### performance_category
- Primary: `/sc:analyze --performance --pup --profile`, `/sc:troubleshoot --seq`
- Secondary: `/sc:improve --performance --iterate`, `/sc:build --optimize`
- MCP: --pup, --seq | Flags: --profile, --benchmark

### security_category
- Primary: `/sc:scan --security --owasp --deps`, `/sc:analyze --security --seq`
- Secondary: `/sc:improve --security --harden`
- MCP: --seq | Flags: --strict, --validate, --owasp

### create_category
- Primary: `/sc:build --feature --tdd`, `/sc:design --seq --ultrathink`
- Secondary: `/sc:analyze --code --c7`, `/sc:test --coverage --e2e`
- MCP: --magic, --c7, --pup | Flags: --interactive, --plan

### test_category
- Primary: `/sc:test --coverage --e2e --pup`, `/sc:scan --validate`
- Secondary: `/sc:improve --quality`
- MCP: --pup | Flags: --validate, --coverage

### improve_category
- Primary: `/sc:improve --quality --iterate`, `/sc:cleanup --code --all`
- Secondary: `/sc:analyze --code --seq`
- MCP: --seq | Flags: --threshold, --iterate

### learning_category
- Primary: `/sc:document --user --examples`, `/sc:analyze --code --c7`
- Secondary: `/sc:brainstorm --interactive`
- MCP: --c7 | Flags: --examples, --interactive

## Expertise Level Customization

| Level | Style | Extra Explanations |
|-------|-------|--------------------|
| Beginner | Detailed, step-by-step | Yes |
| Intermediate | Balanced, technical | Some |
| Expert | Fast, direct | Minimal |

## Project Context Detection

### File System Analysis
- React: package.json with react, src/App.jsx → frontend commands + magic
- Vue: package.json with vue, src/App.vue → frontend commands + magic
- Node API: express in package.json, routes/, controllers/ → backend + security
- Python: requirements.txt, setup.py → analyzer + architect
- Database: schema.sql, migrations/ → backend + security

### Project Size
- Small (<50 files): Direct implementation
- Medium (50-200): Plan → analyze → implement
- Large (>200): Comprehensive analysis → design → implement

## Streaming Mode

Continuous recommendation throughout project lifecycle:
1. Analysis & Planning → 2. Implementation → 3. Testing → 4. Deployment

## Alternative Recommendation Engine

When `--alternatives` flag:
- Present primary recommendation
- 2-3 alternative approaches with pros/cons
- Comparison matrix
- Community preference percentages

## Time and Budget Estimation

When `--estimate` flag:

### Complexity Factors
- Project type: simple component (1-3d) to enterprise (3-6mo)
- Experience multiplier: beginner 2.0x, intermediate 1.5x, expert 1.0x
- Scope: small 1.0x, medium 1.5x, large 2.5x, enterprise 4.0x

### Time Distribution
- ML: data 20-30%, preprocessing 15-25%, training 10-20%, eval 10-15%, deploy 15-25%
- Web: design 15-25%, frontend 30-40%, backend 25-35%, testing 10-20%, deploy 5-15%

## Smart Flag Recommendations

### Context-Based
- Small project: --quick --simple
- Medium: --plan --validate --profile
- Large: --plan --validate --seq --ultrathink

### Security Requirements
- Basic: --basic-security
- Standard: --security --validate
- Enterprise: --security --owasp --strict --audit

### History-Based
- Previous errors: --validate --dry-run --backup
- Security issues: --security --scan --strict
- Performance issues: --profile --optimize --monitor

## Response Format

Standard output structure:
1. Header: Project analysis, language detection, level, persona
2. Main: 3 primary commands, additional recommendations, quick start
3. Enhanced: Smart flags, time estimate, alternatives, community data
