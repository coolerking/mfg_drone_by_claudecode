"""
Phase 1 Unit Tests: Dependency Injection System
依存性注入システムの単体テスト
"""

import pytest
import threading
import time
from unittest.mock import patch, MagicMock
import gc

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dependencies import get_drone_service, DroneServiceDep
from services.drone_service import DroneService


class TestGetDroneService:
    """get_drone_service関数単体テスト"""

    def test_get_drone_service_returns_instance(self):
        """DroneServiceインスタンス取得テスト"""
        service = get_drone_service()
        assert service is not None
        assert isinstance(service, DroneService)

    def test_get_drone_service_singleton_behavior(self):
        """シングルトン動作テスト"""
        service1 = get_drone_service()
        service2 = get_drone_service()
        
        # 同じインスタンスが返されることを確認
        assert service1 is service2
        assert id(service1) == id(service2)

    def test_get_drone_service_multiple_calls(self):
        """複数回呼び出しテスト"""
        services = []
        for _ in range(10):
            services.append(get_drone_service())
        
        # 全て同じインスタンスであることを確認
        first_service = services[0]
        for service in services[1:]:
            assert service is first_service

    def test_get_drone_service_boundary_calls(self):
        """境界値呼び出しテスト"""
        # 1回呼び出し
        service_single = get_drone_service()
        assert isinstance(service_single, DroneService)
        
        # 100回呼び出し
        for _ in range(100):
            service_multiple = get_drone_service()
            assert service_multiple is service_single

    def test_get_drone_service_thread_safety(self):
        """スレッドセーフティテスト"""
        services = []
        errors = []
        
        def get_service():
            try:
                service = get_drone_service()
                services.append(service)
            except Exception as e:
                errors.append(e)
        
        # 5つのスレッドで同時実行
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_service)
            threads.append(thread)
            thread.start()
        
        # 全スレッド完了を待機
        for thread in threads:
            thread.join()
        
        # エラーが発生していないことを確認
        assert len(errors) == 0
        
        # 全て同じインスタンスであることを確認
        assert len(services) == 5
        first_service = services[0]
        for service in services[1:]:
            assert service is first_service

    def test_get_drone_service_concurrent_access(self):
        """同時アクセステスト"""
        import concurrent.futures
        
        def get_service_with_delay():
            time.sleep(0.01)  # 短い遅延
            return get_drone_service()
        
        # 10個の同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_service_with_delay) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # 全て同じインスタンスであることを確認
        first_result = results[0]
        for result in results[1:]:
            assert result is first_result

    def test_get_drone_service_memory_efficiency(self):
        """メモリ効率性テスト"""
        import weakref
        
        # 初期状態のサービス取得
        service = get_drone_service()
        weak_ref = weakref.ref(service)
        
        # 複数回取得してもメモリリークしないことを確認
        for _ in range(100):
            temp_service = get_drone_service()
            assert temp_service is service
        
        # 弱参照が有効であることを確認
        assert weak_ref() is not None

    def test_get_drone_service_after_cache_clear(self):
        """キャッシュクリア後テスト"""
        # 初期サービス取得
        service1 = get_drone_service()
        
        # キャッシュをクリア
        get_drone_service.cache_clear()
        
        # 新しいサービス取得
        service2 = get_drone_service()
        
        # 新しいインスタンスが作成されることを確認
        assert service1 is not service2
        assert isinstance(service2, DroneService)

    def test_get_drone_service_cache_info(self):
        """キャッシュ情報テスト"""
        # キャッシュをクリア
        get_drone_service.cache_clear()
        
        # 初回呼び出し前
        info = get_drone_service.cache_info()
        assert info.hits == 0
        assert info.misses == 0
        
        # 初回呼び出し
        service1 = get_drone_service()
        info = get_drone_service.cache_info()
        assert info.misses == 1
        
        # 2回目呼び出し
        service2 = get_drone_service()
        info = get_drone_service.cache_info()
        assert info.hits == 1
        assert service1 is service2

    def test_get_drone_service_boundary_cache_behavior(self):
        """キャッシュ動作境界値テスト"""
        # キャッシュクリア
        get_drone_service.cache_clear()
        
        # 最小呼び出し（1回）
        service = get_drone_service()
        info = get_drone_service.cache_info()
        assert info.misses == 1
        assert info.hits == 0
        
        # 境界値呼び出し（128回 - lru_cacheのデフォルト最大サイズ）
        for _ in range(127):  # 127回追加（合計128回）
            same_service = get_drone_service()
            assert same_service is service
        
        info = get_drone_service.cache_info()
        assert info.hits == 127


