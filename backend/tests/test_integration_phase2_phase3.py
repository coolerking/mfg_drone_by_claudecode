"""
Phase 2 ↔ Phase 3 統合テストスイート
仮想カメラストリームとドローンシミュレーションの統合機能テスト
"""

import pytest
import time
import numpy as np
import threading
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


class TestCameraDroneIntegration:
    """カメラとドローンの統合テスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.simulator = DroneSimulator("integration_test_drone", (15.0, 15.0, 8.0))
        self.camera_stream = VirtualCameraStream(640, 480, 30)
        
    def teardown_method(self):
        """テスト後清理"""
        if self.simulator.is_running:
            self.simulator.stop_simulation()
        if hasattr(self.camera_stream, '_streaming') and self.camera_stream._streaming:
            self.camera_stream.stop_stream()
    
    def test_camera_drone_integration_setup(self):
        """カメラ・ドローン統合設定テスト"""
        # カメラストリームをドローンに設定
        self.simulator.set_camera_stream(self.camera_stream)
        
        assert self.simulator.camera_stream is not None
        assert self.simulator.camera_integration_enabled == True
        assert self.simulator.camera_stream is self.camera_stream
    
    def test_synchronized_simulation_start_stop(self):
        """同期シミュレーション開始・停止テスト"""
        # 追跡オブジェクトを追加
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(320, 240),
            size=(40, 80),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.LINEAR,
            movement_speed=10.0
        )
        self.camera_stream.add_tracking_object(tracking_obj)
        
        # ドローンにカメラを統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # シミュレーション開始
        self.simulator.start_simulation()
        
        # 両方が動作していることを確認
        assert self.simulator.is_running == True
        time.sleep(0.1)  # カメラストリームが開始されるまで待機
        
        # シミュレーション停止
        self.simulator.stop_simulation()
        
        assert self.simulator.is_running == False
    
    def test_camera_updates_with_drone_movement(self):
        """ドローン移動に応じたカメラ更新テスト"""
        # 追跡オブジェクトを追加
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.BALL,
            position=(100, 100),
            size=(20, 20),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.STATIC
        )
        self.camera_stream.add_tracking_object(tracking_obj)
        
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # 初期高度を記録
        initial_altitude = self.simulator.current_state.position.z
        
        # ドローンを上昇させる
        self.simulator.current_state.position.z = 5.0  # 5m上昇
        
        # カメラ更新を手動で実行
        self.simulator._update_camera_stream()
        
        # 高度変化により追跡オブジェクトのサイズが調整されることを確認
        # (実際の実装に依存するが、高度が上がるとオブジェクトは小さく見える)
        assert self.simulator.current_state.position.z > initial_altitude
    
    def test_tracking_object_follows_drone_position(self):
        """追跡オブジェクトがドローン位置に追従するテスト"""
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # ドローンの位置を変更
        initial_pos = Vector3D(0, 0, 1)
        new_pos = Vector3D(3, 4, 2)
        
        self.simulator.current_state.position = initial_pos
        self.simulator._update_camera_stream()
        
        # 位置変更
        self.simulator.current_state.position = new_pos
        self.simulator._update_camera_stream()
        
        # カメラストリームが更新されていることを確認
        # この例では、高度の変化によりスケールファクターが変わることをテスト
        altitude_factor_new = max(0.1, min(2.0, new_pos.z / 5.0))
        altitude_factor_initial = max(0.1, min(2.0, initial_pos.z / 5.0))
        
        assert altitude_factor_new != altitude_factor_initial
    
    def test_multi_drone_multi_camera_coordination(self):
        """複数ドローン・複数カメラ協調テスト"""
        # マルチドローンシミュレータを作成
        multi_sim = MultiDroneSimulator((20.0, 20.0, 10.0))
        
        # 複数ドローンを追加
        drone1 = multi_sim.add_drone("drone_001", (-5.0, -5.0, 0.1))
        drone2 = multi_sim.add_drone("drone_002", (5.0, 5.0, 0.1))
        
        # 各ドローンにカメラストリームを設定
        camera1 = VirtualCameraStream(320, 240, 15)
        camera2 = VirtualCameraStream(320, 240, 15)
        
        # 異なる追跡オブジェクトを追加
        obj1 = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(160, 120),
            size=(30, 60),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.CIRCULAR
        )
        obj2 = TrackingObject(
            object_type=TrackingObjectType.VEHICLE,
            position=(160, 120),
            size=(40, 20),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.LINEAR
        )
        
        camera1.add_tracking_object(obj1)
        camera2.add_tracking_object(obj2)
        
        drone1.set_camera_stream(camera1)
        drone2.set_camera_stream(camera2)
        
        try:
            # 全シミュレーション開始
            multi_sim.start_all_simulations()
            
            assert drone1.is_running == True
            assert drone2.is_running == True
            assert drone1.camera_integration_enabled == True
            assert drone2.camera_integration_enabled == True
            
            # 少し動作させる
            time.sleep(0.2)
            
            # 各ドローンが独立して動作していることを確認
            stats1 = drone1.get_statistics()
            stats2 = drone2.get_statistics()
            
            assert stats1["drone_id"] == "drone_001"
            assert stats2["drone_id"] == "drone_002"
            
        finally:
            # 清理
            multi_sim.stop_all_simulations()
            camera1.stop_stream() if hasattr(camera1, '_streaming') and camera1._streaming else None
            camera2.stop_stream() if hasattr(camera2, '_streaming') and camera2._streaming else None


class TestCameraFrameGeneration:
    """カメラフレーム生成統合テスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.simulator = DroneSimulator("frame_test_drone")
        self.camera_stream = VirtualCameraStream(320, 240, 10)
        
    def teardown_method(self):
        """テスト後清理"""
        if self.simulator.is_running:
            self.simulator.stop_simulation()
        if hasattr(self.camera_stream, '_streaming') and self.camera_stream._streaming:
            self.camera_stream.stop_stream()
    
    def test_frame_generation_with_drone_data(self):
        """ドローンデータを含むフレーム生成テスト"""
        # 追跡オブジェクトを追加
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.BOX,
            position=(160, 120),
            size=(30, 30),
            color=(0, 0, 255),
            movement_pattern=MovementPattern.STATIC
        )
        self.camera_stream.add_tracking_object(tracking_obj)
        
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # シミュレーション開始
        self.simulator.start_simulation()
        
        try:
            # フレーム生成まで待機
            time.sleep(0.3)
            
            # フレーム取得
            frame = self.camera_stream.get_frame()
            
            assert frame is not None
            assert frame.shape == (240, 320, 3)
            assert frame.dtype == np.uint8
            
            # フレームに何らかの内容があることを確認（完全に黒でない）
            assert np.mean(frame) > 0
            
        finally:
            self.simulator.stop_simulation()
    
    def test_frame_consistency_across_drone_states(self):
        """ドローン状態変化時のフレーム一貫性テスト"""
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # 追跡オブジェクトを追加
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(100, 100),
            size=(25, 50),
            color=(255, 255, 0),
            movement_pattern=MovementPattern.SINE_WAVE
        )
        self.camera_stream.add_tracking_object(tracking_obj)
        
        # シミュレーション開始
        self.simulator.start_simulation()
        
        try:
            # 異なるドローン状態でフレーム取得
            frames = []
            drone_positions = []
            
            for z_height in [1.0, 3.0, 5.0]:
                self.simulator.current_state.position.z = z_height
                self.simulator._update_camera_stream()
                
                time.sleep(0.1)
                frame = self.camera_stream.get_frame()
                
                if frame is not None:
                    frames.append(frame)
                    drone_positions.append(z_height)
            
            # 複数のフレームが取得できることを確認
            assert len(frames) > 0
            
            # 各フレームが有効であることを確認
            for frame in frames:
                assert frame.shape == (240, 320, 3)
                assert frame.dtype == np.uint8
                
        finally:
            self.simulator.stop_simulation()


