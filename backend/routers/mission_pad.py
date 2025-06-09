"""
ミッションパッド関連ルーター
Tello EDU専用のミッションパッド機能エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import MissionPadDetectionRequest, MissionPadGoXYZRequest
from models.responses import StatusResponse, MissionPadStatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/mission_pad",
    tags=["Mission Pad"],
    responses={
        503: {"model": ErrorResponse, "description": "Drone not connected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/enable", response_model=StatusResponse)
async def enable_mission_pad_detection(drone_service: DroneServiceDep):
    """
    ミッションパッド検出有効化
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 有効化結果
        
    Raises:
        HTTPException: 有効化失敗時
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
        
        # TODO: DroneServiceにenable_mission_pad_detectionメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="ミッションパッド検出を有効化しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ミッションパッド有効化エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/disable", response_model=StatusResponse)
async def disable_mission_pad_detection(drone_service: DroneServiceDep):
    """
    ミッションパッド検出無効化
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 無効化結果
        
    Raises:
        HTTPException: 無効化失敗時
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
        
        # TODO: DroneServiceにdisable_mission_pad_detectionメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="ミッションパッド検出を無効化しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ミッションパッド無効化エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.put("/detection_direction", response_model=StatusResponse)
async def set_mission_pad_detection_direction(request: MissionPadDetectionRequest, drone_service: DroneServiceDep):
    """
    ミッションパッド検出方向設定
    
    Args:
        request: 検出方向設定リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 設定結果
        
    Raises:
        HTTPException: 設定失敗時
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
        
        # 方向の説明マッピング
        direction_names = {
            0: "下向きのみ",
            1: "前向きのみ", 
            2: "両方向"
        }
        
        # TODO: DroneServiceにset_mission_pad_detection_directionメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message=f"ミッションパッド検出方向を{direction_names[request.direction]}に設定しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"検出方向設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/go_xyz", response_model=StatusResponse)
async def go_to_mission_pad_xyz(request: MissionPadGoXYZRequest, drone_service: DroneServiceDep):
    """
    ミッションパッド基準移動
    
    Args:
        request: ミッションパッド移動リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 移動結果
        
    Raises:
        HTTPException: 移動失敗時
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
        
        if not hasattr(drone_service, '_is_flying') or not drone_service._is_flying:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが飛行中でない",
                    code=ErrorCode.NOT_FLYING
                ).model_dump()
            )
        
        # TODO: DroneServiceにgo_to_mission_pad_xyzメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message=f"ミッションパッド{request.mission_pad_id}基準で"
                   f"座標({request.x}, {request.y}, {request.z})に移動しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ミッションパッド移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/status", response_model=MissionPadStatusResponse)
async def get_mission_pad_status(drone_service: DroneServiceDep):
    """
    ミッションパッド状態取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        MissionPadStatusResponse: ミッションパッド状態
        
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
        
        # TODO: DroneServiceにget_mission_pad_statusメソッドを実装する必要がある
        # 現在はスケルトン実装 - デフォルト値を返す
        return MissionPadStatusResponse(
            mission_pad_id=-1,  # -1 は検出なし
            distance_x=0,
            distance_y=0,
            distance_z=0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ミッションパッド状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )