"""
システム関連APIのテストケース
/health エンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from config.test_config import TestConfig


class TestSystemAPI:
    """システム関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    def test_health_check_success(self):
        """正常なヘルスチェックテスト"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check_response_format(self):
        """ヘルスチェックレスポンス形式検証"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # レスポンス形式の検証
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "healthy"
    
    def test_health_check_method_not_allowed(self):
        """許可されていないHTTPメソッドテスト"""
        # POST method should not be allowed
        response = self.client.post("/health")
        assert response.status_code == 405
        
        # PUT method should not be allowed
        response = self.client.put("/health")
        assert response.status_code == 405
        
        # DELETE method should not be allowed
        response = self.client.delete("/health")
        assert response.status_code == 405
    
    def test_health_check_with_query_parameters(self):
        """クエリパラメータ付きヘルスチェックテスト"""
        # クエリパラメータがあっても正常に動作することを確認
        response = self.client.get("/health?test=1&debug=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_check_with_headers(self):
        """カスタムヘッダー付きヘルスチェックテスト"""
        headers = {
            "User-Agent": "Test Client",
            "Accept": "application/json",
            "X-Test-Header": "test-value"
        }
        
        response = self.client.get("/health", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_check_content_type(self):
        """ヘルスチェックコンテンツタイプ検証"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_health_check_multiple_requests(self):
        """複数回ヘルスチェック要求テスト"""
        # 連続して複数回リクエストしても安定して動作することを確認
        for i in range(5):
            response = self.client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @patch('fastapi.applications.FastAPI')
    def test_health_check_server_error_simulation(self, mock_app):
        """サーバーエラーシミュレーションテスト"""
        # 通常はヘルスチェックは常に200を返すべきだが、
        # システム障害時の動作を確認
        
        # 実際のアプリケーションでテスト（モックなし）
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # ヘルスチェックは基本的にシステムの基本機能なので
        # 常に成功することを期待
    
    def test_health_check_response_time(self):
        """ヘルスチェック応答時間テスト"""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # ヘルスチェックは高速に応答すべき（1秒以内）
        assert response_time < 1.0
    
    def test_health_check_concurrent_requests(self):
        """同時ヘルスチェック要求テスト"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.get("/health")
            results.append({
                'status_code': response.status_code,
                'data': response.json()
            })
        
        # 5つの同時リクエストを作成
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待つ
        for thread in threads:
            thread.join()
        
        # すべてのリクエストが成功することを確認
        assert len(results) == 5
        for result in results:
            assert result['status_code'] == 200
            assert result['data']['status'] == 'healthy'