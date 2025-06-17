#!/usr/bin/env python3
"""
UIテスト環境検証スクリプト
テスト実行前の環境・依存関係・設定の包括的検証
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path
import requests
import time


class UITestValidator:
    """UIテスト環境の検証クラス"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def check(self, description, condition, error_msg=None, warning_msg=None):
        """検証チェックの実行"""
        self.checks_total += 1
        print(f"  {'✓' if condition else '❌'} {description}")
        
        if condition:
            self.checks_passed += 1
        else:
            if error_msg:
                self.errors.append(f"{description}: {error_msg}")
            elif warning_msg:
                self.warnings.append(f"{description}: {warning_msg}")
            else:
                self.errors.append(description)
    
    def validate_python_environment(self):
        """Python環境の検証"""
        print("\n🐍 Python環境の検証")
        
        # Python バージョン
        python_version = sys.version_info
        self.check(
            f"Python バージョン確認 (現在: {python_version.major}.{python_version.minor}.{python_version.micro})",
            python_version >= (3, 8),
            "Python 3.8以上が必要です"
        )
        
        # 基本モジュール
        required_modules = [
            "pytest",
            "selenium",
            "requests",
            "pathlib"
        ]
        
        for module in required_modules:
            try:
                imported_module = importlib.import_module(module)
                version = getattr(imported_module, '__version__', 'unknown')
                self.check(
                    f"{module} モジュール (バージョン: {version})",
                    True
                )
            except ImportError:
                self.check(
                    f"{module} モジュール",
                    False,
                    f"{module} がインストールされていません"
                )
    
    def validate_selenium_dependencies(self):
        """Selenium依存関係の検証"""
        print("\n🌐 Selenium依存関係の検証")
        
        # Selenium WebDriver関連
        selenium_modules = [
            "selenium.webdriver",
            "selenium.webdriver.common.by",
            "selenium.webdriver.support.ui",
            "selenium.webdriver.support.expected_conditions"
        ]
        
        for module in selenium_modules:
            try:
                importlib.import_module(module)
                self.check(f"{module}", True)
            except ImportError:
                self.check(
                    f"{module}",
                    False,
                    f"Seleniumモジュール {module} が利用できません"
                )
        
        # WebDriver Manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.firefox import GeckoDriverManager
            self.check("webdriver-manager (Chrome)", True)
            self.check("webdriver-manager (Firefox)", True)
        except ImportError:
            self.check(
                "webdriver-manager",
                False,
                "webdriver-manager がインストールされていません"
            )
    
    def validate_pytest_configuration(self):
        """pytest設定の検証"""
        print("\n🧪 pytest設定の検証")
        
        # pytest.ini ファイル
        pytest_ini = Path("pytest.ini")
        self.check(
            "pytest.ini ファイル存在",
            pytest_ini.exists(),
            "pytest.ini ファイルが見つかりません"
        )
        
        if pytest_ini.exists():
            try:
                content = pytest_ini.read_text(encoding='utf-8')
                
                # 重要な設定項目のチェック
                important_configs = [
                    "testpaths = tests",
                    "markers =",
                    "--html=",
                    "--json-report"
                ]
                
                for config in important_configs:
                    self.check(
                        f"pytest.ini 設定: {config.split('=')[0].strip()}",
                        config in content,
                        f"pytest.ini に {config} 設定が見つかりません"
                    )
            except Exception as e:
                self.check(
                    "pytest.ini 読み込み",
                    False,
                    f"pytest.ini の読み込みエラー: {e}"
                )
        
        # conftest.py ファイル
        conftest_py = Path("conftest.py")
        self.check(
            "conftest.py ファイル存在",
            conftest_py.exists(),
            "conftest.py ファイルが見つかりません"
        )
    
    def validate_test_structure(self):
        """テスト構造の検証"""
        print("\n📁 テスト構造の検証")
        
        # 必要なディレクトリ
        required_directories = [
            "tests",
            "tests/pages"
        ]
        
        for directory in required_directories:
            dir_path = Path(directory)
            self.check(
                f"ディレクトリ: {directory}",
                dir_path.exists() and dir_path.is_dir(),
                f"ディレクトリ {directory} が存在しません"
            )
        
        # 必要なテストファイル
        required_test_files = [
            "tests/test_ui_components.py",
            "tests/test_user_scenarios.py",
            "tests/test_maintenance_scenarios.py",
            "tests/test_error_handling.py"
        ]
        
        for test_file in required_test_files:
            file_path = Path(test_file)
            self.check(
                f"テストファイル: {test_file}",
                file_path.exists(),
                f"テストファイル {test_file} が存在しません"
            )
        
        # Page Object ファイル
        page_object_files = [
            "tests/pages/__init__.py",
            "tests/pages/base_page.py",
            "tests/pages/dashboard_page.py",
            "tests/pages/health_page.py"
        ]
        
        for page_file in page_object_files:
            file_path = Path(page_file)
            self.check(
                f"Page Object: {page_file}",
                file_path.exists(),
                f"Page Object ファイル {page_file} が存在しません"
            )
    
    def validate_application_server(self):
        """アプリケーションサーバーの検証"""
        print("\n🚀 アプリケーションサーバーの検証")
        
        # main.py ファイル
        main_py = Path("main.py")
        self.check(
            "main.py ファイル存在",
            main_py.exists(),
            "main.py ファイルが見つかりません"
        )
        
        # Flask の起動確認
        if main_py.exists():
            try:
                # サーバーが既に起動しているかチェック
                response = requests.get("http://localhost:5001/health", timeout=5)
                self.check(
                    "アプリケーションサーバー応答 (既存)",
                    response.status_code == 200,
                    warning_msg="サーバーが応答しません（テスト時に自動起動されます）"
                )
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        self.check(
                            "ヘルスチェックAPI レスポンス",
                            'status' in json_data and json_data['status'] == 'healthy',
                            "ヘルスチェックAPIが正常な応答を返していません"
                        )
                    except Exception:
                        self.check(
                            "ヘルスチェックAPI JSON",
                            False,
                            "ヘルスチェックAPIのJSONレスポンスが無効です"
                        )
                
            except requests.RequestException:
                self.check(
                    "アプリケーションサーバー応答",
                    False,
                    warning_msg="サーバーが起動していません（テスト時に自動起動されます）"
                )
    
    def validate_browser_environment(self):
        """ブラウザ環境の検証"""
        print("\n🌐 ブラウザ環境の検証")
        
        # Chrome WebDriver
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            
            self.check("Chrome WebDriver", True)
        except Exception as e:
            self.check(
                "Chrome WebDriver",
                False,
                f"Chrome WebDriverの初期化エラー: {e}"
            )
        
        # Firefox WebDriver
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.firefox.service import Service as FirefoxService
            
            options = FirefoxOptions()
            options.add_argument("--headless")
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.quit()
            
            self.check("Firefox WebDriver", True)
        except Exception as e:
            self.check(
                "Firefox WebDriver",
                False,
                warning_msg=f"Firefox WebDriver利用不可: {e}"
            )
    
    def validate_test_dependencies(self):
        """テスト専用依存関係の検証"""
        print("\n📦 テスト専用依存関係の検証")
        
        # test_requirements.txt
        test_req_file = Path("test_requirements.txt")
        self.check(
            "test_requirements.txt ファイル",
            test_req_file.exists(),
            "test_requirements.txt ファイルが見つかりません"
        )
        
        # pytest プラグイン
        pytest_plugins = [
            "pytest_html",
            "pytest_selenium", 
            "pytest_cov",
            "pytest_xdist"
        ]
        
        for plugin in pytest_plugins:
            try:
                importlib.import_module(plugin)
                self.check(f"pytest プラグイン: {plugin}", True)
            except ImportError:
                self.check(
                    f"pytest プラグイン: {plugin}",
                    False,
                    warning_msg=f"{plugin} が利用できません"
                )
    
    def validate_system_requirements(self):
        """システム要件の検証"""
        print("\n💻 システム要件の検証")
        
        # ディスプレイ環境（ヘッドレステスト用）
        display_env = os.environ.get('DISPLAY')
        if display_env:
            self.check("DISPLAY 環境変数", True)
        else:
            self.check(
                "DISPLAY 環境変数",
                False,
                warning_msg="DISPLAY環境変数が設定されていません（ヘッドレスモードで実行されます）"
            )
        
        # メモリ要件（概算）
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            self.check(
                f"利用可能メモリ ({available_gb:.1f}GB)",
                available_gb >= 1.0,
                f"メモリが不足している可能性があります: {available_gb:.1f}GB"
            )
        except ImportError:
            self.check(
                "メモリ情報",
                False,
                warning_msg="psutil が利用できないためメモリチェックをスキップします"
            )
    
    def run_validation(self):
        """全体検証の実行"""
        print("🔍 UIテスト環境検証を開始します...")
        print("=" * 60)
        
        # 各検証項目の実行
        self.validate_python_environment()
        self.validate_selenium_dependencies()
        self.validate_pytest_configuration()
        self.validate_test_structure()
        self.validate_application_server()
        self.validate_browser_environment()
        self.validate_test_dependencies()
        self.validate_system_requirements()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 検証結果サマリー")
        print(f"   総チェック項目: {self.checks_total}")
        print(f"   ✅ 成功: {self.checks_passed}")
        print(f"   ❌ 失敗: {len(self.errors)}")
        print(f"   ⚠️  警告: {len(self.warnings)}")
        
        success_rate = (self.checks_passed / self.checks_total) * 100 if self.checks_total > 0 else 0
        print(f"   成功率: {success_rate:.1f}%")
        
        # エラー詳細
        if self.errors:
            print("\n❌ エラー詳細:")
            for error in self.errors:
                print(f"   • {error}")
        
        # 警告詳細
        if self.warnings:
            print("\n⚠️  警告詳細:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # 推奨アクション
        print("\n💡 推奨アクション:")
        if self.errors:
            print("   1. 上記エラーを解決してからテストを実行してください")
            print("   2. 依存関係: pip install -r test_requirements.txt")
            print("   3. ブラウザドライバーの手動インストールが必要な場合があります")
        elif self.warnings:
            print("   1. 警告項目を確認してください（テスト実行は可能です）")
            print("   2. より良いテスト環境のため警告項目の解決を推奨します")
        else:
            print("   🎉 環境は完全に準備されています！")
            print("   テストを実行する準備が整いました")
        
        # 終了判定
        critical_errors = [e for e in self.errors if "ファイルが見つかりません" in e or "インストールされていません" in e]
        
        if critical_errors:
            print("\n🚨 重大なエラーが検出されました")
            return False
        elif len(self.errors) > self.checks_total * 0.3:  # 30%以上失敗
            print("\n⚠️  多数のエラーが検出されました")
            return False
        else:
            print("\n✅ 環境検証が正常に完了しました")
            return True


def main():
    """メイン実行関数"""
    print("🎯 フェーズ4 UIテスト環境検証スクリプト")
    
    validator = UITestValidator()
    validation_success = validator.run_validation()
    
    if validation_success:
        print("\n🚀 UIテストを実行する準備が整いました！")
        print("   実行コマンド例:")
        print("   python tests/run_ui_tests.py --type all")
        print("   python tests/run_ui_tests.py --type component --no-headless")
        sys.exit(0)
    else:
        print("\n🔧 環境の修正が必要です")
        print("   上記のエラー・警告を確認して環境を整備してください")
        sys.exit(1)


if __name__ == "__main__":
    main()