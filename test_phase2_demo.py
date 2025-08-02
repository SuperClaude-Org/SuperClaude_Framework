#!/usr/bin/env python3
"""
Phase 2 Demo Test - Interactive Board System Demo

Run this to see the new Phase 2 board visualization and agent coordination in action.
This creates a realistic scenario with multiple cards and demonstrates all new features.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from SuperClaude.Orchestration.board.board_manager import BoardManager, BoardConfig
from SuperClaude.Orchestration.board.card_model import TaskCard, CardStatus
from SuperClaude.Orchestration.board.resource_tracker import ResourceTracker, ResourceLimits
from SuperClaude.Orchestration.ui.board_renderer import BoardRenderer
from SuperClaude.Orchestration.ui.card_formatter import CardFormatter
from SuperClaude.Orchestration.agents.agent_coordinator import AgentCoordinator
from SuperClaude.Orchestration.agents.recovery_manager import RecoveryManager
from SuperClaude.SubAgents.core.persona_parser import PersonaParser
from SuperClaude.SubAgents.core.prompt_generator import PromptGenerator


def print_header(title: str):
    print(f"\n{'='*80}")
    print(f" {title} ".center(80, '='))
    print(f"{'='*80}")


def print_step(step: str):
    print(f"\n🔹 {step}")
    print("-" * 60)


def wait_for_user():
    input("\n⏸️  Press Enter to continue...")


async def demo_board_system():
    """Demonstrate the complete board system with realistic scenarios"""
    
    print_header("SuperClaude Phase 2 Board System Demo")
    print("""
This demo shows the new Phase 2 features:
• Visual board with ASCII rendering
• Real-time resource tracking
• Agent lifecycle management
• Error recovery strategies
• Card movement and transitions
• Interactive board commands

Let's create a realistic development scenario...
""")
    wait_for_user()

    # Initialize board system
    print_step("Initializing Board System")
    
    config = BoardConfig(
        max_active_cards=3,
        max_token_budget=20000,
        auto_assign_agents=True,
        enable_automatic_transitions=True
    )
    
    board_manager = BoardManager(config)
    resource_tracker = board_manager.resource_tracker
    renderer = BoardRenderer(board_manager, resource_tracker)
    
    print("✅ Board system initialized")
    print(f"   Max active cards: {config.max_active_cards}")
    print(f"   Token budget: {config.max_token_budget:,}")
    print(f"   Available personas: {len(board_manager.personas)}")
    
    wait_for_user()

    # Create realistic development cards
    print_step("Creating Development Tasks")
    
    tasks = [
        ("Implement user authentication system", "backend", "high"),
        ("Create responsive dashboard UI", "frontend", "medium"), 
        ("Add comprehensive logging", "devops", "medium"),
        ("Perform security audit", "security", "critical"),
        ("Optimize database queries", "performance", "high"),
        ("Write API documentation", "scribe", "low")
    ]
    
    created_cards = []
    for title, persona, priority in tasks:
        success, msg, card = board_manager.create_card_from_request(
            title, persona_name=persona, priority=priority
        )
        if success and card:
            created_cards.append(card)
            print(f"✅ {card.id}: {title} ({persona}, {priority})")
        else:
            print(f"❌ Failed: {msg}")
    
    wait_for_user()

    # Show initial board state
    print_step("Initial Board State")
    board_view = renderer.render_board(show_resources=True)
    print(board_view)
    wait_for_user()

    # Initialize agent coordinator
    print_step("Setting up Agent Coordination")
    coordinator = AgentCoordinator(
        board_manager, 
        resource_tracker,
        board_manager.persona_parser,
        board_manager.prompt_generator
    )
    
    recovery_manager = RecoveryManager(board_manager, coordinator)
    print("✅ Agent coordinator and recovery manager ready")
    wait_for_user()

    # Simulate workflow progression
    print_step("Simulating Development Workflow")
    
    # Move some cards through the workflow
    if len(created_cards) >= 3:
        # Start high priority tasks
        high_priority_cards = [c for c in created_cards if c.priority == "high" or c.priority == "critical"]
        
        for i, card in enumerate(high_priority_cards[:2]):
            print(f"\n🚀 Starting work on: {card.title}")
            
            # Move to TODO then IN_PROGRESS
            board_manager.move_card(card.id, "todo")
            board_manager.move_card(card.id, "in_progress")
            
            # Create agent for this card
            agent = await coordinator.create_agent(card.persona_type, card)
            if agent:
                print(f"   🤖 Agent {agent.id} assigned")
                
                # Simulate some work progress
                card.token_usage = 1500 + (i * 800)
                
                # Simulate completion of first card
                if i == 0:
                    await asyncio.sleep(0.1)  # Simulate work time
                    board_manager.move_card(card.id, "review")
                    print(f"   ✅ Moved to REVIEW")
        
        print(f"\n📊 Current board state after starting work:")
        board_view = renderer.render_board(show_resources=True)
        print(board_view)
        wait_for_user()

    # Demonstrate error handling
    print_step("Demonstrating Error Recovery")
    
    if created_cards:
        test_card = created_cards[0]
        print(f"Simulating errors on card: {test_card.title}")
        
        # Simulate different types of errors
        errors = [
            (ConnectionError("Database connection failed"), "Connection issue"),
            (TimeoutError("Operation timed out"), "Timeout error"),
            (ValueError("Invalid configuration"), "Validation error")
        ]
        
        for error, description in errors:
            print(f"\n⚠️  {description}")
            strategy, message = recovery_manager.handle_error(error, test_card)
            print(f"   Recovery strategy: {strategy.value}")
            print(f"   Action: {message}")
        
        # Show error analysis
        print(f"\n📊 Error Analysis:")
        analysis = recovery_manager.analyze_error_patterns()
        print(f"   Total errors: {analysis['total_errors']}")
        print(f"   By severity: {analysis['by_severity']}")
        print(f"   Recovery success rate: {analysis['recovery_success_rate']:.1%}")
        
        wait_for_user()

    # Demonstrate card details and formatting
    print_step("Card Details and Formatting")
    
    if created_cards:
        demo_card = created_cards[0]
        
        # Show compact format
        print("📄 Compact card format (as shown on board):")
        compact_lines = CardFormatter.format_compact(demo_card, width=35)
        print("┌" + "─" * 35 + "┐")
        for line in compact_lines:
            print(f"│ {line.ljust(35)[:35]} │")
        print("└" + "─" * 35 + "┘")
        
        print(f"\n📋 Detailed card view:")
        detailed = CardFormatter.format_detailed(demo_card)
        print(detailed)
        
        wait_for_user()

    # Show agent management
    print_step("Agent Management")
    
    health_report = await coordinator.monitor_agents()
    print(f"📊 Agent Health Report:")
    print(f"   Total agents: {health_report['total_agents']}")
    print(f"   Healthy: {health_report['healthy']}")
    print(f"   Working: {health_report['working']}")
    print(f"   Paused: {health_report['paused']}")
    
    if health_report['agents']:
        print(f"\n🤖 Individual Agent Status:")
        for agent in health_report['agents']:
            print(f"   {agent['id'][:20]}: {agent['status']} ({agent['persona']})")
            print(f"      Tokens: {agent['token_usage']}, Errors: {agent['error_count']}")
    
    # Show coordinator summary
    summary = coordinator.get_agent_summary()
    print(f"\n📈 Coordinator Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    wait_for_user()

    # Final board state
    print_step("Final Board State")
    
    # Complete some work
    review_cards = board_manager.get_cards_by_status(CardStatus.REVIEW)
    for card in review_cards[:1]:  # Complete one card
        board_manager.move_card(card.id, "done")
        print(f"✅ Completed: {card.title}")
    
    # Show final board
    print(f"\n🎯 Final Board State:")
    board_view = renderer.render_board(show_resources=True)
    print(board_view)
    
    # Show mini board summary
    print(f"\n📊 Quick Status:")
    mini_view = renderer.render_mini_board()
    print(mini_view)
    
    wait_for_user()

    # Show available commands
    print_step("Available Board Commands")
    print("""
