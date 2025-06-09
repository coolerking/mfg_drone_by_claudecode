"""
センサー情報取得API
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
    tags=["Sensors"]
)


@router.get("/status", response_model=DroneStatus)
async def get_drone_status(drone_service: DroneServiceDep):
    """ドローン状態取得"""
    try:
        result = drone_service.get_status()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        # Convert the result to proper response format
        response_data = {"connected": result.get("connected", False)}
        
        if result.get("connected"):
            response_data.update({
                "battery": result.get("battery"),
                "height": result.get("height"),
                "temperature": result.get("temperature"),
                "flight_time": result.get("flight_time"),
                "speed": result.get("speed"),
                "barometer": result.get("barometer"),
                "distance_tof": result.get("distance_tof"),
                "acceleration": AccelerationData(**result["acceleration"]) if result.get("acceleration") else None,
                "velocity": VelocityData(**result["velocity"]) if result.get("velocity") else None,
                "attitude": AttitudeData(**result["attitude"]) if result.get("attitude") else None
            })
        
        return DroneStatus(**response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"状態取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/battery", response_model=BatteryResponse)
async def get_battery(drone_service: DroneServiceDep):
    """バッテリー残量取得"""
    try:
        result = drone_service.get_battery()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return BatteryResponse(battery=result["battery"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"バッテリー取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/height", response_model=HeightResponse)
async def get_height(drone_service: DroneServiceDep):
    """飛行高度取得"""
    try:
        result = drone_service.get_height()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return HeightResponse(height=result["height"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"高度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/temperature", response_model=TemperatureResponse)
async def get_temperature(drone_service: DroneServiceDep):
    """ドローン温度取得"""
    try:
        result = drone_service.get_temperature()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return TemperatureResponse(temperature=result["temperature"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"温度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/flight_time", response_model=FlightTimeResponse)
async def get_flight_time(drone_service: DroneServiceDep):
    """累積飛行時間取得"""
    try:
        result = drone_service.get_flight_time()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return FlightTimeResponse(flight_time=result["flight_time"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"飛行時間取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/barometer", response_model=BarometerResponse)
async def get_barometer(drone_service: DroneServiceDep):
    """気圧センサー取得"""
    try:
        result = drone_service.get_barometer()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return BarometerResponse(barometer=result["barometer"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"気圧取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/distance_tof", response_model=DistanceTofResponse)
async def get_distance_tof(drone_service: DroneServiceDep):
    """ToFセンサー距離取得"""
    try:
        result = drone_service.get_distance_tof()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return DistanceTofResponse(distance_tof=result["distance_tof"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"ToF距離取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/acceleration", response_model=AccelerationResponse)
async def get_acceleration(drone_service: DroneServiceDep):
    """加速度取得"""
    try:
        result = drone_service.get_acceleration()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return AccelerationResponse(
            acceleration=AccelerationData(**result["acceleration"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"加速度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/velocity", response_model=VelocityResponse)
async def get_velocity(drone_service: DroneServiceDep):
    """速度取得"""
    try:
        result = drone_service.get_velocity()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return VelocityResponse(
            velocity=VelocityData(**result["velocity"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"速度取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )


@router.get("/attitude", response_model=AttitudeResponse)
async def get_attitude(drone_service: DroneServiceDep):
    """姿勢角取得"""
    try:
        result = drone_service.get_attitude()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error=result["error"],
                    code=ErrorCode.DRONE_NOT_CONNECTED
                ).dict()
            )
        
        return AttitudeResponse(
            attitude=AttitudeData(**result["attitude"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=f"姿勢角取得エラー: {str(e)}",
                code=ErrorCode.INTERNAL_ERROR
            ).dict()
        )