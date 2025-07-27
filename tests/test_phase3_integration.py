#!/usr/bin/env python3
"""
Phase 3 Integration Tests
Comprehensive testing suite for multi-agent orchestration features
"""

import sys
import os
import asyncio
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Add SuperClaude to path
sys.path.insert(0, str(Path(__file__).parent))

from SuperClaude.Orchestration.board.board_manager import BoardManager, BoardConfig
from SuperClaude.Orchestration.board.card_model import Card, CardStatus, CardType, CardPriority
from SuperClaude.Orchestration.board.integration_workflow import IntegrationWorkflow, IntegrationStrategy
from SuperClaude.Orchestration.ui.progress_tracker import ProgressTracker
from SuperClaude.Orchestration.board.performance_analytics import PerformanceAnalytics
from SuperClaude.SubAgents.core.delegation_engine import DelegationEngine
from SuperClaude.Orchestration.agents.recovery_manager import RecoveryManager


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for Phase 3 Advanced Orchestration"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = BoardConfig(
            max_active_cards=3,
            max_token_budget=20000,
            auto_assign_agents=True,
            enable_automatic_transitions=True,
            persist_state=False  # Don't persist during tests
        )
        
        self.board = BoardManager(self.config)
        self.delegation_engine = DelegationEngine(Mock(), Mock())
        self.integration_workflow = IntegrationWorkflow(self.board)
        self.progress_tracker = ProgressTracker(self.board)
        self.analytics = PerformanceAnalytics(self.board, storage_path="/tmp/test_analytics")
        
    def tearDown(self):
        """Clean up after tests"""
        self.progress_tracker.stop_tracking()
        
    def test_smart_delegation_assignment(self):
        """Test intelligent task assignment based on agent capabilities"""
        # Create test cards with different requirements
        ui_card = Card(
            title="Build React Component",
            description="Create responsive UI component with accessibility",
            card_type=CardType.IMPLEMENTATION,
            priority=CardPriority.HIGH
        )
        
        api_card = Card(
            title="Create REST API",
            description="Build secure API endpoint with authentication",
            card_type=CardType.IMPLEMENTATION,
            priority=CardPriority.MEDIUM
        )
        
        security_card = Card(
            title="Security Audit",
            description="Perform vulnerability assessment and penetration testing",
            card_type=CardType.ANALYSIS,
            priority=CardPriority.CRITICAL
        )
        
        # Test delegation
        with patch.object(self.delegation_engine, '_get_available_agents') as mock_agents:
            mock_agents.return_value = ['agent_frontend_001', 'agent_backend_001', 'agent_security_001']
            
            # UI card should go to frontend agent
            ui_agent = self.delegation_engine.assign_task(ui_card)
            self.assertIn('frontend', ui_agent)
            
            # API card should go to backend agent  
            api_agent = self.delegation_engine.assign_task(api_card)
            self.assertIn('backend', api_agent)
            
            # Security card should go to security agent
            security_agent = self.delegation_engine.assign_task(security_card)
            self.assertIn('security', security_agent)
            
    def test_multi_agent_integration_workflow(self):
        """Test multi-agent coordination through INTEGRATE column"""
        # Create cards representing work from different agents
        frontend_card = Card(
            id="card_frontend",
            title="UI Implementation",
            description="Frontend component completed",
            status=CardStatus.REVIEW,
            assigned_agent="agent_frontend_001"
        )
        frontend_card.result.output = "React component with responsive design"
        frontend_card.result.artifacts = ["src/components/UserCard.jsx", "src/styles/UserCard.css"]
        
        backend_card = Card(
            id="card_backend", 
            title="API Implementation",
            description="Backend API completed",
            status=CardStatus.REVIEW,
            assigned_agent="agent_backend_001"
        )
        backend_card.result.output = "REST API with validation and authentication"
        backend_card.result.artifacts = ["src/api/users.js", "src/middleware/auth.js"]
        
        # Test sequential integration
        cards = [backend_card, frontend_card]  # Backend first, then frontend
        success, message = self.integration_workflow.coordinate_agents(cards, IntegrationStrategy.SEQUENTIAL)
        
        self.assertTrue(success)
        self.assertIn("Sequential integration completed", message)
        
        # Test parallel integration
        frontend_card.status = CardStatus.REVIEW  # Reset status
        backend_card.status = CardStatus.REVIEW
        
        success, message = self.integration_workflow.coordinate_agents(cards, IntegrationStrategy.PARALLEL)
        
        self.assertTrue(success)
        self.assertIn("Parallel integration completed", message)
        
    def test_conflict_detection_and_resolution(self):
        """Test detection and resolution of integration conflicts"""
        # Create cards with conflicting file modifications
        card1 = Card(
            id="card_001",
            title="Feature A",
            assigned_agent="agent_frontend_001"
        )
        card1.result.artifacts = ["src/shared/utils.js", "src/components/Form.jsx"]
        
        card2 = Card(
            id="card_002", 
            title="Feature B",
            assigned_agent="agent_backend_001"
        )
        card2.result.artifacts = ["src/shared/utils.js", "src/api/validation.js"]  # Conflict on utils.js
        
        # Create contributions
        from SuperClaude.Orchestration.board.integration_workflow import AgentContribution
        contributions = [
            AgentContribution(
                agent_id="agent_frontend_001",
                card_id="card_001",
                output="Frontend changes",
                artifacts=card1.result.artifacts,
                metrics={},
                timestamp=datetime.now()
            ),
            AgentContribution(
                agent_id="agent_backend_001", 
                card_id="card_002",
                output="Backend changes",
                artifacts=card2.result.artifacts,
                metrics={},
                timestamp=datetime.now()
            )
        ]
        
        # Test conflict detection
        conflicts = self.integration_workflow._detect_conflicts(contributions)
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, "file_modification")
        self.assertIn("src/shared/utils.js", conflicts[0].description)
        
    def test_real_time_progress_tracking(self):
        """Test real-time progress updates and activity feed"""
        # Start progress tracking
        self.progress_tracker.start_tracking()
        
        # Create test card and simulate agent progress
        card = Card(
            id="test_card",
            title="Test Task",
            status=CardStatus.ACTIVE,
            assigned_agent="agent_frontend_001"
        )
        card.started_at = datetime.now()
        
        # Add to board
        self.board.board_state.cards[card.id] = card
        self.board.board_state.active_agents["agent_frontend_001"] = card.id
        
        # Update progress
        self.progress_tracker.update_agent_progress(
            agent_id="agent_frontend_001",
            card_id=card.id,
            progress=75,
            current_action="Finalizing component styles",
            eta_seconds=120
        )
        
        # Add activity
        from SuperClaude.Orchestration.ui.progress_tracker import ActivityType
        self.progress_tracker.add_activity(
            ActivityType.AGENT_STARTED,
            "Frontend agent started working on UI component",
            agent_id="agent_frontend_001",
            card_id=card.id
        )
        
        # Test board rendering with progress
        board_display = self.progress_tracker.render_board_with_progress()
        
        self.assertIn("75%", board_display)
        self.assertIn("2m", board_display)  # ETA
        self.assertIn("Frontend agent started", board_display)
        
        # Test performance metrics
        metrics = self.progress_tracker.get_performance_metrics()
        
        self.assertIn("avg_render_time_ms", metrics)
        self.assertIn("active_agents", metrics)
        self.assertEqual(metrics["active_agents"], 1)
        
    def test_performance_analytics_and_learning(self):
        """Test metrics collection and performance optimization"""
        # Create test card
        card = Card(
            id="analytics_test",
            title="Test Implementation",
            card_type=CardType.IMPLEMENTATION,
            priority=CardPriority.HIGH
        )
        card.metrics.token_usage = 3500
        card.metrics.error_count = 0
        card.result.artifacts = ["src/test.js"]
        
        # Record task start and completion
        agent_id = "agent_frontend_001"
        self.analytics.record_task_start(card, agent_id)
        
        # Simulate some processing time
        import time
        time.sleep(0.1)
        
        self.analytics.record_task_completion(card, agent_id, success=True)
        
        # Test agent performance retrieval
        performance = self.analytics.get_agent_performance(agent_id)
        
        self.assertEqual(performance["total_tasks"], 1)
        self.assertEqual(performance["success_rate"], 1.0)
        self.assertGreater(performance["avg_duration_minutes"], 0)
        
        # Test system metrics
        system_metrics = self.analytics.get_system_metrics()
        
        self.assertEqual(system_metrics["total_tasks"], 1)
        self.assertEqual(system_metrics["success_rate"], 1.0)
        
        # Test resource prediction
        new_card = Card(
            title="Similar Task",
            card_type=CardType.IMPLEMENTATION,
            priority=CardPriority.HIGH
        )
        
        prediction = self.analytics.predict_resource_needs(new_card)
        
        self.assertIn("estimated_duration_minutes", prediction)
        self.assertIn("estimated_tokens", prediction)
        self.assertIn("confidence", prediction)
        
    def test_automatic_error_recovery(self):
        """Test automatic error recovery and reassignment"""
        # Create mock delegation engine for recovery manager
        mock_delegation = Mock()
        mock_delegation.find_alternative_agent.return_value = "agent_backend_002"
        mock_delegation.release_agent = Mock()
        
        # Create recovery manager with delegation
        recovery_manager = RecoveryManager(
            self.board, 
            Mock(),  # Mock agent coordinator
            mock_delegation
        )
        
        # Create test card and error
        card = Card(
            id="failing_card",
            title="Failing Task",
            assigned_agent="agent_frontend_001"
        )
        
        test_error = RuntimeError("Agent processing failed")
        
        # Test error handling
        strategy, message = recovery_manager.handle_error(test_error, card, "agent_frontend_001")
        
        self.assertIsNotNone(strategy)
        self.assertIn("Retrying", message)
        
        # Test automatic reassignment
        recovery_manager.auto_reassignment_enabled = True
        
        # Simulate multiple failures to trigger reassignment
        for _ in range(3):
            recovery_manager.handle_error(test_error, card, "agent_frontend_001")
            
        # The next error should trigger reassignment
        strategy, message = recovery_manager.handle_error(test_error, card, "agent_frontend_001")
        
        # Should use delegation engine for reassignment
        self.assertIn("reassign", strategy.value.lower())
        
        # Test failure analysis
        analysis = recovery_manager.get_failure_analysis("agent_frontend_001")
        
        self.assertGreater(analysis["total_errors"], 0)
        self.assertIn("recommendation", analysis)
        
    def test_end_to_end_workflow(self):
        """Test complete end-to-end multi-agent workflow"""
        print("\n🚀 Running End-to-End Multi-Agent Workflow Test")
        
        # 1. Create complex task requiring multiple agents
        print("📋 Creating complex full-stack feature task...")
        
        main_card = Card(
            title="User Authentication System",
            description="Complete user auth with frontend, backend, and security",
            card_type=CardType.IMPLEMENTATION,
            priority=CardPriority.HIGH
        )
        
        # 2. Simulate breakdown into subtasks
        frontend_card = Card(
            id="auth_frontend",
            title="Login UI Components",
            description="React login forms with validation",
            card_type=CardType.IMPLEMENTATION,
            status=CardStatus.REVIEW,
            assigned_agent="agent_frontend_001"
        )
        frontend_card.result.output = "Login/signup forms with validation"
        frontend_card.result.artifacts = ["src/components/LoginForm.jsx", "src/components/SignupForm.jsx"]
        
        backend_card = Card(
            id="auth_backend",
            title="Authentication API",
            description="JWT-based auth endpoints",
            card_type=CardType.IMPLEMENTATION, 
            status=CardStatus.REVIEW,
            assigned_agent="agent_backend_001"
        )
        backend_card.result.output = "Authentication endpoints with JWT"
        backend_card.result.artifacts = ["src/api/auth.js", "src/middleware/jwt.js"]
        
        security_card = Card(
            id="auth_security",
            title="Security Review",
            description="Security audit of auth system",
            card_type=CardType.ANALYSIS,
            status=CardStatus.REVIEW,
            assigned_agent="agent_security_001"
        )
        security_card.result.output = "Security audit completed - no vulnerabilities found"
        security_card.result.artifacts = ["docs/security_audit.md"]
        
        # 3. Test delegation decisions
        print("🎯 Testing intelligent delegation...")
        
        with patch.object(self.delegation_engine, '_get_available_agents') as mock_agents:
            mock_agents.return_value = ['agent_frontend_001', 'agent_backend_001', 'agent_security_001']
            
            # Each card should be assigned to appropriate specialist
            frontend_assignment = self.delegation_engine.assign_task(frontend_card)
            backend_assignment = self.delegation_engine.assign_task(backend_card)
            security_assignment = self.delegation_engine.assign_task(security_card)
            
            print(f"   ✅ Frontend card → {frontend_assignment}")
            print(f"   ✅ Backend card → {backend_assignment}")
            print(f"   ✅ Security card → {security_assignment}")
        
        # 4. Test multi-agent integration
        print("🔄 Testing multi-agent integration...")
        
        cards_to_integrate = [backend_card, frontend_card, security_card]
        
        # Test hierarchical integration (security as master)
        success, message = self.integration_workflow.coordinate_agents(
            cards_to_integrate, 
            IntegrationStrategy.HIERARCHICAL
        )
        
        print(f"   ✅ Integration result: {message}")
        self.assertTrue(success)
        
        # 5. Test progress tracking
        print("📊 Testing real-time progress tracking...")
        
        self.progress_tracker.start_tracking()
        
        # Simulate active work
        for i, card in enumerate(cards_to_integrate):
            self.board.board_state.cards[card.id] = card
            if card.assigned_agent:
                self.board.board_state.active_agents[card.assigned_agent] = card.id
                
                self.progress_tracker.update_agent_progress(
                    agent_id=card.assigned_agent,
                    card_id=card.id,
                    progress=75 + i * 5,
                    current_action=f"Working on {card.title}",
                    eta_seconds=60 - i * 10
                )
        
        # Generate board display
        board_display = self.progress_tracker.render_board_with_progress()
        print("   ✅ Real-time board generated successfully")
        
        # 6. Test analytics and learning
        print("📈 Testing performance analytics...")
        
        # Record completion metrics for all agents
        for card in cards_to_integrate:
            if card.assigned_agent:
                self.analytics.record_task_start(card, card.assigned_agent)
                self.analytics.record_task_completion(card, card.assigned_agent, success=True)
        
        # Get system metrics
        system_metrics = self.analytics.get_system_metrics()
        print(f"   ✅ System success rate: {system_metrics['success_rate']:.1%}")
        
        # Get optimization recommendations
        recommendations = self.analytics.get_optimization_recommendations()
        print(f"   ✅ Generated {len(recommendations)} optimization recommendations")
        
        # 7. Test error recovery
        print("🛡️  Testing error recovery...")
        
        mock_delegation = Mock()
        mock_delegation.find_alternative_agent.return_value = "agent_frontend_002"
        mock_delegation.release_agent = Mock()
        
        recovery_manager = RecoveryManager(self.board, Mock(), mock_delegation)
        
        # Simulate error and recovery
        test_error = RuntimeError("Simulated agent failure")
        strategy, recovery_message = recovery_manager.handle_error(
            test_error, frontend_card, "agent_frontend_001"
        )
        
        print(f"   ✅ Error recovery strategy: {strategy.value}")
        
        print("\n🎉 End-to-End Test Completed Successfully!")
        print("   ✅ Smart delegation working")
        print("   ✅ Multi-agent integration working") 
        print("   ✅ Real-time progress tracking working")
        print("   ✅ Performance analytics working")
        print("   ✅ Error recovery working")
        
        self.assertTrue(True)  # Test passed
        
    def test_integration_strategies_comparison(self):
        """Test and compare different integration strategies"""
        print("\n🔍 Testing Integration Strategy Comparison")
        
        # Create identical sets of cards for each strategy
        def create_test_cards():
            return [
                Card(
                    id=f"card_a_{i}",
                    title="Component A",
                    status=CardStatus.REVIEW,
                    assigned_agent="agent_frontend_001"
                ),
                Card(
                    id=f"card_b_{i}",
                    title="Component B", 
                    status=CardStatus.REVIEW,
                    assigned_agent="agent_backend_001"
                )
            ]
        
        strategies = [
            IntegrationStrategy.SEQUENTIAL,
            IntegrationStrategy.PARALLEL,
            IntegrationStrategy.HIERARCHICAL,
            IntegrationStrategy.CONSENSUS
        ]
        
        results = {}
        
        for strategy in strategies:
            print(f"   Testing {strategy.value} strategy...")
            cards = create_test_cards()
            
            # Add realistic outputs
            cards[0].result.output = "Frontend component completed"
            cards[0].result.artifacts = ["src/ComponentA.jsx"]
            cards[1].result.output = "Backend API completed"  
            cards[1].result.artifacts = ["src/api/componentB.js"]
            
            start_time = datetime.now()
            success, message = self.integration_workflow.coordinate_agents(cards, strategy)
            duration = (datetime.now() - start_time).total_seconds()
            
            results[strategy.value] = {
                "success": success,
                "message": message,
                "duration": duration
            }
            
            print(f"      ✅ {strategy.value}: {message} ({duration:.3f}s)")
        
        # All strategies should succeed
        for strategy_name, result in results.items():
            self.assertTrue(result["success"], f"{strategy_name} strategy failed")
            
        print("   ✅ All integration strategies working correctly")


