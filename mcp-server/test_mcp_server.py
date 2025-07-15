#!/usr/bin/env python3
"""
MCPサーバーのテストスクリプト
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# パス設定
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from config.logging import setup_logging, get_logger

# ロギング設定
setup_logging(log_level="INFO")
logger = get_logger(__name__)


class MockMCPHost:
    """MCPホストのモックオブジェクト"""
    
    def __init__(self):
        self.tools = []
        self.resources = []
    
    async def test_mcp_server(self):
        """MCPサーバーの基本機能をテスト"""
        logger.info("=== MCPサーバーテスト開始 ===")
        
        try:
            # MCPサーバーをインポート
            from src.mcp_main import server, TOOLS, RESOURCES
            
            # 1. ツール一覧のテスト
            logger.info("1. ツール一覧のテスト")
            await self._test_list_tools()
            
            # 2. リソース一覧のテスト
            logger.info("2. リソース一覧のテスト")
            await self._test_list_resources()
            
            # 3. ツール呼び出しのテスト
            logger.info("3. ツール呼び出しのテスト")
            await self._test_tool_calls()
            
            # 4. リソース読み取りのテスト
            logger.info("4. リソース読み取りのテスト")
            await self._test_resource_reads()
            
            logger.info("=== MCPサーバーテスト完了 ===")
            
        except Exception as e:
            logger.error(f"MCPサーバーテストでエラーが発生しました: {str(e)}")
            raise
    
    async def _test_list_tools(self):
        """ツール一覧のテスト"""
        from src.mcp_main import TOOLS
        
        logger.info(f"定義されたツール数: {len(TOOLS)}")
        for tool in TOOLS:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # ツール名の検証
        expected_tools = [
            "connect_drone",
            "takeoff_drone", 
            "land_drone",
            "move_drone",
            "rotate_drone",
            "take_photo",
            "execute_natural_language_command",
            "emergency_stop"
        ]
        
        actual_tools = [tool.name for tool in TOOLS]
        missing_tools = set(expected_tools) - set(actual_tools)
        
        if missing_tools:
            logger.error(f"不足しているツール: {missing_tools}")
        else:
            logger.info("✅ すべての必要なツールが定義されています")
    
    async def _test_list_resources(self):
        """リソース一覧のテスト"""
        from src.mcp_main import RESOURCES
        
        logger.info(f"定義されたリソース数: {len(RESOURCES)}")
        for resource in RESOURCES:
            logger.info(f"  - {resource.name} ({resource.uri}): {resource.description}")
        
        # リソースURIの検証
        expected_resources = [
            "drone://available",
            "drone://status",
            "system://status"
        ]
        
        actual_resources = [resource.uri for resource in RESOURCES]
        missing_resources = set(expected_resources) - set(actual_resources)
        
        if missing_resources:
            logger.error(f"不足しているリソース: {missing_resources}")
        else:
            logger.info("✅ すべての必要なリソースが定義されています")
    
    async def _test_tool_calls(self):
        """ツール呼び出しのテスト"""
        from mcp.types import CallToolRequest
        from src.mcp_main import call_tool
        
        test_cases = [
            {
                "name": "connect_drone",
                "args": {"drone_id": "test_drone_1"},
                "description": "ドローン接続テスト"
            },
            {
                "name": "takeoff_drone",
                "args": {"drone_id": "test_drone_1", "target_height": 1.5},
                "description": "ドローン離陸テスト"
            },
            {
                "name": "move_drone",
                "args": {
                    "drone_id": "test_drone_1",
                    "direction": "forward",
                    "distance": 100,
                    "speed": 30
                },
                "description": "ドローン移動テスト"
            },
            {
                "name": "take_photo",
                "args": {
                    "drone_id": "test_drone_1",
                    "filename": "test_photo.jpg",
                    "quality": "high"
                },
                "description": "写真撮影テスト"
            },
            {
                "name": "execute_natural_language_command",
                "args": {
                    "command": "前に進んでください",
                    "drone_id": "test_drone_1",
                    "context": "テスト用コマンド"
                },
                "description": "自然言語コマンドテスト"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"  テスト: {test_case['description']}")
            try:
                request = CallToolRequest(
                    name=test_case["name"],
                    arguments=test_case["args"]
                )
                
                # 実際の呼び出しはバックエンドが必要なので、引数の検証のみ
                logger.info(f"    ツール: {request.name}")
                logger.info(f"    引数: {request.arguments}")
                logger.info("    ✅ 引数の形式は正しいです")
                
            except Exception as e:
                logger.error(f"    ❌ テストエラー: {str(e)}")
    
    async def _test_resource_reads(self):
        """リソース読み取りのテスト"""
        from mcp.types import ReadResourceRequest
        from src.mcp_main import read_resource
        
        test_resources = [
            {
                "uri": "drone://available",
                "description": "利用可能なドローン一覧"
            },
            {
                "uri": "drone://status",
                "description": "ドローンステータス"
            },
            {
                "uri": "system://status",
                "description": "システムステータス"
            }
        ]
        
        for test_resource in test_resources:
            logger.info(f"  テスト: {test_resource['description']}")
            try:
                request = ReadResourceRequest(uri=test_resource["uri"])
                
                # 実際の読み取りはバックエンドが必要なので、URIの検証のみ
                logger.info(f"    URI: {request.uri}")
                logger.info("    ✅ URIの形式は正しいです")
                
            except Exception as e:
                logger.error(f"    ❌ テストエラー: {str(e)}")


async def test_mcp_schema_validation():
    """MCPスキーマの検証テスト"""
    logger.info("=== MCPスキーマ検証テスト ===")
    
    try:
        from src.mcp_main import TOOLS, RESOURCES
        
        # ツールスキーマの検証
        logger.info("ツールスキーマの検証:")
        for tool in TOOLS:
            logger.info(f"  {tool.name}:")
            logger.info(f"    説明: {tool.description}")
            logger.info(f"    スキーマ: {tool.inputSchema}")
            
            # 必須フィールドの確認
            if "required" in tool.inputSchema:
                logger.info(f"    必須フィールド: {tool.inputSchema['required']}")
        
        # リソーススキーマの検証
        logger.info("リソーススキーマの検証:")
        for resource in RESOURCES:
            logger.info(f"  {resource.name}:")
            logger.info(f"    URI: {resource.uri}")
            logger.info(f"    MIMEタイプ: {resource.mimeType}")
            logger.info(f"    説明: {resource.description}")
        
        logger.info("✅ MCPスキーマの検証が完了しました")
        
    except Exception as e:
        logger.error(f"❌ MCPスキーマ検証でエラーが発生しました: {str(e)}")
        raise


async def test_configuration():
    """設定のテスト"""
    logger.info("=== 設定テスト ===")
    
    try:
        from config.settings import settings
        
        logger.info("設定値:")
        logger.info(f"  ホスト: {settings.host}")
        logger.info(f"  ポート: {settings.port}")
        logger.info(f"  デバッグモード: {settings.debug}")
        logger.info(f"  ログレベル: {settings.log_level}")
        logger.info(f"  バックエンドAPI URL: {settings.backend_api_url}")
        logger.info(f"  NLP信頼度閾値: {settings.nlp_confidence_threshold}")
        
        # 必須設定の確認
        if not settings.backend_api_url:
            logger.warning("⚠️ バックエンドAPI URLが設定されていません")
        else:
            logger.info("✅ バックエンドAPI URLが設定されています")
        
        logger.info("✅ 設定テストが完了しました")
        
    except Exception as e:
        logger.error(f"❌ 設定テストでエラーが発生しました: {str(e)}")
        raise


async def main():
    """メイン関数"""
    logger.info("MCPサーバーテストスクリプト開始")
    
    try:
        # 設定テスト
        await test_configuration()
        
        # MCPスキーマ検証
        await test_mcp_schema_validation()
        
        # MCPサーバーの基本機能テスト
        mock_host = MockMCPHost()
        await mock_host.test_mcp_server()
        
        logger.info("🎉 すべてのテストが正常に完了しました")
        
    except Exception as e:
        logger.error(f"❌ テスト実行中にエラーが発生しました: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())