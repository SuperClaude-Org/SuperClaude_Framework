#!/usr/bin/env python3
"""
Setup Board Commands for Claude Code Integration

This script sets up the /sc:board commands to be available in Claude Code
by creating the necessary command integration files.
"""

import json
import os
from pathlib import Path


def setup_claude_integration():
    """Set up Claude Code integration for board commands"""
    
    print("🚀 Setting up SuperClaude Board Commands for Claude Code")
    print("=" * 60)
    
    # Get Claude config directory
    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(exist_ok=True)
    
    # Create or update CLAUDE.md
    claude_md = claude_dir / "CLAUDE.md"
    
    board_integration = """
# SuperClaude Board System Integration

## Enable Board Commands
@SuperClaude/Commands/board.md

## Board System Configuration
The board system provides visual task orchestration with:
- Multi-agent coordination
- Resource management
- Error recovery
- Real-time visualization

## Auto-Activation
The board system activates when:
- Multiple complex tasks are requested
- Resource limits need management
- Visual progress tracking is beneficial

## Fallback Safety
If board system fails, automatically falls back to standard SuperClaude operation.
"""
    
    if claude_md.exists():
        content = claude_md.read_text()
        if "SuperClaude Board System" not in content:
            print("📝 Adding board integration to existing CLAUDE.md")
            with open(claude_md, 'a') as f:
                f.write(board_integration)
        else:
            print("✅ Board integration already present in CLAUDE.md")
    else:
        print("📝 Creating new CLAUDE.md with board integration")
        claude_md.write_text(board_integration)
    
    # Create command hook script
    hooks_dir = claude_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    board_hook = hooks_dir / "board_command.py"
    hook_content = '''"""
SuperClaude Board Command Hook

This hook intercepts /sc:board commands and routes them to the board system.
"""

import sys
import os
from pathlib import Path

# Add SuperClaude to path
superclaude_path = Path(__file__).parent.parent.parent / "workspace/tools/SuperClaude"
if superclaude_path.exists():
    sys.path.insert(0, str(superclaude_path))

def handle_board_command(command_args):
    """Handle /sc:board commands"""
    try:
        from SuperClaude.Orchestration.board.board_manager import get_board_manager
        from SuperClaude.Orchestration.ui.board_renderer import BoardRenderer
        
        board_manager = get_board_manager()
        renderer = BoardRenderer(board_manager, board_manager.resource_tracker)
        
        if not command_args or command_args[0] == "show":
            # Show board
            mini = "--mini" in command_args
            no_resources = "--no-resources" in command_args
            
            if mini:
                return renderer.render_mini_board()
            else:
                return renderer.render_board(show_resources=not no_resources)
                
        elif command_args[0] == "status":
            if len(command_args) > 1:
                card_id = command_args[1]
                return renderer.render_card_detail(card_id) or f"Card {card_id} not found"
            else:
                status = board_manager.get_board_status()
                return f"Board Session: {status['board']['session_id']}\\nActive Cards: {len(status['board']['active_agents'])}"
                
        elif command_args[0] == "move" and len(command_args) >= 3:
            card_id = command_args[1]
            column = command_args[2]
            success, msg = board_manager.move_card(card_id, column)
            return f"{'✅' if success else '❌'} {msg}"
            
        elif command_args[0] == "pause" and len(command_args) >= 2:
            card_id = command_args[1]
            reason = " ".join(command_args[2:]) if len(command_args) > 2 else "User requested"
            success, msg = board_manager.pause_card(card_id, reason)
            return f"{'✅' if success else '❌'} {msg}"
            
        else:
            return f"Unknown board command: {' '.join(command_args)}\\nUse /sc:board show for board state"
            
    except Exception as e:
        return f"Board system error: {e}\\nFalling back to standard operation"

# Register with Claude Code hooks system
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = handle_board_command(sys.argv[1:])
        print(result)
'''
    
    print("🔧 Creating board command hook")
    board_hook.write_text(hook_content)
    
    # Create settings configuration
    settings_file = claude_dir / "settings.json"
    
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    # Add board system settings
    if "superclaude" not in settings:
        settings["superclaude"] = {}
    
    settings["superclaude"].update({
        "board_system_enabled": True,
        "max_active_cards": 3,
        "token_budget": 20000,
        "auto_fallback": True,
        "command_prefix": "sc:"
    })
    
    print("⚙️  Updating Claude settings")
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    # Create test command file
    test_file = Path.cwd() / "test_board_commands.md"
    test_content = """# Test Board Commands

After running the setup, you can test these commands in Claude Code:

## Basic Commands
```
/sc:board show
/sc:board show --mini
/sc:board status
```

## Create a Test Scenario
```
/implement user authentication --persona backend
/sc:board show
/sc:board status <card_id>
/sc:board move <card_id> in_progress
/sc:board show
```

## Error Recovery Test
```
/sc:board errors <card_id>
/sc:board errors --recommendations
```

## Agent Management
```
/sc:board agents
/sc:board pause <card_id>
/sc:board resume <card_id>
```

## Cleanup
```
/sc:board clear --completed
/sc:board fallback "regular request"
```

The board system will automatically activate for complex multi-step tasks.
"""
    
    print("📝 Creating test commands reference")
    test_file.write_text(test_content)
    
    print("\n✅ Setup Complete!")
    print(f"   Claude config: {claude_dir}")
    print(f"   Board hook: {board_hook}")
    print(f"   Test commands: {test_file}")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Restart Claude Code to load new configuration")
    print(f"2. Run: python test_phase2_demo.py (to see board in action)")
    print(f"3. Try board commands in Claude Code: /sc:board show")
    print(f"4. Test with complex tasks that auto-activate board mode")
    
    return True


def create_simple_command_test():
    """Create a simple test to verify command integration"""
    test_script = Path.cwd() / "simple_board_test.py"
    
    content = '''#!/usr/bin/env python3
"""
Simple Board System Test - Verify basic functionality
"""

import sys
from pathlib import Path

# Add SuperClaude to path
sys.path.insert(0, str(Path(__file__).parent))

def test_board_basic():
    """Test basic board functionality"""
    try:
        from SuperClaude.Orchestration.board.board_manager import BoardManager
        from SuperClaude.Orchestration.ui.board_renderer import BoardRenderer
        
        print("🧪 Testing basic board functionality...")
        
        # Create board
        board = BoardManager()
        renderer = BoardRenderer(board, board.resource_tracker)
        
        # Create a test card
        success, msg, card = board.create_card_from_request(
            "Test task", persona_name="general", priority="medium"
        )
        
        if success:
            print(f"✅ Card created: {card.id}")
            
            # Show mini board
            mini_view = renderer.render_mini_board()
            print(f"📊 Board status: {mini_view}")
            
            return True
        else:
            print(f"❌ Card creation failed: {msg}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_board_basic()
    print(f"\\n{'✅ Test passed!' if success else '❌ Test failed!'}")
    sys.exit(0 if success else 1)
'''
    
    test_script.write_text(content)
    print(f"📝 Created simple test: {test_script}")
    return test_script


if __name__ == "__main__":
    success = setup_claude_integration()
    if success:
        test_file = create_simple_command_test()
        print(f"\n🔧 Run this to verify setup:")
        print(f"   python {test_file.name}")
        print(f"\n🎮 Run this for full demo:")
        print(f"   python test_phase2_demo.py")