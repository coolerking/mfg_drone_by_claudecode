#!/usr/bin/env python3
"""
ハイブリッドプロセス管理 - FastAPIとMCPサーバーの同時実行管理
Phase 3: ハイブリッド運用のコアコンポーネント
"""

import asyncio
import logging
import multiprocessing
import os
import signal
import sys
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import json

# 外部ライブラリ
import uvicorn
from mcp.server.stdio import stdio_server

# 内部モジュール
from .progress_indicator import AsyncProgressIndicator, with_progress
from .error_handler import error_handler, ErrorSeverity, ErrorCategory
from .security_utils import security_validator
from ..models.system_models import SystemStatusResponse, HealthResponse, HealthCheck


class ServerType(Enum):
    """サーバータイプ"""
    FASTAPI = "fastapi"
    FASTAPI_ENHANCED = "fastapi_enhanced"
    MCP = "mcp"


class ProcessState(Enum):
    """プロセス状態"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServerConfig:
    """サーバー設定"""
    server_type: ServerType
    name: str
    host: str = "0.0.0.0"
    port: int = 8000
    app_module: str = "src.main:app"
    description: str = ""
    features: List[str] = field(default_factory=list)
    startup_timeout: float = 30.0
    shutdown_timeout: float = 15.0
    health_check_interval: float = 10.0
    auto_restart: bool = True
    max_restart_attempts: int = 3


@dataclass
class ServerStatus:
    """サーバー状態"""
    config: ServerConfig
    state: ProcessState = ProcessState.STOPPED
    process: Optional[multiprocessing.Process] = None
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    restart_count: int = 0
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class HybridProcessManager:
    """ハイブリッドプロセス管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス（オプション）
        """
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, ServerStatus] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.process_pool = ThreadPoolExecutor(max_workers=10)
        self.config_path = config_path
        self.shutdown_event = threading.Event()
        
        # デフォルト設定
        self._setup_default_configs()
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_default_configs(self):
        """デフォルト設定の設定"""
        self.default_configs = {
            "fastapi": ServerConfig(
                server_type=ServerType.FASTAPI,
                name="FastAPI Server",
                host="0.0.0.0",
                port=8000,
                app_module="src.main:app",
                description="Original FastAPI Server (Phase 1)",
                features=[
                    "📝 基本的な自然言語処理",
                    "🎯 コマンドルーティング",
                    "📦 シンプルなバッチ処理",
                    "🌐 完全なAPI実装"
                ]
            ),
            "fastapi_enhanced": ServerConfig(
                server_type=ServerType.FASTAPI_ENHANCED,
                name="Enhanced FastAPI Server",
                host="0.0.0.0", 
                port=8001,
                app_module="src.enhanced_main:app",
                description="Enhanced FastAPI Server (Phase 2)",
                features=[
                    "✨ 高度な自然言語処理",
                    "🧠 コンテキスト認識コマンド理解",
                    "🚀 インテリジェントバッチ処理",
                    "📊 依存関係分析・最適化",
                    "🔄 スマートエラー回復",
                    "📈 実行分析"
                ]
            ),
            "mcp": ServerConfig(
                server_type=ServerType.MCP,
                name="MCP Server",
                host="",  # MCPはstdio通信のためホスト不要
                port=0,   # MCPはポート不要
                app_module="src.mcp_main:main",
                description="MCP Server (Model Context Protocol)",
                features=[
                    "🤖 Model Context Protocol対応",
                    "🔧 MCPホスト統合",
                    "🎯 ドローン制御ツール",
                    "📋 リアルタイムリソース",
                    "🗣️ 自然言語コマンド処理",
                    "📊 システムステータス監視"
                ]
            )
        }
    
    def _signal_handler(self, signum: int, frame):
        """シグナルハンドラー"""
        self.logger.info(f"シグナル {signum} を受信しました。シャットダウンを開始します...")
        self.shutdown_event.set()
        asyncio.create_task(self.shutdown_all())
    
    def add_server(self, server_id: str, config: ServerConfig):
        """サーバーを追加"""
        self.servers[server_id] = ServerStatus(config=config)
        self.logger.info(f"サーバー '{server_id}' を追加しました: {config.name}")
    
    def remove_server(self, server_id: str):
        """サーバーを削除"""
        if server_id in self.servers:
            status = self.servers[server_id]
            if status.state == ProcessState.RUNNING:
                self.stop_server(server_id)
            del self.servers[server_id]
            self.logger.info(f"サーバー '{server_id}' を削除しました")
    
    async def start_server(self, server_id: str) -> bool:
        """サーバーを起動"""
        if server_id not in self.servers:
            self.logger.error(f"サーバー '{server_id}' が見つかりません")
            return False
        
        status = self.servers[server_id]
        if status.state == ProcessState.RUNNING:
            self.logger.warning(f"サーバー '{server_id}' は既に実行中です")
            return True
        
        try:
            status.state = ProcessState.STARTING
            self.logger.info(f"サーバー '{server_id}' を起動しています...")
            
            # プログレスインジケーターと共に起動
            async def start_operation(progress: AsyncProgressIndicator) -> bool:
                progress.update(1, "プロセスを開始中...")
                
                # サーバータイプに応じた起動処理
                if status.config.server_type == ServerType.MCP:
                    success = await self._start_mcp_server(status, progress)
                else:
                    success = await self._start_fastapi_server(status, progress)
                
                if success:
                    status.state = ProcessState.RUNNING
                    status.start_time = datetime.now()
                    status.last_heartbeat = datetime.now()
                    progress.update(1, "起動完了")
                    self.logger.info(f"サーバー '{server_id}' が正常に起動しました")
                else:
                    status.state = ProcessState.ERROR
                    progress.update(1, "起動失敗")
                    self.logger.error(f"サーバー '{server_id}' の起動に失敗しました")
                
                return success
            
            return await with_progress(start_operation, 2, f"サーバー '{server_id}' 起動")
            
        except Exception as e:
            status.state = ProcessState.ERROR
            status.error_message = str(e)
            self.logger.error(f"サーバー '{server_id}' の起動中にエラーが発生しました: {e}")
            return False
    
    async def _start_fastapi_server(self, status: ServerStatus, progress: AsyncProgressIndicator) -> bool:
        """FastAPIサーバーを起動"""
        try:
            config = status.config
            
            # uvicornサーバーをプロセスで起動
            def run_uvicorn():
                try:
                    uvicorn.run(
                        config.app_module,
                        host=config.host,
                        port=config.port,
                        reload=False,
                        log_level="info"
                    )
                except Exception as e:
                    self.logger.error(f"FastAPIサーバーの実行中にエラーが発生しました: {e}")
            
            # プロセスを開始
            process = multiprocessing.Process(target=run_uvicorn)
            process.start()
            
            status.process = process
            status.pid = process.pid
            
            # プロセスの起動確認
            await asyncio.sleep(2)
            if process.is_alive():
                progress.update(1, "プロセス起動確認完了")
                return True
            else:
                self.logger.error("FastAPIプロセスが起動に失敗しました")
                return False
                
        except Exception as e:
            self.logger.error(f"FastAPIサーバーの起動中にエラーが発生しました: {e}")
            return False
    
    async def _start_mcp_server(self, status: ServerStatus, progress: AsyncProgressIndicator) -> bool:
        """MCPサーバーを起動"""
        try:
            # MCPサーバーをプロセスで起動
            def run_mcp():
                try:
                    import sys
                    from pathlib import Path
                    
                    # パス設定
                    src_path = Path(__file__).parent.parent
                    sys.path.insert(0, str(src_path))
                    
                    # MCPサーバーの起動
                    from mcp_main import main as mcp_main
                    asyncio.run(mcp_main())
                except Exception as e:
                    self.logger.error(f"MCPサーバーの実行中にエラーが発生しました: {e}")
            
            # プロセスを開始
            process = multiprocessing.Process(target=run_mcp)
            process.start()
            
            status.process = process
            status.pid = process.pid
            
            # プロセスの起動確認
            await asyncio.sleep(2)
            if process.is_alive():
                progress.update(1, "MCPプロセス起動確認完了")
                return True
            else:
                self.logger.error("MCPプロセスが起動に失敗しました")
                return False
                
        except Exception as e:
            self.logger.error(f"MCPサーバーの起動中にエラーが発生しました: {e}")
            return False
    
    async def stop_server(self, server_id: str) -> bool:
        """サーバーを停止"""
        if server_id not in self.servers:
            self.logger.error(f"サーバー '{server_id}' が見つかりません")
            return False
        
        status = self.servers[server_id]
        if status.state != ProcessState.RUNNING:
            self.logger.warning(f"サーバー '{server_id}' は実行中ではありません")
            return True
        
        try:
            status.state = ProcessState.STOPPING
            self.logger.info(f"サーバー '{server_id}' を停止しています...")
            
            if status.process and status.process.is_alive():
                # プロセスを停止
                status.process.terminate()
                
                # 強制終了のタイムアウト
                timeout = status.config.shutdown_timeout
                status.process.join(timeout=timeout)
                
                if status.process.is_alive():
                    self.logger.warning(f"サーバー '{server_id}' が正常に停止しませんでした。強制終了します...")
                    status.process.kill()
                    status.process.join()
            
            status.state = ProcessState.STOPPED
            status.process = None
            status.pid = None
            status.start_time = None
            status.last_heartbeat = None
            
            self.logger.info(f"サーバー '{server_id}' が正常に停止しました")
            return True
            
        except Exception as e:
            status.state = ProcessState.ERROR
            status.error_message = str(e)
            self.logger.error(f"サーバー '{server_id}' の停止中にエラーが発生しました: {e}")
            return False
    
    async def start_all(self, server_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """全サーバーまたは指定されたサーバーを起動"""
        if server_ids is None:
            server_ids = list(self.servers.keys())
        
        results = {}
        
        # 並行して起動（ポート競合を避けるため順次実行）
        for server_id in server_ids:
            results[server_id] = await self.start_server(server_id)
            if not results[server_id]:
                self.logger.error(f"サーバー '{server_id}' の起動に失敗しました")
            
            # 少し待機してポート競合を回避
            await asyncio.sleep(1)
        
        return results
    
    async def stop_all(self) -> Dict[str, bool]:
        """全サーバーを停止"""
        results = {}
        
        # 並行して停止
        tasks = []
        for server_id in self.servers.keys():
            tasks.append(self.stop_server(server_id))
        
        stop_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for server_id, result in zip(self.servers.keys(), stop_results):
            if isinstance(result, Exception):
                results[server_id] = False
                self.logger.error(f"サーバー '{server_id}' の停止中にエラーが発生しました: {result}")
            else:
                results[server_id] = result
        
        return results
    
    async def restart_server(self, server_id: str) -> bool:
        """サーバーを再起動"""
        self.logger.info(f"サーバー '{server_id}' を再起動しています...")
        
        stop_success = await self.stop_server(server_id)
        if not stop_success:
            self.logger.error(f"サーバー '{server_id}' の停止に失敗しました")
            return False
        
        # 少し待機
        await asyncio.sleep(2)
        
        start_success = await self.start_server(server_id)
        if not start_success:
            self.logger.error(f"サーバー '{server_id}' の起動に失敗しました")
            return False
        
        self.logger.info(f"サーバー '{server_id}' が正常に再起動しました")
        return True
    
    def get_server_status(self, server_id: str) -> Optional[ServerStatus]:
        """サーバーステータスを取得"""
        return self.servers.get(server_id)
    
    def get_all_statuses(self) -> Dict[str, ServerStatus]:
        """全サーバーのステータスを取得"""
        return self.servers.copy()
    
    def get_running_servers(self) -> List[str]:
        """実行中のサーバー一覧を取得"""
        return [
            server_id for server_id, status in self.servers.items()
            if status.state == ProcessState.RUNNING
        ]
    
    def get_system_summary(self) -> Dict[str, Any]:
        """システムサマリーを取得"""
        total_servers = len(self.servers)
        running_servers = len(self.get_running_servers())
        
        return {
            "total_servers": total_servers,
            "running_servers": running_servers,
            "stopped_servers": total_servers - running_servers,
            "manager_uptime": time.time() - getattr(self, 'start_time', time.time()),
            "last_update": datetime.now().isoformat()
        }
    
    async def start_monitoring(self):
        """監視を開始"""
        self.running = True
        self.start_time = time.time()
        
        # 監視スレッドを開始
        self.monitor_thread = threading.Thread(target=self._monitor_processes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("プロセス監視を開始しました")
    
    def _monitor_processes(self):
        """プロセス監視（バックグラウンドスレッド）"""
        while self.running and not self.shutdown_event.is_set():
            try:
                for server_id, status in self.servers.items():
                    if status.state == ProcessState.RUNNING:
                        # プロセスの生存確認
                        if status.process and not status.process.is_alive():
                            self.logger.warning(f"サーバー '{server_id}' のプロセスが終了しました")
                            status.state = ProcessState.ERROR
                            
                            # 自動再起動
                            if status.config.auto_restart and status.restart_count < status.config.max_restart_attempts:
                                self.logger.info(f"サーバー '{server_id}' を自動再起動します...")
                                status.restart_count += 1
                                
                                # 再起動を非同期で実行
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                try:
                                    loop.run_until_complete(self.restart_server(server_id))
                                finally:
                                    loop.close()
                        
                        # ハートビートの更新
                        status.last_heartbeat = datetime.now()
                
                # 監視間隔
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"プロセス監視中にエラーが発生しました: {e}")
                time.sleep(5)
    
    async def shutdown_all(self):
        """全システムのシャットダウン"""
        self.logger.info("全システムのシャットダウンを開始しています...")
        
        # 監視を停止
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # 全サーバーを停止
        await self.stop_all()
        
        # スレッドプールを停止
        self.process_pool.shutdown(wait=True)
        
        self.logger.info("全システムのシャットダウンが完了しました")
    
    def setup_hybrid_mode(self) -> List[str]:
        """ハイブリッドモード用のサーバー設定"""
        hybrid_servers = []
        
        # FastAPIサーバー（ポート8000）
        fastapi_config = self.default_configs["fastapi"]
        fastapi_config.port = 8000
        self.add_server("fastapi", fastapi_config)
        hybrid_servers.append("fastapi")
        
        # MCPサーバー
        mcp_config = self.default_configs["mcp"]
        self.add_server("mcp", mcp_config)
        hybrid_servers.append("mcp")
        
        self.logger.info("ハイブリッドモードのサーバー設定を完了しました")
        return hybrid_servers
    
    def setup_enhanced_hybrid_mode(self) -> List[str]:
        """拡張ハイブリッドモード用のサーバー設定"""
        enhanced_hybrid_servers = []
        
        # Enhanced FastAPIサーバー（ポート8001）
        enhanced_config = self.default_configs["fastapi_enhanced"]
        enhanced_config.port = 8001
        self.add_server("fastapi_enhanced", enhanced_config)
        enhanced_hybrid_servers.append("fastapi_enhanced")
        
        # MCPサーバー
        mcp_config = self.default_configs["mcp"]
        self.add_server("mcp", mcp_config)
        enhanced_hybrid_servers.append("mcp")
        
        self.logger.info("拡張ハイブリッドモードのサーバー設定を完了しました")
        return enhanced_hybrid_servers
    
    def setup_full_hybrid_mode(self) -> List[str]:
        """フルハイブリッドモード用のサーバー設定（全サーバー）"""
        full_hybrid_servers = []
        
        # FastAPIサーバー（ポート8000）
        fastapi_config = self.default_configs["fastapi"]
        fastapi_config.port = 8000
        self.add_server("fastapi", fastapi_config)
        full_hybrid_servers.append("fastapi")
        
        # Enhanced FastAPIサーバー（ポート8001）
        enhanced_config = self.default_configs["fastapi_enhanced"]
        enhanced_config.port = 8001
        self.add_server("fastapi_enhanced", enhanced_config)
        full_hybrid_servers.append("fastapi_enhanced")
        
        # MCPサーバー
        mcp_config = self.default_configs["mcp"]
        self.add_server("mcp", mcp_config)
        full_hybrid_servers.append("mcp")
        
        self.logger.info("フルハイブリッドモードのサーバー設定を完了しました")
        return full_hybrid_servers