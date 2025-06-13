"""
Custom assertions for Admin Frontend testing
"""
import json
from typing import Dict, Any, List, Optional, Union
from flask import Response

class ResponseAssertions:
    """Custom assertions for HTTP responses"""
    
    @staticmethod
    def assert_success_response(response: Response, expected_message: str = None):
        """Assert response is successful"""
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        
        if response.content_type and 'application/json' in response.content_type:
            data = response.get_json()
            assert data.get('success', False), f"Response not successful: {data}"
            
            if expected_message:
                assert data.get('message') == expected_message, f"Expected message '{expected_message}', got '{data.get('message')}'"
    
    @staticmethod
    def assert_error_response(response: Response, expected_status: int = None, expected_error_code: str = None):
        """Assert response is an error"""
        if expected_status:
            assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
        else:
            assert response.status_code >= 400, f"Expected error status (>=400), got {response.status_code}"
        
        if response.content_type and 'application/json' in response.content_type:
            data = response.get_json()
            assert 'error' in data, f"Error response missing 'error' field: {data}"
            
            if expected_error_code:
                assert data.get('code') == expected_error_code, f"Expected error code '{expected_error_code}', got '{data.get('code')}'"
    
    @staticmethod
    def assert_json_response(response: Response, expected_data: Dict[str, Any] = None):
        """Assert response is JSON and optionally check data"""
        assert response.content_type and 'application/json' in response.content_type, f"Expected JSON response, got {response.content_type}"
        
        data = response.get_json()
        assert data is not None, "Response JSON data is None"
        
        if expected_data:
            for key, expected_value in expected_data.items():
                assert key in data, f"Missing key '{key}' in response data"
                assert data[key] == expected_value, f"Expected {key}='{expected_value}', got '{data[key]}'"
    
    @staticmethod
    def assert_html_response(response: Response, contains_text: List[str] = None):
        """Assert response is HTML and optionally check content"""
        assert response.content_type and 'text/html' in response.content_type, f"Expected HTML response, got {response.content_type}"
        
        if contains_text:
            content = response.get_data(as_text=True)
            for text in contains_text:
                assert text in content, f"HTML content does not contain '{text}'"
    
    @staticmethod
    def assert_redirect_response(response: Response, expected_location: str = None):
        """Assert response is a redirect"""
        assert 300 <= response.status_code < 400, f"Expected redirect status (3xx), got {response.status_code}"
        
        if expected_location:
            location = response.headers.get('Location', '')
            assert expected_location in location, f"Expected redirect to contain '{expected_location}', got '{location}'"

class APIAssertions:
    """Custom assertions for API interactions"""
    
    @staticmethod
    def assert_api_call_made(mock_api, method: str, endpoint: str, expected_data: Dict[str, Any] = None):
        """Assert API call was made"""
        history = mock_api.get_request_history()
        
        # Find matching call
        matching_calls = [
            call for call in history 
            if call['method'] == method.upper() and call['endpoint'] == endpoint
        ]
        
        assert len(matching_calls) > 0, f"No {method} call made to {endpoint}. History: {history}"
        
        if expected_data:
            last_call = matching_calls[-1]
            call_data = last_call.get('data', {})
            
            for key, expected_value in expected_data.items():
                assert key in call_data, f"Missing key '{key}' in API call data"
                assert call_data[key] == expected_value, f"Expected {key}='{expected_value}', got '{call_data[key]}'"
    
    @staticmethod
    def assert_api_call_count(mock_api, method: str, endpoint: str, expected_count: int):
        """Assert number of API calls made"""
        history = mock_api.get_request_history()
        
        matching_calls = [
            call for call in history 
            if call['method'] == method.upper() and call['endpoint'] == endpoint
        ]
        
        assert len(matching_calls) == expected_count, f"Expected {expected_count} {method} calls to {endpoint}, got {len(matching_calls)}"
    
    @staticmethod
    def assert_no_api_calls(mock_api):
        """Assert no API calls were made"""
        history = mock_api.get_request_history()
        assert len(history) == 0, f"Expected no API calls, but {len(history)} were made: {history}"

