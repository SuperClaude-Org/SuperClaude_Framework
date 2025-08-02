# /sc:board - Board System Management

Manage the SuperClaude board system for visual task orchestration and sub-agent coordination.

## Purpose
Provides visual transparency and control over multi-agent task execution through a Trello-like board interface.

## Usage
```
/sc:board [subcommand] [arguments] [--flags]
```

## Subcommands

### show
Display the current board state with all cards and resource usage.
```
/sc:board show [--mini] [--no-resources]
```
- `--mini` - Compact summary view
- `--no-resources` - Hide resource panel

### status
Get detailed status of a specific card or the entire board.
```
/sc:board status [card_id]
```
- Without card_id: Shows board summary
- With card_id: Shows detailed card information

### create
Create a new task card on the board.
```
/sc:board create "<title>" --persona <type> [--priority high|medium|low] [--context "<context>"]
```

### move
Move a card to a different column.
```
/sc:board move <card_id> <column>
```
Columns: backlog, todo, in_progress, integrate, review, done

### pause
Pause execution of a card (and its agent).
```
/sc:board pause <card_id> [--reason "<reason>"]
```

### resume
Resume a paused card.
```
/sc:board resume <card_id>
```

### assign
Assign or reassign a card to an agent.
```
/sc:board assign <card_id> --persona <type> [--force]
```

### fail
Mark a card as failed.
```
/sc:board fail <card_id> --reason "<reason>"
```

### retry
Retry a failed card.
```
/sc:board retry <card_id> [--strategy retry|reassign|fallback]
```

### agents
Show status of all active agents.
```
/sc:board agents [--detailed]
```

### errors
Analyze error patterns and get recovery recommendations.
```
/sc:board errors [card_id] [--recommendations]
```

### clear
Clear completed or failed cards from the board.
```
/sc:board clear [--completed] [--failed] [--all]
```

### fallback
Execute with main system instead of board mode.
```
/sc:board fallback "<request>"
```

## Flags

### Global Flags
- `--json` - Output in JSON format
- `--watch` - Continuous update mode
- `--immediate` - Bypass board for urgent requests

### Resource Management
- `--max-agents <n>` - Override max concurrent agents (default: 3)
- `--token-limit <n>` - Override token limit (default: 20000)

## Examples

### Basic Usage
```bash
# Show the board
/sc:board show

# Create a new task
/sc:board create "Implement user authentication" --persona backend --priority high

# Check card status
/sc:board status card_001

# Move card to review
/sc:board move card_001 review

# Pause a card
/sc:board pause card_002 --reason "Waiting for API access"
```

### Error Recovery
```bash
# Check errors on a card
/sc:board errors card_003 --recommendations

# Retry with different strategy
/sc:board retry card_003 --strategy fallback

# Manual failure
/sc:board fail card_004 --reason "Requirements changed"
```

### Agent Management
```bash
# View all agents
/sc:board agents --detailed

# Reassign card to different persona
/sc:board assign card_005 --persona architect --force
```

### Resource Control
```bash
# Clear completed cards
/sc:board clear --completed

# Emergency bypass
/sc:board fallback "Fix critical production issue" --immediate
```

## Board Columns

1. **BACKLOG** 📋 - Queued tasks waiting for resources
2. **TODO** 📝 - Ready to start when agent available  
3. **IN_PROGRESS** 🔄 - Actively being worked on
4. **INTEGRATE** 🔗 - Multi-agent coordination needed
5. **REVIEW** 👁️ - Validation and quality checks
6. **DONE** ✅ - Successfully completed
7. **FAILED** ❌ - Failed with errors
8. **BLOCKED** 🚧 - Paused or waiting

## Resource Indicators

- **Token Usage**: Visual bar showing percentage of token budget used
- **Active Agents**: Current/Max agent count
- **MCP Rate**: API calls per minute
- **Queue Length**: Number of cards waiting

## Error Recovery

The board system includes intelligent error recovery:

1. **Automatic Retry**: Transient errors retry with exponential backoff
2. **Agent Reassignment**: Failed agents replaced automatically
3. **Persona Fallback**: Try different persona for difficult tasks
4. **User Intervention**: High-severity errors pause for user input
5. **System Fallback**: Critical failures use main Claude system

## Integration

The board system integrates with:
- **Personas**: Auto-selects best persona for each task
- **MCP Servers**: Coordinates tool access across agents
- **Wave System**: Multi-phase execution for complex tasks
- **Resource Tracker**: Prevents token exhaustion

## Safety Features

- Hard limit of 3 concurrent agents
- 20K token budget enforcement
- Automatic pausing when limits approached
- Graceful degradation to main system
- Full audit trail of all operations

## Tips

1. **Start Small**: Begin with simple single-agent tasks
2. **Monitor Resources**: Watch token usage and adjust
3. **Use Priorities**: High-priority cards get resources first
4. **Review Errors**: Learn from error patterns
5. **Manual Control**: Don't hesitate to pause/move cards

## Troubleshooting

### Common Issues

**"Max agents reached"**
- Wait for current tasks to complete
- Use `/sc:board clear --completed`
- Pause lower priority cards

**"Token limit exceeded"**
- Pause active cards
- Clear completed tasks
- Reduce task scope

**"Agent creation failed"**
- Check error details with `/sc:board errors`
- Try different persona type
- Use fallback mode

**"Card stuck in progress"**
- Check agent health: `/sc:board agents`
- Force move: `/sc:board move <id> review`
- Retry with new agent