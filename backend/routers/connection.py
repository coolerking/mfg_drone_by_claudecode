"""
ドローン接続管理API
接続・切断の管理を行う
"""

from fastapi import APIRouter, HTTPException
from models.responses import StatusResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Connection"])


@router.post(
    "/connect",
    response_model=StatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "接続失敗"}
    },
    summary="ドローン接続",
    description="ドローンに接続します"
)
async def connect(drone_service: DroneServiceDep):
    """ドローン接続"""
    try:
        result = await drone_service.connect()
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
                    code=ErrorCode.DRONE_CONNECTION_FAILED
                ).model_dump()
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"接続エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/disconnect", 
    response_model=StatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "切断失敗"}
    },
    summary="ドローン切断",
    description="ドローンから切断します"
)
async def disconnect(drone_service: DroneServiceDep):
    """ドローン切断"""
    try:
        result = await drone_service.disconnect()
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"切断エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )