"""
Models API Router
Implements model management endpoints from OpenAPI specification
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.responses import JSONResponse

from ..models.model_models import Model, TrainModelRequest, TrainingJob
from ..models.common_models import SuccessResponse
from ..core.model_service import ModelService
from ..core.dataset_service import DatasetService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instances (will be injected)
model_service: ModelService = None
dataset_service: DatasetService = None


def get_model_service() -> ModelService:
    """Get model service instance"""
    global model_service
    if model_service is None:
        raise HTTPException(status_code=503, detail="Model service not initialized")
    return model_service


def get_dataset_service() -> DatasetService:
    """Get dataset service instance"""
    global dataset_service
    if dataset_service is None:
        raise HTTPException(status_code=503, detail="Dataset service not initialized")
    return dataset_service


# Model Management Endpoints

@router.get("/models", response_model=List[Model])
async def get_models(
    model_svc: ModelService = Depends(get_model_service)
) -> List[Model]:
    """
    モデル一覧取得
    
    学習済みモデルの一覧を取得します。
    """
    try:
        models = await model_svc.get_models()
        logger.info(f"Retrieved {len(models)} models")
        return models
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail="モデル一覧の取得に失敗しました")


@router.post("/models", response_model=TrainingJob)
async def start_model_training(
    request: TrainModelRequest,
    model_svc: ModelService = Depends(get_model_service),
    dataset_svc: DatasetService = Depends(get_dataset_service)
) -> TrainingJob:
    """
    モデル学習開始
    
    データセットを使用してモデル学習を開始します。
    """
    try:
        training_job = await model_svc.start_training(request, dataset_svc)
        logger.info(f"Started model training: {training_job.id} for model {request.name}")
        return training_job
    except ValueError as e:
        error_msg = str(e)
        if "Dataset not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたデータセットが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error starting model training: {str(e)}")
        raise HTTPException(status_code=500, detail="モデル学習開始に失敗しました")


@router.get("/models/{model_id}", response_model=Model)
async def get_model(
    model_id: str = Path(..., description="モデルID", regex="^[a-zA-Z0-9_-]+$"),
    model_svc: ModelService = Depends(get_model_service)
) -> Model:
    """
    モデル詳細取得
    
    指定されたモデルの詳細を取得します。
    """
    try:
        model = await model_svc.get_model(model_id)
        logger.debug(f"Retrieved model: {model_id}")
        return model
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたモデルが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="モデル詳細の取得に失敗しました")


@router.delete("/models/{model_id}", response_model=SuccessResponse)
async def delete_model(
    model_id: str = Path(..., description="モデルID", regex="^[a-zA-Z0-9_-]+$"),
    model_svc: ModelService = Depends(get_model_service)
) -> SuccessResponse:
    """
    モデル削除
    
    指定されたモデルを削除します。
    """
    try:
        result = await model_svc.delete_model(model_id)
        logger.info(f"Deleted model: {model_id}")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたモデルが見つかりません")
        elif "being used" in error_msg:
            raise HTTPException(status_code=409, detail="モデルが使用中のため削除できません")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error deleting model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="モデル削除に失敗しました")


# Training Job Management Endpoints

@router.get("/models/training/{job_id}", response_model=TrainingJob)
async def get_training_job(
    job_id: str = Path(..., description="ジョブID", regex="^[a-zA-Z0-9_-]+$"),
    model_svc: ModelService = Depends(get_model_service)
) -> TrainingJob:
    """
    学習状況取得
    
    学習ジョブの状況を取得します。
    """
    try:
        training_job = await model_svc.get_training_job(job_id)
        logger.debug(f"Retrieved training job: {job_id}")
        return training_job
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたジョブが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting training job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="学習状況の取得に失敗しました")


@router.post("/models/training/{job_id}/cancel", response_model=SuccessResponse)
async def cancel_training_job(
    job_id: str = Path(..., description="ジョブID", regex="^[a-zA-Z0-9_-]+$"),
    model_svc: ModelService = Depends(get_model_service)
) -> SuccessResponse:
    """
    学習ジョブキャンセル
    
    実行中の学習ジョブをキャンセルします。
    """
    try:
        result = await model_svc.cancel_training_job(job_id)
        logger.info(f"Cancelled training job: {job_id}")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたジョブが見つかりません")
        elif "Cannot cancel" in error_msg:
            raise HTTPException(status_code=400, detail="ジョブをキャンセルできません")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error cancelling training job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="学習ジョブのキャンセルに失敗しました")


@router.get("/models/training", response_model=List[TrainingJob])
async def get_all_training_jobs(
    model_svc: ModelService = Depends(get_model_service)
) -> List[TrainingJob]:
    """
    全学習ジョブ取得
    
    すべての学習ジョブの一覧を取得します。
    """
    try:
        training_jobs = await model_svc.get_all_training_jobs()
        logger.info(f"Retrieved {len(training_jobs)} training jobs")
        return training_jobs
    except Exception as e:
        logger.error(f"Error getting training jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="学習ジョブ一覧の取得に失敗しました")


@router.get("/models/training/active", response_model=List[TrainingJob])
async def get_active_training_jobs(
    model_svc: ModelService = Depends(get_model_service)
) -> List[TrainingJob]:
    """
    アクティブ学習ジョブ取得
    
    実行中またはキューに入っている学習ジョブの一覧を取得します。
    """
    try:
        active_jobs = await model_svc.get_active_training_jobs()
        logger.info(f"Retrieved {len(active_jobs)} active training jobs")
        return active_jobs
    except Exception as e:
        logger.error(f"Error getting active training jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="アクティブ学習ジョブの取得に失敗しました")


@router.get("/models/statistics")
async def get_model_statistics(
    model_svc: ModelService = Depends(get_model_service)
):
    """
    モデル統計情報取得
    
    モデルサービスの統計情報を取得します。
    """
    try:
        statistics = await model_svc.get_model_statistics()
        logger.debug("Retrieved model statistics")
        return statistics
    except Exception as e:
        logger.error(f"Error getting model statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="統計情報の取得に失敗しました")


def initialize_models_router(model_svc: ModelService, dataset_svc: DatasetService):
    """Initialize the models router with service instances"""
    global model_service, dataset_service
    model_service = model_svc
    dataset_service = dataset_svc
    logger.info("Models router initialized with service instances")