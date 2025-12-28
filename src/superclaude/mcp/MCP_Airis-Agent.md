# Airis Agent MCP Server

Airis Agent provides confidence checking, deep research, and repository indexing capabilities to prevent wrong-direction work.

## Tools

- **airis_confidence_check** - Validate decisions before implementation
- **airis_deep_research** - Comprehensive research with web search
- **airis_repo_index** - Index repository structure for better context
- **airis_docs_optimize** - Optimize documentation structure
- **airis_sync_manifest** - Sync manifest.toml with filesystem

## Installation

**Recommended: Use AIRIS MCP Gateway** (includes airis-agent + 60 other tools)

```bash
git clone https://github.com/agiletec-inc/airis-mcp-gateway.git
cd airis-mcp-gateway
docker compose up -d
claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse
```

## Links

- [AIRIS MCP Gateway](https://github.com/agiletec-inc/airis-mcp-gateway) - Unified gateway (recommended)
- [airis-agent Repository](https://github.com/agiletec-inc/airis-agent) - Standalone package
