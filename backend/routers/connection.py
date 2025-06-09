"""
ドローン接続管理API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Connection"]
)


@router.post("/connect", response_model=StatusResponse)
async def connect_drone(drone_service: DroneServiceDep):
    """ドローン接続"""
    try:
        result = drone_service.connect()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.DRONE_CONNECTION_FAILED
                ).dict()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"接続エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/disconnect", response_model=StatusResponse)
async def disconnect_drone(drone_service: DroneServiceDep):
    """ドローン切断"""
    try:
        result = drone_service.disconnect()
        if result["success"]:
            return StatusResponse(success=True, message=result["message"])
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.DRONE_CONNECTION_FAILED
                ).dict()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"切断エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )