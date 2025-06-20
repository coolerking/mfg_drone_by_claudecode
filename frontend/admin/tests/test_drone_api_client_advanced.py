"""
Unit tests for advanced DroneAPIClient functionality
Tests camera, sensors, advanced movement, mission pad, tracking, and model management
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


class TestDroneAPIClientAdvancedMovement:
    """Test advanced movement control functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_go_xyz_success(self, mock_session_class):
        """Test successful 3D coordinate movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test normal values
        result = self.client.go_xyz(100, 200, 150, 50)
        assert result is not None
        assert result['status'] == 'moving_xyz'
        
        # Test boundary values
        result = self.client.go_xyz(-500, -500, 20, 10)  # Min values
        assert result is not None
        
        result = self.client.go_xyz(500, 500, 500, 100)  # Max values
        assert result is not None
        
        # Test zero values
        result = self.client.go_xyz(0, 0, 0, 10)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_curve_xyz_success(self, mock_session_class):
        """Test successful curve flight"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test normal curve
        result = self.client.curve_xyz(60, 0, 60, 0, 60, 0, 30)
        assert result is not None
        assert result['status'] == 'curve_flight'
        
        # Test boundary values
        result = self.client.curve_xyz(-100, -100, 20, 100, 100, 100, 10)
        assert result is not None
        
        result = self.client.curve_xyz(100, 100, 100, -100, -100, 20, 60)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_rc_control_success(self, mock_session_class):
        """Test successful RC control"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test normal RC control
        result = self.client.rc_control(0, 50, 0, 0)
        assert result is not None
        assert result['status'] == 'rc_control'
        
        # Test boundary values
        result = self.client.rc_control(-100, -100, -100, -100)  # Min values
        assert result is not None
        
        result = self.client.rc_control(100, 100, 100, 100)  # Max values
        assert result is not None
        
        # Test zero values
        result = self.client.rc_control(0, 0, 0, 0)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_advanced_movement_failure(self, mock_session_class):
        """Test advanced movement failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.go_xyz(100, 200, 150, 50) is None
        assert self.client.curve_xyz(60, 0, 60, 0, 60, 0, 30) is None
        assert self.client.rc_control(0, 50, 0, 0) is None


class TestDroneAPIClientCamera:
    """Test camera control functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_start_video_stream_success(self, mock_session_class):
        """Test successful video stream start"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.start_video_stream()
        
        assert result is not None
        assert result['status'] == 'streaming'
    
    @patch('main.requests.Session')
    def test_stop_video_stream_success(self, mock_session_class):
        """Test successful video stream stop"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.stop_video_stream()
        
        assert result is not None
        assert result['status'] == 'stopped'
    
    @patch('main.requests.Session')
    def test_take_photo_success(self, mock_session_class):
        """Test successful photo capture"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.take_photo()
        
        assert result is not None
        assert result['status'] == 'photo_taken'
        assert 'filename' in result
    
    @patch('main.requests.Session')
    def test_start_recording_success(self, mock_session_class):
        """Test successful recording start"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.start_recording()
        
        assert result is not None
        assert result['status'] == 'recording'
    
    @patch('main.requests.Session')
    def test_stop_recording_success(self, mock_session_class):
        """Test successful recording stop"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.stop_recording()
        
        assert result is not None
        assert result['status'] == 'stopped'
        assert 'filename' in result
    
    @patch('main.requests.Session')
    def test_camera_failure(self, mock_session_class):
        """Test camera operation failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.start_video_stream() is None
        assert self.client.stop_video_stream() is None
        assert self.client.take_photo() is None
        assert self.client.start_recording() is None
        assert self.client.stop_recording() is None


class TestDroneAPIClientSensors:
    """Test sensor data functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_get_battery_success(self, mock_session_class):
        """Test successful battery data retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_battery()
        
        assert result is not None
        assert 'battery_level' in result
        assert result['battery_level'] == 85
    
    @patch('main.requests.Session')
    def test_get_altitude_success(self, mock_session_class):
        """Test successful altitude data retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_altitude()
        
        assert result is not None
        assert 'altitude' in result
        assert result['altitude'] == 120
    
    @patch('main.requests.Session')
    def test_get_temperature_success(self, mock_session_class):
        """Test successful temperature data retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_temperature()
        
        assert result is not None
        assert 'temperature' in result
        assert result['temperature'] == 25.5
    
    @patch('main.requests.Session')
    def test_get_attitude_success(self, mock_session_class):
        """Test successful attitude data retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_attitude()
        
        assert result is not None
        assert 'pitch' in result
        assert 'roll' in result
        assert 'yaw' in result
    
    @patch('main.requests.Session')
    def test_get_velocity_success(self, mock_session_class):
        """Test successful velocity data retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_velocity()
        
        assert result is not None
        assert 'vx' in result
        assert 'vy' in result
        assert 'vz' in result
    
    @patch('main.requests.Session')
    def test_sensor_failure(self, mock_session_class):
        """Test sensor data retrieval failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.get_battery() is None
        assert self.client.get_altitude() is None
        assert self.client.get_temperature() is None
        assert self.client.get_attitude() is None
        assert self.client.get_velocity() is None


