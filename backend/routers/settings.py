"""
設定変更ルーター
WiFi設定・任意コマンド送信・飛行速度設定エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.requests import WiFiRequest, CommandRequest, SpeedRequest
from models.responses import StatusResponse, CommandResponse, ErrorResponse, ErrorCode

router = APIRouter(
    prefix="/drone",
    tags=["Settings"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        408: {"model": ErrorResponse, "description": "Command timeout"},
        409: {"model": ErrorResponse, "description": "Drone flying (for speed change)"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.put("/wifi", response_model=StatusResponse)
async def set_wifi_credentials(request: WiFiRequest, drone_service: DroneServiceDep):
    """
    WiFi接続設定
    
    Args:
        request: WiFi設定リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: WiFi設定結果
        
    Raises:
        HTTPException: WiFi設定失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # パラメータ検証
        if not request.ssid or len(request.ssid) > 32:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="無効なSSID",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        if not request.password or len(request.password) > 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="無効なパスワード",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # TODO: DroneServiceにset_wifi_credentialsメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message=f"WiFi設定を更新しました (SSID: {request.ssid})"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"WiFi設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/command", response_model=CommandResponse)
async def send_custom_command(request: CommandRequest, drone_service: DroneServiceDep):
    """
    任意コマンド送信
    
    Args:
        request: コマンドリクエスト
        drone_service: ドローンサービス
        
    Returns:
        CommandResponse: コマンド実行結果
        
    Raises:
        HTTPException: コマンド実行失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # 危険なコマンドのチェック（セキュリティ考慮）
        dangerous_commands = ["format", "rm", "del", "reboot", "shutdown"]
        if any(cmd in request.command.lower() for cmd in dangerous_commands):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="危険なコマンドは実行できません",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # TODO: DroneServiceにsend_custom_commandメソッドを実装する必要がある
        # 現在はスケルトン実装
        return CommandResponse(
            success=True,
            response=f"コマンド '{request.command}' を実行しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # タイムアウトエラーの場合
        if "timeout" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=ErrorResponse(
                    error="コマンドタイムアウト",
                    code=ErrorCode.COMMAND_TIMEOUT
                ).model_dump()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=f"コマンド実行エラー: {str(e)}",
                    code=ErrorCode.INTERNAL_ERROR
                ).model_dump()
            )


@router.put("/speed", response_model=StatusResponse)
async def set_flight_speed(request: SpeedRequest, drone_service: DroneServiceDep):
    """
    飛行速度設定
    
    Args:
        request: 速度設定リクエスト
        drone_service: ドローンサービス
        
    Returns:
        StatusResponse: 速度設定結果
        
    Raises:
        HTTPException: 速度設定失敗時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが接続されていません",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        # 飛行中は速度変更不可（一般的な制約）
        if hasattr(drone_service, '_is_flying') and drone_service._is_flying:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error="ドローンが飛行中です",
                    code=ErrorCode.ALREADY_FLYING
                ).model_dump()
            )
        
        # 速度範囲検証（Pydanticで既に検証済みだが、追加チェック）
        if request.speed < 1.0 or request.speed > 15.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="無効な速度値",
                    code=ErrorCode.INVALID_PARAMETER
                ).model_dump()
            )
        
        # TODO: DroneServiceにset_flight_speedメソッドを実装する必要がある
        # 現在はスケルトン実装
        return StatusResponse(
            success=True,
            message=f"飛行速度を{request.speed}m/sに設定しました"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"速度設定エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )