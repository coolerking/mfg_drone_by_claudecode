"""
Phase 1 Unit Tests: FastAPI Application
FastAPIアプリケーション関連の単体テスト
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app


class TestFastAPIApplication:
    """FastAPIアプリケーション単体テスト"""

    def test_app_instance_creation(self):
        """FastAPIアプリケーションインスタンスの作成テスト"""
        assert app is not None
        assert isinstance(app, FastAPI)
        assert app.title == "MFG Drone Backend API"
        assert app.description == "Tello EDU自動追従撮影システム バックエンドAPI"
        assert app.version == "1.0.0"

    def test_app_openapi_configuration(self):
        """OpenAPI設定テスト"""
        assert app.openapi_url == "/openapi.json"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_app_middleware_cors_configuration(self):
        """CORSミドルウェア設定テスト"""
        # CORSミドルウェアが設定されているかチェック
        cors_middleware_found = False
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware_found = True
                # オプション設定の確認
                options = middleware.options
                assert options["allow_origins"] == ["*"]
                assert options["allow_credentials"] is True
                assert options["allow_methods"] == ["*"]
                assert options["allow_headers"] == ["*"]
                break
        assert cors_middleware_found, "CORSMiddleware not found"

    def test_app_routers_registration(self):
        """ルーター登録確認テスト"""
        # 登録されたルートパスの確認
        routes = [route.path for route in app.routes]
        
        # 基本エンドポイント
        assert "/" in routes
        assert "/health" in routes
        
        # API ルーターのベースパスが含まれているか確認
        expected_base_paths = [
            "/connection",
            "/flight",
            "/movement", 
            "/camera",
            "/sensors",
            "/settings",
            "/tracking",
            "/model"
        ]
        
        # 各ベースパスに対応するルートが存在するかチェック
        for base_path in expected_base_paths:
            matching_routes = [route for route in routes if route.startswith(base_path)]
            assert len(matching_routes) > 0, f"No routes found for base path {base_path}"

    def test_app_route_count_boundary(self):
        """ルート数境界値テスト"""
        routes_count = len(app.routes)
        # 最小ルート数（基本エンドポイント + ルーター）
        assert routes_count >= 2, "Too few routes registered"
        # 最大ルート数（過度な登録の検出）
        assert routes_count <= 100, "Too many routes registered"

    def test_app_openapi_schema_generation(self):
        """OpenAPIスキーマ生成テスト"""
        openapi_schema = app.openapi()
        assert openapi_schema is not None
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert openapi_schema["info"]["title"] == "MFG Drone Backend API"
        assert openapi_schema["info"]["version"] == "1.0.0"

    def test_app_openapi_schema_boundary_values(self):
        """OpenAPIスキーマ境界値テスト"""
        openapi_schema = app.openapi()
        
        # パス数の境界値チェック
        paths = openapi_schema.get("paths", {})
        assert len(paths) >= 1, "No API paths defined"
        assert len(paths) <= 50, "Too many API paths defined"
        
        # コンポーネント数の境界値チェック
        components = openapi_schema.get("components", {})
        schemas = components.get("schemas", {})
        assert len(schemas) >= 1, "No schema components defined"


class TestRootEndpoint:
    """ルートエンドポイント単体テスト"""

    def test_root_endpoint_success(self):
        """ルートエンドポイント正常系テスト"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "MFG Drone Backend API"}

    def test_root_endpoint_response_structure(self):
        """ルートエンドポイントレスポンス構造テスト"""
        client = TestClient(app)
        response = client.get("/")
        json_data = response.json()
        assert isinstance(json_data, dict)
        assert "message" in json_data
        assert isinstance(json_data["message"], str)
        assert len(json_data["message"]) > 0

    def test_root_endpoint_headers(self):
        """ルートエンドポイントヘッダーテスト"""
        client = TestClient(app)
        response = client.get("/")
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"

    def test_root_endpoint_cors_headers(self):
        """ルートエンドポイントCORSヘッダーテスト"""
        client = TestClient(app)
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        # CORSミドルウェアによるヘッダー設定確認
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
    def test_root_endpoint_invalid_methods(self, method):
        """ルートエンドポイント無効メソッドテスト"""
        client = TestClient(app)
        response = client.request(method, "/")
        assert response.status_code == 405


