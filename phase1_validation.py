#!/usr/bin/env python3
"""
Phase 1 Validation Script for P2SA v2.0 Board-Based Orchestration System
Verifies that all Phase 1 success criteria are met
"""

import sys
import os
from pathlib import Path

# Add project path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_phase1_implementation():
    """Test Phase 1 implementation against success criteria"""
    print("🧪 P2SA v2.0 Phase 1 Validation")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Card creation and storage
    print("\n✅ Test 1: Basic card creation and storage")
    total_tests += 1
    try:
        from SuperClaude.Orchestration.board import CardFactory, BoardManager, CardPriority
        
        # Create board manager
        board = BoardManager()
        
        # Create a test card
        success, message, card = board.create_card_from_request(
            "Implement user authentication system",
            persona_name="security",
            priority=CardPriority.HIGH
        )
        
        if success and card:
            print(f"   ✅ Card created: {card.id} - {card.title}")
            print(f"   ✅ Card stored in board state: {card.id in board.board_state.cards}")
            success_count += 1
        else:
            print(f"   ❌ Card creation failed: {message}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Resource limits enforced (max 3 active cards)
    print("\n✅ Test 2: Resource limits enforced (max 3 active cards)")
    total_tests += 1
    try:
        from SuperClaude.Orchestration.board import get_resource_tracker
        
        tracker = get_resource_tracker()
        
        # Test resource allocation
        allocated1 = tracker.allocate_card_resources("test1")
        allocated2 = tracker.allocate_card_resources("test2") 
        allocated3 = tracker.allocate_card_resources("test3")
        allocated4 = tracker.allocate_card_resources("test4")  # Should fail
        
        if allocated1 and allocated2 and allocated3 and not allocated4:
            print("   ✅ Resource limits properly enforced")
            print(f"   ✅ Active cards: {tracker.usage.active_cards}/3")
            success_count += 1
        else:
            print(f"   ❌ Resource limit enforcement failed")
            
        # Cleanup
        tracker.release_card_resources("test1")
        tracker.release_card_resources("test2")
        tracker.release_card_resources("test3")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Sub-agent creation API integration
    print("\n✅ Test 3: Sub-agent creation API integration")
    total_tests += 1
    try:
        board = BoardManager()
        
        # Test sub-agent creation
        success, message, agent_config = board.create_sub_agent("general")
        
        if success and agent_config:
            print(f"   ✅ Sub-agent created: {agent_config.name}")
            print(f"   ✅ System prompt generated: {len(agent_config.system_prompt)} chars")
            success_count += 1
        else:
            print(f"   ❌ Sub-agent creation failed: {message}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Fallback to documentation personas
    print("\n✅ Test 4: Fallback to documentation personas if board fails")
    total_tests += 1
    try:
        from SuperClaude.Orchestration.board import BoardConfig
        
        # Create board with fallback enabled
        config = BoardConfig(fallback_to_personas=True)
        board = BoardManager(config)
        
        # Test fallback mechanism
        success, message = board.fallback_to_personas("Test request for fallback")
        
        if success:
            print("   ✅ Fallback mechanism functional")
            success_count += 1
        else:
            print(f"   ❌ Fallback failed: {message}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Integration verification
    print("\n✅ Test 5: Component integration verification")
    total_tests += 1
    try:
        board = BoardManager()
        
        # Create and process a card through the workflow
        success, message, card = board.create_card_from_request(
            "Analyze system performance",
            persona_name="analyzer",
            priority=CardPriority.MEDIUM
        )
        
        if success and card:
            # Start the card
            start_success, start_message = board.start_card(card.id)
            
            if start_success:
                # Get board status
                status = board.get_board_status()
                
                if status and 'board' in status and 'workflow' in status:
                    print("   ✅ End-to-end workflow functional")
                    print(f"   ✅ Board status accessible: {status['board']['session_id']}")
                    success_count += 1
                else:
                    print("   ❌ Board status not accessible")
            else:
                print(f"   ❌ Card start failed: {start_message}")
        else:
            print(f"   ❌ Card creation failed for integration test: {message}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: File structure verification
    print("\n✅ Test 6: File structure verification")
    total_tests += 1
    try:
        required_files = [
            "SuperClaude/Orchestration/board/card_model.py",
            "SuperClaude/Orchestration/board/resource_tracker.py", 
            "SuperClaude/Orchestration/board/workflow_engine.py",
            "SuperClaude/Orchestration/board/board_manager.py",
            "SuperClaude/SubAgents/templates/system_prompt.j2",
            "SuperClaude/SubAgents/core/persona_parser.py",
            "SuperClaude/SubAgents/core/prompt_generator.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if not missing_files:
            print("   ✅ All required files present")
            success_count += 1
        else:
            print(f"   ❌ Missing files: {missing_files}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Phase 1 Validation Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 Phase 1 SUCCESS: All criteria met!")
        print("\n✅ Foundation infrastructure complete")
        print("✅ Resource safety implemented")
        print("✅ Card-based context preservation working")
        print("✅ Sub-agent integration functional")
        print("✅ Graceful fallback available")
        print("\n🚀 Ready for Phase 2: Visual Workflow")
        return True
    else:
        print(f"⚠️  Phase 1 PARTIAL: {total_tests - success_count} issues need resolution")
        return False

if __name__ == "__main__":
    test_phase1_implementation()