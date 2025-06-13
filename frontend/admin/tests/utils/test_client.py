"""
Test client utilities for Admin Frontend testing
"""
import requests
import time
import threading
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch
import sys
import os

# Add mocks to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mocks'))
from backend_server import MockBackendServer

class AdminFrontendTestClient:
    """Test client for Admin Frontend"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.mock_backend = None
    
    def setup_mock_backend(self, host='localhost', port=8000):
        """Setup mock backend server"""
        self.mock_backend = MockBackendServer(host, port)
        self.mock_backend.start()
        return self.mock_backend
    
    def teardown_mock_backend(self):
        """Teardown mock backend server"""
        if self.mock_backend:
            self.mock_backend.stop()
            self.mock_backend = None
    
    def get(self, path: str, **kwargs) -> requests.Response:
        """GET request to frontend"""
        url = f"{self.base_url}{path}"
        return self.session.get(url, **kwargs)
    
    def post(self, path: str, **kwargs) -> requests.Response:
        """POST request to frontend"""
        url = f"{self.base_url}{path}"
        return self.session.post(url, **kwargs)
    
    def put(self, path: str, **kwargs) -> requests.Response:
        """PUT request to frontend"""
        url = f"{self.base_url}{path}"
        return self.session.put(url, **kwargs)
    
    def delete(self, path: str, **kwargs) -> requests.Response:
        """DELETE request to frontend"""
        url = f"{self.base_url}{path}"
        return self.session.delete(url, **kwargs)
    
    def upload_files(self, path: str, files: List[str], object_name: str = "test_object") -> requests.Response:
        """Upload files to frontend"""
        url = f"{self.base_url}{path}"
        
        files_data = []
        for file_path in files:
            files_data.append(('images', open(file_path, 'rb')))
        
        data = {'object_name': object_name}
        
        try:
            response = self.session.post(url, files=files_data, data=data)
            return response
        finally:
            # Close file handles
            for _, file_handle in files_data:
                file_handle.close()
    
    def check_health(self) -> bool:
        """Check if frontend is healthy"""
        try:
            response = self.get('/health')
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_health():
                return True
            time.sleep(0.5)
        
        return False

class MockAPIClient:
    """Mock API client for unit testing"""
    
    def __init__(self):
        self.responses = {}
        self.request_history = []
        self.default_response = {"success": True, "message": "OK"}
    
    def set_response(self, method: str, endpoint: str, response: Dict[str, Any], status_code: int = 200):
        """Set mock response for specific endpoint"""
        key = f"{method.upper()}:{endpoint}"
        self.responses[key] = {
            'response': response,
            'status_code': status_code
        }
    
    def set_responses(self, responses: Dict[str, Dict[str, Any]]):
        """Set multiple responses at once"""
        for key, response_data in responses.items():
            if ':' in key:
                method, endpoint = key.split(':', 1)
                self.set_response(method, endpoint, response_data.get('response', {}), response_data.get('status_code', 200))
    
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get history of all requests made"""
        return self.request_history.copy()
    
    def clear_history(self):
        """Clear request history"""
        self.request_history.clear()
    
    def _log_request(self, method: str, endpoint: str, data: Any = None, **kwargs):
        """Log request for history tracking"""
        self.request_history.append({
            'method': method.upper(),
            'endpoint': endpoint,
            'data': data,
            'kwargs': kwargs,
            'timestamp': time.time()
        })
    
    def get(self, endpoint: str, **kwargs) -> Mock:
        """Mock GET request"""
        self._log_request('GET', endpoint, **kwargs)
        
        key = f"GET:{endpoint}"
        if key in self.responses:
            response_data = self.responses[key]
        else:
            response_data = {'response': self.default_response, 'status_code': 200}
        
        mock_response = Mock()
        mock_response.status_code = response_data['status_code']
        mock_response.json.return_value = response_data['response']
        mock_response.text = str(response_data['response'])
        
        return mock_response
    
    def post(self, endpoint: str, data: Any = None, **kwargs) -> Mock:
        """Mock POST request"""
        self._log_request('POST', endpoint, data, **kwargs)
        
        key = f"POST:{endpoint}"
        if key in self.responses:
            response_data = self.responses[key]
        else:
            response_data = {'response': self.default_response, 'status_code': 200}
        
        mock_response = Mock()
        mock_response.status_code = response_data['status_code']
        mock_response.json.return_value = response_data['response']
        mock_response.text = str(response_data['response'])
        
        return mock_response
    
    def put(self, endpoint: str, data: Any = None, **kwargs) -> Mock:
        """Mock PUT request"""
        self._log_request('PUT', endpoint, data, **kwargs)
        
        key = f"PUT:{endpoint}"
        if key in self.responses:
            response_data = self.responses[key]
        else:
            response_data = {'response': self.default_response, 'status_code': 200}
        
        mock_response = Mock()
        mock_response.status_code = response_data['status_code']
        mock_response.json.return_value = response_data['response']
        mock_response.text = str(response_data['response'])
        
        return mock_response
    
    def delete(self, endpoint: str, **kwargs) -> Mock:
        """Mock DELETE request"""
        self._log_request('DELETE', endpoint, **kwargs)
        
        key = f"DELETE:{endpoint}"
        if key in self.responses:
            response_data = self.responses[key]
        else:
            response_data = {'response': self.default_response, 'status_code': 200}
        
        mock_response = Mock()
        mock_response.status_code = response_data['status_code']
        mock_response.json.return_value = response_data['response']
        mock_response.text = str(response_data['response'])
        
        return mock_response

class FlaskTestClient:
    """Enhanced Flask test client wrapper"""
    
    def __init__(self, flask_app):
        self.app = flask_app
        self.client = flask_app.test_client()
        self.context = flask_app.app_context()
    
    def __enter__(self):
        self.context.push()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.pop()
    
    def get(self, path: str, **kwargs):
        """GET request with automatic JSON parsing"""
        response = self.client.get(path, **kwargs)
        if response.content_type and 'application/json' in response.content_type:
            response.json_data = response.get_json()
        return response
    
    def post(self, path: str, **kwargs):
        """POST request with automatic JSON parsing"""
        response = self.client.post(path, **kwargs)
        if response.content_type and 'application/json' in response.content_type:
            response.json_data = response.get_json()
        return response
    
    def put(self, path: str, **kwargs):
        """PUT request with automatic JSON parsing"""
        response = self.client.put(path, **kwargs)
        if response.content_type and 'application/json' in response.content_type:
            response.json_data = response.get_json()
        return response
    
    def delete(self, path: str, **kwargs):
        """DELETE request with automatic JSON parsing"""
        response = self.client.delete(path, **kwargs)
        if response.content_type and 'application/json' in response.content_type:
            response.json_data = response.get_json()
        return response

def create_test_environment():
    """Create complete test environment"""
    return {
        'mock_backend': MockBackendServer(),
        'api_client': MockAPIClient(),
        'frontend_client': AdminFrontendTestClient()
    }

def setup_integration_test():
    """Setup integration test with mock backend"""
    mock_backend = MockBackendServer()
    mock_backend.start()
    
    # Wait for server to start
    time.sleep(0.5)
    
    return mock_backend

def teardown_integration_test(mock_backend):
    """Teardown integration test"""
    if mock_backend:
        mock_backend.stop()

class AsyncTestHelper:
    """Helper for testing async operations"""
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def wait_for_value(value_func, expected_value, timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a function to return expected value"""
        def condition():
            try:
                return value_func() == expected_value
            except Exception:
                return False
        
        return AsyncTestHelper.wait_for_condition(condition, timeout, interval)
    
    @staticmethod
    def run_with_timeout(func, timeout: float = 5.0):
        """Run function with timeout"""
        result = {'value': None, 'exception': None}
        
        def target():
            try:
                result['value'] = func()
            except Exception as e:
                result['exception'] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Function did not complete within {timeout} seconds")
        
        if result['exception']:
            raise result['exception']
        
        return result['value']