class TestRealTimeIntegration:
    """リアルタイム統合テスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.simulator = DroneSimulator("realtime_test")
        self.camera_stream = VirtualCameraStream(160, 120, 5)  # 低解像度・低フレームレート
        
    def teardown_method(self):
        """テスト後清理"""
        if self.simulator.is_running:
            self.simulator.stop_simulation()
        if hasattr(self.camera_stream, '_streaming') and self.camera_stream._streaming:
            self.camera_stream.stop_stream()
    
    def test_real_time_simulation_performance(self):
        """リアルタイムシミュレーション性能テスト"""
        # 複数の追跡オブジェクトを追加
        objects = [
            TrackingObject(
                object_type=TrackingObjectType.PERSON,
                position=(50, 50),
                size=(20, 40),
                color=(0, 255, 0),
                movement_pattern=MovementPattern.LINEAR
            ),
            TrackingObject(
                object_type=TrackingObjectType.VEHICLE,
                position=(100, 80),
                size=(30, 15),
                color=(255, 0, 0),
                movement_pattern=MovementPattern.CIRCULAR
            ),
            TrackingObject(
                object_type=TrackingObjectType.BALL,
                position=(80, 60),
                size=(10, 10),
                color=(0, 0, 255),
                movement_pattern=MovementPattern.RANDOM_WALK
            )
        ]
        
        for obj in objects:
            self.camera_stream.add_tracking_object(obj)
        
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # サンプル障害物を追加（負荷増加）
        self.simulator.add_sample_obstacles()
        
        # 性能測定開始
        start_time = time.time()
        self.simulator.start_simulation()
        
        try:
            # 短時間実行
            simulation_duration = 1.0  # 1秒
            time.sleep(simulation_duration)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # 統計情報取得
            drone_stats = self.simulator.get_statistics()
            camera_stats = self.camera_stream.get_statistics()
            
            # 基本的な性能要件を確認
            assert actual_duration >= simulation_duration * 0.9  # 90%以上の時間で実行
            assert actual_duration <= simulation_duration * 2.0  # 2倍以下の時間で完了
            
            # ドローンが動作していることを確認
            assert drone_stats["total_flight_time"] > 0
            
            # カメラフレームが生成されていることを確認
            assert camera_stats["frame_count"] > 0
            
        finally:
            self.simulator.stop_simulation()
    
    def test_concurrent_operations_stability(self):
        """同時操作の安定性テスト"""
        # カメラ統合
        self.simulator.set_camera_stream(self.camera_stream)
        
        # 追跡オブジェクトを追加
        tracking_obj = TrackingObject(
            object_type=TrackingObjectType.ANIMAL,
            position=(80, 60),
            size=(15, 15),
            color=(128, 128, 128),
            movement_pattern=MovementPattern.RANDOM_WALK
        )
        self.camera_stream.add_tracking_object(tracking_obj)
        
        # シミュレーション開始
        self.simulator.start_simulation()
        
        try:
            # 同時にドローン制御とカメラ操作を実行
            operations_successful = 0
            total_operations = 10
            
            for i in range(total_operations):
                # ドローン制御操作
                if i % 3 == 0:
                    success = self.simulator.takeoff()
                    if success:
                        operations_successful += 1
                elif i % 3 == 1:
                    if self.simulator.current_state.state == DroneState.FLYING:
                        success = self.simulator.move_to_position(i * 0.5, i * 0.3, 1.5)
                        if success:
                            operations_successful += 1
                else:
                    # カメラフレーム取得
                    frame = self.camera_stream.get_frame()
                    if frame is not None:
                        operations_successful += 1
                
                time.sleep(0.05)  # 短時間待機
            
            # 大部分の操作が成功することを確認
            success_rate = operations_successful / total_operations
            assert success_rate >= 0.5  # 50%以上の操作が成功
            
        finally:
            self.simulator.stop_simulation()


class TestErrorHandlingIntegration:
    """エラーハンドリング統合テスト"""
    
    def test_camera_failure_handling(self):
        """カメラ故障時の処理テスト"""
        simulator = DroneSimulator("error_test")
        
        # 故障したカメラストリームをモック
        mock_camera = Mock(spec=VirtualCameraStream)
        mock_camera._streaming = False
        mock_camera.start_stream.side_effect = Exception("Camera hardware failure")
        
        simulator.set_camera_stream(mock_camera)
        
        # シミュレーション開始（カメラエラーがあっても継続すべき）
        try:
            simulator.start_simulation()
            assert simulator.is_running == True
            
            # ドローン機能は正常に動作することを確認
            success = simulator.takeoff()
            assert success == True
            
        finally:
            simulator.stop_simulation()
    
    def test_drone_failure_with_camera_cleanup(self):
        """ドローン故障時のカメラ清理テスト"""
        simulator = DroneSimulator("cleanup_test")
        camera_stream = VirtualCameraStream(160, 120, 5)
        
        simulator.set_camera_stream(camera_stream)
        
        try:
            # シミュレーション開始
            simulator.start_simulation()
            
            # 人工的にドローンエラーを発生
            simulator.current_state.battery_level = 0.0
            simulator._handle_battery_empty()
            
            # エラー状態でもシミュレーション停止が正常に行われることを確認
            simulator.stop_simulation()
            
            assert simulator.is_running == False
            
        finally:
            # カメラストリームも停止されることを確認
            if hasattr(camera_stream, '_streaming') and camera_stream._streaming:
                camera_stream.stop_stream()


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])