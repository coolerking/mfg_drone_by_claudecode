"""
境界値・異常値テストスイート
極限条件とエッジケースでのシステム動作テスト
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Vector3D, DroneState, DroneState3D,
    Obstacle, ObstacleType, DronePhysics, DronePhysicsEngine
)
from core.virtual_camera import (
    VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
)


class TestExtremeCoordinates:
    """極座標・境界値テスト"""
    
    def test_zero_coordinates_handling(self):
        """座標ゼロ値処理テスト"""
        simulator = DroneSimulator("zero_test", (10.0, 10.0, 5.0))
        
        # ゼロ座標での各種操作
        zero_vector = Vector3D(0.0, 0.0, 0.0)
        
        # ベクトル演算
        assert zero_vector.magnitude() == 0.0
        normalized = zero_vector.normalize()
        assert normalized.x == 0.0 and normalized.y == 0.0 and normalized.z == 0.0
        
        # ドローン位置設定
        simulator.current_state.position = zero_vector
        assert simulator.get_current_position() == (0.0, 0.0, 0.0)
        
        # ゼロ座標での移動
        simulator.current_state.state = DroneState.FLYING
        move_success = simulator.move_to_position(0.0, 0.0, 1.0)
        assert move_success == True
    
    def test_boundary_coordinates(self):
        """境界座標テスト"""
        bounds = (10.0, 10.0, 5.0)
        simulator = DroneSimulator("boundary_test", bounds)
        
        # 境界ギリギリの座標
        boundary_positions = [
            (4.99, 4.99, 4.99),   # 境界内ギリギリ
            (5.0, 5.0, 5.0),      # 境界線上
            (5.01, 5.01, 5.01),   # 境界外
            (-4.99, -4.99, 0.01), # 負の境界内
            (-5.01, -5.01, -0.01) # 負の境界外
        ]
        
        simulator.current_state.state = DroneState.FLYING
        
        for x, y, z in boundary_positions:
            is_valid = simulator.virtual_world.is_position_valid(Vector3D(x, y, z))
            move_success = simulator.move_to_position(x, y, z)
            
            if abs(x) <= bounds[0]/2 and abs(y) <= bounds[1]/2 and 0 <= z <= bounds[2]:
                assert is_valid == True
                assert move_success == True
            else:
                assert is_valid == False
                assert move_success == False
    
    def test_extreme_negative_coordinates(self):
        """極端な負座標テスト"""
        simulator = DroneSimulator("negative_test")
        
        extreme_negatives = [
            (-1000.0, 0.0, 0.0),
            (0.0, -1000.0, 0.0),
            (0.0, 0.0, -100.0),
            (-1000.0, -1000.0, -100.0)
        ]
        
        simulator.current_state.state = DroneState.FLYING
        
        for x, y, z in extreme_negatives:
            move_success = simulator.move_to_position(x, y, z)
            assert move_success == False  # 全て境界外なので失敗すべき
            
            # 位置有効性チェック
            is_valid = simulator.virtual_world.is_position_valid(Vector3D(x, y, z))
            assert is_valid == False
    
    def test_floating_point_precision(self):
        """浮動小数点精度テスト"""
        simulator = DroneSimulator("precision_test")
        
        # 極小値での計算
        tiny_values = [1e-10, 1e-15, 1e-20]
        
        for tiny in tiny_values:
            vector = Vector3D(tiny, tiny, tiny)
            magnitude = vector.magnitude()
            
            # 極小値でも適切に処理される
            assert magnitude >= 0
            assert not np.isnan(magnitude)
            assert not np.isinf(magnitude)
            
            # 正規化テスト
            if magnitude > 0:
                normalized = vector.normalize()
                assert not np.isnan(normalized.x)
                assert not np.isnan(normalized.y)
                assert not np.isnan(normalized.z)
    
    def test_very_large_coordinates(self):
        """極大座標テスト"""
        # 非常に大きな空間での動作テスト
        large_bounds = (1000.0, 1000.0, 500.0)
        simulator = DroneSimulator("large_test", large_bounds)
        
        large_coordinates = [
            (999.0, 999.0, 499.0),     # 大きいが有効
            (1000.0, 1000.0, 500.0),  # 境界線
            (1001.0, 1001.0, 501.0)   # 境界外
        ]
        
        simulator.current_state.state = DroneState.FLYING
        
        for x, y, z in large_coordinates:
            move_success = simulator.move_to_position(x, y, z)
            is_valid = simulator.virtual_world.is_position_valid(Vector3D(x, y, z))
            
            # 境界内は成功、境界外は失敗
            if abs(x) <= large_bounds[0]/2 and abs(y) <= large_bounds[1]/2 and 0 <= z <= large_bounds[2]:
                assert move_success == True
                assert is_valid == True
            else:
                assert move_success == False
                assert is_valid == False


class TestInvalidInputHandling:
    """無効入力処理テスト"""
    
    def test_nan_infinity_values(self):
        """NaN・無限大値処理テスト"""
        simulator = DroneSimulator("nan_test")
        
        invalid_values = [
            (float('nan'), 0.0, 0.0),
            (0.0, float('nan'), 0.0),
            (0.0, 0.0, float('nan')),
            (float('inf'), 0.0, 0.0),
            (0.0, float('inf'), 0.0),
            (0.0, 0.0, float('inf')),
            (-float('inf'), 0.0, 0.0)
        ]
        
        simulator.current_state.state = DroneState.FLYING
        
        for x, y, z in invalid_values:
            # NaN/無限大値での移動は失敗すべき
            move_success = simulator.move_to_position(x, y, z)
            assert move_success == False
            
            # 位置有効性も失敗すべき
            vector = Vector3D(x, y, z)
            is_valid = simulator.virtual_world.is_position_valid(vector)
            assert is_valid == False
    
    def test_negative_battery_levels(self):
        """負バッテリーレベルテスト"""
        simulator = DroneSimulator("battery_test")
        
        invalid_battery_levels = [-1.0, -10.0, -100.0]
        
        for battery_level in invalid_battery_levels:
            simulator.current_state.battery_level = battery_level
            
            # 負バッテリーでの離陸は失敗すべき
            takeoff_success = simulator.takeoff()
            assert takeoff_success == False
            
            # バッテリー取得時は適切に処理される
            current_battery = simulator.get_battery_level()
            assert current_battery == battery_level  # 値は設定されたまま
    
    def test_invalid_size_obstacles(self):
        """無効サイズ障害物テスト"""
        simulator = DroneSimulator("obstacle_size_test")
        
        invalid_sizes = [
            Vector3D(0.0, 0.0, 0.0),     # ゼロサイズ
            Vector3D(-1.0, 1.0, 1.0),    # 負の幅
            Vector3D(1.0, -1.0, 1.0),    # 負の奥行き
            Vector3D(1.0, 1.0, -1.0),    # 負の高さ
            Vector3D(-1.0, -1.0, -1.0)   # 全て負
        ]
        
        for i, size in enumerate(invalid_sizes):
            obstacle = Obstacle(
                id=f"invalid_obstacle_{i}",
                obstacle_type=ObstacleType.DYNAMIC,
                position=Vector3D(0.0, 0.0, 1.0),
                size=size
            )
            
            # 障害物追加は成功するが、衝突判定で適切に処理される
            simulator.virtual_world.add_obstacle(obstacle)
            
            # バウンディングボックス計算が異常値を発生させないことを確認
            bbox = obstacle.get_bounding_box()
            assert len(bbox) == 2
            assert not any(np.isnan(v) or np.isinf(v) for point in bbox for v in [point.x, point.y, point.z])
    
    def test_extreme_rotation_angles(self):
        """極端な回転角度テスト"""
        simulator = DroneSimulator("rotation_test")
        simulator.current_state.state = DroneState.FLYING
        
        extreme_angles = [
            360.0,    # 一回転
            720.0,    # 二回転
            -360.0,   # 負の一回転
            1800.0,   # 五回転
            -1800.0,  # 負の五回転
            float('inf'),  # 無限大
            float('nan')   # NaN
        ]
        
        for angle in extreme_angles:
            if np.isfinite(angle):
                # 有限値は処理される
                rotation_success = simulator.rotate_to_yaw(angle)
                assert rotation_success == True
                
                # 角度が設定される（正規化されるかもしれない）
                current_rotation = simulator.current_state.rotation.z
                assert np.isfinite(current_rotation)
            else:
                # 無限大・NaNは適切に処理される
                rotation_success = simulator.rotate_to_yaw(angle)
                # 実装によって成功/失敗が決まるが、クラッシュしないことが重要
                assert rotation_success in [True, False]


class TestPhysicsEdgeCases:
    """物理エンジンエッジケーステスト"""
    
    def test_zero_mass_physics(self):
        """質量ゼロ物理計算テスト"""
        physics_params = DronePhysics()
        physics_params.mass = 0.0  # 質量ゼロ
        
        engine = DronePhysicsEngine(physics_params)
        
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 1),
            velocity=Vector3D(0, 0, 0)
        )
        
        thrust = Vector3D(0, 0, 10)
        dt = 0.1
        
        # 質量ゼロでの計算（ゼロ除算回避）
        try:
            new_state = engine.apply_forces(initial_state, thrust, dt)
            # クラッシュしないことが重要
            assert new_state is not None
        except ZeroDivisionError:
            # ゼロ除算エラーが適切に処理される
            pass
    
    def test_extreme_thrust_values(self):
        """極端な推力値テスト"""
        physics_params = DronePhysics()
        engine = DronePhysicsEngine(physics_params)
        
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 1),
            velocity=Vector3D(0, 0, 0)
        )
        
        extreme_thrusts = [
            Vector3D(0, 0, 1000000),    # 極大推力
            Vector3D(0, 0, -1000000),   # 極大負推力
            Vector3D(1000000, 0, 0),    # 極大横推力
            Vector3D(float('inf'), 0, 0),  # 無限大推力
            Vector3D(float('nan'), 0, 0)   # NaN推力
        ]
        
        dt = 0.1
        
        for thrust in extreme_thrusts:
            try:
                new_state = engine.apply_forces(initial_state, thrust, dt)
                
                # 結果が有効であることを確認
                assert new_state is not None
                assert np.isfinite(new_state.position.x)
                assert np.isfinite(new_state.position.y)
                assert np.isfinite(new_state.position.z)
                assert np.isfinite(new_state.velocity.x)
                assert np.isfinite(new_state.velocity.y)
                assert np.isfinite(new_state.velocity.z)
                
            except (OverflowError, ValueError):
                # 極端な値での適切な例外処理
                pass
    
    def test_extreme_time_steps(self):
        """極端な時間ステップテスト"""
        physics_params = DronePhysics()
        engine = DronePhysicsEngine(physics_params)
        
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 1),
            velocity=Vector3D(1, 1, 0)
        )
        
        thrust = Vector3D(0, 0, 9.81 * physics_params.mass)  # 重力補償
        
        extreme_time_steps = [
            0.0,         # ゼロ時間
            1e-10,       # 極小時間
            1000.0,      # 極大時間
            -0.1,        # 負の時間
            float('inf'), # 無限大時間
            float('nan')  # NaN時間
        ]
        
        for dt in extreme_time_steps:
            try:
                new_state = engine.apply_forces(initial_state, thrust, dt)
                
                if np.isfinite(dt) and dt >= 0:
                    # 有効な時間ステップでは結果が期待される
                    assert new_state is not None
                    assert np.isfinite(new_state.position.magnitude())
                else:
                    # 無効な時間ステップは適切に処理される
                    pass
                    
            except (ValueError, OverflowError):
                # 適切な例外処理
                pass


class TestCameraEdgeCases:
    """カメラシステムエッジケーステスト"""
    
    def test_zero_resolution_camera(self):
        """ゼロ解像度カメラテスト"""
        invalid_resolutions = [
            (0, 480),    # 幅ゼロ
            (640, 0),    # 高さゼロ
            (0, 0),      # 両方ゼロ
            (-640, 480), # 負の幅
            (640, -480)  # 負の高さ
        ]
        
        for width, height in invalid_resolutions:
            try:
                camera = VirtualCameraStream(width, height, 30)
                # カメラ作成が成功する場合は、フレーム生成で適切に処理される
                
                if hasattr(camera, '_generate_frame'):
                    frame = camera._generate_frame()
                    if frame is not None:
                        assert frame.shape[0] >= 0
                        assert frame.shape[1] >= 0
                        
            except (ValueError, AssertionError):
                # 無効な解像度での適切な例外処理
                pass
    
    def test_extreme_fps_values(self):
        """極端なFPS値テスト"""
        extreme_fps_values = [0, -1, -30, 1000, 10000, float('inf'), float('nan')]
        
        for fps in extreme_fps_values:
            try:
                camera = VirtualCameraStream(320, 240, fps)
                
                if np.isfinite(fps) and fps > 0:
                    # 有効なFPSでは正常動作
                    assert camera.fps == fps
                    assert camera.frame_interval > 0
                else:
                    # 無効なFPSは適切に処理される
                    pass
                    
            except (ValueError, ZeroDivisionError):
                # 適切な例外処理
                pass
    
    def test_tracking_object_boundary_positions(self):
        """追跡オブジェクト境界位置テスト"""
        camera = VirtualCameraStream(320, 240, 10)
        
        boundary_positions = [
            (-100, -100),   # 画面外左上
            (400, 300),     # 画面外右下
            (160, -50),     # 画面外上
            (160, 300),     # 画面外下
            (-50, 120),     # 画面外左
            (400, 120),     # 画面外右
            (0, 0),         # 左上角
            (319, 239),     # 右下角（境界内）
            (320, 240)      # 右下角（境界外）
        ]
        
        for x, y in boundary_positions:
            obj = TrackingObject(
                object_type=TrackingObjectType.BALL,
                position=(x, y),
                size=(20, 20),
                color=(255, 0, 0),
                movement_pattern=MovementPattern.STATIC
            )
            
            # オブジェクト追加は成功する
            camera.add_tracking_object(obj)
            
            # フレーム生成で適切に処理される
            if hasattr(camera, '_generate_frame'):
                try:
                    frame = camera._generate_frame()
                    if frame is not None:
                        assert frame.shape == (240, 320, 3)
                except Exception:
                    # 境界外オブジェクトでの適切な例外処理
                    pass
            
            # 清理
            camera.tracking_objects.clear()


class TestMemoryAndResourceLimits:
    """メモリ・リソース制限テスト"""
    
    def test_massive_obstacle_count(self):
        """大量障害物テスト"""
        simulator = DroneSimulator("massive_test", (100.0, 100.0, 50.0))
        
        # 大量の障害物を追加
        obstacle_count = 100
        
        for i in range(obstacle_count):
            obstacle = Obstacle(
                id=f"mass_obstacle_{i}",
                obstacle_type=ObstacleType.DYNAMIC,
                position=Vector3D(i % 10 * 5.0, (i // 10) % 10 * 5.0, 1.0),
                size=Vector3D(0.5, 0.5, 2.0)
            )
            simulator.virtual_world.add_obstacle(obstacle)
        
        # 大量障害物環境での動作確認
        simulator.current_state.state = DroneState.FLYING
        
        # 衝突判定性能
        start_time = time.time()
        collision, obstacle_id = simulator.virtual_world.check_collision(Vector3D(2.5, 2.5, 1.0))
        end_time = time.time()
        
        # 合理的な時間内で完了
        assert end_time - start_time < 1.0  # 1秒以内
        
        # 結果の妥当性
        assert isinstance(collision, bool)
        if collision:
            assert obstacle_id is not None
    
    def test_high_frequency_operations(self):
        """高頻度操作テスト"""
        simulator = DroneSimulator("frequency_test")
        simulator.current_state.state = DroneState.FLYING
        
        # 高頻度での位置更新
        operation_count = 100
        successful_operations = 0
        
        start_time = time.time()
        
        for i in range(operation_count):
            x = i * 0.01
            y = i * 0.01
            z = 1.0 + i * 0.001
            
            success = simulator.move_to_position(x, y, z)
            if success:
                successful_operations += 1
        
        end_time = time.time()
        
        # 性能要件
        assert end_time - start_time < 5.0  # 5秒以内
        assert successful_operations > operation_count * 0.8  # 80%以上成功


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])