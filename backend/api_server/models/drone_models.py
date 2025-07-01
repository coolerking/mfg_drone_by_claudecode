"""
Drone-related Pydantic models
Based on OpenAPI specification schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class Attitude(BaseModel):
    """ドローンの姿勢"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pitch": 0.0,
                "roll": 0.0,
                "yaw": 45.0
            }
        }
    )
    
    pitch: float = Field(..., ge=-180, le=180, description="ピッチ角（度）")
    roll: float = Field(..., ge=-180, le=180, description="ロール角（度）")
    yaw: float = Field(..., ge=-180, le=180, description="ヨー角（度）")


class Drone(BaseModel):
    """ドローン情報"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "drone_001",
                "name": "Tello EDU #1",
                "type": "dummy",
                "ip_address": "192.168.1.100",
                "status": "connected",
                "last_seen": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    id: str = Field(..., description="ドローンID")
    name: str = Field(..., description="ドローン名")
    type: Literal["real", "dummy"] = Field(..., description="ドローンタイプ")
    ip_address: Optional[str] = Field(None, description="IPアドレス")
    status: Literal["disconnected", "connected", "flying", "landed", "error"] = Field(
        ..., description="接続状態"
    )
    last_seen: Optional[datetime] = Field(None, description="最終通信時刻")


class DroneStatus(BaseModel):
    """ドローン状態"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "drone_id": "drone_001",
                "connection_status": "connected",
                "flight_status": "flying",
                "battery_level": 85,
                "flight_time": 300,
                "height": 150,
                "temperature": 25.5,
                "speed": 2.5,
                "wifi_signal": 90,
                "attitude": {
                    "pitch": 0.0,
                    "roll": 0.0,
                    "yaw": 45.0
                },
                "last_updated": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    drone_id: str = Field(..., description="ドローンID")
    connection_status: Literal["disconnected", "connected", "error"] = Field(
        ..., description="接続状態"
    )
    flight_status: Literal["landed", "flying", "hovering", "landing", "taking_off"] = Field(
        ..., description="飛行状態"
    )
    battery_level: int = Field(..., ge=0, le=100, description="バッテリーレベル（%）")
    flight_time: Optional[int] = Field(None, ge=0, description="飛行時間（秒）")
    height: Optional[int] = Field(None, ge=0, description="高度（cm）")
    temperature: Optional[float] = Field(None, description="温度（℃）")
    speed: Optional[float] = Field(None, ge=0, description="速度（cm/s）")
    wifi_signal: Optional[int] = Field(None, ge=0, le=100, description="WiFi信号強度（%）")
    attitude: Optional[Attitude] = Field(None, description="姿勢情報")
    last_updated: datetime = Field(..., description="最終更新時刻")


class MoveCommand(BaseModel):
    """移動コマンド"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "direction": "forward",
                "distance": 100
            }
        }
    )
    
    direction: Literal["up", "down", "left", "right", "forward", "back"] = Field(
        ..., description="移動方向"
    )
    distance: int = Field(..., ge=20, le=500, description="移動距離（cm）")


class RotateCommand(BaseModel):
    """回転コマンド"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "direction": "clockwise",
                "angle": 90
            }
        }
    )
    
    direction: Literal["clockwise", "counter_clockwise"] = Field(
        ..., description="回転方向"
    )
    angle: int = Field(..., ge=1, le=360, description="回転角度（度）")


class Photo(BaseModel):
    """写真情報"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "photo_001",
                "filename": "drone_photo_20230101_120000.jpg",
                "path": "/photos/drone_photo_20230101_120000.jpg",
                "timestamp": "2023-01-01T12:00:00Z",
                "drone_id": "drone_001",
                "metadata": {
                    "resolution": "1280x720",
                    "format": "JPEG",
                    "size_bytes": 245760
                }
            }
        }
    )
    
    id: str = Field(..., description="写真ID")
    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")
    timestamp: datetime = Field(..., description="撮影時刻")
    drone_id: str = Field(..., description="撮影したドローンID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="写真のメタデータ")