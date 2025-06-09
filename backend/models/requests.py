"""
リクエストモデル定義
OpenAPI仕様に準拠したリクエストデータ構造
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import UploadFile


class MoveDirection(str, Enum):
    """移動方向"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACK = "back"


class RotateDirection(str, Enum):
    """回転方向"""
    CLOCKWISE = "clockwise"
    COUNTER_CLOCKWISE = "counter_clockwise"


class FlipDirection(str, Enum):
    """宙返り方向"""
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACK = "back"


class CameraResolution(str, Enum):
    """カメラ解像度"""
    HIGH = "high"
    LOW = "low"


class CameraFPS(str, Enum):
    """カメラフレームレート"""
    HIGH = "high"
    MIDDLE = "middle"
    LOW = "low"


class TrackingMode(str, Enum):
    """追跡モード"""
    CENTER = "center"
    FOLLOW = "follow"


class MoveRequest(BaseModel):
    """基本移動リクエスト"""
    direction: MoveDirection = Field(..., description="移動方向")
    distance: int = Field(..., ge=20, le=500, description="移動距離(cm)")


class RotateRequest(BaseModel):
    """回転リクエスト"""
    direction: RotateDirection = Field(..., description="回転方向")
    angle: int = Field(..., ge=1, le=360, description="回転角度(度)")


class FlipRequest(BaseModel):
    """宙返りリクエスト"""
    direction: FlipDirection = Field(..., description="宙返り方向")


class GoXYZRequest(BaseModel):
    """座標移動リクエスト"""
    x: int = Field(..., ge=-500, le=500, description="X座標(cm)")
    y: int = Field(..., ge=-500, le=500, description="Y座標(cm)")
    z: int = Field(..., ge=-500, le=500, description="Z座標(cm)")
    speed: int = Field(..., ge=10, le=100, description="速度(cm/s)")


class CurveXYZRequest(BaseModel):
    """曲線飛行リクエスト"""
    x1: int = Field(..., ge=-500, le=500, description="中間点X座標(cm)")
    y1: int = Field(..., ge=-500, le=500, description="中間点Y座標(cm)")
    z1: int = Field(..., ge=-500, le=500, description="中間点Z座標(cm)")
    x2: int = Field(..., ge=-500, le=500, description="終点X座標(cm)")
    y2: int = Field(..., ge=-500, le=500, description="終点Y座標(cm)")
    z2: int = Field(..., ge=-500, le=500, description="終点Z座標(cm)")
    speed: int = Field(..., ge=10, le=60, description="速度(cm/s)")


class RCControlRequest(BaseModel):
    """リアルタイム制御リクエスト"""
    left_right_velocity: int = Field(..., ge=-100, le=100, description="左右速度(%)")
    forward_backward_velocity: int = Field(..., ge=-100, le=100, description="前後速度(%)")
    up_down_velocity: int = Field(..., ge=-100, le=100, description="上下速度(%)")
    yaw_velocity: int = Field(..., ge=-100, le=100, description="回転速度(%)")


class CameraSettingsRequest(BaseModel):
    """カメラ設定リクエスト"""
    resolution: Optional[CameraResolution] = Field(None, description="解像度設定")
    fps: Optional[CameraFPS] = Field(None, description="フレームレート設定")
    bitrate: Optional[int] = Field(None, ge=1, le=5, description="ビットレート設定")


class WiFiRequest(BaseModel):
    """WiFi設定リクエスト"""
    ssid: str = Field(..., max_length=32, description="WiFi SSID")
    password: str = Field(..., max_length=64, description="WiFiパスワード")


class CommandRequest(BaseModel):
    """任意コマンドリクエスト"""
    command: str = Field(..., description="Tello SDKコマンド")
    timeout: Optional[int] = Field(7, ge=1, le=30, description="タイムアウト(秒)")
    expect_response: Optional[bool] = Field(True, description="レスポンスを期待するか")


class SpeedRequest(BaseModel):
    """飛行速度設定リクエスト"""
    speed: float = Field(..., ge=1.0, le=15.0, description="飛行速度(m/s)")


class MissionPadDetectionRequest(BaseModel):
    """ミッションパッド検出方向設定リクエスト"""
    direction: int = Field(..., ge=0, le=2, description="検出方向(0:下向き, 1:前向き, 2:両方)")


class MissionPadGoXYZRequest(BaseModel):
    """ミッションパッド基準移動リクエスト"""
    x: int = Field(..., ge=-500, le=500, description="X座標(cm)")
    y: int = Field(..., ge=-500, le=500, description="Y座標(cm)")
    z: int = Field(..., ge=-500, le=500, description="Z座標(cm)")
    speed: int = Field(..., ge=10, le=100, description="速度(cm/s)")
    mission_pad_id: int = Field(..., ge=1, le=8, description="ミッションパッドID")


class TrackingStartRequest(BaseModel):
    """物体追跡開始リクエスト"""
    target_object: str = Field(..., description="追跡対象オブジェクト名")
    tracking_mode: Optional[TrackingMode] = Field(TrackingMode.CENTER, description="追跡モード")


class ModelTrainRequest(BaseModel):
    """モデル訓練リクエスト"""
    object_name: str = Field(..., description="学習対象オブジェクト名")
    images: List[UploadFile] = Field(..., description="学習用画像ファイル")