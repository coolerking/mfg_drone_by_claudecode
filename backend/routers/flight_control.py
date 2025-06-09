"""
基本飛行制御API
離陸・着陸・緊急停止・ホバリング機能
"""

from fastapi import APIRouter, HTTPException
from models.responses import StatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Flight Control"])


@router.post(
    "/takeoff",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "離陸失敗"}
    },
    summary="離陸",
    description="ドローンを離陸させます"
)
async def takeoff(drone_service: DroneServiceDep):
    """離陸"""
    try:
        result = await drone_service.takeoff()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            error_code = ErrorCode.DRONE_NOT_CONNECTED if "接続" in result["message"] else ErrorCode.COMMAND_FAILED
            raise HTTPException(
                status_code=400,
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
                error=f"離陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/land",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "着陸失敗"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="着陸", 
    description="ドローンを着陸させます"
)
async def land(drone_service: DroneServiceDep):
    """着陸"""
    try:
        result = await drone_service.land()
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
                error=f"着陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/emergency",
    response_model=StatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "緊急停止失敗"}
    },
    summary="緊急停止",
    description="ドローンを緊急停止させます"
)
async def emergency(drone_service: DroneServiceDep):
    """緊急停止"""
    try:
        result = await drone_service.emergency()
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.COMMAND_FAILED
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"緊急停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/stop",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "ホバリング失敗"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中でない"}
    },
    summary="ホバリング",
    description="ドローンをその場でホバリングさせます"
)
async def stop(drone_service: DroneServiceDep):
    """ホバリング"""
    try:
        result = await drone_service.stop()
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
                error=f"ホバリングエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )