#!/usr/bin/env python3
"""
テスト環境セットアップ検証スクリプト
"""

import sys
import os
import importlib
from pathlib import Path


def check_python_version():
    """Python バージョンをチェック"""
    print("Python バージョンチェック...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Python 3.8+ が必要)")
        return False


def check_required_packages():
    """必要なパッケージがインストールされているかチェック"""
    print("\n必要なパッケージのチェック...")
    
    required_packages = {
        'flask': 'Flask',
        'pytest': 'pytest',
        'pytest_flask': 'pytest-flask',
        'pytest_cov': 'pytest-cov',
        'pytest_html': 'pytest-html',
        'coverage': 'coverage',
        'requests': 'requests',
        'responses': 'responses',
        'unittest.mock': 'unittest.mock (標準ライブラリ)'
    }
    
    all_installed = True
    
    for package, display_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} (インストールが必要)")
            all_installed = False
    
    return all_installed


def check_file_structure():
    """ファイル構造をチェック"""
    print("\nファイル構造のチェック...")
    
    base_dir = Path(__file__).parent
    required_files = [
        "main.py",
        "requirements.txt",
        "test_requirements.txt",
        "pytest.ini",
        "conftest.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/unit/test_main_app.py",
        "tests/unit/test_services.py",
        "tests/unit/test_blueprints.py",
        "tests/unit/test_utils.py",
        "tests/test_runner.py"
    ]
    
    all_exists = True
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (ファイルが見つかりません)")
            all_exists = False
    
    return all_exists


def check_flask_app():
    """Flask アプリケーションが正常に起動できるかチェック"""
    print("\nFlask アプリケーションのチェック...")
    
    try:
        # main.py を import して基本的な動作確認
        sys.path.insert(0, str(Path(__file__).parent))
        import main
        
        app = main.app
        if app is not None:
            print(f"✓ Flask アプリケーション作成成功")
            
            # テストモードでの動作確認
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/')
                if response.status_code == 200:
                    print("✓ インデックスページ応答正常")
                else:
                    print(f"✗ インデックスページ応答異常 (ステータス: {response.status_code})")
                    return False
                
                response = client.get('/health')
                if response.status_code == 200:
                    print("✓ ヘルスチェックエンドポイント正常")
                else:
                    print(f"✗ ヘルスチェックエンドポイント異常 (ステータス: {response.status_code})")
                    return False
            
            return True
        else:
            print("✗ Flask アプリケーション作成失敗")
            return False
            
    except Exception as e:
        print(f"✗ Flask アプリケーションエラー: {e}")
        return False


def check_test_configuration():
    """テスト設定をチェック"""
    print("\nテスト設定のチェック...")
    
    try:
        # pytest.ini の存在確認
        pytest_ini = Path(__file__).parent / "pytest.ini"
        if pytest_ini.exists():
            print("✓ pytest.ini 設定ファイル存在")
        else:
            print("✗ pytest.ini 設定ファイルが見つかりません")
            return False
        
        # conftest.py の基本確認
        sys.path.insert(0, str(Path(__file__).parent))
        import conftest
        print("✓ conftest.py 読み込み成功")
        
        return True
    except Exception as e:
        print(f"✗ テスト設定エラー: {e}")
        return False


def run_basic_test():
    """基本的なテストを実行"""
    print("\n基本テストの実行...")
    
    try:
        import subprocess
        import os
        
        # 現在のディレクトリを変更
        original_dir = os.getcwd()
        test_dir = Path(__file__).parent
        os.chdir(test_dir)
        
        # 単純なテストを実行
        cmd = [sys.executable, "-m", "pytest", "tests/unit/test_main_app.py::TestMainApp::test_app_creation", "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # 元のディレクトリに戻る
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✓ 基本テスト実行成功")
            return True
        else:
            print("✗ 基本テスト実行失敗")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ テスト実行タイムアウト")
        return False
    except Exception as e:
        print(f"✗ テスト実行エラー: {e}")
        return False


def generate_summary_report(results):
    """サマリーレポートを生成"""
    print("\n" + "=" * 60)
    print("テスト環境検証結果サマリー")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    for check_name, result in results.items():
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{check_name:30} {status}")
    
    print("-" * 60)
    print(f"総合結果: {passed_checks}/{total_checks} 項目成功")
    
    if passed_checks == total_checks:
        print("🎉 すべての検証項目が成功しました！")
        print("テスト実行コマンド:")
        print("  python tests/test_runner.py --type unit --verbose")
        print("  python tests/test_runner.py --type all --coverage --html")
        return True
    else:
        print("⚠️  一部の検証項目が失敗しました")
        print("エラーを修正してから再度実行してください")
        return False


def main():
    """メイン関数"""
    print("管理者用フロントエンドサーバ テスト環境検証")
    print("=" * 60)
    
    # 各種チェックを実行
    results = {
        "Python バージョン": check_python_version(),
        "必要パッケージ": check_required_packages(),
        "ファイル構造": check_file_structure(),
        "Flask アプリケーション": check_flask_app(),
        "テスト設定": check_test_configuration(),
        "基本テスト実行": run_basic_test()
    }
    
    # サマリーレポート生成
    success = generate_summary_report(results)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()