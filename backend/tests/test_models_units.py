"""
Phase 1 Unit Tests: Data Models
Pydanticデータモデルの単体テスト
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.requests import (
    MoveDirection, RotateDirection, FlipDirection, CameraResolution, CameraFPS,
    TrackingMode, MoveRequest, RotateRequest, FlipRequest, GoXYZRequest,
    CurveXYZRequest, RCControlRequest, CameraSettingsRequest, WiFiRequest,
    CommandRequest, SpeedRequest, MissionPadDetectionDirectionRequest,
    MissionPadGoXYZRequest, TrackingStartRequest, ModelTrainRequest
)
from models.responses import (
    ErrorCode, StatusResponse, ErrorResponse, AccelerationData, VelocityData,
    AttitudeData, DroneStatus, BatteryResponse, HeightResponse, TemperatureResponse,
    FlightTimeResponse, BarometerResponse, DistanceToFResponse, AccelerationResponse,
    VelocityResponse, AttitudeResponse, CommandResponse, MissionPadStatusResponse,
    TrackingPosition, TrackingStatusResponse, ModelInfo, ModelListResponse,
    ModelTrainResponse
)


class TestRequestEnums:
    """リクエストEnum型テスト"""

    def test_move_direction_enum_values(self):
        """移動方向Enum値テスト"""
        assert MoveDirection.UP == "up"
        assert MoveDirection.DOWN == "down"
        assert MoveDirection.LEFT == "left"
        assert MoveDirection.RIGHT == "right"
        assert MoveDirection.FORWARD == "forward"
        assert MoveDirection.BACK == "back"

    def test_move_direction_enum_membership(self):
        """移動方向Enum所属テスト"""
        valid_directions = ["up", "down", "left", "right", "forward", "back"]
        for direction in valid_directions:
            assert direction in MoveDirection.__members__.values()

    def test_rotate_direction_enum_values(self):
        """回転方向Enum値テスト"""
        assert RotateDirection.CLOCKWISE == "clockwise"
        assert RotateDirection.COUNTER_CLOCKWISE == "counter_clockwise"

    def test_flip_direction_enum_values(self):
        """宙返り方向Enum値テスト"""
        assert FlipDirection.LEFT == "left"
        assert FlipDirection.RIGHT == "right"
        assert FlipDirection.FORWARD == "forward"
        assert FlipDirection.BACK == "back"

    def test_camera_resolution_enum_values(self):
        """カメラ解像度Enum値テスト"""
        assert CameraResolution.HIGH == "high"
        assert CameraResolution.LOW == "low"

    def test_camera_fps_enum_values(self):
        """カメラFPS Enum値テスト"""
        assert CameraFPS.HIGH == "high"
        assert CameraFPS.MIDDLE == "middle"
        assert CameraFPS.LOW == "low"

    def test_tracking_mode_enum_values(self):
        """追跡モードEnum値テスト"""
        assert TrackingMode.CENTER == "center"
        assert TrackingMode.FOLLOW == "follow"

    @pytest.mark.parametrize("enum_class,expected_count", [
        (MoveDirection, 6),
        (RotateDirection, 2),
        (FlipDirection, 4),
        (CameraResolution, 2),
        (CameraFPS, 3),
        (TrackingMode, 2),
    ])
    def test_enum_member_counts(self, enum_class, expected_count):
        """Enumメンバー数テスト"""
        assert len(enum_class.__members__) == expected_count


class TestMoveRequest:
    """MoveRequestモデルテスト"""

    def test_move_request_valid_data(self):
        """MoveRequest有効データテスト"""
        request = MoveRequest(direction="forward", distance=100)
        assert request.direction == MoveDirection.FORWARD
        assert request.distance == 100

    def test_move_request_boundary_values_valid(self):
        """MoveRequest境界値有効テスト"""
        # 最小値
        request_min = MoveRequest(direction="up", distance=20)
        assert request_min.distance == 20
        
        # 最大値
        request_max = MoveRequest(direction="down", distance=500)
        assert request_max.distance == 500

    @pytest.mark.parametrize("distance", [19, 501, 0, -10, 1000])
    def test_move_request_invalid_distance(self, distance):
        """MoveRequest無効距離テスト"""
        with pytest.raises(ValidationError):
            MoveRequest(direction="forward", distance=distance)

    @pytest.mark.parametrize("direction", ["invalid", "", "UP", "FORWARD", "diagonal"])
    def test_move_request_invalid_direction(self, direction):
        """MoveRequest無効方向テスト"""
        with pytest.raises(ValidationError):
            MoveRequest(direction=direction, distance=100)

    def test_move_request_missing_fields(self):
        """MoveRequest必須フィールド欠如テスト"""
        with pytest.raises(ValidationError):
            MoveRequest(direction="forward")  # distance missing
        
        with pytest.raises(ValidationError):
            MoveRequest(distance=100)  # direction missing

    def test_move_request_type_validation(self):
        """MoveRequestタイプバリデーションテスト"""
        with pytest.raises(ValidationError):
            MoveRequest(direction="forward", distance="100")  # string instead of int
        
        with pytest.raises(ValidationError):
            MoveRequest(direction=123, distance=100)  # int instead of string

    @pytest.mark.parametrize("direction,distance", [
        ("up", 20), ("up", 260), ("up", 500),
        ("down", 20), ("down", 260), ("down", 500),
        ("left", 50), ("right", 150), ("forward", 300), ("back", 450)
    ])
    def test_move_request_comprehensive_valid_combinations(self, direction, distance):
        """MoveRequest包括的有効組み合わせテスト"""
        request = MoveRequest(direction=direction, distance=distance)
        assert request.direction.value == direction
        assert request.distance == distance


class TestRotateRequest:
    """RotateRequestモデルテスト"""

    def test_rotate_request_valid_data(self):
        """RotateRequest有効データテスト"""
        request = RotateRequest(direction="clockwise", angle=90)
        assert request.direction == RotateDirection.CLOCKWISE
        assert request.angle == 90

    def test_rotate_request_boundary_values_valid(self):
        """RotateRequest境界値有効テスト"""
        # 最小値
        request_min = RotateRequest(direction="clockwise", angle=1)
        assert request_min.angle == 1
        
        # 最大値
        request_max = RotateRequest(direction="counter_clockwise", angle=360)
        assert request_max.angle == 360

    @pytest.mark.parametrize("angle", [0, 361, -10, 720])
    def test_rotate_request_invalid_angle(self, angle):
        """RotateRequest無効角度テスト"""
        with pytest.raises(ValidationError):
            RotateRequest(direction="clockwise", angle=angle)

    @pytest.mark.parametrize("direction", ["invalid", "left", "right", "CW", "CCW"])
    def test_rotate_request_invalid_direction(self, direction):
        """RotateRequest無効方向テスト"""
        with pytest.raises(ValidationError):
            RotateRequest(direction=direction, angle=90)

    @pytest.mark.parametrize("direction,angle", [
        ("clockwise", 1), ("clockwise", 180), ("clockwise", 360),
        ("counter_clockwise", 1), ("counter_clockwise", 180), ("counter_clockwise", 360),
        ("clockwise", 45), ("counter_clockwise", 90), ("clockwise", 270)
    ])
    def test_rotate_request_comprehensive_valid_combinations(self, direction, angle):
        """RotateRequest包括的有効組み合わせテスト"""
        request = RotateRequest(direction=direction, angle=angle)
        assert request.direction.value == direction
        assert request.angle == angle


class TestFlipRequest:
    """FlipRequestモデルテスト"""

    def test_flip_request_valid_data(self):
        """FlipRequest有効データテスト"""
        request = FlipRequest(direction="forward")
        assert request.direction == FlipDirection.FORWARD

    @pytest.mark.parametrize("direction", ["left", "right", "forward", "back"])
    def test_flip_request_all_valid_directions(self, direction):
        """FlipRequest全有効方向テスト"""
        request = FlipRequest(direction=direction)
        assert request.direction.value == direction

    @pytest.mark.parametrize("direction", ["invalid", "up", "down", "LEFT", "diagonal"])
    def test_flip_request_invalid_direction(self, direction):
        """FlipRequest無効方向テスト"""
        with pytest.raises(ValidationError):
            FlipRequest(direction=direction)

    def test_flip_request_missing_direction(self):
        """FlipRequest方向欠如テスト"""
        with pytest.raises(ValidationError):
            FlipRequest()


class TestGoXYZRequest:
    """GoXYZRequestモデルテスト"""

    def test_go_xyz_request_valid_data(self):
        """GoXYZRequest有効データテスト"""
        request = GoXYZRequest(x=100, y=-50, z=200, speed=50)
        assert request.x == 100
        assert request.y == -50
        assert request.z == 200
        assert request.speed == 50

    def test_go_xyz_request_boundary_values_valid(self):
        """GoXYZRequest境界値有効テスト"""
        # 座標最小値
        request_min = GoXYZRequest(x=-500, y=-500, z=-500, speed=10)
        assert request_min.x == -500
        assert request_min.y == -500
        assert request_min.z == -500
        assert request_min.speed == 10
        
        # 座標最大値
        request_max = GoXYZRequest(x=500, y=500, z=500, speed=100)
        assert request_max.x == 500
        assert request_max.y == 500
        assert request_max.z == 500
        assert request_max.speed == 100

    @pytest.mark.parametrize("x,y,z,speed,should_fail", [
        (-501, 0, 0, 50, True),    # X下限未満
        (501, 0, 0, 50, True),     # X上限超過
        (0, -501, 0, 50, True),    # Y下限未満
        (0, 501, 0, 50, True),     # Y上限超過
        (0, 0, -501, 50, True),    # Z下限未満
        (0, 0, 501, 50, True),     # Z上限超過
        (0, 0, 0, 9, True),        # 速度下限未満
        (0, 0, 0, 101, True),      # 速度上限超過
        (-500, -500, -500, 10, False),  # 有効最小値
        (500, 500, 500, 100, False),    # 有効最大値
        (0, 0, 0, 55, False),           # 有効中央値
    ])
    def test_go_xyz_request_boundary_validation(self, x, y, z, speed, should_fail):
        """GoXYZRequest境界値バリデーションテスト"""
        if should_fail:
            with pytest.raises(ValidationError):
                GoXYZRequest(x=x, y=y, z=z, speed=speed)
        else:
            request = GoXYZRequest(x=x, y=y, z=z, speed=speed)
            assert request.x == x
            assert request.y == y
            assert request.z == z
            assert request.speed == speed

    def test_go_xyz_request_type_validation(self):
        """GoXYZRequestタイプバリデーションテスト"""
        with pytest.raises(ValidationError):
            GoXYZRequest(x="100", y=50, z=200, speed=50)  # x is string
        
        with pytest.raises(ValidationError):
            GoXYZRequest(x=100, y=50.5, z=200, speed=50)  # y is float


class TestCurveXYZRequest:
    """CurveXYZRequestモデルテスト"""

    def test_curve_xyz_request_valid_data(self):
        """CurveXYZRequest有効データテスト"""
        request = CurveXYZRequest(x1=50, y1=0, z1=100, x2=150, y2=50, z2=200, speed=30)
        assert request.x1 == 50
        assert request.y1 == 0
        assert request.z1 == 100
        assert request.x2 == 150
        assert request.y2 == 50
        assert request.z2 == 200
        assert request.speed == 30

    def test_curve_xyz_request_speed_boundary(self):
        """CurveXYZRequest速度境界値テスト"""
        # 最小速度
        request_min = CurveXYZRequest(x1=0, y1=0, z1=0, x2=100, y2=100, z2=100, speed=10)
        assert request_min.speed == 10
        
        # 最大速度
        request_max = CurveXYZRequest(x1=0, y1=0, z1=0, x2=100, y2=100, z2=100, speed=60)
        assert request_max.speed == 60

    @pytest.mark.parametrize("speed", [9, 61, 0, -10, 100])
    def test_curve_xyz_request_invalid_speed(self, speed):
        """CurveXYZRequest無効速度テスト"""
        with pytest.raises(ValidationError):
            CurveXYZRequest(x1=0, y1=0, z1=0, x2=100, y2=100, z2=100, speed=speed)


class TestRCControlRequest:
    """RCControlRequestモデルテスト"""

    def test_rc_control_request_valid_data(self):
        """RCControlRequest有効データテスト"""
        request = RCControlRequest(
            left_right_velocity=50,
            forward_backward_velocity=-30,
            up_down_velocity=20,
            yaw_velocity=10
        )
        assert request.left_right_velocity == 50
        assert request.forward_backward_velocity == -30
        assert request.up_down_velocity == 20
        assert request.yaw_velocity == 10

    def test_rc_control_request_boundary_values(self):
        """RCControlRequest境界値テスト"""
        # 最小値
        request_min = RCControlRequest(
            left_right_velocity=-100,
            forward_backward_velocity=-100,
            up_down_velocity=-100,
            yaw_velocity=-100
        )
        assert request_min.left_right_velocity == -100
        
        # 最大値
        request_max = RCControlRequest(
            left_right_velocity=100,
            forward_backward_velocity=100,
            up_down_velocity=100,
            yaw_velocity=100
        )
        assert request_max.left_right_velocity == 100

    @pytest.mark.parametrize("lr,fb,ud,yaw,should_fail", [
        (-101, 0, 0, 0, True),     # LR下限未満
        (101, 0, 0, 0, True),      # LR上限超過
        (0, -101, 0, 0, True),     # FB下限未満
        (0, 101, 0, 0, True),      # FB上限超過
        (0, 0, -101, 0, True),     # UD下限未満
        (0, 0, 101, 0, True),      # UD上限超過
        (0, 0, 0, -101, True),     # Yaw下限未満
        (0, 0, 0, 101, True),      # Yaw上限超過
        (-100, -100, -100, -100, False),  # 有効最小値
        (100, 100, 100, 100, False),      # 有効最大値
        (0, 0, 0, 0, False),              # 有効中央値
    ])
    def test_rc_control_request_boundary_validation(self, lr, fb, ud, yaw, should_fail):
        """RCControlRequest境界値バリデーションテスト"""
        if should_fail:
            with pytest.raises(ValidationError):
                RCControlRequest(
                    left_right_velocity=lr,
                    forward_backward_velocity=fb,
                    up_down_velocity=ud,
                    yaw_velocity=yaw
                )
        else:
            request = RCControlRequest(
                left_right_velocity=lr,
                forward_backward_velocity=fb,
                up_down_velocity=ud,
                yaw_velocity=yaw
            )
            assert request.left_right_velocity == lr


class TestCameraSettingsRequest:
    """CameraSettingsRequestモデルテスト"""

    def test_camera_settings_request_valid_data(self):
        """CameraSettingsRequest有効データテスト"""
        request = CameraSettingsRequest(
            resolution="high",
            fps="middle",
            bitrate=3
        )
        assert request.resolution == CameraResolution.HIGH
        assert request.fps == CameraFPS.MIDDLE
        assert request.bitrate == 3

    def test_camera_settings_request_optional_fields(self):
        """CameraSettingsRequestオプションフィールドテスト"""
        # 解像度のみ
        request1 = CameraSettingsRequest(resolution="low")
        assert request1.resolution == CameraResolution.LOW
        assert request1.fps is None
        assert request1.bitrate is None
        
        # FPSのみ
        request2 = CameraSettingsRequest(fps="high")
        assert request2.resolution is None
        assert request2.fps == CameraFPS.HIGH
        
        # ビットレートのみ
        request3 = CameraSettingsRequest(bitrate=5)
        assert request3.bitrate == 5

    def test_camera_settings_request_empty(self):
        """CameraSettingsRequest空データテスト"""
        request = CameraSettingsRequest()
        assert request.resolution is None
        assert request.fps is None
        assert request.bitrate is None

    @pytest.mark.parametrize("bitrate", [0, 6, -1, 10])
    def test_camera_settings_request_invalid_bitrate(self, bitrate):
        """CameraSettingsRequest無効ビットレートテスト"""
        with pytest.raises(ValidationError):
            CameraSettingsRequest(bitrate=bitrate)

    @pytest.mark.parametrize("bitrate", [1, 2, 3, 4, 5])
    def test_camera_settings_request_valid_bitrate_range(self, bitrate):
        """CameraSettingsRequest有効ビットレート範囲テスト"""
        request = CameraSettingsRequest(bitrate=bitrate)
        assert request.bitrate == bitrate


class TestWiFiRequest:
    """WiFiRequestモデルテスト"""

    def test_wifi_request_valid_data(self):
        """WiFiRequest有効データテスト"""
        request = WiFiRequest(ssid="TestNetwork", password="TestPassword123")
        assert request.ssid == "TestNetwork"
        assert request.password == "TestPassword123"

    def test_wifi_request_length_boundaries(self):
        """WiFiRequest長さ境界値テスト"""
        # SSID最大長
        long_ssid = "a" * 32
        request1 = WiFiRequest(ssid=long_ssid, password="valid")
        assert request1.ssid == long_ssid
        
        # パスワード最大長
        long_password = "b" * 64
        request2 = WiFiRequest(ssid="valid", password=long_password)
        assert request2.password == long_password

    @pytest.mark.parametrize("ssid,password,should_fail", [
        ("a" * 33, "valid", True),       # SSID長すぎ
        ("valid", "a" * 65, True),       # パスワード長すぎ
        ("", "valid", False),            # 空SSID（許可される可能性）
        ("valid", "", False),            # 空パスワード（許可される可能性）
        ("短い", "短いパス", False),        # 短い値
    ])
    def test_wifi_request_length_validation(self, ssid, password, should_fail):
        """WiFiRequest長さバリデーションテスト"""
        if should_fail:
            with pytest.raises(ValidationError):
                WiFiRequest(ssid=ssid, password=password)
        else:
            request = WiFiRequest(ssid=ssid, password=password)
            assert request.ssid == ssid
            assert request.password == password


class TestCommandRequest:
    """CommandRequestモデルテスト"""

    def test_command_request_valid_data(self):
        """CommandRequest有効データテスト"""
        request = CommandRequest(command="battery?", timeout=10, expect_response=True)
        assert request.command == "battery?"
        assert request.timeout == 10
        assert request.expect_response is True

    def test_command_request_default_values(self):
        """CommandRequestデフォルト値テスト"""
        request = CommandRequest(command="takeoff")
        assert request.command == "takeoff"
        assert request.timeout == 7  # デフォルト値
        assert request.expect_response is True  # デフォルト値

    @pytest.mark.parametrize("timeout", [0, 31, -5])
    def test_command_request_invalid_timeout(self, timeout):
        """CommandRequest無効タイムアウトテスト"""
        with pytest.raises(ValidationError):
            CommandRequest(command="test", timeout=timeout)

    @pytest.mark.parametrize("timeout", [1, 15, 30])
    def test_command_request_valid_timeout_range(self, timeout):
        """CommandRequest有効タイムアウト範囲テスト"""
        request = CommandRequest(command="test", timeout=timeout)
        assert request.timeout == timeout


class TestSpeedRequest:
    """SpeedRequestモデルテスト"""

    def test_speed_request_valid_data(self):
        """SpeedRequest有効データテスト"""
        request = SpeedRequest(speed=5.0)
        assert request.speed == 5.0

    def test_speed_request_boundary_values(self):
        """SpeedRequest境界値テスト"""
        # 最小値
        request_min = SpeedRequest(speed=1.0)
        assert request_min.speed == 1.0
        
        # 最大値
        request_max = SpeedRequest(speed=15.0)
        assert request_max.speed == 15.0

    @pytest.mark.parametrize("speed", [0.9, 15.1, 0, -1, 20])
    def test_speed_request_invalid_speed(self, speed):
        """SpeedRequest無効速度テスト"""
        with pytest.raises(ValidationError):
            SpeedRequest(speed=speed)


class TestMissionPadRequests:
    """ミッションパッドリクエストテスト"""

    def test_mission_pad_detection_direction_request_valid(self):
        """ミッションパッド検出方向リクエスト有効テスト"""
        for direction in [0, 1, 2]:
            request = MissionPadDetectionDirectionRequest(direction=direction)
            assert request.direction == direction

    @pytest.mark.parametrize("direction", [-1, 3, 10])
    def test_mission_pad_detection_direction_request_invalid(self, direction):
        """ミッションパッド検出方向リクエスト無効テスト"""
        with pytest.raises(ValidationError):
            MissionPadDetectionDirectionRequest(direction=direction)

    def test_mission_pad_go_xyz_request_valid(self):
        """ミッションパッドGoXYZリクエスト有効テスト"""
        request = MissionPadGoXYZRequest(x=100, y=-50, z=200, speed=50, mission_pad_id=3)
        assert request.x == 100
        assert request.y == -50
        assert request.z == 200
        assert request.speed == 50
        assert request.mission_pad_id == 3

    @pytest.mark.parametrize("mission_pad_id", [0, 9, -1, 10])
    def test_mission_pad_go_xyz_request_invalid_id(self, mission_pad_id):
        """ミッションパッドGoXYZリクエスト無効IDテスト"""
        with pytest.raises(ValidationError):
            MissionPadGoXYZRequest(x=0, y=0, z=0, speed=50, mission_pad_id=mission_pad_id)

    @pytest.mark.parametrize("mission_pad_id", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_mission_pad_go_xyz_request_valid_id_range(self, mission_pad_id):
        """ミッションパッドGoXYZリクエスト有効ID範囲テスト"""
        request = MissionPadGoXYZRequest(x=0, y=0, z=0, speed=50, mission_pad_id=mission_pad_id)
        assert request.mission_pad_id == mission_pad_id


class TestTrackingStartRequest:
    """TrackingStartRequestモデルテスト"""

    def test_tracking_start_request_valid_data(self):
        """TrackingStartRequest有効データテスト"""
        request = TrackingStartRequest(target_object="person", tracking_mode="follow")
        assert request.target_object == "person"
        assert request.tracking_mode == TrackingMode.FOLLOW

    def test_tracking_start_request_default_mode(self):
        """TrackingStartRequestデフォルトモードテスト"""
        request = TrackingStartRequest(target_object="car")
        assert request.target_object == "car"
        assert request.tracking_mode == TrackingMode.CENTER  # デフォルト値

    @pytest.mark.parametrize("tracking_mode", ["center", "follow"])
    def test_tracking_start_request_valid_modes(self, tracking_mode):
        """TrackingStartRequest有効モードテスト"""
        request = TrackingStartRequest(target_object="object", tracking_mode=tracking_mode)
        assert request.tracking_mode.value == tracking_mode

    @pytest.mark.parametrize("tracking_mode", ["invalid", "track", "CENTER"])
    def test_tracking_start_request_invalid_mode(self, tracking_mode):
        """TrackingStartRequest無効モードテスト"""
        with pytest.raises(ValidationError):
            TrackingStartRequest(target_object="object", tracking_mode=tracking_mode)


class TestModelTrainRequest:
    """ModelTrainRequestモデルテスト"""

    def test_model_train_request_valid_data(self):
        """ModelTrainRequest有効データテスト"""
        request = ModelTrainRequest(object_name="new_object")
        assert request.object_name == "new_object"

    def test_model_train_request_empty_name(self):
        """ModelTrainRequest空名前テスト"""
        # 空文字列も有効とする場合
        request = ModelTrainRequest(object_name="")
        assert request.object_name == ""


class TestResponseEnums:
    """レスポンスEnum型テスト"""

    def test_error_code_enum_values(self):
        """エラーコードEnum値テスト"""
        assert ErrorCode.DRONE_NOT_CONNECTED == "DRONE_NOT_CONNECTED"
        assert ErrorCode.INVALID_PARAMETER == "INVALID_PARAMETER"
        assert ErrorCode.COMMAND_FAILED == "COMMAND_FAILED"
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"

    def test_error_code_enum_completeness(self):
        """エラーコードEnum完全性テスト"""
        expected_codes = [
            "DRONE_NOT_CONNECTED", "DRONE_CONNECTION_FAILED", "INVALID_PARAMETER",
            "COMMAND_FAILED", "COMMAND_TIMEOUT", "NOT_FLYING", "ALREADY_FLYING",
            "STREAMING_NOT_STARTED", "STREAMING_ALREADY_STARTED", "MODEL_NOT_FOUND",
            "TRAINING_IN_PROGRESS", "FILE_TOO_LARGE", "UNSUPPORTED_FORMAT", "INTERNAL_ERROR"
        ]
        
        for code in expected_codes:
            assert code in ErrorCode.__members__.values()


class TestStatusResponse:
    """StatusResponseモデルテスト"""

    def test_status_response_valid_data(self):
        """StatusResponse有効データテスト"""
        response = StatusResponse(success=True, message="操作が成功しました")
        assert response.success is True
        assert response.message == "操作が成功しました"

    def test_status_response_failure_case(self):
        """StatusResponse失敗ケーステスト"""
        response = StatusResponse(success=False, message="操作が失敗しました")
        assert response.success is False
        assert response.message == "操作が失敗しました"

    def test_status_response_type_validation(self):
        """StatusResponseタイプバリデーションテスト"""
        with pytest.raises(ValidationError):
            StatusResponse(success="true", message="test")  # string instead of bool


class TestErrorResponse:
    """ErrorResponseモデルテスト"""

    def test_error_response_valid_data(self):
        """ErrorResponse有効データテスト"""
        response = ErrorResponse(
            error="エラーが発生しました",
            code=ErrorCode.INTERNAL_ERROR,
            details={"trace": "stack trace here"}
        )
        assert response.error == "エラーが発生しました"
        assert response.code == ErrorCode.INTERNAL_ERROR
        assert response.details["trace"] == "stack trace here"

    def test_error_response_without_details(self):
        """ErrorResponse詳細なしテスト"""
        response = ErrorResponse(
            error="簡単なエラー",
            code=ErrorCode.COMMAND_FAILED
        )
        assert response.error == "簡単なエラー"
        assert response.code == ErrorCode.COMMAND_FAILED
        assert response.details is None


class TestSensorDataModels:
    """センサーデータモデルテスト"""

    def test_acceleration_data_valid(self):
        """AccelerationData有効データテスト"""
        data = AccelerationData(x=0.1, y=-0.05, z=0.98)
        assert data.x == 0.1
        assert data.y == -0.05
        assert data.z == 0.98

    def test_velocity_data_valid(self):
        """VelocityData有効データテスト"""
        data = VelocityData(x=10, y=-5, z=2)
        assert data.x == 10
        assert data.y == -5
        assert data.z == 2

    def test_attitude_data_valid(self):
        """AttitudeData有効データテスト"""
        data = AttitudeData(pitch=5, roll=-10, yaw=90)
        assert data.pitch == 5
        assert data.roll == -10
        assert data.yaw == 90

    @pytest.mark.parametrize("pitch,roll,yaw,should_fail", [
        (-181, 0, 0, True),      # pitch下限未満
        (181, 0, 0, True),       # pitch上限超過
        (0, -181, 0, True),      # roll下限未満
        (0, 181, 0, True),       # roll上限超過
        (0, 0, -181, True),      # yaw下限未満
        (0, 0, 181, True),       # yaw上限超過
        (-180, -180, -180, False),  # 有効最小値
        (180, 180, 180, False),     # 有効最大値
        (0, 0, 0, False),           # 有効中央値
    ])
    def test_attitude_data_boundary_validation(self, pitch, roll, yaw, should_fail):
        """AttitudeData境界値バリデーションテスト"""
        if should_fail:
            with pytest.raises(ValidationError):
                AttitudeData(pitch=pitch, roll=roll, yaw=yaw)
        else:
            data = AttitudeData(pitch=pitch, roll=roll, yaw=yaw)
            assert data.pitch == pitch
            assert data.roll == roll
            assert data.yaw == yaw


class TestDroneStatus:
    """DroneStatusモデルテスト"""

    def test_drone_status_valid_data(self):
        """DroneStatus有効データテスト"""
        acceleration = AccelerationData(x=0.1, y=0.2, z=0.98)
        velocity = VelocityData(x=10, y=-5, z=2)
        attitude = AttitudeData(pitch=5, roll=-2, yaw=90)
        
        status = DroneStatus(
            connected=True,
            battery=85,
            height=150,
            temperature=25,
            flight_time=120,
            speed=50.5,
            barometer=1013.25,
            distance_tof=500,
            acceleration=acceleration,
            velocity=velocity,
            attitude=attitude
        )
        
        assert status.connected is True
        assert status.battery == 85
        assert status.height == 150
        assert status.temperature == 25
        assert status.flight_time == 120
        assert status.speed == 50.5
        assert status.barometer == 1013.25
        assert status.distance_tof == 500
        assert status.acceleration == acceleration
        assert status.velocity == velocity
        assert status.attitude == attitude

    @pytest.mark.parametrize("battery", [-1, 101])
    def test_drone_status_invalid_battery(self, battery):
        """DroneStatus無効バッテリーテスト"""
        acceleration = AccelerationData(x=0, y=0, z=1)
        velocity = VelocityData(x=0, y=0, z=0)
        attitude = AttitudeData(pitch=0, roll=0, yaw=0)
        
        with pytest.raises(ValidationError):
            DroneStatus(
                connected=True, battery=battery, height=100, temperature=20,
                flight_time=60, speed=10, barometer=1000, distance_tof=100,
                acceleration=acceleration, velocity=velocity, attitude=attitude
            )

    @pytest.mark.parametrize("height", [-1, 3001])
    def test_drone_status_invalid_height(self, height):
        """DroneStatus無効高度テスト"""
        acceleration = AccelerationData(x=0, y=0, z=1)
        velocity = VelocityData(x=0, y=0, z=0)
        attitude = AttitudeData(pitch=0, roll=0, yaw=0)
        
        with pytest.raises(ValidationError):
            DroneStatus(
                connected=True, battery=50, height=height, temperature=20,
                flight_time=60, speed=10, barometer=1000, distance_tof=100,
                acceleration=acceleration, velocity=velocity, attitude=attitude
            )

    @pytest.mark.parametrize("temperature", [-1, 91])
    def test_drone_status_invalid_temperature(self, temperature):
        """DroneStatus無効温度テスト"""
        acceleration = AccelerationData(x=0, y=0, z=1)
        velocity = VelocityData(x=0, y=0, z=0)
        attitude = AttitudeData(pitch=0, roll=0, yaw=0)
        
        with pytest.raises(ValidationError):
            DroneStatus(
                connected=True, battery=50, height=100, temperature=temperature,
                flight_time=60, speed=10, barometer=1000, distance_tof=100,
                acceleration=acceleration, velocity=velocity, attitude=attitude
            )


class TestSimpleResponseModels:
    """シンプルレスポンスモデルテスト"""

    def test_battery_response_valid(self):
        """BatteryResponse有効テスト"""
        response = BatteryResponse(battery=75)
        assert response.battery == 75

    @pytest.mark.parametrize("battery", [0, 50, 100])
    def test_battery_response_boundary_values(self, battery):
        """BatteryResponse境界値テスト"""
        response = BatteryResponse(battery=battery)
        assert response.battery == battery

    @pytest.mark.parametrize("battery", [-1, 101])
    def test_battery_response_invalid_values(self, battery):
        """BatteryResponse無効値テスト"""
        with pytest.raises(ValidationError):
            BatteryResponse(battery=battery)

    def test_height_response_valid(self):
        """HeightResponse有効テスト"""
        response = HeightResponse(height=200)
        assert response.height == 200

    def test_temperature_response_valid(self):
        """TemperatureResponse有効テスト"""
        response = TemperatureResponse(temperature=30)
        assert response.temperature == 30

    def test_flight_time_response_valid(self):
        """FlightTimeResponse有効テスト"""
        response = FlightTimeResponse(flight_time=300)
        assert response.flight_time == 300

    def test_barometer_response_valid(self):
        """BarometerResponse有効テスト"""
        response = BarometerResponse(barometer=1013.25)
        assert response.barometer == 1013.25

    def test_distance_tof_response_valid(self):
        """DistanceToFResponse有効テスト"""
        response = DistanceToFResponse(distance_tof=500)
        assert response.distance_tof == 500


class TestTrackingModels:
    """追跡関連モデルテスト"""

    def test_tracking_position_valid(self):
        """TrackingPosition有効テスト"""
        position = TrackingPosition(x=320, y=240, width=100, height=80)
        assert position.x == 320
        assert position.y == 240
        assert position.width == 100
        assert position.height == 80

    def test_tracking_status_response_with_position(self):
        """TrackingStatusResponse位置ありテスト"""
        position = TrackingPosition(x=320, y=240, width=100, height=80)
        response = TrackingStatusResponse(
            is_tracking=True,
            target_object="person",
            target_detected=True,
            target_position=position
        )
        assert response.is_tracking is True
        assert response.target_object == "person"
        assert response.target_detected is True
        assert response.target_position == position

    def test_tracking_status_response_without_position(self):
        """TrackingStatusResponse位置なしテスト"""
        response = TrackingStatusResponse(
            is_tracking=False,
            target_object="",
            target_detected=False,
            target_position=None
        )
        assert response.is_tracking is False
        assert response.target_object == ""
        assert response.target_detected is False
        assert response.target_position is None


class TestModelManagementModels:
    """モデル管理関連モデルテスト"""

    def test_model_info_valid(self):
        """ModelInfo有効テスト"""
        created_time = datetime.now()
        model = ModelInfo(
            name="test_model",
            created_at=created_time,
            accuracy=0.85
        )
        assert model.name == "test_model"
        assert model.created_at == created_time
        assert model.accuracy == 0.85

    def test_model_list_response_valid(self):
        """ModelListResponse有効テスト"""
        model1 = ModelInfo(name="model1", created_at=datetime.now(), accuracy=0.9)
        model2 = ModelInfo(name="model2", created_at=datetime.now(), accuracy=0.8)
        
        response = ModelListResponse(models=[model1, model2])
        assert len(response.models) == 2
        assert response.models[0] == model1
        assert response.models[1] == model2

    def test_model_list_response_empty(self):
        """ModelListResponse空リストテスト"""
        response = ModelListResponse(models=[])
        assert len(response.models) == 0

    def test_model_train_response_valid(self):
        """ModelTrainResponse有効テスト"""
        task_id = "12345-abcde-67890"
        response = ModelTrainResponse(task_id=task_id)
        assert response.task_id == task_id


class TestComplexResponseModels:
    """複合レスポンスモデルテスト"""

    def test_command_response_valid(self):
        """CommandResponse有効テスト"""
        response = CommandResponse(success=True, response="ok")
        assert response.success is True
        assert response.response == "ok"

    def test_mission_pad_status_response_valid(self):
        """MissionPadStatusResponse有効テスト"""
        response = MissionPadStatusResponse(
            mission_pad_id=3,
            distance_x=50,
            distance_y=-20,
            distance_z=100
        )
        assert response.mission_pad_id == 3
        assert response.distance_x == 50
        assert response.distance_y == -20
        assert response.distance_z == 100

    def test_mission_pad_status_response_no_detection(self):
        """MissionPadStatusResponse検出なしテスト"""
        response = MissionPadStatusResponse(
            mission_pad_id=-1,  # 検出なし
            distance_x=0,
            distance_y=0,
            distance_z=0
        )
        assert response.mission_pad_id == -1


class TestNestedModelValidation:
    """ネストモデルバリデーションテスト"""

    def test_acceleration_response_nested_validation(self):
        """AccelerationResponseネストバリデーションテスト"""
        acceleration = AccelerationData(x=0.1, y=0.2, z=0.98)
        response = AccelerationResponse(acceleration=acceleration)
        assert response.acceleration == acceleration

    def test_velocity_response_nested_validation(self):
        """VelocityResponseネストバリデーションテスト"""
        velocity = VelocityData(x=10, y=-5, z=2)
        response = VelocityResponse(velocity=velocity)
        assert response.velocity == velocity

    def test_attitude_response_nested_validation(self):
        """AttitudeResponseネストバリデーションテスト"""
        attitude = AttitudeData(pitch=5, roll=-2, yaw=90)
        response = AttitudeResponse(attitude=attitude)
        assert response.attitude == attitude

    def test_nested_model_validation_failure(self):
        """ネストモデルバリデーション失敗テスト"""
        with pytest.raises(ValidationError):
            # 無効なAttitudeDataでAttitudeResponseを作成
            invalid_attitude = {"pitch": 200, "roll": 0, "yaw": 0}  # pitch範囲外
            AttitudeResponse(attitude=invalid_attitude)


class TestModelFieldConstraints:
    """モデルフィールド制約テスト"""

    def test_field_constraints_validation(self):
        """フィールド制約バリデーションテスト"""
        # Pydanticのge, le制約のテスト
        
        # MoveRequest距離制約
        with pytest.raises(ValidationError):
            MoveRequest(direction="forward", distance=19)  # ge=20
        
        with pytest.raises(ValidationError):
            MoveRequest(direction="forward", distance=501)  # le=500
        
        # SpeedRequest速度制約
        with pytest.raises(ValidationError):
            SpeedRequest(speed=0.9)  # ge=1.0
        
        with pytest.raises(ValidationError):
            SpeedRequest(speed=15.1)  # le=15.0

    def test_field_description_metadata(self):
        """フィールド説明メタデータテスト"""
        # Fieldのdescriptionが設定されていることを確認
        move_request_fields = MoveRequest.model_fields
        assert "description" in str(move_request_fields["direction"])
        assert "description" in str(move_request_fields["distance"])

    def test_field_type_coercion(self):
        """フィールド型強制変換テスト"""
        # Pydanticの型変換機能のテスト
        request = MoveRequest(direction="forward", distance=100.0)  # float -> int
        assert isinstance(request.distance, int)
        assert request.distance == 100