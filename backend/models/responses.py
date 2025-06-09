"""
レスポンスモデル定義
OpenAPI仕様に基づいたAPIレスポンスのPydanticモデル
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# エラーコード定義
class ErrorCode(str, Enum):
    DRONE_NOT_CONNECTED = "DRONE_NOT_CONNECTED"
    DRONE_CONNECTION_FAILED = "DRONE_CONNECTION_FAILED"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    COMMAND_FAILED = "COMMAND_FAILED"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    NOT_FLYING = "NOT_FLYING"
    ALREADY_FLYING = "ALREADY_FLYING"
    STREAMING_NOT_STARTED = "STREAMING_NOT_STARTED"
    STREAMING_ALREADY_STARTED = "STREAMING_ALREADY_STARTED"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    TRAINING_IN_PROGRESS = "TRAINING_IN_PROGRESS"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# 基本レスポンス
class StatusResponse(BaseModel):
    success: bool = Field(..., description="操作成功フラグ")
    message: str = Field(..., description="結果メッセージ")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="エラーメッセージ")
    code: ErrorCode = Field(..., description="エラーコード")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細情報")


# データ型定義
class AccelerationData(BaseModel):
    x: float = Field(..., description="X軸加速度(g)")
    y: float = Field(..., description="Y軸加速度(g)")
    z: float = Field(..., description="Z軸加速度(g)")


class VelocityData(BaseModel):
    x: int = Field(..., description="X軸速度(cm/s)")
    y: int = Field(..., description="Y軸速度(cm/s)")
    z: int = Field(..., description="Z軸速度(cm/s)")


class AttitudeData(BaseModel):
    pitch: int = Field(..., description="ピッチ角(度)")
    roll: int = Field(..., description="ロール角(度)")
    yaw: int = Field(..., description="ヨー角(度)")


class TargetPositionData(BaseModel):
    x: int = Field(..., description="画面内X座標")
    y: int = Field(..., description="画面内Y座標")
    width: int = Field(..., description="検出領域幅")
    height: int = Field(..., description="検出領域高さ")


# センサー関連レスポンス
class BatteryResponse(BaseModel):
    battery: int = Field(..., ge=0, le=100, description="バッテリー残量(%)")


class HeightResponse(BaseModel):
    height: int = Field(..., ge=0, le=3000, description="飛行高度(cm)")


class TemperatureResponse(BaseModel):
    temperature: int = Field(..., ge=0, le=90, description="温度(℃)")


class FlightTimeResponse(BaseModel):
    flight_time: int = Field(..., ge=0, description="累積飛行時間(秒)")


class BarometerResponse(BaseModel):
    barometer: float = Field(..., ge=0, description="気圧(hPa)")


class DistanceTofResponse(BaseModel):
    distance_tof: int = Field(..., ge=0, description="距離(mm)")


class AccelerationResponse(BaseModel):
    acceleration: AccelerationData


class VelocityResponse(BaseModel):
    velocity: VelocityData


class AttitudeResponse(BaseModel):
    attitude: AttitudeData


# ドローン状態レスポンス
class DroneStatus(BaseModel):
    connected: bool = Field(..., description="接続状態")
    battery: Optional[int] = Field(None, ge=0, le=100, description="バッテリー残量(%)")
    height: Optional[int] = Field(None, ge=0, le=3000, description="飛行高度(cm)")
    temperature: Optional[int] = Field(None, ge=0, le=90, description="温度(℃)")
    flight_time: Optional[int] = Field(None, description="累積飛行時間(秒)")
    speed: Optional[float] = Field(None, description="現在速度(cm/s)")
    barometer: Optional[float] = Field(None, description="気圧(hPa)")
    distance_tof: Optional[int] = Field(None, description="ToFセンサー距離(mm)")
    acceleration: Optional[AccelerationData] = Field(None, description="加速度情報")
    velocity: Optional[VelocityData] = Field(None, description="速度情報")
    attitude: Optional[AttitudeData] = Field(None, description="姿勢角情報")


# コマンドレスポンス
class CommandResponse(BaseModel):
    success: bool = Field(..., description="コマンド成功フラグ")
    response: str = Field(..., description="ドローンからのレスポンス")


# ミッションパッド関連
class MissionPadStatusResponse(BaseModel):
    mission_pad_id: int = Field(..., description="検出中のミッションパッドID(-1は検出なし)")
    distance_x: int = Field(..., description="X方向距離(cm)")
    distance_y: int = Field(..., description="Y方向距離(cm)")
    distance_z: int = Field(..., description="Z方向距離(cm)")


# 物体追跡関連
class TrackingStatusResponse(BaseModel):
    is_tracking: bool = Field(..., description="追跡中かどうか")
    target_object: Optional[str] = Field(None, description="追跡対象オブジェクト名")
    target_detected: bool = Field(..., description="対象物検出中かどうか")
    target_position: Optional[TargetPositionData] = Field(None, description="対象物位置")


# モデル管理関連
class ModelInfo(BaseModel):
    name: str = Field(..., description="モデル名")
    created_at: datetime = Field(..., description="作成日時")
    accuracy: float = Field(..., description="精度")


class ModelListResponse(BaseModel):
    models: List[ModelInfo] = Field(..., description="利用可能モデル一覧")


class ModelTrainResponse(BaseModel):
    task_id: str = Field(..., description="訓練タスクID")