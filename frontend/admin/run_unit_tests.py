#!/usr/bin/env python3
"""
管理用フロントエンドサーバ単体テスト実行スクリプト
バックエンドサーバやドローン実機なしで実行可能
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse


def setup_environment():
    """テスト環境のセットアップ"""
    # プロジェクトルートディレクトリをPythonパスに追加
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # テスト用環境変数を設定
    test_env = {
        'BACKEND_API_URL': 'http://localhost:8000',
        'SECRET_KEY': 'test-secret-key-for-unit-tests',
        'FLASK_DEBUG': 'False',
        'FLASK_ENV': 'testing',
        'TESTING': 'True'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    print("✅ テスト環境セットアップ完了")
    return test_env


def check_dependencies():
    """必要な依存関係の確認"""
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 不足している依存関係: {', '.join(missing_packages)}")
        print("以下のコマンドで依存関係をインストールしてください:")
        print(f"pip install -r test_requirements.txt")
        return False
    
    print("✅ 依存関係確認完了")
    return True


def run_unit_tests(test_type='all', verbose=False, coverage=True):
    """単体テストの実行"""
    
    # テストファイルパターンの定義
    test_patterns = {
        'all': 'test_drone_api_client*.py test_flask_routes*.py',
        'api_client': 'test_drone_api_client*.py',
        'flask_routes': 'test_flask_routes*.py',
        'basic': 'test_drone_api_client.py test_flask_routes.py',
        'advanced': 'test_drone_api_client_advanced.py test_flask_routes_advanced.py'
    }
    
    if test_type not in test_patterns:
        print(f"❌ 無効なテストタイプ: {test_type}")
        print(f"有効なタイプ: {', '.join(test_patterns.keys())}")
        return False
    
    # pytestコマンドの構築
    cmd = [
        'python', '-m', 'pytest',
        '-c', 'pytest_unit.ini',  # 単体テスト用設定ファイル
        '--tb=short'
    ]
    
    # カバレッジオプション
    if coverage:
        cmd.extend([
            '--cov=main',
            '--cov-report=html:tests/reports/coverage_html',
            '--cov-report=term-missing',
            '--cov-fail-under=85'
        ])
    
    # 詳細出力オプション
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # レポート出力
    cmd.extend([
        '--html=tests/reports/unit_test_report.html',
        '--self-contained-html'
    ])
    
    # テストファイルパターンの追加
    test_files = test_patterns[test_type].split()
    for test_file in test_files:
        cmd.append(f'tests/{test_file}')
    
    print(f"🧪 単体テスト実行開始 (タイプ: {test_type})")
    print(f"📍 コマンド: {' '.join(cmd)}")
    print("=" * 60)
    
    # テスト実行
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, check=False)
        
        print("=" * 60)
        if result.returncode == 0:
            print("✅ 単体テスト実行成功!")
        else:
            print("❌ 単体テスト実行で問題が発生しました")
        
        # レポートファイルの存在確認
        report_dir = Path(__file__).parent / 'tests' / 'reports'
        if (report_dir / 'unit_test_report.html').exists():
            print(f"📊 HTMLレポート: {report_dir / 'unit_test_report.html'}")
        
        if coverage and (report_dir / 'coverage_html' / 'index.html').exists():
            print(f"📊 カバレッジレポート: {report_dir / 'coverage_html' / 'index.html'}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ テスト実行中にエラーが発生しました: {e}")
        return False


def validate_independent_execution():
    """独立実行の検証"""
    print("🔍 独立実行検証中...")
    
    # バックエンドサーバーへの接続確認（接続できないことを確認）
    import requests
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            print("⚠️  バックエンドサーバーが起動している可能性があります")
            print("   単体テストの独立性を確保するため、バックエンドサーバーを停止してください")
            return False
    except (requests.ConnectionError, requests.Timeout):
        # 接続できないのが正常（独立実行）
        pass
    
    print("✅ 独立実行検証完了（バックエンドサーバー非依存）")
    return True


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='管理用フロントエンドサーバ単体テスト実行')
    parser.add_argument('--type', choices=['all', 'api_client', 'flask_routes', 'basic', 'advanced'],
                        default='all', help='実行するテストタイプ')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
    parser.add_argument('--no-coverage', action='store_true', help='カバレッジ測定を無効化')
    parser.add_argument('--skip-validation', action='store_true', help='独立実行検証をスキップ')
    
    args = parser.parse_args()
    
    print("🚁 MFG Drone Admin Frontend - 単体テスト実行")
    print("=" * 60)
    
    # 環境セットアップ
    if not setup_environment():
        sys.exit(1)
    
    # 依存関係確認
    if not check_dependencies():
        sys.exit(1)
    
    # 独立実行検証
    if not args.skip_validation and not validate_independent_execution():
        print("独立実行検証をスキップするには --skip-validation オプションを使用してください")
        sys.exit(1)
    
    # レポートディレクトリ作成
    report_dir = Path(__file__).parent / 'tests' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # テスト実行
    success = run_unit_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage
    )
    
    if success:
        print("\n🎉 すべてのテストが完了しました!")
        sys.exit(0)
    else:
        print("\n💥 テストで問題が発生しました")
        sys.exit(1)


if __name__ == '__main__':
    main()