"""
AIモデル管理API
機械学習モデルの訓練・管理機能
"""

from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.responses import ModelListResponse, ModelTrainResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/model", tags=["Model Management"])


@router.post(
    "/train",
    response_model=ModelTrainResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        413: {"model": ErrorResponse, "description": "ファイルサイズが大きすぎる"},
        503: {"model": ErrorResponse, "description": "訓練システム未初期化"}
    },
    summary="物体認識モデル訓練",
    description="アップロードされた画像を使用して物体認識モデルを訓練します"
)
async def train_model(
    object_name: str = Form(..., description="学習対象オブジェクト名"),
    images: List[UploadFile] = File(..., description="学習用画像ファイル"),
    drone_service: DroneServiceDep = None
):
    """物体認識モデル訓練"""
    try:
        # ファイルサイズとタイプの検証
        for image in images:
            if image.size and image.size > 10 * 1024 * 1024:  # 10MB制限
                raise HTTPException(
                    status_code=413,
                    detail=ErrorResponse(
                        error="ファイルサイズが大きすぎます（最大10MB）",
                        code=ErrorCode.FILE_TOO_LARGE
                    ).model_dump()
                )
            
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=ErrorResponse(
                        error=f"サポートされていないファイル形式: {image.content_type}",
                        code=ErrorCode.UNSUPPORTED_FORMAT
                    ).model_dump()
                )
        
        # 最低画像数の確認
        if len(images) < 5:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="最低5枚の画像が必要です",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        result = await drone_service.train_model(
            object_name=object_name,
            images=images
        )
        
        if result["success"]:
            return ModelTrainResponse(task_id=result["task_id"])
        else:
            if "パラメータ" in result["message"] or "無効" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "進行中" in result["message"]:
                status_code = 400
                error_code = ErrorCode.TRAINING_IN_PROGRESS
            else:
                status_code = 503
                error_code = ErrorCode.INTERNAL_ERROR
            
            raise HTTPException(
                status_code=status_code,
                detail=ErrorResponse(
                    error=result["message"],
                    code=error_code
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"モデル訓練エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get(
    "/list",
    response_model=ModelListResponse,
    responses={
        503: {"model": ErrorResponse, "description": "モデル管理システム未初期化"}
    },
    summary="利用可能モデル一覧取得",
    description="訓練済みの物体認識モデル一覧を取得します"
)
async def list_models(drone_service: DroneServiceDep):
    """利用可能モデル一覧取得"""
    try:
        result = await drone_service.list_models()
        return ModelListResponse(models=result["models"])
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"モデル一覧取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )