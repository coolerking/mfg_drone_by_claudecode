"""
UIコンポーネントレベルテスト
画面部品の入出力・表示・操作性を詳細に検証
"""

import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.health_page import HealthPage


@pytest.mark.ui
@pytest.mark.component
class TestDashboardComponents:
    """メインダッシュボードのコンポーネントテスト"""
    
    def test_page_title_display(self, driver, app_server):
        """A1-001: ページタイトル表示確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        title = dashboard.get_page_title()
        assert title is not None, "ページタイトルが設定されていません"
        assert len(title.strip()) > 0, "ページタイトルが空です"
        assert "MFG Drone" in title, f"期待するタイトル文字列が含まれていません: {title}"
    
    def test_meta_tags_configuration(self, driver, app_server):
        """A1-002: メタタグ設定確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        meta_info = dashboard.check_meta_tags()
        
        # charset確認
        assert 'charset' in meta_info, "charsetメタタグが設定されていません"
        assert meta_info['charset'].upper() == 'UTF-8', f"charsetがUTF-8ではありません: {meta_info['charset']}"
        
        # viewport確認
        assert 'viewport' in meta_info, "viewportメタタグが設定されていません"
        viewport = meta_info['viewport']
        assert 'width=device-width' in viewport, f"viewportにwidth=device-widthが含まれていません: {viewport}"
        assert 'initial-scale=1.0' in viewport, f"viewportにinitial-scale=1.0が含まれていません: {viewport}"
    
    def test_responsive_design(self, driver, app_server):
        """A1-003: レスポンシブデザイン確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        responsive_results = dashboard.perform_responsive_test()
        
        for breakpoint, result in responsive_results.items():
            assert result['layout_valid'], f"ブレークポイント {breakpoint} でレイアウトが正しくありません"
            assert result['no_horizontal_scroll'], f"ブレークポイント {breakpoint} で横スクロールが発生しています"
    
    def test_css_loading(self, driver, app_server):
        """A1-004: CSS読み込み確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        css_info = dashboard.check_css_loading()
        
        # CSS linkタグの存在確認
        assert len(css_info) > 0, "CSSファイルが読み込まれていません"
        
        for css in css_info:
            assert css['rel'] == 'stylesheet', f"rel属性がstylesheetではありません: {css}"
            assert css['href'] is not None, "href属性が設定されていません"
            assert len(css['href']) > 0, "href属性が空です"
    
    def test_error_page_handling(self, driver, app_server):
        """A1-005: エラーページ表示"""
        # 存在しないページにアクセス
        driver.get(f"{driver.current_url.split('/')[0]}//{driver.current_url.split('//')[1].split('/')[0]}/nonexistent")
        
        # 404エラーが適切に処理されていることを確認
        page_source = driver.page_source.lower()
        
        # 典型的なエラーページの要素をチェック
        error_indicators = ['404', 'not found', 'error', 'page not found']
        has_error_indication = any(indicator in page_source for indicator in error_indicators)
        
        assert has_error_indication, "404エラーページが適切に表示されていません"
    
    def test_main_heading_display(self, driver, app_server):
        """A2-001: ページロード成功"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        assert dashboard.is_page_loaded(), "ページが正常にロードされていません"
        
        # ページ構造の確認
        structure = dashboard.validate_page_structure()
        for element, present in structure.items():
            assert present, f"必要な要素が存在しません: {element}"
    
    def test_heading_content(self, driver, app_server):
        """A2-002: 見出し表示確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        heading = dashboard.get_main_heading_text()
        assert heading is not None, "メインヘディングが取得できません"
        assert len(heading.strip()) > 0, "メインヘディングが空です"
        assert "MFG Drone" in heading, f"期待する見出しテキストが含まれていません: {heading}"
    
    def test_description_content(self, driver, app_server):
        """A2-003: 説明文表示確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        description = dashboard.get_description_text()
        assert description is not None, "説明文が取得できません"
        assert len(description.strip()) > 0, "説明文が空です"
        
        # 期待するキーワードの確認
        expected_keywords = ["物体認識", "ドローン制御", "追跡"]
        for keyword in expected_keywords:
            assert keyword in description, f"説明文に期待するキーワードが含まれていません: {keyword}"
    
    def test_container_layout(self, driver, app_server):
        """A2-004: コンテナレイアウト"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        assert dashboard.has_container_element(), "コンテナ要素が存在しません"
        
        # コンテナの基本スタイル確認
        container_element = dashboard.wait_for_element(dashboard.CONTAINER)
        assert container_element is not None, "コンテナ要素が取得できません"
    
    def test_japanese_content_display(self, driver, app_server):
        """日本語コンテンツの正常表示確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        japanese_content = dashboard.check_japanese_content()
        
        assert japanese_content['heading_has_japanese'], "見出しに日本語が含まれていません"
        assert japanese_content['description_has_japanese'], "説明文に日本語が含まれていません"
        
        # 文字化けしていないことを確認
        heading_text = japanese_content['heading_text']
        description_text = japanese_content['description_text']
        
        # 文字化け文字（□、?など）が含まれていないことを確認
        assert '□' not in heading_text, "見出しに文字化け文字が含まれています"
        assert '?' not in heading_text or heading_text.count('?') < 3, "見出しに多数の文字化け文字が含まれています"
        assert '□' not in description_text, "説明文に文字化け文字が含まれています"
    
    def test_accessibility_basics(self, driver, app_server):
        """基本的なアクセシビリティ確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        accessibility = dashboard.check_accessibility_basics()
        
        # HTML lang属性の確認
        assert accessibility.get('html_lang'), "HTML要素にlang属性が設定されていません"
        
        # ページタイトルの確認
        assert accessibility['has_title'], "titleタグが存在しません"
        
        # H1見出しの確認
        assert accessibility['has_single_h1'], f"H1見出しが適切ではありません（数: {accessibility['h1_count']}）"
    
    def test_page_performance(self, driver, app_server):
        """ページパフォーマンス確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        performance = dashboard.get_page_performance_metrics()
        
        if 'error' not in performance:
            # 基本的なパフォーマンス指標の確認
            assert performance['loadEvent'] < 5000, f"ページロードが遅すぎます: {performance['loadEvent']}ms"
            assert performance['domComplete'] < 3000, f"DOM構築が遅すぎます: {performance['domComplete']}ms"
    
    def test_no_javascript_errors(self, driver, app_server):
        """JavaScriptエラーが無いことを確認"""
        dashboard = DashboardPage(driver)
        dashboard.open()
        
        validation = dashboard.validate_no_errors()
        
        assert validation['javascript_clean'], f"JavaScriptエラーが発生しています: {validation['javascript_errors']}"
        assert validation['page_loaded_successfully'], "ページが正常にロードされていません"


@pytest.mark.ui
@pytest.mark.component
class TestHealthCheckComponents:
    """ヘルスチェックAPIのコンポーネントテスト"""
    
    def test_health_endpoint_response(self, driver, app_server):
        """A3-001: ヘルスチェック応答"""
        health = HealthPage(driver)
        health.open()
        
        availability = health.validate_endpoint_availability()
        
        assert availability['overall_available'], "ヘルスチェックエンドポイントが利用できません"
        assert availability['browser_check']['page_accessible'], "ブラウザからアクセスできません"
        assert availability['api_check']['success'], "API経由でアクセスできません"
    
    def test_json_format_validation(self, driver, app_server):
        """A3-002: JSON形式確認"""
        health = HealthPage(driver)
        health.open()
        
        json_validation = health.validate_json_structure()
        
        assert json_validation['valid'], f"JSONレスポンスが無効です: {json_validation.get('error', '')}"
        assert json_validation['has_status_field'], "statusフィールドが存在しません"
        assert json_validation['status_is_healthy'], f"ステータスが正常ではありません: {json_validation['status_value']}"
    
    def test_error_handling_404(self, driver, app_server):
        """A3-003: 404エラーハンドリング"""
        health = HealthPage(driver)
        
        error_handling = health.check_error_handling()
        
        assert error_handling['normal_endpoint_works'], "正常なエンドポイントが動作していません"
        assert error_handling['handles_404_properly'], "404エラーが適切に処理されていません"
    
    def test_content_type_validation(self, driver, app_server):
        """Content-Type ヘッダーの確認"""
        health = HealthPage(driver)
        health.open()
        
        content_type_check = health.check_response_content_type()
        
        assert 'error' not in content_type_check, f"Content-Type確認でエラー: {content_type_check.get('error')}"
        assert content_type_check['is_json'], f"Content-TypeがJSONではありません: {content_type_check['content_type']}"
        assert content_type_check['is_valid_content_type'], f"無効なContent-Type: {content_type_check['content_type']}"
    
    def test_api_performance(self, driver, app_server):
        """APIパフォーマンステスト"""
        health = HealthPage(driver)
        
        performance = health.perform_performance_test()
        
        assert performance['success_rate'] >= 0.8, f"成功率が低すぎます: {performance['success_rate']}"
        assert performance['avg_response_time'] < 1.0, f"平均応答時間が遅すぎます: {performance['avg_response_time']}秒"
    
    def test_comprehensive_health_check(self, driver, app_server):
        """包括的ヘルスチェック"""
        health = HealthPage(driver)
        health.open()
        
        comprehensive = health.comprehensive_health_check()
        
        # 各項目の確認
        assert comprehensive['endpoint_availability']['overall_available'], "エンドポイントが利用できません"
        assert comprehensive['json_structure']['valid'], "JSONレスポンスが無効です"
        assert comprehensive['content_type']['is_json'], "Content-TypeがJSONではありません"
        assert comprehensive['performance']['success_rate'] >= 0.8, "パフォーマンスが不十分です"