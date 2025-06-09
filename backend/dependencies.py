"""
依存性注入システム
FastAPI Depends()を使用したサービス注入管理
"""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from services.drone_service import DroneService


@lru_cache()
def get_drone_service() -> DroneService:
    """
    DroneServiceのシングルトンインスタンスを取得
    
    Returns:
        DroneService: ドローンサービスインスタンス
    """
    return DroneService()


# 型エイリアス - より簡潔な注入用
DroneServiceDep = Annotated[DroneService, Depends(get_drone_service)]