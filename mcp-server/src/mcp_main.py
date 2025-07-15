#!/usr/bin/env python3
"""
真のMCPサーバー実装 - Model Context Protocol対応
ドローン制御用MCPサーバー
"""

import asyncio
import logging
import sys
from typing import Dict, Any, List, Optional, Sequence
from pathlib import Path

# MCP SDK imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListResourcesRequest,
    ListResourcesResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    ResourceContent,
    ResourceTemplate,
    EmbeddedResource,
    ErrorCode,
    McpError,
)

# パスの設定
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(src_path.parent / "config"))

# 既存のコンポーネントをインポート
from core.backend_client import BackendClient
from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter
from config.settings import settings
from config.logging import setup_logging, get_logger

# ロギング設定
setup_logging()
logger = get_logger(__name__)

# グローバルインスタンス
backend_client = BackendClient()
nlp_engine = NLPEngine()
command_router = CommandRouter(backend_client)

# MCPサーバーインスタンス
server = Server("mfg-drone-mcp-server")

# MCPツールの定義
TOOLS: List[Tool] = [
    Tool(
        name="connect_drone",
        description="指定したドローンに接続します",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "接続するドローンのID"
                }
            },
            "required": ["drone_id"]
        }
    ),
    Tool(
        name="takeoff_drone",
        description="ドローンを離陸させます",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "離陸させるドローンのID"
                },
                "target_height": {
                    "type": "number",
                    "description": "目標高度（メートル）",
                    "default": 1.0
                }
            },
            "required": ["drone_id"]
        }
    ),
    Tool(
        name="land_drone",
        description="ドローンを着陸させます",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "着陸させるドローンのID"
                }
            },
            "required": ["drone_id"]
        }
    ),
    Tool(
        name="move_drone",
        description="ドローンを移動させます",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "移動させるドローンのID"
                },
                "direction": {
                    "type": "string",
                    "enum": ["forward", "backward", "left", "right", "up", "down"],
                    "description": "移動方向"
                },
                "distance": {
                    "type": "number",
                    "description": "移動距離（センチメートル）",
                    "minimum": 1,
                    "maximum": 500
                },
                "speed": {
                    "type": "number",
                    "description": "移動速度（cm/s）",
                    "minimum": 10,
                    "maximum": 100,
                    "default": 20
                }
            },
            "required": ["drone_id", "direction", "distance"]
        }
    ),
    Tool(
        name="rotate_drone",
        description="ドローンを回転させます",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "回転させるドローンのID"
                },
                "direction": {
                    "type": "string",
                    "enum": ["clockwise", "counter_clockwise"],
                    "description": "回転方向"
                },
                "angle": {
                    "type": "number",
                    "description": "回転角度（度）",
                    "minimum": 1,
                    "maximum": 360
                }
            },
            "required": ["drone_id", "direction", "angle"]
        }
    ),
    Tool(
        name="take_photo",
        description="ドローンのカメラで写真を撮影します",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "撮影するドローンのID"
                },
                "filename": {
                    "type": "string",
                    "description": "保存するファイル名（オプション）"
                },
                "quality": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "画質設定",
                    "default": "high"
                }
            },
            "required": ["drone_id"]
        }
    ),
    Tool(
        name="execute_natural_language_command",
        description="自然言語でドローンを制御します。日本語の指示を理解して実行します",
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "実行する自然言語コマンド（例：前に進め、写真を撮って、など）"
                },
                "drone_id": {
                    "type": "string",
                    "description": "制御するドローンのID"
                },
                "context": {
                    "type": "string",
                    "description": "コマンドの文脈情報（オプション）"
                }
            },
            "required": ["command", "drone_id"]
        }
    ),
    Tool(
        name="emergency_stop",
        description="ドローンを緊急停止させます",
        inputSchema={
            "type": "object",
            "properties": {
                "drone_id": {
                    "type": "string",
                    "description": "緊急停止させるドローンのID"
                }
            },
            "required": ["drone_id"]
        }
    )
]

# MCPリソースの定義
RESOURCES: List[Resource] = [
    Resource(
        uri="drone://available",
        name="利用可能なドローン",
        mimeType="application/json",
        description="システムで利用可能なドローンの一覧"
    ),
    Resource(
        uri="drone://status",
        name="ドローンステータス",
        mimeType="application/json",
        description="全ドローンの現在のステータス情報"
    ),
    Resource(
        uri="system://status",
        name="システムステータス",
        mimeType="application/json",
        description="MCPサーバーとバックエンドシステムのステータス"
    )
]

