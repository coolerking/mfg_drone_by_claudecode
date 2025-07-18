#!/usr/bin/env python3
"""
統合テストスクリプト - MCPサーバーとバックエンドAPIの統合テスト
"""

import sys
import os
from pathlib import Path
import importlib.util
import json
import traceback

# パス設定
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "src"))
sys.path.insert(0, str(script_dir / "config"))

def test_imports():
    """重要なモジュールのインポートテスト"""
    test_results = {}
    
    # 1. 設定のインポート
    try:
        from config.settings import settings
        test_results["settings_import"] = True
        test_results["backend_api_url"] = settings.backend_api_url
    except Exception as e:
        test_results["settings_import"] = False
        test_results["settings_error"] = str(e)
    
    # 2. MCPメインのインポート
    try:
        from src.mcp_main import main
        test_results["mcp_main_import"] = True
    except Exception as e:
        test_results["mcp_main_import"] = False
        test_results["mcp_main_error"] = str(e)
    
    # 3. バックエンドクライアントのインポート
    try:
        from src.core.backend_client import DroneBackendClient
        test_results["backend_client_import"] = True
    except Exception as e:
        test_results["backend_client_import"] = False
        test_results["backend_client_error"] = str(e)
    
    # 4. NLPエンジンのインポート
    try:
        from src.core.nlp_engine import EnhancedNLPEngine
        test_results["nlp_engine_import"] = True
    except Exception as e:
        test_results["nlp_engine_import"] = False
        test_results["nlp_engine_error"] = str(e)
    
    # 5. コマンドルーターのインポート
    try:
        from src.core.command_router import CommandRouter
        test_results["command_router_import"] = True
    except Exception as e:
        test_results["command_router_import"] = False
        test_results["command_router_error"] = str(e)
    
    return test_results

def test_configuration():
    """設定の検証テスト"""
    test_results = {}
    
    try:
        from config.settings import settings
        
        # 基本設定の確認
        test_results["server_title"] = settings.server_title
        test_results["server_version"] = settings.server_version
        test_results["backend_api_url"] = settings.backend_api_url
        test_results["environment"] = settings.environment
        test_results["log_level"] = settings.log_level
        
        # セキュリティ設定の確認
        test_results["max_failed_attempts"] = settings.max_failed_attempts
        test_results["lockout_duration"] = settings.lockout_duration
        
        # NLP設定の確認
        test_results["default_language"] = settings.default_language
        test_results["nlp_confidence_threshold"] = settings.nlp_confidence_threshold
        
        test_results["configuration_test"] = True
        
    except Exception as e:
        test_results["configuration_test"] = False
        test_results["configuration_error"] = str(e)
    
    return test_results

def test_core_components():
    """コアコンポーネントのテスト"""
    test_results = {}
    
    # 1. バックエンドクライアントの初期化テスト
    try:
        from src.core.backend_client import DroneBackendClient
        client = DroneBackendClient()
        
        # 必要なメソッドの確認
        required_methods = [
            "get_drone_status",
            "send_command", 
            "get_camera_frame",
            "start_video_stream",
            "stop_video_stream",
            "get_system_status"
        ]
        
        method_status = {}
        for method in required_methods:
            method_status[method] = hasattr(client, method)
        
        test_results["backend_client_methods"] = method_status
        test_results["backend_client_init"] = True
        
    except Exception as e:
        test_results["backend_client_init"] = False
        test_results["backend_client_error"] = str(e)
    
    # 2. NLPエンジンの初期化テスト
    try:
        from src.core.nlp_engine import EnhancedNLPEngine
        nlp_engine = EnhancedNLPEngine()
        test_results["nlp_engine_init"] = True
        
        # 基本的なメソッドの確認
        nlp_methods = ["process_natural_language", "extract_intent", "extract_entities"]
        nlp_method_status = {}
        for method in nlp_methods:
            nlp_method_status[method] = hasattr(nlp_engine, method)
        
        test_results["nlp_engine_methods"] = nlp_method_status
        
    except Exception as e:
        test_results["nlp_engine_init"] = False
        test_results["nlp_engine_error"] = str(e)
    
    # 3. セキュリティマネージャーの初期化テスト
    try:
        from src.core.security_manager import SecurityManager
        security_manager = SecurityManager()
        test_results["security_manager_init"] = True
        
        security_methods = ["authenticate_user", "authorize_action", "audit_log"]
        security_method_status = {}
        for method in security_methods:
            security_method_status[method] = hasattr(security_manager, method)
        
        test_results["security_manager_methods"] = security_method_status
        
    except Exception as e:
        test_results["security_manager_init"] = False
        test_results["security_manager_error"] = str(e)
    
    return test_results

def test_mcp_integration():
    """MCP統合機能のテスト"""
    test_results = {}
    
    # 1. MCP設定ファイルの確認
    mcp_config_file = script_dir / "mcp_config.json"
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
            
            test_results["mcp_config_loaded"] = True
            test_results["mcp_tools_count"] = len(mcp_config.get("tools", []))
            test_results["mcp_resources_count"] = len(mcp_config.get("resources", []))
            
            # ツールの詳細
            if "tools" in mcp_config:
                tools = mcp_config["tools"]
                tool_names = [tool.get("name") for tool in tools]
                test_results["mcp_tool_names"] = tool_names
            
            # リソースの詳細
            if "resources" in mcp_config:
                resources = mcp_config["resources"]
                resource_names = [resource.get("name") for resource in resources]
                test_results["mcp_resource_names"] = resource_names
            
        except Exception as e:
            test_results["mcp_config_loaded"] = False
            test_results["mcp_config_error"] = str(e)
    else:
        test_results["mcp_config_loaded"] = False
        test_results["mcp_config_error"] = "設定ファイルが見つかりません"
    
    # 2. MCPメインファイルの基本構造確認
    try:
        mcp_main_file = script_dir / "src" / "mcp_main.py"
        if mcp_main_file.exists():
            content = mcp_main_file.read_text(encoding='utf-8')
            
            # 重要なimportの確認
            test_results["mcp_server_import"] = "from mcp.server import Server" in content
            test_results["mcp_stdio_import"] = "from mcp.server.stdio import stdio_server" in content
            test_results["mcp_types_import"] = "from mcp.types import" in content
            
            # 重要な関数の確認
            test_results["main_function"] = "async def main(" in content
            test_results["setup_tools"] = "setup_tools" in content
            test_results["setup_resources"] = "setup_resources" in content
            
            test_results["mcp_main_structure"] = True
        else:
            test_results["mcp_main_structure"] = False
            test_results["mcp_main_error"] = "mcp_main.pyが見つかりません"
            
    except Exception as e:
        test_results["mcp_main_structure"] = False
        test_results["mcp_main_error"] = str(e)
    
    return test_results

def generate_test_report(results):
    """テストレポートの生成"""
    
    # 成功率の計算
    total_tests = 0
    passed_tests = 0
    
    for category, test_results in results.items():
        for key, value in test_results.items():
            if isinstance(value, bool):
                total_tests += 1
                if value:
                    passed_tests += 1
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bool):
                        total_tests += 1
                        if sub_value:
                            passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("=" * 60)
    print("📊 統合テスト結果")
    print("=" * 60)
    print(f"総テスト数: {total_tests}")
    print(f"成功数: {passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    print()
    
    # 詳細結果の表示
    for category, test_results in results.items():
        print(f"## {category}")
        print("-" * 40)
        
        for key, value in test_results.items():
            if isinstance(value, bool):
                status = "✅ 成功" if value else "❌ 失敗"
                print(f"{key}: {status}")
            elif isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bool):
                        status = "✅" if sub_value else "❌"
                        print(f"  {sub_key}: {status}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            elif key.endswith("_error"):
                print(f"エラー詳細: {value}")
            else:
                print(f"{key}: {value}")
        print()
    
    return success_rate

def main():
    """メイン関数"""
    print("=" * 60)
    print("🧪 統合テストスクリプト")
    print("MCPサーバーとバックエンドAPIの統合テスト")
    print("=" * 60)
    
    # 各テストの実行
    print("1. インポートテスト実行中...")
    import_results = test_imports()
    
    print("2. 設定テスト実行中...")
    config_results = test_configuration()
    
    print("3. コアコンポーネントテスト実行中...")
    component_results = test_core_components()
    
    print("4. MCP統合テスト実行中...")
    mcp_results = test_mcp_integration()
    
    # 結果の統合
    all_results = {
        "インポートテスト": import_results,
        "設定テスト": config_results,
        "コアコンポーネントテスト": component_results,
        "MCP統合テスト": mcp_results
    }
    
    # レポート生成
    success_rate = generate_test_report(all_results)
    
    # 結果の判定
    if success_rate >= 90:
        print("🎉 統合テストが正常に完了しました！")
        return 0
    elif success_rate >= 70:
        print("⚠️  統合テストは概ね成功しましたが、一部の問題があります")
        return 1
    else:
        print("❌ 統合テストで重要な問題が発見されました")
        return 2

if __name__ == "__main__":
    sys.exit(main())