"""
Camera and vision models for MCP Server
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Quality(str, Enum):
    """Quality enumeration"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Resolution(str, Enum):
    """Resolution enumeration"""
    RESOLUTION_720P = "720p"
    RESOLUTION_480P = "480p"
    RESOLUTION_360P = "360p"


class StreamingAction(str, Enum):
    """Streaming action enumeration"""
    START = "start"
    STOP = "stop"


class CapturePosition(str, Enum):
    """Capture position enumeration"""
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class TrackingAction(str, Enum):
    """Tracking action enumeration"""
    START = "start"
    STOP = "stop"


class PhotoCommand(BaseModel):
    """Photo command model"""
    filename: Optional[str] = Field(default=None, description="保存ファイル名（省略可）")
    quality: Quality = Field(default=Quality.HIGH, description="画質設定")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="追加メタデータ")


class StreamingCommand(BaseModel):
    """Streaming command model"""
    action: StreamingAction = Field(..., description="ストリーミング制御")
    quality: Quality = Field(default=Quality.MEDIUM, description="ストリーミング品質")
    resolution: Resolution = Field(default=Resolution.RESOLUTION_720P, description="解像度")


class LearningDataCommand(BaseModel):
    """Learning data command model"""
    object_name: str = Field(..., description="学習対象物体名")
    capture_positions: List[CapturePosition] = Field(
        default=[CapturePosition.FRONT, CapturePosition.BACK, CapturePosition.LEFT, CapturePosition.RIGHT],
        description="撮影位置"
    )
    movement_distance: int = Field(default=30, ge=20, le=100, description="移動距離（cm）")
    photos_per_position: int = Field(default=3, ge=1, le=10, description="位置あたり撮影枚数")
    dataset_name: Optional[str] = Field(default=None, description="データセット名")


class DetectionCommand(BaseModel):
    """Detection command model"""
    drone_id: str = Field(..., description="対象ドローンID")
    model_id: Optional[str] = Field(default=None, description="使用モデルID")
    confidence_threshold: float = Field(default=0.5, ge=0, le=1, description="信頼度閾値")


class TrackingCommand(BaseModel):
    """Tracking command model"""
    action: TrackingAction = Field(..., description="追跡制御")
    drone_id: str = Field(..., description="対象ドローンID")
    model_id: Optional[str] = Field(default=None, description="使用モデルID")
    follow_distance: int = Field(default=200, ge=50, le=500, description="追従距離（cm）")
    confidence_threshold: float = Field(default=0.5, ge=0, le=1, description="信頼度閾値")


class PhotoInfo(BaseModel):
    """Photo information model"""
    id: str = Field(..., description="画像ID")
    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")
    size: int = Field(..., description="ファイルサイズ（bytes）")
    timestamp: datetime = Field(..., description="撮影時刻")


class PhotoResponse(BaseModel):
    """Photo response model"""
    success: bool = Field(..., description="撮影成功フラグ")
    message: str = Field(..., description="撮影結果メッセージ")
    photo: Optional[PhotoInfo] = Field(default=None, description="撮影画像情報")
    timestamp: datetime = Field(default_factory=datetime.now, description="レスポンス時刻")


class DatasetInfo(BaseModel):
    """Dataset information model"""
    id: str = Field(..., description="データセットID")
    name: str = Field(..., description="データセット名")
    image_count: int = Field(..., description="収集画像数")
    positions_captured: List[str] = Field(..., description="撮影完了位置")


class ExecutionSummary(BaseModel):
    """Execution summary model"""
    total_moves: int = Field(..., description="総移動回数")
    total_photos: int = Field(..., description="総撮影枚数")
    execution_time: float = Field(..., description="実行時間（秒）")


class LearningDataResponse(BaseModel):
    """Learning data response model"""
    success: bool = Field(..., description="収集成功フラグ")
    message: str = Field(..., description="収集結果メッセージ")
    dataset: Optional[DatasetInfo] = Field(default=None, description="作成されたデータセット情報")
    execution_summary: Optional[ExecutionSummary] = Field(default=None, description="実行サマリー")
    timestamp: datetime = Field(default_factory=datetime.now, description="完了時刻")


class BoundingBox(BaseModel):
    """Bounding box model"""
    x: float = Field(..., description="X座標")
    y: float = Field(..., description="Y座標")
    width: float = Field(..., description="幅")
    height: float = Field(..., description="高さ")


class Detection(BaseModel):
    """Detection model"""
    label: str = Field(..., description="検出されたオブジェクトのラベル")
    confidence: float = Field(..., ge=0, le=1, description="信頼度")
    bbox: BoundingBox = Field(..., description="バウンディングボックス")


class DetectionResponse(BaseModel):
    """Detection response model"""
    success: bool = Field(..., description="検出成功フラグ")
    message: str = Field(..., description="検出結果メッセージ")
    detections: List[Detection] = Field(..., description="検出結果一覧")
    processing_time: Optional[float] = Field(default=None, description="処理時間（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="検出時刻")