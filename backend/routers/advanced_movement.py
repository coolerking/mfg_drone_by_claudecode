"""
高度な移動制御API
座標移動・曲線飛行・リアルタイム制御機能
"""

from fastapi import APIRouter, HTTPException
from models.requests import GoXYZRequest, CurveXYZRequest, RCControlRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Advanced Movement"])


@router.post(
    "/go_xyz",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="座標移動",
    description="指定座標に指定速度で移動します"
)
async def go_xyz(request: GoXYZRequest, drone_service: DroneServiceDep):
    """座標移動"""
    try:
        result = await drone_service.go_xyz(
            x=request.x,
            y=request.y,
            z=request.z,
            speed=request.speed
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
            elif "接続" in result["message"]:
                status_code = 400
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            elif "パラメータ" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
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
                error=f"座標移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/curve_xyz",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="曲線飛行",
    description="中間点を経由して曲線飛行します"
)
async def curve_xyz(request: CurveXYZRequest, drone_service: DroneServiceDep):
    """曲線飛行"""
    try:
        result = await drone_service.curve_xyz(
            x1=request.x1,
            y1=request.y1,
            z1=request.z1,
            x2=request.x2,
            y2=request.y2,
            z2=request.z2,
            speed=request.speed
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
            elif "接続" in result["message"]:
                status_code = 400
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            elif "パラメータ" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
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
                error=f"曲線飛行エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/rc_control",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="リアルタイム制御",
    description="リアルタイムで速度制御します"
)
async def rc_control(request: RCControlRequest, drone_service: DroneServiceDep):
    """リアルタイム制御"""
    try:
        result = await drone_service.rc_control(
            left_right_velocity=request.left_right_velocity,
            forward_backward_velocity=request.forward_backward_velocity,
            up_down_velocity=request.up_down_velocity,
            yaw_velocity=request.yaw_velocity
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
            elif "接続" in result["message"]:
                status_code = 400
                error_code = ErrorCode.DRONE_NOT_CONNECTED
            elif "パラメータ" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
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
                error=f"リアルタイム制御エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )