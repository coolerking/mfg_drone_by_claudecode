"""
メインダッシュボードページのPage Object
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage


class DashboardPage(BasePage):
    """メインダッシュボードページ"""
    
    # ページ要素のロケーター
    PAGE_TITLE = (By.TAG_NAME, "title")
    MAIN_HEADING = (By.TAG_NAME, "h1")
    DESCRIPTION = (By.TAG_NAME, "p")
    CONTAINER = (By.CLASS_NAME, "container")
    BODY = (By.TAG_NAME, "body")
    HTML = (By.TAG_NAME, "html")
    HEAD = (By.TAG_NAME, "head")
    META_VIEWPORT = (By.CSS_SELECTOR, "meta[name='viewport']")
    META_CHARSET = (By.CSS_SELECTOR, "meta[charset]")
    CSS_LINK = (By.CSS_SELECTOR, "link[rel='stylesheet']")
    
    def __init__(self, driver, base_url="http://localhost:5001"):
        super().__init__(driver, base_url)
        self.page_path = "/"
    
    def open(self):
        """ダッシュボードページを開く"""
        super().open(self.page_path)
        self.wait_for_page_load()
        return self
    
    def is_page_loaded(self):
        """ページが正常にロードされたかチェック"""
        return (
            self.is_element_present(self.MAIN_HEADING) and
            self.is_element_present(self.CONTAINER) and
            self.wait_for_page_load()
        )
    
    def get_page_title(self):
        """ページタイトルを取得"""
        return self.get_title()
    
    def get_main_heading_text(self):
        """メインヘディングのテキストを取得"""
        return self.get_text(self.MAIN_HEADING)
    
    def get_description_text(self):
        """説明文のテキストを取得"""
        return self.get_text(self.DESCRIPTION)
    
    def has_container_element(self):
        """コンテナ要素が存在するかチェック"""
        return self.is_element_present(self.CONTAINER)
    
    def check_meta_tags(self):
        """メタタグの確認"""
        meta_info = {}
        
        # charset確認
        charset_element = self.wait_for_element(self.META_CHARSET, timeout=5)
        if charset_element:
            meta_info['charset'] = charset_element.get_attribute('charset')
        
        # viewport確認
        viewport_element = self.wait_for_element(self.META_VIEWPORT, timeout=5)
        if viewport_element:
            meta_info['viewport'] = viewport_element.get_attribute('content')
        
        return meta_info
    
    def check_css_loading(self):
        """CSS読み込み確認"""
        css_links = self.get_all_elements(self.CSS_LINK)
        css_info = []
        
        for link in css_links:
            css_info.append({
                'href': link.get_attribute('href'),
                'rel': link.get_attribute('rel'),
                'type': link.get_attribute('type')
            })
        
        return css_info
    
    def validate_page_structure(self):
        """ページ構造の妥当性確認"""
        validation_results = {
            'html_present': self.is_element_present(self.HTML),
            'head_present': self.is_element_present(self.HEAD),
            'body_present': self.is_element_present(self.BODY),
            'title_present': self.is_element_present(self.PAGE_TITLE),
            'main_heading_present': self.is_element_present(self.MAIN_HEADING),
            'container_present': self.is_element_present(self.CONTAINER),
            'description_present': self.is_element_present(self.DESCRIPTION)
        }
        
        return validation_results
    
    def check_content_validity(self):
        """コンテンツの妥当性確認"""
        content_check = {}
        
        # ページタイトル
        title = self.get_page_title()
        content_check['title_valid'] = bool(title and len(title.strip()) > 0)
        content_check['title_content'] = title
        
        # メインヘディング
        heading = self.get_main_heading_text()
        content_check['heading_valid'] = bool(heading and len(heading.strip()) > 0)
        content_check['heading_content'] = heading
        
        # 説明文
        description = self.get_description_text()
        content_check['description_valid'] = bool(description and len(description.strip()) > 0)
        content_check['description_content'] = description
        
        return content_check
    
    def check_japanese_content(self):
        """日本語コンテンツの確認"""
        heading = self.get_main_heading_text()
        description = self.get_description_text()
        
        # 日本語文字が含まれているかチェック
        def contains_japanese(text):
            if not text:
                return False
            japanese_ranges = [
                (0x3040, 0x309F),  # ひらがな
                (0x30A0, 0x30FF),  # カタカナ
                (0x4E00, 0x9FAF),  # 漢字
            ]
            return any(
                any(start <= ord(char) <= end for start, end in japanese_ranges)
                for char in text
            )
        
        return {
            'heading_has_japanese': contains_japanese(heading),
            'description_has_japanese': contains_japanese(description),
            'heading_text': heading,
            'description_text': description
        }
    
    def check_accessibility_basics(self):
        """基本的なアクセシビリティ確認"""
        accessibility_check = {}
        
        # lang属性の確認
        html_element = self.wait_for_element(self.HTML)
        if html_element:
            accessibility_check['html_lang'] = html_element.get_attribute('lang')
        
        # ページタイトルの確認
        accessibility_check['has_title'] = self.is_element_present(self.PAGE_TITLE)
        
        # メインヘディング（h1）の確認
        h1_elements = self.get_all_elements((By.TAG_NAME, "h1"))
        accessibility_check['h1_count'] = len(h1_elements)
        accessibility_check['has_single_h1'] = len(h1_elements) == 1
        
        return accessibility_check
    
    def perform_responsive_test(self):
        """レスポンシブデザインテスト"""
        return self.check_responsive_layout()
    
    def get_page_performance_metrics(self):
        """ページパフォーマンス指標の取得"""
        try:
            navigation_timing = self.execute_javascript("""
                var timing = window.performance.timing;
                return {
                    'domLoading': timing.domLoading - timing.navigationStart,
                    'domComplete': timing.domComplete - timing.navigationStart,
                    'loadEvent': timing.loadEventEnd - timing.navigationStart
                };
            """)
            return navigation_timing
        except Exception as e:
            return {'error': str(e)}
    
    def validate_no_errors(self):
        """ページエラーが無いことを確認"""
        # JavaScriptエラーチェック
        js_clean, js_errors = self.check_no_javascript_errors()
        
        # HTTP 200ステータスかチェック（ページが正常に表示されていることで推測）
        page_loaded = self.is_page_loaded()
        
        return {
            'javascript_clean': js_clean,
            'javascript_errors': js_errors,
            'page_loaded_successfully': page_loaded
        }