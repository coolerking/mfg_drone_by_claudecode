"""
依存性注入システム
FastAPI Depends()パターンによるサービス管理
"""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from services.drone_service import DroneService


@lru_cache()
def get_drone_service() -> DroneService:
    """
    ドローンサービスインスタンス取得
    シングルトンパターンで同一インスタンスを返す
    
    Returns:
        DroneService: ドローンサービスインスタンス
    """
    return DroneService()


# 型アノテーション付きの依存性
DroneServiceDep = Annotated[DroneService, Depends(get_drone_service)]


def get_health_info() -> dict:
    """
    ヘルスチェック情報取得
    
    Returns:
        dict: システム状態情報
    """
    return {
        "status": "healthy",
        "service": "MFG Drone Backend API",
        "version": "1.0.0"
    }