class DroneDataAssertions:
    """Custom assertions for drone data validation"""
    
    @staticmethod
    def assert_valid_drone_status(data: Dict[str, Any]):
        """Assert drone status data is valid"""
        required_fields = ['connected', 'battery', 'height', 'temperature']
        
        for field in required_fields:
            assert field in data, f"Missing required field '{field}' in drone status"
        
        # Validate ranges
        if data.get('connected'):
            assert 0 <= data['battery'] <= 100, f"Invalid battery level: {data['battery']}"
            assert 0 <= data['height'] <= 3000, f"Invalid height: {data['height']}"
            assert 0 <= data['temperature'] <= 90, f"Invalid temperature: {data['temperature']}"
    
    @staticmethod
    def assert_valid_tracking_status(data: Dict[str, Any]):
        """Assert tracking status data is valid"""
        required_fields = ['is_tracking', 'target_object', 'target_detected']
        
        for field in required_fields:
            assert field in data, f"Missing required field '{field}' in tracking status"
        
        # Validate tracking logic
        if data['is_tracking']:
            assert data['target_object'] is not None, "Target object should not be None when tracking"
            
            if data['target_detected']:
                assert 'target_position' in data, "Target position required when target is detected"
                position = data['target_position']
                assert isinstance(position, dict), "Target position should be a dict"
                assert all(key in position for key in ['x', 'y', 'width', 'height']), "Missing position coordinates"
        else:
            assert data['target_object'] is None, "Target object should be None when not tracking"
    
    @staticmethod
    def assert_valid_model_list(data: Dict[str, Any]):
        """Assert model list data is valid"""
        assert 'models' in data, "Missing 'models' field in model list"
        
        models = data['models']
        assert isinstance(models, list), "Models should be a list"
        
        for model in models:
            required_fields = ['name', 'created_at', 'accuracy']
            for field in required_fields:
                assert field in model, f"Missing required field '{field}' in model data"
            
            assert 0.0 <= model['accuracy'] <= 1.0, f"Invalid accuracy value: {model['accuracy']}"

class FormAssertions:
    """Custom assertions for form validation"""
    
    @staticmethod
    def assert_form_errors(form_data: Dict[str, Any], expected_errors: List[str]):
        """Assert form contains expected validation errors"""
        errors = form_data.get('errors', [])
        
        for expected_error in expected_errors:
            assert any(expected_error in error for error in errors), f"Expected error '{expected_error}' not found in {errors}"
    
    @staticmethod
    def assert_form_valid(form_data: Dict[str, Any]):
        """Assert form is valid (no errors)"""
        errors = form_data.get('errors', [])
        assert len(errors) == 0, f"Form should be valid but has errors: {errors}"
    
    @staticmethod
    def assert_required_fields(form_data: Dict[str, Any], required_fields: List[str]):
        """Assert form contains all required fields"""
        for field in required_fields:
            assert field in form_data, f"Missing required field '{field}' in form data"
            assert form_data[field] is not None and form_data[field] != "", f"Required field '{field}' is empty"

class WebSocketAssertions:
    """Custom assertions for WebSocket testing"""
    
    @staticmethod
    def assert_event_emitted(mock_socketio, event_name: str, expected_data: Dict[str, Any] = None):
        """Assert WebSocket event was emitted"""
        emitted_events = mock_socketio.get_emitted_events(event=event_name)
        
        assert len(emitted_events) > 0, f"No '{event_name}' events were emitted"
        
        if expected_data:
            last_event = emitted_events[-1]
            event_data = last_event.get('data', {})
            
            for key, expected_value in expected_data.items():
                assert key in event_data, f"Missing key '{key}' in event data"
                assert event_data[key] == expected_value, f"Expected {key}='{expected_value}', got '{event_data[key]}'"
    
    @staticmethod
    def assert_event_count(mock_socketio, event_name: str, expected_count: int):
        """Assert number of WebSocket events emitted"""
        emitted_events = mock_socketio.get_emitted_events(event=event_name)
        
        assert len(emitted_events) == expected_count, f"Expected {expected_count} '{event_name}' events, got {len(emitted_events)}"
    
    @staticmethod
    def assert_no_events_emitted(mock_socketio):
        """Assert no WebSocket events were emitted"""
        all_events = mock_socketio.get_emitted_events()
        assert len(all_events) == 0, f"Expected no events, but {len(all_events)} were emitted"

class FileAssertions:
    """Custom assertions for file upload testing"""
    
    @staticmethod
    def assert_valid_image_files(file_paths: List[str]):
        """Assert files are valid images"""
        from PIL import Image
        
        for file_path in file_paths:
            try:
                with Image.open(file_path) as img:
                    img.verify()  # Verify it's a valid image
            except Exception as e:
                assert False, f"Invalid image file '{file_path}': {e}"
    
    @staticmethod
    def assert_file_upload_limits(files_data: List[Dict[str, Any]], max_size: int = 10 * 1024 * 1024, min_count: int = 5):
        """Assert file upload meets limits"""
        assert len(files_data) >= min_count, f"Need at least {min_count} files, got {len(files_data)}"
        
        for file_data in files_data:
            size = file_data.get('size', 0)
            assert size <= max_size, f"File too large: {size} bytes (max: {max_size})"
            assert size > 0, "File is empty"

# Convenience function to get all assertion classes
def get_all_assertions():
    """Get all assertion classes for easy import"""
    return {
        'response': ResponseAssertions,
        'api': APIAssertions,
        'drone': DroneDataAssertions,
        'form': FormAssertions,
        'websocket': WebSocketAssertions,
        'file': FileAssertions
    }