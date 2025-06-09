"""
基本飛行制御ルーター
離陸・着陸・緊急停止・ホバリングエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.responses import StatusResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Flight Control"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        409: {"model": ErrorResponse, "description": "Conflict - invalid state"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/takeoff", response_model=StatusResponse)
async def takeoff(drone_service: DroneServiceDep):
    """
    離陸
    
    Returns:
        StatusResponse: 離陸結果
        
    Raises:
        HTTPException: 離陸失敗時
    """
    try:
        result = drone_service.takeoff()
        if result["success"]:
            return StatusResponse(**result)
        else:
            # Check if it's a connection issue
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).model_dump()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).model_dump()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"離陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/land", response_model=StatusResponse)
async def land(drone_service: DroneServiceDep):
    """
    着陸
    
    Returns:
        StatusResponse: 着陸結果
        
    Raises:
        HTTPException: 着陸失敗時
    """
    try:
        result = drone_service.land()
        if result["success"]:
            return StatusResponse(**result)
        else:
            # Check specific error types
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).model_dump()
                )
            elif "飛行していません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.NOT_FLYING
                    ).model_dump()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).model_dump()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"着陸エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/emergency", response_model=StatusResponse)
async def emergency_stop(drone_service: DroneServiceDep):
    """
    緊急停止
    
    Returns:
        StatusResponse: 緊急停止結果
        
    Raises:
        HTTPException: 緊急停止失敗時
    """
    try:
        result = drone_service.emergency()
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"緊急停止エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/stop", response_model=StatusResponse)
async def hover_stop(drone_service: DroneServiceDep):
    """
    ホバリング
    
    Returns:
        StatusResponse: ホバリング結果
        
    Raises:
        HTTPException: ホバリング失敗時
    """
    try:
        result = drone_service.stop()
        if result["success"]:
            return StatusResponse(**result)
        else:
            # Check specific error types
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).model_dump()
                )
            elif "飛行していません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.NOT_FLYING
                    ).model_dump()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_FAILED
                    ).model_dump()
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ホバリングエラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )