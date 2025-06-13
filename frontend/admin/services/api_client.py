"""
Backend API Client
バックエンドAPIとの通信を担当するクライアントサービス
"""

import requests
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from werkzeug.datastructures import FileStorage
import json


class BackendAPIClient:
    """バックエンドAPIクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MFG-Drone-Admin/1.0'
        })

    def health_check(self) -> Dict[str, Any]:
        """バックエンドAPIの健全性チェック"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"success": True, "status": "healthy"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def train_model(self, object_name: str, images: List[FileStorage]) -> Dict[str, Any]:
        """
        モデル訓練開始
        
        Args:
            object_name: 学習対象オブジェクト名
            images: 学習用画像ファイルリスト
        
        Returns:
            訓練結果（task_idを含む）
        """
        try:
            # マルチパートフォームデータの準備
            files = []
            for i, image in enumerate(images):
                # ファイルポインタを先頭に戻す
                image.seek(0)
                files.append(('images', (image.filename, image.read(), image.content_type)))
            
            data = {
                'object_name': object_name
            }
            
            response = self.session.post(
                f"{self.base_url}/model/train",
                data=data,
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "task_id": result.get("task_id"),
                    "message": "モデル訓練を開始しました"
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("detail", {}).get("error", "不明なエラー"),
                    "code": error_data.get("detail", {}).get("code", "UNKNOWN_ERROR")
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "タイムアウト: バックエンドAPIが応答しません",
                "code": "TIMEOUT"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "接続エラー: バックエンドAPIに接続できません",
                "code": "CONNECTION_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"予期しないエラー: {str(e)}",
                "code": "UNEXPECTED_ERROR"
            }

    def list_models(self) -> Dict[str, Any]:
        """
        訓練済みモデル一覧取得
        
        Returns:
            モデル一覧
        """
        try:
            response = self.session.get(f"{self.base_url}/model/list", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "models": result.get("models", [])
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("detail", {}).get("error", "不明なエラー"),
                    "code": error_data.get("detail", {}).get("code", "UNKNOWN_ERROR")
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "タイムアウト: バックエンドAPIが応答しません",
                "code": "TIMEOUT"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "接続エラー: バックエンドAPIに接続できません",
                "code": "CONNECTION_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"予期しないエラー: {str(e)}",
                "code": "UNEXPECTED_ERROR"
            }

    def validate_image_files(self, images: List[FileStorage]) -> Dict[str, Any]:
        """
        画像ファイルのバリデーション
        
        Args:
            images: 検証する画像ファイルリスト
        
        Returns:
            バリデーション結果
        """
        errors = []
        
        # 最小枚数チェック
        if len(images) < 5:
            errors.append(f"最低5枚の画像が必要です（現在: {len(images)}枚）")
        
        # 各ファイルのチェック
        valid_types = {'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'}
        max_size = 10 * 1024 * 1024  # 10MB
        
        for i, image in enumerate(images):
            # ファイル名チェック
            if not image.filename:
                errors.append(f"ファイル{i+1}: ファイル名が無効です")
                continue
                
            # ファイルサイズチェック（可能な場合）
            image.seek(0, 2)  # ファイル終端に移動
            file_size = image.tell()
            image.seek(0)  # 先頭に戻す
            
            if file_size > max_size:
                errors.append(f"ファイル{i+1} ({image.filename}): ファイルサイズが大きすぎます (最大10MB)")
            
            # MIMEタイプチェック
            if image.content_type not in valid_types:
                errors.append(f"ファイル{i+1} ({image.filename}): サポートされていないファイル形式です")
        
        if errors:
            return {
                "valid": False,
                "errors": errors
            }
        else:
            return {
                "valid": True,
                "message": f"{len(images)}枚の画像ファイルが有効です"
            }


# グローバルインスタンス
api_client = BackendAPIClient()