Now that you've seen the board in action, here are the commands available:

📋 Basic Commands:
   /sc:board show              - Display full board
   /sc:board show --mini       - Compact summary
   /sc:board status <card_id>  - Card details

🔄 Card Management:
   /sc:board move <card_id> <column>  - Move card
   /sc:board pause <card_id>          - Pause execution
   /sc:board resume <card_id>         - Resume execution
   /sc:board fail <card_id>           - Mark as failed
   /sc:board retry <card_id>          - Retry failed card

🤖 Agent Management:
   /sc:board agents                   - Show all agents
   /sc:board assign <card_id> --persona <type>  - Reassign

⚠️ Error Handling:
   /sc:board errors <card_id>         - Show errors
   /sc:board errors --recommendations  - Get suggestions

🧹 Maintenance:
   /sc:board clear --completed        - Remove done cards
   /sc:board fallback "<request>"     - Use main system

To enable these commands in Claude Code, see the setup instructions below.
""")
    
    # Clean up
    print_step("Cleanup")
    active_agents = list(coordinator.agents.keys())
    for agent_id in active_agents:
        await coordinator.terminate_agent(agent_id, "Demo complete")
    
    print(f"✅ Demo complete! Cleaned up {len(active_agents)} agents")
    print("\n🎉 Phase 2 board system successfully demonstrated!")


def show_integration_instructions():
    """Show how to integrate the board commands with Claude Code"""
    print_header("Integration Instructions")
    print("""
To make the /sc:board commands available in Claude Code:

1. 📁 Command Registration:
   The board.md file is already in SuperClaude/Commands/
   Claude Code should auto-discover it from COMMANDS.md

2. 🔧 Enable the Board System:
   Add to your .claude/CLAUDE.md:
   
   ```
   # Enable SuperClaude Board System
   @SuperClaude/Commands/board.md
   ```

3. 🚀 Usage Examples:
   
   # Show the current board state
   /sc:board show
   
   # Create a new task (if board system is active)
   /sc:board create "Fix login bug" --persona backend --priority high
   
   # Move a card through workflow
   /sc:board move card_abc123 in_progress
   
   # Check card details
   /sc:board status card_abc123
   
   # View all active agents
   /sc:board agents --detailed

4. 🔗 Integration Points:
   - The board system integrates with existing SuperClaude personas
   - Works with MCP servers (Context7, Sequential, Magic, Playwright)
   - Provides fallback to main Claude system if needed
   - Respects token limits and resource management

5. 🎯 Command Flow:
   User types /sc:board command → Claude Code processes → Board system executes → Visual feedback

6. 📊 Monitoring:
   - Token usage displayed in real-time
   - Resource warnings before limits hit
   - Error recovery suggestions provided
   - Full audit trail maintained

The board system is designed to be transparent and controllable,
giving you full visibility into multi-agent task execution.
""")


async def main():
    """Run the Phase 2 demonstration"""
    try:
        await demo_board_system()
        show_integration_instructions()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting SuperClaude Phase 2 Demo...")
    print("   Use Ctrl+C to exit at any time")
    asyncio.run(main())