"""
Phase 3: ドローンシミュレーターテストスイート
物理シミュレーション機能の包括的テスト
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Virtual3DSpace, DronePhysicsEngine,
    Vector3D, DroneState3D, DronePhysics, Obstacle, ObstacleType, DroneState
)
from core.virtual_camera import VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
from config.simulation_config import ConfigurationManager, PresetScenarios


class TestVector3D:
    """Vector3Dクラスのテスト"""
    
    def test_vector_creation(self):
        """ベクトル作成テスト"""
        v = Vector3D(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
    
    def test_vector_addition(self):
        """ベクトル加算テスト"""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        result = v1 + v2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0
    
    def test_vector_subtraction(self):
        """ベクトル減算テスト"""
        v1 = Vector3D(4.0, 5.0, 6.0)
        v2 = Vector3D(1.0, 2.0, 3.0)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 3.0
        assert result.z == 3.0
    
    def test_vector_scalar_multiplication(self):
        """ベクトルスカラー乗算テスト"""
        v = Vector3D(1.0, 2.0, 3.0)
        result = v * 2.0
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0
    
    def test_vector_magnitude(self):
        """ベクトル大きさテスト"""
        v = Vector3D(3.0, 4.0, 0.0)
        assert v.magnitude() == 5.0
    
    def test_vector_normalization(self):
        """ベクトル正規化テスト"""
        v = Vector3D(3.0, 4.0, 0.0)
        normalized = v.normalize()
        assert abs(normalized.magnitude() - 1.0) < 1e-10
        assert abs(normalized.x - 0.6) < 1e-10
        assert abs(normalized.y - 0.8) < 1e-10


class TestObstacle:
    """Obstacleクラスのテスト"""
    
    def test_obstacle_creation(self):
        """障害物作成テスト"""
        obstacle = Obstacle(
            id="test_wall",
            obstacle_type=ObstacleType.WALL,
            position=Vector3D(0, 0, 1),
            size=Vector3D(2, 2, 2)
        )
        assert obstacle.id == "test_wall"
        assert obstacle.obstacle_type == ObstacleType.WALL
        assert obstacle.position.z == 1
    
    def test_bounding_box_calculation(self):
        """バウンディングボックス計算テスト"""
        obstacle = Obstacle(
            id="test_box",
            obstacle_type=ObstacleType.DYNAMIC,
            position=Vector3D(0, 0, 0),
            size=Vector3D(2, 2, 2)
        )
        bbox = obstacle.get_bounding_box()
        assert len(bbox) == 2
        assert bbox[0].x == -1.0  # min_x
        assert bbox[1].x == 1.0   # max_x
    
    def test_point_containment(self):
        """点包含判定テスト"""
        obstacle = Obstacle(
            id="test_container",
            obstacle_type=ObstacleType.COLUMN,
            position=Vector3D(0, 0, 0),
            size=Vector3D(2, 2, 2)
        )
        
        # 内部の点
        assert obstacle.contains_point(Vector3D(0, 0, 0)) == True
        assert obstacle.contains_point(Vector3D(0.5, 0.5, 0.5)) == True
        
        # 外部の点
        assert obstacle.contains_point(Vector3D(2, 0, 0)) == False
        assert obstacle.contains_point(Vector3D(0, 0, 2)) == False


class TestVirtual3DSpace:
    """Virtual3DSpaceクラスのテスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.space = Virtual3DSpace(bounds=(10.0, 10.0, 5.0))
    
    def test_space_creation(self):
        """3D空間作成テスト"""
        assert self.space.bounds.x == 10.0
        assert self.space.bounds.y == 10.0
        assert self.space.bounds.z == 5.0
        
        # デフォルトの境界壁が作成されているか確認
        assert "floor" in self.space.obstacles
        assert "ceiling" in self.space.obstacles
        assert "wall_north" in self.space.obstacles
    
    def test_obstacle_management(self):
        """障害物管理テスト"""
        obstacle = Obstacle(
            id="test_obstacle",
            obstacle_type=ObstacleType.COLUMN,
            position=Vector3D(0, 0, 1),
            size=Vector3D(1, 1, 2)
        )
        
        # 障害物追加
        initial_count = len(self.space.obstacles)
        self.space.add_obstacle(obstacle)
        assert len(self.space.obstacles) == initial_count + 1
        assert "test_obstacle" in self.space.obstacles
        
        # 障害物削除
        success = self.space.remove_obstacle("test_obstacle")
        assert success == True
        assert len(self.space.obstacles) == initial_count
        assert "test_obstacle" not in self.space.obstacles
    
    def test_collision_detection(self):
        """衝突判定テスト"""
        # 障害物を追加
        obstacle = Obstacle(
            id="collision_test",
            obstacle_type=ObstacleType.COLUMN,
            position=Vector3D(0, 0, 1),
            size=Vector3D(1, 1, 2)
        )
        self.space.add_obstacle(obstacle)
        
        # 衝突する位置
        collision, obstacle_id = self.space.check_collision(Vector3D(0, 0, 1))
        assert collision == True
        assert obstacle_id == "collision_test"
        
        # 衝突しない位置
        collision, obstacle_id = self.space.check_collision(Vector3D(3, 3, 1))
        assert collision == False
    
    def test_position_validation(self):
        """位置有効性判定テスト"""
        # 有効な位置
        assert self.space.is_position_valid(Vector3D(0, 0, 2)) == True
        assert self.space.is_position_valid(Vector3D(2, 2, 1)) == True
        
        # 境界外の位置
        assert self.space.is_position_valid(Vector3D(20, 0, 2)) == False
        assert self.space.is_position_valid(Vector3D(0, 0, 10)) == False
        assert self.space.is_position_valid(Vector3D(0, 0, -1)) == False


class TestDronePhysicsEngine:
    """DronePhysicsEngineクラスのテスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.physics_params = DronePhysics()
        self.engine = DronePhysicsEngine(self.physics_params)
    
    def test_physics_engine_creation(self):
        """物理エンジン作成テスト"""
        assert self.engine.physics.mass == 0.087
        assert self.engine.gravity.z == -9.81
    
    def test_force_application(self):
        """力適用テスト"""
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 1),
            velocity=Vector3D(0, 0, 0)
        )
        
        # 上向きの推力を適用
        thrust = Vector3D(0, 0, 10)  # 重力を上回る推力
        dt = 0.1
        
        new_state = self.engine.apply_forces(initial_state, thrust, dt)
        
        # 上向きに加速しているかチェック
        assert new_state.velocity.z > 0
        assert new_state.position.z > initial_state.position.z
    
    def test_gravity_effect(self):
        """重力効果テスト"""
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 5),
            velocity=Vector3D(0, 0, 0)
        )
        
        # 推力なし（重力のみ）
        thrust = Vector3D(0, 0, 0)
        dt = 0.1
        
        new_state = self.engine.apply_forces(initial_state, thrust, dt)
        
        # 下向きに加速しているかチェック
        assert new_state.velocity.z < 0
        assert new_state.position.z < initial_state.position.z
    
    def test_speed_limitation(self):
        """速度制限テスト"""
        initial_state = DroneState3D(
            position=Vector3D(0, 0, 1),
            velocity=Vector3D(15, 0, 0)  # 最大速度を超える初期速度
        )
        
        thrust = Vector3D(0, 0, 9.81 * self.physics_params.mass)  # ホバリング推力
        dt = 0.1
        
        new_state = self.engine.apply_forces(initial_state, thrust, dt)
        
        # 速度が制限されているかチェック
        assert new_state.velocity.magnitude() <= self.physics_params.max_speed


class TestDroneSimulator:
    """DroneSimulatorクラスのテスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.simulator = DroneSimulator("test_drone", (10.0, 10.0, 5.0))
    
    def test_simulator_creation(self):
        """シミュレータ作成テスト"""
        assert self.simulator.drone_id == "test_drone"
        assert self.simulator.current_state.state == DroneState.IDLE
        assert self.simulator.current_state.battery_level == 100.0
    
    def test_takeoff_command(self):
        """離陸コマンドテスト"""
        success = self.simulator.takeoff()
        assert success == True
        assert self.simulator.current_state.state == DroneState.TAKEOFF
        assert self.simulator.target_position is not None
        assert self.simulator.target_position.z == 1.5
    
    def test_takeoff_battery_check(self):
        """離陸時バッテリー確認テスト"""
        # バッテリー残量を低く設定
        self.simulator.current_state.battery_level = 5.0
        
        success = self.simulator.takeoff()
        assert success == False
        assert self.simulator.current_state.state == DroneState.IDLE
    
    def test_landing_command(self):
        """着陸コマンドテスト"""
        # まず離陸状態に設定
        self.simulator.current_state.state = DroneState.FLYING
        
        success = self.simulator.land()
        assert success == True
        assert self.simulator.current_state.state == DroneState.LANDING
        assert self.simulator.target_position.z == 0.1
    
    def test_move_to_position(self):
        """位置移動テスト"""
        # 飛行状態に設定
        self.simulator.current_state.state = DroneState.FLYING
        
        success = self.simulator.move_to_position(2.0, 3.0, 2.0)
        assert success == True
        assert self.simulator.target_position.x == 2.0
        assert self.simulator.target_position.y == 3.0
        assert self.simulator.target_position.z == 2.0
    
    def test_invalid_move_command(self):
        """無効な移動コマンドテスト"""
        # 待機状態での移動コマンド
        success = self.simulator.move_to_position(2.0, 3.0, 2.0)
        assert success == False
        
        # 範囲外への移動コマンド
        self.simulator.current_state.state = DroneState.FLYING
        success = self.simulator.move_to_position(20.0, 20.0, 2.0)
        assert success == False
    
    def test_rotation_command(self):
        """回転コマンドテスト"""
        # 飛行状態に設定
        self.simulator.current_state.state = DroneState.FLYING
        
        success = self.simulator.rotate_to_yaw(90.0)
        assert success == True
        assert self.simulator.current_state.rotation.z == 90.0
    
    def test_simulation_start_stop(self):
        """シミュレーション開始・停止テスト"""
        assert self.simulator.is_running == False
        
        self.simulator.start_simulation()
        assert self.simulator.is_running == True
        assert self.simulator.simulation_thread is not None
        
        # 少し待って停止
        time.sleep(0.1)
        self.simulator.stop_simulation()
        assert self.simulator.is_running == False
    
    def test_camera_integration(self):
        """カメラ統合テスト"""
        camera_stream = VirtualCameraStream(640, 480, 30)
        self.simulator.set_camera_stream(camera_stream)
        
        assert self.simulator.camera_stream is not None
        assert self.simulator.camera_integration_enabled == True
    
    def test_obstacle_addition(self):
        """障害物追加テスト"""
        initial_count = len(self.simulator.virtual_world.obstacles)
        self.simulator.add_sample_obstacles()
        
        # サンプル障害物が追加されているかチェック
        assert len(self.simulator.virtual_world.obstacles) > initial_count
        assert "center_column" in self.simulator.virtual_world.obstacles
    
    def test_statistics_collection(self):
        """統計情報収集テスト"""
        stats = self.simulator.get_statistics()
        
        assert "drone_id" in stats
        assert "current_position" in stats
        assert "battery_level" in stats
        assert "flight_state" in stats
        assert stats["drone_id"] == "test_drone"


class TestMultiDroneSimulator:
    """MultiDroneSimulatorクラスのテスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.multi_sim = MultiDroneSimulator((20.0, 20.0, 10.0))
    
    def test_multi_simulator_creation(self):
        """複数ドローンシミュレータ作成テスト"""
        assert len(self.multi_sim.drones) == 0
        assert self.multi_sim.space_bounds == (20.0, 20.0, 10.0)
    
    def test_drone_management(self):
        """ドローン管理テスト"""
        # ドローン追加
        drone1 = self.multi_sim.add_drone("drone_001", (-5.0, -5.0, 0.1))
        drone2 = self.multi_sim.add_drone("drone_002", (5.0, 5.0, 0.1))
        
        assert len(self.multi_sim.drones) == 2
        assert "drone_001" in self.multi_sim.drones
        assert "drone_002" in self.multi_sim.drones
        assert drone1.drone_id == "drone_001"
        assert drone2.drone_id == "drone_002"
    
    def test_duplicate_drone_handling(self):
        """重複ドローン処理テスト"""
        drone1 = self.multi_sim.add_drone("drone_001")
        drone2 = self.multi_sim.add_drone("drone_001")  # 同じID
        
        assert len(self.multi_sim.drones) == 1
        assert drone1 is drone2  # 同じインスタンスが返される
    
    def test_all_simulations_control(self):
        """全シミュレーション制御テスト"""
        # 複数ドローンを追加
        self.multi_sim.add_drone("drone_001")
        self.multi_sim.add_drone("drone_002")
        
        # 全シミュレーション開始
        self.multi_sim.start_all_simulations()
        
        for drone in self.multi_sim.drones.values():
            assert drone.is_running == True
        
        # 少し待って停止
        time.sleep(0.1)
        self.multi_sim.stop_all_simulations()
        
        for drone in self.multi_sim.drones.values():
            assert drone.is_running == False
    
    def test_all_statistics(self):
        """全統計情報テスト"""
        self.multi_sim.add_drone("drone_001")
        self.multi_sim.add_drone("drone_002")
        
        all_stats = self.multi_sim.get_all_statistics()
        
        assert "drone_001" in all_stats
        assert "drone_002" in all_stats
        assert all_stats["drone_001"]["drone_id"] == "drone_001"
        assert all_stats["drone_002"]["drone_id"] == "drone_002"


class TestConfigurationManager:
    """ConfigurationManagerクラスのテスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.config_manager = ConfigurationManager()
    
    def test_preset_scenarios(self):
        """プリセットシナリオテスト"""
        scenarios = ["empty_room", "obstacle_course", "multi_drone", "emergency"]
        
        for scenario_name in scenarios:
            config = self.config_manager.get_preset_scenario(scenario_name)
            
            assert config is not None
            assert len(config.drones) > 0
            assert config.space_bounds is not None
    
    def test_empty_room_scenario(self):
        """空の部屋シナリオテスト"""
        config = self.config_manager.get_preset_scenario("empty_room")
        
        assert len(config.drones) == 1
        assert config.drones[0].drone_id == "test_drone"
        assert config.space_bounds == (10.0, 10.0, 5.0)
    
    def test_multi_drone_scenario(self):
        """複数ドローンシナリオテスト"""
        config = self.config_manager.get_preset_scenario("multi_drone")
        
        assert len(config.drones) == 3
        assert len(config.obstacles) > 0
        assert config.space_bounds == (25.0, 25.0, 12.0)
    
    def test_invalid_scenario(self):
        """無効なシナリオテスト"""
        with pytest.raises(ValueError):
            self.config_manager.get_preset_scenario("invalid_scenario")


