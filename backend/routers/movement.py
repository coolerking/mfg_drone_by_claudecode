"""
基本移動制御ルーター
基本移動・回転・宙返りエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import MoveRequest, RotateRequest, FlipRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Movement"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        409: {"model": ErrorResponse, "description": "Drone not flying"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/move", response_model=StatusResponse)
async def move_drone(request: MoveRequest, drone_service: DroneServiceDep):
    """
    基本移動
    
    Args:
        request: 移動リクエスト (方向, 距離)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 移動結果
        
    Raises:
        HTTPException: 移動失敗時
    """
    try:
        # TODO: DroneServiceにmoveメソッドを実装する必要がある
        # 現在はスケルトン実装
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        if not hasattr(drone_service, '_is_flying') or not drone_service._is_flying:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが飛行中でない",
                    code=ErrorCode.NOT_FLYING
                ).model_dump()
            )
        
        # スケルトン実装 - 実際のドローン制御は後続で実装
        return StatusResponse(
            success=True,
            message=f"{request.direction.value}方向に{request.distance}cm移動しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/rotate", response_model=StatusResponse)
async def rotate_drone(request: RotateRequest, drone_service: DroneServiceDep):
    """
    回転
    
    Args:
        request: 回転リクエスト (方向, 角度)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 回転結果
        
    Raises:
        HTTPException: 回転失敗時
    """
    try:
        # TODO: DroneServiceにrotateメソッドを実装する必要がある
        # 現在はスケルトン実装
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        if not hasattr(drone_service, '_is_flying') or not drone_service._is_flying:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが飛行中でない",
                    code=ErrorCode.NOT_FLYING
                ).model_dump()
            )
        
        # スケルトン実装 - 実際のドローン制御は後続で実装
        return StatusResponse(
            success=True,
            message=f"{request.direction.value}方向に{request.angle}度回転しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"回転エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/flip", response_model=StatusResponse)
async def flip_drone(request: FlipRequest, drone_service: DroneServiceDep):
    """
    宙返り
    
    Args:
        request: 宙返りリクエスト (方向)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 宙返り結果
        
    Raises:
        HTTPException: 宙返り失敗時
    """
    try:
        # TODO: DroneServiceにflipメソッドを実装する必要がある
        # 現在はスケルトン実装
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        if not hasattr(drone_service, '_is_flying') or not drone_service._is_flying:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが飛行中でない",
                    code=ErrorCode.NOT_FLYING
                ).model_dump()
            )
        
        # スケルトン実装 - 実際のドローン制御は後続で実装
        return StatusResponse(
            success=True,
            message=f"{request.direction.value}方向に宙返りしました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"宙返りエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )