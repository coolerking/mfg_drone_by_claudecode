#!/usr/bin/env python3
"""
簡単なテスト実行確認用スクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_flask_app_basic():
    """Flask アプリケーションの基本テスト"""
    try:
        print("Flask アプリケーションのインポートテスト...")
        import main
        
        app = main.app
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # インデックスページのテスト
            print("インデックスページのテスト...")
            response = client.get('/')
            assert response.status_code == 200
            assert 'MFG Drone' in response.get_data(as_text=True)
            print("✓ インデックスページ正常")
            
            # ヘルスチェックのテスト
            print("ヘルスチェックのテスト...")
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            print("✓ ヘルスチェック正常")
        
        print("✓ Flask アプリケーション基本テスト成功")
        return True
        
    except Exception as e:
        print(f"✗ Flask アプリケーションテスト失敗: {e}")
        return False

def test_conftest_import():
    """conftest.py のインポートテスト"""
    try:
        print("conftest.py のインポートテスト...")
        import conftest
        print("✓ conftest.py インポート成功")
        return True
    except Exception as e:
        print(f"✗ conftest.py インポート失敗: {e}")
        return False

def test_unit_test_files():
    """単体テストファイルのインポートテスト"""
    test_files = [
        'tests.unit.test_main_app',
        'tests.unit.test_services', 
        'tests.unit.test_blueprints',
        'tests.unit.test_utils'
    ]
    
    success_count = 0
    for test_file in test_files:
        try:
            print(f"{test_file} のインポートテスト...")
            __import__(test_file)
            print(f"✓ {test_file} インポート成功")
            success_count += 1
        except Exception as e:
            print(f"✗ {test_file} インポート失敗: {e}")
    
    print(f"単体テストファイル: {success_count}/{len(test_files)} 成功")
    return success_count == len(test_files)

def main():
    """メイン関数"""
    print("管理者用フロントエンドサーバ 簡単テスト実行")
    print("=" * 50)
    
    tests = [
        ("Flask アプリケーション基本", test_flask_app_basic),
        ("conftest.py インポート", test_conftest_import),
        ("単体テストファイル", test_unit_test_files)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{test_name}テスト実行中...")
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results.items():
        status = "成功" if result else "失敗"
        print(f"{test_name:20} {status}")
        if result:
            success_count += 1
    
    print(f"\n総合結果: {success_count}/{len(tests)} テスト成功")
    
    if success_count == len(tests):
        print("🎉 すべてのテストが成功しました！")
        print("\n次のステップ:")
        print("1. pip install -r test_requirements.txt")
        print("2. python tests/test_runner.py --type unit --verbose")
        return True
    else:
        print("⚠️ 一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)