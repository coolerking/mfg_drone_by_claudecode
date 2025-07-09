"""
Data models for MCP Drone Client SDK
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field


class MCPClientConfig(BaseModel):
    """Configuration for MCP Client"""
    base_url: str = Field(..., description="MCP server base URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    bearer_token: Optional[str] = Field(None, description="Bearer token for authentication")
    timeout: float = Field(30.0, description="Request timeout in seconds")


class NaturalLanguageCommand(BaseModel):
    """Natural language command"""
    command: str = Field(..., description="Natural language command")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    options: Optional[Dict[str, Any]] = Field(None, description="Execution options")


class BatchCommand(BaseModel):
    """Batch command execution"""
    commands: List[NaturalLanguageCommand] = Field(..., description="List of commands to execute")
    execution_mode: Literal["sequential", "parallel"] = Field("sequential", description="Execution mode")
    stop_on_error: bool = Field(True, description="Stop on first error")


class CommandResponse(BaseModel):
    """Command execution response"""
    success: bool = Field(..., description="Execution success flag")
    message: str = Field(..., description="Response message")
    parsed_intent: Optional[Dict[str, Any]] = Field(None, description="Parsed intent")
    execution_details: Optional[Dict[str, Any]] = Field(None, description="Execution details")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data")
    timestamp: datetime = Field(..., description="Execution timestamp")


class BatchCommandResponse(BaseModel):
    """Batch command execution response"""
    success: bool = Field(..., description="Overall success flag")
    message: str = Field(..., description="Overall response message")
    results: List[CommandResponse] = Field(..., description="Individual command results")
    summary: Dict[str, Any] = Field(..., description="Execution summary")
    timestamp: datetime = Field(..., description="Execution timestamp")


class DroneInfo(BaseModel):
    """Drone information"""
    id: str = Field(..., description="Drone ID")
    name: str = Field(..., description="Drone name")
    type: Literal["real", "dummy"] = Field(..., description="Drone type")
    status: Literal["available", "connected", "busy", "offline", "error"] = Field(..., description="Drone status")
    capabilities: List[str] = Field(..., description="Drone capabilities")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")


class DroneListResponse(BaseModel):
    """Drone list response"""
    drones: List[DroneInfo] = Field(..., description="List of drones")
    count: int = Field(..., description="Number of drones")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(..., description="Response timestamp")


class DroneStatusResponse(BaseModel):
    """Drone status response"""
    drone_id: str = Field(..., description="Drone ID")
    status: Dict[str, Any] = Field(..., description="Drone status details")
    message: Optional[str] = Field(None, description="Status message")
    timestamp: datetime = Field(..., description="Status timestamp")


class TakeoffCommand(BaseModel):
    """Takeoff command"""
    target_height: Optional[int] = Field(None, ge=20, le=300, description="Target height in cm")
    safety_check: bool = Field(True, description="Perform safety check")


class MoveCommand(BaseModel):
    """Move command"""
    direction: Literal["up", "down", "left", "right", "forward", "back"] = Field(..., description="Movement direction")
    distance: int = Field(..., ge=20, le=500, description="Movement distance in cm")
    speed: Optional[int] = Field(None, ge=10, le=100, description="Movement speed in cm/s")


class RotateCommand(BaseModel):
    """Rotate command"""
    direction: Literal["clockwise", "counter_clockwise", "left", "right"] = Field(..., description="Rotation direction")
    angle: int = Field(..., ge=1, le=360, description="Rotation angle in degrees")


class AltitudeCommand(BaseModel):
    """Altitude command"""
    target_height: int = Field(..., ge=20, le=300, description="Target height in cm")
    mode: Literal["absolute", "relative"] = Field("absolute", description="Altitude mode")


class PhotoCommand(BaseModel):
    """Photo command"""
    filename: Optional[str] = Field(None, description="Photo filename")
    quality: Literal["high", "medium", "low"] = Field("high", description="Photo quality")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class StreamingCommand(BaseModel):
    """Streaming command"""
    action: Literal["start", "stop"] = Field(..., description="Streaming action")
    quality: Literal["high", "medium", "low"] = Field("medium", description="Streaming quality")
    resolution: Literal["720p", "480p", "360p"] = Field("720p", description="Streaming resolution")


class LearningDataCommand(BaseModel):
    """Learning data collection command"""
    object_name: str = Field(..., description="Object name for learning")
    capture_positions: List[Literal["front", "back", "left", "right", "top", "bottom"]] = Field(
        ["front", "back", "left", "right"], description="Capture positions"
    )
    movement_distance: int = Field(30, ge=20, le=100, description="Movement distance in cm")
    photos_per_position: int = Field(3, ge=1, le=10, description="Photos per position")
    dataset_name: Optional[str] = Field(None, description="Dataset name")


class DetectionCommand(BaseModel):
    """Object detection command"""
    drone_id: str = Field(..., description="Drone ID")
    model_id: Optional[str] = Field(None, description="Model ID")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Confidence threshold")


class TrackingCommand(BaseModel):
    """Object tracking command"""
    action: Literal["start", "stop"] = Field(..., description="Tracking action")
    drone_id: str = Field(..., description="Drone ID")
    model_id: Optional[str] = Field(None, description="Model ID")
    follow_distance: int = Field(200, ge=50, le=500, description="Follow distance in cm")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Confidence threshold")


class OperationResponse(BaseModel):
    """Operation response"""
    success: bool = Field(..., description="Operation success flag")
    message: str = Field(..., description="Response message")
    operation_id: Optional[str] = Field(None, description="Operation ID")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(..., description="Response timestamp")


class PhotoResponse(BaseModel):
    """Photo response"""
    success: bool = Field(..., description="Photo operation success")
    message: str = Field(..., description="Response message")
    photo: Optional[Dict[str, Any]] = Field(None, description="Photo information")
    timestamp: datetime = Field(..., description="Response timestamp")


class LearningDataResponse(BaseModel):
    """Learning data collection response"""
    success: bool = Field(..., description="Collection success flag")
    message: str = Field(..., description="Response message")
    dataset: Optional[Dict[str, Any]] = Field(None, description="Dataset information")
    execution_summary: Optional[Dict[str, Any]] = Field(None, description="Execution summary")
    timestamp: datetime = Field(..., description="Response timestamp")


class DetectionResponse(BaseModel):
    """Object detection response"""
    success: bool = Field(..., description="Detection success flag")
    message: str = Field(..., description="Response message")
    detections: List[Dict[str, Any]] = Field(..., description="Detection results")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(..., description="Response timestamp")


class SystemStatusResponse(BaseModel):
    """System status response"""
    mcp_server: Dict[str, Any] = Field(..., description="MCP server status")
    backend_system: Dict[str, Any] = Field(..., description="Backend system status")
    connected_drones: int = Field(..., description="Connected drones count")
    active_operations: int = Field(..., description="Active operations count")
    system_health: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="System health")
    timestamp: datetime = Field(..., description="Status timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "unhealthy"] = Field(..., description="Health status")
    checks: List[Dict[str, Any]] = Field(..., description="Health check details")
    timestamp: datetime = Field(..., description="Check timestamp")


class MCPError(BaseModel):
    """MCP error response"""
    error: bool = Field(True, description="Error flag")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")