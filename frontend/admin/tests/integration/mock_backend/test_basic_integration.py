"""
Basic integration tests with mock backend
"""
import pytest
import requests
import time
import threading
import sys
import os

# Add utils and mocks to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'mocks'))

from test_client import AdminFrontendTestClient, setup_integration_test, teardown_integration_test
from backend_server import MockBackendServer

@pytest.mark.integration
@pytest.mark.mock_backend
class TestBasicIntegration:
    """Basic integration tests with mock backend"""
    
    @classmethod
    def setup_class(cls):
        """Setup mock backend for all tests in this class"""
        cls.mock_backend = MockBackendServer('localhost', 8000)
        cls.mock_backend.start()
        
        # Wait for server to be ready
        time.sleep(0.5)
    
    @classmethod
    def teardown_class(cls):
        """Teardown mock backend"""
        if hasattr(cls, 'mock_backend'):
            cls.mock_backend.stop()
    
    def test_mock_backend_health(self):
        """Test mock backend is responding"""
        response = requests.get('http://localhost:8000/health')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_mock_backend_drone_connect(self):
        """Test mock backend drone connection"""
        response = requests.post('http://localhost:8000/drone/connect')
        assert response.status_code in [200, 500]  # Either success or simulated failure
        
        data = response.json()
        if response.status_code == 200:
            assert data['success'] is True
            assert 'message' in data
        else:
            assert 'error' in data
            assert 'code' in data
    
    def test_mock_backend_drone_status(self):
        """Test mock backend drone status"""
        # First connect drone
        connect_response = requests.post('http://localhost:8000/drone/connect')
        
        if connect_response.status_code == 200:
            # Get status
            response = requests.get('http://localhost:8000/drone/status')
            assert response.status_code == 200
            
            data = response.json()
            assert 'connected' in data
            assert 'battery' in data
            assert 'height' in data
            assert 'temperature' in data
        else:
            # Test when not connected
            response = requests.get('http://localhost:8000/drone/status')
            assert response.status_code == 503
    
    def test_mock_backend_model_list(self):
        """Test mock backend model list"""
        response = requests.get('http://localhost:8000/model/list')
        assert response.status_code == 200
        
        data = response.json()
        assert 'models' in data
        assert isinstance(data['models'], list)
        
        # Check model structure
        if len(data['models']) > 0:
            model = data['models'][0]
            assert 'name' in model
            assert 'created_at' in model
            assert 'accuracy' in model
    
    def test_mock_backend_tracking_status(self):
        """Test mock backend tracking status"""
        response = requests.get('http://localhost:8000/tracking/status')
        assert response.status_code == 200
        
        data = response.json()
        assert 'is_tracking' in data
        assert 'target_object' in data
        assert 'target_detected' in data
    
    def test_mock_backend_tracking_start_stop(self):
        """Test mock backend tracking start/stop"""
        # Start tracking
        start_data = {'target_object': 'person', 'tracking_mode': 'center'}
        response = requests.post('http://localhost:8000/tracking/start', json=start_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        
        # Check status
        response = requests.get('http://localhost:8000/tracking/status')
        assert response.status_code == 200
        
        status = response.json()
        assert status['is_tracking'] is True
        assert status['target_object'] == 'person'
        
        # Stop tracking
        response = requests.post('http://localhost:8000/tracking/stop')
        assert response.status_code == 200
        
        # Check status again
        response = requests.get('http://localhost:8000/tracking/status')
        assert response.status_code == 200
        
        status = response.json()
        assert status['is_tracking'] is False
    
    def test_mock_backend_camera_operations(self):
        """Test mock backend camera operations"""
        # Test stream start (without drone connected)
        response = requests.post('http://localhost:8000/camera/stream/start')
        assert response.status_code == 503  # Not connected
        
        # Connect drone first
        connect_response = requests.post('http://localhost:8000/drone/connect')
        
        if connect_response.status_code == 200:
            # Now try stream start
            response = requests.post('http://localhost:8000/camera/stream/start')
            assert response.status_code in [200, 409]  # Success or already started
            
            # Test photo capture
            response = requests.post('http://localhost:8000/camera/photo')
            assert response.status_code == 200
            
            # Test stream stop
            response = requests.post('http://localhost:8000/camera/stream/stop')
            assert response.status_code == 200

@pytest.mark.integration
@pytest.mark.mock_backend
def test_mock_backend_startup_shutdown():
    """Test mock backend can start and stop cleanly"""
    server = MockBackendServer('localhost', 8001)  # Use different port
    
    # Start server
    server.start()
    time.sleep(0.5)
    
    # Test it's running
    try:
        response = requests.get('http://localhost:8001/health', timeout=2)
        assert response.status_code == 200
    except requests.RequestException:
        pytest.fail("Mock server failed to start or respond")
    
    # Stop server
    server.stop()
    time.sleep(0.5)
    
    # Test it's stopped
    with pytest.raises(requests.RequestException):
        requests.get('http://localhost:8001/health', timeout=1)

@pytest.mark.integration 
@pytest.mark.mock_backend
def test_mock_backend_concurrent_requests():
    """Test mock backend handles concurrent requests"""
    server = MockBackendServer('localhost', 8002)  # Use different port
    
    try:
        server.start()
        time.sleep(0.5)
        
        # Function to make multiple requests
        def make_requests():
            results = []
            for i in range(5):
                try:
                    response = requests.get('http://localhost:8002/health', timeout=2)
                    results.append(response.status_code == 200)
                except requests.RequestException:
                    results.append(False)
            return results
        
        # Start multiple threads
        threads = []
        results = []
        
        for _ in range(3):
            thread = threading.Thread(target=lambda: results.extend(make_requests()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5)
        
        # Check results
        assert len(results) == 15  # 3 threads * 5 requests each
        assert all(results), f"Some requests failed: {results}"
    
    finally:
        server.stop()