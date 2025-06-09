"""
カメラ操作API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import CameraSettingsRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/camera",
    tags=["Camera"]
)


@router.post("/stream/start", response_model=StatusResponse)
async def start_stream(drone_service: DroneServiceDep):
    """ビデオストリーミング開始"""
    try:
        result = drone_service.start_stream()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "既に開始済み" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.STREAMING_ALREADY_STARTED
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ストリーミング開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/stream/stop", response_model=StatusResponse)
async def stop_stream(drone_service: DroneServiceDep):
    """ビデオストリーミング停止"""
    try:
        result = drone_service.stop_stream()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "未開始" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.STREAMING_NOT_STARTED
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ストリーミング停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/photo", response_model=StatusResponse)
async def take_photo(drone_service: DroneServiceDep):
    """写真撮影"""
    try:
        result = drone_service.take_photo()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"写真撮影エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/video/start", response_model=StatusResponse)
async def start_video(drone_service: DroneServiceDep):
    """動画録画開始"""
    try:
        result = drone_service.start_video()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"動画録画開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/video/stop", response_model=StatusResponse)
async def stop_video(drone_service: DroneServiceDep):
    """動画録画停止"""
    try:
        result = drone_service.stop_video()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"動画録画停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.put("/settings", response_model=StatusResponse)
async def update_camera_settings(request: CameraSettingsRequest, drone_service: DroneServiceDep):
    """カメラ設定変更"""
    try:
        result = drone_service.set_camera_settings(
            resolution=request.resolution.value if request.resolution else None,
            fps=request.fps.value if request.fps else None,
            bitrate=request.bitrate
        )
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "無効な" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.INVALID_PARAMETER
                    ).dict()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).dict()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"カメラ設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )