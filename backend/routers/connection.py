"""
ドローン接続管理ルーター
ドローンとの接続・切断エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Connection"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/connect", response_model=StatusResponse)
async def connect_drone(drone_service: DroneServiceDep):
    """
    ドローン接続
    
    Returns:
        StatusResponse: 接続結果
        
    Raises:
        HTTPException: 接続失敗時
    """
    try:
        result = drone_service.connect()
        if result["success"]:
            return StatusResponse(**result)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.DRONE_CONNECTION_FAILED
                ).model_dump()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"接続エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/disconnect", response_model=StatusResponse)
async def disconnect_drone(drone_service: DroneServiceDep):
    """
    ドローン切断
    
    Returns:
        StatusResponse: 切断結果
        
    Raises:
        HTTPException: 切断失敗時
    """
    try:
        result = drone_service.disconnect()
        if result["success"]:
            return StatusResponse(**result)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=result["message"],
                    code=ErrorCode.COMMAND_FAILED
                ).model_dump()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"切断エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )