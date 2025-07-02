"""
Vision-related Pydantic models
Based on OpenAPI specification schemas for vision APIs
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class BoundingBox(BaseModel):
    """バウンディングボックス"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "x": 100.0,
                "y": 50.0,
                "width": 150.0,
                "height": 200.0
            }
        }
    )
    
    x: float = Field(..., description="X座標")
    y: float = Field(..., description="Y座標")
    width: float = Field(..., description="幅")
    height: float = Field(..., description="高さ")


class Detection(BaseModel):
    """検出結果"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "person",
                "confidence": 0.85,
                "bbox": {
                    "x": 100.0,
                    "y": 50.0,
                    "width": 150.0,
                    "height": 200.0
                }
            }
        }
    )
    
    label: str = Field(..., description="検出されたオブジェクトのラベル")
    confidence: float = Field(..., ge=0, le=1, description="信頼度")
    bbox: BoundingBox = Field(..., description="バウンディングボックス")


class DetectionRequest(BaseModel):
    """物体検出リクエスト"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image": "iVBORw0KGgoAAAANSUhEUgAAA...",
                "model_id": "yolo_v8_person_detector",
                "confidence_threshold": 0.5
            }
        }
    )
    
    image: str = Field(..., description="Base64エンコードされた画像データ")
    model_id: str = Field(..., description="使用するモデルID")
    confidence_threshold: float = Field(0.5, ge=0, le=1, description="信頼度閾値")


class DetectionResult(BaseModel):
    """物体検出結果"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detections": [
                    {
                        "label": "person",
                        "confidence": 0.85,
                        "bbox": {
                            "x": 100.0,
                            "y": 50.0,
                            "width": 150.0,
                            "height": 200.0
                        }
                    }
                ],
                "processing_time": 0.25,
                "model_id": "yolo_v8_person_detector"
            }
        }
    )
    
    detections: List[Detection] = Field(..., description="検出結果一覧")
    processing_time: float = Field(..., description="処理時間（秒）")
    model_id: str = Field(..., description="使用したモデルID")


class StartTrackingRequest(BaseModel):
    """追跡開始リクエスト"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_id": "yolo_v8_person_detector",
                "drone_id": "drone_001",
                "confidence_threshold": 0.5,
                "follow_distance": 200
            }
        }
    )
    
    model_id: str = Field(..., description="使用するモデルID")
    drone_id: str = Field(..., description="対象ドローンID")
    confidence_threshold: float = Field(0.5, ge=0, le=1, description="信頼度閾値")
    follow_distance: int = Field(200, ge=50, le=500, description="追従距離（cm）")


class TrackingStatus(BaseModel):
    """追跡状態"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": True,
                "model_id": "yolo_v8_person_detector",
                "drone_id": "drone_001",
                "target_detected": True,
                "target_position": {
                    "x": 320.0,
                    "y": 240.0,
                    "width": 80.0,
                    "height": 160.0
                },
                "follow_distance": 200,
                "last_detection_time": "2023-01-01T12:00:00Z",
                "started_at": "2023-01-01T11:55:00Z"
            }
        }
    )
    
    is_active: bool = Field(..., description="追跡アクティブ状態")
    model_id: Optional[str] = Field(None, description="使用中のモデルID")
    drone_id: Optional[str] = Field(None, description="対象ドローンID")
    target_detected: bool = Field(..., description="ターゲット検出状態")
    target_position: Optional[BoundingBox] = Field(None, description="ターゲット位置")
    follow_distance: Optional[int] = Field(None, description="追従距離（cm）")
    last_detection_time: Optional[datetime] = Field(None, description="最終検出時刻")
    started_at: Optional[datetime] = Field(None, description="追跡開始時刻")


class Dataset(BaseModel):
    """データセット"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "dataset_001",
                "name": "Person Detection Dataset",
                "description": "Dataset for person detection model training",
                "image_count": 1500,
                "labels": ["person", "background"],
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    id: str = Field(..., description="データセットID")
    name: str = Field(..., description="データセット名")
    description: Optional[str] = Field(None, description="データセット説明")
    image_count: int = Field(..., ge=0, description="画像数")
    labels: List[str] = Field(..., description="ラベル一覧")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")


class CreateDatasetRequest(BaseModel):
    """データセット作成リクエスト"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Person Detection Dataset",
                "description": "Dataset for training person detection models"
            }
        }
    )
    
    name: str = Field(..., min_length=1, max_length=100, description="データセット名")
    description: Optional[str] = Field(None, max_length=500, description="データセット説明")


class DatasetImage(BaseModel):
    """データセット画像"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "image_001",
                "filename": "person_001.jpg",
                "path": "/datasets/dataset_001/images/person_001.jpg",
                "label": "person",
                "dataset_id": "dataset_001",
                "uploaded_at": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    id: str = Field(..., description="画像ID")
    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")
    label: Optional[str] = Field(None, description="画像ラベル")
    dataset_id: str = Field(..., description="データセットID")
    uploaded_at: datetime = Field(..., description="アップロード日時")