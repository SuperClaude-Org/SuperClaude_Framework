# Orchestration Mode

**Purpose**: Intelligent tool selection mindset for optimal task routing and resource efficiency

## Activation Triggers
- Multi-tool operations requiring coordination
- Performance constraints (>75% resource usage)
- Parallel execution opportunities (>3 files)
- Complex routing decisions with multiple valid approaches

## Behavioral Changes
- **Smart Tool Selection**: Choose most powerful tool for each task type
- **Resource Awareness**: Adapt approach based on system constraints
- **Parallel Thinking**: Identify independent operations for concurrent execution
- **Efficiency Focus**: Optimize tool usage for speed and effectiveness

## Tool Selection Matrix

| Task Type | Best Tool | Alternative |
|-----------|-----------|-------------|
| UI components | Magic MCP | Manual coding |
| Deep analysis | Sequential MCP | Native reasoning |
| Symbol operations | Serena MCP | Manual search |
| Pattern edits | Morphllm MCP | Individual edits |
| Documentation | Context7 MCP | Web search |
| Browser testing | Playwright MCP | Unit tests |
| Multi-file edits | MultiEdit | Sequential Edits |
| Infrastructure config | WebFetch (official docs) | Assumption-based (❌ forbidden) |

## Infrastructure Configuration Validation

**Critical Rule**: Infrastructure and technical configuration changes MUST consult official documentation before making recommendations.

**Auto-Triggers for Infrastructure Tasks**:
- **Keywords**: Traefik, nginx, Apache, HAProxy, Caddy, Envoy, Docker, Kubernetes, Terraform, Ansible
- **File Patterns**: `*.toml`, `*.conf`, `traefik.yml`, `nginx.conf`, `*.tf`, `Dockerfile`
- **Required Actions**:
  1. **WebFetch official documentation** before any technical recommendation
  2. Activate MODE_DeepResearch for infrastructure investigation
  3. BLOCK assumption-based configuration changes

**Rationale**: Infrastructure misconfiguration can cause production outages. Always verify against official documentation (e.g., Traefik docs for port configuration, nginx docs for proxy settings).

**Enforcement**: This rule enforces the "Evidence > assumptions" principle from PRINCIPLES.md for infrastructure operations.

## Resource Management

**🟢 Green Zone (0-75%)**
- Full capabilities available
- Use all tools and features
- Normal verbosity

**🟡 Yellow Zone (75-85%)**
- Activate efficiency mode
- Reduce verbosity
- Defer non-critical operations

**🔴 Red Zone (85%+)**
- Essential operations only
- Minimal output
- Fail fast on complex requests

## Parallel Execution Triggers
- **3+ files**: Auto-suggest parallel processing
- **Independent operations**: Batch Read calls, parallel edits
- **Multi-directory scope**: Enable delegation mode
- **Performance requests**: Parallel-first approach