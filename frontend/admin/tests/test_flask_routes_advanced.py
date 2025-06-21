"""
Unit tests for advanced Flask routes
Tests sensors, camera, mission pad, tracking, model management, settings, and error handlers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os
from io import BytesIO

# Add the parent directory to sys.path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, api_client
from tests.mocks.backend_mock import create_mock_session, create_mock_requests


class TestSensorRoutes:
    """Test sensor data API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.get_battery')
    @patch('main.api_client.get_altitude')
    @patch('main.api_client.get_temperature')
    @patch('main.api_client.get_attitude')
    @patch('main.api_client.get_velocity')
    def test_get_all_sensors_success(self, mock_velocity, mock_attitude, mock_temp, mock_altitude, mock_battery):
        """Test successful all sensors data retrieval"""
        mock_battery.return_value = {'battery_level': 85}
        mock_altitude.return_value = {'altitude': 120}
        mock_temp.return_value = {'temperature': 25.5}
        mock_attitude.return_value = {'pitch': 0, 'roll': 0, 'yaw': 0}
        mock_velocity.return_value = {'vx': 0, 'vy': 0, 'vz': 0}
        
        response = self.client.get('/api/sensors/all')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'battery' in data
        assert 'altitude' in data
        assert 'temperature' in data
        assert 'attitude' in data
        assert 'velocity' in data
        assert data['battery']['battery_level'] == 85
        assert data['altitude']['altitude'] == 120
    
    @patch('main.api_client.get_battery')
    def test_get_battery_success(self, mock_battery):
        """Test successful battery data retrieval"""
        mock_battery.return_value = {'battery_level': 85, 'status': 'good'}
        
        response = self.client.get('/api/drone/battery')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['battery_level'] == 85
        assert data['status'] == 'good'
    
    @patch('main.api_client.get_battery')
    def test_get_battery_failure(self, mock_battery):
        """Test battery data retrieval failure"""
        mock_battery.return_value = None
        
        response = self.client.get('/api/drone/battery')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Battery data unavailable'
    
    @patch('main.api_client.get_altitude')
    def test_get_altitude_success(self, mock_altitude):
        """Test successful altitude data retrieval"""
        mock_altitude.return_value = {'altitude': 120, 'unit': 'cm'}
        
        response = self.client.get('/api/drone/altitude')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['altitude'] == 120
        assert data['unit'] == 'cm'
    
    @patch('main.api_client.get_altitude')
    def test_get_altitude_failure(self, mock_altitude):
        """Test altitude data retrieval failure"""
        mock_altitude.return_value = None
        
        response = self.client.get('/api/drone/altitude')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Altitude data unavailable'
    
    @patch('main.api_client.get_temperature')
    def test_get_temperature_success(self, mock_temperature):
        """Test successful temperature data retrieval"""
        mock_temperature.return_value = {'temperature': 25.5, 'unit': 'celsius'}
        
        response = self.client.get('/api/drone/temperature')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['temperature'] == 25.5
        assert data['unit'] == 'celsius'
    
    @patch('main.api_client.get_temperature')
    def test_get_temperature_failure(self, mock_temperature):
        """Test temperature data retrieval failure"""
        mock_temperature.return_value = None
        
        response = self.client.get('/api/drone/temperature')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Temperature data unavailable'
    
    @patch('main.api_client.get_attitude')
    def test_get_attitude_success(self, mock_attitude):
        """Test successful attitude data retrieval"""
        mock_attitude.return_value = {'pitch': 0, 'roll': 0, 'yaw': 0}
        
        response = self.client.get('/api/drone/attitude')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['pitch'] == 0
        assert data['roll'] == 0
        assert data['yaw'] == 0
    
    @patch('main.api_client.get_attitude')
    def test_get_attitude_failure(self, mock_attitude):
        """Test attitude data retrieval failure"""
        mock_attitude.return_value = None
        
        response = self.client.get('/api/drone/attitude')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Attitude data unavailable'


