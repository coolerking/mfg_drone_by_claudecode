"""
ミッションパッド関連APIのテストケース（Tello EDU専用）
/mission_pad/enable, /mission_pad/disable, /mission_pad/detection_direction,
/mission_pad/go_xyz, /mission_pad/status エンドポイントのテスト
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


class TestMissionPadAPI:
    """ミッションパッド関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_enable_success(self, mock_drone):
        """正常なミッションパッド検出有効化テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/mission_pad/enable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "有効" in data["message"] or "enable" in data["message"].lower()
    
    def test_mission_pad_enable_not_connected(self):
        """未接続でのミッションパッド検出有効化テスト"""
        response = self.client.post("/mission_pad/enable")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_disable_success(self, mock_drone):
        """正常なミッションパッド検出無効化テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/mission_pad/disable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "無効" in data["message"] or "disable" in data["message"].lower()
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_detection_direction_success(self, mock_drone):
        """正常なミッションパッド検出方向設定テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        valid_directions = [0, 1, 2]  # 下向き、前向き、両方
        
        for direction in valid_directions:
            response = self.client.put("/mission_pad/detection_direction", json={
                "direction": direction
            })
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "設定" in data["message"] or "direction" in data["message"].lower()
    
    def test_mission_pad_detection_direction_invalid(self):
        """無効なミッションパッド検出方向テスト"""
        invalid_directions = [-1, 3, 4, 10]
        
        for direction in invalid_directions:
            response = self.client.put("/mission_pad/detection_direction", json={
                "direction": direction
            })
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_mission_pad_detection_direction_missing_parameter(self):
        """ミッションパッド検出方向必須パラメータ未指定テスト"""
        response = self.client.put("/mission_pad/detection_direction", json={})
        
        assert response.status_code == 422
    
    def test_mission_pad_detection_direction_type_validation(self):
        """ミッションパッド検出方向データ型検証テスト"""
        invalid_types = ["0", True, 1.5, [0]]
        
        for invalid_type in invalid_types:
            response = self.client.put("/mission_pad/detection_direction", json={
                "direction": invalid_type
            })
            assert response.status_code in [400, 422]
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_go_xyz_success(self, mock_drone):
        """正常なミッションパッド基準移動テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/mission_pad/go_xyz", json={
            "x": 100,
            "y": -50,
            "z": 200,
            "speed": 50,
            "mission_pad_id": 1
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "移動" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_go_xyz_boundary_values(self, mock_drone):
        """ミッションパッド基準移動境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary_tests = [
            # 座標境界値
            {"x": -500, "y": -500, "z": -500, "speed": 10, "mission_pad_id": 1},
            {"x": 500, "y": 500, "z": 500, "speed": 100, "mission_pad_id": 8},
            # 速度境界値
            {"x": 0, "y": 0, "z": 0, "speed": 10, "mission_pad_id": 1},
            {"x": 0, "y": 0, "z": 0, "speed": 100, "mission_pad_id": 1},
            # ミッションパッドID境界値
            {"x": 0, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 1},
            {"x": 0, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 8}
        ]
        
        for test_data in boundary_tests:
            response = self.client.post("/mission_pad/go_xyz", json=test_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_mission_pad_go_xyz_invalid_coordinates(self):
        """無効なミッションパッド基準移動座標テスト"""
        invalid_tests = [
            # 座標範囲外
            {"x": -501, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 1},
            {"x": 501, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 1},
            {"x": 0, "y": -501, "z": 0, "speed": 50, "mission_pad_id": 1},
            {"x": 0, "y": 501, "z": 0, "speed": 50, "mission_pad_id": 1},
            {"x": 0, "y": 0, "z": -501, "speed": 50, "mission_pad_id": 1},
            {"x": 0, "y": 0, "z": 501, "speed": 50, "mission_pad_id": 1},
            # 速度範囲外
            {"x": 0, "y": 0, "z": 0, "speed": 9, "mission_pad_id": 1},
            {"x": 0, "y": 0, "z": 0, "speed": 101, "mission_pad_id": 1},
            # ミッションパッドID範囲外
            {"x": 0, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 0},
            {"x": 0, "y": 0, "z": 0, "speed": 50, "mission_pad_id": 9}
        ]
        
        for test_data in invalid_tests:
            response = self.client.post("/mission_pad/go_xyz", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_mission_pad_go_xyz_missing_parameters(self):
        """ミッションパッド基準移動必須パラメータ未指定テスト"""
        missing_tests = [
            {"y": 0, "z": 0, "speed": 50, "mission_pad_id": 1},  # x missing
            {"x": 0, "z": 0, "speed": 50, "mission_pad_id": 1},  # y missing
            {"x": 0, "y": 0, "speed": 50, "mission_pad_id": 1},  # z missing
            {"x": 0, "y": 0, "z": 0, "mission_pad_id": 1},       # speed missing
            {"x": 0, "y": 0, "z": 0, "speed": 50}                # mission_pad_id missing
        ]
        
        for test_data in missing_tests:
            response = self.client.post("/mission_pad/go_xyz", json=test_data)
            assert response.status_code == 422
    
    def test_mission_pad_go_xyz_not_flying(self):
        """非飛行中でのミッションパッド基準移動テスト"""
        response = self.client.post("/mission_pad/go_xyz", json={
            "x": 100,
            "y": 0,
            "z": 100,
            "speed": 50,
            "mission_pad_id": 1
        })
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_status_success(self, mock_drone):
        """正常なミッションパッド状態取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/mission_pad/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # ミッションパッド状態スキーマの検証
        assert isinstance(data, dict)
        assert "mission_pad_id" in data
        assert "distance_x" in data
        assert "distance_y" in data
        assert "distance_z" in data
        
        # データ型の検証
        assert isinstance(data["mission_pad_id"], int)
        assert isinstance(data["distance_x"], int)
        assert isinstance(data["distance_y"], int)
        assert isinstance(data["distance_z"], int)
        
        # ミッションパッドIDの値域確認
        assert data["mission_pad_id"] == -1 or (1 <= data["mission_pad_id"] <= 8)
    
    def test_mission_pad_status_not_connected(self):
        """未接続でのミッションパッド状態取得テスト"""
        response = self.client.get("/mission_pad/status")
        
        # 実装依存：503または200（キャッシュ値）
        assert response.status_code in [200, 503]
        if response.status_code == 503:
            data = response.json()
            assert "error" in data
            assert "code" in data
    
    def test_mission_pad_method_validation(self):
        """ミッションパッドエンドポイントHTTPメソッド検証"""
        # POST専用エンドポイント
        post_endpoints = [
            "/mission_pad/enable",
            "/mission_pad/disable",
            "/mission_pad/go_xyz"
        ]
        
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
        
        # PUT専用エンドポイント
        response = self.client.get("/mission_pad/detection_direction")
        assert response.status_code == 405
        
        response = self.client.post("/mission_pad/detection_direction")
        assert response.status_code == 405
        
        # GET専用エンドポイント
        response = self.client.post("/mission_pad/status")
        assert response.status_code == 405
        
        response = self.client.put("/mission_pad/status")
        assert response.status_code == 405
    
    def test_mission_pad_type_validation(self):
        """ミッションパッドデータ型検証テスト"""
        # 座標の型検証
        response = self.client.post("/mission_pad/go_xyz", json={
            "x": "100",  # 文字列（整数が期待される）
            "y": 0,
            "z": 0,
            "speed": 50,
            "mission_pad_id": 1
        })
        assert response.status_code == 422
        
        # 速度の型検証
        response = self.client.post("/mission_pad/go_xyz", json={
            "x": 0,
            "y": 0,
            "z": 0,
            "speed": "50",  # 文字列（整数が期待される）
            "mission_pad_id": 1
        })
        assert response.status_code == 422
        
        # ミッションパッドIDの型検証
        response = self.client.post("/mission_pad/go_xyz", json={
            "x": 0,
            "y": 0,
            "z": 0,
            "speed": 50,
            "mission_pad_id": "1"  # 文字列（整数が期待される）
        })
        assert response.status_code == 422
    
    @patch('services.drone_service.drone_service.drone')
    def test_mission_pad_sequence(self, mock_drone):
        """ミッションパッド操作シーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. ミッションパッド検出有効化
        response = self.client.post("/mission_pad/enable")
        if response.status_code == 200:
            assert response.json()["success"] is True
            
            # 2. 検出方向設定
            response = self.client.put("/mission_pad/detection_direction", json={
                "direction": 2  # 両方向
            })
            if response.status_code == 200:
                assert response.json()["success"] is True
                
                # 3. ミッションパッド状態確認
                response = self.client.get("/mission_pad/status")
                assert response.status_code == 200
                
                # 4. ミッションパッド検出無効化
                response = self.client.post("/mission_pad/disable")
                if response.status_code == 200:
                    assert response.json()["success"] is True
    
    def test_mission_pad_response_format_validation(self):
        """ミッションパッドレスポンス形式検証"""
        endpoints = [
            "/mission_pad/enable",
            "/mission_pad/disable"
        ]
        
        for endpoint in endpoints:
            response = self.client.post(endpoint)
            
            assert response.status_code in [200, 503]
            
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