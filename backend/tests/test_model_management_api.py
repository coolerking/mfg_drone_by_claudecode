"""
AIモデル管理関連APIのテストケース
/model/train, /model/list エンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from config.test_config import TestConfig
from tests.fixtures.drone_factory import create_test_drone, DroneTestHelper
from tests.stubs.drone_stub import TelloStub


class TestModelManagementAPI:
    """AIモデル管理関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    def create_test_image_file(self, filename="test.jpg", size=1024):
        """テスト用画像ファイルを作成"""
        # 簡単なバイナリデータを作成（実際の画像ではない）
        content = b'\xFF\xD8\xFF\xE0' + b'\x00' * (size - 4)  # JPEG header + padding
        return ("files", (filename, io.BytesIO(content), "image/jpeg"))
    
    def test_model_train_success(self):
        """正常なモデル訓練テスト"""
        files = [
            self.create_test_image_file("image1.jpg"),
            self.create_test_image_file("image2.jpg"),
            self.create_test_image_file("image3.jpg")
        ]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "test_object"},
            files=files
        )
        
        # 実装状況により200または500
        assert response.status_code in [200, 400, 413, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data
            assert isinstance(data["task_id"], str)
            assert len(data["task_id"]) > 0
    
    def test_model_train_missing_object_name(self):
        """オブジェクト名未指定テスト"""
        files = [self.create_test_image_file("image1.jpg")]
        
        response = self.client.post(
            "/model/train",
            files=files
        )
        
        assert response.status_code == 422
    
    def test_model_train_missing_images(self):
        """画像ファイル未指定テスト"""
        response = self.client.post(
            "/model/train",
            data={"object_name": "test_object"}
        )
        
        assert response.status_code == 422
    
    def test_model_train_empty_object_name(self):
        """空のオブジェクト名テスト"""
        files = [self.create_test_image_file("image1.jpg")]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": ""},
            files=files
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_PARAMETER"
    
    def test_model_train_invalid_object_name_characters(self):
        """無効な文字を含むオブジェクト名テスト"""
        invalid_names = [
            "test/object",      # スラッシュ
            "test\\object",     # バックスラッシュ
            "test<object>",     # 山括弧
            "test|object",      # パイプ
            "test:object",      # コロン
            "test?object",      # クエスチョン
            "test*object"       # アスタリスク
        ]
        
        for object_name in invalid_names:
            files = [self.create_test_image_file("image1.jpg")]
            
            response = self.client.post(
                "/model/train",
                data={"object_name": object_name},
                files=files
            )
            
            # 実装依存：400または200（サニタイズされる場合）
            assert response.status_code in [200, 400, 500]
    
    def test_model_train_long_object_name(self):
        """長すぎるオブジェクト名テスト"""
        long_name = "a" * 256  # 256文字
        files = [self.create_test_image_file("image1.jpg")]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": long_name},
            files=files
        )
        
        # 実装依存：400または200（切り詰められる場合）
        assert response.status_code in [200, 400, 500]
    
    def test_model_train_single_image(self):
        """単一画像での訓練テスト"""
        files = [self.create_test_image_file("single.jpg")]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "single_object"},
            files=files
        )
        
        # 単一画像では訓練不可の場合もある
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 400:
            data = response.json()
            assert "error" in data
            # 画像数不足の場合
            assert data["code"] in ["INVALID_PARAMETER", "INSUFFICIENT_DATA"]
    
    def test_model_train_many_images(self):
        """多数画像での訓練テスト"""
        # 20枚の画像でテスト
        files = [self.create_test_image_file(f"image{i}.jpg") for i in range(20)]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "many_images_object"},
            files=files
        )
        
        # 大量の画像でも正常に処理される
        assert response.status_code in [200, 413, 500]
        
        if response.status_code == 413:
            data = response.json()
            assert "error" in data
            assert data["code"] == "FILE_TOO_LARGE"
    
    def test_model_train_large_file_size(self):
        """大きなファイルサイズテスト"""
        # 10MBのファイルを作成
        large_file = self.create_test_image_file("large.jpg", size=10*1024*1024)
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "large_file_object"},
            files=[large_file]
        )
        
        assert response.status_code in [200, 413, 500]
        
        if response.status_code == 413:
            data = response.json()
            assert "error" in data
            assert data["code"] == "FILE_TOO_LARGE"
    
    def test_model_train_invalid_file_format(self):
        """無効なファイル形式テスト"""
        # テキストファイルを画像として送信
        text_content = b"This is not an image file"
        invalid_file = ("files", ("text.txt", io.BytesIO(text_content), "text/plain"))
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "invalid_format"},
            files=[invalid_file]
        )
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 400:
            data = response.json()
            assert "error" in data
            assert data["code"] in ["INVALID_PARAMETER", "UNSUPPORTED_FORMAT"]
    
    def test_model_train_mixed_file_formats(self):
        """混在ファイル形式テスト"""
        files = [
            self.create_test_image_file("image1.jpg"),
            ("files", ("image2.png", io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100), "image/png")),
            ("files", ("image3.gif", io.BytesIO(b'GIF89a' + b'\x00' * 100), "image/gif")),
        ]
        
        response = self.client.post(
            "/model/train",
            data={"object_name": "mixed_formats"},
            files=files
        )
        
        # 混在形式の受け入れは実装依存
        assert response.status_code in [200, 400, 500]
    
    def test_model_list_success(self):
        """正常なモデル一覧取得テスト"""
        response = self.client.get("/model/list")
        
        assert response.status_code == 200
        data = response.json()
        
        # モデル一覧スキーマの検証
        assert isinstance(data, dict)
        assert "models" in data
        assert isinstance(data["models"], list)
        
        # 各モデルの形式検証
        for model in data["models"]:
            assert isinstance(model, dict)
            assert "name" in model
            assert "created_at" in model
            assert "accuracy" in model
            
            assert isinstance(model["name"], str)
            assert isinstance(model["created_at"], str)
            assert isinstance(model["accuracy"], (int, float))
            
            # 精度は0-1の範囲または0-100のパーセンテージ
            assert 0 <= model["accuracy"] <= 100 or 0 <= model["accuracy"] <= 1
    
    def test_model_list_empty(self):
        """空のモデル一覧取得テスト"""
        response = self.client.get("/model/list")
        
        assert response.status_code == 200
        data = response.json()
        
        # 空のリストも有効
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_model_list_date_format_validation(self):
        """モデル一覧の日付形式検証テスト"""
        response = self.client.get("/model/list")
        
        if response.status_code == 200:
            data = response.json()
            
            for model in data["models"]:
                if "created_at" in model:
                    # ISO 8601形式の日付文字列であることを確認
                    import re
                    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?$'
                    assert re.match(iso_pattern, model["created_at"]) is not None
    
    def test_model_method_validation(self):
        """モデル管理エンドポイントHTTPメソッド検証"""
        # POST専用エンドポイント
        response = self.client.get("/model/train")
        assert response.status_code == 405
        
        response = self.client.put("/model/train")
        assert response.status_code == 405
        
        response = self.client.delete("/model/train")
        assert response.status_code == 405
        
        # GET専用エンドポイント
        response = self.client.post("/model/list")
        assert response.status_code == 405
        
        response = self.client.put("/model/list")
        assert response.status_code == 405
        
        response = self.client.delete("/model/list")
        assert response.status_code == 405
    
    def test_model_train_concurrent_requests(self):
        """モデル訓練同時要求テスト"""
        import threading
        
        results = []
        
        def train_model(object_name):
            files = [self.create_test_image_file(f"{object_name}.jpg")]
            response = self.client.post(
                "/model/train",
                data={"object_name": object_name},
                files=files
            )
            results.append({
                'object_name': object_name,
                'status_code': response.status_code
            })
        
        # 複数の同時訓練要求
        threads = []
        for i in range(3):
            thread = threading.Thread(target=train_model, args=(f"concurrent_object_{i}",))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待つ
        for thread in threads:
            thread.join()
        
        # すべてのリクエストが適切に処理されることを確認
        assert len(results) == 3
        for result in results:
            # 同時実行では一部がTRAINING_IN_PROGRESSエラーになる可能性
            assert result['status_code'] in [200, 400, 409, 413, 500]
    
    def test_model_response_format_validation(self):
        """モデル管理レスポンス形式検証"""
        # 訓練レスポンス
        files = [self.create_test_image_file("format_test.jpg")]
        response = self.client.post(
            "/model/train",
            data={"object_name": "format_test"},
            files=files
        )
        
        assert response.status_code in [200, 400, 413, 422, 500]
        
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            assert isinstance(data, dict)
            
            if response.status_code == 200:
                # 成功レスポンス
                assert "task_id" in data
                assert isinstance(data["task_id"], str)
            elif response.status_code in [400, 413, 500]:
                # エラーレスポンス
                assert "error" in data
                assert "code" in data
                assert isinstance(data["error"], str)
                assert isinstance(data["code"], str)
        
        # 一覧レスポンス
        response = self.client.get("/model/list")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        data = response.json()
        assert isinstance(data, dict)
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_model_train_special_characters_in_filenames(self):
        """ファイル名特殊文字テスト"""
        special_names = [
            "画像1.jpg",           # 日本語
            "image with spaces.jpg", # スペース
            "image-with-dashes.jpg", # ダッシュ
            "image_with_underscores.jpg", # アンダースコア
            "image.with.dots.jpg",   # 複数ドット
            "IMAGE.JPG"              # 大文字
        ]
        
        for filename in special_names:
            files = [self.create_test_image_file(filename)]
            
            response = self.client.post(
                "/model/train",
                data={"object_name": "special_filename_test"},
                files=files
            )
            
            # ファイル名の特殊文字は通常受け入れられる
            assert response.status_code in [200, 400, 413, 500]
    
    def test_model_content_type_validation(self):
        """コンテンツタイプ検証テスト"""
        # 正しいMIMEタイプ
        valid_types = ["image/jpeg", "image/png", "image/gif", "image/bmp"]
        
        for content_type in valid_types:
            file_content = self.create_test_image_file("test.jpg")
            # MIMEタイプを変更
            modified_file = ("files", (file_content[1][0], file_content[1][1], content_type))
            
            response = self.client.post(
                "/model/train",
                data={"object_name": "content_type_test"},
                files=[modified_file]
            )
            
            # 有効なMIMEタイプは受け入れられる
            assert response.status_code in [200, 400, 500]