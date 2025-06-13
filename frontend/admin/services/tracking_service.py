"""
MFG Drone Tracking Service
物体追跡API連携サービス
"""

import requests
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class TrackingService:
    """物体追跡API連携サービス"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize tracking service
        
        Args:
            base_url: バックエンドAPIのベースURL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def _build_url(self, endpoint: str) -> str:
        """エンドポイントURLを構築"""
        return urljoin(self.base_url, endpoint)
    
    def start_tracking(self, target_object: str, tracking_mode: str = "center") -> Dict[str, Any]:
        """
        物体追跡開始
        
        Args:
            target_object: 追跡対象オブジェクト名
            tracking_mode: 追跡モード ("center" or "follow")
            
        Returns:
            API応答データ
            
        Raises:
            requests.RequestException: API通信エラー
        """
        try:
            payload = {
                "target_object": target_object,
                "tracking_mode": tracking_mode
            }
            
            response = self.session.post(
                self._build_url("/tracking/start"),
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"追跡開始成功: target={target_object}, mode={tracking_mode}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"追跡開始エラー: {e}")
            raise
    
    def stop_tracking(self) -> Dict[str, Any]:
        """
        物体追跡停止
        
        Returns:
            API応答データ
            
        Raises:
            requests.RequestException: API通信エラー
        """
        try:
            response = self.session.post(
                self._build_url("/tracking/stop"),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info("追跡停止成功")
            return result
            
        except requests.RequestException as e:
            logger.error(f"追跡停止エラー: {e}")
            raise
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """
        追跡状態取得
        
        Returns:
            追跡状態データ
            {
                "is_tracking": bool,
                "target_object": str,
                "target_detected": bool,
                "target_position": {
                    "x": int,
                    "y": int,
                    "width": int,
                    "height": int
                }
            }
            
        Raises:
            requests.RequestException: API通信エラー
        """
        try:
            response = self.session.get(
                self._build_url("/tracking/status")
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.RequestException as e:
            logger.error(f"追跡状態取得エラー: {e}")
            raise
    
    async def get_tracking_status_async(self) -> Dict[str, Any]:
        """
        非同期で追跡状態取得
        
        Returns:
            追跡状態データ
            
        Raises:
            aiohttp.ClientError: API通信エラー
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._build_url("/tracking/status"),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"非同期追跡状態取得エラー: {e}")
            raise
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        利用可能モデル一覧取得（追跡対象選択用）
        
        Returns:
            モデル一覧データ
            
        Raises:
            requests.RequestException: API通信エラー
        """
        try:
            response = self.session.get(
                self._build_url("/model/list")
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.RequestException as e:
            logger.error(f"モデル一覧取得エラー: {e}")
            raise
    
    def close(self):
        """セッションクローズ"""
        if hasattr(self, 'session'):
            self.session.close()

# グローバルサービスインスタンス
tracking_service = TrackingService()