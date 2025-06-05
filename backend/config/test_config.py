"""
テスト設定ファイル
実機接続モードとスタブモードの切り替えを管理
"""

import os
import logging
from typing import Optional, Dict, Any


class TestConfig:
    """テスト設定クラス"""
    
    # 環境変数でモード切り替え (デフォルトはスタブモード)
    USE_REAL_DRONE = os.getenv("USE_REAL_DRONE", "false").lower() == "true"
    
    # Tello接続設定
    TELLO_IP = os.getenv("TELLO_IP", "192.168.10.1")
    TELLO_PORT = int(os.getenv("TELLO_PORT", "8889"))
    
    # テスト用タイムアウト設定
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "5"))
    COMMAND_TIMEOUT = int(os.getenv("COMMAND_TIMEOUT", "3"))
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", "10"))
    
    # FastAPIテストサーバー設定
    TEST_SERVER_HOST = os.getenv("TEST_SERVER_HOST", "127.0.0.1")
    TEST_SERVER_PORT = int(os.getenv("TEST_SERVER_PORT", "8000"))
    
    # ログレベル設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # テスト用データ設定
    MAX_TEST_IMAGES = int(os.getenv("MAX_TEST_IMAGES", "10"))
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "5"))
    
    @classmethod
    def is_real_drone_mode(cls) -> bool:
        """実機モードかどうかを判定"""
        return cls.USE_REAL_DRONE
    
    @classmethod
    def get_drone_connection_info(cls) -> tuple[str, int]:
        """ドローン接続情報を取得"""
        return cls.TELLO_IP, cls.TELLO_PORT
    
    @classmethod
    def get_test_server_url(cls) -> str:
        """テストサーバーURL取得"""
        return f"http://{cls.TEST_SERVER_HOST}:{cls.TEST_SERVER_PORT}"
    
    @classmethod
    def setup_logging(cls) -> None:
        """テスト用ログ設定"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @classmethod
    def get_boundary_test_data(cls) -> Dict[str, Any]:
        """境界値テスト用データ取得"""
        return {
            # 移動距離の境界値
            "move_distance": {
                "min": 20,
                "max": 500,
                "below_min": 19,
                "above_max": 501
            },
            # 回転角度の境界値
            "rotate_angle": {
                "min": 1,
                "max": 360,
                "below_min": 0,
                "above_max": 361
            },
            # 座標の境界値
            "coordinate": {
                "min": -500,
                "max": 500,
                "below_min": -501,
                "above_max": 501
            },
            # 速度の境界値（go_xyz）
            "speed_go_xyz": {
                "min": 10,
                "max": 100,
                "below_min": 9,
                "above_max": 101
            },
            # 速度の境界値（curve_xyz）
            "speed_curve_xyz": {
                "min": 10,
                "max": 60,
                "below_min": 9,
                "above_max": 61
            },
            # 飛行速度の境界値
            "flight_speed": {
                "min": 1.0,
                "max": 15.0,
                "below_min": 0.9,
                "above_max": 15.1
            },
            # RC制御速度の境界値
            "rc_velocity": {
                "min": -100,
                "max": 100,
                "below_min": -101,
                "above_max": 101
            },
            # ミッションパッドIDの境界値
            "mission_pad_id": {
                "min": 1,
                "max": 8,
                "below_min": 0,
                "above_max": 9
            },
            # カメラビットレートの境界値
            "camera_bitrate": {
                "min": 1,
                "max": 5,
                "below_min": 0,
                "above_max": 6
            },
            # コマンドタイムアウトの境界値
            "command_timeout": {
                "min": 1,
                "max": 30,
                "below_min": 0,
                "above_max": 31
            },
            # WiFi設定の境界値
            "wifi_ssid_length": {
                "max": 32,
                "above_max": 33
            },
            "wifi_password_length": {
                "max": 64,
                "above_max": 65
            }
        }
    
    @classmethod
    def get_valid_enum_values(cls) -> Dict[str, list]:
        """有効なenum値取得"""
        return {
            "move_direction": ["up", "down", "left", "right", "forward", "back"],
            "rotate_direction": ["clockwise", "counter_clockwise"],
            "flip_direction": ["left", "right", "forward", "back"],
            "camera_resolution": ["high", "low"],
            "camera_fps": ["high", "middle", "low"],
            "tracking_mode": ["center", "follow"],
            "mission_pad_direction": [0, 1, 2]
        }
    
    @classmethod
    def get_invalid_enum_values(cls) -> Dict[str, list]:
        """無効なenum値取得"""
        return {
            "move_direction": ["invalid", "diagonal", "sideways"],
            "rotate_direction": ["invalid", "left", "right"],
            "flip_direction": ["invalid", "up", "down"],
            "camera_resolution": ["invalid", "medium", "ultra"],
            "camera_fps": ["invalid", "very_high", "ultra"],
            "tracking_mode": ["invalid", "aggressive", "passive"],
            "mission_pad_direction": [-1, 3, 5]
        }