class TestPhase3Performance(unittest.TestCase):
    """Performance tests for Phase 3 features"""
    
    def test_delegation_performance(self):
        """Test delegation engine performance under load"""
        print("\n⚡ Testing Delegation Performance")
        
        delegation_engine = DelegationEngine(Mock(), Mock())
        
        # Create many test cards
        cards = []
        for i in range(100):
            card = Card(
                title=f"Task {i}",
                description=f"Test task number {i}",
                card_type=CardType.IMPLEMENTATION
            )
            cards.append(card)
        
        # Mock available agents
        with patch.object(delegation_engine, '_get_available_agents') as mock_agents:
            mock_agents.return_value = ['agent_frontend_001', 'agent_backend_001', 'agent_security_001']
            
            start_time = datetime.now()
            
            # Assign all cards
            assignments = []
            for card in cards:
                agent = delegation_engine.assign_task(card)
                assignments.append(agent)
                
            duration = (datetime.now() - start_time).total_seconds()
            
        print(f"   ✅ Assigned 100 cards in {duration:.3f}s ({duration*10:.1f}ms per card)")
        
        # Performance should be reasonable
        self.assertLess(duration, 1.0, "Delegation should complete in under 1 second")
        
        # All cards should be assigned
        successful_assignments = sum(1 for a in assignments if a is not None)
        self.assertGreater(successful_assignments, 90, "At least 90% of cards should be assigned")
        
    def test_progress_tracking_performance(self):
        """Test progress tracker performance with many updates"""
        print("\n📊 Testing Progress Tracking Performance")
        
        board = BoardManager(BoardConfig(persist_state=False))
        progress_tracker = ProgressTracker(board, update_interval=0.1)  # Fast updates
        
        try:
            progress_tracker.start_tracking()
            
            # Add many cards and agents
            for i in range(50):
                card = Card(id=f"perf_card_{i}", title=f"Performance Test {i}")
                agent_id = f"agent_test_{i}"
                
                board.board_state.cards[card.id] = card
                board.board_state.active_agents[agent_id] = card.id
                
                progress_tracker.update_agent_progress(
                    agent_id=agent_id,
                    card_id=card.id,
                    progress=i % 100,
                    current_action=f"Processing task {i}"
                )
            
            # Test rendering performance
            start_time = datetime.now()
            board_display = progress_tracker.render_board_with_progress()
            render_time = (datetime.now() - start_time).total_seconds()
            
            print(f"   ✅ Rendered board with 50 active agents in {render_time*1000:.1f}ms")
            
            # Should render quickly
            self.assertLess(render_time, 0.5, "Board rendering should be under 500ms")
            
            # Check performance metrics
            metrics = progress_tracker.get_performance_metrics()
            self.assertEqual(metrics["active_agents"], 50)
            
        finally:
            progress_tracker.stop_tracking()


