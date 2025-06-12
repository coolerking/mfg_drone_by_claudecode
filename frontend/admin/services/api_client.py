"""
API Client Service
バックエンドAPIとの通信を担当するクライアント
"""

import aiohttp
import asyncio
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BackendAPIClient:
    """バックエンドAPIクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """非同期コンテキストマネージャーの開始"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        if self.session:
            await self.session.close()
    
    def _sync_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """同期リクエスト（Flask-SocketIOハンドラー用）"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            return {
                "success": response.status_code < 400,
                "data": response.json() if response.content else {},
                "status_code": response.status_code
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "data": {"error": str(e)},
                "status_code": 500
            }
    
    async def _async_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """非同期リクエスト"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    data = await response.json()
                except:
                    data = {}
                return {
                    "success": response.status < 400,
                    "data": data,
                    "status_code": response.status
                }
        except Exception as e:
            logger.error(f"Async request failed: {e}")
            return {
                "success": False,
                "data": {"error": str(e)},
                "status_code": 500
            }
    
    # システム関連
    def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        return self._sync_request("GET", "/health")
    
    # ドローン接続管理
    def connect_drone(self) -> Dict[str, Any]:
        """ドローン接続"""
        return self._sync_request("POST", "/drone/connect")
    
    def disconnect_drone(self) -> Dict[str, Any]:
        """ドローン切断"""
        return self._sync_request("POST", "/drone/disconnect")
    
    # 基本飛行制御
    def takeoff(self) -> Dict[str, Any]:
        """離陸"""
        return self._sync_request("POST", "/drone/takeoff")
    
    def land(self) -> Dict[str, Any]:
        """着陸"""
        return self._sync_request("POST", "/drone/land")
    
    def emergency_stop(self) -> Dict[str, Any]:
        """緊急停止"""
        return self._sync_request("POST", "/drone/emergency")
    
    def hover(self) -> Dict[str, Any]:
        """ホバリング"""
        return self._sync_request("POST", "/drone/stop")
    
    # 基本移動制御
    def move_drone(self, direction: str, distance: int) -> Dict[str, Any]:
        """基本移動"""
        return self._sync_request("POST", "/drone/move", json={
            "direction": direction,
            "distance": distance
        })
    
    def rotate_drone(self, direction: str, angle: int) -> Dict[str, Any]:
        """回転"""
        return self._sync_request("POST", "/drone/rotate", json={
            "direction": direction,
            "angle": angle
        })
    
    # センサー情報取得
    def get_drone_status(self) -> Dict[str, Any]:
        """ドローン状態取得"""
        return self._sync_request("GET", "/drone/status")
    
    def get_battery(self) -> Dict[str, Any]:
        """バッテリー残量取得"""
        return self._sync_request("GET", "/drone/battery")
    
    def get_height(self) -> Dict[str, Any]:
        """飛行高度取得"""
        return self._sync_request("GET", "/drone/height")
    
    def get_temperature(self) -> Dict[str, Any]:
        """ドローン温度取得"""
        return self._sync_request("GET", "/drone/temperature")
    
    # カメラ操作
    def start_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング開始"""
        return self._sync_request("POST", "/camera/stream/start")
    
    def stop_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング停止"""
        return self._sync_request("POST", "/camera/stream/stop")
    
    def take_photo(self) -> Dict[str, Any]:
        """写真撮影"""
        return self._sync_request("POST", "/camera/photo")
    
    # 物体追跡制御
    def start_tracking(self, target_object: str, tracking_mode: str = "center") -> Dict[str, Any]:
        """物体追跡開始"""
        return self._sync_request("POST", "/tracking/start", json={
            "target_object": target_object,
            "tracking_mode": tracking_mode
        })
    
    def stop_tracking(self) -> Dict[str, Any]:
        """物体追跡停止"""
        return self._sync_request("POST", "/tracking/stop")
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """追跡状態取得"""
        return self._sync_request("GET", "/tracking/status")
    
    # モデル管理
    def get_model_list(self) -> Dict[str, Any]:
        """利用可能モデル一覧取得"""
        return self._sync_request("GET", "/model/list")

# グローバルAPIクライアントインスタンス
api_client = BackendAPIClient()