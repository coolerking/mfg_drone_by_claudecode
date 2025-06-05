"""
移動制御関連APIのテストケース
/drone/move, /drone/rotate, /drone/flip エンドポイントのテスト
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


class TestMovementAPI:
    """移動制御関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
        self.boundary_data = TestConfig.get_boundary_test_data()
        self.valid_enums = TestConfig.get_valid_enum_values()
        self.invalid_enums = TestConfig.get_invalid_enum_values()
    
    @patch('services.drone_service.drone_service.drone')
    def test_move_success_all_directions(self, mock_drone):
        """全方向の正常移動テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        for direction in self.valid_enums["move_direction"]:
            response = self.client.post("/drone/move", json={
                "direction": direction,
                "distance": 100
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "移動" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_move_boundary_values(self, mock_drone):
        """移動距離境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary = self.boundary_data["move_distance"]
        
        # 最小値テスト
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": boundary["min"]
        })
        assert response.status_code == 200
        
        # 最大値テスト
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": boundary["max"]
        })
        assert response.status_code == 200
    
    def test_move_invalid_distance_below_min(self):
        """移動距離最小値未満テスト"""
        boundary = self.boundary_data["move_distance"]
        
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": boundary["below_min"]
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    def test_move_invalid_distance_above_max(self):
        """移動距離最大値超過テスト"""
        boundary = self.boundary_data["move_distance"]
        
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": boundary["above_max"]
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    def test_move_invalid_direction(self):
        """無効な移動方向テスト"""
        for invalid_direction in self.invalid_enums["move_direction"]:
            response = self.client.post("/drone/move", json={
                "direction": invalid_direction,
                "distance": 100
            })
            
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_move_not_flying(self):
        """非飛行中の移動テスト"""
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": 100
        })
        
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "NOT_FLYING"
    
    @patch('services.drone_service.drone_service.drone')
    def test_rotate_success_all_directions(self, mock_drone):
        """全方向の正常回転テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        for direction in self.valid_enums["rotate_direction"]:
            response = self.client.post("/drone/rotate", json={
                "direction": direction,
                "angle": 90
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "回転" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_rotate_boundary_values(self, mock_drone):
        """回転角度境界値テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        boundary = self.boundary_data["rotate_angle"]
        
        # 最小値テスト
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": boundary["min"]
        })
        assert response.status_code == 200
        
        # 最大値テスト
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": boundary["max"]
        })
        assert response.status_code == 200
    
    def test_rotate_invalid_angle_below_min(self):
        """回転角度最小値未満テスト"""
        boundary = self.boundary_data["rotate_angle"]
        
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": boundary["below_min"]
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    def test_rotate_invalid_angle_above_max(self):
        """回転角度最大値超過テスト"""
        boundary = self.boundary_data["rotate_angle"]
        
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": boundary["above_max"]
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    @patch('services.drone_service.drone_service.drone')
    def test_flip_success_all_directions(self, mock_drone):
        """全方向の正常宙返りテスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        for direction in self.valid_enums["flip_direction"]:
            response = self.client.post("/drone/flip", json={
                "direction": direction
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "宙返り" in data["message"]
    
    def test_flip_invalid_direction(self):
        """無効な宙返り方向テスト"""
        for invalid_direction in self.invalid_enums["flip_direction"]:
            response = self.client.post("/drone/flip", json={
                "direction": invalid_direction
            })
            
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "code" in data
            assert data["code"] == "INVALID_PARAMETER"
    
    def test_movement_missing_parameters(self):
        """必須パラメータ未指定テスト"""
        # move: direction未指定
        response = self.client.post("/drone/move", json={"distance": 100})
        assert response.status_code == 422
        
        # move: distance未指定
        response = self.client.post("/drone/move", json={"direction": "forward"})
        assert response.status_code == 422
        
        # rotate: direction未指定
        response = self.client.post("/drone/rotate", json={"angle": 90})
        assert response.status_code == 422
        
        # rotate: angle未指定
        response = self.client.post("/drone/rotate", json={"direction": "clockwise"})
        assert response.status_code == 422
        
        # flip: direction未指定
        response = self.client.post("/drone/flip", json={})
        assert response.status_code == 422
    
    def test_movement_negative_values(self):
        """負の値テスト"""
        # 負の移動距離
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": -50
        })
        assert response.status_code == 400
        
        # 負の回転角度
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": -30
        })
        assert response.status_code == 400
    
    def test_movement_zero_values(self):
        """ゼロ値テスト"""
        # ゼロ移動距離
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": 0
        })
        assert response.status_code == 400
        
        # ゼロ回転角度
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": 0
        })
        assert response.status_code == 400
    
    def test_movement_type_validation(self):
        """データ型検証テスト"""
        # 文字列の距離
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": "100"
        })
        assert response.status_code == 422
        
        # 文字列の角度
        response = self.client.post("/drone/rotate", json={
            "direction": "clockwise",
            "angle": "90"
        })
        assert response.status_code == 422
        
        # 数値の方向
        response = self.client.post("/drone/move", json={
            "direction": 123,
            "distance": 100
        })
        assert response.status_code == 422
    
    def test_movement_extra_parameters(self):
        """余分なパラメータテスト"""
        # 余分なパラメータを含むが正常に動作することを確認
        response = self.client.post("/drone/move", json={
            "direction": "forward",
            "distance": 100,
            "extra_param": "should_be_ignored"
        })
        # パラメータ検証による422エラーまたは正常な200レスポンス
        assert response.status_code in [200, 409, 422]
    
    @patch('services.drone_service.drone_service.drone')
    def test_movement_response_format(self, mock_drone):
        """移動制御レスポンス形式検証"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_flying_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        endpoints_data = [
            ("/drone/move", {"direction": "forward", "distance": 100}),
            ("/drone/rotate", {"direction": "clockwise", "angle": 90}),
            ("/drone/flip", {"direction": "left"})
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