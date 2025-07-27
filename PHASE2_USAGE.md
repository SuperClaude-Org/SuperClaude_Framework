# SuperClaude Phase 2 - Board System Usage Guide

## Quick Start

### 1. Run the Demo
```bash
python test_phase2_demo.py
```
This interactive demo shows all Phase 2 features in action.

### 2. Set Up Commands (Optional)
```bash
python setup_board_commands.py
```
This integrates `/sc:board` commands with Claude Code.

### 3. Simple Test
```bash
python simple_board_test.py
```
Quick verification that the board system works.

## New Features in Phase 2

### 🎯 Visual Board System
- **ASCII Board Display**: See all tasks in columns (Backlog → TODO → In Progress → Review → Done)
- **Resource Monitoring**: Real-time token usage and agent limits
- **Card Details**: Comprehensive task information and progress

### 🤖 Agent Coordination
- **Lifecycle Management**: Create, assign, monitor, and cleanup agents
- **Health Monitoring**: Track agent status and performance
- **Smart Assignment**: Automatic persona selection based on task type

### ⚠️ Error Recovery
- **Intelligent Recovery**: Multiple strategies (retry, reassign, fallback)
- **Pattern Detection**: Learn from errors and suggest improvements
- **Graceful Degradation**: Always falls back to working system

### 🎮 Interactive Control
- **Manual Override**: Pause, move, or reassign cards at any time
- **Real-time Updates**: See progress as it happens
- **User-Friendly Commands**: Simple `/sc:board` interface

## Board Commands Reference

### Basic Display
```bash
/sc:board show              # Full board with resource panel
/sc:board show --mini       # Compact summary
/sc:board status <card_id>  # Detailed card information
```

### Card Management
```bash
/sc:board move <card_id> <column>     # Move card between columns
/sc:board pause <card_id>             # Pause execution
/sc:board resume <card_id>            # Resume paused card
/sc:board fail <card_id> --reason "why"  # Mark as failed
/sc:board retry <card_id>             # Retry failed card
```

### Agent Control
```bash
/sc:board agents                      # Show all active agents
/sc:board agents --detailed           # Detailed agent information
/sc:board assign <card_id> --persona <type>  # Reassign to different persona
```

### Error Handling
```bash
/sc:board errors                      # System-wide error analysis
/sc:board errors <card_id>            # Card-specific errors
/sc:board errors --recommendations    # Get recovery suggestions
```

### Maintenance
```bash
/sc:board clear --completed          # Remove finished cards
/sc:board clear --failed             # Remove failed cards
/sc:board fallback "<request>"       # Use main system instead
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

## Automatic Activation

The board system automatically activates when:
- Multiple complex tasks are requested
- Resource management is needed
- Visual progress tracking would be helpful
- Multi-agent coordination is required

## Safety Features

- **Hard Limits**: Max 3 concurrent agents, 20K token budget
- **Resource Warnings**: Alerts before limits are reached
- **Graceful Fallback**: Always falls back to main Claude system
- **Full Audit Trail**: Complete history of all operations
- **User Control**: Override any automatic decision

## Integration with Existing Features

### Personas
- All existing SuperClaude personas work with the board
- Automatic persona selection based on task analysis
- Manual override with `--persona` flag

### MCP Servers
- Context7: Documentation and patterns
- Sequential: Complex analysis
- Magic: UI components
- Playwright: Testing and automation

### Wave System
- Board integrates with multi-phase wave operations
- Progressive enhancement across multiple cards
- Coordinated execution of complex workflows

## Troubleshooting

### "Board system not found"
```bash
# Verify installation
python -c "from SuperClaude.Orchestration.board.board_manager import BoardManager; print('✅ Board system available')"
```

### "Commands not recognized"
1. Run `python setup_board_commands.py`
2. Restart Claude Code
3. Check `.claude/CLAUDE.md` contains board integration

### "Agent creation failed"
- Check available personas: `/sc:board status`
- Verify resource limits: `/sc:board show`
- Try different persona type

### "Resource limits exceeded"
- Pause active cards: `/sc:board pause <card_id>`
- Clear completed cards: `/sc:board clear --completed`
- Use fallback mode: `/sc:board fallback "<request>"`

## Performance Tips

1. **Monitor Resources**: Keep an eye on token usage in board display
2. **Pause When Needed**: Don't hesitate to pause low-priority cards
3. **Clear Regularly**: Remove completed cards to free resources
4. **Use Fallback**: For urgent tasks, use fallback mode to bypass board

## What's Next - Phase 3

Phase 3 will add:
- **Advanced Orchestration**: Complex multi-agent workflows
- **Smart Delegation**: AI-powered task distribution
- **Performance Analytics**: Learning and optimization
- **Enhanced Recovery**: Predictive error prevention

---

🎉 **Phase 2 delivers the transparency and control needed for confident multi-agent development!**