"""
カメラ操作API
ビデオストリーミング・写真撮影・録画機能
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from models.requests import CameraSettingsRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/camera", tags=["Camera"])


@router.post(
    "/stream/start",
    response_model=StatusResponse,
    responses={
        409: {"model": ErrorResponse, "description": "ストリーミング既に開始済み"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ビデオストリーミング開始",
    description="ビデオストリーミングを開始します"
)
async def start_stream(drone_service: DroneServiceDep):
    """ビデオストリーミング開始"""
    try:
        result = await drone_service.start_stream()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "既に開始" in result["message"]:
                status_code = 409
                error_code = ErrorCode.STREAMING_ALREADY_STARTED
            elif "接続" in result["message"]:
                status_code = 503
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            else:
                status_code = 503
                error_code = ErrorCode.COMMAND_FAILED
            
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
                error=f"ストリーミング開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/stream/stop",
    response_model=StatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "ストリーミング未開始"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ビデオストリーミング停止",
    description="ビデオストリーミングを停止します"
)
async def stop_stream(drone_service: DroneServiceDep):
    """ビデオストリーミング停止"""
    try:
        result = await drone_service.stop_stream()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "未開始" in result["message"]:
                status_code = 404
                error_code = ErrorCode.STREAMING_NOT_STARTED
            elif "接続" in result["message"]:
                status_code = 503
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            else:
                status_code = 503
                error_code = ErrorCode.COMMAND_FAILED
            
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
                error=f"ストリーミング停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get(
    "/stream",
    responses={
        200: {"content": {"multipart/x-mixed-replace": {"schema": {"type": "string", "format": "binary"}}}},
        404: {"model": ErrorResponse, "description": "ストリーミング未開始"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ビデオストリーム取得",
    description="ビデオストリームを取得します"
)
async def get_stream(drone_service: DroneServiceDep):
    """ビデオストリーム取得"""
    try:
        stream_generator = await drone_service.get_stream()
        if stream_generator is None:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error="ストリーミングが開始されていません",
                    code=ErrorCode.STREAMING_NOT_STARTED
                ).model_dump()
            )
        
        return StreamingResponse(
            stream_generator,
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"ストリーム取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/photo",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="写真撮影",
    description="写真を撮影します"
)
async def take_photo(drone_service: DroneServiceDep):
    """写真撮影"""
    try:
        result = await drone_service.take_photo()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.COMMAND_FAILED
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"写真撮影エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/video/start",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="動画録画開始",
    description="動画録画を開始します"
)
async def start_video_recording(drone_service: DroneServiceDep):
    """動画録画開始"""
    try:
        result = await drone_service.start_video_recording()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.COMMAND_FAILED
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"録画開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/video/stop",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="動画録画停止",
    description="動画録画を停止します"
)
async def stop_video_recording(drone_service: DroneServiceDep):
    """動画録画停止"""
    try:
        result = await drone_service.stop_video_recording()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.COMMAND_FAILED
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"録画停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.put(
    "/settings",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="カメラ設定変更",
    description="カメラの設定を変更します"
)
async def update_camera_settings(request: CameraSettingsRequest, drone_service: DroneServiceDep):
    """カメラ設定変更"""
    try:
        result = await drone_service.update_camera_settings(
            resolution=request.resolution.value if request.resolution else None,
            fps=request.fps.value if request.fps else None,
            bitrate=request.bitrate
        )
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "パラメータ" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"]:
                status_code = 503
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            else:
                status_code = 503
                error_code = ErrorCode.COMMAND_FAILED
            
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
                error=f"カメラ設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )