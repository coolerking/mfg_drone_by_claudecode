"""
基本移動制御API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import MoveRequest, RotateRequest, FlipRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Movement"]
)


@router.post("/move", response_model=StatusResponse)
async def move_drone(request: MoveRequest, drone_service: DroneServiceDep):
    """基本移動"""
    try:
        result = drone_service.move(request.direction.value, request.distance)
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
            elif "無効な方向" in result["message"]:
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
                error=f"移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/rotate", response_model=StatusResponse)
async def rotate_drone(request: RotateRequest, drone_service: DroneServiceDep):
    """回転"""
    try:
        result = drone_service.rotate(request.direction.value, request.angle)
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
            elif "無効な回転方向" in result["message"]:
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
                error=f"回転エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/flip", response_model=StatusResponse)
async def flip_drone(request: FlipRequest, drone_service: DroneServiceDep):
    """宙返り"""
    try:
        result = drone_service.flip(request.direction.value)
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
            elif "無効な宙返り方向" in result["message"]:
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
                error=f"宙返りエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )