# D-0013: Static-Tool Orchestration with Result Caching

## Module
`src/superclaude/cli/audit/tool_orchestrator.py`

## Pipeline
1. Receive batch of files (path -> content mapping)
2. For each file, compute SHA-256 content hash
3. Check cache for existing result by hash
4. On miss: invoke analyzer, cache result
5. On hit: return cached result (skip re-invocation)

## Caching Strategy
- Key: SHA-256 of file content
- Invalidation: automatic (different content = different hash)
- No TTL needed (content-addressed)

## Result Schema
```json
{
  "file_path": "string",
  "content_hash": "sha256_hex",
  "imports": ["import os", "from pathlib import Path"],
  "exports": [],
  "references": [],
  "metadata": {"line_count": 42, "size_bytes": 1024}
}
```

## Pluggable Analyzers
Custom analysis tools can be passed via `analyzer` parameter to `ToolOrchestrator`.