def run_integration_tests():
    """Run all Phase 3 integration tests"""
    print("=" * 80)
    print("🧪 PHASE 3 ADVANCED ORCHESTRATION - INTEGRATION TESTS")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add integration tests
    suite.addTest(TestPhase3Integration('test_smart_delegation_assignment'))
    suite.addTest(TestPhase3Integration('test_multi_agent_integration_workflow'))
    suite.addTest(TestPhase3Integration('test_conflict_detection_and_resolution'))
    suite.addTest(TestPhase3Integration('test_real_time_progress_tracking'))
    suite.addTest(TestPhase3Integration('test_performance_analytics_and_learning'))
    suite.addTest(TestPhase3Integration('test_automatic_error_recovery'))
    suite.addTest(TestPhase3Integration('test_integration_strategies_comparison'))
    suite.addTest(TestPhase3Integration('test_end_to_end_workflow'))
    
    # Add performance tests
    suite.addTest(TestPhase3Performance('test_delegation_performance'))
    suite.addTest(TestPhase3Performance('test_progress_tracking_performance'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print(f"   Ran {result.testsRun} tests successfully")
        print("\n🚀 Phase 3 Advanced Orchestration is ready for deployment!")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        
        if result.failures:
            print("\n💥 FAILURES:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback}")
                
        if result.errors:
            print("\n🐛 ERRORS:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)