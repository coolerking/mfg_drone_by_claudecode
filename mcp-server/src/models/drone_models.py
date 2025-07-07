"""
Drone models for MCP Server
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DroneType(str, Enum):
    """Drone type enumeration"""
    REAL = "real"
    DUMMY = "dummy"


class DroneStatus(str, Enum):
    """Drone status enumeration"""
    AVAILABLE = "available"
    CONNECTED = "connected"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class ConnectionStatus(str, Enum):
    """Connection status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


class FlightStatus(str, Enum):
    """Flight status enumeration"""
    LANDED = "landed"
    FLYING = "flying"
    HOVERING = "hovering"
    LANDING = "landing"
    TAKING_OFF = "taking_off"


class MoveDirection(str, Enum):
    """Move direction enumeration"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACK = "back"


class RotateDirection(str, Enum):
    """Rotate direction enumeration"""
    CLOCKWISE = "clockwise"
    COUNTER_CLOCKWISE = "counter_clockwise"
    LEFT = "left"
    RIGHT = "right"


class AltitudeMode(str, Enum):
    """Altitude mode enumeration"""
    ABSOLUTE = "absolute"
    RELATIVE = "relative"


class DroneInfo(BaseModel):
    """Drone information model"""
    id: str = Field(..., description="ドローンID")
    name: str = Field(..., description="ドローン名")
    type: DroneType = Field(..., description="ドローンタイプ")
    status: DroneStatus = Field(..., description="現在ステータス")
    capabilities: List[str] = Field(default_factory=list, description="機能一覧")
    last_seen: Optional[datetime] = Field(default=None, description="最終確認時刻")


class DroneListResponse(BaseModel):
    """Drone list response model"""
    drones: List[DroneInfo] = Field(..., description="ドローン一覧")
    count: int = Field(..., description="ドローン数")
    message: Optional[str] = Field(default=None, description="メッセージ")
    timestamp: datetime = Field(default_factory=datetime.now, description="取得時刻")


class DroneStatusDetail(BaseModel):
    """Detailed drone status"""
    connection_status: ConnectionStatus = Field(..., description="接続状態")
    flight_status: FlightStatus = Field(..., description="飛行状態")
    battery_level: int = Field(..., ge=0, le=100, description="バッテリーレベル（%）")
    height: int = Field(..., ge=0, description="高度（cm）")
    temperature: Optional[float] = Field(default=None, description="温度（℃）")
    wifi_signal: Optional[int] = Field(default=None, ge=0, le=100, description="WiFi信号強度（%）")


class DroneStatusResponse(BaseModel):
    """Drone status response model"""
    drone_id: str = Field(..., description="ドローンID")
    status: DroneStatusDetail = Field(..., description="ドローン状態")
    message: Optional[str] = Field(default=None, description="ステータスメッセージ")
    timestamp: datetime = Field(default_factory=datetime.now, description="取得時刻")


class TakeoffCommand(BaseModel):
    """Takeoff command model"""
    target_height: Optional[int] = Field(default=None, ge=20, le=300, description="目標高度（cm）")
    safety_check: bool = Field(default=True, description="安全チェック実行")


class MoveCommand(BaseModel):
    """Move command model"""
    direction: MoveDirection = Field(..., description="移動方向")
    distance: int = Field(..., ge=20, le=500, description="移動距離（cm）")
    speed: Optional[int] = Field(default=None, ge=10, le=100, description="移動速度（cm/s）")


class RotateCommand(BaseModel):
    """Rotate command model"""
    direction: RotateDirection = Field(..., description="回転方向")
    angle: int = Field(..., ge=1, le=360, description="回転角度（度）")


class AltitudeCommand(BaseModel):
    """Altitude command model"""
    target_height: int = Field(..., ge=20, le=300, description="目標高度（cm）")
    mode: AltitudeMode = Field(default=AltitudeMode.ABSOLUTE, description="高度指定モード")


class OperationResponse(BaseModel):
    """Operation response model"""
    success: bool = Field(..., description="操作成功フラグ")
    message: str = Field(..., description="操作結果メッセージ")
    operation_id: Optional[str] = Field(default=None, description="操作ID")
    execution_time: Optional[float] = Field(default=None, description="実行時間（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="実行時刻")