"""
ユーティリティ関数・フォームバリデーションの単体テスト
"""

import pytest
import os
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import requests


@pytest.mark.unit
class TestFileValidation:
    """ファイルバリデーション関数のテスト"""
    
    def test_valid_image_file_extensions(self):
        """有効な画像ファイル拡張子のテスト"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        for ext in valid_extensions:
            filename = f"test_image{ext}"
            assert self._is_valid_image_file(filename) is True
            
            # 大文字小文字を区別しない
            filename_upper = f"test_image{ext.upper()}"
            assert self._is_valid_image_file(filename_upper) is True
    
    def test_invalid_image_file_extensions(self):
        """無効な画像ファイル拡張子のテスト"""
        invalid_extensions = ['.txt', '.pdf', '.doc', '.exe', '.mp4']
        
        for ext in invalid_extensions:
            filename = f"test_file{ext}"
            assert self._is_valid_image_file(filename) is False
    
    def test_file_size_validation(self):
        """ファイルサイズバリデーションのテスト"""
        # 10MB以下は有効
        assert self._is_valid_file_size(5 * 1024 * 1024) is True  # 5MB
        assert self._is_valid_file_size(10 * 1024 * 1024) is True  # 10MB
        
        # 10MBを超えると無効
        assert self._is_valid_file_size(15 * 1024 * 1024) is False  # 15MB
        assert self._is_valid_file_size(50 * 1024 * 1024) is False  # 50MB
    
    def test_minimum_image_count_validation(self):
        """最低画像枚数バリデーションのテスト"""
        # 5枚以上は有効
        assert self._is_valid_image_count(5) is True
        assert self._is_valid_image_count(10) is True
        assert self._is_valid_image_count(100) is True
        
        # 5枚未満は無効
        assert self._is_valid_image_count(0) is False
        assert self._is_valid_image_count(1) is False
        assert self._is_valid_image_count(4) is False
    
    @staticmethod
    def _is_valid_image_file(filename):
        """画像ファイル拡張子チェック（サンプル実装）"""
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        _, ext = os.path.splitext(filename.lower())
        return ext in valid_extensions
    
    @staticmethod
    def _is_valid_file_size(size_bytes):
        """ファイルサイズチェック（サンプル実装）"""
        max_size = 10 * 1024 * 1024  # 10MB
        return size_bytes <= max_size
    
    @staticmethod
    def _is_valid_image_count(count):
        """画像枚数チェック（サンプル実装）"""
        return count >= 5


@pytest.mark.unit
class TestFormValidation:
    """フォームバリデーション関数のテスト"""
    
    def test_object_name_validation(self):
        """オブジェクト名バリデーションのテスト"""
        # 有効な名前
        valid_names = ["person", "car", "ball", "object_123", "test-object"]
        for name in valid_names:
            assert self._validate_object_name(name) is True
        
        # 無効な名前
        invalid_names = ["", "a", "very_long_name_that_exceeds_maximum_length", "object with spaces", "オブジェクト"]
        for name in invalid_names:
            assert self._validate_object_name(name) is False
    
    def test_tracking_mode_validation(self):
        """追跡モードバリデーションのテスト"""
        # 有効なモード
        valid_modes = ["center", "follow"]
        for mode in valid_modes:
            assert self._validate_tracking_mode(mode) is True
        
        # 無効なモード
        invalid_modes = ["", "invalid", "CENTER", "track", None]
        for mode in invalid_modes:
            assert self._validate_tracking_mode(mode) is False
    
    def test_movement_parameters_validation(self):
        """移動パラメータバリデーションのテスト"""
        # 有効なパラメータ
        valid_params = [
            {"direction": "forward", "distance": 20},
            {"direction": "up", "distance": 50},
            {"direction": "left", "distance": 100}
        ]
        for params in valid_params:
            assert self._validate_movement_params(params) is True
        
        # 無効なパラメータ
        invalid_params = [
            {"direction": "invalid", "distance": 20},
            {"direction": "forward", "distance": -10},
            {"direction": "forward", "distance": 0},
            {"direction": "forward", "distance": 600},
            {"distance": 20},  # direction missing
            {"direction": "forward"}  # distance missing
        ]
        for params in invalid_params:
            assert self._validate_movement_params(params) is False
    
    def test_camera_settings_validation(self):
        """カメラ設定バリデーションのテスト"""
        # 有効な設定
        valid_settings = [
            {"resolution": "high", "framerate": "middle", "bitrate": 3},
            {"resolution": "low", "framerate": "high", "bitrate": 1},
            {"resolution": "high", "framerate": "low", "bitrate": 5}
        ]
        for settings in valid_settings:
            assert self._validate_camera_settings(settings) is True
        
        # 無効な設定
        invalid_settings = [
            {"resolution": "invalid", "framerate": "middle", "bitrate": 3},
            {"resolution": "high", "framerate": "invalid", "bitrate": 3},
            {"resolution": "high", "framerate": "middle", "bitrate": 0},
            {"resolution": "high", "framerate": "middle", "bitrate": 10}
        ]
        for settings in invalid_settings:
            assert self._validate_camera_settings(settings) is False
    
    @staticmethod
    def _validate_object_name(name):
        """オブジェクト名バリデーション（サンプル実装）"""
        if not name or len(name) < 2 or len(name) > 20:
            return False
        # 英数字、ハイフン、アンダースコアのみ許可
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))
    
    @staticmethod
    def _validate_tracking_mode(mode):
        """追跡モードバリデーション（サンプル実装）"""
        valid_modes = {"center", "follow"}
        return mode in valid_modes
    
    @staticmethod
    def _validate_movement_params(params):
        """移動パラメータバリデーション（サンプル実装）"""
        if not isinstance(params, dict):
            return False
        
        valid_directions = {"forward", "backward", "left", "right", "up", "down"}
        if "direction" not in params or params["direction"] not in valid_directions:
            return False
        
        if "distance" not in params:
            return False
        
        distance = params["distance"]
        if not isinstance(distance, (int, float)) or distance <= 0 or distance > 500:
            return False
        
        return True
    
    @staticmethod
    def _validate_camera_settings(settings):
        """カメラ設定バリデーション（サンプル実装）"""
        if not isinstance(settings, dict):
            return False
        
        valid_resolutions = {"high", "low"}
        valid_framerates = {"high", "middle", "low"}
        
        if "resolution" in settings and settings["resolution"] not in valid_resolutions:
            return False
        
        if "framerate" in settings and settings["framerate"] not in valid_framerates:
            return False
        
        if "bitrate" in settings:
            bitrate = settings["bitrate"]
            if not isinstance(bitrate, int) or bitrate < 1 or bitrate > 5:
                return False
        
        return True


@pytest.mark.unit
class TestUtilityFunctions:
    """汎用ユーティリティ関数のテスト"""
    
    def test_format_file_size(self):
        """ファイルサイズフォーマット関数のテスト"""
        # バイト
        assert self._format_file_size(512) == "512 B"
        assert self._format_file_size(1023) == "1023 B"
        
        # キロバイト
        assert self._format_file_size(1024) == "1.0 KB"
        assert self._format_file_size(1536) == "1.5 KB"
        
        # メガバイト
        assert self._format_file_size(1024 * 1024) == "1.0 MB"
        assert self._format_file_size(2.5 * 1024 * 1024) == "2.5 MB"
        
        # ギガバイト
        assert self._format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_generate_unique_filename(self):
        """一意なファイル名生成のテスト"""
        filename1 = self._generate_unique_filename("test", "jpg")
        filename2 = self._generate_unique_filename("test", "jpg")
        
        # 異なるファイル名が生成されること
        assert filename1 != filename2
        
        # 正しい形式であること
        assert filename1.startswith("test_")
        assert filename1.endswith(".jpg")
        assert filename2.startswith("test_")
        assert filename2.endswith(".jpg")
    
    def test_format_duration(self):
        """時間フォーマット関数のテスト"""
        # 秒
        assert self._format_duration(30) == "00:30"
        assert self._format_duration(59) == "00:59"
        
        # 分
        assert self._format_duration(60) == "01:00"
        assert self._format_duration(90) == "01:30"
        assert self._format_duration(3599) == "59:59"
        
        # 時間
        assert self._format_duration(3600) == "1:00:00"
        assert self._format_duration(3661) == "1:01:01"
    
    def test_sanitize_filename(self):
        """ファイル名サニタイズ関数のテスト"""
        # 危険な文字の除去
        assert self._sanitize_filename("file<>name.txt") == "filename.txt"
        assert self._sanitize_filename("file|name.txt") == "filename.txt"
        assert self._sanitize_filename("file\"name.txt") == "filename.txt"
        
        # スペースの処理
        assert self._sanitize_filename("file name.txt") == "file_name.txt"
        assert self._sanitize_filename("  file  name  .txt") == "file_name.txt"
        
        # 日本語文字の処理
        assert self._sanitize_filename("ファイル名.txt") == "ファイル名.txt"
    
    def test_calculate_accuracy_percentage(self):
        """精度パーセンテージ計算のテスト"""
        assert self._calculate_accuracy_percentage(0.95) == "95.0%"
        assert self._calculate_accuracy_percentage(0.8765) == "87.7%"
        assert self._calculate_accuracy_percentage(1.0) == "100.0%"
        assert self._calculate_accuracy_percentage(0.0) == "0.0%"
    
    @staticmethod
    def _format_file_size(size_bytes):
        """ファイルサイズフォーマット（サンプル実装）"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def _generate_unique_filename(prefix, extension):
        """一意なファイル名生成（サンプル実装）"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}.{extension}"
    
    @staticmethod
    def _format_duration(seconds):
        """時間フォーマット（サンプル実装）"""
        if seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def _sanitize_filename(filename):
        """ファイル名サニタイズ（サンプル実装）"""
        import re
        # 危険な文字を除去
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # スペースをアンダースコアに置換
        filename = re.sub(r'\s+', '_', filename)
        # 先頭・末尾の空白・アンダースコアを除去
        filename = filename.strip('_')
        return filename
    
    @staticmethod
    def _calculate_accuracy_percentage(accuracy):
        """精度パーセンテージ計算（サンプル実装）"""
        return f"{accuracy * 100:.1f}%"


@pytest.mark.unit
class TestConfigurationHelpers:
    """設定関連ヘルパー関数のテスト"""
    
    def test_get_backend_url(self):
        """バックエンドURL取得のテスト"""
        # デフォルト値
        assert self._get_backend_url() == "http://localhost:8000"
        
        # 環境変数からの取得をシミュレート
        with patch.dict(os.environ, {'BACKEND_URL': 'http://custom:9000'}):
            assert self._get_backend_url() == "http://custom:9000"
    
    def test_get_upload_directory(self):
        """アップロードディレクトリ取得のテスト"""
        upload_dir = self._get_upload_directory()
        assert upload_dir.endswith("uploads")
        assert os.path.isabs(upload_dir)  # 絶対パスであること
    
    def test_get_allowed_extensions(self):
        """許可された拡張子一覧のテスト"""
        extensions = self._get_allowed_extensions()
        assert isinstance(extensions, set)
        assert 'jpg' in extensions
        assert 'png' in extensions
        assert 'jpeg' in extensions
    
    def test_is_development_mode(self):
        """開発モード判定のテスト"""
        # テスト環境では開発モード
        assert self._is_development_mode() is True
        
        # 本番環境のシミュレート
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            assert self._is_development_mode() is False
    
    @staticmethod
    def _get_backend_url():
        """バックエンドURL取得（サンプル実装）"""
        return os.environ.get('BACKEND_URL', 'http://localhost:8000')
    
    @staticmethod
    def _get_upload_directory():
        """アップロードディレクトリ取得（サンプル実装）"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, '..', '..', 'uploads')
    
    @staticmethod
    def _get_allowed_extensions():
        """許可された拡張子一覧（サンプル実装）"""
        return {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    
    @staticmethod
    def _is_development_mode():
        """開発モード判定（サンプル実装）"""
        return os.environ.get('FLASK_ENV', 'development') == 'development'


@pytest.mark.unit
class TestAPIHelpers:
    """API関連ヘルパー関数のテスト"""
    
    def test_build_api_url(self):
        """API URL構築のテスト"""
        base_url = "http://localhost:8000"
        
        # 基本的なパス
        assert self._build_api_url(base_url, "/api/health") == "http://localhost:8000/api/health"
        
        # スラッシュの正規化
        assert self._build_api_url(base_url, "api/health") == "http://localhost:8000/api/health"
        assert self._build_api_url(base_url + "/", "/api/health") == "http://localhost:8000/api/health"
    
    def test_format_api_response(self):
        """APIレスポンスフォーマットのテスト"""
        # 成功レスポンス
        success_response = self._format_api_response(True, "Success", {"data": "test"})
        expected = {
            "status": "success",
            "message": "Success",
            "data": {"data": "test"}
        }
        assert success_response == expected
        
        # エラーレスポンス
        error_response = self._format_api_response(False, "Error occurred")
        expected = {
            "status": "error",
            "message": "Error occurred",
            "data": None
        }
        assert error_response == expected
    
    def test_handle_api_error(self):
        """APIエラーハンドリングのテスト"""
        # HTTPエラー
        http_error = requests.HTTPError("404 Not Found")
        result = self._handle_api_error(http_error)
        assert result["status"] == "error"
        assert "404" in result["message"]
        
        # 接続エラー
        conn_error = requests.ConnectionError("Connection failed")
        result = self._handle_api_error(conn_error)
        assert result["status"] == "error"
        assert "connection" in result["message"].lower()
        
        # タイムアウトエラー
        timeout_error = requests.Timeout("Request timeout")
        result = self._handle_api_error(timeout_error)
        assert result["status"] == "error"
        assert "timeout" in result["message"].lower()
    
    @staticmethod
    def _build_api_url(base_url, path):
        """API URL構築（サンプル実装）"""
        base_url = base_url.rstrip('/')
        path = path.lstrip('/')
        return f"{base_url}/{path}"
    
    @staticmethod
    def _format_api_response(success, message, data=None):
        """APIレスポンスフォーマット（サンプル実装）"""
        return {
            "status": "success" if success else "error",
            "message": message,
            "data": data
        }
    
    @staticmethod
    def _handle_api_error(error):
        """APIエラーハンドリング（サンプル実装）"""
        if isinstance(error, requests.HTTPError):
            return {"status": "error", "message": f"HTTP error: {str(error)}"}
        elif isinstance(error, requests.ConnectionError):
            return {"status": "error", "message": "Connection error: Cannot connect to backend"}
        elif isinstance(error, requests.Timeout):
            return {"status": "error", "message": "Timeout error: Request timed out"}
        else:
            return {"status": "error", "message": f"Unknown error: {str(error)}"}


@pytest.mark.unit
class TestDateTimeHelpers:
    """日時関連ヘルパー関数のテスト"""
    
    def test_format_timestamp(self):
        """タイムスタンプフォーマットのテスト"""
        # 固定日時でテスト
        test_datetime = datetime(2023, 12, 15, 14, 30, 45)
        
        # デフォルトフォーマット
        assert self._format_timestamp(test_datetime) == "2023-12-15 14:30:45"
        
        # カスタムフォーマット
        assert self._format_timestamp(test_datetime, "%Y/%m/%d") == "2023/12/15"
        assert self._format_timestamp(test_datetime, "%H:%M:%S") == "14:30:45"
    
    def test_get_current_timestamp(self):
        """現在タイムスタンプ取得のテスト"""
        timestamp = self._get_current_timestamp()
        
        # 現在時刻に近いことを確認（5秒以内）
        now = datetime.now()
        diff = abs((now - timestamp).total_seconds())
        assert diff < 5
    
    def test_calculate_elapsed_time(self):
        """経過時間計算のテスト"""
        # 1時間前
        start_time = datetime.now() - timedelta(hours=1)
        elapsed = self._calculate_elapsed_time(start_time)
        assert 3500 <= elapsed <= 3700  # 約1時間（3600秒）
        
        # 30分前
        start_time = datetime.now() - timedelta(minutes=30)
        elapsed = self._calculate_elapsed_time(start_time)
        assert 1700 <= elapsed <= 1900  # 約30分（1800秒）
    
    @staticmethod
    def _format_timestamp(dt, format_str="%Y-%m-%d %H:%M:%S"):
        """タイムスタンプフォーマット（サンプル実装）"""
        return dt.strftime(format_str)
    
    @staticmethod
    def _get_current_timestamp():
        """現在タイムスタンプ取得（サンプル実装）"""
        return datetime.now()
    
    @staticmethod
    def _calculate_elapsed_time(start_time):
        """経過時間計算（サンプル実装）"""
        now = datetime.now()
        return int((now - start_time).total_seconds())