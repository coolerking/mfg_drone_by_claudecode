"""
設定統合テストスイート
YAML/JSON設定の読み込み・保存・検証テスト
"""

import pytest
import json
import yaml
import tempfile
import os
from typing import Dict, Any
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.simulation_config import (
    ConfigurationManager, PresetScenarios, SimulationConfig, 
    DroneConfig, ObstacleConfig, SimulationMode
)
from config.camera_config import (
    DynamicCameraScenarios, CameraScenarioConfig, configure_stream_from_scenario
)
from core.drone_simulator import DroneSimulator, MultiDroneSimulator, Vector3D
from core.virtual_camera import VirtualCameraStream, TrackingObjectType, MovementPattern


class TestConfigurationManager:
    """設定管理基本機能テスト"""
    
    def setup_method(self):
        """テスト前準備"""
        self.config_manager = ConfigurationManager()
        
    def test_preset_scenario_loading(self):
        """プリセットシナリオ読み込みテスト"""
        scenarios = ["empty_room", "obstacle_course", "multi_drone", "emergency"]
        
        for scenario_name in scenarios:
            config = self.config_manager.get_preset_scenario(scenario_name)
            
            assert isinstance(config, SimulationConfig)
            assert len(config.drones) > 0
            assert config.space_bounds is not None
            assert isinstance(config.simulation_mode, SimulationMode)
    
    def test_invalid_scenario_handling(self):
        """無効なシナリオ処理テスト"""
        with pytest.raises(ValueError, match="未知のシナリオ"):
            self.config_manager.get_preset_scenario("invalid_scenario_name")
    
    def test_config_file_round_trip_yaml(self):
        """YAML設定ファイル往復テスト"""
        # プリセット設定を取得
        original_config = self.config_manager.get_preset_scenario("multi_drone")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            # ファイルに保存
            self.config_manager.save_config_to_file(original_config, config_file)
            assert os.path.exists(config_file)
            
            # ファイルから読み込み
            loaded_config = self.config_manager.load_config_from_file(config_file)
            
            # 設定が一致することを確認
            assert loaded_config.simulation_mode == original_config.simulation_mode
            assert loaded_config.space_bounds == original_config.space_bounds
            assert len(loaded_config.drones) == len(original_config.drones)
            assert len(loaded_config.obstacles) == len(original_config.obstacles)
            
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)
    
    def test_config_file_round_trip_json(self):
        """JSON設定ファイル往復テスト"""
        original_config = self.config_manager.get_preset_scenario("obstacle_course")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            # ファイルに保存
            self.config_manager.save_config_to_file(original_config, config_file)
            
            # ファイルから読み込み
            loaded_config = self.config_manager.load_config_from_file(config_file)
            
            # 重要な設定が一致することを確認
            assert loaded_config.space_bounds == original_config.space_bounds
            assert len(loaded_config.obstacles) == len(original_config.obstacles)
            
            # 障害物設定の詳細比較
            for orig_obs, loaded_obs in zip(original_config.obstacles, loaded_config.obstacles):
                assert orig_obs.obstacle_id == loaded_obs.obstacle_id
                assert orig_obs.obstacle_type == loaded_obs.obstacle_type
                assert orig_obs.position == loaded_obs.position
                
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)
    
    def test_malformed_config_file_handling(self):
        """不正な設定ファイル処理テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # 不正なYAMLを書き込み
            f.write("invalid: yaml: content: [unclosed bracket")
            config_file = f.name
        
        try:
            with pytest.raises(Exception):
                self.config_manager.load_config_from_file(config_file)
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)


class TestSimulationConfigIntegration:
    """シミュレーション設定統合テスト"""
    
    def test_config_to_simulator_integration(self):
        """設定からシミュレータへの統合テスト"""
        config_manager = ConfigurationManager()
        config = config_manager.get_preset_scenario("empty_room")
        
        # 設定からシミュレータを作成
        drone_config = config.drones[0]
        simulator = DroneSimulator(
            drone_config.drone_id,
            config.space_bounds
        )
        
        # 初期位置設定
        simulator.current_state.position = Vector3D(*drone_config.initial_position)
        simulator.current_state.battery_level = drone_config.battery_level
        
        # 設定が正しく適用されることを確認
        assert simulator.drone_id == drone_config.drone_id
        assert simulator.current_state.position.x == drone_config.initial_position[0]
        assert simulator.current_state.position.y == drone_config.initial_position[1]
        assert simulator.current_state.position.z == drone_config.initial_position[2]
        assert simulator.current_state.battery_level == drone_config.battery_level
    
    def test_multi_drone_config_integration(self):
        """複数ドローン設定統合テスト"""
        config_manager = ConfigurationManager()
        config = config_manager.get_preset_scenario("multi_drone")
        
        # マルチドローンシミュレータを作成
        multi_sim = MultiDroneSimulator(config.space_bounds)
        
        # 設定からドローンを追加
        for drone_config in config.drones:
            drone = multi_sim.add_drone(
                drone_config.drone_id,
                drone_config.initial_position
            )
            drone.current_state.battery_level = drone_config.battery_level
        
        # 正しい数のドローンが追加されることを確認
        assert len(multi_sim.drones) == len(config.drones)
        
        # 各ドローンの設定が正しいことを確認
        for drone_config in config.drones:
            drone = multi_sim.drones[drone_config.drone_id]
            assert drone.drone_id == drone_config.drone_id
            assert drone.current_state.battery_level == drone_config.battery_level
    
    def test_obstacle_config_integration(self):
        """障害物設定統合テスト"""
        config_manager = ConfigurationManager()
        config = config_manager.get_preset_scenario("obstacle_course")
        
        simulator = DroneSimulator("test_drone", config.space_bounds)
        
        # 設定から障害物を追加
        for obs_config in config.obstacles:
            from core.drone_simulator import Obstacle, ObstacleType
            
            obstacle = Obstacle(
                id=obs_config.obstacle_id,
                obstacle_type=ObstacleType(obs_config.obstacle_type),
                position=Vector3D(*obs_config.position),
                size=Vector3D(*obs_config.size),
                is_static=obs_config.is_static
            )
            simulator.virtual_world.add_obstacle(obstacle)
        
        # 障害物が正しく追加されることを確認
        added_obstacles = len(simulator.virtual_world.obstacles)
        expected_obstacles = len(config.obstacles) + 6  # デフォルト境界壁 + 設定障害物
        assert added_obstacles == expected_obstacles


class TestCameraConfigIntegration:
    """カメラ設定統合テスト"""
    
    def test_camera_scenario_loading(self):
        """カメラシナリオ読み込みテスト"""
        scenarios = DynamicCameraScenarios.get_all_scenarios()
        
        expected_scenarios = ['indoor_tracking', 'outdoor_vehicle', 'sports_ball', 
                            'warehouse', 'emergency']
        
        for scenario_name in expected_scenarios:
            assert scenario_name in scenarios
            scenario = scenarios[scenario_name]
            
            assert isinstance(scenario, CameraScenarioConfig)
            assert scenario.name == scenario_name
            assert isinstance(scenario.description, str)
            assert len(scenario.tracking_objects) > 0
    
    def test_camera_stream_configuration(self):
        """カメラストリーム設定テスト"""
        scenario = DynamicCameraScenarios.get_indoor_tracking_scenario()
        stream = VirtualCameraStream(scenario.width, scenario.height, scenario.fps)
        
        # シナリオから設定を適用
        configured_stream = configure_stream_from_scenario(stream, scenario)
        
        assert configured_stream is stream
        assert stream.width == scenario.width
        assert stream.height == scenario.height
        assert stream.fps == scenario.fps
        assert len(stream.tracking_objects) == len(scenario.tracking_objects)
    
    def test_dynamic_scenario_creation(self):
        """動的シナリオ作成テスト"""
        custom_objects = [
            {
                'object_type': TrackingObjectType.ANIMAL,
                'position': (200, 150),
                'size': (25, 25),
                'color': (100, 100, 100),
                'movement_pattern': MovementPattern.CIRCULAR,
                'movement_speed': 5.0,
                'movement_params': {'radius': 50}
            }
        ]
        
        custom_scenario = DynamicCameraScenarios.create_custom_scenario(
            name="custom_test",
            description="Custom test scenario",
            objects_config=custom_objects,
            width=800,
            height=600,
            fps=24
        )
        
        assert custom_scenario.name == "custom_test"
        assert custom_scenario.width == 800
        assert custom_scenario.height == 600
        assert custom_scenario.fps == 24
        assert len(custom_scenario.tracking_objects) == 1


class TestFullConfigWorkflow:
    """完全設定ワークフローテスト"""
    
    def test_complete_system_configuration(self):
        """完全システム設定テスト"""
        # シミュレーション設定取得
        config_manager = ConfigurationManager()
        sim_config = config_manager.get_preset_scenario("multi_drone")
        
        # カメラ設定取得
        camera_scenario = DynamicCameraScenarios.get_warehouse_scenario()
        
        # システム統合
        multi_sim = MultiDroneSimulator(sim_config.space_bounds)
        
        # ドローンとカメラの統合設定
        drone_configs = sim_config.drones[:2]  # 最初の2台のみテスト
        
        for i, drone_config in enumerate(drone_configs):
            # ドローン追加
            drone = multi_sim.add_drone(
                drone_config.drone_id,
                drone_config.initial_position
            )
            
            # カメラが有効な場合のみカメラストリーム設定
            if drone_config.enable_camera:
                camera_stream = VirtualCameraStream(
                    *drone_config.camera_resolution,
                    drone_config.camera_fps
                )
                
                # カメラシナリオを適用（ドローンごとに異なる設定）
                if i == 0:
                    configure_stream_from_scenario(camera_stream, camera_scenario)
                else:
                    # 2台目は異なるシナリオ
                    alt_scenario = DynamicCameraScenarios.get_sports_ball_scenario()
                    configure_stream_from_scenario(camera_stream, alt_scenario)
                
                drone.set_camera_stream(camera_stream)
        
        # 統合システムが正常に構成されることを確認
        assert len(multi_sim.drones) == len(drone_configs)
        
        for drone_config in drone_configs:
            drone = multi_sim.drones[drone_config.drone_id]
            if drone_config.enable_camera:
                assert drone.camera_stream is not None
                assert drone.camera_integration_enabled == True
    
    def test_configuration_validation(self):
        """設定検証テスト"""
        config_manager = ConfigurationManager()
        
        # 各プリセットシナリオが有効であることを確認
        scenario_names = ["empty_room", "obstacle_course", "multi_drone", "emergency"]
        
        for scenario_name in scenario_names:
            config = config_manager.get_preset_scenario(scenario_name)
            
            # 基本検証
            assert config.space_bounds[0] > 0
            assert config.space_bounds[1] > 0
            assert config.space_bounds[2] > 0
            assert config.simulation_dt > 0
            
            # ドローン設定検証
            for drone_config in config.drones:
                assert drone_config.drone_id != ""
                assert 0 <= drone_config.battery_level <= 100
                assert drone_config.max_speed > 0
                assert drone_config.camera_fps > 0
                
                # 初期位置が空間境界内にあることを確認
                bounds = config.space_bounds
                assert -bounds[0]/2 <= drone_config.initial_position[0] <= bounds[0]/2
                assert -bounds[1]/2 <= drone_config.initial_position[1] <= bounds[1]/2
                assert 0 <= drone_config.initial_position[2] <= bounds[2]
            
            # 障害物設定検証
            for obs_config in config.obstacles:
                assert obs_config.obstacle_id != ""
                assert obs_config.obstacle_type in ["wall", "ceiling", "floor", "column", "dynamic"]
                assert all(size > 0 for size in obs_config.size)
    
    def test_config_file_error_recovery(self):
        """設定ファイルエラー回復テスト"""
        config_manager = ConfigurationManager()
        
        # 存在しないファイルの処理
        with pytest.raises(Exception):
            config_manager.load_config_from_file("nonexistent_file.yaml")
        
        # 不正なファイル形式の処理
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("{ invalid json }")
            invalid_file = f.name
        
        try:
            with pytest.raises(Exception):
                config_manager.load_config_from_file(invalid_file)
        finally:
            if os.path.exists(invalid_file):
                os.unlink(invalid_file)
        
        # エラー後も通常のプリセットシナリオが使用可能であることを確認
        config = config_manager.get_preset_scenario("empty_room")
        assert isinstance(config, SimulationConfig)


class TestConfigurationPerformance:
    """設定性能テスト"""
    
    def test_large_config_loading_performance(self):
        """大きな設定ファイル読み込み性能テスト"""
        import time
        
        # 大きな設定を作成
        large_config = SimulationConfig()
        large_config.space_bounds = (50.0, 50.0, 25.0)
        
        # 多数のドローンを追加
        for i in range(20):
            drone = DroneConfig(
                drone_id=f"drone_{i:03d}",
                initial_position=(i * 2.0, i * 1.5, 0.1),
                enable_camera=True
            )
            large_config.drones.append(drone)
        
        # 多数の障害物を追加
        for i in range(50):
            obstacle = ObstacleConfig(
                obstacle_id=f"obstacle_{i:03d}",
                obstacle_type="dynamic",
                position=(i * 0.8, i * 0.6, 1.0),
                size=(0.5, 0.5, 1.0)
            )
            large_config.obstacles.append(obstacle)
        
        config_manager = ConfigurationManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            # 保存性能測定
            start_time = time.time()
            config_manager.save_config_to_file(large_config, config_file)
            save_time = time.time() - start_time
            
            # 読み込み性能測定
            start_time = time.time()
            loaded_config = config_manager.load_config_from_file(config_file)
            load_time = time.time() - start_time
            
            # 性能要件（大きな設定でも数秒以内）
            assert save_time < 5.0, f"Save took too long: {save_time:.2f}s"
            assert load_time < 5.0, f"Load took too long: {load_time:.2f}s"
            
            # 正確性確認
            assert len(loaded_config.drones) == 20
            assert len(loaded_config.obstacles) == 50
            
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])