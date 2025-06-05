"""
移動制御APIのテスト
"""

import pytest
from tests.stubs.drone_stub import TelloStub


class TestBasicMovement:
    """基本移動テストクラス"""
    
    def test_move_up_success(self, flying_drone):
        """上移動成功テスト"""
        result = flying_drone.move_up(100)
        assert result is True
    
    def test_move_down_success(self, flying_drone):
        """下移動成功テスト"""
        result = flying_drone.move_down(100)
        assert result is True
    
    def test_move_left_success(self, flying_drone):
        """左移動成功テスト"""
        result = flying_drone.move_left(100)
        assert result is True
    
    def test_move_right_success(self, flying_drone):
        """右移動成功テスト"""
        result = flying_drone.move_right(100)
        assert result is True
    
    def test_move_forward_success(self, flying_drone):
        """前進成功テスト"""
        result = flying_drone.move_forward(100)
        assert result is True
    
    def test_move_back_success(self, flying_drone):
        """後退成功テスト"""
        result = flying_drone.move_back(100)
        assert result is True
    
    def test_move_boundary_values(self, flying_drone):
        """移動距離境界値テスト"""
        # 最小値
        result_min = flying_drone.move_up(20)
        assert result_min is True
        
        # 最大値
        result_max = flying_drone.move_down(500)
        assert result_max is True
    
    def test_move_invalid_distances(self, flying_drone):
        """無効な移動距離テスト"""
        # 最小値未満
        result_too_small = flying_drone.move_up(19)
        assert result_too_small is False
        
        # 最大値超過
        result_too_large = flying_drone.move_down(501)
        assert result_too_large is False
        
        # 負の値
        result_negative = flying_drone.move_left(-50)
        assert result_negative is False
    
    def test_move_not_connected(self, drone):
        """未接続時の移動テスト"""
        result = drone.move_up(100)
        assert result is False
    
    def test_move_not_flying(self, connected_drone):
        """未飛行時の移動テスト"""
        result = connected_drone.move_forward(100)
        assert result is False
    
    def test_move_command_failure(self, flying_drone):
        """移動コマンド失敗テスト"""
        flying_drone.set_simulate_command_error(True)
        result = flying_drone.move_up(100)
        assert result is False
    
    def test_move_battery_consumption(self, flying_drone):
        """移動時のバッテリー消費テスト"""
        initial_battery = flying_drone._battery
        flying_drone.move_forward(100)
        assert flying_drone._battery == initial_battery - 2


class TestRotation:
    """回転テストクラス"""
    
    def test_rotate_clockwise_success(self, flying_drone):
        """時計回り回転成功テスト"""
        result = flying_drone.rotate_clockwise(90)
        assert result is True
    
    def test_rotate_counter_clockwise_success(self, flying_drone):
        """反時計回り回転成功テスト"""
        result = flying_drone.rotate_counter_clockwise(90)
        assert result is True
    
    def test_rotate_boundary_values(self, flying_drone):
        """回転角度境界値テスト"""
        # 最小値
        result_min = flying_drone.rotate_clockwise(1)
        assert result_min is True
        
        # 最大値
        result_max = flying_drone.rotate_counter_clockwise(360)
        assert result_max is True
    
    def test_rotate_invalid_angles(self, flying_drone):
        """無効な回転角度テスト"""
        # 最小値未満
        result_too_small = flying_drone.rotate_clockwise(0)
        assert result_too_small is False
        
        # 最大値超過
        result_too_large = flying_drone.rotate_clockwise(361)
        assert result_too_large is False
        
        # 負の値
        result_negative = flying_drone.rotate_clockwise(-30)
        assert result_negative is False
    
    def test_rotate_not_flying(self, connected_drone):
        """未飛行時の回転テスト"""
        result = connected_drone.rotate_clockwise(90)
        assert result is False


class TestFlip:
    """宙返りテストクラス"""
    
    def test_flip_left_success(self, flying_drone):
        """左宙返り成功テスト"""
        result = flying_drone.flip_left()
        assert result is True
    
    def test_flip_right_success(self, flying_drone):
        """右宙返り成功テスト"""
        result = flying_drone.flip_right()
        assert result is True
    
    def test_flip_forward_success(self, flying_drone):
        """前宙返り成功テスト"""
        result = flying_drone.flip_forward()
        assert result is True
    
    def test_flip_back_success(self, flying_drone):
        """後宙返り成功テスト"""
        result = flying_drone.flip_back()
        assert result is True
    
    def test_flip_not_flying(self, connected_drone):
        """未飛行時の宙返りテスト"""
        result = connected_drone.flip_left()
        assert result is False
    
    def test_flip_command_failure(self, flying_drone):
        """宙返りコマンド失敗テスト"""
        flying_drone.set_simulate_command_error(True)
        result = flying_drone.flip_forward()
        assert result is False


