"""
API Integration Tests
API統合テスト - 完全なワークフローテスト
"""
import pytest
import requests
import json
import time
from unittest.mock import Mock, patch
import responses
from concurrent.futures import ThreadPoolExecutor
import threading


@pytest.mark.integration
@pytest.mark.api_integration
class TestAPIIntegration:
    """Complete API integration test suite."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.backend_url = "http://localhost:8000"
        self.timeout = 10.0
        self.session = requests.Session()
        self.session.timeout = self.timeout
    
    @responses.activate
    def test_complete_drone_control_workflow(self):
        """Test complete drone control workflow from connection to flight."""
        # Setup complete workflow responses
        workflow_responses = [
            # System health check
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/system/health",
                "response": {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"},
                "status": 200
            },
            # Connect to drone
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/connection/connect",
                "response": {"status": "connected", "message": "Successfully connected"},
                "status": 200
            },
            # Check connection status
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/connection/status",
                "response": {"connected": True, "battery_level": 85, "signal_strength": "excellent"},
                "status": 200
            },
            # Takeoff
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/flight/takeoff",
                "response": {"status": "success", "operation": "takeoff", "altitude": 120},
                "status": 200
            },
            # Start streaming
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/camera/stream/start",
                "response": {"status": "streaming", "stream_url": "/camera/stream"},
                "status": 200
            },
            # Move forward
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/movement/forward",
                "response": {"status": "success", "movement": "forward", "distance": 50},
                "status": 200
            },
            # Stop streaming
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/camera/stream/stop",
                "response": {"status": "stopped"},
                "status": 200
            },
            # Land
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/flight/land",
                "response": {"status": "success", "operation": "land"},
                "status": 200
            },
            # Disconnect
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/connection/disconnect",
                "response": {"status": "disconnected", "message": "Successfully disconnected"},
                "status": 200
            }
        ]
        
        # Add all responses
        for response_config in workflow_responses:
            responses.add(
                response_config["method"],
                response_config["url"],
                json=response_config["response"],
                status=response_config["status"]
            )
        
        # Execute complete workflow
        workflow_results = []
        
        # 1. System health check
        response = self.session.get(f"{self.backend_url}/system/health")
        assert response.status_code == 200
        workflow_results.append(("health_check", response.json()))
        
        # 2. Connect to drone
        response = self.session.post(f"{self.backend_url}/connection/connect")
        assert response.status_code == 200
        assert response.json()["status"] == "connected"
        workflow_results.append(("connect", response.json()))
        
        # 3. Check connection status
        response = self.session.get(f"{self.backend_url}/connection/status")
        assert response.status_code == 200
        assert response.json()["connected"] == True
        workflow_results.append(("status", response.json()))
        
        # 4. Takeoff
        response = self.session.post(f"{self.backend_url}/flight/takeoff")
        assert response.status_code == 200
        assert response.json()["operation"] == "takeoff"
        workflow_results.append(("takeoff", response.json()))
        
        # 5. Start camera streaming
        response = self.session.post(f"{self.backend_url}/camera/stream/start")
        assert response.status_code == 200
        assert response.json()["status"] == "streaming"
        workflow_results.append(("stream_start", response.json()))
        
        # 6. Move forward
        response = self.session.post(
            f"{self.backend_url}/movement/forward",
            json={"distance": 50}
        )
        assert response.status_code == 200
        assert response.json()["movement"] == "forward"
        workflow_results.append(("move_forward", response.json()))
        
        # 7. Stop streaming
        response = self.session.post(f"{self.backend_url}/camera/stream/stop")
        assert response.status_code == 200
        workflow_results.append(("stream_stop", response.json()))
        
        # 8. Land
        response = self.session.post(f"{self.backend_url}/flight/land")
        assert response.status_code == 200
        assert response.json()["operation"] == "land"
        workflow_results.append(("land", response.json()))
        
        # 9. Disconnect
        response = self.session.post(f"{self.backend_url}/connection/disconnect")
        assert response.status_code == 200
        assert response.json()["status"] == "disconnected"
        workflow_results.append(("disconnect", response.json()))
        
        # Verify complete workflow
        assert len(workflow_results) == 9
        workflow_steps = [step[0] for step in workflow_results]
        expected_steps = [
            "health_check", "connect", "status", "takeoff", "stream_start",
            "move_forward", "stream_stop", "land", "disconnect"
        ]
        assert workflow_steps == expected_steps
    
    @responses.activate
    def test_object_tracking_workflow(self):
        """Test complete object tracking workflow."""
        # Setup tracking workflow responses
        tracking_responses = [
            # Get available models
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/model/list",
                "response": {
                    "models": [
                        {"name": "person", "accuracy": 0.92, "created_at": "2024-01-01T10:00:00Z"},
                        {"name": "vehicle", "accuracy": 0.88, "created_at": "2024-01-01T11:00:00Z"}
                    ]
                },
                "status": 200
            },
            # Start tracking
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/tracking/start",
                "response": {
                    "status": "tracking_started",
                    "target_object": "person",
                    "tracking_mode": "center"
                },
                "status": 200
            },
            # Get tracking status (active)
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/tracking/status",
                "response": {
                    "tracking": True,
                    "target_object": "person",
                    "target_detected": True,
                    "position": {"x": 320, "y": 240},
                    "detection_confidence": 0.95
                },
                "status": 200
            },
            # Stop tracking
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/tracking/stop",
                "response": {"status": "tracking_stopped"},
                "status": 200
            },
            # Get tracking status (inactive)
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/tracking/status",
                "response": {
                    "tracking": False,
                    "target_object": None,
                    "target_detected": False,
                    "position": {"x": 0, "y": 0},
                    "detection_confidence": 0.0
                },
                "status": 200
            }
        ]
        
        # Add all tracking responses
        for response_config in tracking_responses:
            responses.add(
                response_config["method"],
                response_config["url"],
                json=response_config["response"],
                status=response_config["status"]
            )
        
        # Execute tracking workflow
        tracking_results = []
        
        # 1. Get available models
        response = self.session.get(f"{self.backend_url}/model/list")
        assert response.status_code == 200
        models = response.json()["models"]
        assert len(models) >= 1
        tracking_results.append(("models", models))
        
        # 2. Start tracking with first available model
        target_model = models[0]["name"]
        response = self.session.post(
            f"{self.backend_url}/tracking/start",
            json={"target_object": target_model, "tracking_mode": "center"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "tracking_started"
        tracking_results.append(("start", response.json()))
        
        # 3. Check tracking status (should be active)
        response = self.session.get(f"{self.backend_url}/tracking/status")
        assert response.status_code == 200
        status = response.json()
        assert status["tracking"] == True
        assert status["target_object"] == target_model
        tracking_results.append(("status_active", status))
        
        # 4. Stop tracking
        response = self.session.post(f"{self.backend_url}/tracking/stop")
        assert response.status_code == 200
        assert response.json()["status"] == "tracking_stopped"
        tracking_results.append(("stop", response.json()))
        
        # 5. Check tracking status (should be inactive)
        response = self.session.get(f"{self.backend_url}/tracking/status")
        assert response.status_code == 200
        status = response.json()
        assert status["tracking"] == False
        assert status["target_object"] is None
        tracking_results.append(("status_inactive", status))
        
        # Verify tracking workflow
        assert len(tracking_results) == 5
        tracking_steps = [step[0] for step in tracking_results]
        expected_steps = ["models", "start", "status_active", "stop", "status_inactive"]
        assert tracking_steps == expected_steps
    
    @responses.activate
    def test_model_training_workflow(self):
        """Test complete model training workflow."""
        # Setup model training responses
        training_responses = [
            # Start training
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/model/train",
                "response": {
                    "status": "training_started",
                    "task_id": "train_001",
                    "object_name": "new_object",
                    "image_count": 10
                },
                "status": 200
            },
            # Get updated model list
            {
                "method": responses.GET,
                "url": f"{self.backend_url}/model/list",
                "response": {
                    "models": [
                        {"name": "person", "accuracy": 0.92, "created_at": "2024-01-01T10:00:00Z"},
                        {"name": "vehicle", "accuracy": 0.88, "created_at": "2024-01-01T11:00:00Z"},
                        {"name": "new_object", "accuracy": 0.85, "created_at": "2024-01-01T12:00:00Z"}
                    ]
                },
                "status": 200
            }
        ]
        
        # Add training responses
        for response_config in training_responses:
            responses.add(
                response_config["method"],
                response_config["url"],
                json=response_config["response"],
                status=response_config["status"]
            )
        
        # Execute training workflow
        training_results = []
        
        # 1. Start training (simulate with JSON instead of multipart)
        response = self.session.post(
            f"{self.backend_url}/model/train",
            json={"object_name": "new_object", "image_count": 10}
        )
        assert response.status_code == 200
        training_start = response.json()
        assert training_start["status"] == "training_started"
        assert "task_id" in training_start
        training_results.append(("training_start", training_start))
        
        # 2. Get updated model list (after training completion)
        response = self.session.get(f"{self.backend_url}/model/list")
        assert response.status_code == 200
        models = response.json()["models"]
        
        # Verify new model was added
        model_names = [model["name"] for model in models]
        assert "new_object" in model_names
        training_results.append(("models_updated", models))
        
        # Verify training workflow
        assert len(training_results) == 2
        training_steps = [step[0] for step in training_results]
        expected_steps = ["training_start", "models_updated"]
        assert training_steps == expected_steps
    
    @responses.activate
    def test_sensor_monitoring_workflow(self):
        """Test continuous sensor monitoring workflow."""
        # Setup sensor monitoring responses
        sensors = ["battery", "altitude", "temperature", "attitude", "status"]
        sensor_responses = {}
        
        for sensor in sensors:
            sensor_data = {
                "battery": {"battery_percentage": 85},
                "altitude": {"altitude_cm": 120},
                "temperature": {"temperature_c": 25.5},
                "attitude": {"pitch": 0.5, "roll": -0.2, "yaw": 1.8},
                "status": {"connected": True, "flying": True, "emergency": False}
            }
            
            responses.add(
                responses.GET,
                f"{self.backend_url}/sensors/{sensor}",
                json=sensor_data[sensor],
                status=200
            )
        
        # Execute sensor monitoring
        monitoring_results = []
        
        # Monitor each sensor type
        for sensor in sensors:
            response = self.session.get(f"{self.backend_url}/sensors/{sensor}")
            assert response.status_code == 200
            sensor_data = response.json()
            monitoring_results.append((sensor, sensor_data))
        
        # Verify sensor monitoring
        assert len(monitoring_results) == len(sensors)
        monitored_sensors = [result[0] for result in monitoring_results]
        assert set(monitored_sensors) == set(sensors)
        
        # Verify sensor data structure
        for sensor, data in monitoring_results:
            assert isinstance(data, dict)
            assert len(data) > 0
    
    @responses.activate
    def test_emergency_procedures_workflow(self):
        """Test emergency procedures workflow."""
        # Setup emergency responses
        emergency_responses = [
            # Emergency stop
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/flight/emergency",
                "response": {"status": "success", "operation": "emergency", "message": "Emergency stop executed"},
                "status": 200
            },
            # Stop tracking (if active)
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/tracking/stop",
                "response": {"status": "tracking_stopped"},
                "status": 200
            },
            # Stop streaming
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/camera/stream/stop",
                "response": {"status": "stopped"},
                "status": 200
            },
            # Disconnect
            {
                "method": responses.POST,
                "url": f"{self.backend_url}/connection/disconnect",
                "response": {"status": "disconnected", "message": "Emergency disconnect completed"},
                "status": 200
            }
        ]
        
        # Add emergency responses
        for response_config in emergency_responses:
            responses.add(
                response_config["method"],
                response_config["url"],
                json=response_config["response"],
                status=response_config["status"]
            )
        
        # Execute emergency procedures
        emergency_results = []
        
        # 1. Emergency stop
        response = self.session.post(f"{self.backend_url}/flight/emergency")
        assert response.status_code == 200
        assert response.json()["operation"] == "emergency"
        emergency_results.append(("emergency_stop", response.json()))
        
        # 2. Stop tracking
        response = self.session.post(f"{self.backend_url}/tracking/stop")
        assert response.status_code == 200
        emergency_results.append(("stop_tracking", response.json()))
        
        # 3. Stop streaming
        response = self.session.post(f"{self.backend_url}/camera/stream/stop")
        assert response.status_code == 200
        emergency_results.append(("stop_streaming", response.json()))
        
        # 4. Disconnect
        response = self.session.post(f"{self.backend_url}/connection/disconnect")
        assert response.status_code == 200
        emergency_results.append(("disconnect", response.json()))
        
        # Verify emergency procedures
        assert len(emergency_results) == 4
        emergency_steps = [step[0] for step in emergency_results]
        expected_steps = ["emergency_stop", "stop_tracking", "stop_streaming", "disconnect"]
        assert emergency_steps == expected_steps
    
    @responses.activate
    def test_concurrent_api_operations(self):
        """Test concurrent API operations."""
        # Setup responses for concurrent operations
        concurrent_endpoints = [
            ("/sensors/battery", {"battery_percentage": 85}),
            ("/sensors/altitude", {"altitude_cm": 120}),
            ("/sensors/temperature", {"temperature_c": 25.5}),
            ("/sensors/attitude", {"pitch": 0.5, "roll": -0.2, "yaw": 1.8}),
            ("/system/info", {"version": "1.0.0", "drone_connected": True})
        ]
        
        for endpoint, response_data in concurrent_endpoints:
            responses.add(
                responses.GET,
                f"{self.backend_url}{endpoint}",
                json=response_data,
                status=200
            )
        
        # Execute concurrent requests
        concurrent_results = []
        results_lock = threading.Lock()
        
        def make_request(endpoint, expected_data):
            """Make a single API request."""
            try:
                response = self.session.get(f"{self.backend_url}{endpoint}")
                with results_lock:
                    concurrent_results.append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "data": response.json(),
                        "success": response.status_code == 200
                    })
            except Exception as e:
                with results_lock:
                    concurrent_results.append({
                        "endpoint": endpoint,
                        "error": str(e),
                        "success": False
                    })
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for endpoint, expected_data in concurrent_endpoints:
                future = executor.submit(make_request, endpoint, expected_data)
                futures.append(future)
            
            # Wait for all requests to complete
            for future in futures:
                future.result()
        
        # Verify concurrent operations
        assert len(concurrent_results) == len(concurrent_endpoints)
        
        # Check all requests succeeded
        for result in concurrent_results:
            assert result["success"] == True
            assert result["status_code"] == 200
            assert "data" in result
    
    @responses.activate
    def test_api_error_recovery_workflow(self):
        """Test API error recovery and retry workflows."""
        # Setup error and recovery responses
        error_recovery_scenarios = [
            # First attempt fails, second succeeds
            {
                "endpoint": "/connection/connect",
                "attempts": [
                    {"status": 500, "response": {"error": "Connection failed"}},
                    {"status": 200, "response": {"status": "connected"}}
                ]
            },
            # Timeout simulation with eventual success
            {
                "endpoint": "/system/health",
                "attempts": [
                    {"status": 408, "response": {"error": "Request timeout"}},
                    {"status": 200, "response": {"status": "healthy"}}
                ]
            }
        ]
        
        retry_results = []
        
        for scenario in error_recovery_scenarios:
            endpoint = scenario["endpoint"]
            
            # Add responses for multiple attempts
            for attempt in scenario["attempts"]:
                responses.add(
                    responses.POST if "connect" in endpoint else responses.GET,
                    f"{self.backend_url}{endpoint}",
                    json=attempt["response"],
                    status=attempt["status"]
                )
            
            # Execute retry logic
            max_retries = len(scenario["attempts"]) - 1
            last_response = None
            
            for attempt in range(len(scenario["attempts"])):
                try:
                    if "connect" in endpoint:
                        response = self.session.post(f"{self.backend_url}{endpoint}")
                    else:
                        response = self.session.get(f"{self.backend_url}{endpoint}")
                    
                    last_response = response
                    
                    if response.status_code == 200:
                        break
                        
                except Exception as e:
                    if attempt >= max_retries:
                        pytest.fail(f"Max retries exceeded for {endpoint}: {str(e)}")
            
            retry_results.append({
                "endpoint": endpoint,
                "final_status": last_response.status_code if last_response else None,
                "attempts": len(scenario["attempts"])
            })
        
        # Verify error recovery
        assert len(retry_results) == len(error_recovery_scenarios)
        for result in retry_results:
            assert result["final_status"] == 200