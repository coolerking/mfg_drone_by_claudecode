"""
Backend API Mock for Unit Testing
Mocks all backend API calls to eliminate external dependencies
"""

import json
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, Optional


class MockResponse:
    """Mock HTTP response object"""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
        self.headers = {'content-type': 'application/json'}
    
    def json(self):
        return self.json_data
    
    def iter_content(self, chunk_size=1024):
        """Mock streaming content"""
        content = b"mock_video_stream_data"
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]


class BackendAPIMock:
    """Complete backend API mock for testing"""
    
    def __init__(self):
        self.call_history = []
        self.responses = self._setup_default_responses()
        self.should_fail = False
        self.fail_endpoints = set()
        
    def _setup_default_responses(self) -> Dict[str, Dict[str, Any]]:
        """Setup default successful responses"""
        return {
            # Health check
            '/health': {'status': 'healthy', 'version': '1.0.0'},
            
            # Connection
            '/drone/connect': {'status': 'connected', 'message': 'Drone connected successfully'},
            '/drone/disconnect': {'status': 'disconnected', 'message': 'Drone disconnected successfully'},
            
            # Flight control
            '/drone/takeoff': {'status': 'takeoff', 'message': 'Drone taking off'},
            '/drone/land': {'status': 'landed', 'message': 'Drone landed successfully'},
            '/drone/emergency': {'status': 'emergency_stop', 'message': 'Emergency stop executed'},
            
            # Basic movement
            '/drone/move/forward': {'status': 'moving', 'direction': 'forward', 'distance': 30},
            '/drone/move/back': {'status': 'moving', 'direction': 'back', 'distance': 30},
            '/drone/move/left': {'status': 'moving', 'direction': 'left', 'distance': 30},
            '/drone/move/right': {'status': 'moving', 'direction': 'right', 'distance': 30},
            '/drone/move/up': {'status': 'moving', 'direction': 'up', 'distance': 30},
            '/drone/move/down': {'status': 'moving', 'direction': 'down', 'distance': 30},
            '/drone/rotate': {'status': 'rotating', 'direction': 'cw', 'angle': 90},
            '/drone/flip': {'status': 'flipping', 'direction': 'l'},
            
            # Advanced movement
            '/drone/go_xyz': {'status': 'moving_xyz', 'x': 0, 'y': 0, 'z': 0, 'speed': 50},
            '/drone/curve_xyz': {'status': 'curve_flight', 'message': 'Curve flight executed'},
            '/drone/rc_control': {'status': 'rc_control', 'message': 'RC control active'},
            
            # Camera
            '/camera/stream/start': {'status': 'streaming', 'message': 'Video stream started'},
            '/camera/stream/stop': {'status': 'stopped', 'message': 'Video stream stopped'},
            '/camera/photo': {'status': 'photo_taken', 'filename': 'drone_photo_001.jpg'},
            '/camera/recording/start': {'status': 'recording', 'message': 'Recording started'},
            '/camera/recording/stop': {'status': 'stopped', 'filename': 'drone_video_001.mp4'},
            '/camera/stream': {'status': 'streaming'},
            
            # Sensors
            '/drone/battery': {'battery_level': 85, 'status': 'good'},
            '/drone/altitude': {'altitude': 120, 'unit': 'cm'},
            '/drone/temperature': {'temperature': 25.5, 'unit': 'celsius'},
            '/drone/attitude': {'pitch': 0, 'roll': 0, 'yaw': 0},
            '/drone/velocity': {'vx': 0, 'vy': 0, 'vz': 0},
            
            # Settings
            '/drone/wifi': {'status': 'wifi_set', 'message': 'WiFi settings updated'},
            '/drone/speed': {'status': 'speed_set', 'speed': 5.0},
            '/drone/command': {'status': 'command_sent', 'response': 'ok'},
            
            # Mission pad
            '/mission_pad/enable': {'status': 'enabled', 'message': 'Mission pad detection enabled'},
            '/mission_pad/disable': {'status': 'disabled', 'message': 'Mission pad detection disabled'},
            '/mission_pad/detection_direction': {'status': 'direction_set', 'direction': 0},
            '/mission_pad/go_xyz': {'status': 'moving_to_pad', 'mission_pad_id': 1},
            '/mission_pad/status': {'enabled': True, 'detection_direction': 0, 'current_pad': None},
            
            # Tracking
            '/tracking/start': {'status': 'tracking', 'target_object': 'person', 'mode': 'center'},
            '/tracking/stop': {'status': 'stopped', 'message': 'Tracking stopped'},
            '/tracking/status': {'status': 'active', 'target_object': 'person', 'confidence': 0.95},
            
            # Model management
            '/model/list': {'models': ['person_model', 'car_model', 'ball_model']},
            '/model/train': {'status': 'training', 'object_name': 'test_object', 'model_id': 'model_123'},
        }
    
    def set_failure_mode(self, should_fail: bool, endpoints: Optional[list] = None):
        """Set mock to return failures for specified endpoints"""
        self.should_fail = should_fail
        if endpoints:
            self.fail_endpoints = set(endpoints)
        else:
            self.fail_endpoints = set()
    
    def get_call_history(self):
        """Get history of all API calls made"""
        return self.call_history
    
    def clear_call_history(self):
        """Clear call history"""
        self.call_history = []
    
    def mock_request(self, method: str, url: str, **kwargs):
        """Mock HTTP request"""
        # Extract endpoint from URL
        endpoint = url.replace('http://localhost:8000', '').replace('http://testserver', '')
        
        # Record the call
        call_record = {
            'method': method.upper(),
            'endpoint': endpoint,
            'url': url,
            'kwargs': kwargs
        }
        self.call_history.append(call_record)
        
        # Handle special cases
        if endpoint.startswith('/model/') and method.upper() == 'DELETE':
            model_name = endpoint.split('/')[-1]
            return MockResponse({'status': 'deleted', 'model_name': model_name})
        
        # Check if this endpoint should fail
        if (self.should_fail and not self.fail_endpoints) or endpoint in self.fail_endpoints:
            return MockResponse({'error': 'Mocked failure'}, status_code=500)
        
        # Return default response or error
        if endpoint in self.responses:
            return MockResponse(self.responses[endpoint])
        else:
            return MockResponse({'error': 'Endpoint not found'}, status_code=404)


