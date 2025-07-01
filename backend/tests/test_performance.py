"""
パフォーマンステストスイート
長時間稼働・メモリリーク・ストレステスト
"""

import pytest
import time
import threading
import psutil
import gc
import sys
from typing import List, Dict, Any
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Vector3D, DroneState
)
from core.virtual_camera import (
    VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
)
from config.simulation_config import ConfigurationManager


class TestLongRunningSimulation:
    """長時間稼働テスト"""
    
    @pytest.mark.slow  # 時間のかかるテストマーク
    def test_24_hour_endurance_simulation(self):
        """24時間耐久シミュレーションテスト（短縮版）"""
        # 実際は24時間ではなく、比例縮小した短時間テスト
        simulation_duration = 60.0  # 60秒で24時間相当の負荷をテスト
        
        simulator = DroneSimulator("endurance_test", (20.0, 20.0, 10.0))
        
        # カメラ統合
        camera = VirtualCameraStream(320, 240, 15)
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(160, 120),
            size=(30, 60),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.RANDOM_WALK
        )
        camera.add_tracking_object(tracking_obj)
        simulator.set_camera_stream(camera)
        
        # 複数障害物を追加（負荷増加）
        simulator.add_sample_obstacles()
        
        # 初期メモリ使用量測定
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        endurance_success = False
        try:
            simulator.start_simulation()
            start_time = time.time()
            
            # 継続的なドローン操作
            waypoints = [
                (3.0, 3.0, 2.0),
                (-3.0, 3.0, 3.0),
                (-3.0, -3.0, 2.5),
                (3.0, -3.0, 1.5),
                (0.0, 0.0, 2.0)
            ]
            
            simulator.takeoff()
            time.sleep(0.2)
            simulator.current_state.state = DroneState.FLYING
            
            waypoint_index = 0
            last_move_time = start_time
            move_interval = 5.0  # 5秒ごとに移動
            
            while time.time() - start_time < simulation_duration:
                current_time = time.time()
                
                # 定期的な移動
                if current_time - last_move_time >= move_interval:
                    x, y, z = waypoints[waypoint_index % len(waypoints)]
                    simulator.move_to_position(x, y, z)
                    waypoint_index += 1
                    last_move_time = current_time
                
                # メモリ使用量監視
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                # メモリリーク検出（50MB以上増加で警告）
                if memory_increase > 50:
                    print(f"Warning: Memory increase detected: {memory_increase:.2f}MB")
                
                # CPU使用率確認
                cpu_percent = process.cpu_percent()
                if cpu_percent > 80:
                    print(f"Warning: High CPU usage: {cpu_percent:.1f}%")
                
                time.sleep(0.1)  # 短時間待機
            
            endurance_success = True
            
            # 最終統計確認
            final_stats = simulator.get_statistics()
            assert final_stats["total_flight_time"] > simulation_duration * 0.8
            assert final_stats["collision_count"] == 0
            
            # 最終メモリ確認
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # メモリ増加が合理的範囲内（100MB以下）
            assert memory_increase < 100, f"Excessive memory increase: {memory_increase:.2f}MB"
            
        finally:
            simulator.stop_simulation()
            camera.stop_stream() if hasattr(camera, '_streaming') and camera._streaming else None
        
        assert endurance_success == True
    
    def test_memory_leak_detection(self):
        """メモリリーク検出テスト"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 複数回のシミュレーション作成・破棄
        memory_samples = []
        
        for i in range(10):
            # シミュレータ作成
            simulator = DroneSimulator(f"leak_test_{i}")
            camera = VirtualCameraStream(160, 120, 10)
            
            # オブジェクト追加
            for j in range(5):
                obj = TrackingObject(
                    object_type=TrackingObjectType.BALL,
                    position=(j * 30 + 50, j * 20 + 40),
                    size=(15, 15),
                    color=(j * 50, 100, 200 - j * 40),
                    movement_pattern=MovementPattern.LINEAR
                )
                camera.add_tracking_object(obj)
            
            simulator.set_camera_stream(camera)
            
            # 短時間実行
            simulator.start_simulation()
            time.sleep(0.2)
            simulator.stop_simulation()
            
            camera.stop_stream() if hasattr(camera, '_streaming') and camera._streaming else None
            
            # 明示的な削除
            del simulator
            del camera
            
            # ガベージコレクション強制実行
            gc.collect()
            
            # メモリ使用量測定
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            
            time.sleep(0.1)  # GC完了待機
        
        # メモリ増加傾向分析
        memory_increase = memory_samples[-1] - memory_samples[0]
        
        # 合理的なメモリ増加範囲（20MB以下）
        assert memory_increase < 20, f"Potential memory leak: {memory_increase:.2f}MB increase"
        
        # メモリ使用量が安定していることを確認
        recent_avg = sum(memory_samples[-3:]) / 3
        early_avg = sum(memory_samples[:3]) / 3
        stability_ratio = abs(recent_avg - early_avg) / early_avg
        
        assert stability_ratio < 0.3, f"Memory usage unstable: {stability_ratio:.2f} ratio"


class TestStressTesting:
    """ストレステスト"""
    
    def test_maximum_drone_count(self):
        """最大ドローン数テスト"""
        multi_sim = MultiDroneSimulator((50.0, 50.0, 25.0))
        
        max_drones = 20  # テスト用最大数
        drones = []
        
        stress_success = False
        try:
            # 最大数までドローン追加
            for i in range(max_drones):
                drone = multi_sim.add_drone(
                    f"stress_drone_{i:02d}",
                    ((i % 5) * 8.0 - 20.0, (i // 5) * 8.0 - 20.0, 0.1)
                )
                drones.append(drone)
                
                # 各ドローンにカメラ追加
                camera = VirtualCameraStream(80, 60, 5)  # 低解像度
                obj = TrackingObject(
                    object_type=TrackingObjectType.PERSON,
                    position=(40, 30),
                    size=(10, 20),
                    color=(i * 10 % 255, 100, 150),
                    movement_pattern=MovementPattern.STATIC
                )
                camera.add_tracking_object(obj)
                drone.set_camera_stream(camera)
            
            # 全ドローン同時実行
            start_time = time.time()
            multi_sim.start_all_simulations()
            
            # 短時間高負荷運転
            time.sleep(1.0)
            
            # 全ドローンが動作していることを確認
            running_count = sum(1 for drone in drones if drone.is_running)
            assert running_count == max_drones
            
            # 統計取得性能
            stats_start = time.time()
            all_stats = multi_sim.get_all_statistics()
            stats_time = time.time() - stats_start
            
            assert len(all_stats) == max_drones
            assert stats_time < 1.0  # 1秒以内で統計取得
            
            # 同時離陸テスト
            takeoff_results = []
            for drone in drones[:5]:  # 最初の5台のみテスト
                result = drone.takeoff()
                takeoff_results.append(result)
            
            success_rate = sum(takeoff_results) / len(takeoff_results)
            assert success_rate >= 0.8  # 80%以上成功
            
            elapsed_time = time.time() - start_time
            assert elapsed_time < 10.0  # 10秒以内で完了
            
            stress_success = True
            
        finally:
            multi_sim.stop_all_simulations()
            # カメラストリーム停止
            for drone in drones:
                if drone.camera_stream and hasattr(drone.camera_stream, '_streaming'):
                    if drone.camera_stream._streaming:
                        drone.camera_stream.stop_stream()
        
        assert stress_success == True
    
    def test_high_frequency_commands(self):
        """高頻度コマンドテスト"""
        simulator = DroneSimulator("frequency_stress_test")
        simulator.current_state.state = DroneState.FLYING
        
        # 高頻度コマンド実行
        command_count = 1000
        successful_commands = 0
        failed_commands = 0
        
        start_time = time.time()
        
        for i in range(command_count):
            # 異なる種類のコマンドを高頻度実行
            command_type = i % 4
            
            try:
                if command_type == 0:
                    # 移動コマンド
                    x = (i % 10) * 0.1
                    y = (i % 8) * 0.1
                    z = 1.0 + (i % 5) * 0.1
                    success = simulator.move_to_position(x, y, z)
                elif command_type == 1:
                    # 回転コマンド
                    angle = (i % 360)
                    success = simulator.rotate_to_yaw(angle)
                elif command_type == 2:
                    # 統計取得
                    stats = simulator.get_statistics()
                    success = "drone_id" in stats
                else:
                    # 位置取得
                    pos = simulator.get_current_position()
                    success = len(pos) == 3
                
                if success:
                    successful_commands += 1
                else:
                    failed_commands += 1
                    
            except Exception:
                failed_commands += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        commands_per_second = command_count / total_time
        
        # 性能要件
        assert commands_per_second > 100, f"Low command rate: {commands_per_second:.1f} cmd/s"
        assert total_time < 30.0, f"Commands took too long: {total_time:.2f}s"
        
        # 成功率要件
        success_rate = successful_commands / command_count
        assert success_rate > 0.8, f"Low success rate: {success_rate:.2f}"
    
    def test_complex_obstacle_scenarios(self):
        """複雑障害物シナリオテスト"""
        simulator = DroneSimulator("obstacle_stress_test", (30.0, 30.0, 15.0))
        
        # 大量の複雑障害物を追加
        obstacle_count = 100
        
        for i in range(obstacle_count):
            from core.drone_simulator import Obstacle, ObstacleType
            
            # ランダムな位置とサイズ
            x = (i % 20) * 1.0 - 10.0
            y = ((i // 20) % 20) * 1.0 - 10.0
            z = (i % 5) * 2.0 + 1.0
            
            size_factor = 0.5 + (i % 10) * 0.1
            
            obstacle = Obstacle(
                id=f"stress_obstacle_{i}",
                obstacle_type=ObstacleType.DYNAMIC,
                position=Vector3D(x, y, z),
                size=Vector3D(size_factor, size_factor, size_factor * 2)
            )
            simulator.virtual_world.add_obstacle(obstacle)
        
        complex_success = False
        try:
            simulator.start_simulation()
            
            # 複雑環境でのナビゲーション
            simulator.takeoff()
            time.sleep(0.1)
            simulator.current_state.state = DroneState.FLYING
            
            # 障害物間の複雑経路
            complex_waypoints = [
                (5.0, 5.0, 3.0),
                (-5.0, 8.0, 5.0),
                (-8.0, -5.0, 4.0),
                (8.0, -8.0, 6.0),
                (0.0, 0.0, 8.0)
            ]
            
            collision_free_moves = 0
            total_moves = len(complex_waypoints)
            
            for x, y, z in complex_waypoints:
                move_success = simulator.move_to_position(x, y, z)
                if move_success:
                    collision_free_moves += 1
                time.sleep(0.1)
            
            # 衝突回避性能確認
            collision_avoidance_rate = collision_free_moves / total_moves
            
            # 統計確認
            final_stats = simulator.get_statistics()
            
            complex_success = True
            
            # 性能要件
            assert collision_avoidance_rate >= 0.6, f"Low avoidance rate: {collision_avoidance_rate:.2f}"
            assert final_stats["collision_count"] <= 5, f"Too many collisions: {final_stats['collision_count']}"
            
        finally:
            simulator.stop_simulation()
        
        assert complex_success == True


class TestFrameRateStability:
    """フレームレート安定性テスト"""
    
    def test_camera_fps_consistency(self):
        """カメラFPS一貫性テスト"""
        target_fps = 30
        camera = VirtualCameraStream(640, 480, target_fps)
        
        # 複数の動的オブジェクト追加
        for i in range(10):
            obj = TrackingObject(
                object_type=TrackingObjectType.PERSON if i % 2 == 0 else TrackingObjectType.VEHICLE,
                position=(i * 60 + 50, i * 40 + 100),
                size=(30, 50) if i % 2 == 0 else (40, 20),
                color=(i * 25, 150, 255 - i * 20),
                movement_pattern=MovementPattern.RANDOM_WALK if i % 3 == 0 else MovementPattern.CIRCULAR
            )
            camera.add_tracking_object(obj)
        
        fps_success = False
        try:
            camera.start_stream()
            
            # FPS測定
            measurement_duration = 5.0  # 5秒間測定
            frame_count = 0
            
            start_time = time.time()
            end_time = start_time + measurement_duration
            
            while time.time() < end_time:
                frame = camera.get_frame()
                if frame is not None:
                    frame_count += 1
                time.sleep(0.01)  # 短時間待機
            
            actual_duration = time.time() - start_time
            actual_fps = frame_count / actual_duration
            
            # FPS安定性確認
            fps_deviation = abs(actual_fps - target_fps) / target_fps
            
            fps_success = True
            
            # 性能要件（±20%以内）
            assert fps_deviation < 0.2, f"FPS unstable: {actual_fps:.1f} vs {target_fps} (deviation: {fps_deviation:.2f})"
            assert actual_fps >= target_fps * 0.5, f"FPS too low: {actual_fps:.1f}"
            
        finally:
            camera.stop_stream()
        
        assert fps_success == True
    
    def test_integrated_system_frame_rate(self):
        """統合システムフレームレートテスト"""
        simulator = DroneSimulator("fps_integration_test")
        camera = VirtualCameraStream(320, 240, 20)
        
        # 動的オブジェクト追加
        obj = TrackingObject(
            object_type=TrackingObjectType.ANIMAL,
            position=(160, 120),
            size=(25, 25),
            color=(128, 128, 255),
            movement_pattern=MovementPattern.SINE_WAVE
        )
        camera.add_tracking_object(obj)
        
        simulator.set_camera_stream(camera)
        simulator.add_sample_obstacles()
        
        integrated_success = False
        try:
            simulator.start_simulation()
            
            # 統合システムでのFPS測定
            measurement_time = 3.0
            frame_count = 0
            simulation_updates = 0
            
            start_time = time.time()
            last_stats_time = start_time
            
            simulator.takeoff()
            simulator.current_state.state = DroneState.FLYING
            
            while time.time() - start_time < measurement_time:
                # フレーム取得
                frame = camera.get_frame()
                if frame is not None:
                    frame_count += 1
                
                # ドローン操作
                current_time = time.time()
                if current_time - last_stats_time > 0.5:  # 0.5秒ごと
                    stats = simulator.get_statistics()
                    simulation_updates += 1
                    last_stats_time = current_time
                    
                    # 動的移動
                    if simulation_updates % 2 == 0:
                        simulator.move_to_position(
                            simulation_updates * 0.5,
                            simulation_updates * 0.3,
                            2.0
                        )
                
                time.sleep(0.01)
            
            actual_duration = time.time() - start_time
            achieved_fps = frame_count / actual_duration
            update_rate = simulation_updates / actual_duration
            
            integrated_success = True
            
            # 統合性能要件
            assert achieved_fps >= 10, f"Integrated FPS too low: {achieved_fps:.1f}"
            assert update_rate >= 1.5, f"Update rate too low: {update_rate:.1f}"
            
        finally:
            simulator.stop_simulation()
            camera.stop_stream() if hasattr(camera, '_streaming') and camera._streaming else None
        
        assert integrated_success == True


class TestCPUAndMemoryOptimization:
    """CPU・メモリ最適化テスト"""
    
    def test_cpu_usage_optimization(self):
        """CPU使用率最適化テスト"""
        process = psutil.Process()
        
        # CPU使用率測定開始
        process.cpu_percent()  # 初期化
        time.sleep(0.1)
        
        simulator = DroneSimulator("cpu_test")
        camera = VirtualCameraStream(320, 240, 15)
        simulator.set_camera_stream(camera)
        
        optimization_success = False
        try:
            simulator.start_simulation()
            
            # CPU集約的なタスク実行
            simulator.takeoff()
            time.sleep(0.1)
            simulator.current_state.state = DroneState.FLYING
            
            # 複数の同時操作
            operations = [
                lambda: simulator.move_to_position(1, 1, 2),
                lambda: simulator.rotate_to_yaw(45),
                lambda: simulator.get_statistics(),
                lambda: camera.get_frame(),
                lambda: simulator.move_to_position(2, 2, 3)
            ]
            
            # CPU使用率監視
            cpu_samples = []
            operation_start = time.time()
            
            for _ in range(20):  # 20回繰り返し
                for operation in operations:
                    try:
                        operation()
                    except Exception:
                        pass
                
                # CPU使用率サンプリング
                cpu_percent = process.cpu_percent()
                if cpu_percent > 0:  # 有効な値のみ
                    cpu_samples.append(cpu_percent)
                
                time.sleep(0.05)
            
            operation_time = time.time() - operation_start
            
            if cpu_samples:
                avg_cpu = sum(cpu_samples) / len(cpu_samples)
                max_cpu = max(cpu_samples)
                
                optimization_success = True
                
                # CPU使用率要件
                assert avg_cpu < 50, f"Average CPU too high: {avg_cpu:.1f}%"
                assert max_cpu < 80, f"Peak CPU too high: {max_cpu:.1f}%"
                assert operation_time < 5.0, f"Operations too slow: {operation_time:.2f}s"
            else:
                # CPU測定ができない環境での代替テスト
                optimization_success = operation_time < 10.0
                
        finally:
            simulator.stop_simulation()
            camera.stop_stream() if hasattr(camera, '_streaming') and camera._streaming else None
        
        assert optimization_success == True
    
    def test_memory_usage_efficiency(self):
        """メモリ使用効率テスト"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 複数のシミュレータを順次実行（メモリ効率テスト）
        efficiency_results = []
        
        for i in range(5):
            sim_start_memory = process.memory_info().rss / 1024 / 1024
            
            # シミュレータ作成・実行
            simulator = DroneSimulator(f"memory_eff_test_{i}")
            camera = VirtualCameraStream(160, 120, 10)
            
            # オブジェクト追加
            obj = TrackingObject(
                object_type=TrackingObjectType.BALL,
                position=(80, 60),
                size=(15, 15),
                color=(255, 100 + i * 30, 100),
                movement_pattern=MovementPattern.LINEAR
            )
            camera.add_tracking_object(obj)
            simulator.set_camera_stream(camera)
            
            # 実行
            simulator.start_simulation()
            time.sleep(0.5)
            simulator.stop_simulation()
            
            camera.stop_stream() if hasattr(camera, '_streaming') and camera._streaming else None
            
            # メモリ使用量測定
            peak_memory = process.memory_info().rss / 1024 / 1024
            memory_used = peak_memory - sim_start_memory
            
            efficiency_results.append(memory_used)
            
            # 明示的削除・ガベージ回収
            del simulator
            del camera
            gc.collect()
            time.sleep(0.1)
        
        # メモリ効率分析
        avg_memory_per_sim = sum(efficiency_results) / len(efficiency_results)
        max_memory_per_sim = max(efficiency_results)
        
        final_memory = process.memory_info().rss / 1024 / 1024
        total_memory_increase = final_memory - initial_memory
        
        # 効率要件
        assert avg_memory_per_sim < 30, f"Average memory per sim too high: {avg_memory_per_sim:.2f}MB"
        assert max_memory_per_sim < 50, f"Peak memory per sim too high: {max_memory_per_sim:.2f}MB"
        assert total_memory_increase < 20, f"Total memory increase too high: {total_memory_increase:.2f}MB"


if __name__ == "__main__":
    # テスト実行（時間のかかるテストは選択的に実行）
    pytest.main([__file__, "-v", "-m", "not slow"])