#!/usr/bin/env python3
"""
ハイブリッドシステム監視 - Phase 3 実装
FastAPIとMCPサーバーの統合監視とステータス管理
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import psutil
import requests
from collections import deque

from .hybrid_process_manager import HybridProcessManager, ServerStatus, ProcessState
from .error_handler import error_handler, ErrorSeverity, ErrorCategory
from ..models.system_models import SystemStatusResponse, HealthResponse, HealthCheck
from ...config.settings import settings


class ServiceHealth(Enum):
    """サービスヘルス状態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class SystemMetrics:
    """システムメトリクス"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_connections: int = 0
    active_processes: int = 0
    uptime: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServerMetrics:
    """サーバーメトリクス"""
    server_id: str
    status: ProcessState
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: Optional[float] = None
    error_count: int = 0
    request_count: int = 0
    uptime: float = 0.0
    last_heartbeat: Optional[datetime] = None
    health: ServiceHealth = ServiceHealth.UNKNOWN


class HybridSystemMonitor:
    """ハイブリッドシステム監視クラス"""
    
    def __init__(self, process_manager: HybridProcessManager):
        """
        初期化
        
        Args:
            process_manager: ハイブリッドプロセスマネージャー
        """
        self.logger = logging.getLogger(__name__)
        self.process_manager = process_manager
        self.start_time = datetime.now()
        self.monitoring_active = False
        self.monitor_interval = settings.hybrid_monitor_interval
        
        # メトリクス保存（パフォーマンス最適化のためデックを使用）
        self.max_metrics_history = settings.hybrid_max_metrics_history
        self.system_metrics: deque = deque(maxlen=self.max_metrics_history)
        self.server_metrics: Dict[str, deque] = {}
        
        # アラート設定（設定ファイルから取得）
        self.alert_thresholds = {
            'cpu_usage': settings.hybrid_cpu_threshold,
            'memory_usage': settings.hybrid_memory_threshold,
            'disk_usage': settings.hybrid_disk_threshold,
            'response_time': settings.hybrid_response_time_threshold,
            'error_rate': settings.hybrid_error_rate_threshold,
        }
        
        # ヘルスチェック設定（設定ファイルから取得）
        self.health_check_endpoints = {
            'fastapi': f'http://localhost:{settings.hybrid_fastapi_port}{settings.hybrid_fastapi_health_endpoint}',
            'fastapi_enhanced': f'http://localhost:{settings.hybrid_fastapi_enhanced_port}{settings.hybrid_fastapi_enhanced_health_endpoint}',
        }
    
    async def start_monitoring(self):
        """監視を開始"""
        self.monitoring_active = True
        self.logger.info("ハイブリッドシステム監視を開始しました")
        
        # 監視タスクを開始
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        return monitoring_task
    
    async def stop_monitoring(self):
        """監視を停止"""
        self.monitoring_active = False
        self.logger.info("ハイブリッドシステム監視を停止しました")
    
    async def _monitoring_loop(self):
        """監視メインループ"""
        while self.monitoring_active:
            try:
                # システムメトリクスを収集
                await self._collect_system_metrics()
                
                # 各サーバーのメトリクスを収集
                await self._collect_server_metrics()
                
                # アラートをチェック
                await self._check_alerts()
                
                # 古いメトリクスを削除
                self._cleanup_old_metrics()
                
                # 監視間隔で待機
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                self.logger.error(f"監視ループ中にエラーが発生しました: {e}")
                await asyncio.sleep(5)  # エラー時は短時間待機
    
    async def _collect_system_metrics(self):
        """システムメトリクスを収集"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # ネットワーク接続数
            network_connections = len(psutil.net_connections())
            
            # アクティブプロセス数
            active_processes = len(psutil.pids())
            
            # 稼働時間
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # メトリクス作成
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_connections=network_connections,
                active_processes=active_processes,
                uptime=uptime
            )
            
            # 保存（デックの自動サイズ管理を利用）
            self.system_metrics.append(metrics)
            
            # デバッグログ
            self.logger.debug(f"システムメトリクス: CPU={cpu_usage:.1f}%, メモリ={memory_usage:.1f}%, ディスク={disk_usage:.1f}%")
            
        except Exception as e:
            self.logger.error(f"システムメトリクスの収集中にエラーが発生しました: {e}")
    
    async def _collect_server_metrics(self):
        """サーバーメトリクスを収集"""
        statuses = self.process_manager.get_all_statuses()
        
        for server_id, status in statuses.items():
            try:
                # サーバーメトリクスを収集
                metrics = await self._get_server_metrics(server_id, status)
                
                # 保存（デックの自動サイズ管理を利用）
                if server_id not in self.server_metrics:
                    self.server_metrics[server_id] = deque(maxlen=self.max_metrics_history)
                self.server_metrics[server_id].append(metrics)
                
            except Exception as e:
                self.logger.error(f"サーバー '{server_id}' のメトリクス収集中にエラーが発生しました: {e}")
    
    async def _get_server_metrics(self, server_id: str, status: ServerStatus) -> ServerMetrics:
        """個別サーバーのメトリクスを取得"""
        metrics = ServerMetrics(
            server_id=server_id,
            status=status.state
        )
        
        # プロセスが実行中の場合のみメトリクスを取得
        if status.state == ProcessState.RUNNING and status.process and status.pid:
            try:
                # プロセス情報を取得
                process = psutil.Process(status.pid)
                
                # CPU使用率
                metrics.cpu_usage = process.cpu_percent()
                
                # メモリ使用率
                memory_info = process.memory_info()
                metrics.memory_usage = memory_info.rss / 1024 / 1024  # MB
                
                # 稼働時間
                if status.start_time:
                    metrics.uptime = (datetime.now() - status.start_time).total_seconds()
                
                # 最終ハートビート
                metrics.last_heartbeat = status.last_heartbeat
                
                # ヘルスチェック（FastAPIサーバーのみ）
                if server_id in self.health_check_endpoints:
                    health_info = await self._check_server_health(server_id)
                    metrics.health = health_info.get('health', ServiceHealth.UNKNOWN)
                    metrics.response_time = health_info.get('response_time')
                else:
                    # MCPサーバーの場合は プロセス生存で判定（例外処理を追加）
                    try:
                        metrics.health = ServiceHealth.HEALTHY if process.is_running() else ServiceHealth.UNHEALTHY
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        metrics.health = ServiceHealth.UNHEALTHY
                    except Exception as e:
                        self.logger.warning(f"MCPサーバー '{server_id}' のプロセス状態確認中に例外が発生しました: {e}")
                        metrics.health = ServiceHealth.UNKNOWN
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                self.logger.warning(f"サーバー '{server_id}' のプロセス情報を取得できませんでした: {e}")
                metrics.health = ServiceHealth.UNHEALTHY
            except Exception as e:
                self.logger.error(f"サーバー '{server_id}' のメトリクス取得中にエラーが発生しました: {e}")
                metrics.health = ServiceHealth.UNKNOWN
        else:
            metrics.health = ServiceHealth.UNHEALTHY
        
        return metrics
    
    async def _check_server_health(self, server_id: str) -> Dict[str, Any]:
        """サーバーのヘルスチェック"""
        endpoint = self.health_check_endpoints.get(server_id)
        if not endpoint:
            return {'health': ServiceHealth.UNKNOWN}
        
        try:
            start_time = time.time()
            
            # タイムアウト設定でリクエスト
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(endpoint) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        health_data = await response.json()
                        overall_status = health_data.get('status', 'unknown')
                        
                        # ヘルス状態を変換
                        if overall_status == 'healthy':
                            health = ServiceHealth.HEALTHY
                        elif overall_status == 'degraded':
                            health = ServiceHealth.DEGRADED
                        else:
                            health = ServiceHealth.UNHEALTHY
                    else:
                        health = ServiceHealth.UNHEALTHY
                        
                    return {
                        'health': health,
                        'response_time': response_time,
                        'status_code': response.status
                    }
                    
        except asyncio.TimeoutError:
            self.logger.warning(f"サーバー '{server_id}' のヘルスチェックがタイムアウトしました")
            return {'health': ServiceHealth.UNHEALTHY, 'response_time': timeout.total if hasattr(timeout, 'total') else 10.0}
        except Exception as e:
            self.logger.error(f"サーバー '{server_id}' のヘルスチェック中にエラーが発生しました: {e}")
            return {'health': ServiceHealth.UNKNOWN}
    
    async def _check_alerts(self):
        """アラートをチェック"""
        if not self.system_metrics:
            return
        
        # 最新のシステムメトリクス
        latest_metrics = self.system_metrics[-1]
        
        # CPU使用率アラート
        if latest_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            self.logger.warning(f"高CPU使用率アラート: {latest_metrics.cpu_usage:.1f}%")
        
        # メモリ使用率アラート
        if latest_metrics.memory_usage > self.alert_thresholds['memory_usage']:
            self.logger.warning(f"高メモリ使用率アラート: {latest_metrics.memory_usage:.1f}%")
        
        # ディスク使用率アラート
        if latest_metrics.disk_usage > self.alert_thresholds['disk_usage']:
            self.logger.warning(f"高ディスク使用率アラート: {latest_metrics.disk_usage:.1f}%")
        
        # サーバー固有のアラート
        for server_id, metrics_list in self.server_metrics.items():
            if metrics_list:
                latest_server_metrics = metrics_list[-1]
                
                # サーバーヘルスアラート
                if latest_server_metrics.health == ServiceHealth.UNHEALTHY:
                    self.logger.error(f"サーバー '{server_id}' がUnhealthyです")
                elif latest_server_metrics.health == ServiceHealth.DEGRADED:
                    self.logger.warning(f"サーバー '{server_id}' がDegradedです")
                
                # 応答時間アラート
                if (latest_server_metrics.response_time and 
                    latest_server_metrics.response_time > self.alert_thresholds['response_time']):
                    self.logger.warning(f"サーバー '{server_id}' の応答時間が遅いです: {latest_server_metrics.response_time:.2f}秒")
    
    def _cleanup_old_metrics(self):
        """古いメトリクスを削除（デックを使用しているため自動的に管理される）"""
        # デックのmaxlenで自動的にサイズ管理されるため、明示的な清理は不要
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        # 基本情報
        statuses = self.process_manager.get_all_statuses()
        summary = self.process_manager.get_system_summary()
        
        # 最新のシステムメトリクス
        latest_system_metrics = self.system_metrics[-1] if self.system_metrics else None
        
        # 各サーバーの最新メトリクス
        server_info = {}
        for server_id, status in statuses.items():
            info = {
                'name': status.config.name,
                'type': status.config.server_type.value,
                'status': status.state.value,
                'features': status.config.features
            }
            
            # ネットワーク情報
            if status.config.server_type.value != 'mcp':
                info['host'] = status.config.host
                info['port'] = status.config.port
                info['url'] = f"http://{status.config.host}:{status.config.port}"
                info['docs_url'] = f"http://{status.config.host}:{status.config.port}/docs"
            else:
                info['protocol'] = "Model Context Protocol (stdio)"
            
            # プロセス情報
            if status.pid:
                info['pid'] = status.pid
            if status.start_time:
                info['start_time'] = status.start_time.isoformat()
            
            # 最新のメトリクス
            if server_id in self.server_metrics and self.server_metrics[server_id]:
                latest_metrics = self.server_metrics[server_id][-1]
                info['metrics'] = {
                    'cpu_usage': latest_metrics.cpu_usage,
                    'memory_usage': latest_metrics.memory_usage,
                    'uptime': latest_metrics.uptime,
                    'health': latest_metrics.health.value,
                    'response_time': latest_metrics.response_time
                }
            
            server_info[server_id] = info
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'total_servers': summary['total_servers'],
                'running_servers': summary['running_servers'],
                'stopped_servers': summary['stopped_servers'],
                'manager_uptime': summary['manager_uptime']
            },
            'system_metrics': {
                'cpu_usage': latest_system_metrics.cpu_usage if latest_system_metrics else 0,
                'memory_usage': latest_system_metrics.memory_usage if latest_system_metrics else 0,
                'disk_usage': latest_system_metrics.disk_usage if latest_system_metrics else 0,
                'network_connections': latest_system_metrics.network_connections if latest_system_metrics else 0,
                'active_processes': latest_system_metrics.active_processes if latest_system_metrics else 0,
                'uptime': latest_system_metrics.uptime if latest_system_metrics else 0
            },
            'servers': server_info,
            'monitoring': {
                'active': self.monitoring_active,
                'interval': self.monitor_interval,
                'metrics_history_size': len(self.system_metrics)
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """ヘルスステータスを取得"""
        checks = []
        
        # システムヘルスチェック
        if self.system_metrics:
            latest_metrics = self.system_metrics[-1]
            
            # CPU チェック
            cpu_status = "pass" if latest_metrics.cpu_usage < 80 else "warn" if latest_metrics.cpu_usage < 90 else "fail"
            checks.append({
                'name': 'System CPU',
                'status': cpu_status,
                'message': f'CPU使用率: {latest_metrics.cpu_usage:.1f}%'
            })
            
            # メモリ チェック
            memory_status = "pass" if latest_metrics.memory_usage < 80 else "warn" if latest_metrics.memory_usage < 90 else "fail"
            checks.append({
                'name': 'System Memory',
                'status': memory_status,
                'message': f'メモリ使用率: {latest_metrics.memory_usage:.1f}%'
            })
            
            # ディスク チェック
            disk_status = "pass" if latest_metrics.disk_usage < 80 else "warn" if latest_metrics.disk_usage < 90 else "fail"
            checks.append({
                'name': 'System Disk',
                'status': disk_status,
                'message': f'ディスク使用率: {latest_metrics.disk_usage:.1f}%'
            })
        
        # サーバーヘルスチェック
        statuses = self.process_manager.get_all_statuses()
        for server_id, status in statuses.items():
            if server_id in self.server_metrics and self.server_metrics[server_id]:
                latest_metrics = self.server_metrics[server_id][-1]
                
                if latest_metrics.health == ServiceHealth.HEALTHY:
                    server_status = "pass"
                    message = f"サーバー '{server_id}' は正常です"
                elif latest_metrics.health == ServiceHealth.DEGRADED:
                    server_status = "warn"
                    message = f"サーバー '{server_id}' は劣化しています"
                else:
                    server_status = "fail"
                    message = f"サーバー '{server_id}' は異常です"
                
                checks.append({
                    'name': f"Server {server_id}",
                    'status': server_status,
                    'message': message
                })
        
        # 全体の状態を決定
        if all(check['status'] == 'pass' for check in checks):
            overall_status = 'healthy'
        elif any(check['status'] == 'fail' for check in checks):
            overall_status = 'unhealthy'
        else:
            overall_status = 'degraded'
        
        return {
            'status': overall_status,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_history(self, server_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """メトリクス履歴を取得"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'limit': limit
        }
        
        if server_id:
            # 特定のサーバーのメトリクス
            if server_id in self.server_metrics:
                metrics = self.server_metrics[server_id][-limit:]
                result['server_metrics'] = [
                    {
                        'timestamp': m.last_heartbeat.isoformat() if m.last_heartbeat else datetime.now().isoformat(),
                        'cpu_usage': m.cpu_usage,
                        'memory_usage': m.memory_usage,
                        'response_time': m.response_time,
                        'health': m.health.value,
                        'uptime': m.uptime
                    }
                    for m in metrics
                ]
            else:
                result['server_metrics'] = []
        else:
            # システム全体のメトリクス
            system_metrics = self.system_metrics[-limit:]
            result['system_metrics'] = [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'disk_usage': m.disk_usage,
                    'network_connections': m.network_connections,
                    'active_processes': m.active_processes,
                    'uptime': m.uptime
                }
                for m in system_metrics
            ]
        
        return result