class TestDroneAPIClientWiFiSettings:
    """Test WiFi and settings functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_set_wifi_success(self, mock_session_class):
        """Test successful WiFi settings"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.set_wifi('TestSSID', 'TestPassword')
        
        assert result is not None
        assert result['status'] == 'wifi_set'
    
    @patch('main.requests.Session')
    def test_set_wifi_boundary_values(self, mock_session_class):
        """Test WiFi settings with boundary values"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test minimum length values
        result = self.client.set_wifi('A', '12345678')
        assert result is not None
        
        # Test maximum length values
        long_ssid = 'A' * 32
        long_password = 'A' * 63
        result = self.client.set_wifi(long_ssid, long_password)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_set_speed_success(self, mock_session_class):
        """Test successful speed setting"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test normal speed
        result = self.client.set_speed(5.0)
        assert result is not None
        assert result['status'] == 'speed_set'
        
        # Test boundary values
        result = self.client.set_speed(1.0)  # Min speed
        assert result is not None
        
        result = self.client.set_speed(15.0)  # Max speed
        assert result is not None
    
    @patch('main.requests.Session')
    def test_send_command_success(self, mock_session_class):
        """Test successful command sending"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test with default timeout
        result = self.client.send_command('battery?')
        assert result is not None
        assert result['status'] == 'command_sent'
        
        # Test with custom timeout
        result = self.client.send_command('speed?', 10)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_send_command_boundary_values(self, mock_session_class):
        """Test command sending with boundary values"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test minimum timeout
        result = self.client.send_command('battery?', 1)
        assert result is not None
        
        # Test maximum timeout
        result = self.client.send_command('battery?', 30)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_settings_failure(self, mock_session_class):
        """Test settings operation failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.set_wifi('TestSSID', 'TestPassword') is None
        assert self.client.set_speed(5.0) is None
        assert self.client.send_command('battery?') is None


class TestDroneAPIClientMissionPad:
    """Test mission pad functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_enable_mission_pad_success(self, mock_session_class):
        """Test successful mission pad enable"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.enable_mission_pad()
        
        assert result is not None
        assert result['status'] == 'enabled'
    
    @patch('main.requests.Session')
    def test_disable_mission_pad_success(self, mock_session_class):
        """Test successful mission pad disable"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.disable_mission_pad()
        
        assert result is not None
        assert result['status'] == 'disabled'
    
    @patch('main.requests.Session')
    def test_set_detection_direction_success(self, mock_session_class):
        """Test successful detection direction setting"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test all detection directions
        for direction in [0, 1, 2]:
            result = self.client.set_detection_direction(direction)
            assert result is not None
            assert result['status'] == 'direction_set'
    
    @patch('main.requests.Session')
    def test_go_to_mission_pad_success(self, mock_session_class):
        """Test successful mission pad movement"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test normal movement
        result = self.client.go_to_mission_pad(100, 100, 100, 50, 1)
        assert result is not None
        assert result['status'] == 'moving_to_pad'
        
        # Test boundary values
        result = self.client.go_to_mission_pad(-100, -100, 20, 10, 8)
        assert result is not None
    
    @patch('main.requests.Session')
    def test_get_mission_pad_status_success(self, mock_session_class):
        """Test successful mission pad status retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_mission_pad_status()
        
        assert result is not None
        assert 'enabled' in result
        assert 'detection_direction' in result
    
    @patch('main.requests.Session')
    def test_mission_pad_failure(self, mock_session_class):
        """Test mission pad operation failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.enable_mission_pad() is None
        assert self.client.disable_mission_pad() is None
        assert self.client.set_detection_direction(0) is None
        assert self.client.go_to_mission_pad(100, 100, 100, 50, 1) is None
        assert self.client.get_mission_pad_status() is None


class TestDroneAPIClientTracking:
    """Test object tracking functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_start_tracking_success(self, mock_session_class):
        """Test successful tracking start"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        # Test with default mode
        result = self.client.start_tracking('person')
        assert result is not None
        assert result['status'] == 'tracking'
        
        # Test with custom mode
        result = self.client.start_tracking('person', 'follow')
        assert result is not None
    
    @patch('main.requests.Session')
    def test_stop_tracking_success(self, mock_session_class):
        """Test successful tracking stop"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.stop_tracking()
        
        assert result is not None
        assert result['status'] == 'stopped'
    
    @patch('main.requests.Session')
    def test_get_tracking_status_success(self, mock_session_class):
        """Test successful tracking status retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_tracking_status()
        
        assert result is not None
        assert 'status' in result
        assert 'target_object' in result
    
    @patch('main.requests.Session')
    def test_tracking_failure(self, mock_session_class):
        """Test tracking operation failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.start_tracking('person') is None
        assert self.client.stop_tracking() is None
        assert self.client.get_tracking_status() is None


class TestDroneAPIClientModelManagement:
    """Test model management functions"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = DroneAPIClient('http://testserver')
    
    @patch('main.requests.Session')
    def test_get_model_list_success(self, mock_session_class):
        """Test successful model list retrieval"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.get_model_list()
        
        assert result is not None
        assert 'models' in result
        assert isinstance(result['models'], list)
    
    @patch('main.requests.Session')
    def test_delete_model_success(self, mock_session_class):
        """Test successful model deletion"""
        mock_session = create_mock_session()
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        result = self.client.delete_model('test_model')
        
        assert result is not None
        assert result['status'] == 'deleted'
        assert result['model_name'] == 'test_model'
    
    @patch('main.requests.Session')
    def test_model_management_failure(self, mock_session_class):
        """Test model management operation failures"""
        mock_session = create_mock_session()
        mock_session._mock_backend.set_failure_mode(True)
        mock_session_class.return_value = mock_session
        
        self.client.session = mock_session
        
        assert self.client.get_model_list() is None
        assert self.client.delete_model('test_model') is None