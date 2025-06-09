"""
レスポンスモデル定義
OpenAPI仕様に準拠したレスポンスデータ構造
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """エラーコード定義"""
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


class StatusResponse(BaseModel):
    """共通ステータスレスポンス"""
    success: bool = Field(..., description="操作成功フラグ")
    message: str = Field(..., description="結果メッセージ")


class ErrorResponse(BaseModel):
    """共通エラーレスポンス"""
    error: str = Field(..., description="エラーメッセージ")
    code: ErrorCode = Field(..., description="エラーコード")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細情報")


class AccelerationData(BaseModel):
    """加速度データ"""
    x: float = Field(..., description="X軸加速度(g)")
    y: float = Field(..., description="Y軸加速度(g)")
    z: float = Field(..., description="Z軸加速度(g)")


class VelocityData(BaseModel):
    """速度データ"""
    x: int = Field(..., description="X軸速度(cm/s)")
    y: int = Field(..., description="Y軸速度(cm/s)")
    z: int = Field(..., description="Z軸速度(cm/s)")


class AttitudeData(BaseModel):
    """姿勢データ"""
    pitch: int = Field(..., ge=-180, le=180, description="ピッチ角(度)")
    roll: int = Field(..., ge=-180, le=180, description="ロール角(度)")
    yaw: int = Field(..., ge=-180, le=180, description="ヨー角(度)")


class DroneStatus(BaseModel):
    """ドローン総合状態"""
    connected: bool = Field(..., description="接続状態")
    battery: int = Field(..., ge=0, le=100, description="バッテリー残量(%)")
    height: int = Field(..., ge=0, le=3000, description="飛行高度(cm)")
    temperature: int = Field(..., ge=0, le=90, description="温度(℃)")
    flight_time: int = Field(..., ge=0, description="累積飛行時間(秒)")
    speed: float = Field(..., description="現在速度(cm/s)")
    barometer: float = Field(..., ge=0, description="気圧(hPa)")
    distance_tof: int = Field(..., ge=0, description="ToFセンサー距離(mm)")
    acceleration: AccelerationData = Field(..., description="加速度情報")
    velocity: VelocityData = Field(..., description="速度情報")
    attitude: AttitudeData = Field(..., description="姿勢情報")


class BatteryResponse(BaseModel):
    """バッテリー残量レスポンス"""
    battery: int = Field(..., ge=0, le=100, description="バッテリー残量(%)")


class HeightResponse(BaseModel):
    """飛行高度レスポンス"""
    height: int = Field(..., ge=0, le=3000, description="飛行高度(cm)")


class TemperatureResponse(BaseModel):
    """温度レスポンス"""
    temperature: int = Field(..., ge=0, le=90, description="温度(℃)")


class FlightTimeResponse(BaseModel):
    """累積飛行時間レスポンス"""
    flight_time: int = Field(..., ge=0, description="累積飛行時間(秒)")


class BarometerResponse(BaseModel):
    """気圧レスポンス"""
    barometer: float = Field(..., ge=0, description="気圧(hPa)")


class DistanceTofResponse(BaseModel):
    """ToFセンサー距離レスポンス"""
    distance_tof: int = Field(..., ge=0, description="距離(mm)")


class AccelerationResponse(BaseModel):
    """加速度レスポンス"""
    acceleration: AccelerationData = Field(..., description="加速度情報")


class VelocityResponse(BaseModel):
    """速度レスポンス"""
    velocity: VelocityData = Field(..., description="速度情報")


class AttitudeResponse(BaseModel):
    """姿勢角レスポンス"""
    attitude: AttitudeData = Field(..., description="姿勢角情報")


class CommandResponse(BaseModel):
    """任意コマンドレスポンス"""
    success: bool = Field(..., description="コマンド実行成功フラグ")
    response: str = Field(..., description="ドローンからのレスポンス")


class TargetPosition(BaseModel):
    """追跡対象位置情報"""
    x: int = Field(..., description="画面内X座標")
    y: int = Field(..., description="画面内Y座標")
    width: int = Field(..., description="検出領域幅")
    height: int = Field(..., description="検出領域高さ")


class TrackingStatusResponse(BaseModel):
    """物体追跡状態レスポンス"""
    is_tracking: bool = Field(..., description="追跡中かどうか")
    target_object: Optional[str] = Field(None, description="追跡対象オブジェクト名")
    target_detected: bool = Field(..., description="対象物検出中かどうか")
    target_position: Optional[TargetPosition] = Field(None, description="対象物位置情報")


class MissionPadStatusResponse(BaseModel):
    """ミッションパッド状態レスポンス"""
    mission_pad_id: int = Field(..., description="検出中のミッションパッドID(-1は検出なし)")
    distance_x: int = Field(..., description="X方向距離(cm)")
    distance_y: int = Field(..., description="Y方向距離(cm)")
    distance_z: int = Field(..., description="Z方向距離(cm)")


class ModelInfo(BaseModel):
    """モデル情報"""
    name: str = Field(..., description="モデル名")
    created_at: datetime = Field(..., description="作成日時")
    accuracy: float = Field(..., description="精度")


class ModelListResponse(BaseModel):
    """利用可能モデル一覧レスポンス"""
    models: List[ModelInfo] = Field(..., description="モデル一覧")


class ModelTrainResponse(BaseModel):
    """モデル訓練開始レスポンス"""
    task_id: str = Field(..., description="訓練タスクID")