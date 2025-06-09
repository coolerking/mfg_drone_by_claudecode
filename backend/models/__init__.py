"""
Pydanticモデル定義
リクエスト・レスポンス・エラーコードなどのデータモデル
"""

from .requests import *
from .responses import *

__all__ = [
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
    "MissionPadDetectionDirectionRequest",
    "MissionPadGoXYZRequest",
    "TrackingStartRequest",
    "ModelTrainRequest",
    
    # Response models
    "StatusResponse",
    "ErrorResponse",
    "DroneStatus",
    "BatteryResponse",
    "HeightResponse",
    "TemperatureResponse",
    "FlightTimeResponse",
    "BarometerResponse",
    "DistanceToFResponse",
    "AccelerationResponse",
    "VelocityResponse",
    "AttitudeResponse",
    "CommandResponse",
    "MissionPadStatusResponse",
    "TrackingStatusResponse",
    "ModelListResponse",
    
    # Data models
    "AccelerationData",
    "VelocityData",
    "AttitudeData",
    "TrackingPosition",
    "ModelInfo",
    
    # Error codes
    "ErrorCode",
]