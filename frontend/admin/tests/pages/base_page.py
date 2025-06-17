"""
Page Object パターン基底クラス
全ページオブジェクトの共通機能を提供
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class BasePage:
    """Page Object パターンの基底クラス"""
    
    def __init__(self, driver, base_url="http://localhost:5001"):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.base_url = base_url
    
    def open(self, path=""):
        """ページを開く"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)
        return self
    
    def get_title(self):
        """ページタイトルを取得"""
        return self.driver.title
    
    def get_current_url(self):
        """現在のURLを取得"""
        return self.driver.current_url
    
    def is_element_present(self, locator):
        """要素の存在確認"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def wait_for_element(self, locator, timeout=20):
        """要素の出現待機"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            return None
    
    def wait_for_clickable(self, locator, timeout=20):
        """要素のクリック可能状態待機"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            return None
    
    def click_element(self, locator):
        """要素をクリック"""
        element = self.wait_for_clickable(locator)
        if element:
            element.click()
            return True
        return False
    
    def get_text(self, locator):
        """要素のテキストを取得"""
        element = self.wait_for_element(locator)
        if element:
            return element.text
        return ""
    
    def get_attribute(self, locator, attribute):
        """要素の属性値を取得"""
        element = self.wait_for_element(locator)
        if element:
            return element.get_attribute(attribute)
        return ""
    
    def type_text(self, locator, text):
        """テキストを入力"""
        element = self.wait_for_clickable(locator)
        if element:
            element.clear()
            element.send_keys(text)
            return True
        return False
    
    def wait_for_page_load(self, timeout=30):
        """ページロード完了を待機"""
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, locator):
        """要素までスクロール"""
        element = self.wait_for_element(locator)
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)  # スクロール完了待機
            return True
        return False
    
    def take_screenshot(self, filename):
        """スクリーンショット撮影"""
        try:
            self.driver.save_screenshot(filename)
            return True
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False
    
    def execute_javascript(self, script, *args):
        """JavaScript実行"""
        return self.driver.execute_script(script, *args)
    
    def refresh_page(self):
        """ページリフレッシュ"""
        self.driver.refresh()
        self.wait_for_page_load()
    
    def get_page_source(self):
        """ページソースを取得"""
        return self.driver.page_source
    
    def check_no_javascript_errors(self):
        """JavaScriptエラーの確認"""
        logs = self.driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        return len(js_errors) == 0, js_errors
    
    def get_viewport_size(self):
        """ビューポートサイズを取得"""
        return self.driver.execute_script(
            "return [window.innerWidth, window.innerHeight]"
        )
    
    def set_viewport_size(self, width, height):
        """ビューポートサイズを設定"""
        self.driver.set_window_size(width, height)
        time.sleep(0.5)  # リサイズ完了待機
    
    def wait_for_ajax_complete(self, timeout=30):
        """AJAX処理完了を待機"""
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return jQuery.active == 0")
            )
            return True
        except (TimeoutException, Exception):
            # jQueryが無い場合は標準的な待機
            time.sleep(1)
            return True
    
    def check_responsive_layout(self):
        """レスポンシブレイアウトの確認"""
        breakpoints = [
            (320, 568),   # Mobile
            (768, 1024),  # Tablet
            (1024, 768),  # Desktop Small
            (1920, 1080)  # Desktop Large
        ]
        
        original_size = self.get_viewport_size()
        results = {}
        
        for width, height in breakpoints:
            self.set_viewport_size(width, height)
            results[f"{width}x{height}"] = {
                "viewport": (width, height),
                "layout_valid": self._validate_responsive_layout(),
                "no_horizontal_scroll": self._check_no_horizontal_scroll()
            }
        
        # 元のサイズに戻す
        self.set_viewport_size(*original_size)
        return results
    
    def _validate_responsive_layout(self):
        """レスポンシブレイアウトの妥当性確認"""
        # 基本的なレイアウト要素が適切に表示されているかチェック
        viewport_width = self.execute_javascript("return window.innerWidth")
        body_width = self.execute_javascript("return document.body.offsetWidth")
        
        # 横スクロールが発生していないことを確認
        return body_width <= viewport_width
    
    def _check_no_horizontal_scroll(self):
        """横スクロールが発生していないことを確認"""
        scroll_width = self.execute_javascript("return document.body.scrollWidth")
        client_width = self.execute_javascript("return document.body.clientWidth")
        return scroll_width <= client_width
    
    def wait_for_element_not_present(self, locator, timeout=10):
        """要素が存在しないことを確認"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until_not(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def get_all_elements(self, locator):
        """複数要素を取得"""
        try:
            return self.driver.find_elements(*locator)
        except NoSuchElementException:
            return []
    
    def hover_element(self, locator):
        """要素にホバー"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.wait_for_element(locator)
        if element:
            ActionChains(self.driver).move_to_element(element).perform()
            time.sleep(0.5)
            return True
        return False