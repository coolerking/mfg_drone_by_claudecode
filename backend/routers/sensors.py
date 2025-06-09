"""
センサー情報取得ルーター
ドローンの各種センサー情報エンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from dependencies import DroneServiceDep
from models.responses import (
    DroneStatus, BatteryResponse, HeightResponse, TemperatureResponse,
    FlightTimeResponse, BarometerResponse, DistanceTofResponse,
    AccelerationResponse, VelocityResponse, AttitudeResponse,
    ErrorResponse, ErrorCode, AccelerationData, VelocityData, AttitudeData
)

router = APIRouter(
    prefix="/drone",
    tags=["Sensors"],
    responses={
        503: {"model": ErrorResponse, "description": "Drone not connected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get("/status", response_model=DroneStatus)
async def get_drone_status(drone_service: DroneServiceDep):
    """
    ドローン状態取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        DroneStatus: ドローン総合状態
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        status_data = drone_service.get_status()
        
        if "error" in status_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error=status_data["error"],
                    code=ErrorCode.INTERNAL_ERROR
                ).model_dump()
            )
        
        return DroneStatus(**status_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/battery", response_model=BatteryResponse)
async def get_battery(drone_service: DroneServiceDep):
    """
    バッテリー残量取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        BatteryResponse: バッテリー残量
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        battery = drone_service.drone.get_battery()
        return BatteryResponse(battery=battery)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"バッテリー取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/height", response_model=HeightResponse)
async def get_height(drone_service: DroneServiceDep):
    """
    飛行高度取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        HeightResponse: 飛行高度
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        height = drone_service.drone.get_height()
        return HeightResponse(height=height)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"高度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/temperature", response_model=TemperatureResponse)
async def get_temperature(drone_service: DroneServiceDep):
    """
    ドローン温度取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        TemperatureResponse: ドローン温度
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        temperature = drone_service.drone.get_temperature()
        return TemperatureResponse(temperature=temperature)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"温度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/flight_time", response_model=FlightTimeResponse)
async def get_flight_time(drone_service: DroneServiceDep):
    """
    累積飛行時間取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        FlightTimeResponse: 累積飛行時間
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        flight_time = drone_service.drone.get_flight_time()
        return FlightTimeResponse(flight_time=flight_time)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"飛行時間取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/barometer", response_model=BarometerResponse)
async def get_barometer(drone_service: DroneServiceDep):
    """
    気圧センサー取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        BarometerResponse: 気圧値
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        barometer = drone_service.drone.get_barometer()
        return BarometerResponse(barometer=barometer)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"気圧取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/distance_tof", response_model=DistanceTofResponse)
async def get_distance_tof(drone_service: DroneServiceDep):
    """
    ToFセンサー距離取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        DistanceTofResponse: ToFセンサー距離
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        distance_tof = drone_service.drone.get_distance_tof()
        return DistanceTofResponse(distance_tof=distance_tof)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ToF距離取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/acceleration", response_model=AccelerationResponse)
async def get_acceleration(drone_service: DroneServiceDep):
    """
    加速度取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        AccelerationResponse: 加速度情報
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        acceleration = AccelerationData(
            x=drone_service.drone.get_acceleration_x(),
            y=drone_service.drone.get_acceleration_y(),
            z=drone_service.drone.get_acceleration_z()
        )
        return AccelerationResponse(acceleration=acceleration)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"加速度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/velocity", response_model=VelocityResponse)
async def get_velocity(drone_service: DroneServiceDep):
    """
    速度取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        VelocityResponse: 速度情報
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        velocity = VelocityData(
            x=drone_service.drone.get_speed_x(),
            y=drone_service.drone.get_speed_y(),
            z=drone_service.drone.get_speed_z()
        )
        return VelocityResponse(velocity=velocity)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"速度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/attitude", response_model=AttitudeResponse)
async def get_attitude(drone_service: DroneServiceDep):
    """
    姿勢角取得
    
    Args:
        drone_service: ドローンサービス
        
    Returns:
        AttitudeResponse: 姿勢角情報
        
    Raises:
        HTTPException: ドローン未接続時
    """
    try:
        if not hasattr(drone_service, '_is_connected') or not drone_service._is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error="ドローン未接続",
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).model_dump()
            )
        
        attitude = AttitudeData(
            pitch=drone_service.drone.get_pitch(),
            roll=drone_service.drone.get_roll(),
            yaw=drone_service.drone.get_yaw()
        )
        return AttitudeResponse(attitude=attitude)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"姿勢角取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )