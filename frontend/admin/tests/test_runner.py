#!/usr/bin/env python3
"""
テスト実行制御スクリプト
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, html_report=False):
    """
    テストを実行する
    
    Args:
        test_type (str): 実行するテストの種類 ("unit", "integration", "ui", "all")
        verbose (bool): 詳細出力フラグ
        coverage (bool): カバレッジレポート生成フラグ
        html_report (bool): HTMLレポート生成フラグ
    """
    # ベースディレクトリの設定
    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)
    
    # pytest コマンドの構築
    cmd = ["python", "-m", "pytest"]
    
    # テストタイプに応じたパス指定
    if test_type == "unit":
        cmd.append("tests/unit/")
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.append("tests/integration/")
        cmd.extend(["-m", "integration"])
    elif test_type == "mock_backend":
        cmd.append("tests/integration/mock_backend/")
        cmd.extend(["-m", "mock_backend"])
    elif test_type == "real_backend":
        cmd.append("tests/integration/real_backend/")
        cmd.extend(["-m", "real_backend"])
    elif test_type == "ui":
        cmd.append("tests/ui/")
        cmd.extend(["-m", "ui"])
    elif test_type == "all":
        cmd.append("tests/")
        # 実機が必要なテストは除外
        cmd.extend(["-m", "not requires_hardware"])
    else:
        print(f"不明なテストタイプ: {test_type}")
        return False
    
    # オプションの追加
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
        if html_report:
            cmd.extend(["--cov-report=html", "--cov-report=xml"])
    
    if html_report:
        cmd.extend(["--html=tests/reports/report.html", "--self-contained-html"])
    
    # テストレポートディレクトリの作成
    reports_dir = base_dir / "tests" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    print(f"実行コマンド: {' '.join(cmd)}")
    print(f"作業ディレクトリ: {base_dir}")
    print("=" * 60)
    
    try:
        # テストの実行
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("エラー: pytest が見つかりません。以下のコマンドでインストールしてください:")
        print("pip install -r test_requirements.txt")
        return False
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        return False


def check_dependencies():
    """
    必要な依存関係がインストールされているかチェック
    """
    required_packages = [
        "pytest",
        "pytest-flask",
        "pytest-cov",
        "pytest-html",
        "coverage"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("以下のパッケージがインストールされていません:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n以下のコマンドでインストールしてください:")
        print("pip install -r test_requirements.txt")
        return False
    
    return True


def generate_coverage_report():
    """
    カバレッジレポートを生成
    """
    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)
    
    cmd = [
        "python", "-m", "coverage", "html",
        "--directory=tests/reports/coverage_html"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("カバレッジレポートが生成されました: tests/reports/coverage_html/index.html")
        return True
    except subprocess.CalledProcessError:
        print("カバレッジレポートの生成に失敗しました")
        return False


def list_available_tests():
    """
    利用可能なテストの一覧を表示
    """
    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)
    
    cmd = ["python", "-m", "pytest", "--collect-only", "-q"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("利用可能なテスト:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"テスト一覧の取得に失敗しました: {e}")
        return False


def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(description="管理者用フロントエンドのテスト実行ツール")
    
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "mock_backend", "real_backend", "ui", "all"],
        default="unit",
        help="実行するテストの種類 (デフォルト: unit)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="カバレッジレポート生成"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="HTMLレポート生成"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="依存関係のチェック"
    )
    
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="利用可能なテストの一覧表示"
    )
    
    parser.add_argument(
        "--coverage-report",
        action="store_true",
        help="カバレッジレポートのみ生成"
    )
    
    args = parser.parse_args()
    
    # 依存関係チェック
    if args.check_deps:
        if check_dependencies():
            print("すべての依存関係がインストールされています ✓")
        return
    
    # テスト一覧表示
    if args.list_tests:
        list_available_tests()
        return
    
    # カバレッジレポートのみ生成
    if args.coverage_report:
        generate_coverage_report()
        return
    
    # 依存関係の事前チェック
    if not check_dependencies():
        return
    
    print("管理者用フロントエンドサーバ テスト実行")
    print("=" * 60)
    print(f"テストタイプ: {args.type}")
    print(f"詳細出力: {args.verbose}")
    print(f"カバレッジ: {args.coverage}")
    print(f"HTMLレポート: {args.html}")
    print("=" * 60)
    
    # テスト実行
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        html_report=args.html
    )
    
    # 結果の表示
    print("=" * 60)
    if success:
        print("✓ すべてのテストが成功しました")
        
        # カバレッジレポートの生成
        if args.coverage and args.html:
            generate_coverage_report()
    else:
        print("✗ テストが失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()