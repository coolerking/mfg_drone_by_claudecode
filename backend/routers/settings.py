"""
設定変更API
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import WiFiRequest, CommandRequest, SpeedRequest
from models.responses import StatusResponse, CommandResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Settings"]
)


@router.put("/wifi", response_model=StatusResponse)
async def set_wifi(request: WiFiRequest, drone_service: DroneServiceDep):
    """WiFi接続設定"""
    try:
        result = drone_service.set_wifi(request.ssid, request.password)
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
            elif "無効な" in result["message"]:
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
                error=f"WiFi設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.post("/command", response_model=CommandResponse)
async def send_command(request: CommandRequest, drone_service: DroneServiceDep):
    """任意コマンド送信"""
    try:
        result = drone_service.send_command(
            request.command, 
            request.timeout, 
            request.expect_response
        )
        if result["success"]:
            return CommandResponse(
                success=True, 
                response=result.get("response", "")
            )
        else:
            if "接続されていません" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.DRONE_NOT_CONNECTED
                    ).dict()
                )
            elif "タイムアウト" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.COMMAND_TIMEOUT
                    ).dict()
                )
            elif "無効な" in result["message"]:
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
                error=f"コマンド送信エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.put("/speed", response_model=StatusResponse)
async def set_speed(request: SpeedRequest, drone_service: DroneServiceDep):
    """飛行速度設定"""
    try:
        result = drone_service.set_speed(request.speed)
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
            elif "飛行中" in result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error=result["message"],
                        code=ErrorCode.ALREADY_FLYING
                    ).dict()
                )
            elif "無効な" in result["message"]:
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
                error=f"速度設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )