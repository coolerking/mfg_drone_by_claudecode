"""
テスト共通設定・フィクスチャ
"""

import pytest
import os
import tempfile
from flask import Flask
from main import app as flask_app


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション"""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })
    
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テスト用CLIランナー"""
    return app.test_cli_runner()


@pytest.fixture
def temp_dir():
    """一時ディレクトリ"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_image_data():
    """テスト用画像データ"""
    # 1x1 ピクセルのPNG画像データ（base64エンコード済み）
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def mock_backend_response():
    """バックエンドAPIのモックレスポンス"""
    return {
        "status": "success",
        "message": "Operation completed successfully",
        "data": {}
    }


@pytest.fixture
def mock_drone_data():
    """ドローンの模擬データ"""
    return {
        "battery": 85,
        "height": 120,
        "temperature": 25,
        "connected": True,
        "flying": False
    }


@pytest.fixture
def mock_tracking_data():
    """追跡機能の模擬データ"""
    return {
        "tracking_active": False,
        "target_object": None,
        "detection_confidence": 0.0,
        "target_position": {"x": 0, "y": 0}
    }


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """テスト後の一時ファイル清理"""
    yield
    # テスト後のクリーンアップ処理
    import glob
    for pattern in ["*.tmp", "test_*.log", "*.pyc"]:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
            except OSError:
                pass


# テスト実行時の環境変数設定
@pytest.fixture(autouse=True)
def set_test_environment():
    """テスト環境の環境変数設定"""
    os.environ["TESTING"] = "true"
    os.environ["BACKEND_URL"] = "http://localhost:8000"
    yield
    # テスト後の環境変数クリーンアップ
    for key in ["TESTING", "BACKEND_URL"]:
        os.environ.pop(key, None)