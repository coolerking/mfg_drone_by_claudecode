"""
MCP Drone Client SDK Main Client
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from urllib.parse import urljoin, urlparse

import httpx
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .models import (
    MCPClientConfig,
    NaturalLanguageCommand,
    BatchCommand,
    CommandResponse,
    BatchCommandResponse,
    DroneListResponse,
    DroneStatusResponse,
    TakeoffCommand,
    MoveCommand,
    RotateCommand,
    AltitudeCommand,
    PhotoCommand,
    StreamingCommand,
    LearningDataCommand,
    DetectionCommand,
    TrackingCommand,
    OperationResponse,
    PhotoResponse,
    LearningDataResponse,
    DetectionResponse,
    SystemStatusResponse,
    HealthResponse,
    MCPError,
)

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """MCP Client Error"""
    
    def __init__(self, error_data: Dict[str, Any]):
        self.error_code = error_data.get("error_code", "UNKNOWN_ERROR")
        self.message = error_data.get("message", "Unknown error")
        self.details = error_data.get("details")
        self.timestamp = error_data.get("timestamp")
        super().__init__(self.message)


class MCPClient:
    """MCP Drone Client SDK"""
    
    def __init__(self, config: MCPClientConfig):
        """Initialize MCP Client"""
        self.config = config
        self._client = None
        self._websocket = None
        self._websocket_task = None
        
        # Setup headers
        self._headers = {
            "Content-Type": "application/json",
        }
        
        if config.api_key:
            self._headers["X-API-Key"] = config.api_key
        
        if config.bearer_token:
            self._headers["Authorization"] = f"Bearer {config.bearer_token}"
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=self._headers,
                timeout=self.config.timeout,
            )
    
    async def close(self):
        """Close client and cleanup resources"""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        
        if self._websocket_task:
            self._websocket_task.cancel()
            try:
                await self._websocket_task
            except asyncio.CancelledError:
                pass
            self._websocket_task = None
        
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request"""
        await self._ensure_client()
        
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                raise MCPClientError(error_data)
            except json.JSONDecodeError:
                raise MCPClientError({
                    "error_code": f"HTTP_{e.response.status_code}",
                    "message": f"HTTP error {e.response.status_code}: {e.response.text}",
                    "timestamp": None
                })
        except httpx.RequestError as e:
            raise MCPClientError({
                "error_code": "REQUEST_ERROR",
                "message": f"Request failed: {str(e)}",
                "timestamp": None
            })
    
    # Natural Language Commands
    async def execute_command(self, command: NaturalLanguageCommand) -> CommandResponse:
        """Execute natural language command"""
        data = await self._request("POST", "/mcp/command", json=command.dict())
        return CommandResponse(**data)
    
    async def execute_batch_command(self, batch_command: BatchCommand) -> BatchCommandResponse:
        """Execute batch natural language commands"""
        data = await self._request("POST", "/mcp/command/batch", json=batch_command.dict())
        return BatchCommandResponse(**data)
    
    # Drone Query APIs
    async def get_drones(self) -> DroneListResponse:
        """Get list of registered drones"""
        data = await self._request("GET", "/mcp/drones")
        return DroneListResponse(**data)
    
    async def get_available_drones(self) -> DroneListResponse:
        """Get list of available drones"""
        data = await self._request("GET", "/mcp/drones/available")
        return DroneListResponse(**data)
    
    async def get_drone_status(self, drone_id: str) -> DroneStatusResponse:
        """Get drone status"""
        data = await self._request("GET", f"/mcp/drones/{drone_id}/status")
        return DroneStatusResponse(**data)
    
    # Drone Control APIs
    async def connect_drone(self, drone_id: str) -> OperationResponse:
        """Connect to drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/connect")
        return OperationResponse(**data)
    
    async def disconnect_drone(self, drone_id: str) -> OperationResponse:
        """Disconnect from drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/disconnect")
        return OperationResponse(**data)
    
    async def takeoff(self, drone_id: str, command: Optional[TakeoffCommand] = None) -> OperationResponse:
        """Takeoff drone"""
        json_data = command.dict() if command else {}
        data = await self._request("POST", f"/mcp/drones/{drone_id}/takeoff", json=json_data)
        return OperationResponse(**data)
    
    async def land(self, drone_id: str) -> OperationResponse:
        """Land drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/land")
        return OperationResponse(**data)
    
    async def move_drone(self, drone_id: str, command: MoveCommand) -> OperationResponse:
        """Move drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/move", json=command.dict())
        return OperationResponse(**data)
    
    async def rotate_drone(self, drone_id: str, command: RotateCommand) -> OperationResponse:
        """Rotate drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/rotate", json=command.dict())
        return OperationResponse(**data)
    
    async def emergency_stop(self, drone_id: str) -> OperationResponse:
        """Emergency stop drone"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/emergency")
        return OperationResponse(**data)
    
    async def set_altitude(self, drone_id: str, command: AltitudeCommand) -> OperationResponse:
        """Set drone altitude"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/altitude", json=command.dict())
        return OperationResponse(**data)
    
    # Camera APIs
    async def take_photo(self, drone_id: str, command: Optional[PhotoCommand] = None) -> PhotoResponse:
        """Take photo"""
        json_data = command.dict() if command else {}
        data = await self._request("POST", f"/mcp/drones/{drone_id}/camera/photo", json=json_data)
        return PhotoResponse(**data)
    
    async def control_streaming(self, drone_id: str, command: StreamingCommand) -> OperationResponse:
        """Control camera streaming"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/camera/streaming", json=command.dict())
        return OperationResponse(**data)
    
    async def collect_learning_data(self, drone_id: str, command: LearningDataCommand) -> LearningDataResponse:
        """Collect learning data"""
        data = await self._request("POST", f"/mcp/drones/{drone_id}/learning/collect", json=command.dict())
        return LearningDataResponse(**data)
    
    # Vision APIs
    async def detect_objects(self, command: DetectionCommand) -> DetectionResponse:
        """Detect objects"""
        data = await self._request("POST", "/mcp/vision/detection", json=command.dict())
        return DetectionResponse(**data)
    
    async def control_tracking(self, command: TrackingCommand) -> OperationResponse:
        """Control object tracking"""
        data = await self._request("POST", "/mcp/vision/tracking", json=command.dict())
        return OperationResponse(**data)
    
    # System APIs
    async def get_system_status(self) -> SystemStatusResponse:
        """Get system status"""
        data = await self._request("GET", "/mcp/system/status")
        return SystemStatusResponse(**data)
    
    async def get_health_check(self) -> HealthResponse:
        """Get health check"""
        data = await self._request("GET", "/mcp/system/health")
        return HealthResponse(**data)
    
    # WebSocket Support
    async def connect_websocket(
        self,
        on_message: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
        on_connect: Optional[Callable[[], Awaitable[None]]] = None,
        on_disconnect: Optional[Callable[[], Awaitable[None]]] = None,
    ):
        """Connect to WebSocket"""
        if self._websocket:
            logger.warning("WebSocket already connected")
            return
        
        # Build WebSocket URL
        parsed_url = urlparse(self.config.base_url)
        ws_scheme = "wss" if parsed_url.scheme == "https" else "ws"
        ws_url = f"{ws_scheme}://{parsed_url.netloc}/ws"
        
        # Add headers for WebSocket
        extra_headers = {}
        if self.config.api_key:
            extra_headers["X-API-Key"] = self.config.api_key
        if self.config.bearer_token:
            extra_headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        
        async def websocket_handler():
            try:
                async with websockets.connect(ws_url, extra_headers=extra_headers) as websocket:
                    self._websocket = websocket
                    
                    if on_connect:
                        await on_connect()
                    
                    logger.info("WebSocket connected")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if on_message:
                                await on_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse WebSocket message: {e}")
                        except Exception as e:
                            logger.error(f"Error in WebSocket message handler: {e}")
                            if on_error:
                                await on_error(e)
                    
            except ConnectionClosed:
                logger.info("WebSocket connection closed")
            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                if on_error:
                    await on_error(e)
            except Exception as e:
                logger.error(f"Unexpected WebSocket error: {e}")
                if on_error:
                    await on_error(e)
            finally:
                self._websocket = None
                if on_disconnect:
                    await on_disconnect()
        
        self._websocket_task = asyncio.create_task(websocket_handler())
    
    async def disconnect_websocket(self):
        """Disconnect WebSocket"""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        
        if self._websocket_task:
            self._websocket_task.cancel()
            try:
                await self._websocket_task
            except asyncio.CancelledError:
                pass
            self._websocket_task = None
    
    async def send_websocket_message(self, message: Dict[str, Any]):
        """Send message via WebSocket"""
        if not self._websocket:
            raise MCPClientError({
                "error_code": "WEBSOCKET_NOT_CONNECTED",
                "message": "WebSocket not connected",
                "timestamp": None
            })
        
        try:
            await self._websocket.send(json.dumps(message))
        except Exception as e:
            raise MCPClientError({
                "error_code": "WEBSOCKET_SEND_ERROR",
                "message": f"Failed to send WebSocket message: {str(e)}",
                "timestamp": None
            })
    
    # Utility Methods
    async def wait_for_operation(self, operation_id: str, max_wait_time: float = 30.0) -> bool:
        """Wait for operation to complete"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < max_wait_time:
            try:
                # This would need to be implemented based on the actual API
                # For now, just simulate a delay
                await asyncio.sleep(1.0)
                return True
            except Exception:
                # Continue waiting
                pass
        
        return False
    
    async def ping(self) -> bool:
        """Ping the server"""
        try:
            await self.get_health_check()
            return True
        except Exception:
            return False


# Convenience function for creating client
def create_client(
    base_url: str,
    api_key: Optional[str] = None,
    bearer_token: Optional[str] = None,
    timeout: float = 30.0,
) -> MCPClient:
    """Create MCP Client instance"""
    config = MCPClientConfig(
        base_url=base_url,
        api_key=api_key,
        bearer_token=bearer_token,
        timeout=timeout,
    )
    return MCPClient(config)