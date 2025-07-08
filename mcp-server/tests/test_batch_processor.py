"""
Tests for Advanced Batch Processor - Phase 2
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.core.batch_processor import (
    AdvancedBatchProcessor, BatchExecutionContext, BatchExecutionMode, 
    ErrorRecoveryStrategy, CommandExecution, BatchExecutionState
)
from src.core.enhanced_nlp_engine import EnhancedNLPEngine, ParsedCommand, ConfidenceLevel
from src.core.enhanced_command_router import EnhancedCommandRouter
from src.models.command_models import (
    NaturalLanguageCommand, ParsedIntent, CommandResponse, BatchCommandResponse
)


class TestAdvancedBatchProcessor:
    """Test Advanced Batch Processor functionality"""
    
    @pytest.fixture
    def mock_nlp_engine(self):
        """Create mock NLP engine"""
        engine = Mock(spec=EnhancedNLPEngine)
        
        def mock_parse_command(command, context=None):
            # Create different parsed commands based on input
            if "接続" in command or "connect" in command:
                action = "connect"
            elif "離陸" in command or "takeoff" in command:
                action = "takeoff"
            elif "移動" in command or "move" in command:
                action = "move"
            elif "写真" in command or "photo" in command:
                action = "photo"
            elif "着陸" in command or "land" in command:
                action = "land"
            else:
                action = "unknown"
            
            intent = ParsedIntent(
                action=action,
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
        
        engine.parse_command = Mock(side_effect=mock_parse_command)
        return engine
    
    @pytest.fixture
    def mock_command_router(self):
        """Create mock command router"""
        router = Mock(spec=EnhancedCommandRouter)
        
        async def mock_execute_command(parsed_command):
            return CommandResponse(
                success=True,
                message=f"Command {parsed_command.primary_intent.action} executed",
                parsed_intent=parsed_command.primary_intent,
                timestamp=datetime.now()
            )
        
        router.execute_enhanced_command = AsyncMock(side_effect=mock_execute_command)
        router.command_priorities = {
            "emergency": Mock(),
            "connect": Mock(),
            "takeoff": Mock(),
            "move": Mock(),
            "photo": Mock(),
            "land": Mock()
        }
        
        return router
    
    @pytest.fixture
    def batch_processor(self, mock_nlp_engine, mock_command_router):
        """Create batch processor instance"""
        return AdvancedBatchProcessor(mock_nlp_engine, mock_command_router)
    
    @pytest.fixture
    def sample_commands(self):
        """Create sample command list"""
        return [
            NaturalLanguageCommand(command="ドローンAAに接続して"),
            NaturalLanguageCommand(command="離陸して"),
            NaturalLanguageCommand(command="右に50cm移動して"),
            NaturalLanguageCommand(command="写真を撮って"),
            NaturalLanguageCommand(command="着陸して")
        ]
    
    @pytest.fixture
    def basic_context(self):
        """Create basic execution context"""
        return BatchExecutionContext(
            execution_mode=BatchExecutionMode.OPTIMIZED,
            error_recovery=ErrorRecoveryStrategy.SMART_RECOVERY,
            max_retries=2,
            timeout_per_command=10.0
        )
    
    def test_initialization(self, batch_processor):
        """Test batch processor initialization"""
        assert batch_processor is not None
        assert hasattr(batch_processor, 'nlp_engine')
        assert hasattr(batch_processor, 'command_router')
        assert hasattr(batch_processor, 'execution_time_estimates')
        assert hasattr(batch_processor, 'dependency_rules')
    
    @pytest.mark.asyncio
    async def test_basic_batch_processing(self, batch_processor, sample_commands, basic_context):
        """Test basic batch processing"""
        response = await batch_processor.process_batch(sample_commands, basic_context)
        
        assert isinstance(response, BatchCommandResponse)
        assert response.summary.total_commands == len(sample_commands)
        assert len(response.results) == len(sample_commands)
        assert "execution_analytics" in response.result
        assert "optimization_details" in response.result
    
    def test_execution_state_creation(self, batch_processor, basic_context):
        """Test execution state creation"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[],
                confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={},
                missing_parameters=[],
                suggestions=[]
            )
        ]
        
        execution_state = batch_processor._create_execution_state(parsed_commands, basic_context)
        
        assert isinstance(execution_state, BatchExecutionState)
        assert len(execution_state.executions) == 1
        assert execution_state.context == basic_context
        assert execution_state.start_time is not None
    
    def test_dependency_analysis(self, batch_processor):
        """Test dependency analysis"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="move", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        ]
        
        execution_state = batch_processor._create_execution_state(parsed_commands, basic_context)
        batch_processor._analyze_dependencies(execution_state)
        
        # Check that dependencies were identified
        executions = execution_state.executions
        
        # Connect should have no dependencies
        assert len(executions[0].dependencies) == 0
        
        # Takeoff should depend on connect
        assert 0 in executions[1].dependencies or len(executions[1].dependencies) == 0  # May depend on rules
        
        # Move should depend on takeoff
        assert len(executions[2].dependencies) > 0  # Should have dependencies
    
    def test_execution_plan_creation_sequential(self, batch_processor):
        """Test execution plan creation in sequential mode"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        ]
        
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.STOP_ON_ERROR
        )
        
        execution_state = batch_processor._create_execution_state(parsed_commands, context)
        batch_processor._create_execution_plan(execution_state)
        
        # Sequential mode should create individual groups
        assert len(execution_state.execution_groups) == len(parsed_commands)
        assert all(len(group) == 1 for group in execution_state.execution_groups)
    
    def test_execution_plan_creation_parallel(self, batch_processor):
        """Test execution plan creation in parallel mode"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "BB"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        ]
        
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.PARALLEL,
            error_recovery=ErrorRecoveryStrategy.CONTINUE_ON_ERROR,
            max_parallel_commands=2
        )
        
        execution_state = batch_processor._create_execution_state(parsed_commands, context)
        batch_processor._create_execution_plan(execution_state)
        
        # Parallel mode should group commands together
        assert len(execution_state.execution_groups) >= 1
    
    def test_optimized_execution_plan(self, batch_processor):
        """Test optimized execution plan creation"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="takeoff", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "BB"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        ]
        
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.OPTIMIZED,
            error_recovery=ErrorRecoveryStrategy.SMART_RECOVERY
        )
        
        execution_state = batch_processor._create_execution_state(parsed_commands, context)
        batch_processor._analyze_dependencies(execution_state)
        batch_processor._create_execution_plan(execution_state)
        
        # Optimized mode should create efficient execution groups
        assert len(execution_state.execution_groups) > 0
        assert execution_state.total_estimated_time > 0
    
    def test_priority_based_execution_plan(self, batch_processor):
        """Test priority-based execution plan creation"""
        parsed_commands = [
            ParsedCommand(
                primary_intent=ParsedIntent(action="emergency", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            ),
            ParsedCommand(
                primary_intent=ParsedIntent(action="photo", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        ]
        
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.PRIORITY_BASED,
            error_recovery=ErrorRecoveryStrategy.CONTINUE_ON_ERROR
        )
        
        execution_state = batch_processor._create_execution_state(parsed_commands, context)
        batch_processor._create_execution_plan(execution_state)
        
        # Priority-based mode should organize by command priority
        assert len(execution_state.execution_groups) > 0
    
    def test_command_conflict_detection(self, batch_processor):
        """Test command conflict detection"""
        exec1 = CommandExecution(
            command_index=0,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="move", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        exec2 = CommandExecution(
            command_index=1,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="emergency", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        # These commands should conflict
        has_conflict = batch_processor._commands_conflict(exec1, exec2)
        assert has_conflict is True
        
        # Different drones should not conflict
        exec3 = CommandExecution(
            command_index=2,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="move", parameters={"drone_id": "BB"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        has_conflict_diff_drone = batch_processor._commands_conflict(exec1, exec3)
        assert has_conflict_diff_drone is False
    
    def test_priority_score_calculation(self, batch_processor):
        """Test command priority score calculation"""
        exec_emergency = CommandExecution(
            command_index=0,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="emergency", parameters={}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        exec_normal = CommandExecution(
            command_index=1,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="move", parameters={}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        emergency_score = batch_processor._get_command_priority_score(exec_emergency)
        normal_score = batch_processor._get_command_priority_score(exec_normal)
        
        # Emergency should have higher priority score
        assert emergency_score > normal_score
    
    def test_execution_time_calculation(self, batch_processor):
        """Test execution time calculation"""
        execution_state = Mock()
        execution_state.execution_groups = [
            [0],  # Single command
            [1, 2]  # Parallel commands
        ]
        
        execution_state.executions = [
            Mock(parsed_command=Mock(primary_intent=Mock(action="connect"))),
            Mock(parsed_command=Mock(primary_intent=Mock(action="takeoff"))),
            Mock(parsed_command=Mock(primary_intent=Mock(action="move")))
        ]
        
        total_time = batch_processor._calculate_estimated_time(execution_state)
        
        assert total_time > 0
        # Should be connect_time + max(takeoff_time, move_time)
        expected_time = 2.0 + max(5.0, 3.0)  # connect + max(takeoff, move)
        assert abs(total_time - expected_time) < 0.1
    
    @pytest.mark.asyncio
    async def test_single_command_execution(self, batch_processor):
        """Test single command execution"""
        execution = CommandExecution(
            command_index=0,
            parsed_command=ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        )
        
        execution_state = Mock()
        execution_state.context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.CONTINUE_ON_ERROR,
            max_retries=1,
            timeout_per_command=10.0
        )
        execution_state.executions = [execution]
        
        result = await batch_processor._execute_single_command(execution_state, 0)
        
        assert isinstance(result, CommandResponse)
        assert execution.status in ["completed", "failed"]
        assert execution.start_time is not None
        assert execution.end_time is not None
    
    @pytest.mark.asyncio
    async def test_error_recovery_strategies(self, batch_processor, sample_commands):
        """Test different error recovery strategies"""
        # Test stop on error
        context_stop = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.STOP_ON_ERROR
        )
        
        # Mock command router to fail on second command
        batch_processor.command_router.execute_enhanced_command = AsyncMock()
        responses = [
            CommandResponse(success=True, message="Success", timestamp=datetime.now()),
            CommandResponse(success=False, message="Error", timestamp=datetime.now()),
            CommandResponse(success=True, message="Success", timestamp=datetime.now())
        ]
        batch_processor.command_router.execute_enhanced_command.side_effect = responses
        
        response = await batch_processor.process_batch(sample_commands[:3], context_stop)
        
        # Should stop after first error
        assert response.summary.failed_commands > 0
        # Some commands should be skipped
        skipped_count = sum(1 for result in response.results 
                          if result and "skipped" in result.message)
        assert skipped_count > 0 or response.summary.failed_commands > 0
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, batch_processor):
        """Test command timeout handling"""
        # Mock command router to hang
        async def hanging_command(parsed_command):
            await asyncio.sleep(5)  # Longer than timeout
            return CommandResponse(success=True, message="Should not reach here", timestamp=datetime.now())
        
        batch_processor.command_router.execute_enhanced_command = AsyncMock(side_effect=hanging_command)
        
        commands = [NaturalLanguageCommand(command="ドローンAAに接続")]
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.CONTINUE_ON_ERROR,
            timeout_per_command=0.1  # Very short timeout
        )
        
        response = await batch_processor.process_batch(commands, context)
        
        # Should handle timeout gracefully
        assert len(response.results) == 1
        assert not response.results[0].success
        assert "timed out" in response.results[0].message.lower()
    
    def test_execution_analytics_generation(self, batch_processor):
        """Test execution analytics generation"""
        execution_state = Mock()
        execution_state.executions = [
            Mock(status="completed", start_time=datetime.now(), end_time=datetime.now(), attempts=1,
                 parsed_command=Mock(primary_intent=Mock(parameters={"drone_id": "AA"}))),
            Mock(status="failed", start_time=datetime.now(), end_time=datetime.now(), attempts=2,
                 parsed_command=Mock(primary_intent=Mock(parameters={"drone_id": "AA"}))),
            Mock(status="completed", start_time=datetime.now(), end_time=datetime.now(), attempts=1,
                 parsed_command=Mock(primary_intent=Mock(parameters={"drone_id": "BB"})))
        ]
        
        analytics = batch_processor._generate_execution_analytics(execution_state, 10.0)
        
        assert "status_distribution" in analytics
        assert "execution_times" in analytics
        assert "retry_analysis" in analytics
        assert "resource_utilization" in analytics
        assert "dependency_stats" in analytics
        
        assert analytics["status_distribution"]["completed"] == 2
        assert analytics["status_distribution"]["failed"] == 1
    
    def test_parallelization_factor_calculation(self, batch_processor):
        """Test parallelization factor calculation"""
        execution_state = Mock()
        execution_state.executions = [Mock() for _ in range(4)]
        execution_state.execution_groups = [
            [0, 1],  # 2 parallel
            [2],     # 1 sequential
            [3]      # 1 sequential
        ]
        
        factor = batch_processor._calculate_parallelization_factor(execution_state)
        
        assert 0 <= factor <= 1
        # 2 out of 4 commands were parallelized
        expected_factor = 2 / 4
        assert abs(factor - expected_factor) < 0.1
    
    @pytest.mark.asyncio
    async def test_parsing_error_handling(self, batch_processor):
        """Test handling of command parsing errors"""
        # Mock NLP engine to raise error on second command
        def mock_parse_with_error(command, context=None):
            if "エラー" in command:
                raise ValueError("Parsing failed")
            
            return ParsedCommand(
                primary_intent=ParsedIntent(action="connect", parameters={"drone_id": "AA"}, confidence=0.8),
                alternative_intents=[], confidence_level=ConfidenceLevel.HIGH,
                parameter_confidence={}, missing_parameters=[], suggestions=[]
            )
        
        batch_processor.nlp_engine.parse_command = Mock(side_effect=mock_parse_with_error)
        
        commands = [
            NaturalLanguageCommand(command="接続"),
            NaturalLanguageCommand(command="エラーコマンド"),
            NaturalLanguageCommand(command="写真")
        ]
        
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.CONTINUE_ON_ERROR
        )
        
        response = await batch_processor.process_batch(commands, context)
        
        # Should handle parsing error gracefully
        assert len(response.results) == 3
        assert not response.results[1].success  # Second command should fail
        assert "Parsing error" in response.results[1].message
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, batch_processor):
        """Test retry mechanism"""
        # Mock command router to fail twice then succeed
        responses = [
            CommandResponse(success=False, message="Temporary error", timestamp=datetime.now()),
            CommandResponse(success=False, message="Temporary error", timestamp=datetime.now()),
            CommandResponse(success=True, message="Success", timestamp=datetime.now())
        ]
        batch_processor.command_router.execute_enhanced_command = AsyncMock(side_effect=responses)
        
        commands = [NaturalLanguageCommand(command="接続")]
        context = BatchExecutionContext(
            execution_mode=BatchExecutionMode.SEQUENTIAL,
            error_recovery=ErrorRecoveryStrategy.RETRY_AND_CONTINUE,
            max_retries=2,
            retry_delay=0.01  # Short delay for testing
        )
        
        response = await batch_processor.process_batch(commands, context)
        
        # Should succeed after retries
        assert len(response.results) == 1
        assert response.results[0].success
    
    def test_dependency_rules_configuration(self, batch_processor):
        """Test dependency rules configuration"""
        rules = batch_processor.dependency_rules
        
        # Check that basic dependency rules exist
        assert "takeoff" in rules
        assert "requires" in rules["takeoff"]
        assert "connect" in rules["takeoff"]["requires"]
        
        assert "move" in rules
        assert "conflicts" in rules["move"]
        assert "emergency" in rules["move"]["conflicts"]
    
    @pytest.mark.asyncio
    async def test_execution_state_updates(self, batch_processor, sample_commands, basic_context):
        """Test execution state updates during processing"""
        response = await batch_processor.process_batch(sample_commands, basic_context)
        
        # Verify response structure
        assert "execution_analytics" in response.result
        assert "optimization_details" in response.result
        
        optimization = response.result["optimization_details"]
        assert "mode" in optimization
        assert "efficiency_ratio" in optimization
        assert "parallelization_factor" in optimization
        assert optimization["mode"] == basic_context.execution_mode.value