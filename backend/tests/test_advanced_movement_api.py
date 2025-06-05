"""
高度な移動制御関連APIのテストケース
/drone/go_xyz, /drone/curve_xyz, /drone/rc_control エンドポイントのテスト
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


class TestAdvancedMovementAPI:
    """高度な移動制御関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
        self.boundary_data = TestConfig.get_boundary_test_data()
    
    @patch('services.drone_service.drone_service.drone')
    def test_go_xyz_success(self, mock_drone):
        """正常な座標移動テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/go_xyz", json={
            "x": 100,
            "y": -50,
            "z": 200,
            "speed": 50
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "移動" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_go_xyz_boundary_values(self, mock_drone):
        """座標移動境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary_tests = [
            # 最小値テスト
            {"x": -500, "y": -500, "z": -500, "speed": 10},
            # 最大値テスト
            {"x": 500, "y": 500, "z": 500, "speed": 100},
            # ゼロ値テスト
            {"x": 0, "y": 0, "z": 0, "speed": 50},
            # 中央値テスト
            {"x": 250, "y": -250, "z": 250, "speed": 55}
        ]
        
        for test_data in boundary_tests:
            response = self.client.post("/drone/go_xyz", json=test_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_go_xyz_invalid_coordinates(self):
        """無効な座標値テスト"""
        invalid_tests = [
            # X座標範囲外
            {"x": -501, "y": 0, "z": 0, "speed": 50},
            {"x": 501, "y": 0, "z": 0, "speed": 50},
            # Y座標範囲外
            {"x": 0, "y": -501, "z": 0, "speed": 50},
            {"x": 0, "y": 501, "z": 0, "speed": 50},
            # Z座標範囲外
            {"x": 0, "y": 0, "z": -501, "speed": 50},
            {"x": 0, "y": 0, "z": 501, "speed": 50},
            # 速度範囲外
            {"x": 0, "y": 0, "z": 0, "speed": 9},
            {"x": 0, "y": 0, "z": 0, "speed": 101}
        ]
        
        for test_data in invalid_tests:
            response = self.client.post("/drone/go_xyz", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_go_xyz_missing_parameters(self):
        """必須パラメータ未指定テスト"""
        missing_tests = [
            {"y": 0, "z": 0, "speed": 50},  # x missing
            {"x": 0, "z": 0, "speed": 50},  # y missing
            {"x": 0, "y": 0, "speed": 50},  # z missing
            {"x": 0, "y": 0, "z": 0}        # speed missing
        ]
        
        for test_data in missing_tests:
            response = self.client.post("/drone/go_xyz", json=test_data)
            assert response.status_code == 422
    
    def test_go_xyz_not_flying(self):
        """非飛行中での座標移動テスト"""
        response = self.client.post("/drone/go_xyz", json={
            "x": 100,
            "y": 0,
            "z": 100,
            "speed": 50
        })
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_curve_xyz_success(self, mock_drone):
        """正常な曲線飛行テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/curve_xyz", json={
            "x1": 100, "y1": 50, "z1": 100,
            "x2": 200, "y2": -50, "z2": 200,
            "speed": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "曲線飛行" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_curve_xyz_boundary_values(self, mock_drone):
        """曲線飛行境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary_tests = [
            # 最小値テスト
            {"x1": -500, "y1": -500, "z1": -500, "x2": -400, "y2": -400, "z2": -400, "speed": 10},
            # 最大値テスト
            {"x1": 400, "y1": 400, "z1": 400, "x2": 500, "y2": 500, "z2": 500, "speed": 60},
            # 速度境界値テスト
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 100, "z2": 100, "speed": 10},
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 100, "z2": 100, "speed": 60}
        ]
        
        for test_data in boundary_tests:
            response = self.client.post("/drone/curve_xyz", json=test_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_curve_xyz_invalid_parameters(self):
        """無効な曲線飛行パラメータテスト"""
        invalid_tests = [
            # 座標範囲外
            {"x1": -501, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30},
            {"x1": 0, "y1": 0, "z1": 0, "x2": 501, "y2": 0, "z2": 0, "speed": 30},
            # 速度範囲外
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 9},
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 61}
        ]
        
        for test_data in invalid_tests:
            response = self.client.post("/drone/curve_xyz", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_curve_xyz_missing_parameters(self):
        """曲線飛行必須パラメータ未指定テスト"""
        missing_tests = [
            {"y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30},  # x1 missing
            {"x1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30},  # y1 missing
            {"x1": 0, "y1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30},  # z1 missing
            {"x1": 0, "y1": 0, "z1": 0, "y2": 0, "z2": 0, "speed": 30},    # x2 missing
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "z2": 0, "speed": 30},  # y2 missing
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "speed": 30},  # z2 missing
            {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0}       # speed missing
        ]
        
        for test_data in missing_tests:
            response = self.client.post("/drone/curve_xyz", json=test_data)
            assert response.status_code == 422
    
    @patch('services.drone_service.drone_service.drone')
    def test_rc_control_success(self, mock_drone):
        """正常なRC制御テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/rc_control", json={
            "left_right_velocity": 50,
            "forward_backward_velocity": -30,
            "up_down_velocity": 20,
            "yaw_velocity": -10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "制御" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_rc_control_boundary_values(self, mock_drone):
        """RC制御境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary_tests = [
            # 最小値テスト
            {"left_right_velocity": -100, "forward_backward_velocity": -100, 
             "up_down_velocity": -100, "yaw_velocity": -100},
            # 最大値テスト
            {"left_right_velocity": 100, "forward_backward_velocity": 100, 
             "up_down_velocity": 100, "yaw_velocity": 100},
            # ゼロ値テスト
            {"left_right_velocity": 0, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": 0},
            # 混合値テスト
            {"left_right_velocity": 50, "forward_backward_velocity": -50, 
             "up_down_velocity": 25, "yaw_velocity": -25}
        ]
        
        for test_data in boundary_tests:
            response = self.client.post("/drone/rc_control", json=test_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_rc_control_invalid_velocity(self):
        """無効なRC制御速度テスト"""
        invalid_tests = [
            # 範囲外の値
            {"left_right_velocity": -101, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": 0},
            {"left_right_velocity": 101, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": 0},
            {"left_right_velocity": 0, "forward_backward_velocity": -101, 
             "up_down_velocity": 0, "yaw_velocity": 0},
            {"left_right_velocity": 0, "forward_backward_velocity": 101, 
             "up_down_velocity": 0, "yaw_velocity": 0},
            {"left_right_velocity": 0, "forward_backward_velocity": 0, 
             "up_down_velocity": -101, "yaw_velocity": 0},
            {"left_right_velocity": 0, "forward_backward_velocity": 0, 
             "up_down_velocity": 101, "yaw_velocity": 0},
            {"left_right_velocity": 0, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": -101},
            {"left_right_velocity": 0, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": 101}
        ]
        
        for test_data in invalid_tests:
            response = self.client.post("/drone/rc_control", json=test_data)
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_rc_control_missing_parameters(self):
        """RC制御必須パラメータ未指定テスト"""
        missing_tests = [
            {"forward_backward_velocity": 0, "up_down_velocity": 0, "yaw_velocity": 0},  # left_right_velocity missing
            {"left_right_velocity": 0, "up_down_velocity": 0, "yaw_velocity": 0},       # forward_backward_velocity missing
            {"left_right_velocity": 0, "forward_backward_velocity": 0, "yaw_velocity": 0},  # up_down_velocity missing
            {"left_right_velocity": 0, "forward_backward_velocity": 0, "up_down_velocity": 0}  # yaw_velocity missing
        ]
        
        for test_data in missing_tests:
            response = self.client.post("/drone/rc_control", json=test_data)
            assert response.status_code == 422
    
    def test_advanced_movement_type_validation(self):
        """データ型検証テスト"""
        # 文字列の座標
        response = self.client.post("/drone/go_xyz", json={
            "x": "100", "y": 0, "z": 0, "speed": 50
        })
        assert response.status_code == 422
        
        # 浮動小数点の角度（整数が期待される場合）
        response = self.client.post("/drone/curve_xyz", json={
            "x1": 100.5, "y1": 0, "z1": 0, "x2": 200, "y2": 0, "z2": 0, "speed": 30
        })
        # 実装依存：浮動小数点が許可される場合もある
        assert response.status_code in [200, 409, 422]
        
        # ブール値の速度
        response = self.client.post("/drone/rc_control", json={
            "left_right_velocity": True,
            "forward_backward_velocity": 0,
            "up_down_velocity": 0,
            "yaw_velocity": 0
        })
        assert response.status_code == 422
    
    def test_advanced_movement_not_flying(self):
        """非飛行中での高度移動制御テスト"""
        endpoints_data = [
            ("/drone/go_xyz", {"x": 100, "y": 0, "z": 100, "speed": 50}),
            ("/drone/curve_xyz", {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30}),
            ("/drone/rc_control", {"left_right_velocity": 0, "forward_backward_velocity": 0, 
                                   "up_down_velocity": 0, "yaw_velocity": 0})
        ]
        
        for endpoint, data in endpoints_data:
            response = self.client.post(endpoint, json=data)
            assert response.status_code == 409
            response_data = response.json()
            assert "error" in response_data
            assert "code" in response_data
            assert response_data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_advanced_movement_response_format(self, mock_drone):
        """高度移動制御レスポンス形式検証"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        endpoints_data = [
            ("/drone/go_xyz", {"x": 100, "y": 0, "z": 100, "speed": 50}),
            ("/drone/curve_xyz", {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 0, "z2": 0, "speed": 30}),
            ("/drone/rc_control", {"left_right_velocity": 50, "forward_backward_velocity": 0, 
                                   "up_down_velocity": 0, "yaw_velocity": 0})
        ]
        
        for endpoint, data in endpoints_data:
            response = self.client.post(endpoint, json=data)
            
            assert response.status_code == 200
            response_data = response.json()
            
            # StatusResponseスキーマの検証
            assert isinstance(response_data, dict)
            assert "success" in response_data
            assert "message" in response_data
            assert isinstance(response_data["success"], bool)
            assert isinstance(response_data["message"], str)
            assert response_data["success"] is True