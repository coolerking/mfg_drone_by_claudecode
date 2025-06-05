"""
テスト設定ファイル
実機接続モードとスタブモードの切り替えを管理
"""

import os
from typing import Optional


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
    
    @classmethod
    def is_real_drone_mode(cls) -> bool:
        """実機モードかどうかを判定"""
        return cls.USE_REAL_DRONE
    
    @classmethod
    def get_drone_connection_info(cls) -> tuple[str, int]:
        """ドローン接続情報を取得"""
        return cls.TELLO_IP, cls.TELLO_PORT