class TestAdvancedMovement:
    """高度な移動制御テストクラス"""
    
    def test_go_xyz_speed_success(self, flying_drone):
        """座標移動成功テスト"""
        result = flying_drone.go_xyz_speed(100, -50, 200, 50)
        assert result is True
    
    def test_go_xyz_speed_boundary_values(self, flying_drone):
        """座標移動境界値テスト"""
        # 座標最小値
        result_min_coord = flying_drone.go_xyz_speed(-500, -500, -500, 10)
        assert result_min_coord is True
        
        # 座標最大値
        result_max_coord = flying_drone.go_xyz_speed(500, 500, 500, 100)
        assert result_max_coord is True
    
    def test_go_xyz_speed_invalid_coordinates(self, flying_drone):
        """無効な座標移動テスト"""
        # X座標範囲外
        result_x_invalid = flying_drone.go_xyz_speed(501, 0, 0, 50)
        assert result_x_invalid is False
        
        # Y座標範囲外
        result_y_invalid = flying_drone.go_xyz_speed(0, -501, 0, 50)
        assert result_y_invalid is False
        
        # Z座標範囲外
        result_z_invalid = flying_drone.go_xyz_speed(0, 0, 501, 50)
        assert result_z_invalid is False
        
        # 速度範囲外
        result_speed_invalid = flying_drone.go_xyz_speed(0, 0, 0, 101)
        assert result_speed_invalid is False
    
    def test_curve_xyz_speed_success(self, flying_drone):
        """曲線飛行成功テスト"""
        result = flying_drone.curve_xyz_speed(100, 50, 0, 200, 100, 50, 30)
        assert result is True
    
    def test_curve_xyz_speed_boundary_values(self, flying_drone):
        """曲線飛行境界値テスト"""
        # 最小速度
        result_min_speed = flying_drone.curve_xyz_speed(
            -500, -500, -500, 500, 500, 500, 10
        )
        assert result_min_speed is True
        
        # 最大速度
        result_max_speed = flying_drone.curve_xyz_speed(
            -100, -100, -100, 100, 100, 100, 60
        )
        assert result_max_speed is True
    
    def test_curve_xyz_speed_invalid_values(self, flying_drone):
        """無効な曲線飛行テスト"""
        # 速度範囲外
        result_speed_too_low = flying_drone.curve_xyz_speed(
            0, 0, 0, 100, 100, 100, 9
        )
        assert result_speed_too_low is False
        
        result_speed_too_high = flying_drone.curve_xyz_speed(
            0, 0, 0, 100, 100, 100, 61
        )
        assert result_speed_too_high is False
    
    def test_send_rc_control_success(self, flying_drone):
        """リアルタイム制御成功テスト"""
        # 正常なリアルタイム制御
        flying_drone.send_rc_control(50, -30, 20, 10)
        # 例外が発生しないことを確認
        assert True
    
    def test_send_rc_control_boundary_values(self, flying_drone):
        """リアルタイム制御境界値テスト"""
        # 最小値
        flying_drone.send_rc_control(-100, -100, -100, -100)
        assert True
        
        # 最大値
        flying_drone.send_rc_control(100, 100, 100, 100)
        assert True
        
        # ゼロ
        flying_drone.send_rc_control(0, 0, 0, 0)
        assert True
    
    def test_send_rc_control_not_connected(self, drone):
        """未接続時のリアルタイム制御テスト"""
        # 未接続でも例外は発生しない（void関数）
        drone.send_rc_control(50, 50, 50, 50)
        assert True
    
    def test_advanced_movement_battery_consumption(self, flying_drone):
        """高度な移動でのバッテリー消費テスト"""
        initial_battery = flying_drone._battery
        
        # 座標移動
        flying_drone.go_xyz_speed(100, 100, 100, 50)
        after_xyz = flying_drone._battery
        assert after_xyz == initial_battery - 3
        
        # 曲線飛行
        flying_drone.curve_xyz_speed(50, 50, 50, 100, 100, 100, 30)
        after_curve = flying_drone._battery
        assert after_curve == after_xyz - 5


class TestMovementSequence:
    """移動シーケンステストクラス"""
    
    def test_complex_movement_sequence(self, flying_drone):
        """複雑な移動シーケンステスト"""
        initial_battery = flying_drone._battery
        
        # 基本移動
        result1 = flying_drone.move_forward(100)
        assert result1 is True
        
        # 回転
        result2 = flying_drone.rotate_clockwise(90)
        assert result2 is True
        
        # 座標移動
        result3 = flying_drone.go_xyz_speed(50, 50, 50, 30)
        assert result3 is True
        
        # バッテリー消費確認
        assert flying_drone._battery < initial_battery
    
    def test_movement_error_recovery(self, flying_drone):
        """移動エラー回復テスト"""
        # エラー設定
        flying_drone.set_simulate_command_error(True)
        result_error = flying_drone.move_up(100)
        assert result_error is False
        
        # エラー解除後の正常動作
        flying_drone.set_simulate_command_error(False)
        result_success = flying_drone.move_up(100)
        assert result_success is True