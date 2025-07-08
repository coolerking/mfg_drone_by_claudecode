"""
Phase 4 Enhanced Camera & Vision API Router
Advanced camera and vision features with OpenCV integration, enhanced object detection, and learning capabilities
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse

from ..models.camera_models import (
    PhotoCommand, PhotoResponse, StreamingCommand, LearningDataCommand, LearningDataResponse,
    DetectionCommand, DetectionResponse, TrackingCommand, Quality, Resolution
)
from ..models.drone_models import OperationResponse
from ..core.backend_client import BackendClient, backend_client
from ..core.enhanced_nlp_engine import EnhancedNLPEngine
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/mcp/vision", tags=["phase4-vision"])


# ===== Enhanced Object Detection Endpoints =====

@router.post("/detection/enhanced", response_model=Dict[str, Any])
async def enhanced_object_detection(
    image_data: str = Body(..., description="Base64エンコードされた画像データ"),
    model_id: str = Body(..., description="使用する検出モデルID"),
    confidence_threshold: float = Body(default=0.5, description="信頼度閾値"),
    filter_labels: Optional[List[str]] = Body(default=None, description="フィルタリングするラベル"),
    max_detections: Optional[int] = Body(default=None, description="最大検出数"),
    enable_tracking_prep: bool = Body(default=False, description="追跡準備を有効化")
):
    """
    Enhanced object detection with advanced filtering and optimization
    
    高度なフィルタリングと最適化機能を持つ強化された物体検出
    """
    try:
        # Call enhanced detection API in backend
        response = await backend_client._request(
            "POST", 
            "/api/vision/detection/enhanced",
            json={
                "image_data": image_data,
                "model_id": model_id,
                "confidence_threshold": confidence_threshold,
                "filter_labels": filter_labels,
                "max_detections": max_detections
            }
        )
        
        # Add tracking preparation if requested
        if enable_tracking_prep and response.get("detections"):
            best_detection = max(response["detections"], key=lambda x: x["confidence"])
            response["tracking_ready"] = {
                "target_bbox": best_detection["bbox"],
                "target_label": best_detection["label"],
                "target_confidence": best_detection["confidence"]
            }
        
        logger.info(f"Enhanced object detection completed: {len(response.get('detections', []))} objects found")
        return response
        
    except Exception as e:
        logger.error(f"Error in enhanced object detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/performance", response_model=Dict[str, Any])
async def get_model_performance(
    model_id: str = Body(..., description="モデルID")
):
    """
    Get detailed model performance statistics
    
    モデルの詳細なパフォーマンス統計を取得
    """
    try:
        response = await backend_client._request(
            "GET", 
            f"/api/vision/models/{model_id}/performance"
        )
        
        logger.debug(f"Retrieved performance stats for model: {model_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/available", response_model=List[Dict[str, Any]])
async def get_available_models():
    """
    Get list of available vision models with capabilities
    
    利用可能なビジョンモデルの一覧と機能を取得
    """
    try:
        response = await backend_client._request(
            "GET", 
            "/api/vision/models"
        )
        
        logger.info(f"Retrieved {len(response.get('models', []))} available models")
        return response.get("models", [])
        
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Object Tracking Endpoints =====

@router.post("/tracking/enhanced/start", response_model=OperationResponse)
async def start_enhanced_tracking(
    model_id: str = Body(..., description="使用する追跡モデルID"),
    drone_id: str = Body(..., description="対象ドローンID"),
    algorithm: str = Body(default="csrt", description="追跡アルゴリズム"),
    confidence_threshold: float = Body(default=0.5, description="信頼度閾値"),
    follow_distance: int = Body(default=200, description="追従距離（cm）"),
    max_tracking_loss: int = Body(default=30, description="最大追跡失敗フレーム数"),
    update_interval: float = Body(default=0.1, description="更新間隔（秒）"),
    roi_expansion: float = Body(default=1.2, description="ROI拡張率")
):
    """
    Start enhanced object tracking with configurable algorithms
    
    設定可能なアルゴリズムによる強化された物体追跡を開始
    """
    try:
        tracking_config = {
            "algorithm": algorithm,
            "confidence_threshold": confidence_threshold,
            "follow_distance": follow_distance,
            "max_tracking_loss": max_tracking_loss,
            "update_interval": update_interval,
            "roi_expansion": roi_expansion
        }
        
        response = await backend_client._request(
            "POST", 
            "/api/vision/tracking/enhanced/start",
            json={
                "model_id": model_id,
                "drone_id": drone_id,
                "config": tracking_config
            }
        )
        
        logger.info(f"Enhanced tracking started: drone={drone_id}, model={model_id}, algorithm={algorithm}")
        return OperationResponse(
            success=True,
            message=f"Enhanced object tracking started with {algorithm} algorithm",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error starting enhanced tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracking/status/enhanced", response_model=Dict[str, Any])
async def get_enhanced_tracking_status():
    """
    Get enhanced tracking status with detailed metrics
    
    詳細なメトリクスを含む強化された追跡状態を取得
    """
    try:
        response = await backend_client._request(
            "GET", 
            "/api/vision/tracking/status/enhanced"
        )
        
        logger.debug("Retrieved enhanced tracking status")
        return response
        
    except Exception as e:
        logger.error(f"Error getting enhanced tracking status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tracking/enhanced/stop", response_model=OperationResponse)
async def stop_enhanced_tracking():
    """
    Stop enhanced object tracking
    
    強化された物体追跡を停止
    """
    try:
        response = await backend_client._request(
            "POST", 
            "/api/vision/tracking/enhanced/stop"
        )
        
        logger.info("Enhanced tracking stopped")
        return OperationResponse(
            success=True,
            message="Enhanced object tracking stopped",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error stopping enhanced tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Learning Data Collection =====

@router.post("/learning/session/start", response_model=Dict[str, Any])
async def start_learning_session(
    object_name: str = Body(..., description="学習対象物体名"),
    session_config: Optional[Dict[str, Any]] = Body(default=None, description="セッション設定")
):
    """
    Start a learning data collection session
    
    学習データ収集セッションを開始
    """
    try:
        response = await backend_client._request(
            "POST", 
            "/api/vision/learning/session/start",
            json={
                "object_name": object_name,
                "session_config": session_config or {}
            }
        )
        
        session_id = response.get("session_id")
        logger.info(f"Learning session started: {session_id} for object '{object_name}'")
        return response
        
    except Exception as e:
        logger.error(f"Error starting learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/session/{session_id}/sample", response_model=Dict[str, Any])
async def add_learning_sample(
    session_id: str,
    image_data: str = Body(..., description="Base64エンコードされた画像データ"),
    annotation: Dict[str, Any] = Body(..., description="アノテーション情報"),
    quality_score: Optional[float] = Body(default=None, description="品質スコア")
):
    """
    Add a sample to learning session
    
    学習セッションにサンプルを追加
    """
    try:
        response = await backend_client._request(
            "POST", 
            f"/api/vision/learning/session/{session_id}/sample",
            json={
                "image_data": image_data,
                "annotation": annotation,
                "quality_score": quality_score
            }
        )
        
        logger.debug(f"Learning sample added to session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error adding learning sample: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/session/{session_id}/finish", response_model=Dict[str, Any])
async def finish_learning_session(session_id: str):
    """
    Finish learning session and get summary
    
    学習セッションを終了し、サマリーを取得
    """
    try:
        response = await backend_client._request(
            "POST", 
            f"/api/vision/learning/session/{session_id}/finish"
        )
        
        logger.info(f"Learning session completed: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error finishing learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/learning/collect/enhanced", response_model=LearningDataResponse)
async def collect_enhanced_learning_data(
    drone_id: str,
    object_name: str = Body(..., description="学習対象物体名"),
    capture_positions: List[str] = Body(default=["front", "back", "left", "right"], description="撮影位置"),
    altitude_levels: List[int] = Body(default=[100, 150, 200], description="撮影高度（cm）"),
    rotation_angles: List[int] = Body(default=[0, 45, 90, 135, 180, 225, 270, 315], description="回転角度"),
    photos_per_position: int = Body(default=3, description="位置あたり撮影枚数"),
    quality_threshold: float = Body(default=0.7, description="品質閾値"),
    dataset_name: Optional[str] = Body(default=None, description="データセット名")
):
    """
    Enhanced learning data collection with multiple angles, altitudes, and rotations
    
    多角度・多高度・多回転による強化された学習データ収集
    """
    try:
        collection_config = {
            "object_name": object_name,
            "capture_positions": capture_positions,
            "altitude_levels": altitude_levels,
            "rotation_angles": rotation_angles,
            "photos_per_position": photos_per_position,
            "quality_threshold": quality_threshold,
            "dataset_name": dataset_name
        }
        
        response = await backend_client._request(
            "POST", 
            f"/api/drones/{drone_id}/learning_data/collect/enhanced",
            json=collection_config
        )
        
        logger.info(f"Enhanced learning data collection completed for drone {drone_id}")
        return LearningDataResponse(
            success=True,
            message="Enhanced learning data collection completed successfully",
            dataset=response.get("dataset"),
            execution_summary=response.get("execution_summary")
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced learning data collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Camera Control =====

@router.post("/drones/{drone_id}/camera/photo/enhanced", response_model=PhotoResponse)
async def take_enhanced_photo(
    drone_id: str,
    filename: Optional[str] = Body(default=None, description="ファイル名"),
    quality: Quality = Body(default=Quality.HIGH, description="画質"),
    auto_adjust: bool = Body(default=True, description="自動調整"),
    metadata_enhanced: bool = Body(default=True, description="強化メタデータ"),
    apply_filters: List[str] = Body(default=[], description="適用フィルター"),
    capture_multiple: int = Body(default=1, description="連続撮影数")
):
    """
    Enhanced photo capture with auto-adjustment and filters
    
    自動調整とフィルターを備えた強化された写真撮影
    """
    try:
        enhanced_config = {
            "filename": filename,
            "quality": quality,
            "auto_adjust": auto_adjust,
            "metadata_enhanced": metadata_enhanced,
            "apply_filters": apply_filters,
            "capture_multiple": capture_multiple
        }
        
        response = await backend_client._request(
            "POST", 
            f"/api/drones/{drone_id}/camera/photo/enhanced",
            json=enhanced_config
        )
        
        logger.info(f"Enhanced photo captured for drone {drone_id}")
        return PhotoResponse(
            success=True,
            message="Enhanced photo captured successfully",
            photo=response.get("photo")
        )
        
    except Exception as e:
        logger.error(f"Error taking enhanced photo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/camera/streaming/enhanced", response_model=OperationResponse)
async def control_enhanced_streaming(
    drone_id: str,
    action: str = Body(..., description="ストリーミング制御"),
    quality: Quality = Body(default=Quality.MEDIUM, description="品質"),
    resolution: Resolution = Body(default=Resolution.RESOLUTION_720P, description="解像度"),
    frame_rate: int = Body(default=30, description="フレームレート"),
    enable_enhancement: bool = Body(default=True, description="画質強化"),
    auto_exposure: bool = Body(default=True, description="自動露出"),
    stabilization: bool = Body(default=True, description="手ブレ補正")
):
    """
    Enhanced streaming control with quality improvements
    
    画質向上を備えた強化されたストリーミング制御
    """
    try:
        streaming_config = {
            "action": action,
            "quality": quality,
            "resolution": resolution,
            "frame_rate": frame_rate,
            "enable_enhancement": enable_enhancement,
            "auto_exposure": auto_exposure,
            "stabilization": stabilization
        }
        
        response = await backend_client._request(
            "POST", 
            f"/api/drones/{drone_id}/camera/streaming/enhanced",
            json=streaming_config
        )
        
        logger.info(f"Enhanced streaming {action} for drone {drone_id}")
        return OperationResponse(
            success=True,
            message=f"Enhanced streaming {action} successfully",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error controlling enhanced streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Vision Analytics & Statistics =====

@router.get("/analytics/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_vision_analytics():
    """
    Get comprehensive vision analytics and statistics
    
    包括的なビジョン分析と統計を取得
    """
    try:
        response = await backend_client._request(
            "GET", 
            "/api/vision/analytics"
        )
        
        logger.debug("Retrieved comprehensive vision analytics")
        return response
        
    except Exception as e:
        logger.error(f"Error getting vision analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/optimization", response_model=OperationResponse)
async def optimize_vision_system():
    """
    Optimize vision system performance
    
    ビジョンシステムのパフォーマンスを最適化
    """
    try:
        response = await backend_client._request(
            "POST", 
            "/api/vision/optimize"
        )
        
        logger.info("Vision system optimization completed")
        return OperationResponse(
            success=True,
            message="Vision system optimization completed",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error optimizing vision system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/system/cleanup", response_model=Dict[str, Any])
async def cleanup_vision_system(
    max_age_hours: int = Query(default=24, description="最大保持時間（時間）")
):
    """
    Clean up old vision data and sessions
    
    古いビジョンデータとセッションのクリーンアップ
    """
    try:
        response = await backend_client._request(
            "DELETE", 
            f"/api/vision/cleanup?max_age_hours={max_age_hours}"
        )
        
        logger.info(f"Vision system cleanup completed: {response.get('cleaned_items', 0)} items removed")
        return response
        
    except Exception as e:
        logger.error(f"Error cleaning up vision system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))