class TestCameraRoutes:
    """Test camera control API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.start_video_stream')
    def test_start_video_stream_success(self, mock_start):
        """Test successful video stream start"""
        mock_start.return_value = {'status': 'streaming'}
        
        response = self.client.post('/api/camera/stream/start')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'streaming'
    
    @patch('main.api_client.start_video_stream')
    def test_start_video_stream_failure(self, mock_start):
        """Test video stream start failure"""
        mock_start.return_value = None
        
        response = self.client.post('/api/camera/stream/start')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Stream start failed'
    
    @patch('main.api_client.stop_video_stream')
    def test_stop_video_stream_success(self, mock_stop):
        """Test successful video stream stop"""
        mock_stop.return_value = {'status': 'stopped'}
        
        response = self.client.post('/api/camera/stream/stop')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'stopped'
    
    @patch('main.api_client.stop_video_stream')
    def test_stop_video_stream_failure(self, mock_stop):
        """Test video stream stop failure"""
        mock_stop.return_value = None
        
        response = self.client.post('/api/camera/stream/stop')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Stream stop failed'
    
    @patch('main.api_client.take_photo')
    def test_take_photo_success(self, mock_photo):
        """Test successful photo capture"""
        mock_photo.return_value = {'status': 'photo_taken', 'filename': 'photo.jpg'}
        
        response = self.client.post('/api/camera/photo')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'photo_taken'
        assert data['filename'] == 'photo.jpg'
    
    @patch('main.api_client.take_photo')
    def test_take_photo_failure(self, mock_photo):
        """Test photo capture failure"""
        mock_photo.return_value = None
        
        response = self.client.post('/api/camera/photo')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Photo capture failed'
    
    @patch('main.api_client.start_recording')
    def test_start_recording_success(self, mock_record):
        """Test successful recording start"""
        mock_record.return_value = {'status': 'recording'}
        
        response = self.client.post('/api/camera/recording/start')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'recording'
    
    @patch('main.api_client.start_recording')
    def test_start_recording_failure(self, mock_record):
        """Test recording start failure"""
        mock_record.return_value = None
        
        response = self.client.post('/api/camera/recording/start')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Recording start failed'
    
    @patch('main.api_client.stop_recording')
    def test_stop_recording_success(self, mock_record):
        """Test successful recording stop"""
        mock_record.return_value = {'status': 'stopped', 'filename': 'video.mp4'}
        
        response = self.client.post('/api/camera/recording/stop')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'stopped'
        assert data['filename'] == 'video.mp4'
    
    @patch('main.api_client.stop_recording')
    def test_stop_recording_failure(self, mock_record):
        """Test recording stop failure"""
        mock_record.return_value = None
        
        response = self.client.post('/api/camera/recording/stop')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Recording stop failed'
    
    @patch('main.requests.get')
    def test_video_stream_proxy_success(self, mock_get):
        """Test successful video stream proxy"""
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b'video_data'])
        mock_response.headers = {'content-type': 'video/mp4'}
        mock_get.return_value = mock_response
        
        with patch('main.BACKEND_API_URL', 'http://localhost:8000'):
            response = self.client.get('/api/camera/stream')
            assert response.status_code == 200
    
    @patch('main.requests.get')
    def test_video_stream_proxy_failure(self, mock_get):
        """Test video stream proxy failure"""
        mock_get.side_effect = Exception("Network error")
        
        response = self.client.get('/api/camera/stream')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Video stream unavailable'


class TestMissionPadRoutes:
    """Test mission pad API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.enable_mission_pad')
    def test_enable_mission_pad_success(self, mock_enable):
        """Test successful mission pad enable"""
        mock_enable.return_value = {'status': 'enabled'}
        
        response = self.client.post('/api/mission_pad/enable')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'enabled'
    
    @patch('main.api_client.enable_mission_pad')
    def test_enable_mission_pad_failure(self, mock_enable):
        """Test mission pad enable failure"""
        mock_enable.return_value = None
        
        response = self.client.post('/api/mission_pad/enable')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Mission pad enable failed'
    
    @patch('main.api_client.disable_mission_pad')
    def test_disable_mission_pad_success(self, mock_disable):
        """Test successful mission pad disable"""
        mock_disable.return_value = {'status': 'disabled'}
        
        response = self.client.post('/api/mission_pad/disable')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'disabled'
    
    @patch('main.api_client.disable_mission_pad')
    def test_disable_mission_pad_failure(self, mock_disable):
        """Test mission pad disable failure"""
        mock_disable.return_value = None
        
        response = self.client.post('/api/mission_pad/disable')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Mission pad disable failed'
    
    @patch('main.api_client.set_detection_direction')
    def test_set_detection_direction_success(self, mock_set_direction):
        """Test successful detection direction setting"""
        mock_set_direction.return_value = {'status': 'direction_set'}
        
        response = self.client.put('/api/mission_pad/detection_direction', 
                                 json={'direction': 1})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'direction_set'
        mock_set_direction.assert_called_once_with(1)
    
    @patch('main.api_client.set_detection_direction')
    def test_set_detection_direction_default(self, mock_set_direction):
        """Test detection direction setting with default value"""
        mock_set_direction.return_value = {'status': 'direction_set'}
        
        response = self.client.put('/api/mission_pad/detection_direction', json={})
        assert response.status_code == 200
        
        mock_set_direction.assert_called_once_with(0)  # Default value
    
    @patch('main.api_client.set_detection_direction')
    def test_set_detection_direction_failure(self, mock_set_direction):
        """Test detection direction setting failure"""
        mock_set_direction.return_value = None
        
        response = self.client.put('/api/mission_pad/detection_direction', 
                                 json={'direction': 1})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Detection direction setting failed'
    
    @patch('main.api_client.go_to_mission_pad')
    def test_go_to_mission_pad_success(self, mock_go_to_pad):
        """Test successful mission pad movement"""
        mock_go_to_pad.return_value = {'status': 'moving_to_pad'}
        
        response = self.client.post('/api/mission_pad/go_xyz', 
                                  json={'x': 100, 'y': 100, 'z': 100, 
                                       'speed': 50, 'mission_pad_id': 2})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'moving_to_pad'
        mock_go_to_pad.assert_called_once_with(100, 100, 100, 50, 2)
    
    @patch('main.api_client.go_to_mission_pad')
    def test_go_to_mission_pad_default_values(self, mock_go_to_pad):
        """Test mission pad movement with default values"""
        mock_go_to_pad.return_value = {'status': 'moving_to_pad'}
        
        response = self.client.post('/api/mission_pad/go_xyz', json={})
        assert response.status_code == 200
        
        mock_go_to_pad.assert_called_once_with(0, 0, 0, 50, 1)  # Default values
    
    @patch('main.api_client.go_to_mission_pad')
    def test_go_to_mission_pad_failure(self, mock_go_to_pad):
        """Test mission pad movement failure"""
        mock_go_to_pad.return_value = None
        
        response = self.client.post('/api/mission_pad/go_xyz', 
                                  json={'x': 100, 'y': 100, 'z': 100, 
                                       'speed': 50, 'mission_pad_id': 2})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Mission pad movement failed'
    
    @patch('main.api_client.get_mission_pad_status')
    def test_get_mission_pad_status_success(self, mock_get_status):
        """Test successful mission pad status retrieval"""
        mock_get_status.return_value = {'enabled': True, 'detection_direction': 0}
        
        response = self.client.get('/api/mission_pad/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['enabled'] == True
        assert data['detection_direction'] == 0
    
    @patch('main.api_client.get_mission_pad_status')
    def test_get_mission_pad_status_failure(self, mock_get_status):
        """Test mission pad status retrieval failure"""
        mock_get_status.return_value = None
        
        response = self.client.get('/api/mission_pad/status')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Mission pad status unavailable'


class TestTrackingRoutes:
    """Test object tracking API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.start_tracking')
    def test_start_tracking_success(self, mock_start):
        """Test successful tracking start"""
        mock_start.return_value = {'status': 'tracking', 'target_object': 'person'}
        
        response = self.client.post('/api/tracking/start', 
                                  json={'target_object': 'person', 'tracking_mode': 'center'})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'tracking'
        assert data['target_object'] == 'person'
        mock_start.assert_called_once_with('person', 'center')
    
    @patch('main.api_client.start_tracking')
    def test_start_tracking_default_mode(self, mock_start):
        """Test tracking start with default mode"""
        mock_start.return_value = {'status': 'tracking', 'target_object': 'person'}
        
        response = self.client.post('/api/tracking/start', 
                                  json={'target_object': 'person'})
        assert response.status_code == 200
        
        mock_start.assert_called_once_with('person', 'center')  # Default mode
    
    def test_start_tracking_missing_target(self):
        """Test tracking start with missing target object"""
        response = self.client.post('/api/tracking/start', json={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Target object not specified'
    
    @patch('main.api_client.start_tracking')
    def test_start_tracking_failure(self, mock_start):
        """Test tracking start failure"""
        mock_start.return_value = None
        
        response = self.client.post('/api/tracking/start', 
                                  json={'target_object': 'person'})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Tracking start failed'
    
    @patch('main.api_client.stop_tracking')
    def test_stop_tracking_success(self, mock_stop):
        """Test successful tracking stop"""
        mock_stop.return_value = {'status': 'stopped'}
        
        response = self.client.post('/api/tracking/stop')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'stopped'
    
    @patch('main.api_client.stop_tracking')
    def test_stop_tracking_failure(self, mock_stop):
        """Test tracking stop failure"""
        mock_stop.return_value = None
        
        response = self.client.post('/api/tracking/stop')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Tracking stop failed'
    
    @patch('main.api_client.get_tracking_status')
    def test_get_tracking_status_success(self, mock_get_status):
        """Test successful tracking status retrieval"""
        mock_get_status.return_value = {'status': 'active', 'target_object': 'person'}
        
        response = self.client.get('/api/tracking/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'active'
        assert data['target_object'] == 'person'
    
    @patch('main.api_client.get_tracking_status')
    def test_get_tracking_status_failure(self, mock_get_status):
        """Test tracking status retrieval failure"""
        mock_get_status.return_value = None
        
        response = self.client.get('/api/tracking/status')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Tracking status unavailable'


class TestModelManagementRoutes:
    """Test model management API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.requests.post')
    def test_train_model_success(self, mock_post):
        """Test successful model training"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'training', 'model_id': 'model_123'}
        mock_post.return_value = mock_response
        
        data = {
            'object_name': 'test_object'
        }
        data['file'] = (BytesIO(b'test file content'), 'test.jpg')
        
        response = self.client.post('/api/model/train', 
                                  data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['status'] == 'training'
        assert response_data['model_id'] == 'model_123'
    
    def test_train_model_no_file(self):
        """Test model training with no file"""
        response = self.client.post('/api/model/train', 
                                  data={'object_name': 'test_object'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'No file provided'
    
    def test_train_model_no_object_name(self):
        """Test model training with no object name"""
        data = {}
        data['file'] = (BytesIO(b'test file content'), 'test.jpg')
        
        response = self.client.post('/api/model/train', 
                                  data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == 'Object name required'
    
    @patch('main.requests.post')
    def test_train_model_backend_error(self, mock_post):
        """Test model training with backend error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        data = {
            'object_name': 'test_object'
        }
        data['file'] = (BytesIO(b'test file content'), 'test.jpg')
        
        response = self.client.post('/api/model/train', 
                                  data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == 'Model training failed'
    
    @patch('main.requests.post')
    def test_train_model_network_error(self, mock_post):
        """Test model training with network error"""
        mock_post.side_effect = Exception("Network error")
        
        data = {
            'object_name': 'test_object'
        }
        data['file'] = (BytesIO(b'test file content'), 'test.jpg')
        
        response = self.client.post('/api/model/train', 
                                  data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == 'File upload failed'
    
    @patch('main.api_client.get_model_list')
    def test_get_model_list_success(self, mock_get_list):
        """Test successful model list retrieval"""
        mock_get_list.return_value = {'models': ['model1', 'model2', 'model3']}
        
        response = self.client.get('/api/model/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'models' in data
        assert len(data['models']) == 3
    
    @patch('main.api_client.get_model_list')
    def test_get_model_list_failure(self, mock_get_list):
        """Test model list retrieval failure"""
        mock_get_list.return_value = None
        
        response = self.client.get('/api/model/list')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Model list unavailable'
    
    @patch('main.api_client.delete_model')
    def test_delete_model_success(self, mock_delete):
        """Test successful model deletion"""
        mock_delete.return_value = {'status': 'deleted', 'model_name': 'test_model'}
        
        response = self.client.delete('/api/model/test_model')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'deleted'
        assert data['model_name'] == 'test_model'
        mock_delete.assert_called_once_with('test_model')
    
    @patch('main.api_client.delete_model')
    def test_delete_model_failure(self, mock_delete):
        """Test model deletion failure"""
        mock_delete.return_value = None
        
        response = self.client.delete('/api/model/test_model')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Model deletion failed'


class TestSettingsRoutes:
    """Test settings management API routes"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('main.api_client.set_wifi')
    def test_set_wifi_success(self, mock_set_wifi):
        """Test successful WiFi settings"""
        mock_set_wifi.return_value = {'status': 'wifi_set'}
        
        response = self.client.put('/api/settings/wifi', 
                                 json={'ssid': 'TestSSID', 'password': 'TestPassword'})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'wifi_set'
        mock_set_wifi.assert_called_once_with('TestSSID', 'TestPassword')
    
    def test_set_wifi_missing_ssid(self):
        """Test WiFi settings with missing SSID"""
        response = self.client.put('/api/settings/wifi', 
                                 json={'password': 'TestPassword'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'SSID and password required'
    
    def test_set_wifi_missing_password(self):
        """Test WiFi settings with missing password"""
        response = self.client.put('/api/settings/wifi', 
                                 json={'ssid': 'TestSSID'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'SSID and password required'
    
    @patch('main.api_client.set_wifi')
    def test_set_wifi_failure(self, mock_set_wifi):
        """Test WiFi settings failure"""
        mock_set_wifi.return_value = None
        
        response = self.client.put('/api/settings/wifi', 
                                 json={'ssid': 'TestSSID', 'password': 'TestPassword'})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'WiFi setting failed'
    
    @patch('main.api_client.set_speed')
    def test_set_speed_success(self, mock_set_speed):
        """Test successful speed setting"""
        mock_set_speed.return_value = {'status': 'speed_set', 'speed': 5.0}
        
        response = self.client.put('/api/settings/speed', 
                                 json={'speed': 5.0})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'speed_set'
        assert data['speed'] == 5.0
        mock_set_speed.assert_called_once_with(5.0)
    
    @pytest.mark.parametrize("speed", [0.5, 16.0, None])
    def test_set_speed_invalid_values(self, speed):
        """Test speed setting with invalid values"""
        response = self.client.put('/api/settings/speed', 
                                 json={'speed': speed})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid speed value (1.0-15.0 m/s)'
    
    @patch('main.api_client.set_speed')
    def test_set_speed_failure(self, mock_set_speed):
        """Test speed setting failure"""
        mock_set_speed.return_value = None
        
        response = self.client.put('/api/settings/speed', 
                                 json={'speed': 5.0})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Speed setting failed'
    
    @patch('main.api_client.send_command')
    def test_send_command_success(self, mock_send):
        """Test successful command sending"""
        mock_send.return_value = {'status': 'command_sent', 'response': 'ok'}
        
        response = self.client.post('/api/settings/command', 
                                  json={'command': 'battery?', 'timeout': 10})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'command_sent'
        assert data['response'] == 'ok'
        mock_send.assert_called_once_with('battery?', 10)
    
    @patch('main.api_client.send_command')
    def test_send_command_default_timeout(self, mock_send):
        """Test command sending with default timeout"""
        mock_send.return_value = {'status': 'command_sent', 'response': 'ok'}
        
        response = self.client.post('/api/settings/command', 
                                  json={'command': 'battery?'})
        assert response.status_code == 200
        
        mock_send.assert_called_once_with('battery?', 7)  # Default timeout
    
    def test_send_command_missing_command(self):
        """Test command sending with missing command"""
        response = self.client.post('/api/settings/command', json={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Command required'
    
    @patch('main.api_client.send_command')
    def test_send_command_failure(self, mock_send):
        """Test command sending failure"""
        mock_send.return_value = None
        
        response = self.client.post('/api/settings/command', 
                                  json={'command': 'battery?'})
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Command execution failed'


class TestErrorHandlers:
    """Test error handlers"""
    
    def setup_method(self):
        """Setup for each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_404_handler(self):
        """Test 404 error handler"""
        response = self.client.get('/nonexistent/endpoint')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Endpoint not found'
    
    def test_500_handler(self):
        """Test 500 error handler"""
        # This requires triggering a server error
        with patch('main.render_template', side_effect=Exception("Server error")):
            response = self.client.get('/')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Internal server error'