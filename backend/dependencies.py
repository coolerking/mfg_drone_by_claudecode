"""
依存性注入システム
FastAPI Depends()パターンによるサービス注入
"""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from services.drone_service import DroneService


@lru_cache()
def get_drone_service() -> DroneService:
    """DroneServiceのシングルトンインスタンスを取得"""
    return DroneService()


# 型エイリアス
DroneServiceDep = Annotated[DroneService, Depends(get_drone_service)]