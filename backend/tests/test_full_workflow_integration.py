"""
フルワークフロー統合テストスイート
完全なシミュレーションライフサイクルと緊急時シナリオテスト
"""

import pytest
import time
import threading
from typing import List, Dict
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Vector3D, DroneState, Obstacle, ObstacleType
)
from core.virtual_camera import (
    VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
)
from config.simulation_config import ConfigurationManager, SimulationMode
from config.camera_config import DynamicCameraScenarios, configure_stream_from_scenario


class TestCompleteSimulationLifecycle:
    """完全シミュレーションライフサイクルテスト"""
    
    def test_full_single_drone_mission(self):
        """単一ドローン完全ミッションテスト"""
        # 設定読み込み
        config_manager = ConfigurationManager()
        config = config_manager.get_preset_scenario("obstacle_course")
        
        # シミュレータ作成
        simulator = DroneSimulator(
            config.drones[0].drone_id,
            config.space_bounds
        )
        
        # カメラ統合
        camera_scenario = DynamicCameraScenarios.get_warehouse_scenario()
        camera_stream = VirtualCameraStream(640, 480, 30)
        configure_stream_from_scenario(camera_stream, camera_scenario)
        simulator.set_camera_stream(camera_stream)
        
        # 障害物設定適用
        for obs_config in config.obstacles:
            obstacle = Obstacle(
                id=obs_config.obstacle_id,
                obstacle_type=ObstacleType(obs_config.obstacle_type),
                position=Vector3D(*obs_config.position),
                size=Vector3D(*obs_config.size),
                is_static=obs_config.is_static
            )
            simulator.virtual_world.add_obstacle(obstacle)
        
        mission_success = False
        try:
            # ミッション開始
            simulator.start_simulation()
            assert simulator.is_running == True
            
            # Phase 1: 離陸
            takeoff_success = simulator.takeoff()
            assert takeoff_success == True
            
            # 離陸完了まで待機
            time.sleep(0.3)
            simulator.current_state.state = DroneState.FLYING  # テスト用に強制設定
            
            # Phase 2: ウェイポイントナビゲーション
            waypoints = [
                (2.0, 2.0, 2.0),
                (4.0, -2.0, 3.0),
                (-2.0, 3.0, 2.5),
                (0.0, 0.0, 1.5)
            ]
            
            for i, (x, y, z) in enumerate(waypoints):
                move_success = simulator.move_to_position(x, y, z)
                if move_success:
                    # 移動完了まで少し待機
                    time.sleep(0.1)
                    
                    # 統計確認
                    stats = simulator.get_statistics()
                    assert stats["total_distance_traveled"] > 0
                    
                    # カメラフレーム確認
                    frame = camera_stream.get_frame()
                    if frame is not None:
                        assert frame.shape == (480, 640, 3)
            
            # Phase 3: 検査パターン（回転）
            for angle in [90, 180, 270, 0]:
                rotation_success = simulator.rotate_to_yaw(angle)
                assert rotation_success == True
                time.sleep(0.05)
            
            # Phase 4: 着陸
            landing_success = simulator.land()
            assert landing_success == True
            
            # ミッション完了
            mission_success = True
            
            # 最終統計確認
            final_stats = simulator.get_statistics()
            assert final_stats["total_flight_time"] > 0
            assert final_stats["collision_count"] == 0
            assert final_stats["drone_id"] == config.drones[0].drone_id
            
        finally:
            simulator.stop_simulation()
            camera_stream.stop_stream() if hasattr(camera_stream, '_streaming') and camera_stream._streaming else None
            
        assert mission_success == True
    
    def test_multi_drone_coordination_mission(self):
        """複数ドローン協調ミッションテスト"""
        config_manager = ConfigurationManager()
        config = config_manager.get_preset_scenario("multi_drone")
        
        # マルチドローンシミュレータ作成
        multi_sim = MultiDroneSimulator(config.space_bounds)
        
        # ドローン追加（最初の2台のみテスト）
        drone_configs = config.drones[:2]
        drones = []
        camera_streams = []
        
        for i, drone_config in enumerate(drone_configs):
            drone = multi_sim.add_drone(
                drone_config.drone_id,
                drone_config.initial_position
            )
            drones.append(drone)
            
            # 各ドローンに異なるカメラシナリオを設定
            scenarios = [
                DynamicCameraScenarios.get_indoor_tracking_scenario(),
                DynamicCameraScenarios.get_sports_ball_scenario()
            ]
            
            camera_stream = VirtualCameraStream(320, 240, 15)
            configure_stream_from_scenario(camera_stream, scenarios[i])
            drone.set_camera_stream(camera_stream)
            camera_streams.append(camera_stream)
        
        coordination_success = False
        try:
            # 協調ミッション開始
            multi_sim.start_all_simulations()
            
            # 各ドローンが動作していることを確認
            for drone in drones:
                assert drone.is_running == True
            
            # 同期離陸
            takeoff_results = []
            for drone in drones:
                result = drone.takeoff()
                takeoff_results.append(result)
                time.sleep(0.05)  # わずかな時間差
            
            assert all(takeoff_results)
            
            # 協調移動パターン
            time.sleep(0.2)  # 離陸完了待機
            
            # ドローンを飛行状態に設定（テスト用）
            for drone in drones:
                drone.current_state.state = DroneState.FLYING
            
            # 円形フォーメーション移動
            formation_positions = [
                [(3.0, 0.0, 2.0), (-3.0, 0.0, 2.0)],  # X軸配置
                [(0.0, 3.0, 2.5), (0.0, -3.0, 2.5)],  # Y軸配置
                [(2.0, 2.0, 3.0), (-2.0, -2.0, 3.0)]  # 対角配置
            ]
            
            for positions in formation_positions:
                move_results = []
                for drone, (x, y, z) in zip(drones, positions):
                    result = drone.move_to_position(x, y, z)
                    move_results.append(result)
                    time.sleep(0.02)
                
                # 移動完了待機
                time.sleep(0.1)
            
            # 同期着陸
            landing_results = []
            for drone in drones:
                result = drone.land()
                landing_results.append(result)
            
            coordination_success = True
            
            # 協調統計確認
            all_stats = multi_sim.get_all_statistics()
            assert len(all_stats) == len(drones)
            
            for drone_id, stats in all_stats.items():
                assert stats["total_flight_time"] > 0
                assert stats["drone_id"] == drone_id
            
        finally:
            multi_sim.stop_all_simulations()
            for camera_stream in camera_streams:
                if hasattr(camera_stream, '_streaming') and camera_stream._streaming:
                    camera_stream.stop_stream()
        
        assert coordination_success == True


class TestEmergencyScenarios:
    """緊急事態シナリオテスト"""
    
    def test_battery_critical_emergency_landing(self):
        """バッテリー緊急着陸シナリオテスト"""
        simulator = DroneSimulator("emergency_battery_test")
        
        # カメラ設定
        emergency_scenario = DynamicCameraScenarios.get_emergency_scenario()
        camera_stream = VirtualCameraStream(320, 240, 24)
        configure_stream_from_scenario(camera_stream, emergency_scenario)
        simulator.set_camera_stream(camera_stream)
        
        emergency_handled = False
        try:
            simulator.start_simulation()
            
            # 正常離陸
            takeoff_success = simulator.takeoff()
            assert takeoff_success == True
            
            time.sleep(0.1)
            simulator.current_state.state = DroneState.FLYING
            
            # バッテリーレベルを段階的に下げる
            battery_levels = [80, 60, 40, 20, 10, 5, 0]
            
            for battery_level in battery_levels:
                simulator.current_state.battery_level = battery_level
                
                if battery_level <= 10:
                    # 低バッテリー警告状態での動作確認
                    stats = simulator.get_statistics()
                    assert stats["battery_level"] == battery_level
                    
                if battery_level == 0:
                    # バッテリー切れ処理を手動実行
                    simulator._handle_battery_empty()
                    
                    # 緊急状態になることを確認
                    assert simulator.current_state.state == DroneState.EMERGENCY
                    break
                
                time.sleep(0.05)
            
            emergency_handled = True
            
        finally:
            simulator.stop_simulation()
            camera_stream.stop_stream() if hasattr(camera_stream, '_streaming') and camera_stream._streaming else None
            
        assert emergency_handled == True
    
    def test_collision_avoidance_emergency(self):
        """衝突回避緊急シナリオテスト"""
        simulator = DroneSimulator("collision_test")
        
        # 危険な障害物を追加
        dangerous_obstacle = Obstacle(
            id="danger_wall",
            obstacle_type=ObstacleType.WALL,
            position=Vector3D(2.0, 0.0, 2.0),
            size=Vector3D(0.5, 4.0, 4.0)
        )
        simulator.virtual_world.add_obstacle(dangerous_obstacle)
        
        collision_handled = False
        try:
            simulator.start_simulation()
            
            # 離陸
            simulator.takeoff()
            time.sleep(0.1)
            simulator.current_state.state = DroneState.FLYING
            
            # 障害物に向かって移動（衝突するはず）
            move_success = simulator.move_to_position(2.0, 0.0, 2.0)
            
            # 衝突位置への移動は拒否されるべき
            assert move_success == False
            
            # 安全な位置への移動は成功するべき
            safe_move = simulator.move_to_position(0.5, 0.5, 1.5)
            assert safe_move == True
            
            collision_handled = True
            
        finally:
            simulator.stop_simulation()
            
        assert collision_handled == True
    
    def test_system_overload_recovery(self):
        """システム過負荷回復テスト"""
        # 高負荷シナリオを作成
        multi_sim = MultiDroneSimulator((30.0, 30.0, 15.0))
        
        # 多数のドローンを追加
        num_drones = 5
        drones = []
        camera_streams = []
        
        for i in range(num_drones):
            drone = multi_sim.add_drone(
                f"overload_drone_{i}",
                (i * 4.0 - 10.0, i * 3.0 - 7.5, 0.1)
            )
            drones.append(drone)
            
            # 各ドローンに複雑なカメラシナリオを設定
            camera_stream = VirtualCameraStream(160, 120, 10)  # 低解像度でパフォーマンス重視
            
            # 多数の追跡オブジェクトを追加
            for j in range(3):
                obj = TrackingObject(
                    object_type=TrackingObjectType.PERSON if j % 2 == 0 else TrackingObjectType.VEHICLE,
                    position=(j * 40 + 50, j * 30 + 40),
                    size=(20, 20),
                    color=(j * 80, (j + 1) * 70, (j + 2) * 60),
                    movement_pattern=MovementPattern.RANDOM_WALK if j == 0 else MovementPattern.CIRCULAR
                )
                camera_stream.add_tracking_object(obj)
            
            drone.set_camera_stream(camera_stream)
            camera_streams.append(camera_stream)
        
        # 多数の障害物を追加
        for i in range(10):
            obstacle = Obstacle(
                id=f"overload_obstacle_{i}",
                obstacle_type=ObstacleType.DYNAMIC,
                position=Vector3D(i * 2.0 - 10.0, i * 1.5 - 7.5, 1.0),
                size=Vector3D(0.8, 0.8, 2.0)
            )
            multi_sim.shared_virtual_world.add_obstacle(obstacle)
        
        overload_handled = False
        try:
            # 高負荷シミュレーション開始
            start_time = time.time()
            multi_sim.start_all_simulations()
            
            # 全ドローンが開始されることを確認
            for drone in drones:
                assert drone.is_running == True
            
            # 短時間高負荷運転
            time.sleep(0.5)
            
            # システムが応答することを確認
            all_stats = multi_sim.get_all_statistics()
            assert len(all_stats) == num_drones
            
            # 各ドローンが動作していることを確認
            for drone_id, stats in all_stats.items():
                assert stats["drone_id"] == drone_id
                assert "current_position" in stats
            
            elapsed_time = time.time() - start_time
            
            # 合理的な時間内で完了することを確認
            assert elapsed_time < 2.0  # 2秒以内
            
            overload_handled = True
            
        finally:
            multi_sim.stop_all_simulations()
            for camera_stream in camera_streams:
                if hasattr(camera_stream, '_streaming') and camera_stream._streaming:
                    camera_stream.stop_stream()
        
        assert overload_handled == True


class TestFailureRecovery:
    """故障回復テスト"""
    
    def test_camera_failure_mission_continuation(self):
        """カメラ故障時ミッション継続テスト"""
        simulator = DroneSimulator("camera_failure_test")
        
        # 故障するカメラをモック
        mock_camera = Mock(spec=VirtualCameraStream)
        mock_camera._streaming = False
        mock_camera.start_stream.side_effect = Exception("Camera hardware failure")
        mock_camera.get_frame.return_value = None
        
        simulator.set_camera_stream(mock_camera)
        
        mission_continued = False
        try:
            # カメラ故障があってもシミュレーション開始
            simulator.start_simulation()
            assert simulator.is_running == True
            
            # ドローン機能は正常に動作
            takeoff_success = simulator.takeoff()
            assert takeoff_success == True
            
            time.sleep(0.1)
            simulator.current_state.state = DroneState.FLYING
            
            # 移動機能も正常
            move_success = simulator.move_to_position(1.0, 1.0, 2.0)
            assert move_success == True
            
            # 着陸も正常
            landing_success = simulator.land()
            assert landing_success == True
            
            mission_continued = True
            
        finally:
            simulator.stop_simulation()
        
        assert mission_continued == True
    
    def test_partial_system_failure_recovery(self):
        """部分的システム故障回復テスト"""
        multi_sim = MultiDroneSimulator((20.0, 20.0, 10.0))
        
        # 複数ドローンを追加
        drone1 = multi_sim.add_drone("working_drone", (-5.0, 0.0, 0.1))
        drone2 = multi_sim.add_drone("failing_drone", (5.0, 0.0, 0.1))
        
        # 正常なカメラ
        camera1 = VirtualCameraStream(320, 240, 15)
        obj1 = TrackingObject(
            object_type=TrackingObjectType.BALL,
            position=(160, 120),
            size=(20, 20),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.STATIC
        )
        camera1.add_tracking_object(obj1)
        drone1.set_camera_stream(camera1)
        
        # 故障するカメラ
        mock_camera2 = Mock(spec=VirtualCameraStream)
        mock_camera2._streaming = False
        mock_camera2.start_stream.side_effect = Exception("System failure")
        drone2.set_camera_stream(mock_camera2)
        
        recovery_successful = False
        try:
            # 部分故障状態でシステム開始
            multi_sim.start_all_simulations()
            
            # 正常なドローンは動作継続
            assert drone1.is_running == True
            takeoff1 = drone1.takeoff()
            assert takeoff1 == True
            
            # 故障したドローンも基本機能は動作
            assert drone2.is_running == True
            takeoff2 = drone2.takeoff()
            assert takeoff2 == True
            
            time.sleep(0.2)
            
            # 統計取得（部分的に成功）
            all_stats = multi_sim.get_all_statistics()
            assert len(all_stats) == 2
            assert "working_drone" in all_stats
            assert "failing_drone" in all_stats
            
            recovery_successful = True
            
        finally:
            multi_sim.stop_all_simulations()
            camera1.stop_stream() if hasattr(camera1, '_streaming') and camera1._streaming else None
        
        assert recovery_successful == True


