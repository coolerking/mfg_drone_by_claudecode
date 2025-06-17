"""
ユーザ利用シナリオテスト
実際のユーザー操作フローを模擬したテスト
"""

import pytest
import time
from pages.dashboard_page import DashboardPage
from pages.health_page import HealthPage


@pytest.mark.ui
@pytest.mark.scenario
class TestNewAdministratorScenarios:
    """新規管理者シナリオテスト"""
    
    def test_first_time_system_access(self, driver, app_server):
        """B1-001: 初回アクセス・システム確認"""
        # 新規管理者が初めてシステムにアクセスするシナリオ
        
        # Step 1: メインページにアクセス
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        # Step 2: ページが正常に表示されることを確認
        assert dashboard.is_page_loaded(), "初回アクセス時にページが正常に表示されません"
        
        # Step 3: システムの基本情報が表示されることを確認
        content = dashboard.check_content_validity()
        assert content['title_valid'], "システムタイトルが表示されていません"
        assert content['heading_valid'], "見出しが表示されていません"
        assert content['description_valid'], "システム説明が表示されていません"
        
        # Step 4: 日本語コンテンツが正常表示されることを確認
        japanese_content = dashboard.check_japanese_content()
        assert japanese_content['heading_has_japanese'], "見出しに日本語が含まれていません"
        assert japanese_content['description_has_japanese'], "説明文に日本語が含まれていません"
        
        # Step 5: レスポンシブデザインが適切に動作することを確認
        responsive_results = dashboard.perform_responsive_test()
        mobile_result = responsive_results.get('320x568', {})
        tablet_result = responsive_results.get('768x1024', {})
        
        assert mobile_result.get('layout_valid', False), "モバイル表示が適切ではありません"
        assert tablet_result.get('layout_valid', False), "タブレット表示が適切ではありません"
    
    def test_basic_function_understanding(self, driver, app_server):
        """B1-002: 基本機能理解・ナビゲーション"""
        # 管理者がシステムの基本機能を理解するシナリオ
        
        # Step 1: メインダッシュボードにアクセス
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        # Step 2: システムの説明文から機能を理解
        description = dashboard.get_description_text()
        expected_functions = ["物体認識", "ドローン制御", "追跡"]
        
        for function in expected_functions:
            assert function in description, f"基本機能の説明が不足しています: {function}"
        
        # Step 3: ページ構造が理解しやすいことを確認
        structure = dashboard.validate_page_structure()
        assert structure['main_heading_present'], "メイン見出しが存在しません"
        assert structure['container_present'], "コンテナ構造が存在しません"
        
        # Step 4: アクセシビリティが適切であることを確認
        accessibility = dashboard.check_accessibility_basics()
        assert accessibility['has_single_h1'], "H1見出しが適切ではありません"
        assert accessibility['has_title'], "ページタイトルが設定されていません"
    
    def test_system_status_verification(self, driver, app_server):
        """B1-003: システム状態確認"""
        # 管理者がシステムの状態を確認するシナリオ
        
        # Step 1: メインダッシュボードでシステムの基本状態確認
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        validation = dashboard.validate_no_errors()
        assert validation['javascript_clean'], "システムにJavaScriptエラーがあります"
        assert validation['page_loaded_successfully'], "システムが正常に起動していません"
        
        # Step 2: ヘルスチェックエンドポイントでAPI状態確認
        health = HealthPage(driver)
        health.open()
        
        comprehensive_check = health.comprehensive_health_check()
        
        # API エンドポイントの可用性確認
        assert comprehensive_check['endpoint_availability']['overall_available'], "APIが利用できません"
        
        # JSON レスポンスの妥当性確認
        assert comprehensive_check['json_structure']['valid'], "APIレスポンスが不正です"
        assert comprehensive_check['json_structure']['status_is_healthy'], "システムステータスが正常ではありません"
        
        # パフォーマンス確認
        performance = comprehensive_check['performance']
        assert performance['success_rate'] >= 0.8, f"API成功率が低すぎます: {performance['success_rate']}"
        assert performance['avg_response_time'] < 2.0, f"API応答時間が遅すぎます: {performance['avg_response_time']}秒"
        
        # Step 3: システム全体の健全性確認
        content_type = comprehensive_check['content_type']
        assert content_type['is_json'], "APIレスポンス形式が正しくありません"
        
        error_handling = comprehensive_check['error_handling']
        assert error_handling['normal_endpoint_works'], "正常なエンドポイントが動作していません"


