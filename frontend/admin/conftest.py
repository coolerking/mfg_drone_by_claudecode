"""
Pytest configuration and shared fixtures for Admin Frontend tests
"""
import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
from flask import Flask
from pathlib import Path

# Add the admin directory to Python path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory"""
    temp_dir = tempfile.mkdtemp(prefix="admin_frontend_test_")
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def flask_app():
    """Create a Flask app instance for testing"""
    from main import app
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create application context
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def client(flask_app):
    """Create a test client"""
    return flask_app.test_client()

@pytest.fixture(scope="function")
def mock_backend_api():
    """Mock backend API for testing"""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        
        # Default successful responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True, "message": "OK"}
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"success": True, "message": "OK"}
        
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"success": True, "message": "OK"}
        
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = {"success": True, "message": "OK"}
        
        yield {
            'post': mock_post,
            'get': mock_get,
            'put': mock_put,
            'delete': mock_delete
        }

@pytest.fixture(scope="function")
def sample_drone_status():
    """Sample drone status data for testing"""
    return {
        "connected": True,
        "battery": 85,
        "height": 120,
        "temperature": 35,
        "flight_time": 45,
        "speed": 0.5,
        "barometer": 1013.25,
        "distance_tof": 150,
        "acceleration": {"x": 0.1, "y": 0.0, "z": 9.8},
        "velocity": {"x": 0, "y": 0, "z": 0},
        "attitude": {"pitch": 0, "roll": 0, "yaw": 90}
    }

@pytest.fixture(scope="function")  
def sample_tracking_status():
    """Sample tracking status data for testing"""
    return {
        "is_tracking": True,
        "target_object": "person",
        "target_detected": True,
        "target_position": {
            "x": 320,
            "y": 240,
            "width": 100,
            "height": 150
        }
    }

@pytest.fixture(scope="function")
def sample_model_list():
    """Sample model list data for testing"""
    return {
        "models": [
            {
                "name": "person_model",
                "created_at": "2024-01-15T10:30:00Z",
                "accuracy": 0.92
            },
            {
                "name": "car_model", 
                "created_at": "2024-01-20T14:15:00Z",
                "accuracy": 0.88
            }
        ]
    }

@pytest.fixture(scope="function")
def test_image_files(test_data_dir):
    """Create test image files"""
    from PIL import Image
    import numpy as np
    
    images = []
    for i in range(3):
        # Create a simple test image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        img_path = os.path.join(test_data_dir, f"test_image_{i}.jpg")
        img.save(img_path)
        images.append(img_path)
    
    return images

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("BACKEND_API_URL", "http://localhost:8000")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

# Custom test markers
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "mock_backend: mark test as using mock backend"
    )
    config.addinivalue_line(
        "markers", "real_backend: mark test as requiring real backend"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_hardware: mark test as requiring hardware"
    )