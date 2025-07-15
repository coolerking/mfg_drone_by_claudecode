#!/usr/bin/env python3
"""
MCP設定検証スクリプト
MCPサーバーの設定と動作を確認するためのユーティリティ
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def validate_python_environment():
    """Python環境の検証"""
    print("🔍 Python環境を確認中...")
    
    # Pythonバージョン確認
    python_version = sys.version_info
    print(f"Python バージョン: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 9):
        print("❌ Python 3.9以上が必要です")
        return False
    
    # 必要なパッケージの確認
    required_packages = [
        "mcp",
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "structlog"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - インストール済み")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未インストール")
    
    if missing_packages:
        print(f"\n以下のパッケージをインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def validate_mcp_config(config_path: str = "mcp_config.json") -> Optional[Dict[str, Any]]:
    """MCP設定ファイルの検証"""
    print(f"\n🔍 MCP設定ファイルを確認中: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 設定ファイルの読み込み成功")
        
        # 基本構造の確認
        if "mcpServers" not in config:
            print("❌ 'mcpServers' セクションが見つかりません")
            return None
        
        servers = config["mcpServers"]
        if not servers:
            print("❌ MCPサーバーが設定されていません")
            return None
        
        # 各サーバー設定の確認
        for server_name, server_config in servers.items():
            print(f"\n📋 サーバー設定確認: {server_name}")
            
            # 必須フィールドの確認
            if "command" not in server_config:
                print(f"❌ 'command' フィールドが見つかりません")
                return None
            
            if "args" not in server_config:
                print(f"❌ 'args' フィールドが見つかりません")
                return None
            
            command = server_config["command"]
            args = server_config["args"]
            
            print(f"   コマンド: {command}")
            print(f"   引数: {args}")
            
            # メインスクリプトの存在確認
            if args and len(args) > 0:
                main_script = args[0]
                if not os.path.exists(main_script):
                    print(f"❌ メインスクリプトが見つかりません: {main_script}")
                    return None
                print(f"✅ メインスクリプト確認: {main_script}")
            
            # 環境変数の確認
            if "env" in server_config:
                env_vars = server_config["env"]
                print(f"   環境変数: {env_vars}")
        
        return config
        
    except json.JSONDecodeError as e:
        print(f"❌ 設定ファイルのJSONパースエラー: {e}")
        return None
    except Exception as e:
        print(f"❌ 設定ファイルの読み込みエラー: {e}")
        return None

def test_mcp_server():
    """MCPサーバーのテスト実行"""
    print("\n🔍 MCPサーバーのテスト実行中...")
    
    try:
        # テストスクリプトの実行
        result = subprocess.run(
            [sys.executable, "test_mcp_server.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ MCPサーバーのテスト成功")
            print("テスト出力:")
            print(result.stdout)
            return True
        else:
            print("❌ MCPサーバーのテスト失敗")
            print("エラー出力:")
            print(result.stderr)
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ MCPサーバーのテストがタイムアウトしました")
        return False
    except FileNotFoundError:
        print("❌ test_mcp_server.py が見つかりません")
        return False
    except Exception as e:
        print(f"❌ MCPサーバーのテスト中にエラーが発生: {e}")
        return False

def generate_sample_configs():
    """サンプル設定の生成"""
    print("\n📝 サンプル設定を生成中...")
    
    # 現在のディレクトリの絶対パス
    current_dir = os.path.abspath(".")
    main_script = os.path.join(current_dir, "src", "mcp_main.py")
    
    # Claude Desktop用設定
    claude_desktop_config = {
        "mcpServers": {
            "mfg-drone-mcp-server": {
                "command": "python",
                "args": [main_script],
                "env": {
                    "PYTHONPATH": current_dir,
                    "DRONE_MODE": "auto",
                    "TELLO_AUTO_DETECT": "true",
                    "LOG_LEVEL": "INFO"
                }
            }
        }
    }
    
    # VS Code用設定
    vscode_config = {
        "mcp.servers": {
            "mfg-drone-mcp-server": {
                "command": "python",
                "args": [main_script],
                "env": {
                    "PYTHONPATH": current_dir,
                    "DRONE_MODE": "auto"
                }
            }
        }
    }
    
    # 設定ファイルを生成
    with open("claude_desktop_config.json", "w", encoding="utf-8") as f:
        json.dump(claude_desktop_config, f, indent=2, ensure_ascii=False)
    
    with open("vscode_settings.json", "w", encoding="utf-8") as f:
        json.dump(vscode_config, f, indent=2, ensure_ascii=False)
    
    print("✅ サンプル設定ファイルを生成しました:")
    print("   - claude_desktop_config.json (Claude Desktop用)")
    print("   - vscode_settings.json (VS Code用)")
    
    # 設定手順の表示
    print("\n📋 設定手順:")
    print("1. Claude Desktop:")
    print("   - 設定ファイルの場所を確認")
    print("   - claude_desktop_config.json の内容を設定ファイルに追加")
    print("   - Claude Desktop を再起動")
    
    print("\n2. VS Code:")
    print("   - .vscode/settings.json にvscode_settings.json の内容を追加")
    print("   - VS Code を再起動")

def main():
    """メイン関数"""
    print("🚁 MCP ドローン制御システム 設定検証ツール")
    print("=" * 50)
    
    # Python環境の確認
    if not validate_python_environment():
        print("\n❌ Python環境の確認に失敗しました")
        return 1
    
    # MCP設定の確認
    config = validate_mcp_config()
    if not config:
        print("\n⚠️ MCP設定ファイルの問題を検出しました")
        print("サンプル設定を生成します...")
        generate_sample_configs()
        return 1
    
    # MCPサーバーのテスト
    if not test_mcp_server():
        print("\n❌ MCPサーバーのテストに失敗しました")
        return 1
    
    print("\n✅ すべての確認が完了しました！")
    print("MCPサーバーは正常に動作します。")
    
    # 次のステップの提案
    print("\n📋 次のステップ:")
    print("1. 各MCPホストの設定ファイルを更新")
    print("2. MCPホストを再起動")
    print("3. ドローン制御コマンドをテスト")
    print("4. 詳細な使用方法は docs/setup.md を参照")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())