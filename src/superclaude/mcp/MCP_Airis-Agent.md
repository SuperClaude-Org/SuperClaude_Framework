# Airis Agent MCP Server

Airis Agent provides confidence checking, deep research, and repository indexing capabilities to prevent wrong-direction work.

## Tools

- **airis_confidence_check** - Validate decisions before implementation
- **airis_deep_research** - Comprehensive research with web search
- **airis_repo_index** - Index repository structure for better context

## Installation

```bash
superclaude mcp --servers airis-agent
```

## Requirements

- Docker installed and running
- (Optional) Workspace directory mounted at `/workspace`

## Configuration

The server runs as a Docker container from `ghcr.io/agiletec-inc/airis-agent:latest`.

No additional configuration required for basic usage.

## Links

- [GitHub Repository](https://github.com/agiletec-inc/airis-agent)
- [Docker Image](https://ghcr.io/agiletec-inc/airis-agent)
