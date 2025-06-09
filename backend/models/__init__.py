"""
Pydantic models for FastAPI application
OpenAPI仕様に準拠したリクエスト・レスポンスモデル
"""

from .requests import *
from .responses import *

__all__ = [
    # Response models
    "StatusResponse",
    "ErrorResponse", 
    "ErrorCode",
    "DroneStatus",
    "AccelerationData",
    "VelocityData", 
    "AttitudeData",
    "BatteryResponse",
    "HeightResponse",
    "TemperatureResponse",
    "FlightTimeResponse",
    "BarometerResponse",
    "DistanceTofResponse",
    "AccelerationResponse",
    "VelocityResponse",
    "AttitudeResponse",
    "TrackingStatusResponse",
    "MissionPadStatusResponse",
    "ModelListResponse",
    
    # Request models
    "MoveRequest",
    "RotateRequest",
    "FlipRequest",
    "GoXYZRequest",
    "CurveXYZRequest",
    "RCControlRequest",
    "CameraSettingsRequest",
    "WiFiRequest",
    "CommandRequest",
    "SpeedRequest",
    "MissionPadDetectionRequest",
    "MissionPadGoXYZRequest",
    "TrackingStartRequest",
    "ModelTrainRequest",
]