class TestDroneServiceDep:
    """DroneServiceDep型注釈テスト"""

    def test_drone_service_dep_type_annotation(self):
        """型注釈の存在確認テスト"""
        import typing
        
        # DroneServiceDepが型注釈として定義されていることを確認
        assert hasattr(DroneServiceDep, "__origin__")
        assert hasattr(DroneServiceDep, "__args__")

    def test_drone_service_dep_annotation_structure(self):
        """型注釈構造テスト"""
        from typing import get_origin, get_args
        
        # Annotated型であることを確認
        origin = get_origin(DroneServiceDep)
        args = get_args(DroneServiceDep)
        
        assert origin is not None
        assert len(args) >= 2  # 型とDependsが含まれる
        assert args[0] == DroneService

    def test_drone_service_dep_dependency_integration(self):
        """Depends統合テスト"""
        from fastapi import Depends
        from typing import get_args
        
        args = get_args(DroneServiceDep)
        depends_instance = args[1]
        
        # Dependsインスタンスであることを確認
        assert isinstance(depends_instance, Depends)
        assert depends_instance.dependency == get_drone_service

    def test_drone_service_dep_usage_simulation(self):
        """使用シミュレーションテスト"""
        # FastAPIエンドポイントでの使用をシミュレート
        def mock_endpoint(drone_service: DroneServiceDep):
            return drone_service
        
        # 型ヒントが正しく設定されていることを確認
        annotations = mock_endpoint.__annotations__
        assert "drone_service" in annotations
        assert annotations["drone_service"] == DroneServiceDep

    @pytest.mark.parametrize("call_count", [1, 5, 10, 50])
    def test_drone_service_dep_multiple_injections(self, call_count):
        """複数回注入テスト"""
        from typing import get_args
        
        depends_instance = get_args(DroneServiceDep)[1]
        
        # 複数回dependency呼び出し
        services = []
        for _ in range(call_count):
            service = depends_instance.dependency()
            services.append(service)
        
        # 全て同じインスタンスであることを確認
        first_service = services[0]
        for service in services[1:]:
            assert service is first_service


class TestDependencyInjectionSystemIntegration:
    """依存性注入システム統合テスト"""

    def test_dependency_system_consistency(self):
        """依存性システム一貫性テスト"""
        from typing import get_args
        
        # 直接呼び出しとDI経由で同じインスタンスが得られることを確認
        direct_service = get_drone_service()
        depends_instance = get_args(DroneServiceDep)[1]
        di_service = depends_instance.dependency()
        
        assert direct_service is di_service

    def test_dependency_isolation(self):
        """依存性分離テスト"""
        # キャッシュクリア
        get_drone_service.cache_clear()
        
        # 複数の「セッション」を模擬
        session1_service = get_drone_service()
        session2_service = get_drone_service()
        
        # 同じインスタンス（シングルトン）
        assert session1_service is session2_service
        
        # 新しい「アプリケーション」セッションを模擬（キャッシュクリア）
        get_drone_service.cache_clear()
        new_app_service = get_drone_service()
        
        # 新しいインスタンス
        assert session1_service is not new_app_service

    def test_dependency_error_handling(self):
        """依存性エラー処理テスト"""
        # DroneService初期化エラーをシミュレート
        with patch('services.drone_service.DroneService') as mock_service:
            mock_service.side_effect = Exception("Initialization failed")
            
            # キャッシュクリア
            get_drone_service.cache_clear()
            
            # エラーが適切に伝播されることを確認
            with pytest.raises(Exception, match="Initialization failed"):
                get_drone_service()

    def test_dependency_performance(self):
        """依存性パフォーマンステスト"""
        # キャッシュクリア
        get_drone_service.cache_clear()
        
        # 初回呼び出し時間測定
        start_time = time.time()
        service1 = get_drone_service()
        first_call_time = time.time() - start_time
        
        # キャッシュされた呼び出し時間測定
        start_time = time.time()
        service2 = get_drone_service()
        cached_call_time = time.time() - start_time
        
        # キャッシュされた呼び出しが高速であることを確認
        assert cached_call_time < first_call_time
        assert cached_call_time < 0.001  # 1ms以内
        assert service1 is service2

    def test_dependency_memory_management(self):
        """依存性メモリ管理テスト"""
        try:
            import psutil
            import os
            
            # プロセスメモリ使用量取得
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # 大量のサービス取得
            services = []
            for _ in range(1000):
                services.append(get_drone_service())
            
            # メモリ使用量再測定
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # メモリ増加が制限内であることを確認（シングルトンのため）
            assert memory_increase < 1024 * 1024  # 1MB以内
            
            # 全て同じインスタンスであることを確認
            first_service = services[0]
            for service in services[1:]:
                assert service is first_service
        except ImportError:
            # psutilがない場合はスキップ
            pytest.skip("psutil not available")

    def test_dependency_garbage_collection(self):
        """依存性ガベージコレクションテスト"""
        # 初期状態
        get_drone_service.cache_clear()
        
        # サービス取得とweakref作成
        service = get_drone_service()
        import weakref
        weak_ref = weakref.ref(service)
        
        # 参照削除
        del service
        gc.collect()
        
        # キャッシュがあるため参照は残る
        assert weak_ref() is not None
        
        # キャッシュクリア後にガベージコレクション
        get_drone_service.cache_clear()
        gc.collect()
        
        # 参照が削除される（場合によっては残る可能性もある）
        # この部分は実装によって異なる可能性がある

    def test_dependency_system_boundaries(self):
        """依存性システム境界値テスト"""
        # 最小使用パターン
        service = get_drone_service()
        assert isinstance(service, DroneService)
        
        # 最大使用パターン（高負荷シミュレーション）
        def stress_test():
            for _ in range(100):
                s = get_drone_service()
                assert isinstance(s, DroneService)
        
        # 複数スレッドでストレステスト
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=stress_test)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # システムが安定していることを確認
        final_service = get_drone_service()
        assert isinstance(final_service, DroneService)


