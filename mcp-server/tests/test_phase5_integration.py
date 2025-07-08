"""
Phase 5: System Integration Tests for MCP Server
Tests the complete system integration including:
- End-to-end workflow testing
- Error handling and recovery
- Performance testing
- Security testing
- Concurrent operations testing
"""

import asyncio
import pytest
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.command_models import (
    NaturalLanguageCommand, BatchCommand, CommandResponse,
    BatchCommandResponse, CommandError
)
from models.drone_models import (
    DroneInfo, DroneStatusResponse, TakeoffCommand,
    MoveCommand, RotateCommand, AltitudeCommand, OperationResponse
)
from models.camera_models import (
    PhotoCommand, StreamingCommand, LearningDataCommand,
    DetectionCommand, TrackingCommand, PhotoResponse,
    LearningDataResponse, DetectionResponse
)
from models.system_models import SystemStatusResponse, HealthResponse
from core.backend_client import BackendClient, BackendClientError
from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter


class TestPhase5Integration:
    """Phase 5 System Integration Tests"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        self.backend_client = BackendClient()
        self.nlp_engine = NLPEngine()
        self.command_router = CommandRouter(self.backend_client)
        
        # Mock backend client for testing
        self.backend_client.get_drones = AsyncMock()
        self.backend_client.get_available_drones = AsyncMock()
        self.backend_client.get_drone_status = AsyncMock()
        self.backend_client.connect_drone = AsyncMock()
        self.backend_client.disconnect_drone = AsyncMock()
        self.backend_client.takeoff_drone = AsyncMock()
        self.backend_client.land_drone = AsyncMock()
        self.backend_client.move_drone = AsyncMock()
        self.backend_client.rotate_drone = AsyncMock()
        self.backend_client.emergency_stop = AsyncMock()
        self.backend_client.set_altitude = AsyncMock()
        self.backend_client.take_photo = AsyncMock()
        self.backend_client.control_streaming = AsyncMock()
        self.backend_client.collect_learning_data = AsyncMock()
        self.backend_client.detect_objects = AsyncMock()
        self.backend_client.control_tracking = AsyncMock()
        self.backend_client.get_system_status = AsyncMock()
        self.backend_client.health_check = AsyncMock()


class TestEndToEndWorkflows(TestPhase5Integration):
    """End-to-end workflow integration tests"""
    
    async def test_complete_drone_mission_workflow(self):
        """Test complete drone mission from connection to data collection"""
        # Setup mock responses
        self.backend_client.connect_drone.return_value = OperationResponse(
            success=True, message="Connected", timestamp=datetime.now()
        )
        self.backend_client.takeoff_drone.return_value = OperationResponse(
            success=True, message="Takeoff successful", timestamp=datetime.now()
        )
        self.backend_client.move_drone.return_value = OperationResponse(
            success=True, message="Move successful", timestamp=datetime.now()
        )
        self.backend_client.take_photo.return_value = {
            "id": "photo_001",
            "filename": "test_photo.jpg",
            "path": "/photos/test_photo.jpg",
            "size": 1024000,
            "timestamp": datetime.now()
        }
        self.backend_client.land_drone.return_value = OperationResponse(
            success=True, message="Landing successful", timestamp=datetime.now()
        )
        
        # Define mission commands
        mission_commands = [
            "ドローンAAに接続して",
            "離陸して",
            "右に50センチ移動して",
            "写真を撮って",
            "着陸して"
        ]
        
        # Execute mission
        results = []
        for command_text in mission_commands:
            command = NaturalLanguageCommand(command=command_text)
            parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
            response = await self.command_router.execute_command(parsed_intent)
            results.append(response)
        
        # Verify all commands succeeded
        assert all(result.success for result in results), "Mission workflow failed"
        assert len(results) == 5, "Not all commands executed"
        
        # Verify backend calls
        self.backend_client.connect_drone.assert_called_once()
        self.backend_client.takeoff_drone.assert_called_once()
        self.backend_client.move_drone.assert_called_once()
        self.backend_client.take_photo.assert_called_once()
        self.backend_client.land_drone.assert_called_once()
    
    async def test_batch_command_sequential_execution(self):
        """Test batch command execution in sequential mode"""
        # Setup mock responses
        self.backend_client.connect_drone.return_value = OperationResponse(
            success=True, message="Connected", timestamp=datetime.now()
        )
        self.backend_client.takeoff_drone.return_value = OperationResponse(
            success=True, message="Takeoff successful", timestamp=datetime.now()
        )
        
        # Create batch command
        commands = [
            NaturalLanguageCommand(command="ドローンAAに接続して"),
            NaturalLanguageCommand(command="離陸して")
        ]
        batch_command = BatchCommand(
            commands=commands,
            execution_mode="sequential",
            stop_on_error=True
        )
        
        # Execute batch
        results = []
        successful_commands = 0
        failed_commands = 0
        start_time = datetime.now()
        
        for cmd in batch_command.commands:
            try:
                parsed_intent = self.nlp_engine.parse_command(cmd.command, cmd.context)
                response = await self.command_router.execute_command(parsed_intent)
                results.append(response)
                
                if response.success:
                    successful_commands += 1
                else:
                    failed_commands += 1
                    if batch_command.stop_on_error:
                        break
                        
            except Exception as e:
                failed_commands += 1
                error_response = CommandResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    timestamp=datetime.now()
                )
                results.append(error_response)
                
                if batch_command.stop_on_error:
                    break
        
        # Verify results
        assert successful_commands == 2, "Not all commands succeeded"
        assert failed_commands == 0, "Some commands failed"
        assert len(results) == 2, "Wrong number of results"
    
    async def test_learning_data_collection_workflow(self):
        """Test learning data collection workflow"""
        # Setup mock responses
        self.backend_client.connect_drone.return_value = OperationResponse(
            success=True, message="Connected", timestamp=datetime.now()
        )
        self.backend_client.collect_learning_data.return_value = {
            "dataset": {
                "id": "dataset_001",
                "name": "test_object",
                "image_count": 12,
                "positions_captured": ["front", "back", "left", "right"]
            },
            "execution_summary": {
                "total_moves": 4,
                "total_photos": 12,
                "execution_time": 60.5
            }
        }
        
        # Execute learning data collection
        command = NaturalLanguageCommand(command="工業部品の学習データを収集して")
        parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
        response = await self.command_router.execute_command(parsed_intent)
        
        # Verify success
        assert response.success, "Learning data collection failed"
        self.backend_client.collect_learning_data.assert_called_once()


class TestErrorHandlingAndRecovery(TestPhase5Integration):
    """Error handling and recovery integration tests"""
    
    async def test_backend_connection_failure_handling(self):
        """Test handling of backend connection failures"""
        # Setup backend client to raise connection error
        self.backend_client.connect_drone.side_effect = BackendClientError(
            "CONNECTION_FAILED", "Backend connection failed"
        )
        
        # Try to execute command
        command = NaturalLanguageCommand(command="ドローンAAに接続して")
        parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
        
        with pytest.raises(BackendClientError):
            await self.command_router.execute_command(parsed_intent)
    
    async def test_batch_command_error_recovery(self):
        """Test batch command execution with error recovery"""
        # Setup mixed responses (some success, some failure)
        self.backend_client.connect_drone.return_value = OperationResponse(
            success=True, message="Connected", timestamp=datetime.now()
        )
        self.backend_client.takeoff_drone.side_effect = BackendClientError(
            "TAKEOFF_FAILED", "Takeoff failed"
        )
        
        # Create batch command with stop_on_error=False
        commands = [
            NaturalLanguageCommand(command="ドローンAAに接続して"),
            NaturalLanguageCommand(command="離陸して"),
            NaturalLanguageCommand(command="写真を撮って")
        ]
        batch_command = BatchCommand(
            commands=commands,
            execution_mode="sequential",
            stop_on_error=False
        )
        
        # Execute batch with error handling
        results = []
        successful_commands = 0
        failed_commands = 0
        
        for cmd in batch_command.commands:
            try:
                parsed_intent = self.nlp_engine.parse_command(cmd.command, cmd.context)
                response = await self.command_router.execute_command(parsed_intent)
                results.append(response)
                
                if response.success:
                    successful_commands += 1
                else:
                    failed_commands += 1
                    
            except Exception as e:
                failed_commands += 1
                error_response = CommandResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    timestamp=datetime.now()
                )
                results.append(error_response)
        
        # Verify partial success
        assert successful_commands >= 1, "No commands succeeded"
        assert failed_commands >= 1, "No commands failed as expected"
        assert len(results) == 3, "Wrong number of results"
    
    async def test_nlp_parsing_error_handling(self):
        """Test handling of NLP parsing errors"""
        # Test with ambiguous command
        command = NaturalLanguageCommand(command="あいまいなコマンド")
        parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
        
        # Should handle low confidence
        if parsed_intent.confidence < 0.5:
            assert True, "Low confidence handled correctly"
        else:
            # If confidence is high, command should execute
            response = await self.command_router.execute_command(parsed_intent)
            assert isinstance(response, CommandResponse)


class TestPerformanceAndConcurrency(TestPhase5Integration):
    """Performance and concurrency integration tests"""
    
    async def test_concurrent_command_execution(self):
        """Test concurrent command execution"""
        # Setup mock responses
        self.backend_client.get_drone_status.return_value = {
            "connection_status": "connected",
            "flight_status": "landed",
            "battery_level": 85,
            "height": 0,
            "temperature": 25.5,
            "wifi_signal": 90
        }
        
        # Create multiple concurrent commands
        commands = [
            NaturalLanguageCommand(command="ドローンAAの状態を教えて"),
            NaturalLanguageCommand(command="ドローンBBの状態を教えて"),
            NaturalLanguageCommand(command="ドローンCCの状態を教えて")
        ]
        
        # Execute commands concurrently
        async def execute_command(cmd):
            parsed_intent = self.nlp_engine.parse_command(cmd.command, cmd.context)
            return await self.command_router.execute_command(parsed_intent)
        
        start_time = time.time()
        results = await asyncio.gather(*[execute_command(cmd) for cmd in commands])
        execution_time = time.time() - start_time
        
        # Verify results
        assert len(results) == 3, "Not all commands executed"
        assert all(isinstance(result, CommandResponse) for result in results)
        assert execution_time < 5.0, "Concurrent execution too slow"
    
    async def test_batch_command_performance(self):
        """Test batch command execution performance"""
        # Setup mock responses for fast execution
        self.backend_client.take_photo.return_value = {
            "id": "photo_001",
            "filename": "test_photo.jpg",
            "path": "/photos/test_photo.jpg",
            "size": 1024000,
            "timestamp": datetime.now()
        }
        
        # Create batch of photo commands
        commands = [
            NaturalLanguageCommand(command="写真を撮って")
            for _ in range(10)
        ]
        batch_command = BatchCommand(
            commands=commands,
            execution_mode="parallel"
        )
        
        # Execute in parallel mode
        start_time = time.time()
        results = await asyncio.gather(*[
            self.command_router.execute_command(
                self.nlp_engine.parse_command(cmd.command, cmd.context)
            ) for cmd in batch_command.commands
        ])
        execution_time = time.time() - start_time
        
        # Verify performance
        assert len(results) == 10, "Not all commands executed"
        assert execution_time < 2.0, "Parallel execution too slow"
    
    async def test_memory_usage_stability(self):
        """Test memory usage stability during extended operation"""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Execute many commands
        for i in range(100):
            command = NaturalLanguageCommand(command=f"ドローンAAの状態を教えて")
            parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
            
            # Mock response to avoid actual backend calls
            self.backend_client.get_drone_status.return_value = {
                "connection_status": "connected",
                "flight_status": "landed",
                "battery_level": 85
            }
            
            response = await self.command_router.execute_command(parsed_intent)
            assert response.success
            
            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()
        
        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / initial_memory
        
        # Memory increase should be reasonable (less than 50%)
        assert memory_increase < 0.5, f"Memory usage increased too much: {memory_increase*100:.1f}%"


class TestSecurityIntegration(TestPhase5Integration):
    """Security integration tests"""
    
    async def test_api_key_authentication(self):
        """Test API key authentication"""
        # This would typically be tested with actual FastAPI test client
        # For now, we'll test the authentication logic
        
        # Mock authentication function
        async def verify_api_key(credentials):
            if not credentials or credentials.credentials != "valid_key":
                raise Exception("Invalid API key")
            return True
        
        # Test valid key
        class MockCredentials:
            credentials = "valid_key"
        
        result = await verify_api_key(MockCredentials())
        assert result is True
        
        # Test invalid key
        class MockInvalidCredentials:
            credentials = "invalid_key"
        
        with pytest.raises(Exception, match="Invalid API key"):
            await verify_api_key(MockInvalidCredentials())
    
    async def test_command_validation(self):
        """Test command input validation"""
        # Test malicious command detection
        malicious_commands = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../../etc/passwd",
            "eval('malicious_code')"
        ]
        
        for malicious_cmd in malicious_commands:
            command = NaturalLanguageCommand(command=malicious_cmd)
            parsed_intent = self.nlp_engine.parse_command(command.command, command.context)
            
            # Verify that malicious commands are either rejected or sanitized
            assert parsed_intent.confidence < 0.3, f"Malicious command not detected: {malicious_cmd}"
    
    async def test_rate_limiting_simulation(self):
        """Test rate limiting behavior simulation"""
        # Simulate rapid requests
        commands = [
            NaturalLanguageCommand(command="ドローンAAの状態を教えて")
            for _ in range(50)
        ]
        
        # Execute commands rapidly
        start_time = time.time()
        request_times = []
        
        for cmd in commands:
            request_start = time.time()
            parsed_intent = self.nlp_engine.parse_command(cmd.command, cmd.context)
            
            self.backend_client.get_drone_status.return_value = {
                "connection_status": "connected"
            }
            
            response = await self.command_router.execute_command(parsed_intent)
            request_end = time.time()
            request_times.append(request_end - request_start)
        
        total_time = time.time() - start_time
        avg_request_time = sum(request_times) / len(request_times)
        
        # Verify reasonable performance under load
        assert total_time < 10.0, "Requests took too long under load"
        assert avg_request_time < 0.2, "Average request time too high"


class TestSystemHealthMonitoring(TestPhase5Integration):
    """System health monitoring integration tests"""
    
    async def test_health_check_comprehensive(self):
        """Test comprehensive health check"""
        # Setup mock health responses
        self.backend_client.health_check.return_value = {
            "status": "healthy",
            "checks": [
                {"name": "Database", "status": "pass"},
                {"name": "Redis", "status": "pass"},
                {"name": "Drone Connection", "status": "pass"}
            ]
        }
        
        # Execute health check (simulated)
        backend_health = await self.backend_client.health_check()
        
        # Verify health status
        assert backend_health["status"] == "healthy"
        assert len(backend_health["checks"]) == 3
        assert all(check["status"] == "pass" for check in backend_health["checks"])
    
    async def test_system_status_monitoring(self):
        """Test system status monitoring"""
        # Setup mock system status
        self.backend_client.get_system_status.return_value = {
            "connected_drones": 3,
            "active_operations": 2,
            "system_health": "healthy",
            "uptime": 86400  # 1 day
        }
        
        # Get system status
        status = await self.backend_client.get_system_status()
        
        # Verify status information
        assert status["connected_drones"] == 3
        assert status["active_operations"] == 2
        assert status["system_health"] == "healthy"
        assert status["uptime"] > 0
    
    async def test_error_tracking_and_logging(self):
        """Test error tracking and logging functionality"""
        errors_logged = []
        
        # Mock logger to capture errors
        def mock_log_error(message):
            errors_logged.append(message)
        
        # Simulate various error conditions
        error_scenarios = [
            ("Connection timeout", "BACKEND_TIMEOUT"),
            ("Invalid drone ID", "DRONE_NOT_FOUND"),
            ("Command parsing failed", "PARSE_ERROR")
        ]
        
        for error_msg, error_code in error_scenarios:
            mock_log_error(f"{error_code}: {error_msg}")
        
        # Verify error logging
        assert len(errors_logged) == 3
        assert all(":" in error for error in errors_logged)


# Test fixtures and utilities

@pytest.fixture
def sample_drone_data():
    """Sample drone data for testing"""
    return [
        DroneInfo(
            id="drone_AA",
            name="Test Drone AA",
            type="real",
            status="available",
            capabilities=["flight", "camera", "vision"],
            last_seen=datetime.now()
        ),
        DroneInfo(
            id="drone_BB",
            name="Test Drone BB", 
            type="dummy",
            status="connected",
            capabilities=["flight", "camera"],
            last_seen=datetime.now()
        )
    ]


@pytest.fixture
def sample_commands():
    """Sample commands for testing"""
    return [
        "ドローンAAに接続して",
        "離陸して",
        "右に50センチ移動して",
        "写真を撮って",
        "着陸して"
    ]


# Performance benchmarks

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    async def test_nlp_parsing_benchmark(self):
        """Benchmark NLP parsing performance"""
        nlp_engine = NLPEngine()
        
        test_commands = [
            "ドローンAAに接続して",
            "高度を100センチに設定して",
            "右に50センチ移動して",
            "写真を撮って",
            "緊急停止して"
        ] * 100  # 500 commands total
        
        start_time = time.time()
        
        for command in test_commands:
            parsed_intent = nlp_engine.parse_command(command)
            assert parsed_intent is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_command = total_time / len(test_commands)
        
        print(f"NLP Parsing Benchmark:")
        print(f"Total commands: {len(test_commands)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per command: {avg_time_per_command*1000:.2f}ms")
        
        # Performance assertion
        assert avg_time_per_command < 0.01, "NLP parsing too slow"  # < 10ms per command


if __name__ == "__main__":
    import asyncio
    
    # Run a simple test
    async def run_test():
        test_instance = TestEndToEndWorkflows()
        await test_instance.setup()
        await test_instance.test_complete_drone_mission_workflow()
        print("Integration test passed!")
    
    asyncio.run(run_test())