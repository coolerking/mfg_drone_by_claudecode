"""
Enhanced Drone API Tests
Tests for Phase 2 enhanced drone control and camera functionality
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from backend.api_server.main import app
from backend.api_server.models.drone_models import DroneStatus, Photo, Attitude
from backend.api_server.models.common_models import SuccessResponse


class TestEnhancedDroneAPI:
    """拡張ドローンAPIのテスト"""
    
    @pytest.fixture
    def client(self):
        """テスト用HTTPクライアント"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_drone_manager(self):
        """モックDroneManagerインスタンス"""
        manager = Mock()
        manager.get_available_drones = AsyncMock()
        manager.connect_drone = AsyncMock()
        manager.disconnect_drone = AsyncMock() 
        manager.takeoff_drone = AsyncMock()
        manager.land_drone = AsyncMock()
        manager.move_drone = AsyncMock()
        manager.rotate_drone = AsyncMock()
        manager.emergency_stop_drone = AsyncMock()
        manager.get_drone_status = AsyncMock()
        manager.start_camera_stream = AsyncMock()
        manager.stop_camera_stream = AsyncMock()
        manager.capture_photo = AsyncMock()
        return manager
    
    def test_start_camera_stream_success(self, client, mock_drone_manager):
        """カメラストリーミング開始成功テスト"""
        success_response = SuccessResponse(
            message="ドローン drone_001 のカメラストリーミングを開始しました"
        )
        mock_drone_manager.start_camera_stream.return_value = success_response
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_001/camera/stream/start")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "drone_001" in data["message"]
            
            mock_drone_manager.start_camera_stream.assert_called_once_with("drone_001")
    
    def test_start_camera_stream_drone_not_found(self, client, mock_drone_manager):
        """存在しないドローンのカメラストリーミング開始テスト"""
        mock_drone_manager.start_camera_stream.side_effect = ValueError("Drone drone_999 not found")
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_999/camera/stream/start")
            
            assert response.status_code == 404
            data = response.json()
            assert "指定されたドローンが見つかりません" in data["detail"]
    
    def test_start_camera_stream_drone_not_connected(self, client, mock_drone_manager):
        """未接続ドローンのカメラストリーミング開始テスト"""
        mock_drone_manager.start_camera_stream.side_effect = ValueError("Drone drone_001 not connected")
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_001/camera/stream/start")
            
            assert response.status_code == 400
            data = response.json()
            assert "ドローンが接続されていません" in data["detail"]
    
    def test_stop_camera_stream_success(self, client, mock_drone_manager):
        """カメラストリーミング停止成功テスト"""
        success_response = SuccessResponse(
            message="ドローン drone_001 のカメラストリーミングを停止しました"
        )
        mock_drone_manager.stop_camera_stream.return_value = success_response
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_001/camera/stream/stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "drone_001" in data["message"]
            
            mock_drone_manager.stop_camera_stream.assert_called_once_with("drone_001")
    
    def test_capture_photo_success(self, client, mock_drone_manager):
        """写真撮影成功テスト"""
        test_photo = Photo(
            id="photo_123",
            filename="drone_photo_20230101_120000.jpg",
            path="/photos/drone_photo_20230101_120000.jpg",
            timestamp=datetime.now(),
            drone_id="drone_001",
            metadata={
                "resolution": "640x480",
                "format": "JPEG",
                "size_bytes": 12345
            }
        )
        mock_drone_manager.capture_photo.return_value = test_photo
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_001/camera/photo")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "photo_123"
            assert data["drone_id"] == "drone_001"
            assert data["filename"] == "drone_photo_20230101_120000.jpg"
            assert data["metadata"]["resolution"] == "640x480"
            
            mock_drone_manager.capture_photo.assert_called_once_with("drone_001")
    
    def test_capture_photo_drone_not_connected(self, client, mock_drone_manager):
        """未接続ドローンの写真撮影テスト"""
        mock_drone_manager.capture_photo.side_effect = ValueError("Drone drone_001 not connected")
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.post("/api/drones/drone_001/camera/photo")
            
            assert response.status_code == 400
            data = response.json()
            assert "ドローンが接続されていません" in data["detail"]
    
    def test_invalid_drone_id_format(self, client):
        """不正なドローンIDフォーマットテスト"""
        # 特殊文字を含むドローンID
        response = client.post("/api/drones/drone@001/camera/stream/start")
        assert response.status_code == 422  # Validation error
        
        # 空のドローンID
        response = client.post("/api/drones//camera/stream/start") 
        assert response.status_code == 404  # Not found (route mismatch)
    
    def test_enhanced_drone_status_with_camera_info(self, client, mock_drone_manager):
        """カメラ情報を含むドローン状態取得テスト"""
        test_status = DroneStatus(
            drone_id="drone_001",
            connection_status="connected",
            flight_status="flying",
            battery_level=85,
            flight_time=300,
            height=150,
            temperature=25.5,
            speed=2.5,
            wifi_signal=90,
            attitude=Attitude(pitch=0.0, roll=0.0, yaw=45.0),
            last_updated=datetime.now()
        )
        mock_drone_manager.get_drone_status.return_value = test_status
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            response = client.get("/api/drones/drone_001/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["drone_id"] == "drone_001"
            assert data["connection_status"] == "connected"
            assert data["flight_status"] == "flying"
            assert data["battery_level"] == 85
            assert data["flight_time"] == 300
            assert data["height"] == 150
            assert data["temperature"] == 25.5
            assert data["speed"] == 2.5
            assert data["wifi_signal"] == 90
            assert data["attitude"]["yaw"] == 45.0
    
    def test_move_drone_enhanced_validation(self, client, mock_drone_manager):
        """移動コマンドの拡張バリデーションテスト"""
        success_response = SuccessResponse(message="移動開始")
        mock_drone_manager.move_drone.return_value = success_response
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            # 正常な移動コマンド
            valid_command = {"direction": "forward", "distance": 100}
            response = client.post("/api/drones/drone_001/move", json=valid_command)
            assert response.status_code == 200
            
            # 距離が範囲外
            invalid_command = {"direction": "forward", "distance": 600}  # 最大500cm
            response = client.post("/api/drones/drone_001/move", json=invalid_command)
            assert response.status_code == 422
            
            # 距離が最小値未満
            invalid_command = {"direction": "forward", "distance": 10}  # 最小20cm
            response = client.post("/api/drones/drone_001/move", json=invalid_command)
            assert response.status_code == 422
            
            # 無効な方向
            invalid_command = {"direction": "invalid", "distance": 100}
            response = client.post("/api/drones/drone_001/move", json=invalid_command)
            assert response.status_code == 422
    
    def test_rotate_drone_enhanced_validation(self, client, mock_drone_manager):
        """回転コマンドの拡張バリデーションテスト"""
        success_response = SuccessResponse(message="回転開始")
        mock_drone_manager.rotate_drone.return_value = success_response
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_drone_manager):
            # 正常な回転コマンド
            valid_command = {"direction": "clockwise", "angle": 90}
            response = client.post("/api/drones/drone_001/rotate", json=valid_command)
            assert response.status_code == 200
            
            # 角度が範囲外
            invalid_command = {"direction": "clockwise", "angle": 400}  # 最大360度
            response = client.post("/api/drones/drone_001/rotate", json=invalid_command)
            assert response.status_code == 422
            
            # 角度が最小値未満
            invalid_command = {"direction": "clockwise", "angle": 0}  # 最小1度
            response = client.post("/api/drones/drone_001/rotate", json=invalid_command)
            assert response.status_code == 422
            
            # 無効な方向
            invalid_command = {"direction": "invalid", "angle": 90}
            response = client.post("/api/drones/drone_001/rotate", json=invalid_command)
            assert response.status_code == 422


