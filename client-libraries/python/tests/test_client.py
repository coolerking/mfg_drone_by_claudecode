"""
Tests for MCP Drone Client SDK
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from mcp_drone_client import MCPClient, MCPClientError, create_client
from mcp_drone_client.models import (
    MCPClientConfig,
    NaturalLanguageCommand,
    BatchCommand,
    CommandResponse,
    BatchCommandResponse,
    DroneListResponse,
    DroneStatusResponse,
    TakeoffCommand,
    MoveCommand,
    RotateCommand,
    AltitudeCommand,
    PhotoCommand,
    StreamingCommand,
    LearningDataCommand,
    DetectionCommand,
    TrackingCommand,
    OperationResponse,
    PhotoResponse,
    LearningDataResponse,
    DetectionResponse,
    SystemStatusResponse,
    HealthResponse,
)


@pytest.fixture
def client_config():
    """Client configuration fixture"""
    return MCPClientConfig(
        base_url="http://localhost:8001",
        api_key="test-api-key",
        timeout=30.0,
    )


@pytest.fixture
async def client(client_config):
    """Client fixture"""
    client = MCPClient(client_config)
    yield client
    await client.close()


class TestMCPClient:
    """Test MCP Client"""
    
    def test_create_client_convenience_function(self):
        """Test create_client convenience function"""
        client = create_client(
            base_url="http://localhost:8001",
            api_key="test-key",
            timeout=60.0,
        )
        
        assert isinstance(client, MCPClient)
        assert client.config.base_url == "http://localhost:8001"
        assert client.config.api_key == "test-key"
        assert client.config.timeout == 60.0
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, client_config):
        """Test async context manager"""
        async with MCPClient(client_config) as client:
            assert isinstance(client, MCPClient)
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self, client):
        """Test execute command success"""
        mock_response = {
            "success": True,
            "message": "Command executed successfully",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            command = NaturalLanguageCommand(command="ドローンAAに接続して")
            result = await client.execute_command(command)
            
            assert isinstance(result, CommandResponse)
            assert result.success is True
            assert result.message == "Command executed successfully"
            mock_request.assert_called_once_with("POST", "/mcp/command", json=command.dict())
    
    @pytest.mark.asyncio
    async def test_execute_batch_command_success(self, client):
        """Test execute batch command success"""
        mock_response = {
            "success": True,
            "message": "Batch command executed successfully",
            "results": [],
            "summary": {
                "total_commands": 2,
                "successful_commands": 2,
                "failed_commands": 0,
                "total_execution_time": 1.5,
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            batch_command = BatchCommand(
                commands=[
                    NaturalLanguageCommand(command="ドローンAAに接続して"),
                    NaturalLanguageCommand(command="離陸して"),
                ]
            )
            result = await client.execute_batch_command(batch_command)
            
            assert isinstance(result, BatchCommandResponse)
            assert result.success is True
            assert result.summary["total_commands"] == 2
            mock_request.assert_called_once_with("POST", "/mcp/command/batch", json=batch_command.dict())
    
    @pytest.mark.asyncio
    async def test_get_drones_success(self, client):
        """Test get drones success"""
        mock_response = {
            "drones": [
                {
                    "id": "drone_001",
                    "name": "Test Drone",
                    "type": "real",
                    "status": "available",
                    "capabilities": ["camera", "movement"],
                }
            ],
            "count": 1,
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_drones()
            
            assert isinstance(result, DroneListResponse)
            assert result.count == 1
            assert len(result.drones) == 1
            assert result.drones[0].id == "drone_001"
            mock_request.assert_called_once_with("GET", "/mcp/drones")
    
    @pytest.mark.asyncio
    async def test_get_available_drones_success(self, client):
        """Test get available drones success"""
        mock_response = {
            "drones": [],
            "count": 0,
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_available_drones()
            
            assert isinstance(result, DroneListResponse)
            assert result.count == 0
            mock_request.assert_called_once_with("GET", "/mcp/drones/available")
    
    @pytest.mark.asyncio
    async def test_get_drone_status_success(self, client):
        """Test get drone status success"""
        mock_response = {
            "drone_id": "drone_001",
            "status": {
                "connection_status": "connected",
                "flight_status": "landed",
                "battery_level": 85,
                "height": 0,
                "temperature": 25.5,
                "wifi_signal": 90,
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_drone_status("drone_001")
            
            assert isinstance(result, DroneStatusResponse)
            assert result.drone_id == "drone_001"
            assert result.status["connection_status"] == "connected"
            mock_request.assert_called_once_with("GET", "/mcp/drones/drone_001/status")
    
    @pytest.mark.asyncio
    async def test_connect_drone_success(self, client):
        """Test connect drone success"""
        mock_response = {
            "success": True,
            "message": "Drone connected successfully",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.connect_drone("drone_001")
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            assert result.message == "Drone connected successfully"
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/connect")
    
    @pytest.mark.asyncio
    async def test_takeoff_success(self, client):
        """Test takeoff success"""
        mock_response = {
            "success": True,
            "message": "Drone takeoff successful",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            takeoff_command = TakeoffCommand(target_height=100, safety_check=True)
            result = await client.takeoff("drone_001", takeoff_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/takeoff", json=takeoff_command.dict())
    
    @pytest.mark.asyncio
    async def test_move_drone_success(self, client):
        """Test move drone success"""
        mock_response = {
            "success": True,
            "message": "Drone moved successfully",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            move_command = MoveCommand(direction="forward", distance=100, speed=50)
            result = await client.move_drone("drone_001", move_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/move", json=move_command.dict())
    
    @pytest.mark.asyncio
    async def test_rotate_drone_success(self, client):
        """Test rotate drone success"""
        mock_response = {
            "success": True,
            "message": "Drone rotated successfully",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            rotate_command = RotateCommand(direction="clockwise", angle=90)
            result = await client.rotate_drone("drone_001", rotate_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/rotate", json=rotate_command.dict())
    
    @pytest.mark.asyncio
    async def test_emergency_stop_success(self, client):
        """Test emergency stop success"""
        mock_response = {
            "success": True,
            "message": "Emergency stop executed",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.emergency_stop("drone_001")
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/emergency")
    
    @pytest.mark.asyncio
    async def test_set_altitude_success(self, client):
        """Test set altitude success"""
        mock_response = {
            "success": True,
            "message": "Altitude set successfully",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            altitude_command = AltitudeCommand(target_height=150, mode="absolute")
            result = await client.set_altitude("drone_001", altitude_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/altitude", json=altitude_command.dict())
    
    @pytest.mark.asyncio
    async def test_take_photo_success(self, client):
        """Test take photo success"""
        mock_response = {
            "success": True,
            "message": "Photo taken successfully",
            "photo": {
                "id": "photo_001",
                "filename": "photo.jpg",
                "path": "/photos/photo.jpg",
                "size": 1024,
                "timestamp": datetime.now().isoformat(),
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            photo_command = PhotoCommand(filename="test.jpg", quality="high")
            result = await client.take_photo("drone_001", photo_command)
            
            assert isinstance(result, PhotoResponse)
            assert result.success is True
            assert result.photo["filename"] == "photo.jpg"
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/camera/photo", json=photo_command.dict())
    
    @pytest.mark.asyncio
    async def test_control_streaming_success(self, client):
        """Test control streaming success"""
        mock_response = {
            "success": True,
            "message": "Streaming started",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            streaming_command = StreamingCommand(action="start", quality="high", resolution="720p")
            result = await client.control_streaming("drone_001", streaming_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/camera/streaming", json=streaming_command.dict())
    
    @pytest.mark.asyncio
    async def test_collect_learning_data_success(self, client):
        """Test collect learning data success"""
        mock_response = {
            "success": True,
            "message": "Learning data collected",
            "dataset": {
                "id": "dataset_001",
                "name": "test_object",
                "image_count": 12,
                "positions_captured": ["front", "back", "left", "right"],
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            learning_command = LearningDataCommand(
                object_name="test_object",
                capture_positions=["front", "back", "left", "right"],
                photos_per_position=3,
            )
            result = await client.collect_learning_data("drone_001", learning_command)
            
            assert isinstance(result, LearningDataResponse)
            assert result.success is True
            assert result.dataset["name"] == "test_object"
            mock_request.assert_called_once_with("POST", "/mcp/drones/drone_001/learning/collect", json=learning_command.dict())
    
    @pytest.mark.asyncio
    async def test_detect_objects_success(self, client):
        """Test detect objects success"""
        mock_response = {
            "success": True,
            "message": "Objects detected",
            "detections": [
                {
                    "label": "person",
                    "confidence": 0.95,
                    "bbox": {"x": 100, "y": 100, "width": 50, "height": 100},
                }
            ],
            "processing_time": 0.5,
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            detection_command = DetectionCommand(
                drone_id="drone_001",
                model_id="yolo_v8",
                confidence_threshold=0.7,
            )
            result = await client.detect_objects(detection_command)
            
            assert isinstance(result, DetectionResponse)
            assert result.success is True
            assert len(result.detections) == 1
            mock_request.assert_called_once_with("POST", "/mcp/vision/detection", json=detection_command.dict())
    
    @pytest.mark.asyncio
    async def test_control_tracking_success(self, client):
        """Test control tracking success"""
        mock_response = {
            "success": True,
            "message": "Tracking started",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            tracking_command = TrackingCommand(
                action="start",
                drone_id="drone_001",
                model_id="yolo_v8",
                follow_distance=200,
            )
            result = await client.control_tracking(tracking_command)
            
            assert isinstance(result, OperationResponse)
            assert result.success is True
            mock_request.assert_called_once_with("POST", "/mcp/vision/tracking", json=tracking_command.dict())
    
    @pytest.mark.asyncio
    async def test_get_system_status_success(self, client):
        """Test get system status success"""
        mock_response = {
            "mcp_server": {
                "status": "running",
                "uptime": 3600,
                "version": "1.0.0",
                "active_connections": 1,
            },
            "backend_system": {
                "connection_status": "connected",
                "api_endpoint": "http://backend:8000",
                "response_time": 50,
            },
            "connected_drones": 1,
            "active_operations": 0,
            "system_health": "healthy",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_system_status()
            
            assert isinstance(result, SystemStatusResponse)
            assert result.system_health == "healthy"
            assert result.connected_drones == 1
            mock_request.assert_called_once_with("GET", "/mcp/system/status")
    
    @pytest.mark.asyncio
    async def test_get_health_check_success(self, client):
        """Test get health check success"""
        mock_response = {
            "status": "healthy",
            "checks": [
                {
                    "name": "database",
                    "status": "pass",
                    "message": "Database connection healthy",
                    "response_time": 10,
                }
            ],
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_health_check()
            
            assert isinstance(result, HealthResponse)
            assert result.status == "healthy"
            assert len(result.checks) == 1
            mock_request.assert_called_once_with("GET", "/mcp/system/health")
    
    @pytest.mark.asyncio
    async def test_ping_success(self, client):
        """Test ping success"""
        with patch.object(client, "get_health_check", return_value=Mock()) as mock_health:
            result = await client.ping()
            
            assert result is True
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, client):
        """Test ping failure"""
        with patch.object(client, "get_health_check", side_effect=Exception("Network error")) as mock_health:
            result = await client.ping()
            
            assert result is False
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self, client):
        """Test client error handling"""
        error_response = {
            "error": True,
            "error_code": "DRONE_NOT_FOUND",
            "message": "Drone not found",
            "timestamp": datetime.now().isoformat(),
        }
        
        with patch.object(client, "_request", side_effect=MCPClientError(error_response)):
            with pytest.raises(MCPClientError) as exc_info:
                await client.get_drone_status("invalid_drone")
            
            assert exc_info.value.error_code == "DRONE_NOT_FOUND"
            assert exc_info.value.message == "Drone not found"


class TestMCPClientError:
    """Test MCP Client Error"""
    
    def test_mcp_client_error_creation(self):
        """Test MCP client error creation"""
        error_data = {
            "error": True,
            "error_code": "DRONE_NOT_FOUND",
            "message": "Drone not found",
            "details": {"suggested_corrections": ["Check drone ID"]},
            "timestamp": datetime.now().isoformat(),
        }
        
        error = MCPClientError(error_data)
        
        assert error.error_code == "DRONE_NOT_FOUND"
        assert error.message == "Drone not found"
        assert error.details == {"suggested_corrections": ["Check drone ID"]}
        assert str(error) == "Drone not found"
    
    def test_mcp_client_error_minimal(self):
        """Test MCP client error with minimal data"""
        error_data = {}
        
        error = MCPClientError(error_data)
        
        assert error.error_code == "UNKNOWN_ERROR"
        assert error.message == "Unknown error"
        assert error.details is None
        assert str(error) == "Unknown error"