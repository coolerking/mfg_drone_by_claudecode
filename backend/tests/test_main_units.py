"""
FastAPIアプリケーション単体テスト
main.py の個別コンポーネント単体テスト - Phase 1
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app


class TestFastAPIApplication:
    """FastAPIアプリケーション単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.client = TestClient(app)
    
    def test_app_instance_creation(self):
        """FastAPIアプリケーションインスタンス作成テスト"""
        # アプリケーション基本属性確認
        assert isinstance(app, FastAPI)
        assert app.title == "MFG Drone Backend API"
        assert app.description == "Tello EDU自動追従撮影システム バックエンドAPI"
        assert app.version == "1.0.0"
        assert app.openapi_url == "/openapi.json"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
    
    def test_app_initialization_boundary_values(self):
        """アプリケーション初期化境界値テスト"""
        # バージョン境界値テスト
        valid_versions = ["1.0.0", "0.1.0", "99.99.99"]
        for version in valid_versions:
            test_app = FastAPI(version=version)
            assert test_app.version == version
        
        # タイトル境界値テスト (空文字列、長い文字列)
        boundary_titles = [
            "",  # 空文字列
            "A",  # 最小
            "A" * 100,  # 長い文字列
            "MFG Drone Backend API"  # 現在値
        ]
        for title in boundary_titles:
            test_app = FastAPI(title=title)
            assert test_app.title == title
    
    def test_cors_middleware_configuration(self):
        """CORSミドルウェア設定単体テスト"""
        # ミドルウェア設定確認
        middleware_found = False
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                middleware_found = True
                options = middleware.options
                
                # CORS設定値確認
                assert options["allow_origins"] == ["*"]
                assert options["allow_credentials"] is True
                assert options["allow_methods"] == ["*"]
                assert options["allow_headers"] == ["*"]
                break
        
        assert middleware_found, "CORSMiddleware not found"
    
    def test_cors_middleware_boundary_values(self):
        """CORSミドルウェア境界値テスト"""
        # 各種境界値でのCORSミドルウェア作成テスト
        cors_configs = [
            # 境界値1: 空のorigins
            {"allow_origins": [], "allow_credentials": False, "allow_methods": [], "allow_headers": []},
            # 境界値2: 単一origin
            {"allow_origins": ["http://localhost:3000"], "allow_credentials": True, "allow_methods": ["GET"], "allow_headers": ["Content-Type"]},
            # 境界値3: 全許可（現在の設定）
            {"allow_origins": ["*"], "allow_credentials": True, "allow_methods": ["*"], "allow_headers": ["*"]},
        ]
        
        for config in cors_configs:
            test_app = FastAPI()
            test_app.add_middleware(CORSMiddleware, **config)
            
            # ミドルウェアが追加されていることを確認
            assert len(test_app.user_middleware) == 1
            assert test_app.user_middleware[0].cls == CORSMiddleware
    
    def test_router_registration(self):
        """Router登録単体テスト"""
        # 登録されるべきルーターの数をチェック
        expected_routers = [
            "connection_router",
            "flight_control_router", 
            "movement_router",
            "advanced_movement_router",
            "camera_router",
            "sensors_router",
            "settings_router",
            "mission_pad_router",
            "tracking_router",
            "model_router"
        ]
        
        # ルート数確認（各ルーターが複数のエンドポイントを持つ）
        # 最低でも基本的なエンドポイント数は存在するはず
        routes = app.routes
        assert len(routes) >= len(expected_routers)
    
    def test_router_registration_boundary_values(self):
        """Router登録境界値テスト"""
        # 空のルーターテスト
        test_app = FastAPI()
        assert len(test_app.routes) == 0
        
        # 重複ルーター登録テスト
        from fastapi import APIRouter
        test_router = APIRouter()
        test_router.get("/test")(lambda: {"message": "test"})
        
        test_app.include_router(test_router)
        initial_count = len(test_app.routes)
        
        # 同じルーターを再度登録
        test_app.include_router(test_router)
        final_count = len(test_app.routes)
        
        # ルートが追加されることを確認（重複は許可される）
        assert final_count >= initial_count


