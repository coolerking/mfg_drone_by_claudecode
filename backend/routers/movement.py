"""
基本移動制御API
基本的な移動・回転・宙返り機能
"""

from fastapi import APIRouter, HTTPException
from models.requests import MoveRequest, RotateRequest, FlipRequest
from models.responses import StatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Movement"])


@router.post(
    "/move",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="基本移動",
    description="指定方向に指定距離移動します"
)
async def move(request: MoveRequest, drone_service: DroneServiceDep):
    """基本移動"""
    try:
        result = await drone_service.move(
            direction=request.direction.value,
            distance=request.distance
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
                error=f"移動エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/rotate",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="回転",
    description="指定方向に指定角度回転します"
)
async def rotate(request: RotateRequest, drone_service: DroneServiceDep):
    """回転"""
    try:
        result = await drone_service.rotate(
            direction=request.direction.value,
            angle=request.angle
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
                error=f"回転エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/flip",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なパラメータ"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="宙返り",
    description="指定方向に宙返りします"
)
async def flip(request: FlipRequest, drone_service: DroneServiceDep):
    """宙返り"""
    try:
        result = await drone_service.flip(direction=request.direction.value)
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
                error=f"宙返りエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )