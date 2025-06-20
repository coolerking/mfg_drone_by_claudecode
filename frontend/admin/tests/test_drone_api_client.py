"""
Unit tests for DroneAPIClient class
Tests all public methods with normal, boundary, and error conditions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import sys
import os

# Add the parent directory to sys.path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import DroneAPIClient, app
from tests.mocks.backend_mock import create_mock_session, create_mock_requests


class TestDroneAPIClientBasic:
    """Test basic DroneAPIClient functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.base_url = 'http://testserver'
        self.client = DroneAPIClient(self.base_url)
        
    def test_initialization(self):
        """Test DroneAPIClient initialization"""
        # Test default initialization
        client = DroneAPIClient()
        assert client.base_url == 'http://localhost:8000'
        assert client.session.timeout == 10
        
        # Test custom base_url
        client = DroneAPIClient('http://example.com:8080/')
        assert client.base_url == 'http://example.com:8080'
        
        # Test base_url with trailing slash removal
        client = DroneAPIClient('http://example.com:8080///')
        assert client.base_url == 'http://example.com:8080'
    
    @patch('main.requests.Session')
    def test_make_request_success(self, mock_session_class):
        """Test successful API request"""
        # Setup mock
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        client = DroneAPIClient(self.base_url)
        client.session = mock_session
        
        # Test GET request
        result = client._make_request('GET', '/test')
        assert result is not None
        
        # Test POST request with data
        result = client._make_request('POST', '/test', {'key': 'value'})
        assert result is not None
        
        # Test PUT request
        result = client._make_request('PUT', '/test', {'key': 'value'})
        assert result is not None
        
        # Test DELETE request
        result = client._make_request('DELETE', '/test')
        assert result is not None
    
    @patch('main.requests.Session')
    def test_make_request_invalid_method(self, mock_session_class):
        """Test invalid HTTP method"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        client = DroneAPIClient(self.base_url)
        client.session = mock_session
        
        result = client._make_request('INVALID', '/test')
        assert result is None
    
    @patch('main.requests.Session')
    def test_make_request_http_error(self, mock_session_class):
        """Test HTTP error response"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_session.get.return_value = mock_response
        mock_session.timeout = 10
        mock_session_class.return_value = mock_session
        
        client = DroneAPIClient(self.base_url)
        client.session = mock_session
        
        result = client._make_request('GET', '/test')
        assert result is None
    
    @patch('main.requests.Session')
    def test_make_request_network_error(self, mock_session_class):
        """Test network error"""
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("Network error")
        mock_session.timeout = 10
        mock_session_class.return_value = mock_session
        
        client = DroneAPIClient(self.base_url)
        client.session = mock_session
        
        result = client._make_request('GET', '/test')
        assert result is None


class TestDroneAPIClientHealth:
    """Test health check functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_health_check_success(self, mock_session_class):
        """Test successful health check"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.health_check()
        
        assert result is not None
        assert result['status'] == 'healthy'
    
    @patch('main.requests.Session')
    def test_health_check_failure(self, mock_session_class):
        """Test health check failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/health'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.health_check()
        
        assert result is None


class TestDroneAPIClientConnection:
    """Test drone connection management"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_connect_drone_success(self, mock_session_class):
        """Test successful drone connection"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.connect_drone()
        
        assert result is not None
        assert result['status'] == 'connected'
    
    @patch('main.requests.Session')
    def test_connect_drone_failure(self, mock_session_class):
        """Test drone connection failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/drone/connect'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.connect_drone()
        
        assert result is None
    
    @patch('main.requests.Session')
    def test_disconnect_drone_success(self, mock_session_class):
        """Test successful drone disconnection"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.disconnect_drone()
        
        assert result is not None
        assert result['status'] == 'disconnected'
    
    @patch('main.requests.Session')
    def test_disconnect_drone_failure(self, mock_session_class):
        """Test drone disconnection failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/drone/disconnect'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.disconnect_drone()
        
        assert result is None


class TestDroneAPIClientFlightControl:
    """Test basic flight control functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_takeoff_success(self, mock_session_class):
        """Test successful takeoff"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.takeoff()
        
        assert result is not None
        assert result['status'] == 'takeoff'
    
    @patch('main.requests.Session')
    def test_takeoff_failure(self, mock_session_class):
        """Test takeoff failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/drone/takeoff'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.takeoff()
        
        assert result is None
    
    @patch('main.requests.Session')
    def test_land_success(self, mock_session_class):
        """Test successful landing"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.land()
        
        assert result is not None
        assert result['status'] == 'landed'
    
    @patch('main.requests.Session')
    def test_land_failure(self, mock_session_class):
        """Test landing failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/drone/land'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.land()
        
        assert result is None
    
    @patch('main.requests.Session')
    def test_emergency_stop_success(self, mock_session_class):
        """Test successful emergency stop"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.emergency_stop()
        
        assert result is not None
        assert result['status'] == 'emergency_stop'
    
    @patch('main.requests.Session')
    def test_emergency_stop_failure(self, mock_session_class):
        """Test emergency stop failure"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True, ['/drone/emergency'])
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.emergency_stop()
        
        assert result is None


class TestDroneAPIClientBasicMovement:
    """Test basic movement control functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_move_forward_success(self, mock_session_class):
        """Test successful forward movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test with default distance
        result = self.client.move_forward(30)
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'forward'
        
        # Test with boundary values
        result = self.client.move_forward(20)  # Min value
        assert result is not None
        
        result = self.client.move_forward(500)  # Max value
        assert result is not None
    
    @patch('main.requests.Session')
    def test_move_backward_success(self, mock_session_class):
        """Test successful backward movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.move_backward(30)
        
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'back'
    
    @patch('main.requests.Session')
    def test_move_left_success(self, mock_session_class):
        """Test successful left movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.move_left(30)
        
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'left'
    
    @patch('main.requests.Session')
    def test_move_right_success(self, mock_session_class):
        """Test successful right movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.move_right(30)
        
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'right'
    
    @patch('main.requests.Session')
    def test_move_up_success(self, mock_session_class):
        """Test successful upward movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.move_up(30)
        
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'up'
    
    @patch('main.requests.Session')
    def test_move_down_success(self, mock_session_class):
        """Test successful downward movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.move_down(30)
        
        assert result is not None
        assert result['status'] == 'moving'
        assert result['direction'] == 'down'
    
    @patch('main.requests.Session')
    def test_rotate_success(self, mock_session_class):
        """Test successful rotation"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test clockwise rotation
        result = self.client.rotate('cw', 90)
        assert result is not None
        assert result['status'] == 'rotating'
        
        # Test counter-clockwise rotation
        result = self.client.rotate('ccw', 180)
        assert result is not None
        
        # Test boundary values
        result = self.client.rotate('cw', 1)  # Min angle
        assert result is not None
        
        result = self.client.rotate('cw', 360)  # Max angle
        assert result is not None
    
    @patch('main.requests.Session')
    def test_flip_success(self, mock_session_class):
        """Test successful flip"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test all flip directions
        for direction in ['f', 'b', 'l', 'r']:
            result = self.client.flip(direction)
            assert result is not None
            assert result['status'] == 'flipping'
    
    @patch('main.requests.Session')
    def test_movement_failure(self, mock_session_class):
        """Test movement command failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test all movement functions with failure
        assert self.client.move_forward(30) is None
        assert self.client.move_backward(30) is None
        assert self.client.move_left(30) is None
        assert self.client.move_right(30) is None
        assert self.client.move_up(30) is None
        assert self.client.move_down(30) is None
        assert self.client.rotate('cw', 90) is None
        assert self.client.flip('f') is None