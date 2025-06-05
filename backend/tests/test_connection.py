"""
ドローン接続関連APIのテスト
"""

import pytest
from tests.stubs.drone_stub import TelloStub


class TestConnection:
    """ドローン接続テストクラス"""
    
    def test_connect_success(self, drone):
        """正常な接続テスト"""
        result = drone.connect()
        assert result is True
        assert drone._connected is True
    
    def test_connect_failure(self, connection_error_drone):
        """接続失敗テスト"""
        with pytest.raises(Exception, match="Connection failed"):
            connection_error_drone.connect()
        assert connection_error_drone._connected is False
    
    def test_connect_timeout(self, timeout_drone):
        """接続タイムアウトテスト"""
        # タイムアウトは実際には発生させずにシミュレート
        with pytest.raises(Exception):
            timeout_drone.connect()
    
    def test_disconnect_success(self, connected_drone):
        """正常な切断テスト"""
        result = connected_drone.disconnect()
        assert result is True
        assert connected_drone._connected is False
        assert connected_drone._streaming is False
        assert connected_drone._flying is False
    
    def test_disconnect_not_connected(self, drone):
        """未接続状態での切断テスト"""
        result = drone.disconnect()
        assert result is True  # 切断は常に成功
        assert drone._connected is False
    
    def test_multiple_connections(self, drone):
        """複数回接続テスト"""
        # 最初の接続
        result1 = drone.connect()
        assert result1 is True
        assert drone._connected is True
        
        # 2回目の接続（既に接続済み）
        result2 = drone.connect()
        assert result2 is True
        assert drone._connected is True
    
    def test_connection_state_persistence(self, drone):
        """接続状態の永続性テスト"""
        # 接続
        drone.connect()
        assert drone._connected is True
        
        # 他の操作後も接続状態が維持されるか
        battery = drone.get_battery()
        assert battery is not None
        assert drone._connected is True
        
        # 切断
        drone.disconnect()
        assert drone._connected is False


class TestConnectionStatus:
    """接続状態確認テストクラス"""
    
    def test_operations_require_connection(self, drone):
        """接続が必要な操作のテスト"""
        # 未接続状態でセンサー値取得
        with pytest.raises(Exception, match="Not connected"):
            drone.get_battery()
        
        with pytest.raises(Exception, match="Not connected"):
            drone.get_height()
        
        with pytest.raises(Exception, match="Not connected"):
            drone.get_temperature()
    
    def test_operations_work_when_connected(self, connected_drone):
        """接続時の操作テスト"""
        # 接続状態でセンサー値取得
        battery = connected_drone.get_battery()
        assert 0 <= battery <= 100
        
        height = connected_drone.get_height()
        assert height >= 0
        
        temperature = connected_drone.get_temperature()
        assert 0 <= temperature <= 90
    
    def test_connection_error_propagation(self, connection_error_drone):
        """接続エラーの伝播テスト"""
        # 接続エラー設定時の動作確認
        with pytest.raises(Exception):
            connection_error_drone.connect()
        
        # エラー設定解除後の動作確認
        connection_error_drone.set_simulate_connection_error(False)
        result = connection_error_drone.connect()
        assert result is True
    
    def test_connection_recovery_after_error(self, drone):
        """エラー後の接続回復テスト"""
        # 最初は接続エラー
        drone.set_simulate_connection_error(True)
        with pytest.raises(Exception):
            drone.connect()
        
        # エラー設定解除後に接続成功
        drone.set_simulate_connection_error(False)
        result = drone.connect()
        assert result is True
        assert drone._connected is True