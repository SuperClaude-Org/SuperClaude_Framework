# Distribution Guide

This document explains how to distribute Airiscode plugin according to Claude Code best practices.

## 📚 References

- [Claude Code Plugins](https://docs.claude.com/ja/docs/claude-code/plugins)
- [Sub-Agents](https://docs.claude.com/ja/docs/claude-code/sub-agents)
- [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## 🎯 Distribution Methods

### 1. Marketplace Distribution (Recommended for End Users)

**Status**: Coming Soon

**Benefits**:
- ✅ Automatic updates
- ✅ Easy discovery via `/plugin` command
- ✅ Centralized management
- ✅ Version control
- ✅ Team-wide consistency

**Implementation**:

```json
// .claude/settings.json (in user projects)
{
  "marketplaces": {
    "airiscode": {
      "type": "remote",
      "url": "https://marketplace.agiletec.com/airiscode"
    }
  },
  "plugins": {
    "autoInstall": ["airiscode@airiscode"]
  }
}
```

**Installation (Future)**:

```bash
# Interactive menu
/plugin

# Direct command
/plugin install @airiscode/airiscode
```

### 2. Project-Local (Current - For Development)

**Status**: ✅ Implemented

**Use Case**: Plugin development, testing, contributing

**How it works**:

```
airiscode/
├── .claude/
│   └── settings.json          # Defines local marketplace
├── .claude-plugin/
│   ├── plugin.json            # Plugin manifest (auto-detected)
│   └── marketplace.json       # Local marketplace catalog
├── pm/
│   └── index.ts               # Plugin source (hot reload enabled)
├── commands/
│   └── pm.md                  # Command definitions
└── hooks/
    └── hooks.json             # SessionStart auto-activation
```

**Installation**:

```bash
git clone https://github.com/agiletec-inc/airiscode.git
cd airiscode
claude  # Auto-detects .claude-plugin/
```

**Configuration files**:

`.claude/settings.json`:
```json
{
  "marketplaces": {
    "airiscode": {
      "type": "local",
      "path": ".claude-plugin"
    }
  },
  "plugins": {
    "autoInstall": ["airiscode@airiscode"]
  }
}
```

`.claude-plugin/marketplace.json`:
```json
{
  "name": "airiscode",
  "description": "PM Agent for Claude Code - Confidence-driven development framework",
  "owner": {
    "name": "Agiletec Inc."
  },
  "plugins": [
    {
      "name": "airiscode",
      "source": ".",
      "version": "0.1.0",
      "description": "PM Agent for Claude Code - Confidence-driven development framework"
    }
  ]
}
```

`.claude-plugin/plugin.json`:
```json
{
  "name": "airiscode",
  "version": "0.1.0",
  "description": "PM Agent for Claude Code - Confidence-driven development framework",
  "author": {
    "name": "Agiletec Inc."
  },
  "homepage": "https://github.com/agiletec-inc/airiscode",
  "repository": "https://github.com/agiletec-inc/airiscode",
  "license": "MIT",
  "keywords": ["pm-agent", "confidence-check", "research", "indexing", "claude-code"],
  "commands": "./commands/",
  "hooks": "./hooks/hooks.json",
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 3. Global Manual Installation (Advanced)

**Status**: ✅ Implemented

**Use Case**: Advanced users who want global access without marketplace

**Installation**:

```bash
cd airiscode
make install-plugin-dev  # Copies to ~/.claude/plugins/pm-agent/
# Restart Claude Code
```

**What happens**:

```bash
# Makefile target
~/.claude/plugins/pm-agent/
├── plugin.json
├── marketplace.json
├── commands/
├── hooks/
├── pm/
├── research/
└── index/
```

**Limitations**:
- ❌ No automatic updates (manual `make reinstall-plugin-dev`)
- ❌ No hot reload (requires Claude Code restart)
- ❌ Potential conflicts with other plugins

## 🔧 Plugin Components

### Required Files

1. **plugin.json** (Manifest)
   - `name`: Plugin identifier
   - `version`: Semantic versioning (e.g., "0.1.0")
   - `description`: Short description
   - `author`: Creator information
   - `commands`: Path to command definitions
   - `hooks`: Path to hook configuration

2. **commands/*.md** (Command Definitions)
   - YAML frontmatter with `name` and `description`
   - Markdown body with instructions

3. **hooks/hooks.json** (Auto-Activation)
   - `SessionStart`: Commands to run on session start

### Optional Components

4. **marketplace.json** (Marketplace Catalog)
   - For project-local or team marketplaces

5. **.claude/settings.json** (Auto-Install Configuration)
   - Marketplace definitions
   - Auto-install rules

6. **skills/** (Future - Agent Skills)
   - `SKILL.md`: Skill definition with YAML frontmatter
   - Additional reference files

7. **.claude/agents/** (Future - Sub-Agents)
   - Markdown files with YAML frontmatter
   - Task-specific AI personalities

## 🚀 Publishing Checklist

### Before Publishing

- [ ] Update version in `plugin.json`
- [ ] Update version in `marketplace.json`
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Test Claude Code plugin:
  - [ ] `cd airiscode && claude` (project-local)
  - [ ] Test commands: `/pm`, `/research`, `/index-repo`
  - [ ] Check hot reload (edit `pm/index.ts`)
- [ ] Test Python package (optional):
  - [ ] `uv venv && source .venv/bin/activate`
  - [ ] `make dev` (Python package install)
  - [ ] `uv run pytest` (run tests)
  - [ ] `make verify` (verify installation)

### Git Tag and Release

```bash
# Create version tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# Create GitHub release
gh release create v0.1.0 \
  --title "Airiscode v0.1.0" \
  --notes "Initial release"
```

### Future: Marketplace Submission

**When marketplace becomes available**:

1. Package plugin:
   ```bash
   tar -czf airiscode-v0.1.0.tar.gz .claude-plugin/ pm/ research/ index/ commands/ hooks/
   ```

2. Submit to marketplace:
   - Fill out submission form
   - Provide `plugin.json` metadata
   - Upload packaged plugin
   - Wait for review

3. Update documentation with marketplace URL

## 📊 Version Management

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., command name changes)
- **MINOR**: New features (e.g., new `/analyze` command)
- **PATCH**: Bug fixes (e.g., confidence calculation fix)

**Example**:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.1` → `0.2.0`: New feature
- `0.2.0` → `1.0.0`: Stable release / breaking change

## 🔍 Troubleshooting

### Plugin not detected

```bash
# Verify .claude-plugin/plugin.json exists
ls -la .claude-plugin/plugin.json

# Check Claude Code output for errors
claude
```

### Commands not working

```bash
# Verify commands/ directory
ls -la commands/

# Check command definitions
cat commands/pm.md
```

### Hot reload not working

- Hot reload only works in **project-local** mode
- Edit `pm/index.ts` → Save → Command updates automatically
- Global installation requires restart

## 📝 Best Practices

1. **Use Semantic Versioning**: Helps users understand changes
2. **Document Breaking Changes**: In CHANGELOG.md
3. **Test Before Release**: Run full test suite
4. **Keep plugin.json Minimal**: Only include necessary fields
5. **Optimize for Marketplace**: Prepare for future marketplace distribution
6. **Provide Clear README**: Installation and usage instructions
7. **Use Conventional Commits**: For automated changelog generation

## 🔗 Related Documentation

- **CLAUDE.md**: Developer guide for Claude Code
- **README.md**: User-facing documentation
- **CONTRIBUTING.md**: Contribution guidelines (to be created)
- **CHANGELOG.md**: Version history (to be created)
