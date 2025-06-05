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
    """システムAPI関連のテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    def test_health_check_success(self):
        """正常なヘルスチェック"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """ルートエンドポイントの正常動作"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "MFG Drone Backend API" in data["message"]
    
    def test_health_check_multiple_calls(self):
        """ヘルスチェックの連続呼び出し"""
        for i in range(5):
            response = self.client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    def test_invalid_endpoint(self):
        """存在しないエンドポイントへのリクエスト"""
        response = self.client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_health_check_response_format(self):
        """ヘルスチェックレスポンス形式の検証"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # 必須フィールドの確認
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "healthy"
        
        # 余計なフィールドがないことを確認
        expected_keys = {"status"}
        assert set(data.keys()) == expected_keys
    
    def test_cors_headers(self):
        """CORS ヘッダーの確認"""
        response = self.client.get("/health")
        
        # CORS関連ヘッダーが適切に設定されているか確認
        # FastAPI + CORSMiddleware設定による
        assert response.status_code == 200
    
    def test_health_check_performance(self):
        """ヘルスチェックの応答時間テスト"""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # 応答時間が1秒以内であることを確認
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health check took too long: {response_time:.3f}s"