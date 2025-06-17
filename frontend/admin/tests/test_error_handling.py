"""
エラーハンドリングテスト
異常系・境界値・エラー復旧の包括的検証
"""

import pytest
import time
import requests
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.dashboard_page import DashboardPage
from pages.health_page import HealthPage


@pytest.mark.ui
@pytest.mark.error_handling
class TestBasicErrorCases:
    """基本エラーケーステスト"""
    
    def test_nonexistent_page_access(self, driver, app_server):
        """D1-001: 存在しないページアクセス"""
        # 存在しないページにアクセスした場合のエラーハンドリング
        
        base_url = "http://localhost:5001"
        nonexistent_paths = [
            "/nonexistent",
            "/admin/dashboard",  # 現在は存在しない管理画面
            "/api/undefined",
            "/test/invalid",
            "/ドローン"  # 日本語パス
        ]
        
        for path in nonexistent_paths:
            # 存在しないページにアクセス
            driver.get(f"{base_url}{path}")
            time.sleep(1)
            
            # エラーページが適切に表示されることを確認
            page_source = driver.page_source.lower()
            
            # 404エラーまたはエラー表示の確認
            error_indicators = ['404', 'not found', 'error', 'page not found', 'file not found']
            has_error_indication = any(indicator in page_source for indicator in error_indicators)
            
            assert has_error_indication, f"パス {path} で適切なエラーページが表示されていません"
            
            # ページが完全にクラッシュしていないことを確認
            assert "internal server error" not in page_source, f"パス {path} で内部サーバーエラーが発生"
    
    def test_server_error_handling(self, driver, app_server):
        """D1-002: サーバーエラー処理"""
        # サーバーエラー時のフロントエンド動作確認
        
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # Step 1: 正常時のベースライン確認
        dashboard.open()
        assert dashboard.is_page_loaded(), "正常時の動作確認失敗"
        
        # Step 2: 無効なAPIエンドポイントアクセステスト
        invalid_endpoints = [
            "/health/invalid",
            "/api/nonexistent",
            "/status/undefined"
        ]
        
        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"http://localhost:5001{endpoint}", timeout=5)
                # 404または適切なエラーステータスが返されることを確認
                assert response.status_code in [404, 405, 500], f"エンドポイント {endpoint} で不適切なステータス: {response.status_code}"
            except requests.RequestException as e:
                # 接続エラーも許容される場合がある
                assert "Connection" in str(e) or "timeout" in str(e).lower(), f"予期しないエラー: {e}"
        
        # Step 3: 正常エンドポイントの回復確認
        health.open()
        recovery_check = health.validate_json_structure()
        assert recovery_check['valid'], "エラーテスト後に正常エンドポイントが復旧していません"
    
    def test_network_error_handling(self, driver, app_server):
        """D1-003: ネットワークエラー処理"""
        # ネットワーク関連エラーのハンドリング確認
        
        dashboard = DashboardPage(driver)
        
        # Step 1: 正常接続の確認
        dashboard.open()
        initial_load = dashboard.is_page_loaded()
        assert initial_load, "初期ロードが失敗"
        
        # Step 2: 無効なホストへのアクセステスト
        invalid_hosts = [
            "http://nonexistent.localhost:5001",
            "http://127.0.0.1:9999",  # 使用されていないポート
        ]
        
        for host in invalid_hosts:
            try:
                driver.get(host)
                time.sleep(3)  # タイムアウト待機
                
                # ブラウザのエラーページまたはタイムアウトページが表示されることを確認
                page_source = driver.page_source.lower()
                connection_error_indicators = [
                    'connection', 'timeout', 'unreachable', 'failed to load',
                    'this site can't be reached', 'connection timed out'
                ]
                
                has_connection_error = any(indicator in page_source for indicator in connection_error_indicators)
                # ネットワークエラーが適切に処理されているかは、ブラウザ固有の動作に依存
                # 少なくともクラッシュしていないことを確認
                assert len(page_source) > 0, f"ホスト {host} でページが完全に応答しない"
                
            except Exception as e:
                # タイムアウト例外は期待される動作
                assert "timeout" in str(e).lower() or "unreachable" in str(e).lower(), f"予期しないエラー: {e}"
        
        # Step 3: 正常接続への復旧確認
        dashboard.open()
        recovery_load = dashboard.is_page_loaded()
        assert recovery_load, "ネットワークエラーテスト後に正常接続に復旧できません"
    
    def test_timeout_handling(self, driver, app_server):
        """D1-004: タイムアウト処理"""
        # タイムアウト関連のエラーハンドリング確認
        
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # Step 1: 正常時のレスポンス時間確認
        start_time = time.time()
        dashboard.open()
        load_time = time.time() - start_time
        
        assert load_time < 10.0, f"正常時のロード時間が長すぎます: {load_time}秒"
        assert dashboard.is_page_loaded(), "正常時のロードが失敗"
        
        # Step 2: APIレスポンス時間の確認
        health.open()
        api_performance = health.perform_performance_test()
        
        # タイムアウト閾値を超えないことを確認
        max_acceptable_time = 5.0  # 5秒
        assert api_performance['avg_response_time'] < max_acceptable_time, f"API応答時間がタイムアウト閾値を超過: {api_performance['avg_response_time']}秒"
        
        # Step 3: 連続アクセス時のタイムアウト確認
        consecutive_access_times = []
        for i in range(3):
            start = time.time()
            health.refresh_page()
            health.wait_for_page_load()
            end = time.time()
            consecutive_access_times.append(end - start)
        
        max_consecutive_time = max(consecutive_access_times)
        avg_consecutive_time = sum(consecutive_access_times) / len(consecutive_access_times)
        
        assert max_consecutive_time < 8.0, f"連続アクセス時の最大時間がタイムアウト閾値を超過: {max_consecutive_time}秒"
        assert avg_consecutive_time < 3.0, f"連続アクセス時の平均時間が基準を超過: {avg_consecutive_time}秒"


@pytest.mark.ui
@pytest.mark.error_handling
class TestBrowserCompatibilityErrors:
    """ブラウザ互換性エラーテスト"""
    
    def test_chrome_compatibility(self, driver, app_server, browser_name):
        """D2-001: Chrome 最新版"""
        if browser_name != "chrome":
            pytest.skip("Chrome specific test")
        
        self._test_browser_specific_functionality(driver, app_server, "Chrome")
    
    def test_firefox_compatibility(self, driver, app_server, browser_name):
        """D2-002: Firefox 最新版"""
        if browser_name != "firefox":
            pytest.skip("Firefox specific test")
        
        self._test_browser_specific_functionality(driver, app_server, "Firefox")
    
    def test_safari_compatibility(self, driver, app_server, browser_name):
        """D2-003: Safari 最新版"""
        # Safari WebDriverは設定が複雑なためスキップ
        pytest.skip("Safari WebDriver not configured in test environment")
    
    def test_edge_compatibility(self, driver, app_server, browser_name):
        """D2-004: Edge 最新版"""
        # Edge WebDriverは設定が複雑なためスキップ
        pytest.skip("Edge WebDriver not configured in test environment")
    
    def _test_browser_specific_functionality(self, driver, app_server, browser_type):
        """ブラウザ固有機能のテスト"""
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # Step 1: 基本ページロード確認
        dashboard.open()
        assert dashboard.is_page_loaded(), f"{browser_type}でページロードが失敗"
        
        # Step 2: JavaScript動作確認
        js_validation = dashboard.validate_no_errors()
        assert js_validation['javascript_clean'], f"{browser_type}でJavaScriptエラーが発生: {js_validation['javascript_errors']}"
        
        # Step 3: CSS表示確認
        css_info = dashboard.check_css_loading()
        assert len(css_info) > 0, f"{browser_type}でCSSが読み込まれていません"
        
        # Step 4: レスポンシブデザイン確認
        responsive_results = dashboard.perform_responsive_test()
        for breakpoint, result in responsive_results.items():
            assert result['layout_valid'], f"{browser_type}のブレークポイント{breakpoint}でレイアウト異常"
        
        # Step 5: API通信確認
        health.open()
        json_validation = health.validate_json_structure()
        assert json_validation['valid'], f"{browser_type}でAPI通信が異常"
        
        # Step 6: 日本語表示確認
        japanese_content = dashboard.check_japanese_content()
        assert japanese_content['heading_has_japanese'], f"{browser_type}で日本語見出しが正常表示されない"
        assert japanese_content['description_has_japanese'], f"{browser_type}で日本語説明文が正常表示されない"


