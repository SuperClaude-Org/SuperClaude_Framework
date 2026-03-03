# MCP Gateway Alternatives to AIRIS

**Date**: 2026-02-25
**Query**: Alternatives to AIRIS MCP Gateway for centralized MCP server management
**Context**: Running inside Coder dev containers; need something that can run externally and serve multiple environments
**Confidence**: High (multiple corroborating sources)

---

## Executive Summary

There are **3 tiers** of alternatives to AIRIS, depending on what you need:

1. **Full Gateway/Aggregators** — Run centrally, expose one endpoint, many tools behind it (closest to AIRIS)
2. **Transport Bridges** — Lightweight proxies that convert stdio ↔ SSE so you can run servers anywhere
3. **Enterprise/Infrastructure Gateways** — Kubernetes-native, production-grade routing with auth, rate limiting, observability

For your use case (central server accessible from multiple Coder dev containers), **Tier 1 and Tier 2** are most relevant.

---

## Tier 1: Full Gateway/Aggregators (AIRIS-like)

### 1. MetaMCP
**What it is**: All-in-one MCP Aggregator/Orchestrator/Middleware/Gateway in a single Docker Compose stack. Web UI for managing servers, namespacing, tool-level enable/disable, middleware hooks.

| Factor | Details |
|--------|---------|
| **Transport** | SSE + Streamable HTTP endpoints |
| **Setup** | Docker Compose (`docker compose up`) |
| **UI** | Web admin on `localhost:12008` |
| **Auth** | API key support |
| **Client config** | Claude Code connects via `npx` proxy or SSE URL |
| **Maturity** | Active development, community-driven |

**Best for**: Closest drop-in replacement for AIRIS. Docker-based, has a UI, aggregates many servers behind one endpoint.

