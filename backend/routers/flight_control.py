"""
基本飛行制御API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Flight Control"]
)


@router.post("/takeoff", response_model=StatusResponse)
async def takeoff(drone_service: DroneServiceDep):
    """離陸"""
    try:
        result = drone_service.takeoff()
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
                error=f"離陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/land", response_model=StatusResponse)
async def land(drone_service: DroneServiceDep):
    """着陸"""
    try:
        result = drone_service.land()
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
                error=f"着陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/emergency", response_model=StatusResponse)
async def emergency(drone_service: DroneServiceDep):
    """緊急停止"""
    try:
        result = drone_service.emergency()
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
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                error=f"緊急停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/stop", response_model=StatusResponse)
async def stop(drone_service: DroneServiceDep):
    """ホバリング"""
    try:
        result = drone_service.stop()
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
                error=f"ホバリングエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )