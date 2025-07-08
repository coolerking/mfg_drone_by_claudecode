"""
Phase 4 Enhanced Vision Models
Advanced models for camera and vision functionality with OpenCV integration
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class TrackingAlgorithm(str, Enum):
    """Tracking algorithm enumeration"""
    CSRT = "csrt"
    KCF = "kcf"
    MOSSE = "mosse"
    MEDIANFLOW = "medianflow"
    TLD = "tld"
    BOOSTING = "boosting"


class VisionModelType(str, Enum):
    """Vision model type enumeration"""
    YOLO_V8_GENERAL = "yolo_v8_general"
    YOLO_V8_PERSON = "yolo_v8_person"
    YOLO_V8_VEHICLE = "yolo_v8_vehicle"
    SSD_MOBILENET = "ssd_mobilenet_v2"
    FASTER_RCNN = "faster_rcnn_resnet50"
    CUSTOM_TRAINED = "custom_trained"


class ExecutionMode(str, Enum):
    """Execution mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    OPTIMIZED = "optimized"
    PRIORITY_BASED = "priority_based"


class CameraFilter(str, Enum):
    """Camera filter enumeration"""
    SHARPEN = "sharpen"
    DENOISE = "denoise"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    GAUSSIAN_BLUR = "gaussian_blur"


# ===== Enhanced Detection Models =====

class EnhancedDetectionRequest(BaseModel):
    """Enhanced detection request model"""
    image_data: str = Field(..., description="Base64エンコードされた画像データ")
    model_id: str = Field(..., description="使用する検出モデルID")
    confidence_threshold: float = Field(default=0.5, ge=0, le=1, description="信頼度閾値")
    filter_labels: Optional[List[str]] = Field(default=None, description="フィルタリングするラベル")
    max_detections: Optional[int] = Field(default=None, description="最大検出数")
    enable_tracking_prep: bool = Field(default=False, description="追跡準備を有効化")


class BoundingBox(BaseModel):
    """Enhanced bounding box model"""
    x: float = Field(..., description="X座標")
    y: float = Field(..., description="Y座標")
    width: float = Field(..., description="幅")
    height: float = Field(..., description="高さ")
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    @property
    def area(self) -> float:
        return self.width * self.height


class EnhancedDetection(BaseModel):
    """Enhanced detection model"""
    label: str = Field(..., description="検出されたオブジェクトのラベル")
    confidence: float = Field(..., ge=0, le=1, description="信頼度")
    bbox: BoundingBox = Field(..., description="バウンディングボックス")
    tracking_id: Optional[int] = Field(default=None, description="追跡ID")
    features: Optional[Dict[str, Any]] = Field(default=None, description="特徴量")


class EnhancedDetectionResult(BaseModel):
    """Enhanced detection result model"""
    detections: List[EnhancedDetection] = Field(..., description="検出結果一覧")
    processing_time: float = Field(..., description="処理時間（秒）")
    model_id: str = Field(..., description="使用モデルID")
    image_size: tuple = Field(..., description="画像サイズ (width, height)")
    filter_applied: bool = Field(default=False, description="フィルター適用済み")
    max_detections_applied: bool = Field(default=False, description="最大検出数制限適用済み")
    tracking_ready: Optional[Dict[str, Any]] = Field(default=None, description="追跡準備情報")


# ===== Enhanced Tracking Models =====

class TrackingConfig(BaseModel):
    """Tracking configuration model"""
    algorithm: TrackingAlgorithm = Field(default=TrackingAlgorithm.CSRT, description="追跡アルゴリズム")
    confidence_threshold: float = Field(default=0.5, ge=0, le=1, description="信頼度閾値")
    follow_distance: int = Field(default=200, ge=50, le=500, description="追従距離（cm）")
    max_tracking_loss: int = Field(default=30, ge=1, le=100, description="最大追跡失敗フレーム数")
    update_interval: float = Field(default=0.1, ge=0.01, le=1.0, description="更新間隔（秒）")
    roi_expansion: float = Field(default=1.2, ge=1.0, le=3.0, description="ROI拡張率")


class EnhancedTrackingRequest(BaseModel):
    """Enhanced tracking request model"""
    model_id: str = Field(..., description="使用する追跡モデルID")
    drone_id: str = Field(..., description="対象ドローンID")
    config: Optional[TrackingConfig] = Field(default=None, description="追跡設定")


class TrackingSession(BaseModel):
    """Tracking session model"""
    session_id: str = Field(..., description="セッションID")
    model_id: str = Field(..., description="モデルID")
    drone_id: str = Field(..., description="ドローンID")
    target_detected: bool = Field(..., description="ターゲット検出状態")
    target_position: Optional[BoundingBox] = Field(default=None, description="ターゲット位置")
    last_detection_time: Optional[datetime] = Field(default=None, description="最終検出時刻")
    tracking_loss_count: int = Field(default=0, description="追跡失敗回数")
    total_frames: int = Field(default=0, description="総フレーム数")
    success_rate: float = Field(default=0.0, description="成功率")
    runtime: float = Field(default=0.0, description="実行時間（秒）")


class EnhancedTrackingStatus(BaseModel):
    """Enhanced tracking status model"""
    is_active: bool = Field(..., description="追跡アクティブ状態")
    total_sessions: int = Field(..., description="総セッション数")
    active_sessions: List[TrackingSession] = Field(default_factory=list, description="アクティブセッション")
    global_stats: Dict[str, Any] = Field(default_factory=dict, description="グローバル統計")
    active_trackers: int = Field(default=0, description="アクティブトラッカー数")


# ===== Enhanced Learning Models =====

class LearningSessionConfig(BaseModel):
    """Learning session configuration model"""
    collection_mode: str = Field(default="comprehensive", description="収集モード")
    quality_threshold: float = Field(default=0.7, ge=0, le=1, description="品質閾値")
    auto_annotation: bool = Field(default=True, description="自動アノテーション")
    metadata_enhanced: bool = Field(default=True, description="強化メタデータ")


class LearningSession(BaseModel):
    """Learning session model"""
    session_id: str = Field(..., description="セッションID")
    object_name: str = Field(..., description="学習対象物体名")
    start_time: datetime = Field(..., description="開始時刻")
    collected_images: List[str] = Field(default_factory=list, description="収集画像ID一覧")
    annotations: List[Dict[str, Any]] = Field(default_factory=list, description="アノテーション一覧")
    quality_scores: List[float] = Field(default_factory=list, description="品質スコア一覧")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")


class EnhancedLearningDataRequest(BaseModel):
    """Enhanced learning data collection request model"""
    object_name: str = Field(..., description="学習対象物体名")
    capture_positions: List[str] = Field(
        default=["front", "back", "left", "right"], 
        description="撮影位置"
    )
    altitude_levels: List[int] = Field(
        default=[100, 150, 200], 
        description="撮影高度（cm）"
    )
    rotation_angles: List[int] = Field(
        default=[0, 45, 90, 135, 180, 225, 270, 315], 
        description="回転角度"
    )
    photos_per_position: int = Field(default=3, ge=1, le=10, description="位置あたり撮影枚数")
    quality_threshold: float = Field(default=0.7, ge=0, le=1, description="品質閾値")
    dataset_name: Optional[str] = Field(default=None, description="データセット名")


class LearningDataSummary(BaseModel):
    """Learning data collection summary model"""
    session_id: str = Field(..., description="セッションID")
    object_name: str = Field(..., description="物体名")
    duration_seconds: float = Field(..., description="実行時間（秒）")
    total_samples: int = Field(..., description="総サンプル数")
    high_quality_samples: int = Field(..., description="高品質サンプル数")
    average_quality: float = Field(..., description="平均品質スコア")
    quality_distribution: Dict[str, int] = Field(..., description="品質分布")


# ===== Enhanced Camera Models =====

class EnhancedPhotoRequest(BaseModel):
    """Enhanced photo request model"""
    filename: Optional[str] = Field(default=None, description="ファイル名")
    quality: str = Field(default="high", description="画質")
    auto_adjust: bool = Field(default=True, description="自動調整")
    metadata_enhanced: bool = Field(default=True, description="強化メタデータ")
    apply_filters: List[CameraFilter] = Field(default_factory=list, description="適用フィルター")
    capture_multiple: int = Field(default=1, ge=1, le=10, description="連続撮影数")


