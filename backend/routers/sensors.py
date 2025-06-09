"""
センサー情報取得API
ドローンの各種センサーデータ取得機能
"""

from fastapi import APIRouter, HTTPException
from models.responses import (
    DroneStatus, BatteryResponse, HeightResponse, TemperatureResponse,
    FlightTimeResponse, BarometerResponse, DistanceToFResponse,
    AccelerationResponse, VelocityResponse, AttitudeResponse,
    ErrorResponse, ErrorCode
)
from dependencies import DroneServiceDep

router = APIRouter(prefix="/drone", tags=["Sensors"])


@router.get(
    "/status",
    response_model=DroneStatus,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ドローン状態取得",
    description="ドローンの全体状態を取得します"
)
async def get_status(drone_service: DroneServiceDep):
    """ドローン状態取得"""
    try:
        result = await drone_service.get_status()
        if "error" in result:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        return DroneStatus(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get(
    "/battery",
    response_model=BatteryResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="バッテリー残量取得",
    description="バッテリー残量を取得します"
)
async def get_battery(drone_service: DroneServiceDep):
    """バッテリー残量取得"""
    try:
        battery = await drone_service.get_battery()
        return BatteryResponse(battery=battery)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"バッテリー情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/height",
    response_model=HeightResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="飛行高度取得",
    description="現在の飛行高度を取得します"
)
async def get_height(drone_service: DroneServiceDep):
    """飛行高度取得"""
    try:
        height = await drone_service.get_height()
        return HeightResponse(height=height)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"高度情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/temperature",
    response_model=TemperatureResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ドローン温度取得",
    description="ドローンの温度を取得します"
)
async def get_temperature(drone_service: DroneServiceDep):
    """ドローン温度取得"""
    try:
        temperature = await drone_service.get_temperature()
        return TemperatureResponse(temperature=temperature)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"温度情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/flight_time",
    response_model=FlightTimeResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="累積飛行時間取得",
    description="累積飛行時間を取得します"
)
async def get_flight_time(drone_service: DroneServiceDep):
    """累積飛行時間取得"""
    try:
        flight_time = await drone_service.get_flight_time()
        return FlightTimeResponse(flight_time=flight_time)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"飛行時間取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/barometer",
    response_model=BarometerResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="気圧センサー取得",
    description="気圧値を取得します"
)
async def get_barometer(drone_service: DroneServiceDep):
    """気圧センサー取得"""
    try:
        barometer = await drone_service.get_barometer()
        return BarometerResponse(barometer=barometer)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"気圧情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/distance_tof",
    response_model=DistanceToFResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="ToFセンサー距離取得",
    description="ToFセンサーの距離を取得します"
)
async def get_distance_tof(drone_service: DroneServiceDep):
    """ToFセンサー距離取得"""
    try:
        distance_tof = await drone_service.get_distance_tof()
        return DistanceToFResponse(distance_tof=distance_tof)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"ToFセンサー情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/acceleration",
    response_model=AccelerationResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="加速度取得",
    description="3軸加速度を取得します"
)
async def get_acceleration(drone_service: DroneServiceDep):
    """加速度取得"""
    try:
        acceleration = await drone_service.get_acceleration()
        return AccelerationResponse(acceleration=acceleration)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"加速度情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/velocity",
    response_model=VelocityResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="速度取得",
    description="3軸速度を取得します"
)
async def get_velocity(drone_service: DroneServiceDep):
    """速度取得"""
    try:
        velocity = await drone_service.get_velocity()
        return VelocityResponse(velocity=velocity)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"速度情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )


@router.get(
    "/attitude",
    response_model=AttitudeResponse,
    responses={
        503: {"model": ErrorResponse, "description": "ドローン未接続"}
    },
    summary="姿勢角取得",
    description="ピッチ・ロール・ヨー角を取得します"
)
async def get_attitude(drone_service: DroneServiceDep):
    """姿勢角取得"""
    try:
        attitude = await drone_service.get_attitude()
        return AttitudeResponse(attitude=attitude)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error=f"姿勢角情報取得エラー: {str(e)}",
                code=ErrorCode.DRONE_NOT_CONNECTED
            ).model_dump()
        )