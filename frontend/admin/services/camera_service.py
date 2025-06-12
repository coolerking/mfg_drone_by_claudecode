"""
Camera Service - Backend API integration for camera operations
カメラサービス - カメラ操作のためのバックエンドAPI統合
"""

import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class CameraService:
    """Camera API service for backend integration"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        """
        Initialize camera service
        
        Args:
            backend_url: Backend API base URL
        """
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to backend API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(self.backend_url, endpoint)
        
        try:
            logger.info(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Return JSON if response has content
            if response.content:
                return response.json()
            return {"status": "success"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            error_msg = f"Backend API error: {str(e)}"
            
            # Try to extract error message from response
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
            except:
                pass
                
            raise requests.RequestException(error_msg)
    
    # Stream control methods
    def start_stream(self) -> Dict[str, Any]:
        """
        Start video streaming
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request('POST', '/camera/stream/start')
    
    def stop_stream(self) -> Dict[str, Any]:
        """
        Stop video streaming
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request('POST', '/camera/stream/stop')
    
    def get_stream_url(self) -> str:
        """
        Get video stream URL
        
        Returns:
            Video stream URL
        """
        return f"{self.backend_url}/camera/stream"
    
    # Photo capture methods
    def capture_photo(self) -> Dict[str, Any]:
        """
        Capture photo
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request('POST', '/camera/photo')
    
    # Video recording methods
    def start_recording(self) -> Dict[str, Any]:
        """
        Start video recording
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request('POST', '/camera/video/start')
    
    def stop_recording(self) -> Dict[str, Any]:
        """
        Stop video recording
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        return self._make_request('POST', '/camera/video/stop')
    
    # Camera settings methods
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update camera settings
        
        Args:
            settings: Dictionary containing camera settings
                - resolution: 'high' or 'low'
                - fps: 'high', 'middle', or 'low'
                - bitrate: integer from 1 to 5
        
        Returns:
            Dict containing response data
            
        Raises:
            requests.RequestException: If request fails
        """
        # Validate settings
        valid_settings = {}
        
        if 'resolution' in settings:
            if settings['resolution'] in ['high', 'low']:
                valid_settings['resolution'] = settings['resolution']
            else:
                raise ValueError("Resolution must be 'high' or 'low'")
        
        if 'fps' in settings:
            if settings['fps'] in ['high', 'middle', 'low']:
                valid_settings['fps'] = settings['fps']
            else:
                raise ValueError("FPS must be 'high', 'middle', or 'low'")
        
        if 'bitrate' in settings:
            bitrate = int(settings['bitrate'])
            if 1 <= bitrate <= 5:
                valid_settings['bitrate'] = bitrate
            else:
                raise ValueError("Bitrate must be between 1 and 5")
        
        if not valid_settings:
            raise ValueError("No valid settings provided")
        
        return self._make_request('PUT', '/camera/settings', json=valid_settings)
    
    # Status check methods
    def check_stream_status(self) -> bool:
        """
        Check if streaming is currently active
        
        Returns:
            True if streaming is active, False otherwise
        """
        try:
            # Try to access the stream endpoint
            stream_url = self.get_stream_url()
            response = self.session.get(stream_url, timeout=5, stream=True)
            response.close()
            return response.status_code == 200
        except:
            return False
    
    def get_camera_status(self) -> Dict[str, Any]:
        """
        Get current camera status and settings
        
        Returns:
            Dict containing camera status information
        """
        try:
            # This would be a backend endpoint to get camera status
            # For now, we'll return basic status
            return {
                "streaming": self.check_stream_status(),
                "recording": False,  # This would need backend endpoint
                "connected": True    # This would need backend endpoint
            }
        except Exception as e:
            logger.error(f"Failed to get camera status: {e}")
            return {
                "streaming": False,
                "recording": False,
                "connected": False,
                "error": str(e)
            }


# Singleton instance
camera_service = CameraService()