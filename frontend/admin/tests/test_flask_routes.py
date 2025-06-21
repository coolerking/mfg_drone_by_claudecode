"""
Unit tests for Flask routes
Tests all API endpoints and route handlers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the parent directory to sys.path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, api_client
from tests.mocks.backend_mock import create_mock_session, create_mock_requests


class TestBasicRoutes:
    """Test basic Flask routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_index_route(self):
        """Test main page route"""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data  # Should return HTML content
    
    @patch('main.api_client.health_check')
    def test_health_check_success(self, mock_health_check):
        """Test successful health check"""
        mock_health_check.return_value = {'status': 'healthy'}
        
        response = self.client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['frontend'] == 'MFG Drone Admin v1.0.0 (Phase 5)'
        assert data['backend'] == 'healthy'
    
    @patch('main.api_client.health_check')
    def test_health_check_backend_unavailable(self, mock_health_check):
        """Test health check with backend unavailable"""
        mock_health_check.return_value = None
        
        response = self.client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['frontend'] == 'MFG Drone Admin v1.0.0 (Phase 5)'
        assert data['backend'] == 'unavailable'


class TestDroneControlRoutes:
    """Test drone control API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.connect_drone')
    def test_connect_drone_success(self, mock_connect):
        """Test successful drone connection"""
        mock_connect.return_value = {'status': 'connected'}
        
        response = self.client.post('/api/drone/connect')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'connected'
    
    @patch('main.api_client.connect_drone')
    def test_connect_drone_failure(self, mock_connect):
        """Test drone connection failure"""
        mock_connect.return_value = None
        
        response = self.client.post('/api/drone/connect')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Connection failed'
    
    @patch('main.api_client.disconnect_drone')
    def test_disconnect_drone_success(self, mock_disconnect):
        """Test successful drone disconnection"""
        mock_disconnect.return_value = {'status': 'disconnected'}
        
        response = self.client.post('/api/drone/disconnect')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'disconnected'
    
    @patch('main.api_client.disconnect_drone')
    def test_disconnect_drone_failure(self, mock_disconnect):
        """Test drone disconnection failure"""
        mock_disconnect.return_value = None
        
        response = self.client.post('/api/drone/disconnect')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Disconnection failed'
    
    @patch('main.api_client.takeoff')
    def test_takeoff_success(self, mock_takeoff):
        """Test successful takeoff"""
        mock_takeoff.return_value = {'status': 'takeoff'}
        
        response = self.client.post('/api/drone/takeoff')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'takeoff'
    
    @patch('main.api_client.takeoff')
    def test_takeoff_failure(self, mock_takeoff):
        """Test takeoff failure"""
        mock_takeoff.return_value = None
        
        response = self.client.post('/api/drone/takeoff')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Takeoff failed'
    
    @patch('main.api_client.land')
    def test_land_success(self, mock_land):
        """Test successful landing"""
        mock_land.return_value = {'status': 'landed'}
        
        response = self.client.post('/api/drone/land')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'landed'
    
    @patch('main.api_client.land')
    def test_land_failure(self, mock_land):
        """Test landing failure"""
        mock_land.return_value = None
        
        response = self.client.post('/api/drone/land')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Landing failed'
    
    @patch('main.api_client.emergency_stop')
    def test_emergency_stop_success(self, mock_emergency):
        """Test successful emergency stop"""
        mock_emergency.return_value = {'status': 'emergency_stop'}
        
        response = self.client.post('/api/drone/emergency')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'emergency_stop'
    
    @patch('main.api_client.emergency_stop')
    def test_emergency_stop_failure(self, mock_emergency):
        """Test emergency stop failure"""
        mock_emergency.return_value = None
        
        response = self.client.post('/api/drone/emergency')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Emergency stop failed'


class TestMovementRoutes:
    """Test movement control API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.move_forward')
    def test_move_forward_success(self, mock_move):
        """Test successful forward movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'forward'}
        
        response = self.client.post('/api/drone/move/forward', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'forward'
        mock_move.assert_called_once_with(50)
    
    @patch('main.api_client.move_forward')
    def test_move_forward_default_distance(self, mock_move):
        """Test forward movement with default distance"""
        mock_move.return_value = {'status': 'moving', 'direction': 'forward'}
        
        response = self.client.post('/api/drone/move/forward', json={})
        assert response.status_code == 200
        
        mock_move.assert_called_once_with(30)  # Default distance
    
    @patch('main.api_client.move_backward')
    def test_move_backward_success(self, mock_move):
        """Test successful backward movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'back'}
        
        response = self.client.post('/api/drone/move/backward', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'back'
        mock_move.assert_called_once_with(50)
    
    @patch('main.api_client.move_left')
    def test_move_left_success(self, mock_move):
        """Test successful left movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'left'}
        
        response = self.client.post('/api/drone/move/left', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'left'
        mock_move.assert_called_once_with(50)
    
    @patch('main.api_client.move_right')
    def test_move_right_success(self, mock_move):
        """Test successful right movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'right'}
        
        response = self.client.post('/api/drone/move/right', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'right'
        mock_move.assert_called_once_with(50)
    
    @patch('main.api_client.move_up')
    def test_move_up_success(self, mock_move):
        """Test successful upward movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'up'}
        
        response = self.client.post('/api/drone/move/up', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'up'
        mock_move.assert_called_once_with(50)
    
    @patch('main.api_client.move_down')
    def test_move_down_success(self, mock_move):
        """Test successful downward movement"""
        mock_move.return_value = {'status': 'moving', 'direction': 'down'}
        
        response = self.client.post('/api/drone/move/down', 
                                  json={'distance': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving'
        assert data['direction'] == 'down'
        mock_move.assert_called_once_with(50)
    
    def test_move_invalid_direction(self):
        """Test movement with invalid direction"""
        response = self.client.post('/api/drone/move/invalid', 
                                  json={'distance': 50})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid direction'
    
    @patch('main.api_client.move_forward')
    def test_move_failure(self, mock_move):
        """Test movement failure"""
        mock_move.return_value = None
        
        response = self.client.post('/api/drone/move/forward', 
                                  json={'distance': 50})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'forward movement failed'
    
    @patch('main.api_client.rotate')
    def test_rotate_success(self, mock_rotate):
        """Test successful rotation"""
        mock_rotate.return_value = {'status': 'rotating', 'direction': 'cw'}
        
        response = self.client.post('/api/drone/rotate', 
                                  json={'direction': 'cw', 'angle': 90})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'rotating'
        mock_rotate.assert_called_once_with('cw', 90)
    
    @patch('main.api_client.rotate')
    def test_rotate_default_angle(self, mock_rotate):
        """Test rotation with default angle"""
        mock_rotate.return_value = {'status': 'rotating', 'direction': 'cw'}
        
        response = self.client.post('/api/drone/rotate', 
                                  json={'direction': 'cw'})
        assert response.status_code == 200
        
        mock_rotate.assert_called_once_with('cw', 90)  # Default angle
    
    @patch('main.api_client.rotate')
    def test_rotate_failure(self, mock_rotate):
        """Test rotation failure"""
        mock_rotate.return_value = None
        
        response = self.client.post('/api/drone/rotate', 
                                  json={'direction': 'cw', 'angle': 90})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Rotation failed'


class TestAdvancedMovementRoutes:
    """Test advanced movement API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.go_xyz')
    def test_go_xyz_success(self, mock_go_xyz):
        """Test successful 3D coordinate movement"""
        mock_go_xyz.return_value = {'status': 'moving_xyz'}
        
        response = self.client.post('/api/drone/go_xyz', 
                                  json={'x': 100, 'y': 200, 'z': 150, 'speed': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving_xyz'
        mock_go_xyz.assert_called_once_with(100, 200, 150, 50)
    
    @patch('main.api_client.go_xyz')
    def test_go_xyz_default_values(self, mock_go_xyz):
        """Test 3D movement with default values"""
        mock_go_xyz.return_value = {'status': 'moving_xyz'}
        
        response = self.client.post('/api/drone/go_xyz', json={})
        assert response.status_code == 200
        
        mock_go_xyz.assert_called_once_with(0, 0, 0, 50)  # Default values
    
    @patch('main.api_client.go_xyz')
    def test_go_xyz_failure(self, mock_go_xyz):
        """Test 3D movement failure"""
        mock_go_xyz.return_value = None
        
        response = self.client.post('/api/drone/go_xyz', 
                                  json={'x': 100, 'y': 200, 'z': 150, 'speed': 50})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'XYZ movement failed'
    
    @patch('main.api_client.curve_xyz')
    def test_curve_xyz_success(self, mock_curve_xyz):
        """Test successful curve flight"""
        mock_curve_xyz.return_value = {'status': 'curve_flight'}
        
        response = self.client.post('/api/drone/curve_xyz', 
                                  json={'x1': 60, 'y1': 0, 'z1': 60, 
                                       'x2': 0, 'y2': 60, 'z2': 0, 'speed': 30})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'curve_flight'
        mock_curve_xyz.assert_called_once_with(60, 0, 60, 0, 60, 0, 30)
    
    @patch('main.api_client.curve_xyz')
    def test_curve_xyz_default_values(self, mock_curve_xyz):
        """Test curve flight with default values"""
        mock_curve_xyz.return_value = {'status': 'curve_flight'}
        
        response = self.client.post('/api/drone/curve_xyz', json={})
        assert response.status_code == 200
        
        mock_curve_xyz.assert_called_once_with(0, 0, 0, 0, 0, 0, 30)  # Default values
    
    @patch('main.api_client.curve_xyz')
    def test_curve_xyz_failure(self, mock_curve_xyz):
        """Test curve flight failure"""
        mock_curve_xyz.return_value = None
        
        response = self.client.post('/api/drone/curve_xyz', 
                                  json={'x1': 60, 'y1': 0, 'z1': 60, 
                                       'x2': 0, 'y2': 60, 'z2': 0, 'speed': 30})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Curve flight failed'
    
    @patch('main.api_client.rc_control')
    def test_rc_control_success(self, mock_rc_control):
        """Test successful RC control"""
        mock_rc_control.return_value = {'status': 'rc_control'}
        
        response = self.client.post('/api/drone/rc_control', 
                                  json={'left_right_velocity': 0, 
                                       'forward_backward_velocity': 50,
                                       'up_down_velocity': 0, 
                                       'yaw_velocity': 0})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'rc_control'
        mock_rc_control.assert_called_once_with(0, 50, 0, 0)
    
    @patch('main.api_client.rc_control')
    def test_rc_control_default_values(self, mock_rc_control):
        """Test RC control with default values"""
        mock_rc_control.return_value = {'status': 'rc_control'}
        
        response = self.client.post('/api/drone/rc_control', json={})
        assert response.status_code == 200
        
        mock_rc_control.assert_called_once_with(0, 0, 0, 0)  # Default values
    
    @patch('main.api_client.rc_control')
    def test_rc_control_failure(self, mock_rc_control):
        """Test RC control failure"""
        mock_rc_control.return_value = None
        
        response = self.client.post('/api/drone/rc_control', 
                                  json={'left_right_velocity': 0, 
                                       'forward_backward_velocity': 50,
                                       'up_down_velocity': 0, 
                                       'yaw_velocity': 0})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'RC control failed'