class TestLRUCacheImplementation:
    """LRUキャッシュ実装テスト"""

    def test_lru_cache_decorator_presence(self):
        """LRUキャッシュデコレータ存在確認テスト"""
        # lru_cacheデコレータが適用されていることを確認
        assert hasattr(get_drone_service, 'cache_info')
        assert hasattr(get_drone_service, 'cache_clear')
        assert callable(get_drone_service.cache_info)
        assert callable(get_drone_service.cache_clear)

    def test_lru_cache_functionality(self):
        """LRUキャッシュ機能テスト"""
        # キャッシュクリア
        get_drone_service.cache_clear()
        
        # 初回アクセス
        info_before = get_drone_service.cache_info()
        service = get_drone_service()
        info_after = get_drone_service.cache_info()
        
        assert info_after.misses == info_before.misses + 1
        assert isinstance(service, DroneService)

    def test_lru_cache_hit_ratio(self):
        """LRUキャッシュヒット率テスト"""
        get_drone_service.cache_clear()
        
        # 100回アクセス
        for _ in range(100):
            get_drone_service()
        
        info = get_drone_service.cache_info()
        assert info.hits == 99  # 初回のみmiss
        assert info.misses == 1
        
        # ヒット率100%近く
        hit_ratio = info.hits / (info.hits + info.misses)
        assert hit_ratio >= 0.99

    def test_lru_cache_maxsize_behavior(self):
        """LRUキャッシュ最大サイズ動作テスト"""
        # デフォルトでは maxsize=128
        get_drone_service.cache_clear()
        
        # キャッシュサイズは1つの関数に対して1つのエントリのみ
        service1 = get_drone_service()
        service2 = get_drone_service()
        
        info = get_drone_service.cache_info()
        assert info.currsize == 1  # 1つのエントリのみ
        assert service1 is service2

    def test_lru_cache_thread_safety_detailed(self):
        """LRUキャッシュスレッドセーフティ詳細テスト"""
        get_drone_service.cache_clear()
        
        results = []
        errors = []
        
        def cache_access_worker():
            try:
                for _ in range(10):
                    service = get_drone_service()
                    results.append(id(service))
                    time.sleep(0.001)  # 短い遅延
            except Exception as e:
                errors.append(e)
        
        # 10スレッドで同時実行
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=cache_access_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # エラーがないことを確認
        assert len(errors) == 0
        
        # 全ての結果が同じIDであることを確認
        assert len(set(results)) == 1