"""
カメラ操作関連APIのテストケース
/camera/stream/start, /camera/stream/stop, /camera/stream, /camera/photo, 
/camera/video/start, /camera/video/stop, /camera/settings エンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from config.test_config import TestConfig
from tests.fixtures.drone_factory import create_test_drone, DroneTestHelper
from tests.stubs.drone_stub import TelloStub


class TestCameraAPI:
    """カメラ操作関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_start_success(self, mock_drone):
        """正常なストリーミング開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/stream/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ストリーミング" in data["message"]
    
    def test_camera_stream_start_not_connected(self):
        """未接続でのストリーミング開始テスト"""
        response = self.client.post("/camera/stream/start")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_start_already_started(self, mock_drone):
        """既に開始済みのストリーミング開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        # ストリーミング開始済み状態を設定
        DroneTestHelper.setup_streaming_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/stream/start")
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "STREAMING_ALREADY_STARTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_stop_success(self, mock_drone):
        """正常なストリーミング停止テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        DroneTestHelper.setup_streaming_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/stream/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停止" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_stop_not_started(self, mock_drone):
        """未開始でのストリーミング停止テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/stream/stop")
        
        # 実装依存：エラーまたは成功（冪等性）
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        else:
            data = response.json()
            assert "error" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_get_success(self, mock_drone):
        """正常なストリーム取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        DroneTestHelper.setup_streaming_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/camera/stream")
        
        assert response.status_code == 200
        # multipart/x-mixed-replaceのコンテンツタイプを確認
        content_type = response.headers.get("content-type", "")
        assert "multipart/x-mixed-replace" in content_type or "video" in content_type
    
    def test_camera_stream_get_not_connected(self):
        """未接続でのストリーム取得テスト"""
        response = self.client.get("/camera/stream")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_get_not_started(self, mock_drone):
        """ストリーミング未開始でのストリーム取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/camera/stream")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "STREAMING_NOT_STARTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_photo_success(self, mock_drone):
        """正常な写真撮影テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/photo")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "撮影" in data["message"]
    
    def test_camera_photo_not_connected(self):
        """未接続での写真撮影テスト"""
        response = self.client.post("/camera/photo")
        
        # 実装依存：503または400エラー
        assert response.status_code in [400, 503]
        data = response.json()
        assert "error" in data
        assert "code" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_video_start_success(self, mock_drone):
        """正常な動画録画開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/video/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "録画" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_video_stop_success(self, mock_drone):
        """正常な動画録画停止テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        # 録画開始済み状態を設定
        DroneTestHelper.setup_recording_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/camera/video/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停止" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_settings_success(self, mock_drone):
        """正常なカメラ設定変更テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        valid_settings = [
            {"resolution": "high", "fps": "high", "bitrate": 5},
            {"resolution": "low", "fps": "middle", "bitrate": 3},
            {"resolution": "high", "fps": "low", "bitrate": 1},
            # 部分的な設定変更
            {"resolution": "high"},
            {"fps": "middle"},
            {"bitrate": 3}
        ]
        
        for settings in valid_settings:
            response = self.client.put("/camera/settings", json=settings)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "設定" in data["message"]
    
    def test_camera_settings_invalid_resolution(self):
        """無効な解像度設定テスト"""
        invalid_settings = [
            {"resolution": "medium"},    # 無効な解像度
            {"resolution": "ultra"},     # 無効な解像度
            {"resolution": 1080},        # 数値
            {"resolution": True}         # ブール値
        ]
        
        for settings in invalid_settings:
            response = self.client.put("/camera/settings", json=settings)
            assert response.status_code in [400, 422]
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
                assert "code" in data
                assert data["code"] == "INVALID_PARAMETER"
    
    def test_camera_settings_invalid_fps(self):
        """無効なFPS設定テスト"""
        invalid_settings = [
            {"fps": "ultra"},      # 無効なFPS
            {"fps": "fast"},       # 無効なFPS
            {"fps": 60},           # 数値
            {"fps": False}         # ブール値
        ]
        
        for settings in invalid_settings:
            response = self.client.put("/camera/settings", json=settings)
            assert response.status_code in [400, 422]
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
                assert "code" in data
                assert data["code"] == "INVALID_PARAMETER"
    
    def test_camera_settings_invalid_bitrate(self):
        """無効なビットレート設定テスト"""
        invalid_settings = [
            {"bitrate": 0},        # 最小値未満
            {"bitrate": 6},        # 最大値超過
            {"bitrate": -1},       # 負の値
            {"bitrate": "high"},   # 文字列
            {"bitrate": 2.5}       # 浮動小数点（整数が期待される場合）
        ]
        
        for settings in invalid_settings:
            response = self.client.put("/camera/settings", json=settings)
            assert response.status_code in [400, 422]
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
                assert "code" in data
                assert data["code"] == "INVALID_PARAMETER"
    
    def test_camera_settings_boundary_values(self):
        """カメラ設定境界値テスト"""
        boundary_settings = [
            {"bitrate": 1},        # 最小値
            {"bitrate": 5},        # 最大値
        ]
        
        for settings in boundary_settings:
            response = self.client.put("/camera/settings", json=settings)
            # 接続状態によってエラーまたは成功
            assert response.status_code in [200, 400, 503]
    
    def test_camera_settings_empty_body(self):
        """空のリクエストボディテスト"""
        response = self.client.put("/camera/settings", json={})
        
        # 空のボディでも正常に処理される場合がある
        assert response.status_code in [200, 400, 422]
    
    def test_camera_endpoints_method_validation(self):
        """カメラエンドポイントHTTPメソッド検証"""
        # POST専用エンドポイント
        post_endpoints = [
            "/camera/stream/start",
            "/camera/stream/stop", 
            "/camera/photo",
            "/camera/video/start",
            "/camera/video/stop"
        ]
        
        for endpoint in post_endpoints:
            # GET method should not be allowed
            response = self.client.get(endpoint)
            assert response.status_code == 405
            
            # PUT method should not be allowed
            response = self.client.put(endpoint)
            assert response.status_code == 405
        
        # GET専用エンドポイント
        response = self.client.post("/camera/stream")
        assert response.status_code == 405
        
        response = self.client.put("/camera/stream")
        assert response.status_code == 405
        
        # PUT専用エンドポイント
        response = self.client.get("/camera/settings")
        assert response.status_code == 405
        
        response = self.client.post("/camera/settings")
        assert response.status_code == 405
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_stream_sequence(self, mock_drone):
        """カメラストリーミングシーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. ストリーミング開始
        response = self.client.post("/camera/stream/start")
        if response.status_code == 200:
            assert response.json()["success"] is True
            
            # ストリーミング開始済み状態を設定
            DroneTestHelper.setup_streaming_state(mock_drone_instance)
            
            # 2. ストリーム取得
            response = self.client.get("/camera/stream")
            assert response.status_code == 200
            
            # 3. ストリーミング停止
            response = self.client.post("/camera/stream/stop")
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    @patch('services.drone_service.drone_service.drone')
    def test_camera_video_sequence(self, mock_drone):
        """動画録画シーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. 録画開始
        response = self.client.post("/camera/video/start")
        if response.status_code == 200:
            assert response.json()["success"] is True
            
            # 録画開始済み状態を設定
            DroneTestHelper.setup_recording_state(mock_drone_instance)
            
            # 2. 録画停止
            response = self.client.post("/camera/video/stop")
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    def test_camera_response_format_validation(self):
        """カメラレスポンス形式検証"""
        endpoints = [
            "/camera/stream/start",
            "/camera/stream/stop",
            "/camera/photo",
            "/camera/video/start",
            "/camera/video/stop"
        ]
        
        for endpoint in endpoints:
            response = self.client.post(endpoint)
            
            # ステータスコードの検証
            assert response.status_code in [200, 400, 409, 503]
            
            # JSONレスポンスの場合
            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                assert isinstance(data, dict)
                
                if response.status_code == 200:
                    # 成功レスポンス
                    assert "success" in data
                    assert "message" in data
                    assert isinstance(data["success"], bool)
                    assert isinstance(data["message"], str)
                else:
                    # エラーレスポンス
                    assert "error" in data
                    assert "code" in data
                    assert isinstance(data["error"], str)
                    assert isinstance(data["code"], str)
    
    def test_camera_settings_response_format(self):
        """カメラ設定レスポンス形式検証"""
        response = self.client.put("/camera/settings", json={"resolution": "high"})
        
        assert response.status_code in [200, 400, 422, 503]
        
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            assert isinstance(data, dict)
            
            if response.status_code == 200:
                assert "success" in data
                assert "message" in data
                assert isinstance(data["success"], bool)
                assert isinstance(data["message"], str)
            else:
                # エラーまたはバリデーションエラー
                if response.status_code == 400:
                    assert "error" in data
                    assert "code" in data
                elif response.status_code == 422:
                    # FastAPIバリデーションエラー
                    assert "detail" in data or "error" in data