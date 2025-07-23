#!/usr/bin/env python3
"""
Phase 9: Performance Benchmark Tests
MCPサーバーのPython版とNode.js版のパフォーマンス詳細比較

ベンチマーク項目:
1. 基本的な応答時間測定
2. スループット測定
3. メモリ使用量比較
4. CPU使用率比較
5. 同時接続負荷テスト
6. 長時間稼働安定性テスト
"""

import asyncio
import json
import os
import time
import psutil
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import matplotlib.pyplot as plt
import numpy as np


class BenchmarkCategory(Enum):
    """ベンチマークカテゴリ"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONCURRENCY = "concurrency"
    STABILITY = "stability"


@dataclass
class BenchmarkResult:
    """ベンチマーク結果"""
    category: BenchmarkCategory
    test_name: str
    python_metrics: Dict[str, Any]
    nodejs_metrics: Dict[str, Any]
    winner: str  # "python", "nodejs", "tie"
    performance_ratio: float  # nodejs/python比率
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """パフォーマンスレポート"""
    python_wins: int = 0
    nodejs_wins: int = 0
    ties: int = 0
    total_benchmarks: int = 0
    results: List[BenchmarkResult] = field(default_factory=list)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class MCPPerformanceBenchmark:
    """MCPパフォーマンスベンチマーク"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.report = PerformanceReport()
        
        # サーバーURL設定（環境変数対応）
        self.python_server_url = f"http://localhost:{os.environ.get('MCP_PYTHON_PORT', '8001')}"  # レガシーPython版  
        self.nodejs_server_url = f"http://localhost:{os.environ.get('MCP_NODEJS_PORT', '3001')}"  # メインNode.js版
        
        # ベンチマーク設定
        self.benchmark_config = {
            "response_time_samples": 100,
            "throughput_duration": 30,  # 秒
            "concurrency_levels": [1, 5, 10, 20, 50],
            "stability_duration": 300,  # 5分
            "memory_sampling_interval": 5  # 秒
        }
    
    async def run_performance_benchmarks(self) -> PerformanceReport:
        """パフォーマンスベンチマーク実行"""
        print("🚀 Phase 9: Performance Benchmark - Python vs Node.js")
        print("=" * 80)
        
        start_time = time.time()
        
        # 各カテゴリのベンチマーク実行
        await self._benchmark_response_time()
        await self._benchmark_throughput()
        await self._benchmark_memory_usage()
        await self._benchmark_cpu_usage()
        await self._benchmark_concurrency()
        await self._benchmark_stability()
        
        # 結果分析とレポート生成
        self._analyze_results()
        self._generate_recommendations()
        
        execution_time = time.time() - start_time
        print(f"\n✅ 全ベンチマーク完了 - 実行時間: {execution_time:.2f}秒")
        
        return self.report
    
    async def _benchmark_response_time(self):
        """応答時間ベンチマーク"""
        print("\n⏱️ 応答時間ベンチマーク...")
        
        # ヘルスチェックエンドポイントの応答時間測定
        python_times = await self._measure_response_times(
            f"{self.python_server_url}/mcp/system/health",
            self.benchmark_config["response_time_samples"]
        )
        
        nodejs_times = await self._measure_response_times(
            f"{self.nodejs_server_url}/mcp/system/health",
            self.benchmark_config["response_time_samples"]
        )
        
        # 統計計算
        python_stats = self._calculate_time_stats(python_times)
        nodejs_stats = self._calculate_time_stats(nodejs_times)
        
        # 勝者決定
        winner = "nodejs" if nodejs_stats["mean"] < python_stats["mean"] else "python"
        if abs(nodejs_stats["mean"] - python_stats["mean"]) < 0.01:  # 10ms以内は同等
            winner = "tie"
        
        performance_ratio = nodejs_stats["mean"] / python_stats["mean"] if python_stats["mean"] > 0 else 1.0
        
        result = BenchmarkResult(
            category=BenchmarkCategory.RESPONSE_TIME,
            test_name="Health Check Response Time",
            python_metrics=python_stats,
            nodejs_metrics=nodejs_stats,
            winner=winner,
            performance_ratio=performance_ratio,
            details={"python_times": python_times, "nodejs_times": nodejs_times}
        )
        
        self._add_result(result)
        print(f"  Python平均応答時間: {python_stats['mean']:.3f}s (±{python_stats['std']:.3f})")
        print(f"  Node.js平均応答時間: {nodejs_stats['mean']:.3f}s (±{nodejs_stats['std']:.3f})")
        print(f"  勝者: {winner}")
    
    async def _benchmark_throughput(self):
        """スループットベンチマーク"""
        print("\n📊 スループットベンチマーク...")
        
        duration = self.benchmark_config["throughput_duration"]
        
        # Python版スループット測定
        python_rps = await self._measure_throughput(
            f"{self.python_server_url}/mcp/system/health", duration
        )
        
        # Node.js版スループット測定
        nodejs_rps = await self._measure_throughput(
            f"{self.nodejs_server_url}/mcp/system/health", duration
        )
        
        python_metrics = {"requests_per_second": python_rps, "total_requests": python_rps * duration}
        nodejs_metrics = {"requests_per_second": nodejs_rps, "total_requests": nodejs_rps * duration}
        
        winner = "nodejs" if nodejs_rps > python_rps else "python"
        if abs(nodejs_rps - python_rps) < (max(nodejs_rps, python_rps) * 0.05):  # 5%以内は同等
            winner = "tie"
        
        performance_ratio = nodejs_rps / python_rps if python_rps > 0 else 1.0
        
        result = BenchmarkResult(
            category=BenchmarkCategory.THROUGHPUT,
            test_name="Request Throughput",
            python_metrics=python_metrics,
            nodejs_metrics=nodejs_metrics,
            winner=winner,
            performance_ratio=performance_ratio
        )
        
        self._add_result(result)
        print(f"  Python RPS: {python_rps:.2f}")
        print(f"  Node.js RPS: {nodejs_rps:.2f}")
        print(f"  勝者: {winner}")
    
    async def _benchmark_memory_usage(self):
        """メモリ使用量ベンチマーク"""
        print("\n💾 メモリ使用量ベンチマーク...")
        
        # 現在は基本的な実装のみ（実際のプロセス監視が必要）
        python_metrics = {"note": "Memory monitoring requires process identification"}
        nodejs_metrics = {"note": "Memory monitoring requires process identification"}
        
        result = BenchmarkResult(
            category=BenchmarkCategory.MEMORY_USAGE,
            test_name="Memory Usage Comparison",
            python_metrics=python_metrics,
            nodejs_metrics=nodejs_metrics,
            winner="tie",
            performance_ratio=1.0,
            details={"implementation_note": "Requires process monitoring setup"}
        )
        
        self._add_result(result)
        print("  メモリ使用量測定: プロセス監視の実装が必要")
    
    async def _benchmark_cpu_usage(self):
        """CPU使用率ベンチマーク"""
        print("\n🖥️ CPU使用率ベンチマーク...")
        
        # 現在は基本的な実装のみ
        python_metrics = {"note": "CPU monitoring requires process identification"}
        nodejs_metrics = {"note": "CPU monitoring requires process identification"}
        
        result = BenchmarkResult(
            category=BenchmarkCategory.CPU_USAGE,
            test_name="CPU Usage Comparison",
            python_metrics=python_metrics,
            nodejs_metrics=nodejs_metrics,
            winner="tie",
            performance_ratio=1.0
        )
        
        self._add_result(result)
        print("  CPU使用率測定: プロセス監視の実装が必要")
    
    async def _benchmark_concurrency(self):
        """同時接続負荷ベンチマーク"""
        print("\n🔀 同時接続負荷ベンチマーク...")
        
        concurrency_levels = self.benchmark_config["concurrency_levels"]
        python_results = {}
        nodejs_results = {}
        
        for concurrency in concurrency_levels:
            print(f"  同時接続数 {concurrency} テスト中...")
            
            # Python版テスト
            python_success_rate = await self._test_concurrency_level(
                f"{self.python_server_url}/mcp/system/health", concurrency
            )
            
            # Node.js版テスト
            nodejs_success_rate = await self._test_concurrency_level(
                f"{self.nodejs_server_url}/mcp/system/health", concurrency
            )
            
            python_results[f"concurrency_{concurrency}"] = python_success_rate
            nodejs_results[f"concurrency_{concurrency}"] = nodejs_success_rate
            
            print(f"    Python成功率: {python_success_rate:.1%}")
            print(f"    Node.js成功率: {nodejs_success_rate:.1%}")
        
        # 全体的な成功率計算
        python_avg = statistics.mean(python_results.values())
        nodejs_avg = statistics.mean(nodejs_results.values())
        
        winner = "nodejs" if nodejs_avg > python_avg else "python"
        if abs(nodejs_avg - python_avg) < 0.05:  # 5%以内は同等
            winner = "tie"
        
        performance_ratio = nodejs_avg / python_avg if python_avg > 0 else 1.0
        
        result = BenchmarkResult(
            category=BenchmarkCategory.CONCURRENCY,
            test_name="Concurrent Request Handling",
            python_metrics={"average_success_rate": python_avg, "results_by_level": python_results},
            nodejs_metrics={"average_success_rate": nodejs_avg, "results_by_level": nodejs_results},
            winner=winner,
            performance_ratio=performance_ratio
        )
        
        self._add_result(result)
        print(f"  Python平均成功率: {python_avg:.1%}")
        print(f"  Node.js平均成功率: {nodejs_avg:.1%}")
        print(f"  勝者: {winner}")
    
    async def _benchmark_stability(self):
        """長時間稼働安定性ベンチマーク"""
        print("\n🏃 長時間稼働安定性ベンチマーク...")
        
        duration = self.benchmark_config["stability_duration"]
        print(f"  {duration}秒間の安定性テスト実行中...")
        
        # 簡易版: 定期的なヘルスチェック
        python_stability = await self._test_stability(
            f"{self.python_server_url}/mcp/system/health", duration
        )
        
        nodejs_stability = await self._test_stability(
            f"{self.nodejs_server_url}/mcp/system/health", duration
        )
        
        winner = "nodejs" if nodejs_stability["success_rate"] > python_stability["success_rate"] else "python"
        if abs(nodejs_stability["success_rate"] - python_stability["success_rate"]) < 0.02:  # 2%以内は同等
            winner = "tie"
        
        performance_ratio = nodejs_stability["success_rate"] / python_stability["success_rate"] if python_stability["success_rate"] > 0 else 1.0
        
        result = BenchmarkResult(
            category=BenchmarkCategory.STABILITY,
            test_name="Long-term Stability",
            python_metrics=python_stability,
            nodejs_metrics=nodejs_stability,
            winner=winner,
            performance_ratio=performance_ratio
        )
        
        self._add_result(result)
        print(f"  Python安定性: {python_stability['success_rate']:.1%}")
        print(f"  Node.js安定性: {nodejs_stability['success_rate']:.1%}")
        print(f"  勝者: {winner}")
    
    async def _measure_response_times(self, url: str, samples: int) -> List[float]:
        """応答時間測定"""
        times = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(samples):
                try:
                    start_time = time.time()
                    async with session.get(url) as response:
                        end_time = time.time()
                        if response.status == 200:
                            times.append(end_time - start_time)
                        else:
                            # エラー応答も時間として記録（ペナルティとして高い値を設定）
                            times.append((end_time - start_time) * 2)
                except:
                    # 接続エラーの場合はペナルティ時間を追加
                    times.append(5.0)
                
                # サーバーに負荷をかけすぎないよう小さな待機
                if i < samples - 1:
                    await asyncio.sleep(0.01)
        
        return times
    
    def _calculate_time_stats(self, times: List[float]) -> Dict[str, float]:
        """時間統計計算"""
        if not times:
            return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "p95": 0, "p99": 0}
        
        times_sorted = sorted(times)
        n = len(times)
        
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "std": statistics.stdev(times) if n > 1 else 0,
            "min": min(times),
            "max": max(times),
            "p95": times_sorted[int(n * 0.95)] if n > 0 else 0,
            "p99": times_sorted[int(n * 0.99)] if n > 0 else 0
        }
    
    async def _measure_throughput(self, url: str, duration: int) -> float:
        """スループット測定"""
        end_time = time.time() + duration
        request_count = 0
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    async with session.get(url) as response:
                        request_count += 1
                except:
                    pass
                
                # 小さな待機を入れてサーバー過負荷を防ぐ
                await asyncio.sleep(0.001)
        
        return request_count / duration
    
    async def _test_concurrency_level(self, url: str, concurrency: int) -> float:
        """同時接続レベルテスト"""
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            for _ in range(concurrency):
                task = session.get(url)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = 0
            for response in responses:
                if not isinstance(response, Exception):
                    if hasattr(response, 'status') and response.status == 200:
                        successful_requests += 1
            
            return successful_requests / concurrency
    
    async def _test_stability(self, url: str, duration: int) -> Dict[str, Any]:
        """安定性テスト"""
        end_time = time.time() + duration
        total_requests = 0
        successful_requests = 0
        error_count = 0
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    async with session.get(url) as response:
                        total_requests += 1
                        if response.status == 200:
                            successful_requests += 1
                        else:
                            error_count += 1
                except Exception as e:
                    total_requests += 1
                    error_count += 1
                
                # 定期的なテスト間隔
                await asyncio.sleep(1)
        
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_count": error_count,
            "success_rate": success_rate,
            "test_duration": duration
        }
    
    def _add_result(self, result: BenchmarkResult):
        """結果追加とカウント更新"""
        self.report.results.append(result)
        self.report.total_benchmarks += 1
        
        if result.winner == "python":
            self.report.python_wins += 1
        elif result.winner == "nodejs":
            self.report.nodejs_wins += 1
        else:
            self.report.ties += 1
    
    def _analyze_results(self):
        """結果分析"""
        if not self.report.results:
            return
        
        # カテゴリ別分析
        category_stats = {}
        for category in BenchmarkCategory:
            category_results = [r for r in self.report.results if r.category == category]
            if category_results:
                python_wins = sum(1 for r in category_results if r.winner == "python")
                nodejs_wins = sum(1 for r in category_results if r.winner == "nodejs")
                ties = sum(1 for r in category_results if r.winner == "tie")
                
                category_stats[category.value] = {
                    "total": len(category_results),
                    "python_wins": python_wins,
                    "nodejs_wins": nodejs_wins,
                    "ties": ties
                }
        
        # 全体的なパフォーマンス比較
        performance_ratios = [r.performance_ratio for r in self.report.results 
                             if r.performance_ratio > 0 and r.performance_ratio != 1.0]
        
        summary_stats = {
            "category_breakdown": category_stats,
            "overall_performance_ratio": statistics.mean(performance_ratios) if performance_ratios else 1.0,
            "nodejs_win_rate": self.report.nodejs_wins / self.report.total_benchmarks if self.report.total_benchmarks > 0 else 0,
            "python_win_rate": self.report.python_wins / self.report.total_benchmarks if self.report.total_benchmarks > 0 else 0
        }
        
        self.report.summary_stats = summary_stats
    
    def _generate_recommendations(self):
        """推奨事項生成"""
        nodejs_win_rate = self.report.summary_stats.get("nodejs_win_rate", 0)
        python_win_rate = self.report.summary_stats.get("python_win_rate", 0)
        
        if nodejs_win_rate > python_win_rate + 0.2:  # 20%以上の差
            self.report.recommendations.append(
                "🚀 Node.js版が総合的に優秀なパフォーマンスを示しています。移行を推奨します。"
            )
        elif python_win_rate > nodejs_win_rate + 0.2:
            self.report.recommendations.append(
                "🐍 Python版が総合的に優秀なパフォーマンスを示しています。現行維持を推奨します。"
            )
        else:
            self.report.recommendations.append(
                "⚖️ 両バージョンのパフォーマンスは同等レベルです。他の要因を考慮して判断してください。"
            )
        
        # 応答時間に関する推奨事項
        response_time_results = [r for r in self.report.results 
                               if r.category == BenchmarkCategory.RESPONSE_TIME]
        if response_time_results:
            avg_ratio = statistics.mean(r.performance_ratio for r in response_time_results)
            if avg_ratio < 0.8:  # Node.js版が20%以上高速
                self.report.recommendations.append(
                    "⚡ Node.js版の応答時間が優秀です。ユーザー体験向上のため移行検討を推奨します。"
                )
        
        # 安定性に関する推奨事項
        stability_results = [r for r in self.report.results 
                           if r.category == BenchmarkCategory.STABILITY]
        if stability_results:
            for result in stability_results:
                python_stability = result.python_metrics.get("success_rate", 0)
                nodejs_stability = result.nodejs_metrics.get("success_rate", 0)
                
                if min(python_stability, nodejs_stability) < 0.95:  # 95%未満は問題
                    self.report.recommendations.append(
                        "⚠️ 長時間稼働での安定性に問題があります。詳細調査が必要です。"
                    )
    
    def print_performance_report(self):
        """パフォーマンスレポート表示"""
        print("\n" + "=" * 80)
        print("⚡ Phase 9: Performance Benchmark Report - Python vs Node.js")
        print("=" * 80)
        
        print(f"\n📊 ベンチマーク実行統計:")
        print(f"  総ベンチマーク数: {self.report.total_benchmarks}")
        print(f"  Python優位: {self.report.python_wins}")
        print(f"  Node.js優位: {self.report.nodejs_wins}")
        print(f"  引き分け: {self.report.ties}")
        
        if self.report.total_benchmarks > 0:
            nodejs_win_rate = (self.report.nodejs_wins / self.report.total_benchmarks) * 100
            python_win_rate = (self.report.python_wins / self.report.total_benchmarks) * 100
            tie_rate = (self.report.ties / self.report.total_benchmarks) * 100
            
            print(f"  Node.js勝率: {nodejs_win_rate:.1f}%")
            print(f"  Python勝率: {python_win_rate:.1f}%")
            print(f"  引き分け率: {tie_rate:.1f}%")
        
        # カテゴリ別詳細結果
        print(f"\n📋 カテゴリ別詳細結果:")
        for category in BenchmarkCategory:
            category_results = [r for r in self.report.results if r.category == category]
            if category_results:
                print(f"\n  {category.value.upper()}:")
                for result in category_results:
                    winner_icon = "🥇" if result.winner != "tie" else "🤝"
                    print(f"    {winner_icon} {result.test_name}: {result.winner} (比率: {result.performance_ratio:.2f})")
        
        # 全体的なパフォーマンス分析
        if self.report.summary_stats:
            overall_ratio = self.report.summary_stats.get("overall_performance_ratio", 1.0)
            print(f"\n📈 全体的なパフォーマンス比較:")
            print(f"  平均パフォーマンス比率 (Node.js/Python): {overall_ratio:.2f}")
            
            if overall_ratio < 0.9:
                print("  → Node.js版が総合的に高速です")
            elif overall_ratio > 1.1:
                print("  → Python版が総合的に高速です")
            else:
                print("  → 両バージョンのパフォーマンスは同等です")
        
        # 推奨事項
        if self.report.recommendations:
            print(f"\n💡 パフォーマンス観点での推奨事項:")
            for recommendation in self.report.recommendations:
                print(f"  {recommendation}")
        
        # 最終評価
        print(f"\n🏆 パフォーマンス総合評価:")
        if self.report.nodejs_wins > self.report.python_wins:
            print("  🚀 Node.js版がパフォーマンス面で優位です")
        elif self.report.python_wins > self.report.nodejs_wins:
            print("  🐍 Python版がパフォーマンス面で優位です")
        else:
            print("  ⚖️ 両バージョンのパフォーマンスは拮抗しています")
        
        print("\n" + "=" * 80)
    
    def save_performance_charts(self):
        """パフォーマンスチャート保存"""
        try:
            # 応答時間比較チャート
            response_time_results = [r for r in self.report.results 
                                   if r.category == BenchmarkCategory.RESPONSE_TIME]
            
            if response_time_results:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                test_names = [r.test_name for r in response_time_results]
                python_times = [r.python_metrics.get("mean", 0) for r in response_time_results]
                nodejs_times = [r.nodejs_metrics.get("mean", 0) for r in response_time_results]
                
                x = np.arange(len(test_names))
                width = 0.35
                
                ax.bar(x - width/2, python_times, width, label='Python', alpha=0.8)
                ax.bar(x + width/2, nodejs_times, width, label='Node.js', alpha=0.8)
                
                ax.set_xlabel('Test')
                ax.set_ylabel('Response Time (seconds)')
                ax.set_title('Response Time Comparison: Python vs Node.js')
                ax.set_xticks(x)
                ax.set_xticklabels(test_names, rotation=45)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig("phase9_response_time_comparison.png")
                plt.close()
                
                print("📊 応答時間比較チャートを保存しました: phase9_response_time_comparison.png")
        
        except ImportError:
            print("⚠️ matplotlib が利用できないため、チャートは生成されませんでした")
        except Exception as e:
            print(f"⚠️ チャート生成エラー: {str(e)}")


