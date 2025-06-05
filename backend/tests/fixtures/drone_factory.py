"""
ドローンインスタンス作成ファクトリ
実機/スタブの切り替えを管理
"""

from typing import Union
from config.test_config import TestConfig
from tests.stubs.drone_stub import TelloStub


def create_drone_instance() -> Union[TelloStub, object]:
    """
    テスト設定に基づいてドローンインスタンスを作成
    
    Returns:
        実機モード時: djitellopy.Tello
        スタブモード時: TelloStub
    """
    if TestConfig.is_real_drone_mode():
        try:
            from djitellopy import Tello
            return Tello()
        except ImportError:
            print("Warning: djitellopy not installed, falling back to stub mode")
            return TelloStub()
    else:
        return TelloStub()


def create_test_drone() -> TelloStub:
    """
    テスト専用のスタブドローンインスタンスを作成
    エラーシミュレーション機能付き
    """
    return TelloStub()


class DroneTestHelper:
    """ドローンテスト用ヘルパークラス"""
    
    @staticmethod
    def setup_connection_error(drone: TelloStub):
        """接続エラーをシミュレート"""
        if hasattr(drone, 'set_simulate_connection_error'):
            drone.set_simulate_connection_error(True)
    
    @staticmethod
    def setup_command_error(drone: TelloStub):
        """コマンドエラーをシミュレート"""
        if hasattr(drone, 'set_simulate_command_error'):
            drone.set_simulate_command_error(True)
    
    @staticmethod
    def setup_timeout_error(drone: TelloStub):
        """タイムアウトエラーをシミュレート"""
        if hasattr(drone, 'set_simulate_timeout'):
            drone.set_simulate_timeout(True)
    
    @staticmethod
    def reset_drone_state(drone: TelloStub):
        """ドローン状態をリセット"""
        if hasattr(drone, 'reset_state'):
            drone.reset_state()
    
    @staticmethod
    def setup_flying_state(drone: TelloStub):
        """飛行状態にセットアップ"""
        if hasattr(drone, '_connected') and hasattr(drone, '_flying'):
            drone._connected = True
            drone._flying = True
            drone._height = 120
    
    @staticmethod
    def setup_connected_state(drone: TelloStub):
        """接続状態にセットアップ"""
        if hasattr(drone, '_connected'):
            drone._connected = True