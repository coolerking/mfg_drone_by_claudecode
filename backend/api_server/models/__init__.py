"""
Pydantic models for MFG Drone Backend API
All models are based on the OpenAPI specification
"""

from .common_models import SuccessResponse, ErrorResponse
from .drone_models import (
    Drone, DroneStatus, Attitude, MoveCommand, RotateCommand, Photo
)

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "Drone",
    "DroneStatus", 
    "Attitude",
    "MoveCommand",
    "RotateCommand",
    "Photo"
]