@server.list_tools()
async def list_tools(request: ListToolsRequest) -> List[Tool]:
    """利用可能なツールの一覧を返す"""
    logger.info("リクエスト: 利用可能なツール一覧")
    return TOOLS

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """ツールを呼び出す"""
    logger.info(f"ツール呼び出し: {request.name}")
    
    try:
        args = request.arguments or {}
        
        if request.name == "connect_drone":
            return await _connect_drone(args)
        elif request.name == "takeoff_drone":
            return await _takeoff_drone(args)
        elif request.name == "land_drone":
            return await _land_drone(args)
        elif request.name == "move_drone":
            return await _move_drone(args)
        elif request.name == "rotate_drone":
            return await _rotate_drone(args)
        elif request.name == "take_photo":
            return await _take_photo(args)
        elif request.name == "execute_natural_language_command":
            return await _execute_natural_language_command(args)
        elif request.name == "emergency_stop":
            return await _emergency_stop(args)
        else:
            raise McpError(
                code=ErrorCode.METHOD_NOT_FOUND,
                message=f"未知のツール: {request.name}"
            )
    
    except Exception as e:
        logger.error(f"ツール実行エラー ({request.name}): {str(e)}")
        raise McpError(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"ツール実行エラー: {str(e)}"
        )

@server.list_resources()
async def list_resources(request: ListResourcesRequest) -> ListResourcesResult:
    """利用可能なリソースの一覧を返す"""
    logger.info("リクエスト: 利用可能なリソース一覧")
    return ListResourcesResult(resources=RESOURCES)

@server.read_resource()
async def read_resource(request: ReadResourceRequest) -> ReadResourceResult:
    """リソースを読み取る"""
    logger.info(f"リソース読み取り: {request.uri}")
    
    try:
        if request.uri == "drone://available":
            return await _get_available_drones()
        elif request.uri == "drone://status":
            return await _get_drone_status()
        elif request.uri == "system://status":
            return await _get_system_status()
        else:
            raise McpError(
                code=ErrorCode.INVALID_REQUEST,
                message=f"未知のリソース: {request.uri}"
            )
    
    except Exception as e:
        logger.error(f"リソース読み取りエラー ({request.uri}): {str(e)}")
        raise McpError(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"リソース読み取りエラー: {str(e)}"
        )

# ツール実装関数群

async def _connect_drone(args: Dict[str, Any]) -> CallToolResult:
    """ドローン接続"""
    drone_id = args["drone_id"]
    
    try:
        result = await backend_client.connect_drone(drone_id)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} に接続しました。\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} への接続に失敗しました: {str(e)}"
                )
            ]
        )

async def _takeoff_drone(args: Dict[str, Any]) -> CallToolResult:
    """ドローン離陸"""
    drone_id = args["drone_id"]
    target_height = args.get("target_height", 1.0)
    
    try:
        result = await backend_client.takeoff_drone(drone_id, target_height)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} が離陸しました。\n目標高度: {target_height}m\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} の離陸に失敗しました: {str(e)}"
                )
            ]
        )

async def _land_drone(args: Dict[str, Any]) -> CallToolResult:
    """ドローン着陸"""
    drone_id = args["drone_id"]
    
    try:
        result = await backend_client.land_drone(drone_id)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} が着陸しました。\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} の着陸に失敗しました: {str(e)}"
                )
            ]
        )

async def _move_drone(args: Dict[str, Any]) -> CallToolResult:
    """ドローン移動"""
    drone_id = args["drone_id"]
    direction = args["direction"]
    distance = args["distance"]
    speed = args.get("speed", 20)
    
    try:
        result = await backend_client.move_drone(drone_id, direction, distance, speed)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} が移動しました。\n方向: {direction}\n距離: {distance}cm\n速度: {speed}cm/s\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} の移動に失敗しました: {str(e)}"
                )
            ]
        )

async def _rotate_drone(args: Dict[str, Any]) -> CallToolResult:
    """ドローン回転"""
    drone_id = args["drone_id"]
    direction = args["direction"]
    angle = args["angle"]
    
    try:
        result = await backend_client.rotate_drone(drone_id, direction, angle)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} が回転しました。\n方向: {direction}\n角度: {angle}度\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} の回転に失敗しました: {str(e)}"
                )
            ]
        )

