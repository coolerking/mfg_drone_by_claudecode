"""
Command Router for MCP Server
Maps parsed intents to backend API calls
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..models.command_models import ParsedIntent, CommandResponse, ExecutionDetails
from ..models.drone_models import OperationResponse
from ..models.camera_models import PhotoResponse, DetectionResponse
from ..models.system_models import ErrorCodes, ApiError
from .backend_client import BackendClient, BackendClientError
from config.logging import get_logger


logger = get_logger(__name__)


class CommandRouter:
    """Command router for mapping intents to API calls"""
    
    def __init__(self, backend_client: BackendClient):
        """Initialize command router"""
        self.backend_client = backend_client
        
        # Action mappings
        self.action_mappings = {
            # Connection actions
            "connect": self._execute_connect,
            "disconnect": self._execute_disconnect,
            
            # Flight control actions
            "takeoff": self._execute_takeoff,
            "land": self._execute_land,
            "emergency": self._execute_emergency,
            
            # Movement actions
            "move": self._execute_move,
            "rotate": self._execute_rotate,
            "altitude": self._execute_altitude,
            
            # Camera actions
            "photo": self._execute_photo,
            "streaming": self._execute_streaming,
            "learning": self._execute_learning_data,
            
            # Vision actions
            "detection": self._execute_detection,
            "tracking": self._execute_tracking,
            
            # System actions
            "status": self._execute_status,
            "health": self._execute_health
        }
        
        logger.info("Command router initialized")
    
    async def execute_command(self, parsed_intent: ParsedIntent) -> CommandResponse:
        """Execute command based on parsed intent"""
        start_time = datetime.now()
        backend_calls = []
        
        try:
            logger.info(f"Executing command: {parsed_intent.action}")
            
            # Get executor function
            executor = self.action_mappings.get(parsed_intent.action)
            if not executor:
                raise ValueError(f"Unknown action: {parsed_intent.action}")
            
            # Execute command
            result = await executor(parsed_intent.parameters)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create execution details
            execution_details = ExecutionDetails(
                backend_calls=backend_calls,
                execution_time=execution_time
            )
            
            # Create response
            response = CommandResponse(
                success=True,
                message=f"Command '{parsed_intent.action}' executed successfully",
                parsed_intent=parsed_intent,
                execution_details=execution_details,
                result=result
            )
            
            logger.info(f"Command executed successfully in {execution_time:.2f}s")
            return response
            
        except BackendClientError as e:
            logger.error(f"Backend error executing command: {e.message}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CommandResponse(
                success=False,
                message=f"Backend error: {e.message}",
                parsed_intent=parsed_intent,
                execution_details=ExecutionDetails(
                    backend_calls=backend_calls,
                    execution_time=execution_time
                ),
                result={"error_code": e.error_code}
            )
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CommandResponse(
                success=False,
                message=f"Error executing command: {str(e)}",
                parsed_intent=parsed_intent,
                execution_details=ExecutionDetails(
                    backend_calls=backend_calls,
                    execution_time=execution_time
                ),
                result={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
            )
    
    # Connection actions
    async def _execute_connect(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute connect command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for connection")
        
        result = await self.backend_client.connect_drone(drone_id)
        return {"operation": "connect", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_disconnect(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute disconnect command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for disconnection")
        
        result = await self.backend_client.disconnect_drone(drone_id)
        return {"operation": "disconnect", "drone_id": drone_id, "result": result.dict()}
    
    # Flight control actions
    async def _execute_takeoff(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute takeoff command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for takeoff")
        
        target_height = parameters.get("height")
        result = await self.backend_client.takeoff_drone(drone_id, target_height)
        return {"operation": "takeoff", "drone_id": drone_id, "target_height": target_height, "result": result.dict()}
    
    async def _execute_land(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute land command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for landing")
        
        result = await self.backend_client.land_drone(drone_id)
        return {"operation": "land", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_emergency(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency stop command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for emergency stop")
        
        result = await self.backend_client.emergency_stop(drone_id)
        return {"operation": "emergency", "drone_id": drone_id, "result": result.dict()}
    
    # Movement actions
    async def _execute_move(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute move command"""
        drone_id = parameters.get("drone_id")
        direction = parameters.get("direction")
        distance = parameters.get("distance")
        speed = parameters.get("speed")
        
        if not drone_id:
            raise ValueError("Drone ID is required for movement")
        if not direction:
            raise ValueError("Direction is required for movement")
        if not distance:
            raise ValueError("Distance is required for movement")
        
        result = await self.backend_client.move_drone(drone_id, direction, distance, speed)
        return {
            "operation": "move",
            "drone_id": drone_id,
            "direction": direction,
            "distance": distance,
            "speed": speed,
            "result": result.dict()
        }
    
    async def _execute_rotate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rotate command"""
        drone_id = parameters.get("drone_id")
        direction = parameters.get("direction")
        angle = parameters.get("angle")
        
        if not drone_id:
            raise ValueError("Drone ID is required for rotation")
        if not direction:
            raise ValueError("Direction is required for rotation")
        if not angle:
            raise ValueError("Angle is required for rotation")
        
        result = await self.backend_client.rotate_drone(drone_id, direction, angle)
        return {
            "operation": "rotate",
            "drone_id": drone_id,
            "direction": direction,
            "angle": angle,
            "result": result.dict()
        }
    
    async def _execute_altitude(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute altitude command"""
        drone_id = parameters.get("drone_id")
        height = parameters.get("height")
        mode = parameters.get("mode", "absolute")
        
        if not drone_id:
            raise ValueError("Drone ID is required for altitude adjustment")
        if not height:
            raise ValueError("Height is required for altitude adjustment")
        
        result = await self.backend_client.set_altitude(drone_id, height, mode)
        return {
            "operation": "altitude",
            "drone_id": drone_id,
            "height": height,
            "mode": mode,
            "result": result.dict()
        }
    
    # Camera actions
    async def _execute_photo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute photo command"""
        drone_id = parameters.get("drone_id")
        filename = parameters.get("filename")
        quality = parameters.get("quality", "high")
        
        if not drone_id:
            raise ValueError("Drone ID is required for photo capture")
        
        result = await self.backend_client.take_photo(drone_id, filename, quality)
        return {
            "operation": "photo",
            "drone_id": drone_id,
            "filename": filename,
            "quality": quality,
            "result": result.dict()
        }
    
    async def _execute_streaming(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute streaming command"""
        drone_id = parameters.get("drone_id")
        action = parameters.get("action", "start")
        quality = parameters.get("quality", "medium")
        resolution = parameters.get("resolution", "720p")
        
        if not drone_id:
            raise ValueError("Drone ID is required for streaming control")
        
        result = await self.backend_client.control_streaming(drone_id, action, quality, resolution)
        return {
            "operation": "streaming",
            "drone_id": drone_id,
            "action": action,
            "quality": quality,
            "resolution": resolution,
            "result": result.dict()
        }
    
    async def _execute_learning_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute learning data collection command"""
        drone_id = parameters.get("drone_id")
        object_name = parameters.get("object_name")
        
        if not drone_id:
            raise ValueError("Drone ID is required for learning data collection")
        if not object_name:
            raise ValueError("Object name is required for learning data collection")
        
        result = await self.backend_client.collect_learning_data(drone_id, object_name, **parameters)
        return {
            "operation": "learning_data",
            "drone_id": drone_id,
            "object_name": object_name,
            "result": result
        }
    
    # Vision actions
    async def _execute_detection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute detection command"""
        drone_id = parameters.get("drone_id")
        model_id = parameters.get("model_id")
        confidence_threshold = parameters.get("confidence_threshold", 0.5)
        
        if not drone_id:
            raise ValueError("Drone ID is required for object detection")
        
        result = await self.backend_client.detect_objects(drone_id, model_id, confidence_threshold)
        return {
            "operation": "detection",
            "drone_id": drone_id,
            "model_id": model_id,
            "confidence_threshold": confidence_threshold,
            "result": [detection.dict() for detection in result]
        }
    
    async def _execute_tracking(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tracking command"""
        drone_id = parameters.get("drone_id")
        action = parameters.get("action", "start")
        
        if not drone_id:
            raise ValueError("Drone ID is required for object tracking")
        
        result = await self.backend_client.control_tracking(action, drone_id, **parameters)
        return {
            "operation": "tracking",
            "drone_id": drone_id,
            "action": action,
            "result": result.dict()
        }
    
    # System actions
    async def _execute_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute status command"""
        drone_id = parameters.get("drone_id")
        
        if drone_id:
            # Get specific drone status
            result = await self.backend_client.get_drone_status(drone_id)
            return {
                "operation": "status",
                "drone_id": drone_id,
                "result": result.dict()
            }
        else:
            # Get system status
            result = await self.backend_client.get_system_status()
            return {
                "operation": "system_status",
                "result": result
            }
    
    async def _execute_health(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health check command"""
        result = await self.backend_client.health_check()
        return {
            "operation": "health_check",
            "result": result
        }