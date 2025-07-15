#!/usr/bin/env python3
"""
統合起動スクリプト - FastAPIモードとMCPモードの両方をサポート
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
        description="MFG Drone MCP Server - 統合起動スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # FastAPIモード（従来のHTTPサーバー）
  python start_mcp_server_unified.py --mode fastapi
  
  # MCPモード（Model Context Protocol対応）
  python start_mcp_server_unified.py --mode mcp
  
  # 拡張FastAPIモード
  python start_mcp_server_unified.py --mode fastapi --enhanced
  
  # カスタムポート
  python start_mcp_server_unified.py --mode fastapi --port 8002
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["fastapi", "mcp"],
        required=True,
        help="サーバーモード選択: fastapi (HTTP API) または mcp (Model Context Protocol)"
    )
    
    parser.add_argument(
        "--enhanced", "-e",
        action="store_true",
        help="拡張機能を有効にする（FastAPIモードのみ）"
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


if __name__ == "__main__":
    main()