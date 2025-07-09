"""
MCP Drone Client SDK for Python
Python SDK for MCP Drone Control Server
"""

from .client import MCPClient, MCPClientError
from .models import *

__version__ = "1.0.0"
__author__ = "MFG Drone Team"
__email__ = "team@mfg-drone.com"

__all__ = [
    "MCPClient",
    "MCPClientError",
    # Models
    "NaturalLanguageCommand",
    "BatchCommand",
    "CommandResponse",
    "BatchCommandResponse",
    "DroneInfo",
    "DroneListResponse",
    "DroneStatusResponse",
    "TakeoffCommand",
    "MoveCommand",
    "RotateCommand",
    "AltitudeCommand",
    "PhotoCommand",
    "StreamingCommand",
    "LearningDataCommand",
    "DetectionCommand",
    "TrackingCommand",
    "OperationResponse",
    "PhotoResponse",
    "LearningDataResponse",
    "DetectionResponse",
    "SystemStatusResponse",
    "HealthResponse",
    "MCPError",
]