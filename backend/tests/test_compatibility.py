"""
環境互換性テストスイート
異なるOS・Pythonバージョン・依存ライブラリ互換性テスト
"""

import pytest
import sys
import platform
import importlib
from unittest.mock import Mock, patch
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.drone_simulator import DroneSimulator, Vector3D, DroneState
from core.virtual_camera import VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern


class TestPythonVersionCompatibility:
    """Pythonバージョン互換性テスト"""
    
    def test_python_version_support(self):
        """対応Pythonバージョンテスト"""
        # Python 3.8以上をサポート
        python_version = sys.version_info
        
        assert python_version.major == 3, f"Python 3.x required, got {python_version.major}.x"
        assert python_version.minor >= 8, f"Python 3.8+ required, got 3.{python_version.minor}"
        
        # バージョン情報を記録
        version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        print(f"Testing on Python {version_str}")
    
    def test_dataclass_compatibility(self):
        """dataclass互換性テスト（Python 3.7+）"""
        from dataclasses import dataclass, field
        
        @dataclass
        class TestConfig:
            name: str
            values: List[float] = field(default_factory=list)
            settings: Dict[str, Any] = field(default_factory=dict)
        
        # dataclass基本機能
        config = TestConfig("test", [1.0, 2.0], {"key": "value"})
        assert config.name == "test"
        assert config.values == [1.0, 2.0]
        assert config.settings["key"] == "value"
    
    def test_typing_annotations_compatibility(self):
        """型ヒント互換性テスト"""
        from typing import Optional, Union, Dict, List, Tuple
        
        def test_function(
            param1: str,
            param2: Optional[int] = None,
            param3: Union[str, int] = "default",
            param4: Dict[str, Any] = None,
            param5: List[float] = None,
            param6: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        ) -> bool:
            return True
        
        # 型ヒント付き関数の動作確認
        result = test_function("test")
        assert result == True
        
        result = test_function("test", 42, 100, {"a": 1}, [1.0, 2.0], (1.0, 2.0, 3.0))
        assert result == True


class TestOSCompatibility:
    """OS互換性テスト"""
    
    def test_platform_detection(self):
        """プラットフォーム検出テスト"""
        system = platform.system()
        machine = platform.machine()
        
        # サポートプラットフォーム
        supported_systems = ["Windows", "Linux", "Darwin"]  # Darwin = macOS
        
        print(f"Platform: {system} {machine}")
        print(f"Python implementation: {platform.python_implementation()}")
        
        if system not in supported_systems:
            pytest.skip(f"Platform {system} not officially supported")
    
    def test_file_path_compatibility(self):
        """ファイルパス互換性テスト"""
        import tempfile
        import os
        
        # 一時ディレクトリでのパス操作
        with tempfile.TemporaryDirectory() as temp_dir:
            # パス結合テスト
            test_path = os.path.join(temp_dir, "test_config.json")
            
            # ファイル作成・読み書きテスト
            test_content = '{"test": "value"}'
            
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # ファイル存在確認
            assert os.path.exists(test_path)
            
            # ファイル読み込み
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert content == test_content
    
    def test_multiprocessing_compatibility(self):
        """マルチプロセシング互換性テスト"""
        import threading
        import multiprocessing
        
        # スレッド作成テスト
        result = []
        
        def thread_function():
            result.append("thread_executed")
        
        thread = threading.Thread(target=thread_function)
        thread.start()
        thread.join()
        
        assert "thread_executed" in result
        
        # マルチプロセシング基本機能テスト
        cpu_count = multiprocessing.cpu_count()
        assert cpu_count > 0
        
        print(f"CPU cores: {cpu_count}")


