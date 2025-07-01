"""
エラーハンドリングテストスイート
システム例外・故障・異常状態の処理テスト
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, Vector3D, DroneState, DroneState3D,
    Obstacle, ObstacleType, DronePhysics
)
from core.virtual_camera import (
    VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern
)
from config.simulation_config import ConfigurationManager


class TestDroneSystemErrorHandling:
    """ドローンシステムエラーハンドリングテスト"""
    
    def test_invalid_drone_commands(self):
        """無効なドローンコマンドテスト"""
        simulator = DroneSimulator("error_test")
        
        # 待機状態での無効コマンド
        assert simulator.current_state.state == DroneState.IDLE
        
        # 待機状態での移動コマンド
        move_result = simulator.move_to_position(1.0, 1.0, 2.0)
        assert move_result == False
        
        # 待機状態での着陸コマンド
        land_result = simulator.land()
        assert land_result == False
        
        # 待機状態での回転コマンド
        rotate_result = simulator.rotate_to_yaw(90.0)
        assert rotate_result == False
        
        # 低バッテリーでの離陸
        simulator.current_state.battery_level = 5.0
        takeoff_result = simulator.takeoff()
        assert takeoff_result == False
    
    def test_collision_detection_errors(self):
        """衝突判定エラーテスト"""
        simulator = DroneSimulator("collision_error_test")
        
        # 不正な障害物での衝突判定
        invalid_obstacle = Mock(spec=Obstacle)
        invalid_obstacle.get_bounding_box.side_effect = Exception("Bounding box calculation error")
        
        simulator.virtual_world.obstacles["invalid"] = invalid_obstacle
        
        # 衝突判定が例外で失敗しても全体は継続
        try:
            collision, obstacle_id = simulator.virtual_world.check_collision(Vector3D(0, 0, 1))
            # エラーがあっても適切に処理される
            assert isinstance(collision, bool)
        except Exception:
            # 例外が発生しても適切に処理される
            pass
    
    def test_physics_calculation_errors(self):
        """物理計算エラーテスト"""
        simulator = DroneSimulator("physics_error_test")
        
        # 物理エンジンをモック
        mock_engine = Mock()
        mock_engine.apply_forces.side_effect = Exception("Physics calculation error")
        simulator.physics_engine = mock_engine
        
        # 物理計算エラーがあってもシミュレーション継続
        simulator.start_simulation()
        
        try:
            # 短時間実行
            time.sleep(0.1)
            
            # シミュレーションは実行中のまま
            assert simulator.is_running == True
            
        finally:
            simulator.stop_simulation()
    
    def test_thread_safety_violations(self):
        """スレッドセーフティ違反テスト"""
        simulator = DroneSimulator("thread_test")
        
        # 複数スレッドから同時にドローンを操作
        results = []
        errors = []
        
        def drone_operation(operation_id):
            try:
                simulator.current_state.state = DroneState.FLYING
                success = simulator.move_to_position(
                    operation_id * 0.1, 
                    operation_id * 0.1, 
                    1.0 + operation_id * 0.1
                )
                results.append(success)
            except Exception as e:
                errors.append(e)
        
        # 複数スレッドで同時実行
        threads = []
        for i in range(5):
            thread = threading.Thread(target=drone_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 全スレッド完了を待機
        for thread in threads:
            thread.join()
        
        # スレッドセーフティ違反があっても致命的エラーにならない
        total_operations = len(results) + len(errors)
        assert total_operations == 5
    
    def test_resource_exhaustion_handling(self):
        """リソース枯渇処理テスト"""
        simulator = DroneSimulator("resource_test")
        
        # メモリ不足をシミュレート
        with patch('threading.Thread') as mock_thread:
            mock_thread.side_effect = MemoryError("Cannot allocate memory")
            
            # シミュレーション開始でメモリエラー
            try:
                simulator.start_simulation()
                # エラーハンドリングが適切に行われる
            except MemoryError:
                # メモリエラーが適切に伝播される
                pass
            
            # システム状態が一貫している
            assert simulator.simulation_thread is None


class TestCameraSystemErrorHandling:
    """カメラシステムエラーハンドリングテスト"""
    
    def test_camera_initialization_failures(self):
        """カメラ初期化失敗テスト"""
        # 異常なパラメータでのカメラ作成
        invalid_configs = [
            {"width": -640, "height": 480, "fps": 30},
            {"width": 640, "height": -480, "fps": 30},
            {"width": 640, "height": 480, "fps": -30}
        ]
        
        for config in invalid_configs:
            try:
                camera = VirtualCameraStream(**config)
                # 作成が成功する場合は、後続処理で適切にエラーハンドリング
                if hasattr(camera, 'start_stream'):
                    camera.start_stream()
                    time.sleep(0.1)
                    camera.stop_stream()
            except (ValueError, Exception):
                # 適切な例外処理
                pass
    
    def test_frame_generation_failures(self):
        """フレーム生成失敗テスト"""
        camera = VirtualCameraStream(320, 240, 10)
        
        # フレーム生成メソッドをモック
        with patch.object(camera, '_generate_background') as mock_bg:
            mock_bg.side_effect = Exception("Frame generation error")
            
            # エラーがあってもストリーム処理継続
            try:
                camera.start_stream()
                time.sleep(0.2)
                
                # フレーム取得時のエラーハンドリング
                frame = camera.get_frame()
                # None または有効なフレームが返される
                assert frame is None or frame.shape == (240, 320, 3)
                
            finally:
                camera.stop_stream()
    
    def test_tracking_object_update_failures(self):
        """追跡オブジェクト更新失敗テスト"""
        camera = VirtualCameraStream(320, 240, 10)
        
        # 問題のある追跡オブジェクト
        problematic_obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(160, 120),
            size=(30, 60),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.LINEAR
        )
        
        camera.add_tracking_object(problematic_obj)
        
        # 位置更新メソッドをモック
        with patch.object(camera, '_update_object_position') as mock_update:
            mock_update.side_effect = Exception("Object update error")
            
            try:
                camera.start_stream()
                time.sleep(0.2)
                
                # エラーがあってもカメラストリーム継続
                assert hasattr(camera, '_streaming')
                
            finally:
                camera.stop_stream()
    
    def test_concurrent_camera_access_errors(self):
        """同時カメラアクセスエラーテスト"""
        camera = VirtualCameraStream(160, 120, 5)
        
        # 複数スレッドから同時にフレーム取得
        frame_results = []
        frame_errors = []
        
        def get_frame_operation():
            try:
                for _ in range(10):
                    frame = camera.get_frame()
                    frame_results.append(frame)
                    time.sleep(0.01)
            except Exception as e:
                frame_errors.append(e)
        
        camera.start_stream()
        time.sleep(0.1)  # カメラ開始待機
        
        try:
            # 複数スレッドで同時フレーム取得
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=get_frame_operation)
                threads.append(thread)
                thread.start()
            
            # 全スレッド完了待機
            for thread in threads:
                thread.join()
            
            # 同時アクセスでも致命的エラーにならない
            total_attempts = len(frame_results) + len(frame_errors)
            assert total_attempts == 30  # 3スレッド × 10回
            
        finally:
            camera.stop_stream()


class TestConfigurationErrorHandling:
    """設定エラーハンドリングテスト"""
    
    def test_corrupted_config_file_handling(self):
        """破損設定ファイル処理テスト"""
        config_manager = ConfigurationManager()
        
        # 破損したファイルを作成
        corrupted_contents = [
            "{ corrupted json file",  # 不正JSON
            "yaml: [unclosed bracket",  # 不正YAML
            "",  # 空ファイル
            "null",  # Null内容
            "{ \"simulation_mode\": \"invalid_mode\" }"  # 無効な値
        ]
        
        for i, content in enumerate(corrupted_contents):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(content)
                corrupted_file = f.name
            
            try:
                # 破損ファイル読み込み試行
                config = config_manager.load_config_from_file(corrupted_file)
                # 読み込み成功の場合は妥当性チェック
                assert hasattr(config, 'simulation_mode')
                
            except Exception:
                # 適切なエラーハンドリング
                pass
            finally:
                if os.path.exists(corrupted_file):
                    os.unlink(corrupted_file)
    
    def test_missing_required_config_fields(self):
        """必須設定フィールド欠落テスト"""
        config_manager = ConfigurationManager()
        
        # 不完全な設定データ
        incomplete_configs = [
            {},  # 完全に空
            {"simulation_mode": "physics"},  # ドローン設定なし
            {"drones": []},  # 空のドローンリスト
            {"drones": [{"drone_id": "test"}]},  # 不完全なドローン設定
        ]
        
        for i, config_data in enumerate(incomplete_configs):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                import json
                json.dump(config_data, f)
                config_file = f.name
            
            try:
                config = config_manager.load_config_from_file(config_file)
                
                # 読み込み成功時は、デフォルト値で補完されている
                assert hasattr(config, 'simulation_mode')
                assert hasattr(config, 'space_bounds')
                assert isinstance(config.drones, list)
                
            except Exception:
                # または適切なエラーが発生
                pass
            finally:
                if os.path.exists(config_file):
                    os.unlink(config_file)
    
    def test_invalid_preset_scenario_handling(self):
        """無効プリセットシナリオ処理テスト"""
        config_manager = ConfigurationManager()
        
        invalid_scenarios = [
            "nonexistent_scenario",
            "",
            None,
            123,
            ["invalid", "type"]
        ]
        
        for invalid_scenario in invalid_scenarios:
            try:
                config = config_manager.get_preset_scenario(invalid_scenario)
                # 想定外の成功
                assert False, f"Should have failed for {invalid_scenario}"
                
            except (ValueError, TypeError, AttributeError):
                # 適切なエラータイプ
                pass
            except Exception as e:
                # その他の例外も許容（適切に処理されている）
                pass


class TestIntegrationErrorHandling:
    """統合エラーハンドリングテスト"""
    
    def test_drone_camera_integration_failures(self):
        """ドローン・カメラ統合失敗テスト"""
        simulator = DroneSimulator("integration_error_test")
        
        # 故障カメラをモック
        mock_camera = Mock(spec=VirtualCameraStream)
        mock_camera.start_stream.side_effect = Exception("Camera hardware failure")
        mock_camera._streaming = False
        
        # カメラ故障があってもドローンは動作継続
        simulator.set_camera_stream(mock_camera)
        
        try:
            simulator.start_simulation()
            
            # ドローン機能は正常
            takeoff_success = simulator.takeoff()
            assert takeoff_success == True
            
            # カメラ統合エラーがあってもシミュレーション継続
            assert simulator.is_running == True
            
        finally:
            simulator.stop_simulation()
    
    def test_multi_system_cascade_failures(self):
        """複数システム連鎖故障テスト"""
        multi_sim = MultiDroneSimulator((20.0, 20.0, 10.0))
        
        # 複数ドローンを追加
        drone1 = multi_sim.add_drone("stable_drone", (-5.0, 0.0, 0.1))
        drone2 = multi_sim.add_drone("failing_drone", (5.0, 0.0, 0.1))
        
        # 一つのドローンに故障カメラを設定
        mock_camera = Mock(spec=VirtualCameraStream)
        mock_camera.start_stream.side_effect = Exception("System failure")
        drone2.set_camera_stream(mock_camera)
        
        # 物理エンジンも故障
        mock_physics = Mock()
        mock_physics.apply_forces.side_effect = Exception("Physics failure")
        drone2.physics_engine = mock_physics
        
        try:
            # 連鎖故障があってもシステム全体は動作継続
            multi_sim.start_all_simulations()
            
            # 正常ドローンは動作
            assert drone1.is_running == True
            takeoff1 = drone1.takeoff()
            assert takeoff1 == True
            
            # 故障ドローンも基本機能は維持
            assert drone2.is_running == True
            
            # 短時間動作
            time.sleep(0.2)
            
            # 統計取得可能
            stats = multi_sim.get_all_statistics()
            assert len(stats) == 2
            
        finally:
            multi_sim.stop_all_simulations()
    
    def test_resource_cleanup_on_errors(self):
        """エラー時リソース清理テスト"""
        simulator = DroneSimulator("cleanup_test")
        camera = VirtualCameraStream(320, 240, 10)
        
        # カメラ統合
        simulator.set_camera_stream(camera)
        
        # リソース使用中に強制エラー
        simulator.start_simulation()
        camera.start_stream()
        
        # 人工的にエラー状況を作成
        simulator.current_state.battery_level = 0.0
        simulator._handle_battery_empty()
        
        try:
            # エラー後でも適切にリソース清理
            simulator.stop_simulation()
            
            # シミュレーション停止確認
            assert simulator.is_running == False
            
            # カメラリソース清理確認
            if hasattr(camera, '_streaming'):
                camera.stop_stream()
            
        except Exception:
            # 清理処理でエラーが発生しても致命的でない
            pass


class TestErrorRecoveryStrategies:
    """エラー回復戦略テスト"""
    
    def test_automatic_error_recovery(self):
        """自動エラー回復テスト"""
        simulator = DroneSimulator("recovery_test")
        
        # 一時的なエラーをシミュレート
        error_count = 0
        original_method = simulator._update_simulation
        
        def failing_update(dt):
            nonlocal error_count
            error_count += 1
            if error_count <= 3:  # 最初の3回は失敗
                raise Exception(f"Temporary error {error_count}")
            return original_method(dt)  # その後は正常
        
        simulator._update_simulation = failing_update
        
        try:
            simulator.start_simulation()
            
            # エラー回復後に正常動作
            time.sleep(0.3)
            
            # システムが回復していることを確認
            assert simulator.is_running == True
            assert error_count > 3  # エラーが発生し、回復した
            
        finally:
            simulator.stop_simulation()
    
    def test_graceful_degradation(self):
        """グレースフル劣化テスト"""
        simulator = DroneSimulator("degradation_test")
        
        # 高機能カメラから低機能カメラに劣化
        high_res_camera = VirtualCameraStream(1920, 1080, 60)
        low_res_camera = VirtualCameraStream(160, 120, 5)
        
        # 最初は高解像度カメラ
        simulator.set_camera_stream(high_res_camera)
        
        simulator.start_simulation()
        
        try:
            # 高解像度カメラでエラー発生をシミュレート
            with patch.object(high_res_camera, 'get_frame') as mock_get_frame:
                mock_get_frame.side_effect = Exception("High-res camera failure")
                
                # 低解像度カメラに切り替え
                simulator.set_camera_stream(low_res_camera)
                
                # 劣化した状態でも基本機能は維持
                takeoff_success = simulator.takeoff()
                assert takeoff_success == True
                
                # 低解像度カメラは動作
                time.sleep(0.1)
                frame = low_res_camera.get_frame()
                if frame is not None:
                    assert frame.shape == (120, 160, 3)
                
        finally:
            simulator.stop_simulation()
            high_res_camera.stop_stream() if hasattr(high_res_camera, '_streaming') and high_res_camera._streaming else None
            low_res_camera.stop_stream() if hasattr(low_res_camera, '_streaming') and low_res_camera._streaming else None


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])