class TestIntegration:
    """統合テスト"""
    
    def test_full_simulation_workflow(self):
        """完全シミュレーションワークフローテスト"""
        # シミュレータ作成
        simulator = DroneSimulator("integration_test")
        
        # カメラストリーム統合
        camera = VirtualCameraStream(320, 240, 15)
        tracking_obj = TrackingObject(
            TrackingObjectType.PERSON,
            (100, 100),
            (30, 60),
            (0, 255, 0),
            MovementPattern.LINEAR,
            10.0
        )
        camera.add_tracking_object(tracking_obj)
        simulator.set_camera_stream(camera)
        
        # サンプル障害物を追加
        simulator.add_sample_obstacles()
        
        # シミュレーション開始
        simulator.start_simulation()
        
        try:
            # 離陸
            success = simulator.takeoff()
            assert success == True
            
            # 少し待機（離陸完了まで）
            time.sleep(0.2)
            
            # 飛行状態に手動設定（テスト用）
            simulator.current_state.state = DroneState.FLYING
            
            # 移動
            success = simulator.move_to_position(2.0, 2.0, 2.0)
            assert success == True
            
            # 回転
            success = simulator.rotate_to_yaw(45.0)
            assert success == True
            
            # 着陸
            success = simulator.land()
            assert success == True
            
            # 統計情報確認
            stats = simulator.get_statistics()
            assert stats["drone_id"] == "integration_test"
            
        finally:
            # シミュレーション停止
            simulator.stop_simulation()
    
    def test_collision_scenario(self):
        """衝突シナリオテスト"""
        simulator = DroneSimulator("collision_test")
        
        # 障害物を追加
        obstacle = Obstacle(
            id="collision_target",
            obstacle_type=ObstacleType.COLUMN,
            position=Vector3D(1, 1, 1),
            size=Vector3D(0.5, 0.5, 2)
        )
        simulator.virtual_world.add_obstacle(obstacle)
        
        # 衝突する位置に移動試行
        simulator.current_state.state = DroneState.FLYING
        
        # 障害物の位置に移動試行
        success = simulator.move_to_position(1.0, 1.0, 1.0)
        # 衝突判定により移動が拒否されるはず
        assert success == False
    
    def test_battery_drain_scenario(self):
        """バッテリー消耗シナリオテスト"""
        simulator = DroneSimulator("battery_test")
        
        # バッテリー残量を低く設定
        simulator.current_state.battery_level = 15.0
        
        # 離陸試行
        success = simulator.takeoff()
        assert success == True
        
        # バッテリー残量を更に下げる
        simulator.current_state.battery_level = 0.0
        
        # バッテリー切れの処理が実行されるかチェック
        # 実際のテストでは_handle_battery_empty()の呼び出しを確認


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])