class TestDependencyCompatibility:
    """依存ライブラリ互換性テスト"""
    
    def test_numpy_compatibility(self):
        """NumPy互換性テスト"""
        import numpy as np
        
        # バージョン確認
        numpy_version = np.__version__
        print(f"NumPy version: {numpy_version}")
        
        # 基本機能テスト
        array = np.array([1.0, 2.0, 3.0])
        assert array.shape == (3,)
        assert np.mean(array) == 2.0
        
        # 数学関数テスト
        assert np.isclose(np.sqrt(4.0), 2.0)
        assert np.isfinite(1.0)
        assert not np.isnan(1.0)
        
        # データ型テスト
        float_array = np.array([1.0, 2.0], dtype=np.float64)
        assert float_array.dtype == np.float64
    
    def test_opencv_compatibility(self):
        """OpenCV互換性テスト"""
        try:
            import cv2
            
            # バージョン確認
            opencv_version = cv2.__version__
            print(f"OpenCV version: {opencv_version}")
            
            # 基本画像操作テスト
            import numpy as np
            
            # 空白画像作成
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            assert image.shape == (100, 100, 3)
            
            # 基本描画機能テスト
            cv2.rectangle(image, (10, 10), (50, 50), (255, 0, 0), -1)
            cv2.circle(image, (75, 75), 10, (0, 255, 0), -1)
            
            # 画像が変更されていることを確認
            assert np.sum(image) > 0
            
        except ImportError:
            pytest.skip("OpenCV not available")
    
    def test_matplotlib_compatibility(self):
        """Matplotlib互換性テスト"""
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            
            # バージョン確認
            mpl_version = matplotlib.__version__
            print(f"Matplotlib version: {mpl_version}")
            
            # 非GUI バックエンド設定
            matplotlib.use('Agg')
            
            # 基本プロット機能テスト
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 2])
            ax.set_title("Test Plot")
            
            # プロット作成確認
            assert len(ax.lines) == 1
            
            plt.close(fig)  # メモリリーク防止
            
        except ImportError:
            pytest.skip("Matplotlib not available")
    
    def test_scipy_compatibility(self):
        """SciPy互換性テスト"""
        try:
            import scipy
            from scipy.spatial.distance import cdist
            import numpy as np
            
            # バージョン確認
            scipy_version = scipy.__version__
            print(f"SciPy version: {scipy_version}")
            
            # 基本機能テスト
            points1 = np.array([[0, 0], [1, 1]])
            points2 = np.array([[0, 1], [1, 0]])
            
            distances = cdist(points1, points2)
            assert distances.shape == (2, 2)
            
            # 距離計算の妥当性確認
            assert distances[0, 0] == 1.0  # (0,0) to (0,1)
            
        except ImportError:
            pytest.skip("SciPy not available")
    
    def test_shapely_compatibility(self):
        """Shapely互換性テスト"""
        try:
            from shapely.geometry import Point, Polygon
            
            # 基本ジオメトリ操作テスト
            point = Point(0.5, 0.5)
            polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
            
            # 包含判定テスト
            assert polygon.contains(point)
            
            # 面積計算テスト
            assert polygon.area == 1.0
            
        except ImportError:
            pytest.skip("Shapely not available")
    
    def test_yaml_compatibility(self):
        """PyYAML互換性テスト"""
        try:
            import yaml
            
            # YAML読み書きテスト
            test_data = {
                "simulation": {
                    "mode": "physics",
                    "drones": [
                        {"id": "drone_1", "position": [0, 0, 1]}
                    ]
                }
            }
            
            # YAML文字列に変換
            yaml_str = yaml.dump(test_data)
            assert "simulation:" in yaml_str
            
            # YAML文字列から復元
            loaded_data = yaml.safe_load(yaml_str)
            assert loaded_data["simulation"]["mode"] == "physics"
            
        except ImportError:
            pytest.skip("PyYAML not available")


class TestSystemIntegrationCompatibility:
    """システム統合互換性テスト"""
    
    def test_basic_simulator_functionality(self):
        """基本シミュレータ機能互換性テスト"""
        # 現在の環境でのシミュレータ動作確認
        simulator = DroneSimulator("compatibility_test")
        
        # 基本操作テスト
        assert simulator.drone_id == "compatibility_test"
        assert simulator.current_state.state == DroneState.IDLE
        
        # 離陸テスト
        takeoff_success = simulator.takeoff()
        assert takeoff_success == True
        
        # 位置取得テスト
        position = simulator.get_current_position()
        assert len(position) == 3
        assert all(isinstance(p, (int, float)) for p in position)
    
    def test_camera_functionality_compatibility(self):
        """カメラ機能互換性テスト"""
        # 現在の環境でのカメラ動作確認
        camera = VirtualCameraStream(320, 240, 10)
        
        # 追跡オブジェクト追加
        obj = TrackingObject(
            object_type=TrackingObjectType.BALL,
            position=(160, 120),
            size=(20, 20),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.STATIC
        )
        camera.add_tracking_object(obj)
        
        # ストリーム開始
        try:
            camera.start_stream()
            
            # 短時間待機
            import time
            time.sleep(0.2)
            
            # フレーム取得テスト
            frame = camera.get_frame()
            if frame is not None:
                assert frame.shape == (240, 320, 3)
                assert frame.dtype.name.startswith('uint')
            
        finally:
            camera.stop_stream()
    
    def test_configuration_compatibility(self):
        """設定機能互換性テスト"""
        from config.simulation_config import ConfigurationManager
        
        config_manager = ConfigurationManager()
        
        # プリセットシナリオ読み込み
        config = config_manager.get_preset_scenario("empty_room")
        
        # 設定オブジェクトの妥当性確認
        assert hasattr(config, 'simulation_mode')
        assert hasattr(config, 'space_bounds')
        assert hasattr(config, 'drones')
        assert len(config.drones) > 0


