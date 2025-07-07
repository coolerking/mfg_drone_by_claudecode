"""
Backend API client for MCP Server
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio

from ..models.drone_models import DroneInfo, DroneStatusDetail, OperationResponse
from ..models.camera_models import PhotoInfo, Detection
from ..models.system_models import ErrorCodes, ApiError
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class BackendClientError(Exception):
    """Backend client error"""
    def __init__(self, message: str, error_code: str = ErrorCodes.BACKEND_CONNECTION_ERROR):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class BackendClient:
    """Backend API client"""
    
    def __init__(self, base_url: str = None, timeout: int = None, api_key: str = None):
        """Initialize backend client"""
        self.base_url = base_url or settings.backend_api_url
        self.timeout = timeout or settings.backend_api_timeout
        self.api_key = api_key or settings.backend_api_key
        
        # Create HTTP client
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=headers
        )
        
        logger.info("Backend client initialized", base_url=self.base_url)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("Backend client closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend API"""
        try:
            logger.debug(f"Making {method} request to {endpoint}")
            response = await self.client.request(method, endpoint, **kwargs)
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("detail", f"HTTP {response.status_code}")
                logger.error(f"Backend API error: {error_message}")
                raise BackendClientError(error_message, ErrorCodes.BACKEND_CONNECTION_ERROR)
            
            return response.json()
            
        except httpx.TimeoutException:
            logger.error("Backend API timeout")
            raise BackendClientError("Backend API timeout", ErrorCodes.BACKEND_TIMEOUT)
        except httpx.ConnectError:
            logger.error("Backend API connection error")
            raise BackendClientError("Backend API connection error", ErrorCodes.BACKEND_CONNECTION_ERROR)
        except Exception as e:
            logger.error(f"Backend API error: {str(e)}")
            raise BackendClientError(f"Backend API error: {str(e)}", ErrorCodes.BACKEND_CONNECTION_ERROR)
    
    # Drone Management Methods
    async def get_drones(self) -> List[DroneInfo]:
        """Get all registered drones"""
        data = await self._request("GET", "/drones")
        return [DroneInfo(**drone) for drone in data.get("drones", [])]
    
    async def get_available_drones(self) -> List[DroneInfo]:
        """Get available drones"""
        data = await self._request("GET", "/drones/available")
        return [DroneInfo(**drone) for drone in data.get("drones", [])]
    
    async def get_drone_status(self, drone_id: str) -> DroneStatusDetail:
        """Get drone status"""
        data = await self._request("GET", f"/drones/{drone_id}/status")
        return DroneStatusDetail(**data["status"])
    
    async def connect_drone(self, drone_id: str) -> OperationResponse:
        """Connect to drone"""
        data = await self._request("POST", f"/drones/{drone_id}/connect")
        return OperationResponse(**data)
    
    async def disconnect_drone(self, drone_id: str) -> OperationResponse:
        """Disconnect from drone"""
        data = await self._request("POST", f"/drones/{drone_id}/disconnect")
        return OperationResponse(**data)
    
    async def takeoff_drone(self, drone_id: str, target_height: Optional[int] = None) -> OperationResponse:
        """Take off drone"""
        payload = {}
        if target_height:
            payload["target_height"] = target_height
        
        data = await self._request("POST", f"/drones/{drone_id}/takeoff", json=payload)
        return OperationResponse(**data)
    
    async def land_drone(self, drone_id: str) -> OperationResponse:
        """Land drone"""
        data = await self._request("POST", f"/drones/{drone_id}/land")
        return OperationResponse(**data)
    
    async def move_drone(self, drone_id: str, direction: str, distance: int, speed: Optional[int] = None) -> OperationResponse:
        """Move drone"""
        payload = {
            "direction": direction,
            "distance": distance
        }
        if speed:
            payload["speed"] = speed
        
        data = await self._request("POST", f"/drones/{drone_id}/move", json=payload)
        return OperationResponse(**data)
    
    async def rotate_drone(self, drone_id: str, direction: str, angle: int) -> OperationResponse:
        """Rotate drone"""
        payload = {
            "direction": direction,
            "angle": angle
        }
        data = await self._request("POST", f"/drones/{drone_id}/rotate", json=payload)
        return OperationResponse(**data)
    
    async def set_altitude(self, drone_id: str, target_height: int, mode: str = "absolute") -> OperationResponse:
        """Set drone altitude"""
        payload = {
            "target_height": target_height,
            "mode": mode
        }
        data = await self._request("POST", f"/drones/{drone_id}/altitude", json=payload)
        return OperationResponse(**data)
    
    async def emergency_stop(self, drone_id: str) -> OperationResponse:
        """Emergency stop drone"""
        data = await self._request("POST", f"/drones/{drone_id}/emergency")
        return OperationResponse(**data)
    
    # Camera Methods
    async def take_photo(self, drone_id: str, filename: Optional[str] = None, quality: str = "high") -> PhotoInfo:
        """Take photo"""
        payload = {
            "quality": quality
        }
        if filename:
            payload["filename"] = filename
        
        data = await self._request("POST", f"/drones/{drone_id}/camera/photo", json=payload)
        return PhotoInfo(**data["photo"])
    
    async def control_streaming(self, drone_id: str, action: str, quality: str = "medium", resolution: str = "720p") -> OperationResponse:
        """Control camera streaming"""
        payload = {
            "action": action,
            "quality": quality,
            "resolution": resolution
        }
        data = await self._request("POST", f"/drones/{drone_id}/camera/streaming", json=payload)
        return OperationResponse(**data)
    
    async def collect_learning_data(self, drone_id: str, object_name: str, **kwargs) -> Dict[str, Any]:
        """Collect learning data"""
        payload = {
            "object_name": object_name,
            **kwargs
        }
        data = await self._request("POST", f"/drones/{drone_id}/learning/collect", json=payload)
        return data
    
    # Vision Methods
    async def detect_objects(self, drone_id: str, model_id: Optional[str] = None, confidence_threshold: float = 0.5) -> List[Detection]:
        """Detect objects"""
        payload = {
            "drone_id": drone_id,
            "confidence_threshold": confidence_threshold
        }
        if model_id:
            payload["model_id"] = model_id
        
        data = await self._request("POST", "/vision/detection", json=payload)
        return [Detection(**detection) for detection in data.get("detections", [])]
    
    async def control_tracking(self, action: str, drone_id: str, **kwargs) -> OperationResponse:
        """Control object tracking"""
        payload = {
            "action": action,
            "drone_id": drone_id,
            **kwargs
        }
        data = await self._request("POST", "/vision/tracking", json=payload)
        return OperationResponse(**data)
    
    # System Methods
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return await self._request("GET", "/system/status")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return await self._request("GET", "/system/health")


# Global backend client instance
backend_client = BackendClient()