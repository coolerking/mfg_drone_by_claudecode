"""
Vision API Router
Implements vision-related endpoints from OpenAPI specification
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path, File, UploadFile, Form
from fastapi.responses import JSONResponse

from ..models.vision_models import (
    Dataset, CreateDatasetRequest, DatasetImage, DetectionRequest, 
    DetectionResult, StartTrackingRequest, TrackingStatus
)
from ..models.common_models import SuccessResponse
from ..core.vision_service import VisionService
from ..core.dataset_service import DatasetService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instances (will be injected)
vision_service: VisionService = None
dataset_service: DatasetService = None


def get_vision_service() -> VisionService:
    """Get vision service instance"""
    global vision_service
    if vision_service is None:
        raise HTTPException(status_code=503, detail="Vision service not initialized")
    return vision_service


def get_dataset_service() -> DatasetService:
    """Get dataset service instance"""
    global dataset_service
    if dataset_service is None:
        raise HTTPException(status_code=503, detail="Dataset service not initialized")
    return dataset_service


# Dataset Management Endpoints

@router.get("/vision/datasets", response_model=List[Dataset])
async def get_datasets(
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> List[Dataset]:
    """
    データセット一覧取得
    
    学習データセットの一覧を取得します。
    """
    try:
        datasets = await dataset_svc.get_datasets()
        logger.info(f"Retrieved {len(datasets)} datasets")
        return datasets
    except Exception as e:
        logger.error(f"Error getting datasets: {str(e)}")
        raise HTTPException(status_code=500, detail="データセット一覧の取得に失敗しました")


@router.post("/vision/datasets", response_model=Dataset)
async def create_dataset(
    request: CreateDatasetRequest,
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> Dataset:
    """
    データセット作成
    
    新しい学習データセットを作成します。
    """
    try:
        dataset = await dataset_svc.create_dataset(request)
        logger.info(f"Created dataset: {dataset.id} - {dataset.name}")
        return dataset
    except Exception as e:
        logger.error(f"Error creating dataset: {str(e)}")
        raise HTTPException(status_code=500, detail="データセット作成に失敗しました")


@router.get("/vision/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str = Path(..., description="データセットID", regex="^[a-zA-Z0-9_-]+$"),
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> Dataset:
    """
    データセット詳細取得
    
    指定されたデータセットの詳細を取得します。
    """
    try:
        dataset = await dataset_svc.get_dataset(dataset_id)
        logger.debug(f"Retrieved dataset: {dataset_id}")
        return dataset
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたデータセットが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="データセット詳細の取得に失敗しました")


@router.delete("/vision/datasets/{dataset_id}", response_model=SuccessResponse)
async def delete_dataset(
    dataset_id: str = Path(..., description="データセットID", regex="^[a-zA-Z0-9_-]+$"),
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> SuccessResponse:
    """
    データセット削除
    
    指定されたデータセットを削除します。
    """
    try:
        result = await dataset_svc.delete_dataset(dataset_id)
        logger.info(f"Deleted dataset: {dataset_id}")
        return result
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたデータセットが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="データセット削除に失敗しました")


@router.post("/vision/datasets/{dataset_id}/images", response_model=DatasetImage)
async def add_image_to_dataset(
    dataset_id: str = Path(..., description="データセットID", regex="^[a-zA-Z0-9_-]+$"),
    file: UploadFile = File(..., description="アップロードする画像ファイル"),
    label: str = Form(None, description="画像のラベル"),
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> DatasetImage:
    """
    画像追加
    
    データセットに画像を追加します。
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="有効な画像ファイルをアップロードしてください")
        
        # Read file data
        file_data = await file.read()
        
        if len(file_data) == 0:
            raise HTTPException(status_code=400, detail="空のファイルはアップロードできません")
        
        # Add image to dataset
        dataset_image = await dataset_svc.add_image_to_dataset(
            dataset_id, file_data, file.filename, label
        )
        
        logger.info(f"Added image to dataset {dataset_id}: {dataset_image.filename}")
        return dataset_image
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたデータセットが見つかりません")
        elif "Invalid" in error_msg or "Unsupported" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error adding image to dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="画像追加に失敗しました")


# Object Detection Endpoints

@router.post("/vision/detection", response_model=DetectionResult)
async def detect_objects(
    request: DetectionRequest,
    vision_svc: VisionService = Depends(get_vision_service)
) -> DetectionResult:
    """
    物体検出
    
    画像から物体を検出します。
    """
    try:
        result = await vision_svc.detect_objects(
            request.image, 
            request.model_id, 
            request.confidence_threshold
        )
        logger.info(f"Object detection completed: {len(result.detections)} objects found")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "Model not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたモデルが見つかりません")
        elif "Invalid image" in error_msg:
            raise HTTPException(status_code=400, detail="無効な画像データです")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error in object detection: {str(e)}")
        raise HTTPException(status_code=500, detail="物体検出に失敗しました")


# Object Tracking Endpoints

@router.post("/vision/tracking/start", response_model=SuccessResponse)
async def start_tracking(
    request: StartTrackingRequest,
    vision_svc: VisionService = Depends(get_vision_service)
) -> SuccessResponse:
    """
    追跡開始
    
    指定されたモデルで物体追跡を開始します。
    """
    try:
        result = await vision_svc.start_tracking(
            request.model_id,
            request.drone_id,
            request.confidence_threshold,
            request.follow_distance
        )
        logger.info(f"Object tracking started: drone={request.drone_id}, model={request.model_id}")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "Model not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたモデルが見つかりません")
        elif "already active" in error_msg:
            raise HTTPException(status_code=409, detail="物体追跡は既にアクティブです")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error starting tracking: {str(e)}")
        raise HTTPException(status_code=500, detail="追跡開始に失敗しました")


@router.post("/vision/tracking/stop", response_model=SuccessResponse)
async def stop_tracking(
    vision_svc: VisionService = Depends(get_vision_service)
) -> SuccessResponse:
    """
    追跡停止
    
    物体追跡を停止します。
    """
    try:
        result = await vision_svc.stop_tracking()
        logger.info("Object tracking stopped")
        return result
    except Exception as e:
        logger.error(f"Error stopping tracking: {str(e)}")
        raise HTTPException(status_code=500, detail="追跡停止に失敗しました")


@router.get("/vision/tracking/status", response_model=TrackingStatus)
async def get_tracking_status(
    vision_svc: VisionService = Depends(get_vision_service)
) -> TrackingStatus:
    """
    追跡状態取得
    
    現在の追跡状態を取得します。
    """
    try:
        status = await vision_svc.get_tracking_status()
        logger.debug("Retrieved tracking status")
        return status
    except Exception as e:
        logger.error(f"Error getting tracking status: {str(e)}")
        raise HTTPException(status_code=500, detail="追跡状態の取得に失敗しました")


def initialize_vision_router(vision_svc: VisionService, dataset_svc: DatasetService):
    """Initialize the vision router with service instances"""
    global vision_service, dataset_service
    vision_service = vision_svc
    dataset_service = dataset_svc
    logger.info("Vision router initialized with service instances")