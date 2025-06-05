"""
飛行制御関連APIのテストケース
/drone/takeoff, /drone/land, /drone/emergency, /drone/stop エンドポイントのテスト
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


class TestFlightControlAPI:
    """飛行制御関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_takeoff_success(self, mock_drone):
        """正常な離陸テスト"""
        # 接続済みドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/takeoff")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "離陸" in data["message"]
    
    def test_takeoff_not_connected(self):
        """未接続での離陸テスト"""
        response = self.client.post("/drone/takeoff")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_takeoff_already_flying(self, mock_drone):
        """既に飛行中での離陸テスト"""
        # 飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/takeoff")
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "ALREADY_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_land_success(self, mock_drone):
        """正常な着陸テスト"""
        # 飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/land")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "着陸" in data["message"]
    
    def test_land_not_connected(self):
        """未接続での着陸テスト"""
        response = self.client.post("/drone/land")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_land_not_flying(self, mock_drone):
        """非飛行中での着陸テスト"""
        # 接続済みだが非飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/land")
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_emergency_success(self, mock_drone):
        """正常な緊急停止テスト"""
        # 飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/emergency")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "緊急停止" in data["message"]
    
    def test_emergency_not_connected(self):
        """未接続での緊急停止テスト"""
        response = self.client.post("/drone/emergency")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_stop_success(self, mock_drone):
        """正常な停止（ホバリング）テスト"""
        # 飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ホバリング" in data["message"]
    
    def test_stop_not_connected(self):
        """未接続での停止テスト"""
        response = self.client.post("/drone/stop")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_stop_not_flying(self, mock_drone):
        """非飛行中での停止テスト"""
        # 接続済みだが非飛行中ドローンのモック
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/stop")
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_takeoff_command_error(self, mock_drone):
        """離陸コマンドエラーテスト"""
        # コマンドエラーをシミュレート
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        DroneTestHelper.setup_command_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/takeoff")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "COMMAND_FAILED"
    
    def test_flight_control_response_format(self):
        """飛行制御レスポンス形式の検証"""
        # 各エンドポイントのレスポンス形式をテスト
        endpoints = ["/drone/takeoff", "/drone/land", "/drone/emergency", "/drone/stop"]
        
        for endpoint in endpoints:
            response = self.client.post(endpoint)
            
            # エラーレスポンスでも適切な形式であることを確認
            assert response.status_code in [200, 400, 409, 500]
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
    
    @patch('services.drone_service.drone_service.drone')
    def test_flight_sequence_api(self, mock_drone):
        """APIレベルでの飛行シーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. 離陸
        response = self.client.post("/drone/takeoff")
        assert response.status_code == 200
        
        # ドローン状態を飛行中に更新
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        
        # 2. ホバリング
        response = self.client.post("/drone/stop")
        assert response.status_code == 200
        
        # 3. 着陸
        response = self.client.post("/drone/land")
        assert response.status_code == 200