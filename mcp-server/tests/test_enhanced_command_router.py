"""
Tests for Enhanced Command Router - Phase 2
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.core.enhanced_command_router import (
    EnhancedCommandRouter, CommandPriority, DependencyType, 
    CommandDependency, ExecutionPlan
)
from src.core.enhanced_nlp_engine import (
    ParsedCommand, ConfidenceLevel, IntentType
)
from src.models.command_models import ParsedIntent, CommandResponse, ExecutionDetails
from src.core.backend_client import BackendClient, BackendClientError


class TestEnhancedCommandRouter:
    """Test Enhanced Command Router functionality"""
    
    @pytest.fixture
    def mock_backend_client(self):
        """Create mock backend client"""
        client = Mock(spec=BackendClient)
        
        # Mock common methods
        client.connect_drone = AsyncMock(return_value=Mock(dict=Mock(return_value={"success": True})))
        client.takeoff_drone = AsyncMock(return_value=Mock(dict=Mock(return_value={"success": True})))
        client.move_drone = AsyncMock(return_value=Mock(dict=Mock(return_value={"success": True})))
        client.land_drone = AsyncMock(return_value=Mock(dict=Mock(return_value={"success": True})))
        client.take_photo = AsyncMock(return_value=Mock(dict=Mock(return_value={"success": True})))
        client.get_drone_status = AsyncMock(return_value=Mock(dict=Mock(return_value={"status": "connected"})))
        
        return client
    
    @pytest.fixture
    def command_router(self, mock_backend_client):
        """Create command router instance"""
        return EnhancedCommandRouter(mock_backend_client)
    
    @pytest.fixture
    def sample_parsed_command(self):
        """Create sample parsed command"""
        intent = ParsedIntent(
            action="connect",
            parameters={"drone_id": "AA"},
            confidence=0.8
        )
        
        return ParsedCommand(
            primary_intent=intent,
            alternative_intents=[],
            confidence_level=ConfidenceLevel.HIGH,
            parameter_confidence={"drone_id": 0.9},
            missing_parameters=[],
            suggestions=[]
        )
    
    def test_initialization(self, command_router):
        """Test command router initialization"""
        assert command_router is not None
        assert hasattr(command_router, 'backend_client')
        assert hasattr(command_router, 'action_mappings')
        assert hasattr(command_router, 'command_priorities')
        assert hasattr(command_router, 'dependencies')
        assert hasattr(command_router, 'execution_stats')
    
    @pytest.mark.asyncio
    async def test_basic_command_execution(self, command_router, sample_parsed_command):
        """Test basic command execution"""
        response = await command_router.execute_enhanced_command(sample_parsed_command)
        
        assert isinstance(response, CommandResponse)
        assert response.success is True
        assert response.parsed_intent.action == "connect"
        assert "confidence_level" in response.result
        assert "alternatives_available" in response.result
    
    @pytest.mark.asyncio
    async def test_command_validation(self, command_router):
        """Test command validation"""
        # Valid command
        valid_intent = ParsedIntent(
            action="connect",
            parameters={"drone_id": "AA"},
            confidence=0.8
        )
        valid_parsed = ParsedCommand(
            primary_intent=valid_intent,
            alternative_intents=[],
            confidence_level=ConfidenceLevel.HIGH,
            parameter_confidence={"drone_id": 0.9},
            missing_parameters=[],
            suggestions=[]
        )
        
        validation = await command_router._validate_command(valid_parsed)
        assert validation["valid"] is True
        
        # Invalid command with missing parameters
        invalid_intent = ParsedIntent(
            action="move",
            parameters={"drone_id": "AA"},
            confidence=0.8
        )
        invalid_parsed = ParsedCommand(
            primary_intent=invalid_intent,
            alternative_intents=[],
            confidence_level=ConfidenceLevel.HIGH,
            parameter_confidence={"drone_id": 0.9},
            missing_parameters=["direction", "distance"],
            suggestions=[]
        )
        
        validation = await command_router._validate_command(invalid_parsed)
        assert validation["valid"] is False
        assert "Missing required parameters" in validation["error"]
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, command_router, mock_backend_client):
        """Test retry mechanism"""
        # Setup backend to fail once then succeed
        mock_backend_client.connect_drone.side_effect = [
            BackendClientError("Connection failed"),
            Mock(dict=Mock(return_value={"success": True}))
        ]
        
        async def mock_executor(parameters):
            return await mock_backend_client.connect_drone(parameters["drone_id"])
        
        result = await command_router._execute_with_retry(mock_executor, {"drone_id": "AA"})
        
        # Should succeed after retry
        assert result is not None
        assert mock_backend_client.connect_drone.call_count == 2
    
    @pytest.mark.asyncio
    async def test_alternative_intent_fallback(self, command_router):
        """Test alternative intent fallback"""
        # Primary intent with unknown action
        primary_intent = ParsedIntent(
            action="unknown_action",
            parameters={"drone_id": "AA"},
            confidence=0.8
        )
        
        # Alternative intent with known action
        alt_intent = ParsedIntent(
            action="connect",
            parameters={"drone_id": "AA"},
            confidence=0.7
        )
        
        parsed_command = ParsedCommand(
            primary_intent=primary_intent,
            alternative_intents=[alt_intent],
            confidence_level=ConfidenceLevel.MEDIUM,
            parameter_confidence={"drone_id": 0.9},
            missing_parameters=[],
            suggestions=[]
        )
        
        response = await command_router.execute_enhanced_command(parsed_command)
        
        # Should use alternative intent
        assert response.parsed_intent.action == "connect"
    
    @pytest.mark.asyncio
    async def test_low_confidence_handling(self, command_router):
        """Test handling of low confidence commands"""
        low_confidence_intent = ParsedIntent(
            action="move",
            parameters={"drone_id": "AA"},
            confidence=0.2
        )
        
        low_confidence_parsed = ParsedCommand(
            primary_intent=low_confidence_intent,
            alternative_intents=[],
            confidence_level=ConfidenceLevel.VERY_LOW,
            parameter_confidence={"drone_id": 0.9},
            missing_parameters=["direction", "distance"],
            suggestions=["方向を指定してください", "距離を指定してください"]
        )
        
        response = await command_router.execute_enhanced_command(low_confidence_parsed)
        
        assert response.success is False
        assert "suggestions" in response.result
        assert len(response.result["suggestions"]) > 0
    
    def test_command_priority_mapping(self, command_router):
        """Test command priority mapping"""
        assert command_router.command_priorities["emergency"] == CommandPriority.EMERGENCY
        assert command_router.command_priorities["connect"] == CommandPriority.HIGH
        assert command_router.command_priorities["move"] == CommandPriority.NORMAL
        assert command_router.command_priorities["status"] == CommandPriority.LOW
    
    def test_dependency_rules(self, command_router):
        """Test dependency rules"""
        # Check that takeoff requires connect
        takeoff_requires_connect = any(
            dep.source_action == "connect" and 
            dep.target_action == "takeoff" and 
            dep.dependency_type == DependencyType.REQUIRES
            for dep in command_router.dependencies
        )
        assert takeoff_requires_connect
        
        # Check that move conflicts with emergency
        move_conflicts_emergency = any(
            dep.source_action == "emergency" and 
            dep.target_action == "move" and 
            dep.dependency_type == DependencyType.CONFLICTS
            for dep in command_router.dependencies
        )
        assert move_conflicts_emergency
    
    def test_execution_plan_creation(self, command_router):
        """Test execution plan creation"""
        # Create sample commands
        commands = [
            ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
            ParsedIntent(action="move", parameters={"drone_id": "AA", "direction": "right", "distance": 50}, confidence=0.8),
        ]
        
        parsed_commands = []
        for cmd in commands:
            parsed_cmd = ParsedCommand(
                primary_intent=cmd,
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            )
            parsed_commands.append(parsed_cmd)
        
        plan = command_router._create_execution_plan(parsed_commands, "optimized")
        
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.execution_groups) > 0
        assert plan.total_estimated_time > 0
        assert plan.parallelizable_count >= 0
        assert plan.sequential_count >= 0
    
    def test_dependency_graph_building(self, command_router):
        """Test dependency graph building"""
        commands = [
            ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
        ]
        
        graph = command_router._build_dependency_graph(commands)
        
        assert isinstance(graph, dict)
        assert len(graph) == len(commands)
        # Connect should come before takeoff
        assert 1 in graph[0]  # takeoff depends on connect
    
    def test_conflict_detection(self, command_router):
        """Test conflict detection"""
        move_intent = ParsedIntent(action="move", parameters={"drone_id": "AA"}, confidence=0.8)
        emergency_intent = ParsedIntent(action="emergency", parameters={"drone_id": "AA"}, confidence=0.8)
        
        has_conflict = command_router._has_conflict(move_intent, emergency_intent)
        assert has_conflict is True
        
        # Different drones should not conflict
        move_intent_b = ParsedIntent(action="move", parameters={"drone_id": "BB"}, confidence=0.8)
        has_conflict_diff_drone = command_router._has_conflict(move_intent, move_intent_b)
        assert has_conflict_diff_drone is False
    
    @pytest.mark.asyncio
    async def test_batch_execution_sequential(self, command_router):
        """Test batch execution in sequential mode"""
        commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            )
        ]
        
        response = await command_router.execute_optimized_batch(commands, "sequential", True)
        
        assert response.success is True
        assert len(response.results) == 2
        assert response.summary.total_commands == 2
        assert "execution_plan" in response.result
    
    @pytest.mark.asyncio
    async def test_batch_execution_parallel(self, command_router):
        """Test batch execution in parallel mode"""
        # Commands that can run in parallel (different drones)
        commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "BB"}, confidence=0.8),
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            )
        ]
        
        response = await command_router.execute_optimized_batch(commands, "parallel", False)
        
        assert len(response.results) == 2
        assert "execution_plan" in response.result
        assert response.result["execution_plan"]["efficiency"] > 0
    
    def test_execution_statistics(self, command_router):
        """Test execution statistics tracking"""
        initial_stats = command_router.get_execution_statistics()
        
        assert "total_commands" in initial_stats
        assert "successful_commands" in initial_stats
        assert "failed_commands" in initial_stats
        assert "average_execution_time" in initial_stats
        
        # Update stats
        command_router._update_execution_stats(1.5, True)
        updated_stats = command_router.get_execution_statistics()
        
        assert updated_stats["total_commands"] == initial_stats["total_commands"] + 1
        assert updated_stats["successful_commands"] == initial_stats["successful_commands"] + 1
    
    def test_parallel_command_grouping(self, command_router):
        """Test parallel command grouping"""
        ready_commands = [0, 1, 2]
        commands = [
            ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            ParsedIntent(action="connect", parameters={"drone_id": "BB"}, confidence=0.8),
            ParsedIntent(action="status", parameters={}, confidence=0.8),
        ]
        
        groups = command_router._group_parallel_commands(ready_commands, commands)
        
        assert len(groups) > 0
        # Should group commands that don't conflict
        for group in groups:
            assert len(group) >= 1
    
    def test_execution_time_estimation(self, command_router):
        """Test execution time estimation"""
        commands = [
            ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
        ]
        
        execution_groups = [[0], [1]]  # Sequential execution
        estimated_time = command_router._estimate_batch_execution_time(commands, execution_groups)
        
        assert estimated_time > 0
        # Should be sum of individual times for sequential
        expected_time = 2.0 + 5.0  # connect + takeoff
        assert abs(estimated_time - expected_time) < 0.1
    
    @pytest.mark.asyncio
    async def test_error_response_creation(self, command_router):
        """Test error response creation"""
        sample_parsed = ParsedCommand(
            primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            alternative_intents=[],
            confidence_level=ConfidenceLevel.HIGH,
            parameter_confidence={},
            missing_parameters=[],
            suggestions=[]
        )
        
        error_response = command_router._create_error_response(
            sample_parsed, "Test error", "TEST_ERROR", 1.0, []
        )
        
        assert error_response.success is False
        assert "Test error" in error_response.message
        assert error_response.result["error_code"] == "TEST_ERROR"
        assert "suggestions" in error_response.result
    
    @pytest.mark.asyncio
    async def test_suggestion_response_creation(self, command_router):
        """Test suggestion response creation"""
        low_confidence_parsed = ParsedCommand(
            primary_intent=ParsedIntent(action="unknown", parameters={}, confidence=0.1),
            alternative_intents=[],
            confidence_level=ConfidenceLevel.VERY_LOW,
            parameter_confidence={},
            missing_parameters=["drone_id"],
            suggestions=["ドローンIDを指定してください"]
        )
        
        suggestion_response = command_router._create_suggestion_response(
            low_confidence_parsed, datetime.now()
        )
        
        assert suggestion_response.success is False
        assert "confidence too low" in suggestion_response.message
        assert len(suggestion_response.result["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, command_router, mock_backend_client):
        """Test command timeout handling"""
        # Mock backend to hang indefinitely
        async def hanging_operation(drone_id):
            await asyncio.sleep(10)  # Longer than timeout
            return Mock(dict=Mock(return_value={"success": True}))
        
        mock_backend_client.connect_drone = hanging_operation
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                command_router._execute_connect({"drone_id": "AA"}),
                timeout=0.1
            )
    
    def test_optimization_metrics(self, command_router):
        """Test optimization metrics calculation"""
        # Test parallelization factor calculation
        execution_state = Mock()
        execution_state.executions = [Mock() for _ in range(4)]
        execution_state.execution_groups = [[0, 1], [2], [3]]  # 2 parallel, 2 sequential
        
        factor = command_router._calculate_parallelization_factor(execution_state)
        
        assert 0 <= factor <= 1
        # 2 out of 4 commands were parallelized
        expected_factor = 2 / 4
        assert abs(factor - expected_factor) < 0.1
    
    @pytest.mark.asyncio
    async def test_backend_error_handling(self, command_router, mock_backend_client):
        """Test backend error handling"""
        # Setup backend to raise error
        mock_backend_client.connect_drone.side_effect = BackendClientError(
            "Backend unavailable", "BACKEND_ERROR"
        )
        
        sample_parsed = ParsedCommand(
            primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
            alternative_intents=[],
            confidence_level=ConfidenceLevel.HIGH,
            parameter_confidence={},
            missing_parameters=[],
            suggestions=[]
        )
        
        response = await command_router.execute_enhanced_command(sample_parsed)
        
        assert response.success is False
        assert "Backend error" in response.message
        assert response.result["error_code"] == "BACKEND_ERROR"