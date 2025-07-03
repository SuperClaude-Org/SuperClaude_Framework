# Configuration Management System

## Overview

The SuperClaude MCP configuration management system provides a flexible, hierarchical configuration system that supports both local and remote data sources with optional persistence to the user's home directory.

## Features

- **Multiple Source Types**: Support for local file system and remote GitHub repository sources
- **Configuration Hierarchy**: CLI arguments → Environment variables → User config → Defaults
- **Persistence**: Optional saving of configuration to `~/.superclaude/config.json`
- **CLI Management**: Full CLI commands for configuration management (init, show, set, reset)
- **Backwards Compatibility**: Maintains compatibility with existing GitHub repository setup

## Configuration Schema

The configuration uses Zod schemas for runtime validation:

```typescript
interface AppConfig {
  source: {
    type: "local" | "remote";
    local: { path: string };
    remote: { url: string; branch: string; cacheTTL: number };
  };
  database: {
    path: string;
    autoInit: boolean;
  };
  sync: {
    enabled: boolean;
    intervalMinutes: number;
    onStartup: boolean;
  };
  server: {
    transport: "stdio" | "http";
    port: number;
    logLevel: string;
  };
  persistence: {
    enabled: boolean;
    autoSave: boolean;
  };
}
```

## CLI Usage

### Configuration Commands

```bash
# Initialize configuration file
superclaude-mcp config init

# Show current configuration
superclaude-mcp config show

# Set configuration values
superclaude-mcp config set sync.enabled false
superclaude-mcp config set source.remote.url https://github.com/myorg/myrepo

# Reset configuration to defaults
superclaude-mcp config reset
superclaude-mcp config reset --delete  # Also removes config file
```

### Global Options

```bash
# Use local source
superclaude-mcp --source-type local --source-path /path/to/data server

# Use remote source with custom settings
superclaude-mcp --source-type remote --source-url https://github.com/org/repo --source-branch develop server

# Persist configuration
superclaude-mcp --source-type local --source-path /data --persist-config server
```

## Environment Variables

The following environment variables are supported:

- `SC_SOURCE_TYPE`: Source type (local or remote)
- `SC_SOURCE_PATH`: Path for local source
- `SC_SOURCE_URL`: URL for remote source
- `SC_SOURCE_BRANCH`: Branch for remote source
- `SC_SOURCE_CACHE_TTL`: Cache TTL in minutes for remote source
- `SC_DATABASE_PATH`: Database file path
- `SC_AUTO_SYNC_ENABLED`: Enable/disable auto sync
- `SC_TRANSPORT`: Server transport (stdio or http)
- `PORT`: Server port for HTTP transport
- `LOG_LEVEL`: Logging level
- `SC_PERSIST_CONFIG`: Persist configuration to home directory

## Source Loaders

### LocalSourceLoader

Loads SuperClaude data from the local file system:

```
{basePath}/
├── commands/
│   ├── command1.yaml
│   └── command2.yaml
├── personas/
│   ├── persona1.yaml
│   └── persona2.yaml
└── rules/
    └── rules.yaml
```

### GitHubSourceLoader

Loads data from a GitHub repository with configurable:
- Repository URL
- Branch
- Cache TTL

## Implementation Details

### ConfigService

- Manages configuration hierarchy
- Handles loading from multiple sources
- Provides configuration persistence
- Validates configuration with Zod schemas

### SourceLoaderFactory

- Creates appropriate source loader based on configuration
- Validates source configuration
- Provides factory methods for each source type

### Integration

The configuration system is fully integrated with:
- HTTP server initialization
- MCP server setup
- Sync service configuration
- CLI commands

## Testing

Comprehensive test coverage includes:
- Configuration model validation
- ConfigService hierarchy and persistence
- LocalSourceLoader file operations
- SourceLoaderFactory creation logic
- Integration tests for CLI commands (skipped due to fs mock conflicts)

Note: Some tests are skipped in the test suite due to conflicts between fs mocking and vitest setup that uses real fs operations.