@pytest.mark.ui
@pytest.mark.scenario
class TestDailyOperationScenarios:
    """日常運用シナリオテスト"""
    
    def test_system_startup_dashboard_check(self, driver, app_server):
        """B2-001: システム起動・ダッシュボード確認"""
        # 日常業務でのシステム起動からダッシュボード確認のシナリオ
        
        # Step 1: システム起動（ブラウザでアクセス）
        dashboard = DashboardPage(driver)
        start_time = time.time()
        dashboard.open()
        load_time = time.time() - start_time
        
        # Step 2: 起動時間が妥当であることを確認
        assert load_time < 5.0, f"システム起動が遅すぎます: {load_time}秒"
        
        # Step 3: ダッシュボードの基本表示確認
        assert dashboard.is_page_loaded(), "ダッシュボードが正常に表示されません"
        
        content = dashboard.check_content_validity()
        assert content['title_valid'], "ダッシュボードタイトルが表示されていません"
        assert content['heading_valid'], "ダッシュボード見出しが表示されていません"
        
        # Step 4: システムパフォーマンス確認
        performance = dashboard.get_page_performance_metrics()
        if 'error' not in performance:
            assert performance['loadEvent'] < 3000, "ページロードが遅すぎます"
            assert performance['domComplete'] < 2000, "DOM構築が遅すぎます"
        
        # Step 5: エラーが無いことを確認
        validation = dashboard.validate_no_errors()
        assert validation['javascript_clean'], "起動時にJavaScriptエラーが発生しています"
    
    def test_regular_health_monitoring(self, driver, app_server):
        """B2-002: 定期健全性チェック"""
        # 日常的なシステム監視のシナリオ
        
        # Step 1: ダッシュボードから状態確認開始
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        # 基本的な表示状態確認
        assert dashboard.is_page_loaded(), "ダッシュボードにアクセスできません"
        
        # Step 2: ヘルスチェックエンドポイントで詳細確認
        health = HealthPage(driver)
        health.open()
        
        # 複数回のヘルスチェックで安定性確認
        health_checks = []
        for i in range(3):
            health.refresh_page()
            time.sleep(0.5)
            
            check_result = health.validate_json_structure()
            health_checks.append(check_result)
            
            assert check_result['valid'], f"第{i+1}回ヘルスチェックで異常検出"
            assert check_result['status_is_healthy'], f"第{i+1}回ヘルスチェックで不正ステータス"
        
        # Step 3: パフォーマンス監視
        performance = health.perform_performance_test()
        
        assert performance['success_rate'] >= 0.9, f"健全性チェック成功率が低下: {performance['success_rate']}"
        assert performance['avg_response_time'] < 1.0, f"応答時間が劣化: {performance['avg_response_time']}秒"
        
        # Step 4: エラーハンドリング確認
        error_handling = health.check_error_handling()
        assert error_handling['normal_endpoint_works'], "正常エンドポイントが異常です"
        assert error_handling['handles_404_properly'], "エラーハンドリングが適切ではありません"
    
    def test_multi_browser_compatibility_check(self, driver, app_server, browser_name):
        """ブラウザ互換性確認（日常運用での複数ブラウザ対応）"""
        # 異なるブラウザでの動作確認シナリオ
        
        # Step 1: ブラウザ固有の動作確認
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        # Step 2: 基本機能の動作確認
        assert dashboard.is_page_loaded(), f"{browser_name}で正常にロードできません"
        
        # Step 3: レスポンシブデザインの確認
        responsive_results = dashboard.perform_responsive_test()
        for breakpoint, result in responsive_results.items():
            assert result['layout_valid'], f"{browser_name}のブレークポイント{breakpoint}でレイアウト異常"
        
        # Step 4: API動作確認
        health = HealthPage(driver)
        health.open()
        
        json_validation = health.validate_json_structure()
        assert json_validation['valid'], f"{browser_name}でJSONレスポンス異常"
        assert json_validation['status_is_healthy'], f"{browser_name}でステータス異常"
        
        # Step 5: JavaScript動作確認
        validation = dashboard.validate_no_errors()
        assert validation['javascript_clean'], f"{browser_name}でJavaScriptエラー発生"


@pytest.mark.ui
@pytest.mark.scenario
class TestExtendedUserScenarios:
    """拡張ユーザシナリオテスト"""
    
    def test_long_session_stability(self, driver, app_server):
        """長時間セッション安定性テスト"""
        # 長時間の操作セッションでの安定性確認
        
        dashboard = DashboardPage(driver)
        health = HealthPage(driver)
        
        # 複数ページ間の遷移を繰り返す
        for cycle in range(3):
            # ダッシュボード表示
            dashboard.open()
            assert dashboard.is_page_loaded(), f"サイクル{cycle+1}: ダッシュボード表示失敗"
            
            time.sleep(1)
            
            # ヘルスチェック表示
            health.open()
            json_check = health.validate_json_structure()
            assert json_check['valid'], f"サイクル{cycle+1}: ヘルスチェック失敗"
            
            time.sleep(1)
            
            # パフォーマンス劣化チェック
            if cycle > 0:
                performance = health.perform_performance_test()
                assert performance['success_rate'] >= 0.8, f"サイクル{cycle+1}: パフォーマンス劣化"
    
    def test_error_recovery_workflow(self, driver, app_server):
        """エラー回復ワークフローテスト"""
        # エラー発生からの回復プロセス確認
        
        # Step 1: 正常状態の確認
        dashboard = DashboardPage(driver)
        dashboard.open()
        assert dashboard.is_page_loaded(), "初期状態が正常ではありません"
        
        # Step 2: 意図的にエラー状況を作成（存在しないページアクセス）
        driver.get(f"{dashboard.base_url}/nonexistent-page")
        
        # Step 3: エラーページが適切に表示されることを確認
        page_source = driver.page_source.lower()
        error_indicators = ['404', 'not found', 'error']
        has_error_indication = any(indicator in page_source for indicator in error_indicators)
        assert has_error_indication, "エラーページが適切に表示されていません"
        
        # Step 4: 正常ページへの回復
        dashboard.open()
        assert dashboard.is_page_loaded(), "エラー後に正常ページに戻れません"
        
        # Step 5: システム機能の回復確認
        health = HealthPage(driver)
        health.open()
        
        json_validation = health.validate_json_structure()
        assert json_validation['valid'], "エラー後にAPIが正常に動作していません"
        assert json_validation['status_is_healthy'], "エラー後にシステムステータスが異常です"