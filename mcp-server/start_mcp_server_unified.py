#!/usr/bin/env python3
"""
統合起動スクリプト - FastAPIモード、MCPモード、ハイブリッドモードをサポート
Phase 3: ハイブリッド運用対応版
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

# パス設定
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from config.settings import settings
from config.logging import setup_logging, get_logger


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="MFG Drone MCP Server - 統合起動スクリプト (Phase 3 ハイブリッド運用対応)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # FastAPIモード（従来のHTTPサーバー）
  python start_mcp_server_unified.py --mode fastapi
  
  # MCPモード（Model Context Protocol対応）
  python start_mcp_server_unified.py --mode mcp
  
  # 拡張FastAPIモード
  python start_mcp_server_unified.py --mode fastapi --enhanced
  
  # ハイブリッドモード（FastAPI + MCP同時実行）
  python start_mcp_server_unified.py --mode hybrid
  
  # 拡張ハイブリッドモード（Enhanced FastAPI + MCP同時実行）
  python start_mcp_server_unified.py --mode hybrid --enhanced
  
  # フルハイブリッドモード（FastAPI + Enhanced FastAPI + MCP同時実行）
  python start_mcp_server_unified.py --mode hybrid --full
  
  # カスタムポート
  python start_mcp_server_unified.py --mode fastapi --port 8002
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["fastapi", "mcp", "hybrid"],
        required=True,
        help="サーバーモード選択: fastapi (HTTP API), mcp (Model Context Protocol), または hybrid (両方同時実行)"
    )
    
    parser.add_argument(
        "--enhanced", "-e",
        action="store_true",
        help="拡張機能を有効にする（FastAPIモードまたはハイブリッドモード）"
    )
    
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="フル機能を有効にする（ハイブリッドモードのみ - 全サーバー同時実行）"
    )
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"バインドするホスト (デフォルト: {settings.host})"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=settings.port,
        help=f"バインドするポート (デフォルト: {settings.port})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.debug,
        help="開発用オートリロードを有効にする"
    )
    
    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"ログレベル (デフォルト: {settings.log_level})"
    )
    
    args = parser.parse_args()
    
    # ロギング設定
    setup_logging(log_level=args.log_level)
    logger = get_logger(__name__)
    
    if args.mode == "fastapi":
        run_fastapi_server(args, logger)
    elif args.mode == "mcp":
        run_mcp_server(args, logger)
    elif args.mode == "hybrid":
        run_hybrid_server(args, logger)


def run_fastapi_server(args, logger):
    """FastAPIサーバーを起動"""
    import uvicorn
    
    # モジュール選択
    if args.enhanced:
        app_module = "src.enhanced_main:app"
        server_type = "Enhanced FastAPI Server (Phase 2)"
        features = [
            "✨ 高度な自然言語処理",
            "🧠 コンテキスト認識コマンド理解", 
            "🚀 インテリジェントバッチ処理",
            "📊 依存関係分析・最適化",
            "🔄 スマートエラー回復",
            "📈 実行分析"
        ]
    else:
        app_module = "src.main:app"
        server_type = "Original FastAPI Server (Phase 1)"
        features = [
            "📝 基本的な自然言語処理",
            "🎯 コマンドルーティング",
            "📦 シンプルなバッチ処理", 
            "🌐 完全なAPI実装"
        ]
    
    logger.info(f"Starting {server_type}")
    logger.info("機能:")
    for feature in features:
        logger.info(f"  {feature}")
    
    logger.info(f"ホスト: {args.host}")
    logger.info(f"ポート: {args.port}")
    logger.info(f"デバッグモード: {args.reload}")
    logger.info(f"バックエンドAPI URL: {settings.backend_api_url}")
    logger.info(f"サーバーアドレス: http://{args.host}:{args.port}")
    logger.info(f"APIドキュメント: http://{args.host}:{args.port}/docs")
    logger.info("-" * 60)
    
    try:
        uvicorn.run(
            app_module,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 FastAPIサーバーがユーザーにより停止されました")
    except Exception as e:
        logger.error(f"❌ FastAPIサーバーの起動に失敗しました: {e}")
        sys.exit(1)


def run_mcp_server(args, logger):
    """MCPサーバーを起動"""
    logger.info("Starting MCP Server (Model Context Protocol)")
    logger.info("機能:")
    logger.info("  🤖 Model Context Protocol対応")
    logger.info("  🔧 MCPホスト統合 (Claude Desktop, VS Code, etc.)")
    logger.info("  🎯 ドローン制御ツール")
    logger.info("  📋 リアルタイムリソース")
    logger.info("  🗣️ 自然言語コマンド処理")
    logger.info("  📊 システムステータス監視")
    
    logger.info(f"ログレベル: {args.log_level}")
    logger.info(f"バックエンドAPI URL: {settings.backend_api_url}")
    logger.info("MCPサーバーは標準入出力を使用してMCPホストと通信します")
    logger.info("-" * 60)
    
    try:
        # MCPサーバーを起動
        from src.mcp_main import main as mcp_main
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        logger.info("🛑 MCPサーバーがユーザーにより停止されました")
    except Exception as e:
        logger.error(f"❌ MCPサーバーの起動に失敗しました: {e}")
        sys.exit(1)


def run_hybrid_server(args, logger):
    """ハイブリッドサーバーを起動（Phase 3 実装）"""
    logger.info("Starting Hybrid Server (Phase 3 - FastAPI + MCP)")
    
    # ハイブリッドモードの決定
    if args.full:
        hybrid_mode = "full"
        mode_description = "フルハイブリッドモード (FastAPI + Enhanced FastAPI + MCP)"
        features = [
            "🚀 FastAPI Server (基本機能)",
            "✨ Enhanced FastAPI Server (高度な機能)",
            "🤖 MCP Server (Model Context Protocol)",
            "⚡ 並行実行・統合監視",
            "🔄 プロセス管理・自動復旧",
            "📊 統合ステータス監視"
        ]
    elif args.enhanced:
        hybrid_mode = "enhanced"
        mode_description = "拡張ハイブリッドモード (Enhanced FastAPI + MCP)"
        features = [
            "✨ Enhanced FastAPI Server (高度な機能)",
            "🤖 MCP Server (Model Context Protocol)",
            "⚡ 並行実行・統合監視",
            "🔄 プロセス管理・自動復旧",
            "📊 統合ステータス監視"
        ]
    else:
        hybrid_mode = "basic"
        mode_description = "基本ハイブリッドモード (FastAPI + MCP)"
        features = [
            "🚀 FastAPI Server (基本機能)",
            "🤖 MCP Server (Model Context Protocol)",
            "⚡ 並行実行・統合監視",
            "🔄 プロセス管理・自動復旧",
            "📊 統合ステータス監視"
        ]
    
    logger.info(f"モード: {mode_description}")
    logger.info("機能:")
    for feature in features:
        logger.info(f"  {feature}")
    
    logger.info(f"ログレベル: {args.log_level}")
    logger.info(f"バックエンドAPI URL: {settings.backend_api_url}")
    logger.info("ハイブリッドモードでは複数のサーバーが同時に実行されます")
    logger.info("-" * 60)
    
    try:
        # ハイブリッドサーバーマネージャーを起動
        from core.hybrid_process_manager import HybridProcessManager
        from start_hybrid_server import HybridServerManager
        
        hybrid_manager = HybridServerManager()
        
        # 非同期でハイブリッドモードを実行
        async def run_hybrid():
            success = await hybrid_manager.start_hybrid_mode(hybrid_mode)
            if not success:
                logger.error("ハイブリッドモードの起動に失敗しました")
                sys.exit(1)
            
            # メインループを実行
            await hybrid_manager.run_forever()
        
        # 実行
        asyncio.run(run_hybrid())
        
    except KeyboardInterrupt:
        logger.info("🛑 ハイブリッドサーバーがユーザーにより停止されました")
    except Exception as e:
        logger.error(f"❌ ハイブリッドサーバーの起動に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()