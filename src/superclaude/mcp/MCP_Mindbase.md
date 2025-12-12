# MindBase MCP Server

MindBase provides semantic memory storage and retrieval using PostgreSQL with pgvector for embeddings.

## Tools

- **store_memory** - Store memories with automatic embedding
- **search_memories** - Semantic search across stored memories
- **list_memories** - List all stored memories
- **delete_memory** - Remove specific memories

## Installation

```bash
superclaude mcp --servers mindbase
```

## Requirements

- Docker installed and running
- PostgreSQL with pgvector extension
- Ollama running locally (for embeddings)

## Configuration

Set the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MINDBASE_DATABASE_URL` | PostgreSQL connection string | `postgresql://mindbase:mindbase@host.docker.internal:5432/mindbase` |
| `OLLAMA_URL` | Ollama server URL | `http://host.docker.internal:11434` |
| `EMBEDDING_MODEL` | Embedding model name | `nomic-embed-text` |

## Quick Start with Docker Compose

```yaml
services:
  mindbase-postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: mindbase
      POSTGRES_PASSWORD: mindbase
      POSTGRES_DB: mindbase
    ports:
      - "5432:5432"
```

## Links

- [GitHub Repository](https://github.com/kazuph/mindbase)
- [Docker Image](https://ghcr.io/agiletec-inc/mindbase-mcp)
