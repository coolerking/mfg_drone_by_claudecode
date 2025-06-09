"""
高度移動制御ルーター
座標移動・曲線飛行・リアルタイム制御エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import GoXYZRequest, CurveXYZRequest, RCControlRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Advanced Movement"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        409: {"model": ErrorResponse, "description": "Drone not flying"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/go_xyz", response_model=StatusResponse)
async def go_xyz(request: GoXYZRequest, drone_service: DroneServiceDep):
    """
    座標移動
    
    Args:
        request: 座標移動リクエスト (x, y, z, speed)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 移動結果
        
    Raises:
        HTTPException: 移動失敗時
    """
    try:
        # TODO: DroneServiceにgo_xyzメソッドを実装する必要がある
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
            message=f"座標({request.x}, {request.y}, {request.z})に速度{request.speed}cm/sで移動しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"座標移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/curve_xyz", response_model=StatusResponse)
async def curve_xyz(request: CurveXYZRequest, drone_service: DroneServiceDep):
    """
    曲線飛行
    
    Args:
        request: 曲線飛行リクエスト (中間点, 終点, 速度)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 曲線飛行結果
        
    Raises:
        HTTPException: 曲線飛行失敗時
    """
    try:
        # TODO: DroneServiceにcurve_xyzメソッドを実装する必要がある
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
            message=f"中間点({request.x1}, {request.y1}, {request.z1})経由で"
                   f"終点({request.x2}, {request.y2}, {request.z2})に曲線飛行しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"曲線飛行エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/rc_control", response_model=StatusResponse)
async def rc_control(request: RCControlRequest, drone_service: DroneServiceDep):
    """
    リアルタイム制御
    
    Args:
        request: リアルタイム制御リクエスト (各軸速度)
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 制御コマンド送信結果
        
    Raises:
        HTTPException: 制御失敗時
    """
    try:
        # TODO: DroneServiceにrc_controlメソッドを実装する必要がある
        # 現在はスケルトン実装
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # RC制御は飛行中でなくても使用可能
        
        # スケルトン実装 - 実際のドローン制御は後続で実装
        return StatusResponse(
            success=True,
            message="リアルタイム制御コマンドを送信しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"RC制御エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )