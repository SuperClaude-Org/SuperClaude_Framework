# MindBase MCP Server

MindBase provides semantic memory storage and retrieval using PostgreSQL with pgvector for embeddings.

## Tools

- **conversation_save** - Save conversations with automatic embedding
- **conversation_get** - Retrieve conversations with filtering
- **conversation_search** - Semantic search across conversations
- **conversation_delete** - Remove specific conversations
- **memory_write** - Store memories (markdown + DB)
- **memory_read** - Read memories
- **memory_list** - List all memories
- **memory_search** - Semantic search across memories
- **session_create** - Create session for organizing conversations
- **session_start** - Start/resume a session

## Installation

**Recommended: Use AIRIS MCP Gateway** (includes mindbase + 60 other tools)

```bash
git clone https://github.com/agiletec-inc/airis-mcp-gateway.git
cd airis-mcp-gateway
docker compose up -d
claude mcp add --scope user --transport sse airis-mcp-gateway http://localhost:9400/sse
```

MindBase is managed by Docker MCP Gateway via `airis-catalog.yaml`. PostgreSQL with pgvector is included.

## Links

- [AIRIS MCP Gateway](https://github.com/agiletec-inc/airis-mcp-gateway) - Unified gateway (recommended)
- [mindbase Repository](https://github.com/agiletec-inc/mindbase) - Standalone package