- [MetaMCP Official Site](https://metamcp.com/)
- [GitHub: metatool-ai/metamcp](https://github.com/metatool-ai/metamcp)
- [MetaMCP Quick Start Docs](https://docs.metamcp.com/en/quickstart)

### 2. Docker MCP Gateway (Docker MCP Toolkit)
**What it is**: Docker's official MCP gateway. Part of the Docker MCP Catalog & Toolkit. Runs MCP servers as Docker containers behind a single gateway endpoint. First-class Claude Code integration via `docker mcp client connect claude-code`.

| Factor | Details |
|--------|---------|
| **Transport** | Stdio (via Docker) + HTTP/SSE gateway |
| **Setup** | `docker mcp gateway run` CLI |
| **UI** | CLI-driven, profile-based |
| **Auth** | Docker-managed |
| **Client config** | `docker mcp client connect claude-code` auto-configures |
| **Maturity** | Official Docker product, well-documented |

**Best for**: If you already use Docker heavily and want the most "official" path. Excellent Claude Code integration. Requires Docker on the host (but NOT Docker-in-Docker).

- [Docker MCP Gateway Docs](https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/)
- [Docker Blog: Add MCP Servers to Claude Code](https://www.docker.com/blog/add-mcp-servers-to-claude-code-with-mcp-toolkit/)
- [Docker MCP Get Started](https://docs.docker.com/ai/mcp-catalog-and-toolkit/get-started/)
- [Docker MCP CLI Reference](https://docs.docker.com/ai/mcp-catalog-and-toolkit/cli/)

### 3. MCP Hub (ravitemer/mcp-hub)
**What it is**: Central coordinator between MCP clients and multiple servers. Supports local STDIO servers and remote SSE/streamable-http servers. JSON config, auto-detects server type.

| Factor | Details |
|--------|---------|
| **Transport** | STDIO (local) + SSE + Streamable HTTP (remote) |
| **Setup** | Node.js (`npx`), config file |
| **UI** | None (config-driven) |
| **Auth** | Header-based for remote servers |
| **Client config** | Single MCP endpoint for clients |
| **Maturity** | Community project, active |

**Best for**: Lightweight central hub without Docker overhead. Good if you want to mix local stdio servers with remote SSE ones.

- [GitHub: ravitemer/mcp-hub](https://github.com/ravitemer/mcp-hub)

### 4. Gatekit
**What it is**: "Hackable" MCP gateway with plugin architecture. Tool management/filtering, PII/secrets checks, audit logging, token usage tracking.

| Factor | Details |
|--------|---------|
| **Transport** | SSE + Streamable HTTP |
| **Setup** | Node.js / Docker |
| **UI** | Minimal |
| **Auth** | Plugin-based |
| **Maturity** | Newer, plugin-focused |

**Best for**: If you want fine-grained control over tool filtering, PII detection, and audit logging.

- [Gatekit Official Site](https://gatekit.ai/)

---

## Tier 2: Transport Bridges (Run servers anywhere, connect from anywhere)

These are lighter-weight — they don't aggregate servers, but they let you **run an MCP server on one machine and access it from another** by bridging transports.

### 5. Supergateway (supercorp-ai)
**What it is**: One-command bridge that converts stdio ↔ SSE (and Streamable HTTP). Run a stdio MCP server, expose it as an SSE endpoint. Or consume an SSE endpoint as stdio.

| Factor | Details |
|--------|---------|
| **Transport** | stdio → SSE, SSE → stdio, Streamable HTTP |
| **Setup** | `npx supergateway --stdio "command"` or Docker |
| **Auth** | `--header` flag for bearer tokens |
| **Maturity** | Active, v2.6+ with auth support |

**Best for**: Wrapping individual stdio MCP servers (like Serena, Context7) to expose them as remote SSE endpoints. Combine multiple instances behind a reverse proxy for a DIY gateway.

- [GitHub: supercorp-ai/supergateway](https://github.com/supercorp-ai/supergateway)

### 6. mcp-proxy (sparfenyuk, Python)
**What it is**: Bidirectional MCP proxy for stdio ↔ SSE transport conversion.

- [Model Context Protocol listing](https://model-context-protocol.com/servers/mcp-server-sse-stdio-proxy-connector)

### 7. mcp-proxy (stephenlacy, Rust)
**What it is**: High-performance bidirectional proxy with SSE + Streamable HTTP + OAuth support.

- [GitHub: stephenlacy/mcp-proxy](https://github.com/stephenlacy/mcp-proxy)

### 8. mcp_bridge (geosp, Python)
**What it is**: "Universal transport bridge" for stdio clients ↔ remote HTTP/SSE servers.

- [GitHub: geosp/mcp_bridge](https://github.com/geosp/mcp_bridge)

---

## Tier 3: Enterprise/Infrastructure Gateways

### 9. Envoy AI Gateway
**What it is**: MCP routing built into the Envoy proxy ecosystem. Kubernetes-native with CRDs (`MCPRoute`), OAuth, rate limiting, load balancing, observability.

| Factor | Details |
|--------|---------|
| **Transport** | Streamable HTTP (June 2025 MCP spec) |
| **Setup** | Kubernetes + Helm charts |
| **Auth** | OAuth 2.1, fine-grained authorization |
| **Maturity** | Production-grade (Envoy ecosystem), v0.5+ |

**Best for**: Enterprise Kubernetes environments needing production-grade MCP routing with full observability stack.

- [Envoy AI Gateway MCP Docs](https://aigateway.envoyproxy.io/docs/capabilities/mcp/)
- [Envoy AI Gateway Installation](https://aigateway.envoyproxy.io/docs/getting-started/installation)

### 10. Microsoft mcp-gateway
**What it is**: Reverse proxy + management layer for MCP servers with session-aware routing. Kubernetes-focused.

- [GitHub: microsoft/mcp-gateway](https://github.com/microsoft/mcp-gateway)
- [Microsoft MCP Gateway Docs](https://microsoft.github.io/mcp-gateway/sample-servers/mcp-proxy/)

### 11. IBM MCP Context Forge
**What it is**: MCP gateway, proxy, and registry. Federates MCP + REST, with security, rate limiting, observability, virtual servers, admin UI.

- [IBM MCP Context Forge](https://ibm.github.io/mcp-context-forge/)

### 12. AWS MCP Proxy
**What it is**: Client-side proxy for connecting to AWS-hosted MCP servers with SigV4 auth, read-only mode, logging.

- [AWS MCP Proxy Announcement](https://aws.amazon.com/about-aws/whats-new/2025/10/model-context-protocol-proxy-available/)

---

## Comparison Matrix

| Solution | Type | Docker Required | Web UI | Multi-client | Auth | Complexity |
|----------|------|----------------|--------|-------------|------|------------|
| **MetaMCP** | Aggregator | Yes (Compose) | Yes | Yes (SSE) | API keys | Low-Medium |
| **Docker MCP Gateway** | Aggregator | Yes | No (CLI) | Yes | Docker-managed | Low |
| **MCP Hub** | Coordinator | No (Node.js) | No | Yes (SSE) | Headers | Low |
| **Gatekit** | Gateway | Optional | Minimal | Yes | Plugins | Medium |
| **Supergateway** | Bridge | Optional | No | Yes (SSE) | Headers | Very Low |
| **Envoy AI Gateway** | Enterprise | K8s | Envoy UI | Yes | OAuth 2.1 | High |
| **Microsoft mcp-gateway** | Enterprise | K8s | No | Yes | Configurable | High |
| **IBM Context Forge** | Enterprise | Yes | Yes | Yes | Full suite | High |

---

## Recommendations for Your Use Case

**Context**: Coder dev containers, need central server accessible from multiple environments.

### Top Pick: MetaMCP
- Docker Compose on a dedicated host (VM, local machine, cloud instance)
- Web UI for managing which MCP servers are active
- Exposes SSE endpoint that all your Coder workspaces connect to
- Closest to AIRIS in concept and capability

### Runner-up: Docker MCP Gateway
- If you have a machine with Docker, this is the most "official" option
- First-class Claude Code support
- Profile system for different tool sets

### Lightweight Alternative: Supergateway + Reverse Proxy
- Run individual MCP servers with Supergateway wrapping each one
- Put Nginx/Caddy in front for routing and auth
- Maximum flexibility, minimum overhead per server
- DIY but very transparent

### If You Have Kubernetes: Envoy AI Gateway
- Production-grade, but requires K8s infrastructure
- Best for teams/orgs with existing K8s

---

## Sources

- [MetaMCP](https://metamcp.com/) | [GitHub](https://github.com/metatool-ai/metamcp) | [Docs](https://docs.metamcp.com/en/quickstart)
- [Docker MCP Gateway](https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/) | [Blog](https://www.docker.com/blog/add-mcp-servers-to-claude-code-with-mcp-toolkit/)
- [MCP Hub](https://github.com/ravitemer/mcp-hub)
- [Gatekit](https://gatekit.ai/)
- [Supergateway](https://github.com/supercorp-ai/supergateway)
- [Envoy AI Gateway](https://aigateway.envoyproxy.io/docs/capabilities/mcp/)
- [Microsoft mcp-gateway](https://github.com/microsoft/mcp-gateway)
- [IBM MCP Context Forge](https://ibm.github.io/mcp-context-forge/)
- [AWS MCP Proxy](https://aws.amazon.com/about-aws/whats-new/2025/10/model-context-protocol-proxy-available/)
- [mcp-proxy (Rust)](https://github.com/stephenlacy/mcp-proxy)
- [mcp_bridge](https://github.com/geosp/mcp_bridge)
- [MCPRouter](https://www.mcprouters.com/)
