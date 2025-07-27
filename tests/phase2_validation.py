#!/usr/bin/env python3
"""
Phase 2 Validation Script - Test Board Visualization and Agent Coordination

This script validates all Phase 2 components work together:
- Board rendering and visualization
- Agent coordinator lifecycle management
- Recovery manager error handling
- Card movement and transitions
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from SuperClaude.Orchestration.board.board_manager import BoardManager, get_board_manager
from SuperClaude.Orchestration.board.card_model import TaskCard, CardStatus
from SuperClaude.Orchestration.board.resource_tracker import ResourceTracker
from SuperClaude.Orchestration.ui.board_renderer import BoardRenderer
from SuperClaude.Orchestration.ui.card_formatter import CardFormatter
from SuperClaude.Orchestration.agents.agent_coordinator import AgentCoordinator
from SuperClaude.Orchestration.agents.recovery_manager import RecoveryManager
from SuperClaude.SubAgents.core.persona_parser import PersonaParser
from SuperClaude.SubAgents.core.prompt_generator import PromptGenerator


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"{title.center(60)}")
    print('='*60)


async def test_board_visualization():
    """Test the board rendering and visualization components"""
    print_section("Testing Board Visualization")
    
    # Get board manager
    board_manager = get_board_manager()
    resource_tracker = board_manager.resource_tracker
    
    # Create board renderer
    renderer = BoardRenderer(board_manager, resource_tracker)
    
    # Create some test cards
    print("\n📝 Creating test cards...")
    
    card1_success, msg1, card1 = board_manager.create_card_from_request(
        "Implement user authentication system",
        persona_name="backend",
        priority="high"
    )
    print(f"Card 1: {msg1}")
    
    card2_success, msg2, card2 = board_manager.create_card_from_request(
        "Create responsive dashboard UI",
        persona_name="frontend",
        priority="medium"
    )
    print(f"Card 2: {msg2}")
    
    card3_success, msg3, card3 = board_manager.create_card_from_request(
        "Perform security audit",
        persona_name="security",
        priority="critical"
    )
    print(f"Card 3: {msg3}")
    
    # Move some cards to different columns
    print("\n🔄 Moving cards to different columns...")
    if card1:
        board_manager.move_card(card1.id, "in_progress")
        print(f"Moved {card1.id} to IN_PROGRESS")
        
    if card2:
        board_manager.move_card(card2.id, "todo")
        print(f"Moved {card2.id} to TODO")
    
    # Render the board
    print("\n🎯 Rendering board state:")
    board_view = renderer.render_board(show_resources=True)
    print(board_view)
    
    # Test mini board view
    print("\n📊 Mini board view:")
    mini_view = renderer.render_mini_board()
    print(mini_view)
    
    # Test card detail view
    if card1:
        print(f"\n📋 Detailed view of card {card1.id}:")
        detail_view = renderer.render_card_detail(card1.id)
        print(detail_view)
    
    return True


async def test_agent_coordination():
    """Test agent coordinator functionality"""
    print_section("Testing Agent Coordination")
    
    # Get dependencies
    board_manager = get_board_manager()
    resource_tracker = board_manager.resource_tracker
    persona_parser = board_manager.persona_parser
    prompt_generator = board_manager.prompt_generator
    
    # Create agent coordinator
    coordinator = AgentCoordinator(
        board_manager, 
        resource_tracker,
        persona_parser,
        prompt_generator
    )
    
    # Get a card to assign
    cards = board_manager.get_cards_by_status(CardStatus.TODO)
    if not cards:
        print("❌ No TODO cards available for agent assignment")
        return False
        
    test_card = cards[0]
    print(f"\n📝 Using card: {test_card.id} - {test_card.title}")
    
    # Create an agent
    print("\n🤖 Creating agent for backend persona...")
    agent = await coordinator.create_agent("backend", test_card)
    
    if agent:
        print(f"✅ Agent created: {agent.id}")
        print(f"   Status: {agent.status.value}")
        print(f"   Persona: {agent.persona_type}")
        print(f"   Card: {agent.card_id}")
    else:
        print("❌ Failed to create agent")
        return False
    
    # Test agent monitoring
    print("\n📊 Agent health report:")
    health = await coordinator.monitor_agents()
    print(f"Total agents: {health['total_agents']}")
    print(f"Healthy: {health['healthy']}")
    print(f"Working: {health['working']}")
    
    # Test agent pause/resume
    print(f"\n⏸️  Pausing agent {agent.id}...")
    pause_success = await coordinator.pause_agent(agent.id, "Testing pause functionality")
    print(f"Pause result: {'Success' if pause_success else 'Failed'}")
    
    print(f"\n▶️  Resuming agent {agent.id}...")
    resume_success = await coordinator.resume_agent(agent.id)
    print(f"Resume result: {'Success' if resume_success else 'Failed'}")
    
    # Get agent summary
    print("\n📈 Agent coordinator summary:")
    summary = coordinator.get_agent_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Clean up
    print(f"\n🧹 Terminating agent {agent.id}...")
    await coordinator.terminate_agent(agent.id, "Test complete")
    
    return True


async def test_error_recovery():
    """Test error recovery manager"""
    print_section("Testing Error Recovery")
    
    # Get dependencies
    board_manager = get_board_manager()
    coordinator = AgentCoordinator(
        board_manager,
        board_manager.resource_tracker,
        board_manager.persona_parser,
        board_manager.prompt_generator
    )
    
    # Create recovery manager
    recovery = RecoveryManager(board_manager, coordinator)
    
    # Create a test card
    success, msg, card = board_manager.create_card_from_request(
        "Test error recovery mechanisms",
        persona_name="qa",
        priority="high"
    )
    
    if not card:
        print("❌ Failed to create test card")
        return False
        
    print(f"✅ Created test card: {card.id}")
    
    # Simulate different error types
    errors = [
        (TimeoutError("Operation timed out"), "Timeout during execution"),
        (ValueError("Invalid input provided"), "Validation error"),
        (RuntimeError("Critical system error"), "Runtime failure")
    ]
    
    for error, description in errors:
        print(f"\n🔥 Simulating error: {description}")
        strategy, message = recovery.handle_error(error, card)
        print(f"   Recovery strategy: {strategy.value}")
        print(f"   Message: {message}")
    
    # Test error pattern analysis
    print("\n📊 Error pattern analysis:")
    analysis = recovery.analyze_error_patterns()
    print(f"Total errors: {analysis['total_errors']}")
    print(f"By severity: {analysis['by_severity']}")
    print(f"By type: {analysis['by_type']}")
    
    if analysis['patterns']:
        print("\n🔍 Detected patterns:")
        for pattern in analysis['patterns']:
            print(f"   - {pattern['type']}: {pattern['recommendation']}")
    
    # Get recovery recommendations
    print(f"\n💡 Recovery recommendations for card {card.id}:")
    recommendations = recovery.get_recovery_recommendations(card.id)
    for rec in recommendations:
        print(f"   - {rec}")
    
    return True


def test_card_formatting():
    """Test card formatting utilities"""
    print_section("Testing Card Formatting")
    
    # Create a test card
    test_card = TaskCard(
        title="Implement advanced search functionality",
        context="Add full-text search with filters and facets to the product catalog",
        priority="high",
        persona_type="backend",
        allowed_tools=["Read", "Write", "Edit", "Bash"],
        scope="feature"
    )
    
    # Add some test data
    test_card.assigned_agent = "backend-agent-impl"
    test_card.token_usage = 3500
    test_card.error_count = 2
    test_card.error_log = [
        "Connection timeout to search service",
        "Index creation failed - insufficient permissions"
    ]
    
    # Test compact formatting
    print("\n📄 Compact card format:")
    compact_lines = CardFormatter.format_compact(test_card, width=30)
    for line in compact_lines:
        print(f"│ {line} │")
    
    # Test detailed formatting
    print("\n📋 Detailed card format:")
    detailed = CardFormatter.format_detailed(test_card)
    print(detailed)
    
    # Test status update formatting
    print("\n🔄 Status update format:")
    status_update = CardFormatter.format_status_update(
        test_card,
        CardStatus.TODO,
        CardStatus.IN_PROGRESS,
        "Agent assigned and starting work"
    )
    print(status_update)
    
    # Test error notification
    print("\n⚠️  Error notification format:")
    error_notif = CardFormatter.format_error_notification(
        test_card,
        "Database connection pool exhausted"
    )
    print(error_notif)
    
    # Test progress bar
    print("\n📊 Progress indicators:")
    for percent in [0, 25, 50, 75, 100]:
        progress = CardFormatter.format_progress_bar(percent, 100, 20)
        print(f"   {percent}%: {progress}")
    
    return True


def test_board_commands():
    """Test board command integration"""
    print_section("Testing Board Commands")
    
    board_manager = get_board_manager()
    
    # Simulate command execution
    print("\n🎮 Simulating board commands...")
    
    # Show command
    print("\n/sc:board show")
    status = board_manager.get_board_status()
    print(f"Session: {status['board']['session_id']}")
    print(f"Active agents: {len(status['board']['active_agents'])}")
    print(f"Available personas: {', '.join(status['board']['available_personas'])}")
    
    # Status command
    cards = board_manager.get_cards_by_status(CardStatus.TODO)
    if cards:
        card = cards[0]
        print(f"\n/sc:board status {card.id}")
        print(f"Card: {card.title}")
        print(f"Status: {card.status.value}")
        print(f"Priority: {card.priority}")
    
    # Move command test
    if cards:
        card = cards[0]
        print(f"\n/sc:board move {card.id} review")
        success, msg = board_manager.move_card(card.id, "review")
        print(f"Result: {msg}")
    
    # Pause command test
    active_cards = board_manager.get_cards_by_status(CardStatus.IN_PROGRESS)
    if active_cards:
        card = active_cards[0]
        print(f"\n/sc:board pause {card.id}")
        success, msg = board_manager.pause_card(card.id, "Testing pause")
        print(f"Result: {msg}")
    
    return True


async def main():
    """Run all Phase 2 validation tests"""
    print("🚀 SuperClaude Phase 2 Validation")
    print("=" * 60)
    
    tests = [
        ("Board Visualization", test_board_visualization),
        ("Card Formatting", test_card_formatting),
        ("Agent Coordination", test_agent_coordination),
        ("Error Recovery", test_error_recovery),
        ("Board Commands", test_board_commands)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    print("\nDetailed results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 All Phase 2 tests passed!")
        print("\nPhase 2 implementation is complete:")
        print("- ✅ Board visualization with resource indicators")
        print("- ✅ Agent lifecycle management")
        print("- ✅ Error recovery strategies")
        print("- ✅ Card movement and transitions")
        print("- ✅ Board command interface")
        print("\nReady to proceed to Phase 3!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review and fix issues.")


if __name__ == "__main__":
    asyncio.run(main())