async def main():
    """メイン実行関数"""
    print("⚡ Phase 9: Performance Benchmark Tests")
    print("Python版 vs Node.js版 詳細パフォーマンス比較")
    print("=" * 80)
    
    # ベンチマークスイート初期化
    benchmark_suite = MCPPerformanceBenchmark()
    
    # パフォーマンスベンチマーク実行
    report = await benchmark_suite.run_performance_benchmarks()
    
    # レポート表示
    benchmark_suite.print_performance_report()
    
    # チャート生成
    benchmark_suite.save_performance_charts()
    
    # JSONレポート出力
    json_report = {
        "performance_benchmark_report": {
            "python_wins": report.python_wins,
            "nodejs_wins": report.nodejs_wins,
            "ties": report.ties,
            "total_benchmarks": report.total_benchmarks,
            "summary_stats": report.summary_stats,
            "recommendations": report.recommendations,
            "benchmark_results": [
                {
                    "category": result.category.value,
                    "test_name": result.test_name,
                    "winner": result.winner,
                    "performance_ratio": result.performance_ratio,
                    "python_metrics": result.python_metrics,
                    "nodejs_metrics": result.nodejs_metrics
                }
                for result in report.results
            ]
        },
        "timestamp": datetime.now().isoformat(),
        "phase": "9",
        "test_type": "performance_benchmark"
    }
    
    # レポートファイル出力
    with open("phase9_performance_benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 パフォーマンスベンチマークレポートが保存されました: phase9_performance_benchmark_report.json")
    
    # 終了コード決定
    if report.nodejs_wins > report.python_wins:
        return 0  # Node.js版優位
    elif report.python_wins > report.nodejs_wins:
        return 1  # Python版優位  
    else:
        return 2  # 拮抗


if __name__ == "__main__":
    asyncio.run(main())