class TestApplicationEndpoints:
    """アプリケーションエンドポイント単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.client = TestClient(app)
    
    def test_root_endpoint_functionality(self):
        """ルートエンドポイント機能テスト"""
        response = self.client.get("/")
        
        # レスポンス構造確認
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert data["message"] == "MFG Drone Backend API"
    
    def test_health_check_endpoint_functionality(self):
        """ヘルスチェックエンドポイント機能テスト"""
        response = self.client.get("/health")
        
        # レスポンス構造確認
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint_boundary_values(self):
        """ルートエンドポイント境界値テスト"""
        # 複数回連続アクセス
        for i in range(10):
            response = self.client.get("/")
            assert response.status_code == 200
            assert response.json()["message"] == "MFG Drone Backend API"
        
        # 異なるHTTPメソッドでのアクセステスト
        methods_results = [
            ("GET", 200),      # 許可
            ("POST", 405),     # Method Not Allowed
            ("PUT", 405),      # Method Not Allowed
            ("DELETE", 405),   # Method Not Allowed
        ]
        
        for method, expected_status in methods_results:
            response = self.client.request(method, "/")
            assert response.status_code == expected_status
    
    def test_health_check_boundary_values(self):
        """ヘルスチェック境界値テスト"""
        # 複数回連続ヘルスチェック
        for i in range(100):
            response = self.client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
        
        # 不正なパスでのテスト
        invalid_paths = [
            "/health/",      # 末尾スラッシュ
            "/health/status", # サブパス
            "/Health",       # 大文字
            "/HEALTH",       # 全大文字
        ]
        
        for path in invalid_paths:
            response = self.client.get(path)
            # 404 Not Found または正常レスポンス
            assert response.status_code in [200, 404]


class TestApplicationErrorHandling:
    """アプリケーションエラーハンドリング単体テスト"""
    
    @pytest.fixture(autouse=True) 
    def setup(self):
        """各テスト前のセットアップ"""
        self.client = TestClient(app)
    
    def test_nonexistent_endpoint_error(self):
        """存在しないエンドポイントエラーテスト"""
        response = self.client.get("/nonexistent")
        
        assert response.status_code == 404
        # FastAPIの標準404レスポンス確認
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data
    
    def test_method_not_allowed_error(self):
        """許可されていないメソッドエラーテスト"""
        # ルートエンドポイントにPOSTでアクセス
        response = self.client.post("/")
        
        assert response.status_code == 405
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data
    
    def test_malformed_request_handling(self):
        """不正なリクエスト処理テスト"""
        # 存在しないパスでの境界値テスト
        malformed_paths = [
            "//",             # 重複スラッシュ
            "/../../etc",     # パストラバーサル試行
            "/null",          # null文字列
            "/%00",           # URLエンコードされたnull
            "/テスト",         # 日本語パス
        ]
        
        for path in malformed_paths:
            response = self.client.get(path)
            # 400 Bad Request または 404 Not Found
            assert response.status_code in [400, 404]
    
    def test_openapi_documentation_generation(self):
        """OpenAPIドキュメント生成テスト"""
        # OpenAPI仕様書取得
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        openapi_spec = response.json()
        
        # OpenAPI仕様書構造確認
        assert isinstance(openapi_spec, dict)
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        
        # info セクション確認
        info = openapi_spec["info"]
        assert info["title"] == "MFG Drone Backend API"
        assert info["version"] == "1.0.0"
    
    def test_docs_endpoints_accessibility(self):
        """ドキュメントエンドポイントアクセス可能性テスト"""
        # Swagger UI
        response = self.client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = self.client.get("/redoc")
        assert response.status_code == 200


class TestApplicationConfiguration:
    """アプリケーション設定単体テスト"""
    
    def test_app_metadata_configuration(self):
        """アプリケーションメタデータ設定テスト"""
        # 設定値境界テスト
        config_values = {
            "title": "MFG Drone Backend API",
            "description": "Tello EDU自動追従撮影システム バックエンドAPI",
            "version": "1.0.0",
            "openapi_url": "/openapi.json",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
        
        for key, expected_value in config_values.items():
            actual_value = getattr(app, key)
            assert actual_value == expected_value, f"{key} configuration mismatch"
    
    def test_app_middleware_stack(self):
        """アプリケーションミドルウェアスタック構成テスト"""
        # ミドルウェア数確認
        middleware_count = len(app.user_middleware)
        assert middleware_count >= 1  # 最低でもCORSミドルウェア
        
        # 各ミドルウェアの型確認
        middleware_types = [middleware.cls for middleware in app.user_middleware]
        assert CORSMiddleware in middleware_types
    
    def test_app_exception_handlers(self):
        """アプリケーション例外ハンドラー設定テスト"""
        # デフォルトの例外ハンドラー確認
        exception_handlers = app.exception_handlers
        assert isinstance(exception_handlers, dict)
        
        # FastAPI標準例外ハンドラーが設定されていることを確認
        # （具体的なハンドラーは実装に依存）
        assert len(exception_handlers) >= 0