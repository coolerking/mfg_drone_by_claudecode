#!/usr/bin/env python3
"""
Tello EDU Dummy System Test Runner
包括的テストスイートの実行スクリプト
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """テスト実行管理クラス"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.test_categories = {
            'unit': {
                'description': '単体テスト（既存のPhase2・Phase3テスト）',
                'files': [
                    'tests/test_drone_simulator.py',
                    'tests/test_virtual_camera.py'
                ],
                'markers': 'unit'
            },
            'integration': {
                'description': '統合テスト（Phase2↔Phase3、設定統合、フルワークフロー）',
                'files': [
                    'tests/test_integration_phase2_phase3.py',
                    'tests/test_configuration_integration.py',
                    'tests/test_full_workflow_integration.py'
                ],
                'markers': 'integration'
            },
            'edge_cases': {
                'description': 'エッジケース・境界値テスト',
                'files': [
                    'tests/test_edge_cases.py'
                ],
                'markers': 'edge_case'
            },
            'error_handling': {
                'description': 'エラーハンドリング・例外処理テスト',
                'files': [
                    'tests/test_error_handling.py'
                ],
                'markers': 'error_handling'
            },
            'performance': {
                'description': 'パフォーマンス・長時間稼働テスト',
                'files': [
                    'tests/test_performance.py'
                ],
                'markers': 'performance'
            },
            'compatibility': {
                'description': '環境互換性・依存ライブラリテスト',
                'files': [
                    'tests/test_compatibility.py'
                ],
                'markers': 'compatibility'
            }
        }
    
    def run_category(self, category: str, verbose: bool = False, coverage: bool = True) -> bool:
        """指定カテゴリのテストを実行"""
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            return False
        
        category_info = self.test_categories[category]
        print(f"\n🧪 Running {category_info['description']}")
        print(f"Files: {', '.join(category_info['files'])}")
        
        cmd = ['python', '-m', 'pytest']
        
        # ファイル指定
        for test_file in category_info['files']:
            if (self.backend_dir / test_file).exists():
                cmd.append(test_file)
        
        # オプション追加
        if verbose:
            cmd.append('-v')
        
        if coverage:
            cmd.extend(['--cov=src', '--cov-report=term-missing'])
        
        # マーカー指定
        if category_info['markers']:
            cmd.extend(['-m', category_info['markers']])
        
        # 実行
        start_time = time.time()
        try:
            result = subprocess.run(cmd, cwd=self.backend_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {category} tests passed")
            else:
                print(f"❌ {category} tests failed")
                if verbose:
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
            
            elapsed = time.time() - start_time
            print(f"⏱️  Time: {elapsed:.2f}s")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running {category} tests: {e}")
            return False
    
    def run_all(self, exclude_slow: bool = True, verbose: bool = False) -> Dict[str, bool]:
        """全テストカテゴリを実行"""
        print("🚀 Running Tello EDU Dummy System Comprehensive Test Suite")
        print("=" * 60)
        
        results = {}
        total_start = time.time()
        
        for category in self.test_categories.keys():
            # パフォーマンステストは時間がかかるため、除外オプション
            if exclude_slow and category == 'performance':
                print(f"\n⏭️  Skipping {category} tests (slow tests excluded)")
                results[category] = None
                continue
            
            success = self.run_category(category, verbose=verbose)
            results[category] = success
        
        total_time = time.time() - total_start
        
        # 結果サマリー
        print("\n📊 Test Results Summary")
        print("=" * 40)
        
        passed = sum(1 for r in results.values() if r is True)
        failed = sum(1 for r in results.values() if r is False)
        skipped = sum(1 for r in results.values() if r is None)
        
        for category, result in results.items():
            if result is True:
                print(f"✅ {category:15} PASSED")
            elif result is False:
                print(f"❌ {category:15} FAILED")
            else:
                print(f"⏭️  {category:15} SKIPPED")
        
        print(f"\n📈 Total: {passed} passed, {failed} failed, {skipped} skipped")
        print(f"⏱️  Total time: {total_time:.2f}s")
        
        return results
    
    def run_quick(self) -> bool:
        """クイックテスト（単体テストのみ）"""
        print("⚡ Running Quick Tests (Unit Tests Only)")
        return self.run_category('unit', verbose=True)
    
    def run_coverage_report(self) -> bool:
        """カバレッジレポート生成"""
        print("📊 Generating Coverage Report")
        
        cmd = [
            'python', '-m', 'pytest',
            '--cov=src',
            '--cov-report=html:htmlcov',
            '--cov-report=xml',
            '--cov-report=term-missing',
            'tests/'
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.backend_dir)
            if result.returncode == 0:
                print("✅ Coverage report generated in htmlcov/")
                return True
            else:
                print("❌ Coverage report generation failed")
                return False
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
            return False
    
    def list_categories(self):
        """利用可能なテストカテゴリ一覧表示"""
        print("📋 Available Test Categories:")
        print("=" * 50)
        
        for category, info in self.test_categories.items():
            print(f"  {category:15} - {info['description']}")
            for file in info['files']:
                exists = "✅" if (self.backend_dir / file).exists() else "❌"
                print(f"    {exists} {file}")
            print()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Tello EDU Dummy System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                # Run all tests
  python run_tests.py --quick              # Run only unit tests
  python run_tests.py --category integration  # Run integration tests
  python run_tests.py --coverage           # Generate coverage report
  python run_tests.py --list               # List available categories
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', 
                      help='Run all test categories')
    group.add_argument('--quick', action='store_true',
                      help='Run quick tests (unit tests only)')
    group.add_argument('--category', choices=['unit', 'integration', 'edge_cases', 
                                             'error_handling', 'performance', 'compatibility'],
                      help='Run specific test category')
    group.add_argument('--coverage', action='store_true',
                      help='Generate coverage report')
    group.add_argument('--list', action='store_true',
                      help='List available test categories')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--include-slow', action='store_true',
                       help='Include slow tests (like performance tests)')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        runner.list_categories()
        return 0
    
    if args.coverage:
        success = runner.run_coverage_report()
        return 0 if success else 1
    
    if args.quick:
        success = runner.run_quick()
        return 0 if success else 1
    
    if args.category:
        success = runner.run_category(args.category, verbose=args.verbose)
        return 0 if success else 1
    
    if args.all:
        results = runner.run_all(exclude_slow=not args.include_slow, verbose=args.verbose)
        failed_count = sum(1 for r in results.values() if r is False)
        return 0 if failed_count == 0 else 1
    
    # デフォルト: ヘルプ表示
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())