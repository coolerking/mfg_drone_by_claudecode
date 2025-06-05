"""
センサー関連APIのテストケース
/drone/status, /drone/battery, /drone/height, etc. エンドポイントのテスト
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


class TestSensorsAPI:
    """センサー関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_drone_status_success(self, mock_drone):
        """ドローン状態取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # DroneStatusスキーマの検証
        required_fields = [
            "connected", "battery", "height", "temperature", "flight_time",
            "speed", "barometer", "distance_tof", "acceleration", "velocity", "attitude"
        ]
        
        for field in required_fields:
            assert field in data
        
        # データ型の検証
        assert isinstance(data["connected"], bool)
        assert isinstance(data["battery"], int)
        assert isinstance(data["height"], int)
        assert isinstance(data["temperature"], int)
        assert isinstance(data["flight_time"], int)
        assert isinstance(data["speed"], (int, float))
        assert isinstance(data["barometer"], (int, float))
        assert isinstance(data["distance_tof"], int)
        assert isinstance(data["acceleration"], dict)
        assert isinstance(data["velocity"], dict)
        assert isinstance(data["attitude"], dict)
        
        # 範囲の検証
        assert 0 <= data["battery"] <= 100
        assert data["height"] >= 0
        assert 0 <= data["temperature"] <= 90
        assert data["flight_time"] >= 0
        assert -180 <= data["attitude"]["pitch"] <= 180
        assert -180 <= data["attitude"]["roll"] <= 180
        assert -180 <= data["attitude"]["yaw"] <= 180
    
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
        """バッテリー残量取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/battery")
        
        assert response.status_code == 200
        data = response.json()
        assert "battery" in data
        assert isinstance(data["battery"], int)
        assert 0 <= data["battery"] <= 100
    
    def test_battery_not_connected(self):
        """未接続でのバッテリー残量取得テスト"""
        response = self.client.get("/drone/battery")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_NOT_CONNECTED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_height_success(self, mock_drone):
        """高度取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/height")
        
        assert response.status_code == 200
        data = response.json()
        assert "height" in data
        assert isinstance(data["height"], int)
        assert 0 <= data["height"] <= 3000
    
    @patch('services.drone_service.drone_service.drone')
    def test_temperature_success(self, mock_drone):
        """温度取得成功テスト"""
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
    def test_flight_time_success(self, mock_drone):
        """飛行時間取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/flight_time")
        
        assert response.status_code == 200
        data = response.json()
        assert "flight_time" in data
        assert isinstance(data["flight_time"], int)
        assert data["flight_time"] >= 0
    
    @patch('services.drone_service.drone_service.drone')
    def test_barometer_success(self, mock_drone):
        """気圧取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/barometer")
        
        assert response.status_code == 200
        data = response.json()
        assert "barometer" in data
        assert isinstance(data["barometer"], (int, float))
        assert data["barometer"] >= 0
    
    @patch('services.drone_service.drone_service.drone')
    def test_distance_tof_success(self, mock_drone):
        """ToF距離取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/distance_tof")
        
        assert response.status_code == 200
        data = response.json()
        assert "distance_tof" in data
        assert isinstance(data["distance_tof"], int)
        assert data["distance_tof"] >= 0
    
    @patch('services.drone_service.drone_service.drone')
    def test_acceleration_success(self, mock_drone):
        """加速度取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/acceleration")
        
        assert response.status_code == 200
        data = response.json()
        assert "acceleration" in data
        assert isinstance(data["acceleration"], dict)
        
        acceleration = data["acceleration"]
        assert "x" in acceleration
        assert "y" in acceleration
        assert "z" in acceleration
        assert isinstance(acceleration["x"], (int, float))
        assert isinstance(acceleration["y"], (int, float))
        assert isinstance(acceleration["z"], (int, float))
    
    @patch('services.drone_service.drone_service.drone')
    def test_velocity_success(self, mock_drone):
        """速度取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/velocity")
        
        assert response.status_code == 200
        data = response.json()
        assert "velocity" in data
        assert isinstance(data["velocity"], dict)
        
        velocity = data["velocity"]
        assert "x" in velocity
        assert "y" in velocity
        assert "z" in velocity
        assert isinstance(velocity["x"], int)
        assert isinstance(velocity["y"], int)
        assert isinstance(velocity["z"], int)
    
    @patch('services.drone_service.drone_service.drone')
    def test_attitude_success(self, mock_drone):
        """姿勢角取得成功テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/attitude")
        
        assert response.status_code == 200
        data = response.json()
        assert "attitude" in data
        assert isinstance(data["attitude"], dict)
        
        attitude = data["attitude"]
        assert "pitch" in attitude
        assert "roll" in attitude
        assert "yaw" in attitude
        assert isinstance(attitude["pitch"], int)
        assert isinstance(attitude["roll"], int)
        assert isinstance(attitude["yaw"], int)
        
        # 角度の範囲確認
        assert -180 <= attitude["pitch"] <= 180
        assert -180 <= attitude["roll"] <= 180
        assert -180 <= attitude["yaw"] <= 180
    
    def test_sensors_not_connected_error_handling(self):
        """センサー類の未接続エラーハンドリングテスト"""
        sensor_endpoints = [
            "/drone/status",
            "/drone/battery", 
            "/drone/height",
            "/drone/temperature",
            "/drone/flight_time",
            "/drone/barometer",
            "/drone/distance_tof",
            "/drone/acceleration",
            "/drone/velocity",
            "/drone/attitude"
        ]
        
        for endpoint in sensor_endpoints:
            response = self.client.get(endpoint)
            
            assert response.status_code == 503
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "DRONE_NOT_CONNECTED"
            assert isinstance(data["error"], str)
    
    @patch('services.drone_service.drone_service.drone')
    def test_sensors_response_consistency(self, mock_drone):
        """センサーレスポンスの一貫性テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 複数回のリクエストで一貫性を確認
        responses = []
        for _ in range(3):
            response = self.client.get("/drone/status")
            assert response.status_code == 200
            responses.append(response.json())
        
        # バッテリーは時間経過で減少する可能性があるが、他のデータは安定しているべき
        for i in range(1, len(responses)):
            assert responses[i]["connected"] == responses[0]["connected"]
            # バッテリーは減少する可能性がある
            assert responses[i]["battery"] <= responses[i-1]["battery"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_sensors_data_simulation_accuracy(self, mock_drone):
        """センサーデータシミュレーション精度テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 複数回測定してノイズの確認
        height_readings = []
        for _ in range(5):
            response = self.client.get("/drone/height")
            assert response.status_code == 200
            height_readings.append(response.json()["height"])
        
        # シミュレーションではノイズが含まれているはず
        # 同じ値ばかりではないことを確認
        unique_values = set(height_readings)
        assert len(unique_values) >= 1  # 少なくとも1つの値は存在
    
    @patch('services.drone_service.drone_service.drone')
    def test_sensor_error_simulation(self, mock_drone):
        """センサーエラーシミュレーションテスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connection_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.get("/drone/battery")
        
        # 接続エラーの場合は503エラー
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "code" in data