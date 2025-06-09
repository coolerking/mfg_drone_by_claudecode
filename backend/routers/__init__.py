"""
APIルーター
各カテゴリ別のエンドポイント定義
"""

from .connection import router as connection_router
from .flight_control import router as flight_control_router
from .movement import router as movement_router
from .advanced_movement import router as advanced_movement_router
from .camera import router as camera_router
from .sensors import router as sensors_router
from .settings import router as settings_router
from .mission_pad import router as mission_pad_router
from .tracking import router as tracking_router
from .model import router as model_router

__all__ = [
    "connection_router",
    "flight_control_router", 
    "movement_router",
    "advanced_movement_router",
    "camera_router",
    "sensors_router",
    "settings_router",
    "mission_pad_router",
    "tracking_router",
    "model_router",
]