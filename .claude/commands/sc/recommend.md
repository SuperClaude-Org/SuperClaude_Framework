---
name: sc:recommend
description: "Ultra-intelligent command recommendation engine - recommends the most suitable SuperClaude commands for any user input"
category: utility
---

# /sc:recommend - Intelligent Command Recommender

## Triggers

- User asks "which command should I use?"
- User describes a goal without specifying a command
- User requests command recommendations
- Explicit `/sc:recommend [query]` invocation
- Multi-language input (English, Turkish, etc.)

## Usage

```bash
/sc:recommend [user request] [flags]
```

### Flags

| Flag | Description |
|------|-------------|
| `--estimate` | Include time and budget estimation |
| `--alternatives` | Provide multiple solution recommendations |
| `--stream` | Continuous project tracking mode |
| `--community` | Include community usage data |
| `--language [auto\|en\|tr]` | Language setting (default: auto) |
| `--expertise [beginner\|intermediate\|expert]` | Expertise level setting |

## Behavioral Summary

Analyzes user requests through multi-language keyword extraction, project context detection, and expertise level assessment to recommend optimal SuperClaude command sequences with appropriate personas, MCP servers, and flags. Supports streaming mode for continuous project tracking, alternative recommendations with comparison matrices, and intelligent time/budget estimation with complexity-adjusted multipliers.

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:recommend-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Examples

### Basic Recommendation
```bash
/sc:recommend "I want to build a React component"

# Output:
# → Project Analysis: React component development
# → Persona: --persona-frontend
# → Primary: /sc:build --feature --magic --react
# → Secondary: /sc:test --coverage --e2e
```

### With Estimation
```bash
/sc:recommend "need to secure my API" --estimate

# Includes time/budget analysis + security-focused commands
```

### With Alternatives
```bash
/sc:recommend "new blog site" --alternatives

# Provides multiple technology stack options with comparison
```

### Streaming Mode
```bash
/sc:recommend --stream "building e-commerce site"

# Continuous recommendations across project phases
```

## Boundaries

**Will:**
- Analyze user requests in multiple languages and recommend optimal command sequences
- Detect project context from file system analysis
- Provide time and budget estimations when requested
- Present alternative approaches with comparison matrices
- Adapt recommendations based on expertise level

**Will Not:**
- Execute recommended commands automatically (user must invoke)
- Make assumptions about project type without evidence
- Provide fake metrics or community data
- Override user-specified preferences
