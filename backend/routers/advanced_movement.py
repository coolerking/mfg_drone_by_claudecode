"""
高度な移動制御API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import GoXYZRequest, CurveXYZRequest, RCControlRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Advanced Movement"]
)


@router.post("/go_xyz", response_model=StatusResponse)
async def go_xyz(request: GoXYZRequest, drone_service: DroneServiceDep):
    """座標移動"""
    try:
        result = drone_service.go_xyz(request.x, request.y, request.z, request.speed)
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            # Check for specific error conditions
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "飛行していません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.NOT_FLYING
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
                error=f"座標移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/curve_xyz", response_model=StatusResponse)
async def curve_xyz(request: CurveXYZRequest, drone_service: DroneServiceDep):
    """曲線飛行"""
    try:
        result = drone_service.curve_xyz(
            request.x1, request.y1, request.z1,
            request.x2, request.y2, request.z2,
            request.speed
        )
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            # Check for specific error conditions
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "飛行していません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.NOT_FLYING
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
                error=f"曲線飛行エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/rc_control", response_model=StatusResponse)
async def rc_control(request: RCControlRequest, drone_service: DroneServiceDep):
    """リアルタイム制御"""
    try:
        result = drone_service.rc_control(
            request.left_right_velocity,
            request.forward_backward_velocity,
            request.up_down_velocity,
            request.yaw_velocity
        )
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            # Check for specific error conditions
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
                error=f"RC制御エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )