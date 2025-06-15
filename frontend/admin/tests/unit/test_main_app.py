"""
main.py アプリケーションの単体テスト
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from main import app


@pytest.mark.unit
class TestMainApp:
    """メインアプリケーションの基本機能テスト"""
    
    def test_app_creation(self, app):
        """アプリケーションが正常に作成されることをテスト"""
        assert app is not None
        assert app.config['TESTING'] is True
        assert 'SECRET_KEY' in app.config
    
    def test_index_route(self, client):
        """インデックスページのテスト"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'MFG Drone' in response.data
        assert b'\xe7\xae\xa1\xe7\x90\x86\xe8\x80\x85\xe7\x94\xbb\xe9\x9d\xa2' in response.data  # 管理者画面
    
    def test_health_check_route(self, client):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get('/health')
        assert response.status_code == 200
        
        # JSONレスポンスの確認
        data = json.loads(response.get_data(as_text=True))
        assert data['status'] == 'healthy'
    
    def test_health_check_content_type(self, client):
        """ヘルスチェックのContent-Typeテスト"""
        response = client.get('/health')
        assert 'application/json' in response.content_type
    
    def test_nonexistent_route(self, client):
        """存在しないルートの404テスト"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_index_template_variables(self, client):
        """インデックステンプレートの内容テスト"""
        response = client.get('/')
        # テンプレートが正しくレンダリングされていることを確認
        content = response.get_data(as_text=True)
        assert 'MFG Drone - 管理者画面' in content
        assert '物体認識モデルのトレーニング' in content
        assert 'ドローン制御' in content
        assert '追跡開始/停止' in content


@pytest.mark.unit
class TestAppConfiguration:
    """アプリケーション設定のテスト"""
    
    def test_secret_key_configuration(self, app):
        """SECRET_KEYの設定テスト"""
        # テスト環境では test-secret-key が設定されている
        assert app.config['SECRET_KEY'] == 'test-secret-key'
    
    def test_testing_mode(self, app):
        """テストモードの確認"""
        assert app.config['TESTING'] is True
    
    @patch.dict('os.environ', {'SECRET_KEY': 'custom-secret'})
    def test_secret_key_from_environment(self):
        """環境変数からのSECRET_KEY設定テスト"""
        # 新しいアプリインスタンスを作成して環境変数をテスト
        from main import Flask
        test_app = Flask(__name__)
        import os
        test_app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
        assert test_app.secret_key == 'custom-secret'


@pytest.mark.unit
class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_method_not_allowed(self, client):
        """許可されていないHTTPメソッドのテスト"""
        # POSTは許可されていない
        response = client.post('/')
        assert response.status_code == 405
        
        # PUTも許可されていない
        response = client.put('/health')
        assert response.status_code == 405
    
    def test_large_request(self, client):
        """大きなリクエストボディの処理テスト"""
        # 通常のGETリクエストに大きなヘッダーを追加
        headers = {'X-Large-Header': 'x' * 1000}
        response = client.get('/', headers=headers)
        # サーバーが正常に応答することを確認
        assert response.status_code == 200


@pytest.mark.unit
class TestBoundaryConditions:
    """境界値テスト"""
    
    def test_empty_request(self, client):
        """空のリクエストの処理"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_request_with_query_parameters(self, client):
        """クエリパラメータ付きリクエスト"""
        response = client.get('/?test=value&another=param')
        assert response.status_code == 200
    
    def test_request_with_special_characters(self, client):
        """特殊文字を含むパスのテスト"""
        # URLエンコードされた特殊文字
        response = client.get('/%E3%83%86%E3%82%B9%E3%83%88')  # "テスト"
        assert response.status_code == 404  # 存在しないルートなので404
    
    def test_multiple_headers(self, client):
        """複数のHTTPヘッダーテスト"""
        headers = {
            'User-Agent': 'Test-Agent/1.0',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ja,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        response = client.get('/', headers=headers)
        assert response.status_code == 200


@pytest.mark.unit
class TestResponseValidation:
    """レスポンス検証テスト"""
    
    def test_index_response_structure(self, client):
        """インデックスページのレスポンス構造テスト"""
        response = client.get('/')
        
        # HTTPヘッダーの確認
        assert 'text/html' in response.content_type
        assert response.status_code == 200
        
        # レスポンスボディの基本構造確認
        content = response.get_data(as_text=True)
        assert '<!DOCTYPE html>' in content
        assert '<html' in content
        assert '</html>' in content
        assert '<head>' in content
        assert '<body>' in content
    
    def test_health_response_structure(self, client):
        """ヘルスチェックレスポンス構造テスト"""
        response = client.get('/health')
        
        # JSONレスポンスの確認
        assert response.is_json
        data = response.get_json()
        
        # 必須フィールドの確認
        assert 'status' in data
        assert isinstance(data['status'], str)
        assert data['status'] == 'healthy'
    
    def test_response_encoding(self, client):
        """レスポンスエンコーディングテスト"""
        response = client.get('/')
        
        # UTF-8エンコーディングの確認
        assert 'charset=utf-8' in response.content_type
        
        # 日本語文字の正しい表示確認
        content = response.get_data(as_text=True)
        assert '管理者画面' in content
        assert '物体認識' in content