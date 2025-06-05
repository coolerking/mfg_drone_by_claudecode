"""
センサー情報取得関連APIのテストケース（完全版）
/drone/status, /drone/battery, /drone/height, /drone/temperature, /drone/flight_time,
/drone/barometer, /drone/distance_tof, /drone/acceleration, /drone/velocity, /drone/attitude エンドポイントのテスト
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


class TestSensorsAPIComplete:
    """センサー情報取得関連APIの完全テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_drone_status_success(self, mock_drone):
        """正常なドローン状態取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # DroneStatusスキーマの検証
        assert isinstance(data, dict)
        assert "connected" in data
        assert isinstance(data["connected"], bool)
        
        if data["connected"]:
            # 接続済みの場合は他のフィールドも確認
            expected_fields = ["battery", "height", "temperature", "flight_time", 
                             "speed", "barometer", "distance_tof", "acceleration", 
                             "velocity", "attitude"]
            for field in expected_fields:
                if field in data:
                    assert data[field] is not None
    
    def test_drone_status_not_connected(self):
        """未接続でのドローン状態取得テスト"""
        response = self.client.get("/drone/status")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_battery_success(self, mock_drone):
        """正常なバッテリー残量取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/battery")
        
        assert response.status_code == 200
        data = response.json()
        assert "battery" in data
        assert isinstance(data["battery"], int)
        assert 0 <= data["battery"] <= 100
    
    @patch('services.drone_service.drone_service.drone')
    def test_battery_boundary_values(self, mock_drone):
        """バッテリー境界値検証テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        
        # テストデータで境界値を設定
        test_batteries = [0, 1, 50, 99, 100]
        
        for battery in test_batteries:
            if hasattr(mock_drone_instance, '_battery'):
                mock_drone_instance._battery = battery
            
            mock_drone.return_value = mock_drone_instance
            
            response = self.client.get("/drone/battery")
            assert response.status_code == 200
            data = response.json()
            assert 0 <= data["battery"] <= 100
    
    @patch('services.drone_service.drone_service.drone')
    def test_height_success(self, mock_drone):
        """正常な飛行高度取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/height")
        
        assert response.status_code == 200
        data = response.json()
        assert "height" in data
        assert isinstance(data["height"], int)
        assert 0 <= data["height"] <= 3000
    
    @patch('services.drone_service.drone_service.drone')
    def test_altitude_boundary_values(self, mock_drone):
        """高度境界値検証テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        
        # テストデータで境界値を設定
        test_heights = [0, 1, 1500, 2999, 3000]
        
        for height in test_heights:
            if hasattr(mock_drone_instance, '_height'):
                mock_drone_instance._height = height
            
            mock_drone.return_value = mock_drone_instance
            
            response = self.client.get("/drone/height")
            assert response.status_code == 200
            data = response.json()
            assert 0 <= data["height"] <= 3000
    
    @patch('services.drone_service.drone_service.drone')
    def test_temperature_success(self, mock_drone):
        """正常なドローン温度取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/temperature")
        
        assert response.status_code == 200
        data = response.json()
        assert "temperature" in data
        assert isinstance(data["temperature"], int)
        assert 0 <= data["temperature"] <= 90
    
    @patch('services.drone_service.drone_service.drone')
    def test_attitude_success(self, mock_drone):
        """正常な姿勢角取得テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/attitude")
        
        assert response.status_code == 200
        data = response.json()
        assert "attitude" in data
        assert isinstance(data["attitude"], dict)
        
        # 姿勢角データ検証
        attitude = data["attitude"]
        for angle in ["pitch", "roll", "yaw"]:
            assert angle in attitude
            assert isinstance(attitude[angle], int)
            assert -180 <= attitude[angle] <= 180
    
    @patch('services.drone_service.drone_service.drone')
    def test_attitude_boundary_values(self, mock_drone):
        """姿勢角境界値検証テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        
        # テストデータで境界値を設定
        test_angles = [-180, -179, -90, -1, 0, 1, 90, 179, 180]
        
        for angle in test_angles:
            if hasattr(mock_drone_instance, '_attitude'):
                mock_drone_instance._attitude = {"pitch": angle, "roll": angle, "yaw": angle}
            
            mock_drone.return_value = mock_drone_instance
            
            response = self.client.get("/drone/attitude")
            assert response.status_code == 200
            data = response.json()
            attitude = data["attitude"]
            for axis in ["pitch", "roll", "yaw"]:
                assert -180 <= attitude[axis] <= 180
    
    def test_sensors_method_validation(self):
        """センサーエンドポイントHTTPメソッド検証"""
        sensor_endpoints = [
            "/drone/status", "/drone/battery", "/drone/height", "/drone/temperature",
            "/drone/flight_time", "/drone/barometer", "/drone/distance_tof",
            "/drone/acceleration", "/drone/velocity", "/drone/attitude"
        ]
        
        for endpoint in sensor_endpoints:
            # POST method should not be allowed
            response = self.client.post(endpoint)
            assert response.status_code == 405
            
            # PUT method should not be allowed
            response = self.client.put(endpoint)
            assert response.status_code == 405
            
            # DELETE method should not be allowed
            response = self.client.delete(endpoint)
            assert response.status_code == 405
    
    def test_sensors_not_connected_scenarios(self):
        """各センサーの未接続シナリオテスト"""
        sensor_endpoints = [
            "/drone/flight_time", "/drone/barometer", "/drone/distance_tof",
            "/drone/acceleration", "/drone/velocity", "/drone/attitude"
        ]
        
        for endpoint in sensor_endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 503
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "DRONE_NOT_CONNECTED"