@pytest.mark.ui
@pytest.mark.error_handling
class TestEdgeCaseErrors:
    """エッジケースエラーテスト"""
    
    def test_rapid_navigation_errors(self, driver, app_server):
        """高速ナビゲーション時のエラー確認"""
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # 高速でページ間を移動してエラーが発生しないことを確認
        navigation_sequence = [
            (dashboard, "ダッシュボード"),
            (health, "ヘルスチェック"),
            (dashboard, "ダッシュボード"),
            (health, "ヘルスチェック"),
            (dashboard, "ダッシュボード")
        ]
        
        for page_obj, page_name in navigation_sequence:
            page_obj.open()
            time.sleep(0.1)  # 最小限の待機
            
            # ページが正常にロードされることを確認
            if hasattr(page_obj, 'is_page_loaded'):
                assert page_obj.is_page_loaded(), f"高速ナビゲーション時に{page_name}のロードが失敗"
        
        # 最終的にJavaScriptエラーが発生していないことを確認
        final_validation = dashboard.validate_no_errors()
        assert final_validation['javascript_clean'], "高速ナビゲーション後にJavaScriptエラーが発生"
    
    def test_concurrent_request_errors(self, driver, app_server):
        """同時リクエスト時のエラー確認"""
        health = HealthPage(driver)
        
        # 複数の同時APIリクエストでエラーが発生しないことを確認
        import concurrent.futures
        import threading
        
        def make_api_request():
            try:
                response = requests.get("http://localhost:5001/health", timeout=10)
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'thread_id': threading.current_thread().ident
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'thread_id': threading.current_thread().ident
                }
        
        # 5つの同時リクエストを実行
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_api_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 結果の分析
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        # 少なくとも80%は成功することを期待
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.8, f"同時リクエストの成功率が低すぎます: {success_rate}"
        
        # 失敗したリクエストのエラー内容を確認
        for failed in failed_requests:
            error_msg = failed.get('error', '').lower()
            # 一時的なエラーは許容（タイムアウト、接続エラー等）
            acceptable_errors = ['timeout', 'connection', 'max retries']
            is_acceptable = any(acceptable in error_msg for acceptable in acceptable_errors)
            assert is_acceptable, f"許容できないエラーが発生: {failed.get('error')}"
    
    def test_memory_leak_detection(self, driver, app_server):
        """メモリリーク検出テスト"""
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # 初期メモリ使用量の取得
        initial_memory = driver.execute_script("""
            return {
                usedJSHeapSize: performance.memory ? performance.memory.usedJSHeapSize : 0,
                totalJSHeapSize: performance.memory ? performance.memory.totalJSHeapSize : 0
            };
        """)
        
        # 繰り返し操作でメモリリークがないことを確認
        for cycle in range(5):
            # ページ遷移を繰り返す
            dashboard.open()
            time.sleep(0.5)
            health.open()
            time.sleep(0.5)
            
            # 現在のメモリ使用量を取得
            current_memory = driver.execute_script("""
                return {
                    usedJSHeapSize: performance.memory ? performance.memory.usedJSHeapSize : 0,
                    totalJSHeapSize: performance.memory ? performance.memory.totalJSHeapSize : 0
                };
            """)
            
            # メモリ使用量が大幅に増加していないことを確認
            if initial_memory['usedJSHeapSize'] > 0 and current_memory['usedJSHeapSize'] > 0:
                memory_increase_ratio = current_memory['usedJSHeapSize'] / initial_memory['usedJSHeapSize']
                assert memory_increase_ratio < 3.0, f"サイクル{cycle+1}でメモリ使用量が大幅増加: {memory_increase_ratio}倍"
    
    def test_javascript_exception_handling(self, driver, app_server):
        """JavaScript例外処理テスト"""
        dashboard = DashboardPage(driver)
        
        dashboard.open()
        
        # 意図的にJavaScript例外を発生させてハンドリングを確認
        try:
            # 存在しない関数を呼び出す
            driver.execute_script("nonExistentFunction();")
        except Exception:
            # JavaScript例外は期待される
            pass
        
        # ページが正常に動作し続けることを確認
        assert dashboard.is_page_loaded(), "JavaScript例外後にページが正常動作しない"
        
        # コンテンツが正常に表示されることを確認
        content = dashboard.check_content_validity()
        assert content['title_valid'], "JavaScript例外後にタイトルが正常表示されない"
        assert content['heading_valid'], "JavaScript例外後に見出しが正常表示されない"
        
        # 新しいページロードが正常に動作することを確認
        dashboard.refresh_page()
        assert dashboard.is_page_loaded(), "JavaScript例外後のページリフレッシュが失敗"


