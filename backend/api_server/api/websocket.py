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
            # Phase 6: Real drone specific message types
            elif message_type == "scan_real_drones":
                await self._handle_scan_real_drones(websocket, message)
            elif message_type == "get_network_status":
                await self._handle_get_network_status(websocket, message)
            elif message_type == "verify_drone_connection":
                await self._handle_verify_drone_connection(websocket, message)
            elif message_type == "get_drone_type_info":
                await self._handle_get_drone_type_info(websocket, message)
            elif message_type == "start_auto_scan":
                await self._handle_start_auto_scan(websocket, message)
            elif message_type == "stop_auto_scan":
                await self._handle_stop_auto_scan(websocket, message)
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

    # Phase 6: Real drone specific WebSocket handlers

    async def _handle_scan_real_drones(self, websocket: WebSocket, message: dict):
        """実機ドローンスキャン処理"""
        timeout = message.get("timeout", 5.0)
        
        try:
            await manager.send_personal_message(websocket, {
                "type": "scan_started",
                "timeout": timeout,
                "timestamp": datetime.now().isoformat()
            })
            
            detected_drones = await self.drone_manager.scan_for_real_drones(timeout)
            
            await manager.send_personal_message(websocket, {
                "type": "scan_completed",
                "detected_drones": detected_drones,
                "count": len(detected_drones),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "SCAN_ERROR",
                "message": f"Failed to scan for real drones: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_get_network_status(self, websocket: WebSocket, message: dict):
        """ネットワーク状態取得処理"""
        try:
            network_status = await self.drone_manager.get_network_status()
            
            await manager.send_personal_message(websocket, {
                "type": "network_status",
                "status": network_status,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "NETWORK_STATUS_ERROR",
                "message": f"Failed to get network status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_verify_drone_connection(self, websocket: WebSocket, message: dict):
        """ドローン接続検証処理"""
        ip_address = message.get("ip_address")
        
        if not ip_address:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MISSING_IP_ADDRESS",
                "message": "ip_address is required for connection verification",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        try:
            verification_result = await self.drone_manager.verify_real_drone_connection(ip_address)
            
            await manager.send_personal_message(websocket, {
                "type": "connection_verification",
                "verification_result": verification_result,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "VERIFICATION_ERROR",
                "message": f"Failed to verify drone connection: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_get_drone_type_info(self, websocket: WebSocket, message: dict):
        """ドローンタイプ情報取得処理"""
        drone_id = message.get("drone_id")
        
        if not drone_id:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "MISSING_DRONE_ID",
                "message": "drone_id is required for type info",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        try:
            type_info = self.drone_manager.get_drone_type_info(drone_id)
            
            await manager.send_personal_message(websocket, {
                "type": "drone_type_info",
                "drone_id": drone_id,
                "type_info": type_info,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "TYPE_INFO_ERROR",
                "message": f"Failed to get drone type info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_start_auto_scan(self, websocket: WebSocket, message: dict):
        """自動スキャン開始処理"""
        interval_seconds = message.get("interval_seconds", 60.0)
        
        try:
            result = await self.drone_manager.start_auto_scan(interval_seconds)
            
            await manager.send_personal_message(websocket, {
                "type": "auto_scan_started",
                "interval_seconds": interval_seconds,
                "message": result.message,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "AUTO_SCAN_START_ERROR",
                "message": f"Failed to start auto scan: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_stop_auto_scan(self, websocket: WebSocket, message: dict):
        """自動スキャン停止処理"""
        try:
            result = await self.drone_manager.stop_auto_scan()
            
            await manager.send_personal_message(websocket, {
                "type": "auto_scan_stopped",
                "message": result.message,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            await manager.send_personal_message(websocket, {
                "type": "error",
                "error_code": "AUTO_SCAN_STOP_ERROR",
                "message": f"Failed to stop auto scan: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })


async def start_status_broadcaster(drone_manager: DroneManager):
    """定期的なドローン状態ブロードキャストを開始（Phase 6対応）"""
    while True:
        try:
            if manager.drone_subscriptions:
                for drone_id, subscribers in manager.drone_subscriptions.items():
                    if subscribers:  # 購読者がいる場合のみ
                        try:
                            status = await drone_manager.get_drone_status(drone_id)
                            
                            # 基本ステータス送信
                            status_message = {
                                "type": "drone_status_update",
                                "drone_id": drone_id,
                                "status": status.model_dump(),
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            # 実機ドローンの場合は追加情報を含める
                            try:
                                type_info = drone_manager.get_drone_type_info(drone_id)
                                if type_info.get("is_real_drone", False):
                                    status_message["real_drone_info"] = {
                                        "connection_state": type_info.get("connection_state"),
                                        "real_ip_address": type_info.get("real_ip_address"),
                                        "is_real_drone": True
                                    }
                            except Exception:
                                # タイプ情報取得に失敗してもステータス配信は継続
                                pass
                            
                            await manager.send_to_drone_subscribers(drone_id, status_message)
                            
                        except Exception as e:
                            logger.error(f"Error broadcasting status for drone {drone_id}: {e}")
            
            await asyncio.sleep(1.0)  # 1秒間隔で更新
            
        except Exception as e:
            logger.error(f"Error in status broadcaster: {e}")
            await asyncio.sleep(5.0)  # エラー時は5秒待機


async def start_network_broadcaster(drone_manager: DroneManager):
    """定期的なネットワーク状態ブロードキャストを開始（Phase 6新機能）"""
    last_network_status = {}
    broadcast_interval = 10.0  # 10秒間隔
    
    while True:
        try:
            # アクティブな接続がある場合のみブロードキャスト
            if manager.active_connections:
                try:
                    current_network_status = await drone_manager.get_network_status()
                    
                    # 前回と比較して変化があった場合のみブロードキャスト
                    if current_network_status != last_network_status:
                        network_message = {
                            "type": "network_status_update",
                            "network_status": current_network_status,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        await manager.broadcast(network_message)
                        last_network_status = current_network_status.copy()
                        
                except Exception as e:
                    logger.error(f"Error broadcasting network status: {e}")
            
            await asyncio.sleep(broadcast_interval)
            
        except Exception as e:
            logger.error(f"Error in network broadcaster: {e}")
            await asyncio.sleep(30.0)  # エラー時は30秒待機


async def start_real_drone_events_broadcaster(drone_manager: DroneManager):
    """実機ドローンイベントブロードキャストを開始（Phase 6新機能）"""
    detected_drones_history = set()
    check_interval = 5.0  # 5秒間隔でチェック
    
    while True:
        try:
            if manager.active_connections:
                try:
                    # 実機ドローンの検出状況をチェック
                    network_status = await drone_manager.get_network_status()
                    current_detected = set()
                    
                    if "network_service" in network_status:
                        last_detections = network_status["network_service"].get("last_detections", [])
                        current_detected = set(d["ip"] for d in last_detections)
                    
                    # 新しく検出されたドローン
                    newly_detected = current_detected - detected_drones_history
                    # 接続が失われたドローン
                    disconnected_drones = detected_drones_history - current_detected
                    
                    # 新規検出をブロードキャスト
                    for ip in newly_detected:
                        detection_event = {
                            "type": "real_drone_detected",
                            "ip_address": ip,
                            "timestamp": datetime.now().isoformat()
                        }
                        await manager.broadcast(detection_event)
                        logger.info(f"Real drone detected and broadcasted: {ip}")
                    
                    # 切断をブロードキャスト
                    for ip in disconnected_drones:
                        disconnection_event = {
                            "type": "real_drone_disconnected",
                            "ip_address": ip,
                            "timestamp": datetime.now().isoformat()
                        }
                        await manager.broadcast(disconnection_event)
                        logger.info(f"Real drone disconnection broadcasted: {ip}")
                    
                    detected_drones_history = current_detected
                    
                except Exception as e:
                    logger.error(f"Error broadcasting real drone events: {e}")
            
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Error in real drone events broadcaster: {e}")
            await asyncio.sleep(15.0)  # エラー時は15秒待機


def get_connection_manager() -> ConnectionManager:
    """接続マネージャーを取得"""
    return manager