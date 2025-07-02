"""
WebSocket API Tests
Tests for real-time drone communication via WebSocket
"""

import asyncio
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from backend.api_server.main import app
from backend.api_server.api.websocket import ConnectionManager, WebSocketHandler
from backend.api_server.core.drone_manager import DroneManager
from backend.api_server.models.drone_models import DroneStatus, Attitude


class TestConnectionManager:
    """ConnectionManager のテスト"""
    
    @pytest.fixture
    def manager(self):
        """テスト用ConnectionManagerインスタンス"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """モックWebSocketオブジェクト"""
        ws = Mock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        return ws
    
    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """WebSocket接続テスト"""
        await manager.connect(mock_websocket)
        
        assert mock_websocket in manager.active_connections
        mock_websocket.accept.assert_called_once()
        mock_websocket.send_text.assert_called_once()
        
        # 送信されたメッセージを確認
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "connection_established"
    
    def test_disconnect(self, manager, mock_websocket):
        """WebSocket切断テスト"""
        manager.active_connections.add(mock_websocket)
        manager.drone_subscriptions["drone_001"] = {mock_websocket}
        
        manager.disconnect(mock_websocket)
        
        assert mock_websocket not in manager.active_connections
        assert mock_websocket not in manager.drone_subscriptions["drone_001"]
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager, mock_websocket):
        """個人メッセージ送信テスト"""
        message = {"type": "test", "data": "test data"}
        
        await manager.send_personal_message(mock_websocket, message)
        
        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert json.loads(sent_data) == message
    
    @pytest.mark.asyncio
    async def test_broadcast(self, manager):
        """ブロードキャストテスト"""
        ws1 = Mock()
        ws1.send_text = AsyncMock()
        ws2 = Mock()
        ws2.send_text = AsyncMock()
        
        manager.active_connections.add(ws1)
        manager.active_connections.add(ws2)
        
        message = {"type": "broadcast", "data": "broadcast data"}
        await manager.broadcast(message)
        
        expected_data = json.dumps(message)
        ws1.send_text.assert_called_once_with(expected_data)
        ws2.send_text.assert_called_once_with(expected_data)
    
    @pytest.mark.asyncio
    async def test_send_to_drone_subscribers(self, manager):
        """ドローン購読者へのメッセージ送信テスト"""
        ws1 = Mock()
        ws1.send_text = AsyncMock()
        ws2 = Mock()
        ws2.send_text = AsyncMock()
        
        manager.drone_subscriptions["drone_001"] = {ws1, ws2}
        
        message = {"type": "drone_status", "drone_id": "drone_001"}
        await manager.send_to_drone_subscribers("drone_001", message)
        
        expected_data = json.dumps(message)
        ws1.send_text.assert_called_once_with(expected_data)
        ws2.send_text.assert_called_once_with(expected_data)
    
    def test_subscribe_to_drone(self, manager, mock_websocket):
        """ドローン購読テスト"""
        manager.subscribe_to_drone(mock_websocket, "drone_001")
        
        assert "drone_001" in manager.drone_subscriptions
        assert mock_websocket in manager.drone_subscriptions["drone_001"]
    
    def test_unsubscribe_from_drone(self, manager, mock_websocket):
        """ドローン購読解除テスト"""
        manager.drone_subscriptions["drone_001"] = {mock_websocket}
        
        manager.unsubscribe_from_drone(mock_websocket, "drone_001")
        
        assert mock_websocket not in manager.drone_subscriptions["drone_001"]


class TestWebSocketHandler:
    """WebSocketHandler のテスト"""
    
    @pytest.fixture
    def mock_drone_manager(self):
        """モックDroneManagerインスタンス"""
        manager = Mock(spec=DroneManager)
        manager.get_drone_status = AsyncMock()
        manager.get_available_drones = AsyncMock()
        return manager
    
    @pytest.fixture
    def handler(self, mock_drone_manager):
        """テスト用WebSocketHandlerインスタンス"""
        return WebSocketHandler(mock_drone_manager)
    
    @pytest.fixture
    def mock_websocket(self):
        """モックWebSocketオブジェクト"""
        return Mock()
    
    @pytest.fixture
    def mock_manager(self):
        """モックConnectionManagerインスタンス"""
        manager = Mock()
        manager.send_personal_message = AsyncMock()
        manager.subscribe_to_drone = Mock()
        manager.unsubscribe_from_drone = Mock()
        return manager
    
    @pytest.mark.asyncio
    async def test_handle_subscribe_drone(self, handler, mock_websocket, mock_drone_manager):
        """ドローン購読メッセージ処理テスト"""
        # 正常なドローン状態を設定
        mock_status = DroneStatus(
            drone_id="drone_001",
            connection_status="connected",
            flight_status="flying",
            battery_level=85,
            last_updated=datetime.now()
        )
        mock_drone_manager.get_drone_status.return_value = mock_status
        
        message = {
            "type": "subscribe_drone",
            "drone_id": "drone_001"
        }
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            mock_manager.subscribe_to_drone = Mock()
            
            await handler.handle_message(mock_websocket, message)
            
            mock_manager.subscribe_to_drone.assert_called_once_with(mock_websocket, "drone_001")
            mock_drone_manager.get_drone_status.assert_called_once_with("drone_001")
            
            # 状態メッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "drone_status"
            assert sent_message["drone_id"] == "drone_001"
    
    @pytest.mark.asyncio
    async def test_handle_unsubscribe_drone(self, handler, mock_websocket):
        """ドローン購読解除メッセージ処理テスト"""
        message = {
            "type": "unsubscribe_drone",
            "drone_id": "drone_001"
        }
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            mock_manager.unsubscribe_from_drone = Mock()
            
            await handler.handle_message(mock_websocket, message)
            
            mock_manager.unsubscribe_from_drone.assert_called_once_with(mock_websocket, "drone_001")
            
            # 応答メッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "unsubscribed"
            assert sent_message["drone_id"] == "drone_001"
    
    @pytest.mark.asyncio
    async def test_handle_get_drone_status(self, handler, mock_websocket, mock_drone_manager):
        """ドローン状態取得メッセージ処理テスト"""
        mock_status = DroneStatus(
            drone_id="drone_001",
            connection_status="connected",
            flight_status="flying",
            battery_level=85,
            last_updated=datetime.now()
        )
        mock_drone_manager.get_drone_status.return_value = mock_status
        
        message = {
            "type": "get_drone_status",
            "drone_id": "drone_001"
        }
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            await handler.handle_message(mock_websocket, message)
            
            mock_drone_manager.get_drone_status.assert_called_once_with("drone_001")
            
            # 状態メッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "drone_status"
            assert sent_message["drone_id"] == "drone_001"
    
    @pytest.mark.asyncio
    async def test_handle_ping(self, handler, mock_websocket):
        """pingメッセージ処理テスト"""
        message = {"type": "ping"}
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            await handler.handle_message(mock_websocket, message)
            
            # pongメッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_handle_unknown_message_type(self, handler, mock_websocket):
        """未知のメッセージタイプ処理テスト"""
        message = {"type": "unknown_type"}
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            await handler.handle_message(mock_websocket, message)
            
            # エラーメッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "error"
            assert sent_message["error_code"] == "UNKNOWN_MESSAGE_TYPE"
    
    @pytest.mark.asyncio
    async def test_handle_missing_drone_id(self, handler, mock_websocket):
        """drone_id欠落エラーテスト"""
        message = {"type": "subscribe_drone"}  # drone_idなし
        
        with patch('backend.api_server.api.websocket.manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            await handler.handle_message(mock_websocket, message)
            
            # エラーメッセージが送信されることを確認
            mock_manager.send_personal_message.assert_called()
            sent_message = mock_manager.send_personal_message.call_args[0][1]
            assert sent_message["type"] == "error"
            assert sent_message["error_code"] == "MISSING_DRONE_ID"


@pytest.mark.asyncio
async def test_status_broadcaster():
    """状態ブロードキャスターのテスト"""
    mock_drone_manager = Mock(spec=DroneManager)
    mock_status = DroneStatus(
        drone_id="drone_001",
        connection_status="connected",
        flight_status="flying", 
        battery_level=85,
        last_updated=datetime.now()
    )
    mock_drone_manager.get_drone_status = AsyncMock(return_value=mock_status)
    
    mock_manager = Mock()
    mock_manager.drone_subscriptions = {"drone_001": {Mock()}}
    mock_manager.send_to_drone_subscribers = AsyncMock()
    
    with patch('backend.api_server.api.websocket.manager', mock_manager):
        # ブロードキャスターをテスト用に短時間実行
        broadcaster_task = asyncio.create_task(
            start_status_broadcaster(mock_drone_manager)
        )
        
        # 少し待ってからキャンセル
        await asyncio.sleep(0.1)
        broadcaster_task.cancel()
        
        try:
            await broadcaster_task
        except asyncio.CancelledError:
            pass
        
        # 状態更新が送信されることを確認
        assert mock_manager.send_to_drone_subscribers.called


class TestWebSocketIntegration:
    """WebSocket統合テスト"""
    
    def test_websocket_connection(self):
        """WebSocket接続統合テスト"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # 接続確立メッセージを受信
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # pingテスト
            websocket.send_text(json.dumps({"type": "ping"}))
            response = websocket.receive_text()
            response_data = json.loads(response)
            assert response_data["type"] == "pong"
    
    def test_websocket_invalid_json(self):
        """不正なJSONメッセージテスト"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # 接続確立メッセージを受信
            websocket.receive_text()
            
            # 不正なJSONを送信
            websocket.send_text("invalid json")
            response = websocket.receive_text()
            response_data = json.loads(response)
            assert response_data["type"] == "error"
            assert response_data["error_code"] == "INVALID_JSON"