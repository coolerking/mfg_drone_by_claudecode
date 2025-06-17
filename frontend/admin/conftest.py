"""
共通テスト設定・フィクスチャ
UIテスト用のSelenium WebDriver設定とユーティリティ
"""

import pytest
import time
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import subprocess
import threading
import requests
from flask import Flask


# テスト設定
TEST_CONFIG = {
    "base_url": "http://localhost:5001",
    "implicit_wait": 10,
    "explicit_wait": 20,
    "screenshot_dir": "tests/screenshots",
    "reports_dir": "tests/reports"
}

# ディレクトリ作成
for directory in [TEST_CONFIG["screenshot_dir"], TEST_CONFIG["reports_dir"]]:
    Path(directory).mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def app_server():
    """Flaskアプリケーションサーバーを起動・管理"""
    # main.pyが存在することを確認
    main_py_path = Path("main.py")
    if not main_py_path.exists():
        pytest.skip("main.py not found - skipping server tests")
    
    # Flaskサーバーをサブプロセスで起動
    server_process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # サーバー起動を待機
    max_wait = 30
    wait_time = 0
    while wait_time < max_wait:
        try:
            response = requests.get(f"{TEST_CONFIG['base_url']}/health", timeout=2)
            if response.status_code == 200:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(1)
        wait_time += 1
    else:
        server_process.terminate()
        pytest.fail("Failed to start Flask server within 30 seconds")
    
    yield server_process
    
    # テスト後のクリーンアップ
    server_process.terminate()
    server_process.wait()


@pytest.fixture(scope="session", params=["chrome", "firefox"])
def browser_name(request):
    """テスト実行ブラウザの選択"""
    return request.param


@pytest.fixture(scope="function")
def driver(request, browser_name):
    """WebDriverインスタンスの作成・管理"""
    driver_instance = None
    
    try:
        if browser_name == "chrome":
            driver_instance = create_chrome_driver(request)
        elif browser_name == "firefox":
            driver_instance = create_firefox_driver(request)
        else:
            pytest.skip(f"Unsupported browser: {browser_name}")
        
        # 基本設定
        driver_instance.implicitly_wait(TEST_CONFIG["implicit_wait"])
        driver_instance.maximize_window()
        
        yield driver_instance
        
    finally:
        if driver_instance:
            # 失敗時のスクリーンショット取得
            if request.node.rep_setup.failed or request.node.rep_call.failed:
                take_screenshot(driver_instance, request.node.name, browser_name)
            
            driver_instance.quit()


def create_chrome_driver(request):
    """Chrome WebDriverの作成"""
    options = ChromeOptions()
    
    # ヘッドレスモード（CI/CD環境用）
    if os.getenv("HEADLESS", "false").lower() == "true":
        options.add_argument("--headless=new")
    
    # Chrome固有のオプション
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def create_firefox_driver(request):
    """Firefox WebDriverの作成"""
    options = FirefoxOptions()
    
    # ヘッドレスモード（CI/CD環境用）
    if os.getenv("HEADLESS", "false").lower() == "true":
        options.add_argument("--headless")
    
    # Firefox固有のオプション
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)


def take_screenshot(driver, test_name, browser_name):
    """失敗時のスクリーンショット取得"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{browser_name}_{timestamp}.png"
    filepath = Path(TEST_CONFIG["screenshot_dir"]) / filename
    
    try:
        driver.save_screenshot(str(filepath))
        print(f"Screenshot saved: {filepath}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")


@pytest.fixture
def wait(driver):
    """WebDriverWaitインスタンス"""
    return WebDriverWait(driver, TEST_CONFIG["explicit_wait"])


@pytest.fixture
def base_url():
    """ベースURL"""
    return TEST_CONFIG["base_url"]


@pytest.fixture
def navigate_to_home(driver, base_url):
    """ホームページへのナビゲーション"""
    driver.get(base_url)
    return driver


@pytest.fixture
def navigate_to_health(driver, base_url):
    """ヘルスチェックエンドポイントへのナビゲーション"""
    driver.get(f"{base_url}/health")
    return driver


# テスト結果レポート用フック
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """テスト結果をitem.rep_*に保存（スクリーンショット判定用）"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def pytest_html_report_title(report):
    """HTMLレポートのタイトル"""
    report.title = "MFG Drone Admin Frontend - UI Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """HTMLレポートのサマリー情報"""
    prefix.extend([f"<p>Test executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"])
    prefix.extend([f"<p>Base URL: {TEST_CONFIG['base_url']}</p>"])


def pytest_configure(config):
    """pytest設定の追加"""
    # カスタムマーカーの説明
    config.addinivalue_line(
        "markers", "ui: UI tests using Selenium WebDriver"
    )
    config.addinivalue_line(
        "markers", "component: Component-level UI tests"
    )
    config.addinivalue_line(
        "markers", "scenario: User scenario tests"
    )
    config.addinivalue_line(
        "markers", "maintenance: Operations and maintenance tests"
    )
    config.addinivalue_line(
        "markers", "error_handling: Error handling tests"
    )


class UITestHelper:
    """UIテスト用ヘルパークラス"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def is_element_present(self, by, value):
        """要素の存在確認"""
        try:
            self.driver.find_element(by, value)
            return True
        except:
            return False
    
    def wait_for_element(self, by, value, timeout=None):
        """要素の出現待機"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_clickable(self, by, value, timeout=None):
        """要素のクリック可能状態待機"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def get_text_safe(self, by, value):
        """安全なテキスト取得"""
        try:
            element = self.driver.find_element(by, value)
            return element.text
        except:
            return ""
    
    def check_responsive_breakpoints(self):
        """レスポンシブデザインのブレークポイント確認"""
        breakpoints = [
            (320, 568),   # Mobile
            (768, 1024),  # Tablet
            (1024, 768),  # Desktop Small
            (1920, 1080)  # Desktop Large
        ]
        
        results = {}
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(0.5)  # レイアウト調整待機
            results[f"{width}x{height}"] = {
                "viewport": (width, height),
                "body_size": self.driver.execute_script(
                    "return [document.body.offsetWidth, document.body.offsetHeight]"
                )
            }
        
        # ウィンドウサイズを元に戻す
        self.driver.maximize_window()
        return results


@pytest.fixture
def ui_helper(driver, wait):
    """UIテストヘルパーインスタンス"""
    return UITestHelper(driver, wait)