class TestPerformanceCharacteristics:
    """性能特性テスト（環境別）"""
    
    def test_platform_specific_performance(self):
        """プラットフォーム固有性能テスト"""
        import time
        import platform
        
        system = platform.system()
        
        # 簡単な性能ベンチマーク
        simulator = DroneSimulator("perf_test")
        
        # タイミング測定
        start_time = time.time()
        
        # 基本操作の実行時間測定
        operations = [
            lambda: simulator.takeoff(),
            lambda: simulator.get_current_position(),
            lambda: simulator.get_statistics(),
            lambda: Vector3D(1, 2, 3).magnitude(),
            lambda: Vector3D(3, 4, 0).normalize()
        ]
        
        for operation in operations:
            operation()
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # プラットフォーム別性能期待値
        if system == "Linux":
            max_expected_time = 0.1  # Linux: 100ms以内
        elif system == "Windows":
            max_expected_time = 0.2  # Windows: 200ms以内
        elif system == "Darwin":  # macOS
            max_expected_time = 0.15  # macOS: 150ms以内
        else:
            max_expected_time = 0.5  # その他: 500ms以内
        
        print(f"Platform {system}: Operations took {operation_time:.3f}s")
        assert operation_time < max_expected_time, f"Performance too slow on {system}: {operation_time:.3f}s"
    
    def test_memory_behavior_by_platform(self):
        """プラットフォーム別メモリ動作テスト"""
        try:
            import psutil
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # メモリ使用テスト
            simulators = []
            for i in range(5):
                sim = DroneSimulator(f"mem_test_{i}")
                simulators.append(sim)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = peak_memory - initial_memory
            
            # 清理
            del simulators
            import gc
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_released = peak_memory - final_memory
            
            print(f"Memory used: {memory_used:.2f}MB, released: {memory_released:.2f}MB")
            
            # メモリ効率要件
            assert memory_used < 50, f"Memory usage too high: {memory_used:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")


class TestBackwardCompatibility:
    """後方互換性テスト"""
    
    def test_legacy_api_compatibility(self):
        """旧API互換性テスト"""
        # 基本的なAPIが変更されていないことを確認
        simulator = DroneSimulator("legacy_test")
        
        # 旧来のメソッドが存在することを確認
        assert hasattr(simulator, 'takeoff')
        assert hasattr(simulator, 'land')
        assert hasattr(simulator, 'move_to_position')
        assert hasattr(simulator, 'get_current_position')
        assert hasattr(simulator, 'get_battery_level')
        assert hasattr(simulator, 'get_statistics')
        
        # メソッドが呼び出し可能であることを確認
        assert callable(simulator.takeoff)
        assert callable(simulator.land)
        assert callable(simulator.move_to_position)
    
    def test_config_format_compatibility(self):
        """設定フォーマット互換性テスト"""
        from config.simulation_config import ConfigurationManager
        import tempfile
        import json
        
        # 旧フォーマットの設定ファイルをシミュレート
        legacy_config = {
            "simulation_mode": "physics",
            "space_bounds": [10.0, 10.0, 5.0],
            "drones": [
                {
                    "drone_id": "legacy_drone",
                    "initial_position": [0, 0, 0],
                    "battery_level": 100.0
                }
            ]
        }
        
        config_manager = ConfigurationManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(legacy_config, f)
            config_file = f.name
        
        try:
            # 旧フォーマット読み込みテスト
            config = config_manager.load_config_from_file(config_file)
            
            # 正常に読み込まれることを確認
            assert hasattr(config, 'simulation_mode')
            assert len(config.drones) == 1
            assert config.drones[0].drone_id == "legacy_drone"
            
        finally:
            import os
            if os.path.exists(config_file):
                os.unlink(config_file)


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])