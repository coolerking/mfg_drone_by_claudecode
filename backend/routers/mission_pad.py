"""
ミッションパッド関連API（Tello EDU専用）
ミッションパッド検出・制御機能
"""

from fastapi import APIRouter, HTTPException
from models.requests import MissionPadDetectionDirectionRequest, MissionPadGoXYZRequest
from models.responses import StatusResponse, MissionPadStatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/mission_pad", tags=["Mission Pad"])


@router.post(
    "/enable",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ミッションパッド検出有効化",
    description="ミッションパッド検出機能を有効化します（Tello EDU専用）"
)
async def enable_mission_pad(drone_service: DroneServiceDep):
    """ミッションパッド検出有効化"""
    try:
        result = await drone_service.enable_mission_pad()
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
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"ミッションパッド有効化エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/disable",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ミッションパッド検出無効化",
    description="ミッションパッド検出機能を無効化します"
)
async def disable_mission_pad(drone_service: DroneServiceDep):
    """ミッションパッド検出無効化"""
    try:
        result = await drone_service.disable_mission_pad()
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
                error=f"ミッションパッド無効化エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.put(
    "/detection_direction",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ミッションパッド検出方向設定",
    description="ミッションパッドの検出方向を設定します"
)
async def set_mission_pad_detection_direction(
    request: MissionPadDetectionDirectionRequest, 
    drone_service: DroneServiceDep
):
    """ミッションパッド検出方向設定"""
    try:
        result = await drone_service.set_mission_pad_detection_direction(
            direction=request.direction
        )
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "パラメータ" in result["message"] or "無効" in result["message"]:
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
            status_code=400,
            detail=ErrorResponse(
                error=f"検出方向設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/go_xyz",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="ミッションパッド基準移動",
    description="指定したミッションパッドを基準に座標移動します"
)
async def mission_pad_go_xyz(request: MissionPadGoXYZRequest, drone_service: DroneServiceDep):
    """ミッションパッド基準移動"""
    try:
        result = await drone_service.mission_pad_go_xyz(
            x=request.x,
            y=request.y,
            z=request.z,
            speed=request.speed,
            mission_pad_id=request.mission_pad_id
        )
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "飛行していません" in result["message"]:
                status_code = 409
                error_code = ErrorCode.NOT_FLYING
            elif "パラメータ" in result["message"] or "無効" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"]:
                status_code = 400
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            else:
                status_code = 400
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
            status_code=400,
            detail=ErrorResponse(
                error=f"ミッションパッド移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get(
    "/status",
    response_model=MissionPadStatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ミッションパッド状態取得",
    description="現在検出中のミッションパッド情報を取得します"
)
async def get_mission_pad_status(drone_service: DroneServiceDep):
    """ミッションパッド状態取得"""
    try:
        result = await drone_service.get_mission_pad_status()
        return MissionPadStatusResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"ミッションパッド状態取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )