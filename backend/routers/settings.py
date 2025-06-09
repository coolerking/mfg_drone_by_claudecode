"""
設定管理API
WiFi設定・任意コマンド・飛行速度設定機能
"""

from fastapi import APIRouter, HTTPException
from models.requests import WiFiRequest, CommandRequest, SpeedRequest
from models.responses import StatusResponse, CommandResponse, ErrorResponse, ErrorCode
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Settings"])


@router.put(
    "/wifi",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なWiFiパラメータ"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="WiFi接続設定",
    description="ドローンのWiFi接続を設定します"
)
async def set_wifi(request: WiFiRequest, drone_service: DroneServiceDep):
    """WiFi接続設定"""
    try:
        result = await drone_service.set_wifi(
            ssid=request.ssid,
            password=request.password
        )
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "パラメータ" in result["message"] or "無効" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"]:
                status_code = 503
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
                error=f"WiFi設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post(
    "/command",
    response_model=CommandResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効なコマンド"},
        408: {"model": ErrorResponse, "description": "コマンドタイムアウト"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="任意コマンド送信",
    description="Tello SDKコマンドを直接送信します"
)
async def send_command(request: CommandRequest, drone_service: DroneServiceDep):
    """任意コマンド送信"""
    try:
        result = await drone_service.send_command(
            command=request.command,
            timeout=request.timeout,
            expect_response=request.expect_response
        )
        if result["success"]:
            return CommandResponse(
                success=True,
                response=result["response"]
            )
        else:
            if "タイムアウト" in result["message"]:
                status_code = 408
                error_code = ErrorCode.COMMAND_TIMEOUT
            elif "無効" in result["message"] or "パラメータ" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"]:
                status_code = 503
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
                error=f"コマンド送信エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.put(
    "/speed",
    response_model=StatusResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無効な速度値"},
        409: {"model": ErrorResponse, "description": "ドローンが飛行中"},
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="飛行速度設定",
    description="ドローンの飛行速度を設定します"
)
async def set_speed(request: SpeedRequest, drone_service: DroneServiceDep):
    """飛行速度設定"""
    try:
        result = await drone_service.set_speed(speed=request.speed)
        if result["success"]:
            return StatusResponse(
                success=True,
                message=result["message"]
            )
        else:
            if "飛行中" in result["message"]:
                status_code = 409
                error_code = ErrorCode.ALREADY_FLYING
            elif "無効" in result["message"] or "速度" in result["message"]:
                status_code = 400
                error_code = ErrorCode.INVALID_PARAMETER
            elif "接続" in result["message"]:
                status_code = 503
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
                error=f"速度設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )