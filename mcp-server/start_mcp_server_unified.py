#!/usr/bin/env python3
"""
MCP サーバー起動スクリプト - Model Context Protocol専用
Phase 6: FastAPIサーバー機能除去後の統合版
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
        description="MFG Drone MCP Server - Model Context Protocol専用起動スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # MCPモード（Model Context Protocol対応）
  python start_mcp_server_unified.py
  
  # カスタムログレベル
  python start_mcp_server_unified.py --log-level DEBUG
        """
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
    
    # MCPサーバーのみ起動
    run_mcp_server(args, logger)



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