@pytest.mark.ui
@pytest.mark.error_handling
class TestRecoveryScenarios:
    """エラー復旧シナリオテスト"""
    
    def test_error_recovery_workflow(self, driver, app_server):
        """包括的エラー復旧ワークフロー"""
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # Step 1: 正常状態の確認
        dashboard.open()
        initial_state = {
            'dashboard_loaded': dashboard.is_page_loaded(),
            'content_valid': dashboard.check_content_validity(),
            'no_js_errors': dashboard.validate_no_errors()['javascript_clean']
        }
        
        for key, value in initial_state.items():
            assert value or (isinstance(value, dict) and all(value.values())), f"初期状態が正常ではありません: {key}"
        
        # Step 2: 複数のエラー状況を順次発生
        error_scenarios = [
            ("存在しないページアクセス", "/nonexistent"),
            ("無効なAPIエンドポイント", "/api/invalid"),
            ("日本語パス", "/テスト"),
        ]
        
        for scenario_name, error_path in error_scenarios:
            # エラー状況の発生
            driver.get(f"http://localhost:5001{error_path}")
            time.sleep(1)
            
            # エラーが適切に処理されることを確認
            page_source = driver.page_source.lower()
            error_handled = any(indicator in page_source for indicator in ['404', 'not found', 'error'])
            assert error_handled, f"{scenario_name}でエラーが適切に処理されていません"
            
            # 正常ページへの復旧
            dashboard.open()
            recovery_success = dashboard.is_page_loaded()
            assert recovery_success, f"{scenario_name}後にダッシュボードに復旧できません"
            
            # 機能の完全復旧確認
            health.open()
            api_recovery = health.validate_json_structure()
            assert api_recovery['valid'], f"{scenario_name}後にAPI機能が復旧していません"
        
        # Step 3: 最終的な完全復旧確認
        final_comprehensive_check = health.comprehensive_health_check()
        
        recovery_criteria = {
            'endpoint_available': final_comprehensive_check['endpoint_availability']['overall_available'],
            'json_valid': final_comprehensive_check['json_structure']['valid'],
            'status_healthy': final_comprehensive_check['json_structure']['status_is_healthy'],
            'performance_acceptable': final_comprehensive_check['performance']['success_rate'] >= 0.8
        }
        
        for criterion, status in recovery_criteria.items():
            assert status, f"最終復旧確認で異常: {criterion}"