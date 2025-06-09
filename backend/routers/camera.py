"""
カメラ操作ルーター
ビデオストリーミング・写真撮影・動画録画・カメラ設定エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from dependencies import DroneServiceDep
from models.requests import CameraSettingsRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/camera",
    tags=["Camera"],
    responses={
        404: {"model": ErrorResponse, "description": "Streaming not started"},
        409: {"model": ErrorResponse, "description": "Streaming already started"},
        503: {"model": ErrorResponse, "description": "Drone not connected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/stream/start", response_model=StatusResponse)
async def start_video_streaming(drone_service: DroneServiceDep):
    """
    ビデオストリーミング開始
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: ストリーミング開始結果
        
    Raises:
        HTTPException: ストリーミング開始失敗時
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
        
        if hasattr(drone_service, '_is_streaming') and drone_service._is_streaming:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ストリーミング既に開始済み",
                    code=ErrorCode.STREAMING_ALREADY_STARTED
                ).model_dump()
            )
        
        # TODO: DroneServiceにstart_streamingメソッドを実装する必要がある
        # 現在はスケルトン実装
        if hasattr(drone_service, '_is_streaming'):
            drone_service._is_streaming = True
        
        return StatusResponse(
            success=True,
            message="ビデオストリーミングを開始しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ストリーミング開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/stream/stop", response_model=StatusResponse)
async def stop_video_streaming(drone_service: DroneServiceDep):
    """
    ビデオストリーミング停止
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: ストリーミング停止結果
        
    Raises:
        HTTPException: ストリーミング停止失敗時
    """
    try:
        # TODO: DroneServiceにstop_streamingメソッドを実装する必要がある
        # 現在はスケルトン実装
        if hasattr(drone_service, '_is_streaming'):
            drone_service._is_streaming = False
        
        return StatusResponse(
            success=True,
            message="ビデオストリーミングを停止しました"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ストリーミング停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/stream")
async def get_video_stream(drone_service: DroneServiceDep):
    """
    ビデオストリーム取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StreamingResponse: ビデオストリーム
        
    Raises:
        HTTPException: ストリーミング未開始またはドローン未接続時
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
        
        if not hasattr(drone_service, '_is_streaming') or not drone_service._is_streaming:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="ストリーミング未開始",
                    code=ErrorCode.STREAMING_NOT_STARTED
                ).model_dump()
            )
        
        # TODO: 実際のビデオストリーミング実装
        # 現在はスケルトン実装
        def generate_dummy_stream():
            yield b"--frame\r\n"
            yield b"Content-Type: image/jpeg\r\n\r\n"
            yield b"dummy frame data"
            yield b"\r\n"
        
        return StreamingResponse(
            generate_dummy_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ストリーミング取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/photo", response_model=StatusResponse)
async def take_photo(drone_service: DroneServiceDep):
    """
    写真撮影
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 撮影結果
        
    Raises:
        HTTPException: 撮影失敗時
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
        
        # TODO: DroneServiceにtake_photoメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="写真を撮影しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"撮影エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/video/start", response_model=StatusResponse)
async def start_video_recording(drone_service: DroneServiceDep):
    """
    動画録画開始
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 録画開始結果
        
    Raises:
        HTTPException: 録画開始失敗時
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
        
        # TODO: DroneServiceにstart_video_recordingメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="動画録画を開始しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"録画開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/video/stop", response_model=StatusResponse)
async def stop_video_recording(drone_service: DroneServiceDep):
    """
    動画録画停止
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 録画停止結果
        
    Raises:
        HTTPException: 録画停止失敗時
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
        
        # TODO: DroneServiceにstop_video_recordingメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message="動画録画を停止しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"録画停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.put("/settings", response_model=StatusResponse)
async def update_camera_settings(request: CameraSettingsRequest, drone_service: DroneServiceDep):
    """
    カメラ設定変更
    
    Args:
        request: カメラ設定リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 設定変更結果
        
    Raises:
        HTTPException: 設定変更失敗時
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
        
        # TODO: DroneServiceにupdate_camera_settingsメソッドを実装する必要がある
        # 現在はスケルトン実装
        settings_changed = []
        if request.resolution:
            settings_changed.append(f"解像度: {request.resolution.value}")
        if request.fps:
            settings_changed.append(f"FPS: {request.fps.value}")
        if request.bitrate:
            settings_changed.append(f"ビットレート: {request.bitrate}")
        
        return StatusResponse(
            success=True,
            message=f"カメラ設定を変更しました ({', '.join(settings_changed)})"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"設定変更エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )