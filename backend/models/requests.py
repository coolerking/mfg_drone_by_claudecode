"""
リクエストモデル定義
OpenAPI仕様に基づいたAPIリクエストのPydanticモデル
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum


# Movement関連
class DirectionEnum(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACK = "back"


class RotationDirectionEnum(str, Enum):
    CLOCKWISE = "clockwise"
    COUNTER_CLOCKWISE = "counter_clockwise"


class FlipDirectionEnum(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACK = "back"


class MoveRequest(BaseModel):
    direction: DirectionEnum = Field(..., description="移動方向")
    distance: int = Field(..., ge=20, le=500, description="移動距離(cm)")


class RotateRequest(BaseModel):
    direction: RotationDirectionEnum = Field(..., description="回転方向")
    angle: int = Field(..., ge=1, le=360, description="回転角度(度)")


class FlipRequest(BaseModel):
    direction: FlipDirectionEnum = Field(..., description="宙返り方向")


# Advanced Movement関連
class GoXYZRequest(BaseModel):
    x: int = Field(..., ge=-500, le=500, description="X座標(cm)")
    y: int = Field(..., ge=-500, le=500, description="Y座標(cm)")
    z: int = Field(..., ge=-500, le=500, description="Z座標(cm)")
    speed: int = Field(..., ge=10, le=100, description="速度(cm/s)")


class CurveXYZRequest(BaseModel):
    x1: int = Field(..., ge=-500, le=500, description="中間点X座標(cm)")
    y1: int = Field(..., ge=-500, le=500, description="中間点Y座標(cm)")
    z1: int = Field(..., ge=-500, le=500, description="中間点Z座標(cm)")
    x2: int = Field(..., ge=-500, le=500, description="終点X座標(cm)")
    y2: int = Field(..., ge=-500, le=500, description="終点Y座標(cm)")
    z2: int = Field(..., ge=-500, le=500, description="終点Z座標(cm)")
    speed: int = Field(..., ge=10, le=60, description="速度(cm/s)")


class RCControlRequest(BaseModel):
    left_right_velocity: int = Field(..., ge=-100, le=100, description="左右速度(%)")
    forward_backward_velocity: int = Field(..., ge=-100, le=100, description="前後速度(%)")
    up_down_velocity: int = Field(..., ge=-100, le=100, description="上下速度(%)")
    yaw_velocity: int = Field(..., ge=-100, le=100, description="回転速度(%)")


# Camera関連
class ResolutionEnum(str, Enum):
    HIGH = "high"
    LOW = "low"


class FPSEnum(str, Enum):
    HIGH = "high"
    MIDDLE = "middle"
    LOW = "low"


class CameraSettingsRequest(BaseModel):
    resolution: Optional[ResolutionEnum] = Field(None, description="解像度設定")
    fps: Optional[FPSEnum] = Field(None, description="フレームレート設定")
    bitrate: Optional[int] = Field(None, ge=1, le=5, description="ビットレート設定")


# Settings関連
class WiFiRequest(BaseModel):
    ssid: str = Field(..., max_length=32, description="WiFi SSID")
    password: str = Field(..., max_length=64, description="WiFiパスワード")


class CommandRequest(BaseModel):
    command: str = Field(..., description="Tello SDKコマンド")
    timeout: int = Field(7, ge=1, le=30, description="タイムアウト(秒)")
    expect_response: bool = Field(True, description="レスポンスを期待するか")


class SpeedRequest(BaseModel):
    speed: float = Field(..., ge=1.0, le=15.0, description="飛行速度(m/s)")


# Mission Pad関連
class MissionPadDirectionRequest(BaseModel):
    direction: int = Field(..., ge=0, le=2, description="検出方向(0:下向き, 1:前向き, 2:両方)")


class MissionPadGoXYZRequest(BaseModel):
    x: int = Field(..., ge=-500, le=500, description="X座標(cm)")
    y: int = Field(..., ge=-500, le=500, description="Y座標(cm)")
    z: int = Field(..., ge=-500, le=500, description="Z座標(cm)")
    speed: int = Field(..., ge=10, le=100, description="速度(cm/s)")
    mission_pad_id: int = Field(..., ge=1, le=8, description="ミッションパッドID")


# Object Tracking関連
class TrackingModeEnum(str, Enum):
    CENTER = "center"
    FOLLOW = "follow"


class TrackingStartRequest(BaseModel):
    target_object: str = Field(..., description="追跡対象オブジェクト名")
    tracking_mode: TrackingModeEnum = Field(TrackingModeEnum.CENTER, description="追跡モード")


# Model Management関連
class ModelTrainRequest(BaseModel):
    object_name: str = Field(..., description="学習対象オブジェクト名")
    # images: List[UploadFile] - FastAPIのFile()で処理