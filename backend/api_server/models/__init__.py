"""
Pydantic models for MFG Drone Backend API
All models are based on the OpenAPI specification
"""

from .common_models import SuccessResponse, ErrorResponse
from .drone_models import (
    Drone, DroneStatus, Attitude, MoveCommand, RotateCommand, Photo
)
from .vision_models import (
    BoundingBox, Detection, DetectionRequest, DetectionResult,
    StartTrackingRequest, TrackingStatus, Dataset, CreateDatasetRequest,
    DatasetImage
)
from .model_models import (
    TrainingParams, Model, TrainModelRequest, TrainingJob, SystemStatus
)

__all__ = [
    # Common models
    "SuccessResponse",
    "ErrorResponse",
    # Drone models
    "Drone",
    "DroneStatus", 
    "Attitude",
    "MoveCommand",
    "RotateCommand",
    "Photo",
    # Vision models
    "BoundingBox",
    "Detection",
    "DetectionRequest",
    "DetectionResult",
    "StartTrackingRequest",
    "TrackingStatus",
    "Dataset",
    "CreateDatasetRequest",
    "DatasetImage",
    # Model management models
    "TrainingParams",
    "Model",
    "TrainModelRequest",
    "TrainingJob",
    "SystemStatus"
]