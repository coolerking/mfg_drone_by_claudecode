"""
WebSocket API for real-time drone communication
Provides real-time status updates, camera streaming, and control
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIWebSocketRoute
import websockets

from ..core.drone_manager import DroneManager
from ..models.drone_models import DroneStatus

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket接続マネージャー"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.drone_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.status_broadcast_task: Optional[asyncio.Task] = None
        
    async def connect(self, websocket: WebSocket):
        """新しい接続を受け入れ"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # 初回接続時にスタートアップメッセージを送信
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """接続を切断"""
        self.active_connections.discard(websocket)
        
        # ドローン購読から削除
        for drone_id, subscribers in self.drone_subscriptions.items():
            subscribers.discard(websocket)
        
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """個別にメッセージを送信"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """全接続にブロードキャスト"""
        if not self.active_connections:
            return
            
        message_text = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(connection)
        
        # 切断された接続を削除
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_drone_subscribers(self, drone_id: str, message: dict):
        """特定のドローン購読者にメッセージを送信"""
        if drone_id not in self.drone_subscriptions:
            return
            
        subscribers = self.drone_subscriptions[drone_id].copy()
        message_text = json.dumps(message)
        disconnected = set()
        
        for connection in subscribers:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error sending to drone subscriber: {e}")
                disconnected.add(connection)
        
        # 切断された接続を削除
        for connection in disconnected:
            self.disconnect(connection)
    
    def subscribe_to_drone(self, websocket: WebSocket, drone_id: str):
        """ドローンの状態更新を購読"""
        if drone_id not in self.drone_subscriptions:
            self.drone_subscriptions[drone_id] = set()
        
        self.drone_subscriptions[drone_id].add(websocket)
        logger.info(f"WebSocket subscribed to drone {drone_id}")
    
    def unsubscribe_from_drone(self, websocket: WebSocket, drone_id: str):
        """ドローンの状態更新購読を解除"""
        if drone_id in self.drone_subscriptions:
            self.drone_subscriptions[drone_id].discard(websocket)
            logger.info(f"WebSocket unsubscribed from drone {drone_id}")


# グローバル接続マネージャー
manager = ConnectionManager()


class WebSocketHandler:
    """WebSocketメッセージハンドラー"""
    
    def __init__(self, drone_manager: DroneManager):
        self.drone_manager = drone_manager
    
    async def handle_message(self, websocket: WebSocket, message: dict):
        """受信メッセージを処理"""
        message_type = message.get("type")
        
        try:
            if message_type == "subscribe_drone":
                await self._handle_subscribe_drone(websocket, message)
            elif message_type == "unsubscribe_drone":
                await self._handle_unsubscribe_drone(websocket, message)
            elif message_type == "get_drone_status":
                await self._handle_get_drone_status(websocket, message)
            elif message_type == "get_all_drones":
                await self._handle_get_all_drones(websocket, message)
            elif message_type == "ping":
                await self._handle_ping(websocket, message)
            else:
                await manager.send_personal_message(websocket, {
                    "type": "error",
                    "error_code": "UNKNOWN_MESSAGE_TYPE",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MESSAGE_PROCESSING_ERROR",
                "message": f"Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_subscribe_drone(self, websocket: WebSocket, message: dict):
        """ドローン購読処理"""
        drone_id = message.get("drone_id")
        if not drone_id:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MISSING_DRONE_ID",
                "message": "drone_id is required for subscription",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        manager.subscribe_to_drone(websocket, drone_id)
        
        # 現在の状態を即座に送信
        try:
            status = await self.drone_manager.get_drone_status(drone_id)
            await manager.send_personal_message(websocket, {
                "type": "drone_status",
                "drone_id": drone_id,
                "status": status.model_dump(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "subscription_error",
                "drone_id": drone_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_unsubscribe_drone(self, websocket: WebSocket, message: dict):
        """ドローン購読解除処理"""
        drone_id = message.get("drone_id")
        if not drone_id:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MISSING_DRONE_ID", 
                "message": "drone_id is required for unsubscription",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        manager.unsubscribe_from_drone(websocket, drone_id)
        await manager.send_personal_message(websocket, {
            "type": "unsubscribed",
            "drone_id": drone_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_get_drone_status(self, websocket: WebSocket, message: dict):
        """ドローン状態取得処理"""
        drone_id = message.get("drone_id")
        if not drone_id:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MISSING_DRONE_ID",
                "message": "drone_id is required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        try:
            status = await self.drone_manager.get_drone_status(drone_id)
            await manager.send_personal_message(websocket, {
                "type": "drone_status",
                "drone_id": drone_id,
                "status": status.model_dump(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "DRONE_STATUS_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_get_all_drones(self, websocket: WebSocket, message: dict):
        """全ドローン取得処理"""
        try:
            drones = await self.drone_manager.get_available_drones()
            await manager.send_personal_message(websocket, {
                "type": "all_drones",
                "drones": [drone.model_dump() for drone in drones],
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "DRONES_LIST_ERROR",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_ping(self, websocket: WebSocket, message: dict):
        """pingメッセージ処理"""
        await manager.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })


async def start_status_broadcaster(drone_manager: DroneManager):
    """定期的なドローン状態ブロードキャストを開始"""
    while True:
        try:
            if manager.drone_subscriptions:
                for drone_id, subscribers in manager.drone_subscriptions.items():
                    if subscribers:  # 購読者がいる場合のみ
                        try:
                            status = await drone_manager.get_drone_status(drone_id)
                            await manager.send_to_drone_subscribers(drone_id, {
                                "type": "drone_status_update",
                                "drone_id": drone_id,
                                "status": status.model_dump(),
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as e:
                            logger.error(f"Error broadcasting status for drone {drone_id}: {e}")
            
            await asyncio.sleep(1.0)  # 1秒間隔で更新
            
        except Exception as e:
            logger.error(f"Error in status broadcaster: {e}")
            await asyncio.sleep(5.0)  # エラー時は5秒待機


def get_connection_manager() -> ConnectionManager:
    """接続マネージャーを取得"""
    return manager