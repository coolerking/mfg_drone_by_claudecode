#!/usr/bin/env python3
"""
システム品質保証チェックツール
MCP Drone Control Systemの非機能要件（パフォーマンス、セキュリティ、可用性等）を検証

検証項目:
1. パフォーマンス測定
2. セキュリティ脆弱性チェック
3. 可用性・信頼性テスト
4. リソース使用量監視
5. スケーラビリティテスト
6. エラー回復テスト
7. データ整合性チェック
8. 監視・ログ機能テスト
"""

import asyncio
import time
import json
import statistics
import subprocess
import sys
import os
import psutil
import aiofiles
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import websockets
import ssl
import socket
from urllib.parse import urlparse


@dataclass
class QualityMetric:
    """品質メトリクス"""
    name: str
    value: float
    unit: str
    threshold: float
    passed: bool
    category: str
    description: str = ""


@dataclass
class QualityIssue:
    """品質問題"""
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    category: str
    title: str
    description: str
    recommendation: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """システム品質レポート"""
    overall_score: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    reliability_score: float = 0.0
    scalability_score: float = 0.0
    metrics: List[QualityMetric] = field(default_factory=list)
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    test_duration: float = 0.0


class SystemQualityChecker:
    """システム品質保証チェックツール"""
    
    def __init__(self, mcp_mode: str = "auto"):
        """
        初期化
        
        Args:
            mcp_mode: MCPサーバーモード 
                     - "python": Python MCPサーバー（HTTP API、ポート8001）
                     - "nodejs": Node.js MCPサーバー（バックエンドAPI経由、ポート8000）
                     - "auto": 環境変数 MCP_MODE から自動判定
        """
        # 環境変数からモード設定を取得
        if mcp_mode == "auto":
            self.mcp_mode = os.environ.get("MCP_MODE", "nodejs").lower()
        else:
            self.mcp_mode = mcp_mode.lower()
        
        # 共通設定
        self.backend_port = int(os.environ.get("BACKEND_PORT", "8000"))
        self.backend_api_url = f"http://localhost:{self.backend_port}"
        self.frontend_port = int(os.environ.get("FRONTEND_PORT", "3000"))
        self.frontend_url = f"http://localhost:{self.frontend_port}"
        
        # モード別URL設定
        if self.mcp_mode == "python":
            # Python MCPサーバー: 直接HTTP API
            self.mcp_server_port = int(os.environ.get("MCP_PYTHON_PORT", "8001"))
            self.mcp_server_url = f"http://localhost:{self.mcp_server_port}"
            self.test_endpoints_mode = "python_mcp"
            print(f"🐍 Python MCPサーバーモード: {self.mcp_server_url}")
        else:
            # Node.js MCPサーバー: バックエンドAPI経由でテスト
            self.mcp_server_url = self.backend_api_url  # Node.js MCPはバックエンド経由
            self.test_endpoints_mode = "nodejs_backend"
            print(f"🟢 Node.js MCPサーバーモード（バックエンド経由）: {self.backend_api_url}")
        
        self.report = QualityReport()
        
        # 品質基準しきい値
        self.quality_thresholds = {
            # パフォーマンス基準
            "max_response_time": 2000,  # ms
            "min_throughput": 100,  # requests/sec
            "max_memory_usage": 512,  # MB
            "max_cpu_usage": 80,  # %
            
            # セキュリティ基準
            "min_ssl_strength": 2048,  # bit
            "max_open_ports": 10,
            "max_security_headers": 5,
            
            # 可用性基準
            "min_uptime": 99.9,  # %
            "max_error_rate": 1.0,  # %
            "min_success_rate": 99.0,  # %
            
            # スケーラビリティ基準
            "max_concurrent_users": 100,
            "max_load_increase": 200,  # %
        }
    
    async def run_quality_assessment(self) -> QualityReport:
        """品質保証の総合評価"""
        print("🎯 システム品質保証チェック開始")
        print("=" * 70)
        
        start_time = time.time()
        
        # 各カテゴリの品質チェック
        await self._check_performance_quality()
        await self._check_security_quality()
        await self._check_reliability_quality()
        await self._check_scalability_quality()
        await self._check_monitoring_quality()
        await self._check_data_integrity()
        
        # 総合スコア計算
        self._calculate_overall_scores()
        
        self.report.test_duration = time.time() - start_time
        
        print(f"\n✅ 品質保証チェック完了 - 実行時間: {self.report.test_duration:.2f}秒")
        return self.report
    
    async def _check_performance_quality(self):
        """パフォーマンス品質チェック"""
        print("\n⚡ パフォーマンス品質チェック...")
        
        # API応答時間測定
        await self._measure_api_response_time()
        
        # スループット測定
        await self._measure_throughput()
        
        # リソース使用量測定
        await self._measure_resource_usage()
        
        # 並行処理性能測定
        await self._measure_concurrent_performance()
    
    async def _measure_api_response_time(self):
        """API応答時間測定"""
        print(f"  📊 API応答時間測定 ({self.mcp_mode}モード)...")
        
        if self.test_endpoints_mode == "python_mcp":
            # Python MCPサーバー: 直接MCPエンドポイント + バックエンドAPI
            endpoints = [
                f"{self.mcp_server_url}/mcp/system/health",
                f"{self.mcp_server_url}/mcp/drones",
                f"{self.backend_api_url}/api/drones",
                f"{self.backend_api_url}/api/system/status",
            ]
        else:
            # Node.js MCPサーバー: バックエンドAPIのみ（MCPサーバーは stdio 通信）
            endpoints = [
                f"{self.mcp_server_url}/api/system/health",
                f"{self.mcp_server_url}/api/system/status", 
                f"{self.mcp_server_url}/api/drones",
                f"{self.mcp_server_url}/api/drones/scan",
            ]
        
        all_response_times = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                response_times = []
                
                # 各エンドポイントを10回測定
                for _ in range(10):
                    start_time = time.time()
                    try:
                        async with session.get(endpoint, timeout=5) as response:
                            response_time = (time.time() - start_time) * 1000  # ms
                            response_times.append(response_time)
                            all_response_times.append(response_time)
                    except Exception as e:
                        print(f"    ⚠️ {endpoint}: アクセスエラー ({str(e)})")
                        continue
                
                if response_times:
                    avg_time = statistics.mean(response_times)
                    max_time = max(response_times)
                    min_time = min(response_times)
                    
                    print(f"    • {endpoint}: avg={avg_time:.1f}ms, max={max_time:.1f}ms, min={min_time:.1f}ms")
                    
                    # メトリクス追加
                    self.report.metrics.append(QualityMetric(
                        name=f"Response Time ({endpoint})",
                        value=avg_time,
                        unit="ms",
                        threshold=self.quality_thresholds["max_response_time"],
                        passed=avg_time <= self.quality_thresholds["max_response_time"],
                        category="Performance"
                    ))
        
        if all_response_times:
            overall_avg = statistics.mean(all_response_times)
            print(f"  📈 全体平均応答時間: {overall_avg:.1f}ms")
            
            if overall_avg > self.quality_thresholds["max_response_time"]:
                self.report.issues.append(QualityIssue(
                    severity="HIGH",
                    category="Performance",
                    title="API応答時間が基準を超過",
                    description=f"平均応答時間 {overall_avg:.1f}ms が基準値 {self.quality_thresholds['max_response_time']}ms を超えています",
                    recommendation="データベースクエリの最適化、キャッシュの実装、サーバーリソースの増強を検討してください"
                ))
    
    async def _measure_throughput(self):
        """スループット測定"""
        print("  🚀 スループット測定...")
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
        
        duration = 10  # 10秒間測定
        request_count = 0
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            request_count += 1
                except:
                    pass
        
        throughput = request_count / duration
        print(f"  📊 スループット: {throughput:.1f} requests/sec")
        
        self.report.metrics.append(QualityMetric(
            name="API Throughput",
            value=throughput,
            unit="req/sec",
            threshold=self.quality_thresholds["min_throughput"],
            passed=throughput >= self.quality_thresholds["min_throughput"],
            category="Performance"
        ))
        
        if throughput < self.quality_thresholds["min_throughput"]:
            self.report.issues.append(QualityIssue(
                severity="MEDIUM",
                category="Performance",
                title="スループットが基準を下回る",
                description=f"スループット {throughput:.1f} req/sec が基準値 {self.quality_thresholds['min_throughput']} req/sec を下回っています",
                recommendation="アプリケーションの並列処理能力向上、ロードバランサーの導入を検討してください"
            ))
    
    async def _measure_resource_usage(self):
        """リソース使用量測定"""
        print("  💾 リソース使用量測定...")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"  📊 CPU使用率: {cpu_percent:.1f}%")
        
        self.report.metrics.append(QualityMetric(
            name="CPU Usage",
            value=cpu_percent,
            unit="%",
            threshold=self.quality_thresholds["max_cpu_usage"],
            passed=cpu_percent <= self.quality_thresholds["max_cpu_usage"],
            category="Performance"
        ))
        
        # メモリ使用量
        memory = psutil.virtual_memory()
        memory_usage_mb = (memory.total - memory.available) / 1024 / 1024
        print(f"  📊 メモリ使用量: {memory_usage_mb:.1f}MB ({memory.percent:.1f}%)")
        
        self.report.metrics.append(QualityMetric(
            name="Memory Usage",
            value=memory_usage_mb,
            unit="MB",
            threshold=self.quality_thresholds["max_memory_usage"],
            passed=memory_usage_mb <= self.quality_thresholds["max_memory_usage"],
            category="Performance"
        ))
        
        # ディスク使用量
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        print(f"  📊 ディスク使用量: {disk_usage_percent:.1f}%")
        
        if cpu_percent > self.quality_thresholds["max_cpu_usage"]:
            self.report.issues.append(QualityIssue(
                severity="HIGH",
                category="Performance",
                title="CPU使用率が高い",
                description=f"CPU使用率 {cpu_percent:.1f}% が基準値 {self.quality_thresholds['max_cpu_usage']}% を超えています",
                recommendation="プロセスの最適化、サーバーリソースの増強を検討してください"
            ))
    
    async def _measure_concurrent_performance(self):
        """並行処理性能測定"""
        print("  🔄 並行処理性能測定...")
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
            
        concurrent_users = [10, 25, 50, 100]
        
        for users in concurrent_users:
            start_time = time.time()
            success_count = 0
            error_count = 0
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for _ in range(users):
                    task = self._make_concurrent_request(session, endpoint)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        error_count += 1
                    else:
                        success_count += 1
            
            duration = time.time() - start_time
            success_rate = (success_count / users) * 100
            
            print(f"    • {users}同時ユーザー: 成功率={success_rate:.1f}%, 応答時間={duration:.2f}s")
            
            if users <= 50 and success_rate < 95:
                self.report.issues.append(QualityIssue(
                    severity="MEDIUM",
                    category="Performance",
                    title=f"並行処理で成功率低下 ({users}ユーザー)",
                    description=f"{users}同時ユーザーで成功率が {success_rate:.1f}% に低下",
                    recommendation="アプリケーションの並行処理能力向上、コネクションプールの調整を検討してください"
                ))
    
    async def _make_concurrent_request(self, session: aiohttp.ClientSession, endpoint: str):
        """並行リクエスト実行"""
        try:
            async with session.get(endpoint, timeout=5) as response:
                return response.status == 200
        except:
            return False
    
    async def _check_security_quality(self):
        """セキュリティ品質チェック"""
        print("\n🔒 セキュリティ品質チェック...")
        
        # SSL/TLS設定チェック
        await self._check_ssl_configuration()
        
        # 認証・認可チェック
        await self._check_authentication_security()
        
        # セキュリティヘッダーチェック
        await self._check_security_headers()
        
        # ポートスキャンチェック
        await self._check_open_ports()
        
        # 入力検証チェック
        await self._check_input_validation_security()
    
    async def _check_ssl_configuration(self):
        """SSL/TLS設定チェック"""
        print("  🔐 SSL/TLS設定チェック...")
        
        # HTTPSエンドポイントの確認（本番環境想定）
        https_endpoints = [
            "https://localhost:8001",
            "https://localhost:8000",
        ]
        
        for endpoint in https_endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, ssl=False) as response:
                        print(f"    ✅ {endpoint}: HTTPS接続可能")
            except aiohttp.ClientSSLError:
                print(f"    ℹ️ {endpoint}: SSL証明書エラー（開発環境では正常）")
            except:
                print(f"    ⚠️ {endpoint}: HTTPS接続不可")
        
        # セキュリティ推奨事項
        self.report.recommendations.append("本番環境では有効なSSL証明書を使用し、HTTPS通信を強制してください")
    
    async def _check_authentication_security(self):
        """認証・認可セキュリティチェック"""
        print("  🔑 認証・認可セキュリティチェック...")
        
        # 認証なしアクセステスト
        if self.test_endpoints_mode == "python_mcp":
            protected_endpoints = [
                f"{self.mcp_server_url}/mcp/command",
                f"{self.mcp_server_url}/mcp/drones",
            ]
        else:
            protected_endpoints = [
                f"{self.mcp_server_url}/api/drones/scan",
                f"{self.mcp_server_url}/api/vision/detection",
            ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in protected_endpoints:
                try:
                    async with session.post(endpoint) as response:
                        if response.status in [401, 403]:
                            print(f"    ✅ {endpoint}: 認証保護有効")
                        else:
                            print(f"    ❌ {endpoint}: 認証保護なし (HTTP {response.status})")
                            self.report.issues.append(QualityIssue(
                                severity="CRITICAL",
                                category="Security",
                                title="認証保護の不備",
                                description=f"エンドポイント {endpoint} が認証なしでアクセス可能",
                                recommendation="すべての機密エンドポイントに適切な認証を実装してください"
                            ))
                except Exception as e:
                    print(f"    ⚠️ {endpoint}: テストエラー ({str(e)})")
    
    async def _check_security_headers(self):
        """セキュリティヘッダーチェック"""
        print("  📋 セキュリティヘッダーチェック...")
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    missing_headers = []
                    present_headers = []
                    
                    for header in security_headers:
                        if header in response.headers:
                            present_headers.append(header)
                        else:
                            missing_headers.append(header)
                    
                    print(f"    ✅ 実装済みセキュリティヘッダー: {len(present_headers)}個")
                    print(f"    ⚠️ 未実装セキュリティヘッダー: {len(missing_headers)}個")
                    
                    if missing_headers:
                        self.report.issues.append(QualityIssue(
                            severity="MEDIUM",
                            category="Security",
                            title="セキュリティヘッダーの不足",
                            description=f"推奨セキュリティヘッダーが不足: {', '.join(missing_headers)}",
                            recommendation="セキュリティヘッダーを追加して、XSS、クリックジャッキング等の攻撃を防止してください"
                        ))
        except Exception as e:
            print(f"    ❌ セキュリティヘッダーチェックエラー: {str(e)}")
    
    async def _check_open_ports(self):
        """開放ポートチェック"""
        print("  🚪 開放ポートチェック...")
        
        common_ports = [22, 80, 443, 3000, 8000, 8001, 5432, 3306, 6379]
        open_ports = []
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        print(f"    📊 開放ポート数: {len(open_ports)}個 {open_ports}")
        
        self.report.metrics.append(QualityMetric(
            name="Open Ports",
            value=len(open_ports),
            unit="ports",
            threshold=self.quality_thresholds["max_open_ports"],
            passed=len(open_ports) <= self.quality_thresholds["max_open_ports"],
            category="Security"
        ))
        
        # 不要なポートの警告
        unnecessary_ports = [port for port in open_ports if port not in [3000, 8000, 8001]]
        if unnecessary_ports:
            self.report.issues.append(QualityIssue(
                severity="LOW",
                category="Security",
                title="不要なポートが開放されている",
                description=f"アプリケーション以外のポートが開放: {unnecessary_ports}",
                recommendation="セキュリティのため、不要なポートを閉じることを検討してください"
            ))
    
    async def _check_input_validation_security(self):
        """入力検証セキュリティチェック"""
        print("  🛡️ 入力検証セキュリティチェック...")
        
        # SQLインジェクション試行
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('XSS')</script>",
            "../../../etc/passwd",
            "{{7*7}}"  # Template injection
        ]
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/command"
        else:
            # Node.js版の場合はバックエンドAPIの入力検証をテスト
            endpoint = f"{self.mcp_server_url}/api/drones/scan"
        
        async with aiohttp.ClientSession() as session:
            for malicious_input in malicious_inputs:
                try:
                    payload = {"command": malicious_input}
                    async with session.post(endpoint, json=payload) as response:
                        if response.status == 400:
                            print(f"    ✅ 入力検証有効: 悪意ある入力を適切に拒否")
                        else:
                            print(f"    ⚠️ 入力検証に問題の可能性: HTTP {response.status}")
                except Exception:
                    print(f"    ℹ️ 入力検証テスト: 接続エラー（認証が必要な可能性）")
                    break
    
    async def _check_reliability_quality(self):
        """信頼性品質チェック"""
        print("\n🛡️ 信頼性品質チェック...")
        
        # 可用性テスト
        await self._check_availability()
        
        # エラー回復テスト
        await self._check_error_recovery()
        
        # ログ機能テスト
        await self._check_logging_functionality()
    
    async def _check_availability(self):
        """可用性テスト"""
        print("  📈 可用性テスト...")
        
        if self.test_endpoints_mode == "python_mcp":
            endpoints = [
                f"{self.mcp_server_url}/mcp/system/health",
                f"{self.backend_api_url}/api/system/status",
            ]
        else:
            endpoints = [
                f"{self.mcp_server_url}/api/system/health",
                f"{self.mcp_server_url}/api/system/status",
            ]
        
        total_requests = 0
        successful_requests = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                for _ in range(20):  # 各エンドポイント20回テスト
                    total_requests += 1
                    try:
                        async with session.get(endpoint, timeout=5) as response:
                            if response.status == 200:
                                successful_requests += 1
                    except:
                        pass
        
        availability = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        print(f"  📊 可用性: {availability:.1f}%")
        
        self.report.metrics.append(QualityMetric(
            name="System Availability",
            value=availability,
            unit="%",
            threshold=self.quality_thresholds["min_uptime"],
            passed=availability >= self.quality_thresholds["min_uptime"],
            category="Reliability"
        ))
        
        if availability < self.quality_thresholds["min_uptime"]:
            self.report.issues.append(QualityIssue(
                severity="HIGH",
                category="Reliability",
                title="システム可用性が低い",
                description=f"可用性 {availability:.1f}% が基準値 {self.quality_thresholds['min_uptime']}% を下回っています",
                recommendation="システムの安定性向上、冗長化の実装を検討してください"
            ))
    
    async def _check_error_recovery(self):
        """エラー回復テスト"""
        print("  🔄 エラー回復テスト...")
        
        # 無効なエンドポイントへのアクセス
        invalid_endpoints = [
            f"{self.mcp_server_url}/invalid",
            f"{self.mcp_server_url}/mcp/nonexistent",
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in invalid_endpoints:
                try:
                    async with session.get(endpoint) as response:
                        if response.status == 404:
                            print(f"    ✅ 適切なエラーレスポンス: HTTP 404")
                        else:
                            print(f"    ⚠️ 予期しないレスポンス: HTTP {response.status}")
                except Exception as e:
                    print(f"    ❌ エラー処理に問題: {str(e)}")
    
    async def _check_logging_functionality(self):
        """ログ機能テスト"""
        print("  📝 ログ機能テスト...")
        
        # ログファイルの存在確認
        log_directories = [
            Path("./logs"),
            Path("./mcp-server/logs"),
            Path("./backend/logs"),
        ]
        
        log_files_found = 0
        for log_dir in log_directories:
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                log_files_found += len(log_files)
                if log_files:
                    print(f"    ✅ ログファイル発見: {log_dir} ({len(log_files)}個)")
        
        if log_files_found == 0:
            print(f"    ⚠️ ログファイルが見つかりません")
            self.report.issues.append(QualityIssue(
                severity="LOW",
                category="Reliability",
                title="ログファイルが見つからない",
                description="システムログファイルが適切に生成されていない可能性があります",
                recommendation="ログ設定を確認し、適切なログ出力を設定してください"
            ))
        else:
            print(f"    📊 ログファイル総数: {log_files_found}個")
    
    async def _check_scalability_quality(self):
        """スケーラビリティ品質チェック"""
        print("\n📈 スケーラビリティ品質チェック...")
        
        # 負荷増大テスト
        await self._check_load_scalability()
        
        # メモリ使用量増大テスト
        await self._check_memory_scalability()
    
    async def _check_load_scalability(self):
        """負荷スケーラビリティテスト"""
        print("  ⚡ 負荷スケーラビリティテスト...")
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
            
        base_load = 10
        max_load = 100
        
        async with aiohttp.ClientSession() as session:
            # ベースライン測定
            start_time = time.time()
            tasks = [self._make_concurrent_request(session, endpoint) for _ in range(base_load)]
            results = await asyncio.gather(*tasks)
            baseline_duration = time.time() - start_time
            baseline_success = sum(results)
            
            print(f"    📊 ベースライン({base_load}): 成功={baseline_success}, 時間={baseline_duration:.2f}s")
            
            # 高負荷測定
            start_time = time.time()
            tasks = [self._make_concurrent_request(session, endpoint) for _ in range(max_load)]
            results = await asyncio.gather(*tasks)
            high_load_duration = time.time() - start_time
            high_load_success = sum(results)
            
            print(f"    📊 高負荷({max_load}): 成功={high_load_success}, 時間={high_load_duration:.2f}s")
            
            # スケーラビリティ分析
            load_increase = (max_load / base_load) * 100
            time_increase = (high_load_duration / baseline_duration) * 100
            
            if time_increase > load_increase * 2:  # 時間増加が負荷増加の2倍を超える場合
                self.report.issues.append(QualityIssue(
                    severity="MEDIUM",
                    category="Scalability",
                    title="負荷増大時の性能劣化",
                    description=f"負荷が{load_increase:.0f}%増加時、処理時間が{time_increase:.0f}%増加",
                    recommendation="アプリケーションのスケーラビリティ改善、負荷分散の実装を検討してください"
                ))
            else:
                print(f"    ✅ スケーラビリティ良好: 時間増加率{time_increase:.0f}%")
    
    async def _check_memory_scalability(self):
        """メモリスケーラビリティテスト"""
        print("  💾 メモリスケーラビリティテスト...")
        
        # メモリ使用量の変化を監視
        initial_memory = psutil.virtual_memory().used
        
        # 簡易的な負荷をかける
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
        
        async with aiohttp.ClientSession() as session:
            tasks = [self._make_concurrent_request(session, endpoint) for _ in range(200)]
            await asyncio.gather(*tasks)
        
        final_memory = psutil.virtual_memory().used
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        print(f"    📊 メモリ使用量増加: {memory_increase:.1f}MB")
        
        if memory_increase > 100:  # 100MB以上の増加
            self.report.issues.append(QualityIssue(
                severity="LOW",
                category="Scalability",
                title="メモリ使用量の大幅増加",
                description=f"負荷テスト中にメモリ使用量が{memory_increase:.1f}MB増加",
                recommendation="メモリリークの確認、ガベージコレクションの最適化を検討してください"
            ))
    
    async def _check_monitoring_quality(self):
        """監視品質チェック"""
        print("\n📊 監視品質チェック...")
        
        # メトリクス収集機能の確認
        await self._check_metrics_collection()
        
        # アラート機能の確認
        await self._check_alerting_system()
    
    async def _check_metrics_collection(self):
        """メトリクス収集機能チェック"""
        print("  📈 メトリクス収集機能チェック...")
        
        # Prometheusメトリクスエンドポイントの確認
        metrics_endpoints = [
            f"{self.mcp_server_url}/metrics",
            f"{self.backend_api_url}/metrics",
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in metrics_endpoints:
                try:
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            content = await response.text()
                            if "# HELP" in content:  # Prometheusメトリクス形式
                                print(f"    ✅ {endpoint}: Prometheusメトリクス利用可能")
                            else:
                                print(f"    ℹ️ {endpoint}: カスタムメトリクス利用可能")
                        else:
                            print(f"    ⚠️ {endpoint}: メトリクス利用不可 (HTTP {response.status})")
                except Exception as e:
                    print(f"    ⚠️ {endpoint}: アクセスエラー ({str(e)})")
    
    async def _check_alerting_system(self):
        """アラートシステムチェック"""
        print("  🚨 アラートシステムチェック...")
        
        # アラート設定ファイルの存在確認
        alert_config_paths = [
            Path("./monitoring/alerts.yml"),
            Path("./mcp-server/monitoring/alerts.yml"),
        ]
        
        alert_configs_found = 0
        for config_path in alert_config_paths:
            if config_path.exists():
                alert_configs_found += 1
                print(f"    ✅ アラート設定発見: {config_path}")
        
        if alert_configs_found == 0:
            print(f"    ⚠️ アラート設定ファイルが見つかりません")
            self.report.recommendations.append("Prometheusアラートルールを設定し、システム監視を強化してください")
        else:
            print(f"    📊 アラート設定ファイル: {alert_configs_found}個")
    
    async def _check_data_integrity(self):
        """データ整合性チェック"""
        print("\n🔍 データ整合性チェック...")
        
        # 設定ファイルの整合性確認
        await self._check_configuration_integrity()
        
        # APIレスポンスの整合性確認
        await self._check_api_response_integrity()
    
    async def _check_configuration_integrity(self):
        """設定ファイル整合性チェック"""
        print("  ⚙️ 設定ファイル整合性チェック...")
        
        # 重要な設定ファイルの存在確認
        config_files = [
            Path("./mcp-server/requirements.txt"),
            Path("./backend/requirements.txt"),
            Path("./shared/api-specs/mcp-api.yaml"),
            Path("./docker-compose.prod.yml"),
        ]
        
        missing_configs = []
        for config_file in config_files:
            if not config_file.exists():
                missing_configs.append(str(config_file))
            else:
                print(f"    ✅ {config_file}: 存在確認")
        
        if missing_configs:
            self.report.issues.append(QualityIssue(
                severity="MEDIUM",
                category="Data Integrity",
                title="重要な設定ファイルが不足",
                description=f"不足ファイル: {', '.join(missing_configs)}",
                recommendation="不足している設定ファイルを作成し、適切な設定を行ってください"
            ))
    
    async def _check_api_response_integrity(self):
        """APIレスポンス整合性チェック"""
        print("  🔍 APIレスポンス整合性チェック...")
        
        if self.test_endpoints_mode == "python_mcp":
            endpoint = f"{self.mcp_server_url}/mcp/system/health"
        else:
            endpoint = f"{self.mcp_server_url}/api/system/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 必須フィールドの確認
                        required_fields = ["status", "checks", "timestamp"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            print(f"    ✅ APIレスポンス整合性: 正常")
                        else:
                            print(f"    ❌ APIレスポンス整合性: 不足フィールド {missing_fields}")
                            self.report.issues.append(QualityIssue(
                                severity="MEDIUM",
                                category="Data Integrity",
                                title="APIレスポンス形式の不整合",
                                description=f"必須フィールドが不足: {missing_fields}",
                                recommendation="APIレスポンス形式を仕様に合わせて修正してください"
                            ))
                    else:
                        print(f"    ⚠️ APIレスポンス取得失敗: HTTP {response.status}")
        except Exception as e:
            print(f"    ❌ APIレスポンス整合性チェックエラー: {str(e)}")
    
    def _calculate_overall_scores(self):
        """総合スコア計算"""
        # カテゴリ別スコア計算
        category_scores = {}
        
        for category in ["Performance", "Security", "Reliability", "Scalability"]:
            category_metrics = [m for m in self.report.metrics if m.category == category]
            if category_metrics:
                passed_metrics = sum(1 for m in category_metrics if m.passed)
                category_score = (passed_metrics / len(category_metrics)) * 100
                category_scores[category] = category_score
            else:
                category_scores[category] = 75  # デフォルトスコア
        
        self.report.performance_score = category_scores.get("Performance", 75)
        self.report.security_score = category_scores.get("Security", 75)
        self.report.reliability_score = category_scores.get("Reliability", 75)
        self.report.scalability_score = category_scores.get("Scalability", 75)
        
        # 重大な問題による減点
        critical_issues = [issue for issue in self.report.issues if issue.severity == "CRITICAL"]
        high_issues = [issue for issue in self.report.issues if issue.severity == "HIGH"]
        
        penalty = len(critical_issues) * 20 + len(high_issues) * 10
        
        # 総合スコア計算
        base_score = statistics.mean([
            self.report.performance_score,
            self.report.security_score,
            self.report.reliability_score,
            self.report.scalability_score
        ])
        
        self.report.overall_score = max(0, base_score - penalty)
    
    def print_quality_report(self):
        """品質レポート表示"""
        print("\n" + "=" * 80)
        print("🎯 システム品質保証レポート")
        print("=" * 80)
        
        print(f"\n📊 総合品質スコア: {self.report.overall_score:.1f}/100")
        print(f"  ⚡ パフォーマンス: {self.report.performance_score:.1f}/100")
        print(f"  🔒 セキュリティ: {self.report.security_score:.1f}/100")
        print(f"  🛡️ 信頼性: {self.report.reliability_score:.1f}/100")
        print(f"  📈 スケーラビリティ: {self.report.scalability_score:.1f}/100")
        print(f"  ⏱️ テスト実行時間: {self.report.test_duration:.2f}秒")
        
        # 品質メトリクス
        if self.report.metrics:
            print(f"\n📋 品質メトリクス:")
            for metric in self.report.metrics:
                status = "✅" if metric.passed else "❌"
                print(f"  {status} {metric.name}: {metric.value:.1f}{metric.unit} (基準: {metric.threshold}{metric.unit})")
        
        # 品質問題
        if self.report.issues:
            print(f"\n🚨 品質問題 ({len(self.report.issues)}件):")
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            sorted_issues = sorted(self.report.issues, key=lambda x: severity_order.get(x.severity, 4))
            
            for issue in sorted_issues:
                severity_icon = {"CRITICAL": "🚨", "HIGH": "❌", "MEDIUM": "⚠️", "LOW": "ℹ️"}
                icon = severity_icon.get(issue.severity, "•")
                print(f"  {icon} [{issue.severity}] {issue.title}")
                print(f"    {issue.description}")
                print(f"    💡 {issue.recommendation}")
        
        # 推奨事項
        if self.report.recommendations:
            print(f"\n💡 システム改善推奨事項:")
            for rec in self.report.recommendations:
                print(f"  💡 {rec}")
        
        # 最終評価
        print(f"\n🏆 最終品質評価:")
        if self.report.overall_score >= 90:
            print("  ✅ 優秀 - システムは高品質で本番環境に適しています")
        elif self.report.overall_score >= 80:
            print("  ✅ 良好 - システムは良い品質レベルです")
        elif self.report.overall_score >= 70:
            print("  ⚠️ 改善必要 - いくつかの品質問題があります")
        else:
            print("  ❌ 要改善 - 重大な品質問題があります")
        
        print("\n" + "=" * 80)


def print_usage():
    """使用方法を表示"""
    print("""
🎯 システム品質保証チェックツール
MCP Drone Control System - System Quality Assurance Checker

使用方法:
  python system_quality_checker.py [mode]

モード:
  python    Python MCPサーバー（HTTP API、ポート8001）をテスト
  nodejs    Node.js MCPサーバー（バックエンドAPI経由、ポート8000）をテスト  
  auto      環境変数 MCP_MODE から自動判定（デフォルト: nodejs）

環境変数:
  MCP_MODE           MCPサーバーモード (python/nodejs)
  MCP_PYTHON_PORT    Python MCPサーバーポート (デフォルト: 8001)
  BACKEND_PORT       バックエンドAPIポート (デフォルト: 8000)
  FRONTEND_PORT      フロントエンドポート (デフォルト: 3000)

使用例:
  # Node.js MCPサーバーをテスト（デフォルト）
  python system_quality_checker.py
  python system_quality_checker.py nodejs
  
  # Python MCPサーバーをテスト
  python system_quality_checker.py python
  
  # 環境変数で設定
  export MCP_MODE=nodejs && python system_quality_checker.py
  export BACKEND_PORT=8080 && python system_quality_checker.py nodejs
    """)


async def main():
    """メイン実行関数"""
    # ヘルプ表示チェック
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        return
    
    print("🎯 システム品質保証チェックツール")
    print("MCP Drone Control System - System Quality Assurance Checker")
    print("=" * 80)
    
    # コマンドライン引数からモード取得
    mcp_mode = "auto"
    if len(sys.argv) > 1:
        mcp_mode = sys.argv[1]
    
    # 品質チェッカー初期化
    checker = SystemQualityChecker(mcp_mode=mcp_mode)
    
    # 品質評価実行
    report = await checker.run_quality_assessment()
    
    # レポート表示
    checker.print_quality_report()
    
    # JSONレポート出力
    json_report = {
        "quality_report": {
            "overall_score": report.overall_score,
            "performance_score": report.performance_score,
            "security_score": report.security_score,
            "reliability_score": report.reliability_score,
            "scalability_score": report.scalability_score,
            "test_duration": report.test_duration,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "threshold": m.threshold,
                    "passed": m.passed,
                    "category": m.category
                }
                for m in report.metrics
            ],
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "title": issue.title,
                    "description": issue.description,
                    "recommendation": issue.recommendation
                }
                for issue in report.issues
            ],
            "recommendations": report.recommendations
        },
        "timestamp": datetime.now().isoformat(),
        "system": "MCP Drone Control System"
    }
    
    with open("system_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 詳細レポートが保存されました: system_quality_report.json")
    
    # 終了コード決定
    if report.overall_score >= 90:
        return 0  # 優秀
    elif report.overall_score >= 70:
        return 1  # 改善必要
    else:
        return 2  # 要改善


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)