"""
Model Management-related Pydantic models
Based on OpenAPI specification schemas for model management APIs
"""

from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class TrainingParams(BaseModel):
    """学習パラメータ"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "epochs": 100,
                "batch_size": 16,
                "learning_rate": 0.001,
                "validation_split": 0.2
            }
        }
    )
    
    epochs: int = Field(100, ge=1, le=1000, description="エポック数")
    batch_size: int = Field(16, ge=1, le=64, description="バッチサイズ")
    learning_rate: float = Field(0.001, ge=0.00001, le=1, description="学習率")
    validation_split: float = Field(0.2, ge=0.1, le=0.5, description="検証データ分割比率")


class Model(BaseModel):
    """モデル情報"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "model_001",
                "name": "Person Detection Model v1",
                "description": "YOLOv8 based person detection model",
                "dataset_id": "dataset_001",
                "model_type": "yolo",
                "status": "completed",
                "accuracy": 0.92,
                "file_path": "/models/model_001/best.pt",
                "created_at": "2023-01-01T10:00:00Z",
                "trained_at": "2023-01-01T15:30:00Z"
            }
        }
    )
    
    id: str = Field(..., description="モデルID")
    name: str = Field(..., description="モデル名")
    description: Optional[str] = Field(None, description="モデル説明")
    dataset_id: str = Field(..., description="学習に使用したデータセットID")
    model_type: Literal["yolo", "ssd", "faster_rcnn"] = Field(..., description="モデルタイプ")
    status: Literal["training", "completed", "failed"] = Field(..., description="モデル状態")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="モデル精度")
    file_path: Optional[str] = Field(None, description="モデルファイルパス")
    created_at: datetime = Field(..., description="作成日時")
    trained_at: Optional[datetime] = Field(None, description="学習完了日時")


class TrainModelRequest(BaseModel):
    """モデル学習リクエスト"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Person Detection Model v2",
                "description": "Improved person detection model with better accuracy",
                "dataset_id": "dataset_001",
                "model_type": "yolo",
                "training_params": {
                    "epochs": 150,
                    "batch_size": 16,
                    "learning_rate": 0.001,
                    "validation_split": 0.2
                }
            }
        }
    )
    
    name: str = Field(..., min_length=1, max_length=100, description="モデル名")
    description: Optional[str] = Field(None, max_length=500, description="モデル説明")
    dataset_id: str = Field(..., description="学習データセットID")
    model_type: Literal["yolo", "ssd", "faster_rcnn"] = Field("yolo", description="モデルタイプ")
    training_params: Optional[TrainingParams] = Field(None, description="学習パラメータ")


class TrainingJob(BaseModel):
    """学習ジョブ"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "job_001",
                "model_name": "Person Detection Model v2",
                "dataset_id": "dataset_001",
                "status": "running",
                "progress": 45.0,
                "current_epoch": 45,
                "total_epochs": 100,
                "loss": 0.123,
                "accuracy": 0.87,
                "estimated_remaining_time": 1800,
                "started_at": "2023-01-01T13:00:00Z",
                "completed_at": None,
                "error_message": None
            }
        }
    )
    
    id: str = Field(..., description="ジョブID")
    model_name: str = Field(..., description="モデル名")
    dataset_id: str = Field(..., description="データセットID")
    status: Literal["queued", "running", "completed", "failed", "cancelled"] = Field(
        ..., description="ジョブ状態"
    )
    progress: float = Field(..., ge=0, le=100, description="進捗率（%）")
    current_epoch: Optional[int] = Field(None, ge=0, description="現在のエポック")
    total_epochs: Optional[int] = Field(None, ge=1, description="総エポック数")
    loss: Optional[float] = Field(None, ge=0, description="現在の損失値")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="現在の精度")
    estimated_remaining_time: Optional[int] = Field(None, ge=0, description="推定残り時間（秒）")
    started_at: Optional[datetime] = Field(None, description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")


class SystemStatus(BaseModel):
    """システム状態"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1,
                "temperature": 42.5,
                "connected_drones": 3,
                "active_tracking": 1,
                "running_training_jobs": 2,
                "uptime": 86400,
                "last_updated": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU使用率（%）")
    memory_usage: float = Field(..., ge=0, le=100, description="メモリ使用率（%）")
    disk_usage: float = Field(..., ge=0, le=100, description="ディスク使用率（%）")
    temperature: Optional[float] = Field(None, description="システム温度（℃）")
    connected_drones: int = Field(..., ge=0, description="接続中ドローン数")
    active_tracking: int = Field(..., ge=0, description="アクティブな追跡数")
    running_training_jobs: int = Field(..., ge=0, description="実行中の学習ジョブ数")
    uptime: int = Field(..., ge=0, description="稼働時間（秒）")
    last_updated: datetime = Field(..., description="最終更新時刻")