class TestComplexScenarioIntegration:
    """複雑シナリオ統合テスト"""
    
    def test_dynamic_environment_adaptation(self):
        """動的環境適応テスト"""
        simulator = DroneSimulator("adaptation_test", (25.0, 25.0, 12.0))
        
        # 動的カメラシナリオ
        camera_stream = VirtualCameraStream(640, 480, 30)
        
        # 動的に変化する追跡オブジェクト
        dynamic_objects = [
            TrackingObject(
                object_type=TrackingObjectType.PERSON,
                position=(100, 200),
                size=(30, 60),
                color=(0, 255, 0),
                movement_pattern=MovementPattern.LINEAR
            ),
            TrackingObject(
                object_type=TrackingObjectType.VEHICLE,
                position=(400, 300),
                size=(50, 25),
                color=(255, 0, 0),
                movement_pattern=MovementPattern.CIRCULAR
            )
        ]
        
        for obj in dynamic_objects:
            camera_stream.add_tracking_object(obj)
        
        simulator.set_camera_stream(camera_stream)
        
        adaptation_successful = False
        try:
            simulator.start_simulation()
            
            # 環境変化シミュレーション
            change_phases = [
                # Phase 1: 高度変化による視野変更
                {"altitude": 3.0, "duration": 0.2},
                # Phase 2: さらに高高度
                {"altitude": 6.0, "duration": 0.2},
                # Phase 3: 低高度復帰
                {"altitude": 1.5, "duration": 0.2}
            ]
            
            for phase in change_phases:
                # ドローン高度変更
                simulator.current_state.position.z = phase["altitude"]
                simulator._update_camera_stream()
                
                # 指定時間維持
                time.sleep(phase["duration"])
                
                # フレーム取得確認
                frame = camera_stream.get_frame()
                if frame is not None:
                    assert frame.shape == (480, 640, 3)
                
                # 統計更新確認
                stats = simulator.get_statistics()
                assert abs(stats["current_position"][2] - phase["altitude"]) < 0.1
            
            adaptation_successful = True
            
        finally:
            simulator.stop_simulation()
            camera_stream.stop_stream() if hasattr(camera_stream, '_streaming') and camera_stream._streaming else None
        
        assert adaptation_successful == True


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])