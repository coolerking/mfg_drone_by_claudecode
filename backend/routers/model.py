"""
AIモデル管理ルーター
物体認識モデルの訓練・管理エンドポイント
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from dependencies import DroneServiceDep
from models.responses import (
    ModelListResponse, ModelTrainResponse, ErrorResponse, ErrorCode,
    ModelInfo
)
from datetime import datetime

router = APIRouter(
    prefix="/model",
    tags=["Model Management"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/train", response_model=ModelTrainResponse)
async def train_model(
    object_name: str = Form(..., description="学習対象オブジェクト名"),
    images: List[UploadFile] = File(..., description="学習用画像ファイル"),
    drone_service: DroneServiceDep = None
):
    """
    物体認識モデル訓練
    
    Args:
        object_name: 学習対象オブジェクト名
        images: 学習用画像ファイルリスト
        drone_service: ドローンサービス
        
    Returns:
        ModelTrainResponse: 訓練タスクID
        
    Raises:
        HTTPException: 訓練開始失敗時
    """
    try:
        # オブジェクト名のバリデーション
        if not object_name or len(object_name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="オブジェクト名が無効です",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # 画像ファイルのバリデーション
        if not images or len(images) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="学習用画像が提供されていません",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # ファイルサイズとタイプのチェック
        max_file_size = 10 * 1024 * 1024  # 10MB
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        
        for image in images:
            # ファイルサイズチェック
            if image.size and image.size > max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=ErrorResponse(
                        error=f"ファイル {image.filename} が大きすぎます",
                        code=ErrorCode.FILE_TOO_LARGE
                    ).model_dump()
                )
            
            # ファイルタイプチェック
            if image.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=f"ファイル {image.filename} の形式がサポートされていません",
                        code=ErrorCode.UNSUPPORTED_FORMAT
                    ).model_dump()
                )
        
        # TODO: 実際のモデル訓練実装
        # TODO: 非同期タスクキューの実装
        # TODO: GPU使用可能性の確認
        # TODO: 既存モデルの競合チェック
        # 現在はスケルトン実装
        
        # タスクIDの生成（実際はUUIDやタイムスタンプベースのIDを使用）
        task_id = f"train_{object_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ModelTrainResponse(task_id=task_id)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"モデル訓練開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/list", response_model=ModelListResponse)
async def list_available_models(drone_service: DroneServiceDep):
    """
    利用可能モデル一覧取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        ModelListResponse: モデル一覧
        
    Raises:
        HTTPException: モデル一覧取得失敗時
    """
    try:
        # TODO: 実際のモデルストレージからのモデル一覧取得
        # TODO: モデルファイルの存在確認
        # TODO: モデルメタデータの読み込み
        # 現在はスケルトン実装 - サンプルモデルを返す
        
        sample_models = [
            ModelInfo(
                name="person_detector",
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                accuracy=0.92
            ),
            ModelInfo(
                name="vehicle_detector", 
                created_at=datetime(2024, 1, 20, 14, 15, 0),
                accuracy=0.88
            ),
            ModelInfo(
                name="animal_detector",
                created_at=datetime(2024, 1, 25, 9, 45, 0), 
                accuracy=0.85
            )
        ]
        
        return ModelListResponse(models=sample_models)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"モデル一覧取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )