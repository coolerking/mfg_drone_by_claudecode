"""
基本飛行制御APIのテスト
"""

import pytest
from tests.stubs.drone_stub import TelloStub


class TestTakeoff:
    """離陸テストクラス"""
    
    def test_takeoff_success(self, connected_drone):
        """正常な離陸テスト"""
        result = connected_drone.takeoff()
        assert result is True
        assert connected_drone._flying is True
        assert connected_drone._height == 120  # 1.2m
        assert connected_drone._battery < 100  # バッテリー消費
    
    def test_takeoff_not_connected(self, drone):
        """未接続時の離陸テスト"""
        with pytest.raises(Exception, match="Not connected"):
            drone.takeoff()
        assert drone._flying is False
    
    def test_takeoff_already_flying(self, flying_drone):
        """既に飛行中の離陸テスト"""
        with pytest.raises(Exception, match="Already flying"):
            flying_drone.takeoff()
    
    def test_takeoff_command_failure(self, connected_drone):
        """離陸コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.takeoff()
        assert result is False
        assert connected_drone._flying is False
    
    def test_takeoff_battery_consumption(self, connected_drone):
        """離陸時のバッテリー消費テスト"""
        initial_battery = connected_drone._battery
        connected_drone.takeoff()
        assert connected_drone._battery == initial_battery - 5


class TestLand:
    """着陸テストクラス"""
    
    def test_land_success(self, flying_drone):
        """正常な着陸テスト"""
        result = flying_drone.land()
        assert result is True
        assert flying_drone._flying is False
        assert flying_drone._height == 0
    
    def test_land_not_connected(self, drone):
        """未接続時の着陸テスト"""
        with pytest.raises(Exception, match="Not connected"):
            drone.land()
    
    def test_land_not_flying(self, connected_drone):
        """未飛行時の着陸テスト"""
        with pytest.raises(Exception, match="Not flying"):
            connected_drone.land()
    
    def test_land_command_failure(self, flying_drone):
        """着陸コマンド失敗テスト"""
        flying_drone.set_simulate_command_error(True)
        result = flying_drone.land()
        assert result is False
        assert flying_drone._flying is True  # 失敗時は飛行状態維持
    
    def test_land_battery_consumption(self, flying_drone):
        """着陸時のバッテリー消費テスト"""
        initial_battery = flying_drone._battery
        flying_drone.land()
        assert flying_drone._battery == initial_battery - 2


class TestEmergency:
    """緊急停止テストクラス"""
    
    def test_emergency_success(self, flying_drone):
        """正常な緊急停止テスト"""
        result = flying_drone.emergency()
        assert result is True
        assert flying_drone._flying is False
        assert flying_drone._height == 0
    
    def test_emergency_not_connected(self, drone):
        """未接続時の緊急停止テスト"""
        with pytest.raises(Exception, match="Not connected"):
            drone.emergency()
    
    def test_emergency_not_flying(self, connected_drone):
        """未飛行時の緊急停止テスト"""
        result = connected_drone.emergency()
        assert result is True  # 緊急停止は常に実行される
        assert connected_drone._flying is False
    
    def test_emergency_command_failure(self, connected_drone):
        """緊急停止コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.emergency()
        assert result is False
    
    def test_emergency_immediate_stop(self, flying_drone):
        """緊急停止の即座実行テスト"""
        # 飛行中に緊急停止
        initial_flying = flying_drone._flying
        assert initial_flying is True
        
        flying_drone.emergency()
        assert flying_drone._flying is False
        assert flying_drone._height == 0


class TestStop:
    """ホバリングテストクラス"""
    
    def test_stop_success(self, flying_drone):
        """正常なホバリングテスト"""
        result = flying_drone.stop()
        assert result is True
        # 飛行状態は維持される
        assert flying_drone._flying is True
    
    def test_stop_not_connected(self, drone):
        """未接続時のホバリングテスト"""
        with pytest.raises(Exception, match="Not connected"):
            drone.stop()
    
    def test_stop_not_flying(self, connected_drone):
        """未飛行時のホバリングテスト"""
        with pytest.raises(Exception, match="Not flying"):
            connected_drone.stop()
    
    def test_stop_command_failure(self, flying_drone):
        """ホバリングコマンド失敗テスト"""
        flying_drone.set_simulate_command_error(True)
        result = flying_drone.stop()
        assert result is False


class TestFlightSequence:
    """飛行シーケンステストクラス"""
    
    def test_complete_flight_sequence(self, connected_drone):
        """完全な飛行シーケンステスト"""
        # 離陸
        takeoff_result = connected_drone.takeoff()
        assert takeoff_result is True
        assert connected_drone._flying is True
        
        # ホバリング
        stop_result = connected_drone.stop()
        assert stop_result is True
        assert connected_drone._flying is True
        
        # 着陸
        land_result = connected_drone.land()
        assert land_result is True
        assert connected_drone._flying is False
    
    def test_emergency_during_flight(self, connected_drone):
        """飛行中の緊急停止テスト"""
        # 離陸
        connected_drone.takeoff()
        assert connected_drone._flying is True
        
        # 緊急停止
        emergency_result = connected_drone.emergency()
        assert emergency_result is True
        assert connected_drone._flying is False
    
    def test_multiple_takeoffs_prevention(self, connected_drone):
        """重複離陸防止テスト"""
        # 最初の離陸
        connected_drone.takeoff()
        assert connected_drone._flying is True
        
        # 2回目の離陸（エラー）
        with pytest.raises(Exception, match="Already flying"):
            connected_drone.takeoff()
    
    def test_landing_without_takeoff_prevention(self, connected_drone):
        """離陸なし着陸防止テスト"""
        # 離陸せずに着陸（エラー）
        with pytest.raises(Exception, match="Not flying"):
            connected_drone.land()
    
    def test_battery_drain_during_flight(self, connected_drone):
        """飛行中のバッテリー消費テスト"""
        initial_battery = connected_drone._battery
        
        # 離陸（バッテリー消費）
        connected_drone.takeoff()
        after_takeoff = connected_drone._battery
        assert after_takeoff < initial_battery
        
        # 着陸（バッテリー消費）
        connected_drone.land()
        after_landing = connected_drone._battery
        assert after_landing < after_takeoff