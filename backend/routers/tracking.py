"""
物体認識・追跡API
物体の検出・追跡機能
"""

from fastapi import APIRouter, HTTPException
from models.requests import TrackingStartRequest
from models.responses import StatusResponse, TrackingStatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/tracking", tags=["Object Tracking"])


@router.post(
    "/start",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        503: {"model": ErrorResponse, "description": "ドローン未接続またはカメラ未開始"}
    },
    summary="物体追跡開始",
    description="指定したオブジェクトの追跡を開始します"
)
async def start_tracking(request: TrackingStartRequest, drone_service: DroneServiceDep):
    """物体追跡開始"""
    try:
        result = await drone_service.start_tracking(
            target_object=request.target_object,
            tracking_mode=request.tracking_mode.value
        )
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "オブジェクト" in result["message"] or "無効" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"] or "カメラ" in result["message"]:
                status_code = 503
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            elif "モデル" in result["message"]:
                status_code = 400
                error_code = ErrorCode.MODEL_NOT_FOUND
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
                error=f"追跡開始エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/stop",
    response_model=StatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "追跡未開始"},
        503: {"model": ErrorResponse, "description": "追跡停止失敗"}
    },
    summary="物体追跡停止",
    description="現在実行中の物体追跡を停止します"
)
async def stop_tracking(drone_service: DroneServiceDep):
    """物体追跡停止"""
    try:
        result = await drone_service.stop_tracking()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "追跡していません" in result["message"] or "開始されていません" in result["message"]:
                status_code = 404
                error_code = ErrorCode.COMMAND_FAILED
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
                error=f"追跡停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get(
    "/status",
    response_model=TrackingStatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "追跡システム未初期化"}
    },
    summary="追跡状態取得",
    description="現在の物体追跡状態を取得します"
)
async def get_tracking_status(drone_service: DroneServiceDep):
    """追跡状態取得"""
    try:
        result = await drone_service.get_tracking_status()
        return TrackingStatusResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"追跡状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )