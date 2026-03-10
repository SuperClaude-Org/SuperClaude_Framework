---
name: sc
description: SuperClaude command dispatcher - Use /sc [command] to access all SuperClaude features
---

# SuperClaude Command Dispatcher

🚀 **SuperClaude Framework** - Main command dispatcher

## Usage

All SuperClaude commands use the `/sc:` prefix:

```
/sc:command [args...]
```

## Available Commands

### Research & Analysis
```
/sc:research [query]         - Deep web research with parallel search
```

### Repository Management
```
/sc:index-repo              - Index repository for context optimization
```

### AI Agents
```
/sc:agent [type]            - Launch specialized AI agents
```

### Recommendations
```
/sc:recommend [context]     - Get command recommendations
```

### Help
```
/sc                         - Show this help (all available commands)
```

## Command Namespace

All commands are namespaced under `sc:` to keep them organized:
- ✅ `/sc:research query`
- ✅ `/sc:index-repo`
- ✅ `/sc:agent type`
- ✅ `/sc:recommend`
- ✅ `/sc` (help)

## Examples

### Research
```
/sc:research React 18 new features
/sc:research LLM agent architectures 2024
/sc:research Python async best practices
```

### Index Repository
```
/sc:index-repo
```

### Agent
```
/sc:agent deep-research
/sc:agent self-review
/sc:agent repo-index
```

### Recommendations
```
/sc:recommend
```

## Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:research` | Deep web research | `/sc:research topic` |
| `/sc:index-repo` | Repository indexing | `/sc:index-repo` |
| `/sc:agent` | Specialized AI agents | `/sc:agent type` |
| `/sc:recommend` | Command suggestions | `/sc:recommend` |
| `/sc` | Show help | `/sc` |

## Features

- **Parallel Execution**: Research runs multiple searches in parallel
- **Evidence-Based**: All findings backed by sources
- **Context-Aware**: Uses repository context when available
- **Token Efficient**: Optimized for minimal token usage

## Help

For help on specific commands:
```
/sc:research --help
/sc:agent --help
```

Or use the main help command:
```
/sc
```

Check the documentation:
- PLANNING.md - Architecture and design
- TASK.md - Current tasks and priorities
- KNOWLEDGE.md - Tips and best practices

## Version

SuperClaude v4.1.7
- Python package: 0.4.0
- Pytest plugin included
- PM Agent patterns enabled

---

💡 **Tip**: All commands use the `/sc:` prefix - e.g., `/sc:research`, `/sc:agent`

🔧 **Installation**: Run `superclaude install` to install/update commands

📚 **Documentation**: https://github.com/SuperClaude-Org/SuperClaude_Framework

⚠️ **Important**: Restart Claude Code after installing commands to use them!
