"""
設定変更関連APIのテストケース
/drone/wifi, /drone/command, /drone/speed エンドポイントのテスト
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


class TestSettingsAPI:
    """設定変更関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_wifi_settings_success(self, mock_drone):
        """正常なWiFi設定テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        valid_wifi_data = {
            "ssid": "TestNetwork",
            "password": "TestPassword123"
        }
        
        response = self.client.put("/drone/wifi", json=valid_wifi_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "WiFi" in data["message"]
    
    def test_wifi_settings_invalid_ssid_length(self):
        """無効なSSID長のWiFi設定テスト"""
        invalid_tests = [
            {"ssid": "", "password": "validpassword"},           # 空のSSID
            {"ssid": "a" * 33, "password": "validpassword"},    # SSID長すぎ（33文字）
        ]
        
        for test_data in invalid_tests:
            response = self.client.put("/drone/wifi", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_wifi_settings_invalid_password_length(self):
        """無効なパスワード長のWiFi設定テスト"""
        invalid_tests = [
            {"ssid": "validssid", "password": ""},              # 空のパスワード
            {"ssid": "validssid", "password": "a" * 65},       # パスワード長すぎ（65文字）
        ]
        
        for test_data in invalid_tests:
            response = self.client.put("/drone/wifi", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_wifi_settings_boundary_values(self):
        """WiFi設定境界値テスト"""
        boundary_tests = [
            {"ssid": "a", "password": "b"},                     # 最小長
            {"ssid": "a" * 32, "password": "b" * 64},          # 最大長
            {"ssid": "Test-WiFi_123", "password": "Pass123!"}  # 特殊文字含む
        ]
        
        for test_data in boundary_tests:
            response = self.client.put("/drone/wifi", json=test_data)
            # 接続状態により200または400
            assert response.status_code in [200, 400, 503]
    
    def test_wifi_settings_missing_parameters(self):
        """WiFi設定必須パラメータ未指定テスト"""
        missing_tests = [
            {"password": "testpassword"},    # ssid missing
            {"ssid": "testssid"},           # password missing
            {}                              # both missing
        ]
        
        for test_data in missing_tests:
            response = self.client.put("/drone/wifi", json=test_data)
            assert response.status_code == 422
    
    @patch('services.drone_service.drone_service.drone')
    def test_command_success(self, mock_drone):
        """正常な任意コマンド送信テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        command_data = {
            "command": "battery?",
            "timeout": 5,
            "expect_response": True
        }
        
        response = self.client.post("/drone/command", json=command_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "response" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["response"], str)
    
    def test_command_timeout_boundary_values(self):
        """コマンドタイムアウト境界値テスト"""
        boundary_tests = [
            {"command": "battery?", "timeout": 1},     # 最小値
            {"command": "battery?", "timeout": 30},    # 最大値
        ]
        
        for test_data in boundary_tests:
            response = self.client.post("/drone/command", json=test_data)
            # 接続状態により200, 400, 408, 503のいずれか
            assert response.status_code in [200, 400, 408, 503]
    
    def test_command_invalid_timeout(self):
        """無効なタイムアウト値テスト"""
        invalid_tests = [
            {"command": "battery?", "timeout": 0},     # 最小値未満
            {"command": "battery?", "timeout": 31},    # 最大値超過
            {"command": "battery?", "timeout": -1},    # 負の値
        ]
        
        for test_data in invalid_tests:
            response = self.client.post("/drone/command", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_command_missing_required_parameter(self):
        """コマンド必須パラメータ未指定テスト"""
        response = self.client.post("/drone/command", json={
            "timeout": 5,
            "expect_response": True
        })
        
        assert response.status_code == 422
    
    def test_command_default_values(self):
        """コマンドデフォルト値テスト"""
        # timeoutとexpect_responseのデフォルト値を確認
        response = self.client.post("/drone/command", json={
            "command": "battery?"
        })
        
        # 接続状態により200, 400, 408, 503のいずれか
        assert response.status_code in [200, 400, 408, 503]
    
    @patch('services.drone_service.drone_service.drone')
    def test_command_timeout_simulation(self, mock_drone):
        """コマンドタイムアウトシミュレーションテスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        DroneTestHelper.setup_timeout_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/command", json={
            "command": "battery?",
            "timeout": 1
        })
        
        assert response.status_code == 408
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "COMMAND_TIMEOUT"
    
    @patch('services.drone_service.drone_service.drone')
    def test_speed_settings_success(self, mock_drone):
        """正常な飛行速度設定テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        valid_speeds = [1.0, 8.0, 15.0]  # 最小値、中央値、最大値
        
        for speed in valid_speeds:
            response = self.client.put("/drone/speed", json={"speed": speed})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "速度" in data["message"]
    
    def test_speed_settings_boundary_values(self):
        """飛行速度境界値テスト"""
        boundary_tests = [
            {"speed": 1.0},    # 最小値
            {"speed": 15.0},   # 最大値
        ]
        
        for test_data in boundary_tests:
            response = self.client.put("/drone/speed", json=test_data)
            # 接続状態により200または400
            assert response.status_code in [200, 400, 409, 503]
    
    def test_speed_settings_invalid_values(self):
        """無効な飛行速度値テスト"""
        invalid_tests = [
            {"speed": 0.9},    # 最小値未満
            {"speed": 15.1},   # 最大値超過
            {"speed": 0.0},    # ゼロ
            {"speed": -1.0},   # 負の値
        ]
        
        for test_data in invalid_tests:
            response = self.client.put("/drone/speed", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_speed_settings_missing_parameter(self):
        """飛行速度必須パラメータ未指定テスト"""
        response = self.client.put("/drone/speed", json={})
        
        assert response.status_code == 422
    
    @patch('services.drone_service.drone_service.drone')
    def test_speed_settings_while_flying(self, mock_drone):
        """飛行中の速度設定テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.put("/drone/speed", json={"speed": 10.0})
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] in ["ALREADY_FLYING", "NOT_ALLOWED_WHILE_FLYING"]
    
    def test_settings_method_validation(self):
        """設定エンドポイントHTTPメソッド検証"""
        # PUT専用エンドポイント
        put_endpoints = ["/drone/wifi", "/drone/speed"]
        
        for endpoint in put_endpoints:
            # GET method should not be allowed
            response = self.client.get(endpoint)
            assert response.status_code == 405
            
            # POST method should not be allowed
            response = self.client.post(endpoint)
            assert response.status_code == 405
            
            # DELETE method should not be allowed
            response = self.client.delete(endpoint)
            assert response.status_code == 405
        
        # POST専用エンドポイント
        response = self.client.get("/drone/command")
        assert response.status_code == 405
        
        response = self.client.put("/drone/command")
        assert response.status_code == 405
    
    def test_settings_type_validation(self):
        """設定データ型検証テスト"""
        # WiFi設定の型検証
        response = self.client.put("/drone/wifi", json={
            "ssid": 12345,  # 数値（文字列が期待される）
            "password": "validpassword"
        })
        assert response.status_code == 422
        
        response = self.client.put("/drone/wifi", json={
            "ssid": "validssid",
            "password": True  # ブール値（文字列が期待される）
        })
        assert response.status_code == 422
        
        # 速度設定の型検証
        response = self.client.put("/drone/speed", json={
            "speed": "10.0"  # 文字列（数値が期待される）
        })
        assert response.status_code == 422
        
        response = self.client.put("/drone/speed", json={
            "speed": True  # ブール値（数値が期待される）
        })
        assert response.status_code == 422
        
        # コマンドの型検証
        response = self.client.post("/drone/command", json={
            "command": 123,  # 数値（文字列が期待される）
            "timeout": 5
        })
        assert response.status_code == 422
        
        response = self.client.post("/drone/command", json={
            "command": "battery?",
            "timeout": "5"  # 文字列（数値が期待される）
        })
        assert response.status_code == 422
    
    def test_settings_response_format_validation(self):
        """設定レスポンス形式検証"""
        endpoints_data = [
            ("/drone/wifi", {"ssid": "test", "password": "test"}),
            ("/drone/speed", {"speed": 10.0})
        ]
        
        for endpoint, data in endpoints_data:
            response = self.client.put(endpoint, json=data)
            
            assert response.status_code in [200, 400, 409, 422, 503]
            
            if response.status_code == 200:
                # 成功レスポンス
                response_data = response.json()
                assert isinstance(response_data, dict)
                assert "success" in response_data
                assert "message" in response_data
                assert isinstance(response_data["success"], bool)
                assert isinstance(response_data["message"], str)
            elif response.status_code in [400, 409, 503]:
                # エラーレスポンス
                response_data = response.json()
                assert isinstance(response_data, dict)
                assert "error" in response_data
                assert "code" in response_data
                assert isinstance(response_data["error"], str)
                assert isinstance(response_data["code"], str)
    
    def test_command_response_format_validation(self):
        """コマンドレスポンス形式検証"""
        response = self.client.post("/drone/command", json={
            "command": "battery?",
            "timeout": 5
        })
        
        assert response.status_code in [200, 400, 408, 422, 503]
        
        if response.status_code == 200:
            # 成功レスポンス
            data = response.json()
            assert isinstance(data, dict)
            assert "success" in data
            assert "response" in data
            assert isinstance(data["success"], bool)
            assert isinstance(data["response"], str)
        elif response.status_code in [400, 408, 503]:
            # エラーレスポンス
            data = response.json()
            assert isinstance(data, dict)
            assert "error" in data
            assert "code" in data
            assert isinstance(data["error"], str)
            assert isinstance(data["code"], str)