"""
物体認識・追跡関連APIのテストケース
/tracking/start, /tracking/stop, /tracking/status エンドポイントのテスト
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


class TestTrackingAPI:
    """物体認識・追跡関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_start_success(self, mock_drone):
        """正常な物体追跡開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        tracking_data = {
            "target_object": "person",
            "tracking_mode": "center"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "追跡" in data["message"] or "tracking" in data["message"].lower()
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_start_with_follow_mode(self, mock_drone):
        """フォローモードでの物体追跡開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        tracking_data = {
            "target_object": "car",
            "tracking_mode": "follow"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "追跡" in data["message"] or "tracking" in data["message"].lower()
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_start_default_mode(self, mock_drone):
        """デフォルトモードでの物体追跡開始テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # tracking_modeを指定しない（デフォルトはcenter）
        tracking_data = {
            "target_object": "bicycle"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_tracking_start_missing_target_object(self):
        """追跡対象オブジェクト未指定テスト"""
        tracking_data = {
            "tracking_mode": "center"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        assert response.status_code == 422
    
    def test_tracking_start_invalid_tracking_mode(self):
        """無効な追跡モードテスト"""
        invalid_modes = ["track", "chase", "hunt", "invalid", 123, True]
        
        for mode in invalid_modes:
            tracking_data = {
                "target_object": "person",
                "tracking_mode": mode
            }
            
            response = self.client.post("/tracking/start", json=tracking_data)
            assert response.status_code in [400, 422]
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
                assert "code" in data
                assert data["code"] == "INVALID_PARAMETER"
    
    def test_tracking_start_empty_target_object(self):
        """空の追跡対象オブジェクトテスト"""
        tracking_data = {
            "target_object": "",
            "tracking_mode": "center"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    def test_tracking_start_type_validation(self):
        """追跡開始データ型検証テスト"""
        invalid_types = [
            {"target_object": 123, "tracking_mode": "center"},      # 数値
            {"target_object": True, "tracking_mode": "center"},     # ブール値
            {"target_object": ["person"], "tracking_mode": "center"}, # 配列
            {"target_object": "person", "tracking_mode": 123}       # 数値モード
        ]
        
        for test_data in invalid_types:
            response = self.client.post("/tracking/start", json=test_data)
            assert response.status_code == 422
    
    def test_tracking_start_not_connected(self):
        """未接続での追跡開始テスト"""
        tracking_data = {
            "target_object": "person",
            "tracking_mode": "center"
        }
        
        response = self.client.post("/tracking/start", json=tracking_data)
        
        # 実装依存：503または400
        assert response.status_code in [400, 503]
        data = response.json()
        assert "error" in data
        assert "code" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_stop_success(self, mock_drone):
        """正常な物体追跡停止テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        # 追跡中状態を設定
        if hasattr(mock_drone_instance, '_tracking'):
            mock_drone_instance._tracking = True
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/tracking/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "停止" in data["message"] or "stop" in data["message"].lower()
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_stop_not_tracking(self, mock_drone):
        """非追跡中での追跡停止テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/tracking/stop")
        
        # 実装依存：成功（冪等性）またはエラー
        assert response.status_code in [200, 400, 409]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        else:
            data = response.json()
            assert "error" in data
    
    def test_tracking_stop_not_connected(self):
        """未接続での追跡停止テスト"""
        response = self.client.post("/tracking/stop")
        
        # 実装依存：503または400
        assert response.status_code in [400, 503]
        data = response.json()
        assert "error" in data
        assert "code" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_status_success(self, mock_drone):
        """正常な追跡状態取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/tracking/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # 追跡状態スキーマの検証
        assert isinstance(data, dict)
        assert "is_tracking" in data
        assert "target_object" in data
        assert "target_detected" in data
        assert "target_position" in data
        
        # データ型の検証
        assert isinstance(data["is_tracking"], bool)
        assert isinstance(data["target_object"], (str, type(None)))
        assert isinstance(data["target_detected"], bool)
        
        # target_positionの検証
        if data["target_position"] is not None:
            assert isinstance(data["target_position"], dict)
            position = data["target_position"]
            required_fields = ["x", "y", "width", "height"]
            for field in required_fields:
                assert field in position
                assert isinstance(position[field], int)
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_status_while_tracking(self, mock_drone):
        """追跡中の状態取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        
        # 追跡中状態を設定
        if hasattr(mock_drone_instance, '_tracking_status'):
            mock_drone_instance._tracking_status = {
                "is_tracking": True,
                "target_object": "person",
                "target_detected": True,
                "target_position": {
                    "x": 320,
                    "y": 240,
                    "width": 100,
                    "height": 150
                }
            }
        
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/tracking/status")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["is_tracking"]:
            assert data["target_object"] is not None
            assert isinstance(data["target_object"], str)
            assert len(data["target_object"]) > 0
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_status_not_tracking(self, mock_drone):
        """非追跡中の状態取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        
        # 非追跡状態を設定
        if hasattr(mock_drone_instance, '_tracking_status'):
            mock_drone_instance._tracking_status = {
                "is_tracking": False,
                "target_object": None,
                "target_detected": False,
                "target_position": None
            }
        
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/tracking/status")
        
        assert response.status_code == 200
        data = response.json()
        
        if not data["is_tracking"]:
            # 非追跡中はtarget_objectがNullまたは空文字列
            assert data["target_object"] is None or data["target_object"] == ""
            assert data["target_detected"] is False
    
    def test_tracking_status_not_connected(self):
        """未接続での追跡状態取得テスト"""
        response = self.client.get("/tracking/status")
        
        # 実装依存：503または200（キャッシュ値）
        assert response.status_code in [200, 503]
        if response.status_code == 503:
            data = response.json()
            assert "error" in data
            assert "code" in data
    
    def test_tracking_method_validation(self):
        """追跡エンドポイントHTTPメソッド検証"""
        # POST専用エンドポイント
        post_endpoints = ["/tracking/start", "/tracking/stop"]
        
        for endpoint in post_endpoints:
            # GET method should not be allowed
            response = self.client.get(endpoint)
            assert response.status_code == 405
            
            # PUT method should not be allowed
            response = self.client.put(endpoint)
            assert response.status_code == 405
            
            # DELETE method should not be allowed
            response = self.client.delete(endpoint)
            assert response.status_code == 405
        
        # GET専用エンドポイント
        response = self.client.post("/tracking/status")
        assert response.status_code == 405
        
        response = self.client.put("/tracking/status")
        assert response.status_code == 405
    
    @patch('services.drone_service.drone_service.drone')
    def test_tracking_sequence(self, mock_drone):
        """追跡操作シーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. 追跡開始
        response = self.client.post("/tracking/start", json={
            "target_object": "person",
            "tracking_mode": "center"
        })
        
        if response.status_code == 200:
            assert response.json()["success"] is True
            
            # 追跡中状態を設定
            if hasattr(mock_drone_instance, '_tracking'):
                mock_drone_instance._tracking = True
            
            # 2. 追跡状態確認
            response = self.client.get("/tracking/status")
            assert response.status_code == 200
            
            # 3. 追跡停止
            response = self.client.post("/tracking/stop")
            if response.status_code == 200:
                assert response.json()["success"] is True
                
                # 4. 停止後の状態確認
                response = self.client.get("/tracking/status")
                assert response.status_code == 200
                data = response.json()
                if "is_tracking" in data:
                    # 停止後は追跡していない状態
                    assert data["is_tracking"] is False
    
    def test_tracking_response_format_validation(self):
        """追跡レスポンス形式検証"""
        endpoints = ["/tracking/start", "/tracking/stop"]
        
        for endpoint in endpoints:
            if endpoint == "/tracking/start":
                response = self.client.post(endpoint, json={
                    "target_object": "person",
                    "tracking_mode": "center"
                })
            else:
                response = self.client.post(endpoint)
            
            assert response.status_code in [200, 400, 409, 422, 503]
            
            if "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                assert isinstance(data, dict)
                
                if response.status_code == 200:
                    # 成功レスポンス
                    assert "success" in data
                    assert "message" in data
                    assert isinstance(data["success"], bool)
                    assert isinstance(data["message"], str)
                elif response.status_code in [400, 409, 503]:
                    # エラーレスポンス
                    assert "error" in data
                    assert "code" in data
                    assert isinstance(data["error"], str)
                    assert isinstance(data["code"], str)
    
    def test_tracking_concurrent_operations(self):
        """追跡同時操作テスト"""
        import threading
        
        results = []
        
        def start_tracking():
            response = self.client.post("/tracking/start", json={
                "target_object": "person",
                "tracking_mode": "center"
            })
            results.append({
                'operation': 'start',
                'status_code': response.status_code
            })
        
        def stop_tracking():
            response = self.client.post("/tracking/stop")
            results.append({
                'operation': 'stop',
                'status_code': response.status_code
            })
        
        def get_status():
            response = self.client.get("/tracking/status")
            results.append({
                'operation': 'status',
                'status_code': response.status_code
            })
        
        # 複数の同時操作を実行
        threads = [
            threading.Thread(target=start_tracking),
            threading.Thread(target=get_status),
            threading.Thread(target=stop_tracking)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # すべての操作が適切に処理されることを確認
        assert len(results) == 3
        for result in results:
            # 同時操作でも適切なステータスコードが返される
            assert result['status_code'] in [200, 400, 409, 503]
    
    def test_tracking_target_object_variations(self):
        """追跡対象オブジェクト種類テスト"""
        valid_objects = [
            "person", "car", "bicycle", "dog", "cat", "ball",
            "Person", "CAR", "Bicycle",  # 大文字小文字
            "person_1", "car-blue", "bicycle.red",  # 特殊文字
            "a", "x" * 100  # 長さの境界
        ]
        
        for obj in valid_objects:
            response = self.client.post("/tracking/start", json={
                "target_object": obj,
                "tracking_mode": "center"
            })
            
            # 接続状態やモデルの可用性により結果が変わる
            assert response.status_code in [200, 400, 503]
            
            if response.status_code == 400:
                data = response.json()
                if "error" in data:
                    # 無効なオブジェクト名の場合はINVALID_PARAMETERまたはMODEL_NOT_FOUND
                    assert data["code"] in ["INVALID_PARAMETER", "MODEL_NOT_FOUND"]