def create_mock_session():
    """Create a mock requests session"""
    mock = BackendAPIMock()
    session = Mock()
    session.timeout = 10
    session.get = Mock(side_effect=lambda url, **kwargs: mock.mock_request('GET', url, **kwargs))
    session.post = Mock(side_effect=lambda url, **kwargs: mock.mock_request('POST', url, **kwargs))
    session.put = Mock(side_effect=lambda url, **kwargs: mock.mock_request('PUT', url, **kwargs))
    session.delete = Mock(side_effect=lambda url, **kwargs: mock.mock_request('DELETE', url, **kwargs))
    
    # Store reference to mock for test access
    session._mock_backend = mock
    
    return session


def create_mock_requests():
    """Create mock for requests module"""
    mock = BackendAPIMock()
    requests_mock = Mock()
    requests_mock.get = Mock(side_effect=lambda url, **kwargs: mock.mock_request('GET', url, **kwargs))
    requests_mock.post = Mock(side_effect=lambda url, **kwargs: mock.mock_request('POST', url, **kwargs))
    requests_mock.put = Mock(side_effect=lambda url, **kwargs: mock.mock_request('PUT', url, **kwargs))
    requests_mock.delete = Mock(side_effect=lambda url, **kwargs: mock.mock_request('DELETE', url, **kwargs))
    requests_mock.Session = Mock(return_value=create_mock_session())
    
    # Handle exceptions
    requests_mock.exceptions = Mock()
    requests_mock.exceptions.RequestException = Exception
    requests_mock.exceptions.Timeout = Exception
    requests_mock.exceptions.ConnectionError = Exception
    
    # Store reference to mock for test access
    requests_mock._mock_backend = mock
    
    return requests_mock