async def _take_photo(args: Dict[str, Any]) -> CallToolResult:
    """写真撮影"""
    drone_id = args["drone_id"]
    filename = args.get("filename")
    quality = args.get("quality", "high")
    
    try:
        result = await backend_client.take_photo(drone_id, filename, quality)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} で写真を撮影しました。\nファイル名: {filename or '自動生成'}\n画質: {quality}\n結果: 撮影成功"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} での写真撮影に失敗しました: {str(e)}"
                )
            ]
        )

async def _execute_natural_language_command(args: Dict[str, Any]) -> CallToolResult:
    """自然言語コマンド実行"""
    command = args["command"]
    drone_id = args["drone_id"]
    context = args.get("context", "")
    
    try:
        # NLPエンジンでコマンドを解析
        from models.command_models import NaturalLanguageCommand
        nl_command = NaturalLanguageCommand(
            command=command,
            context=context
        )
        
        parsed_intent = nlp_engine.parse_command(nl_command.command, nl_command.context)
        
        # 信頼度チェック
        if parsed_intent.confidence < settings.nlp_confidence_threshold:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"コマンドの解析に失敗しました。\n信頼度が低いです ({parsed_intent.confidence:.2f})。\nコマンドを言い換えてください。"
                    )
                ]
            )
        
        # コマンドを実行
        result = await command_router.execute_command(parsed_intent)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"自然言語コマンドを実行しました。\nコマンド: {command}\nドローン: {drone_id}\n結果: {result.message}\n成功: {result.success}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"自然言語コマンドの実行に失敗しました: {str(e)}"
                )
            ]
        )

async def _emergency_stop(args: Dict[str, Any]) -> CallToolResult:
    """緊急停止"""
    drone_id = args["drone_id"]
    
    try:
        result = await backend_client.emergency_stop(drone_id)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} を緊急停止しました。\n結果: {result.message}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"ドローン {drone_id} の緊急停止に失敗しました: {str(e)}"
                )
            ]
        )

# リソース読み取り関数群

async def _get_available_drones() -> ReadResourceResult:
    """利用可能なドローンの取得"""
    try:
        drones = await backend_client.get_available_drones()
        import json
        
        content = json.dumps({
            "available_drones": drones,
            "count": len(drones),
            "timestamp": str(asyncio.get_event_loop().time())
        }, indent=2, ensure_ascii=False)
        
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=content
                )
            ]
        )
    except Exception as e:
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=f"利用可能なドローンの取得に失敗しました: {str(e)}"
                )
            ]
        )

async def _get_drone_status() -> ReadResourceResult:
    """ドローンステータスの取得"""
    try:
        # 全ドローンのステータスを取得
        drones = await backend_client.get_drones()
        statuses = {}
        
        for drone in drones:
            try:
                status = await backend_client.get_drone_status(drone["id"])
                statuses[drone["id"]] = status
            except Exception as e:
                statuses[drone["id"]] = {"error": str(e)}
        
        import json
        content = json.dumps({
            "drone_statuses": statuses,
            "timestamp": str(asyncio.get_event_loop().time())
        }, indent=2, ensure_ascii=False)
        
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=content
                )
            ]
        )
    except Exception as e:
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=f"ドローンステータスの取得に失敗しました: {str(e)}"
                )
            ]
        )

async def _get_system_status() -> ReadResourceResult:
    """システムステータスの取得"""
    try:
        backend_status = await backend_client.get_system_status()
        
        import json
        content = json.dumps({
            "mcp_server": {
                "status": "running",
                "version": "1.0.0",
                "protocol": "Model Context Protocol"
            },
            "backend_system": backend_status,
            "timestamp": str(asyncio.get_event_loop().time())
        }, indent=2, ensure_ascii=False)
        
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=content
                )
            ]
        )
    except Exception as e:
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=f"システムステータスの取得に失敗しました: {str(e)}"
                )
            ]
        )

async def main():
    """MCPサーバーのメイン関数"""
    logger.info("MCP Server starting...")
    
    try:
        # サーバーを起動
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mfg-drone-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
    except Exception as e:
        logger.error(f"MCPサーバーの実行中にエラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())