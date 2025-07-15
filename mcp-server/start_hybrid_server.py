#!/usr/bin/env python3
"""
ハイブリッドサーバー起動スクリプト - Phase 3 実装
FastAPIサーバーとMCPサーバーの同時実行をサポート
"""

import os
import sys
import argparse
import asyncio
import signal
from pathlib import Path
from typing import Optional, List
import logging

# パス設定
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from config.settings import settings
from config.logging import setup_logging, get_logger
from core.hybrid_process_manager import HybridProcessManager, ServerConfig, ServerType


class HybridServerManager:
    """ハイブリッドサーバー管理クラス"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.process_manager = HybridProcessManager()
        self.running = False
        self.shutdown_requested = False
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame):
        """シグナルハンドラー"""
        self.logger.info(f"終了シグナル ({signum}) を受信しました")
        self.shutdown_requested = True
        asyncio.create_task(self.shutdown())
    
    async def start_hybrid_mode(self, mode: str = "basic") -> bool:
        """
        ハイブリッドモードでサーバーを起動
        
        Args:
            mode: "basic" | "enhanced" | "full"
        """
        self.logger.info(f"ハイブリッドモード '{mode}' でサーバーを起動しています...")
        
        try:
            # 監視を開始
            await self.process_manager.start_monitoring()
            
            # モードに応じたサーバー設定
            if mode == "basic":
                server_ids = self.process_manager.setup_hybrid_mode()
                mode_description = "基本ハイブリッドモード (FastAPI + MCP)"
            elif mode == "enhanced":
                server_ids = self.process_manager.setup_enhanced_hybrid_mode()
                mode_description = "拡張ハイブリッドモード (Enhanced FastAPI + MCP)"
            elif mode == "full":
                server_ids = self.process_manager.setup_full_hybrid_mode()
                mode_description = "フルハイブリッドモード (FastAPI + Enhanced FastAPI + MCP)"
            else:
                self.logger.error(f"不正なモード: {mode}")
                return False
            
            self.logger.info(f"モード: {mode_description}")
            self.logger.info(f"起動予定サーバー: {', '.join(server_ids)}")
            
            # 全サーバーを起動
            results = await self.process_manager.start_all(server_ids)
            
            # 結果を確認
            failed_servers = [server_id for server_id, success in results.items() if not success]
            if failed_servers:
                self.logger.error(f"以下のサーバーの起動に失敗しました: {', '.join(failed_servers)}")
                return False
            
            self.logger.info("全サーバーが正常に起動しました")
            self.running = True
            
            # サーバー情報を表示
            self._display_server_info()
            
            return True
            
        except Exception as e:
            self.logger.error(f"ハイブリッドモードの起動中にエラーが発生しました: {e}")
            return False
    
    def _display_server_info(self):
        """サーバー情報を表示"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 ハイブリッドサーバー起動完了")
        self.logger.info("=" * 80)
        
        statuses = self.process_manager.get_all_statuses()
        for server_id, status in statuses.items():
            config = status.config
            
            self.logger.info(f"📍 {config.name} ({server_id})")
            self.logger.info(f"   状態: {status.state.value}")
            
            if config.server_type != ServerType.MCP:
                self.logger.info(f"   URL: http://{config.host}:{config.port}")
                self.logger.info(f"   ドキュメント: http://{config.host}:{config.port}/docs")
            else:
                self.logger.info(f"   プロトコル: Model Context Protocol (stdio)")
                self.logger.info(f"   MCPホスト統合: Claude Desktop, VS Code, Claude Code, Dify")
            
            self.logger.info(f"   機能:")
            for feature in config.features:
                self.logger.info(f"     {feature}")
            
            if status.pid:
                self.logger.info(f"   PID: {status.pid}")
            
            self.logger.info("")
        
        # システムサマリー
        summary = self.process_manager.get_system_summary()
        self.logger.info(f"システムサマリー:")
        self.logger.info(f"  総サーバー数: {summary['total_servers']}")
        self.logger.info(f"  実行中サーバー数: {summary['running_servers']}")
        self.logger.info(f"  停止中サーバー数: {summary['stopped_servers']}")
        
        self.logger.info("=" * 80)
        self.logger.info("🎯 ハイブリッド運用モード有効")
        self.logger.info("   - FastAPIサーバー: HTTP REST API提供")
        self.logger.info("   - MCPサーバー: MCPホスト統合")
        self.logger.info("   - 両サーバーは同じバックエンドを共有")
        self.logger.info("   - 統合監視とプロセス管理が有効")
        self.logger.info("=" * 80)
    
    async def run_forever(self):
        """メインループ"""
        self.logger.info("ハイブリッドサーバーの実行を開始しています...")
        
        try:
            while self.running and not self.shutdown_requested:
                # 定期的な状態チェック
                await self._periodic_health_check()
                
                # 少し待機
                await asyncio.sleep(30)
                
        except Exception as e:
            self.logger.error(f"メインループ中にエラーが発生しました: {e}")
        finally:
            await self.shutdown()
    
    async def _periodic_health_check(self):
        """定期的なヘルスチェック"""
        try:
            running_servers = self.process_manager.get_running_servers()
            total_servers = len(self.process_manager.get_all_statuses())
            
            if len(running_servers) < total_servers:
                self.logger.warning(f"一部のサーバーが停止しています: {running_servers}/{total_servers}")
            
            # 詳細な状態ログ（デバッグレベル）
            if self.logger.isEnabledFor(logging.DEBUG):
                statuses = self.process_manager.get_all_statuses()
                for server_id, status in statuses.items():
                    self.logger.debug(f"サーバー '{server_id}': {status.state.value}")
                    
        except Exception as e:
            self.logger.error(f"ヘルスチェック中にエラーが発生しました: {e}")
    
    async def shutdown(self):
        """シャットダウン"""
        if not self.running:
            return
        
        self.logger.info("ハイブリッドサーバーのシャットダウンを開始しています...")
        self.running = False
        
        try:
            # 全サーバーを停止
            await self.process_manager.shutdown_all()
            self.logger.info("ハイブリッドサーバーのシャットダウンが完了しました")
            
        except Exception as e:
            self.logger.error(f"シャットダウン中にエラーが発生しました: {e}")
    
    async def status_check(self):
        """ステータスチェック"""
        statuses = self.process_manager.get_all_statuses()
        summary = self.process_manager.get_system_summary()
        
        print("=" * 60)
        print("🔍 ハイブリッドサーバー ステータス")
        print("=" * 60)
        
        for server_id, status in statuses.items():
            config = status.config
            print(f"📍 {config.name} ({server_id})")
            print(f"   状態: {status.state.value}")
            
            if status.state.value == "running":
                print(f"   ✅ 実行中")
                if config.server_type != ServerType.MCP:
                    print(f"   📊 URL: http://{config.host}:{config.port}")
                else:
                    print(f"   📊 プロトコル: MCP (stdio)")
                    
                if status.pid:
                    print(f"   🔢 PID: {status.pid}")
                if status.start_time:
                    print(f"   ⏰ 開始時刻: {status.start_time}")
            else:
                print(f"   ❌ 停止中")
                if status.error_message:
                    print(f"   💥 エラー: {status.error_message}")
            
            print()
        
        print("システムサマリー:")
        print(f"  総サーバー数: {summary['total_servers']}")
        print(f"  実行中: {summary['running_servers']}")
        print(f"  停止中: {summary['stopped_servers']}")
        print(f"  マネージャー稼働時間: {summary['manager_uptime']:.1f}秒")
        print("=" * 60)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="MFG Drone ハイブリッドサーバー - Phase 3 実装",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本ハイブリッドモード (FastAPI + MCP)
  python start_hybrid_server.py --mode basic
  
  # 拡張ハイブリッドモード (Enhanced FastAPI + MCP)
  python start_hybrid_server.py --mode enhanced
  
  # フルハイブリッドモード (FastAPI + Enhanced FastAPI + MCP)
  python start_hybrid_server.py --mode full
  
  # ステータスチェック
  python start_hybrid_server.py --status
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["basic", "enhanced", "full"],
        default="basic",
        help="ハイブリッドモード選択"
    )
    
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="ステータスチェックのみ実行"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="ログレベル"
    )
    
    args = parser.parse_args()
    
    # ロギング設定
    setup_logging(log_level=args.log_level)
    logger = get_logger(__name__)
    
    # ハイブリッドサーバーマネージャーを作成
    hybrid_manager = HybridServerManager()
    
    if args.status:
        # ステータスチェックのみ
        asyncio.run(hybrid_manager.status_check())
        return
    
    # メイン実行
    async def run_main():
        try:
            logger.info("=" * 80)
            logger.info("🚀 MFG Drone ハイブリッドサーバー Phase 3")
            logger.info("=" * 80)
            logger.info(f"モード: {args.mode}")
            logger.info(f"ログレベル: {args.log_level}")
            logger.info(f"バックエンドAPI: {settings.backend_api_url}")
            
            # ハイブリッドモードを起動
            success = await hybrid_manager.start_hybrid_mode(args.mode)
            if not success:
                logger.error("ハイブリッドモードの起動に失敗しました")
                sys.exit(1)
            
            # メインループを実行
            await hybrid_manager.run_forever()
            
        except KeyboardInterrupt:
            logger.info("ユーザーにより中断されました")
        except Exception as e:
            logger.error(f"予期しないエラーが発生しました: {e}")
            sys.exit(1)
    
    # 実行
    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        logger.info("🛑 ハイブリッドサーバーが停止されました")
    except Exception as e:
        logger.error(f"❌ ハイブリッドサーバーの実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()