class TestDroneAPIErrorHandling:
    """ドローンAPIエラーハンドリングテスト"""
    
    @pytest.fixture
    def client(self):
        """テスト用HTTPクライアント"""
        return TestClient(app)
    
    def test_general_exception_handling(self, client):
        """一般例外ハンドリングテスト"""
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(side_effect=Exception("Unexpected error"))
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
            response = client.get("/api/drones")
            
            assert response.status_code == 500
            data = response.json()
            assert data["error"] is True
            assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    
    def test_drone_manager_not_initialized(self, client):
        """ドローンマネージャー未初期化エラーテスト"""
        with patch('backend.api_server.main.drone_manager', None):
            response = client.get("/api/drones")
            
            assert response.status_code == 503
            data = response.json()
            assert "Drone manager not initialized" in data["detail"]
    
    def test_concurrent_requests_handling(self, client):
        """並行リクエスト処理テスト"""
        import threading
        import time
        
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock()
        
        results = []
        
        def make_request():
            with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
                response = client.get("/api/drones")
                results.append(response.status_code)
        
        # 複数スレッドで同時リクエスト
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 全リクエストが正常に処理されることを確認
        assert len(results) == 5
        assert all(status == 200 for status in results)


class TestDroneAPIPerformance:
    """ドローンAPIパフォーマンステスト"""
    
    @pytest.fixture
    def client(self):
        """テスト用HTTPクライアント"""
        return TestClient(app)
    
    def test_response_time_benchmark(self, client):
        """レスポンス時間ベンチマークテスト"""
        import time
        
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(return_value=[])
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
            start_time = time.time()
            response = client.get("/api/drones")
            end_time = time.time()
            
            assert response.status_code == 200
            
            # レスポンス時間が1秒未満であることを確認
            response_time = end_time - start_time
            assert response_time < 1.0, f"Response time {response_time} seconds is too slow"
    
    def test_memory_usage_stability(self, client):
        """メモリ使用量安定性テスト"""
        import gc
        import psutil
        import os
        
        mock_manager = Mock()
        mock_manager.get_available_drones = AsyncMock(return_value=[])
        
        # ベースラインメモリ使用量を取得
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
            # 複数回リクエストを実行
            for _ in range(10):
                response = client.get("/api/drones")
                assert response.status_code == 200
                gc.collect()  # ガベージコレクション実行
            
            # 最終メモリ使用量を確認
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # メモリ増加が10MB未満であることを確認（メモリリーク防止）
            assert memory_increase < 10 * 1024 * 1024, f"Memory increase {memory_increase} bytes is too high"


