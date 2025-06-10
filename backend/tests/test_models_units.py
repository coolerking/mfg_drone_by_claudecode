"""
データモデル単体テスト
models/requests.py と models/responses.py の個別モデル単体テスト - Phase 1
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.requests import (
    MoveRequest, RotateRequest, FlipRequest, GoXYZRequest, CurveXYZRequest,
    RCControlRequest, CameraSettingsRequest, WiFiRequest, CommandRequest,
    SpeedRequest, MissionPadDetectionDirectionRequest, MissionPadGoXYZRequest,
    TrackingStartRequest, ModelTrainRequest,
    MoveDirection, RotateDirection, FlipDirection, CameraResolution, CameraFPS, TrackingMode
)
from models.responses import (
    StatusResponse, ErrorResponse, AccelerationData, VelocityData, AttitudeData,
    DroneStatus, BatteryResponse, HeightResponse, TemperatureResponse,
    FlightTimeResponse, BarometerResponse, DistanceToFResponse,
    AccelerationResponse, VelocityResponse, AttitudeResponse,
    CommandResponse, MissionPadStatusResponse, TrackingPosition,
    TrackingStatusResponse, ModelInfo, ModelListResponse, ModelTrainResponse,
    ErrorCode
)


class TestMoveRequest:
    """MoveRequestモデル単体テスト"""
    
    def test_move_request_valid_data(self):
        """MoveRequest有効データテスト"""
        # 有効な中央値データ
        valid_data = {"direction": "forward", "distance": 100}
        request = MoveRequest(**valid_data)
        
        assert request.direction == MoveDirection.FORWARD
        assert request.distance == 100
        assert isinstance(request.direction, MoveDirection)
        assert isinstance(request.distance, int)
    
    def test_move_request_boundary_values(self):
        """MoveRequest境界値テスト"""
        # 境界値テスト: 最小値、最大値
        boundary_cases = [
            {"direction": "up", "distance": 20},     # 最小値
            {"direction": "down", "distance": 500},  # 最大値
            {"direction": "left", "distance": 260},  # 中央値
        ]
        
        for data in boundary_cases:
            request = MoveRequest(**data)
            assert request.direction == MoveDirection(data["direction"])
            assert request.distance == data["distance"]
    
    def test_move_request_invalid_distance(self):
        """MoveRequest無効距離テスト"""
        # 距離境界値超過テスト
        invalid_distances = [
            19,   # 最小値未満
            501,  # 最大値超過
            -50,  # 負の値
            0,    # ゼロ
        ]
        
        for distance in invalid_distances:
            with pytest.raises(ValidationError) as exc_info:
                MoveRequest(direction="forward", distance=distance)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0
            assert any("distance" in str(error) for error in errors)
    
    def test_move_request_invalid_direction(self):
        """MoveRequest無効方向テスト"""
        # 無効な方向値
        invalid_directions = [
            "invalid_direction",
            "top",
            "bottom", 
            "",
            None,
            123,
        ]
        
        for direction in invalid_directions:
            with pytest.raises(ValidationError) as exc_info:
                MoveRequest(direction=direction, distance=100)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0
    
    def test_move_direction_enum_values(self):
        """MoveDirection列挙値テスト"""
        # 全ての有効な方向をテスト
        valid_directions = ["up", "down", "left", "right", "forward", "back"]
        
        for direction in valid_directions:
            request = MoveRequest(direction=direction, distance=100)
            assert request.direction.value == direction
            assert isinstance(request.direction, MoveDirection)


class TestRotateRequest:
    """RotateRequestモデル単体テスト"""
    
    def test_rotate_request_valid_data(self):
        """RotateRequest有効データテスト"""
        valid_data = {"direction": "clockwise", "angle": 90}
        request = RotateRequest(**valid_data)
        
        assert request.direction == RotateDirection.CLOCKWISE
        assert request.angle == 90
    
    def test_rotate_request_boundary_values(self):
        """RotateRequest境界値テスト"""
        boundary_cases = [
            {"direction": "clockwise", "angle": 1},         # 最小値
            {"direction": "counter_clockwise", "angle": 360}, # 最大値
            {"direction": "clockwise", "angle": 180},       # 中央値
        ]
        
        for data in boundary_cases:
            request = RotateRequest(**data)
            assert request.direction == RotateDirection(data["direction"])
            assert request.angle == data["angle"]
    
    def test_rotate_request_invalid_angle(self):
        """RotateRequest無効角度テスト"""
        invalid_angles = [
            0,    # 最小値未満
            361,  # 最大値超過
            -30,  # 負の値
        ]
        
        for angle in invalid_angles:
            with pytest.raises(ValidationError) as exc_info:
                RotateRequest(direction="clockwise", angle=angle)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0
            assert any("angle" in str(error) for error in errors)


class TestGoXYZRequest:
    """GoXYZRequestモデル単体テスト"""
    
    def test_go_xyz_request_valid_data(self):
        """GoXYZRequest有効データテスト"""
        valid_data = {"x": 100, "y": -50, "z": 200, "speed": 50}
        request = GoXYZRequest(**valid_data)
        
        assert request.x == 100
        assert request.y == -50
        assert request.z == 200
        assert request.speed == 50
    
    def test_go_xyz_request_boundary_values(self):
        """GoXYZRequest境界値テスト"""
        boundary_cases = [
            {"x": -500, "y": -500, "z": -500, "speed": 10},  # 最小値
            {"x": 500, "y": 500, "z": 500, "speed": 100},    # 最大値
            {"x": 0, "y": 0, "z": 0, "speed": 55},           # 中央値
        ]
        
        for data in boundary_cases:
            request = GoXYZRequest(**data)
            assert request.x == data["x"]
            assert request.y == data["y"] 
            assert request.z == data["z"]
            assert request.speed == data["speed"]
    
    def test_go_xyz_request_invalid_coordinates(self):
        """GoXYZRequest無効座標テスト"""
        # X座標境界値超過
        invalid_x_cases = [
            {"x": -501, "y": 0, "z": 0, "speed": 50},  # X最小値未満
            {"x": 501, "y": 0, "z": 0, "speed": 50},   # X最大値超過
        ]
        
        for data in invalid_x_cases:
            with pytest.raises(ValidationError) as exc_info:
                GoXYZRequest(**data)
            
            errors = exc_info.value.errors()
            assert any("x" in str(error) for error in errors)
        
        # Y座標境界値超過
        invalid_y_cases = [
            {"x": 0, "y": -501, "z": 0, "speed": 50},  # Y最小値未満
            {"x": 0, "y": 501, "z": 0, "speed": 50},   # Y最大値超過
        ]
        
        for data in invalid_y_cases:
            with pytest.raises(ValidationError) as exc_info:
                GoXYZRequest(**data)
            
            errors = exc_info.value.errors()
            assert any("y" in str(error) for error in errors)
        
        # Z座標境界値超過
        invalid_z_cases = [
            {"x": 0, "y": 0, "z": -501, "speed": 50},  # Z最小値未満
            {"x": 0, "y": 0, "z": 501, "speed": 50},   # Z最大値超過
        ]
        
        for data in invalid_z_cases:
            with pytest.raises(ValidationError) as exc_info:
                GoXYZRequest(**data)
            
            errors = exc_info.value.errors()
            assert any("z" in str(error) for error in errors)
    
    def test_go_xyz_request_invalid_speed(self):
        """GoXYZRequest無効速度テスト"""
        invalid_speed_cases = [
            {"x": 0, "y": 0, "z": 0, "speed": 9},    # 速度最小値未満
            {"x": 0, "y": 0, "z": 0, "speed": 101},  # 速度最大値超過
            {"x": 0, "y": 0, "z": 0, "speed": 0},    # ゼロ速度
            {"x": 0, "y": 0, "z": 0, "speed": -10},  # 負の速度
        ]
        
        for data in invalid_speed_cases:
            with pytest.raises(ValidationError) as exc_info:
                GoXYZRequest(**data)
            
            errors = exc_info.value.errors()
            assert any("speed" in str(error) for error in errors)


class TestRCControlRequest:
    """RCControlRequestモデル単体テスト"""
    
    def test_rc_control_request_valid_data(self):
        """RCControlRequest有効データテスト"""
        valid_data = {
            "left_right_velocity": 20,
            "forward_backward_velocity": -30,
            "up_down_velocity": 10,
            "yaw_velocity": 15
        }
        request = RCControlRequest(**valid_data)
        
        assert request.left_right_velocity == 20
        assert request.forward_backward_velocity == -30
        assert request.up_down_velocity == 10
        assert request.yaw_velocity == 15
    
    def test_rc_control_request_boundary_values(self):
        """RCControlRequest境界値テスト"""
        boundary_cases = [
            {"left_right_velocity": -100, "forward_backward_velocity": -100, 
             "up_down_velocity": -100, "yaw_velocity": -100},  # 最小値
            {"left_right_velocity": 100, "forward_backward_velocity": 100,
             "up_down_velocity": 100, "yaw_velocity": 100},    # 最大値
            {"left_right_velocity": 0, "forward_backward_velocity": 0,
             "up_down_velocity": 0, "yaw_velocity": 0},        # 中央値
        ]
        
        for data in boundary_cases:
            request = RCControlRequest(**data)
            assert request.left_right_velocity == data["left_right_velocity"]
            assert request.forward_backward_velocity == data["forward_backward_velocity"]
            assert request.up_down_velocity == data["up_down_velocity"]
            assert request.yaw_velocity == data["yaw_velocity"]
    
    def test_rc_control_request_invalid_values(self):
        """RCControlRequest無効値テスト"""
        # 各速度パラメータの境界値超過テスト
        invalid_cases = [
            {"left_right_velocity": -101, "forward_backward_velocity": 0, 
             "up_down_velocity": 0, "yaw_velocity": 0},        # left_right最小値未満
            {"left_right_velocity": 101, "forward_backward_velocity": 0,
             "up_down_velocity": 0, "yaw_velocity": 0},        # left_right最大値超過
            {"left_right_velocity": 0, "forward_backward_velocity": -101,
             "up_down_velocity": 0, "yaw_velocity": 0},        # forward_backward最小値未満
            {"left_right_velocity": 0, "forward_backward_velocity": 101,
             "up_down_velocity": 0, "yaw_velocity": 0},        # forward_backward最大値超過
        ]
        
        for data in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                RCControlRequest(**data)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0


class TestWiFiRequest:
    """WiFiRequestモデル単体テスト"""
    
    def test_wifi_request_valid_data(self):
        """WiFiRequest有効データテスト"""
        valid_data = {"ssid": "TestNetwork", "password": "TestPassword123"}
        request = WiFiRequest(**valid_data)
        
        assert request.ssid == "TestNetwork"
        assert request.password == "TestPassword123"
    
    def test_wifi_request_boundary_values(self):
        """WiFiRequest境界値テスト"""
        boundary_cases = [
            {"ssid": "A", "password": "B"},              # 最小長
            {"ssid": "A" * 32, "password": "B" * 64},    # 最大長
            {"ssid": "Test", "password": "Password"},    # 中間長
        ]
        
        for data in boundary_cases:
            request = WiFiRequest(**data)
            assert request.ssid == data["ssid"]
            assert request.password == data["password"]
    
    def test_wifi_request_invalid_data(self):
        """WiFiRequest無効データテスト"""
        invalid_cases = [
            {"ssid": "A" * 33, "password": "valid"},      # SSID長すぎ
            {"ssid": "valid", "password": "B" * 65},      # パスワード長すぎ
            {"ssid": "", "password": "valid"},            # 空のSSID
            {"ssid": "valid", "password": ""},            # 空のパスワード
        ]
        
        for data in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                WiFiRequest(**data)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0


class TestSpeedRequest:
    """SpeedRequestモデル単体テスト"""
    
    def test_speed_request_valid_data(self):
        """SpeedRequest有効データテスト"""
        valid_data = {"speed": 10.5}
        request = SpeedRequest(**valid_data)
        
        assert request.speed == 10.5
        assert isinstance(request.speed, float)
    
    def test_speed_request_boundary_values(self):
        """SpeedRequest境界値テスト"""
        boundary_values = [
            1.0,   # 最小値
            15.0,  # 最大値
            8.0,   # 中央値
        ]
        
        for speed in boundary_values:
            request = SpeedRequest(speed=speed)
            assert request.speed == speed
    
    def test_speed_request_invalid_values(self):
        """SpeedRequest無効値テスト"""
        invalid_speeds = [
            0.9,   # 最小値未満
            15.1,  # 最大値超過
            -5.0,  # 負の値
            0.0,   # ゼロ
        ]
        
        for speed in invalid_speeds:
            with pytest.raises(ValidationError) as exc_info:
                SpeedRequest(speed=speed)
            
            errors = exc_info.value.errors()
            assert any("speed" in str(error) for error in errors)


class TestStatusResponse:
    """StatusResponseモデル単体テスト"""
    
    def test_status_response_valid_data(self):
        """StatusResponse有効データテスト"""
        valid_data = {"success": True, "message": "操作が成功しました"}
        response = StatusResponse(**valid_data)
        
        assert response.success is True
        assert response.message == "操作が成功しました"
        assert isinstance(response.success, bool)
        assert isinstance(response.message, str)
    
    def test_status_response_boundary_values(self):
        """StatusResponse境界値テスト"""
        boundary_cases = [
            {"success": True, "message": ""},                # 空メッセージ
            {"success": False, "message": "A"},              # 最小メッセージ
            {"success": True, "message": "A" * 1000},        # 長いメッセージ
            {"success": False, "message": "エラーが発生しました"}, # 日本語メッセージ
        ]
        
        for data in boundary_cases:
            response = StatusResponse(**data)
            assert response.success == data["success"]
            assert response.message == data["message"]
    
    def test_status_response_type_validation(self):
        """StatusResponse型検証テスト"""
        # success フィールドの型検証
        invalid_success_cases = [
            {"success": "true", "message": "test"},   # 文字列
            {"success": 1, "message": "test"},        # 数値
            {"success": None, "message": "test"},     # None
        ]
        
        for data in invalid_success_cases:
            with pytest.raises(ValidationError) as exc_info:
                StatusResponse(**data)
            
            errors = exc_info.value.errors()
            assert any("success" in str(error) for error in errors)


class TestErrorResponse:
    """ErrorResponseモデル単体テスト"""
    
    def test_error_response_valid_data(self):
        """ErrorResponse有効データテスト"""
        valid_data = {
            "error": "ドローンに接続できませんでした",
            "code": ErrorCode.DRONE_CONNECTION_FAILED,
            "details": {"attempt": 1, "timeout": 5}
        }
        response = ErrorResponse(**valid_data)
        
        assert response.error == "ドローンに接続できませんでした"
        assert response.code == ErrorCode.DRONE_CONNECTION_FAILED
        assert response.details == {"attempt": 1, "timeout": 5}
    
    def test_error_response_boundary_values(self):
        """ErrorResponse境界値テスト"""
        # 全エラーコードテスト
        all_error_codes = [
            ErrorCode.DRONE_NOT_CONNECTED,
            ErrorCode.DRONE_CONNECTION_FAILED,
            ErrorCode.INVALID_PARAMETER,
            ErrorCode.COMMAND_FAILED,
            ErrorCode.COMMAND_TIMEOUT,
            ErrorCode.NOT_FLYING,
            ErrorCode.ALREADY_FLYING,
            ErrorCode.STREAMING_NOT_STARTED,
            ErrorCode.STREAMING_ALREADY_STARTED,
            ErrorCode.MODEL_NOT_FOUND,
            ErrorCode.TRAINING_IN_PROGRESS,
            ErrorCode.FILE_TOO_LARGE,
            ErrorCode.UNSUPPORTED_FORMAT,
            ErrorCode.INTERNAL_ERROR,
        ]
        
        for code in all_error_codes:
            response = ErrorResponse(
                error=f"エラー: {code.value}",
                code=code,
                details=None
            )
            assert response.code == code
            assert response.details is None
    
    def test_error_response_optional_details(self):
        """ErrorResponseオプション詳細テスト"""
        # detailsなし
        response = ErrorResponse(
            error="エラーメッセージ",
            code=ErrorCode.INTERNAL_ERROR
        )
        assert response.details is None
        
        # 空のdetails
        response = ErrorResponse(
            error="エラーメッセージ",
            code=ErrorCode.INTERNAL_ERROR,
            details={}
        )
        assert response.details == {}


class TestAccelerationData:
    """AccelerationDataモデル単体テスト"""
    
    def test_acceleration_data_valid_data(self):
        """AccelerationData有効データテスト"""
        valid_data = {"x": 0.5, "y": -0.3, "z": 1.0}
        data = AccelerationData(**valid_data)
        
        assert data.x == 0.5
        assert data.y == -0.3
        assert data.z == 1.0
        assert isinstance(data.x, float)
        assert isinstance(data.y, float)
        assert isinstance(data.z, float)
    
    def test_acceleration_data_boundary_values(self):
        """AccelerationData境界値テスト"""
        boundary_cases = [
            {"x": -10.0, "y": -10.0, "z": -10.0},   # 大きな負の値
            {"x": 0.0, "y": 0.0, "z": 0.0},         # ゼロ値
            {"x": 10.0, "y": 10.0, "z": 10.0},      # 大きな正の値
            {"x": 0.001, "y": 0.001, "z": 0.001},   # 小さな正の値
        ]
        
        for case in boundary_cases:
            data = AccelerationData(**case)
            assert data.x == case["x"]
            assert data.y == case["y"]
            assert data.z == case["z"]
    
    def test_acceleration_data_type_conversion(self):
        """AccelerationData型変換テスト"""
        # 整数から浮動小数点への変換
        data = AccelerationData(x=1, y=2, z=3)
        assert data.x == 1.0
        assert data.y == 2.0
        assert data.z == 3.0
        assert isinstance(data.x, float)


class TestAttitudeData:
    """AttitudeDataモデル単体テスト"""
    
    def test_attitude_data_valid_data(self):
        """AttitudeData有効データテスト"""
        valid_data = {"pitch": 15, "roll": -30, "yaw": 90}
        data = AttitudeData(**valid_data)
        
        assert data.pitch == 15
        assert data.roll == -30
        assert data.yaw == 90
    
    def test_attitude_data_boundary_values(self):
        """AttitudeData境界値テスト"""
        boundary_cases = [
            {"pitch": -180, "roll": -180, "yaw": -180},  # 最小値
            {"pitch": 180, "roll": 180, "yaw": 180},     # 最大値
            {"pitch": 0, "roll": 0, "yaw": 0},           # 中央値
        ]
        
        for case in boundary_cases:
            data = AttitudeData(**case)
            assert data.pitch == case["pitch"]
            assert data.roll == case["roll"]
            assert data.yaw == case["yaw"]
    
    def test_attitude_data_invalid_values(self):
        """AttitudeData無効値テスト"""
        invalid_cases = [
            {"pitch": -181, "roll": 0, "yaw": 0},    # pitch最小値未満
            {"pitch": 181, "roll": 0, "yaw": 0},     # pitch最大値超過
            {"pitch": 0, "roll": -181, "yaw": 0},    # roll最小値未満
            {"pitch": 0, "roll": 181, "yaw": 0},     # roll最大値超過
            {"pitch": 0, "roll": 0, "yaw": -181},    # yaw最小値未満
            {"pitch": 0, "roll": 0, "yaw": 181},     # yaw最大値超過
        ]
        
        for case in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                AttitudeData(**case)
            
            errors = exc_info.value.errors()
            assert len(errors) > 0


class TestModelInfo:
    """ModelInfoモデル単体テスト"""
    
    def test_model_info_valid_data(self):
        """ModelInfo有効データテスト"""
        created_at = datetime.now()
        valid_data = {
            "name": "person_detector",
            "created_at": created_at,
            "accuracy": 0.85
        }
        model = ModelInfo(**valid_data)
        
        assert model.name == "person_detector"
        assert model.created_at == created_at
        assert model.accuracy == 0.85
    
    def test_model_info_boundary_values(self):
        """ModelInfo境界値テスト"""
        created_at = datetime.now()
        boundary_cases = [
            {"name": "A", "created_at": created_at, "accuracy": 0.0},     # 最小精度
            {"name": "A" * 100, "created_at": created_at, "accuracy": 1.0}, # 最大精度
            {"name": "detector", "created_at": created_at, "accuracy": 0.5}, # 中央精度
        ]
        
        for case in boundary_cases:
            model = ModelInfo(**case)
            assert model.name == case["name"]
            assert model.accuracy == case["accuracy"]
    
    def test_model_info_type_validation(self):
        """ModelInfo型検証テスト"""
        created_at = datetime.now()
        
        # accuracyの型検証
        invalid_accuracy_cases = [
            {"name": "test", "created_at": created_at, "accuracy": "0.85"},  # 文字列
            {"name": "test", "created_at": created_at, "accuracy": None},    # None
        ]
        
        for case in invalid_accuracy_cases:
            with pytest.raises(ValidationError) as exc_info:
                ModelInfo(**case)
            
            errors = exc_info.value.errors()
            assert any("accuracy" in str(error) for error in errors)


class TestEnumValues:
    """列挙値単体テスト"""
    
    def test_move_direction_enum(self):
        """MoveDirection列挙値テスト"""
        expected_values = ["up", "down", "left", "right", "forward", "back"]
        actual_values = [direction.value for direction in MoveDirection]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_rotate_direction_enum(self):
        """RotateDirection列挙値テスト"""
        expected_values = ["clockwise", "counter_clockwise"]
        actual_values = [direction.value for direction in RotateDirection]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_flip_direction_enum(self):
        """FlipDirection列挙値テスト"""
        expected_values = ["left", "right", "forward", "back"]
        actual_values = [direction.value for direction in FlipDirection]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_camera_resolution_enum(self):
        """CameraResolution列挙値テスト"""
        expected_values = ["high", "low"]
        actual_values = [resolution.value for resolution in CameraResolution]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_camera_fps_enum(self):
        """CameraFPS列挙値テスト"""
        expected_values = ["high", "middle", "low"]
        actual_values = [fps.value for fps in CameraFPS]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_tracking_mode_enum(self):
        """TrackingMode列挙値テスト"""
        expected_values = ["center", "follow"]
        actual_values = [mode.value for mode in TrackingMode]
        
        assert set(actual_values) == set(expected_values)
        assert len(actual_values) == len(expected_values)
    
    def test_error_code_enum(self):
        """ErrorCode列挙値テスト"""
        expected_codes = [
            "DRONE_NOT_CONNECTED", "DRONE_CONNECTION_FAILED", "INVALID_PARAMETER",
            "COMMAND_FAILED", "COMMAND_TIMEOUT", "NOT_FLYING", "ALREADY_FLYING",
            "STREAMING_NOT_STARTED", "STREAMING_ALREADY_STARTED", "MODEL_NOT_FOUND",
            "TRAINING_IN_PROGRESS", "FILE_TOO_LARGE", "UNSUPPORTED_FORMAT", "INTERNAL_ERROR"
        ]
        actual_codes = [code.value for code in ErrorCode]
        
        assert set(actual_codes) == set(expected_codes)
        assert len(actual_codes) == len(expected_codes)