class EnhancedPhotoInfo(BaseModel):
    """Enhanced photo information model"""
    id: str = Field(..., description="画像ID")
    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")
    size: int = Field(..., description="ファイルサイズ（bytes）")
    timestamp: datetime = Field(..., description="撮影時刻")
    quality_score: Optional[float] = Field(default=None, description="品質スコア")
    applied_filters: List[str] = Field(default_factory=list, description="適用されたフィルター")
    camera_settings: Optional[Dict[str, Any]] = Field(default=None, description="カメラ設定")


class EnhancedStreamingRequest(BaseModel):
    """Enhanced streaming request model"""
    action: str = Field(..., description="ストリーミング制御")
    quality: str = Field(default="medium", description="品質")
    resolution: str = Field(default="720p", description="解像度")
    frame_rate: int = Field(default=30, ge=1, le=60, description="フレームレート")
    enable_enhancement: bool = Field(default=True, description="画質強化")
    auto_exposure: bool = Field(default=True, description="自動露出")
    stabilization: bool = Field(default=True, description="手ブレ補正")


# ===== Analytics Models =====

class ModelPerformanceStats(BaseModel):
    """Model performance statistics model"""
    model_id: str = Field(..., description="モデルID")
    model_type: VisionModelType = Field(..., description="モデルタイプ")
    avg_detection_count: float = Field(..., description="平均検出数")
    avg_confidence: float = Field(..., description="平均信頼度")
    total_inferences: int = Field(..., description="総推論回数")
    avg_inference_time: float = Field(..., description="平均推論時間（秒）")
    labels: List[str] = Field(..., description="対応ラベル")


class VisionAnalytics(BaseModel):
    """Vision analytics model"""
    model_performance: Dict[str, ModelPerformanceStats] = Field(..., description="モデルパフォーマンス")
    tracking_statistics: Dict[str, Any] = Field(..., description="追跡統計")
    learning_statistics: Dict[str, Any] = Field(..., description="学習統計")
    system_status: Dict[str, Any] = Field(..., description="システム状態")


class VisionOptimizationResult(BaseModel):
    """Vision optimization result model"""
    optimizations_applied: List[str] = Field(..., description="適用された最適化")
    performance_improvement: Dict[str, float] = Field(..., description="パフォーマンス向上")
    memory_freed: int = Field(..., description="解放されたメモリ（bytes）")
    execution_time: float = Field(..., description="実行時間（秒）")


class VisionCleanupResult(BaseModel):
    """Vision cleanup result model"""
    cleaned_sessions: int = Field(..., description="クリーンアップされたセッション数")
    cleaned_images: int = Field(..., description="クリーンアップされた画像数")
    freed_storage: int = Field(..., description="解放されたストレージ（bytes）")
    execution_time: float = Field(..., description="実行時間（秒）")


# ===== Command Enhancement Models =====

class VisionCommandAnalysis(BaseModel):
    """Vision command analysis model"""
    command: str = Field(..., description="元のコマンド")
    detected_intent: str = Field(..., description="検出された意図")
    extracted_parameters: Dict[str, Any] = Field(..., description="抽出されたパラメータ")
    confidence: float = Field(..., description="解析信頼度")
    suggested_api_calls: List[Dict[str, Any]] = Field(..., description="推奨APIコール")
    complexity_score: float = Field(..., description="複雑度スコア")


class BatchVisionCommand(BaseModel):
    """Batch vision command model"""
    commands: List[str] = Field(..., description="コマンド一覧")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL, description="実行モード")
    error_recovery: str = Field(default="continue", description="エラー回復戦略")
    optimization_enabled: bool = Field(default=True, description="最適化有効")


class BatchVisionResult(BaseModel):
    """Batch vision command result model"""
    success: bool = Field(..., description="全体成功フラグ")
    results: List[Dict[str, Any]] = Field(..., description="個別結果")
    execution_plan: Dict[str, Any] = Field(..., description="実行計画")
    performance_metrics: Dict[str, Any] = Field(..., description="パフォーマンスメトリクス")
    total_execution_time: float = Field(..., description="総実行時間（秒）")
    optimization_applied: bool = Field(..., description="最適化適用済み")