@pytest.mark.asyncio
async def test_api_integration_with_camera_workflow():
    """カメラワークフロー統合テスト"""
    client = TestClient(app)
    
    # モックマネージャーを設定
    mock_manager = Mock()
    mock_manager.get_available_drones = AsyncMock(return_value=[])
    mock_manager.connect_drone = AsyncMock(return_value=SuccessResponse(message="Connected"))
    mock_manager.start_camera_stream = AsyncMock(return_value=SuccessResponse(message="Stream started"))
    mock_manager.capture_photo = AsyncMock(return_value=Photo(
        id="test_photo",
        filename="test.jpg",
        path="/photos/test.jpg",
        timestamp=datetime.now(),
        drone_id="drone_001"
    ))
    mock_manager.stop_camera_stream = AsyncMock(return_value=SuccessResponse(message="Stream stopped"))
    mock_manager.disconnect_drone = AsyncMock(return_value=SuccessResponse(message="Disconnected"))
    
    with patch('backend.api_server.main.get_drone_manager', return_value=mock_manager):
        # 1. ドローン接続
        response = client.post("/api/drones/drone_001/connect")
        assert response.status_code == 200
        
        # 2. カメラストリーミング開始
        response = client.post("/api/drones/drone_001/camera/stream/start")
        assert response.status_code == 200
        
        # 3. 写真撮影
        response = client.post("/api/drones/drone_001/camera/photo")
        assert response.status_code == 200
        photo_data = response.json()
        assert photo_data["id"] == "test_photo"
        
        # 4. カメラストリーミング停止
        response = client.post("/api/drones/drone_001/camera/stream/stop")
        assert response.status_code == 200
        
        # 5. ドローン切断
        response = client.post("/api/drones/drone_001/disconnect")
        assert response.status_code == 200
        
        # 全ての操作が順序通りに呼び出されたことを確認
        mock_manager.connect_drone.assert_called_with("drone_001")
        mock_manager.start_camera_stream.assert_called_with("drone_001")
        mock_manager.capture_photo.assert_called_with("drone_001")
        mock_manager.stop_camera_stream.assert_called_with("drone_001")
        mock_manager.disconnect_drone.assert_called_with("drone_001")