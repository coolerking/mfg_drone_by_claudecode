#!/usr/bin/env python3
"""
UIテスト実行スクリプト
フェーズ4 UIテストの包括的実行・レポート生成
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
import json


def setup_environment():
    """テスト環境のセットアップ"""
    print("🔧 テスト環境をセットアップしています...")
    
    # 必要なディレクトリの作成
    directories = [
        "tests/reports",
        "tests/screenshots",
        "tests/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ ディレクトリ作成: {directory}")
    
    print("✅ テスト環境セットアップ完了")


def check_dependencies():
    """依存関係の確認"""
    print("📦 依存関係を確認しています...")
    
    try:
        import pytest
        import selenium
        print(f"   ✓ pytest: {pytest.__version__}")
        print(f"   ✓ selenium: {selenium.__version__}")
    except ImportError as e:
        print(f"   ❌ 依存関係が不足しています: {e}")
        print("   pip install -r test_requirements.txt を実行してください")
        return False
    
    print("✅ 依存関係確認完了")
    return True


def run_tests(test_type="all", browsers=None, headless=True, verbose=True, coverage=False):
    """テストの実行"""
    if browsers is None:
        browsers = ["chrome"]  # デフォルトはChromeのみ
    
    print(f"🚀 UIテストを実行しています...")
    print(f"   テストタイプ: {test_type}")
    print(f"   ブラウザ: {', '.join(browsers)}")
    print(f"   ヘッドレスモード: {headless}")
    
    # 環境変数の設定
    env = os.environ.copy()
    if headless:
        env["HEADLESS"] = "true"
    
    # pytest実行コマンドの構築
    cmd = ["python", "-m", "pytest"]
    
    # テストタイプに応じたマーカーの設定
    if test_type == "component":
        cmd.extend(["-m", "component"])
    elif test_type == "scenario":
        cmd.extend(["-m", "scenario"])
    elif test_type == "maintenance":
        cmd.extend(["-m", "maintenance"])
    elif test_type == "error_handling":
        cmd.extend(["-m", "error_handling"])
    elif test_type == "smoke":
        cmd.extend(["-m", "smoke"])
    elif test_type == "critical":
        cmd.extend(["-m", "critical"])
    # "all"の場合はマーカー指定なし
    
    # ブラウザ指定
    if len(browsers) == 1:
        cmd.extend(["--browser", browsers[0]])
    
    # その他のオプション
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html:tests/reports/coverage"])
    
    # HTMLレポート生成
    cmd.extend([
        "--html=tests/reports/ui_test_report.html",
        "--self-contained-html"
    ])
    
    # JSON レポート生成
    cmd.extend([
        "--json-report",
        "--json-report-file=tests/reports/ui_test_report.json"
    ])
    
    # 並列実行（Chrome のみの場合）
    if len(browsers) == 1 and browsers[0] == "chrome":
        cmd.extend(["-n", "2"])  # 2並列
    
    print(f"   実行コマンド: {' '.join(cmd)}")
    
    # テスト実行
    start_time = time.time()
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"\n⏱️  実行時間: {execution_time:.2f}秒")
        
        # 結果の表示
        if result.returncode == 0:
            print("✅ 全テストが成功しました！")
        else:
            print(f"❌ テストが失敗しました (終了コード: {result.returncode})")
        
        # 出力の表示
        if verbose and result.stdout:
            print("\n📊 テスト出力:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  エラー出力:")
            print(result.stderr)
        
        return result.returncode == 0, execution_time
        
    except KeyboardInterrupt:
        print("\n⏹️  テストが中断されました")
        return False, 0
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return False, 0


def generate_summary_report(success, execution_time, test_type):
    """サマリーレポートの生成"""
    print("\n📋 テスト結果サマリーを生成しています...")
    
    # JSON レポートの読み込み
    json_report_path = Path("tests/reports/ui_test_report.json")
    summary_data = {
        "test_type": test_type,
        "success": success,
        "execution_time": execution_time,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    if json_report_path.exists():
        try:
            with open(json_report_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            summary_data.update({
                "total_tests": json_data.get("summary", {}).get("total", 0),
                "passed": json_data.get("summary", {}).get("passed", 0),
                "failed": json_data.get("summary", {}).get("failed", 0),
                "skipped": json_data.get("summary", {}).get("skipped", 0)
            })
        except Exception as e:
            print(f"   ⚠️  JSONレポート読み込みエラー: {e}")
    
    # サマリーの表示
    print(f"\n📊 テスト結果サマリー")
    print(f"   テストタイプ: {summary_data['test_type']}")
    print(f"   実行時間: {summary_data['execution_time']:.2f}秒")
    print(f"   総テスト数: {summary_data['total_tests']}")
    print(f"   成功: {summary_data['passed']}")
    print(f"   失敗: {summary_data['failed']}")
    print(f"   スキップ: {summary_data['skipped']}")
    
    if summary_data['total_tests'] > 0:
        success_rate = (summary_data['passed'] / summary_data['total_tests']) * 100
        print(f"   成功率: {success_rate:.1f}%")
    
    # サマリーファイルの保存
    summary_path = Path("tests/reports/test_summary.json")
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        print(f"   ✓ サマリー保存: {summary_path}")
    except Exception as e:
        print(f"   ⚠️  サマリー保存エラー: {e}")
    
    return summary_data


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="フェーズ4 UIテスト実行スクリプト")
    
    parser.add_argument(
        "--type", 
        choices=["all", "component", "scenario", "maintenance", "error_handling", "smoke", "critical"],
        default="all",
        help="実行するテストタイプ"
    )
    
    parser.add_argument(
        "--browsers",
        nargs="+",
        choices=["chrome", "firefox"],
        default=["chrome"],
        help="使用するブラウザ"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="ヘッドレスモードを無効化"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="カバレッジレポートを生成"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="詳細出力を抑制"
    )
    
    args = parser.parse_args()
    
    print("🎯 フェーズ4 UIテスト実行スクリプト")
    print("=" * 50)
    
    # 環境セットアップ
    setup_environment()
    
    # 依存関係確認
    if not check_dependencies():
        sys.exit(1)
    
    # テスト実行
    success, execution_time = run_tests(
        test_type=args.type,
        browsers=args.browsers,
        headless=not args.no_headless,
        verbose=not args.quiet,
        coverage=args.coverage
    )
    
    # サマリーレポート生成
    summary = generate_summary_report(success, execution_time, args.type)
    
    # レポートファイルの確認
    print("\n📁 生成されたレポート:")
    report_files = [
        "tests/reports/ui_test_report.html",
        "tests/reports/ui_test_report.json",
        "tests/reports/test_summary.json"
    ]
    
    if args.coverage:
        report_files.append("tests/reports/coverage/index.html")
    
    for report_file in report_files:
        if Path(report_file).exists():
            print(f"   ✓ {report_file}")
        else:
            print(f"   ❌ {report_file} (生成されませんでした)")
    
    # 終了
    print("\n" + "=" * 50)
    if success:
        print("🎉 UIテストが正常に完了しました！")
        sys.exit(0)
    else:
        print("💥 UIテストで問題が発生しました")
        sys.exit(1)


if __name__ == "__main__":
    main()