"""
pytest設定ファイル
共通フィクスチャとテスト設定
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.fixtures.drone_factory import create_test_drone, DroneTestHelper
from tests.stubs.drone_stub import TelloStub


@pytest.fixture
def drone():
    """基本ドローンフィクスチャ"""
    drone = create_test_drone()
    yield drone
    DroneTestHelper.reset_drone_state(drone)


@pytest.fixture
def connected_drone():
    """接続済みドローンフィクスチャ"""
    drone = create_test_drone()
    DroneTestHelper.setup_connected_state(drone)
    yield drone
    DroneTestHelper.reset_drone_state(drone)


@pytest.fixture
def flying_drone():
    """飛行中ドローンフィクスチャ"""
    drone = create_test_drone()
    DroneTestHelper.setup_flying_state(drone)
    yield drone
    DroneTestHelper.reset_drone_state(drone)


@pytest.fixture
def error_drone():
    """エラー発生ドローンフィクスチャ"""
    drone = create_test_drone()
    DroneTestHelper.setup_command_error(drone)
    yield drone
    DroneTestHelper.reset_drone_state(drone)


@pytest.fixture
def connection_error_drone():
    """接続エラードローンフィクスチャ"""
    drone = create_test_drone()
    DroneTestHelper.setup_connection_error(drone)
    yield drone
    DroneTestHelper.reset_drone_state(drone)


@pytest.fixture
def timeout_drone():
    """タイムアウトドローンフィクスチャ"""
    drone = create_test_drone()
    DroneTestHelper.setup_timeout_error(drone)
    yield drone
    DroneTestHelper.reset_drone_state(drone)


# テスト用データ
@pytest.fixture
def valid_move_data():
    """有効な移動データ"""
    return {
        "direction": "forward",
        "distance": 100
    }


@pytest.fixture
def boundary_move_data():
    """境界値移動データ"""
    return [
        {"direction": "up", "distance": 20},      # 最小値
        {"direction": "down", "distance": 500},   # 最大値
    ]


@pytest.fixture
def invalid_move_data():
    """無効な移動データ"""
    return [
        {"direction": "forward", "distance": 19},   # 最小値未満
        {"direction": "back", "distance": 501},     # 最大値超過
        {"direction": "invalid", "distance": 100},  # 無効な方向
        {"direction": "left", "distance": -50},     # 負の値
    ]


@pytest.fixture
def valid_rotate_data():
    """有効な回転データ"""
    return {
        "direction": "clockwise",
        "angle": 90
    }


@pytest.fixture
def boundary_rotate_data():
    """境界値回転データ"""
    return [
        {"direction": "clockwise", "angle": 1},       # 最小値
        {"direction": "counter_clockwise", "angle": 360}, # 最大値
    ]


@pytest.fixture
def invalid_rotate_data():
    """無効な回転データ"""
    return [
        {"direction": "clockwise", "angle": 0},           # 最小値未満
        {"direction": "clockwise", "angle": 361},         # 最大値超過
        {"direction": "invalid", "angle": 90},            # 無効な方向
        {"direction": "clockwise", "angle": -30},         # 負の値
    ]


@pytest.fixture
def valid_coordinate_data():
    """有効な座標データ"""
    return {
        "x": 100,
        "y": -50,
        "z": 200,
        "speed": 50
    }


@pytest.fixture
def boundary_coordinate_data():
    """境界値座標データ"""
    return [
        {"x": -500, "y": -500, "z": -500, "speed": 10},  # 最小値
        {"x": 500, "y": 500, "z": 500, "speed": 100},    # 最大値
    ]


@pytest.fixture
def invalid_coordinate_data():
    """無効な座標データ"""
    return [
        {"x": -501, "y": 0, "z": 0, "speed": 50},        # X最小値未満
        {"x": 501, "y": 0, "z": 0, "speed": 50},         # X最大値超過
        {"x": 0, "y": -501, "z": 0, "speed": 50},        # Y最小値未満
        {"x": 0, "y": 501, "z": 0, "speed": 50},         # Y最大値超過
        {"x": 0, "y": 0, "z": -501, "speed": 50},        # Z最小値未満
        {"x": 0, "y": 0, "z": 501, "speed": 50},         # Z最大値超過
        {"x": 0, "y": 0, "z": 0, "speed": 9},            # 速度最小値未満
        {"x": 0, "y": 0, "z": 0, "speed": 101},          # 速度最大値超過
    ]


@pytest.fixture
def valid_speed_data():
    """有効な速度データ"""
    return {"speed": 10.0}


@pytest.fixture
def boundary_speed_data():
    """境界値速度データ"""
    return [
        {"speed": 1.0},   # 最小値
        {"speed": 15.0},  # 最大値
    ]


@pytest.fixture
def invalid_speed_data():
    """無効な速度データ"""
    return [
        {"speed": 0.9},   # 最小値未満
        {"speed": 15.1},  # 最大値超過
        {"speed": -5.0},  # 負の値
    ]


@pytest.fixture
def valid_camera_settings():
    """有効なカメラ設定"""
    return {
        "resolution": "high",
        "fps": "middle",
        "bitrate": 3
    }


@pytest.fixture
def invalid_camera_settings():
    """無効なカメラ設定"""
    return [
        {"resolution": "invalid", "fps": "high", "bitrate": 3},
        {"resolution": "high", "fps": "invalid", "bitrate": 3},
        {"resolution": "high", "fps": "high", "bitrate": 0},
        {"resolution": "high", "fps": "high", "bitrate": 6},
    ]


@pytest.fixture
def valid_wifi_data():
    """有効なWiFiデータ"""
    return {
        "ssid": "TestNetwork",
        "password": "TestPassword123"
    }


@pytest.fixture
def invalid_wifi_data():
    """無効なWiFiデータ"""
    return [
        {"ssid": "a" * 33, "password": "valid"},       # SSID長すぎ
        {"ssid": "valid", "password": "a" * 65},       # パスワード長すぎ
        {"ssid": "", "password": "valid"},             # 空のSSID
        {"ssid": "valid", "password": ""},             # 空のパスワード
    ]


@pytest.fixture
def valid_mission_pad_data():
    """有効なミッションパッドデータ"""
    return {
        "x": 100,
        "y": -50,
        "z": 200,
        "speed": 50,
        "mission_pad_id": 1
    }


@pytest.fixture
def invalid_mission_pad_data():
    """無効なミッションパッドデータ"""
    return [
        {"x": 100, "y": -50, "z": 200, "speed": 50, "mission_pad_id": 0},   # ID最小値未満
        {"x": 100, "y": -50, "z": 200, "speed": 50, "mission_pad_id": 9},   # ID最大値超過
    ]