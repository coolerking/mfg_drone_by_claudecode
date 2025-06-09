"""
物体認識・追跡ルーター
物体追跡機能のエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import TrackingStartRequest
from models.responses import StatusResponse, TrackingStatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/tracking",
    tags=["Object Tracking"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "Target not found"},
        503: {"model": ErrorResponse, "description": "Drone not connected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/start", response_model=StatusResponse)
async def start_object_tracking(request: TrackingStartRequest, drone_service: DroneServiceDep):
    """
    物体追跡開始
    
    Args:
        request: 追跡開始リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 追跡開始結果
        
    Raises:
        HTTPException: 追跡開始失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # 対象オブジェクト名のバリデーション
        if not request.target_object or len(request.target_object.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="追跡対象オブジェクト名が無効です",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # TODO: DroneServiceにstart_object_trackingメソッドを実装する必要がある
        # TODO: 物体認識モデルの存在確認
        # TODO: カメラストリーミングの開始確認
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message=f"物体追跡を開始しました (対象: {request.target_object}, モード: {request.tracking_mode.value})"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"追跡開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/stop", response_model=StatusResponse)
async def stop_object_tracking(drone_service: DroneServiceDep):
    """
    物体追跡停止
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 追跡停止結果
        
    Raises:
        HTTPException: 追跡停止失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # TODO: DroneServiceにstop_object_trackingメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="物体追跡を停止しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"追跡停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/status", response_model=TrackingStatusResponse)
async def get_tracking_status(drone_service: DroneServiceDep):
    """
    追跡状態取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        TrackingStatusResponse: 追跡状態
        
    Raises:
        HTTPException: 状態取得失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # TODO: DroneServiceにget_tracking_statusメソッドを実装する必要がある
        # 現在はスケルトン実装 - デフォルト値を返す
        return TrackingStatusResponse(
            is_tracking=False,
            target_object=None,
            target_detected=False,
            target_position=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"追跡状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )