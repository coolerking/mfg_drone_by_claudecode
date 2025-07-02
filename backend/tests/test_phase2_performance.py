"""
Phase 2 Performance Tests
Performance and load tests for enhanced drone control and camera functionality
"""

import asyncio
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from backend.api_server.main import app
from backend.api_server.core.camera_service import CameraService
from backend.api_server.api.websocket import ConnectionManager
from backend.api_server.models.drone_models import Photo, SuccessResponse


class TestCameraPerformance:
    """カメラ機能パフォーマンステスト"""
    
    @pytest.mark.asyncio
    async def test_camera_stream_startup_time(self):
        """カメラストリーム起動時間テスト"""
        camera_service = CameraService()
        
        start_time = time.time()
        try:
            result = await camera_service.start_camera_stream("perf_test_drone")
            startup_time = time.time() - start_time
            
            assert result["success"] is True
            assert startup_time < 2.0, f"Camera stream startup took {startup_time:.2f}s, should be under 2s"
            
        finally:
            await camera_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_streams(self):
        """複数同時ストリーム性能テスト"""
        camera_service = CameraService()
        drone_count = 5
        
        start_time = time.time()
        try:
            # 複数ドローンのストリームを同時開始
            tasks = []
            for i in range(drone_count):
                task = camera_service.start_camera_stream(f"drone_{i:03d}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            setup_time = time.time() - start_time
            
            # 全ストリームが正常に開始されることを確認
            assert all(result["success"] for result in results)
            assert setup_time < 5.0, f"Multiple streams setup took {setup_time:.2f}s, should be under 5s"
            
            # ストリーム情報を取得
            info_list = await camera_service.get_all_streams_info()
            assert len(info_list) == drone_count
            
            # フレーム生成待機
            await asyncio.sleep(1.0)
            
            # 全ストリームからフレーム取得を並行実行
            frame_start = time.time()
            frame_tasks = []
            for i in range(drone_count):
                task = camera_service.get_current_frame_base64(f"drone_{i:03d}")
                frame_tasks.append(task)
            
            frames = await asyncio.gather(*frame_tasks)
            frame_time = time.time() - frame_start
            
            # 全フレームが取得できることを確認
            assert all(frame is not None for frame in frames)
            assert frame_time < 2.0, f"Frame capture took {frame_time:.2f}s, should be under 2s"
            
        finally:
            await camera_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_photo_capture_performance(self):
        """写真撮影パフォーマンステスト"""
        camera_service = CameraService()
        
        try:
            # ストリーム開始
            await camera_service.start_camera_stream("photo_perf_drone")
            await asyncio.sleep(0.5)  # ストリーム安定化待機
            
            # 連続写真撮影
            photo_count = 10
            start_time = time.time()
            
            photos = []
            for i in range(photo_count):
                photo = await camera_service.capture_photo("photo_perf_drone")
                photos.append(photo)
            
            total_time = time.time() - start_time
            avg_time = total_time / photo_count
            
            assert len(photos) == photo_count
            assert all(isinstance(photo, Photo) for photo in photos)
            assert avg_time < 0.5, f"Average photo capture time {avg_time:.3f}s, should be under 0.5s"
            
        finally:
            await camera_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_tracking_object_performance(self):
        """追跡オブジェクト性能テスト"""
        camera_service = CameraService()
        
        try:
            await camera_service.start_camera_stream("tracking_perf_drone")
            await asyncio.sleep(0.2)
            
            # 大量の追跡オブジェクトを追加
            object_count = 20
            start_time = time.time()
            
            for i in range(object_count):
                object_config = {
                    "type": "ball",
                    "position": [50 + i * 10, 50 + i * 5],
                    "size": [20, 20],
                    "color": [255, 0, 0],
                    "movement_pattern": "linear",
                    "movement_speed": 20.0
                }
                await camera_service.add_tracking_object("tracking_perf_drone", object_config)
            
            setup_time = time.time() - start_time
            assert setup_time < 2.0, f"Tracking objects setup took {setup_time:.2f}s, should be under 2s"
            
            # フレーム生成パフォーマンスを確認
            await asyncio.sleep(1.0)
            frame_start = time.time()
            frame = await camera_service.get_current_frame_base64("tracking_perf_drone")
            frame_time = time.time() - frame_start
            
            assert frame is not None
            assert frame_time < 0.1, f"Frame generation with tracking objects took {frame_time:.3f}s, should be under 0.1s"
            
        finally:
            await camera_service.shutdown()


class TestWebSocketPerformance:
    """WebSocket パフォーマンステスト"""
    
    def test_websocket_connection_throughput(self):
        """WebSocket接続スループットテスト"""
        client = TestClient(app)
        connection_count = 10
        
        start_time = time.time()
        connections = []
        
        try:
            # 複数のWebSocket接続を同時に確立
            for i in range(connection_count):
                ws = client.websocket_connect("/ws")
                connections.append(ws)
                
                # 接続確立メッセージを受信
                data = ws.receive_text()
                import json
                message = json.loads(data)
                assert message["type"] == "connection_established"
            
            connection_time = time.time() - start_time
            assert connection_time < 5.0, f"WebSocket connections took {connection_time:.2f}s, should be under 5s"
            
            # 全接続でpingテスト
            ping_start = time.time()
            for ws in connections:
                ws.send_text('{"type": "ping"}')
                response = ws.receive_text()
                response_data = json.loads(response)
                assert response_data["type"] == "pong"
            
            ping_time = time.time() - ping_start
            avg_ping = ping_time / connection_count
            assert avg_ping < 0.1, f"Average ping time {avg_ping:.3f}s, should be under 0.1s"
            
        finally:
            # 接続をクリーンアップ
            for ws in connections:
                try:
                    ws.close()
                except:
                    pass
    
    @pytest.mark.asyncio
    async def test_websocket_message_broadcasting_performance(self):
        """WebSocketメッセージブロードキャスト性能テスト"""
        manager = ConnectionManager()
        
        # 模擬WebSocket接続を大量作成
        mock_connections = []
        for i in range(50):
            mock_ws = Mock()
            mock_ws.send_text = AsyncMock()
            manager.active_connections.add(mock_ws)
            mock_connections.append(mock_ws)
        
        # ブロードキャストパフォーマンステスト
        message = {"type": "test_broadcast", "data": "performance test"}
        
        start_time = time.time()
        await manager.broadcast(message)
        broadcast_time = time.time() - start_time
        
        assert broadcast_time < 1.0, f"Broadcast to 50 connections took {broadcast_time:.3f}s, should be under 1s"
        
        # 全接続でメッセージが送信されたことを確認
        for mock_ws in mock_connections:
            mock_ws.send_text.assert_called_once()


class TestAPIEndpointPerformance:
    """APIエンドポイントパフォーマンステスト"""
    
    @pytest.fixture
    def client(self):
        """テスト用HTTPクライアント"""
        return TestClient(app)
    
    def test_drone_list_performance(self, client):
        """ドローン一覧取得パフォーマンステスト"""
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(return_value=[])
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
            # 複数回連続でリクエスト
            request_count = 20
            start_time = time.time()
            
            for _ in range(request_count):
                response = client.get("/api/drones")
                assert response.status_code == 200
            
            total_time = time.time() - start_time
            avg_time = total_time / request_count
            
            assert avg_time < 0.1, f"Average drone list request time {avg_time:.3f}s, should be under 0.1s"
    
    def test_concurrent_api_requests(self, client):
        """並行APIリクエストパフォーマンステスト"""
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(return_value=[])
        mock_manager.get_drone_status = AsyncMock(return_value=Mock())
        
        def make_request(endpoint):
            with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
                return client.get(endpoint)
        
        # 複数エンドポイントに並行リクエスト
        endpoints = ["/api/drones", "/health", "/"]
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(30):  # 各エンドポイントに10回ずつ
                for endpoint in endpoints:
                    future = executor.submit(make_request, endpoint)
                    futures.append(future)
            
            # 全リクエストの完了を待機
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # 全リクエストが成功することを確認
        assert all(result.status_code in [200, 422] for result in results)
        assert total_time < 10.0, f"Concurrent requests took {total_time:.2f}s, should be under 10s"
    
    def test_memory_efficiency_under_load(self, client):
        """負荷下でのメモリ効率テスト"""
        import psutil
        import os
        import gc
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(return_value=[])
        mock_manager.start_camera_stream = AsyncMock(return_value=SuccessResponse(message="Started"))
        mock_manager.stop_camera_stream = AsyncMock(return_value=SuccessResponse(message="Stopped"))
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
            # 大量のリクエストを処理
            for i in range(100):
                # ドローン一覧取得
                response = client.get("/api/drones")
                assert response.status_code == 200
                
                # カメラストリーム操作
                response = client.post(f"/api/drones/drone_{i:03d}/camera/stream/start")
                assert response.status_code == 200
                
                response = client.post(f"/api/drones/drone_{i:03d}/camera/stream/stop")
                assert response.status_code == 200
                
                # 定期的にガベージコレクション
                if i % 20 == 0:
                    gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # メモリ増加が20MB未満であることを確認
        assert memory_increase < 20 * 1024 * 1024, f"Memory increase {memory_increase / 1024 / 1024:.1f}MB is too high"


@pytest.mark.asyncio
async def test_end_to_end_performance():
    """エンドツーエンドパフォーマンステスト"""
    client = TestClient(app)
    
    # モック設定
    mock_manager = Mock()
    mock_manager.get_available_drones = AsyncMock(return_value=[])
    mock_manager.connect_drone = AsyncMock(return_value=SuccessResponse(message="Connected"))
    mock_manager.start_camera_stream = AsyncMock(return_value=SuccessResponse(message="Stream started"))
    mock_manager.capture_photo = AsyncMock(return_value=Photo(
        id="perf_photo",
        filename="perf_test.jpg",
        path="/photos/perf_test.jpg",
        timestamp=time.time(),
        drone_id="drone_001"
    ))
    mock_manager.stop_camera_stream = AsyncMock(return_value=SuccessResponse(message="Stream stopped"))
    mock_manager.disconnect_drone = AsyncMock(return_value=SuccessResponse(message="Disconnected"))
    
    with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
        # 完全なワークフローのパフォーマンステスト
        workflow_count = 5
        start_time = time.time()
        
        for i in range(workflow_count):
            drone_id = f"drone_{i:03d}"
            
            # 1. 接続
            response = client.post(f"/api/drones/{drone_id}/connect")
            assert response.status_code == 200
            
            # 2. カメラ開始
            response = client.post(f"/api/drones/{drone_id}/camera/stream/start")
            assert response.status_code == 200
            
            # 3. 写真撮影（複数回）
            for _ in range(3):
                response = client.post(f"/api/drones/{drone_id}/camera/photo")
                assert response.status_code == 200
            
            # 4. カメラ停止
            response = client.post(f"/api/drones/{drone_id}/camera/stream/stop")
            assert response.status_code == 200
            
            # 5. 切断
            response = client.post(f"/api/drones/{drone_id}/disconnect")
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        avg_workflow_time = total_time / workflow_count
        
        assert avg_workflow_time < 2.0, f"Average workflow time {avg_workflow_time:.2f}s, should be under 2s"
        assert total_time < 8.0, f"Total workflow time {total_time:.2f}s, should be under 8s"