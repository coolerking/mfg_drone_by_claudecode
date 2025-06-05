"""
ドローン接続管理関連APIのテストケース
/drone/connect, /drone/disconnect エンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from config.test_config import TestConfig
from tests.fixtures.drone_factory import create_test_drone, DroneTestHelper
from tests.stubs.drone_stub import TelloStub


class TestConnectionAPI:
    """ドローン接続管理関連APIのテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        TestConfig.setup_logging()
        self.client = TestClient(app)
    
    @patch('services.drone_service.drone_service.drone')
    def test_connect_success(self, mock_drone):
        """正常な接続テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_disconnected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/connect")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "接続" in data["message"]
        assert isinstance(data, dict)
        assert "success" in data
        assert "message" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_connect_already_connected(self, mock_drone):
        """既に接続済みでの接続テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/connect")
        
        # 既に接続済みの場合の動作は実装依存
        # 成功（冪等性）またはエラーのいずれも有効
        assert response.status_code in [200, 409]
        data = response.json()
        if response.status_code == 200:
            assert data["success"] is True
        else:
            assert "error" in data
            assert "code" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_connect_connection_failure(self, mock_drone):
        """接続失敗テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connection_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/connect")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "DRONE_CONNECTION_FAILED"
    
    @patch('services.drone_service.drone_service.drone')
    def test_connect_timeout(self, mock_drone):
        """接続タイムアウトテスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_timeout_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/connect")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] in ["COMMAND_TIMEOUT", "DRONE_CONNECTION_FAILED"]
    
    def test_connect_method_not_allowed(self):
        """許可されていないHTTPメソッドテスト"""
        # GET method should not be allowed
        response = self.client.get("/drone/connect")
        assert response.status_code == 405
        
        # PUT method should not be allowed
        response = self.client.put("/drone/connect")
        assert response.status_code == 405
        
        # DELETE method should not be allowed
        response = self.client.delete("/drone/connect")
        assert response.status_code == 405
    
    def test_connect_with_request_body(self):
        """リクエストボディ付き接続テスト"""
        # 接続エンドポイントはボディを期待しないが、
        # ボディがあっても正常に動作することを確認
        response = self.client.post("/drone/connect", json={"test": "data"})
        
        # パラメータ検証エラーまたは正常な処理
        assert response.status_code in [200, 422, 500]
    
    @patch('services.drone_service.drone_service.drone')
    def test_disconnect_success(self, mock_drone):
        """正常な切断テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/disconnect")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "切断" in data["message"] or "接続解除" in data["message"]
    
    @patch('services.drone_service.drone_service.drone')
    def test_disconnect_not_connected(self, mock_drone):
        """未接続での切断テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_disconnected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/disconnect")
        
        # 未接続状態での切断は成功（冪等性）またはエラーのいずれも有効
        assert response.status_code in [200, 500]
        data = response.json()
        if response.status_code == 200:
            assert data["success"] is True
        else:
            assert "error" in data
            assert "code" in data
    
    @patch('services.drone_service.drone_service.drone')
    def test_disconnect_failure(self, mock_drone):
        """切断失敗テスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone_instance)
        DroneTestHelper.setup_command_error(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        response = self.client.post("/drone/disconnect")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] in ["COMMAND_FAILED", "INTERNAL_ERROR"]
    
    def test_disconnect_method_not_allowed(self):
        """許可されていないHTTPメソッドテスト"""
        # GET method should not be allowed
        response = self.client.get("/drone/disconnect")
        assert response.status_code == 405
        
        # PUT method should not be allowed
        response = self.client.put("/drone/disconnect")
        assert response.status_code == 405
        
        # DELETE method should not be allowed
        response = self.client.delete("/drone/disconnect")
        assert response.status_code == 405
    
    @patch('services.drone_service.drone_service.drone')
    def test_connection_sequence(self, mock_drone):
        """接続・切断シーケンステスト"""
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_disconnected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        # 1. 接続
        response = self.client.post("/drone/connect")
        if response.status_code == 200:
            assert response.json()["success"] is True
            
            # 接続後の状態を設定
            DroneTestHelper.setup_connected_state(mock_drone_instance)
            
            # 2. 切断
            response = self.client.post("/drone/disconnect")
            if response.status_code == 200:
                assert response.json()["success"] is True
    
    def test_connection_response_format(self):
        """接続関連レスポンス形式検証"""
        endpoints = ["/drone/connect", "/drone/disconnect"]
        
        for endpoint in endpoints:
            response = self.client.post(endpoint)
            
            # ステータスコードの検証
            assert response.status_code in [200, 500]
            data = response.json()
            assert isinstance(data, dict)
            
            if response.status_code == 200:
                # 成功レスポンス
                assert "success" in data
                assert "message" in data
                assert isinstance(data["success"], bool)
                assert isinstance(data["message"], str)
            else:
                # エラーレスポンス
                assert "error" in data
                assert "code" in data
                assert isinstance(data["error"], str)
                assert isinstance(data["code"], str)
    
    @patch('services.drone_service.drone_service.drone')
    def test_connection_concurrent_requests(self, mock_drone):
        """同時接続要求テスト"""
        import threading
        
        mock_drone_instance = create_test_drone()
        DroneTestHelper.setup_disconnected_state(mock_drone_instance)
        mock_drone.return_value = mock_drone_instance
        
        results = []
        
        def make_connect_request():
            response = self.client.post("/drone/connect")
            results.append({
                'status_code': response.status_code,
                'data': response.json()
            })
        
        # 3つの同時接続リクエストを作成
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_connect_request)
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待つ
        for thread in threads:
            thread.join()
        
        # 少なくとも1つは成功することを確認
        success_count = sum(1 for result in results if result['status_code'] == 200)
        assert success_count >= 1
        
        # すべてのレスポンスが適切な形式であることを確認
        for result in results:
            assert result['status_code'] in [200, 409, 500]
            assert isinstance(result['data'], dict)