class TestHealthEndpoint:
    """ヘルスチェックエンドポイント単体テスト"""

    def test_health_endpoint_success(self):
        """ヘルスチェックエンドポイント正常系テスト"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_endpoint_response_structure(self):
        """ヘルスチェックエンドポイントレスポンス構造テスト"""
        client = TestClient(app)
        response = client.get("/health")
        json_data = response.json()
        assert isinstance(json_data, dict)
        assert "status" in json_data
        assert isinstance(json_data["status"], str)
        assert json_data["status"] == "healthy"

    def test_health_endpoint_headers(self):
        """ヘルスチェックエンドポイントヘッダーテスト"""
        client = TestClient(app)
        response = client.get("/health")
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_cors_headers(self):
        """ヘルスチェックエンドポイントCORSヘッダーテスト"""
        client = TestClient(app)
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        # CORSミドルウェアによるヘッダー設定確認
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
    def test_health_endpoint_invalid_methods(self, method):
        """ヘルスチェックエンドポイント無効メソッドテスト"""
        client = TestClient(app)
        response = client.request(method, "/health")
        assert response.status_code == 405

    def test_health_endpoint_boundary_headers(self):
        """ヘルスチェックエンドポイント境界値ヘッダーテスト"""
        client = TestClient(app)
        
        # 最大長ヘッダー
        long_header_value = "a" * 8192
        response = client.get("/health", headers={"X-Custom": long_header_value})
        assert response.status_code == 200
        
        # 空ヘッダー
        response = client.get("/health", headers={"X-Empty": ""})
        assert response.status_code == 200


class TestApplicationErrorHandling:
    """アプリケーション例外処理テスト"""

    def test_invalid_endpoint_404(self):
        """無効エンドポイント404テスト"""
        client = TestClient(app)
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_endpoint_structure(self):
        """無効エンドポイント構造テスト"""
        client = TestClient(app)
        response = client.get("/invalid/path/structure")
        assert response.status_code == 404

    @pytest.mark.parametrize("invalid_path", [
        "/",  # root は存在するので除外
        "//",
        "///",
        "/path//double//slash",
        "/path%20with%20spaces",
        "/ドローン",  # Unicode文字
        "/path?query=invalid",
        "/path#fragment"
    ])
    def test_invalid_path_formats(self, invalid_path):
        """無効パス形式テスト"""
        client = TestClient(app)
        # root以外は404が期待される
        if invalid_path != "/":
            response = client.get(invalid_path)
            assert response.status_code in [404, 422]

    def test_malformed_request_handling(self):
        """不正形式リクエスト処理テスト"""
        client = TestClient(app)
        
        # 不正JSON
        response = client.post("/health", json="invalid json structure")
        assert response.status_code in [405, 422]  # healthはGETのみ
        
        # 空ボディでPOST
        response = client.post("/health", content="")
        assert response.status_code == 405  # healthはGETのみ

    def test_large_request_handling(self):
        """大きなリクエスト処理テスト"""
        client = TestClient(app)
        
        # 大きなクエリパラメータ
        large_query = "a" * 1000
        response = client.get(f"/health?large_param={large_query}")
        assert response.status_code == 200  # ヘルスチェックは影響なし


class TestApplicationBoundaryConditions:
    """アプリケーション境界条件テスト"""

    def test_concurrent_request_handling(self):
        """同時リクエスト処理テスト"""
        import concurrent.futures
        
        client = TestClient(app)
        
        def make_request():
            return client.get("/health")
        
        # 5つの同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        
        # 全てのリクエストが成功することを確認
        for response in responses:
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

    def test_request_timeout_boundary(self):
        """リクエストタイムアウト境界テスト"""
        client = TestClient(app)
        
        # 基本的なリクエストは高速で完了することを確認
        import time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # 1秒以内で完了

    @pytest.mark.parametrize("content_type", [
        "application/json",
        "text/plain",
        "application/xml",
        "application/octet-stream"
    ])
    def test_different_content_types(self, content_type):
        """異なるContent-Typeテスト"""
        client = TestClient(app)
        response = client.get("/health", headers={"Content-Type": content_type})
        assert response.status_code == 200

    def test_unicode_handling(self):
        """Unicode文字処理テスト"""
        client = TestClient(app)
        
        # Unicode文字を含むヘッダー
        response = client.get("/health", headers={"X-Unicode": "ドローン🚁"})
        assert response.status_code == 200
        
        # Unicode文字を含むクエリパラメータ
        response = client.get("/health?name=ドローン")
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """ミドルウェア統合テスト"""

    def test_cors_preflight_request(self):
        """CORS Preflightリクエストテスト"""
        client = TestClient(app)
        
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Preflightレスポンスの確認
        assert response.status_code in [200, 204]
        assert "access-control-allow-origin" in response.headers

    def test_cors_actual_request(self):
        """CORS実際のリクエストテスト"""
        client = TestClient(app)
        
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.parametrize("origin", [
        "http://localhost:3000",
        "https://example.com",
        "https://subdomain.example.com",
        "http://192.168.1.100:8080"
    ])
    def test_cors_different_origins(self, origin):
        """CORS異なるOriginテスト"""
        client = TestClient(app)
        response = client.get("/health", headers={"Origin": origin})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_middleware_order_and_execution(self):
        """ミドルウェア順序と実行テスト"""
        client = TestClient(app)
        
        # ミドルウェアが正しく実行されることを確認
        response = client.get("/health")
        assert response.status_code == 200
        
        # レスポンスヘッダーでミドルウェア実行を確認
        assert "content-type" in response.headers


class TestApplicationStartupShutdown:
    """アプリケーション起動・終了テスト"""

    def test_app_startup_event_handling(self):
        """アプリケーション起動イベント処理テスト"""
        # FastAPIアプリケーションが正常に起動できることを確認
        test_client = TestClient(app)
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_app_configuration_after_startup(self):
        """起動後設定確認テスト"""
        # 起動後にアプリケーション設定が正しいことを確認
        assert app.title == "MFG Drone Backend API"
        assert app.version == "1.0.0"
        
        # ルーターが正しく登録されていることを確認
        assert len(app.routes) > 0

    def test_app_state_consistency(self):
        """アプリケーション状態一貫性テスト"""
        # アプリケーション状態が一貫していることを確認
        client = TestClient(app)
        
        # 複数のリクエストで状態が維持されることを確認
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        assert response1.status_code == response2.status_code
        assert response1.json() == response2.json()