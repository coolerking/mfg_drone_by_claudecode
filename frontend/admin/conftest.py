"""
Global test configuration and fixtures for admin frontend tests
"""
import os
import pytest
import tempfile
from unittest.mock import Mock, patch
from flask import Flask
from main import app as flask_app


@pytest.fixture(scope="session")
def app():
    """Create and configure test Flask application."""
    # Create a temporary instance folder
    with tempfile.TemporaryDirectory() as temp_dir:
        flask_app.config.update({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,
            "INSTANCE_PATH": temp_dir,
        })
        
        # Create application context
        with flask_app.app_context():
            yield flask_app


@pytest.fixture
def client(app):
    """Create test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def mock_backend_url():
    """Mock backend API base URL."""
    return "http://localhost:8000"


@pytest.fixture
def mock_websocket_url():
    """Mock WebSocket server URL."""
    return "ws://localhost:8000"


@pytest.fixture(scope="session")
def backend_api_endpoints():
    """Complete list of backend API endpoints for testing."""
    return {
        # System & Connection
        "system_health": "/system/health",
        "system_info": "/system/info", 
        "connection_connect": "/connection/connect",
        "connection_disconnect": "/connection/disconnect",
        "connection_status": "/connection/status",
        
        # Flight Control
        "flight_takeoff": "/flight/takeoff",
        "flight_land": "/flight/land",
        "flight_emergency": "/flight/emergency",
        "flight_hover": "/flight/hover",
        
        # Movement Control
        "movement_forward": "/movement/forward",
        "movement_backward": "/movement/backward", 
        "movement_left": "/movement/left",
        "movement_right": "/movement/right",
        "movement_up": "/movement/up",
        "movement_down": "/movement/down",
        "movement_rotate_cw": "/movement/rotate_cw",
        "movement_rotate_ccw": "/movement/rotate_ccw",
        "movement_stop": "/movement/stop",
        
        # Camera Operations
        "camera_stream_start": "/camera/stream/start",
        "camera_stream_stop": "/camera/stream/stop",
        "camera_stream": "/camera/stream",
        "camera_photo": "/camera/photo",
        "camera_video_start": "/camera/video/start",
        "camera_video_stop": "/camera/video/stop",
        "camera_settings": "/camera/settings",
        
        # Sensors & Status
        "sensors_battery": "/sensors/battery",
        "sensors_altitude": "/sensors/altitude", 
        "sensors_temperature": "/sensors/temperature",
        "sensors_attitude": "/sensors/attitude",
        "sensors_status": "/sensors/status",
        
        # Object Tracking
        "tracking_start": "/tracking/start",
        "tracking_stop": "/tracking/stop", 
        "tracking_status": "/tracking/status",
        
        # Model Management
        "model_train": "/model/train",
        "model_list": "/model/list",
    }


@pytest.fixture
def mock_api_responses():
    """Standard mock API responses for testing."""
    return {
        "system_health": {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"},
        "system_info": {
            "version": "1.0.0",
            "drone_connected": True,
            "available_models": ["person", "vehicle", "ball"]
        },
        "connection_status": {
            "connected": True,
            "battery_level": 85,
            "signal_strength": "excellent"
        },
        "sensors_battery": {"battery_percentage": 85},
        "sensors_altitude": {"altitude_cm": 120},
        "sensors_temperature": {"temperature_c": 25.5},
        "sensors_attitude": {
            "pitch": 0.5,
            "roll": -0.2, 
            "yaw": 1.8
        },
        "tracking_status": {
            "tracking": False,
            "target_object": None,
            "detection_confidence": 0.0,
            "position": {"x": 0, "y": 0}
        },
        "model_list": {
            "models": [
                {
                    "name": "person",
                    "accuracy": 0.92,
                    "created_at": "2024-01-01T10:00:00Z"
                },
                {
                    "name": "vehicle", 
                    "accuracy": 0.88,
                    "created_at": "2024-01-01T11:00:00Z"
                }
            ]
        }
    }


@pytest.fixture
def mock_websocket_events():
    """Standard WebSocket event data for testing.""" 
    return {
        "sensor_update": {
            "event": "sensor_update",
            "data": {
                "battery": 85,
                "altitude": 120,
                "temperature": 25.5,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "tracking_update": {
            "event": "tracking_update", 
            "data": {
                "tracking": True,
                "target_detected": True,
                "position": {"x": 320, "y": 240},
                "confidence": 0.95,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "model_training_progress": {
            "event": "model_training_progress",
            "data": {
                "task_id": "train_001",
                "progress": 75,
                "status": "training",
                "estimated_remaining": 120,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    }


@pytest.fixture
def sample_image_files():
    """Generate sample image files for upload testing."""
    import io
    from PIL import Image
    
    def create_test_image(width=640, height=480, color='RGB'):
        """Create a test image in memory."""
        image = Image.new(color, (width, height), color='red')
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer
    
    return {
        "valid_image": create_test_image(),
        "small_image": create_test_image(320, 240),
        "large_image": create_test_image(1920, 1080),
    }


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean test environment before each test."""
    # Set test environment variables
    os.environ["TESTING"] = "True"
    os.environ["BACKEND_URL"] = "http://localhost:8000"
    
    yield
    
    # Cleanup after test
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "backend_timeout": 5.0,
        "websocket_timeout": 3.0,
        "file_upload_timeout": 10.0,
        "max_retry_attempts": 3,
        "retry_delay": 0.5,
    }