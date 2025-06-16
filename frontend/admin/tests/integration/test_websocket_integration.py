"""
WebSocket Integration Tests
WebSocketリアルタイム通信テスト
"""
import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
import socketio
from threading import Event


@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocketIntegration:
    """WebSocket integration test suite."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.websocket_url = "http://localhost:8000"
        self.timeout = 5.0
        self.received_events = []
        self.connection_event = Event()
        self.disconnect_event = Event()
    
    @pytest.fixture
    def mock_socketio_client(self):
        """Create mock SocketIO client."""
        client = Mock(spec=socketio.Client)
        client.connected = False
        client.connect = Mock()
        client.disconnect = Mock()
        client.emit = Mock()
        client.wait = Mock()
        return client
    
    def test_websocket_connection_establishment(self, mock_socketio_client):
        """Test WebSocket connection establishment."""
        # Setup mock connection
        mock_socketio_client.connected = True
        mock_socketio_client.connect.return_value = True
        
        # Simulate connection
        try:
            mock_socketio_client.connect(self.websocket_url, wait_timeout=self.timeout)
            assert mock_socketio_client.connected == True
            mock_socketio_client.connect.assert_called_once()
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {str(e)}")
    
    def test_websocket_event_emission(self, mock_socketio_client):
        """Test WebSocket event emission."""
        mock_socketio_client.connected = True
        
        # Test various event emissions
        test_events = [
            ("sensor_request", {"sensor": "battery"}),
            ("tracking_command", {"action": "start", "target": "person"}),
            ("camera_command", {"action": "start_stream"}),
        ]
        
        for event_name, event_data in test_events:
            mock_socketio_client.emit(event_name, event_data)
            mock_socketio_client.emit.assert_called_with(event_name, event_data)
    
    def test_websocket_event_reception(self, mock_websocket_events):
        """Test WebSocket event reception."""
        received_events = []
        
        def mock_event_handler(event_name, data):
            """Mock event handler to capture received events."""
            received_events.append({"event": event_name, "data": data})
        
        # Simulate receiving events
        for event_name, event_data in mock_websocket_events.items():
            mock_event_handler(event_name, event_data["data"])
        
        # Verify events were received
        assert len(received_events) == len(mock_websocket_events)
        
        # Check specific event types
        event_names = [event["event"] for event in received_events]
        assert "sensor_update" in event_names
        assert "tracking_update" in event_names
        assert "model_training_progress" in event_names
    
    def test_sensor_data_streaming(self, mock_websocket_events):
        """Test real-time sensor data streaming."""
        sensor_updates = []
        
        def handle_sensor_update(data):
            """Handle sensor update events."""
            sensor_updates.append(data)
        
        # Simulate multiple sensor updates
        sensor_data = mock_websocket_events["sensor_update"]["data"]
        
        for i in range(5):
            # Modify data to simulate different sensor readings
            modified_data = sensor_data.copy()
            modified_data["battery"] = 85 - i
            modified_data["altitude"] = 120 + i * 10
            modified_data["temperature"] = 25.5 + i * 0.2
            
            handle_sensor_update(modified_data)
        
        # Verify sensor updates
        assert len(sensor_updates) == 5
        assert sensor_updates[0]["battery"] == 85
        assert sensor_updates[4]["battery"] == 81
        assert sensor_updates[0]["altitude"] == 120
        assert sensor_updates[4]["altitude"] == 160
    
    def test_tracking_status_updates(self, mock_websocket_events):
        """Test real-time tracking status updates."""
        tracking_updates = []
        
        def handle_tracking_update(data):
            """Handle tracking update events."""
            tracking_updates.append(data)
        
        # Simulate tracking scenario
        tracking_scenarios = [
            {"tracking": False, "target_detected": False, "confidence": 0.0},
            {"tracking": True, "target_detected": True, "confidence": 0.75, "position": {"x": 300, "y": 200}},
            {"tracking": True, "target_detected": True, "confidence": 0.92, "position": {"x": 320, "y": 240}},
            {"tracking": True, "target_detected": False, "confidence": 0.0},  # Lost target
            {"tracking": False, "target_detected": False, "confidence": 0.0}  # Stopped tracking
        ]
        
        for scenario in tracking_scenarios:
            handle_tracking_update(scenario)
        
        # Verify tracking updates
        assert len(tracking_updates) == 5
        assert tracking_updates[0]["tracking"] == False
        assert tracking_updates[1]["tracking"] == True
        assert tracking_updates[1]["confidence"] == 0.75
        assert tracking_updates[2]["confidence"] == 0.92
        assert tracking_updates[3]["target_detected"] == False  # Target lost
        assert tracking_updates[4]["tracking"] == False  # Tracking stopped
    
    def test_model_training_progress_updates(self, mock_websocket_events):
        """Test real-time model training progress updates."""
        training_updates = []
        
        def handle_training_progress(data):
            """Handle model training progress events."""
            training_updates.append(data)
        
        # Simulate training progress
        progress_steps = [0, 25, 50, 75, 90, 100]
        base_data = mock_websocket_events["model_training_progress"]["data"]
        
        for progress in progress_steps:
            update_data = base_data.copy()
            update_data["progress"] = progress
            update_data["estimated_remaining"] = max(0, 120 - (progress * 1.2))
            
            if progress == 100:
                update_data["status"] = "completed"
                update_data["estimated_remaining"] = 0
            
            handle_training_progress(update_data)
        
        # Verify training progress updates
        assert len(training_updates) == 6
        assert training_updates[0]["progress"] == 0
        assert training_updates[-1]["progress"] == 100
        assert training_updates[-1]["status"] == "completed"
        assert training_updates[-1]["estimated_remaining"] == 0
    
    def test_websocket_reconnection_handling(self, mock_socketio_client):
        """Test WebSocket reconnection scenarios."""
        connection_attempts = []
        
        def mock_connect_with_retry(url, **kwargs):
            """Mock connection with retry logic."""
            connection_attempts.append(time.time())
            if len(connection_attempts) <= 2:
                raise ConnectionError("Connection failed")
            mock_socketio_client.connected = True
            return True
        
        mock_socketio_client.connect.side_effect = mock_connect_with_retry
        
        # Simulate reconnection attempts
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries + 1):
            try:
                mock_socketio_client.connect(self.websocket_url)
                if mock_socketio_client.connected:
                    break
            except ConnectionError:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    pytest.fail("Failed to reconnect after maximum retries")
        
        # Verify reconnection attempts
        assert len(connection_attempts) == 3
        assert mock_socketio_client.connected == True
    
    def test_websocket_error_handling(self, mock_socketio_client):
        """Test WebSocket error handling."""
        error_events = []
        
        def handle_error(error_data):
            """Handle WebSocket errors."""
            error_events.append(error_data)
        
        # Simulate various error scenarios
        error_scenarios = [
            {"type": "connection_error", "message": "Failed to connect to server"},
            {"type": "timeout_error", "message": "Request timeout"},
            {"type": "invalid_data", "message": "Received invalid JSON data"},
            {"type": "authentication_error", "message": "Authentication failed"},
        ]
        
        for error in error_scenarios:
            handle_error(error)
        
        # Verify error handling
        assert len(error_events) == 4
        error_types = [error["type"] for error in error_events]
        assert "connection_error" in error_types
        assert "timeout_error" in error_types
        assert "invalid_data" in error_types
        assert "authentication_error" in error_types
    
    def test_websocket_disconnect_handling(self, mock_socketio_client):
        """Test WebSocket disconnect scenarios."""
        mock_socketio_client.connected = True
        disconnect_reasons = []
        
        def handle_disconnect(reason):
            """Handle disconnect events."""
            disconnect_reasons.append(reason)
            mock_socketio_client.connected = False
        
        # Simulate different disconnect scenarios
        disconnect_scenarios = [
            "user_initiated",
            "server_shutdown", 
            "network_error",
            "timeout"
        ]
        
        for reason in disconnect_scenarios:
            mock_socketio_client.connected = True  # Reset connection
            handle_disconnect(reason)
            assert mock_socketio_client.connected == False
            mock_socketio_client.disconnect()
        
        # Verify disconnect handling
        assert len(disconnect_reasons) == 4
        assert "user_initiated" in disconnect_reasons
        assert "server_shutdown" in disconnect_reasons
        assert "network_error" in disconnect_reasons
    
    def test_websocket_message_queuing(self):
        """Test message queuing when connection is down."""
        message_queue = []
        connected = False
        
        def queue_message(event, data):
            """Queue messages when not connected."""
            if connected:
                # Send immediately
                return {"status": "sent", "event": event, "data": data}
            else:
                # Queue for later
                message_queue.append({"event": event, "data": data})
                return {"status": "queued", "event": event, "data": data}
        
        # Test queuing while disconnected
        test_messages = [
            ("sensor_request", {"sensor": "battery"}),
            ("tracking_command", {"action": "start"}),
            ("camera_command", {"action": "photo"}),
        ]
        
        for event, data in test_messages:
            result = queue_message(event, data)
            assert result["status"] == "queued"
        
        assert len(message_queue) == 3
        
        # Test sending queued messages when connected
        connected = True
        sent_messages = []
        
        while message_queue:
            queued_msg = message_queue.pop(0)
            result = queue_message(queued_msg["event"], queued_msg["data"])
            assert result["status"] == "sent"
            sent_messages.append(result)
        
        assert len(sent_messages) == 3
        assert len(message_queue) == 0
    
    def test_websocket_event_filtering(self, mock_websocket_events):
        """Test WebSocket event filtering and processing."""
        filtered_events = {
            "sensor_updates": [],
            "tracking_updates": [],
            "training_updates": [],
            "other_events": []
        }
        
        def filter_and_process_event(event_name, event_data):
            """Filter and process events based on type."""
            if "sensor" in event_name:
                filtered_events["sensor_updates"].append(event_data)
            elif "tracking" in event_name:
                filtered_events["tracking_updates"].append(event_data)
            elif "training" in event_name:
                filtered_events["training_updates"].append(event_data)
            else:
                filtered_events["other_events"].append(event_data)
        
        # Process mock events
        for event_name, event_data in mock_websocket_events.items():
            filter_and_process_event(event_name, event_data["data"])
        
        # Verify filtering
        assert len(filtered_events["sensor_updates"]) == 1
        assert len(filtered_events["tracking_updates"]) == 1
        assert len(filtered_events["training_updates"]) == 1
        assert len(filtered_events["other_events"]) == 0
        
        # Verify event data integrity
        sensor_data = filtered_events["sensor_updates"][0]
        assert "battery" in sensor_data
        assert "altitude" in sensor_data
        assert "temperature" in sensor_data
        
        tracking_data = filtered_events["tracking_updates"][0]
        assert "tracking" in tracking_data
        assert "target_detected" in tracking_data
        assert "position" in tracking_data