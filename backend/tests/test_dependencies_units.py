"""
依存性注入システム単体テスト
dependencies.py の個別コンポーネント単体テスト - Phase 1
"""

import pytest
from unittest.mock import patch, MagicMock
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dependencies import get_drone_service, DroneServiceDep
from services.drone_service import DroneService


class TestDroneServiceDependency:
    """DroneService依存性注入単体テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        # LRUキャッシュをクリア
        get_drone_service.cache_clear()
    
    def teardown_method(self):
        """各テスト後のクリーンアップ"""
        # LRUキャッシュをクリア
        get_drone_service.cache_clear()
    
    def test_get_drone_service_returns_instance(self):
        """get_drone_service()がDroneServiceインスタンスを返すテスト"""
        service = get_drone_service()
        
        # インスタンス型確認
        assert isinstance(service, DroneService)
        assert hasattr(service, 'connect')
        assert hasattr(service, 'disconnect')
        assert hasattr(service, 'takeoff')
        assert hasattr(service, 'land')
        assert hasattr(service, '_is_connected')
        assert hasattr(service, '_is_flying')
    
    def test_singleton_behavior(self):
        """シングルトン動作単体テスト"""
        # 複数回呼び出し
        service1 = get_drone_service()
        service2 = get_drone_service()
        service3 = get_drone_service()
        
        # 同一インスタンスであることを確認
        assert service1 is service2
        assert service2 is service3
        assert id(service1) == id(service2) == id(service3)
    
    def test_singleton_boundary_values(self):
        """シングルトン境界値テスト"""
        # 大量呼び出しテスト（境界値: 1000回）
        services = []
        for i in range(1000):
            service = get_drone_service()
            services.append(service)
        
        # 全て同一インスタンス確認
        first_service = services[0]
        for service in services:
            assert service is first_service
        
        # メモリアドレス確認
        unique_ids = set(id(service) for service in services)
        assert len(unique_ids) == 1  # 単一のインスタンスのみ
    
    def test_lru_cache_functionality(self):
        """LRUキャッシュ機能単体テスト"""
        # キャッシュ情報取得
        cache_info_before = get_drone_service.cache_info()
        
        # 初回呼び出し
        service1 = get_drone_service()
        cache_info_after_first = get_drone_service.cache_info()
        
        # キャッシュミス確認
        assert cache_info_after_first.misses == cache_info_before.misses + 1
        assert cache_info_after_first.hits == cache_info_before.hits
        
        # 二回目呼び出し
        service2 = get_drone_service()
        cache_info_after_second = get_drone_service.cache_info()
        
        # キャッシュヒット確認
        assert cache_info_after_second.hits == cache_info_after_first.hits + 1
        assert cache_info_after_second.misses == cache_info_after_first.misses
        
        # 同一インスタンス確認
        assert service1 is service2
    
    def test_lru_cache_boundary_values(self):
        """LRUキャッシュ境界値テスト"""
        # キャッシュクリア前状態
        get_drone_service.cache_clear()
        cache_info_cleared = get_drone_service.cache_info()
        assert cache_info_cleared.hits == 0
        assert cache_info_cleared.misses == 0
        assert cache_info_cleared.currsize == 0
        
        # 境界値: 連続100回アクセス
        for i in range(100):
            service = get_drone_service()
            assert isinstance(service, DroneService)
        
        final_cache_info = get_drone_service.cache_info()
        assert final_cache_info.hits == 99  # 2回目以降はヒット
        assert final_cache_info.misses == 1  # 初回のみミス
        assert final_cache_info.currsize == 1  # 1つのアイテムがキャッシュ
    
    def test_cache_clear_functionality(self):
        """キャッシュクリア機能テスト"""
        # 初回呼び出し
        service1 = get_drone_service()
        cache_info_before_clear = get_drone_service.cache_info()
        assert cache_info_before_clear.currsize == 1
        
        # キャッシュクリア
        get_drone_service.cache_clear()
        cache_info_after_clear = get_drone_service.cache_info()
        assert cache_info_after_clear.hits == 0
        assert cache_info_after_clear.misses == 0
        assert cache_info_after_clear.currsize == 0
        
        # クリア後の新規呼び出し
        service2 = get_drone_service()
        
        # 新しいインスタンス生成確認
        # 注意: LRUキャッシュはクリア後に新しいインスタンスを作成
        assert isinstance(service2, DroneService)


class TestMultiThreadingSafety:
    """マルチスレッド安全性単体テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        get_drone_service.cache_clear()
    
    def teardown_method(self):
        """各テスト後のクリーンアップ"""
        get_drone_service.cache_clear()
    
    def test_concurrent_access_singleton(self):
        """並行アクセス時のシングルトン動作テスト"""
        services = []
        errors = []
        
        def worker():
            try:
                service = get_drone_service()
                services.append(service)
            except Exception as e:
                errors.append(e)
        
        # 境界値: 10スレッドで並行アクセス
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
        
        # 全スレッド開始
        for thread in threads:
            thread.start()
        
        # 全スレッド完了待機
        for thread in threads:
            thread.join(timeout=5.0)  # 5秒タイムアウト
        
        # 結果確認
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(services) == 10
        
        # 全て同一インスタンス確認
        first_service = services[0]
        for service in services:
            assert service is first_service
    
    def test_rapid_successive_calls(self):
        """高速連続呼び出しテスト"""
        services = []
        
        # 境界値: 0.001秒間隔で100回呼び出し
        start_time = time.time()
        for i in range(100):
            service = get_drone_service()
            services.append(service)
            time.sleep(0.001)
        end_time = time.time()
        
        # 実行時間確認（境界値: 1秒以内）
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Execution too slow: {execution_time}s"
        
        # 全て同一インスタンス確認
        first_service = services[0]
        for service in services:
            assert service is first_service


class TestDroneServiceDepType:
    """DroneServiceDep型注釈単体テスト"""
    
    def test_drone_service_dep_type_annotation(self):
        """DroneServiceDep型注釈確認テスト"""
        from typing import get_origin, get_args
        from fastapi import Depends
        
        # DroneServiceDepの型情報確認
        assert hasattr(DroneServiceDep, '__origin__')
        assert hasattr(DroneServiceDep, '__args__')
        
        # Annotated型の確認
        origin = get_origin(DroneServiceDep)
        args = get_args(DroneServiceDep)
        
        # Annotated[DroneService, Depends(get_drone_service)]の構造確認
        assert len(args) == 2
        assert args[0] == DroneService
        
        # Depends部分の確認
        depends_part = args[1]
        assert isinstance(depends_part, Depends)
    
    def test_dependency_injection_simulation(self):
        """依存性注入シミュレーションテスト"""
        from fastapi import Depends
        
        # FastAPI Dependsを使った関数定義のシミュレーション
        def example_endpoint(drone_service: DroneServiceDep):
            return drone_service
        
        # 型ヒント確認
        annotations = example_endpoint.__annotations__
        assert 'drone_service' in annotations
        assert annotations['drone_service'] == DroneServiceDep
    
    def test_multiple_dependency_usage(self):
        """複数依存性使用テスト"""
        # 複数の関数で同じ依存性を使用するシミュレーション
        def endpoint1(service: DroneServiceDep):
            return service
        
        def endpoint2(service: DroneServiceDep):  
            return service
        
        def endpoint3(service: DroneServiceDep):
            return service
        
        # 型注釈確認
        for endpoint in [endpoint1, endpoint2, endpoint3]:
            annotations = endpoint.__annotations__
            assert annotations['service'] == DroneServiceDep


class TestDependencyError:
    """依存性エラーハンドリング単体テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        get_drone_service.cache_clear()
    
    def teardown_method(self):
        """各テスト後のクリーンアップ"""
        get_drone_service.cache_clear()
    
    @patch('services.drone_service.DroneService')
    def test_drone_service_creation_error(self, mock_drone_service):
        """DroneService作成エラーテスト"""
        # DroneService初期化エラーをシミュレート
        mock_drone_service.side_effect = Exception("Initialization failed")
        
        with pytest.raises(Exception) as exc_info:
            get_drone_service()
        
        assert "Initialization failed" in str(exc_info.value)
    
    @patch('services.drone_service.DroneService')
    def test_drone_service_creation_none_return(self, mock_drone_service):
        """DroneService作成時None返却テスト"""
        # DroneServiceがNoneを返すケース
        mock_drone_service.return_value = None
        
        result = get_drone_service()
        assert result is None
    
    def test_dependency_memory_usage(self):
        """依存性メモリ使用量テスト"""
        import gc
        
        # ガベージコレクション実行
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # 大量のservice取得（境界値: 1000回）
        services = []
        for i in range(1000):
            service = get_drone_service()
            services.append(service)
        
        # メモリリーク確認
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # メモリ増加量確認（シングルトンパターンなので大幅な増加はないはず）
        object_increase = final_objects - initial_objects
        assert object_increase < 100, f"Potential memory leak: {object_increase} objects created"
        
        # 全て同一インスタンス確認
        first_service = services[0]
        for service in services:
            assert service is first_service


class TestCacheConfiguration:
    """キャッシュ設定単体テスト"""
    
    def test_lru_cache_decorator_configuration(self):
        """LRUキャッシュデコレータ設定確認テスト"""
        # キャッシュ情報取得
        cache_info = get_drone_service.cache_info()
        
        # LRUキャッシュの属性確認
        assert hasattr(get_drone_service, 'cache_info')
        assert hasattr(get_drone_service, 'cache_clear')
        assert hasattr(cache_info, 'hits')
        assert hasattr(cache_info, 'misses')
        assert hasattr(cache_info, 'maxsize')
        assert hasattr(cache_info, 'currsize')
        
        # デフォルト設定確認（lru_cache()はmaxsize=128がデフォルト）
        assert cache_info.maxsize == 128
    
    def test_cache_size_boundary_values(self):
        """キャッシュサイズ境界値テスト"""
        get_drone_service.cache_clear()
        
        # キャッシュサイズ確認
        cache_info_empty = get_drone_service.cache_info()
        assert cache_info_empty.currsize == 0
        
        # 1つの項目をキャッシュ
        service = get_drone_service()
        cache_info_one = get_drone_service.cache_info()
        assert cache_info_one.currsize == 1
        
        # 最大サイズ確認（get_drone_serviceは引数なしなので1つのみキャッシュされる）
        for i in range(10):
            service = get_drone_service()
        
        cache_info_final = get_drone_service.cache_info()
        assert cache_info_final.currsize == 1  # 引数なしなので1つのアイテムのみ